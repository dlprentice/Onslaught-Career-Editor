// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// What the Battle Engine's last event-path crosshair line struck, as
/// <c>CWorldLineColReport::mHitType</c> records it: 0 nothing, 1 ground,
/// 3 a thing (<c>CWorld::FindFirstThingToHitLine</c>, <c>0x0050b030</c>).
/// </summary>
public enum Level100CrosshairHitKind : byte
{
    Nothing = 0,
    Ground = 1,
    Thing = 3,
}

/// <summary>
/// The player Battle Engine's targeting state: the crosshair units
/// (<c>+0x4c8</c>, <c>+0x4cc</c>), the retained event-path line report
/// (<c>mWlcr</c>) and the lock sets.
/// </summary>
public sealed record Level100BattleEngineTargetingSnapshot(
    Level100ActorId? CrosshairUnit,
    Level100ActorId? CrosshairUnitRegardlessOfRange,
    Level100CrosshairHitKind CrosshairHitKind,
    int CrosshairHitDistanceMillimeters,
    Level100PlayerLockSetSnapshot Locks)
{
    public static Level100BattleEngineTargetingSnapshot Initial { get; } = new(
        null, null, Level100CrosshairHitKind.Nothing, 0,
        new Level100PlayerLockSetSnapshot([], [], 0, 0));
}

public sealed partial class Simulation
{
    private Level100ActorId? _crosshairUnit;
    private Level100ActorId? _crosshairUnitRegardlessOfRange;
    private Level100CrosshairHitKind _crosshairHitKind;
    private int _crosshairHitDistanceMillimeters;
    private Level100PlayerLocks _playerLocks = null!;
    private readonly RetailBattleEngineShake _shake = new();

    /// <summary>
    /// The tail of <c>CBattleEngine::Init</c> (<c>0x00404dd0</c>,
    /// <c>BattleEngine.cpp:350-352</c>): one draw and event 6002, then
    /// <c>HandleAutoAim(NULL)</c>, which files 6003 with its own draw.
    /// </summary>
    /// <remarks>
    /// Where this Init sits in the level's construction order relative to
    /// the other constructors' draws is the RE lane's open first-flush
    /// question; Core runs it once the level's actors and mechanics exist.
    /// </remarks>
    private void InitializeBattleEngineRefreshEvents()
    {
        RetailEventScheduler events = _level100ActorMechanics.LevelEvents;
        if (events.FrameCount != _retailEventFrameCount)
        {
            throw new InvalidOperationException(
                "The Battle Engine must be constructed on the level event clock.");
        }

        events.AddEvent(
            RetailBattleEngineRefresh.CrosshairEvent,
            Level100ActorMechanics.BattleEngineListener,
            RetailBattleEngineRefresh.CrosshairDueTime(
                _level100ActorMechanics.NextReleasedRandom(), events.Time),
            RetailEventPriority.StartOfFrame);
        HandleAutoAim(events, reuseHandle: -1);
    }

    /// <summary><c>CBattleEngine::HandleEvent</c> for 6002 and 6003 (<c>0x0040c180</c>).</summary>
    private void HandleBattleEngineEvent(RetailEventScheduler events, RetailEventDispatch dispatch)
    {
        switch (dispatch.EventNum)
        {
            case RetailBattleEngineRefresh.CrosshairEvent:
            {
                Level100ActorId? unit = CalcUnitOverCrossHair(updateData: true);
                // 0x0040b091: the requeue closes CalcUnitOverCrossHair; HandleEvent
                // then stores its result in +0x4c8.
                events.AddEvent(
                    RetailBattleEngineRefresh.CrosshairEvent,
                    dispatch.Listener,
                    RetailBattleEngineRefresh.CrosshairDueTime(
                        _level100ActorMechanics.NextReleasedRandom(), events.Time),
                    RetailEventPriority.StartOfFrame,
                    reuseHandle: dispatch.Handle);
                _crosshairUnit = unit;
                return;
            }
            case RetailBattleEngineRefresh.AutoAimEvent:
                HandleAutoAim(events, dispatch.Handle);
                return;
            default:
                throw new InvalidOperationException(
                    $"Unadmitted Battle Engine event {dispatch.EventNum}.");
        }
    }

