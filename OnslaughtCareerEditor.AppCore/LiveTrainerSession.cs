using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>Why an attach was refused. <see cref="None"/> is the only value that allows one.</summary>
    public enum LiveTrainerAttachRefusal
    {
        None,
        NoProcessGiven,
        InstalledGameDirectory,
        NotAManagedProcess,
        NotRunning,
        ProcessIdentityChanged,
        CouldNotOpen,
    }

    public sealed record LiveTrainerAttachDecision(
        bool Allowed,
        LiveTrainerAttachRefusal Refusal,
        string Message);

    /// <summary>
    /// The gate that decides whether the app is allowed to open a process's memory at all.
    ///
    /// The rule is narrow on purpose: only a copy this app launched and is still tracking, proved
    /// to be the same process it registered. A process id alone is never enough, because Windows
    /// recycles them - the same reason the stop path and the liveness poll both compare start time
    /// and main module path. This gate calls
    /// <see cref="GameProfileRuntimeService.MatchesManagedProcessIdentity"/>, the same method those
    /// two use, so the three cannot drift apart.
    ///
    /// The installed game is refused by name and first, before the registry is even consulted, so
    /// the reason a player sees is the real one rather than "not registered".
    /// </summary>
    public static class LiveTrainerAttachPolicy
    {
        public static LiveTrainerAttachDecision Decide(
            GameProfileManagedProcess? candidate,
            GameProfileManagedProcessRegistry registry,
            IGameProfileProcessLivenessProbe? probe = null)
        {
            ArgumentNullException.ThrowIfNull(registry);

            if (candidate is null || candidate.ProcessId <= 0 || string.IsNullOrWhiteSpace(candidate.ExecutablePath))
            {
                return new LiveTrainerAttachDecision(
                    false,
                    LiveTrainerAttachRefusal.NoProcessGiven,
                    "No game process was given.");
            }

            if (LooksLikeAnInstalledGameDirectory(candidate.ExecutablePath))
            {
                return new LiveTrainerAttachDecision(
                    false,
                    LiveTrainerAttachRefusal.InstalledGameDirectory,
                    "That BEA.exe is your installed game. The trainer only ever attaches to a copy this app "
                        + "launched, so your installation is never opened, read, or written.");
            }

            GameProfileRegisteredProcess? registered = registry.Snapshot()
                .FirstOrDefault(row => IsSameRecord(row.Process, candidate));

            if (registered is null)
            {
                return new LiveTrainerAttachDecision(
                    false,
                    LiveTrainerAttachRefusal.NotAManagedProcess,
                    "That process was not launched by this app, so the trainer will not attach to it.");
            }

            GameProfileProcessLivenessProbeResult probed =
                (probe ?? DefaultGameProfileProcessLivenessProbe.Instance).Probe(registered.Process);

            if (!probed.IsRunning || probed.StartedAt is null)
            {
                return new LiveTrainerAttachDecision(
                    false,
                    LiveTrainerAttachRefusal.NotRunning,
                    "That copied game is not running any more.");
            }

            if (!GameProfileRuntimeService.MatchesManagedProcessIdentity(
                    probed.StartedAt.Value,
                    probed.MainModulePath,
                    registered.Process))
            {
                return new LiveTrainerAttachDecision(
                    false,
                    LiveTrainerAttachRefusal.ProcessIdentityChanged,
                    "The process with that id is not the copied game this app started - Windows has reused the "
                        + "id. Nothing was opened.");
            }

            return new LiveTrainerAttachDecision(true, LiveTrainerAttachRefusal.None, "Attached to the copy this app launched.");
        }

        /// <summary>
        /// Whether a path looks like a real Battle Engine Aquila installation rather than an
        /// app-owned copy. Uses the same shapes <see cref="BinaryPatchEngine"/> recognises, so the
        /// trainer and the patch engine agree about what "the installed game" means.
        ///
        /// They no longer agree about what to DO with one, and that is deliberate. Since
        /// <see cref="BinaryPatchEngine.AuthorizeInstalledGameWrite"/> the patch engine will write
        /// to an installed game once a verified original is sitting beside it, because a byte
        /// change to a file on disk has something to put back. The trainer has no equivalent: it
        /// writes into the memory of a live process, there is nothing to snapshot and nothing to
        /// restore, and the refusal below is not a placeholder waiting for the same treatment.
        /// </summary>
        public static bool LooksLikeAnInstalledGameDirectory(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
                return false;

            string fullPath;
            try
            {
                fullPath = Path.GetFullPath(path);
            }
            catch (Exception ex) when (ex is ArgumentException or NotSupportedException or PathTooLongException or IOException)
            {
                // A path the app cannot even normalize is not a path it is going to open.
                return true;
            }

            string[] parts = fullPath.Split(
                new[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar },
                StringSplitOptions.RemoveEmptyEntries);

            for (int i = 0; i <= parts.Length - 3; i++)
            {
                if (string.Equals(parts[i], "steamapps", StringComparison.OrdinalIgnoreCase) &&
                    string.Equals(parts[i + 1], "common", StringComparison.OrdinalIgnoreCase) &&
                    string.Equals(parts[i + 2], "Battle Engine Aquila", StringComparison.OrdinalIgnoreCase))
                {
                    return true;
                }
            }

            foreach (Environment.SpecialFolder folder in new[]
                     {
                         Environment.SpecialFolder.ProgramFiles,
                         Environment.SpecialFolder.ProgramFilesX86,
                         Environment.SpecialFolder.Windows,
                     })
            {
                string root = Environment.GetFolderPath(folder);
                if (string.IsNullOrWhiteSpace(root))
                    continue;

                string normalizedRoot = Path.GetFullPath(root)
                    .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
                if (fullPath.StartsWith(normalizedRoot, StringComparison.OrdinalIgnoreCase))
                    return true;
            }

            return false;
        }

        private static bool IsSameRecord(GameProfileManagedProcess left, GameProfileManagedProcess right)
        {
            if (left.ProcessId != right.ProcessId)
                return false;

            if (left.StartedAt.ToUniversalTime().Ticks != right.StartedAt.ToUniversalTime().Ticks)
                return false;

            try
            {
                return string.Equals(
                    Path.GetFullPath(left.ExecutablePath),
                    Path.GetFullPath(right.ExecutablePath),
                    StringComparison.OrdinalIgnoreCase);
            }
            catch (Exception ex) when (ex is ArgumentException or NotSupportedException or IOException)
            {
                return false;
            }
        }
    }

    /// <summary>How far a read got.</summary>
    public enum LiveTrainerReadStatus
    {
        /// <summary>No session, or it has been disposed.</summary>
        NotAttached,

        /// <summary>The player table itself could not be read: the process has gone or closed.</summary>
        ProcessGone,

        /// <summary>Slot 0 is null. This is what the frontend and the menus look like.</summary>
        NoMissionRunning,

        /// <summary>
        /// A player exists but has no battle engine hanging off it yet, which is what the moment
        /// between loading a mission and being in a vehicle looks like.
        /// </summary>
        NoBattleEngine,

        /// <summary>One of the two pointers held something that cannot be a heap object.</summary>
        PointerImplausible,

        /// <summary>A pointer looked fine but the object behind it could not be read.</summary>
        PlayerUnreadable,

        /// <summary>Values were read. Whether they are believable is a separate question.</summary>
        Read,
    }

    public sealed record LiveTrainerReadResult(
        LiveTrainerReadStatus Status,
        LivePlayerVitals? Vitals,
        string Message)
    {
        public bool HasVitals => Status == LiveTrainerReadStatus.Read && Vitals is not null;

        /// <summary>
        /// The gate on the whole write half of the feature. Values have to have been read, and at
        /// least one of them has to look like a number rather than a bit pattern, before any
        /// control that writes is allowed to be live.
        /// </summary>
        public bool WritingCanBeOffered => HasVitals && Vitals!.AnyVitalLooksPlausible;
    }

    public sealed record LiveTrainerWriteOutcome(
        bool Success,
        string Message,
        LiveTrainerVital Vital,
        float Requested,
        LiveTrainerFieldReading? Before = null,
        LiveTrainerFieldReading? After = null);

    /// <summary>
    /// What a hold loop needs from a session. It exists so the loop can be driven against a fake
    /// in a test without a process, a timer, or a game.
    /// </summary>
    public interface ILiveTrainerVitalsTarget
    {
        LiveTrainerReadResult Read();

        LiveTrainerWriteOutcome Write(LiveTrainerVital vital, float value);

        void ReleaseWriteAccess();
    }

    public sealed record LiveTrainerAttachOutcome(
        bool Success,
        LiveTrainerSession? Session,
        LiveTrainerAttachDecision Decision)
    {
        public string Message => Decision.Message;
    }

    /// <summary>
    /// An open, read-only view of one app-launched copy's memory, plus the guarded route to
    /// writing.
    ///
    /// Three properties matter more than anything else here:
    ///
    /// 1. It can only exist for a process that passed <see cref="LiveTrainerAttachPolicy"/>.
    /// 2. It opens with read access only. A write handle is not requested until a write is
    ///    actually asked for, and <see cref="ReleaseWriteAccess"/> gives it back.
    /// 3. <see cref="Write"/> re-reads the exact address first and refuses unless that fresh read
    ///    is believable. The app never writes an address it has not just successfully read.
    /// </summary>
    public sealed class LiveTrainerSession : ILiveTrainerVitalsTarget, IDisposable
    {
        private readonly IProcessMemoryAccessorFactory _factory;
        private readonly IProcessMemoryAccessor _reader;
        private IProcessMemoryAccessor? _writer;
        private bool _disposed;

        private LiveTrainerSession(
            GameProfileManagedProcess process,
            IProcessMemoryAccessorFactory factory,
            IProcessMemoryAccessor reader)
        {
            Process = process;
            _factory = factory;
            _reader = reader;
        }

        public GameProfileManagedProcess Process { get; }

        public bool HasWriteAccess => _writer is not null;

        public static LiveTrainerAttachOutcome Attach(
            GameProfileManagedProcess? candidate,
            GameProfileManagedProcessRegistry registry,
            IProcessMemoryAccessorFactory? accessorFactory = null,
            IGameProfileProcessLivenessProbe? probe = null)
        {
            LiveTrainerAttachDecision decision = LiveTrainerAttachPolicy.Decide(candidate, registry, probe);
            if (!decision.Allowed || candidate is null)
                return new LiveTrainerAttachOutcome(false, null, decision);

            IProcessMemoryAccessorFactory factory = accessorFactory ?? Win32ProcessMemoryAccessorFactory.Instance;
            if (!factory.TryOpen(candidate.ProcessId, ProcessMemoryAccess.Read, out IProcessMemoryAccessor? reader, out string failure) ||
                reader is null)
            {
                return new LiveTrainerAttachOutcome(
                    false,
                    null,
                    new LiveTrainerAttachDecision(false, LiveTrainerAttachRefusal.CouldNotOpen, failure));
            }

            return new LiveTrainerAttachOutcome(true, new LiveTrainerSession(candidate, factory, reader), decision);
        }

        /// <summary>
        /// Follows the whole chain: player table slot 0, then that player's battle engine at
        /// +0x1c, then the fields on it. Read-only, and safe to call on a timer - every failure
        /// mode is a returned status rather than an exception.
        ///
        /// Both hops are checked. Skipping the second one and reading the vitals off the player
        /// directly would produce numbers that are wrong rather than absent, which is the one
        /// failure this design is built to avoid.
        /// </summary>
        public LiveTrainerReadResult Read()
        {
            if (_disposed)
                return new LiveTrainerReadResult(LiveTrainerReadStatus.NotAttached, null, "Not attached to a game.");

            Span<byte> table = stackalloc byte[LiveTrainerAddresses.PlayerTableByteCount];
            if (!_reader.TryRead(LiveTrainerAddresses.PlayerTable, table))
            {
                return new LiveTrainerReadResult(
                    LiveTrainerReadStatus.ProcessGone,
                    null,
                    "The copied game is no longer readable. It has probably closed.");
            }

            // Which slot holds player one is not settled. IScript::GetPlayerBattleEngine indexes
            // this table from a getter and the literal on the path that reaches the table load is
            // 1, not 0, with a dec eax before it that suggests a 1-based index being converted
            // (local-lab/PLAYER-CHAIN-STATIC-CONFIRMATION-2026-08-01.md). Rather than guess, take
            // the first slot that actually holds something: an empty slot is the documented state
            // the game itself null-checks for, so scanning costs nothing and being wrong by one
            // index would otherwise make this look broken while it sat next to the answer.
            // Only EMPTY slots are skipped. A slot holding something unusable is reported rather
            // than scanned past: "that is not a player" and "there is no player" are different
            // answers, and collapsing them would hide exactly the case where these addresses have
            // gone stale.
            uint playerPointer = 0;
            for (int slot = 0; slot < LiveTrainerAddresses.PlayerSlotCount; slot++)
            {
                uint candidate = LivePlayerVitalsDecoder.ReadSlotPointer(table, slot);
                if (candidate != 0)
                {
                    playerPointer = candidate;
                    break;
                }
            }

            if (playerPointer == 0)
            {
                return new LiveTrainerReadResult(
                    LiveTrainerReadStatus.NoMissionRunning,
                    null,
                    "No mission is running. Start one in the copied game and the numbers appear here.");
            }

            if (!LiveTrainerPlausibility.IsPlausiblePointer(playerPointer))
            {
                return new LiveTrainerReadResult(
                    LiveTrainerReadStatus.PointerImplausible,
                    null,
                    "The player slot held something that cannot be a player, so nothing is being shown.");
            }

            Span<byte> battleEngineSlot = stackalloc byte[4];
            if (!_reader.TryRead(unchecked(playerPointer + LiveTrainerAddresses.BattleEngineOffsetInPlayer), battleEngineSlot))
            {
                return new LiveTrainerReadResult(
                    LiveTrainerReadStatus.PlayerUnreadable,
                    null,
                    "The player was there a moment ago but could not be read. The mission may have just ended.");
            }

            uint battleEnginePointer = System.Buffers.Binary.BinaryPrimitives.ReadUInt32LittleEndian(battleEngineSlot);
            if (battleEnginePointer == 0)
            {
                return new LiveTrainerReadResult(
                    LiveTrainerReadStatus.NoBattleEngine,
                    null,
                    "A mission is loading but you are not in a vehicle yet.");
            }

            if (!LiveTrainerPlausibility.IsPlausiblePointer(battleEnginePointer))
            {
                return new LiveTrainerReadResult(
                    LiveTrainerReadStatus.PointerImplausible,
                    null,
                    "The player's vehicle pointer is not something that can be read, so nothing is being shown.");
            }

            byte[] battleEngine = new byte[LivePlayerVitalsDecoder.RequiredBattleEngineByteCount];
            if (!_reader.TryRead(battleEnginePointer, battleEngine))
            {
                return new LiveTrainerReadResult(
                    LiveTrainerReadStatus.PlayerUnreadable,
                    null,
                    "Your vehicle was there a moment ago but could not be read. The mission may have just ended.");
            }

            return new LiveTrainerReadResult(
                LiveTrainerReadStatus.Read,
                LivePlayerVitalsDecoder.Decode(playerPointer, battleEnginePointer, battleEngine),
                "Reading the running mission.");
        }

        /// <summary>
        /// Sets one vital, after re-reading it. The order is fixed and is the safety argument:
        /// validate the request, read the exact address, refuse unless what came back is
        /// believable, then and only then ask for write access and write four bytes.
        /// </summary>
        public LiveTrainerWriteOutcome Write(LiveTrainerVital vital, float value)
        {
            if (_disposed)
                return new LiveTrainerWriteOutcome(false, "Not attached to a game.", vital, value);

            if (!LiveTrainerPlausibility.IsWritableVital(value, out string refusal))
                return new LiveTrainerWriteOutcome(false, refusal, vital, value);

            LiveTrainerReadResult fresh = Read();
            if (!fresh.HasVitals)
                return new LiveTrainerWriteOutcome(false, fresh.Message, vital, value);

            LiveTrainerFieldReading before = fresh.Vitals!.Field(vital);
            if (!before.LooksLikeAVital)
            {
                return new LiveTrainerWriteOutcome(
                    false,
                    $"The {LiveTrainerAddresses.NameOf(vital)} reading ({before.RawHex}) does not look like a number, "
                        + "so nothing was written.",
                    vital,
                    value,
                    before);
            }

            if (!EnsureWriteAccess(out _))
            {
                return new LiveTrainerWriteOutcome(
                    false,
                    "Could not open that copied game. Nothing was written.",
                    vital,
                    value,
                    before);
            }

            Span<byte> payload = stackalloc byte[4];
            BinaryPrimitives.WriteUInt32LittleEndian(payload, unchecked((uint)BitConverter.SingleToInt32Bits(value)));

            if (!_writer!.TryWrite(before.Address, payload))
            {
                return new LiveTrainerWriteOutcome(
                    false,
                    $"The {LiveTrainerAddresses.NameOf(vital)} write did not go through.",
                    vital,
                    value,
                    before);
            }

            // The read-back is reported, never enforced. The game simulates at 20 Hz and is
            // entitled to have already changed the value again; that is not a failed write.
            LiveTrainerFieldReading? after = null;
            Span<byte> confirm = stackalloc byte[4];
            if (_reader.TryRead(before.Address, confirm))
            {
                after = new LiveTrainerFieldReading(before.Address, BinaryPrimitives.ReadUInt32LittleEndian(confirm));
            }

            return new LiveTrainerWriteOutcome(
                true,
                $"Set {LiveTrainerAddresses.NameOf(vital)} to {value.ToString("0.##", CultureInfo.InvariantCulture)}.",
                vital,
                value,
                before,
                after);
        }

        /// <summary>
        /// Closes the write handle while keeping the reading session open. Called when the last
        /// hold is released, so the app is not sitting on write access to a game it is only
        /// watching.
        /// </summary>
        public void ReleaseWriteAccess()
        {
            _writer?.Dispose();
            _writer = null;
        }

        public void Dispose()
        {
            if (_disposed)
                return;

            _disposed = true;
            ReleaseWriteAccess();
            _reader.Dispose();
        }

        private bool EnsureWriteAccess(out string failure)
        {
            failure = string.Empty;
            if (_writer is not null)
                return true;

            if (!_factory.TryOpen(Process.ProcessId, ProcessMemoryAccess.ReadWrite, out IProcessMemoryAccessor? writer, out failure) ||
                writer is null)
            {
                return false;
            }

            _writer = writer;
            return true;
        }
    }

    public sealed record LiveTrainerHoldTick(
        LiveTrainerReadResult Reading,
        int Attempted,
        int Succeeded,
        bool StoppedItself,
        string Message);

    /// <summary>
    /// Holds vitals at a value by writing them again, on a timer the caller owns.
    ///
    /// A single poke is a no-op here: the game's simulation runs at 20 Hz and rewrites these
    /// fields every tick, so "freeze" can only mean "write it again, often enough". The loop runs
    /// at <see cref="DefaultInterval"/> - 10 Hz, half the simulation rate - because that is the
    /// lowest rate that visibly holds, and because an unsigned .NET app writing into a game process
    /// as fast as it can is exactly the shape antivirus heuristics look for.
    /// <see cref="ClampInterval"/> refuses to go faster than <see cref="FastestInterval"/>.
    ///
    /// The loop stops itself - clearing every hold and handing back write access - the moment the
    /// mission ends, the process goes, or writes stop landing. Nothing here owns a thread or a
    /// timer; <see cref="Tick"/> is called by whoever does.
    /// </summary>
    public sealed class LiveTrainerHold
    {
        /// <summary>10 Hz. Half the game's own 20 Hz simulation rate.</summary>
        public static readonly TimeSpan DefaultInterval = TimeSpan.FromMilliseconds(100);

        /// <summary>2 Hz, used while nothing is held and the page is only watching.</summary>
        public static readonly TimeSpan IdleInterval = TimeSpan.FromMilliseconds(500);

        /// <summary>The floor. Faster than this is a spin loop wearing a timer's clothes.</summary>
        public static readonly TimeSpan FastestInterval = TimeSpan.FromMilliseconds(50);

        public const int ConsecutiveFailuresBeforeStopping = 5;

        private readonly ILiveTrainerVitalsTarget _target;
        private readonly Dictionary<LiveTrainerVital, float> _held = new();
        private int _consecutiveFailures;

        public LiveTrainerHold(ILiveTrainerVitalsTarget target)
        {
            _target = target ?? throw new ArgumentNullException(nameof(target));
        }

        public bool IsHolding => _held.Count > 0;

        public IReadOnlyDictionary<LiveTrainerVital, float> Held => _held;

        public static TimeSpan ClampInterval(TimeSpan requested) =>
            requested < FastestInterval ? FastestInterval : requested;

        public bool TryHold(LiveTrainerVital vital, float value, out string refusal)
        {
            if (!LiveTrainerPlausibility.IsWritableVital(value, out refusal))
                return false;

            _held[vital] = value;
            _consecutiveFailures = 0;
            return true;
        }

        /// <summary>
        /// Hold life, energy, and shields together, or hold none of them.
        /// The Cheats page's "Hold all three" switch uses this so a refused
        /// third value cannot leave two holds running under a switch that said all.
        /// </summary>
        public bool TryHoldAll(float life, float energy, float shields, out string refusal)
        {
            if (!LiveTrainerPlausibility.IsWritableVital(life, out refusal)
                || !LiveTrainerPlausibility.IsWritableVital(energy, out refusal)
                || !LiveTrainerPlausibility.IsWritableVital(shields, out refusal))
            {
                return false;
            }

            _held[LiveTrainerVital.Life] = life;
            _held[LiveTrainerVital.Energy] = energy;
            _held[LiveTrainerVital.Shields] = shields;
            _consecutiveFailures = 0;
            return true;
        }

        public void Release(LiveTrainerVital vital)
        {
            _held.Remove(vital);
            if (_held.Count == 0)
                StopHolding();
        }

        public void ReleaseAll()
        {
            _held.Clear();
            StopHolding();
        }

        /// <summary>
        /// One pass: read, then rewrite whatever is being held. Returns what happened so the
        /// caller can show it without having to ask again.
        /// </summary>
        public LiveTrainerHoldTick Tick()
        {
            LiveTrainerReadResult reading = _target.Read();

            if (!IsHolding)
                return new LiveTrainerHoldTick(reading, 0, 0, false, reading.Message);

            if (!reading.HasVitals)
            {
                ReleaseAll();
                return new LiveTrainerHoldTick(reading, 0, 0, true, $"Holding stopped: {reading.Message}");
            }

            int attempted = 0;
            int succeeded = 0;
            foreach ((LiveTrainerVital vital, float value) in _held.ToArray())
            {
                attempted++;
                if (_target.Write(vital, value).Success)
                    succeeded++;
            }

            if (succeeded == 0)
            {
                _consecutiveFailures++;
                if (_consecutiveFailures >= ConsecutiveFailuresBeforeStopping)
                {
                    ReleaseAll();
                    return new LiveTrainerHoldTick(
                        reading,
                        attempted,
                        0,
                        true,
                        "Holding stopped: the writes stopped landing.");
                }
            }
            else
            {
                _consecutiveFailures = 0;
            }

            return new LiveTrainerHoldTick(reading, attempted, succeeded, false, reading.Message);
        }

        private void StopHolding()
        {
            _consecutiveFailures = 0;
            _target.ReleaseWriteAccess();
        }
    }
}
