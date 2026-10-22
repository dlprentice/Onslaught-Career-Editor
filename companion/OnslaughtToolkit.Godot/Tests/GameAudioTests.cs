// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Tests;

/// <summary>The game's own music, voice lines and cutscene list, found in a game-shaped folder of tiny original bytes.</summary>
internal static class GameAudioTests
{
    /// <summary>The game-audio catalog's grouping and its header check, on tiny original byte files.</summary>
    internal static void Run(string outputDirectory, byte[] career, Checks check)
    {
        check.Suite("game audio");
        FakeInstall install = FakeInstall.Create(Path.Combine(outputDirectory, "game-audio"), career);
        IReadOnlyList<Media.GameAudioItem> items = Media.GameAudio.Catalog(Game.GameFolder.Inspect(install.Game, "test"), null);
        check.That(items.Count == 3 && items.Count(item => item.Kind == Media.AudioKind.Music) == 1 &&
            items.Single(item => item.Kind == Media.AudioKind.Voice).Group == "Level 2.11" &&
            items.Single(item => item.Kind == Media.AudioKind.Cutscene) is { Playable: false },
            "Music, voice lines by level and unplayable cutscenes are listed from the install.");
        check.That(Media.GameAudio.VoiceGroup("tutorial_01", null).Group == "Tutorial" && Media.GameAudio.VoiceGroup("health_low", null).Group ==
            "Status messages" && Media.GameAudio.VoiceGroup("wingman_03", null).Group == "Wingman", "Voice lines group by their kind.");
        string header = Path.Combine(outputDirectory, "game-audio", "header.ogg");
        File.WriteAllBytes(header, Convert.FromHexString("4f676753" + "0002" + new string('0', 16) + new string('0', 24) + "01" + "1e" +
            "01" + Convert.ToHexString("vorbis"u8.ToArray()) + new string('0', 40)));
        check.That(Media.GameAudio.LooksLikeOggVorbis(header) && !Media.GameAudio.LooksLikeOggVorbis(install.Career) &&
            !Media.GameAudio.LooksLikeOggVorbis(Path.Combine(install.Game, "data", "Music", "theme.ogg")),
            "Only a file with an Ogg page carrying a Vorbis identification header reaches the decoder.");
    }
}
