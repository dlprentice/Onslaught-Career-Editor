// SPDX-License-Identifier: MIT
using System.Text.RegularExpressions;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Media;

public enum AudioKind { Music, Voice, Cutscene }

/// <summary>One of the game's own media files, found in the player's install. Nothing is copied or bundled.</summary>
public sealed record GameAudioItem(string Title, string Path, AudioKind Kind, string Group, int GroupOrder, string? Transcript)
{
    public bool Playable => Kind != AudioKind.Cutscene;
}

/// <summary>
/// The game's soundtrack (<c>data/Music</c>), voice lines (<c>data/sounds/english/MessageBox</c>) grouped
/// by mission with transcripts from the game's own text table, and cutscenes (Bink <c>.vid</c>, listed but
/// not playable: Godot has no Bink decoder). Read-only.
/// </summary>
public static partial class GameAudio
{
    public static IReadOnlyList<GameAudioItem> Catalog(GameFolder game, GameText? text)
    {
        List<GameAudioItem> items = [];
        foreach (string file in Files(Path.Combine(game.Root, "data", "Music"), "*.ogg"))
        {
            string stem = Path.GetFileNameWithoutExtension(file);
            Match number = TrackNumber().Match(stem);
            items.Add(new GameAudioItem(number.Success ? $"Soundtrack {number.Groups[1].Value}" : stem.Replace('_', ' '), file,
                AudioKind.Music, "Soundtrack", 0, null));
        }
        foreach (string file in Files(Path.Combine(game.Root, "data", "sounds", "english", "MessageBox"), "*.ogg"))
        {
            string stem = Path.GetFileNameWithoutExtension(file);
            (string group, int order) = VoiceGroup(stem, text);
            items.Add(new GameAudioItem(stem, file, AudioKind.Voice, group, order, text?.VoiceLine(stem)));
        }
        foreach (string file in Files(Path.Combine(game.Root, "data", "video", "cutscenes"), "*.vid"))
            items.Add(new GameAudioItem(Path.GetFileNameWithoutExtension(file), file, AudioKind.Cutscene, "Cutscenes (Bink video)", 99999, null));
        return items.OrderBy(item => item.GroupOrder).ThenBy(item => item.Group, StringComparer.OrdinalIgnoreCase)
            .ThenBy(item => item.Title, StringComparer.OrdinalIgnoreCase).ToArray();
    }

    /// <summary>Which heading a voice line belongs under: its mission (named from the game's text when possible) or its kind.</summary>
    public static (string Group, int Order) VoiceGroup(string stem, GameText? text)
    {
        string prefix = stem.Split('_')[0];
        if (uint.TryParse(prefix, out uint mission) && mission is >= 100 and <= 999)
            return (text?.LevelName(mission) ?? $"Level {mission}", (int)mission);
        string upper = stem.ToUpperInvariant();
        if (upper.StartsWith("TUTORIAL", StringComparison.Ordinal)) return ("Tutorial", 10000);
        if (upper.StartsWith("RACING", StringComparison.Ordinal)) return ("Racing", 10001);
        if (upper.StartsWith("WINGMAN", StringComparison.Ordinal)) return ("Wingman", 10002);
        if (new[] { "HEALTH_", "UNDER_", "BASE_", "NEED_" }.Any(start => upper.StartsWith(start, StringComparison.Ordinal)))
            return ("Status messages", 10003);
        return ("Other", 10004);
    }

    /// <summary>
    /// True when a file starts with an Ogg page whose first packet is a Vorbis identification header.
    /// Checked before handing a file to the engine, so a damaged or mislabelled file is refused quietly.
    /// </summary>
    public static bool LooksLikeOggVorbis(string path)
    {
        try
        {
            Span<byte> head = stackalloc byte[64];
            using FileStream stream = new(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
            int read = stream.Read(head);
            if (read < 35 || head[0] != 'O' || head[1] != 'g' || head[2] != 'g' || head[3] != 'S') return false;
            int segments = head[26];
            int packet = 27 + segments;
            return packet + 7 <= read && head[packet] == 1 && head.Slice(packet + 1, 6).SequenceEqual("vorbis"u8);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return false;
        }
    }

    private static string[] Files(string folder, string pattern)
    {
        try
        {
            return Directory.Exists(folder) ? Directory.GetFiles(folder, pattern) : [];
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return [];
        }
    }

    [GeneratedRegex(@"^BEA_(\d+)", RegexOptions.IgnoreCase)]
    private static partial Regex TrackNumber();
}
