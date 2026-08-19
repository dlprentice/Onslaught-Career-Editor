using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Last operation used to require an app-owned workspace
/// folder when the patch target had no workspace. Name the folder.
/// </summary>
public class PatchBenchWorkspaceFolderLastOperationHonestyTests
{
    [Test]
    public void ABlankWorkspaceFolderLastOperationNamesTheFolderNotAnAppOwnedWorkspace()
    {
        string folder = Path.Combine(Path.GetTempPath(), $"bea-workspace-{Guid.NewGuid():N}");
        Directory.CreateDirectory(folder);
        string exePath = Path.Combine(folder, "BEA.exe");
        File.WriteAllBytes(exePath, new byte[16]);
        try
        {
            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: " "));

            string lastOperation = DescribePatchLog(message);

            Assert.That(success, Is.False);
            Assert.That(lastOperation, Is.EqualTo(BinaryPatchEngine.WorkspaceFolderRequired));
            Assert.That(lastOperation, Is.EqualTo("A workspace folder is required."));
            Assert.That(lastOperation, Does.Contain("workspace folder"));
            Assert.That(lastOperation, Does.Not.Contain("app-owned"));
            Assert.That(lastOperation, Does.Not.Contain(folder));
            Assert.That(lastOperation, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(folder, recursive: true);
        }
    }

    [Test]
    public void LastOperationPaintsTheEngineWorkspaceFolderSentence()
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
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchEngine.cs"));

        Assert.That(page, Does.Contain("FormatPatchLogForUi"));
        Assert.That(page, Does.Contain("PatchBenchSafeCopyOutcomeText.DescribePatchLog"));
        Assert.That(helper, Does.Contain("return message;"));
        Assert.That(engine, Does.Contain("WorkspaceFolderRequired"));
        Assert.That(engine, Does.Not.Contain("An app-owned workspace folder is required."));
    }

    private static string DescribePatchLog(string message)
    {
        return (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            ReflectedWinUiTestSupport.GetRequiredType(
                "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchSafeCopyOutcomeText",
                "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs"),
            "DescribePatchLog",
            message);
    }
}
