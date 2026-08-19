using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to say sidecar after a leftover texture preview
/// loaded. The status bar paints that success path. Name the texture.
/// </summary>
public class AssetLibrarySidecarTexturePreviewStatusHonestyTests
{
    private const string PaintedSentence = "Asset Library: showing texture preview orphan_sidecar.png";

    [Test]
    public void ALoadedTexturePreviewStatusPaintsTheTextureNotASidecar()
    {
        string painted = InvokeSidecarTexturePreviewStatus("orphan_sidecar.png");

        Assert.That(painted, Is.EqualTo(PaintedSentence));
        Assert.That(painted.ToLowerInvariant(), Does.Contain("texture preview"));
        Assert.That(painted, Does.Contain("orphan_sidecar.png"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("previewing sidecar"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("sidecar texture"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(painted, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheStatusBarPaintsTheLoadedTexturePreviewSentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));

        Assert.That(page, Does.Contain("AppStatusService.SetStatus(BuildSidecarTexturePreviewStatus(_selectedModelSidecarTextureFileName))"));
        Assert.That(page, Does.Contain("Asset Library: showing texture preview {fileName}"));
        Assert.That(page, Does.Not.Contain("previewing sidecar texture"));
    }

    private static string InvokeSidecarTexturePreviewStatus(string fileName)
    {
        return (string)(GetRequiredPageMethod("BuildSidecarTexturePreviewStatus")
            .Invoke(null, [fileName])
            ?? throw new InvalidOperationException("AssetLibraryPage.BuildSidecarTexturePreviewStatus returned null."));
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
