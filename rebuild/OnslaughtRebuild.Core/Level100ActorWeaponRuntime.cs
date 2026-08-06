// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// Actor-owned weapons and rounds, on the released 20 Hz base tick.
///
/// <para><b>Provenance.</b> Every law here is read out of the pristine
/// BEA.exe (sha256 <c>74154bfa...7750</c>) through the 2026-07-23 Ghidra full
/// pass, and every scalar is a dword out of <c>data/default physics.dat</c>
/// (sha256 <c>e1fb3ded...ada14</c>) or a shipped record default. The four
/// bodies that own the behaviour are:</para>
/// <list type="bullet">
///   <item><c>ProjectileBurst__SpawnFromPercentBucketFallback</c>
///     @<c>0x00506010</c> - the reload gate and burst start.</item>
///   <item><c>CWeapon__HandleFireBurstEvent</c> @<c>0x00506930</c> - the
///     burst continuation.</item>
///   <item><c>ProjectileBurst__SpawnFromCurrentPreset</c> @<c>0x005069f0</c> -
///     the per-projectile inaccuracy scatter.</item>
///   <item>round vtable slot 66 @<c>0x004d8e40</c> - wiggle, the seek gate and
///     the homing law.</item>
/// </list>
/// <para>The firing gate is
/// <c>CUnit__ClassifyTargetRangeBand</c> @<c>0x004fb670</c> plus
/// <c>OID__CanFireAtTarget_BallisticArcA</c> @<c>0x00507ab0</c>.</para>
///
/// <para><b>Not modelled, and why.</b> The target-height window
/// (<c>CWeaponMinTargetHeight</c>/<c>MaxTargetHeight</c>) is unconditional
/// under the shipped defaults for both drone weapons, so it is omitted rather
/// than invented. The line-of-sight trace through
/// <c>CWorld__FindFirstThingToHitLine</c> runs only when the caller supplies a
/// trace context, and which callers do is unread; it is omitted. Muzzle
/// offsets are omitted because neither drone weapon mode carries a
/// <c>CWeaponLaunchSequence</c> node. <c>CWeaponTrack</c> is absent from both
/// modes (shipped default 0), so rounds launch along the actor's own facing
/// and not along the line to the target - which is precisely what makes
/// <c>CWeaponYawTolerance</c> load-bearing.</para>
/// </summary>
public sealed partial class Level100ActorMechanics
{
    private sealed class ActorWeaponState
    {
        internal required Level100ActorId ActorId { get; init; }
        internal required Level100ActorWeaponKind Weapon { get; init; }
        internal int ReloadBaseTicksRemaining { get; set; }
        internal int BurstShotsRemaining { get; set; }
        internal int BurstDelayBaseTicksRemaining { get; set; }
    }

    private sealed class ActorRoundState
    {
        internal required int Id { get; init; }
        internal required Level100ActorId OwnerActorId { get; init; }
        internal required Level100ActorId TargetActorId { get; init; }
        internal required Level100ActorRoundKind Kind { get; init; }
        internal SimVector3 PositionMillimeters { get; set; }
        internal int YawMicroRadians { get; set; }
        internal int PitchMicroRadians { get; set; }
        internal int RemainingBaseTicks { get; set; }
        internal int ElapsedBaseTicks { get; set; }
        internal bool Locked { get; set; }
    }

    private readonly List<ActorWeaponState> _actorWeapons = [];
    private readonly List<ActorRoundState> _actorRounds = [];
    private readonly List<Level100ActorRoundImpact> _actorRoundImpacts = [];
    private Level100ReleasedRandom _releasedRandom = new();
    private int _nextActorRoundId = 1;

