// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public enum Level100DestructionEventKind : byte
{
    PulseImpact = 0,
    SegmentDamaged = 1,
    SegmentDetached = 2,
    ActiveSubtreeBelowHalf = 3,
    Terminal = 4,
}

public enum Level100DestructionEffectKind : byte
{
    None = 0,
    PulseImpact = 1,
    TargetDestroyed = 2,
    FacilityDestroyed = 3,
}

public readonly record struct Level100DestructionEvent(
    Level100DestructionEventKind Kind,
    Level100DestructionEffectKind EffectKind,
    int ActorId,
    int PartIndex,
    uint RemainingHealthBits,
    Level100Vector3 Position);

public sealed class Level100DestructionSnapshot
{
    private readonly uint[] _initialHealthBits;
    private readonly uint[] _currentHealthBits;
    private readonly byte[] _partActivity;

    internal Level100DestructionSnapshot(
        int actorId,
        string definitionName,
        uint currentLifeBits,
        bool terminal,
        bool belowHalfReported,
        uint[] initialHealthBits,
        uint[] currentHealthBits,
        byte[] partActivity)
    {
        ActorId = actorId;
        DefinitionName = definitionName;
        CurrentLifeBits = currentLifeBits;
        Terminal = terminal;
        BelowHalfReported = belowHalfReported;
        _initialHealthBits = initialHealthBits;
        _currentHealthBits = currentHealthBits;
        _partActivity = partActivity;
    }

    public int ActorId { get; }

    public string DefinitionName { get; }

    public uint CurrentLifeBits { get; }

    public bool Terminal { get; }

    public bool BelowHalfReported { get; }

    public ReadOnlyMemory<uint> InitialHealthBits => _initialHealthBits;

    public ReadOnlyMemory<uint> CurrentHealthBits => _currentHealthBits;

    public ReadOnlyMemory<byte> PartActivity => _partActivity;

    internal uint[] CopyInitialHealthBits() => (uint[])_initialHealthBits.Clone();

    internal uint[] CopyCurrentHealthBits() => (uint[])_currentHealthBits.Clone();

    internal byte[] CopyPartActivity() => (byte[])_partActivity.Clone();

}

public sealed record Level100DestructionRuntimeSnapshot(
    IReadOnlyList<Level100DestructionSnapshot> Actors);

