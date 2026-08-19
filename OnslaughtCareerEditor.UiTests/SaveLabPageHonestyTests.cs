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
            SaveLabPageText.SafeCopyInstallFailed,
            SaveLabPageText.SaveEditorPatchFailed,
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
        Assert.That(analyzer, Does.Contain("SaveLabPageText.SafeCopyInstallFailed"));
        Assert.That(analyzer, Does.Contain("SaveLabPageText.AnalysisNeedsAFile"));
        Assert.That(analyzer, Does.Not.Contain("No analysis yet"));
        Assert.That(analyzer, Does.Contain("SaveAnalyzerService.BuildInfoTitle"));
        Assert.That(analyzer, Does.Not.Contain("ex.Message"));
        Assert.That(analyzer, Does.Not.Contain("or .bea path"));
        Assert.That(analyzer, Does.Contain("SaveAnalyzerService.NoDetectedFilesNextStep"));
        Assert.That(analyzer, Does.Not.Contain("No detected files yet"));
        Assert.That(analyzer, Does.Not.Contain("No detected career saves yet"));

        Assert.That(options, Does.Contain("SaveLabPageText.BrowseOptionsFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.ChooseOutputFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.BrowseCopySourceFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.LoadKeybindsFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.InputNotReady"));
        Assert.That(options, Does.Contain("SaveLabPageText.PatchFailed"));
        Assert.That(options, Does.Contain("SaveLabPageText.DescribeOutputRefusal"));
        Assert.That(options, Does.Contain("SaveLabPageText.BuildOverwriteQuestion"));
        Assert.That(options, Does.Contain("SaveLabPageText.OverwriteCanceled"));
        Assert.That(options, Does.Contain("SaveAnalyzerService.NoDetectedFilesNextStep"));
        Assert.That(options, Does.Not.Contain("No detected options files yet"));
        Assert.That(options, Does.Not.Contain("ex.Message"));
        Assert.That(options, Does.Not.Contain("{request.OutputPath}"));

        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml"));
        Assert.That(xaml, Does.Contain(SaveAnalyzerService.NoDetectedFilesNextStep));
        Assert.That(xaml, Does.Not.Contain("No detected options files yet"));
    }

    [Test]
    public void AnalyzerMissingFileNamesTheFileNotAPath()
    {
        string sentence = SaveLabPageText.AnalysisNeedsAFile;

        Assert.That(sentence, Does.Contain(".bes"));
        Assert.That(sentence, Does.Contain(".bea"));
        Assert.That(sentence, Does.Contain("file"));
        Assert.That(sentence, Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
    }

    [Test]
    public void AnalyzerReadyNamesTheFileNotAPath()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs"));
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml"));

        const string ready =
            "Choose a detected file or browse for a .bes or .bea file to inspect save structure, options, and comparison data.";

        Assert.That(page, Does.Contain(ready));
        Assert.That(xaml, Does.Contain(ready));
        Assert.That(page, Does.Not.Contain("manual file path"));
        Assert.That(xaml, Does.Not.Contain("manual file path"));
    }

    [Test]
    public void EmptyDetectedListsNameTheFolderNotADirectory()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs"));
        string options = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.Configuration.cs"));

        Assert.That(page, Does.Not.Contain("Set the game directory in Settings or browse manually."));
        Assert.That(options, Does.Not.Contain("Set the game directory in Settings or browse manually."));
        Assert.That(page, Does.Contain("Set the game folder in Settings or browse manually."));
        Assert.That(options, Does.Contain("Set the game folder in Settings or browse manually."));

        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml"));
        Assert.That(xaml, Does.Not.Contain("changing the game directory in Settings"));
        Assert.That(xaml, Does.Contain("changing the game folder in Settings"));
    }

    [Test]
    public void GameOptionsOutputHintNamesTheFileNotAPath()
    {
        string options = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.Configuration.cs"));

        Assert.That(options, Does.Contain("The output file must remain a .bea / defaultoptions.bea file."));
        Assert.That(options, Does.Not.Contain("Output path must remain"));
    }

    [Test]
    public void OverwriteQuestionNamesTheFileNotThePath()
    {
        string path = Path.Combine(
            "C:" + Path.DirectorySeparatorChar + "Users",
            "player",
            "Documents",
            "defaultoptions.bea");
        string question = SaveLabPageText.BuildOverwriteQuestion(path);

        Assert.That(question, Does.Contain("defaultoptions.bea"));
        Assert.That(question, Does.Contain("cannot be undone"));
        Assert.That(question, Does.Not.Contain(path));
        Assert.That(question, Does.Not.Contain(":\\"));
        Assert.That(question, Does.Not.Contain("/"));
        Assert.That(SaveLabPageText.OverwriteCanceled, Does.Contain("Nothing was changed"));
        Assert.That(SaveLabPageText.OverwriteCanceled, Does.Not.Contain(":\\"));
    }

    [Test]
    public void PuttingASaveInASafeCopyDoesNotPaintTheWriteMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));

        int start = code.IndexOf("private async void SaveEditorInstallToSafeCopyButton_Click", StringComparison.Ordinal);
        int end = code.IndexOf("private void ShowInstallNote", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("SaveLabPageText.SafeCopyInstallFailed"));
        Assert.That(method, Does.Not.Contain("outcome.Message"));
    }

    [Test]
    public void ASaveEditorPatchDumpUsesTheSharedFailureSentence()
    {
        string dump = @"Could not write C:\Users\player\Documents\career.bes (Win32 error 5).";
        string sentence = SaveLabPageText.DescribeEditorPatchFailure(dump);

        Assert.That(sentence, Is.EqualTo(SaveLabPageText.SaveEditorPatchFailed));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("win32"));
        Assert.That(sentence, Does.Contain("Nothing was changed"));
    }

    [Test]
    public void TheSaveEditorPatchResultUsesTheNamedFailureSentence()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));

        int start = code.IndexOf("private static string FormatEditorPatchResultForUi", StringComparison.Ordinal);
        int end = code.IndexOf("private static string RedactEditorPatchPaths", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("SaveLabPageText.DescribeEditorPatchFailure"));
    }

    [Test]
    public void TheFocusedGoodiePatchResultUsesTheNamedFailureSentence()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));

        int start = code.IndexOf("private async void EditorPatchFocusedGoodieButton_Click", StringComparison.Ordinal);
        int end = code.IndexOf("private async void EditorPatchButton_Click", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("SaveLabPageText.DescribeEditorPatchFailure"));
    }

    [Test]
    public void AGameOptionsPatchDumpUsesTheSharedFailureSentence()
    {
        string dump = @"Could not write C:\Users\player\Documents\defaultoptions.bea (Win32 error 5).";
        string sentence = SaveLabPageText.DescribeConfigurationPatchFailure(dump);

        Assert.That(sentence, Is.EqualTo(SaveLabPageText.PatchFailed));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("win32"));
        Assert.That(sentence, Does.Contain("Nothing was changed"));
    }

    [Test]
    public void TheGameOptionsPatchResultUsesTheNamedFailureSentence()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.Configuration.cs"));

        int start = code.IndexOf("private static string FormatConfigurationPatchResultForUi", StringComparison.Ordinal);
        int end = code.IndexOf("private static string RedactConfigurationPatchPaths", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("SaveLabPageText.DescribeConfigurationPatchFailure"));
    }

    [Test]
    public void GameOptionsRefusalsNameTheFilesNotThePaths()
    {
        Assert.That(ConfigurationEditorService.PathsUnusable.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(ConfigurationEditorService.PathsUnusable, Does.Contain("Nothing was changed"));
        Assert.That(ConfigurationEditorService.PathsUnusable, Does.Contain("options files"));

        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "ConfigurationEditorService.cs"));

        Assert.That(source, Does.Not.Contain("input and output .bea paths"));
        Assert.That(source, Does.Not.Contain("input and output paths"));
        Assert.That(source, Does.Contain("Select both input and output files before patching."));
        Assert.That(source, Does.Contain("requires .bea/defaultoptions.bea"));
    }

    [Test]
    public void AFocusedGoodieBesPatcherRefusalNamesTheFilesNotPaths()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BesFilePatcher.cs"));

        Assert.That(source, Does.Contain("Goodie state patching requires .bes input and output files."));
        Assert.That(source, Does.Not.Contain("Goodie state patching requires .bes input and output paths."));
    }

    [Test]
    public void GameOptionsAsksBeforeItPatchesAndLeavesTheFileAloneOnCancel()
    {
        string options = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.Configuration.cs"));

        int confirm = options.IndexOf("SaveLabPageText.BuildOverwriteQuestion", StringComparison.Ordinal);
        int patch = options.IndexOf("ConfigurationEditorService.PatchConfiguration", StringComparison.Ordinal);
        int canceled = options.IndexOf("SaveLabPageText.OverwriteCanceled", StringComparison.Ordinal);

        Assert.That(confirm, Is.GreaterThanOrEqualTo(0));
        Assert.That(patch, Is.GreaterThan(confirm));
        Assert.That(canceled, Is.GreaterThan(confirm));
        Assert.That(canceled, Is.LessThan(patch));
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
