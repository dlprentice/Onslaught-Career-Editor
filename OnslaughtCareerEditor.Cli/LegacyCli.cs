using System;
using System.Collections.Generic;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor.Cli
{
    /// <summary>
    /// The original flag-style invocation: <c>onslaught-career-editor &lt;input&gt; [output] [flags]</c>.
    ///
    /// This is kept whole rather than rewritten as a shim over the new verbs. The old form is a single
    /// combined write - career sections, CCareer settings, and options entries in one pass over one file
    /// - and no single new verb models that, because <c>SavePatchRequest</c> carries career payloads only.
    /// Re-expressing it as a sequence of verb calls would change what is written and when, which is
    /// exactly the kind of silent behaviour change that is not worth the tidiness.
    ///
    /// What it does share with the new verbs is every read path (analyze, compare, goodie list, config)
    /// and the career option resolver, so the two forms cannot disagree about what a flag means.
    /// </summary>
    public static class LegacyCli
    {
        /// <summary>
        /// The context is built per invocation rather than passed in, because whether this run speaks
        /// JSON is only known after <c>--json</c> has been parsed.
        /// </summary>
        public static RootCommand Build(Func<bool, CliContext> contextFactory)
        {
            var inputArg = new Argument<FileInfo?>("input", () => null, "Input .bes/.bea file");
            var outputArg = new Argument<FileInfo?>("output", () => null, "Output .bes/.bea file (required for patching)");

            var jsonOption = new Option<bool>("--json", "Emit a machine-readable JSON envelope on stdout.");
            var analyzeOption = new Option<bool>("--analyze", "Analyze the input file without patching");
            var verboseOption = new Option<bool>(new[] { "--verbose", "-v" }, "Verbose output (hex dumps in analyze mode)");
            var dumpMysteryOption = new Option<bool>("--dump-mystery", "Show hex dump of reserved/unmapped byte regions (use with --analyze)");
            var compareOption = new Option<FileInfo?>("--compare", "Compare input with another .bes/.bea file");
            var listGoodiesOption = new Option<bool>("--list-goodies", "List per-slot goodie states (read-only; requires input file).");
            var showReservedGoodiesOption = new Option<bool>("--show-reserved-goodies", "With --list-goodies: include reserved slots (233-299).");
            var setGoodieStateOption = new Option<string[]>("--set-goodie-state",
                "Targeted Goodie state override for copied-save proof setup (format: INDEX:STATE; state 0/1/2/3 or locked/instructions/new/old).")
            { AllowMultipleArgumentsPerToken = true };

            var newOption = new Option<bool>("--new", "Mark goodies as NEW (gold) instead of OLD (blue)");
            var killsOption = new Option<int?>("--kills", "Global kill count for all categories (default: 100)");
            var rankOption = new Option<string?>("--rank",
                "Rank written to every completed mission: S, A, B, C, D, E, or NONE. Omit it alongside --level-rank to change only the listed missions. Defaults to S when mission patching is on and no --level-rank was given.");
            var killsOnlyOption = new Option<bool>("--kills-only", "Only patch kill counts (preserve nodes, links, goodies)");
            var noNodesOption = new Option<bool>("--no-nodes", "Skip patching mission nodes");
            var noLinksOption = new Option<bool>("--no-links", "Skip patching mission links");
            var noGoodiesOption = new Option<bool>("--no-goodies", "Skip patching goodies");
            var noKillsOption = new Option<bool>("--no-kills", "Skip patching kill counts");
            var allowCareerSectionsOnOptionsFileOption = new Option<bool>("--allow-career-sections-on-options-file",
                "Allow patching career sections when input/output is .bea/defaultoptions.bea (advanced; off by default).");
            var levelRankOption = new Option<string[]>("--level-rank",
                "Per-level rank override (format: NODE_INDEX:GRADE, repeatable; node index 1-43). Sets only the listed missions; every other mission keeps its current grade unless --rank is also supplied.")
            { AllowMultipleArgumentsPerToken = true };

            var aircraftKillsOption = new Option<int?>("--aircraft-kills", "Override aircraft kill count (thresholds: 25/50/75/100). Sets only this category; the other four keep their current counts unless --kills is also supplied.");
            var vehicleKillsOption = new Option<int?>("--vehicle-kills", "Override vehicle kill count (thresholds: 100/200/300/400). Sets only this category; the other four keep their current counts unless --kills is also supplied.");
            var emplacementKillsOption = new Option<int?>("--emplacement-kills", "Override emplacement kill count (thresholds: 25/50; 75 appears only in combined unlocks). Sets only this category; the other four keep their current counts unless --kills is also supplied.");
            var infantryKillsOption = new Option<int?>("--infantry-kills", "Override infantry kill count (thresholds: 40/80/160). Sets only this category; the other four keep their current counts unless --kills is also supplied.");
            var mechKillsOption = new Option<int?>("--mech-kills", "Override mech kill count (thresholds: 20/40/80; 40 unlocks two goodies). Sets only this category; the other four keep their current counts unless --kills is also supplied.");

            var soundVolumeOption = new Option<double?>("--sound-volume", "Override sound volume (0.0-1.0). Omit to preserve.");
            var musicVolumeOption = new Option<double?>("--music-volume", "Override music volume (0.0-1.0). Omit to preserve.");
            var invertWalkerP1Option = new Option<string?>(new[] { "--invert-walker-p1", "--invert-y-p1" }, "Override invert-Y (Walker mode) for player 1: on/off/true/false/1/0 (omit to preserve).");
            var invertWalkerP2Option = new Option<string?>(new[] { "--invert-walker-p2", "--invert-y-p2" }, "Override invert-Y (Walker mode) for player 2: on/off/true/false/1/0 (omit to preserve).");
            var invertFlightP1Option = new Option<string?>("--invert-flight-p1", "Override invert-Y (Flight/Jet mode) for player 1: on/off/true/false/1/0 (omit to preserve).");
            var invertFlightP2Option = new Option<string?>("--invert-flight-p2", "Override invert-Y (Flight/Jet mode) for player 2: on/off/true/false/1/0 (omit to preserve).");
            var vibrationP1Option = new Option<string?>("--vibration-p1", "Override controller vibration for player 1: on/off/true/false/1/0 (omit to preserve).");
            var vibrationP2Option = new Option<string?>("--vibration-p2", "Override controller vibration for player 2: on/off/true/false/1/0 (omit to preserve).");
            var controllerConfigP1Option = new Option<uint?>("--controller-config-p1", "Override controller configuration index for player 1 (omit to preserve).");
            var controllerConfigP2Option = new Option<uint?>("--controller-config-p2", "Override controller configuration index for player 2 (omit to preserve).");
            var experimentalPendingExtraGoodiesOption = new Option<int?>("--experimental-pending-extra-goodies",
                "Experimental only: pending-extra-goodies override (currently ignored on retail Steam until persistence is re-verified).");

            var copyOptionsFromOption = new Option<FileInfo?>("--copy-options-from", "Copy the options entries + tail snapshot from another .bes/.bea file (same size/layout).");
            var noCopyOptionsEntriesOption = new Option<bool>("--no-copy-options-entries", "With --copy-options-from: do not copy the options entries region (`0x20*N`, typically `0x200` in Steam saves).");
            var noCopyOptionsTailOption = new Option<bool>("--no-copy-options-tail", "With --copy-options-from: do not copy the fixed 0x56-byte options tail snapshot (globals).");

            Option<string[]> Bind(string name, string description) =>
                new(name, description) { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };

            var bindMoveForwardOption = Bind("--bind-move-forward", "Override Movement: Forward bindings (P1 P2).");
            var bindMoveBackwardOption = Bind("--bind-move-backward", "Override Movement: Backward bindings (P1 P2).");
            var bindMoveLeftOption = Bind("--bind-move-left", "Override Movement: Left bindings (P1 P2).");
            var bindMoveRightOption = Bind("--bind-move-right", "Override Movement: Right bindings (P1 P2).");
            var bindLookUpOption = Bind("--bind-look-up", "Override Look: Up bindings (P1 P2). Use Mouse / MouseX+ / MouseY- to bind to mouse axis.");
            var bindLookDownOption = Bind("--bind-look-down", "Override Look: Down bindings (P1 P2). Use Mouse / MouseX+ / MouseY- to bind to mouse axis.");
            var bindLookLeftOption = Bind("--bind-look-left", "Override Look: Left bindings (P1 P2). Use Mouse / MouseX+ / MouseY- to bind to mouse axis.");
            var bindLookRightOption = Bind("--bind-look-right", "Override Look: Right bindings (P1 P2). Use Mouse / MouseX+ / MouseY- to bind to mouse axis.");
            var bindZoomInOption = Bind("--bind-zoom-in", "Override Zoom: In bindings (P1 P2). Use MouseWheelUp/MouseWheelDown for wheel.");
            var bindZoomOutOption = Bind("--bind-zoom-out", "Override Zoom: Out bindings (P1 P2). Use MouseWheelUp/MouseWheelDown for wheel.");
            var bindFireWeaponOption = Bind("--bind-fire-weapon", "Override Others: Fire weapon bindings (P1 P2). Use MouseLeft to bind to LMB.");
            var bindSelectWeaponOption = Bind("--bind-select-weapon", "Override Others: Select weapon bindings (P1 P2). Use MouseRight to bind to RMB.");
            var bindTransformOption = Bind("--bind-transform", "Override Others: Transform bindings (P1 P2).");
            var bindAirBrakeOption = Bind("--bind-air-brake", "Override Others: Air brake bindings (P1 P2).");
            var bindSpecialOption = Bind("--bind-special", "Override Others: Special function bindings (P1 P2).");

            var listSavesOption = new Option<bool>("--list-saves", "List save files found in the game directory");
            var setGameDirOption = new Option<string?>("--set-game-dir", "Set the game directory path for save file discovery");
            var showConfigOption = new Option<bool>("--show-config", "Show current configuration");

            var rootCommand = new RootCommand("Onslaught Toolkit - legacy flag-style save/options editor")
            {
                inputArg, outputArg,
                jsonOption, analyzeOption, verboseOption, dumpMysteryOption, compareOption,
                listGoodiesOption, showReservedGoodiesOption, setGoodieStateOption,
                newOption, killsOption, rankOption, killsOnlyOption,
                noNodesOption, noLinksOption, noGoodiesOption, noKillsOption,
                allowCareerSectionsOnOptionsFileOption, levelRankOption,
                aircraftKillsOption, vehicleKillsOption, emplacementKillsOption, infantryKillsOption, mechKillsOption,
                soundVolumeOption, musicVolumeOption,
                invertWalkerP1Option, invertWalkerP2Option, invertFlightP1Option, invertFlightP2Option,
                vibrationP1Option, vibrationP2Option, controllerConfigP1Option, controllerConfigP2Option,
                experimentalPendingExtraGoodiesOption,
                copyOptionsFromOption, noCopyOptionsEntriesOption, noCopyOptionsTailOption,
                bindMoveForwardOption, bindMoveBackwardOption, bindMoveLeftOption, bindMoveRightOption,
                bindLookUpOption, bindLookDownOption, bindLookLeftOption, bindLookRightOption,
                bindZoomInOption, bindZoomOutOption,
                bindFireWeaponOption, bindSelectWeaponOption, bindTransformOption, bindAirBrakeOption, bindSpecialOption,
                listSavesOption, setGameDirOption, showConfigOption,
            };
            rootCommand.Name = Program.AppCliName;

            rootCommand.SetHandler((InvocationContext invocation) =>
            {
                CliContext ctx = contextFactory(invocation.ParseResult.GetValueForOption(jsonOption));

                FileInfo? input = invocation.ParseResult.GetValueForArgument(inputArg);
                FileInfo? output = invocation.ParseResult.GetValueForArgument(outputArg);
                bool listSaves = invocation.ParseResult.GetValueForOption(listSavesOption);
                string? setGameDir = invocation.ParseResult.GetValueForOption(setGameDirOption);
                bool showConfig = invocation.ParseResult.GetValueForOption(showConfigOption);

                // Config commands short-circuit: they never need an input file.
                if (listSaves || setGameDir is not null || showConfig)
                {
                    int configExit = CliExit.Success;
                    if (setGameDir is not null)
                    {
                        configExit = SaveVerbs.ConfigSetGameDir(ctx, setGameDir);
                        if (configExit != CliExit.Success)
                        {
                            invocation.ExitCode = configExit;
                            return;
                        }
                    }

                    if (showConfig)
                        configExit = SaveVerbs.ConfigShow(ctx);

                    if (listSaves)
                        configExit = SaveVerbs.SavesList(ctx);

                    invocation.ExitCode = configExit;
                    return;
                }

                var bindings = new Dictionary<string, string[]>(StringComparer.OrdinalIgnoreCase);
                void Collect(string name, Option<string[]> option)
                {
                    string[]? value = invocation.ParseResult.GetValueForOption(option);
                    if (value is { Length: 2 })
                        bindings[name] = value;
                }

                Collect("move-forward", bindMoveForwardOption);
                Collect("move-backward", bindMoveBackwardOption);
                Collect("move-left", bindMoveLeftOption);
                Collect("move-right", bindMoveRightOption);
                Collect("look-up", bindLookUpOption);
                Collect("look-down", bindLookDownOption);
                Collect("look-left", bindLookLeftOption);
                Collect("look-right", bindLookRightOption);
                Collect("zoom-in", bindZoomInOption);
                Collect("zoom-out", bindZoomOutOption);
                Collect("fire-weapon", bindFireWeaponOption);
                Collect("select-weapon", bindSelectWeaponOption);
                Collect("transform", bindTransformOption);
                Collect("air-brake", bindAirBrakeOption);
                Collect("special", bindSpecialOption);

                Dictionary<int, BesFilePatcher.OptionsEntryOverride>? keybindOverrides;
                try
                {
                    keybindOverrides = KeybindTokens.ParseEntryOverrides(bindings);
                }
                catch (ArgumentException ex)
                {
                    invocation.ExitCode = ctx.Usage("legacy", ex.Message);
                    return;
                }

                // `--new` is a boolean flag, so its value alone cannot distinguish "the user asked for
                // OLD" from "the user said nothing about goodies". FindResultFor is non-null only when
                // the token actually appeared, which is what lets `--new --no-goodies` be refused
                // instead of silently dropped.
                bool? useNew = invocation.ParseResult.FindResultFor(newOption) is null
                    ? null
                    : invocation.ParseResult.GetValueForOption(newOption);

                invocation.ExitCode = Execute(
                    ctx,
                    input,
                    output,
                    invocation.ParseResult.GetValueForOption(analyzeOption),
                    invocation.ParseResult.GetValueForOption(verboseOption),
                    invocation.ParseResult.GetValueForOption(dumpMysteryOption),
                    invocation.ParseResult.GetValueForOption(compareOption),
                    invocation.ParseResult.GetValueForOption(listGoodiesOption),
                    invocation.ParseResult.GetValueForOption(showReservedGoodiesOption),
                    invocation.ParseResult.GetValueForOption(setGoodieStateOption),
                    useNew,
                    invocation.ParseResult.GetValueForOption(killsOption),
                    invocation.ParseResult.GetValueForOption(rankOption),
                    invocation.ParseResult.GetValueForOption(killsOnlyOption),
                    invocation.ParseResult.GetValueForOption(noNodesOption),
                    invocation.ParseResult.GetValueForOption(noLinksOption),
                    invocation.ParseResult.GetValueForOption(noGoodiesOption),
                    invocation.ParseResult.GetValueForOption(noKillsOption),
                    invocation.ParseResult.GetValueForOption(allowCareerSectionsOnOptionsFileOption),
                    invocation.ParseResult.GetValueForOption(levelRankOption),
                    invocation.ParseResult.GetValueForOption(aircraftKillsOption),
                    invocation.ParseResult.GetValueForOption(vehicleKillsOption),
                    invocation.ParseResult.GetValueForOption(emplacementKillsOption),
                    invocation.ParseResult.GetValueForOption(infantryKillsOption),
                    invocation.ParseResult.GetValueForOption(mechKillsOption),
                    invocation.ParseResult.GetValueForOption(soundVolumeOption),
                    invocation.ParseResult.GetValueForOption(musicVolumeOption),
                    invocation.ParseResult.GetValueForOption(invertWalkerP1Option),
                    invocation.ParseResult.GetValueForOption(invertWalkerP2Option),
                    invocation.ParseResult.GetValueForOption(invertFlightP1Option),
                    invocation.ParseResult.GetValueForOption(invertFlightP2Option),
                    invocation.ParseResult.GetValueForOption(vibrationP1Option),
                    invocation.ParseResult.GetValueForOption(vibrationP2Option),
                    invocation.ParseResult.GetValueForOption(controllerConfigP1Option),
                    invocation.ParseResult.GetValueForOption(controllerConfigP2Option),
                    invocation.ParseResult.GetValueForOption(experimentalPendingExtraGoodiesOption),
                    invocation.ParseResult.GetValueForOption(copyOptionsFromOption),
                    invocation.ParseResult.GetValueForOption(noCopyOptionsEntriesOption),
                    invocation.ParseResult.GetValueForOption(noCopyOptionsTailOption),
                    keybindOverrides,
                    bindings);
            });

            return rootCommand;
        }

        private static int Execute(
            CliContext ctx,
            FileInfo? input,
            FileInfo? output,
            bool analyze,
            bool verbose,
            bool dumpMystery,
            FileInfo? compare,
            bool listGoodies,
            bool showReservedGoodies,
            string[]? setGoodieStates,
            bool? useNew,
            int? kills,
            string? rank,
            bool killsOnly,
            bool noNodes,
            bool noLinks,
            bool noGoodies,
            bool noKills,
            bool allowCareerSectionsOnOptionsFile,
            string[]? levelRanks,
            int? aircraftKills,
            int? vehicleKills,
            int? emplacementKills,
            int? infantryKills,
            int? mechKills,
            double? soundVolume,
            double? musicVolume,
            string? invertWalkerP1,
            string? invertWalkerP2,
            string? invertFlightP1,
            string? invertFlightP2,
            string? vibrationP1,
            string? vibrationP2,
            uint? controllerConfigP1,
            uint? controllerConfigP2,
            int? experimentalPendingExtraGoodies,
            FileInfo? copyOptionsFrom,
            bool noCopyOptionsEntries,
            bool noCopyOptionsTail,
            Dictionary<int, BesFilePatcher.OptionsEntryOverride>? keybindOverrides,
            IReadOnlyDictionary<string, string[]> bindings)
        {
            const string command = "legacy.patch";

            if (input is null)
            {
                return ctx.Usage(
                    "legacy",
                    "Input file is required.",
                    $"Usage: {Program.AppCliName} <input.bes|input.bea> [output.bes|output.bea] [options]",
                    $"       {Program.AppCliName} --help");
            }

            if (!input.Exists)
                return ctx.Usage("legacy", $"Input file not found: {input.FullName}");

            if (showReservedGoodies && !listGoodies)
                ctx.Warn("--show-reserved-goodies is only used with --list-goodies.");

            if (compare is not null)
                return SaveVerbs.SavesCompare(ctx, input, compare);

            if (analyze)
                return SaveVerbs.SavesAnalyze(ctx, input, verbose, dumpMystery);

            if (listGoodies)
                return SaveVerbs.GoodiesList(ctx, input, showReservedGoodies);

            bool hasTargetedGoodieStates = setGoodieStates is { Length: > 0 };

            if (output is null)
            {
                return ctx.Usage(
                    "legacy",
                    "Output file is required for patching.",
                    "Use --analyze for read-only analysis, or specify an output file.");
            }

            if (!SaveVerbs.TryRejectInPlaceWrite(ctx, command, input.FullName, output.FullName, out int inPlaceRefusal))
                return inPlaceRefusal;

            if (hasTargetedGoodieStates)
            {
                // The targeted Goodie write is a narrow proof-setup mode. Mixing it with the broad
                // passes would mean two different write models over one file, so it is refused rather
                // than resolved to some precedence order nobody could predict.
                if (HasBroadPatchOptions(
                        useNew, kills, rank, killsOnly, noNodes, noLinks, noGoodies, noKills,
                        allowCareerSectionsOnOptionsFile, levelRanks,
                        aircraftKills, vehicleKills, emplacementKills, infantryKills, mechKills,
                        soundVolume, musicVolume,
                        invertWalkerP1, invertWalkerP2, invertFlightP1, invertFlightP2,
                        vibrationP1, vibrationP2, controllerConfigP1, controllerConfigP2,
                        experimentalPendingExtraGoodies, copyOptionsFrom,
                        noCopyOptionsEntries, noCopyOptionsTail, keybindOverrides))
                {
                    return ctx.Usage(
                        "legacy.set-goodie-state",
                        "--set-goodie-state is a narrow copied-save proof setup mode. Do not combine it with broad patch, settings, options, kill, rank, or keybind overrides.");
                }

                return SaveVerbs.GoodiesSet(ctx, input, output, setGoodieStates);
            }

            var careerOptions = new CareerPatchOptions
            {
                UseNew = useNew,
                Kills = kills,
                Rank = rank,
                KillsOnly = killsOnly,
                NoNodes = noNodes,
                NoLinks = noLinks,
                NoGoodies = noGoodies,
                NoKills = noKills,
                LevelRanks = levelRanks,
                AircraftKills = aircraftKills,
                VehicleKills = vehicleKills,
                EmplacementKills = emplacementKills,
                InfantryKills = infantryKills,
                MechKills = mechKills,
            };

            if (!CareerPatchPlan.TryResolve(careerOptions, out ResolvedCareerPatch plan, out string error, out IReadOnlyList<string> details))
                return ctx.Usage(command, error, details.ToArray());

            var patcher = new BesFilePatcher
            {
                UseNewGoodiesInstead = plan.UseNewGoodiesInstead,
                GlobalKillCount = plan.GlobalKillCount,
                Rank = plan.Rank,
                LevelRanks = plan.LevelRanks,
                PerCategoryKills = plan.PerCategoryKills,
                PatchNodes = plan.PatchNodes,
                PatchLinks = plan.PatchLinks,
                PatchGoodies = plan.PatchGoodies,
                PatchKills = plan.PatchKills,
                OptionsEntryOverrides = keybindOverrides,
            };

            try
            {
                patcher.SoundVolumeOverride = soundVolume.HasValue ? (float)soundVolume.Value : null;
                patcher.MusicVolumeOverride = musicVolume.HasValue ? (float)musicVolume.Value : null;
                patcher.InvertYAxisP1Override = KeybindTokens.ParseTriBool(invertWalkerP1, "--invert-walker-p1");
                patcher.InvertYAxisP2Override = KeybindTokens.ParseTriBool(invertWalkerP2, "--invert-walker-p2");
                patcher.InvertFlightP1Override = KeybindTokens.ParseTriBool(invertFlightP1, "--invert-flight-p1");
                patcher.InvertFlightP2Override = KeybindTokens.ParseTriBool(invertFlightP2, "--invert-flight-p2");
                patcher.VibrationP1Override = KeybindTokens.ParseTriBool(vibrationP1, "--vibration-p1");
                patcher.VibrationP2Override = KeybindTokens.ParseTriBool(vibrationP2, "--vibration-p2");
                patcher.ControllerConfigP1Override = controllerConfigP1;
                patcher.ControllerConfigP2Override = controllerConfigP2;
            }
            catch (ArgumentException ex)
            {
                return ctx.Usage(command, ex.Message);
            }

            if (experimentalPendingExtraGoodies.HasValue)
            {
                ctx.Warn("--experimental-pending-extra-goodies is currently ignored for retail Steam until persistence semantics are re-verified.");
            }

            if (copyOptionsFrom is not null)
            {
                if (!copyOptionsFrom.Exists)
                    return ctx.Usage(command, $"--copy-options-from file not found: {copyOptionsFrom.FullName}");

                patcher.CopyOptionsFromPath = copyOptionsFrom.FullName;
                patcher.CopyOptionsEntries = !noCopyOptionsEntries;
                patcher.CopyOptionsTail = !noCopyOptionsTail;
                if (!patcher.CopyOptionsEntries && !patcher.CopyOptionsTail)
                {
                    return ctx.Usage(
                        command,
                        "--copy-options-from was provided, but both --no-copy-options-entries and --no-copy-options-tail were set (nothing to copy).");
                }
            }

            // Career sections must not be written into an options file by accident. This is the one
            // place a caller can override that, and it must be asked for by name.
            bool inputOptionsLike = CareerPatchPlan.IsOptionsLikePath(input.FullName);
            bool outputOptionsLike = CareerPatchPlan.IsOptionsLikePath(output.FullName);
            if ((inputOptionsLike || outputOptionsLike) && plan.AnyCareerSectionEnabled)
            {
                if (!allowCareerSectionsOnOptionsFile)
                {
                    return ctx.Usage(
                        command,
                        "Career section patching is blocked for .bea/defaultoptions files by default.",
                        "Use settings-only mode (--no-nodes --no-links --no-goodies --no-kills),",
                        "or pass --allow-career-sections-on-options-file to override intentionally.");
                }

                ctx.Warn("Applying career section patching to an options-style file (.bea/defaultoptions).");
            }

            // Ask the shared intent contract before printing or writing anything. The patcher enforces
            // the same rule, but only once it is already running, where a contradictory request can only
            // come back as a patch failure - and a contradiction the caller typed is a usage error.
            SavePatchIntentSnapshot snapshot = CareerPatchPlan.ToIntentSnapshot(plan);
            if (SavePatchIntentContract.DescribeDiscardedIntents(snapshot) is { } discardedIntent)
                return ctx.Usage(command, discardedIntent);

            if (SavePatchIntentContract.DescribeEmptySectionPass(snapshot) is { } emptySectionPass)
                return ctx.Usage(command, emptySectionPass);

            PrintConfiguration(ctx, input, output, patcher, plan);

            PatchResult patchResult;
            try
            {
                patchResult = patcher.PatchFile(input.FullName, output.FullName);
            }
            catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
            {
                return ctx.Usage(command, SaveVerbs.DescribeFileFailure(ex));
            }

            object payload = new
            {
                input = input.FullName,
                output = output.FullName,
                route = "BesFilePatcher (legacy combined career + options write)",
                message = patchResult.Message,
                plan = CareerPatchPlan.Project(plan),
                keybindOverrideCount = keybindOverrides?.Count ?? 0,
                bindings = bindings.ToDictionary(pair => pair.Key, pair => pair.Value),
            };

            if (!ctx.Json)
            {
                ctx.Line(patchResult.Message);
                if (patchResult.Success)
                    PrintPatchSummary(ctx, patcher, output.FullName, plan.LevelRanks, plan.PerCategoryKills);
            }

            return patchResult.Success
                ? ctx.Ok(command, payload)
                : ctx.Verdict(command, patchResult.Message, payload);
        }

        private static void PrintConfiguration(
            CliContext ctx,
            FileInfo input,
            FileInfo output,
            BesFilePatcher patcher,
            ResolvedCareerPatch plan)
        {
            if (ctx.Json)
                return;

            ctx.Line("Onslaught Career Editor - CLI Mode");
            ctx.Line("===================================");
            ctx.Line($"Input:  {input.FullName}");
            ctx.Line($"Output: {output.FullName}");
            ctx.Line();
            ctx.Line("Configuration:");
            ctx.Line($"  Rank:           {(!patcher.PatchNodes ? "(missions not patched)" : patcher.Rank ?? "Keep (only the missions listed below are written)")}");
            ctx.Line($"  Kill count:     {(!patcher.PatchKills ? "(kills not patched)" : patcher.GlobalKillCount?.ToString() ?? "Keep (only the categories listed below are written)")}");
            ctx.Line($"  Goodies style:  {(!patcher.PatchGoodies ? "(goodies not patched)" : patcher.UseNewGoodiesInstead == true ? "NEW (gold)" : "OLD (blue)")}");
            ctx.Line($"  Patch nodes:    {(patcher.PatchNodes ? "Yes" : "No")}");
            ctx.Line($"  Patch links:    {(patcher.PatchLinks ? "Yes" : "No")}");
            ctx.Line($"  Patch goodies:  {(patcher.PatchGoodies ? "Yes" : "No")}");
            ctx.Line($"  Patch kills:    {(patcher.PatchKills ? "Yes" : "No")}");

            if (patcher.SoundVolumeOverride.HasValue) ctx.Line($"  Sound volume:   {patcher.SoundVolumeOverride.Value:0.###}");
            if (patcher.MusicVolumeOverride.HasValue) ctx.Line($"  Music volume:   {patcher.MusicVolumeOverride.Value:0.###}");
            if (patcher.InvertYAxisP1Override.HasValue) ctx.Line($"  Invert Y (Walker) (P1): {(patcher.InvertYAxisP1Override.Value ? "On" : "Off")}");
            if (patcher.InvertYAxisP2Override.HasValue) ctx.Line($"  Invert Y (Walker) (P2): {(patcher.InvertYAxisP2Override.Value ? "On" : "Off")}");
            if (patcher.InvertFlightP1Override.HasValue) ctx.Line($"  Invert Y (Flight) (P1): {(patcher.InvertFlightP1Override.Value ? "On" : "Off")}");
            if (patcher.InvertFlightP2Override.HasValue) ctx.Line($"  Invert Y (Flight) (P2): {(patcher.InvertFlightP2Override.Value ? "On" : "Off")}");
            if (patcher.VibrationP1Override.HasValue) ctx.Line($"  Vibration (P1): {(patcher.VibrationP1Override.Value ? "On" : "Off")}");
            if (patcher.VibrationP2Override.HasValue) ctx.Line($"  Vibration (P2): {(patcher.VibrationP2Override.Value ? "On" : "Off")}");
            if (patcher.ControllerConfigP1Override.HasValue) ctx.Line($"  Ctrl cfg (P1):  {patcher.ControllerConfigP1Override.Value}");
            if (patcher.ControllerConfigP2Override.HasValue) ctx.Line($"  Ctrl cfg (P2):  {patcher.ControllerConfigP2Override.Value}");

            if (!string.IsNullOrWhiteSpace(patcher.CopyOptionsFromPath))
            {
                ctx.Line($"  Copy options from: {patcher.CopyOptionsFromPath}");
                ctx.Line($"    - entries: {(patcher.CopyOptionsEntries ? "Yes" : "No")}");
                ctx.Line($"    - tail:    {(patcher.CopyOptionsTail ? "Yes" : "No")}");
            }

            if (patcher.OptionsEntryOverrides is { Count: > 0 })
            {
                ctx.Line($"  Keybind overrides: {patcher.OptionsEntryOverrides.Count} entries");
                ctx.Line("    NOTE: ControlSchemeIndex is forced to 0 (Custom) when applying keybind overrides.");
            }

            if (plan.LevelRanks is { Count: > 0 })
                ctx.Line($"  Level overrides: {plan.LevelRanks.Count} levels");

            if (plan.PerCategoryKills is { Count: > 0 })
            {
                ctx.Line("  Per-category kills:");
                foreach (int category in new[]
                         {
                             BesFilePatcher.KILL_AIRCRAFT, BesFilePatcher.KILL_VEHICLES,
                             BesFilePatcher.KILL_EMPLACEMENTS, BesFilePatcher.KILL_INFANTRY,
                             BesFilePatcher.KILL_MECHS,
                         })
                {
                    if (plan.PerCategoryKills.TryGetValue(category, out int value))
                        ctx.Line($"    {CareerPatchPlan.KillCategoryName(category) + ":",-14}{value}");
                }
            }

            ctx.Line();
        }

        private static void PrintPatchSummary(
            CliContext ctx,
            BesFilePatcher patcher,
            string outputPath,
            Dictionary<int, string>? levelRanks,
            Dictionary<int, int>? perCategoryKills)
        {
            ctx.Line($"Patched: {outputPath}");

            var patched = new List<string>();
            if (patcher.PatchNodes)
            {
                if (levelRanks is { Count: > 0 })
                {
                    patched.Add(patcher.Rank is null
                        ? $"Nodes ({levelRanks.Count} overrides only; every other mission untouched)"
                        : $"Nodes ({patcher.Rank} + {levelRanks.Count} overrides)");
                }
                else
                {
                    patched.Add($"Nodes ({patcher.Rank}-rank)");
                }
            }

            if (patcher.PatchLinks) patched.Add("Links");
            if (patcher.PatchGoodies) patched.Add($"Goodies ({(patcher.UseNewGoodiesInstead == true ? "NEW" : "OLD")})");
            if (patcher.PatchKills)
            {
                if (perCategoryKills is { Count: > 0 })
                {
                    patched.Add(patcher.GlobalKillCount is null
                        ? $"Kills ({perCategoryKills.Count} categories only; every other category untouched)"
                        : "Kills (custom per-category)");
                }
                else
                {
                    patched.Add($"Kills ({patcher.GlobalKillCount} each)");
                }
            }

            bool hasCareerSettings =
                patcher.SoundVolumeOverride.HasValue || patcher.MusicVolumeOverride.HasValue ||
                patcher.InvertYAxisP1Override.HasValue || patcher.InvertYAxisP2Override.HasValue ||
                patcher.InvertFlightP1Override.HasValue || patcher.InvertFlightP2Override.HasValue ||
                patcher.VibrationP1Override.HasValue || patcher.VibrationP2Override.HasValue ||
                patcher.ControllerConfigP1Override.HasValue || patcher.ControllerConfigP2Override.HasValue;
            if (hasCareerSettings)
                patched.Add("Career settings");

            if (!string.IsNullOrWhiteSpace(patcher.CopyOptionsFromPath))
            {
                var parts = new List<string>();
                if (patcher.CopyOptionsEntries) parts.Add("entries");
                if (patcher.CopyOptionsTail) parts.Add("tail");
                if (parts.Count > 0)
                    patched.Add($"Options copy ({string.Join("+", parts)})");
            }

            if (patcher.OptionsEntryOverrides is { Count: > 0 })
                patched.Add($"Keybind overrides ({patcher.OptionsEntryOverrides.Count} entries)");

            if (patched.Count > 0)
                ctx.Line($"  Patched: {string.Join(", ", patched)}");
            else
                ctx.Line("  WARNING: No sections selected for patching!");

            var skipped = new List<string>();
            if (!patcher.PatchNodes) skipped.Add("Nodes");
            if (!patcher.PatchLinks) skipped.Add("Links");
            if (!patcher.PatchGoodies) skipped.Add("Goodies");
            if (!patcher.PatchKills) skipped.Add("Kills");
            if (skipped.Count > 0)
                ctx.Line($"  Skipped: {string.Join(", ", skipped)}");

            if (patcher.PatchKills && perCategoryKills is { Count: > 0 })
            {
                ctx.Line($"  Kill counts (default: {patcher.GlobalKillCount?.ToString() ?? "keep current"}):");
                string[] categories = { "Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs" };
                for (int i = 0; i < categories.Length; i++)
                {
                    string value = perCategoryKills.TryGetValue(i, out int overrideKills)
                        ? overrideKills.ToString()
                        : patcher.GlobalKillCount?.ToString() ?? "kept unchanged";
                    string marker = perCategoryKills.ContainsKey(i) ? " *" : "";
                    ctx.Line($"    {categories[i]}: {value}{marker}");
                }
            }
        }

        private static bool HasBroadPatchOptions(
            bool? useNew, int? kills, string? rank, bool killsOnly,
            bool noNodes, bool noLinks, bool noGoodies, bool noKills,
            bool allowCareerSectionsOnOptionsFile, string[]? levelRanks,
            int? aircraftKills, int? vehicleKills, int? emplacementKills, int? infantryKills, int? mechKills,
            double? soundVolume, double? musicVolume,
            string? invertWalkerP1, string? invertWalkerP2, string? invertFlightP1, string? invertFlightP2,
            string? vibrationP1, string? vibrationP2, uint? controllerConfigP1, uint? controllerConfigP2,
            int? experimentalPendingExtraGoodies, FileInfo? copyOptionsFrom,
            bool noCopyOptionsEntries, bool noCopyOptionsTail,
            Dictionary<int, BesFilePatcher.OptionsEntryOverride>? keybindOverrides)
        {
            return useNew is not null ||
                   kills.HasValue ||
                   !string.IsNullOrWhiteSpace(rank) ||
                   killsOnly || noNodes || noLinks || noGoodies || noKills ||
                   allowCareerSectionsOnOptionsFile ||
                   levelRanks is { Length: > 0 } ||
                   aircraftKills.HasValue || vehicleKills.HasValue || emplacementKills.HasValue ||
                   infantryKills.HasValue || mechKills.HasValue ||
                   soundVolume.HasValue || musicVolume.HasValue ||
                   !string.IsNullOrWhiteSpace(invertWalkerP1) || !string.IsNullOrWhiteSpace(invertWalkerP2) ||
                   !string.IsNullOrWhiteSpace(invertFlightP1) || !string.IsNullOrWhiteSpace(invertFlightP2) ||
                   !string.IsNullOrWhiteSpace(vibrationP1) || !string.IsNullOrWhiteSpace(vibrationP2) ||
                   controllerConfigP1.HasValue || controllerConfigP2.HasValue ||
                   experimentalPendingExtraGoodies.HasValue ||
                   copyOptionsFrom is not null || noCopyOptionsEntries || noCopyOptionsTail ||
                   keybindOverrides is { Count: > 0 };
        }
    }
}
