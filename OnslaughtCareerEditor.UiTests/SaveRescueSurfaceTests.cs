using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The Save Lab's way out of a safe copy.
///
/// The app could put a career into a copy and offered no way to get one back, while the only
/// deletion in the codebase was a recursive delete of the whole copy folder. That combination is
/// the one place in this design where somebody could lose something the game cannot make again,
/// so this suite pins the parts of the fix that a later refactor could quietly undo: the control
/// exists in the shipped markup, it goes through the guarded writer rather than a bare file copy,
/// it asks before replacing a file, and it never deletes.
/// </summary>
[TestFixture]
public class SaveRescueSurfaceTests
{
    private static string RepoRoot()
    {
        DirectoryInfo? directory = new(TestContext.CurrentContext.TestDirectory);
        while (directory is not null && !File.Exists(Path.Combine(directory.FullName, "package.json")))
            directory = directory.Parent;

        Assert.That(directory, Is.Not.Null, "Could not find the repository root.");
        return directory!.FullName;
    }

    private static string SavesPageXaml() =>
        File.ReadAllText(Path.Combine(RepoRoot(), "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml"));

    private static string SavesPageCode() =>
        File.ReadAllText(Path.Combine(RepoRoot(), "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs"));

    [Test]
    public void TheCardShipsInTheMarkupWithStableAccessibleIds()
    {
        string xaml = SavesPageXaml();

        foreach (string id in new[]
                 {
                     "SaveRescueCard",
                     "SaveRescueHeading",
                     "SaveRescueIntro",
                     "SaveRescueCopyComboBox",
                     "SaveRescueSaveComboBox",
                     "SaveRescueSelection",
                     "SaveRescueButton",
                     "SaveRescueRefreshButton",
                     "SaveRescueNote",
                 })
        {
            Assert.That(
                xaml,
                Does.Contain($"AutomationProperties.AutomationId=\"{id}\""),
                $"{id} is how this flow is driven and asserted on; it must stay in the markup.");
        }
    }

    /// <summary>
    /// The visible words live in the XAML and the same words live in the text helper, which is
    /// where the tests and any future code path read them from. Two copies of a sentence drift;
    /// this makes the drift fail here rather than in front of a player.
    /// </summary>
    [Test]
    public void TheVisibleWordsMatchTheTextHelperExactly()
    {
        string xaml = SavesPageXaml();

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain($"Text=\"{SaveRescuePageText.SectionTitle}\""));
            Assert.That(xaml, Does.Contain($"Text=\"{SaveRescuePageText.Introduction}\""));
            Assert.That(xaml, Does.Contain($"Content=\"{SaveRescuePageText.RescueButtonText}\""));
            Assert.That(xaml, Does.Contain($"Content=\"{SaveRescuePageText.RefreshButtonText}\""));
            Assert.That(
                xaml,
                Does.Contain($"AutomationProperties.Name=\"{SaveRescuePageText.RescueButtonAccessibleName}\""));
        });
    }

    /// <summary>
    /// WCAG 2.5.3. A screen reader user hearing one label and a sighted user reading another
    /// cannot talk to each other about the same button.
    /// </summary>
    [Test]
    public void TheAccessibleNameContainsTheVisibleLabel()
    {
        Assert.That(
            SaveRescuePageText.RescueButtonAccessibleName,
            Does.Contain(SaveRescuePageText.RescueButtonText));
    }

    [Test]
    public void TheRescueGoesThroughTheGuardedWriterAndNeverDeletes()
    {
        string code = SavesPageCode();

        Assert.Multiple(() =>
        {
            Assert.That(
                code,
                Does.Contain("SafeCopySaveRescueService.Rescue"),
                "Bringing a career out must reuse the guarded transaction, not a bare File.Copy.");
            Assert.That(
                code,
                Does.Contain("NeedsOverwriteConfirmation"),
                "Replacing a file in the destination has to be asked about, never silent.");
            Assert.That(
                code,
                Does.Contain("cannot be undone"),
                "The replace confirmation must say what it costs.");
            Assert.That(
                code,
                Does.Not.Contain("Directory.Delete"),
                "Nothing on this page deletes a safe copy. Rescue copies; the copy stays playable.");
            Assert.That(
                code,
                Does.Not.Contain("File.Move"),
                "A move would empty the copy the player is still using.");
        });
    }

    /// <summary>
    /// The button must not be live in the shipped markup. Enabling it is the code's job once a
    /// copy and a career are actually selected, and a control that is enabled before there is
    /// anything to act on is a control that can act on nothing.
    /// </summary>
    [Test]
    public void TheRescueButtonStartsSwitchedOff()
    {
        string xaml = SavesPageXaml();
        int start = xaml.IndexOf("x:Name=\"SaveRescueButton\"", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "The rescue button must be in the markup.");

        int end = xaml.IndexOf("/>", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start));

        Assert.That(xaml[start..end], Does.Contain("IsEnabled=\"False\""));
    }

    // ---------------------------------------------------------------- the wording

    [Test]
    public void WithNoCopiesTheSummarySaysWhereCopiesComeFrom()
    {
        string summary = SaveRescuePageText.BuildSelectionSummary(null, null);

        Assert.That(summary, Is.EqualTo(SaveRescuePageText.NoCopiesNote));
        Assert.That(summary, Does.Contain("Windowed & Mods"), "Naming the page is the whole point of the sentence.");
    }

    [Test]
    public void WithAnEmptyCopyTheSummaryNamesTheCopyRatherThanBlamingThePlayer()
    {
        var empty = new SafeCopySaveInventory(@"X:\copies\my-copy", "my-copy", Array.Empty<SafeCopySaveFile>());

        Assert.That(
            SaveRescuePageText.BuildSelectionSummary(empty, null),
            Is.EqualTo("my-copy has no careers in it yet."));
    }

    [Test]
    public void WithACareerChosenTheSummarySaysItIsACopyNotAMove()
    {
        var save = new SafeCopySaveFile("Maladim.bes", @"X:\copies\my-copy\savegames\Maladim.bes", "savegames", 10004, DateTime.UtcNow);
        var inventory = new SafeCopySaveInventory(@"X:\copies\my-copy", "my-copy", new[] { save });

        string summary = SaveRescuePageText.BuildSelectionSummary(inventory, save);

        Assert.That(summary, Does.Contain("Maladim"));
        Assert.That(summary, Does.Contain("my-copy"));
        Assert.That(
            summary,
            Does.Contain("does not take it away"),
            "Somebody has to be able to tell, before pressing it, that the copy stays playable.");
    }

    [Test]
    public void TheOutcomeNoteSaysWhereTheFileWentRatherThanJustSucceeding()
    {
        var result = new SafeCopySaveRescueResult(
            true,
            "Kept 1 save from my-copy.",
            @"D:\my careers",
            new[] { new SafeCopySaveRescueFileOutcome("Maladim.bes", true, @"D:\my careers\Maladim.bes", "Kept.") });

        Assert.That(SaveRescuePageText.BuildOutcomeNote(result), Does.Contain(@"D:\my careers"));
    }

    [Test]
    public void AFailedRescueReportsTheReasonItWasGivenAndInventsNothing()
    {
        var result = new SafeCopySaveRescueResult(
            false,
            "There is already a save called Maladim.bes in that folder.",
            @"D:\my careers",
            Array.Empty<SafeCopySaveRescueFileOutcome>());

        Assert.That(
            SaveRescuePageText.BuildOutcomeNote(result),
            Is.EqualTo("There is already a save called Maladim.bes in that folder."));
    }
}
