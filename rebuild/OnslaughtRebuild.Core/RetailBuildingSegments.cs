// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public enum RetailBuildingSegmentKind { Core, Swap, Extra, X1 }

/// <summary>
/// One allocated segment. Mesh aliases share this owner; children are linked
/// at the head. Unwritten allocator bytes and later damage logic are excluded.
/// </summary>
public sealed class RetailBuildingSegment
{
    private readonly LinkedList<RetailBuildingSegment> _children = [];
    internal RetailBuildingSegment(int identity, int partOrdinal,
        RetailBuildingSegmentKind kind, RetailBuildingSegment? parent,
        float weight, int? coreOrdinal, int? numNmic)
    {
        Identity = identity;
        PartOrdinal = partOrdinal;
        Kind = kind;
        Parent = parent;
        Weight = weight;
        CoreOrdinal = coreOrdinal;
        NumNmic = numNmic;
    }

    public int Identity { get; }
    public int PartOrdinal { get; }
    public RetailBuildingSegmentKind Kind { get; }
    public RetailBuildingSegment? Parent { get; }
    public float Weight { get; }
    public int? CoreOrdinal { get; }
    public int? NumNmic { get; }
    public int? CurrentVariant => Kind == RetailBuildingSegmentKind.Swap ? 0 : null;
    public float Health { get; private set; }
    public float InitialHealth { get; private set; }
    public bool Active => true;
    public IEnumerable<RetailBuildingSegment> ChildrenNewestFirst
    {
        get { foreach (var child in _children) yield return child; }
    }

    internal void LinkToParent() => Parent?._children.AddFirst(this);

    internal void Scale(float life, float totalWeight)
    {
        // 442870/443590 keep divide and multiply wide until the float store.
        double value = Weight / (double)totalWeight * life;
        if (Kind == RetailBuildingSegmentKind.Core)
            value = CoreOrdinal == 1 ? 0 : value * 5.0;
        Health = InitialHealth = (float)value;
    }

    internal float SumHealth()
    {
        float total = Health;
        foreach (var child in _children) total = (float)((double)total + child.SumHealth());
        return total;
    }
}

/// <summary>
/// Successful segment initialization for the admitted Building geometry.
/// Pristine 74154bfa…7750: 444660,444c10,4449c0,442870,443590,442900.
/// Exact body/data pins and numerical limits live in the World110 RE owner.
/// No damage, destruction, callbacks or animation evaluation is implemented.
/// </summary>
public sealed class RetailBuildingSegments
{
    internal RetailBuildingSegments(RetailInitialMesh mesh, float life,
        Func<int> allocateIdentity, Action<RetailBuildingSegment> publish)
    {
        var allocated = new List<RetailBuildingSegment>();
        // Retail allocates/clears partCount+1 pointer slots, including sentinel.
        var byPart = new RetailBuildingSegment?[mesh.Parts.Count + 1];
        int cores = 0;
        float totalWeight = 0;
        RetailBuildingSegment? root = null;

        void Visit(int ordinal, RetailBuildingSegment? parent)
        {
            RetailInitialMeshPart part = mesh.Parts[ordinal];
            RetailInitialMeshPart? geometry = part.Type switch
            {
                1 or 3 => part,
                6 when part.Reference.HasValue => mesh.Parts[part.Reference.Value],
                _ => null
            };
            RetailBuildingSegment? current = parent;
            if (geometry?.Type == 1 && part.IsNmic == 0)
            {
                float weight = BitConverter.Int32BitsToSingle(geometry.HalfExtentFloatBits.X);
                float y = BitConverter.Int32BitsToSingle(geometry.HalfExtentFloatBits.Y);
                float z = BitConverter.Int32BitsToSingle(geometry.HalfExtentFloatBits.Z);
                if (y > weight) weight = y;
                if (z > weight) weight = z;
                RetailBuildingSegmentKind kind =
                    part.Name.StartsWith("core", StringComparison.Ordinal) ||
                    part.Name.StartsWith("CORE", StringComparison.Ordinal) ? RetailBuildingSegmentKind.Core :
                    part.NumNmic > 0 ? RetailBuildingSegmentKind.Swap :
                    part.Name.StartsWith("x1", StringComparison.Ordinal) ||
                    part.Name.StartsWith("X1", StringComparison.Ordinal) ? RetailBuildingSegmentKind.X1 :
                    RetailBuildingSegmentKind.Extra;
                if (parent is not null) totalWeight = (float)((double)totalWeight + weight);
                current = new(allocateIdentity(), ordinal, kind, parent, weight,
                    kind == RetailBuildingSegmentKind.Core ? ++cores : null,
                    kind == RetailBuildingSegmentKind.Swap ? part.NumNmic : null);
                allocated.Add(current);
                publish(current);
                current.LinkToParent();
                if (parent is null)
                {
                    // Other roots take retail's early warning/return branches;
                    // they are outside this exact mesh admission.
                    if (kind != RetailBuildingSegmentKind.Core || cores != 1 || root is not null)
                        throw new NotSupportedException("Unadmitted destructible root topology.");
                    root = current;
                }
                byPart[ordinal] = current;
                if (part.NumNmic > 0)
                    for (int? alias = part.Nmic; alias.HasValue; alias = mesh.Parts[alias.Value].Nmic)
                        byPart[alias.Value] = current;
            }
            foreach (int child in part.Children) Visit(child, current);
        }

        Visit(0, null);
        if (root is null || !float.IsFinite(totalWeight) || totalWeight <= 0)
            throw new NotSupportedException("Destructible mesh has no admitted weighted root.");
        foreach (var segment in byPart) segment?.Scale(life, totalWeight);
        Root = root;
        CoreCount = cores;
        TotalWeight = totalWeight;
        InitialTotalHealth = root.SumHealth();
        Allocated = allocated.AsReadOnly();
        ByPart = Array.AsReadOnly(byPart);
    }

    public RetailBuildingSegment Root { get; }
    public int CoreCount { get; }
    public float TotalWeight { get; }
    public float InitialTotalHealth { get; }
    public IReadOnlyList<RetailBuildingSegment> Allocated { get; }
    public IReadOnlyList<RetailBuildingSegment?> ByPart { get; }
}
