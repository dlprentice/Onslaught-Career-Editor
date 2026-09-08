// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text.Json;

namespace OnslaughtRebuild.Core;

/// <summary>Raw frontend settings, not object identities or inferred career choices.</summary>
public sealed record RetailWorld110GameSettings(
    int InvertSidesWord,
    int Player1ConfigurationId,
    int Player2ConfigurationId)
{
    /// <summary>CGame ctor 0x0046c210; explicitly select this only for a fresh game object.</summary>
    public static RetailWorld110GameSettings FreshGameDefaults { get; } = new(0, 0, 0);
}

/// <summary>The supported fields transferred into Start's embedded engine initializer.</summary>
public sealed record RetailWorld110EngineInitFields(
    Level100FloatVector3Bits PositionBits,
    Level100FloatVector3Bits EulerBits,
    int Allegiance,
    int ConfigurationId,
    int PlaneModeWord);

public sealed class RetailWorld110StartShell
{
    internal RetailWorld110StartShell(int identity, int readerIdentity, int playerNumber,
        RetailWorldPlayerStartHeightClampResult clamp, RetailWorld110EngineInitFields fields)
    {
        Identity = identity;
        BattleEngineReaderCellIdentity = readerIdentity;
        PlayerNumber = playerNumber;
        HeightClamp = clamp;
        EngineInitFields = fields;
    }

    public int Identity { get; }
    public int BattleEngineReaderCellIdentity { get; }
    public int PlayerNumber { get; }
    public RetailWorldPlayerStartHeightClampResult HeightClamp { get; }
    public RetailWorld110EngineInitFields EngineInitFields { get; }
    public string AuthoredObjectIdentity => HeightClamp.AuthoredObjectIdentity!;
}

/// <summary>
/// Owned engine shell with the supported configuration/state writes performed.
/// These are initialization fields, not final post-Unit-Init life, pose or state.
/// Parts, collision, resource objects and initial events remain unconstructed.
/// </summary>
public sealed class RetailWorld110BattleEngineShell
{
    private RetailBattleEngineConfigurationRecord? _configuration;

    internal RetailWorld110BattleEngineShell(int identity, int readerIdentity,
        RetailWorld110EngineInitFields fields)
    {
        Identity = identity;
        PlayerReaderCellIdentity = readerIdentity;
        InitFields = fields;
    }

    internal void InitializeConfiguration(RetailBattleEngineConfigurationRecord configuration,
        int lifeBits, int energyBits)
    {
        _configuration = configuration;
        ConfigurationLifeBits = lifeBits;
        ConfigurationEnergyBits = energyBits;
        InitialStateWord = InitFields.PlaneModeWord == 0 ? 2 : 3;
        InitialShieldsBits = InitFields.PlaneModeWord == 0 ? energyBits : 0;
        for (int store = 0; store < RetailWeaponStores.StoreCount; store++)
        {
            Stores.StoreOverheat[store] = 0;
            Stores.StoreHeat[store] = configuration.StoreHeat[store];
            Stores.ConfigurationStoreValue[store] = configuration.StoreValue[store];
            Stores.StoreValue[store] = configuration.StoreHeat[store] == 0
                ? configuration.StoreValue[store] : 0;
        }
    }

    public int Identity { get; }
    public int PlayerReaderCellIdentity { get; }
    public RetailWorld110EngineInitFields InitFields { get; }
    public RetailBattleEngineConfigurationRecord Configuration => _configuration ??
        throw new InvalidOperationException("Engine configuration is not initialized.");
    public int ConfigurationLifeBits { get; private set; }
    public int ConfigurationEnergyBits { get; private set; }
    public int InitialStateWord { get; private set; }
    public int InitialShieldsBits { get; private set; }
    public RetailWeaponStores Stores { get; } = new();
}

/// <summary>CPlayer constructor state; its post-load Init/camera/timeout has not run.</summary>
public sealed class RetailWorld110PlayerShell
{
    internal RetailWorld110PlayerShell(int identity, int readerIdentity, int godWord)
    {
        Identity = identity;
        BattleEngineReaderCellIdentity = readerIdentity;
        GodWord = godWord;
    }

    public int Identity { get; }
    public int BattleEngineReaderCellIdentity { get; }
    public int PlayerNumber => 1;
    public int GodWord { get; }
    public int CurrentViewMode => 1;
    public int PreferredControlView => 1;
    public IReadOnlyList<int> Stats { get; } = Array.AsReadOnly(new int[7]);
    public IReadOnlyList<int> ThingKillCounts { get; } = Array.AsReadOnly(new int[5]);
}

/// <summary>
/// Constructs owned Start, engine and player shells from real World110 inputs.
/// No caller supplies identities. This detached construction stage carries
/// supported field/reader operations across otherwise unfinished initializers;
/// it is not a replay of a completed retail LoadWorld/LoadLevel call sequence.
/// </summary>
/// <remarks>
/// CStart's engine reader is published before engine Init. The other two cells
/// stay null: post-load assignment must wait for full world/engine initialization.
/// CComplexThing/CThing render/world publication, engine parts/meshes/collision,
/// cockpit/RWR/targeting, random event scheduling and CPlayer::Init are unresolved
/// here. Start's post-engine-Init template reset is therefore also not applied.
/// This type offers no completion, assignment or playable Simulation method.
/// </remarks>
public sealed class RetailWorld110PlayerConstruction
{
    public const string MaterializedAssetSha256 =
        "3bcd5eac3bf17474f60e67d3f4aa135dd239de9a896d63f64f23c494fe339c7d";
    private const string ResourceName =
        "OnslaughtRebuild.Core.Assets.Level110.level110-player-inputs.json";
    private const int Player1GodWordSaveOffset = 0x2496;

