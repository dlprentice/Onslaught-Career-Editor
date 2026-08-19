using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// An empty player-mod list used to say none instead of the next step.
/// </summary>
public class PatchBenchPlayerModsHonestyTests
{
    [Test]
    public void AnEmptyPlayerModListSaysWhatToDoNext()
    {
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "PatchBenchSelectedProfileText.cs"));
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));

        Assert.That(helper, Does.Contain("No player mods on. Turn one on above."));
        Assert.That(helper, Does.Not.Contain("Player mods selected: none."));
        Assert.That(xaml, Does.Contain("No player mods on. Turn one on above."));
        Assert.That(xaml, Does.Not.Contain("Player mods selected: none."));
    }
}
