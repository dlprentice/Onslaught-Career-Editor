// SPDX-License-Identifier: GPL-3.0-or-later
using System.Collections;
using System.Reflection;
using System.Runtime.ExceptionServices;
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;
using M = System.Collections.Generic.Dictionary<string, object?>;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Unchanged Level100ActorRegistry oracle. Reflections reach only the
/// current internal construction/state seams; they do not alter production.
/// Prepared terrain/manifest inputs are read only, outputs are private values.</summary>
public sealed partial class ActorRegistryReferenceChecks : Node
{
    private const BindingFlags Instance = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
    private const BindingFlags Static = BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
    private readonly List<Level100ActorDefinitionSet> _definitions = [];
    private readonly List<M> _cases = [];
    private int _operations, _checks;
    private sealed record Raw(object? Value);

    public override void _Ready()
    {
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2 && !Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Two owned outputs and headless runtime required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            Check(fixturePath != reportPath, "Distinct outputs required.");
            var pointer = Godot.Input.MouseMode;
            string project = ProjectSettings.GlobalizePath("res://");
            string manifestPath = Path.Combine(project, "Assets/Level100/StaticWorld/level100-static-world.json");
            byte[] manifest = File.ReadAllBytes(manifestPath);
            Check(Hash(manifest) == Level100ActorDefinitionManifest.ExpectedManifestSha256.ToLowerInvariant(), "Pinned manifest identity.");
            Level100ActorDefinitionSet actual = Level100ActorDefinitionManifest.Decode(manifest);
            var terrainRows = new List<M>();
            foreach (int world in new[] { 100, 110 })
            {
                string path = Path.GetFullPath(Path.Combine(project, "..", "OnslaughtRebuild.Core", "Assets", "Level" + world, $"level{world}-heightfield.hfld.bin"));
                byte[] bytes = File.ReadAllBytes(path);
                Level100Terrain terrain = world == 100 ? Level100Terrain.Instance : Level100Terrain.World110;
                Check(StringComparer.OrdinalIgnoreCase.Equals(Hash(bytes), terrain.PayloadSha256), "Prepared terrain equals original admitted resource.");
                terrainRows.Add(new M { ["world"] = world, ["path"] = path, ["sha256"] = Hash(bytes) });
            }
            SequenceCases(actual);
            RestoreCases(actual);
            ConstructorCases(actual);
            RawAndConstructionCases(actual);
            var sets = _definitions.Select(DefinitionFacts).ToArray();
            var contexts = _definitions.Select(d => d.WorldNumber).Distinct().Select(ContextFacts).ToArray();
            var fixture = new M { ["schema"] = 1, ["completed"] = new[] { "actor_registry_reference" },
                ["definitions"] = sets, ["contexts"] = contexts, ["terrains"] = terrainRows, ["cases"] = _cases,
                ["manifest_path"] = manifestPath, ["manifest_sha256"] = Hash(manifest), ["source_sha256"] = SourceHashes() };
            using (Variant value = Pack(fixture))
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot create registry fixture."))
                file.StoreVar(value, false);
            Check(Hash(File.ReadAllBytes(manifestPath)) == Hash(manifest) && Godot.Input.MouseMode == pointer, "Manifest and pointer unchanged.");
            foreach (M terrain in terrainRows) Check(Hash(File.ReadAllBytes((string)terrain["path"]!)) == (string)terrain["sha256"]!, "Terrain unchanged.");
            var report = new M { ["schema"] = 1, ["failure_count"] = 0, ["completed"] = new[] { "actor_registry_reference" },
                ["counts"] = new M { ["assertions"] = _checks, ["cases"] = _cases.Count, ["operations"] = _operations, ["definition_sets"] = sets.Length },
                ["fixture_sha256"] = Hash(File.ReadAllBytes(fixturePath)), ["actual_definition_identity"] = actual.IdentitySha256 };
            File.WriteAllText(reportPath, JsonSerializer.Serialize(report));
            GD.Print($"ACTOR_REGISTRY_REFERENCE_CHECKS: {_checks} assertions; {_cases.Count} cases, {_operations} operations; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private sealed class Sequence(ActorRegistryReferenceChecks owner, Level100ActorRegistry state, M row, Level100ActorDefinitionSet definitions, int terrain, bool support)
    {
        public Level100ActorRegistry State { get; } = state;
        public Sequence Do(string op, params object?[] args)
        {
            M expected = Capture(() => Operation(State, definitions, terrain, support, op, args));
            ((List<M>)row["steps"]!).Add(new M { ["op"] = op, ["args"] = new Raw(args), ["expected"] = expected,
                ["snapshot"] = Capture(() => State.Snapshot) });
            owner._operations++;
            return this;
        }
    }

    private Sequence? Case(string name, Level100ActorDefinitionSet definitions, Level100ActorRegistrySnapshot? snapshot = null,
        bool restore = false, int terrain = 100, bool support = true)
    {
        int index = _definitions.FindIndex(item => ReferenceEquals(item, definitions));
        if (index < 0) { index = _definitions.Count; _definitions.Add(definitions); }
        Level100ActorRegistry? owner = null;
        M constructed = Capture(() => { owner = Construct(definitions, snapshot, restore, terrain, support); return null; });
        var row = new M { ["name"] = name, ["definition"] = index, ["terrain"] = terrain, ["support"] = support,
            ["kind"] = restore ? "restore" : "create", ["input"] = snapshot, ["result"] = constructed,
            ["snapshot"] = owner is null ? null : Capture(() => owner.Snapshot), ["steps"] = new List<M>() };
        _cases.Add(row);
        return owner is null ? null : new Sequence(this, owner, row, definitions, terrain, support);
    }

    private void SequenceCases(Level100ActorDefinitionSet actual)
    {
        var s = Case("actual/lifecycle-and-order", actual)!;
        Level100ActorId player = s.State.GetThingRef("Player 1")!.Value;
        Level100ActorId trainer = s.State.GetThingRef("Air Trainer")!.Value;
        Level100ActorId trigger = s.State.Snapshot.Actors.First(a => a.Trigger.HasValue).ActorId;
        Level100ActorId owner = s.State.GetThingRef("Airfield")!.Value;
        Check(s.State.GetActor(trainer).Health == 3000, "Retained authored Air Trainer health.");
        foreach (string? text in new string?[] { null, "", "missing", "Player 1", "player 1", "Air Trainer", "x\0y", "\ud800", "\udc00" }) s.Do("get_thing_ref", text);
        foreach (int id in new[] { int.MinValue, -1, 0, player.Value, int.MaxValue })
            foreach (string op in new[] { "get_actor", "get_base_state", "get_pose", "get_health", "is_active", "get_lifecycle", "flag_word", "get_thing_type_mask", "get_plane_state", "get_construction_state" }) s.Do(op, new Level100ActorId(id));
        s.Do("set_objective", player, true).Do("flag_word", player).Do("make_invisible", player).Do("make_visible", player);
        foreach (string op in new[] { "declare_on_ground", "declare_in_water", "declare_on_object" })
            foreach (int word in new[] { 0, int.MinValue, 1, 0x41480000, 0x7f7fffff, 0x7f800000, unchecked((int)0xff800000), 0x7fc00001 }) s.Do(op, player, word);
        var pose = s.State.GetActor(player).Pose with { PositionMillimeters = new(123, -234, 345),
            LinearVelocityMillimetersPerTick = new(int.MaxValue, 2, -3), AngularVelocityMicroRadiansPerTick = new(-4, 5, int.MinValue) };
        s.Do("set_pose", player, pose).Do("advance_pose", player, pose with { PositionMillimeters = new(-9, 8, -7) })
            .Do("update_current_pose", player, pose with { PositionMillimeters = new(7, -8, 9) })
            .Do("advance_low_fidelity_position", player, new SimVector3(int.MinValue, int.MaxValue, 5)).Do("stop_motion", player);
        foreach (string op in new[] { "set_pose", "advance_pose", "update_current_pose" })
            s.Do(op, new Level100ActorId(-1), null).Do(op, new Level100ActorId(-1), pose with { BasisFloatBits = pose.BasisFloatBits with { Row2Z = 0x7f800000 } });
        foreach (string? script in new string?[] { null, "", "missing", "x\0y", "\ud800", "LevelScript", "Flyby" }) s.Do("set_actor_script", player, script);
        s.Do("set_actor_script", player, actual.Actors.First(a => a.Name == "Player 1").ScriptName ?? "LevelScript");
        s.Do("set_health", new Level100ActorId(-1), -1).Do("set_health", player, -1).Do("set_health", player, int.MaxValue).Do("set_health", player, 0);
        s.Do("report_hit", player, null, 4u).Do("report_hit", player, trainer, 0u).Do("report_hit", player, player, 4u)
            .Do("report_hit", player, null, 1u).Do("report_hit", new Level100ActorId(-1), null, uint.MaxValue)
            .Do("report_hit", player, new Level100ActorId(-1), 0u).Do("drain_facts").Do("drain_facts");
        s.Do("begin_trigger_dispatch", trigger, Level100MissionJetModeState.InJetMode).Do("begin_trigger_dispatch", trigger, Level100MissionJetModeState.NotInJetMode)
            .Do("mark_trigger_event_dispatched", trigger).Do("mark_trigger_event_dispatched", trigger).Do("deactivate", trigger)
            .Do("begin_trigger_dispatch", trigger, (Level100MissionJetModeState)999).Do("begin_trigger_dispatch", player, (Level100MissionJetModeState)999);
        s.Do("report_plane_started_dying", player).Do("report_plane_started_dying", trainer).Do("report_plane_started_dying", trainer)
            .Do("set_objective", trainer, true).Do("report_died", trainer).Do("flag_word", trainer).Do("activate", trainer).Do("set_objective", trainer, true)
            .Do("set_objective", trainer, false).Do("report_died", trainer).Do("restore_snapshot");
        s.Do("report_started_dying", player).Do("report_started_dying", player).Do("report_died", player).Do("drain_facts");
        s.Do("get_plane_spawner_exit_point", owner, 1);

        foreach (Level100SpawnDefinition spawn in actual.Spawns)
        {
            var run = Case("actual/spawn/" + spawn.DefinitionIdentity, actual)!;
            Level100ActorId spawnOwner = run.State.Snapshot.Actors.Single(a => a.DefinitionIdentity == spawn.OwnerDefinitionIdentity).ActorId;
            run.Do("spawn_thing", spawnOwner, spawn.DefinitionName, spawn.SpawnerName, 1, spawn.ScriptName, 0x41480000);
            Level100ActorId id = run.State.Snapshot.Actors.Last().ActorId;
            run.Do("get_actor", id).Do("get_plane_state", id).Do("get_plane_spawner_exit_point", id, 1).Do("get_plane_spawner_exit_point", id, 0)
                .Do("get_plane_spawner_exit_point", id, int.MinValue).Do("get_plane_spawner_exit_point", id, int.MaxValue).Do("restore_snapshot");
            for (int i = 0; i < Math.Min(4, spawn.MaximumGroupActors + 1); i++) run.Do("spawn_thing", spawnOwner, spawn.DefinitionName, spawn.SpawnerName, 1, spawn.ScriptName, int.MinValue);
        }
        var bad = Case("actual/spawn-failure-order", actual)!;
        foreach (int count in new[] { int.MinValue, -1, 0, 2, int.MaxValue }) bad.Do("spawn_thing", owner, "Air Trainer", "SpawnerB", count, "AirTrainer", 0);
        bad.Do("spawn_thing", new Level100ActorId(-1), null, null, 0, null, 0).Do("spawn_thing", owner, null, null, 0, null, 0)
            .Do("spawn_thing", owner, "", null, 0, null, 0).Do("spawn_thing", owner, "Air Trainer", null, 0, null, 0)
            .Do("spawn_thing", owner, "Air Trainer", "SpawnerB", 1, null, 0)
            .Do("spawn_thing", owner, "Air Trainer", "SpawnerB", 1, "AirTrainer", 0x7fc00001);
        var moved = bad.State.GetActor(owner).Pose;
        bad.Do("set_pose", owner, moved with { PositionMillimeters = moved.PositionMillimeters with { X = moved.PositionMillimeters.X + 1 } })
            .Do("spawn_thing", owner, "Air Trainer", "SpawnerB", 1, "AirTrainer", 0x7fc00001);
        Check(bad.State.Snapshot.NextActorId == actual.Actors.Count + 1, "Invalid Plane creation preserves the next identity.");

        var grounds = Case("actual/ground-death", actual)!;
        Level100ActorId tank = grounds.State.Snapshot.Actors.First(a => a.DefinitionName == "Target Tank").ActorId;
        grounds.Do("shutdown_ground_unit", tank).Do("set_health", tank, 0).Do("report_ground_unit_died", tank).Do("restore_snapshot")
            .Do("report_ground_unit_died", tank).Do("shutdown_ground_unit", tank).Do("shutdown_ground_unit", tank).Do("restore_snapshot").Do("drain_facts");
    }

    private void RestoreCases(Level100ActorDefinitionSet actual)
    {
        Level100ActorRegistrySnapshot b = new Level100ActorRegistry(actual).Snapshot;
        void R(string name, Level100ActorRegistrySnapshot? input) => Case("restore/" + name, actual, input, true)?.Do("restore_snapshot");
        Level100ActorSnapshot first = b.Actors[0]; Level100ActorBaseStateSnapshot firstBase = b.BaseStates[0];
        Level100ActorRegistrySnapshot Actor(Level100ActorSnapshot? value) => b with { Actors = b.Actors.Select((a, i) => i == 0 ? value! : a).ToArray() };
        Level100ActorRegistrySnapshot Base(ThingActorBaseStateSnapshot? value) => b with { BaseStates = b.BaseStates.Select((a, i) => i == 0 ? a with { State = value! } : a).ToArray() };
        R("valid", b); R("null", null); R("identity-null", b with { DefinitionSetIdentitySha256 = null! });
        R("identity-case", b with { DefinitionSetIdentitySha256 = b.DefinitionSetIdentitySha256.ToUpperInvariant() });
        foreach (int next in new[] { int.MinValue, -1, 0, 1, b.NextActorId - 1, b.NextActorId + 1, int.MaxValue }) R("next-id/" + next, b with { NextActorId = next });
        foreach (long next in new[] { long.MinValue, -1, 0, 2, long.MaxValue }) R("next-fact/" + next, b with { NextFactSequence = next });
        R("null-actors", b with { Actors = null! }); R("null-facts", b with { PendingFacts = null! }); R("null-bases", b with { BaseStates = null! });
        R("null-collections-order", b with { Actors = null!, PendingFacts = null!, BaseStates = null! });
        R("null-actor", Actor(null)); R("null-fact", b with { PendingFacts = new Level100ActorFactSnapshot[] { null! } });
        R("null-base", b with { BaseStates = new Level100ActorBaseStateSnapshot[] { null! } }); R("null-state", Base(null));
        R("duplicate-base", b with { BaseStates = b.BaseStates.Concat([firstBase]).ToArray() });
        R("duplicate-base-before-id", b with { Actors = [first with { ActorId = new(0) }], BaseStates = [firstBase, firstBase] });
        R("duplicate-actor", b with { Actors = b.Actors.Concat([first]).ToArray() });
        R("duplicate-actor-base-refusal-first", b with { Actors = [first, first], BaseStates = [firstBase with { State = firstBase.State with { CurrentPose = null! } }] });
        R("missing-base", b with { BaseStates = b.BaseStates.Skip(1).ToArray() });
        R("extra-base", b with { BaseStates = b.BaseStates.Concat([firstBase with { ActorId = new(b.NextActorId + 1) }]).ToArray() });
        R("missing-actor", b with { Actors = b.Actors.Skip(1).ToArray() });
        R("empty", b with { Actors = [], BaseStates = [], NextActorId = 1 });
        R("unsorted", b with { Actors = b.Actors.Reverse().ToArray(), BaseStates = b.BaseStates.Reverse().ToArray() });
        foreach (int id in new[] { int.MinValue, -1, 0, b.NextActorId, int.MaxValue }) R("actor-id/" + id, Actor(first with { ActorId = new(id) }));
        R("actor-null-pose", Actor(first with { Pose = null! })); R("actor-nonfinite-pose", Actor(first with { Pose = first.Pose with { BasisFloatBits = first.Pose.BasisFloatBits with { Row1Y = 0x7fc00001 } } }));
        R("actor-position", Actor(first with { Pose = first.Pose with { PositionMillimeters = new(1, 2, 3) } }));
        R("actor-velocity", Actor(first with { Pose = first.Pose with { LinearVelocityMillimetersPerTick = new(1, 2, 3) } }));
        R("actor-angular", Actor(first with { Pose = first.Pose with { AngularVelocityMicroRadiansPerTick = new(1, 2, 3) } }));
        R("actor-basis", Actor(first with { Pose = first.Pose with { BasisFloatBits = first.Pose.BasisFloatBits with { Row0Y = first.Pose.BasisFloatBits.Row0Y ^ int.MinValue } } }));
        R("actor-health", Actor(first with { Health = -1 })); R("actor-health-max", Actor(first with { Health = int.MaxValue }));
        foreach (int lifecycle in new[] { -1, 0, 1, 2, 3, 4, int.MaxValue }) R("lifecycle/" + lifecycle, Actor(first with { Lifecycle = (Level100ActorLifecycle)lifecycle }));
        foreach (uint mask in new uint[] { 0, 1, 4, 8, 12, uint.MaxValue }) R("leaf-mask/" + mask, Actor(first with { ThingTypeMask = mask }));
        foreach (string? text in new string?[] { null, "", "missing", "x\0y", "\ud800", "\udc00", "Flyby", "LevelScript" })
        {
            string label = text is null ? "null" : Convert.ToHexString(System.Text.Encoding.Unicode.GetBytes(text));
            R("identity/" + label, Actor(first with { DefinitionIdentity = text! })); R("name/" + label, Actor(first with { Name = text! }));
            R("definition/" + label, Actor(first with { DefinitionName = text })); R("script/" + label, Actor(first with { ScriptName = text }));
            R("mesh/" + label, Actor(first with { MeshBinding = text })); R("spawner/" + label, Actor(first with { SpawnerName = text }));
        }
        R("static-toggle", Actor(first with { IsStatic = !first.IsStatic })); R("active-toggle", Actor(first with { Active = !first.Active }));
        R("objective-toggle", Actor(first with { IsObjective = !first.IsObjective }));
        R("group-unknown", Actor(first with { TargetGroup = (Level100MissionTargetGroup)999 }));
        R("ordinal", Actor(first with { TargetOrdinal = 1 })); R("trigger-unknown", Actor(first with { Trigger = (Level100MissionTrigger)999 }));
        R("trigger-changed", Actor(first with { Trigger = Level100MissionTrigger.FiringRange }));
        R("trigger-entered-without-trigger", Actor(first with { TriggerEntered = true }));
        R("trigger-entry-without-trigger", Actor(first with { TriggerEntryJetModeState = Level100MissionJetModeState.InJetMode }));
        R("trigger-event-without-trigger", Actor(first with { TriggerEventDispatched = true }));
        R("spawn-owner-missing", Actor(first with { SpawnOwnerId = new(-1) }));
        foreach (ThingActorFlags flags in new[] { ThingActorFlags.Dying, ThingActorFlags.DeclaredShutdown, (ThingActorFlags)ushort.MaxValue }) R("base-flags/" + flags, Base(firstBase.State with { Flags = flags }));
        R("base-invalid-before-actor-health", Base(firstBase.State with { CurrentPose = null! }) with { Actors = Actor(first with { Health = -1 }).Actors });

        Level100ActorId planeId = b.Actors.First(a => a.DefinitionName == "Air Trainer").ActorId;
        var planeBase = b.BaseStates.First(item => item.ActorId == planeId);
        R("plane-without-creation-words", b with { BaseStates = b.BaseStates.Select(item => item.ActorId == planeId
            ? item with { State = item.State with { RetailPoses = null, RetailMotion = null, RetailPlane = null } } : item).ToArray() });
        R("raw-plane-under-static-identity", b with { Actors = b.Actors.Select(a => a.ActorId == first.ActorId
            ? a with { Pose = b.Actors.First(p => p.ActorId == planeId).Pose } : a).ToArray(),
            BaseStates = b.BaseStates.Select(item => item.ActorId == first.ActorId ? item with { State = planeBase.State } : item).ToArray() });
        Case("restore/plane-with-disabled-admission", actual, b, true, support: false);
        var groundInvalid = new Level100ActorRegistry(actual);
        var groundId = groundInvalid.Snapshot.Actors.First(a => a.DefinitionName == "Target Tank").ActorId;
        Call(groundInvalid, "ReportGroundUnitDied", [groundId]);
        R("ground-pending-with-life", groundInvalid.Snapshot);
        var groundState = groundInvalid.Snapshot;
        R("ground-pending-with-shutdown", groundState with { Actors = groundState.Actors.Select(a => a.ActorId == groundId ? a with { Health = 0 } : a).ToArray(),
            BaseStates = groundState.BaseStates.Select(item => item.ActorId == groundId ? item with { State = item.State with { Flags = item.State.Flags | ThingActorFlags.DeclaredShutdown } } : item).ToArray() });

        var triggered = new Level100ActorRegistry(actual);
        Level100ActorId tid = triggered.Snapshot.Actors.First(a => a.Trigger.HasValue).ActorId;
        triggered.BeginTriggerDispatch(tid, (Level100MissionJetModeState)999);
        R("trigger-invalid-entry-value", triggered.Snapshot);
        triggered.MarkTriggerEventDispatched(tid); R("trigger-invalid-dispatched-entry", triggered.Snapshot);
        var spawnRun = new Level100ActorRegistry(actual);
        Level100SpawnDefinition spawn = actual.Spawns.First(s => s.DefinitionName == "Target Truck");
        Level100ActorId owner = spawnRun.Snapshot.Actors.First(a => a.DefinitionIdentity == spawn.OwnerDefinitionIdentity).ActorId;
        Level100ActorId spawned = spawnRun.SpawnThing(owner, spawn.DefinitionName, spawn.SpawnerName, 1, spawn.ScriptName).Single();
        var sb = spawnRun.Snapshot; var sa = spawnRun.GetActor(spawned);
        void S(string name, Level100ActorSnapshot actor) => R("spawn/" + name, sb with { Actors = sb.Actors.Select(a => a.ActorId == spawned ? actor : a).ToArray() });
        R("spawn-valid", sb);
        S("owner-missing", sa with { SpawnOwnerId = new(-1) }); S("owner-wrong", sa with { SpawnOwnerId = first.ActorId });
        S("name", sa with { Name = "bad" }); S("identity", sa with { DefinitionIdentity = "bad" });
        S("script-known-wrong", sa with { ScriptName = "Flyby" }); S("ordinal", sa with { TargetOrdinal = 0 });
        S("ordinal-high", sa with { TargetOrdinal = int.MaxValue }); S("static", sa with { IsStatic = true });
        S("trigger", sa with { Trigger = Level100MissionTrigger.TargetZone1 }); S("owner-null", sa with { SpawnOwnerId = null });
        var fact = new Level100ActorFactSnapshot(1, Level100ActorFactKind.Hit, first.ActorId, null, 4);
        foreach (long sequence in new[] { long.MinValue, -1, 0, 1, 2, long.MaxValue }) R("fact-sequence/" + sequence, b with { NextFactSequence = 2, PendingFacts = [fact with { Sequence = sequence }] });
        foreach (int kind in new[] { -1, 0, 1, 2, 3, 4, 5, int.MaxValue }) R("fact-kind/" + kind, b with { NextFactSequence = 3, PendingFacts = [fact with { Kind = (Level100ActorFactKind)kind }] });
        R("fact-actor", b with { NextFactSequence = 2, PendingFacts = [fact with { ActorId = new(-1) }] });
        R("fact-other", b with { NextFactSequence = 2, PendingFacts = [fact with { OtherActorId = new(-1) }] });
        foreach (uint mask in new uint[] { 0, 1, 4, 8, 12, uint.MaxValue }) R("fact-mask/" + mask, b with { NextFactSequence = 2, PendingFacts = [fact with { OtherActorId = first.ActorId, OtherThingTypeMask = mask }] });
        R("fact-duplicate", b with { NextFactSequence = 2, PendingFacts = [fact, fact] });
        R("facts-unsorted", b with { NextFactSequence = 4, PendingFacts = [fact with { Sequence = 3 }, fact, fact with { Sequence = 2 }] });
        Case("sequence/int64-wrap", actual, b with { NextFactSequence = long.MaxValue }, true)!
            .Do("report_hit", first.ActorId, null, 0u).Do("report_hit", first.ActorId, null, 4u).Do("drain_facts").Do("restore_snapshot");
    }

    private void ConstructorCases(Level100ActorDefinitionSet actual)
    {
        var trainer = actual.Actors.Single(a => a.Name == "Air Trainer");
        Level100ActorDefinitionSet Replace(Level100ActorDefinition changed) => new(actual.Actors.Select(a => a.DefinitionIdentity == changed.DefinitionIdentity ? changed : a), actual.Spawns, actual.WaypointPaths, actual.MotionDefinitions);
        Case("constructor/plane-nonzero-linear", Replace(trainer with { InitialPose = trainer.InitialPose with { LinearVelocityMillimetersPerTick = new(1, 0, 0) } }));
        Case("constructor/plane-nonzero-angular", Replace(trainer with { InitialPose = trainer.InitialPose with { AngularVelocityMicroRadiansPerTick = new(0, 1, 0) } }));
        var water = trainer with { AuthoredTransform = trainer.AuthoredTransform with { RetailPositionFloatBits = new(0x44160000, 0x44160000, 0x42c80000) }, InitialPose = trainer.InitialPose with { PositionMillimeters = new(311313, -110000, 356750) } };
        var seated = Case("constructor/ground-then-current-water", Replace(water))!;
        var raw = seated.State.GetBaseState(seated.State.GetThingRef("Air Trainer")!.Value).RetailPoses!;
        Check(raw.Old.PositionFloatBits.Z == 0 && raw.Current.PositionFloatBits.Z == BitConverter.SingleToInt32Bits(Level100Terrain.Instance.WaterLevel), "Ground teleport precedes current-only water clamp.");
        Case("constructor/no-support", actual, support: false)?.Do("get_plane_state", new Level100ActorId(trainer.AuthoredOrder + 1));
        var noExit = new Level100ActorDefinitionSet(actual.Actors, actual.Spawns.Select(s => s with { SpawnerExitWaypoints = null }), actual.WaypointPaths, actual.MotionDefinitions);
        var sequence = Case("constructor/missing-exits", noExit)!;
        Level100ActorId owner = sequence.State.GetThingRef("Airfield")!.Value;
        sequence.Do("spawn_thing", owner, "Air Trainer", "SpawnerB", 1, "AirTrainer", 0);
        Level100ActorId id = sequence.State.Snapshot.Actors.Last().ActorId;
        sequence.Do("get_plane_spawner_exit_point", id, 1).Do("get_plane_spawner_exit_point", id, 0);
    }

    private void RawAndConstructionCases(Level100ActorDefinitionSet actual)
    {
        Level100ActorDefinition seed = actual.Actors[0] with { AuthoredOrder = 0, DefinitionIdentity = "raw\0\ud800", Name = "name\0\udc00", DefinitionName = null, ScriptName = null, MeshBinding = "", ThingTypeMask = 8,
            IsStatic = false, InitialHealth = 123, TargetGroup = Level100MissionTargetGroup.None, TargetOrdinal = 0, Trigger = null,
            InitialPose = actual.Actors[0].InitialPose with { LinearVelocityMillimetersPerTick = default, AngularVelocityMicroRadiansPerTick = default } };
        Level100ActorDefinitionSet Set(int world, bool duplicate = false) => new(duplicate ? [seed, seed with { AuthoredOrder = 1, DefinitionIdentity = "raw\0\udc00" }] : [seed], [], worldNumber: world);
        var raw = Case("raw/nul-and-surrogate-name", Set(100))!;
        raw.Do("get_thing_ref", seed.Name).Do("get_thing_ref", "name\0\ud800").Do("get_thing_ref", "name").Do("restore_snapshot");
        Case("raw/duplicate-names", Set(100, true))!.Do("get_thing_ref", seed.Name).Do("restore_snapshot");
        int unsupported = RetailWorldCatalog.Nodes.First(n => n.WorldNumber is not (100 or 110 or 200 or 300)).WorldNumber;
        Case("world/unsupported-program", Set(unsupported))!.Do("set_actor_script", new Level100ActorId(-1), "Flyby").Do("restore_snapshot");
        foreach (int world in new[] { 110, 200, 300 }) Case("world/program-admission/" + world, Set(world))!.Do("set_actor_script", new Level100ActorId(1), ProgramNames(world)!.First()).Do("restore_snapshot");
        var construction = Case("construction/same-owner-and-refusal", Set(110), terrain: 110, support: false)!;
        Level100ActorId id = new(1);
        object first = Call(construction.State, "GetConstructionState", [id])!;
        Check(ReferenceEquals(first, Call(construction.State, "GetConstructionState", [id])), "Guarded construction getter returns the existing allocation.");
        construction.Do("get_construction_state", id).Do("construction_begin", id, new RetailActorPoseSnapshot(new(0x43905800, 0x43734000, unchecked((int)0xc1200000)), seed.InitialPose.BasisFloatBits), 8u)
            .Do("get_construction_state", id).Do("get_actor", id).Do("set_health", id, -1).Do("set_health", id, 1)
            .Do("set_actor_script", id, "unknown").Do("set_actor_script", id, ProgramNames(110)!.First())
            .Do("report_hit", id, null, uint.MaxValue).Do("make_visible", id).Do("report_died", id).Do("restore_snapshot");
    }

    private static object? Operation(Level100ActorRegistry state, Level100ActorDefinitionSet definitions, int terrain, bool support, string operation, object?[] args)
    {
        if (operation == "restore_snapshot") return Construct(definitions, state.Snapshot, true, terrain, support).Snapshot;
        if (operation == "construction_begin")
        {
            var actor = (ThingActorBaseState)Call(state, "GetConstructionState", [args[0]])!;
            return Call(actor, "BeginRetailInitialization", [args[1], args[1], args[2]]);
        }
        string method = operation == "set_actor_script" ? "SetScript" : string.Concat(operation.Split('_').Select(p => char.ToUpperInvariant(p[0]) + p[1..]));
        object? result = Call(state, method, args);
        return result is ThingActorBaseState actorState ? actorState.Snapshot : result;
    }
    private static Level100ActorRegistry Construct(Level100ActorDefinitionSet definitions, Level100ActorRegistrySnapshot? snapshot, bool restore, int terrain, bool support)
    {
        object?[] args = restore
            ? [definitions, snapshot, terrain == 100 ? RetailWorldTerrain.World100 : RetailWorldTerrain.World110, support]
            : [definitions, terrain == 100 ? RetailWorldTerrain.World100 : RetailWorldTerrain.World110, support];
        Type[] types = restore ? [typeof(Level100ActorDefinitionSet), typeof(Level100ActorRegistrySnapshot), typeof(RetailWorldTerrain), typeof(bool)]
            : [typeof(Level100ActorDefinitionSet), typeof(RetailWorldTerrain), typeof(bool)];
        ConstructorInfo constructor = typeof(Level100ActorRegistry).GetConstructor(Instance, null, types, null) ?? throw new MissingMethodException("Registry constructor.");
        return (Level100ActorRegistry)Unwrap(() => constructor.Invoke(args))!;
    }
    private static object? Call(object instance, string method, object?[] args)
    {
        MethodInfo member = instance.GetType().GetMethod(method, Instance) ?? throw new MissingMethodException(instance.GetType().Name, method);
        return Unwrap(() => member.Invoke(instance, args));
    }
    private static object? Unwrap(Func<object?> action)
    {
        try { return action(); }
        catch (TargetInvocationException e) when (e.InnerException is not null) { ExceptionDispatchInfo.Capture(e.InnerException).Throw(); throw; }
    }
    private static M Capture(Func<object?> action)
    {
        try { return new M { ["ok"] = true, ["value"] = action() }; }
        catch (Exception error)
        {
            if (error is not (ArgumentException or InvalidOperationException or KeyNotFoundException or NotSupportedException or OverflowException)) throw;
            return new M { ["ok"] = false, ["error_type"] = error.GetType().Name,
                ["parameter"] = error is ArgumentException argument ? argument.ParamName ?? "" : "" };
        }
    }
    private static IReadOnlyCollection<string>? ProgramNames(int world)
    {
        if (world is not (100 or 110 or 200 or 300)) return null;
        Type owner = typeof(Level100ActorRegistry).Assembly.GetType("OnslaughtRebuild.Core.Level100MissionProgram") ?? throw new TypeLoadException("Mission program owner.");
        MethodInfo member = owner.GetMethod("ProgramNamesFor", Static) ?? throw new MissingMethodException("ProgramNamesFor");
        return (IReadOnlyCollection<string>)Unwrap(() => member.Invoke(null, [world]))!;
    }
    private static M ContextFacts(int world) => new()
    {
        ["mission_program_world_number"] = world, ["mission_program_names"] = new Raw(ProgramNames(world)),
        ["contact_definitions"] = Level100ContactCatalog.Instance.Definitions.Select(d => new M
        { ["definition_name"] = new Raw(d.Name), ["kind"] = (int)d.Kind, ["maximum_life_float_bits"] = unchecked((int)d.MaximumLifeBits) }).ToArray(),
    };
    private static M DefinitionFacts(Level100ActorDefinitionSet value) => new()
    {
        ["world_number"] = value.WorldNumber, ["identity_sha256"] = value.IdentitySha256,
        ["actors"] = value.Actors, ["spawns"] = value.Spawns, ["waypoint_paths"] = value.WaypointPaths, ["motion_definitions"] = value.MotionDefinitions,
    };
    private static Variant Pack(object? value, bool rawText = false)
    {
        if (value is null) return default;
        if (value is Raw raw) return Pack(raw.Value, true);
        if (value is bool boolean) return boolean;
        if (value is string text) return rawText ? Variant.From(text.Select(c => (int)c).ToArray()) : Variant.From(text);
        if (value is int integer) return integer;
        if (value is long wide) return wide;
        if (value is uint unsigned) return (long)unsigned;
        if (value is Enum enumeration) return Convert.ToInt32(enumeration);
        if (value is Level100ActorId id) return id.Value;
        if (value is IDictionary map)
        {
            using D result = new();
            foreach (DictionaryEntry pair in map) { using Variant item = Pack(pair.Value, rawText); result.Add((string)pair.Key, item); }
            return Variant.From(result);
        }
        if (value is IEnumerable sequence)
        {
            using A result = new();
            foreach (object? child in sequence) { using Variant item = Pack(child, rawText); result.Add(item); }
            return Variant.From(result);
        }
        Type type = value.GetType();
        if (type.Namespace != "OnslaughtRebuild.Core") throw new NotSupportedException("Unadmitted fixture transport: " + type.FullName);
        using D record = new();
        foreach (PropertyInfo property in type.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            if (property.Name is "HorizontalPositionMillimeters" or "TagIndex" or "IsInvisible" or "IsDying" or "IsShuttingDown" or "LocalLastFrameMovement") continue;
            using Variant field = Pack(property.GetValue(value), property.Name != "DefinitionSetIdentitySha256");
            record.Add(Snake(property.Name), field);
        }
        return Variant.From(record);
    }
    private static string Snake(string name) => string.Concat(name.Select((c, i) => (i > 0 && char.IsUpper(c) ? "_" : "") + char.ToLowerInvariant(c)));
    private static M SourceHashes()
    {
        string root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "OnslaughtRebuild.Core"));
        var result = new M();
        foreach (string name in new[] { "Level100ActorRegistry.cs", "ThingActorBaseState.cs", "RetailWorldTerrain.cs", "RetailMeshPartPose.cs", "RetailPlaneMotion.cs", "Level100MissionProgram.cs", "Level100ContactMap.cs" }) result[name] = Hash(File.ReadAllBytes(Path.Combine(root, name)));
        return result;
    }
    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private static string Owned(string value)
    {
        string path = Path.GetFullPath(value), root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data"));
        if (path != value || !path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.Ordinal) || File.Exists(path) || Directory.Exists(path) || !Directory.Exists(Path.GetDirectoryName(path)))
            throw new ArgumentException("Fresh existing worktree-local output parent required.");
        for (DirectoryInfo? parent = new(Path.GetDirectoryName(path)!); parent is not null; parent = parent.Parent)
        { if (parent.LinkTarget is not null) throw new ArgumentException("Output ancestry cannot traverse links."); if (parent.FullName == root) break; }
        return path;
    }
    private void Check(bool value, string message) { _checks++; if (!value) throw new InvalidOperationException(message); }
}
