using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A catalog with two rows pointing at the same export used to say
/// "primary export paths". Name the exports.
/// </summary>
public class AssetCatalogUniqueExportHonestyTests
{
    [Test]
    public void ADuplicateExportNamesTheExportsNotAPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "AssetCatalogService.cs"));

        Assert.That(source, Does.Not.Contain("Asset catalog primary export paths must be unique."));
        Assert.That(source, Does.Contain("Asset catalog primary exports must be unique."));
    }
}
