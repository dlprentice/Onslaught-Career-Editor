// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;
using Dictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Actual native owner against the unchanged 1bb29345 driver below. Synthetic
/// tracks exercise malformed constructor states; the read-only pinned manifest
/// adds the admitted production frames. No scene import, renderer, or game host.
/// </summary>
public sealed partial class StaticAnimationChecks : Node
{
    private const string ScriptPath = "res://Scenes/World/static_world_animation.gd";
    private int _checks;
    private readonly List<string> _sections = [];
    // --write-golden=PATH records every legacy expectation, with its exact
    // inputs, for the GDScript port (Scenes/World/static_animation_checks.gd).
    private readonly Godot.Collections.Array _golden = [];
    private Godot.Collections.Array? _rigSteps;

    public override async void _Ready()
    {
        try
        {
            Input.MouseModeEnum pointer = Input.MouseMode;
            CheckTransformWords();
            _sections.Add("raw_transform_words_and_refusals");
            CheckSyntheticPlayback();
            _sections.Add("clock_lcm_frames_partial_writes");
            CheckProductionTracks();
            _sections.Add("pinned_production_tracks");
            CheckNativeAdmissionAndCopies();
            _sections.Add("native_admission_detachment_and_lifetime");
            Check(Input.MouseMode == pointer, "Static animation never acquires pointer ownership.");
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            string? golden = OS.GetCmdlineUserArgs().Where(arg => arg.StartsWith("--write-golden=", StringComparison.Ordinal))
                .Select(arg => arg["--write-golden=".Length..]).SingleOrDefault();
            if (golden is not null) System.IO.File.WriteAllBytes(golden, GD.VarToBytes(_golden));
            GD.Print("STATIC_ANIMATION_CHECKS: " + System.Text.Json.JsonSerializer.Serialize(new
            {
                completed = true, checks = _checks, failures = 0, sections = _sections,
                manifest_sha256 = Level100StaticWorldAnimationManifest.ExpectedManifestSha256,
            }));
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            GD.PushError($"STATIC_ANIMATION_CHECKS FAILED after {_checks}: {error}");
            GetTree().Quit(1);
        }
    }

    private void CheckTransformWords()
    {
        uint[] special = [0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x00800000,
            0x3f800000, 0xbf800000, 0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000,
            0x7fc00000, 0xffc00000, 0x7f800001, 0xff800001, 0x7fffffff, 0xffffffff];
        uint state = 0x4f4e534c;
        for (int sample = 0; sample < 384; sample++)
        {
            float[] values = new float[12];
            for (int word = 0; word < values.Length; word++)
            {
                state = unchecked(state * 1664525 + 1013904223);
                uint bits = sample < special.Length ? special[(sample + word) % special.Length] : state;
                values[word] = BitConverter.UInt32BitsToSingle(bits);
            }
            var frame = new Level100RigidFrame(values[..9], values[9..]);
            Transform3D legacy = LegacyDriver.ToObjSpaceTransform(frame);
            Record(new() { ["kind"] = "transform", ["frame"] = RawFrame(frame), ["expected"] = TransformWords(legacy).Select(word => (long)word).ToArray() });
            CompareTransform(legacy,
                Level100StaticWorldAnimationDriver.ToObjSpaceTransform(frame), $"raw transform {sample}");
        }
        foreach (Level100RigidFrame frame in new[]
        {
            new Level100RigidFrame(null!, null!), new Level100RigidFrame([], null!),
            new Level100RigidFrame(new float[8], new float[3]),
            new Level100RigidFrame(new float[9], null!),
            new Level100RigidFrame(new float[9], []),
            new Level100RigidFrame(new float[10], new float[2]),
        })
        {
            Exception? legacy = Catch(() => _ = LegacyDriver.ToObjSpaceTransform(frame));
            Record(new() { ["kind"] = "transform", ["frame"] = RawFrame(frame), ["expected_error"] = Error(legacy) });
            CompareFailure(legacy,
                Catch(() => _ = Level100StaticWorldAnimationDriver.ToObjSpaceTransform(frame)),
                "Static converter null/short arrays retain the original read order.");
        }
        Level100RigidFrame extra = new(Enumerable.Range(0, 11).Select(i => (float)i).ToArray(), [1, 2, 3, 4]);
        Transform3D trailing = LegacyDriver.ToObjSpaceTransform(extra);
        Record(new() { ["kind"] = "transform", ["frame"] = RawFrame(extra), ["expected"] = TransformWords(trailing).Select(word => (long)word).ToArray() });
        CompareTransform(trailing,
            Level100StaticWorldAnimationDriver.ToObjSpaceTransform(extra), "Unused trailing frame words");
    }

