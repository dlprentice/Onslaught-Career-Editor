using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab focused Goodie still lets a write under GameProfiles proceed,
/// then refuses anything that is not one .bes file in that copy's
/// savegames folder. The painted sentence used to name a verified
/// profile. Name the copy.
/// </summary>
public class SaveLabGoodieSavegamesFolderHonestyTests
{
    [Test]
    public void ASafeCopyGoodieOutsideSavegamesPaintsTheCopyNotAVerifiedProfile()
    {
        string root = Path.Combine(Path.GetTempPath(), $"bea-savelab-goodie-{Guid.NewGuid():N}");
        string? previous = Environment.GetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT");
        try
        {
            Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", root);
            Directory.CreateDirectory(root);

            string inputDir = Path.Combine(root, "input");
            Directory.CreateDirectory(inputDir);
            string input = Path.Combine(inputDir, "career.bes");
            File.Copy(TestFixturePaths.RequireGoldSavePath(), input);

            string copy = Path.Combine(AppConfig.GetGameProfilesDir(), "copy");
            Directory.CreateDirectory(copy);
            string output = Path.Combine(copy, "career-out.bes");

            PatchResult result = SaveEditorService.PatchFocusedGoodieState(new FocusedGoodieStatePatchRequest
            {
                InputPath = input,
                OutputPath = output,
                GoodieId = 0,
                State = MissionScriptGoodieState.New,
            });

            string lastOperation = SaveLabPageText.DescribeEditorPatchFailure(result.Message);

            Assert.That(result.Success, Is.False);
            Assert.That(File.Exists(output), Is.False);
            Assert.That(
                lastOperation,
                Is.EqualTo("Inside a safe copy, that Goodie save has to be one .bes file in that copy's savegames folder."));
            Assert.That(lastOperation, Does.Contain("savegames folder"));
            Assert.That(lastOperation, Does.Not.Contain("verified profile"));
            Assert.That(lastOperation, Does.Not.Contain("app-owned"));
            Assert.That(lastOperation, Does.Not.Contain(root));
            Assert.That(lastOperation, Does.Not.Contain(":\\"));
        }
        finally
        {
            Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", previous);
            if (Directory.Exists(root))
                Directory.Delete(root, recursive: true);
        }
    }

    [Test]
    public void LastOperationAndHelpNameTheCopyNotAVerifiedProfile()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "SaveLabPageText.cs"));
        string editor = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "SaveEditorService.cs"));

        Assert.That(page, Does.Contain("SaveLabPageText.DescribeEditorPatchFailure"));
        Assert.That(helper, Does.Contain("return message;"));
        Assert.That(
            editor,
            Does.Contain("Inside a safe copy, that Goodie save has to be one .bes file in that copy's savegames folder."));
        Assert.That(editor, Does.Not.Contain("verified profile"));
        Assert.That(xaml, Does.Contain("that copy's savegames folder"));
        Assert.That(xaml, Does.Not.Contain("verified profile"));
    }
}
