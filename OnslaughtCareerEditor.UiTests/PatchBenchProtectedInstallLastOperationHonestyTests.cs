using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Last operation used to pass the protected-install
/// refusal through DescribePatchLog and paint "Patch target". Name the
/// BEA.exe-only copy. The steamapps/common install sentence is a different
/// leftover.
/// </summary>
public class PatchBenchProtectedInstallLastOperationHonestyTests
{
    [Test]
    public void AProtectedInstallLastOperationNamesTheCopyNotAPatchTarget()
    {
        string? programFiles = Environment.GetEnvironmentVariable("ProgramFiles");
        Assert.That(programFiles, Is.Not.Null.And.Not.Empty);

        string folder = Path.Combine(Path.GetTempPath(), $"bea-lastop-protected-{Guid.NewGuid():N}");
        Directory.CreateDirectory(folder);
        string exePath = Path.Combine(folder, "BEA.exe");
        File.WriteAllBytes(exePath, new byte[16]);
        try
        {
            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: programFiles));

            string lastOperation = DescribePatchLog(message);

            Assert.That(success, Is.False);
            Assert.That(message, Is.EqualTo(BinaryPatchEngine.ProtectedInstallFolder));
            Assert.That(
                lastOperation,
                Is.EqualTo("The BEA.exe-only copy is under Program Files or another protected install folder. Work in a copy, or choose to patch your installed game - which takes a verified backup first."));
            Assert.That(lastOperation, Does.Contain("BEA.exe-only copy"));
            Assert.That(lastOperation, Does.Contain("protected install folder"));
            Assert.That(lastOperation, Does.Not.Contain("Patch target"));
            Assert.That(lastOperation, Does.Not.Contain("app-owned"));
            Assert.That(lastOperation, Does.Not.Contain(folder));
            Assert.That(lastOperation, Does.Not.Contain(programFiles));
            Assert.That(lastOperation, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(folder, recursive: true);
        }
    }

    [Test]
    public void LastOperationPaintsTheProtectedInstallSentence()
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
        Assert.That(helper, Does.Contain("BeaExeOnlyCopyProtectedInstallFolder"));
        Assert.That(helper, Does.Contain("return message;"));
        Assert.That(engine, Does.Contain("ProtectedInstallFolder"));
        Assert.That(engine, Does.Contain("Patch target is under Program Files or another protected install folder."));
        Assert.That(helper, Does.Not.Contain("Patch target is under Program Files or another protected install folder."));
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
