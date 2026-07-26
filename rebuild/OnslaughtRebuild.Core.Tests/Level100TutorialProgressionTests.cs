// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;
using Xunit.Abstractions;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Drives Level 100 the way a player does — only through <see cref="SimInput"/>
/// — and pins which released tutorial beats the world can generate on its own.
/// No named mission event is posted by any test here; every beat these tests
/// observe is produced by the simulation.
/// </summary>
public sealed class Level100TutorialProgressionTests
{
    private readonly ITestOutputHelper _output;

    public Level100TutorialProgressionTests(ITestOutputHelper output) =>
        _output = output;

    [Fact]
    public void AuthoredGroundVehicles_AreSeatedOnTheTerrain()
    {
        var simulation = new Simulation(1u, Level100TestActorDefinitions.Create());
        Level100ActorSnapshot[] tanks = simulation.Snapshot.Level100Actors.Actors
            .Where(actor => actor.Name is "Target Tank 2" or "Target Tank 3")
            .OrderBy(actor => actor.Name, StringComparer.Ordinal)
            .ToArray();

        Assert.Equal(2, tanks.Length);
        foreach (Level100ActorSnapshot tank in tanks)
        {
            // Authored Y is 0; the released height field puts the firing-range
            // ground at 600 and the Target Tank class origin sits 100 above it.
            Assert.Equal(700, tank.Pose.PositionMillimeters.Y);
        }
    }

    /// <summary>
    /// The released firing-range exercise, played rather than scripted. The
    /// two authored Target Tanks and the Target Warehouse are reached, aimed
    /// at and destroyed by Pulse Cannon rounds alone, and each Target Tank
    /// takes exactly the four hits the recorded 6 -> 4.2 -> 2.4 -> 0.6 -> -1.2
    /// life sequence predicts.
    /// </summary>
    [Fact]
    public void PulseCannonRun_DestroysEveryAuthoredStaticTarget()
    {
        var driver = Level100PlayerDriver.Create();
        driver.Run(9_000);
        foreach (string line in driver.Report)
        {
            _output.WriteLine(line);
        }

        WorldSnapshot final = driver.Snapshot;
        foreach (string name in new[] { "Target Tank 2", "Target Tank 3", "Target Warehouse" })
        {
            Level100ActorSnapshot actor = final.Level100Actors.Actors
                .Single(item => item.Name == name);
            Assert.Equal(Level100ActorLifecycle.Destroyed, actor.Lifecycle);
        }

        Assert.Equal(
            4,
            driver.ImpactsByActor[final.Level100Actors.Actors
                .Single(item => item.Name == "Target Tank 2").ActorId.Value]);
        Assert.Equal(
            4,
            driver.ImpactsByActor[final.Level100Actors.Actors
                .Single(item => item.Name == "Target Tank 3").ActorId.Value]);
    }

    /// <summary>
    /// The Twin Vulcan's Mech Bullet against the released Target Tank life.
    /// This is what the second firing-range exercise depends on, and it also
    /// bounds the open sum-versus-round-only damage question: the two
    /// surviving models differ by a single bullet out of seventy-five against
    /// a Target Tank, so tutorial progression cannot distinguish them, while
    /// the already-killed explosion-only model would need six thousand.
    /// </summary>
    [Theory]
    [InlineData(Level100DestructionState.MechBulletDamageBits, 75)]
    [InlineData(0x3DA3D70Au, 76)]
    public void MechBullet_NeedsTheSameOrderOfHitsUnderBothSurvivingDamageModels(
        uint damageBits,
        int expectedHits)
    {
        Assert.Equal(expectedHits, HitsToDestroyATargetTank(damageBits));
    }

    [Fact]
    public void PulseCannonRound_StillTakesFourHitsToDestroyATargetTank()
    {
        Assert.Equal(
            4,
            HitsToDestroyATargetTank(Level100DestructionState.PulseDamageBits));
    }

    private static int HitsToDestroyATargetTank(uint damageBits)
    {
        var state = new Level100DestructionState(
            1,
            Level100ContactCatalog.Instance.GetDefinition("Target Tank"));
        Span<Level100DestructionEvent> events =
            stackalloc Level100DestructionEvent[Level100DestructionState.MaximumEventsPerHit];
        var hit = new Level100ContactHit(
            1,
            0,
            Level100ContactSurfaceKind.Mesh,
            0,
            default,
            default,
            default);

        int hits = 0;
        while (!state.Terminal && hits < 10_000)
        {
            state.ApplyRoundHit(hit, damageBits, events);
            hits++;
        }

        return hits;
    }
}

/// <summary>
/// A minimal deterministic autopilot. It reads only what the HUD shows a
/// player — the current objective actor and its position — and answers with
/// look, move and fire. It never posts a mission event and never writes world
/// state.
/// </summary>
internal sealed class Level100PlayerDriver
{
    private readonly Simulation _simulation;
    private readonly List<string> _events = [];
    private readonly SortedDictionary<int, int> _impactsByActor = [];

    private Level100PlayerDriver(Simulation simulation) => _simulation = simulation;

    internal IReadOnlyList<string> Report => _events;

    internal IReadOnlyDictionary<int, int> ImpactsByActor => _impactsByActor;

    internal WorldSnapshot Snapshot => _simulation.Snapshot;

