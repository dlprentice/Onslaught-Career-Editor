// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Prints the pinned engine's redistribution notices as one JSON line for export packaging:
/// <c>--script res://Development/LicenseMetadata.cs</c>. Development builds only.
/// </summary>
public partial class LicenseMetadata : SceneTree
{
    public override void _Initialize()
    {
        Godot.Collections.Dictionary notices = new()
        {
            ["license"] = Engine.GetLicenseText(),
            ["components"] = Engine.GetCopyrightInfo(),
            ["licenses"] = Engine.GetLicenseInfo(),
        };
        GD.Print(Json.Stringify(notices));
        Quit();
    }
}
