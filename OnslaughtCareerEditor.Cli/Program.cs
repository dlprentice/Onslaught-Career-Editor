using System;
using System.Collections.Generic;
using System.CommandLine;
using System.CommandLine.IO;
using System.CommandLine.Invocation;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using Onslaught___Career_Editor.Cli;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Headless host for the toolkit's save, options, safe-copy, binary-patch, and process lanes.
    ///
    /// Two parsers live here on purpose. The verb tree is the interface going forward; the legacy
    /// flag-style command is kept intact behind a first-argument check so existing invocations and
    /// scripts keep working byte for byte. Dispatch is by first token rather than by trying to make one
    /// grammar serve both, because a root command carrying both a positional input file and a set of
    /// subcommands makes "is <c>saves</c> a verb or a filename?" a question the parser has to guess at.
    /// </summary>
    public static class Program
    {
        public const string AppCliName = "onslaught-career-editor";

        [DllImport("kernel32.dll")]
        private static extern bool AttachConsole(int dwProcessId);

        private const int ATTACH_PARENT_PROCESS = -1;

        private static readonly HashSet<string> VerbNames = new(StringComparer.OrdinalIgnoreCase)
        {
            "config", "saves", "goodies", "options", "copy", "patch", "process", "trainer", "version",
        };

        [STAThread]
        public static int Main(string[] args)
        {
            AttachConsole(ATTACH_PARENT_PROCESS);
            return Run(args, Console.Out, Console.Error);
        }

        /// <summary>
        /// The whole CLI, with its output injected. Tests drive this directly rather than spawning a
        /// process, which is what makes it affordable to pin verb routing, envelope shape, and the
        /// exit-code split.
        /// </summary>
        public static int Run(string[] args, TextWriter output, TextWriter error)
        {
            ArgumentNullException.ThrowIfNull(args);

            var console = new TextWriterConsole(output, error);
            CliContext MakeContext(bool json) => new(output, error, json);

            if (args.Length == 0)
            {
                BuildVerbRoot(MakeContext).Invoke(new[] { "--help" }, console);
                return CliExit.UsageOrToolError;
            }

            string first = args[0];
            bool verbForm =
                VerbNames.Contains(first) ||
                first is "--help" or "-h" or "-?" or "/?" or "--version";

            return verbForm
                ? BuildVerbRoot(MakeContext).Invoke(args, console)
                : LegacyCli.Build(MakeContext).Invoke(args, console);
        }

        private static RootCommand BuildVerbRoot(Func<bool, CliContext> contextFactory)
        {
            var jsonOption = new Option<bool>(
                "--json",
                "Emit a machine-readable JSON envelope on stdout and print nothing else.");

            var root = new RootCommand(
                """
                Onslaught Toolkit - Battle Engine Aquila save, options, safe-copy and patch tooling.

                Exit codes:
                  0  the operation ran and the answer is yes
                  1  usage or tool error - the operation could not be attempted (bad flags, missing
                     file, safety refusal). Nothing was measured.
                  2  the operation ran to completion and the data says no (invalid save, patch target
                     in an unexpected state, no game install detected). Re-running with different
                     flags will not change this.

                Every verb accepts --json. The envelope is
                  {"ok":bool,"command":string,"exitCode":int,"warnings":[string],"data":{...},"error":{...}}
                and is emitted on both success and failure, so a caller can parse first and branch second.

                The original flag-style invocation still works:
                  onslaught-career-editor <input.bes> [output.bes] [flags]
                Run it with any non-verb first argument to reach it.
                """)
            {
                Name = AppCliName,
            };

            root.AddGlobalOption(jsonOption);
            bool Json(InvocationContext c) => c.ParseResult.GetValueForOption(jsonOption);

            root.AddCommand(BuildConfigCommand(contextFactory, Json));
            root.AddCommand(BuildSavesCommand(contextFactory, Json));
            root.AddCommand(BuildGoodiesCommand(contextFactory, Json));
            root.AddCommand(BuildOptionsCommand(contextFactory, Json));
            root.AddCommand(BuildCopyCommand(contextFactory, Json));
            root.AddCommand(BuildPatchCommand(contextFactory, Json));
            root.AddCommand(BuildProcessCommand(contextFactory, Json));
            root.AddCommand(BuildTrainerCommand(contextFactory, Json));

            var version = new Command("version", "Show the tool version and catalog identities.");
            version.SetHandler((InvocationContext c) =>
            {
                CliContext ctx = contextFactory(Json(c));
                string assemblyVersion = typeof(Program).Assembly.GetName().Version?.ToString() ?? "unknown";
                c.ExitCode = ctx.Ok("version", new
                {
                    version = assemblyVersion,
                    patchCatalogStatus = BinaryPatchEngine.CatalogStatus,
                    usingFallbackPatchCatalog = BinaryPatchEngine.UsingFallbackCatalog,
                    safeCopyProfileCatalogVersion = BinaryPatchPlanBuilder.SafeCopyProfileCatalogVersion,
                    safeCopyProfileCatalogSha256 = BinaryPatchPlanBuilder.SafeCopyProfileCatalogSha256,
                    safeCopyRoot = SafeCopyVerbs.SafeCopyRoot,
                    patchBenchRoot = SafeCopyVerbs.PatchBenchRoot,
                }, $"{AppCliName} {assemblyVersion}");
            });
            root.AddCommand(version);

            return root;
        }

        // ------------------------------------------------------------------ config

        private static Command BuildConfigCommand(Func<bool, CliContext> factory, Func<InvocationContext, bool> json)
        {
            var config = new Command("config", "Inspect and set tool configuration.");

            var show = new Command("show", "Show the current configuration and resolved paths.");
            show.SetHandler((InvocationContext c) => c.ExitCode = SaveVerbs.ConfigShow(factory(json(c))));
            config.AddCommand(show);

            var pathArg = new Argument<string?>("path", () => null, "Game installation folder.");
            var setGameDir = new Command("set-game-dir", "Set the game directory used for save discovery.") { pathArg };
            setGameDir.SetHandler((InvocationContext c) =>
                c.ExitCode = SaveVerbs.ConfigSetGameDir(factory(json(c)), c.ParseResult.GetValueForArgument(pathArg)));
            config.AddCommand(setGameDir);

            var detect = new Command("detect", "Auto-detect a Battle Engine Aquila installation. Exit 2 when none is found.");
            detect.SetHandler((InvocationContext c) => c.ExitCode = SaveVerbs.ConfigDetect(factory(json(c))));
            config.AddCommand(detect);

            return config;
        }

        // ------------------------------------------------------------------ saves

        private static Command BuildSavesCommand(Func<bool, CliContext> factory, Func<InvocationContext, bool> json)
        {
            var saves = new Command("saves", "Read and patch .bes career saves.");

            var list = new Command("list", "List save files discovered in the game directory.");
            list.SetHandler((InvocationContext c) => c.ExitCode = SaveVerbs.SavesList(factory(json(c))));
            saves.AddCommand(list);

            var analyzeFile = new Argument<FileInfo?>("file", () => null, "Input .bes/.bea file.");
            var verboseOption = new Option<bool>(new[] { "--verbose", "-v" }, "Include hex dumps.");
            var dumpMysteryOption = new Option<bool>("--dump-mystery", "Hex dump reserved/unmapped regions.");
            var analyze = new Command("analyze", "Analyze a save. Exit 2 when the file is not a valid save.")
            { analyzeFile, verboseOption, dumpMysteryOption };
            analyze.SetHandler((InvocationContext c) => c.ExitCode = SaveVerbs.SavesAnalyze(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(analyzeFile),
                c.ParseResult.GetValueForOption(verboseOption),
                c.ParseResult.GetValueForOption(dumpMysteryOption)));
            saves.AddCommand(analyze);

            var leftArg = new Argument<FileInfo?>("left", () => null, "First file.");
            var rightArg = new Argument<FileInfo?>("right", () => null, "Second file.");
            var compare = new Command("compare", "Compare two save/options files byte by byte.") { leftArg, rightArg };
            compare.SetHandler((InvocationContext c) => c.ExitCode = SaveVerbs.SavesCompare(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(leftArg),
                c.ParseResult.GetValueForArgument(rightArg)));
            saves.AddCommand(compare);

            var inArg = new Argument<FileInfo?>("input", () => null, "Input .bes career save.");
            var outArg = new Argument<FileInfo?>("output", () => null, "Output .bes career save (must differ from input).");
            var rankOption = new Option<string?>("--rank", "Baseline mission grade: S, A, B, C, D, E, NONE. Omit alongside --level-rank to change only the listed missions.");
            var levelRankOption = new Option<string[]>("--level-rank", "Per-mission grade override, NODE_INDEX:GRADE (1-43), repeatable.") { AllowMultipleArgumentsPerToken = true };
            var killsOption = new Option<int?>("--kills", "Baseline kill count for every category.");
            var aircraftOption = new Option<int?>("--aircraft-kills", "Aircraft kill count override.");
            var vehicleOption = new Option<int?>("--vehicle-kills", "Vehicle kill count override.");
            var emplacementOption = new Option<int?>("--emplacement-kills", "Emplacement kill count override.");
            var infantryOption = new Option<int?>("--infantry-kills", "Infantry kill count override.");
            var mechOption = new Option<int?>("--mech-kills", "Mech kill count override.");
            var newOption = new Option<bool>("--new", "Mark goodies NEW (gold) instead of OLD (blue).");
            var noNodesOption = new Option<bool>("--no-nodes", "Skip the mission node pass.");
            var noLinksOption = new Option<bool>("--no-links", "Skip the mission link pass.");
            var noGoodiesOption = new Option<bool>("--no-goodies", "Skip the goodie pass.");
            var noKillsOption = new Option<bool>("--no-kills", "Skip the kill pass.");
            var killsOnlyOption = new Option<bool>("--kills-only", "Patch kills only (nodes, links and goodies untouched).");

            var patch = new Command(
                "patch",
                "Patch career sections through SaveEditorService. Refuses .bea options files.")
            {
                inArg, outArg, rankOption, levelRankOption, killsOption,
                aircraftOption, vehicleOption, emplacementOption, infantryOption, mechOption,
                newOption, noNodesOption, noLinksOption, noGoodiesOption, noKillsOption, killsOnlyOption,
            };
            patch.SetHandler((InvocationContext c) =>
            {
                // The flag's presence, not its value, is what separates "asked for OLD" from silence.
                bool? useNew = c.ParseResult.FindResultFor(newOption) is null
                    ? null
                    : c.ParseResult.GetValueForOption(newOption);

                c.ExitCode = WriteVerbs.SavesPatch(
                    factory(json(c)),
                    c.ParseResult.GetValueForArgument(inArg),
                    c.ParseResult.GetValueForArgument(outArg),
                    new CareerPatchOptions
                    {
                        UseNew = useNew,
                        Kills = c.ParseResult.GetValueForOption(killsOption),
                        Rank = c.ParseResult.GetValueForOption(rankOption),
                        KillsOnly = c.ParseResult.GetValueForOption(killsOnlyOption),
                        NoNodes = c.ParseResult.GetValueForOption(noNodesOption),
                        NoLinks = c.ParseResult.GetValueForOption(noLinksOption),
                        NoGoodies = c.ParseResult.GetValueForOption(noGoodiesOption),
                        NoKills = c.ParseResult.GetValueForOption(noKillsOption),
                        LevelRanks = c.ParseResult.GetValueForOption(levelRankOption),
                        AircraftKills = c.ParseResult.GetValueForOption(aircraftOption),
                        VehicleKills = c.ParseResult.GetValueForOption(vehicleOption),
                        EmplacementKills = c.ParseResult.GetValueForOption(emplacementOption),
                        InfantryKills = c.ParseResult.GetValueForOption(infantryOption),
                        MechKills = c.ParseResult.GetValueForOption(mechOption),
                    });
            });
            saves.AddCommand(patch);

            return saves;
        }

        // ------------------------------------------------------------------ goodies

        private static Command BuildGoodiesCommand(Func<bool, CliContext> factory, Func<InvocationContext, bool> json)
        {
            var goodies = new Command("goodies", "Read and write per-slot Goodie states.");

            var fileArg = new Argument<FileInfo?>("file", () => null, "Input .bes/.bea file.");
            var showReservedOption = new Option<bool>("--show-reserved", "Include reserved slots 233-299.");
            var list = new Command("list", "List per-slot Goodie states. Exit 2 when the file is not a valid save.")
            { fileArg, showReservedOption };
            list.SetHandler((InvocationContext c) => c.ExitCode = SaveVerbs.GoodiesList(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(fileArg),
                c.ParseResult.GetValueForOption(showReservedOption)));
            goodies.AddCommand(list);

            var inArg = new Argument<FileInfo?>("input", () => null, "Input .bes file.");
            var outArg = new Argument<FileInfo?>("output", () => null, "Output .bes file (must differ from input).");
            var goodieOption = new Option<string[]>("--goodie", "Goodie override INDEX:STATE (state 0/1/2/3 or locked/instructions/new/old), repeatable.")
            { AllowMultipleArgumentsPerToken = true };
            var set = new Command(
                "set",
                "Write targeted Goodie states. A single slot goes through SaveEditorService's focused write.")
            { inArg, outArg, goodieOption };
            set.SetHandler((InvocationContext c) => c.ExitCode = SaveVerbs.GoodiesSet(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(inArg),
                c.ParseResult.GetValueForArgument(outArg),
                c.ParseResult.GetValueForOption(goodieOption)));
            goodies.AddCommand(set);

            return goodies;
        }

        // ------------------------------------------------------------------ options

        private static Command BuildOptionsCommand(Func<bool, CliContext> factory, Func<InvocationContext, bool> json)
        {
            var options = new Command("options", "Read and edit .bea game options files.");

            var showFileArg = new Argument<FileInfo?>("file", () => null, "Input .bea options file.");
            var show = new Command("show", "Show settings and keybinds from an options file.") { showFileArg };
            show.SetHandler((InvocationContext c) => c.ExitCode = SaveVerbs.OptionsShow(
                factory(json(c)), c.ParseResult.GetValueForArgument(showFileArg)));
            options.AddCommand(show);

            var inArg = new Argument<FileInfo?>("input", () => null, "Input options/save file.");
            var outArg = new Argument<FileInfo?>("output", () => null, "Output file (must differ from input).");
            var soundOption = new Option<double?>("--sound-volume", "Sound volume 0.0-1.0.");
            var musicOption = new Option<double?>("--music-volume", "Music volume 0.0-1.0.");
            var invertWalkerP1Option = new Option<string?>("--invert-walker-p1", "Invert Y (Walker) P1: on/off.");
            var invertWalkerP2Option = new Option<string?>("--invert-walker-p2", "Invert Y (Walker) P2: on/off.");
            var invertFlightP1Option = new Option<string?>("--invert-flight-p1", "Invert Y (Flight) P1: on/off.");
            var invertFlightP2Option = new Option<string?>("--invert-flight-p2", "Invert Y (Flight) P2: on/off.");
            var vibrationP1Option = new Option<string?>("--vibration-p1", "Controller vibration P1: on/off.");
            var vibrationP2Option = new Option<string?>("--vibration-p2", "Controller vibration P2: on/off.");
            var controllerP1Option = new Option<uint?>("--controller-config-p1", "Controller configuration index P1.");
            var controllerP2Option = new Option<uint?>("--controller-config-p2", "Controller configuration index P2.");
            var mouseSensOption = new Option<double?>("--mouse-sensitivity", "Mouse look sensitivity.");
            var screenShapeOption = new Option<uint?>("--screen-shape", "Screen shape: 0=4:3, 1=16:9, 2=1:1.");
            var copyFromOption = new Option<FileInfo?>("--copy-options-from", "Copy options entries + tail snapshot from another file.");
            var noCopyEntriesOption = new Option<bool>("--no-copy-options-entries", "With --copy-options-from: skip the entries region.");
            var noCopyTailOption = new Option<bool>("--no-copy-options-tail", "With --copy-options-from: skip the 0x56-byte tail snapshot.");

            var bindOptions = new Dictionary<string, Option<string[]>>(StringComparer.OrdinalIgnoreCase);
            foreach (string binding in KeybindTokens.BindingEntryIds.Keys)
            {
                var option = new Option<string[]>(
                    $"--bind-{binding}",
                    $"Override the {binding} binding (P1 P2). Use 'keep' to leave a side alone.")
                { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
                bindOptions[binding] = option;
            }

            var edit = new Command(
                "edit",
                "Edit options. A .bea target goes through ConfigurationEditorService; a .bes target uses the settings-only patcher.")
            {
                inArg, outArg, soundOption, musicOption,
                invertWalkerP1Option, invertWalkerP2Option, invertFlightP1Option, invertFlightP2Option,
                vibrationP1Option, vibrationP2Option, controllerP1Option, controllerP2Option,
                mouseSensOption, screenShapeOption, copyFromOption, noCopyEntriesOption, noCopyTailOption,
            };
            foreach (Option<string[]> option in bindOptions.Values)
                edit.AddOption(option);

            edit.SetHandler((InvocationContext c) =>
            {
                var bindings = new Dictionary<string, string[]>(StringComparer.OrdinalIgnoreCase);
                foreach (KeyValuePair<string, Option<string[]>> pair in bindOptions)
                {
                    string[]? value = c.ParseResult.GetValueForOption(pair.Value);
                    if (value is { Length: 2 })
                        bindings[pair.Key] = value;
                }

                c.ExitCode = WriteVerbs.OptionsEdit(
                    factory(json(c)),
                    c.ParseResult.GetValueForArgument(inArg),
                    c.ParseResult.GetValueForArgument(outArg),
                    new WriteVerbs.OptionsEditRequest
                    {
                        SoundVolume = c.ParseResult.GetValueForOption(soundOption),
                        MusicVolume = c.ParseResult.GetValueForOption(musicOption),
                        InvertWalkerP1 = c.ParseResult.GetValueForOption(invertWalkerP1Option),
                        InvertWalkerP2 = c.ParseResult.GetValueForOption(invertWalkerP2Option),
                        InvertFlightP1 = c.ParseResult.GetValueForOption(invertFlightP1Option),
                        InvertFlightP2 = c.ParseResult.GetValueForOption(invertFlightP2Option),
                        VibrationP1 = c.ParseResult.GetValueForOption(vibrationP1Option),
                        VibrationP2 = c.ParseResult.GetValueForOption(vibrationP2Option),
                        ControllerConfigP1 = c.ParseResult.GetValueForOption(controllerP1Option),
                        ControllerConfigP2 = c.ParseResult.GetValueForOption(controllerP2Option),
                        MouseSensitivity = c.ParseResult.GetValueForOption(mouseSensOption),
                        ScreenShape = c.ParseResult.GetValueForOption(screenShapeOption),
                        CopyOptionsFrom = c.ParseResult.GetValueForOption(copyFromOption),
                        NoCopyOptionsEntries = c.ParseResult.GetValueForOption(noCopyEntriesOption),
                        NoCopyOptionsTail = c.ParseResult.GetValueForOption(noCopyTailOption),
                        Bindings = bindings,
                    });
            });
            options.AddCommand(edit);

            return options;
        }

        // ------------------------------------------------------------------ copy

        private static Command BuildCopyCommand(Func<bool, CliContext> factory, Func<InvocationContext, bool> json)
        {
            var copy = new Command("copy", "Create, list, launch, stop and delete app-owned playable game copies.");

            var list = new Command("list", "List safe copies under the app-owned root.");
            list.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.CopyList(factory(json(c))));
            copy.AddCommand(list);

            var sourceOption = new Option<string?>("--source", "Source game root. Defaults to the configured or detected install.");
            var exeOption = new Option<string?>("--executable", "Explicit BEA.exe (or BEA.exe.original.backup) source.");
            var nameOption = new Option<string?>("--name", "Profile folder name. Letters, digits, dot, underscore, dash; max 64.");
            var presetOption = new Option<string?>("--profile", "Safe copy profile preset id. See 'patch list'.");
            var patchKeyOption = new Option<string[]>("--patch", "Extra patch key to apply, repeatable.") { AllowMultipleArgumentsPerToken = true };
            var launchArgOption = new Option<string[]>("--launch-arg", "Launch argument for the copied game, repeatable.") { AllowMultipleArgumentsPerToken = true };
            var resolutionOption = new Option<string?>("--resolution", "Gameplay resolution as WIDTHxHEIGHT. Defaults to 1600x900, the size that was played and measured.");
            var savegamesOption = new Option<bool>("--include-savegames", "Copy the source savegames folder into the copy.");
            var musicOption = new Option<string?>("--music-swap", "Music swap preset id to stage.");
            var textModOption = new Option<bool>("--level100-text-mod", "Apply the Level 100 tutorial text mod.");
            var flightModOption = new Option<bool>("--level100-early-flight", "Apply the Level 100 early flight mod.");

            var create = new Command(
                "create",
                "Create a playable copied game folder. Copies several GB; never touches the installed game.")
            {
                sourceOption, exeOption, nameOption, presetOption, patchKeyOption, launchArgOption,
                resolutionOption, savegamesOption, musicOption, textModOption, flightModOption,
            };
            create.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.CopyCreate(
                factory(json(c)),
                c.ParseResult.GetValueForOption(sourceOption),
                c.ParseResult.GetValueForOption(exeOption),
                c.ParseResult.GetValueForOption(nameOption),
                c.ParseResult.GetValueForOption(presetOption),
                c.ParseResult.GetValueForOption(patchKeyOption),
                c.ParseResult.GetValueForOption(launchArgOption),
                c.ParseResult.GetValueForOption(resolutionOption),
                c.ParseResult.GetValueForOption(savegamesOption),
                c.ParseResult.GetValueForOption(musicOption),
                c.ParseResult.GetValueForOption(textModOption),
                c.ParseResult.GetValueForOption(flightModOption)));
            copy.AddCommand(create);

            var launchIdArg = new Argument<string?>("id", () => null, "Safe copy id (folder name) or path.");
            var launchArgsOption = new Option<string[]>("--launch-arg", "Launch argument, repeatable.") { AllowMultipleArgumentsPerToken = true };
            var launch = new Command("launch", "Launch a safe copy and register it as a managed process.")
            { launchIdArg, launchArgsOption };
            launch.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.CopyLaunch(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(launchIdArg),
                c.ParseResult.GetValueForOption(launchArgsOption)));
            copy.AddCommand(launch);

            var stopIdArg = new Argument<string?>("id", () => null, "Safe copy id (folder name) or path.");
            var stop = new Command("stop", "Stop the managed process running from a safe copy.") { stopIdArg };
            stop.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.CopyStop(
                factory(json(c)), c.ParseResult.GetValueForArgument(stopIdArg)));
            copy.AddCommand(stop);

            var savesIdArg = new Argument<string?>("id", () => null, "Safe copy id (folder name) or path. Omit to sweep every copy.");
            var saves = new Command(
                "saves",
                "List the career saves inside a safe copy - what a delete would take with it.")
            { savesIdArg };
            saves.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.CopySaves(
                factory(json(c)), c.ParseResult.GetValueForArgument(savesIdArg)));
            copy.AddCommand(saves);

            var rescueIdArg = new Argument<string?>("id", () => null, "Safe copy id (folder name) or path.");
            var rescueToOption = new Option<string?>("--to", "Folder to keep the saves in. Must be outside the copy.");
            var rescueNameOption = new Option<string[]>("--save", "Save to bring out, repeatable. Default: all of them.")
            { AllowMultipleArgumentsPerToken = true };
            var rescueOverwriteOption = new Option<bool>("--overwrite", "Replace saves of the same name already in the destination.");
            var rescue = new Command(
                "rescue",
                "Copy career saves out of a safe copy into an ordinary folder. The copy is left untouched.")
            { rescueIdArg, rescueToOption, rescueNameOption, rescueOverwriteOption };
            rescue.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.CopyRescue(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(rescueIdArg),
                c.ParseResult.GetValueForOption(rescueToOption),
                c.ParseResult.GetValueForOption(rescueNameOption),
                c.ParseResult.GetValueForOption(rescueOverwriteOption)));
            copy.AddCommand(rescue);

            var deleteIdArg = new Argument<string?>("id", () => null, "Safe copy id (folder name) or path.");
            var forceOption = new Option<bool>("--force", "Confirm the irreversible delete.");
            var keepSavesOption = new Option<string?>(
                "--keep-saves-in",
                "Copy the career saves into this folder first, and delete only once every one of them is verified there.");
            var discardSavesOption = new Option<bool>(
                "--discard-saves",
                "Delete the career saves along with the copy. Only after you have looked at 'copy saves'.");
            var delete = new Command(
                "delete",
                "Delete an app-owned safe copy. Refuses anything outside the app-owned root, anything without a generated manifest, anything still running, and anything holding career saves you have not dealt with.")
            { deleteIdArg, forceOption, keepSavesOption, discardSavesOption };
            delete.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.CopyDelete(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(deleteIdArg),
                c.ParseResult.GetValueForOption(forceOption),
                c.ParseResult.GetValueForOption(keepSavesOption),
                c.ParseResult.GetValueForOption(discardSavesOption)));
            copy.AddCommand(delete);

            return copy;
        }

        // ------------------------------------------------------------------ patch

        private static Command BuildPatchCommand(Func<bool, CliContext> factory, Func<InvocationContext, bool> json)
        {
            var patch = new Command("patch", "Inspect and apply binary patches to an app-owned BEA.exe working copy.");

            var list = new Command("list", "List the patch catalog and the safe copy profile presets.");
            list.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.PatchList(factory(json(c))));
            patch.AddCommand(list);

            var stageSourceArg = new Argument<string?>("source", () => null, "Source BEA.exe or BEA.exe.original.backup.");
            var stage = new Command("stage", "Copy a BEA.exe into a fresh app-owned Patch Bench workspace.") { stageSourceArg };
            stage.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.PatchStage(
                factory(json(c)), c.ParseResult.GetValueForArgument(stageSourceArg)));
            patch.AddCommand(stage);

            Argument<string?> TargetArg() =>
                new("target", () => null, "Patch Bench workspace id, workspace folder, or path to BEA.exe.");
            Option<string?> ProfileOption() => new("--profile", "Select every patch key in this profile preset.");
            Option<string[]> KeysOption() =>
                new("--patch", "Select an individual patch key, repeatable.") { AllowMultipleArgumentsPerToken = true };

            var planTarget = TargetArg();
            var planProfile = ProfileOption();
            var planKeys = KeysOption();
            var plan = new Command("plan", "Show what an apply would change and the current state of each region. Read-only.")
            { planTarget, planProfile, planKeys };
            plan.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.PatchPlan(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(planTarget),
                c.ParseResult.GetValueForOption(planProfile),
                c.ParseResult.GetValueForOption(planKeys)));
            patch.AddCommand(plan);

            var verifyTarget = TargetArg();
            var verifyProfile = ProfileOption();
            var verifyKeys = KeysOption();
            var verify = new Command("verify", "Verify the selected patches against the target. Exit 2 when verification fails.")
            { verifyTarget, verifyProfile, verifyKeys };
            verify.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.PatchVerify(
                factory(json(c)),
                c.ParseResult.GetValueForArgument(verifyTarget),
                c.ParseResult.GetValueForOption(verifyProfile),
                c.ParseResult.GetValueForOption(verifyKeys)));
            patch.AddCommand(verify);

            var applyTarget = TargetArg();
            var applyIds = new Argument<string[]>("ids", () => Array.Empty<string>(), "Patch keys to apply.");
            var applyProfile = ProfileOption();
            var applyKeys = KeysOption();
            var apply = new Command("apply", "Apply the selected patches. Verifies first and refuses if verification fails.")
            { applyTarget, applyIds, applyProfile, applyKeys };
            apply.SetHandler((InvocationContext c) =>
            {
                var keys = new List<string>(c.ParseResult.GetValueForArgument(applyIds));
                string[]? viaOption = c.ParseResult.GetValueForOption(applyKeys);
                if (viaOption is { Length: > 0 })
                    keys.AddRange(viaOption);

                c.ExitCode = SafeCopyVerbs.PatchApply(
                    factory(json(c)),
                    c.ParseResult.GetValueForArgument(applyTarget),
                    c.ParseResult.GetValueForOption(applyProfile),
                    keys);
            });
            patch.AddCommand(apply);

            var restoreTarget = TargetArg();
            var restore = new Command("restore", "Restore the target from its verified full-file backup snapshot.") { restoreTarget };
            restore.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.PatchRestore(
                factory(json(c)), c.ParseResult.GetValueForArgument(restoreTarget)));
            patch.AddCommand(restore);

            return patch;
        }

        // ------------------------------------------------------------------ process

        private static Command BuildProcessCommand(Func<bool, CliContext> factory, Func<InvocationContext, bool> json)
        {
            var process = new Command("process", "Inspect and stop managed safe-copy game processes.");

            var list = new Command("list", "List registered managed processes, with verified liveness.");
            list.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.ProcessList(factory(json(c))));
            process.AddCommand(list);

            var pidArg = new Argument<int>("pid", "Process id.");
            var stop = new Command("stop", "Stop a registered managed process by id.") { pidArg };
            stop.SetHandler((InvocationContext c) => c.ExitCode = SafeCopyVerbs.ProcessStop(
                factory(json(c)), c.ParseResult.GetValueForArgument(pidArg)));
            process.AddCommand(stop);

            return process;
        }

        // ------------------------------------------------------------------ trainer

        private static Command BuildTrainerCommand(Func<bool, CliContext> factory, Func<InvocationContext, bool> json)
        {
            var trainer = new Command(
                "trainer",
                "Read and set player vitals in a running safe copy. Attaches only to a process this app launched.");

            Option<int?> PidOption() => new(
                "--pid",
                "Managed process id to work on. Defaults to the newest safe copy that is still running.");

            var statusPid = PidOption();
            var status = new Command(
                "status",
                "Report whether a managed copy is running and whether attaching to it is allowed. Reads no vitals.")
            { statusPid };
            status.SetHandler((InvocationContext c) => c.ExitCode = TrainerVerbs.TrainerStatus(
                factory(json(c)), c.ParseResult.GetValueForOption(statusPid)));
            trainer.AddCommand(status);

            var readPid = PidOption();
            var read = new Command(
                "read",
                "Read player one's life, energy, shields and state. Exit 2 when no mission is running.")
            { readPid };
            read.SetHandler((InvocationContext c) => c.ExitCode = TrainerVerbs.TrainerRead(
                factory(json(c)), c.ParseResult.GetValueForOption(readPid)));
            trainer.AddCommand(read);

            var setPid = PidOption();
            var lifeOption = new Option<float?>("--life", "Life value to write.");
            var energyOption = new Option<float?>("--energy", "Energy value to write.");
            var shieldsOption = new Option<float?>("--shields", "Shields value to write.");
            var set = new Command(
                "set",
                "Write a vital, after re-reading it. Refuses unless that read comes back believable.")
            { setPid, lifeOption, energyOption, shieldsOption };
            set.SetHandler((InvocationContext c) => c.ExitCode = TrainerVerbs.TrainerSet(
                factory(json(c)),
                c.ParseResult.GetValueForOption(setPid),
                c.ParseResult.GetValueForOption(lifeOption),
                c.ParseResult.GetValueForOption(energyOption),
                c.ParseResult.GetValueForOption(shieldsOption)));
            trainer.AddCommand(set);

            return trainer;
        }

        /// <summary>
        /// Routes System.CommandLine's own output (help, parse errors) through the injected writers, so
        /// an in-process caller sees everything the process would have printed.
        /// </summary>
        private sealed class TextWriterConsole : IConsole
        {
            public TextWriterConsole(TextWriter output, TextWriter error)
            {
                Out = new Writer(output);
                Error = new Writer(error);
            }

            public IStandardStreamWriter Out { get; }

            public IStandardStreamWriter Error { get; }

            public bool IsOutputRedirected => true;

            public bool IsErrorRedirected => true;

            public bool IsInputRedirected => false;

            private sealed class Writer : IStandardStreamWriter
            {
                private readonly TextWriter _writer;

                public Writer(TextWriter writer) => _writer = writer;

                public void Write(string? value) => _writer.Write(value);
            }
        }
    }
}
