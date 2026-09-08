// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public sealed record RetailFeatureDefinition(string DefinitionName, string MeshName,
    int InvincibleWord, int ProfileWord18, IReadOnlyList<RetailPhysicsFieldInput> Fields);

/// <summary>
/// Feature44ca30 on the six actual iceberg inputs, after preceding Units.
/// The shared water clamp changes only current pose: authored old Z survives.
/// No Unit, AI, animation, sound, damage or later dying transition is invented.
/// </summary>
public sealed class RetailWorld110Feature : RetailWorld110Actor
{
    internal RetailWorld110Feature(RetailWorld110InitialConstruction world, Level100ActorId actorId,
        RetailWorld110InitialActorInput input, RetailInitialMesh mesh, RetailFeatureDefinition definition)
        : base(world, actorId, input, mesh)
    {
        if (input.SerializedThingType != 35 || input.Actor.DefinitionName != definition.DefinitionName ||
            mesh.Name != definition.MeshName || input.Allegiance != 2 || definition.InvincibleWord != 1 ||
            definition.ProfileWord18 != 0)
            throw new NotSupportedException("Unadmitted Feature initializer.");
        Definition = definition;
        InitializeActor(0x00500020, 0x20, 2, false, false);
        world.PublishOccupancyCandidate(this);
        WaterFlagWord = BitConverter.Int32BitsToSingle(PositionFloatBits.Z) < world.Terrain.Heightfield.WaterLevel ? 1 : 0;
    }
    public RetailFeatureDefinition Definition { get; }
    public int Allegiance => Input.Allegiance;
    public int FieldE0 => Definition.ProfileWord18;
    public int FieldF0 => 0;
    public int WaterFlagWord { get; }
}
