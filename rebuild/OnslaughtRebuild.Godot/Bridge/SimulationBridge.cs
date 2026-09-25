// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The one Godot boundary to the C# simulation Core, which stays C# under the
/// repository language rule (measured hot path; see VALIDATION.md). GDScript
/// owns real-time input adaptation in Client/interactive_session.gd and calls
/// <see cref="Step"/> once per fixed 20 Hz tick with the exact consumed input.
/// Recording, state hashing and create-new tape persistence stay beside Core.
/// Every method returns an explicit {ok, value?, error_type?, error?} result;
/// nothing throws across the language boundary.
/// </summary>
public sealed partial class SimulationBridge : RefCounted
{
    private Simulation? _simulation;
    private WorldSnapshot? _previous;
    private WorldSnapshot? _current;
    private SimInput? _lastConsumedInput;
    private CommandTapeRecorder? _recorder;
    private int _recordedTicks;
    private uint _seed;
    private readonly List<Level100MissionEvent> _missionEvents = [];
    private readonly List<AquilaFlightEvent> _flightEvents = [];
    private readonly List<Level100DestructionEvent> _destructionEvents = [];
    private readonly List<Level100WeaponFireEvent> _weaponFireEvents = [];

    internal WorldSnapshot PreviousSnapshot => _previous ?? throw new InvalidOperationException("The simulation has not started.");

    internal WorldSnapshot CurrentSnapshot => _current ?? throw new InvalidOperationException("The simulation has not started.");

    /// <summary>
    /// Creates the Level 100 simulation from the verified static-world manifest
    /// bytes. The initial snapshot's events are retained for the first frame.
    /// </summary>
    public D Start(long seed, byte[] manifestBytes) => Guard(() =>
    {
        if (_simulation is not null) throw new InvalidOperationException("The simulation has already started.");
        if (seed is <= 0 or > uint.MaxValue) throw new ArgumentOutOfRangeException(nameof(seed), "Seed must be a nonzero UInt32.");
        ArgumentNullException.ThrowIfNull(manifestBytes);
        Level100ActorDefinitionSet definitions = Level100ActorDefinitionManifest.Decode(manifestBytes);
        _seed = (uint)seed;
        _simulation = new Simulation(_seed, definitions);
        _current = _simulation.Snapshot;
        _previous = _current;
        AppendEvents(_current);
        return default;
    });

    /// <summary>
    /// Advances exactly one simulation tick with the consumed input and returns
    /// the new tick. When recording, the input and resulting snapshot are observed.
    /// </summary>
    public D Step(long moveX, long moveZ, long actions, long lookX, long lookY,
        long lookXAnalogPermille, long lookYAnalogPermille) => Guard(() =>
    {
        Simulation simulation = _simulation ?? throw new InvalidOperationException("The simulation has not started.");
        var input = new SimInput(
            checked((sbyte)moveX), checked((sbyte)moveZ), (SimActions)checked((ushort)actions),
            checked((sbyte)lookX), checked((sbyte)lookY),
            checked((short)lookXAnalogPermille), checked((short)lookYAnalogPermille));
        _previous = _current;
        _current = simulation.Step(input);
        _lastConsumedInput = input;
        _recorder?.Observe(_recordedTicks++, input, _current);
        AppendEvents(_current);
        return _current.Tick;
    });

    public D IsStarted() => Guard(() => _simulation is not null);

    public D GetTick() => Guard(() => CurrentSnapshot.Tick);

    public D GetStateHash() => Guard(() => StateHasher.ComputeHex(CurrentSnapshot));

    /// <summary>The input Core consumed on the most recent step, or null before one.</summary>
    public D GetLastConsumedInput() => Guard(() => _lastConsumedInput is SimInput input
        ? new D
        {
            ["move_x"] = input.MoveX, ["move_z"] = input.MoveZ, ["actions"] = (int)input.Actions,
            ["look_x"] = input.LookX, ["look_y"] = input.LookY,
            ["look_x_analog_permille"] = input.LookXAnalogPermille,
            ["look_y_analog_permille"] = input.LookYAnalogPermille,
        }
        : default(Variant));

    /// <summary>Recording must begin with an empty recorder before the first step.</summary>
    public D EnableRecording() => Guard(() =>
    {
        if (_recorder is not null) throw new InvalidOperationException("This simulation is already recording.");
        if (CurrentSnapshot.Tick != 0) throw new InvalidOperationException("Recording must be enabled before the first simulation tick.");
        _recorder = new CommandTapeRecorder();
        return default;
    });

    public D IsRecording() => Guard(() => _recorder is not null);

    /// <summary>
    /// Writes the observed tape once with create-new, protected-destination
    /// semantics (<see cref="TapeFile.WriteNew(string, CommandTape)"/>); GDScript
    /// file access has no exclusive create. Returns false when no tick was run.
    /// </summary>
    public D PersistRecordedTape(string path) => Guard(() =>
    {
        CommandTapeRecorder recorder = _recorder ?? throw new InvalidOperationException("This simulation is not recording.");
        WorldSnapshot final = CurrentSnapshot;
        if (final.Tick == 0)
        {
            recorder.Dispose();
            _recorder = null;
            return false;
        }
        // A failed write keeps the recorder, so the host's later attempt (at
        // exit) still has the whole session; nothing is dropped silently.
        TapeFile.WriteNew(path, recorder.BuildObserved($"recorded-{final.Tick}", _seed));
        recorder.Dispose();
        _recorder = null;
        return true;
    });

    /// <summary>
    /// Writes a new file with create-new semantics and flushes it to disk; an
    /// existing destination is never overwritten. GDScript file access has no
    /// exclusive create (the smoke report uses this).
    /// </summary>
    public D WriteNewFileDurably(string path, byte[] content) => Guard(() =>
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);
        ArgumentNullException.ThrowIfNull(content);
        using FileStream stream = new(path, System.IO.FileMode.CreateNew, System.IO.FileAccess.Write, System.IO.FileShare.None);
        stream.Write(content);
        stream.Flush(flushToDisk: true);
        return default;
    });

    /// <summary>Discards an unwritten recording, releasing its trace hasher.</summary>
    public D DiscardRecording() => Guard(() =>
    {
        _recorder?.Dispose();
        _recorder = null;
        return default;
    });

    private void AppendEvents(WorldSnapshot snapshot)
    {
        _missionEvents.AddRange(snapshot.Level100MissionEvents);
        _flightEvents.AddRange(snapshot.AquilaFlightEventLog);
        _destructionEvents.AddRange(snapshot.Level100DestructionEvents);
        _weaponFireEvents.AddRange(snapshot.Level100WeaponFireEvents);
    }

    public override void _Notification(int what)
    {
        if (what == NotificationPredelete)
        {
            _recorder?.Dispose();
            _recorder = null;
        }
    }

    private static D Guard(Func<Variant> action)
    {
        try
        {
            return new D { ["ok"] = true, ["value"] = action() };
        }
        catch (Exception error)
        {
            return new D { ["ok"] = false, ["error_type"] = error.GetType().Name, ["error"] = error.Message };
        }
    }
}
