// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// A native editable rectangle for one exact HUD drawing law. SourceRect names
/// the measured retail coordinate frame; Position, Size, Scale and Rotation
/// are ordinary Control transforms and affect the production drawing.
/// </summary>
[Tool]
public sealed partial class RetailHudPart : Control
{
    public enum Content
    {
        CompassBase,
        LeftWeapon,
        ScannerContacts,
        RightWeapon,
        WeaponSelection,
        BattleLine,
        MessageFrame,
        OffscreenObjectives,
        CrosshairTarget,
        ScannerOutline,
        LeftWeaponOutline,
        RightWeaponOutline,
        WeaponSelectionOutline,
        CompassGlow,
        InfluenceMap,
        BattleLineOutline,
        Forseti,
        ObjectiveReticles,
        MessageText,
        HelpText,
        WeaponAmmo,
        Terminal,
    }

    private Content _part;
    private Rect2 _sourceRect = new(0f, 0f, 640f, 480f);
    private FirstFlightHud? _hud;

    [Export]
    public Content Part
    {
        get => _part;
        set { _part = value; QueueRedraw(); }
    }

    [Export]
    public Rect2 SourceRect
    {
        get => _sourceRect;
        set { _sourceRect = value; QueueRedraw(); }
    }

    public override void _ValidateProperty(Godot.Collections.Dictionary property)
    {
        // Imported drawing identities are visible separately from the ordinary
        // editable Control transform. Deliberate enhanced layouts change that
        // transform; replacing a measured drawing law is an explicit code edit.
        string name = property["name"].AsString();
        if (name is nameof(Part) or nameof(SourceRect))
            property["usage"] = (int)(property["usage"].As<PropertyUsageFlags>() | PropertyUsageFlags.ReadOnly);
    }

    public override void _Ready()
    {
        MouseFilter = MouseFilterEnum.Ignore;
        Resized += QueueRedraw;
        for (Node? node = GetParent(); node is not null; node = node.GetParent())
        {
            if (node is FirstFlightHud hud)
            {
                _hud = hud;
                break;
            }
        }
    }

    public override void _Draw() => _hud?.DrawPart(this);

    public Transform2D RetailToLocalTransform()
    {
        Vector2 ratio = new(
            SourceRect.Size.X > 0f ? Size.X / SourceRect.Size.X : 1f,
            SourceRect.Size.Y > 0f ? Size.Y / SourceRect.Size.Y : 1f);
        return new Transform2D(
            new Vector2(ratio.X, 0f),
            new Vector2(0f, ratio.Y),
            -SourceRect.Position * ratio);
    }

    internal void SetRetailDrawTransform(Vector2 offset, float rotation, Vector2 scale)
    {
        Transform2D local = new Transform2D(rotation, offset).ScaledLocal(scale);
        DrawSetTransformMatrix(RetailToLocalTransform() * local);
    }
}
