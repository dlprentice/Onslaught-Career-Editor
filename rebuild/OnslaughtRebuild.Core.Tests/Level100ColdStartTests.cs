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
        Outcome = Driver.Run(30 * 1_200);
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
        Outcome = Driver.Run(30 * 1_200);
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
    /// <para>The client/input-adapter path destroys all 22 targets, completes
    /// primary objective 4, never fires the released abort poll, and reaches
    /// <see cref="Level100MissionOutcome.Won"/> through
    /// <c>event("Reached Target Zone 4")</c>. A direct-Core run with the same
    /// pointer/integer-pixel quantisation has the same outcome, tick, state
    /// hash, and pose trace, and so does the <b>unquantised</b> direct-Core
    /// control for the same cold career.</para>
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

        // Beats 4, 5, 7 and 9, every one of them shot with the weapon the
        // script hands over in the order it hands it over.
        Assert.Equal(3, Destroyed(final, Level100MissionTargetGroup.TargetTrucks));
        Assert.Equal(6, Destroyed(final, Level100MissionTargetGroup.MovingTargets));
        Assert.Equal(3, Destroyed(final, Level100MissionTargetGroup.AirborneTargets1));
        Assert.Equal(6, Destroyed(final, Level100MissionTargetGroup.AirborneTargets2));

        // Beat 9 was cleared by KILLS, not by the released sub-40 % hull poll:
        // `aborted` is the LevelScript's own local and `Assert.False` on it is
        // the claim that the poll never fired at all.
        Assert.False(
            final.Level100Mission.Aborted,
            "this run is expected to clear wave 2 outright");
        Assert.Equal(
            Level100PrimaryObjectiveStatus.Complete,
            final.Level100Mission.PrimaryObjectives
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
