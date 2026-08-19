using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A blank Asset Library path card used to say only that no file is
/// selected. Name the next step.
/// </summary>
public class AssetPathCardHonestyTests
{
    [Test]
    public void ABlankPathCardNamesTheNextStep()
    {
        string sentence = AssetLibraryPageText.BuildPathSummary(null);

        Assert.That(sentence, Is.EqualTo(AssetLibraryPageText.EmptyPathCardNextStep));
        Assert.That(sentence.ToLowerInvariant(), Does.Contain("choose"));
        Assert.That(sentence.ToLowerInvariant(), Does.Contain("file"));
        Assert.That(sentence, Does.Not.Contain("no file selected"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(AssetLibraryPageText.BuildPathSummary("   "), Is.EqualTo(sentence));
    }
}
