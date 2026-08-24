// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class SimulationTests
{
    private static readonly Level100TutorialProgress CompletedTutorialSlots =
        new(Introduction: true, PulseCannon: true, VulcanCannon: true, StatusBars: true);

    [Fact]
    public void Constructor_RejectsZeroSeed()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            new Simulation(0, Level100TestActorDefinitions.Create()));
    }

    [Fact]
    public void RetailZoom_EasesLookAndProjectionScaleAndMorphForcesZoomOut()
    {
        Simulation simulation = CreatePlayingSimulation();

        Assert.Equal(SimulationConstants.ZoomOutPermille, simulation.Snapshot.ZoomPermille);
        Assert.Equal(
            SimulationConstants.ZoomOutPermille,
            simulation.Snapshot.DesiredZoomPermille);

        int[] zoomInSteps = [900, 800, 700, 600, 500, 400];
        for (int index = 0; index < zoomInSteps.Length; index++)
        {
            WorldSnapshot state = simulation.Step(new SimInput(
                0,
                0,
                index == 0 ? SimActions.ZoomIn : SimActions.None));
            Assert.Equal(zoomInSteps[index], state.ZoomPermille);
            Assert.Equal(SimulationConstants.ZoomInPermille, state.DesiredZoomPermille);
        }

        WorldSnapshot looked = simulation.Step(new SimInput(0, 0, LookX: 1));
        Assert.Equal(5_333, looked.WalkerYawVelocityMicroRadPerTick);

        WorldSnapshot zoomingOut = simulation.Step(
            new SimInput(0, 0, SimActions.ZoomOut));
        Assert.Equal(500, zoomingOut.ZoomPermille);
        Assert.Equal(SimulationConstants.ZoomOutPermille, zoomingOut.DesiredZoomPermille);
        for (int tick = 0; tick < 5; tick++)
        {
            zoomingOut = simulation.Step(SimInput.Idle);
        }
        Assert.Equal(SimulationConstants.ZoomOutPermille, zoomingOut.ZoomPermille);

        simulation.Step(new SimInput(0, 0, SimActions.ZoomIn));
        for (int tick = 0; tick < 5; tick++)
        {
            simulation.Step(SimInput.Idle);
        }
        Assert.Equal(SimulationConstants.ZoomInPermille, simulation.Snapshot.ZoomPermille);

        simulation.GrantFlightLegForMeasurement(Level100MissionTrigger.TargetZone2);
        WorldSnapshot morphing = simulation.Step(
            new SimInput(0, 0, SimActions.ToggleMode));
        Assert.Equal(VehicleTransition.WalkerToJet, morphing.Transition);
        Assert.Equal(SimulationConstants.ZoomOutPermille, morphing.DesiredZoomPermille);
        Assert.Equal(500, morphing.ZoomPermille);

        for (int tick = 0;
             simulation.Snapshot.Mode != VehicleMode.Jet ||
                 simulation.Snapshot.Transition != VehicleTransition.None;
             tick++)
        {
            Assert.True(tick < 100, "Walker-to-jet morph did not complete.");
            simulation.Step(SimInput.Idle);
        }

        WorldSnapshot jetZoomAttempt = simulation.Step(
            new SimInput(0, 0, SimActions.ZoomIn));
        Assert.Equal(SimulationConstants.ZoomOutPermille, jetZoomAttempt.ZoomPermille);
        Assert.Equal(
            SimulationConstants.ZoomOutPermille,
            jetZoomAttempt.DesiredZoomPermille);
    }

    [Theory]
    [InlineData(73_904, 62_272, -11_153)]
    [InlineData(73_895, 62_287, -11_161)]
    [InlineData(73_647, 62_729, -11_469)]
    public void Level100Terrain_MatchesCopiedRetailGroundSamples(
        int retailXFixed,
        int retailYFixed,
        int expectedHeightUnits)
    {
        Assert.Equal(
            expectedHeightUnits,
            Level100Terrain.Instance.SampleHeightUnitsAtFixed(retailXFixed, retailYFixed));
    }

    [Fact]
    public void Level100Terrain_ExposesReleasedWaterSelection()
    {
        Assert.Equal(
            unchecked((int)0xC10D70A4),
            BitConverter.SingleToInt32Bits(Level100Terrain.Instance.WaterLevel));
        Assert.Equal(0, Level100Terrain.Instance.WaterTexture);
        Assert.Equal(-1_160, Level100Terrain.WaterElevationMillimeters);
    }

    [Theory]
    [InlineData(36, 30, 0x420C2A31)]
    [InlineData(36, 31, 0x416C43B1)]
    [InlineData(35, 30, 0x41A9B2A7)]
    [InlineData(0, 0, 0x00000000)]
    public void Level100Terrain_ReproducesReleasedPatchComplexity(
        int tileX,
        int tileY,
        int expectedFloatBits)
    {
        Assert.Equal(
            expectedFloatBits,
            BitConverter.SingleToInt32Bits(
                Level100Terrain.Instance.GetTileComplexityScore(tileX, tileY)));
    }

    [Fact]
    public void WalkerGroundElevation_IsDeterministicCoreState()
    {
        Simulation first = CreatePlayingSimulation();
        Simulation repeat = CreatePlayingSimulation();

        Assert.Equal(211, first.Snapshot.PlayerGroundElevationMillimeters);
        // 1.333 s, stated against the rate. This was a bare 40, which at 20 Hz
        // would be half a second further down the slope.
        for (int tick = 0;
             tick < 4 * SimulationConstants.TicksPerSecond / 3;
             tick++)
        {
            WorldSnapshot firstState = first.Step(new SimInput(-1, 1));
            WorldSnapshot repeatState = repeat.Step(new SimInput(-1, 1));
            Assert.Equal(
                firstState.PlayerGroundElevationMillimeters,
                repeatState.PlayerGroundElevationMillimeters);
            Assert.Equal(StateHasher.ComputeHex(firstState), StateHasher.ComputeHex(repeatState));
        }

        // Within 92 mm of the 30 Hz pose over the same 1.333 s of held input:
        // the walker model is preserved by the migration, and this is the
        // measurement that says so rather than the argument.
        Assert.Equal(new SimVector2(-3_613, 1_011), first.Snapshot.PlayerPosition);
        Assert.Equal(30, first.Snapshot.PlayerGroundElevationMillimeters);
    }

    [Fact]
    public void PlayerBaseState_CapturesPreviousPoseOncePerSimulationTick()
    {
        Simulation simulation = CreatePlayingSimulation();
        Level100ActorId player = simulation.Snapshot.Level100Actors.Actors
            .Single(actor =>
                actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine)
            .ActorId;
        ThingActorBaseStateSnapshot before = simulation.Snapshot.Level100Actors.BaseStates
            .Single(item => item.ActorId == player)
            .State;

        WorldSnapshot moved = simulation.Step(new SimInput(0, 1));

        ThingActorBaseStateSnapshot after = moved.Level100Actors.BaseStates
            .Single(item => item.ActorId == player)
            .State;
        Assert.Equal(before.CurrentPose, after.OldPose);
        Assert.NotEqual(after.OldPose, after.CurrentPose);

        WorldSnapshot next = simulation.Step(SimInput.Idle);
        ThingActorBaseStateSnapshot nextState = next.Level100Actors.BaseStates
            .Single(item => item.ActorId == player)
            .State;
        Assert.Equal(after.CurrentPose, nextState.OldPose);
    }

    [Fact]
    public void CanonicalHashRetainsResetBaselineGroundDeltaAndExactFootPhase()
    {
        Simulation simulation = CreatePlayingSimulation();
        WorldSnapshot state = simulation.Step(new SimInput(0, 1));
        for (int tick = 0;
             state.WalkerFeet.All(foot => foot.PhaseThirds == 0) && tick < 120;
             tick++)
        {
            state = simulation.Step(new SimInput(0, 1));
        }

        Assert.Contains(state.WalkerFeet, foot => foot.PhaseThirds > 0);
        Level100ActorSnapshot player = state.Level100Actors.Actors.Single(actor =>
            actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine);
        Assert.Equal(
            state.PlayerVerticalVelocityMillimetersPerTick,
            player.Pose.LinearVelocityMillimetersPerTick.Y);

        string hash = StateHasher.ComputeHex(state);
        Assert.NotEqual(hash, StateHasher.ComputeHex(state with
        {
            PlayerGroundDeltaMillimeters = state.PlayerGroundDeltaMillimeters + 1,
        }));
        WalkerFootContactSnapshot changedFoot = state.WalkerFeet[0] with
        {
            PhaseThirds = state.WalkerFeet[0].PhaseThirds + 1,
        };
        Assert.NotEqual(hash, StateHasher.ComputeHex(state with
        {
            WalkerFeet = state.WalkerFeet
                .Select((foot, index) => index == 0 ? changedFoot : foot)
                .ToArray(),
        }));
        Assert.NotEqual(hash, StateHasher.ComputeHex(state with
        {
            InitialLevel100TutorialProgress = default,
        }));

        WorldSnapshot reset = simulation.Step(new SimInput(0, 0, SimActions.Reset));
        Assert.Equal(CompletedTutorialSlots, reset.InitialLevel100TutorialProgress);
    }

    [Fact]
    public void WalkerFeet_RepeatReleasedDiagonalStepsAndSettleOnTheLevel100Slope()
    {
        Simulation first = CreatePlayingSimulation();
        Simulation repeat = CreatePlayingSimulation();
        int[]? firstSwing = null;

        for (int tick = 0; tick < 360; tick++)
        {
            WorldSnapshot firstState = first.Step(new SimInput(0, 1));
            WorldSnapshot repeatState = repeat.Step(new SimInput(0, 1));
            Assert.Equal(StateHasher.ComputeHex(firstState), StateHasher.ComputeHex(repeatState));
            firstSwing ??= firstState.WalkerFeet.Any(foot => foot.StepPhase > 0)
                ? firstState.WalkerFeet
                    .Where(foot => foot.StepPhase > 0)
                    .Select(foot => foot.Id)
                    .ToArray()
                : null;
        }

        Assert.NotNull(firstSwing);
        Assert.Equal([0, 3], firstSwing!);
        for (int tick = 0; tick < 450; tick++)
        {
            WorldSnapshot firstState = first.Step(SimInput.Idle);
            WorldSnapshot repeatState = repeat.Step(SimInput.Idle);
            Assert.Equal(StateHasher.ComputeHex(firstState), StateHasher.ComputeHex(repeatState));
        }

        Assert.All(first.Snapshot.WalkerFeet, foot =>
        {
            Assert.Equal(0, foot.StepPhase);
            Assert.Equal(0, foot.LiftMillimeters);
            Assert.Equal(
                Level100Terrain.Instance.SampleGroundElevationMillimeters(foot.Position),
                foot.GroundElevationMillimeters);
        });
        Assert.True(
            first.Snapshot.WalkerFeet.Max(foot => foot.GroundElevationMillimeters) -
            first.Snapshot.WalkerFeet.Min(foot => foot.GroundElevationMillimeters) >= 500);
    }

    [Fact]
    public void Level100FirstRun_AppliesReleasedMessagesActivationAndTriggerCommands()
    {
        var simulation = new Simulation(1, Level100TestActorDefinitions.Create());
        var attemptedInput = new SimInput(
            0,
            1,
            SimActions.Fire | SimActions.ToggleMode,
            LookX: 1);

        Assert.Equal(SimulationConstants.Level100OpeningPanTicks, simulation.Snapshot.Level100OpeningTicksRemaining);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.False(simulation.Snapshot.Level100FlightEnabled);
        Assert.False(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.Empty(simulation.Snapshot.Level100Mission.PendingEvents);
        // The greeting is NOT delivered here. CPanCamera::GetShowHUD is false
        // for the whole opening pan, and CGame::StartPlayingState only lets the
        // message box play once the pan is over
        // (Level100MissionTiming.MessageBoxAllowedTick). Delivering HUD_01 on
        // tick 0 is exactly how the reconstruction managed to show no greeting
        // at all: it was over before the HUD appeared.
        Assert.DoesNotContain(
            simulation.Snapshot.Level100MissionEvents.OfType<Level100MessageRequested>(),
            message => message.MessageId == 292562);

        var messages = simulation.Snapshot.Level100MissionEvents
            .OfType<Level100MessageRequested>()
            .Select(message => message.MessageId)
            .ToList();

        for (int tick = 1; tick <= SimulationConstants.Level100OpeningPanTicks; tick++)
        {
            WorldSnapshot state = simulation.Step(attemptedInput);
            messages.AddRange(state.Level100MissionEvents
                .OfType<Level100MessageRequested>()
                .Select(message => message.MessageId));
        }

        Assert.Equal(0, simulation.Snapshot.Level100OpeningTicksRemaining);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.Equal(SimVector2.Zero, simulation.Snapshot.PlayerPosition);
        Assert.Equal(SimulationConstants.Level100PlayerStartYawMicroRad, simulation.Snapshot.FacingYawMicroRad);
        Assert.Equal(VehicleTransition.None, simulation.Snapshot.Transition);
        Assert.Equal(SimulationConstants.MaximumEnergy, simulation.Snapshot.Energy);
        Assert.Empty(simulation.Snapshot.Projectiles);

        AdvanceUntil(
            simulation,
            state => string.Equals(
                state.Level100Mission.NavigationObjective,
                "Target Zone 1",
                StringComparison.Ordinal),
            1_500,
            state => messages.AddRange(state.Level100MissionEvents
                .OfType<Level100MessageRequested>()
                .Select(message => message.MessageId)));

        Assert.Equal(812, simulation.Snapshot.Level100Mission.Tick);

        // TUTORIAL_01 and TUTORIAL_SCANNER are both PlayCharMessage - the
        // script does not wait for them - so the objective is set before either
        // reaches the message box. They arrive at the box's own pace.
        for (int tick = 0; tick < 200; tick++)
        {
            messages.AddRange(simulation.Step(SimInput.Idle).Level100MissionEvents
                .OfType<Level100MessageRequested>()
                .Select(message => message.MessageId));
        }

        Assert.Equal(
            [292562, 293386, 296682, -1575499396, -257967449, 82987417, 4422830, 175347826],
            messages);
        Assert.True(simulation.Snapshot.Level100PlayerActive);
        Assert.True(simulation.Snapshot.Level100PlayerControlEnabled);
        Level100TriggerActorSnapshot trigger = simulation.Snapshot.Level100TriggerActors
            .Single(item => item.Trigger == Level100MissionTrigger.TargetZone1);
        Assert.True(trigger.Active);
        Assert.True(trigger.IsObjective);
        Assert.False(trigger.Reached);
    }

    [Fact]
    public void WalkerForward_AcceleratesToMeasuredCapAndCoastsAfterRelease()
    {
        Simulation simulation = CreatePlayingSimulation();

        // Every value below moved with the 20 Hz migration and none of them is
        // a behaviour change: WalkerAccelerationPerTick is 70 where it was 33
        // (a damped-input conversion, x2.126), and the cap is
        // mMaxWalkVelocity 0.15 = 150 mm/tick where it was 100 - both of which
        // are the SAME 3,000 mm/s. The measured retail sequence this pins,
        // 0 -> 0.07 -> 0.119 -> 0.15 units per RELEASED update, is now
        // reproduced tick for tick rather than through a time-equivalent.
        foreach (SimVector2 expected in new[]
                 {
                     new SimVector2(-34, 61),
                     new SimVector2(-57, 103),
                     new SimVector2(-72, 131),
                     new SimVector2(-72, 131),
                     new SimVector2(-72, 131),
                 })
        {
            WorldSnapshot state = simulation.Step(new SimInput(0, 1));
            Assert.Equal(expected, state.PlayerVelocity);
        }

        foreach (SimVector2 expected in new[]
                 {
                     new SimVector2(-50, 91),
                     new SimVector2(-35, 63),
                     new SimVector2(-24, 44),
                     new SimVector2(-16, 30),
                     new SimVector2(-11, 21),
                 })
        {
            WorldSnapshot state = simulation.Step(SimInput.Idle);
            Assert.Equal(expected, state.PlayerVelocity);
        }
    }

    [Fact]
    public void WalkerStrafe_UsesTheSameMeasuredResponseAsForward()
    {
        Simulation simulation = CreatePlayingSimulation();

        foreach (SimVector2 expected in new[]
                 {
                     new SimVector2(61, 34),
                     new SimVector2(103, 57),
                     new SimVector2(131, 72),
                     new SimVector2(131, 72),
                     new SimVector2(131, 72),
                 })
        {
            WorldSnapshot state = simulation.Step(new SimInput(1, 0));
            Assert.Equal(expected, state.PlayerVelocity);
        }
    }

    [Fact]
    public void WalkerOppositeFlick_TriggersRetailDashAndLocksInputForItsLifecycle()
    {
        Simulation simulation = CreatePlayingSimulation();

        WorldSnapshot backward = simulation.Step(new SimInput(0, -1));
        Assert.Equal(new SimVector2(34, -61), backward.PlayerVelocity);

        WorldSnapshot triggered = simulation.Step(new SimInput(0, 1));
        Assert.Equal(new SimVector2(-831, 1_485), triggered.PlayerVelocity);
        Assert.Equal(14, triggered.WalkerDashTicksRemaining);
        Assert.Single(
            triggered.AquilaFlightEventLog,
            item => item.Kind == AquilaFlightEvents.WalkerDashRequested);

        simulation.GrantFlightLegForMeasurement(Level100MissionTrigger.TargetZone2);
        WorldSnapshot morphRejected = simulation.Step(
            new SimInput(0, 0, SimActions.ToggleMode));
        Assert.Equal(VehicleTransition.None, morphRejected.Transition);
        Assert.Equal(13, morphRejected.WalkerDashTicksRemaining);
        Assert.Contains(
            morphRejected.AquilaFlightEventLog,
            item => item.Kind == AquilaFlightEvents.TransformRejected);

        for (int remaining = 12; remaining >= 0; remaining--)
        {
            WorldSnapshot locked = simulation.Step(new SimInput(0, -1));
            Assert.Equal(remaining, locked.WalkerDashTicksRemaining);
            Assert.True(locked.PlayerVelocity.X < 0);
            Assert.True(locked.PlayerVelocity.Z > 0);
        }

        WorldSnapshot released = simulation.Step(new SimInput(0, -1));
        Assert.Equal(-1_000, released.WalkerLastMoveZPermille);
        Assert.Equal(released.Tick, released.WalkerLastHardBackwardTick);

        // The retail lateral pair is asymmetric: left assigns +0.08 roll
        // velocity, while right subtracts 0.08 from whatever residual remains.
        var lateral = CreatePlayingSimulation();
        lateral.Step(new SimInput(1, 0));
        WorldSnapshot leftDash = lateral.Step(new SimInput(-1, 0));
        Assert.Equal(
            SimulationConstants.WalkerDashRollVelocityMicroRadPerTick,
            leftDash.RollVelocityMicroRadPerTick);
        Assert.Single(
            leftDash.AquilaFlightEventLog,
            item => item.Kind == AquilaFlightEvents.WalkerDashRequested);
        while (lateral.Snapshot.WalkerDashTicksRemaining > 0)
        {
            lateral.Step(SimInput.Idle);
        }
        lateral.Step(SimInput.Idle);
        WorldSnapshot hardLeft = lateral.Step(new SimInput(-1, 0));
        int expectedRightRoll =
            (int)((long)hardLeft.RollVelocityMicroRadPerTick *
                SimulationConstants.WalkerYawRetentionNumerator /
                SimulationConstants.WalkerYawRetentionDenominator) -
            SimulationConstants.WalkerDashRollVelocityMicroRadPerTick;
        WorldSnapshot rightDash = lateral.Step(new SimInput(1, 0));
        Assert.Equal(14, rightDash.WalkerDashTicksRemaining);
        Assert.Equal(expectedRightRoll, rightDash.RollVelocityMicroRadPerTick);
        Assert.Single(
            rightDash.AquilaFlightEventLog,
            item => item.Kind == AquilaFlightEvents.WalkerDashRequested);
    }

    [Fact]
    public void WalkerLook_AcceleratesBodyYawAndCoastsAfterRelease()
    {
        Simulation simulation = CreatePlayingSimulation();

        foreach (int expected in
                 new[] { 13_333, 23_999, 32_532, 39_358, 44_819 })
        {
            WorldSnapshot state = simulation.Step(new SimInput(0, 0, LookX: 1));
            Assert.Equal(expected, state.WalkerYawVelocityMicroRadPerTick);
        }

        WorldSnapshot coast = simulation.Step(SimInput.Idle);
        Assert.Equal(35_855, coast.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(699_726, coast.FacingYawMicroRad);
    }

    /// <summary>
    /// The jet's ground-effect lookahead is HALF A SECOND of travel, not half a
    /// tick.
    ///
    /// <para><c>BattleEngineJetPart.cpp:548</c> is
    /// <c>pos = mMainPart-&gt;mPos + (mMainPart-&gt;mVelocity * GAME_FR * 0.5f)</c>.
    /// <c>GAME_FR</c> is <c>20.0f</c> (<c>thing.h:28</c>) and <c>mVelocity</c> is
    /// per released UPDATE - <c>actor.cpp</c> bounds it with
    /// <c>GetMaxVelocity()/GAME_FR</c>, which only type-checks as a per-update
    /// quantity. So <c>mVelocity * GAME_FR</c> is units per second and the
    /// <c>0.5f</c> makes the sample point half a second ahead.</para>
    ///
    /// <para>This asserts the LAW as a ratio rather than pinning a distance,
    /// because the distance is velocity-dependent and a pinned number would have
    /// to be re-derived every time the flight model moves. Core read
    /// <c>velocity / 2</c> and was 30x too near; the ratio is what was wrong and
    /// the ratio is what is guarded.</para>
    /// </summary>
    [Fact]
    public void JetGroundEffectLookahead_IsHalfASecondOfTravel_NotHalfATick()
    {
        // The released law, stated independently of our constant so that
        // changing the constant cannot make this test agree with itself.
        const double ReleasedSeconds = 0.5;
        int expectedTicks = (int)(ReleasedSeconds * SimulationConstants.TicksPerSecond);

        Assert.Equal(SimulationConstants.JetGroundEffectLookaheadTicks, expectedTicks);

        // And the thing that actually went wrong: it must be a multiplier on
        // velocity, not a divisor. `velocity / 2` satisfies no positive tick
        // count, so this would have failed on the old code for the right reason.
        Assert.True(
            SimulationConstants.JetGroundEffectLookaheadTicks > 1,
            "a lookahead of one tick or less is the defect this guards");

        // 30x is the measured size of the old error at the documented cruise
        // speed, recorded so the magnitude is not lost if the constant moves.
        int CruiseSpeedMillimetresPerTick =
            SimulationConstants.JetMaximumSpeedPerTick;
        Assert.Equal(
            9_000,
            CruiseSpeedMillimetresPerTick * SimulationConstants.JetGroundEffectLookaheadTicks);
    }

    /// <summary>
    /// Skimming water damages the Aquila, and the amount is pinned to the
    /// released anchor rather than to our own arithmetic.
    ///
    /// <para><c>BattleEngineJetPart.cpp:536</c> is
    /// <c>float damage=(0.5f-altitude)*20.0f</c>, applied once per released
    /// 20 Hz update. At zero altitude that is 10.0 released life against the
    /// Aquila Prototype's <c>mLife</c> of 20.0 - so touching the water costs
    /// EXACTLY HALF THE HULL PER RELEASED UPDATE. That halving is the anchor:
    /// it is a property of the released numbers, independent of our tick rate,
    /// our units and our conversion, so it cannot be satisfied by a
    /// self-consistent but wrongly-scaled implementation.</para>
    ///
    /// <para>Ours applied no damage at all until 2026-07-27 - measured by flying
    /// four skim passes at ~500 mm over water with the hull sitting at full
    /// throughout.</para>
    /// </summary>
    [Fact]
    public void WaterSkimDamage_CostsHalfTheHullPerReleasedUpdate_AtZeroAltitude()
    {
        // The released law, restated here from the source rather than read from
        // our constants, so the test cannot agree with itself.
        const int ReleasedDamagePerUnitOfDepth = 20;
        const double ReleasedSkimCeilingUnits = 0.5;
        const double ReleasedAquilaLife = 20.0;

        double releasedDamageAtZeroAltitude =
            ReleasedSkimCeilingUnits * ReleasedDamagePerUnitOfDepth;
        Assert.Equal(ReleasedAquilaLife / 2.0, releasedDamageAtZeroAltitude);

        // Half the hull per released update, expressed in registry milli-life.
        // This is the anchor and it is derived from the released numbers above,
        // not from our conversion.
        int expectedPerReleasedUpdate = SimulationConstants.MaximumHull / 2;
        Assert.Equal(
            (int)(releasedDamageAtZeroAltitude * 1_000),
            expectedPerReleasedUpdate);

        // The same quantity through OUR units, in the direction the simulation
        // actually computes it. Core and retail both run at 20 Hz now, so this
        // ratio is exact; spelling it out still binds the unit-conversion law.
        long milliLifePerCoreTick = SimulationConstants.JetSkimHeightMillimeters *
            (long)SimulationConstants.JetWaterSkimDamagePerReleasedUnit *
            SimulationConstants.RetailTicksPerCoreTickNumerator /
            SimulationConstants.RetailTicksPerCoreTickDenominator;
        long expectedPerCoreTick =
            (long)expectedPerReleasedUpdate *
            SimulationConstants.RetailTicksPerCoreTickNumerator /
            SimulationConstants.RetailTicksPerCoreTickDenominator;

        Assert.Equal(expectedPerCoreTick, milliLifePerCoreTick);

        // Retail starts death strictly below zero. Two 10.0 released updates
        // therefore leave exact-zero life alive and the third kills. Core now
        // runs at retail's 20 Hz rate, so those are also three Core ticks and
        // 0.15 seconds—not a ceil-to-zero shortcut.
        int releasedUpdatesToDeath =
            ((int)ReleasedAquilaLife / (int)releasedDamageAtZeroAltitude) + 1;
        int coreTicksToDeath =
            (SimulationConstants.MaximumHull / (int)expectedPerCoreTick) + 1;
        Assert.Equal(3, releasedUpdatesToDeath);
        Assert.Equal(3, coreTicksToDeath);
    }

    [Fact]
    public void TerrainPitch_IsNegatedAgainstForwardRise_AndRollIsNot()
    {
        // Guards the sign defect directly, rather than inferring it from an
        // endpoint. Both released producers compute
        //     p = (yv x map_normal) x map_normal;  pitch = -p.Z
        // (BattleEngine.cpp:1143, BattleEngineJetPart.cpp:597). Because
        // (a x n) x n = n(a.n) - a, p is anti-parallel to facing, so retail's
        // pitch is NEGATIVE when the ground rises ahead. Roll uses the SINGLE
        // cross r = yv x map_normal and is NOT negated.
        //
        // Ground rising ahead must produce nose-up (negative) pitch; falling
        // away must produce nose-down (positive); flat must produce zero.
        (SimVector2 position, int yaw, int forwardSlopePermille) = FindSlopedSample();
        Assert.NotEqual(0, forwardSlopePermille);

        int pitch = Simulation.SampleTerrainPitchMicroRad(position, yaw);
        Assert.NotEqual(0, pitch);
        Assert.Equal(-Math.Sign(forwardSlopePermille), Math.Sign(pitch));

        // Reversing the facing reverses the forward slope, so the pitch sign
        // must flip too. This catches a constant offset masquerading as a sign.
        int reversedYaw = yaw + 3_141_593;
        int reversedPitch = Simulation.SampleTerrainPitchMicroRad(position, reversedYaw);
        Assert.Equal(-Math.Sign(pitch), Math.Sign(reversedPitch));

        // Roll must keep the SAME sign as the rightward slope - negating it
        // alongside pitch would be a half-applied fix and worse than none.
        // At yaw 0 the rightward slope reduces to gradient.X exactly, so no
        // trig helper is needed and the assertion stays exact.
        SimVector2 gradient =
            Level100Terrain.Instance.SampleGroundGradientPermille(position);
        int rightSlopePermille = gradient.X;
        if (rightSlopePermille != 0)
        {
            int roll = Simulation.SampleTerrainRollMicroRad(position, yaw);
            Assert.Equal(Math.Sign(rightSlopePermille), Math.Sign(roll));
        }
    }

    private static (SimVector2 Position, int Yaw, int ForwardSlopePermille)
        FindSlopedSample()
    {
        // Walk the authored Level 100 heightfield for a sample with a clearly
        // non-zero forward slope at yaw 0, so the assertion is not riding on
        // rounding noise.
        for (int z = -40_000; z <= 40_000; z += 1_000)
        {
            for (int x = -40_000; x <= 40_000; x += 1_000)
            {
                var position = new SimVector2(x, z);
                SimVector2 gradient =
                    Level100Terrain.Instance.SampleGroundGradientPermille(position);
                if (Math.Abs(gradient.Z) >= 200)
                {
                    return (position, 0, gradient.Z);
                }
            }
        }

        throw new InvalidOperationException(
            "no sufficiently sloped Level 100 sample found");
    }

    [Fact]
    public void WalkerVerticalLook_UsesMeasuredInertiaAndReleasedTerrainRelativeLimits()
    {
        Assert.Equal(
            -1_091_250,
            SimulationConstants.ObservedWalkerPitchUpLimitAtLevel100StartMicroRad);
        Assert.Equal(
            532_123,
            SimulationConstants.ObservedWalkerPitchDownLimitAtLevel100StartMicroRad);

        Simulation simulation = CreatePlayingSimulation();

        (int Velocity, int Pitch)[] expected =
        [
            (-8_547, -8_547),
            (-15_384, -23_931),
            (-20_854, -44_785),
            (-25_230, -70_015),
            (-28_731, -98_746),
        ];
        foreach ((int velocity, int pitch) in expected)
        {
            WorldSnapshot state = simulation.Step(new SimInput(0, 0, LookY: -1));
            Assert.Equal(velocity, state.WalkerPitchVelocityMicroRadPerTick);
            Assert.Equal(pitch, state.FacingPitchMicroRad);
        }

        WorldSnapshot coast = simulation.Step(SimInput.Idle);
        Assert.Equal(-22_984, coast.WalkerPitchVelocityMicroRadPerTick);
        Assert.Equal(-121_730, coast.FacingPitchMicroRad);

        for (int tick = 0; tick < 100; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookY: -1));
        }
        // TERRAIN-RELATIVE, derived from released constants - not a window
        // fitted around our own output. BattleEngine.cpp:1145-1176 damps with a
        // 6.0 coefficient from a -0.8 threshold, so the soft limiter's
        // equilibrium is delta = -800_000 - 1_000_000/6 = -966_667. Held input
        // converges toward that bound without passing it. Asserting the DELTA
        // rather than the absolute pitch makes this immune to the separate
        // terrain-gradient shortfall below, and it fails loudly if the limiter
        // itself regresses.
        int upDelta = simulation.Snapshot.FacingPitchMicroRad -
            Simulation.SampleTerrainPitchMicroRad(
                simulation.Snapshot.PlayerPosition,
                simulation.Snapshot.FacingYawMicroRad);
        Assert.InRange(upDelta, -966_667, -900_000);
        Assert.True(simulation.Snapshot.WalkerPitchVelocityMicroRadPerTick <= 0);

        for (int tick = 0; tick < 200; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookY: 1));
        }
        // Same treatment, opposite bound: 500_000 + 1_000_000/6 = 666_667.
        int downDelta = simulation.Snapshot.FacingPitchMicroRad -
            Simulation.SampleTerrainPitchMicroRad(
                simulation.Snapshot.PlayerPosition,
                simulation.Snapshot.FacingYawMicroRad);
        Assert.InRange(downDelta, 600_000, 666_667);

        // PARITY, with a NAMED tolerance rather than a silent one. The two
        // Observed* constants above were previously only ever asserted against
        // their own literals - a tautology that let the file look like it
        // checked retail parity while checking nothing. 60_000 uRad is not a
        // target, it is the CURRENT known shortfall: inverting the limiter
        // equilibrium through both released endpoints brackets retail's ground
        // pitch at the Level 100 start to [-134_544, -124_583], while ours
        // brackets to [-83_663, -69_722]. Disjoint, both negative - the sign is
        // right and the magnitude is not. Our sampled forward slope is roughly
        // 59% of retail's, most likely because SampleGroundGradientPermille
        // central-differences over +/-1000 mm and smooths the slope relative to
        // whatever MAP.Normal does. Tightening that sampler MUST tighten this
        // tolerance; do not widen it to accommodate a regression.
        Assert.InRange(
            Math.Abs(simulation.Snapshot.FacingPitchMicroRad -
                SimulationConstants.ObservedWalkerPitchDownLimitAtLevel100StartMicroRad),
            0,
            60_000);
        Assert.True(simulation.Snapshot.WalkerPitchVelocityMicroRadPerTick >= 0);
    }

    [Fact]
    public void WalkerMovementUsesContinuousBodyYawWithoutResettingLookYaw()
    {
        Simulation simulation = CreatePlayingSimulation();
        // 0.667 s of held look, stated against the rate.
        for (int tick = 0;
             tick < 2 * SimulationConstants.TicksPerSecond / 3;
             tick++)
        {
            simulation.Step(new SimInput(0, 0, LookX: 1));
        }

        WorldSnapshot state = simulation.Step(new SimInput(0, 1));
        Assert.Equal(1, state.FacingX);
        Assert.Equal(1, state.FacingZ);
        // The shipped Aquila record's 1.0 GroundTurnRate leaves the same
        // continuous inertial yaw owner in place; only the superseded fitted
        // 1.7 gain changed.
        Assert.Equal(1_174_857, state.FacingYawMicroRad);
        Assert.Equal(new SimVector2(-65, 27), state.PlayerVelocity);
    }

    [Fact]
    public void SnapshotPlayerOwners_AgreeAfterMovementDamageActivationDeathAndReset()
    {
        Simulation simulation = CreatePlayingSimulation();

        WorldSnapshot state = simulation.Step(
            new SimInput(1, 1, SimActions.ToggleMode, LookX: 1),
            [new Level100PlayerDamageFact(200)]);

        AssertCanonicalPlayer(state);
        Assert.Equal(VehicleTransition.None, state.Transition);

        state = simulation.Step(
            SimInput.Idle,
            [new Level100ActorActivationFact(
                state.Level100Actors.Actors.Single(actor =>
                    actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine).ActorId,
                false)]);
        AssertCanonicalPlayer(state);
        Assert.False(state.Level100PlayerActive);

        Level100ActorId playerId = state.Level100Actors.Actors.Single(actor =>
            actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine).ActorId;
        state = simulation.Step(
            SimInput.Idle,
            [new Level100ActorActivationFact(playerId, true),
             new Level100PlayerDamageFact(
                 SimulationConstants.MaximumHull +
                 SimulationConstants.MaximumShield + 1)]);
        AssertCanonicalPlayer(state);
        Assert.Equal(0, state.Hull);
        Assert.Equal(Level100ActorLifecycle.Destroyed, state.Level100Actors.Actors.Single(
            actor => actor.ActorId == playerId).Lifecycle);

        state = simulation.Step(new SimInput(0, 0, SimActions.Reset));
        AssertCanonicalPlayer(state);
        Assert.Equal(SimulationConstants.MaximumHull, state.Hull);
        Assert.Equal(Level100ActorLifecycle.Alive, state.Level100Actors.Actors.Single(
            actor => actor.ActorId == playerId).Lifecycle);
    }

    [Fact]
    public void SegmentedActorRejectsExternalHealthBeforeMutatingTheTick()
    {
        Simulation simulation = CreatePlayingSimulation();
        WorldSnapshot before = simulation.Snapshot;
        Level100ActorId targetId = before.Level100Actors.Actors.First(actor =>
            actor.DefinitionName == "Target Tank").ActorId;

        Assert.Throws<InvalidOperationException>(() => simulation.Step(
            SimInput.Idle,
            [new Level100ActorHealthFact(targetId, 1)]));

        Assert.Equal(before.Tick, simulation.Snapshot.Tick);
        Assert.Equal(
            StateHasher.ComputeHex(before),
            StateHasher.ComputeHex(simulation.Snapshot));
    }

    [Fact]
    public void SegmentedActorRejectsExternalDyingFactsBeforeMutatingTheTick()
    {
        foreach (bool died in new[] { false, true })
        {
            Simulation simulation = CreatePlayingSimulation();
            WorldSnapshot before = simulation.Snapshot;
            Level100ActorId targetId = before.Level100Actors.Actors.First(actor =>
                actor.DefinitionName == "Target Tank").ActorId;
            Level100SimulationFact fact = died
                ? new Level100ActorDiedFact(targetId)
                : new Level100ActorStartedDyingFact(targetId);

            Assert.Throws<InvalidOperationException>(() => simulation.Step(
                SimInput.Idle,
                [fact]));

            Assert.Equal(before.Tick, simulation.Snapshot.Tick);
            Assert.Equal(
                StateHasher.ComputeHex(before),
                StateHasher.ComputeHex(simulation.Snapshot));
        }
    }

    private static void AssertCanonicalPlayer(WorldSnapshot state)
    {
        Level100ActorSnapshot player = state.Level100Actors.Actors.Single(actor =>
            actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine);
        Assert.Equal(state.PlayerPosition.X, player.Pose.PositionMillimeters.X);
        Assert.Equal(state.PlayerElevationMillimeters, player.Pose.PositionMillimeters.Y);
        Assert.Equal(state.PlayerPosition.Z, player.Pose.PositionMillimeters.Z);
        Assert.Equal(state.PlayerVelocity.X, player.Pose.LinearVelocityMillimetersPerTick.X);
        Assert.Equal(
            state.PlayerVerticalVelocityMillimetersPerTick,
            player.Pose.LinearVelocityMillimetersPerTick.Y);
        Assert.Equal(state.PlayerVelocity.Z, player.Pose.LinearVelocityMillimetersPerTick.Z);
        Assert.Equal(state.Hull, player.Health);
        Assert.Equal(state.Level100PlayerActive, player.Active);
        Assert.Equal(state.Mode == VehicleMode.Jet, state.Level100ActorScripts.PlayerInJetMode);
    }

    [Fact]
    public void LookAxes_OutsideUnitRange_AreRejected()
    {
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookX: 2).Validate);
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookY: -2).Validate);
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookXAnalogPermille: 1_001).Validate);
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookYAnalogPermille: -1_001).Validate);
    }

    [Fact]
    public void WalkerAnalogLook_FollowsTheReleasedCurveAndUsesTheSameRetailCoast()
    {
        // This test asserted PROPORTIONALITY until 2026-07-27 — half input,
        // half rate. That was the defect, not the specification.
        // Player.cpp:334-355 curves every look axis through
        // tan(1.2*val)/tan(1.2) before it reaches the battle engine, so half
        // deflection commands about 27% of full rate. Full deflection is
        // unchanged, which is why nothing else caught this.
        Simulation half = CreatePlayingSimulation();
        Simulation full = CreatePlayingSimulation();

        WorldSnapshot halfInput = half.Step(new SimInput(0, 0, LookXAnalogPermille: 500));
        WorldSnapshot fullInput = full.Step(new SimInput(0, 0, LookXAnalogPermille: 1_000));

        Assert.Equal(13_333, fullInput.WalkerYawVelocityMicroRadPerTick);

        // Asserted as the law rather than as a golden number: whatever full
        // deflection commands, half deflection commands the curve's fraction
        // of it, to within the integer rounding of one scaling step.
        int expectedHalf =
            fullInput.WalkerYawVelocityMicroRadPerTick * LookAxisResponse.Apply(500) / 1_000;
        Assert.InRange(
            halfInput.WalkerYawVelocityMicroRadPerTick, expectedHalf - 1, expectedHalf + 1);

        // And the compression is real, not a rounding artefact: half input
        // turns the walker through well under half the angle.
        long halfTurn =
            halfInput.FacingYawMicroRad - SimulationConstants.Level100PlayerStartYawMicroRad;
        long fullTurn =
            fullInput.FacingYawMicroRad - SimulationConstants.Level100PlayerStartYawMicroRad;
        Assert.True(halfTurn * 3 < fullTurn, $"half turned {halfTurn} against full {fullTurn}");

        WorldSnapshot coast = half.Step(SimInput.Idle);
        Assert.Equal(
            RetainedYawFor(halfInput.WalkerYawVelocityMicroRadPerTick),
            coast.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(
            halfInput.FacingYawMicroRad + coast.WalkerYawVelocityMicroRadPerTick,
            coast.FacingYawMicroRad);
    }

    private static int RetainedYawFor(int velocity) =>
        (int)((long)velocity * SimulationConstants.WalkerYawRetentionNumerator /
            SimulationConstants.WalkerYawRetentionDenominator);

    [Fact]
    public void LookX_OneTick_DoesNotYetLeaveForwardFacing()
    {
        Simulation simulation = CreatePlayingSimulation();
        WorldSnapshot state = simulation.Step(new SimInput(0, 0, LookX: 1));
        Assert.Equal(0, state.FacingX);
        Assert.Equal(1, state.FacingZ);
        Assert.Equal(523_163, state.FacingYawMicroRad);
    }

    [Fact]
    public void LookX_Negative_TurnsLeftFromTheAuthoredStartYaw()
    {
        Simulation simulation = CreatePlayingSimulation();
        // 0.667 s of held look, stated against the rate. Held for 20 ticks at
        // 20 Hz the walker turns half again as far and leaves this sector.
        for (int tick = 0;
             tick < 2 * SimulationConstants.TicksPerSecond / 3;
             tick++)
        {
            simulation.Step(new SimInput(0, 0, LookX: -1));
        }

        WorldSnapshot state = simulation.Snapshot;
        Assert.Equal(-1, state.FacingX);
        Assert.Equal(1, state.FacingZ);
    }

    [Fact]
    public void JetEnergyDrain_UsesTheAquilaPrototypeThrottleCurve()
    {
        // Level 100's RLWD declares "Aquila Prototype". Its record in
        // data/battle engine configurations.dat carries mEnergy 8.0,
        // mMinAirEnergyCost 0.005 and mMaxAirEnergyCost 0.012, spent once per
        // RETAIL tick. Stored in micro-retail energy so half throttle
        // interpolates exactly (0.0085) and so the values are unchanged by a
        // Core tick-rate move.
        Assert.Equal(8_000, SimulationConstants.MaximumEnergy);
        Assert.Equal(
            SimulationConstants.MaximumEnergy,
            SimulationConstants.MaximumShield);
        Assert.Equal(
            5_000,
            SimulationConstants.JetMinimumEnergyDrainMicroPerRetailTick);
        Assert.Equal(
            12_000,
            SimulationConstants.JetMaximumEnergyDrainMicroPerRetailTick);
        Assert.Equal(20, SimulationConstants.RetailTicksPerSecond);
        Assert.Equal(10, SimulationConstants.JetStrafeAccelerationNumerator);
        Assert.Equal(3, SimulationConstants.JetStrafeAccelerationDenominator);
    }

    [Fact]
    public void CanonicalFlightGate_RejectsTransformUntilReleasedMissionEnablesIt()
    {
        Simulation simulation = CreatePlayingSimulation();

        WorldSnapshot rejected = simulation.Step(
            new SimInput(0, 0, SimActions.ToggleMode));

        Assert.False(rejected.Level100FlightEnabled);
        Assert.Equal(VehicleMode.Walker, rejected.Mode);
        Assert.Equal(VehicleTransition.None, rejected.Transition);
        Assert.Contains(
            rejected.AquilaFlightEventLog,
            item => item.Kind == AquilaFlightEvents.TransformRejected);
        Assert.Equal(
            rejected.PlayerGroundElevationMillimeters +
                Level100Terrain.WalkerCenterOfGravityMillimeters,
            rejected.PlayerElevationMillimeters);
        Level100ActorSnapshot player = rejected.Level100Actors.Actors.Single(actor =>
            actor.Name == "Player 1");
        Assert.Equal(
            rejected.PlayerElevationMillimeters,
            player.Pose!.PositionMillimeters.Y);
    }

    [Fact]
    public void Reset_DominatesOtherActionsInTheSameInputSlot()
    {
        Simulation simulation = CreatePlayingSimulation();
        simulation.Step(new SimInput(1, 0, SimActions.Fire));

        WorldSnapshot reset = simulation.Step(new SimInput(
            1,
            1,
            SimActions.Reset | SimActions.Fire | SimActions.ToggleMode));

        Assert.Equal(SimulationConstants.Level100OpeningPanTicks + 2, reset.Tick);
        Assert.Equal(VehicleMode.Walker, reset.Mode);
        Assert.Equal(SimVector2.Zero, reset.PlayerPosition);
        Assert.Equal(SimulationConstants.MaximumEnergy, reset.Energy);
        Assert.Equal(SimulationConstants.MaximumShield, reset.Shield);
        Assert.Empty(reset.Projectiles);
    }

    [Fact]
    public void Movement_IsNotClampedByTheRetiredSyntheticArena()
    {
        Simulation simulation = CreatePlayingSimulation();

        for (int tick = 0; tick < 500; tick++)
        {
            simulation.Step(new SimInput(1, 1));
        }

        long distanceSquared =
            ((long)simulation.Snapshot.PlayerPosition.X * simulation.Snapshot.PlayerPosition.X) +
            ((long)simulation.Snapshot.PlayerPosition.Z * simulation.Snapshot.PlayerPosition.Z);
        Assert.True(distanceSquared > 30_000L * 30_000L);
        Assert.NotEqual(SimVector2.Zero, simulation.Snapshot.PlayerVelocity);
    }

    [Fact]
    public void Level100ObservedFacilityContacts_PreserveSlideAndPreventEntry()
    {
        Simulation towerRun = CreatePlayingSimulation();
        AimAtTargetAndSettle(towerRun, SimulationConstants.Level100ControlTowerPosition);
        bool observedTowerSlide = false;
        for (int tick = 0; tick < 260; tick++)
        {
            WorldSnapshot state = towerRun.Step(new SimInput(0, 1));
            long offsetX = (long)state.PlayerPosition.X -
                SimulationConstants.Level100ControlTowerPosition.X;
            long offsetZ = (long)state.PlayerPosition.Z -
                SimulationConstants.Level100ControlTowerPosition.Z;
            long radius = SimulationConstants.Level100ControlTowerContactRadius;
            Assert.True((offsetX * offsetX) + (offsetZ * offsetZ) >= radius * radius);
            observedTowerSlide |=
                Math.Abs(offsetX * state.PlayerVelocity.Z - offsetZ * state.PlayerVelocity.X) >
                    40_000;
        }

        Assert.True(observedTowerSlide);

        Simulation factoryRun = CreatePlayingSimulation();
        AimAtTargetAndSettle(factoryRun, SimulationConstants.Level100TankFactoryPosition);
        bool reachedFactory = false;
        bool removedFactoryInwardMotion = false;
        for (int tick = 0; tick < 360; tick++)
        {
            WorldSnapshot state = factoryRun.Step(new SimInput(0, 1));
            long offsetX = (long)state.PlayerPosition.X -
                SimulationConstants.Level100TankFactoryPosition.X;
            long offsetZ = (long)state.PlayerPosition.Z -
                SimulationConstants.Level100TankFactoryPosition.Z;
            long radius = SimulationConstants.Level100TankFactoryContactRadius;
            long distanceSquared = (offsetX * offsetX) + (offsetZ * offsetZ);
            Assert.True(distanceSquared >= radius * radius);
            reachedFactory |= distanceSquared <= (radius + 2L) * (radius + 2L);
            if (distanceSquared <= (radius + 2L) * (radius + 2L))
            {
                long radialVelocity =
                    (offsetX * state.PlayerVelocity.X) +
                    (offsetZ * state.PlayerVelocity.Z);
                removedFactoryInwardMotion |= radialVelocity >= -(radius * 2L);
            }
        }

        Assert.True(reachedFactory);
        Assert.True(removedFactoryInwardMotion);
    }

    [Fact]
    public void Level100Triggers_UsePhysicalActorsAndReleasedSideScriptDispatch()
    {
        Simulation simulation = CreatePlayingSimulation();

        AdvanceUntilNavigation(simulation, "Target Zone 1", 500);
        Assert.True(Trigger(simulation, Level100MissionTrigger.TargetZone1).Active);
        Level100ActorScriptContinuationSnapshot targetZonePause =
            DriveUntilTriggerPause(simulation, Level100MissionTrigger.TargetZone1);
        Level100TriggerActorSnapshot targetZone = Trigger(
            simulation,
            Level100MissionTrigger.TargetZone1);
        Assert.False(targetZone.Reached);
        Assert.Equal(Level100ActorScriptWaitKind.Pause, targetZonePause.WaitKind);
        Assert.Equal(
            BitConverter.SingleToInt32Bits(0.5f).ToString(
                System.Globalization.CultureInfo.InvariantCulture),
            targetZonePause.WaitArgument);
        Assert.Equal(10, targetZonePause.DueTick - simulation.Snapshot.Tick);

        // The released Pause is 0.5 s, which is ten ticks at 20 Hz.
        for (int tick = 1; tick < 10; tick++)
        {
            Assert.False(Trigger(
                simulation.Step(SimInput.Idle),
                Level100MissionTrigger.TargetZone1).Reached);
        }

        WorldSnapshot firingRangeAssignment = simulation.Step(SimInput.Idle);
        Assert.True(Trigger(firingRangeAssignment, Level100MissionTrigger.TargetZone1).Reached);
        Assert.Equal("Firing Range", firingRangeAssignment.Level100Mission.NavigationObjective);
        Assert.Contains(
            firingRangeAssignment.Level100MissionEvents.OfType<Level100MessageRequested>(),
            message => message.MessageId == 4458134);

        Level100ActorScriptContinuationSnapshot firingRangePause =
            DriveUntilTriggerPause(simulation, Level100MissionTrigger.FiringRange);
        Assert.Equal(Level100ActorScriptWaitKind.Pause, firingRangePause.WaitKind);
        Assert.Equal(10, firingRangePause.DueTick - simulation.Snapshot.Tick);
        for (int tick = 0; tick < 10; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(Trigger(simulation, Level100MissionTrigger.FiringRange).Reached);
        Assert.Equal(
            Level100PrimaryObjectiveStatus.Complete,
            simulation.Snapshot.Level100Mission.PrimaryObjectives[0].Status);
        Assert.True(simulation.Snapshot.Level100FiringRangeTargetsActive);
        Assert.False(simulation.Snapshot.Level100PulseCannonEnabled);
        for (int tick = 0; tick < SimulationConstants.TicksPerSecond; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.Single(simulation.Step(new SimInput(0, 0, SimActions.Fire)).Projectiles);
    }

    /// <summary>
    /// Retail does not launch an adjustable weapon parallel to the centre-screen
    /// ray. <c>CBattleEngine::GetLaunchPosition</c> traces from the current camera
    /// view and rotates the physical cockpit emitter toward that hit point before
    /// projectile inaccuracy is applied. The Pulse Cannon inherits
    /// <c>CWeaponAdjustAim = true</c>; its shipped record carries no override.
    /// </summary>
    [Fact]
    public void PulseCannonEmitter_ConvergesOnTheCameraReticleContact()
    {
        Simulation simulation = CreateFiringRangeExerciseSimulation();
        Level100ActorSnapshot target = simulation.Snapshot.Level100Actors.Actors
            .Single(actor => actor.Name == "Target Tank #23");
        AimReticleAtActor(simulation, target, heightAboveOriginMillimeters: 600);

        int healthBefore = target.Health;
        WorldSnapshot state = simulation.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.Single(state.Projectiles);
        for (int tick = 0; tick < 20 && state.Projectiles.Count > 0; tick++)
        {
            state = simulation.Step(SimInput.Idle);
        }

        Level100ActorSnapshot after = state.Level100Actors.Actors
            .Single(actor => actor.ActorId == target.ActorId);
        Assert.Empty(state.Projectiles);
        Assert.Equal(healthBefore - 1_800, after.Health);
        Assert.Equal(Level100ActorLifecycle.Alive, after.Lifecycle);
        Assert.Equal(Level100MissionOutcome.Running, state.Level100Mission.Outcome);
    }

    [Theory]
    [InlineData(-300)]
    [InlineData(3_000)]
    public void PulseCannonEmitter_DoesNotSnapMissesOutsideTheContactVolume(
        int heightAboveOriginMillimeters)
    {
        Simulation simulation = CreateFiringRangeExerciseSimulation();
        Level100ActorSnapshot target = simulation.Snapshot.Level100Actors.Actors
            .Single(actor => actor.Name == "Target Tank #23");
        AimReticleAtActor(
            simulation,
            target,
            heightAboveOriginMillimeters);

        WorldSnapshot state = simulation.Step(new SimInput(0, 0, SimActions.Fire));
        for (int tick = 0; tick < 120 && state.Projectiles.Count > 0; tick++)
        {
            state = simulation.Step(SimInput.Idle);
        }

        Level100ActorSnapshot after = state.Level100Actors.Actors
            .Single(actor => actor.ActorId == target.ActorId);
        Assert.Empty(state.Projectiles);
        Assert.Equal(target.Health, after.Health);
        Assert.Equal(Level100ActorLifecycle.Alive, after.Lifecycle);
        Assert.Equal(Level100MissionOutcome.Running, state.Level100Mission.Outcome);
    }

    [Fact]
    public void Level100SimulationFailureTape_FirstRunRetainsLossTextAndExactTicks()
    {
        DeterministicSimulationTape first = RunLevel100FailureTape();
        DeterministicSimulationTape repeat = RunLevel100FailureTape();

        Assert.Equal(first.Hashes, repeat.Hashes);
        Assert.Equal(Level100MissionOutcome.Lost, first.Snapshot.Level100Mission.Outcome);
        Assert.Equal(Level100MissionFailureReason.TutorialBroken,
            first.Snapshot.Level100Mission.FailureReason);
        Assert.Equal(1_110_345_999, first.Snapshot.Level100Mission.FailureTextId);
        Assert.Equal(
            Level100MissionTerminalState.FailureCountdownElapsed,
            first.Snapshot.Level100Mission.TerminalState);
        Assert.Equal(0, first.Snapshot.Level100Mission.TerminalTicksRemaining);

        Simulation death = CreatePlayingSimulation();
        WorldSnapshot declared = death.Step(
            SimInput.Idle,
            [new Level100PlayerDeathFact()]);
        Assert.Equal(Level100MissionFailureReason.PlayerDeath,
            declared.Level100Mission.FailureReason);
        Assert.Equal(
            Level100MissionTiming.DeathPauseDelayTicks,
            declared.Level100Mission.TerminalTicksRemaining);
        Assert.Equal(0x3f800000, MixBits(declared));

        int actorScriptTickAtDeclaration = declared.Level100ActorScripts.Tick;
        WorldSnapshot advancing = declared;
        for (int elapsed = 1;
             elapsed < Level100MissionTiming.DeathPauseDelayTicks;
             elapsed++)
        {
            advancing = death.Step(SimInput.Idle);
            Assert.Equal(
                actorScriptTickAtDeclaration + elapsed,
                advancing.Level100ActorScripts.Tick);
            if (elapsed == 1)
            {
                Assert.Equal(0x3f7f3b64, MixBits(advancing));
            }
            if (elapsed == Level100MissionTiming.FailureMenuDelayTicks)
            {
                Assert.Equal(
                    Level100MissionTerminalState.FailureMenuReady,
                    advancing.Level100Mission.TerminalState);
            }
        }

        Assert.Equal(1, advancing.Level100Mission.TerminalTicksRemaining);
        WorldSnapshot paused = death.Step(SimInput.Idle);
        Assert.Equal(0, paused.Level100Mission.TerminalTicksRemaining);
        Assert.Equal(
            Level100MissionTerminalState.FailureCountdownElapsed,
            paused.Level100Mission.TerminalState);
        Assert.Equal(
            actorScriptTickAtDeclaration +
                Level100MissionTiming.DeathPauseDelayTicks - 1,
            paused.Level100ActorScripts.Tick);
        Assert.Equal(0x3dcccb3b, MixBits(paused));

        WorldSnapshot held = death.Step(SimInput.Idle);
        Assert.Equal(paused.Level100ActorScripts.Tick, held.Level100ActorScripts.Tick);
        Assert.Equal(0x3dcccb3b, MixBits(held));

        static int MixBits(WorldSnapshot snapshot) => BitConverter.SingleToInt32Bits(
            Level100MissionTiming.GameplayMix(
                snapshot.Level100Mission.Outcome,
                snapshot.Level100Mission.FailureReason,
                snapshot.Level100Mission.TerminalTicksRemaining));
    }

    [Fact]
    public void PlayerWeaponReloadsUseAuthoredPerModeCadence()
    {
        Simulation pulse = CreateFiringRangeExerciseSimulation();

        WorldSnapshot pulseFirst = pulse.Step(new SimInput(0, 0, SimActions.Fire));
        AssertWeaponFire(pulseFirst, Level100PlayerWeapon.PulseCannonPod, 1);
        Assert.All(
            pulseFirst.Projectiles,
            projectile => Assert.Equal(
                Level100ProjectileKind.MechPulseBoltMedium,
                projectile.Kind));
        Assert.Equal(2, pulseFirst.FireCooldownTicksRemaining);
        WorldSnapshot pulseBlocked = pulse.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.Empty(pulseBlocked.Level100WeaponFireEvents);
        Assert.Equal(1, pulseBlocked.FireCooldownTicksRemaining);
        WorldSnapshot pulseSecond = pulse.Step(new SimInput(0, 0, SimActions.Fire));
        AssertWeaponFire(pulseSecond, Level100PlayerWeapon.PulseCannonPod, 1);
        Assert.Equal(2, pulseSecond.FireCooldownTicksRemaining);

        Simulation jet = CreatePlayingSimulation();
        jet.GrantFlightLegForMeasurement(Level100MissionTrigger.TargetZone2);
        jet.Step(new SimInput(0, 0, SimActions.ToggleMode));
        for (int tick = 0;
             jet.Snapshot.Mode != VehicleMode.Jet ||
                 jet.Snapshot.Transition != VehicleTransition.None;
             tick++)
        {
            Assert.True(tick < 100, "Walker-to-jet morph did not complete.");
            jet.Step(SimInput.Idle);
        }

        WorldSnapshot jetFirst = jet.Step(new SimInput(0, 0, SimActions.Fire));
        AssertWeaponFire(
            jetFirst,
            Level100PlayerWeapon.MechVulcanCannon,
            SimulationConstants.MechVulcanVolleySize);
        Assert.All(
            jetFirst.Projectiles,
            projectile => Assert.Equal(
                Level100ProjectileKind.MechAirBullet,
                projectile.Kind));
        Assert.Equal(1, jetFirst.FireCooldownTicksRemaining);
        WorldSnapshot jetSecond = jet.Step(new SimInput(0, 0, SimActions.Fire));
        AssertWeaponFire(
            jetSecond,
            Level100PlayerWeapon.MechVulcanCannon,
            SimulationConstants.MechVulcanVolleySize);
        Assert.Equal(1, jetSecond.FireCooldownTicksRemaining);

        static void AssertWeaponFire(
            WorldSnapshot snapshot,
            Level100PlayerWeapon weapon,
            int roundCount)
        {
            Level100WeaponFireEvent fired = Assert.Single(snapshot.Level100WeaponFireEvents);
            Assert.Equal(weapon, fired.Weapon);
            Assert.Equal(roundCount, fired.RoundCount);
        }
    }

    [Fact]
    public void PlayerProjectilesConsumeReleasedScatterInRetailDrawOrder()
    {
        Simulation pulse = CreateFiringRangeExerciseSimulation();
        int pulseSeed = pulse.Snapshot.Level100ActorMechanics.ReleasedRandomSeed;
        var pulseRandom = new Level100ReleasedRandom(pulseSeed);
        (int PulseYaw, int PulsePitch) pulseOffset = NextOffsets(
            pulseRandom,
            SimulationConstants.PulseCannonInaccuracyMicroRadians);

        WorldSnapshot pulseShot = pulse.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.Equal(
            pulseRandom.Seed,
            pulseShot.Level100ActorMechanics.ReleasedRandomSeed);
        AssertDirection(
            Assert.Single(pulseShot.Projectiles),
            pulseShot.FacingYawMicroRad,
            pulseShot.FacingPitchMicroRad,
            pulseOffset);

        Simulation jet = CreatePlayingSimulation();
        jet.GrantFlightLegForMeasurement(Level100MissionTrigger.TargetZone2);
        jet.Step(new SimInput(0, 0, SimActions.ToggleMode));
        for (int tick = 0;
             jet.Snapshot.Mode != VehicleMode.Jet ||
                 jet.Snapshot.Transition != VehicleTransition.None;
             tick++)
        {
            Assert.True(tick < 100, "Walker-to-jet morph did not complete.");
            jet.Step(SimInput.Idle);
        }

        int jetSeed = jet.Snapshot.Level100ActorMechanics.ReleasedRandomSeed;
        var jetRandom = new Level100ReleasedRandom(jetSeed);
        (int Yaw, int Pitch)[] jetOffsets = Enumerable.Range(
                0,
                SimulationConstants.MechVulcanVolleySize)
            .Select(_ => NextOffsets(
                jetRandom,
                SimulationConstants.PlayerVulcanInaccuracyMicroRadians))
            .ToArray();

        WorldSnapshot jetShot = jet.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.Equal(jetRandom.Seed, jetShot.Level100ActorMechanics.ReleasedRandomSeed);
        ProjectileSnapshot[] rounds = jetShot.Projectiles.OrderBy(item => item.Id).ToArray();
        Assert.Equal(jetOffsets.Length, rounds.Length);
        for (int index = 0; index < rounds.Length; index++)
        {
            AssertDirection(
                rounds[index],
                jetShot.FacingYawMicroRad,
                jetShot.FacingPitchMicroRad,
                jetOffsets[index]);
        }
        Assert.NotEqual(rounds[0].Velocity, rounds[1].Velocity);
        Assert.NotEqual(
            rounds[0].VerticalVelocityMillimetersPerTick,
            rounds[1].VerticalVelocityMillimetersPerTick);

        static (int Yaw, int Pitch) NextOffsets(
            Level100ReleasedRandom random,
            int inaccuracyMicroRadians)
        {
            int first = random.NextSignedUnitScaled(inaccuracyMicroRadians);
            int second = random.NextSignedUnitScaled(inaccuracyMicroRadians);
            return (second, first);
        }

        static void AssertDirection(
            ProjectileSnapshot projectile,
            int facingYaw,
            int facingPitch,
            (int Yaw, int Pitch) offset)
        {
            int actualYaw = (int)Math.Round(
                Math.Atan2(-projectile.Velocity.X, projectile.Velocity.Z) * 1_000_000d,
                MidpointRounding.AwayFromZero);
            long horizontalSquared =
                ((long)projectile.Velocity.X * projectile.Velocity.X) +
                ((long)projectile.Velocity.Z * projectile.Velocity.Z);
            int actualPitch = (int)Math.Round(
                Math.Atan2(
                    -projectile.VerticalVelocityMillimetersPerTick,
                    Math.Sqrt(horizontalSquared)) * 1_000_000d,
                MidpointRounding.AwayFromZero);

            Assert.InRange(
                Normalize(actualYaw - Normalize(facingYaw + offset.Yaw)),
                -500,
                500);
            Assert.InRange(
                Normalize(actualPitch - Normalize(facingPitch + offset.Pitch)),
                -500,
                500);
        }

        static int Normalize(int angle)
        {
            const int Pi = 3_141_593;
            const int Tau = Pi * 2;
            int normalized = angle % Tau;
            if (normalized > Pi)
            {
                normalized -= Tau;
            }
            else if (normalized < -Pi)
            {
                normalized += Tau;
            }
            return normalized;
        }
    }

    [Theory]
    [InlineData(Level100ProjectileKind.MechBullet, false)]
    [InlineData(Level100ProjectileKind.MechBullet, true)]
    [InlineData(Level100ProjectileKind.MechAirBullet, false)]
    [InlineData(Level100ProjectileKind.MechAirBullet, true)]
    public void VulcanRoundsSelectTheirImpactKindThroughProductionProjectileUpdate(
        Level100ProjectileKind projectileKind,
        bool hitMesh)
    {
        var simulation = new Simulation(
            0x100u,
            Level100TestActorDefinitions.Create());
        Level100ActorSnapshot target = simulation.Snapshot.Level100Actors.Actors
            .Single(actor => actor.Name == "Target Tank 2");
        SimVector3 start;
        SimVector3 end;
        int expectedActorId;
        if (hitMesh)
        {
            SimVector3 position = target.Pose.PositionMillimeters;
            start = position with { Y = position.Y + 2_000 };
            end = position with { Y = position.Y - 1_000 };
            expectedActorId = target.ActorId.Value;
        }
        else
        {
            start = new SimVector3(0, 2_000, 0);
            end = new SimVector3(0, -2_000, 0);
            expectedActorId = 0;
        }

        simulation.QueueVulcanRoundForContactMeasurement(
            projectileKind,
            start,
            end);
        WorldSnapshot result = simulation.Step(SimInput.Idle);

        Level100DestructionEvent impact = Assert.Single(
            result.Level100DestructionEvents,
            item => item.Kind == Level100DestructionEventKind.VulcanImpact);
        Assert.Equal(Level100DestructionEventKind.VulcanImpact, impact.Kind);
        Assert.Equal(
            Level100DestructionEffectKind.VulcanImpact,
            impact.EffectKind);
        Assert.Equal(expectedActorId, impact.ActorId);
        Assert.Empty(result.Projectiles);
    }

    [Fact]
    public void PitchedPulseRound_FollowsViewPitchWithoutInventingVerticalTargetHits()
    {
        Simulation simulation = CreateFiringRangeExerciseSimulation();
        TargetSnapshot target = simulation.Snapshot.Targets.Single(item => item.Id == 1);
        AimAtTarget(simulation, target.Position);
        for (int tick = 0; tick < 100; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookY: -1));
        }

        WorldSnapshot fired = simulation.Step(new SimInput(0, 0, SimActions.Fire));
        ProjectileSnapshot projectile = Assert.Single(fired.Projectiles);
        Assert.Equal(Level100ProjectileKind.MechPulseBoltMedium, projectile.Kind);
        Assert.Equal(120, SimulationConstants.ProjectileLifetimeTicks);
        Assert.Equal(119, projectile.RemainingTicks);
        Assert.InRange(fired.FacingPitchMicroRad, -1_000_000, -800_000);
        Assert.True(projectile.VerticalVelocityMillimetersPerTick > 0);
        long speedSquared =
            ((long)projectile.Velocity.X * projectile.Velocity.X) +
            ((long)projectile.Velocity.Z * projectile.Velocity.Z) +
            ((long)projectile.VerticalVelocityMillimetersPerTick *
                projectile.VerticalVelocityMillimetersPerTick);
        Assert.InRange(speedSquared, (long)1_749 * 1_749, (long)1_751 * 1_751);
        double yaw = fired.FacingYawMicroRad / 1_000_000d;
        double pitch = fired.FacingPitchMicroRad / 1_000_000d;
        double emitterForwardPlane =
            (SimulationConstants.PulseCannonEmitterForwardMillimeters * Math.Cos(pitch)) +
            (SimulationConstants.PulseCannonEmitterUpMillimeters * Math.Sin(pitch));
        int expectedEmitterOffsetX = (int)Math.Round(
            (SimulationConstants.PulseCannonEmitterRightMillimeters * Math.Cos(yaw)) -
            (emitterForwardPlane * Math.Sin(yaw)),
            MidpointRounding.AwayFromZero);
        int expectedEmitterOffsetZ = (int)Math.Round(
            (SimulationConstants.PulseCannonEmitterRightMillimeters * Math.Sin(yaw)) +
            (emitterForwardPlane * Math.Cos(yaw)),
            MidpointRounding.AwayFromZero);
        Assert.InRange(
            (projectile.Position.X - projectile.Velocity.X) - fired.PlayerPosition.X,
            expectedEmitterOffsetX - 1,
            expectedEmitterOffsetX + 1);
        Assert.InRange(
            (projectile.Position.Z - projectile.Velocity.Z) - fired.PlayerPosition.Z,
            expectedEmitterOffsetZ - 1,
            expectedEmitterOffsetZ + 1);
        int emitterVerticalOffset = (int)Math.Round(
            (-SimulationConstants.PulseCannonEmitterForwardMillimeters *
                Math.Sin(fired.FacingPitchMicroRad / 1_000_000d)) +
            (SimulationConstants.PulseCannonEmitterUpMillimeters *
                Math.Cos(fired.FacingPitchMicroRad / 1_000_000d)),
            MidpointRounding.AwayFromZero);
        Assert.Equal(
            fired.PlayerElevationMillimeters +
                emitterVerticalOffset +
                projectile.VerticalVelocityMillimetersPerTick,
            projectile.ElevationMillimeters);

        int firstElevation = projectile.ElevationMillimeters;
        projectile = Assert.Single(simulation.Step(SimInput.Idle).Projectiles);
        Assert.Equal(118, projectile.RemainingTicks);
        Assert.Equal(
            firstElevation + projectile.VerticalVelocityMillimetersPerTick,
            projectile.ElevationMillimeters);
        for (int remaining = 117; remaining >= 1; remaining--)
        {
            projectile = Assert.Single(simulation.Step(SimInput.Idle).Projectiles);
            Assert.Equal(remaining, projectile.RemainingTicks);
        }
        Assert.Empty(simulation.Step(SimInput.Idle).Projectiles);

        Assert.Equal(
            SimulationConstants.Level100TargetTankLife,
            simulation.Snapshot.Targets.Single(item => item.Id == 1).Hull);
    }

    [Fact]
    public void Reset_RestoresDynamicStateWithoutRewindingReplayTick()
    {
        Simulation simulation = CreatePlayingSimulation(42);
        simulation.Step(new SimInput(1, 0));
        simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

        WorldSnapshot reset = simulation.Step(new SimInput(0, 0, SimActions.Reset));

        Assert.Equal(SimulationConstants.Level100OpeningPanTicks + 3, reset.Tick);
        Assert.Equal(VehicleMode.Walker, reset.Mode);
        Assert.Equal(SimVector2.Zero, reset.PlayerPosition);
        Assert.Equal(SimulationConstants.MaximumEnergy, reset.Energy);
        Assert.Equal(SimulationConstants.MaximumShield, reset.Shield);
        Assert.Equal(0, reset.TargetsDestroyed);
        Assert.Empty(reset.Projectiles);
    }

    [Fact]
    public void HoldingChargeWeapon_FillsThePulseCannonPodInTenTicks()
    {
        Simulation simulation = CreateFiringRangeExerciseSimulation();
        Assert.True(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.Equal(
            Level100MissionWeapon.PulseCannonPod,
            simulation.Snapshot.Level100WalkerSelectedWeapon);

        var charge = new SimInput(0, 0, SimActions.ChargeWeapon);
        charge.Validate();
        Assert.Equal(0x00000000u, simulation.Level100PulseCannonChargeBits);

        for (int sample = 0; sample < 10; sample++)
        {
            simulation.Step(charge);
        }

        Assert.Equal(0x42C80000u, simulation.Level100PulseCannonChargeBits);
        simulation.Step(charge);
        Assert.Equal(0x42C80000u, simulation.Level100PulseCannonChargeBits);
    }

    [Fact]
    public void FireAtFullyCharged_LaunchesMechPulseBoltLarge()
    {
        Simulation tap = CreateFiringRangeExerciseSimulation();
        WorldSnapshot tapFired = tap.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.Equal(
            Level100ProjectileKind.MechPulseBoltMedium,
            Assert.Single(tapFired.Projectiles).Kind);

        Simulation charged = CreateFiringRangeExerciseSimulation();
        var charge = new SimInput(0, 0, SimActions.ChargeWeapon);
        charge.Validate();
        for (int sample = 0; sample < 10; sample++)
        {
            charged.Step(charge);
        }

        Assert.Equal(0x42C80000u, charged.Level100PulseCannonChargeBits);
        WorldSnapshot chargedFired = charged.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.Equal(
            Level100ProjectileKind.MechPulseBoltLarge,
            Assert.Single(chargedFired.Projectiles).Kind);
    }

    [Fact]
    public void AfterPulseFire_ChargeWaitsUntilReloadStrictlyElapses()
    {
        Simulation simulation = CreateFiringRangeExerciseSimulation();
        var charge = new SimInput(0, 0, SimActions.ChargeWeapon);
        charge.Validate();

        WorldSnapshot fired = simulation.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.Equal(
            Level100PlayerWeapon.PulseCannonPod,
            Assert.Single(fired.Level100WeaponFireEvents).Weapon);
        Assert.Equal(SimulationConstants.PulseCannonReloadTicks, fired.FireCooldownTicksRemaining);
        Assert.Equal(0x00000000u, simulation.Level100PulseCannonChargeBits);

        // ReadyToCharge at 0x0050A080 is `now > weapon+0x64` (`test ah, 0x41`
        // / jz). Fire stamps +0x64 = now + CWeaponReloadTime 0.1 s, so the
        // equality tick (exactly 0.1 s / two 20 Hz updates later) is still
        // blocked. Fire itself is already allowed on that tick; Charge is not.
        simulation.Step(charge);
        Assert.Equal(0x00000000u, simulation.Level100PulseCannonChargeBits);
        Assert.Equal(1, simulation.Snapshot.FireCooldownTicksRemaining);

        simulation.Step(charge);
        Assert.Equal(0x00000000u, simulation.Level100PulseCannonChargeBits);
        Assert.Equal(0, simulation.Snapshot.FireCooldownTicksRemaining);

        simulation.Step(charge);
        Assert.Equal(0x41200000u, simulation.Level100PulseCannonChargeBits);
    }

    [Fact]
    public void SnapshotCollections_DoNotExposeMutableArrays()
    {
        Simulation simulation = CreatePlayingSimulation();
        WorldSnapshot state = simulation.Step(new SimInput(0, 0, SimActions.Fire));

        Assert.False(state.Targets.GetType().IsArray);
        Assert.False(state.Projectiles.GetType().IsArray);
        Assert.False(state.Level100MissionEvents.GetType().IsArray);
        Assert.False(state.Level100TriggerActors.GetType().IsArray);
        Assert.False(state.AquilaFlightEventLog.GetType().IsArray);

        var targets = Assert.IsAssignableFrom<IList<TargetSnapshot>>(state.Targets);
        var projectiles = Assert.IsAssignableFrom<IList<ProjectileSnapshot>>(state.Projectiles);
        var flightEvents =
            Assert.IsAssignableFrom<IList<AquilaFlightEvent>>(state.AquilaFlightEventLog);
        Assert.True(targets.IsReadOnly);
        Assert.True(projectiles.IsReadOnly);
        Assert.True(flightEvents.IsReadOnly);
        Assert.Throws<NotSupportedException>(() => targets[0] = targets[0] with { Hull = 0 });
    }

    private static void DriveIntoTrigger(
        Simulation simulation,
        Level100MissionTrigger trigger)
    {
        Level100ActorScriptContinuationSnapshot pause =
            DriveUntilTriggerPause(simulation, trigger);
        int dueTick = Assert.IsType<int>(pause.DueTick);
        while (simulation.Snapshot.Tick < dueTick)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(Trigger(simulation, trigger).Reached);
    }

    private static Level100ActorScriptContinuationSnapshot DriveUntilTriggerPause(
        Simulation simulation,
        Level100MissionTrigger trigger)
    {
        Level100TriggerActorSnapshot releasedActor = Trigger(simulation, trigger);
        Assert.True(releasedActor.Active);
        SimVector2 destination = releasedActor.Position;
        for (int tick = 0; tick < 4_000; tick++)
        {
            WorldSnapshot state = simulation.Snapshot;
            Level100ActorSnapshot actor = state.Level100Actors.Actors.Single(
                item => item.Trigger == trigger);
            Level100ActorScriptContinuationSnapshot? pause = state.Level100ActorScripts.Instances
                .Single(item => item.ActorId == actor.ActorId)
                .Continuations
                .SingleOrDefault(item => item.WaitKind == Level100ActorScriptWaitKind.Pause);
            if (pause is not null)
            {
                return pause;
            }

            long deltaX = (long)destination.X - state.PlayerPosition.X;
            long deltaZ = (long)destination.Z - state.PlayerPosition.Z;
            double yaw = state.FacingYawMicroRad / 1_000_000d;
            double localX = (deltaX * Math.Cos(yaw)) + (deltaZ * Math.Sin(yaw));
            double localZ = (-deltaX * Math.Sin(yaw)) + (deltaZ * Math.Cos(yaw));
            sbyte moveX = (sbyte)Math.Sign(localX);
            sbyte moveZ = (sbyte)Math.Sign(localZ);
            simulation.Step(new SimInput(moveX, moveZ));
        }

        Level100ActorSnapshot stalledPlayer = simulation.Snapshot.Level100Actors.Actors.Single(
            actor => actor.Name == "Player 1");
        throw new Xunit.Sdk.XunitException(
            $"Did not start released trigger actor {trigger}; " +
            $"position={simulation.Snapshot.PlayerPosition}; " +
            $"playerActive={simulation.Snapshot.Level100PlayerActive}; " +
            $"controlEnabled={simulation.Snapshot.Level100PlayerControlEnabled}; " +
            $"navigation={simulation.Snapshot.Level100Mission.NavigationObjective}; " +
            $"playerScript={stalledPlayer.ScriptName}.");
    }

    private static Simulation CreatePlayingSimulation(uint seed = 1)
    {
        var simulation = new Simulation(
            seed,
            Level100TestActorDefinitions.Create(),
            CompletedTutorialSlots);
        for (int tick = 0; tick < SimulationConstants.Level100OpeningPanTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(simulation.Snapshot.Level100PlayerControlEnabled);
        return simulation;
    }

    private static Simulation CreateFiringRangeExerciseSimulation()
    {
        Simulation simulation = CreatePlayingSimulation();
        AdvanceUntilNavigation(simulation, "Target Zone 1", 500);
        DriveIntoTrigger(simulation, Level100MissionTrigger.TargetZone1);
        AdvanceUntilNavigation(simulation, "Firing Range", 100);
        DriveIntoTrigger(simulation, Level100MissionTrigger.FiringRange);
        AdvanceUntil(simulation, state => state.Level100FiringRangeTargetsActive, 100);
        AdvanceUntil(simulation, state => state.Level100PulseCannonEnabled, 100);
        return simulation;
    }

    private static DeterministicSimulationTape RunLevel100FailureTape()
    {
        var simulation = new Simulation(
            0x100u,
            Level100TestActorDefinitions.Create());
        var hashes = new List<string> { StateHasher.ComputeHex(simulation.Snapshot) };
        WorldSnapshot snapshot = simulation.Step(
            SimInput.Idle,
            [new Level100MissionInputFact(Level100MissionInput.BrokeTutorial)]);
        hashes.Add(StateHasher.ComputeHex(snapshot));
        // "Broke Tutorial" is posted on tick 1, while HUD_01 still owns the
        // message box until tick 351. Its own two messages queue behind that
        // and behind each other at the released advance gap, so the terminal
        // call lands at tick 594 rather than 291.
        for (int tick = 0;
             tick < 800 && snapshot.Level100Mission.Outcome != Level100MissionOutcome.Lost;
             tick++)
        {
            snapshot = simulation.Step(SimInput.Idle);
            hashes.Add(StateHasher.ComputeHex(snapshot));
        }

        Assert.Equal(Level100MissionOutcome.Lost, snapshot.Level100Mission.Outcome);
        Assert.Equal(
            Level100MissionTiming.FailureCountdownTicks,
            snapshot.Level100Mission.TerminalTicksRemaining);
        int actorScriptTickAtLoss = snapshot.Level100ActorScripts.Tick;
        for (int tick = 0; tick < Level100MissionTiming.FailureCountdownTicks; tick++)
        {
            snapshot = simulation.Step(SimInput.Idle);
            hashes.Add(StateHasher.ComputeHex(snapshot));
        }
        Assert.Equal(actorScriptTickAtLoss, snapshot.Level100ActorScripts.Tick);

        return new DeterministicSimulationTape(snapshot, hashes.AsReadOnly());
    }

    private static void AdvanceUntilNavigation(
        Simulation simulation,
        string thingName,
        int maximumTicks) => AdvanceUntil(
            simulation,
            state => string.Equals(
                state.Level100Mission.NavigationObjective,
                thingName,
                StringComparison.Ordinal),
            maximumTicks);

    private static void AdvanceUntil(
        Simulation simulation,
        Func<WorldSnapshot, bool> predicate,
        int maximumTicks,
        Action<WorldSnapshot>? observe = null)
    {
        for (int tick = 0; tick < maximumTicks && !predicate(simulation.Snapshot); tick++)
        {
            WorldSnapshot state = simulation.Step(SimInput.Idle);
            observe?.Invoke(state);
        }

        Assert.True(
            predicate(simulation.Snapshot),
            $"Condition was not reached by simulation tick {simulation.Snapshot.Tick}.");
    }

    private static Level100TriggerActorSnapshot Trigger(
        Simulation simulation,
        Level100MissionTrigger trigger) => Trigger(simulation.Snapshot, trigger);

    private static Level100TriggerActorSnapshot Trigger(
        WorldSnapshot snapshot,
        Level100MissionTrigger trigger) => snapshot.Level100TriggerActors
            .Single(item => item.Trigger == trigger);

    private sealed record DeterministicSimulationTape(
        WorldSnapshot Snapshot,
        IReadOnlyList<string> Hashes);

    private static void AimAtTarget(Simulation simulation, SimVector2 target)
    {
        for (int tick = 0; tick < 300; tick++)
        {
            WorldSnapshot state = simulation.Snapshot;
            double desired = Math.Atan2(
                -(target.X - state.PlayerPosition.X),
                target.Z - state.PlayerPosition.Z);
            double error = NormalizeRadians(desired - (state.FacingYawMicroRad / 1_000_000d));
            if (Math.Abs(error) < 0.04d)
            {
                return;
            }

            simulation.Step(new SimInput(0, 0, LookX: (sbyte)Math.Sign(error)));
        }

        throw new Xunit.Sdk.XunitException("Could not aim the deterministic Core at the requested target.");
    }

    private static void AimAtTargetAndSettle(Simulation simulation, SimVector2 target)
    {
        for (int tick = 0; tick < 1_200; tick++)
        {
            WorldSnapshot state = simulation.Snapshot;
            double desired = Math.Atan2(
                -(target.X - state.PlayerPosition.X),
                target.Z - state.PlayerPosition.Z);
            double error = NormalizeRadians(desired - (state.FacingYawMicroRad / 1_000_000d));
            if (Math.Abs(error) < 0.035d &&
                Math.Abs(state.WalkerYawVelocityMicroRadPerTick) <
                    SimulationConstants.WalkerYawInputMicroRadPerTick * 2 / 3)
            {
                return;
            }

            double demand = error -
                ((state.WalkerYawVelocityMicroRadPerTick / 1_000_000d) * 5d);
            sbyte look = (sbyte)Math.Sign(demand);
            simulation.Step(new SimInput(0, 0, LookX: look));
        }

        WorldSnapshot final = simulation.Snapshot;
        double finalDesired = Math.Atan2(
            -(target.X - final.PlayerPosition.X),
            target.Z - final.PlayerPosition.Z);
        double finalError = NormalizeRadians(
            finalDesired - (final.FacingYawMicroRad / 1_000_000d));
        throw new Xunit.Sdk.XunitException(
            $"Could not settle the deterministic walker heading: error={finalError:F6}, " +
            $"velocity={final.WalkerYawVelocityMicroRadPerTick}.");
    }

    private static void AimReticleAtActor(
        Simulation simulation,
        Level100ActorSnapshot target,
        int heightAboveOriginMillimeters)
    {
        SimVector3 position = target.Pose.PositionMillimeters;
        for (int tick = 0; tick < 1_200; tick++)
        {
            WorldSnapshot state = simulation.Snapshot;
            double deltaX = (double)position.X - state.PlayerPosition.X;
            double deltaZ = (double)position.Z - state.PlayerPosition.Z;
            double horizontal = Math.Sqrt((deltaX * deltaX) + (deltaZ * deltaZ));
            double yawError = NormalizeRadians(
                Math.Atan2(-deltaX, deltaZ) -
                (state.FacingYawMicroRad / 1_000_000d));
            double pitchError =
                -Math.Atan2(
                    position.Y + heightAboveOriginMillimeters -
                        state.PlayerElevationMillimeters,
                    Math.Max(1.0, horizontal)) -
                (state.FacingPitchMicroRad / 1_000_000d);
            if (Math.Abs(yawError) < 0.002d &&
                Math.Abs(pitchError) < 0.002d &&
                Math.Abs(state.WalkerYawVelocityMicroRadPerTick) < 500 &&
                Math.Abs(state.WalkerPitchVelocityMicroRadPerTick) < 500)
            {
                return;
            }

            double yawDemand = yawError -
                ((state.WalkerYawVelocityMicroRadPerTick / 1_000_000d) * 5d);
            double pitchDemand = pitchError -
                ((state.WalkerPitchVelocityMicroRadPerTick / 1_000_000d) * 5d);
            int yawResponsePermille = (int)(
                yawDemand * 45_334d * 1_000d /
                SimulationConstants.WalkerYawInputMicroRadPerTick);
            int pitchResponsePermille = (int)(pitchDemand * 4_000d);
            simulation.Step(new SimInput(
                0,
                0,
                SimActions.None,
                0,
                0,
                LookAxisCommand.ForResponsePermille(yawResponsePermille),
                LookAxisCommand.ForResponsePermille(pitchResponsePermille)));
        }

        throw new Xunit.Sdk.XunitException(
            "Could not settle the reticle on the requested Level 100 actor contact.");
    }

    private static double NormalizeRadians(double value)
    {
        while (value > Math.PI) value -= Math.Tau;
        while (value <= -Math.PI) value += Math.Tau;
        return value;
    }

}
