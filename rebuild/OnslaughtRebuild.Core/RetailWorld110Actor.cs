// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>Original source nodes and complete cached tracks; no reference expansion.</summary>
public sealed record RetailInitialMeshPart(string Name, int Type, int? Reference,
    int? Parent, IReadOnlyList<int> Children, int? Nmic, int NumNmic, int IsNmic,
    Level100FloatVector3Bits HalfExtentFloatBits, IReadOnlyList<int> CachedPositionWords,
    IReadOnlyList<int> CachedOrientationWords);
public sealed record RetailInitialMeshEmitter(string Name, int Selector, int? PartOrdinal);
public sealed record RetailMeshAnimationInput(int SourceOrdinal, string Name, int ModeId,
    int StartFrame, int EndFrame, int FrameDelta, int IncrementFloatBits);
public sealed record RetailInitialMesh(string Name, string SourceSha256,
    int RadiusFloatBits, IReadOnlyList<int> GlobalBoundingBoxWords,
    IReadOnlyList<RetailInitialMeshPart> Parts, IReadOnlyList<RetailInitialMeshEmitter> Emitters,
    int FrameCount, IReadOnlyList<RetailMeshAnimationInput> Animations);

public interface IRetailInitialCollisionOwner : IRetailMapWhoOwner
{
    uint CollisionExclusionMask { get; }
}

/// <summary>
/// Owned common persistent collision Init state. The primary sphere stores
/// the rounded owner-relative centre; the secondary volume binds the actual
/// mesh owner and its fixed/animation flags. Renderer cache allocation and
/// geometry intersection are not implemented by this constructor.
/// Pristine 74154bfa…7750: 4f39c0,426150,4269b0,4f3ac0.
/// </summary>
public sealed class RetailActorCollision
{
    internal RetailActorCollision(RetailWorld110Actor owner, uint exclusionMask,
        int minimumKind, bool fixedMeshTransforms, bool forceObb, RetailEventScheduler events)
    {
        Owner = owner;
        Identity = owner.World.AllocateObjectIdentity();
        PrimarySphereIdentity = owner.World.AllocateObjectIdentity();
        MeshVolumeIdentity = owner.World.AllocateObjectIdentity();
        ExclusionMask = exclusionMask;
        MinimumKind = minimumKind;
        FixedMeshTransforms = fixedMeshTransforms;
        ForceObb = forceObb;
        RadiusFloatBits = owner.Mesh.GlobalBoundingBoxWords[9];
        double radius = BitConverter.Int32BitsToSingle(RadiusFloatBits);
        RadiusSquaredFloatBits = BitConverter.SingleToInt32Bits((float)(radius * radius));
        Level100FloatVector3Bits position = owner.PositionFloatBits;
        // GetCentrePos tests 0x80100 before bit 8. Buildings transform the
        // complete BBOX centre; SAT and Features retain current X/Y. The
        // centre stores precede separate owner-relative subtraction stores.
        var centre = new Level100FloatVector3Bits(owner.Mesh.GlobalBoundingBoxWords[0],
            owner.Mesh.GlobalBoundingBoxWords[1], owner.Mesh.GlobalBoundingBoxWords[2]);
        WorldCentreFloatBits = (owner.ThingTypeMask & 0x80100) != 0
            ? RetailUnitAttachmentPose.TransformPosition(new(position,
                owner.ActorState.RetailPoses!.Current.BasisFloatBits), centre)
            : position with { Z = Store(Read(position.Z) + Read(centre.Z)) };
        OwnerRelativeCentreFloatBits = new(
            Store(Read(WorldCentreFloatBits.X) - Read(position.X)),
            Store(Read(WorldCentreFloatBits.Y) - Read(position.Y)),
            Store(Read(WorldCentreFloatBits.Z) - Read(position.Z)));
        InitialEvent = events.AddEventTimeFromNow(-1, 3000, Identity);
    }
    private static double Read(int bits) => BitConverter.Int32BitsToSingle(bits);
    private static int Store(double value) => BitConverter.SingleToInt32Bits((float)value);
    public RetailWorld110Actor Owner { get; }
    public int Identity { get; }
    public int PrimarySphereIdentity { get; }
    public int MeshVolumeIdentity { get; }
    public uint ExclusionMask { get; }
    public int DesiredKind => 1;
    public int MinimumKind { get; }
    public int MaximumKind => 2;
    public int Response => 2;
    public int Flags => DesiredKind | MinimumKind << 2 | MaximumKind << 4 | Response << 6 | (ForceObb ? 0x200 : 0);
    public bool FixedMeshTransforms { get; }
    public bool ForceObb { get; }
    public bool IgnoreAnimationCollision => false;
    public RetailInitialMesh Mesh => Owner.Mesh;
    public int RadiusFloatBits { get; }
    public int RadiusSquaredFloatBits { get; }
    public Level100FloatVector3Bits WorldCentreFloatBits { get; }
    public Level100FloatVector3Bits OwnerRelativeCentreFloatBits { get; }
    public Level100FloatVector3Bits MeshVolumeOffsetFloatBits => default;
    public RetailEventAdmission InitialEvent { get; }
}

