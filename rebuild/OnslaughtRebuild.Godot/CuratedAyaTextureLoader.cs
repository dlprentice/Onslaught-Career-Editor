// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary import-only bridge to the production native decoder. The retained
/// managed implementation lives in Scenes/Shared/Tests as an independent oracle.
/// </summary>
internal static class CuratedAyaTextureLoader
{
    internal enum Compression
    {
        Dxt1,
        Dxt2,
        Rgba8,
    }

    private const string ScriptPath = "res://Scenes/Shared/retail_aya_texture.gd";

    public static Texture2D Load(
        string resourcePath,
        int expectedWidth,
        int expectedHeight,
        Compression expectedCompression = Compression.Dxt2,
        Image.Format? expectedTargetFormat = null,
        int? expectedMipCount = null)
    {
        using GDScript script = GD.Load<GDScript>(ScriptPath);
        using Variant created = script.New();
        using RefCounted loader = created.As<RefCounted>();
        // Nil is distinct from an explicit negative enum/mip value in the
        // original API. Do not use the strict recipe API's negative sentinels.
        using Variant target = expectedTargetFormat is Image.Format format ? Variant.From((int)format) : default;
        using Variant mips = expectedMipCount is int count ? Variant.From(count) : default;
        using Variant returned = loader.Call("load_texture_checked", resourcePath,
            expectedWidth, expectedHeight, (int)expectedCompression, target, mips);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        using Variant ok = result["ok"];
        if (!ok.AsBool())
        {
            using Variant message = result["error"];
            throw new InvalidDataException(message.AsString());
        }
        using Variant value = result["value"];
        return value.As<ImageTexture>();
    }
}
