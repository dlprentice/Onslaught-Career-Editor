using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to call the BEA.exe-only diagnostics an
/// app-owned executable-copy workflow. Name the copy.
/// </summary>
public class PatchBenchExeOnlyCopyWorkflowHonestyTests
{
    [Test]
    public void BeaExeOnlyDiagnosticsNamesTheCopyWorkflowNotAnAppOwnedWorkflow()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));

        Assert.That(page, Does.Not.Contain("app-owned executable-copy workflow"));
        Assert.That(page, Does.Not.Contain("app-owned"));
        Assert.That(
            page,
            Does.Contain("This BEA.exe-only copy workflow is separate from Safe Game Copy and never counts as a creation input."));
    }
}
