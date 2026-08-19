using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The live trainer reading line and Hold-stop still painted
/// <c>LiveTrainerReadResult.Message</c> / <c>LiveTrainerHoldTick.Message</c>.
/// Those strings are owned by AppCore and can change. The page has to name
/// the status instead.
/// </summary>
public class LiveTrainerReadingHonestyTests
{
    [Test]
    public void AReadingWithoutVitalsNamesTheStatusWithoutTheMessage()
    {
        var reading = new LiveTrainerReadResult(
            LiveTrainerReadStatus.NoMissionRunning,
            null,
            @"No mission. C:\Games\BEA.exe Win32 error 5.");

        string summary = LiveTrainerPageText.BuildReadingSummary(reading);
        string? blocked = LiveTrainerPageText.DescribeWhyWritingIsBlocked(true, reading);

        Assert.That(summary, Is.EqualTo(LiveTrainerPageText.DescribeReadStatus(LiveTrainerReadStatus.NoMissionRunning)));
        Assert.That(blocked, Is.EqualTo(summary));
        AssertSentenceIsPublicSafe(summary);
    }

    [Test]
    public void EveryReadStatusIsNamedWithoutAPath()
    {
        foreach (LiveTrainerReadStatus status in Enum.GetValues<LiveTrainerReadStatus>())
        {
            string sentence = LiveTrainerPageText.DescribeReadStatus(status);
            Assert.That(sentence, Is.Not.Null.And.Not.Empty, $"{status} needs a named sentence.");
            AssertSentenceIsPublicSafe(sentence);
        }
    }

    [Test]
    public void AHoldStopNamesTheReasonWithoutTheTickMessage()
    {
        var gone = new LiveTrainerHoldTick(
            new LiveTrainerReadResult(
                LiveTrainerReadStatus.ProcessGone,
                null,
                @"The copied game closed at C:\Games\BEA.exe (Win32 error 5)."),
            0,
            0,
            true,
            @"Holding stopped: C:\Games\BEA.exe");

        string sentence = LiveTrainerPageText.DescribeHoldStop(gone);

        Assert.That(sentence, Does.Contain("Holding stopped"));
        Assert.That(sentence, Does.Contain("no longer readable"));
        AssertSentenceIsPublicSafe(sentence);
    }

    [Test]
    public void TheHoldTickUsesTheNamedSentenceInsteadOfTheTickMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "CheatsPage.xaml.cs"));

        int start = code.IndexOf("private void LiveTrainerTick", StringComparison.Ordinal);
        int end = code.IndexOf("private void RefreshLiveTrainerControls", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("LiveTrainerPageText.DescribeHoldStop"));
        Assert.That(method, Does.Not.Contain("tick.Message"));
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
