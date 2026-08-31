// SPDX-License-Identifier: GPL-3.0-or-later

using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;

namespace OnslaughtRebuild.Core;

/// <summary>
/// Closed type-specific suffix of one serialized retail initial-object seed.
/// These values are inert constructor inputs, not constructed runtime objects.
/// </summary>
public abstract record RetailWorldInitialObjectSeedTail;

public sealed record RetailWorldUnitSeedTail(
    string DefinitionName,
    int Trailer) : RetailWorldInitialObjectSeedTail;

public sealed record RetailWorldStartSeedTail(
    int PlaneModeWord,
    int PlayerNumber) : RetailWorldInitialObjectSeedTail;

public sealed record RetailWorldWaypointSeedTail() : RetailWorldInitialObjectSeedTail;

public sealed record RetailWorldSpawnerSeedTail(
    int Amount,
    int DelayBits,
    int SquadDelayBits,
    int InitialDelayBits,
    int SquadSize,
    string SpawnUnit,
    string SpawnerSpawnScript) : RetailWorldInitialObjectSeedTail;

public sealed record RetailWorldScriptSeedTail() : RetailWorldInitialObjectSeedTail;

public sealed record RetailWorldSquadSeedTail(
    int Amount,
    int Mode,
    string DefinitionName,
    int Trailer) : RetailWorldInitialObjectSeedTail;

public sealed record RetailWorldVolumeSeedTail(
    int RadiusBits) : RetailWorldInitialObjectSeedTail;

/// <summary>
/// One exact World-110 RLWD initial-object row in released serialized order.
/// Float values remain raw IEEE-754 words; no coordinate conversion, actor ID,
/// squad expansion, script execution, or runtime publication is performed.
/// </summary>
public sealed class RetailWorldInitialObjectSeed
{
    internal RetailWorldInitialObjectSeed(
        string objectIdentity,
        int ordinal,
        int recordOffset,
        int serializedByteLength,
        string serializedSha256,
        int thingType,
        int positionXBits,
        int positionYBits,
        int positionZBits,
        int orientationXBits,
        int orientationYBits,
        int orientationZBits,
        int meshNumber,
        int allegiance,
        int target,
        string script,
        string name,
        string spawnScript,
        int activeWord,
        int attachScriptsToUnitsWord,
        RetailWorldInitialObjectSeedTail tail)
    {
        ObjectIdentity = objectIdentity;
        Ordinal = ordinal;
        RecordOffset = recordOffset;
        SerializedByteLength = serializedByteLength;
        SerializedSha256 = serializedSha256;
        ThingType = thingType;
        PositionXBits = positionXBits;
        PositionYBits = positionYBits;
        PositionZBits = positionZBits;
        OrientationXBits = orientationXBits;
        OrientationYBits = orientationYBits;
        OrientationZBits = orientationZBits;
        MeshNumber = meshNumber;
        Allegiance = allegiance;
        Target = target;
        Script = script;
        Name = name;
        SpawnScript = spawnScript;
        ActiveWord = activeWord;
        AttachScriptsToUnitsWord = attachScriptsToUnitsWord;
        Tail = tail;
    }

    public string ObjectIdentity { get; }

    public int Ordinal { get; }

    public int RecordOffset { get; }

    public int SerializedByteLength { get; }

    public string SerializedSha256 { get; }

    public int ThingType { get; }

    public int PositionXBits { get; }

    public int PositionYBits { get; }

    public int PositionZBits { get; }

    public int OrientationXBits { get; }

    public int OrientationYBits { get; }

    public int OrientationZBits { get; }

    public int MeshNumber { get; }

    public int Allegiance { get; }

    public int Target { get; }

    public string Script { get; }

    public string Name { get; }

    public string SpawnScript { get; }

    public int ActiveWord { get; }

    public int AttachScriptsToUnitsWord { get; }

    public RetailWorldInitialObjectSeedTail Tail { get; }

