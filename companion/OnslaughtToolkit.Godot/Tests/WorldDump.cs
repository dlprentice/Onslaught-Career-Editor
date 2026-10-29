// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The reference dump of a world body (tools/level_editor_vectors.py, <c>dump_lines</c>): one <c>path = value</c> line per
/// field, sorted. Paths and values are the Toolkit reference model's: integers in decimal, floats as their four stored
/// bytes in hex, strings in double quotes with every byte outside printable ASCII as <c>\xNN</c>, and the regions the
/// loader only skips as <c>bytes(LENGTH):SHA256</c>. Two readers that agree on every line agree on every field.
/// </summary>
internal static class WorldDump
{
    internal static List<string> Lines(WorldBody body)
    {
        List<string> lines = [];
        void Add(string path, string value) => lines.Add($"{path} = {value}");
        void Int(string path, int value) => Add(path, value.ToString(System.Globalization.CultureInfo.InvariantCulture));
        void Float(string path, float value) => Add(path, Hex(value));
        void Text(string path, string value) => Add(path, Quote(value));
        void Blob(string path, byte[] data) => Add(path, $"bytes({data.Length}):{Convert.ToHexStringLower(SHA256.HashData(data))}");
        void Vector(string path, System.Numerics.Vector3 value)
        {
            Float($"{path}[0]", value.X);
            Float($"{path}[1]", value.Y);
            Float($"{path}[2]", value.Z);
        }

        Int("version", body.Version);
        WorldHeader header = body.Header;
        Int("header.headerVersion", header.HeaderVersion);
        Int("header.unused[0]", header.Unused1);
        Int("header.unused[1]", header.Unused2);
        for (int i = 0; i < header.BattleEngineConfigurations.Count; i++) Text($"header.battleEngineConfigurations[{i}]", header.BattleEngineConfigurations[i]);
        if (header.V2Words is not null)
            for (int i = 0; i < header.V2Words.Length; i++) Int($"header.v2Words[{i}]", header.V2Words[i]);
        if (header.HeaderVersion >= 3) Int("header.worldType", header.WorldType);
        Int("baseLevel", body.BaseLevel);

        for (int s = 0; s < body.Scripts.Count; s++)
        {
            MissionScript script = body.Scripts[s];
            string at = $"scripts[{s}]";
            Text($"{at}.name", script.Name);
            ScriptCode code = script.Code;
            for (int i = 0; i < code.Instructions.Count; i++)
            {
                Int($"{at}.code.instructions[{i}][0]", code.Instructions[i].Opcode);
                Int($"{at}.code.instructions[{i}][1]", code.Instructions[i].Attribute);
            }
            for (int i = 0; i < code.EventPcs.Length; i++) Int($"{at}.code.eventPCs[{i}]", code.EventPcs[i]);
            for (int i = 0; i < code.Symbols.Count; i++)
            {
                ScriptSymbol symbol = code.Symbols[i];
                string sym = $"{at}.code.symbols[{i}]";
                Text($"{sym}.name", symbol.Name);
                Int($"{sym}.dataType", symbol.DataType);
                switch (symbol.Value)
                {
                    case null: Add($"{sym}.value", "null"); break;
                    case ScriptInt v: Int($"{sym}.value", v.Value); break;
                    case ScriptFloat v: Float($"{sym}.value", v.Value); break;
                    case ScriptText v: Text($"{sym}.value", v.Value); break;
                    case ScriptVector v: Vector($"{sym}.value", v.Value); break;
                }
                Int($"{sym}.symbolType", symbol.SymbolType);
                Int($"{sym}.index", symbol.Index);
                Int($"{sym}.flag", symbol.Flag);
            }
            Int($"{at}.code.nextSymbolIndex", code.NextSymbolIndex);
            for (int i = 0; i < code.EventFunctions.Count; i++)
            {
                Int($"{at}.code.eventFunctions[{i}].entryPC", code.EventFunctions[i].EntryPc);
                for (int j = 0; j < code.EventFunctions[i].Parameters.Count; j++)
                    Int($"{at}.code.eventFunctions[{i}].params[{j}]", code.EventFunctions[i].Parameters[j]);
            }
            Int($"{at}.code.tail[0]", code.Tail1);
            Int($"{at}.code.tail[1]", code.Tail2);
            Blob($"{at}.trailer", script.Trailer);
        }

        Int("mapNumber", body.MapNumber);
        for (int i = 0; i < body.NamedMeshes.Count; i++) Text($"namedMeshes[{i}]", body.NamedMeshes[i]);

        for (int t = 0; t < body.Things.Count; t++)
        {
            PlacedObject thing = body.Things[t];
            string at = $"things[{t}]";
            Int($"{at}.oid", thing.ObjectId);
            Text($"{at}.kind", thing.Kind);
            ObjectInit init = thing.Init;
            Vector($"{at}.init.position", init.Position);
            Vector($"{at}.init.orientation", init.Orientation);
            Int($"{at}.init.meshNumber", init.MeshNumber);
            Int($"{at}.init.allegiance", init.Allegiance);
            Int($"{at}.init.target", init.Target);
            Text($"{at}.init.script", init.Script);
            Text($"{at}.init.name", init.Name);
            Text($"{at}.init.spawnScript", init.SpawnScript);
            Int($"{at}.init.active", init.Active);
            if (init.AttachScriptsToUnits is int attach) Int($"{at}.init.attachScriptsToUnits", attach);
            if (init.Spawner is { } spawner)
            {
                Int($"{at}.init.spawner.amount", spawner.Amount);
                Float($"{at}.init.spawner.delay", spawner.Delay);
                Float($"{at}.init.spawner.squadDelay", spawner.SquadDelay);
                Float($"{at}.init.spawner.initialDelay", spawner.InitialDelay);
                Int($"{at}.init.spawner.squadSize", spawner.SquadSize);
                Text($"{at}.init.spawner.spawnUnit", spawner.SpawnUnit);
                if (spawner.SpawnerSpawnScript is { } spawnScript) Text($"{at}.init.spawner.spawnerSpawnScript", spawnScript);
            }
            if (init.Squad is { } squad)
            {
                Int($"{at}.init.squad.amount", squad.Amount);
                Int($"{at}.init.squad.mode", squad.Mode);
            }
            if (init.Cutscene is { } cutscene)
            {
                Text($"{at}.init.cutscene.file", cutscene.File);
                Text($"{at}.init.cutscene.linkTo", cutscene.LinkTo);
            }
            if (init.Start is { } start)
            {
                Int($"{at}.init.start.planeMode", start.PlaneMode);
                Int($"{at}.init.start.playerNumber", start.PlayerNumber);
            }
            if (init.Tree is { } tree) Text($"{at}.init.tree.treeType", tree.TreeType);
            if (init.SphereTrigger is { } trigger) Float($"{at}.init.sphereTrigger.radius", trigger.Radius);
            if (thing.Definition is { } definition)
            {
                Text($"{at}.definition", definition);
                Int($"{at}.diesOn", thing.DiesOn);
            }
        }

        for (int i = 0; i < body.TreeGroups.Count; i++)
        {
            TreeGroup group = body.TreeGroups[i];
            Float($"treeGroups[{i}].y0", group.Y0);
            Float($"treeGroups[{i}].x0", group.X0);
            Float($"treeGroups[{i}].y1", group.Y1);
            Float($"treeGroups[{i}].x1", group.X1);
            Int($"treeGroups[{i}].count", group.Count);
            Text($"treeGroups[{i}].treeType", group.TreeType);
            Int($"treeGroups[{i}].seed", group.Seed);
        }
        for (int i = 0; i < body.TreeTypes.Count; i++)
        {
            Text($"treeTypes[{i}].name", body.TreeTypes[i].Name);
            for (int j = 0; j < body.TreeTypes[i].Positions.Count; j++)
            {
                TreePosition position = body.TreeTypes[i].Positions[j];
                Float($"treeTypes[{i}].positions[{j}][0]", position.X);
                Float($"treeTypes[{i}].positions[{j}][1]", position.Y);
                Int($"treeTypes[{i}].positions[{j}][2]", position.Kind);
            }
        }

        InfluenceMap influence = body.InfluenceMap;
        Int("influenceMap.version", influence.Version);
        Int("influenceMap.nodes", influence.Nodes);
        Blob("influenceMap.nodeBytes", influence.NodeBytes);
        Int("influenceMap.links", influence.Links);
        Blob("influenceMap.linkBytes", influence.LinkBytes);

        for (int i = 0; i < body.WaypointPaths.Count; i++)
        {
            Text($"waypointPaths[{i}].name", body.WaypointPaths[i].Name);
            for (int j = 0; j < body.WaypointPaths[i].Slots.Count; j++) Int($"waypointPaths[{i}].slots[{j}]", body.WaypointPaths[i].Slots[j]);
        }

        WorldTimings timings = body.Timings;
        Float("timings.oldF", timings.OldF);
        Float("timings.oldG", timings.OldG);
        Float("timings.oldH", timings.OldH);
        Float("timings.preRun", timings.PreRun);
        Float("timings.pan", timings.Pan);
        Int("timings.sGrade", timings.SGrade);
        Int("timings.dGrade", timings.DGrade);
        Float("timings.timeLimit", timings.TimeLimit);
        Float("timings.fullScoreTime", timings.FullScoreTime);
        Float("timings.percentageScoreTime", timings.PercentageScoreTime);
        Float("timings.scorePercentage", timings.ScorePercentage);
        if (body.LegacyTimings is { } legacy)
        {
            Int("legacyTimings[0]", legacy.A);
            Int("legacyTimings[1]", legacy.B);
            Int("legacyTimings[2]", legacy.C);
            Float("legacyTimings[3]", legacy.D);
            Float("legacyTimings[4]", legacy.E);
        }
        if (body.OccupancyGrids is { } grids)
            for (int i = 0; i < grids.Count; i++)
            {
                Int($"occupancyGrids[{i}].version", grids[i].Version);
                Blob($"occupancyGrids[{i}].data", grids[i].Data);
            }
        if (body.LegacyGridWords is { } words)
            for (int i = 0; i < words.Length; i++) Int($"legacyGridWords[{i}]", words[i]);
        if (body.LevelStartTime is float start0) Float("levelStartTime", start0);

        lines.Sort(StringComparer.Ordinal);
        return lines;
    }

    /// <summary>The SHA-256 of the sorted lines joined by newlines, with a final newline.</summary>
    internal static string Hash(IReadOnlyList<string> lines) =>
        Convert.ToHexStringLower(SHA256.HashData(Encoding.ASCII.GetBytes(string.Join("\n", lines) + "\n")));

    internal static string Hex(float value)
    {
        Span<byte> bytes = stackalloc byte[4];
        BinaryPrimitives.WriteSingleLittleEndian(bytes, value);
        return "f32:" + Convert.ToHexStringLower(bytes);
    }

    internal static string Quote(string text)
    {
        StringBuilder quoted = new("\"");
        foreach (char c in text)
        {
            if (c is >= ' ' and <= '~' and not '"' and not '\\') quoted.Append(c);
            else quoted.Append("\\x").Append(((int)c).ToString("x2", System.Globalization.CultureInfo.InvariantCulture));
        }
        return quoted.Append('"').ToString();
    }
}
