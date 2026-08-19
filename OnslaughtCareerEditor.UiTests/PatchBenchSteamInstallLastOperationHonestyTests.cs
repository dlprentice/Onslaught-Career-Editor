using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Last operation used to pass the steamapps/common
/// install refusal through DescribePatchLog and paint "Patch target". Name
/// the BEA.exe-only copy. ProtectedInstallFolder is a different leftover
/// (7b482519). This tree is not under Program Files.
/// </summary>
public class PatchBenchSteamInstallLastOperationHonestyTests
{
    [Test]
    public void ASteamInstallLastOperationNamesTheCopyNotAPatchTarget()
    {
        string tempDir = Path.Combine(Path.GetTempPath(), $"bea-lastop-steam-{Guid.NewGuid():N}");
        string folder = Path.Combine(tempDir, "steamapps", "common", "Battle Engine Aquila");
        Directory.CreateDirectory(folder);
        string exePath = Path.Combine(folder, "BEA.exe");
        File.WriteAllBytes(exePath, new byte[16]);
        try
        {
            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: folder));

            string lastOperation = DescribePatchLog(message);

            Assert.That(success, Is.False);
            Assert.That(message, Is.EqualTo(BinaryPatchEngine.SteamAppsCommonInstall));
            Assert.That(
                lastOperation,
                Is.EqualTo("The BEA.exe-only copy is a steamapps/common/Battle Engine Aquila install. Work in a copy, or choose to patch your installed game - which takes a verified backup first."));
            Assert.That(lastOperation, Does.Contain("BEA.exe-only copy"));
            Assert.That(lastOperation, Does.Contain("steamapps/common/Battle Engine Aquila"));
            Assert.That(lastOperation, Does.Not.Contain("Patch target"));
            Assert.That(lastOperation, Does.Not.Contain("app-owned"));
            Assert.That(lastOperation, Does.Not.Contain(folder));
            Assert.That(lastOperation, Does.Not.Contain(tempDir));
            Assert.That(lastOperation, Does.Not.Contain(":\\"));
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void LastOperationPaintsTheSteamInstallSentence()
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
        Assert.That(helper, Does.Contain("BeaExeOnlyCopySteamAppsCommonInstall"));
        Assert.That(helper, Does.Contain("return message;"));
        Assert.That(engine, Does.Contain("SteamAppsCommonInstall"));
        Assert.That(engine, Does.Contain("Patch target is a steamapps/common/Battle Engine Aquila install."));
        Assert.That(helper, Does.Not.Contain("Patch target is a steamapps/common/Battle Engine Aquila install."));
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