    /// <summary>
    /// <c>HandleAutoAim</c> (<c>0x0040b6d0</c>, <c>BattleEngine.cpp:2446-2613</c>).
    /// Auto-aim is allowed for the whole level: <c>CGame::InitRestartLoop</c>
    /// sets <c>GAME+0x20</c> to 1 (<c>0x0046c4c2</c>) and only the pause
    /// menu's option changes it, which the rebuild's pause menu does not
    /// offer. The call therefore always ends with one draw and a new 6003.
    /// </summary>
    /// <remarks>
    /// The Smart-weapon candidate search and the offsets it drives are not
    /// implemented yet: <c>mAutoAimTarget</c> stays null, which is exactly
    /// retail for the non-Smart Pulse Cannon Pod and Missile Pod, and not yet
    /// retail for the Smart Vulcans. The draw and requeue are exact.
    /// </remarks>
    private void HandleAutoAim(RetailEventScheduler events, int reuseHandle)
    {
        events.AddEvent(
            RetailBattleEngineRefresh.AutoAimEvent,
            Level100ActorMechanics.BattleEngineListener,
            RetailBattleEngineRefresh.AutoAimDueTime(
                _level100ActorMechanics.NextReleasedRandom(), events.Time),
            RetailEventPriority.StartOfFrame,
            reuseHandle: reuseHandle);
    }

    /// <summary>
    /// <c>CalcUnitOverCrossHair</c> (<c>0x0040acc0</c>,
    /// <c>BattleEngine.cpp:2278-2344</c>) on its event path: clear both
    /// crosshair readers, cast the 1000-unit view line with mesh collision
    /// and retain its report, then return the struck unit when the current
    /// weapon's range exceeds the hit distance.
    /// </summary>
    private Level100ActorId? CalcUnitOverCrossHair(bool updateData)
    {
        if (updateData)
        {
            _crosshairUnit = null;
            _crosshairUnitRegardlessOfRange = null;
        }

        (SimVector3 start, SimVector3 end) = CrosshairLine();
        bool struck = _level100Destruction.TryFindFirstThingOnLine(
            start,
            end,
            IsCrosshairLineCandidate,
            out Level100ContactHit hit);
        Level100CrosshairHitKind kind = !struck
            ? Level100CrosshairHitKind.Nothing
            : hit.SurfaceKind == Level100ContactSurfaceKind.Terrain
                ? Level100CrosshairHitKind.Ground
                : Level100CrosshairHitKind.Thing;
        // The line is 1,000,000 mm long, so its parts-per-million time is the
        // distance in millimetres.
        int distance = struck ? hit.TimePartsPerMillion : 0;
        if (updateData)
        {
            _crosshairHitKind = kind;
            if (struck)
            {
                _crosshairHitDistanceMillimeters = distance;
            }
        }

        if (kind != Level100CrosshairHitKind.Thing)
        {
            return null;
        }

        var unit = new Level100ActorId(hit.ActorId);
        Level100ActorSnapshot actor = _level100Actors.GetActor(unit);
        Level100ThingClass thingClass = Level100ThingClasses.Of(actor.DefinitionName);
        // A lifeless building is not a crosshair unit (BattleEngine.cpp:2327).
        if (!thingClass.IsUnit ||
            (thingClass.IsBuilding && actor.Lifecycle != Level100ActorLifecycle.Alive))
        {
            return null;
        }

        if (updateData)
        {
            _crosshairUnitRegardlessOfRange = unit;
        }

        long range = (long)(CurrentWeaponActualMaxRange() * 1000.0f);
        return range > distance ? unit : null;
    }

    /// <summary>
    /// The candidate filter the crosshair line applies: dying things that are
    /// not buildings are skipped (<c>0x0050b030</c>). The Battle Engine,
    /// trees and rounds are never contact actors here.
    /// </summary>
    private static bool IsCrosshairLineCandidate(
        Level100ActorSnapshot actor,
        Level100ContactDefinition definition) =>
        actor.Lifecycle is not (Level100ActorLifecycle.StartedDying or
            Level100ActorLifecycle.DiedAwaitingShutdown) ||
        Level100ThingClasses.Of(actor.DefinitionName).IsBuilding;

