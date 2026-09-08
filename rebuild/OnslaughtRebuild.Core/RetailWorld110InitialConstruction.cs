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
        "5ef08128e6bf0ab2fe59bd036871d4700b95d2330257a285b06dc11ff7110f97";

    private const string ResourceName =
        "OnslaughtRebuild.Core.Assets.Level110.level110-initial-actors.json";

    internal sealed record AttachmentUse(string OwnerIdentity, string ComponentName,
        Level100FloatBasis3Bits ParentInitBasis);
    internal sealed record Inputs(IReadOnlyList<RetailWorld110InitialActorInput> Actors,
        RetailUnitAttachmentPose LocalAttachment, IReadOnlyList<AttachmentUse> AttachmentUses,
        IReadOnlyList<RetailWorld110TreeTableInput> TreeTables,
        IReadOnlyList<RetailWorld110TreeMesh> TreeMeshes, IReadOnlyList<RetailBuildingMesh> BuildingMeshes,
        IReadOnlyList<RetailUnitConstructionUses> BuildingUnitUses,
        IReadOnlyList<RetailUnitWeaponDefinition> BuildingWeaponDefinitions,
        IReadOnlyList<RetailUnitSpawnerDefinition> BuildingSpawnerDefinitions);

    private static readonly Lazy<Inputs> s_inputs =
        new(LoadEmbedded);

    private int _nextObjectIdentity = 1;
    private readonly Dictionary<int, RetailWorld110Tree> _treeListeners = [];
    private readonly LinkedList<IRetailMapWhoOwner> _initializedThings = [];
    private readonly LinkedList<RetailWorld110Building> _namedBuildings = [];
    private readonly LinkedList<RetailWorld110Building> _units = [];
    private readonly List<RetailWorld110Building> _bigThings = [];
    private readonly List<RetailWorld110Building> _buildings = [];
    private readonly LinkedList<RetailBuildingSegment> _segments = [];
    private readonly LinkedList<RetailWorld110Building> _occupancyCandidates = [];
    private readonly List<RetailWorld110Building>[] _factions = [[], []];
    private readonly int[,] _unitCounts = new int[2, 26];
    // On the fresh resource-loaded route, 50d9e0 skips definition-catalog Add.
    // MarkUsed50dc20 can only set an existing exact-name entry; misses stay empty.
    private readonly Dictionary<string, bool> _worldMeshUsage = new(StringComparer.Ordinal);
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
    /// Extends the fresh-process, successful-allocation base-tree prefix through
    /// the first Control Tower's Core initialization. Uses preloaded materialized
    /// mesh geometry; render/resource caches remain adapter work. Shared counters,
    /// lists and effect head start at the fresh lifecycle boundary, not arbitrary
    /// BSWD re-entry. No frame is delivered and this is not a playable Simulation.
    /// </summary>
    public static RetailWorld110InitialConstruction CreateWithControlTower(int randomSeedAtFirstTree)
    {
        var world = new RetailWorld110InitialConstruction(randomSeedAtFirstTree);
        world.InitializeBuildings(1);
        return world;
    }

    /// <summary>
    /// Extends the same fresh resource route through the first three Buildings,
    /// including the factory's attached template and the repair weapon. It does
    /// not spawn a tank, fire/heal, deliver a frame or initialize later objects.
    /// </summary>
    public static RetailWorld110InitialConstruction CreateWithInitialBuildings(int randomSeedAtFirstTree)
    {
        var world = new RetailWorld110InitialConstruction(randomSeedAtFirstTree);
        world.InitializeBuildings(3);
        return world;
    }

    private void InitializeBuildings(int count)
    {
        Inputs inputs = s_inputs.Value;
        for (int index = 0; index < count; index++)
        {
            RetailWorld110InitialActorInput input = ActorInputs[index];
            Level100ActorId actorId = Actors.Snapshot.Actors.Single(
                actor => actor.DefinitionIdentity == input.Actor.DefinitionIdentity).ActorId;
            _buildings.Add(new(this, actorId, input, inputs.BuildingMeshes[index],
                inputs.BuildingUnitUses[index], inputs.BuildingWeaponDefinitions,
                inputs.BuildingSpawnerDefinitions, _events!));
        }
    }

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
        get { foreach (var thing in _initializedThings) if (thing is RetailWorld110Tree tree) yield return tree; }
    }
    public IEnumerable<IRetailMapWhoOwner> InitializedThingsNewestFirst => Enumerate(_initializedThings);
    public IEnumerable<RetailWorld110Building> NamedBuildingsNewestFirst => Enumerate(_namedBuildings);
    public IEnumerable<RetailWorld110Building> UnitsNewestFirst => Enumerate(_units);
    public IEnumerable<RetailBuildingSegment> SegmentsNewestFirst => Enumerate(_segments);
    public IEnumerable<RetailWorld110Building> OccupancyCandidatesNewestFirst => Enumerate(_occupancyCandidates);
    public IReadOnlyList<RetailWorld110Building> Buildings => _buildings.AsReadOnly();
    public IEnumerable<RetailWorld110Building> BigThingsOldestFirst => Enumerate(_bigThings);
    public RetailWorld110Building? ControlTower => _buildings.FirstOrDefault();
    public RetailEffectLink? EffectHead { get; private set; }
    public bool OccupancyActive => false;
    public IReadOnlyList<IReadOnlyList<byte>> OccupancyBitplanes { get; private set; } = [];
    public IReadOnlyList<int> OccupancySlopeThresholdFloatBits { get; private set; } = [];
    public IReadOnlyList<RetailWorld110Building> FactionUnits(int allegiance) => _factions[allegiance].AsReadOnly();
    public int UnitCount(int allegiance, int selector) => _unitCounts[allegiance, selector];
    public int WorldMeshCatalogCount => _worldMeshUsage.Count;
    public bool IsUnitDefinitionUsed(string name) => _worldMeshUsage.TryGetValue(name, out bool used) && used;
    public IReadOnlyDictionary<Level100ActorId, int> ActorWorldIdentities { get; }
    internal RetailMapWho? MapWho { get; private set; }
    internal Level100ReleasedRandom? ReleasedRandom { get; private set; }
    internal RetailEventScheduler? Events => _events;
    public int SpatialEntryCount => MapWho?.Count ?? 0;
    public int? ReleasedRandomSeed => ReleasedRandom?.Seed;
    public int PendingTreeEvents => Trees.Count(tree => !tree.CollisionReady);
    public int PendingEvents => _events?.TotalEvents ?? 0;
    public float EventTime => _events?.Time ?? 0;

    /// <summary>
    /// A read-only query of current membership. Initialization itself consumes
    /// the live callback traversal, not this diagnostic projection.
    /// </summary>
    public IReadOnlyList<RetailWorld110Tree> GetTreeCollisionNeighbors(int treeOrdinal)
    {
        if (MapWho is null) throw new InvalidOperationException("Base trees are not initialized.");
        var neighbors = new List<RetailWorld110Tree>();
        MapWho.VisitInitialCollisionNeighbors(Trees[treeOrdinal].MapEntry,
            entry => { if (entry.Owner is RetailWorld110Tree tree) neighbors.Add(tree); });
        return neighbors.AsReadOnly();
    }

    public int UnconstructedTreeCount => TreeTables.SelectMany(table => table.Groups)
        .Where(group => group.CallsTreeInit).Sum(group => group.Placements.Count) - Trees.Count;

    internal int AllocateObjectIdentity() => checked(_nextObjectIdentity++);
    internal void PublishNamedBuilding(RetailWorld110Building building) => _namedBuildings.AddFirst(building);
    internal void PublishInitializedThing(IRetailMapWhoOwner thing) => _initializedThings.AddFirst(thing);
    internal void PublishUnit(RetailWorld110Building unit) => _units.AddFirst(unit);
    internal void PublishBigThing(RetailWorld110Building unit) => _bigThings.Add(unit);
    internal void PublishSegment(RetailBuildingSegment segment) => _segments.AddFirst(segment);
    internal void PublishFactionUnit(RetailWorld110Building unit) => _factions[unit.Allegiance].Add(unit);
    internal void IncrementUnitCount(int allegiance, int selector) => _unitCounts[allegiance, selector]++;
    internal void MarkUnitDefinitionUsed(string name)
    {
        if (_worldMeshUsage.ContainsKey(name)) _worldMeshUsage[name] = true;
    }
    internal void PublishOccupancyCandidate(RetailWorld110Building building) => _occupancyCandidates.AddFirst(building);
    internal RetailEffectLink AddEffectLink(object owner, int? ownerOffset) =>
        EffectHead = new(owner, ownerOffset, EffectHead);

    private static IEnumerable<T> Enumerate<T>(IEnumerable<T> source)
    {
        foreach (T item in source) yield return item;
    }

    /// <summary>
    /// Advances the owned readiness events only. This is not a World110 game
    /// tick: ordinary actor/script/player listeners are not initialized yet.
    /// </summary>
    public IReadOnlyList<RetailEventDispatch> AdvanceTreeReadinessEvents()
    {
        if (_events is null) throw new InvalidOperationException("Base trees are not initialized.");
        if (ControlTower is not null)
            throw new NotSupportedException("Building listeners require the complete world event dispatcher.");
        _events.AdvanceTime();
        return _events.Flush((_, item) => _treeListeners[item.Listener].HandleCollisionEvent(item)).ToArray();
    }

    private void InitializeBaseTrees(int seed)
    {
        MapWho = new(MidpointRounding.ToEven);
        ReleasedRandom = new(seed);
        _events = new();
        // 50d580/4bc260 before BSWD recursion: three all-set bitplanes, inactive
        // until the later non-base load tail. No invented Building footprint.
        OccupancyBitplanes = Array.AsReadOnly(Enumerable.Range(0, 3).Select(_ =>
            (IReadOnlyList<byte>)Array.AsReadOnly(Enumerable.Repeat((byte)255, 8192).ToArray())).ToArray());
        OccupancySlopeThresholdFloatBits = Array.AsReadOnly(new[] { 35, 45, 60 }.Select(degrees =>
            BitConverter.SingleToInt32Bits((float)(degrees * (double)0.01745329238474369f))).ToArray());
        var trees = new List<RetailWorld110Tree>();
        foreach (RetailWorld110TreeTableInput table in TreeTables)
            foreach (RetailWorld110TreeGroupInput group in table.Groups.Where(group => group.CallsTreeInit))
                foreach (RetailWorld110TreePlacement placement in group.Placements)
                {
                    var tree = new RetailWorld110Tree(AllocateObjectIdentity(), AllocateObjectIdentity(),
                        trees.Count, placement, TreeMeshes[placement.Variant], Terrain.Heightfield,
                        ReleasedRandom, MapWho, _events);
                    _treeListeners.Add(tree.CollisionIdentity, tree);
                    PublishInitializedThing(tree); // CThing publication follows collision Init.
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
        if (root.GetProperty("schema").GetString() != "onslaught.world110-initial-actors.v6" ||
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
        var buildingMeshes = root.GetProperty("buildingMeshes").EnumerateArray().Select(DecodeBuildingMesh).ToArray();
        var buildingUses = root.GetProperty("buildingUnitUses").EnumerateArray().Select(use =>
            new RetailUnitConstructionUses(use.GetProperty("actorDefinitionIdentity").GetString()!,
                DecodeUnitUses(use.GetProperty("weaponUses")), DecodeUnitUses(use.GetProperty("spawnerUses")))).ToArray();
        var weapons = root.GetProperty("buildingWeaponDefinitions").EnumerateArray().Select(weapon =>
        {
            JsonElement mode = weapon.GetProperty("selectedMode");
            return new RetailUnitWeaponDefinition(weapon.GetProperty("definitionName").GetString()!,
                weapon.GetProperty("typeOrdinal").GetInt32(), weapon.GetProperty("chargeRateFloatBits").GetInt32(),
                Array.AsReadOnly(weapon.GetProperty("chargeSlots").EnumerateArray().Select(slot => slot.GetInt32()).ToArray()),
                weapon.GetProperty("consumptionFloatBits").GetInt32(), weapon.GetProperty("ammoStore").GetInt32(),
                weapon.GetProperty("zoomMode").GetInt32(), weapon.GetProperty("adjustAimWord").GetInt32(),
                DecodePhysicsFields(weapon.GetProperty("fields")),
                new(mode.GetProperty("definitionName").GetString()!, mode.GetProperty("typeOrdinal").GetInt32(),
                    DecodePhysicsFields(mode.GetProperty("fields"))));
        }).ToArray();
        var spawners = root.GetProperty("buildingSpawnerDefinitions").EnumerateArray().Select(spawner =>
            new RetailUnitSpawnerDefinition(spawner.GetProperty("definitionName").GetString()!,
                spawner.GetProperty("targetUnitDefinitionName").GetString()!,
                spawner.GetProperty("targetUnitBehaviourSelector").GetInt32(),
                DecodePhysicsFields(spawner.GetProperty("fields")))).ToArray();
        return new(Array.AsReadOnly(rows.ToArray()), localAttachment, Array.AsReadOnly(uses),
            Array.AsReadOnly(treeTables.ToArray()), Array.AsReadOnly(treeMeshes), Array.AsReadOnly(buildingMeshes),
            Array.AsReadOnly(buildingUses), Array.AsReadOnly(weapons), Array.AsReadOnly(spawners));
    }

    private static IReadOnlyList<RetailPhysicsFieldInput> DecodePhysicsFields(JsonElement fields) =>
        Array.AsReadOnly(fields.EnumerateArray().Select(field => new RetailPhysicsFieldInput(
            field.GetProperty("fieldId").GetInt32(), field.GetProperty("rawHex").GetString()!)).ToArray());

    private static IReadOnlyList<RetailUnitConstructionUse> DecodeUnitUses(JsonElement uses) =>
        Array.AsReadOnly(uses.EnumerateArray().Select(use => new RetailUnitConstructionUse(
            use.GetProperty("definitionName").GetString()!, use.GetProperty("tagName").GetString()!,
            use.GetProperty("rawCreationFlags").GetUInt32())).ToArray());

    private static RetailBuildingMesh DecodeBuildingMesh(JsonElement element)
    {
        var parts = element.GetProperty("parts").EnumerateArray().Select(part =>
            new RetailBuildingMeshPart(part.GetProperty("name").GetString()!, part.GetProperty("type").GetInt32(),
                OptionalInt(part.GetProperty("reference")), OptionalInt(part.GetProperty("parent")),
                Array.AsReadOnly(part.GetProperty("children").EnumerateArray().Select(value => value.GetInt32()).ToArray()),
                OptionalInt(part.GetProperty("nmic")), part.GetProperty("numNmic").GetInt32(),
                part.GetProperty("isNmic").GetInt32(), VectorBits(part.GetProperty("halfExtentFloatBits")))).ToArray();
        var emitters = element.GetProperty("emitters").EnumerateArray().Select(emitter =>
            new RetailBuildingEmitter(emitter.GetProperty("name").GetString()!,
                emitter.GetProperty("selector").GetInt32(), OptionalInt(emitter.GetProperty("partOrdinal")))).ToArray();
        return new(element.GetProperty("meshName").GetString()!,
            element.GetProperty("sourceSha256").GetString()!, element.GetProperty("meshRadiusFloatBits").GetInt32(),
            Array.AsReadOnly(element.GetProperty("globalBoundingBoxWords").EnumerateArray()
                .Select(word => word.GetInt32()).ToArray()), Array.AsReadOnly(parts), Array.AsReadOnly(emitters));
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
