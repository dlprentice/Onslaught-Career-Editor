using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to say sidecar while a leftover texture preview
/// was loading. TexturePreviewEmptyTextBlock paints that loading path.
/// Name the texture.
/// </summary>
public class AssetLibrarySidecarTexturePreviewLoadingHonestyTests
{
    private const string PaintedSentence = "Loading texture preview...";

    [Test]
    public void ALoadingTexturePreviewPaintsTheTextureNotASidecar()
    {
        string painted = InvokeSidecarTexturePreviewLoading();

        Assert.That(painted, Is.EqualTo(PaintedSentence));
        Assert.That(painted.ToLowerInvariant(), Does.Contain("texture preview"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(painted, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TexturePreviewEmptyPaintsTheLoadingTextureSentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));

        Assert.That(page, Does.Contain("TexturePreviewEmptyTextBlock.Text = BuildSidecarTexturePreviewLoading()"));
        Assert.That(page, Does.Contain("Loading texture preview..."));
        Assert.That(page, Does.Not.Contain("Loading sidecar texture preview..."));
    }

    private static string InvokeSidecarTexturePreviewLoading()
    {
        return (string)(GetRequiredPageMethod("BuildSidecarTexturePreviewLoading")
            .Invoke(null, [])
            ?? throw new InvalidOperationException("AssetLibraryPage.BuildSidecarTexturePreviewLoading returned null."));
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
