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

    [Test]
    public void AnEmptySaveListNamesTheFolderNotAPath()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SettingsPage.xaml.cs"));

        Assert.That(page, Does.Not.Contain("verify the selected install path."));
        Assert.That(page, Does.Contain("check the selected game folder."));
        Assert.That(page, Does.Not.Contain("Game directory not configured"));
        Assert.That(page, Does.Not.Contain("Set the game directory to enable save/options file detection."));
        Assert.That(page, Does.Contain("Game folder not set"));
        Assert.That(page, Does.Contain("Set the game folder to find save and options files."));
    }

    [Test]
    public void SettingsNamesTheFolderNotADirectory()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SettingsPage.xaml.cs"));

        Assert.That(page, Does.Not.Contain("No game directory set."));
        Assert.That(page, Does.Contain("No game folder set. Click Browse or Auto-Detect."));
        Assert.That(page, Does.Not.Contain("could not auto-detect the game directory"));
        Assert.That(page, Does.Contain("Settings: could not find the game folder"));
        Assert.That(page, Does.Not.Contain("failed to save game directory"));
        Assert.That(page, Does.Contain("Settings: could not keep that folder"));
        Assert.That(page, Does.Not.Contain("Settings: game directory updated"));
        Assert.That(page, Does.Contain("Settings: game folder updated"));
    }
}
