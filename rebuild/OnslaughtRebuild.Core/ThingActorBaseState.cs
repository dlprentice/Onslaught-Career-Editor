// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// The source <c>CThing::mFlags</c> bits that this deterministic Core seam
/// currently carries. World/map/render ownership bits remain outside Core.
/// </summary>
[Flags]
public enum ThingActorFlags : ushort
{
    None = 0,
    DeclaredShutdown = 1 << 0,
    Dying = 1 << 2,
    Invisible = 1 << 4,
}

/// <summary>
/// Source inheritance bits composed by the CThing/CComplexThing/CActor
/// <c>SetThingType</c> chain. Retail proves the CThing and CActor endpoints;
/// the CComplexThing middle override remains source-only in the W2 receipt.
/// </summary>
public static class ThingActorTypeMasks
{
    public const uint Thing = 0x00000001;
    public const uint Actor = 0x00000002;
    public const uint ComplexThing = 0x80000000;
    public const uint ActorLineage = Thing | ComplexThing | Actor;
}

/// <summary>
/// A deterministic simulation pose. It contains no renderer or engine object.
/// </summary>
public sealed record ThingActorPoseSnapshot(
    SimVector3 PositionMillimeters,
    Level100FloatBasis3Bits BasisFloatBits);

/// <summary>
/// Immutable presentation-safe projection of the reusable Thing/Actor state.
/// </summary>
public sealed record ThingActorBaseStateSnapshot(
    ThingActorFlags Flags,
    ThingActorPoseSnapshot CurrentPose,
    ThingActorPoseSnapshot OldPose,
    SimVector3 Velocity,
    SimVector3 AngularVelocity,
    uint ThingTypeMask,
    int LastTimeOnGroundFloatBits,
    int LastTimeInWaterFloatBits,
    int LastTimeOnObjectFloatBits)
{
    public bool IsInvisible => (Flags & ThingActorFlags.Invisible) != 0;

    public bool IsDying => (Flags & ThingActorFlags.Dying) != 0;

    public bool IsShuttingDown =>
        (Flags & ThingActorFlags.DeclaredShutdown) != 0;

    /// <summary>
    /// Retail <c>0x00401550</c>, source inline
    /// <c>CActor::GetLocalLastFrameMovement</c>.
    /// </summary>
    public SimVector3 LocalLastFrameMovement => new(
        CurrentPose.PositionMillimeters.X - OldPose.PositionMillimeters.X,
        CurrentPose.PositionMillimeters.Y - OldPose.PositionMillimeters.Y,
        CurrentPose.PositionMillimeters.Z - OldPose.PositionMillimeters.Z);

    public bool IsA(uint typeMask) => (ThingTypeMask & typeMask) != 0;
}

/// <summary>
/// Pure deterministic state laws shared by source <c>CThing</c> and
/// <c>CActor</c>. Filesystem, clock, render, audio, and engine ownership stay at
/// adapters.
/// </summary>
/// <remarks>
/// <para>
/// Source authority is pinned <c>references/Onslaught</c> commit
/// <c>5352a81cdb838b145a57f7febc5d9fc4b0129ebb</c>:
/// <c>thing.h:41-52, 113-118, 138-146, 156-158, 172-174, 194-199, 237-248,
/// 268-275</c>, <c>thing.cpp:28-37, 183-204, 423-435, 563-571, 742-745</c>,
/// <c>actor.h:13-65</c>, and <c>actor.cpp:15-40, 54-81, 114-149,
/// 326-367</c>.
/// </para>
/// <para>
/// Retail identity is the W2 receipt landed at <c>07fca645</c> (main merge
/// <c>561c2099</c>) plus the promoted CThing/CComplexThing/CActor semantic
/// tables. Relevant exact bodies are visibility <c>0x00401460/0x00401470</c>,
/// actor type <c>0x00401540</c>, last-frame movement <c>0x00401550</c>, stop
/// <c>0x00401580</c>, actor init/move/contact
/// <c>0x004011e0/0x004015e0/0x00402000..0x00402020</c>, CThing type
/// <c>0x004f3470</c>, and shutdown/dying
/// <c>0x004f3760/0x004f37a0</c>.
/// </para>
/// <para>
/// Compiler-folded identities stay explicit: <c>0x004040a0</c> is the one
/// current-position body for render/current/start/end, <c>0x0043e9f0</c> is
/// CThing sound/old position, and <c>0x0043ea20</c> is CComplexThing
/// sound/old orientation. This owner retains one current and one old pose; it
/// does not reintroduce the excluded render/audio virtual defaults.
/// </para>
/// <para>
/// Reuse disposition: <b>REUSED</b> — W2 receipt and sealed
/// <c>pc-layout-thing-complexthing-20260813-v1</c> predecessor
/// <c>e788ffde077c9c861d9163a7526964917cc1747c9c69f6287d9e919a1e399efa</c>;
/// <b>EXTENDED</b> — these existing authorities into a Core state owner and
/// Level-100 adapter; <b>NEW_MEASUREMENT</b> — zero.
/// </para>
/// </remarks>
public sealed class ThingActorBaseState
{
    public static readonly int InitialContactTimeFloatBits =
        BitConverter.SingleToInt32Bits(-100.0f);

