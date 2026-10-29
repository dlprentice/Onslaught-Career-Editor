// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// One world body: what <c>CWorld::LoadWorld</c> reads from a level archive's BSWD or RLWD chunk, or from a loose
/// <c>data\worlds\worldNNN.wrd</c> file. Every field the loader reads is a property here, in the loader's order, so a
/// body read and written again is byte for byte the same; the regions the loader only skips or copies (the influence
/// map's nodes and links, the occupancy grids, each script's ten trailing bytes) stay as bytes.
/// <para>
/// The Toolkit's <c>tools/world_resources_encode.py</c> (<c>read_world_model</c> and <c>write_world_body</c>) is the
/// reference: this code reads and refuses what that code does, and the tests compare the two on vectors it generates.
/// Properties that exist only in some versions are null in the others.
/// </para>
/// <para>
/// Order matters: waypoint paths name things by their place in the thing list, so a thing added to an edited body goes
/// after the existing ones.
/// </para>
/// </summary>
public sealed class WorldBody
{
    public const int MinVersion = 43, MaxVersion = 50;

    /// <summary>LoadWorld's thing array holds this many records; a body with more is read but not written.</summary>
    public const int MaxThings = 1000;

    public int Version { get; set; }
    public WorldHeader Header { get; set; } = new();
    public int BaseLevel { get; set; }
    public List<MissionScript> Scripts { get; } = [];
    public int MapNumber { get; set; }
    public List<string> NamedMeshes { get; } = [];
    public List<PlacedObject> Things { get; } = [];
    public List<TreeGroup> TreeGroups { get; } = [];
    public List<TreeType> TreeTypes { get; } = [];
    public InfluenceMap InfluenceMap { get; set; } = new();
    public List<WaypointPath> WaypointPaths { get; } = [];
    public WorldTimings Timings { get; set; } = new();

    /// <summary>Versions 45 to 47 only.</summary>
    public LegacyTimings? LegacyTimings { get; set; }

    /// <summary>Versions 47 and later: exactly three grids.</summary>
    public List<OccupancyGrid>? OccupancyGrids { get; set; }

    /// <summary>Versions 47 to 49 only: five words.</summary>
    public int[]? LegacyGridWords { get; set; }

    /// <summary>Version 49 and later.</summary>
    public float? LevelStartTime { get; set; }

    /// <summary>Reads a body, refusing what <c>CWorld::LoadWorld</c> would not accept (and any unread byte).</summary>
    /// <exception cref="InvalidDataException">The bytes are not a world body.</exception>
    public static WorldBody Read(ReadOnlySpan<byte> body) => WorldBodyReader.Read(body);

    /// <summary>The bytes <c>CWorld::LoadWorld</c> reads for this body.</summary>
    /// <exception cref="InvalidDataException">The body holds something the format cannot store.</exception>
    public byte[] Write() => WorldBodyWriter.Write(this);
}

public sealed class WorldHeader
{
    public int HeaderVersion { get; set; }
    public int Unused1 { get; set; }
    public int Unused2 { get; set; }
    public List<string> BattleEngineConfigurations { get; } = [];

    /// <summary>Header version 2 and later: three words.</summary>
    public int[]? V2Words { get; set; }

    /// <summary>Header version 3 and later.</summary>
    public int WorldType { get; set; }
}

/// <summary>A compiled mission script: its name, its code and ten bytes the loader reads and drops.</summary>
public sealed class MissionScript
{
    public string Name { get; set; } = "";
    public ScriptCode Code { get; set; } = new();
    public byte[] Trailer { get; set; } = new byte[10];
}

public readonly record struct ScriptInstruction(int Opcode, int Attribute);

public sealed class ScriptCode
{
    public const int EventCount = 13;

    public List<ScriptInstruction> Instructions { get; } = [];
    public int[] EventPcs { get; set; } = new int[EventCount];
    public List<ScriptSymbol> Symbols { get; } = [];
    public int NextSymbolIndex { get; set; }
    public List<EventFunction> EventFunctions { get; } = [];
    public int Tail1 { get; set; }
    public int Tail2 { get; set; }
}

public sealed class ScriptSymbol
{
    public string Name { get; set; } = "";

    /// <summary>0 holds no value; 1, 4 and 5 an integer (a bool keeps its stored word); 2 a float; 3 a string; 6 a position.</summary>
    public int DataType { get; set; }

    public ScriptValue? Value { get; set; }
    public int SymbolType { get; set; }
    public int Index { get; set; }
    public int Flag { get; set; }
}

public abstract record ScriptValue;

public sealed record ScriptInt(int Value) : ScriptValue;

public sealed record ScriptFloat(float Value) : ScriptValue;

public sealed record ScriptText(string Value) : ScriptValue;

public sealed record ScriptVector(Vector3 Value) : ScriptValue;

public sealed class EventFunction
{
    public int EntryPc { get; set; }
    public List<int> Parameters { get; } = [];
}

