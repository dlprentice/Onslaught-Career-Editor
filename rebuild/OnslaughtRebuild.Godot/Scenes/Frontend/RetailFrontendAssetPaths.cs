// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Public routing recipe; textures remain in the private materialized asset owner.</summary>
[Tool]
[GlobalClass]
public sealed partial class RetailFrontendAssetPaths : Resource
{
    [Export(PropertyHint.Dir)] public string FrontendDirectory { get; set; } = "res://Assets/Frontend";
    [Export(PropertyHint.Dir)] public string HudDirectory { get; set; } = "res://Assets/Hud";
    [Export(PropertyHint.Dir)] public string PauseDirectory { get; set; } = "res://Assets/PauseMenu";
    [Export] public Godot.Collections.Dictionary<string, string> TextureOverrides { get; set; } = new();

    public string TexturePath(string folder, string name)
    {
        string key = $"{folder}/{name}";
        if (TextureOverrides.TryGetValue(key, out string? path) && !string.IsNullOrWhiteSpace(path))
            return path;
        string directory = folder switch
        {
            "Frontend" => FrontendDirectory,
            "Hud" => HudDirectory,
            "PauseMenu" => PauseDirectory,
            _ => throw new ArgumentOutOfRangeException(nameof(folder)),
        };
        return $"{directory.TrimEnd('/')}/{name}.texture.aya";
    }
}
