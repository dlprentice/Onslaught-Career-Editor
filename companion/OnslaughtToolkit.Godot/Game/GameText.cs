// SPDX-License-Identifier: MIT
using System.Text.RegularExpressions;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>
/// The game's own words, read at run time from the player's install and never bundled: mission names
/// and voice-line transcripts from <c>data/language/&lt;language&gt;.dat</c> (decoded by the linked MIT
/// GameTextCatalog, whose loader order comes from the game's CText__Init), and Goodie titles through
/// the name-to-id map in <c>data/MissionScripts/text/text.stf</c>.
/// </summary>
public sealed partial class GameText
{
    private readonly Dictionary<string, GameLevelName> _levels = new(StringComparer.Ordinal);
    private readonly Dictionary<int, string> _goodieTitles = [];
    private readonly Dictionary<string, string> _voiceLines = new(StringComparer.OrdinalIgnoreCase);

    private GameText(GameTextCatalog catalog, IReadOnlyDictionary<string, uint> names)
    {
        Language = catalog.LanguageName;
        Levels = GameTextCatalogService.GetLevelNames(catalog);
        foreach (GameLevelName level in Levels)
            _levels.TryAdd(level.Code, level); // The plain row sorts before its (Evo) variant.
        Dictionary<uint, string> byId = [];
        foreach (GameTextEntry entry in catalog.Entries)
        {
            byId.TryAdd(entry.TextId, entry.Text);
            if (!string.IsNullOrWhiteSpace(entry.AudioName) && !string.IsNullOrWhiteSpace(entry.Text))
                _voiceLines.TryAdd(entry.AudioName, entry.Text.Trim());
        }
        foreach ((string name, uint id) in names)
        {
            Match goodie = GoodieTitle().Match(name);
            if (goodie.Success && byId.TryGetValue(id, out string? title) && title.Trim().Length > 0)
                _goodieTitles[int.Parse(goodie.Groups[1].Value) - 1] = title.Trim();
        }
    }

    public string Language { get; }

    /// <summary>Every mission the game's text names, in code order, each harder (Evo) version after its map.</summary>
    public IReadOnlyList<GameLevelName> Levels { get; }
    public int LevelCount => _levels.Count;
    public int GoodieTitleCount => _goodieTitles.Count;
    public int VoiceLineCount => _voiceLines.Count;

    /// <summary>The game's text for an install, or null when its language file cannot be read.</summary>
    public static GameText? Load(string gameRoot)
    {
        if (GameTextCatalogService.TryLoadFromGameDirectory(gameRoot) is not GameTextCatalog catalog) return null;
        string stf = Path.Combine(gameRoot, "data", "MissionScripts", "text", "text.stf");
        return new GameText(catalog, ReadNames(stf));
    }

    internal static GameText FromCatalog(GameTextCatalog catalog, IReadOnlyDictionary<string, uint> names) => new(catalog, names);

    /// <summary>"2.11 - Assault On Apollo" for level 211, as the game's Select Level screen writes it.</summary>
    public string? LevelName(uint world) =>
        GameTextCatalogService.TryGetLevelCodeForMissionNumber((int)Math.Min(world, int.MaxValue)) is string code &&
        _levels.TryGetValue(code, out GameLevelName? name) ? name.Display : null;

    /// <summary>The Goodie's own title for a zero-based save index, when the game names one.</summary>
    public string? GoodieTitle(int index) => _goodieTitles.GetValueOrDefault(index);

    public string? VoiceLine(string audioStem) => _voiceLines.GetValueOrDefault(audioStem);

    /// <summary><c>#define NAME id</c> lines; anything else is ignored.</summary>
    public static IReadOnlyDictionary<string, uint> ParseNames(string text)
    {
        Dictionary<string, uint> names = new(StringComparer.Ordinal);
        foreach (Match match in Define().Matches(text))
            if (uint.TryParse(match.Groups[2].Value, out uint id)) names.TryAdd(match.Groups[1].Value, id);
        return names;
    }

    private static IReadOnlyDictionary<string, uint> ReadNames(string path)
    {
        try
        {
            FileInfo file = new(path);
            return file.Exists && file.Length < 4_000_000 ? ParseNames(File.ReadAllText(path)) : new Dictionary<string, uint>();
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return new Dictionary<string, uint>();
        }
    }

    [GeneratedRegex(@"^\s*#define\s+(\S+)\s+(\d+)\s*$", RegexOptions.Multiline)]
    private static partial Regex Define();

    [GeneratedRegex(@"^GOODIE_TEXT_(\d+)_TITLE$")]
    private static partial Regex GoodieTitle();
}
