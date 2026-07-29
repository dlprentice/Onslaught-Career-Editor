// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public static class Level100MissionTiming
{
    // Consumed evidence only: supported 100_res_PC.aya SHA-256
    // ed6350c0e214d00ab1bf6a7bd137fba3e77d0afe19a6dc4c0607f56ac037496a;
    // exact LevelScript object SHA-256
    // 73eb349b9c4b5c5d7294b2183cd4d4aebe024c5d3c8cda9be685bd1463ed6fb1;
    // readable LevelScript.msl SHA-256
    // d51f8864564b5bde872092ec822df5af49daac16563f500719135f1a8c6c04a4.
    // Steam Ghidra establishes the object loader,
    // opcode dispatch (0x0052d3d0), saved-state restore (0x00533840), Pause
    // (0x00537c70), message-wait path (0x005375f0), and terminal functions
    // (0x0046f2f0/0x0046f430). Voice ticks are shipped Ogg granules plus the
    // evidenced 18-tick wait post-roll. No retail executable is a play dependency.

    public const int AuthoredTriggerRadiusMillimeters = 5_000;
    public const int HealthPollCadenceTicks = SimulationConstants.TicksPerSecond;
    public const int SuccessCountdownTicks = 5 * SimulationConstants.TicksPerSecond;
    public const int FailureCountdownTicks = 5 * SimulationConstants.TicksPerSecond;
    public const int FailureMenuDelayTicks = SimulationConstants.TicksPerSecond / 2;

    public static SimVector2 TriggerPosition(Level100MissionTrigger trigger) => trigger switch
    {
        Level100MissionTrigger.TargetZone1 => SimulationConstants.Level100TargetZone1Position,
        Level100MissionTrigger.FiringRange => SimulationConstants.Level100FiringRangePosition,
        Level100MissionTrigger.TargetZone2 => new(-56_688, -62_250),
        Level100MissionTrigger.TargetZone3 => new(-57_938, 2_625),
        Level100MissionTrigger.TargetZone4 => new(0, -31),
        _ => throw new ArgumentOutOfRangeException(nameof(trigger)),
    };

    public static bool RequiresNotInJetMode(Level100MissionTrigger trigger) => trigger is
        Level100MissionTrigger.TargetZone2 or
        Level100MissionTrigger.TargetZone3 or
        Level100MissionTrigger.TargetZone4;

    /// <summary>
    /// The released <c>InJetMode()</c> script builtin, read out of the pristine
    /// executable rather than inferred.
    /// </summary>
    /// <remarks>
    /// The registered handler at <c>0x005380f0</c> is nine instructions:
    /// <code>
    ///   8B 49 10          MOV  ECX, [ECX+0x10]
    ///   56 33 F6          PUSH ESI ; XOR ESI, ESI          ; result = FALSE
    ///   F6 41 34 08       TEST byte [ECX+0x34], 8          ; THING_TYPE_BATTLE_ENGINE
    ///   74 0E             JZ   done                        ; anything else is never in jet mode
    ///   E8 1F 00 ED FF    CALL 0x00408120
    ///   85 C0  75 05      TEST EAX, EAX ; JNZ done
    ///   BE 01 00 00 00    MOV  ESI, 1                      ; result = TRUE
    /// </code>
    /// and <c>0x00408120</c> returns true when
    /// <c>*(int*)(this+0x260) == 2 &amp;&amp; DAT_00672fd0 - *(float*)(this+0xcc) &lt; _DAT_005d85ec</c>.
    /// <para>
    /// So <c>InJetMode()</c> is the <em>negation</em> of "is a walker that
    /// touched the ground recently". <c>+0x260 == 2</c> is the walker state —
    /// <c>CPlayer::ReceiveButtonAction</c> (<c>0x004D3110</c>) routes
    /// button <c>0x15</c> to <c>ActivateLandingJets</c> only inside that same
    /// <c>== 2</c> branch, which is <c>BATTLE_ENGINE_STATE_WALKER</c> in
    /// <c>references/Onslaught/Player.cpp</c>. The threshold at
    /// <c>0x005D85EC</c> reads <c>00 00 00 3F</c> in the pristine binary
    /// (sha256 74154bfa…7750), i.e. <b>0.5 s</b> — note that the GPL source's
    /// only other use of this predicate,
    /// <c>CBattleEngineWalkerPart::Move</c>'s
    /// <c>GetTime() - mLastTimeOnGround &lt; 0.3f</c>, says 0.3. The shipped
    /// bytes win; the reference does not describe this executable here.
    /// </para>
    /// <para>
    /// This matters because <c>TargetZone2/3/4.msl</c> gate on
    /// <c>InJetMode() == FALSE</c>. Reading that as "not in jet mode" accepted
    /// an airborne walker, so beats 6, 8 and 10 could be completed by morphing
    /// mid-air over the volume and never landing at all.
    /// </para>
    /// </remarks>
    public static Level100MissionJetModeState JetModeState(
        VehicleMode mode,
        VehicleTransition transition,
        int ticksSinceGroundContact) =>
        mode == VehicleMode.Walker &&
        transition == VehicleTransition.None &&
        ticksSinceGroundContact < GroundContactRecencyTicks
            ? Level100MissionJetModeState.NotInJetMode
            : Level100MissionJetModeState.InJetMode;

    /// <summary>
    /// 0.5 s, the shipped <c>_DAT_005d85ec</c> threshold. Written in seconds so
    /// a Core tick-rate change leaves it meaning the same thing.
    /// </summary>
    public const int GroundContactRecencyTicks = SimulationConstants.TicksPerSecond / 2;

    /// <summary>Converts an authored MissionScript <c>Pause</c> duration to Core ticks.</summary>
    /// <remarks>
    /// Shipped registry row 4 binds <c>Pause</c> to <c>0x00537C70</c>. The
    /// pristine body reads argument zero through the float getter, clones the
    /// current script execution, appends that continuation to
    /// <c>IScript+0x28</c>, and schedules event <c>0x7D1</c> for
    /// <c>currentTime + seconds</c>. A trace-hashed copied-runtime query observed
    /// the handler once with equal symbolic/numeric <c>TTD.Calls</c> counts and
    /// observed its continuation-list/global-flag side effects. The durable
    /// evidence summary is in
    /// <c>reverse-engineering/binary-analysis/functions/IScript.cpp.md</c>.
    /// This is script suspension, not the player-facing game-pause menu.
    /// </remarks>
    internal static int PauseTicks(float seconds)
    {
        if (!float.IsFinite(seconds) || seconds < 0)
        {
            throw new InvalidOperationException("The released LevelScript requested an invalid pause.");
        }

        return checked((int)MathF.Round(
            seconds * SimulationConstants.TicksPerSecond,
            MidpointRounding.AwayFromZero));
    }

    /// <summary>
    /// One released 20 Hz event-manager frame, expressed in whole Core ticks.
    /// 30/20 = 1.5, and a released <c>NEXT_FRAME</c> event cannot fire before
    /// the frame boundary, so it rounds up.
    /// </summary>
    public const int ReleasedEventFrameTicks =
        (SimulationConstants.TicksPerSecond +
            Level100ActorMechanics.RetailBaseTicksPerSecond - 1) /
        Level100ActorMechanics.RetailBaseTicksPerSecond;

    /// <summary>
    /// The first Core tick on which a character message may become active
    /// <b>when the player lets the opening pan run to its full length</b>.
    /// </summary>
    /// <remarks>
    /// <para>
    /// The released level script runs from level start — it deactivates the
    /// player, disables both weapons and initialises the four primary
    /// objectives before the opening pan is over — but the message box is
    /// <em>not permitted to play anything</em> until the game leaves
    /// <c>GAME_STATE_PANNING</c>. <c>CGame::StartPlayingState</c>
    /// (<c>references/Onslaught/game.cpp:3026-3031</c>) is the whole law:
    /// </para>
    /// <code>
    ///   mGameState = GAME_STATE_PLAYING ;
    ///   SCRIPT_EVENT_NB.PostEvent("game playing");
    ///   EVENT_MANAGER.AddEvent(ALLOWED_TO_PLAY_MESSAGES, mMessageBox, NEXT_FRAME) ;
    /// </code>
    /// <para>
    /// So the greeting is held, not skipped, and every later message inherits
    /// the same offset. <c>FINISHED_PANNING</c> arrives at the end of the
    /// six-second pan (<c>SimulationConstants.Level100OpeningPanTicks</c> =
    /// 180, and <c>CPanCamera::GetShowHUD</c> is false for all of it), and
    /// <c>ALLOWED_TO_PLAY_MESSAGES</c> is one released event frame later.
    /// 180 + 2 = <b>182</b>, which is exactly the tick two fresh uninterrupted
    /// app-owned Steam runs measured for the first message boundary
    /// (<c>rebuild/PROVENANCE.md</c>, "HUD introduction 182..351").
    /// </para>
    /// <para>
    /// This is why the reconstruction showed no greeting at all: the script
    /// initialiser ran at tick 0, so HUD_01 was delivered and had already
    /// finished before the HUD became visible at tick ~179, and the first
    /// thing the player ever saw was HUD_02 mid-reveal.
    /// </para>
    /// <para>
    /// <b>This is the unskipped value, not a fixed one.</b> The gate is
    /// <c>StartPlayingState + NEXT_FRAME</c>, and
    /// <c>CPlayer::ReceiveButtonAction</c> lets
    /// <c>BUTTON_SKIP_PANNING</c> call <c>StartPlayingState</c> at any tick of
    /// the pan (<c>Player.cpp:311-315</c>). A player who skips at tick
    /// <c>T</c> therefore moves the whole opening message chain — and with it
    /// <c>player.Activate()</c>, which the script reaches when
    /// <c>TUTORIAL_TECHNICIAN_01</c> clears — to <c>T + 2</c>. That makes the
    /// released tutorial's message schedule a
    /// <b>player-controllable timing input</b>, not a fixed table.
    /// <see cref="Level100Mission"/> owns the live value; this constant is
    /// only the value it starts at, and is what the two measured no-input
    /// Steam runs saw.
    /// </para>
    /// </remarks>
    public const int MessageBoxAllowedTick =
        SimulationConstants.Level100OpeningPanTicks + ReleasedEventFrameTicks;

    /// <summary>
    /// The gap between one character message clearing and the next queued one
    /// becoming active, in Core ticks.
    /// </summary>
    /// <remarks>
    /// <para>
    /// 0.2 s at the released 0.05 s event clock, from
    /// <c>CMessageBox__TryAdvanceQueuedMessage</c> (<c>0x004b7b80</c>), which
    /// waits 0.2 s before starting the voice/reveal path of the message it
    /// dequeues.
    /// </para>
    /// <para>
    /// Independently measured: the eight retail opening boundaries in
    /// <c>rebuild/PROVENANCE.md</c> are 182..351, 357..567, 573..756,
    /// 762..926, 932..998, 1004..1220, 1226..1387, 1393..1530. Every single
    /// end-to-next-start gap is exactly six ticks, and every span equals this
    /// file's <see cref="MessagePlaybackTicks"/> entry to within the ±1 tick
    /// the 50 ms sampler can resolve.
    /// </para>
    /// <para>
    /// That measurement also settles what the 18-tick offset in
    /// <see cref="MessagePlaybackTicks"/> is <em>not</em>: it is not a
    /// post-roll to subtract for display. Retail activates the message before
    /// the voice starts and retains it through the completion hold, so the
    /// table value <b>is</b> the on-screen duration.
    /// </para>
    /// </remarks>
    public const int MessageAdvanceDelayTicks = SimulationConstants.TicksPerSecond / 5;

    internal static int MessagePlaybackTicks(int messageId) => messageId switch
    {
        292562 => 169,       // HUD_01
        293386 => 210,       // HUD_02
        294210 => 265,       // HUD_03
        295034 => 264,       // HUD_04
        295858 => 260,       // HUD_05
        296682 => 183,       // HUD_06
        297506 => 235,       // HUD_07
        -1575499396 => 163,  // TUTORIAL_MESSAGE_LOG
        -257967449 => 65,    // TUTORIAL_TECHNICIAN_01
        82987417 => 215,     // TUTORIAL_13_MOD
        4422830 => 160,      // TUTORIAL_01
        175347826 => 138,    // TUTORIAL_SCANNER
        4458134 => 180,      // TUTORIAL_02
        4493438 => 97,       // TUTORIAL_03
        1339691000 => 221,   // TUTORIAL_PULSE_CANNON
        669198996 => 112,    // TUTORIAL_OPEN_FIRE
        -1715818922 => 243,  // TUTORIAL_PULSE_CANNON_2
        -1616775312 => 239,  // TUTORIAL_VULCAN_CANNON
        -1860407443 => 121,  // TUTORIAL_OPEN_FIRE_2
        864965454 => 182,    // TUTORIAL_VULCAN_CANNON_2
        4564046 => 281,      // TUTORIAL_05
        22775962 => 190,     // TUTORIAL_ZOOM
        667656903 => 201,    // TUTORIAL_DODGE_MOD
        150647733 => 165,    // TUTORIAL_DODGE_2
        151778876 => 244,    // TUTORIAL_DODGE_3
        623538785 => 136,    // TUTORIAL_DODGE_BAD
        1326027769 => 129,   // TUTORIAL_DODGE_GOOD
        4528742 => 262,      // TUTORIAL_04
        165861931 => 228,    // TUTORIAL_LANDING
        4599350 => 226,      // TUTORIAL_06
        1062059777 => 130,   // TUTORIAL_THROTTLE_MOD
        4475837 => 133,      // TUTORIAL_12
        4705262 => 213,      // TUTORIAL_09
        4634654 => 168,      // TUTORIAL_07
        80260569 => 197,     // TUTORIAL_STRAFE
        4669958 => 227,      // TUTORIAL_08
        4440532 => 225,      // TUTORIAL_11
        162342028 => 168,    // TUTORIAL_ABORTED
        150940633 => 109,    // TUTORIAL_BROKE_1
        152071864 => 122,    // TUTORIAL_BROKE_2
        153203095 => 127,    // TUTORIAL_BROKE_3
        -1455850811 => 114,  // TUTORIAL_HELP_PLAYER
        4405227 => 199,      // TUTORIAL_10
        _ => throw new InvalidOperationException(
            $"Released Level 100 message id {messageId} has no evidenced wait duration."),
    };
}
