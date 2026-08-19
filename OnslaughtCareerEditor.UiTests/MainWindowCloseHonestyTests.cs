using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Canceling close while a copied game is running used to say
/// <c>Close canceled</c>. Reuse the Windowed &amp; Mods sentence.
/// </summary>
public class MainWindowCloseHonestyTests
{
    [Test]
    public void ACanceledCloseNamesTheRunningCopy()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "MainWindow.xaml.cs"));

        Assert.That(code, Does.Not.Contain("Close canceled: copied game still running"));
        Assert.That(code, Does.Contain("Safe copy is still running."));
        Assert.That(code, Does.Not.Contain("Close canceled"));
    }
}
