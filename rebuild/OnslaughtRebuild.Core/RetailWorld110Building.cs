// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// First three Buildings' Init, around the shared Unit/Actor transaction.
/// Pristine74154bfa…7750: Building417190, Unit4f86d0, Actor4011e0.
/// Render/resource caches, damage, frame delivery and complete lifecycle remain open.
/// </summary>
public sealed class RetailWorld110Building : RetailWorld110Unit
{
    internal RetailWorld110Building(RetailWorld110InitialConstruction world,
        Level100ActorId actorId, RetailWorld110InitialActorInput input,
        RetailInitialMesh mesh, RetailUnitConstructionUses uses,
        IReadOnlyList<RetailUnitWeaponDefinition> weaponDefinitions,
        IReadOnlyList<RetailUnitSpawnerDefinition> spawnerDefinitions)
        : base(world, actorId, input, mesh)
    {
        if (input.Actor.DefinitionIdentity is not ("wres:bswd:0000" or "wres:bswd:0001" or "wres:bswd:0002") ||
            input.InternalBehaviourSelector != 7 || mesh.Name != input.Actor.MeshBinding + ".msh")
            throw new NotSupportedException("Unadmitted Building initializer.");
        SegmentControllerIdentity = world.AllocateObjectIdentity();
        MotionControllerIdentity = world.AllocateObjectIdentity();
        Segments = InitializeUnit(uses, weaponDefinitions, spawnerDefinitions,
            0x40100130, 0x08000020, 2, true, false, true)!;
        // Zero-animation meshes: closed/notshut miss; Idle still calls SetAnim.
        SeatOnGround();
        Ai = new(this);
        Animation = new(this, "Idle");
        world.PublishOccupancyCandidate(this);
    }
    public int SegmentControllerIdentity { get; }
    public RetailBuildingSegments Segments { get; }
    public bool HasNotShutAnimation => false;
    public int BuildingState => 3;
    public float LastBuildingUpdateTime => -100;
}
