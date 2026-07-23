// SPDX-License-Identifier: GPL-3.0-or-later

using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;

namespace OnslaughtRebuild.Core;

/// <summary>
/// Millimetre-space vector in Battle Engine Aquila axes: X/Y are horizontal
/// and positive Z is down.
/// </summary>
public readonly record struct Level100Vector3(int X, int Y, int Z)
{
    public static Level100Vector3 Zero => default;
}

/// <summary>
/// Allocation-free model-to-world basis, with each element expressed in
/// parts per million. The mission/native bridge owns the mutable basis.
/// </summary>
public readonly record struct Level100Basis3(
    int M00,
    int M01,
    int M02,
    int M10,
    int M11,
    int M12,
    int M20,
    int M21,
    int M22)
{
    public const int Scale = 1_000_000;

    public static Level100Basis3 Identity => new(
        Scale, 0, 0,
        0, Scale, 0,
        0, 0, Scale);

    internal bool IsOrthonormal =>
        IsElement(M00) && IsElement(M01) && IsElement(M02) &&
        IsElement(M10) && IsElement(M11) && IsElement(M12) &&
        IsElement(M20) && IsElement(M21) && IsElement(M22) &&
        IsUnitRow(M00, M01, M02) &&
        IsUnitRow(M10, M11, M12) &&
        IsUnitRow(M20, M21, M22) &&
        IsPerpendicular(M00, M01, M02, M10, M11, M12) &&
        IsPerpendicular(M00, M01, M02, M20, M21, M22) &&
        IsPerpendicular(M10, M11, M12, M20, M21, M22);

    private static bool IsElement(int value) => value is >= -Scale and <= Scale;

    private static bool IsUnitRow(int x, int y, int z)
    {
        const long tolerance = 10_000_000_000;
        long squaredLength = ((long)x * x) + ((long)y * y) + ((long)z * z);
        long unitSquared = (long)Scale * Scale;
        return Math.Abs(squaredLength - unitSquared) <= tolerance;
    }

    private static bool IsPerpendicular(
        int ax,
        int ay,
        int az,
        int bx,
        int by,
        int bz)
    {
        const long tolerance = 10_000_000_000;
        long dot = ((long)ax * bx) + ((long)ay * by) + ((long)az * bz);
        return Math.Abs(dot) <= tolerance;
    }
}

public readonly record struct Level100Transform3(
    Level100Vector3 Position,
    Level100Basis3 Basis)
{
    public static Level100Transform3 Identity => new(
        Level100Vector3.Zero,
        Level100Basis3.Identity);
}

public enum Level100ContactSurfaceKind : byte
{
    Mesh = 0,
    Terrain = 2,
}

public readonly record struct Level100ContactHit(
    int ActorId,
    int PartIndex,
    Level100ContactSurfaceKind SurfaceKind,
    int TimePartsPerMillion,
    Level100Vector3 ImpactCenter,
    Level100Vector3 SurfacePoint,
    Level100Vector3 NormalPartsPerMillion);

/// <summary>
/// One externally owned actor presented to a contact query. Empty
/// PartActivity means every decoded part is active; otherwise zero disables
/// the corresponding part. Velocity is the actor's world displacement over
/// the same interval as the supplied sweep.
/// </summary>
public readonly struct Level100ContactActor
{
    public Level100ContactActor(
        int actorId,
        bool active,
        Level100Transform3 transform,
        Level100Vector3 sweepVelocity,
        Level100ContactDefinition definition,
        ReadOnlyMemory<byte> partActivity = default)
    {
        if (actorId <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(actorId));
        }
        if (!transform.Basis.IsOrthonormal)
        {
            throw new ArgumentOutOfRangeException(
                nameof(transform),
                "The actor transform must contain an orthonormal basis.");
        }
        ArgumentNullException.ThrowIfNull(definition);
        if (!partActivity.IsEmpty &&
            partActivity.Length != definition.PartCount)
        {
            throw new ArgumentException(
                "Part activity must be empty or match the decoded definition.",
                nameof(partActivity));
        }

        ActorId = actorId;
        Active = active;
        Transform = transform;
        SweepVelocity = sweepVelocity;
        Definition = definition;
        PartActivity = partActivity;
    }

    public int ActorId { get; }

    public bool Active { get; }

    public Level100Transform3 Transform { get; }

    public Level100Vector3 SweepVelocity { get; }

    public Level100ContactDefinition Definition { get; }

    public ReadOnlyMemory<byte> PartActivity { get; }
}

public enum Level100DefinitionKind : byte
{
    Static = 0,
    TargetTank = 1,
    Warehouse = 2,
}

public sealed class Level100ContactPart
{
    internal Level100ContactPart(
        int index,
        int parent,
        int reference,
        int type,
        string name,
        bool collidable,
        uint segmentValueBits,
        Level100Vector3 center,
        Level100Vector3 halfExtents,
        Level100Basis3 orientation,
        int[] vertices,
        int[] triangles)
    {
        Index = index;
        Parent = parent;
        Reference = reference;
        Type = type;
        Name = name;
        Collidable = collidable;
        SegmentValueBits = segmentValueBits;
        Center = center;
        HalfExtents = halfExtents;
        Orientation = orientation;
        VerticesMillimeters = vertices;
        Triangles = triangles;
    }

    public int Index { get; }

    public int Parent { get; }

    public int Reference { get; }

    public int Type { get; }

    public string Name { get; }

    public bool Collidable { get; }

    public uint SegmentValueBits { get; }

    public float SegmentValue =>
        BitConverter.Int32BitsToSingle(unchecked((int)SegmentValueBits));

    public Level100Vector3 Center { get; }

    public Level100Vector3 HalfExtents { get; }

    public Level100Basis3 Orientation { get; }

    public ReadOnlyMemory<int> VerticesMillimeters { get; }

    public ReadOnlyMemory<int> Triangles { get; }
}

public sealed class Level100ContactDefinition
{
    private readonly Level100ContactPart[] _parts;