/// <summary>
/// Segment/contact mechanics attached to actors owned by the native registry.
/// This owner neither creates actors nor advances mission state: it consumes
/// exact identity, mesh, active state and full mutable pose, then reports the
/// released hit/dying/died facts back through the registry.
/// </summary>
public sealed class Level100DestructionRuntime
{
    private readonly Level100ActorRegistry _registry;
    private readonly SortedDictionary<int, Level100DestructionState> _states = [];
    private readonly List<Level100DestructionEvent> _events = [];
    private Level100ContactActor[] _contactActors = [];
    private readonly Level100DestructionEvent[] _hitEvents =
        new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];

    public Level100DestructionRuntime(Level100ActorRegistry registry)
    {
        _registry = registry ?? throw new ArgumentNullException(nameof(registry));
        SynchronizeActors(requireInitialState: true);
    }

    public Level100DestructionRuntime(
        Level100ActorRegistry registry,
        Level100DestructionRuntimeSnapshot snapshot)
    {
        _registry = registry ?? throw new ArgumentNullException(nameof(registry));
        ArgumentNullException.ThrowIfNull(snapshot);
        ArgumentNullException.ThrowIfNull(snapshot.Actors);
        if (snapshot.Actors.Any(item => item is null) ||
            snapshot.Actors.Select(item => item.ActorId).Distinct().Count() !=
                snapshot.Actors.Count)
        {
            throw new ArgumentException(
                "The destruction runtime snapshot has invalid actor identities.",
                nameof(snapshot));
        }

        SynchronizeActors(
            requireInitialState: false,
            validateExisting: false);
        foreach (Level100DestructionSnapshot actor in snapshot.Actors)
        {
            if (!_states.TryGetValue(actor.ActorId, out Level100DestructionState? state))
            {
                throw new ArgumentException(
                    "The destruction snapshot refers to a non-destructible actor.",
                    nameof(snapshot));
            }
            state.Restore(actor);
        }
        if (_states.Count != snapshot.Actors.Count)
        {
            throw new ArgumentException(
                "The destruction snapshot omits a registered destructible actor.",
                nameof(snapshot));
        }
        ValidateRegistryInvariants();
    }

    public Level100DestructionRuntimeSnapshot Snapshot => new(
        Array.AsReadOnly(_states.Values
            .Select(state => state.CaptureSnapshot())
            .ToArray()));

    public IReadOnlyList<Level100DestructionEvent> Events =>
        Array.AsReadOnly(_events.ToArray());

    internal void RegisterActor(Level100ActorId actorId)
    {
        Level100ActorSnapshot actor = _registry.GetActor(actorId);
        _ = EnsureState(actor);
    }

    internal void BeginTick()
    {
        _events.Clear();
        SynchronizeActors(requireInitialState: false);
    }

    internal void ValidateExternalFacts(
        IReadOnlyList<Level100SimulationFact>? facts)
    {
        if (facts is null)
        {
            return;
        }

        foreach (Level100SimulationFact fact in facts)
        {
            ArgumentNullException.ThrowIfNull(fact);
            switch (fact)
            {
                case Level100ActorHealthFact health:
                    RejectOwnedExternalMutation(health.ActorId);
                    break;
                case Level100ActorStartedDyingFact startedDying:
                    RejectOwnedExternalMutation(startedDying.ActorId);
                    break;
                case Level100ActorDiedFact died:
                    RejectOwnedExternalMutation(died.ActorId);
                    break;
            }
        }
    }

    internal void SetExternalHealth(Level100ActorId actorId, int health)
    {
        RejectOwnedExternalMutation(actorId);
        _registry.SetHealth(actorId, health);
    }

    internal void ReportExternalStartedDying(Level100ActorId actorId)
    {
        RejectOwnedExternalMutation(actorId);
        _registry.ReportStartedDying(actorId);
    }

    internal void ReportExternalDied(Level100ActorId actorId)
    {
        RejectOwnedExternalMutation(actorId);
        _registry.ReportDied(actorId);
    }

    public bool TryApplyPulseSweep(
        SimVector3 start,
        SimVector3 end,
        out Level100ContactHit hit)
    {
        SynchronizeActors(requireInitialState: false);
        Level100ActorRegistrySnapshot registrySnapshot = _registry.Snapshot;
        if (_contactActors.Length < registrySnapshot.Actors.Count)
        {
            Array.Resize(
                ref _contactActors,
                registrySnapshot.Actors.Count);
        }

        int contactActorCount = 0;
        foreach (Level100ActorSnapshot actor in registrySnapshot.Actors)
        {
            if (!actor.Active ||
                actor.Lifecycle == Level100ActorLifecycle.Destroyed ||
                actor.DefinitionName is null ||
                !Level100ContactCatalog.Instance.TryGetDefinition(
                    actor.DefinitionName,
                    out Level100ContactDefinition? definition) ||
                definition is null)
            {
                continue;
            }
            if (!StringComparer.OrdinalIgnoreCase.Equals(
                    actor.MeshBinding,
                    definition.Mesh))
            {
                throw new InvalidDataException(
                    $"Level 100 actor {actor.ActorId.Value} definition/mesh binding changed.");
            }

            ReadOnlyMemory<byte> partActivity =
                _states.TryGetValue(
                    actor.ActorId.Value,
                    out Level100DestructionState? state)
                    ? state.ContactPartActivity
                    : default;
            _contactActors[contactActorCount++] = new Level100ContactActor(
                actor.ActorId.Value,
                active: true,
                ToContactTransform(actor.Pose),
                ToContactVector(actor.Pose.LinearVelocityMillimetersPerTick),
                definition,
                partActivity: partActivity);
        }

        if (!Level100ContactMechanics.TrySweepPulseWithTerrain(
                ToContactVector(start),
                ToContactVector(end),
                _contactActors.AsSpan(0, contactActorCount),
                out hit))
        {
            return false;
        }
        if (hit.ActorId == 0 ||
            !_states.TryGetValue(
                hit.ActorId,
                out Level100DestructionState? destruction))
        {
            _events.Add(Level100DestructionState.CreatePulseImpactEvent(hit));
            return true;
        }

        int eventCount = destruction.ApplyPulseHit(
            hit,
            _hitEvents);
        for (int index = 0; index < eventCount; index++)
        {
            _events.Add(_hitEvents[index]);
        }

        Level100ActorId actorId = new(hit.ActorId);
        _registry.ReportHit(
            actorId,
            otherThingTypeMask: Level100ReleasedThingTypeMasks.Ammunition);
        _registry.SetHealth(actorId, destruction.RegistryHealth);
        if (destruction.Terminal)
        {
            _registry.ReportStartedDying(actorId);
            _registry.ReportDied(actorId);
        }
        ValidateRegistryInvariant(
            _registry.GetActor(actorId),
            destruction);
        return true;
    }

    private void RejectOwnedExternalMutation(Level100ActorId actorId)
    {
        if (_states.ContainsKey(actorId.Value))
        {
            throw new InvalidOperationException(
                $"Level 100 actor {actorId.Value} health and destruction lifecycle " +
                "are owned by segmented destruction contact.");
        }
    }

    private void SynchronizeActors(
        bool requireInitialState,
        bool validateExisting = true)
    {
        foreach (Level100ActorSnapshot actor in _registry.Snapshot.Actors
            .OrderBy(item => item.ActorId.Value))
        {
            Level100DestructionState? state = EnsureState(
                actor,
                requireInitialState);
            if (state is not null &&
                !requireInitialState &&
                validateExisting)
            {
                ValidateRegistryInvariant(actor, state);
            }
        }
    }

    private Level100DestructionState? EnsureState(
        Level100ActorSnapshot actor,
        bool requireInitialState = true)
    {
        if (actor.DefinitionName is null ||
            !Level100ContactCatalog.Instance.TryGetDefinition(
                actor.DefinitionName,
                out Level100ContactDefinition? definition) ||
            definition is null ||
            definition.Kind is not (
                Level100DefinitionKind.TargetTank or
                Level100DefinitionKind.Warehouse))
        {
            return null;
        }
        if (!StringComparer.OrdinalIgnoreCase.Equals(
                actor.MeshBinding,
                definition.Mesh))
        {
            throw new InvalidDataException(
                $"Level 100 actor {actor.ActorId.Value} definition/mesh binding changed.");
        }

        if (_states.TryGetValue(
                actor.ActorId.Value,
                out Level100DestructionState? existing))
        {
            if (!ReferenceEquals(existing.Definition, definition))
            {
                throw new InvalidDataException(
                    "A Level 100 actor changed destruction definition.");
            }
            return existing;
        }

        int expectedHealth = checked((int)MathF.Round(
            definition.MaximumLife * 1_000f,
            MidpointRounding.AwayFromZero));
        if (requireInitialState &&
            (actor.Health != expectedHealth ||
             actor.Lifecycle != Level100ActorLifecycle.Alive))
        {
            throw new InvalidDataException(
                $"Level 100 actor {actor.ActorId.Value} is not in the released " +
                $"{definition.Name} initial state.");
        }
        var state = new Level100DestructionState(actor.ActorId.Value, definition);
        _states.Add(actor.ActorId.Value, state);
        return state;
    }

    private void ValidateRegistryInvariants()
    {
        foreach (Level100DestructionState state in _states.Values)
        {
            ValidateRegistryInvariant(
                _registry.GetActor(new Level100ActorId(state.ActorId)),
                state);
        }
    }

    private static void ValidateRegistryInvariant(
        Level100ActorSnapshot actor,
        Level100DestructionState destruction)
    {
        Level100ActorLifecycle expectedLifecycle = destruction.Terminal
            ? Level100ActorLifecycle.Destroyed
            : Level100ActorLifecycle.Alive;
        if (actor.Health != destruction.RegistryHealth ||
            actor.Lifecycle != expectedLifecycle ||
            (destruction.Terminal && actor.Active))
        {
            throw new InvalidDataException(
                $"Level 100 actor {actor.ActorId.Value} registry and segmented " +
                "destruction state disagree.");
        }
    }

    private static Level100Transform3 ToContactTransform(
        Level100ActorPoseSnapshot pose) =>
        new(ToContactVector(pose.PositionMillimeters), ToContactBasis(pose.BasisFloatBits));

    private static Level100Vector3 ToContactVector(SimVector3 vector) =>
        new(vector.X, vector.Z, checked(-vector.Y));

    private static Level100Basis3 ToContactBasis(Level100FloatBasis3Bits core)
    {
        static int Component(int bits)
        {
            float value = BitConverter.Int32BitsToSingle(bits);
            if (!float.IsFinite(value))
            {
                throw new InvalidDataException(
                    "A Level 100 actor basis contains a non-finite component.");
            }
            return checked((int)MathF.Round(
                value * Level100Basis3.Scale,
                MidpointRounding.AwayFromZero));
        }

        // Core is (retail X, up=-retail Z, retail Y). Contact meshes remain
        // (X,Y,Z-down), so transform the full basis rather than transferring
        // yaw-only source enums or dropping pitch/roll.
        var result = new Level100Basis3(
            Component(core.Row0X),
            Component(core.Row0Z),
            -Component(core.Row0Y),
            Component(core.Row2X),
            Component(core.Row2Z),
            -Component(core.Row2Y),
            -Component(core.Row1X),
            -Component(core.Row1Z),
            Component(core.Row1Y));
        return result.IsOrthonormal
            ? result
            : throw new InvalidDataException(
                "A Level 100 actor basis cannot be represented by contact mechanics.");
    }
}