/// <summary>
/// One stored thing record. The ordinal is its place in this body's list, not a runtime slot: whether a record takes a
/// slot depends on the game's definitions.
/// </summary>
public sealed class PlacedObject
{
    public int ObjectId { get; set; }

    /// <summary>The kind name the loader's object-id table gives (<c>unit</c>, <c>waypoint</c>, ...).</summary>
    public string Kind => ObjectKinds.NameOf(ObjectId);

    /// <summary>What a player would call it: the record's own name, else the definition it names (a Target Tank), else its kind.</summary>
    public string Label => Init.Name.Length > 0 ? Init.Name : Definition is { Length: > 0 } definition ? definition : Kind;

    public ObjectInit Init { get; set; } = new();

    /// <summary>Units, buildings, squads, features and hazards name a definition; other kinds have none.</summary>
    public string? Definition { get; set; }

    /// <summary>The word after the definition (defined kinds only).</summary>
    public int DiesOn { get; set; }
}

/// <summary>The fields every thing record has, then the one extra block its kind adds.</summary>
public sealed class ObjectInit
{
    public Vector3 Position { get; set; }
    public Vector3 Orientation { get; set; }
    public int MeshNumber { get; set; }
    public int Allegiance { get; set; }
    public int Target { get; set; }
    public string Script { get; set; } = "";
    public string Name { get; set; } = "";
    public string SpawnScript { get; set; } = "";
    public int Active { get; set; }

    /// <summary>Versions 46 and later.</summary>
    public int? AttachScriptsToUnits { get; set; }

    public SpawnerInit? Spawner { get; set; }
    public SquadInit? Squad { get; set; }
    public CutsceneInit? Cutscene { get; set; }
    public StartInit? Start { get; set; }
    public TreeInit? Tree { get; set; }
    public SphereTriggerInit? SphereTrigger { get; set; }
}

public sealed class SpawnerInit
{
    public int Amount { get; set; }
    public float Delay { get; set; }
    public float SquadDelay { get; set; }
    public float InitialDelay { get; set; }
    public int SquadSize { get; set; }
    public string SpawnUnit { get; set; } = "";

    /// <summary>Versions 44 and later.</summary>
    public string? SpawnerSpawnScript { get; set; }
}

public sealed class SquadInit
{
    public int Amount { get; set; }
    public int Mode { get; set; }
}

public sealed class CutsceneInit
{
    public string File { get; set; } = "";
    public string LinkTo { get; set; } = "";
}

public sealed class StartInit
{
    public int PlaneMode { get; set; }
    public int PlayerNumber { get; set; }
}

public sealed class TreeInit
{
    public string TreeType { get; set; } = "";
}

public sealed class SphereTriggerInit
{
    public float Radius { get; set; }
}

public sealed class TreeGroup
{
    public float Y0 { get; set; }
    public float X0 { get; set; }
    public float Y1 { get; set; }
    public float X1 { get; set; }
    public int Count { get; set; }
    public string TreeType { get; set; } = "";
    public int Seed { get; set; }
}

public readonly record struct TreePosition(float X, float Y, int Kind);

public sealed class TreeType
{
    public string Name { get; set; } = "";
    public List<TreePosition> Positions { get; } = [];
}

/// <summary>The influence map the loader skips: a version (0 or 1) and its node and link records as bytes.</summary>
public sealed class InfluenceMap
{
    public int Version { get; set; }
    public int Nodes { get; set; }
    public byte[] NodeBytes { get; set; } = [];
    public int Links { get; set; }
    public byte[] LinkBytes { get; set; } = [];

    /// <summary>Bytes per node and per link record for a map version.</summary>
    public static int NodeSize(int version) => version == 0 ? 12 : 16;

    public static int LinkSize(int version) => version == 0 ? 8 : 12;
}

/// <summary>A named list of thing slots (positions in the loader's thing array) a unit can follow.</summary>
public sealed class WaypointPath
{
    public string Name { get; set; } = "";
    public List<short> Slots { get; } = [];
}

public sealed class WorldTimings
{
    public float OldF { get; set; }
    public float OldG { get; set; }
    public float OldH { get; set; }
    public float PreRun { get; set; }
    public float Pan { get; set; }
    public int SGrade { get; set; }
    public int DGrade { get; set; }
    public float TimeLimit { get; set; }
    public float FullScoreTime { get; set; }
    public float PercentageScoreTime { get; set; }
    public float ScorePercentage { get; set; }
}

/// <summary>Three words and two floats that versions 45 to 47 carry after the timings.</summary>
public sealed class LegacyTimings
{
    public int A { get; set; }
    public int B { get; set; }
    public int C { get; set; }
    public float D { get; set; }
    public float E { get; set; }
}

/// <summary>An occupancy grid the loader skips: version 1 holds 0x8000 bytes, version 2 holds 0x2000, any other none.</summary>
public sealed class OccupancyGrid
{
    public int Version { get; set; }
    public byte[] Data { get; set; } = [];

    public static int DataSize(int version) => version switch { 1 => 0x8000, 2 => 0x2000, _ => 0 };
}
