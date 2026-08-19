using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A sidecar folder outside the generated exports used to say
/// "texture directory" and "export root". Name the folder.
/// </summary>
public class AssetModelSidecarHonestyTests
{
    [Test]
    public void AnEscapedSidecarFolderNamesTheFolderNotADirectory()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "AssetModelTextureLinkService.cs"));

        Assert.That(source, Does.Not.Contain("Model sidecar texture directory resolves outside"));
        Assert.That(
            source,
            Does.Contain("The model sidecar texture folder resolves outside the trusted generated export folder."));
    }

    [Test]
    public void ASidecarSnapshotNamesTheExportFolderNotATrustedRoot()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "AssetModelTextureLinkService.cs"));

        Assert.That(source, Does.Not.Contain("Trusted asset export root"));
        Assert.That(source, Does.Contain("\"generated export folder\""));
    }
}
