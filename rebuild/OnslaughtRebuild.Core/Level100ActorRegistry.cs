// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text;

namespace OnslaughtRebuild.Core;

public readonly record struct Level100ActorId(int Value)
{
    public override string ToString() => Value.ToString(System.Globalization.CultureInfo.InvariantCulture);
}

public static class Level100ReleasedThingTypeMasks
{
    public const uint Ammunition = 4;
    public const uint BattleEngine = 8;
    public const uint ProvenBits = Ammunition | BattleEngine;
}

public readonly record struct SimVector3(int X, int Y, int Z)
{
    public static SimVector3 Zero => new(0, 0, 0);
}

/// <summary>
/// Exact IEEE-754 single-precision components retained from the released mesh
/// emitter. Core treats these as immutable authored data rather than doing
/// presentation or floating-point transform work with them.
/// </summary>
public readonly record struct Level100FloatVector3Bits(int X, int Y, int Z);

public readonly record struct Level100FloatBasis3Bits(
    int Row0X,
    int Row0Y,
    int Row0Z,
    int Row1X,
    int Row1Y,
    int Row1Z,
    int Row2X,
    int Row2Y,
    int Row2Z);

public sealed record Level100SpawnerTransform(
    Level100FloatVector3Bits LocalPositionFloatBits,
    Level100FloatBasis3Bits LocalBasisFloatBits);

public sealed record Level100AuthoredTransform(
    Level100FloatVector3Bits RetailPositionFloatBits,
    Level100FloatVector3Bits RetailEulerFloatBits,
    Level100FloatBasis3Bits RetailBasisFloatBits);

public sealed record Level100ActorPoseSnapshot(
    SimVector3 PositionMillimeters,
    Level100FloatBasis3Bits BasisFloatBits,
    SimVector3 LinearVelocityMillimetersPerTick,
    SimVector3 AngularVelocityMicroRadiansPerTick);

public sealed record Level100ActorDefinition(
    int AuthoredOrder,
    string DefinitionIdentity,
    string Name,
    string? DefinitionName,
    string? ScriptName,
    string? MeshBinding,
    uint ThingTypeMask,
    bool IsStatic,
    bool Active,
    int InitialHealth,
    Level100AuthoredTransform AuthoredTransform,
    Level100ActorPoseSnapshot InitialPose,
    Level100MissionTargetGroup TargetGroup,
    int TargetOrdinal,
    Level100MissionTrigger? Trigger);

public sealed record Level100SpawnDefinition(
    int AuthoredOrder,
    string DefinitionIdentity,
    string OwnerDefinitionIdentity,
    string DefinitionName,
    string SpawnerName,
    string ScriptName,
    string? MeshBinding,
    uint ThingTypeMask,
    bool Active,
    int InitialHealth,
    Level100ActorPoseSnapshot InitialPose,
    Level100SpawnerTransform AuthoredEmitterTransform,
    Level100MissionTargetGroup TargetGroup,
    int FixedTargetOrdinal,
    int MaximumGroupActors);

/// <summary>
/// Immutable, scenario-supplied Level 100 actor definitions. The product
/// adapter decodes these from the locally materialized released WRES/static
/// world; Core owns only validation and a canonical content identity.
/// </summary>
public sealed class Level100ActorDefinitionSet
{
    private static readonly byte[] s_identityMagic =
        Encoding.ASCII.GetBytes("ONSLAUGHT-LEVEL100-ACTOR-DEFINITIONS");

    private readonly IReadOnlyList<Level100ActorDefinition> _actors;
    private readonly IReadOnlyList<Level100SpawnDefinition> _spawns;
    private readonly Dictionary<string, Level100ActorDefinition> _actorsByIdentity;
    private readonly Dictionary<string, Level100SpawnDefinition> _spawnsByIdentity;
    private readonly Dictionary<SpawnKey, Level100SpawnDefinition> _spawnsByRequest;

