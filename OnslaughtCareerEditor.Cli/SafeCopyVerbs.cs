using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.Cli
{
    /// <summary>
    /// The safe-copy, binary-patch, launch, and managed-process lane.
    ///
    /// This is the half of the app that had no headless twin at all, which is why an agent could create
    /// nothing, verify nothing, and clean up nothing without a human driving the GUI. Every operation
    /// here goes through the same AppCore services the GUI calls, with the same roots, so the two cannot
    /// disagree about what is app-owned.
    ///
    /// Two roots exist and must never be confused:
    ///   - <see cref="SafeCopyRoot"/> (GameProfiles) holds whole playable copied game folders.
    ///   - <see cref="PatchBenchRoot"/> (PatchBench) holds BEA.exe-only working copies for the patch
    ///     engine.
    /// The installed game is never a target of either, and cannot be reached by any verb under
    /// <c>copy</c> or by <c>patch plan/verify/apply/restore</c>: <see cref="BinaryPatchEngine"/>
    /// independently refuses Program Files and steamapps shapes for those, so a mistake is caught
    /// twice.
    ///
    /// The one way to reach it is the <c>patch install</c> group, where saying so is the point. Those
    /// verbs still cannot write until <c>AuthorizeInstalledGameWrite</c> has put a verified original
    /// beside the executable, so "the installed game is off limits" became "the installed game costs
    /// a backup" rather than becoming nothing.
    /// </summary>
    public static class SafeCopyVerbs
    {
        public static string SafeCopyRoot => AppConfig.GetGameProfilesDir();

        public static string PatchBenchRoot => Path.Combine(AppConfig.GetConfigDir(), "PatchBench");

        public static string LeasePath =>
            Path.Combine(SafeCopyRoot, GameProfileManagedProcessRegistry.LeaseFileName);

        private static GameProfileManagedProcessRegistry OpenRegistry()
        {
            // The registry compares the lease file's own directory against the app-owned root it is
            // handed on Register, so these must resolve identically or every registration throws.
            Directory.CreateDirectory(SafeCopyRoot);
            return new GameProfileManagedProcessRegistry(LeasePath);
        }

        // ================================================================ copy

        /// <summary>
        /// Enumerate the app-owned playable copied game folders.
        ///
        /// There is no AppCore or GUI equivalent to copy here: the GUI only ever tracks the single most
        /// recent copy it made plus whatever the process lease still points at, so it cannot tell you
        /// what is on disk. Identification is by the generated manifest - a directory under the root
        /// without one is reported as unmanaged and is never a valid target for launch or delete.
        /// </summary>
        public static int CopyList(CliContext ctx)
        {
            const string command = "copy.list";
            string root = SafeCopyRoot;

            if (!Directory.Exists(root))
            {
                return ctx.Ok(command, new { root, count = 0, copies = Array.Empty<object>() },
                    $"No safe copies: {root} does not exist yet.");
            }

            GameProfileManagedProcessRegistry registry = OpenRegistry();
            registry.PruneDeadLeases();
            IReadOnlyList<GameProfileRegisteredProcess> live = registry.Snapshot();

            var rows = new List<object>();
            string[] directories;
            try
            {
                directories = Directory.GetDirectories(root).OrderBy(path => path, StringComparer.OrdinalIgnoreCase).ToArray();
            }
            catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
            {
                return ctx.Usage(command, SaveVerbs.DescribeFileFailure(ex));
            }

            foreach (string directory in directories)
            {
                string id = Path.GetFileName(directory);
                string manifestPath = Path.Combine(directory, GameProfilePreflightService.ProfileManifestFileName);
                bool managed = File.Exists(manifestPath) && File.Exists(Path.Combine(directory, "BEA.exe"));

                GameProfileRegisteredProcess? runningLease = live.FirstOrDefault(row =>
                    string.Equals(
                        Path.GetFullPath(row.Process.WorkingDirectory).TrimEnd(Path.DirectorySeparatorChar),
                        Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar),
                        StringComparison.OrdinalIgnoreCase));

                // A lease only counts as running when the process still passes the identity check, so a
                // recycled process id can never be reported as a live game.
                bool running = runningLease is not null &&
                               GameProfileRuntimeService.IsManagedProcessLive(runningLease.Process);

                ManifestSummary manifest = ReadManifestSummary(manifestPath);
                long sizeBytes = SafeCopyCatalogService.MeasureDirectoryBytes(directory);
                int careerSaveCount = CountCareerSaves(directory, root);
                rows.Add(new
                {
                    id,
                    path = directory,
                    managed,
                    running,
                    sizeBytes,
                    careerSaveCount,
                    processId = running ? runningLease!.Process.ProcessId : (int?)null,
                    startedAt = running ? runningLease!.Process.StartedAt : (DateTimeOffset?)null,
                    schemaVersion = manifest.SchemaVersion,
                    generatedAt = manifest.GeneratedAt,
                    profilePresetId = manifest.PresetId,
                    profilePresetDisplayName = manifest.PresetDisplayName,
                    patchKeys = manifest.PatchKeys,
                    launchArguments = manifest.LaunchArguments,
                    entryCount = manifest.EntryCount,
                });
            }

            if (ctx.Json)
                return ctx.Ok(command, new { root, count = rows.Count, copies = rows.ToArray() });

            ctx.Line($"Safe copies under: {root}");
            ctx.Line();
            if (rows.Count == 0)
            {
                ctx.Line("None found.");
                return CliExit.Success;
            }

            ctx.Line($"{"Id",-36} {"Size",-9} {"Careers",-8} {"Managed",-8} {"Running",-8} {"Preset",-20}");
            ctx.Line(new string('-', 94));
            long totalBytes = 0;
            foreach (string directory in directories)
            {
                string id = Path.GetFileName(directory);
                string manifestPath = Path.Combine(directory, GameProfilePreflightService.ProfileManifestFileName);
                bool managed = File.Exists(manifestPath) && File.Exists(Path.Combine(directory, "BEA.exe"));
                GameProfileRegisteredProcess? lease = live.FirstOrDefault(row =>
                    string.Equals(
                        Path.GetFullPath(row.Process.WorkingDirectory).TrimEnd(Path.DirectorySeparatorChar),
                        Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar),
                        StringComparison.OrdinalIgnoreCase));
                bool running = lease is not null && GameProfileRuntimeService.IsManagedProcessLive(lease.Process);
                ManifestSummary manifest = ReadManifestSummary(manifestPath);
                long sizeBytes = SafeCopyCatalogService.MeasureDirectoryBytes(directory);
                totalBytes += sizeBytes;
                ctx.Line(
                    $"{Truncate(id, 36),-36} {SafeCopyCatalogService.DescribeSize(sizeBytes),-9} " +
                    $"{CountCareerSaves(directory, root),-8} {(managed ? "yes" : "NO"),-8} {(running ? "yes" : "no"),-8} " +
                    $"{Truncate(manifest.PresetId ?? "(custom)", 20),-20}");
            }

            ctx.Line();
            ctx.Line($"{rows.Count} folder(s), {SafeCopyCatalogService.DescribeSize(totalBytes)} total. 'Managed: NO' means no generated manifest; those cannot be launched or deleted.");
            ctx.Line("Careers is what a delete would take with it. See them: copy saves <id>");
            return CliExit.Success;
        }

        /// <summary>
        /// How many careers a delete would take with it, or 0 for a folder this app cannot vouch
        /// for. Reported beside the size because those are the two numbers that decide whether a
        /// copy is disposable.
        /// </summary>
        private static int CountCareerSaves(string profileRoot, string appOwnedProfilesRoot)
        {
            try
            {
                return SafeCopySaveRescueService.Inventory(profileRoot, appOwnedProfilesRoot).Saves.Count;
            }
            catch (Exception ex) when (ex is InvalidOperationException or IOException
                                        or UnauthorizedAccessException or ArgumentException
                                        or DirectoryNotFoundException)
            {
                return 0;
            }
        }

        public static int CopyCreate(
            CliContext ctx,
            string? sourceGameRoot,
            string? executableOverride,
            string? profileName,
            string? presetId,
            IReadOnlyList<string>? patchKeys,
            IReadOnlyList<string>? launchArguments,
            string? resolution,
            bool includeSavegames,
            string? musicSwapPresetId,
            bool level100TextMod,
            bool level100EarlyFlightMod)
        {
            const string command = "copy.create";

            string? resolvedSource = sourceGameRoot;
            if (string.IsNullOrWhiteSpace(resolvedSource))
            {
                AppConfig config = AppConfig.Load();
                resolvedSource = config.GetGameDir() ?? AppConfig.DetectGameDirectory();
                if (resolvedSource is null)
                {
                    return ctx.Usage(
                        command,
                        "No source game root given and none could be detected.",
                        "Pass --source <path>, or set one with 'config set-game-dir <path>'.");
                }
            }

            if (!Directory.Exists(resolvedSource))
                return ctx.Usage(command, $"Source game root does not exist: {resolvedSource}");

            // Same shape the GUI generates. AppCore independently enforces ^[A-Za-z0-9._-]{1,64}$, so a
            // caller-supplied name that would be unsafe as a folder is rejected there rather than here.
            string name = string.IsNullOrWhiteSpace(profileName)
                ? $"safe-game-copy-{DateTime.UtcNow:yyyyMMdd-HHmmss-fff}-{Guid.NewGuid().ToString("N")[..8]}"
                : profileName.Trim();

            // The GUI seeds a new copy with the compatibility profile's own
            // launch arguments; the CLI used to pass none, so a copy made
            // headlessly launched without the -res the profile expects. Match
            // the GUI unless the caller supplied their own arguments.
            IReadOnlyList<string> resolvedLaunchArguments =
                launchArguments is { Count: > 0 }
                    ? launchArguments
                    : BinaryPatchPlanBuilder
                        .GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.CompatibilityProfileId)
                        .Modules
                        .SelectMany(module => module.LaunchArguments)
                        .ToArray();

            if (!string.IsNullOrWhiteSpace(resolution))
            {
                if (!DisplayResolutionPreset.TryParse(resolution, out DisplayResolutionPreset preset, out string? problem))
                {
                    return ctx.Usage(command, problem ?? "That resolution cannot be used.");
                }

                resolvedLaunchArguments = preset.ApplyTo(resolvedLaunchArguments);
                if (!preset.IsMeasured)
                {
                    ctx.Warn($"{preset.Label} has not been played and measured; 1600x900 is the size that has.");
                }
            }

            Directory.CreateDirectory(SafeCopyRoot);

            var options = new GameProfilePrepareOptions(
                SourceGameRoot: resolvedSource,
                OutputRoot: SafeCopyRoot,
                ProfileName: name,
                ExecutableOverridePath: string.IsNullOrWhiteSpace(executableOverride) ? null : executableOverride,
                ApplyWindowedCompatibilityPatch: true,
                AllowByteLayoutOnlyTarget: false,
                IncludeSavegames: includeSavegames,
                PatchKeys: patchKeys?.ToArray() ?? Array.Empty<string>(),
                LaunchArguments: resolvedLaunchArguments.ToArray(),
                ProfilePresetId: string.IsNullOrWhiteSpace(presetId) ? null : presetId,
                MusicSwapPresetId: string.IsNullOrWhiteSpace(musicSwapPresetId) ? null : musicSwapPresetId,
                ApplyLevel100TutorialTextMod: level100TextMod,
                ApplyLevel100EarlyFlightMod: level100EarlyFlightMod);

            GameProfilePrepareResult result;
            try
            {
                result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(options);
            }
            catch (Exception ex) when (ex is InvalidOperationException or DirectoryNotFoundException
                                        or FileNotFoundException or IOException or UnauthorizedAccessException)
            {
                return ctx.Usage(command, ex.Message);
            }

            object payload = new
            {
                id = Path.GetFileName(Path.TrimEndingDirectorySeparator(result.TargetGameRoot)),
                schemaVersion = result.SchemaVersion,
                generatedAt = result.GeneratedAt,
                sourceGameRoot = result.SourceGameRoot,
                targetGameRoot = result.TargetGameRoot,
                executablePath = result.ExecutablePath,
                manifestPath = result.ManifestPath,
                entryCount = result.Entries.Count,
                profilePresetId = result.ProfilePresetId,
                profilePresetDisplayName = result.ProfilePresetDisplayName,
                profilePresetProofStatus = result.ProfilePresetProofStatus,
                patchResult = new
                {
                    requested = result.PatchResult.Requested,
                    success = result.PatchResult.Success,
                    patchKeys = result.PatchResult.PatchKeys,
                    message = result.PatchResult.Message,
                },
                launchPlan = new
                {
                    executablePath = result.LaunchPlan.ExecutablePath,
                    workingDirectory = result.LaunchPlan.WorkingDirectory,
                    arguments = result.LaunchPlan.Arguments,
                    commandPreview = result.LaunchPlan.CommandPreview,
                },
                level100TextMod = result.Level100TextModResult is null ? null : new { applied = true },
                level100EarlyFlightMod = result.Level100EarlyFlightModResult is null ? null : new { applied = true },
            };

            if (!ctx.Json)
            {
                ctx.Line("Safe copy created.");
                ctx.Line($"  Id:      {Path.GetFileName(Path.TrimEndingDirectorySeparator(result.TargetGameRoot))}");
                ctx.Line($"  Folder:  {result.TargetGameRoot}");
                ctx.Line($"  Entries: {result.Entries.Count}");
                ctx.Line($"  Patches: {(result.PatchResult.PatchKeys.Count == 0 ? "(none)" : string.Join(", ", result.PatchResult.PatchKeys))}");
                ctx.Line($"  Launch:  {result.LaunchPlan.CommandPreview}");
            }

            // The prepare succeeded but its patch pass can independently report failure; that is a
            // verdict about the copied bytes, not a bad invocation.
            return result.PatchResult.Requested && !result.PatchResult.Success
                ? ctx.Verdict(command, result.PatchResult.Message, payload)
                : ctx.Ok(command, payload);
        }

        public static int CopyLaunch(CliContext ctx, string? id, IReadOnlyList<string>? launchArguments)
        {
            const string command = "copy.launch";
            if (!TryResolveProfileRoot(ctx, command, id, out string profileRoot, out int failure))
                return failure;

            GameProfileManagedProcessRegistry registry = OpenRegistry();
            registry.PruneDeadLeases();

            GameProfileLaunchPlan plan;
            try
            {
                plan = GameProfilePreflightService.BuildLaunchPlan(profileRoot, launchArguments?.ToArray());
            }
            catch (Exception ex) when (ex is InvalidOperationException or DirectoryNotFoundException or IOException)
            {
                return ctx.Usage(command, ex.Message);
            }

            GameProfileManagedProcess launched;
            try
            {
                launched = GameProfileRuntimeService.LaunchCopiedProfile(new GameProfileLaunchOptions(
                    ProfileRoot: plan.WorkingDirectory,
                    AppOwnedProfilesRoot: SafeCopyRoot,
                    LaunchArguments: launchArguments?.ToArray()));
                registry.Register(launched, SafeCopyRoot);
            }
            catch (Exception ex) when (ex is InvalidOperationException or DirectoryNotFoundException
                                        or IOException or System.ComponentModel.Win32Exception)
            {
                return ctx.Usage(command, ex.Message);
            }

            return ctx.Ok(command, new
            {
                id = Path.GetFileName(Path.TrimEndingDirectorySeparator(profileRoot)),
                processId = launched.ProcessId,
                executablePath = launched.ExecutablePath,
                workingDirectory = launched.WorkingDirectory,
                arguments = launched.Arguments,
                startedAt = launched.StartedAt,
                commandPreview = plan.CommandPreview,
            }, $"Launched pid {launched.ProcessId}: {plan.CommandPreview}");
        }

        public static int CopyStop(CliContext ctx, string? id)
        {
            const string command = "copy.stop";
            if (!TryResolveProfileRoot(ctx, command, id, out string profileRoot, out int failure))
                return failure;

            GameProfileManagedProcessRegistry registry = OpenRegistry();
            registry.PruneDeadLeases();

            GameProfileRegisteredProcess? match = registry.Snapshot().FirstOrDefault(row =>
                string.Equals(
                    Path.GetFullPath(row.Process.WorkingDirectory).TrimEnd(Path.DirectorySeparatorChar),
                    Path.GetFullPath(profileRoot).TrimEnd(Path.DirectorySeparatorChar),
                    StringComparison.OrdinalIgnoreCase));

            if (match is null)
            {
                return ctx.Verdict(
                    command,
                    "No live managed process is registered for that safe copy.",
                    new { id = Path.GetFileName(Path.TrimEndingDirectorySeparator(profileRoot)), running = false });
            }

            GameProfileStopResult result = registry.Stop(match.Process);
            object payload = new
            {
                id = Path.GetFileName(Path.TrimEndingDirectorySeparator(profileRoot)),
                processId = result.ProcessId,
                success = result.Success,
                message = result.Message,
                liveBeforeStop = result.LiveBeforeStop,
                closeRequested = result.CloseRequested,
                forceRequested = result.ForceRequested,
                exitObserved = result.ExitObserved,
                alreadyGone = result.AlreadyGone,
                exitTime = result.ExitTime,
            };

            if (!ctx.Json)
                ctx.Line(result.Message);

            return result.Success ? ctx.Ok(command, payload) : ctx.Verdict(command, result.Message, payload);
        }

        /// <summary>
        /// Delete one app-owned safe copy.
        ///
        /// Two refusals stack here. This layer refuses to delete a copy that a registered process is
        /// still running out of, because pulling the files out from under a live game is a data-loss
        /// bug wearing a cleanup costume. AppCore then independently refuses anything that is not a
        /// manifest-carrying folder strictly under the app-owned root - so a wrong path fails even if
        /// this check were bypassed.
        /// </summary>
        public static int CopyDelete(
            CliContext ctx,
            string? id,
            bool force,
            string? keepSavesIn = null,
            bool discardSaves = false)
        {
            const string command = "copy.delete";
            if (!TryResolveProfileRoot(ctx, command, id, out string profileRoot, out int failure, requireManifest: false))
                return failure;

            GameProfileManagedProcessRegistry registry = OpenRegistry();
            registry.PruneDeadLeases();

            GameProfileRegisteredProcess? lease = registry.Snapshot().FirstOrDefault(row =>
                string.Equals(
                    Path.GetFullPath(row.Process.WorkingDirectory).TrimEnd(Path.DirectorySeparatorChar),
                    Path.GetFullPath(profileRoot).TrimEnd(Path.DirectorySeparatorChar),
                    StringComparison.OrdinalIgnoreCase));

            if (lease is not null && GameProfileRuntimeService.IsManagedProcessLive(lease.Process))
            {
                return ctx.Usage(
                    command,
                    "That safe copy is still running; refusing to delete it.",
                    $"Stop it first: copy stop {Path.GetFileName(Path.TrimEndingDirectorySeparator(profileRoot))}");
            }

            if (!force)
            {
                return ctx.Usage(
                    command,
                    "Deleting a safe copy is irreversible; pass --force to confirm.",
                    $"Folder: {profileRoot}");
            }

            if (!string.IsNullOrWhiteSpace(keepSavesIn) && discardSaves)
            {
                return ctx.Usage(
                    command,
                    "--keep-saves-in and --discard-saves ask for opposite things; pass one.");
            }

            // The careers inside the copy are the only thing here the game cannot make again, so
            // the delete is gated on them and not on --force. --force says "yes, remove several
            // gigabytes of copied game"; it was never an answer to "and lose the save named
            // Maladim". Those are different questions and they get asked separately.
            SafeCopySaveInventory inventory;
            try
            {
                inventory = SafeCopySaveRescueService.Inventory(profileRoot, SafeCopyRoot);
            }
            catch (Exception ex) when (ex is InvalidOperationException or DirectoryNotFoundException
                                        or IOException or UnauthorizedAccessException)
            {
                return ctx.Usage(command, ex.Message);
            }

            string? atRisk = SafeCopySaveRescueService.DescribeSavesAtRisk(inventory);
            if (atRisk is not null && !discardSaves && string.IsNullOrWhiteSpace(keepSavesIn))
            {
                string copyId = Path.GetFileName(Path.TrimEndingDirectorySeparator(profileRoot));
                return ctx.Usage(
                    command,
                    atRisk,
                    $"Keep them: copy delete {copyId} --force --keep-saves-in <folder>",
                    $"Or lose them on purpose: copy delete {copyId} --force --discard-saves",
                    $"See them first: copy saves {copyId}");
            }

            string deleted;
            SafeCopySaveRescueResult? rescued = null;
            try
            {
                if (!string.IsNullOrWhiteSpace(keepSavesIn))
                {
                    SafeCopyRemovalResult removal = SafeCopySaveRescueService.RescueThenDelete(
                        profileRoot,
                        SafeCopyRoot,
                        keepSavesIn!,
                        allowOverwrite: false);

                    if (!removal.Success || removal.DeletedProfileRoot is null)
                        return ctx.Usage(command, removal.Message);

                    rescued = removal.Rescue;
                    deleted = removal.DeletedProfileRoot;
                }
                else
                {
                    deleted = GameProfilePreflightService.DeleteGeneratedProfile(
                        profileRoot,
                        SafeCopyRoot,
                        SafeCopySaveDisposition.DiscardSaves);
                }
            }
            catch (Exception ex) when (ex is InvalidOperationException or DirectoryNotFoundException
                                        or IOException or UnauthorizedAccessException)
            {
                return ctx.Usage(command, ex.Message);
            }

            if (lease is not null)
                registry.Forget(lease.Process);

            string summary = rescued is null
                ? $"Deleted safe copy: {deleted}"
                : $"{rescued.Message} Deleted safe copy: {deleted}";

            return ctx.Ok(
                command,
                new
                {
                    id = Path.GetFileName(Path.TrimEndingDirectorySeparator(deleted)),
                    path = deleted,
                    deleted = true,
                    savesKept = rescued?.RescuedCount ?? 0,
                    savesKeptIn = rescued is null ? null : rescued.DestinationDirectory,
                    savesDiscarded = rescued is null ? inventory.Saves.Count : 0,
                },
                summary);
        }

        // ========================================================== copy saves / rescue

        /// <summary>
        /// What one copy - or every copy - is holding, so nobody has to find out by deleting it.
        /// </summary>
        public static int CopySaves(CliContext ctx, string? id)
        {
            const string command = "copy.saves";

            if (string.IsNullOrWhiteSpace(id))
            {
                IReadOnlyList<SafeCopySaveInventory> all = SafeCopySaveRescueService.InventoryAll(SafeCopyRoot);
                if (ctx.Json)
                {
                    return ctx.Ok(command, new
                    {
                        root = SafeCopyRoot,
                        copies = all.Select(DescribeInventory).ToArray(),
                    });
                }

                if (all.Count == 0)
                    return ctx.Ok(command, new { root = SafeCopyRoot, copies = Array.Empty<object>() }, "No safe copies.");

                foreach (SafeCopySaveInventory row in all)
                {
                    ctx.Line($"{row.DisplayName}: {(row.HasSaves ? $"{row.Saves.Count} career save(s)" : "no career saves")}");
                    foreach (SafeCopySaveFile save in row.Saves)
                        ctx.Line($"    {save.FileName,-40} {save.Length,10:N0} bytes  {save.LastWriteUtc:yyyy-MM-dd HH:mm} UTC");
                }

                return CliExit.Success;
            }

            if (!TryResolveProfileRoot(ctx, command, id, out string profileRoot, out int failure, requireManifest: false))
                return failure;

            SafeCopySaveInventory inventory;
            try
            {
                inventory = SafeCopySaveRescueService.Inventory(profileRoot, SafeCopyRoot);
            }
            catch (Exception ex) when (ex is InvalidOperationException or DirectoryNotFoundException
                                        or IOException or UnauthorizedAccessException)
            {
                return ctx.Usage(command, ex.Message);
            }

            if (ctx.Json)
                return ctx.Ok(command, DescribeInventory(inventory));

            if (!inventory.HasSaves)
                return ctx.Ok(command, DescribeInventory(inventory), $"{inventory.DisplayName} has no career saves in it.");

            ctx.Line($"Career saves in {inventory.DisplayName}:");
            ctx.Line();
            foreach (SafeCopySaveFile save in inventory.Saves)
                ctx.Line($"{save.FileName,-40} {save.Length,10:N0} bytes  {save.LastWriteUtc:yyyy-MM-dd HH:mm} UTC");
            ctx.Line();
            ctx.Line($"Bring them out: copy rescue {inventory.DisplayName} --to <folder>");
            return CliExit.Success;
        }

        /// <summary>
        /// Copy career saves out of a copy. This never deletes anything - the copy is still
        /// playable afterwards - so it is safe to run before deciding what to do with the copy.
        /// </summary>
        public static int CopyRescue(
            CliContext ctx,
            string? id,
            string? destination,
            IReadOnlyList<string>? saveNames,
            bool overwrite)
        {
            const string command = "copy.rescue";
            if (!TryResolveProfileRoot(ctx, command, id, out string profileRoot, out int failure, requireManifest: false))
                return failure;

            if (string.IsNullOrWhiteSpace(destination))
                return ctx.Usage(command, "Say where the saves should go: --to <folder>.");

            SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest
                {
                    ProfileRoot = profileRoot,
                    DestinationDirectory = destination!,
                    FileNames = saveNames is { Count: > 0 } ? saveNames : null,
                    AllowOverwrite = overwrite,
                },
                SafeCopyRoot);

            object payload = new
            {
                id = Path.GetFileName(Path.TrimEndingDirectorySeparator(profileRoot)),
                destination = result.DestinationDirectory,
                rescued = result.RescuedCount,
                needsOverwriteConfirmation = result.NeedsOverwriteConfirmation,
                files = result.Files.Select(file => new
                {
                    fileName = file.FileName,
                    rescued = file.Rescued,
                    outputPath = file.OutputPath,
                    message = file.Message,
                }).ToArray(),
            };

            if (!result.Success)
            {
                return result.NeedsOverwriteConfirmation
                    ? ctx.Usage(command, result.Message, "Replace them on purpose: add --overwrite.")
                    : ctx.Usage(command, result.Message);
            }

            return ctx.Ok(command, payload, $"{result.Message} They are in {result.DestinationDirectory}.");
        }

        private static object DescribeInventory(SafeCopySaveInventory inventory) => new
        {
            id = inventory.DisplayName,
            path = inventory.ProfileRoot,
            count = inventory.Saves.Count,
            totalBytes = inventory.TotalBytes,
            saves = inventory.Saves.Select(save => new
            {
                fileName = save.FileName,
                fullPath = save.FullPath,
                folder = save.RelativeDirectory,
                length = save.Length,
                lastWriteUtc = save.LastWriteUtc,
            }).ToArray(),
        };

        // ================================================================ process

        public static int ProcessList(CliContext ctx)
        {
            const string command = "process.list";
            GameProfileManagedProcessRegistry registry = OpenRegistry();
            IReadOnlyList<GameProfileRegisteredProcess> pruned = registry.PruneDeadLeases();
            IReadOnlyList<GameProfileRegisteredProcess> rows = registry.Snapshot();

            foreach (GameProfileRegisteredProcess dead in pruned)
                ctx.Warn($"Dropped a stale lease for pid {dead.Process.ProcessId} ({dead.Process.WorkingDirectory}).");

            object[] payload = rows.Select(row => new
            {
                processId = row.Process.ProcessId,
                // Re-checked rather than assumed: the prune above already dropped the dead ones, but a
                // process can exit between the two calls and reporting it as live would be a lie.
                running = GameProfileRuntimeService.IsManagedProcessLive(row.Process),
                copyId = Path.GetFileName(Path.TrimEndingDirectorySeparator(row.Process.WorkingDirectory)),
                executablePath = row.Process.ExecutablePath,
                workingDirectory = row.Process.WorkingDirectory,
                arguments = row.Process.Arguments,
                startedAt = row.Process.StartedAt,
                manifestPath = row.Process.ManifestPath,
            }).ToArray();

            if (ctx.Json)
                return ctx.Ok(command, new { leasePath = LeasePath, count = payload.Length, processes = payload });

            ctx.Line($"Managed processes (lease: {LeasePath})");
            ctx.Line();
            if (payload.Length == 0)
            {
                ctx.Line("None running.");
                return CliExit.Success;
            }

            ctx.Line($"{"Pid",-8} {"Running",-8} {"Started",-22} {"Copy"}");
            ctx.Line(new string('-', 80));
            foreach (GameProfileRegisteredProcess row in rows)
            {
                bool running = GameProfileRuntimeService.IsManagedProcessLive(row.Process);
                string copyId = Path.GetFileName(Path.TrimEndingDirectorySeparator(row.Process.WorkingDirectory));
                ctx.Line($"{row.Process.ProcessId,-8} {(running ? "yes" : "no"),-8} {row.Process.StartedAt:yyyy-MM-dd HH:mm:ss,-22} {copyId}");
            }

            return CliExit.Success;
        }

        public static int ProcessStop(CliContext ctx, int processId)
        {
            const string command = "process.stop";
            if (processId <= 0)
                return ctx.Usage(command, "A positive process id is required.");

            GameProfileManagedProcessRegistry registry = OpenRegistry();
            GameProfileRegisteredProcess? match = registry.Snapshot()
                .FirstOrDefault(row => row.Process.ProcessId == processId);

            if (match is null)
            {
                return ctx.Verdict(
                    command,
                    $"Process {processId} is not registered as a managed safe-copy process.",
                    new { processId, registered = false });
            }

            GameProfileStopResult result = registry.Stop(match.Process);
            object payload = new
            {
                processId = result.ProcessId,
                success = result.Success,
                message = result.Message,
                liveBeforeStop = result.LiveBeforeStop,
                closeRequested = result.CloseRequested,
                forceRequested = result.ForceRequested,
                exitObserved = result.ExitObserved,
                alreadyGone = result.AlreadyGone,
                exitTime = result.ExitTime,
            };

            if (!ctx.Json)
                ctx.Line(result.Message);

            return result.Success ? ctx.Ok(command, payload) : ctx.Verdict(command, result.Message, payload);
        }

        // ================================================================ patch

        public static int PatchList(CliContext ctx)
        {
            const string command = "patch.list";
            IReadOnlyList<BinaryPatchSpec> specs = BinaryPatchPlanBuilder.GetVisibleSpecs();
            IReadOnlyList<SafeCopyProfilePreset> presets = BinaryPatchPlanBuilder.GetSafeCopyProfilePresets();

            if (ctx.Json)
            {
                return ctx.Ok(command, new
                {
                    catalogStatus = BinaryPatchEngine.CatalogStatus,
                    usingFallbackCatalog = BinaryPatchEngine.UsingFallbackCatalog,
                    profileCatalogVersion = BinaryPatchPlanBuilder.SafeCopyProfileCatalogVersion,
                    profileCatalogSha256 = BinaryPatchPlanBuilder.SafeCopyProfileCatalogSha256,
                    patches = specs.Select(spec => new
                    {
                        key = spec.Key,
                        track = spec.Track,
                        displayName = spec.DisplayName,
                        fileOffset = spec.FileOffset,
                        optional = spec.Optional,
                        proofLevel = spec.ProofLevel,
                        selectability = spec.Selectability,
                        exclusiveGroup = spec.ExclusiveGroup,
                        dependencies = spec.Dependencies,
                        conflicts = spec.Conflicts,
                        requiresWindowedPair = spec.RequiresWindowedPair,
                        regionCount = BinaryPatchEngine.GetPatchRegions(spec).Count,
                    }).ToArray(),
                    profiles = presets.Select(preset => new
                    {
                        id = preset.Id,
                        displayName = preset.DisplayName,
                        description = preset.Description,
                        isSelectable = preset.IsSelectable,
                        proofStatus = preset.ProofStatus,
                        patchKeys = preset.PatchKeys,
                    }).ToArray(),
                });
            }

            ctx.Line($"Patch catalog: {BinaryPatchEngine.CatalogStatus}");
            ctx.Line();
            ctx.Line($"{"Key",-30} {"Track",-14} {"Proof",-12} {"Name"}");
            ctx.Line(new string('-', 96));
            foreach (BinaryPatchSpec spec in specs)
                ctx.Line($"{Truncate(spec.Key, 30),-30} {Truncate(spec.Track, 14),-14} {Truncate(spec.ProofLevel ?? "-", 12),-12} {spec.DisplayName}");

            ctx.Line();
            ctx.Line("Profiles:");
            foreach (SafeCopyProfilePreset preset in presets)
                ctx.Line($"  {preset.Id,-28} {(preset.IsSelectable ? "" : "(not selectable) ")}{preset.DisplayName} [{preset.PatchKeys.Count} keys]");

            return CliExit.Success;
        }

        /// <summary>
        /// Copy a BEA.exe into a fresh app-owned Patch Bench workspace, so there is something to patch
        /// that is not the installed game. Both the source check and the destination check are AppCore's
        /// own, so this cannot stage from or to somewhere the GUI would refuse.
        /// </summary>
        public static int PatchStage(CliContext ctx, string? sourceExe)
        {
            const string command = "patch.stage";
            if (string.IsNullOrWhiteSpace(sourceExe))
                return ctx.Usage(command, "A source BEA.exe (or BEA.exe.original.backup) path is required.");

            string validatedSource;
            try
            {
                validatedSource = GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy(sourceExe);
            }
            catch (Exception ex) when (ex is InvalidOperationException or FileNotFoundException or IOException or UnauthorizedAccessException)
            {
                return ctx.Usage(command, ex.Message);
            }

            string root = PatchBenchRoot;
            string workspaceId = $"{DateTime.UtcNow:yyyyMMdd-HHmmss-fff}-{Guid.NewGuid().ToString("N")[..8]}";
            string destination = Path.Combine(root, workspaceId, "BEA.exe");

            string validatedDestination;
            try
            {
                validatedDestination = GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination(
                    destination, root, "BEA.exe");
                Directory.CreateDirectory(Path.GetDirectoryName(validatedDestination)!);
                File.Copy(validatedSource, validatedDestination, overwrite: false);
            }
            catch (Exception ex) when (ex is InvalidOperationException or IOException or UnauthorizedAccessException)
            {
                return ctx.Usage(command, ex.Message);
            }

            return ctx.Ok(command, new
            {
                workspaceId,
                source = validatedSource,
                target = validatedDestination,
                allowedRoot = root,
            }, $"Staged patch target: {validatedDestination}");
        }

        public static int PatchPlan(CliContext ctx, string? target, string? profileId, IReadOnlyList<string>? patchKeys)
        {
            const string command = "patch.plan";
            if (!TryResolvePatchTarget(ctx, command, target, out string exePath, out int failure))
                return failure;

            if (!TryResolveSelection(ctx, command, profileId, patchKeys, out IReadOnlyList<BinaryPatchSpec> selected, out failure))
                return failure;

            // A plan never opens the file for writing and never touches the backup; it reports what apply
            // would do and what the bytes look like right now.
            BinaryPatchTargetVerifyResult verify = BinaryPatchEngine.VerifyPatchTargetFile(
                BuildTargetOptions(exePath), selected);

            object payload = new
            {
                target = exePath,
                allowedRoot = PatchBenchRoot,
                backupPath = BinaryPatchEngine.BuildBackupPath(exePath),
                backupExists = File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)),
                identityLabel = verify.IdentityLabel,
                verifyPasses = verify.Success,
                message = verify.Message,
                selection = selected.Select(spec => new
                {
                    key = spec.Key,
                    track = spec.Track,
                    displayName = spec.DisplayName,
                    currentState = verify.Rows.FirstOrDefault(row => row.Spec.Key == spec.Key) is { } row
                        ? BinaryPatchEngine.StateLabel(row.State)
                        : "Unknown",
                    regions = BinaryPatchEngine.GetPatchRegions(spec).Select(region => new
                    {
                        fileOffset = region.FileOffset,
                        byteCount = region.Original.Length,
                        original = Convert.ToHexString(region.Original),
                        patched = Convert.ToHexString(region.Patched),
                    }).ToArray(),
                }).ToArray(),
            };

            if (!ctx.Json)
            {
                ctx.Line($"Target: {exePath}");
                ctx.Line($"Identity: {verify.IdentityLabel ?? "(unknown)"}");
                ctx.Line($"Verify would {(verify.Success ? "pass" : "FAIL")}: {verify.Message}");
                ctx.Line();
                foreach (BinaryPatchSpec spec in selected)
                {
                    BinaryPatchVerifyRow? row = verify.Rows.FirstOrDefault(candidate => candidate.Spec.Key == spec.Key);
                    string state = row is null ? "Unknown" : BinaryPatchEngine.StateLabel(row.State);
                    ctx.Line($"  {spec.Key,-30} {state,-12} @ 0x{spec.FileOffset:X}  {spec.DisplayName}");
                }
            }

            return ctx.Ok(command, payload);
        }

        public static int PatchVerify(CliContext ctx, string? target, string? profileId, IReadOnlyList<string>? patchKeys)
        {
            const string command = "patch.verify";
            if (!TryResolvePatchTarget(ctx, command, target, out string exePath, out int failure))
                return failure;

            if (!TryResolveSelection(ctx, command, profileId, patchKeys, out IReadOnlyList<BinaryPatchSpec> selected, out failure))
                return failure;

            BinaryPatchTargetVerifyResult verify = BinaryPatchEngine.VerifyPatchTargetFile(
                BuildTargetOptions(exePath), selected);

            object payload = BuildVerifyPayload(exePath, verify);

            if (!ctx.Json)
                ctx.Line(BinaryPatchEngine.RenderStateReport(exePath, verify.Rows.ToList(), verify.Message));

            // The engine ran and reported on the bytes; a failed verification is the answer.
            return verify.Success ? ctx.Ok(command, payload) : ctx.Verdict(command, verify.Message, payload);
        }

        /// <summary>
        /// Apply a selection, after verifying it. The verify-before-apply order mirrors the GUI, which
        /// will not enable Apply until a verification of that exact selection against that exact file has
        /// passed - applying to bytes nobody has looked at is how a half-patched executable gets made.
        /// </summary>
        public static int PatchApply(CliContext ctx, string? target, string? profileId, IReadOnlyList<string>? patchKeys)
        {
            const string command = "patch.apply";
            if (!TryResolvePatchTarget(ctx, command, target, out string exePath, out int failure))
                return failure;

            if (!TryResolveSelection(ctx, command, profileId, patchKeys, out IReadOnlyList<BinaryPatchSpec> selected, out failure))
                return failure;

            BinaryPatchTargetOptions options = BuildTargetOptions(exePath);
            BinaryPatchTargetVerifyResult verify = BinaryPatchEngine.VerifyPatchTargetFile(options, selected);
            if (!verify.Success)
            {
                return ctx.Verdict(
                    command,
                    $"Refusing to apply: verification did not pass. {verify.Message}",
                    BuildVerifyPayload(exePath, verify));
            }

            (bool success, string message) = BinaryPatchEngine.ApplyPatchesToFile(options, selected);
            object payload = new
            {
                target = exePath,
                allowedRoot = PatchBenchRoot,
                backupPath = BinaryPatchEngine.BuildBackupPath(exePath),
                identityLabel = verify.IdentityLabel,
                applied = success,
                message,
                selection = selected.Select(spec => spec.Key).ToArray(),
            };

            if (!ctx.Json)
                ctx.Line(message);

            return success ? ctx.Ok(command, payload) : ctx.Verdict(command, message, payload);
        }

        public static int PatchRestore(CliContext ctx, string? target)
        {
            const string command = "patch.restore";
            if (!TryResolvePatchTarget(ctx, command, target, out string exePath, out int failure))
                return failure;

            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            if (!File.Exists(backupPath))
                return ctx.Usage(command, $"Backup file not found: {backupPath}");

            (bool success, string message) = BinaryPatchEngine.RestoreFromBackup(BuildTargetOptions(exePath));
            object payload = new
            {
                target = exePath,
                backupPath,
                restored = success,
                message,
            };

            if (!ctx.Json)
                ctx.Line(message);

            return success ? ctx.Ok(command, payload) : ctx.Verdict(command, message, payload);
        }

        // ================================================================ helpers

        private static BinaryPatchTargetOptions BuildTargetOptions(string exePath) =>
            new(ExePath: exePath, AllowedRoot: PatchBenchRoot, AllowByteLayoutOnlyTarget: false);

        private static object BuildVerifyPayload(string exePath, BinaryPatchTargetVerifyResult verify) => new
        {
            target = exePath,
            allowedRoot = PatchBenchRoot,
            success = verify.Success,
            message = verify.Message,
            identityLabel = verify.IdentityLabel,
            rows = verify.Rows.Select(row => new
            {
                key = row.Spec.Key,
                track = row.Spec.Track,
                displayName = row.Spec.DisplayName,
                fileOffset = row.Spec.FileOffset,
                state = BinaryPatchEngine.StateLabel(row.State),
                stateCode = row.State.ToString(),
            }).ToArray(),
        };

        /// <summary>
        /// Accepts a safe-copy id (folder name) or a path. Anything that does not land strictly under the
        /// app-owned root is refused here, before any AppCore call.
        /// </summary>
        private static bool TryResolveProfileRoot(
            CliContext ctx,
            string command,
            string? id,
            out string profileRoot,
            out int exitCode,
            bool requireManifest = true)
        {
            profileRoot = string.Empty;
            exitCode = CliExit.Success;

            if (string.IsNullOrWhiteSpace(id))
            {
                exitCode = ctx.Usage(command, "A safe copy id (folder name) or path is required. List them with 'copy list'.");
                return false;
            }

            string root = SafeCopyRoot;
            string candidate = id.Contains(Path.DirectorySeparatorChar) || id.Contains(Path.AltDirectorySeparatorChar) || Path.IsPathRooted(id)
                ? id
                : Path.Combine(root, id);

            string resolved;
            string resolvedRoot;
            try
            {
                resolved = Path.GetFullPath(candidate).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                resolvedRoot = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            }
            catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
            {
                exitCode = ctx.Usage(command, $"Path could not be normalized: {ex.Message}");
                return false;
            }

            bool strictlyUnderRoot =
                !string.Equals(resolved, resolvedRoot, StringComparison.OrdinalIgnoreCase) &&
                (resolved + Path.DirectorySeparatorChar).StartsWith(resolvedRoot + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase);

            if (!strictlyUnderRoot)
            {
                exitCode = ctx.Usage(
                    command,
                    "Refusing to operate on a folder outside the app-owned safe copy root.",
                    $"Root: {resolvedRoot}",
                    $"Given: {resolved}");
                return false;
            }

            if (!Directory.Exists(resolved))
            {
                exitCode = ctx.Usage(command, $"Safe copy not found: {resolved}");
                return false;
            }

            if (requireManifest &&
                !File.Exists(Path.Combine(resolved, GameProfilePreflightService.ProfileManifestFileName)))
            {
                exitCode = ctx.Usage(
                    command,
                    "That folder is not an app-generated safe copy (no generated manifest).",
                    $"Expected: {Path.Combine(resolved, GameProfilePreflightService.ProfileManifestFileName)}");
                return false;
            }

            profileRoot = resolved;
            return true;
        }

        private static bool TryResolvePatchTarget(
            CliContext ctx,
            string command,
            string? target,
            out string exePath,
            out int exitCode)
        {
            exePath = string.Empty;
            exitCode = CliExit.Success;

            if (string.IsNullOrWhiteSpace(target))
            {
                exitCode = ctx.Usage(
                    command,
                    "A patch target is required: a Patch Bench workspace id, a workspace folder, or a path to BEA.exe.",
                    "Create one with: patch stage <path-to-BEA.exe>");
                return false;
            }

            string candidate = target.Trim();
            string resolved;
            try
            {
                if (!candidate.Contains(Path.DirectorySeparatorChar) &&
                    !candidate.Contains(Path.AltDirectorySeparatorChar) &&
                    !Path.IsPathRooted(candidate))
                {
                    resolved = Path.Combine(PatchBenchRoot, candidate, "BEA.exe");
                }
                else
                {
                    resolved = Path.GetFullPath(candidate);
                    if (Directory.Exists(resolved))
                        resolved = Path.Combine(resolved, "BEA.exe");
                }

                resolved = Path.GetFullPath(resolved);
            }
            catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
            {
                exitCode = ctx.Usage(command, $"Patch target path could not be normalized: {ex.Message}");
                return false;
            }

            // Containment is checked here, before the engine, so that pointing at the installed game is
            // reported as what it is - a refusal to attempt the operation, exit 1 - rather than surfacing
            // later as a failed verification, which would read as a verdict about the bytes. The engine
            // refuses the same thing independently; this is the outer of two gates, not the only one.
            string benchRoot;
            try
            {
                benchRoot = Path.GetFullPath(PatchBenchRoot).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            }
            catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
            {
                exitCode = ctx.Usage(command, $"Patch Bench root could not be normalized: {ex.Message}");
                return false;
            }

            if (!(resolved + Path.DirectorySeparatorChar)
                    .StartsWith(benchRoot + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            {
                exitCode = ctx.Usage(
                    command,
                    "These patch verbs only work inside the app-owned Patch Bench workspace.",
                    $"Patch Bench root: {benchRoot}",
                    $"Given: {resolved}",
                    "Stage a working copy first: patch stage <path-to-BEA.exe>",
                    "Or work on the game you installed, backup first: patch install apply");
                return false;
            }

            if (!File.Exists(resolved))
            {
                exitCode = ctx.Usage(command, $"Patch target not found: {resolved}");
                return false;
            }

            exePath = resolved;
            return true;
        }

        // ================================================== patch install (the real game)

        /// <summary>
        /// The installed game, and what the app would be able to put back.
        ///
        /// Read-only. It exists so nobody has to find out what state their install is in by
        /// running the thing that changes it.
        /// </summary>
        public static int PatchInstallStatus(CliContext ctx, string? exePath)
        {
            const string command = "patch.install.status";
            if (!TryResolveInstalledExecutable(ctx, command, exePath, out string resolved, out int failure))
                return failure;

            string backupPath = BinaryPatchEngine.BuildBackupPath(resolved);
            string backupHashPath = BinaryPatchEngine.BuildBackupHashPath(resolved);
            bool hasBackup = File.Exists(backupPath);
            bool hasSidecar = File.Exists(backupHashPath);

            BinaryPatchTargetVerifyResult verify = BinaryPatchEngine.VerifyPatchTargetFile(
                new BinaryPatchTargetOptions(resolved, AllowedRoot: Path.GetDirectoryName(resolved) ?? string.Empty),
                BinaryPatchEngine.PatchSpecs);

            var payload = new
            {
                exePath = resolved,
                backupPath,
                backupHashPath,
                hasBackup,
                hasHashSidecar = hasSidecar,
                canBeRestored = hasBackup && hasSidecar,
                identity = verify.IdentityLabel,
            };

            if (ctx.Json)
                return ctx.Ok(command, payload);

            ctx.Line($"Installed game: {resolved}");
            ctx.Line($"Original backup: {(hasBackup ? backupPath : "none")}");
            ctx.Line($"Recorded hash:   {(hasSidecar ? backupHashPath : "none")}");
            ctx.Line();
            ctx.Line(hasBackup && hasSidecar
                ? "This install can be put back the way it was."
                : hasBackup
                    ? "There is a backup but no recorded hash. 'patch install backup' will write one if the backup is a clean retail BEA.exe."
                    : "There is no backup yet. 'patch install backup' will make one if the executable is still a clean retail BEA.exe.");
            return CliExit.Success;
        }

        /// <summary>
        /// Make sure there is something to go back to, and say what happened. Never touches the
        /// executable itself.
        /// </summary>
        public static int PatchInstallBackup(CliContext ctx, string? exePath)
        {
            const string command = "patch.install.backup";
            if (!TryResolveInstalledExecutable(ctx, command, exePath, out string resolved, out int failure))
                return failure;

            var (success, message, authorization) = BinaryPatchEngine.AuthorizeInstalledGameWrite(resolved);
            if (!success || authorization is null)
                return ctx.Usage(command, message);

            return ctx.Ok(command, DescribeAuthorization(authorization), message);
        }

        /// <summary>
        /// Patch the installed game, after making and verifying the backup.
        ///
        /// The backup is not a flag here. <c>AuthorizeInstalledGameWrite</c> is what produces the
        /// permission the engine requires, and it will not produce one until a verified original is
        /// beside the executable - so there is no ordering of these lines that writes first.
        /// </summary>
        public static int PatchInstallApply(
            CliContext ctx,
            string? exePath,
            string? profileId,
            IReadOnlyList<string>? patchKeys,
            bool confirmed)
        {
            const string command = "patch.install.apply";
            if (!TryResolveInstalledExecutable(ctx, command, exePath, out string resolved, out int failure))
                return failure;

            if (!confirmed)
            {
                return ctx.Usage(
                    command,
                    "This changes the game you have installed, not a copy. Pass --yes once you mean it.",
                    $"Target: {resolved}",
                    "A verified backup is made first, and 'patch install restore' puts it back.",
                    "Prefer a sandbox? copy create");
            }

            if (!TryResolveSelection(ctx, command, profileId, patchKeys, out var selected, out failure))
                return failure;

            var (authorized, authorizationMessage, authorization) =
                BinaryPatchEngine.AuthorizeInstalledGameWrite(resolved);
            if (!authorized || authorization is null)
                return ctx.Usage(command, authorizationMessage);

            var target = new BinaryPatchTargetOptions(
                resolved,
                AllowedRoot: string.Empty,
                InstalledGame: authorization);

            BinaryPatchTargetVerifyResult verify = BinaryPatchEngine.VerifyPatchTargetFile(target, selected);
            if (!verify.Success)
            {
                return ctx.Usage(
                    command,
                    $"Refusing to apply: verification did not pass. {verify.Message}",
                    "Your game was not changed.");
            }

            var (applied, applyMessage) = BinaryPatchEngine.ApplyPatchesToFile(target, selected);
            if (!applied)
                return ctx.Usage(command, applyMessage);

            return ctx.Ok(
                command,
                new
                {
                    exePath = resolved,
                    backupPath = authorization.BackupPath,
                    backupSha256 = authorization.BackupSha256,
                    backupCreatedNow = authorization.BackupWasCreatedNow,
                    patchKeys = selected.Select(spec => spec.Key).ToArray(),
                },
                $"{authorizationMessage}\n{applyMessage}");
        }

        /// <summary>Put the installed game back from its verified original.</summary>
        public static int PatchInstallRestore(CliContext ctx, string? exePath)
        {
            const string command = "patch.install.restore";
            if (!TryResolveInstalledExecutable(ctx, command, exePath, out string resolved, out int failure))
                return failure;

            if (!File.Exists(BinaryPatchEngine.BuildBackupPath(resolved)))
            {
                return ctx.Usage(
                    command,
                    "There is no BEA.exe.original.backup beside that game, so there is nothing to put back.",
                    $"Target: {resolved}");
            }

            var (authorized, authorizationMessage, authorization) =
                BinaryPatchEngine.AuthorizeInstalledGameWrite(resolved);
            if (!authorized || authorization is null)
                return ctx.Usage(command, authorizationMessage);

            var (success, message) = BinaryPatchEngine.RestoreFromBackup(new BinaryPatchTargetOptions(
                resolved,
                AllowedRoot: string.Empty,
                InstalledGame: authorization));

            return success
                ? ctx.Ok(command, DescribeAuthorization(authorization), message)
                : ctx.Usage(command, message);
        }

        private static object DescribeAuthorization(InstalledGameWriteAuthorization authorization) => new
        {
            exePath = authorization.ExePath,
            gameRoot = authorization.GameRoot,
            backupPath = authorization.BackupPath,
            backupHashPath = authorization.BackupHashPath,
            backupSha256 = authorization.BackupSha256,
            backupCreatedNow = authorization.BackupWasCreatedNow,
            hashSidecarCreatedNow = authorization.HashSidecarWasCreatedNow,
        };

        /// <summary>
        /// The BEA.exe of the installed game - the one given, or the configured/detected install.
        ///
        /// Unlike <see cref="TryResolvePatchTarget"/> this deliberately does NOT confine the path to
        /// the app-owned workspace. That is the whole point of this verb group, and the engine still
        /// refuses everything else: the file has to be named BEA.exe, it has to sit beside a data
        /// folder, and nothing is written until a verified original exists.
        /// </summary>
        private static bool TryResolveInstalledExecutable(
            CliContext ctx,
            string command,
            string? exePath,
            out string resolved,
            out int exitCode)
        {
            resolved = string.Empty;
            exitCode = CliExit.Success;

            string? candidate = exePath?.Trim();
            if (string.IsNullOrWhiteSpace(candidate))
            {
                string? gameDir = AppConfig.Load().GetGameDir() ?? AppConfig.DetectGameDirectory();
                if (string.IsNullOrWhiteSpace(gameDir))
                {
                    exitCode = ctx.Usage(
                        command,
                        "No installed game folder is configured and none was found.",
                        "Give the path: patch install status <path-to-BEA.exe>");
                    return false;
                }

                candidate = Path.Combine(gameDir, "BEA.exe");
            }

            try
            {
                resolved = Path.GetFullPath(candidate);
                if (Directory.Exists(resolved))
                    resolved = Path.Combine(resolved, "BEA.exe");

                resolved = Path.GetFullPath(resolved);
            }
            catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
            {
                exitCode = ctx.Usage(command, $"Path could not be normalized: {ex.Message}");
                return false;
            }

            if (!File.Exists(resolved))
            {
                exitCode = ctx.Usage(command, $"No BEA.exe there: {resolved}");
                return false;
            }

            return true;
        }

        /// <summary>
        /// Resolve a patch selection from a profile id, explicit keys, or - when neither is given - the
        /// compatibility baseline the GUI always forces on. The default is stated out loud rather than
        /// applied silently, because "which patches did that actually touch" must never be a guess.
        /// </summary>
        private static bool TryResolveSelection(
            CliContext ctx,
            string command,
            string? profileId,
            IReadOnlyList<string>? patchKeys,
            out IReadOnlyList<BinaryPatchSpec> selected,
            out int exitCode)
        {
            selected = Array.Empty<BinaryPatchSpec>();
            exitCode = CliExit.Success;

            var keys = new List<string>();
            if (!string.IsNullOrWhiteSpace(profileId))
            {
                try
                {
                    keys.AddRange(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(profileId));
                }
                catch (Exception ex) when (ex is InvalidOperationException or KeyNotFoundException or ArgumentException)
                {
                    exitCode = ctx.Usage(command, $"Unknown patch profile '{profileId}'. List them with 'patch list'.");
                    return false;
                }
            }

            if (patchKeys is { Count: > 0 })
                keys.AddRange(patchKeys);

            if (keys.Count == 0)
            {
                keys.AddRange(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(
                    BinaryPatchPlanBuilder.CompatibilityProfileId));
                ctx.Warn(
                    $"No selection given; defaulting to the '{BinaryPatchPlanBuilder.CompatibilityProfileId}' " +
                    $"profile ({string.Join(", ", keys)}).");
            }

            string[] distinct = keys.Distinct(StringComparer.OrdinalIgnoreCase).ToArray();
            string? selectionError = BinaryPatchPlanBuilder.ValidateVisibleSelection(distinct);
            if (!string.IsNullOrWhiteSpace(selectionError))
            {
                exitCode = ctx.Usage(command, selectionError);
                return false;
            }

            try
            {
                selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(distinct);
            }
            catch (Exception ex) when (ex is InvalidOperationException or KeyNotFoundException or ArgumentException)
            {
                exitCode = ctx.Usage(command, ex.Message);
                return false;
            }

            (bool policyOk, string policyMessage) = BinaryPatchEngine.ValidatePatchSelectionPolicy(selected);
            if (!policyOk)
            {
                exitCode = ctx.Usage(command, policyMessage);
                return false;
            }

            return true;
        }

        private sealed record ManifestSummary(
            string? SchemaVersion,
            DateTimeOffset? GeneratedAt,
            string? PresetId,
            string? PresetDisplayName,
            string[] PatchKeys,
            string[] LaunchArguments,
            int EntryCount);

        private static ManifestSummary ReadManifestSummary(string manifestPath)
        {
            var empty = new ManifestSummary(null, null, null, null, Array.Empty<string>(), Array.Empty<string>(), 0);
            if (!File.Exists(manifestPath))
                return empty;

            try
            {
                using JsonDocument document = JsonDocument.Parse(File.ReadAllText(manifestPath));
                JsonElement root = document.RootElement;

                string? schemaVersion = root.TryGetProperty("schemaVersion", out JsonElement schema) ? schema.GetString() : null;
                DateTimeOffset? generatedAt = root.TryGetProperty("generatedAt", out JsonElement generated) &&
                                              generated.ValueKind == JsonValueKind.String &&
                                              DateTimeOffset.TryParse(generated.GetString(), out DateTimeOffset parsed)
                    ? parsed
                    : null;

                string? presetId = null;
                string? presetDisplayName = null;
                if (root.TryGetProperty("profilePreset", out JsonElement preset) && preset.ValueKind == JsonValueKind.Object)
                {
                    presetId = preset.TryGetProperty("id", out JsonElement presetIdEl) ? presetIdEl.GetString() : null;
                    presetDisplayName = preset.TryGetProperty("displayName", out JsonElement nameEl) ? nameEl.GetString() : null;
                }

                string[] patchKeys = Array.Empty<string>();
                if (root.TryGetProperty("patchResult", out JsonElement patchResult) &&
                    patchResult.ValueKind == JsonValueKind.Object &&
                    patchResult.TryGetProperty("patchKeys", out JsonElement keysEl) &&
                    keysEl.ValueKind == JsonValueKind.Array)
                {
                    patchKeys = keysEl.EnumerateArray()
                        .Where(item => item.ValueKind == JsonValueKind.String)
                        .Select(item => item.GetString()!)
                        .ToArray();
                }

                string[] launchArguments = Array.Empty<string>();
                if (root.TryGetProperty("launchPlan", out JsonElement launchPlan) &&
                    launchPlan.ValueKind == JsonValueKind.Object &&
                    launchPlan.TryGetProperty("arguments", out JsonElement argsEl) &&
                    argsEl.ValueKind == JsonValueKind.Array)
                {
                    launchArguments = argsEl.EnumerateArray()
                        .Where(item => item.ValueKind == JsonValueKind.String)
                        .Select(item => item.GetString()!)
                        .ToArray();
                }

                int entryCount = root.TryGetProperty("entries", out JsonElement entries) && entries.ValueKind == JsonValueKind.Array
                    ? entries.GetArrayLength()
                    : 0;

                return new ManifestSummary(schemaVersion, generatedAt, presetId, presetDisplayName, patchKeys, launchArguments, entryCount);
            }
            catch (Exception ex) when (ex is JsonException or IOException or UnauthorizedAccessException)
            {
                return empty;
            }
        }

        private static string Truncate(string value, int max) =>
            value.Length <= max ? value : value[..Math.Max(0, max - 1)] + "~";
    }
}
