// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;
using Xunit.Abstractions;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// The ambient Air Trainer's opening pass along <c>Flyby Path</c>: which nodes
/// it visits, in which order, and how close to the ground it gets doing it.
/// </summary>
/// <remarks>
/// <para>
/// <b>The defect these pin.</b> <c>Flyby Path</c> serializes its nodes
/// <c>[43, 42, 41]</c> and its markers' own <c>target</c> pointers chain them
/// <c>[41, 42, 43]</c>. Until #146 the follower indexed
/// <c>Level100WaypointPathDefinition.Points</c> — the serialized list — so the
/// Air Trainer began its authored route at the chain's TAIL and flew the whole
/// thing backwards.
/// </para>
/// <para>
/// <b>Why chain order is retail.</b> Read from the pristine specimen
/// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, sha256
/// <c>74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750</c>:
/// <c>CScriptEventNB::UpdateWaypointFollowing</c> (<c>0x00538470</c>) holds a
/// POINTER to the current waypoint at <c>this+0x14</c> and advances it with
/// <c>mov eax,[esi+0x14]</c> / <c>mov ecx,[eax+0x3c]</c> (<c>0x005384dc</c>)
/// followed by <c>mov [esi+0x14],ecx</c> (<c>0x005384fd</c>) — the successor
/// comes from the waypoint itself. <c>CWaypoint::InitAndLink</c>
/// (<c>0x005057b0</c>) is what fills that <c>+0x3c</c>, from the marker's own
/// spawn record at <c>+0xa4</c>. And the two script natives seed the cursor
/// with the single pointer the shared path lookup at <c>0x00505c30</c> returns,
/// never with a list — <c>FollowWaypointWait</c> (<c>0x00537e40</c>) at
/// <c>mov [ebx+0x14],eax</c>, <c>0x00537e73</c>. There is no serialized index
/// anywhere in that loop.
/// </para>
/// <para>
/// The corroborating shipped string, at VA <c>0x0064fe50</c> in the same
/// specimen: <c>"ERROR: Waypoint points to previous"</c>. Waypoints point at
/// waypoints.
/// </para>
/// </remarks>
public sealed class Level100AirTrainerFlybyTests
{
    private readonly ITestOutputHelper _output;

    public Level100AirTrainerFlybyTests(ITestOutputHelper output) =>
        _output = output;

    /// <summary>
    /// The Air Trainer's authored initial pose, from the hash-pinned manifest
    /// <c>level100-static-world.json</c> (sha256
    /// <c>2DFAD0DC…8568</c>, schema v14), actor <c>wres:rlwd:0040</c>. The Core
    /// fixture parks every non-static actor at the origin, which is fine for
    /// the tests that only need an actor to exist and useless for a test about
    /// a flight path, so this one is stated here and cross-checked against the
    /// manifest by
    /// <see cref="Level100WaypointFixtureTests.ManifestAirTrainer_IsAuthoredWhereTheseTestsPutIt"/>.
    /// </summary>
    internal static readonly SimVector3 AuthoredAirTrainerPosition =
        new(-23_188, -15_000, 149_250);

    /// <summary>
    /// The authored basis, same source. Its third column is
    /// <c>(8.74e-8, 0, -1)</c>: the aircraft starts pointing down -Z, which is
    /// broadly toward both candidate first nodes, so nothing about the result
    /// below is an artefact of the plane being aimed at the answer.
    /// </summary>
    internal static readonly Level100FloatBasis3Bits AuthoredAirTrainerBasis =
        new(
            -1_082_130_432, 0, 867_941_678,
            0, 1_065_353_216, 0,
            -1_279_541_970, 0, -1_082_130_432);

    private const int FlightCoreTicks = 200 * SimulationConstants.TicksPerSecond;

    /// <summary>
    /// COUNTABLE (a): the node visit order, observed from the aircraft's own
    /// position rather than from the field under test.
    /// </summary>
    /// <remarks>
    /// The visited node is identified by asking which authored point the
    /// aircraft is inside the arrival radius of at the moment the cursor moves.
    /// That reads <c>Points</c> — the serialized list — and the plane's pose,
    /// and never reads <c>TargetChainNodeIndices</c>. So the assertion is not
    /// the chain restated: it is where the aeroplane actually went.
    /// </remarks>
    [Fact]
    public void AirTrainer_VisitsFlybyPathNodesInAuthoredChainOrder()
    {
        Assert.Equal([41, 42, 43], FlyTheAuthoredRoute().Visited);
    }

