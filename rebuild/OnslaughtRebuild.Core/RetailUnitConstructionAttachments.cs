// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public sealed record RetailPhysicsFieldInput(int FieldId, string RawHex);
public sealed record RetailUnitConstructionUse(string DefinitionName, string TagName, uint RawCreationFlags)
{
    // The admitted 5115b0 mappings. These are not mesh emitter selectors
    // or the target unit's behavior selector.
    public int TagIndex => TagName switch
    {
        "GunA" => 1,
        "GunB" => 2,
        "SpawnerA" => 10,
        _ => throw new NotSupportedException("Unadmitted Unit attachment tag.")
    };
}
public sealed record RetailUnitConstructionUses(string ActorDefinitionIdentity,
    IReadOnlyList<RetailUnitConstructionUse> WeaponUses, IReadOnlyList<RetailUnitConstructionUse> SpawnerUses);
public sealed record RetailUnitWeaponModeInput(string DefinitionName, int TypeOrdinal,
    IReadOnlyList<RetailPhysicsFieldInput> Fields);
public sealed record RetailUnitWeaponDefinition(string DefinitionName, int TypeOrdinal,
    int ChargeRateFloatBits, IReadOnlyList<int> ChargeSlots, int ConsumptionFloatBits,
    int AmmoStore, int ZoomMode, int AdjustAimWord, IReadOnlyList<RetailPhysicsFieldInput> Fields,
    RetailUnitWeaponModeInput SelectedMode);
public sealed record RetailUnitSpawnerDefinition(string DefinitionName, string TargetUnitDefinitionName,
    int TargetUnitBehaviourSelector, IReadOnlyList<RetailPhysicsFieldInput> Fields);

/// <summary>
/// Shared process-global effect-list node. Unit primary nodes are separately
/// allocated; Weapon nodes are embedded at +14/+1c. Payloads start null.
/// </summary>
public sealed record RetailEffectLink(object Owner, int? OwnerOffset, RetailEffectLink? Next)
{
    public bool HasEffect => false;
}

/// <summary>
/// Admitted successful Weapon construction before Unit's Actor Init. Uses the
/// existing charge and mounted-weapon owners. Does not implement fire, repair,
/// particles or sound. Pristine 74154bfa…7750: 50f6d0,505e00,44a830; exact
/// body/input pins and unwritten-state limits live in the World110 RE owner.
/// </summary>
public sealed class RetailUnitWeapon
{
    internal RetailUnitWeapon(RetailWorld110Unit owner, RetailUnitConstructionUse use,
        RetailUnitWeaponDefinition definition)
    {
        if (use.DefinitionName != definition.DefinitionName || use.TagName is not ("GunA" or "GunB") ||
            definition.ChargeSlots.Count != RetailWeaponChargeTable.LevelCount ||
            definition.ChargeSlots[0] != definition.SelectedMode.TypeOrdinal)
            throw new NotSupportedException("Unadmitted Unit weapon constructor inputs.");
        Identity = owner.World.AllocateObjectIdentity();
        Owner = owner;
        Use = use;
        Definition = definition;
        // The vector constructor visits +14 before +1c; each pushes at head.
        Effect14 = owner.World.AddEffectLink(this, 0x14);
        Effect1C = owner.World.AddEffectLink(this, 0x1c);
        ChargeState = new()
        {
            ChargeRate = BitConverter.Int32BitsToSingle(definition.ChargeRateFloatBits),
            Charge = 0, ReadyAtTime = -200, ReadyToChargeGateActive = true
        };
        for (int slot = 0; slot < RetailWeaponChargeTable.LevelCount; slot++)
            ChargeState.Levels[slot] = definition.ChargeSlots[slot];
        MountedState = new()
        {
            IsActive = 1, AmmoStore = definition.AmmoStore,
            Consumption = BitConverter.Int32BitsToSingle(definition.ConsumptionFloatBits),
            ZoomMode = definition.ZoomMode
        };
    }

