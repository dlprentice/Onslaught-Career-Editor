// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailMapWhoTests
{
    private sealed class Thing(int identity, float x, float y) : IRetailMapWhoOwner
    {
        public int Identity { get; } = identity;
        public Level100FloatVector3Bits PositionFloatBits { get; set; } = Position(x, y);
        public uint ThingTypeMask { get; set; } = ThingActorTypeMasks.Thing;
    }
    private static Level100FloatVector3Bits Position(float x, float y) =>
        new(BitConverter.SingleToInt32Bits(x), BitConverter.SingleToInt32Bits(y), 0);

    private static int[] SectorOwners(RetailMapWho map, RetailMapWhoSector sector)
    {
        var owners = new List<int>();
        for (var entry = map.FirstInSector(sector); entry is not null; entry = map.NextInSector())
            owners.Add(entry.Owner.Identity);
        return owners.ToArray();
    }

    [Fact]
    public void SortAfterLoad_RotatesAnAllTreeSectorAndPreservesTheSharedCursor()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        var first = map.Add(new Thing(1, 20, 20) { ThingTypeMask = 0x02800021 }, 1);
        map.Add(new Thing(2, 20, 20) { ThingTypeMask = 0x02800021 }, 1);
        var third = map.Add(new Thing(3, 20, 20) { ThingTypeMask = 0x02800021 }, 1);
        Assert.Same(third, map.FirstInSector(first.Sector));
        map.SortAfterLoad();
        Assert.Equal(2, map.NextInSector()!.Owner.Identity); // Still follows entry3.
        Assert.Equal(new[] { 1, 3, 2 }, SectorOwners(map, first.Sector));
        map.SortAfterLoad();
        Assert.Equal(new[] { 2, 1, 3 }, SectorOwners(map, first.Sector));
        Assert.Equal(3, map.Count);
    }

    [Fact]
    public void SortAfterLoad_KeepsOriginalTailAheadOfMovedTreesAndRepairsBothLinks()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        var entries = new Dictionary<int, RetailMapWho.Entry>();
        for (int id = 5; id >= 1; id--)
            entries[id] = map.Add(new Thing(id, 20, 20)
                { ThingTypeMask = id % 2 != 0 ? 0x02000001u : 0x80000003u }, 1);
        var sector = entries[1].Sector;
        map.SortAfterLoad();
        Assert.Equal(new[] { 2, 4, 5, 1, 3 }, SectorOwners(map, sector));
        Assert.All(entries.Values, entry =>
        {
            Assert.True(entry.IsRegistered);
            Assert.Equal(sector, entry.Sector);
        });
        // These operations use the repaired Previous pointers as well as Next.
        map.Remove(entries[4]);
        Assert.True(map.UpdatePosition(entries[1], Position(100, 100)));
        Assert.Equal(new[] { 2, 5, 3 }, SectorOwners(map, sector));
        Assert.Equal(new[] { 1 }, SectorOwners(map, entries[1].Sector));
        Assert.Equal(4, map.Count);
    }

    [Fact]
    public void SortAfterLoad_VisitsFourFinerLayersAndLeavesLayerZeroUntouched()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        float[] radii = [32, 16, 8, 4, 1];
        var sectors = new RetailMapWhoSector[5];
        for (int layer = 0; layer < 5; layer++)
            for (int offset = 1; offset <= 2; offset++)
                sectors[layer] = map.Add(new Thing(layer * 2 + offset, 20, 20)
                    { ThingTypeMask = 0x02000001 }, radii[layer]).Sector;
        map.SortAfterLoad();
        Assert.Equal(new[] { 2, 1 }, SectorOwners(map, sectors[0]));
        for (int layer = 1; layer < 5; layer++)
        {
            Assert.Equal(layer, sectors[layer].Layer);
            Assert.Equal(new[] { layer * 2 + 1, layer * 2 + 2 }, SectorOwners(map, sectors[layer]));
        }
        Assert.Equal(10, map.Count);
    }

    [Fact]
    public void SortAfterLoad_PreservesEmptySingletonAndNonTreeSectors()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        map.SortAfterLoad();
        var single = map.Add(new Thing(1, 100, 100) { ThingTypeMask = 0x02000001 }, 1);
        var ordinary = map.Add(new Thing(2, 20, 20) { ThingTypeMask = 0x20 }, 1);
        map.Add(new Thing(3, 20, 20), 1);
        map.SortAfterLoad();
        Assert.Equal(new[] { 1 }, SectorOwners(map, single.Sector));
        Assert.Equal(new[] { 3, 2 }, SectorOwners(map, ordinary.Sector));
        Assert.Equal(3, map.Count);
    }

    [Fact]
    public void IntegerRounding_IsExplicitAndChangesAnActualPineSector()
    {
        var nearest = new RetailMapWho(MidpointRounding.ToEven);
        var floor = new RetailMapWho(MidpointRounding.ToNegativeInfinity);
        var pine = Position(330.23974609375f, 247.9563446044922f);
        Assert.Equal(new(41, 31, 4), nearest.WorldToSector(pine, 4));
        Assert.Equal(new(41, 30, 4), floor.WorldToSector(pine, 4));
        Assert.Equal(new(0, 63, 4), nearest.WorldToSector(Position(-10, 600), 4));
        // FISTP ties-even before shifting; floor(x/cell) is a different law.
        Assert.Equal(new(1, 0, 4), nearest.WorldToSector(Position(7.5f, 6.5f), 4));
        Assert.Throws<ArgumentOutOfRangeException>(() => new RetailMapWho(MidpointRounding.AwayFromZero));
    }

    [Fact]
    public void Radius_UsesStoredInflationEqualityAndAllFiveLayers()
    {
        Assert.Equal(new[] { 4, 3, 2, 1, 0, 0 },
            new[] { 1f, 4f, 8f, 16f, 32f, 1000f }.Select(RetailMapWho.GetLevelForRadius));
        // This quotient times float2.01 stores exactly8.0f; equality is fine.
        float edge = 8f / BitConverter.Int32BitsToSingle(0x4000a3d7);
        Assert.Equal(4, RetailMapWho.GetLevelForRadius(edge));
        // The very next radius still rounds its diameter to8.0f; comparing
        // the unspilled double product would select the wrong layer.
        Assert.Equal(4, RetailMapWho.GetLevelForRadius(MathF.BitIncrement(edge)));
        Assert.Equal(3, RetailMapWho.GetLevelForRadius(MathF.BitIncrement(MathF.BitIncrement(edge))));
        Assert.Throws<ArgumentOutOfRangeException>(() => RetailMapWho.GetLevelForRadius(float.NaN));
    }

    [Fact]
    public void Membership_UsesHeadInsertionAndSameSectorUpdatesKeepOrder()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        var a = new Thing(1, 10, 10);
        var b = new Thing(2, 11, 11);
        var first = map.Add(a, 1);
        var second = map.Add(b, 1);
        Assert.Same(second, map.FirstInSector(first.Sector));
        Assert.Same(first, map.NextInSector());
        a.PositionFloatBits = Position(12, 12);
        Assert.False(map.UpdatePosition(first));
        Assert.Same(second, map.FirstInSector(first.Sector));
        a.PositionFloatBits = Position(20, 20);
        Assert.True(map.UpdatePosition(first));
        Assert.Equal(new(2, 2, 4), first.Sector);
        Assert.Same(first, map.FirstInSector(first.Sector));
        Assert.Same(a, first.Owner);
        Assert.Same(second, map.FirstInSector(second.Sector));
        Assert.Null(map.NextInSector());
        map.Remove(first);
        Assert.False(first.IsRegistered);
        Assert.Equal(new(2, 2, 4), first.Sector); // Remove does not invalidate.
        Assert.Equal(1, map.Count);
        Assert.Throws<ArgumentException>(() => map.Remove(first));
        Assert.Throws<ArgumentException>(() => map.Add(new Thing(2, 40, 40), 1));
    }

    [Fact]
    public void Scan_VisitsChildrenInSlotOrderBeforeParentThenCoarserLayers()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        var parent = map.Add(new Thing(1, 20, 20), 4); // Layer3, sector1,1.
        map.Add(new Thing(2, 18, 18), 1);
        map.Add(new Thing(3, 26, 18), 1);
        map.Add(new Thing(4, 18, 26), 1);
        map.Add(new Thing(5, 26, 26), 1);
        map.Add(new Thing(6, 20, 20), 8); // Layer2, sector0,0.
        map.Add(new Thing(7, 500, 500), 1); // Outside this neighborhood.
        var seen = new List<int>();
        map.VisitInitialCollisionNeighbors(parent, entry => seen.Add(entry.Owner.Identity));
        Assert.Equal(new[] { 2, 3, 4, 5, 1, 6 }, seen);
    }

    [Fact]
    public void Scan_ReadsNextAfterCallbackAndRemovedCursorRetainsItsLinks()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        var a = map.Add(new Thing(1, 20, 20), 1);
        var b = map.Add(new Thing(2, 20, 20), 1);
        var c = map.Add(new Thing(3, 20, 20), 1);
        var seen = new List<int>();
        map.VisitInitialCollisionNeighbors(a, entry =>
        {
            seen.Add(entry.Owner.Identity);
            if (ReferenceEquals(entry, c)) map.Remove(b);
        });
        Assert.Equal(new[] { 3, 1 }, seen); // Captured candidates would include2.
        Assert.Same(c, map.FirstInSector(c.Sector));
        map.Remove(c);
        Assert.Same(a, map.NextInSector()); // Removed current still links to1.
        Assert.Same(a, map.FirstInSector(a.Sector));
    }

    [Fact]
    public void NestedSectorQuery_OverwritesTheSharedCursor()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        var a = map.Add(new Thing(1, 20, 20), 1);
        var b = map.Add(new Thing(2, 20, 20), 1);
        var far = map.Add(new Thing(3, 500, 500), 1);
        var seen = new List<int>();
        map.VisitInitialCollisionNeighbors(a, entry =>
        {
            seen.Add(entry.Owner.Identity);
            if (ReferenceEquals(entry, b)) Assert.Same(far, map.FirstInSector(far.Sector));
        });
        Assert.Equal(new[] { 2 }, seen); // Independent enumerators wrongly visit1.
    }

    [Fact]
    public void UpdateCanUseAnExplicitOldPositionWithoutRewritingTheOwner()
    {
        var map = new RetailMapWho(MidpointRounding.ToEven);
        var owner = new Thing(1, 20, 20);
        var entry = map.Add(owner, 1);
        Assert.True(map.UpdatePosition(entry, Position(50, 50)));
        Assert.Equal(new RetailMapWhoSector(6, 6, 4), entry.Sector);
        Assert.Equal(Position(20, 20), owner.PositionFloatBits);
    }
}
