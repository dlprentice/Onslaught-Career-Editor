// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>The one letterbox transform shared by every authored HUD layer.</summary>
[Tool]
public sealed partial class HudDesignStage : Control
{
    private Control? _surface;

    public override void _Ready()
    {
        _surface = GetParent<Control>();
        _surface.Resized += Fit;
        Fit();
    }

    private void Fit()
    {
        if (_surface is null || _surface.Size.X <= 0f || _surface.Size.Y <= 0f)
            return;
        float factor = Mathf.Min(_surface.Size.X / 640f, _surface.Size.Y / 480f);
        Scale = new Vector2(factor, factor);
        Position = (_surface.Size - new Vector2(640f, 480f) * factor) * 0.5f;
    }
}
