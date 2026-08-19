using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A media-only install used to name media/data. The other partial-install
/// sentence already says the data folder.
/// </summary>
public class SettingsPartialInstallHonestyTests
{
    [Test]
    public void AMediaOnlyInstallNamesTheDataFolderNotAPath()
    {
        string settings = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SettingsPage.xaml.cs"));

        int start = settings.IndexOf("GameDirectoryStatus.MediaOnly", StringComparison.Ordinal);
        int end = settings.IndexOf("GameDirectoryStatus.ExecutableOnly", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = settings[start..end];
        Assert.That(method, Does.Contain("the data folder is present"));
        Assert.That(method, Does.Contain("BEA.exe is missing"));
        Assert.That(method, Does.Not.Contain("media/data"));
        Assert.That(method, Does.Not.Contain(@":\"));
        Assert.That(settings, Does.Not.Contain("media/data"));
    }
}
