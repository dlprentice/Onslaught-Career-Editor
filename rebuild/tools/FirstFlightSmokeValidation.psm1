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

function Assert-SmokeSequence {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][AllowEmptyCollection()][int[]]$Expected,
        [Parameter(Mandatory)][AllowEmptyCollection()][int[]]$Actual
    )

    if ($Expected.Count -ne $Actual.Count -or
        @(Compare-Object -ReferenceObject $Expected -DifferenceObject $Actual -SyncWindow 0).Count -ne 0) {
        throw ("First Flight smoke '$Name' mismatch: expected '" +
            ($Expected -join ',') + "', observed '" + ($Actual -join ',') + "'.")
    }
}

function Assert-SmokeStringSequence {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]]$Expected,
        [Parameter(Mandatory)][AllowEmptyCollection()][string[]]$Actual
    )

    if ($Expected.Count -ne $Actual.Count -or
        @(Compare-Object -ReferenceObject $Expected -DifferenceObject $Actual -SyncWindow 0).Count -ne 0) {
        throw ("First Flight smoke '$Name' mismatch: expected '" +
            ($Expected -join ',') + "', observed '" + ($Actual -join ',') + "'.")
    }
}

# For an ordered observation whose CONTENT is determined by the simulation but
# whose LENGTH is decided by how far the audio mixer has advanced in real
# seconds. The strongest honest claim is that what was observed is an exact
# ordered prefix of the deterministic sequence - no skipped, reordered or
# invented entries - together with a floor on how far it got.
function Assert-SmokePrefixOf {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$SequenceName,
        [Parameter(Mandatory)][AllowEmptyCollection()][int[]]$Sequence,
        [Parameter(Mandatory)][AllowEmptyCollection()][int[]]$Actual,
        [Parameter(Mandatory)][int]$MinimumLength
    )

    if ($Actual.Count -lt $MinimumLength) {
        throw ("First Flight smoke '$Name' is too short: expected at least " +
            "$MinimumLength entries of $SequenceName, observed " +
            "$($Actual.Count) '" + ($Actual -join ',') + "'.")
    }

    if ($Actual.Count -gt $Sequence.Count) {
        throw ("First Flight smoke '$Name' is longer than " +
            "${SequenceName}: observed $($Actual.Count) entries against " +
            "$($Sequence.Count).")
    }

    $prefix = @($Sequence | Select-Object -First $Actual.Count)
    if (@(Compare-Object -ReferenceObject $prefix -DifferenceObject $Actual -SyncWindow 0).Count -ne 0) {
        throw ("First Flight smoke '$Name' mismatch: expected the ordered " +
            "prefix of $SequenceName '" + ($prefix -join ',') +
            "', observed '" + ($Actual -join ',') + "'.")
    }
}

# For a one-directional bound between two reported observations. Both sides may
# legitimately be false at the sampled tick, so neither can be pinned, but the
# implication holds at every instant and fails on a real defect.
function Assert-SmokeImplies {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][AllowNull()]$Antecedent,
        [Parameter(Mandatory)][string]$ConsequentName,
        [Parameter(Mandatory)][AllowNull()]$Consequent
    )

    if ($Antecedent -and -not $Consequent) {
        throw ("First Flight smoke '$Name' implies '$ConsequentName': " +
            "observed '$Name' true with '$ConsequentName' '$Consequent'.")
    }
}

