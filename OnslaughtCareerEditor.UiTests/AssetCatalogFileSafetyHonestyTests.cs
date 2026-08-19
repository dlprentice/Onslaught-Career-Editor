using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A catalog export that left the generated folder used to say
/// "Catalog export paths". Name the exports and the folder.
/// </summary>
public class AssetCatalogFileSafetyHonestyTests
{
    [Test]
    public void AnEscapedExportNamesTheFolderNotAPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "AssetCatalogFileSafety.cs"));

        Assert.That(source, Does.Not.Contain("Catalog export paths must remain below"));
        Assert.That(source, Does.Not.Contain("Catalog export paths must be bundle-root-relative."));
        Assert.That(source, Does.Contain("Catalog exports must stay inside the selected generated export folder."));
        Assert.That(source, Does.Contain("Catalog exports must be bundle-root-relative."));
    }

    [Test]
    public void ACatalogWithoutAParentNamesTheFolderNotADirectory()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "AssetCatalogFileSafety.cs"));

        Assert.That(source, Does.Not.Contain("has no containing directory."));
        Assert.That(source, Does.Contain("The asset catalog has no containing folder."));
        Assert.That(source, Does.Contain("has no containing folder."));
    }
}