    public Level100ActorDefinitionSet(
        IEnumerable<Level100ActorDefinition> actors,
        IEnumerable<Level100SpawnDefinition> spawns)
    {
        ArgumentNullException.ThrowIfNull(actors);
        ArgumentNullException.ThrowIfNull(spawns);

        Level100ActorDefinition[] actorArray = actors.ToArray();
        Level100SpawnDefinition[] spawnArray = spawns.ToArray();
        if (actorArray.Length == 0)
        {
            throw new ArgumentException("Level 100 requires at least one actor definition.", nameof(actors));
        }

        _actorsByIdentity = new Dictionary<string, Level100ActorDefinition>(StringComparer.Ordinal);
        for (int index = 0; index < actorArray.Length; index++)
        {
            Level100ActorDefinition definition = actorArray[index] ??
                throw new ArgumentException("Level 100 actor definitions cannot contain null.", nameof(actors));
            ValidateActorDefinition(definition, index);
            if (!_actorsByIdentity.TryAdd(definition.DefinitionIdentity, definition))
            {
                throw new ArgumentException(
                    $"Duplicate Level 100 actor definition identity '{definition.DefinitionIdentity}'.",
                    nameof(actors));
            }
        }

        _spawnsByIdentity = new Dictionary<string, Level100SpawnDefinition>(StringComparer.Ordinal);
        _spawnsByRequest = [];
        for (int index = 0; index < spawnArray.Length; index++)
        {
            Level100SpawnDefinition definition = spawnArray[index] ??
                throw new ArgumentException("Level 100 spawn definitions cannot contain null.", nameof(spawns));
            ValidateSpawnDefinition(definition, index);
            if (!_actorsByIdentity.ContainsKey(definition.OwnerDefinitionIdentity))
            {
                throw new ArgumentException(
                    $"Level 100 spawn owner '{definition.OwnerDefinitionIdentity}' is undefined.",
                    nameof(spawns));
            }

            var key = new SpawnKey(
                definition.OwnerDefinitionIdentity,
                definition.DefinitionName,
                definition.SpawnerName,
                definition.ScriptName);
            if (!_spawnsByIdentity.TryAdd(definition.DefinitionIdentity, definition) ||
                !_spawnsByRequest.TryAdd(key, definition))
            {
                throw new ArgumentException(
                    $"Duplicate Level 100 spawn definition '{definition.DefinitionIdentity}'.",
                    nameof(spawns));
            }
        }

        _actors = Array.AsReadOnly(actorArray);
        _spawns = Array.AsReadOnly(spawnArray);
        IdentitySha256 = ComputeIdentity(actorArray, spawnArray);
    }

    public IReadOnlyList<Level100ActorDefinition> Actors => _actors;

    public IReadOnlyList<Level100SpawnDefinition> Spawns => _spawns;

    public string IdentitySha256 { get; }

    internal Level100ActorDefinition GetActorDefinition(string identity) =>
        _actorsByIdentity.TryGetValue(identity, out Level100ActorDefinition? definition)
            ? definition
            : throw new KeyNotFoundException($"Level 100 actor definition '{identity}' does not exist.");

    internal Level100SpawnDefinition GetSpawnDefinition(string identity) =>
        _spawnsByIdentity.TryGetValue(identity, out Level100SpawnDefinition? definition)
            ? definition
            : throw new KeyNotFoundException($"Level 100 spawn definition '{identity}' does not exist.");

    internal Level100SpawnDefinition? FindSpawnDefinition(
        string ownerDefinitionIdentity,
        string definitionName,
        string spawnerName,
        string scriptName) => _spawnsByRequest.GetValueOrDefault(
            new SpawnKey(ownerDefinitionIdentity, definitionName, spawnerName, scriptName));

    private static void ValidateActorDefinition(Level100ActorDefinition definition, int expectedOrder)
    {
        if (definition.AuthoredOrder != expectedOrder ||
            string.IsNullOrWhiteSpace(definition.DefinitionIdentity) ||
            string.IsNullOrWhiteSpace(definition.Name) ||
            definition.AuthoredTransform is null ||
            definition.InitialPose is null ||
            !HasFiniteAuthoredTransform(definition.AuthoredTransform) ||
            !HasFinitePose(definition.InitialPose) ||
            (definition.ThingTypeMask & ~Level100ReleasedThingTypeMasks.ProvenBits) != 0 ||
            definition.InitialHealth < 0 ||
            definition.TargetOrdinal < 0 ||
            (definition.TargetGroup == Level100MissionTargetGroup.None) !=
                (definition.TargetOrdinal == 0) ||
            (definition.Trigger.HasValue && definition.TargetGroup != Level100MissionTargetGroup.None))
        {
            throw new ArgumentException(
                $"Invalid Level 100 actor definition at authored order {expectedOrder}.");
        }
    }

    private static void ValidateSpawnDefinition(Level100SpawnDefinition definition, int expectedOrder)
    {
        if (definition.AuthoredOrder != expectedOrder ||
            string.IsNullOrWhiteSpace(definition.DefinitionIdentity) ||
            string.IsNullOrWhiteSpace(definition.OwnerDefinitionIdentity) ||
            string.IsNullOrWhiteSpace(definition.DefinitionName) ||
            string.IsNullOrWhiteSpace(definition.SpawnerName) ||
            string.IsNullOrWhiteSpace(definition.ScriptName) ||
            definition.InitialPose is null ||
            definition.AuthoredEmitterTransform is null ||
            !HasFinitePose(definition.InitialPose) ||
            (definition.ThingTypeMask & ~Level100ReleasedThingTypeMasks.ProvenBits) != 0 ||
            definition.InitialHealth < 0 ||
            definition.FixedTargetOrdinal < 0 ||
            (definition.TargetGroup == Level100MissionTargetGroup.None &&
                (definition.FixedTargetOrdinal != 0 || definition.MaximumGroupActors != 0)) ||
            (definition.TargetGroup != Level100MissionTargetGroup.None &&
                (definition.MaximumGroupActors <= 0 ||
                 definition.FixedTargetOrdinal > definition.MaximumGroupActors)) ||
            !HasFiniteEmitterTransform(definition.AuthoredEmitterTransform))
        {
            throw new ArgumentException(
                $"Invalid Level 100 spawn definition at authored order {expectedOrder}.");
        }
    }

