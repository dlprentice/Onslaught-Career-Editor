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
    Assert-SmokeValue 'engineVersion' '4.7.1-stable (official)' $report.engineVersion
    Assert-SmokeValue 'exitReason' 'smoke-complete' $report.exitReason
    Assert-SmokeValue 'tick' 2148 $report.tick
    # REPINNED 2026-07-31 BY THE 30 Hz -> 20 Hz CORE MIGRATION (WORKSTREAM 4).
    # Two independent native Godot runs produced byte-identical reports at this
    # value, and it also matches the in-process scenario pinned by
    # InteractiveSessionTests, which is an independent implementation of the
    # same tape through a different host.
    #
    # FIELD-LEVEL ACCOUNTING - which fields moved and why. FOUR independent
    # causes, any one of which alone would move this hash, so do not attribute
    # it to a single one:
    #   1. StateHasher version 32 -> 33. A hashed literal.
    #   2. Level100ActorMechanicsSnapshot.RetailBaseTickAccumulatorThirtieths
    #      was DELETED. It was the 20-of-every-30 base-tick accumulator, which
    #      is the identity at 20 Hz. Four bytes leave every hashed tick.
    #   3. StateHasher hashes state.Tick first, and the tape's terminal tick is
    #      2148 where it was 3228 - within 0.2 s of the same simulated time.
    #   4. Every trajectory is re-integrated against the reconverted constants
    #      (retentions now the shipped floats verbatim, gravity now the shipped
    #      0.01/0.002/0.005, input impulses reconverted under the damped-input
    #      rule).
    #
    # The report fields that MOVED with it, all re-derived rather than nudged:
    #   tick / level100MissionTick / totalSteps  3228 -> 2148
    #   retailLevel100TerrainVertexCount         34398 -> 34499
    #   retailLevel100TerrainTriangleCount       33308 -> 33476
    # The fields that did NOT move, and are the evidence the tape still proves
    # what it proved: targetsDestroyed 0, mode Walker, outcome Running,
    # terminal None, the six script-gate booleans, fireHeldTicksSampled 4, all
    # five edge counters 0, cappedFrameCount 0, droppedElapsedTicks 0,
    # level100DeliveredHelpCount 1, level100ObjectiveMarkerCount 4, the
    # thirteen delivered message ids and their speakers,
    # targetVisualCount 9, openingPanActive false, and the whole retail-geometry
    # block.
    # REPINNED AGAIN 2026-08-01 by the VERTICAL DATUM (#154) and the
    # LOOK-RESPONSE TABLE (#161).
    # d4967b1206f851a27ef2bb998ffaae2575fb898f15dec67cdbead987b0737ed3
    # -> e41f55ff98b7d6e7b17a5c85e443533c46147dc81d2b0188ea56bbd89277dc16.
    #
    # PROTOCOL SATISFIED BEFORE PINNING: two native Godot runs produced
    # BYTE-IDENTICAL reports - sha256
    # a71fd60ad692e695abe42250135d2cf90b3838bc02d3c1ff35739e27a4b59a24,
    # 3,859 bytes, all 86 fields equal - and the value also matches the
    # in-process scenario pinned by InteractiveSessionTests, which is an
    # independent implementation of the same tape through a different host.
    #
    # FIELD-LEVEL ACCOUNTING: stateHash is the ONLY field that moved. Every
    # other field this gate pins is unchanged and re-asserted below - tick /
    # level100MissionTick / totalSteps 2148, targetsDestroyed 0, mode Walker,
    # outcome Running, terminal None, targetVisualCount 9, the thirteen
    # delivered message ids and their speakers, level100DeliveredHelpCount 1,
    # level100ObjectiveMarkerCount 4, fireHeldTicksSampled 4, four release edges,
    # the other four edge counters 0, cappedFrameCount 0, droppedElapsedTicks 0, openingPanActive
    # false, and the whole retail-geometry block including
    # retailLevel100TerrainVertexCount 34499 and TriangleCount 33476.
    #
    # WHY IT MOVED, and it is two causes rather than one:
    #   1. #154. StateHasher hashes every actor pose and the definition-set
    #      identity. The datum correction moved 54 manifest leaves - the
    #      vertical of all 44 actors and all 10 spawns - and the general
    #      CThing::Init support clamp in Level100ActorRegistry.SeatOnGround now
    #      seats every class rather than ground vehicles alone. The tape's own
    #      behaviour did not change: it is walker-only, destroys nothing, and
    #      every pinned schedule field above is identical.
    #   2. #161. The look table is now one entry per representable input, which
    #      changes 187 of the 1,001 responses by one permille each. Measured
    #      alone on 2026-07-31 it did NOT move this hash - the tape's probe
    #      points are all on entries the two tables agree about - so this is
    #      #154's move with #161 riding along, not a sum of two.
    # StateHasher v36 adds current and desired zoom after v35's selected
    # Walker/Jet slots and Twin Vulcan reload countdown. This tape stays at
    # unzoomed 1000/1000, so the move is structural; the in-process canonical
    # tape independently measures the exact repin and native remains the host
    # check.
    Assert-SmokeValue 'stateHash' '997c20348dd9c4cbd7d59011060aa1c18e2906d912bba0e035671e60fe3bb1e5' $report.stateHash
    Assert-SmokeValue 'targetsDestroyed' 0 $report.targetsDestroyed
    Assert-SmokeValue 'mode' 'Walker' $report.mode
    Assert-SmokeValue 'level100OpeningTicksRemaining' 0 $report.level100OpeningTicksRemaining
    Assert-SmokeValue 'level100MissionTick' 2148 $report.level100MissionTick
    Assert-SmokeValue 'level100MissionOutcome' 'Running' $report.level100MissionOutcome
    Assert-SmokeValue 'level100TerminalState' 'None' $report.level100TerminalState
    # The message sequence the released script has requested by this tick is a
    # Core fact and is pinned exactly, in order.
    # Thirteen, not fourteen, since the released message-box gate
    # (Level100MissionTiming.MessageBoxAllowedTick / MessageAdvanceDelayTicks):
    # the script blocks on PlayCharMessageWait until the box may play, so the
    # whole chain sits later and TUTORIAL_PULSE_CANNON_2 (-1715818922) falls
    # outside this scenario's fixed tick budget. The scenario was not extended
    # to keep the old count - that would be fitting the gate to the pin.
    #
    # STILL THIRTEEN AFTER THE 20 Hz MIGRATION, but by a much smaller margin
    # than before and for a reason worth reading: at the faithful two-thirds
    # duration of 2152 the fourteenth message IS delivered, on tick 2150. The
    # scenario ends at 2148 instead, and FirstFlightSmokeScenario.DurationTicks
    # carries the criterion that decided it - the report has to be sampled where
    # the deterministic message schedule is quiet, or the three mixer-derived
    # fields below couple into the implication assertions at the end of this
    # gate. Read that comment before treating this thirteen as unchanged.
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
    # Absent is also legal: RetailCharacterMessageHandoffSeconds is a 4/20s gap
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
    Assert-SmokeValue 'totalSteps' 2148 $report.totalSteps
    Assert-SmokeValue 'toggleEdgesConsumed' 0 $report.toggleEdgesConsumed
    Assert-SmokeValue 'resetEdgesConsumed' 0 $report.resetEdgesConsumed
    Assert-SmokeValue 'resetGeneration' 0 $report.resetGeneration
    Assert-SmokeValue 'fireHeldTicksSampled' 4 $report.fireHeldTicksSampled
    Assert-SmokeValue 'firePulseEdgesConsumed' 4 $report.firePulseEdgesConsumed
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
    # MOVED 2026-07-31 by task #114, the two ambient aircraft. This is the
    # countable evidence that they are now DRAWN, so it has to move: the
    # WorldSnapshot.Targets projection admitted only StaticTargets and
    # TargetTrucks and now also carries the two ungrouped world actors, and
    # FirstFlightWorldView registers their meshes.
    #
    # Both numbers are arithmetic over shipped material groups, not observations
    # accepted on trust:
    #   visuals   7 -> 9   + U-17 Highside Transporter, + ambient Air Trainer
    #   surfaces  9 -> 12  the transporter's `m_f_lifter.msh.aya` emits TWO
    #                      material groups (base slots 0 and 2 against the same
    #                      Chrome3 reflection) and the Air Trainer's
    #                      `m_FA_F24_training.msh.aya` emits ONE, the Target
    #                      Tank's group verbatim.
    # The 9 before was 3 Target Tanks (1 group each) + Warehouse (3) + 3 Target
    # Trucks (1 each). Nothing existing changed shape.
    Assert-SmokeValue 'retailLevel100TargetSurfaceCount' 12 $report.retailLevel100TargetSurfaceCount
    Assert-SmokeValue 'level100ObjectiveMarkerCount' 4 $report.level100ObjectiveMarkerCount
    # THESE TWO ARE NOT ASSET FACTS, and the 20 Hz migration is what made that
    # visible. Level100HeightFieldAsset selects a per-tile geometry LOD from the
    # squared distance between the tile centre and the SMOOTHED CAMERA
    # (`SelectTiles`, the `projectedSize` band), so the vertex and triangle
    # totals are a pure function of where the camera is on the frame the report
    # is written. They sit in this file's retail-geometry block beside genuinely
    # static counts (pine count, static-object surfaces, the water grid), which
    # is why they were read as static; they are not.
    #
    # Repinned 2026-07-31: 34398 -> 34499 vertices, 33308 -> 33476 triangles.
    # The cause is the re-flown smoke tape ending at a marginally different
    # player pose, not any change to the height field, whose source asset digest
    # is unchanged. Deterministic under --fixed-fps and proven so by the
    # two byte-identical native reports this repin required.
    Assert-SmokeValue 'retailLevel100TerrainVertexCount' 34499 $report.retailLevel100TerrainVertexCount
    Assert-SmokeValue 'retailLevel100TerrainTriangleCount' 33476 $report.retailLevel100TerrainTriangleCount
    Assert-SmokeValue 'retailLevel100SkySurfaceCount' 5 $report.retailLevel100SkySurfaceCount
    # MOVED 2026-07-31 with retailLevel100TargetSurfaceCount above, same cause:
    # the two ambient aircraft are now rendered world actors. See the comment
    # there for the arithmetic.
    Assert-SmokeValue 'targetVisualCount' 9 $report.targetVisualCount
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