    /// <summary>
    /// Lossless adapter to the existing bounded player-start projection. It is
    /// valid only for a type-15 start seed and does not perform start selection
    /// or construction.
    /// </summary>
    public RetailWorldPlayerStartRecord ToPlayerStartRecord()
    {
        if (Tail is not RetailWorldStartSeedTail start || ThingType != 15)
        {
            throw new InvalidOperationException(
                "Only a type-15 start seed can become a player-start record.");
        }

        return new RetailWorldPlayerStartRecord(
            ObjectIdentity,
            ThingType,
            SerializedByteLength,
            SerializedSha256,
            PositionXBits,
            PositionYBits,
            PositionZBits,
            OrientationXBits,
            OrientationYBits,
            OrientationZBits,
            start.PlaneModeWord,
            start.PlayerNumber);
    }
}

/// <summary>
/// Immutable, complete admission of World 110's 40 serialized RLWD
/// initial-object seeds. The typed views filter the same row instances in the
/// same released order; they do not construct or normalize them.
/// </summary>
public sealed class RetailWorldInitialObjectSeedProjection
{
    private readonly IReadOnlyList<RetailWorldInitialObjectSeed> _rows;
    private readonly IReadOnlyList<RetailWorldInitialObjectSeed> _unitSeeds;
    private readonly IReadOnlyList<RetailWorldInitialObjectSeed> _startSeeds;
    private readonly IReadOnlyList<RetailWorldInitialObjectSeed> _waypointSeeds;
    private readonly IReadOnlyList<RetailWorldInitialObjectSeed> _spawnerSeeds;
    private readonly IReadOnlyList<RetailWorldInitialObjectSeed> _scriptSeeds;
    private readonly IReadOnlyList<RetailWorldInitialObjectSeed> _squadSeeds;
    private readonly IReadOnlyList<RetailWorldInitialObjectSeed> _volumeSeeds;

    internal RetailWorldInitialObjectSeedProjection(
        string schema,
        int worldNumber,
        RetailWorldArchiveIdentity archiveIdentity,
        int rlwdByteLength,
        string rlwdSha256,
        int rlwdInitialObjectHeaderOffset,
        int headerA,
        int headerB,
        int initialObjectCount,
        int treeGroupHeaderOffset,
        string materializedAssetSha256,
        IReadOnlyList<RetailWorldInitialObjectSeed> rows)
    {
        Schema = schema;
        WorldNumber = worldNumber;
        ArchiveIdentity = archiveIdentity;
        RlwdByteLength = rlwdByteLength;
        RlwdSha256 = rlwdSha256;
        RlwdInitialObjectHeaderOffset = rlwdInitialObjectHeaderOffset;
        HeaderA = headerA;
        HeaderB = headerB;
        InitialObjectCount = initialObjectCount;
        TreeGroupHeaderOffset = treeGroupHeaderOffset;
        MaterializedAssetSha256 = materializedAssetSha256;

        RetailWorldInitialObjectSeed[] snapshot = rows.ToArray();
        _rows = Array.AsReadOnly(snapshot);
        _unitSeeds = Filter<RetailWorldUnitSeedTail>(snapshot);
        _startSeeds = Filter<RetailWorldStartSeedTail>(snapshot);
        _waypointSeeds = Filter<RetailWorldWaypointSeedTail>(snapshot);
        _spawnerSeeds = Filter<RetailWorldSpawnerSeedTail>(snapshot);
        _scriptSeeds = Filter<RetailWorldScriptSeedTail>(snapshot);
        _squadSeeds = Filter<RetailWorldSquadSeedTail>(snapshot);
        _volumeSeeds = Filter<RetailWorldVolumeSeedTail>(snapshot);
    }

    public string Schema { get; }

    public int WorldNumber { get; }

    public RetailWorldArchiveIdentity ArchiveIdentity { get; }

    public int RlwdByteLength { get; }

    public string RlwdSha256 { get; }

    public int RlwdInitialObjectHeaderOffset { get; }

    public int HeaderA { get; }

    public int HeaderB { get; }

    public int InitialObjectCount { get; }

    public int TreeGroupHeaderOffset { get; }

    public string MaterializedAssetSha256 { get; }

    public IReadOnlyList<RetailWorldInitialObjectSeed> Rows => _rows;

    public IReadOnlyList<RetailWorldInitialObjectSeed> UnitSeeds => _unitSeeds;

    public IReadOnlyList<RetailWorldInitialObjectSeed> StartSeeds => _startSeeds;

    public IReadOnlyList<RetailWorldInitialObjectSeed> WaypointSeeds => _waypointSeeds;

