// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.TestSupport;

internal static class Level100TestActorDefinitions
{
    internal static Level100ActorDefinitionSet Create()
    {
        var actors = new List<Level100ActorDefinition>();

        void Add(
            string identity,
            string name,
            string? definition,
            string? script,
            string? mesh,
            Level100ActorPoseSnapshot pose,
            Level100MissionTargetGroup group = Level100MissionTargetGroup.None,
            int ordinal = 0,
            Level100MissionTrigger? trigger = null,
            int health = 0,
            bool active = true,
            bool isStatic = true,
            uint thingTypeMask = 0) => actors.Add(new Level100ActorDefinition(
                actors.Count,
                identity,
                name,
                definition,
                script,
                mesh,
                thingTypeMask,
                isStatic,
                active,
                health,
                AuthoredTransform(),
                pose,
                group,
                ordinal,
                trigger));

        Add("test:control-tower", "Control Tower", "Control Tower", "Facilities", "fb_control_tower", Pose(-13_290, -760, 5_603));
        Add("test:tank-factory", "Tank Factory", "Forseti Pulse Tank Factory", "TankFactory", "fb_tank_factory", Pose(10_125, 0, 22_375, 1_789_434));
        Add("test:health-pad", "Health Pad", "Forseti Repair Pad", "Facilities", "fb_health_pad", Pose(-58_438, 0, 10_500));
        Add("test:turret-03", "Turret 03", "SAT Turret", "Turret", "ft_sam", Pose(-36_188, 0, 18_000));
        Add("test:turret-01", "Turret 01", "Blaster Turret", "Turret", "ft_blaster", Pose(-49_188, 0, 23_250));
        Add("test:turret-02", "Turret 02", "Blaster Turret", "Turret", "ft_blaster", Pose(-17_313, 0, -3_250, 3_141_593));
        Add("test:turret-04", "Turret 04", "Pulse Turret", "Turret", "ft_pulse", Pose(-63_188, 0, 38_750));
        Add("test:research", "Forseti Research Building 1", "Forseti Research Building", "Facilities", "fb_research", Pose(-36_557, -760, -628, 2_470_636));
        Add("test:radar", "Radar Station", "Forseti Radar Station", "Facilities", "FB_radar_station", Pose(-102_563, 0, -23_500, -1_570_796));
        Add("test:airfield", "Airfield", "Forseti Light Fighter Airfield", "Hangar", "fb_aircraft_factory", Pose(47_188, 0, 15_125, 2_094_395));
        Add("test:hangar", "Hangar", "Hangar", null, "fb_hangar", Pose(26_636, 0, 41_727, -2_443_461));

        AddTrigger(Level100MissionTrigger.TargetZone1, "Target Zone 1", "TargetZone1");
        AddTrigger(Level100MissionTrigger.FiringRange, "Firing Range", "FiringRange");
        AddTrigger(Level100MissionTrigger.TargetZone2, "Target Zone 2", "TargetZone2");
        AddTrigger(Level100MissionTrigger.TargetZone3, "Target Zone 3", "TargetZone3");
        AddTrigger(Level100MissionTrigger.TargetZone4, "Target Zone 4", "TargetZone4");

        AddTarget(2, "Target Tank 2", "Target Tank", "StaticTarget", "m_f_pulsetank_training.msh.aya", SimulationConstants.Level100TargetTank2Position, -2_153_579, SimulationConstants.Level100TargetTankLife, true);
        AddTarget(3, "Target Tank 3", "Target Tank", "StaticTarget", "m_f_pulsetank_training.msh.aya", SimulationConstants.Level100TargetTank3Position, 2_404_331, SimulationConstants.Level100TargetTankLife, true);
        AddTarget(4, "Target Warehouse", "Warehouse", "StaticTarget", "m_m_warehouse.msh.aya", SimulationConstants.Level100TargetWarehousePosition, -1_970_861, SimulationConstants.Level100TargetWarehouseLife, true);
        Add("test:player", "Player 1", "Battle Engine", null, "m_f_be1.msh.aya", Pose(0, 0, 0), health: SimulationConstants.MaximumHull, isStatic: false, thingTypeMask: Level100ReleasedThingTypeMasks.BattleEngine);
        Add("test:transporter", "Transporter", "U-17 Highside Transporter", null, "m_f_lifter.msh.aya", Pose(0, 0, 0), isStatic: false);
        Add("test:air-trainer", "Air Trainer", "Air Trainer", null, "m_FA_F24_training.msh.aya", Pose(0, 0, 0), isStatic: false);

        var spawns = new List<Level100SpawnDefinition>();
        AddSpawn("test:tank-factory", "Target Tank", "SpawnerA", "TargetTank1", "m_f_pulsetank_training.msh.aya", Level100MissionTargetGroup.StaticTargets, 1, 4);
        AddSpawn("test:tank-factory", "Target Truck", "SpawnerA", "TargetTruck1", "m_f_truck_training.msh.aya", Level100MissionTargetGroup.TargetTrucks, 1, 3);
        AddSpawn("test:tank-factory", "Target Truck", "SpawnerA", "TargetTruck2", "m_f_truck_training.msh.aya", Level100MissionTargetGroup.TargetTrucks, 2, 3);
        AddSpawn("test:tank-factory", "Target Truck", "SpawnerA", "TargetTruck3", "m_f_truck_training.msh.aya", Level100MissionTargetGroup.TargetTrucks, 3, 3);
        AddSpawn("test:tank-factory", "Target Tank", "SpawnerA", "TargetTank2", "m_f_pulsetank_training.msh.aya", Level100MissionTargetGroup.MovingTargets, 0, 6);
        AddSpawn("test:tank-factory", "Target Truck", "SpawnerA", "TargetTank2", "m_f_truck_training.msh.aya", Level100MissionTargetGroup.MovingTargets, 0, 6);
        AddSpawn("test:airfield", "Air Trainer", "SpawnerB", "AirTrainer", "m_FA_F24_training.msh.aya", Level100MissionTargetGroup.AirTrainer, 1, 1);
        AddSpawn("test:airfield", "Target Drone", "SpawnerB", "AirborneDrone1", "m_FA_F24_training.msh.aya", Level100MissionTargetGroup.AirborneTargets1, 0, 3);
        AddSpawn("test:airfield", "Target Drone", "SpawnerA", "AirborneDrone2", "m_FA_F24_training.msh.aya", Level100MissionTargetGroup.AirborneTargets2, 0, 6);
        AddSpawn("test:airfield", "Target Drone", "SpawnerB", "AirborneDrone2", "m_FA_F24_training.msh.aya", Level100MissionTargetGroup.AirborneTargets2, 0, 6);
        return new Level100ActorDefinitionSet(
            actors,
            spawns,
            WaypointPaths(),
            MotionDefinitions());

        void AddTrigger(Level100MissionTrigger trigger, string name, string script)
        {
            SimVector2 position = Level100MissionTiming.TriggerPosition(trigger);
            Add(
                $"test:trigger:{trigger}",
                name,
                "General Volume",
                script,
                null,
                Pose(position.X, 0, position.Z),
                trigger: trigger,
                active: false);
        }

        void AddTarget(
            int ordinal,
            string name,
            string definition,
            string script,
            string mesh,
            SimVector2 position,
            int yaw,
            int health,
            bool isStatic) => Add(
                $"test:target-{ordinal}",
                name,
                definition,
                script,
                mesh,
                Pose(position.X, 0, position.Z, yaw),
                Level100MissionTargetGroup.StaticTargets,
                ordinal,
                health: health,
                isStatic: isStatic);

        void AddSpawn(
            string ownerIdentity,
            string definition,
            string spawner,
            string script,
            string? mesh,
            Level100MissionTargetGroup group,
            int fixedOrdinal,
            int maximum) => spawns.Add(new Level100SpawnDefinition(
                spawns.Count,
                $"test:spawn:{ownerIdentity}:{definition}:{spawner}:{script}",
                ownerIdentity,
                definition,
                spawner,
                script,
                mesh,
                0,
                true,
                definition switch
                {
                    "Target Tank" => SimulationConstants.Level100TargetTankLife,
                    "Target Truck" => SimulationConstants.Level100TrainingTruckLife,
                    _ => 0,
                },
                ownerIdentity == "test:tank-factory"
                    ? TankFactorySpawnerPose()
                    : Pose(46_216, -6_133, 14_450),
                ownerIdentity == "test:tank-factory"
                    ? new Level100SpawnerTransform(
                        new Level100FloatVector3Bits(
                            1_042_393_533,
                            1_088_031_702,
                            -1_107_199_288),
                        IdentityBasis())
                    : new Level100SpawnerTransform(
                        new Level100FloatVector3Bits(
                            -1_110_748_774,
                            1_066_854_716,
                            -1_060_880_958),
                        IdentityBasis()),
                group,
                fixedOrdinal,
                maximum));
    }

