# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [switch]$Offline,
    [switch]$LocalAssets,
    [string]$LocalAssetsRoot = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$buildArguments = @{}
if ($Offline) {
    $buildArguments.Offline = $true
}

$toolchain = & (Join-Path $PSScriptRoot 'Build-FirstFlight.ps1') @buildArguments
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\OnslaughtRebuild.Godot'))
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))

$userArgs = @()
if ($LocalAssets) {
    if ([string]::IsNullOrWhiteSpace($LocalAssetsRoot)) {
        $LocalAssetsRoot = Join-Path $repoRoot 'local-lab\rebuild-godot'
    }
    $LocalAssetsRoot = [IO.Path]::GetFullPath($LocalAssetsRoot)
    if (-not (Test-Path -LiteralPath $LocalAssetsRoot)) {
        throw "Local assets root not found: $LocalAssetsRoot. Run Initialize-LocalGodotAssets.ps1 / Bootstrap-LocalGodotAssets.ps1 first."
    }
    $userArgs += "--local-assets=$LocalAssetsRoot"
}

try {
    $engineArgs = @('--path', $projectRoot, '--windowed', '--resolution', '1280x720')
    if ($userArgs.Count -gt 0) {
        $engineArgs += @('--') + $userArgs
    }
    & $toolchain.EnginePath @engineArgs
    $engineExitCode = $LASTEXITCODE
}
finally {
    $toolchain.Dispose()
}

exit $engineExitCode
