# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param([switch]$Offline)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$buildArguments = @{}
if ($Offline) {
    $buildArguments.Offline = $true
}

$toolchain = & (Join-Path $PSScriptRoot 'Build-FirstFlight.ps1') @buildArguments
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\OnslaughtRebuild.Godot'))

try {
    & $toolchain.EnginePath --path $projectRoot --windowed --resolution 1280x720
    $engineExitCode = $LASTEXITCODE
}
finally {
    $toolchain.Dispose()
}

exit $engineExitCode
