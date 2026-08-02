// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using Xunit.Abstractions;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// The deterministic in-process reconstruction path, once: cold start,
/// frontend, Level 100, played through the client's own player-input surface.
///
/// <para>It takes about six seconds, so it is paid for once.</para>
/// </summary>
public sealed class Level100ColdStartRunFixture
{
    internal Level100ColdStartRun Run { get; }

    internal Level100MissionOutcome Outcome { get; }

    public Level100ColdStartRunFixture()
    {
        Run = new Level100ColdStartRun();
        Outcome = Run.Run();
    }
}

/// <summary>
/// The control that separates the two things the joined run changes at once.
///
/// <para>The joined run differs from
/// <c>Level100FullChainTests.ChainAutopilot_ReachesWonByInputAlone</c> in
/// exactly two ways: it is a <b>cold first career</b> rather than a returning
/// player with all four tutorial slots saved, and its input travels through
/// <c>OnslaughtRebuild.Client.InteractiveSession</c> rather than into
/// <c>Simulation.Step</c>. This fixture holds the first constant and removes
/// the second, so a divergence is attributed rather than guessed at.</para>
/// </summary>
public sealed class Level100ColdCareerDirectRunFixture
{
    internal Level100ChainAutopilot Driver { get; }

    internal Level100MissionOutcome Outcome { get; }

    public Level100ColdCareerDirectRunFixture()
    {
        Driver = Level100ChainAutopilot.Create(default);
        Outcome = Driver.Run(1_200 * SimulationConstants.TicksPerSecond);
    }
}

/// <summary>
/// The instrument check for <see cref="Level100InteractiveChainHost"/>.
///
/// <para>Same cold career, same seed as the client's, straight into
/// <c>Simulation.Step</c> — with ONLY the analogue-look quantisation the
/// client's pointer path imposes applied on the way in. If this run's pose
/// trace equals the client run's, the host's inverse of the pointer laws is
/// exact and the whole-pixel quantum is the whole of what the client costs. If
/// it does not, the joined run's divergence is this driver's arithmetic and
/// every number taken from it is suspect.</para>
/// </summary>
public sealed class Level100ClientPointerQuantisedRunFixture
{
    internal Level100ChainAutopilot Driver { get; }

    internal Level100MissionOutcome Outcome { get; }

    public Level100ClientPointerQuantisedRunFixture()
    {
        Driver = Level100ChainAutopilot.Create(
            default,
            quantizeLookToClientPointerPath: true,
            seed: Level100ColdStartRun.SimulationSeed,
            quantizeLookToIntegerMousePixels: true);
        Outcome = Driver.Run(1_200 * SimulationConstants.TicksPerSecond);
    }
}