    /// <summary>
    /// Released actor rounds that reached their designated target since the
    /// last drain. The caller owns applying the damage, because the player's
    /// hull is not owned by this class.
    /// </summary>
    public IReadOnlyList<Level100ActorRoundImpact> DrainActorRoundImpacts()
    {
        if (_actorRoundImpacts.Count == 0)
        {
            return Array.Empty<Level100ActorRoundImpact>();
        }

        Level100ActorRoundImpact[] drained = _actorRoundImpacts.ToArray();
        _actorRoundImpacts.Clear();
        return Array.AsReadOnly(drained);
    }

    private IReadOnlyList<Level100ActorWeaponSnapshot> SnapshotActorWeapons() =>
        Array.AsReadOnly(_actorWeapons
            .OrderBy(weapon => weapon.ActorId.Value)
            .ThenBy(weapon => (int)weapon.Weapon)
            .Select(weapon => new Level100ActorWeaponSnapshot(
                weapon.ActorId,
                weapon.Weapon,
                weapon.ReloadBaseTicksRemaining,
                weapon.BurstShotsRemaining,
                weapon.BurstDelayBaseTicksRemaining))
            .ToArray());

    private IReadOnlyList<Level100ActorRoundSnapshot> SnapshotActorRounds() =>
        Array.AsReadOnly(_actorRounds
            .OrderBy(round => round.Id)
            .Select(round => new Level100ActorRoundSnapshot(
                round.Id,
                round.OwnerActorId,
                round.TargetActorId,
                round.Kind,
                round.PositionMillimeters,
                round.YawMicroRadians,
                round.PitchMicroRadians,
                round.RemainingBaseTicks,
                round.ElapsedBaseTicks,
                round.Locked))
            .ToArray());

    private void RestoreArmament(Level100ActorMechanicsSnapshot snapshot)
    {
        if (snapshot.NextActorRoundId < 1)
        {
            throw new ArgumentException(
                "Level 100 actor mechanics snapshot has an invalid round id.",
                nameof(snapshot));
        }

        _releasedRandom = new Level100ReleasedRandom(snapshot.ReleasedRandomSeed);
        _nextActorRoundId = snapshot.NextActorRoundId;
        _actorWeapons.Clear();
        foreach (Level100ActorWeaponSnapshot weapon in snapshot.ActorWeapons)
        {
            ArgumentNullException.ThrowIfNull(weapon);
            _actorWeapons.Add(new ActorWeaponState
            {
                ActorId = weapon.ActorId,
                Weapon = weapon.Weapon,
                ReloadBaseTicksRemaining = weapon.ReloadBaseTicksRemaining,
                BurstShotsRemaining = weapon.BurstShotsRemaining,
                BurstDelayBaseTicksRemaining = weapon.BurstDelayBaseTicksRemaining,
            });
        }

        _actorRounds.Clear();
        foreach (Level100ActorRoundSnapshot round in snapshot.ActorRounds)
        {
            ArgumentNullException.ThrowIfNull(round);
            _actorRounds.Add(new ActorRoundState
            {
                Id = round.Id,
                OwnerActorId = round.OwnerActorId,
                TargetActorId = round.TargetActorId,
                Kind = round.Kind,
                PositionMillimeters = round.PositionMillimeters,
                YawMicroRadians = round.YawMicroRadians,
                PitchMicroRadians = round.PitchMicroRadians,
                RemainingBaseTicks = round.RemainingBaseTicks,
                ElapsedBaseTicks = round.ElapsedBaseTicks,
                Locked = round.Locked,
            });
        }
    }

    /// <summary>
    /// Arms an actor's released weapon slots when it is first told to attack.
    /// The slot list is exactly the <c>CUnitUse</c> statements on the shipped
    /// <c>Unit</c> record.
    /// </summary>
    private void ArmActorWeapons(ActorState state)
    {
        Level100ActorSnapshot actor = _actors.GetActor(state.ActorId);
        if (actor.DefinitionName is null)
        {
            return;
        }

        foreach (Level100ActorWeaponKind kind in
                 Level100ActorArmament.Slots(actor.DefinitionName))
        {
            if (_actorWeapons.Any(weapon =>
                    weapon.ActorId == state.ActorId && weapon.Weapon == kind))
            {
                continue;
            }

            _actorWeapons.Add(new ActorWeaponState
            {
                ActorId = state.ActorId,
                Weapon = kind,
            });
        }
    }

