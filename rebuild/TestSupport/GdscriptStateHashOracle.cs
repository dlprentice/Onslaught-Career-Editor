// SPDX-License-Identifier: GPL-3.0-or-later
using System.Collections;
using System.Globalization;
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.Core.Tests;

// Existing bounded simulation snapshots plus synthetic hash envelopes. Envelopes
// exercise serialization only and must not be mistaken for restore admission.
internal static class GdscriptStateHashOracle
{
    private static readonly MethodInfo Canonical = typeof(StateHasher).GetMethod(
        "GetCanonicalBytes", BindingFlags.Static | BindingFlags.NonPublic)!;
    private sealed record UnknownEvent(int Tick) : Level100MissionEvent(Tick);

    internal static object Build()
    {
        var cases = new List<object>();
        void Add(string name, WorldSnapshot? state, string? pinnedHash = null)
        {
            object expected;
            try
            {
                byte[] bytes = (byte[])Canonical.Invoke(null, [state])!;
                string hash = StateHasher.ComputeHex(state!);
                if (hash != Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant())
                    throw new InvalidOperationException("C# canonical byte/hash owners disagree.");
                if (pinnedHash is not null && hash != pinnedHash)
                    throw new InvalidOperationException("Existing SimulationTests canonical fingerprint moved: " + hash);
                expected = new { ok = true, bytes = Convert.ToHexString(bytes).ToLowerInvariant(), hash,
                    schema = BitConverter.ToInt32(bytes, 23), pinned_hash = pinnedHash };
            }
            catch (TargetInvocationException error) when (error.InnerException is not null)
            {
                expected = new { ok = false, error_type = error.InnerException.GetType().Name };
            }
            cases.Add(new { name, snapshot = Facts(state), expected });
        }

        Type fixtures = typeof(SimulationTests).Assembly.GetType("OnslaughtRebuild.TestSupport.Level100TestActorDefinitions")!;
        var definitions = (Level100ActorDefinitionSet)fixtures.GetMethod("Create", BindingFlags.NonPublic | BindingFlags.Static)!.Invoke(null, null)!;
        var simulation = new Simulation(1, definitions, new(true, true, true, true));
        WorldSnapshot initial = simulation.Snapshot;
        Add("live-initial-schema47", initial);
        foreach (int tick in Enumerable.Range(1, 40))
        {
            simulation.Step(new SimInput(0, 1));
            if (tick is 1 or 2 or 9 or 20 or 40)
                Add("live-forward-tick-" + tick, simulation.Snapshot, tick == 40
                    ? "0a0b24633f25bb96ac2e8b98443524de47e065b3744b9a15871c09595127a19d" : null);
        }
        WorldSnapshot live = simulation.Snapshot;
        WorldSnapshot legacy = Legacy(live) with { Level100PlayerWeaponState = Level100PlayerWeaponStateSnapshot.Initial };
        Add("legacy-root-schema42", legacy);
        Add("legacy-world110-schema43", legacy with { Level100Mission = legacy.Level100Mission with { WorldNumber = 110 } });
        Add("legacy-secondary-text-schema43", legacy with { Level100Mission = legacy.Level100Mission with
            { SecondaryObjectives = legacy.Level100Mission.SecondaryObjectives.Select((o, i) => i == 1 ? o with { TextId = 1 } : o).ToArray() } });
        Add("legacy-secondary-status-schema43", legacy with { Level100Mission = legacy.Level100Mission with
            { SecondaryObjectives = legacy.Level100Mission.SecondaryObjectives.Select((o, i) => i == 2 ? o with { Status = RetailSecondaryObjectiveStatus.Failed } : o).ToArray() } });
        foreach (var weapons in new[] {
            Level100PlayerWeaponStateSnapshot.Initial with { PulseChargeBits = 0x80000000 },
            Level100PlayerWeaponStateSnapshot.Initial with { PulseReadyAtTimeBits = 0xc3480001 },
            Level100PlayerWeaponStateSnapshot.Initial with { TwinVulcanReadyAtTimeBits = 0 },
            Level100PlayerWeaponStateSnapshot.Initial with { MechVulcanReadyAtTimeBits = 0xffffffff },
            Level100PlayerWeaponStateSnapshot.Initial with { MissilePodReadyAtTimeBits = 0x7fc00000 },
        }) Add("weapon-extension-schema44-" + cases.Count, legacy with { Level100PlayerWeaponState = weapons });
        foreach (uint frame in new[] { 0u, 1u, uint.MaxValue })
            Add("independent-clock-schema45-" + frame, legacy with { RetailEventFrameCount = frame });
        var shutdown = legacy with { Level100Destruction = legacy.Level100Destruction with { PendingShutdowns =
            [new(5, uint.MaxValue, 0, 0x80000000), new(2, 40, 41, 0x40033334)] } };
        Add("shutdown-schema46", shutdown);
        Add("shutdown-order-retained", shutdown with { Level100Destruction = shutdown.Level100Destruction with
            { PendingShutdowns = shutdown.Level100Destruction.PendingShutdowns.Reverse().ToArray() } });
        Add("dying-shutdown-schema46", legacy with { Level100Actors = legacy.Level100Actors with
            { Actors = legacy.Level100Actors.Actors.Select((actor, i) => i == 0 ? actor with { Lifecycle = Level100ActorLifecycle.DiedAwaitingShutdown } : actor).ToArray() } });

