using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods stop already used DescribeCaughtFailure in the catch, but
/// the OperationLog still painted result.Message. That string interpolated
/// ex.Message, which put full paths and Win32 text on the page.
/// </summary>
public class PatchBenchStopHonestyTests
{
    [Test]
    public void AFailedStopNamesTheActionWithoutTheException()
    {
        string sentence = GameProfileRuntimeService.StopFailed;

        Assert.That(sentence, Is.EqualTo("Could not stop that copied game. Nothing was changed."));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("exception"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("win32"));
    }

    [Test]
    public void TheStopServiceDoesNotInterpolateExMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileRuntimeService.cs"));

        Assert.That(code, Does.Contain("StopFailed"));
        Assert.That(code, Does.Not.Contain("{ex.Message}"));
        Assert.That(code, Does.Not.Contain("Stop requires a managed playable copied game folder process record."));
        Assert.That(code, Does.Contain("StopNeedsManagedCopy"));
        Assert.That(GameProfileRuntimeService.StopNeedsManagedCopy,
            Is.EqualTo("Stop needs a copy this app started."));
        Assert.That(GameProfileRuntimeService.StopNeedsManagedCopy.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(code, Does.Contain("StopWaitInvalid"));
        Assert.That(code, Does.Contain("CopyAlreadyGone"));
        Assert.That(code, Does.Contain("CopyNoLongerMatches"));
        Assert.That(code, Does.Contain("CopyExitedBeforeStop"));
        Assert.That(code, Does.Contain("CopyExitTimeUnread"));
        Assert.That(code, Does.Contain("CopyClosed"));
        Assert.That(code, Does.Contain("CopyDidNotExit"));
        Assert.That(code, Does.Contain("CopyStillRunning"));
        Assert.That(code, Does.Contain("CopyWasStopped"));
        Assert.That(code, Does.Not.Contain("Managed playable copied game folder process"));
        Assert.That(code, Does.Not.Contain("Could not stop managed playable copied game folder process"));
        Assert.That(code, Does.Not.Contain("Int32.MaxValue"));
        Assert.That(GameProfileRuntimeService.CopyAlreadyGone,
            Is.EqualTo("That copy was already gone."));
        Assert.That(GameProfileRuntimeService.CopyWasStopped,
            Is.EqualTo("That copy was stopped."));
        Assert.That(GameProfileRuntimeService.StopWaitInvalid.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfileRuntimeService.CopyNoLongerMatches.ToLowerInvariant(),
            Does.Not.Contain("record"));
    }

    [Test]
    public void ThePageStopLogUsesTheSharedSentencesInsteadOfResultMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));

        int start = code.IndexOf("private async void StopCopiedProfileButton_Click", StringComparison.Ordinal);
        int end = code.IndexOf("private async void StageMusicReplacementButton_Click", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("PatchBenchLaunchText.BuildBoundary(\"Managed safe copy process stopped.\")"));
        Assert.That(method, Does.Contain("PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure(\"stop the safe copy\")"));
        Assert.That(method, Does.Not.Contain("OperationLogTextBox.Text = result.Message"));
        Assert.That(method, Does.Not.Contain("{ex.Message}"));
    }

    [Test]
    public void StoppingWithNoProcessSaysWhatToDoNext()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "PatchBenchLaunchText.cs"));

        Assert.That(helper, Does.Contain("NoActiveCopiedGame"));
        Assert.That(helper, Does.Contain("Launch a safe copy first."));
        Assert.That(page, Does.Contain("PatchBenchLaunchText.NoActiveCopiedGame"));
        Assert.That(page, Does.Not.Contain("No managed safe copy process is active."));
    }
}
