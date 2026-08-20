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

public readonly record struct Level100FloatVector4Bits(int X, int Y, int Z, int W);

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

public sealed record Level100WaypointPointDefinition(
    int NodeIndex,
    SimVector3 PositionMillimeters,
    Level100FloatVector4Bits RetailComponentsFloatBits)
{
    public SimVector2 HorizontalPositionMillimeters =>
        new(PositionMillimeters.X, PositionMillimeters.Z);
}

/// <summary>
/// One named released waypoint path: the nodes it owns, in the order the level
/// file SERIALIZES them, plus the order retail actually WALKS them.
/// </summary>
/// <remarks>
/// <para>
/// The two differ, and the difference is the whole point of this type carrying
/// both. <c>Flyby Path</c> serializes <c>[43, 42, 41]</c> and is walked
/// <c>[41, 42, 43]</c>.
/// </para>
/// <para>
/// <b>Retail does not walk the serialized list at all.</b> Read from the
/// pristine specimen
/// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, sha256
/// <c>74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750</c>:
/// </para>
/// <list type="number">
///   <item><c>CWaypoint::InitAndLink</c> (<c>0x005057b0</c>) binds each
///   waypoint's <c>this+0x3c</c> from its own spawn record's <c>+0xa4</c> —
///   <c>mov eax,[ebx+0xa4]</c> / <c>lea ecx,[esi+0x3c]</c> at
///   <c>0x005057fc</c>..<c>0x00505802</c>. That is the marker's successor
///   pointer, and the shipped source of it is the marker record's own
///   <c>target</c> ordinal.</item>
///   <item><c>CScriptEventNB::UpdateWaypointFollowing</c> (<c>0x00538470</c>)
///   advances with <c>mov eax,[esi+0x14]</c> / <c>mov ecx,[eax+0x3c]</c> at
///   <c>0x005384dc</c>, then <c>mov [esi+0x14],ecx</c> at <c>0x005384fd</c>.
///   The cursor is a POINTER to the current waypoint and the next one comes
///   from that waypoint itself. The serialized index list is never consulted
///   after the first node.</item>
///   <item>The self-reference guard three instructions later pushes the
///   developer-authored string at <c>0x0064fe50</c> — <c>"ERROR: Waypoint
///   points to previous"</c> — which only makes sense for waypoints that point
///   at each other.</item>
///   <item>Both script natives seed that cursor with the SINGLE pointer the
///   shared path lookup at <c>0x00505c30</c> returns — no array, so there is
///   nowhere for a serialized order to enter. <c>FollowWaypointWait</c>
///   (<c>0x00537e40</c>) stores it with <c>mov [ebx+0x14],eax</c> at
///   <c>0x00537e73</c> immediately after the call at <c>0x00537e6b</c>;
///   <c>FollowWaypoint</c> (<c>0x00537d70</c>) does the same at
///   <c>0x00537dfe</c> after the call at <c>0x00537d8c</c>, having first
///   pushed the node's <c>+0x1c..+0x28</c> to the unit guide through vtable
///   <c>+0xf4</c>. The wait variant is the one Level 100 actually uses: in the
///   TTD recording of a real Level 100 opening
///   (<c>G:\bea-ttd\play-level100\play-level100.run</c>) <c>0x00537e40</c>
///   executes 3 times and <c>0x00537d70</c> 0 times.</item>
/// </list>
/// <para>
/// A NULL successor ends the walk, which is the shipped <c>target == -1</c>
/// terminator. A chain that closes on its own head therefore never ends;
/// <see cref="IsClosed"/> is that fact, and two of the eight Level 100 paths
/// carry it.
/// </para>
/// </remarks>
/// <param name="Name">The authored path name scripts call it by.</param>
/// <param name="Points">
/// The nodes in SERIALIZED order. Deliberately not re-sorted: this is what the
/// level file holds, and re-sorting it here would destroy the ability to see
/// that the two orders differ.
/// </param>
/// <param name="TargetChainNodeIndices">
/// The same node indices in <c>target</c>-chain order — the traversal order.
/// A permutation of <see cref="Points"/>' node indices.
/// </param>
/// <param name="IsClosed">Whether the chain closes back on its head.</param>
public sealed record Level100WaypointPathDefinition(
    string Name,
    IReadOnlyList<Level100WaypointPointDefinition> Points,
    IReadOnlyList<int> TargetChainNodeIndices,
    bool IsClosed)
{
    /// <summary>
    /// The node visited at step <paramref name="chainIndex"/> of the authored
    /// traversal. This — not <c>Points[i]</c> — is what a follower steers at.
    /// </summary>
    public Level100WaypointPointDefinition ChainPoint(int chainIndex)
    {
        int nodeIndex = TargetChainNodeIndices[chainIndex];
        foreach (Level100WaypointPointDefinition point in Points)
        {
            if (point.NodeIndex == nodeIndex)
            {
                return point;
            }
        }

        throw new InvalidOperationException(
            $"Level 100 waypoint path '{Name}' has no node {nodeIndex}.");
    }
}

