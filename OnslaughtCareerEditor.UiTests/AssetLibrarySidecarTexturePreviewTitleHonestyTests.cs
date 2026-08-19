using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to title leftover texture previews as a
/// sidecar. PreviewTitleTextBlock paints that title. Name the texture.
/// </summary>
public class AssetLibrarySidecarTexturePreviewTitleHonestyTests
{
    private const string PaintedSentence = "Texture preview: orphan_sidecar.png";

    [Test]
    public void ATexturePreviewTitlePaintsTheTextureNotASidecar()
    {
        string painted = InvokeSidecarTexturePreviewTitle("orphan_sidecar.png");

        Assert.That(painted, Is.EqualTo(PaintedSentence));
        Assert.That(painted.ToLowerInvariant(), Does.Contain("texture preview"));
        Assert.That(painted, Does.Contain("orphan_sidecar.png"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("sidecar texture preview"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(painted, Does.Not.Contain(@":\"));
    }

    [Test]
    public void PreviewTitlePaintsTheTexturePreviewTitle()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));

        Assert.That(page, Does.Contain("PreviewTitleTextBlock.Text = BuildSidecarTexturePreviewTitle"));
        Assert.That(page, Does.Contain("Texture preview: {fileName}"));
        Assert.That(page, Does.Not.Contain("Sidecar texture preview: {_selectedModelSidecarTextureFileName}"));
        Assert.That(page, Does.Not.Contain("Sidecar texture preview:"));
    }

    private static string InvokeSidecarTexturePreviewTitle(string fileName)
    {
        return (string)(GetRequiredPageMethod("BuildSidecarTexturePreviewTitle")
            .Invoke(null, [fileName])
            ?? throw new InvalidOperationException("AssetLibraryPage.BuildSidecarTexturePreviewTitle returned null."));
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
