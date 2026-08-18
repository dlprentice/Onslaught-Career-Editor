using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
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
        Assert.That(analyzer, Does.Contain("SaveLabPageText.DescribeOutputRefusal"));
        Assert.That(analyzer, Does.Not.Contain("ex.Message"));

        Assert.That(options, Does.Contain("SaveLabPageText.BrowseOptionsFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.ChooseOutputFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.BrowseCopySourceFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.LoadKeybindsFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.InputNotReady"));
        Assert.That(options, Does.Contain("SaveLabPageText.PatchFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.DescribeOutputRefusal"));
        Assert.That(options, Does.Not.Contain("ex.Message"));
    }

    [Test]
    public void AnInstalledOutputIsNamedAndBlocksTheWrite()
    {
        using var lab = new OutputLocationLab();
        lab.MakeInstalledGame();
        string output = lab.WriteFile("savegames", "career-out.bes");

        string? refusal = SaveLabPageText.DescribeOutputRefusal(output);
        Assert.That(refusal, Is.EqualTo(CareerSaveLocation.InstalledDestinationRefused));
        Assert.That(refusal, Does.Contain("installed game"));
        Assert.That(refusal, Does.Not.Contain(lab.Root));
        Assert.That(refusal, Does.Not.Contain(":\\"));
    }

    [Test]
    public void ANotYetCreatedOutputInsideTheInstalledGameStillBlocksTheWrite()
    {
        using var lab = new OutputLocationLab();
        lab.MakeInstalledGame();
        string savegames = Path.Combine(lab.Root, "savegames");
        Directory.CreateDirectory(savegames);
        string missing = Path.Combine(savegames, "new-career.bes");

        Assert.That(File.Exists(missing), Is.False);
        Assert.That(
            SaveLabPageText.DescribeOutputRefusal(missing),
            Is.EqualTo(CareerSaveLocation.InstalledDestinationRefused));
    }

    [Test]
    public void APlayableCopyOutputIsNotCalledTheInstalledGame()
    {
        using var lab = new OutputLocationLab();
        lab.MakeInstalledGame();
        lab.WriteText(GameProfilePreflightService.ProfileManifestFileName, "{}");
        string output = lab.WriteFile("savegames", "career-out.bes");

        Assert.That(SaveLabPageText.DescribeOutputRefusal(output), Is.Null);
    }

    [Test]
    public void AChosenFolderOutputIsNotCalledTheInstalledGame()
    {
        using var lab = new OutputLocationLab();
        string output = lab.WriteFile("Documents", "career-out.bes");

        Assert.That(SaveLabPageText.DescribeOutputRefusal(output), Is.Null);
    }

    private sealed class OutputLocationLab : IDisposable
    {
        public OutputLocationLab()
        {
            Root = Path.Combine(Path.GetTempPath(), $"bea-savelab-out-{Guid.NewGuid():N}");
            Directory.CreateDirectory(Root);
        }

        public string Root { get; }

        public void MakeInstalledGame()
        {
            Directory.CreateDirectory(Path.Combine(Root, "data"));
            File.WriteAllBytes(Path.Combine(Root, "BEA.exe"), new byte[16]);
        }

        public void WriteText(string relativePath, string contents)
        {
            string path = Path.Combine(Root, relativePath);
            string? dir = Path.GetDirectoryName(path);
            if (!string.IsNullOrWhiteSpace(dir))
                Directory.CreateDirectory(dir);
            File.WriteAllText(path, contents);
        }

        public string WriteFile(string folder, string fileName)
        {
            string dir = Path.Combine(Root, folder);
            Directory.CreateDirectory(dir);
            string path = Path.Combine(dir, fileName);
            File.WriteAllBytes(path, new byte[16]);
            return path;
        }

        public void Dispose()
        {
            try
            {
                if (Directory.Exists(Root))
                    Directory.Delete(Root, recursive: true);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
            }
        }
    }
}