    internal Level100ContactDefinition(
        string name,
        string? mesh,
        Level100DefinitionKind kind,
        uint maximumLifeBits,
        string? destructionPhysicsDefinition,
        string? destructionParticleDescriptor,
        string? destructionSoundDescriptor,
        Level100ContactPart[] parts)
    {
        Name = name;
        Mesh = mesh;
        Kind = kind;
        MaximumLifeBits = maximumLifeBits;
        DestructionPhysicsDefinition = destructionPhysicsDefinition;
        DestructionParticleDescriptor = destructionParticleDescriptor;
        DestructionSoundDescriptor = destructionSoundDescriptor;
        _parts = parts;
        Parts = Array.AsReadOnly(parts);
    }

    public string Name { get; }

    public string? Mesh { get; }

    public Level100DefinitionKind Kind { get; }

    public uint MaximumLifeBits { get; }

    public float MaximumLife =>
        BitConverter.Int32BitsToSingle(unchecked((int)MaximumLifeBits));

    public string? DestructionPhysicsDefinition { get; }

    public string? DestructionParticleDescriptor { get; }

    public string? DestructionSoundDescriptor { get; }

    public IReadOnlyList<Level100ContactPart> Parts { get; }

    public int PartCount => _parts.Length;

    internal Level100ContactPart[] PartArray => _parts;
}

public readonly record struct Level100PulseRoundContract(
    int RadiusMillimeters,
    string ImpactPhysicsDefinition,
    string ImpactParticleDescriptor,
    string ImpactSoundDescriptor);

/// <summary>
/// Hash-verified, locally materialized Level 100 definitions. Mesh vertices,
/// part transforms and strip topology are deterministically millimetre-quantized
/// projections for Core contact; this is not a claim of bit-identical retail
/// collision geometry. The 33 serialized WRES rows are validated by this loader
/// but are intentionally not turned into actors; the mission/native Simulation
/// bridge owns identity, pose, activation and spawn.
/// </summary>
public sealed class Level100ContactCatalog
{
    private const string ResourceName =
        "OnslaughtRebuild.Core.Assets.Level100.level100-contact-owners.json";
    private const string SourceSha256 =
        "FE5F109526E39231EA3D02898A035DBC7EB842B7B37776EC5EFDA7BA45F138B0";
    private const string StaticSourceAggregateSha256 =
        "8D85C9BFBE366C815E00D3900D8D29B71A33BEF7A60CDDFCE9ED6AC558E06B4C";
    private const string TargetTankSourceSha256 =
        "9B2CFDCEB86ED700ED924051FBFF13C32DC30BD8F8B948EA1CF8AA9FBFE8B97B";
    private const string WarehouseSourceSha256 =
        "61FE5465BD7AFFEDF749AD784209BE02B2E4DD28631E70386C3810302B5F6F15";

    private readonly Dictionary<string, Level100ContactDefinition> _definitions;

    private Level100ContactCatalog(
        Dictionary<string, Level100ContactDefinition> definitions,
        Level100PulseRoundContract pulseRound)
    {
        _definitions = definitions;
        var orderedDefinitions = new Level100ContactDefinition[definitions.Count];
        int index = 0;
        foreach (Level100ContactDefinition definition in definitions.Values)
        {
            orderedDefinitions[index++] = definition;
        }
        Definitions = Array.AsReadOnly(orderedDefinitions);
        PulseRound = pulseRound;
    }

    public static Level100ContactCatalog Instance { get; } = LoadEmbedded();

    public IReadOnlyList<Level100ContactDefinition> Definitions { get; }

    public Level100PulseRoundContract PulseRound { get; }

    public Level100ContactDefinition GetDefinition(string name)
    {
        ArgumentNullException.ThrowIfNull(name);
        return _definitions.TryGetValue(name, out Level100ContactDefinition? definition)
            ? definition
            : throw new KeyNotFoundException($"Level 100 has no decoded definition '{name}'.");
    }

    public bool TryGetDefinition(
        string name,
        out Level100ContactDefinition? definition) =>
        _definitions.TryGetValue(name, out definition);