    // ------------------------------------------------------------------
    // Weapons
    // ------------------------------------------------------------------

    private void AdvanceActorWeapons()
    {
        if (_actorWeapons.Count == 0)
        {
            return;
        }

        for (int index = _actorWeapons.Count - 1; index >= 0; index--)
        {
            ActorWeaponState weapon = _actorWeapons[index];
            if (weapon.ReloadBaseTicksRemaining > 0)
            {
                weapon.ReloadBaseTicksRemaining--;
            }
            if (weapon.BurstDelayBaseTicksRemaining > 0)
            {
                weapon.BurstDelayBaseTicksRemaining--;
            }

            if (!_states.TryGetValue(weapon.ActorId.Value, out ActorState? state))
            {
                _actorWeapons.RemoveAt(index);
                continue;
            }

            Level100ActorSnapshot owner = _actors.GetActor(weapon.ActorId);
            if (!owner.Active ||
                owner.Lifecycle != Level100ActorLifecycle.Alive)
            {
                weapon.BurstShotsRemaining = 0;
                continue;
            }

            // AI_OFF silences the unit. The released script command was being
            // parsed and stored and then never read by anything - AiState was
            // written at Level100ActorMechanics, copied into the snapshot and
            // hashed, and NOTHING branched on it. Measured consequence: six
            // drones kept firing after the LevelScript posted its abort, which
            // turns off their AI.
            //
            // AI_OFF is 1, from the released `data\MissionScripts\onsldef.msl`
            // lines 2-6 - authored developer text that the source itself
            // #includes as a header (Career.cpp:11, game.cpp:46):
            //     AI_ON 0, AI_OFF 1, AI_NORMAL 2, AI_DEFENSIVE 3, AI_ONF 4
            // The default is 0, so an actor that was never given an AI state
            // reads as AI_ON and is unaffected by this gate.
            //
            // ONLY AI_OFF is gated here. The sibling defect - SetAllegiance
            // being equally unread - is NOT fixed alongside it, because
            // FRIENDLY_ALLIGENCE is 0 and our Allegiance field also defaults to
            // 0, so a naive "friendly units do not attack" gate would silence
            // every actor in the level. That needs each actor's AUTHORED
            // allegiance established first and is tracked separately.
            if (state.AiState == SimulationConstants.ReleasedAiStateOff)
            {
                weapon.BurstShotsRemaining = 0;
                continue;
            }

            if (state.Intent != Level100ActorCommandIntent.Attacking ||
                state.TargetActorId is not { } targetId)
            {
                weapon.BurstShotsRemaining = 0;
                continue;
            }

            Level100ActorMotionDefinition? motion =
                _definitions.FindMotionDefinition(owner.DefinitionName);
            if (motion?.MotionClass != Level100ActorMotionClass.Plane)
            {
                continue;
            }

            Level100ActorWeaponMode mode = Level100ActorArmament.Mode(weapon.Weapon);

            // Burst continuation: CWeapon__HandleFireBurstEvent @0x00506930
            // spawns while weapon[+0x6c] < mode[+0x44] regardless of the aim
            // gate - only the burst-start path is gated.
            if (weapon.BurstShotsRemaining > 0)
            {
                if (weapon.BurstDelayBaseTicksRemaining == 0)
                {
                    LaunchActorRound(weapon, mode, state, targetId);
                    weapon.BurstShotsRemaining--;
                    weapon.BurstDelayBaseTicksRemaining = mode.BurstDelayBaseTicks;
                }
                continue;
            }

            if (weapon.ReloadBaseTicksRemaining > 0)
            {
                continue;
            }

            if (!CanActorWeaponFire(weapon.ActorId, targetId, mode))
            {
                continue;
            }

            // Burst start: reload is charged from the FIRST shot
            // (`weapon[+0x64] = NOW + mode[+0x38]` before the first spawn).
            weapon.ReloadBaseTicksRemaining = mode.ReloadBaseTicks;
            LaunchActorRound(weapon, mode, state, targetId);
            weapon.BurstShotsRemaining = mode.BurstSize - 1;
            weapon.BurstDelayBaseTicksRemaining = mode.BurstDelayBaseTicks;
        }
    }

