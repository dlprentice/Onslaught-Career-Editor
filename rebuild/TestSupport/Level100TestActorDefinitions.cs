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
        AddTarget(4, "Target Warehouse", "Warehouse", "StaticTarget", "m_m_warehouse.msh.aya", SimulationConstants.Level100TargetWarehousePosition, -1_970_861, SimulationConstants.Level100TargetWarehouseCenterAimDamageEnvelope, true);
        Add("test:player", "Player 1", "Battle Engine", null, "m_f_be1.msh.aya", Pose(0, 0, 0), health: SimulationConstants.MaximumHull, isStatic: false, thingTypeMask: Level100ReleasedThingTypeMasks.BattleEngine);
        Add("test:transporter", "Transporter", "Transporter", null, "m_f_lifter.msh.aya", Pose(0, 0, 0), isStatic: false);
        Add("test:air-trainer", "Air Trainer", "Air Trainer", null, "m_FA_F24_training.msh.aya", Pose(0, 0, 0), isStatic: false);

        var spawns = new List<Level100SpawnDefinition>();
        AddSpawn("test:tank-factory", "Target Tank", "SpawnerA", "TargetTank1", "m_f_pulsetank_training.msh.aya", Level100MissionTargetGroup.StaticTargets, 1, 4);
        AddSpawn("test:tank-factory", "Target Truck", "SpawnerA", "TargetTruck1", null, Level100MissionTargetGroup.TargetTrucks, 1, 3);
        AddSpawn("test:tank-factory", "Target Truck", "SpawnerA", "TargetTruck2", null, Level100MissionTargetGroup.TargetTrucks, 2, 3);
        AddSpawn("test:tank-factory", "Target Truck", "SpawnerA", "TargetTruck3", null, Level100MissionTargetGroup.TargetTrucks, 3, 3);
        AddSpawn("test:tank-factory", "Target Tank", "SpawnerA", "TargetTank2", "m_f_pulsetank_training.msh.aya", Level100MissionTargetGroup.MovingTargets, 0, 6);
        AddSpawn("test:tank-factory", "Target Truck", "SpawnerA", "TargetTank2", null, Level100MissionTargetGroup.MovingTargets, 0, 6);
        AddSpawn("test:airfield", "Air Trainer", "SpawnerB", "AirTrainer", null, Level100MissionTargetGroup.AirTrainer, 1, 1);
        AddSpawn("test:airfield", "Target Drone", "SpawnerB", "AirborneDrone1", null, Level100MissionTargetGroup.AirborneTargets1, 0, 3);
        AddSpawn("test:airfield", "Target Drone", "SpawnerA", "AirborneDrone2", null, Level100MissionTargetGroup.AirborneTargets2, 0, 6);
        AddSpawn("test:airfield", "Target Drone", "SpawnerB", "AirborneDrone2", null, Level100MissionTargetGroup.AirborneTargets2, 0, 6);
        return new Level100ActorDefinitionSet(actors, spawns);

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
                definition == "Target Tank" ? SimulationConstants.Level100TargetTankLife : 0,
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
}
