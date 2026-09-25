// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Text.RegularExpressions;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the frontend page background as retail's THREE terms — clear, darkener,
/// FEBack128 video — so that a later "the frontend is showing the raw D3D clear
/// colour, make it flat" pass cannot delete the video underlay.
///
/// <para><b>This test exists because that pass was proposed.</b> Task #147
/// measured retail's main menu as 73.50% one flat colour (23,23,48) against our
/// 3.56%, measured our options root's modal as (31,32,63) — bit-identical to the
/// <c>Clear(0x001F1F3F)</c> immediate at <c>CDXFrontEnd__RenderStart</c>
/// VA 0x00540F88 in the pristine specimen <c>BEA.exe.original.backup</c>
/// (74154bfa) — and concluded we were letting the clear show through where
/// retail covers it. Every number in it reproduces. The conclusion does not.</para>
///
/// <para><b>Both retail references are <c>-skipfmv</c> captures.</b> That switch
/// suppresses the FEBack128 video, and the video is what covers the page. Retail
/// captured WITHOUT it
/// (<c>local-lab/retail-reference-pristine/nofmv-frontend-2026-07-26/</c>) is not
/// flat either — over run1's fifteen settled main-menu frames the modal colour
/// holds only 1.36%..3.57% of the frame across 34,795..39,593 distinct colours,
/// and <c>mm-t001020ms.png</c> reads modal (30,31,60) at 3.57% against our own
/// (30,31,60) at 3.56%. Retail's video-on frames also produce modal (31,32,63)
/// in their own right (<c>mm-t006031ms.png</c>, 2.17%), so the options-root
/// coincidence with the clear colour is the video composite's modal, not leaked
/// clear. The 73% flat frame is real and retail does render it — for the ~420 ms
/// before the video becomes visible, which is why retail's own
/// <c>mm-t000014ms.png</c> reads (23,23,48) at 80.08%.</para>
///
/// <para><b>What is asserted is the mechanism, not a pixel score.</b> The
/// #147 fix would have had to do one of exactly three things to make the page
/// flat: change the clear, change the darkener, or stop drawing the strip. One
/// test guards each, plus the gains, because zeroing those is the fourth way to
/// reach the same wrong place.</para>
/// </summary>
public sealed class RetailFrontendPageFillEvidenceTests
{
    /// <summary>
    /// Retail's page fill is two draws, and the reconstruction keeps them as two
    /// so that neither input can drift silently behind a baked answer.
    ///
    /// <para>Term 1 is <c>Clear(0x001F1F3F)</c> = RGB(31,31,63). Term 2 is draw 0
    /// of every frontend page: a full-screen quad, diffuse <c>0x3E000000</c>,
    /// SRCALPHA/INVSRCALPHA, whose stage-0 COLOROP is MODULATE(TEXTURE, DIFFUSE)
    /// with BLACK diffuse RGB and whose stage-0 ALPHAOP is DISABLE — so it is
    /// black at a flat 0x3E/255, whatever its texture holds
    /// (<c>G:\bea-frontend-pages\SWEEP-2026-07-27\inventories\main-menu-settled.csv</c>,
    /// frame 3000, draw 0).</para>
    ///
    /// <para>The arithmetic is the falsifiable part: it has to land on the
    /// (23,23,48) that retail's <c>-skipfmv</c> frames actually read.</para>
    /// </summary>
    [Fact]
    public void PageFillIsRetailsTwoTermsAndComposesToTheMeasuredFlatFill()
    {
        string source = NativeMainMenuSource.Read("frontend_underlay.gd");
        int[] clear = ParseByteColor(source, "CLEAR");
        Assert.Equal([31, 31, 63], clear);

        int darkenerAlpha = ParseDarkenerAlpha(source);
        Assert.Equal(0x3E, darkenerAlpha);

        // SRCALPHA/INVSRCALPHA of black over the clear, rounded as the device
        // rounds on the write to an 8-bit target.
        double keep = (255d - darkenerAlpha) / 255d;
        int[] composed = [.. clear.Select(c => (int)Math.Round(c * keep, MidpointRounding.AwayFromZero))];
        Assert.Equal([23, 23, 48], composed);

        // The baked constant the FEBack strip is added to must BE that composite.
        string composite = NativeMainMenuSource.Function("frontend_underlay.gd", "composite_tables");
        Assert.Equal(composed, ParseCompositeFill(composite));
        Assert.Contains("F.value(fill[channel] + F.value(gain[channel] * value))", composite, StringComparison.Ordinal);
        Assert.Contains("int(clampf(F.round_even(composed), 0.0, 255.0))", composite, StringComparison.Ordinal);
    }

