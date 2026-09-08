// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public enum RetailUnitAiKind { Warspite, RepairPad }

public sealed class RetailUnitAi
{
    private readonly RetailActiveReaderGraph _readers;
    internal RetailUnitAi(RetailWorld110Unit owner)
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
        _readers.SetReader(TargetReaderCell24, null);
        _readers.SetReader(SpawnedByReaderCell28, null);
        InitialEvent = owner.World.Events!.AddEvent(3000, Identity, owner.World.Events.Time);
        Kind = owner.Input.Actor.DefinitionName!.Equals("Forseti Repair Pad", StringComparison.OrdinalIgnoreCase)
            ? RetailUnitAiKind.RepairPad : RetailUnitAiKind.Warspite;
    }
    public RetailWorld110Unit Owner { get; }
    public int Identity { get; }
    public int ReaderCell0C { get; }
    public int TargetReaderCell24 { get; }
    public int SpawnedByReaderCell28 { get; }
    public int? TargetIdentity => _readers.TargetOf(TargetReaderCell24);
    public int? SpawnedByIdentity => _readers.TargetOf(SpawnedByReaderCell28);
    public int State => 1;
    public RetailUnitAiKind Kind { get; }
    public RetailEventAdmission InitialEvent { get; }
}

/// <summary>Fresh 4046d0/404860 state; metadata lookup does not evaluate a pose.</summary>
public sealed class RetailUnitAnimation
{
    internal RetailUnitAnimation(RetailWorld110Unit owner, string name)
    {
        Owner = owner;
        Identity = owner.World.AllocateObjectIdentity();
        InitialEvent = owner.World.Events!.AddEvent(3000, Identity, -1);
        Definition = owner.Mesh.Animations.FirstOrDefault(animation =>
            animation.Name.Equals(name, StringComparison.OrdinalIgnoreCase));
        if (Definition is not null && Definition.IncrementFloatBits != 0)
            throw new NotSupportedException("Unadmitted initial animation rate.");
    }
    public RetailWorld110Unit Owner { get; }
    public int Identity { get; }
    public RetailMeshAnimationInput? Definition { get; }
    public int Mode => Definition?.ModeId ?? -1;
    public int RealIndex => Definition?.SourceOrdinal ?? -1;
    public int Frame => 0;
    public bool ForceLoop => true;
    public float Increment => 1;
    public RetailEventAdmission InitialEvent { get; }
}

/// <summary>
/// Shared Unit4f86d0 transaction around Actor Init for admitted Buildings and
/// the first Cannon. No child units, Dust/Vent/Thruster emission, frame delivery
/// or fire control is synthesized. Their exact profiles disable those arms.
/// </summary>
public abstract class RetailWorld110Unit : RetailWorld110Actor
{
    protected RetailWorld110Unit(RetailWorld110InitialConstruction world, Level100ActorId actorId,
        RetailWorld110InitialActorInput input, RetailInitialMesh mesh) : base(world, actorId, input, mesh) { }

    protected RetailBuildingSegments? InitializeUnit(RetailUnitConstructionUses uses,
        IReadOnlyList<RetailUnitWeaponDefinition> weapons, IReadOnlyList<RetailUnitSpawnerDefinition> spawners,
        uint specificTypeMask, uint collisionMask, int minimumCollisionKind,
        bool fixedMeshTransforms, bool forceObb, bool createSegments)
    {
        if (uses.ActorDefinitionIdentity != Input.Actor.DefinitionIdentity || Input.Allegiance != 0)
            throw new NotSupportedException("Unadmitted Unit initialization profile.");
        Weapons = Array.AsReadOnly(uses.WeaponUses.Select(use => new RetailUnitWeapon(this, use,
            weapons.Single(definition => definition.DefinitionName == use.DefinitionName))).ToArray());
        Spawners = Array.AsReadOnly(uses.SpawnerUses.Select(use => new RetailUnitAttachedSpawner(this, use,
            spawners.Single(definition => definition.DefinitionName == use.DefinitionName))).ToArray());
        InitializeActor(specificTypeMask, collisionMask, minimumCollisionKind, fixedMeshTransforms, forceObb);
        PrimaryEffect = World.AddEffectLink(this, null);
        World.PublishUnit(this);
        Allegiance = Input.Allegiance;
        RetailBuildingSegments? segments = createSegments
            ? new(Mesh, BitConverter.Int32BitsToSingle(Input.LifeFloatBits!.Value),
                World.AllocateObjectIdentity, World.PublishSegment) : null;
        World.MarkUnitDefinitionUsed(Input.Actor.DefinitionName!);
        World.IncrementUnitCount(Allegiance, Input.InternalBehaviourSelector!.Value);
        World.PublishFactionUnit(this);
        UnitEvent = World.Events!.AddEvent(4003, Identity, -1);
        return segments;
    }

    public IReadOnlyList<RetailUnitWeapon> Weapons { get; private set; } = [];
    public IReadOnlyList<RetailUnitAttachedSpawner> Spawners { get; private set; } = [];
    public int ActiveWord => Input.ActiveWord;
    public int FireControlEnabledWord => 0;
    public int RepairAiFlagWord => Ai.Kind == RetailUnitAiKind.RepairPad ? 1 : 0;
    public int Allegiance { get; private set; }
    public int MotionControllerIdentity { get; protected set; }
    public RetailEffectLink PrimaryEffect { get; private set; } = null!;
    public RetailEventAdmission UnitEvent { get; private set; }
    public RetailUnitAi Ai { get; protected set; } = null!;
    public RetailUnitAnimation Animation { get; protected set; } = null!;
    public int AnimationMode => Animation.Mode;
    public int AnimationFrame => Animation.Frame;
    public bool AnimationForceLoop => Animation.ForceLoop;
    public float AnimationIncrement => Animation.Increment;
}
