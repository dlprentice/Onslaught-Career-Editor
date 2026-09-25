// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Retained original Main Menu component used only by its comparison scene. Position, size and modulate are ordinary
/// Control properties and affect the production draw. SourceRect is the
/// measured retail coordinate space, not a second preview implementation.
/// No input, media playback, simulation or file writes are owned here.
/// </summary>
[Tool]
public sealed partial class MainMenuReferencePart : Control
{
    [Export] public string Section { get; set; } = string.Empty;
    private Rect2 _sourceRect = new(0, 0, 640, 480);
    [Export]
    public Rect2 SourceRect
    {
        get => _sourceRect;
        set { _sourceRect = value; QueueRedraw(); }
    }

    private string _text = string.Empty;
    private bool _overrideText;
    /// <summary>Faithful defaults keep the imported localized string in every language.</summary>
    [Export]
    public bool OverrideText
    {
        get => _overrideText;
        set { _overrideText = value; QueueRedraw(); }
    }
    /// <summary>Used only when OverrideText deliberately enables an enhanced-layout override.</summary>
    [Export(PropertyHint.MultilineText)]
    public string Text
    {
        get => _text;
        set { _text = value; QueueRedraw(); }
    }

    public override void _Draw()
    {
        Node? current = GetParent();
        while (current is not null && current is not MainMenuReference)
            current = current.GetParent();
        if (current is MainMenuReference frontend)
            frontend.DrawScenePart(this);
    }

    public override void _Notification(int what)
    {
        if (what == NotificationResized)
            QueueRedraw();
    }
}
