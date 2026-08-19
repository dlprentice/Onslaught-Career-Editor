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
        Assert.That(settings, Does.Not.Contain("Partial game directory detected"));
        Assert.That(settings, Does.Contain("Partial game folder detected"));
        Assert.That(settings, Does.Not.Contain("Valid game directory detected"));
        Assert.That(settings, Does.Contain("Valid game folder detected"));
        Assert.That(settings, Does.Contain("GameDirectoryIdentityText.SnapshotNeedsFullInstall"));
        Assert.That(settings, Does.Not.Contain("Choose the full install"));
        Assert.That(settings, Does.Not.Contain("Choose the full game folder"));
        Assert.That(settings, Does.Not.Contain("full BEA installation yet"));

        int executableStart = end;
        int executableEnd = settings.IndexOf("This does not look like", executableStart, StringComparison.Ordinal);
        Assert.That(executableStart, Is.GreaterThan(start));
        Assert.That(executableEnd, Is.GreaterThan(executableStart));
        string executableOnly = settings[executableStart..executableEnd];
        Assert.That(executableOnly, Does.Contain("GameDirectoryIdentityText.SnapshotNeedsFullInstall"));
        Assert.That(executableOnly, Does.Contain("the data folder is missing"));
        Assert.That(executableOnly, Does.Not.Contain("Choose the full game folder"));
    }
}
