using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Media already had a friendly load sentence, then appended the exception after
/// "Details:". That put full paths and HRESULT text on the page. These sentences
/// have to stay complete without the exception.
/// </summary>
public class MediaPageHonestyTests
{
    [Test]
    public void ALoadFailureSaysWhatHappenedWithoutTheException()
    {
        string sentence = MediaPageText.LoadFailureMessage;

        Assert.That(sentence, Does.Contain("Nothing was changed"));
        Assert.That(sentence, Does.Contain("game folder"));
        Assert.That(sentence, Does.Not.Contain("Details"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void AnUnavailableInlinePlayerSaysWhatToTryNext()
    {
        string sentence = MediaPageText.InlineVideoUnavailableBody;

        Assert.That(sentence, Does.Contain("could not start"));
        Assert.That(sentence, Does.Contain("intact"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("exception"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("libvlc"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
    }

    [Test]
    public void PlaybackStatusLinesDoNotCarryExceptionText()
    {
        string[] lines =
        {
            MediaPageText.AudioPlaybackFailedStatus,
            MediaPageText.VideoPlaybackFailedStatus,
            MediaPageText.StoryStartFailedStatus,
            MediaPageText.StoryContinueFailedStatus,
        };

        foreach (string line in lines)
        {
            Assert.That(line, Does.StartWith("Media:"));
            Assert.That(line.ToLowerInvariant(), Does.Contain("could not"));
            Assert.That(line, Does.Not.Contain("Details"));
            Assert.That(line, Does.Not.Contain("{ex."));
        }
    }

    [Test]
    public void ThePageUsesTheSharedSentencesAndNeverDumpsExMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml.cs"));

        Assert.That(code, Does.Contain("MediaPageText.LoadFailureMessage"));
        Assert.That(code, Does.Contain("MediaPageText.InlineVideoUnavailableBody"));
        Assert.That(code, Does.Contain("MediaPageText.AudioPlaybackFailedStatus"));
        Assert.That(code, Does.Contain("MediaPageText.VideoPlaybackFailedStatus"));
        Assert.That(code, Does.Contain("MediaPageText.StoryStartFailedStatus"));
        Assert.That(code, Does.Contain("MediaPageText.StoryContinueFailedStatus"));
        Assert.That(code, Does.Not.Contain("ex.Message"));
        Assert.That(code, Does.Not.Contain("Details:"));
        Assert.That(code, Does.Contain("MediaPageText.DescribeAudioEmptyState"));
        Assert.That(code, Does.Contain("MediaPageText.DescribeVideoEmptyState"));
        Assert.That(code, Does.Not.Contain("matches the current search"));
    }

    [Test]
    public void AnEmptySearchSaysWhatToDoNext_RatherThanDescribingTheEmptiness()
    {
        string audio = MediaPageText.DescribeAudioEmptyState(true, "no-such-track");
        string video = MediaPageText.DescribeVideoEmptyState(true, "no-such-cutscene");

        Assert.That(audio, Is.EqualTo(MediaPageText.EmptySearchNextStep));
        Assert.That(video, Is.EqualTo(MediaPageText.EmptySearchNextStep));
        Assert.That(audio, Does.Contain("another word"));
        Assert.That(audio, Does.Contain("clear the search"));
        Assert.That(audio, Does.Not.Contain("matches"));
        Assert.That(audio, Does.Not.Contain("no-such-track"));
        Assert.That(video, Does.Not.Contain("no-such-cutscene"));
    }

    [Test]
    public void AnEmptyLibraryWithoutASearchKeepsTheInstallLine()
    {
        Assert.That(
            MediaPageText.DescribeAudioEmptyState(true, ""),
            Does.Contain("No audio found"));
        Assert.That(
            MediaPageText.DescribeVideoEmptyState(true, "   "),
            Does.Contain("No video found"));
        Assert.That(
            MediaPageText.DescribeAudioEmptyState(false, "music"),
            Does.Contain("not configured"));
    }
}
