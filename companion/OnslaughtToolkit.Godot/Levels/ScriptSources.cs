// SPDX-License-Identifier: GPL-3.0-only
using System.Text;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>A mission script's installed source text: the file it was read from, its text with <c>\n</c> line ends, and its line count.</summary>
public sealed record ScriptSource(string Path, string Text, int Lines);

/// <param name="Source">The source, or null.</param>
/// <param name="Problem">When there is no source, a sentence saying why.</param>
public sealed record ScriptSourceResult(ScriptSource? Source, string? Problem);

/// <summary>
/// Finds a compiled script's source in a game folder: <c>data/MissionScripts/level&lt;NNN&gt;/&lt;name&gt;.msl</c>, each part in any case (the game's
/// files are named for Windows). The game never reads these files: they are the original compiler's input, shipped with the data, so what
/// they say is what the script was compiled from only if they are the revision that was compiled (<c>tools/msl_gate.py</c> checks that).
/// Read only. A name is matched against the folder's entries, never joined into a path, so a script named like a path finds nothing; links
/// are ignored, as the level archive reader ignores them.
/// </summary>
public static class ScriptSources
{
    public const int MaxBytes = 1 << 20;

    public static ScriptSourceResult Find(string gameRoot, int level, string scriptName)
    {
        string? scripts = ChildFolder(gameRoot, "data") is { } data ? ChildFolder(data, "MissionScripts") : null;
        if (scripts is null) return new(null, "This game has no data/MissionScripts folder.");
        string folderName = $"level{level:D3}";
        if (ChildFolder(scripts, folderName) is not { } folder) return new(null, $"This game has no MissionScripts folder for level {level}.");
        if (ChildFile(folder, scriptName + ".msl") is not { } file) return new(null, $"No file named {scriptName}.msl in {System.IO.Path.GetFileName(folder)}.");
        try
        {
            FileInfo info = new(file);
            if (info.Length > MaxBytes) return new(null, $"{info.Name} is larger than {MaxBytes / 1024} KiB, so it is not shown.");
            string text = Encoding.Latin1.GetString(System.IO.File.ReadAllBytes(file)).Replace("\r\n", "\n").Replace('\r', '\n');
            int lines = text.Count(c => c == '\n') + (text.Length > 0 && text[^1] != '\n' ? 1 : 0);
            return new(new ScriptSource(file, text, lines), null);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return new(null, $"{System.IO.Path.GetFileName(file)} could not be read: {error.Message}");
        }
    }

    /// <summary>The subfolder of <paramref name="parent"/> with this name in any case (the exact spelling first), or null; links are ignored.</summary>
    private static string? ChildFolder(string parent, string name)
    {
        if (!Directory.Exists(parent)) return null;
        return Pick(new DirectoryInfo(parent).EnumerateDirectories().Where(folder => folder.LinkTarget is null).Select(folder => folder.Name), name) is { } found
            ? System.IO.Path.Combine(parent, found) : null;
    }

    private static string? ChildFile(string parent, string name) =>
        Pick(new DirectoryInfo(parent).EnumerateFiles().Where(file => file.LinkTarget is null).Select(file => file.Name), name) is { } found
            ? System.IO.Path.Combine(parent, found) : null;

    private static string? Pick(IEnumerable<string> names, string wanted) =>
        names.Where(name => string.Equals(name, wanted, StringComparison.OrdinalIgnoreCase)).OrderBy(name => name != wanted).ThenBy(name => name, StringComparer.Ordinal).FirstOrDefault();
}