    private static bool HasFiniteEmitterTransform(Level100SpawnerTransform transform)
    {
        int[] components =
        [
            transform.LocalPositionFloatBits.X,
            transform.LocalPositionFloatBits.Y,
            transform.LocalPositionFloatBits.Z,
            transform.LocalBasisFloatBits.Row0X,
            transform.LocalBasisFloatBits.Row0Y,
            transform.LocalBasisFloatBits.Row0Z,
            transform.LocalBasisFloatBits.Row1X,
            transform.LocalBasisFloatBits.Row1Y,
            transform.LocalBasisFloatBits.Row1Z,
            transform.LocalBasisFloatBits.Row2X,
            transform.LocalBasisFloatBits.Row2Y,
            transform.LocalBasisFloatBits.Row2Z,
        ];
        return components.All(component => float.IsFinite(BitConverter.Int32BitsToSingle(component)));
    }

    private static bool HasFiniteAuthoredTransform(Level100AuthoredTransform transform)
    {
        int[] components =
        [
            transform.RetailPositionFloatBits.X,
            transform.RetailPositionFloatBits.Y,
            transform.RetailPositionFloatBits.Z,
            transform.RetailEulerFloatBits.X,
            transform.RetailEulerFloatBits.Y,
            transform.RetailEulerFloatBits.Z,
            transform.RetailBasisFloatBits.Row0X,
            transform.RetailBasisFloatBits.Row0Y,
            transform.RetailBasisFloatBits.Row0Z,
            transform.RetailBasisFloatBits.Row1X,
            transform.RetailBasisFloatBits.Row1Y,
            transform.RetailBasisFloatBits.Row1Z,
            transform.RetailBasisFloatBits.Row2X,
            transform.RetailBasisFloatBits.Row2Y,
            transform.RetailBasisFloatBits.Row2Z,
        ];
        return components.All(component => float.IsFinite(BitConverter.Int32BitsToSingle(component)));
    }

    private static bool HasFinitePose(Level100ActorPoseSnapshot pose) =>
        HasFiniteBasis(pose.BasisFloatBits);

    private static bool HasFiniteBasis(Level100FloatBasis3Bits basis) =>
        new[]
        {
            basis.Row0X, basis.Row0Y, basis.Row0Z,
            basis.Row1X, basis.Row1Y, basis.Row1Z,
            basis.Row2X, basis.Row2Y, basis.Row2Z,
        }.All(component => float.IsFinite(BitConverter.Int32BitsToSingle(component)));

    private static string ComputeIdentity(
        IReadOnlyList<Level100ActorDefinition> actors,
        IReadOnlyList<Level100SpawnDefinition> spawns)
    {
        using var stream = new MemoryStream();
        using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true))
        {
            writer.Write(s_identityMagic);
            writer.Write(2);
            writer.Write(actors.Count);
            foreach (Level100ActorDefinition actor in actors)
            {
                writer.Write(actor.AuthoredOrder);
                writer.Write(actor.DefinitionIdentity);
                writer.Write(actor.Name);
                WriteNullableString(writer, actor.DefinitionName);
                WriteNullableString(writer, actor.ScriptName);
                WriteNullableString(writer, actor.MeshBinding);
                writer.Write(actor.ThingTypeMask);
                writer.Write(actor.IsStatic);
                writer.Write(actor.Active);
                writer.Write(actor.InitialHealth);
                WriteVector(writer, actor.AuthoredTransform.RetailPositionFloatBits);
                WriteVector(writer, actor.AuthoredTransform.RetailEulerFloatBits);
                WriteBasis(writer, actor.AuthoredTransform.RetailBasisFloatBits);
                WritePose(writer, actor.InitialPose);
                writer.Write((int)actor.TargetGroup);
                writer.Write(actor.TargetOrdinal);
                writer.Write(actor.Trigger.HasValue);
                if (actor.Trigger.HasValue)
                {
                    writer.Write((int)actor.Trigger.Value);
                }
            }

            writer.Write(spawns.Count);
            foreach (Level100SpawnDefinition spawn in spawns)
            {
                writer.Write(spawn.AuthoredOrder);
                writer.Write(spawn.DefinitionIdentity);
                writer.Write(spawn.OwnerDefinitionIdentity);
                writer.Write(spawn.DefinitionName);
                writer.Write(spawn.SpawnerName);
                writer.Write(spawn.ScriptName);
                WriteNullableString(writer, spawn.MeshBinding);
                writer.Write(spawn.ThingTypeMask);
                writer.Write(spawn.Active);
                writer.Write(spawn.InitialHealth);
                WritePose(writer, spawn.InitialPose);
                WriteVector(writer, spawn.AuthoredEmitterTransform.LocalPositionFloatBits);
                WriteBasis(writer, spawn.AuthoredEmitterTransform.LocalBasisFloatBits);
                writer.Write((int)spawn.TargetGroup);
                writer.Write(spawn.FixedTargetOrdinal);
                writer.Write(spawn.MaximumGroupActors);
            }
        }

        return Convert.ToHexString(SHA256.HashData(stream.ToArray())).ToLowerInvariant();
    }

    private static void WritePose(BinaryWriter writer, Level100ActorPoseSnapshot pose)
    {
        WriteVector(writer, pose.PositionMillimeters);
        WriteBasis(writer, pose.BasisFloatBits);
        WriteVector(writer, pose.LinearVelocityMillimetersPerTick);
        WriteVector(writer, pose.AngularVelocityMicroRadiansPerTick);
    }

    private static void WriteVector(BinaryWriter writer, SimVector3 vector)
    {
        writer.Write(vector.X);
        writer.Write(vector.Y);
        writer.Write(vector.Z);
    }

    private static void WriteVector(BinaryWriter writer, Level100FloatVector3Bits vector)
    {
        writer.Write(vector.X);
        writer.Write(vector.Y);
        writer.Write(vector.Z);
    }

    private static void WriteBasis(BinaryWriter writer, Level100FloatBasis3Bits basis)
    {
        writer.Write(basis.Row0X);
        writer.Write(basis.Row0Y);
        writer.Write(basis.Row0Z);
        writer.Write(basis.Row1X);
        writer.Write(basis.Row1Y);
        writer.Write(basis.Row1Z);
        writer.Write(basis.Row2X);
        writer.Write(basis.Row2Y);
        writer.Write(basis.Row2Z);
    }

    private static void WriteNullableString(BinaryWriter writer, string? value)
    {
        writer.Write(value is not null);
        if (value is not null)
        {
            writer.Write(value);
        }
    }

    private readonly record struct SpawnKey(
        string OwnerDefinitionIdentity,
        string DefinitionName,
        string SpawnerName,
        string ScriptName);
}