    private static Level100ContactCatalog LoadEmbedded()
    {
        Assembly assembly = typeof(Level100ContactCatalog).Assembly;
        using Stream stream = assembly.GetManifestResourceStream(ResourceName) ??
            throw new InvalidDataException(
                "The locally materialized Level 100 contact asset is missing.");
        var source = new byte[checked((int)stream.Length)];
        stream.ReadExactly(source);
        if (!StringComparer.Ordinal.Equals(
            Convert.ToHexString(SHA256.HashData(source)),
            SourceSha256))
        {
            throw new InvalidDataException(
                "The Level 100 contact asset does not match its exact recipe.");
        }

        DocumentRow document = JsonSerializer.Deserialize<DocumentRow>(
            source,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ??
            throw new InvalidDataException("The Level 100 contact asset is empty.");
        if (!StringComparer.Ordinal.Equals(
                document.Schema,
                "onslaught.level100-contact-owners.v3") ||
            document.DefinitionCount != 24 ||
            document.InstanceCount != 33 ||
            document.PartCount != 349 ||
            document.StaticMeshCount != 24 ||
            document.TargetDefinitionCount != 2 ||
            document.Definitions.Length != 24 ||
            document.Instances.Length != 33 ||
            document.TargetDefinitions.Length != 2 ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                document.StaticSourceAggregateSha256,
                StaticSourceAggregateSha256) ||
            document.TargetSourceSha256.Count != 2 ||
            !document.TargetSourceSha256.TryGetValue(
                "Target Tank",
                out string? targetTankSourceSha256) ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                targetTankSourceSha256,
                TargetTankSourceSha256) ||
            !document.TargetSourceSha256.TryGetValue(
                "Warehouse",
                out string? warehouseSourceSha256) ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                warehouseSourceSha256,
                WarehouseSourceSha256))
        {
            throw new InvalidDataException(
                "The Level 100 contact asset identity or counts changed.");
        }

        ValidateInstances(document.Instances);
        Level100PulseRoundContract pulse = ReadPulse(document.PulseRound);
        var definitions = new Dictionary<string, Level100ContactDefinition>(
            26,
            StringComparer.Ordinal);
        int partCount = 0;
        for (int index = 0; index < document.Definitions.Length; index++)
        {
            DefinitionRow row = document.Definitions[index];
            Level100ContactPart[] parts = ReadParts(row.Parts);
            partCount += parts.Length;
            if (!definitions.TryAdd(
                row.Definition,
                new Level100ContactDefinition(
                    row.Definition,
                    row.Mesh,
                    Level100DefinitionKind.Static,
                    0,
                    null,
                    null,
                    null,
                    parts)))
            {
                throw new InvalidDataException(
                    "Level 100 has a duplicate decoded definition.");
            }
        }

        for (int index = 0; index < document.TargetDefinitions.Length; index++)
        {
            TargetDefinitionRow row = document.TargetDefinitions[index];
            Level100DefinitionKind kind = row.Definition switch
            {
                "Target Tank" => Level100DefinitionKind.TargetTank,
                "Warehouse" => Level100DefinitionKind.Warehouse,
                _ => throw new InvalidDataException(
                    "Level 100 has an unexpected target definition."),
            };
            Level100ContactPart[] parts = ReadParts(row.Parts);
            partCount += parts.Length;
            if (!definitions.TryAdd(
                row.Definition,
                new Level100ContactDefinition(
                    row.Definition,
                    row.Mesh,
                    kind,
                    row.MaximumLifeBits,
                    row.DestructionPhysicsDefinition,
                    row.DestructionParticleDescriptor,
                    row.DestructionSoundDescriptor,
                    parts)))
            {
                throw new InvalidDataException(
                    "Level 100 has a duplicate target definition.");
            }
        }

        ValidateTargetContracts(definitions);
        if (partCount != document.PartCount)
        {
            throw new InvalidDataException(
                "Level 100 decoded part ownership changed.");
        }
        return new Level100ContactCatalog(definitions, pulse);
    }

    private static Level100PulseRoundContract ReadPulse(PulseRoundRow row)
    {
        if (row.RadiusMillimeters != Level100ContactMechanics.PulseRadiusMillimeters ||
            !StringComparer.Ordinal.Equals(
                row.ImpactPhysicsDefinition,
                "Mech Pulse Hit Medium") ||
            !StringComparer.Ordinal.Equals(
                row.ImpactParticleDescriptor,
                "Mech Pulse Bolt Explosion Medium") ||
            !StringComparer.Ordinal.Equals(
                row.ImpactSoundDescriptor,
                "Explosion Small"))
        {
            throw new InvalidDataException(
                "The Level 100 pulse impact contract changed.");
        }
        return new Level100PulseRoundContract(
            row.RadiusMillimeters,
            row.ImpactPhysicsDefinition,
            row.ImpactParticleDescriptor,
            row.ImpactSoundDescriptor);
    }

    private static void ValidateTargetContracts(
        Dictionary<string, Level100ContactDefinition> definitions)
    {
        Level100ContactDefinition tank = definitions["Target Tank"];
        Level100ContactDefinition warehouse = definitions["Warehouse"];
        if (tank.MaximumLifeBits != 0x40C00000 || tank.PartCount != 7 ||
            !StringComparer.Ordinal.Equals(
                tank.Mesh,
                "m_f_pulsetank_training.msh.aya") ||
            !StringComparer.Ordinal.Equals(
                tank.DestructionPhysicsDefinition,
                "Tank Explosion Medium") ||
            !StringComparer.Ordinal.Equals(
                tank.DestructionParticleDescriptor,
                "Tank Explosion Medium") ||
            !StringComparer.Ordinal.Equals(
                tank.DestructionSoundDescriptor,
                "Explosion Medium") ||
            warehouse.MaximumLifeBits != 0x42480000 || warehouse.PartCount != 28 ||
            !StringComparer.Ordinal.Equals(
                warehouse.Mesh,
                "m_m_warehouse.msh.aya") ||
            !StringComparer.Ordinal.Equals(
                warehouse.DestructionPhysicsDefinition,
                "Muspell Building Explosion") ||
            !StringComparer.Ordinal.Equals(
                warehouse.DestructionParticleDescriptor,
                "Muspell Building Explosion Effect") ||
            !StringComparer.Ordinal.Equals(
                warehouse.DestructionSoundDescriptor,
                "Explosion Medium Building"))
        {
            throw new InvalidDataException(
                "Level 100 target damage/effect definitions changed.");
        }
    }

    private static void ValidateInstances(InstanceRow[] instances)
    {
        var ids = new HashSet<int>();
        for (int index = 0; index < instances.Length; index++)
        {
            InstanceRow row = instances[index];
            if (!ids.Add(row.Id) ||
                row.PositionMillimeters.Length != 2 ||
                row.RetailPositionBits.Length != 3 ||
                row.RetailYawPitchRollBits.Length != 3 ||
                string.IsNullOrWhiteSpace(row.Definition) ||
                !StringComparer.Ordinal.Equals(
                    row.RootMode,
                    "authored-terrain-water"))
            {
                throw new InvalidDataException(
                    "Level 100 WRES instance metadata changed.");
            }
        }
    }

    private static Level100ContactPart[] ReadParts(PartRow[] rows)
    {
        var parts = new Level100ContactPart[rows.Length];
        for (int index = 0; index < rows.Length; index++)
        {
            PartRow row = rows[index];
            if (row.Index != index ||
                row.Parent >= index || row.Parent < -1 ||
                row.Reference >= index || row.Reference < -1 ||
                row.CenterMillimeters.Length != 3 ||
                row.HalfExtentsMillimeters.Length != 3 ||
                row.OrientationPartsPerMillion.Length != 9 ||
                row.VerticesMillimeters.Length % 3 != 0 ||
                row.Triangles.Length % 3 != 0 ||
                string.IsNullOrEmpty(row.Name))
            {
                throw new InvalidDataException(
                    "Level 100 has invalid decoded part metadata.");
            }
            int vertexCount = row.VerticesMillimeters.Length / 3;
            for (int triangleIndex = 0;
                 triangleIndex < row.Triangles.Length;
                 triangleIndex++)
            {
                if ((uint)row.Triangles[triangleIndex] >= (uint)vertexCount)
                {
                    throw new InvalidDataException(
                        "Level 100 has an invalid mesh triangle index.");
                }
            }
            if (row.Collidable &&
                (vertexCount == 0 || row.Triangles.Length == 0 ||
                 row.HalfExtentsMillimeters[0] <= 0 ||
                 row.HalfExtentsMillimeters[1] <= 0 ||
                 row.HalfExtentsMillimeters[2] <= 0))
            {
                throw new InvalidDataException(
                    "Level 100 has an empty collidable mesh part.");
            }

            parts[index] = new Level100ContactPart(
                row.Index,
                row.Parent,
                row.Reference,
                row.Type,
                row.Name,
                row.Collidable,
                row.SegmentValueBits,
                ReadVector(row.CenterMillimeters),
                ReadVector(row.HalfExtentsMillimeters),
                ReadBasis(row.OrientationPartsPerMillion),
                row.VerticesMillimeters,
                row.Triangles);
        }
        return parts;
    }

    private static Level100Vector3 ReadVector(int[] values) =>
        new(values[0], values[1], values[2]);

    private static Level100Basis3 ReadBasis(int[] values)
    {
        var basis = new Level100Basis3(
            values[0], values[1], values[2],
            values[3], values[4], values[5],
            values[6], values[7], values[8]);
        return basis.IsOrthonormal
            ? basis
            : throw new InvalidDataException(
                "Level 100 has an invalid decoded part basis.");
    }

    private sealed class DocumentRow
    {
        public string Schema { get; set; } = string.Empty;
        public int DefinitionCount { get; set; }
        public int InstanceCount { get; set; }
        public int PartCount { get; set; }
        public int StaticMeshCount { get; set; }
        public int TargetDefinitionCount { get; set; }
        public string StaticSourceAggregateSha256 { get; set; } = string.Empty;
        public Dictionary<string, string> TargetSourceSha256 { get; set; } = [];
        public DefinitionRow[] Definitions { get; set; } = [];
        public InstanceRow[] Instances { get; set; } = [];
        public TargetDefinitionRow[] TargetDefinitions { get; set; } = [];
        public PulseRoundRow PulseRound { get; set; } = new();
    }

    private sealed class DefinitionRow
    {
        public string Definition { get; set; } = string.Empty;
        public string Mesh { get; set; } = string.Empty;
        public PartRow[] Parts { get; set; } = [];
    }

    private sealed class TargetDefinitionRow
    {
        public string Definition { get; set; } = string.Empty;
        public string Mesh { get; set; } = string.Empty;
        public string DestructionPhysicsDefinition { get; set; } = string.Empty;
        public string DestructionParticleDescriptor { get; set; } = string.Empty;
        public string DestructionSoundDescriptor { get; set; } = string.Empty;
        public uint MaximumLifeBits { get; set; }
        public PartRow[] Parts { get; set; } = [];
    }

    private sealed class PulseRoundRow
    {
        public string ImpactPhysicsDefinition { get; set; } = string.Empty;
        public string ImpactParticleDescriptor { get; set; } = string.Empty;
        public string ImpactSoundDescriptor { get; set; } = string.Empty;
        public int RadiusMillimeters { get; set; }
    }

    private sealed class InstanceRow
    {
        public int Id { get; set; }
        public string Definition { get; set; } = string.Empty;
        public int[] PositionMillimeters { get; set; } = [];
        public uint[] RetailPositionBits { get; set; } = [];
        public uint[] RetailYawPitchRollBits { get; set; } = [];
        public string RootMode { get; set; } = string.Empty;
    }

    private sealed class PartRow
    {
        public int Index { get; set; }
        public int Parent { get; set; }
        public int Reference { get; set; }
        public int Type { get; set; }
        public string Name { get; set; } = string.Empty;
        public bool Collidable { get; set; }
        public uint SegmentValueBits { get; set; }
        public int[] CenterMillimeters { get; set; } = [];
        public int[] HalfExtentsMillimeters { get; set; } = [];
        public int[] OrientationPartsPerMillion { get; set; } = [];
        public int[] VerticesMillimeters { get; set; } = [];
        public int[] Triangles { get; set; } = [];
    }
}

