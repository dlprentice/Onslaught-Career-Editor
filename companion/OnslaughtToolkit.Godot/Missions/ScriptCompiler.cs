// SPDX-License-Identifier: GPL-3.0-only
using System.Text;
using System.Text.RegularExpressions;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>Something the compiler did that the author may want to see. <see cref="Line"/> is 0-based; <see cref="Kind"/> is "grouping" (how a mixed chain of operators was grouped), "handler" (a handler the game never calls) or "declaration".</summary>
public sealed record CompileNote(int Line, string Kind, string Text);

/// <summary>
/// What the compiler refuses instead of running out of stack, time or memory: the characters of a script (and bytes of a header), the tokens of a
/// script once <c>#define</c> names are replaced, the names looked at while replacing them (a define can expand to nothing, so tokens alone do not
/// bound the work) and how deep statements and expressions may nest (the parser calls itself for each level). The defaults are the reference's;
/// the tests pass smaller ones to put each limit exactly at its edge.
/// </summary>
public sealed record CompileLimits(int MaxSource = 1 << 20, int MaxTokens = 1 << 20, int MaxExpansionSteps = 4 << 20, int MaxDepth = 100)
{
    public static CompileLimits Default { get; } = new();
}

/// <summary>What a name from a missing header stood for: a constant's data type (1 int, 2 float, 3 string, 4 bool, 5 thing, 6 position) and value.</summary>
public readonly record struct ResolvedName(int DataType, ScriptValue Value);

/// <summary>Gives the constant a name that no header in the game folder defines would have had (<paramref name="symbolIndex"/> is where the compiler would enter it), or null.</summary>
public delegate ResolvedName? NameResolver(string name, int symbolIndex);

/// <summary>
/// Compiles a mission script source (<c>.msl</c>) to the compiled script a level's world file stores: what <c>CWorld::LoadScripts</c> reads for each
/// script (name, code, the ten bytes after it). The game never reads the sources; this is the original compiler's job done here, held to the
/// Toolkit's reference (<c>tools/msl_compile.py</c>) by vectors it generates and, on an installed game, by every script the game ships
/// (<c>Development/ScriptsGate.cs</c>). The result goes into a <see cref="WorldBody"/> as it stands; nothing here writes a file.
/// </summary>
public static class ScriptCompiler
{
    public const int MaxSource = 1 << 20;  // characters of a script, bytes of a header

    /// <summary>The ten bytes after each compiled script: the text <c>end_script</c>.</summary>
    internal static readonly byte[] Trailer = "end_script"u8.ToArray();

    /// <summary>
    /// Compiles one script. <paramref name="constStart"/> numbers its first constant (<c>const dataN</c>) and <paramref name="doOnceStart"/> its first
    /// do_once symbol: both counters belong to the compile session and not to the script, so the caller says where they start (0 for a new script).
    /// <paramref name="resolve"/> may give a constant for a name a missing header would have defined; <paramref name="notes"/> collects what the author may want to see.
    /// </summary>
    /// <exception cref="CompileError">The source is not a script this compiler accepts; the message says why and where.</exception>
    public static MissionScript Compile(string name, string source, Func<string, string> readInclude, int constStart = 0, int doOnceStart = 0,
        NameResolver? resolve = null, List<CompileNote>? notes = null, CompileLimits? limits = null)
    {
        limits ??= CompileLimits.Default;
        if (source.Length > limits.MaxSource) throw new CompileError("the script is longer than a million characters");
        (List<Token> tokens, string text) = ScriptPreprocessor.Run(source, readInclude, limits);
        return new ScriptParser(name, tokens, text, constStart, doOnceStart, resolve, notes, limits).Script();
    }

    /// <summary>The number of the first constant of a shipped script (the counter is the compile session's, the source cannot give it), or 0.</summary>
    public static int ConstStartOf(MissionScript script) => CounterStart(script, ConstNamePattern);

    /// <summary>The number of the first do_once symbol of a shipped script, or 0.</summary>
    public static int DoOnceStartOf(MissionScript script) => CounterStart(script, DoOnceNamePattern);

    private static int CounterStart(MissionScript script, Regex pattern)
    {
        foreach (ScriptSymbol symbol in script.Code.Symbols)
            if (pattern.Match(symbol.Name) is { Success: true } match && int.TryParse(match.Groups[1].Value, out int number)) return number;
        return 0;
    }

    private static readonly Regex ConstNamePattern = new("^const data([0-9]+)$", RegexOptions.CultureInvariant);
    private static readonly Regex DoOnceNamePattern = new("^do-once-([0-9]+)$", RegexOptions.CultureInvariant);

    /// <summary>A script or header as text: the game's files are single-byte text.</summary>
    /// <exception cref="CompileError">The file is longer than a million bytes.</exception>
    public static string ReadSource(string path)
    {
        FileInfo info = new(path);
        if (info.Length > MaxSource) throw new CompileError($"{info.Name} is longer than a million bytes");
        return Encoding.Latin1.GetString(File.ReadAllBytes(path));
    }

    /// <summary>Reads an included file by the game-relative path the source names (backslashes, any case: the game's files are named for Windows), only inside the game folder.</summary>
    public static Func<string, string> IncludesFrom(string gameRoot) => path => ReadSource(GameFile(gameRoot, path));

    /// <summary>The file a game-relative path names, found entry by entry in any case (the exact spelling first), never through a path that leaves the game folder.</summary>
    /// <exception cref="MissingInclude">An entry on the path is not there.</exception>
    /// <exception cref="CompileError">The path climbs out of the game folder, or does not end at a regular file inside it.</exception>
    public static string GameFile(string gameRoot, string path)
    {
        string root = Path.GetFullPath(gameRoot);
        string at = root;
        foreach (string part in path.Replace('\\', '/').Split('/'))
        {
            if (part.Length == 0 || part == ".") continue;
            if (part == "..") throw new CompileError($"a path cannot climb out of the game folder: {path}");
            string? match = Directory.Exists(at) ? EntryNamed(at, part) : null;
            at = match ?? throw new MissingInclude(path);
        }
        // A link that stays inside the game folder is a file inside it; one that leaves it (the file's own, or a folder's on the way) is not.
        string real = RealPath(at), realRoot = RealPath(root);
        string relative = Path.GetRelativePath(realRoot, real);
        if (relative == ".." || relative.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal) || Path.IsPathRooted(relative) ||
            !File.Exists(real) || !ScriptSources.IsRegularFile(real))
            throw new CompileError($"{path} is not a file inside the game folder");
        return at;
    }

    private static string? EntryNamed(string folder, string name)
    {
        string? found = new DirectoryInfo(folder).EnumerateFileSystemInfos().Select(entry => entry.Name)
            .Where(entry => string.Equals(entry, name, StringComparison.OrdinalIgnoreCase))
            .OrderBy(entry => entry != name).ThenBy(entry => entry, StringComparer.Ordinal).FirstOrDefault();
        return found is null ? null : Path.Combine(folder, found);
    }

    /// <summary>The path with every link on it followed (as <c>realpath</c> does).</summary>
    private static string RealPath(string path)
    {
        string full = Path.GetFullPath(path);
        string current = Path.GetPathRoot(full) ?? "";
        foreach (string part in full[current.Length..].Split(Path.DirectorySeparatorChar, StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, part);
            FileSystemInfo info = Directory.Exists(current) ? new DirectoryInfo(current) : new FileInfo(current);
            if (info.LinkTarget is not null && info.ResolveLinkTarget(returnFinalTarget: true) is { } target) current = target.FullName;
        }
        return current;
    }
}
