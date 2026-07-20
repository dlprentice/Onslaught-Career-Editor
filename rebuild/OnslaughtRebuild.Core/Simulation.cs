// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public sealed class Simulation
{
    private sealed class MutableTarget
    {
        public required int Id { get; init; }
        public required SimVector2 Position { get; init; }
        public int Hull { get; set; }
        public bool IsActive { get; set; }
    }

    private sealed class MutableProjectile
    {
        public required int Id { get; init; }
        public SimVector2 Position { get; set; }
        public required SimVector2 Velocity { get; init; }
        public int ElevationMillimeters { get; set; }
        public required int VerticalVelocityMillimetersPerTick { get; init; }
        public int RemainingTicks { get; set; }
    }

    private readonly uint _seed;
    private readonly List<MutableTarget> _targets = [];
    private readonly List<MutableProjectile> _projectiles = [];
    private int _tick;
    private int _nextProjectileId;
    private VehicleMode _mode;
    private VehicleTransition _transition;
    private SimVector2 _playerPosition;
    private SimVector2 _playerVelocity;
    private int _playerGroundElevationMillimeters;
    private sbyte _facingX;
    private sbyte _facingZ;
    // Continuous body yaw (0 = +Z) and its retail-observed inertial step.
    private int _facingYawMicroRad;
    private int _walkerYawVelocityMicroRadPerTick;
    private int _facingPitchMicroRad;
    private int _walkerPitchVelocityMicroRadPerTick;
    private int _energy;
    private int _shield;
    private int _hull;
    private int _transformTicksRemaining;
    private int _fireCooldownTicksRemaining;
    private int _level100OpeningTicksRemaining;
    private int _level100TimelineTick;
    private Level100TutorialMessage _level100Message;
    private int _level100EventMessageTicksRemaining;
    private bool _level100PowerEnabled;
    private bool _level100FlightEnabled;
    private bool _level100PulseCannonEnabled;
    private bool _level100VulcanCannonEnabled;
    private Level100OpeningPhase _level100Phase;
    private int _level100DispatchTicksRemaining;
    private int _level100FiringRangeSequenceTick;
    private int _level100FiringRangeHandoffTick;
    private int _targetsDestroyed;

    // Jet handling remains provisional and outside this walker milestone.
    private const int ProvisionalJetLookYawRateMicroRadPerTick = 3_000;

    public Simulation(uint seed)
    {
        if (seed == 0)
        {
            throw new ArgumentOutOfRangeException(nameof(seed), "Seed must be nonzero.");
        }

        _seed = seed;
        ResetDynamicState();
    }

    public WorldSnapshot Snapshot => CreateSnapshot();

    public WorldSnapshot Step(SimInput input)
    {
        input.Validate();
        _tick++;

        if (input.HasAction(SimActions.Reset))
        {
            ResetDynamicState();
            return CreateSnapshot();
        }

        AdvanceLevel100EventMessage();
        AdvanceLevel100FiringRangeSequence();
        AdvanceLevel100FiringRangeHandoff();

        SimInput playerInput = _level100PowerEnabled ? input : SimInput.Idle;

        AdvanceTransition();

        if (_fireCooldownTicksRemaining > 0)
        {
            _fireCooldownTicksRemaining--;
        }

        TryToggleMode(playerInput);
        UpdateMovement(playerInput);
        UpdateLevel100Opening();
        UpdateResources();
        TryFire(playerInput);
        UpdateProjectiles();
        AdvanceLevel100Timeline();

        return CreateSnapshot();
    }

    private void AdvanceLevel100Timeline()
    {
        if (_level100OpeningTicksRemaining > 0)
        {
            _level100OpeningTicksRemaining--;
        }

        _level100TimelineTick++;
        if (_level100TimelineTick == SimulationConstants.Level100PowerActivationTick)
        {
            _level100PowerEnabled = true;
        }
        if (_level100EventMessageTicksRemaining == 0 &&
            _level100FiringRangeSequenceTick < 0)
        {
            _level100Message = MessageAtLevel100Tick(_level100TimelineTick);
        }
        if (_level100Phase == Level100OpeningPhase.Briefing &&
            _level100TimelineTick >= SimulationConstants.Level100TargetZone1ActivationTick)
        {
            _level100Phase = Level100OpeningPhase.ReachTargetZone1;
        }
    }

    private static Level100TutorialMessage MessageAtLevel100Tick(int tick) => tick switch
    {
        >= SimulationConstants.Level100Hud01StartTick and
            < SimulationConstants.Level100Hud01EndTick =>
                Level100TutorialMessage.HudIntroduction,
        >= SimulationConstants.Level100Hud02StartTick and
            < SimulationConstants.Level100Hud02EndTick =>
                Level100TutorialMessage.ThreatCircle,
        >= SimulationConstants.Level100Hud06StartTick and
            < SimulationConstants.Level100Hud06EndTick =>
                Level100TutorialMessage.Scanner,
        >= SimulationConstants.Level100MessageLogStartTick and
            < SimulationConstants.Level100MessageLogEndTick =>
                Level100TutorialMessage.MessageLog,
        >= SimulationConstants.Level100TechnicianStartTick and
            < SimulationConstants.Level100TechnicianEndTick =>
                Level100TutorialMessage.TechnicianStatus,
        >= SimulationConstants.Level100MovementInstructionStartTick and
            < SimulationConstants.Level100MovementInstructionEndTick =>
                Level100TutorialMessage.MovementControls,
        >= SimulationConstants.Level100TargetZone1InstructionStartTick and
            < SimulationConstants.Level100TargetZone1InstructionEndTick =>
                Level100TutorialMessage.ReachTargetZone1,
        >= SimulationConstants.Level100ScannerInstructionStartTick and
            < SimulationConstants.Level100ScannerInstructionEndTick =>
                Level100TutorialMessage.ScannerObjective,
        _ => Level100TutorialMessage.None,
    };

    private void AdvanceLevel100EventMessage()
    {
        if (_level100EventMessageTicksRemaining == 0)
        {
            return;
        }

        _level100EventMessageTicksRemaining--;
        if (_level100EventMessageTicksRemaining == 0)
        {
            _level100Message = Level100TutorialMessage.None;
        }
    }

    private void AdvanceLevel100FiringRangeSequence()
    {
        if (_level100FiringRangeSequenceTick < 0 ||
            _level100FiringRangeSequenceTick >=
                SimulationConstants.Level100PulseCannonEnergyEndTick)
        {
            return;
        }

        _level100FiringRangeSequenceTick++;
        _level100Message = MessageAtFiringRangeTick(_level100FiringRangeSequenceTick);
        if (_level100FiringRangeSequenceTick ==
            SimulationConstants.Level100PulseCannonActivationTick)
        {
            _level100PowerEnabled = true;
            _level100PulseCannonEnabled = true;
            _level100Phase = Level100OpeningPhase.FiringRangeExercise;
        }
    }

    private static Level100TutorialMessage MessageAtFiringRangeTick(int tick) => tick switch
    {
        >= SimulationConstants.Level100WeaponSystemsStartTick and
            < SimulationConstants.Level100WeaponSystemsEndTick =>
                Level100TutorialMessage.WeaponSystems,
        >= SimulationConstants.Level100WeaponIndicatorStartTick and
            < SimulationConstants.Level100WeaponIndicatorEndTick =>
                Level100TutorialMessage.WeaponIndicator,
        >= SimulationConstants.Level100PulseCannonStartTick and
            < SimulationConstants.Level100PulseCannonEndTick =>
                Level100TutorialMessage.PulseCannon,
        >= SimulationConstants.Level100OpenFireStartTick and
            < SimulationConstants.Level100OpenFireEndTick =>
                Level100TutorialMessage.OpenFire,
        >= SimulationConstants.Level100PulseCannonEnergyStartTick and
            < SimulationConstants.Level100PulseCannonEnergyEndTick =>
                Level100TutorialMessage.PulseCannonEnergy,
        _ => Level100TutorialMessage.None,
    };

    private void AdvanceLevel100FiringRangeHandoff()
    {
        if (_level100FiringRangeHandoffTick < 0 ||
            _level100FiringRangeHandoffTick >=
                SimulationConstants.Level100VulcanCannonAmmoEndTick)
        {
            return;
        }

        _level100FiringRangeHandoffTick++;
        _level100Message = MessageAtFiringRangeHandoffTick(
            _level100FiringRangeHandoffTick);
        if (_level100FiringRangeHandoffTick ==
            SimulationConstants.Level100VulcanActivationTick)
        {
            _level100PowerEnabled = true;
            _level100PulseCannonEnabled = false;
            _level100VulcanCannonEnabled = true;
            _level100Phase = Level100OpeningPhase.FiringRangeVulcanExercise;
        }
    }

    private static Level100TutorialMessage MessageAtFiringRangeHandoffTick(int tick) =>
        tick switch
    {
        >= SimulationConstants.Level100VulcanCannonStartTick and
            < SimulationConstants.Level100VulcanCannonEndTick =>
                Level100TutorialMessage.VulcanCannon,
        >= SimulationConstants.Level100OpenFireVulcanStartTick and
            < SimulationConstants.Level100OpenFireVulcanEndTick =>
                Level100TutorialMessage.OpenFireVulcan,
        >= SimulationConstants.Level100VulcanCannonAmmoStartTick and
            < SimulationConstants.Level100VulcanCannonAmmoEndTick =>
                Level100TutorialMessage.VulcanCannonAmmo,
        _ => Level100TutorialMessage.None,
    };

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
        if (_transformTicksRemaining != 0)
        {
            _playerVelocity = SimVector2.Zero;
            _walkerYawVelocityMicroRadPerTick = 0;
            _walkerPitchVelocityMicroRadPerTick = 0;
            return;
        }

        if (_mode == VehicleMode.Walker)
        {
            UpdateWalkerYaw(input.LookX);
            UpdateWalkerPitch(input.LookY);
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

    private void UpdateWalkerYaw(sbyte lookX)
    {
        _walkerYawVelocityMicroRadPerTick =
            (int)((long)_walkerYawVelocityMicroRadPerTick *
                SimulationConstants.WalkerYawRetentionNumerator /
                SimulationConstants.WalkerYawRetentionDenominator) +
            (lookX * SimulationConstants.WalkerYawInputMicroRadPerTick);
        _facingYawMicroRad = NormalizeMicroRad(
            _facingYawMicroRad + _walkerYawVelocityMicroRadPerTick);
        QuantizeFacingFromYaw();
    }

    private void UpdateWalkerPitch(sbyte lookY)
    {
        _walkerPitchVelocityMicroRadPerTick =
            (int)((long)_walkerPitchVelocityMicroRadPerTick *
                SimulationConstants.WalkerPitchRetentionNumerator /
                SimulationConstants.WalkerPitchRetentionDenominator) +
            (lookY * SimulationConstants.WalkerPitchInputMicroRadPerTick);

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

    private void UpdateWalkerMovement(SimInput input)
    {
        SimVector2 acceleration = ProjectWalkerInput(
            input,
            SimulationConstants.WalkerAccelerationPerTick);
        var velocity = new SimVector2(
            RetainWalkerVelocity(_playerVelocity.X) + acceleration.X,
            RetainWalkerVelocity(_playerVelocity.Z) + acceleration.Z);
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
        SimVector2 nextPosition = new(
            _playerPosition.X + velocity.X,
            _playerPosition.Z + velocity.Z);
        nextPosition = ResolveLevel100WalkerContact(
            _playerPosition,
            nextPosition,
            SimulationConstants.Level100ControlTowerPosition,
            SimulationConstants.Level100ControlTowerContactRadius);
        nextPosition = ResolveLevel100WalkerContact(
            _playerPosition,
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
        SimVector2 nextPosition = new(
            _playerPosition.X + velocity.X,
            _playerPosition.Z + velocity.Z);
        CommitPlayerPosition(nextPosition);
    }

    private void CommitPlayerPosition(SimVector2 nextPosition)
    {
        _playerVelocity = new SimVector2(
            nextPosition.X - _playerPosition.X,
            nextPosition.Z - _playerPosition.Z);
        _playerPosition = nextPosition;
        _playerGroundElevationMillimeters =
            Level100Terrain.Instance.SampleGroundElevationMillimeters(_playerPosition);
    }

    private void UpdateLevel100Opening()
    {
        if (_level100DispatchTicksRemaining > 0)
        {
            _level100DispatchTicksRemaining--;
            if (_level100DispatchTicksRemaining == 0)
            {
                if (_level100Phase == Level100OpeningPhase.TargetZone1DispatchPending)
                {
                    _level100Phase = Level100OpeningPhase.ReachFiringRange;
                    _level100Message = Level100TutorialMessage.FiringRangeInstruction;
                    _level100EventMessageTicksRemaining =
                        SimulationConstants.Level100FiringRangeInstructionTicks;
                }
                else if (_level100Phase == Level100OpeningPhase.FiringRangeDispatchPending)
                {
                    _level100Phase = Level100OpeningPhase.FiringRangeBriefing;
                    _level100FiringRangeSequenceTick = 0;
                    _level100EventMessageTicksRemaining = 0;
                    _level100Message = Level100TutorialMessage.WeaponSystems;
                    _level100PowerEnabled = false;
                    _level100PulseCannonEnabled = false;
                }
            }

            return;
        }

        SimVector2? trigger = _level100Phase switch
        {
            Level100OpeningPhase.ReachTargetZone1 =>
                SimulationConstants.Level100TargetZone1Position,
            Level100OpeningPhase.ReachFiringRange =>
                SimulationConstants.Level100FiringRangePosition,
            _ => null,
        };
        if (!trigger.HasValue || !IsWithinLevel100Trigger(_playerPosition, trigger.Value))
        {
            return;
        }

        _level100Phase = _level100Phase == Level100OpeningPhase.ReachTargetZone1
            ? Level100OpeningPhase.TargetZone1DispatchPending
            : Level100OpeningPhase.FiringRangeDispatchPending;
        _level100DispatchTicksRemaining = _level100Phase == Level100OpeningPhase.TargetZone1DispatchPending
            ? SimulationConstants.Level100TargetZone1DispatchTicks
            : SimulationConstants.Level100FiringRangeDispatchTicks;
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
        _projectiles.Add(new MutableProjectile
        {
            Id = _nextProjectileId++,
            Position = new SimVector2(
                _playerPosition.X + emitterOffsetX,
                _playerPosition.Z + emitterOffsetZ),
            Velocity = new SimVector2(velocityX, velocityZ),
            ElevationMillimeters = _playerGroundElevationMillimeters +
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
            projectile.Position = new SimVector2(
                projectile.Position.X + projectile.Velocity.X,
                projectile.Position.Z + projectile.Velocity.Z);
            projectile.ElevationMillimeters += projectile.VerticalVelocityMillimetersPerTick;
            projectile.RemainingTicks--;

            bool hit = false;
            foreach (MutableTarget target in _targets)
            {
                if (_level100FiringRangeSequenceTick <
                        SimulationConstants.Level100StaticTargetsActivationTick ||
                    target.Id is < 1 or > 4 ||
                    !target.IsActive ||
                    projectile.VerticalVelocityMillimetersPerTick != 0)
                {
                    continue;
                }

                long deltaX = (long)projectile.Position.X - target.Position.X;
                long deltaZ = (long)projectile.Position.Z - target.Position.Z;
                int hitRadius = target.Id == 4
                    ? SimulationConstants.Level100TargetWarehouseHorizontalBound
                    : SimulationConstants.Level100TargetTankHitRadius;
                long hitRadiusSquared = (long)hitRadius * hitRadius;
                if ((deltaX * deltaX) + (deltaZ * deltaZ) > hitRadiusSquared)
                {
                    continue;
                }

                target.Hull = Math.Max(
                    0,
                    target.Hull - SimulationConstants.Level100PulseCannonFullHitDamage);
                if (target.Hull == 0)
                {
                    target.IsActive = false;
                    _targetsDestroyed++;
                    if (_level100FiringRangeHandoffTick < 0 &&
                        _targets
                            .Where(item => item.Id is >= 1 and <= 4)
                            .All(item => !item.IsActive))
                    {
                        BeginLevel100VulcanHandoff();
                    }
                }

                hit = true;
                break;
            }

            if (hit || projectile.RemainingTicks <= 0)
            {
                _projectiles.RemoveAt(projectileIndex);
            }
        }
    }

    private void BeginLevel100VulcanHandoff()
    {
        _level100FiringRangeHandoffTick = 0;
        _level100Phase = Level100OpeningPhase.FiringRangeVulcanBriefing;
        _level100PowerEnabled = false;
        _level100Message = Level100TutorialMessage.None;
    }

    private void ResetDynamicState()
    {
        _nextProjectileId = 1;
        _mode = VehicleMode.Walker;
        _transition = VehicleTransition.None;
        _playerPosition = SimVector2.Zero;
        _playerVelocity = SimVector2.Zero;
        _playerGroundElevationMillimeters =
            Level100Terrain.Instance.SampleGroundElevationMillimeters(_playerPosition);
        _facingYawMicroRad = SimulationConstants.Level100PlayerStartYawMicroRad;
        QuantizeFacingFromYaw();
        _walkerYawVelocityMicroRadPerTick = 0;
        _facingPitchMicroRad = 0;
        _walkerPitchVelocityMicroRadPerTick = 0;
        _energy = SimulationConstants.MaximumEnergy;
        _shield = SimulationConstants.MaximumShield;
        _hull = SimulationConstants.MaximumHull;
        _transformTicksRemaining = 0;
        _fireCooldownTicksRemaining = 0;
        _level100OpeningTicksRemaining = SimulationConstants.Level100OpeningPanTicks;
        _level100TimelineTick = 0;
        _level100Message = Level100TutorialMessage.None;
        _level100EventMessageTicksRemaining = 0;
        _level100PowerEnabled = false;
        _level100FlightEnabled = false;
        _level100PulseCannonEnabled = false;
        _level100VulcanCannonEnabled = false;
        _level100Phase = Level100OpeningPhase.Briefing;
        _level100DispatchTicksRemaining = 0;
        _level100FiringRangeSequenceTick = -1;
        _level100FiringRangeHandoffTick = -1;
        _targetsDestroyed = 0;
        _projectiles.Clear();
        BuildTargets();
    }

    private void BuildTargets()
    {
        _targets.Clear();
        _targets.Add(CreateTarget(
            1,
            SimulationConstants.Level100TargetTank1Position,
            SimulationConstants.Level100TargetTankLife));
        _targets.Add(CreateTarget(
            2,
            SimulationConstants.Level100TargetTank2Position,
            SimulationConstants.Level100TargetTankLife));
        _targets.Add(CreateTarget(
            3,
            SimulationConstants.Level100TargetTank3Position,
            SimulationConstants.Level100TargetTankLife));
        _targets.Add(CreateTarget(
            4,
            SimulationConstants.Level100TargetWarehousePosition,
            SimulationConstants.Level100TargetWarehouseCenterAimDamageEnvelope));
    }

    private static MutableTarget CreateTarget(int id, SimVector2 position, int initialHull)
    {
        return new MutableTarget
        {
            Id = id,
            Position = position,
            Hull = initialHull,
            IsActive = true,
        };
    }

    private WorldSnapshot CreateSnapshot()
    {
        TargetSnapshot[] targets = _targets
            .OrderBy(target => target.Id)
            .Select(target => new TargetSnapshot(
                target.Id,
                target.Position,
                target.Hull,
                target.IsActive))
            .ToArray();
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

        return new WorldSnapshot(
            _tick,
            _seed,
            _mode,
            _transition,
            _playerPosition,
            _playerVelocity,
            _playerGroundElevationMillimeters,
            _facingX,
            _facingZ,
            _facingYawMicroRad,
            _walkerYawVelocityMicroRadPerTick,
            _facingPitchMicroRad,
            _walkerPitchVelocityMicroRadPerTick,
            _energy,
            _shield,
            _hull,
            _transformTicksRemaining,
            _fireCooldownTicksRemaining,
            _level100OpeningTicksRemaining,
            _level100TimelineTick,
            _level100Message,
            _level100EventMessageTicksRemaining,
            _level100PowerEnabled,
            _level100FlightEnabled,
            _level100PulseCannonEnabled,
            _level100VulcanCannonEnabled,
            _level100Phase,
            _level100DispatchTicksRemaining,
            _level100FiringRangeSequenceTick,
            _level100FiringRangeHandoffTick,
            _nextProjectileId,
            _targetsDestroyed,
            Array.AsReadOnly(targets),
            Array.AsReadOnly(projectiles));
    }

}
