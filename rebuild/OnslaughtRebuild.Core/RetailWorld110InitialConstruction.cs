// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text.Json;

namespace OnslaughtRebuild.Core;

public sealed record RetailWorld110InitialActorInput(
    int SerializedThingType,
    int? SerializedBehaviourType,
    int? InternalBehaviourSelector,
    int? LifeFloatBits,
    int ActiveWord,
    int Allegiance,
    int Target,
    int MeshNumber,
    string SpawnScript,
    int AttachScriptsToUnitsWord,
    Level100ActorDefinition Actor);

/// <summary>
/// Real arguments prepared for one landing-craft Component Init. Owner identity
/// is construction provenance, not an already-bound child parent reader. No
/// child object, world publication or event dispatch is represented here.
/// </summary>
public sealed record RetailWorld110ComponentInitInput(
    Level100ActorId OwnerActorId,
    string OwnerDefinitionIdentity,
    string ComponentDefinitionName,
    int AttachmentIndex,
    RetailUnitAttachmentPose AttachmentPose,
    Level100FloatVector3Bits RetailEulerFloatBits,
    int Allegiance,
    int ActiveWord,
    int AttachScriptsToUnitsWord,
    string SpawnScript)
{
    public int OrientationTypeWord => 0;
    public string Name => string.Empty;
    public string Script => string.Empty;
}

/// <summary>One serialized XY/variant record, before terrain, yaw or Tree Init.</summary>
public readonly record struct RetailWorld110TreePlacement(
    int PositionXFloatBits, int PositionYFloatBits, int Variant);

public sealed record RetailWorld110TreeGroupInput(
    string Name,
    int HeaderOffset,
    int RecordsOffset,
    string RecordsSha256,
    bool CallsTreeInit,
    IReadOnlyList<RetailWorld110TreePlacement> Placements);

/// <summary>
/// An ordered table read by LoadWorld. Only BSWD pines call Tree Init in this
/// world. Ferns and the repeated RLWD table are consumed without creating trees.
/// CallsTreeInit describes the measured retail branch, not completed Core work.
/// </summary>
public sealed record RetailWorld110TreeTableInput(
    string SourceChunk,
    string SourceSha256,
    int HeaderOffset,
    int EndOffset,
    IReadOnlyList<RetailWorld110TreeGroupInput> Groups);

/// <summary>
/// Production construction of the admitted direct World 110 actors, before
/// class initialization. This is an incomplete construction stage, not a
/// playable world or a Simulation factory. It allocates Core actor/base state
/// from the real BSWD and ten type-8 RLWD rows; no World 100 fixture is involved.
/// </summary>
/// <remarks>
/// Core actor IDs are local allocation IDs, not retail thing numbers. Authored
/// poses are retained pending class Init ground/water policy. Script names are
/// bound as data but no script is run. The thirty other RLWD objects, two BSWD
/// type-37 objects, player/engine, squad members and spawner output still need
/// complete initialization. The explicit base-tree factory adds initialized
/// pines and their readiness events under stated numerical assumptions.
/// Unit life uses Core's existing thousandths convention;
/// type-35 life is absent and its registry zero does not prove invulnerability.
/// </remarks>
public sealed class RetailWorld110InitialConstruction
{
    public const string MaterializedAssetSha256 =
        "ab47754b2fc547ae88685477b5408907d7598c45f117a05ffa367ae19809e9c8";

    private const string ResourceName =
        "OnslaughtRebuild.Core.Assets.Level110.level110-initial-actors.json";

    internal sealed record AttachmentUse(string OwnerIdentity, string ComponentName,
        Level100FloatBasis3Bits ParentInitBasis);
    internal sealed record Inputs(IReadOnlyList<RetailWorld110InitialActorInput> Actors,
        RetailUnitAttachmentPose LocalAttachment, IReadOnlyList<AttachmentUse> AttachmentUses,
        IReadOnlyList<RetailWorld110TreeTableInput> TreeTables,
        IReadOnlyList<RetailWorld110TreeMesh> TreeMeshes);

