$ErrorActionPreference = 'Stop'

$lane = Split-Path -Parent $PSScriptRoot
$src = Join-Path $lane 'source\id-ID'
$priorSnapshotPath = Join-Path $lane 'qa\build-through-ch17-final\input-snapshot.csv'
$out = Join-Path $lane 'qa\build-complete-source-final'
$tex = 'functional-analysis-id-complete-source.tex'
$stem = 'functional-analysis-id-complete-source'
$pdf = Join-Path $out ($stem + '.pdf')
$pass1Pdf = Join-Path $lane 'tmp\pdfs\complete-source-final-pass1.pdf'
$pass1Log = Join-Path $lane 'qa\COMPLETE_SOURCE_FINAL_BUILD_PASS1_LOG.txt'
$pass2Log = Join-Path $lane 'qa\COMPLETE_SOURCE_FINAL_BUILD_PASS2_LOG.txt'
$resultPath = Join-Path $lane 'qa\COMPLETE_SOURCE_FINAL_BUILD_RESULT.json'
$reader = Join-Path $lane 'output\pdf\analisis-fungsional-dan-aljabar-operator-id-teks-sumber-lengkap.pdf'

function Get-LaneRelativePath([string]$path) {
    $prefix = $lane.TrimEnd('\') + '\'
    if (-not $path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the lane: $path"
    }
    return $path.Substring($prefix.Length).Replace('\', '/')
}

function Invoke-LatexmkCaptured([string[]]$arguments, [string]$consolePath) {
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & latexmk @arguments *> $consolePath
        return $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $saved }
}

if (-not (Test-Path -LiteralPath $priorSnapshotPath -PathType Leaf)) {
    throw "Missing inherited Chapter 17 input snapshot: $priorSnapshotPath"
}
$priorSnapshot = @(Import-Csv -LiteralPath $priorSnapshotPath)
if ($priorSnapshot.Count -ne 20) {
    throw "Chapter 17 input snapshot row count differs: $($priorSnapshot.Count)"
}
$oldMaster = 'source/id-ID/functional-analysis-id-through-ch17.tex'
$inheritedRows = @($priorSnapshot | Where-Object { $_.relative_path -cne $oldMaster })
if ($inheritedRows.Count -ne 19) {
    throw "Inherited dependency/chapter row count differs: $($inheritedRows.Count)"
}

$inherited = foreach ($row in $inheritedRows) {
    $path = Join-Path $lane $row.relative_path.Replace('/', '\')
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing inherited build input: $($row.relative_path)"
    }
    $item = Get-Item -LiteralPath $path
    $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($item.Length -ne [int64]$row.bytes -or $hash -cne $row.sha256) {
        throw "Inherited input differs from Chapter 17 lock: $($row.relative_path)"
    }
    $path
}

$master = Join-Path $src $tex
$preface = Join-Path $src 'preface-id.tex'
foreach ($path in @($master, $preface)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing complete-source build input: $path"
    }
}
$masterHash = (Get-FileHash -LiteralPath $master -Algorithm SHA256).Hash.ToLowerInvariant()
if ((Get-Item -LiteralPath $master).Length -ne 11176 -or
    $masterHash -cne '7f06919a8ec9088a3bc812fab962a48b5f1b3b0d5d3bce80eb21055f65089041') {
    throw 'Complete-source cumulative master identity differs'
}
$prefaceHash = (Get-FileHash -LiteralPath $preface -Algorithm SHA256).Hash.ToLowerInvariant()
if ((Get-Item -LiteralPath $preface).Length -ne 18140 -or
    $prefaceHash -cne 'c622dc9d9c1af4e5b1a6112c84eeff7328c778e8ef8643fc267f6fc6e3e7d564') {
    throw 'Translated preface identity differs'
}

$required = @($master, $preface) + $inherited
$before = @{}
$snapshot = foreach ($path in $required) {
    $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    $before[$path] = $hash
    [pscustomobject]@{
        relative_path = Get-LaneRelativePath $path
        bytes = (Get-Item -LiteralPath $path).Length
        sha256 = $hash
    }
}

foreach ($freshPath in @($out, $pass1Pdf, $pass1Log, $pass2Log, $resultPath, $reader)) {
    if (Test-Path -LiteralPath $freshPath) {
        throw "Fresh final-build target required: $freshPath"
    }
}
New-Item -ItemType Directory -Path $out | Out-Null
New-Item -ItemType Directory -Path (Split-Path -Parent $pass1Pdf) -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path -Parent $reader) -Force | Out-Null
$snapshot | Export-Csv -LiteralPath (Join-Path $out 'input-snapshot.csv') -NoTypeInformation -Encoding utf8
$env:SOURCE_DATE_EPOCH = '1444126743'

