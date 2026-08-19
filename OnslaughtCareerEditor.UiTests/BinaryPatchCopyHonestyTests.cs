using System.IO;
using System.Text.RegularExpressions;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Copied-game apply/restore already named the action, then appended ex.Message
/// on the next line. That still put the OS path on Windowed &amp; Mods Last operation.
/// </summary>
public class BinaryPatchCopyHonestyTests
{
    [Test]
    public void CopiedGameApplyAndRestoreDoNotAppendTheException()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));

        Assert.That(
            Regex.IsMatch(engine, @"\+\s*ex\.Message\)"),
            Is.False,
            "Apply/restore I/O still concatenates ex.Message after the honest sentence.");
        Assert.That(engine, Does.Contain("the BEA.exe-only copy was not modified"));
        Assert.That(engine, Does.Contain("The verified full-file backup remains available"));
        Assert.That(engine, Does.Contain("The verified backup snapshot was left unchanged"));
    }

    [Test]
    public void AnUnusablePatchTargetDoesNotDumpTheException()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));

        Assert.That(engine, Does.Contain("WorkingCopyPathUnusable"));
        Assert.That(engine, Does.Not.Contain("Patch target path could not be normalized: {ex.Message}"));
        Assert.That(engine, Does.Contain("That patch target could not be used. Nothing was changed."));
    }

    [Test]
    public void CatalogReadFallbackDoesNotDumpTheException()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));
        string profiles = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchPlanBuilder.cs"));

        Assert.That(engine, Does.Not.Contain("Catalog read failed ({ex.Message})"));
        Assert.That(engine, Does.Contain("Catalog could not be read; using built-in fallback patch specs."));
        Assert.That(profiles, Does.Not.Contain("Profile catalog read failed ({ex.Message})"));
        Assert.That(profiles, Does.Contain("Profile catalog could not be read; using built-in safe-copy profile presets."));
    }
}