    /// <summary>
    /// COUNTABLE (b): the altitude profile of the first leg. Once airborne the
    /// aircraft makes no ground contact and settles into the released level
    /// band, rather than descending toward the ground-level node.
    /// </summary>
    /// <remarks>
    /// <para>
    /// <b>What this test does NOT say, and why.</b> The recorded defect for
    /// #146 read "flies its authored route backwards, beginning with a dive
    /// into the ground", and the second half of that is <i>not</i> what the
    /// simulation does. It was read off the DATA — the serialized head, node
    /// 43, is the only <c>Flyby Path</c> node at ground level — and never
    /// measured. A Level 100 plane's pitch does not come from its waypoint at
    /// all: <c>Level100ActorMechanics.TryGetPlaneGuideTarget</c> hands the
    /// guide the node's X and Z only, and <c>PlaneDesiredPitch</c> is a pure
    /// function of terrain clearance, which is the released
    /// <c>CAirGuide::VFunc03</c> clearance band at <c>0x0040240d</c>. So the
    /// aircraft never steers at node 43's altitude in either order, and the
    /// wrong order does not produce a dive.
    /// </para>
    /// <para>
    /// <b>What the measurement did turn up.</b> The aircraft starts BELOW the
    /// terrain, by 3,840 mm, in both orders — its authored Y of −15,000 mm sits
    /// under a terrain sample of −11,160 mm at its own authored X/Z. That is a
    /// separate, pre-existing vertical-datum defect: the manifest carries
    /// retail's z-DOWN altitude verbatim into Core's y-UP frame, so the two
    /// ambient aircraft (and only they, being the only actors with a non-zero
    /// authored altitude) are placed underground. It is identical either side
    /// of the traversal fix, so it is emphatically not the ordering bug, and it
    /// is deliberately NOT papered over here with a clamp: the authored data is
    /// the authority, and hiding a datum error inside this lane would put a
    /// second wrong answer on top of a first one.
    /// </para>
    /// <para>
    /// That defect is already on the books - it is the <c>_actor_pose</c>
    /// vertical datum item owned by
    /// <c>local-lab/TARGET-CONTACT-GEOMETRY-2026-07-26.md</c>, recorded there as
    /// bigger than first reported and not repairable by the fix specified for
    /// it. The same underground-then-climb-out shape was measured for the
    /// SPAWNED Air Trainer on 2026-07-26
    /// (<c>local-lab/PLANE-MOTION-AND-ACTOR-WEAPONS-2026-07-26.md</c> §2.3: spawn
    /// clearance −6,133 mm, climbing out by t150), so this is a known pattern
    /// rather than a new symptom. The same section is why the "dive" reading
    /// above cannot be right: <i>"There is no altitude hold and no setpoint"</i>
    /// - the clearance band is the only altitude authority a plane has.
    /// </para>
    /// <para>
    /// What is asserted, therefore, is the part that is about flight: after the
    /// released climb response lifts it out, the aircraft clears the terrain for
    /// the whole remainder of the first leg and is inside the level band, so
    /// nothing in the corrected route flies it into the deck.
    /// </para>
    /// </remarks>
    [Fact]
    public void AirTrainer_ClearsTheGroundOnceAirborneAlongTheFirstLeg()
    {
        FlightProfile authored = FlyTheAuthoredRoute();

        Assert.True(
            authored.FirstLegTicks > 0,
            "the aircraft never reached the first node, so there is no first leg to measure");
        Assert.True(
            authored.ClimbedOutAtTick > 0,
            "the aircraft never climbed clear of the terrain at all");
        Assert.True(
            authored.MinimumClearanceAfterClimb > 0,
            $"the Air Trainer touched the terrain {authored.MinimumClearanceAfterClimb} mm " +
            "into it after it had already climbed clear, on the first leg of its " +
            "corrected route.");
        Assert.InRange(
            authored.MinimumClearanceAfterClimb,
            SimulationConstants.Level100PlaneClimbClearanceMillimeters,
            SimulationConstants.Level100PlaneDiveClearanceMillimeters);

        // The datum defect named in the remarks, pinned so that fixing it is
        // visible here rather than silent, and so that this test cannot be read
        // as evidence that it does not exist.
        Assert.Equal(-3_840, authored.ClearanceAtSpawn);
        Assert.Equal(
            authored.ClearanceAtSpawn,
            FlyTheAuthoredRoute(SerializedOrderAsChain).ClearanceAtSpawn);
    }

