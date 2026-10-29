// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// <c>CWorld::LoadWorld</c>'s read order (the Toolkit's <c>read_world_model</c>): the header, the compiled scripts, the
/// named meshes, every thing record, the trees, the influence map, the waypoint paths, the timings, the occupancy
/// grids and the version-dependent tail. Anything the loader would not accept, and any byte left over, is refused.
/// </summary>
internal static class WorldBodyReader
{
    internal static WorldBody Read(ReadOnlySpan<byte> body)
    {
        ByteReader r = new(body.ToArray());
        int version = r.UInt16();
        if (version is < WorldBody.MinVersion or > WorldBody.MaxVersion)
            throw new InvalidDataException($"world version {version} outside {WorldBody.MinVersion}..{WorldBody.MaxVersion}");
        WorldBody model = new() { Version = version };

        WorldHeader header = model.Header;
        header.HeaderVersion = r.Int32();
        header.Unused1 = r.Int32();
        header.Unused2 = r.Int32();
        for (int i = 0, n = r.Count(); i < n; i++) header.BattleEngineConfigurations.Add(r.LString());
        if (header.HeaderVersion >= 2) header.V2Words = [r.Int32(), r.Int32(), r.Int32()];
        if (header.HeaderVersion >= 3) header.WorldType = r.Int32();
        model.BaseLevel = r.Int32();

        for (int i = 0, n = r.Count(); i < n; i++)
        {
            MissionScript script = new() { Name = r.LString(LengthKind.Int32) };
            ReadCode(r, script.Code);
            script.Trailer = r.Bytes(10);
            model.Scripts.Add(script);
        }

        model.MapNumber = r.Int32();
        for (int i = 0, n = r.Count(); i < n; i++) model.NamedMeshes.Add(r.LString(LengthKind.UnsignedByte));

        for (int i = 0, n = r.CountUInt16(); i < n; i++)
        {
            PlacedObject thing = new() { ObjectId = r.Int32() };
            ObjectClass objectClass = ObjectKinds.ClassOf(thing.ObjectId);
            thing.Init = ReadInit(r, version, objectClass);
            if (ObjectKinds.IsDefined(thing.ObjectId))
            {
                thing.Definition = r.LString();
                thing.DiesOn = r.Int32();
            }
            model.Things.Add(thing);
        }

        for (int i = 0, n = r.CountInt16(); i < n; i++)
        {
            TreeGroup group = new() { Y0 = r.Single(), X0 = r.Single(), Y1 = r.Single(), X1 = r.Single(), Count = r.Int32() };
            group.TreeType = r.LString();
            group.Seed = r.Int32();
            model.TreeGroups.Add(group);
        }

        for (int i = 0, n = r.Count(); i < n; i++)
        {
            TreeType type = new() { Name = r.LString() };
            for (int j = 0, m = r.Count(); j < m; j++) type.Positions.Add(new TreePosition(r.Single(), r.Single(), r.Int32()));
            model.TreeTypes.Add(type);
        }

        InfluenceMap influence = model.InfluenceMap;
        influence.Version = r.UInt16();
        if (influence.Version is not (0 or 1)) throw new InvalidDataException($"influence map version {influence.Version}");
        influence.Nodes = r.Count();
        influence.NodeBytes = r.Bytes(checked(influence.Nodes * InfluenceMap.NodeSize(influence.Version)));
        influence.Links = r.Count();
        influence.LinkBytes = r.Bytes(checked(influence.Links * InfluenceMap.LinkSize(influence.Version)));

        for (int i = 0, n = r.CountInt16(); i < n; i++)
        {
            WaypointPath path = new() { Name = r.LString() };
            for (int j = 0, m = r.Count(); j < m; j++) path.Slots.Add(r.Int16());
            model.WaypointPaths.Add(path);
        }

        WorldTimings timings = model.Timings;
        timings.OldF = r.Single();
        timings.OldG = r.Single();
        timings.OldH = r.Single();
        timings.PreRun = r.Single();
        timings.Pan = r.Single();
        timings.SGrade = r.Int32();
        timings.DGrade = r.Int32();
        timings.TimeLimit = r.Single();
        timings.FullScoreTime = r.Single();
        timings.PercentageScoreTime = r.Single();
        timings.ScorePercentage = r.Single();

        if (version is >= 45 and < 48)
            model.LegacyTimings = new LegacyTimings { A = r.Int32(), B = r.Int32(), C = r.Int32(), D = r.Single(), E = r.Single() };
        if (version >= 47)
        {
            model.OccupancyGrids = [];
            for (int i = 0; i < 3; i++)
            {
                OccupancyGrid grid = new() { Version = r.Int32() };
                grid.Data = r.Bytes(OccupancyGrid.DataSize(grid.Version));
                model.OccupancyGrids.Add(grid);
            }
            if (version < 50) model.LegacyGridWords = [r.Int32(), r.Int32(), r.Int32(), r.Int32(), r.Int32()];
        }
        if (version >= 49) model.LevelStartTime = r.Single();

        if (r.Position != r.Length) throw new InvalidDataException($"world body has {r.Length - r.Position} unread bytes");
        return model;
    }

