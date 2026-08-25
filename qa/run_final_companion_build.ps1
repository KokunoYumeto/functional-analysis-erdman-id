$ErrorActionPreference = 'Stop'

$lane = Split-Path -Parent $PSScriptRoot
$src = Join-Path $lane 'source\id-ID'
$baseSnapshotPath = Join-Path $lane 'qa\build-complete-source-final\input-snapshot.csv'
$out = Join-Path $lane 'qa\build-final-companion-final'
$tex = 'functional-analysis-id-complete-with-companions.tex'
$stem = 'functional-analysis-id-complete-with-companions'
$pdf = Join-Path $out ($stem + '.pdf')
$pass1Pdf = Join-Path $lane 'tmp\pdfs\final-companion-pass1.pdf'
$pass1Log = Join-Path $lane 'qa\FINAL_COMPANION_BUILD_PASS1_LOG.txt'
$pass2Log = Join-Path $lane 'qa\FINAL_COMPANION_BUILD_PASS2_LOG.txt'
$reader = Join-Path $lane 'output\pdf\analisis-fungsional-dan-aljabar-operator-id-edisi-lengkap-dengan-pendamping.pdf'
$snapshotPath = Join-Path $lane 'qa\FINAL_COMPANION_INPUT_SNAPSHOT.csv'
$resultPath = Join-Path $lane 'qa\FINAL_COMPANION_BUILD_RESULT.json'

