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
}