    private void CheckSyntheticPlayback()
    {
        float[] deltas = [0f, -0f, -1f, float.NaN, float.PositiveInfinity, float.NegativeInfinity,
            float.Epsilon, MathF.BitDecrement(0.05f), 0.05f, MathF.BitIncrement(0.05f),
            0.001f, 0.125f, 0.9999f, 1.0001f, 6.5f, 123456.75f, float.MaxValue, 0.05f];
        foreach (int fps in new[] { 20, 0, -1, int.MinValue, int.MaxValue })
        {
            using var rig = NewRig(fps, [Spec.Loop(26), Spec.Loop(25), Spec.Loop(10),
                Spec.Loop(0), Spec.Loop(-7), Spec.Loop(31) with { Playback = 1 },
                Spec.Loop(17) with { Playback = int.MinValue }]);
            CompareState(rig, $"fps {fps} initial");
            foreach (float delta in deltas) Step(rig, delta, $"fps {fps}");
        }
        using (var empty = NewRig(20, []))
            foreach (float delta in deltas) Step(empty, delta, "empty binding list");

        // Alias two bindings to one node: authored order, not node identity,
        // decides the final write when both select a new frame.
        using (var aliases = NewRig(20, [Spec.Loop(3) with { NodeGroup = 0 },
            Spec.Loop(5) with { NodeGroup = 0, Frames = Frames(5, 100) }]))
        {
            foreach (float delta in new[] { 0.051f, 0.102f, 0.25f, 0.25f, 1.0f })
                Step(aliases, delta, "aliased nodes keep binding order");
        }

        // Unchecked Int64 overflow is exercised without a large frame table.
        // One-shot meshes still participate in the LCM but never dereference
        // their deliberately null part/node. No million-frame loop is needed.
        int[][] lengths = [[int.MaxValue, 2147483629, 2147483587],
            [46337, 46349, 46351, 46381, 46399], [1073741824, int.MaxValue, 2147483629]];
        foreach (int[] loops in lengths)
            foreach (int fps in new[] { 20, -20, 0, int.MaxValue })
            {
                Spec[] specs = loops.Select(length => Spec.Loop(1) with
                {
                    LoopFrames = length, Playback = 1, NullPart = true, NullNode = true,
                }).ToArray();
                using var rig = NewRig(fps, specs);
                foreach (float delta in deltas) Step(rig, delta, $"wrapped LCM {string.Join(',', loops)} fps {fps}");
            }

        Spec[] broken =
        [
            Spec.Loop(4) with { NullBinding = true },
            Spec.Loop(4) with { NullMesh = true },
            Spec.Loop(4) with { NullPart = true },
            Spec.Loop(4) with { Frames = null },
            Spec.Loop(4) with { Frames = [] },
            Spec.Loop(4) with { Frames = Frames(1) },
            Spec.Loop(4) with { Frames = [Frames(1)[0], new(null!, null!), Frames(1)[0], Frames(1)[0]] },
            Spec.Loop(4) with { Frames = [Frames(1)[0], new(new float[8], null!), Frames(1)[0], Frames(1)[0]] },
            Spec.Loop(4) with { Frames = [Frames(1)[0], new(new float[9], null!), Frames(1)[0], Frames(1)[0]] },
            Spec.Loop(4) with { Frames = [Frames(1)[0], new(new float[9], new float[2]), Frames(1)[0], Frames(1)[0]] },
            Spec.Loop(4) with { NullNode = true },
            Spec.Loop(4) with { NullNode = true, Frames = [Frames(1)[0], new(null!, null!)] },
        ];
        for (int index = 0; index < broken.Length; index++)
        {
            // Broken middle binding tests earlier writes and later omissions.
            // A null mesh instead fails during the full LCM scan before any
            // transform writes, even though the clock has already advanced.
            using var rig = NewRig(20, [Spec.Loop(4), broken[index], Spec.Loop(4)]);
            foreach (float delta in new[] { -1f, float.NaN, 0.001f, 0.05f, 0.001f, 0.05f, 0.15f })
                Step(rig, delta, $"malformed case {index}");
        }
        using (var dormant = NewRig(20, [Spec.Loop(0) with { NullNode = true, NullPart = true },
            Spec.Loop(4) with { Playback = 1, NullNode = true, NullPart = true },
            Spec.Loop(4) with { Playback = 72, NullNode = true, NullPart = true }]))
            foreach (float delta in deltas) Step(dormant, delta, "zero selection bypasses malformed part/node");
        using (var disposed = NewRig(20, [Spec.Loop(4), Spec.Loop(4), Spec.Loop(4)]))
        {
            disposed.Nodes[1].Expected.Free();
            disposed.Nodes[1].Actual.Free();
            _rigSteps!.Add(new Godot.Collections.Dictionary { ["free_node"] = 1 });
            Step(disposed, 0.001f, "freed node skipped at frame zero");
            Step(disposed, 0.05f, "freed node fails after shown-frame write");
            Step(disposed, 0.001f, "same selected frame bypasses previous setter failure");
        }
        Exception? nullList = Catch(() => _ = new LegacyDriver(20, null!));
        Record(new() { ["kind"] = "null_bindings", ["expected_error"] = Error(nullList) });
        CompareFailure(nullList,
            Catch(() => _ = new Level100StaticWorldAnimationDriver(20, null!)), "Null binding list constructor");
    }

