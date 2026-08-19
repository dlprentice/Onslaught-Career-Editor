using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to say sidecar when leftover textures were
/// missing. The empty texture-link note and the missing-preview
/// status both paint that helper sentence. Name the texture.
/// </summary>
public class AssetLibrarySidecarPreviewMissingHonestyTests
{
    [Test]
    public void AMissingTexturePreviewPaintsTheTextureNotASidecar()
    {
        string painted = AssetLibraryPageText.SidecarPreviewMissing;

        Assert.That(
            painted,
            Is.EqualTo("Choose another export if you need a texture preview."));
        Assert.That(painted, Does.Contain("texture"));
        Assert.That(painted, Does.Contain("another export"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("unavailable"));
        Assert.That(painted.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(painted, Does.Not.Contain(":\\"));
        Assert.That(painted, Does.Not.Contain("/"));
    }

    [Test]
    public void ModelTextureLinksAndStatusPaintTheMissingTextureSentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "AssetLibraryPageText.cs"));

        Assert.That(page, Does.Contain("ModelTextureLinksTextBlock.Text = BuildModelTextureLinkText"));
        Assert.That(page, Does.Contain("? AssetLibraryPageText.SidecarPreviewMissing"));
        Assert.That(page, Does.Contain("AppStatusService.SetStatus(AssetLibraryPageText.SidecarPreviewMissing)"));
        Assert.That(helper, Does.Contain("Choose another export if you need a texture preview."));
        Assert.That(helper, Does.Not.Contain("Choose another export if you need a sidecar preview."));
        Assert.That(page, Does.Not.Contain("No sidecar preview file was found beside the export."));
    }
}
