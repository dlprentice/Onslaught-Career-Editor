using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to say sidecar when leftover textures sat
/// beside a model export. ModelTextureLinksTextBlock paints that
/// non-zero summary. Name the texture.
/// </summary>
public class AssetLibrarySidecarPreviewFilesHonestyTests
{
    private const string PaintedSentence = "Texture preview files: 1/1.";

    [Test]
    public void APresentTexturePreviewPaintsTheTextureNotASidecar()
    {
        string painted = InvokeSidecarTextureSummary(sidecarCount: 1, bindingCount: 1);
        string composed = InvokeModelTextureLinkText(
            new AssetModelTextureLinks(["crate.png"], [], []),
            [new AssetModelSidecarTexture("crate.png", @"C:\exports\crate.png", true)]);

        Assert.That(painted, Is.EqualTo(PaintedSentence));
        Assert.That(painted.ToLowerInvariant(), Does.Contain("texture"));
        Assert.That(painted, Does.Contain("1/1"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(painted, Does.Not.Contain(@":\"));
        Assert.That(composed, Does.Contain(PaintedSentence));
        Assert.That(composed.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(composed, Does.Not.Contain(@"C:\exports\crate.png"));
    }

    [Test]
    public void ModelTextureLinksPaintTheTexturePreviewSummary()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));

        Assert.That(page, Does.Contain("ModelTextureLinksTextBlock.Text = BuildModelTextureLinkText"));
        Assert.That(page, Does.Contain("Texture preview files: {sidecarCount}/{bindingCount}."));
        Assert.That(page, Does.Not.Contain("Sidecar preview files: {sidecarCount}/{bindingCount}."));
        Assert.That(page, Does.Not.Contain("Sidecar preview files:"));
    }

    private static string InvokeSidecarTextureSummary(int sidecarCount, int bindingCount)
    {
        return (string)(GetRequiredPageMethod("BuildSidecarTextureSummary")
            .Invoke(null, [sidecarCount, bindingCount])
            ?? throw new InvalidOperationException("AssetLibraryPage.BuildSidecarTextureSummary returned null."));
    }

    private static string InvokeModelTextureLinkText(
        AssetModelTextureLinks links,
        AssetModelSidecarTexture[] sidecarTextures)
    {
        return (string)(GetRequiredPageMethod("BuildModelTextureLinkText")
            .Invoke(null, [links, sidecarTextures])
            ?? throw new InvalidOperationException("AssetLibraryPage.BuildModelTextureLinkText returned null."));
    }

    private static MethodInfo GetRequiredPageMethod(string methodName)
    {
        Type pageType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Pages.AssetLibraryPage",
            "OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml.cs");
        return pageType.GetMethod(methodName, BindingFlags.Static | BindingFlags.NonPublic)
            ?? throw new InvalidOperationException($"Missing AssetLibraryPage.{methodName}.");
    }
}
