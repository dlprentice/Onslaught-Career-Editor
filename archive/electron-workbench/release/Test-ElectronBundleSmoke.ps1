[CmdletBinding()]
param(
    [string]$BundleName = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($BundleName)) {
    $BundleName = "OnslaughtToolkit-electron-portable-smoke-$PID"
}

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\..\.."))
$artifactRoot = Join-Path $PSScriptRoot "artifacts"
$bundleRoot = Join-Path $artifactRoot $BundleName
$appRoot = Join-Path $bundleRoot "app"
$runtimeRoot = Join-Path $bundleRoot "runtime\electron"
$policyPath = Join-Path $bundleRoot "bundle-policy.v1.json"
$zipPath = Join-Path $artifactRoot "$BundleName.zip"
$indexPath = Join-Path $appRoot "ui\index.html"
$electronExe = Join-Path $runtimeRoot "electron.exe"

Push-Location $repoRoot
try {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "Build-ElectronBundle.ps1") -BundleName $BundleName -ForceClean
    if ($LASTEXITCODE -ne 0) {
        throw "Build-ElectronBundle.ps1 failed with exit code $LASTEXITCODE."
    }

    foreach ($requiredPath in @($bundleRoot, $appRoot, $runtimeRoot, $policyPath, $zipPath, $indexPath, $electronExe)) {
        if (-not (Test-Path $requiredPath)) {
            throw "Expected bundle smoke path is missing: $requiredPath"
        }
    }

    $policy = Get-Content -Raw $policyPath | ConvertFrom-Json
    if ($policy.schema -ne "electron-bundle-policy.v1") {
        throw "Unexpected bundle policy schema: $($policy.schema)"
    }
    if ([int]$policy.deniedPathCount -ne 0) {
        throw "Bundle policy found denied paths: $($policy.deniedPathCount)"
    }

    $indexHtml = Get-Content -Raw $indexPath
    if ($indexHtml -match 'src="/assets/' -or $indexHtml -match 'href="/assets/') {
        throw "Packaged renderer still contains root-relative asset paths."
    }
    if ($indexHtml -notmatch '\./assets/') {
        throw "Packaged renderer does not contain relative ./assets references."
    }

    $deniedAppPaths = @(
        "game",
        ".codex",
        "media",
        "save-attempts",
        "subagents",
        "AGENTS.md",
        "developer_agent_state.json",
        "documentation_agent_state.json",
        "archive",
        "OnslaughtCareerEditor.WinUI"
    )
    foreach ($relativePath in $deniedAppPaths) {
        $candidate = Join-Path $appRoot $relativePath
        if (Test-Path $candidate) {
            throw "Denied bundle path is present: $candidate"
        }
    }

    $env:ONSLAUGHT_RENDERER_SMOKE = "1"
    try {
        & $electronExe $appRoot
        if ($LASTEXITCODE -ne 0) {
            throw "Packaged Electron renderer smoke failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Remove-Item Env:\ONSLAUGHT_RENDERER_SMOKE -ErrorAction SilentlyContinue
    }

    Write-Host "Electron bundle smoke: PASS"
    Write-Host "  Bundle: $bundleRoot"
    Write-Host "  Zip:    $zipPath"
}
finally {
    Pop-Location
}
