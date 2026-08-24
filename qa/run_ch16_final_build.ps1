$ErrorActionPreference = 'Stop'

$lane = Split-Path -Parent $PSScriptRoot
$src = Join-Path $lane 'source\id-ID'
$out = Join-Path $lane 'qa\build-through-ch16-final'
$tex = 'functional-analysis-id-through-ch16.tex'
$stem = 'functional-analysis-id-through-ch16'
$pdf = Join-Path $out ($stem + '.pdf')
$pass1Pdf = Join-Path $lane 'tmp\pdfs\ch16-final-pass1.pdf'
$pass1Log = Join-Path $lane 'qa\CH16_FINAL_BUILD_PASS1_LOG.txt'
$pass2Log = Join-Path $lane 'qa\CH16_FINAL_BUILD_PASS2_LOG.txt'
$resultPath = Join-Path $lane 'qa\CH16_FINAL_BUILD_RESULT.json'
$reader = Join-Path $lane 'output\pdf\analisis-fungsional-dan-aljabar-operator-id-bab-1-16.pdf'

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

$requiredNames = @(
    $tex,
    'DIAGXY.TEX',
    'functional_analysis_op_algs_bib.bib',
    'linalg-id.tex',
    'categories-id.tex',
    'normlinspaces-id.tex',
    'Hilbert_spaces-id.tex',
    'Hilbert_space_operators-id.tex',
    'Banach_spaces-id.tex',
    'compact_operators-id.tex',
    'spectrum-id.tex',
    'topvecspaces-id.tex',
    'distributions-id.tex',
    'Gelfand_Naimark-id.tex',
    'no_identity-id.tex',
    'GNS_construction-id.tex',
    'multiplier_algebras-id.tex',
    'fredholm_theory-id.tex',
    'extensions-id.tex'
)
$required = @($requiredNames | ForEach-Object { Join-Path $src $_ })
$missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missing.Count) { throw "Missing build inputs: $($missing -join ', ')" }
if (Test-Path -LiteralPath $out) { throw "Fresh fixed build path required: $out" }
if (Test-Path -LiteralPath $reader) { throw "Fresh reader target required: $reader" }
if (Test-Path -LiteralPath $pass1Pdf) { throw "Fresh pass-1 witness required: $pass1Pdf" }

$masterHash = (Get-FileHash -LiteralPath (Join-Path $src $tex) -Algorithm SHA256).Hash.ToLowerInvariant()
if ($masterHash -cne '6e528b0193d3179b58e44169430d043fa5399f7c860f09d832eb3ccd954a5388') {
    throw 'Chapter 16 cumulative master identity differs'
}
$chapterHash = (Get-FileHash -LiteralPath (Join-Path $src 'extensions-id.tex') -Algorithm SHA256).Hash.ToLowerInvariant()
if ($chapterHash -cne '59d745a18c74f9abe2ebe6eda3a78eb7c89bdc7fdef935cbc31ea0a552bfbbc3') {
    throw 'Chapter 16 target identity differs'
}

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
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $pdf -PathType Leaf)) { throw "Replay 1 build failed: $code" }
    $hash1 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
    $length1 = (Get-Item -LiteralPath $pdf).Length
    Copy-Item -LiteralPath $pdf -Destination $pass1Pdf
    Copy-Item -LiteralPath (Join-Path $out ($stem + '.log')) -Destination $pass1Log

    $code = Invoke-LatexmkCaptured @('-C', "-outdir=$out", $tex) (Join-Path $out 'replay-2-clean-console.txt')
    if ($code -ne 0) { throw "Replay 2 clean failed: $code" }
    $code = Invoke-LatexmkCaptured @('-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', "-outdir=$out", $tex) (Join-Path $out 'replay-2-console.txt')
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $pdf -PathType Leaf)) { throw "Replay 2 build failed: $code" }
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
$expectedInheritedPoints = @(7.30707, 11.09703)
$actualPoints = @($overfull | ForEach-Object { [double]$_.points })
if ($actualPoints.Count -ne $expectedInheritedPoints.Count) {
    throw "Unexpected cumulative overfull-box count: $($actualPoints.Count)"
}
for ($i = 0; $i -lt $expectedInheritedPoints.Count; $i++) {
    if ([math]::Abs($actualPoints[$i] - $expectedInheritedPoints[$i]) -gt 0.000001) {
        throw "Unexpected cumulative overfull box at index $i`: $($actualPoints[$i])"
    }
}
$chapterOverfullCount = $overfull.Count - $expectedInheritedPoints.Count

$info = & pdfinfo $pdf
if ($LASTEXITCODE -ne 0) { throw "pdfinfo failed: $LASTEXITCODE" }
$match = $info | Select-String '^Pages:\s+(\d+)\s*$'
if ($match.Count -ne 1) { throw 'Could not read exact PDF page count' }
$pages = [int]$match.Matches[0].Groups[1].Value
Copy-Item -LiteralPath $pdf -Destination $reader
$readerHash = (Get-FileHash -LiteralPath $reader -Algorithm SHA256).Hash.ToLowerInvariant()
if ($readerHash -cne $hash2 -or (Get-Item -LiteralPath $reader).Length -ne $length2) {
    throw 'Canonical reader copy differs from deterministic build'
}

$result = [ordered]@{
    schema_version = 'o008.ch16-final-build.v1'
    source_date_epoch = 1444126743
    fixed_output_path = Get-LaneRelativePath $out
    input_count = $required.Count
    inputs_unchanged = $true
    replay_1 = [ordered]@{ bytes = $length1; sha256 = $hash1 }
    replay_2 = [ordered]@{ bytes = $length2; sha256 = $hash2 }
    byte_identical = $true
    pages = $pages
    final_log_forbidden_counts = $failures
    overfull_boxes = $overfull
    inherited_chapter_11_overfull_boxes = $expectedInheritedPoints.Count
    chapter_16_overfull_boxes = $chapterOverfullCount
    pdf = [ordered]@{ path = Get-LaneRelativePath $pdf; bytes = $length2; sha256 = $hash2 }
    reader = [ordered]@{ path = Get-LaneRelativePath $reader; bytes = $length2; sha256 = $readerHash }
}
$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resultPath -Encoding utf8
$result | ConvertTo-Json -Depth 6