    public IReadOnlyList<RetailWorldInitialObjectSeed> SpawnerSeeds => _spawnerSeeds;

    public IReadOnlyList<RetailWorldInitialObjectSeed> ScriptSeeds => _scriptSeeds;

    public IReadOnlyList<RetailWorldInitialObjectSeed> SquadSeeds => _squadSeeds;

    public IReadOnlyList<RetailWorldInitialObjectSeed> VolumeSeeds => _volumeSeeds;

    private static IReadOnlyList<RetailWorldInitialObjectSeed> Filter<TTail>(
        IEnumerable<RetailWorldInitialObjectSeed> rows)
        where TTail : RetailWorldInitialObjectSeedTail =>
        Array.AsReadOnly(rows.Where(row => row.Tail is TTail).ToArray());
}

/// <summary>
/// Fail-closed admission of the one locally materialized, embedded World-110
/// all-40 seed asset. There is deliberately no public arbitrary-data overload.
/// </summary>
public static class RetailWorldInitialObjectSeedAdmission
{
    public const string World110Schema =
        "onslaught.world110-initial-object-seeds.v1";

    public const string World110MaterializedAssetSha256 =
        "51e51f5e1d3f7bce52ce99297711b1f299494271af3129828959e726aed04e5a";

    private const string World110ResourceName =
        "OnslaughtRebuild.Core.Assets.Level110.level110-initial-object-seeds.json";
    private const int World110RlwdByteLength = 76_600;
    private const string World110RlwdSha256 =
        "fb56249deac8faf0033f4d4b67688ff72e12d922291c880d75b10599fc739837";
    private const int World110HeaderOffset = 15_709;
    private const int World110FirstRecordOffset = 15_719;
    private const int World110TreeGroupHeaderOffset = 18_327;
    private const int World110RowCount = 40;

    private static readonly string[] s_documentProperties =
    [
        "archive", "census", "headerA", "headerB", "initialObjectCount",
        "rlwdByteLength", "rlwdInitialObjectHeaderOffset", "rlwdSha256", "rows",
        "schema", "treeGroupHeaderA", "treeGroupHeaderB",
        "treeGroupHeaderOffset", "worldNumber",
    ];

    private static readonly string[] s_rowProperties =
    [
        "activeWord", "allegiance", "attachScriptsToUnitsWord", "meshNumber",
        "name", "objectIdentity", "ordinal", "orientationXBits",
        "orientationYBits", "orientationZBits", "positionXBits",
        "positionYBits", "positionZBits", "recordOffset", "script",
        "serializedByteLength", "serializedSha256", "spawnScript", "tail",
        "target", "thingType",
    ];

    private static readonly (int ThingType, int Count)[] s_expectedCensus =
    [
        (8, 10),
        (15, 1),
        (18, 19),
        (19, 1),
        (27, 3),
        (28, 5),
        (36, 1),
    ];

    private static readonly Lazy<RetailWorldInitialObjectSeedProjection> s_world110 =
        new(LoadWorld110Embedded, LazyThreadSafetyMode.ExecutionAndPublication);

    public static RetailWorldInitialObjectSeedProjection World110 => s_world110.Value;

    internal static RetailWorldInitialObjectSeedProjection DecodeWorld110ForTests(
        byte[] source,
        string? expectedSha256 = null)
    {
        ArgumentNullException.ThrowIfNull(source);
        byte[] snapshot = source.ToArray();
        string actualSha256 = Sha256(snapshot);
        return DecodeWorld110(snapshot, expectedSha256 ?? actualSha256);
    }

    private static RetailWorldInitialObjectSeedProjection LoadWorld110Embedded()
    {
        Assembly assembly = typeof(RetailWorldInitialObjectSeedAdmission).Assembly;
        using Stream stream = assembly.GetManifestResourceStream(World110ResourceName) ??
            throw new InvalidDataException(
                "The locally materialized World 110 initial-object seed asset is missing.");
        if (stream.Length is <= 0 or > 1_000_000)
        {
            throw new InvalidDataException(
                "The World 110 initial-object seed asset has an invalid length.");
        }

        var source = new byte[checked((int)stream.Length)];
        stream.ReadExactly(source);
        return DecodeWorld110(source, World110MaterializedAssetSha256);
    }

