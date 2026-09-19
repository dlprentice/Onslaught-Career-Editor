// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// A normal editor-visible TextureRect whose decoded retail texture is a
/// transient binding. Saving a public scene preserves its layout, never the
/// private pixels supplied by a presentation asset owner.
/// </summary>
[Tool]
public sealed partial class RetailTextureRect : TextureRect
{
    public override void _ValidateProperty(Godot.Collections.Dictionary property)
    {
        if (property["name"].AsStringName() == PropertyName.Texture)
        {
            PropertyUsageFlags usage = property["usage"].As<PropertyUsageFlags>();
            property["usage"] = (int)((usage & ~PropertyUsageFlags.Storage) |
                PropertyUsageFlags.Editor | PropertyUsageFlags.ReadOnly);
        }
    }
}
