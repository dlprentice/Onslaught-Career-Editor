// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>DrawClickToStart retained unchanged from cf3ee02e. Only scene
/// section routing is removed; direct Godot drawing remains the pixel oracle.
/// CFEPIntro provenance and scalar laws stay in RetailClickToStart*.cs.</summary>
public sealed partial class ClickReference : Control
{
    private Texture2D _clickBackground = null!, _clickSlide = null!, _titleLogo = null!, _titleFont = null!;
    private int[] _glyphWidths = [];
    private double _clickPulseTimer, _clickPageSeconds;
    internal void Initialize()
    {
        _clickBackground = CuratedAyaTextureLoader.Load("res://Assets/Frontend/Backgrounds/click-to-start.texture.aya", 1024, 1024, CuratedAyaTextureLoader.Compression.Dxt1);
        _clickSlide = CuratedAyaTextureLoader.Load("res://Assets/Frontend/click-slide.texture.aya", 128, 128);
        _titleLogo = CuratedAyaTextureLoader.Load("res://Assets/Frontend/title-logo.texture.aya", 512, 256);
        _titleFont = CuratedAyaTextureLoader.Load("res://Assets/Hud/font-13ps.texture.aya", 256, 256, CuratedAyaTextureLoader.Compression.Rgba8);
        using Image image = _titleFont.GetImage();
        // Same scanner retained by LoadingReference, with the original font13 cell.
        _glyphWidths = (int[])typeof(LoadingReference).GetMethod("MeasureGlyphWidths",
            System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!.Invoke(null, [image, 16, 16])!;
        MouseFilter = MouseFilterEnum.Ignore;
        Size = new Vector2(640, 480);
        SetProcess(false); SetProcessInput(false);
    }
    internal void SetFrame(double timer, double seconds) { _clickPulseTimer = timer; _clickPageSeconds = seconds; QueueRedraw(); }
    internal Texture2D Font => _titleFont;
    internal Texture2D Splash => _clickBackground;
    internal Texture2D Slide => _clickSlide;
    internal Texture2D Title => _titleLogo;
    public override void _Draw() => DrawClickToStart();
    public override void _Notification(int what)
    {
        if (what != NotificationPredelete) return;
        _clickBackground?.Dispose(); _clickSlide?.Dispose(); _titleLogo?.Dispose(); _titleFont?.Dispose();
    }
    private static void SelectSceneSection(string _) { }
    private void DrawClickToStart()
    {
        // CFEPIntro::Render 0x0051B866 splash dest — DAT_0089d880 / fe_splash1.
        // Scale is min(this+0x18, 1.0) then the stored pulse; dest is the
        // specimen affine, not a scale-free (320, 240) centre.
        SelectSceneSection("Click.Splash");
        float splashScale = RetailClickToStartSplash.Scale(_clickPulseTimer);
        DrawSurfaceCentered(
            _clickBackground,
            RetailClickToStartSplash.X(_clickPulseTimer),
            RetailClickToStartSplash.Y(_clickPulseTimer),
            splashScale,
            splashScale,
            Colors.White);

        // CFEPIntro::Render 0x0051B92F glyph submits — Localization 0x77,
        // five CDXFont__DrawTextScaled calls at Y 401/399/400, sx=sy=1.
        // A capture-derived textScale=2 is not the body. ShouldDraw is the
        // same timer>4 / fmod<2 arm as RetailClickToStartPrompt.
        SelectSceneSection("Click.Prompt");
        if (RetailClickToStartGlyphs.ShouldDraw(_clickPulseTimer))
        {
            const string prompt = "Click to start"; // Localization 0x77
            int width = (int)MeasureText(prompt, RetailClickToStartGlyphs.ScaleX);
            foreach (RetailClickToStartGlyphs.Pass pass in RetailClickToStartGlyphs.Passes)
            {
                DrawTextFlat(
                    prompt,
                    new Vector2(RetailClickToStartGlyphs.X(pass, width), pass.Y),
                    RetailClickToStartGlyphs.ScaleX,
                    RetailColor(pass.Color));
            }
        }

        // DAT_0089d7bc LostToys sliding pair. No skip after the two byte
        // writes: both mode-0 CDXSurf calls issue even when this+0x18 <= 4
        // (the pair sits 400 px off the left edge). Fade is
        // clamp(timer-4, 0, 1); offset is (1-fade)²*400; dest X is
        // settled − offset.
        SelectSceneSection("Click.Slide");
        if (RetailClickToStartSlide.ShouldDraw(_clickPulseTimer))
        {
            foreach (RetailClickToStartSlide.Pass pass in RetailClickToStartSlide.Passes)
            {
                DrawTextureRect(
                    _clickSlide,
                    new Rect2(
                        RetailClickToStartSlide.X(pass, _clickPulseTimer),
                        pass.Y,
                        _clickSlide.GetWidth(),
                        _clickSlide.GetHeight()),
                    false,
                    RetailColor(pass.Color));
            }
        }

        // CFEPIntro::Render 0x0051BBA0 title slam — DAT_0089d88c / FE_BEA_Title2.
        // Gate is page*1.2 > 2; scale slams 2.5→0.5; four z=0.05 outline
        // corners then the z=0.04 body. The previous 0.35 / sin(page*3) stub
        // is not the specimen law.
        SelectSceneSection("Click.Title");
        if (RetailClickToStartTitle.ShouldDraw(_clickPageSeconds))
        {
            float titleScale = RetailClickToStartTitle.Scale(_clickPageSeconds);
            uint outline = RetailClickToStartTitle.OutlineColor(_clickPageSeconds);
            uint body = RetailClickToStartTitle.BodyColor(_clickPageSeconds);
            foreach (RetailClickToStartTitle.Pass pass in RetailClickToStartTitle.Passes)
            {
                DrawSurfaceCentered(
                    _titleLogo,
                    pass.X,
                    pass.Y,
                    titleScale,
                    titleScale,
                    RetailColor(pass.Outline ? outline : body));
            }
        }

        // CFEPIntro::Render 0x0051BD01 sixth z=0.02 copy. Second gate:
        // 2 < page < 2.25, not page*1.2 > 2. Dest (250, 290), sx=sy=1-v.
        // Not folded into Passes.
        SelectSceneSection("Click.TitleFlash");
        if (RetailClickToStartTitle.ShouldDrawSixth(_clickPageSeconds))
        {
            float sixthScale = RetailClickToStartTitle.SixthScale(_clickPageSeconds);
            DrawSurfaceCentered(
                _titleLogo,
                RetailClickToStartTitle.SixthPass.X,
                RetailClickToStartTitle.SixthPass.Y,
                sixthScale,
                sixthScale,
                RetailColor(RetailClickToStartTitle.SixthColor(_clickPageSeconds)));
        }
    }

    private void DrawSurfaceCentered(Texture2D texture, float x, float y, float sx, float sy, Color tint)
    {
        float width = texture.GetWidth() * sx, height = texture.GetHeight() * sy;
        DrawTextureRect(texture, new Rect2(x - width * 0.5f, y - height * 0.5f, width, height), false, tint);
    }
    private float MeasureText(string text, float scale)
    {
        float width = 0f;
        foreach (char character in text) width += (_glyphWidths[GlyphIndex(character)] + 1) * scale;
        return Mathf.Max(0f, width - scale);
    }
    private void DrawTextFlat(string text, Vector2 position, float scale, Color color)
    {
        float x = position.X;
        foreach (char character in text)
        {
            int glyph = GlyphIndex(character);
            float width = _glyphWidths[glyph] * scale;
            DrawTextureRectRegion(_titleFont, new Rect2(x, position.Y, width, 16 * scale),
                new Rect2(glyph % 16 * 16, glyph / 16 * 16, _glyphWidths[glyph], 16), color);
            x += width + scale;
        }
    }
    private static int GlyphIndex(char c) => (c is < (char)32 or >= (char)288 ? '?' : c) - 32;
    private static Color RetailColor(uint color) => new(((color >> 16) & 255) / 255f,
        ((color >> 8) & 255) / 255f, (color & 255) / 255f, (color >> 24) / 255f);
}