        Level100ActorBaseStateSnapshot raw = live.Level100Actors.BaseStates.First(item => item.State.RetailPlane is not null);
        WorldSnapshot ChangeRaw(ThingActorBaseStateSnapshot state) => live with { Level100Actors = live.Level100Actors with
            { BaseStates = live.Level100Actors.BaseStates.Select(item => item.ActorId == raw.ActorId ? item with { State = state } : item).ToArray() } };
        Level100ActorId owner = live.Level100Actors.Actors.First(actor => actor.ActorId != raw.ActorId).ActorId;
        WorldSnapshot exited = live with {
            Level100Actors = live.Level100Actors with { Actors = live.Level100Actors.Actors.Select(actor => actor.ActorId == raw.ActorId
                ? actor with { SpawnOwnerId = owner, SpawnerName = "Synthetic exit owner" } : actor).ToArray() },
            Level100ActorMechanics = live.Level100ActorMechanics with { Actors = live.Level100ActorMechanics.Actors.Select(actor => actor.ActorId == raw.ActorId
                ? actor with { PlaneSpawnerExit = new(owner, owner, int.MinValue, 2, 0x3f800001, false) } : actor).ToArray() } };
        Add("synthetic-exit-envelope-schema48", exited);
        Add("nullable-exit-readers", exited with { Level100ActorMechanics = exited.Level100ActorMechanics with
            { Actors = exited.Level100ActorMechanics.Actors.Select(actor => actor.PlaneSpawnerExit is null ? actor : actor with
                { PlaneSpawnerExit = actor.PlaneSpawnerExit with { SpawningOwnerId = null, CollisionIgnoredActorId = null, ScriptControlResumed = true } }).ToArray() } });
        Add("subprojection-drive-word", ChangeRaw(raw.State with { RetailPlane = raw.State.RetailPlane! with { Drive = new(int.MinValue, 1, 0) } }));
        Add("guide-word-is-not-restore-admission", live with { Level100ActorMechanics = live.Level100ActorMechanics with
            { Actors = live.Level100ActorMechanics.Actors.Select(actor => actor.PlaneGuide is null ? actor : actor with
                { PlaneGuide = actor.PlaneGuide with { ClearanceFloatBits = int.MinValue, ClearanceCellX = int.MaxValue } }).ToArray() } });
        Add("event-arithmetic-mode-is-hashed", live with { Level100ActorMechanics = live.Level100ActorMechanics with
            { PlaneEvents = live.Level100ActorMechanics.PlaneEvents! with { Float24Arithmetic = false } } });
        Add("event-pool-order-is-hashed", live with { Level100ActorMechanics = live.Level100ActorMechanics with
            { PlaneEvents = live.Level100ActorMechanics.PlaneEvents! with {
                Slots = live.Level100ActorMechanics.PlaneEvents!.Slots.Reverse().ToArray(),
                Lanes = live.Level100ActorMechanics.PlaneEvents.Lanes.Select(lane => lane with { Handles = lane.Handles.Reverse().ToArray() }).Reverse().ToArray(),
                Overflow = [17, 4, -1] } } });

