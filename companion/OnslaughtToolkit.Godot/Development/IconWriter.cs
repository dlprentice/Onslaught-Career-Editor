// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Writes the companion's emblem, rasterised by the same code as the window icon, as a PNG for an
/// export's application icon: <c>--script res://Development/IconWriter.cs -- --output=ABSOLUTE_PNG</c>.
/// The file is made in a staged export copy and never committed. Development builds only.
/// </summary>
public partial class IconWriter : SceneTree
{
    public override void _Initialize()
    {
        string output = OS.GetCmdlineUserArgs().FirstOrDefault(argument => argument.StartsWith("--output=", StringComparison.Ordinal))?["--output=".Length..] ?? "";
        Error saved = output.Length > 0 ? Emblem.Icon(256).SavePng(output) : Error.InvalidParameter;
        if (saved != Error.Ok) GD.PrintErr($"The icon could not be written to '{output}': {saved}");
        else GD.Print("ICON_WRITTEN " + output);
        Quit(saved == Error.Ok ? 0 : 1);
    }
}
