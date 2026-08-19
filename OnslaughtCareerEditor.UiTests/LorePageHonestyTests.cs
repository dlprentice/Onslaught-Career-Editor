using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Lore search used to say "Filtered results for" even when the tree was empty.
/// That describes a state the player can already see. The empty answer has to
/// say what to do next, and it must not pretend there are results.
/// </summary>
public class LorePageHonestyTests
{
    [Test]
    public void AnEmptySearchSaysWhatToDoNext_RatherThanDescribingTheEmptiness()
    {
        string sentence = LorePageText.DescribeSearchStatus("no-such-article", 0);

        Assert.That(sentence, Is.EqualTo(LorePageText.EmptySearchNextStep));
        Assert.That(sentence.Count(character => character == '.'), Is.EqualTo(1));
        Assert.That(sentence, Does.Contain("clear the search"));
        Assert.That(sentence, Does.Contain("another word"));
        Assert.That(sentence, Does.Not.Contain("yet").IgnoreCase);
        Assert.That(sentence, Does.Not.Contain("Filtered"));
        Assert.That(sentence, Does.Not.Contain("no-such-article"));
    }

    [Test]
    public void AHitKeepsTheExistingFilteredLineSoTheLiveSmokeStillHasAHandle()
    {
        string line = LorePageText.DescribeSearchStatus("Technology Lore", 3);

        Assert.That(line, Does.Contain("Filtered results for"));
        Assert.That(line, Does.Contain("Technology Lore"));
    }

    [Test]
    public void TheLibraryPaneUsesTheSharedSearchSentence()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml.cs"));

        Assert.That(code, Does.Contain("LorePageText.DescribeSearchStatus"));
        Assert.That(code, Does.Not.Contain("Filtered results for \\\"{query}\\\""));
    }

    [Test]
    public void ADocumentTooltipNamesTheFileNotTheFolder()
    {
        string tooltip = LorePageText.BuildDocumentTooltip(
            "The Book",
            "lore-book/BOOK.md",
            @"C:\Games\Battle Engine Aquila\lore\BOOK.md");

        Assert.That(tooltip, Is.EqualTo("BOOK.md"));
        Assert.That(tooltip, Does.Not.Contain("lore-book"));
        Assert.That(tooltip, Does.Not.Contain("/"));
        Assert.That(tooltip, Does.Not.Contain("\\"));
        Assert.That(tooltip, Does.Not.Contain(":\\"));
        Assert.That(tooltip, Does.Not.Contain("C:"));
    }

    [Test]
    public void ABlankRelativePathFallsBackToTheTitleThenTheSourceFile()
    {
        Assert.That(
            LorePageText.BuildDocumentTooltip("Start Here", "   ", null),
            Is.EqualTo("Start Here"));
        Assert.That(
            LorePageText.BuildDocumentTooltip(null, null, Path.Combine("C:" + Path.DirectorySeparatorChar, "lore", "Start-Here.md")),
            Is.EqualTo("Start-Here.md"));
        Assert.That(
            LorePageText.BuildDocumentTooltip("  ", "", ""),
            Is.EqualTo(LorePageText.DocumentTooltipFallback));
    }

    [Test]
    public void TheReaderUsesTheSharedTooltipAndDoesNotPaintTheRelativePath()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml.cs"));

        Assert.That(code, Does.Contain("LorePageText.BuildDocumentTooltip"));
        Assert.That(code, Does.Contain("LorePageText.DocumentTooltipFallback"));
        Assert.That(code, Does.Not.Contain("return document.RelativePath;"));
    }

    [Test]
    public void AnEmptyLibrarySaysWhatToDoNext_RatherThanDescribingTheEmptiness()
    {
        string sentence = LorePageText.EmptyLibraryNextStep;

        Assert.That(sentence, Does.Contain("Refresh"));
        Assert.That(sentence, Does.Contain("library"));
        Assert.That(sentence, Does.Not.Contain("did not produce"));
        Assert.That(sentence, Does.Not.Contain("no documents").IgnoreCase);
        Assert.That(sentence, Does.Not.Contain("/"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
    }

    [Test]
    public void TheEmptyLibraryPathUsesTheSharedNextStep()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml.cs"));

        Assert.That(code, Does.Contain("LorePageText.EmptyLibraryNextStep"));
        Assert.That(code, Does.Not.Contain("did not produce any readable documents"));
        Assert.That(code, Does.Not.Contain("did not return any readable files"));
        Assert.That(code, Does.Not.Contain("No documents found"));
    }

    [Test]
    public void AFailedDocumentOpenNamesTheActionNotTheSelection()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml.cs"));

        Assert.That(page, Does.Not.Contain("The selected Lore document could not be opened"));
        Assert.That(page, Does.Not.Contain("The selected Lore link could not be opened"));
        Assert.That(page, Does.Contain("LorePageText.DocumentLoadFailed"));
        Assert.That(page, Does.Contain("LorePageText.LinkOpenFailed"));
        Assert.That(LorePageText.DocumentLoadFailed, Does.Contain("could not be opened"));
        Assert.That(LorePageText.DocumentLoadFailed, Does.Contain("Refresh"));
        Assert.That(LorePageText.DocumentLoadFailed, Does.Not.Contain("The selected"));
        Assert.That(LorePageText.LinkOpenFailed, Does.Contain("could not be opened"));
        Assert.That(LorePageText.LinkOpenFailed, Does.Not.Contain("The selected"));
    }

    [Test]
    public void AMissingDocumentDoesNotAttachTheKey()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "LorePage.xaml.cs"));

        Assert.That(page, Does.Contain("throw new FileNotFoundException(LorePageText.DocumentLoadFailed)"));
        Assert.That(page, Does.Not.Contain("The selected lore document was not found."));
        Assert.That(page, Does.Not.Contain("FileNotFoundException(\"The selected lore document was not found.\", documentKey)"));
    }
}
