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
}
