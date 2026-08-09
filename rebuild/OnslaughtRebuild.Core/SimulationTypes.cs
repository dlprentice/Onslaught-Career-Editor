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

/// <summary>
/// The complete discrete player action set of the released PC build, plus the
/// one rebuild-owned harness action.
/// </summary>
/// <remarks>
/// <para>
/// <b>The width is decided once, here, deliberately.</b> This was a
/// four-member <c>byte</c>; the released set does not fit in eight bits, and
/// discovering that one action at a time would re-cut the command tape and the
/// replay trace every time. So the whole released set is declared now and the
/// storage is <c>ushort</c>, leaving six spare bits.
/// </para>
/// <para>
/// The set is taken from the shipped 47-row binding table
/// (<c>OptionsEntries__InitDefaultSingleBindingsTable</c>, <c>0x00514210</c>)
/// intersected with what <c>CPlayer::ReceiveButtonAction</c> actually
/// dispatches (<c>references/Onslaught/Player.cpp:283-511</c>, retail
/// <c>0x004D3110</c>). Axes — yaw <c>0x19</c>/<c>0x1b</c>, pitch
/// <c>0x1a</c>/<c>0x1c</c>, strafe <c>0x1d</c>/<c>0x1e</c>, forward/back
/// <c>0x1f</c>/<c>0x20</c> — are not flags; they are the
/// <see cref="SimInput"/> axis fields.
/// </para>
/// <para><b>Deliberately absent, each verified against the shipped table's
/// <c>entry_id</c> multiset:</b></para>
/// <list type="bullet">
///   <item><c>BUTTON_HELP</c> <c>0x39</c> — no row binds it, and retail
///   <c>0x004D3110</c> short-circuits the entire body on
///   <c>if (button != 0x39)</c>. Stuart's handler
///   (<c>Player.cpp:302-309</c>) is a commented-out stub that returns.</item>
///   <item><c>BUTTON_MECH_CONFIGURATION_DOWN</c> <c>0x3d</c> and
///   <c>BUTTON_MECH_CONFIGURATION_UP</c> <c>0x3e</c>
///   (<c>references/Onslaught/Controller.h:161-162</c> — note that order) — no
///   row binds either, and both retail cases reach only <c>DebugTrace</c>.</item>
///   <item><c>BUTTON_MECH_JET_AFTERBURNER</c> <c>0x16</c> — no row binds it,
///   and Stuart's case body is commented out
///   (<c>Player.cpp:490-494</c>).</item>
///   <item><c>BUTTON_PAUSE</c> <c>0x38</c> — bound (row 34, Escape) but handled
///   by <c>CGame::Pause</c> before any player dispatch. Pause is a client
///   lifecycle concern; Core advances zero steps while paused and owns no
///   pause state.</item>
/// </list>
/// </remarks>
[Flags]
public enum SimActions : ushort
{
    None = 0,

    /// <summary>
    /// <c>BUTTON_MECH_MORPH</c> <c>0x21</c>. Shipped row 9, <c>active=1</c>,
    /// KEY_ONCE, DIK_SPACE.
    /// </summary>
    ToggleMode = 1 << 0,

    /// <summary>
    /// <c>BUTTON_MECH_FIRE_GUN_POD</c> <c>0x12</c>. Shipped row 11,
    /// <c>active=1</c>, mouse device <c>0x11</c>.
    /// </summary>
    Fire = 1 << 1,

    /// <summary>
    /// Rebuild-owned. No released button dispatches this; it exists so a tape
    /// or a client can restart a run deterministically.
    /// </summary>
    Reset = 1 << 2,

    /// <summary>
    /// <c>BUTTON_MECH_LANDING_JETS</c> <c>0x15</c>. Shipped row 15,
    /// <c>active=1</c>, KEY_ON, DIK_LSHIFT.
    /// </summary>
    LandingJets = 1 << 3,

