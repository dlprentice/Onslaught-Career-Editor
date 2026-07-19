# SPDX-License-Identifier: GPL-3.0-or-later

Set-StrictMode -Version Latest

function Assert-SmokeValue {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)]$Expected,
        [Parameter(Mandatory)]$Actual
    )

    if ($Expected -ne $Actual) {
        throw "First Flight smoke '$Name' mismatch: expected '$Expected', observed '$Actual'."
    }
}

function Assert-SmokeNear {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][double]$Expected,
        [Parameter(Mandatory)][double]$Actual,
        [double]$Tolerance = 0.00001
    )

    if ([Math]::Abs($Expected - $Actual) -gt $Tolerance) {
        throw "First Flight smoke '$Name' mismatch: expected '$Expected' ± '$Tolerance', observed '$Actual'."
    }
}

function Test-FirstFlightSmokeEvidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ReportPath,
        [Parameter(Mandatory)][string]$ScreenshotPath,
        [Parameter(Mandatory)][string]$LogPath,
        [int]$ExpectedWidth = 1280,
        [int]$ExpectedHeight = 720
    )

    foreach ($path in @($ReportPath, $ScreenshotPath, $LogPath)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "First Flight smoke artifact is missing: $path"
        }
    }

    $rawReport = Get-Content -LiteralPath $ReportPath -Raw
    if ($rawReport -match '(?i)[a-z]:[\\/]' -or $rawReport -match '(?i)users[\\/]') {
        throw 'First Flight smoke report contains an absolute or user-specific path.'
    }

    $report = $rawReport | ConvertFrom-Json
    Assert-SmokeValue 'schemaVersion' 'onslaught-first-flight-smoke.v6' $report.schemaVersion
    Assert-SmokeValue 'engineVersion' '4.7-stable (official)' $report.engineVersion
    Assert-SmokeValue 'exitReason' 'smoke-complete' $report.exitReason
    Assert-SmokeValue 'tick' 1256 $report.tick
    Assert-SmokeValue 'stateHash' '58b46d9b1d7979a2b7849b3b40a9fadd3fdf6bf19acc3794026bc78f21168b58' $report.stateHash
    Assert-SmokeValue 'targetsDestroyed' 0 $report.targetsDestroyed
    Assert-SmokeValue 'mode' 'Walker' $report.mode
    Assert-SmokeValue 'level100Phase' 'ReachTargetZone1' $report.level100Phase
    Assert-SmokeValue 'level100OpeningTicksRemaining' 0 $report.level100OpeningTicksRemaining
    Assert-SmokeValue 'level100TimelineTick' 1256 $report.level100TimelineTick
    Assert-SmokeValue 'level100Message' 'ReachTargetZone1' $report.level100Message
    Assert-SmokeValue 'level100PlayerControlEnabled' $true $report.level100PlayerControlEnabled
    Assert-SmokeValue 'level100FlightEnabled' $false $report.level100FlightEnabled
    Assert-SmokeValue 'level100WeaponsEnabled' $false $report.level100WeaponsEnabled
    Assert-SmokeValue 'tutorialVoicePlaying' $true $report.tutorialVoicePlaying
    Assert-SmokeValue 'totalSteps' 1256 $report.totalSteps
    Assert-SmokeValue 'toggleEdgesConsumed' 0 $report.toggleEdgesConsumed
    Assert-SmokeValue 'resetEdgesConsumed' 0 $report.resetEdgesConsumed
    Assert-SmokeValue 'resetGeneration' 0 $report.resetGeneration
    Assert-SmokeValue 'fireHeldTicksSampled' 0 $report.fireHeldTicksSampled
    Assert-SmokeValue 'firePulseEdgesConsumed' 0 $report.firePulseEdgesConsumed
    Assert-SmokeValue 'movementPulseEdgesConsumed' 0 $report.movementPulseEdgesConsumed
    Assert-SmokeValue 'cappedFrameCount' 0 $report.cappedFrameCount
    Assert-SmokeValue 'droppedElapsedTicks' 0 $report.droppedElapsedTicks
    Assert-SmokeValue 'playerVisualPresent' $true $report.playerVisualPresent
    Assert-SmokeValue 'retailAquilaMeshesPresent' $true $report.retailAquilaMeshesPresent
    Assert-SmokeValue 'retailAquilaSurfaceCount' 57 $report.retailAquilaSurfaceCount
    Assert-SmokeValue 'retailAquilaPartCount' 63 $report.retailAquilaPartCount
    Assert-SmokeValue 'retailAquilaAnimatedPartCount' 20 $report.retailAquilaAnimatedPartCount
    Assert-SmokeNear 'retailAquilaStandingClearance' 0.059322417 $report.retailAquilaStandingClearance
    Assert-SmokeValue 'retailCockpitSurfaceCount' 2 $report.retailCockpitSurfaceCount
    Assert-SmokeNear 'level100PlayerStartRelativeHeight' 0.21149921 $report.level100PlayerStartRelativeHeight
    Assert-SmokeValue 'retailLevel100FacilityCount' 2 $report.retailLevel100FacilityCount
    Assert-SmokeValue 'retailLevel100FacilitySurfaceCount' 8 $report.retailLevel100FacilitySurfaceCount
    Assert-SmokeValue 'level100ObjectiveMarkerCount' 0 $report.level100ObjectiveMarkerCount
    Assert-SmokeValue 'retailLevel100TerrainVertexCount' 4225 $report.retailLevel100TerrainVertexCount
    Assert-SmokeValue 'retailLevel100TerrainTriangleCount' 8192 $report.retailLevel100TerrainTriangleCount
    Assert-SmokeValue 'retailLevel100SkySurfaceCount' 5 $report.retailLevel100SkySurfaceCount
    Assert-SmokeValue 'targetVisualCount' 0 $report.targetVisualCount
    Assert-SmokeValue 'openingPanActive' $false $report.openingPanActive
    Assert-SmokeValue 'hudVisible' $true $report.hudVisible
    Assert-SmokeValue 'hudReady' $true $report.hudReady
    Assert-SmokeValue 'focusLossHandlerInputCleared' $true $report.focusLossHandlerInputCleared
    Assert-SmokeValue 'focusLossHandlerNeutralRearmed' $true $report.focusLossHandlerNeutralRearmed
    Assert-SmokeValue 'screenshotFileName' ([IO.Path]::GetFileName($ScreenshotPath)) $report.screenshotFileName
    Assert-SmokeValue 'screenshotWidth' $ExpectedWidth $report.screenshotWidth
    Assert-SmokeValue 'screenshotHeight' $ExpectedHeight $report.screenshotHeight

    $screenshotHash = (Get-FileHash -LiteralPath $ScreenshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
    Assert-SmokeValue 'screenshotSha256' $screenshotHash $report.screenshotSha256

    try {
        Add-Type -AssemblyName System.Drawing.Common -ErrorAction Stop
    }
    catch {
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
    }

    $bitmap = [Drawing.Bitmap]::new([string][IO.Path]::GetFullPath($ScreenshotPath))
    try {
        Assert-SmokeValue 'decoded screenshot width' $ExpectedWidth $bitmap.Width
        Assert-SmokeValue 'decoded screenshot height' $ExpectedHeight $bitmap.Height
        $colors = [Collections.Generic.HashSet[int]]::new()
        $worldColors = [Collections.Generic.HashSet[int]]::new()
        $nonBlackSamples = 0
        $worldNonBlackSamples = 0
        $worldTop = [int]($bitmap.Height * 0.27)
        $worldBottom = [int]($bitmap.Height * 0.86)
        for ($y = 0; $y -lt $bitmap.Height; $y += 32) {
            for ($x = 0; $x -lt $bitmap.Width; $x += 32) {
                $color = $bitmap.GetPixel($x, $y)
                $null = $colors.Add($color.ToArgb())
                if (($color.R + $color.G + $color.B) -gt 30) {
                    $nonBlackSamples++
                }
                if ($y -ge $worldTop -and $y -lt $worldBottom) {
                    $null = $worldColors.Add($color.ToArgb())
                    if (($color.R + $color.G + $color.B) -gt 30) {
                        $worldNonBlackSamples++
                    }
                }
            }
        }

        if ($colors.Count -lt 30 -or $nonBlackSamples -lt 200) {
            throw "First Flight screenshot appears blank or under-rendered: $($colors.Count) sampled colors, $nonBlackSamples non-black samples."
        }
        if ($worldColors.Count -lt 15 -or $worldNonBlackSamples -lt 100) {
            throw "First Flight world appears blank or under-rendered: $($worldColors.Count) sampled colors, $worldNonBlackSamples non-black samples."
        }

    }
    finally {
        $bitmap.Dispose()
    }

    $log = Get-Content -LiteralPath $LogPath -Raw
    if ($log -match '(?im)(^|\s)(SCRIPT ERROR|ERROR:|FATAL|CRASH|Unhandled exception|System\.[A-Za-z]+Exception)') {
        throw 'First Flight Godot log contains an error.'
    }

    return [pscustomobject]@{
        Valid = $true
        Tick = [int]$report.tick
        StateHash = [string]$report.stateHash
        SampledColorCount = $colors.Count
        NonBlackSampleCount = $nonBlackSamples
        WorldSampledColorCount = $worldColors.Count
        WorldNonBlackSampleCount = $worldNonBlackSamples
        ScreenshotSha256 = $screenshotHash
    }
}

Export-ModuleMember -Function 'Test-FirstFlightSmokeEvidence'