    /// <summary>
    /// The released firing gate, reduced to the terms that are not
    /// unconditional for Level 100. See the class remarks for what is omitted.
    /// </summary>
    private bool CanActorWeaponFire(
        Level100ActorId ownerId,
        Level100ActorId targetId,
        Level100ActorWeaponMode mode)
    {
        Level100ActorSnapshot target = _actors.GetActor(targetId);
        if (!target.Active || target.Lifecycle != Level100ActorLifecycle.Alive)
        {
            return false;
        }

        Level100ActorPoseSnapshot ownerPose = _actors.GetPose(ownerId);
        Level100ActorPoseSnapshot targetPose = _actors.GetPose(targetId);
        long deltaX = (long)targetPose.PositionMillimeters.X -
            ownerPose.PositionMillimeters.X;
        long deltaY = (long)targetPose.PositionMillimeters.Y -
            ownerPose.PositionMillimeters.Y;
        long deltaZ = (long)targetPose.PositionMillimeters.Z -
            ownerPose.PositionMillimeters.Z;

        // CUnit__ClassifyTargetRangeBand @0x004fb670: a plain 3D centre
        // distance against CWeaponMinRange / CWeaponMaxRange, because neither
        // drone weapon uses a ballistic arc.
        long distanceSquared =
            (deltaX * deltaX) + (deltaY * deltaY) + (deltaZ * deltaZ);
        long minimum = mode.MinimumRangeMillimeters;
        long maximum = mode.MaximumRangeMillimeters;
        if (distanceSquared < minimum * minimum ||
            distanceSquared > maximum * maximum)
        {
            return false;
        }

        (int ownerYaw, int ownerPitch) = ReadPoseYawPitch(ownerPose);
        long horizontal = IntegerSquareRoot((deltaX * deltaX) + (deltaZ * deltaZ));
        int targetYaw = FixedAtan2(-deltaX, deltaZ);
        int targetPitch = FixedAtan2(deltaY, horizontal);

        // |wrapped yaw error| < CWeaponYawTolerance, strict, at
        // `ABS(fVar2) < mode[+0x84]`.
        int yawError = NormalizeMicroRad(targetYaw - ownerYaw);
        if (Math.Abs(yawError) >= mode.YawToleranceMicroRadians)
        {
            return false;
        }

        // The deflection window. The shipped records carry
        // CWeaponMinDeflection = +pi/4 and CWeaponMaxDeflection = -pi/4, i.e.
        // the two names are the wrong way round, which is what makes the
        // shipped comparisons read as inverted. Net effect: a symmetric window.
        int pitchError = NormalizeMicroRad(targetPitch - ownerPitch);
        return Math.Abs(pitchError) < mode.PitchWindowMicroRadians;
    }

