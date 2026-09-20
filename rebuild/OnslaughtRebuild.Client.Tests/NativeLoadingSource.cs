// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client.Tests;

/// <summary>Source routing for the existing Loading-only isolation guards.</summary>
internal static class NativeLoadingSource
{
    public static string Read(string name) => File.ReadAllText(Path.Combine(
        AppContext.BaseDirectory, "godot-loading-source", name));

    public static string Presentation => Read("loading_presentation.gd") + "\n" + Read("Loading.tscn");
}
