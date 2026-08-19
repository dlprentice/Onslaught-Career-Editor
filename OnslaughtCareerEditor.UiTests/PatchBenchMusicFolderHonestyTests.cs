using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A missing Music folder used to name data\Music. Name the folder.
/// </summary>
public class PatchBenchMusicFolderHonestyTests
{
    [Test]
    public void AMissingMusicFolderNamesTheFolderNotAPath()
    {
        string sentence = GameProfileMusicReplacementService.MusicFolderMissing;

        Assert.That(sentence, Is.EqualTo("That copy does not have a Music folder."));
        Assert.That(sentence, Does.Contain("Music folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain("data"));
        Assert.That(sentence, Does.Not.Contain("\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
    }

    [Test]
    public void TheServiceDropsTheRelativeMusicPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Contain("MusicFolderMissing"));
        Assert.That(source, Does.Contain("MusicSwapPresetUnknown"));
        Assert.That(source, Does.Not.Contain("Unknown safe-copy music swap preset:"));
        Assert.That(source, Does.Not.Contain("{presetId}"));
        Assert.That(GameProfileMusicReplacementService.MusicSwapPresetUnknown,
            Is.EqualTo("That music swap is not available."));
        Assert.That(GameProfileMusicReplacementService.MusicSwapPresetUnknown.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(source, Does.Not.Contain("does not contain data\\\\Music."));
        Assert.That(source, Does.Not.Contain("does not contain data\\Music."));
    }

    [Test]
    public void AnUnknownMusicSwapNamesTheRefusalWithoutTheCatalogId()
    {
        InvalidOperationException error = Assert.Throws<InvalidOperationException>(
            () => GameProfileMusicReplacementService.GetSafeCopyMusicSwapPreset("not_a_music_swap"));

        Assert.That(error.Message, Is.EqualTo(GameProfileMusicReplacementService.MusicSwapPresetUnknown));
        Assert.That(error.Message, Does.Not.Contain("not_a_music_swap"));
        Assert.That(error.Message, Does.Not.Contain("preset"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(error.Message, Does.Not.Contain(":\\"));
        Assert.That(error.Message, Does.Not.Contain("/"));
    }
}
