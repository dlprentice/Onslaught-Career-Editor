using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// An executable override outside the install used to say
/// "source game root". Name the file and the folder.
/// </summary>
public class PreflightExecutableFolderHonestyTests
{
    [Test]
    public void AnEscapedSourceExecutableNamesTheFolderNotARoot()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Not.Contain("Executable source must stay inside the source game root."));
        Assert.That(source, Does.Contain("That source executable must stay inside the game folder."));
    }
}
