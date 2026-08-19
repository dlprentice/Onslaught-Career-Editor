using System.IO;
using NUnit.Framework;

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
        Assert.That(source, Does.Contain(
            "Playable copied game folder music replacement manifest files do not match the target music file."));
        Assert.That(source, Does.Contain(
            "Music replacement manifest files must stay inside the copy."));
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
}
