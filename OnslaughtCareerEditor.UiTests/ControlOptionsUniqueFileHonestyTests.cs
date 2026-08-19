using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A failed unique sibling name used to dump the folder path
/// (`path in {directory}`). Name the folder, not a path.
/// </summary>
public class ControlOptionsUniqueFileHonestyTests
{
    [Test]
    public void AFailedUniqueNameDoesNotDumpTheFolderPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileControlOptionsService.cs"));

        Assert.That(source, Does.Not.Contain("path in {directory}"));
        Assert.That(source, Does.Contain("Could not make a unique {prefix}{extension} in that folder."));
    }
}