    /// <summary>
    /// <c>BUTTON_SKIP_PANNING</c> <c>0x3a</c>
    /// (<c>references/Onslaught/Controller.h:158</c>). Shipped rows 22-25,
    /// <c>active=0</c> (hard-wired, not rebindable), KEY_ONCE, DIK scan codes
    /// <c>0x39</c>/<c>0x1c</c>/<c>0x01</c>/<c>0x9c</c> = Space, Enter, Escape,
    /// Numpad Enter.
    /// </summary>
    /// <remarks>
    /// <para>
    /// <b>WHICH KEY ACTUALLY REACHES THIS ACTION IN RETAIL IS UNPROVEN, FOR ALL
    /// FOUR SCAN CODES.</b> The rows are byte-read facts; the routing is not.
    /// Recorded here 2026-07-27 because the client's binding excluded Escape on
    /// exactly this reasoning and then applied none of it to the other three,
    /// which is an asymmetry rather than a conclusion.
    /// </para>
    /// <para>
    /// Reading a KEY_ONCE flag CONSUMES it in the developers' own PC shell —
    /// <c>references/Onslaught/ltshell.h:292</c>,
    /// <c>BYTE xKeyOnce(int c) { BYTE a = KeyWasDown[c]; KeyWasDown[c] = 0;
    /// return a; }</c> — and <c>CController::DoMappings</c> walks the shipped
    /// table in row order. Every one of the four scan codes is also bound to an
    /// EARLIER row:
    /// </para>
    /// <list type="bullet">
    ///   <item>Space <c>0x39</c> — row 9, <c>BUTTON_MECH_MORPH</c>
    ///   <c>0x21</c>, KEY_ONCE, <c>active=1</c>;</item>
    ///   <item>Enter <c>0x1c</c> and Numpad Enter <c>0x9c</c> — row 20,
    ///   <c>BUTTON_SKIP_CUTSCENE</c>
    ///   (<c>reverse-engineering/source-code/frontend/fep-systems.md:19</c>);</item>
    ///   <item>Escape <c>0x01</c> — rows 17 <c>BUTTON_FRONTEND_MENU_BACK</c>,
    ///   20 <c>BUTTON_SKIP_CUTSCENE</c> and 34 <c>BUTTON_PAUSE</c>.</item>
    /// </list>
    /// <para>
    /// If retail's <c>GetKeyOnce</c> (vtable <c>+0x18</c>) consumes the way
    /// Stuart's does, the earlier row eats the press and rows 22-25 never see
    /// it. That body is not in the partial drop and is not decompiled.
    /// Corroborating the doubt rather than settling it,
    /// <c>references/Onslaught/PCController.cpp:76</c> binds
    /// <c>BUTTON_SKIP_PANNING</c> as <c>BUTTON_ONCE, 1</c> — <b>a pad button,
    /// not a key</b>.
    /// </para>
    /// <para>
    /// None of this touches the LAW Core implements, which is
    /// <c>Player.cpp:311-315</c> and is about game state, not about scan codes:
    /// Core takes the action from whoever raises it. It bounds what a CLIENT
    /// binding may claim. The Godot client's Space/Enter/Numpad Enter choice is
    /// a reconstruction decision made for playability, and
    /// <c>Level100SkipPanningClientTests</c> pins it as such rather than as
    /// released reachability.
    /// </para>
    /// </remarks>
    SkipPanning = 1 << 4,

    /// <summary>
    /// <c>BUTTON_MECH_CHARGE_GUN_POD</c> <c>0x13</c>, shipped row 10
    /// (<c>active=1</c>, mouse device <c>0x0f</c>). DECLARED, NOT IMPLEMENTED:
    /// Core currently models a release as a single <see cref="Fire"/> edge and
    /// has no charge accumulator. <see cref="SimInput.Validate"/> rejects it.
    /// </summary>
    ChargeWeapon = 1 << 5,

    /// <summary>
    /// <c>BUTTON_MECH_CHANGE_WEAPON</c> <c>0x14</c>, shipped row 12
    /// (<c>active=1</c>, mouse device <c>0x10</c> code 2). DECLARED, NOT
    /// IMPLEMENTED: Core now preserves the selected Walker and Jet slots, but
    /// changing them would expose the still-unimplemented Missile Pod launch
    /// law and charge/store eligibility gate.
    /// <see cref="SimInput.Validate"/> rejects it.
    /// </summary>
    ChangeWeapon = 1 << 6,

    /// <summary>
    /// <c>BUTTON_MECH_CHANGE_ZOOM_IN</c> <c>0x10</c>, shipped row 13
    /// (<c>active=1</c>, mouse device <c>0x10</c> code 4). DECLARED, NOT
    /// IMPLEMENTED: zoom is a projection term with no Core state.
    /// <see cref="SimInput.Validate"/> rejects it.
    /// </summary>
    ZoomIn = 1 << 7,

