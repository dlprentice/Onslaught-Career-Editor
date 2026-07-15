// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightHud : CanvasLayer
{
    private static readonly Color PanelBackground = new(0.025f, 0.035f, 0.045f, 0.92f);
    private static readonly Color PanelBorder = new(0.24f, 0.33f, 0.38f, 0.9f);
    private static readonly Color TextPrimary = new(0.92f, 0.96f, 0.97f);
    private static readonly Color TextMuted = new(0.60f, 0.69f, 0.72f);
    private static readonly Color Energy = new(0.13f, 0.80f, 0.88f);
    private static readonly Color Shield = new(0.24f, 0.48f, 0.93f);
    private static readonly Color Hull = new(0.32f, 0.78f, 0.43f);
    private static readonly Color Alert = new(0.96f, 0.59f, 0.22f);

    private Label _objectiveLabel = null!;
    private Label _modeLabel = null!;
    private Label _statusLabel = null!;
    private ProgressBar _energyBar = null!;
    private ProgressBar _shieldBar = null!;
    private ProgressBar _hullBar = null!;
    private PanelContainer _controlsPanel = null!;
    private double _elapsed;

    public bool IsReadyForSmoke =>
        IsInstanceValid(_objectiveLabel) &&
        IsInstanceValid(_modeLabel) &&
        IsInstanceValid(_energyBar) &&
        IsInstanceValid(_controlsPanel);

    public void Initialize(LocalPresentationLoadStatus localPresentation = default)
    {
        var root = new Control
        {
            Name = "HudRoot",
            AnchorRight = 1f,
            AnchorBottom = 1f,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        AddChild(root);

        BuildIdentityPanel(root, localPresentation);
        BuildObjectivePanel(root);
        BuildModePanel(root);
        BuildControlsPanel(root);
        BuildReticle(root);
    }

    public override void _Process(double delta)
    {
        _elapsed += delta;
        if (_elapsed > 14d)
        {
            Color color = _controlsPanel.Modulate;
            color.A = Mathf.MoveToward(color.A, 0.62f, (float)delta * 0.25f);
            _controlsPanel.Modulate = color;
        }
    }

    public void UpdateFromSnapshot(WorldSnapshot snapshot)
    {
        SetProgressValue(_energyBar, snapshot.Energy);
        SetProgressValue(_shieldBar, snapshot.Shield);
        SetProgressValue(_hullBar, snapshot.Hull);

        int targetCount = snapshot.Targets.Count;
        SetLabelText(_objectiveLabel, snapshot.TargetsDestroyed == targetCount
            ? "ARENA CLEAR  |  PRESS R TO RESET"
            : $"DESTROY SENTRIES  {snapshot.TargetsDestroyed}/{targetCount}");
        SetLabelColor(_objectiveLabel, snapshot.TargetsDestroyed == targetCount ? Hull : TextPrimary);

        if (snapshot.TransformTicksRemaining > 0)
        {
            SetLabelText(_modeLabel, $"TRANSFORMING  {snapshot.TransformTicksRemaining}");
            SetLabelColor(_modeLabel, Alert);
            SetLabelText(_statusLabel, "Movement and weapons are locked during transformation");
        }
        else if (snapshot.Mode == VehicleMode.Jet)
        {
            SetLabelText(_modeLabel, "JET MODE");
            SetLabelColor(_modeLabel, Energy);
            SetLabelText(_statusLabel, "Fast movement | Energy drains | Shield offline");
        }
        else
        {
            SetLabelText(_modeLabel, "WALKER MODE");
            SetLabelColor(_modeLabel, TextPrimary);
            SetLabelText(_statusLabel, "Energy and shield regenerate");
        }
    }

    public void MarkInputActivity()
    {
        _elapsed = 0d;
        Color color = _controlsPanel.Modulate;
        color.A = 1f;
        _controlsPanel.Modulate = color;
    }

    private void BuildIdentityPanel(Control root, LocalPresentationLoadStatus localPresentation)
    {
        var panel = CreatePanel("IdentityPanel");
        panel.OffsetLeft = 24f;
        panel.OffsetTop = 22f;
        panel.OffsetRight = 354f;
        panel.OffsetBottom = 190f;
        root.AddChild(panel);

        var stack = new VBoxContainer();
        stack.AddThemeConstantOverride("separation", 5);
        panel.AddChild(stack);
        stack.AddChild(CreateLabel("FIRST FLIGHT", 22, TextPrimary));
        stack.AddChild(CreateLabel(
            DescribePresentation(localPresentation),
            13,
            TextMuted));

        _energyBar = AddResourceRow(stack, "ENERGY", Energy);
        _shieldBar = AddResourceRow(stack, "SHIELD", Shield);
        _hullBar = AddResourceRow(stack, "HULL", Hull);
    }

    private static string DescribePresentation(LocalPresentationLoadStatus status) => status switch
    {
        { PlayerLoaded: true, TerrainLoaded: true } => "User-supplied local meshes: player + terrain | non-parity",
        { PlayerLoaded: true } => "User-supplied local mesh: player | synthetic terrain | non-parity",
        { TerrainLoaded: true } => "Synthetic player | user-supplied local mesh: terrain | non-parity",
        _ => "Synthetic arena | RE-informed prototype",
    };

    private void BuildObjectivePanel(Control root)
    {
        var panel = CreatePanel("ObjectivePanel");
        panel.AnchorLeft = 0.5f;
        panel.AnchorRight = 0.5f;
        panel.OffsetLeft = -225f;
        panel.OffsetRight = 225f;
        panel.OffsetTop = 22f;
        panel.OffsetBottom = 82f;
        root.AddChild(panel);

        _objectiveLabel = CreateLabel("DESTROY SENTRIES  0/3", 18, TextPrimary);
        _objectiveLabel.HorizontalAlignment = HorizontalAlignment.Center;
        _objectiveLabel.VerticalAlignment = VerticalAlignment.Center;
        panel.AddChild(_objectiveLabel);
    }

    private void BuildModePanel(Control root)
    {
        var panel = CreatePanel("ModePanel");
        panel.AnchorLeft = 1f;
        panel.AnchorRight = 1f;
        panel.OffsetLeft = -338f;
        panel.OffsetRight = -24f;
        panel.OffsetTop = 22f;
        panel.OffsetBottom = 112f;
        root.AddChild(panel);

        var stack = new VBoxContainer();
        stack.AddThemeConstantOverride("separation", 5);
        panel.AddChild(stack);
        _modeLabel = CreateLabel("WALKER MODE", 20, TextPrimary);
        _modeLabel.HorizontalAlignment = HorizontalAlignment.Right;
        stack.AddChild(_modeLabel);
        _statusLabel = CreateLabel("Energy and shield regenerate", 13, TextMuted);
        _statusLabel.HorizontalAlignment = HorizontalAlignment.Right;
        _statusLabel.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        stack.AddChild(_statusLabel);
    }

    private void BuildControlsPanel(Control root)
    {
        _controlsPanel = CreatePanel("ControlsPanel");
        _controlsPanel.AnchorLeft = 0.5f;
        _controlsPanel.AnchorRight = 0.5f;
        _controlsPanel.AnchorTop = 1f;
        _controlsPanel.AnchorBottom = 1f;
        _controlsPanel.OffsetLeft = -390f;
        _controlsPanel.OffsetRight = 390f;
        _controlsPanel.OffsetTop = -70f;
        _controlsPanel.OffsetBottom = -20f;
        root.AddChild(_controlsPanel);

        var controls = CreateLabel(
            "WASD  MOVE     ←→  LOOK     SPACE  FIRE     Q  TRANSFORM     R  RESET     ESC  EXIT",
            15,
            TextPrimary);
        controls.HorizontalAlignment = HorizontalAlignment.Center;
        controls.VerticalAlignment = VerticalAlignment.Center;
        _controlsPanel.AddChild(controls);
    }

    private static void BuildReticle(Control root)
    {
        var horizontal = new ColorRect
        {
            Name = "ReticleHorizontal",
            Color = new Color(0.90f, 0.95f, 0.95f, 0.78f),
            AnchorLeft = 0.5f,
            AnchorRight = 0.5f,
            AnchorTop = 0.5f,
            AnchorBottom = 0.5f,
            OffsetLeft = -9f,
            OffsetRight = 9f,
            OffsetTop = -1f,
            OffsetBottom = 1f,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        root.AddChild(horizontal);

        var vertical = new ColorRect
        {
            Name = "ReticleVertical",
            Color = horizontal.Color,
            AnchorLeft = 0.5f,
            AnchorRight = 0.5f,
            AnchorTop = 0.5f,
            AnchorBottom = 0.5f,
            OffsetLeft = -1f,
            OffsetRight = 1f,
            OffsetTop = -9f,
            OffsetBottom = 9f,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        root.AddChild(vertical);
    }

    private static PanelContainer CreatePanel(string name)
    {
        var panel = new PanelContainer
        {
            Name = name,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        panel.AddThemeStyleboxOverride(
            "panel",
            VisualPrimitives.CreatePanelStyle(PanelBackground, PanelBorder));
        return panel;
    }

    private static Label CreateLabel(string text, int size, Color color)
    {
        var label = new Label
        {
            Text = text,
            Modulate = color,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        label.AddThemeFontSizeOverride("font_size", size);
        return label;
    }

    private static ProgressBar AddResourceRow(VBoxContainer parent, string labelText, Color fillColor)
    {
        var row = new HBoxContainer();
        row.AddThemeConstantOverride("separation", 8);
        parent.AddChild(row);

        var label = CreateLabel(labelText, 12, TextMuted);
        label.CustomMinimumSize = new Vector2(54f, 16f);
        row.AddChild(label);

        var bar = new ProgressBar
        {
            MinValue = 0,
            MaxValue = 1000,
            Value = 1000,
            ShowPercentage = false,
            CustomMinimumSize = new Vector2(225f, 12f),
            SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        bar.AddThemeStyleboxOverride(
            "background",
            VisualPrimitives.CreatePanelStyle(new Color(0.07f, 0.09f, 0.10f, 0.95f), new Color(0.13f, 0.16f, 0.17f)));
        bar.AddThemeStyleboxOverride(
            "fill",
            VisualPrimitives.CreatePanelStyle(fillColor, fillColor.Lightened(0.15f)));
        row.AddChild(bar);
        return bar;
    }

    private static void SetProgressValue(ProgressBar bar, double value)
    {
        if (!Mathf.IsEqualApprox((float)bar.Value, (float)value))
        {
            bar.Value = value;
        }
    }

    private static void SetLabelText(Label label, string text)
    {
        if (!string.Equals(label.Text, text, StringComparison.Ordinal))
        {
            label.Text = text;
        }
    }

    private static void SetLabelColor(Label label, Color color)
    {
        if (!label.Modulate.IsEqualApprox(color))
        {
            label.Modulate = color;
        }
    }
}
