[CmdletBinding()]
param(
    [string]$BundleName = "OnslaughtToolkit-electron-portable-win-x64",
    [ValidateSet("community", "maintainer")]
    [string]$Audience = "community",
    [switch]$ForceClean,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\..\.."))
$artifactRoot = Join-Path $PSScriptRoot "artifacts"
$bundleRoot = Join-Path $artifactRoot $BundleName
$runtimeRoot = Join-Path $bundleRoot "runtime\electron"
$appRoot = Join-Path $bundleRoot "app"
$electronAppRoot = Join-Path $appRoot "electron"
$uiRoot = Join-Path $appRoot "ui"
$zipPath = Join-Path $artifactRoot "$BundleName.zip"

Import-Module (Join-Path $PSScriptRoot "ElectronBundlePolicy.psm1") -Force

function Assert-UnderPath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Candidate
    )

    $resolvedRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $resolvedCandidate = [System.IO.Path]::GetFullPath($Candidate)
    if (-not $resolvedCandidate.StartsWith($resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside artifact root. Candidate: $resolvedCandidate"
    }
}

function Copy-Directory {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (-not (Test-Path $Source)) {
        throw "Required source directory is missing: $Source"
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    if (Test-Path $Destination) {
        Remove-Item $Destination -Recurse -Force
    }
    Copy-Item $Source -Destination $Destination -Recurse -Force
}

function Copy-ElectronRuntime {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (-not (Test-Path $Source)) {
        throw "Required Electron runtime directory is missing: $Source"
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    if (Test-Path $Destination) {
        Remove-Item $Destination -Recurse -Force
    }

    # The portable launcher always passes our app root to electron.exe, so Electron's stock
    # default app is unused. Skipping it also avoids Windows file-lock issues while zipping.
    $robocopyArgs = @(
        $Source,
        $Destination,
        "/E",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS",
        "/NC",
        "/NS",
        "/NP",
        "/XF",
        "default_app.asar",
        "/XD",
        "default_app.asar.unpacked"
    )
    & robocopy @robocopyArgs | Out-Null
    $robocopyExitCode = $LASTEXITCODE
    if ($robocopyExitCode -ge 8) {
        throw "Failed to copy Electron runtime. Robocopy exit code: $robocopyExitCode"
    }
    $global:LASTEXITCODE = 0
}

function Copy-IfExists {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (Test-Path $Source) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
        Copy-Item $Source -Destination $Destination -Recurse -Force
    }
}

function Copy-FileIfExists {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (Test-Path $Source) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
        Copy-Item $Source -Destination $Destination -Force
    }
}

function Copy-CommunityContent {
    param(
        [Parameter(Mandatory = $true)][string]$SourceRoot,
        [Parameter(Mandatory = $true)][string]$DestinationRoot
    )

    $communityDocs = @(
        "lore-book\BOOK.md",
        "lore\team-roster.md",
        "lore\development-history.md",
        "reverse-engineering\save-file\save-format.md",
        "reverse-engineering\save-file\goodies-system.md",
        "reverse-engineering\save-file\grade-system.md",
        "reverse-engineering\save-file\kill-tracking.md",
        "reverse-engineering\game-mechanics\cheat-codes.md",
        "reverse-engineering\game-mechanics\god-mode.md",
        "reverse-engineering\game-assets\extraction-pipeline.md",
        "reverse-engineering\RE-INDEX.md",
        "roadmap\ROADMAP-INDEX.md",
        "roadmap\electron-workbench-migration.md"
    )

    foreach ($relativePath in $communityDocs) {
        Copy-FileIfExists -Source (Join-Path $SourceRoot $relativePath) -Destination (Join-Path $DestinationRoot $relativePath)
    }
}

Assert-UnderPath -Root $artifactRoot -Candidate $bundleRoot
Assert-UnderPath -Root $artifactRoot -Candidate $zipPath

if ($ForceClean) {
    if (Test-Path $bundleRoot) {
        Remove-Item $bundleRoot -Recurse -Force
    }
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
}

if (Test-Path $bundleRoot) {
    throw "Bundle root already exists: $bundleRoot. Re-run with -ForceClean to replace it, or pass a unique -BundleName."
}