function Get-LaneRelativePath([string]$path) {
    $full = [IO.Path]::GetFullPath($path)
    $prefix = [IO.Path]::GetFullPath($lane).TrimEnd('\') + '\'
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the lane: $full"
    }
    return $full.Substring($prefix.Length).Replace('\', '/')
}

function Get-Sha256([string]$path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Invoke-Captured([string]$program, [string[]]$arguments, [string]$consolePath) {
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $program @arguments *> $consolePath
        return $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $saved }
}

foreach ($path in @($baseSnapshotPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing input: $path" }
}

$generatorLog = Join-Path $lane 'qa\FINAL_COMPANION_GENERATOR_CONSOLE.txt'
$validatorLog = Join-Path $lane 'qa\FINAL_COMPANION_COMPONENT_VALIDATION_CONSOLE.txt'
foreach ($fresh in @($out, $pass1Pdf, $pass1Log, $pass2Log, $reader, $snapshotPath, $resultPath, $generatorLog, $validatorLog)) {
    if (Test-Path -LiteralPath $fresh) { throw "Fresh final-build target required: $fresh" }
}

$code = Invoke-Captured 'python' @('qa/build_final_companion_master.py') $generatorLog
if ($code -ne 0) { throw "Companion master generation failed: $code" }
$validatorCommands = @(
    'qa/validate_o001_solutions.py',
    'qa/validate_o001_reader_work.py',
    'qa/validate_compact_spectral_bridge.py'
)
$validationOutput = New-Object Text.StringBuilder
foreach ($script in $validatorCommands) {
    $temp = Join-Path $lane ('qa\.' + [IO.Path]::GetFileNameWithoutExtension($script) + '.console.tmp')
    $code = Invoke-Captured 'python' @($script) $temp
    [void]$validationOutput.AppendLine((Get-Content -LiteralPath $temp -Raw))
    Remove-Item -LiteralPath $temp -Force
    if ($code -ne 0) { throw "Component validation failed for $script`: $code" }
}
[IO.File]::WriteAllText($validatorLog, $validationOutput.ToString(), [Text.UTF8Encoding]::new($false))

$baseRows = @(Import-Csv -LiteralPath $baseSnapshotPath)
if ($baseRows.Count -ne 21) { throw "Complete-source snapshot row count differs: $($baseRows.Count)" }
$basePaths = foreach ($row in $baseRows) {
    $path = Join-Path $lane $row.relative_path.Replace('/', '\')
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing locked base input: $($row.relative_path)" }
    if ((Get-Item -LiteralPath $path).Length -ne [int64]$row.bytes -or (Get-Sha256 $path) -cne $row.sha256) {
        throw "Locked complete-source input differs: $($row.relative_path)"
    }
    $path
}

$companionRelative = @(
    'source/id-ID/functional-analysis-id-complete-with-companions.tex',
    'bridge/id-ID/compact-spectral-svd.tex',
    'mastery/id-ID/reader-work-selected.tex',
    'mastery/id-ID/solutions-ch01.tex',
    'mastery/id-ID/solutions-ch03.tex',
    'mastery/id-ID/solutions-ch04.tex',
    'mastery/id-ID/solutions-ch05.tex',
    'mastery/id-ID/solutions-ch06.tex',
    'mastery/id-ID/solutions-ch07.tex',
    'mastery/id-ID/solutions-ch08.tex',
    'mastery/id-ID/solutions-ch09.tex',
    'mastery/id-ID/solutions-ch10.tex',
    'mastery/id-ID/solutions-ch13.tex',
    'mastery/id-ID/solutions-ch14.tex',
    'mastery/id-ID/solutions-ch17.tex'
)
$companionPaths = foreach ($relative in $companionRelative) {
    $path = Join-Path $lane $relative.Replace('/', '\')
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing companion input: $relative" }
    $path
}
$required = @($basePaths) + @($companionPaths)
if (($required | Select-Object -Unique).Count -ne 36) { throw 'Expected 36 unique final inputs' }
$before = @{}
$snapshot = foreach ($path in $required) {
    $hash = Get-Sha256 $path
    $before[$path] = $hash
    [pscustomobject]@{
        relative_path = Get-LaneRelativePath $path
        bytes = (Get-Item -LiteralPath $path).Length
        sha256 = $hash
    }
}
$snapshot | Export-Csv -LiteralPath $snapshotPath -NoTypeInformation -Encoding utf8

New-Item -ItemType Directory -Path $out | Out-Null
New-Item -ItemType Directory -Path (Split-Path -Parent $pass1Pdf) -Force | Out-Null
$env:SOURCE_DATE_EPOCH = '1444126743'
Push-Location -LiteralPath $src
try {
    $code = Invoke-Captured 'latexmk' @('-C', "-outdir=$out", $tex) (Join-Path $out 'replay-1-clean-console.txt')
    if ($code -ne 0) { throw "Replay 1 clean failed: $code" }
    $code = Invoke-Captured 'latexmk' @(
        '-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
        "-outdir=$out", $tex
    ) (Join-Path $out 'replay-1-console.txt')
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $pdf -PathType Leaf)) {
        throw "Replay 1 build failed: $code"
    }
    $hashA = Get-Sha256 $pdf
    $lengthA = (Get-Item -LiteralPath $pdf).Length
    Copy-Item -LiteralPath $pdf -Destination $pass1Pdf
    Copy-Item -LiteralPath (Join-Path $out ($stem + '.log')) -Destination $pass1Log

    $code = Invoke-Captured 'latexmk' @('-C', "-outdir=$out", $tex) (Join-Path $out 'replay-2-clean-console.txt')
    if ($code -ne 0) { throw "Replay 2 clean failed: $code" }
    $code = Invoke-Captured 'latexmk' @(
        '-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
        "-outdir=$out", $tex
    ) (Join-Path $out 'replay-2-console.txt')
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $pdf -PathType Leaf)) {
        throw "Replay 2 build failed: $code"
    }
    $hashB = Get-Sha256 $pdf
    $lengthB = (Get-Item -LiteralPath $pdf).Length
    Copy-Item -LiteralPath (Join-Path $out ($stem + '.log')) -Destination $pass2Log
}
finally { Pop-Location }

$changed = @($required | Where-Object { (Get-Sha256 $_) -cne $before[$_] })
if ($changed.Count) { throw "Build inputs changed: $($changed -join ', ')" }
if ($hashA -cne $hashB -or $lengthA -ne $lengthB) {
    throw "Non-deterministic PDFs: A=$lengthA/$hashA B=$lengthB/$hashB"
}

