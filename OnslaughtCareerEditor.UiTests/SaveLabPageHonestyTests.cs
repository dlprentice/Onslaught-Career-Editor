using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab and Game Options already named the failed action, then appended the
/// exception. That put full paths on the page. These sentences have to stay
/// complete without it.
/// </summary>
public class SaveLabPageHonestyTests
{
    [Test]
    public void FailureSentencesSayNothingWasChangedWithoutTheException()
    {
        string[] lines =
        {
            SaveLabPageText.ComparisonFailed,
            SaveLabPageText.AnalysisFailed,
            SaveLabPageText.BrowseOptionsFailed,
            SaveLabPageText.ChooseOutputFailed,
            SaveLabPageText.BrowseCopySourceFailed,
            SaveLabPageText.LoadKeybindsFailed,
            SaveLabPageText.PatchFailed,
        };

        foreach (string line in lines)
        {
            Assert.That(line, Does.Contain("Nothing was changed"));
            Assert.That(line, Does.Not.Contain(":\\"));
            Assert.That(line, Does.Not.Contain("0x"));
            Assert.That(line.ToLowerInvariant(), Does.Not.Contain("exception"));
            Assert.That(line, Does.Not.Contain("{ex."));
        }

        Assert.That(SaveLabPageText.InputNotReady, Does.Contain("not ready"));
        Assert.That(SaveLabPageText.InputNotReady, Does.Contain("defaultoptions.bea"));
        Assert.That(SaveLabPageText.InputNotReady, Does.Not.Contain(":\\"));
        Assert.That(SaveLabPageText.InputNotReady.ToLowerInvariant(), Does.Not.Contain("exception"));
    }

    [Test]
    public void ThePagesUseTheSharedSentencesAndNeverDumpExMessage()
    {
        string analyzer = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs"));
        string options = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.Configuration.cs"));

        Assert.That(analyzer, Does.Contain("SaveLabPageText.ComparisonFailed"));
        Assert.That(analyzer, Does.Contain("SaveLabPageText.AnalysisFailed"));
        Assert.That(analyzer, Does.Not.Contain("ex.Message"));

        Assert.That(options, Does.Contain("SaveLabPageText.BrowseOptionsFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.ChooseOutputFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.BrowseCopySourceFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.LoadKeybindsFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.InputNotReady"));
        Assert.That(options, Does.Contain("SaveLabPageText.PatchFailed"));
        Assert.That(options, Does.Not.Contain("ex.Message"));
    }
}
