// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text.Json;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

/// <summary>
/// Bounded decoder for the actor-definition projection inside the exact
/// locally materialized Level 100 static-world manifest. Filesystem ownership
/// remains with the calling client/scenario adapter.
/// </summary>
public static class Level100ActorDefinitionManifest
{
    // Moved 2026-07-27 from
    // E4CC77FF457EDD7ADA351CC92347108CEE2E2AE6E01A16DEE277B5CB83841F06 by the
    // waypoint-path coordinate correction (task #114 section 4-B). The eight
    // named paths index RLWD initial-actor ordinals of the 30 thingType-18
    // marker records, not the 121-entry navigation graph the materializer was
    // reading; nodeIndex was already right, only the coordinate lookup was
    // wrong. Schema v13 -> v14 for the two fields the correction adds.
    //
    // Verified against the previous manifest, 9,685 -> 9,723 leaves:
    //   changed 181 - schema (1) and waypointPaths (180)
    //   added    38 - waypointPaths[].isClosed and .targetChainNodeIndices
    //   removed   0
    // Nothing outside waypointPaths and schema moved.
    //
    // UNLIKE the pine move this replaces, this one DOES reach the decoder and
    // DOES move the simulation state hash, by two independent routes: the
    // waypoint positions and retail component bits feed
    // Level100ActorRegistry.ComputeIdentity, whose digest StateHasher writes;
    // and the ground actors now drive along different, much longer routes. Both
    // are intended. See the golden in InteractiveSessionTests.
    public const string ExpectedManifestSha256 =
        "2DFAD0DC536B2CDF5E01B26F04CF81C4185975D85357C16498ADBACDBB8B8568";

    private const string ExpectedSchema = "onslaught.level100-static-world.v14";
    private const string ExpectedSourceArchiveSha256 =
        "ED6350C0E214D00AB1BF6A7BD137FBA3E77D0AFE19A6DC4C0607F56AC037496A";
    private const string ExpectedPhysicsSourceSha256 =
        "E1FB3DEDBEB29B4B4151DA2C8CBBDC940B716B1A2321E1D6A9BA1542C74ADA14";
    private const int MaximumManifestBytes = 512_000;

    /// <summary>
    /// The authored WRES <c>allegiance</c> int32 of each of the 33 base-world
    /// objects, keyed by the same <c>wres:bswd:NNNN</c> identity the actor
    /// definitions carry. This is presentation input for the released scanner's
    /// colour partition; it is deliberately NOT folded into
    /// <see cref="Level100ActorDefinitionSet"/>, so no Core state and no state
    /// hash moves. The manifest is the same hash-pinned file
    /// <see cref="Decode"/> validates.
    ///
    /// <para>The 11 level-world actors (Player 1, the Firing Range group, the
    /// Transporter and the Air Trainer) have no allegiance in schema v13, so
    /// they are absent from this map and the caller falls back.</para>
    /// </summary>
    public static IReadOnlyDictionary<string, int> DecodeAuthoredAllegiance(
        ReadOnlySpan<byte> manifestBytes)
    {
        Manifest manifest = ReadValidatedManifest(manifestBytes);
        var allegiance = new Dictionary<string, int>(StringComparer.Ordinal);
        foreach (WorldObject worldObject in manifest.Objects)
        {
            allegiance[$"wres:bswd:{worldObject.Ordinal:D4}"] = worldObject.Allegiance;
        }

        if (allegiance.Count != manifest.VisibleObjectCount)
        {
            throw new InvalidDataException(
                "The Level 100 base-world object ordinals are not unique.");
        }

        return allegiance;
    }

    public static Level100ActorDefinitionSet Decode(ReadOnlySpan<byte> manifestBytes)
    {
        Manifest manifest = ReadValidatedManifest(manifestBytes);
        return Decode(manifest);
    }

