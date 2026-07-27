// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightGame : Node3D
{
    private const uint SimulationSeed = 0x4F4E534Cu;
    private const long SmokeFrameElapsedTicks = 333_334;

    private static readonly StringName MoveForwardAction = "first_flight_move_forward";
    private static readonly StringName MoveBackwardAction = "first_flight_move_backward";
    private static readonly StringName MoveLeftAction = "first_flight_move_left";
    private static readonly StringName MoveRightAction = "first_flight_move_right";
    private static readonly StringName LookLeftAction = "first_flight_look_left";
    private static readonly StringName LookRightAction = "first_flight_look_right";
    private static readonly StringName LookUpAction = "first_flight_look_up";
    private static readonly StringName LookDownAction = "first_flight_look_down";
    private static readonly StringName FireAction = "first_flight_fire";
    private static readonly StringName ToggleModeAction = "first_flight_toggle_mode";
    private static readonly StringName LandingJetsAction = "first_flight_landing_jets";
    private static readonly StringName ResetAction = "first_flight_reset";

    private InteractiveSession _session = null!;
    private readonly Level100PauseMenu _pauseMenu = new();
    private Level100Audio _audio = null!;
    private FirstFlightWorldView _world = null!;
    private FirstFlightHud _hud = null!;
    private FirstFlightPauseMenu _pauseView = null!;
    private Level100HudAssetCatalog _hudAssetCatalog = null!;
    private RetailFrontendFlow? _frontend;
    private bool _level100WorldCreated;
    private bool _gameplayActive;
    private bool _pauseExitAudioCompleted;
    private bool _smokeMode;
    private bool _captureMode;
    private bool _captureArgumentsPresent;
    private bool _skipStartupMedia;
    private bool _forceStartupMedia;
    private RetailStartupSequence? _startupSequence;
    private bool _smokeCompleting;
    private bool _windowHasFocus;
    private bool _focusLossHandlerInputCleared;
    private bool _focusLossHandlerNeutralRearmed;
    private bool _smokeSawClickToStart;
    private bool _smokeSawMainMenu;
    private bool _smokeSawDevSelect;
    private bool _smokeSawLevelSelect;
    private bool _smokeSawMissionBriefing;
    private bool _smokeSawSelectConfiguration;
    private bool _smokeSawLoading;
    private bool _smokeSawGameplay;
    private bool _smokeCursorVisibleAtFrontend;
    private bool _smokeCursorHiddenAtLoading;
    private bool _smokeCursorPolicyAppliedAtGameplay;
    private bool _smokeWindowFocusedAtGameplay;
    private string[] _smokeGameplayCursorPolicy = [];
    private readonly List<int> _smokeAudioQueuedSpeakerIds = [];
    private readonly List<int> _smokeAudioQueuedMessageIds = [];
    private readonly List<int> _smokeVoiceStartedMessageIds = [];
    private int? _smokeVoiceLastObservedMessageId;
    private bool _smokeVoicePlaybackConsistent = true;
    private bool _smokeCursorReleasedOnFocusLoss;
    private bool _smokeCursorRecapturedOnFocusGain;
    private bool _smokeRetryRequested;
    private bool _smokeRetryGameplayActivated;
    private bool _smokeRetrySessionFresh;
    private bool _smokeReturnRequested;
    private bool _smokeReturnedToMainMenu;
    private bool _smokeWorldReleasedAtMainMenu;
    private bool _smokeCursorVisibleAtMainMenu;
    private string? _smokeReportPath;
    private RetailFrontendCursorMode _requestedCursorMode = RetailFrontendCursorMode.Visible;
    private SmokePhase _smokePhase = SmokePhase.ColdFrontend;
    private SmokeReport? _smokeReport;

    public event Action<RetailFrontendAudioCue>? FrontendAudioCueRequested;

    public override void _Ready()
    {
        try
        {
            ConfigureInputMap();
            ParseUserArguments();

            Window window = GetWindow();
            window.Title = "Onslaught Rebuild - Battle Engine Aquila";
            _windowHasFocus = window.HasFocus();

            _audio = new Level100Audio();
            AddChild(_audio);
            _hudAssetCatalog = Level100HudAssetCatalog.Load();

            _frontend = new RetailFrontendFlow { Name = "RetailStartupFrontend" };
            _frontend.Initialize();
            _frontend.Level100LoadRequested += LoadLevel100FromFrontend;
            _frontend.GameplayActivated += ActivateFrontendGameplay;
            _frontend.GameplaySuspended += SuspendFrontendGameplay;
            _frontend.ReturnToMainMenuRequested += ReleaseLevel100ForMainMenu;
            _frontend.CursorModeRequested += ApplyFrontendCursorMode;
            _frontend.AudioCueRequested += ForwardFrontendAudioCue;
            AddChild(_frontend);
            ApplyFrontendCursorMode(RetailFrontendCursorMode.Visible);
            // CFrontEnd::Init starts MUS_FRONTEND once for the whole frontend
            // (FrontEnd.cpp:332-333, retail 0x004662a0), so it spans click-to-start,
            // main menu, level select and briefing.
            _audio.StartFrontendMusic();

            if (FrontendCaptureRig.TryCreate(OS.GetCmdlineUserArgs(), _frontend, out FrontendCaptureRig? rig))
            {
                // The gameplay capture plan holds the level for 42 s of engine
                // time. Without this the released policy would put the host mouse
                // into Input.MouseModeEnum.Captured for the whole run and steal
                // the operator's pointer. Cursor mode is not in the viewport
                // texture, so suppressing the OS call cannot alter a single
                // captured pixel; _requestedCursorMode still tracks the released
                // policy exactly as it does in product mode.
                _captureMode = true;
                AddChild(rig);
            }

            StartRetailStartupMedia();
        }
        catch (Exception exception)
        {
            SetProcess(false);
            GD.PushError($"Level 100 opening slice failed to initialize: {exception.Message}");
            GetTree().Quit(4);
        }
    }

    /// <summary>
    /// Pause integration seam. The frontend enters Loading and the existing
    /// host replaces its one Level 100 session/world when requested.
    /// </summary>
    public void RestartLevel100()
    {
        RequireLevel100Frontend().RestartLevel100();
    }

    /// <summary>
    /// Pause integration seam for Exit Level. This returns to the existing
    /// frontend shell; it never quits the application.
    /// </summary>
    public void LeaveLevel100ForMainMenu()
    {
        RequireLevel100Frontend().LeaveLevel100ForMainMenu();
    }

    public override void _Process(double delta)
    {
        if (_level100WorldCreated)
        {
            _pauseView.AdvanceAnimation(delta);
        }

        if (_smokeMode && !_gameplayActive)
        {
            DriveSmokeFrontend();
            return;
        }

        if (!_gameplayActive)
        {
            return;
        }

        if (_smokeMode && _smokePhase == SmokePhase.RetryGameplay)
        {
            FinishSmokeRetryAndReturn();
            return;
        }

        if (_smokeCompleting)
        {
            return;
        }

        if (_session.IsPaused)
        {
            return;
        }

        if (_smokeMode)
        {
            InteractiveInput smokeInput = FirstFlightSmokeScenario.GetInputForTick(_session.CurrentSnapshot.Tick);
            ApplySyntheticInput(smokeInput);
        }

        InteractiveInput input = SampleInput();
        _session.ObserveInput(input);
        if (input != InteractiveInput.Idle && _session.CurrentSnapshot.Level100PlayerControlEnabled)
        {
            _hud.MarkInputActivity();
        }

        long elapsedTicks = _smokeMode
            ? SmokeFrameElapsedTicks
            : Math.Max(0L, (long)Math.Round(delta * TimeSpan.TicksPerSecond, MidpointRounding.AwayFromZero));
        FrameAdvanceResult result = _session.AdvanceFrameTicks(elapsedTicks);
        ConsumeFrameEvents(result);
        _world.Render(
            result.PreviousSnapshot,
            result.CurrentSnapshot,
            (float)result.InterpolationAlpha,
            (float)delta);
        _hud.UpdateFromSnapshot(
            result.CurrentSnapshot,
            _audio.CharacterMessagePlayback);
        _hud.Visible = _world.ShowHud;

        if (_smokeMode)
        {
            SampleSmokeVoiceProgress();
        }

        if (_smokeMode && result.CurrentSnapshot.Tick >= FirstFlightSmokeScenario.DurationTicks)
        {
            _smokeCompleting = true;
            RunFocusLossHandlerSmokeProbe();
            _smokeReport = CaptureSmokeReport();
            RestartLevel100();
            _smokeRetryRequested = _frontend!.CurrentScreen == RetailFrontendScreen.Loading;
            _smokeCursorHiddenAtLoading &=
                _requestedCursorMode == RetailFrontendCursorMode.Hidden;
            _smokePhase = SmokePhase.AwaitingRetryGameplay;
        }
    }

    public override void _Input(InputEvent inputEvent)
    {
        if (_smokeMode)
        {
            return;
        }

        if (!_gameplayActive)
        {
            return;
        }

        bool authenticPausePressed =
            (inputEvent is InputEventKey pauseKey &&
                pauseKey.Pressed && !pauseKey.Echo && IsKey(pauseKey, Key.Escape)) ||
            (inputEvent is InputEventJoypadButton pauseButton &&
                pauseButton.Pressed && pauseButton.ButtonIndex == JoyButton.Start);
        if (authenticPausePressed)
        {
            if (_pauseMenu.IsOpen)
            {
                if (_pauseView.InputReady)
                {
                    ForwardFrontendAudioCue(RetailFrontendAudioCue.Back);
                    HandlePauseAction(_pauseMenu.Cancel());
                    _pauseView.Refresh();
                }
            }
            else if (!_pauseView.IsClosing)
            {
                OpenAuthenticPauseMenu();
            }
            GetViewport().SetInputAsHandled();
            return;
        }

        if (_pauseMenu.IsOpen)
        {
            if (HandleAuthenticPauseInput(inputEvent))
            {
                GetViewport().SetInputAsHandled();
            }
            return;
        }

        if (_session.IsPaused)
        {
            return;
        }

        if (inputEvent is InputEventMouseMotion mouseMotion)
        {
            if (_session.CurrentSnapshot.Transition == VehicleTransition.None)
            {
                int deltaX = ToMilliPixels(mouseMotion.ScreenRelative.X);
                int deltaY = ToMilliPixels(mouseMotion.ScreenRelative.Y);
                if (deltaX != 0 || deltaY != 0)
                {
                    _session.QueuePointerMotionMilliPixels(deltaX, deltaY);
                }
            }
            return;
        }

        if (inputEvent is not InputEventKey keyEvent || !keyEvent.Pressed || keyEvent.Echo)
        {
            return;
        }

        bool togglePressed = inputEvent.IsActionPressed(ToggleModeAction) ||
            IsKey(keyEvent, Key.Q);
        bool resetPressed = inputEvent.IsActionPressed(ResetAction) ||
            IsKey(keyEvent, Key.R);
        if (IsKey(keyEvent, Key.W) || IsKey(keyEvent, Key.Up))
        {
            _session.QueueMovementPulse(0, 1);
        }
        if (IsKey(keyEvent, Key.S) || IsKey(keyEvent, Key.Down))
        {
            _session.QueueMovementPulse(0, -1);
        }
        if (IsKey(keyEvent, Key.A) || IsKey(keyEvent, Key.Left))
        {
            _session.QueueMovementPulse(-1, 0);
        }
        if (IsKey(keyEvent, Key.D) || IsKey(keyEvent, Key.Right))
        {
            _session.QueueMovementPulse(1, 0);
        }
        if (IsKey(keyEvent, Key.Space))
        {
            _session.QueueFirePulse();
        }

        if (togglePressed)
        {
            _session.QueueToggleMode();
        }

        if (resetPressed)
        {
            _session.QueueReset();
        }

    }

    private bool HandleAuthenticPauseInput(InputEvent inputEvent)
    {
        if (!_pauseView.InputReady)
        {
            return false;
        }

        if (inputEvent is InputEventMouseMotion mouseMotion)
        {
            if (_pauseView.TryHover(mouseMotion.Position))
            {
                ForwardFrontendAudioCue(RetailFrontendAudioCue.Move);
            }
            return true;
        }

        if (inputEvent is InputEventMouseButton mouseButton && mouseButton.Pressed)
        {
            if (mouseButton.ButtonIndex == MouseButton.WheelUp)
            {
                MovePauseSelection(-1);
                return true;
            }
            if (mouseButton.ButtonIndex == MouseButton.WheelDown)
            {
                MovePauseSelection(1);
                return true;
            }
            if (mouseButton.ButtonIndex == MouseButton.Left &&
                _pauseView.TryPointAt(mouseButton.Position, out bool moved))
            {
                if (moved)
                {
                    ForwardFrontendAudioCue(RetailFrontendAudioCue.Move);
                }
                ActivatePauseSelection();
                return true;
            }
            return false;
        }

        if (inputEvent is InputEventJoypadButton joypadButton && joypadButton.Pressed)
        {
            switch (joypadButton.ButtonIndex)
            {
                case JoyButton.DpadUp:
                    MovePauseSelection(-1);
                    return true;
                case JoyButton.DpadDown:
                    MovePauseSelection(1);
                    return true;
                case JoyButton.A:
                    ActivatePauseSelection();
                    return true;
                case JoyButton.B:
                    ForwardFrontendAudioCue(RetailFrontendAudioCue.Back);
                    HandlePauseAction(_pauseMenu.Cancel());
                    _pauseView.Refresh();
                    return true;
            }
            return false;
        }

        if (inputEvent is not InputEventKey keyEvent || !keyEvent.Pressed || keyEvent.Echo)
        {
            return false;
        }

        if (IsKey(keyEvent, Key.Up))
        {
            MovePauseSelection(-1);
            return true;
        }
        if (IsKey(keyEvent, Key.Down))
        {
            MovePauseSelection(1);
            return true;
        }
        if (IsKey(keyEvent, Key.Enter) ||
            IsKey(keyEvent, Key.KpEnter) ||
            IsKey(keyEvent, Key.Space))
        {
            ActivatePauseSelection();
            return true;
        }

        return false;
    }

    private void MovePauseSelection(int direction)
    {
        if (_pauseMenu.MoveSelection(direction))
        {
            ForwardFrontendAudioCue(RetailFrontendAudioCue.Move);
            _pauseView.Refresh();
        }
    }

    private void ActivatePauseSelection()
    {
        Level100PauseAction action = _pauseMenu.ActivateSelected();
        if (action is not Level100PauseAction.RetryLevel and
            not Level100PauseAction.ReturnToFrontend)
        {
            ForwardFrontendAudioCue(RetailFrontendAudioCue.Select);
        }
        HandlePauseAction(action);
        _pauseView.Refresh();
    }

    private void OpenAuthenticPauseMenu()
    {
        _pauseMenu.Open();
        _session.SetAuthenticMenuPaused(true);
        _audio.SetGameplayPaused(true);
        _pauseView.Open();
        UpdateGameplayCursorMode();
    }

    private void HandlePauseAction(Level100PauseAction action)
    {
        switch (action)
        {
            case Level100PauseAction.None:
                return;
            case Level100PauseAction.Resume:
                ResumeFromAuthenticPause();
                return;
            case Level100PauseAction.RetryLevel:
                CompletePauseExitAudio();
                CloseAuthenticPauseForLifecycle();
                RestartLevel100();
                return;
            case Level100PauseAction.ReturnToFrontend:
                CompletePauseExitAudio();
                CloseAuthenticPauseForLifecycle();
                LeaveLevel100ForMainMenu();
                return;
            default:
                throw new InvalidOperationException($"Unsupported pause action {action}.");
        }
    }

    private void CompletePauseExitAudio()
    {
        _audio.StopForLevelExit(playFrontendSelect: true);
        _pauseExitAudioCompleted = true;
        RaiseFrontendAudioCueRequested(RetailFrontendAudioCue.Select);
    }

    private void ResumeFromAuthenticPause()
    {
        _session.SetAuthenticMenuPaused(false);
        _audio.SetGameplayPaused(false);
        _pauseView.Close();
        UpdateGameplayCursorMode();
    }

    private void CloseAuthenticPauseForLifecycle()
    {
        _pauseMenu.Reset();
        _session.SetAuthenticMenuPaused(false);
        _audio.SetGameplayPaused(false);
        _pauseView.Reset();
    }

    public override void _Notification(int what)
    {
        if (what == NotificationWMWindowFocusOut)
        {
            _windowHasFocus = false;
            if (_gameplayActive && (!_smokeMode || _smokeCompleting))
            {
                _session.SuspendInputUntilReleased();
                UpdateGameplayCursorMode();
                _smokeCursorReleasedOnFocusLoss =
                    _requestedCursorMode == RetailFrontendCursorMode.Visible;
            }
        }
        else if (what == NotificationWMWindowFocusIn)
        {
            _windowHasFocus = true;
            if (_gameplayActive)
            {
                UpdateGameplayCursorMode();
                _smokeCursorRecapturedOnFocusGain =
                    _requestedCursorMode == RetailFrontendCursorMode.Captured;
            }
        }
    }

    public override void _ExitTree()
    {
        if (!_smokeMode)
        {
            ApplyFrontendCursorMode(RetailFrontendCursorMode.Visible);
        }
        ReleaseSyntheticInput();
    }

    private static void ConfigureInputMap()
    {
        EnsureKeyAction(MoveForwardAction, Key.W);
        EnsureKeyAction(MoveForwardAction, Key.Up);
        EnsureKeyAction(MoveBackwardAction, Key.S);
        EnsureKeyAction(MoveBackwardAction, Key.Down);
        EnsureKeyAction(MoveLeftAction, Key.A);
        EnsureKeyAction(MoveLeftAction, Key.Left);
        EnsureKeyAction(MoveRightAction, Key.D);
        EnsureKeyAction(MoveRightAction, Key.Right);
        EnsureUnboundAction(LookLeftAction);
        EnsureUnboundAction(LookRightAction);
        EnsureUnboundAction(LookUpAction);
        EnsureUnboundAction(LookDownAction);
        EnsureKeyAction(FireAction, Key.Space);
        EnsureKeyAction(ToggleModeAction, Key.Q);
        EnsureKeyAction(LandingJetsAction, Key.Shift);
        EnsureKeyAction(ResetAction, Key.R);
    }

    private static void EnsureKeyAction(StringName action, Key key)
    {
        if (!InputMap.HasAction(action))
        {
            InputMap.AddAction(action, 0.2f);
        }

        bool physicalMapped = InputMap.ActionGetEvents(action)
            .OfType<InputEventKey>()
            .Any(input => input.PhysicalKeycode == key);
        if (!physicalMapped)
        {
            InputMap.ActionAddEvent(action, new InputEventKey { PhysicalKeycode = key });
        }

        bool logicalMapped = InputMap.ActionGetEvents(action)
            .OfType<InputEventKey>()
            .Any(input => input.Keycode == key);
        if (!logicalMapped)
        {
            InputMap.ActionAddEvent(action, new InputEventKey { Keycode = key });
        }
    }

    private static void EnsureUnboundAction(StringName action)
    {
        if (!InputMap.HasAction(action))
        {
            InputMap.AddAction(action, 0.2f);
        }

        InputMap.ActionEraseEvents(action);
    }

    private static bool IsKey(InputEventKey input, Key key) =>
        input.PhysicalKeycode == key || input.Keycode == key;

    private static InteractiveInput SampleInput()
    {
        sbyte moveX = QuantizeAxis(Input.GetAxis(MoveLeftAction, MoveRightAction));
        sbyte moveZ = QuantizeAxis(Input.GetAxis(MoveBackwardAction, MoveForwardAction));
        sbyte lookX = QuantizeAxis(Input.GetAxis(LookLeftAction, LookRightAction));
        sbyte lookY = QuantizeAxis(Input.GetAxis(LookUpAction, LookDownAction));
        return new InteractiveInput(
            moveX,
            moveZ,
            Input.IsActionPressed(FireAction),
            Input.IsActionPressed(ToggleModeAction),
            Input.IsActionPressed(ResetAction),
            lookX,
            lookY,
            Input.IsActionPressed(LandingJetsAction));
    }

    private static sbyte QuantizeAxis(float value)
    {
        return value switch
        {
            > 0.01f => 1,
            < -0.01f => -1,
            _ => 0,
        };
    }

    private static int ToMilliPixels(float value) =>
        (int)Math.Clamp(
            Math.Round(value * 1_000f, MidpointRounding.AwayFromZero),
            -1_000_000d,
            1_000_000d);

    private void CreateLevel100World()
    {
        if (_level100WorldCreated)
        {
            throw new InvalidOperationException("The Level 100 world is already created.");
        }

        WorldSnapshot snapshot = _session.CurrentSnapshot;
        _world = new FirstFlightWorldView();
        AddChild(_world);
        _world.Initialize(snapshot);
        _audio.BindAquila(
            RequirePlayerAquilaActorId(snapshot.Level100Actors),
            snapshot.Level100Actors);
        // Level entry is a stop-then-start handoff, not a crossfade: CGame::RunLevel
        // stops the frontend track (game.cpp:1584-1586, retail 0x0046e240) and the
        // level loop then selects MUS_TUTORIAL (game.cpp:1431-1441, retail
        // CGame::PlayMusicForCurrentLevel 0x0046dc00).
        _audio.StopFrontendMusic();
        _audio.StartTutorialMusic();

        _hud = new FirstFlightHud();
        AddChild(_hud);
        _hud.Initialize(_hudAssetCatalog);
        _hud.UpdateFromSnapshot(
            _session.CurrentSnapshot,
            _audio.CharacterMessagePlayback);
        _hud.Visible = _world.ShowHud;

        _pauseView = new FirstFlightPauseMenu();
        AddChild(_pauseView);
        _pauseView.Initialize(_pauseMenu);

        ConsumeFrameEvents(_session.AdvanceFrameTicks(0));
        _hud.UpdateFromSnapshot(
            _session.CurrentSnapshot,
            _audio.CharacterMessagePlayback);
        _level100WorldCreated = true;
    }

    private void LoadLevel100FromFrontend()
    {
        try
        {
            if (_level100WorldCreated)
            {
                DestroyLevel100World();
            }
            _session = CreateSession();
            CreateLevel100World();
            _frontend!.MarkLevel100Ready();
        }
        catch (Exception exception)
        {
            SetProcess(false);
            GD.PushError($"Level 100 failed to load from the frontend: {exception.Message}");
            GetTree().Quit(4);
        }
    }

    private void ActivateFrontendGameplay()
    {
        if (!_level100WorldCreated)
        {
            GD.PushError("The frontend tried to activate gameplay before Level 100 was ready.");
            GetTree().Quit(4);
            return;
        }

        _gameplayActive = true;
        UpdateGameplayCursorMode();
        if (_smokeMode)
        {
            if (_smokePhase == SmokePhase.ColdFrontend)
            {
                _smokeSawGameplay = true;
                CaptureSmokeGameplayCursorPolicy();
                _smokePhase = SmokePhase.InitialGameplay;
            }
            else if (_smokePhase == SmokePhase.AwaitingRetryGameplay)
            {
                _smokeRetryGameplayActivated = true;
                _smokeRetrySessionFresh =
                    _session.CurrentSnapshot.Tick == 0 &&
                    _session.Metrics.TotalSteps == 0 &&
                    _level100WorldCreated;
                _smokePhase = SmokePhase.RetryGameplay;
            }
        }
    }

    // The single boolean this replaces asserted "the cursor is Captured right
    // now", which pins HOST WINDOW FOCUS, not the rebuild: Godot cannot capture
    // an unfocused window, and one run in six observed exactly that and failed.
    // Whether the user clicked away is not evidence about this project.
    //
    // What is decidable is (a) the released policy over every (focus, pause)
    // input pair, evaluated through the same UpdateGameplayCursorMode the
    // product uses, and (b) that gameplay activation applied that policy to
    // whatever the focus actually was. Both are independent of host focus.
    // The observed focus itself is reported for honesty and never asserted.
    private void CaptureSmokeGameplayCursorPolicy()
    {
        bool actualFocus = _windowHasFocus;
        _smokeWindowFocusedAtGameplay = actualFocus;
        _smokeCursorPolicyAppliedAtGameplay =
            _requestedCursorMode ==
                (actualFocus && !_session.IsPaused
                    ? RetailFrontendCursorMode.Captured
                    : RetailFrontendCursorMode.Visible);

        var policy = new List<string>(4);
        foreach ((bool focused, bool paused) in new[]
                 {
                     (true, false),
                     (true, true),
                     (false, false),
                     (false, true),
                 })
        {
            _windowHasFocus = focused;
            _session.SetAuthenticMenuPaused(paused);
            UpdateGameplayCursorMode();
            policy.Add(_requestedCursorMode.ToString());
        }

        _session.SetAuthenticMenuPaused(false);
        _windowHasFocus = actualFocus;
        UpdateGameplayCursorMode();
        _smokeGameplayCursorPolicy = [.. policy];
    }

    // AudioStreamPlayer.Playing is wall-clock state, so "a message is audible
    // at tick N" is not decidable by the simulation. What IS decidable, and
    // holds at every instant regardless of how far the mixer trails the script,
    // is that the voice adapter starts the Core-requested messages in Core
    // order without inventing or reordering any. Sampling every smoke frame
    // accumulates that ordered prefix, and the per-sample consistency predicate
    // below must hold on every one of the ~3200 samples, not just the last.
    private void SampleSmokeVoiceProgress()
    {
        Level100MessagePlaybackState playback = _audio.CharacterMessagePlayback;
        int? audibleMessageId = playback.Playing ? playback.ActiveMessageId : null;
        if (audibleMessageId.HasValue &&
            audibleMessageId != _smokeVoiceLastObservedMessageId)
        {
            _smokeVoiceStartedMessageIds.Add(audibleMessageId.Value);
        }
        _smokeVoiceLastObservedMessageId = audibleMessageId;

        bool audibleImpliesIdentified =
            !playback.Playing ||
            (playback.ActiveMessageId.HasValue &&
                playback.ActiveSpeakerId.HasValue &&
                playback.LengthSeconds > 0d &&
                playback.PositionSeconds >= 0d &&
                playback.PositionSeconds <= playback.LengthSeconds);
        bool activeMessageWasRequested =
            !playback.ActiveMessageId.HasValue ||
            _hud.Level100DeliveredMessageIds.Contains(
                playback.ActiveMessageId.Value);
        _smokeVoicePlaybackConsistent &=
            audibleImpliesIdentified &&
            activeMessageWasRequested &&
            !playback.Paused;
    }

    private void SuspendFrontendGameplay()
    {
        if (_level100WorldCreated && _session.IsAuthenticMenuPaused)
        {
            CloseAuthenticPauseForLifecycle();
        }
        _gameplayActive = false;
        _session.ReleaseAllInput();
    }

    private void ReleaseLevel100ForMainMenu()
    {
        SuspendFrontendGameplay();
        DestroyLevel100World();
        // Retail restores MUS_FRONTEND whenever the frontend takes the screen back
        // — CFEPMain::Process (0x00462640) and CFEPGoodies::Process (0x0045d7e0)
        // both stop and re-select it. The exact retail post-level path is not
        // established here; without this the main menu would return silent.
        _audio.StartFrontendMusic();
    }

    private void DestroyLevel100World()
    {
        if (!_level100WorldCreated)
        {
            return;
        }

        _world.Visible = false;
        _hud.Visible = false;
        _pauseView.Visible = false;
        _pauseMenu.Reset();
        _session.SetAuthenticMenuPaused(false);
        _audio.SetGameplayPaused(false);
        if (!_pauseExitAudioCompleted)
        {
            _audio.StopLevel100Audio();
        }
        _pauseExitAudioCompleted = false;
        _world.QueueFree();
        _hud.QueueFree();
        _pauseView.QueueFree();
        _level100WorldCreated = false;
        _session = null!;
    }

    private static InteractiveSession CreateSession() =>
        new(SimulationSeed, Level100StaticWorldAsset.LoadActorDefinitions());

    private static Level100ActorId RequirePlayerAquilaActorId(
        Level100ActorRegistrySnapshot actors)
    {
        Level100ActorId? playerActorId = null;
        foreach (Level100ActorSnapshot actor in actors.Actors)
        {
            if (!StringComparer.Ordinal.Equals(actor.Name, "Player 1") ||
                actor.ThingTypeMask != Level100ReleasedThingTypeMasks.BattleEngine)
            {
                continue;
            }
            if (playerActorId.HasValue)
            {
                throw new InvalidDataException(
                    "Level 100 has multiple Player 1 Battle Engine actors.");
            }
            playerActorId = actor.ActorId;
        }

        return playerActorId ??
            throw new InvalidDataException(
                "Level 100 is missing its Player 1 Battle Engine actor.");
    }

    private RetailFrontendFlow RequireLevel100Frontend()
    {
        if (_frontend is null ||
            _frontend.CurrentScreen != RetailFrontendScreen.Gameplay)
        {
            throw new InvalidOperationException(
                "A Level 100 restart or Main Menu return requires active gameplay.");
        }

        return _frontend;
    }

    private void DriveSmokeFrontend()
    {
        RetailFrontendFlow frontend = _frontend ??
            throw new InvalidOperationException("Smoke requires the normal retail frontend.");

        if (_smokePhase == SmokePhase.ColdFrontend)
        {
            switch (frontend.CurrentScreen)
            {
                case RetailFrontendScreen.ClickToStart:
                    _smokeSawClickToStart = true;
                    _smokeCursorVisibleAtFrontend =
                        _requestedCursorMode == RetailFrontendCursorMode.Visible;
                    frontend.ConfirmForSmoke();
                    return;

                case RetailFrontendScreen.MainMenu:
                    _smokeSawMainMenu = true;
                    _smokeCursorVisibleAtFrontend &=
                        _requestedCursorMode == RetailFrontendCursorMode.Visible;
                    frontend.ConfirmForSmoke();
                    return;

                case RetailFrontendScreen.DevSelect:
                    _smokeSawDevSelect = true;
                    _smokeCursorVisibleAtFrontend &=
                        _requestedCursorMode == RetailFrontendCursorMode.Visible;
                    frontend.ConfirmForSmoke();
                    return;

                case RetailFrontendScreen.LevelSelect:
                    _smokeSawLevelSelect = true;
                    _smokeCursorVisibleAtFrontend &=
                        _requestedCursorMode == RetailFrontendCursorMode.Visible;
                    frontend.ConfirmForSmoke();
                    return;

                // MISSION BRIEFING and SELECT CONFIGURATION sit between level
                // select and loading in the released flow. Smoke traverses them
                // rather than asserting on them: their parity is measured by
                // pixel capture, and duplicating that here would assert a
                // presentation value the simulation does not determine.
                case RetailFrontendScreen.MissionBriefing:
                    _smokeSawMissionBriefing = true;
                    _smokeCursorVisibleAtFrontend &=
                        _requestedCursorMode == RetailFrontendCursorMode.Visible;
                    frontend.ConfirmForSmoke();
                    return;

                case RetailFrontendScreen.SelectConfiguration:
                    _smokeSawSelectConfiguration = true;
                    _smokeCursorVisibleAtFrontend &=
                        _requestedCursorMode == RetailFrontendCursorMode.Visible;
                    frontend.ConfirmForSmoke();
                    return;

                case RetailFrontendScreen.Loading:
                    _smokeSawLoading = true;
                    _smokeCursorHiddenAtLoading =
                        _requestedCursorMode == RetailFrontendCursorMode.Hidden;
                    return;

                default:
                    throw new InvalidOperationException(
                        $"Cold frontend smoke reached unexpected state {frontend.CurrentScreen}.");
            }
        }

        if (_smokePhase == SmokePhase.AwaitingRetryGameplay)
        {
            if (frontend.CurrentScreen != RetailFrontendScreen.Loading)
            {
                throw new InvalidOperationException(
                    $"Retry smoke reached unexpected state {frontend.CurrentScreen}.");
            }

            _smokeCursorHiddenAtLoading &=
                _requestedCursorMode == RetailFrontendCursorMode.Hidden;
        }
    }

    private void FinishSmokeRetryAndReturn()
    {
        _smokeReturnRequested = true;
        LeaveLevel100ForMainMenu();
        _smokeReturnedToMainMenu =
            _frontend!.CurrentScreen == RetailFrontendScreen.MainMenu;
        _smokeWorldReleasedAtMainMenu = !_level100WorldCreated;
        _smokeCursorVisibleAtMainMenu =
            _requestedCursorMode == RetailFrontendCursorMode.Visible;
        _smokePhase = SmokePhase.ReturnedToMainMenu;
        Callable.From(CompleteSmoke).CallDeferred();
    }

    private void ApplyFrontendCursorMode(RetailFrontendCursorMode mode)
    {
        _requestedCursorMode = mode;
        if (_smokeMode || _captureMode)
        {
            return;
        }

        Input.MouseMode = mode switch
        {
            RetailFrontendCursorMode.Visible => Input.MouseModeEnum.Visible,
            RetailFrontendCursorMode.Hidden => Input.MouseModeEnum.Hidden,
            RetailFrontendCursorMode.Captured => Input.MouseModeEnum.Captured,
            _ => throw new ArgumentOutOfRangeException(nameof(mode)),
        };
    }

    private void UpdateGameplayCursorMode()
    {
        ApplyFrontendCursorMode(
            !_windowHasFocus || _session.IsPaused
                ? RetailFrontendCursorMode.Visible
                : RetailFrontendCursorMode.Captured);
    }

    private void ForwardFrontendAudioCue(RetailFrontendAudioCue cue)
    {
        _audio.PlayFrontendCue(cue.ToString());
        RaiseFrontendAudioCueRequested(cue);
    }

    private void RaiseFrontendAudioCueRequested(RetailFrontendAudioCue cue)
    {
        FrontendAudioCueRequested?.Invoke(cue);
    }

    private static void ApplySyntheticInput(InteractiveInput input)
    {
        SetSyntheticAction(MoveLeftAction, input.MoveX < 0);
        SetSyntheticAction(MoveRightAction, input.MoveX > 0);
        SetSyntheticAction(MoveBackwardAction, input.MoveZ < 0);
        SetSyntheticAction(MoveForwardAction, input.MoveZ > 0);
        SetSyntheticAction(LookLeftAction, input.LookX < 0);
        SetSyntheticAction(LookRightAction, input.LookX > 0);
        SetSyntheticAction(LookUpAction, input.LookY < 0);
        SetSyntheticAction(LookDownAction, input.LookY > 0);
        SetSyntheticAction(FireAction, input.FireHeld);
        SetSyntheticAction(ToggleModeAction, input.ToggleModeHeld);
        SetSyntheticAction(ResetAction, input.ResetHeld);
    }

    private static void SetSyntheticAction(StringName action, bool pressed)
    {
        if (pressed)
        {
            Input.ActionPress(action);
        }
        else
        {
            Input.ActionRelease(action);
        }
    }

    private static void ReleaseSyntheticInput()
    {
        foreach (StringName action in new[]
                 {
                     MoveForwardAction,
                     MoveBackwardAction,
                     MoveLeftAction,
                     MoveRightAction,
                     LookLeftAction,
                     LookRightAction,
                     LookUpAction,
                     LookDownAction,
                     FireAction,
                     ToggleModeAction,
                     LandingJetsAction,
                     ResetAction,
                 })
        {
            Input.ActionRelease(action);
        }
    }

    private void ConsumeLevel100MissionEvents(IReadOnlyList<Level100MissionEvent> events)
    {
        _hud.ConsumeMissionEvents(events);
        foreach (Level100MissionEvent missionEvent in events)
        {
            if (missionEvent is Level100MessageRequested message)
            {
                if (_smokeMode && _smokeReport is null)
                {
                    // Recorded on the audio-forwarding path specifically, so it
                    // cross-checks the HUD delivery path rather than restating
                    // it. Both are Core-event ordered and tick-deterministic.
                    _smokeAudioQueuedSpeakerIds.Add(message.SpeakerId);
                    _smokeAudioQueuedMessageIds.Add(message.MessageId);
                }
                _audio.QueueCharacterMessage(message.SpeakerId, message.MessageId);
            }
        }
    }

    private void ConsumeFrameEvents(FrameAdvanceResult result)
    {
        _audio.UpdateAquilaPose(result.CurrentSnapshot.Level100Actors);
        ConsumeLevel100MissionEvents(result.Level100MissionEvents);
        _audio.ConsumeAquilaFlightEvents(result.AquilaFlightEvents);
        _audio.ConsumeLevel100WeaponFireEvents(result.Level100WeaponFireEvents);
        _audio.SetAquilaFlightPitch(
            result.CurrentSnapshot.JetThrusterPermille / 1_000f);
        _world.ConsumeLevel100DestructionEvents(
            result.Level100DestructionEvents,
            result.CurrentSnapshot.Tick);
        _audio.ConsumeLevel100DestructionEvents(
            result.Level100DestructionEvents);
    }

    private void RunFocusLossHandlerSmokeProbe()
    {
        var heldInput = new InteractiveInput(1, 1, true, true, true);
        _session.ObserveInput(heldInput);
        _session.QueueMovementPulse(-1, -1);
        _session.QueueLookPulse(-1, -1);
        _session.QueuePointerMotionMilliPixels(-10_000, 10_000);
        _session.QueueFirePulse();

        _Notification((int)NotificationWMWindowFocusOut);
        _session.ObserveInput(heldInput);
        _session.QueueMovementPulse(1, 0);
        _session.QueueLookPulse(1, 0);
        _session.QueuePointerMotionMilliPixels(10_000, -10_000);
        _session.QueueFirePulse();
        _session.QueueToggleMode();
        _session.QueueReset();
        _focusLossHandlerInputCleared =
            _session.InputSuspendedUntilReleased &&
            !_session.HasHeldOrPendingInput;

        ReleaseSyntheticInput();
        _session.ObserveInput(InteractiveInput.Idle);
        _session.QueueFirePulse();
        _focusLossHandlerNeutralRearmed =
            !_session.InputSuspendedUntilReleased &&
            _session.HasHeldOrPendingInput;
        _session.ReleaseAllInput();
        _Notification((int)NotificationWMWindowFocusIn);
    }

    /// <summary>
    /// Runs retail's cold-start media — the Lost Toys logo movie, the opening
    /// montage and the splash card — ahead of the interactive frontend.
    ///
    /// <para><b>When it is suppressed, and why that is parity rather than an
    /// escape hatch.</b></para>
    /// Capture and smoke runs suppress it, exactly as retail's <c>-skipfmv</c>
    /// does. That is not a convenience: EVERY retail reference frame this
    /// project compares against was captured with <c>-skipfmv</c> on, so a
    /// capture run that played the intro would be measuring the reconstruction
    /// against a reference that structurally cannot contain it, and the 13
    /// pinned startup shots — whose first shot is click-to-start at engine
    /// frame 12 — would all land on the wrong screen.
    ///
    /// The risk this creates is real and was named by an independent adversarial pass:
    /// if the only automated visual path skips the intro, the intro can rot
    /// unobserved, which is precisely how <c>_feBackFrames</c> came to be loaded
    /// and never drawn. The mitigation is that the deterministic part of this
    /// lane — the schedule and the media index — carries no Godot types and is
    /// unit tested directly in <c>OnslaughtRebuild.Client.Tests</c>, and
    /// <c>--intro</c> forces the sequence on for a human or a future rig.
    /// </summary>
    private void StartRetailStartupMedia()
    {
        bool suppressed = !_forceStartupMedia &&
            (_skipStartupMedia || _smokeMode || _captureArgumentsPresent);
        if (suppressed)
        {
            return;
        }

        var sequence = new RetailStartupSequence { Name = "RetailStartupSequence" };
        sequence.Initialize(
            RetailStartupSequence.ResolveMediaRoot(OS.GetCmdlineUserArgs()),
            // A capture run is deterministic by contract, so the sequence has to
            // advance on the tick rather than on a delta the host could jitter.
            _captureArgumentsPresent
                ? RetailStartupClockMode.FixedTick
                : RetailStartupClockMode.Wall);

        if (sequence.ScheduledSeconds <= 0d)
        {
            // Nothing was decoded. Do not hold a black screen, and above all do
            // not draw a stand-in for the missing footage.
            GD.PushWarning(
                "Startup media is absent, so splash and intro FMV do not play. " +
                (sequence.MediaUnavailableReason ?? "No cue had decoded media."));
            sequence.QueueFree();
            return;
        }

        // The frontend must not tick or draw underneath the sequence: its
        // click-to-start pulse timer starts when the page is first shown, and
        // letting it run for 90 s would put the pulse at an arbitrary phase the
        // moment the player finally sees the page.
        RetailFrontendFlow frontend = _frontend ??
            throw new InvalidOperationException(
                "The startup media sequence needs the frontend to already exist.");
        frontend.SuspendForStartupMedia();
        sequence.Completed += frontend.ResumeAfterStartupMedia;

        _startupSequence = sequence;
        AddChild(sequence);
    }

    private void ParseUserArguments()
    {
        foreach (string argument in OS.GetCmdlineUserArgs())
        {
            if (argument == "--smoke")
            {
                _smokeMode = true;
            }
            else if (argument.StartsWith("--report=", StringComparison.Ordinal))
            {
                _smokeReportPath = argument["--report=".Length..];
            }
            else if (argument.StartsWith("--capture-dir=", StringComparison.Ordinal) ||
                     argument.StartsWith("--capture-plan=", StringComparison.Ordinal) ||
                     argument.StartsWith("--capture-size=", StringComparison.Ordinal) ||
                     argument.StartsWith("--capture-offsets-ms=", StringComparison.Ordinal))
            {
                // Consumed by FrontendCaptureRig.TryCreate during _Ready.
                _captureArgumentsPresent = true;
            }
            else if (argument == "--skipfmv")
            {
                // Retail's own flag, reproduced by name: CLIParams.cpp:272 sets
                // mSkipFMV, and CGame::GetIntroFMV returns -1 when it is set.
                _skipStartupMedia = true;
            }
            else if (argument == "--intro")
            {
                _forceStartupMedia = true;
            }
            else if (argument.StartsWith("--startup-media=", StringComparison.Ordinal))
            {
                // Consumed by RetailStartupSequence.ResolveMediaRoot.
            }
            else
            {
                throw new ArgumentException($"Unknown First Flight argument '{argument}'.");
            }
        }

        if (!_smokeMode)
        {
            return;
        }

        if (string.IsNullOrWhiteSpace(_smokeReportPath) ||
            !Path.IsPathFullyQualified(_smokeReportPath))
        {
            throw new ArgumentException("Smoke mode requires an absolute --report path.");
        }
    }

    private SmokeReport CaptureSmokeReport()
    {
        InteractiveSessionMetrics metrics = _session.Metrics;
        Godot.Collections.Dictionary versionInfo = Engine.GetVersionInfo();
        string engineVersion = versionInfo["string"].AsString();
        return new SmokeReport
        {
            SchemaVersion = "onslaught-first-flight-smoke.v16",
                EngineVersion = engineVersion,
                ExitReason = "smoke-complete",
                Tick = _session.CurrentSnapshot.Tick,
                StateHash = StateHasher.ComputeHex(_session.CurrentSnapshot),
                TargetsDestroyed = _session.CurrentSnapshot.TargetsDestroyed,
                Mode = _session.CurrentSnapshot.Mode.ToString(),
                Level100OpeningTicksRemaining = _session.CurrentSnapshot.Level100OpeningTicksRemaining,
                Level100MissionTick = _session.CurrentSnapshot.Level100Mission.Tick,
                Level100MissionOutcome =
                    _session.CurrentSnapshot.Level100Mission.Outcome.ToString(),
                Level100TerminalState =
                    _session.CurrentSnapshot.Level100Mission.TerminalState.ToString(),
                // Wall-clock, NOT tick-derived. AudioStreamPlayer.Playing and
                // its Finished signal advance on the audio mixer in real time
                // while --fixed-fps drives the simulation as fast as the host
                // allows, so which queued message is audible at a fixed tick is
                // a race. Measured on one host at tick 3228 over six runs with
                // an identical stateHash: -257967449 three times, 82987417
                // three times. Callers must bound this against
                // Level100DeliveredMessageIds, never pin it.
                Level100PlayingMessageId =
                    _audio.CharacterMessagePlayback.ActiveMessageId,
                Level100DeliveredMessageIds = _hud.Level100DeliveredMessageIds,
                Level100AudioQueuedMessageIds = _smokeAudioQueuedMessageIds,
                Level100AudioQueuedSpeakerIds = _smokeAudioQueuedSpeakerIds,
                // Accumulated over every smoke frame, not sampled at this tick:
                // an ordered prefix of Level100DeliveredMessageIds whose LENGTH
                // is host-dependent but whose CONTENT is not.
                Level100VoiceStartedMessageIds = _smokeVoiceStartedMessageIds,
                Level100VoicePlaybackConsistent = _smokeVoicePlaybackConsistent,
                Level100PlayerControlEnabled = _session.CurrentSnapshot.Level100PlayerControlEnabled,
                Level100FlightEnabled = _session.CurrentSnapshot.Level100FlightEnabled,
                Level100PulseCannonEnabled =
                    _session.CurrentSnapshot.Level100PulseCannonEnabled,
                Level100VulcanCannonEnabled =
                    _session.CurrentSnapshot.Level100VulcanCannonEnabled,
                Level100FiringRangeTargetsActive =
                    _session.CurrentSnapshot.Level100FiringRangeTargetsActive,
                Level100CurrentWeaponHighlighted =
                    _session.CurrentSnapshot.Level100CurrentWeaponHighlighted,
                // Mixer state at this tick. Reported, never pinned: false is a
                // legal observation whenever the report lands in the 6/30s
                // RetailCharacterMessageHandoffSeconds gap between messages.
                TutorialVoicePlaying = _audio.TutorialVoicePlaying,
                TotalSteps = metrics.TotalSteps,
                ToggleEdgesConsumed = metrics.ToggleEdgesConsumed,
                ResetEdgesConsumed = metrics.ResetEdgesConsumed,
                ResetGeneration = metrics.ResetGeneration,
                FireHeldTicksSampled = metrics.FireHeldTicksSampled,
                FirePulseEdgesConsumed = metrics.FirePulseEdgesConsumed,
                MovementPulseEdgesConsumed = metrics.MovementPulseEdgesConsumed,
                CappedFrameCount = metrics.CappedFrameCount,
                DroppedElapsedTicks = metrics.DroppedElapsedTicks,
                PlayerVisualPresent = _world.PlayerVisualPresent,
                RetailAquilaMeshesPresent = _world.RetailAquilaMeshesPresent,
                RetailAquilaSurfaceCount = _world.RetailAquilaSurfaceCount,
                RetailAquilaPartCount = _world.RetailAquilaPartCount,
                RetailAquilaAnimatedPartCount = _world.RetailAquilaAnimatedPartCount,
                RetailAquilaStandingClearance = _world.RetailAquilaStandingClearance,
                RetailCockpitSurfaceCount = _world.RetailCockpitSurfaceCount,
                Level100PlayerStartRelativeHeight = _world.Level100PlayerStartRelativeHeight,
                RetailLevel100StaticObjectCount = _world.RetailLevel100StaticObjectCount,
                RetailLevel100StaticObjectSurfaceCount = _world.RetailLevel100StaticObjectSurfaceCount,
                RetailLevel100PineCount = _world.RetailLevel100PineCount,
                RetailLevel100WaterPresent = _world.RetailLevel100WaterPresent,
                RetailLevel100WaterGridVertexCount =
                    _world.RetailLevel100WaterGridVertexCount,
                RetailLevel100WaterGridTriangleCount =
                    _world.RetailLevel100WaterGridTriangleCount,
                RetailLevel100ShorelineTriangleCount =
                    _world.RetailLevel100ShorelineTriangleCount,
                RetailLevel100TargetSurfaceCount = _world.RetailLevel100TargetSurfaceCount,
                Level100ObjectiveMarkerCount = _hud.Level100ObjectiveMarkerCount,
                Level100DeliveredMessageCount = _hud.Level100DeliveredMessageCount,
                Level100DeliveredHelpCount = _hud.Level100DeliveredHelpCount,
                // Both mixer-derived like TutorialVoicePlaying, and additionally
                // false whenever the mixer trails the script far enough that the
                // audible message is no longer the HUD's active delivery.
                // Reported, never pinned; bounded by implication in the gate.
                Level100MessagePlaybackAvailable = _hud.Level100MessagePlaybackAvailable,
                Level100MessagePlaying = _hud.Level100MessagePlaying,
                RetailLevel100TerrainVertexCount = _world.RetailLevel100TerrainVertexCount,
                RetailLevel100TerrainTriangleCount = _world.RetailLevel100TerrainTriangleCount,
                RetailLevel100SkySurfaceCount = _world.RetailLevel100SkySurfaceCount,
                TargetVisualCount = _world.TargetVisualCount,
                OpeningPanActive = _world.OpeningPanActive,
                HudVisible = _world.ShowHud,
                HudReady = _hud.IsReadyForSmoke,
                FocusLossHandlerInputCleared = _focusLossHandlerInputCleared,
                FocusLossHandlerNeutralRearmed = _focusLossHandlerNeutralRearmed,
            };
    }

    private void CompleteSmoke()
    {
        try
        {
            SmokeReport report = _smokeReport ??
                throw new InvalidOperationException("Smoke gameplay evidence was not captured.");
            report.ColdClickToStart = _smokeSawClickToStart;
            report.ColdMainMenu = _smokeSawMainMenu;
            report.ColdDevSelect = _smokeSawDevSelect;
            report.ColdLevelSelect = _smokeSawLevelSelect;
            report.ColdMissionBriefing = _smokeSawMissionBriefing;
            report.ColdSelectConfiguration = _smokeSawSelectConfiguration;
            report.ColdLoading = _smokeSawLoading;
            report.ColdGameplay = _smokeSawGameplay;
            report.CursorPolicyVisibleAtFrontend = _smokeCursorVisibleAtFrontend;
            report.CursorPolicyHiddenAtLoading = _smokeCursorHiddenAtLoading;
            report.GameplayCursorPolicy = _smokeGameplayCursorPolicy;
            report.CursorPolicyAppliedAtGameplay = _smokeCursorPolicyAppliedAtGameplay;
            report.WindowFocusedAtGameplay = _smokeWindowFocusedAtGameplay;
            report.FocusLossCursorPolicyVisible = _smokeCursorReleasedOnFocusLoss;
            report.FocusGainCursorPolicyCaptured = _smokeCursorRecapturedOnFocusGain;
            report.RetryRequested = _smokeRetryRequested;
            report.RetryGameplayActivated = _smokeRetryGameplayActivated;
            report.RetrySessionFresh = _smokeRetrySessionFresh;
            report.ReturnToMainMenuRequested = _smokeReturnRequested;
            report.ReturnedToMainMenu = _smokeReturnedToMainMenu;
            report.WorldReleasedAtMainMenu = _smokeWorldReleasedAtMainMenu;
            report.MainMenuCursorPolicyVisible = _smokeCursorVisibleAtMainMenu;
            report.FinalFrontendScreen = _frontend?.CurrentScreen.ToString() ?? string.Empty;

            string json = JsonSerializer.Serialize(report, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = true,
            });
            WriteNewFileDurably(
                _smokeReportPath!,
                new UTF8Encoding(false).GetBytes(json + System.Environment.NewLine));
            GetTree().Quit(0);
        }
        catch (Exception exception)
        {
            GD.PushError($"First Flight smoke failed: {exception.Message}");
            GetTree().Quit(4);
        }
    }

    private static void WriteNewFileDurably(string path, byte[] content)
    {
        using FileStream stream = new(
            path,
            System.IO.FileMode.CreateNew,
            System.IO.FileAccess.Write,
            System.IO.FileShare.None);
        stream.Write(content);
        stream.Flush(flushToDisk: true);
    }

    private sealed record SmokeReport
    {
        public required string SchemaVersion { get; init; }
        public required string EngineVersion { get; init; }
        public required string ExitReason { get; init; }
        public required int Tick { get; init; }
        public required string StateHash { get; init; }
        public required int TargetsDestroyed { get; init; }
        public required string Mode { get; init; }
        public required int Level100OpeningTicksRemaining { get; init; }
        public required int Level100MissionTick { get; init; }
        public required string Level100MissionOutcome { get; init; }
        public required string Level100TerminalState { get; init; }
        public int? Level100PlayingMessageId { get; init; }
        public required IReadOnlyList<int> Level100DeliveredMessageIds { get; init; }
        public required IReadOnlyList<int> Level100AudioQueuedMessageIds { get; init; }
        public required IReadOnlyList<int> Level100AudioQueuedSpeakerIds { get; init; }
        public required IReadOnlyList<int> Level100VoiceStartedMessageIds { get; init; }
        public required bool Level100VoicePlaybackConsistent { get; init; }
        public required bool Level100PlayerControlEnabled { get; init; }
        public required bool Level100FlightEnabled { get; init; }
        public required bool Level100PulseCannonEnabled { get; init; }
        public required bool Level100VulcanCannonEnabled { get; init; }
        public required bool Level100FiringRangeTargetsActive { get; init; }
        public required bool Level100CurrentWeaponHighlighted { get; init; }
        public required bool TutorialVoicePlaying { get; init; }
        public required long TotalSteps { get; init; }
        public required long ToggleEdgesConsumed { get; init; }
        public required long ResetEdgesConsumed { get; init; }
        public required long ResetGeneration { get; init; }
        public required long FireHeldTicksSampled { get; init; }
        public required long FirePulseEdgesConsumed { get; init; }
        public required long MovementPulseEdgesConsumed { get; init; }
        public required long CappedFrameCount { get; init; }
        public required long DroppedElapsedTicks { get; init; }
        public required bool PlayerVisualPresent { get; init; }
        public required bool RetailAquilaMeshesPresent { get; init; }
        public required int RetailAquilaSurfaceCount { get; init; }
        public required int RetailAquilaPartCount { get; init; }
        public required int RetailAquilaAnimatedPartCount { get; init; }
        public required float RetailAquilaStandingClearance { get; init; }
        public required int RetailCockpitSurfaceCount { get; init; }
        public required float Level100PlayerStartRelativeHeight { get; init; }
        public required int RetailLevel100StaticObjectCount { get; init; }
        public required int RetailLevel100StaticObjectSurfaceCount { get; init; }
        public required int RetailLevel100PineCount { get; init; }
        public required bool RetailLevel100WaterPresent { get; init; }
        public required int RetailLevel100WaterGridVertexCount { get; init; }
        public required int RetailLevel100WaterGridTriangleCount { get; init; }
        public required int RetailLevel100ShorelineTriangleCount { get; init; }
        public required int RetailLevel100TargetSurfaceCount { get; init; }
        public required int Level100ObjectiveMarkerCount { get; init; }
        public required int Level100DeliveredMessageCount { get; init; }
        public required int Level100DeliveredHelpCount { get; init; }
        public required bool Level100MessagePlaybackAvailable { get; init; }
        public required bool Level100MessagePlaying { get; init; }
        public required int RetailLevel100TerrainVertexCount { get; init; }
        public required int RetailLevel100TerrainTriangleCount { get; init; }
        public required int RetailLevel100SkySurfaceCount { get; init; }
        public required int TargetVisualCount { get; init; }
        public required bool OpeningPanActive { get; init; }
        public required bool HudVisible { get; init; }
        public required bool HudReady { get; init; }
        public required bool FocusLossHandlerInputCleared { get; init; }
        public required bool FocusLossHandlerNeutralRearmed { get; init; }
        public bool ColdClickToStart { get; set; }
        public bool ColdMainMenu { get; set; }
        public bool ColdDevSelect { get; set; }

        public bool ColdLevelSelect { get; set; }
        public bool ColdMissionBriefing { get; set; }
        public bool ColdSelectConfiguration { get; set; }
        public bool ColdLoading { get; set; }
        public bool ColdGameplay { get; set; }
        public bool CursorPolicyVisibleAtFrontend { get; set; }
        public bool CursorPolicyHiddenAtLoading { get; set; }
        public string[] GameplayCursorPolicy { get; set; } = [];
        public bool CursorPolicyAppliedAtGameplay { get; set; }
        // Host desktop state. Reported so a reader can see it; never asserted.
        public bool WindowFocusedAtGameplay { get; set; }
        public bool FocusLossCursorPolicyVisible { get; set; }
        public bool FocusGainCursorPolicyCaptured { get; set; }
        public bool RetryRequested { get; set; }
        public bool RetryGameplayActivated { get; set; }
        public bool RetrySessionFresh { get; set; }
        public bool ReturnToMainMenuRequested { get; set; }
        public bool ReturnedToMainMenu { get; set; }
        public bool WorldReleasedAtMainMenu { get; set; }
        public bool MainMenuCursorPolicyVisible { get; set; }
        public string FinalFrontendScreen { get; set; } = string.Empty;
    }

    private enum SmokePhase
    {
        ColdFrontend,
        InitialGameplay,
        AwaitingRetryGameplay,
        RetryGameplay,
        ReturnedToMainMenu,
    }
}
