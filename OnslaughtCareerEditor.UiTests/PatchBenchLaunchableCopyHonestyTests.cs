using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to call the safe copy an app-owned game copy.
/// Name the launchable copy.
/// </summary>
public class PatchBenchLaunchableCopyHonestyTests
{
    [Test]
    public void SafeGameCopyNamesTheLaunchableCopyNotAnAppOwnedGameCopy()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));

        Assert.That(page, Does.Not.Contain("launchable app-owned game copy"));
        Assert.That(
            page,
            Does.Contain("Create a launchable game copy. The app applies the verified 16:9 gameplay correction, writes the copied 16:9 display option, and launches the tested 1600x900 windowed baseline; selected mods are added too. Savegames are optional, and the installed game is unchanged."));
    }
}
