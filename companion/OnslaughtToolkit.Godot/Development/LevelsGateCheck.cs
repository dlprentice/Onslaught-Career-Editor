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
        Dictionary<string, string[]>? table = null, terrainTable = null;
        if (tablePath.Length > 0)
        {
            table = [];
            terrainTable = [];
            foreach (string line in File.ReadLines(tablePath).Skip(1))
            {
                string[] cells = line.Split('\t');
                if (cells.Length != 6) continue;
                (cells[1] == "TERRAIN" ? terrainTable : table)[cells[0] + "\t" + cells[1]] = cells[2..];
            }
        }

        List<string> failures = [];
        HashSet<string> seen = [], seenTerrain = [];
        int bodies = 0, exact = 0, matched = 0, terrains = 0, terrainsMatched = 0;
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
        foreach (string failure in failures.Take(25)) printError("FAIL: " + failure);
        print($"LEVELS_GATE: {bodies} world bodies in {archives.Count} level archives; byte-identical round trips {exact}; " +
                 (table is null ? "no reference table given" : $"fields equal to the reference's on {matched} of {table.Count} rows") +
                 $"; {terrains} terrains" + (terrainTable is null ? "" : $", heights equal to the reference's lookup on {terrainsMatched} of {terrainTable.Count}") + $"; {failures.Count} failures");
        return failures.Count == 0 && bodies > 0 ? 0 : 1;
    }

    /// <summary>
    /// The terrain of one archive: it reads, and when a table is given its samples, scale, water and the heights the lookup answers
    /// at a grid reaching past the square and at every thing of the level's own world are the reference's.
    /// </summary>
    private static void CheckTerrain(int level, LevelWorlds worlds, Dictionary<string, string[]>? table, HashSet<string> seen, List<string> failures, ref int terrains, ref int matched)
    {
        string name = $"{level:D3} TERRAIN";
        terrains++;
        Heightfield field;
        WorldBody world;
        try
        {
            field = Heightfield.Read(worlds.Terrain!);
            world = WorldBody.Read(worlds.RealBody!);
        }
        catch (InvalidDataException error)
        {
            failures.Add($"{name}: refused: {error.Message}");
            return;
        }
        if (table is null) return;
        string key = $"{level:D3}\tTERRAIN";
        if (!table.TryGetValue(key, out string[]? row))
        {
            failures.Add($"{name}: the reference table has no row for it");
            return;
        }
        seen.Add(key);
        List<(float X, float Y)> positions = [];
        for (int j = 0; j < 33; j++)
            for (int i = 0; i < 33; i++) positions.Add(((float)(i * 16 + 0.37), (float)(j * 16 + 0.71)));
        positions.AddRange(world.Things.Select(thing => (thing.Init.Position.X, thing.Init.Position.Y)));
        byte[] heights = new byte[positions.Count * 4];
        for (int i = 0; i < positions.Count; i++) BitConverter.TryWriteBytes(heights.AsSpan(i * 4), BitConverter.SingleToUInt32Bits(field.HeightAt(positions[i].X, positions[i].Y)));
        string digest = Convert.ToHexStringLower(SHA256.HashData(heights));
        string scaleAndWater = $"{BitConverter.SingleToUInt32Bits(field.Scale):x8}:{BitConverter.SingleToUInt32Bits(field.Water):x8}";
        if (row[0] == scaleAndWater && row[1] == field.SamplesSha256() && row[2] == positions.Count.ToString() && row[3] == digest) matched++;
        else failures.Add($"{name}: the table says {row[0]}, {row[1][..12]} and {row[2]} heights hashing to {row[3][..12]}; here {scaleAndWater}, {field.SamplesSha256()[..12]} and {positions.Count} heights hashing to {digest[..12]}");
    }
}