        // Every canonical sort is exercised, including equal-key pairs where
        // LINQ's stable ordering retains the original encounter order.
        var sorted = legacy with {
            Level100Actors = legacy.Level100Actors with {
                Actors = legacy.Level100Actors.Actors.Reverse().Concat([legacy.Level100Actors.Actors[0] with { Name = "equal-id-second" }]).ToArray(),
                BaseStates = legacy.Level100Actors.BaseStates.Reverse().Concat([legacy.Level100Actors.BaseStates[0] with
                    { State = legacy.Level100Actors.BaseStates[0].State with { LastTimeOnGroundFloatBits = int.MinValue } }]).ToArray(),
                PendingFacts = [new(long.MaxValue, 0, new(5), null, uint.MaxValue), new(-1, (Level100ActorFactKind)1, new(2), new(-3), 0),
                    new(-1, (Level100ActorFactKind)2, new(4), null, 1), new(long.MinValue, 0, new(-1), null, 2)] },
            Level100ActorMechanics = legacy.Level100ActorMechanics with {
                LastConsumedCommandSequence = long.MinValue,
                Actors = legacy.Level100ActorMechanics.Actors.Reverse().Concat([legacy.Level100ActorMechanics.Actors[0] with { AiState = int.MinValue }]).ToArray(),
                ActorWeapons = [new(new(2), (Level100ActorWeaponKind)1, 10, 11, 12), new(new(1), 0, 20, 21, 22),
                    new(new(2), 0, 30, 31, 32), new(new(1), 0, 40, 41, 42)],
                ActorRounds = [new(2, new(9), new(8), 0, new(1, 2, 3), 4, 5, 6, 7, true),
                    new(1, new(8), new(9), (Level100ActorRoundKind)1, new(-1, -2, -3), -4, -5, -6, -7, false),
                    new(1, new(7), new(6), 0, new(3, 2, 1), 8, 9, 10, 11, true)] },
            Projectiles = [new(2, 0, new(1, 2), new(3, 4), 5, 6, 7), new(-1, (Level100ProjectileKind)255, new(-1, -2), new(-3, -4), -5, -6, -7),
                new(2, (Level100ProjectileKind)1, new(8, 9), new(10, 11), 12, 13, 14)],
            WalkerFeet = [new(2, new(1, 2), 3, 4, 5), new(1, new(6, 7), 8, 9, 10), new(2, new(11, 12), 13, 14, 15)],
            Level100Destruction = new([Destruction(2, "second", [1, uint.MaxValue], [0x80000000, 0x7fc00000], [0, 255]),
                Destruction(1, "first", [], [], []), Destruction(2, "equal-id", [2], [3], [4])]),
        };
        Add("all-sorts-and-stable-ties", sorted);
        Add("stable-tie-encounter-order-changes-bytes", sorted with { Projectiles = sorted.Projectiles.Reverse().ToArray(),
            Level100ActorMechanics = sorted.Level100ActorMechanics with { ActorWeapons = sorted.Level100ActorMechanics.ActorWeapons.Reverse().ToArray() } });
        Add("unique-sorts-reorder-to-same-bytes", live with { Level100Actors = live.Level100Actors with
            { Actors = live.Level100Actors.Actors.Reverse().ToArray(), BaseStates = live.Level100Actors.BaseStates.Reverse().ToArray(), PendingFacts = live.Level100Actors.PendingFacts.Reverse().ToArray() },
            Level100ActorMechanics = live.Level100ActorMechanics with { Actors = live.Level100ActorMechanics.Actors.Reverse().ToArray(),
                ActorWeapons = live.Level100ActorMechanics.ActorWeapons.Reverse().ToArray(), ActorRounds = live.Level100ActorMechanics.ActorRounds.Reverse().ToArray() },
            Projectiles = live.Projectiles.Reverse().ToArray(), WalkerFeet = live.WalkerFeet.Reverse().ToArray() });