/// <summary>
/// The bounded released contact paths used by Level 100. CMSH BBOX records
/// reject candidates only; mesh triangles own every reported actor hit.
/// </summary>
public static class Level100ContactMechanics
{
    public const int PulseRadiusMillimeters = 70;

    private const double AxisScale = Level100Basis3.Scale;
    private const double RetailTriangleEpsilonMillimeters = 10.0;
    private const double GeometryEpsilon = 1e-9;

    public static bool TrySweepPulse(
        Level100Vector3 start,
        Level100Vector3 end,
        ReadOnlySpan<Level100ContactActor> actors,
        out Level100ContactHit hit) =>
        TrySweepActors(
            start,
            end,
            PulseRadiusMillimeters,
            actors,
            out hit);

    /// <summary>
    /// Deterministic Level 100 pulse/heightfield contact. The subdivision walks
    /// the exact 24.8 sampler lattice and searches each crossed interval in
    /// order, so a ridge cannot be skipped merely because both endpoints are
    /// clear.
    /// </summary>
    public static bool TrySweepPulseAgainstTerrain(
        Level100Vector3 start,
        Level100Vector3 end,
        out Level100ContactHit hit)
    {
        int high;
        if (TouchesTerrain(start, PulseRadiusMillimeters))
        {
            high = 0;
        }
        else if (!TryFindFirstTerrainContact(
            start,
            end,
            0,
            Level100Basis3.Scale,
            out high))
        {
            hit = default;
            return false;
        }

        Level100Vector3 center = Interpolate(start, end, high);
        int groundElevation = SampleTerrain(center.X, center.Y);
        Level100Vector3 normal = TerrainNormal(center.X, center.Y);
        hit = new Level100ContactHit(
            0,
            -1,
            Level100ContactSurfaceKind.Terrain,
            high,
            center,
            new Level100Vector3(center.X, center.Y, -groundElevation),
            normal);
        return true;
    }

