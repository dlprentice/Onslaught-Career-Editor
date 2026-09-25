// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FrontendSessionSceneChecks
{
    /// <summary>
    /// Failure boundaries from RetailFrontendFlow.cs/.Options.cs at 02cc3dfb:
    /// initialization applies settings before page setup; Confirm mutates the
    /// Session before Select audio/navigation; Loading consumes its edge before
    /// the host callback; activation marks/hides the frontend before Captured.
    /// These are existing partial-write laws, not fabricated combat outcomes.
    /// Every callback here runs inside an explicit checked facade command, so
    /// expected failures must rethrow their original object without engine logs.
    /// </summary>
    private void CheckHostEffects()
    {
        Input.MouseModeEnum pointer = Input.MouseMode;
        CheckInitializationEffectFailure();
        CheckSelectEffectFailure();
        CheckLoadingStartedEffectFailure();
        CheckLoadRequestedEffectFailure();
        CheckCapturedEffectFailure();
        CheckNavigationEffectReentry();
        Check(Input.MouseMode == pointer, "Checked host effects never take ownership of the physical pointer.");
    }

    private void CheckInitializationEffectFailure()
    {
        RetailFrontendFlow flow = RetailFrontendFlow.InstantiateScene();
        try
        {
            var expected = new IOException("synthetic frontend initialization observer failure");
            var events = new List<string>();
            float observedVolume = float.NaN;
            flow.AudioCueRequested += _ => events.Add("audio");
            flow.CursorModeRequested += _ => events.Add("cursor");
            flow.OptionsSettingsChanged += settings =>
            {
                events.Add("settings");
                observedVolume = settings.SoundVolume;
                Check(flow.CurrentScreen == RetailFrontendScreen.ClickToStart,
                    "Initialization publishes the current cold Session before its settings observer.");
                Check(flow.OptionsSettings.SoundVolume == settings.SoundVolume,
                    "Initialization publishes admitted settings before its observer.");
                throw expected;
            };
            Check(ReferenceEquals(EffectFailure(() => flow.Initialize([])), expected),
                "Initialization rethrows the exact apply_settings exception object.");
            Check(!EffectFlag(flow, "_initialized") && flow.CurrentScreen == RetailFrontendScreen.ClickToStart,
                "Failed initialization retains its created Session without setting the completion guard.");
            Check(flow.OptionsSettings.SoundVolume == observedVolume && events.SequenceEqual(["settings"]),
                "Failed initialization retains configured settings and stops before later effects.");
            Check(flow.PendingCallbackFailureCount == 0,
                "Initialization failure leaves no retained exception token.");
            Check(EffectFailure(() => flow.Initialize(null!)) is ArgumentNullException argument
                    && argument.ParamName == "careerDescriptors",
                "An unfinished initialization still checks a later null descriptor argument.");
            // The original LoadLocalization uses Dictionary.Add; those earlier
            // writes survive the callback failure, so a valid retry refuses the
            // duplicate localization key before reaching the observer again.
            Check(EffectFailure(() => flow.Initialize([])) is ArgumentException,
                "Initialization retry preserves the existing duplicate-localization refusal.");
            Check(events.SequenceEqual(["settings"]) && !EffectFlag(flow, "_initialized")
                    && flow.PendingCallbackFailureCount == 0,
                "A refused retry neither replays settings effects nor retains exception transport.");
        }
        finally { ReleaseEffectFlow(flow); }
    }

    private void CheckSelectEffectFailure()
    {
        RetailFrontendFlow flow = CreateEffectFlow();
        try
        {
            var expected = new ArgumentException("synthetic Select observer failure");
            var events = new List<string>();
            void Fail(RetailFrontendAudioCue cue)
            {
                events.Add("audio:" + cue);
                Check(cue == RetailFrontendAudioCue.Select && flow.CurrentScreen == RetailFrontendScreen.MainMenu,
                    "Select audio sees the already-changed Main Menu in the host cache.");
                throw expected;
            }
            flow.AudioCueRequested += Fail;
            flow.CursorModeRequested += mode => events.Add("cursor:" + mode);
            Check(ReferenceEquals(EffectFailure(flow.ConfirmForSmoke), expected),
                "Confirm rethrows the exact Select-audio exception object.");
            flow.AudioCueRequested -= Fail;
            Check(flow.CurrentScreen == RetailFrontendScreen.MainMenu && events.SequenceEqual(["audio:Select"]),
                "Audio failure retains the Session transition and stops before navigation cursor effects.");
            Check(flow.View.GetNode<Control>("Stage/ClickToStart").Visible
                    && !flow.View.GetNode<Control>("Stage/MainMenu").Visible,
                "Audio failure stops before the old Confirm redraw point.");
            Check(flow.PendingCallbackFailureCount == 0, "Select failure releases its exception token.");
            Check(!AdvanceEffectFlow(flow), "The next Main Menu advance does not report a gameplay activation.");
            Check(flow.View.GetNode<Control>("Stage/MainMenu").Visible
                    && !flow.View.GetNode<Control>("Stage/ClickToStart").Visible
                    && EffectInteger(flow, "_main_transition_count") == 1,
                "A later advance resumes the existing first-frame Main Menu reveal from the partial state.");
            Check(events.SequenceEqual(["audio:Select"]) && flow.PendingCallbackFailureCount == 0,
                "Resuming a frame does not replay the interrupted audio or cursor effects.");
        }
        finally { ReleaseEffectFlow(flow); }
    }

    private void CheckLoadingStartedEffectFailure()
    {
        RetailFrontendFlow flow = CreateEffectFlow();
        try
        {
            EnterEffectConfiguration(flow);
            var expected = new InvalidOperationException("synthetic loading-start observer failure");
            var events = new List<string>();
            void FailStart()
            {
                events.Add("loading_started");
                Check(flow.CurrentScreen == RetailFrontendScreen.Loading
                        && EffectInteger(flow, "_loading_frames") == 0
                        && !EffectFlag(flow, "_load_request_raised") && !EffectFlag(flow, "_level100_ready")
                        && !EffectFlag(flow, "_gameplay_activation_raised"),
                    "LoadingStarted observes the new page and all preceding loading-flag resets.");
                throw expected;
            }
            flow.AudioCueRequested += cue => events.Add("audio:" + cue);
            flow.Level100LoadingStarted += FailStart;
            flow.CursorModeRequested += mode => events.Add("cursor:" + mode);
            flow.Level100LoadRequested += () => { events.Add("load_requested"); flow.MarkLevel100Ready(); };
            flow.GameplayActivated += () => events.Add("gameplay_activated");
            Check(ReferenceEquals(EffectFailure(flow.ConfirmForSmoke), expected),
                "LoadingStarted rethrows its exact observer exception.");
            flow.Level100LoadingStarted -= FailStart;
            Check(events.SequenceEqual(["audio:Select", "loading_started"]),
                "LoadingStarted failure follows Select audio and suppresses Hidden cursor and later effects.");
            Check(flow.View.GetNode<Control>("Stage/SelectConfiguration").Visible
                    && !flow.View.GetNode<Control>("Stage/Loading").Visible
                    && flow.PendingCallbackFailureCount == 0,
                "LoadingStarted failure stops before redraw and releases its token.");
            Check(!AdvanceEffectFlow(flow) && EffectInteger(flow, "_loading_frames") == 1,
                "The following frame resumes Loading without consuming its two-frame edge early.");
            Check(AdvanceEffectFlow(flow), "The second Loading frame returns the successful activation result.");
            Check(flow.CurrentScreen == RetailFrontendScreen.Gameplay && events.SequenceEqual([
                    "audio:Select", "loading_started", "load_requested", "cursor:Captured", "gameplay_activated"]),
                "Later frames consume the surviving edge exactly once without replaying LoadingStarted or Hidden.");
            Check(flow.PendingCallbackFailureCount == 0, "Resumed Loading leaves no pending callback token.");
        }
        finally { ReleaseEffectFlow(flow); }
    }

    private void CheckLoadRequestedEffectFailure()
    {
        RetailFrontendFlow flow = CreateEffectFlow();
        try
        {
            EnterEffectConfiguration(flow);
            flow.ConfirmForSmoke();
            var expected = new IOException("synthetic load observer failure after ready");
            var events = new List<string>();
            void FailLoad()
            {
                events.Add("load_requested");
                Check(flow.CurrentScreen == RetailFrontendScreen.Loading && EffectFlag(flow, "_load_request_raised"),
                    "The host sees Loading after the one-shot request was consumed and marked raised.");
                flow.MarkLevel100Ready();
                Check(EffectFlag(flow, "_level100_ready"), "Reentrant MarkReady commits before the observer throws.");
                throw expected;
            }
            flow.Level100LoadRequested += FailLoad;
            flow.CursorModeRequested += mode => events.Add("cursor:" + mode);
            flow.GameplayActivated += () => events.Add("gameplay_activated");
            Check(!AdvanceEffectFlow(flow) && events.Count == 0, "First Loading frame emits no load callback.");
            Check(ReferenceEquals(EffectFailure(() => AdvanceEffectFlow(flow)), expected),
                "Advance rethrows the exact load exception through its nested MarkReady call.");
            flow.Level100LoadRequested -= FailLoad;
            Check(flow.CurrentScreen == RetailFrontendScreen.Loading && EffectInteger(flow, "_loading_frames") == 2
                    && EffectFlag(flow, "_load_request_raised") && EffectFlag(flow, "_level100_ready")
                    && !EffectFlag(flow, "_gameplay_activation_raised") && events.SequenceEqual(["load_requested"]),
                "Load failure retains consumed/ready writes and stops before completion, cursor capture and activation.");
            Check(flow.PendingCallbackFailureCount == 0, "Nested MarkReady and load failure leave no exception tokens.");
            Check(AdvanceEffectFlow(flow), "A later explicit frame completes the retained ready handoff.");
            Check(flow.CurrentScreen == RetailFrontendScreen.Gameplay && events.SequenceEqual([
                    "load_requested", "cursor:Captured", "gameplay_activated"])
                    && EffectInteger(flow, "_loading_frames") == 3,
                "Resumed loading activates once without calling the failed load observer again.");
            Check(flow.PendingCallbackFailureCount == 0, "Completed recovery leaves no callback transport state.");
        }
        finally { ReleaseEffectFlow(flow); }
    }

    private void CheckCapturedEffectFailure()
    {
        RetailFrontendFlow flow = CreateEffectFlow();
        try
        {
            EnterEffectConfiguration(flow);
            flow.ConfirmForSmoke();
            var expected = new NotSupportedException("synthetic Captured cursor observer failure");
            var events = new List<string>();
            flow.Level100LoadRequested += () => { events.Add("load_requested"); flow.MarkLevel100Ready(); };
            void FailCursor(RetailFrontendCursorMode mode)
            {
                events.Add("cursor:" + mode);
                Check(mode == RetailFrontendCursorMode.Captured && flow.CurrentScreen == RetailFrontendScreen.Gameplay,
                    "Captured cursor observes the already-completed Gameplay Session.");
                Check(EffectFlag(flow, "_gameplay_activation_raised") && !flow.View.Visible
                        && !flow.View.IsProcessing() && !flow.View.IsProcessingInput(),
                    "The original activation flag, hide and process/input writes precede Captured.");
                throw expected;
            }
            flow.CursorModeRequested += FailCursor;
            flow.GameplayActivated += () => events.Add("gameplay_activated");
            Check(!AdvanceEffectFlow(flow), "Captured-failure fixture retains the first Loading frame.");
            Check(ReferenceEquals(EffectFailure(() => AdvanceEffectFlow(flow)), expected),
                "Captured cursor failure rethrows the exact observer exception.");
            flow.CursorModeRequested -= FailCursor;
            Check(events.SequenceEqual(["load_requested", "cursor:Captured"])
                    && flow.CurrentScreen == RetailFrontendScreen.Gameplay && flow.PendingCallbackFailureCount == 0,
                "Captured failure suppresses GameplayActivated and releases its exception token.");
            Check(!AdvanceEffectFlow(flow) && events.SequenceEqual(["load_requested", "cursor:Captured"]),
                "The retained activation guard prevents a later manual frame from replaying a failed activation edge.");
            Check(!flow.View.Visible && !flow.View.IsProcessing() && !flow.View.IsProcessingInput()
                    && flow.PendingCallbackFailureCount == 0,
                "A later explicit advance preserves the old hidden/stopped partial-activation state.");
        }
        finally { ReleaseEffectFlow(flow); }
    }

    private void CheckNavigationEffectReentry()
    {
        RetailFrontendFlow flow = CreateEffectFlow();
        try
        {
            var events = new List<string>();
            bool reentered = false;
            flow.AudioCueRequested += cue =>
            {
                events.Add("audio:" + cue + ":" + flow.CurrentScreen);
                if (reentered) return;
                reentered = true;
                Check(flow.CurrentScreen == RetailFrontendScreen.MainMenu,
                    "The outer Select observer sees Main Menu before its reentrant navigation.");
                flow.SelectMainIndexForCapture(0);
                flow.ConfirmForSmoke();
                Check(flow.CurrentScreen == RetailFrontendScreen.DevSelect,
                    "The outer observer immediately sees the completed nested career-page transition.");
            };
            flow.CursorModeRequested += mode => events.Add("cursor:" + mode + ":" + flow.CurrentScreen);
            flow.ConfirmForSmoke();
            Check(reentered && events.SequenceEqual([
                    "audio:Select:MainMenu", "audio:Select:DevSelect", "cursor:Custom:DevSelect", "cursor:Custom:DevSelect"]),
                "Nested navigation completes its audio/cursor pair before the outer cursor effect, with current cached facts.");
            Check(flow.CurrentScreen == RetailFrontendScreen.DevSelect
                    && flow.View.GetNode<Control>("Stage/CareerName").Visible,
                "The outer redraw uses the state left by reentrant navigation.");
            Check(flow.PendingCallbackFailureCount == 0, "General callback reentry leaves no retained exception token.");
            Check(EffectFailure(() => flow.Initialize(null!)) is InvalidOperationException,
                "Successful initialization still rejects repeats before checking a null descriptor argument.");
        }
        finally { ReleaseEffectFlow(flow); }
    }

    private RetailFrontendFlow CreateEffectFlow()
    {
        RetailFrontendFlow flow = RetailFrontendFlow.InstantiateScene();
        try
        {
            flow.Initialize([]);
            AddChild(flow.View);
            flow.View.SetProcess(false);
            flow.View.SetProcessInput(false);
            return flow;
        }
        catch { ReleaseEffectFlow(flow); throw; }
    }

    private void EnterEffectConfiguration(RetailFrontendFlow flow)
    {
        for (int index = 0; index < 5; index++) flow.ConfirmForSmoke();
        Check(flow.CurrentScreen == RetailFrontendScreen.SelectConfiguration,
            "Effect fixture reaches the existing one-configuration route without a game world.");
    }

    private void ReleaseEffectFlow(RetailFrontendFlow flow)
    {
        try
        {
            Check(flow.View.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0
                    && flow.View.FindChildren("*", "Camera3D", true, false).Count == 0,
                "The isolated effect fixture starts no audio player or gameplay world.");
        }
        finally
        {
            flow.Dispose();
            if (GodotObject.IsInstanceValid(flow.View)) flow.View.Free();
        }
    }

    private static bool AdvanceEffectFlow(RetailFrontendFlow flow)
    {
        using D result = flow.InvokeNative("advance", 0d);
        if (!result.TryGetValue("value", out Variant value)) return false;
        using (value) return value.VariantType == Variant.Type.Bool && value.AsBool();
    }

    private static bool EffectFlag(RetailFrontendFlow flow, string field)
    {
        using Variant value = flow.View.Get(field);
        return value.AsBool();
    }

    private static long EffectInteger(RetailFrontendFlow flow, string field)
    {
        using Variant value = flow.View.Get(field);
        return value.AsInt64();
    }

    private static Exception? EffectFailure(Action action)
    {
        try { action(); return null; }
        catch (Exception error) { return error; }
    }
}
