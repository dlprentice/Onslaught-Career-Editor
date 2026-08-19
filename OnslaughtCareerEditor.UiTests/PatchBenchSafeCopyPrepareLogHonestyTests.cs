using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Last operation used to say the safe copy was
/// prepared in an app-owned GameProfiles workspace. Name the copy.
/// </summary>
public class PatchBenchSafeCopyPrepareLogHonestyTests
{
    [Test]
    public void PreparingLogNamesTheSafeCopyNotAnAppOwnedGameProfilesWorkspace()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));

        Assert.That(page, Does.Not.Contain("app-owned GameProfiles workspace"));
        Assert.That(
            page,
            Does.Contain("Preparing a safe game copy. The selected Steam/game install stays unchanged."));
    }
}