    private static RetailWorldInitialObjectSeedProjection DecodeWorld110(
        byte[] source,
        string expectedSha256)
    {
        string actualSha256 = Sha256(source);
        if (!StringComparer.Ordinal.Equals(actualSha256, expectedSha256))
        {
            throw new InvalidDataException(
                "The World 110 initial-object seed asset does not match its exact recipe.");
        }

        try
        {
            using JsonDocument json = JsonDocument.Parse(source, new JsonDocumentOptions
            {
                AllowTrailingCommas = false,
                CommentHandling = JsonCommentHandling.Disallow,
                MaxDepth = 16,
            });
            Dictionary<string, JsonElement> document = ReadObject(
                json.RootElement,
                "World 110 seed document",
                s_documentProperties);
            Dictionary<string, JsonElement> archive = ReadObject(
                document["archive"],
                "World 110 archive identity",
                ["relativePath", "sha256"]);

            string schema = ReadString(document["schema"], "schema");
            int worldNumber = ReadInt(document["worldNumber"], "world number");
            string archivePath = ReadString(archive["relativePath"], "archive path");
            string archiveSha256 = ReadString(archive["sha256"], "archive SHA-256");
            int rlwdByteLength = ReadInt(document["rlwdByteLength"], "RLWD length");
            string rlwdSha256 = ReadString(document["rlwdSha256"], "RLWD SHA-256");
            int headerOffset = ReadInt(
                document["rlwdInitialObjectHeaderOffset"],
                "initial-object header offset");
            int headerA = ReadInt(document["headerA"], "initial-object header A");
            int headerB = ReadInt(document["headerB"], "initial-object header B");
            int initialObjectCount = ReadInt(
                document["initialObjectCount"],
                "initial-object count");
            int treeHeaderOffset = ReadInt(
                document["treeGroupHeaderOffset"],
                "tree-group header offset");
            int treeHeaderA = ReadInt(
                document["treeGroupHeaderA"],
                "tree-group header A");
            int treeHeaderB = ReadInt(
                document["treeGroupHeaderB"],
                "tree-group header B");

            if (!StringComparer.Ordinal.Equals(schema, World110Schema) ||
                worldNumber != RetailWorld110LevelActors.WorldNumber ||
                !StringComparer.Ordinal.Equals(
                    archivePath,
                    RetailWorld110LevelActors.SourceArchiveRelativePath) ||
                !StringComparer.Ordinal.Equals(
                    archiveSha256,
                    RetailWorld110LevelActors.SourceArchiveSha256) ||
                rlwdByteLength != World110RlwdByteLength ||
                !StringComparer.Ordinal.Equals(rlwdSha256, World110RlwdSha256) ||
                headerOffset != World110HeaderOffset ||
                headerA != 2 ||
                headerB != 0 ||
                initialObjectCount != World110RowCount ||
                treeHeaderOffset != World110TreeGroupHeaderOffset ||
                treeHeaderA != 0 ||
                treeHeaderB != 2)
            {
                throw new InvalidDataException(
                    "The World 110 initial-object seed envelope changed.");
            }

            ValidateCensus(document["census"]);
            RetailWorldInitialObjectSeed[] rows = ReadRows(document["rows"]);
            return new RetailWorldInitialObjectSeedProjection(
                schema,
                worldNumber,
                new RetailWorldArchiveIdentity(archivePath, archiveSha256),
                rlwdByteLength,
                rlwdSha256,
                headerOffset,
                headerA,
                headerB,
                initialObjectCount,
                treeHeaderOffset,
                actualSha256,
                rows);
        }
        catch (InvalidDataException)
        {
            throw;
        }
        catch (JsonException exception)
        {
            throw new InvalidDataException(
                "The World 110 initial-object seed asset is invalid JSON.",
                exception);
        }
        catch (OverflowException exception)
        {
            throw new InvalidDataException(
                "The World 110 initial-object seed asset contains an out-of-range value.",
                exception);
        }
    }

    private static void ValidateCensus(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Array ||
            element.GetArrayLength() != s_expectedCensus.Length)
        {
            throw new InvalidDataException("The World 110 seed census changed.");
        }