/// <summary>
/// Per-actor destruction component. The mission/native registry creates and
/// attaches this state; it does not register, spawn, position, deactivate or
/// advance mission objectives itself.
/// </summary>
public sealed class Level100DestructionState
{
    public const uint PulseDamageBits = 0x3FE66666;
    public const int MaximumEventsPerHit = 8;

    private const uint WarehouseTerminalFractionBits = 0x3E99999A;
    private const uint WarehouseHalfFractionBits = 0x3F000000;
    private const uint WarehouseCoreMultiplierBits = 0x40A00000;

    private readonly Level100ContactDefinition _definition;
    private uint[] _initialHealthBits;
    private uint[] _currentHealthBits;
    private byte[] _partActivity;
    private uint _currentLifeBits;
    private bool _terminal;
    private bool _belowHalfReported;

    public Level100DestructionState(
        int actorId,
        Level100ContactDefinition definition)
    {
        ArgumentNullException.ThrowIfNull(definition);
        if (actorId <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(actorId));
        }
        if (definition.Kind is not (
            Level100DefinitionKind.TargetTank or
            Level100DefinitionKind.Warehouse))
        {
            throw new ArgumentException(
                "Only released Level 100 destructible definitions have state.",
                nameof(definition));
        }

        ActorId = actorId;
        _definition = definition;
        _initialHealthBits = new uint[definition.PartCount];
        _currentHealthBits = new uint[definition.PartCount];
        _partActivity = new byte[definition.PartCount];
        Reset();
    }

    public int ActorId { get; }

    public Level100ContactDefinition Definition => _definition;

    public bool Terminal => _terminal;

    public uint CurrentLifeBits => _currentLifeBits;

    public float CurrentLife => FromBits(_currentLifeBits);

    /// <summary>
    /// Canonical registry projection. Target Tanks expose their root life;
    /// Warehouse health is the normalized sum of current segment health.
    /// Terminal state always projects to zero.
    /// </summary>
    public int RegistryHealth
    {
        get
        {
            if (_terminal)
            {
                return 0;
            }

            int maximum = checked((int)MathF.Round(
                _definition.MaximumLife * 1_000f,
                MidpointRounding.AwayFromZero));
            if (_definition.Kind == Level100DefinitionKind.TargetTank)
            {
                return Math.Clamp(
                    checked((int)MathF.Round(
                        MathF.Max(0, CurrentLife) * 1_000f,
                        MidpointRounding.AwayFromZero)),
                    1,
                    maximum);
            }

            float initial = SumInitialHealth(0);
            float current = SumCurrentHealth(0);
            if (!float.IsFinite(initial) ||
                !float.IsFinite(current) ||
                initial <= 0 ||
                current < 0)
            {
                throw new InvalidDataException(
                    "Warehouse segment health cannot be projected to the actor registry.");
            }
            return Math.Clamp(
                checked((int)MathF.Round(
                    maximum * (current / initial),
                    MidpointRounding.AwayFromZero)),
                1,
                maximum);
        }
    }

    public ReadOnlyMemory<byte> ContactPartActivity => _partActivity;

    public uint GetInitialSegmentHealthBits(int partIndex)
    {
        ValidatePartIndex(partIndex);
        return _initialHealthBits[partIndex];
    }

    public uint GetCurrentSegmentHealthBits(int partIndex)
    {
        ValidatePartIndex(partIndex);
        return _currentHealthBits[partIndex];
    }

    public void Reset()
    {
        Array.Clear(_initialHealthBits);
        Array.Clear(_currentHealthBits);
        Array.Fill(_partActivity, (byte)1);
        _terminal = false;
        _belowHalfReported = false;
        _currentLifeBits = _definition.MaximumLifeBits;

        if (_definition.Kind == Level100DefinitionKind.Warehouse)
        {
            InitializeWarehouseHealth();
        }
    }

    /// <summary>
    /// Applies the proven medium-pulse damage to a factual narrowphase hit.
    /// The caller retains actor activation and mission consequence ownership.
    /// </summary>
    public int ApplyPulseHit(
        in Level100ContactHit hit,
        Span<Level100DestructionEvent> events)
    {
        if (hit.ActorId != ActorId)
        {
            throw new ArgumentException(
                "The hit actor does not own this destruction component.",
                nameof(hit));
        }
        if ((uint)hit.PartIndex >= (uint)_definition.PartCount)
        {
            throw new ArgumentOutOfRangeException(
                nameof(hit),
                "The factual hit must identify a decoded actor part.");
        }
        if (events.Length < MaximumEventsPerHit)
        {
            throw new ArgumentException(
                $"At least {MaximumEventsPerHit} event slots are required.",
                nameof(events));
        }

        var writer = new EventWriter(events);
        writer.Add(CreatePulseImpactEvent(hit));

        if (_terminal)
        {
            return writer.Count;
        }

        if (_definition.Kind == Level100DefinitionKind.TargetTank)
        {
            ApplyTargetTankDamage(hit, ref writer);
        }
        else
        {
            ApplyWarehouseDamage(hit, ref writer);
        }
        return writer.Count;
    }

    internal static Level100DestructionEvent CreatePulseImpactEvent(
        in Level100ContactHit hit)
        => new(
            Level100DestructionEventKind.PulseImpact,
            Level100DestructionEffectKind.PulseImpact,
            hit.ActorId,
            hit.PartIndex,
            0,
            hit.SurfacePoint);

    public Level100DestructionSnapshot CaptureSnapshot()
    {
        return new Level100DestructionSnapshot(
            ActorId,
            _definition.Name,
            _currentLifeBits,
            _terminal,
            _belowHalfReported,
            (uint[])_initialHealthBits.Clone(),
            (uint[])_currentHealthBits.Clone(),
            (byte[])_partActivity.Clone());
    }

    public void Restore(Level100DestructionSnapshot snapshot)
    {
        ArgumentNullException.ThrowIfNull(snapshot);
        if (snapshot.ActorId != ActorId ||
            !StringComparer.Ordinal.Equals(
                snapshot.DefinitionName,
                _definition.Name) ||
            snapshot.InitialHealthBits.Length != _definition.PartCount ||
            snapshot.CurrentHealthBits.Length != _definition.PartCount ||
            snapshot.PartActivity.Length != _definition.PartCount)
        {
            throw new ArgumentException(
                "The destruction snapshot does not belong to this component.",
                nameof(snapshot));
        }

        uint[] initial = snapshot.CopyInitialHealthBits();
        uint[] current = snapshot.CopyCurrentHealthBits();
        byte[] activity = snapshot.CopyPartActivity();
        float currentLife = FromBits(snapshot.CurrentLifeBits);
        if (!float.IsFinite(currentLife) ||
            (_definition.Kind == Level100DefinitionKind.Warehouse &&
             currentLife < 0))
        {
            throw new ArgumentException(
                "The destruction snapshot has invalid actor health.",
                nameof(snapshot));
        }
        for (int index = 0; index < activity.Length; index++)
        {
            if (activity[index] is not 0 and not 1 ||
                !float.IsFinite(FromBits(initial[index])) ||
                !float.IsFinite(FromBits(current[index])) ||
                FromBits(initial[index]) < 0 ||
                FromBits(current[index]) < 0)
            {
                throw new ArgumentException(
                    "The destruction snapshot has invalid segment state.",
                    nameof(snapshot));
            }
        }
        _initialHealthBits = initial;
        _currentHealthBits = current;
        _partActivity = activity;
        _currentLifeBits = snapshot.CurrentLifeBits;
        _terminal = snapshot.Terminal;
        _belowHalfReported = snapshot.BelowHalfReported;
    }

    private void ApplyTargetTankDamage(
        in Level100ContactHit hit,
        ref EventWriter writer)
    {
        // CUnit retains the demonstrated overkill value through its terminal
        // transition (6 -> 4.2 -> 2.4 -> 0.6 -> -1.2).
        float remaining = FromBits(_currentLifeBits) - FromBits(PulseDamageBits);
        _currentLifeBits = ToBits(remaining);
        writer.Add(new Level100DestructionEvent(
            Level100DestructionEventKind.SegmentDamaged,
            Level100DestructionEffectKind.None,
            ActorId,
            hit.PartIndex,
            _currentLifeBits,
            hit.SurfacePoint));
        if (remaining <= 0)
        {
            SetTerminal(hit, ref writer);
        }
    }

    private void ApplyWarehouseDamage(
        in Level100ContactHit hit,
        ref EventWriter writer)
    {
        if ((uint)hit.PartIndex >= (uint)_definition.PartCount ||
            _partActivity[hit.PartIndex] == 0 ||
            _currentHealthBits[hit.PartIndex] == 0)
        {
            return;
        }

        float remaining = MathF.Max(
            0,
            FromBits(_currentHealthBits[hit.PartIndex]) -
                FromBits(PulseDamageBits));
        _currentHealthBits[hit.PartIndex] = ToBits(remaining);
        writer.Add(new Level100DestructionEvent(
            Level100DestructionEventKind.SegmentDamaged,
            Level100DestructionEffectKind.None,
            ActorId,
            hit.PartIndex,
            _currentHealthBits[hit.PartIndex],
            hit.SurfacePoint));
        if (remaining <= 0)
        {
            _partActivity[hit.PartIndex] = 0;
            writer.Add(new Level100DestructionEvent(
                Level100DestructionEventKind.SegmentDetached,
                Level100DestructionEffectKind.None,
                ActorId,
                hit.PartIndex,
                0,
                hit.SurfacePoint));
        }

        float activeInitial = SumActiveInitialHealth(0);
        float totalInitial = SumInitialHealth(0);
        float halfThreshold = totalInitial * FromBits(WarehouseHalfFractionBits);
        if (!_belowHalfReported && activeInitial < halfThreshold)
        {
            _belowHalfReported = true;
            writer.Add(new Level100DestructionEvent(
                Level100DestructionEventKind.ActiveSubtreeBelowHalf,
                Level100DestructionEffectKind.None,
                ActorId,
                hit.PartIndex,
                ToBits(activeInitial),
                hit.SurfacePoint));
        }

        float terminalThreshold = totalInitial *
            FromBits(WarehouseTerminalFractionBits);
        if (CoreChildrenDestroyed() || activeInitial < terminalThreshold)
        {
            SetTerminal(hit, ref writer);
        }
    }

    private void SetTerminal(
        in Level100ContactHit hit,
        ref EventWriter writer)
    {
        if (_terminal)
        {
            return;
        }
        _terminal = true;
        writer.Add(new Level100DestructionEvent(
            Level100DestructionEventKind.Terminal,
            _definition.Kind == Level100DefinitionKind.TargetTank
                ? Level100DestructionEffectKind.TargetDestroyed
                : Level100DestructionEffectKind.FacilityDestroyed,
            ActorId,
            hit.PartIndex,
            0,
            hit.SurfacePoint));
    }

    private void InitializeWarehouseHealth()
    {
        Level100ContactPart[] parts = _definition.PartArray;
        float divisor = 0;
        for (int index = 1; index < parts.Length; index++)
        {
            divisor += parts[index].SegmentValue;
        }
        if (!float.IsFinite(divisor) || divisor <= 0)
        {
            throw new InvalidDataException(
                "Warehouse segment extent divisor is invalid.");
        }

        float scale = _definition.MaximumLife;
        float coreMultiplier = FromBits(WarehouseCoreMultiplierBits);
        for (int index = 1; index < parts.Length; index++)
        {
            float health = (parts[index].SegmentValue / divisor) * scale;
            if (parts[index].Name.StartsWith("core", StringComparison.OrdinalIgnoreCase))
            {
                health *= coreMultiplier;
            }
            uint bits = ToBits(health);
            _initialHealthBits[index] = bits;
            _currentHealthBits[index] = bits;
        }

        // The first core segment is the zero-health hierarchy root in Steam.
        _initialHealthBits[0] = 0;
        _currentHealthBits[0] = 0;
    }

    private float SumInitialHealth(int parent)
    {
        float sum = _initialHealthBits[parent] == 0
            ? 0
            : FromBits(_initialHealthBits[parent]);
        Level100ContactPart[] parts = _definition.PartArray;
        for (int index = 0; index < parts.Length; index++)
        {
            if (parts[index].Parent == parent)
            {
                sum += SumInitialHealth(index);
            }
        }
        return sum;
    }

    private float SumCurrentHealth(int parent)
    {
        float sum = _currentHealthBits[parent] == 0
            ? 0
            : FromBits(_currentHealthBits[parent]);
        Level100ContactPart[] parts = _definition.PartArray;
        for (int index = 0; index < parts.Length; index++)
        {
            if (parts[index].Parent == parent)
            {
                sum += SumCurrentHealth(index);
            }
        }
        return sum;
    }

    private float SumActiveInitialHealth(int parent)
    {
        float sum = _partActivity[parent] != 0 &&
            _currentHealthBits[parent] != 0
            ? FromBits(_initialHealthBits[parent])
            : 0;
        Level100ContactPart[] parts = _definition.PartArray;
        for (int index = 0; index < parts.Length; index++)
        {
            if (parts[index].Parent == parent)
            {
                sum += SumActiveInitialHealth(index);
            }
        }
        return sum;
    }

    private bool CoreChildrenDestroyed()
    {
        bool hasChild = false;
        Level100ContactPart[] parts = _definition.PartArray;
        for (int index = 0; index < parts.Length; index++)
        {
            if (parts[index].Parent != 0)
            {
                continue;
            }
            hasChild = true;
            if (_partActivity[index] != 0 && _currentHealthBits[index] != 0)
            {
                return false;
            }
        }
        return hasChild;
    }

    private void ValidatePartIndex(int partIndex)
    {
        if ((uint)partIndex >= (uint)_definition.PartCount)
        {
            throw new ArgumentOutOfRangeException(nameof(partIndex));
        }
    }

    private static float FromBits(uint bits) =>
        BitConverter.Int32BitsToSingle(unchecked((int)bits));

    private static uint ToBits(float value) =>
        unchecked((uint)BitConverter.SingleToInt32Bits(value));

    private ref struct EventWriter
    {
        private readonly Span<Level100DestructionEvent> _events;

        public EventWriter(Span<Level100DestructionEvent> events)
        {
            _events = events;
            Count = 0;
        }

        public int Count { get; private set; }

        public void Add(Level100DestructionEvent item)
        {
            if ((uint)Count >= (uint)_events.Length)
            {
                throw new InvalidOperationException(
                    "The bounded destruction event capacity was exceeded.");
            }
            _events[Count++] = item;
        }
    }

}
