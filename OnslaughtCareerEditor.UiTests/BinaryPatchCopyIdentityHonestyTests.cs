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
}
