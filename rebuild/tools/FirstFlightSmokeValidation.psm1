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
    Assert-SmokeValue 'schemaVersion' 'onslaught-first-flight-smoke.v1' $report.schemaVersion
    Assert-SmokeValue 'engineVersion' '4.7-stable (official)' $report.engineVersion
    Assert-SmokeValue 'exitReason' 'smoke-complete' $report.exitReason
    Assert-SmokeValue 'tick' 120 $report.tick
    Assert-SmokeValue 'stateHash' '5bace807dc0fc80b66f2c306b2b6a16c0b5aaea12efde3eb883e1b4577e67b62' $report.stateHash
    Assert-SmokeValue 'targetsDestroyed' 1 $report.targetsDestroyed
    Assert-SmokeValue 'mode' 'Walker' $report.mode
    Assert-SmokeValue 'totalSteps' 120 $report.totalSteps
    Assert-SmokeValue 'toggleEdgesConsumed' 1 $report.toggleEdgesConsumed
    Assert-SmokeValue 'resetEdgesConsumed' 1 $report.resetEdgesConsumed
    Assert-SmokeValue 'resetGeneration' 1 $report.resetGeneration
    Assert-SmokeValue 'fireHeldTicksSampled' 61 $report.fireHeldTicksSampled
    Assert-SmokeValue 'firePulseEdgesConsumed' 0 $report.firePulseEdgesConsumed
    Assert-SmokeValue 'movementPulseEdgesConsumed' 0 $report.movementPulseEdgesConsumed
    Assert-SmokeValue 'cappedFrameCount' 0 $report.cappedFrameCount
    Assert-SmokeValue 'droppedElapsedTicks' 0 $report.droppedElapsedTicks
    Assert-SmokeValue 'playerVisualPresent' $true $report.playerVisualPresent
    Assert-SmokeValue 'targetVisualCount' 3 $report.targetVisualCount
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

        function Measure-BrightRegion {
            param(
                [int]$Left,
                [int]$Top,
                [int]$Right,
                [int]$Bottom
            )

            $bright = 0
            for ($regionY = $Top; $regionY -lt $Bottom; $regionY += 4) {
                for ($regionX = $Left; $regionX -lt $Right; $regionX += 4) {
                    $pixel = $bitmap.GetPixel($regionX, $regionY)
                    if (($pixel.R + $pixel.G + $pixel.B) -gt 420) {
                        $bright++
                    }
                }
            }

            return $bright
        }

        $identityBright = Measure-BrightRegion 28 26 350 186
        $objectiveLeft = [Math]::Max(0, [int]($bitmap.Width / 2) - 220)
        $objectiveBright = Measure-BrightRegion $objectiveLeft 26 ($objectiveLeft + 440) 80
        $modeBright = Measure-BrightRegion ($bitmap.Width - 334) 26 ($bitmap.Width - 28) 108
        if ($identityBright -lt 300 -or $objectiveBright -lt 45 -or $modeBright -lt 40) {
            throw "First Flight HUD appears under-rendered: identity=$identityBright, objective=$objectiveBright, mode=$modeBright bright samples."
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
        HudBrightSampleCount = $identityBright + $objectiveBright + $modeBright
        WorldSampledColorCount = $worldColors.Count
        WorldNonBlackSampleCount = $worldNonBlackSamples
        ScreenshotSha256 = $screenshotHash
    }
}

Export-ModuleMember -Function 'Test-FirstFlightSmokeEvidence'
