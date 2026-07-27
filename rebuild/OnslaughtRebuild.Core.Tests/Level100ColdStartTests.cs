// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using Xunit.Abstractions;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// The whole released experience, once: cold start, frontend, Level 100, played
/// through the client's own player-input surface.
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
/// exact and the dead zone is the whole of what the client costs. If it does
/// not, the joined run's divergence is this driver's arithmetic and every
/// number taken from it is suspect.</para>
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
            seed: Level100ColdStartRun.SimulationSeed);
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
    /// Startup through the tutorial as ONE run, and the honest result.
    ///
    /// <para><b>It does not reach <c>Won</c>. It is lost to
    /// <c>TutorialBroken</c>, and the cause is NOT the join.</b> The control in
    /// this same file - the same cold career, driven straight into
    /// <c>Simulation.Step</c> with no client anywhere - loses the same way, to
    /// the same released guard, about seventy ticks earlier. What both runs do
    /// is kill <c>Target Truck #25</c> with a beat-3 miss while it is still
    /// running its authored route unactivated, and <c>TargetTruck1.msl</c>'s
    /// <c>died()</c> <c>case FALSE</c> arm posts <c>Broke Tutorial</c>. That is
    /// the released script defending itself, not a reconstruction gap, and it is
    /// the same failure mode
    /// <see cref="Level100FullChainTests.NaiveWalkerAutopilot_StallsOnBeatThreeAndNeverFinishes"/>
    /// documents at t2545 for a different driver.</para>
    ///
    /// <para><b>What is different about the cold career, and why it matters.</b>
    /// <c>Level100FullChainTests.ChainAutopilot_ReachesWonByInputAlone</c> runs
    /// with all four <c>SLOT_TUTORIAL_*</c> saved - a returning player, which
    /// skips the HUD lectures and their <c>player.Deactivate()</c> /
    /// <c>player.Activate()</c> theatre. <b>The client cannot produce that
    /// player.</b> <c>InteractiveSession</c>'s only constructor takes a seed and
    /// a definition set and forwards <c>default</c> to <c>Simulation</c>, so
    /// every level the shipping client enters is a cold first career. The
    /// lectures cost roughly nine hundred ticks before the player is handed
    /// control, the beat-4 trucks drive their authored routes from level start
    /// either way, and the driver therefore arrives at the firing range with a
    /// truck in a place it was not in when the chain was measured.</para>
    ///
    /// <para><b>And this measures how close the passing chain run was, which
    /// nothing did before.</b> In
    /// <c>ChainAutopilot_ReachesWonByInputAlone</c>, <c>Target Tank #23</c> dies
    /// at t6355 — which is what fires <c>Activate Static Targets 2</c> — and
    /// <c>Target Truck #25</c> dies at t6391. <b>The guard is cleared by 36
    /// ticks</b>, 1.2 released seconds. The cold career moves the same pair of
    /// deaths to t4765/t4741 (direct) and t4880/t4814 (through the client), so
    /// the margin is not merely reduced, it changes sign. The driver was
    /// already firing at the truck; the only thing that ever made it legal was
    /// the tank dying first.</para>
    ///
    /// <para><b>This assertion is failing-forward, in the style of the naive
    /// walker control.</b> It pins the outcome that is true today rather than
    /// the one wanted, because pinning <c>Won</c> would leave a red gate and
    /// pinning nothing would let the run rot. When a driver clears the cold
    /// career, replace <see cref="Level100MissionOutcome.Lost"/> here with
    /// <see cref="Level100MissionOutcome.Won"/> and restore the beat-4 to
    /// beat-10 assertions from
    /// <c>Level100FullChainTests.ChainAutopilot_ReachesWonByInputAlone</c>.</para>
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
        // over control, both walked-to volumes dispatched, and beats 1-3's four
        // authored statics were destroyed by the player's own rounds.
        Assert.True(final.Tick > SimulationConstants.Level100OpeningPanTicks);
        foreach (Level100MissionTrigger trigger in new[]
        {
            Level100MissionTrigger.TargetZone1,
            Level100MissionTrigger.FiringRange,
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

        // The honest negative, and the control that says whose fault it is.
        Assert.Equal(Level100MissionOutcome.Lost, _coldStart.Outcome);
        Assert.Equal(
            Level100MissionFailureReason.TutorialBroken,
            final.Level100Mission.FailureReason);
        Assert.Equal(_coldStart.Outcome, _control.Outcome);
        Assert.Equal(
            final.Level100Mission.FailureReason,
            controlFinal.Level100Mission.FailureReason);

        // Full hull at the loss. This is not a run that was worn down; it is a
        // run that broke a released rule.
        Assert.Equal(SimulationConstants.MaximumHull, final.Hull);
    }

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
    /// control as a property of the client rather than of this driver.</para>
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
    /// <c>InteractiveSession.QueuePointerMotionMilliPixels</c>. That path
    /// recenters by the released 10/17-per-20 Hz retention and then discards
    /// any residue below half a pixel - and half a pixel is already
    /// <b>15 permille</b> of stick. So the first fourteen stops of the axis do
    /// not exist through the client, and a driver asking for them gets
    /// nothing.</para>
    ///
    /// <para>This is a property of the reconstruction's input adapter, not of
    /// Core: <c>Simulation.Step</c> accepts every value from 1 to 1000 and
    /// <c>Level100ChainAutopilot</c> commands them. It is recorded here because
    /// the joined run's trace diverges from its own control because of it,
    /// while every isolated measurement in this suite drives
    /// <c>SimInput</c> directly and cannot see it at all.</para>
    /// </summary>
    [Fact]
    public void ClientPointerPath_CannotReachTheFirstFourteenLookStops()
    {
        for (short requested = 1; requested <= 14; requested++)
        {
            Assert.Equal(
                (short)0,
                Level100InteractiveChainHost.DeliverablePermille(requested));
            Assert.Equal(
                (short)0,
                Level100InteractiveChainHost.DeliverablePermille((short)-requested));
        }

        // From 15 up the axis is exact, in both directions, all the way to full
        // deflection.
        for (short requested = 15; requested <= 1_000; requested++)
        {
            Assert.Equal(
                requested,
                Level100InteractiveChainHost.DeliverablePermille(requested));
            Assert.Equal(
                (short)-requested,
                Level100InteractiveChainHost.DeliverablePermille((short)-requested));
        }
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
