using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A missing quick-pick row used to interpolate the catalog key into Last
/// operation. That is an internal id, not something a player should see.
/// </summary>
public class PatchBenchPatchRowHonestyTests
{
    [Test]
    public void AMissingRowNamesTheRefusalWithoutTheCatalogKey()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "PatchBenchSafeCopyOutcomeText.cs"));

        Assert.That(helper, Does.Contain("That patch row is not available."));
        Assert.That(page, Does.Contain("PatchBenchSafeCopyOutcomeText.PatchRowUnavailable"));
        Assert.That(page, Does.Not.Contain("Patch row is not available: {key}"));
        Assert.That(helper, Does.Not.Contain("{key}"));
    }
}
