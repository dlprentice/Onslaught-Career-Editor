// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public enum VehicleMode
{
    Walker = 0,
    Jet = 1,
}

public enum VehicleTransition
{
    None = 0,
    WalkerToJet = 1,
    JetToWalker = 2,
}

public enum AquilaJetWeapon : byte
{
    None = 0,
    MechVulcanCannon = 1,
    SpreadPod = 2,
}

[Flags]
public enum AquilaFlightEvents : ushort
{
    None = 0,
    TransformRejected = 1 << 0,
    WalkerToJetStarted = 1 << 1,
    JetToWalkerStarted = 1 << 2,
    TransformCompleted = 1 << 3,
    Touchdown = 1 << 4,
    EnteredWater = 1 << 5,
    WaterSkim = 1 << 6,
    StallStarted = 1 << 7,
    GroundImpactDamageThresholdCrossed = 1 << 8,
    WaterFailureStarted = 1 << 9,
    JetWeaponFireRequested = 1 << 10,
}

public sealed record AquilaFlightEvent(
    int Tick,
    AquilaFlightEvents Kind,
    VehicleMode Mode,
    VehicleTransition Transition,
    AquilaJetWeapon Weapon = AquilaJetWeapon.None);

/// <summary>
/// The player weapon whose release produced a
/// <see cref="Level100WeaponFireEvent"/>. These are the released `weapon`
/// records of the Level 100 configuration, `Aquila Prototype`
/// (data/battle engine configurations.dat record 3 @0x2d2): walker list
/// ["Mech Twin Vulcan Cannon"], mPrimaryWeapon "Pulse Cannon Pod", jet list
/// ["Mech Vulcan Cannon", "Missile Pod"]. The Level 100 LevelScript enables
/// and disables exactly these by name.
/// </summary>
public enum Level100PlayerWeapon : byte
{
    None = 0,

    /// <summary>
    /// `Pulse Cannon Pod` (data/default physics.dat @0x1746b). Charge level 0
    /// selects weapon mode `Mech Pulse Cannon Charged` (@0x134eb), whose
    /// CWeaponRound is `Mech Pulse Bolt Medium` and whose CWeaponLaunchSound is
    /// `BE Pulse Cannon Fire` (payload @0x13576) = sounds.sfx record 37.
    /// This is the weapon the released firing-range exercise enables
    /// (LevelScript.msl line 112).
    /// </summary>
    PulseCannonPod = 1,

    /// <summary>
    /// `Mech Twin Vulcan Cannon`. Its weapon mode (@0x13368) carries
    /// CWeaponVolleySize 4 and CWeaponLaunchSound `BE Vulcan Cannon`
    /// (payload @0x133fe) = sounds.sfx record 42.
    /// </summary>
    MechTwinVulcanCannon = 2,

    /// <summary>
    /// The jet-mode `Mech Vulcan Cannon`. Its weapon mode (@0x1327d) carries
    /// CWeaponVolleySize 2 and names the same `BE Vulcan Cannon` launch sound
    /// (payload @0x13303) as the walker Twin Vulcan.
    /// </summary>
    MechVulcanCannon = 3,
}

/// <summary>
/// One released weapon RELEASE by the player - a single launch instant, not a
/// single round.
///
/// <para><b>The cadence is byte-proven, not chosen.</b> In the pristine
/// specimen (local-lab/safe-copy-bea-pristine/BEA.exe.original.backup, sha256
/// 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750 - NOT the
/// installed executable, which is patched) the launch body
/// `ProjectileBurst__SpawnFromCurrentPreset` at 0x005069f0 issues exactly one
/// `CSoundManager::PlayEffect` before it enters the spawn loop:</para>
/// <code>
/// 0x00506a91  b9 88 69 89 00           MOV  ECX, 0x00896988   ; CSoundManager
/// 0x00506a96  e8 a5 ae fd ff           CALL 0x004e1940        ; PlayEffect
/// 0x00506a9b  8b 43 48                 MOV  EAX,[EBX+0x48]    ; CWeaponVolleySize
/// 0x00506aa2  3b c7                    CMP  EAX,EDI
/// 0x00506aa4  0f 8e e7 0d 00 00        JLE  0x00507891        ; skip empty volley
/// 0x00506aaa  ...                                             ; LOOP HEAD
/// 0x0050788b  0f 8c 19 f2 ff ff        JL   0x00506aaa        ; back edge
/// </code>
/// <para>The volley-size load is at a HIGHER address than the call and the back
/// edge targets 0x00506aaa, so the sound is issued once per release and the
/// loop then creates <c>[weaponMode+0x48]</c> rounds. `+0x48` is
/// CWeaponVolleySize: `CWeaponVolleySize__ApplyToWeaponModeByName` (0x00436130)
/// is its only writer. A four-round Twin Vulcan volley therefore makes ONE
/// sound call, not four.</para>
///
/// <para><see cref="RoundCount"/> is what that release actually launched, so a
/// consumer can see the volley without inferring it from projectile ids.</para>
/// </summary>
public sealed record Level100WeaponFireEvent(
    int Tick,
    Level100PlayerWeapon Weapon,
    int RoundCount);

