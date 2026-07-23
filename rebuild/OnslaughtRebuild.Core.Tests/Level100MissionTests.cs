// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class Level100MissionTests
{
    private static readonly Level100TutorialProgress CompletedTutorialSlots =
        new(Introduction: true, PulseCannon: true, VulcanCannon: true, StatusBars: true);

    [Fact]
    public void ReleasedPrograms_InitializeAgainstOneCanonicalActorRegistry()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var actorScripts = new Level100ActorScriptRuntime(actors, player);
        actorScripts.InitializeReleasedScripts();
        var mission = new Level100Mission(
            actors,
            player,
            CompletedTutorialSlots,
            initialPlayerHealth: 735);

        Level100MissionSnapshot missionState = mission.Snapshot;
        Level100ActorScriptRuntimeSnapshot actorState = actorScripts.Snapshot;
        Assert.Equal(
            "73eb349b9c4b5c5d7294b2183cd4d4aebe024c5d3c8cda9be685bd1463ed6fb1",
            missionState.ProgramSha256);
        Assert.Equal(334, missionState.Locals.Count);
        Assert.False(missionState.FlightModeEnabled);
        Assert.Equal(735, missionState.InitialPlayerHealth);
        Assert.Contains(actorState.Instances, instance =>
            instance.ActorId is null && instance.ProgramName == "Setup");
        Assert.Contains(actorState.Instances, instance =>
            instance.ActorId == actors.GetThingRef("Player 1"));
        Assert.All(actorState.Instances, instance => Assert.True(instance.Initialized));
    }

    [Fact]
    public void ActorRuntimeSnapshot_RoundTripsAndChangesCanonicalWorldHash()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var runtime = new Level100ActorScriptRuntime(actors, player);
        runtime.InitializeReleasedScripts();
        Level100ActorScriptRuntimeSnapshot snapshot = runtime.Snapshot;

        var restored = new Level100ActorScriptRuntime(actors, player, snapshot);
        WorldSnapshot envelope = new Simulation(0x100u, definitions).Snapshot;
        string originalHash = StateHasher.ComputeHex(envelope with
        {
            Level100Actors = actors.Snapshot,
            Level100ActorScripts = snapshot,
        });
        string restoredHash = StateHasher.ComputeHex(envelope with
        {
            Level100Actors = actors.Snapshot,
            Level100ActorScripts = restored.Snapshot,
        });
        Assert.Equal(originalHash, restoredHash);

        int changedInstanceIndex = snapshot.Instances
            .Select((instance, index) => (instance, index))
            .First(item => item.instance.Locals.Count > 0)
            .index;
        Level100ActorScriptInstanceSnapshot source = snapshot.Instances[changedInstanceIndex];
        Level100ScriptLocalSnapshot local = source.Locals[0];
        Level100ScriptValueSnapshot changedValue = local.Value with
        {
            Scalar = unchecked(local.Value.Scalar + 1),
        };
        Level100ActorScriptInstanceSnapshot changedInstance = source with
        {
            Locals = source.Locals
                .Select((item, index) => index == 0 ? item with { Value = changedValue } : item)
                .ToArray(),
        };
        Level100ActorScriptRuntimeSnapshot changed = snapshot with
        {
            Instances = snapshot.Instances
                .Select((item, index) => index == changedInstanceIndex ? changedInstance : item)
                .ToArray(),
        };
        Assert.NotEqual(originalHash, StateHasher.ComputeHex(envelope with
        {
            Level100Actors = actors.Snapshot,
            Level100ActorScripts = changed,
        }));

        Level100ActorScriptRuntimeSnapshot wrongProgram = snapshot with
        {
            Instances = snapshot.Instances
                .Select((item, index) => index == 0
                    ? item with { ProgramSha256 = new string('0', 64) }
                    : item)
                .ToArray(),
        };
        Assert.Throws<ArgumentException>(() =>
            new Level100ActorScriptRuntime(actors, player, wrongProgram));

        Level100ActorScriptInstanceSnapshot waiting = snapshot.Instances.First(instance =>
            instance.Continuations.Count > 0);
        Level100ActorScriptRuntimeSnapshot activeExecution = snapshot with
        {
            Instances = snapshot.Instances
                .Select(instance => ReferenceEquals(instance, waiting)
                    ? instance with
                    {
                        ActiveExecution = instance.Continuations[0].Execution,
                    }
                    : instance)
                .ToArray(),
        };
        Assert.Throws<ArgumentException>(() =>
            new Level100ActorScriptRuntime(actors, player, activeExecution));
    }

    [Fact]
    public void TargetTank1_StopsAtTheReleasedWaypointMechanicsBoundary()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var runtime = new Level100ActorScriptRuntime(actors, player);
        runtime.InitializeReleasedScripts();
        Level100ActorSnapshot target = actors.Snapshot.Actors.Single(actor =>
            actor.TargetGroup == Level100MissionTargetGroup.StaticTargets &&
            actor.TargetOrdinal == 1);

        Assert.Equal("test:spawn:test:tank-factory:Target Tank:SpawnerA:TargetTank1",
            target.DefinitionIdentity);
        Assert.Equal("Target Tank", target.DefinitionName);
        Assert.Equal("TargetTank1", target.ScriptName);
        Assert.Equal("SpawnerA", target.SpawnerName);
        Assert.Equal(actors.GetThingRef("Tank Factory"), target.SpawnOwnerId);
        Assert.Equal(new SimVector3(3_439, -126, 21_051), target.Pose!.PositionMillimeters);
        Assert.Equal(
            new Level100FloatBasis3Bits(
                -1_101_128_975, 0, -1_082_529_832,
                0, 1_065_353_216, 0,
                1_064_953_816, 0, -1_101_128_975),
            target.Pose.BasisFloatBits);

        Level100ActorScriptCommand command = Assert.Single(runtime.DrainCommands(), item =>
            item.ActorId == target.ActorId &&
            item.Kind == Level100ActorScriptCommandKind.FollowWaypointWait);
        Assert.Equal(target.ActorId, command.ActorId);
        Assert.Equal(Level100ActorScriptCommandKind.FollowWaypointWait, command.Kind);
        Assert.Equal("Target Tank Path 1", command.Argument);
        Level100ActorScriptInstanceSnapshot instance = runtime.Snapshot.Instances.Single(
            item => item.ActorId == target.ActorId);
        Level100ActorScriptContinuationSnapshot continuation = Assert.Single(
            instance.Continuations);
        Assert.Equal(Level100ActorScriptWaitKind.FollowWaypoint, continuation.WaitKind);
        Assert.Equal("Target Tank Path 1", continuation.WaitArgument);
        Assert.Null(continuation.DueTick);
    }

    [Fact]
    public void ExternalTerminalFacts_StopTheReleasedLevelScriptOnce()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var deathActors = new Level100ActorRegistry(definitions);
        var death = new Level100Mission(
            deathActors,
            deathActors.GetThingRef("Player 1")!.Value,
            CompletedTutorialSlots);
        Assert.True(death.ReportPlayerDeath());
        Assert.False(death.ReportWaterLoss());
        Assert.Equal(Level100MissionFailureReason.PlayerDeath, death.Snapshot.FailureReason);

        var waterActors = new Level100ActorRegistry(definitions);
        var water = new Level100Mission(
            waterActors,
            waterActors.GetThingRef("Player 1")!.Value,
            CompletedTutorialSlots);
        Assert.True(water.ReportWaterLoss());
        Assert.False(water.SubmitInput(Level100MissionInput.BrokeTutorial));
        Assert.Equal(Level100MissionFailureReason.WaterLoss, water.Snapshot.FailureReason);
    }
}
