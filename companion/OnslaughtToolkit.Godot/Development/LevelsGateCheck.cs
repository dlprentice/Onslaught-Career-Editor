// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Tests;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// The retail conformance check behind <see cref="LevelsGate"/>, free of Godot types so that it can also run in a plain
/// console host. Read-only: the game folder is only read, and only counts and short hashes are printed.
/// </summary>
internal static class LevelsGateCheck
{
    /// <summary>0 when every body round-trips (and matches the table, when one is given), 1 when one does not, 2 for no game.</summary>
    internal static int Run(string game, string tablePath, Action<string> print, Action<string> printError)
    {
        IReadOnlyList<LevelArchiveFile> archives = game.Length == 0 ? [] : LevelArchive.List(game);
        if (archives.Count == 0)
        {
            printError("Set BEA_GAME to a game folder with data/resources/NNN_res_PC.aya files.");
            return 2;
        }
        Dictionary<string, string[]>? table = null, terrainTable = null, scriptsTable = null;
        if (tablePath.Length > 0)
        {
            table = [];
            terrainTable = [];
            scriptsTable = [];
            foreach (string line in File.ReadLines(tablePath).Skip(1))
            {
                string[] cells = line.Split('\t');
                if (cells.Length != 6) continue;
                (cells[1] == "TERRAIN" ? terrainTable : cells[1] == "SCRIPTS" ? scriptsTable : table)[cells[0] + "\t" + cells[1]] = cells[2..];
            }
        }

        List<string> failures = [];
        HashSet<string> seen = [], seenTerrain = [], seenScripts = [];
        int bodies = 0, exact = 0, matched = 0, terrains = 0, terrainsMatched = 0, scriptLists = 0, scriptListsMatched = 0, scriptsListed = 0, sourcesFound = 0;
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
            if (worlds.RealBody is not null) CheckScripts(game, archive.Level, worlds, scriptsTable, seenScripts, failures, ref scriptLists, ref scriptListsMatched, ref scriptsListed, ref sourcesFound);
            if (worlds.Terrain is not null && worlds.RealBody is not null) CheckTerrain(archive.Level, worlds, terrainTable, seenTerrain, failures, ref terrains, ref terrainsMatched);
            foreach ((string tag, byte[]? body) in new[] { ("BSWD", worlds.BaseBody), ("RLWD", worlds.RealBody) })
            {
                if (body is null) continue;
                string key = $"{archive.Level:D3}\t{tag}", name = $"{archive.Level:D3} {tag}";
                bodies++;
                WorldBody model;
                try
                {
                    model = WorldBody.Read(body);
                }
                catch (InvalidDataException error)
                {
                    failures.Add($"{name}: refused: {error.Message}");
                    continue;
                }
                byte[] again = model.Write();
                if (again.AsSpan().SequenceEqual(body)) exact++;
                else failures.Add($"{name}: written again it differs ({body.Length} to {again.Length} bytes)");
                if (table is null) continue;
                if (!table.TryGetValue(key, out string[]? row))
                {
                    failures.Add($"{name}: the reference table has no row for it");
                    continue;
                }
                seen.Add(key);
                List<string> lines = WorldDump.Lines(model);
                string sha = Convert.ToHexStringLower(SHA256.HashData(body)), dump = WorldDump.Hash(lines);
                if (row[0] == body.Length.ToString() && row[1] == sha && row[2] == lines.Count.ToString() && row[3] == dump) matched++;
                else failures.Add($"{name}: the table says {row[0]} bytes, {row[2]} fields and dump {row[3][..12]}; here {body.Length} bytes, {lines.Count} fields and dump {dump[..12]}");
            }
        }
        if (table is not null)
            foreach (string key in table.Keys.Except(seen)) failures.Add($"{key.Replace('\t', ' ')}: in the reference table but not read here");
        if (terrainTable is not null)
            foreach (string key in terrainTable.Keys.Except(seenTerrain)) failures.Add($"{key.Replace('\t', ' ')}: in the reference table but not read here");
        if (scriptsTable is not null)
            foreach (string key in scriptsTable.Keys.Except(seenScripts)) failures.Add($"{key.Replace('\t', ' ')}: in the reference table but not read here");
        foreach (string failure in failures.Take(25)) printError("FAIL: " + failure);
        print($"LEVELS_GATE: {bodies} world bodies in {archives.Count} level archives; byte-identical round trips {exact}; " +
                 (table is null ? "no reference table given" : $"fields equal to the reference's on {matched} of {table.Count} rows") +
                 $"; {terrains} terrains" + (terrainTable is null ? "" : $", heights equal to the reference's lookup on {terrainsMatched} of {terrainTable.Count}") +
                 $"; {scriptLists} script lists" + (scriptsTable is null ? "" : $", equal to the reference's on {scriptListsMatched} of {scriptsTable.Count}") +
                 $", {scriptsListed} scripts of which {sourcesFound} find their source; {failures.Count} failures");
        return failures.Count == 0 && bodies > 0 ? 0 : 1;
    }

    /// <summary>
    /// The scripts of one archive as the Level editor lists them (<see cref="LevelEditorModel.ListScripts"/>): their catalog lines and the sources
    /// the finder reads for them hash as the Toolkit reference's do (<c>level_editor_vectors.py</c>'s SCRIPTS row), and every listed script finds its
    /// source in an installed game (a game missing sources, as a partial copy may be, fails here by count: the table says how many it found).
    /// </summary>
    private static void CheckScripts(string game, int level, LevelWorlds worlds, Dictionary<string, string[]>? table, HashSet<string> seen, List<string> failures,
        ref int lists, ref int matched, ref int listed, ref int found)
    {
        string name = $"{level:D3} SCRIPTS", key = $"{level:D3}\tSCRIPTS";
        lists++;
        IReadOnlyList<ScriptEntry> entries;
        try
        {
            entries = LevelEditorModel.ListScripts(WorldBody.Read(worlds.RealBody!), worlds);
        }
        catch (InvalidDataException error)
        {
            failures.Add($"{name}: the level's own world was refused: {error.Message}");
            return;
        }
        List<string> lines = [], sourceLines = [];
        int here = 0;
        foreach (ScriptEntry entry in entries)
        {
            string tag = entry.FromBaseWorld ? "base" : "own";
            ScriptSummary summary = entry.Summary;
            lines.Add(string.Join('|', tag, summary.Name, summary.Instructions.ToString(System.Globalization.CultureInfo.InvariantCulture), string.Join(',', summary.Events),
                string.Join(',', summary.Calls.Select(call => $"{call.Name}:{call.Count}")), string.Join(',', summary.Uses.Select(use => $"{use.Row}:{use.Role}"))));
            if (ScriptSources.Find(game, entry.SourceLevel, summary.Name).Source is { } source)
            {
                here++;
                sourceLines.Add($"{tag}|{summary.Name}|{Convert.ToHexStringLower(SHA256.HashData(System.Text.Encoding.Latin1.GetBytes(source.Text)))}");
            }
        }
        listed += entries.Count;
        found += here;
        if (table is null) return;
        if (!table.TryGetValue(key, out string[]? row))
        {
            failures.Add($"{name}: the reference table has no row for it");
            return;
        }
        seen.Add(key);
        string counts = $"{entries.Count(entry => !entry.FromBaseWorld)}:{entries.Count(entry => entry.FromBaseWorld)}", catalog = WorldDump.Hash(lines), sources = WorldDump.Hash(sourceLines);
        if (row[0] == counts && row[1] == catalog && row[2] == $"{here}/{entries.Count}" && row[3] == sources) matched++;
        else failures.Add($"{name}: the table says {row[0]} scripts, catalog {row[1][..12]} and {row[2]} sources hashing to {row[3][..12]}; here {counts}, catalog {catalog[..12]} and {here}/{entries.Count} sources hashing to {sources[..12]}");
    }

    /// <summary>
    /// The terrain of one archive: it reads, and when a table is given its samples, scale, water and the heights the lookup answers
    /// at a grid reaching past the square and at every thing of the level's own world are the reference's. A terrain the reference
    /// refuses has a "refused" row, and this reader must refuse it too.
    /// </summary>
    private static void CheckTerrain(int level, LevelWorlds worlds, Dictionary<string, string[]>? table, HashSet<string> seen, List<string> failures, ref int terrains, ref int matched)
    {
        string name = $"{level:D3} TERRAIN", key = $"{level:D3}\tTERRAIN";
        terrains++;
        string[]? row = null;
        bool listed = table is not null && table.TryGetValue(key, out row);
        Heightfield? field = null;
        string refusal = "";
        try
        {
            field = Heightfield.Read(worlds.Terrain!);
        }
        catch (InvalidDataException error)
        {
            refusal = error.Message;
        }
        if (field is null)
        {
            if (table is null) failures.Add($"{name}: refused: {refusal}");
            else if (!listed) failures.Add($"{name}: refused here ({refusal}) and the reference table has no row for it");
            else if (row![0] == "refused")
            {
                seen.Add(key);
                matched++;
            }
            else failures.Add($"{name}: refused here ({refusal}) but the reference reads it");
            return;
        }
        WorldBody world;
        try
        {
            world = WorldBody.Read(worlds.RealBody!);
        }
        catch (InvalidDataException error)
        {
            failures.Add($"{name}: the level's own world was refused: {error.Message}");
            return;
        }
        if (table is null) return;
        if (!listed)
        {
            failures.Add($"{name}: the reference table has no row for it");
            return;
        }
        seen.Add(key);
        if (row![0] == "refused")
        {
            failures.Add($"{name}: the reference refuses it; here it reads");
            return;
        }
        List<(float X, float Y)> positions = [];
        for (int j = 0; j < 33; j++)
            for (int i = 0; i < 33; i++) positions.Add(((float)(i * 16 + 0.37), (float)(j * 16 + 0.71)));
        positions.AddRange(world.Things.Select(thing => (thing.Init.Position.X, thing.Init.Position.Y)));
        byte[] heights = new byte[positions.Count * 4];
        for (int i = 0; i < positions.Count; i++) BitConverter.TryWriteBytes(heights.AsSpan(i * 4), BitConverter.SingleToUInt32Bits(field.HeightAt(positions[i].X, positions[i].Y)));
        string digest = Convert.ToHexStringLower(SHA256.HashData(heights));
        string scaleAndWater = $"{BitConverter.SingleToUInt32Bits(field.Scale):x8}:{BitConverter.SingleToUInt32Bits(field.Water):x8}";
        if (row[0] == scaleAndWater && row[1] == field.SamplesSha256() && row[2] == positions.Count.ToString() && row[3] == digest) matched++;
        else failures.Add($"{name}: the table says {row[0]}, {row[1][..Math.Min(12, row[1].Length)]} and {row[2]} heights hashing to {row[3][..Math.Min(12, row[3].Length)]}; here {scaleAndWater}, {field.SamplesSha256()[..12]} and {positions.Count} heights hashing to {digest[..12]}");
    }
}