    private void LaunchActorRound(
        ActorWeaponState weapon,
        Level100ActorWeaponMode mode,
        ActorState state,
        Level100ActorId targetId)
    {
        Level100ActorPoseSnapshot ownerPose = _actors.GetPose(weapon.ActorId);

        // The launch direction is the WEAPON's aim transform
        // (`burstContext+0x30`), not the unit's facing.
        // `OID__UpdateAimTransformAndAttachTargetReader` @0x00509140 rebuilds
        // that matrix every update from `-atan2(...)` and `acos(...)` of the
        // vector to the attached target reader, so a weapon that is allowed to
        // fire is already pointing at what it is firing at. The unit's own
        // facing is what CWeaponYawTolerance gates, which is why the two are
        // separate tests. CWeaponTrack (mode +0xac, the branch that instead
        // rebuilds the matrix inside the spawn body) is absent from both drone
        // weapon modes and is not modelled.
        Level100ActorPoseSnapshot aimPose = _actors.GetPose(targetId);
        long aimX = (long)aimPose.PositionMillimeters.X -
            ownerPose.PositionMillimeters.X;
        long aimY = (long)aimPose.PositionMillimeters.Y -
            ownerPose.PositionMillimeters.Y;
        long aimZ = (long)aimPose.PositionMillimeters.Z -
            ownerPose.PositionMillimeters.Z;
        int yaw = FixedAtan2(-aimX, aimZ);
        int pitch = FixedAtan2(
            aimY,
            IntegerSquareRoot((aimX * aimX) + (aimZ * aimZ)));

        // ProjectileBurst__SpawnFromCurrentPreset @0x005069f0 draws exactly two
        // samples per projectile and feeds the second one to the first Euler
        // argument. The draws are taken even when CWeaponInaccuracy is zero in
        // the reconstruction only if the shipped code would take them - it
        // does, unconditionally, so the stream advances by two per projectile
        // regardless of the scatter magnitude.
        int firstSample =
            _releasedRandom.NextSignedUnitScaled(mode.InaccuracyMicroRadians);
        int secondSample =
            _releasedRandom.NextSignedUnitScaled(mode.InaccuracyMicroRadians);

        Level100ActorRoundData round = Level100ActorArmament.Round(mode.Round);
        _actorRounds.Add(new ActorRoundState
        {
            Id = _nextActorRoundId++,
            OwnerActorId = weapon.ActorId,
            TargetActorId = targetId,
            Kind = round.Kind,
            PositionMillimeters = ownerPose.PositionMillimeters,
            YawMicroRadians = NormalizeMicroRad(yaw + secondSample),
            PitchMicroRadians = NormalizeMicroRad(pitch + firstSample),
            RemainingBaseTicks = round.LifeSpanBaseTicks,
            ElapsedBaseTicks = 0,
            Locked = round.Seeks,
        });
        _ = state;
    }

    // ------------------------------------------------------------------
    // Rounds
    // ------------------------------------------------------------------