Push-Location -LiteralPath $src
try {
    $code = Invoke-LatexmkCaptured @('-C', "-outdir=$out", $tex) (Join-Path $out 'replay-1-clean-console.txt')
    if ($code -ne 0) { throw "Replay 1 clean failed: $code" }
    $code = Invoke-LatexmkCaptured @('-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', "-outdir=$out", $tex) (Join-Path $out 'replay-1-console.txt')
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $pdf -PathType Leaf)) {
        throw "Replay 1 build failed: $code"
    }
    $hash1 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
    $length1 = (Get-Item -LiteralPath $pdf).Length
    Copy-Item -LiteralPath $pdf -Destination $pass1Pdf
    Copy-Item -LiteralPath (Join-Path $out ($stem + '.log')) -Destination $pass1Log

    $code = Invoke-LatexmkCaptured @('-C', "-outdir=$out", $tex) (Join-Path $out 'replay-2-clean-console.txt')
    if ($code -ne 0) { throw "Replay 2 clean failed: $code" }
    $code = Invoke-LatexmkCaptured @('-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', "-outdir=$out", $tex) (Join-Path $out 'replay-2-console.txt')
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $pdf -PathType Leaf)) {
        throw "Replay 2 build failed: $code"
    }
    $hash2 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
    $length2 = (Get-Item -LiteralPath $pdf).Length
    Copy-Item -LiteralPath (Join-Path $out ($stem + '.log')) -Destination $pass2Log
}
finally { Pop-Location }

$changed = @($required | Where-Object {
    (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant() -cne $before[$_]
})
if ($changed.Count) { throw "Build inputs changed: $($changed -join ', ')" }
if ($hash1 -cne $hash2 -or $length1 -ne $length2) {
    throw "Non-deterministic PDFs: replay1=$length1/$hash1 replay2=$length2/$hash2"
}

$log = Get-Content -LiteralPath $pass2Log -Raw
$forbidden = [ordered]@{
    tex_error = '(?m)^!'
    undefined_reference = 'LaTeX Warning: Reference .* undefined'
    undefined_citation = 'LaTeX Warning: Citation .* undefined'
    unresolved_summary = 'There were undefined references|There were undefined citations'
    rerun_required = 'Rerun to get cross-references right|Label\(s\) may have changed'
    multiply_defined = 'multiply defined'
    missing_character = 'Missing character:'
}
$failures = [ordered]@{}
foreach ($entry in $forbidden.GetEnumerator()) {
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
if ($actualPoints.Count -ne $expectedInheritedPoints.Count) {
    throw "Overfull-box count differs: $($actualPoints.Count)"
}
for ($i = 0; $i -lt $expectedInheritedPoints.Count; $i++) {
    if ([math]::Abs($actualPoints[$i] - $expectedInheritedPoints[$i]) -gt 0.000001) {
        throw "Unexpected overfull box at index $i`: $($actualPoints[$i])"
    }
}

$info = & pdfinfo $pdf
if ($LASTEXITCODE -ne 0) { throw "pdfinfo failed: $LASTEXITCODE" }
$match = $info | Select-String '^Pages:\s+(\d+)\s*$'
if ($match.Count -ne 1) { throw 'Could not read exact PDF page count' }
$pages = [int]$match.Matches[0].Groups[1].Value
if ($pages -ne 238) { throw "Complete-source page count differs: $pages" }
Copy-Item -LiteralPath $pdf -Destination $reader
$readerHash = (Get-FileHash -LiteralPath $reader -Algorithm SHA256).Hash.ToLowerInvariant()
if ($readerHash -cne $hash2 -or (Get-Item -LiteralPath $reader).Length -ne $length2) {
    throw 'Canonical reader copy differs from deterministic build'
}

$result = [ordered]@{
    schema_version = 'o008.complete-source-final-build.v1'
    source_date_epoch = 1444126743
    fixed_output_path = Get-LaneRelativePath $out
    input_count = $required.Count
    inherited_ch17_input_count = $inherited.Count
    inherited_ch17_inputs_exact = $true
    inputs_unchanged = $true
    replay_1 = [ordered]@{ bytes = $length1; sha256 = $hash1 }
    replay_2 = [ordered]@{ bytes = $length2; sha256 = $hash2 }
    byte_identical = $true
    pages = $pages
    final_log_forbidden_counts = $failures
    overfull_boxes = $overfull
    inherited_overfull_box_count = $expectedInheritedPoints.Count
    preface_overfull_box_count = 0
    pdf = [ordered]@{ path = Get-LaneRelativePath $pdf; bytes = $length2; sha256 = $hash2 }
    reader = [ordered]@{ path = Get-LaneRelativePath $reader; bytes = $length2; sha256 = $readerHash }
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resultPath -Encoding utf8
$result | ConvertTo-Json -Depth 6
