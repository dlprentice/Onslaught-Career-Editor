// SPDX-License-Identifier: GPL-3.0-only
using System.Text.RegularExpressions;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>What a name in a script's source can stand for in the open level.</summary>
public enum NameKind
{
    /// <summary>An object of the level, by its own name.</summary>
    Object,

    /// <summary>An object of the level's base world (which the game loads with it), by its own name. The Level editor does not list those, so there is nothing to go to.</summary>
    BaseObject,

    /// <summary>A waypoint path of the level's own world.</summary>
    Path,

    /// <summary>A waypoint path of the level's base world, which the game finds before the level's own paths of that name. The Level editor does not draw it, so there is nothing to go to.</summary>
    BasePath,

    /// <summary>A script, by name.</summary>
    Script,

    /// <summary>An event that a script handles (<c>event "name"</c>).</summary>
    Handler,
}

/// <param name="Kind">What was found.</param>
/// <param name="Label">What to call it for the player.</param>
/// <param name="Index">An object's row in its world (the level's own, or the base world's for <see cref="NameKind.BaseObject"/>), a path's index in the world, or a script's index in the level's script list.</param>
/// <param name="ExactCase">False when the name matched only with other letter case.</param>
public readonly record struct NameMatch(NameKind Kind, string Label, int Index, bool ExactCase = true);

/// <summary>
/// A quoted text or a word of the source and where it is on its line. <see cref="PathArgument"/> is true for a quoted text that is the first argument of a
/// <c>FollowWaypoint</c> or <c>FollowWaypointWait</c> call: the game finds a waypoint path by name ignoring letter case there (and nowhere else).
/// </summary>
public readonly record struct SourceToken(string Text, bool Quoted, int Start, int Length, bool PathArgument = false);

/// <summary>
/// Names in a mission script's source and what they name in a level. The scripts take names as quoted texts (a thing, a waypoint path, an
/// event, a script), so a quoted text that is the name of an object, a path or a script of the open level is a link to it. The compiled
/// script holds the same texts as string constants and nothing says which function reads which text as what, so this goes by the name
/// alone: it finds what has that name and does not claim the script uses it as such.
/// </summary>
public static partial class ScriptNames
{
    [GeneratedRegex("[A-Za-z_][A-Za-z_0-9]*")]
    private static partial Regex Word();

    /// <summary>
    /// The quoted text or the word at a column of a line (a column is the position between two characters, so one just after a token is
    /// in it), or null on a comment, a space or a symbol. The quotes count as part of a quoted text but are not in <see cref="SourceToken.Text"/>.
    /// A quote that is never closed runs to the end of the line.
    /// </summary>
    public static SourceToken? TokenAt(string line, int column)
    {
        if (column < 0 || column > line.Length) return null;
        int i = 0;
        while (i < line.Length)
        {
            if (line[i] == '/' && i + 1 < line.Length && line[i + 1] == '/') return null;  // a comment: the rest of the line says nothing
            if (line[i] == '"')
            {
                int close = line.IndexOf('"', i + 1);
                int end = close < 0 ? line.Length : close + 1;
                if (column >= i && column <= end) return new SourceToken(line[(i + 1)..(close < 0 ? line.Length : close)], true, i + 1, (close < 0 ? line.Length : close) - i - 1, FollowsPathCall(line, i));
                i = end;
                continue;
            }
            if (char.IsAsciiLetter(line[i]) || line[i] == '_')
            {
                Match word = Word().Match(line, i);
                if (column >= word.Index && column <= word.Index + word.Length) return new SourceToken(word.Value, false, word.Index, word.Length);
                i = word.Index + word.Length;
                continue;
            }
            i++;
        }
        return null;
    }

    private static string PointsText(int count) => count == 1 ? "1 point" : $"{count} points";

    private static bool IsBlank(char c) => c is ' ' or '\t' or '\r' or '\f' or '\v';

    private static bool IsWordChar(char c) => c is (>= 'A' and <= 'Z') or (>= 'a' and <= 'z') or (>= '0' and <= '9') or '_';

