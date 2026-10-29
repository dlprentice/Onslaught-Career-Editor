// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Missions;
using OnslaughtToolkit.Companion.Tests;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// The retail conformance check behind <see cref="ScriptsGate"/>, free of Godot types so that it can also run in a plain console host.
/// Read-only: the game folder is only read, and only counts and names are printed.
/// </summary>
internal static class ScriptsGateCheck
{
    /// <summary>
    /// (folder level, script name) to how the installed source differs from the shipped script: the shipped script has statements, variables or
    /// handlers the file lacks (or the reverse), so the file is another revision. The same list as <c>tools/msl_gate.py</c>'s; described by
    /// structure, the scripts themselves stay out of the repository.
    /// </summary>
    internal static readonly Dictionary<(int Level, string Name), string> StaleSources = new()
    {
        [(201, "EnemyLander")] = "the shipped script has a variable and a started_dying handler where the file has a died handler, and posts different events",
        [(201, "EnemyLander2")] = "the shipped script has a variable and a started_dying handler where the file has a died handler",
        [(201, "LevelScript")] = "the shipped script has a variable, different print statements and a different message call",
        [(720, "battleline")] = "the shipped script has an objective check (a lookup, an Exists call and an objective-complete call) the file lacks",
        [(731, "Fenrir")] = "the shipped script makes three more components invulnerable before its waypoint call than the file does (7 against 4), and none after it",
        [(732, "Fenrir")] = "the shipped script makes three more components invulnerable before its waypoint call than the file does (7 against 4), and none after it",
        [(720, "Level720script")] = "one message call names a different speaker than the file does",
    };

    /// <summary>0 when every script is exact, assisted or a pinned stale source (and has the reference's status, when a table is given), 1 when one is not, 2 for no game.</summary>
    internal static int Run(string game, string tablePath, Action<string> print, Action<string> printError)
    {
        IReadOnlyList<LevelArchiveFile> archives = game.Length == 0 ? [] : LevelArchive.List(game);
        if (archives.Count == 0)
        {
            printError("Set BEA_GAME to a game folder with data/resources/NNN_res_PC.aya files.");
            return 2;
        }
        Dictionary<string, List<string>>? table = null;
        int tableRows = 0;
        if (tablePath.Length > 0)
        {
            table = [];
            foreach (string line in File.ReadLines(tablePath).Skip(1))
            {
                string[] cells = line.Split('\t');
                if (cells.Length < 4 || !int.TryParse(cells[0], out _)) continue;  // the summary line at the end is not a row
                string key = $"{cells[0]}\t{cells[1]}\t{cells[2]}";
                if (!table.TryGetValue(key, out List<string>? statuses)) table[key] = statuses = [];
                statuses.Add(cells[3]);
                tableRows++;
            }
        }
        Func<string, string> readInclude = ScriptCompiler.IncludesFrom(game);
        List<string> failures = [];
        SortedDictionary<string, int> counts = [];
        HashSet<(int, string)> seenStale = [];
        int scripts = 0, bodies = 0, bodiesRewritten = 0, tableMatched = 0;
        foreach (LevelArchiveFile archive in archives)
        {
            LevelWorlds worlds;
            try
            {
                worlds = LevelArchive.ReadFile(archive.Path);
            }
            catch (Exception error) when (error is InvalidDataException or IOException)
            {
                failures.Add($"{archive.Level:D3}: archive refused: {error.Message}");
                continue;
            }
            foreach ((string tag, byte[]? bytes, int folderLevel) in new[] { ("BSWD", worlds.BaseBody, worlds.BaseLevel), ("RLWD", worlds.RealBody, worlds.RealLevel) })
            {
                if (bytes is null) continue;
                WorldBody body;
                try
                {
                    body = WorldBody.Read(bytes);
                }
                catch (InvalidDataException error)
                {
                    failures.Add($"{archive.Level:D3} {tag}: refused: {error.Message}");
                    continue;
                }
                bodies++;
                bool replaced = false, allReplaced = true;
                for (int index = 0; index < body.Scripts.Count; index++)
                {
                    MissionScript shipped = body.Scripts[index];
                    var (status, _, compiled) = Judge(game, readInclude, folderLevel, shipped);
                    (int, string) staleKey = (folderLevel, shipped.Name);
                    if (status == "different" && StaleSources.ContainsKey(staleKey))
                    {
                        status = "stale source";
                        seenStale.Add(staleKey);
                    }
                    else if (StaleSources.ContainsKey(staleKey))
                    {
                        failures.Add($"{folderLevel} {shipped.Name}: listed as a stale source but it is {status}");
                        seenStale.Add(staleKey);
                    }
                    scripts++;
                    counts[status] = counts.GetValueOrDefault(status) + 1;
                    if (status is not ("exact" or "exact, assisted" or "stale source")) failures.Add($"{archive.Level:D3} {tag} {shipped.Name}: {status}");
                    if (table is not null)
                    {
                        string key = $"{archive.Level}\t{tag}\t{shipped.Name}";
                        if (table.TryGetValue(key, out List<string>? expected) && expected.Remove(status)) tableMatched++;
                        else failures.Add($"{archive.Level:D3} {tag} {shipped.Name}: the reference table says {(expected is { Count: > 0 } ? string.Join(" or ", expected) : "nothing")}; here {status}");
                    }
                    if (compiled is not null && status is "exact" or "exact, assisted")
                    {
                        body.Scripts[index] = compiled;
                        replaced = true;
                    }
                    else
                    {
                        allReplaced = false;
                    }
                }
                // The whole world body with every compiled script put in the place of the shipped one writes back to the bytes it was read from.
                if (replaced && allReplaced)
                {
                    if (body.Write().AsSpan().SequenceEqual(bytes)) bodiesRewritten++;
                    else failures.Add($"{archive.Level:D3} {tag}: with the compiled scripts put in, the world body writes to other bytes");
                }
            }
        }
        if (scripts == 0) failures.Add("no compiled scripts were found to compare: choose a game folder whose data/resources holds level archives");
        foreach ((int Level, string Name) key in StaleSources.Keys.Where(key => !seenStale.Contains(key))) failures.Add($"{key.Level} {key.Name}: listed as a stale source but no such script was met");
        if (table is not null)
            foreach ((string key, List<string> left) in table.Where(pair => pair.Value.Count > 0)) failures.Add($"{key.Replace('\t', ' ')}: in the reference table but not met here");
        foreach (string failure in failures.Take(25)) printError("FAIL: " + failure);
        print($"SCRIPTS_GATE: {scripts} scripts in {bodies} world bodies: " + string.Join(", ", counts.Select(pair => $"{pair.Value} {pair.Key}")) +
              $"; world bodies with every script compiled written back to their own bytes: {bodiesRewritten}; " +
              (table is null ? "no reference table given" : $"status equal to the reference's on {tableMatched} of {tableRows}") + $"; {failures.Count} failures");
        return failures.Count == 0 ? 0 : 1;
    }

