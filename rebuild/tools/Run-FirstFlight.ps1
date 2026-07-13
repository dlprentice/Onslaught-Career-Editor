# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [switch]$Offline,
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
if (-not [string]::IsNullOrWhiteSpace($LocalAssetsRoot)) {
    Import-Module (Join-Path $PSScriptRoot 'LocalAssetWorkspace.psm1') -Force
    $LocalAssetsRoot = [IO.Path]::GetFullPath($LocalAssetsRoot)
    Assert-LocalAssetOutputRoot -RepoRoot $repoRoot -OutputRoot $LocalAssetsRoot | Out-Null
    if (-not (Test-Path -LiteralPath (Join-Path $LocalAssetsRoot 'manifest.json') -PathType Leaf)) { throw "Local asset manifest not found under exact opt-in root: $LocalAssetsRoot" }
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
