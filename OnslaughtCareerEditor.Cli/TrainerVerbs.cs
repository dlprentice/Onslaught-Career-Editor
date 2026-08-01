using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor.Cli
{
    /// <summary>
    /// The live-memory lane: read, and carefully write, the vitals of a running copy of the game.
    ///
    /// It exists because the GUI has this feature and a GUI-only feature cannot be exercised,
    /// regression-tested, or reproduced by anyone who is not sitting at the machine. Every
    /// operation here goes through the same AppCore types the Cheats page calls -
    /// <see cref="LiveTrainerAttachPolicy"/>, <see cref="LiveTrainerSession"/> - so the two cannot
    /// disagree about which process is attachable or when a write is allowed.
    ///
    /// Three refusals are inherited rather than reimplemented, which is the point:
    ///   - only a process this app launched and still has a lease for is attachable;
    ///   - that process must still pass the start-time and module-path identity check, because
    ///     Windows recycles process ids;
    ///   - a write only happens on an address that was just read and came back believable.
    ///
    /// There is no freeze verb. Holding a value means writing it ten times a second for as long as
    /// the user wants it held, which needs a process that stays alive; a one-shot CLI invocation is
    /// the wrong shape for that and pretending otherwise would ship a control that silently does
    /// nothing. <see cref="TrainerSet"/> says so out loud instead.
    /// </summary>
    public static class TrainerVerbs
    {
        private static GameProfileManagedProcessRegistry OpenRegistry()
        {
            Directory.CreateDirectory(SafeCopyVerbs.SafeCopyRoot);
            return new GameProfileManagedProcessRegistry(SafeCopyVerbs.LeasePath);
        }

        /// <summary>
        /// Whether there is anything to attach to, and whether attaching is allowed - without
        /// reading any vitals. This is the verb to call first: it separates "no copy is running"
        /// from "a copy is running but the trainer refuses it".
        /// </summary>
        public static int TrainerStatus(CliContext ctx, int? processId)
        {
            const string command = "trainer.status";
            GameProfileManagedProcessRegistry registry = OpenRegistry();
            registry.PruneDeadLeases();

            if (!TryResolveTarget(ctx, command, registry, processId, out GameProfileManagedProcess target, out int failure))
                return failure;

            LiveTrainerAttachDecision decision = LiveTrainerAttachPolicy.Decide(target, registry);
            object payload = new
            {
                processId = target.ProcessId,
                copyId = Path.GetFileName(Path.TrimEndingDirectorySeparator(target.WorkingDirectory)),
                workingDirectory = target.WorkingDirectory,
                executablePath = target.ExecutablePath,
                startedAt = target.StartedAt,
                attachAllowed = decision.Allowed,
                refusal = decision.Refusal.ToString(),
                message = decision.Message,
                playerTableAddress = "0x" + LiveTrainerAddresses.PlayerTable.ToString("X8", CultureInfo.InvariantCulture),
                battleEngineOffsetInPlayer = "0x" + LiveTrainerAddresses.BattleEngineOffsetInPlayer.ToString("X", CultureInfo.InvariantCulture),
                vitalOffsetsConfirmedAgainstALiveProcess = true,
            };

            if (!decision.Allowed)
                return ctx.Usage(command, decision.Message);

            if (!ctx.Json)
            {
                ctx.Line($"Managed copy: {Path.GetFileName(Path.TrimEndingDirectorySeparator(target.WorkingDirectory))}");
                ctx.Line($"  Pid:     {target.ProcessId}");
                ctx.Line($"  Started: {target.StartedAt:yyyy-MM-dd HH:mm:ss}");
                ctx.Line($"  Attach:  allowed");
                ctx.Line();
                ctx.Line("The life/energy/shields offsets have never been read from a running game.");
            }

            return ctx.Ok(command, payload);
        }

        /// <summary>
        /// Read player one's vitals. Exit 2 when the game is running but there is nothing to read,
        /// which is the normal answer at the frontend and in menus.
        /// </summary>
        public static int TrainerRead(CliContext ctx, int? processId)
        {
            const string command = "trainer.read";
            GameProfileManagedProcessRegistry registry = OpenRegistry();
            registry.PruneDeadLeases();

            if (!TryResolveTarget(ctx, command, registry, processId, out GameProfileManagedProcess target, out int failure))
                return failure;

            LiveTrainerAttachOutcome attach = LiveTrainerSession.Attach(target, registry);
            if (!attach.Success || attach.Session is null)
                return ctx.Usage(command, attach.Message);

            using LiveTrainerSession session = attach.Session;
            LiveTrainerReadResult reading = session.Read();
            object payload = BuildReadPayload(target, reading);

            if (!ctx.Json)
                RenderReading(ctx, reading);

            return reading.HasVitals
                ? ctx.Ok(command, payload)
                : ctx.Verdict(command, reading.Message, payload);
        }

        /// <summary>
        /// Set one or more vitals. Each one is re-read immediately before it is written and the
        /// write is refused unless that read came back believable, so a wrong offset cannot be
        /// written through.
        /// </summary>
        public static int TrainerSet(CliContext ctx, int? processId, float? life, float? energy, float? shields)
        {
            const string command = "trainer.set";

            var requested = new List<(LiveTrainerVital Vital, float Value)>();
            if (life is not null)
                requested.Add((LiveTrainerVital.Life, life.Value));
            if (energy is not null)
                requested.Add((LiveTrainerVital.Energy, energy.Value));
            if (shields is not null)
                requested.Add((LiveTrainerVital.Shields, shields.Value));

            if (requested.Count == 0)
            {
                return ctx.Usage(
                    command,
                    "Nothing to set. Pass at least one of --life, --energy, --shields.",
                    "Read the current values first: trainer read");
            }

            GameProfileManagedProcessRegistry registry = OpenRegistry();
            registry.PruneDeadLeases();

            if (!TryResolveTarget(ctx, command, registry, processId, out GameProfileManagedProcess target, out int failure))
                return failure;

            LiveTrainerAttachOutcome attach = LiveTrainerSession.Attach(target, registry);
            if (!attach.Success || attach.Session is null)
                return ctx.Usage(command, attach.Message);

            using LiveTrainerSession session = attach.Session;

            // Show what is there before touching it, and refuse the whole batch if the read is not
            // believable. This is the same gate the GUI puts in front of its write controls.
            LiveTrainerReadResult before = session.Read();
            if (!before.WritingCanBeOffered)
            {
                return ctx.Verdict(
                    command,
                    before.HasVitals
                        ? "The values read back do not look like vitals, so nothing was written."
                        : before.Message,
                    BuildReadPayload(target, before));
            }

            ctx.Warn(
                "The game rewrites these fields about 20 times a second, so a single write is usually "
                    + "overwritten almost immediately. Holding a value needs the app's Cheats page.");
            if (shields is not null)
            {
                ctx.Warn(
                    "In walker mode the game copies energy into shields on every update, so setting "
                        + "shields on its own will not stick.");
            }

            var results = new List<object>();
            bool allSucceeded = true;
            foreach ((LiveTrainerVital vital, float value) in requested)
            {
                LiveTrainerWriteOutcome outcome = session.Write(vital, value);
                allSucceeded &= outcome.Success;
                results.Add(new
                {
                    vital = LiveTrainerAddresses.NameOf(vital),
                    requested = value,
                    success = outcome.Success,
                    message = outcome.Message,
                    address = outcome.Before is null ? null : "0x" + outcome.Before.Address.ToString("X8", CultureInfo.InvariantCulture),
                    before = outcome.Before?.AsSingle,
                    beforeRaw = outcome.Before?.RawHex,
                    readBack = outcome.After?.AsSingle,
                    readBackRaw = outcome.After?.RawHex,
                });

                if (!ctx.Json)
                    ctx.Line(outcome.Message);
            }

            object payload = new
            {
                processId = target.ProcessId,
                copyId = Path.GetFileName(Path.TrimEndingDirectorySeparator(target.WorkingDirectory)),
                writes = results.ToArray(),
                vitalOffsetsConfirmedAgainstALiveProcess = true,
            };

            return allSucceeded
                ? ctx.Ok(command, payload)
                : ctx.Verdict(command, "At least one write did not go through.", payload);
        }

        // ================================================================ helpers

        private static object BuildReadPayload(GameProfileManagedProcess target, LiveTrainerReadResult reading) => new
        {
            processId = target.ProcessId,
            copyId = Path.GetFileName(Path.TrimEndingDirectorySeparator(target.WorkingDirectory)),
            status = reading.Status.ToString(),
            message = reading.Message,
            missionRunning = reading.HasVitals,
            writingCanBeOffered = reading.WritingCanBeOffered,
            playerPointer = reading.Vitals is null ? null : "0x" + reading.Vitals.PlayerPointer.ToString("X8", CultureInfo.InvariantCulture),
            battleEnginePointer = reading.Vitals is null ? null : "0x" + reading.Vitals.BattleEnginePointer.ToString("X8", CultureInfo.InvariantCulture),
            life = Describe(reading.Vitals?.Life),
            energy = Describe(reading.Vitals?.Energy),
            shields = Describe(reading.Vitals?.Shields),
            state = reading.Vitals is null
                ? null
                : new
                {
                    raw = reading.Vitals.State.AsInt32,
                    rawHex = reading.Vitals.State.RawHex,
                    name = reading.Vitals.StateName,
                },
            vitalOffsetsConfirmedAgainstALiveProcess = true,
        };

        private static object? Describe(LiveTrainerFieldReading? field) => field is null
            ? null
            : new
            {
                address = "0x" + field.Address.ToString("X8", CultureInfo.InvariantCulture),
                asDecimal = field.AsSingle,
                asWholeNumber = field.AsInt32,
                raw = field.RawHex,
                looksLikeAVital = field.LooksLikeAVital,
            };

        private static void RenderReading(CliContext ctx, LiveTrainerReadResult reading)
        {
            if (!reading.HasVitals)
            {
                ctx.Line(reading.Message);
                return;
            }

            LivePlayerVitals vitals = reading.Vitals!;
            ctx.Line($"Player one battle engine at 0x{vitals.BattleEnginePointer:X8} (player 0x{vitals.PlayerPointer:X8})");
            ctx.Line();
            ctx.Line($"{"Field",-10} {"As a number",-16} {"Raw",-12} {"Believable"}");
            ctx.Line(new string('-', 56));
            foreach (LiveTrainerVital vital in new[] { LiveTrainerVital.Life, LiveTrainerVital.Energy, LiveTrainerVital.Shields })
            {
                LiveTrainerFieldReading field = vitals.Field(vital);
                ctx.Line($"{LiveTrainerAddresses.NameOf(vital),-10} {field.AsSingle.ToString("0.###", CultureInfo.InvariantCulture),-16} {field.RawHex,-12} {(field.LooksLikeAVital ? "yes" : "NO")}");
            }

            ctx.Line($"{"state",-10} {vitals.State.AsInt32.ToString(CultureInfo.InvariantCulture),-16} {vitals.State.RawHex,-12} {vitals.StateName ?? "(unknown value)"}");
            ctx.Line();
            ctx.Line("These offsets have never been read from a running game before. If the numbers above");
            ctx.Line("look like nonsense, they are - do not write to them.");
        }

        /// <summary>
        /// Finds the copy to work on: the one whose id was given, or the newest one that is still
        /// genuinely running. Anything that is not a registered, still-live managed process is a
        /// verdict rather than an error - "no copy is running" is an answer, not a mistake.
        /// </summary>
        private static bool TryResolveTarget(
            CliContext ctx,
            string command,
            GameProfileManagedProcessRegistry registry,
            int? processId,
            out GameProfileManagedProcess target,
            out int exitCode)
        {
            target = null!;
            exitCode = CliExit.Success;

            if (processId is not null)
            {
                if (processId.Value <= 0)
                {
                    exitCode = ctx.Usage(command, "A positive process id is required.");
                    return false;
                }

                GameProfileRegisteredProcess? match = registry.Snapshot()
                    .FirstOrDefault(row => row.Process.ProcessId == processId.Value);
                if (match is null)
                {
                    exitCode = ctx.Verdict(
                        command,
                        $"Process {processId.Value} is not a managed safe-copy process this app launched.",
                        new { processId = processId.Value, attached = false });
                    return false;
                }

                target = match.Process;
                return true;
            }

            if (!registry.TryResolveLiveManagedProcess(out GameProfileRegisteredProcess live))
            {
                exitCode = ctx.Verdict(
                    command,
                    "No safe copy launched by this app is running.",
                    new { attached = false },
                    "Launch one first: copy launch <id>");
                return false;
            }

            target = live.Process;
            return true;
        }
    }
}
