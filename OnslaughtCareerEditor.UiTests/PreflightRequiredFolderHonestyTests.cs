using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A missing required install folder used to say game directory and interpolate
/// the entry. Name the folder, not a directory or a path fragment.
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

        Assert.That(source, Does.Contain("RequiredGameFolderMissing"));
        Assert.That(source, Does.Contain("A required game folder is missing."));
        Assert.That(source, Does.Not.Contain("Required game folder is missing:"));
        Assert.That(source, Does.Not.Contain("Required game directory is missing:"));
        Assert.That(source, Does.Not.Contain("required game directory '"));
        Assert.That(source, Does.Not.Contain("required game folder '{entry}'"));
        Assert.That(source, Does.Not.Contain("game entry '{entry}'"));
        Assert.That(GameProfilePreflightService.RequiredGameFolderMissing,
            Is.EqualTo("A required game folder is missing."));
        Assert.That(GameProfilePreflightService.RequiredGameFolderMissing.ToLowerInvariant(),
            Does.Not.Contain("directory"));
        Assert.That(GameProfilePreflightService.RequiredGameFolderMissing.ToLowerInvariant(),
            Does.Not.Contain("path"));
    }
}
