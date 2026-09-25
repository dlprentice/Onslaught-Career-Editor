// SPDX-License-Identifier: GPL-3.0-or-later
using System.Collections;
using System.Reflection;
using System.Runtime.ExceptionServices;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;
using M = System.Collections.Generic.Dictionary<string, object?>;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary differential oracle for the unchanged Thing/Actor state owner.
/// Fixtures are synthetic or taken from ThingActorBaseStateTests and
/// RetailPlaneMotionTests. Reflection reaches the existing internal seam;
/// no actor registry, Plane stepping or retail inputs are constructed here.
/// </summary>
public sealed partial class ThingActorStateReferenceChecks : Node
{
    private static readonly Type s_actor = typeof(ThingActorBaseState);
    private static readonly Type s_thing = s_actor.Assembly.GetType("OnslaughtRebuild.Core.ThingBaseState", true)!;
    private const BindingFlags Instance = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
    private const BindingFlags Static = BindingFlags.Static | BindingFlags.NonPublic;
    private readonly List<M> _cases = [];
    private readonly List<M> _laws = [];
    private readonly List<M> _properties = [];
    private int _operations;

    public override void _Ready()
    {
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            if (args.Length != 2 || Engine.IsEditorHint() || DisplayServer.GetName() != "headless")
                throw new InvalidOperationException("Two fresh owned outputs and headless runtime are required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            if (fixturePath == reportPath) throw new ArgumentException("Fixture and report paths must differ.");
            Godot.Input.MouseModeEnum pointer = Godot.Input.MouseMode;
            ConstructionCases();
            MillimeterCases();
            ThingCases();
            RetailCases();
            PlaneCases();
            RestoreCases();
            ProjectionCases();
            var fixture = new M
            {
                ["schema"] = 1, ["constants"] = new M
                {
                    ["actor_lineage"] = ThingActorTypeMasks.ActorLineage, ["thing"] = ThingActorTypeMasks.Thing,
                    ["actor"] = ThingActorTypeMasks.Actor, ["complex_thing"] = ThingActorTypeMasks.ComplexThing,
                    ["initial_contact_time_float_bits"] = ThingActorBaseState.InitialContactTimeFloatBits,
                    ["flags"] = Enum.GetValues<ThingActorFlags>().ToDictionary(v => Snake(v.ToString()), v => (object?)(int)v),
                },
                ["cases"] = _cases, ["laws"] = _laws, ["properties"] = _properties,
                ["source_sha256"] = SourceHashes(),
            };
            using (Variant packed = Pack(fixture))
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create Thing state fixtures."))
                file.StoreVar(packed, false);
            if (Godot.Input.MouseMode != pointer) throw new InvalidOperationException("Pointer ownership changed.");
            var report = new M
            {
                ["schema"] = 1, ["failure_count"] = 0, ["completed"] = new[] { "thing_actor_state_reference" },
                ["counts"] = new M { ["cases"] = _cases.Count, ["operations"] = _operations, ["laws"] = _laws.Count, ["properties"] = _properties.Count },
                ["runtime"] = RuntimeInformation.FrameworkDescription,
                ["fixture_sha256"] = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(fixturePath))).ToLowerInvariant(),
            };
            File.WriteAllText(reportPath, JsonSerializer.Serialize(report));
            GD.Print($"THING_ACTOR_STATE_REFERENCE_CHECKS: {_cases.Count} cases, {_operations} operations, {_laws.Count} laws, {_properties.Count} properties; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private static int Word(float value) => BitConverter.SingleToInt32Bits(value);
    private static Level100FloatBasis3Bits Identity() => new(0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000);
    private static ThingActorPoseSnapshot Pose(int x = 10, int y = 20, int z = 30) => new(new(x, y, z), Identity());
    private static RetailActorPoseSnapshot RawPose() => new(new(Word(288.6875f), Word(243.25f), Word(-10f)), Identity());
    private static RetailPlaneMotionSnapshot Plane() => new(default, default, default, default,
        new(0x3d32b8c2, 0x3d32b8c2, 0x3d32b8c2), 0);
    private static int[] Words() => [0, int.MinValue, 1, unchecked((int)0x80000001), 0x007fffff, 0x00800000,
        0x3f000000, 0x3f800000, unchecked((int)0xbf800000), 0x7f7fffff, unchecked((int)0xff7fffff),
        0x7f800000, unchecked((int)0xff800000), 0x7fc00001, unchecked((int)0xff800001)];

    private sealed class Sequence(ThingActorStateReferenceChecks owner, object state, M row)
    {
        public object State { get; } = state;
        public Sequence Do(string operation, params object?[] args)
        {
            M result = Capture(() => InvokeOperation(State, operation, args));
            ((List<M>)row["steps"]!).Add(new M
            {
                ["op"] = operation, ["args"] = args, ["result"] = result,
                ["snapshot"] = Capture(() => Snapshot(State)),
            });
            owner._operations++;
            return this;
        }
    }

    private Sequence? ActorCase(string name, ThingActorPoseSnapshot? pose = null, SimVector3 velocity = default,
        SimVector3 angular = default, uint mask = 0, bool nullPose = false) => Case(name, "create",
            [nullPose ? null : pose ?? Pose(), velocity, angular, mask],
            () => new ThingActorBaseState(nullPose ? null! : pose ?? Pose(), velocity, angular, mask));

    private Sequence? RestoreCase(string name, ThingActorBaseStateSnapshot? snapshot) =>
        Case(name, "restore", [snapshot], () => new ThingActorBaseState(snapshot!));

    private Sequence? Case(string name, string kind, object?[] args, Func<object> construct)
    {
        object? state = null;
        M result = Capture(() => { state = construct(); return Snapshot(state); });
        var row = new M { ["name"] = name, ["kind"] = kind, ["args"] = args, ["result"] = result, ["steps"] = new List<M>() };
        _cases.Add(row);
        return state is null ? null : new Sequence(this, state, row);
    }

    private void ConstructionCases()
    {
        ActorCase("constructor/null", nullPose: true);
        foreach (uint mask in new uint[] { 0, 1, 2, 3, 0x40, 0x40100130, 0x80000000, uint.MaxValue })
            ActorCase("constructor/mask/" + mask, mask: mask)?.Do("snapshot").Do("get_retail_poses")
                .Do("has_retail_construction").Do("has_retail_plane_motion");
        for (int component = 0; component < 9; component++)
            foreach (int word in Words())
                ActorCase($"constructor/basis/{component}/{word}", Pose() with { BasisFloatBits = BasisWord(Identity(), component, word) });
        ActorCase("constructor/signed-extremes", Pose(int.MinValue, int.MaxValue, -1),
            new(int.MinValue, 0, int.MaxValue), new(int.MaxValue, int.MinValue, 0));
    }

    private void MillimeterCases()
    {
        var s = ActorCase("millimeters/full-order", velocity: new(1, 2, 3), angular: new(4, 5, 6), mask: 0x40)!;
        var turn = Pose(15, 18, 41) with { BasisFloatBits = Identity() with { Row0Y = int.MinValue } };
        s.Do("advance_pose", turn).Do("advance_low_fidelity_position", new SimVector3(99, 88, 77))
            .Do("update_current_pose", Pose(-2, -3, -4) with { BasisFloatBits = Identity() with { Row2X = int.MinValue } })
            .Do("advance_low_fidelity_position", new SimVector3(-7, -8, -9))
            .Do("reset_pose", Pose(-1, -2, -3)).Do("set_velocity", new SimVector3(10, 20, 30))
            .Do("add_velocity", new SimVector3(-2, 4, 8)).Do("stop")
            .Do("set_angular_velocity", new SimVector3(int.MinValue, int.MaxValue, 0)).Do("stop");
        foreach (string op in new[] { "advance_pose", "update_current_pose", "reset_pose" })
        {
            s.Do(op, (object?)null);
            foreach (int bad in new[] { 0x7f800000, 0x7fc00001, unchecked((int)0xff800000) })
                s.Do(op, Pose(88, 77, 66) with { BasisFloatBits = Identity() with { Row2Z = bad } });
        }
        for (int axis = 0; axis < 3; axis++)
            foreach (int sign in new[] { -1, 1 })
            {
                SimVector3 v = SimAxis(new(31, 32, 33), axis, sign < 0 ? int.MinValue : int.MaxValue);
                s.Do("set_velocity", v).Do("add_velocity", SimAxis(new(1, 1, 1), axis, sign)).Do("stop");
            }
        foreach (string contact in new[] { "declare_on_ground", "declare_in_water", "declare_on_object" })
            foreach (int word in Words()) s.Do(contact, word);
        s.Do("set_thing_type", 0x80u).Do("add_published_type", uint.MaxValue).Do("set_thing_type", 0u);
        s.Do("make_invisible").Do("make_invisible").Do("make_visible").Do("make_visible")
            .Do("mark_unit_dying").Do("start_die_process").Do("declare_shutdown").Do("start_die_process").Do("declare_shutdown")
            .Do("restore_snapshot");
        var extremes = ActorCase("millimeters/unchecked-last-frame", Pose(int.MinValue, int.MaxValue, int.MinValue))!;
        extremes.Do("advance_pose", Pose(int.MaxValue, int.MinValue, int.MaxValue));
        var snap = ((ThingActorBaseState)extremes.State).Snapshot;
        Properties("wrapped-movement", snap, uint.MaxValue);
        Properties("null-current", snap with { CurrentPose = null! }, 0);
        Properties("null-old", snap with { OldPose = null! }, 0);
        var begin = ActorCase("millimeters/nonstationary-failure-order", velocity: new(1, 0, 0))!;
        begin.Do("begin_retail_initialization", null, null, 0u)
            .Do("begin_retail_plane", null, null, 0x7f800000, 0u)
            .Do("begin_retail_plane", null, Plane(), 0x7f800000, 0u)
            .Do("begin_retail_plane", null, Plane(), 0, 0u)
            .Do("stop").Do("begin_retail_initialization", null, RawPose(), 0u);
        ActorCase("millimeters/nonstationary-angular", angular: new(0, 1, 0))!
            .Do("begin_retail_initialization", RawPose(), RawPose(), 0u).Do("stop")
            .Do("begin_retail_initialization", RawPose(), RawPose(), 0u)
            .Do("set_angular_velocity", SimVector3.Zero).Do("begin_retail_initialization", RawPose(), RawPose(), 0u);
    }

    private void ThingCases()
    {
        foreach (uint lineage in new uint[] { 0, 1, 0x80000003, uint.MaxValue })
            foreach (ushort flags in new ushort[] { 0, 1, 2, 4, 5, 16, 64, 0xffff })
            {
                var s = Case($"thing/{lineage}/{flags}", "create_thing", [lineage, 0x40u, (int)flags],
                    () => Activator.CreateInstance(s_thing, Instance, null, [lineage, 0x40u, (ThingActorFlags)flags], null)!)!;
                s.Do("get_flags").Do("get_type_mask").Do("make_visible").Do("make_invisible").Do("make_visible")
                    .Do("mark_dying").Do("start_die_process").Do("declare_shutdown").Do("declare_shutdown")
                    .Do("set_thing_type", 0x80u).Do("add_type", 0x10u).Do("set_thing_type", 0u)
                    .Do("add_flags", (ThingActorFlags)0x8080).Do("get_flags").Do("snapshot");
            }
        Case("thing/die-first", "create_thing", [0u, 0u, 0],
            () => Activator.CreateInstance(s_thing, Instance, null, [0u, 0u, ThingActorFlags.None], null)!)!
            .Do("start_die_process").Do("mark_dying").Do("start_die_process");
        foreach (ThingActorFlags flags in Enum.GetValues<ThingActorFlags>())
            ActorCase("actor/publication/" + flags)!.Do("add_publication_flags", flags).Do("restore_snapshot");
    }

    private void RetailCases()
    {
        RetailActorPoseSnapshot current = RawPose() with
        {
            PositionFloatBits = new(0x43880001, 0x43700001, unchecked((int)0xc1200001)),
            BasisFloatBits = Identity() with { Row0Y = int.MinValue },
        };
        RetailActorPoseSnapshot old = RawPose() with { BasisFloatBits = Identity() with { Row2X = int.MinValue } };
        var s = ActorCase("retail/retained-words-and-world110-refusal")!;
        s.Do("get_retail_poses").Do("copy_retail_position_to_old").Do("set_retail_motion", 0x7f800000, 1)
            .Do("set_retail_position", new Level100FloatVector3Bits(0x7f800000, 0, 0))
            .Do("set_retail_position", current.PositionFloatBits)
            .Do("teleport_retail_position", current.PositionFloatBits)
            .Do("begin_retail_initialization", current, old, 0x40100130u)
            .Do("get_retail_poses").Do("set_retail_motion", 0, 1).Do("restore_snapshot")
            .Do("set_retail_position", current.PositionFloatBits with { Z = unchecked((int)0xc1300001) })
            .Do("copy_retail_position_to_old").Do("teleport_retail_position", current.PositionFloatBits)
            .Do("set_retail_motion", int.MinValue, int.MinValue).Do("set_retail_motion", 0x7fc00001, 10)
            .Do("has_retail_construction").Do("has_retail_plane_motion");
        foreach (string op in new[] { "advance_pose", "update_current_pose", "reset_pose" }) s.Do(op, (object?)null);
        foreach (string op in new[] { "advance_low_fidelity_position", "set_velocity", "add_velocity", "set_angular_velocity" })
            s.Do(op, SimVector3.Zero);
        s.Do("stop").Do("clear_retail_plane_drive")
            .Do("commit_retail_plane_move", null, null, 0x7f800000)
            .Do("begin_retail_initialization", null, null, 0u)
            .Do("begin_retail_plane", null, null, 0x7f800000, 0u)
            .Do("begin_retail_plane", null, Plane(), 0, 0u);
        foreach (string op in new[] { "set_retail_position", "teleport_retail_position" })
            foreach (int word in Words().Concat(new[] { Word(3_000_000), Word(-3_000_000) }))
                for (int axis = 0; axis < 3; axis++) s.Do(op, RawAxis(current.PositionFloatBits, axis, word));
        s.Do("make_invisible").Do("declare_on_ground", Word(1.25f)).Do("declare_in_water", Word(2.5f))
            .Do("declare_on_object", Word(3.75f)).Do("mark_unit_dying").Do("start_die_process")
            .Do("add_published_type", uint.MaxValue).Do("add_publication_flags", ThingActorFlags.IsBigThing).Do("restore_snapshot");
        foreach (RetailActorPoseSnapshot? pose in new RetailActorPoseSnapshot?[] { null,
            RawPose() with { PositionFloatBits = new(Word(3_000_000), 0x7fc00001, 0) },
            RawPose() with { PositionFloatBits = new(Word(3_000_000), 0, 0), BasisFloatBits = Identity() with { Row0X = 0x7fc00001 } },
            RawPose() with { BasisFloatBits = Identity() with { Row2Y = 0x7fc00001 } } })
        {
            ActorCase("retail/invalid-current/" + _cases.Count)!.Do("begin_retail_initialization", pose, RawPose(), 0u);
            ActorCase("retail/invalid-old/" + _cases.Count)!.Do("begin_retail_initialization", RawPose(), pose, 0u);
        }
    }

    private void PlaneCases()
    {
        RetailPlaneMotionSnapshot motion = Plane() with
        { Velocity = new(Word(1), Word(2), Word(3)), Drive = new(Word(4), Word(5), Word(6)) };
        var s = ActorCase("plane/complete-state-and-current-old-order")!;
        s.Do("clear_retail_plane_drive").Do("commit_retail_plane_move", null, null, 0x7f800000)
            .Do("begin_retail_plane", RawPose(), motion, 0, 0x40u)
            .Do("has_retail_plane_motion").Do("has_retail_construction").Do("restore_snapshot")
            .Do("clear_retail_plane_drive").Do("clear_retail_plane_drive");
        foreach (float angle in new[] { MathF.PI, -MathF.PI, 0f, 2 * MathF.PI, -2 * MathF.PI, 0.0000005f, -0.0000005f, 0.5f, -0.5f })
        {
            motion = motion with { CurrentEuler = new(Word(angle), Word(angle * 0.1f), Word(-angle)) };
            var pose = RawPose() with { BasisFloatBits = Identity() with { Row1X = Word(angle) } };
            s.Do("commit_retail_plane_move", pose, motion, Word(angle)).Do("restore_snapshot");
        }
        foreach (int time in Words()) s.Do("commit_retail_plane_move", RawPose(), motion, time);
        foreach (RetailPlaneMotionSnapshot? bad in InvalidMotions())
        {
            s.Do("commit_retail_plane_move", RawPose(), bad, 0);
            ActorCase("plane/initial-admission/" + _cases.Count)!.Do("begin_retail_plane", RawPose(), bad, 0, 0u);
        }
        foreach (int axis in new[] { 0, 1, 2 })
        {
            var overflow = motion with { CurrentEuler = RawAxis(motion.CurrentEuler, axis, 0x7f7fffff) };
            s.Do("commit_retail_plane_move", RawPose(), overflow, 0);
        }
        s.Do("commit_retail_plane_move", null, null, 0x7fc00001)
            .Do("commit_retail_plane_move", RawPose() with { PositionFloatBits = new(Word(3_000_000), 0, 0) }, null, 0x7fc00001)
            .Do("begin_retail_plane", null, motion with { Velocity = new(0x7f7fffff, 0, 0) }, 0, 0u)
            .Do("begin_retail_plane", null, Plane(), 0x7fc00001, 0u)
            .Do("set_retail_motion", 0, -1).Do("restore_snapshot")
            .Do("commit_retail_plane_move", RawPose(), motion, 0).Do("restore_snapshot")
            .Do("set_retail_motion", int.MinValue, int.MaxValue).Do("restore_snapshot")
            .Do("set_retail_position", RawPose().PositionFloatBits with { X = 0x43880001 }).Do("copy_retail_position_to_old")
            .Do("teleport_retail_position", RawPose().PositionFloatBits).Do("restore_snapshot");
        foreach (string op in new[] { "advance_pose", "reset_pose", "update_current_pose" }) s.Do(op, Pose());
        s.Do("stop").Do("declare_on_ground", int.MinValue).Do("make_invisible").Do("mark_unit_dying")
            .Do("start_die_process").Do("restore_snapshot");
    }

    private static IEnumerable<RetailPlaneMotionSnapshot?> InvalidMotions()
    {
        yield return null;
        foreach (string field in new[] { "velocity", "drive", "current_euler", "desired_euler", "euler_rates" })
            for (int axis = 0; axis < 3; axis++)
                foreach (int word in new[] { 0x7f800000, unchecked((int)0xff800000), 0x7fc00001 })
                    yield return MotionField(Plane(), field, RawAxis(default, axis, word));
        for (int axis = 0; axis < 3; axis++)
            foreach (int word in new[] { Word(-1), unchecked((int)0x80000001), int.MinValue, 0x7f7fffff })
                yield return Plane() with { EulerRates = RawAxis(default, axis, word) };
        foreach (int word in new[] { 0, int.MinValue, 0x3f800000, 0x3f000000, 1, -1, 0x7fc00001 })
            yield return Plane() with { BankFlagFloatBits = word };
        for (int axis = 0; axis < 3; axis++) yield return Plane() with { Velocity = RawAxis(default, axis, 0x7f7fffff) };
    }

    private void RestoreCases()
    {
        ThingActorBaseStateSnapshot normal = new ThingActorBaseState(Pose(), new(7, 8, 9), new(4, 5, 6), 0).Snapshot;
        RestoreCase("restore/null", null);
        RestoreCase("restore/mm", normal)?.Do("advance_low_fidelity_position", new SimVector3(41, 42, 43)).Do("restore_snapshot");
        var owner = new ThingActorBaseState(Pose(), default, default, 0);
        Call(owner, "BeginRetailPlane", [RawPose(), Plane(), 0, 0u]);
        ThingActorBaseStateSnapshot complete = owner.Snapshot;
        RestoreCase("restore/plane", complete)?.Do("clear_retail_plane_drive").Do("restore_snapshot");
        foreach (ThingActorBaseStateSnapshot b in new[] { normal, complete })
        {
            string mode = b.RetailPlane is null ? "mm" : "plane";
            for (int flags = 0; flags < 128; flags++)
            {
                var row = b with { Flags = (ThingActorFlags)flags };
                RestoreCase($"restore/{mode}/flags/{flags}", row);
                Properties($"flags/{mode}/{flags}", row, (uint)(1 << (flags % 32)));
            }
            RestoreCase($"restore/{mode}/flags-max", b with { Flags = (ThingActorFlags)ushort.MaxValue });
            foreach (uint mask in new uint[] { 0, 1, 2, 3, 0x80000000, 0x80000001, 0x80000002, 0x80000003, uint.MaxValue })
            {
                RestoreCase($"restore/{mode}/type/{mask}", b with { ThingTypeMask = mask });
                foreach (uint test in new uint[] { 0, 1, 2, 0x80000000, uint.MaxValue })
                    Properties($"type/{mode}/{mask}/{test}", b with { ThingTypeMask = mask }, test);
            }
            RestoreCase($"restore/{mode}/current-null", b with { CurrentPose = null! });
            RestoreCase($"restore/{mode}/old-null", b with { OldPose = null! });
            foreach (int word in Words())
            {
                RestoreCase($"restore/{mode}/ground/{word}", b with { LastTimeOnGroundFloatBits = word });
                RestoreCase($"restore/{mode}/water/{word}", b with { LastTimeInWaterFloatBits = word });
                RestoreCase($"restore/{mode}/object/{word}", b with { LastTimeOnObjectFloatBits = word });
                RestoreCase($"restore/{mode}/current-basis/{word}", b with { CurrentPose = b.CurrentPose with { BasisFloatBits = Identity() with { Row1X = word } } });
                RestoreCase($"restore/{mode}/old-basis/{word}", b with { OldPose = b.OldPose with { BasisFloatBits = Identity() with { Row2Y = word } } });
            }
        }
        RestoreCase("restore/incomplete-poses", normal with { RetailPoses = complete.RetailPoses });
        RestoreCase("restore/incomplete-motion", normal with { RetailMotion = complete.RetailMotion });
        RestoreCase("restore/incomplete-before-invalid-mm", normal with { RetailPoses = new(null!, null!), CurrentPose = null!, Flags = (ThingActorFlags)65535 });
        RestoreCase("restore/plane-missing-both", normal with { RetailPlane = Plane() });
        RestoreCase("restore/plane-missing-poses", complete with { RetailPoses = null });
        RestoreCase("restore/plane-missing-motion", complete with { RetailMotion = null });
        RestoreCase("restore/plane-null-current", complete with { RetailPoses = complete.RetailPoses! with { Current = null! } });
        RestoreCase("restore/plane-null-old", complete with { RetailPoses = complete.RetailPoses! with { Old = null! } });
        RestoreCase("restore/plane-current-mismatch", complete with { CurrentPose = Pose() });
        RestoreCase("restore/plane-old-mismatch", complete with { OldPose = Pose() });
        RestoreCase("restore/plane-velocity-mismatch", complete with { Velocity = new(1, 0, 0) });
        foreach (int count in new[] { int.MinValue, -1, 0, 1, int.MaxValue })
            RestoreCase("restore/countdown/" + count, complete with { RetailMotion = new(0, count) });
        foreach (int word in Words())
        {
            RestoreCase("restore/last-move/" + word, complete with { RetailMotion = new(word, 1) });
            RestoreCase("restore/raw-position/" + word, complete with { RetailPoses = complete.RetailPoses! with { Current = RawPose() with { PositionFloatBits = new(word, 0, 0) } } });
        }
        foreach (var motion in InvalidMotions()) if (motion is not null)
            RestoreCase("restore/plane-field/" + _cases.Count, complete with { RetailPlane = motion });
        var overflowPlane = Plane() with { Velocity = new(0x7f7fffff, 0, 0) };
        RestoreCase("restore/negative-count-before-velocity-overflow", complete with { RetailPlane = overflowPlane, RetailMotion = new(0, -1) });
        RestoreCase("restore/current-mismatch-before-velocity-overflow", complete with { RetailPlane = overflowPlane, CurrentPose = Pose() });
        RestoreCase("restore/old-mismatch-before-velocity-overflow", complete with { RetailPlane = overflowPlane, OldPose = Pose() });
        RestoreCase("restore/velocity-overflow-before-flags", complete with { RetailPlane = overflowPlane, Flags = (ThingActorFlags)65535 });
        RestoreCase("restore/event-before-count", complete with { RetailMotion = new(0x7fc00001, -1) });
        RestoreCase("restore/raw-before-motion", complete with { RetailPoses = complete.RetailPoses! with { Current = null! }, RetailPlane = Plane() with { BankFlagFloatBits = 1 } });
    }

    private void ProjectionCases()
    {
        for (int component = 0; component < 9; component++)
            foreach (int word in Words())
                Law($"basis/raw/{component}/{word}", "project_pose", "ProjectRetailPose",
                    RawPose() with { BasisFloatBits = BasisWord(Identity(), component, word) });
        // Existing pitch/roll and signed-zero Core fixtures. This compares
        // every raw matrix word, not only an approximate transformed vector.
        Law("basis/quarter-pitch", "project_pose", "ProjectRetailPose", RawPose() with { BasisFloatBits = new(0x3f800000, 0, 0, 0, 0, Word(-1), 0, 0x3f800000, 0) });
        Law("basis/quarter-roll", "project_pose", "ProjectRetailPose", RawPose() with { BasisFloatBits = new(0, 0, 0x3f800000, 0, 0x3f800000, 0, Word(-1), 0, 0) });
        Law("basis/signed-zero", "project_pose", "ProjectRetailPose", RawPose() with
        { BasisFloatBits = Identity() with { Row0Y = int.MinValue, Row1X = int.MinValue, Row1Z = int.MinValue, Row2Y = int.MinValue } });
        var boundary = new List<int>(Words());
        foreach (float value in new[] { 0.0005f, -0.0005f, 0.0015f, -0.0015f, 2147483.5f, -2147483.5f,
            2147483.75f, -2147483.75f, 2147484f, -2147484f, 288.6875f, 243.25f, -10f, 3_000_000f })
        {
            int word = Word(value);
            boundary.Add(unchecked(word - 1)); boundary.Add(word); boundary.Add(unchecked(word + 1));
        }
        uint random = 0x5131729a;
        for (int i = 0; i < 256; i++) { random = unchecked(random * 1664525 + 1013904223); boundary.Add(unchecked((int)random)); }
        foreach (int word in boundary)
            for (int axis = 0; axis < 3; axis++)
            {
                Law($"position/{axis}/{word}", "project_position", "ProjectRetailPosition", RawAxis(RawPose().PositionFloatBits, axis, word));
                Law($"velocity/{axis}/{word}", "project_vector", "ProjectRetailVector", RawAxis(default, axis, word));
            }
        var angles = new List<int> { 0, int.MinValue, 1, unchecked((int)0x80000001), 0x40490fda, 0x40490fdb, 0x40490fdc,
            unchecked((int)0xc0490fda), unchecked((int)0xc0490fdb), unchecked((int)0xc0490fdc), Word(2 * MathF.PI), Word(-2 * MathF.PI),
            Word(0.0000005f), Word(-0.0000005f), Word(2147.483648f), Word(-2147.483648f), 0x7f7fffff };
        foreach (int before in angles)
            foreach (int after in angles)
                for (int axis = 0; axis < 3; axis++)
                    Law($"angular/{axis}/{before}/{after}", "angular_delta", "ProjectPlaneAngularDelta",
                        RawAxis(default, axis, before), RawAxis(default, axis, after));
        // Exact checked unary-negation boundary: -2147483648 must overflow
        // even when the preceding rounded signed delta was representable.
        if (checked((int)Math.Round(((double)-0.483648f - 2147f) * 1_000_000, MidpointRounding.AwayFromZero)) != int.MinValue)
            throw new InvalidOperationException("Checked-negation fixture no longer reaches exactly Int32.MinValue.");
        Law("angular/checked-intmin-negation", "angular_delta", "ProjectPlaneAngularDelta",
            new Level100FloatVector3Bits(0, Word(2147f), 0), new Level100FloatVector3Bits(0, Word(-0.483648f), 0));
    }

    private void Law(string name, string native, string source, params object?[] args) => _laws.Add(new M
    { ["name"] = name, ["op"] = native, ["args"] = args, ["result"] = Capture(() => CallStatic(source, args)) });

    private void Properties(string name, ThingActorBaseStateSnapshot snapshot, uint typeMask) => _properties.Add(new M
    {
        ["name"] = name, ["snapshot"] = snapshot, ["type_mask"] = typeMask,
        ["result"] = Capture(() => new M
        {
            ["is_invisible"] = snapshot.IsInvisible, ["is_dying"] = snapshot.IsDying,
            ["is_shutting_down"] = snapshot.IsShuttingDown, ["local_last_frame_movement"] = snapshot.LocalLastFrameMovement,
            ["is_a"] = snapshot.IsA(typeMask),
        }, allowNullReference: true),
    });

    private static object? InvokeOperation(object state, string operation, object?[] args)
    {
        if (operation == "snapshot") return Snapshot(state);
        if (operation == "restore_snapshot") return new ThingActorBaseState(((ThingActorBaseState)state).Snapshot).Snapshot;
        string? property = operation switch
        {
            "get_retail_poses" => "RetailPoses", "has_retail_construction" => "HasRetailConstruction",
            "has_retail_plane_motion" => "HasRetailPlaneMotion", "get_flags" => "Flags", "get_type_mask" => "TypeMask", _ => null,
        };
        if (property is not null) return Unwrap(() => state.GetType().GetProperty(property, Instance)!.GetValue(state));
        return Call(state, string.Concat(operation.Split('_').Select(s => char.ToUpperInvariant(s[0]) + s[1..])), args);
    }

    private static object Snapshot(object state) => state is ThingActorBaseState actor ? actor.Snapshot : new M
    {
        ["flags"] = s_thing.GetProperty("Flags", Instance)!.GetValue(state),
        ["type_mask"] = s_thing.GetProperty("TypeMask", Instance)!.GetValue(state),
    };

    private static object? Call(object state, string method, object?[] args) =>
        Unwrap(() => state.GetType().GetMethod(method, Instance)!.Invoke(state, args));
    private static object? CallStatic(string method, object?[] args) =>
        Unwrap(() => s_actor.GetMethod(method, Static)!.Invoke(null, args));
    private static object? Unwrap(Func<object?> call)
    {
        try { return call(); }
        catch (TargetInvocationException wrapped) when (wrapped.InnerException is not null)
        { ExceptionDispatchInfo.Capture(wrapped.InnerException).Throw(); throw; }
    }
    private static M Capture(Func<object?> call, bool allowNullReference = false)
    {
        try { return new M { ["ok"] = true, ["value"] = call() }; }
        catch (Exception error)
        {
            // An absent reflection member or transport failure is an oracle
            // defect, never an expected refusal attributed to Core.
            if (error is NullReferenceException && !allowNullReference)
                throw;
            if (error is not (ArgumentException or InvalidOperationException or NotSupportedException or OverflowException or NullReferenceException)) throw;
            return new M { ["ok"] = false, ["error_type"] = error.GetType().Name,
                ["parameter"] = error is ArgumentException argument ? argument.ParamName ?? "" : "" };
        }
    }

    private static SimVector3 SimAxis(SimVector3 v, int axis, int word) => axis switch
    { 0 => v with { X = word }, 1 => v with { Y = word }, _ => v with { Z = word } };
    private static Level100FloatVector3Bits RawAxis(Level100FloatVector3Bits v, int axis, int word) => axis switch
    { 0 => v with { X = word }, 1 => v with { Y = word }, _ => v with { Z = word } };
    private static RetailPlaneMotionSnapshot MotionField(RetailPlaneMotionSnapshot m, string field, Level100FloatVector3Bits v) => field switch
    { "velocity" => m with { Velocity = v }, "drive" => m with { Drive = v }, "current_euler" => m with { CurrentEuler = v },
        "desired_euler" => m with { DesiredEuler = v }, _ => m with { EulerRates = v } };
    private static Level100FloatBasis3Bits BasisWord(Level100FloatBasis3Bits b, int index, int word) => index switch
    { 0 => b with { Row0X = word }, 1 => b with { Row0Y = word }, 2 => b with { Row0Z = word },
        3 => b with { Row1X = word }, 4 => b with { Row1Y = word }, 5 => b with { Row1Z = word },
        6 => b with { Row2X = word }, 7 => b with { Row2Y = word }, _ => b with { Row2Z = word } };

    private static Variant Pack(object? value)
    {
        if (value is null) return default;
        if (value is bool boolean) return boolean;
        if (value is string text) return text;
        if (value is int integer) return integer;
        if (value is uint unsigned) return (long)unsigned;
        if (value is ThingActorFlags flags) return (int)flags;
        if (value is ThingActorBaseStateSnapshot s) return Pack(new M
        {
            ["flags"] = s.Flags, ["current_pose"] = s.CurrentPose, ["old_pose"] = s.OldPose,
            ["velocity"] = s.Velocity, ["angular_velocity"] = s.AngularVelocity, ["thing_type_mask"] = s.ThingTypeMask,
            ["last_time_on_ground_float_bits"] = s.LastTimeOnGroundFloatBits, ["last_time_in_water_float_bits"] = s.LastTimeInWaterFloatBits,
            ["last_time_on_object_float_bits"] = s.LastTimeOnObjectFloatBits,
            ["retail_poses"] = s.RetailPoses, ["retail_motion"] = s.RetailMotion, ["retail_plane"] = s.RetailPlane,
        });
        if (value is ThingActorPoseSnapshot p) return Pack(new M { ["position_millimeters"] = p.PositionMillimeters, ["basis_float_bits"] = p.BasisFloatBits });
        if (value is RetailActorPoseSnapshot r) return Pack(new M { ["position_float_bits"] = r.PositionFloatBits, ["basis_float_bits"] = r.BasisFloatBits });
        if (value is RetailActorPosePair pair) return Pack(new M { ["current"] = pair.Current, ["old"] = pair.Old });
        if (value is RetailActorMotionSnapshot motion) return Pack(new M { ["last_move_time_float_bits"] = motion.LastMoveTimeFloatBits, ["move_countdown"] = motion.MoveCountdown });
        if (value is RetailPlaneMotionSnapshot plane) return Pack(new M { ["velocity"] = plane.Velocity, ["drive"] = plane.Drive,
            ["current_euler"] = plane.CurrentEuler, ["desired_euler"] = plane.DesiredEuler, ["euler_rates"] = plane.EulerRates,
            ["bank_flag_float_bits"] = plane.BankFlagFloatBits });
        if (value is SimVector3 v) return Pack(new M { ["x"] = v.X, ["y"] = v.Y, ["z"] = v.Z });
        if (value is Level100FloatVector3Bits raw) return Pack(new M { ["x"] = raw.X, ["y"] = raw.Y, ["z"] = raw.Z });
        if (value is Level100FloatBasis3Bits b) return Pack(new M
        {
            ["row0_x"] = b.Row0X, ["row0_y"] = b.Row0Y, ["row0_z"] = b.Row0Z,
            ["row1_x"] = b.Row1X, ["row1_y"] = b.Row1Y, ["row1_z"] = b.Row1Z,
            ["row2_x"] = b.Row2X, ["row2_y"] = b.Row2Y, ["row2_z"] = b.Row2Z,
        });
        if (value is IDictionary dictionary)
        {
            using D result = new();
            foreach (DictionaryEntry entry in dictionary)
            {
                using Variant item = Pack(entry.Value);
                result.Add((string)entry.Key, item);
            }
            return result;
        }
        if (value is IEnumerable enumerable)
        {
            using A result = new();
            foreach (object? entry in enumerable) { using Variant item = Pack(entry); result.Add(item); }
            return result;
        }
        throw new NotSupportedException("Unadmitted fixture transport: " + value.GetType().FullName);
    }

    private static string Snake(string name)
    {
        var text = new System.Text.StringBuilder();
        foreach (char c in name) { if (char.IsUpper(c) && text.Length > 0) text.Append('_'); text.Append(char.ToLowerInvariant(c)); }
        return text.ToString();
    }
    private static M SourceHashes()
    {
        var result = new M();
        string root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "OnslaughtRebuild.Core"));
        foreach (string file in new[] { "ThingBaseState.cs", "ThingActorBaseState.cs" })
            result[file] = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(root, file)))).ToLowerInvariant();
        return result;
    }
    private static string Owned(string value)
    {
        string path = Path.GetFullPath(value);
        string root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data"));
        if (!Path.IsPathFullyQualified(value) || path != value || !path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.Ordinal)
            || File.Exists(path) || Directory.Exists(path) || new FileInfo(path).LinkTarget is not null)
            throw new ArgumentException("Output must be fresh and below this checkout's local-data, without a final symlink.");
        for (DirectoryInfo? parent = new(Path.GetDirectoryName(path)!); parent is not null; parent = parent.Parent)
        {
            if (parent.LinkTarget is not null) throw new ArgumentException("Output ancestry must not contain symlinks.");
            if (parent.FullName == root) break;
        }
        if (!Directory.Exists(Path.GetDirectoryName(path))) throw new ArgumentException("Caller must create a fresh owned output directory.");
        return path;
    }
}