public sealed class Level100ColdStartTests
    : IClassFixture<Level100ColdStartRunFixture>,
      IClassFixture<Level100ColdCareerDirectRunFixture>,
      IClassFixture<Level100ClientPointerQuantisedRunFixture>
{
    private readonly ITestOutputHelper _output;
    private readonly Level100ColdStartRunFixture _coldStart;
    private readonly Level100ColdCareerDirectRunFixture _control;
    private readonly Level100ClientPointerQuantisedRunFixture _quantised;

    public Level100ColdStartTests(
        ITestOutputHelper output,
        Level100ColdStartRunFixture coldStart,
        Level100ColdCareerDirectRunFixture control,
        Level100ClientPointerQuantisedRunFixture quantised)
    {
        _output = output;
        _coldStart = coldStart;
        _control = control;
        _quantised = quantised;
    }

    /// <summary>
    /// The cold-start sequence: every stage of the released experience appears
    /// once, in the released order, before the level begins.
    ///
    /// <para>Nothing here is stepped past. The frontend is navigated by
    /// keystrokes and left clicks at 640x480 design-stage coordinates, Level 100
    /// is entered by CLICKING THE LEVEL NODE on SELECT LEVEL, and the Loading
    /// page completes on its own two-frame gate.</para>
    /// </summary>
    [Fact]
    public void ColdStart_VisitsEveryReleasedStageInOrder()
    {
        foreach (ColdStartStage stage in _coldStart.Run.Stages)
        {
            _output.WriteLine(stage.ToString());
        }

        string[] expected =
        [
            "startup:LostToysLogo",
            "startup:OpeningMontage",
            "startup:Splash",
            "startup:Finished",
            "frontend:ClickToStart",
            "frontend:MainMenu",
            "frontend:MainMenuInteractive",
            "frontend:DevSelect",
            "frontend:LevelSelect",
            "frontend:MissionBriefing",
            "frontend:SelectConfiguration",
            "frontend:Loading",
            "frontend:Gameplay",
            "level:opening-pan-done",
        ];

        Assert.Equal(
            expected,
            _coldStart.Run.Stages.Select(stage => stage.Name).Take(expected.Length));

        // The reveal that runs on the way into the main menu really does own the
        // input: a click during it changed nothing.
        Assert.True(
            _coldStart.Run.MainMenuRevealSwallowedAClick,
            "a click during the 50-frame main-menu reveal must do nothing");
        Assert.True(_coldStart.Run.LoadRequestFrame > 0, "the load request never fired");
    }

    /// <summary>
    /// Startup through the tutorial as one deterministic in-process run, and
    /// the honest current result.
    ///
    /// <para>The client/input-adapter path destroys <b>18 of the 22</b>
    /// targets, reaches <see cref="Level100MissionOutcome.Won"/> through
    /// <c>event("Reached Target Zone 4")</c>, and gets there on the released
    /// sub-40 % hull ABORT branch: it takes 2 of the six wave-2 drones, trips
    /// <c>event("Abort Airborne Drones")</c> at t6732 with 5,700 of 20,000
    /// hull, and leaves primary objective 4 <c>Failed</c>. A direct-Core run
    /// with the same pointer/integer-pixel quantisation has the same outcome,
    /// tick, state hash, and pose trace.</para>
    ///
    /// <para><b>The UNQUANTISED direct-Core control for the same cold career
    /// still does the whole thing</b> - all 22 destroyed, all six wave-2
    /// drones, no abort, objective 4 <c>Complete</c>, <c>Won</c> at t7876 with
    /// 8,100 hull. So the four the client arm loses are lost to the
    /// whole-retail-pixel look quantum, on a beat that is chaotic at finer than
    /// that quantum, and not to anything in <c>InteractiveSession</c>.</para>
    ///
    /// <para><b>The client arm used to destroy all 22 and clear wave 2
    /// outright.</b> It stopped on 2026-08-01, when task #154 (the vertical
    /// datum) and task #161 (the look-response table) both moved the world this
    /// driver flies through - each of them TOWARD the released build. The
    /// counts here are re-derived from the run, not tuned back; see the beat-9
    /// comment in the body.</para>
    ///
    /// <para><b>This run used to end <see cref="Level100MissionOutcome.Lost"/>
    /// with <see cref="Level100MissionFailureReason.WaterLoss"/> at tick
    /// 17,699</b>, on the ferry flight home, with every target in the level
    /// already destroyed. See the terminal-state comment in the body for what
    /// that was and what changed.</para>
    ///
    /// <para>This is not a human or native-Godot playthrough. It pins the
    /// deterministic regression truth of this omniscient synthetic test driver.
    /// It does not establish a frontend defect or released water-navigation
    /// behavior. A naive water guard was already tried and measured worse; see
    /// the ignored local evidence named in <c>developer_state.json</c> before
    /// changing that behavior.</para>
    /// </summary>
    [Fact]
    public void ColdStart_PlaysLevel100ThroughThePlayerInputSurface()
    {
        Level100ColdStartRun run = _coldStart.Run;
        WorldSnapshot final = run.Final;
        WorldSnapshot controlFinal = _control.Driver.Snapshot;

        _output.WriteLine(
            "analogue look commands = {0}; unreachable through the client's " +
            "pointer path (<15 permille) = {1}; finer than one retail mouse " +
            "pixel (<30 permille) = {2}",
            run.Host.LookCommands,
            run.Host.UnreachableLookCommands,
            run.Host.SubRetailPixelLookCommands);
        _output.WriteLine(
            "CLIENT  outcome={0} tick={1} hull={2} reason={3} hash={4}",
            _coldStart.Outcome,
            final.Tick,
            final.Hull,
            final.Level100Mission.FailureReason,
            StateHasher.ComputeHex(final));
        _output.WriteLine(
            "CONTROL outcome={0} tick={1} hull={2} reason={3} hash={4}",
            _control.Outcome,
            controlFinal.Tick,
            controlFinal.Hull,
            controlFinal.Level100Mission.FailureReason,
            StateHasher.ComputeHex(controlFinal));
        _output.WriteLine(
            "first divergent tick = {0}",
            FirstDivergentTick(run.Driver!, _control.Driver));
        _output.WriteLine(string.Empty);
        _output.WriteLine("--- client (through InteractiveSession) ---");
        foreach (string line in run.Driver!.Report)
        {
            _output.WriteLine(line);
        }

        _output.WriteLine(string.Empty);
        _output.WriteLine("--- control (straight into Core) ---");
        foreach (string line in _control.Driver.Report)
        {
            _output.WriteLine(line);
        }

        // The level really was played: the opening pan ran, the script handed
        // over control, and ALL FIVE trigger volumes dispatched - each of which
        // only dispatches out of jet mode, so the three flight legs were flown
        // and landed.
        Assert.True(final.Tick > SimulationConstants.Level100OpeningPanTicks);
        foreach (Level100MissionTrigger trigger in new[]
        {
            Level100MissionTrigger.TargetZone1,
            Level100MissionTrigger.FiringRange,
            Level100MissionTrigger.TargetZone2,
            Level100MissionTrigger.TargetZone3,
        })
        {
            Assert.True(
                final.Level100Actors.Actors
                    .Single(actor => actor.Trigger == trigger).TriggerEventDispatched,
                $"{trigger} never dispatched.");
        }

        foreach (string name in new[]
        {
            "Target Tank 2", "Target Tank 3", "Target Warehouse", "Target Tank #23",
        })
        {
            Assert.Equal(
                Level100ActorLifecycle.Destroyed,
                final.Level100Actors.Actors
                    .Single(actor => actor.Name == name).Lifecycle);
        }

        // Reported before it is asserted, so a beat-9 move prints its numbers
        // instead of only its first tripped assertion. That ordering cost a
        // re-run during the 2026-08-01 re-derivation.
        _output.WriteLine(
            "CLIENT beats: trucks={0} moving={1} air1={2} air2={3} aborted={4} " +
            "objective4={5}",
            Destroyed(final, Level100MissionTargetGroup.TargetTrucks),
            Destroyed(final, Level100MissionTargetGroup.MovingTargets),
            Destroyed(final, Level100MissionTargetGroup.AirborneTargets1),
            Destroyed(final, Level100MissionTargetGroup.AirborneTargets2),
            final.Level100Mission.Aborted,
            final.Level100Mission.PrimaryObjectives
                .Single(objective => objective.Objective == 4).Status);
        _output.WriteLine(
            "CONTROL beats: air2={0} aborted={1} objective4={2}",
            controlFinal.Level100Actors.Actors.Count(actor =>
                actor.TargetGroup == Level100MissionTargetGroup.AirborneTargets2 &&
                actor.Lifecycle == Level100ActorLifecycle.Destroyed),
            controlFinal.Level100Mission.Aborted,
            controlFinal.Level100Mission.PrimaryObjectives
                .Single(objective => objective.Objective == 4).Status);

        // Beats 4, 5, 7 and 9, every one of them shot with the weapon the
        // script hands over in the order it hands it over.
        //
        // BEAT 9 MOVED ON 2026-08-01 and it is a REGRESSION IN THE DRIVER'S
        // RESULT on this arm, recorded as one rather than absorbed. The client
        // arm now takes 2 of the six wave-2 drones instead of six and wins on
        // the released sub-40 % hull abort branch instead of by clearing the
        // wave.
        //
        // ISOLATED CAUSALLY, NOT ARGUED. Two changes landed together - #154
        // (the vertical datum, so every static and every air spawn now seats
        // where released `CThing::Init` puts it) and #161 (the look-response
        // table, now the nearest integer permille to the released law at all
        // 1,001 inputs). Re-running this fixture with ONLY #154 applied and the
        // released look table restored gives the SAME two kills on this arm -
        // CLIENT Won t7216 hull 6800, abort at t6666 - so the client arm's move
        // is #154's alone and #161 adds nothing to it.
        //
        // #161's contribution here is the OPPOSITE SIGN, on the other arm: with
        // #154 alone the unquantised control ALSO drops onto the abort branch
        // (control Won t7399 hull 3000, abort at t6718); adding #161 puts it
        // back to a full clear of all 22 with no abort. That is the same
        // single-term-flips-one-career pattern the measurement table on
        // `Level100ChainAutopilot.ErrorPole` already records, and it is why
        // neither number here is evidence about either change's correctness.
        //
        // NEITHER CHANGE IS A DEFECT AND NEITHER IS BEING BACKED OUT: each
        // moves the reconstruction TOWARD the released build, and the beat-9
        // kill count is a property of this synthetic driver, not of the game.
        // The counts are RE-DERIVED from the run rather than recovered by
        // tuning the driver, which would be fitting a chaotic objective.
        //
        // WHAT DID NOT MOVE, and it is the reason this is a re-derivation
        // rather than a failure: beats 4, 5 and 7 are unchanged at 3, 6 and 3,
        // the run still reaches `Won` through `Reached Target Zone 4` (asserted
        // below), and the UNQUANTISED control still destroys all 22 and clears
        // wave 2 outright (asserted below, and printed above).
        Assert.Equal(3, Destroyed(final, Level100MissionTargetGroup.TargetTrucks));
        Assert.Equal(6, Destroyed(final, Level100MissionTargetGroup.MovingTargets));
        Assert.Equal(3, Destroyed(final, Level100MissionTargetGroup.AirborneTargets1));
        Assert.Equal(2, Destroyed(final, Level100MissionTargetGroup.AirborneTargets2));

        // Beat 9 is now cleared by the released sub-40 % hull poll rather than
        // by kills: `aborted` is the LevelScript's own local, set by
        // `event("Abort Airborne Drones")`, which fired at t6732 with the hull
        // at 5,700 of 20,000. This is an exact assertion on the branch taken,
        // not a relaxed one - it says the poll fired, where it used to say the
        // poll never fired.
        Assert.True(
            final.Level100Mission.Aborted,
            "this run is expected to reach `Reached Target Zone 4` through the " +
            "LevelScript's sub-40 % hull abort poll. If it has stopped firing, " +
            "the driver is clearing wave 2 again - that is a BETTER run and " +
            "this assertion, the wave-2 count and objective 4 below should all " +
            "be re-derived back up rather than left passing by accident.");
        Assert.Equal(
            Level100PrimaryObjectiveStatus.Failed,
            final.Level100Mission.PrimaryObjectives
                .Single(objective => objective.Objective == 4).Status);

        // THE CONTROL STILL CLEARS THE WAVE, and this is what separates "the
        // world moved" from "the reconstruction got worse". The unquantised
        // cold career destroys all six wave-2 drones, never trips the abort
        // poll, and completes objective 4. The whole of the regression above is
        // therefore carried by the client path's whole-retail-pixel look
        // quantisation, on a beat that is chaotic at finer than that quantum.
        Assert.Equal(
            6,
            controlFinal.Level100Actors.Actors.Count(actor =>
                actor.TargetGroup == Level100MissionTargetGroup.AirborneTargets2 &&
                actor.Lifecycle == Level100ActorLifecycle.Destroyed));
        Assert.False(controlFinal.Level100Mission.Aborted);
        Assert.Equal(
            Level100PrimaryObjectiveStatus.Complete,
            controlFinal.Level100Mission.PrimaryObjectives
                .Single(objective => objective.Objective == 4).Status);

        // THE OUTPUT-CHANNEL CONTRACT, and it is the reason the joined run gets
        // this far at all. The driver is held to the stick positions an INTEGER
        // mouse pixel can produce, which since 2026-07-30 is exactly what the
        // client's own pointer path delivers, so nothing is lost between the
        // two. Before this run was quantised, 2,575 of its 5,439 analogue look
        // commands arrived as ZERO and it lost the level at t5277.
        //
        // This is HALF of player-plausibility, and the half that is cheap. What
        // the driver READS is still omniscient - exact Health, full 3D actor
        // poses, line-of-sight ray tests - so a `Won` here is not yet evidence
        // that a human could reach it. GOAL.md's demotion of the driven run to
        // an acceptance test is aimed at exactly that gap.
        Assert.Equal(0, run.Host.UnreachableLookCommands);
        Assert.True(run.Host.LookCommands > 1_000);

        // THE TERMINAL STATE, and it changed: this run used to end
        // `Lost`/`WaterLoss` at t17699 and now reaches `Won`.
        //
        // What it used to do, because the reason matters more than the verdict:
        // the fight was over and won - objective 4 is `Complete` above - and the
        // ferry home drowned. `NavigateToZone` dropped out of jet mode as soon
        // as the volume was inside 20 m HORIZONTALLY, with no altitude term at
        // all, and on this route that happened 28.7 m up over open water. From
        // that tick the airframe was an airborne walker, and
        // `Simulation.UpdateAirborneWalkerMovement` takes no `SimInput`: the
        // touchdown point was fixed at the morph and it came down 10.1 m past
        // the zone, in the sea.
        //
        // What fixed it is an altitude term on the hand-off - see
        // `Level100ChainAutopilot.ZoneHandoffClearanceMillimeters`. It is NOT a
        // change to the water rule, which is a byte-faithful port of
        // `BattleEngine.cpp:1259-1262` and is now pinned two ways by
        // `Level100FerryLandingTests`.
        //
        // THIS IS THE ACCEPTANCE TEST IN `GOAL.md`, WITH BOTH OF ITS
        // QUALIFIERS. The career is the COLD first career - all four
        // `SLOT_TUTORIAL_*` unsaved, which is the only career the shipping
        // client can start - and the input travels through the client's own
        // `InteractiveSession`, restricted to stick positions a whole retail
        // mouse pixel can produce. It is still not a claim that a human can do
        // this: what the driver READS is omniscient, and `GOAL.md` demotes the
        // driven run to an acceptance test for exactly that reason.
        Assert.Equal(Level100MissionOutcome.Won, _coldStart.Outcome);
        Assert.Equal(
            Level100MissionFailureReason.None,
            final.Level100Mission.FailureReason);
        Assert.True(
            final.Level100Actors.Actors
                .Single(actor => actor.Trigger == Level100MissionTrigger.TargetZone4)
                .TriggerEventDispatched,
            "Target Zone 4 never dispatched, so `Won` did not come from " +
            "`event(\"Reached Target Zone 4\")`.");

        // AND THE CONTROL: the same cold first career driven unquantised
        // straight into `Simulation.Step` also reaches `Won`. The
        // pointer-quantised direct run matches the client run exactly; see the
        // next test.
        //
        // THE CONTROL IS WHERE THE 20 Hz MIGRATION SHOWED FIRST, and it was
        // not a host defect. Immediately after the migration this arm ended
        // `Lost` / `PlayerDeath` at t6877 with hull 0 while the client arm
        // still reached `Won` at t7177 - which reads like a divergence between
        // the two drivers, and is not one: QUANTISED matched CLIENT bit for
        // bit, so both hosts were exact. Both arms were losing beat 9 onto the
        // released sub-40 % abort with one kill between them, and the control
        // simply ran out of hull first because the unquantised look axis puts
        // it on a slightly different trajectory. The cause was three
        // rate-denominated constants in the DRIVER that the migration did not
        // move; see `Level100ChainAutopilot.ErrorPole` for the arithmetic and
        // the four-way measurement that attributes it.
        Assert.Equal(Level100MissionOutcome.Won, _control.Outcome);
        Assert.Equal(
            Level100MissionFailureReason.None,
            controlFinal.Level100Mission.FailureReason);
    }

    private static int Destroyed(
        WorldSnapshot state,
        Level100MissionTargetGroup group) => state.Level100Actors.Actors
        .Count(actor => actor.TargetGroup == group &&
            actor.Lifecycle == Level100ActorLifecycle.Destroyed);

    /// <summary>
    /// The joined run is the direct run plus exactly one thing: the analogue
    /// look quantisation the client's pointer path imposes.
    ///
    /// <para>Both runs are the same cold career on the same seed. One goes
    /// through <c>InteractiveSession</c>; the other goes straight into
    /// <c>Simulation.Step</c> with the look axes passed through
    /// <see cref="Level100InteractiveChainHost.DeliverablePermille"/> and
    /// nothing else changed. <b>Equal traces mean the pointer inverse in
    /// <see cref="Level100InteractiveChainHost"/> is exact</b>, which is what
    /// entitles anyone to read the joined run's divergence from the unquantised
    /// control as the measured effect of pointer quantisation, not as an
    /// additional <c>InteractiveSession</c> or frontend defect.</para>
    /// </summary>
    [Fact]
    public void ClientRoute_IsTheDirectRoutePlusPointerQuantisationAndNothingElse()
    {
        WorldSnapshot client = _coldStart.Run.Final;
        WorldSnapshot quantised = _quantised.Driver.Snapshot;
        _output.WriteLine(
            "CLIENT    tick={0} hull={1} outcome={2} hash={3}",
            client.Tick,
            client.Hull,
            _coldStart.Outcome,
            StateHasher.ComputeHex(client));
        _output.WriteLine(
            "QUANTISED tick={0} hull={1} outcome={2} hash={3}",
            quantised.Tick,
            quantised.Hull,
            _quantised.Outcome,
            StateHasher.ComputeHex(quantised));
        _output.WriteLine(
            "first divergent tick = {0}",
            FirstDivergentTick(_coldStart.Run.Driver!, _quantised.Driver));

        Assert.Equal(_quantised.Outcome, _coldStart.Outcome);
        Assert.Equal(quantised.Tick, client.Tick);
        Assert.Equal(
            StateHasher.ComputeHex(quantised),
            StateHasher.ComputeHex(client));
        Assert.Equal(_quantised.Driver.PoseTrace, _coldStart.Run.Driver!.PoseTrace);
    }

    /// <summary>
    /// The client's player-input surface is <b>not</b> transparent to a driver
    /// that commands an analogue look axis, and this measures the loss without
    /// reference to any particular run.
    ///
    /// <para>The client leaves its look actions unbound on purpose
    /// (<c>FirstFlightGame.ConfigureInputMap</c>), so the only route to the
    /// analogue axis is mouse motion through
    /// <c>InteractiveSession.QueuePointerMotionMilliPixels</c>. That path is
    /// quantised to whole retail mouse pixels, so the axis it can deliver is
    /// the LATTICE <c>{0, ±30, ±61, ±91, …}</c> and nothing in between.</para>
    ///
    /// <para><b>This test used to be called
    /// <c>ClientPointerPath_CannotReachTheFirstFourteenLookStops</c>, and its
    /// premise was half wrong.</b> The client did discard permille ±1..±14 -
    /// an invented half-pixel dead zone, task #141, measured at 44.2 % of one
    /// run's analogue look commands. But it then delivered ±15..±1000
    /// <i>exactly</i>, which is finer than the released build can aim. Retail
    /// has no dead zone on this path at all (the shipped mouse case at
    /// 0x0042DB40 clamps to ±1.0 and sign-gates at 0.0, and the GPL drop's 0.36
    /// <c>ANALOGUE_X_DEAD</c> is a joystick rule that does not occur once in
    /// the shipped image); what it has is a QUANTUM, because the cursor
    /// displacement is an integer pixel count. So the fourteen stops are still
    /// zero and the floor moved by one permille, while everything ABOVE the
    /// floor snapped onto retail's grid. The reconstruction lost a capability
    /// the released build never had.</para>
    ///
    /// <para>This is a property of the reconstruction's input adapter, not of
    /// Core: <c>Simulation.Step</c> accepts every value from 1 to 1000 and
    /// <c>Level100ChainAutopilot</c> commands them. It is recorded here because
    /// every isolated measurement in this suite drives <c>SimInput</c> directly
    /// and cannot see it at all.</para>
    /// </summary>
    [Fact]
    public void ClientPointerPath_DeliversExactlyRetailsWholePixelLattice()
    {
        // Derived from the released law rather than transcribed: n whole pixels
        // are worth n * g_MouseSensitivity * 13/3000 of full deflection, and
        // the image's untouched sensitivity is 7.0.
        var lattice = new HashSet<short>();
        for (int pixels = 1; pixels <= 1_000; pixels++)
        {
            int permille = (int)Math.Round(
                pixels * 91_000 / 3_000d,
                MidpointRounding.AwayFromZero);
            lattice.Add((short)Math.Min(permille, 1_000));
        }

        int exact = 0;
        int swallowed = 0;
        for (short requested = 1; requested <= 1_000; requested++)
        {
            short delivered =
                Level100InteractiveChainHost.DeliverablePermille(requested);

            // Odd symmetry, on every single stop and not just the sampled ones.
            Assert.Equal(
                (short)-delivered,
                Level100InteractiveChainHost.DeliverablePermille((short)-requested));

            if (delivered == 0)
            {
                // The ONLY thing delivered as nothing is a request that rounds
                // to zero whole pixels - below half of one, which at this
                // sensitivity is 15 permille.
                Assert.True(
                    requested <= 15,
                    $"{requested} permille was swallowed; only <= 15 should be");
                swallowed++;
                continue;
            }

            // Everything else lands ON the lattice, at the NEAREST point to
            // what was asked for. It snaps; it never refuses.
            Assert.Contains(delivered, lattice);
            Assert.True(
                Math.Abs(delivered - requested) <= 16,
                $"{requested} permille was delivered as {delivered}, which is " +
                "not the nearest whole pixel");

            if (delivered == requested)
            {
                exact++;
            }
        }

        // 32 whole pixels reach 971 permille and the 33rd saturates the axis.
        Assert.Equal(33, exact);

        // TASK #141'S FOURTEEN STOPS, STATED AS THE COUNT IT ASKED FOR - AND
        // THE ANSWER IS NOT THE ONE THE TASK EXPECTED.
        //
        // Before: 1..14 were delivered as ZERO by a half-pixel dead zone, and
        // 15..1000 were delivered EXACTLY - finer than the released build can
        // aim anywhere above the floor.
        // After:  1..15 are delivered as zero, because retail's first whole
        // pixel is worth 30 permille and half a pixel is 15.17.
        //
        // So the floor moved by ONE permille, 14 -> 15, and the fourteen stops
        // are still zero. What actually changed is everything above the floor:
        // the client no longer aims between retail's pixels. Making 1..14
        // reachable would need sub-pixel cursor state, which the released build
        // does not have - #141 called that out as the outcome to preserve
        // rather than fix, and this is that case.
        Assert.Equal(15, swallowed);

        // The stop immediately above the floor is no longer itself: it is the
        // first pixel, which is where a hand would actually put it.
        Assert.Equal(
            (short)30,
            Level100InteractiveChainHost.DeliverablePermille(16));
        Assert.Equal(
            (short)30,
            Level100InteractiveChainHost.DeliverablePermille(30));
        Assert.Equal(
            (short)0,
            Level100InteractiveChainHost.DeliverablePermille(15));
    }

    /// <summary>
    /// The first tick at which the two runs' player poses differ. Both traces
    /// start on the tick the opening pan ends.
    /// </summary>
    private static int FirstDivergentTick(
        Level100ChainAutopilot client,
        Level100ChainAutopilot control)
    {
        IReadOnlyList<long> a = client.PoseTrace;
        IReadOnlyList<long> b = control.PoseTrace;
        int shared = Math.Min(a.Count, b.Count);
        for (int index = 0; index < shared; index++)
        {
            if (a[index] != b[index])
            {
                return SimulationConstants.Level100OpeningPanTicks + index;
            }
        }

        return -1;
    }
}
