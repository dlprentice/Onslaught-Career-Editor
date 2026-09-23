// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;

namespace OnslaughtRebuild.GodotClient;

// The authored MouseCursor scene owns the final frontend draw. Measurement
// provenance and the retired renderer remain in Tests/MouseCursorReference.cs.
public sealed partial class RetailFrontendFlow
{
    private Control? _mouseCursorLayer;
    private Vector2? _captureMouseCursorDesignPosition;

    private void InitializeMouseCursor()
    {
        _mouseCursorLayer = GetNode<Control>("MouseCursor");
        if (Engine.IsEditorHint())
        {
            // The component is inspectable in the scene, but opening the full
            // frontend does not poll the editor pointer or install a cursor.
            _mouseCursorLayer.Visible = false;
            return;
        }
        _mouseCursorLayer.Visible = true;
        using Variant configured = _mouseCursorLayer.Call("configure_live_pointer", this);
        using Godot.Collections.Dictionary result = configured.AsGodotDictionary();
        RequireOptionsResult(result);
        UpdateMouseCursorFrame();
    }

    internal void SetMouseCursorDesignPositionForCapture(Vector2? position)
    {
        _captureMouseCursorDesignPosition = position;
        UpdateMouseCursorFrame();
    }

    private void UpdateMouseCursorFrame()
    {
        if (_mouseCursorLayer is null || Engine.IsEditorHint()) return;
        using var facts = new Godot.Collections.Dictionary
        {
            ["screen"] = (int)_session.Screen,
            ["cursor_position"] = _captureMouseCursorDesignPosition.HasValue
                ? Variant.From(_captureMouseCursorDesignPosition.Value) : default,
        };
        using Variant batch = facts;
        using Variant returned = _mouseCursorLayer.Call("set_frame", batch);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        RequireOptionsResult(result);
    }
}
