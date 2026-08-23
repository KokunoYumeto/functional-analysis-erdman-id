$ErrorActionPreference = 'Stop'

$lane = Split-Path -Parent $PSScriptRoot
$src = Join-Path $lane 'source\id-ID'
$out = Join-Path $lane 'qa\build-through-ch12-final'
$tex = 'functional-analysis-id-through-ch12.tex'
$pdf = Join-Path $out 'functional-analysis-id-through-ch12.pdf'
$tmpPdf = Join-Path $lane 'tmp\pdfs\ch12-final-pass1.pdf'
$pass1Log = Join-Path $lane 'qa\CH12_FINAL_BUILD_PASS1_LOG.txt'
$pass2Log = Join-Path $lane 'qa\CH12_FINAL_BUILD_PASS2_LOG.txt'
$resultPath = Join-Path $lane 'qa\CH12_FINAL_BUILD_RESULT.json'

function Get-LaneRelativePath([string]$path) {
    $lanePrefix = $lane.TrimEnd('\') + '\'
    if (-not $path.StartsWith($lanePrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the lane: $path"
    }
    return $path.Substring($lanePrefix.Length).Replace('\', '/')
}

function Invoke-LatexmkCaptured([string[]]$arguments, [string]$consolePath) {
    $savedPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & latexmk @arguments *> $consolePath
        return $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $savedPreference
    }
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
    'no_identity-id.tex'
)
$required = @($requiredNames | ForEach-Object { Join-Path $src $_ })
$missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missing.Count) {
    throw "Missing build inputs: $($missing -join ', ')"
}
if (Test-Path -LiteralPath $out) {
    throw "Fresh fixed build path required: $out"
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
New-Item -ItemType Directory -Path (Split-Path -Parent $tmpPdf) -Force | Out-Null
$snapshot | Export-Csv -LiteralPath (Join-Path $out 'input-snapshot.csv') -NoTypeInformation -Encoding utf8
$env:SOURCE_DATE_EPOCH = '1444126743'

Push-Location -LiteralPath $src
try {
    $code = Invoke-LatexmkCaptured -arguments @('-C', "-outdir=$out", $tex) -consolePath (Join-Path $out 'replay-1-clean-console.txt')
    if ($code -ne 0) { throw "Replay 1 clean failed: $code" }
    $code = Invoke-LatexmkCaptured -arguments @('-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', "-outdir=$out", $tex) -consolePath (Join-Path $out 'replay-1-console.txt')
    if ($code -ne 0) { throw "Replay 1 build failed: $code" }
    if (-not (Test-Path -LiteralPath $pdf -PathType Leaf)) { throw 'Replay 1 PDF missing' }
    $hash1 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
    $length1 = (Get-Item -LiteralPath $pdf).Length
    Copy-Item -LiteralPath $pdf -Destination $tmpPdf -Force
    Copy-Item -LiteralPath (Join-Path $out 'functional-analysis-id-through-ch12.log') -Destination $pass1Log -Force

    $code = Invoke-LatexmkCaptured -arguments @('-C', "-outdir=$out", $tex) -consolePath (Join-Path $out 'replay-2-clean-console.txt')
    if ($code -ne 0) { throw "Replay 2 clean failed: $code" }
    $code = Invoke-LatexmkCaptured -arguments @('-pdf', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', "-outdir=$out", $tex) -consolePath (Join-Path $out 'replay-2-console.txt')
    if ($code -ne 0) { throw "Replay 2 build failed: $code" }
    if (-not (Test-Path -LiteralPath $pdf -PathType Leaf)) { throw 'Replay 2 PDF missing' }
    $hash2 = (Get-FileHash -LiteralPath $pdf -Algorithm SHA256).Hash.ToLowerInvariant()
    $length2 = (Get-Item -LiteralPath $pdf).Length
    Copy-Item -LiteralPath (Join-Path $out 'functional-analysis-id-through-ch12.log') -Destination $pass2Log -Force
}
finally {
    Pop-Location
}

$changed = @()
foreach ($path in $required) {
    $now = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($now -cne $before[$path]) { $changed += $path }
}
if ($changed.Count) { throw "Build inputs changed: $($changed -join ', ')" }
if (($hash1 -cne $hash2) -or ($length1 -ne $length2)) {
    throw "Non-deterministic PDFs: replay1=$length1/$hash1 replay2=$length2/$hash2"
}

$info = & pdfinfo $pdf
if ($LASTEXITCODE -ne 0) { throw "pdfinfo failed: $LASTEXITCODE" }
$pagesMatch = $info | Select-String '^Pages:\s+(\d+)\s*$'
if ($pagesMatch.Count -ne 1) { throw 'Could not read exact PDF page count' }
$pages = [int]$pagesMatch.Matches[0].Groups[1].Value
$result = [ordered]@{
    schema_version = 'o008.ch12-final-build.v1'
    source_date_epoch = 1444126743
    fixed_output_path = Get-LaneRelativePath $out
    input_count = $required.Count
    inputs_unchanged = $true
    replay_1 = [ordered]@{ bytes = $length1; sha256 = $hash1 }
    replay_2 = [ordered]@{ bytes = $length2; sha256 = $hash2 }
    byte_identical = $true
    pages = $pages
    pdf = [ordered]@{ path = Get-LaneRelativePath $pdf; bytes = $length2; sha256 = $hash2 }
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $resultPath -Encoding utf8
$result | ConvertTo-Json -Depth 5