public enum Level100ActorLifecycle
{
    Alive = 0,
    StartedDying = 1,
    Destroyed = 2,
}

public enum Level100ActorFactKind
{
    Hit = 1,
    StartedDying = 2,
    Died = 3,
    TriggerDispatchReady = 4,
}

public sealed record Level100ActorFactSnapshot(
    long Sequence,
    Level100ActorFactKind Kind,
    Level100ActorId ActorId,
    Level100ActorId? OtherActorId,
    uint OtherThingTypeMask);

public sealed record Level100ActorSnapshot(
    Level100ActorId ActorId,
    string DefinitionIdentity,
    string Name,
    string? DefinitionName,
    string? ScriptName,
    string? MeshBinding,
    uint ThingTypeMask,
    Level100ActorId? SpawnOwnerId,
    string? SpawnerName,
    bool IsStatic,
    bool Active,
    bool IsObjective,
    Level100ActorLifecycle Lifecycle,
    int Health,
    Level100ActorPoseSnapshot Pose,
    Level100MissionTargetGroup TargetGroup,
    int TargetOrdinal,
    Level100MissionTrigger? Trigger,
    bool TriggerEntered,
    Level100MissionJetModeState? TriggerEntryJetModeState,
    bool TriggerEventDispatched);

public sealed record Level100ActorRegistrySnapshot(
    string DefinitionSetIdentitySha256,
    int NextActorId,
    long NextFactSequence,
    IReadOnlyList<Level100ActorSnapshot> Actors,
    IReadOnlyList<Level100ActorFactSnapshot> PendingFacts);

/// <summary>
/// Native Level 100 object identity and lifecycle owner. It contains no
/// movement, AI, collision, damage, or mission progression policy.
/// </summary>
public sealed class Level100ActorRegistry
{
    private sealed class Actor
    {
        internal required Level100ActorId ActorId { get; init; }
        internal required string DefinitionIdentity { get; init; }
        internal required string Name { get; init; }
        internal string? DefinitionName { get; init; }
        internal string? ScriptName { get; set; }
        internal string? MeshBinding { get; init; }
        internal uint ThingTypeMask { get; init; }
        internal Level100ActorId? SpawnOwnerId { get; init; }
        internal string? SpawnerName { get; init; }
        internal bool IsStatic { get; init; }
        internal bool Active { get; set; }
        internal bool IsObjective { get; set; }
        internal Level100ActorLifecycle Lifecycle { get; set; }
        internal int Health { get; set; }
        internal required Level100ActorPoseSnapshot Pose { get; set; }
        internal Level100MissionTargetGroup TargetGroup { get; init; }
        internal int TargetOrdinal { get; init; }
        internal Level100MissionTrigger? Trigger { get; init; }
        internal bool TriggerEntered { get; set; }
        internal Level100MissionJetModeState? TriggerEntryJetModeState { get; set; }
        internal bool TriggerEventDispatched { get; set; }
    }

    private readonly Level100ActorDefinitionSet _definitions;
    private readonly SortedDictionary<int, Actor> _actors = [];
    private readonly List<Level100ActorFactSnapshot> _pendingFacts = [];
    private int _nextActorId = 1;
    private long _nextFactSequence = 1;

    public Level100ActorRegistry(Level100ActorDefinitionSet definitions)
    {
        _definitions = definitions ?? throw new ArgumentNullException(nameof(definitions));
        foreach (Level100ActorDefinition definition in definitions.Actors)
        {
            Level100ActorId actorId = AllocateId();
            _actors.Add(actorId.Value, CreateActor(actorId, definition));
        }
    }