    private static Level100ActorPoseSnapshot Pose(int x, int y, int z, int yaw = 0) => new(
        new SimVector3(x, y, z),
        IdentityBasis(),
        SimVector3.Zero,
        SimVector3.Zero);

    private static Level100AuthoredTransform AuthoredTransform() => new(
        new Level100FloatVector3Bits(0, 0, 0),
        new Level100FloatVector3Bits(0, 0, 0),
        IdentityBasis());

    private static Level100ActorPoseSnapshot TankFactorySpawnerPose() => new(
        new SimVector3(3_439, -126, 21_051),
        new Level100FloatBasis3Bits(
            -1_101_128_975, 0, -1_082_529_832,
            0, 1_065_353_216, 0,
            1_064_953_816, 0, -1_101_128_975),
        SimVector3.Zero,
        SimVector3.Zero);

    private static Level100FloatBasis3Bits IdentityBasis() => new(
        FloatBits(1f), 0, 0,
        0, FloatBits(1f), 0,
        0, 0, FloatBits(1f));

    private static int FloatBits(float value) => BitConverter.SingleToInt32Bits(value);

    // Every route below is the released one, transcribed point for point from
    // the materialized manifest `level100-static-world.json` (`waypointPaths`),
    // which the Client tests load directly.
    //
    // They used to be synthetic single points 500-620 m out at exactly 45
    // degrees, with a comment claiming that kept Core-only tests independent of
    // retail route data. It did not: it made whole released beats unreachable
    // in Core, because every actor that follows one of these paths drives off
    // the authored map and parks in deep water where no walker can follow it.
    // Measured before this correction, with beat 3 completing for the first
    // time: the three beat-4 Target Trucks stopped at (197322, -11060, 213103),
    // (187162, -11060, 203960) and (176998, -11060, 194815) - 170-197 m from
    // the player and 11 m below the water plane. Beat 4 could not complete, and
    // beats 5, 6, 8 and 10 are behind it. This is the same class of fixture
    // defect that `Target Tank Path 1` carried until it was corrected on
    // 2026-07-26, and nothing pins the synthetic values.
    //
    // `Transporter Path` keeps its released duplicate leading node, which is
    // what `TransporterArrival_UsesStrictClassRadiusAndRetainsDuplicateNodes`
    // asserts: the retail route repeats (-95688, -42250).
    //
    // Every field is the manifest's, including the retail `nodeIndex` and the
    // retail `retailComponentsFloatBits`. The previous corrections renumbered
    // nodes 0..N-1 and rebuilt the float bits from the rounded millimetres,
    // which produces *different bits* - harmless today because nothing in the
    // movement path reads either field, and wrong tomorrow because both are
    // part of the hashed definition set.
    private static IReadOnlyList<Level100WaypointPathDefinition> WaypointPaths() =>
    [
        ExactPath("Flyby Path",
            (43, -13_188, 10_000, 12_250, 1_133_101_056, 1_132_429_312, 1_092_616_192, 0),
            (42, 33_813, 10_000, 21_250, 1_134_641_152, 1_132_740_608, 1_092_616_192, 0),
            (41, -688, 10_000, 48_750, 1_133_510_656, 1_133_641_728, 1_092_616_192, 0)),
        ExactPath("Target Truck Path 3",
            (36, -66_688, 10_000, 16_750, 1_130_233_856, 1_132_593_152, 1_092_616_192, 0),
            (35, -108_688, 10_000, 37_750, 1_127_481_344, 1_133_281_280, 1_092_616_192, 0),
            (34, -99_688, 10_000, -3_250, 1_128_071_168, 1_131_413_504, 1_092_616_192, 0),
            (33, -95_688, 10_000, -42_250, 1_128_333_312, 1_128_857_600, 1_092_616_192, 0)),
        ExactPath("Target Truck Path 2",
            (32, -13_188, 10_000, 12_250, 1_133_101_056, 1_132_429_312, 1_092_616_192, 0),
            (31, 33_813, 10_000, 21_250, 1_134_641_152, 1_132_740_608, 1_092_616_192, 0),
            (30, -688, 10_000, 48_750, 1_133_510_656, 1_133_641_728, 1_092_616_192, 0),
            (29, 33_313, 10_000, 69_750, 1_134_624_768, 1_134_329_856, 1_092_616_192, 0)),
        ExactPath("Target Truck Path 1",
            (25, -66_688, 10_000, 16_750, 1_130_233_856, 1_132_593_152, 1_092_616_192, 0),
            (26, -77_688, 10_000, 84_750, 1_129_512_960, 1_134_821_376, 1_092_616_192, 0),
            (27, -43_688, 10_000, 57_750, 1_131_741_184, 1_133_936_640, 1_092_616_192, 0),
            (28, -11_688, 10_000, 91_750, 1_133_150_208, 1_135_050_752, 1_092_616_192, 0)),
        ExactPath("Transporter Path",
            (44, -95_688, 10_000, -42_250, 1_128_333_312, 1_128_857_600, 1_092_616_192, 0),
            (22, -95_688, 10_000, -42_250, 1_128_333_312, 1_128_857_600, 1_092_616_192, 0),
            (23, -99_688, 10_000, -3_250, 1_128_071_168, 1_131_413_504, 1_092_616_192, 0)),
        ExactPath("Target Tank Path 2",
            (38, -43_688, 10_000, 57_750, 1_131_741_184, 1_133_936_640, 1_092_616_192, 0),
            (37, -77_688, 10_000, 84_750, 1_129_512_960, 1_134_821_376, 1_092_616_192, 0),
            (8, -688, 10_000, 48_750, 1_133_510_656, 1_133_641_728, 1_092_616_192, 0),
            (10, -13_188, 10_000, 12_250, 1_133_101_056, 1_132_429_312, 1_092_616_192, 0),
            (24, -108_688, 10_000, 37_750, 1_127_481_344, 1_133_281_280, 1_092_616_192, 0)),
        // `Target Tank Path 1` was the synthetic triple (610000, 610000)..
        // (612000, 612000) - 610 m away at exactly 45 degrees - so
        // `Target Tank #23`, the fourth beat-3 static target, drove away from
        // the firing range forever and beat 3 could never complete. That is the
        // G2 gap recorded in LEVEL100-TUTORIAL-BEATS-2026-07-26.md.
        ExactPath("Target Tank Path 1",
            (18, 33_313, 10_000, 69_750, 1_134_624_768, 1_134_329_856, 1_092_616_192, 0),
            (6, -11_688, 10_000, 91_750, 1_133_150_208, 1_135_050_752, 1_092_616_192, 0),
            (7, 33_313, 10_000, 69_750, 1_134_624_768, 1_134_329_856, 1_092_616_192, 0)),
        ExactPath("Drone Path 1",
            (1, -99_688, 10_000, -3_250, 1_128_071_168, 1_131_413_504, 1_092_616_192, 0),
            (2, -108_688, 10_000, 37_750, 1_127_481_344, 1_133_281_280, 1_092_616_192, 0),
            (3, -66_688, 10_000, 16_750, 1_130_233_856, 1_132_593_152, 1_092_616_192, 0),
            (4, -77_688, 10_000, 84_750, 1_129_512_960, 1_134_821_376, 1_092_616_192, 0)),
    ];