[Flags]
public enum SimActions : byte
{
    None = 0,
    ToggleMode = 1 << 0,
    Fire = 1 << 1,
    Reset = 1 << 2,
    LandingJets = 1 << 3,
}

public readonly record struct SimVector2(int X, int Z)
{
    public static SimVector2 Zero => new(0, 0);
}

public readonly record struct SimInput(
    sbyte MoveX,
    sbyte MoveZ,
    SimActions Actions = SimActions.None,
    sbyte LookX = 0,
    sbyte LookY = 0,
    short LookXAnalogPermille = 0,
    short LookYAnalogPermille = 0)
{
    // Fire and LandingJets may be held. UI adapters must edge-sample
    // ToggleMode and Reset.
    // LookX is body look left/right and LookY is screen up/down (-1/0/+1).
    // Analog look is the deterministic -1000..1000 axis produced by an input adapter.
    public static SimInput Idle => new(0, 0);

    public bool HasAction(SimActions action) => (Actions & action) != 0;

    public void Validate()
    {
        if (MoveX is < -1 or > 1)
        {
            throw new ArgumentOutOfRangeException(nameof(MoveX), "MoveX must be -1, 0, or 1.");
        }

        if (MoveZ is < -1 or > 1)
        {
            throw new ArgumentOutOfRangeException(nameof(MoveZ), "MoveZ must be -1, 0, or 1.");
        }

        if (LookX is < -1 or > 1)
        {
            throw new ArgumentOutOfRangeException(nameof(LookX), "LookX must be -1, 0, or 1.");
        }

        if (LookY is < -1 or > 1)
        {
            throw new ArgumentOutOfRangeException(nameof(LookY), "LookY must be -1, 0, or 1.");
        }

        if (LookXAnalogPermille is < -1_000 or > 1_000)
        {
            throw new ArgumentOutOfRangeException(
                nameof(LookXAnalogPermille),
                "LookXAnalogPermille must be between -1000 and 1000.");
        }

        if (LookYAnalogPermille is < -1_000 or > 1_000)
        {
            throw new ArgumentOutOfRangeException(
                nameof(LookYAnalogPermille),
                "LookYAnalogPermille must be between -1000 and 1000.");
        }

        const SimActions known = SimActions.ToggleMode |
            SimActions.Fire |
            SimActions.Reset |
            SimActions.LandingJets;
        if ((Actions & ~known) != 0)
        {
            throw new ArgumentOutOfRangeException(nameof(Actions), "Input contains an unknown action bit.");
        }
    }
}

public sealed record TargetSnapshot(
    Level100ActorId ActorId,
    int Id,
    string DefinitionName,
    string MeshBinding,
    SimVector2 Position,
    int Hull,
    bool IsActive,
    Level100ActorPoseSnapshot Pose);

public sealed record ProjectileSnapshot(
    int Id,
    SimVector2 Position,
    SimVector2 Velocity,
    int ElevationMillimeters,
    int VerticalVelocityMillimetersPerTick,
    int RemainingTicks);

public sealed record WalkerFootContactSnapshot(
    int Id,
    SimVector2 Position,
    int GroundElevationMillimeters,
    int PhaseThirds,
    int LiftMillimeters)
{
    public int StepPhase => PhaseThirds == 0
        ? 0
        : Math.Min(
            SimulationConstants.WalkerFootPhaseEnd,
            (PhaseThirds + 1) / 3);
}

