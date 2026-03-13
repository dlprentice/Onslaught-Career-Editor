[CmdletBinding()]
param(
    [string]$Configuration = "Release",
    [string]$RuntimeIdentifier = "win-x64",
    [switch]$ForceClean
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$artifactRoot = Join-Path $PSScriptRoot "artifacts"
$bundleName = "OnslaughtToolkit-winui-portable-$RuntimeIdentifier"
$bundleRoot = Join-Path $artifactRoot $bundleName
$appBundleRoot = Join-Path $bundleRoot "app"
$cliBundleRoot = Join-Path $appBundleRoot "cli"
$zipPath = Join-Path $artifactRoot "$bundleName.zip"

if ($ForceClean) {
    if (Test-Path $bundleRoot) {
        Remove-Item $bundleRoot -Recurse -Force
    }
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
}

if (Test-Path $bundleRoot) {
    throw "Bundle root already exists: $bundleRoot. Re-run with -ForceClean to replace it."
}

New-Item -ItemType Directory -Path $bundleRoot -Force | Out-Null
New-Item -ItemType Directory -Path $appBundleRoot -Force | Out-Null
New-Item -ItemType Directory -Path $cliBundleRoot -Force | Out-Null

Push-Location $repoRoot
try {
    $winUiProject = Join-Path $repoRoot "OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj"
    $cliProject = Join-Path $repoRoot "OnslaughtCareerEditor.Cli\OnslaughtCareerEditor.Cli.csproj"

    dotnet publish $winUiProject `
        -c $Configuration `
        -r $RuntimeIdentifier `
        --self-contained true `
        -p:WindowsPackageType=None `
        -o $appBundleRoot

    $winUiBuildOutput = Join-Path $repoRoot "OnslaughtCareerEditor.WinUI\bin\$Configuration\net10.0-windows10.0.19041.0\$RuntimeIdentifier"
    if (-not (Test-Path $winUiBuildOutput)) {
        throw "Expected WinUI build output was not found: $winUiBuildOutput"
    }

    Copy-Item (Join-Path $winUiBuildOutput "OnslaughtCareerEditor.WinUI.pri") -Destination (Join-Path $appBundleRoot "OnslaughtCareerEditor.WinUI.pri") -Force
    Get-ChildItem $winUiBuildOutput -Recurse -File -Filter *.xbf | ForEach-Object {
        $relativePath = $_.FullName.Substring($winUiBuildOutput.Length).TrimStart('\', '/')
        $destinationPath = Join-Path $appBundleRoot $relativePath
        $destinationDirectory = Split-Path -Parent $destinationPath
        if (-not (Test-Path $destinationDirectory)) {
            New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
        }

        Copy-Item $_.FullName -Destination $destinationPath -Force
    }

    dotnet publish $cliProject `
        -c $Configuration `
        -r $RuntimeIdentifier `
        --self-contained true `
        -o $cliBundleRoot

    $loreSource = Join-Path $repoRoot "lore-book"
    $catalogSource = Join-Path $repoRoot "patches\catalog"

    Copy-Item $loreSource -Destination (Join-Path $appBundleRoot "lore-book") -Recurse -Force
    New-Item -ItemType Directory -Path (Join-Path $appBundleRoot "patches") -Force | Out-Null
    Copy-Item $catalogSource -Destination (Join-Path $appBundleRoot "patches\catalog") -Recurse -Force

    Copy-Item (Join-Path $repoRoot "release\BUNDLE-LAUNCHER.cmd") -Destination (Join-Path $bundleRoot "Launch Onslaught Toolkit.cmd") -Force
    Copy-Item (Join-Path $repoRoot "release\BUNDLE-README.MD") -Destination (Join-Path $bundleRoot "README.MD") -Force
    Copy-Item (Join-Path $repoRoot "release\BUNDLE-README.MD") -Destination (Join-Path $appBundleRoot "README.MD") -Force
    Copy-Item (Join-Path $repoRoot "LICENSE") -Destination (Join-Path $bundleRoot "LICENSE") -Force

    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }

    Compress-Archive -Path (Join-Path $bundleRoot "*") -DestinationPath $zipPath -CompressionLevel Optimal

    Write-Host "Portable bundle ready:"
    Write-Host "  Folder: $bundleRoot"
    Write-Host "  Zip:    $zipPath"
}
finally {
    Pop-Location
}
