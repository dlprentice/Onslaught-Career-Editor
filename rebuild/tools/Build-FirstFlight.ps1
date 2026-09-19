# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [switch]$Offline,
    [string]$GameRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not $IsWindows) {
    throw 'This historical launcher is Windows-only, and no Windows validation host is provisioned here. Use npm run build:rebuild-godot on Omarchy; a Windows result requires a separately provided Windows host.'
}

$materializeArguments = @(
    (Join-Path $PSScriptRoot 'materialize_retail_assets.py')
)
if (-not [string]::IsNullOrWhiteSpace($GameRoot)) {
    $materializeArguments += @('--game-root', $GameRoot)
}

& python @materializeArguments | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0) {
    throw "Retail asset materialization failed with exit code $LASTEXITCODE."
}

$setupArguments = @{}
if ($Offline) {
    $setupArguments.Offline = $true
}

$toolchain = $null
try {
    $toolchain = & (Join-Path $PSScriptRoot 'Setup-Godot.ps1') @setupArguments
    $projectPath = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\OnslaughtRebuild.Godot\OnslaughtRebuild.Godot.csproj'))
    $localPackages = Join-Path (Split-Path -Parent $toolchain.ConsolePath) 'GodotSharp\Tools\nupkgs'

    & dotnet restore $projectPath --source $localPackages --locked-mode --nologo |
        ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        throw "First Flight restore failed with exit code $LASTEXITCODE."
    }

    & dotnet build $projectPath --no-restore --nologo |
        ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        throw "First Flight build failed with exit code $LASTEXITCODE."
    }

    $projectRoot = Split-Path -Parent $projectPath
    $sceneArguments = @('--headless', '--audio-driver', 'Dummy', '--path', $projectRoot,
        'res://Scenes/World/ImportLevel100.tscn', '--', '--prepare-level100-scene')
    $terrainProbe = [Environment]::GetEnvironmentVariable('ONSLAUGHT_TERRAIN_PROBE')
    try {
        [Environment]::SetEnvironmentVariable('ONSLAUGHT_TERRAIN_PROBE', $null)
        & $toolchain.ConsolePath @sceneArguments | ForEach-Object { Write-Host $_ }
        $sceneExitCode = $LASTEXITCODE
    }
    finally {
        [Environment]::SetEnvironmentVariable('ONSLAUGHT_TERRAIN_PROBE', $terrainProbe)
    }
    if ($sceneExitCode -ne 0) {
        throw "Level 100 production scene import failed with exit code $sceneExitCode."
    }

    return $toolchain
}
catch {
    if ($null -ne $toolchain) {
        $toolchain.Dispose()
    }
    throw
}
