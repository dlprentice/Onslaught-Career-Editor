using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// BesFilePatcher extension refusals used to say input/output paths.
/// Name the files, the same way the Goodie leftover already does.
/// </summary>
public class BesFilePatcherHonestyTests
{
    [Test]
    public void PatchExtensionRefusalsNameTheFilesNotThePaths()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BesFilePatcher.cs"));

        Assert.That(source, Does.Not.Contain("requires a .bes output path."));
        Assert.That(source, Does.Not.Contain("requires a .bea output path."));
        Assert.That(source, Does.Not.Contain("options input path."));
        Assert.That(source, Does.Contain("Career save patching requires a .bes output file."));
        Assert.That(source, Does.Contain("Game options patching requires a .bea output file."));
        Assert.That(source, Does.Contain("Patching requires a .bes career save or .bea options input file."));
    }
}
