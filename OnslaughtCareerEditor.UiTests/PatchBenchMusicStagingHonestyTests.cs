using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods staging already used DescribeCaughtFailure in the catch,
/// but the OperationLog still interpolated TargetRelativePath / BackupRelativePath
/// and said a manifest was written.
/// </summary>
public class PatchBenchMusicStagingHonestyTests
{
    private static readonly string[] ReflectedSafeCopyOutcomeSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyOutcomeTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyControlOptionsTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyMusicSwapTextState.cs",
    ];

    [Test]
    public void AStagedSwapNamesTheFilesWithoutTheRelativePath()
    {
        string sentence = InvokeString(
            "BuildMusicStagedOperationLog",
            "BEA_01(Master).ogg",
            "BEA_02(Master).ogg",
            true);

        Assert.That(sentence, Does.Contain("BEA_01(Master).ogg"));
        Assert.That(sentence, Does.Contain("BEA_02(Master).ogg"));
        Assert.That(sentence, Does.Contain("staged"));
        Assert.That(sentence, Does.Contain("original install stays unchanged"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("manifest"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("data"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void AStagedReplacementUsesOnlyTheFileName()
    {
        string target = Path.Combine("data", "Music", "BEA_01(Master).ogg");
        string replacement = Path.Combine(
            "C:" + Path.DirectorySeparatorChar + "Users",
            "player",
            "Downloads",
            "BEA_02(Master).ogg");
        string sentence = InvokeString("BuildMusicStagedOperationLog", target, replacement, false);

        Assert.That(sentence, Does.Contain("BEA_01(Master).ogg"));
        Assert.That(sentence, Does.Contain("BEA_02(Master).ogg"));
        Assert.That(sentence, Does.Not.Contain(target));
        Assert.That(sentence, Does.Not.Contain(replacement));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("Users"));
        Assert.That(sentence, Does.Not.Contain("Downloads"));
        Assert.That(sentence, Does.Not.Contain("Music"));
    }

    [Test]
    public void ThePageStagingLogUsesTheSharedSentenceInsteadOfRelativePaths()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));

        int start = code.IndexOf("private async Task StageMusicReplacementAsync", StringComparison.Ordinal);
        int end = code.IndexOf("private async void RestoreMusicReplacementButton_Click", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = code[start..end];
        Assert.That(method, Does.Contain("PatchBenchSafeCopyOutcomeText.BuildMusicStagedOperationLog"));
        Assert.That(method, Does.Contain("PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure(\"stage copied music bytes\")"));
        Assert.That(method, Does.Not.Contain("TargetRelativePath"));
        Assert.That(method, Does.Not.Contain("BackupRelativePath"));
        Assert.That(method, Does.Not.Contain("Manifest written"));
        Assert.That(method, Does.Not.Contain("{ex.Message}"));
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