    private void CheckProductionTracks()
    {
        const string path = "res://Assets/Level100/StaticWorld/level100-static-world-animation.json";
        byte[] bytes = Godot.FileAccess.GetFileAsBytes(path);
        Level100StaticWorldAnimationSet set = Level100StaticWorldAnimationManifest.Decode(bytes);
        Spec[] specs = set.Meshes.Values.SelectMany(mesh => mesh.Parts.Select(part => new Spec(
            (int)mesh.Playback, mesh.LoopFrameCount, part.Frames.ToArray()))).ToArray();
        Check(specs.Length > 0, "The exact pinned production manifest supplies hierarchy parts.");
        using var rig = NewRig(set.FramesPerSecond, specs);
        CompareState(rig, "production tracks before any update");
        for (int frame = 0; frame < 270; frame++)
            Step(rig, frame % 7 == 0 ? 0.05001f : 0.05f, $"pinned manifest step {frame}");
        Step(rig, 65001.25f, "pinned manifest long-session wrap");
    }

    private void CheckNativeAdmissionAndCopies()
    {
        using GDScript script = GD.Load<GDScript>(ScriptPath);
        using Godot.Collections.Array empty = new();
        NativeFailure(script, "create", [20, default], "NullReferenceException");
        NativeFailure(script, "create", [20, 1], "ArgumentException");
        NativeFailure(script, "create", [20.5, empty], "ArgumentException");
        NativeFailure(script, "create", [2147483648L, empty], "ArgumentException");
        using Dictionary missing = new() { ["basis_bits"] = new long[9] };
        NativeFailure(script, "to_obj_space_transform", [missing], "ArgumentException");
        using Dictionary badWord = new() { ["basis_bits"] = new long[] { -1 }, ["origin_bits"] = new long[3] };
        NativeFailure(script, "to_obj_space_transform", [badWord], "ArgumentException");
        using Dictionary badCarrier = new() { ["basis_bits"] = new int[9], ["origin_bits"] = new long[3] };
        NativeFailure(script, "to_obj_space_transform", [badCarrier], "ArgumentException");
        using Dictionary missingBinding = new();
        using Godot.Collections.Array badBindings = new() { missingBinding };
        NativeFailure(script, "create", [20, badBindings], "ArgumentException");
        using Dictionary badNode = new() { ["mesh"] = default, ["part"] = default, ["node"] = 123 };
        using Godot.Collections.Array badNodeBindings = new() { badNode };
        NativeFailure(script, "create", [20, badNodeBindings], "ArgumentException");

        // This is the deliberate immutable transport boundary, not a claim
        // that the retired driver copied a caller-mutated IReadOnlyList.
        var node = new MeshInstance3D { Transform = Sentinel(0) };
        try
        {
            Level100RigidFrame[] frames = Frames(4);
            using Dictionary mesh = new() { ["playback"] = 0, ["loop_frame_count"] = 4 };
            using Godot.Collections.Array frameRows = new();
            foreach (Level100RigidFrame frame in frames)
            {
                using Dictionary row = FrameFacts(frame);
                frameRows.Add(row);
            }
            using Dictionary part = new() { ["frames"] = frameRows };
            using Dictionary binding = new() { ["mesh"] = mesh, ["part"] = part, ["node"] = node };
            using Godot.Collections.Array bindings = new() { binding };
            using Variant returned = script.Call("create", 20, bindings);
            using Dictionary created = Checked(returned);
            using Variant value = created["value"];
            using RefCounted owner = value.As<RefCounted>();
            CompareTransform(Sentinel(0), node.Transform, "Configuration does not apply frame zero");
            Record(new() { ["kind"] = "detached_copy", ["expected"] = TransformWords(LegacyDriver.ToObjSpaceTransform(frames[1])).Select(word => (long)word).ToArray() });
            mesh["loop_frame_count"] = 1;
            using (Variant first = frameRows[1])
            using (Dictionary row = first.AsGodotDictionary()) row["basis_bits"] = new long[9];
            frameRows.Clear();
            part["frames"] = default;
            bindings.Clear();
            using (Variant updated = owner.Call("update", 0.051f))
            using (Dictionary result = Checked(updated)) { }
            CompareTransform(LegacyDriver.ToObjSpaceTransform(frames[1]), node.Transform,
                "Changing every supplied container cannot mutate the admitted native track");
            using (Variant snapshot = owner.Call("host_snapshot"))
            using (Dictionary facts = snapshot.AsGodotDictionary())
            {
                facts["elapsed_seconds_bits"] = 0;
                facts["shown_frames"] = new int[] { 99 };
            }
            using (Variant snapshot = owner.Call("host_snapshot"))
            using (Dictionary facts = snapshot.AsGodotDictionary())
            using (Variant shown = facts["shown_frames"])
            using (Variant elapsed = facts["elapsed_seconds_bits"])
            {
                Check(shown.AsInt32Array().SequenceEqual(new[] { 1 }), "Host snapshots detach selected frames.");
                Check(elapsed.AsInt64() == BitConverter.DoubleToInt64Bits((double)0.051f), "Host snapshots detach the clock.");
            }
        }
        finally { node.Free(); }
        var borrowed = new MeshInstance3D();
        try
        {
            var mesh = new Level100StaticWorldMeshAnimation("test", 4, Level100StaticWorldPlayback.CyclicLoop, 4, "", []);
            var part = new Level100StaticWorldAnimatedPart(0, "test", 0, 0, Frames(4));
            using var driver = new Level100StaticWorldAnimationDriver(20, [new(mesh, part, borrowed)]);
            driver.Dispose();
            driver.Dispose();
            Check(GodotObject.IsInstanceValid(borrowed), "Disposing the adapter never frees borrowed scenery nodes.");
            Check(Catch(() => driver.Update(0.05f)) is ObjectDisposedException, "Disposed adapter cannot resume updates.");
        }
        finally { borrowed.Free(); }
    }

