using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to say sidecar when a leftover texture existed
/// but its preview could not be opened. TexturePreviewEmptyTextBlock
/// paints that catch. Name the texture.
/// </summary>
public class AssetLibrarySidecarTexturePreviewUnreadableHonestyTests
{
    private const string PaintedSentence = "Texture exists, but the preview could not be opened.";

    [Test]
    public void AnUnreadableTexturePreviewPaintsTheTextureNotASidecar()
    {
        string painted = InvokeSidecarTexturePreviewUnreadable();

        Assert.That(painted, Is.EqualTo(PaintedSentence));
        Assert.That(painted.ToLowerInvariant(), Does.Contain("texture"));
        Assert.That(painted.ToLowerInvariant(), Does.Contain("preview could not be opened"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(painted, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TexturePreviewEmptyPaintsTheUnreadableTextureSentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));

        Assert.That(page, Does.Contain("TexturePreviewEmptyTextBlock.Text = BuildSidecarTexturePreviewUnreadable()"));
        Assert.That(page, Does.Contain("Texture exists, but the preview could not be opened."));
        Assert.That(page, Does.Not.Contain("Sidecar texture exists, but the preview could not be opened."));
    }

    private static string InvokeSidecarTexturePreviewUnreadable()
    {
        return (string)(GetRequiredPageMethod("BuildSidecarTexturePreviewUnreadable")
            .Invoke(null, [])
            ?? throw new InvalidOperationException("AssetLibraryPage.BuildSidecarTexturePreviewUnreadable returned null."));
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
