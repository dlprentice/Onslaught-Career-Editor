// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>One real scheduled subowner; its identity is not the Actor identity.</summary>
public sealed record RetailBuildingListener(int Identity, RetailWorld110Building Owner,
    RetailEventAdmission InitialEvent);

public sealed class RetailBuildingAi
{
    private readonly RetailActiveReaderGraph _readers;
    internal RetailBuildingAi(RetailWorld110Building owner, RetailEventScheduler events)
    {
        Owner = owner;
        _readers = owner.World.Readers;
        Identity = owner.World.AllocateObjectIdentity();
        ReaderCell0C = owner.World.AllocateObjectIdentity();
        TargetReaderCell24 = owner.World.AllocateObjectIdentity();
        SpawnedByReaderCell28 = owner.World.AllocateObjectIdentity();
        _readers.CreateReaderCell(ReaderCell0C);
        _readers.CreateReaderCell(TargetReaderCell24);
        _readers.CreateReaderCell(SpawnedByReaderCell28);
        // The admitted target -1 is normalized to null by LoadWorld; spawnedBy
        // is null. Null-to-null SetReader is a no-op, including reverse sets.
        _readers.SetReader(TargetReaderCell24, null);
        _readers.SetReader(SpawnedByReaderCell28, null);
        InitialEvent = events.AddEvent(3000, Identity, events.Time);
    }
    public RetailWorld110Building Owner { get; }
    public int Identity { get; }
    public int ReaderCell0C { get; }
    public int TargetReaderCell24 { get; }
    public int SpawnedByReaderCell28 { get; }
    public int? TargetIdentity => _readers.TargetOf(TargetReaderCell24);
    public int? SpawnedByIdentity => _readers.TargetOf(SpawnedByReaderCell28);
    public int State => 1;
    public RetailEventAdmission InitialEvent { get; }
}

public sealed record RetailBuildingEffectLink(RetailWorld110Building Owner,
    RetailBuildingEffectLink? Next)
{
    public bool HasEffect => false;
}

/// <summary>
/// Core state at the first Control Tower's successful Init return. Uses the
/// existing Actor allocation, real preceding pines, shared RNG and event pool.
/// No frame delivery, damage, renderer cache allocation or resource loading is
/// implemented here. Geometry is the explicitly preloaded materialized mesh.
/// Pristine 74154bfa…7750: Building417190, Unit4f86d0, Actor4011e0,
/// Thing4f34a0; contracts and body pins are in the World110 RE owner.
/// </summary>
public sealed class RetailWorld110Building : IRetailMapWhoOwner
{
    private readonly ThingActorBaseState _actor;