    private Rig NewRig(int fps, Spec[] specs)
    {
        _rigSteps = new Godot.Collections.Array();
        var rows = new Godot.Collections.Array();
        foreach (Spec spec in specs)
        {
            Variant frames = default;
            if (spec.Frames is not null)
            {
                var values = new Godot.Collections.Array();
                foreach (Level100RigidFrame frame in spec.Frames) values.Add(RawFrame(frame));
                frames = values;
            }
            rows.Add(new Godot.Collections.Dictionary
            {
                ["null_binding"] = spec.NullBinding, ["null_mesh"] = spec.NullMesh, ["null_part"] = spec.NullPart,
                ["null_node"] = spec.NullNode, ["node_group"] = spec.NodeGroup, ["playback"] = spec.Playback,
                ["loop_frames"] = spec.LoopFrames, ["frames"] = frames,
            });
        }
        Record(new() { ["kind"] = "rig", ["fps"] = fps, ["specs"] = rows, ["steps"] = _rigSteps });
        return new Rig(fps, specs);
    }

    private void Record(Godot.Collections.Dictionary entry) => _golden.Add(entry);

    private static Variant Error(Exception? error) => error is null ? default : Variant.From(new Godot.Collections.Dictionary
    {
        ["type"] = error.GetType().Name, ["param"] = (error as ArgumentException)?.ParamName ?? "",
    });

