using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods restore already used DescribeCaughtFailure in the catch,
/// but the OperationLog still painted result.Message. That string is the
/// internal "playable copied game folder" sentence.
/// </summary>
public class PatchBenchMusicRestoreHonestyTests
{
    private static readonly string[] ReflectedSafeCopyOutcomeSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyOutcomeTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyControlOptionsTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyMusicSwapTextState.cs",
    ];

    [Test]
    public void ARestoredBackupNamesTheFileWithoutInternalJargon()
    {
        string sentence = InvokeString("BuildMusicRestoreOperationLog", "BEA_01(Master).ogg", true);

        Assert.That(sentence, Does.Contain("BEA_01(Master).ogg"));
        Assert.That(sentence, Does.Contain("restored"));
        Assert.That(sentence, Does.Contain("original install stays unchanged"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("playable copied"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("manifest"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void AFailedRestoreUsesTheSharedFailureSentence()
    {
        string sentence = InvokeString("BuildMusicRestoreOperationLog", "BEA_01(Master).ogg", false);

        Assert.That(
            sentence,
            Is.EqualTo("Could not restore the safe-copy music backup. Nothing was changed."));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("0x"));
    }

    [Test]
    public void ARestoredBackupUsesOnlyTheFileName()
    {
        string full = Path.Combine(
            "C:" + Path.DirectorySeparatorChar + "Users",
            "player",
            "GameProfiles",
            "copy",
            "data",
            "Music",
            "BEA_01(Master).ogg");
        string sentence = InvokeString("BuildMusicRestoreOperationLog", full, true);

        Assert.That(sentence, Does.Contain("BEA_01(Master).ogg"));
        Assert.That(sentence, Does.Contain("original install stays unchanged"));
        Assert.That(sentence, Does.Not.Contain(full));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("Users"));
        Assert.That(sentence, Does.Not.Contain("GameProfiles"));
    }

    [Test]
    public void ABlankNameFallsBackToThatTrack()
    {
        string sentence = InvokeString("BuildMusicRestoreOperationLog", "   ", true);

        Assert.That(sentence, Does.Contain("that track"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void ThePageRestoreLogUsesTheSharedSentencesInsteadOfResultMessage()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));

        int start = code.IndexOf("private async void RestoreMusicReplacementButton_Click", StringComparison.Ordinal);
        int end = code.IndexOf("private void SetSourceExecutablePath", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("PatchBenchSafeCopyOutcomeText.BuildMusicRestoreOperationLog"));
        Assert.That(method, Does.Contain("PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure(\"restore the safe-copy music backup\")"));
        Assert.That(method, Does.Not.Contain("OperationLogTextBox.Text = result.Message"));
        Assert.That(method, Does.Not.Contain("{ex.Message}"));
        Assert.That(method, Does.Not.Contain("Playable copied game folder"));
    }

    private static string InvokeString(string methodName, params object?[] arguments)
    {
        return (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            GetHelperType(),
            methodName,
            arguments);
    }

    private static Type GetHelperType()
    {
        return ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchSafeCopyOutcomeText",
            ReflectedSafeCopyOutcomeSourcePaths);
    }
}
