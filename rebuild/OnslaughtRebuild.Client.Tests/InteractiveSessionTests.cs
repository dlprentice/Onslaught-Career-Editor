// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Client.Tests;

public sealed class InteractiveSessionTests
{
    // The first tick a first run has player control. The released
    // LevelScript reaches player.Activate() when TUTORIAL_TECHNICIAN_01
    // clears, and the released message box holds the opening five messages
    // to Level100MissionTiming.MessageBoxAllowedTick + the advance gaps:
    // 121 +113 +4+140 +4+122 +4+109 +4+44 = 665. Two fresh app-owned Steam
    // runs measured the Battle Engine power flag at +0x580 changing 0 -> 1
    // at 30 Hz Core tick 1000 (rebuild/PROVENANCE.md), i.e. 33,333 ms; 665
    // 20 Hz ticks is 33,250 ms, an 83 ms residual against the 50 ms sampler.
    //
    // THIS IS THE ACCEPTANCE SIGNAL THE 20 Hz MIGRATION WAS FOR, and it moved
    // the right way. At 30 Hz the sum was 182 +169 +6+210 +6+183 +6+163 +6+65
    // = 996 against the measured 1000, i.e. 33,200 ms against 33,333 ms - a
    // 133 ms residual. Retail floors every scheduled delay onto a whole 20 Hz
    // boundary (references/Onslaught/eventmanager.cpp:210-212), which a 30 Hz
    // Core cannot land at all, so the residual SHOULD shrink; it did, from
    // 133 ms to 83 ms. See Level100MissionTests
    // .ReleasedMessageBox_ReproducesTheRetailOpeningDeliverySchedule for the
    // same signal asserted across all eight measured boundaries.
    //
    // The value before either of those was 790, which is the same sum with the
    // gate and the gaps both absent.
    private const int FirstRunControlTick = 665;
    private static Level100ActorDefinitionSet ActorDefinitions =>
        Level100TestActorDefinitions.Create();
    private const long OneCoreStepTicks = 500_000;
    private const uint Seed = 0x4F4E534Cu;

    [Fact]
    public void RationalAccumulator_DoesNotTruncateTheCoreStep()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        FrameAdvanceResult beforeBoundary = session.AdvanceFrameTicks(499_999);
        FrameAdvanceResult afterBoundary = session.AdvanceFrameTicks(1);

