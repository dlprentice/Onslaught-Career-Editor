using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The dedicated video window still appended the exception to its status
/// line. That put HRESULT and path text on a surface the player can read.
/// </summary>
public class VideoPlayerHonestyTests
{
    [Test]
    public void InitFailureSaysThePlayerCouldNotStartWithoutTheException()
    {
        string sentence = MediaPageText.DedicatedPlayerInitFailed;

        Assert.That(sentence, Does.Contain("could not start"));
        Assert.That(sentence, Does.Contain("Nothing was changed"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("exception"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("libvlc"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("{ex."));
    }

    [Test]
    public void TheDedicatedWindowUsesTheSharedSentenceAndNeverDumpsExMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "VideoPlayerWindow.xaml.cs"));

        Assert.That(code, Does.Contain("MediaPageText.DedicatedPlayerInitFailed"));
        Assert.That(code, Does.Not.Contain("ex.Message"));
        Assert.That(code, Does.Not.Contain("initialization failed"));
    }
}