    private static Godot.Collections.Dictionary RawFrame(Level100RigidFrame frame) => new()
    {
        ["basis_bits"] = frame.Basis is null ? default : Variant.From(
            frame.Basis.Select(value => (long)BitConverter.SingleToUInt32Bits(value)).ToArray()),
        ["origin_bits"] = frame.Origin is null ? default : Variant.From(
            frame.Origin.Select(value => (long)BitConverter.SingleToUInt32Bits(value)).ToArray()),
    };

    private void Step(Rig rig, float delta, string label)
    {
        string sample = $"{label}; delta 0x{BitConverter.SingleToUInt32Bits(delta):X8}";
        Exception? legacy = Catch(() => rig.Reference.Update(delta));
        _rigSteps!.Add(new Godot.Collections.Dictionary { ["label"] = sample,
            ["delta_bits"] = (long)BitConverter.SingleToUInt32Bits(delta), ["expected_error"] = Error(legacy) });
        CompareFailure(legacy, Catch(() => rig.Native.Update(delta)), sample);
        CompareState(rig, sample);
    }

    private void CompareState(Rig rig, string label)
    {
        using (var expected = new Godot.Collections.Array())
        {
            foreach ((MeshInstance3D node, MeshInstance3D _) in rig.Nodes)
                expected.Add(GodotObject.IsInstanceValid(node)
                    ? Variant.From(TransformWords(node.Transform).Select(word => (long)word).ToArray()) : default);
            _rigSteps!.Add(new Godot.Collections.Dictionary { ["label"] = label, ["state"] = new Godot.Collections.Dictionary
            {
                ["elapsed_bits"] = BitConverter.DoubleToInt64Bits(rig.Reference.ElapsedSeconds),
                ["shown_frames"] = rig.Reference.ShownFrames, ["transforms"] = expected.Duplicate(),
            } });
        }
        using Variant returned = rig.Native.NativeOwner.Call("host_snapshot");
        Check(returned.VariantType == Variant.Type.Dictionary, $"{label}: explicit native state result");
        using Dictionary state = returned.AsGodotDictionary();
        using Variant fps = state["frames_per_second"];
        using Variant count = state["binding_count"];
        using Variant elapsed = state["elapsed_seconds_bits"];
        using Variant shown = state["shown_frames"];
        Check(fps.AsInt32() == rig.Native.FramesPerSecond && count.AsInt32() == rig.Native.BindingCount,
            $"{label}: immutable rate/count");
        Check(elapsed.AsInt64() == BitConverter.DoubleToInt64Bits(rig.Reference.ElapsedSeconds),
            $"{label}: elapsed bits actual 0x{elapsed.AsInt64():X16}, expected 0x{BitConverter.DoubleToInt64Bits(rig.Reference.ElapsedSeconds):X16}");
        Check(shown.AsInt32Array().SequenceEqual(rig.Reference.ShownFrames),
            $"{label}: shown frames actual [{string.Join(',', shown.AsInt32Array())}], expected [{string.Join(',', rig.Reference.ShownFrames)}]");
        foreach ((MeshInstance3D expected, MeshInstance3D actual) in rig.Nodes)
            if (GodotObject.IsInstanceValid(expected) && GodotObject.IsInstanceValid(actual))
                CompareTransform(expected.Transform, actual.Transform, label);
    }

