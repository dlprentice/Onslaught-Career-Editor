# SPDX-License-Identifier: GPL-3.0-or-later
#
# Deterministic frontend screenshot capture for parity comparison.
#
# Retail reference captures are 640x480 because the released frontend composes at
# 4:3 (see local-lab/HYPOTHESIS-1-VERDICT-2026-07-25.md). This script launches the
# reconstruction at the SAME resolution so output is pixel-comparable against
# local-lab/startup-parity-ghidra-ro-2026-07-23/captures/ without any rescaling
# step in between - rescaling would hide exactly the layout errors we are hunting.
#
# --fixed-fps pins one _Process call to one logical frame so FrontendCaptureRig's
# frame ordinals are reproducible across runs.

[CmdletBinding()]
param(
    [switch]$Offline,
    [string]$GameRoot,
    [string]$OutputDirectory,
    [string]$Plan = 'startup',
    [string]$Resolution = '640x480',
    [int]$TimeoutSeconds = 120
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
    $OutputDirectory = Join-Path ([IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))) "local-lab\godot-captures\$stamp-$Plan"
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)

$buildArguments = @{}
if ($Offline) {
    $buildArguments.Offline = $true
}
if (-not [string]::IsNullOrWhiteSpace($GameRoot)) {
    $buildArguments.GameRoot = $GameRoot
}

$toolchain = & (Join-Path $PSScriptRoot 'Build-FirstFlight.ps1') @buildArguments
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\OnslaughtRebuild.Godot'))

try {
    $null = [IO.Directory]::CreateDirectory($OutputDirectory)
    $logPath = Join-Path $OutputDirectory 'capture.log'

    $engineArgs = @(
        '--log-file', $logPath,
        '--path', $projectRoot,
        '--windowed',
        '--resolution', $Resolution,
        '--fixed-fps', '60',
        '--',
        "--capture-dir=$OutputDirectory",
        "--capture-plan=$Plan")

    $process = Start-Process -FilePath $toolchain.EnginePath -ArgumentList $engineArgs -PassThru -NoNewWindow
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
        $process.Kill($true)
        throw "Capture timed out after $TimeoutSeconds seconds. Partial output: $OutputDirectory"
    }

    $manifestPath = Join-Path $OutputDirectory 'capture-manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "Capture produced no manifest. The rig did not reach its final shot. See $logPath"
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

    # A shot taken on the wrong screen is not evidence, so surface it loudly
    # rather than letting a mislabeled PNG into a parity comparison.
    $mismatched = @($manifest.shots | Where-Object { -not $_.screenMatched })
    $failedSaves = @($manifest.shots | Where-Object { $null -ne $_.saveError })

    [pscustomobject]@{
        Status = if ($mismatched.Count -eq 0 -and $failedSaves.Count -eq 0) { 'PASS' } else { 'SUSPECT' }
        Plan = $manifest.plan
        EngineVersion = $manifest.engineVersion
        Viewport = "$($manifest.viewportWidth)x$($manifest.viewportHeight)"
        RetailReferenceSize = $manifest.retailReferenceSize
        Shots = $manifest.shots.Count
        ScreenMismatches = $mismatched.Count
        FailedSaves = $failedSaves.Count
        OutputDirectory = $OutputDirectory
    }
}
finally {
    $toolchain.Dispose()
}
