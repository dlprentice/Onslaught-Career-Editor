// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>Whether a thing is a <c>CUnit</c> and whether it is a building.</summary>
public readonly record struct Level100ThingClass(bool IsUnit, bool IsBuilding);

/// <summary>
/// The native class of every Level 100 thing a crosshair or lock query can
/// meet, by definition name. The registry admits only the Ammunition and
/// Battle Engine type bits, so the unit and building bits the crosshair
/// tests (<c>BattleEngine.cpp:2325-2327</c>) come from each thing's class.
/// </summary>
/// <remarks>
/// Evidence: the RE lane's class table in
/// <c>reverse-engineering/game-mechanics/level100-final-drone-wave.md</c>
/// ("AI owners that draw shared RNG"): base-world rows 0-2, 13-20 and 23-29
/// are <c>CBuilding</c>, the four turrets are <c>CCannon</c>, the icebergs are
/// features, and the level-world Target Tank/Truck are <c>CGroundVehicle</c>,
/// the Warehouse a <c>CBuilding</c>, and Air Trainer and Target Drone
/// <c>CPlane</c>. The city buildings (rows 30-34) are <c>CSimpleBuilding</c>,
/// whose slot 66 uses the Unit small-explosion path
/// (<c>reverse-engineering/binary-analysis/cexplosion-factory-callers-2026-08-10.md</c>);
/// that it is a unit and a building is recorded as an open question in
/// <c>rebuild/PARITY.md</c>, not a measured fact.
/// </remarks>
public static class Level100ThingClasses
{
    private static readonly Level100ThingClass s_building = new(IsUnit: true, IsBuilding: true);
    private static readonly Level100ThingClass s_unit = new(IsUnit: true, IsBuilding: false);
    private static readonly Level100ThingClass s_feature = new(IsUnit: false, IsBuilding: false);

    public static Level100ThingClass Of(string? definitionName) => definitionName switch
    {
        "Control Tower" or "Forseti Pulse Tank Factory" or "Forseti Repair Pad" or
            "Forseti Research Building" or "Forseti Building 1" or "Forseti Building 2" or
            "Forseti Building 3" or "Forseti Solar Pod" or "Forseti Radar Station" or
            "Forseti Light Fighter Airfield" or "Forseti Docks" or "Hangar" or
            "Forseti Tall Building 1" or "Forseti Tall Building 3" or "Warehouse" => s_building,
        "Forseti City Building 1" or "Forseti City Building 2" or
            "Forseti City Building 3" => s_building,
        "SAT Turret" or "Blaster Turret" or "Pulse Turret" or "Target Tank" or
            "Target Truck" or "Target Drone" or "Air Trainer" => s_unit,
        "Iceberg 1" or "Iceberg 2" or "Iceberg 3" or "Iceberg 4" => s_feature,
        _ => throw new NotSupportedException(
            $"Level 100 thing class is unadmitted for definition '{definitionName}'."),
    };
}
