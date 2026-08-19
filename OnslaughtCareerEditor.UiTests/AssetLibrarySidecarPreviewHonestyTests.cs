using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library status used to say sidecar when a leftover texture
/// preview could not be opened. Name the texture. The catch covers more
/// than one refusal, so do not invent a specific folder-check.
/// </summary>
public class AssetLibrarySidecarPreviewHonestyTests
{
    [Test]
    public void ARefusedSidecarPreviewPaintsTheTextureNotASidecar()
    {
        string exportFolder = Path.Combine(Path.GetTempPath(), $"bea-sidecar-preview-{Guid.NewGuid():N}");
        string texturePath = Path.Combine(exportFolder, "orphan_sidecar.png");
        Exception? refusal = null;
        try
        {
            AssetCatalogSourceAccessService.Open(
                AssetCatalogSnapshot.Empty,
                texturePath,
                "Selected model sidecar texture");
        }
        catch (Exception ex) when (
            ex is ArgumentException
            or IOException
            or InvalidOperationException
            or NotSupportedException
            or UnauthorizedAccessException)
        {
            refusal = ex;
        }

        string status = AssetLibraryPageText.SidecarPreviewRefused;

        Assert.That(refusal, Is.Not.Null);
        Assert.That(
            status,
            Is.EqualTo("Asset Library: that texture could not be opened."));
        Assert.That(status, Does.Contain("texture"));
        Assert.That(status.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(status.ToLowerInvariant(), Does.Not.Contain("trusted"));
        Assert.That(status.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(status.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(status, Does.Not.Contain(exportFolder));
        Assert.That(status, Does.Not.Contain(texturePath));
        Assert.That(status, Does.Not.Contain(":\\"));
        Assert.That(status, Does.Not.Contain("/"));
    }

    [Test]
    public void TheStatusBarPaintsTheRefusedTextureSentence()
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

        Assert.That(page, Does.Contain("AppStatusService.SetStatus(AssetLibraryPageText.SidecarPreviewRefused)"));
        Assert.That(helper, Does.Contain("Asset Library: that texture could not be opened."));
        Assert.That(helper, Does.Not.Contain("that sidecar texture could not be opened."));
        Assert.That(page, Does.Not.Contain("trusted-root"));
        Assert.That(page, Does.Not.Contain("failed trusted-root validation"));
    }
}