# For values whose exact identity is genuinely not determined by the tick the
# report is captured at. Pinning one of these produces a test that fails on
# host speed rather than on a behaviour change.
function Assert-SmokeMemberOf {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$SetName,
        [Parameter(Mandatory)][AllowEmptyCollection()][int[]]$Set,
        [Parameter(Mandatory)][AllowNull()]$Actual,
        # Absent is a legal observation for a mixer-derived identity sampled in
        # the inter-message handoff gap. Off by default so a field that must
        # always be present still fails when it disappears.
        [switch]$AllowAbsent
    )

    if ($null -eq $Actual) {
        if ($AllowAbsent) {
            return
        }
        throw "First Flight smoke '$Name' is absent; expected a member of $SetName."
    }

    if ($Set -notcontains [int]$Actual) {
        throw ("First Flight smoke '$Name' mismatch: expected a member of " +
            "$SetName '" + ($Set -join ',') + "', observed '$Actual'.")
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
    Assert-SmokeValue 'schemaVersion' 'onslaught-first-flight-smoke.v17' $report.schemaVersion
    Assert-SmokeValue 'engineVersion' '4.7-stable (official)' $report.engineVersion
    Assert-SmokeValue 'exitReason' 'smoke-complete' $report.exitReason
    Assert-SmokeValue 'tick' 3228 $report.tick
    # Measured 2026-07-28 after the reviewed Core changes landed: two independent
    # native Godot runs produced byte-identical reports at tick 3228, and the
    # hash also matches the in-process scenario pinned by InteractiveSessionTests.
    Assert-SmokeValue 'stateHash' '0f1fb80918c5acb42f2c7025736b6690d9a47109b594d0307ec90d7ecd25f5ba' $report.stateHash
    Assert-SmokeValue 'targetsDestroyed' 0 $report.targetsDestroyed
    Assert-SmokeValue 'mode' 'Walker' $report.mode
    Assert-SmokeValue 'level100OpeningTicksRemaining' 0 $report.level100OpeningTicksRemaining
    Assert-SmokeValue 'level100MissionTick' 3228 $report.level100MissionTick
    Assert-SmokeValue 'level100MissionOutcome' 'Running' $report.level100MissionOutcome
    Assert-SmokeValue 'level100TerminalState' 'None' $report.level100TerminalState
    # The message sequence the released script has requested by this tick is a
    # Core fact and is pinned exactly, in order.
    # Thirteen, not fourteen, since the released message-box gate
    # (Level100MissionTiming.MessageBoxAllowedTick / MessageAdvanceDelayTicks):
    # the script blocks on PlayCharMessageWait until the box may play, so the
    # whole chain sits later and TUTORIAL_PULSE_CANNON_2 (-1715818922) now falls
    # outside this scenario's fixed tick budget. The scenario was not extended
    # to keep the old count - that would be fitting the gate to the pin.
    $expectedMessageIds = @(
        292562, 293386, 296682, -1575499396, -257967449, 82987417, 4422830,
        175347826, 4458134, 4493438, 295858, 1339691000, 669198996)
    Assert-SmokeSequence 'level100DeliveredMessageIds' $expectedMessageIds `
        $report.level100DeliveredMessageIds
    Assert-SmokeValue 'level100DeliveredMessageCount' 13 $report.level100DeliveredMessageCount
    # Recorded where the host forwards Core message events to the audio adapter,
    # so it cross-checks the audio path against the HUD path above rather than
    # restating it. Speaker identity is Core-ordered and was previously unpinned.
    Assert-SmokeSequence 'level100AudioQueuedMessageIds' $expectedMessageIds `
        $report.level100AudioQueuedMessageIds
    Assert-SmokeSequence 'level100AudioQueuedSpeakerIds' @(
        1508464, 1508464, 1508464, 1508464, 10565784, 1508464, 1508464,
        1508464, 1508464, 1508464, 1508464, 1508464,
        1508464) $report.level100AudioQueuedSpeakerIds
    # Which of those the Godot mixer is audibly playing at the same tick is NOT
    # a Core fact. AudioStreamPlayer playback advances on the audio thread in
    # wall-clock seconds while --fixed-fps advances the simulation as fast as
    # the host allows, so the voice queue trails the script by a host-dependent
    # amount. Six runs on one host with a byte-identical stateHash produced
    # -257967449 three times and 82987417 three times; this assertion was
    # previously pinned to 82987417 and failed whenever the host was loaded.
    # Bound it to the delivered sequence instead of pinning a run.
    # Absent is also legal: RetailCharacterMessageHandoffSeconds is a 6/30s gap
    # in which no message is active at all. A report captured in that gap made
    # this field null and failed parameter binding before the previous fix's own
    # null branch could run, so the v14 gate still flaked on host speed.
    Assert-SmokeMemberOf 'level100PlayingMessageId' 'level100DeliveredMessageIds' `
        $report.level100DeliveredMessageIds $report.level100PlayingMessageId -AllowAbsent
    # The claim the three pinned mixer booleans below were standing in for -
    # "the voice pipeline really consumed the Core message stream" - stated over
    # something the simulation decides. Accumulated across every smoke frame, so
    # host speed changes only how far the prefix got, never its content.
    Assert-SmokePrefixOf 'level100VoiceStartedMessageIds' 'level100DeliveredMessageIds' `
        $report.level100DeliveredMessageIds $report.level100VoiceStartedMessageIds `
        -MinimumLength 1
    # Held on every sampled frame, not just the reported tick: anything audible
    # was an identified, Core-requested message, and gameplay was never paused.
    Assert-SmokeValue 'level100VoicePlaybackConsistent' $true `
        $report.level100VoicePlaybackConsistent
    Assert-SmokeValue 'level100DeliveredHelpCount' 1 $report.level100DeliveredHelpCount
    Assert-SmokeValue 'level100PlayerControlEnabled' $true $report.level100PlayerControlEnabled
    Assert-SmokeValue 'level100FlightEnabled' $false $report.level100FlightEnabled
    Assert-SmokeValue 'level100PulseCannonEnabled' $true $report.level100PulseCannonEnabled
    Assert-SmokeValue 'level100VulcanCannonEnabled' $false $report.level100VulcanCannonEnabled
    Assert-SmokeValue 'level100FiringRangeTargetsActive' $true $report.level100FiringRangeTargetsActive
    Assert-SmokeValue 'level100CurrentWeaponHighlighted' $false $report.level100CurrentWeaponHighlighted
    # level100MessagePlaybackAvailable, level100MessagePlaying and
    # tutorialVoicePlaying are all AudioStreamPlayer.Playing derived. All three
    # were observed FALSE together in a passing-Core run whose stateHash was
    # byte-identical to runs that reported true - the report simply landed in
    # the handoff gap. They are reported for the reader and bounded by the
    # implications that do hold at every instant, never pinned.
    Assert-SmokeImplies 'level100MessagePlaying' $report.level100MessagePlaying `
        'level100MessagePlaybackAvailable' $report.level100MessagePlaybackAvailable
    Assert-SmokeImplies 'tutorialVoicePlaying' $report.tutorialVoicePlaying `
        'level100PlayingMessageId' ($null -ne $report.level100PlayingMessageId)
    Assert-SmokeImplies 'level100MessagePlaybackAvailable' `
        $report.level100MessagePlaybackAvailable `
        'level100PlayingMessageId' ($null -ne $report.level100PlayingMessageId)
    Assert-SmokeValue 'totalSteps' 3228 $report.totalSteps
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
    # The 13 separately animated static-world subparts are now bound and counted
    # in addition to the original 111 object surfaces.
    Assert-SmokeValue 'retailLevel100StaticObjectSurfaceCount' 124 $report.retailLevel100StaticObjectSurfaceCount
    Assert-SmokeValue 'retailLevel100PineCount' 1481 $report.retailLevel100PineCount
    Assert-SmokeValue 'retailLevel100WaterPresent' $true $report.retailLevel100WaterPresent
    Assert-SmokeValue 'retailLevel100WaterGridVertexCount' 625 $report.retailLevel100WaterGridVertexCount
    Assert-SmokeValue 'retailLevel100WaterGridTriangleCount' 1152 $report.retailLevel100WaterGridTriangleCount
    Assert-SmokeValue 'retailLevel100ShorelineTriangleCount' 2056 $report.retailLevel100ShorelineTriangleCount
    Assert-SmokeValue 'retailLevel100TargetSurfaceCount' 9 $report.retailLevel100TargetSurfaceCount
    Assert-SmokeValue 'level100ObjectiveMarkerCount' 4 $report.level100ObjectiveMarkerCount
    Assert-SmokeValue 'retailLevel100TerrainVertexCount' 34398 $report.retailLevel100TerrainVertexCount
    Assert-SmokeValue 'retailLevel100TerrainTriangleCount' 33308 $report.retailLevel100TerrainTriangleCount
    Assert-SmokeValue 'retailLevel100SkySurfaceCount' 5 $report.retailLevel100SkySurfaceCount
    Assert-SmokeValue 'targetVisualCount' 7 $report.targetVisualCount
    Assert-SmokeValue 'openingPanActive' $false $report.openingPanActive
    Assert-SmokeValue 'hudVisible' $true $report.hudVisible
    Assert-SmokeValue 'hudReady' $true $report.hudReady
    Assert-SmokeValue 'focusLossHandlerInputCleared' $true $report.focusLossHandlerInputCleared
    Assert-SmokeValue 'focusLossHandlerNeutralRearmed' $true $report.focusLossHandlerNeutralRearmed
    Assert-SmokeValue 'coldClickToStart' $true $report.coldClickToStart
    Assert-SmokeValue 'coldMainMenu' $true $report.coldMainMenu
    Assert-SmokeValue 'coldDevSelect' $true $report.coldDevSelect
    Assert-SmokeValue 'coldLevelSelect' $true $report.coldLevelSelect
    # MISSION BRIEFING and SELECT CONFIGURATION are traversal evidence only. Their
    # visual parity is measured by pixel capture, not asserted here.
    Assert-SmokeValue 'coldMissionBriefing' $true $report.coldMissionBriefing
    Assert-SmokeValue 'coldSelectConfiguration' $true $report.coldSelectConfiguration
    Assert-SmokeValue 'coldLoading' $true $report.coldLoading
    Assert-SmokeValue 'coldGameplay' $true $report.coldGameplay
    Assert-SmokeValue 'cursorPolicyCustomAtFrontend' $true $report.cursorPolicyCustomAtFrontend
    Assert-SmokeValue 'cursorPolicyHiddenAtLoading' $true $report.cursorPolicyHiddenAtLoading
    # Replaces cursorPolicyCapturedAtGameplay, which observed False in 1 of 6
    # runs because Godot cannot capture an unfocused window - it pinned whether
    # the user had clicked away. The policy itself is pinned over all four
    # (focused, paused) inputs, evaluated through the product's own
    # UpdateGameplayCursorMode, and activation is required to have applied that
    # policy to whatever focus actually was. windowFocusedAtGameplay is reported
    # and deliberately NOT asserted: it is host desktop state, not evidence.
    Assert-SmokeStringSequence 'gameplayCursorPolicy' @(
        'Captured', 'Visible', 'Visible', 'Visible') $report.gameplayCursorPolicy
    Assert-SmokeValue 'cursorPolicyAppliedAtGameplay' $true $report.cursorPolicyAppliedAtGameplay
    Assert-SmokeValue 'focusLossCursorPolicyVisible' $true $report.focusLossCursorPolicyVisible
    Assert-SmokeValue 'focusGainCursorPolicyCaptured' $true $report.focusGainCursorPolicyCaptured
    Assert-SmokeValue 'retryRequested' $true $report.retryRequested
    Assert-SmokeValue 'retryGameplayActivated' $true $report.retryGameplayActivated
    Assert-SmokeValue 'retrySessionFresh' $true $report.retrySessionFresh
    Assert-SmokeValue 'returnToMainMenuRequested' $true $report.returnToMainMenuRequested
    Assert-SmokeValue 'returnedToMainMenu' $true $report.returnedToMainMenu
    Assert-SmokeValue 'worldReleasedAtMainMenu' $true $report.worldReleasedAtMainMenu
    Assert-SmokeValue 'mainMenuCursorPolicyCustom' $true $report.mainMenuCursorPolicyCustom
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

Export-ModuleMember -Function @(
    'Test-FirstFlightSmokeEvidence'
    'Assert-SmokeSequence'
    'Assert-SmokeStringSequence'
    'Assert-SmokeMemberOf'
    'Assert-SmokePrefixOf'
    'Assert-SmokeImplies'
)