    private void AdvanceActorRounds()
    {
        if (_actorRounds.Count == 0)
        {
            return;
        }

        for (int index = _actorRounds.Count - 1; index >= 0; index--)
        {
            ActorRoundState round = _actorRounds[index];
            Level100ActorRoundData data = Level100ActorArmament.Round(round.Kind);

            // Seek, before the move: the shipped body runs the guidance block
            // after CActor__Move, so the round travels one tick on its launch
            // heading before homing can act. That is the same ordering as
            // steering here and integrating below, because the steering result
            // is only used by the next integration.
            if (data.Seeks && round.Locked)
            {
                SteerSeekingRound(round, data);
            }

            (int sin, int cos) = FixedSinCos(round.YawMicroRadians);
            (int pitchSin, int pitchCos) = FixedSinCos(round.PitchMicroRadians);

            // CRoundWiggle: two draws with the same [-1,+1) law as the weapon
            // scatter, applied to the travel direction for this integration
            // step only and then undone. Retail composes it as a matrix on the
            // velocity vector; Core composes the identical pair of Euler
            // samples onto the round's own (yaw, pitch), which leaves the
            // round's stored attitude bit-identical either way and differs only
            // within the single step by O(wiggle * pitch).
            int travelYaw = round.YawMicroRadians;
            int travelPitch = round.PitchMicroRadians;
            if (data.WiggleMicroRadians > 0)
            {
                int wiggleFirst =
                    _releasedRandom.NextSignedUnitScaled(data.WiggleMicroRadians);
                int wiggleSecond =
                    _releasedRandom.NextSignedUnitScaled(data.WiggleMicroRadians);
                travelYaw = NormalizeMicroRad(travelYaw + wiggleSecond);
                travelPitch = NormalizeMicroRad(travelPitch + wiggleFirst);
                (sin, cos) = FixedSinCos(travelYaw);
                (pitchSin, pitchCos) = FixedSinCos(travelPitch);
            }

            int speed = data.SpeedMillimetersPerBaseTick;
            var step = new SimVector3(
                DivideRoundNearest(
                    (long)-MultiplyFixed(sin, pitchCos) * speed,
                    FixedTrigScale),
                DivideRoundNearest((long)pitchSin * speed, FixedTrigScale),
                DivideRoundNearest(
                    (long)MultiplyFixed(cos, pitchCos) * speed,
                    FixedTrigScale));

            SimVector3 start = round.PositionMillimeters;
            var end = new SimVector3(
                checked(start.X + step.X),
                checked(start.Y + step.Y),
                checked(start.Z + step.Z));
            round.PositionMillimeters = end;
            round.ElapsedBaseTicks++;
            round.RemainingBaseTicks--;

            if (TryReportActorRoundImpact(round, data, start, end))
            {
                _actorRounds.RemoveAt(index);
                continue;
            }

            // The shipped round collides with the world through
            // CCollisionSeekingRound. The reconstruction models only the
            // terrain half of that: a round below the height field is spent.
            // No damage is produced, which matches a terrain impact.
            if (end.Y <
                    Level100Terrain.Instance.SampleGroundElevationMillimeters(
                        new SimVector2(end.X, end.Z)) ||
                round.RemainingBaseTicks <= 0)
            {
                _actorRounds.RemoveAt(index);
            }
        }
    }

