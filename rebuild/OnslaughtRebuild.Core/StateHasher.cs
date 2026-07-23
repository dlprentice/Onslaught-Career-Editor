// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text;

namespace OnslaughtRebuild.Core;

public static class StateHasher
{
    private static readonly byte[] s_magic = Encoding.ASCII.GetBytes("ONSLAUGHT-REBUILD-STATE");

    public static string ComputeHex(WorldSnapshot state)
    {
        ArgumentNullException.ThrowIfNull(state);

        return Convert.ToHexString(SHA256.HashData(GetCanonicalBytes(state))).ToLowerInvariant();
    }

    internal static byte[] GetCanonicalBytes(WorldSnapshot state)
    {
        ArgumentNullException.ThrowIfNull(state);

        using var stream = new MemoryStream();
        using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true))
        {
            writer.Write(s_magic);
            writer.Write(23);
            writer.Write(state.Tick);
            writer.Write(state.Seed);
            writer.Write(state.InitialLevel100TutorialProgress.Introduction);
            writer.Write(state.InitialLevel100TutorialProgress.PulseCannon);
            writer.Write(state.InitialLevel100TutorialProgress.VulcanCannon);
            writer.Write(state.InitialLevel100TutorialProgress.StatusBars);
            writer.Write((int)state.Mode);
            writer.Write((int)state.Transition);
            WriteVector(writer, state.PlayerPosition);
            WriteVector(writer, state.PlayerVelocity);
            writer.Write(state.PlayerGroundElevationMillimeters);
            writer.Write(state.PlayerGroundDeltaMillimeters);
            writer.Write(state.FacingX);
            writer.Write(state.FacingZ);
            writer.Write(state.FacingYawMicroRad);
            writer.Write(state.WalkerYawVelocityMicroRadPerTick);
            writer.Write(state.FacingPitchMicroRad);
            writer.Write(state.WalkerPitchVelocityMicroRadPerTick);
            writer.Write(state.Energy);
            writer.Write(state.Shield);
            writer.Write(state.Hull);
            writer.Write(state.TransformTicksRemaining);
            writer.Write(state.FireCooldownTicksRemaining);
            writer.Write(state.Level100OpeningTicksRemaining);
            writer.Write(state.Level100PlayerActive);
            writer.Write(state.Level100FlightEnabled);
            writer.Write(state.Level100PulseCannonEnabled);
            writer.Write(state.Level100VulcanCannonEnabled);
            writer.Write(state.Level100MechVulcanCannonEnabled);
            writer.Write(state.Level100MissilePodEnabled);
            writer.Write(state.Level100HudEmphasisMask);
            WriteLevel100Mission(writer, state.Level100Mission);
            WriteLevel100Events(writer, state.Level100MissionEvents);
            WriteLevel100ActorRegistry(writer, state.Level100Actors);
            WriteLevel100Destruction(
                writer,
                state.Level100Destruction,
                state.Level100DestructionEvents);
            WriteLevel100ActorScripts(writer, state.Level100ActorScripts);
            WriteLevel100ActorScriptCommands(writer, state.Level100ActorScriptCommands);
            writer.Write(state.NextProjectileId);

            ProjectileSnapshot[] projectiles = state.Projectiles
                .OrderBy(projectile => projectile.Id)
                .ToArray();
            writer.Write(projectiles.Length);
            foreach (ProjectileSnapshot projectile in projectiles)
            {
                writer.Write(projectile.Id);
                WriteVector(writer, projectile.Position);
                WriteVector(writer, projectile.Velocity);
                writer.Write(projectile.ElevationMillimeters);
                writer.Write(projectile.VerticalVelocityMillimetersPerTick);
                writer.Write(projectile.RemainingTicks);
            }

            WalkerFootContactSnapshot[] walkerFeet = state.WalkerFeet
                .OrderBy(foot => foot.Id)
                .ToArray();
            writer.Write(walkerFeet.Length);
            foreach (WalkerFootContactSnapshot foot in walkerFeet)
            {
                writer.Write(foot.Id);
                WriteVector(writer, foot.Position);
                writer.Write(foot.GroundElevationMillimeters);
                writer.Write(foot.PhaseThirds);
                writer.Write(foot.LiftMillimeters);
            }
        }

        return stream.ToArray();
    }

    private static void WriteVector(BinaryWriter writer, SimVector2 vector)
    {
        writer.Write(vector.X);
        writer.Write(vector.Z);
    }

    private static void WriteLevel100ActorScripts(
        BinaryWriter writer,
        Level100ActorScriptRuntimeSnapshot scripts)
    {
        ArgumentNullException.ThrowIfNull(scripts);
        writer.Write(scripts.Tick);
        writer.Write(scripts.NextSequence);
        writer.Write(scripts.PlayerInJetMode);
        writer.Write(scripts.Instances.Count);
        foreach (Level100ActorScriptInstanceSnapshot instance in scripts.Instances)
        {
            WriteNullableActorId(writer, instance.ActorId);
            writer.Write(instance.ProgramName);
            writer.Write(instance.ProgramSha256);
            writer.Write(instance.Initialized);
            writer.Write(instance.Locals.Count);
            foreach (Level100ScriptLocalSnapshot local in instance.Locals)
            {
                writer.Write(local.Ordinal);
                writer.Write(local.Name);
                WriteLevel100Value(writer, local.Value);
            }
            WriteLevel100Execution(writer, instance.ActiveExecution);
            writer.Write(instance.QueuedEvents.Count);
            foreach (Level100QueuedEventSnapshot queuedEvent in instance.QueuedEvents)
            {
                writer.Write(queuedEvent.Sequence);
                writer.Write(queuedEvent.EventName);
            }
            writer.Write(instance.Continuations.Count);
            foreach (Level100ActorScriptContinuationSnapshot continuation in instance.Continuations)
            {
                writer.Write(continuation.Sequence);
                writer.Write(continuation.DueTick.HasValue);
                if (continuation.DueTick.HasValue)
                {
                    writer.Write(continuation.DueTick.Value);
                }
                writer.Write((int)continuation.WaitKind);
                WriteNullableString(writer, continuation.WaitArgument);
                WriteLevel100Execution(writer, continuation.Execution);
            }
        }
        writer.Write(scripts.PendingPostedEvents.Count);
        foreach (Level100ActorScriptEventPosted posted in scripts.PendingPostedEvents)
        {
            writer.Write(posted.Sequence);
            writer.Write(posted.Tick);
            WriteNullableActorId(writer, posted.ActorId);
            writer.Write(posted.EventName);
        }
        WriteLevel100ActorScriptCommands(writer, scripts.PendingCommands);
    }

    private static void WriteLevel100ActorScriptCommands(
        BinaryWriter writer,
        IReadOnlyList<Level100ActorScriptCommand> commands)
    {
        writer.Write(commands.Count);
        foreach (Level100ActorScriptCommand command in commands)
        {
            writer.Write(command.Sequence);
            writer.Write(command.Tick);
            WriteNullableActorId(writer, command.ActorId);
            writer.Write((int)command.Kind);
            WriteNullableActorId(writer, command.TargetActorId);
            WriteNullableString(writer, command.Argument);
            writer.Write(command.Scalar);
        }
    }

    private static void WriteLevel100ActorRegistry(
        BinaryWriter writer,
        Level100ActorRegistrySnapshot registry)
    {
        ArgumentNullException.ThrowIfNull(registry);
        writer.Write(registry.DefinitionSetIdentitySha256);
        writer.Write(registry.NextActorId);
        writer.Write(registry.NextFactSequence);

        Level100ActorSnapshot[] actors = registry.Actors
            .OrderBy(actor => actor.ActorId.Value)
            .ToArray();
        writer.Write(actors.Length);
        foreach (Level100ActorSnapshot actor in actors)
        {
            writer.Write(actor.ActorId.Value);
            writer.Write(actor.DefinitionIdentity);
            writer.Write(actor.Name);
            WriteNullableString(writer, actor.DefinitionName);
            WriteNullableString(writer, actor.ScriptName);
            WriteNullableString(writer, actor.MeshBinding);
            writer.Write(actor.ThingTypeMask);
            WriteNullableActorId(writer, actor.SpawnOwnerId);
            WriteNullableString(writer, actor.SpawnerName);
            writer.Write(actor.IsStatic);
            writer.Write(actor.Active);
            writer.Write(actor.IsObjective);
            writer.Write((int)actor.Lifecycle);
            writer.Write(actor.Health);
            ArgumentNullException.ThrowIfNull(actor.Pose);
            WriteVector(writer, actor.Pose.PositionMillimeters);
            WriteBasis(writer, actor.Pose.BasisFloatBits);
            WriteVector(writer, actor.Pose.LinearVelocityMillimetersPerTick);
            WriteVector(writer, actor.Pose.AngularVelocityMicroRadiansPerTick);

            writer.Write((int)actor.TargetGroup);
            writer.Write(actor.TargetOrdinal);
            writer.Write(actor.Trigger.HasValue);
            if (actor.Trigger.HasValue)
            {
                writer.Write((int)actor.Trigger.Value);
            }

            writer.Write(actor.TriggerEntered);
            writer.Write(actor.TriggerEntryJetModeState.HasValue);
            if (actor.TriggerEntryJetModeState.HasValue)
            {
                writer.Write((int)actor.TriggerEntryJetModeState.Value);
            }

            writer.Write(actor.TriggerEventDispatched);
        }

        Level100ActorFactSnapshot[] pendingFacts = registry.PendingFacts
            .OrderBy(fact => fact.Sequence)
            .ToArray();
        writer.Write(pendingFacts.Length);
        foreach (Level100ActorFactSnapshot fact in pendingFacts)
        {
            writer.Write(fact.Sequence);
            writer.Write((int)fact.Kind);
            writer.Write(fact.ActorId.Value);
            WriteNullableActorId(writer, fact.OtherActorId);
            writer.Write(fact.OtherThingTypeMask);
        }
    }

    private static void WriteLevel100Destruction(
        BinaryWriter writer,
        Level100DestructionRuntimeSnapshot destruction,
        IReadOnlyList<Level100DestructionEvent> events)
    {
        ArgumentNullException.ThrowIfNull(destruction);
        ArgumentNullException.ThrowIfNull(destruction.Actors);
        Level100DestructionSnapshot[] actors = destruction.Actors
            .OrderBy(actor => actor.ActorId)
            .ToArray();
        writer.Write(actors.Length);
        foreach (Level100DestructionSnapshot actor in actors)
        {
            writer.Write(actor.ActorId);
            writer.Write(actor.DefinitionName);
            writer.Write(actor.CurrentLifeBits);
            writer.Write(actor.Terminal);
            writer.Write(actor.BelowHalfReported);

            ReadOnlySpan<uint> initial = actor.InitialHealthBits.Span;
            ReadOnlySpan<uint> current = actor.CurrentHealthBits.Span;
            ReadOnlySpan<byte> activity = actor.PartActivity.Span;
            if (initial.Length != current.Length || initial.Length != activity.Length)
            {
                throw new InvalidDataException(
                    "A Level 100 destruction snapshot changed part shape.");
            }
            writer.Write(initial.Length);
            for (int index = 0; index < initial.Length; index++)
            {
                writer.Write(initial[index]);
                writer.Write(current[index]);
                writer.Write(activity[index]);
            }
        }

        ArgumentNullException.ThrowIfNull(events);
        writer.Write(events.Count);
        foreach (Level100DestructionEvent item in events)
        {
            writer.Write((byte)item.Kind);
            writer.Write((byte)item.EffectKind);
            writer.Write(item.ActorId);
            writer.Write(item.PartIndex);
            writer.Write(item.RemainingHealthBits);
            WriteContactVector(writer, item.Position);
        }
    }

    private static void WriteContactVector(BinaryWriter writer, Level100Vector3 vector)
    {
        writer.Write(vector.X);
        writer.Write(vector.Y);
        writer.Write(vector.Z);
    }

    private static void WriteVector(BinaryWriter writer, SimVector3 vector)
    {
        writer.Write(vector.X);
        writer.Write(vector.Y);
        writer.Write(vector.Z);
    }

    private static void WriteBasis(BinaryWriter writer, Level100FloatBasis3Bits basis)
    {
        writer.Write(basis.Row0X);
        writer.Write(basis.Row0Y);
        writer.Write(basis.Row0Z);
        writer.Write(basis.Row1X);
        writer.Write(basis.Row1Y);
        writer.Write(basis.Row1Z);
        writer.Write(basis.Row2X);
        writer.Write(basis.Row2Y);
        writer.Write(basis.Row2Z);
    }

    private static void WriteNullableActorId(
        BinaryWriter writer,
        Level100ActorId? actorId)
    {
        writer.Write(actorId.HasValue);
        if (actorId.HasValue)
        {
            writer.Write(actorId.Value.Value);
        }
    }

    private static void WriteLevel100Mission(
        BinaryWriter writer,
        Level100MissionSnapshot mission)
    {
        ArgumentNullException.ThrowIfNull(mission);

        writer.Write(mission.Tick);
        writer.Write(mission.ProgramSha256);
        writer.Write(mission.InitializerRan);
        writer.Write(mission.IsRunning);
        writer.Write(mission.NextSequence);
        WriteLevel100Execution(writer, mission.ActiveExecution);

        writer.Write(mission.Locals.Count);
        foreach (Level100ScriptLocalSnapshot local in mission.Locals)
        {
            writer.Write(local.Ordinal);
            writer.Write(local.Name);
            WriteLevel100Value(writer, local.Value);
        }

        writer.Write(mission.EventQueue.Count);
        foreach (Level100QueuedEventSnapshot queuedEvent in mission.EventQueue)
        {
            writer.Write(queuedEvent.Sequence);
            writer.Write(queuedEvent.EventName);
        }

        writer.Write(mission.Continuations.Count);
        foreach (Level100ScriptContinuationSnapshot continuation in mission.Continuations)
        {
            writer.Write(continuation.Sequence);
            writer.Write(continuation.DueTick);
            writer.Write((int)continuation.WaitKind);
            writer.Write(continuation.WaitArgument);
            WriteLevel100Execution(writer, continuation.Execution);
        }

        writer.Write((int)mission.Outcome);
        writer.Write((int)mission.TerminalState);
        writer.Write((int)mission.FailureReason);
        writer.Write(mission.FailureTextId);
        writer.Write(mission.TerminalTicksRemaining);
        writer.Write(mission.InitialPlayerHealth);
        writer.Write(mission.LatestPlayerHealth);
        writer.Write(mission.ObservedPlayerHealth);
        writer.Write(mission.PlayerActive);
        writer.Write(mission.FlightModeEnabled);
        writer.Write((int)mission.PulseCannonAvailability);
        writer.Write((int)mission.TwinVulcanAvailability);
        writer.Write((int)mission.MechVulcanAvailability);
        writer.Write((int)mission.MissilePodAvailability);
        WriteNullableString(writer, mission.NavigationObjective);
        writer.Write(mission.Evaded);
        writer.Write(mission.Aborted);
        writer.Write(mission.FriendlyBuildingHits);
        writer.Write(mission.ScoreDelta);
        writer.Write(mission.TutorialProgress.Introduction);
        writer.Write(mission.TutorialProgress.PulseCannon);
        writer.Write(mission.TutorialProgress.VulcanCannon);
        writer.Write(mission.TutorialProgress.StatusBars);

        writer.Write(mission.PrimaryObjectives.Count);
        foreach (Level100PrimaryObjectiveSnapshot objective in mission.PrimaryObjectives)
        {
            writer.Write(objective.Objective);
            writer.Write(objective.TextId);
            writer.Write((int)objective.Status);
        }

        WriteLevel100Events(writer, mission.PendingEvents);
    }

    private static void WriteLevel100Events(
        BinaryWriter writer,
        IReadOnlyList<Level100MissionEvent> events)
    {
        writer.Write(events.Count);
        foreach (Level100MissionEvent missionEvent in events)
        {
            switch (missionEvent)
            {
                case Level100MessageRequested item:
                    writer.Write((byte)1);
                    writer.Write(item.Tick);
                    writer.Write(item.SpeakerId);
                    writer.Write(item.MessageId);
                    writer.Write(item.ScriptWaitsForDuration);
                    writer.Write(item.ExpectedPlaybackTicks);
                    break;
                case Level100HudEmphasisChanged item:
                    writer.Write((byte)2);
                    writer.Write(item.Tick);
                    writer.Write(item.PartId);
                    writer.Write(item.Emphasized);
                    break;
                case Level100PlayerActivationChanged item:
                    writer.Write((byte)3);
                    writer.Write(item.Tick);
                    writer.Write(item.Active);
                    break;
                case Level100FlightModeAvailabilityChanged item:
                    writer.Write((byte)4);
                    writer.Write(item.Tick);
                    writer.Write(item.Enabled);
                    break;
                case Level100WeaponAvailabilityChanged item:
                    writer.Write((byte)5);
                    writer.Write(item.Tick);
                    writer.Write((int)item.Weapon);
                    writer.Write(item.Enabled);
                    break;
                case Level100NavigationObjectiveChanged item:
                    writer.Write((byte)6);
                    writer.Write(item.Tick);
                    WriteNullableString(writer, item.ThingName);
                    break;
                case Level100ActorCommandRequested item:
                    writer.Write((byte)7);
                    writer.Write(item.Tick);
                    writer.Write(item.ActorId.Value);
                    writer.Write((int)item.Command);
                    break;
                case Level100SpawnThingRequested item:
                    writer.Write((byte)8);
                    writer.Write(item.Tick);
                    writer.Write(item.OwnerActorId.Value);
                    writer.Write(item.DefinitionName);
                    writer.Write(item.SpawnerName);
                    writer.Write(item.Count);
                    writer.Write(item.ScriptName);
                    break;
                case Level100MissionEventPosted item:
                    writer.Write((byte)9);
                    writer.Write(item.Tick);
                    writer.Write(item.EventName);
                    break;
                case Level100HelpRequested item:
                    writer.Write((byte)13);
                    writer.Write(item.Tick);
                    writer.Write(item.HelpMessageId);
                    break;
                case Level100ScoreChanged item:
                    writer.Write((byte)14);
                    writer.Write(item.Tick);
                    writer.Write(item.Delta);
                    writer.Write(item.TotalDelta);
                    break;
                case Level100TutorialSlotSaved item:
                    writer.Write((byte)15);
                    writer.Write(item.Tick);
                    writer.Write(item.Slot);
                    break;
                case Level100PrimaryObjectiveChanged item:
                    writer.Write((byte)16);
                    writer.Write(item.Tick);
                    writer.Write(item.Objective);
                    writer.Write(item.TextId);
                    writer.Write((int)item.Status);
                    break;
                case Level100MissionOutcomeDeclared item:
                    writer.Write((byte)17);
                    writer.Write(item.Tick);
                    writer.Write((int)item.Outcome);
                    writer.Write((int)item.FailureReason);
                    writer.Write(item.FailureTextId);
                    break;
                case Level100TerminalStateChanged item:
                    writer.Write((byte)18);
                    writer.Write(item.Tick);
                    writer.Write((int)item.State);
                    break;
                default:
                    throw new InvalidOperationException(
                        $"Unknown Level 100 mission event {missionEvent.GetType().Name}.");
            }
        }
    }

    private static void WriteLevel100Execution(
        BinaryWriter writer,
        Level100ScriptExecutionSnapshot execution)
    {
        ArgumentNullException.ThrowIfNull(execution);
        WriteNullableString(writer, execution.EventName);
        writer.Write(execution.InstructionPointer);
        writer.Write(execution.Flags);
        writer.Write(execution.SavedStackSize);
        writer.Write(execution.Abort);
        writer.Write(execution.CallContext.HasValue);
        if (execution.CallContext.HasValue)
        {
            WriteLevel100Value(writer, execution.CallContext.Value);
        }
        writer.Write(execution.Stack.Count);
        foreach (Level100ScriptValueSnapshot value in execution.Stack)
        {
            WriteLevel100Value(writer, value);
        }

        writer.Write(execution.CallFrames.Count);
        foreach (int instructionPointer in execution.CallFrames)
        {
            writer.Write(instructionPointer);
        }
    }

    private static void WriteLevel100Value(
        BinaryWriter writer,
        Level100ScriptValueSnapshot value)
    {
        writer.Write((int)value.Type);
        writer.Write(value.Scalar);
        writer.Write(value.ComponentY);
        writer.Write(value.ComponentZ);
        WriteNullableString(writer, value.Text);
    }

    private static void WriteNullableString(BinaryWriter writer, string? value)
    {
        writer.Write(value is not null);
        if (value is not null)
        {
            writer.Write(value);
        }
    }
}
