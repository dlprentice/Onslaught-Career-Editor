using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.Cli
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
    /// Holding a value means writing it ten times a second for as long as it is wanted, which needs
    /// a process that stays alive. This lane used to argue that made it the wrong shape for a CLI
    /// and left the feature to the GUI - which meant the headless twin could read a trainer's
    /// numbers and not act on them. <see cref="TrainerHold"/> settles it the honest way instead: it
    /// holds for a stated time, says so, and always lets go.
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
                ctx.Line("Life, energy and shields were read out of a running mission on 1 August 2026,");
                ctx.Line("and setting life took. Read them before writing anything - the app refuses the");
                ctx.Line("write if what comes back does not look like vitals.");
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
                    + "overwritten almost immediately. To make one stick: trainer hold --life 100 --for 30");
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

        /// <summary>
        /// Hold vitals at a value for a while.
        ///
        /// A single write is almost a no-op - the game rewrites these fields about twenty times a
        /// second - so the GUI has always had per-vital hold toggles and the CLI has not. That gap
        /// meant the headless twin could not do the one thing a trainer is actually for, and
        /// <c>trainer set</c> had to end by telling people to go and use the app instead.
        ///
        /// The loop, the 10 Hz rate, the self-stop when the mission ends and the release-everything
        /// on the way out are all <see cref="LiveTrainerHold"/> - the same code the GUI drives. Only
        /// the timer belongs to this verb.
        /// </summary>
        public static int TrainerHold(
            CliContext ctx,
            int? processId,
            float? life,
            float? energy,
            float? shields,
            double seconds)
        {
            const string command = "trainer.hold";

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
                    "Nothing to hold. Pass at least one of --life, --energy, --shields.",
                    "Read the current values first: trainer read");
            }

            if (seconds is <= 0 or > 3600)
            {
                return ctx.Usage(
                    command,
                    "--for must be between 1 and 3600 seconds.",
                    "This verb holds for a stated time and then lets go; it is not a daemon.");
            }

            GameProfileManagedProcessRegistry registry = OpenRegistry();
            registry.PruneDeadLeases();

            if (!TryResolveTarget(ctx, command, registry, processId, out GameProfileManagedProcess target, out int failure))
                return failure;

            LiveTrainerAttachOutcome attach = LiveTrainerSession.Attach(target, registry);
            if (!attach.Success || attach.Session is null)
                return ctx.Usage(command, attach.Message);

            using LiveTrainerSession session = attach.Session;

            LiveTrainerReadResult before = session.Read();
            if (!before.WritingCanBeOffered)
            {
                return ctx.Verdict(
                    command,
                    before.HasVitals
                        ? "The values read back do not look like vitals, so nothing was held."
                        : before.Message,
                    BuildReadPayload(target, before));
            }

            var hold = new LiveTrainerHold(session);
            foreach ((LiveTrainerVital vital, float value) in requested)
            {
                if (!hold.TryHold(vital, value, out string refusal))
                {
                    hold.ReleaseAll();
                    return ctx.Usage(command, $"{LiveTrainerAddresses.NameOf(vital)}: {refusal}");
                }
            }

            if (shields is not null)
            {
                ctx.Warn(
                    "In walker mode the game copies energy into shields on every update, so holding "
                        + "shields on its own will not stick - hold energy as well.");
            }

            TimeSpan interval = LiveTrainerHold.ClampInterval(LiveTrainerHold.DefaultInterval);
            ctx.Line($"Holding {string.Join(", ", requested.Select(entry => $"{LiveTrainerAddresses.NameOf(entry.Vital)}={entry.Value:0.###}"))} " +
                     $"for {seconds:0.#}s at {1000 / interval.TotalMilliseconds:0.#} Hz. Ctrl+C stops it.");

            int ticks = 0;
            int attempted = 0;
            int succeeded = 0;
            string stopReason = "The time ran out.";
            bool stoppedItself = false;

            DateTime deadline = DateTime.UtcNow.AddSeconds(seconds);
            while (DateTime.UtcNow < deadline)
            {
                LiveTrainerHoldTick tick = hold.Tick();
                ticks++;
                attempted += tick.Attempted;
                succeeded += tick.Succeeded;

                if (tick.StoppedItself)
                {
                    stoppedItself = true;
                    stopReason = tick.Message;
                    break;
                }

                Thread.Sleep(interval);
            }

            // Whatever happened, let go. A CLI that exits still holding would leave the game being
            // written to by a process that is no longer there to stop.
            hold.ReleaseAll();

            LiveTrainerReadResult after = session.Read();
            object payload = new
            {
                processId = target.ProcessId,
                copyId = Path.GetFileName(Path.TrimEndingDirectorySeparator(target.WorkingDirectory)),
                held = requested.Select(entry => new
                {
                    vital = LiveTrainerAddresses.NameOf(entry.Vital),
                    value = entry.Value,
                }).ToArray(),
                seconds,
                intervalMilliseconds = interval.TotalMilliseconds,
                ticks,
                writesAttempted = attempted,
                writesSucceeded = succeeded,
                stoppedItself,
                stopReason,
                reading = BuildReadPayload(target, after),
                vitalOffsetsConfirmedAgainstALiveProcess = true,
            };

            if (!ctx.Json)
            {
                ctx.Line();
                ctx.Line($"{succeeded} of {attempted} writes landed over {ticks} passes. {stopReason}");
                ctx.Line("Released. The game owns those fields again.");
            }

            return stoppedItself && succeeded == 0
                ? ctx.Verdict(command, stopReason, payload)
                : ctx.Ok(command, payload);
        }

        /// <summary>
        /// Render the trainer's music to a file.
        ///
        /// The tune is generated, not shipped, so there is no file to go and listen to - which
        /// makes it exactly the sort of thing that rots unheard. This writes it out so it can be
        /// played, diffed, or checked by something that is not a person with speakers.
        /// </summary>
        public static int TrainerMusic(CliContext ctx, string? track, string? outputPath)
        {
            const string command = "trainer.music";

            TrainerMusicTrack selected = TrainerMusicTrack.Ascent;
            if (!string.IsNullOrWhiteSpace(track) &&
                !Enum.TryParse(track, ignoreCase: true, out selected))
            {
                return ctx.Usage(
                    command,
                    $"Unknown track '{track}'.",
                    "Tracks: " + string.Join(", ", Enum.GetNames<TrainerMusicTrack>()).ToLowerInvariant());
            }

            byte[] wav = TrainerMusicSynth.Render(selected);
            TimeSpan duration = TrainerMusicSynth.GetDuration(selected);

            if (string.IsNullOrWhiteSpace(outputPath))
            {
                return ctx.Ok(
                    command,
                    DescribeMusic(selected, wav, duration, writtenTo: null),
                    $"{TrainerMusicSynth.GetDisplayName(selected)}: {duration.TotalSeconds:0.#}s, " +
                        $"{wav.Length / 1024.0:0} KB. Pass --out to write it somewhere.");
            }

            string resolved;
            try
            {
                resolved = Path.GetFullPath(outputPath.Trim());
                string? directory = Path.GetDirectoryName(resolved);
                if (!string.IsNullOrWhiteSpace(directory))
                    Directory.CreateDirectory(directory);

                File.WriteAllBytes(resolved, wav);
            }
            catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
            {
                return ctx.Usage(command, $"Could not write that file: {ex.Message}");
            }

            return ctx.Ok(
                command,
                DescribeMusic(selected, wav, duration, resolved),
                $"Wrote {TrainerMusicSynth.GetDisplayName(selected)} to {resolved} ({duration.TotalSeconds:0.#}s).");
        }

        private static object DescribeMusic(
            TrainerMusicTrack track,
            byte[] wav,
            TimeSpan duration,
            string? writtenTo) => new
            {
                track = track.ToString().ToLowerInvariant(),
                displayName = TrainerMusicSynth.GetDisplayName(track),
                seconds = Math.Round(duration.TotalSeconds, 2),
                bytes = wav.Length,
                sampleRate = TrainerMusicSynth.SampleRate,
                channels = 1,
                writtenTo,
                originalToThisProject = true,
            };

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

            // Read and reported, never written. The offset came out of CBattleEngine::Damage in
            // the pristine specimen on 2026-08-01; nothing has written to it in a running game, so
            // there is no `trainer set --vulnerable` and the payload says why in the same breath
            // it hands over the number.
            damageSwitch = reading.Vitals?.Vulnerable is null
                ? null
                : new
                {
                    address = "0x" + reading.Vitals.Vulnerable.Address.ToString("X8", CultureInfo.InvariantCulture),
                    raw = reading.Vitals.Vulnerable.AsInt32,
                    rawHex = reading.Vitals.Vulnerable.RawHex,
                    looksLikeABool = reading.Vitals.VulnerableLooksLikeABool,
                    invulnerable = reading.Vitals.IsInvulnerable,
                    provenLiveByAWrite = false,
                    note = "Zero means damage is undone. Position read from the bytes, never written "
                        + "in a running game - so no verb sets it. The save-name God mode cheat was "
                        + "checked in a real mission and is the working route.",
                },
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

            if (vitals.Vulnerable is not null)
            {
                string meaning = vitals.IsInvulnerable switch
                {
                    true => "0 = damage is undone",
                    false => "1 = damage counts",
                    null => "not 0 or 1, so this is not the switch",
                };
                ctx.Line($"{"damage",-10} {vitals.Vulnerable.AsInt32.ToString(CultureInfo.InvariantCulture),-16} {vitals.Vulnerable.RawHex,-12} {meaning}");
            }

            ctx.Line();
            ctx.Line("These three were read out of a running mission on 1 August 2026, and changing life");
            ctx.Line("took. If the numbers above look like nonsense, they are - and writing is refused.");
            ctx.Line("The damage switch is shown and never set: its position is known from the bytes,");
            ctx.Line("but nothing has written to it in a running game.");
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
