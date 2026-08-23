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

    public static int SumOfTypedRows =>
        Type8UnitCount + Type15Count + Type18WaypointCount + Type19SpawnerCount +
        Type27ScriptCount + Type28UnitCount + Type36VolumeCount;
}
