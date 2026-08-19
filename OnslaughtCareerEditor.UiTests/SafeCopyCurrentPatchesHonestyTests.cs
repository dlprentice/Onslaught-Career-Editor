using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Your safe copies used to show size and careers without saying which
/// catalog patches that copy already has. The current-patch line paints
/// the copy's BEA.exe bytes.
/// </summary>
public class SafeCopyCurrentPatchesHonestyTests
{
    [Test]
    public void CurrentPatchesPaintsThisCopyNotAPath()
    {
        string mixed = SafeCopyManagerText.DescribeCurrentPatches(
            BinaryPatchCopyInspectRefusal.None,
            new[]
            {
                ("Prefer windowed startup", BinaryPatchState.Patched),
                ("Correct 16:9 gameplay view", BinaryPatchState.Original),
            });

        Assert.That(mixed, Is.EqualTo("This copy already has Prefer windowed startup."));
        AssertHonesty(mixed);
        AssertHonesty(SafeCopyManagerText.CurrentPatchesAllOriginal);
        AssertHonesty(SafeCopyManagerText.CurrentPatchesAllPatched);
        AssertHonesty(SafeCopyManagerText.CurrentPatchesNoExecutable);
        AssertHonesty(SafeCopyManagerText.CurrentPatchesUnreadable);
        AssertHonesty(SafeCopyManagerText.CurrentPatchesInstalledGame);
    }

    [Test]
    public void UnmatchedBytesAreNamedWithoutADump()
    {
        string painted = SafeCopyManagerText.DescribeCurrentPatches(
            BinaryPatchCopyInspectRefusal.None,
            new[]
            {
                ("Experimental O-key pause test", BinaryPatchState.Mismatch),
            });

        Assert.That(
            painted,
            Is.EqualTo("This copy's bytes for Experimental O-key pause test do not match original or patched."));
        AssertHonesty(painted);
        Assert.That(painted, Does.Not.Contain("0x"));
        Assert.That(painted, Does.Not.Contain("unexpected bytes"));
    }

    [Test]
    public void WindowedAndModsBindsTheCurrentPatchLineAndReadsTheCopy()
    {
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));
        string item = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Models",
            "SafeCopyManagerItem.cs"));

        Assert.That(xaml, Does.Contain("Text=\"{Binding PatchStateText}\""));
        Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"{Binding PatchStateAutomationId}\""));
        Assert.That(item, Does.Contain("BinaryPatchEngine.InspectCopyExecutable"));
        Assert.That(item, Does.Contain("SafeCopyManagerText.DescribeCurrentPatches"));
        Assert.That(page, Does.Contain("new Models.SafeCopyManagerItem(copy)"));
        Assert.That(xaml, Does.Not.Contain("CDB"));
        Assert.That(xaml, Does.Not.Contain("sidecar"));
    }

    [Test]
    public void AMissingCopyExecutablePaintsTheNoExeSentenceWithoutTheFolder()
    {
        var item = new SafeCopyManagerItem(new SafeCopyOverview(
            "trainer-proof",
            @"X:\GameProfiles\trainer-proof",
            700L * 1024 * 1024,
            new DateTime(2026, 8, 1, 12, 0, 0, DateTimeKind.Utc),
            new DateTime(2026, 8, 1, 12, 0, 0, DateTimeKind.Utc),
            0,
            Playable: true));

        Assert.That(item.PatchStateText, Is.EqualTo(SafeCopyManagerText.CurrentPatchesNoExecutable));
        Assert.That(item.PatchStateText, Does.Not.Contain(@":\"));
        Assert.That(item.PatchStateAutomationId, Is.EqualTo("SafeCopyRowCurrentPatches_trainer_proof"));
    }

    private static void AssertHonesty(string painted)
    {
        Assert.That(painted, Does.Not.Contain(@":\"));
        Assert.That(painted, Does.Not.Contain("verified"));
        Assert.That(painted, Does.Not.Contain("app-owned"));
        Assert.That(painted, Does.Not.Contain("exception"));
        Assert.That(painted, Does.Not.Contain("sidecar"));
        Assert.That(painted, Does.Not.Contain("CDB"));
    }
}
