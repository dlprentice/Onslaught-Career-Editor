# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param(
    [switch]$Offline,
    [string]$GameRoot
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Import-Module (Join-Path $PSScriptRoot 'FirstFlightSmokeRunner.psm1') -Force
Import-Module (Join-Path $PSScriptRoot 'FirstFlightSmokeValidation.psm1') -Force

function Invoke-FirstFlightNativeSmoke {
    param(
        [Parameter(Mandatory)]$Toolchain,
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string]$RunRoot,
        [Parameter(Mandatory)][string]$Label
    )

    $outputRoot = Join-Path $RunRoot $Label
    if (Test-Path -LiteralPath $outputRoot) {
        throw "First Flight smoke profile output already exists: $outputRoot"
    }
    $null = [IO.Directory]::CreateDirectory($outputRoot)

    $reportPath = Join-Path $outputRoot 'first-flight-smoke.json'
    $logPath = Join-Path $outputRoot 'first-flight-smoke.log'
    $processResult = Invoke-BoundedProcess `
        -FileName $Toolchain.ConsolePath `
        -Arguments @(
            '--log-file', $logPath,
            '--path', $ProjectRoot,
            '--windowed',
            '--fixed-fps', '60',
            '--',
            '--smoke',
            "--report=$reportPath") `
        -TimeoutMilliseconds 75000 `
        -Description "First Flight native smoke '$Label'"

    if (-not [string]::IsNullOrWhiteSpace($processResult.StandardOutput)) {
        Write-Host $processResult.StandardOutput.TrimEnd()
    }
    if (-not [string]::IsNullOrWhiteSpace($processResult.StandardError)) {
        Write-Host $processResult.StandardError.TrimEnd()
    }

    $validation = Test-FirstFlightSmokeEvidence `
        -ReportPath $reportPath `
        -LogPath $logPath

    return [pscustomobject]@{
        Label = $Label
        Tick = $validation.Tick
        StateHash = $validation.StateHash
        ReportPath = $reportPath
        LogPath = $logPath
    }
}

$buildArguments = @{}
if ($Offline) {
    $buildArguments.Offline = $true
}
if (-not [string]::IsNullOrWhiteSpace($GameRoot)) {
    $buildArguments.GameRoot = $GameRoot
}

$toolchain = $null
try {
    $toolchain = & (Join-Path $PSScriptRoot 'Build-FirstFlight.ps1') @buildArguments
    $repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
    $projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\OnslaughtRebuild.Godot'))
    $runRoot = New-BoundedFirstFlightSmokeRoot -RepoRoot $repoRoot

    $smoke = Invoke-FirstFlightNativeSmoke `
        -Toolchain $toolchain `
        -ProjectRoot $projectRoot `
        -RunRoot $runRoot `
        -Label 'cold-frontend-lifecycle'

    [pscustomobject]@{
        Status = 'PASS'
        EngineVersion = $toolchain.Version
        EngineArchiveSha256 = $toolchain.ArchiveSha256
        EngineManifestSha256 = $toolchain.ManifestSha256
        Tick = $smoke.Tick
        StateHash = $smoke.StateHash
        RunRoot = $runRoot
    }
}
finally {
    if ($null -ne $toolchain) {
        $toolchain.Dispose()
    }
}