    public Level100ActorRegistry(
        Level100ActorDefinitionSet definitions,
        Level100ActorRegistrySnapshot snapshot)
    {
        _definitions = definitions ?? throw new ArgumentNullException(nameof(definitions));
        ArgumentNullException.ThrowIfNull(snapshot);
        if (!StringComparer.Ordinal.Equals(
                snapshot.DefinitionSetIdentitySha256,
                definitions.IdentitySha256) ||
            snapshot.NextActorId <= 0 ||
            snapshot.NextFactSequence <= 0)
        {
            throw new ArgumentException(
                "Actor registry snapshot does not match its immutable definition set.",
                nameof(snapshot));
        }

        _nextActorId = snapshot.NextActorId;
        _nextFactSequence = snapshot.NextFactSequence;
        ArgumentNullException.ThrowIfNull(snapshot.Actors);
        ArgumentNullException.ThrowIfNull(snapshot.PendingFacts);
        if (snapshot.Actors.Any(actor => actor is null) ||
            snapshot.PendingFacts.Any(fact => fact is null))
        {
            throw new ArgumentException(
                "Actor registry snapshot contains a null record.",
                nameof(snapshot));
        }

        foreach (Level100ActorSnapshot actor in snapshot.Actors.OrderBy(item => item.ActorId.Value))
        {
            if (actor.ActorId.Value <= 0 || actor.ActorId.Value >= _nextActorId ||
                !_actors.TryAdd(actor.ActorId.Value, RestoreActor(actor)))
            {
                throw new ArgumentException("Actor registry snapshot has invalid identities.", nameof(snapshot));
            }
        }

        if (_actors.Count != _nextActorId - 1 ||
            definitions.Actors.Any(definition =>
                _actors.Values.Count(actor =>
                    !actor.SpawnOwnerId.HasValue &&
                    StringComparer.Ordinal.Equals(
                        actor.DefinitionIdentity,
                        definition.DefinitionIdentity)) != 1))
        {
            throw new ArgumentException(
                "Actor registry snapshot does not contain each authored actor exactly once.",
                nameof(snapshot));
        }

        foreach (Actor actor in _actors.Values)
        {
            ValidateRestoredActor(actor, snapshot);
        }

        if (_actors.Values
            .Where(actor => actor.TargetGroup != Level100MissionTargetGroup.None)
            .GroupBy(actor => (actor.TargetGroup, actor.TargetOrdinal))
            .Any(group => group.Key.TargetOrdinal <= 0 || group.Count() != 1))
        {
            throw new ArgumentException(
                "Actor registry snapshot has duplicate or invalid mission ordinals.",
                nameof(snapshot));
        }

        _pendingFacts.AddRange(snapshot.PendingFacts.OrderBy(item => item.Sequence));
        if (_pendingFacts.Any(item =>
                item.Sequence <= 0 ||
                item.Sequence >= _nextFactSequence ||
                !Enum.IsDefined(item.Kind) ||
                !_actors.ContainsKey(item.ActorId.Value) ||
                (item.OtherActorId.HasValue && !_actors.ContainsKey(item.OtherActorId.Value.Value))) ||
            _pendingFacts.Any(item =>
                (item.OtherThingTypeMask & ~Level100ReleasedThingTypeMasks.ProvenBits) != 0 ||
                (item.Kind != Level100ActorFactKind.Hit &&
                    (item.OtherActorId.HasValue || item.OtherThingTypeMask != 0)) ||
                (item.Kind == Level100ActorFactKind.Hit && item.OtherActorId.HasValue &&
                    _actors[item.OtherActorId.Value.Value].ThingTypeMask != item.OtherThingTypeMask)) ||
            _pendingFacts.Select(item => item.Sequence).Distinct().Count() != _pendingFacts.Count)
        {
            throw new ArgumentException("Actor registry snapshot has invalid fact sequencing.", nameof(snapshot));
        }
    }

    public Level100ActorRegistrySnapshot Snapshot => new(
        _definitions.IdentitySha256,
        _nextActorId,
        _nextFactSequence,
        Array.AsReadOnly(_actors.Values.Select(SnapshotActor).ToArray()),
        Array.AsReadOnly(_pendingFacts.OrderBy(item => item.Sequence).ToArray()));

    public Level100ActorId? GetThingRef(string name)
    {
        ArgumentException.ThrowIfNullOrEmpty(name);
        Actor[] matches = _actors.Values
            .Where(actor => string.Equals(actor.Name, name, StringComparison.Ordinal))
            .ToArray();
        return matches.Length == 1 ? matches[0].ActorId : null;
    }

    public Level100ActorSnapshot GetActor(Level100ActorId actorId) =>
        SnapshotActor(Require(actorId));

    internal Level100ActorPoseSnapshot GetPose(Level100ActorId actorId) =>
        Require(actorId).Pose;

    internal int GetHealth(Level100ActorId actorId) => Require(actorId).Health;

    internal bool IsActive(Level100ActorId actorId) => Require(actorId).Active;

    internal Level100ActorLifecycle GetLifecycle(Level100ActorId actorId) =>
        Require(actorId).Lifecycle;

    public uint GetThingTypeMask(Level100ActorId actorId) => Require(actorId).ThingTypeMask;

