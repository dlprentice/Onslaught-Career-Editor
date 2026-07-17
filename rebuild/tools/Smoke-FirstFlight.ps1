# SPDX-License-Identifier: GPL-3.0-or-later

[CmdletBinding()]
param([switch]$Offline)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Import-Module (Join-Path $PSScriptRoot 'FirstFlightSmokeRunner.psm1') -Force
Import-Module (Join-Path $PSScriptRoot 'FirstFlightSmokeValidation.psm1') -Force

function Invoke-FirstFlightNativeSmoke {
    param(
        [Parameter(Mandatory)]$Toolchain,
        [Parameter(Mandatory)][string]$ProjectRoot,
        [Parameter(Mandatory)][string]$RunRoot,
        [Parameter(Mandatory)][string]$Label,
        [Parameter(Mandatory)][int]$Width,
        [Parameter(Mandatory)][int]$Height
    )

    $outputRoot = Join-Path $RunRoot $Label
    if (Test-Path -LiteralPath $outputRoot) {
        throw "First Flight smoke profile output already exists: $outputRoot"
    }
    $null = [IO.Directory]::CreateDirectory($outputRoot)

    $reportPath = Join-Path $outputRoot 'first-flight-smoke.json'
    $screenshotPath = Join-Path $outputRoot 'first-flight-smoke.png'
    $logPath = Join-Path $outputRoot 'first-flight-smoke.log'
    $processResult = Invoke-BoundedProcess `
        -FileName $Toolchain.ConsolePath `
        -Arguments @(
            '--log-file', $logPath,
            '--path', $ProjectRoot,
            '--windowed',
            '--resolution', "${Width}x${Height}",
            '--fixed-fps', '60',
            '--',
            '--smoke',
            "--report=$reportPath",
            "--screenshot=$screenshotPath") `
        -TimeoutMilliseconds 45000 `
        -Description "First Flight native smoke '$Label'"

    if (-not [string]::IsNullOrWhiteSpace($processResult.StandardOutput)) {
        Write-Host $processResult.StandardOutput.TrimEnd()
    }
    if (-not [string]::IsNullOrWhiteSpace($processResult.StandardError)) {
        Write-Host $processResult.StandardError.TrimEnd()
    }

    $validation = Test-FirstFlightSmokeEvidence `
        -ReportPath $reportPath `
        -ScreenshotPath $screenshotPath `
        -LogPath $logPath `
        -ExpectedWidth $Width `
        -ExpectedHeight $Height

    return [pscustomobject]@{
        Label = $Label
        Width = $Width
        Height = $Height
        Tick = $validation.Tick
        StateHash = $validation.StateHash
        SampledColorCount = $validation.SampledColorCount
        NonBlackSampleCount = $validation.NonBlackSampleCount
        WorldSampledColorCount = $validation.WorldSampledColorCount
        WorldNonBlackSampleCount = $validation.WorldNonBlackSampleCount
        ReportPath = $reportPath
        ScreenshotPath = $screenshotPath
        LogPath = $logPath
    }
}

$buildArguments = @{}
if ($Offline) {
    $buildArguments.Offline = $true
}

$toolchain = $null
try {
    $toolchain = & (Join-Path $PSScriptRoot 'Build-FirstFlight.ps1') @buildArguments
    $repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
    $projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\OnslaughtRebuild.Godot'))
    $runRoot = New-BoundedFirstFlightSmokeRoot -RepoRoot $repoRoot

    $standard = Invoke-FirstFlightNativeSmoke `
        -Toolchain $toolchain `
        -ProjectRoot $projectRoot `
        -RunRoot $runRoot `
        -Label 'standard-1280x720' `
        -Width 1280 `
        -Height 720
    $minimum = Invoke-FirstFlightNativeSmoke `
        -Toolchain $toolchain `
        -ProjectRoot $projectRoot `
        -RunRoot $runRoot `
        -Label 'minimum-1200x675' `
        -Width 1200 `
        -Height 675

    [pscustomobject]@{
        Status = 'PASS'
        EngineVersion = $toolchain.Version
        EngineArchiveSha256 = $toolchain.ArchiveSha256
        EngineManifestSha256 = $toolchain.ManifestSha256
        Tick = $standard.Tick
        StateHash = $standard.StateHash
        StandardViewport = "$($standard.Width)x$($standard.Height)"
        StandardWorldSampledColorCount = $standard.WorldSampledColorCount
        StandardWorldNonBlackSampleCount = $standard.WorldNonBlackSampleCount
        MinimumViewport = "$($minimum.Width)x$($minimum.Height)"
        MinimumWorldSampledColorCount = $minimum.WorldSampledColorCount
        MinimumWorldNonBlackSampleCount = $minimum.WorldNonBlackSampleCount
        RunRoot = $runRoot
    }
}
finally {
    if ($null -ne $toolchain) {
        $toolchain.Dispose()
    }
}
