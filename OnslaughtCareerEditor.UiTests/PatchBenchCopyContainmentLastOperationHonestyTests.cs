using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Last operation used to pass the stay-inside refusal
/// through DescribePatchLog and paint "Patch target". Name the BEA.exe-only
/// copy. GameProfilePreflightService.WorkspaceFileMustStayInside is swallowed
/// by create-copy DescribeCaughtFailure and is not this gap.
/// </summary>
public class PatchBenchCopyContainmentLastOperationHonestyTests
{
    [Test]
    public void ACopyOutsideTheFolderLastOperationNamesTheCopyNotAPatchTarget()
    {
        string allowed = Path.Combine(Path.GetTempPath(), $"bea-lastop-allowed-{Guid.NewGuid():N}");
        string outside = Path.Combine(Path.GetTempPath(), $"bea-lastop-outside-{Guid.NewGuid():N}");
        Directory.CreateDirectory(allowed);
        Directory.CreateDirectory(outside);
        string exePath = Path.Combine(outside, "BEA.exe");
        File.WriteAllBytes(exePath, new byte[16]);
        try
        {
            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: allowed));

            string lastOperation = DescribePatchLog(message);

            Assert.That(success, Is.False);
            Assert.That(message, Is.EqualTo(BinaryPatchEngine.PatchTargetMustStayInsideWorkspaceFolder));
            Assert.That(lastOperation, Is.EqualTo("The BEA.exe-only copy must stay inside the workspace folder."));
            Assert.That(lastOperation, Does.Contain("BEA.exe-only copy"));
            Assert.That(lastOperation, Does.Contain("workspace folder"));
            Assert.That(lastOperation, Does.Not.Contain("Patch target"));
            Assert.That(lastOperation, Does.Not.Contain("app-owned"));
            Assert.That(lastOperation, Does.Not.Contain(allowed));
            Assert.That(lastOperation, Does.Not.Contain(outside));
            Assert.That(lastOperation, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(allowed, recursive: true);
            Directory.Delete(outside, recursive: true);
        }
    }

    [Test]
    public void LastOperationPaintsTheStayInsideSentence()
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
        Assert.That(helper, Does.Contain("BeaExeOnlyCopyMustStayInside"));
        Assert.That(helper, Does.Contain("return message;"));
        Assert.That(engine, Does.Contain("PatchTargetMustStayInsideWorkspaceFolder"));
        Assert.That(engine, Does.Contain("Patch target must stay inside the workspace folder."));
        Assert.That(helper, Does.Not.Contain("Patch target must stay inside the workspace folder."));
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
