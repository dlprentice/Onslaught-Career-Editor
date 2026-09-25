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
/// Temporary exact oracle for the unchanged RetailPlaneMotion owner. All
/// motion fixtures are synthetic or retained RetailPlaneMotionTests words;
/// clearance uses the already admitted Level 100 terrain, never a copied lab.
/// This does not install a registry, guide scheduler or collision owner.
/// </summary>
public sealed partial class RetailPlaneMotionReferenceChecks : Node
{
    private const BindingFlags InternalStatic = BindingFlags.Static | BindingFlags.NonPublic;
    private const BindingFlags InternalInstance = BindingFlags.Instance | BindingFlags.NonPublic;
    private static readonly MethodInfo s_advance = typeof(RetailPlaneMotion).GetMethod("AdvanceFreeFlight", InternalStatic)
        ?? throw new MissingMethodException("RetailPlaneMotion.AdvanceFreeFlight");
    // Reuse only the existing object-free raw-word fixture transport. Every
    // behavior result below calls the unchanged Core implementation directly.
    private static readonly MethodInfo s_pack = typeof(ThingActorStateReferenceChecks).GetMethod("Pack", InternalStatic)
        ?? throw new MissingMethodException("ThingActorStateReferenceChecks.Pack");
    private readonly List<M> _direct = [];
    private readonly List<M> _sequences = [];
    private int _steps;
    private int _restores;

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
            string terrainPath = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..",
                "OnslaughtRebuild.Core", "Assets", "Level100", "level100-heightfield.hfld.bin"));
            byte[] terrain = File.ReadAllBytes(terrainPath);
            string terrainHash = Hash(terrain);
            using (Stream embedded = typeof(Level100Terrain).Assembly.GetManifestResourceStream(
                "OnslaughtRebuild.Core.Assets.Level100.level100-heightfield.hfld.bin")
                ?? throw new IOException("Missing admitted terrain resource."))
            {
                byte[] bytes = new byte[embedded.Length];
                embedded.ReadExactly(bytes);
                if (!terrain.AsSpan().SequenceEqual(bytes) ||
                    !StringComparer.OrdinalIgnoreCase.Equals(terrainHash, Level100Terrain.Instance.PayloadSha256))
                    throw new InvalidDataException("Prepared terrain differs from the unchanged C# resource.");
            }
            InitialCases();
            AirCases();
            GuideCases();
            TranslateAlignCases();
            ClearanceCases();
            SequenceCases();
            var fixture = new M { ["schema"] = 1, ["direct"] = _direct, ["sequences"] = _sequences,
                ["source_sha256"] = SourceHashes(), ["terrain_sha256"] = terrainHash };
            using (Variant packed = Pack(fixture))
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create Plane motion fixture.")) file.StoreVar(packed, false);
            if (Hash(File.ReadAllBytes(terrainPath)) != terrainHash || Godot.Input.MouseMode != pointer)
                throw new InvalidOperationException("Input bytes or pointer ownership changed.");
            using var version = Engine.GetVersionInfo();
            using Variant engineString = version["string"];
            var report = new M { ["schema"] = 1, ["failure_count"] = 0,
                ["completed"] = new[] { "retail_plane_motion_reference" },
                ["counts"] = new M { ["direct"] = _direct.Count, ["sequences"] = _sequences.Count,
                    ["steps"] = _steps, ["restores"] = _restores },
                ["runtime"] = RuntimeInformation.FrameworkDescription,
                ["engine"] = engineString.AsString(),
                ["terrain_sha256"] = terrainHash, ["fixture_sha256"] = Hash(File.ReadAllBytes(fixturePath)) };
            File.WriteAllText(reportPath, JsonSerializer.Serialize(report));
            GD.Print($"RETAIL_PLANE_MOTION_REFERENCE_CHECKS: {_direct.Count} direct, {_sequences.Count} sequences, {_steps} steps, {_restores} restores; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private void Direct(string name, string op, params object?[] args) => _direct.Add(new M
    { ["name"] = name, ["op"] = op, ["args"] = args, ["result"] = Capture(() => Evaluate(op, args)) });

    private static object? Evaluate(string op, object?[] a) => op switch
    {
        "create_initial" => RetailPlaneMotion.CreateInitial((RetailActorPoseSnapshot)a[0]!, (Level100FloatVector3Bits)a[1]!),
        "euler_from_spawner_basis" => RetailPlaneMotion.EulerFromSpawnerBasis((Level100FloatBasis3Bits)a[0]!),
        "integrate_velocity" => RetailPlaneMotion.IntegrateVelocity((Level100FloatVector3Bits)a[0]!, (Level100FloatVector3Bits)a[1]!, (int)a[2]!, (int)a[3]!),
        "update_guide" => RetailPlaneMotion.UpdateGuide((RetailActorPoseSnapshot)a[0]!, (Level100FloatVector3Bits)a[1]!, (RetailPlaneGuideInput)a[2]!),
        "translate" => RetailPlaneMotion.Translate((Level100FloatVector3Bits)a[0]!, (Level100FloatVector3Bits)a[1]!),
        "align_velocity" => RetailPlaneMotion.AlignVelocity((Level100FloatVector3Bits)a[0]!, (Level100FloatBasis3Bits)a[1]!),
        "compute_clearance" => RetailPlaneMotion.ComputeClearance((bool)a[0]! ? Level100Terrain.Instance : null!, (Level100FloatVector3Bits)a[1]!),
        _ => throw new NotSupportedException("Unknown Plane fixture operation: " + op),
    };

    private void InitialCases()
    {
        Direct("initial/null-before-euler", "create_initial", null, W(0x7fc00001, 0, 0));
        Direct("initial/pose-unused", "create_initial", RawPose() with
        { PositionFloatBits = W(0x7fc00001, 0x7f800000, 0xff800000), BasisFloatBits = BasisWord(Identity(), 4, 0x7fc00001) }, W(0x80000000, 1, 0));
        for (int axis = 0; axis < 3; axis++) foreach (int word in Words())
            Direct($"initial/euler/{axis}/{word}", "create_initial", RawPose(), Axis(default, axis, word));
        for (int component = 0; component < 9; component++) foreach (int word in Words())
            Direct($"spawner/word/{component}/{word}", "euler_from_spawner_basis", BasisWord(Identity(), component, word));
        foreach (int x in new[] { 0, int.MinValue, Word(1), Word(-1) })
            foreach (int y in new[] { 0, int.MinValue, Word(1), Word(-1) })
                foreach (int z in new[] { 0, int.MinValue, Word(1), Word(-1) })
                    Direct($"spawner/signed/{x}/{y}/{z}", "euler_from_spawner_basis", ColumnY(new(x, y, z)));
        var random = new Random(0x504c414e);
        for (int i = 0; i < 160; i++)
            Direct("spawner/bounded/" + i, "euler_from_spawner_basis", ColumnY(RandomVector(random, 2)));
    }

    private void AirCases()
    {
        Direct("air/retained-cap", "integrate_velocity", default(Level100FloatVector3Bits), W(0, 0xc0400000, 0), 0x41133333, 0);
        foreach (int axis in Enumerable.Range(0, 3)) foreach (int word in Words())
        {
            Direct($"air/velocity/{axis}/{word}", "integrate_velocity", Axis(default, axis, word), default(Level100FloatVector3Bits), Word(20), 0);
            Direct($"air/drive/{axis}/{word}", "integrate_velocity", default(Level100FloatVector3Bits), Axis(default, axis, word), Word(20), 0);
            Direct($"air/store-order/{axis}/{word}", "integrate_velocity", Axis(default, axis, word), Axis(default, axis, word), 0x7fc00001, 1);
        }
        foreach (int mode in new[] { int.MinValue, -1, 0, 1, 2, 3, int.MaxValue }) foreach (int speed in Words())
            Direct($"air/speed/{mode}/{speed}", "integrate_velocity", V(.25f, -.5f, .75f), V(.01f, -.1f, -.3f), speed, mode);
        for (int mask = 0; mask < 64; mask++)
        {
            var v = new Level100FloatVector3Bits((mask & 1) == 0 ? 0 : int.MinValue, (mask & 2) == 0 ? 0 : int.MinValue, (mask & 4) == 0 ? 0 : int.MinValue);
            var d = new Level100FloatVector3Bits((mask & 8) == 0 ? 0 : int.MinValue, (mask & 16) == 0 ? 0 : int.MinValue, (mask & 32) == 0 ? 0 : int.MinValue);
            Direct("air/signed-zero/" + mask, "integrate_velocity", v, d, 0, 0);
        }
        foreach (uint word in new uint[] { 0x3ef05506, 0x3ef05507, 0x3ef05508, 0x3f000000, 0x7f7fffff })
            foreach (int mode in new[] { 0, 1, 2 })
                Direct($"air/cap-adjacent/{word}/{mode}", "integrate_velocity", W(0, word, 0), default(Level100FloatVector3Bits), 0x41133333, mode);
        var random = new Random(0x414952);
        for (int i = 0; i < 256; i++)
            Direct("air/bounded/" + i, "integrate_velocity", RandomVector(random, 10), RandomVector(random, 4), Word((float)random.NextDouble() * 40), i % 4);
    }

    private void GuideCases()
    {
        Direct("guide/null-pose-first", "update_guide", null, default(Level100FloatVector3Bits), null);
        Direct("guide/null-guide", "update_guide", RawPose(), W(0x7fc00001, 0, 0), null);
        int[] modes = [int.MinValue, -1, 0, 1, 2, 3, int.MaxValue];
        foreach (int mode in modes) foreach (int controller in new[] { int.MinValue, 0, 1, 2, 3, int.MaxValue })
            foreach (int speed in new[] { -1, 0, 1, 2, 3 })
                Direct($"guide/modes/{mode}/{controller}/{speed}", "update_guide", RawPose(), V(.3f, -.2f, 0),
                    Guide() with { Mode = mode, ControllerState = controller, SpeedMode = speed });
        foreach (int clearance in new[] { 0, int.MinValue, Word(-1), Word(5)-1, Word(5), Word(5)+1,
            Word(15)-1, Word(15), Word(15)+1, Word(50)-1, Word(50), Word(50)+1, 0x7fc00001, 0x7f800000 })
            foreach (int controller in new[] { 1, 2 }) foreach (float dz in new[] { -20f, 20f })
                Direct($"guide/clearance/{clearance}/{controller}/{dz}", "update_guide", RawPose(), V(.2f, .4f, 0),
                    Guide() with { Destination = V(101, 130, dz), ClearanceFloatBits = clearance, ControllerState = controller });
        foreach (int word in new[] { Word(10)-1, Word(10), Word(10)+1, Word(502)-1, Word(502), Word(502)+1 })
            for (int axis = 0; axis < 2; axis++) foreach (int speed in new[] { 0, 1, 2 })
                Direct($"guide/edge/{axis}/{word}/{speed}", "update_guide", RawPose() with
                { PositionFloatBits = Axis(V(10, 502, -10), axis, word) }, V(.3f, -.2f, 0), Guide() with { SpeedMode = speed });
        for (int axis = 0; axis < 3; axis++) foreach (int word in Words())
        {
            Direct($"guide/position/{axis}/{word}", "update_guide", RawPose() with { PositionFloatBits = Axis(RawPose().PositionFloatBits, axis, word) }, V(.1f, .2f, .3f), Guide());
            Direct($"guide/destination/{axis}/{word}", "update_guide", RawPose(), V(.1f, .2f, .3f), Guide() with { Destination = Axis(Guide().Destination, axis, word) });
            Direct($"guide/velocity/{axis}/{word}", "update_guide", RawPose(), Axis(V(.1f, .2f, .3f), axis, word), Guide());
            Direct($"guide/avoidance/{axis}/{word}", "update_guide", RawPose(), V(.1f, .2f, .3f), Guide() with { AvoidancePosition = Axis(V(100, 100, -9), axis, word) });
            Direct($"guide/controller-two-unused/{axis}/{word}", "update_guide", RawPose(), V(.1f, .2f, .3f),
                Guide() with { ControllerState = 2, ClearanceFloatBits = 0x7fc00001, AvoidancePosition = Axis(default, axis, word) });
        }
        for (int component = 0; component < 9; component++) foreach (int word in Words())
            Direct($"guide/basis/{component}/{word}", "update_guide", RawPose() with { BasisFloatBits = BasisWord(Identity(), component, word) }, V(.1f, .2f, 0), Guide());
        foreach (int x in new[] { 0, int.MinValue, Word(1), Word(-1) }) foreach (int y in new[] { 0, int.MinValue, Word(1), Word(-1) })
            foreach (int mode in new[] { 0, 1, 2 })
                Direct($"guide/wrap-zero/{x}/{y}/{mode}", "update_guide", new RetailActorPoseSnapshot(default, Identity()), new Level100FloatVector3Bits(x, y, 0),
                    Guide() with { Destination = new(x, y, int.MinValue), ControllerState = 2, Mode = mode });
        var random = new Random(0x47554944);
        for (int i = 0; i < 256; i++)
            Direct("guide/bounded/" + i, "update_guide", RawPose() with { PositionFloatBits = V(random.Next(513), random.Next(513), -random.Next(100)) },
                RandomVector(random, 2), Guide() with { Destination = V(random.Next(513), random.Next(513), -random.Next(100)), Mode = i % 3,
                    ClearanceFloatBits = Word(random.Next(100)), SpeedMode = i % 4, ControllerState = i % 3 });
    }

    private void TranslateAlignCases()
    {
        for (int axis = 0; axis < 3; axis++) foreach (int word in Words())
        {
            Direct($"translate/position/{axis}/{word}", "translate", Axis(default, axis, word), V(.25f, -.5f, .75f));
            Direct($"translate/velocity/{axis}/{word}", "translate", V(.25f, -.5f, .75f), Axis(default, axis, word));
            Direct($"translate/overflow/{axis}/{word}", "translate", Axis(default, axis, word), Axis(default, axis, word));
            Direct($"align/velocity/{axis}/{word}", "align_velocity", Axis(default, axis, word), Identity());
        }
        for (int component = 0; component < 9; component++) foreach (int word in Words())
            Direct($"align/basis/{component}/{word}", "align_velocity", V(.25f, -.5f, .75f), BasisWord(Identity(), component, word));
        Direct("align/extended-norm-zero-column", "align_velocity", W(0x7f7fffff, 0x7f7fffff, 0x7f7fffff), default(Level100FloatBasis3Bits));
        Direct("align/extended-norm-small-column", "align_velocity", W(0x7f7fffff, 0x7f7fffff, 0x7f7fffff), ColumnY(V(.1f, -.1f, 0)));
        var random = new Random(0x414c4947);
        for (int i = 0; i < 256; i++)
        {
            Direct("translate/bounded/" + i, "translate", RandomVector(random, 1024), RandomVector(random, 4));
            Direct("align/bounded/" + i, "align_velocity", RandomVector(random, 10), ColumnY(RandomVector(random, 1)));
        }
    }

    private void ClearanceCases()
    {
        Direct("clearance/null-first", "compute_clearance", false, W(0x7fc00001, 0, 0));
        Direct("clearance/retained-first", "compute_clearance", true, TrainerPose().PositionFloatBits);
        Direct("clearance/retained-ceiling", "compute_clearance", true, W(0x4384c000, 0x43c44000, 0xca000000));
        foreach (float x in new[] { -1.5f, -.5f, 0f, .5f, 1.5f, 2.5f, 19.5f, 20.5f, 511.5f, 512.5f, 768.5f, 1023.5f, 4194305f })
            foreach (float y in new[] { -.5f, .5f, 1.5f, 20.5f, 512.5f, 4194306f })
                Direct($"clearance/round-mask/{x}/{y}", "compute_clearance", true, V(x, y, -15));
        for (int axis = 0; axis < 3; axis++) foreach (int word in Words().Concat(new[] { 0x4effffff, 0x4f000000, unchecked((int)0xcf000000), unchecked((int)0xceffffff) }))
            Direct($"clearance/word/{axis}/{word}", "compute_clearance", true, Axis(TrainerPose().PositionFloatBits, axis, word));
        Direct("clearance/x-overflow-before-y-read", "compute_clearance", true, W(0x4f000000, 0x7fc00001, 0x7fc00001));
        Direct("clearance/x-offset-overflow-after-z-read", "compute_clearance", true, W(0xcf000000, 0, 0x7fc00001));
        var random = new Random(0x434c4541);
        for (int i = 0; i < 96; i++)
            Direct("clearance/bounded/" + i, "compute_clearance", true, V((float)random.NextDouble()*800-100, (float)random.NextDouble()*800-100, -random.Next(100)));
    }

    private void SequenceCases()
    {
        var trainer = Sequence("retained-trainer", "plane", TrainerPose(), TrainerMotion());
        ThingActorBaseState? restored = null;
        for (int tick = 1; tick <= 32; tick++)
        {
            int clearance = tick == 1 ? 0 : tick < 13 ? 0x40c51eb8 : tick < 29 ? 0x40ccc3a8 : 0x40cadd7c;
            var guide = new RetailPlaneGuideInput(W(0x43843000, 0x43913000, 0xc1ae661a), 1, clearance, 1, 0, null);
            RetailActorPoseSnapshot previous = trainer.Actor!.Snapshot.RetailPoses!.Current;
            Step(trainer, guide, 0x41133333, Word(tick * .05f), tick == 16);
            if (trainer.Actor.Snapshot.RetailPoses!.Old != previous) throw new InvalidOperationException("Retained old/current order changed.");
            if (restored is not null)
            {
                Advance(restored, guide, 0x41133333, Word(tick * .05f));
                if (restored.Snapshot != trainer.Actor.Snapshot) throw new InvalidOperationException("Retained mid-flight restore diverged.");
            }
            if (tick == 16) restored = new(trainer.Actor.Snapshot);
            if (tick == 1 && trainer.Actor.Snapshot.RetailPlane!.Velocity != W(0x80000000, 0x80000000, 0x80000000))
                throw new InvalidOperationException("Retained first signed-zero velocity changed.");
            if (tick == 2 && trainer.Actor.Snapshot.RetailPoses.Current.PositionFloatBits != W(0x4384c000, 0x43c4051f, 0xc1700000))
                throw new InvalidOperationException("Retained second position changed.");
        }
        var final = trainer.Actor!.Snapshot;
        if (final.RetailPoses!.Current.PositionFloatBits != W(0x4384b1b6, 0x43bd21ff, 0xc17d37c4)
            || final.RetailPlane!.Velocity != W(0xbba68f4f, 0xbeeafaf2, 0xbcfb8c91)
            || final.RetailPlane.CurrentEuler != W(0x40485a67, 0xbd88d02d, 0xbb5345e4)
            || final.RetailPlane.Drive != W(0xbd072b70, 0xc03f8fc4, 0xbe4cb5ba))
            throw new InvalidOperationException("Retained 32-step recurrence changed.");
        foreach (string kind in new[] { "null", "actor", "raw" })
        {
            var partial = Sequence("partial/" + kind, kind, RawPose(), null);
            Step(partial, null, 0x7fc00001, 0x7fc00001);
            Step(partial, Guide(), Word(20), 0);
        }
        foreach (string kind in new[] { "null-guide", "bad-speed", "negative-speed", "bad-destination", "bad-event", "drive-overflow", "angular-overflow", "projected-overflow" })
        {
            var motion = TrainerMotion();
            var pose = TrainerPose();
            if (kind == "drive-overflow") motion = motion with { Drive = W(0x7f7fffff, 0x7f7fffff, 0x7f7fffff) };
            if (kind == "angular-overflow") motion = motion with { CurrentEuler = V(0, 40000, 0), EulerRates = V(0, 80000, 0) };
            if (kind == "projected-overflow")
            {
                pose = pose with { PositionFloatBits = V(2_147_772.25f, 100, -10) };
                motion = motion with { Velocity = V(1, 0, 0), Drive = V(1, 0, 0) };
            }
            var seq = Sequence("failure/" + kind, "plane", pose, motion);
            Step(seq, kind == "null-guide" ? null : kind == "bad-destination" ? Guide() with { Destination = W(0x7fc00001, 0, 0) } : Guide(),
                kind == "bad-speed" ? 0x7fc00001 : kind == "negative-speed" ? Word(-1) : Word(20),
                kind is "angular-overflow" or "projected-overflow" ? 0 : 0x7fc00001);
            if (kind is "angular-overflow" or "projected-overflow")
            {
                var failed = (M)((List<M>)seq.Row["steps"]!)[0]["result"]!;
                if ((bool)failed["ok"]! || (string)failed["error_type"]! != "OverflowException")
                    throw new InvalidOperationException("Synthetic overflow did not reach the intended checked projection: " + kind);
            }
            // Recovery on the same owner proves failed calls did not commit.
            Step(seq, Guide(), Word(20), Word(.1f), true);
        }
        // Every current/desired angle compares numerically equal while zero
        // signs differ. Unit must retain the unusual original basis exactly.
        var equalPose = RawPose() with { PositionFloatBits = V(100, 100, -10), BasisFloatBits = Identity() with { Row0X = Word(2), Row1Z = int.MinValue } };
        var equal = Sequence("equal-euler-preserves-basis", "plane", equalPose, TrainerMotion() with
        { CurrentEuler = W(0, 0x80000000, 0), DesiredEuler = default, EulerRates = W(0x7f7fffff, 0x7f7fffff, 0x7f7fffff) });
        Step(equal, Guide() with { Destination = V(100, 110, -10), ControllerState = 2 }, Word(20), 0, true);
        if (equal.Actor!.Snapshot.RetailPoses!.Current.BasisFloatBits != equalPose.BasisFloatBits)
            throw new InvalidOperationException("Equal-angle basis preservation changed.");
        var random = new Random(0x4d4f5645);
        for (int run = 0; run < 8; run++)
        {
            var seq = Sequence("varied/" + run, "plane", RawPose(), TrainerMotion() with { CurrentEuler = default, DesiredEuler = default });
            for (int tick = 1; tick <= 64; tick++)
            {
                var guide = Guide() with { Destination = V(random.Next(600)-50, random.Next(600)-50, -random.Next(80)),
                    Mode = tick % 3, ControllerState = tick % 4, SpeedMode = tick % 5, ClearanceFloatBits = Word(random.Next(80)),
                    AvoidancePosition = tick % 7 == 0 ? V(0, 0, -random.Next(80)) : null };
                Step(seq, guide, Word(2 + run * 5), Word(tick * .05f), tick == 16 || tick == 32);
            }
        }
    }

    private sealed record SequenceState(ThingActorBaseState? Actor, M Row);
    private SequenceState Sequence(string name, string kind, RetailActorPoseSnapshot pose, RetailPlaneMotionSnapshot? motion)
    {
        ThingActorBaseState? actor = kind == "null" ? null : new(new(SimVector3.Zero, Identity()), default, default, 0);
        if (kind == "raw") InvokeActor(actor!, "BeginRetailInitialization", pose, pose, 0u);
        if (kind == "plane") InvokeActor(actor!, "BeginRetailPlane", pose, motion, 0, 0u);
        var row = new M { ["name"] = name, ["kind"] = kind, ["pose"] = pose, ["motion"] = motion,
            ["initial"] = Capture(() => actor?.Snapshot), ["steps"] = new List<M>() };
        _sequences.Add(row);
        return new(actor, row);
    }
    private void Step(SequenceState state, RetailPlaneGuideInput? guide, int speed, int time, bool restore = false)
    {
        ThingActorBaseStateSnapshot? before = state.Actor?.Snapshot;
        var row = new M { ["guide"] = guide, ["speed"] = speed, ["time"] = time,
            ["result"] = Capture(() => { Advance(state.Actor, guide, speed, time); return null; }, guide is null),
            ["snapshot"] = Capture(() => state.Actor?.Snapshot), ["restore"] = null };
        if (!(bool)((M)row["result"]!)["ok"]! && state.Actor?.Snapshot != before)
            throw new InvalidOperationException("Failed free-flight call changed the retained actor.");
        if (restore)
        {
            row["restore"] = Capture(() => new ThingActorBaseState(state.Actor!.Snapshot).Snapshot);
            _restores++;
        }
        ((List<M>)state.Row["steps"]!).Add(row);
        _steps++;
    }
    private static void Advance(ThingActorBaseState? actor, RetailPlaneGuideInput? guide, int speed, int time) =>
        Unwrap(() => s_advance.Invoke(null, [actor, guide, speed, time]));
    private static void InvokeActor(ThingActorBaseState actor, string method, params object?[] args) =>
        Unwrap(() => (typeof(ThingActorBaseState).GetMethod(method, InternalInstance)
            ?? throw new MissingMethodException(method)).Invoke(actor, args));
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
            if (error is NullReferenceException && !allowNullReference) throw;
            if (error is not (ArgumentException or InvalidOperationException or OverflowException or NotSupportedException or NullReferenceException)) throw;
            return new M { ["ok"] = false, ["error_type"] = error.GetType().Name,
                ["parameter"] = error is ArgumentException argument ? argument.ParamName ?? "" : "" };
        }
    }

    private static int Word(float value) => BitConverter.SingleToInt32Bits(value);
    private static int[] Words() => [0, int.MinValue, 1, unchecked((int)0x80000001), 0x007fffff, 0x00800000,
        0x3f000000, 0x3f800000, unchecked((int)0xbf800000), 0x7f7fffff, unchecked((int)0xff7fffff),
        0x7f800000, unchecked((int)0xff800000), 0x7fc00001, unchecked((int)0xff800001)];
    private static Level100FloatVector3Bits W(uint x, uint y, uint z) => new(unchecked((int)x), unchecked((int)y), unchecked((int)z));
    private static Level100FloatVector3Bits V(float x, float y, float z) => new(Word(x), Word(y), Word(z));
    private static Level100FloatVector3Bits Axis(Level100FloatVector3Bits v, int axis, int word) => axis switch
    { 0 => v with { X = word }, 1 => v with { Y = word }, _ => v with { Z = word } };
    private static Level100FloatVector3Bits RandomVector(Random random, float radius) =>
        V(((float)random.NextDouble()*2-1)*radius, ((float)random.NextDouble()*2-1)*radius, ((float)random.NextDouble()*2-1)*radius);
    private static Level100FloatBasis3Bits Identity() => new(0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000);
    private static Level100FloatBasis3Bits ColumnY(Level100FloatVector3Bits v) => Identity() with { Row0Y = v.X, Row1Y = v.Y, Row2Y = v.Z };
    private static Level100FloatBasis3Bits BasisWord(Level100FloatBasis3Bits b, int index, int word) => index switch
    { 0 => b with { Row0X = word }, 1 => b with { Row0Y = word }, 2 => b with { Row0Z = word },
        3 => b with { Row1X = word }, 4 => b with { Row1Y = word }, 5 => b with { Row1Z = word },
        6 => b with { Row2X = word }, 7 => b with { Row2Y = word }, _ => b with { Row2Z = word } };
    private static RetailActorPoseSnapshot RawPose() => new(V(100, 100, -10), Identity());
    private static RetailPlaneGuideInput Guide() => new(V(102, 130, -15), 1, Word(20), 1, 0, null);
    private static RetailActorPoseSnapshot TrainerPose() => new(W(0x4384c000, 0x43c44000, 0xc1700000), new(
        unchecked((int)0xbf800000), 0x33bbbd2e, int.MinValue, unchecked((int)0xb3bbbd2e), unchecked((int)0xbf800000), 0, int.MinValue, 0, 0x3f800000));
    private static RetailPlaneMotionSnapshot TrainerMotion() => new(default, default, W(0x40490fdb, 0, 0), W(0x40490fdb, 0, 0), W(0x3d32b8c2, 0x3d32b8c2, 0x3d32b8c2), 0);

    private static Variant Pack(object? value)
    {
        if (value is RetailPlaneGuideInput guide) return Pack(new M { ["destination"] = guide.Destination, ["mode"] = guide.Mode,
            ["clearance_float_bits"] = guide.ClearanceFloatBits, ["controller_state"] = guide.ControllerState,
            ["speed_mode"] = guide.SpeedMode, ["avoidance_position"] = guide.AvoidancePosition });
        if (value is RetailPlaneGuideOutput output) return Pack(new M { ["desired_euler"] = output.DesiredEuler,
            ["drive"] = output.Drive, ["bank_flag_float_bits"] = output.BankFlagFloatBits });
        if (value is IDictionary dictionary)
        {
            using D result = new();
            foreach (DictionaryEntry entry in dictionary) { using Variant item = Pack(entry.Value); result.Add((string)entry.Key, item); }
            return result;
        }
        if (value is IEnumerable enumerable && value is not string)
        {
            using A result = new();
            foreach (object? entry in enumerable) { using Variant item = Pack(entry); result.Add(item); }
            return result;
        }
        return (Variant)Unwrap(() => s_pack.Invoke(null, [value]))!;
    }
    private static M SourceHashes()
    {
        var result = new M();
        string root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "OnslaughtRebuild.Core"));
        foreach (string file in new[] { "RetailPlaneMotion.cs", "RetailFloat24.cs", "RetailUnitEuler.cs", "ThingActorBaseState.cs" })
            result[file] = Hash(File.ReadAllBytes(Path.Combine(root, file)));
        return result;
    }
    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
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
