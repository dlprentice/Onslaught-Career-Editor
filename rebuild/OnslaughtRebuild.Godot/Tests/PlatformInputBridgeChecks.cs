// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Runtime.ExceptionServices;
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Actual engine boundary checks against PlatformInputEdgeState and paired
/// InteractiveSessions. Operation families retain the existing focused tests
/// and TestSupport/GdscriptInputOracle cases. The latter is not linked into
/// this project; no runtime compiler or second fixture framework is used.
/// This scene is headless-only, writes no files and never samples physical
/// input, creates a game world, plays audio or enters the FirstFlightGame tree.
/// </summary>
public sealed partial class PlatformInputBridgeChecks : Node
{
    private const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
    private const uint Seed = 0x4F4E534Cu;
    private const string Manifest = "res://Assets/Level100/StaticWorld/level100-static-world.json";
    private static readonly string[] Required = ["edge_operations", "counters_and_snapshots", "errors_and_disposal", "session_equivalence", "host_lifetime_and_read_only"];
    private readonly List<string> _completed = [];
    private readonly Dictionary<string, int> _counts = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> _inputHashes = new(StringComparer.Ordinal);
    private int _checks, _operations, _frames;
    private string _group = Required[0];
    private string? _stateHash, _traceHash;

    public override async void _Ready()
    {
        try
        {
            Check(!Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Only an actual headless runtime is admitted.");
            Input.MouseModeEnum pointer = Input.MouseMode;
            RecordInputs();
            EdgeOperations(); Complete();
            _group = Required[1]; CountersAndSnapshots(); Complete();
            _group = Required[2]; ErrorsAndDisposal(); Complete();
            _group = Required[3]; SessionEquivalence(); Complete();
            _group = Required[4]; HostLifetime();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(GetChildCount() == 0, "Checks create no game, presentation or input nodes.");
            Check(Input.MouseMode == pointer, "No check takes pointer ownership.");
            foreach ((string path, string expected) in _inputHashes)
                Check(Hash(path) == expected, "Input bytes remain unchanged: " + path);
            Complete();
            Check(_completed.SequenceEqual(Required) && _counts.Values.All(count => count > 0)
                && _operations >= 500 && _frames >= 10, "Every required group and bounded operation family completed.");
            Report(null);
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            GD.PushError(error.ToString());
            Report(error.ToString());
            GetTree().Quit(1);
        }
    }

    private void EdgeOperations()
    {
        var expected = new PlatformInputEdgeState();
        using var actual = new GdPlatformInputEdges();
        void Run(Action<IPlatformInputEdges> operation, string label) => Mutate(expected, actual, operation, label);
        void Value<T>(Func<IPlatformInputEdges, T> operation, string label) => Read(expected, actual, operation, label);
        Run(_ => { }, "initial");
        Value(state => state.GetHeldKey(0x51), "absent held byte");
        Run(state => state.ObserveKey(0x51, true, true), "echo press ignored");
        Value(state => state.ConsumeKeyOnce(0x51), "echo did not latch");
        Run(state => state.ObserveKey(0x51, true, false), "first key press");
        Run(state => state.ObserveKey(0x52, true, false), "independent key press");
        Run(state => state.ObserveKey(0x51, false, true), "echo release ignored");
        Value(state => state.ConsumeKeyOnce(0x51), "first consume");
        Value(state => state.ConsumeKeyOnce(0x51), "second consume");
        Value(state => state.GetHeldKey(0x51), "consume leaves held byte");
        Run(state => state.ObserveKey(0x51, true, false), "duplicate non-echo press relatches");
        Run(state => state.ObserveKey(0x51, false, false), "release keeps latch");
        Value(state => state.GetHeldKey(0x51), "release clears held byte");
        Run(state => state.AdvanceFrame(), "frame retains latch");
        Value(state => state.ConsumeKeyOnce(0x51), "release-latched consume after frame");
        Check(actual.GetHeldKey(0x51) == 0 && actual.ConsumeKeyOnce(0x51) == 0, "Released key is fully consumed.");
        Run(state => state.Reset(), "clear both maps");

        foreach (byte value in new byte[] { 0, 1, 2, 127, 128, 254, 255 })
        {
            Run(state => state.ObserveJoyButton(2, 7, value), "raw joy byte " + value);
            Value(state => state.GetPreviousJoyButton(2, 7), "previous joy byte");
            Value(state => state.GetCurrentJoyButton(2, 7), "current joy byte");
            Value(state => state.IsJoyButtonRising(2, 7), "rising joy predicate");
            Value(state => state.IsJoyButtonHeld(2, 7), "held joy predicate");
            Value(state => state.IsJoyButtonFalling(2, 7), "falling joy predicate");
            Check(actual.GetCurrentJoyButton(2, 7) == value, "Unsigned byte transport preserves " + value);
            Run(state => state.AdvanceFrame(), "joy frame advance");
            Run(state => state.ObserveJoyButton(2, 7, 0), "joy release");
            Value(state => state.IsJoyButtonFalling(2, 7), "joy falling once");
            Run(state => state.AdvanceFrame(), "joy release frame");
            Value(state => state.IsJoyButtonFalling(2, 7), "joy falling clears");
        }

        int[] ids = [int.MaxValue, 9, -1, 0, int.MinValue, 2];
        foreach (int id in ids)
        {
            Run(state => state.ObserveKey(id, true, false), "signed key " + id);
            Run(state => state.ObserveJoyButton(id, int.MaxValue, 128), "signed joy/maximum button");
            Run(state => state.ObserveJoyButton(id, int.MinValue, 255), "signed joy/minimum button");
        }
        Run(state => state.AdvanceFrame(), "signed IDs frame");
        using (var reverse = new GdPlatformInputEdges())
        {
            foreach (int id in ids.Reverse())
            {
                reverse.ObserveJoyButton(id, int.MinValue, 255);
                reverse.ObserveJoyButton(id, int.MaxValue, 128);
                reverse.ObserveKey(id, true, false);
            }
            reverse.AdvanceFrame();
            PlatformInputEdgeSnapshot left = actual.Capture(), right = reverse.Capture();
            Check(left.HeldKeys.SequenceEqual(right.HeldKeys) && left.ConsumeOnceKeys.SequenceEqual(right.ConsumeOnceKeys)
                && left.CurrentJoyButtons.SequenceEqual(right.CurrentJoyButtons)
                && left.PreviousJoyButtons.SequenceEqual(right.PreviousJoyButtons), "Sorted byte rows are independent of insertion order.");
        }

        // Same deterministic operation generator as GdscriptInputOracle.
        uint random = 0x494e5054;
        uint Next() => random = unchecked(random * 1664525u + 1013904223u);
        for (int index = 0; index < 384; index++)
        {
            int operation = (int)(Next() % 11), key = (int)(Next() % 7) - 3;
            int joypad = (int)(Next() % 5) - 2, button = (int)(Next() % 7) - 3;
            byte value = unchecked((byte)Next()); bool pressed = (Next() & 4) != 0, echo = (Next() & 8) != 0;
            string label = "varied " + index;
            switch (operation)
            {
                case 0: Run(state => state.ObserveKey(key, pressed, echo), label); break;
                case 1: Value(state => state.GetHeldKey(key), label); break;
                case 2: Value(state => state.ConsumeKeyOnce(key), label); break;
                case 3: Run(state => state.ObserveJoyButton(joypad, button, value), label); break;
                case 4: Value(state => state.GetPreviousJoyButton(joypad, button), label); break;
                case 5: Value(state => state.GetCurrentJoyButton(joypad, button), label); break;
                case 6: Value(state => state.IsJoyButtonRising(joypad, button), label); break;
                case 7: Value(state => state.IsJoyButtonHeld(joypad, button), label); break;
                case 8: Value(state => state.IsJoyButtonFalling(joypad, button), label); break;
                case 9: Run(state => state.AdvanceFrame(), label); break;
                case 10: Run(state => state.Reset(), label); break;
            }
        }
    }

    private void CountersAndSnapshots()
    {
        foreach ((long frame, long generation) in new[] { (0L, 0L), (9_007_199_254_740_993L, -9_007_199_254_740_993L),
            ((long)int.MaxValue + 1, (long)int.MinValue - 1), (long.MaxValue, long.MaxValue), (long.MinValue, long.MinValue) })
        {
            var expected = new PlatformInputEdgeState();
            using var actual = new GdPlatformInputEdges();
            typeof(PlatformInputEdgeState).GetField("<FrameIndex>k__BackingField", Private)!.SetValue(expected, frame);
            typeof(PlatformInputEdgeState).GetField("<ResetGeneration>k__BackingField", Private)!.SetValue(expected, generation);
            Native(actual).Set("_frame_index", frame);
            Native(actual).Set("_reset_generation", generation);
            Compare(expected, actual, "seeded full-width counters");
            Mutate(expected, actual, state => state.ObserveKey(int.MinValue, true, false), "counter key state");
            Mutate(expected, actual, state => state.ObserveJoyButton(int.MinValue, int.MaxValue, 255), "counter joy state");
            Mutate(expected, actual, state => state.AdvanceFrame(), "counter increment/wrap");
            PlatformInputEdgeSnapshot savedExpected = expected.Capture(), savedActual = actual.Capture();
            using D nativeSnapshot = Native(actual).Call("capture").AsGodotDictionary();
            using Godot.Collections.Array rows = nativeSnapshot["held_keys"].AsGodotArray();
            using D row = rows[0].AsGodotDictionary(); row["value"] = 72;
            Check(actual.GetHeldKey(int.MinValue) == 1, "Native snapshot rows cannot mutate the input owner.");
            Expect<NotSupportedException>(() => ((IList<PlatformInputKeyByte>)savedActual.HeldKeys)[0] = new(7, 2), "Managed key snapshot is read-only.");
            Expect<NotSupportedException>(() => ((IList<PlatformInputJoyButtonByte>)savedActual.CurrentJoyButtons)[0] = new(7, 8, 2), "Managed joy snapshot is read-only.");
            Mutate(expected, actual, state => state.Reset(), "generation increment/wrap");
            Compare(savedExpected, savedActual, "old snapshots survive owner reset");
            Mutate(expected, actual, state => state.AdvanceFrame(), "frame retained by reset");
            Mutate(expected, actual, state => state.Reset(), "second generation");
        }
    }

    private void ErrorsAndDisposal()
    {
        using (var actual = new GdPlatformInputEdges())
        {
            MethodInfo result = typeof(GdPlatformInputEdges).GetMethod("Result", Private)!;
            PlatformInputEdgeSnapshot before = actual.Capture();
            // Test-only access to the actual bridge admission seam: public C#
            // argument types cannot express these invalid Variant arguments.
            foreach ((string method, Variant[] args) in new (string, Variant[])[]
            {
                ("observe_key", [1.5d, true, false]), ("observe_key", [1, 1, false]),
                ("get_held_key", [(long)int.MaxValue + 1]),
                ("observe_joy_button", [0, 0, 256]), ("observe_joy_button", [0, 0, -1]),
                ("is_joy_button_rising", [0, (long)int.MinValue - 1]),
            })
            {
                Expect<ArgumentException>(() => Invoke(result, actual, [method, args]), "Explicit native refusal maps to an exception: " + method);
                Compare(before, actual.Capture(), "refused operation leaves bytes and counters untouched");
                foreach (Variant value in args) value.Dispose();
            }
            foreach (Variant value in new Variant[] { 1.5d, -1, 256, true })
            {
                using D malformed = new() { [-7] = value };
                Native(actual).Set("_held_keys", malformed);
                Expect<InvalidDataException>(() => actual.GetHeldKey(-7), "Invalid native byte carrier is never coerced or truncated.");
                Expect<InvalidDataException>(() => actual.Capture(), "Snapshot validates the same byte carrier.");
                actual.Reset(); value.Dispose();
            }
            using D badId = new() { [(long)int.MaxValue + 1] = 1 };
            Native(actual).Set("_held_keys", badId);
            Expect<InvalidDataException>(() => actual.Capture(), "Snapshot IDs cannot truncate to Int32.");
            actual.Reset();
        }

        var disposed = new GdPlatformInputEdges();
        disposed.ObserveKey(8, true, false);
        PlatformInputEdgeSnapshot saved = disposed.Capture();
        using WeakRef owner = GodotObject.WeakRef(Native(disposed))
            ?? throw new InvalidOperationException("Native input owner was invalid before disposal.");
        disposed.Dispose(); disposed.Dispose();
        using (Variant reference = owner.GetRef()) Check(reference.VariantType == Variant.Type.Nil, "Dispose releases the sole native state handle.");
        Action[] calls = [() => _ = disposed.FrameIndex, () => _ = disposed.ResetGeneration,
            () => disposed.ObserveKey(1, true, false), () => disposed.GetHeldKey(1), () => disposed.ConsumeKeyOnce(1),
            () => disposed.ObserveJoyButton(0, 0, 128), () => disposed.GetPreviousJoyButton(0, 0), () => disposed.GetCurrentJoyButton(0, 0),
            () => disposed.IsJoyButtonRising(0, 0), () => disposed.IsJoyButtonHeld(0, 0), () => disposed.IsJoyButtonFalling(0, 0),
            disposed.AdvanceFrame, disposed.Reset, () => disposed.Capture()];
        foreach (Action call in calls) Expect<ObjectDisposedException>(call, "Every public operation rejects a disposed owner.");
        Check(saved.HeldKeys.SequenceEqual([new PlatformInputKeyByte(8, 1)]), "Detached snapshot remains usable after disposal.");
    }

    private void SessionEquivalence()
    {
        Level100ActorDefinitionSet definitions = Level100StaticWorldAsset.LoadActorDefinitions();
        var expected = new InteractiveSession(Seed, definitions);
        using var input = new GdPlatformInputEdges();
        var actual = new InteractiveSession(Seed, definitions, input);
        using var expectedTape = new CommandTapeRecorder(); using var actualTape = new CommandTapeRecorder();
        expected.EnableRecording(expectedTape); actual.EnableRecording(actualTape);
        Check(expected.PlatformInput is PlatformInputEdgeState && ReferenceEquals(actual.PlatformInput, input), "Default reference and borrowed native owner retain distinct, single ownership.");
        void Both(Action<InteractiveSession> action, string label)
        {
            action(expected); action(actual); CompareSession(expected, actual, label);
        }
        void Frame(long elapsed)
        {
            FrameAdvanceResult left = expected.AdvanceFrameTicks(elapsed), right = actual.AdvanceFrameTicks(elapsed);
            Check(left.StepsAdvanced == right.StepsAdvanced && left.FrameTimeCapped == right.FrameTimeCapped
                && left.InterpolationPhase == right.InterpolationPhase && left.InterpolationPhaseScale == right.InterpolationPhaseScale,
                "Frame timing and step count remain exact.");
            Check(left.Level100MissionEvents.SequenceEqual(right.Level100MissionEvents)
                && left.AquilaFlightEvents.SequenceEqual(right.AquilaFlightEvents)
                && left.Level100DestructionEvents.SequenceEqual(right.Level100DestructionEvents)
                && left.Level100WeaponFireEvents.SequenceEqual(right.Level100WeaponFireEvents), "Frame event arrays preserve order and values.");
            CompareSession(expected, actual, "frame " + _frames++);
        }
        Both(session =>
        {
            session.PlatformInput.ObserveKey(0x51, true, false);
            session.PlatformInput.ObserveKey(0x51, false, false);
            if (session.PlatformInput.ConsumeKeyOnce(0x51) != 0) session.QueueToggleMode();
            session.PlatformInput.ObserveJoyButton(-1, int.MaxValue, 128);
        }, "release-latched action enters the existing queue");
        Frame(0); Frame(499_999); Frame(1);
        Check(actual.Metrics.ToggleEdgesConsumed == 1 && actual.PlatformInput.FrameIndex == 3, "Queued edge is consumed once at the real step boundary.");
        Both(session =>
        {
            session.PlatformInput.ObserveKey(0x51, true, true);
            if (session.PlatformInput.ConsumeKeyOnce(0x51) != 0) session.QueueToggleMode();
            session.QueueMovementPulse(1, -1); session.QueueLookPulse(-1, 1);
            session.QueuePointerMotionMilliPixels(1_750, -2_250);
            session.ObserveInput(new InteractiveInput(0, 1, true, false, false));
        }, "echo and merged consumed input");
        Frame(1_000_000);
        Both(session => session.ObserveInput(InteractiveInput.Idle), "fire release"); Frame(500_000);
        Both(session =>
        {
            session.PlatformInput.ObserveKey(int.MaxValue, true, false);
            session.QueueChangeWeapon(); session.QueueToggleMode();
            session.SetAuthenticMenuPaused(true);
        }, "pause clears held and pending input");
        long pausedTick = actual.CurrentSnapshot.Tick, pausedGeneration = actual.PlatformInput.ResetGeneration;
        Both(session => session.SetAuthenticMenuPaused(true), "repeated pause is inert");
        Check(actual.PlatformInput.ResetGeneration == pausedGeneration, "Repeated pause does not reset twice.");
        Frame(500_000); Frame(0);
        // These are explicit calls to the session API. FirstFlightGame's
        // paused _Process returns before this API and does not advance it.
        Check(actual.CurrentSnapshot.Tick == pausedTick && !actual.HasHeldOrPendingInput, "Explicit paused session calls advance platform state but not simulation or pending input.");
        Both(session => session.SetAuthenticMenuPaused(false), "resume keeps release interlock");
        Both(session => session.ObserveInput(new InteractiveInput(1, 0, true, true, false)), "held input cannot rearm after pause");
        Check(actual.InputSuspendedUntilReleased && !actual.HasHeldOrPendingInput, "Pause release interlock is unchanged.");
        Both(session => session.ObserveInput(InteractiveInput.Idle), "neutral input rearms"); Frame(500_000);
        Both(session =>
        {
            session.PlatformInput.ObserveJoyButton(int.MinValue, -1, 255);
            session.PlatformInput.ObserveKey(0x51, true, false);
            session.QueueFirePulse(); session.QueueMovementPulse(1, 0);
            session.SuspendInputUntilReleased(); // Existing focus-loss boundary.
        }, "focus loss clears all input");
        Check(actual.InputSuspendedUntilReleased && !actual.HasHeldOrPendingInput
            && actual.PlatformInput.GetCurrentJoyButton(int.MinValue, -1) == 0
            && actual.PlatformInput.ConsumeKeyOnce(0x51) == 0, "Focus suspension clears both platform bytes and session queues.");
        Both(session => session.ObserveInput(new InteractiveInput(1, 0, true, false, false)), "held focus-return input stays blocked"); Frame(500_000);
        Both(session => session.ReleaseAllInput(), "explicit host release rearms");
        Both(session =>
        {
            session.PlatformInput.ObserveKey(0x52, true, false);
            if (session.PlatformInput.ConsumeKeyOnce(0x52) != 0) session.QueueReset();
        }, "consumed reset queue");
        Frame(500_000); Frame(3_000_000);
        Check(actual.Metrics.ResetEdgesConsumed == 1 && actual.Metrics.CappedFrameCount == 1, "Reset consumption and bounded host frame retain existing behavior.");
        Expect<ArgumentOutOfRangeException>(() => expected.AdvanceFrameTicks(-1), "Reference refuses negative elapsed time.");
        Expect<ArgumentOutOfRangeException>(() => actual.AdvanceFrameTicks(-1), "Native-input session refuses the same elapsed time.");
        CompareSession(expected, actual, "failed frame does not advance platform state");
        CommandTape leftTape = expectedTape.BuildObserved("platform-input-bridge", Seed), rightTape = actualTape.BuildObserved("platform-input-bridge", Seed);
        Check(CommandTapeCodec.Serialize(leftTape) == CommandTapeCodec.Serialize(rightTape), "Exact consumed command tape, final state and trace hashes match the C# owner.");
        _stateHash = rightTape.ExpectedFinalStateHash; _traceHash = rightTape.ExpectedTraceHash;
        Check(expectedTape.NextTick > 0 && expectedTape.NextTick == actualTape.NextTick, "Tape comparison contains actual consumed simulation ticks.");
    }

    private void HostLifetime()
    {
        var host = new FirstFlightGame();
        MethodInfo create = typeof(FirstFlightGame).GetMethod("CreateSession", Private)!;
        MethodInfo release = typeof(FirstFlightGame).GetMethod("ReleasePlatformInput", Private)!;
        try
        {
            Check(!host.IsInsideTree() && host.GetChildCount() == 0, "Host lifecycle probe never enters or creates the game world.");
            var first = (InteractiveSession)Invoke(create, host, [])!;
            var owner = (GdPlatformInputEdges)first.PlatformInput;
            Check(ReferenceEquals(typeof(FirstFlightGame).GetField("_platformInput", Private)!.GetValue(host), owner), "Live host retains exactly the session's borrowed native owner.");
            owner.ObserveKey(99, true, false);
            Expect<InvalidOperationException>(() => Invoke(create, host, []), "Host refuses replacement while an input owner is live.");
            Check(first.PlatformInput.GetHeldKey(99) == 1, "Refused creation preserves the current owner.");
            Invoke(release, host, []); Invoke(release, host, []);
            Expect<ObjectDisposedException>(() => owner.Capture(), "Host release invalidates its native bridge.");
            var second = (InteractiveSession)Invoke(create, host, [])!;
            Check(second.PlatformInput is GdPlatformInputEdges && !ReferenceEquals(second.PlatformInput, owner), "Retry creates a distinct sole native owner.");
            Compare(new PlatformInputEdgeState(), second.PlatformInput, "retry begins with fresh input bytes and counters");
            Invoke(release, host, []);
            Expect<ObjectDisposedException>(() => second.PlatformInput.AdvanceFrame(), "Second host release also closes the borrowed owner.");
        }
        finally
        {
            Invoke(release, host, []);
            ((IDisposable)typeof(FirstFlightGame).GetField("_pauseMenu", Private)!.GetValue(host)!).Dispose();
            ((IDisposable)typeof(FirstFlightGame).GetField("_audioRetirement", Private)!.GetValue(host)!).Dispose();
            host.Free();
        }
    }

    private void Mutate(IPlatformInputEdges expected, IPlatformInputEdges actual, Action<IPlatformInputEdges> operation, string label)
    { operation(expected); operation(actual); _operations++; Compare(expected, actual, label); }
    private void Read<T>(IPlatformInputEdges expected, IPlatformInputEdges actual, Func<IPlatformInputEdges, T> operation, string label)
    { Check(EqualityComparer<T>.Default.Equals(operation(expected), operation(actual)), label + " value"); _operations++; Compare(expected, actual, label); }
    private void Compare(IPlatformInputEdges expected, IPlatformInputEdges actual, string label)
    {
        Check(expected.FrameIndex == actual.FrameIndex && expected.ResetGeneration == actual.ResetGeneration, label + " signed Int64 getters");
        Compare(expected.Capture(), actual.Capture(), label);
    }
    private void Compare(PlatformInputEdgeSnapshot expected, PlatformInputEdgeSnapshot actual, string label)
    {
        Check(expected.FrameIndex == actual.FrameIndex && expected.ResetGeneration == actual.ResetGeneration, label + " snapshot counters");
        Check(expected.HeldKeys.SequenceEqual(actual.HeldKeys), label + " held keys");
        Check(expected.ConsumeOnceKeys.SequenceEqual(actual.ConsumeOnceKeys), label + " consume-once keys");
        Check(expected.PreviousJoyButtons.SequenceEqual(actual.PreviousJoyButtons), label + " previous joy bytes");
        Check(expected.CurrentJoyButtons.SequenceEqual(actual.CurrentJoyButtons), label + " current joy bytes");
    }
    private void CompareSession(InteractiveSession expected, InteractiveSession actual, string label)
    {
        Compare(expected.PlatformInput, actual.PlatformInput, label);
        Check(expected.LastConsumedInput == actual.LastConsumedInput && expected.Metrics == actual.Metrics, label + " consumed input and metrics");
        Check(expected.PauseReasons == actual.PauseReasons && expected.IsPaused == actual.IsPaused
            && expected.IsAuthenticMenuPaused == actual.IsAuthenticMenuPaused
            && expected.InputSuspendedUntilReleased == actual.InputSuspendedUntilReleased
            && expected.HasHeldOrPendingInput == actual.HasHeldOrPendingInput
            && expected.InterpolationPhase == actual.InterpolationPhase, label + " pause/focus/accumulator state");
        Check(CanonicalBytes(expected.PreviousSnapshot).SequenceEqual(CanonicalBytes(actual.PreviousSnapshot)), label + " previous canonical state bytes");
        Check(CanonicalBytes(expected.CurrentSnapshot).SequenceEqual(CanonicalBytes(actual.CurrentSnapshot)), label + " current canonical state bytes");
    }
    // Core deliberately keeps its byte serializer internal. The comparison
    // reads that exact implementation without expanding the production API.
    private static byte[] CanonicalBytes(WorldSnapshot state) =>
        (byte[])typeof(StateHasher).GetMethod("GetCanonicalBytes", BindingFlags.Static | BindingFlags.NonPublic)!
            .Invoke(null, [state])!;
    private static GodotObject Native(GdPlatformInputEdges value) =>
        (GodotObject)typeof(GdPlatformInputEdges).GetField("_state", Private)!.GetValue(value)!;
    private static object? Invoke(MethodInfo method, object target, object?[] args)
    {
        try { return method.Invoke(target, args); }
        catch (TargetInvocationException error) when (error.InnerException is not null)
        { ExceptionDispatchInfo.Capture(error.InnerException).Throw(); throw; }
    }
    private void Expect<T>(Action action, string message) where T : Exception
    {
        try { action(); }
        catch (T) { Check(true, message); return; }
        throw new InvalidOperationException(message + " Expected " + typeof(T).Name + ".");
    }
    private void Check(bool condition, string message)
    {
        _checks++; _counts[_group] = _counts.GetValueOrDefault(_group) + 1;
        if (!condition) throw new InvalidOperationException(message);
    }
    private void Complete() => _completed.Add(_group);
    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(ProjectSettings.GlobalizePath(path)))).ToLowerInvariant();
    private void RecordInputs()
    {
        foreach (string path in new[] { Manifest, "res://Client/platform_input_edges.gd", "res://GdPlatformInputEdges.cs",
            "res://../OnslaughtRebuild.Client/PlatformInputEdgeState.cs", "res://../OnslaughtRebuild.Client/InteractiveSession.cs" })
            _inputHashes.Add(path, Hash(path));
        Check(_inputHashes[Manifest] == Level100ActorDefinitionManifest.ExpectedManifestSha256.ToLowerInvariant(), "Session fixture is the unchanged admitted production actor manifest.");
    }
    private void Report(string? error) => GD.Print("PLATFORM_INPUT_BRIDGE_CHECKS: ", JsonSerializer.Serialize(new
    {
        schema = 1, checks = _checks, operations = _operations, frames = _frames, completed = _completed, counts = _counts,
        input_sha256 = _inputHashes, final_state_hash = _stateHash, trace_hash = _traceHash,
        failure_count = error is null ? 0 : 1, error,
        engine = Engine.GetVersionInfo()["string"].AsString(), runtime = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,
    }));
}
