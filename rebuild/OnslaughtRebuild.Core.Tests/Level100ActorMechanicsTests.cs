// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class Level100ActorMechanicsTests
{
    [Fact]
    public void GroundVehicle_AdvancesAtRetailCadenceAndUsesCoreGroundOriginOffset()
    {
        Level100ActorDefinitionSet definitions =
            Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player =
            actors.GetThingRef("Player 1")!.Value;
        var scripts =
            new Level100ActorScriptRuntime(actors, player);
        var mechanics =
            new Level100ActorMechanics(actors, definitions);

        scripts.InitializeReleasedScripts();
        Level100ActorScriptCommand[] commands =
            scripts.DrainCommands().ToArray();
        mechanics.ConsumeCommands(commands);
        Level100ActorSnapshot target =
            actors.Snapshot.Actors.Single(actor =>
                actor.ScriptName == "TargetTank1");
        Level100ActorPoseSnapshot emitterPose = target.Pose;
        Level100ActorCommandIntentSnapshot intent =
            Assert.Single(
                mechanics.Snapshot.Actors,
                item => item.ActorId == target.ActorId);
        Assert.Equal(
            Level100ActorCommandIntent.FollowingWaypoint,
            intent.Intent);
        Assert.Equal("Target Tank Path 1", intent.WaypointPath);
        Assert.True(intent.WaitForWaypointCompletion);
        Assert.Equal(0, intent.GroundFullGuideBaseTickPhase);
        Assert.Equal(
            commands.Max(command => command.Sequence),
            mechanics.Snapshot.LastConsumedCommandSequence);

        // EVERY Core tick is a released base tick since the 20 Hz migration.
        // This assertion used to interleave two skipped ticks - the 30 Hz Core
        // ran the base frame on 20 ticks of every 30 and zeroed the reported
        // velocity on the other 10 - and the skipped arms are gone with the
        // accumulator. What remains, and is the real released cadence, is the
        // ground guide's own `FullGuideBaseTicks` = 4 phase: the guide reaims
        // on phase 0 and coasts on the other three.
        Assert.Empty(mechanics.AdvanceTick());
        Level100ActorPoseSnapshot fullUpdate =
            actors.GetActor(target.ActorId).Pose;
        Assert.NotEqual(
            emitterPose.PositionMillimeters,
            fullUpdate.PositionMillimeters);
        Assert.Equal(
            1,
            mechanics.Snapshot.Actors.Single(item =>
                item.ActorId == target.ActorId)
                .GroundFullGuideBaseTickPhase);
        Assert.NotEqual(
            SimVector3.Zero,
            fullUpdate.AngularVelocityMicroRadiansPerTick);
        Assert.Equal(
            Level100Terrain.Instance.SampleGroundElevationMillimeters(
                new SimVector2(
                    fullUpdate.PositionMillimeters.X,
                    fullUpdate.PositionMillimeters.Z)) +
                100,
            fullUpdate.PositionMillimeters.Y);
        Assert.NotEqual(
            definitions.GetWaypointPath("Target Tank Path 1")
                .Points[0].PositionMillimeters.Y,
            fullUpdate.PositionMillimeters.Y);

        // Phases 1, 2 and 3: the vehicle keeps moving but the guide does not
        // reaim, so the angular velocity is zero on all three.
        Level100ActorPoseSnapshot previous = fullUpdate;
        for (int phase = 1; phase <= 3; phase++)
        {
            Assert.Empty(mechanics.AdvanceTick());
            Level100ActorPoseSnapshot coasting =
                actors.GetActor(target.ActorId).Pose;
            Assert.NotEqual(
                previous.PositionMillimeters,
                coasting.PositionMillimeters);
            Assert.NotEqual(
                SimVector3.Zero,
                coasting.LinearVelocityMillimetersPerTick);
            Assert.Equal(
                SimVector3.Zero,
                coasting.AngularVelocityMicroRadiansPerTick);
            Assert.Equal(
                (phase + 1) % 4,
                mechanics.Snapshot.Actors.Single(item =>
                    item.ActorId == target.ActorId)
                    .GroundFullGuideBaseTickPhase);
            previous = coasting;
        }

        // Back to phase 0, and the guide reaims again.
        Assert.Empty(mechanics.AdvanceTick());
        Assert.NotEqual(
            SimVector3.Zero,
            actors.GetActor(target.ActorId).Pose
                .AngularVelocityMicroRadiansPerTick);
    }

    [Fact]
    public void GroundVehicle_CoreVelocityMatchesEachTickAndSumsToNormalSpeed()
    {
        Level100ActorDefinitionSet definitions =
            Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        var mechanics =
            new Level100ActorMechanics(actors, definitions);
        Level100ActorId factory =
            actors.GetThingRef("Tank Factory")!.Value;
        Level100ActorId target = Assert.Single(
            actors.SpawnThing(
                factory,
                "Target Tank",
                "SpawnerA",
                1,
                "TargetTank1"));
        // The first node of the TRAVERSAL, not of the serialized list. The tank
        // is parked on that node's X and pointed down +Z so the leg is a
        // straight run with no lateral component, which is what makes the
        // `displacement.X == 0` assertion below a speed measurement rather than
        // a turn measurement. `Target Tank Path 1` serializes [18, 6, 7] and is
        // walked [6, 7, 18], so aligning on `Points[0]` (node 18) would aim the
        // tank at a node it visits LAST and the run would curve.
        Level100WaypointPathDefinition route =
            definitions.GetWaypointPath("Target Tank Path 1");
        Level100WaypointPointDefinition destination = route.ChainPoint(0);
        int initialZ = 0;
        int initialY =
            Level100Terrain.Instance.SampleGroundElevationMillimeters(
                new SimVector2(
                    destination.PositionMillimeters.X,
                    initialZ)) +
            100;
        Level100ActorPoseSnapshot aligned =
            actors.GetActor(target).Pose with
            {
                PositionMillimeters = new SimVector3(
                    destination.PositionMillimeters.X,
                    initialY,
                    initialZ),
                BasisFloatBits = IdentityBasis(),
                LinearVelocityMillimetersPerTick =
                    SimVector3.Zero,
                AngularVelocityMicroRadiansPerTick =
                    SimVector3.Zero,
            };
        actors.SetPose(target, aligned);
        mechanics.ApplyCommand(Command(
            1,
            target,
            Level100ActorScriptCommandKind.FollowWaypoint,
            argument: "Target Tank Path 1"));

        // One released second. Every Core tick is a released base tick, so the
        // vehicle moves on all of them; before the 20 Hz migration this loop
        // had to predict which 20 of 30 ticks would move and assert that the
        // reported velocity was zeroed on the other 10.
        int movingCoreTicks = 0;
        int totalZ = 0;
        for (int coreTick = 0;
             coreTick < SimulationConstants.TicksPerSecond;
             coreTick++)
        {
            Level100ActorPoseSnapshot before =
                actors.GetActor(target).Pose;

            Assert.Empty(mechanics.AdvanceTick());
            Level100ActorPoseSnapshot after =
                actors.GetActor(target).Pose;
            var displacement = new SimVector3(
                after.PositionMillimeters.X -
                    before.PositionMillimeters.X,
                after.PositionMillimeters.Y -
                    before.PositionMillimeters.Y,
                after.PositionMillimeters.Z -
                    before.PositionMillimeters.Z);
            Assert.Equal(
                displacement,
                after.LinearVelocityMillimetersPerTick);
            movingCoreTicks++;
            totalZ += displacement.Z;
            Assert.Equal(0, displacement.X);
            Assert.Equal(175, displacement.Z);
            Assert.Equal(
                Level100Terrain.Instance
                    .SampleGroundElevationMillimeters(
                        new SimVector2(
                            after.PositionMillimeters.X,
                            after.PositionMillimeters.Z)) +
                    100,
                after.PositionMillimeters.Y);
        }

        // Unchanged where it counts: 20 moving updates in a released second,
        // and 3.5 released units of ground covered. That total is the actual
        // parity claim, and the migration must not move it.
        Assert.Equal(20, movingCoreTicks);
        Assert.Equal(3_500, totalZ);
    }

    [Fact]
    public void CommandIntent_IsActorSortedSequenceStrictAndStopPreservesFullPose()
    {
        Level100ActorDefinitionSet definitions =
            Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        var mechanics =
            new Level100ActorMechanics(actors, definitions);
        Level100ActorId factory =
            actors.GetThingRef("Tank Factory")!.Value;
        Level100ActorId player =
            actors.GetThingRef("Player 1")!.Value;
        Level100ActorId target = Assert.Single(
            actors.SpawnThing(
                factory,
                "Target Tank",
                "SpawnerA",
                1,
                "TargetTank1"));
        Level100ActorPoseSnapshot moving =
            actors.GetActor(target).Pose with
            {
                LinearVelocityMillimetersPerTick =
                    new SimVector3(4, 5, 6),
                AngularVelocityMicroRadiansPerTick =
                    new SimVector3(7, 8, 9),
            };
        actors.SetPose(target, moving);

        mechanics.ConsumeCommands(
        [
            Command(10, target,
                Level100ActorScriptCommandKind.SetAIState,
                scalar: 3),
            Command(20, target,
                Level100ActorScriptCommandKind.Print,
                argument: "retained but not mechanics-owned"),
            Command(30, target,
                Level100ActorScriptCommandKind.SetAllegiance,
                scalar: 2),
            Command(40, target,
                Level100ActorScriptCommandKind.Attack,
                targetActorId: player),
        ]);
        Level100ActorCommandIntentSnapshot attacking =
            Assert.Single(mechanics.Snapshot.Actors);
        Assert.Equal(3, attacking.AiState);
        Assert.Equal(2, attacking.Allegiance);
        Assert.Equal(
            Level100ActorCommandIntent.Attacking,
            attacking.Intent);
        Assert.Equal(player, attacking.TargetActorId);
        Assert.Equal(
            40,
            mechanics.Snapshot.LastConsumedCommandSequence);
        Assert.Equal(
            SimVector3.Zero,
            actors.GetActor(target).Pose
                .LinearVelocityMillimetersPerTick);
        Assert.Equal(
            SimVector3.Zero,
            actors.GetActor(target).Pose
                .AngularVelocityMicroRadiansPerTick);

        actors.SetPose(target, moving);
        Assert.Empty(mechanics.AdvanceTick());
        Assert.Equal(
            SimVector3.Zero,
            actors.GetActor(target).Pose
                .LinearVelocityMillimetersPerTick);
        actors.SetPose(target, moving);
        Assert.Empty(mechanics.AdvanceTick());
        Assert.Equal(
            SimVector3.Zero,
            actors.GetActor(target).Pose
                .LinearVelocityMillimetersPerTick);

        actors.SetPose(target, moving);
        mechanics.ApplyCommand(Command(
            50,
            target,
            Level100ActorScriptCommandKind.Retreat));
        Assert.Equal(
            SimVector3.Zero,
            actors.GetActor(target).Pose
                .LinearVelocityMillimetersPerTick);
        Assert.Equal(
            SimVector3.Zero,
            actors.GetActor(target).Pose
                .AngularVelocityMicroRadiansPerTick);
        mechanics.ApplyCommand(Command(
            60,
            target,
            Level100ActorScriptCommandKind.FollowWaypoint,
            argument: "Target Tank Path 2",
            scalar: 17));
        Level100ActorCommandIntentSnapshot following =
            Assert.Single(mechanics.Snapshot.Actors);
        Assert.Equal(
            Level100ActorCommandIntent.FollowingWaypoint,
            following.Intent);
        Assert.Equal(17, following.WaypointCommandScalar);
        Assert.False(following.WaitForWaypointCompletion);

        Level100ActorPoseSnapshot pose =
            actors.GetActor(target).Pose with
            {
                PositionMillimeters =
                    new SimVector3(101, 202, 303),
                LinearVelocityMillimetersPerTick =
                    new SimVector3(4, 5, 6),
                AngularVelocityMicroRadiansPerTick =
                    new SimVector3(7, 8, 9),
            };
        actors.SetPose(target, pose);
        mechanics.ApplyCommand(Command(
            70,
            target,
            Level100ActorScriptCommandKind.Stop));

        Level100ActorPoseSnapshot stopped =
            actors.GetActor(target).Pose;
        Assert.Equal(
            pose.PositionMillimeters,
            stopped.PositionMillimeters);
        Assert.Equal(
            pose.BasisFloatBits,
            stopped.BasisFloatBits);
        Assert.Equal(
            SimVector3.Zero,
            stopped.LinearVelocityMillimetersPerTick);
        Assert.Equal(
            SimVector3.Zero,
            stopped.AngularVelocityMicroRadiansPerTick);
        Assert.Throws<InvalidOperationException>(() =>
            mechanics.ApplyCommand(Command(
                70,
                player,
                Level100ActorScriptCommandKind.Stop)));

        mechanics.ApplyCommand(Command(
            80,
            player,
            Level100ActorScriptCommandKind.Stop));
        Assert.Equal(
            mechanics.Snapshot.Actors.OrderBy(
                item => item.ActorId.Value),
            mechanics.Snapshot.Actors);

        Assert.Empty(mechanics.AdvanceTick());
        Level100ActorMechanicsSnapshot snapshot =
            mechanics.Snapshot;
        var restored = new Level100ActorMechanics(
            actors,
            definitions,
            snapshot);
        Assert.Equal(
            snapshot.LastConsumedCommandSequence,
            restored.Snapshot.LastConsumedCommandSequence);
        Assert.Equal(
            snapshot.Actors,
            restored.Snapshot.Actors);
    }

    /// <summary>
    /// The released dropship arrival radius, and the fact that the comparison
    /// is strict.
    /// </summary>
    /// <remarks>
    /// <para>
    /// <b>This test used to be called
    /// <c>…UsesStrictClassRadiusAndRetainsDuplicateNodes</c> and asserted a
    /// DEFECT as retail truth.</b> It opened by asserting that
    /// <c>Transporter Path</c>'s first two nodes hold the same position, and the
    /// fixture comment called that "its released duplicate leading node". There
    /// is no duplicate. It was an aliasing artefact of the materializer
    /// resolving waypoint node indices against the 121-entry navigation graph
    /// instead of the 30 RLWD thingType-18 marker records, which collapsed all
    /// 30 nodes onto 11 positions (<c>58d9ce57</c>). Nodes 44 and 22 are
    /// 116.26 m apart horizontally.
    /// </para>
    /// <para>
    /// The half that was real is kept: <c>ObserveWaypointArrival</c> requires
    /// <c>distance &lt; radius</c>, not <c>&lt;=</c>, so a dropship sitting at
    /// exactly 8,000 mm has not arrived.
    /// </para>
    /// </remarks>
    [Fact]
    public void TransporterArrival_UsesTheStrictReleasedClassRadius()
    {
        Level100ActorDefinitionSet definitions =
            Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        var mechanics =
            new Level100ActorMechanics(actors, definitions);
        Level100ActorId transporter =
            actors.GetThingRef("Transporter")!.Value;
        Level100WaypointPathDefinition path =
            definitions.GetWaypointPath("Transporter Path");
        Assert.NotEqual(
            path.Points[0].PositionMillimeters,
            path.Points[1].PositionMillimeters);
        // The cursor walks the authored `target` chain, so step 0 of the
        // traversal is node 22 - the chain head - not node 44, which the level
        // file happens to serialize first and the chain visits LAST.
        Assert.Equal([44, 22, 23], path.Points.Select(point => point.NodeIndex));
        Assert.Equal([22, 23, 44], path.TargetChainNodeIndices);
        Assert.Equal(22, path.ChainPoint(0).NodeIndex);
        Assert.Equal(
            8_000,
            definitions
                .GetMotionDefinition("U-17 Highside Transporter")
                .ArrivalRadiusMillimeters);

        mechanics.ApplyCommand(Command(
            1,
            transporter,
            Level100ActorScriptCommandKind.FollowWaypointWait,
            argument: path.Name));
        Level100ActorPoseSnapshot pose =
            actors.GetActor(transporter).Pose with
            {
                PositionMillimeters = new SimVector3(
                    path.ChainPoint(0).PositionMillimeters.X +
                        8_000,
                    -12_345,
                    path.ChainPoint(0).PositionMillimeters.Z),
            };
        actors.SetPose(transporter, pose);

        Assert.Empty(mechanics.AdvanceTick());
        Assert.Equal(
            0,
            Assert.Single(mechanics.Snapshot.Actors)
                .WaypointPointIndex);
        Assert.Empty(mechanics.AdvanceTick());
        Assert.Equal(
            0,
            Assert.Single(mechanics.Snapshot.Actors)
                .WaypointPointIndex);
        Assert.Equal(pose, actors.GetActor(transporter).Pose);

        pose = pose with
        {
            PositionMillimeters =
                pose.PositionMillimeters with
                {
                    X =
                        path.ChainPoint(0).PositionMillimeters.X +
                        7_999,
                },
        };
        actors.SetPose(transporter, pose);
        Assert.Empty(mechanics.AdvanceTick());
        Assert.Equal(
            1,
            Assert.Single(mechanics.Snapshot.Actors)
                .WaypointPointIndex);

        // ...and it stops there. Under the aliased table both of the base ticks
        // below advanced the cursor again, because node 22 held node 44's
        // coordinates and the dropship was therefore already "at" it. On the
        // corrected route node 22 is 116.26 m away, so one arrival advances the
        // cursor exactly one node.
        Assert.Empty(mechanics.AdvanceTick());
        Assert.Equal(
            1,
            Assert.Single(mechanics.Snapshot.Actors)
                .WaypointPointIndex);
        Assert.Empty(mechanics.AdvanceTick());
        Assert.Equal(
            1,
            Assert.Single(mechanics.Snapshot.Actors)
                .WaypointPointIndex);

        // Dropship movement is not implemented - the class identity and radius
        // are retained evidence only - so the pose is still exactly where the
        // test put it.
        Assert.Equal(pose, actors.GetActor(transporter).Pose);
    }

    /// <summary>
    /// The canonical hash still covers the command cursor and the ground
    /// guide's phase.
    /// </summary>
    /// <remarks>
    /// This test used to cover a third field,
    /// <c>RetailBaseTickAccumulatorThirtieths</c>. That field was the
    /// 20-of-every-30 base-tick accumulator, and the 20 Hz migration deleted it
    /// because a Core tick now IS a released base tick. Its removal is one of
    /// the reasons every pinned hash moved in that change, independently of any
    /// trajectory - see <c>StateHasher</c> version 34.
    /// </remarks>
    [Fact]
    public void CanonicalHash_RetainsCommandCursorAndGuidePhase()
    {
        var simulation = new Simulation(
            0xA100u,
            Level100TestActorDefinitions.Create());
        WorldSnapshot snapshot = simulation.Snapshot;
        Level100ActorCommandIntentSnapshot following =
            Assert.Single(
                snapshot.Level100ActorMechanics.Actors,
                item =>
                    item.Intent ==
                    Level100ActorCommandIntent.FollowingWaypoint);

        WorldSnapshot changedCursor = snapshot with
        {
            Level100ActorMechanics =
                snapshot.Level100ActorMechanics with
                {
                    LastConsumedCommandSequence =
                        snapshot.Level100ActorMechanics
                            .LastConsumedCommandSequence + 1,
                },
        };
        WorldSnapshot changedPhase = snapshot with
        {
            Level100ActorMechanics =
                snapshot.Level100ActorMechanics with
                {
                    Actors = Array.AsReadOnly(
                        snapshot.Level100ActorMechanics.Actors
                            .Select(item =>
                                item.ActorId == following.ActorId
                                    ? item with
                                    {
                                        GroundFullGuideBaseTickPhase =
                                            item.GroundFullGuideBaseTickPhase +
                                            1,
                                    }
                                    : item)
                            .ToArray()),
                },
        };

        string canonical =
            StateHasher.ComputeHex(snapshot);
        Assert.NotEqual(
            canonical,
            StateHasher.ComputeHex(changedCursor));
        Assert.NotEqual(
            canonical,
            StateHasher.ComputeHex(changedPhase));
    }

    private static Level100ActorScriptCommand Command(
        long sequence,
        Level100ActorId actorId,
        Level100ActorScriptCommandKind kind,
        Level100ActorId? targetActorId = null,
        string? argument = null,
        int scalar = 0) => new(
            sequence,
            0,
            actorId,
            kind,
            targetActorId,
            argument,
            scalar);

    private static Level100FloatBasis3Bits IdentityBasis() => new(
        BitConverter.SingleToInt32Bits(1f), 0, 0,
        0, BitConverter.SingleToInt32Bits(1f), 0,
        0, 0, BitConverter.SingleToInt32Bits(1f));
}