    internal RetailWorld110Building(RetailWorld110InitialConstruction world,
        Level100ActorId actorId, RetailWorld110InitialActorInput input,
        RetailBuildingMesh mesh, RetailEventScheduler events)
    {
        if (input.Actor.DefinitionIdentity != "wres:bswd:0000" ||
            input.Actor.DefinitionName != "Control Tower" || input.InternalBehaviourSelector != 7 ||
            input.Actor.AuthoredTransform.RetailEulerFloatBits != default ||
            input.Allegiance != 0 || input.ActiveWord != 1 || input.Target != -1 ||
            !string.IsNullOrEmpty(input.Actor.ScriptName) || input.SpawnScript.Length != 0)
            throw new NotSupportedException("Only the admitted first Control Tower Init is supported.");

        World = world;
        ActorId = actorId;
        Identity = world.ActorWorldIdentities[actorId];
        Input = input;
        Mesh = mesh;
        _actor = world.Actors.GetConstructionState(actorId);
        SegmentControllerIdentity = world.AllocateObjectIdentity();
        MotionControllerIdentity = world.AllocateObjectIdentity();
        Level100FloatVector3Bits authored = input.Actor.AuthoredTransform.RetailPositionFloatBits;
        // Actual finite zero-Euler stores preserve the two negative zeros.
        var basis = new Level100FloatBasis3Bits(0x3f800000, int.MinValue, 0,
            0, 0x3f800000, 0, int.MinValue, 0, 0x3f800000);
        var pose = new RetailActorPoseSnapshot(authored, basis);
        _actor.BeginRetailInitialization(pose, pose, 0x40100130);
        world.PublishNamedBuilding(this); // ComplexThing's first virtual call.

        float ground = RetailWorldTerrain.SampleRetailHeight(world.Terrain.Heightfield, authored);
        if (BitConverter.Int32BitsToSingle(authored.Z) > ground)
            _actor.TeleportRetailPosition(authored with { Z = BitConverter.SingleToInt32Bits(ground) });
        if (BitConverter.Int32BitsToSingle(PositionFloatBits.Z) > world.Terrain.Heightfield.WaterLevel)
            _actor.SetRetailPosition(PositionFloatBits with
            { Z = BitConverter.SingleToInt32Bits(world.Terrain.Heightfield.WaterLevel) });

        MapEntry = world.MapWho!.Add(this, RetailMapWho.MeshSpatialRadius(mesh.GlobalBoundingBoxWords));
        if (MapEntry.Sector.Layer < 3) _actor.AddPublicationFlags(ThingActorFlags.IsBigThing);
        int collisionIdentity = world.AllocateObjectIdentity();
        Collision = new(collisionIdentity, this, events.AddEventTimeFromNow(-1, 3000, collisionIdentity));
        world.MapWho.VisitInitialCollisionNeighbors(MapEntry, entry =>
        {
            if (ReferenceEquals(entry.Owner, this)) return;
            // Persistent426900 rejects these actual prior owners before
            // readiness, pair dispatch and all narrowphase/event callbacks.
            if ((entry.Owner.ThingTypeMask & CollisionExclusionMask) == 0)
                throw new NotSupportedException("Unadmitted eligible Building collision pair.");
            InitialRejectedPeerCount++;
        });
        _actor.AddPublishedType(0x00800000);
        world.PublishInitializedThing(this);

        // Actor Init always consumes a draw, even when multiplier == 1.
        MovePhase = world.ReleasedRandom!.Next() % 1;
        _actor.SetRetailMotion(BitConverter.SingleToInt32Bits(events.Time), 1);
        MoveEvent = events.AddEvent(3000, Identity, -1);
        PrimaryEffect = world.AddPrimaryEffect(this);
        world.PublishUnit(this);
        Allegiance = input.Allegiance;
        Segments = new(mesh, BitConverter.Int32BitsToSingle(input.LifeFloatBits!.Value),
            world.AllocateObjectIdentity, world.PublishSegment);
        world.MarkUnitDefinitionUsed(input.Actor.DefinitionName!);
        world.IncrementUnitCount(Allegiance, input.InternalBehaviourSelector.Value);
        world.PublishFactionUnit(this);
        UnitEvent = events.AddEvent(4003, Identity, -1);

        // closed/notshut/Idle all miss this zero-animation primary mesh.
        // +48 ground snap copies position only, then clamps both Z words.
        _actor.SetRetailPosition(PositionFloatBits with { Z = BitConverter.SingleToInt32Bits(ground) });
        _actor.CopyRetailPositionToOld();
        if (ground > world.Terrain.Heightfield.WaterLevel)
            _actor.TeleportRetailPosition(PositionFloatBits with
            { Z = BitConverter.SingleToInt32Bits(world.Terrain.Heightfield.WaterLevel) });
        Ai = new(this, events);
        int animationIdentity = world.AllocateObjectIdentity();
        Animation = new(animationIdentity, this, events.AddEvent(3000, animationIdentity, -1));
        world.PublishOccupancyCandidate(this);
    }

    internal RetailWorld110InitialConstruction World { get; }
    public Level100ActorId ActorId { get; }
    public int Identity { get; }
    public RetailWorld110InitialActorInput Input { get; }
    public RetailBuildingMesh Mesh { get; }
    public ThingActorBaseStateSnapshot ActorState => _actor.Snapshot;
    public Level100FloatVector3Bits PositionFloatBits => _actor.RetailPoses.Current.PositionFloatBits;
    public uint ThingTypeMask => _actor.Snapshot.ThingTypeMask;
    public RetailMapWho.Entry MapEntry { get; }
    public RetailBuildingListener Collision { get; }
    public uint CollisionExclusionMask => 0x08000020;
    public int CollisionFlags => 0x0a9; // Fixed-transform/delayed, ready400 cleared.
    public int CollisionDesiredKind => 1;
    public int CollisionMinimumKind => 2;
    public int CollisionMaximumKind => 2;
    public int CollisionResponse => 2;
    public int InitialRejectedPeerCount { get; private set; }
    public int MovePhase { get; }
    public int MoveCountdown => _actor.Snapshot.RetailMotion!.MoveCountdown;
    public RetailEventAdmission MoveEvent { get; }
    public RetailEventAdmission UnitEvent { get; }
    public int Allegiance { get; }
    public int SegmentControllerIdentity { get; }
    public int MotionControllerIdentity { get; }
    public RetailBuildingSegments Segments { get; }
    public RetailBuildingEffectLink PrimaryEffect { get; }
    public RetailBuildingAi Ai { get; }
    public RetailBuildingListener Animation { get; }
    public int AnimationMode => -1;
    public int AnimationFrame => 0;
    public bool AnimationForceLoop => true;
    public float AnimationIncrement => 1;
    public bool HasNotShutAnimation => false;
    public int BuildingState => 3;
    public float LastBuildingUpdateTime => -100;
}
