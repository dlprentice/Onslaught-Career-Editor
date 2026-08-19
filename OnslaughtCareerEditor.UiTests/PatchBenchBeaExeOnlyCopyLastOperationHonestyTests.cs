using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Last operation used to pass the wrong-filename
/// refusal through DescribePatchLog and paint "Patch target". Name the
/// file. SteamAppsCommonInstall is a different leftover (b2796cc6).
/// RestoreFromBackup of an existing file not named BEA.exe hits this
/// check before steam, protected, or stay-inside.
/// </summary>
public class PatchBenchBeaExeOnlyCopyLastOperationHonestyTests
{
    [Test]
    public void AWrongFilenameLastOperationNamesTheFileNotAPatchTarget()
    {
        string folder = Path.Combine(Path.GetTempPath(), $"bea-lastop-filename-{Guid.NewGuid():N}");
        Directory.CreateDirectory(folder);
        string exePath = Path.Combine(folder, "not-bea.bin");
        File.WriteAllBytes(exePath, new byte[16]);
        try
        {
            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: folder));

            string lastOperation = DescribePatchLog(message);

            Assert.That(success, Is.False);
            Assert.That(message, Is.EqualTo(BinaryPatchEngine.PatchTargetMustBeBeaExeOnlyCopy));
            Assert.That(lastOperation, Is.EqualTo("That file must be a BEA.exe-only copy."));
            Assert.That(lastOperation, Does.Contain("BEA.exe-only copy"));
            Assert.That(lastOperation, Does.Not.Contain("Patch target"));
            Assert.That(lastOperation, Does.Not.Contain("app-owned"));
            Assert.That(lastOperation, Does.Not.Contain(folder));
            Assert.That(lastOperation, Does.Not.Contain(exePath));
            Assert.That(lastOperation, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(folder, recursive: true);
        }
    }

    [Test]
    public void LastOperationPaintsTheFilenameSentence()
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
        Assert.That(helper, Does.Contain("ThatFileMustBeBeaExeOnlyCopy"));
        Assert.That(helper, Does.Contain("return message;"));
        Assert.That(engine, Does.Contain("PatchTargetMustBeBeaExeOnlyCopy"));
        Assert.That(engine, Does.Contain("Patch target must be a BEA.exe-only copy."));
        Assert.That(helper, Does.Not.Contain("Patch target must be a BEA.exe-only copy."));
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