    public IReadOnlyList<Level100ActorId> SpawnThing(
        Level100ActorId ownerId,
        string definitionName,
        string spawnerName,
        int count,
        string scriptName)
    {
        Actor owner = Require(ownerId);
        ArgumentException.ThrowIfNullOrEmpty(definitionName);
        ArgumentException.ThrowIfNullOrEmpty(spawnerName);
        ArgumentException.ThrowIfNullOrEmpty(scriptName);
        Level100SpawnDefinition? definition = _definitions.FindSpawnDefinition(
            owner.DefinitionIdentity,
            definitionName,
            spawnerName,
            scriptName);
        if (count != 1 || definition is null)
        {
            throw new InvalidOperationException(
                $"SpawnThing request is outside the supplied Level 100 definition set: " +
                $"{definitionName}/{count}.");
        }

        int ordinal = AllocateMissionOrdinal(definition);
        Level100ActorId actorId = AllocateId();
        _actors.Add(actorId.Value, new Actor
        {
            ActorId = actorId,
            DefinitionIdentity = definition.DefinitionIdentity,
            Name = $"{definitionName} #{actorId.Value}",
            DefinitionName = definitionName,
            ScriptName = scriptName,
            MeshBinding = definition.MeshBinding,
            ThingTypeMask = definition.ThingTypeMask,
            SpawnOwnerId = ownerId,
            SpawnerName = spawnerName,
            IsStatic = false,
            Active = definition.Active,
            Lifecycle = Level100ActorLifecycle.Alive,
            Health = definition.InitialHealth,
            Pose = definition.InitialPose,
            TargetGroup = definition.TargetGroup,
            TargetOrdinal = ordinal,
        });
        return Array.AsReadOnly(new[] { actorId });
    }

    public void Activate(Level100ActorId actorId)
    {
        Actor actor = Require(actorId);
        if (actor.Lifecycle == Level100ActorLifecycle.Destroyed)
        {
            throw new InvalidOperationException("A destroyed Level 100 actor cannot be activated.");
        }

        actor.Active = true;
    }

    public void Deactivate(Level100ActorId actorId)
    {
        Actor actor = Require(actorId);
        actor.Active = false;
        if (actor.Trigger.HasValue && actor.TriggerEntered)
        {
            actor.TriggerEventDispatched = true;
            actor.IsObjective = false;
        }
    }

    public void SetObjective(Level100ActorId actorId, bool objective)
    {
        Actor actor = Require(actorId);
        if (objective && actor.Lifecycle == Level100ActorLifecycle.Destroyed)
        {
            throw new InvalidOperationException(
                "A destroyed Level 100 actor cannot become an objective.");
        }

        actor.IsObjective = objective;
    }

    public void SetScript(Level100ActorId actorId, string scriptName)
    {
        ArgumentException.ThrowIfNullOrEmpty(scriptName);
        if (!Level100MissionProgram.ProgramNames.Contains(scriptName, StringComparer.Ordinal))
        {
            throw new InvalidOperationException($"Unknown Level 100 script '{scriptName}'.");
        }

        Require(actorId).ScriptName = scriptName;
    }

    public void SetPose(Level100ActorId actorId, Level100ActorPoseSnapshot pose)
    {
        ArgumentNullException.ThrowIfNull(pose);
        if (!HasFinitePose(pose))
        {
            throw new ArgumentException("Actor pose basis must contain finite values.", nameof(pose));
        }

        Require(actorId).Pose = pose;
    }

    public void SetHealth(Level100ActorId actorId, int health)
    {
        if (health < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(health));
        }

