using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Cheats live trainer still painted <c>LiveTrainerWriteOutcome.Message</c>.
/// A failed write-open is the Win32 dump. The page has to name the refusal
/// instead.
/// </summary>
public class LiveTrainerWriteHonestyTests
{
    [Test]
    public void AFailedWriteOpenNamesTheRefusalWithoutTheDump()
    {
        var outcome = new LiveTrainerWriteOutcome(
            false,
            "Could not open the game process for reading and writing (Win32 error 5).",
            LiveTrainerVital.Life,
            100f);

        string sentence = LiveTrainerPageText.DescribeWriteOutcome(outcome);

        Assert.That(sentence, Is.EqualTo("Could not open that copied game. Nothing was written."));
        AssertSentenceIsPublicSafe(sentence);
    }

    [Test]
    public void ASuccessfulWriteNamesTheValueWithoutTheOutcomeMessage()
    {
        var outcome = new LiveTrainerWriteOutcome(
            true,
            @"Set life to 100. C:\Games\BEA.exe Win32 error 0.",
            LiveTrainerVital.Life,
            100f);

        string sentence = LiveTrainerPageText.DescribeWriteOutcome(outcome);

        Assert.That(sentence, Is.EqualTo("Set life to 100."));
        AssertSentenceIsPublicSafe(sentence);
    }

    [Test]
    public void TheSetButtonUsesTheNamedWriteSentenceInsteadOfTheOutcomeMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "CheatsPage.xaml.cs"));

        int start = code.IndexOf("private void WriteLiveTrainerVital", StringComparison.Ordinal);
        int end = code.IndexOf("// ------------------------------------------------------------ trainer music", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("LiveTrainerPageText.DescribeWriteOutcome"));
        Assert.That(method, Does.Not.Contain("outcome.Message"));
    }

    [Test]
    public void AFailedProcessOpenDoesNotDumpWin32()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "LiveTrainerMemoryAccess.cs"));

        Assert.That(source, Does.Contain("Could not open that copied game."));
        Assert.That(source, Does.Not.Contain("Win32 error"));
        Assert.That(source, Does.Not.Contain("game process for"));
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