    /// <summary>
    /// <c>BUTTON_MECH_CHANGE_ZOOM_OUT</c> <c>0x11</c>, shipped row 14
    /// (<c>active=1</c>, mouse device <c>0x10</c> code 3). DECLARED, NOT
    /// IMPLEMENTED. <see cref="SimInput.Validate"/> rejects it.
    /// </summary>
    ZoomOut = 1 << 8,

    /// <summary>
    /// <c>BUTTON_MECH_CLOAK</c> <c>0x3b</c>, shipped row 8 (<c>active=1</c>,
    /// KEY_ONCE, DIK_TAB). DECLARED, NOT IMPLEMENTED: Core has no cloak state.
    /// <see cref="SimInput.Validate"/> rejects it.
    /// </summary>
    Cloak = 1 << 9,
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
    // LandingJets may be held. Fire is the released gun-button edge; UI
    // adapters must also edge-sample ToggleMode, Reset and SkipPanning - every
    // shipped BUTTON_SKIP_PANNING row is KEY_ONCE (push type 8).
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

        if ((Actions & ~DeclaredActions) != 0)
        {
            throw new ArgumentOutOfRangeException(nameof(Actions), "Input contains an unknown action bit.");
        }

        // A declared-but-unimplemented action must NOT be accepted and
        // silently ignored. The enum fixes the released set and the storage
        // width in one decision; this keeps that from becoming a bit that
        // looks bound and does nothing.
        SimActions unimplemented = Actions & ~ImplementedActions;
        if (unimplemented != 0)
        {
            throw new ArgumentOutOfRangeException(
                nameof(Actions),
                $"Input requests released action(s) {unimplemented} that Core declares but does not implement.");
        }
    }

    /// <summary>Every bit this enum assigns a meaning to.</summary>
    public const SimActions DeclaredActions =
        SimActions.ToggleMode |
        SimActions.Fire |
        SimActions.Reset |
        SimActions.LandingJets |
        SimActions.SkipPanning |
        SimActions.ChargeWeapon |
        SimActions.ChangeWeapon |
        SimActions.ZoomIn |
        SimActions.ZoomOut |
        SimActions.Cloak;

    /// <summary>The subset Core actually acts on.</summary>
    public const SimActions ImplementedActions =
        SimActions.ToggleMode |
        SimActions.Fire |
        SimActions.Reset |
        SimActions.LandingJets |
        SimActions.SkipPanning;
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

public sealed record Level100PlayerDamageFact(int IncomingDamageMilliLife)
    : Level100SimulationFact;

public sealed record Level100PlayerDeathFact : Level100SimulationFact;

public sealed record Level100WaterLossFact : Level100SimulationFact;

public enum Level100PlayerDamageSource : byte
{
    ExternalFact = 1,
    ActorRound = 2,
    WaterSkim = 3,
}

