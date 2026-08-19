using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to label the leftover-texture button as a sidecar.
/// ViewLinkedTextureButton paints that label. Name the texture.
/// </summary>
public class AssetLibrarySidecarTexturePreviewButtonHonestyTests
{
    private const string PaintedSentence = "Preview texture";

    [Test]
    public void ALeftoverTextureButtonPaintsTheTextureNotASidecar()
    {
        string painted = InvokeSidecarTexturePreviewButtonLabel();

        Assert.That(painted, Is.EqualTo(PaintedSentence));
        Assert.That(painted.ToLowerInvariant(), Does.Contain("texture"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(painted, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheLinkedTextureButtonPaintsTheLeftoverTextureSentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));

        Assert.That(page, Does.Contain("ViewLinkedTextureButton.Content = _selectedModelLinkedTexture == null ? BuildSidecarTexturePreviewButtonLabel() : \"View linked texture\""));
        Assert.That(page, Does.Contain("Preview texture"));
        Assert.That(page, Does.Not.Contain("Preview sidecar texture"));
    }

    private static string InvokeSidecarTexturePreviewButtonLabel()
    {
        return (string)(GetRequiredPageMethod("BuildSidecarTexturePreviewButtonLabel")
            .Invoke(null, [])
            ?? throw new InvalidOperationException("AssetLibraryPage.BuildSidecarTexturePreviewButtonLabel returned null."));
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
