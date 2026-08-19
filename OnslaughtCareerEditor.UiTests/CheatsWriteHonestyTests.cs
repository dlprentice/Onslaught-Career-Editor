using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Cheats write still painted <c>CheatSaveWriteOutcome.Message</c>. An
/// input-rejection sentence can name a path. The page has to name the
/// file, or the refusal, without it.
/// </summary>
public class CheatsWriteHonestyTests
{
    [Test]
    public void AFailedWriteWithAPathUsesTheSharedFailureSentence()
    {
        var outcome = new CheatSaveWriteOutcome(
            false,
            @"No file exists at C:\Users\player\Documents\career.bes.",
            null);

        string sentence = CheatsPageText.DescribeWriteOutcome(outcome);

        Assert.That(sentence, Is.EqualTo(CheatSaveWriterService.WriteFailed));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("exception"));
    }

    [Test]
    public void ASuccessfulWriteNamesTheFileWithoutTheFolder()
    {
        string full = Path.Combine(
            "C:" + Path.DirectorySeparatorChar + "Users",
            "player",
            "GameProfiles",
            "copy",
            "savegames",
            "MALLOY.bes");
        var outcome = new CheatSaveWriteOutcome(
            true,
            $"Wrote MALLOY.bes. Dump leftover {full} Win32 error 5.",
            full);

        string sentence = CheatsPageText.DescribeWriteOutcome(outcome);

        Assert.That(sentence, Does.Contain("MALLOY.bes"));
        Assert.That(sentence, Does.Contain("not touched"));
        Assert.That(sentence, Does.Not.Contain(full));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("win32"));
    }

    [Test]
    public void TheWriteButtonUsesTheNamedSentenceInsteadOfTheOutcomeMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "CheatsPage.xaml.cs"));

        int start = code.IndexOf("CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write", StringComparison.Ordinal);
        int end = code.IndexOf("// ================================================================ live trainer", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("CheatsPageText.DescribeWriteOutcome"));
        Assert.That(method, Does.Not.Contain("outcome.Message"));
    }

    [Test]
    public void ASaveInsideACopyNamesTheProfileFolderNotARoot()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "CheatSaveWriterService.cs"));

        Assert.That(source, Does.Not.Contain("App-owned profiles root"));
        Assert.That(source, Does.Contain("\"app-owned profile folder\""));
    }
}
