using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Last operation used to pass WorkingCopyPathUnusable
/// through DescribePatchLog and paint "patch target". Name the BEA.exe-only
/// copy. PatchTargetMustBeBeaExeOnlyCopy is a different leftover (4ec08925).
/// RestoreFromBackup of an existing BEA.exe whose workspace folder cannot
/// be normalized hits this check after the filename gate.
/// </summary>
public class PatchBenchUnusableCopyLastOperationHonestyTests
{
    [Test]
    public void AnUnusableCopyLastOperationNamesTheCopyNotAPatchTarget()
    {
        string folder = Path.Combine(Path.GetTempPath(), $"bea-lastop-unusable-{Guid.NewGuid():N}");
        Directory.CreateDirectory(folder);
        string exePath = Path.Combine(folder, "BEA.exe");
        File.WriteAllBytes(exePath, new byte[16]);
        // GetFullPath accepts '|'. An embedded NUL makes NormalizeDirectoryRoot
        // throw after the file exists and is named BEA.exe.
        string unusableRoot = folder + "\0unusable";
        try
        {
            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: unusableRoot));

            string lastOperation = DescribePatchLog(message);

            Assert.That(success, Is.False);
            Assert.That(message, Is.EqualTo(BinaryPatchEngine.WorkingCopyPathUnusable));
            Assert.That(lastOperation, Is.EqualTo("That BEA.exe-only copy could not be used. Nothing was changed."));
            Assert.That(lastOperation, Does.Contain("BEA.exe-only copy"));
            Assert.That(lastOperation, Does.Not.Contain("patch target").IgnoreCase);
            Assert.That(lastOperation, Does.Not.Contain("Patch target"));
            Assert.That(lastOperation, Does.Not.Contain("app-owned"));
            Assert.That(lastOperation, Does.Not.Contain(folder));
            Assert.That(lastOperation, Does.Not.Contain(exePath));
            Assert.That(lastOperation, Does.Not.Contain(unusableRoot));
            Assert.That(lastOperation, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(folder, recursive: true);
        }
    }

    [Test]
    public void LastOperationPaintsTheUnusableCopySentence()
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
        Assert.That(helper, Does.Contain("BeaExeOnlyCopyUnusable"));
        Assert.That(helper, Does.Contain("return message;"));
        Assert.That(engine, Does.Contain("WorkingCopyPathUnusable"));
        Assert.That(engine, Does.Contain("That patch target could not be used. Nothing was changed."));
        Assert.That(helper, Does.Not.Contain("That patch target could not be used. Nothing was changed."));
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
