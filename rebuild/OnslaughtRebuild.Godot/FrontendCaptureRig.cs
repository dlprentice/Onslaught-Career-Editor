// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Deterministic screenshot capture for the bounded released frontend path.
///
/// This is a PRESENTATION-LAYER rig. It exists so parity claims can cite pixels
/// instead of code paths. <c>OnslaughtRebuild.Core</c> must never reference it —
/// it touches the GPU (viewport readback), the filesystem (PNG writes), and the
/// engine frame clock, all of which Core is contractually free of.
///
/// Determinism contract: the engine must be launched with <c>--fixed-fps</c> so
/// that one <c>_Process</c> call is one logical frame. Shots are keyed to frame
/// ordinals, never to wall-clock time, so a given plan yields byte-identical
/// framing across runs on the same build.
///
/// Retail reference captures are 640x480 (see the Hypothesis 1 verdict — the
/// released frontend composes at 4:3). Launch with <c>--resolution 640x480</c>
/// for pixel-comparable output; the rig records the actual size it saw so a
/// mismatched run cannot be silently compared against a 640x480 reference.
/// </summary>
public sealed partial class FrontendCaptureRig : Node
{
    /// <summary>Frame ordinal, the shot label, and the screen expected at that point.</summary>
    private readonly record struct Shot(int Frame, string Label, RetailFrontendScreen? ExpectScreen);

    /// <summary>Frame ordinal and the flow action to apply before that frame draws.</summary>
    private readonly record struct Step(int Frame, string Action);

    private readonly List<Shot> _shots = [];
    private readonly List<Step> _steps = [];
    private readonly List<Dictionary<string, object?>> _written = [];

    /// <summary>
    /// Released composition size. `CD3DApplication__Init` seeds
    /// `m_dwCreationWidth = 0x280` (640) and `m_dwCreationHeight = 0x1e0` (480),
    /// and every retail reference capture is 640x480.
    /// </summary>
    private const int NativeWidth = 640;
    private const int NativeHeight = 480;

    private RetailFrontendFlow _frontend = null!;
    private string _outputDirectory = string.Empty;
    private string _planName = string.Empty;
    private int _captureWidth = NativeWidth;
    private int _captureHeight = NativeHeight;
    private int _frame = -1;
    private int _shotCursor;
    private int _stepCursor;
    private string? _pendingLabel;
    private bool _finished;

    /// <summary>
    /// Frames are chosen to land on settled state, not on transition edges.
    /// FEBack128 runs at 15 fps over 286 frames; at --fixed-fps 60 one video
    /// frame is four engine frames, so multiples of 4 sample a stable video frame.
    /// </summary>
    private static readonly (int Frame, string Label, RetailFrontendScreen? Screen)[] StartupPlan =
    [
        (12, "01-click-early", RetailFrontendScreen.ClickToStart),
        (120, "02-click-settled", RetailFrontendScreen.ClickToStart),
        (132, "03-main-menu-entry", RetailFrontendScreen.MainMenu),
        (240, "04-main-menu-settled", RetailFrontendScreen.MainMenu),
        (252, "05-dev-select-entry", RetailFrontendScreen.DevSelect),
        (300, "06-dev-select-settled", RetailFrontendScreen.DevSelect),
        (312, "07-level-select", RetailFrontendScreen.LevelSelect),
        (360, "08-level-select-settled", RetailFrontendScreen.LevelSelect),
        // The loading screen is short-lived: at +4 frames the flow has already
        // reached Gameplay. Sample the frame immediately after the confirm.
        (369, "09-loading-handoff", RetailFrontendScreen.Loading),
    ];

    private static readonly (int Frame, string Action)[] StartupSteps =
    [
        (128, "confirm"), // click-to-start -> main menu
        (248, "confirm"), // main menu New Game -> FEP_DEVSELECT
        (308, "confirm"), // CHOOSE GAME NAME -> level select
        (368, "confirm"), // level select Level 100 -> loading
    ];

    public static bool TryCreate(
        IReadOnlyList<string> arguments,
        RetailFrontendFlow frontend,
        out FrontendCaptureRig? rig)
    {
        rig = null;
        string? directory = null;
        string plan = "startup";
        int width = NativeWidth;
        int height = NativeHeight;

        foreach (string argument in arguments)
        {
            if (argument.StartsWith("--capture-dir=", System.StringComparison.Ordinal))
            {
                directory = argument["--capture-dir=".Length..];
            }
            else if (argument.StartsWith("--capture-plan=", System.StringComparison.Ordinal))
            {
                plan = argument["--capture-plan=".Length..];
            }
            else if (argument.StartsWith("--capture-size=", System.StringComparison.Ordinal))
            {
                string[] parts = argument["--capture-size=".Length..].Split('x');
                if (parts.Length != 2 ||
                    !int.TryParse(parts[0], out width) ||
                    !int.TryParse(parts[1], out height) ||
                    width <= 0 || height <= 0)
                {
                    throw new ArgumentException(
                        $"Malformed --capture-size in '{argument}'. Expected WIDTHxHEIGHT, e.g. 640x480.");
                }
            }
        }

        if (string.IsNullOrWhiteSpace(directory))
        {
            return false;
        }

        if (!Path.IsPathFullyQualified(directory))
        {
            throw new ArgumentException("Capture mode requires an absolute --capture-dir path.");
        }

        if (plan != "startup")
        {
            throw new ArgumentException($"Unknown capture plan '{plan}'. Known plans: startup.");
        }

        rig = new FrontendCaptureRig
        {
            Name = "FrontendCaptureRig",
            _frontend = frontend,
            _outputDirectory = directory,
            _planName = plan,
            _captureWidth = width,
            _captureHeight = height,
        };
        return true;
    }

