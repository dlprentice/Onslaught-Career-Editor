using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A failed unique sibling name used to interpolate the prefix and extension
/// (`Could not make a unique {prefix}{extension} in that folder.`). Name the file.
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
        Assert.That(source, Does.Not.Contain("Could not make a unique {prefix}{extension} in that folder."));
        Assert.That(source, Does.Contain("UniqueFileCouldNotBeMade"));
        Assert.That(GameProfileControlOptionsService.UniqueFileCouldNotBeMade,
            Is.EqualTo("That file could not be created in that folder."));
        Assert.That(GameProfileControlOptionsService.UniqueFileCouldNotBeMade.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(GameProfileControlOptionsService.UniqueFileCouldNotBeMade.ToLowerInvariant(),
            Does.Not.Contain("prefix"));
    }
}
