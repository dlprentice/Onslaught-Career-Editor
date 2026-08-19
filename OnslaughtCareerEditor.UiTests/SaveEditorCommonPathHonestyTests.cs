using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Editor titled the shared workflow "common path" and told the player
/// to keep that path explicit. Name the editor and the regions, not a path.
/// </summary>
public class SaveEditorCommonPathHonestyTests
{
    [Test]
    public void TheSaveEditorNamesTheEditorNotACommonPath()
    {
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml"));

        Assert.That(xaml, Does.Not.Contain("Save editor common path"));
        Assert.That(xaml, Does.Not.Contain("Keep the common path explicit"));
        Assert.That(xaml, Does.Contain("Title=\"Save Editor\""));
        Assert.That(xaml, Does.Contain("Choose only the save regions you want rewritten."));
    }
}