    /// <summary>
    /// The mutation proof for both tests above, kept as a test so it cannot rot:
    /// re-introducing the defect - steering at <c>Points[cursor]</c> instead of
    /// <c>ChainPoint(cursor)</c> - produces a DIFFERENT visit order.
    /// </summary>
    /// <remarks>
    /// The reversal is re-introduced here by handing the mechanics a definition
    /// set whose chain has been overwritten with the serialized order, which is
    /// exactly the state the product was in before #146. If someone reverts
    /// <c>ChainPoint</c> back to <c>Points</c> indexing, this test and
    /// <see cref="AirTrainer_VisitsFlybyPathNodesInAuthoredChainOrder"/> assert
    /// the same sequence and this one fails.
    /// </remarks>
    [Fact]
    public void ReintroducingTheReversal_ChangesTheVisitOrder()
    {
        int[] authored = FlyTheAuthoredRoute().Visited;
        int[] reversed = FlyTheAuthoredRoute(SerializedOrderAsChain).Visited;

        _output.WriteLine($"authored chain visit order: [{string.Join(", ", authored)}]");
        _output.WriteLine($"serialized-order visit order: [{string.Join(", ", reversed)}]");
        Assert.NotEqual(authored, reversed);
        Assert.Equal([43, 42, 41], reversed);
    }

    /// <summary>
    /// A chain that closes on its own head never ends, so the follower wraps
    /// instead of completing.
    /// </summary>
    /// <remarks>
    /// <para>
    /// Two of the eight Level 100 paths close - <c>Drone Path 1</c> and
    /// <c>Target Tank Path 2</c> - and until #146 nothing read
    /// <c>isClosed</c> at all, so both were walked once and abandoned.
    /// </para>
    /// <para>
    /// This is not a design choice, it is what the released cursor cannot avoid
    /// doing. <c>CScriptEventNB::UpdateWaypointFollowing</c> (<c>0x00538470</c>,
    /// pristine specimen sha256 <c>74154BFA…</c>) ends the walk on exactly one
    /// condition: the successor it loaded from <c>[current+0x3c]</c> is NULL
    /// (<c>mov eax,[esi+0x14]</c> / <c>cmp eax,edi</c> at <c>0x00538500</c>
    /// with <c>edi</c> zero). When the tail's successor is the head there is no
    /// NULL on the ring, so the completion path is unreachable.
    /// </para>
    /// <para>
    /// Driven by parking the aircraft on whatever node it is currently steering
    /// at, rather than flying the ring, because what is under test is the cursor
    /// and not the aerodynamics. Note it re-parks on EVERY core tick: arrivals
    /// are only observed on released base ticks, which fire 20 times per 30 core
    /// ticks, so "one tick per node" would be wrong.
    /// </para>
    /// </remarks>
    [Fact]
    public void ClosedChain_WrapsToItsHeadInsteadOfCompleting()
    {
        Level100WaypointPathDefinition path;
        (int[] visited, var completions, var final) = WalkByTeleport("Drone Path 1", out path);

        Assert.True(path.IsClosed);
        Assert.Equal([1, 2, 3, 4], path.TargetChainNodeIndices);

        // Round the ring and past the seam, twice over: 1,2,3,4,1,2,3,4...
        Assert.Equal(
            [1, 2, 3, 4, 1, 2, 3, 4, 1],
            visited.Take(9));

        // No wait completion is ever raised, even though the command was
        // FollowWaypointWait: the ring has no end to report.
        Assert.Empty(completions);
        Assert.Equal(Level100ActorCommandIntent.FollowingWaypoint, final.Intent);
        Assert.Equal(path.Name, final.WaypointPath);
    }

    /// <summary>
    /// The contrast that makes the test above mean something: an OPEN chain
    /// still completes, exactly once, and still reports its wait.
    /// </summary>
    [Fact]
    public void OpenChain_StillCompletesAtItsTail()
    {
        Level100WaypointPathDefinition path;
        (int[] visited, var completions, var final) = WalkByTeleport("Flyby Path", out path);

        Assert.False(path.IsClosed);
        Assert.Equal([41, 42, 43], visited);

        Level100ActorMechanicsWaitCompletion completion = Assert.Single(completions);
        Assert.Equal(path.Name, completion.Argument);
        Assert.Equal(Level100ActorScriptWaitKind.FollowWaypoint, completion.WaitKind);
        Assert.Equal(Level100ActorCommandIntent.Stopped, final.Intent);
    }

