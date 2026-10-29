// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// The inverse of <see cref="WorldBodyReader"/> (the Toolkit's <c>write_world_body</c>): the bytes
/// <c>CWorld::LoadWorld</c> reads for a body, refusing anything the format's fixed-width fields cannot hold and any
/// field a version needs and the body leaves unset.
/// </summary>
internal static class WorldBodyWriter
{
    internal static byte[] Write(WorldBody model)
    {
        int version = model.Version;
        if (version is < WorldBody.MinVersion or > WorldBody.MaxVersion)
            throw new InvalidDataException($"world version {version} outside {WorldBody.MinVersion}..{WorldBody.MaxVersion} (LoadWorld refuses it)");
        ByteWriter w = new();
        w.UInt16(version);

        WorldHeader header = model.Header;
        w.Int32(header.HeaderVersion);
        w.Int32(header.Unused1);
        w.Int32(header.Unused2);
        w.Int32(header.BattleEngineConfigurations.Count);
        foreach (string name in header.BattleEngineConfigurations) w.LString(name);
        if (header.HeaderVersion >= 2)
            foreach (int word in Fixed(header.V2Words, 3, "the header's version 2 words")) w.Int32(word);
        if (header.HeaderVersion >= 3) w.Int32(header.WorldType);
        w.Int32(model.BaseLevel);

        w.Int32(model.Scripts.Count);
        foreach (MissionScript? script in model.Scripts) WriteScript(w, Need(script, "a script"));

        w.Int32(model.MapNumber);
        w.Int32(model.NamedMeshes.Count);
        foreach (string name in model.NamedMeshes) w.LString(name, LengthKind.UnsignedByte);

        if (model.Things.Count > WorldBody.MaxThings)
            throw new InvalidDataException($"LoadWorld's thing array holds {WorldBody.MaxThings} records");
        w.UInt16(model.Things.Count);
        foreach (PlacedObject thing in model.Things)
        {
            w.Int32(thing.ObjectId);
            WriteInit(w, thing.Init, version, ObjectKinds.ClassOf(thing.ObjectId));
            if (ObjectKinds.IsDefined(thing.ObjectId))
            {
                w.LString(Need(thing.Definition, "a defined thing's definition"));
                w.Int32(thing.DiesOn);
            }
        }

        w.Int16(model.TreeGroups.Count);
        foreach (TreeGroup group in model.TreeGroups)
        {
            w.Single(group.Y0);
            w.Single(group.X0);
            w.Single(group.Y1);
            w.Single(group.X1);
            w.Int32(group.Count);
            w.LString(group.TreeType);
            w.Int32(group.Seed);
        }

        w.Int32(model.TreeTypes.Count);
        foreach (TreeType type in model.TreeTypes)
        {
            w.LString(type.Name);
            w.Int32(type.Positions.Count);
            foreach (TreePosition position in type.Positions)
            {
                w.Single(position.X);
                w.Single(position.Y);
                w.Int32(position.Kind);
            }
        }

        InfluenceMap influence = model.InfluenceMap;
        if (influence.Version is not (0 or 1)) throw new InvalidDataException($"influence map version {influence.Version} is not 0 or 1");
        if (influence.NodeBytes.Length != (long)influence.Nodes * InfluenceMap.NodeSize(influence.Version) ||
            influence.LinkBytes.Length != (long)influence.Links * InfluenceMap.LinkSize(influence.Version))
            throw new InvalidDataException("influence map counts do not match its bytes");
        w.UInt16(influence.Version);
        w.Int32(influence.Nodes);
        w.Raw(influence.NodeBytes);
        w.Int32(influence.Links);
        w.Raw(influence.LinkBytes);

        w.Int16(model.WaypointPaths.Count);
        foreach (WaypointPath path in model.WaypointPaths)
        {
            w.LString(path.Name);
            w.Int32(path.Slots.Count);
            foreach (short slot in path.Slots) w.Int16(slot);
        }

        WorldTimings timings = model.Timings;
        foreach (float value in (ReadOnlySpan<float>)[timings.OldF, timings.OldG, timings.OldH, timings.PreRun, timings.Pan]) w.Single(value);
        w.Int32(timings.SGrade);
        w.Int32(timings.DGrade);
        foreach (float value in (ReadOnlySpan<float>)[timings.TimeLimit, timings.FullScoreTime, timings.PercentageScoreTime, timings.ScorePercentage])
            w.Single(value);

        if (version is >= 45 and < 48)
        {
            LegacyTimings legacy = Need(model.LegacyTimings, "the version 45 to 47 timings");
            w.Int32(legacy.A);
            w.Int32(legacy.B);
            w.Int32(legacy.C);
            w.Single(legacy.D);
            w.Single(legacy.E);
        }
        if (version >= 47)
        {
            List<OccupancyGrid> grids = Need(model.OccupancyGrids, "the occupancy grids");
            if (grids.Count != 3) throw new InvalidDataException("a world has exactly three occupancy grids");
            foreach (OccupancyGrid grid in grids)
            {
                if (grid.Data.Length != OccupancyGrid.DataSize(grid.Version))
                    throw new InvalidDataException($"occupancy grid version {grid.Version} with {grid.Data.Length} bytes");
                w.Int32(grid.Version);
                w.Raw(grid.Data);
            }
            if (version < 50)
                foreach (int word in Fixed(model.LegacyGridWords, 5, "the version 47 to 49 grid words")) w.Int32(word);
        }
        if (version >= 49) w.Single(Need(model.LevelStartTime, "the level start time"));
        return w.ToArray();
    }

    /// <summary>The bytes the world stores for one script: its name, its code and its trailer. Two scripts are the same record when these are the same bytes.</summary>
    /// <exception cref="InvalidDataException">The script holds something the format cannot store.</exception>
    internal static byte[] ScriptBytes(MissionScript script)
    {
        ByteWriter w = new();
        WriteScript(w, script);
        return w.ToArray();
    }

