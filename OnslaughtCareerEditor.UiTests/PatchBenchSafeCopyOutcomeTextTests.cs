using System;
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

    private static string InvokeString(string methodName, params object?[] arguments)
    {
        return (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            GetHelperType(),
            methodName,
            arguments);
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