    /// <summary>
    /// Whether the quote that opens a string at <paramref name="quote"/> is the first thing inside the parentheses of a call to <c>FollowWaypoint</c> or
    /// <c>FollowWaypointWait</c> (blanks allowed on either side of the parenthesis; the name is a whole word).
    /// </summary>
    internal static bool FollowsPathCall(string line, int quote)
    {
        int at = quote - 1;
        while (at >= 0 && IsBlank(line[at])) at--;
        if (at < 0 || line[at] != '(') return false;
        at--;
        while (at >= 0 && IsBlank(line[at])) at--;
        int end = at + 1;
        while (at >= 0 && IsWordChar(line[at])) at--;
        return line[(at + 1)..end] is "FollowWaypoint" or "FollowWaypointWait";
    }

    /// <summary>
    /// What a quoted text names in the level: the objects whose name it is (exactly, else in other letter case), the objects of the base
    /// world (<paramref name="baseWorld"/>, when the level has one) by the same rule, the waypoint paths of that name, the scripts of that
    /// name and the scripts that handle an event of that name. The scripts are <paramref name="scripts"/> in its order. Paths match exactly,
    /// except where the text is the path argument of a follow-waypoint call (<paramref name="pathsIgnoreCase"/>): the game keeps one list of
    /// paths, the base world's before the level's own, and takes the first whose name matches. This page models its C-locale byte comparison:
    /// ASCII letters match in either case, other bytes match exactly, and a NUL ends the name. A base world's path is a
    /// <see cref="NameKind.BasePath"/>; a match is marked when the compared spelling differs in case. The game's behavior under another
    /// process locale or native Windows has not been checked. This page does not resolve an empty quoted name. A path's label counts the
    /// points the game keeps (see <see cref="WaypointCatalog"/>).
    /// </summary>
    public static IReadOnlyList<NameMatch> Resolve(string text, WorldBody world, IReadOnlyList<ScriptEntry> scripts, WorldBody? baseWorld = null, bool pathsIgnoreCase = false)
    {
        if (text.Length == 0) return [];
        List<NameMatch> matches = [];
        AddObjects(matches, NameKind.Object, text, world);
        if (baseWorld is not null) AddObjects(matches, NameKind.BaseObject, text, baseWorld);
        if (pathsIgnoreCase)
        {
            // The game's one list of paths: the base world's, then the level's own; use the first C-locale byte match.
            if (FirstPath(text, baseWorld, NameKind.BasePath) is { } inBase) matches.Add(inBase);
            else if (FirstPath(text, world, NameKind.Path) is { } own) matches.Add(own);
        }
        else
        {
            for (int index = 0; index < world.WaypointPaths.Count; index++)
            {
                WaypointPath path = world.WaypointPaths[index];
                if (string.Equals(path.Name, text, StringComparison.Ordinal))
                    matches.Add(new NameMatch(NameKind.Path, $"path {path.Name} · {PointsText(WaypointCatalog.Rows(world, path).Count)}", index));
            }
        }
        for (int index = 0; index < scripts.Count; index++)
            if (string.Equals(scripts[index].Summary.Name, text, StringComparison.Ordinal))
                matches.Add(new NameMatch(NameKind.Script, scripts[index].FromBaseWorld ? $"script {text} (base world)" : $"script {text}", index));
        string handler = $"event \"{text}\"";
        for (int index = 0; index < scripts.Count; index++)
            if (scripts[index].Summary.Events.Contains(handler, StringComparer.Ordinal))
                matches.Add(new NameMatch(NameKind.Handler, $"event handled by {scripts[index].Summary.Name}", index));
        return matches;
    }