Push-Location $repoRoot
try {
    if (-not $SkipBuild) {
        npm run build
    }

    $electronRuntimeSource = Join-Path $repoRoot "node_modules\electron\dist"
    $electronExe = Join-Path $electronRuntimeSource "electron.exe"
    if (-not (Test-Path $electronExe)) {
        throw "Electron runtime is missing. Run npm install before building the portable Electron bundle."
    }

    New-Item -ItemType Directory -Path $bundleRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $appRoot -Force | Out-Null

    Copy-ElectronRuntime -Source $electronRuntimeSource -Destination $runtimeRoot
    Copy-Directory -Source (Join-Path $repoRoot "archive\electron-workbench\apps\electron\dist") -Destination (Join-Path $electronAppRoot "dist")
    Copy-Directory -Source (Join-Path $repoRoot "archive\electron-workbench\packages\ui\dist") -Destination $uiRoot

    Copy-IfExists -Source (Join-Path $repoRoot "patches\catalog") -Destination (Join-Path $appRoot "patches\catalog")
    if ($Audience -eq "maintainer") {
        Copy-IfExists -Source (Join-Path $repoRoot "lore") -Destination (Join-Path $appRoot "lore")
        Copy-IfExists -Source (Join-Path $repoRoot "lore-book") -Destination (Join-Path $appRoot "lore-book")
        Copy-IfExists -Source (Join-Path $repoRoot "reverse-engineering") -Destination (Join-Path $appRoot "reverse-engineering")
        Copy-IfExists -Source (Join-Path $repoRoot "roadmap") -Destination (Join-Path $appRoot "roadmap")
        Copy-IfExists -Source (Join-Path $repoRoot "tools") -Destination (Join-Path $appRoot "tools")
    } else {
        Copy-CommunityContent -SourceRoot $repoRoot -DestinationRoot $appRoot
    }

    $generatedCatalog = Join-Path $repoRoot "subagents\asset_catalog_wave1_2026-03-14\catalog.json"
    if (Test-Path $generatedCatalog) {
        New-Item -ItemType Directory -Path (Join-Path $appRoot "asset-catalog") -Force | Out-Null
        Copy-Item $generatedCatalog -Destination (Join-Path $appRoot "asset-catalog\catalog.json") -Force
    }

    Copy-Item (Join-Path $repoRoot "README.MD") -Destination (Join-Path $appRoot "README.MD") -Force
    Copy-Item (Join-Path $repoRoot "CURRENT_CAPABILITIES.md") -Destination (Join-Path $appRoot "CURRENT_CAPABILITIES.md") -Force
    Copy-Item (Join-Path $repoRoot "RELEASE_SCOPE_AND_TEST_COMMANDS.md") -Destination (Join-Path $appRoot "RELEASE_SCOPE_AND_TEST_COMMANDS.md") -Force
    Copy-Item (Join-Path $repoRoot "LICENSE") -Destination (Join-Path $bundleRoot "LICENSE") -Force
    Copy-Item (Join-Path $PSScriptRoot "ELECTRON-BUNDLE-LAUNCHER.cmd") -Destination (Join-Path $bundleRoot "Launch Onslaught Workbench.cmd") -Force
    Copy-Item (Join-Path $PSScriptRoot "ELECTRON-BUNDLE-README.MD") -Destination (Join-Path $bundleRoot "README.MD") -Force

    $packageJson = @"
{
  "name": "onslaught-toolkit-electron-portable",
  "version": "0.0.0",
  "private": true,
  "main": "electron/dist/main.js"
}
"@
    Set-Content -Path (Join-Path $appRoot "package.json") -Value $packageJson -Encoding UTF8

    Assert-ElectronBundlePolicy -BundleRoot $bundleRoot -Audience $Audience -ReportPath (Join-Path $bundleRoot "bundle-policy.v1.json") | Out-Null

    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }

    Compress-Archive -Path (Join-Path $bundleRoot "*") -DestinationPath $zipPath -CompressionLevel Optimal

    Write-Host "Electron portable bundle ready:"
    Write-Host "  Audience: $Audience"
    Write-Host "  Folder: $bundleRoot"
    Write-Host "  Zip:    $zipPath"
    Write-Host "  Launch: $bundleRoot\Launch Onslaught Workbench.cmd"
}
finally {
    Pop-Location
}