    /// <summary>
    /// Walks a path by repeatedly teleporting the follower onto the node its
    /// cursor currently names, and records the node index each time the cursor
    /// moves. Stops early once the follower leaves FollowingWaypoint.
    /// </summary>
    private (int[] Visited,
        IReadOnlyList<Level100ActorMechanicsWaitCompletion> Completions,
        Level100ActorCommandIntentSnapshot Final)
        WalkByTeleport(string pathName, out Level100WaypointPathDefinition path)
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        var mechanics = new Level100ActorMechanics(actors, definitions);
        Level100ActorId trainer = actors.GetThingRef("Air Trainer")!.Value;
        path = definitions.GetWaypointPath(pathName);

        mechanics.ApplyCommand(new Level100ActorScriptCommand(
            1,
            0,
            trainer,
            Level100ActorScriptCommandKind.FollowWaypointWait,
            null,
            pathName,
            0));

        Level100ActorCommandIntentSnapshot State() =>
            mechanics.Snapshot.Actors.Single(actor => actor.ActorId == trainer);

        var visited = new List<int>();
        var completions = new List<Level100ActorMechanicsWaitCompletion>();
        int cursor = 0;
        // Three core ticks per base tick is the worst case, and nine laps of the
        // longest path is more headroom than any assertion here needs.
        int budget = 9 * 3 * (path.TargetChainNodeIndices.Count + 1);
        for (int tick = 0; tick < budget; tick++)
        {
            Level100ActorCommandIntentSnapshot before = State();
            if (before.Intent != Level100ActorCommandIntent.FollowingWaypoint)
            {
                break;
            }

            actors.SetPose(
                trainer,
                actors.GetActor(trainer).Pose with
                {
                    PositionMillimeters =
                        path.ChainPoint(before.WaypointPointIndex).PositionMillimeters,
                });
            completions.AddRange(mechanics.AdvanceTick());

            Level100ActorCommandIntentSnapshot after = State();
            bool advanced =
                after.WaypointPointIndex != before.WaypointPointIndex ||
                after.Intent != Level100ActorCommandIntent.FollowingWaypoint;
            if (advanced)
            {
                // The node just reached is the one the cursor named going in.
                visited.Add(path.TargetChainNodeIndices[before.WaypointPointIndex]);
                cursor = after.WaypointPointIndex;
            }
        }