public abstract record Level100SimulationFact;

public sealed record Level100ActorHitFact(
    Level100ActorId ActorId,
    Level100ActorId? OtherActorId = null,
    uint OtherThingTypeMask = 0)
    : Level100SimulationFact;

public sealed record Level100ActorStartedDyingFact(Level100ActorId ActorId)
    : Level100SimulationFact;

public sealed record Level100ActorDiedFact(Level100ActorId ActorId)
    : Level100SimulationFact;

public sealed record Level100ActorPoseFact(
    Level100ActorId ActorId,
    Level100ActorPoseSnapshot Pose)
    : Level100SimulationFact;

public sealed record Level100ActorActivationFact(
    Level100ActorId ActorId,
    bool Active)
    : Level100SimulationFact;

public sealed record Level100ActorObjectiveFact(
    Level100ActorId ActorId,
    bool IsObjective)
    : Level100SimulationFact;

public sealed record Level100ActorHealthFact(
    Level100ActorId ActorId,
    int Health)
    : Level100SimulationFact;

public sealed record Level100SpawnThingFact(
    Level100ActorId OwnerActorId,
    string DefinitionName,
    string SpawnerName,
    int Count,
    string ScriptName)
    : Level100SimulationFact;

public sealed record Level100MissionInputFact(Level100MissionInput Input)
    : Level100SimulationFact;

public sealed record Level100PlayerDamageFact(int Damage) : Level100SimulationFact;

public sealed record Level100PlayerDeathFact : Level100SimulationFact;

public sealed record Level100WaterLossFact : Level100SimulationFact;

public sealed record Level100TriggerActorSnapshot(
    Level100MissionTrigger Trigger,
    SimVector2 Position,
    bool Active,
    bool IsObjective,
    bool Reached);