    private ThingActorFlags _flags;
    private ThingActorPoseSnapshot _currentPose;
    private ThingActorPoseSnapshot _oldPose;
    private SimVector3 _velocity;
    private SimVector3 _angularVelocity;
    private uint _thingTypeMask;
    private int _lastTimeOnGroundFloatBits;
    private int _lastTimeInWaterFloatBits;
    private int _lastTimeOnObjectFloatBits;

    public ThingActorBaseState(
        ThingActorPoseSnapshot initialPose,
        SimVector3 velocity,
        SimVector3 angularVelocity,
        uint specificTypeMask)
    {
        ValidatePose(initialPose, nameof(initialPose));
        _currentPose = initialPose;
        _oldPose = initialPose;
        _velocity = velocity;
        _angularVelocity = angularVelocity;
        SetThingType(specificTypeMask);
        _lastTimeOnGroundFloatBits = InitialContactTimeFloatBits;
        _lastTimeInWaterFloatBits = InitialContactTimeFloatBits;
        _lastTimeOnObjectFloatBits = InitialContactTimeFloatBits;
    }

    public ThingActorBaseState(ThingActorBaseStateSnapshot snapshot)
    {
        ArgumentNullException.ThrowIfNull(snapshot);
        ThingActorFlags knownFlags =
            ThingActorFlags.DeclaredShutdown |
            ThingActorFlags.Dying |
            ThingActorFlags.Invisible;
        if ((snapshot.Flags & ~knownFlags) != 0 ||
            (snapshot.IsDying && !snapshot.IsShuttingDown) ||
            snapshot.CurrentPose is null ||
            snapshot.OldPose is null ||
            !HasFiniteBasis(snapshot.CurrentPose.BasisFloatBits) ||
            !HasFiniteBasis(snapshot.OldPose.BasisFloatBits) ||
            (snapshot.ThingTypeMask & ThingActorTypeMasks.ActorLineage) !=
                ThingActorTypeMasks.ActorLineage ||
            !IsFiniteFloatBits(snapshot.LastTimeOnGroundFloatBits) ||
            !IsFiniteFloatBits(snapshot.LastTimeInWaterFloatBits) ||
            !IsFiniteFloatBits(snapshot.LastTimeOnObjectFloatBits))
        {
            throw new ArgumentException(
                "Thing/Actor base-state snapshot violates the source contract.",
                nameof(snapshot));
        }

        _flags = snapshot.Flags;
        _currentPose = snapshot.CurrentPose;
        _oldPose = snapshot.OldPose;
        _velocity = snapshot.Velocity;
        _angularVelocity = snapshot.AngularVelocity;
        _thingTypeMask = snapshot.ThingTypeMask;
        _lastTimeOnGroundFloatBits = snapshot.LastTimeOnGroundFloatBits;
        _lastTimeInWaterFloatBits = snapshot.LastTimeInWaterFloatBits;
        _lastTimeOnObjectFloatBits = snapshot.LastTimeOnObjectFloatBits;
    }

    public ThingActorBaseStateSnapshot Snapshot => new(
        _flags,
        _currentPose,
        _oldPose,
        _velocity,
        _angularVelocity,
        _thingTypeMask,
        _lastTimeOnGroundFloatBits,
        _lastTimeInWaterFloatBits,
        _lastTimeOnObjectFloatBits);

    /// <summary>
    /// Retail <c>0x00401470</c>, source inline
    /// <c>CThing::MakeInvisible</c>: set <c>TF_INVISIBLE</c>.
    /// </summary>
    public void MakeInvisible() => _flags |= ThingActorFlags.Invisible;

    /// <summary>
    /// Retail <c>0x00401460</c>, source inline
    /// <c>CThing::MakeVisible</c>: clear <c>TF_INVISIBLE</c>.
    /// </summary>
    public void MakeVisible() => _flags &= ~ThingActorFlags.Invisible;

    /// <summary>
    /// Retail <c>0x004f3760</c>, source <c>CThing::AddShutdownEvent</c>:
    /// set <c>TF_DECLARED_SHUTDOWN</c> once. Scheduling remains outside Core.
    /// </summary>
    public bool DeclareShutdown()
    {
        if ((_flags & ThingActorFlags.DeclaredShutdown) != 0)
        {
            return false;
        }

        _flags |= ThingActorFlags.DeclaredShutdown;
        return true;
    }

