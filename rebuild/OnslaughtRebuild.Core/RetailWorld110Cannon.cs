// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public sealed record RetailGroundUnitDefinition(string DefinitionName, int FieldC8FloatBits,
    int FieldD0FloatBits, IReadOnlyList<RetailPhysicsFieldInput> Fields);

public sealed record RetailCannonTerrainGuide(int Identity, RetailWorld110Cannon Owner,
    Level100FloatVector3Bits PositionFloatBits)
{
    public int Field04 => 0;
    public int Field1C => 0;
}

public sealed record RetailCannonMotionController(int Identity, RetailWorld110Cannon Owner)
{
    public bool UsesOwnerRenderInterface => true;
    public int Field04 => 0;
    public int Field0CFloatBits => unchecked((int)0xc479c000);
    public int Field10FloatBits => unchecked((int)0xc479c000);
}

/// <summary>
/// SAT Cannon41b1a0/GroundUnit47c730 around shared Unit initialization.
/// Its inactive animation is scheduled before AI. This does not implement
/// aiming, firing, guide motion, animation delivery or renderer/resource caches.
/// </summary>
public sealed class RetailWorld110Cannon : RetailWorld110Unit
{
    internal RetailWorld110Cannon(RetailWorld110InitialConstruction world, Level100ActorId actorId,
        RetailWorld110InitialActorInput input, RetailInitialMesh mesh, RetailUnitConstructionUses uses,
        IReadOnlyList<RetailUnitWeaponDefinition> weapons, IReadOnlyList<RetailUnitSpawnerDefinition> spawners,
        RetailGroundUnitDefinition groundDefinition) : base(world, actorId, input, mesh)
    {
        if (input.Actor.DefinitionIdentity != "wres:bswd:0003" || input.InternalBehaviourSelector != 4 ||
            input.ActiveWord != 0 || groundDefinition.DefinitionName != input.Actor.DefinitionName)
            throw new NotSupportedException("Unadmitted Cannon initializer.");
        GroundDefinition = groundDefinition;
        InitializeUnit(uses, weapons, spawners, 0x40040230, 0x20, 0, false, true, false);
        Animation = new(this, "Inactive");
        TerrainGuide = new(world.AllocateObjectIdentity(), this, PositionFloatBits);
        Ai = new(this);
        MotionControllerIdentity = world.AllocateObjectIdentity();
        MotionController = new(MotionControllerIdentity, this);
        world.PublishOccupancyCandidate(this);
        WaterFlagWord = world.Terrain.Heightfield.WaterLevel <= BitConverter.Int32BitsToSingle(PositionFloatBits.Z) ? 1 : 0;
    }
    public RetailGroundUnitDefinition GroundDefinition { get; }
    public int Field100FloatBits => GroundDefinition.FieldC8FloatBits;
    public int Field104FloatBits => GroundDefinition.FieldC8FloatBits;
    public int Field108FloatBits => GroundDefinition.FieldD0FloatBits;
    public RetailCannonTerrainGuide TerrainGuide { get; }
    public RetailCannonMotionController MotionController { get; }
    public int State260 => 1;
    public int State264 => 0;
    public Level100FloatVector3Bits Fields12CTo134 => default;
    public int FieldF4FloatBits => 0;
    public int WaterFlagWord { get; }
}