        Require(actorId).Health = health;
    }

    public void ReportHit(
        Level100ActorId actorId,
        Level100ActorId? otherActorId = null,
        uint otherThingTypeMask = 0)
    {
        _ = Require(actorId);
        if ((otherThingTypeMask & ~Level100ReleasedThingTypeMasks.ProvenBits) != 0)
        {
            throw new ArgumentOutOfRangeException(nameof(otherThingTypeMask));
        }

        if (otherActorId.HasValue)
        {
            uint actorMask = Require(otherActorId.Value).ThingTypeMask;
            if (otherThingTypeMask != 0 && otherThingTypeMask != actorMask)
            {
                throw new ArgumentException("A hit source actor and type mask disagree.");
            }
            otherThingTypeMask = actorMask;
        }

        EnqueueFact(Level100ActorFactKind.Hit, actorId, otherActorId, otherThingTypeMask);
    }

    public bool ReportStartedDying(Level100ActorId actorId)
    {
        Actor actor = Require(actorId);
        if (actor.Lifecycle != Level100ActorLifecycle.Alive)
        {
            return false;
        }

        actor.Lifecycle = Level100ActorLifecycle.StartedDying;
        EnqueueFact(Level100ActorFactKind.StartedDying, actorId, null, 0);
        return true;
    }

    public bool ReportDied(Level100ActorId actorId)
    {
        Actor actor = Require(actorId);
        if (actor.Lifecycle == Level100ActorLifecycle.Destroyed)
        {
            return false;
        }

        actor.Lifecycle = Level100ActorLifecycle.Destroyed;
        actor.Active = false;
        actor.IsObjective = false;
        EnqueueFact(Level100ActorFactKind.Died, actorId, null, 0);
        return true;
    }

    public bool BeginTriggerDispatch(
        Level100ActorId actorId,
        Level100MissionJetModeState entryJetModeState)
    {
        Actor actor = Require(actorId);
        if (!actor.Trigger.HasValue || actor.TriggerEntered)
        {
            return false;
        }

        actor.TriggerEntered = true;
        actor.TriggerEntryJetModeState = entryJetModeState;
        EnqueueFact(Level100ActorFactKind.TriggerDispatchReady, actor.ActorId, null, 0);
        return true;
    }

    public void MarkTriggerEventDispatched(Level100ActorId actorId)
    {
        Actor actor = Require(actorId);
        if (!actor.Trigger.HasValue || !actor.TriggerEntered || actor.TriggerEventDispatched)
        {
            throw new InvalidOperationException("Trigger dispatch is not ready.");
        }

        actor.TriggerEventDispatched = true;
        actor.Active = false;
        actor.IsObjective = false;
    }

    public IReadOnlyList<Level100ActorFactSnapshot> DrainFacts()
    {
        Level100ActorFactSnapshot[] result = _pendingFacts
            .OrderBy(item => item.Sequence)
            .ToArray();
        _pendingFacts.Clear();
        return Array.AsReadOnly(result);
    }

    private int AllocateMissionOrdinal(Level100SpawnDefinition definition)
    {
        if (definition.TargetGroup == Level100MissionTargetGroup.None)
        {
            return 0;
        }

        int ordinal = definition.FixedTargetOrdinal > 0
            ? definition.FixedTargetOrdinal
            : _actors.Values.Count(actor => actor.TargetGroup == definition.TargetGroup) + 1;
        if (ordinal > definition.MaximumGroupActors ||
            _actors.Values.Any(actor =>
                actor.TargetGroup == definition.TargetGroup &&
                actor.TargetOrdinal == ordinal))
        {
            throw new InvalidOperationException(
                $"Released Level 100 spawned an invalid {definition.TargetGroup} actor ordinal {ordinal}.");
        }

        return ordinal;
    }

    private Actor Require(Level100ActorId actorId)
    {
        if (actorId.Value <= 0 || !_actors.TryGetValue(actorId.Value, out Actor? actor))
        {
            throw new KeyNotFoundException($"Level 100 actor {actorId.Value} does not exist.");
        }

        return actor;
    }

    private static bool HasFinitePose(Level100ActorPoseSnapshot pose) =>
        new[]
        {
            pose.BasisFloatBits.Row0X, pose.BasisFloatBits.Row0Y, pose.BasisFloatBits.Row0Z,
            pose.BasisFloatBits.Row1X, pose.BasisFloatBits.Row1Y, pose.BasisFloatBits.Row1Z,
            pose.BasisFloatBits.Row2X, pose.BasisFloatBits.Row2Y, pose.BasisFloatBits.Row2Z,
        }.All(component => float.IsFinite(BitConverter.Int32BitsToSingle(component)));

    private Level100ActorId AllocateId() => new(_nextActorId++);

    private void EnqueueFact(
        Level100ActorFactKind kind,
        Level100ActorId actorId,
        Level100ActorId? otherActorId,
        uint otherThingTypeMask) => _pendingFacts.Add(
            new Level100ActorFactSnapshot(
                _nextFactSequence++, kind, actorId, otherActorId, otherThingTypeMask));

    private static Actor CreateActor(Level100ActorId actorId, Level100ActorDefinition definition) =>
        new()
        {
            ActorId = actorId,
            DefinitionIdentity = definition.DefinitionIdentity,
            Name = definition.Name,
            DefinitionName = definition.DefinitionName,
            ScriptName = definition.ScriptName,
            MeshBinding = definition.MeshBinding,
            ThingTypeMask = definition.ThingTypeMask,
            IsStatic = definition.IsStatic,
            Active = definition.Active,
            Lifecycle = Level100ActorLifecycle.Alive,
            Health = definition.InitialHealth,
            Pose = definition.InitialPose,
            TargetGroup = definition.TargetGroup,
            TargetOrdinal = definition.TargetOrdinal,
            Trigger = definition.Trigger,
        };

    private void ValidateRestoredActor(Actor actor, Level100ActorRegistrySnapshot snapshot)
    {
        if (actor.Pose is null ||
            !HasFinitePose(actor.Pose) ||
            actor.Health < 0 ||
            !Enum.IsDefined(actor.Lifecycle) ||
            (actor.Lifecycle == Level100ActorLifecycle.Destroyed &&
                (actor.Active || actor.IsObjective)) ||
            !Enum.IsDefined(actor.TargetGroup) ||
            (actor.ScriptName is not null &&
                !Level100MissionProgram.ProgramNames.Contains(
                    actor.ScriptName,
                    StringComparer.Ordinal)) ||
            (actor.Trigger.HasValue && !Enum.IsDefined(actor.Trigger.Value)) ||
            (actor.TriggerEntryJetModeState.HasValue &&
                !Enum.IsDefined(actor.TriggerEntryJetModeState.Value)) ||
            (!actor.Trigger.HasValue &&
                (actor.TriggerEntered ||
                 actor.TriggerEntryJetModeState.HasValue ||
                 actor.TriggerEventDispatched)) ||
            (actor.Trigger.HasValue &&
                ((!actor.TriggerEntered &&
                    (actor.TriggerEntryJetModeState.HasValue ||
                     actor.TriggerEventDispatched)) ||
                 (actor.TriggerEntered && !actor.TriggerEntryJetModeState.HasValue))))
        {
            throw new ArgumentException(
                "Actor registry snapshot contains invalid mutable actor state.",
                nameof(snapshot));
        }

        if (actor.SpawnOwnerId.HasValue)
        {
            Level100SpawnDefinition definition = _definitions.GetSpawnDefinition(actor.DefinitionIdentity);
            Actor owner = _actors.GetValueOrDefault(actor.SpawnOwnerId.Value.Value) ??
                throw new ArgumentException(
                    "Actor registry snapshot has a missing spawn owner.",
                    nameof(snapshot));
            if (!StringComparer.Ordinal.Equals(
                    owner.DefinitionIdentity,
                    definition.OwnerDefinitionIdentity) ||
                !StringComparer.Ordinal.Equals(actor.Name, $"{definition.DefinitionName} #{actor.ActorId.Value}") ||
                !StringComparer.Ordinal.Equals(actor.DefinitionName, definition.DefinitionName) ||
                !StringComparer.Ordinal.Equals(actor.ScriptName, definition.ScriptName) ||
                !StringComparer.Ordinal.Equals(actor.SpawnerName, definition.SpawnerName) ||
                !StringComparer.Ordinal.Equals(actor.MeshBinding, definition.MeshBinding) ||
                actor.ThingTypeMask != definition.ThingTypeMask ||
                actor.IsStatic ||
                actor.TargetGroup != definition.TargetGroup ||
                (definition.TargetGroup == Level100MissionTargetGroup.None &&
                    actor.TargetOrdinal != 0) ||
                (definition.TargetGroup != Level100MissionTargetGroup.None &&
                    (actor.TargetOrdinal <= 0 ||
                     actor.TargetOrdinal > definition.MaximumGroupActors ||
                     (definition.FixedTargetOrdinal > 0 &&
                        actor.TargetOrdinal != definition.FixedTargetOrdinal))) ||
                actor.Trigger.HasValue)
            {
                throw new ArgumentException(
                    "Actor registry snapshot changed immutable spawn identity.",
                    nameof(snapshot));
            }
            return;
        }

        Level100ActorDefinition actorDefinition =
            _definitions.GetActorDefinition(actor.DefinitionIdentity);
        if (actor.SpawnerName is not null ||
            !StringComparer.Ordinal.Equals(actor.Name, actorDefinition.Name) ||
            !StringComparer.Ordinal.Equals(actor.DefinitionName, actorDefinition.DefinitionName) ||
            !StringComparer.Ordinal.Equals(actor.MeshBinding, actorDefinition.MeshBinding) ||
            actor.ThingTypeMask != actorDefinition.ThingTypeMask ||
            actor.IsStatic != actorDefinition.IsStatic ||
            actor.TargetGroup != actorDefinition.TargetGroup ||
            actor.TargetOrdinal != actorDefinition.TargetOrdinal ||
            actor.Trigger != actorDefinition.Trigger)
        {
            throw new ArgumentException(
                "Actor registry snapshot changed immutable authored identity.",
                nameof(snapshot));
        }
    }

    private static Actor RestoreActor(Level100ActorSnapshot actor) => new()
    {
        ActorId = actor.ActorId,
        DefinitionIdentity = actor.DefinitionIdentity,
        Name = actor.Name,
        DefinitionName = actor.DefinitionName,
        ScriptName = actor.ScriptName,
        MeshBinding = actor.MeshBinding,
        ThingTypeMask = actor.ThingTypeMask,
        SpawnOwnerId = actor.SpawnOwnerId,
        SpawnerName = actor.SpawnerName,
        IsStatic = actor.IsStatic,
        Active = actor.Active,
        IsObjective = actor.IsObjective,
        Lifecycle = actor.Lifecycle,
        Health = actor.Health,
        Pose = actor.Pose,
        TargetGroup = actor.TargetGroup,
        TargetOrdinal = actor.TargetOrdinal,
        Trigger = actor.Trigger,
        TriggerEntered = actor.TriggerEntered,
        TriggerEntryJetModeState = actor.TriggerEntryJetModeState,
        TriggerEventDispatched = actor.TriggerEventDispatched,
    };

    private static Level100ActorSnapshot SnapshotActor(Actor actor) => new(
        actor.ActorId,
        actor.DefinitionIdentity,
        actor.Name,
        actor.DefinitionName,
        actor.ScriptName,
        actor.MeshBinding,
        actor.ThingTypeMask,
        actor.SpawnOwnerId,
        actor.SpawnerName,
        actor.IsStatic,
        actor.Active,
        actor.IsObjective,
        actor.Lifecycle,
        actor.Health,
        actor.Pose,
        actor.TargetGroup,
        actor.TargetOrdinal,
        actor.Trigger,
        actor.TriggerEntered,
        actor.TriggerEntryJetModeState,
        actor.TriggerEventDispatched);
}
