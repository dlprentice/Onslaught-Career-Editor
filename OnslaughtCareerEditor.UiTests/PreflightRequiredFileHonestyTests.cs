using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Advanced copy used to say a source or destination path is required.
/// Name the file, not a path.
/// </summary>
public class PreflightRequiredFileHonestyTests
{
    [Test]
    public void ABlankSourceNamesTheExecutableNotAPath()
    {
        InvalidOperationException ex = Assert.Throws<InvalidOperationException>(
            () => GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy("  "));

        Assert.That(ex.Message, Is.EqualTo("A source executable is required."));
        Assert.That(ex.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void ABlankDestinationNamesTheFileNotAPath()
    {
        InvalidOperationException ex = Assert.Throws<InvalidOperationException>(
            () => GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination("  ", "root", "BEA.exe"));

        Assert.That(ex.Message, Is.EqualTo("A destination file is required."));
        Assert.That(ex.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void TheSourceDoesNotKeepTheOldPathSentences()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Not.Contain("Executable source path is required."));
        Assert.That(source, Does.Not.Contain("Workspace destination path is required."));
    }
}