    /// <summary>
    /// Every frontend page renderer composites the underlay. Retail draws the
    /// video on the non-main pages too: its own no-<c>-skipfmv</c> devselect
    /// frames (<c>run1/ds-t003507ms.png</c>) carry the video plainly, at 11,283
    /// to 13,174 distinct colours against a flat page's ~1.
    /// </summary>
    [Theory]
    [InlineData("DrawMainMenu")]
    [InlineData("DrawDevSelect")]
    [InlineData("DrawLevelSelect")]
    [InlineData("DrawOptions")]
    public void EveryFrontendPageRendererCompositesTheUnderlay(string renderer)
    {
        if (renderer is "DrawMainMenu" or "DrawDevSelect" or "DrawLevelSelect")
        {
            string body = NativeMainMenuSource.Function("main_menu_underlay.gd", "_draw");
            int clear = body.IndexOf("Underlay.CLEAR", StringComparison.Ordinal);
            int darkener = body.IndexOf("Underlay.DARKENER", StringComparison.Ordinal);
            int video = body.IndexOf("draw_texture_rect(_frames[Underlay.frame_index", StringComparison.Ordinal);
            Assert.True(clear >= 0 && darkener > clear && video > darkener);
            Assert.Contains("fe-back-128x128x30.rgb", NativeMainMenuSource.Read("frontend_underlay.gd"), StringComparison.Ordinal);
            if (renderer is "DrawDevSelect" or "DrawLevelSelect")
            {
                static string CareerSource(string name) => File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "godot-career-name-source", name));
                string underlay = CareerSource("career_name_underlay.gd");
                Assert.Contains("extends \"res://Scenes/Frontend/main_menu_underlay.gd\"", underlay, StringComparison.Ordinal);
                Assert.Contains("load_frames(1 if Engine.is_editor_hint() else 2147483647)", underlay, StringComparison.Ordinal);
                string controller = renderer == "DrawDevSelect" ? CareerSource("career_name_presentation.gd") : NativeLevelSelectSource.Controller;
                string scene = renderer == "DrawDevSelect" ? CareerSource("CareerName.tscn") : NativeLevelSelectSource.Scene;
                Assert.Contains("get_node(\"Background\").set_frame(1.0, facts.background_seconds)", controller, StringComparison.Ordinal);
                string background = NativeMainMenuSource.Node("Background", scene);
                AssertUsesCareerUnderlay(scene, background);
            }
            else
            {
                Assert.Contains("load_frames(1 if Engine.is_editor_hint() else 2147483647)", NativeMainMenuSource.Read("main_menu_underlay.gd"), StringComparison.Ordinal);
                Assert.Contains("get_node(\"Background\").set_frame(transition, facts.background_seconds)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
                Assert.Contains("recipe = ExtResource(\"underlay_recipe\")", NativeMainMenuSource.Node("Background"), StringComparison.Ordinal);
            }
            Assert.Contains("Color(31.0 / 255.0, 31.0 / 255.0, 63.0 / 255.0, 1.0)", NativeMainMenuSource.Read("frontend_underlay.gd"), StringComparison.Ordinal);
            Assert.Contains("Color(0.0, 0.0, 0.0, 62.0 / 255.0)", NativeMainMenuSource.Read("frontend_underlay.gd"), StringComparison.Ordinal);
            return;
        }
        if (renderer == "DrawOptions")
        {
            string scene = NativeOptionsSource.Read("Options.tscn");
            int clear = scene.IndexOf("[node name=\"Clear\"", StringComparison.Ordinal);
            int darkener = scene.IndexOf("[node name=\"Darkener\"", StringComparison.Ordinal);
            int video = scene.IndexOf("[node name=\"Video\"", StringComparison.Ordinal);
            Assert.True(clear >= 0 && darkener > clear && video > darkener);
            Assert.Contains("_frames[Underlay.frame_index", NativeOptionsSource.Function("options_presentation.gd", "set_frame"), StringComparison.Ordinal);
            Assert.Contains("underlay.load_frames(1)", NativeOptionsSource.Read("options_presentation.gd"), StringComparison.Ordinal);
            return;
        }
        throw new InvalidOperationException("No production underlay route is checked for " + renderer);
    }

    /// <summary>
    /// The underlay draws the strip, not just the flat fill. This is the exact
    /// edit #147 would have produced — keep the two fill rects, drop the video —
    /// and it is the one that has to stay red.
    /// </summary>
    [Fact]
    public void TheUnderlayDrawsTheFeBack128StripOverTheFill()
    {
        string body = NativeMainMenuSource.Function("main_menu_underlay.gd", "_draw");
        const string clearDraw = "draw_rect(Rect2(0.0, 0.0, 640.0, 480.0), Underlay.CLEAR)";
        const string darkenerDraw = "draw_rect(Rect2(-40.0, -3.0, 720.0, 486.0), Underlay.DARKENER)";
        const string stripDraw = "draw_texture_rect(_frames[Underlay.frame_index(_seconds, _frames.size())], Rect2(0.0, 0.0, 640.0, 480.0), false, Color(1.0, 1.0, 1.0, _alpha))";
        int clear = body.IndexOf(clearDraw, StringComparison.Ordinal);
        int darkener = body.IndexOf(darkenerDraw, StringComparison.Ordinal);
        int video = body.IndexOf(stripDraw, StringComparison.Ordinal);
        Assert.True(clear >= 0 && darkener > clear && video > darkener,
            "Production underlay must draw the clear, black darkener, then the selected composited FEBack frame.");
        string recipe = NativeMainMenuSource.Read("frontend_underlay.gd");
        Assert.Contains("var tables: Array[PackedByteArray] = composite_tables()", recipe, StringComparison.Ordinal);
        foreach (string channel in new[] { "pixels[index] = tables[0][pixels[index]]", "pixels[index + 1] = tables[1][pixels[index + 1]]", "pixels[index + 2] = tables[2][pixels[index + 2]]" })
            Assert.Contains(channel, recipe, StringComparison.Ordinal);
    }

    /// <summary>
    /// The additive gains stay inside the band the per-frame least-squares fits
    /// actually produced against retail's video-on main menu (run1 frames
    /// mm-t001020ms..mm-t007027ms, scored on the 222,683 pixels the
    /// <c>-skipfmv</c> capture proves are pure underlay). Zeroing these is the
    /// fourth route to a flat page and would leave every other assertion green.
    /// </summary>
    [Theory]
    [InlineData(0, 0.2523, 0.2687)]
    [InlineData(1, 0.2456, 0.2674)]
    [InlineData(2, 0.2290, 0.2467)]
    public void FeBackUnderlayGainStaysInsideTheMeasuredPerFrameBand(int channel, double low, double high)
    {
        string native = NativeOptionsSource.Function("frontend_underlay.gd", "composite_tables");
        Match match = Regex.Match(native, @"var gain: Array\[float\] = \[(?<values>[^\]]+)\]", RegexOptions.None, TimeSpan.FromSeconds(5));
        Assert.True(match.Success, "The production native gain declaration was not found.");
        double[] gains = Regex.Matches(match.Groups["values"].Value, @"F\.value\((?<value>[0-9.]+)\)", RegexOptions.None, TimeSpan.FromSeconds(5))
            .Select(m => double.Parse(m.Groups["value"].Value, CultureInfo.InvariantCulture)).ToArray();

        Assert.Equal(3, gains.Length);
        Assert.InRange(gains[channel], low, high);
    }

    /// <summary>Reads the production native Color's /255 declaration as bytes.</summary>
    private static int[] ParseByteColor(string source, string name)
    {
        Match match = Regex.Match(
            source,
            name + @"\s*:=\s*Color\(\s*(?<r>\d+)(?:\.0)?\s*/\s*255\.0\s*,\s*(?<g>\d+)(?:\.0)?\s*/\s*255\.0\s*,\s*(?<b>\d+)(?:\.0)?\s*/\s*255\.0\s*,\s*1\.0\s*\)",
            RegexOptions.None,
            TimeSpan.FromSeconds(5));
        Assert.True(match.Success, $"{name} was not declared as an opaque /255 byte colour.");

        return
        [
            int.Parse(match.Groups["r"].Value, CultureInfo.InvariantCulture),
            int.Parse(match.Groups["g"].Value, CultureInfo.InvariantCulture),
            int.Parse(match.Groups["b"].Value, CultureInfo.InvariantCulture),
        ];
    }

    /// <summary>Reads the production black darkener's alpha numerator as a byte.</summary>
    private static int ParseDarkenerAlpha(string source)
    {
        Match match = Regex.Match(
            source,
            @"DARKENER\s*:=\s*Color\(\s*0\.0\s*,\s*0\.0\s*,\s*0\.0\s*,\s*(?<a>\d+)(?:\.0)?\s*/\s*255\.0\s*\)",
            RegexOptions.None,
            TimeSpan.FromSeconds(5));
        Assert.True(match.Success, "Production DARKENER was not declared as black with a byte alpha over 255.");

        return int.Parse(match.Groups["a"].Value, CultureInfo.InvariantCulture);
    }

    private static int[] ParseCompositeFill(string source)
    {
        Match match = Regex.Match(
            source,
            @"var fill: Array\[int\] = \[(?<values>\d+\s*,\s*\d+\s*,\s*\d+)\]",
            RegexOptions.None,
            TimeSpan.FromSeconds(5));
        Assert.True(match.Success, "The production FEBack composite fill was not found.");
        return match.Groups["values"].Value.Split(',').Select(value => int.Parse(value.Trim(), CultureInfo.InvariantCulture)).ToArray();
    }

    private static void AssertUsesCareerUnderlay(string scene, string background)
    {
        Match script = Regex.Match(scene,
            @"\[ext_resource type=""Script"" path=""res://Scenes/Frontend/career_name_underlay\.gd"" id=""(?<id>[^""]+)""\]",
            RegexOptions.None, TimeSpan.FromSeconds(5));
        Assert.True(script.Success, "The page is missing its shared production underlay script.");
        Assert.Contains("script = ExtResource(\"" + script.Groups["id"].Value + "\")", background, StringComparison.Ordinal);
        Match recipe = Regex.Match(scene,
            @"\[ext_resource type=""Resource"" path=""res://Scenes/Frontend/FrontendUnderlay\.tres"" id=""(?<id>[^""]+)""\]",
            RegexOptions.None, TimeSpan.FromSeconds(5));
        Assert.True(recipe.Success, "The page is missing its shared production underlay recipe.");
        Assert.Contains("recipe = ExtResource(\"" + recipe.Groups["id"].Value + "\")", background, StringComparison.Ordinal);
    }
}
