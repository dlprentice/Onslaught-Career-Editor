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
/// their constructors. Unit life uses Core's existing thousandths convention;
/// type-35 life is absent and its registry zero does not prove invulnerability.
/// </remarks>
public sealed class RetailWorld110InitialConstruction
{
    public const string MaterializedAssetSha256 =
        "6ff0f899aaeaf1322c8089d92235e81d2851c2bc29fa1558028f1d7494115d04";

    private const string ResourceName =
        "OnslaughtRebuild.Core.Assets.Level110.level110-initial-actors.json";

    internal sealed record AttachmentUse(string OwnerIdentity, string ComponentName,
        Level100FloatBasis3Bits ParentInitBasis);
    internal sealed record Inputs(IReadOnlyList<RetailWorld110InitialActorInput> Actors,
        RetailUnitAttachmentPose LocalAttachment, IReadOnlyList<AttachmentUse> AttachmentUses);

    private static readonly Lazy<Inputs> s_inputs =
        new(LoadEmbedded);

    private RetailWorld110InitialConstruction()
    {
        Inputs inputs = s_inputs.Value;
        ActorInputs = inputs.Actors;
        InitialObjectSeeds = RetailWorldInitialObjectSeedAdmission.World110;
        Terrain = RetailWorldTerrain.World110;
        ActorDefinitions = new Level100ActorDefinitionSet(
            ActorInputs.Select(input => input.Actor), [], worldNumber: 110);
        Actors = new Level100ActorRegistry(
            ActorDefinitions, Terrain, initializeSupport: false);
        ComponentInitInputs = PrepareComponentInputs(inputs);
        UnconstructedInitialObjects = Array.AsReadOnly(
            InitialObjectSeeds.Rows.Where(seed => seed.ThingType != 8).ToArray());
    }

    public static RetailWorld110InitialConstruction Create() => new();

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

    public RetailWorld110PlayerConstruction? PlayerConstruction { get; private set; }

    public IReadOnlyList<RetailWorld110InitialActorInput> ActorInputs { get; }

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
        if (root.GetProperty("schema").GetString() != "onslaught.world110-initial-actors.v2" ||
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
        return new(Array.AsReadOnly(rows.ToArray()), localAttachment, Array.AsReadOnly(uses));
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
