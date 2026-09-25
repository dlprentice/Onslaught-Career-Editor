// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Executes the production frontend and its native state bridge without a game
/// world, device input, playback or save writes. The explicit tracked gold
/// fixture is read only; --skipfmv prevents starting the level movie.
/// </summary>
public sealed partial class FrontendSessionSceneChecks : Node
{
    private int _checks;

    public override async void _Ready()
    {
        List<RetailFrontendFlow> facades = [];
        try
        {
            string[] arguments = OS.GetCmdlineUserArgs();
            Check(arguments.Contains("--skipfmv", StringComparer.Ordinal), "This focused harness requires --skipfmv.");
            string fixture = arguments.Single(value => value.StartsWith("--gold-career-fixture=", StringComparison.Ordinal))
                ["--gold-career-fixture=".Length..];
            Check(Path.IsPathFullyQualified(fixture), "Fixture path must be explicit and absolute.");
            byte[] fixtureBytes = File.ReadAllBytes(fixture);
            byte[] fixtureHash = SHA256.HashData(fixtureBytes);
            RetailCareerSave save = RetailCareerSaveCodec.Read(fixtureBytes);
            var first = new RetailCareerDescriptor(7, "same slot and name", save);
            var second = new RetailCareerDescriptor(7, "same slot and name", save);

            CheckNativePathAgainstReference();
            GD.Print("FRONTEND_SESSION_SCENE_SECTION: native_path");
            CheckTransportAndOwnership(first, second);
            GD.Print("FRONTEND_SESSION_SCENE_SECTION: ownership_and_transport");
            CheckHostEffects();
            GD.Print("FRONTEND_SESSION_SCENE_SECTION: host_effect_failures_reentry");

            Input.MouseModeEnum pointerBefore = Input.MouseMode;
            RetailFrontendFlow view = RetailFrontendFlow.InstantiateScene(); facades.Add(view);
            Check(view.View.GetNode<Control>("Stage").GetChildCount() == 10 && view.View.HasNode("MouseCursor/Quad"),
                "The production scene retains ten authored pages and their inspectable cursor before initialization.");
            view.Initialize([first, second]);
            GdFrontendSession state = NativeState(view);
            Check(FrontendHarnessChecks.HasNativeRoot(view), "The actual root is GDScript and its managed facade cannot process or draw as a Node.");
            int careerEvents = 0;
            RetailCareerDescriptor? selected = null;
            int loads = 0, starts = 0, activations = 0, suspensions = 0, returns = 0;
            var loadWorlds = new List<int>();
            view.CareerSelected += descriptor => { careerEvents++; selected = descriptor; };
            view.Level100LoadingStarted += () => starts++;
            view.Level100LoadRequested += () =>
            {
                loads++;
                loadWorlds.Add(view.LaunchWorldNumber);
                if (view.SelectedWorldIsConstructible) view.MarkLevel100Ready();
                else view.ReturnUnconstructibleLaunchToLevelSelect();
            };
            view.GameplayActivated += () => activations++;
            view.GameplaySuspended += () => suspensions++;
            view.ReturnToMainMenuRequested += () => returns++;
            AddChild(view.View);
            view.View.SetProcess(false);
            view.View.SetProcessInput(false);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);

            Check(view.CurrentScreen == RetailFrontendScreen.ClickToStart, "Runtime opens its real click page.");
            using (var rejectedKey = new InputEventKey { Keycode = Godot.Key.Escape, PhysicalKeycode = Godot.Key.Escape, Pressed = true })
                Check(Key(view, rejectedKey), "The production key owner consumes Escape without accepting the click page.");
            Check(view.CurrentScreen == RetailFrontendScreen.ClickToStart, "Rejected input leaves the page unchanged.");
            using (var enter = new InputEventKey { Keycode = Godot.Key.Enter, PhysicalKeycode = Godot.Key.Enter, Pressed = true })
                Check(Key(view, enter), "The production key owner accepts Enter.");
            Check(view.View.GetNode<Control>("Stage/MainMenu").Visible, "Native state drives the actual Main Menu page.");
            view.SelectMainIndexForCapture(2);
            view.ConfirmForSmoke();
            Check(NativeState(view).CareerPageMode == RetailFrontendCareerPageMode.Load && NativeState(view).SelectCareerIndex(1), "Load mode selects the second supplied descriptor.");
            view.ConfirmForSmoke();
            Check(careerEvents == 1 && ReferenceEquals(selected, second) && !ReferenceEquals(selected, first),
                "CareerSelected hands the exact second verified object to the existing host seam.");
            Check(ReferenceEquals(selected!.Career, save) && selected.Career.ContainerBytes.SequenceEqual(fixtureBytes),
                "The native menu never replaces, serializes or edits the verified save bytes.");
            Check(NativeState(view).SelectedWorldNumber == save.SuggestedWorldNumber, "Loaded selection uses the verified career projection.");
            Check(NativeState(view).ConsumeSelectedCareerLoadRequest() is null, "The production load edge is consumed once.");
            Escape(view);
            Escape(view);
            Check(NativeState(view).Screen == RetailFrontendScreen.MainMenu, "Loaded campaign Back returns through the native path.");
            view.SelectMainIndexForCapture(0);
            view.ConfirmForSmoke();
            Check(view.View.GetNode<Control>("Stage/CareerName").Visible, "New Game shows the authored career page.");
            using (var character = new InputEventKey { Unicode = 'X', Pressed = true })
                Check(Key(view, character), "Actual key dispatch edits the native name.");
            Check(NativeState(view).GameName == "X" && !NativeState(view).GameNameIsFresh, "Fresh-name replacement is visible in the cached display facts.");
            view.ConfirmForSmoke();
            Check(NativeState(view).SelectedWorldNumber == 100 && view.View.GetNode<Control>("Stage/LevelSelect").Visible,
                "New Game selects the actual cold campaign root.");
            view.ConfirmForSmoke();
            view.ConfirmForSmoke();
            view.ConfirmForSmoke();
            Check(starts == 1 && loads == 0 && NativeState(view).Screen == RetailFrontendScreen.Loading,
                "Configuration emits LoadingStarted without prematurely consuming the launch edge.");
            FrontendHarnessChecks.Command(view, "advance", 0d);
            Check(loads == 0 && activations == 0, "First loading frame preserves the two-frame boundary.");
            FrontendHarnessChecks.Command(view, "advance", 0d);
            Check(loads == 1 && activations == 1 && NativeState(view).Screen == RetailFrontendScreen.Gameplay,
                "Second loading frame consumes once, accepts ready and activates once.");
            Check(!view.View.Visible && !view.View.IsProcessing() && !view.View.IsProcessingInput(), "Gameplay suspends the production frontend.");
            Check(!NativeState(view).Level100IntroCutscenePending, "Skipped intro consumes the original first-entry flag.");
            view.RestartLevel100();
            Check(starts == 2 && suspensions == 1 && !NativeState(view).Level100IntroCutscenePending,
                "Retry preserves the native campaign and does not re-arm the intro.");
            view.View.SetProcess(false);
            view.View.SetProcessInput(false);
            FrontendHarnessChecks.Command(view, "advance", 0d);
            FrontendHarnessChecks.Command(view, "advance", 0d);
            Check(loads == 2 && activations == 2 && NativeState(view).Screen == RetailFrontendScreen.Gameplay,
                "Retry uses the same load seam exactly once.");
            view.AcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.SuccessCountdown);
            Check(NativeState(view).Screen == RetailFrontendScreen.Gameplay && returns == 0, "Won countdown is not a completed handoff.");
            view.AcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.FrontEndHandoffReady);
            view.View.SetProcess(false);
            view.View.SetProcessInput(false);
            var expected = new RetailFrontendSession();
            PrepareGameplay(expected);
            Check(expected.TryAcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.FrontEndHandoffReady),
                "Retained reference accepts the same terminal handoff.");
            Check(NativeState(view).Debriefing == expected.Debriefing && returns == 1 && suspensions == 2,
                "The production Won handoff applies the actual campaign update and exact debriefing projection.");
            Check(view.View.GetNode<Control>("Stage/Debriefing").Visible && NativeState(view).Level100IntroCutscenePending,
                "Won shows the authored debriefing and re-arms the next level intro.");
            view.AcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.FrontEndHandoffReady);
            Check(returns == 1, "Repeated terminal handoff cannot apply the campaign update twice.");
            view.ConfirmForSmoke();
            Check(NativeState(view).SelectWorld(110), "Actual Won progression unlocks World 110.");
            view.ConfirmForSmoke();
            view.ConfirmForSmoke();
            view.ConfirmForSmoke();
            FrontendHarnessChecks.Command(view, "advance", 0d);
            FrontendHarnessChecks.Command(view, "advance", 0d);
            Check(loadWorlds.SequenceEqual([100, 100, 110]) && activations == 2 && NativeState(view).Screen == RetailFrontendScreen.LevelSelect,
                "Unconstructed World 110 returns through its existing seam without substituting Level 100.");
            GD.Print("FRONTEND_SESSION_SCENE_SECTION: production_handoff");

            state.Refresh();
            int boundaryCalls = view.NativeCallCount;
            byte[] beforeFrames = state.SnapshotBytes();
            int borrowedCalls = state.NativeCallCount;
            for (int index = 0; index < 1000; index++)
            {
                _ = state.SelectedMainItem;
                _ = state.CareerNames.Count;
                _ = state.GameName;
                _ = state.SelectedConfiguration;
                _ = state.SelectedBriefingBody.Count;
                _ = state.SelectedLevelName;
                _ = view.CurrentScreen;
                _ = view.LaunchWorldNumber;
                _ = view.SelectedWorldIsConstructible;
            }
            Check(state.NativeCallCount == borrowedCalls && view.NativeCallCount == boundaryCalls,
                "Repeated detached test facts and production facade getters make no native calls.");
            // Exercise the actual native _process, without a managed advance
            // call per frame. Settled presentation must leave Session untouched.
            int factSignals = 0;
            Callable observeFacts = Callable.From<Godot.Collections.Dictionary>(_ => factSignals++);
            view.View.Connect("host_state_changed", observeFacts);
            view.View.SetProcess(true);
            for (int frame = 0; frame < 3; frame++)
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            view.View.SetProcess(false);
            view.View.Disconnect("host_state_changed", observeFacts);
            Check(view.NativeCallCount == boundaryCalls && factSignals == 0 && beforeFrames.SequenceEqual(state.SnapshotBytes()),
                "Native settled frames preserve Session facts without crossing the managed facade.");
            Check(Input.MouseMode == pointerBefore, "Initialization and navigation leave pointer ownership unchanged.");
            Check(view.View.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0,
                "The test does not start audio playback.");
            Check(view.View.FindChildren("*", "Camera3D", true, false).Count == 0,
                "Frontend events do not create a gameplay world.");
            Check(SHA256.HashData(File.ReadAllBytes(fixture)).SequenceEqual(fixtureHash), "Original fixture bytes are unchanged.");
            Check(save.ContainerBytes.SequenceEqual(fixtureBytes), "Verified read owner still retains every original byte.");
            FrontendHarnessChecks.ReleaseFacades(facades);
            view.View.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(Result(() => state.Confirm()).Error == nameof(ObjectDisposedException), "Deleting the scene releases its native state bridge.");
            GD.Print("FRONTEND_SESSION_SCENE_SECTION: cached_display_and_safety");
            GD.Print($"FRONTEND_SESSION_SCENE_CHECKS: {_checks} passed; native path, exact descriptor/name transport, actual scene handoffs, cache and read-only fixture.");
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            FrontendHarnessChecks.ReleaseFacades(facades);
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private void CheckTransportAndOwnership(RetailCareerDescriptor first, RetailCareerDescriptor second)
    {
        RetailCareerDescriptor[] input = [first, second];
        using var state = new GdFrontendSession(input);
        input[1] = first;
        Check(ReferenceEquals(state.CareerDescriptors[1], second), "Host input array changes cannot replace admitted descriptor identity.");
        state.Confirm(); state.SelectMainIndex(2); state.Confirm(); state.SelectCareerIndex(1); state.Confirm();
        state.Back(); state.SelectCareerIndex(0);
        Check(ReferenceEquals(state.ConsumeSelectedCareerLoadRequest(), second),
            "A delayed load edge retains its original ordinal when the current row changes.");
        Check(state.ConsumeSelectedCareerLoadRequest() is null, "Delayed load edge remains one-shot.");
        string[] names = ["A\0B", "\ufeffhead", "\ud800alone", "\udfff", "\ud83d\ude80"];
        using var raw = new GdFrontendSession(names.Select(name => new RetailCareerDescriptor(null, name, first.Career)));
        Check(raw.CareerNames.SequenceEqual(names), "Native transport preserves NUL, BOM, paired and unpaired UTF-16 units.");
        IReadOnlyList<string> before = raw.CareerNames;
        raw.Confirm(); raw.Confirm();
        for (int index = 0; index < names.Length; index++)
        {
            raw.SelectCareerIndex(index);
            Check(raw.GameName == names[index] && raw.GameNameCursor == names[index].Length,
                "Selected raw name and cursor retain UTF-16 semantics.");
        }
        Check(before.SequenceEqual(names), "Earlier display snapshots remain detached after later selection.");
        Check(Result(() => { ((IList<string>)raw.CareerNames)[0] = "overwrite"; return null; }).Error == nameof(NotSupportedException),
            "Display callers cannot mutate the cached career list.");
        using var invalid = new GdFrontendSession([new RetailCareerDescriptor(null, null!, first.Career)]);
        var original = new RetailFrontendSession([new RetailCareerDescriptor(null, null!, first.Career)]);
        invalid.Confirm(); invalid.Confirm(); original.Confirm(); original.Confirm();
        Check(Result(() => invalid.SelectCareerIndex(0)) == Result(() => original.SelectCareerIndex(0)),
            "Null-name selection preserves the original exception type.");
        Check(invalid.SelectedCareerIndex == original.SelectedCareerIndex && invalid.GameName == original.GameName &&
            invalid.GameNameCursor == original.GameNameCursor && invalid.GameNameIsFresh == original.GameNameIsFresh,
            "Failed native operation refreshes writes that precede the original exception.");
    }

    private void CheckNativePathAgainstReference()
    {
        foreach (RetailFrontendScreen screen in Enum.GetValues<RetailFrontendScreen>())
        {
            using (var state = new GdFrontendSession())
            {
                var original = new RetailFrontendSession();
                Prepare(state, original, screen);
                foreach ((float x, float y) in new[] { (0f, 0f), (-1f, 999f), (float.NaN, float.PositiveInfinity) })
                    Check(state.AcceptsClickToStartMouse(x, y) == RetailFrontendScenePath.AcceptsClickToStartMouse(screen, x, y),
                        "Native click predicate preserves its coordinate-independent screen gate.");
                foreach (int key in new[] { 0, 0x1c, 0x39, 0x9c, 1, 0x1e, int.MinValue, int.MaxValue })
                    Check(state.AcceptsClickToStartKey(key) == RetailFrontendScenePath.AcceptsClickToStartKey(screen, key),
                        "Native key predicate retains exact DirectInput scan codes.");
                for (int index = -1; index <= 7; index++)
                    Check(state.CanAcceptMainMenuRow(index) == RetailFrontendScenePath.CanAcceptMainMenuRow(original, index),
                        "Native row admission preserves disabled and unavailable choices.");
            }
            foreach (bool startup in new[] { false, true })
            {
                CompareOperation(screen, (native, original) =>
                {
                    var actual = Result(() => (native.TryConfirmPage(startup, out RetailFrontendSignal signal), signal));
                    var expected = Result(() => (RetailFrontendScenePath.TryConfirmPage(original, startup, out RetailFrontendSignal signal), signal));
                    Check(actual == expected, "Native Confirm path preserves acceptance, signal and errors.");
                });
                CompareOperation(screen, (native, original) =>
                {
                    var actual = Result(() => (native.TryBackPage(startup, out RetailFrontendSignal signal), signal));
                    var expected = Result(() => (RetailFrontendScenePath.TryBackPage(original, startup, out RetailFrontendSignal signal), signal));
                    Check(actual == expected, "Native Back path preserves acceptance, signal and errors.");
                });
                foreach (bool consumed in new[] { false, true })
                    CompareOperation(screen, (native, original) => Check(
                        Result(() => native.TryCompleteLoading(startup, consumed)) ==
                        Result(() => RetailFrontendScenePath.TryCompleteLoading(original, startup, consumed)),
                        "Native loading predicate does not bypass the real unconsumed edge."));
                CompareOperation(screen, (native, original) => Check(
                    Result(() => native.TryCompleteIntroCutscene(startup)) ==
                    Result(() => RetailFrontendScenePath.TryCompleteIntroCutscene(original, startup)),
                    "Native intro completion preserves startup and page gates."));
            }
            foreach (Level100MissionOutcome outcome in Enum.GetValues<Level100MissionOutcome>())
                foreach (Level100MissionTerminalState terminal in Enum.GetValues<Level100MissionTerminalState>())
                    CompareOperation(screen, (native, original) => Check(
                        Result(() => native.TryAcceptWonHandoff(outcome, terminal)) ==
                        Result(() => RetailFrontendScenePath.TryAcceptWonHandoff(original, outcome, terminal)),
                        "Native Won admission matches the reference across page/outcome/terminal combinations."));
        }
    }

    private void CompareOperation(RetailFrontendScreen screen, Action<GdFrontendSession, RetailFrontendSession> operation)
    {
        using var native = new GdFrontendSession();
        var original = new RetailFrontendSession();
        Prepare(native, original, screen);
        operation(native, original);
        Check(native.Screen == original.Screen && native.SelectedMainIndex == original.SelectedMainIndex &&
            native.SelectedCareerIndex == original.SelectedCareerIndex && native.GameName == original.GameName &&
            native.SelectedWorldNumber == original.SelectedWorldNumber && native.Debriefing == original.Debriefing &&
            native.Level100IntroCutscenePending == original.Level100IntroCutscenePending,
            "Scene-path operation leaves the same observable native state.");
    }

    private static void Prepare(GdFrontendSession native, RetailFrontendSession original, RetailFrontendScreen screen)
    {
        if (screen == RetailFrontendScreen.ClickToStart) return;
        native.Confirm(); original.Confirm();
        if (screen == RetailFrontendScreen.MainMenu) return;
        if (screen is RetailFrontendScreen.QuitConfirm or RetailFrontendScreen.Options)
        {
            int index = screen == RetailFrontendScreen.QuitConfirm ? 6 : 5;
            native.SelectMainIndex(index); original.SelectMainIndex(index);
            native.Confirm(); original.Confirm(); return;
        }
        native.Confirm(); original.Confirm();
        if (screen == RetailFrontendScreen.DevSelect) return;
        native.Confirm(); original.Confirm();
        if (screen == RetailFrontendScreen.LevelSelect) return;
        native.Confirm(); original.Confirm();
        if (screen == RetailFrontendScreen.MissionBriefing) return;
        native.Confirm(); original.Confirm();
        if (screen == RetailFrontendScreen.SelectConfiguration) return;
        native.Confirm(); original.Confirm();
        if (screen == RetailFrontendScreen.Loading) return;
        native.ConsumeLevel100LaunchRequest(); original.ConsumeLevel100LaunchRequest();
        if (screen == RetailFrontendScreen.IntroCutscene)
        {
            native.BeginLevel100IntroCutscene(); original.BeginLevel100IntroCutscene(); return;
        }
        native.CompleteLevel100Load(); original.CompleteLevel100Load();
        if (screen == RetailFrontendScreen.Gameplay) return;
        native.TryAcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.FrontEndHandoffReady);
        original.TryAcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.FrontEndHandoffReady);
    }

    private static void PrepareGameplay(RetailFrontendSession value)
    {
        for (int index = 0; index < 6; index++) value.Confirm();
        value.ConsumeLevel100LaunchRequest();
        value.CompleteLevel100Load();
    }
    private readonly record struct OperationResult(object? Value, string? Error);
    private static OperationResult Result(Func<object?> operation)
    {
        try { return new(operation(), null); }
        catch (Exception error) { return new(null, error.GetType().Name); }
    }
    private static GdFrontendSession NativeState(RetailFrontendFlow value) => GdFrontendSession.BorrowExisting(value.View);
    private static bool Key(RetailFrontendFlow value, InputEventKey input) => FrontendHarnessChecks.Boolean(value, "handle_key", input);
    private void Escape(RetailFrontendFlow value)
    {
        using var key = new InputEventKey { Keycode = Godot.Key.Escape, PhysicalKeycode = Godot.Key.Escape, Pressed = true };
        Check(Key(value, key), "Production Back dispatch accepts Escape on a campaign page.");
    }
    private void Check(bool condition, string message)
    {
        _checks++;
        if (!condition) throw new InvalidOperationException(message);
    }
}