        _output.WriteLine(
            $"{pathName}: visited [{string.Join(", ", visited)}] " +
            $"completions={completions.Count} finalCursor={cursor}");
        return (visited.ToArray(), completions, State());
    }

    /// <summary>
    /// The pre-#146 definition set: every path's traversal chain replaced by its
    /// own serialized node order.
    /// </summary>
    private static Level100ActorDefinitionSet SerializedOrderAsChain(
        Level100ActorDefinitionSet definitions) =>
        new(
            definitions.Actors,
            definitions.Spawns,
            definitions.WaypointPaths
                .Select(path => new Level100WaypointPathDefinition(
                    path.Name,
                    path.Points,
                    path.Points.Select(point => point.NodeIndex).ToArray(),
                    path.IsClosed))
                .ToArray(),
            definitions.MotionDefinitions);

    /// <param name="Visited">
    /// The node indices the aircraft actually arrived at, in order.
    /// </param>
    /// <param name="ClearanceAtSpawn">
    /// Terrain clearance at the authored pose, before the first tick moves
    /// anything. Negative means the aircraft is authored underground.
    /// </param>
    /// <param name="ClimbedOutAtTick">
    /// The first core tick at which clearance reached the released climb
    /// threshold, or 0 if it never did.
    /// </param>
    /// <param name="MinimumClearanceAfterClimb">
    /// The smallest clearance held between that tick and the end of the first
    /// leg.
    /// </param>
    /// <param name="FirstLegTicks">Core ticks to the first arrival.</param>
    private readonly record struct FlightProfile(
        int[] Visited,
        int ClearanceAtSpawn,
        int ClimbedOutAtTick,
        int MinimumClearanceAfterClimb,
        int FirstLegTicks);

    private FlightProfile FlyTheAuthoredRoute(
        Func<Level100ActorDefinitionSet, Level100ActorDefinitionSet>? rewrite = null)
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        if (rewrite is not null)
        {
            definitions = rewrite(definitions);
        }

        var actors = new Level100ActorRegistry(definitions);
        var mechanics = new Level100ActorMechanics(actors, definitions);
        Level100ActorId trainer = actors.GetThingRef("Air Trainer")!.Value;
        Level100WaypointPathDefinition path = definitions.GetWaypointPath("Flyby Path");
        long arrivalRadius = definitions
            .GetMotionDefinition("Air Trainer").ArrivalRadiusMillimeters;

        actors.SetPose(
            trainer,
            actors.GetActor(trainer).Pose with
            {
                PositionMillimeters = AuthoredAirTrainerPosition,
                BasisFloatBits = AuthoredAirTrainerBasis,
                LinearVelocityMillimetersPerTick = SimVector3.Zero,
                AngularVelocityMicroRadiansPerTick = SimVector3.Zero,
            });
        mechanics.ApplyCommand(new Level100ActorScriptCommand(
            1,
            0,
            trainer,
            Level100ActorScriptCommandKind.FollowWaypoint,
            null,
            path.Name,
            0));

        int clearanceAtSpawn = Clearance(actors.GetActor(trainer).Pose);

        var visited = new List<int>();
        int cursor = 0;
        int climbedOutAtTick = 0;
        int minimumClearanceAfterClimb = int.MaxValue;
        int firstLegTicks = 0;
        for (int coreTick = 0; coreTick < FlightCoreTicks; coreTick++)
        {
            mechanics.AdvanceTick();
            Level100ActorCommandIntentSnapshot state =
                mechanics.Snapshot.Actors.Single(actor => actor.ActorId == trainer);
            Level100ActorPoseSnapshot pose = actors.GetActor(trainer).Pose;

            if (visited.Count == 0)
            {
                firstLegTicks = coreTick + 1;
                int clearance = Clearance(pose);
                if (climbedOutAtTick == 0 &&
                    clearance >=
                        SimulationConstants.Level100PlaneClimbClearanceMillimeters)
                {
                    climbedOutAtTick = coreTick + 1;
                }

                if (climbedOutAtTick > 0)
                {
                    minimumClearanceAfterClimb =
                        Math.Min(minimumClearanceAfterClimb, clearance);
                }
            }

            bool advanced = state.WaypointPointIndex != cursor;
            bool finished = state.Intent != Level100ActorCommandIntent.FollowingWaypoint;
            if (!advanced && !finished)
            {
                continue;
            }

            // Whichever authored node the aircraft is standing inside is the
            // one it just arrived at. Read from Points and the pose only.
            Level100WaypointPointDefinition[] inside = path.Points
                .Where(point =>
                {
                    long deltaX =
                        (long)point.PositionMillimeters.X - pose.PositionMillimeters.X;
                    long deltaZ =
                        (long)point.PositionMillimeters.Z - pose.PositionMillimeters.Z;
                    return (deltaX * deltaX) + (deltaZ * deltaZ) <
                        arrivalRadius * arrivalRadius;
                })
                .ToArray();
            visited.Add(Assert.Single(inside).NodeIndex);
            _output.WriteLine(
                $"tick {coreTick + 1}: arrived node {visited[^1]} at " +
                $"{pose.PositionMillimeters}");
            cursor = state.WaypointPointIndex;
            if (finished)
            {
                break;
            }
        }

        _output.WriteLine(
            $"visited [{string.Join(", ", visited)}]; first leg {firstLegTicks} core ticks; " +
            $"clearance at spawn {clearanceAtSpawn} mm; climbed clear at tick " +
            $"{climbedOutAtTick}; minimum clearance after that " +
            $"{minimumClearanceAfterClimb} mm");
        return new FlightProfile(
            visited.ToArray(),
            clearanceAtSpawn,
            climbedOutAtTick,
            minimumClearanceAfterClimb,
            firstLegTicks);
    }

    private static int Clearance(Level100ActorPoseSnapshot pose) =>
        pose.PositionMillimeters.Y -
        Level100Terrain.Instance.SampleGroundElevationMillimeters(
            new SimVector2(pose.PositionMillimeters.X, pose.PositionMillimeters.Z));
}
