// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.RegularExpressions;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins DrawLoading to the measured full-width bar bbox from
/// <c>local-lab/retail-reference-pristine/loading/07-loading-640x480.png</c>
/// and forbids the rejected DrawBar-cap dest.
///
/// <para>28e6ad93 replaced the measured x78..562 y423..447 overlay with two
/// unmodulated 64x25 <c>DrawTextureRect</c> caps of FrontEnd\BarL/BarR. Those
/// files are CFrontEnd::DrawBar header masks, not this page's sprite:
/// CConsole__RenderLoadingScreen (0x0042C810) does not call DrawBar. The
/// capture is a continuous dark overlay, not two isolated end pieces.</para>
/// </summary>
public sealed class RetailFrontendLoadingBarTests
{
    private static readonly string FlowSource = File.ReadAllText(
        Path.Combine(AppContext.BaseDirectory, "godot-pause-source", "RetailFrontendFlow.cs"));
    private static readonly string ReferenceSource = NativeLoadingSource.Read("LoadingReference.cs");

    [Fact]
    public void DrawLoadingSpansTheMeasuredBarBboxAndDoesNotDrawDrawBarCaps()
    {
        string body = MethodBody(ReferenceSource, "DrawLoading");

        Assert.Contains(
            "new Rect2(LoadingBarLeft, LoadingBarTop, LoadingBarWidth, LoadingBarHeight)",
            body,
            StringComparison.Ordinal);
        Assert.Contains("Colors.Black", body, StringComparison.Ordinal);
        Assert.DoesNotContain("_loadingBarL", body, StringComparison.Ordinal);
        Assert.DoesNotContain("_loadingBarR", body, StringComparison.Ordinal);
        Assert.DoesNotContain("const float capWidth", body, StringComparison.Ordinal);

        string scene = NativeLoadingSource.Read("Loading.tscn");
        string bar = scene[scene.IndexOf("[node name=\"Bar\"", StringComparison.Ordinal)..];
        Assert.Contains("type=\"ColorRect\"", bar, StringComparison.Ordinal);
        Assert.Contains("offset_left = 78.0", bar, StringComparison.Ordinal);
        Assert.Contains("offset_top = 423.0", bar, StringComparison.Ordinal);
        Assert.Contains("offset_right = 563.0", bar, StringComparison.Ordinal);
        Assert.Contains("offset_bottom = 448.0", bar, StringComparison.Ordinal);
        Assert.Contains("color = Color(0, 0, 0, 1)", bar, StringComparison.Ordinal);
        Assert.DoesNotContain("bar-l", NativeLoadingSource.Presentation, StringComparison.Ordinal);
        Assert.DoesNotContain("bar-c", NativeLoadingSource.Presentation, StringComparison.Ordinal);
        Assert.DoesNotContain("bar-r", NativeLoadingSource.Presentation, StringComparison.Ordinal);
    }

    [Fact]
    public void DrawLoadingNamesRenderLoadingScreenAsOwnerAndDoesNotLoadDrawBarMasks()
    {
        Assert.Contains("CConsole__RenderLoadingScreen", ReferenceSource, StringComparison.Ordinal);
        Assert.Contains("0x0042C810", ReferenceSource, StringComparison.Ordinal);
        Assert.Contains("07-loading-640x480.png", ReferenceSource, StringComparison.Ordinal);
        Assert.Contains("KNOWN GAP", ReferenceSource, StringComparison.Ordinal);
        Assert.DoesNotContain("LoadTexture(\"bar-l\"", FlowSource, StringComparison.Ordinal);
        Assert.DoesNotContain("LoadTexture(\"bar-c\"", FlowSource, StringComparison.Ordinal);
        Assert.DoesNotContain("LoadTexture(\"bar-r\"", FlowSource, StringComparison.Ordinal);
    }

    [Fact]
    public void ProductionLoadingUsesAuthoredNativeCaptionAndSourceRecipes()
    {
        string scene = NativeLoadingSource.Read("Loading.tscn");
        Assert.Contains("[node name=\"Caption\" type=\"Node2D\"", scene, StringComparison.Ordinal);
        Assert.Contains("position = Vector2(270, 393.5)", scene, StringComparison.Ordinal);
        Assert.Equal(5, Regex.Matches(scene, "shadow = false", RegexOptions.None, TimeSpan.FromSeconds(5)).Count);
        Assert.Contains("FrontendFont22.tres", scene, StringComparison.Ordinal);
        Assert.Contains("LoadingBackground.tres", scene, StringComparison.Ordinal);
        Assert.Contains("source_path = \"res://Assets/Frontend/loading-screen.texture.aya\"", NativeLoadingSource.Read("LoadingBackground.tres"), StringComparison.Ordinal);
        Assert.Contains("compression = 0", NativeLoadingSource.Read("LoadingBackground.tres"), StringComparison.Ordinal);
        Assert.Contains("SOURCE_SHA256", NativeLoadingSource.Read("loading_strings.gd"), StringComparison.Ordinal);
        Assert.DoesNotContain("private void DrawLoading", FlowSource, StringComparison.Ordinal);
        Assert.DoesNotContain("_loadingScreen", FlowSource, StringComparison.Ordinal);
    }

    private static string MethodBody(string source, string methodName)
    {
        Match signature = Regex.Match(
            source,
            @"private\s+void\s+" + Regex.Escape(methodName) + @"\s*\([^)]*\)\s*\{",
            RegexOptions.None,
            TimeSpan.FromSeconds(5));
        Assert.True(signature.Success, $"{methodName} was not found as a private void method.");

        int open = source.IndexOf('{', signature.Index);
        int depth = 0;
        for (int index = open; index < source.Length; index++)
        {
            if (source[index] == '{')
            {
                depth++;
            }
            else if (source[index] == '}')
            {
                depth--;
                if (depth == 0)
                {
                    return source[open..(index + 1)];
                }
            }
        }

        throw new InvalidOperationException($"{methodName} has an unbalanced body.");
    }
}
