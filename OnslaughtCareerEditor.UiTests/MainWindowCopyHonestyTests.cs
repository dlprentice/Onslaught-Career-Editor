using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Review Setup and the close dialog used to call the safe copy an
/// app-owned workspace. Name the copy.
/// </summary>
public class MainWindowCopyHonestyTests
{
    [Test]
    public void ReviewSetupAndCloseNameTheCopyNotAnAppOwnedWorkspace()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "MainWindow.xaml.cs"));

        Assert.That(code, Does.Not.Contain("safe app-owned workspace behavior"));
        Assert.That(code, Does.Not.Contain("app-owned safe copy"));
        Assert.That(
            code,
            Does.Contain("Open Settings to review the configured install and the safe copy."));
        Assert.That(code, Does.Contain("it launched from a safe copy."));
    }
}