    public static bool TrySweepPulseWithTerrain(
        Level100Vector3 start,
        Level100Vector3 end,
        ReadOnlySpan<Level100ContactActor> actors,
        out Level100ContactHit hit)
    {
        bool hasActor = TrySweepPulse(start, end, actors, out Level100ContactHit actorHit);
        bool hasTerrain = TrySweepPulseAgainstTerrain(
            start,
            end,
            out Level100ContactHit terrainHit);
        if (!hasActor && !hasTerrain)
        {
            hit = default;
            return false;
        }
        if (!hasTerrain ||
            (hasActor && actorHit.TimePartsPerMillion <= terrainHit.TimePartsPerMillion))
        {
            hit = actorHit;
            return true;
        }
        hit = terrainHit;
        return true;
    }

    private static bool TrySweepActors(
        Level100Vector3 start,
        Level100Vector3 end,
        int meshSphereRadius,
        ReadOnlySpan<Level100ContactActor> actors,
        out Level100ContactHit hit)
    {
        bool found = false;
        double bestTime = double.PositiveInfinity;
        int bestActorId = int.MaxValue;
        int bestPart = int.MaxValue;
        Level100ContactHit bestHit = default;
        for (int actorIndex = 0; actorIndex < actors.Length; actorIndex++)
        {
            ref readonly Level100ContactActor actor = ref actors[actorIndex];
            if (!actor.Active)
            {
                continue;
            }

            if (TrySweepMesh(
                    start,
                    end,
                    meshSphereRadius,
                    actor,
                    out double meshTime,
                    out Level100ContactHit meshHit) &&
                IsPreferred(
                    meshTime,
                    actor.ActorId,
                    meshHit.PartIndex,
                    bestTime,
                    bestActorId,
                    bestPart))
            {
                found = true;
                bestTime = meshTime;
                bestActorId = actor.ActorId;
                bestPart = meshHit.PartIndex;
                bestHit = meshHit;
            }
        }
        hit = bestHit;
        return found;
    }

    private static bool IsPreferred(
        double time,
        int actorId,
        int part,
        double bestTime,
        int bestActorId,
        int bestPart) =>
        time < bestTime - GeometryEpsilon ||
        (Math.Abs(time - bestTime) <= GeometryEpsilon &&
            (actorId < bestActorId ||
             (actorId == bestActorId && part < bestPart)));

    private static bool TrySweepMesh(
        Level100Vector3 worldStart,
        Level100Vector3 worldEnd,
        int radius,
        in Level100ContactActor actor,
        out double bestTime,
        out Level100ContactHit hit)
    {
        DVector3 start = ToActorModel(
            worldStart,
            actor.Transform.Position,
            actor.Transform.Basis);
        Level100Vector3 movedPosition = Add(
            actor.Transform.Position,
            actor.SweepVelocity);
        DVector3 end = ToActorModel(
            worldEnd,
            movedPosition,
            actor.Transform.Basis);
        DVector3 delta = end - start;
        Level100ContactPart[] parts = actor.Definition.PartArray;
        ReadOnlySpan<byte> activity = actor.PartActivity.Span;
        bool found = false;
        bestTime = double.PositiveInfinity;
        int selectedPart = -1;
        DVector3 selectedNormal = default;

        for (int partIndex = 0; partIndex < parts.Length; partIndex++)
        {
            Level100ContactPart part = parts[partIndex];
            if (!part.Collidable ||
                (!activity.IsEmpty && activity[partIndex] == 0) ||
                !SweptSphereIntersectsBounds(start, end, radius, part))
            {
                continue;
            }

            ReadOnlySpan<int> vertices = part.VerticesMillimeters.Span;
            ReadOnlySpan<int> triangles = part.Triangles.Span;
            for (int triangle = 0; triangle < triangles.Length; triangle += 3)
            {
                DVector3 a = ReadVertex(vertices, triangles[triangle]);
                DVector3 b = ReadVertex(vertices, triangles[triangle + 1]);
                DVector3 c = ReadVertex(vertices, triangles[triangle + 2]);
                if (TrySweepSphereTriangle(
                        start,
                        delta,
                        radius,
                        a,
                        b,
                        c,
                        out double time,
                        out DVector3 normal) &&
                    (time < bestTime - GeometryEpsilon ||
                     (Math.Abs(time - bestTime) <= GeometryEpsilon &&
                      part.Index < selectedPart)))
                {
                    found = true;
                    bestTime = time;
                    selectedPart = part.Index;
                    selectedNormal = normal;
                }
            }
        }

        if (!found)
        {
            hit = default;
            return false;
        }
        hit = BuildActorHit(
            actor.ActorId,
            selectedPart,
            Level100ContactSurfaceKind.Mesh,
            worldStart,
            worldEnd,
            radius,
            bestTime,
            selectedNormal,
            actor.Transform.Basis);
        return true;
    }

    private static Level100ContactHit BuildActorHit(
        int actorId,
        int partIndex,
        Level100ContactSurfaceKind kind,
        Level100Vector3 start,
        Level100Vector3 end,
        int radius,
        double time,
        DVector3 modelNormal,
        Level100Basis3 actorBasis)
    {
        DVector3 worldNormal = Normalize(ToWorldVector(modelNormal, actorBasis));
        DVector3 worldCenter = FromInt(start) +
            ((FromInt(end) - FromInt(start)) * time);
        DVector3 surface = worldCenter - (worldNormal * radius);
        return new Level100ContactHit(
            actorId,
            partIndex,
            kind,
            QuantizeTime(time),
            RoundVector(worldCenter),
            RoundVector(surface),
            new Level100Vector3(
                RoundAway(worldNormal.X * AxisScale),
                RoundAway(worldNormal.Y * AxisScale),
                RoundAway(worldNormal.Z * AxisScale)));
    }

