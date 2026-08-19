using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab asked "overwrite this file?" and then printed the full output
/// path. The question has to name the file and say the replace cannot be
/// undone, without the folder.
/// </summary>
public class SaveLabOverwriteHonestyTests
{
    [Test]
    public void TheOverwriteQuestionNamesTheFileNotTheFolder()
    {
        string path = @"C:\Games\Battle Engine Aquila\savegames\career-out.bes";
        string question = SaveLabPageText.BuildOverwriteQuestion(path);

        Assert.That(question, Does.Contain("career-out.bes"));
        Assert.That(question, Does.Contain("cannot be undone"));
        Assert.That(question, Does.Not.Contain(path));
        Assert.That(question, Does.Not.Contain(":\\"));
        Assert.That(question, Does.Not.Contain("/"));
        Assert.That(question, Does.Not.Contain("Games"));
        Assert.That(question.ToLowerInvariant(), Does.Not.Contain("nothing was changed"));
    }

    [Test]
    public void AMissingNameStillDoesNotPrintAPath()
    {
        string question = SaveLabPageText.BuildOverwriteQuestion("   ");

        Assert.That(question, Does.Contain("That file"));
        Assert.That(question, Does.Contain("cannot be undone"));
        Assert.That(question, Does.Not.Contain(":\\"));
        Assert.That(question, Does.Not.Contain("/"));
    }

    [Test]
    public void TheEditorConfirmUsesTheSharedQuestionAndDoesNotDumpThePath()
    {
        string editor = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs"));

        Assert.That(editor, Does.Contain("SaveLabPageText.BuildOverwriteQuestion"));
        Assert.That(editor, Does.Contain("SaveLabPageText.OverwriteCanceled"));
        Assert.That(editor, Does.Not.Contain("The output file already exists"));
        Assert.That(editor, Does.Not.Contain("{outputPath}"));

        int firstConfirm = editor.IndexOf("SaveLabPageText.BuildOverwriteQuestion", StringComparison.Ordinal);
        int secondConfirm = editor.IndexOf("SaveLabPageText.BuildOverwriteQuestion", firstConfirm + 1, StringComparison.Ordinal);
        int firstCanceled = editor.IndexOf("SaveLabPageText.OverwriteCanceled", StringComparison.Ordinal);
        int secondCanceled = editor.IndexOf("SaveLabPageText.OverwriteCanceled", firstCanceled + 1, StringComparison.Ordinal);
        Assert.That(secondConfirm, Is.GreaterThan(firstConfirm));
        Assert.That(firstCanceled, Is.GreaterThan(firstConfirm));
        Assert.That(firstCanceled, Is.LessThan(secondConfirm));
        Assert.That(secondCanceled, Is.GreaterThan(secondConfirm));
        Assert.That(editor, Does.Not.Contain("already exists in"));
        Assert.That(editor, Does.Contain("It is in {target.DisplayName}"));
    }
}