    private static readonly Lazy<Inputs> s_inputs =
        new(LoadEmbedded);

    private int _nextObjectIdentity = 1;
    private readonly Dictionary<int, RetailWorld110Tree> _treeListeners = [];
    private readonly LinkedList<RetailWorld110Tree> _initializedTrees = [];
    private RetailEventScheduler? _events;
    internal RetailActiveReaderGraph Readers { get; } = new();

    private RetailWorld110InitialConstruction(int? randomSeedAtFirstTree = null)
    {
        Inputs inputs = s_inputs.Value;
        ActorInputs = inputs.Actors;
        TreeTables = inputs.TreeTables;
        TreeMeshes = inputs.TreeMeshes;
        InitialObjectSeeds = RetailWorldInitialObjectSeedAdmission.World110;
        Terrain = RetailWorldTerrain.World110;
        ActorDefinitions = new Level100ActorDefinitionSet(
            ActorInputs.Select(input => input.Actor), [], worldNumber: 110);
        Actors = new Level100ActorRegistry(
            ActorDefinitions, Terrain, initializeSupport: false);
        ActorWorldIdentities = new System.Collections.ObjectModel.ReadOnlyDictionary<Level100ActorId, int>(
            Actors.Snapshot.Actors.ToDictionary(actor => actor.ActorId, _ => AllocateObjectIdentity()));
        ComponentInitInputs = PrepareComponentInputs(inputs);
        UnconstructedInitialObjects = Array.AsReadOnly(
            InitialObjectSeeds.Rows.Where(seed => seed.ThingType != 8).ToArray());
        if (randomSeedAtFirstTree.HasValue) InitializeBaseTrees(randomSeedAtFirstTree.Value);
    }

    public static RetailWorld110InitialConstruction Create() => new();

    /// <summary>
    /// Constructs the successful fresh-world base-tree prefix using an explicit
    /// RNG state at the first tree. Arithmetic is binary64 with nearest float32
    /// stores and nearest-even FISTP. These are explicit reconstruction assumptions;
    /// the live load's seed/control word and complete load/reset remain unobserved.
    /// </summary>
    public static RetailWorld110InitialConstruction CreateWithBaseTrees(int randomSeedAtFirstTree) =>
        new(randomSeedAtFirstTree);

    /// <summary>
    /// Adds detached player-construction shells with explicit career/settings
    /// inputs. Full world initialization and post-load assignment remain pending.
    /// </summary>
    public static RetailWorld110InitialConstruction Create(
        RetailCareerSave career, RetailWorld110GameSettings settings)
    {
        var world = new RetailWorld110InitialConstruction();
        world.PlayerConstruction = new(world, career, settings);
        return world;
    }

    public static RetailWorld110InitialConstruction Create(
        RetailCareerSave career, RetailWorld110GameSettings settings, int randomSeedAtFirstTree)
    {
        var world = new RetailWorld110InitialConstruction(randomSeedAtFirstTree);
        world.PlayerConstruction = new(world, career, settings);
        return world;
    }

    public RetailWorld110PlayerConstruction? PlayerConstruction { get; private set; }

    public IReadOnlyList<RetailWorld110InitialActorInput> ActorInputs { get; }

    public IReadOnlyList<RetailWorld110TreeTableInput> TreeTables { get; }

    public IReadOnlyList<RetailWorld110TreeMesh> TreeMeshes { get; }
    public IReadOnlyList<RetailWorld110Tree> Trees { get; private set; } = Array.Empty<RetailWorld110Tree>();
    public IEnumerable<RetailWorld110Tree> InitializedTreesNewestFirst
    {
        get { foreach (RetailWorld110Tree tree in _initializedTrees) yield return tree; }
    }
    public IReadOnlyDictionary<Level100ActorId, int> ActorWorldIdentities { get; }
    internal RetailMapWho? MapWho { get; private set; }
    internal Level100ReleasedRandom? ReleasedRandom { get; private set; }
    public int SpatialEntryCount => MapWho?.Count ?? 0;
    public int? ReleasedRandomSeed => ReleasedRandom?.Seed;
    public int PendingTreeEvents => _events?.TotalEvents ?? 0;

