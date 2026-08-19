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

    [Test]
    public void AnEscapedCatalogFolderNamesTheFolderNotADirectory()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "AssetCatalogFileSafety.cs"));

        Assert.That(source, Does.Not.Contain("The asset catalog directory resolves outside"));
        Assert.That(source, Does.Contain("The asset catalog folder resolves outside the selected generated export folder."));
        Assert.That(source, Does.Not.Contain("directory resolves outside the selected generated export root."));
        Assert.That(source, Does.Contain("folder resolves outside the selected generated export folder."));
        Assert.That(source, Does.Not.Contain("The asset catalog file resolves outside the selected generated export root."));
        Assert.That(source, Does.Contain("The asset catalog file resolves outside the selected generated export folder."));
        Assert.That(source, Does.Not.Contain("{label} resolves outside the selected generated export root."));
        Assert.That(source, Does.Contain("{label} resolves outside the selected generated export folder."));
    }

    [Test]
    public void AMissingExportDoesNotAttachTheFilePath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "AssetCatalogFileSafety.cs"));

        Assert.That(source, Does.Not.Contain(
            "throw new FileNotFoundException(\"The catalog export file does not exist.\", Path);"));
        Assert.That(source, Does.Contain("That catalog export file could not be found."));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(\"That catalog export file could not be found.\","));
        Assert.That(source, Does.Not.Contain("\"Asset catalog path\""));
        Assert.That(source, Does.Not.Contain("\"Catalog export path\""));
        Assert.That(source, Does.Contain("\"Asset catalog\""));
        Assert.That(source, Does.Contain("\"Catalog export file\""));
    }
}