/// <summary>
/// Shared stationary Actor initialization on the admitted World110 load route.
/// Uses the existing registry's Actor/base state, real spatial owners, RNG and
/// scheduler. Derived Init runs before/after this transaction in retail order.
/// Source: actor.cpp:15-40, thing.cpp:40-85,591-632; retail closure in Actor.cpp.md.
/// No frame, restore, damage or full renderer/resource lifecycle is implemented.
/// </summary>
public abstract class RetailWorld110Actor : IRetailInitialCollisionOwner
{
    private readonly ThingActorBaseState _actor;
    protected RetailWorld110Actor(RetailWorld110InitialConstruction world, Level100ActorId actorId,
        RetailWorld110InitialActorInput input, RetailInitialMesh mesh)
    {
        if (input.Actor.AuthoredTransform.RetailEulerFloatBits.Y != 0 ||
            input.Actor.AuthoredTransform.RetailEulerFloatBits.Z != 0 ||
            input.ActiveWord is not (0 or 1) || input.Target != -1 ||
            !string.IsNullOrEmpty(input.Actor.ScriptName) || input.SpawnScript.Length != 0)
            throw new NotSupportedException("Unadmitted stationary Actor initializer.");
        World = world;
        ActorId = actorId;
        Identity = world.ActorWorldIdentities[actorId];
        Input = input;
        Mesh = mesh;
        _actor = world.Actors.GetConstructionState(actorId);
    }

    protected void InitializeActor(uint specificTypeMask, uint collisionMask, int minimumCollisionKind,
        bool fixedMeshTransforms, bool forceObb)
    {
        Level100FloatVector3Bits authored = Input.Actor.AuthoredTransform.RetailPositionFloatBits;
        // Admitted yaw-only sine/cosine stores are checked against native x87.
        // Direct Euler additionally retains the negative zero at row2x.
        var basis = Input.Actor.AuthoredTransform.RetailBasisFloatBits with { Row2X = int.MinValue };
        var pose = new RetailActorPoseSnapshot(authored, basis);
        _actor.BeginRetailInitialization(pose, pose, specificTypeMask);
        if (Input.Actor.Name.Length != 0) World.PublishNamedActor(this);
        float ground = RetailWorldTerrain.SampleRetailHeight(World.Terrain.Heightfield, authored);
        if (BitConverter.Int32BitsToSingle(authored.Z) > ground)
            _actor.TeleportRetailPosition(authored with { Z = BitConverter.SingleToInt32Bits(ground) });
        // Unlike Teleport, the water clamp changes CURRENT position only.
        if (BitConverter.Int32BitsToSingle(PositionFloatBits.Z) > World.Terrain.Heightfield.WaterLevel)
            _actor.SetRetailPosition(PositionFloatBits with
            { Z = BitConverter.SingleToInt32Bits(World.Terrain.Heightfield.WaterLevel) });
        MapEntry = World.MapWho!.Add(this, RetailMapWho.MeshSpatialRadius(Mesh.GlobalBoundingBoxWords));
        if (MapEntry.Sector.Layer < 3)
        {
            World.PublishBigThing(this);
            _actor.AddPublicationFlags(ThingActorFlags.IsBigThing);
        }
        Collision = new(this, collisionMask, minimumCollisionKind, fixedMeshTransforms, forceObb, World.Events!);
        World.MapWho.VisitInitialCollisionNeighbors(MapEntry, entry =>
        {
            if (ReferenceEquals(entry.Owner, this)) return;
            if ((entry.Owner.ThingTypeMask & CollisionExclusionMask) != 0)
                InitialRejectedPeerCount++;
            else if (entry.Owner is IRetailInitialCollisionOwner peer && (ThingTypeMask & peer.CollisionExclusionMask) != 0)
            {
                InitialRejectedPeerCount++;
                InitialRejectedByPeerMaskCount++;
            }
            else throw new NotSupportedException("Unadmitted eligible initial Actor collision pair.");
        });
        _actor.AddPublishedType(0x00800000);
        World.PublishInitializedThing(this);
        MovePhase = World.ReleasedRandom!.Next() % 1;
        _actor.SetRetailMotion(BitConverter.SingleToInt32Bits(World.Events!.Time), 1);
        MoveEvent = World.Events.AddEvent(3000, Identity, -1);
    }

    protected void SeatOnGround()
    {
        float ground = RetailWorldTerrain.SampleRetailHeight(World.Terrain.Heightfield, PositionFloatBits);
        _actor.SetRetailPosition(PositionFloatBits with { Z = BitConverter.SingleToInt32Bits(ground) });
        _actor.CopyRetailPositionToOld();
        if (ground > World.Terrain.Heightfield.WaterLevel)
            _actor.TeleportRetailPosition(PositionFloatBits with
            { Z = BitConverter.SingleToInt32Bits(World.Terrain.Heightfield.WaterLevel) });
    }

    internal RetailWorld110InitialConstruction World { get; }
    public Level100ActorId ActorId { get; }
    public int Identity { get; }
    public RetailWorld110InitialActorInput Input { get; }
    public RetailInitialMesh Mesh { get; }
    public ThingActorBaseStateSnapshot ActorState => _actor.Snapshot;
    public Level100FloatVector3Bits PositionFloatBits => _actor.RetailPoses.Current.PositionFloatBits;
    public uint ThingTypeMask => _actor.Snapshot.ThingTypeMask;
    public RetailMapWho.Entry MapEntry { get; private set; } = null!;
    public RetailActorCollision Collision { get; private set; } = null!;
    public uint CollisionExclusionMask => Collision.ExclusionMask;
    public int CollisionFlags => Collision.Flags;
    public int CollisionDesiredKind => Collision.DesiredKind;
    public int CollisionMinimumKind => Collision.MinimumKind;
    public int CollisionMaximumKind => Collision.MaximumKind;
    public int CollisionResponse => Collision.Response;
    public int InitialRejectedPeerCount { get; private set; }
    public int InitialRejectedByPeerMaskCount { get; private set; }
    public int MovePhase { get; private set; }
    public int MoveCountdown => _actor.Snapshot.RetailMotion!.MoveCountdown;
    public RetailEventAdmission MoveEvent { get; private set; }
}