    /// <summary>The first path of a world matching the C-locale byte spelling, as a match of this kind, or null.</summary>
    private static NameMatch? FirstPath(string text, WorldBody? world, NameKind kind)
    {
        if (world is null) return null;
        string comparedText = PathPrefix(text);
        for (int index = 0; index < world.WaypointPaths.Count; index++)
        {
            WaypointPath path = world.WaypointPaths[index];
            string comparedName = PathPrefix(path.Name);
            if (PathEquals(comparedName, comparedText))
                return new NameMatch(kind, $"path {comparedName} · {PointsText(WaypointCatalog.Rows(world, path).Count)}", index, string.Equals(comparedName, comparedText, StringComparison.Ordinal));
        }
        return null;
    }

    /// <summary>The name seen by the game's C-string comparison; the stored path itself is not changed.</summary>
    private static string PathPrefix(string text)
    {
        int nul = text.IndexOf('\0');
        return nul < 0 ? text : text[..nul];
    }

    /// <summary>C-locale comparison of the Latin-1 decoded path bytes: fold ASCII capitals only.</summary>
    private static bool PathEquals(string left, string right)
    {
        if (left.Length != right.Length) return false;
        for (int i = 0; i < left.Length; i++)
        {
            char a = left[i], b = right[i];
            if (a is >= 'A' and <= 'Z') a = (char)(a + ('a' - 'A'));
            if (b is >= 'A' and <= 'Z') b = (char)(b + ('a' - 'A'));
            if (a != b) return false;
        }
        return true;
    }

    /// <summary>The objects of a world that have this name exactly, or, if none has, those that have it in other letter case.</summary>
    private static void AddObjects(List<NameMatch> matches, NameKind kind, string text, WorldBody world)
    {
        bool exactObject = world.Things.Any(thing => string.Equals(thing.Init.Name, text, StringComparison.Ordinal));
        for (int row = 0; row < world.Things.Count; row++)
        {
            PlacedObject thing = world.Things[row];
            bool exact = string.Equals(thing.Init.Name, text, StringComparison.Ordinal);
            if (exact || (!exactObject && string.Equals(thing.Init.Name, text, StringComparison.OrdinalIgnoreCase)))
                matches.Add(new NameMatch(kind, $"{thing.Kind} {row} · {thing.Label}", row, exact));
        }
    }
}

/// <summary>An object's place on a waypoint path: it is point <see cref="Position"/> (counting from 1) of <see cref="Count"/> on the path <see cref="Name"/>.</summary>
public readonly record struct PathStop(int PathIndex, string Name, int Position, int Count);

/// <summary>
/// The waypoint paths of a world body, read for display. A path names objects by their place in the world's thing list (its slots), which is what a
/// <c>PlacedObject</c>'s row is. The game's loader (<c>CWaypointPath::Load</c>) keeps a slot only if it indexes a loaded thing that is a waypoint, so a
/// slot past the list, and a slot that names a unit, a spawner or anything else, is dropped: those are not points of the path, are not drawn and are
/// not counted. (Read over every retail level the paths run from point to point under this reading: the median step between neighbouring points
/// is shortest at it and longer at any shift of it by one or two.)
/// </summary>
public static class WaypointCatalog
{
    /// <summary>The kind name of the objects a path can pass through.</summary>
    public const string WaypointKind = "waypoint";

    /// <summary>The paths an object is a point of, each once for every time the path passes through it. A point's place and a path's count are of the points kept.</summary>
    public static IReadOnlyList<PathStop> Through(WorldBody world, int row)
    {
        List<PathStop> stops = [];
        for (int index = 0; index < world.WaypointPaths.Count; index++)
        {
            WaypointPath path = world.WaypointPaths[index];
            IReadOnlyList<int> kept = Rows(world, path);
            for (int at = 0; at < kept.Count; at++)
                if (kept[at] == row) stops.Add(new PathStop(index, path.Name, at + 1, kept.Count));
        }
        return stops;
    }

    /// <summary>The points of a path: its slots that index a thing of the world that is a waypoint, in the path's order, as the loader keeps them.</summary>
    public static IReadOnlyList<int> Rows(WorldBody world, WaypointPath path) =>
        [.. path.Slots.Where(slot => slot >= 0 && slot < world.Things.Count && world.Things[slot].Kind == WaypointKind).Select(slot => (int)slot)];
}