    private static bool SweptSphereIntersectsBounds(
        DVector3 start,
        DVector3 end,
        int radius,
        Level100ContactPart part)
    {
        DVector3 localStart = ToPartLocal(start, part);
        DVector3 localEnd = ToPartLocal(end, part);
        DVector3 half = FromInt(part.HalfExtents);
        return SegmentIntersectsBox(
            localStart,
            localEnd,
            new DVector3(
                half.X + radius,
                half.Y + radius,
                half.Z + radius));
    }

    private static DVector3 ToPartLocal(
        DVector3 modelPoint,
        Level100ContactPart part)
    {
        DVector3 delta = modelPoint - FromInt(part.Center);
        return TransposeMultiply(part.Orientation, delta);
    }

    private static bool SegmentIntersectsBox(
        DVector3 start,
        DVector3 end,
        DVector3 half)
    {
        DVector3 delta = end - start;
        double minimum = 0;
        double maximum = 1;
        if (!ClipSlab(start.X, delta.X, half.X, ref minimum, ref maximum) ||
            !ClipSlab(start.Y, delta.Y, half.Y, ref minimum, ref maximum) ||
            !ClipSlab(start.Z, delta.Z, half.Z, ref minimum, ref maximum))
        {
            return false;
        }
        return minimum <= maximum;
    }

    private static bool ClipSlab(
        double start,
        double delta,
        double half,
        ref double minimum,
        ref double maximum)
    {
        if (Math.Abs(delta) <= GeometryEpsilon)
        {
            return start >= -half && start <= half;
        }
        double first = (-half - start) / delta;
        double second = (half - start) / delta;
        if (first > second)
        {
            (first, second) = (second, first);
        }
        minimum = Math.Max(minimum, first);
        maximum = Math.Min(maximum, second);
        return minimum <= maximum;
    }

    private static bool TrySweepSphereTriangle(
        DVector3 start,
        DVector3 delta,
        double radius,
        DVector3 a,
        DVector3 b,
        DVector3 c,
        out double time,
        out DVector3 hitNormal)
    {
        DVector3 cross = Cross(b - a, c - a);
        double crossLength = Length(cross);
        if (crossLength <= GeometryEpsilon)
        {
            time = 0;
            hitNormal = default;
            return false;
        }
        DVector3 triangleNormal = cross / crossLength;
        double normalSweep = Dot(triangleNormal, delta);
        if (normalSweep >= RetailTriangleEpsilonMillimeters ||
            Dot(a - start, triangleNormal) >= RetailTriangleEpsilonMillimeters)
        {
            time = 0;
            hitNormal = default;
            return false;
        }

        DVector3 closest = ClosestPointOnTriangle(start, a, b, c);
        DVector3 initialOffset = start - closest;
        double radiusSquared = radius * radius;
        if (LengthSquared(initialOffset) <= radiusSquared + GeometryEpsilon)
        {
            time = 0;
            hitNormal = LengthSquared(initialOffset) > GeometryEpsilon
                ? Normalize(initialOffset)
                : triangleNormal;
            return true;
        }

        bool found = false;
        double best = double.PositiveInfinity;
        DVector3 bestNormal = default;
        double startDistance = Dot(start - a, triangleNormal);
        if (normalSweep < -GeometryEpsilon)
        {
            double planeTime = (radius - startDistance) / normalSweep;
            if (planeTime is >= 0 and <= 1)
            {
                DVector3 center = start + (delta * planeTime);
                DVector3 point = center - (triangleNormal * radius);
                if (PointInTriangle(point, a, b, c, triangleNormal))
                {
                    found = true;
                    best = planeTime;
                    bestNormal = triangleNormal;
                }
            }
        }

        TryEdgeCandidate(start, delta, radius, a, b, ref found, ref best, ref bestNormal);
        TryEdgeCandidate(start, delta, radius, b, c, ref found, ref best, ref bestNormal);
        TryEdgeCandidate(start, delta, radius, c, a, ref found, ref best, ref bestNormal);

        time = best;
        hitNormal = bestNormal;
        return found;
    }

    private static void TryEdgeCandidate(
        DVector3 start,
        DVector3 delta,
        double radius,
        DVector3 a,
        DVector3 b,
        ref bool found,
        ref double best,
        ref DVector3 bestNormal)
    {
        DVector3 edge = b - a;
        double edgeLengthSquared = LengthSquared(edge);
        if (edgeLengthSquared > GeometryEpsilon)
        {
            DVector3 fromA = start - a;
            double startProjection = Dot(fromA, edge) / edgeLengthSquared;
            double deltaProjection = Dot(delta, edge) / edgeLengthSquared;
            DVector3 radialStart = fromA - (edge * startProjection);
            DVector3 radialDelta = delta - (edge * deltaProjection);
            if (TryFirstQuadraticRoot(
                    LengthSquared(radialDelta),
                    2 * Dot(radialStart, radialDelta),
                    LengthSquared(radialStart) - (radius * radius),
                    out double cylinderTime))
            {
                double edgeParameter = startProjection +
                    (deltaProjection * cylinderTime);
                if (edgeParameter is >= 0 and <= 1)
                {
                    DVector3 center = start + (delta * cylinderTime);
                    DVector3 point = a + (edge * edgeParameter);
                    SelectCandidate(
                        cylinderTime,
                        center - point,
                        ref found,
                        ref best,
                        ref bestNormal);
                }
            }
        }
        TryPointCandidate(start, delta, radius, a, ref found, ref best, ref bestNormal);
        TryPointCandidate(start, delta, radius, b, ref found, ref best, ref bestNormal);
    }

