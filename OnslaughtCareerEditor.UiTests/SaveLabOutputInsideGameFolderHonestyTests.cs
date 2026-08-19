using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab still lets a write into a playable copy proceed, then
/// FileMutationSafety blocks it. The painted sentence used to send the
/// player to an app-owned patched-output folder. Name the output folder.
/// </summary>
public class SaveLabOutputInsideGameFolderHonestyTests
{
    [Test]
    public void ASafeCopyOutputPaintsTheOutputFolderNotAnAppOwnedPatchedOutputFolder()
    {
        string root = Path.Combine(Path.GetTempPath(), $"bea-savelab-game-out-{Guid.NewGuid():N}");
        string inputDir = Path.Combine(root, "input");
        string copy = Path.Combine(root, "copy");
        Directory.CreateDirectory(inputDir);
        Directory.CreateDirectory(Path.Combine(copy, "data"));
        Directory.CreateDirectory(Path.Combine(copy, "savegames"));
        File.WriteAllBytes(Path.Combine(copy, "BEA.exe"), new byte[16]);
        File.WriteAllText(
            Path.Combine(copy, GameProfilePreflightService.ProfileManifestFileName),
            "{}");

        string input = Path.Combine(inputDir, "career.bes");
        string output = Path.Combine(copy, "savegames", "career-out.bes");
        File.Copy(TestFixturePaths.RequireGoldSavePath(), input);

        try
        {
            Assert.That(SaveLabPageText.DescribeOutputRefusal(output), Is.Null);

            PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = input,
                OutputPath = output,
                PatchNodes = false,
                PatchLinks = true,
                PatchGoodies = false,
                PatchKills = false,
            });

            string lastOperation = SaveLabPageText.DescribeEditorPatchFailure(result.Message);

            Assert.That(result.Success, Is.False);
            Assert.That(File.Exists(output), Is.False);
            Assert.That(
                lastOperation,
                Is.EqualTo("Output files inside a Battle Engine Aquila game folder are blocked. Choose the output folder or another non-game folder."));
            Assert.That(lastOperation, Does.Contain("output folder"));
            Assert.That(lastOperation, Does.Not.Contain("app-owned"));
            Assert.That(lastOperation, Does.Not.Contain("patched-output"));
            Assert.That(lastOperation, Does.Not.Contain(root));
            Assert.That(lastOperation, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(root, recursive: true);
        }
    }

    [Test]
    public void LastOperationPaintsTheSafetySentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "SaveLabPageText.cs"));
        string safety = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "FileMutationSafety.cs"));

        Assert.That(page, Does.Contain("SaveLabPageText.DescribeEditorPatchFailure"));
        Assert.That(helper, Does.Contain("return message;"));
        Assert.That(safety, Does.Contain("OutputInsideGameFolder"));
        Assert.That(safety, Does.Not.Contain("Choose the app-owned patched-output folder"));
    }
}
