using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab focused Goodie SUCCESS still tells the player the output
/// is staged in a verified copy's savegames folder. EditorInfoBar and
/// EditorOutputTextBox both paint that sentence. Name the copy.
/// </summary>
public class SaveLabGoodieSuccessSavegamesFolderHonestyTests
{
    private const string PaintedSentence =
        "If this destination is a Safe Game Copy, the output is staged only in that copy's savegames folder.";

    [Test]
    public void FocusedGoodieSuccessPaintsTheCopyNotAVerifiedCopy()
    {
        string success = ExtractSuccessDisplayMessage();

        Assert.That(success, Does.Contain(PaintedSentence));
        Assert.That(success, Does.Contain("that copy's savegames folder"));
        Assert.That(success, Does.Not.Contain("verified copy"));
        Assert.That(success, Does.Not.Contain("verified profile"));
        Assert.That(success, Does.Not.Contain("app-owned"));
        Assert.That(success, Does.Not.Contain(":\\"));
    }

    [Test]
    public void EditorInfoBarAndOutputPaintTheSuccessDisplayMessage()
    {
        string handler = ExtractFocusedGoodieClickHandler();

        Assert.That(handler, Does.Contain("string displayMessage = result.Success"));
        Assert.That(handler, Does.Contain(PaintedSentence));
        Assert.That(handler, Does.Contain("EditorOutputTextBox.Text = displayMessage;"));
        Assert.That(handler, Does.Contain("EditorInfoBar.Message = displayMessage;"));
        Assert.That(handler, Does.Not.Contain("verified copy"));
    }

    private static string ExtractSuccessDisplayMessage()
    {
        string handler = ExtractFocusedGoodieClickHandler();
        const string startMark = "string displayMessage = result.Success";
        int start = handler.IndexOf(startMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "Focused Goodie success displayMessage is missing.");

        int end = handler.IndexOf("EditorOutputTextBox.Text = displayMessage;", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Focused Goodie success displayMessage has no paint.");
        return handler[start..end];
    }

    private static string ExtractFocusedGoodieClickHandler()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));
        const string startMark = "private async void EditorPatchFocusedGoodieButton_Click";
        int start = page.IndexOf(startMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "Focused Goodie click handler is missing.");

        const string endMark = "private async void EditorPatchButton_Click";
        int end = page.IndexOf(endMark, start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Focused Goodie click handler has no end.");
        return page[start..end];
    }
}