    private static void WriteScript(ByteWriter w, MissionScript script)
    {
        w.LString(Need(script.Name, "a script's name"), LengthKind.Int32);
        WriteCode(w, Need(script.Code, "a script's code"));
        w.Raw(Fixed(script.Trailer, 10, "a script's trailer"));
    }

    private static void WriteCode(ByteWriter w, ScriptCode code)
    {
        ScriptCount(w, code.Instructions.Count, "instructions");
        foreach (ScriptInstruction instruction in code.Instructions)
        {
            w.Int32(instruction.Opcode);
            w.Int32(instruction.Attribute);
        }
        foreach (int pc in Fixed(code.EventPcs, ScriptCode.EventCount, "a script's event entry points")) w.Int32(pc);
        ScriptCount(w, code.Symbols.Count, "symbols");
        foreach (ScriptSymbol? item in code.Symbols)
        {
            ScriptSymbol symbol = Need(item, "a script symbol");
            w.LString(Need(symbol.Name, "a script symbol's name"), LengthKind.Int32);
            w.Int32(symbol.DataType);
            if (symbol.DataType != 0) WriteValue(w, symbol.DataType, symbol.Value);
            w.Int32(symbol.SymbolType);
            w.Int32(symbol.Index);
            w.Int32(symbol.Flag);
        }
        w.Int32(code.NextSymbolIndex);
        ScriptCount(w, code.EventFunctions.Count, "handlers");
        foreach (EventFunction? item in code.EventFunctions)
        {
            EventFunction function = Need(item, "a script handler");
            w.Int32(function.EntryPc);
            ScriptCount(w, function.Parameters.Count, "handler parameters");
            foreach (int parameter in function.Parameters) w.Int32(parameter);
        }
        w.Int32(code.Tail1);
        w.Int32(code.Tail2);
    }

    /// <summary>A script count the strict reader can read back; larger values cannot form a usable world record.</summary>
    private static void ScriptCount(ByteWriter w, int count, string what)
    {
        if (count > ByteReader.CountLimit) throw new InvalidDataException($"a script has more {what} than the reader's {ByteReader.CountLimit} limit");
        w.Int32(count);
    }

    private static void WriteValue(ByteWriter w, int dataType, ScriptValue? value)
    {
        switch (dataType, value)
        {
            case (1 or 4 or 5, ScriptInt integer):
                w.Int32(integer.Value);
                break;
            case (2, ScriptFloat number):
                w.Single(number.Value);
                break;
            case (3, ScriptText text):
                w.LString(Need(text.Value, "a script text value"), LengthKind.Int32);
                break;
            case (6, ScriptVector vector):
                w.Single(vector.Value.X);
                w.Single(vector.Value.Y);
                w.Single(vector.Value.Z);
                break;
            case (>= 1 and <= 6, _):
                throw new InvalidDataException($"a script symbol of data type {dataType} holds the wrong kind of value");
            default:
                throw new InvalidDataException($"unknown script data type {dataType}");
        }
    }

    private static void WriteInit(ByteWriter w, ObjectInit init, int version, ObjectClass objectClass)
    {
        WriteVector(w, init.Position);
        WriteVector(w, init.Orientation);
        w.Int32(init.MeshNumber);
        w.Int32(init.Allegiance);
        w.Int32(init.Target);
        w.CString(init.Script);
        w.CString(init.Name);
        w.CString(init.SpawnScript);
        w.Int32(init.Active);
        if (version > 45) w.Int32(Need(init.AttachScriptsToUnits, "a thing's attach-scripts word"));
        switch (objectClass)
        {
            case ObjectClass.Spawner:
                SpawnerInit spawner = Need(init.Spawner, "a spawner's fields");
                w.Int32(spawner.Amount);
                w.Single(spawner.Delay);
                w.Single(spawner.SquadDelay);
                w.Single(spawner.InitialDelay);
                w.Int32(spawner.SquadSize);
                w.CString(spawner.SpawnUnit);
                if (version > 43) w.CString(Need(spawner.SpawnerSpawnScript, "a spawner's spawn script"));
                break;
            case ObjectClass.Squad:
                SquadInit squad = Need(init.Squad, "a squad's fields");
                w.Int32(squad.Amount);
                w.Int32(squad.Mode);
                break;
            case ObjectClass.Cutscene:
                CutsceneInit cutscene = Need(init.Cutscene, "a cutscene's fields");
                w.CString(cutscene.File);
                w.CString(cutscene.LinkTo);
                break;
            case ObjectClass.Start:
                StartInit start = Need(init.Start, "a start's fields");
                w.Int32(start.PlaneMode);
                w.Int32(start.PlayerNumber);
                break;
            case ObjectClass.Tree:
                w.CString(Need(init.Tree, "a tree's fields").TreeType);
                break;
            case ObjectClass.SphereTrigger:
                w.Single(Need(init.SphereTrigger, "a sphere trigger's fields").Radius);
                break;
        }
    }

    private static void WriteVector(ByteWriter w, Vector3 vector)
    {
        w.Single(vector.X);
        w.Single(vector.Y);
        w.Single(vector.Z);
    }

    private static T Need<T>(T? value, string what) where T : class =>
        value ?? throw new InvalidDataException($"{what} is missing");

    private static T Need<T>(T? value, string what) where T : struct =>
        value ?? throw new InvalidDataException($"{what} is missing");

    private static T[] Fixed<T>(T[]? values, int length, string what)
    {
        if (values is null || values.Length != length) throw new InvalidDataException($"{what} must hold exactly {length} values");
        return values;
    }
}
