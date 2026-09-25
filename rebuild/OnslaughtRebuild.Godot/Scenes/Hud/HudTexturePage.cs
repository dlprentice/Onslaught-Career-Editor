// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// A serializable recipe for a private curated texture. Only the source path,
/// dimensions and format are stored in the public scene; decoded pixels remain
/// an unexported in-memory texture. Native TextureRects use this in editor and game.
/// </summary>
[Tool]
public sealed partial class HudTexturePage : Texture2D
{
    public enum PageFormat { Dxt1, Dxt2, Rgba8 }

    private string _sourcePath = string.Empty;
    private Vector2I _dimensions = new(128, 128);
    private PageFormat _compression = PageFormat.Dxt2;

    [Export(PropertyHint.File, "*.texture.aya")]
    public string SourcePath
    {
        get => _sourcePath;
        set { _sourcePath = value; Invalidate(); }
    }

    [Export]
    public Vector2I Dimensions
    {
        get => _dimensions;
        set { _dimensions = value; Invalidate(); }
    }

    [Export]
    public PageFormat Compression
    {
        get => _compression;
        set { _compression = value; Invalidate(); }
    }

    private void Invalidate()
    {
        _loadedRecipe = string.Empty;
        _decoded = null;
        EmitChanged();
    }

    private Texture2D? _decoded;
    private string _loadedRecipe = string.Empty;

    private Texture2D? Decoded()
    {
        string recipe = $"{SourcePath}|{Dimensions}|{Compression}";
        if (recipe != _loadedRecipe)
        {
            _decoded = null;
            _loadedRecipe = recipe;
            if (!Godot.FileAccess.FileExists(SourcePath))
            {
                if (!Engine.IsEditorHint())
                    throw new InvalidDataException($"Curated HUD texture is missing: {SourcePath}");
                return null;
            }
            _decoded = CuratedAyaTextureLoader.Load(SourcePath, Dimensions.X, Dimensions.Y,
                (CuratedAyaTextureLoader.Compression)Compression);
        }
        return _decoded;
    }

    public override int _GetWidth() => Dimensions.X;
    public override int _GetHeight() => Dimensions.Y;
    public override bool _HasAlpha() => true;
    public override Rid _GetRid() => Decoded()?.GetRid() ?? default;
    public override Image _GetImage() => Decoded()?.GetImage() ?? Image.CreateEmpty(1, 1, false, Image.Format.Rgba8);

    public override void _Draw(Rid canvasItem, Vector2 pos, Color modulate, bool transpose) =>
        Decoded()?.Draw(canvasItem, pos, modulate, transpose);

    public override void _DrawRect(Rid canvasItem, Rect2 rect, bool tile, Color modulate, bool transpose) =>
        Decoded()?.DrawRect(canvasItem, rect, tile, modulate, transpose);

    public override void _DrawRectRegion(Rid canvasItem, Rect2 rect, Rect2 srcRect,
        Color modulate, bool transpose, bool clipUv) =>
        Decoded()?.DrawRectRegion(canvasItem, rect, srcRect, modulate, transpose, clipUv);
}
