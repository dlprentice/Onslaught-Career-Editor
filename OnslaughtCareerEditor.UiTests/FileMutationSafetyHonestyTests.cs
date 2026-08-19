using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// FileMutationSafety used to say "output paths" when a write would land
/// inside a Battle Engine Aquila game folder. Name the files.
/// </summary>
public class FileMutationSafetyHonestyTests
{
    [Test]
    public void AGameFolderWriteNamesTheFilesNotThePaths()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "FileMutationSafety.cs"));

        Assert.That(source, Does.Not.Contain("Output paths inside a Battle Engine Aquila game folder"));
        Assert.That(source, Does.Contain("Output files inside a Battle Engine Aquila game folder are blocked."));
        Assert.That(source, Does.Contain("Choose the app-owned patched-output folder or another non-game folder."));
    }
}