    private static Manifest ReadValidatedManifest(ReadOnlySpan<byte> manifestBytes)
    {
        if (manifestBytes.Length is < 1 or > MaximumManifestBytes ||
            !StringComparer.Ordinal.Equals(
                Convert.ToHexString(SHA256.HashData(manifestBytes)),
                ExpectedManifestSha256))
        {
            throw new InvalidDataException(
                "The locally materialized Level 100 actor-definition manifest is missing or changed.");
        }

        Manifest manifest = JsonSerializer.Deserialize<Manifest>(
                manifestBytes,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ??
            throw new InvalidDataException("The Level 100 actor-definition manifest is empty.");
        if (!StringComparer.Ordinal.Equals(manifest.Schema, ExpectedSchema) ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                manifest.SourceArchiveSha256,
                ExpectedSourceArchiveSha256) ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                manifest.PhysicsSourceSha256,
                ExpectedPhysicsSourceSha256) ||
            manifest.UnitRecordCount != 35 ||
            manifest.VisibleObjectCount != 33 ||
            manifest.ActorDefinitions.Length != 44 ||
            manifest.SpawnDefinitions.Length != 10 ||
            manifest.WaypointPaths.Length != 8 ||
            manifest.MotionDefinitions.Length != 5 ||
            manifest.ActorDefinitions.Count(definition =>
                definition.DefinitionIdentity.StartsWith("wres:bswd:", StringComparison.Ordinal)) != 33)
        {
            throw new InvalidDataException(
                "The Level 100 actor-definition identity or authored counts changed.");
        }

