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
}