    /// <summary>
    /// The released homing law, round vtable slot 66 @<c>0x004d8e40</c>.
    ///
    /// <para>The gate is <c>CRoundDamage &gt;= 0</c> and
    /// <c>CRoundTurnRate &gt; 0</c> and a bound target and
    /// <c>SeekDelay &lt; age &lt; SeekTerminationTime</c>. Both surviving
    /// Level 100 seekers pass the first two by construction, and
    /// <c>Forseti Missile</c> carries no <c>CRoundSeekTerminationTime</c>, so
    /// the shipped default 1000.0 s (item[0x11] of
    /// <c>CRoundData__CreateAndRegisterByName</c> @<c>0x0042ffa0</c>) never
    /// expires inside its 10 s lifespan and is not represented.</para>
    ///
    /// <para>The direction to the target is taken into the round's own frame;
    /// if its forward component falls below <c>cos(CRoundSeekAngle)</c> the
    /// lock is dropped outright and never re-acquired - <c>CRoundSeek 3</c> is
    /// distinguished from <c>CRoundSeek 1</c> by exactly that, because
    /// <c>== 1</c> in
    /// <c>CRound__SelectBestTargetReaderAndSyncAimState</c> @<c>0x004dac90</c>
    /// is the only self-acquire path in the binary. Nothing in the shipped
    /// image distinguishes 2 from 3.</para>
    ///
    /// <para>The steering is a per-axis clamp to <c>CRoundTurnRate</c> in the
    /// body frame, exactly as the shipped body computes
    /// <c>yawErr = -atan2(localX, localForward)</c> and
    /// <c>pitchErr = atan2(localUpward, hypot(localX, localForward))</c> and
    /// clamps each independently before composing them onto the basis.</para>
    /// </summary>
    private void SteerSeekingRound(
        ActorRoundState round,
        Level100ActorRoundData data)
    {
        if (round.ElapsedBaseTicks <= data.SeekDelayBaseTicks)
        {
            return;
        }

        Level100ActorSnapshot target = _actors.GetActor(round.TargetActorId);
        if (!target.Active || target.Lifecycle != Level100ActorLifecycle.Alive)
        {
            round.Locked = false;
            return;
        }

        Level100ActorPoseSnapshot targetPose = _actors.GetPose(round.TargetActorId);
        long deltaX = (long)targetPose.PositionMillimeters.X -
            round.PositionMillimeters.X;
        long deltaY = (long)targetPose.PositionMillimeters.Y -
            round.PositionMillimeters.Y;
        long deltaZ = (long)targetPose.PositionMillimeters.Z -
            round.PositionMillimeters.Z;
        long length = IntegerSquareRoot(
            (deltaX * deltaX) + (deltaY * deltaY) + (deltaZ * deltaZ));
        if (length == 0)
        {
            return;
        }

        // The round's own frame, from its (yaw, pitch): forward is the third
        // basis column and up is the second, matching BuildPlaneBasis.
        (int yawSin, int yawCos) = FixedSinCos(round.YawMicroRadians);
        (int pitchSin, int pitchCos) = FixedSinCos(round.PitchMicroRadians);
        long rightX = yawCos;
        long rightY = 0;
        long rightZ = yawSin;
        long upX = MultiplyFixed(yawSin, pitchSin);
        long upY = pitchCos;
        long upZ = -MultiplyFixed(yawCos, pitchSin);
        long forwardX = -MultiplyFixed(yawSin, pitchCos);
        long forwardY = pitchSin;
        long forwardZ = MultiplyFixed(yawCos, pitchCos);

        long localRight =
            ((deltaX * rightX) + (deltaY * rightY) + (deltaZ * rightZ)) / length;
        long localUp =
            ((deltaX * upX) + (deltaY * upY) + (deltaZ * upZ)) / length;
        long localForward =
            ((deltaX * forwardX) + (deltaY * forwardY) + (deltaZ * forwardZ)) /
            length;

        (_, int seekCosine) = FixedSinCos(data.SeekAngleMicroRadians);
        if (localForward < seekCosine)
        {
            round.Locked = false;
            return;
        }

        int yawError = FixedAtan2(localRight, localForward);
        int pitchError = FixedAtan2(
            localUp,
            IntegerSquareRoot((localRight * localRight) +
                (localForward * localForward)));
        int cappedYaw = Math.Clamp(
            yawError,
            -data.TurnRateMicroRadians,
            data.TurnRateMicroRadians);
        int cappedPitch = Math.Clamp(
            pitchError,
            -data.TurnRateMicroRadians,
            data.TurnRateMicroRadians);

        // New forward = right*sin(cy)cos(cp) + up*sin(cp) + forward*cos(cy)cos(cp).
        // When neither axis clamps this reproduces the direction to the target
        // exactly, because the two errors were defined by that decomposition.
        (int cySin, int cyCos) = FixedSinCos(cappedYaw);
        (int cpSin, int cpCos) = FixedSinCos(cappedPitch);
        int alongRight = MultiplyFixed(cySin, cpCos);
        int alongForward = MultiplyFixed(cyCos, cpCos);
        int nextX =
            MultiplyFixed((int)rightX, alongRight) +
            MultiplyFixed((int)upX, cpSin) +
            MultiplyFixed((int)forwardX, alongForward);
        int nextY =
            MultiplyFixed((int)rightY, alongRight) +
            MultiplyFixed((int)upY, cpSin) +
            MultiplyFixed((int)forwardY, alongForward);
        int nextZ =
            MultiplyFixed((int)rightZ, alongRight) +
            MultiplyFixed((int)upZ, cpSin) +
            MultiplyFixed((int)forwardZ, alongForward);

        round.YawMicroRadians = FixedAtan2(-nextX, nextZ);
        round.PitchMicroRadians = FixedAtan2(
            nextY,
            IntegerSquareRoot(((long)nextX * nextX) + ((long)nextZ * nextZ)));
    }

