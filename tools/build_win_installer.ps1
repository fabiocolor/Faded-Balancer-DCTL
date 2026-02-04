# Build Windows installer for Faded Balancer DCTL (Inno Setup).
# Run from repo root. Requires Inno Setup (iscc) on PATH.
# Usage: .\tools\build_win_installer.ps1 [version]
# Example: .\tools\build_win_installer.ps1 1.6.0

param(
    [string]$Version = "1.6.0"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$IssPath = Join-Path $RepoRoot "installers\win\FadedBalancerDCTL.iss"
$DctlPath = Join-Path $RepoRoot "FadedBalancerDCTL.dctl"

if (-not (Test-Path $DctlPath)) {
    Write-Error "DCTL not found: $DctlPath"
}
if (-not (Test-Path $IssPath)) {
    Write-Error "Inno Setup script not found: $IssPath"
}

$isccExe = $null
$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if ($iscc) {
    $isccExe = $iscc.Source
} else {
    $commonPaths = @(
        "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
    )
    foreach ($p in $commonPaths) {
        if (Test-Path $p) { $isccExe = $p; break }
    }
}
if (-not $isccExe) {
    Write-Error "Inno Setup compiler (iscc) not found. Install from https://jrsoftware.org/isinfo.php or run: winget install JRSoftware.InnoSetup (then restart the terminal)."
}

Push-Location $RepoRoot
try {
    # Pass version to compiler; Inno Setup preprocessor can use /DMyAppVersion=1.6.0
    & $isccExe /DMyAppVersion=$Version (Resolve-Path $IssPath).Path
    if ($LASTEXITCODE -ne 0) { throw "iscc exited with $LASTEXITCODE" }
    $outDir = Join-Path $RepoRoot "installers"
    $exe = Get-ChildItem -Path $outDir -Filter "FadedBalancerDCTL-Setup-*.exe" | Select-Object -First 1
    if ($exe) { Write-Host "Built: $($exe.FullName)" }
} finally {
    Pop-Location
}