public enum Level100ActorMotionClass
{
    GroundVehicle = 1,
    Plane = 2,
    Dropship = 3,
}

/// <summary>
/// Exact released class/radius data and the class-specific Unit fields consumed
/// by the bounded Level 100 mechanics owner. Nullable fields are deliberately
/// absent for classes whose motion is not implemented.
/// </summary>
public sealed record Level100ActorMotionDefinition(
    int AuthoredOrder,
    string DefinitionName,
    Level100ActorMotionClass MotionClass,
    int BehaviorSerializedType,
    int BehaviorInternalId,
    int SteamClassVtableAddress,
    int ArrivalRadiusMillimeters,
    int? MaximumSpeedFloatBits,
    int? MaximumTurnRadiansPerBaseTickFloatBits,
    int? FullGuideBaseTicks,
    int? CoreGroundOriginOffsetMillimeters);

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
    private readonly IReadOnlyList<Level100WaypointPathDefinition> _waypointPaths;
    private readonly IReadOnlyList<Level100ActorMotionDefinition> _motionDefinitions;
    private readonly Dictionary<string, Level100ActorDefinition> _actorsByIdentity;
    private readonly Dictionary<string, Level100SpawnDefinition> _spawnsByIdentity;
    private readonly Dictionary<SpawnKey, Level100SpawnDefinition> _spawnsByRequest;
    private readonly Dictionary<string, Level100WaypointPathDefinition> _waypointPathsByName;
    private readonly Dictionary<string, Level100ActorMotionDefinition> _motionDefinitionsByName;

    public Level100ActorDefinitionSet(
        IEnumerable<Level100ActorDefinition> actors,
        IEnumerable<Level100SpawnDefinition> spawns,
        IEnumerable<Level100WaypointPathDefinition>? waypointPaths = null,
        IEnumerable<Level100ActorMotionDefinition>? motionDefinitions = null)
    {
        ArgumentNullException.ThrowIfNull(actors);
        ArgumentNullException.ThrowIfNull(spawns);

        Level100ActorDefinition[] actorArray = actors.ToArray();
        Level100SpawnDefinition[] spawnArray = spawns.ToArray();
        Level100WaypointPathDefinition[] waypointPathArray =
            waypointPaths?.ToArray() ?? [];
        Level100ActorMotionDefinition[] motionDefinitionArray =
            motionDefinitions?.ToArray() ?? [];
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
        _waypointPathsByName = new Dictionary<string, Level100WaypointPathDefinition>(
            StringComparer.Ordinal);
        for (int pathIndex = 0; pathIndex < waypointPathArray.Length; pathIndex++)
        {
            Level100WaypointPathDefinition path = waypointPathArray[pathIndex] ??
                throw new ArgumentException(
                    "Level 100 waypoint paths cannot contain null.",
                    nameof(waypointPaths));
            if (string.IsNullOrWhiteSpace(path.Name) ||
                path.Points is null ||
                path.Points.Count == 0)
            {
                throw new ArgumentException(
                    $"Invalid Level 100 waypoint path at authored order {pathIndex}.",
                    nameof(waypointPaths));
            }

            Level100WaypointPointDefinition[] points = path.Points.ToArray();
            // The traversal chain must be a permutation of the path's own
            // serialized nodes. Retail cannot express anything else: the
            // successor pointer each marker carries is a pointer to another
            // marker of the same path, and a path lookup returns one head. A
            // chain that named a node the path does not own, repeated one, or
            // dropped one would be a decode defect, and this is where it stops.
            int[] chain = (path.TargetChainNodeIndices ?? []).ToArray();
            if (points.Any(point =>
                    point.NodeIndex < 0 ||
                    !HasFiniteWaypointComponents(point.RetailComponentsFloatBits)) ||
                chain.Length != points.Length ||
                chain.Distinct().Count() != chain.Length ||
                chain.Any(node => !points.Any(point => point.NodeIndex == node)) ||
                !_waypointPathsByName.TryAdd(
                    path.Name,
                    new Level100WaypointPathDefinition(
                        path.Name,
                        Array.AsReadOnly(points),
                        Array.AsReadOnly(chain),
                        path.IsClosed)))
            {
                throw new ArgumentException(
                    $"Invalid or duplicate Level 100 waypoint path '{path.Name}'.",
                    nameof(waypointPaths));
            }
        }

        _waypointPaths = Array.AsReadOnly(
            waypointPathArray
                .Select(path => _waypointPathsByName[path.Name])
                .ToArray());
        _motionDefinitionsByName =
            new Dictionary<string, Level100ActorMotionDefinition>(StringComparer.Ordinal);
        for (int index = 0; index < motionDefinitionArray.Length; index++)
        {
            Level100ActorMotionDefinition definition = motionDefinitionArray[index] ??
                throw new ArgumentException(
                    "Level 100 motion definitions cannot contain null.",
                    nameof(motionDefinitions));
            ValidateMotionDefinition(definition, index);
            if (!actorArray.Any(actor =>
                    StringComparer.Ordinal.Equals(
                        actor.DefinitionName,
                        definition.DefinitionName)) &&
                !spawnArray.Any(spawn =>
                    StringComparer.Ordinal.Equals(
                        spawn.DefinitionName,
                        definition.DefinitionName)))
            {
                throw new ArgumentException(
                    $"Level 100 motion definition '{definition.DefinitionName}' has no actor.",
                    nameof(motionDefinitions));
            }
            if (!_motionDefinitionsByName.TryAdd(
                    definition.DefinitionName,
                    definition))
            {
                throw new ArgumentException(
                    $"Duplicate Level 100 motion definition '{definition.DefinitionName}'.",
                    nameof(motionDefinitions));
            }
        }

        _motionDefinitions = Array.AsReadOnly(motionDefinitionArray);
        IdentitySha256 = ComputeIdentity(
            actorArray,
            spawnArray,
            _waypointPaths,
            _motionDefinitions);
    }

    public IReadOnlyList<Level100ActorDefinition> Actors => _actors;

    public IReadOnlyList<Level100SpawnDefinition> Spawns => _spawns;

    public IReadOnlyList<Level100WaypointPathDefinition> WaypointPaths => _waypointPaths;

    public IReadOnlyList<Level100ActorMotionDefinition> MotionDefinitions =>
        _motionDefinitions;

    public string IdentitySha256 { get; }

    public Level100WaypointPathDefinition GetWaypointPath(string name) =>
        _waypointPathsByName.TryGetValue(name, out Level100WaypointPathDefinition? path)
            ? path
            : throw new KeyNotFoundException($"Level 100 waypoint path '{name}' does not exist.");

    public Level100ActorMotionDefinition GetMotionDefinition(string name) =>
        _motionDefinitionsByName.TryGetValue(name, out Level100ActorMotionDefinition? definition)
            ? definition
            : throw new KeyNotFoundException(
                $"Level 100 actor motion definition '{name}' does not exist.");

    internal Level100ActorMotionDefinition? FindMotionDefinition(string? name) =>
        name is not null &&
        _motionDefinitionsByName.TryGetValue(
            name,
            out Level100ActorMotionDefinition? definition)
            ? definition
            : null;

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

    private static bool HasFiniteWaypointComponents(
        Level100FloatVector4Bits components) =>
        new[] { components.X, components.Y, components.Z, components.W }
            .All(component =>
                float.IsFinite(BitConverter.Int32BitsToSingle(component)));

    private static void ValidateMotionDefinition(
        Level100ActorMotionDefinition definition,
        int expectedOrder)
    {
        bool groundVehicle =
            definition.MotionClass == Level100ActorMotionClass.GroundVehicle;
        bool hasValidGroundFields =
            definition.MaximumSpeedFloatBits.HasValue &&
            definition.MaximumTurnRadiansPerBaseTickFloatBits.HasValue &&
            float.IsFinite(BitConverter.Int32BitsToSingle(
                definition.MaximumSpeedFloatBits.Value)) &&
            BitConverter.Int32BitsToSingle(
                definition.MaximumSpeedFloatBits.Value) > 0.0f &&
            float.IsFinite(BitConverter.Int32BitsToSingle(
                definition.MaximumTurnRadiansPerBaseTickFloatBits.Value)) &&
            BitConverter.Int32BitsToSingle(
                definition.MaximumTurnRadiansPerBaseTickFloatBits.Value) > 0.0f &&
            definition.FullGuideBaseTicks is > 0 &&
            definition.CoreGroundOriginOffsetMillimeters is > 0;
        bool hasNoGroundFields =
            !definition.MaximumSpeedFloatBits.HasValue &&
            !definition.MaximumTurnRadiansPerBaseTickFloatBits.HasValue &&
            !definition.FullGuideBaseTicks.HasValue &&
            !definition.CoreGroundOriginOffsetMillimeters.HasValue;

        if (definition.AuthoredOrder != expectedOrder ||
            string.IsNullOrWhiteSpace(definition.DefinitionName) ||
            !Enum.IsDefined(definition.MotionClass) ||
            definition.BehaviorSerializedType <= 0 ||
            definition.BehaviorInternalId < 0 ||
            definition.SteamClassVtableAddress <= 0 ||
            definition.ArrivalRadiusMillimeters <= 0 ||
            (groundVehicle
                ? !hasValidGroundFields
                : !hasNoGroundFields))
        {
            throw new ArgumentException(
                $"Invalid Level 100 motion definition at authored order {expectedOrder}.");
        }
    }

    private static string ComputeIdentity(
        IReadOnlyList<Level100ActorDefinition> actors,
        IReadOnlyList<Level100SpawnDefinition> spawns,
        IReadOnlyList<Level100WaypointPathDefinition> waypointPaths,
        IReadOnlyList<Level100ActorMotionDefinition> motionDefinitions)
    {
        using var stream = new MemoryStream();
        using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true))
        {
            writer.Write(s_identityMagic);
            writer.Write(6);
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

            writer.Write(waypointPaths.Count);
            foreach (Level100WaypointPathDefinition path in waypointPaths)
            {
                writer.Write(path.Name);
                writer.Write(path.Points.Count);
                foreach (Level100WaypointPointDefinition point in path.Points)
                {
                    writer.Write(point.NodeIndex);
                    writer.Write(point.PositionMillimeters.X);
                    writer.Write(point.PositionMillimeters.Y);
                    writer.Write(point.PositionMillimeters.Z);
                    writer.Write(point.RetailComponentsFloatBits.X);
                    writer.Write(point.RetailComponentsFloatBits.Y);
                    writer.Write(point.RetailComponentsFloatBits.Z);
                    writer.Write(point.RetailComponentsFloatBits.W);
                }

                // Version 6. The traversal chain and the loop flag are hashed
                // because they DECIDE MOTION: two definition sets with the same
                // 30 node positions and different chains produce different
                // routes. Leaving them out would let exactly the class of
                // defect this pair was added to fix - a route silently walked
                // in the wrong order - carry an unchanged definition identity.
                writer.Write(path.TargetChainNodeIndices.Count);
                foreach (int nodeIndex in path.TargetChainNodeIndices)
                {
                    writer.Write(nodeIndex);
                }

                writer.Write(path.IsClosed);
            }

            writer.Write(motionDefinitions.Count);
            foreach (Level100ActorMotionDefinition definition in motionDefinitions)
            {
                writer.Write(definition.AuthoredOrder);
                writer.Write(definition.DefinitionName);
                writer.Write((int)definition.MotionClass);
                writer.Write(definition.BehaviorSerializedType);
                writer.Write(definition.BehaviorInternalId);
                writer.Write(definition.SteamClassVtableAddress);
                writer.Write(definition.ArrivalRadiusMillimeters);
                WriteNullableInt(writer, definition.MaximumSpeedFloatBits);
                WriteNullableInt(
                    writer,
                    definition.MaximumTurnRadiansPerBaseTickFloatBits);
                WriteNullableInt(writer, definition.FullGuideBaseTicks);
                WriteNullableInt(
                    writer,
                    definition.CoreGroundOriginOffsetMillimeters);
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

    private static void WriteNullableInt(BinaryWriter writer, int? value)
    {
        writer.Write(value.HasValue);
        if (value.HasValue)
        {
            writer.Write(value.Value);
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
        internal int FlagWord { get; set; }
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
            _actors.Add(
                actorId.Value,
                CreateActor(actorId, definition, SeatOnGround(
                    definition.DefinitionName,
                    definition.InitialPose)));
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

    /// <summary>
    /// Isolated <see cref="Level100ActorSnapshot.IsObjective"/> names
    /// the rebuild bool. This is the
    /// <c>or/and [esi+0x2c], 0x20</c> word actor-script
    /// SetObjective / UnsetObjective write. Noticeboard stays
    /// unclaimed.
    /// </summary>
    public int FlagWord(Level100ActorId actorId) => Require(actorId).FlagWord;

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
            Health = ReleasedInitialHealth(definitionName, definition.InitialHealth),
            Pose = SeatOnGround(definitionName, definition.InitialPose),
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

        actor.FlagWord = objective
            ? RetailSetObjective.Mark(actor.FlagWord)
            : RetailSetObjective.Unmark(actor.FlagWord);
        actor.IsObjective = (actor.FlagWord & RetailSetObjective.MarkedBit) != 0;
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
        if (!actor.Trigger.HasValue || actor.TriggerEventDispatched)
        {
            return false;
        }

        actor.TriggerEntryJetModeState = entryJetModeState;
        EnqueueFact(Level100ActorFactKind.TriggerDispatchReady, actor.ActorId, null, 0);
        return true;
    }

    public void MarkTriggerEventDispatched(Level100ActorId actorId)
    {
        Actor actor = Require(actorId);
        if (!actor.Trigger.HasValue || actor.TriggerEventDispatched)
        {
            throw new InvalidOperationException("Trigger dispatch is not ready.");
        }

        actor.TriggerEntered = true;
        actor.TriggerEntryJetModeState ??= Level100MissionJetModeState.NotInJetMode;
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

    /// <summary>
    /// The released <c>CThing::Init</c> support clamp, applied to every actor
    /// rather than to one motion class.
    /// </summary>
    /// <remarks>
    /// <para>
    /// Read from the pristine specimen
    /// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, sha256
    /// <c>74154BFAE14DDC8ECB87A0766F5BC381C7B7F1AB334ED7A753040EDA1E1E7750</c>.
    /// <c>CThing::Init</c> (<c>0x004F34A0</c>) copies the authored position
    /// into <c>this+0x1c..+0x28</c> and then does exactly two things to the
    /// vertical and nothing else:
    /// </para>
    /// <list type="number">
    ///   <item>it samples the one global height field
    ///   (<c>MOV ECX, 0x006FADC8</c> / <c>CALL 0x0047EB80</c>), compares the
    ///   sample against the authored Z-down position
    ///   (<c>FCOM [ESI+0x24]</c>) and writes the sample in when the authored
    ///   value is below the ground (<c>FSTP [ESP+0x14]</c> at
    ///   <c>0x004F3529</c>, then <c>CALL [EAX+0x50]</c>) — guarded by
    ///   <c>vtable[+0xB0]() != 0</c>;</item>
    ///   <item>it loads the water level (<c>FLD [0x006FBDFC]</c> at
    ///   <c>0x004F3549</c>), compares (<c>FCOM [ESI+0x24]</c>) and writes it in
    ///   the same way (<c>FSTP [ESI+0x24]</c>) — guarded by
    ///   <c>vtable[+0xC4]() == 0</c>.</item>
    /// </list>
    /// <para>
    /// The authored value is ABSOLUTE. It is only ever pulled toward a surface
    /// — never offset, never terrain-relative, and there is no per-class
    /// additive term at <c>Init</c>. Z is down-positive in that space, so both
    /// <c>min</c>s are <c>Math.Max</c> here.
    /// </para>
    /// <para>
    /// <b>Why the clamps are unconditional for Level 100.</b> Measured from
    /// vtable slots 44/49 across all 24 concrete classes: 19 take both clamps
    /// unconditionally; <c>CDropship</c>, <c>CSimpleBuilding</c> and
    /// <c>CBoat</c> gate on <c>+0x2C</c> bit 2; <c>CSubmarine</c> takes
    /// neither. That bit is never set anywhere in the <c>play-level100</c>
    /// trace, and Level 100 instantiates no <c>CSubmarine</c>, so every actor
    /// in this level takes both clamps and no runtime flag is modelled. The
    /// <c>CDropship</c> is the check on that: it takes both and NEITHER MOVES
    /// IT — authored equals seated at retail −15.0 for both ambient aircraft —
    /// while a positive control in the same trace shows the terrain clamp
    /// firing on another object (−15.0 -> −18.10016), so the instrument can see
    /// one fire.
    /// </para>
    /// <para>
    /// <b>The one term retail does not have.</b> A <c>GroundVehicle</c> keeps
    /// <c>ground + CoreGroundOriginOffsetMillimeters</c> as its terrain
    /// support, which is the same expression
    /// <see cref="Level100ActorMechanics"/> applies on every base tick once
    /// the actor starts following a waypoint, so it does not jump the moment
    /// it is first commanded to move. That offset is a Core pivot convention,
    /// not a retail placement rule, and it is deliberately NOT applied to the
    /// water support or to any other class — the renderer's own seat at
    /// <c>Level100StaticWorldAsset.Load</c> spells the unoffset
    /// <c>max(authored, terrain, water)</c>, and Core and the renderer must
    /// agree about where an object is.
    /// </para>
    /// <para>
    /// Level 100 authors every Target Tank and Target Truck at retail Z = 0
    /// while the firing-range ground is at Core Y = 600, and every retail-Z-0
    /// static at a Core Y of −10,000; without this clamp all of them are buried
    /// and their contact meshes are unreachable.
    /// </para>
    /// </remarks>
    private Level100ActorPoseSnapshot SeatOnGround(
        string? definitionName,
        Level100ActorPoseSnapshot pose)
    {
        Level100ActorMotionDefinition? motion =
            _definitions.FindMotionDefinition(definitionName);
        int groundOriginOffset =
            motion?.MotionClass == Level100ActorMotionClass.GroundVehicle
                ? motion.CoreGroundOriginOffsetMillimeters!.Value
                : 0;
        int seated = Math.Max(
            checked(
                Level100Terrain.Instance.SampleGroundElevationMillimeters(
                    new SimVector2(
                        pose.PositionMillimeters.X,
                        pose.PositionMillimeters.Z)) +
                groundOriginOffset),
            Level100Terrain.WaterElevationMillimeters);
        return pose.PositionMillimeters.Y >= seated
            ? pose
            : pose with
            {
                PositionMillimeters = new SimVector3(
                    pose.PositionMillimeters.X,
                    seated,
                    pose.PositionMillimeters.Z),
            };
    }

    /// <summary>
    /// Released <c>CUnit::Init</c> takes a unit's life from its <c>Unit</c>
    /// record's <c>CUnitLife</c> field (physics value id 3, record +0xc0), not
    /// from the level file. The materialized spawn manifest carries the same
    /// number for the two ground targets and carries <c>0</c> for the air
    /// units, which nothing ever filled in. Rather than change a manifest whose
    /// SHA-256 is pinned in a tree this work does not own
    /// (rebuild/OnslaughtRebuild.Client/Level100ActorDefinitionManifest.cs:16),
    /// Core takes the released value from the contact catalog - the same
    /// physics record, decoded once - whenever the definition has one. For
    /// Target Tank (6.0), Target Truck (3.0) and Warehouse (50.0) this is
    /// exactly the value already in the manifest, so nothing moves; for
    /// Target Drone (1.0) it replaces a 0 that would otherwise make the actor
    /// spawn with no life to lose.
    /// </summary>
    private static int ReleasedInitialHealth(
        string definitionName,
        int manifestInitialHealth)
    {
        if (!Level100ContactCatalog.Instance.TryGetDefinition(
                definitionName,
                out Level100ContactDefinition? definition) ||
            definition is null ||
            definition.Kind == Level100DefinitionKind.Static)
        {
            return manifestInitialHealth;
        }
        return checked((int)MathF.Round(
            definition.MaximumLife * 1_000f,
            MidpointRounding.AwayFromZero));
    }

    private static Actor CreateActor(
        Level100ActorId actorId,
        Level100ActorDefinition definition,
        Level100ActorPoseSnapshot pose) =>
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
            Pose = pose,
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
                ((actor.TriggerEventDispatched && !actor.TriggerEntered) ||
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
        FlagWord = actor.IsObjective ? RetailSetObjective.MarkedBit : 0,
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