    /// <summary>
    /// A read-only query of current membership. Initialization itself consumes
    /// the live callback traversal, not this diagnostic projection.
    /// </summary>
    public IReadOnlyList<RetailWorld110Tree> GetTreeCollisionNeighbors(int treeOrdinal)
    {
        if (MapWho is null) throw new InvalidOperationException("Base trees are not initialized.");
        var neighbors = new List<RetailWorld110Tree>();
        MapWho.VisitInitialCollisionNeighbors(Trees[treeOrdinal].MapEntry,
            entry => neighbors.Add((RetailWorld110Tree)entry.Owner));
        return neighbors.AsReadOnly();
    }

    public int UnconstructedTreeCount => TreeTables.SelectMany(table => table.Groups)
        .Where(group => group.CallsTreeInit).Sum(group => group.Placements.Count) - Trees.Count;

    internal int AllocateObjectIdentity() => checked(_nextObjectIdentity++);

    /// <summary>
    /// Advances the owned readiness events only. This is not a World110 game
    /// tick: ordinary actor/script/player listeners are not initialized yet.
    /// </summary>
    public IReadOnlyList<RetailEventDispatch> AdvanceTreeReadinessEvents()
    {
        if (_events is null) throw new InvalidOperationException("Base trees are not initialized.");
        _events.AdvanceTime();
        return _events.Flush((_, item) => _treeListeners[item.Listener].HandleCollisionEvent(item)).ToArray();
    }

    private void InitializeBaseTrees(int seed)
    {
        MapWho = new(MidpointRounding.ToEven);
        ReleasedRandom = new(seed);
        _events = new();
        var trees = new List<RetailWorld110Tree>();
        foreach (RetailWorld110TreeTableInput table in TreeTables)
            foreach (RetailWorld110TreeGroupInput group in table.Groups.Where(group => group.CallsTreeInit))
                foreach (RetailWorld110TreePlacement placement in group.Placements)
                {
                    var tree = new RetailWorld110Tree(AllocateObjectIdentity(), AllocateObjectIdentity(),
                        trees.Count, placement, TreeMeshes[placement.Variant], Terrain.Heightfield,
                        ReleasedRandom, MapWho, _events);
                    _treeListeners.Add(tree.CollisionIdentity, tree);
                    _initializedTrees.AddFirst(tree); // CThing world publication follows collision Init.
                    trees.Add(tree);
                }
        Trees = trees.AsReadOnly();
    }

    /// <summary>
    /// The four ordered Unit attachment queries and their following Euler
    /// conversion. The admitted parent Init origin survives the ground/water
    /// clamps and delayed collision response. Complete parent/child Init and
    /// world/event ownership remain unfinished; these are incoming arguments.
    /// </summary>
    public IReadOnlyList<RetailWorld110ComponentInitInput> ComponentInitInputs { get; }

    public RetailWorldInitialObjectSeedProjection InitialObjectSeeds { get; }

    public RetailWorldTerrain Terrain { get; }

    public Level100ActorDefinitionSet ActorDefinitions { get; }

    public Level100ActorRegistry Actors { get; }

    public IReadOnlyList<RetailWorldInitialObjectSeed> UnconstructedInitialObjects { get; }

    public IReadOnlyList<int> UnconstructedBaseObjectOrdinals { get; } =
        Array.AsReadOnly(new[] { 21, 22 });

    public Level100ActorRegistry RestoreActors(Level100ActorRegistrySnapshot snapshot) =>
        new(ActorDefinitions, snapshot, Terrain, initializeSupport: false);

