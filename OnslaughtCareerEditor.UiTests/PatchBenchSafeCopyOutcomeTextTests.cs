using System;
using System.IO;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchSafeCopyOutcomeTextTests
{
    private static readonly string[] ReflectedSafeCopyOutcomeSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyOutcomeTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyControlOptionsTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyMusicSwapTextState.cs",
    ];

    [Test]
    public void MusicReplacementStatusBuilders_PreserveSafeCopyBoundaryText()
    {
        Assert.Multiple(() =>
        {
            Assert.That(
                InvokeString("BuildDefaultMusicReplacementStatus"),
                Is.EqualTo("No music swap staged. Staging only; in-game playback is still experimental and unproven."));
            Assert.That(
                InvokeString("BuildMusicReplacementStatus", (object?)null),
                Is.EqualTo("Safe copy ready for music replacement staging. Staging only; in-game playback is still experimental and unproven."));
            Assert.That(
                InvokeString(
                    "BuildMusicReplacementStatus",
                    CreateMusicSwapTextState("BEA_03(Master).ogg", "backup/BEA_03(Master).ogg")),
                Is.EqualTo("Safe-copy track swap staged for BEA_03(Master).ogg. Restore before staging another swap. In-game playback is still experimental and unproven."));
            Assert.That(
                InvokeString("BuildMusicSwapInputsMissingStatus"),
                Is.EqualTo("Prepare a safe game copy and select two safe-copy tracks before staging a swap."));
            Assert.That(
                InvokeString("BuildMusicPresetMissingSafeCopyStatus"),
                Is.EqualTo("Prepare a safe game copy before staging a music preset."));
            Assert.That(
                InvokeString("BuildMusicPresetFailedStatus"),
                Is.EqualTo("Safe-copy music preset staging failed."));
            Assert.That(
                InvokeString("BuildMusicStagingBlockedStatus"),
                Is.EqualTo("Stop the managed safe copy before staging copied music bytes."));
            Assert.That(
                InvokeString("BuildMusicStagingMissingSafeCopyStatus"),
                Is.EqualTo("Prepare a safe game copy before staging copied music bytes."));
            Assert.That(
                InvokeString("BuildMusicStagingProgressStatus", true),
                Is.EqualTo("Staging safe-copy music swap..."));
            Assert.That(
                InvokeString("BuildMusicStagingProgressStatus", false),
                Is.EqualTo("Staging copied music bytes..."));
            Assert.That(
                InvokeString("BuildMusicStagedStatus", "BEA_02(Master).ogg", true),
                Is.EqualTo("Safe-copy track swap staged for BEA_02(Master).ogg. Staging only; in-game playback is still experimental and unproven."));
            Assert.That(
                InvokeString("BuildMusicStagedStatus", "BEA_02(Master).ogg", false),
                Is.EqualTo("Copied music bytes staged for BEA_02(Master).ogg. Staging only; in-game playback is still experimental and unproven."));
            Assert.That(
                InvokeString("BuildMusicStagingFailedStatus"),
                Is.EqualTo("Copied music byte staging failed."));
            Assert.That(
                InvokeString("BuildMusicRestoreBlockedStatus"),
                Is.EqualTo("Stop the managed safe copy before restoring music backup."));
            Assert.That(
                InvokeString("BuildMusicRestoreMissingSafeCopyStatus"),
                Is.EqualTo("Prepare a safe game copy before restoring music backup."));
            Assert.That(
                InvokeString("BuildMusicRestoreProgressStatus"),
                Is.EqualTo("Restoring safe-copy music backup..."));
            Assert.That(
                InvokeString("BuildMusicRestoreResultStatus", "BEA_01(Master).ogg", true),
                Is.EqualTo("Music backup restored for BEA_01(Master).ogg. Staging only; in-game playback is still experimental and unproven."));
            Assert.That(
                InvokeString("BuildMusicRestoreResultStatus", "BEA_01(Master).ogg", false),
                Is.EqualTo("Safe-copy music backup was not restored."));
            Assert.That(
                InvokeString("BuildMusicRestoreFailedStatus"),
                Is.EqualTo("Safe-copy music backup restore failed."));
        });
    }

    [Test]
    public void ACaughtFailureSaysWhatFailedWithoutTheException()
    {
        string line = InvokeString("DescribeCaughtFailure", "launch the safe copy");

        Assert.That(line, Is.EqualTo("Could not launch the safe copy. Nothing was changed."));
        Assert.That(line, Does.Not.Contain(":\\"));
        Assert.That(line, Does.Not.Contain("0x"));
        Assert.That(line.ToLowerInvariant(), Does.Not.Contain("exception"));
    }

    [Test]
    public void ADumpedInstalledWriteUsesTheSharedFailureSentence()
    {
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "PatchBenchSafeCopyOutcomeText.cs"));

        Assert.That(helper, Does.Contain("DescribeInstalledWriteFailure"));
        Assert.That(helper, Does.Contain("change your installed game"));
        Assert.That(helper, Does.Contain("LooksLikeAPathOrDump"));
        Assert.That(helper, Does.Contain("Nothing was changed"));
        Assert.That(helper.ToLowerInvariant(), Does.Not.Contain("ex.Message"));
    }

    [Test]
    public void ADumpedPatchLogUsesTheSharedFailureSentence()
    {
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "PatchBenchSafeCopyOutcomeText.cs"));
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));

        Assert.That(helper, Does.Contain("DescribePatchLog"));
        Assert.That(helper, Does.Contain("change that BEA.exe"));
        Assert.That(page, Does.Contain("PatchBenchSafeCopyOutcomeText.DescribePatchLog"));
        Assert.That(helper, Does.Not.Contain("ex.Message"));
    }

    [Test]
    public void CreateConfirmationNamesTheFoldersNotThePaths()
    {
        string source = Path.Combine("C:" + Path.DirectorySeparatorChar + "Steam", "steamapps", "common", "Battle Engine Aquila");
        string dest = Path.Combine("C:" + Path.DirectorySeparatorChar + "Users", "player", "AppData", "GameProfiles");
        string question = InvokeString(
            "BuildCreateConfirmation",
            source,
            dest,
            "Settings affecting this copy:" + Environment.NewLine + "Extra settings for next copy: none active.",
            "There may not be enough free space.");

        Assert.That(question, Does.Contain("Battle Engine Aquila"));
        Assert.That(question, Does.Contain("GameProfiles"));
        Assert.That(question, Does.Contain("There may not be enough free space."));
        Assert.That(question, Does.Contain("Steam/game install stays unchanged"));
        Assert.That(question, Does.Not.Contain(source));
        Assert.That(question, Does.Not.Contain(dest));
        Assert.That(question, Does.Not.Contain(":\\"));
        Assert.That(question, Does.Not.Contain("steamapps"));
        Assert.That(question, Does.Not.Contain("Users"));
    }

    [Test]
    public void PreparedMusicSwapNamesTheBackupFileNotTheFolder()
    {
        object music = CreateMusicSwapTextState(
            "BEA_01(Master).ogg",
            "data/Music/BEA_01(Master).ogg.original.backup");
        string summary = InvokeString("BuildPreparedSummary", CreatePreparedState(music));

        Assert.That(summary, Does.Contain("BEA_01(Master).ogg"));
        Assert.That(summary, Does.Contain("BEA_01(Master).ogg.original.backup"));
        Assert.That(summary, Does.Not.Contain("data/Music"));
        Assert.That(summary, Does.Not.Contain("data\\Music"));
    }

    private static string InvokeString(string methodName, params object?[] arguments)
    {
        return (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            GetHelperType(),
            methodName,
            arguments);
    }

    private static object CreatePreparedState(object musicSwap)
    {
        Type stateType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Models.PatchBenchSafeCopyOutcomeTextState",
            ReflectedSafeCopyOutcomeSourcePaths);

        return Activator.CreateInstance(
            stateType,
            BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic,
            binder: null,
            args:
            [
                false,
                null,
                musicSwap,
                "copy-one",
                1,
                "none",
                "no launch modifiers",
                false,
                false,
            ],
            culture: null)
            ?? throw new InvalidOperationException($"Could not create {stateType.FullName}.");
    }

    private static object CreateMusicSwapTextState(string targetMusicFileName, string backupRelativePath)
    {
        Type textStateType = ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Models.PatchBenchSafeCopyMusicSwapTextState",
            ReflectedSafeCopyOutcomeSourcePaths);

        return Activator.CreateInstance(
            textStateType,
            BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic,
            binder: null,
            args: [targetMusicFileName, backupRelativePath],
            culture: null)
            ?? throw new InvalidOperationException($"Could not create {textStateType.FullName}.");
    }

    private static Type GetHelperType()
    {
        return ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchSafeCopyOutcomeText",
            ReflectedSafeCopyOutcomeSourcePaths);
    }
}
