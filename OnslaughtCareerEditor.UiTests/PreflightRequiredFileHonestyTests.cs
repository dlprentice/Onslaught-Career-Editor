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
        Assert.That(source, Does.Not.Contain("BEA.exe was not found under the copied game profile."));
        Assert.That(source, Does.Contain("CopiedBeaMissing"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(CopiedBeaMissing,"));
        Assert.That(source, Does.Not.Contain("Executable source was not found."));
        Assert.That(source, Does.Contain("SourceExecutableMissing"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(SourceExecutableMissing,"));
        Assert.That(source, Does.Not.Contain("BEA.exe source was not found."));
        Assert.That(source, Does.Not.Contain("Required game entry is missing: BEA.exe"));
        Assert.That(source, Does.Not.Contain("Executable override is missing."));
        Assert.That(source, Does.Not.Contain("FileNotFoundException($\"Required game file is missing: {entry}\", path)"));
        Assert.That(source, Does.Not.Contain("Level 100 text target is missing."));
        Assert.That(source, Does.Not.Contain("Level 100 text backup is missing."));
        Assert.That(source, Does.Not.Contain("Level 100 early-flight target is missing."));
        Assert.That(source, Does.Not.Contain("Level 100 early-flight backup is missing."));
        Assert.That(source, Does.Not.Contain("data\\\\language\\\\english.dat."));
        Assert.That(source, Does.Not.Contain("data\\\\resources\\\\100_res_PC.aya."));
        Assert.That(source, Does.Contain("Level100EnglishDatMissing"));
        Assert.That(source, Does.Contain("Level100EnglishDatBackupMissing"));
        Assert.That(source, Does.Contain("Level100ResourceMissing"));
        Assert.That(source, Does.Contain("Level100ResourceBackupMissing"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(Level100EnglishDatMissing,"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(Level100ResourceMissing,"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(Level100ResourceBackupMissing,"));
    }

    [Test]
    public void AMissingSourceExecutableDoesNotAttachTheFilePath()
    {
        string missing = Path.Combine(Path.GetTempPath(), $"gone-bea-{Guid.NewGuid():N}", "BEA.exe");
        FileNotFoundException error = Assert.Throws<FileNotFoundException>(
            () => GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy(missing));

        Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.SourceExecutableMissing));
        Assert.That(error.Message, Is.EqualTo("That source executable could not be found."));
        Assert.That(error.FileName, Is.Null.Or.Empty);
        Assert.That(error.Message, Does.Not.Contain(missing));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }
}