        Level100MissionEvent[] allEvents = [
            new Level100MessageRequested(int.MinValue, -1, int.MaxValue, true, 0), new Level100HudEmphasisChanged(2, -2, true),
            new Level100PlayerActivationChanged(3, false), new Level100FlightModeAvailabilityChanged(4, true),
            new Level100WeaponAvailabilityChanged(5, (Level100MissionWeapon)int.MaxValue, false), new Level100NavigationObjectiveChanged(6, null),
            new Level100ActorCommandRequested(7, new(-1), (Level100ActorCommand)int.MaxValue),
            new Level100SpawnThingRequested(8, new(1), "def\0tail", "spawner", -1, "\ud800script"),
            new Level100MissionEventPosted(9, "posted"), new Level100HelpRequested(13, -13), new Level100ScoreChanged(14, -1, int.MaxValue),
            new Level100TutorialSlotSaved(15, -15), new Level100PrimaryObjectiveChanged(16, -1, 0, (Level100PrimaryObjectiveStatus)int.MinValue),
            new Level100MissionOutcomeDeclared(17, (Level100MissionOutcome)9, (Level100MissionFailureReason)8, -7),
            new Level100TerminalStateChanged(18, (Level100MissionTerminalState)int.MaxValue), new Level100NavigationObjectiveChanged(19, ""),
        ];
        var stackValue = new Level100ScriptValueSnapshot((Level100ScriptValueType)int.MaxValue, int.MinValue, 123, -123, "\ud800\0🚀\udc00");
        var execution = new Level100ScriptExecutionSnapshot("", int.MinValue, int.MaxValue, -1, true, stackValue,
            [stackValue, stackValue with { Text = null }], [int.MaxValue, int.MinValue, 0]);
        Add("all-events-executions-null-and-utf16", legacy with {
            FacingX = sbyte.MinValue, FacingZ = sbyte.MaxValue, Seed = uint.MaxValue,
            AquilaFlightEventLog = [new(-1, (AquilaFlightEvents)ushort.MaxValue, (VehicleMode)(-1), (VehicleTransition)(-2), (AquilaJetWeapon)255)],
            Level100PlayerDamageEvents = [new(-1, (Level100PlayerDamageSource)255, int.MinValue, 1, int.MaxValue, true)],
            Level100DamageFlashes = [new(int.MinValue, int.MaxValue), new(1, -2)],
            Level100WeaponFireEvents = [new(-1, (Level100PlayerWeapon)255, int.MinValue)],
            Level100MissionEvents = allEvents,
            Level100Mission = legacy.Level100Mission with { ProgramSha256 = "prefix\0suffix", NavigationObjective = "\ud800", NextSequence = long.MaxValue,
                ActiveExecution = execution, Locals = [new(-1, "\udc00name", stackValue)], EventQueue = [new(long.MinValue, "event")],
                Continuations = [new(long.MaxValue, int.MinValue, (Level100ScriptWaitKind)8, int.MaxValue, execution)],
                PendingEvents = allEvents.Reverse().ToArray(), PendingMessages = [new(3, 4, 5, false, 6)] },
            Level100ActorScripts = new(-1, long.MinValue, true, [new(null, "program", "sha", true, [new(1, "local", stackValue)], execution,
                [new(long.MaxValue, "queue")], [new(long.MinValue, null, (Level100ActorScriptWaitKind)7, null, execution),
                    new(1, int.MinValue, (Level100ActorScriptWaitKind)8, "", execution)])],
                [new(long.MaxValue, int.MinValue, new(int.MaxValue), "posted\0tail")],
                [new(long.MinValue, int.MaxValue, null, (Level100ActorScriptCommandKind)10, new(-1), null, int.MinValue)]),
            Level100ActorScriptCommands = [new(long.MaxValue, int.MinValue, new(int.MaxValue), (Level100ActorScriptCommandKind)9, null, "\ud800", int.MaxValue)],
            Level100DestructionEvents = [new((Level100DestructionEventKind)255, (Level100DestructionEffectKind)254, int.MinValue, int.MaxValue,
                uint.MaxValue, new(-1, 0, 1))],
        });