    private sealed record ConfigurationInput(RetailBattleEngineConfigurationRecord Stores,
        int LifeBits, int EnergyBits);
    private sealed record Inputs(string?[] WorldNames, ConfigurationInput[] Configurations);
    private static readonly Lazy<Inputs> s_inputs = new(LoadEmbedded);
    private readonly RetailActiveReaderGraph _readers;

    internal RetailWorld110PlayerConstruction(RetailWorld110InitialConstruction world,
        RetailCareerSave career, RetailWorld110GameSettings settings)
    {
        ArgumentNullException.ThrowIfNull(career);
        ArgumentNullException.ThrowIfNull(settings);
        Settings = settings;
        _readers = world.Readers;
        RetailWorldInitialObjectSeed seed = world.InitialObjectSeeds.StartSeeds.Single();
        var admission = RetailWorldPlayerStartAdmission.Admit(110,
            world.InitialObjectSeeds.ArchiveIdentity, [seed.ToPlayerStartRecord()]);
        var clamp = RetailWorldPlayerStartHeightClamp.Apply(
            admission.ResolveForPlayer(1), world.Terrain.Heightfield);
        int effectivePlayerNumber = settings.InvertSidesWord == 0 ? 1 : 2;
        int configurationId = effectivePlayerNumber == 1
            ? settings.Player1ConfigurationId : settings.Player2ConfigurationId;
        var fields = new RetailWorld110EngineInitFields(
            new(seed.PositionXBits, seed.PositionYBits, clamp.FinalPositionZBits),
            new(seed.OrientationXBits, seed.OrientationYBits, seed.OrientationZBits),
            seed.Allegiance, configurationId,
            ((RetailWorldStartSeedTail)seed.Tail).PlaneModeWord);

        // All shells and reader cells share the world's identity allocator;
        // actor registry IDs remain a separate dense, explicitly mapped domain.
        int startIdentity = world.AllocateObjectIdentity();
        int engineIdentity = world.AllocateObjectIdentity();
        int playerIdentity = world.AllocateObjectIdentity();
        int startReaderIdentity = world.AllocateObjectIdentity();
        int engineReaderIdentity = world.AllocateObjectIdentity();
        int playerReaderIdentity = world.AllocateObjectIdentity();
        _readers.CreateReaderCell(startReaderIdentity);
        _readers.CreateReaderCell(engineReaderIdentity);
        _readers.CreateReaderCell(playerReaderIdentity);
        Start = new(startIdentity, startReaderIdentity, effectivePlayerNumber, clamp, fields);

        Inputs inputs = s_inputs.Value;
        var catalog = new RetailBattleEngineConfigurationCatalog(
            inputs.Configurations.Select(item => item.Stores));
        RetailBattleEngineConfigurationRecord selected = catalog.ResolveConfiguration(
            inputs.WorldNames, inputs.WorldNames.Length, configurationId) ??
            throw new InvalidOperationException("World110 configuration lookup returned no data.");
        ConfigurationInput selectedInput = inputs.Configurations.Single(
            item => ReferenceEquals(item.Stores, selected));
        BattleEngine = new(engineIdentity, engineReaderIdentity, fields);
        _readers.SetReader(startReaderIdentity, engineIdentity);
        BattleEngine.InitializeConfiguration(selected, selectedInput.LifeBits, selectedInput.EnergyBits);
        Player = new(playerIdentity, playerReaderIdentity,
            BinaryPrimitives.ReadInt32LittleEndian(
                career.ContainerBytes.Slice(Player1GodWordSaveOffset, sizeof(int))));
    }

    public RetailWorld110GameSettings Settings { get; }
    public RetailWorld110StartShell Start { get; }
    public RetailWorld110BattleEngineShell BattleEngine { get; }
    public RetailWorld110PlayerShell Player { get; }
    public int? ReaderTargetOf(int readerIdentity) => _readers.TargetOf(readerIdentity);
    public int[] ReadersNewestFirst(int objectIdentity) => _readers.ReadersNewestFirst(objectIdentity);

    private static Inputs LoadEmbedded()
    {
        using Stream stream = typeof(RetailWorld110PlayerConstruction).Assembly
            .GetManifestResourceStream(ResourceName) ??
            throw new InvalidOperationException("Materialize World110 player inputs first.");
        using var memory = new MemoryStream();
        stream.CopyTo(memory);
        byte[] source = memory.ToArray();
        if (!StringComparer.OrdinalIgnoreCase.Equals(
                Convert.ToHexString(SHA256.HashData(source)), MaterializedAssetSha256))
        {
            throw new InvalidOperationException("World110 player input asset identity changed.");
        }
        using JsonDocument document = JsonDocument.Parse(source);
        JsonElement root = document.RootElement;
        string?[] names = root.GetProperty("configurationNames").EnumerateArray()
            .Select(value => value.GetString()).ToArray();
        ConfigurationInput[] configurations = root.GetProperty("records").EnumerateArray()
            .Select(row => new ConfigurationInput(
                new RetailBattleEngineConfigurationRecord(row.GetProperty("name").GetString()!,
                    row.GetProperty("storeHeat").EnumerateArray().Select(value => value.GetInt32()),
                    row.GetProperty("storeValueBits").EnumerateArray()
                        .Select(value => BitConverter.Int32BitsToSingle(value.GetInt32()))),
                row.GetProperty("lifeBits").GetInt32(), row.GetProperty("energyBits").GetInt32()))
            .ToArray();
        return new(names, configurations);
    }
}