$logPath = $pass2Log
$log = Get-Content -LiteralPath $logPath -Raw
$forbiddenPatterns = [ordered]@{
    tex_error = '(?m)^!'
    undefined_reference = 'LaTeX Warning: Reference .* undefined'
    undefined_citation = 'LaTeX Warning: Citation .* undefined'
    unresolved_summary = 'There were undefined references|There were undefined citations'
    rerun_required = 'Rerun to get cross-references right|Label\(s\) may have changed|Rerun to get bibliographical references right'
    multiply_defined = 'multiply defined'
    missing_character = 'Missing character:'
}
$failures = [ordered]@{}
foreach ($entry in $forbiddenPatterns.GetEnumerator()) {
    $failures[$entry.Key] = [regex]::Matches($log, $entry.Value).Count
}
if (@($failures.Values | Where-Object { $_ -ne 0 }).Count) {
    throw "Final log contains forbidden conditions: $($failures | ConvertTo-Json -Compress)"
}

$overfullMatches = [regex]::Matches($log, 'Overfull \\[hv]box \((?<pt>[0-9.]+)pt too (?:wide|high)\)(?<context>[^\r\n]*)')
$overfull = @($overfullMatches | ForEach-Object {
    [ordered]@{ points = [double]$_.Groups['pt'].Value; context = $_.Groups['context'].Value.Trim() }
})
$expectedInheritedPoints = @(2.90276, 7.30707, 11.09703, 21.73163, 14.48387, 3.32439)
$actualPoints = @($overfull | ForEach-Object { [double]$_.points })
if ($actualPoints.Count -ne $expectedInheritedPoints.Count) { throw "Overfull-box count differs: $($actualPoints.Count)" }
for ($i = 0; $i -lt $expectedInheritedPoints.Count; $i++) {
    if ([math]::Abs($actualPoints[$i] - $expectedInheritedPoints[$i]) -gt 0.000001) {
        throw "Unexpected overfull box at index $i`: $($actualPoints[$i])"
    }
}

$info = & pdfinfo $pdf
if ($LASTEXITCODE -ne 0) { throw "pdfinfo failed: $LASTEXITCODE" }
$pageMatch = $info | Select-String '^Pages:\s+(\d+)\s*$'
if ($pageMatch.Count -ne 1) { throw 'Could not read exact PDF page count' }
$pages = [int]$pageMatch.Matches[0].Groups[1].Value
# The twelve solution groups are section-level units inside Chapter 20.  This
# avoids nested unnumbered chapters, their forced blank versos, and the CH01
# two-line widow present in the provisional 302-page layout.
if ($pages -ne 298) { throw "Final companion page count differs: $pages" }
Copy-Item -LiteralPath $pdf -Destination $reader
if ((Get-Sha256 $reader) -cne $hashB -or (Get-Item -LiteralPath $reader).Length -ne $lengthB) {
    throw 'Canonical final reader differs from deterministic build'
}

$result = [ordered]@{
    schema_version = 'o008.final-companion-build.v1'
    result = 'pass'
    source_date_epoch = 1444126743
    input_count = $required.Count
    inputs_unchanged = $true
    component_counts = [ordered]@{
        source_exercise_solutions = 52
        selected_reader_work_solutions = 10
        bridge_units = 13
        solution_files = 12
    }
    replay_a = [ordered]@{ bytes = $lengthA; sha256 = $hashA }
    replay_b = [ordered]@{ bytes = $lengthB; sha256 = $hashB }
    byte_identical = $true
    pages = $pages
    final_log_forbidden_counts = $failures
    overfull_boxes = $overfull
    inherited_overfull_box_count = $expectedInheritedPoints.Count
    companion_overfull_box_count = 0
    pdf = [ordered]@{ path = Get-LaneRelativePath $reader; bytes = $lengthB; sha256 = $hashB }
    input_snapshot = [ordered]@{ path = Get-LaneRelativePath $snapshotPath; rows = $snapshot.Count; sha256 = Get-Sha256 $snapshotPath }
}
$json = $result | ConvertTo-Json -Depth 7
[IO.File]::WriteAllText($resultPath, $json + "`n", [Text.UTF8Encoding]::new($false))
$json
