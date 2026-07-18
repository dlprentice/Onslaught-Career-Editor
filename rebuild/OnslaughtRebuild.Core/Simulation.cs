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
    private sbyte _facingX;
    private sbyte _facingZ;
    // Continuous body yaw in milli-radians (0 = +Z). LookX integrates this;
    // discrete Move still snaps facing when LookX is idle.
    private int _facingYawMilliRad;
    private int _energy;
    private int _shield;
    private int _hull;
    private int _transformTicksRemaining;
    private int _fireCooldownTicksRemaining;
    private int _targetsDestroyed;

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

        AdvanceTransition();

        if (_fireCooldownTicksRemaining > 0)
        {
            _fireCooldownTicksRemaining--;
        }

        TryToggleMode(input);
        UpdateMovement(input);
        UpdateResources();
        TryFire(input);
        UpdateProjectiles();

        return CreateSnapshot();
    }

    private void TryToggleMode(SimInput input)
    {
        if (!input.HasAction(SimActions.ToggleMode) ||
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
            return;
        }

        if (input.LookX != 0)
        {
            _facingYawMilliRad += input.LookX * SimulationConstants.WalkerLookYawRateMilliRadPerTick;
            _facingYawMilliRad = NormalizeMilliRad(_facingYawMilliRad);
            QuantizeFacingFromYaw();
        }
        // Walker lateral uses dual-accepted strafe path speed; forward uses walker
        // forward scalar. Jet keeps a single measured jet thrust speed for now.
        int speedX = _mode == VehicleMode.Walker
            ? SimulationConstants.WalkerStrafeSpeedPerTick
            : SimulationConstants.JetSpeedPerTick;
        int speedZ = _mode == VehicleMode.Walker
            ? SimulationConstants.WalkerSpeedPerTick
            : SimulationConstants.JetSpeedPerTick;
        // Movement axes are local to the body. The pinned walker source rotates
        // forward and strafe acceleration by heading; this integer eight-way
        // projection keeps Core deterministic while the motion model remains a
        // deliberately small handling slice.
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

        SimVector2 nextPosition = new(
            Math.Clamp(
                _playerPosition.X + velocityX,
                -SimulationConstants.ArenaHalfExtent,
                SimulationConstants.ArenaHalfExtent),
            Math.Clamp(
                _playerPosition.Z + velocityZ,
                -SimulationConstants.ArenaHalfExtent,
                SimulationConstants.ArenaHalfExtent));
        _playerVelocity = new SimVector2(
            nextPosition.X - _playerPosition.X,
            nextPosition.Z - _playerPosition.Z);
        _playerPosition = nextPosition;
    }

    /// <summary>
    /// Full turn ≈ 2π rad ≈ 6283 milli-rad. Keeps yaw in (−half, half].
    /// </summary>
    private const int TwoPiMilliRad = 6283;

    private static int NormalizeMilliRad(int milliRad)
    {
        int wrapped = milliRad % TwoPiMilliRad;
        if (wrapped > TwoPiMilliRad / 2)
        {
            wrapped -= TwoPiMilliRad;
        }
        else if (wrapped <= -(TwoPiMilliRad / 2))
        {
            wrapped += TwoPiMilliRad;
        }

        return wrapped;
    }

    private void QuantizeFacingFromYaw()
    {
        // Eight-way snap from continuous yaw for FacingX/Z and fire aim.
        int yaw = NormalizeMilliRad(_facingYawMilliRad);
        int sector = ((yaw + TwoPiMilliRad) % TwoPiMilliRad) * 8 / TwoPiMilliRad;
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
            _transformTicksRemaining != 0 ||
            _fireCooldownTicksRemaining != 0 ||
            _energy < SimulationConstants.FireEnergyCost)
        {
            return;
        }

        int velocityX = _facingX * SimulationConstants.ProjectileSpeedPerTick;
        int velocityZ = _facingZ * SimulationConstants.ProjectileSpeedPerTick;
        if (_facingX != 0 && _facingZ != 0)
        {
            velocityX = velocityX * 181 / 256;
            velocityZ = velocityZ * 181 / 256;
        }

        if (velocityX == 0 && velocityZ == 0)
        {
            velocityZ = SimulationConstants.ProjectileSpeedPerTick;
        }

        _energy -= SimulationConstants.FireEnergyCost;
        _fireCooldownTicksRemaining = SimulationConstants.FireCooldownTicks;
        _projectiles.Add(new MutableProjectile
        {
            Id = _nextProjectileId++,
            Position = _playerPosition,
            Velocity = new SimVector2(velocityX, velocityZ),
            RemainingTicks = SimulationConstants.ProjectileLifetimeTicks,
        });
    }

    private void UpdateProjectiles()
    {
        long hitRadiusSquared =
            (long)SimulationConstants.TargetHitRadius * SimulationConstants.TargetHitRadius;

        for (int projectileIndex = _projectiles.Count - 1; projectileIndex >= 0; projectileIndex--)
        {
            MutableProjectile projectile = _projectiles[projectileIndex];
            projectile.Position = new SimVector2(
                projectile.Position.X + projectile.Velocity.X,
                projectile.Position.Z + projectile.Velocity.Z);
            projectile.RemainingTicks--;

            bool hit = false;
            foreach (MutableTarget target in _targets)
            {
                if (!target.IsActive)
                {
                    continue;
                }

                long deltaX = (long)projectile.Position.X - target.Position.X;
                long deltaZ = (long)projectile.Position.Z - target.Position.Z;
                if ((deltaX * deltaX) + (deltaZ * deltaZ) > hitRadiusSquared)
                {
                    continue;
                }

                target.Hull = Math.Max(0, target.Hull - SimulationConstants.ProjectileDamage);
                if (target.Hull == 0)
                {
                    target.IsActive = false;
                    _targetsDestroyed++;
                }

                hit = true;
                break;
            }

            if (hit ||
                projectile.RemainingTicks <= 0 ||
                Math.Abs(projectile.Position.X) > SimulationConstants.ArenaHalfExtent + 5_000 ||
                Math.Abs(projectile.Position.Z) > SimulationConstants.ArenaHalfExtent + 5_000)
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
        _playerPosition = SimVector2.Zero;
        _playerVelocity = SimVector2.Zero;
        _facingX = 0;
        _facingZ = 1;
        _facingYawMilliRad = 0;
        _energy = SimulationConstants.MaximumEnergy;
        _shield = SimulationConstants.MaximumShield;
        _hull = SimulationConstants.MaximumHull;
        _transformTicksRemaining = 0;
        _fireCooldownTicksRemaining = 0;
        _targetsDestroyed = 0;
        _projectiles.Clear();
        BuildTargets();
    }

    private void BuildTargets()
    {
        var random = new DeterministicRandom(_seed);
        _targets.Clear();
        _targets.Add(CreateTarget(1, 0, 14_000));
        _targets.Add(CreateTarget(
            2,
            16_000 + random.NextRange(-1_500, 1_501),
            -8_000 + random.NextRange(-1_500, 1_501)));
        _targets.Add(CreateTarget(
            3,
            -18_000 + random.NextRange(-1_500, 1_501),
            -12_000 + random.NextRange(-1_500, 1_501)));
    }

    private static MutableTarget CreateTarget(int id, int x, int z)
    {
        return new MutableTarget
        {
            Id = id,
            Position = new SimVector2(x, z),
            Hull = SimulationConstants.TargetHull,
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
                projectile.RemainingTicks))
            .ToArray();

        return new WorldSnapshot(
            _tick,
            _seed,
            _mode,
            _transition,
            _playerPosition,
            _playerVelocity,
            _facingX,
            _facingZ,
            _facingYawMilliRad,
            _energy,
            _shield,
            _hull,
            _transformTicksRemaining,
            _fireCooldownTicksRemaining,
            _nextProjectileId,
            _targetsDestroyed,
            Array.AsReadOnly(targets),
            Array.AsReadOnly(projectiles));
    }

    private sealed class DeterministicRandom
    {
        private uint _state;

        public DeterministicRandom(uint seed)
        {
            _state = seed;
        }

        public int NextRange(int minimumInclusive, int maximumExclusive)
        {
            if (minimumInclusive >= maximumExclusive)
            {
                throw new ArgumentOutOfRangeException(nameof(maximumExclusive));
            }

            uint width = (uint)(maximumExclusive - minimumInclusive);
            return minimumInclusive + (int)(NextUInt32() % width);
        }

        private uint NextUInt32()
        {
            uint value = _state;
            value ^= value << 13;
            value ^= value >> 17;
            value ^= value << 5;
            _state = value;
            return value;
        }
    }
}
