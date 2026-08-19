using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Restore identity used to say "app-owned Patch Bench BEA.exe-only copy".
/// Name the copy.
/// </summary>
public class BinaryPatchCopyIdentityHonestyTests
{
    [Test]
    public void ANoCatalogTargetNamesTheCopyNotPatchBench()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchEngine.cs"));

        Assert.That(source, Does.Contain("BeaExeOnlyCopyIdentity"));
        Assert.That(source, Does.Not.Contain("app-owned Patch Bench BEA.exe-only copy"));
        Assert.That(BinaryPatchEngine.BeaExeOnlyCopyIdentity, Is.EqualTo("BEA.exe-only copy"));
        Assert.That(BinaryPatchEngine.BeaExeOnlyCopyIdentity.ToLowerInvariant(),
            Does.Not.Contain("patch bench"));
        Assert.That(BinaryPatchEngine.BeaExeOnlyCopyIdentity.ToLowerInvariant(),
            Does.Not.Contain("app-owned"));
    }

    [Test]
    public void WindowedAndModsNamesTheCopyNotAnAppOwnedCopy()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));

        Assert.That(page, Does.Not.Contain("app-owned BEA.exe-only copy"));
        Assert.That(page, Does.Not.Contain("Create an BEA.exe-only copy"));
        Assert.That(page, Does.Contain("Create a BEA.exe-only copy before verification."));
        Assert.That(page, Does.Contain("Create a BEA.exe-only copy before applying patches."));
        Assert.That(page, Does.Contain("Create a BEA.exe-only copy before restoring patch backups."));
        Assert.That(page, Does.Contain("Create a BEA.exe-only copy before verification or patching."));
        Assert.That(page, Does.Contain("applied to the BEA.exe-only copy only"));
        Assert.That(page, Does.Contain("Replace(exePath, \"BEA.exe-only copy\""));
        Assert.That(page, Does.Not.Contain("app advanced patch workspace"));
        Assert.That(page, Does.Contain("This is a BEA.exe-only copy."));
    }
}
