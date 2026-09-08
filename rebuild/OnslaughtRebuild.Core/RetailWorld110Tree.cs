// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>Materialized mesh fields, not OBJ or part-bounds approximations.</summary>
public sealed record RetailWorld110TreeMesh(int Variant, string MeshName, string SourceSha256,
    int MeshRadiusFloatBits, IReadOnlyList<int> GlobalBoundingBoxWords)
{
    public float SpatialRadius
    {
        get
        {
            double x = Math.Abs((double)BitConverter.Int32BitsToSingle(GlobalBoundingBoxWords[0])) +
                BitConverter.Int32BitsToSingle(GlobalBoundingBoxWords[4]);
            double y = Math.Abs((double)BitConverter.Int32BitsToSingle(GlobalBoundingBoxWords[1])) +
                BitConverter.Int32BitsToSingle(GlobalBoundingBoxWords[5]);
            return (float)Math.Sqrt(y * y + x * x); // 492bd0..492beb, one final store.
        }
    }
}

/// <summary>
/// Initialized explicit pine in the base-world tree prefix. CTree derives
/// directly from CThing, not CActor. Pristine 74154bfa…7750: Init 4f6080,
/// collision Init 4f6480, persistent readiness 4269b0/426a20. Position is kept
/// in retail float words; millimetre and renderer transforms are not truth.
/// Falling, shutdown and matrix evaluation remain outside this prefix.
/// </summary>
public sealed class RetailWorld110Tree : IRetailMapWhoOwner
{
    private readonly ThingBaseState _thing = new(ThingActorTypeMasks.Thing,
        0x02000020, ThingActorFlags.InMapWho);

    internal RetailWorld110Tree(int identity, int collisionIdentity, int ordinal,
        RetailWorld110TreePlacement placement, RetailWorld110TreeMesh mesh,
        Level100Terrain terrain, Level100ReleasedRandom random, RetailMapWho map,
        RetailEventScheduler events)
    {
        Identity = identity;
        CollisionIdentity = collisionIdentity;
        Ordinal = ordinal;
        Mesh = mesh;
        // Explicit LoadWorld variant suppresses the second, variant-selection
        // draw. FISTP rounds this first draw; 32 is a legal stored result.
        InitialRotationSelector = checked((int)Math.Round(
            (random.Next() % 65536) / 2048.0, map.IntegerRounding));
        int x = HeightCoordinate(placement.PositionXFloatBits);
        int y = HeightCoordinate(placement.PositionYFloatBits);
        float height = (float)((double)terrain.SampleHeightUnitsAtFixed(x, y) * terrain.HeightScale);
        float z = height > terrain.WaterLevel ? terrain.WaterLevel : height;
        PositionFloatBits = new(placement.PositionXFloatBits, placement.PositionYFloatBits,
            BitConverter.SingleToInt32Bits(z));
        MapEntry = map.Add(this, mesh.SpatialRadius);
        if (MapEntry.Sector.Layer < 3) _thing.AddFlags(ThingActorFlags.IsBigThing);
        CollisionHalfHeightFloatBits = BitConverter.SingleToInt32Bits(
            BitConverter.Int32BitsToSingle(mesh.MeshRadiusFloatBits) * 0.5f);
        ReadinessEvent = events.AddEventTimeFromNow(-1, 3000, CollisionIdentity);
        // Registration precedes this immediate scan; world publication follows
        // it. Read actual previous pines and exclude self/mutual mask20.
        map.VisitInitialCollisionNeighbors(MapEntry, entry =>
        {
            if (ReferenceEquals(entry.Owner, this)) return;
            if (entry.Owner is not RetailWorld110Tree other || (other.ThingTypeMask & CollisionMask) == 0)
                throw new NotSupportedException("The base-tree prefix cannot dispatch a non-tree collision pair.");
            InitialRejectedPeerCount++;
        });
        _thing.AddType(0x00800000); // CThing.Init adds renderability after collision Init.
    }

    public int Identity { get; }
    public int CollisionIdentity { get; }
    public int Ordinal { get; }
    public Level100FloatVector3Bits PositionFloatBits { get; }
    public RetailWorld110TreeMesh Mesh { get; }
    public RetailMapWho.Entry MapEntry { get; }
    public uint ThingTypeMask => _thing.TypeMask;
    public ThingActorFlags Flags => _thing.Flags;
    public uint CollisionMask => 0x20;
    public int CollisionMaximumKind => 1;
    public int CollisionRadiusFloatBits => 0x3e4ccccd;
    public int CollisionRadiusSquaredFloatBits => 0x3d23d70b;
    public int CollisionHalfHeightFloatBits { get; }
    public bool CollisionReady { get; private set; }
    public RetailEventAdmission ReadinessEvent { get; }
    public int InitialRejectedPeerCount { get; private set; }
    public int InitialRotationSelector { get; }

    // Init resets the matrix cache. GetMatrix replaces the selector using
    // native-address phase and global67a680; the random selector is NOT a
    // final render yaw. Do not expose an invented identity/rotation matrix.
    public bool MatrixCacheValid => false;
    public bool HasFallingTreeData => false;
    public int InitialFallScalarFloatBits => 0x3fc00000;

    internal void HandleCollisionEvent(RetailEventDispatch item)
    {
        if (item.Listener != CollisionIdentity || item.EventNum != 3000)
            throw new InvalidOperationException("Unsupported tree collision listener event.");
        CollisionReady = true; // 426a20: sets400 only, no scan, RNG or reschedule.
    }

    private static int HeightCoordinate(int bits)
    {
        // 47eb80 uses the bit pattern of this biased float, not an integer
        // cast. Under the admitted nearest-store arithmetic all actual pine
        // XY words agree with floor(x*256), including fractional placements.
        double coordinate = BitConverter.Int32BitsToSingle(bits);
        float biased = (float)((coordinate - BitConverter.Int32BitsToSingle(0x3afffeb0)) + 49152.0);
        return unchecked(BitConverter.SingleToInt32Bits(biased) - 0x47400000);
    }
}