    private static IReadOnlyList<Level100ActorMotionDefinition>
        MotionDefinitions() =>
    [
        GroundMotion(0, "Target Tank"),
        GroundMotion(1, "Target Truck"),
        new Level100ActorMotionDefinition(
            2,
            "Air Trainer",
            Level100ActorMotionClass.Plane,
            9,
            8,
            0x005E1930,
            5_000,
            null,
            null,
            null,
            null),
        new Level100ActorMotionDefinition(
            3,
            "Target Drone",
            Level100ActorMotionClass.Plane,
            9,
            8,
            0x005E1930,
            5_000,
            null,
            null,
            null,
            null),
        new Level100ActorMotionDefinition(
            4,
            "U-17 Highside Transporter",
            Level100ActorMotionClass.Dropship,
            12,
            12,
            0x005E1DD8,
            8_000,
            null,
            null,
            null,
            null),
    ];

    private static Level100ActorMotionDefinition GroundMotion(
        int authoredOrder,
        string definitionName) => new(
            authoredOrder,
            definitionName,
            Level100ActorMotionClass.GroundVehicle,
            3,
            2,
            0x005E297C,
            2_000,
            0x40600000,
            0x3D567750,
            4,
            100);

    /// <summary>
    /// One released waypoint path, every field taken verbatim from the
    /// materialized manifest: node index, millimetre position, and the retail
    /// float components. Nothing here is reconstructed or renumbered.
    /// </summary>
    private static Level100WaypointPathDefinition ExactPath(
        string name,
        params (int Node, int X, int Y, int Z, int B0, int B1, int B2, int B3)[] points) => new(
        name,
        Array.AsReadOnly(points
            .Select(point => new Level100WaypointPointDefinition(
                point.Node,
                new SimVector3(point.X, point.Y, point.Z),
                new Level100FloatVector4Bits(point.B0, point.B1, point.B2, point.B3)))
            .ToArray()));
}