    /// <summary>
    /// Retail <c>0x004f37a0</c>, source <c>CThing::StartDieProcess</c>:
    /// set <c>TF_DYING</c> once, then declare shutdown.
    /// </summary>
    public bool StartDieProcess()
    {
        if ((_flags & ThingActorFlags.Dying) != 0)
        {
            return false;
        }

        _flags |= ThingActorFlags.Dying;
        DeclareShutdown();
        return true;
    }

    /// <summary>
    /// The source/retail <c>CActor::Move</c> ordering: capture current pose as
    /// old before publishing the next current pose.
    /// </summary>
    public void AdvancePose(ThingActorPoseSnapshot pose)
    {
        ValidatePose(pose, nameof(pose));
        _oldPose = _currentPose;
        _currentPose = pose;
    }

    /// <summary>
    /// Update current pose without starting another movement transition. A
    /// later phase of the same tick uses this after old pose was captured.
    /// </summary>
    public void UpdateCurrentPose(ThingActorPoseSnapshot pose)
    {
        ValidatePose(pose, nameof(pose));
        _currentPose = pose;
    }

    /// <summary>
    /// Teleport/reset control: collapse old and current pose so presentation
    /// cannot interpolate through an out-of-band relocation.
    /// </summary>
    public void ResetPose(ThingActorPoseSnapshot pose)
    {
        ValidatePose(pose, nameof(pose));
        _currentPose = pose;
        _oldPose = pose;
    }

    public void SetVelocity(SimVector3 velocity) => _velocity = velocity;

    public void AddVelocity(SimVector3 velocity) => _velocity = new SimVector3(
        checked(_velocity.X + velocity.X),
        checked(_velocity.Y + velocity.Y),
        checked(_velocity.Z + velocity.Z));

    /// <summary>
    /// Retail <c>0x00401580</c>, source inline <c>CActor::Stop</c>. Only the
    /// linear <c>mVelocity</c> vector is zeroed.
    /// </summary>
    public void Stop() => _velocity = SimVector3.Zero;

    public void SetAngularVelocity(SimVector3 angularVelocity) =>
        _angularVelocity = angularVelocity;

    /// <summary>
    /// Retail <c>0x004f3470</c> (CThing), source-only CComplexThing lineage
    /// <c>0x80000001</c>, and retail <c>0x00401540</c> (CActor): replace the
    /// stored mask with the supplied subclass bits OR the full actor lineage.
    /// </summary>
    public void SetThingType(uint specificTypeMask) =>
        _thingTypeMask = specificTypeMask | ThingActorTypeMasks.ActorLineage;

    /// <summary>
    /// Retail <c>0x00402000</c>, source <c>CActor::DeclareOnGround</c>.
    /// Event time is supplied as exact single-precision bits; Core owns no
    /// clock.
    /// </summary>
    public void DeclareOnGround(int eventTimeFloatBits) =>
        _lastTimeOnGroundFloatBits = ValidateEventTime(eventTimeFloatBits);

    /// <summary>Retail <c>0x00402010</c>, CActor water-contact timestamp.</summary>
    public void DeclareInWater(int eventTimeFloatBits) =>
        _lastTimeInWaterFloatBits = ValidateEventTime(eventTimeFloatBits);

    /// <summary>Retail <c>0x00402020</c>, CActor object-contact timestamp.</summary>
    public void DeclareOnObject(int eventTimeFloatBits) =>
        _lastTimeOnObjectFloatBits = ValidateEventTime(eventTimeFloatBits);

    private static int ValidateEventTime(int eventTimeFloatBits)
    {
        if (!IsFiniteFloatBits(eventTimeFloatBits))
        {
            throw new ArgumentOutOfRangeException(nameof(eventTimeFloatBits));
        }

        return eventTimeFloatBits;
    }

    private static bool IsFiniteFloatBits(int bits) =>
        float.IsFinite(BitConverter.Int32BitsToSingle(bits));

    private static bool HasFiniteBasis(Level100FloatBasis3Bits basis) =>
        new[]
        {
            basis.Row0X, basis.Row0Y, basis.Row0Z,
            basis.Row1X, basis.Row1Y, basis.Row1Z,
            basis.Row2X, basis.Row2Y, basis.Row2Z,
        }.All(IsFiniteFloatBits);

    private static void ValidatePose(ThingActorPoseSnapshot? pose, string parameterName)
    {
        ArgumentNullException.ThrowIfNull(pose, parameterName);
        if (!HasFiniteBasis(pose.BasisFloatBits))
        {
            throw new ArgumentException(
                "Thing/Actor pose basis must contain finite values.",
                parameterName);
        }
    }
}