    /// <summary>
    /// The view line: 1000 units from the view point along the view
    /// orientation times the auto-aim matrix. Core has no camera, so the
    /// Battle Engine's position and facing stand in for the view, as the
    /// launch correction has always assumed; the auto-aim offsets are zero
    /// until its search is implemented.
    /// </summary>
    private (SimVector3 Start, SimVector3 End) CrosshairLine()
    {
        const int LineLengthMillimeters = 1_000_000;
        (int yawSin, int yawCos) = FixedSinCos(_facingYawMicroRad);
        (int pitchSin, int pitchCos) = FixedSinCos(_facingPitchMicroRad);
        int horizontalLength = DivideRoundNearest(
            (long)pitchCos * LineLengthMillimeters,
            FixedTrigScale);
        var start = new SimVector3(
            PlayerPosition.X,
            PlayerElevationMillimeters,
            PlayerPosition.Z);
        var end = new SimVector3(
            checked(start.X + DivideRoundNearest(
                -(long)yawSin * horizontalLength,
                FixedTrigScale)),
            checked(start.Y + DivideRoundNearest(
                -(long)pitchSin * LineLengthMillimeters,
                FixedTrigScale)),
            checked(start.Z + DivideRoundNearest(
                (long)yawCos * horizontalLength,
                FixedTrigScale)));
        return (start, end);
    }

    /// <summary>
    /// <c>GetCurrentWeapon</c> (<c>BattleEngine.cpp:2740-2746</c>): the jet
    /// part's weapon only in the jet state, the walker part's otherwise,
    /// including both morphs.
    /// </summary>
    private Level100MissionWeapon RetailCurrentWeapon =>
        _mode == VehicleMode.Jet && _transition == VehicleTransition.None
            ? _level100PlayerWeapons.JetSelectedWeapon
            : _level100PlayerWeapons.WalkerSelectedWeapon;

    private float CurrentWeaponActualMaxRange()
    {
        Level100MissionWeapon weapon = RetailCurrentWeapon;
        return RetailBattleEngineRefresh.ActualMaxRange(
            weapon,
            weapon == Level100MissionWeapon.PulseCannonPod &&
                _level100PlayerWeapons.PulseChargeLevel >= 1);
    }

    /// <summary>
    /// Causal-probe seam for the crosshair line: sets the Battle Engine's
    /// current yaw and pitch, which Core also uses as the view orientation.
    /// No shipped path calls this; the next <see cref="Step"/> still owns the
    /// event delivery, the line query and every later use of the report.
    /// </summary>
    internal void SetFacingForMeasurement(int yawMicroRad, int pitchMicroRad)
    {
        _facingYawMicroRad = NormalizeMicroRad(yawMicroRad);
        _facingPitchMicroRad = NormalizeMicroRad(pitchMicroRad);
        QuantizeFacingFromYaw();
    }

    /// <summary>
    /// Causal-probe seam: the launch orientation a round from this emitter
    /// would take now, from <see cref="ReticleAdjustedLaunchAngles"/>.
    /// </summary>
    internal (int YawMicroRad, int PitchMicroRad) LaunchAnglesForMeasurement(SimVector3 emitter) =>
        ReticleAdjustedLaunchAngles(emitter);

    private Level100BattleEngineTargetingSnapshot TargetingSnapshot => new(
        _crosshairUnit,
        _crosshairUnitRegardlessOfRange,
        _crosshairHitKind,
        _crosshairHitDistanceMillimeters,
        _playerLocks.Snapshot);

    private void ResetBattleEngineTargeting()
    {
        _crosshairUnit = null;
        _crosshairUnitRegardlessOfRange = null;
        _crosshairHitKind = Level100CrosshairHitKind.Nothing;
        _crosshairHitDistanceMillimeters = 0;
        _playerLocks = new Level100PlayerLocks(id => _level100Actors.GetLifecycle(id));
        _shake.Reset();
    }

    /// <summary>
    /// The tail of <c>CBattleEngine::Move</c> after the part moves:
    /// <c>UpdateRotation</c>'s shake decay (<c>BattleEngine.cpp:1222-1233</c>)
    /// and the heat-store cooling loop (<c>:1708-1718</c>). Both run on every
    /// Move, dying or not, for as long as the Battle Engine exists.
    /// </summary>
    private void AdvanceBattleEngineRotationTail()
    {
        if (_level100Actors.GetLifecycle(_level100PlayerActorId) == Level100ActorLifecycle.Destroyed)
        {
            return;
        }

        _shake.Decay();
        _level100PlayerWeapons.CoolStores();
    }
}