    private IReadOnlyList<RetailWorld110ComponentInitInput> PrepareComponentInputs(Inputs inputs)
    {
        var actorsByIdentity = Actors.Snapshot.Actors.ToDictionary(actor => actor.DefinitionIdentity);
        return Array.AsReadOnly(inputs.AttachmentUses.Select(use =>
        {
            RetailWorld110InitialActorInput parent = ActorInputs.Single(
                input => input.Actor.DefinitionIdentity == use.OwnerIdentity);
            // Keep the original float words. The registry's millimetres lose
            // precision and are not a round-trip source for retail transforms.
            var parentPose = new RetailUnitAttachmentPose(
                parent.Actor.AuthoredTransform.RetailPositionFloatBits, use.ParentInitBasis);
            RetailUnitAttachmentPose attachment = RetailUnitAttachmentPose.Transform(
                parentPose, inputs.LocalAttachment);
            return new RetailWorld110ComponentInitInput(
                actorsByIdentity[use.OwnerIdentity].ActorId, use.OwnerIdentity,
                use.ComponentName, 1, attachment, attachment.ToComponentEuler(),
                parent.Allegiance, parent.ActiveWord, parent.AttachScriptsToUnitsWord,
                parent.SpawnScript);
        }).ToArray());
    }

    private static Inputs LoadEmbedded()
    {
        using Stream stream = typeof(RetailWorld110InitialConstruction).Assembly
            .GetManifestResourceStream(ResourceName) ??
            throw new InvalidOperationException(
                "World 110 initial actors are missing; materialize the retail inputs first.");
        using var memory = new MemoryStream();
        stream.CopyTo(memory);
        return Decode(memory.ToArray());
    }