    /// <summary>CMissionScriptObjectCode(file): instructions, event entry points, symbols, event functions, two words.</summary>
    private static void ReadCode(ByteReader r, ScriptCode code)
    {
        for (int i = 0, n = r.Count(); i < n; i++) code.Instructions.Add(new ScriptInstruction(r.Int32(), r.Int32()));
        for (int i = 0; i < ScriptCode.EventCount; i++) code.EventPcs[i] = r.Int32();
        for (int i = 0, n = r.Count(); i < n; i++)
        {
            ScriptSymbol symbol = new() { Name = r.LString(LengthKind.Int32), DataType = r.Int32() };
            if (symbol.DataType != 0) symbol.Value = ReadValue(r, symbol.DataType);
            symbol.SymbolType = r.Int32();
            symbol.Index = r.Int32();
            symbol.Flag = r.Int32();
            code.Symbols.Add(symbol);
        }
        code.NextSymbolIndex = r.Int32();
        for (int i = 0, n = r.Count(); i < n; i++)
        {
            EventFunction function = new() { EntryPc = r.Int32() };
            for (int j = 0, m = r.Count(); j < m; j++) function.Parameters.Add(r.Int32());
            code.EventFunctions.Add(function);
        }
        code.Tail1 = r.Int32();
        code.Tail2 = r.Int32();
    }

    /// <summary>A symbol's value by its data type; a bool keeps its stored word (any nonzero is true).</summary>
    private static ScriptValue ReadValue(ByteReader r, int dataType) => dataType switch
    {
        1 or 4 or 5 => new ScriptInt(r.Int32()),
        2 => new ScriptFloat(r.Single()),
        3 => new ScriptText(r.LString(LengthKind.Int32)),
        6 => new ScriptVector(new Vector3(r.Single(), r.Single(), r.Single())),
        _ => throw new InvalidDataException($"unknown script data type {dataType}"),
    };

    /// <summary>CInitThing::Load and the subclass fields, in the loader's order.</summary>
    private static ObjectInit ReadInit(ByteReader r, int version, ObjectClass objectClass)
    {
        ObjectInit init = new()
        {
            Position = new Vector3(r.Single(), r.Single(), r.Single()),
            Orientation = new Vector3(r.Single(), r.Single(), r.Single()),
            MeshNumber = r.Int32(),
            Allegiance = r.Int32(),
            Target = r.Int32(),
            Script = r.CString(),
            Name = r.CString(),
            SpawnScript = r.CString(),
            Active = r.Int32(),
        };
        if (version > 45) init.AttachScriptsToUnits = r.Int32();
        switch (objectClass)
        {
            case ObjectClass.Spawner:
                SpawnerInit spawner = new()
                {
                    Amount = r.Int32(), Delay = r.Single(), SquadDelay = r.Single(), InitialDelay = r.Single(),
                    SquadSize = r.Int32(), SpawnUnit = r.CString(),
                };
                if (version > 43) spawner.SpawnerSpawnScript = r.CString();
                init.Spawner = spawner;
                break;
            case ObjectClass.Squad:
                init.Squad = new SquadInit { Amount = r.Int32(), Mode = r.Int32() };
                break;
            case ObjectClass.Cutscene:
                init.Cutscene = new CutsceneInit { File = r.CString(), LinkTo = r.CString() };
                break;
            case ObjectClass.Start:
                init.Start = new StartInit { PlaneMode = r.Int32(), PlayerNumber = r.Int32() };
                break;
            case ObjectClass.Tree:
                init.Tree = new TreeInit { TreeType = r.CString() };
                break;
            case ObjectClass.SphereTrigger:
                init.SphereTrigger = new SphereTriggerInit { Radius = r.Single() };
                break;
        }
        return init;
    }
}
