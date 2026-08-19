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
        Assert.That(code, Does.Contain("MediaPageText.AudioPlaybackFailedBody"));
        Assert.That(code, Does.Contain("MediaPageText.VideoPlaybackFailedStatus"));
        Assert.That(code, Does.Contain("MediaPageText.VideoPlaybackFailedBody"));
        Assert.That(code, Does.Contain("MediaPageText.StoryStartFailedStatus"));
        Assert.That(code, Does.Contain("MediaPageText.StoryContinueFailedStatus"));
        Assert.That(code, Does.Not.Contain("ex.Message"));
        Assert.That(code, Does.Not.Contain("Inline playback error."));
        Assert.That(code, Does.Not.Contain("Details:"));
        Assert.That(code, Does.Contain("MediaPageText.DescribeAudioEmptyState"));
        Assert.That(code, Does.Contain("MediaPageText.DescribeVideoEmptyState"));
        Assert.That(code, Does.Not.Contain("matches the current search"));
        Assert.That(code, Does.Not.Contain("No audio found in the current install"));
        Assert.That(code, Does.Not.Contain("No video found in the current install"));
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
    public void AnEmptyLibraryWithoutASearchSaysWhatToDoNext()
    {
        Assert.That(
            MediaPageText.DescribeAudioEmptyState(true, ""),
            Is.EqualTo(MediaPageText.EmptyLibraryNextStep));
        Assert.That(
            MediaPageText.DescribeVideoEmptyState(true, "   "),
            Is.EqualTo(MediaPageText.EmptyLibraryNextStep));
        Assert.That(MediaPageText.EmptyLibraryNextStep, Does.Contain("game folder"));
        Assert.That(MediaPageText.EmptyLibraryNextStep, Does.Contain("another folder"));
        Assert.That(MediaPageText.EmptyLibraryNextStep, Does.Not.Contain("No audio found"));
        Assert.That(MediaPageText.EmptyLibraryNextStep, Does.Not.Contain("No video found"));
        Assert.That(MediaPageText.EmptyLibraryNextStep, Does.Not.Contain(@":\"));
        Assert.That(MediaPageText.EmptyLibraryNextStep, Does.Not.Contain("/"));
        Assert.That(
            MediaPageText.DescribeAudioEmptyState(false, "music"),
            Does.Contain("not configured"));
        Assert.That(
            MediaPageText.DescribeAudioEmptyState(false, "music"),
            Is.EqualTo(MediaPageText.GameFolderNotConfigured));
        Assert.That(MediaPageText.GameFolderNotConfigured, Does.Contain("Browse Game Folder"));
        Assert.That(MediaPageText.GameFolderNotConfigured, Does.Not.Contain("Directory"));
    }

    [Test]
    public void AnUnsetInstallNamesTheFolderNotADirectory()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml.cs"));
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml"));

        Assert.That(code, Does.Contain("MediaPageText.GameFolderNotConfigured"));
        Assert.That(code, Does.Not.Contain("Game directory not set"));
        Assert.That(code, Does.Not.Contain("Set the game directory"));
        Assert.That(code, Does.Not.Contain("game directory not configured"));
        Assert.That(code, Does.Not.Contain("game directory selected"));
        Assert.That(code, Does.Not.Contain("Browse Game Directory"));
        Assert.That(xaml, Does.Not.Contain("Game directory not set"));
        Assert.That(xaml, Does.Not.Contain("current game directory"));
        Assert.That(xaml, Does.Not.Contain("Browse Game Directory"));
        Assert.That(xaml, Does.Contain("Browse Game Folder"));
        Assert.That(xaml, Does.Contain("current game folder"));
        Assert.That(xaml, Does.Not.Contain("Path details"));
        Assert.That(xaml, Does.Contain("Folder details"));
    }

    [Test]
    public void AGameFolderIsNamedByItsLeafNotThePath()
    {
        string path = @"C:\Games\Steam\steamapps\common\Battle Engine Aquila";
        string leaf = MediaPageText.BuildFolderSummary(path, "Configured install");

        Assert.That(leaf, Is.EqualTo("Battle Engine Aquila"));
        Assert.That(leaf, Does.Not.Contain(path));
        Assert.That(leaf, Does.Not.Contain(@":\"));
        Assert.That(leaf, Does.Not.Contain("/"));
        Assert.That(leaf, Does.Not.Contain("Games"));
        Assert.That(
            MediaPageText.BuildFolderSummary(@"C:\Games\Battle Engine Aquila\", "Configured install"),
            Is.EqualTo("Battle Engine Aquila"));
    }

    [Test]
    public void AMissingFolderFallsBackWithoutPrintingAPath()
    {
        Assert.That(MediaPageText.BuildFolderSummary("   ", "Configured install"), Is.EqualTo("Configured install"));
        Assert.That(MediaPageText.BuildFolderSummary(null, "Configured install"), Is.EqualTo("Configured install"));
        Assert.That(MediaPageText.DescribeDirectoryDetail(null), Does.Contain("folder"));
        Assert.That(MediaPageText.DescribeDirectoryDetail(null), Does.Not.Contain(@":\"));
        Assert.That(MediaPageText.DescribeDirectoryDetail(@"D:\Steam\common\BEA"), Is.EqualTo("BEA"));
    }

    [Test]
    public void ASelectedFileIsNamedByItsLeafNotThePath()
    {
        string path = @"C:\Games\Battle Engine Aquila\data\sound\briefing.ogg";
        string name = MediaPageText.BuildFileName(path, "that file");

        Assert.That(name, Is.EqualTo("briefing.ogg"));
        Assert.That(name, Does.Not.Contain(path));
        Assert.That(name, Does.Not.Contain(@":\"));
        Assert.That(name, Does.Not.Contain("Games"));
        Assert.That(MediaPageText.BuildFileName("   ", "that file"), Is.EqualTo("that file"));
    }

    [Test]
    public void ThePagePaintsTheFolderLeafNotThePath()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml.cs"));

        Assert.That(code, Does.Contain("MediaPageText.BuildFolderSummary"));
        Assert.That(code, Does.Contain("MediaPageText.DescribeDirectoryDetail"));
        Assert.That(code, Does.Contain("MediaPageText.BuildFileName"));
        Assert.That(code, Does.Not.Contain("MediaGameDirectoryTextBlock.Text = _snapshot.GameDirectory"));
        Assert.That(code, Does.Not.Contain("MediaGameDirectoryTextBlock.Text = path"));
        Assert.That(code, Does.Not.Contain(": fullPath;"));
    }

    [Test]
    public void AnInlinePlaybackFailureUsesTheSharedVideoSentence()
    {
        string sentence = MediaPageText.VideoPlaybackFailedBody;

        Assert.That(sentence, Does.Contain("could not be played"));
        Assert.That(sentence, Does.Contain("intact"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("exception"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("inline playback error"));
        Assert.That(sentence, Does.Not.Contain(@":\"));
        Assert.That(sentence, Does.Not.Contain("/"));

        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml.cs"));
        int start = code.IndexOf("private void VideoPlayer_EncounteredError", StringComparison.Ordinal);
        int end = code.IndexOf("private void VideoPlayer_LengthChanged", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("MediaPageText.VideoPlaybackFailedBody"));
        Assert.That(method, Does.Contain("MediaPageText.VideoPlaybackFailedStatus"));
        Assert.That(method, Does.Not.Contain("Inline playback error."));
        Assert.That(method, Does.Not.Contain("Media: video playback failed"));
    }

    [Test]
    public void AnAudioPlaybackFailureUsesTheSharedSentence()
    {
        string sentence = MediaPageText.AudioPlaybackFailedBody;

        Assert.That(sentence, Does.Contain("could not be played"));
        Assert.That(sentence, Does.Contain("intact"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("exception"));
        Assert.That(sentence, Does.Not.Contain(@":\"));
        Assert.That(sentence, Does.Not.Contain("/"));

        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml.cs"));
        Assert.That(code, Does.Contain("MediaPageText.AudioPlaybackFailedBody"));
        Assert.That(code, Does.Not.Contain("This audio track could not be played. Try another one"));
    }

    [Test]
    public void AnUnselectedTrackOrVideoSaysWhatToDoNext_RatherThanDescribingTheEmptiness()
    {
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml"));
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml.cs"));

        Assert.That(MediaPageText.NoTrackSelectedNextStep, Is.EqualTo("Choose a track."));
        Assert.That(MediaPageText.NoVideoSelectedNextStep, Is.EqualTo("Choose a video."));
        Assert.That(MediaPageText.NoTrackSelectedNextStep.ToLowerInvariant(), Does.Not.Contain("selected"));
        Assert.That(MediaPageText.NoVideoSelectedNextStep.ToLowerInvariant(), Does.Not.Contain("selected"));
        Assert.That(MediaPageText.NoTrackSelectedNextStep, Does.Not.Contain(@":\"));
        Assert.That(MediaPageText.NoVideoSelectedNextStep, Does.Not.Contain(@":\"));

        Assert.That(code, Does.Contain("MediaPageText.NoTrackSelectedNextStep"));
        Assert.That(code, Does.Contain("MediaPageText.NoVideoSelectedNextStep"));
        Assert.That(code, Does.Not.Contain("No track selected"));
        Assert.That(code, Does.Not.Contain("No video selected"));
        Assert.That(xaml, Does.Not.Contain("No track selected"));
        Assert.That(xaml, Does.Not.Contain("No video selected"));
        Assert.That(xaml, Does.Contain(MediaPageText.NoTrackSelectedNextStep));
        Assert.That(xaml, Does.Contain(MediaPageText.NoVideoSelectedNextStep));
    }
}
