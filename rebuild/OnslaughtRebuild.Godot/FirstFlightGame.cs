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
    private static readonly StringName FireAction = "first_flight_fire";
    private static readonly StringName ToggleModeAction = "first_flight_toggle_mode";
    private static readonly StringName ResetAction = "first_flight_reset";
    private static readonly StringName ExitAction = "first_flight_exit";

    private readonly InteractiveSession _session = new(SimulationSeed);
    private FirstFlightWorldView _world = null!;
    private FirstFlightHud _hud = null!;
    private bool _smokeMode;
    private bool _smokeCompleting;
    private bool _focusLossHandlerInputCleared;
    private bool _focusLossHandlerNeutralRearmed;
    private string? _smokeReportPath;
    private string? _smokeScreenshotPath;
    private string? _localAssetsRoot;

    public override void _Ready()
    {
        ConfigureInputMap();
        ParseUserArguments();

        Window window = GetWindow();
        window.Title = "Onslaught Rebuild - First Flight";
        window.MinSize = new Vector2I(1200, 675);

        LocalPresentationConfig? localPresentation =
            LocalPresentationConfig.TryResolve(_localAssetsRoot, _smokeMode, out string? localPresentationError);
        if (!_smokeMode && _localAssetsRoot is not null && localPresentation is null)
        {
            GD.PushWarning($"First Flight local presentation rejected: {localPresentationError}");
        }

        _world = new FirstFlightWorldView();
        AddChild(_world);
        _world.Initialize(_session.CurrentSnapshot, localPresentation);

        _hud = new FirstFlightHud();
        AddChild(_hud);
        _hud.Initialize(_world.LocalPresentationStatus);
        _hud.UpdateFromSnapshot(_session.CurrentSnapshot);
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
        if (input != InteractiveInput.Idle)
        {
            _hud.MarkInputActivity();
        }

        long elapsedTicks = _smokeMode
            ? SmokeFrameElapsedTicks
            : Math.Max(0L, (long)Math.Round(delta * TimeSpan.TicksPerSecond, MidpointRounding.AwayFromZero));
        FrameAdvanceResult result = _session.AdvanceFrameTicks(elapsedTicks);
        _world.Render(
            result.PreviousSnapshot,
            result.CurrentSnapshot,
            (float)result.InterpolationAlpha,
            (float)delta);
        _hud.UpdateFromSnapshot(result.CurrentSnapshot);

        if (_smokeMode && result.CurrentSnapshot.Tick >= FirstFlightSmokeScenario.DurationTicks)
        {
            _smokeCompleting = true;
            RunFocusLossHandlerSmokeProbe();
            Callable.From(CompleteSmoke).CallDeferred();
        }
    }

    public override void _Input(InputEvent inputEvent)
    {
        if (_smokeMode || inputEvent is not InputEventKey keyEvent || !keyEvent.Pressed || keyEvent.Echo)
        {
            return;
        }

        bool togglePressed = inputEvent.IsActionPressed(ToggleModeAction) ||
            keyEvent.PhysicalKeycode == Key.Q ||
            keyEvent.Keycode == Key.Q;
        bool resetPressed = inputEvent.IsActionPressed(ResetAction) ||
            keyEvent.PhysicalKeycode == Key.R ||
            keyEvent.Keycode == Key.R;
        bool exitPressed = inputEvent.IsActionPressed(ExitAction) ||
            keyEvent.PhysicalKeycode == Key.Escape ||
            keyEvent.Keycode == Key.Escape;

        if (keyEvent.PhysicalKeycode == Key.W || keyEvent.Keycode == Key.W)
        {
            _session.QueueMovementPulse(0, 1);
        }
        if (keyEvent.PhysicalKeycode == Key.S || keyEvent.Keycode == Key.S)
        {
            _session.QueueMovementPulse(0, -1);
        }
        if (keyEvent.PhysicalKeycode == Key.A || keyEvent.Keycode == Key.A)
        {
            _session.QueueMovementPulse(-1, 0);
        }
        if (keyEvent.PhysicalKeycode == Key.D || keyEvent.Keycode == Key.D)
        {
            _session.QueueMovementPulse(1, 0);
        }
        if (keyEvent.PhysicalKeycode == Key.Space || keyEvent.Keycode == Key.Space)
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
        }
    }

    public override void _ExitTree()
    {
        ReleaseSyntheticInput();
    }

    private static void ConfigureInputMap()
    {
        EnsureKeyAction(MoveForwardAction, Key.W);
        EnsureKeyAction(MoveBackwardAction, Key.S);
        EnsureKeyAction(MoveLeftAction, Key.A);
        EnsureKeyAction(MoveRightAction, Key.D);
        EnsureKeyAction(LookLeftAction, Key.Left);
        EnsureKeyAction(LookRightAction, Key.Right);
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

    private static InteractiveInput SampleInput()
    {
        sbyte moveX = QuantizeAxis(Input.GetAxis(MoveLeftAction, MoveRightAction));
        sbyte moveZ = QuantizeAxis(Input.GetAxis(MoveBackwardAction, MoveForwardAction));
        sbyte lookX = QuantizeAxis(Input.GetAxis(LookLeftAction, LookRightAction));
        return new InteractiveInput(
            moveX,
            moveZ,
            Input.IsActionPressed(FireAction),
            Input.IsActionPressed(ToggleModeAction),
            Input.IsActionPressed(ResetAction),
            lookX);
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

    private static void ApplySyntheticInput(InteractiveInput input)
    {
        SetSyntheticAction(MoveLeftAction, input.MoveX < 0);
        SetSyntheticAction(MoveRightAction, input.MoveX > 0);
        SetSyntheticAction(MoveBackwardAction, input.MoveZ < 0);
        SetSyntheticAction(MoveForwardAction, input.MoveZ > 0);
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
                     FireAction,
                     ToggleModeAction,
                     ResetAction,
                 })
        {
            Input.ActionRelease(action);
        }
    }

    private void RunFocusLossHandlerSmokeProbe()
    {
        var heldInput = new InteractiveInput(1, 1, true, true, true);
        _session.ObserveInput(heldInput);
        _session.QueueMovementPulse(-1, -1);
        _session.QueueFirePulse();

        _Notification((int)NotificationWMWindowFocusOut);
        _session.ObserveInput(heldInput);
        _session.QueueMovementPulse(1, 0);
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
            else if (argument.StartsWith("--local-assets=", StringComparison.Ordinal))
            {
                _localAssetsRoot = argument["--local-assets=".Length..];
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
                SchemaVersion = "onslaught-first-flight-smoke.v1",
                EngineVersion = engineVersion,
                ExitReason = "smoke-complete",
                Tick = _session.CurrentSnapshot.Tick,
                StateHash = StateHasher.ComputeHex(_session.CurrentSnapshot),
                TargetsDestroyed = _session.CurrentSnapshot.TargetsDestroyed,
                Mode = _session.CurrentSnapshot.Mode.ToString(),
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
                TargetVisualCount = _world.TargetVisualCount,
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
        public required int TargetVisualCount { get; init; }
        public required bool HudReady { get; init; }
        public required bool FocusLossHandlerInputCleared { get; init; }
        public required bool FocusLossHandlerNeutralRearmed { get; init; }
        public required string ScreenshotFileName { get; init; }
        public required int ScreenshotWidth { get; init; }
        public required int ScreenshotHeight { get; init; }
        public required string ScreenshotSha256 { get; init; }
    }
}