    internal static Inputs Decode(byte[] source)
    {
        ArgumentNullException.ThrowIfNull(source);
        if (!StringComparer.OrdinalIgnoreCase.Equals(
                Convert.ToHexString(SHA256.HashData(source)), MaterializedAssetSha256))
        {
            throw new ArgumentException("World 110 initial actor asset identity changed.", nameof(source));
        }

        using JsonDocument document = JsonDocument.Parse(source);
        JsonElement root = document.RootElement;
        if (root.GetProperty("schema").GetString() != "onslaught.world110-initial-actors.v4" ||
            root.GetProperty("worldNumber").GetInt32() != 110 ||
            root.GetProperty("archiveSha256").GetString() != RetailWorld110LevelActors.SourceArchiveSha256)
        {
            throw new ArgumentException("World 110 initial actor provenance changed.", nameof(source));
        }

        var rows = new List<RetailWorld110InitialActorInput>();
        foreach (JsonElement row in root.GetProperty("rows").EnumerateArray())
        {
            JsonElement actor = row.GetProperty("actor");
            JsonElement authored = actor.GetProperty("authoredTransform");
            JsonElement pose = actor.GetProperty("initialPose");
            var definition = new Level100ActorDefinition(
                actor.GetProperty("authoredOrder").GetInt32(),
                actor.GetProperty("definitionIdentity").GetString()!,
                actor.GetProperty("name").GetString()!,
                actor.GetProperty("definitionName").GetString(),
                actor.GetProperty("scriptName").GetString(),
                actor.GetProperty("meshBinding").GetString(),
                0, // The legacy registry stores only leaf ammunition/engine bits.
                actor.GetProperty("isStatic").GetBoolean(),
                actor.GetProperty("active").GetBoolean(),
                actor.GetProperty("initialHealth").GetInt32(),
                new Level100AuthoredTransform(
                    VectorBits(authored.GetProperty("retailPositionFloatBits")),
                    VectorBits(authored.GetProperty("retailEulerFloatBits")),
                    Basis(authored.GetProperty("retailBasisFloatBits"))),
                new Level100ActorPoseSnapshot(
                    Vector(pose.GetProperty("positionMillimeters")),
                    Basis(pose.GetProperty("basisFloatBits")),
                    Vector(pose.GetProperty("linearVelocityMillimetersPerTick")),
                    Vector(pose.GetProperty("angularVelocityMicroRadiansPerTick"))),
                Level100MissionTargetGroup.None, 0, null);
            rows.Add(new RetailWorld110InitialActorInput(
                row.GetProperty("serializedThingType").GetInt32(),
                OptionalInt(row.GetProperty("serializedBehaviourType")),
                OptionalInt(row.GetProperty("internalBehaviourSelector")),
                OptionalInt(row.GetProperty("lifeFloatBits")),
                row.GetProperty("activeWord").GetInt32(),
                row.GetProperty("allegiance").GetInt32(),
                row.GetProperty("target").GetInt32(),
                row.GetProperty("meshNumber").GetInt32(),
                row.GetProperty("spawnScript").GetString()!,
                row.GetProperty("attachScriptsToUnitsWord").GetInt32(), definition));
        }

        JsonElement attachment = root.GetProperty("componentAttachment");
        if (attachment.GetProperty("emitterTag").GetInt32() != 20 ||
            attachment.GetProperty("selector").GetInt32() != 1 ||
            attachment.GetProperty("partOrdinal").GetInt32() != 31)
        {
            throw new ArgumentException("World110 Component attachment binding changed.", nameof(source));
        }
        var localAttachment = new RetailUnitAttachmentPose(
            VectorBits(attachment.GetProperty("localPositionFloatBits")),
            Basis(attachment.GetProperty("localBasisFloatBits")));
        var uses = attachment.GetProperty("uses").EnumerateArray().Select(use => new AttachmentUse(
            use.GetProperty("parentDefinitionIdentity").GetString()!,
            use.GetProperty("componentDefinitionName").GetString()!,
            Basis(use.GetProperty("parentInitBasisFloatBits")))).ToArray();
        var treeTables = new List<RetailWorld110TreeTableInput>();
        foreach (JsonElement table in root.GetProperty("treeTables").EnumerateArray())
        {
            var groups = new List<RetailWorld110TreeGroupInput>();
            foreach (JsonElement group in table.GetProperty("groups").EnumerateArray())
            {
                var placements = group.GetProperty("placements").EnumerateArray()
                    .Select(placement => new RetailWorld110TreePlacement(
                        placement[0].GetInt32(), placement[1].GetInt32(),
                        placement[2].GetInt32())).ToArray();
                groups.Add(new(group.GetProperty("name").GetString()!,
                    group.GetProperty("headerOffset").GetInt32(),
                    group.GetProperty("recordsOffset").GetInt32(),
                    group.GetProperty("recordsSha256").GetString()!,
                    group.GetProperty("callsTreeInit").GetBoolean(),
                    Array.AsReadOnly(placements)));
            }
            treeTables.Add(new(table.GetProperty("sourceChunk").GetString()!,
                table.GetProperty("sourceSha256").GetString()!,
                table.GetProperty("headerOffset").GetInt32(),
                table.GetProperty("endOffset").GetInt32(), Array.AsReadOnly(groups.ToArray())));
        }
        var treeMeshes = root.GetProperty("treeMeshes").EnumerateArray().Select(mesh =>
            new RetailWorld110TreeMesh(mesh.GetProperty("variant").GetInt32(),
                mesh.GetProperty("meshName").GetString()!, mesh.GetProperty("sourceSha256").GetString()!,
                mesh.GetProperty("meshRadiusFloatBits").GetInt32(),
                Array.AsReadOnly(mesh.GetProperty("globalBoundingBoxWords").EnumerateArray()
                    .Select(word => word.GetInt32()).ToArray()))).ToArray();
        return new(Array.AsReadOnly(rows.ToArray()), localAttachment, Array.AsReadOnly(uses),
            Array.AsReadOnly(treeTables.ToArray()), Array.AsReadOnly(treeMeshes));
    }

    private static int? OptionalInt(JsonElement value) =>
        value.ValueKind == JsonValueKind.Null ? null : value.GetInt32();

    private static SimVector3 Vector(JsonElement value) =>
        new(value[0].GetInt32(), value[1].GetInt32(), value[2].GetInt32());

    private static Level100FloatVector3Bits VectorBits(JsonElement value) =>
        new(value[0].GetInt32(), value[1].GetInt32(), value[2].GetInt32());

    private static Level100FloatBasis3Bits Basis(JsonElement value) => new(
        value[0].GetInt32(), value[1].GetInt32(), value[2].GetInt32(),
        value[3].GetInt32(), value[4].GetInt32(), value[5].GetInt32(),
        value[6].GetInt32(), value[7].GetInt32(), value[8].GetInt32());
}