    public override void _Ready()
    {
        _ = Directory.CreateDirectory(_outputDirectory);
        ApplyNativeCaptureViewport();

        foreach ((int frame, string label, RetailFrontendScreen? screen) in StartupPlan)
        {
            _shots.Add(new Shot(frame, label, screen));
        }

        foreach ((int frame, string action) in StartupSteps)
        {
            _steps.Add(new Step(frame, action));
        }

        _shots.Sort(static (left, right) => left.Frame.CompareTo(right.Frame));
        _steps.Sort(static (left, right) => left.Frame.CompareTo(right.Frame));

        // FramePostDraw fires after the frame is rasterized, which is the only
        // point at which viewport readback returns the frame _Process just staged.
        RenderingServer.Singleton.Connect(
            RenderingServer.SignalName.FramePostDraw,
            Callable.From(OnFramePostDraw));
    }

    /// <summary>
    /// Forces a 1:1 native composition for the duration of the capture run.
    ///
    /// This is CAPTURE-ONLY and deliberately does not change the shipped window
    /// contract in `project.godot` (1280x720) — that is a product decision, not a
    /// parity concern. `RetailFrontendFlow` letterboxes its 640x480 design stage
    /// with `scale = min(Size.X / 640, Size.Y / 480)`, so at exactly 640x480 the
    /// scale is 1.0 and the offset is zero: every drawn pixel maps to one output
    /// pixel, which is what makes a direct diff against the retail reference
    /// meaningful. At any other size the frame is resampled and sub-pixel layout
    /// error — the kind we are hunting — gets smeared away before it can be seen.
    ///
    /// Content scaling is disabled rather than resized so Godot does not
    /// reintroduce its own stretch transform on top of the flow's.
    /// </summary>
    private void ApplyNativeCaptureViewport()
    {
        Window window = GetWindow();
        window.ContentScaleMode = Window.ContentScaleModeEnum.Disabled;
        window.ContentScaleAspect = Window.ContentScaleAspectEnum.Ignore;
        window.Size = new Vector2I(_captureWidth, _captureHeight);
    }

    public override void _Process(double delta)
    {
        if (_finished)
        {
            return;
        }

        _frame++;

        while (_stepCursor < _steps.Count && _steps[_stepCursor].Frame == _frame)
        {
            ApplyAction(_steps[_stepCursor].Action);
            _stepCursor++;
        }

        if (_shotCursor < _shots.Count && _shots[_shotCursor].Frame == _frame)
        {
            _pendingLabel = _shots[_shotCursor].Label;
        }
    }

    private void ApplyAction(string action)
    {
        switch (action)
        {
            case "confirm":
                _frontend.ConfirmForSmoke();
                break;
            default:
                throw new ArgumentException($"Unknown capture action '{action}'.");
        }
    }

    private void OnFramePostDraw()
    {
        if (_pendingLabel is not { } label)
        {
            return;
        }

        _pendingLabel = null;
        Shot shot = _shots[_shotCursor];
        _shotCursor++;

        Image image = GetViewport().GetTexture().GetImage();
        string path = Path.Combine(_outputDirectory, $"{label}.png");
        Error error = image.SavePng(path);

        RetailFrontendScreen actual = _frontend.CurrentScreen;
        _written.Add(new Dictionary<string, object?>
        {
            ["label"] = label,
            ["frame"] = shot.Frame,
            ["path"] = path,
            ["width"] = image.GetWidth(),
            ["height"] = image.GetHeight(),
            ["expectedScreen"] = shot.ExpectScreen?.ToString(),
            ["actualScreen"] = actual.ToString(),
            // A shot taken on the wrong screen is not evidence. Record the
            // disagreement rather than letting a mislabeled PNG be compared.
            ["screenMatched"] = shot.ExpectScreen is null || shot.ExpectScreen == actual,
            ["saveError"] = error == Error.Ok ? null : error.ToString(),
        });

        if (_shotCursor >= _shots.Count)
        {
            _finished = true;
            WriteManifest();
            GetTree().Quit();
        }
    }

    private void WriteManifest()
    {
        Godot.Collections.Dictionary versionInfo = Engine.GetVersionInfo();
        var manifest = new Dictionary<string, object?>
        {
            ["schema"] = "onslaught-frontend-capture.v1",
            ["plan"] = _planName,
            ["engineVersion"] = versionInfo["string"].AsString(),
            ["viewportWidth"] = GetViewport().GetVisibleRect().Size.X,
            ["viewportHeight"] = GetViewport().GetVisibleRect().Size.Y,
            ["retailReferenceSize"] = "640x480",
            ["shots"] = _written,
        };

        File.WriteAllText(
            Path.Combine(_outputDirectory, "capture-manifest.json"),
            JsonSerializer.Serialize(manifest, new JsonSerializerOptions { WriteIndented = true }));
    }
}
