// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
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
    private static readonly StringName ResetAction = "first_flight_reset";
    private static readonly StringName ExitAction = "first_flight_exit";

    private InteractiveSession _session = null!;
    private FirstFlightWorldView _world = null!;
    private FirstFlightHud _hud = null!;
    private AudioStreamPlayer _tutorialVoice = null!;
    private int? _playingTutorialMessageId;
    private bool _smokeMode;
    private bool _smokeCompleting;
    private bool _focusLossHandlerInputCleared;
    private bool _focusLossHandlerNeutralRearmed;
    private string? _smokeReportPath;
    private string? _smokeScreenshotPath;

    public override void _Ready()
    {
        try
        {
            ConfigureInputMap();
            ParseUserArguments();
            _session = new InteractiveSession(
                SimulationSeed,
                Level100StaticWorldAsset.LoadActorDefinitions());

            Window window = GetWindow();
            window.Title = "Onslaught Rebuild - Level 100 Opening Slice";
            window.MinSize = new Vector2I(1200, 675);

            _world = new FirstFlightWorldView();
            AddChild(_world);
            _world.Initialize(_session.CurrentSnapshot);

            _hud = new FirstFlightHud();
            AddChild(_hud);
            _hud.Initialize();
            _hud.UpdateFromSnapshot(_session.CurrentSnapshot);
            _hud.Visible = _world.ShowHud;

            _tutorialVoice = new AudioStreamPlayer { Name = "RetailLevel100TutorialVoice" };
            AddChild(_tutorialVoice);
            _tutorialVoice.Finished += OnTutorialVoiceFinished;
            ConsumeLevel100MissionEvents(_session.CurrentSnapshot.Level100MissionEvents);
            _hud.UpdateFromSnapshot(_session.CurrentSnapshot);

            if (!_smokeMode)
            {
                Input.MouseMode = Input.MouseModeEnum.Captured;
            }
        }
        catch (Exception exception)
        {
            SetProcess(false);
            GD.PushError($"Level 100 opening slice failed to initialize: {exception.Message}");
            GetTree().Quit(4);
        }
    }

    public override void _Process(double delta)
    {
        if (!_smokeMode && Input.IsActionJustPressed(ExitAction))
        {
            GetTree().Quit(0);
            return;
        }

        if (_smokeCompleting)
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
        ConsumeLevel100MissionEvents(result.Level100MissionEvents);
        _world.Render(
            result.PreviousSnapshot,
            result.CurrentSnapshot,
            (float)result.InterpolationAlpha,
            (float)delta);
        _hud.UpdateFromSnapshot(result.CurrentSnapshot);
        _hud.Visible = _world.ShowHud;

        if (_smokeMode && result.CurrentSnapshot.Tick >= FirstFlightSmokeScenario.DurationTicks)
        {
            _smokeCompleting = true;
            RunFocusLossHandlerSmokeProbe();
            Callable.From(CompleteSmoke).CallDeferred();
        }
    }

    public override void _Input(InputEvent inputEvent)
    {
        if (_smokeMode)
        {
            return;
        }

        if (inputEvent is InputEventMouseMotion mouseMotion)
        {
            if (_session.CurrentSnapshot.Mode == VehicleMode.Walker &&
                _session.CurrentSnapshot.Transition == VehicleTransition.None)
            {
                int deltaX = ToMilliPixels(mouseMotion.ScreenRelative.X);
                int deltaY = ToMilliPixels(mouseMotion.ScreenRelative.Y);
                if (deltaX != 0 || deltaY != 0)
                {
                    _session.QueuePointerMotionMilliPixels(deltaX, deltaY);
                }
            }
            else
            {
                sbyte lookX = QuantizeAxis(mouseMotion.ScreenRelative.X);
                sbyte lookY = QuantizeAxis(mouseMotion.ScreenRelative.Y);
                if (lookX != 0 || lookY != 0)
                {
                    // Jet input remains on its existing provisional digital path.
                    _session.QueueLookPulse(lookX, lookY);
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
        bool exitPressed = inputEvent.IsActionPressed(ExitAction) ||
            IsKey(keyEvent, Key.Escape);

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

        if (exitPressed)
        {
            GetTree().Quit(0);
        }
    }

    public override void _Notification(int what)
    {
        if (what == NotificationWMWindowFocusOut && (!_smokeMode || _smokeCompleting))
        {
            _session.SuspendInputUntilReleased();
            if (!_smokeMode)
            {
                Input.MouseMode = Input.MouseModeEnum.Visible;
            }
        }
        else if (what == NotificationWMWindowFocusIn && !_smokeMode)
        {
            Input.MouseMode = Input.MouseModeEnum.Captured;
        }
    }

    public override void _ExitTree()
    {
        if (!_smokeMode)
        {
            Input.MouseMode = Input.MouseModeEnum.Visible;
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
        EnsureKeyAction(ResetAction, Key.R);
        EnsureKeyAction(ExitAction, Key.Escape);
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
            lookY);
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
                     ResetAction,
                 })
        {
            Input.ActionRelease(action);
        }
    }

    private void ConsumeLevel100MissionEvents(IReadOnlyList<Level100MissionEvent> events)
    {
        foreach (Level100MessageRequested message in events.OfType<Level100MessageRequested>())
        {
            _hud.ShowTutorialMessage(message.SpeakerId, message.MessageId);
            UpdateTutorialVoice(message.MessageId);
        }
    }

    private void UpdateTutorialVoice(int messageId)
    {
        _playingTutorialMessageId = messageId;
        _tutorialVoice.Stop();
        string? resourcePath = messageId switch
        {
            292562 =>
                "res://Assets/Level100/TutorialAudio/hud_01.ogg",
            293386 =>
                "res://Assets/Level100/TutorialAudio/hud_02.ogg",
            296682 =>
                "res://Assets/Level100/TutorialAudio/hud_06.ogg",
            -1575499396 =>
                "res://Assets/Level100/TutorialAudio/tutorial_message_log.ogg",
            -257967449 =>
                "res://Assets/Level100/TutorialAudio/tutorial_technician_01.ogg",
            82987417 =>
                "res://Assets/Level100/TutorialAudio/tutorial_13_mod.ogg",
            4422830 =>
                "res://Assets/Level100/TutorialAudio/tutorial_01.ogg",
            175347826 =>
                "res://Assets/Level100/TutorialAudio/tutorial_scanner.ogg",
            4458134 =>
                "res://Assets/Level100/TutorialAudio/tutorial_02.ogg",
            4493438 =>
                "res://Assets/Level100/TutorialAudio/tutorial_03.ogg",
            295858 =>
                "res://Assets/Level100/TutorialAudio/hud_05.ogg",
            1339691000 =>
                "res://Assets/Level100/TutorialAudio/tutorial_pulse_cannon.ogg",
            669198996 =>
                "res://Assets/Level100/TutorialAudio/tutorial_open_fire.ogg",
            -1715818922 =>
                "res://Assets/Level100/TutorialAudio/tutorial_pulse_cannon_2.ogg",
            -1616775312 =>
                "res://Assets/Level100/TutorialAudio/tutorial_vulcan_cannon.ogg",
            -1860407443 =>
                "res://Assets/Level100/TutorialAudio/tutorial_open_fire_2.ogg",
            864965454 =>
                "res://Assets/Level100/TutorialAudio/tutorial_vulcan_cannon_2.ogg",
            _ => null,
        };
        if (resourcePath is null)
        {
            _tutorialVoice.Stream = null;
            return;
        }

        byte[] source = Godot.FileAccess.GetFileAsBytes(resourcePath);
        _tutorialVoice.Stream = source.Length == 0
            ? null
            : AudioStreamOggVorbis.LoadFromBuffer(source);
        if (_tutorialVoice.Stream is null)
        {
            throw new InvalidDataException($"Released tutorial voice is missing or invalid: {resourcePath}");
        }
        _tutorialVoice.Play();
    }

    private void OnTutorialVoiceFinished()
    {
        _playingTutorialMessageId = null;
        _hud.ClearTutorialMessage();
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
            else if (argument.StartsWith("--screenshot=", StringComparison.Ordinal))
            {
                _smokeScreenshotPath = argument["--screenshot=".Length..];
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
            string.IsNullOrWhiteSpace(_smokeScreenshotPath) ||
            !Path.IsPathFullyQualified(_smokeReportPath) ||
            !Path.IsPathFullyQualified(_smokeScreenshotPath))
        {
            throw new ArgumentException("Smoke mode requires absolute --report and --screenshot paths.");
        }
    }

    private async void CompleteSmoke()
    {
        try
        {
            await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);

            Image image = GetViewport().GetTexture().GetImage();
            byte[] screenshotBytes = image.SavePngToBuffer();
            if (screenshotBytes.Length == 0)
            {
                throw new IOException("Godot returned an empty smoke screenshot.");
            }
            WriteNewFileDurably(_smokeScreenshotPath!, screenshotBytes);

            string screenshotHash = Convert.ToHexString(SHA256.HashData(screenshotBytes)).ToLowerInvariant();
            InteractiveSessionMetrics metrics = _session.Metrics;
            Godot.Collections.Dictionary versionInfo = Engine.GetVersionInfo();
            string engineVersion = versionInfo["string"].AsString();
            var report = new SmokeReport
            {
                SchemaVersion = "onslaught-first-flight-smoke.v10",
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
                Level100PlayingMessageId = _playingTutorialMessageId,
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
                TutorialVoicePlaying = _tutorialVoice.Playing,
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
                RetailLevel100TerrainVertexCount = _world.RetailLevel100TerrainVertexCount,
                RetailLevel100TerrainTriangleCount = _world.RetailLevel100TerrainTriangleCount,
                RetailLevel100SkySurfaceCount = _world.RetailLevel100SkySurfaceCount,
                TargetVisualCount = _world.TargetVisualCount,
                OpeningPanActive = _world.OpeningPanActive,
                HudVisible = _world.ShowHud,
                HudReady = _hud.IsReadyForSmoke,
                FocusLossHandlerInputCleared = _focusLossHandlerInputCleared,
                FocusLossHandlerNeutralRearmed = _focusLossHandlerNeutralRearmed,
                ScreenshotFileName = Path.GetFileName(_smokeScreenshotPath) ?? string.Empty,
                ScreenshotWidth = image.GetWidth(),
                ScreenshotHeight = image.GetHeight(),
                ScreenshotSha256 = screenshotHash,
            };
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
        public required int RetailLevel100TerrainVertexCount { get; init; }
        public required int RetailLevel100TerrainTriangleCount { get; init; }
        public required int RetailLevel100SkySurfaceCount { get; init; }
        public required int TargetVisualCount { get; init; }
        public required bool OpeningPanActive { get; init; }
        public required bool HudVisible { get; init; }
        public required bool HudReady { get; init; }
        public required bool FocusLossHandlerInputCleared { get; init; }
        public required bool FocusLossHandlerNeutralRearmed { get; init; }
        public required string ScreenshotFileName { get; init; }
        public required int ScreenshotWidth { get; init; }
        public required int ScreenshotHeight { get; init; }
        public required string ScreenshotSha256 { get; init; }
    }
}
