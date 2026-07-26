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
    [ValidateSet('startup', 'gameplay')]
    [string]$Plan = 'startup',
    [string]$Resolution = '640x480',
    # gameplay plan only. Point this at
    # local-lab/retail-reference-pristine/level100-gameplay/manifest.json to
    # sample the reconstruction at retail's REALISED level offsets instead of the
    # nominal 250 ms / 1 s grid. Retail's burst scheduler drifted up to ~80 ms
    # over the 1 Hz window, so nominal-grid pairing can exceed retail's own
    # +-25 ms matched-offset validity; this removes that error entirely.
    [string]$RetailOffsetManifest,
    [string]$RetailOffsetRuns = 'opening-pan-run1,hud-timeline-run1',
    [int]$TimeoutSeconds = 0
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# The gameplay plan holds Level 100 for 42 s of engine time plus the ~8 s
# frontend traversal, so the frontend default would abort it mid-timeline.
if ($TimeoutSeconds -le 0) {
    $TimeoutSeconds = if ($Plan -eq 'gameplay') { 600 } else { 120 }
}

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

    # The rig sets the viewport to $Resolution itself and disables content scaling,
    # so the frame is composed 1:1. --resolution alone is not enough: project.godot
    # pins viewport_width/height plus window_*_override, which win over the flag.
    $engineArgs = @(
        '--log-file', $logPath,
        '--path', $projectRoot,
        '--windowed',
        '--resolution', $Resolution,
        '--fixed-fps', '60',
        '--',
        "--capture-dir=$OutputDirectory",
        "--capture-plan=$Plan",
        "--capture-size=$Resolution")

    # In-level capture runs the tutorial music and voice for the full timeline.
    # Audio is not in the viewport texture, so silencing the mixer cannot change
    # a captured pixel; it only stops a 50-second capture from taking over the
    # operator's speakers. Left alone for the frontend plan so the 13 existing
    # startup shots are produced by an unchanged invocation.
    if ($Plan -eq 'gameplay') {
        $engineArgs = @('--audio-driver', 'Dummy') + $engineArgs
    }

    if (-not [string]::IsNullOrWhiteSpace($RetailOffsetManifest)) {
        if ($Plan -ne 'gameplay') {
            throw "-RetailOffsetManifest applies only to -Plan gameplay."
        }
        $wantedRuns = @($RetailOffsetRuns -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        $retail = Get-Content -LiteralPath $RetailOffsetManifest -Raw | ConvertFrom-Json
        $offsets = @($retail.frames |
            Where-Object { $wantedRuns -contains ($_.path -split '/')[0] } |
            ForEach-Object { [int]$_.levelOffsetMs } |
            Sort-Object -Unique)
        if ($offsets.Count -eq 0) {
            throw "No frames from runs '$RetailOffsetRuns' in $RetailOffsetManifest."
        }
        $engineArgs += "--capture-offsets-ms=$($offsets -join ',')"
    }

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

    # A frame that is not the requested size was resampled somewhere, and comparing
    # it against the retail reference would silently launder away layout error.
    $wanted = $Resolution -split 'x'
    $wrongSize = @($manifest.shots | Where-Object {
        $_.width -ne [int]$wanted[0] -or $_.height -ne [int]$wanted[1] })

    # A short manifest means the rig stopped before the end of its plan - the
    # reconstruction could not reach part of the timeline. That is a legitimate
    # and reportable outcome, but it is never a PASS, and the frames that WERE
    # captured must not be mistaken for a complete set.
    $planned = if ($manifest.PSObject.Properties.Name -contains 'plannedShots') { [int]$manifest.plannedShots } else { $manifest.shots.Count }
    $missing = [Math]::Max(0, $planned - $manifest.shots.Count)
    $boundary = if ($manifest.PSObject.Properties.Name -contains 'boundary') { $manifest.boundary } else { $null }

    [pscustomobject]@{
        Status = if ($mismatched.Count -eq 0 -and $failedSaves.Count -eq 0 -and $wrongSize.Count -eq 0 -and $missing -eq 0) { 'PASS' } else { 'SUSPECT' }
        WrongSizeShots = $wrongSize.Count
        MissingShots = $missing
        Boundary = $boundary
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