    internal static Level100PlayerDriver Create()
    {
        var simulation = new Simulation(
            1u,
            Level100TestActorDefinitions.Create(),
            new Level100TutorialProgress(true, true, true, true));
        for (int tick = 0; tick < SimulationConstants.Level100OpeningPanTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        return new Level100PlayerDriver(simulation);
    }

    internal void Run(int maximumTicks)
    {
        string? lastNavigation = null;
        int lastDestroyed = -1;
        for (int tick = 0; tick < maximumTicks; tick++)
        {
            WorldSnapshot state = _simulation.Snapshot;
            if (state.Level100Mission.Outcome != Level100MissionOutcome.Running)
            {
                _events.Add($"t{state.Tick} outcome {state.Level100Mission.Outcome}");
                return;
            }

            string? navigation = state.Level100Mission.NavigationObjective;
            if (navigation != lastNavigation)
            {
                _events.Add($"t{state.Tick} navigation -> {navigation ?? "(none)"}");
                lastNavigation = navigation;
            }

            int destroyed = state.Level100Actors.Actors.Count(
                actor => actor.Lifecycle == Level100ActorLifecycle.Destroyed);
            if (destroyed != lastDestroyed)
            {
                _events.Add($"t{state.Tick} destroyed actors = {destroyed}");
                lastDestroyed = destroyed;
            }

            WorldSnapshot next = _simulation.Step(NextInput(state));
            foreach (Level100DestructionEvent destruction in next.Level100DestructionEvents)
            {
                if (destruction.Kind != Level100DestructionEventKind.PulseImpact)
                {
                    continue;
                }
                _impactsByActor.TryGetValue(destruction.ActorId, out int count);
                _impactsByActor[destruction.ActorId] = count + 1;
            }
        }

        WorldSnapshot final = _simulation.Snapshot;
        _events.Add(
            $"t{final.Tick} stopped, outcome {final.Level100Mission.Outcome}, " +
            $"pulse={final.Level100PulseCannonEnabled} " +
            $"twinVulcan={final.Level100VulcanCannonEnabled}");
        _events.Add(
            "impactsByActor=" +
            string.Join(",", _impactsByActor.Select(pair => $"{pair.Key}:{pair.Value}")));
        foreach (Level100ActorSnapshot actor in final.Level100Actors.Actors
            .Where(actor => actor.TargetGroup != Level100MissionTargetGroup.None)
            .OrderBy(actor => actor.ActorId.Value))
        {
            _events.Add(
                $"  actor {actor.ActorId.Value} {actor.Name} def={actor.DefinitionName} " +
                $"grp={actor.TargetGroup} obj={actor.IsObjective} active={actor.Active} " +
                $"life={actor.Lifecycle} hp={actor.Health}");
        }
    }

    private static SimInput NextInput(WorldSnapshot state)
    {
        if (!state.Level100PlayerControlEnabled)
        {
            return SimInput.Idle;
        }

        Level100ActorSnapshot? target = SelectTarget(state);
        if (target is null)
        {
            return SimInput.Idle;
        }

        long deltaX = (long)target.Pose.PositionMillimeters.X - state.PlayerPosition.X;
        long deltaZ = (long)target.Pose.PositionMillimeters.Z - state.PlayerPosition.Z;
        double yawError = NormalizeRadians(
            Math.Atan2(-deltaX, deltaZ) - (state.FacingYawMicroRad / 1_000_000d));
        short lookX = (short)Math.Clamp((int)(yawError * 2_000), -1_000, 1_000);
        double horizontal = Math.Sqrt((double)((deltaX * deltaX) + (deltaZ * deltaZ)));

        // A player sweeps the target's body rather than shooting at its pivot.
        // Scanning the vertical extent keeps "the world cannot be hit" from
        // being confused with "the driver aimed at the ground".
        int aimHeight = 200 + (((state.Tick / 11) % 12) * 200);
        double pitchError =
            -Math.Atan2(
                target.Pose.PositionMillimeters.Y + aimHeight -
                    state.PlayerElevationMillimeters,
                horizontal) -
            (state.FacingPitchMicroRad / 1_000_000d);
        short lookY = (short)Math.Clamp((int)(pitchError * 4_000), -1_000, 1_000);

        if (target.Trigger.HasValue)
        {
            return new SimInput(
                0,
                horizontal > 1_500 ? (sbyte)1 : (sbyte)0,
                SimActions.None,
                0,
                0,
                lookX,
                lookY);
        }

        SimActions actions = Math.Abs(yawError) < 0.02 && Math.Abs(pitchError) < 0.02
            ? SimActions.Fire
            : SimActions.None;
        return new SimInput(
            0,
            horizontal > 18_000 ? (sbyte)1 : (sbyte)0,
            actions,
            0,
            0,
            lookX,
            lookY);
    }

    private static Level100ActorSnapshot? SelectTarget(WorldSnapshot state) =>
        state.Level100Actors.Actors
            .Where(actor =>
                actor.IsObjective &&
                actor.Active &&
                actor.Lifecycle == Level100ActorLifecycle.Alive)
            .OrderBy(actor => Distance(state, actor))
            .FirstOrDefault();

    private static double Distance(WorldSnapshot state, Level100ActorSnapshot actor)
    {
        double deltaX = (double)actor.Pose.PositionMillimeters.X - state.PlayerPosition.X;
        double deltaZ = (double)actor.Pose.PositionMillimeters.Z - state.PlayerPosition.Z;
        return Math.Sqrt((deltaX * deltaX) + (deltaZ * deltaZ));
    }

    private static double NormalizeRadians(double value)
    {
        while (value > Math.PI)
        {
            value -= 2 * Math.PI;
        }
        while (value < -Math.PI)
        {
            value += 2 * Math.PI;
        }
        return value;
    }
}
