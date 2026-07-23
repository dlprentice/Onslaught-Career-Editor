// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public sealed class Simulation
{
    private sealed class MutableProjectile
    {
        // Rounds are deterministic ammunition state, not script actors. They
        // enter the actor runtime only as the released external Ammunition
        // type mask carried by a hit fact.
        public required int Id { get; init; }
        public SimVector2 Position { get; set; }
        public required SimVector2 Velocity { get; init; }
        public int ElevationMillimeters { get; set; }
        public required int VerticalVelocityMillimetersPerTick { get; init; }
        public int RemainingTicks { get; set; }
    }

    private sealed class MutableWalkerFoot
    {
        public required int Id { get; init; }
        public required SimVector2 StanceOffset { get; init; }
        public SimVector2 Position { get; set; }
        public int GroundElevationMillimeters { get; set; }
        public int PhaseThirds { get; set; }
        public int LiftMillimeters { get; set; }
    }

    private readonly uint _seed;
    private readonly List<MutableProjectile> _projectiles = [];
    private readonly List<MutableWalkerFoot> _walkerFeet = [];
    private readonly List<Level100MissionEvent> _level100MissionEvents = [];
    private readonly List<Level100ActorScriptCommand> _level100ActorScriptCommands = [];
    private readonly Level100TutorialProgress _level100TutorialProgress;
    private readonly Level100ActorDefinitionSet _level100ActorDefinitions;
    private Level100Mission _level100Mission = null!;
    private Level100ActorRegistry _level100Actors = null!;
    private Level100ActorScriptRuntime _level100ActorScripts = null!;
    private Level100DestructionRuntime _level100Destruction = null!;
    private Level100ActorId _level100PlayerActorId;
    private int _tick;
    private int _nextProjectileId;
    private VehicleMode _mode;
    private VehicleTransition _transition;
    private sbyte _facingX;
    private sbyte _facingZ;
    // Continuous body yaw (0 = +Z) and its retail-observed inertial step.
    private int _facingYawMicroRad;
    private int _walkerYawVelocityMicroRadPerTick;
    private int _facingPitchMicroRad;
    private int _walkerPitchVelocityMicroRadPerTick;
    private int _energy;
    private int _shield;
    private int _transformTicksRemaining;
    private int _fireCooldownTicksRemaining;
    private int _level100OpeningTicksRemaining;
    private bool _level100FlightEnabled;
    private bool _level100PulseCannonEnabled;
    private bool _level100VulcanCannonEnabled;
    private bool _level100MechVulcanCannonEnabled;
    private bool _level100MissilePodEnabled;
    private int _level100HudEmphasisMask;

    // Jet handling remains provisional and outside this walker milestone.
    private const int ProvisionalJetLookYawRateMicroRadPerTick = 3_000;

    public Simulation(
        uint seed,
        Level100ActorDefinitionSet level100ActorDefinitions,
        Level100TutorialProgress tutorialProgress = default)
    {
        if (seed == 0)
        {
            throw new ArgumentOutOfRangeException(nameof(seed), "Seed must be nonzero.");
        }

        _seed = seed;
        _level100ActorDefinitions = level100ActorDefinitions ??
            throw new ArgumentNullException(nameof(level100ActorDefinitions));
        _level100TutorialProgress = tutorialProgress;
        ResetDynamicState();
    }

    public WorldSnapshot Snapshot => CreateSnapshot();

    public WorldSnapshot Step(
        SimInput input,
        IReadOnlyList<Level100SimulationFact>? level100Facts = null)
    {
        input.Validate();
        _level100Destruction.ValidateExternalFacts(level100Facts);
        _tick++;

        if (input.HasAction(SimActions.Reset))
        {
            ResetDynamicState();
            return CreateSnapshot();
        }

        _level100MissionEvents.Clear();
        _level100ActorScriptCommands.Clear();
        _level100Destruction.BeginTick();
        AdvanceOpeningCamera();
        SyncLevel100PlayerState();
        _level100ActorScripts.AdvanceTick();
        PumpLevel100EventBus();
        _level100Mission.AdvanceTick(PlayerHull);
        PumpLevel100EventBus();
        ApplyLevel100Facts(level100Facts);

        SimInput playerInput = _level100Mission.Outcome == Level100MissionOutcome.Running &&
            Level100PlayerActive &&
            _level100OpeningTicksRemaining == 0
            ? input
            : SimInput.Idle;

        AdvanceTransition();

        if (_fireCooldownTicksRemaining > 0)
        {
            _fireCooldownTicksRemaining--;
        }

        TryToggleMode(playerInput);
        UpdateMovement(playerInput);
        UpdateWalkerFeet();
        UpdateLevel100TriggerActors();
        UpdateResources();
        TryFire(playerInput);
        UpdateProjectiles();
        SyncLevel100PlayerState();

        return CreateSnapshot();
    }

    private void AdvanceOpeningCamera()
    {
        if (_level100OpeningTicksRemaining > 0)
        {
            _level100OpeningTicksRemaining--;
        }
    }

    private Level100ActorPoseSnapshot PlayerPose =>
        _level100Actors.GetPose(_level100PlayerActorId);

    private SimVector2 PlayerPosition
    {
        get
        {
            Level100ActorPoseSnapshot pose = PlayerPose;
            return new SimVector2(
                pose.PositionMillimeters.X,
                pose.PositionMillimeters.Z);
        }
    }

    private SimVector2 PlayerVelocity
    {
        get
        {
            Level100ActorPoseSnapshot pose = PlayerPose;
            return new SimVector2(
                pose.LinearVelocityMillimetersPerTick.X,
                pose.LinearVelocityMillimetersPerTick.Z);
        }
    }

    private int PlayerGroundElevationMillimeters =>
        PlayerPose.PositionMillimeters.Y;

    private int PlayerGroundDeltaMillimeters =>
        PlayerPose.LinearVelocityMillimetersPerTick.Y;

    private int PlayerHull => _level100Actors.GetHealth(_level100PlayerActorId);

    private bool Level100PlayerActive => _level100Actors.IsActive(_level100PlayerActorId);

    private void CommitLevel100PlayerPose(
        SimVector2 position,
        int groundElevationMillimeters,
        SimVector2 velocity,
        int groundDeltaMillimeters)
    {
        (int yawSinFixed, int yawCosFixed) = FixedSinCos(_facingYawMicroRad);
        (int pitchSinFixed, int pitchCosFixed) = FixedSinCos(_facingPitchMicroRad);
        float yawSin = (float)yawSinFixed / FixedTrigScale;
        float yawCos = (float)yawCosFixed / FixedTrigScale;
        float pitchSin = (float)pitchSinFixed / FixedTrigScale;
        float pitchCos = (float)pitchCosFixed / FixedTrigScale;
        static int Bits(float value) => BitConverter.SingleToInt32Bits(value);

        var basis = new Level100FloatBasis3Bits(
            Bits(yawCos), Bits(0f), Bits(-yawSin),
            Bits(yawSin * pitchSin), Bits(pitchCos), Bits(yawCos * pitchSin),
            Bits(yawSin * pitchCos), Bits(-pitchSin), Bits(yawCos * pitchCos));
        _level100Actors.SetPose(
            _level100PlayerActorId,
            new Level100ActorPoseSnapshot(
                new SimVector3(
                    position.X,
                    groundElevationMillimeters,
                    position.Z),
                basis,
                new SimVector3(
                    velocity.X,
                    groundDeltaMillimeters,
                    velocity.Z),
                new SimVector3(
                    _walkerPitchVelocityMicroRadPerTick,
                    _walkerYawVelocityMicroRadPerTick,
                    0)));
    }

    private void SyncLevel100PlayerState()
    {
        Level100ActorPoseSnapshot pose = PlayerPose;
        CommitLevel100PlayerPose(
            new SimVector2(
                pose.PositionMillimeters.X,
                pose.PositionMillimeters.Z),
            pose.PositionMillimeters.Y,
            new SimVector2(
                pose.LinearVelocityMillimetersPerTick.X,
                pose.LinearVelocityMillimetersPerTick.Z),
            pose.LinearVelocityMillimetersPerTick.Y);
        _level100ActorScripts.SetPlayerInJetMode(_mode == VehicleMode.Jet);
    }

    private void DestroyLevel100PlayerActor()
    {
        if (_level100Actors.GetLifecycle(_level100PlayerActorId) ==
            Level100ActorLifecycle.Destroyed)
        {
            return;
        }

        _level100Destruction.ReportExternalStartedDying(_level100PlayerActorId);
        _level100Destruction.ReportExternalDied(_level100PlayerActorId);
        DrainAndDispatchLevel100ActorFacts();
    }

    private void ApplyLevel100Facts(IReadOnlyList<Level100SimulationFact>? facts)
    {
        if (facts is null)
        {
            return;
        }

        foreach (Level100SimulationFact fact in facts)
        {
            ArgumentNullException.ThrowIfNull(fact);
            switch (fact)
            {
                case Level100ActorHitFact hit:
                    _level100Actors.ReportHit(
                        hit.ActorId,
                        hit.OtherActorId,
                        hit.OtherThingTypeMask);
                    DrainAndDispatchLevel100ActorFacts();
                    break;
                case Level100ActorStartedDyingFact startedDying:
                    _level100Destruction.ReportExternalStartedDying(
                        startedDying.ActorId);
                    DrainAndDispatchLevel100ActorFacts();
                    break;
                case Level100ActorDiedFact died:
                    _level100Destruction.ReportExternalDied(died.ActorId);
                    DrainAndDispatchLevel100ActorFacts();
                    break;
                case Level100ActorPoseFact pose:
                    if (pose.ActorId == _level100PlayerActorId)
                    {
                        throw new InvalidOperationException(
                            "Player pose is owned by the deterministic vehicle simulation.");
                    }
                    _level100Actors.SetPose(pose.ActorId, pose.Pose);
                    break;
                case Level100ActorActivationFact activation:
                    if (activation.Active)
                    {
                        _level100Actors.Activate(activation.ActorId);
                    }
                    else
                    {
                        _level100Actors.Deactivate(activation.ActorId);
                    }
                    break;
                case Level100ActorObjectiveFact objective:
                    _level100Actors.SetObjective(objective.ActorId, objective.IsObjective);
                    break;
                case Level100ActorHealthFact health:
                    _level100Destruction.SetExternalHealth(
                        health.ActorId,
                        health.Health);
                    break;
                case Level100SpawnThingFact spawn:
                    IReadOnlyList<Level100ActorId> spawned = _level100Actors.SpawnThing(
                        spawn.OwnerActorId,
                        spawn.DefinitionName,
                        spawn.SpawnerName,
                        spawn.Count,
                        spawn.ScriptName);
                    foreach (Level100ActorId actorId in spawned)
                    {
                        _level100Destruction.RegisterActor(actorId);
                        _level100ActorScripts.AttachAndInitializeSpawnedActor(
                            actorId,
                            spawn.ScriptName);
                    }
                    break;
                case Level100MissionInputFact missionInput:
                    _level100Mission.SubmitInput(missionInput.Input);
                    break;
                case Level100PlayerDamageFact damage:
                    if (damage.Damage <= 0)
                    {
                        throw new ArgumentOutOfRangeException(
                            nameof(facts),
                            "Player damage must be positive.");
                    }

                    int hull = Math.Max(0, PlayerHull - damage.Damage);
                    _level100Destruction.SetExternalHealth(
                        _level100PlayerActorId,
                        hull);
                    _level100Mission.ReportPlayerHitDuringEvasion();
                    if (hull == 0)
                    {
                        DestroyLevel100PlayerActor();
                        _level100Mission.ReportPlayerDeath();
                    }
                    break;
                case Level100PlayerDeathFact:
                    DestroyLevel100PlayerActor();
                    _level100Mission.ReportPlayerDeath();
                    break;
                case Level100WaterLossFact:
                    _level100Mission.ReportWaterLoss();
                    break;
                case Level100ActorScriptWaitCompletedFact completed:
                    if (!_level100ActorScripts.CompleteMechanicsWait(
                            completed.ActorId,
                            completed.WaitKind,
                            completed.Argument))
                    {
                        throw new InvalidOperationException(
                            $"Actor {completed.ActorId} has no matching script mechanics wait.");
                    }
                    break;
                default:
                    throw new ArgumentOutOfRangeException(
                        nameof(facts),
                        $"Unknown Level 100 fact type {fact.GetType().Name}.");
            }

            PumpLevel100EventBus();
        }
    }

    private void ApplyWeaponAvailability(Level100WeaponAvailabilityChanged weapon)
    {
        switch (weapon.Weapon)
        {
            case Level100MissionWeapon.PulseCannonPod:
                _level100PulseCannonEnabled = weapon.Enabled;
                break;
            case Level100MissionWeapon.MechTwinVulcanCannon:
                _level100VulcanCannonEnabled = weapon.Enabled;
                break;
            case Level100MissionWeapon.MechVulcanCannon:
                _level100MechVulcanCannonEnabled = weapon.Enabled;
                break;
            case Level100MissionWeapon.MissilePod:
                _level100MissilePodEnabled = weapon.Enabled;
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(weapon));
        }
    }

    private void ApplyHudEmphasis(Level100HudEmphasisChanged emphasis)
    {
        if (emphasis.PartId is < 0 or > 30)
        {
            throw new InvalidOperationException(
                $"Released Level 100 requested unsupported HUD part {emphasis.PartId}.");
        }

        int bit = 1 << emphasis.PartId;
        _level100HudEmphasisMask = emphasis.Emphasized
            ? _level100HudEmphasisMask | bit
            : _level100HudEmphasisMask & ~bit;
    }

    private void ApplyLevel100ActorCommand(Level100ActorCommandRequested command)
    {
        switch (command.Command)
        {
            case Level100ActorCommand.Activate:
                _level100Actors.Activate(command.ActorId);
                break;
            case Level100ActorCommand.Deactivate:
                _level100Actors.Deactivate(command.ActorId);
                break;
            case Level100ActorCommand.SetObjective:
                _level100Actors.SetObjective(command.ActorId, true);
                break;
            case Level100ActorCommand.UnsetObjective:
                _level100Actors.SetObjective(command.ActorId, false);
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(command));
        }
    }

    private void ApplyLevel100SpawnRequest(Level100SpawnThingRequested spawn)
    {
        IReadOnlyList<Level100ActorId> spawned = _level100Actors.SpawnThing(
            spawn.OwnerActorId,
            spawn.DefinitionName,
            spawn.SpawnerName,
            spawn.Count,
            spawn.ScriptName);
        foreach (Level100ActorId actorId in spawned)
        {
            _level100Destruction.RegisterActor(actorId);
            _level100ActorScripts.AttachAndInitializeSpawnedActor(
                actorId,
                spawn.ScriptName);
        }
    }

    private void DrainAndDispatchLevel100ActorFacts()
    {
        foreach (Level100ActorFactSnapshot fact in _level100Actors.DrainFacts())
        {
            _level100ActorScripts.DispatchFact(fact);
            PumpLevel100EventBus();
        }
    }

    private void PumpLevel100EventBus()
    {
        for (int pass = 0; pass < 1_000; pass++)
        {
            IReadOnlyList<Level100MissionEvent> missionEvents = _level100Mission.DrainEvents();
            foreach (Level100MissionEvent missionEvent in missionEvents)
            {
                _level100MissionEvents.Add(missionEvent);
                ApplyLevel100MissionEvent(missionEvent);
            }

            IReadOnlyList<Level100ActorScriptEventPosted> actorEvents =
                _level100ActorScripts.DrainPostedEvents();
            IReadOnlyList<Level100ActorScriptCommand> actorCommands =
                _level100ActorScripts.DrainCommands();
            _level100ActorScriptCommands.AddRange(actorCommands);
            foreach (Level100ActorScriptEventPosted actorEvent in actorEvents)
            {
                if (actorEvent.ActorId is { } actorId)
                {
                    Level100ActorSnapshot actor = _level100Actors.GetActor(actorId);
                    if (actor.Trigger.HasValue &&
                        actor.TriggerEntered &&
                        !actor.TriggerEventDispatched)
                    {
                        _level100Actors.MarkTriggerEventDispatched(actorId);
                    }
                }

                _level100Mission.QueueExternalEvent(actorEvent.EventName);
            }

            if (missionEvents.Count == 0 && actorEvents.Count == 0 && actorCommands.Count == 0)
            {
                return;
            }
        }

        throw new InvalidOperationException("Level 100 script event bus did not settle.");
    }

    private void ApplyLevel100MissionEvent(Level100MissionEvent missionEvent)
    {
        switch (missionEvent)
        {
            case Level100PlayerActivationChanged activation:
                if (activation.Active)
                {
                    _level100Actors.Activate(_level100PlayerActorId);
                }
                else
                {
                    _level100Actors.Deactivate(_level100PlayerActorId);
                }
                break;
            case Level100FlightModeAvailabilityChanged flight:
                _level100FlightEnabled = flight.Enabled;
                break;
            case Level100WeaponAvailabilityChanged weapon:
                ApplyWeaponAvailability(weapon);
                break;
            case Level100HudEmphasisChanged emphasis:
                ApplyHudEmphasis(emphasis);
                break;
            case Level100ActorCommandRequested actorCommand:
                ApplyLevel100ActorCommand(actorCommand);
                break;
            case Level100SpawnThingRequested spawn:
                ApplyLevel100SpawnRequest(spawn);
                break;
            case Level100MissionEventPosted posted:
                _level100ActorScripts.PublishEvent(posted.EventName);
                break;
        }
    }

    private void TryToggleMode(SimInput input)
    {
        if (!input.HasAction(SimActions.ToggleMode) ||
            !_level100FlightEnabled ||
            _transformTicksRemaining != 0 ||
            _energy < SimulationConstants.TransformEnergyThreshold)
        {
            return;
        }

        _energy -= SimulationConstants.TransformEnergyCost;
        if (_mode == VehicleMode.Walker)
        {
            _transition = VehicleTransition.WalkerToJet;
            _transformTicksRemaining = SimulationConstants.WalkerToJetTransitionTicks;
            return;
        }

        _mode = VehicleMode.Walker;
        _transformTicksRemaining = SimulationConstants.TransformDurationTicks;
    }

    private void AdvanceTransition()
    {
        if (_transformTicksRemaining == 0)
        {
            return;
        }

        _transformTicksRemaining--;
        if (_transformTicksRemaining != 0 || _transition != VehicleTransition.WalkerToJet)
        {
            return;
        }

        _mode = VehicleMode.Jet;
        _transition = VehicleTransition.None;
        _shield = 0;
    }

    private void UpdateMovement(SimInput input)
    {
        Level100ActorPoseSnapshot player = PlayerPose;
        SimVector2 position = new(
            player.PositionMillimeters.X,
            player.PositionMillimeters.Z);
        int groundElevation = player.PositionMillimeters.Y;
        SimVector2 velocity = new(
            player.LinearVelocityMillimetersPerTick.X,
            player.LinearVelocityMillimetersPerTick.Z);
        CommitLevel100PlayerPose(position, groundElevation, velocity, 0);
        if (_transformTicksRemaining != 0)
        {
            CommitLevel100PlayerPose(position, groundElevation, SimVector2.Zero, 0);
            _walkerYawVelocityMicroRadPerTick = 0;
            _walkerPitchVelocityMicroRadPerTick = 0;
            return;
        }

        if (_mode == VehicleMode.Walker)
        {
            UpdateWalkerYaw(input.LookX, input.LookXAnalogPermille);
            UpdateWalkerPitch(input.LookY, input.LookYAnalogPermille);
            UpdateWalkerMovement(input);
            return;
        }

        _walkerYawVelocityMicroRadPerTick = 0;
        _walkerPitchVelocityMicroRadPerTick = 0;
        if (input.LookX != 0)
        {
            _facingYawMicroRad = NormalizeMicroRad(
                _facingYawMicroRad + (input.LookX * ProvisionalJetLookYawRateMicroRadPerTick));
            QuantizeFacingFromYaw();
        }

        SimVector2 jetVelocity = ProjectEightWayInput(
            input,
            SimulationConstants.JetSpeedPerTick,
            SimulationConstants.JetSpeedPerTick);
        MovePlayer(jetVelocity);
    }

    private void UpdateWalkerYaw(sbyte lookX, short analogPermille)
    {
        int inputPermille = ResolveLookInputPermille(lookX, analogPermille);
        _walkerYawVelocityMicroRadPerTick =
            (int)((long)_walkerYawVelocityMicroRadPerTick *
                SimulationConstants.WalkerYawRetentionNumerator /
                SimulationConstants.WalkerYawRetentionDenominator) +
            ScaleLookInput(
                SimulationConstants.WalkerYawInputMicroRadPerTick,
                inputPermille);
        _facingYawMicroRad = NormalizeMicroRad(
            _facingYawMicroRad + _walkerYawVelocityMicroRadPerTick);
        QuantizeFacingFromYaw();
    }

    private void UpdateWalkerPitch(sbyte lookY, short analogPermille)
    {
        int inputPermille = ResolveLookInputPermille(lookY, analogPermille);
        _walkerPitchVelocityMicroRadPerTick =
            (int)((long)_walkerPitchVelocityMicroRadPerTick *
                SimulationConstants.WalkerPitchRetentionNumerator /
                SimulationConstants.WalkerPitchRetentionDenominator) +
            ScaleLookInput(
                SimulationConstants.WalkerPitchInputMicroRadPerTick,
                inputPermille);

        int nextPitch = _facingPitchMicroRad + _walkerPitchVelocityMicroRadPerTick;
        int clampedPitch = Math.Clamp(
            nextPitch,
            SimulationConstants.WalkerPitchUpLimitMicroRad,
            SimulationConstants.WalkerPitchDownLimitMicroRad);
        _facingPitchMicroRad = clampedPitch;
        if (clampedPitch != nextPitch)
        {
            _walkerPitchVelocityMicroRadPerTick = 0;
        }
    }

    private static int ResolveLookInputPermille(sbyte digital, short analog) =>
        Math.Clamp((digital * 1_000) + analog, -1_000, 1_000);

    private static int ScaleLookInput(int fullScale, int inputPermille)
    {
        long scaled = (long)fullScale * inputPermille;
        return (int)(scaled >= 0
            ? (scaled + 500) / 1_000
            : (scaled - 500) / 1_000);
    }

    private void UpdateWalkerMovement(SimInput input)
    {
        SimVector2 acceleration = ProjectWalkerInput(
            input,
            SimulationConstants.WalkerAccelerationPerTick);
        var velocity = new SimVector2(
            RetainWalkerVelocity(PlayerVelocity.X) + acceleration.X,
            RetainWalkerVelocity(PlayerVelocity.Z) + acceleration.Z);
        MoveWalker(ClampMagnitude(velocity, SimulationConstants.WalkerMaximumSpeedPerTick));
    }

    private static int RetainWalkerVelocity(int velocity) =>
        (int)((long)velocity * SimulationConstants.WalkerVelocityRetentionNumerator /
            SimulationConstants.WalkerVelocityRetentionDenominator);

    private SimVector2 ProjectWalkerInput(SimInput input, int acceleration)
    {
        int localX = input.MoveX * acceleration;
        int localZ = input.MoveZ * acceleration;
        if (input.MoveX != 0 && input.MoveZ != 0)
        {
            localX = localX * 181 / 256;
            localZ = localZ * 181 / 256;
        }

        (int sin, int cos) = FixedSinCos(_facingYawMicroRad);
        return new SimVector2(
            DivideRoundNearest(((long)localX * cos) - ((long)localZ * sin), FixedTrigScale),
            DivideRoundNearest(((long)localX * sin) + ((long)localZ * cos), FixedTrigScale));
    }

    private SimVector2 ProjectEightWayInput(SimInput input, int speedX, int speedZ)
    {
        // Jet movement remains a bounded eight-way approximation. Walker
        // acceleration uses the continuous released body-yaw basis above.
        int forwardX = _facingX;
        int forwardZ = _facingZ;
        int headingScale = forwardX != 0 && forwardZ != 0 ? 181 : 256;
        int forwardXScaled = forwardX * headingScale;
        int forwardZScaled = forwardZ * headingScale;
        int rightXScaled = forwardZScaled;
        int rightZScaled = -forwardXScaled;
        int velocityX =
            ((input.MoveZ * speedZ * forwardXScaled) +
             (input.MoveX * speedX * rightXScaled)) / 256;
        int velocityZ =
            ((input.MoveZ * speedZ * forwardZScaled) +
             (input.MoveX * speedX * rightZScaled)) / 256;
        if (input.MoveX != 0 && input.MoveZ != 0)
        {
            velocityX = velocityX * 181 / 256;
            velocityZ = velocityZ * 181 / 256;
        }

        return new SimVector2(velocityX, velocityZ);
    }

    private const int FixedTrigScale = 1 << 30;
    private const int HalfPiMicroRad = 1_570_796;
    private const int PiMicroRad = 3_141_593;
    private const int CordicGainQ30 = 652_032_874;

    // Integer CORDIC keeps the local-to-world rotation deterministic without
    // introducing platform floating-point math into Core state updates.
    private static ReadOnlySpan<int> CordicAnglesMicroRad =>
    [
        785_398, 463_648, 244_979, 124_355, 62_419, 31_240, 15_624,
        7_812, 3_906, 1_953, 977, 488, 244, 122, 61, 31, 15, 8, 4, 2, 1,
    ];

    private static (int Sin, int Cos) FixedSinCos(int angleMicroRad)
    {
        int angle = NormalizeMicroRad(angleMicroRad);
        int resultSign = 1;
        if (angle > HalfPiMicroRad)
        {
            angle -= PiMicroRad;
            resultSign = -1;
        }
        else if (angle < -HalfPiMicroRad)
        {
            angle += PiMicroRad;
            resultSign = -1;
        }

        long x = CordicGainQ30;
        long y = 0;
        int remainder = angle;
        ReadOnlySpan<int> angles = CordicAnglesMicroRad;
        for (int index = 0; index < angles.Length; index++)
        {
            long previousX = x;
            if (remainder >= 0)
            {
                x -= y >> index;
                y += previousX >> index;
                remainder -= angles[index];
            }
            else
            {
                x += y >> index;
                y -= previousX >> index;
                remainder += angles[index];
            }
        }

        return ((int)y * resultSign, (int)x * resultSign);
    }

    private static int DivideRoundNearest(long numerator, int denominator)
    {
        long half = denominator / 2L;
        return (int)(numerator >= 0
            ? (numerator + half) / denominator
            : (numerator - half) / denominator);
    }

    private void MoveWalker(SimVector2 velocity)
    {
        SimVector2 currentPosition = PlayerPosition;
        SimVector2 nextPosition = new(
            currentPosition.X + velocity.X,
            currentPosition.Z + velocity.Z);
        nextPosition = ResolveLevel100WalkerContact(
            currentPosition,
            nextPosition,
            SimulationConstants.Level100ControlTowerPosition,
            SimulationConstants.Level100ControlTowerContactRadius);
        nextPosition = ResolveLevel100WalkerContact(
            currentPosition,
            nextPosition,
            SimulationConstants.Level100TankFactoryPosition,
            SimulationConstants.Level100TankFactoryContactRadius);
        CommitPlayerPosition(nextPosition);
    }

    private static SimVector2 ResolveLevel100WalkerContact(
        SimVector2 currentPosition,
        SimVector2 nextPosition,
        SimVector2 facilityPosition,
        int contactRadius)
    {
        long offsetX = (long)nextPosition.X - facilityPosition.X;
        long offsetZ = (long)nextPosition.Z - facilityPosition.Z;
        long radiusSquared = (long)contactRadius * contactRadius;
        long distanceSquared = (offsetX * offsetX) + (offsetZ * offsetZ);
        if (distanceSquared >= radiusSquared)
        {
            return nextPosition;
        }

        if (distanceSquared == 0)
        {
            offsetX = (long)currentPosition.X - facilityPosition.X;
            offsetZ = (long)currentPosition.Z - facilityPosition.Z;
            distanceSquared = (offsetX * offsetX) + (offsetZ * offsetZ);
            if (distanceSquared == 0)
            {
                return new SimVector2(facilityPosition.X + contactRadius, facilityPosition.Z);
            }
        }

        int distance = IntegerSquareRoot(distanceSquared);
        int resolvedX =
            facilityPosition.X + DivideRoundNearest(offsetX * contactRadius, distance);
        int resolvedZ =
            facilityPosition.Z + DivideRoundNearest(offsetZ * contactRadius, distance);
        while (true)
        {
            long resolvedOffsetX = (long)resolvedX - facilityPosition.X;
            long resolvedOffsetZ = (long)resolvedZ - facilityPosition.Z;
            if ((resolvedOffsetX * resolvedOffsetX) + (resolvedOffsetZ * resolvedOffsetZ) >=
                radiusSquared)
            {
                return new SimVector2(resolvedX, resolvedZ);
            }

            if (Math.Abs(offsetX) >= Math.Abs(offsetZ))
            {
                resolvedX += Math.Sign(offsetX);
            }
            else
            {
                resolvedZ += Math.Sign(offsetZ);
            }
        }
    }

    private void MovePlayer(SimVector2 velocity)
    {
        SimVector2 currentPosition = PlayerPosition;
        SimVector2 nextPosition = new(
            currentPosition.X + velocity.X,
            currentPosition.Z + velocity.Z);
        CommitPlayerPosition(nextPosition);
    }

    private void CommitPlayerPosition(SimVector2 nextPosition)
    {
        SimVector2 previousPosition = PlayerPosition;
        int previousGroundElevation = PlayerGroundElevationMillimeters;
        SimVector2 velocity = new(
            nextPosition.X - previousPosition.X,
            nextPosition.Z - previousPosition.Z);
        int groundElevation =
            Level100Terrain.Instance.SampleGroundElevationMillimeters(nextPosition);
        CommitLevel100PlayerPose(
            nextPosition,
            groundElevation,
            velocity,
            groundElevation - previousGroundElevation);
    }

    private void UpdateWalkerFeet()
    {
        if (_mode != VehicleMode.Walker || _transition != VehicleTransition.None)
        {
            AlignWalkerFeetToNaturalTargets();
            return;
        }

        long playerDisplacementSquared =
            ((long)PlayerVelocity.X * PlayerVelocity.X) +
            ((long)PlayerVelocity.Z * PlayerVelocity.Z) +
            ((long)PlayerGroundDeltaMillimeters * PlayerGroundDeltaMillimeters);
        bool ownerMoved = playerDisplacementSquared > 10L * 10L;
        int threshold = ownerMoved
            ? SimulationConstants.WalkerFootMovingThresholdMillimeters
            : SimulationConstants.WalkerFootStationaryThresholdMillimeters;

        for (int footIndex = 0; footIndex < _walkerFeet.Count; footIndex++)
        {
            MutableWalkerFoot foot = _walkerFeet[footIndex];
            SimVector2 targetPosition = NaturalWalkerFootPosition(foot.StanceOffset);
            int targetGround =
                Level100Terrain.Instance.SampleGroundElevationMillimeters(targetPosition);
            int deltaX = targetPosition.X - foot.Position.X;
            int deltaZ = targetPosition.Z - foot.Position.Z;
            int deltaGround = targetGround - foot.GroundElevationMillimeters;

            if (foot.PhaseThirds == 0)
            {
                long distanceSquared =
                    ((long)deltaX * deltaX) +
                    ((long)deltaZ * deltaZ) +
                    ((long)deltaGround * deltaGround);
                if (distanceSquared > (long)threshold * threshold &&
                    CanBeginWalkerFootSwing(footIndex, distanceSquared, threshold))
                {
                    // Released CMCMech enters phase one without moving or
                    // lifting the planted point until its next update.
                    foot.PhaseThirds = 3;
                }
                continue;
            }

            foot.PhaseThirds +=
                SimulationConstants.WalkerFootPhaseUnitsPerSecond * 3 /
                SimulationConstants.TicksPerSecond;
            if (foot.PhaseThirds >=
                (SimulationConstants.WalkerFootPhaseEnd + 1) * 3)
            {
                foot.PhaseThirds = 0;
                foot.LiftMillimeters = 0;
                continue;
            }

            int phaseDenominator = SimulationConstants.WalkerFootPhaseEnd * 3;
            foot.Position = new SimVector2(
                foot.Position.X + DivideRoundNearest(
                    (long)deltaX * foot.PhaseThirds,
                    phaseDenominator),
                foot.Position.Z + DivideRoundNearest(
                    (long)deltaZ * foot.PhaseThirds,
                    phaseDenominator));
            foot.GroundElevationMillimeters =
                Level100Terrain.Instance.SampleGroundElevationMillimeters(foot.Position);
            int phaseAngleMicroRad = DivideRoundNearest(
                (long)foot.PhaseThirds * PiMicroRad,
                phaseDenominator);
            (int phaseSin, _) = FixedSinCos(phaseAngleMicroRad);
            foot.LiftMillimeters = Math.Max(
                0,
                DivideRoundNearest(
                    (long)phaseSin * SimulationConstants.WalkerFootLiftMillimeters,
                    FixedTrigScale));
        }
    }

    private bool CanBeginWalkerFootSwing(
        int footIndex,
        long distanceSquared,
        int threshold)
    {
        long forcedThreshold = threshold * 2L;
        if (distanceSquared > forcedThreshold * forcedThreshold)
        {
            return true;
        }

        int earlySwings = _walkerFeet.Count(foot =>
            foot.PhaseThirds > 0 &&
            foot.PhaseThirds <= (SimulationConstants.WalkerFootPhaseEnd / 2) * 3);
        if (earlySwings >= SimulationConstants.WalkerFootMaximumEarlySwings)
        {
            return false;
        }

        bool sameParityReady = false;
        bool predecessorClear = true;
        for (int otherIndex = 0; otherIndex < _walkerFeet.Count; otherIndex++)
        {
            int otherPhase = _walkerFeet[otherIndex].PhaseThirds;
            bool otherReady = otherPhase == 0 ||
                otherPhase > (SimulationConstants.WalkerFootPhaseEnd / 2) * 3;
            if (otherReady && otherIndex != footIndex)
            {
                if ((otherIndex & 1) == (footIndex & 1))
                {
                    sameParityReady = true;
                }
            }
            else if (otherIndex == footIndex - 1)
            {
                predecessorClear = false;
            }
        }

        return sameParityReady && predecessorClear;
    }

    private void BuildWalkerFeet()
    {
        _walkerFeet.Clear();
        for (int index = 0;
             index < SimulationConstants.WalkerFootStanceOffsetsMillimeters.Count;
             index++)
        {
            SimVector2 stance = SimulationConstants.WalkerFootStanceOffsetsMillimeters[index];
            SimVector2 position = NaturalWalkerFootPosition(stance);
            _walkerFeet.Add(new MutableWalkerFoot
            {
                Id = index,
                StanceOffset = stance,
                Position = position,
                GroundElevationMillimeters =
                    Level100Terrain.Instance.SampleGroundElevationMillimeters(position),
            });
        }
    }

    private void AlignWalkerFeetToNaturalTargets()
    {
        foreach (MutableWalkerFoot foot in _walkerFeet)
        {
            foot.Position = NaturalWalkerFootPosition(foot.StanceOffset);
            foot.GroundElevationMillimeters =
                Level100Terrain.Instance.SampleGroundElevationMillimeters(foot.Position);
            foot.PhaseThirds = 0;
            foot.LiftMillimeters = 0;
        }
    }

    private SimVector2 NaturalWalkerFootPosition(SimVector2 stanceOffset)
    {
        SimVector2 playerPosition = PlayerPosition;
        (int sin, int cos) = FixedSinCos(_facingYawMicroRad);
        return new SimVector2(
            playerPosition.X + DivideRoundNearest(
                ((long)stanceOffset.X * cos) - ((long)stanceOffset.Z * sin),
                FixedTrigScale),
            playerPosition.Z + DivideRoundNearest(
                ((long)stanceOffset.X * sin) + ((long)stanceOffset.Z * cos),
                FixedTrigScale));
    }

    private void UpdateLevel100TriggerActors()
    {
        DrainAndDispatchLevel100ActorFacts();

        foreach (Level100ActorSnapshot trigger in _level100Actors.Snapshot.Actors
            .Where(actor => actor.Trigger.HasValue && actor.Pose is not null)
            .OrderBy(actor => actor.ActorId.Value))
        {
            if (trigger.TriggerEventDispatched || trigger.TriggerEntered)
            {
                continue;
            }

            Level100MissionJetModeState jetModeState =
                Level100MissionTiming.JetModeState(_mode, _transition);
            SimVector2 triggerPosition = new(
                trigger.Pose!.PositionMillimeters.X,
                trigger.Pose.PositionMillimeters.Z);
            if (trigger.Active &&
                (!Level100MissionTiming.RequiresNotInJetMode(trigger.Trigger!.Value) ||
                 jetModeState ==
                    Level100MissionJetModeState.NotInJetMode) &&
                IsWithinLevel100Trigger(PlayerPosition, triggerPosition))
            {
                // The side actor owns its factual overlap and released pause;
                // LevelScript sees only the resulting named event.
                _level100Actors.BeginTriggerDispatch(
                    trigger.ActorId,
                    jetModeState);
                DrainAndDispatchLevel100ActorFacts();
            }
        }
    }

    private static bool IsWithinLevel100Trigger(SimVector2 position, SimVector2 trigger)
    {
        long deltaX = (long)position.X - trigger.X;
        long deltaZ = (long)position.Z - trigger.Z;
        long radius = SimulationConstants.Level100ObjectiveTriggerRadius;
        return (deltaX * deltaX) + (deltaZ * deltaZ) <= radius * radius;
    }

    private static SimVector2 ClampMagnitude(SimVector2 value, int maximum)
    {
        long magnitudeSquared = ((long)value.X * value.X) + ((long)value.Z * value.Z);
        long maximumSquared = (long)maximum * maximum;
        if (magnitudeSquared <= maximumSquared)
        {
            return value;
        }

        int magnitude = IntegerSquareRoot(magnitudeSquared);
        if ((long)magnitude * magnitude < magnitudeSquared)
        {
            magnitude++;
        }

        return new SimVector2(
            value.X * maximum / magnitude,
            value.Z * maximum / magnitude);
    }

    private static int IntegerSquareRoot(long value)
    {
        int low = 0;
        int high = 46_340;
        int result = 0;
        while (low <= high)
        {
            int middle = low + ((high - low) / 2);
            long square = (long)middle * middle;
            if (square <= value)
            {
                result = middle;
                low = middle + 1;
            }
            else
            {
                high = middle - 1;
            }
        }

        return result;
    }

    /// <summary>
    /// Full turn rounded to integer micro-radians. Keeps yaw in (−half, half].
    /// </summary>
    private const int TwoPiMicroRad = 6_283_185;

    private static int NormalizeMicroRad(int microRad)
    {
        int wrapped = microRad % TwoPiMicroRad;
        if (wrapped > TwoPiMicroRad / 2)
        {
            wrapped -= TwoPiMicroRad;
        }
        else if (wrapped <= -(TwoPiMicroRad / 2))
        {
            wrapped += TwoPiMicroRad;
        }

        return wrapped;
    }

    private void QuantizeFacingFromYaw()
    {
        // Eight-way snap from continuous yaw for FacingX/Z and fire aim.
        int yaw = NormalizeMicroRad(_facingYawMicroRad);
        int sector = (int)((long)((yaw + TwoPiMicroRad) % TwoPiMicroRad) * 8 / TwoPiMicroRad);
        (_facingX, _facingZ) = sector switch
        {
            0 => ((sbyte)0, (sbyte)1),
            1 => ((sbyte)1, (sbyte)1),
            2 => ((sbyte)1, (sbyte)0),
            3 => ((sbyte)1, (sbyte)-1),
            4 => ((sbyte)0, (sbyte)-1),
            5 => ((sbyte)-1, (sbyte)-1),
            6 => ((sbyte)-1, (sbyte)0),
            _ => ((sbyte)-1, (sbyte)1),
        };
    }

    private void UpdateResources()
    {
        if (_mode == VehicleMode.Walker && _transition == VehicleTransition.None)
        {
            _energy = Math.Min(
                SimulationConstants.MaximumEnergy,
                _energy + SimulationConstants.WalkerEnergyRegenerationPerTick);
            _shield = Math.Min(
                SimulationConstants.MaximumShield,
                _shield + SimulationConstants.WalkerShieldRegenerationPerTick);
            return;
        }

        _energy = Math.Max(0, _energy - SimulationConstants.JetEnergyDrainPerTick);
        _shield = 0;
        if (_energy == 0)
        {
            _mode = VehicleMode.Walker;
            _transition = VehicleTransition.None;
            _transformTicksRemaining = SimulationConstants.TransformDurationTicks;
        }
    }

    private void TryFire(SimInput input)
    {
        if (!input.HasAction(SimActions.Fire) ||
            !_level100PulseCannonEnabled ||
            _transformTicksRemaining != 0 ||
            _fireCooldownTicksRemaining != 0 ||
            _energy < SimulationConstants.FireEnergyCost)
        {
            return;
        }

        (int sin, int cos) = FixedSinCos(_facingYawMicroRad);
        (int pitchSin, int pitchCos) = FixedSinCos(_facingPitchMicroRad);
        int horizontalSpeed = DivideRoundNearest(
            (long)pitchCos * SimulationConstants.ProjectileSpeedPerTick,
            FixedTrigScale);
        int velocityX = DivideRoundNearest(
            -(long)sin * horizontalSpeed,
            FixedTrigScale);
        int velocityZ = DivideRoundNearest(
            (long)cos * horizontalSpeed,
            FixedTrigScale);
        int verticalVelocity = DivideRoundNearest(
            -(long)pitchSin * SimulationConstants.ProjectileSpeedPerTick,
            FixedTrigScale);
        int emitterForwardPlane = DivideRoundNearest(
            ((long)SimulationConstants.PulseCannonEmitterForwardMillimeters * pitchCos) +
            ((long)SimulationConstants.PulseCannonEmitterUpMillimeters * pitchSin),
            FixedTrigScale);
        int emitterVerticalOffset = DivideRoundNearest(
            (-(long)SimulationConstants.PulseCannonEmitterForwardMillimeters * pitchSin) +
            ((long)SimulationConstants.PulseCannonEmitterUpMillimeters * pitchCos),
            FixedTrigScale);
        int emitterOffsetX = DivideRoundNearest(
            ((long)SimulationConstants.PulseCannonEmitterRightMillimeters * cos) -
            ((long)emitterForwardPlane * sin),
            FixedTrigScale);
        int emitterOffsetZ = DivideRoundNearest(
            ((long)SimulationConstants.PulseCannonEmitterRightMillimeters * sin) +
            ((long)emitterForwardPlane * cos),
            FixedTrigScale);

        _energy -= SimulationConstants.FireEnergyCost;
        _fireCooldownTicksRemaining = SimulationConstants.FireCooldownTicks;
        SimVector2 playerPosition = PlayerPosition;
        _projectiles.Add(new MutableProjectile
        {
            Id = _nextProjectileId++,
            Position = new SimVector2(
                playerPosition.X + emitterOffsetX,
                playerPosition.Z + emitterOffsetZ),
            Velocity = new SimVector2(velocityX, velocityZ),
            ElevationMillimeters = PlayerGroundElevationMillimeters +
                Level100Terrain.WalkerCenterOfGravityMillimeters +
                emitterVerticalOffset,
            VerticalVelocityMillimetersPerTick = verticalVelocity,
            RemainingTicks = SimulationConstants.ProjectileLifetimeTicks,
        });
    }

    private void UpdateProjectiles()
    {
        for (int projectileIndex = _projectiles.Count - 1; projectileIndex >= 0; projectileIndex--)
        {
            MutableProjectile projectile = _projectiles[projectileIndex];
            var start = new SimVector3(
                projectile.Position.X,
                projectile.ElevationMillimeters,
                projectile.Position.Z);
            var end = new SimVector3(
                checked(projectile.Position.X + projectile.Velocity.X),
                checked(projectile.ElevationMillimeters +
                    projectile.VerticalVelocityMillimetersPerTick),
                checked(projectile.Position.Z + projectile.Velocity.Z));
            projectile.Position = new SimVector2(end.X, end.Z);
            projectile.ElevationMillimeters = end.Y;
            projectile.RemainingTicks--;

            bool hit = _level100Destruction.TryApplyPulseSweep(
                start,
                end,
                out _);
            if (hit)
            {
                DrainAndDispatchLevel100ActorFacts();
            }

            if (hit || projectile.RemainingTicks <= 0)
            {
                _projectiles.RemoveAt(projectileIndex);
            }
        }
    }

    private void ResetDynamicState()
    {
        _nextProjectileId = 1;
        _mode = VehicleMode.Walker;
        _transition = VehicleTransition.None;
        _facingYawMicroRad = SimulationConstants.Level100PlayerStartYawMicroRad;
        QuantizeFacingFromYaw();
        _walkerYawVelocityMicroRadPerTick = 0;
        _facingPitchMicroRad = 0;
        _walkerPitchVelocityMicroRadPerTick = 0;
        _energy = SimulationConstants.MaximumEnergy;
        _shield = SimulationConstants.MaximumShield;
        _transformTicksRemaining = 0;
        _fireCooldownTicksRemaining = 0;
        _level100OpeningTicksRemaining = SimulationConstants.Level100OpeningPanTicks;
        _level100FlightEnabled = true;
        _level100PulseCannonEnabled = false;
        _level100VulcanCannonEnabled = false;
        _level100MechVulcanCannonEnabled = false;
        _level100MissilePodEnabled = false;
        _level100HudEmphasisMask = 0;
        _projectiles.Clear();
        _level100Actors = new Level100ActorRegistry(_level100ActorDefinitions);
        _level100Destruction = new Level100DestructionRuntime(_level100Actors);
        _level100PlayerActorId = _level100Actors.GetThingRef("Player 1") ??
            throw new InvalidOperationException("Level 100 Player is missing.");
        _level100Actors.SetHealth(_level100PlayerActorId, SimulationConstants.MaximumHull);
        _level100Actors.Activate(_level100PlayerActorId);
        SimVector2 initialPosition = SimVector2.Zero;
        CommitLevel100PlayerPose(
            initialPosition,
            Level100Terrain.Instance.SampleGroundElevationMillimeters(initialPosition),
            SimVector2.Zero,
            0);
        BuildWalkerFeet();
        _level100ActorScripts = new Level100ActorScriptRuntime(
            _level100Actors,
            _level100PlayerActorId);
        _level100ActorScripts.InitializeReleasedScripts();
        _level100MissionEvents.Clear();
        _level100ActorScriptCommands.Clear();
        _level100Mission = new Level100Mission(
            _level100Actors,
            _level100PlayerActorId,
            _level100TutorialProgress,
            PlayerHull);
        SyncLevel100PlayerState();
        PumpLevel100EventBus();
    }

    private WorldSnapshot CreateSnapshot()
    {
        Level100ActorSnapshot player = _level100Actors.GetActor(_level100PlayerActorId);
        SimVector2 playerPosition = new(
            player.Pose.PositionMillimeters.X,
            player.Pose.PositionMillimeters.Z);
        SimVector2 playerVelocity = new(
            player.Pose.LinearVelocityMillimetersPerTick.X,
            player.Pose.LinearVelocityMillimetersPerTick.Z);
        ProjectileSnapshot[] projectiles = _projectiles
            .OrderBy(projectile => projectile.Id)
            .Select(projectile => new ProjectileSnapshot(
                projectile.Id,
                projectile.Position,
                projectile.Velocity,
                projectile.ElevationMillimeters,
                projectile.VerticalVelocityMillimetersPerTick,
                projectile.RemainingTicks))
            .ToArray();
        WalkerFootContactSnapshot[] walkerFeet = _walkerFeet
            .OrderBy(foot => foot.Id)
            .Select(foot => new WalkerFootContactSnapshot(
                foot.Id,
                foot.Position,
                foot.GroundElevationMillimeters,
                foot.PhaseThirds,
                foot.LiftMillimeters))
            .ToArray();
        return new WorldSnapshot(
            _tick,
            _seed,
            _level100TutorialProgress,
            _mode,
            _transition,
            playerPosition,
            playerVelocity,
            player.Pose.PositionMillimeters.Y,
            player.Pose.LinearVelocityMillimetersPerTick.Y,
            _facingX,
            _facingZ,
            _facingYawMicroRad,
            _walkerYawVelocityMicroRadPerTick,
            _facingPitchMicroRad,
            _walkerPitchVelocityMicroRadPerTick,
            _energy,
            _shield,
            player.Health,
            _transformTicksRemaining,
            _fireCooldownTicksRemaining,
            _level100OpeningTicksRemaining,
            player.Active,
            _level100FlightEnabled,
            _level100PulseCannonEnabled,
            _level100VulcanCannonEnabled,
            _level100MechVulcanCannonEnabled,
            _level100MissilePodEnabled,
            _level100HudEmphasisMask,
            _level100Mission.Snapshot,
            Array.AsReadOnly(_level100MissionEvents.ToArray()),
            _level100Actors.Snapshot,
            _level100Destruction.Snapshot,
            _level100Destruction.Events,
            _level100ActorScripts.Snapshot,
            Array.AsReadOnly(_level100ActorScriptCommands.ToArray()),
            _nextProjectileId,
            Array.AsReadOnly(projectiles),
            Array.AsReadOnly(walkerFeet));
    }

}