        Add("null-state-refused", null);
        Add("incomplete-raw-construction-refused", ChangeRaw(raw.State with { RetailPlane = null }));
        Add("missing-retail-poses-refused", ChangeRaw(raw.State with { RetailPoses = null }));
        Add("missing-retail-motion-refused", ChangeRaw(raw.State with { RetailMotion = null }));
        Add("raw-world110-refused", live with { Level100Mission = live.Level100Mission with { WorldNumber = 110 } });
        Add("missing-guide-refused", live with { Level100ActorMechanics = live.Level100ActorMechanics with
            { Actors = live.Level100ActorMechanics.Actors.Select(actor => actor with { PlaneGuide = null }).ToArray() } });
        Add("missing-events-refused", live with { Level100ActorMechanics = live.Level100ActorMechanics with { PlaneEvents = null } });
        Add("mismatched-clock-refused", live with { RetailEventFrameCount = live.RetailEventFrameCount + 1 });
        Add("missing-exit-owner-refused", exited with { Level100ActorMechanics = live.Level100ActorMechanics });
        Add("orphan-exit-refused", live with { Level100ActorMechanics = exited.Level100ActorMechanics });
        Add("unsupported-definition-refused", live with { Level100Actors = live.Level100Actors with
            { Actors = live.Level100Actors.Actors.Select(actor => actor.ActorId == raw.ActorId ? actor with { DefinitionName = "Unsupported" } : actor).ToArray() } });
        Add("duplicate-plane-actor-refused", live with { Level100Actors = live.Level100Actors with
            { Actors = live.Level100Actors.Actors.Concat([live.Level100Actors.Actors.Single(actor => actor.ActorId == raw.ActorId)]).ToArray() } });
        Add("nonfinite-raw-position-refused", ChangeRaw(raw.State with { RetailPoses = raw.State.RetailPoses! with
            { Current = raw.State.RetailPoses.Current with { PositionFloatBits = new(0x7fc00000, 0, 0) } } }));
        Add("raw-position-overflow-refused", ChangeRaw(raw.State with { RetailPoses = raw.State.RetailPoses! with
            { Current = raw.State.RetailPoses.Current with { PositionFloatBits = new(0x7f7fffff, 0, 0) } } }));
        Add("negative-euler-rate-refused", ChangeRaw(raw.State with { RetailPlane = raw.State.RetailPlane! with { EulerRates = new(unchecked((int)0xbf800000), 0, 0) } }));
        Add("signed-zero-bank-refused", ChangeRaw(raw.State with { RetailPlane = raw.State.RetailPlane! with { BankFlagFloatBits = int.MinValue } }));
        Add("invalid-actor-flags-refused", ChangeRaw(raw.State with { Flags = ThingActorFlags.IsBigThing }));
        Add("missing-lineage-refused", ChangeRaw(raw.State with { ThingTypeMask = 0 }));
        Add("negative-move-countdown-refused", ChangeRaw(raw.State with { RetailMotion = raw.State.RetailMotion! with { MoveCountdown = -1 } }));
        Add("nonfinite-move-time-refused", ChangeRaw(raw.State with { RetailMotion = raw.State.RetailMotion! with { LastMoveTimeFloatBits = 0x7f800000 } }));
        Add("compatibility-pose-conflict-refused", ChangeRaw(raw.State with { CurrentPose = raw.State.CurrentPose with
            { PositionMillimeters = raw.State.CurrentPose.PositionMillimeters with { X = raw.State.CurrentPose.PositionMillimeters.X + 1 } } }));
        Add("actor-projection-conflict-refused", live with { Level100Actors = live.Level100Actors with
            { Actors = live.Level100Actors.Actors.Select(actor => actor.ActorId == raw.ActorId ? actor with
                { Pose = actor.Pose with { LinearVelocityMillimetersPerTick = new(1, 2, 3) } } : actor).ToArray() } });
        Add("destruction-shape-refused", legacy with { Level100Destruction = new([Destruction(1, "bad-shape", [1], [], [1])]) });
        Add("unknown-mission-event-refused", legacy with { Level100MissionEvents = [new UnknownEvent(1)] });
        return new { cases };
    }