/// <summary>
/// One positive incoming-damage application after the released shield split.
/// This is a per-tick observation stream, not accumulated history.
/// </summary>
public sealed record Level100PlayerDamageEvent(
    int Tick,
    Level100PlayerDamageSource Source,
    int IncomingDamageMilliLife,
    int ShieldAbsorbedMilliLife,
    int LifeDamageMilliLife,
    bool RequestsDeath);

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
    int AugmentCharge,
    bool AugmentActive,
    IReadOnlyList<Level100PlayerDamageEvent> Level100PlayerDamageEvents,
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
    int TwinVulcanReloadTicksRemaining,
    int Level100OpeningTicksRemaining,
    bool Level100PlayerActive,
    bool Level100FlightEnabled,
    bool Level100PulseCannonEnabled,
    bool Level100VulcanCannonEnabled,
    bool Level100MechVulcanCannonEnabled,
    bool Level100MissilePodEnabled,
    Level100MissionWeapon Level100WalkerSelectedWeapon,
    Level100MissionWeapon Level100JetSelectedWeapon,
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

    /// <summary>
    /// The Level 100 world actors the RENDERER draws. This is a presentation
    /// projection: nothing in it is hashed into simulation state, and no
    /// mission, HUD or targeting decision reads it except
    /// <see cref="Level100FiringRangeTargetsActive"/>, which tests ids 1..4.
    ///
    /// <para>It is NOT a targetability list. Retail already distinguishes the
    /// two: the ambient U-17 Highside Transporter and the ambient Air Trainer
    /// are authored with mission target group <c>None</c> and no ordinal, and
    /// they stay that way here. The scanner reaches actors through
    /// <c>Level100Actors.Actors</c> directly, so widening this projection adds
    /// nothing to the HUD.</para>
    /// </summary>
    public IReadOnlyList<TargetSnapshot> Targets =>
        Array.AsReadOnly(Level100Actors.Actors
            .Where(IsRenderedWorldActor)
            .OrderBy(actor => actor.TargetGroup)
            .ThenBy(actor => actor.TargetOrdinal)
            // The two ambient aircraft share TargetOrdinal 0, so the canonical
            // actor id is what keeps this projection totally ordered.
            .ThenBy(actor => actor.ActorId.Value)
            .Select(CreateTargetSnapshot)
            .ToArray());

    /// <summary>
    /// Every Level 100 world actor the renderer draws. This was a two-group
    /// whitelist admitting only <see cref="Level100MissionTargetGroup.StaticTargets"/>
    /// and <see cref="Level100MissionTargetGroup.TargetTrucks"/>, which silently
    /// dropped 18 of the level's 26 dynamic actors: both ambient aircraft, the
    /// six Vulcan-exercise moving targets, the dodge-exercise Air Trainer and
    /// all nine airborne Target Drones.
    ///
    /// <para>The two ambient aircraft carry NO mission target group, so
    /// <see cref="Level100MissionTargetGroup.None"/> has to be admitted, and it
    /// is admitted narrowly. Widening on "has a mesh binding" alone does not
    /// work: of the 44 authored actor definitions 41 carry group
    /// <c>None</c> and 36 of those carry a non-null mesh binding - the 33
    /// base-world structures are drawn by the static-world asset and the player
    /// carries <c>m_f_be1.msh.aya</c> and is drawn by the Aquila walker/jet
    /// asset. <c>IsStatic</c> excludes the structures and the five General
    /// Volume trigger spheres; "Player 1" is the same canonical name the
    /// simulation itself resolves the player by.</para>
    ///
    /// <para>MEASURED, 2026-07-28 TTD trace of the pristine specimen: retail
    /// constructs both ambient aircraft at level load out of
    /// <c>CWorld__LoadWorld</c> - <c>CreateThingByType</c> creation 28
    /// (<c>CDropship</c>) and creation 29 (<c>CPlane</c>) - and attaches their
    /// <c>Transporter</c> and <c>Flyby</c> scripts before the player has
    /// control. Neither motion nor rendering nor audio is shown by that trace;
    /// it stops at the briefing.</para>
    /// </summary>
    private static bool IsRenderedWorldActor(Level100ActorSnapshot actor) =>
        actor.Pose is not null &&
        actor.MeshBinding is not null &&
        actor.TargetGroup switch
        {
            Level100MissionTargetGroup.StaticTargets or
            Level100MissionTargetGroup.TargetTrucks or
            Level100MissionTargetGroup.MovingTargets or
            Level100MissionTargetGroup.AirborneTargets1 or
            Level100MissionTargetGroup.AirborneTargets2 or
            Level100MissionTargetGroup.AirTrainer => true,
            Level100MissionTargetGroup.None =>
                !actor.IsStatic &&
                !StringComparer.Ordinal.Equals(actor.Name, "Player 1"),
            _ => false,
        };

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
        // Presentation ids, one disjoint band per authored group. Ordinals run
        // 1..MaximumGroupActors inside a group (Level100ActorRegistry
        // .AllocateMissionOrdinal counts per GROUP, not per spawn definition),
        // so the bands below cannot overlap. StaticTargets 1-4 and TargetTrucks
        // 5-7 are unchanged and load-bearing: Level100FiringRangeTargetsActive
        // tests ids 1..4.
        int id = actor.TargetGroup switch
        {
            Level100MissionTargetGroup.StaticTargets =>
                actor.TargetOrdinal,                     // 1-4
            Level100MissionTargetGroup.TargetTrucks =>
                4 + actor.TargetOrdinal,                 // 5-7
            Level100MissionTargetGroup.MovingTargets =>
                7 + actor.TargetOrdinal,                 // 8-13
            Level100MissionTargetGroup.AirborneTargets1 =>
                13 + actor.TargetOrdinal,                // 14-16
            Level100MissionTargetGroup.AirborneTargets2 =>
                16 + actor.TargetOrdinal,                // 17-22
            Level100MissionTargetGroup.AirTrainer =>
                22 + actor.TargetOrdinal,                // 23
            // The two ambient aircraft are authored with no group and no
            // ordinal, so their id comes from the canonical actor id, which is
            // unique and stable across the run.
            Level100MissionTargetGroup.None =>
                100 + actor.ActorId.Value,
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