    private static void TryPointCandidate(
        DVector3 start,
        DVector3 delta,
        double radius,
        DVector3 point,
        ref bool found,
        ref double best,
        ref DVector3 bestNormal)
    {
        DVector3 offset = start - point;
        if (TryFirstQuadraticRoot(
            LengthSquared(delta),
            2 * Dot(offset, delta),
            LengthSquared(offset) - (radius * radius),
            out double candidate))
        {
            SelectCandidate(
                candidate,
                (start + (delta * candidate)) - point,
                ref found,
                ref best,
                ref bestNormal);
        }
    }

    private static void SelectCandidate(
        double time,
        DVector3 normal,
        ref bool found,
        ref double best,
        ref DVector3 bestNormal)
    {
        if (time is < 0 or > 1 ||
            (found && time >= best - GeometryEpsilon) ||
            LengthSquared(normal) <= GeometryEpsilon)
        {
            return;
        }
        found = true;
        best = time;
        bestNormal = Normalize(normal);
    }

    private static bool TryFirstQuadraticRoot(
        double a,
        double b,
        double c,
        out double time)
    {
        if (c <= 0)
        {
            time = 0;
            return true;
        }
        if (a <= GeometryEpsilon)
        {
            time = 0;
            return false;
        }
        double discriminant = (b * b) - (4 * a * c);
        if (discriminant < 0)
        {
            time = 0;
            return false;
        }
        double root = (-b - Math.Sqrt(discriminant)) / (2 * a);
        if (root is < 0 or > 1)
        {
            time = 0;
            return false;
        }
        time = root;
        return true;
    }

    private static DVector3 ClosestPointOnTriangle(
        DVector3 point,
        DVector3 a,
        DVector3 b,
        DVector3 c)
    {
        DVector3 ab = b - a;
        DVector3 ac = c - a;
        DVector3 ap = point - a;
        double d1 = Dot(ab, ap);
        double d2 = Dot(ac, ap);
        if (d1 <= 0 && d2 <= 0)
        {
            return a;
        }

        DVector3 bp = point - b;
        double d3 = Dot(ab, bp);
        double d4 = Dot(ac, bp);
        if (d3 >= 0 && d4 <= d3)
        {
            return b;
        }

        double vc = (d1 * d4) - (d3 * d2);
        if (vc <= 0 && d1 >= 0 && d3 <= 0)
        {
            double v = d1 / (d1 - d3);
            return a + (ab * v);
        }

        DVector3 cp = point - c;
        double d5 = Dot(ab, cp);
        double d6 = Dot(ac, cp);
        if (d6 >= 0 && d5 <= d6)
        {
            return c;
        }

        double vb = (d5 * d2) - (d1 * d6);
        if (vb <= 0 && d2 >= 0 && d6 <= 0)
        {
            double w = d2 / (d2 - d6);
            return a + (ac * w);
        }

        double va = (d3 * d6) - (d5 * d4);
        if (va <= 0 && (d4 - d3) >= 0 && (d5 - d6) >= 0)
        {
            double w = (d4 - d3) / ((d4 - d3) + (d5 - d6));
            return b + ((c - b) * w);
        }

        double denominator = 1 / (va + vb + vc);
        double barycentricV = vb * denominator;
        double barycentricW = vc * denominator;
        return a + (ab * barycentricV) + (ac * barycentricW);
    }

    private static bool PointInTriangle(
        DVector3 point,
        DVector3 a,
        DVector3 b,
        DVector3 c,
        DVector3 normal) =>
        Dot(Cross(b - a, point - a), normal) >= -GeometryEpsilon &&
        Dot(Cross(c - b, point - b), normal) >= -GeometryEpsilon &&
        Dot(Cross(a - c, point - c), normal) >= -GeometryEpsilon;

    private static DVector3 ReadVertex(ReadOnlySpan<int> vertices, int index)
    {
        int offset = index * 3;
        return new DVector3(
            vertices[offset],
            vertices[offset + 1],
            vertices[offset + 2]);
    }

    private static DVector3 ToActorModel(
        Level100Vector3 point,
        Level100Vector3 actorPosition,
        Level100Basis3 basis) =>
        TransposeMultiply(
            basis,
            new DVector3(
                (long)point.X - actorPosition.X,
                (long)point.Y - actorPosition.Y,
                (long)point.Z - actorPosition.Z));

    private static DVector3 TransposeMultiply(
        Level100Basis3 basis,
        DVector3 value) =>
        new(
            ((basis.M00 * value.X) +
             (basis.M10 * value.Y) +
             (basis.M20 * value.Z)) / AxisScale,
            ((basis.M01 * value.X) +
             (basis.M11 * value.Y) +
             (basis.M21 * value.Z)) / AxisScale,
            ((basis.M02 * value.X) +
             (basis.M12 * value.Y) +
             (basis.M22 * value.Z)) / AxisScale);

    private static DVector3 ToWorldVector(
        DVector3 value,
        Level100Basis3 basis) =>
        new(
            ((basis.M00 * value.X) +
             (basis.M01 * value.Y) +
             (basis.M02 * value.Z)) / AxisScale,
            ((basis.M10 * value.X) +
             (basis.M11 * value.Y) +
             (basis.M12 * value.Z)) / AxisScale,
            ((basis.M20 * value.X) +
             (basis.M21 * value.Y) +
             (basis.M22 * value.Z)) / AxisScale);

    private static bool TouchesTerrain(Level100Vector3 center, int radius) =>
        center.Z + radius >= -SampleTerrain(center.X, center.Y);