        Assert.Equal(0, beforeBoundary.StepsAdvanced);
        Assert.Equal(1, afterBoundary.StepsAdvanced);
        Assert.Equal(1, afterBoundary.CurrentSnapshot.Tick);
        Assert.Equal(0, afterBoundary.InterpolationPhase);
        Assert.Equal(InteractiveSession.PhaseUnitsPerStep, afterBoundary.InterpolationPhaseScale);
    }

    [Fact]
    public void FourQuarterSecondFrames_AdvanceExactlyOneSecondOfTicks()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        FrameAdvanceResult result = default;
        for (int frame = 0; frame < 4; frame++)
        {
            result = session.AdvanceFrame(TimeSpan.FromMilliseconds(250));
            Assert.False(result.FrameTimeCapped);
        }

        Assert.Equal(SimulationConstants.TicksPerSecond, result.CurrentSnapshot.Tick);
        Assert.Equal(SimulationConstants.TicksPerSecond, session.Metrics.TotalSteps);
        Assert.Equal(0, session.Metrics.DroppedElapsedTicks);
    }

    [Fact]
    public void LongFrame_IsCappedAndReportedWithoutSkippingSimulationTicks()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        FrameAdvanceResult result = session.AdvanceFrame(TimeSpan.FromSeconds(1));

        Assert.True(result.FrameTimeCapped);
        // MaximumFrameElapsedTicks is 0.25 s of WALL CLOCK, and stays 0.25 s
        // across the 20 Hz migration: it bounds how far behind real time one
        // frame may catch up, which is a property of the host, not of the
        // simulation rate. Five 20 Hz steps fit in it where seven 30 Hz steps
        // did.
        Assert.Equal(5, result.StepsAdvanced);
        Assert.Equal(5, result.CurrentSnapshot.Tick);
        Assert.Equal(1, session.Metrics.CappedFrameCount);
        Assert.Equal(TimeSpan.FromMilliseconds(750).Ticks, session.Metrics.DroppedElapsedTicks);
    }

    [Fact]
    public void HeldToggleLevel_IsConsumedOnOneTickOnly()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(0, 0, false, true, false));

        FrameAdvanceResult result = session.AdvanceFrame(TimeSpan.FromMilliseconds(100));
        session.ObserveInput(new InteractiveInput(0, 0, false, true, false));
        session.AdvanceFrame(TimeSpan.FromMilliseconds(100));

        Assert.Equal(VehicleMode.Walker, result.CurrentSnapshot.Mode);
        Assert.Equal(VehicleTransition.None, result.CurrentSnapshot.Transition);
        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);

        for (int frame = 0; frame < 4; frame++)
        {
            session.AdvanceFrame(TimeSpan.FromMilliseconds(100));
        }

        Assert.Equal(VehicleMode.Walker, session.CurrentSnapshot.Mode);
        Assert.Equal(VehicleTransition.None, session.CurrentSnapshot.Transition);
        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
    }

    [Fact]
    public void PressAndReleaseBetweenTicks_LeavesOneLatchedEdge()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(0, 0, false, true, false));
        session.ObserveInput(InteractiveInput.Idle);

        FrameAdvanceResult result = session.AdvanceFrameTicks(500_000);

        Assert.Equal(VehicleMode.Walker, result.CurrentSnapshot.Mode);
        Assert.Equal(VehicleTransition.None, result.CurrentSnapshot.Transition);
        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
    }

    [Fact]
    public void DuplicateEventAndLevelEdge_AreCoalescedBeforeTheTick()
    {
        InteractiveSession session = CreatePlayingSession();
        session.QueueToggleMode();
        session.ObserveInput(new InteractiveInput(0, 0, false, true, false));

        session.AdvanceFrame(TimeSpan.FromMilliseconds(100));

        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
    }

    [Fact]
    public void ZoomWheelEdge_ReachesCoreOnceAndContinuesTheRetailEase()
    {
        InteractiveSession session = CreatePlayingSession();

        session.QueueZoomIn();
        Assert.True(session.HasHeldOrPendingInput);
        FrameAdvanceResult first = session.AdvanceFrameTicks(OneCoreStepTicks);

        Assert.Equal(900, first.CurrentSnapshot.ZoomPermille);
        Assert.Equal(
            SimulationConstants.ZoomInPermille,
            first.CurrentSnapshot.DesiredZoomPermille);
        Assert.False(session.HasHeldOrPendingInput);

        FrameAdvanceResult second = session.AdvanceFrameTicks(OneCoreStepTicks);
        Assert.Equal(800, second.CurrentSnapshot.ZoomPermille);
        Assert.Equal(
            SimulationConstants.ZoomInPermille,
            second.CurrentSnapshot.DesiredZoomPermille);
    }

    [Fact]
    public void GunAction_FiresOnceOnReleaseAndDoesNotRepeatWhileHeld()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(0, 0, true, false, false));

        session.AdvanceFrame(TimeSpan.FromMilliseconds(200));
        session.ObserveInput(new InteractiveInput(0, 0, true, false, false));
        session.AdvanceFrameTicks(500_000);

        Assert.Equal(0, session.Metrics.FirePulseEdgesConsumed);
        Assert.Equal(5, session.Metrics.FireHeldTicksSampled);

        // Godot can observe the same physical release twice: once from its
        // key-up event and once from the next sampled level. The bool latch
        // must coalesce those sources into one retail release action.
        session.QueueFirePulse();
        session.ObserveInput(InteractiveInput.Idle);
        session.AdvanceFrameTicks(500_000);
        Assert.Equal(1, session.Metrics.FirePulseEdgesConsumed);
        session.AdvanceFrameTicks(500_000);

        Assert.Equal(1, session.Metrics.FirePulseEdgesConsumed);

        // A complete repress/release between fixed steps still contributes one
        // edge, matching CPCController's old/current button truth table.
        session.ObserveInput(new InteractiveInput(0, 0, true, false, false));
        session.ObserveInput(InteractiveInput.Idle);
        session.AdvanceFrameTicks(500_000);

        Assert.Equal(2, session.Metrics.FirePulseEdgesConsumed);
    }

    [Fact]
    public void FlightDisabledSession_ConsumesTheTransformEdgeIntoCanonicalRejection()
    {
        InteractiveSession session = CreatePlayingSession();
        session.QueueToggleMode();

        FrameAdvanceResult result = session.AdvanceFrame(
            TimeSpan.FromMilliseconds(200));

        Assert.Equal(VehicleTransition.None, result.CurrentSnapshot.Transition);
        Assert.Empty(result.CurrentSnapshot.AquilaFlightEventLog);
        AquilaFlightEvent rejected = Assert.Single(result.AquilaFlightEvents);
        Assert.Equal(AquilaFlightEvents.TransformRejected, rejected.Kind);
        Assert.True(rejected.Tick < result.CurrentSnapshot.Tick);
        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
    }

    [Fact]
    public void LandingJetsHeld_AreLevelSampledIntoCore()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(
            0,
            0,
            false,
            false,
            false,
            LandingJetsHeld: true));

        FrameAdvanceResult result = session.AdvanceFrameTicks(500_000);

        Assert.True(result.CurrentSnapshot.LandingJetsActive);
    }

    [Fact]
    public void ShortFirePulse_SurvivesUntilOneTickConsumesIt()
    {
        InteractiveSession session = CreatePlayingSession();

        session.QueueFirePulse();
        session.AdvanceFrameTicks(100_000);
        FrameAdvanceResult firingTick = session.AdvanceFrameTicks(233_334);
        FrameAdvanceResult followingTick = session.AdvanceFrameTicks(500_000);

        Assert.Empty(firingTick.CurrentSnapshot.Projectiles);
        Assert.Empty(followingTick.CurrentSnapshot.Projectiles);
        Assert.Equal(1, session.Metrics.FirePulseEdgesConsumed);
        Assert.Equal(0, session.Metrics.FireHeldTicksSampled);
    }

    [Fact]
    public void ShortMovementPulse_StartsAccelerationAndThenCoasts()
    {
        InteractiveSession session = CreatePlayingSession();

        session.QueueMovementPulse(0, 1);
        FrameAdvanceResult movementTick = session.AdvanceFrameTicks(500_000);
        FrameAdvanceResult idleTick = session.AdvanceFrameTicks(500_000);

        // MOVED by the 20 Hz migration. The walker's first accelerating tick
        // is WalkerAccelerationPerTick along the facing, and that constant is
        // 70 where it was 33: a per-tick increment into a store damped by
        // mWalkFriction, so it converts by (1-0.7)/(1-0.7884) * 1.5 = 2.126,
        // not by the velocity rule. |(-34, 61)| is 70; |(-16, 29)| was 33.
        // The walker's SPEED is unchanged - both rates cap at
        // mMaxWalkVelocity 0.15 = 3,000 mm/s.
        Assert.Equal(
            new SimVector2(-34, 61),
            movementTick.CurrentSnapshot.PlayerPosition);
        Assert.Equal(
            new SimVector2(-57, 103),
            idleTick.CurrentSnapshot.PlayerPosition);
        Assert.Equal(1, session.Metrics.MovementPulseEdgesConsumed);
    }

    [Fact]
    public void PulseAndHeldState_AreCoalescedIntoOneSimulationInput()
    {
        InteractiveSession session = CreatePlayingSession();
        session.QueueMovementPulse(0, 1);
        session.QueueFirePulse();
        session.ObserveInput(new InteractiveInput(0, 1, true, false, false));

        FrameAdvanceResult result = session.AdvanceFrameTicks(500_000);

        // MOVED by the 20 Hz migration. The walker's first accelerating tick
        // is WalkerAccelerationPerTick along the facing, and that constant is
        // 70 where it was 33: a per-tick increment into a store damped by
        // mWalkFriction, so it converts by (1-0.7)/(1-0.7884) * 1.5 = 2.126,
        // not by the velocity rule. |(-34, 61)| is 70; |(-16, 29)| was 33.
        // The walker's SPEED is unchanged - both rates cap at
        // mMaxWalkVelocity 0.15 = 3,000 mm/s.
        Assert.Equal(new SimVector2(-34, 61), result.CurrentSnapshot.PlayerPosition);
        Assert.Empty(result.CurrentSnapshot.Projectiles);
        Assert.Equal(1, session.Metrics.MovementPulseEdgesConsumed);
        Assert.Equal(1, session.Metrics.FirePulseEdgesConsumed);
        Assert.Equal(1, session.Metrics.FireHeldTicksSampled);
    }

    [Fact]
    public void ResetDominatesItsTick_AndRestartsTheOpeningInputGate()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(0, 0, true, false, true));

        FrameAdvanceResult resetTick = session.AdvanceFrameTicks(500_000);
        FrameAdvanceResult followingTick = session.AdvanceFrameTicks(500_000);

        Assert.Empty(resetTick.CurrentSnapshot.Projectiles);
        Assert.Empty(followingTick.CurrentSnapshot.Projectiles);
        Assert.False(followingTick.CurrentSnapshot.Level100PlayerControlEnabled);
        Assert.Equal(
            SimulationConstants.Level100OpeningPanTicks - 1,
            followingTick.CurrentSnapshot.Level100OpeningTicksRemaining);
        Assert.Equal(1, session.Metrics.ResetEdgesConsumed);
        Assert.Equal(1, session.Metrics.ResetGeneration);
        Assert.Equal(2, session.Metrics.FireHeldTicksSampled);
    }

    [Fact]
    public void SameIntegerFrameAndInputSequence_ProducesSameStateAndMetrics()
    {
        InteractiveSession first = RunInteractiveSequence();
        InteractiveSession second = RunInteractiveSequence();

        Assert.Equal(StateHasher.ComputeHex(first.CurrentSnapshot), StateHasher.ComputeHex(second.CurrentSnapshot));
        Assert.Equal(first.Metrics, second.Metrics);
        Assert.Equal(first.InterpolationPhase, second.InterpolationPhase);
    }

    [Fact]
    public void FramePartitioning_DoesNotChangeStateForTheSameHeldInput()
    {
        InteractiveSession coarse = CreatePlayingSession();
        InteractiveSession fine = CreatePlayingSession();
        var input = new InteractiveInput(1, 1, true, false, false);
        coarse.ObserveInput(input);
        fine.ObserveInput(input);

        for (int frame = 0; frame < 10; frame++)
        {
            coarse.AdvanceFrame(TimeSpan.FromMilliseconds(100));
        }

        for (int frame = 0; frame < 40; frame++)
        {
            fine.AdvanceFrame(TimeSpan.FromMilliseconds(25));
        }

        Assert.Equal(
            FirstRunControlTick + SimulationConstants.TicksPerSecond,
            coarse.CurrentSnapshot.Tick);
        Assert.Equal(
            FirstRunControlTick + SimulationConstants.TicksPerSecond,
            fine.CurrentSnapshot.Tick);
        Assert.Equal(StateHasher.ComputeHex(coarse.CurrentSnapshot), StateHasher.ComputeHex(fine.CurrentSnapshot));
    }

    [Fact]
    public void LookX_HeldRotatesFacingUsingWalkerYawInertia()
    {
        InteractiveSession session = CreatePlayingSession(1);
        // One Core step needs elapsedTicks such that elapsed * TPS >= PhaseUnitsPerStep.
        const long oneCoreStepTicks =
            (TimeSpan.TicksPerSecond / SimulationConstants.TicksPerSecond) + 1;
        session.ObserveInput(new InteractiveInput(0, 0, false, false, false, LookX: 1));
        Assert.True(session.HasHeldOrPendingInput);
        for (int i = 0; i < 20; i++)
        {
            session.AdvanceFrameTicks(oneCoreStepTicks);
        }

        Assert.Equal(1, session.CurrentSnapshot.FacingX);
        Assert.Equal(0, session.CurrentSnapshot.FacingZ);
    }

    [Fact]
    public void LookY_HeldPitchesTheBattleEngineThroughTheClientAdapter()
    {
        InteractiveSession session = CreatePlayingSession(1);
        const long oneCoreStepTicks =
            (TimeSpan.TicksPerSecond / SimulationConstants.TicksPerSecond) + 1;
        session.ObserveInput(new InteractiveInput(0, 0, false, false, false, LookY: -1));

        session.AdvanceFrameTicks(oneCoreStepTicks);

        // Retail's own 1/117 rad per update (BattleEngineWalkerPart.cpp:355),
        // verbatim since the 20 Hz migration. This read -3,938 at 30 Hz, the
        // time-equivalent of the same shipped divisor.
        Assert.Equal(-8_547, session.CurrentSnapshot.FacingPitchMicroRad);
        Assert.Equal(
            -8_547,
            session.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);
    }

    [Fact]
    public void ShortLookPulse_SurvivesUntilOneTickConsumesIt()
    {
        InteractiveSession session = CreatePlayingSession(1);
        int startingYaw = session.CurrentSnapshot.FacingYawMicroRad;

        session.QueueLookPulse(1, -1);
        FrameAdvanceResult beforeTick = session.AdvanceFrameTicks(100_000);

        Assert.Equal(0, beforeTick.StepsAdvanced);
        Assert.True(session.HasHeldOrPendingInput);

        FrameAdvanceResult lookTick = session.AdvanceFrameTicks(400_001);

        Assert.Equal(1, lookTick.StepsAdvanced);
        Assert.False(session.HasHeldOrPendingInput);
        Assert.Equal(startingYaw + 22_667, lookTick.CurrentSnapshot.FacingYawMicroRad);
        Assert.Equal(22_667, lookTick.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(-8_547, lookTick.CurrentSnapshot.FacingPitchMicroRad);
        Assert.Equal(
            -8_547,
            lookTick.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);
    }

    /// <summary>
    /// The mouse-sensitivity slider's consumer.
    ///
    /// Steam <c>CController::DoMappings</c> scales a centred displacement by
    /// <c>g_MouseSensitivity * 0.004333333</c> (= 13/3000), and the slider's
    /// reachable values are <c>(index + 1) * 3</c>. Two things must hold together
    /// and neither is safe alone: passing the image default 7.0 must leave the
    /// axis EXACTLY where it was before the slider existed (91/3000), and a
    /// different sensitivity must actually move it. Asserting only the first
    /// would pass on a setter that does nothing.
    /// </summary>
    [Fact]
    public void PointerMotion_SensitivitySliderScalesTheAxisAndSevenIsTheDefault()
    {
        const long oneCoreStepTicks =
            (TimeSpan.TicksPerSecond / SimulationConstants.TicksPerSecond) + 1;

        InteractiveSession explicitDefault = CreatePlayingSession(1);
        explicitDefault.SetMouseSensitivity(7f);
        explicitDefault.QueuePointerMotionMilliPixels(15_000, -7_500);
        FrameAdvanceResult atSeven = explicitDefault.AdvanceFrameTicks(oneCoreStepTicks);

        // The goldens PointerMotion_PreservesMagnitudeAndRetailRecenteringCoast
        // pins for the untouched session, reproduced through the slider at 7.0.
        // MOVED 2026-07-30, from 1,640 and -299. See the accounting on that
        // test; both pins record the same 15 px / -7.5 px motion.
        Assert.Equal(5_349, atSeven.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(
            -863,
            atSeven.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);

        // The lowest reachable stop is 3.0, well under the shipped 7.0, so the
        // same hand motion must turn the walker measurably less far.
        InteractiveSession slowest = CreatePlayingSession(1);
        slowest.SetMouseSensitivity(3f);
        slowest.QueuePointerMotionMilliPixels(15_000, -7_500);
        FrameAdvanceResult atThree = slowest.AdvanceFrameTicks(oneCoreStepTicks);

        Assert.True(
            atThree.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick <
                atSeven.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick,
            "the sensitivity slider did not reach the pointer axis");
        Assert.True(atThree.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick > 0);
    }

    /// <summary>
    /// One whole mouse pixel is worth exactly the stick position the released
    /// build gives it - the countable half of task #141.
    ///
    /// <para>Retail's look axis is
    /// <c>g_MouseSensitivity * (cursor - centre) * 13/3000</c>
    /// (<c>CController::DoMappings</c> 0x0042DB40, scalar at pristine
    /// VA 0x005D97C8), read out of an INTEGER cursor position. So one pixel is
    /// 91/3000 = <b>30 permille</b> at the image's untouched 7.0, and 39/3000 =
    /// <b>13 permille</b> at the slider's lowest reachable stop of 3.0.</para>
    ///
    /// <para><b>Neither number was reachable before 2026-07-30.</b> This client
    /// eased the offset BEFORE reading it, so one pixel was read as
    /// round(1 px × 0.702049) and arrived as 21 permille at 7.0 and 9 at 3.0 -
    /// 30 % short, and values the released build cannot produce at all. Retail
    /// sets its recentre flag on the way OUT of the read
    /// (<c>DAT_0066E94D = 1</c>) and eases afterwards in
    /// <c>Input__UpdateCursorCenterWithWindowScale</c> 0x0042DA00.</para>
    ///
    /// <para>The 13 is the interesting one: it is below the 15-permille floor
    /// the old half-pixel dead zone imposed, so it is a stop that was
    /// unreachable at ANY sensitivity and is now delivered exactly.</para>
    /// </summary>
    [Fact]
    public void PointerMotion_OneWholePixelIsWorthRetailsOwnStop()
    {
        foreach ((float sensitivity, short permille) in
            new (float, short)[] { (7f, 30), (3f, 13) })
        {
            InteractiveSession session = CreatePlayingSession(1);
            session.SetMouseSensitivity(sensitivity);
            session.QueuePointerMotionMilliPixels(1_000, 0);
            FrameAdvanceResult moved = session.AdvanceFrameTicks(OneCoreStepTicks);

            // Stated as an EQUIVALENCE rather than a golden: one pixel of mouse
            // has to be the same thing to Core as commanding that stick
            // position outright. A golden here would survive the axis moving.
            var direct = new Simulation(1, ActorDefinitions);
            for (int tick = 0; tick < FirstRunControlTick; tick++)
            {
                direct.Step(SimInput.Idle);
            }

            WorldSnapshot commanded = direct.Step(
                new SimInput(0, 0, SimActions.None, 0, 0, permille, 0));

            Assert.Equal(
                commanded.WalkerYawVelocityMicroRadPerTick,
                moved.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick);

            // The guard that stops the equivalence being trivially true if both
            // sides collapse to a motionless walker.
            Assert.True(
                moved.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick > 0,
                $"one pixel at sensitivity {sensitivity} moved nothing");
        }
    }

    /// <summary>
    /// The offset returns to rest, and it does so because of 0x0042DA00's
    /// one-pixel anti-stall rather than because a floor snapped it away.
    ///
    /// <para>Retail's ease is integer, so it stalls: round(1 px × 0.702049) is
    /// 1 px again. 0x0042DA00 carries
    /// <c>if ((centre != cursor) &amp;&amp; (step == 0)) step = ±1</c> for
    /// exactly that case. Without the rule a one-pixel offset would coast
    /// forever; with it, one pixel is spent in a single step.</para>
    /// </summary>
    [Fact]
    public void PointerMotion_OffsetWalksBackToRestOnePixelAtATime()
    {
        InteractiveSession session = CreatePlayingSession(1);
        int startingYaw = session.CurrentSnapshot.FacingYawMicroRad;
        session.QueuePointerMotionMilliPixels(1_000, 0);

        FrameAdvanceResult spent = session.AdvanceFrameTicks(OneCoreStepTicks);

        // It was READ before it was eased - the pixel reached the simulation.
        Assert.NotEqual(startingYaw, spent.CurrentSnapshot.FacingYawMicroRad);

        // And then it was gone, in one step, with no floor to snap it away.
        Assert.False(
            session.HasHeldOrPendingInput,
            "a one-pixel offset outlived its step - the anti-stall is missing");

        // Three pixels take exactly three steps: 3 -> 2 -> 1 -> 0. The last of
        // those only happens because of the ±1 forcing; round(1 × 0.702049) is
        // 1, so without it the offset coasts at one pixel for ever.
        InteractiveSession longer = CreatePlayingSession(1);
        longer.QueuePointerMotionMilliPixels(3_000, 0);
        for (int step = 1; step <= 2; step++)
        {
            longer.AdvanceFrameTicks(OneCoreStepTicks);
            Assert.True(
                longer.HasHeldOrPendingInput,
                $"a three-pixel offset was already at rest after {step} step(s)");
        }

        longer.AdvanceFrameTicks(OneCoreStepTicks);
        Assert.False(
            longer.HasHeldOrPendingInput,
            "a three-pixel offset never returned to rest");
    }

    [Fact]
    public void PointerMotion_PreservesMagnitudeAndRetailRecenteringCoast()
    {
        InteractiveSession session = CreatePlayingSession(1);
        int startingYaw = session.CurrentSnapshot.FacingYawMicroRad;
        const long oneCoreStepTicks =
            (TimeSpan.TicksPerSecond / SimulationConstants.TicksPerSecond) + 1;

        // 15 px, not the 80 px this test used before 2026-07-27. At retail's
        // sensitivity an 80 px flick SATURATES the axis, and both samples came
        // back at the full 10,444 - which would have made this test pass for
        // almost any sensitivity at all, blind to the constants it exists to
        // protect. 15 px lands mid-range, where the sensitivity scalar and the
        // Player.cpp:334-355 response curve both actually show up.
        session.QueuePointerMotionMilliPixels(15_000, -7_500);
        FrameAdvanceResult first = session.AdvanceFrameTicks(oneCoreStepTicks);

        // THESE FOUR GOLDENS MOVED ON 2026-07-30, and the old values are kept
        // here rather than replaced because the move is the whole point of the
        // change that caused it. The pins were:
        //
        //     step 1 yaw   1,640 -> 2,465        step 1 pitch  -299 -> -398
        //     step 2 yaw   2,531 -> 3,847        step 2 pitch  -466 -> -626
        //
        // THE ACCOUNTING. The motion is unchanged: 15 px right, 7.5 px up.
        //   WAS: the offset was eased BEFORE it was read, so 15,000 milli-px
        //        became round(15,000 x 0.702049) = 10,531 and the axis saw
        //        319 permille; -7,500 became -5,265 and the axis saw -160.
        //   NOW: retail's order - CController::DoMappings reads the cursor and
        //        only then raises the recentre flag - so the axis sees the
        //        whole-pixel cursor itself: 15 px = 455 permille and -7 px =
        //        -212. 455/319 is 1.426, which is 1/0.702049: exactly the ease
        //        that is no longer taken before the read.
        //   The Y axis moves by slightly more than that ratio because 7.5 px is
        //   not a whole cursor position. It reads as 7 px and the half pixel is
        //   CARRIED, which is what Windows does with sub-pixel mouse counts;
        //   retail's cursor globals (DAT_0089BDA8/DAT_0089BDA4) are ints and
        //   never hold a fraction.
        //
        // Neither the sensitivity scalar (13/3000), the Player.cpp:334-355
        // response curve, nor any Core constant moved: the whole change is
        // confined to InteractiveSession's pointer path. The cold-career
        // acceptance run is BIT-IDENTICAL across it - same Won, same terminal
        // tick 12463, same hull 12100, same state hash ffe391e7... - because
        // that run only ever asks for stick positions a whole pixel can produce,
        // and those are delivered the same either way. These four goldens moved
        // precisely because they are the one place that exercises a motion that
        // is NOT already on retail's lattice.
        // MOVED AGAIN 2026-07-31 BY THE 20 Hz MIGRATION, and this is a pure
        // R3 unit change with no behaviour in it. The pointer path, the
        // sensitivity scalar and the response curve are all untouched; what
        // moved is WalkerYawInputMicroRadPerTick 10,444 -> 22,667 and
        // WalkerPitchInputMicroRadPerTick 3,938 -> 8,547, because a per-tick
        // impulse into a store retained at retail's exact 0.8 converts by
        // (1-0.8)/(1-0.861774) * 1.5 = 2.170337. Every pin below scales by
        // that factor to within one micro-radian of integer rounding on the
        // FIRST step. The second step also carries the pointer recentring ease,
        // which is retail's own 10/17 per 20 Hz update and was itself running
        // as (10/17)^(2/3) = 702049/1000000 at 30 Hz - so the two-step pins
        // move by more than 2.170337. That ease is a THIRD verbatim retail
        // value the migration recovers, and it lives in InteractiveSession
        // rather than Core:
        //     step 1 yaw   2,465 -> 5,349        step 1 pitch  -398 -> -863
        //     step 2 yaw   3,847 -> 7,294        step 2 pitch  -626 -> -1,177
        // The walker's turn is the same angular rate per SECOND at either
        // Core rate; only the per-tick quantum changed.
        Assert.Equal(5_349, first.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(-863, first.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);
        Assert.Equal(startingYaw + 5_349, first.CurrentSnapshot.FacingYawMicroRad);
        Assert.True(session.HasHeldOrPendingInput);

        // The guard that makes the numbers above mean something. If a future
        // sensitivity change pushes this input to the clamp, these fail loudly
        // instead of the goldens quietly becoming a constant.
        Assert.True(
            first.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick < FullDeflectionYawPerTick,
            "pointer input saturated the yaw axis - pick a smaller motion");
        Assert.True(
            Math.Abs(first.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick) <
                FullDeflectionYawPerTick,
            "pointer input saturated the pitch axis - pick a smaller motion");

        FrameAdvanceResult second = session.AdvanceFrameTicks(oneCoreStepTicks);

        // STEP 2's YAW MOVED 7,294 -> 7,271 ON 2026-08-01, by the look-response
        // table going to one entry per representable input (task #161). The
        // move is EXACTLY ONE PERMILLE OF THE YAW SCALE and that is the whole
        // of it: WalkerYawInputMicroRadPerTick is 22,667, the difference is 23,
        // and 22,667 / 1,000 = 22.667. So a single table entry changed by one
        // permille at the magnitude the recentring ease leaves on the axis at
        // this step, and nothing else did - which is why STEP 1 above did not
        // move at all, its magnitude landing on an entry the new table agrees
        // with the old one about.
        //
        // The new value is the more faithful one. Retail computes
        // tan(1.2v)/tan(1.2) live per sample (Player.cpp:346,350) with no table
        // at all; ours exists only because .NET does not guarantee bit-identical
        // transcendentals. Every one of the 187 entries that moved is strictly
        // closer to that law - worst case 0.4997 permille against the old
        // table's 0.9436 - so this pin is nearer retail than the one it
        // replaces, not merely different.
        Assert.Equal(7_271, second.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(
            -1_177,
            second.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);
        Assert.Equal(
            first.CurrentSnapshot.FacingYawMicroRad + 7_271,
            second.CurrentSnapshot.FacingYawMicroRad);
    }

    // Yaw rate at full look deflection, from
    // WalkerAnalogLook_FollowsTheReleasedCurveAndUsesTheSameRetailCoast.
    private const int FullDeflectionYawPerTick = 22_667;

    [Fact]
    public void InteractiveInputSequence_MatchesDirectCoreTicks()
    {
        InteractiveSession session = CreatePlayingSession();
        var direct = new Simulation(Seed, ActorDefinitions);
        for (int tick = 0; tick < FirstRunControlTick; tick++)
        {
            direct.Step(SimInput.Idle);
        }
        var held = new InteractiveInput(0, 1, true, false, false);
        session.ObserveInput(held);
        session.AdvanceFrameTicks(1_500_000);
        for (int tick = 0; tick < 3; tick++)
        {
            direct.Step(new SimInput(0, 1, SimActions.Fire));
        }

        session.ObserveInput(new InteractiveInput(0, 1, false, true, false));
        session.AdvanceFrameTicks(500_000);
        direct.Step(new SimInput(0, 1, SimActions.ToggleMode));

        session.ObserveInput(new InteractiveInput(0, 0, true, false, true));
        session.AdvanceFrameTicks(500_000);
        direct.Step(new SimInput(0, 0, SimActions.Fire | SimActions.Reset));

        Assert.Equal(StateHasher.ComputeHex(direct.Snapshot), StateHasher.ComputeHex(session.CurrentSnapshot));
    }

    [Fact]
    public void FocusLoss_ReleasesHeldInputAndDiscardsUnconsumedEdges()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(1, 1, true, true, true));
        session.QueueMovementPulse(-1, -1);
        session.QueueLookPulse(-1, -1);
        session.QueuePointerMotionMilliPixels(-10_000, 10_000);
        session.QueueFirePulse();

        session.ReleaseAllInput();
        session.AdvanceFrameTicks(500_000);

        Assert.Equal(SimVector2.Zero, session.CurrentSnapshot.PlayerPosition);
        Assert.Empty(session.CurrentSnapshot.Projectiles);
        Assert.Equal(VehicleMode.Walker, session.CurrentSnapshot.Mode);
        Assert.Equal(0, session.Metrics.ToggleEdgesConsumed);
        Assert.Equal(0, session.Metrics.ResetEdgesConsumed);
        Assert.Equal(0, session.Metrics.FireHeldTicksSampled);
    }

    [Fact]
    public void FocusLoss_SuppressesHeldAndPulseInputUntilANeutralSample()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(1, 1, true, true, true));
        session.QueueMovementPulse(-1, -1);
        session.QueueLookPulse(-1, -1);
        session.QueuePointerMotionMilliPixels(-10_000, 10_000);
        session.QueueFirePulse();

        session.SuspendInputUntilReleased();
        session.ObserveInput(new InteractiveInput(0, 1, true, false, false));
        session.QueueMovementPulse(1, 0);
        session.QueueLookPulse(1, 0);
        session.QueuePointerMotionMilliPixels(10_000, -10_000);
        session.QueueFirePulse();
        session.QueueToggleMode();
        session.QueueReset();
        session.AdvanceFrameTicks(500_000);

        Assert.True(session.InputSuspendedUntilReleased);
        Assert.False(session.HasHeldOrPendingInput);
        Assert.Equal(SimVector2.Zero, session.CurrentSnapshot.PlayerPosition);
        Assert.Empty(session.CurrentSnapshot.Projectiles);
        Assert.Equal(VehicleMode.Walker, session.CurrentSnapshot.Mode);
        Assert.Equal(0, session.Metrics.ToggleEdgesConsumed);
        Assert.Equal(0, session.Metrics.ResetEdgesConsumed);

        session.ObserveInput(InteractiveInput.Idle);
        Assert.False(session.InputSuspendedUntilReleased);
        session.AdvanceFrameTicks(500_000);
        Assert.Equal(0, session.Metrics.FirePulseEdgesConsumed);

        session.QueueMovementPulse(0, 1);
        session.QueueFirePulse();
        session.AdvanceFrameTicks(500_000);

        Assert.Equal(new SimVector2(-34, 61), session.CurrentSnapshot.PlayerPosition);
        Assert.Empty(session.CurrentSnapshot.Projectiles);
    }

    [Fact]
    public void AuthenticPauseFreezesOneSessionAndRequiresNeutralInputAfterResume()
    {
        InteractiveSession session = CreatePlayingSession();
        int startingTick = session.CurrentSnapshot.Tick;
        string startingHash = StateHasher.ComputeHex(session.CurrentSnapshot);
        InteractiveSessionMetrics startingMetrics = session.Metrics;
        long startingPhase = session.InterpolationPhase;
        session.ObserveInput(new InteractiveInput(1, 1, true, true, true));
        session.QueueMovementPulse(-1, -1);
        session.QueueLookPulse(1, -1);
        session.QueuePointerMotionMilliPixels(10_000, -10_000);
        session.QueueFirePulse();

        session.SetAuthenticMenuPaused(true);

        Assert.Equal(InteractivePauseReason.AuthenticMenu, session.PauseReasons);
        Assert.True(session.IsPaused);
        Assert.True(session.IsAuthenticMenuPaused);
        Assert.True(session.InputSuspendedUntilReleased);
        Assert.False(session.HasHeldOrPendingInput);

        session.ObserveInput(InteractiveInput.Idle);
        session.QueueMovementPulse(0, 1);
        FrameAdvanceResult pausedFrame = session.AdvanceFrame(TimeSpan.FromSeconds(1));

        Assert.Equal(0, pausedFrame.StepsAdvanced);
        Assert.False(pausedFrame.FrameTimeCapped);
        Assert.Empty(pausedFrame.Level100MissionEvents);
        Assert.Equal(startingTick, session.CurrentSnapshot.Tick);
        Assert.Equal(startingPhase, session.InterpolationPhase);
        Assert.Equal(startingHash, StateHasher.ComputeHex(session.CurrentSnapshot));
        Assert.Equal(startingMetrics, session.Metrics);

        session.SetAuthenticMenuPaused(false);

        Assert.False(session.IsPaused);
        Assert.True(session.InputSuspendedUntilReleased);
        session.ObserveInput(new InteractiveInput(0, 1, true, false, false));
        Assert.True(session.InputSuspendedUntilReleased);
        Assert.False(session.HasHeldOrPendingInput);
        session.ObserveInput(InteractiveInput.Idle);
        Assert.False(session.InputSuspendedUntilReleased);
        session.AdvanceFrameTicks(500_000);
        Assert.Equal(
            startingMetrics.FirePulseEdgesConsumed,
            session.Metrics.FirePulseEdgesConsumed);
    }

    [Fact]
    public void PauseResumePreservesTheSameCoreInputTapeTraceAndFinalHash()
    {
        InteractiveSession uninterrupted = CreatePlayingSession();
        InteractiveSession paused = CreatePlayingSession();
        InteractiveInput[] tape =
        [
            new InteractiveInput(0, 1, false, false, false),
            InteractiveInput.Idle,
            new InteractiveInput(0, 0, true, false, false),
            InteractiveInput.Idle,
            new InteractiveInput(0, 0, false, true, false),
            InteractiveInput.Idle,
            new InteractiveInput(1, 0, false, false, false),
        ];
        var uninterruptedTrace = new List<string>();
        var pausedTrace = new List<string>();

        for (int index = 0; index < tape.Length; index++)
        {
            if (index == 2)
            {
                paused.SetAuthenticMenuPaused(true);
                Assert.Equal(0, paused.AdvanceFrame(TimeSpan.FromSeconds(1)).StepsAdvanced);
                paused.ObserveInput(new InteractiveInput(1, 1, true, true, true));
                paused.QueuePointerMotionMilliPixels(100_000, -100_000);
                paused.SetAuthenticMenuPaused(false);
                paused.ObserveInput(InteractiveInput.Idle);
            }

            uninterrupted.ObserveInput(tape[index]);
            paused.ObserveInput(tape[index]);
            FrameAdvanceResult directFrame = uninterrupted.AdvanceFrameTicks(OneCoreStepTicks);
            FrameAdvanceResult resumedFrame = paused.AdvanceFrameTicks(OneCoreStepTicks);
            Assert.Equal(1, directFrame.StepsAdvanced);
            Assert.Equal(1, resumedFrame.StepsAdvanced);
            uninterruptedTrace.Add(StateHasher.ComputeHex(directFrame.CurrentSnapshot));
            pausedTrace.Add(StateHasher.ComputeHex(resumedFrame.CurrentSnapshot));
        }

        Assert.Equal(uninterruptedTrace, pausedTrace);
        Assert.Equal(
            StateHasher.ComputeHex(uninterrupted.CurrentSnapshot),
            StateHasher.ComputeHex(paused.CurrentSnapshot));
        Assert.Equal(uninterrupted.Metrics, paused.Metrics);
    }

    [Fact]
    public void SnapshotsExposePreviousAndCurrentSimulationStates()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(1, 0, false, false, false));

        int startingTick = session.CurrentSnapshot.Tick;

        FrameAdvanceResult result = session.AdvanceFrameTicks(500_000);

        Assert.Equal(startingTick, result.PreviousSnapshot.Tick);
        Assert.Equal(startingTick + 1, result.CurrentSnapshot.Tick);
        Assert.Equal(0, result.PreviousSnapshot.PlayerPosition.X);
        Assert.True(result.CurrentSnapshot.PlayerPosition.X > 0);
    }

    [Fact]
    public void InvalidInputAndElapsedTime_AreRejected()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        Assert.Throws<ArgumentOutOfRangeException>(() =>
            session.ObserveInput(new InteractiveInput(2, 0, false, false, false)));
        Assert.Throws<ArgumentOutOfRangeException>(() => session.AdvanceFrameTicks(-1));
        WorldSnapshot before = session.CurrentSnapshot;
        Assert.Throws<ArgumentException>(() => session.AdvanceFrameTicks(
            1,
            [new Level100PlayerDeathFact()]));
        Assert.Same(before, session.CurrentSnapshot);
    }

    [Fact]
    public void InitialMissionEvents_AreDeliveredOnceByFrameEnvelope()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        FrameAdvanceResult initial = session.AdvanceFrameTicks(0);
        FrameAdvanceResult next = session.AdvanceFrameTicks(0);

        Assert.Equal(0, initial.StepsAdvanced);
        // No character message is delivered on tick 0. The released message box
        // is not allowed to play anything until the opening pan is over
        // (Level100MissionTiming.MessageBoxAllowedTick, from
        // CGame::StartPlayingState in references/Onslaught/game.cpp:3026-3031),
        // and the HUD is not even drawn before then.
        Assert.Empty(initial.Level100MissionEvents.OfType<Level100MessageRequested>());
        Assert.Empty(next.Level100MissionEvents);

        var session2 = new InteractiveSession(Seed, ActorDefinitions);
        session2.AdvanceFrameTicks(0);
        Level100MessageRequested? greeting = null;
        for (int tick = 0;
             tick < Level100MissionTiming.MessageBoxAllowedTick && greeting is null;
             tick++)
        {
            greeting = session2.AdvanceFrameTicks(OneCoreStepTicks)
                .Level100MissionEvents
                .OfType<Level100MessageRequested>()
                .FirstOrDefault();
        }

        Assert.NotNull(greeting);
        Assert.Equal(292562, greeting!.MessageId);
        Assert.Equal(Level100MissionTiming.MessageBoxAllowedTick, greeting.Tick);
    }

    [Fact]
    public void FrameMissionEvents_AggregateEverySimulationStepInOrder()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);
        // HUD_02 becomes active at MessageBoxAllowedTick + HUD_01's 113 ticks +
        // the released 4-tick advance gap = 238. Step to 236 so the two-step
        // frame below straddles it.
        for (int tick = 0; tick < 237; tick++)
        {
            session.AdvanceFrameTicks(OneCoreStepTicks);
        }

        FrameAdvanceResult frame = session.AdvanceFrameTicks(1_000_000);

        Assert.Equal(2, frame.StepsAdvanced);
        Level100MessageRequested message = Assert.Single(
            frame.Level100MissionEvents.OfType<Level100MessageRequested>());
        Assert.Equal(293386, message.MessageId);
        Assert.Empty(frame.CurrentSnapshot.Level100MissionEvents);
    }

    [Fact]
    public void FrameDestructionEvents_AggregateTheReleaseTickInOrder()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);
        while (session.CurrentSnapshot.Tick < FirstFlightSmokeScenario.DurationTicks)
        {
            session.ObserveInput(
                FirstFlightSmokeScenario.GetInputForTick(session.CurrentSnapshot.Tick));
            session.AdvanceFrameTicks(OneCoreStepTicks);
        }

        // Use the released static Target Tank 2 so a multi-step client frame
        // exercises event aggregation without a waypoint mover changing the
        // contact pose during the release tick.
        TargetSnapshot target = session.CurrentSnapshot.Targets.Single(item => item.Id == 2);
        Level100ActorPoseSnapshot contactPose =
            PlaceTargetCenterAtPulseEmitter(session.CurrentSnapshot);
        session.QueueFirePulse();

        FrameAdvanceResult frame = session.AdvanceFrameTicks(
            InteractiveSession.MaximumFrameElapsedTicks,
            [
                new Level100ActorActivationFact(target.ActorId, true),
                new Level100ActorPoseFact(target.ActorId, contactPose),
            ]);

        Assert.Equal(5, frame.StepsAdvanced);
        Level100DestructionEvent[] targetEvents = frame.Level100DestructionEvents
            .Where(item => item.ActorId == target.ActorId.Value)
            .ToArray();
        Assert.Equal(
            new[]
            {
                Level100DestructionEventKind.PulseImpact,
                Level100DestructionEventKind.SegmentDamaged,
            },
            targetEvents.Select(item => item.Kind));
        Assert.All(
            targetEvents.Where(item =>
                item.Kind == Level100DestructionEventKind.PulseImpact),
            item => Assert.Equal(
                Level100DestructionEffectKind.PulseImpact,
                item.EffectKind));
        float pulseDamage =
            BitConverter.UInt32BitsToSingle(Level100DestructionState.PulseDamageBits);
        float afterFirstHit = 6f - pulseDamage;
        Assert.Equal(
            new[]
            {
                BitConverter.SingleToUInt32Bits(afterFirstHit),
            },
            targetEvents
                .Where(item => item.Kind == Level100DestructionEventKind.SegmentDamaged)
                .Select(item => item.RemainingHealthBits));
        Assert.Empty(frame.CurrentSnapshot.Level100DestructionEvents);
        Assert.Empty(session.AdvanceFrameTicks(0).Level100DestructionEvents);
    }

    [Fact]
    public void ClientLevel100FailureTape_FirstRunRepeatsLossTextAndHashes()
    {
        ClientMissionTape first = RunClientFailureTape();
        ClientMissionTape repeat = RunClientFailureTape();

        Assert.Equal(first.Hashes, repeat.Hashes);
        Assert.Equal(Level100MissionOutcome.Lost, first.Snapshot.Level100Mission.Outcome);
        Assert.Equal(1_110_345_999, first.Snapshot.Level100Mission.FailureTextId);
        Assert.Equal(
            Level100MissionTerminalState.FailureCountdownElapsed,
            first.Snapshot.Level100Mission.TerminalState);
    }

    [Fact]
    public void ClientAssembly_HasNoGodotOrForbiddenRuntimeDependencies()
    {
        string[] references = typeof(InteractiveSession).Assembly
            .GetReferencedAssemblies()
            .Select(reference => reference.Name ?? string.Empty)
            .ToArray();

        Assert.DoesNotContain(references, name => name.StartsWith("Godot", StringComparison.Ordinal));
        Assert.DoesNotContain(references, name => name == "System.Diagnostics.Process");
        Assert.DoesNotContain(references, name => name == "System.IO.FileSystem");
        Assert.DoesNotContain(references, name => name == "System.Net.Http");
    }

    [Fact]
    public void MaterializedLevel100ActorDefinitions_OwnCompleteWorldAndAuthoredSpawns()
    {
        Level100ActorDefinitionSet definitions = LoadMaterializedActorDefinitions();

        Assert.Equal(44, definitions.Actors.Count);
        Assert.Equal(33, definitions.Actors.Count(actor =>
            actor.DefinitionIdentity.StartsWith("wres:bswd:", StringComparison.Ordinal)));
        Assert.Equal(3, definitions.Actors.Count(actor =>
            actor.DefinitionIdentity.StartsWith("wres:rlwd:", StringComparison.Ordinal) &&
            actor.TargetGroup == Level100MissionTargetGroup.StaticTargets));
        Assert.Equal(5, definitions.Actors.Count(actor => actor.Trigger.HasValue));
        Assert.Single(definitions.Actors, actor => actor.ThingTypeMask ==
            Level100ReleasedThingTypeMasks.BattleEngine);
        Assert.Contains(definitions.Actors, actor => actor.Name == "Transporter");
        Assert.Contains(definitions.Actors, actor => actor.Name == "Air Trainer");
        Assert.Equal(10, definitions.Spawns.Count);
        Assert.Equal(5, definitions.MotionDefinitions.Count);
        Assert.Equal(
            [
                ("Target Tank", Level100ActorMotionClass.GroundVehicle,
                    3, 2, 0x005E297C, 2_000),
                ("Target Truck", Level100ActorMotionClass.GroundVehicle,
                    3, 2, 0x005E297C, 2_000),
                ("Air Trainer", Level100ActorMotionClass.Plane,
                    9, 8, 0x005E1930, 5_000),
                ("Target Drone", Level100ActorMotionClass.Plane,
                    9, 8, 0x005E1930, 5_000),
                ("U-17 Highside Transporter",
                    Level100ActorMotionClass.Dropship,
                    12, 12, 0x005E1DD8, 8_000),
            ],
            definitions.MotionDefinitions.Select(definition =>
                (
                    definition.DefinitionName,
                    definition.MotionClass,
                    definition.BehaviorSerializedType,
                    definition.BehaviorInternalId,
                    definition.SteamClassVtableAddress,
                    definition.ArrivalRadiusMillimeters)));
        Assert.All(
            definitions.MotionDefinitions.Where(definition =>
                definition.MotionClass ==
                Level100ActorMotionClass.GroundVehicle),
            definition =>
            {
                Assert.Equal(0x40600000,
                    definition.MaximumSpeedFloatBits);
                Assert.Equal(0x3D567750,
                    definition.MaximumTurnRadiansPerBaseTickFloatBits);
                Assert.Equal(4, definition.FullGuideBaseTicks);
                Assert.Equal(100,
                    definition.CoreGroundOriginOffsetMillimeters);
            });
        Assert.All(
            definitions.MotionDefinitions.Where(definition =>
                definition.MotionClass !=
                Level100ActorMotionClass.GroundVehicle),
            definition =>
            {
                Assert.Null(definition.MaximumSpeedFloatBits);
                Assert.Null(
                    definition.MaximumTurnRadiansPerBaseTickFloatBits);
                Assert.Null(definition.FullGuideBaseTicks);
                Assert.Null(
                    definition.CoreGroundOriginOffsetMillimeters);
            });
        Assert.Equal(
            [
                "Flyby Path",
                "Target Truck Path 3",
                "Target Truck Path 2",
                "Target Truck Path 1",
                "Transporter Path",
                "Target Tank Path 2",
                "Target Tank Path 1",
                "Drone Path 1",
            ],
            definitions.WaypointPaths.Select(path => path.Name));
        // Re-pinned 2026-07-27 by the waypoint coordinate correction. These
        // values used to come from the 121-entry navigation graph, which holds
        // 11 distinct XY tuples repeated 11 times, all at z = 10.0. Node 25 is
        // RLWD initial-actor ordinal 25, a thingType-18 marker authored at
        // retail (248.75, 275.0, -0.0).
        Level100WaypointPathDefinition truckPath =
            definitions.GetWaypointPath("Target Truck Path 1");
        Assert.Equal([25, 26, 27, 28], truckPath.Points.Select(point => point.NodeIndex));
        Assert.Equal(
            new SimVector3(-39_938, 0, 31_750),
            truckPath.Points[0].PositionMillimeters);
        Assert.Equal(
            new Level100FloatVector4Bits(
                BitConverter.SingleToInt32Bits(248.75f),
                BitConverter.SingleToInt32Bits(275.0f),
                BitConverter.SingleToInt32Bits(-0.0f),
                BitConverter.SingleToInt32Bits(0.0f)),
            truckPath.Points[0].RetailComponentsFloatBits);
        // No two of the 30 authored markers resolve to one position any more.
        // Before the correction these 30 points collapsed onto 11, and this
        // assertion is the regression guard for that specific failure.
        Assert.Equal(
            30,
            definitions.WaypointPaths
                .SelectMany(path => path.Points)
                .Select(point => point.PositionMillimeters)
                .Distinct()
                .Count());
        // `Flyby Path` and `Target Truck Path 2` used to share their first
        // three points exactly. They are the aliasing pair named in the
        // measurement, so they are the pair pinned here.
        Assert.Empty(
            definitions.GetWaypointPath("Flyby Path").Points
                .Select(point => point.PositionMillimeters)
                .Intersect(
                    definitions.GetWaypointPath("Target Truck Path 2").Points
                        .Select(point => point.PositionMillimeters)));
        // The two ambient aircraft routes carry their own authored altitude:
        // the Air Trainer's markers sit at retail z = -15 and the Transporter's
        // at z = -20. Every node used to be flattened to Y = +10000 mm.
        Assert.Equal(
            [0, -15_000, -15_000],
            definitions.GetWaypointPath("Flyby Path").Points
                .Select(point => point.PositionMillimeters.Y));
        // The decoder reads the schema v14 traversal fields. They shipped on
        // 2026-07-27 and were dropped on the floor here until #146, which is
        // why the Air Trainer flew this route from its far end: `Points` is the
        // SERIALIZED order and the chain is the order retail walks.
        Assert.Equal(
            [41, 42, 43],
            definitions.GetWaypointPath("Flyby Path").TargetChainNodeIndices);
        Assert.False(definitions.GetWaypointPath("Flyby Path").IsClosed);
        Assert.True(definitions.GetWaypointPath("Drone Path 1").IsClosed);
        Assert.Equal(
            41,
            definitions.GetWaypointPath("Flyby Path").ChainPoint(0).NodeIndex);
        Level100SpawnDefinition[] trainingTrucks = definitions.Spawns
            .Where(spawn => spawn.ScriptName is
                "TargetTruck1" or "TargetTruck2" or "TargetTruck3")
            .ToArray();
        Assert.Equal(3, trainingTrucks.Length);
        Assert.All(trainingTrucks, spawn =>
            Assert.Equal(SimulationConstants.Level100TrainingTruckLife, spawn.InitialHealth));
        Level100WaypointPathDefinition transporterPath =
            definitions.GetWaypointPath("Transporter Path");
        Assert.Equal([44, 22, 23], transporterPath.Points.Select(point => point.NodeIndex));
        // This pair used to assert the defect: nodes 44 and 22 resolved to the
        // SAME point, because the navigation graph they were read from repeats
        // its 11 positions. They are 92.2 m apart in the authored data, and
        // node 22 carries the Transporter's own -20 m cruise altitude.
        Assert.NotEqual(
            transporterPath.Points[0].PositionMillimeters,
            transporterPath.Points[1].PositionMillimeters);
        Assert.NotEqual(
            transporterPath.Points[0].RetailComponentsFloatBits,
            transporterPath.Points[1].RetailComponentsFloatBits);
        Assert.Equal(
            new SimVector3(68_313, 0, 28_750),
            transporterPath.Points[0].PositionMillimeters);
        Assert.Equal(
            new SimVector3(-47_688, -20_000, 36_500),
            transporterPath.Points[1].PositionMillimeters);
        Assert.Equal(
            new SimVector3(-20_188, -20_000, 23_250),
            transporterPath.Points[2].PositionMillimeters);
        Assert.Equal(64, definitions.IdentitySha256.Length);
        Assert.Null(definitions.Actors.Single(actor => actor.Name == "Airfield").ScriptName);
        Assert.Null(definitions.Actors.Single(actor => actor.Name == "Hangar").ScriptName);

        Level100SpawnDefinition trainer = definitions.Spawns.Single(spawn =>
            spawn.ScriptName == "AirTrainer");
        Assert.Equal("wres:bswd:0023", trainer.OwnerDefinitionIdentity);
        Assert.Equal(
            BitConverter.SingleToInt32Bits(-0.099276736f),
            trainer.AuthoredEmitterTransform.LocalPositionFloatBits.X);

        var registry = new Level100ActorRegistry(definitions);
        Level100ActorId trainerId = Assert.Single(registry.SpawnThing(
            registry.GetThingRef("Airfield")!.Value,
            "Air Trainer",
            "SpawnerB",
            1,
            "AirTrainer"));
        // Re-derived 2026-08-01 by task #154. The manifest's authored spawn
        // vertical moved -6133 -> -3867 with the datum correction, and
        // Level100ActorRegistry.SeatOnGround now applies the general
        // CThing::Init support clamp instead of the ground-vehicle-only one, so
        // the spawn is seated on the terrain sample at the emitter's own
        // (46216, 14450), which is 0. Everything else about the pose is still
        // the authored pose verbatim; the two are asserted separately so a
        // basis or velocity that moved could not hide behind the vertical.
        Assert.Equal(-3_867, trainer.InitialPose.PositionMillimeters.Y);
        Assert.Equal(
            trainer.InitialPose with
            {
                PositionMillimeters =
                    trainer.InitialPose.PositionMillimeters with { Y = 0 },
            },
            registry.GetActor(trainerId).Pose);
        Assert.DoesNotContain(registry.Snapshot.Actors, actor => actor.Pose is null);
    }

    [Fact]
    public void MaterializedActorCommands_DriveCanonicalMechanicsOwner()
    {
        Level100ActorDefinitionSet definitions = LoadMaterializedActorDefinitions();
        var simulation = new Simulation(Seed, definitions);
        WorldSnapshot snapshot = simulation.Snapshot;

        Level100ActorSnapshot factory = snapshot.Level100Actors.Actors.Single(
            actor => actor.Name == "Tank Factory");
        Assert.False(factory.Active);
        Level100ActorSnapshot target = snapshot.Level100Actors.Actors.Single(
            actor => actor.ScriptName == "TargetTank1");
        Assert.Equal(factory.ActorId, target.SpawnOwnerId);
        Assert.Equal("SpawnerA", target.SpawnerName);
        Assert.Equal(6_000, target.Health);

        Level100ActorCommandIntentSnapshot intent = Assert.Single(
            snapshot.Level100ActorMechanics.Actors,
            item => item.ActorId == target.ActorId);
        Assert.Equal(Level100ActorCommandIntent.FollowingWaypoint, intent.Intent);
        Assert.Equal("Target Tank Path 1", intent.WaypointPath);
        Assert.True(intent.WaitForWaypointCompletion);
        Assert.Equal(0, intent.GroundFullGuideBaseTickPhase);
        Assert.Contains(
            snapshot.Level100ActorScriptCommands,
            command =>
                command.ActorId == target.ActorId &&
                command.Kind ==
                    Level100ActorScriptCommandKind.FollowWaypointWait &&
                command.Argument == intent.WaypointPath);
        Assert.Equal(
            definitions.IdentitySha256,
            snapshot.Level100Actors.DefinitionSetIdentitySha256);
    }

    [Fact]
    public void MaterializedTargetTank1_FollowsReleasedRouteNaturally()
    {
        Level100ActorDefinitionSet definitions =
            LoadMaterializedActorDefinitions();
        var simulation = new Simulation(Seed, definitions);
        WorldSnapshot snapshot = simulation.Snapshot;
        Level100ActorId targetId =
            snapshot.Level100Actors.Actors.Single(actor =>
                actor.ScriptName == "TargetTank1").ActorId;
        bool reachedSecondNode = false;
        bool reachedThirdNode = false;
        bool completed = false;

        for (int tick = 0; tick < 3_000; tick++)
        {
            snapshot = simulation.Step(SimInput.Idle);
            Level100ActorCommandIntentSnapshot intent =
                snapshot.Level100ActorMechanics.Actors.Single(item =>
                    item.ActorId == targetId);
            reachedSecondNode |=
                intent.WaypointPointIndex >= 1;
            reachedThirdNode |=
                intent.WaypointPointIndex >= 2;
            if (intent.Intent ==
                Level100ActorCommandIntent.Stopped)
            {
                completed = true;
                break;
            }
        }

        Assert.True(reachedSecondNode);
        Assert.True(reachedThirdNode);
        Assert.True(completed);
        Level100ActorSnapshot target =
            snapshot.Level100Actors.Actors.Single(actor =>
                actor.ActorId == targetId);
        // The end of the AUTHORED TRAVERSAL, which is the last entry of the
        // `target` chain and not of the serialized list. `Target Tank Path 1`
        // serializes [18, 6, 7] and is walked [6, 7, 18]; `Points[^1]` is node
        // 7, the route's MIDDLE, which the tank drives straight through.
        Level100WaypointPathDefinition route =
            definitions.GetWaypointPath("Target Tank Path 1");
        Level100WaypointPointDefinition destination =
            route.ChainPoint(route.TargetChainNodeIndices.Count - 1);
        long deltaX =
            (long)destination.PositionMillimeters.X -
            target.Pose.PositionMillimeters.X;
        long deltaZ =
            (long)destination.PositionMillimeters.Z -
            target.Pose.PositionMillimeters.Z;
        Assert.True(
            (deltaX * deltaX) + (deltaZ * deltaZ) <
            2_000L * 2_000L);
        Assert.Equal(
            Level100Terrain.Instance.SampleGroundElevationMillimeters(
                new SimVector2(
                    target.Pose.PositionMillimeters.X,
                    target.Pose.PositionMillimeters.Z)) +
                100,
            target.Pose.PositionMillimeters.Y);
        Assert.Equal(
            SimVector3.Zero,
            target.Pose.LinearVelocityMillimetersPerTick);
        Assert.Equal(
            SimVector3.Zero,
            target.Pose.AngularVelocityMicroRadiansPerTick);
        Level100ActorScriptInstanceSnapshot targetScript =
            snapshot.Level100ActorScripts.Instances.Single(item =>
                item.ActorId == targetId);
        Assert.DoesNotContain(
            targetScript.Continuations,
            continuation =>
                continuation.WaitKind ==
                Level100ActorScriptWaitKind.FollowWaypoint);
    }

    [Fact]
    public void TargetPresentation_ProjectsWarehouseAndNewTruckCanonicalBindings()
    {
        var actorId = new Level100ActorId(47);
        var identityBasis = new Level100FloatBasis3Bits(
            0x3F800000, 0, 0,
            0, 0x3F800000, 0,
            0, 0, 0x3F800000);
        var firstPose = new Level100ActorPoseSnapshot(
            new SimVector3(1_000, 2_000, 3_000),
            identityBasis,
            SimVector3.Zero,
            SimVector3.Zero);
        var target = new TargetSnapshot(
            actorId,
            5,
            "Target Truck",
            "m_f_truck_training.msh.aya",
            new SimVector2(1_000, 3_000),
            3_000,
            true,
            firstPose);

        Level100TargetVisualDescriptor first =
            Level100TargetPresentation.Project(target);
        var turnedPose = firstPose with
        {
            PositionMillimeters = new SimVector3(
                -4_000,
                5_000,
                -6_000),
            BasisFloatBits = new Level100FloatBasis3Bits(
                0, 0, unchecked((int)0xBF800000),
                0, 0x3F800000, 0,
                0x3F800000, 0, 0),
        };
        Level100TargetVisualDescriptor changed =
            Level100TargetPresentation.Project(
                target with
                {
                    Position = new SimVector2(-4_000, -6_000),
                    Pose = turnedPose,
                });

        Assert.Equal(actorId, first.ActorId);
        Assert.Equal("Target Truck", first.DefinitionName);
        Assert.Equal(
            "m_f_truck_training.msh.aya",
            first.MeshBinding);
        Assert.Equal(
            Level100TargetPresentation.TargetTruckBinding,
            first.Binding);
        Assert.True(first.Visible);
        Assert.Equal(1f, first.Position.X, 5);
        Assert.Equal(2f, first.Position.Y, 5);
        Assert.Equal(-3f, first.Position.Z, 5);
        Assert.Equal(
            new Level100RenderBasis3(
                new Level100RenderVector3(1f, 0f, 0f),
                new Level100RenderVector3(0f, 1f, 0f),
                new Level100RenderVector3(0f, 0f, 1f)),
            first.Basis);
        Assert.Equal(actorId, changed.ActorId);
        Assert.Equal(-4f, changed.Position.X, 5);
        Assert.Equal(5f, changed.Position.Y, 5);
        Assert.Equal(6f, changed.Position.Z, 5);
        Assert.Equal(
            new Level100RenderBasis3(
                new Level100RenderVector3(0f, 0f, -1f),
                new Level100RenderVector3(0f, 1f, 0f),
                new Level100RenderVector3(1f, 0f, 0f)),
            changed.Basis);
        Assert.NotEqual(first, changed);
        Assert.False(
            Level100TargetPresentation.Project(
                target with { IsActive = false }).Visible);

        var session = new InteractiveSession(
            Seed,
            LoadMaterializedActorDefinitions());
        TargetSnapshot warehouse =
            session.CurrentSnapshot.Targets.Single(item => item.Id == 4);
        Level100TargetVisualDescriptor warehouseDescriptor =
            Level100TargetPresentation.Project(warehouse);
        Assert.Equal(
            Level100TargetPresentation.WarehouseBinding,
            warehouseDescriptor.Binding);
        Assert.Equal("Warehouse", warehouseDescriptor.DefinitionName);
        Assert.Equal(
            "m_m_warehouse.msh.aya",
            warehouseDescriptor.MeshBinding);
    }

    [Fact]
    public void MaterializedTargetZone1_SpawnsThreeTrucksIntoCanonicalMover()
    {
        Level100ActorDefinitionSet definitions =
            LoadMaterializedActorDefinitions();
        var session =
            new InteractiveSession(Seed, definitions);
        Level100ActorSnapshot[] trucks = [];

        while (session.CurrentSnapshot.Tick <
            FirstFlightSmokeScenario.DurationTicks)
        {
            session.ObserveInput(
                FirstFlightSmokeScenario.GetInputForTick(
                    session.CurrentSnapshot.Tick));
            session.AdvanceFrameTicks(OneCoreStepTicks);
            trucks = session.CurrentSnapshot.Level100Actors.Actors
                .Where(actor =>
                    actor.TargetGroup ==
                    Level100MissionTargetGroup.TargetTrucks)
                .OrderBy(actor => actor.ScriptName)
                .ToArray();
            if (trucks.Length == 3 &&
                trucks.All(actor =>
                {
                    Level100SpawnDefinition spawn =
                        definitions.Spawns.Single(definition =>
                            definition.ScriptName ==
                            actor.ScriptName);
                    return actor.Pose.PositionMillimeters !=
                        spawn.InitialPose.PositionMillimeters;
                }))
            {
                break;
            }
        }

        Assert.Equal(3, trucks.Length);
        Assert.Equal(
            ["TargetTruck1", "TargetTruck2", "TargetTruck3"],
            trucks.Select(actor => actor.ScriptName));
        HashSet<Level100ActorId> truckActorIds =
            trucks.Select(actor => actor.ActorId).ToHashSet();
        TargetSnapshot[] truckTargets =
            session.CurrentSnapshot.Targets
                .Where(target => truckActorIds.Contains(target.ActorId))
                .OrderBy(target => target.Id)
                .ToArray();
        Assert.Equal(3, truckTargets.Length);
        Assert.Equal([5, 6, 7], truckTargets.Select(target => target.Id));
        foreach (TargetSnapshot truckTarget in truckTargets)
        {
            Level100TargetVisualDescriptor descriptor =
                Level100TargetPresentation.Project(truckTarget);
            Assert.Equal(truckTarget.ActorId, descriptor.ActorId);
            Assert.Equal("Target Truck", descriptor.DefinitionName);
            Assert.Equal(
                "m_f_truck_training.msh.aya",
                descriptor.MeshBinding);
            Assert.Equal(
                Level100TargetPresentation.TargetTruckBinding,
                descriptor.Binding);
            Assert.True(descriptor.Visible);
        }
        foreach (Level100ActorSnapshot truck in trucks)
        {
            Level100SpawnDefinition spawn =
                definitions.Spawns.Single(definition =>
                    definition.ScriptName ==
                    truck.ScriptName);
            Assert.Equal(
                spawn.OwnerDefinitionIdentity,
                session.CurrentSnapshot.Level100Actors.Actors
                    .Single(actor =>
                        actor.ActorId == truck.SpawnOwnerId)
                    .DefinitionIdentity);
            Assert.Equal(
                SimulationConstants.Level100TrainingTruckLife,
                truck.Health);
            Assert.NotEqual(
                spawn.InitialPose.PositionMillimeters,
                truck.Pose.PositionMillimeters);
            Assert.Equal(
                Level100Terrain.Instance
                    .SampleGroundElevationMillimeters(
                        new SimVector2(
                            truck.Pose.PositionMillimeters.X,
                            truck.Pose.PositionMillimeters.Z)) +
                    100,
                truck.Pose.PositionMillimeters.Y);
            Level100ActorCommandIntentSnapshot intent =
                session.CurrentSnapshot.Level100ActorMechanics.Actors
                    .Single(item =>
                        item.ActorId == truck.ActorId);
            Assert.Equal(
                Level100ActorCommandIntent.FollowingWaypoint,
                intent.Intent);
            Assert.Equal(
                $"Target Truck Path {truck.ScriptName![^1]}",
                intent.WaypointPath);
        }
    }

    [Fact]
    public void MaterializedLevel100ActorDefinitions_RepeatFailureHashes()
    {
        Level100ActorDefinitionSet definitions = LoadMaterializedActorDefinitions();

        ClientMissionTape failure = RunClientFailureTape(definitions);
        ClientMissionTape repeatedFailure = RunClientFailureTape(definitions);

        Assert.Equal(failure.Hashes, repeatedFailure.Hashes);
        Assert.Equal(Level100MissionOutcome.Lost, failure.Snapshot.Level100Mission.Outcome);
    }

    [Fact]
    public void FirstFlightSmokeScenario_ReachesFiringRangeAndCompletesWaypoint()
    {
        InteractiveInput pan = FirstFlightSmokeScenario.GetInputForTick(0);
        InteractiveInput strafe = FirstFlightSmokeScenario.GetInputForTick(
            FirstFlightSmokeScenario.TargetZoneInputStartTick);
        InteractiveInput forward = FirstFlightSmokeScenario.GetInputForTick(
            FirstFlightSmokeScenario.TargetZoneInputStartTick + 144);
        InteractiveInput closeout = FirstFlightSmokeScenario.GetInputForTick(
            FirstFlightSmokeScenario.DurationTicks - 1);
        InteractiveInput firingRangeTurn = FirstFlightSmokeScenario.GetInputForTick(1_330);
        InteractiveInput firingRangeApproach = FirstFlightSmokeScenario.GetInputForTick(1_360);
        InteractiveInput firingRangeAim = FirstFlightSmokeScenario.GetInputForTick(2_093);
        InteractiveInput pulseCannonProof = FirstFlightSmokeScenario.GetInputForTick(2_104);

        Assert.Equal(InteractiveInput.Idle, pan);
        Assert.Equal((sbyte)-1, strafe.MoveX);
        Assert.False(strafe.FireHeld);
        Assert.Equal((sbyte)1, forward.MoveZ);
        Assert.False(forward.ToggleModeHeld);
        Assert.Equal((sbyte)-1, firingRangeTurn.MoveX);
        Assert.Equal((sbyte)1, firingRangeApproach.MoveZ);
        Assert.Equal((sbyte)-1, firingRangeAim.LookX);
        Assert.True(pulseCannonProof.FireHeld);
        Assert.Equal(InteractiveInput.Idle, closeout);
        Assert.Equal(2_148, FirstFlightSmokeScenario.DurationTicks);
        Assert.Throws<ArgumentOutOfRangeException>(() => FirstFlightSmokeScenario.GetInputForTick(-1));

        var session = new InteractiveSession(
            Seed,
            LoadMaterializedActorDefinitions());
        while (session.CurrentSnapshot.Tick < FirstFlightSmokeScenario.DurationTicks)
        {
            session.ObserveInput(
                FirstFlightSmokeScenario.GetInputForTick(session.CurrentSnapshot.Tick));
            FrameAdvanceResult result = session.AdvanceFrameTicks(500_000);
            Assert.Equal(1, result.StepsAdvanced);
        }

        TargetSnapshot firstTarget = session.CurrentSnapshot.Targets.Single(target => target.Id == 1);
        Assert.True(firstTarget.IsActive);
        Assert.Equal(SimulationConstants.Level100TargetTankLife, firstTarget.Hull);
        Assert.Equal(0, session.CurrentSnapshot.TargetsDestroyed);
        Level100ActorScriptInstanceSnapshot targetScript =
            session.CurrentSnapshot.Level100ActorScripts.Instances.Single(item =>
                item.ActorId == firstTarget.ActorId);
        Assert.DoesNotContain(
            targetScript.Continuations,
            continuation =>
                continuation.WaitKind ==
                Level100ActorScriptWaitKind.FollowWaypoint);
        Level100ActorCommandIntentSnapshot targetIntent =
            session.CurrentSnapshot.Level100ActorMechanics.Actors.Single(item =>
                item.ActorId == firstTarget.ActorId);
        Assert.Equal(
            Level100ActorCommandIntent.Stopped,
            targetIntent.Intent);
        Assert.Equal(4, session.Metrics.FireHeldTicksSampled);
        Assert.Equal(4, session.Metrics.FirePulseEdgesConsumed);
        // Re-pinned 2026-07-26 from c3ae5a39... after Level100ActorRegistry
        // began ground-seating authored actors, which retail's CThing::Init
        // (0x004F34A0) does and this reconstruction did not: Target Tank 2,
        // Target Tank 3 and Target Warehouse sat 600/600/426 mm underground.
        //
        // The delta was NOT assumed to be the seating - it was measured
        // causally. Disabling ONLY SeatOnGround and re-running the smoke
        // returns this hash to c3ae5a39... exactly, so the seating accounts for
        // the whole move and the Twin Vulcan Cannon added in the same change
        // contributes nothing to this scenario.
        //
        // MOVED AGAIN 2026-07-27 by the MaximumHull unit correction, 1_000 ->
        // 20_000. StateHasher hashes raw Hull, so a units change to the player's
        // health necessarily moves this hash and its move here is expected
        // rather than suspicious.
        //
        // Measured causally the same way: reverting ONLY MaximumHull to 1_000
        // and rebuilding returns this assertion to ab1e5844... exactly, so the
        // hull unit accounts for the whole move and nothing else changed
        // behaviour. No damage number, threshold or trajectory moved - the
        // conversion in
        // Level100ActorWeapons.IncomingDamageMilliLifeFromFloatBits scaled with
        // MaximumHull, so the former direct-hull shortcut kept hits-to-kill
        // identical on both sides. The later shield-law reconstruction is a
        // separate trajectory change.
        // DID NOT MOVE 2026-07-27 for the WalkerEnergyRegenerationPerTick
        // correction, 4 -> 33, and that is a measurement rather than an
        // assumption. This scenario is walker-only, so energy is never spent by
        // flight; it dips to a measured minimum of 7,970 of 8,000 and the regen
        // clamps it back to the maximum well before the final snapshot, which
        // is the only state this hashes. Walker dynamics do not read energy
        // above zero - it only feeds `_shield` - so neither trajectory nor
        // final value differs. Checked both ways: the constant at 4 and at 33
        // both produce fb2219b6... exactly.
        // MOVED 2026-07-27 for the released message-box gate
        // (Level100MissionTiming.MessageBoxAllowedTick /
        // MessageAdvanceDelayTicks). The scenario's inputs are unchanged, but
        // the LevelScript now blocks on PlayCharMessageWait until the message
        // box is allowed to play, so player.Activate() lands at tick 996
        // instead of 790 and every later script step follows. Isolated
        // causally, not argued: stashing this change alone and re-running this
        // test returns fb2219b6f39e768ad68facf648c1697d8de955b46316b991e547262
        // 77c6c4927 exactly, and restoring it returns this value again.
        // MOVED AGAIN 2026-07-27 for the weapon-fire event stream. This one is
        // STRUCTURAL, not behavioural: StateHasher gained a version bump 30->31
        // and now appends Level100WeaponFireEvents, so every hashed tick carries
        // a new four-byte count whether or not a weapon fires. No simulation
        // state is read differently - the hasher diff adds fields and changes
        // nothing else.
        // Isolated causally on a three-point ladder rather than argued:
        //   v30, stream NOT written  -> 84d6fcae... , the previous golden,
        //                               reproduced EXACTLY
        //   v30, stream written      -> 7e67640e...
        //   v31, stream written      -> this value
        // The first row is the proof: revert only the hasher edit and the old
        // golden returns bit for bit, so the four fire events at ticks 3157,
        // 3165, 3173 and 3185 changed no state - they are only now recorded.
        // MOVED AGAIN 2026-07-27 for the released action set. STRUCTURAL, like
        // the last one: StateHasher went 31 -> 32 and one int32 is appended.
        // Isolated MECHANICALLY, not argued — canonical bytes were dumped at 15
        // ticks before and after, and every "after" stream was reconstructed
        // from its "before" by exactly two edits: the version int at byte 23,
        // and an inserted int32 182 (MessageBoxAllowedTick). ALL TICKS
        // EXPLAINED. Message start ticks are identical either side
        // (182, 357, 573, 762, 931, 1002, 1223), so no schedule moved.
        // The same three-point ladder as before also holds: with the whole
        // change in place EXCEPT the two StateHasher lines, this test passes
        // with the previous golden reproduced exactly.
        //
        // MOVED AGAIN 2026-07-27 by the waypoint-path coordinate correction
        // (task #114 section 4-B). This one is BEHAVIOURAL, not structural:
        // StateHasher is unchanged at version 32. The manifest's eight named
        // paths now resolve against the RLWD thingType-18 marker records
        // instead of the 121-entry navigation graph, so the routes are real.
        //
        // TWO mechanisms, both intended, and both were measured rather than
        // argued. Reverting ONLY the two files the correction touches
        // (materialize_retail_assets.py and Level100ActorDefinitionManifest.cs)
        // and re-materializing returns this assertion to
        // 673661bba2fd43b4af3175b9fa028fb00133460361fb2b93137a289b497c1fe8
        // exactly. A field-level dump of the same scenario either side isolates
        // the whole delta to:
        //   1. Level100ActorRegistry.ComputeIdentity, which hashes every
        //      waypoint point's position and retail component bits, and whose
        //      digest StateHasher writes. It moves
        //      1a6bb9b711f4eba15f7c2f51132b3ca5141399a37b748ac47b532975e1d0585b
        //      -> e3916c3c1614e251a62e177489d45b66e55ad8fde603e2928a372b475e2029e3.
        //   2. The five waypoint-following actors' poses and intents, because
        //      they now drive the authored routes. Target Tank 1 ends at
        //      (-68648, 1100, 50244) rather than (31409, 9277, 70361); the
        //      ambient Air Trainer finishes its three-point pass and reaches
        //      Retreating instead of still sitting on point 1 at tick 3228.
        //
        // NOTHING ELSE MOVED, and that is the check that makes the move safe to
        // accept. Every mission schedule transition is identical either side -
        // NextSequence at ticks 1..3202, PulseCannon Disabled at 1 and Enabled
        // at 3142, MechVulcan at 1, player Activate at 3142, TargetsDestroyed
        // unchanged. Player position, yaw, pitch, mission tick and outcome are
        // identical. All 39 static and base-world actor poses are identical,
        // including the Transporter, whose Dropship motion class is still
        // unimplemented so it stays frozen at its authored pose.
        //
        // #146 MOVED THIS, AND THE MOVE WAS ADJUDICATED AND ACCEPTED 2026-07-31
        // by the integrating owner: the traversal-order law is byte-proven from
        // the pristine specimen (74154bfa, CScriptEventNB::UpdateWaypointFollowing
        // 0x00538470 advances by the waypoint's own successor pointer) and
        // runtime-confirmed in the play-level100 trace; the repin followed the
        // two-byte-identical-native-reports protocol, and the measured value
        // reproduced independently in two separate trees. The waypoint
        // TRAVERSAL-ORDER correction:
        // 0f1fb80918c5acb42f2c7025736b6690d9a47109b594d0307ec90d7ecd25f5ba
        // -> 8a89e33dc3cd689786a2e4b18e3e40992b8bc1a29f9f7c2917d7d4ea4ce08ec1.
        // The route COORDINATES did not change; the order the followers walk
        // them in did. Six of the eight paths serialize their nodes in an order
        // that is not the order the markers' own `target` pointers chain them,
        // and until now the product indexed the serialized list.
        //
        // Two independent causes, isolated rather than argued. Re-running this
        // scenario against a definition set that differs from the shipped one
        // ONLY in having each path's chain overwritten with its own serialized
        // order - i.e. the pre-#146 behaviour under the post-#146 hasher -
        // gives 46d69bd0359ebf0898bd960e5b1bdb1024d7ad08cb849cc68368d0482eccc997
        // and definition identity f2e664a301d670a1d036942f9c86955c156c6f5faa32
        // 492a02dbf345efa5c04f, against the shipped 005d10fa0e247e97f71b5ddcaf5
        // 159d64505b66d539ed6d426f235a999dcdf64. So:
        //   1. STRUCTURAL. Level100ActorRegistry.ComputeIdentity went to
        //      version 6 and now hashes TargetChainNodeIndices and IsClosed.
        //      Those fields decide motion, so leaving them out of the
        //      definition identity would let a route silently change order
        //      without the identity moving. No behaviour rides on this half.
        //   2. BEHAVIOURAL. Four of the 48 actors end the scenario somewhere
        //      else, all four of them waypoint followers, measured either side:
        //        Air Trainer      (31445, 23906, -96389) was (78086, 27136, 51089)
        //        Target Tank #45  (-68781,  700,  78107) was (-68648, 1100, 50244)
        //        Target Truck #47 (-52537,  700,  91659) was (-51373, 1012, 39939)
        //        Target Truck #48 (-47665,  500,  84727) was (-53921, 1100, 41995)
        //      The Air Trainer now finishes its pass at node 43, the chain's
        //      tail, having started at node 41; before, it started at 43 and
        //      was still short of 41. Trucks #47 and #48 reach Stopped inside
        //      the scenario where before they were still FollowingWaypoint at
        //      chain index 3 - the corrected order is SHORTER for them, not
        //      merely different.
        //
        // The other 44 actor poses are identical, including the Transporter,
        // still frozen because Dropship motion remains unimplemented. Player
        // position (-66783, 68633), elevation 2500, yaw 282931, pitch 0, mode
        // Walker and hull 20000 are identical either side, as are the mission
        // outcome and the "Firing Range" navigation objective.
        // MOVED 2026-07-31 BY THE 30 Hz -> 20 Hz CORE MIGRATION (WORKSTREAM 4).
        // 8a89e33dc3cd689786a2e4b18e3e40992b8bc1a29f9f7c2917d7d4ea4ce08ec1
        // -> d4967b1206f851a27ef2bb998ffaae2575fb898f15dec67cdbead987b0737ed3.
        //
        // THIS ONE IS NOT ISOLABLE TO A SINGLE CAUSE AND IS NOT CLAIMED TO BE.
        // Four things move it and each would suffice alone:
        //   1. StateHasher's version literal, 32 -> 33.
        //   2. The DELETION of the hashed field
        //      Level100ActorMechanicsSnapshot.RetailBaseTickAccumulatorThirtieths -
        //      the 20-of-every-30 base-tick accumulator, which is the identity
        //      once Core runs at 20 Hz. Four bytes leave every hashed tick, so
        //      this alone moves the hash with NO behaviour change at all.
        //   3. state.Tick is hashed first and the tape's terminal tick is 2152
        //      where it was 3228 - the same 107.6 s of simulated time.
        //   4. Every trajectory is re-integrated against the reconverted
        //      constants.
        // Isolating them individually is not possible here, because (1) and (2)
        // are prerequisites of the rate change rather than separable edits.
        //
        // WHAT DID NOT CHANGE is the evidence that the tape still proves what it
        // proved, and it is asserted above rather than argued: Walker mode, zero
        // targets destroyed, Target Tank 1 alive at its full 6,000 hull with no
        // FollowWaypoint continuation and a Stopped intent, exactly four
        // fire-held ticks, and the "Firing Range" navigation objective.
        //
        // Cross-checked against the native Godot host: the same value appears in
        // rebuild/tools/FirstFlightSmokeValidation.psm1, produced by two
        // byte-identical native smoke reports through a completely different
        // host and frame clock.
        // MOVED 2026-08-01 BY THE VERTICAL DATUM (#154) AND THE LOOK-RESPONSE
        // TABLE (#161).
        // d4967b1206f851a27ef2bb998ffaae2575fb898f15dec67cdbead987b0737ed3
        // -> e41f55ff98b7d6e7b17a5c85e443533c46147dc81d2b0188ea56bbd89277dc16.
        //
        // Repinned under the two-byte-identical-native-reports protocol: two
        // runs of the native Godot smoke produced identical report files
        // (sha256 a71fd60ad692e695abe42250135d2cf90b3838bc02d3c1ff35739e27a4b5
        // 9a24, 3,859 bytes, all 86 fields equal) at exactly this value, so the
        // in-process tape here and a completely different host with a different
        // frame clock agree. The same value is pinned in
        // rebuild/tools/FirstFlightSmokeValidation.psm1, which also carries the
        // field-level accounting.
        //
        // TWO CAUSES, and they are not a sum:
        //   1. #154 moved it. StateHasher hashes every actor pose and the
        //      definition-set identity; the datum correction moved the vertical
        //      of all 44 authored actors and all 10 spawn definitions, and
        //      Level100ActorRegistry.SeatOnGround now applies the general
        //      CThing::Init support clamp to every class instead of to ground
        //      vehicles alone.
        //   2. #161 did NOT move it on its own - measured 2026-07-31, the
        //      1,001-entry look table left this hash at d4967b12 exactly,
        //      because every probe point this tape touches is on an entry the
        //      old and new tables agree about.
        //
        // NOTHING THE TAPE PROVES CHANGED, and that is asserted above rather
        // than argued: Walker mode, zero targets destroyed, Target Tank 1 alive
        // at its full 6,000 hull with no FollowWaypoint continuation and a
        // Stopped intent, exactly four fire-held ticks, and the "Firing Range"
        // navigation objective. The native report agrees field for field:
        // tick 2148, thirteen delivered messages, four objective markers, nine
        // target visuals, and the whole retail-geometry block are all unchanged.
        // MOVED 2026-08-09 by StateHasher v35. The selected Walker/Jet slots
        // and Twin Vulcan reload countdown are future-affecting state, so they
        // are now serialized. This scenario still ends on Pulse Cannon / Mech
        // Vulcan with reload zero; the gameplay assertions above are unchanged.
        // MOVED 2026-08-09 by the controller release-edge correction:
        // 897c1115... -> 419e7995.... Retail maps gun fire as BUTTON_RELEASE,
        // while the client had sent SimActions.Fire on every held tick. The
        // same four physical holds now produce exactly four falling edges; the
        // asserted mission/target outcome above is unchanged.
        // MOVED 2026-08-10 by StateHasher v36. Current and desired zoom now
        // affect the projection/look law and future easing, so both are
        // serialized. This tape never zooms and ends at 1000/1000; the moved
        // hash is structural and the gameplay assertions above are unchanged.
        // MOVED 2026-08-10 by StateHasher v37. The Walker opposite-flick
        // gesture history and live dash countdown are future-affecting state,
        // so all seven values are now serialized. The firing-range assertions
        // above remain the consequential gate for this smoke path.
        Assert.Equal(
            "1bd823fa5cd7196f0f4893ddbaab5825d66c6d9a8ed61ebd634934a271e1af86",
            StateHasher.ComputeHex(session.CurrentSnapshot));
    }

    private static InteractiveSession RunInteractiveSequence()
    {
        InteractiveSession session = CreatePlayingSession();
        (long ElapsedTicks, InteractiveInput Input)[] frames =
        [
            (100_000, new InteractiveInput(0, 1, false, false, false)),
            (250_000, new InteractiveInput(0, 1, true, false, false)),
            (500_000, new InteractiveInput(0, 1, true, true, false)),
            (1_100_000, new InteractiveInput(1, 0, true, false, false)),
            (500_000, new InteractiveInput(0, 0, false, false, true)),
            (700_000, InteractiveInput.Idle),
        ];

        foreach ((long elapsedTicks, InteractiveInput input) in frames)
        {
            session.ObserveInput(input);
            session.AdvanceFrameTicks(elapsedTicks);
        }

        return session;
    }

    private static ClientMissionTape RunClientFailureTape(
        Level100ActorDefinitionSet? actorDefinitions = null)
    {
        var tape = new ClientMissionTape(actorDefinitions);
        tape.Step([new Level100MissionInputFact(Level100MissionInput.BrokeTutorial)]);
        tape.AdvanceUntil(
            state => state.Level100Mission.Outcome == Level100MissionOutcome.Lost,
            // "Broke Tutorial" is posted while HUD_01 still owns the message
            // box, so its two messages queue behind it at the released advance
            // gap and the terminal call lands at tick 594 rather than 291.
            800);
        tape.Advance(Level100MissionTiming.FailureCountdownTicks);
        return tape;
    }

    private sealed class ClientMissionTape
    {
        private readonly InteractiveSession _session;

        internal ClientMissionTape(Level100ActorDefinitionSet? actorDefinitions = null)
        {
            _session = new InteractiveSession(
                0x100u,
                actorDefinitions ?? Level100TestActorDefinitions.Create());
            Capture(_session.AdvanceFrameTicks(0).Level100MissionEvents);
        }

        internal WorldSnapshot Snapshot => _session.CurrentSnapshot;

        internal List<Level100MissionEvent> Events { get; } = [];

        internal List<string> Hashes { get; } = [];

        internal void Step(IReadOnlyList<Level100SimulationFact>? facts = null) =>
            Step(InteractiveInput.Idle, facts);

        internal void Step(
            InteractiveInput input,
            IReadOnlyList<Level100SimulationFact>? facts = null)
        {
            _session.ObserveInput(input);
            FrameAdvanceResult result = _session.AdvanceFrameTicks(OneCoreStepTicks, facts);
            Assert.Equal(1, result.StepsAdvanced);
            Assert.Empty(result.CurrentSnapshot.Level100Mission.PendingEvents);
            Capture(result.Level100MissionEvents);
        }

        internal void Advance(int ticks)
        {
            for (int tick = 0; tick < ticks; tick++)
            {
                Step();
            }
        }

        internal void AdvanceUntil(Func<WorldSnapshot, bool> predicate, int maximumTicks)
        {
            for (int tick = 0; tick < maximumTicks && !predicate(Snapshot); tick++)
            {
                Step();
            }

            Assert.True(predicate(Snapshot),
                $"Condition was not reached by client tick {Snapshot.Tick}.");
        }

        private void Capture(IReadOnlyList<Level100MissionEvent> events)
        {
            Events.AddRange(events);
            Hashes.Add(StateHasher.ComputeHex(Snapshot));
        }
    }

    private static InteractiveSession CreatePlayingSession(uint seed = Seed)
    {
        var session = new InteractiveSession(seed, ActorDefinitions);
        for (int tick = 0; tick < FirstRunControlTick; tick++)
        {
            session.AdvanceFrameTicks(OneCoreStepTicks);
        }

        Assert.True(session.CurrentSnapshot.Level100PlayerControlEnabled);
        return session;
    }

    private static Level100ActorPoseSnapshot PlaceTargetCenterAtPulseEmitter(
        WorldSnapshot state)
    {
        double yaw = state.FacingYawMicroRad / 1_000_000d;
        double pitch = state.FacingPitchMicroRad / 1_000_000d;
        double emitterForwardPlane =
            (SimulationConstants.PulseCannonEmitterForwardMillimeters * Math.Cos(pitch)) +
            (SimulationConstants.PulseCannonEmitterUpMillimeters * Math.Sin(pitch));
        int emitterOffsetX = (int)Math.Round(
            (SimulationConstants.PulseCannonEmitterRightMillimeters * Math.Cos(yaw)) -
            (emitterForwardPlane * Math.Sin(yaw)),
            MidpointRounding.AwayFromZero);
        int emitterOffsetZ = (int)Math.Round(
            (SimulationConstants.PulseCannonEmitterRightMillimeters * Math.Sin(yaw)) +
            (emitterForwardPlane * Math.Cos(yaw)),
            MidpointRounding.AwayFromZero);
        int emitterVerticalOffset = (int)Math.Round(
            (-SimulationConstants.PulseCannonEmitterForwardMillimeters * Math.Sin(pitch)) +
            (SimulationConstants.PulseCannonEmitterUpMillimeters * Math.Cos(pitch)),
            MidpointRounding.AwayFromZero);
        var emitter = new SimVector3(
            state.PlayerPosition.X + emitterOffsetX,
            state.PlayerGroundElevationMillimeters +
                Level100Terrain.WalkerCenterOfGravityMillimeters +
                emitterVerticalOffset,
            state.PlayerPosition.Z + emitterOffsetZ);

        // The released Target Tank root broadphase center is contact-local
        // (43,-228,-275). Core is (retail X, up=-retail Z, retail Y).
        return new Level100ActorPoseSnapshot(
            new SimVector3(
                emitter.X - 43,
                emitter.Y - 275,
                emitter.Z + 228),
            new Level100FloatBasis3Bits(
                BitConverter.SingleToInt32Bits(1f), 0, 0,
                0, BitConverter.SingleToInt32Bits(1f), 0,
                0, 0, BitConverter.SingleToInt32Bits(1f)),
            SimVector3.Zero,
            SimVector3.Zero);
    }

    private static Level100ActorDefinitionSet LoadMaterializedActorDefinitions()
    {
        string path = Path.Combine(
            AppContext.BaseDirectory,
            "Assets",
            "Level100",
            "StaticWorld",
            "level100-static-world.json");
        return Level100ActorDefinitionManifest.Decode(File.ReadAllBytes(path));
    }
}
