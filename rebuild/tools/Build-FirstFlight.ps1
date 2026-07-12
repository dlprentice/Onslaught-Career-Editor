# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param([switch]$Offline)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

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

    return $toolchain
}
catch {
    if ($null -ne $toolchain) {
        $toolchain.Dispose()
    }
    throw
}
