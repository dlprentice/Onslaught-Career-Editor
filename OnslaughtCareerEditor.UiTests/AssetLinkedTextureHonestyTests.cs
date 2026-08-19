using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to say a linked or sidecar texture was unavailable.
/// Name the next step, the same leftover SidecarPreviewMissing already closed.
/// </summary>
public class AssetLinkedTextureHonestyTests
{
    [Test]
    public void AMissingLinkedTextureSaysWhatToDoNext()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));

        Assert.That(page, Does.Contain("AssetLibraryPageText.SidecarPreviewMissing"));
        Assert.That(page, Does.Not.Contain("no linked texture is available"));
        Assert.That(page, Does.Not.Contain("sidecar texture preview file is unavailable"));
        Assert.That(AssetLibraryPageText.SidecarPreviewMissing, Does.Contain("another export"));
        Assert.That(AssetLibraryPageText.SidecarPreviewMissing.ToLowerInvariant(), Does.Not.Contain("unavailable"));
        Assert.That(AssetLibraryPageText.SidecarPreviewMissing.ToLowerInvariant(), Does.Not.Contain("path"));
    }
}
