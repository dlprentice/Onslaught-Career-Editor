// SPDX-License-Identifier: GPL-3.0-or-later
using System.Collections;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Temporary exact value/identity oracle; original Core and manifest
/// implementations remain unchanged. Outputs are private and object-free.</summary>
public sealed partial class ActorDefinitionReferenceChecks : Node
{
    private static readonly byte[] s_identityMagic = Encoding.ASCII.GetBytes("ONSLAUGHT-LEVEL100-ACTOR-DEFINITIONS");
    private int _checks;
    private sealed record Input(Level100ActorDefinition[]? Actors, Level100SpawnDefinition[]? Spawns,
        Level100WaypointPathDefinition[]? WaypointPaths, Level100ActorMotionDefinition[]? MotionDefinitions, int WorldNumber = 100);

    public override async void _Ready()
    {
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2, "Two fresh owned output paths are required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            Check(fixturePath != reportPath && !Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Distinct outputs and headless runtime are required.");
            Godot.Input.MouseModeEnum pointer = Godot.Input.MouseMode;
            string manifestPath = ProjectSettings.GlobalizePath("res://Assets/Level100/StaticWorld/level100-static-world.json");
            byte[] bytes = File.ReadAllBytes(manifestPath);
            string inputHash = Hex(bytes);
            Check(inputHash == Level100ActorDefinitionManifest.ExpectedManifestSha256.ToLowerInvariant(), "Unchanged pinned manifest identity.");
            Level100ActorDefinitionSet actual = Level100ActorDefinitionManifest.Decode(bytes);
            using Variant actualFacts = Facts(actual);
            byte[] actualCanonical = IdentityBytes(actual.Actors, actual.Spawns, actual.WaypointPaths, actual.MotionDefinitions);
            Check(Hex(actualCanonical) == actual.IdentitySha256, "Copied byte emitter matches the unchanged production identity.");
            using Variant allegiance = Value(Level100ActorDefinitionManifest.DecodeAuthoredAllegiance(bytes));
            using A cases = new();
            int acceptedCases = 0, refusedCases = 0;
            Input original = BaseInput();
            void Case(string name, Input input)
            {
                using Variant inputFacts = Value(input);
                using D row = new() { ["name"] = name, ["input"] = inputFacts };
                Level100ActorDefinitionSet? set = null;
                try { set = Construct(input); }
                catch (Exception exception)
                {
                    refusedCases++;
                    row["ok"] = false; row["error_type"] = exception.GetType().Name;
                    row["parameter"] = exception is ArgumentException argument ? argument.ParamName ?? "" : "";
                }
                if (set is not null)
                {
                    acceptedCases++;
                    // Transport or copied-emitter defects must abort the oracle;
                    // only the unchanged constructor establishes a refusal.
                    byte[] canonical = IdentityBytes(set.Actors, set.Spawns, set.WaypointPaths, set.MotionDefinitions);
                    Check(Hex(canonical) == set.IdentitySha256, name + " copied identity bytes match production.");
                    using Variant facts = Facts(set);
                    row["ok"] = true; row["snapshot"] = facts; row["bytes"] = canonical;
                }
                Append(cases, row);
            }
            Cases(original, Case);
            using A lookups = Lookups(actual);
            using A refusals = ManifestRefusals(bytes);
            CopyChecks(original);
            Check(Hex(File.ReadAllBytes(manifestPath)) == inputHash && Godot.Input.MouseMode == pointer, "Read-only input and pointer ownership unchanged.");
            using D fixture = new()
            {
                ["schema"] = 1, ["completed"] = new A { "actor_definition_reference" }, ["manifest_path"] = manifestPath,
                ["manifest_sha256"] = inputHash, ["actual"] = actualFacts, ["actual_bytes"] = actualCanonical,
                ["allegiance"] = allegiance, ["cases"] = cases, ["lookups"] = lookups, ["manifest_refusals"] = refusals,
                ["case_counts"] = new D { ["accepted"] = acceptedCases, ["refused"] = refusedCases },
            };
            using Variant fixtureValue = fixture;
            Check(ObjectFree(fixtureValue), "No native object enters fixture transport.");
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot create actor fixture.")) file.StoreVar(fixtureValue, false);
            using D report = new() { ["schema"] = 1, ["failure_count"] = 0, ["completed"] = new A { "actor_definition_reference" },
                ["counts"] = new D { ["reference"] = _checks, ["cases"] = cases.Count, ["lookups"] = lookups.Count,
                    ["accepted"] = acceptedCases, ["refused"] = refusedCases,
                    ["manifest_refusals"] = refusals.Count, ["actual_identity_bytes"] = actualCanonical.Length }, ["identity_sha256"] = actual.IdentitySha256 };
            using (var file = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot create actor report.")) file.StoreString(Json.Stringify(report));
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"ACTOR_DEFINITION_REFERENCE_CHECKS: {_checks} passed; {cases.Count} construction and {lookups.Count} lookup cases; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private static Level100ActorDefinitionSet Construct(Input input) => new(input.Actors!, input.Spawns!, input.WaypointPaths, input.MotionDefinitions, input.WorldNumber);
    private static Level100FloatBasis3Bits Basis() => new(0x3f800000, 0, int.MinValue, 0, 0x3f800000, 0, 0, 0, 0x3f800000);
    private static Level100SpawnerTransform Emitter() => new(new(int.MinValue, 0x3f000000, 0), Basis());
    private static Level100ActorPoseSnapshot Pose() => new(new(int.MinValue, 2, int.MaxValue), Basis(), new(-1, 0, 1), new(2, 3, 4));
    private static Level100ActorWeaponMountDefinition Mount() => new(new("Weapon", "GunA", 0xffffffff), 1, new(Emitter().LocalPositionFloatBits, Basis()));
    private static Input BaseInput()
    {
        Level100ActorDefinition actor = new(0, "owner", "Owner", "Ground", null, "", 0, true, true, 10,
            new(new(int.MinValue, 0, 0), new(0, 0, 0), Basis()), Pose(), Level100MissionTargetGroup.None, 0, null);
        Level100SpawnDefinition spawn = new(0, "spawn", "owner", "Plane", "SpawnerA", "Spawn", null, 0, true, 10,
            Pose(), Emitter(), Level100MissionTargetGroup.None, 0, 0);
        Level100WaypointPathDefinition path = new("Route", new[] { 43, 42, 41 }.Select(i => new Level100WaypointPointDefinition(i,
            new(i, -i, 2 * i), new(int.MinValue, 0, 0x3f800000, 1))).ToArray(), new[] { 41, 42, 43 }, false);
        Level100ActorMotionDefinition ground = new(0, "Ground", Level100ActorMotionClass.GroundVehicle, 3, 0, 0x401000, 1000,
            0x3f800000, 0x3e800000, 1, 2);
        Level100ActorMotionDefinition plane = new(1, "Plane", Level100ActorMotionClass.Plane, 1, 1, 0x401010, 500, null, null, null, null);
        return new([actor, actor with { AuthoredOrder = 1, DefinitionIdentity = "plane", Name = "Plane", DefinitionName = "Plane", IsStatic = false }],
            [spawn], [path], [ground, plane]);
    }

    private static void Cases(Input b, Action<string, Input> add)
    {
        var a = b.Actors![0]; var s = b.Spawns![0]; var p = b.WaypointPaths![0]; var g = b.MotionDefinitions![0]; var m = b.MotionDefinitions![1];
        void Actor(string name, Level100ActorDefinition? value) => add("actor/" + name, b with { Actors = [value!, b.Actors![1]] });
        void Spawn(string name, Level100SpawnDefinition? value) => add("spawn/" + name, b with { Spawns = [value!] });
        void Path(string name, Level100WaypointPathDefinition? value) => add("path/" + name, b with { WaypointPaths = [value!] });
        void Motion(string name, Level100ActorMotionDefinition? value) => add("motion/" + name, b with { MotionDefinitions = [g, value!] });
        add("base-format6", b); add("null-actors", b with { Actors = null }); add("null-spawns", b with { Spawns = null });
        add("empty-actors", b with { Actors = [] }); add("no-spawns", b with { Spawns = [] });
        add("null-paths-motions", b with { WaypointPaths = null, MotionDefinitions = null });
        add("empty-paths-motions", b with { WaypointPaths = [], MotionDefinitions = [] });
        foreach (RetailWorldNode node in RetailWorldCatalog.Nodes) add("world/" + node.WorldNumber, b with { WorldNumber = node.WorldNumber });
        foreach (int world in new[] { int.MinValue, -1, 0, 99, 101, 801, int.MaxValue }) add("bad-world/" + world, b with { WorldNumber = world });
        Actor("null", null); Actor("order", a with { AuthoredOrder = 1 }); Actor("null-name", a with { Name = null! });
        Actor("null-authored", a with { AuthoredTransform = null! }); Actor("null-pose", a with { InitialPose = null! });
        Actor("mask-unknown", a with { ThingTypeMask = 1 }); Actor("mask-both", a with { ThingTypeMask = 12 });
        Actor("health-negative", a with { InitialHealth = -1 }); Actor("health-max", a with { InitialHealth = int.MaxValue });
        Actor("ordinal-negative", a with { TargetOrdinal = -1 }); Actor("none-nonzero", a with { TargetOrdinal = 1 });
        Actor("group-no-ordinal", a with { TargetGroup = Level100MissionTargetGroup.StaticTargets });
        Actor("unknown-group", a with { TargetGroup = (Level100MissionTargetGroup)999, TargetOrdinal = 1 });
        Actor("unknown-trigger", a with { Trigger = (Level100MissionTrigger)(-77) });
        Actor("trigger-and-group", a with { Trigger = Level100MissionTrigger.FiringRange, TargetGroup = Level100MissionTargetGroup.StaticTargets, TargetOrdinal = 1 });
        add("actor/duplicate-identity", b with { Actors = [a, b.Actors![1] with { DefinitionIdentity = a.DefinitionIdentity }] });
        add("actor/ordinal-case-sensitive", b with { Actors = [a, b.Actors![1] with { DefinitionIdentity = "OWNER" }] });
        foreach (string? text in new string?[] { null, "", " ", "\u0085\u00a0", "\u200b", "x\0y", "\ud800", "\udc00", "\ud83d\ude80", "é", "e\u0301", "I", "ı", "\ufeff", new('x', 140) })
        {
            string label = text is null ? "null" : string.Concat(text.Select(unit => ((int)unit).ToString("X4")));
            Actor("identity-" + label, a with { DefinitionIdentity = text! });
            add("actor/content-key-" + label, b with { Actors = [a with { DefinitionIdentity = text! }, b.Actors![1]], Spawns = [] });
            Actor("name-" + label, a with { Name = text! });
            Actor("script-" + label, a with { ScriptName = text });
            add("actor/definition-" + label, b with { Actors = [a with { DefinitionName = text }, b.Actors![1]], MotionDefinitions = [] });
        }
        add("actor/distinct-unpaired-surrogate-keys", b with
        {
            Actors = [a with { DefinitionIdentity = "\ud800" }, b.Actors![1] with { DefinitionIdentity = "\udc00" }], Spawns = [],
        });
        foreach (string text in new[] { "x\0y", "\ud800", "\udc00", "\ud83d\ude80", "e\u0301" })
        {
            string label = string.Concat(text.Select(unit => ((int)unit).ToString("X4")));
            Path("content-key-" + label, p with { Name = text });
            Spawn("content-keys-" + label, s with { DefinitionIdentity = text, DefinitionName = text, SpawnerName = text, ScriptName = text });
            add("motion/content-key-" + label, b with
            {
                Actors = [a with { DefinitionName = text }, b.Actors![1]], MotionDefinitions = [g with { DefinitionName = text }, m],
            });
        }
        foreach (int word in new[] { 0, int.MinValue, 1, 0x7f7fffff, 0x7f800000, unchecked((int)0xff800000), 0x7fc00001 })
        {
            Actor("position-word/" + word, a with { AuthoredTransform = a.AuthoredTransform with { RetailPositionFloatBits = a.AuthoredTransform.RetailPositionFloatBits with { X = word } } });
            Actor("basis-word/" + word, a with { InitialPose = a.InitialPose with { BasisFloatBits = a.InitialPose.BasisFloatBits with { Row2Y = word } } });
            add("ground-speed/" + word, b with { MotionDefinitions = [g with { MaximumSpeedFloatBits = word }, m] });
        }
        Spawn("null", null); Spawn("order", s with { AuthoredOrder = 1 }); Spawn("owner-missing", s with { OwnerDefinitionIdentity = "missing" });
        Spawn("null-emitter", s with { AuthoredEmitterTransform = null! }); Spawn("null-pose", s with { InitialPose = null! });
        Spawn("unknown-mask", s with { ThingTypeMask = 16 }); Spawn("negative-health", s with { InitialHealth = -1 });
        Spawn("none-has-max", s with { MaximumGroupActors = 1 }); Spawn("none-has-ordinal", s with { FixedTargetOrdinal = 1 });
        Spawn("group-no-max", s with { TargetGroup = Level100MissionTargetGroup.AirTrainer });
        Spawn("unknown-group", s with { TargetGroup = (Level100MissionTargetGroup)(-99), MaximumGroupActors = 3 });
        Spawn("fixed-too-high", s with { TargetGroup = Level100MissionTargetGroup.AirTrainer, FixedTargetOrdinal = 4, MaximumGroupActors = 3 });
        Spawn("fixed-at-limit", s with { TargetGroup = Level100MissionTargetGroup.AirTrainer, FixedTargetOrdinal = 3, MaximumGroupActors = 3 });
        add("spawn/duplicate-identity", b with { Spawns = [s, s with { AuthoredOrder = 1, ScriptName = "Other" }] });
        add("spawn/duplicate-request", b with { Spawns = [s, s with { AuthoredOrder = 1, DefinitionIdentity = "other" }] });
        foreach (string? text in new string?[] { null, "", " \u0085", "Other", "SpawnerB", "SpawnerA\0" })
        {
            Spawn("spawner-name/" + text, s with { SpawnerName = text! });
            Spawn("script-name/" + text, s with { ScriptName = text! });
            Spawn("definition-name/" + text, s with { DefinitionName = text! });
        }
        Level100SpawnerExitPoint exit = new(1, Emitter());
        Spawn("exit-empty", s with { SpawnerExitWaypoints = [] });
        Spawn("exit-valid-format7", s with { SpawnerExitWaypoints = [exit] });
        Spawn("exit-order", s with { SpawnerExitWaypoints = [exit with { Selector = 2 }, exit] });
        Spawn("exit-reverse-order", s with { SpawnerExitWaypoints = [exit, exit with { Selector = 2 }] });
        Spawn("exit-duplicate", s with { SpawnerExitWaypoints = [exit, exit] });
        Spawn("exit-wrong-spawner", s with { SpawnerName = "Other", SpawnerExitWaypoints = [exit] });
        foreach (Level100SpawnerExitPoint? changed in new Level100SpawnerExitPoint?[] { null, exit with { Selector = 0 }, exit with { ModelTransform = null! },
            exit with { ModelTransform = exit.ModelTransform with { LocalPositionFloatBits = new(0x7fc00000, 0, 0) } } })
            Spawn("exit-invalid/" + changed, s with { SpawnerExitWaypoints = [changed!] });
        Path("null", null); Path("null-points", p with { Points = null! }); Path("empty-points", p with { Points = [] });
        Path("null-point", p with { Points = [null!, p.Points[1], p.Points[2]] });
        Path("negative-before-null", p with { Points = [p.Points[0] with { NodeIndex = -1 }, null!, p.Points[2]] });
        Path("null-before-negative", p with { Points = [null!, p.Points[1] with { NodeIndex = -1 }, p.Points[2]] });
        Path("nonfinite-before-null", p with { Points = [p.Points[0] with { RetailComponentsFloatBits = new(0, 0, 0, 0x7fc00000) }, null!, p.Points[2]] });
        Path("bad-name", p with { Name = "\u0085" }); Path("null-chain", p with { TargetChainNodeIndices = null! });
        Path("unknown-node", p with { TargetChainNodeIndices = [41, 42, 999] }); Path("duplicate-chain", p with { TargetChainNodeIndices = [41, 41, 43] });
        Path("negative-node", p with { Points = [p.Points[0] with { NodeIndex = -1 }, p.Points[1], p.Points[2]] });
        Path("nan-components", p with { Points = [p.Points[0] with { RetailComponentsFloatBits = new(0, 0, 0, 0x7fc00000) }, p.Points[1], p.Points[2]] });
        Path("closed", p with { IsClosed = true }); Path("serialized-walk", p with { TargetChainNodeIndices = [43, 42, 41] });
        add("path/duplicate-name", b with { WaypointPaths = [p, p] });
        add("path/ordered", b with { WaypointPaths = [p, p with { Name = "Second" }] });
        add("path/reverse-order", b with { WaypointPaths = [p with { Name = "Second" }, p] });
        Motion("null", null); Motion("order", m with { AuthoredOrder = 0 }); Motion("enum", m with { MotionClass = (Level100ActorMotionClass)4 });
        Motion("dropship", m with { MotionClass = Level100ActorMotionClass.Dropship }); Motion("owner-missing", m with { DefinitionName = "Absent" });
        Motion("ground-field-on-plane", m with { FullGuideBaseTicks = 1 }); Motion("vtable", m with { SteamClassVtableAddress = 0 });
        Motion("radius", m with { ArrivalRadiusMillimeters = 0 }); Motion("serialized-type", m with { BehaviorSerializedType = 0 });
        Motion("internal-id", m with { BehaviorInternalId = -1 });
        add("motion/duplicate", b with { MotionDefinitions = [g, g with { AuthoredOrder = 1 }] });
        add("motion/ground-guide-null", b with { MotionDefinitions = [g with { FullGuideBaseTicks = null }, m] });
        add("motion/ground-offset-zero", b with { MotionDefinitions = [g with { CoreGroundOriginOffsetMillimeters = 0 }, m] });
        Level100ActorWeaponMountDefinition mount = Mount();
        Motion("mount-empty-format8", m with { WeaponMounts = [] }); Motion("mount-valid-format8", m with { WeaponMounts = [mount] });
        Motion("mount-duplicates-allowed", m with { WeaponMounts = [mount, mount] });
        add("mounts-and-exits-format8", b with { Spawns = [s with { SpawnerExitWaypoints = [exit] }], MotionDefinitions = [g, m with { WeaponMounts = [mount] }] });
        add("motion/mount-empty-ground", b with { MotionDefinitions = [g with { WeaponMounts = [] }, m] });
        foreach (Level100ActorWeaponMountDefinition? changed in new Level100ActorWeaponMountDefinition?[] { null, mount with { Use = null! }, mount with { Selector = 0 },
            mount with { Use = mount.Use with { DefinitionName = " " } }, mount with { Use = mount.Use with { TagName = "SpawnerA" } },
            mount with { ModelPose = new(new(0, 0, 0), default) }, mount with { ModelPose = mount.ModelPose with { BasisFloatBits = Basis() with { Row0Z = 0 } } },
            mount with { ModelPose = mount.ModelPose with { PositionFloatBits = new(0x7f800000, 0, 0) } },
            mount with { Use = mount.Use with { RawCreationFlags = 0 } }, mount with { Selector = int.MaxValue } })
            Motion("mount-case/" + changed, m with { WeaponMounts = [changed!] });
    }

    private A Lookups(Level100ActorDefinitionSet set)
    {
        A rows = new();
        void Add(string method, object?[] arguments, Func<object?> action)
        {
            using Variant args = Value(arguments);
            using D row = new() { ["method"] = method, ["arguments"] = args };
            object? result = null;
            bool accepted = false;
            try { result = action(); accepted = true; }
            catch (Exception caught)
            {
                Exception error = caught is TargetInvocationException invocation ? invocation.InnerException! : caught;
                row["ok"] = false; row["error_type"] = error.GetType().Name;
                row["parameter"] = error is ArgumentException argument ? argument.ParamName ?? "" : "";
            }
            if (accepted)
            {
                using Variant value = Value(result);
                row["ok"] = true; row["value"] = value;
            }
            Append(rows, row);
        }
        object? Invoke(string name, params object?[] args) => typeof(Level100ActorDefinitionSet)
            .GetMethod(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)!.Invoke(set, args);
        foreach (var actor in set.Actors) Add("get_actor_definition", [actor.DefinitionIdentity], () => Invoke("GetActorDefinition", actor.DefinitionIdentity));
        foreach (var spawn in set.Spawns)
        {
            Add("get_spawn_definition", [spawn.DefinitionIdentity], () => Invoke("GetSpawnDefinition", spawn.DefinitionIdentity));
            object?[] request = [spawn.OwnerDefinitionIdentity, spawn.DefinitionName, spawn.SpawnerName, spawn.ScriptName];
            Add("find_spawn_definition", request, () => Invoke("FindSpawnDefinition", request));
        }
        foreach (var path in set.WaypointPaths)
        {
            Add("get_waypoint_path", [path.Name], () => set.GetWaypointPath(path.Name));
            for (int index = -1; index <= path.Points.Count; index++)
            { int captured = index; Add("chain_point", [path.Name, index], () => path.ChainPoint(captured)); }
        }
        foreach (var motion in set.MotionDefinitions)
        {
            Add("get_motion_definition", [motion.DefinitionName], () => set.GetMotionDefinition(motion.DefinitionName));
            Add("find_motion_definition", [motion.DefinitionName], () => Invoke("FindMotionDefinition", motion.DefinitionName));
        }
        foreach (string? text in new string?[] { null, "", "missing", "air trainer", "Air Trainer\0", "\ud800" })
        {
            Add("get_actor_definition", [text], () => Invoke("GetActorDefinition", text));
            Add("get_spawn_definition", [text], () => Invoke("GetSpawnDefinition", text));
            Add("get_waypoint_path", [text], () => set.GetWaypointPath(text!));
            Add("get_motion_definition", [text], () => set.GetMotionDefinition(text!));
            Add("find_motion_definition", [text], () => Invoke("FindMotionDefinition", text));
            Add("find_spawn_definition", [text, text, text, text], () => Invoke("FindSpawnDefinition", text, text, text, text));
        }
        return rows;
    }

    private A ManifestRefusals(byte[] source)
    {
        A rows = new();
        void Add(string kind, int amount)
        {
            byte[]? changed = kind switch { "null" => null, "prefix" => source[..amount], "oversize" => new byte[amount],
                "append" => [.. source, 0], "flip" => (byte[])source.Clone(), _ => throw new InvalidOperationException() };
            if (kind == "flip") changed![amount] ^= 1;
            foreach (bool allegiance in new[] { false, true })
            {
                Exception? failure = null;
                try { if (allegiance) Level100ActorDefinitionManifest.DecodeAuthoredAllegiance(changed); else Level100ActorDefinitionManifest.Decode(changed); }
                catch (Exception error) { failure = error; }
                Check(failure is InvalidDataException, "Changed manifest fails its existing identity gate.");
                using D row = new() { ["kind"] = kind, ["amount"] = amount, ["allegiance"] = allegiance, ["error_type"] = failure!.GetType().Name };
                Append(rows, row);
            }
        }
        Add("null", 0); Add("prefix", 0); Add("prefix", 1); Add("prefix", source.Length - 1);
        Add("oversize", 512001); Add("append", 0); Add("flip", 0); Add("flip", source.Length / 2); Add("flip", source.Length - 1);
        return rows;
    }

    private void CopyChecks(Input source)
    {
        var exits = new List<Level100SpawnerExitPoint> { new(1, Emitter()) };
        var mounts = new List<Level100ActorWeaponMountDefinition> { Mount() };
        var points = source.WaypointPaths![0].Points.ToList(); var chain = source.WaypointPaths![0].TargetChainNodeIndices.ToList();
        var actors = source.Actors!.ToArray();
        var spawns = new[] { source.Spawns![0] with { SpawnerExitWaypoints = exits } };
        var motions = new[] { source.MotionDefinitions![0], source.MotionDefinitions![1] with { WeaponMounts = mounts } };
        var path = source.WaypointPaths![0] with { Points = points, TargetChainNodeIndices = chain };
        var set = new Level100ActorDefinitionSet(actors, spawns, [path], motions);
        string identity = set.IdentitySha256;
        actors[0] = actors[1]; spawns[0] = spawns[0] with { DefinitionIdentity = "changed" }; motions[1] = motions[0];
        exits.Clear(); mounts.Clear(); points.Clear(); chain.Clear();
        Check(set.Actors[0].AuthoredOrder == 0 && set.Spawns[0].DefinitionIdentity == "spawn" && set.Spawns[0].SpawnerExitWaypoints!.Count == 1 &&
            set.MotionDefinitions[1].WeaponMounts!.Count == 1 && set.WaypointPaths[0].Points.Count == 3 && set.WaypointPaths[0].TargetChainNodeIndices.Count == 3,
            "Constructor owns every mutable supplied collection.");
        Check(Hex(IdentityBytes(set.Actors, set.Spawns, set.WaypointPaths, set.MotionDefinitions)) == identity, "Caller mutations cannot invalidate the stored identity.");
    }

    private static Variant Facts(Level100ActorDefinitionSet set)
    {
        using Variant value = Value(new { set.WorldNumber, set.Actors, set.Spawns, set.WaypointPaths, set.MotionDefinitions });
        using D snapshot = value.AsGodotDictionary();
        snapshot["identity_sha256"] = set.IdentitySha256;
        return Variant.From(snapshot);
    }
    private static Variant Value(object? value)
    {
        if (value is null) return default;
        if (value is string text) return text.Select(unit => (int)unit).ToArray();
        if (value is bool boolean) return boolean;
        if (value is int signed) return signed;
        if (value is uint unsigned) return unsigned;
        if (value is Enum enumeration) return Convert.ToInt32(enumeration);
        if (value is IReadOnlyDictionary<string, int> map)
        {
            using D dictionary = new(); foreach (var pair in map) dictionary[pair.Key] = pair.Value;
            return Variant.From(dictionary);
        }
        if (value is IEnumerable sequence)
        {
            using A array = new();
            foreach (object? item in sequence) { using Variant converted = Value(item); array.Add(converted); }
            return Variant.From(array);
        }
        using D record = new();
        foreach (PropertyInfo property in value.GetType().GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            // These computed conveniences are not the authored record fields.
            if (property.Name is "HorizontalPositionMillimeters" or "TagIndex") continue;
            string name = string.Concat(property.Name.Select((c, i) => (i > 0 && char.IsUpper(c) ? "_" : "") + char.ToLowerInvariant(c)));
            using Variant field = Value(property.GetValue(value)); record[name] = field;
        }
        return Variant.From(record);
    }
    private static string Hex(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private static void Append(A array, D row) { using Variant value = row; array.Add(value); }
    private static bool ObjectFree(Variant value)
    {
        if (value.VariantType == Variant.Type.Object) return false;
        if (value.VariantType == Variant.Type.Array)
        { using A array = value.AsGodotArray(); for (int i = 0; i < array.Count; i++) { using Variant item = array[i]; if (!ObjectFree(item)) return false; } }
        if (value.VariantType == Variant.Type.Dictionary)
        {
            using D dictionary = value.AsGodotDictionary(); ICollection<Variant> keys = dictionary.Keys; using IDisposable? release = keys as IDisposable;
            foreach (Variant key in keys) using (key) using (Variant item = dictionary[key]) if (!ObjectFree(key) || !ObjectFree(item)) return false;
        }
        return true;
    }
    private string Owned(string path)
    {
        string result = Path.GetFullPath(path), owned = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data"));
        Check(path == result && result.StartsWith(owned + Path.DirectorySeparatorChar, StringComparison.Ordinal) && Directory.Exists(Path.GetDirectoryName(result)) && !File.Exists(result), "Fresh worktree-local output required.");
        string part = owned; foreach (string segment in Path.GetRelativePath(owned, result).Split(Path.DirectorySeparatorChar))
        { part = Path.Combine(part, segment); Check(new FileInfo(part).LinkTarget is null, "Output cannot traverse links."); }
        return result;
    }
    private void Check(bool value, string message) { _checks++; if (!value) throw new InvalidOperationException(message); }

    // Copied unchanged field emission from Level100ActorDefinitionSet.ComputeIdentity;
    // only the return is bytes. Every accepted fixture also checks the actual
    // original identity hash, so this helper cannot silently redefine it.
    private static byte[] IdentityBytes(
        IReadOnlyList<Level100ActorDefinition> actors,
        IReadOnlyList<Level100SpawnDefinition> spawns,
        IReadOnlyList<Level100WaypointPathDefinition> waypointPaths,
        IReadOnlyList<Level100ActorMotionDefinition> motionDefinitions)
    {
        using var stream = new MemoryStream();
        using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true))
        {
            writer.Write(s_identityMagic);
            bool hasSpawnerExits = spawns.Any(spawn => spawn.SpawnerExitWaypoints is not null);
            bool hasWeaponMounts = motionDefinitions.Any(definition => definition.WeaponMounts is not null);
            // Formats 6/7 remain byte-exact without mount input. Format 8
            // includes the format-7 exit fields even when all exits are null.
            writer.Write(hasWeaponMounts ? 8 : hasSpawnerExits ? 7 : 6);
            writer.Write(actors.Count);
            foreach (Level100ActorDefinition actor in actors)
            {
                writer.Write(actor.AuthoredOrder);
                writer.Write(actor.DefinitionIdentity);
                writer.Write(actor.Name);
                WriteNullableString(writer, actor.DefinitionName);
                WriteNullableString(writer, actor.ScriptName);
                WriteNullableString(writer, actor.MeshBinding);
                writer.Write(actor.ThingTypeMask);
                writer.Write(actor.IsStatic);
                writer.Write(actor.Active);
                writer.Write(actor.InitialHealth);
                WriteVector(writer, actor.AuthoredTransform.RetailPositionFloatBits);
                WriteVector(writer, actor.AuthoredTransform.RetailEulerFloatBits);
                WriteBasis(writer, actor.AuthoredTransform.RetailBasisFloatBits);
                WritePose(writer, actor.InitialPose);
                writer.Write((int)actor.TargetGroup);
                writer.Write(actor.TargetOrdinal);
                writer.Write(actor.Trigger.HasValue);
                if (actor.Trigger.HasValue)
                {
                    writer.Write((int)actor.Trigger.Value);
                }
            }

            writer.Write(spawns.Count);
            foreach (Level100SpawnDefinition spawn in spawns)
            {
                writer.Write(spawn.AuthoredOrder);
                writer.Write(spawn.DefinitionIdentity);
                writer.Write(spawn.OwnerDefinitionIdentity);
                writer.Write(spawn.DefinitionName);
                writer.Write(spawn.SpawnerName);
                writer.Write(spawn.ScriptName);
                WriteNullableString(writer, spawn.MeshBinding);
                writer.Write(spawn.ThingTypeMask);
                writer.Write(spawn.Active);
                writer.Write(spawn.InitialHealth);
                WritePose(writer, spawn.InitialPose);
                WriteVector(writer, spawn.AuthoredEmitterTransform.LocalPositionFloatBits);
                WriteBasis(writer, spawn.AuthoredEmitterTransform.LocalBasisFloatBits);
                writer.Write((int)spawn.TargetGroup);
                writer.Write(spawn.FixedTargetOrdinal);
                writer.Write(spawn.MaximumGroupActors);
                if (hasSpawnerExits || hasWeaponMounts)
                {
                    writer.Write(spawn.SpawnerExitWaypoints is not null);
                    if (spawn.SpawnerExitWaypoints is { } points)
                    {
                        writer.Write(points.Count);
                        foreach (Level100SpawnerExitPoint point in points)
                        {
                            writer.Write(point.Selector);
                            WriteVector(writer, point.ModelTransform.LocalPositionFloatBits);
                            WriteBasis(writer, point.ModelTransform.LocalBasisFloatBits);
                        }
                    }
                }
            }

            writer.Write(waypointPaths.Count);
            foreach (Level100WaypointPathDefinition path in waypointPaths)
            {
                writer.Write(path.Name);
                writer.Write(path.Points.Count);
                foreach (Level100WaypointPointDefinition point in path.Points)
                {
                    writer.Write(point.NodeIndex);
                    writer.Write(point.PositionMillimeters.X);
                    writer.Write(point.PositionMillimeters.Y);
                    writer.Write(point.PositionMillimeters.Z);
                    writer.Write(point.RetailComponentsFloatBits.X);
                    writer.Write(point.RetailComponentsFloatBits.Y);
                    writer.Write(point.RetailComponentsFloatBits.Z);
                    writer.Write(point.RetailComponentsFloatBits.W);
                }

                // Version 6. The traversal chain and the loop flag are hashed
                // because they DECIDE MOTION: two definition sets with the same
                // 30 node positions and different chains produce different
                // routes. Leaving them out would let exactly the class of
                // defect this pair was added to fix - a route silently walked
                // in the wrong order - carry an unchanged definition identity.
                writer.Write(path.TargetChainNodeIndices.Count);
                foreach (int nodeIndex in path.TargetChainNodeIndices)
                {
                    writer.Write(nodeIndex);
                }

                writer.Write(path.IsClosed);
            }

            writer.Write(motionDefinitions.Count);
            foreach (Level100ActorMotionDefinition definition in motionDefinitions)
            {
                writer.Write(definition.AuthoredOrder);
                writer.Write(definition.DefinitionName);
                writer.Write((int)definition.MotionClass);
                writer.Write(definition.BehaviorSerializedType);
                writer.Write(definition.BehaviorInternalId);
                writer.Write(definition.SteamClassVtableAddress);
                writer.Write(definition.ArrivalRadiusMillimeters);
                WriteNullableInt(writer, definition.MaximumSpeedFloatBits);
                WriteNullableInt(
                    writer,
                    definition.MaximumTurnRadiansPerBaseTickFloatBits);
                WriteNullableInt(writer, definition.FullGuideBaseTicks);
                WriteNullableInt(
                    writer,
                    definition.CoreGroundOriginOffsetMillimeters);
                if (hasWeaponMounts)
                {
                    writer.Write(definition.WeaponMounts is not null);
                    if (definition.WeaponMounts is { } mounts)
                    {
                        writer.Write(mounts.Count);
                        foreach (Level100ActorWeaponMountDefinition mount in mounts)
                        {
                            writer.Write(mount.Use.DefinitionName);
                            writer.Write(mount.Use.TagName);
                            writer.Write(mount.Use.RawCreationFlags);
                            writer.Write(mount.Selector);
                            WriteVector(writer, mount.ModelPose.PositionFloatBits);
                            WriteBasis(writer, mount.ModelPose.BasisFloatBits);
                        }
                    }
                }
            }
        }

        return stream.ToArray();
    }

    private static void WritePose(BinaryWriter writer, Level100ActorPoseSnapshot pose)
    {
        WriteVector(writer, pose.PositionMillimeters);
        WriteBasis(writer, pose.BasisFloatBits);
        WriteVector(writer, pose.LinearVelocityMillimetersPerTick);
        WriteVector(writer, pose.AngularVelocityMicroRadiansPerTick);
    }

    private static void WriteVector(BinaryWriter writer, SimVector3 vector)
    {
        writer.Write(vector.X);
        writer.Write(vector.Y);
        writer.Write(vector.Z);
    }

    private static void WriteVector(BinaryWriter writer, Level100FloatVector3Bits vector)
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

    private static void WriteNullableString(BinaryWriter writer, string? value)
    {
        writer.Write(value is not null);
        if (value is not null)
        {
            writer.Write(value);
        }
    }

    private static void WriteNullableInt(BinaryWriter writer, int? value)
    {
        writer.Write(value.HasValue);
        if (value.HasValue)
        {
            writer.Write(value.Value);
        }
    }


}
