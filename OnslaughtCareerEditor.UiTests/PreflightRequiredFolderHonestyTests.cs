using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A missing required install folder used to say game directory and interpolate
/// the entry. Name the folder, not a directory.
/// </summary>
public class PreflightRequiredFolderHonestyTests
{
    [Test]
    public void AMissingRequiredInstallFolderIsNamedAsAFolder()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("Required game folder is missing:"));
        Assert.That(source, Does.Contain("{entry}"));
        Assert.That(source, Does.Not.Contain("Required game directory is missing:"));
        Assert.That(source, Does.Not.Contain("required game directory '"));
    }
}
