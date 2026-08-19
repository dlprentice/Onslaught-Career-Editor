using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Music replacement used to say "Replacement OGG path".
/// Name the file, not a path.
/// </summary>
public class MusicReplacementOggHonestyTests
{
    [Test]
    public void AReplacementOggIsNamedWithoutCallingItAPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Not.Contain("Replacement OGG path is required."));
        Assert.That(source, Does.Not.Contain("Replacement OGG path must not be the target music file."));
        Assert.That(source, Does.Contain("A replacement OGG is required."));
        Assert.That(source, Does.Contain("The replacement OGG must not be the target music file."));
    }
}
