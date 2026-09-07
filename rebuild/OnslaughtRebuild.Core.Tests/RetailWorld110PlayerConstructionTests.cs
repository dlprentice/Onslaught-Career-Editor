// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorld110PlayerConstructionTests
{
    [Fact]
    public void ProductionFactory_OwnsObjectsAndThreeDistinctReaderCells()
    {
        var world = RetailWorld110InitialConstruction.Create(Career(),
            RetailWorld110GameSettings.FreshGameDefaults);
        var construction = Assert.IsType<RetailWorld110PlayerConstruction>(world.PlayerConstruction);
        int[] identities = [construction.Start.Identity, construction.BattleEngine.Identity,
            construction.Player.Identity, construction.Start.BattleEngineReaderCellIdentity,
            construction.BattleEngine.PlayerReaderCellIdentity,
            construction.Player.BattleEngineReaderCellIdentity];
        Assert.Equal(6, identities.Distinct().Count());
        Assert.All(identities, identity => Assert.True(identity >= world.Actors.Snapshot.NextActorId));
        Assert.Equal(construction.BattleEngine.Identity,
            construction.ReaderTargetOf(construction.Start.BattleEngineReaderCellIdentity));
        Assert.Equal([construction.Start.BattleEngineReaderCellIdentity],
            construction.ReadersNewestFirst(construction.BattleEngine.Identity));
        Assert.Null(construction.ReaderTargetOf(construction.Player.BattleEngineReaderCellIdentity));
        Assert.Null(construction.ReaderTargetOf(construction.BattleEngine.PlayerReaderCellIdentity));
        Assert.Empty(construction.ReadersNewestFirst(construction.Player.Identity));
        Assert.Null(world.Actors.GetThingRef("Player 1"));
        Assert.Equal(43, world.Actors.Snapshot.Actors.Count);
    }

    [Theory]
    [InlineData(0, 0, 7, 1, 0)]
    [InlineData(0, -1, 7, 1, -1)]
    [InlineData(1, 7, 3, 2, 3)]
    [InlineData(-1, 7, -9, 2, -9)]
    public void Start_TransfersClampedFieldsAndUsesEffectivePlayersConfiguration(
        int invertSides, int firstId, int secondId, int playerNumber, int selectedId)
    {
        var construction = RetailWorld110InitialConstruction.Create(Career(),
            new(invertSides, firstId, secondId)).PlayerConstruction!;
        Assert.Equal("wres:rlwd:0001", construction.Start.AuthoredObjectIdentity);
        Assert.Equal(playerNumber, construction.Start.PlayerNumber);
        Assert.Equal(2, construction.Start.HeightClamp.SampleCallCount);
        Assert.Equal(new Level100FloatVector3Bits(0x43846000, 0x43816800,
            unchecked((int)0xc1199926)), construction.Start.EngineInitFields.PositionBits);
        Assert.Equal(unchecked((int)0xbf04fd8b), construction.Start.EngineInitFields.EulerBits.X);
        Assert.Equal(0, construction.Start.EngineInitFields.Allegiance);
        Assert.Equal(0, construction.Start.EngineInitFields.PlaneModeWord);
        Assert.Equal(selectedId, construction.BattleEngine.InitFields.ConfigurationId);
        Assert.Equal("Aquila Prototype", construction.BattleEngine.Configuration.ConfigurationName);
        // All requested ids clamp through the one-name RLWD table, including
        // invalid ids; the BSWD-only Paladin name must not select fallback Racer.
        Assert.Equal(0x41a00000, construction.BattleEngine.ConfigurationLifeBits);
        Assert.Equal(0x41000000, construction.BattleEngine.ConfigurationEnergyBits);
    }

    [Fact]
    public void Engine_InitializesRealConfigurationStoresAndWalkerScalars()
    {
        var engine = RetailWorld110InitialConstruction.Create(Career(),
            RetailWorld110GameSettings.FreshGameDefaults).PlayerConstruction!.BattleEngine;
        Assert.Equal(2, engine.InitialStateWord);
        Assert.Equal(engine.ConfigurationEnergyBits, engine.InitialShieldsBits);
        Assert.Equal([0, 0, 1, 0, 1, 1], engine.Stores.StoreHeat);
        Assert.Equal([2000f, 100f, 150f, 200f, 100f, 100f], engine.Stores.ConfigurationStoreValue);
        Assert.Equal([2000f, 100f, 0f, 200f, 0f, 0f], engine.Stores.StoreValue);
        Assert.All(engine.Stores.StoreOverheat, value => Assert.Equal(0, value));
    }

    [Fact]
    public void Player_ConsumesCareerGodDwordWithoutExecutingPostLoadPolicyOrHostInit()
    {
        byte[] bytes = Career().ContainerBytes.ToArray();
        // In-memory discriminator over a real baseline; no save file is written.
        BinaryPrimitives.WriteInt32LittleEndian(bytes.AsSpan(0x2496, 4), 0x100);
        var construction = RetailWorld110InitialConstruction.Create(
            RetailCareerSaveCodec.Read(bytes), RetailWorld110GameSettings.FreshGameDefaults)
            .PlayerConstruction!;
        Assert.Equal(0x100, construction.Player.GodWord);
        Assert.Equal(1, construction.Player.PlayerNumber);
        Assert.Equal(1, construction.Player.CurrentViewMode);
        Assert.Equal(1, construction.Player.PreferredControlView);
        Assert.Equal(7, construction.Player.Stats.Count);
        Assert.Equal(5, construction.Player.ThingKillCounts.Count);
        Assert.All(construction.Player.Stats.Concat(construction.Player.ThingKillCounts),
            value => Assert.Equal(0, value));
        Assert.Null(construction.ReaderTargetOf(construction.Player.BattleEngineReaderCellIdentity));
    }

    [Fact]
    public void RepeatedConstruction_UsesIndependentOwnedStorageWithDeterministicIdentities()
    {
        var first = RetailWorld110InitialConstruction.Create(Career(),
            RetailWorld110GameSettings.FreshGameDefaults).PlayerConstruction!;
        var second = RetailWorld110InitialConstruction.Create(Career(),
            RetailWorld110GameSettings.FreshGameDefaults).PlayerConstruction!;
        Assert.NotSame(first.BattleEngine, second.BattleEngine);
        Assert.Equal(first.BattleEngine.Identity, second.BattleEngine.Identity);
        first.BattleEngine.Stores.StoreValue[0] = 12;
        Assert.Equal(2000f, second.BattleEngine.Stores.StoreValue[0]);
        Assert.Null(RetailWorld110InitialConstruction.Create().PlayerConstruction);
    }

    private static RetailCareerSave Career() => RetailCareerSaveCodec.Read(
        File.ReadAllBytes(Path.Combine(AppContext.BaseDirectory, "fixtures", "gold_career_save.bin")));
}
