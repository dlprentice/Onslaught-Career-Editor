// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary language bridge: GDScript owns both the pause model and the
/// complete authored presentation in the standard-Godot scene. The
/// bridge creates no controls, loads no visual assets, and handles no devices.
/// </summary>
public sealed partial class FirstFlightPauseMenu : Node
{
    public const string ScenePath = "res://Scenes/Pause/PauseMenu.tscn";
    private GdPauseMenuState _model = null!;
    public CanvasLayer Presentation { get; private set; } = null!;
    public bool InputReady => Presentation.Get("input_ready").AsBool();
    public bool IsClosing => Presentation.Get("is_closing").AsBool();
    public bool Visible
    {
        get => Presentation.Visible;
        set => Presentation.Visible = value;
    }

    public static FirstFlightPauseMenu Create(GdPauseMenuState model)
    {
        ArgumentNullException.ThrowIfNull(model);
        var bridge = new FirstFlightPauseMenu { Name = "Level100PauseBridge" };
        bridge.Presentation = GD.Load<PackedScene>(ScenePath).Instantiate<CanvasLayer>();
        bridge.AddChild(bridge.Presentation);
        bridge.Initialize(model);
        return bridge;
    }

    public void Initialize(GdPauseMenuState model)
    {
        ArgumentNullException.ThrowIfNull(model);
        _model = model;
        Refresh();
    }

    public override void _Ready() => Refresh();

    public void Open()
    {
        Refresh();
        Presentation.Call("open_panel");
    }

    public void Close() => Presentation.Call("close_panel");
    public void Reset() => Presentation.Call("reset_panel");
    public void AdvanceAnimation(double delta) => Presentation.Call("advance_animation", delta);

    public void Refresh()
    {
        if (!Presentation.Call("set_snapshot", _model.ViewSnapshot).AsBool())
            throw new InvalidDataException("The pause presentation rejected the Client menu snapshot.");
    }

    public bool TryHover(Vector2 viewportPosition) => TryPointAt(viewportPosition, out bool moved) && moved;

    public bool TryPointAt(Vector2 viewportPosition, out bool moved)
    {
        int index = Presentation.Call("point_at", viewportPosition).AsInt32();
        if (index < 0 || index >= _model.Entries.Count || !_model.Entries[index].IsEnabled)
        {
            moved = false;
            return false;
        }
        moved = _model.Hover(index);
        if (moved)
            Refresh();
        return true;
    }

}