    private static bool TryFindFirstTerrainContact(
        Level100Vector3 start,
        Level100Vector3 end,
        int lowTime,
        int highTime,
        out int contactTime)
    {
        Level100Vector3 low = Interpolate(start, end, lowTime);
        if (TouchesTerrain(low, PulseRadiusMillimeters))
        {
            contactTime = lowTime;
            return true;
        }

        Level100Vector3 high = Interpolate(start, end, highTime);
        bool highTouches = TouchesTerrain(high, PulseRadiusMillimeters);
        (int lowX, int lowY) = GetTerrainSampleCoordinates(low);
        (int highX, int highY) = GetTerrainSampleCoordinates(high);
        bool sameSample = lowX == highX && lowY == highY;
        if (!highTouches && sameSample)
        {
            contactTime = 0;
            return false;
        }

        if (highTime - lowTime <= 1)
        {
            if (highTouches ||
                TerrainBoundaryCouldTouch(
                    low,
                    high,
                    lowX,
                    lowY,
                    highX,
                    highY))
            {
                contactTime = highTime;
                return true;
            }

            contactTime = 0;
            return false;
        }

        int middleTime = lowTime + ((highTime - lowTime) / 2);
        if (TryFindFirstTerrainContact(
            start,
            end,
            lowTime,
            middleTime,
            out contactTime))
        {
            return true;
        }
        return TryFindFirstTerrainContact(
            start,
            end,
            middleTime,
            highTime,
            out contactTime);
    }

    private static bool TerrainBoundaryCouldTouch(
        Level100Vector3 low,
        Level100Vector3 high,
        int lowX,
        int lowY,
        int highX,
        int highY)
    {
        Level100Terrain terrain = Level100Terrain.Instance;
        int minimumSurfaceDown = int.MaxValue;
        Span<int> xValues = stackalloc int[] { lowX, highX };
        Span<int> yValues = stackalloc int[] { lowY, highY };
        foreach (int x in xValues)
        {
            foreach (int y in yValues)
            {
                minimumSurfaceDown = Math.Min(
                    minimumSurfaceDown,
                    -terrain.SampleGroundElevationMillimetersAtFixed(x, y));
            }
        }

        int maximumSphereDown = checked(
            Math.Max(low.Z, high.Z) + PulseRadiusMillimeters);
        return maximumSphereDown >= minimumSurfaceDown;
    }

    private static (int X, int Y) GetTerrainSampleCoordinates(
        Level100Vector3 point) =>
        Level100Terrain.Instance.GetRetailFixedCoordinates(
            new SimVector2(point.X, point.Y));

    private static int SampleTerrain(int x, int y) =>
        Level100Terrain.Instance.SampleGroundElevationMillimeters(
            new SimVector2(x, y));

    private static Level100Vector3 TerrainNormal(int x, int y)
    {
        const int sampleOffset = 1_000;
        int downX0 = -SampleTerrain(x - sampleOffset, y);
        int downX1 = -SampleTerrain(x + sampleOffset, y);
        int downY0 = -SampleTerrain(x, y - sampleOffset);
        int downY1 = -SampleTerrain(x, y + sampleOffset);
        DVector3 normal = Normalize(new DVector3(
            downX1 - downX0,
            downY1 - downY0,
            -(sampleOffset * 2)));
        return new Level100Vector3(
            RoundAway(normal.X * AxisScale),
            RoundAway(normal.Y * AxisScale),
            RoundAway(normal.Z * AxisScale));
    }

    private static Level100Vector3 Interpolate(
        Level100Vector3 start,
        Level100Vector3 end,
        int timePartsPerMillion) =>
        new(
            checked(start.X + DivideRoundNearest(
                ((long)end.X - start.X) * timePartsPerMillion,
                Level100Basis3.Scale)),
            checked(start.Y + DivideRoundNearest(
                ((long)end.Y - start.Y) * timePartsPerMillion,
                Level100Basis3.Scale)),
            checked(start.Z + DivideRoundNearest(
                ((long)end.Z - start.Z) * timePartsPerMillion,
                Level100Basis3.Scale)));

    private static Level100Vector3 Add(
        Level100Vector3 left,
        Level100Vector3 right) =>
        new(
            checked(left.X + right.X),
            checked(left.Y + right.Y),
            checked(left.Z + right.Z));

    private static DVector3 FromInt(Level100Vector3 value) =>
        new(value.X, value.Y, value.Z);

    private static Level100Vector3 RoundVector(DVector3 value) =>
        new(RoundAway(value.X), RoundAway(value.Y), RoundAway(value.Z));

    private static int QuantizeTime(double time) =>
        Math.Clamp(RoundAway(time * Level100Basis3.Scale), 0, Level100Basis3.Scale);

    private static int RoundAway(double value) => checked((int)Math.Round(
        value,
        MidpointRounding.AwayFromZero));

    private static int DivideRoundNearest(long numerator, long denominator)
    {
        long half = denominator / 2;
        return checked((int)(numerator >= 0
            ? (numerator + half) / denominator
            : (numerator - half) / denominator));
    }

    private static double Dot(DVector3 left, DVector3 right) =>
        (left.X * right.X) + (left.Y * right.Y) + (left.Z * right.Z);

    private static DVector3 Cross(DVector3 left, DVector3 right) =>
        new(
            (left.Y * right.Z) - (left.Z * right.Y),
            (left.Z * right.X) - (left.X * right.Z),
            (left.X * right.Y) - (left.Y * right.X));

    private static double LengthSquared(DVector3 value) => Dot(value, value);

    private static double Length(DVector3 value) => Math.Sqrt(LengthSquared(value));

    private static DVector3 Normalize(DVector3 value)
    {
        double length = Length(value);
        return length <= GeometryEpsilon
            ? new DVector3(0, 0, -1)
            : value / length;
    }

    private readonly record struct DVector3(double X, double Y, double Z)
    {
        public static DVector3 operator +(DVector3 left, DVector3 right) =>
            new(left.X + right.X, left.Y + right.Y, left.Z + right.Z);

        public static DVector3 operator -(DVector3 left, DVector3 right) =>
            new(left.X - right.X, left.Y - right.Y, left.Z - right.Z);

        public static DVector3 operator *(DVector3 value, double scale) =>
            new(value.X * scale, value.Y * scale, value.Z * scale);

        public static DVector3 operator /(DVector3 value, double scale) =>
            new(value.X / scale, value.Y / scale, value.Z / scale);
    }
}
