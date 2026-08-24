// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// Measured census of world 110's level-world (RLWD) initial actors and its
/// shared base world. Not a session owner.
/// </summary>
/// <remarks>
/// <para>
/// Measured 2026-08-22 from <c>data/resources/110_res_PC.aya</c> (archive
/// SHA-256 <c>4e041c75…3c2b</c>). After the 13 admitted script objects the
/// RLWD actor header is <c>(2, 0, 40)</c> — Level 100's is <c>(1, 0, 45)</c>.
/// All 40 common InitThing records parse; trailers that Level 100 does not
/// use are type 19 (<c>int32 + 3 floats + int32 + two c-strings</c>, first
/// row <c>Fighter Second Wave</c> / <c>Muspell Fighter</c>) and type 28
/// (<c>int32 + int32 + string8 + int32</c>, first row <c>Light Gun Tank</c>
/// with trailer -1). The walk ends on the same tree-group header Level 100
/// uses (<c>uint16 0 / int32 2 / fernsnow</c>).
/// </para>
/// <para>
/// The BSWD chunk is byte-identical to Level 100's BSWD (54669 B, SHA-256
/// <c>04c5a383…10f4</c>): same <c>Paladin Prototype</c> header
/// <c>(50, 3, 42, 1)</c> and the same 35 base records. World 110 is a
/// different RLWD overlay on the same island, not a second island.
/// </para>
/// <para>
/// <b>What this deliberately does not claim.</b> No RLWD row is a Battle
/// Engine. Ordinal 0 is the LevelScript object (type 27), not the L100
/// ordinal-0 <c>Player 1</c> mapping. Retail's player for this world is not
/// authored in the level-world table; inventing a spawn from the L100 start
/// pad or from the type-15 row at (264.75, 258.81) is not licensed here.
/// </para>
/// </remarks>
public static class RetailWorld110LevelActors
{
    public const int WorldNumber = 110;

    public const string SourceArchiveRelativePath =
        "data/resources/110_res_PC.aya";

    public const string SourceArchiveSha256 =
        "4e041c758b9d41ba18311b1fadeacb95fc31af51320861480b97033bc24e3c2b";

    public const int InitialActorCount = 40;

    public const int ActorHeaderA = 2;

    public const int ActorHeaderB = 0;

    /// <summary>SHA-256 of the BSWD chunk shared with Level 100.</summary>
    public const string SharedBaseWorldSha256 =
        "04C5A3838548A2C50819F46DC1F1746F7C20EC4AA34678BD23C8BCD2186010F4";

    public const int SharedBaseWorldBytes = 54_669;

    public const int Type8UnitCount = 10;

    public const int Type15Count = 1;

    public const int Type18WaypointCount = 19;

    public const int Type19SpawnerCount = 1;

    public const int Type27ScriptCount = 3;

    public const int Type28UnitCount = 5;

    public const int Type36VolumeCount = 1;

    /// <summary>
    /// Exact archive identity already used by the world-110 script, heightfield,
    /// and actor-census admissions.
    /// </summary>
    public static RetailWorldArchiveIdentity ArchiveIdentity { get; } =
        new(SourceArchiveRelativePath, SourceArchiveSha256);

    /// <summary>
    /// The complete definition-bearing projection from the byte-identical BSWD
    /// loaded first and world 110's own RLWD loaded second. Identities reuse the
    /// existing Level 100 <c>wres:bswd:NNNN</c> / <c>wres:rlwd:NNNN</c> law.
    /// Type 19 is the one authored spawner definition; types 8, 28, and 35 are
    /// actor definitions. The type-15 start is deliberately absent because its
    /// row carries no Battle Engine definition identity.
    /// </summary>
    public static IReadOnlyList<RetailWorldAuthoredDefinitionIdentity>
        AuthoredDefinitions { get; } =
        Array.AsReadOnly<RetailWorldAuthoredDefinitionIdentity>(
        [
        new("wres:bswd:0000", 8, "Control Tower", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0001", 8, "Forseti Pulse Tank Factory", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0002", 8, "Forseti Repair Pad", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0003", 8, "SAT Turret", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0004", 35, "Iceberg 1", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0005", 35, "Iceberg 2", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0006", 35, "Iceberg 3", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0007", 35, "Iceberg 4", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0008", 35, "Iceberg 2", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0009", 35, "Iceberg 4", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0010", 8, "Blaster Turret", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0011", 8, "Blaster Turret", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0012", 8, "Pulse Turret", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0013", 8, "Forseti Research Building", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0014", 8, "Forseti Building 1", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0015", 8, "Forseti Building 2", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0016", 8, "Forseti Building 2", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0017", 8, "Forseti Solar Pod", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0018", 8, "Forseti Building 3", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0019", 8, "Forseti Building 3", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0020", 8, "Forseti Radar Station", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0023", 8, "Forseti Light Fighter Airfield", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0024", 8, "Forseti Docks", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0025", 8, "Hangar", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0026", 8, "Forseti Tall Building 1", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0027", 8, "Forseti Tall Building 3", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0028", 8, "Forseti Tall Building 1", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0029", 8, "Forseti Tall Building 3", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0030", 8, "Forseti City Building 1", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0031", 8, "Forseti City Building 2", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0032", 8, "Forseti City Building 3", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0033", 8, "Forseti City Building 2", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:bswd:0034", 8, "Forseti City Building 2", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0005", 19, "Muspell Fighter", RetailWorldAuthoredDefinitionKind.Spawner),
        new("wres:rlwd:0008", 8, "Muspell Light Landing Craft", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0012", 8, "Muspell Light Landing Craft", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0013", 8, "Muspell Light Landing Empty", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0014", 28, "Light Gun Tank", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0016", 28, "Light Gun Tank", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0017", 28, "AV-14B Sabre Pulse Tank", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0018", 28, "Light Gun Tank", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0019", 28, "AV-14B Sabre Pulse Tank", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0020", 8, "Muspell Light Landing Craft", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0025", 8, "Muspell Fighter", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0034", 8, "Muspell Light Fighter", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0035", 8, "Muspell Light Fighter", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0036", 8, "Muspell Light Fighter", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0037", 8, "Muspell Light Fighter", RetailWorldAuthoredDefinitionKind.Actor),
        new("wres:rlwd:0038", 8, "Muspell Light Fighter", RetailWorldAuthoredDefinitionKind.Actor),
        ]);

    public static int SumOfTypedRows =>
        Type8UnitCount + Type15Count + Type18WaypointCount + Type19SpawnerCount +
        Type27ScriptCount + Type28UnitCount + Type36VolumeCount;
}
