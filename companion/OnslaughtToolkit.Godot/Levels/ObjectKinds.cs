// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>What a thing record holds after the fields every thing has.</summary>
public enum ObjectClass { Base, Spawner, Squad, Cutscene, Start, Tree, SphereTrigger }

/// <summary>
/// The object ids a world body's thing records carry and what each record holds after its common fields
/// (<c>CWorld::LoadWorld</c> reads each record through <c>SpawnInitThing</c>). The table mirrors the Toolkit's
/// <c>tools/world_resources_decode.py</c> and <c>thing_class</c> in <c>tools/world_resources_encode.py</c>, the reference
/// this code is checked against. An id <c>SpawnThing</c> does not make is refused: the game would not read its record,
/// so the bytes after it could not be framed.
/// </summary>
public static class ObjectKinds
{
    public const int Unit = 8, Building = 25, Squad = 28, Feature = 35, Hazard = 39;

    private static readonly Dictionary<int, string> Names = new()
    {
        [3] = "battle-engine", [7] = "tree", [8] = "unit", [10] = "radar", [11] = "named-mesh", [15] = "start",
        [16] = "rocket", [17] = "building-named-mesh", [18] = "waypoint", [19] = "spawner", [21] = "shell",
        [25] = "building", [26] = "cutscene", [27] = "level-script", [28] = "squad", [29] = "animal", [31] = "debris",
        [33] = "wall", [35] = "feature", [36] = "sphere-trigger", [37] = "safe-side", [38] = "wingman-start",
        [39] = "hazard", [41] = "spawn-point", [43] = "escape-pod",
    };

    /// <summary>The stored kind name of an object id, or <c>oid-N</c> for an id the table does not name.</summary>
    public static string NameOf(int objectId) => Names.TryGetValue(objectId, out string? name) ? name : $"oid-{objectId}";

    /// <summary>Whether the record names a definition and a "dies on" word after the common fields.</summary>
    public static bool IsDefined(int objectId) => objectId is Unit or Building or Squad or Feature or Hazard;

    /// <summary>The record's layout after the common fields; refuses an id the game would not read.</summary>
    public static ObjectClass ClassOf(int objectId) => objectId switch
    {
        Unit or Building or Feature or Hazard => ObjectClass.Base,
        Squad => ObjectClass.Squad,
        19 => ObjectClass.Spawner,
        26 => ObjectClass.Cutscene,
        15 or 41 => ObjectClass.Start,
        7 => ObjectClass.Tree,
        36 => ObjectClass.SphereTrigger,
        3 or 10 or 11 or 16 or 17 or 18 or 21 or 27 or 29 or 31 or 37 or 38 or 43 => ObjectClass.Base,
        _ => throw new InvalidDataException($"object id {objectId} is not one SpawnThing makes (LoadWorld would not read its record)"),
    };
}
