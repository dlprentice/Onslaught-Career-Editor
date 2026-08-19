using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A published package that landed elsewhere used to dump both folder
/// paths. Name the folder, not a path.
/// </summary>
public class PublishedPackageHonestyTests
{
    [Test]
    public void AMismatchedPackageFolderDoesNotDumpThePaths()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "FileMutationSafety.cs"));

        Assert.That(source, Does.Not.Contain("The published package path is no longer vacant."));
        Assert.That(source, Does.Not.Contain("The published package path is invalid."));
        Assert.That(source, Does.Not.Contain("The published package path appeared during publication."));
        Assert.That(source, Does.Not.Contain("{publishedPath}"));
        Assert.That(source, Does.Not.Contain("{physicalDestination}"));
        Assert.That(source, Does.Contain("The published package folder is no longer vacant."));
        Assert.That(source, Does.Contain("The published package folder is invalid."));
        Assert.That(source, Does.Contain("The published package folder appeared during publication."));
        Assert.That(source, Does.Contain("The published package folder did not stay in the expected place."));
    }
}