        int index = 0;
        foreach (JsonElement candidate in element.EnumerateArray())
        {
            Dictionary<string, JsonElement> row = ReadObject(
                candidate,
                $"World 110 census row {index}",
                ["count", "thingType"]);
            if (ReadInt(row["thingType"], "census thing type") !=
                    s_expectedCensus[index].ThingType ||
                ReadInt(row["count"], "census count") !=
                    s_expectedCensus[index].Count)
            {
                throw new InvalidDataException("The World 110 seed census changed.");
            }
            index++;
        }
    }

    private static RetailWorldInitialObjectSeed[] ReadRows(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Array ||
            element.GetArrayLength() != World110RowCount)
        {
            throw new InvalidDataException(
                "World 110 requires exactly 40 serialized initial-object seeds.");
        }

        var rows = new RetailWorldInitialObjectSeed[World110RowCount];
        var actualCensus = new Dictionary<int, int>();
        int expectedOffset = World110FirstRecordOffset;
        int index = 0;
        foreach (JsonElement candidate in element.EnumerateArray())
        {
            Dictionary<string, JsonElement> row = ReadObject(
                candidate,
                $"World 110 initial-object seed {index}",
                s_rowProperties);
            int ordinal = ReadInt(row["ordinal"], "seed ordinal");
            int recordOffset = ReadInt(row["recordOffset"], "seed record offset");
            int serializedByteLength = ReadInt(
                row["serializedByteLength"],
                "seed byte length");
            string objectIdentity = ReadString(
                row["objectIdentity"],
                "seed object identity");
            string serializedSha256 = ReadString(
                row["serializedSha256"],
                "seed SHA-256");
            int thingType = ReadInt(row["thingType"], "seed thing type");
            int positionXBits = ReadInt(row["positionXBits"], "position X bits");
            int positionYBits = ReadInt(row["positionYBits"], "position Y bits");
            int positionZBits = ReadInt(row["positionZBits"], "position Z bits");
            int orientationXBits = ReadInt(
                row["orientationXBits"],
                "orientation X bits");
            int orientationYBits = ReadInt(
                row["orientationYBits"],
                "orientation Y bits");
            int orientationZBits = ReadInt(
                row["orientationZBits"],
                "orientation Z bits");
            int meshNumber = ReadInt(row["meshNumber"], "mesh number");
            int allegiance = ReadInt(row["allegiance"], "allegiance");
            int target = ReadInt(row["target"], "target");
            string script = ReadString(row["script"], "script");
            string name = ReadString(row["name"], "name");
            string spawnScript = ReadString(row["spawnScript"], "spawn script");
            int activeWord = ReadInt(row["activeWord"], "active word");
            int attachWord = ReadInt(
                row["attachScriptsToUnitsWord"],
                "attach-scripts word");

            if (ordinal != index ||
                !StringComparer.Ordinal.Equals(
                    objectIdentity,
                    $"wres:rlwd:{ordinal:D4}") ||
                recordOffset != expectedOffset ||
                serializedByteLength <= 0 ||
                !IsSha256(serializedSha256) ||
                !AllFinite(
                    positionXBits,
                    positionYBits,
                    positionZBits,
                    orientationXBits,
                    orientationYBits,
                    orientationZBits) ||
                meshNumber < 0 ||
                allegiance is < 0 or > 2 ||
                target is < -1 or >= World110RowCount ||
                activeWord is not (0 or 1) ||
                attachWord is not (0 or 1))
            {
                throw new InvalidDataException(
                    $"World 110 initial-object seed {index} has an invalid common shape.");
            }

            RetailWorldInitialObjectSeedTail tail = ReadTail(
                thingType,
                row["tail"],
                index);
            rows[index] = new RetailWorldInitialObjectSeed(
                objectIdentity,
                ordinal,
                recordOffset,
                serializedByteLength,
                serializedSha256,
                thingType,
                positionXBits,
                positionYBits,
                positionZBits,
                orientationXBits,
                orientationYBits,
                orientationZBits,
                meshNumber,
                allegiance,
                target,
                script,
                name,
                spawnScript,
                activeWord,
                attachWord,
                tail);
            expectedOffset = checked(expectedOffset + serializedByteLength);
            actualCensus[thingType] = actualCensus.GetValueOrDefault(thingType) + 1;
            index++;
        }

        if (expectedOffset != World110TreeGroupHeaderOffset ||
            actualCensus.Count != s_expectedCensus.Length ||
            s_expectedCensus.Any(expected =>
                actualCensus.GetValueOrDefault(expected.ThingType) != expected.Count))
        {
            throw new InvalidDataException(
                "The World 110 initial-object seed extent or census changed.");
        }

        return rows;
    }

    private static RetailWorldInitialObjectSeedTail ReadTail(
        int thingType,
        JsonElement element,
        int ordinal)
    {
        if (element.ValueKind != JsonValueKind.Object)
        {
            throw new InvalidDataException(
                $"World 110 initial-object seed {ordinal} has no closed tail.");
        }

        JsonElement kindElement = default;
        int kindCount = 0;
        foreach (JsonProperty property in element.EnumerateObject())
        {
            if (StringComparer.Ordinal.Equals(property.Name, "kind"))
            {
                kindElement = property.Value;
                kindCount++;
            }
        }
        if (kindCount != 1)
        {
            throw new InvalidDataException(
                $"World 110 initial-object seed {ordinal} has an invalid tail discriminator.");
        }

        string kind = ReadString(kindElement, "tail kind");
        RetailWorldInitialObjectSeedTail tail = kind switch
        {
            "unit" => ReadUnitTail(element),
            "start" => ReadStartTail(element),
            "waypoint" => ReadEmptyTail(element, "waypoint", new RetailWorldWaypointSeedTail()),
            "spawner" => ReadSpawnerTail(element),
            "script" => ReadEmptyTail(element, "script", new RetailWorldScriptSeedTail()),
            "squad" => ReadSquadTail(element),
            "volume" => ReadVolumeTail(element),
            _ => throw new InvalidDataException(
                $"World 110 initial-object seed {ordinal} has an unsupported tail kind."),
        };

        bool matches = (thingType, tail) switch
        {
            (8, RetailWorldUnitSeedTail) => true,
            (15, RetailWorldStartSeedTail) => true,
            (18, RetailWorldWaypointSeedTail) => true,
            (19, RetailWorldSpawnerSeedTail) => true,
            (27, RetailWorldScriptSeedTail) => true,
            (28, RetailWorldSquadSeedTail) => true,
            (36, RetailWorldVolumeSeedTail) => true,
            _ => false,
        };
        return matches
            ? tail
            : throw new InvalidDataException(
                $"World 110 initial-object seed {ordinal} has a mismatched thing type and tail.");
    }

    private static RetailWorldUnitSeedTail ReadUnitTail(JsonElement element)
    {
        Dictionary<string, JsonElement> row = ReadObject(
            element,
            "unit tail",
            ["definitionName", "kind", "trailer"]);
        string definition = ReadString(row["definitionName"], "unit definition");
        int trailer = ReadInt(row["trailer"], "unit trailer");
        if (definition.Length == 0 || trailer != -1)
        {
            throw new InvalidDataException("A World 110 unit tail is invalid.");
        }
        return new RetailWorldUnitSeedTail(definition, trailer);
    }

    private static RetailWorldStartSeedTail ReadStartTail(JsonElement element)
    {
        Dictionary<string, JsonElement> row = ReadObject(
            element,
            "start tail",
            ["kind", "planeModeWord", "playerNumber"]);
        int planeMode = ReadInt(row["planeModeWord"], "start plane-mode word");
        int playerNumber = ReadInt(row["playerNumber"], "start player number");
        if (planeMode is not (0 or 1) || playerNumber is not (1 or 2))
        {
            throw new InvalidDataException("A World 110 start tail is invalid.");
        }
        return new RetailWorldStartSeedTail(planeMode, playerNumber);
    }

    private static RetailWorldInitialObjectSeedTail ReadEmptyTail(
        JsonElement element,
        string label,
        RetailWorldInitialObjectSeedTail tail)
    {
        _ = ReadObject(element, $"{label} tail", ["kind"]);
        return tail;
    }

    private static RetailWorldSpawnerSeedTail ReadSpawnerTail(JsonElement element)
    {
        Dictionary<string, JsonElement> row = ReadObject(
            element,
            "spawner tail",
            [
                "amount", "delayBits", "initialDelayBits", "kind", "spawnUnit",
                "spawnerSpawnScript", "squadDelayBits", "squadSize",
            ]);
        int amount = ReadInt(row["amount"], "spawner amount");
        int delayBits = ReadInt(row["delayBits"], "spawner delay bits");
        int squadDelayBits = ReadInt(row["squadDelayBits"], "spawner squad-delay bits");
        int initialDelayBits = ReadInt(
            row["initialDelayBits"],
            "spawner initial-delay bits");
        int squadSize = ReadInt(row["squadSize"], "spawner squad size");
        string spawnUnit = ReadString(row["spawnUnit"], "spawner unit");
        string spawnScript = ReadString(
            row["spawnerSpawnScript"],
            "spawner tail script");
        if (amount is <= 0 or > 10_000 ||
            squadSize is <= 0 or > 10_000 ||
            spawnUnit.Length == 0 ||
            !AllFinite(delayBits, squadDelayBits, initialDelayBits))
        {
            throw new InvalidDataException("A World 110 spawner tail is invalid.");
        }
        return new RetailWorldSpawnerSeedTail(
            amount,
            delayBits,
            squadDelayBits,
            initialDelayBits,
            squadSize,
            spawnUnit,
            spawnScript);
    }

    private static RetailWorldSquadSeedTail ReadSquadTail(JsonElement element)
    {
        Dictionary<string, JsonElement> row = ReadObject(
            element,
            "squad tail",
            ["amount", "definitionName", "kind", "mode", "trailer"]);
        int amount = ReadInt(row["amount"], "squad amount");
        int mode = ReadInt(row["mode"], "squad mode");
        string definition = ReadString(row["definitionName"], "squad definition");
        int trailer = ReadInt(row["trailer"], "squad trailer");
        if (amount is <= 0 or > 10_000 ||
            mode is < 0 or > 3 ||
            definition.Length == 0 ||
            trailer != -1)
        {
            throw new InvalidDataException("A World 110 squad tail is invalid.");
        }
        return new RetailWorldSquadSeedTail(amount, mode, definition, trailer);
    }

    private static RetailWorldVolumeSeedTail ReadVolumeTail(JsonElement element)
    {
        Dictionary<string, JsonElement> row = ReadObject(
            element,
            "volume tail",
            ["kind", "radiusBits"]);
        int radiusBits = ReadInt(row["radiusBits"], "volume radius bits");
        if (!AllFinite(radiusBits))
        {
            throw new InvalidDataException("A World 110 volume tail is invalid.");
        }
        return new RetailWorldVolumeSeedTail(radiusBits);
    }

    private static Dictionary<string, JsonElement> ReadObject(
        JsonElement element,
        string label,
        IReadOnlyCollection<string> expectedProperties)
    {
        if (element.ValueKind != JsonValueKind.Object)
        {
            throw new InvalidDataException($"{label} must be a JSON object.");
        }

        var expected = new HashSet<string>(expectedProperties, StringComparer.Ordinal);
        var result = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
        foreach (JsonProperty property in element.EnumerateObject())
        {
            if (!expected.Contains(property.Name) ||
                !result.TryAdd(property.Name, property.Value))
            {
                throw new InvalidDataException(
                    $"{label} has an unknown or duplicate member '{property.Name}'.");
            }
        }
        if (result.Count != expected.Count)
        {
            throw new InvalidDataException($"{label} is missing a required member.");
        }
        return result;
    }

    private static int ReadInt(JsonElement element, string label)
    {
        if (element.ValueKind != JsonValueKind.Number || !element.TryGetInt32(out int value))
        {
            throw new InvalidDataException($"World 110 {label} must be an Int32.");
        }
        return value;
    }

    private static string ReadString(JsonElement element, string label)
    {
        if (element.ValueKind != JsonValueKind.String)
        {
            throw new InvalidDataException($"World 110 {label} must be a string.");
        }
        return element.GetString() ??
            throw new InvalidDataException($"World 110 {label} cannot be null.");
    }

    private static bool AllFinite(params int[] words) =>
        words.All(word => float.IsFinite(BitConverter.Int32BitsToSingle(word)));

    private static bool IsSha256(string value) =>
        value.Length == 64 && value.All(character =>
            character is >= '0' and <= '9' or >= 'a' and <= 'f');

    private static string Sha256(byte[] source) =>
        Convert.ToHexString(SHA256.HashData(source)).ToLowerInvariant();
}