    private static WorldSnapshot Legacy(WorldSnapshot state) => state with {
        Level100Actors = state.Level100Actors with { BaseStates = state.Level100Actors.BaseStates.Select(item => item.State.RetailPlane is null ? item : item with {
            State = item.State with { RetailPlane = null, RetailPoses = null, RetailMotion = null, Flags = item.State.Flags & ~ThingActorFlags.InMapWho } }).ToArray() },
        Level100ActorMechanics = state.Level100ActorMechanics with { PlaneEvents = null,
            Actors = state.Level100ActorMechanics.Actors.Select(actor => actor with { PlaneGuide = null, PlaneSpawnerExit = null }).ToArray() } };

    private static Level100DestructionSnapshot Destruction(int id, string name, uint[] initial, uint[] current, byte[] activity) =>
        (Level100DestructionSnapshot)Activator.CreateInstance(typeof(Level100DestructionSnapshot), BindingFlags.Instance | BindingFlags.NonPublic,
            null, [id, name, 0x80000000u, false, true, initial, current, activity], CultureInfo.InvariantCulture)!;

    // Fixture transport alone uses reflection over stored (settable) properties.
    // Production serialization is the explicit, source-ordered GDScript owner.
    // Read-only computed views are excluded; destruction's immutable payload is
    // listed explicitly. Markers avoid lossy JSON int64 and UTF-16 conversion.
    private static object? Facts(object? value)
    {
        if (value is null) return null;
        if (value is string text) return new Dictionary<string, object> { ["$utf16"] = text.Select(c => (int)c).ToArray() };
        if (value is Level100ActorId id) return id.Value;
        if (value is long sequence) return new Dictionary<string, object> { ["$i64"] = sequence.ToString(CultureInfo.InvariantCulture) };
        if (value is bool or byte or sbyte or short or ushort or int or uint) return value;
        if (value is Enum) return Convert.ToInt64(value, CultureInfo.InvariantCulture);
        if (value is ReadOnlyMemory<uint> words) return words.ToArray();
        if (value is ReadOnlyMemory<byte> bytes) return bytes.ToArray().Select(b => (int)b).ToArray();
        if (value is Level100DestructionSnapshot destruction)
            return new Dictionary<string, object?> { ["actor_id"] = destruction.ActorId, ["definition_name"] = Facts(destruction.DefinitionName),
                ["current_life_bits"] = destruction.CurrentLifeBits, ["terminal"] = destruction.Terminal, ["below_half_reported"] = destruction.BelowHalfReported,
                ["initial_health_bits"] = Facts(destruction.InitialHealthBits), ["current_health_bits"] = Facts(destruction.CurrentHealthBits), ["part_activity"] = Facts(destruction.PartActivity) };
        if (value is IEnumerable sequenceValues) return sequenceValues.Cast<object?>().Select(Facts).ToArray();
        var result = value.GetType().GetProperties(BindingFlags.Instance | BindingFlags.Public)
            .Where(property => property.SetMethod is not null && property.GetIndexParameters().Length == 0)
            .ToDictionary(property => JsonNamingPolicy.SnakeCaseLower.ConvertName(property.Name), property => Facts(property.GetValue(value)));
        if (value is Level100MissionEvent missionEvent)
            result["event_type"] = missionEvent switch { Level100MessageRequested => 1, Level100HudEmphasisChanged => 2,
                Level100PlayerActivationChanged => 3, Level100FlightModeAvailabilityChanged => 4, Level100WeaponAvailabilityChanged => 5,
                Level100NavigationObjectiveChanged => 6, Level100ActorCommandRequested => 7, Level100SpawnThingRequested => 8,
                Level100MissionEventPosted => 9, Level100HelpRequested => 13, Level100ScoreChanged => 14, Level100TutorialSlotSaved => 15,
                Level100PrimaryObjectiveChanged => 16, Level100MissionOutcomeDeclared => 17, Level100TerminalStateChanged => 18, _ => 0 };
        if (result.Count == 0) throw new NotSupportedException("Unmapped canonical fixture carrier: " + value.GetType());
        return result;
    }
}
