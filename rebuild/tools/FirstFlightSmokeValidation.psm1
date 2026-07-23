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
        [Parameter(Mandatory)][string]$LogPath
    )

    foreach ($path in @($ReportPath, $LogPath)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "First Flight smoke artifact is missing: $path"
        }
    }

    $rawReport = Get-Content -LiteralPath $ReportPath -Raw
    if ($rawReport -match '(?i)[a-z]:[\\/]' -or $rawReport -match '(?i)users[\\/]') {
        throw 'First Flight smoke report contains an absolute or user-specific path.'
    }

    $report = $rawReport | ConvertFrom-Json
    Assert-SmokeValue 'schemaVersion' 'onslaught-first-flight-smoke.v12' $report.schemaVersion
    Assert-SmokeValue 'engineVersion' '4.7-stable (official)' $report.engineVersion
    Assert-SmokeValue 'exitReason' 'smoke-complete' $report.exitReason
    Assert-SmokeValue 'tick' 3244 $report.tick
    Assert-SmokeValue 'stateHash' 'c35f0796ef588ca3cd4f36a08bb2371956c071053af03ec3242e050f0d725974' $report.stateHash
    Assert-SmokeValue 'targetsDestroyed' 0 $report.targetsDestroyed
    Assert-SmokeValue 'mode' 'Walker' $report.mode
    Assert-SmokeValue 'level100OpeningTicksRemaining' 0 $report.level100OpeningTicksRemaining
    Assert-SmokeValue 'level100MissionTick' 3244 $report.level100MissionTick
    Assert-SmokeValue 'level100MissionOutcome' 'Lost' $report.level100MissionOutcome
    Assert-SmokeValue 'level100TerminalState' 'FailureMenuReady' $report.level100TerminalState
    Assert-SmokeValue 'level100PlayingMessageId' -257967449 $report.level100PlayingMessageId
    Assert-SmokeValue 'level100DeliveredMessageCount' 14 $report.level100DeliveredMessageCount
    Assert-SmokeValue 'level100DeliveredHelpCount' 1 $report.level100DeliveredHelpCount
    Assert-SmokeValue 'level100PlayerControlEnabled' $false $report.level100PlayerControlEnabled
    Assert-SmokeValue 'level100FlightEnabled' $false $report.level100FlightEnabled
    Assert-SmokeValue 'level100PulseCannonEnabled' $true $report.level100PulseCannonEnabled
    Assert-SmokeValue 'level100VulcanCannonEnabled' $false $report.level100VulcanCannonEnabled
    Assert-SmokeValue 'level100FiringRangeTargetsActive' $true $report.level100FiringRangeTargetsActive
    Assert-SmokeValue 'level100CurrentWeaponHighlighted' $false $report.level100CurrentWeaponHighlighted
    Assert-SmokeValue 'level100MessagePlaybackAvailable' $true $report.level100MessagePlaybackAvailable
    Assert-SmokeValue 'level100MessagePlaying' $true $report.level100MessagePlaying
    Assert-SmokeValue 'tutorialVoicePlaying' $true $report.tutorialVoicePlaying
    Assert-SmokeValue 'totalSteps' 3244 $report.totalSteps
    Assert-SmokeValue 'toggleEdgesConsumed' 0 $report.toggleEdgesConsumed
    Assert-SmokeValue 'resetEdgesConsumed' 0 $report.resetEdgesConsumed
    Assert-SmokeValue 'resetGeneration' 0 $report.resetGeneration
    Assert-SmokeValue 'fireHeldTicksSampled' 4 $report.fireHeldTicksSampled
    Assert-SmokeValue 'firePulseEdgesConsumed' 0 $report.firePulseEdgesConsumed
    Assert-SmokeValue 'movementPulseEdgesConsumed' 0 $report.movementPulseEdgesConsumed
    Assert-SmokeValue 'cappedFrameCount' 0 $report.cappedFrameCount
    Assert-SmokeValue 'droppedElapsedTicks' 0 $report.droppedElapsedTicks
    Assert-SmokeValue 'playerVisualPresent' $true $report.playerVisualPresent
    Assert-SmokeValue 'retailAquilaMeshesPresent' $true $report.retailAquilaMeshesPresent
    Assert-SmokeValue 'retailAquilaSurfaceCount' 112 $report.retailAquilaSurfaceCount
    Assert-SmokeValue 'retailAquilaPartCount' 63 $report.retailAquilaPartCount
    Assert-SmokeValue 'retailAquilaAnimatedPartCount' 20 $report.retailAquilaAnimatedPartCount
    Assert-SmokeNear 'retailAquilaStandingClearance' 0.059322417 $report.retailAquilaStandingClearance
    Assert-SmokeValue 'retailCockpitSurfaceCount' 10 $report.retailCockpitSurfaceCount
    Assert-SmokeNear 'level100PlayerStartRelativeHeight' 0.21149921 $report.level100PlayerStartRelativeHeight
    Assert-SmokeValue 'retailLevel100StaticObjectCount' 33 $report.retailLevel100StaticObjectCount
    Assert-SmokeValue 'retailLevel100StaticObjectSurfaceCount' 111 $report.retailLevel100StaticObjectSurfaceCount
    Assert-SmokeValue 'retailLevel100PineCount' 1481 $report.retailLevel100PineCount
    Assert-SmokeValue 'retailLevel100WaterPresent' $true $report.retailLevel100WaterPresent
    Assert-SmokeValue 'retailLevel100WaterGridVertexCount' 625 $report.retailLevel100WaterGridVertexCount
    Assert-SmokeValue 'retailLevel100WaterGridTriangleCount' 1152 $report.retailLevel100WaterGridTriangleCount
    Assert-SmokeValue 'retailLevel100ShorelineTriangleCount' 2056 $report.retailLevel100ShorelineTriangleCount
    Assert-SmokeValue 'retailLevel100TargetSurfaceCount' 6 $report.retailLevel100TargetSurfaceCount
    Assert-SmokeValue 'level100ObjectiveMarkerCount' 4 $report.level100ObjectiveMarkerCount
    Assert-SmokeValue 'retailLevel100TerrainVertexCount' 34398 $report.retailLevel100TerrainVertexCount
    Assert-SmokeValue 'retailLevel100TerrainTriangleCount' 33308 $report.retailLevel100TerrainTriangleCount
    Assert-SmokeValue 'retailLevel100SkySurfaceCount' 5 $report.retailLevel100SkySurfaceCount
    Assert-SmokeValue 'targetVisualCount' 4 $report.targetVisualCount
    Assert-SmokeValue 'openingPanActive' $false $report.openingPanActive
    Assert-SmokeValue 'hudVisible' $true $report.hudVisible
    Assert-SmokeValue 'hudReady' $true $report.hudReady
    Assert-SmokeValue 'focusLossHandlerInputCleared' $true $report.focusLossHandlerInputCleared
    Assert-SmokeValue 'focusLossHandlerNeutralRearmed' $true $report.focusLossHandlerNeutralRearmed
    Assert-SmokeValue 'coldClickToStart' $true $report.coldClickToStart
    Assert-SmokeValue 'coldMainMenu' $true $report.coldMainMenu
    Assert-SmokeValue 'coldLevelSelect' $true $report.coldLevelSelect
    Assert-SmokeValue 'coldLoading' $true $report.coldLoading
    Assert-SmokeValue 'coldGameplay' $true $report.coldGameplay
    Assert-SmokeValue 'cursorPolicyVisibleAtFrontend' $true $report.cursorPolicyVisibleAtFrontend
    Assert-SmokeValue 'cursorPolicyHiddenAtLoading' $true $report.cursorPolicyHiddenAtLoading
    Assert-SmokeValue 'cursorPolicyCapturedAtGameplay' $true $report.cursorPolicyCapturedAtGameplay
    Assert-SmokeValue 'focusLossCursorPolicyVisible' $true $report.focusLossCursorPolicyVisible
    Assert-SmokeValue 'focusGainCursorPolicyCaptured' $true $report.focusGainCursorPolicyCaptured
    Assert-SmokeValue 'missionTerminalHandoffEntered' $true $report.missionTerminalHandoffEntered
    Assert-SmokeValue 'missionFailureReason' 'PlayerDeath' $report.missionFailureReason
    Assert-SmokeValue 'terminalCursorPolicyVisible' $true $report.terminalCursorPolicyVisible
    Assert-SmokeValue 'retryRequested' $true $report.retryRequested
    Assert-SmokeValue 'retryGameplayActivated' $true $report.retryGameplayActivated
    Assert-SmokeValue 'retrySessionFresh' $true $report.retrySessionFresh
    Assert-SmokeValue 'returnToMainMenuRequested' $true $report.returnToMainMenuRequested
    Assert-SmokeValue 'returnedToMainMenu' $true $report.returnedToMainMenu
    Assert-SmokeValue 'worldReleasedAtMainMenu' $true $report.worldReleasedAtMainMenu
    Assert-SmokeValue 'mainMenuCursorPolicyVisible' $true $report.mainMenuCursorPolicyVisible
    Assert-SmokeValue 'finalFrontendScreen' 'MainMenu' $report.finalFrontendScreen

    $log = Get-Content -LiteralPath $LogPath -Raw
    if ($log -match '(?im)(^|\s)(SCRIPT ERROR|ERROR:|FATAL|CRASH|Unhandled exception|System\.[A-Za-z]+Exception)') {
        throw 'First Flight Godot log contains an error.'
    }

    return [pscustomobject]@{
        Valid = $true
        Tick = [int]$report.tick
        StateHash = [string]$report.stateHash
    }
}

Export-ModuleMember -Function 'Test-FirstFlightSmokeEvidence'