    /// <summary>
    /// Point-of-closest-approach test of the round's swept segment against the
    /// designated target's collision sphere. The shipped round has no
    /// <c>CRoundRadius</c> node (default 0), so the whole envelope is the
    /// target's own <c>CThing</c> radius - 0.4 for the single-player battle
    /// engine, the same 0.4 already carried by
    /// <see cref="SimulationConstants.Level100ObjectiveTriggerRadius"/>.
    /// </summary>
    private bool TryReportActorRoundImpact(
        ActorRoundState round,
        Level100ActorRoundData data,
        SimVector3 start,
        SimVector3 end)
    {
        Level100ActorSnapshot target = _actors.GetActor(round.TargetActorId);
        if (!target.Active || target.Lifecycle != Level100ActorLifecycle.Alive)
        {
            return false;
        }

        Level100ActorPoseSnapshot targetPose =
            _actors.GetPose(round.TargetActorId);
        long segmentX = (long)end.X - start.X;
        long segmentY = (long)end.Y - start.Y;
        long segmentZ = (long)end.Z - start.Z;
        long toTargetX = (long)targetPose.PositionMillimeters.X - start.X;
        long toTargetY = (long)targetPose.PositionMillimeters.Y - start.Y;
        long toTargetZ = (long)targetPose.PositionMillimeters.Z - start.Z;
        long segmentLengthSquared =
            (segmentX * segmentX) + (segmentY * segmentY) + (segmentZ * segmentZ);

        long closestX = toTargetX;
        long closestY = toTargetY;
        long closestZ = toTargetZ;
        if (segmentLengthSquared > 0)
        {
            long projection = (toTargetX * segmentX) +
                (toTargetY * segmentY) +
                (toTargetZ * segmentZ);
            if (projection > 0)
            {
                if (projection >= segmentLengthSquared)
                {
                    closestX = toTargetX - segmentX;
                    closestY = toTargetY - segmentY;
                    closestZ = toTargetZ - segmentZ;
                }
                else
                {
                    closestX = toTargetX - (segmentX * projection / segmentLengthSquared);
                    closestY = toTargetY - (segmentY * projection / segmentLengthSquared);
                    closestZ = toTargetZ - (segmentZ * projection / segmentLengthSquared);
                }
            }
        }

        long distanceSquared = (closestX * closestX) +
            (closestY * closestY) +
            (closestZ * closestZ);
        long radius = SimulationConstants.Level100PlayerContactRadiusMillimeters;
        if (distanceSquared > radius * radius)
        {
            return false;
        }

        _actorRoundImpacts.Add(new Level100ActorRoundImpact(
            round.TargetActorId,
            round.OwnerActorId,
            round.Kind,
            data.IncomingDamageMilliLife));
        return true;
    }

    private static (int Yaw, int Pitch) ReadPoseYawPitch(
        Level100ActorPoseSnapshot pose)
    {
        int forwardX = FloatBitsToQ30(pose.BasisFloatBits.Row0Z);
        int forwardY = FloatBitsToQ30(pose.BasisFloatBits.Row1Z);
        int forwardZ = FloatBitsToQ30(pose.BasisFloatBits.Row2Z);
        int horizontal = Q30Hypotenuse(forwardX, forwardZ);
        return (FixedAtan2(-forwardX, forwardZ), FixedAtan2(forwardY, horizontal));
    }

    private static long IntegerSquareRoot(long value)
    {
        if (value <= 0)
        {
            return 0;
        }
        long root = 0;
        long bit = 1L << 62;
        while (bit > value)
        {
            bit >>= 2;
        }
        long remainder = value;
        while (bit != 0)
        {
            if (remainder >= root + bit)
            {
                remainder -= root + bit;
                root = (root >> 1) + bit;
            }
            else
            {
                root >>= 1;
            }
            bit >>= 2;
        }
        return root;
    }
}