    private void CompareTransform(Transform3D expected, Transform3D actual, string label)
    {
        uint[] wanted = TransformWords(expected), got = TransformWords(actual);
        for (int index = 0; index < wanted.Length; index++)
            Check(wanted[index] == got[index], $"{label}: transform word {index}: expected 0x{wanted[index]:X8}, actual 0x{got[index]:X8}");
    }

    private void CompareFailure(Exception? expected, Exception? actual, string label)
    {
        Check(expected?.GetType() == actual?.GetType(), $"{label}: expected {expected?.GetType().Name ?? "success"}, actual {actual?.ToString() ?? "success"}");
        if (expected is ArgumentException wanted && actual is ArgumentException got)
            Check(wanted.ParamName == got.ParamName, $"{label}: expected parameter '{wanted.ParamName}', actual '{got.ParamName}'");
    }

    private void NativeFailure(GDScript script, string method, Variant[] arguments, string expected)
    {
        using Variant returned = script.Call(method, arguments);
        Check(returned.VariantType == Variant.Type.Dictionary, "Native refusal returns a completion dictionary.");
        using Dictionary result = returned.AsGodotDictionary();
        using Variant ok = result["ok"];
        using Variant type = result["error_type"];
        Check(ok.VariantType == Variant.Type.Bool && !ok.AsBool() && type.AsString() == expected,
            $"Native {method} refuses impossible transport as {expected}.");
        foreach (Variant argument in arguments) argument.Dispose();
    }

    private void Check(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
        _checks++;
    }

    private static Exception? Catch(Action operation)
    {
        try { operation(); return null; }
        catch (Exception error) { return error; }
    }

    private static Dictionary Checked(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidOperationException("Native static animation aborted without a completion result.");
        Dictionary result = returned.AsGodotDictionary();
        using Variant ok = result["ok"];
        if (ok.VariantType == Variant.Type.Bool && ok.AsBool()) return result;
        using (result)
        using (Variant error = result["error"])
            throw new InvalidOperationException("Unexpected native refusal: " + error.AsString());
    }

    private static uint[] TransformWords(Transform3D value) => new[]
    {
        value.Basis.X.X, value.Basis.X.Y, value.Basis.X.Z,
        value.Basis.Y.X, value.Basis.Y.Y, value.Basis.Y.Z,
        value.Basis.Z.X, value.Basis.Z.Y, value.Basis.Z.Z,
        value.Origin.X, value.Origin.Y, value.Origin.Z,
    }.Select(BitConverter.SingleToUInt32Bits).ToArray();

    private static Dictionary FrameFacts(Level100RigidFrame frame) => new()
    {
        ["basis_bits"] = frame.Basis.Select(value => (long)BitConverter.SingleToUInt32Bits(value)).ToArray(),
        ["origin_bits"] = frame.Origin.Select(value => (long)BitConverter.SingleToUInt32Bits(value)).ToArray(),
    };

    private static Transform3D Sentinel(int index) => new(Basis.Identity, new Vector3(900 + index, -700 - index, 31));

    private static Level100RigidFrame[] Frames(int count, int offset = 0) => Enumerable.Range(0, count)
        .Select(index => new Level100RigidFrame(
            index % 2 == 0 ? [1, 0, 0, 0, 1, 0, 0, 0, 1] : [0, -1, 0, 1, 0, 0, 0, 0, 1],
            [index + offset, -index - offset, index * 0.25f])).ToArray();

    private sealed record Spec(int Playback, int LoopFrames, Level100RigidFrame[]? Frames)
    {
        public bool NullBinding { get; init; }
        public bool NullMesh { get; init; }
        public bool NullPart { get; init; }
        public bool NullNode { get; init; }
        public int NodeGroup { get; init; } = -1;
        public static Spec Loop(int length) => new(0, length, StaticAnimationChecks.Frames(Math.Max(1, length)));
    }

    private sealed class Rig : IDisposable
    {
        public readonly List<(MeshInstance3D Expected, MeshInstance3D Actual)> Nodes = [];
        public readonly LegacyDriver Reference;
        public readonly Level100StaticWorldAnimationDriver Native;

