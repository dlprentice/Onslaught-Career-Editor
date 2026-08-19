using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Music replacement used to say "manifest paths".
/// Name the files, not a path.
/// </summary>
public class MusicReplacementManifestHonestyTests
{
    [Test]
    public void AMusicManifestIsNamedWithoutCallingItAPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Not.Contain(
            "Playable copied game folder music replacement manifest paths do not match the target music file."));
        Assert.That(source, Does.Not.Contain(
            "Music replacement manifest paths must be package-relative."));
        Assert.That(source, Does.Not.Contain(
            "Playable copied game folder music replacement manifest files do not match the target music file."));
        Assert.That(source, Does.Contain("MusicDetailsWrongTarget"));
        Assert.That(source, Does.Contain(
            "Music replacement manifest files must stay inside the copy."));
        Assert.That(GameProfileMusicReplacementService.MusicDetailsWrongTarget,
            Is.EqualTo("That copy's music details do not match the music file."));
        Assert.That(GameProfileMusicReplacementService.MusicDetailsWrongTarget.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfileMusicReplacementService.MusicDetailsWrongTarget.ToLowerInvariant(),
            Does.Not.Contain("manifest"));
        Assert.That(source, Does.Contain("MusicDetailsUnsupported"));
        Assert.That(source, Does.Not.Contain(
            "Playable copied game folder music replacement manifest has an unsupported schema."));
        Assert.That(GameProfileMusicReplacementService.MusicDetailsUnsupported,
            Is.EqualTo("That copy's music details are out of date."));
        Assert.That(GameProfileMusicReplacementService.MusicDetailsUnsupported.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfileMusicReplacementService.MusicDetailsUnsupported.ToLowerInvariant(),
            Does.Not.Contain("schema"));
        Assert.That(source, Does.Contain("MusicBackupMismatch"));
        Assert.That(source, Does.Not.Contain(
            "Playable copied game folder music backup no longer matches the replacement manifest."));
        Assert.That(GameProfileMusicReplacementService.MusicBackupMismatch,
            Is.EqualTo("That copy's music backup no longer matches."));
        Assert.That(GameProfileMusicReplacementService.MusicBackupMismatch.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfileMusicReplacementService.MusicBackupMismatch.ToLowerInvariant(),
            Does.Not.Contain("manifest"));
        Assert.That(source, Does.Contain("MusicRestoreMismatch"));
        Assert.That(source, Does.Not.Contain(
            "Playable copied game folder music restore did not read back the expected original track hash."));
        Assert.That(GameProfileMusicReplacementService.MusicRestoreMismatch,
            Is.EqualTo("That copy's restored music file no longer matches."));
        Assert.That(GameProfileMusicReplacementService.MusicRestoreMismatch.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfileMusicReplacementService.MusicRestoreMismatch.ToLowerInvariant(),
            Does.Not.Contain("hash"));
    }

    [Test]
    public void AManifestThatLeavesTheCopyIsNamedWithoutCallingItAPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Not.Contain(
            "Music replacement manifest path escapes the playable copied game folder root."));
        Assert.That(source, Does.Contain(
            "Music replacement manifest files must stay inside the copy."));
    }

    [Test]
    public void AMissingManifestNamesTheFileNotAPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Not.Contain(
            "Playable copied game folder music replacement manifest was not found."));
        Assert.That(source, Does.Not.Contain(", manifestPath)"));
        Assert.That(source, Does.Contain(
            "That copy is missing onslaught-music-replacement-manifest.json."));
    }

    [Test]
    public void AMissingReplacementOggDoesNotAttachTheFilePath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Not.Contain(
            "throw new FileNotFoundException(\"Replacement OGG file was not found.\", fullPath);"));
        Assert.That(source, Does.Contain("That replacement OGG file could not be found."));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(\"That replacement OGG file could not be found.\","));
    }

    [Test]
    public void MissingCopiedMusicFilesDoNotAttachTheFilePath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Contain("TargetMusicFileMissing"));
        Assert.That(source, Does.Contain("ReplacementMusicFileMissing"));
        Assert.That(source, Does.Contain("MusicBackupMissing"));
        Assert.That(source, Does.Not.Contain("does not exist in the playable copied game folder."));
        Assert.That(source, Does.Not.Contain("Playable copied game folder music backup was not found."));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(TargetMusicFileMissing,"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(ReplacementMusicFileMissing,"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(MusicBackupMissing,"));
    }

    [Test]
    public void ASharedMusicFileIsNamedWithoutCallingItAHardlink()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Not.Contain("is hardlinked to another file"));
        Assert.That(source, Does.Contain("FileCannotShareData"));
        Assert.That(GameProfileMusicReplacementService.FileCannotShareData,
            Is.EqualTo("That file cannot share its data with another file."));
        Assert.That(source, Does.Not.Contain("Could not inspect hardlink count"));
        Assert.That(source, Does.Not.Contain("Win32 error:"));
        Assert.That(source, Does.Contain("FileCouldNotBeInspected"));
    }
}
