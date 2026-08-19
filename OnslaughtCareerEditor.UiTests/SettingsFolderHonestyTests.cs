using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A remembered install folder that is gone used to say
/// <c>Directory does not exist</c> on the page and
/// <c>game directory path is invalid</c> in the status bar.
/// Name the folder, not a path.
/// </summary>
public class SettingsFolderHonestyTests
{
    [Test]
    public void AMissingFolderIsNamedWithoutCallingItAPath()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SettingsPage.xaml.cs"));

        Assert.That(page, Does.Contain("That folder is gone."));
        Assert.That(page, Does.Contain("Settings: that folder is gone"));
        Assert.That(page, Does.Not.Contain("Directory does not exist."));
        Assert.That(page, Does.Not.Contain("game directory path is invalid"));
    }
}