    /// <summary>The status of one shipped script and why, with the compiled script when there is one (the shipped script's source compiled with the session's counters).</summary>
    private static (string Status, string Detail, MissionScript? Compiled) Judge(string game, Func<string, string> readInclude, int folderLevel, MissionScript shipped)
    {
        string name = shipped.Name;
        string source;
        try
        {
            source = ScriptCompiler.ReadSource(ScriptCompiler.GameFile(game, $"data\\MissionScripts\\level{folderLevel:D3}\\{name}.msl"));
        }
        catch (MissingInclude error)
        {
            return ("no source", $"{error.Path} is not in the game folder", null);
        }
        catch (CompileError error)
        {
            return ("no source", error.Message, null);
        }
        int constStart, doOnceStart;
        try
        {
            constStart = ScriptCompiler.ConstStartOf(shipped);
            doOnceStart = ScriptCompiler.DoOnceStartOf(shipped);
        }
        catch (CompileError error)
        {
            return ("refused", error.Message, null);
        }
        string status = "exact";
        MissionScript compiled;
        try
        {
            compiled = ScriptCompiler.Compile(name, source, readInclude, constStart, doOnceStart);
        }
        catch (MissingInclude error)
        {
            status = "exact, assisted";
            List<string> missing = [error.Path];

            string ReadMissingAsEmpty(string include)
            {
                try
                {
                    return readInclude(include);
                }
                catch (MissingInclude inner)
                {
                    if (!missing.Contains(inner.Path)) missing.Add(inner.Path);
                    return "";
                }
            }

            try
            {
                compiled = ScriptCompiler.Compile(name, source, ReadMissingAsEmpty, constStart, doOnceStart, AssistedResolver(shipped));
            }
            catch (CompileError inner)
            {
                return ("refused", $"{inner.Message} (without {string.Join(", ", missing)})", null);
            }
        }
        catch (CompileError error)
        {
            return ("refused", error.Message, null);
        }
        if (!compiled.Trailer.SequenceEqual(shipped.Trailer)) return ("different", "the trailer of the record", compiled);
        string[] ours = ScriptDump.Lines(compiled), theirs = ScriptDump.Lines(shipped);
        for (int line = 0; line < Math.Min(ours.Length, theirs.Length); line++)
            if (ours[line] != theirs[line]) return ("different", $"line {line} of the record: {ours[line]} against {theirs[line]}", compiled);
        return ours.Length == theirs.Length ? (status, "", compiled) : ("different", $"the record has {ours.Length} lines against {theirs.Length}", compiled);
    }

    /// <summary>Names a missing header would have defined: the shipped script's constant at the position where the compiler needs one.</summary>
    private static NameResolver AssistedResolver(MissionScript shipped) => (_, index) =>
        index < shipped.Code.Symbols.Count && shipped.Code.Symbols[index] is { DataType: >= 1 and <= 6, Value: { } value } symbol &&
        symbol.Name.StartsWith("const data", StringComparison.Ordinal) ? new ResolvedName(symbol.DataType, value) : null;
}
