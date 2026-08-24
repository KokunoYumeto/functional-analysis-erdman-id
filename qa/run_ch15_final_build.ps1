$ErrorActionPreference = 'Stop'

$lane = Split-Path -Parent $PSScriptRoot
$src = Join-Path $lane 'source\id-ID'
$out = Join-Path $lane 'qa\build-through-ch15-final'
$tex = 'functional-analysis-id-through-ch15.tex'
$stem = 'functional-analysis-id-through-ch15'
$pdf = Join-Path $out ($stem + '.pdf')
$pass1Pdf = Join-Path $lane 'tmp\pdfs\ch15-final-pass1.pdf'
$pass1Log = Join-Path $lane 'qa\CH15_FINAL_BUILD_PASS1_LOG.txt'
$pass2Log = Join-Path $lane 'qa\CH15_FINAL_BUILD_PASS2_LOG.txt'
$resultPath = Join-Path $lane 'qa\CH15_FINAL_BUILD_RESULT.json'
$reader = Join-Path $lane 'output\pdf\analisis-fungsional-dan-aljabar-operator-id-bab-1-15.pdf'

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
    'fredholm_theory-id.tex'
)
$required = @($requiredNames | ForEach-Object { Join-Path $src $_ })
$missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missing.Count) { throw "Missing build inputs: $($missing -join ', ')" }
if (Test-Path -LiteralPath $out) { throw "Fresh fixed build path required: $out" }
if (Test-Path -LiteralPath $reader) { throw "Fresh reader target required: $reader" }

$masterHash = (Get-FileHash -LiteralPath (Join-Path $src $tex) -Algorithm SHA256).Hash.ToLowerInvariant()
if ($masterHash -cne 'f2df36c70dcca86f44687efe450ea46a5611be2d1170a9ded16dbfbfcdb73a33') {
    throw 'Chapter 15 cumulative master identity differs'
}
$chapterHash = (Get-FileHash -LiteralPath (Join-Path $src 'fredholm_theory-id.tex') -Algorithm SHA256).Hash.ToLowerInvariant()
if ($chapterHash -cne '174b1ad2557f7dfa10e8171bd7482d907f858389b509f4d55de9cc785e2b43ba') {
    throw 'Chapter 15 target identity differs'
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
    Copy-Item -LiteralPath $pdf -Destination $pass1Pdf -Force
    Copy-Item -LiteralPath (Join-Path $out ($stem + '.log')) -Destination $pass1Log -Force

    $code = Invoke-LatexmkCaptured @('-C', "-outdir=$out", $tex) (Join-Path $out 'replay-2-clean-console.txt')
    if ($code -ne 0) { throw "Replay 2 clean failed: $code" }
    $code = Invoke-LatexmkCaptured @('-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', "-outdir=$out", $tex) (Join-Path $out 'replay-2-console.txt')
    if ($code -ne 0 -or -not (Test-Path -LiteralPath $pdf -PathType Leaf)) { throw "Replay 2 build failed: $code" }
    $hash2 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
    $length2 = (Get-Item -LiteralPath $pdf).Length
    Copy-Item -LiteralPath (Join-Path $out ($stem + '.log')) -Destination $pass2Log -Force
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
    schema_version = 'o008.ch15-final-build.v1'
    source_date_epoch = 1444126743
    fixed_output_path = Get-LaneRelativePath $out
    input_count = $required.Count
    inputs_unchanged = $true
    replay_1 = [ordered]@{ bytes = $length1; sha256 = $hash1 }
    replay_2 = [ordered]@{ bytes = $length2; sha256 = $hash2 }
    byte_identical = $true
    pages = $pages
    final_log_forbidden_counts = $failures
    pdf = [ordered]@{ path = Get-LaneRelativePath $pdf; bytes = $length2; sha256 = $hash2 }
    reader = [ordered]@{ path = Get-LaneRelativePath $reader; bytes = $length2; sha256 = $readerHash }
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $resultPath -Encoding utf8
$result | ConvertTo-Json -Depth 5