        public Rig(int fps, Spec[] specs)
        {
            List<Level100StaticWorldAnimationBinding> expected = [], actual = [];
            System.Collections.Generic.Dictionary<int, int> groups = [];
            foreach ((Spec spec, int index) in specs.Select((spec, index) => (spec, index)))
            {
                if (spec.NullBinding) { expected.Add(null!); actual.Add(null!); continue; }
                MeshInstance3D? referenceNode = null, nativeNode = null;
                if (!spec.NullNode)
                {
                    int key = spec.NodeGroup < 0 ? index + 1000 : spec.NodeGroup;
                    if (!groups.TryGetValue(key, out int nodeIndex))
                    {
                        nodeIndex = Nodes.Count;
                        groups.Add(key, nodeIndex);
                        Nodes.Add((new() { Transform = Sentinel(index) }, new() { Transform = Sentinel(index) }));
                    }
                    (referenceNode, nativeNode) = Nodes[nodeIndex];
                }
                Level100StaticWorldMeshAnimation? mesh = spec.NullMesh ? null : new("test", 4,
                    (Level100StaticWorldPlayback)spec.Playback, spec.LoopFrames, "", []);
                Level100StaticWorldAnimatedPart? part = spec.NullPart ? null : new(0, "test", 0, 0, spec.Frames!);
                expected.Add(new(mesh!, part!, referenceNode!));
                actual.Add(new(mesh!, part!, nativeNode!));
            }
            Reference = new(fps, expected);
            try { Native = new(fps, actual); }
            catch
            {
                foreach ((MeshInstance3D expectedNode, MeshInstance3D actualNode) in Nodes)
                { expectedNode.Free(); actualNode.Free(); }
                throw;
            }
        }

        public void Dispose()
        {
            Native.Dispose();
            foreach ((MeshInstance3D expected, MeshInstance3D actual) in Nodes)
            {
                if (GodotObject.IsInstanceValid(expected)) expected.Free();
                if (GodotObject.IsInstanceValid(actual)) actual.Free();
            }
        }
    }

    // Exact original algorithm from 1bb29345:Level100StaticWorldAsset.cs,
    // including its unchecked LCM and mutation-before-setter behavior. Only
    // these read-only diagnostics and the class name are added for comparison.
    private sealed class LegacyDriver(int framesPerSecond, IReadOnlyList<Level100StaticWorldAnimationBinding> bindings)
    {
        private readonly int[] _shownFrames = new int[bindings.Count];
        private double _elapsedSeconds;
        public int[] ShownFrames => (int[])_shownFrames.Clone();
        public double ElapsedSeconds => _elapsedSeconds;
        public int FramesPerSecond { get; } = framesPerSecond;

        public void Update(float frameDelta)
        {
            if (!float.IsFinite(frameDelta) || frameDelta <= 0f) return;
            _elapsedSeconds += frameDelta;
            double period = LongestLapSeconds();
            if (period > 0d && _elapsedSeconds >= period) _elapsedSeconds %= period;
            for (int index = 0; index < bindings.Count; index++)
            {
                Level100StaticWorldAnimationBinding binding = bindings[index];
                int frame = binding.Mesh.SelectVirtualFrame(_elapsedSeconds, FramesPerSecond);
                if (frame == _shownFrames[index]) continue;
                _shownFrames[index] = frame;
                binding.Node.Transform = ToObjSpaceTransform(binding.Part.Frames[frame]);
            }
        }

        public static Transform3D ToObjSpaceTransform(Level100RigidFrame frame)
        {
            float[] basis = frame.Basis;
            return new Transform3D(new Basis(
                new Vector3(basis[0], basis[3], basis[6]),
                new Vector3(basis[1], basis[4], basis[7]),
                new Vector3(basis[2], basis[5], basis[8])),
                new Vector3(frame.Origin[0], frame.Origin[1], frame.Origin[2]));
        }

        private double LongestLapSeconds()
        {
            long lapFrames = 1;
            foreach (Level100StaticWorldAnimationBinding binding in bindings)
                if (binding.Mesh.LoopFrameCount > 0) lapFrames = Lcm(lapFrames, binding.Mesh.LoopFrameCount);
            return lapFrames / (double)FramesPerSecond;
        }

        private static long Lcm(long left, long right)
        {
            long a = left, b = right;
            while (b != 0) (a, b) = (b, a % b);
            return left / a * right;
        }
    }
}
