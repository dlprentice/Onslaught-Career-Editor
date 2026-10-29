// SPDX-License-Identifier: GPL-3.0-only
using System.Text.RegularExpressions;
using System.Globalization;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>Something the compiler did that the author may want to see. <see cref="Line"/> is 0-based; <see cref="Kind"/> is "grouping" (how a mixed chain of operators was grouped), "handler" (a handler the game never calls) or "declaration".</summary>
public sealed record CompileNote(int Line, string Kind, string Text);

/// <summary>
/// What the compiler refuses instead of running out of stack, time or memory: the characters of a script or one included text (file readers also cap header bytes), the tokens of a
/// script once <c>#define</c> names are replaced, the names looked at while replacing them (a define can expand to nothing, so tokens alone do not
/// bound the work), the number and total characters of included headers, and how deep statements and expressions may nest (the parser calls itself for each level). The defaults are the reference's;
/// the tests pass smaller ones to put each limit exactly at its edge.
/// </summary>
public sealed record CompileLimits(int MaxSource = 1 << 20, int MaxTokens = 1 << 20, int MaxExpansionSteps = 4 << 20, int MaxDepth = 100,
    int MaxIncludes = 128, int MaxIncludeChars = 2 << 20)
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
    internal const string CounterPast = "a counter of the compile session is past 2147483647";

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
        if (PythonText.CharacterCount(source) > limits.MaxSource) throw new CompileError("the script is longer than a million characters");
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
            if (pattern.Match(symbol.Name) is { Success: true } match)
            {
                string digits = match.Groups[1].Value.TrimStart('0');
                if (digits.Length == 0) return 0;
                if (digits.Length > 10 || !int.TryParse(digits, NumberStyles.None, CultureInfo.InvariantCulture, out int number))
                    throw new CompileError(CounterPast);
                return number;
            }
        return 0;
    }

    private static readonly Regex ConstNamePattern = new("\\Aconst data([0-9]+)\\z", RegexOptions.CultureInvariant);
    private static readonly Regex DoOnceNamePattern = new("\\Ado-once-([0-9]+)\\z", RegexOptions.CultureInvariant);

    /// <summary>A script or header as single-byte text, read from a regular file without following its final entry.</summary>
    /// <exception cref="CompileError">The file cannot be safely read, or is longer than a million bytes.</exception>
    public static string ReadSource(string path) => ScriptSourceReader.ReadPath(path);

    /// <summary>Reads an included file by the game-relative path the source names (backslashes, any case: the game's files are named for Windows), only inside the game folder.</summary>
    public static Func<string, string> IncludesFrom(string gameRoot) => path => ReadGameSource(gameRoot, path);

    /// <summary>Reads a game-relative source while holding the selected directories and file open; links below the game folder are refused.</summary>
    public static string ReadGameSource(string gameRoot, string path) => ScriptSourceReader.ReadInGame(gameRoot, path);

    /// <summary>
    /// Looks up a game-relative path for display. A later open may see a changed path; use <see cref="ReadGameSource"/> for reading.
    /// </summary>
    /// <exception cref="MissingInclude">An entry on the path is not there.</exception>
    /// <exception cref="CompileError">The path climbs out of the game folder, or does not end at a regular file inside it.</exception>
    public static string GameFile(string gameRoot, string path) => ScriptSourceReader.Locate(gameRoot, path);
}