public sealed record WorldSnapshot(
    int Tick,
    uint Seed,
    Level100TutorialProgress InitialLevel100TutorialProgress,
    VehicleMode Mode,
    VehicleTransition Transition,
    SimVector2 PlayerPosition,
    SimVector2 PlayerVelocity,
    int PlayerGroundElevationMillimeters,
    int PlayerGroundDeltaMillimeters,
    int PlayerElevationMillimeters,
    int PlayerVerticalVelocityMillimetersPerTick,
    bool PlayerOnGround,
    bool PlayerInWater,
    bool PlayerWaterFailure,
    bool PlayerOnSteepSlope,
    bool LandingJetsActive,
    int GroundImpactSpeedMillimetersPerTick,
    IReadOnlyList<AquilaFlightEvent> AquilaFlightEventLog,
    sbyte FacingX,
    sbyte FacingZ,
    int FacingYawMicroRad,
    int WalkerYawVelocityMicroRadPerTick,
    int FacingPitchMicroRad,
    int WalkerPitchVelocityMicroRadPerTick,
    int BodyRollMicroRad,
    int RollVelocityMicroRadPerTick,
    int Energy,
    int Shield,
    int Hull,
    int TransformTicksRemaining,
    bool WalkerToJetUsesTakeoffLift,
    bool WalkerToJetLiftApplied,
    int TicksSinceGroundContact,
    int JetTicksSinceTransform,
    int JetStrafeTicksRemaining,
    int JetStrafeAccelerationRemainder,
    int JetEnergyDrainRemainderMicroRetail,
    int JetThrusterPermille,
    int JetGroundedSlowTicks,
    int JetStallTicks,
    int FireCooldownTicksRemaining,
    int Level100OpeningTicksRemaining,
    bool Level100PlayerActive,
    bool Level100FlightEnabled,
    bool Level100PulseCannonEnabled,
    bool Level100VulcanCannonEnabled,
    bool Level100MechVulcanCannonEnabled,
    bool Level100MissilePodEnabled,
    int Level100HudEmphasisMask,
    Level100MissionSnapshot Level100Mission,
    IReadOnlyList<Level100MissionEvent> Level100MissionEvents,
    Level100ActorRegistrySnapshot Level100Actors,
    Level100DestructionRuntimeSnapshot Level100Destruction,
    IReadOnlyList<Level100DestructionEvent> Level100DestructionEvents,
    IReadOnlyList<Level100WeaponFireEvent> Level100WeaponFireEvents,
    Level100ActorScriptRuntimeSnapshot Level100ActorScripts,
    IReadOnlyList<Level100ActorScriptCommand> Level100ActorScriptCommands,
    Level100ActorMechanicsSnapshot Level100ActorMechanics,
    int NextProjectileId,
    IReadOnlyList<ProjectileSnapshot> Projectiles,
    IReadOnlyList<WalkerFootContactSnapshot> WalkerFeet)
{
    public bool Level100PlayerControlEnabled =>
        Level100PlayerActive && Level100OpeningTicksRemaining == 0;

    public bool Level100StaticTargetsArmed => Level100Actors.Actors.Any(actor =>
        actor.TargetGroup == Level100MissionTargetGroup.StaticTargets &&
        actor.IsObjective &&
        actor.Lifecycle != Level100ActorLifecycle.Destroyed);

    public IReadOnlyList<Level100TriggerActorSnapshot> Level100TriggerActors =>
        Array.AsReadOnly(Level100Actors.Actors
            .Where(actor => actor.Trigger.HasValue && actor.Pose is not null)
            .OrderBy(actor => actor.Trigger)
            .Select(actor => new Level100TriggerActorSnapshot(
                actor.Trigger!.Value,
                new SimVector2(
                    actor.Pose!.PositionMillimeters.X,
                    actor.Pose.PositionMillimeters.Z),
                actor.Active,
                actor.IsObjective,
                actor.TriggerEventDispatched))
            .ToArray());

    public int TargetsDestroyed => Level100Actors.Actors.Count(actor =>
        actor.TargetGroup == Level100MissionTargetGroup.StaticTargets &&
        actor.Lifecycle == Level100ActorLifecycle.Destroyed);

    public IReadOnlyList<TargetSnapshot> Targets =>
        Array.AsReadOnly(Level100Actors.Actors
            .Where(actor =>
                (actor.TargetGroup is
                    Level100MissionTargetGroup.StaticTargets or
                    Level100MissionTargetGroup.TargetTrucks) &&
                actor.Pose is not null)
            .OrderBy(actor => actor.TargetGroup)
            .ThenBy(actor => actor.TargetOrdinal)
            .Select(CreateTargetSnapshot)
            .ToArray());

    private static TargetSnapshot CreateTargetSnapshot(
        Level100ActorSnapshot actor)
    {
        string definitionName = actor.DefinitionName ??
            throw new InvalidDataException(
                $"Level 100 target actor {actor.ActorId.Value} has no definition.");
        string meshBinding = actor.MeshBinding ??
            throw new InvalidDataException(
                $"Level 100 target actor {actor.ActorId.Value} has no mesh binding.");
        Level100ActorPoseSnapshot pose = actor.Pose ??
            throw new InvalidDataException(
                $"Level 100 target actor {actor.ActorId.Value} has no pose.");
        int id = actor.TargetGroup switch
        {
            Level100MissionTargetGroup.StaticTargets =>
                actor.TargetOrdinal,
            Level100MissionTargetGroup.TargetTrucks =>
                4 + actor.TargetOrdinal,
            _ => throw new InvalidDataException(
                $"Level 100 actor {actor.ActorId.Value} is not a rendered target."),
        };
        return new TargetSnapshot(
            actor.ActorId,
            id,
            definitionName,
            meshBinding,
            new SimVector2(
                pose.PositionMillimeters.X,
                pose.PositionMillimeters.Z),
            actor.Health,
            actor.Active &&
                actor.Lifecycle !=
                Level100ActorLifecycle.Destroyed,
            pose);
    }

    public int PlayerAltitudeAboveGroundMillimeters =>
        PlayerElevationMillimeters - PlayerGroundElevationMillimeters;

    public int PlayerAltitudeAboveSurfaceMillimeters =>
        PlayerElevationMillimeters - Math.Max(
            PlayerGroundElevationMillimeters,
            Level100Terrain.WaterElevationMillimeters);

    public bool Level100FiringRangeTargetsActive =>
        Level100StaticTargetsArmed &&
        Targets.Any(target => target.Id is >= 1 and <= 4 && target.IsActive);

    public bool Level100CurrentWeaponHighlighted =>
        (Level100HudEmphasisMask & (1 << 5)) != 0;
}