        return manifest;
    }

    private static Level100ActorDefinitionSet Decode(Manifest manifest)
    {
        var actors = new Level100ActorDefinition[manifest.ActorDefinitions.Length];
        for (int index = 0; index < actors.Length; index++)
        {
            ActorDefinition source = manifest.ActorDefinitions[index];
            actors[index] = new Level100ActorDefinition(
                source.AuthoredOrder,
                source.DefinitionIdentity,
                source.Name,
                EmptyToNull(source.DefinitionName),
                EmptyToNull(source.ScriptName),
                EmptyToNull(source.MeshBinding),
                source.ThingTypeMask,
                source.IsStatic,
                source.Active,
                source.InitialHealth,
                DecodeAuthoredTransform(source.AuthoredTransform),
                DecodePose(source.InitialPose),
                ParseEnum<Level100MissionTargetGroup>(source.TargetGroup, "target group"),
                source.TargetOrdinal,
                source.Trigger is null
                    ? null
                    : ParseEnum<Level100MissionTrigger>(source.Trigger, "trigger"));
        }

        var spawns = new Level100SpawnDefinition[manifest.SpawnDefinitions.Length];
        for (int index = 0; index < spawns.Length; index++)
        {
            SpawnDefinition source = manifest.SpawnDefinitions[index];
            spawns[index] = new Level100SpawnDefinition(
                source.AuthoredOrder,
                source.DefinitionIdentity,
                source.OwnerDefinitionIdentity,
                source.DefinitionName,
                source.SpawnerName,
                source.ScriptName,
                EmptyToNull(source.MeshBinding),
                source.ThingTypeMask,
                source.Active,
                source.InitialHealth,
                DecodePose(source.InitialPose),
                DecodeEmitterTransform(source.AuthoredEmitterTransform),
                ParseEnum<Level100MissionTargetGroup>(source.TargetGroup, "target group"),
                source.FixedTargetOrdinal,
                source.MaximumGroupActors);
        }

        var waypointPaths =
            new Level100WaypointPathDefinition[manifest.WaypointPaths.Length];
        for (int pathIndex = 0; pathIndex < waypointPaths.Length; pathIndex++)
        {
            WaypointPath source = manifest.WaypointPaths[pathIndex];
            var points = new Level100WaypointPointDefinition[source.Points.Length];
            for (int pointIndex = 0; pointIndex < points.Length; pointIndex++)
            {
                WaypointPoint point = source.Points[pointIndex];
                if (point.PositionMillimeters.Length != 3 ||
                    point.RetailComponentsFloatBits.Length != 4)
                {
                    throw new InvalidDataException(
                        "A Level 100 waypoint point changed shape.");
                }
                points[pointIndex] = new Level100WaypointPointDefinition(
                    point.NodeIndex,
                    new SimVector3(
                        point.PositionMillimeters[0],
                        point.PositionMillimeters[1],
                        point.PositionMillimeters[2]),
                    new Level100FloatVector4Bits(
                        point.RetailComponentsFloatBits[0],
                        point.RetailComponentsFloatBits[1],
                        point.RetailComponentsFloatBits[2],
                        point.RetailComponentsFloatBits[3]));
            }
            if (source.TargetChainNodeIndices.Length != points.Length)
            {
                throw new InvalidDataException(
                    $"Level 100 waypoint path '{source.Name}' has " +
                    $"{source.TargetChainNodeIndices.Length} chain entries for " +
                    $"{points.Length} nodes.");
            }
            waypointPaths[pathIndex] = new Level100WaypointPathDefinition(
                source.Name,
                points,
                Array.AsReadOnly(source.TargetChainNodeIndices.ToArray()),
                source.IsClosed);
        }

        var motionDefinitions =
            new Level100ActorMotionDefinition[manifest.MotionDefinitions.Length];
        for (int index = 0; index < motionDefinitions.Length; index++)
        {
            MotionDefinition source = manifest.MotionDefinitions[index];
            motionDefinitions[index] = new Level100ActorMotionDefinition(
                source.AuthoredOrder,
                source.DefinitionName,
                ParseEnum<Level100ActorMotionClass>(
                    source.MotionClass,
                    "motion class"),
                source.BehaviorSerializedType,
                source.BehaviorInternalId,
                source.SteamClassVtableAddress,
                source.ArrivalRadiusMillimeters,
                source.MaximumSpeedFloatBits,
                source.MaximumTurnRadiansPerBaseTickFloatBits,
                source.FullGuideBaseTicks,
                source.CoreGroundOriginOffsetMillimeters);
        }

        return new Level100ActorDefinitionSet(
            actors,
            spawns,
            waypointPaths,
            motionDefinitions);
    }

    private static Level100ActorPoseSnapshot DecodePose(Pose source)
    {
        ArgumentNullException.ThrowIfNull(source);
        return new Level100ActorPoseSnapshot(
            DecodeVector(source.PositionMillimeters, "position"),
            DecodeBasis(source.BasisFloatBits, "basis"),
            DecodeVector(source.LinearVelocityMillimetersPerTick, "linear velocity"),
            DecodeVector(source.AngularVelocityMicroRadiansPerTick, "angular velocity"));
    }

    private static Level100AuthoredTransform DecodeAuthoredTransform(AuthoredTransform source)
    {
        ArgumentNullException.ThrowIfNull(source);
        return new Level100AuthoredTransform(
            DecodeFloatVector(source.RetailPositionFloatBits, "authored position"),
            DecodeFloatVector(source.RetailEulerFloatBits, "authored Euler"),
            DecodeBasis(source.RetailBasisFloatBits, "authored basis"));
    }

    private static Level100FloatVector3Bits DecodeFloatVector(int[] values, string role)
    {
        if (values.Length != 3)
        {
            throw new InvalidDataException($"A Level 100 actor {role} changed shape.");
        }

        return new Level100FloatVector3Bits(values[0], values[1], values[2]);
    }

    private static Level100FloatBasis3Bits DecodeBasis(int[] values, string role)
    {
        if (values.Length != 9)
        {
            throw new InvalidDataException($"A Level 100 actor {role} changed shape.");
        }

        return new Level100FloatBasis3Bits(
            values[0], values[1], values[2],
            values[3], values[4], values[5],
            values[6], values[7], values[8]);
    }

    private static Level100SpawnerTransform DecodeEmitterTransform(EmitterTransform source)
    {
        ArgumentNullException.ThrowIfNull(source);
        if (source.LocalPositionFloatBits.Length != 3 || source.LocalBasisFloatBits.Length != 9)
        {
            throw new InvalidDataException("A Level 100 authored emitter transform changed shape.");
        }

        return new Level100SpawnerTransform(
            new Level100FloatVector3Bits(
                source.LocalPositionFloatBits[0],
                source.LocalPositionFloatBits[1],
                source.LocalPositionFloatBits[2]),
            new Level100FloatBasis3Bits(
                source.LocalBasisFloatBits[0],
                source.LocalBasisFloatBits[1],
                source.LocalBasisFloatBits[2],
                source.LocalBasisFloatBits[3],
                source.LocalBasisFloatBits[4],
                source.LocalBasisFloatBits[5],
                source.LocalBasisFloatBits[6],
                source.LocalBasisFloatBits[7],
                source.LocalBasisFloatBits[8]));
    }

    private static SimVector3 DecodeVector(int[] values, string role)
    {
        if (values.Length != 3)
        {
            throw new InvalidDataException($"A Level 100 actor {role} changed shape.");
        }

        return new SimVector3(values[0], values[1], values[2]);
    }

    private static T ParseEnum<T>(string value, string role)
        where T : struct, Enum =>
        Enum.TryParse(value, ignoreCase: false, out T result) && Enum.IsDefined(result)
            ? result
            : throw new InvalidDataException($"A Level 100 actor {role} is invalid: {value}.");

    private static string? EmptyToNull(string? value) =>
        string.IsNullOrEmpty(value) ? null : value;

    private sealed record Manifest
    {
        public string Schema { get; init; } = string.Empty;
        public string SourceArchiveSha256 { get; init; } = string.Empty;
        public string PhysicsSourceSha256 { get; init; } = string.Empty;
        public int UnitRecordCount { get; init; }
        public int VisibleObjectCount { get; init; }
        public ActorDefinition[] ActorDefinitions { get; init; } = [];
        public MotionDefinition[] MotionDefinitions { get; init; } = [];
        public SpawnDefinition[] SpawnDefinitions { get; init; } = [];
        public WaypointPath[] WaypointPaths { get; init; } = [];
        public WorldObject[] Objects { get; init; } = [];
    }

    private sealed record WorldObject
    {
        public int Ordinal { get; init; }
        public int Allegiance { get; init; }
    }

    private sealed record MotionDefinition
    {
        public int ArrivalRadiusMillimeters { get; init; }
        public int AuthoredOrder { get; init; }
        public int BehaviorInternalId { get; init; }
        public int BehaviorSerializedType { get; init; }
        public string DefinitionName { get; init; } = string.Empty;
        public int? FullGuideBaseTicks { get; init; }
        public int? CoreGroundOriginOffsetMillimeters { get; init; }
        public int? MaximumSpeedFloatBits { get; init; }
        public int? MaximumTurnRadiansPerBaseTickFloatBits { get; init; }
        public string MotionClass { get; init; } = string.Empty;
        public int SteamClassVtableAddress { get; init; }
    }

    private sealed record ActorDefinition
    {
        public bool Active { get; init; }
        public AuthoredTransform AuthoredTransform { get; init; } = new();
        public int AuthoredOrder { get; init; }
        public string DefinitionIdentity { get; init; } = string.Empty;
        public string? DefinitionName { get; init; }
        public int InitialHealth { get; init; }
        public Pose InitialPose { get; init; } = new();
        public bool IsStatic { get; init; }
        public string? MeshBinding { get; init; }
        public string Name { get; init; } = string.Empty;
        public string? ScriptName { get; init; }
        public uint ThingTypeMask { get; init; }
        public string TargetGroup { get; init; } = string.Empty;
        public int TargetOrdinal { get; init; }
        public string? Trigger { get; init; }
    }

    private sealed record SpawnDefinition
    {
        public bool Active { get; init; }
        public EmitterTransform AuthoredEmitterTransform { get; init; } = new();
        public int AuthoredOrder { get; init; }
        public string DefinitionIdentity { get; init; } = string.Empty;
        public string DefinitionName { get; init; } = string.Empty;
        public int FixedTargetOrdinal { get; init; }
        public int InitialHealth { get; init; }
        public Pose InitialPose { get; init; } = new();
        public int MaximumGroupActors { get; init; }
        public string? MeshBinding { get; init; }
        public string OwnerDefinitionIdentity { get; init; } = string.Empty;
        public string ScriptName { get; init; } = string.Empty;
        public string SpawnerName { get; init; } = string.Empty;
        public string TargetGroup { get; init; } = string.Empty;
        public uint ThingTypeMask { get; init; }
    }

    private sealed record WaypointPath
    {
        public string Name { get; init; } = string.Empty;
        public WaypointPoint[] Points { get; init; } = [];

        // Schema v14 shipped these two on 2026-07-27 and nothing read them for
        // three days, so the product walked `Points` - the SERIALIZED order -
        // and the ambient Air Trainer flew `Flyby Path` backwards, from the
        // chain's tail. They are consumed now; see
        // Level100WaypointPathDefinition for the bytes that settle which order
        // retail walks.
        public int[] TargetChainNodeIndices { get; init; } = [];
        public bool IsClosed { get; init; }
    }

    private sealed record WaypointPoint
    {
        public int NodeIndex { get; init; }
        public int[] PositionMillimeters { get; init; } = [];
        public int[] RetailComponentsFloatBits { get; init; } = [];
    }

    private sealed record Pose
    {
        public int[] AngularVelocityMicroRadiansPerTick { get; init; } = [];
        public int[] BasisFloatBits { get; init; } = [];
        public int[] LinearVelocityMillimetersPerTick { get; init; } = [];
        public int[] PositionMillimeters { get; init; } = [];
    }

    private sealed record AuthoredTransform
    {
        public int[] RetailBasisFloatBits { get; init; } = [];
        public int[] RetailEulerFloatBits { get; init; } = [];
        public int[] RetailPositionFloatBits { get; init; } = [];
    }

    private sealed record EmitterTransform
    {
        public int[] LocalBasisFloatBits { get; init; } = [];
        public int[] LocalPositionFloatBits { get; init; } = [];
    }
}