    public int Identity { get; }
    public RetailWorld110Unit Owner { get; }
    public RetailUnitConstructionUse Use { get; }
    public RetailUnitWeaponDefinition Definition { get; }
    public RetailUnitWeaponModeInput CurrentMode => Definition.SelectedMode;
    internal RetailWeaponChargeTable ChargeState { get; }
    internal RetailMountedWeapon MountedState { get; }
    public float Charge => ChargeState.Charge;
    public float ReadyAtTime => ChargeState.ReadyAtTime;
    public int ActiveWord => MountedState.IsActive;
    public int ModeIndex => 0;
    public int InitializedWord => 1;
    public int TagIndex => Use.TagIndex;
    public int UnitTagIndex => Use.TagIndex;
    public bool HasTurretPart => false;
    public bool HasBarrelPart => false;
    // Integer-Euler construction is a separate matrix-product route. Its nine
    // stores are identity/+0, not the direct Actor Euler matrix's signed zeros.
    public Level100FloatBasis3Bits BasisFloatBits => new(
        0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000);
    public RetailEffectLink Effect14 { get; }
    public RetailEffectLink Effect1C { get; }
}

/// <summary>
/// Meaningful fields of the private attached-spawner Init copy. The factory's
/// profile and authored pose survive; its inactive/name/target fields do not.
/// Padding and omitted constructor fields are not fabricated as copied data.
/// </summary>
public sealed record RetailAttachedSpawnerInit(RetailWorld110InitialActorInput CopiedFrom)
{
    public string ProfileDefinitionName => CopiedFrom.Actor.DefinitionName!;
    public Level100FloatVector3Bits PositionFloatBits => CopiedFrom.Actor.AuthoredTransform.RetailPositionFloatBits;
    public Level100FloatVector3Bits EulerFloatBits => CopiedFrom.Actor.AuthoredTransform.RetailEulerFloatBits with { Z = 0 };
    // World loading leaves the inactive DCM field at the Init constructor's identity.
    public Level100FloatBasis3Bits OrientationFloatBits => new(
        0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000);
    public int OrientationTypeWord => 0;
    public int MeshNumber => CopiedFrom.MeshNumber;
    public int Allegiance => CopiedFrom.Allegiance;
    public int Target => 0;
    public string Name => string.Empty;
    public string Script => string.Empty;
    public string SpawnScript => CopiedFrom.SpawnScript;
    public int ActiveWord => 1;
    public int AttachScriptsToUnitsWord => CopiedFrom.AttachScriptsToUnitsWord;
}

/// <summary>
/// Attached template from 4e37f0/48dbe0, not CSpawnerThing's separate Init.
/// Does not allocate the target unit or run a spawn cycle, event or RNG draw.
/// </summary>
public sealed class RetailUnitAttachedSpawner
{
    internal RetailUnitAttachedSpawner(RetailWorld110Unit owner, RetailUnitConstructionUse use,
        RetailUnitSpawnerDefinition definition)
    {
        if (use.DefinitionName != definition.DefinitionName || use.TagName != "SpawnerA" ||
            definition.TargetUnitBehaviourSelector != 2)
            throw new NotSupportedException("Unadmitted attached-spawner constructor inputs.");
        Identity = owner.World.AllocateObjectIdentity();
        Owner = owner;
        Use = use;
        Definition = definition;
        Initializer = new(owner.Input);
    }
    public int Identity { get; }
    public RetailWorld110Unit Owner { get; }
    public RetailUnitConstructionUse Use { get; }
    public RetailUnitSpawnerDefinition Definition { get; }
    public RetailAttachedSpawnerInit Initializer { get; }
    public int TagIndex => Use.TagIndex;
    public uint CreationContext => Use.RawCreationFlags;
    public bool MutatedSharedProfile => false; // Selector2 passes 50f680.
}
