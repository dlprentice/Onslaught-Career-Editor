using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Cheats live trainer still painted <c>LiveTrainerAttachOutcome.Message</c>.
/// For a failed <c>TryOpen</c> that string is the Win32 dump, and a path can
/// ride along. The page has to name the refusal instead.
/// </summary>
public class LiveTrainerAttachHonestyTests
{
    [Test]
    public void AFailedOpenNamesTheRefusalWithoutTheDump()
    {
        string sentence = LiveTrainerPageText.DescribeAttachRefusal(LiveTrainerAttachRefusal.CouldNotOpen);

        Assert.That(sentence, Is.EqualTo("Could not open that copied game. Nothing was read."));
        AssertSentenceIsPublicSafe(sentence);
    }

    [Test]
    public void EveryAttachRefusalIsNamedWithoutAPath()
    {
        foreach (LiveTrainerAttachRefusal refusal in Enum.GetValues<LiveTrainerAttachRefusal>())
        {
            if (refusal == LiveTrainerAttachRefusal.None)
                continue;

            string sentence = LiveTrainerPageText.DescribeAttachRefusal(refusal);
            Assert.That(sentence, Is.Not.Null.And.Not.Empty, $"{refusal} needs a named sentence.");
            AssertSentenceIsPublicSafe(sentence);
        }
    }

    [Test]
    public void TheWatchButtonUsesTheNamedRefusalInsteadOfTheAttachMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "CheatsPage.xaml.cs"));

        int start = code.IndexOf("private void LiveTrainerWatchButton_Click", StringComparison.Ordinal);
        int end = code.IndexOf("private void LiveTrainerStopWatchingButton_Click", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("LiveTrainerPageText.DescribeAttachRefusal"));
        Assert.That(method, Does.Not.Contain("outcome.Message"));
        Assert.That(method, Does.Not.Contain("Decision.Message"));
    }

    private static void AssertSentenceIsPublicSafe(string sentence)
    {
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("win32"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("exception"));
        Assert.That(sentence, Does.Not.Contain("0x"));
    }
}
