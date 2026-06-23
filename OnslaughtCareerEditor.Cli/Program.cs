using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.CommandLine;
using System.CommandLine.Invocation;
using System.IO;
using System.Globalization;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Dedicated CLI host for retail-backed save/config/binary patch workflows.
    /// </summary>
    public static class Program
    {
        private const string AppCliName = "onslaught-career-editor";
        private const string AssetMaterialImportManifestSchemaVersion = "appcore-asset-material-import-manifest.v1";
        private const string AssetMaterialImportDryRunPlanSchemaVersion = "appcore-asset-material-import-dry-run-plan.v1";
        private const string AssetMaterialImportPackagePlanSchemaVersion = "appcore-asset-material-import-package-plan.v1";
        private const string AssetMaterialImportPackageMaterializationSchemaVersion = "appcore-asset-material-import-package-materialization.v1";
        private const string AssetMaterialPackageInspectionSchemaVersion = "appcore-asset-material-package-inspection.v1";
        private const string AssetMaterialPackageWorkOrderSchemaVersion = "appcore-asset-material-package-work-order.v1";
        private const string AssetMaterialPackageWorkOrderSidecarValidationSchemaVersion = "appcore-asset-material-package-work-order-sidecar-validation.v1";
        private const string AssetMaterialPackageImporterBatchSchemaVersion = "appcore-asset-material-package-importer-batch.v1";
        private const string AssetMaterialPackageImporterDryRunSchemaVersion = "appcore-asset-material-package-importer-dry-run.v1";
        private const string AssetMaterialPackageImporterDryRunSidecarValidationSchemaVersion = "appcore-asset-material-package-importer-dry-run-sidecar-validation.v1";
        private const string AssetMaterialPackageImporterInputMaterializationSchemaVersion = "appcore-asset-material-package-importer-input-materialization.v1";
        private const string AssetMaterialPackageImporterInputPlanSchemaVersion = "appcore-asset-material-package-importer-input-plan.v1";
        private const string AssetMaterialPackageRebuildPreviewMaterializationSchemaVersion = "appcore-asset-material-package-rebuild-preview-materialization.v1";
        private const string AssetMaterialPackageRebuildSceneMaterializationSchemaVersion = "appcore-asset-material-package-rebuild-scene-materialization.v1";
        private const string AssetMaterialPackageRebuildMeshMaterializationSchemaVersion = "appcore-asset-material-package-rebuild-mesh-materialization.v1";
        private const string AssetMaterialPackageRebuildMeshImportSchemaVersion = "appcore-asset-material-package-rebuild-mesh-import.v1";
        private const string PrivateAssetOutputArmPhrase = "MATERIALIZE ASSET MATERIAL PACKAGE";

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            PropertyNameCaseInsensitive = true,
            WriteIndented = true
        };

        // Win32 console attachment for CLI output
        [DllImport("kernel32.dll")]
        private static extern bool AttachConsole(int dwProcessId);

        [DllImport("kernel32.dll")]
        private static extern bool FreeConsole();

        [DllImport("kernel32.dll")]
        private static extern bool AllocConsole();

        private const int ATTACH_PARENT_PROCESS = -1;

        [STAThread]
        public static int Main(string[] args)
        {
            AttachConsole(ATTACH_PARENT_PROCESS);
            return BuildRootCommand().Invoke(args);
        }

        /// <summary>
        /// Build the System.CommandLine root command with all options.
        /// </summary>
        private static RootCommand BuildRootCommand()
        {
            // Positional arguments
            var inputArg = new Argument<FileInfo?>(
                "input",
                description: "Input .bes/.bea file",
                getDefaultValue: () => null);

            var outputArg = new Argument<FileInfo?>(
                "output",
                description: "Output .bes/.bea file (required for patching)",
                getDefaultValue: () => null);

            // Options (matching patcher.py)
            var analyzeOption = new Option<bool>(
                "--analyze",
                "Analyze the input file without patching");

            var verboseOption = new Option<bool>(
                new[] { "--verbose", "-v" },
                "Verbose output (hex dumps in analyze mode)");

            var dumpMysteryOption = new Option<bool>(
                "--dump-mystery",
                "Show hex dump of reserved/unmapped byte regions (use with --analyze)");

            var compareOption = new Option<FileInfo?>(
                "--compare",
                "Compare input with another .bes/.bea file");

            var listGoodiesOption = new Option<bool>(
                "--list-goodies",
                "List per-slot goodie states (read-only; requires input file).");

            var showReservedGoodiesOption = new Option<bool>(
                "--show-reserved-goodies",
                "With --list-goodies: include reserved slots (233-299).");

            var setGoodieStateOption = new Option<string[]>(
                "--set-goodie-state",
                "Targeted Goodie state override for copied-save proof setup (format: INDEX:STATE; state 0/1/2/3 or locked/instructions/new/old).")
            { AllowMultipleArgumentsPerToken = true };

            var newOption = new Option<bool>(
                "--new",
                "Mark goodies as NEW (gold) instead of OLD (blue)");

            var killsOption = new Option<int?>(
                "--kills",
                "Global kill count for all categories (default: 100)");

            var rankOption = new Option<string?>(
                "--rank",
                "Rank for all missions: S, A, B, C, D, E, or NONE (default: S)");

            var killsOnlyOption = new Option<bool>(
                "--kills-only",
                "Only patch kill counts (preserve nodes, links, goodies)");

            var noNodesOption = new Option<bool>(
                "--no-nodes",
                "Skip patching mission nodes");

            var noLinksOption = new Option<bool>(
                "--no-links",
                "Skip patching mission links");

            var noGoodiesOption = new Option<bool>(
                "--no-goodies",
                "Skip patching goodies");

            var noKillsOption = new Option<bool>(
                "--no-kills",
                "Skip patching kill counts");

            var allowCareerSectionsOnOptionsFileOption = new Option<bool>(
                "--allow-career-sections-on-options-file",
                "Allow patching career sections when input/output is .bea/defaultoptions.bea (advanced; off by default).");

            // Per-level rank (repeatable): --level-rank N:GRADE
            var levelRankOption = new Option<string[]>(
                "--level-rank",
                "Per-level rank override (format: NODE_INDEX:GRADE, repeatable; node index 1-43)")
            { AllowMultipleArgumentsPerToken = true };

            // Per-category kill count options
            var aircraftKillsOption = new Option<int?>(
                "--aircraft-kills",
                "Override aircraft kill count (thresholds: 25/50/75/100)");

            var vehicleKillsOption = new Option<int?>(
                "--vehicle-kills",
                "Override vehicle kill count (thresholds: 100/200/300/400)");

            var emplacementKillsOption = new Option<int?>(
                "--emplacement-kills",
                "Override emplacement kill count (thresholds: 25/50; 75 appears only in combined unlocks)");

            var infantryKillsOption = new Option<int?>(
                "--infantry-kills",
                "Override infantry kill count (thresholds: 40/80/160)");

            var mechKillsOption = new Option<int?>(
                "--mech-kills",
                "Override mech kill count (thresholds: 20/40/80; 40 unlocks two goodies)");

            // Optional CCareer settings overrides (true dword view; omit to preserve existing save values)
            var soundVolumeOption = new Option<double?>(
                "--sound-volume",
                "Override sound volume (0.0-1.0). Omit to preserve.");

            var musicVolumeOption = new Option<double?>(
                "--music-volume",
                "Override music volume (0.0-1.0). Omit to preserve.");

            var invertWalkerP1Option = new Option<string?>(
                new[] { "--invert-walker-p1", "--invert-y-p1" },
                "Override invert-Y (Walker mode) for player 1: on/off/true/false/1/0 (omit to preserve).");

            var invertWalkerP2Option = new Option<string?>(
                new[] { "--invert-walker-p2", "--invert-y-p2" },
                "Override invert-Y (Walker mode) for player 2: on/off/true/false/1/0 (omit to preserve).");

            var invertFlightP1Option = new Option<string?>(
                "--invert-flight-p1",
                "Override invert-Y (Flight/Jet mode) for player 1: on/off/true/false/1/0 (omit to preserve).");

            var invertFlightP2Option = new Option<string?>(
                "--invert-flight-p2",
                "Override invert-Y (Flight/Jet mode) for player 2: on/off/true/false/1/0 (omit to preserve).");

            var vibrationP1Option = new Option<string?>(
                "--vibration-p1",
                "Override controller vibration for player 1: on/off/true/false/1/0 (omit to preserve).");

            var vibrationP2Option = new Option<string?>(
                "--vibration-p2",
                "Override controller vibration for player 2: on/off/true/false/1/0 (omit to preserve).");

            var controllerConfigP1Option = new Option<uint?>(
                "--controller-config-p1",
                "Override controller configuration index for player 1 (omit to preserve).");

            var controllerConfigP2Option = new Option<uint?>(
                "--controller-config-p2",
                "Override controller configuration index for player 2 (omit to preserve).");

            var experimentalPendingExtraGoodiesOption = new Option<int?>(
                "--experimental-pending-extra-goodies",
                "Experimental only: pending-extra-goodies override (currently ignored on retail Steam until persistence is re-verified).");

            // Options entries + tail snapshot copy (raw byte copy for keybinds + global options snapshot)
            var copyOptionsFromOption = new Option<FileInfo?>(
                "--copy-options-from",
                "Copy the options entries + tail snapshot from another .bes/.bea file (same size/layout).");

            var noCopyOptionsEntriesOption = new Option<bool>(
                "--no-copy-options-entries",
                "With --copy-options-from: do not copy the options entries region (`0x20*N`, typically `0x200` in Steam saves).");

            var noCopyOptionsTailOption = new Option<bool>(
                "--no-copy-options-tail",
                "With --copy-options-from: do not copy the fixed 0x56-byte options tail snapshot (globals).");

            // Keybind overrides (options entries). Each takes exactly 2 values: P1 P2.
            // Use "keep" to preserve that side. Examples: A, Num7, Up, Mouse, MouseX+, MouseY-, MouseWheelUp, MouseLeft, MouseRight.
            var bindMoveForwardOption = new Option<string[]>(
                "--bind-move-forward",
                "Override Movement: Forward bindings (P1 P2).")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindMoveBackwardOption = new Option<string[]>(
                "--bind-move-backward",
                "Override Movement: Backward bindings (P1 P2).")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindMoveLeftOption = new Option<string[]>(
                "--bind-move-left",
                "Override Movement: Left bindings (P1 P2).")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindMoveRightOption = new Option<string[]>(
                "--bind-move-right",
                "Override Movement: Right bindings (P1 P2).")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };

            var bindLookUpOption = new Option<string[]>(
                "--bind-look-up",
                "Override Look: Up bindings (P1 P2). Use Mouse / MouseX+ / MouseY- to bind to mouse axis.")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindLookDownOption = new Option<string[]>(
                "--bind-look-down",
                "Override Look: Down bindings (P1 P2). Use Mouse / MouseX+ / MouseY- to bind to mouse axis.")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindLookLeftOption = new Option<string[]>(
                "--bind-look-left",
                "Override Look: Left bindings (P1 P2). Use Mouse / MouseX+ / MouseY- to bind to mouse axis.")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindLookRightOption = new Option<string[]>(
                "--bind-look-right",
                "Override Look: Right bindings (P1 P2). Use Mouse / MouseX+ / MouseY- to bind to mouse axis.")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };

            var bindZoomInOption = new Option<string[]>(
                "--bind-zoom-in",
                "Override Zoom: In bindings (P1 P2). Use MouseWheelUp/MouseWheelDown for wheel.")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindZoomOutOption = new Option<string[]>(
                "--bind-zoom-out",
                "Override Zoom: Out bindings (P1 P2). Use MouseWheelUp/MouseWheelDown for wheel.")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };

            var bindFireWeaponOption = new Option<string[]>(
                "--bind-fire-weapon",
                "Override Others: Fire weapon bindings (P1 P2). Use MouseLeft to bind to LMB.")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindSelectWeaponOption = new Option<string[]>(
                "--bind-select-weapon",
                "Override Others: Select weapon bindings (P1 P2). Use MouseRight to bind to RMB.")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindTransformOption = new Option<string[]>(
                "--bind-transform",
                "Override Others: Transform bindings (P1 P2).")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindAirBrakeOption = new Option<string[]>(
                "--bind-air-brake",
                "Override Others: Air brake bindings (P1 P2).")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };
            var bindSpecialOption = new Option<string[]>(
                "--bind-special",
                "Override Others: Special function bindings (P1 P2).")
            { Arity = new ArgumentArity(2, 2), AllowMultipleArgumentsPerToken = true };

            // Config management options
            var listSavesOption = new Option<bool>(
                "--list-saves",
                "List save files found in the game directory");

            var setGameDirOption = new Option<string?>(
                "--set-game-dir",
                "Set the game directory path for save file discovery");

            var showConfigOption = new Option<bool>(
                "--show-config",
                "Show current configuration");

            var assetMaterialImportManifestOption = new Option<string?>(
                "--asset-material-import-manifest",
                "Emit a read-only, public-safe material import manifest from a generated asset catalog path or directory.");

            var assetMaterialImportDryRunPlanOption = new Option<string?>(
                "--asset-material-import-dry-run-plan",
                "Emit a read-only, public-safe material import dry-run plan from a generated asset catalog path or directory.");

            var assetMaterialImportPackagePlanOption = new Option<string?>(
                "--asset-material-import-package-plan",
                "Emit a read-only, public-safe material import package plan from a generated asset catalog path or directory.");

            var assetMaterialImportPackageMaterializeOption = new Option<string?>(
                "--asset-material-import-package-materialize",
                "Copy ready model and texture package files from a generated asset catalog into an app-owned output root.");

            var assetMaterialPackageInspectOption = new Option<string?>(
                "--asset-material-package-inspect",
                "Inspect a materialized asset material package output folder and validate its manifest/payload files.");

            var assetMaterialPackageWorkOrderOption = new Option<string?>(
                "--asset-material-package-work-order",
                "Emit a read-only importer/rebuild work order from a materialized asset material package output folder.");

            var assetMaterialPackageWorkOrderSidecarValidateOption = new Option<string?>(
                "--asset-material-package-work-order-sidecar-validate",
                "Validate the saved material package work-order sidecar against the current package manifest and payload files.");

            var assetMaterialPackageImporterBatchOption = new Option<string?>(
                "--asset-material-package-importer-batch",
                "Emit flat package-relative importer/rebuild batch tasks from a validated material package work-order sidecar.");

            var assetMaterialPackageImporterDryRunOption = new Option<string?>(
                "--asset-material-package-importer-dry-run",
                "Emit package-relative importer dry-run adapter rows from a validated material package importer batch.");

            var assetMaterialPackageImporterDryRunSidecarValidateOption = new Option<string?>(
                "--asset-material-package-importer-dry-run-sidecar-validate",
                "Validate the saved material package importer dry-run sidecar against the current package work-order and payload files.");

            var assetMaterialPackageImporterInputMaterializeOption = new Option<string?>(
                "--asset-material-package-importer-input-materialize",
                "Stage validated package-local model/texture payloads into an importer-input tree for future importer/rebuild tooling. Defaults to preflight unless the private-output arm phrase is supplied.");

            var assetMaterialPackageImporterInputPlanOption = new Option<string?>(
                "--asset-material-package-importer-input-plan",
                "Build a read-only importer/rebuild consumer plan from package-local importer-input files.");

            var assetMaterialPackageRebuildPreviewMaterializeOption = new Option<string?>(
                "--asset-material-package-rebuild-preview-materialize",
                "Write deterministic OBJ wireframe preview files and binding sidecars from staged package-local importer-input files. Defaults to preflight unless the private-output arm phrase is supplied.");

            var assetMaterialPackageRebuildSceneMaterializeOption = new Option<string?>(
                "--asset-material-package-rebuild-scene-materialize",
                "Write deterministic package-relative scene/mesh/material contract JSON from staged importer-input and rebuild-preview files. Defaults to preflight unless the private-output arm phrase is supplied.");

            var assetMaterialPackageRebuildMeshMaterializeOption = new Option<string?>(
                "--asset-material-package-rebuild-mesh-materialize",
                "Write deterministic package-relative OBJ/MTL mesh outputs from existing rebuild-scene contracts and staged FBX data. Defaults to preflight unless the private-output arm phrase is supplied.");

            var assetMaterialPackageRebuildMeshImportMaterializeOption = new Option<string?>(
                "--asset-material-package-rebuild-mesh-import-materialize",
                "Validate generated package-relative OBJ/MTL rebuild mesh outputs as importer-consumable data. Defaults to preflight unless the private-output arm phrase is supplied.");

            var assetMaterialPackageOutputOption = new Option<string?>(
                "--asset-material-package-output",
                "Output directory for --asset-material-import-package-materialize.");

            var assetMaterialPackagePreflightOption = new Option<bool>(
                "--asset-material-package-preflight",
                "Preflight material package output without copying asset bytes. This is the default unless the exact arm phrase is supplied.");

            var armPrivateAssetOutputOption = new Option<string?>(
                "--arm-private-asset-output",
                "Exact arm phrase required to copy private asset bytes: MATERIALIZE ASSET MATERIAL PACKAGE.");

            var failOnUnresolvedMaterialBindingsOption = new Option<bool>(
                "--fail-on-unresolved-material-bindings",
                "With material-import outputs: return a non-zero exit code if texture bindings remain unresolved; package plans also fail when model exports or metadata are not package-ready.");

            // Build root command
            var rootCommand = new RootCommand("Onslaught Toolkit - Battle Engine Aquila save/options editor")
            {
                inputArg,
                outputArg,
                analyzeOption,
                verboseOption,
                dumpMysteryOption,
                compareOption,
                listGoodiesOption,
                showReservedGoodiesOption,
                setGoodieStateOption,
                newOption,
                killsOption,
                rankOption,
                killsOnlyOption,
                noNodesOption,
                noLinksOption,
                noGoodiesOption,
                noKillsOption,
                allowCareerSectionsOnOptionsFileOption,
                levelRankOption,
                aircraftKillsOption,
                vehicleKillsOption,
                emplacementKillsOption,
                infantryKillsOption,
                mechKillsOption,
                soundVolumeOption,
                musicVolumeOption,
                invertWalkerP1Option,
                invertWalkerP2Option,
                invertFlightP1Option,
                invertFlightP2Option,
                vibrationP1Option,
                vibrationP2Option,
                controllerConfigP1Option,
                controllerConfigP2Option,
                experimentalPendingExtraGoodiesOption,
                copyOptionsFromOption,
                noCopyOptionsEntriesOption,
                noCopyOptionsTailOption,
                bindMoveForwardOption,
                bindMoveBackwardOption,
                bindMoveLeftOption,
                bindMoveRightOption,
                bindLookUpOption,
                bindLookDownOption,
                bindLookLeftOption,
                bindLookRightOption,
                bindZoomInOption,
                bindZoomOutOption,
                bindFireWeaponOption,
                bindSelectWeaponOption,
                bindTransformOption,
                bindAirBrakeOption,
                bindSpecialOption,
                listSavesOption,
                setGameDirOption,
                showConfigOption,
                assetMaterialImportManifestOption,
                assetMaterialImportDryRunPlanOption,
                assetMaterialImportPackagePlanOption,
                assetMaterialImportPackageMaterializeOption,
                assetMaterialPackageInspectOption,
                assetMaterialPackageWorkOrderOption,
                assetMaterialPackageWorkOrderSidecarValidateOption,
                assetMaterialPackageImporterBatchOption,
                assetMaterialPackageImporterDryRunOption,
                assetMaterialPackageImporterDryRunSidecarValidateOption,
                assetMaterialPackageImporterInputMaterializeOption,
                assetMaterialPackageImporterInputPlanOption,
                assetMaterialPackageRebuildPreviewMaterializeOption,
                assetMaterialPackageRebuildSceneMaterializeOption,
                assetMaterialPackageRebuildMeshMaterializeOption,
                assetMaterialPackageRebuildMeshImportMaterializeOption,
                assetMaterialPackageOutputOption,
                assetMaterialPackagePreflightOption,
                armPrivateAssetOutputOption,
                failOnUnresolvedMaterialBindingsOption
            };
            rootCommand.Name = AppCliName;

            rootCommand.SetHandler((InvocationContext context) =>
            {
                // Extract all values
                var input = context.ParseResult.GetValueForArgument(inputArg);
                var output = context.ParseResult.GetValueForArgument(outputArg);
                var analyze = context.ParseResult.GetValueForOption(analyzeOption);
                var verbose = context.ParseResult.GetValueForOption(verboseOption);
                var dumpMystery = context.ParseResult.GetValueForOption(dumpMysteryOption);
                var compare = context.ParseResult.GetValueForOption(compareOption);
                var listGoodies = context.ParseResult.GetValueForOption(listGoodiesOption);
                var showReservedGoodies = context.ParseResult.GetValueForOption(showReservedGoodiesOption);
                var setGoodieStates = context.ParseResult.GetValueForOption(setGoodieStateOption);
                var useNew = context.ParseResult.GetValueForOption(newOption);
                var kills = context.ParseResult.GetValueForOption(killsOption);
                var rank = context.ParseResult.GetValueForOption(rankOption);
                var killsOnly = context.ParseResult.GetValueForOption(killsOnlyOption);
                var noNodes = context.ParseResult.GetValueForOption(noNodesOption);
                var noLinks = context.ParseResult.GetValueForOption(noLinksOption);
                var noGoodies = context.ParseResult.GetValueForOption(noGoodiesOption);
                var noKills = context.ParseResult.GetValueForOption(noKillsOption);
                var allowCareerSectionsOnOptionsFile = context.ParseResult.GetValueForOption(allowCareerSectionsOnOptionsFileOption);
                var levelRanks = context.ParseResult.GetValueForOption(levelRankOption);
                var aircraftKills = context.ParseResult.GetValueForOption(aircraftKillsOption);
                var vehicleKills = context.ParseResult.GetValueForOption(vehicleKillsOption);
                var emplacementKills = context.ParseResult.GetValueForOption(emplacementKillsOption);
                var infantryKills = context.ParseResult.GetValueForOption(infantryKillsOption);
                var mechKills = context.ParseResult.GetValueForOption(mechKillsOption);
                var soundVolume = context.ParseResult.GetValueForOption(soundVolumeOption);
                var musicVolume = context.ParseResult.GetValueForOption(musicVolumeOption);
                var invertWalkerP1 = context.ParseResult.GetValueForOption(invertWalkerP1Option);
                var invertWalkerP2 = context.ParseResult.GetValueForOption(invertWalkerP2Option);
                var invertFlightP1 = context.ParseResult.GetValueForOption(invertFlightP1Option);
                var invertFlightP2 = context.ParseResult.GetValueForOption(invertFlightP2Option);
                var vibrationP1 = context.ParseResult.GetValueForOption(vibrationP1Option);
                var vibrationP2 = context.ParseResult.GetValueForOption(vibrationP2Option);
                var controllerConfigP1 = context.ParseResult.GetValueForOption(controllerConfigP1Option);
                var controllerConfigP2 = context.ParseResult.GetValueForOption(controllerConfigP2Option);
                var experimentalPendingExtraGoodies = context.ParseResult.GetValueForOption(experimentalPendingExtraGoodiesOption);
                var copyOptionsFrom = context.ParseResult.GetValueForOption(copyOptionsFromOption);
                var noCopyOptionsEntries = context.ParseResult.GetValueForOption(noCopyOptionsEntriesOption);
                var noCopyOptionsTail = context.ParseResult.GetValueForOption(noCopyOptionsTailOption);
                var bindMoveForward = context.ParseResult.GetValueForOption(bindMoveForwardOption);
                var bindMoveBackward = context.ParseResult.GetValueForOption(bindMoveBackwardOption);
                var bindMoveLeft = context.ParseResult.GetValueForOption(bindMoveLeftOption);
                var bindMoveRight = context.ParseResult.GetValueForOption(bindMoveRightOption);
                var bindLookUp = context.ParseResult.GetValueForOption(bindLookUpOption);
                var bindLookDown = context.ParseResult.GetValueForOption(bindLookDownOption);
                var bindLookLeft = context.ParseResult.GetValueForOption(bindLookLeftOption);
                var bindLookRight = context.ParseResult.GetValueForOption(bindLookRightOption);
                var bindZoomIn = context.ParseResult.GetValueForOption(bindZoomInOption);
                var bindZoomOut = context.ParseResult.GetValueForOption(bindZoomOutOption);
                var bindFireWeapon = context.ParseResult.GetValueForOption(bindFireWeaponOption);
                var bindSelectWeapon = context.ParseResult.GetValueForOption(bindSelectWeaponOption);
                var bindTransform = context.ParseResult.GetValueForOption(bindTransformOption);
                var bindAirBrake = context.ParseResult.GetValueForOption(bindAirBrakeOption);
                var bindSpecial = context.ParseResult.GetValueForOption(bindSpecialOption);
                var listSaves = context.ParseResult.GetValueForOption(listSavesOption);
                var setGameDir = context.ParseResult.GetValueForOption(setGameDirOption);
                var showConfig = context.ParseResult.GetValueForOption(showConfigOption);
                var assetMaterialImportManifest = context.ParseResult.GetValueForOption(assetMaterialImportManifestOption);
                var assetMaterialImportDryRunPlan = context.ParseResult.GetValueForOption(assetMaterialImportDryRunPlanOption);
                var assetMaterialImportPackagePlan = context.ParseResult.GetValueForOption(assetMaterialImportPackagePlanOption);
                var assetMaterialImportPackageMaterialize = context.ParseResult.GetValueForOption(assetMaterialImportPackageMaterializeOption);
                var assetMaterialPackageInspect = context.ParseResult.GetValueForOption(assetMaterialPackageInspectOption);
                var assetMaterialPackageWorkOrder = context.ParseResult.GetValueForOption(assetMaterialPackageWorkOrderOption);
                var assetMaterialPackageWorkOrderSidecarValidate = context.ParseResult.GetValueForOption(assetMaterialPackageWorkOrderSidecarValidateOption);
                var assetMaterialPackageImporterBatch = context.ParseResult.GetValueForOption(assetMaterialPackageImporterBatchOption);
                var assetMaterialPackageImporterDryRun = context.ParseResult.GetValueForOption(assetMaterialPackageImporterDryRunOption);
                var assetMaterialPackageImporterDryRunSidecarValidate = context.ParseResult.GetValueForOption(assetMaterialPackageImporterDryRunSidecarValidateOption);
                var assetMaterialPackageImporterInputMaterialize = context.ParseResult.GetValueForOption(assetMaterialPackageImporterInputMaterializeOption);
                var assetMaterialPackageImporterInputPlan = context.ParseResult.GetValueForOption(assetMaterialPackageImporterInputPlanOption);
                var assetMaterialPackageRebuildPreviewMaterialize = context.ParseResult.GetValueForOption(assetMaterialPackageRebuildPreviewMaterializeOption);
                var assetMaterialPackageRebuildSceneMaterialize = context.ParseResult.GetValueForOption(assetMaterialPackageRebuildSceneMaterializeOption);
                var assetMaterialPackageRebuildMeshMaterialize = context.ParseResult.GetValueForOption(assetMaterialPackageRebuildMeshMaterializeOption);
                var assetMaterialPackageRebuildMeshImportMaterialize = context.ParseResult.GetValueForOption(assetMaterialPackageRebuildMeshImportMaterializeOption);
                var assetMaterialPackageOutput = context.ParseResult.GetValueForOption(assetMaterialPackageOutputOption);
                var assetMaterialPackagePreflight = context.ParseResult.GetValueForOption(assetMaterialPackagePreflightOption);
                var armPrivateAssetOutput = context.ParseResult.GetValueForOption(armPrivateAssetOutputOption);
                var failOnUnresolvedMaterialBindings = context.ParseResult.GetValueForOption(failOnUnresolvedMaterialBindingsOption);

                // Handle config commands first (don't require input file)
                if (listSaves || setGameDir != null || showConfig)
                {
                    context.ExitCode = HandleConfigCommands(listSaves, setGameDir, showConfig);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialImportManifest))
                {
                    context.ExitCode = HandleAssetMaterialImportManifest(
                        assetMaterialImportManifest,
                        failOnUnresolvedMaterialBindings);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialImportDryRunPlan))
                {
                    context.ExitCode = HandleAssetMaterialImportDryRunPlan(
                        assetMaterialImportDryRunPlan,
                        failOnUnresolvedMaterialBindings);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialImportPackagePlan))
                {
                    context.ExitCode = HandleAssetMaterialImportPackagePlan(
                        assetMaterialImportPackagePlan,
                        failOnUnresolvedMaterialBindings);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageInspect))
                {
                    context.ExitCode = HandleAssetMaterialPackageInspection(assetMaterialPackageInspect);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageWorkOrder))
                {
                    context.ExitCode = HandleAssetMaterialPackageWorkOrder(assetMaterialPackageWorkOrder);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageWorkOrderSidecarValidate))
                {
                    context.ExitCode = HandleAssetMaterialPackageWorkOrderSidecarValidation(assetMaterialPackageWorkOrderSidecarValidate);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageImporterBatch))
                {
                    context.ExitCode = HandleAssetMaterialPackageImporterBatch(assetMaterialPackageImporterBatch);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageImporterDryRun))
                {
                    context.ExitCode = HandleAssetMaterialPackageImporterDryRun(assetMaterialPackageImporterDryRun);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageImporterDryRunSidecarValidate))
                {
                    context.ExitCode = HandleAssetMaterialPackageImporterDryRunSidecarValidate(assetMaterialPackageImporterDryRunSidecarValidate);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageImporterInputMaterialize))
                {
                    context.ExitCode = HandleAssetMaterialPackageImporterInputMaterialization(
                        assetMaterialPackageImporterInputMaterialize,
                        assetMaterialPackagePreflight,
                        armPrivateAssetOutput);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageImporterInputPlan))
                {
                    context.ExitCode = HandleAssetMaterialPackageImporterInputPlan(assetMaterialPackageImporterInputPlan);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageRebuildPreviewMaterialize))
                {
                    context.ExitCode = HandleAssetMaterialPackageRebuildPreviewMaterialization(
                        assetMaterialPackageRebuildPreviewMaterialize,
                        assetMaterialPackagePreflight,
                        armPrivateAssetOutput);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageRebuildSceneMaterialize))
                {
                    context.ExitCode = HandleAssetMaterialPackageRebuildSceneMaterialization(
                        assetMaterialPackageRebuildSceneMaterialize,
                        assetMaterialPackagePreflight,
                        armPrivateAssetOutput);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageRebuildMeshMaterialize))
                {
                    context.ExitCode = HandleAssetMaterialPackageRebuildMeshMaterialization(
                        assetMaterialPackageRebuildMeshMaterialize,
                        assetMaterialPackagePreflight,
                        armPrivateAssetOutput);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialPackageRebuildMeshImportMaterialize))
                {
                    context.ExitCode = HandleAssetMaterialPackageRebuildMeshImportMaterialization(
                        assetMaterialPackageRebuildMeshImportMaterialize,
                        assetMaterialPackagePreflight,
                        armPrivateAssetOutput);
                    return;
                }

                if (!string.IsNullOrWhiteSpace(assetMaterialImportPackageMaterialize))
                {
                    context.ExitCode = HandleAssetMaterialImportPackageMaterialization(
                        assetMaterialImportPackageMaterialize,
                        assetMaterialPackageOutput,
                        assetMaterialPackagePreflight,
                        armPrivateAssetOutput);
                    return;
                }

                    Dictionary<int, BesFilePatcher.OptionsEntryOverride>? keybindOverrides = null;
                    try
                    {
                        // Keybind overrides (options entries)
                        keybindOverrides = ParseKeybindOverridesFromCli(
                            bindMoveForward, bindMoveBackward, bindMoveLeft, bindMoveRight,
                            bindLookUp, bindLookDown, bindLookLeft, bindLookRight,
                            bindZoomIn, bindZoomOut,
                            bindFireWeapon, bindSelectWeapon, bindTransform, bindAirBrake, bindSpecial);
                    }
                    catch (ArgumentException ex)
                    {
                        Console.Error.WriteLine(ex.Message);
                        context.ExitCode = 1;
                        return;
                    }

	                // Execute CLI logic
		                int exitCode = ExecuteCli(
		                    input, output, analyze, verbose, dumpMystery, compare, listGoodies, showReservedGoodies, setGoodieStates, useNew,
                    kills, rank, killsOnly,
                    noNodes, noLinks, noGoodies, noKills,
                    allowCareerSectionsOnOptionsFile,
                    levelRanks,
	                    aircraftKills, vehicleKills, emplacementKills, infantryKills, mechKills,
	                    soundVolume, musicVolume,
		                    invertWalkerP1, invertWalkerP2,
		                    invertFlightP1, invertFlightP2,
		                    vibrationP1, vibrationP2,
		                    controllerConfigP1, controllerConfigP2,
		                    experimentalPendingExtraGoodies,
                        copyOptionsFrom, noCopyOptionsEntries, noCopyOptionsTail,
                        keybindOverrides);
	
	                context.ExitCode = exitCode;
	            });

            return rootCommand;
        }

        /// <summary>
        /// Execute CLI commands based on parsed options.
        /// </summary>
	        private static int ExecuteCli(
	            FileInfo? input,
	            FileInfo? output,
	            bool analyze,
	            bool verbose,
	            bool dumpMystery,
	            FileInfo? compare,
	            bool listGoodies,
	            bool showReservedGoodies,
                string[]? setGoodieStates,
	            bool useNew,
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
                Dictionary<int, BesFilePatcher.OptionsEntryOverride>? keybindOverrides)
	        {
            // Validate input file is provided for all operations
            if (input == null)
            {
                Console.Error.WriteLine("Error: Input file is required.");
                Console.Error.WriteLine($"Usage: {AppCliName} <input.bes|input.bea> [output.bes|output.bea] [options]");
                Console.Error.WriteLine($"       {AppCliName} --help");
                return 1;
            }

            if (!input.Exists)
            {
                Console.Error.WriteLine($"Error: Input file not found: {input.FullName}");
                return 1;
            }

            if (showReservedGoodies && !listGoodies)
            {
                Console.Error.WriteLine("Warning: --show-reserved-goodies is only used with --list-goodies.");
            }

            // Compare mode
            if (compare != null)
            {
                if (!compare.Exists)
                {
                    Console.Error.WriteLine($"Error: Compare file not found: {compare.FullName}");
                    return 1;
                }

                try
                {
                    var result = BesFilePatcher.CompareFiles(input.FullName, compare.FullName);
                    string report = BesFilePatcher.FormatCompareReport(result, input.FullName, compare.FullName);
                    Console.WriteLine(report);
                    return 0;
                }
                catch (IOException ex)
                {
                    Console.Error.WriteLine($"Error: Failed to access file: {ex.Message}");
                    return 1;
                }
                catch (UnauthorizedAccessException ex)
                {
                    Console.Error.WriteLine($"Error: Access denied: {ex.Message}");
                    return 1;
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Error: {ex.Message}");
                    return 1;
                }
            }

            // Analyze mode
            if (analyze)
            {
                try
                {
                    var analysis = BesFilePatcher.AnalyzeSave(input.FullName);
                    string report = BesFilePatcher.FormatAnalysisReport(analysis, verbose, dumpMystery);
                    Console.WriteLine(report);
                    return analysis.IsValid ? 0 : 1;
                }
                catch (IOException ex)
                {
                    Console.Error.WriteLine($"Error: Failed to access file: {ex.Message}");
                    return 1;
                }
                catch (UnauthorizedAccessException ex)
                {
                    Console.Error.WriteLine($"Error: Access denied: {ex.Message}");
                    return 1;
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Error: {ex.Message}");
                    return 1;
                }
            }

            // Goodie list mode
            if (listGoodies)
            {
                return PrintGoodieList(input.FullName, showReservedGoodies);
            }

            bool hasTargetedGoodieStates = setGoodieStates != null && setGoodieStates.Length > 0;

            // Patch mode - requires output file
            if (output == null)
            {
                Console.Error.WriteLine("Error: Output file is required for patching.");
                Console.Error.WriteLine("Use --analyze for read-only analysis, or specify an output file.");
                return 1;
            }

            try
            {
                string inCanon = Path.GetFullPath(input.FullName);
                string outCanon = Path.GetFullPath(output.FullName);
                if (string.Equals(inCanon, outCanon, StringComparison.OrdinalIgnoreCase))
                {
                    Console.Error.WriteLine("Error: Output file must be different from input file. In-place patching is blocked.");
                    return 1;
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error: Unable to canonicalize input/output paths: {ex.Message}");
                return 1;
            }

            if (hasTargetedGoodieStates)
            {
                if (HasBroadPatchOptions(
                    useNew,
                    kills,
                    rank,
                    killsOnly,
                    noNodes,
                    noLinks,
                    noGoodies,
                    noKills,
                    allowCareerSectionsOnOptionsFile,
                    levelRanks,
                    aircraftKills,
                    vehicleKills,
                    emplacementKills,
                    infantryKills,
                    mechKills,
                    soundVolume,
                    musicVolume,
                    invertWalkerP1,
                    invertWalkerP2,
                    invertFlightP1,
                    invertFlightP2,
                    vibrationP1,
                    vibrationP2,
                    controllerConfigP1,
                    controllerConfigP2,
                    experimentalPendingExtraGoodies,
                    copyOptionsFrom,
                    noCopyOptionsEntries,
                    noCopyOptionsTail,
                    keybindOverrides))
                {
                    Console.Error.WriteLine("Error: --set-goodie-state is a narrow copied-save proof setup mode. Do not combine it with broad patch, settings, options, kill, rank, or keybind overrides.");
                    return 1;
                }

                if (!TryParseGoodieStateOverrides(setGoodieStates, out Dictionary<int, uint> overrides, out string error))
                {
                    Console.Error.WriteLine($"Error: {error}");
                    return 1;
                }

                PatchResult result = BesFilePatcher.PatchGoodieStates(input.FullName, output.FullName, overrides);
                Console.WriteLine(result.Message);
                if (result.Success)
                {
                    Console.WriteLine("Targeted Goodie state setup used true-view offsets and wrote only requested Goodie slots.");
                }

                return result.Success ? 0 : 1;
            }

            // Validate rank if specified
            string effectiveRank = rank?.ToUpper() ?? "S";
            var validRanks = new HashSet<string> { "S", "A", "B", "C", "D", "E", "NONE" };
            if (!validRanks.Contains(effectiveRank))
            {
                Console.Error.WriteLine($"Error: Invalid rank '{rank}'. Valid values: S, A, B, C, D, E, NONE");
                return 1;
            }

            // Parse per-level ranks
            Dictionary<int, string>? parsedLevelRanks = null;
            if (levelRanks != null && levelRanks.Length > 0)
            {
                parsedLevelRanks = new Dictionary<int, string>();
                var levelRankErrors = new List<string>();
                foreach (var entry in levelRanks)
                {
                    var parts = entry.Split(':');
                    if (parts.Length == 2 &&
                        int.TryParse(parts[0], out int level) &&
                        level >= 1 && level <= 43)
                    {
                        string levelRank = parts[1].ToUpper();
                        if (validRanks.Contains(levelRank))
                        {
                            // CLI contract is 1-based (1..43). Internally we patch zero-based node indexes.
                            parsedLevelRanks[level - 1] = levelRank;
                        }
                        else
                        {
                            levelRankErrors.Add($"Error: Invalid rank '{parts[1]}' for node index {level}. Valid values: S, A, B, C, D, E, NONE.");
                        }
                    }
                    else
                    {
                        levelRankErrors.Add($"Error: Invalid --level-rank entry '{entry}', expected NODE_INDEX:GRADE (e.g., 1:S).");
                    }
                }

                if (levelRankErrors.Count > 0)
                {
                    foreach (var err in levelRankErrors)
                        Console.Error.WriteLine(err);
                    return 1;
                }
            }

            // Build per-category kills dictionary
            Dictionary<int, int>? perCategoryKills = null;
            if (aircraftKills.HasValue || vehicleKills.HasValue || emplacementKills.HasValue ||
                infantryKills.HasValue || mechKills.HasValue)
            {
                perCategoryKills = new Dictionary<int, int>();
                if (aircraftKills.HasValue) perCategoryKills[BesFilePatcher.KILL_AIRCRAFT] = aircraftKills.Value;
                if (vehicleKills.HasValue) perCategoryKills[BesFilePatcher.KILL_VEHICLES] = vehicleKills.Value;
                if (emplacementKills.HasValue) perCategoryKills[BesFilePatcher.KILL_EMPLACEMENTS] = emplacementKills.Value;
                if (infantryKills.HasValue) perCategoryKills[BesFilePatcher.KILL_INFANTRY] = infantryKills.Value;
                if (mechKills.HasValue) perCategoryKills[BesFilePatcher.KILL_MECHS] = mechKills.Value;
            }

            // Configure patcher
            var patcher = new BesFilePatcher
            {
                UseNewGoodiesInstead = useNew,
                GlobalKillCount = kills ?? 100,
                Rank = effectiveRank,
                LevelRanks = parsedLevelRanks,
                PerCategoryKills = perCategoryKills,
                OptionsEntryOverrides = keybindOverrides
            };

            // Optional settings overrides (only written when explicitly set)
            try
            {
                patcher.SoundVolumeOverride = soundVolume.HasValue ? (float)soundVolume.Value : null;
                patcher.MusicVolumeOverride = musicVolume.HasValue ? (float)musicVolume.Value : null;
                patcher.InvertYAxisP1Override = ParseTriBool(invertWalkerP1, "--invert-walker-p1");
                patcher.InvertYAxisP2Override = ParseTriBool(invertWalkerP2, "--invert-walker-p2");
                patcher.InvertFlightP1Override = ParseTriBool(invertFlightP1, "--invert-flight-p1");
                patcher.InvertFlightP2Override = ParseTriBool(invertFlightP2, "--invert-flight-p2");
                patcher.VibrationP1Override = ParseTriBool(vibrationP1, "--vibration-p1");
                patcher.VibrationP2Override = ParseTriBool(vibrationP2, "--vibration-p2");
                patcher.ControllerConfigP1Override = controllerConfigP1;
                patcher.ControllerConfigP2Override = controllerConfigP2;
                if (experimentalPendingExtraGoodies.HasValue)
                {
                    Console.Error.WriteLine(
                        "Warning: --experimental-pending-extra-goodies is currently ignored for retail Steam until persistence semantics are re-verified.");
                }

                if (copyOptionsFrom != null)
                {
                    if (!copyOptionsFrom.Exists)
                    {
                        Console.Error.WriteLine($"Error: --copy-options-from file not found: {copyOptionsFrom.FullName}");
                        return 1;
                    }

                    patcher.CopyOptionsFromPath = copyOptionsFrom.FullName;
                    patcher.CopyOptionsEntries = !noCopyOptionsEntries;
                    patcher.CopyOptionsTail = !noCopyOptionsTail;
                    if (!patcher.CopyOptionsEntries && !patcher.CopyOptionsTail)
                    {
                        Console.Error.WriteLine("Error: --copy-options-from was provided, but both --no-copy-options-entries and --no-copy-options-tail were set (nothing to copy).");
                        return 1;
                    }
                }
            }
            catch (ArgumentException ex)
            {
                Console.Error.WriteLine(ex.Message);
                return 1;
            }

            // Handle selective patching flags
            if (killsOnly)
            {
                patcher.KillsOnly = true;
            }
            else
            {
                patcher.PatchNodes = !noNodes;
                patcher.PatchLinks = !noLinks;
                patcher.PatchGoodies = !noGoodies;
                patcher.PatchKills = !noKills;
            }

            bool inputOptionsLike = IsOptionsLikePath(input.FullName);
            bool outputOptionsLike = IsOptionsLikePath(output.FullName);
            bool careerSectionsEnabled = patcher.KillsOnly ||
                                         patcher.PatchNodes ||
                                         patcher.PatchLinks ||
                                         patcher.PatchGoodies ||
                                         patcher.PatchKills;

            if ((inputOptionsLike || outputOptionsLike) && careerSectionsEnabled)
            {
                if (!allowCareerSectionsOnOptionsFile)
                {
                    Console.Error.WriteLine(
                        "Error: Career section patching is blocked for .bea/defaultoptions files by default.");
                    Console.Error.WriteLine(
                        "Use settings-only mode (--no-nodes --no-links --no-goodies --no-kills),");
                    Console.Error.WriteLine(
                        "or pass --allow-career-sections-on-options-file to override intentionally.");
                    return 1;
                }

                Console.Error.WriteLine(
                    "Warning: Applying career section patching to an options-style file (.bea/defaultoptions).");
            }

            // Show configuration
            Console.WriteLine("Onslaught Career Editor - CLI Mode");
            Console.WriteLine("===================================");
            Console.WriteLine($"Input:  {input.FullName}");
            Console.WriteLine($"Output: {output.FullName}");
            Console.WriteLine();
            Console.WriteLine("Configuration:");
            Console.WriteLine($"  Rank:           {patcher.Rank}");
            Console.WriteLine($"  Kill count:     {patcher.GlobalKillCount}");
            Console.WriteLine($"  Goodies style:  {(patcher.UseNewGoodiesInstead ? "NEW (gold)" : "OLD (blue)")}");
            Console.WriteLine($"  Patch nodes:    {(patcher.PatchNodes ? "Yes" : "No")}");
            Console.WriteLine($"  Patch links:    {(patcher.PatchLinks ? "Yes" : "No")}");
            Console.WriteLine($"  Patch goodies:  {(patcher.PatchGoodies ? "Yes" : "No")}");
            Console.WriteLine($"  Patch kills:    {(patcher.PatchKills ? "Yes" : "No")}");

            if (patcher.SoundVolumeOverride.HasValue)
                Console.WriteLine($"  Sound volume:   {patcher.SoundVolumeOverride.Value:0.###}");
            if (patcher.MusicVolumeOverride.HasValue)
                Console.WriteLine($"  Music volume:   {patcher.MusicVolumeOverride.Value:0.###}");
            if (patcher.InvertYAxisP1Override.HasValue)
                Console.WriteLine($"  Invert Y (Walker) (P1): {(patcher.InvertYAxisP1Override.Value ? "On" : "Off")}");
            if (patcher.InvertYAxisP2Override.HasValue)
                Console.WriteLine($"  Invert Y (Walker) (P2): {(patcher.InvertYAxisP2Override.Value ? "On" : "Off")}");
            if (patcher.InvertFlightP1Override.HasValue)
                Console.WriteLine($"  Invert Y (Flight) (P1): {(patcher.InvertFlightP1Override.Value ? "On" : "Off")}");
            if (patcher.InvertFlightP2Override.HasValue)
                Console.WriteLine($"  Invert Y (Flight) (P2): {(patcher.InvertFlightP2Override.Value ? "On" : "Off")}");
            if (patcher.VibrationP1Override.HasValue)
                Console.WriteLine($"  Vibration (P1): {(patcher.VibrationP1Override.Value ? "On" : "Off")}");
            if (patcher.VibrationP2Override.HasValue)
                Console.WriteLine($"  Vibration (P2): {(patcher.VibrationP2Override.Value ? "On" : "Off")}");
            if (patcher.ControllerConfigP1Override.HasValue)
                Console.WriteLine($"  Ctrl cfg (P1):  {patcher.ControllerConfigP1Override.Value}");
            if (patcher.ControllerConfigP2Override.HasValue)
                Console.WriteLine($"  Ctrl cfg (P2):  {patcher.ControllerConfigP2Override.Value}");
            if (!string.IsNullOrWhiteSpace(patcher.CopyOptionsFromPath))
            {
                Console.WriteLine($"  Copy options from: {patcher.CopyOptionsFromPath}");
                Console.WriteLine($"    - entries: {(patcher.CopyOptionsEntries ? "Yes" : "No")}");
                Console.WriteLine($"    - tail:    {(patcher.CopyOptionsTail ? "Yes" : "No")}");
            }
            if (patcher.OptionsEntryOverrides != null && patcher.OptionsEntryOverrides.Count > 0)
            {
                Console.WriteLine($"  Keybind overrides: {patcher.OptionsEntryOverrides.Count} entries");
                Console.WriteLine("    NOTE: ControlSchemeIndex is forced to 0 (Custom) when applying keybind overrides.");
            }

            if (parsedLevelRanks != null && parsedLevelRanks.Count > 0)
            {
                Console.WriteLine($"  Level overrides: {parsedLevelRanks.Count} levels");
            }

            if (perCategoryKills != null && perCategoryKills.Count > 0)
            {
                Console.WriteLine("  Per-category kills:");
                if (perCategoryKills.TryGetValue(BesFilePatcher.KILL_AIRCRAFT, out int ac))
                    Console.WriteLine($"    Aircraft:     {ac}");
                if (perCategoryKills.TryGetValue(BesFilePatcher.KILL_VEHICLES, out int vc))
                    Console.WriteLine($"    Vehicles:     {vc}");
                if (perCategoryKills.TryGetValue(BesFilePatcher.KILL_EMPLACEMENTS, out int ec))
                    Console.WriteLine($"    Emplacements: {ec}");
                if (perCategoryKills.TryGetValue(BesFilePatcher.KILL_INFANTRY, out int ic))
                    Console.WriteLine($"    Infantry:     {ic}");
                if (perCategoryKills.TryGetValue(BesFilePatcher.KILL_MECHS, out int mc))
                    Console.WriteLine($"    Mechs:        {mc}");
            }

            Console.WriteLine();

            // Perform patching
            try
            {
                var patchResult = patcher.PatchFile(input.FullName, output.FullName);
                Console.WriteLine(patchResult.Message);
                if (patchResult.Success)
                {
                    PrintPatchSummary(patcher, output.FullName, parsedLevelRanks, perCategoryKills);
                }
                return patchResult.Success ? 0 : 1;
            }
            catch (IOException ex)
            {
                Console.Error.WriteLine($"Error: Failed to access file: {ex.Message}");
                return 1;
            }
            catch (UnauthorizedAccessException ex)
            {
                Console.Error.WriteLine($"Error: Access denied: {ex.Message}");
                return 1;
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error: {ex.Message}");
                return 1;
            }
        }

        /// <summary>
        /// Handle configuration management commands.
        /// </summary>
        private static int HandleConfigCommands(bool listSaves, string? setGameDir, bool showConfig)
        {
            var config = AppConfig.Load();

            // Set game directory
            if (setGameDir != null)
            {
                if (Directory.Exists(setGameDir))
                {
                    if (!config.SetGameDir(setGameDir))
                    {
                        Console.Error.WriteLine($"Error: Failed to persist game directory: {setGameDir}");
                        return 1;
                    }
                    Console.WriteLine($"Game directory set to: {setGameDir}");
                }
                else
                {
                    Console.Error.WriteLine($"Error: Directory not found: {setGameDir}");
                    return 1;
                }
            }

            // Show configuration
            if (showConfig)
            {
                Console.WriteLine("Onslaught Career Editor - Configuration");
                Console.WriteLine("=======================================");
                Console.WriteLine($"Config file: {AppConfig.GetConfigPath()}");
                Console.WriteLine();

                string? gameDir = config.GetGameDir();
                string? detectedDir = AppConfig.DetectGameDirectory();

                Console.WriteLine($"Game directory:     {gameDir ?? "(not set)"}");
                Console.WriteLine($"Auto-detected:      {detectedDir ?? "(not found)"}");
                Console.WriteLine($"Max recent files:   {config.MaxRecentFiles}");
                Console.WriteLine($"Window size:        {config.WindowWidth}x{config.WindowHeight}");
                Console.WriteLine($"Last tab:           {config.LastTab}");

                if (config.RecentFiles.Count > 0)
                {
                    Console.WriteLine();
                    Console.WriteLine($"Recent files ({config.RecentFiles.Count}):");
                    foreach (var file in config.RecentFiles)
                    {
                        bool exists = File.Exists(file);
                        Console.WriteLine($"  {(exists ? "[OK]" : "[X]")} {file}");
                    }
                }
            }

            // List save files
            if (listSaves)
            {
                string? effectiveDir = config.GetGameDir() ?? AppConfig.DetectGameDirectory();

                Console.WriteLine("Onslaught Career Editor - Save Files");
                Console.WriteLine("====================================");

                if (effectiveDir == null)
                {
                    Console.WriteLine("Game directory not configured and could not be auto-detected.");
                    Console.WriteLine("Use --set-game-dir <path> to specify the game installation folder.");
                    return 1;
                }

                Console.WriteLine($"Searching in: {effectiveDir}");
                Console.WriteLine();

                var saves = AppConfig.FindSaveFiles(effectiveDir);

                if (saves.Count == 0)
                {
                    Console.WriteLine("No .bes/.bea save/options files found.");
            return 0;
        }

                Console.WriteLine($"Found {saves.Count} save file(s):");
                Console.WriteLine();
                Console.WriteLine($"{"Name",-30} {"Size",-12} {"Modified",-20} {"Valid"}");
                Console.WriteLine(new string('-', 70));

                foreach (var save in saves)
                {
                    string sizeStr = save.Size == 10004 ? "10,004 B" : $"{save.Size:N0} B";
                    string validStr = save.IsValid ? "Yes" : "No*";
                    Console.WriteLine($"{save.Name,-30} {sizeStr,-12} {save.Modified:yyyy-MM-dd HH:mm,-20} {validStr}");
                }

                Console.WriteLine();
                Console.WriteLine("Paths:");
                foreach (var save in saves)
                {
                    Console.WriteLine($"  {save.Path}");
                }
                Console.WriteLine();
                Console.WriteLine($"* Invalid format: expected {BesFilePatcher.EXPECTED_FILE_SIZE:N0} bytes and version word 0x{BesFilePatcher.VERSION_WORD:X4}");
            }

	            return 0;
	        }

        private static int HandleAssetMaterialImportManifest(
            string catalogPathOrDirectory,
            bool failOnUnresolvedMaterialBindings)
        {
            string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(catalogPathOrDirectory);
            if (catalogFilePath is null)
            {
                Console.Error.WriteLine("Error: Generated asset catalog was not found at the supplied path or directory.");
                return 1;
            }

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);
            var payload = new
            {
                schemaVersion = AssetMaterialImportManifestSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-import-manifest",
                mutation = false,
                input = new
                {
                    catalogFileName = Path.GetFileName(catalogFilePath),
                    failOnUnresolvedMaterialBindings
                },
                catalog = new
                {
                    totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                    textureRows = snapshot.Summary.TextureCount,
                    looseMeshRows = snapshot.Summary.LooseMeshCount,
                    embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
                },
                materialImportManifest = manifest,
                gate = new
                {
                    passed = manifest.UnresolvedTextureBindingRows == 0,
                    unresolvedTextureBindingRows = manifest.UnresolvedTextureBindingRows,
                    failOnUnresolvedMaterialBindings
                },
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialImportManifestSchemaVersion,
                    note = "Read-only material-import manifest payload. It contains sanitized catalog IDs, labels, and file names only; full local paths and private asset payloads are intentionally omitted."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return failOnUnresolvedMaterialBindings && manifest.UnresolvedTextureBindingRows > 0 ? 1 : 0;
        }

        private static int HandleAssetMaterialImportDryRunPlan(
            string catalogPathOrDirectory,
            bool failOnUnresolvedMaterialBindings)
        {
            string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(catalogPathOrDirectory);
            if (catalogFilePath is null)
            {
                Console.Error.WriteLine("Error: Generated asset catalog was not found at the supplied path or directory.");
                return 1;
            }

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);
            AssetMaterialImportDryRunPlan dryRunPlan = new AssetMaterialImportDryRunPlanService().Build(manifest);
            var payload = new
            {
                schemaVersion = AssetMaterialImportDryRunPlanSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-import-dry-run-plan",
                mutation = false,
                input = new
                {
                    catalogFileName = Path.GetFileName(catalogFilePath),
                    failOnUnresolvedMaterialBindings
                },
                catalog = new
                {
                    totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                    textureRows = snapshot.Summary.TextureCount,
                    looseMeshRows = snapshot.Summary.LooseMeshCount,
                    embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
                },
                materialImportDryRunPlan = dryRunPlan,
                gate = new
                {
                    passed = dryRunPlan.UnresolvedTextureOperations == 0,
                    unresolvedTextureOperations = dryRunPlan.UnresolvedTextureOperations,
                    blockedModelOperations = dryRunPlan.BlockedModelOperations,
                    failOnUnresolvedMaterialBindings
                },
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialImportDryRunPlanSchemaVersion,
                    note = "Read-only material-import dry-run plan. It emits deterministic relative operations only; no asset bytes are copied and no full local paths are included."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return failOnUnresolvedMaterialBindings && dryRunPlan.UnresolvedTextureOperations > 0 ? 1 : 0;
        }

        private static int HandleAssetMaterialImportPackagePlan(
            string catalogPathOrDirectory,
            bool failOnUnresolvedMaterialBindings)
        {
            string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(catalogPathOrDirectory);
            if (catalogFilePath is null)
            {
                Console.Error.WriteLine("Error: Generated asset catalog was not found at the supplied path or directory.");
                return 1;
            }

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);
            AssetMaterialImportPackagePlan packagePlan = new AssetMaterialImportPackagePlanService().Build(manifest);
            var payload = new
            {
                schemaVersion = AssetMaterialImportPackagePlanSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-import-package-plan",
                mutation = false,
                input = new
                {
                    catalogFileName = Path.GetFileName(catalogFilePath),
                    failOnUnresolvedMaterialBindings
                },
                catalog = new
                {
                    totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                    textureRows = snapshot.Summary.TextureCount,
                    looseMeshRows = snapshot.Summary.LooseMeshCount,
                    embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
                },
                materialImportPackagePlan = packagePlan,
                gate = new
                {
                    passed = packagePlan.UnresolvedTextureReferences == 0 && packagePlan.BlockedPackageModelOperations == 0,
                    unresolvedTextureReferences = packagePlan.UnresolvedTextureReferences,
                    blockedPackageModelOperations = packagePlan.BlockedPackageModelOperations,
                    failOnUnresolvedMaterialBindings
                },
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialImportPackagePlanSchemaVersion,
                    note = "Read-only material-import package plan. It emits deterministic package-relative file entries only; no asset bytes are copied and no full local paths are included."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return failOnUnresolvedMaterialBindings &&
                   (packagePlan.UnresolvedTextureReferences > 0 || packagePlan.BlockedPackageModelOperations > 0)
                ? 1
                : 0;
        }

        private static int HandleAssetMaterialImportPackageMaterialization(
            string catalogPathOrDirectory,
            string? outputDirectory,
            bool explicitPreflight,
            string? armPrivateAssetOutput)
        {
            if (string.IsNullOrWhiteSpace(outputDirectory))
            {
                Console.Error.WriteLine("Error: --asset-material-package-output is required for package materialization.");
                return 1;
            }

            bool executeCopy = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
            if (executeCopy && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
            {
                Console.Error.WriteLine("Error: Refusing to copy private asset bytes: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
                return 1;
            }

            string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(catalogPathOrDirectory);
            if (catalogFilePath is null)
            {
                Console.Error.WriteLine("Error: Generated asset catalog was not found at the supplied path or directory.");
                return 1;
            }

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
            AssetMaterialImportPackageMaterializationService service = new();
            AssetMaterialImportPackageMaterializationResult result = executeCopy
                ? service.Materialize(snapshot, outputDirectory)
                : service.Preflight(snapshot, outputDirectory);
            var payload = new
            {
                schemaVersion = AssetMaterialImportPackageMaterializationSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-import-package-materialize",
                mode = executeCopy ? "copy" : "preflight",
                mutation = executeCopy,
                input = new
                {
                    catalogFileName = Path.GetFileName(catalogFilePath),
                    outputRootName = BuildOutputRootName(outputDirectory),
                    explicitPreflight,
                    armedPrivateAssetOutput = executeCopy
                },
                catalog = new
                {
                    totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                    textureRows = snapshot.Summary.TextureCount,
                    looseMeshRows = snapshot.Summary.LooseMeshCount,
                    embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
                },
                materialImportPackageMaterialization = result,
                artifact = new
                {
                    kind = "app-owned-private-output",
                    mutation = executeCopy,
                    originalGameMutation = false,
                    schemaVersion = AssetMaterialImportPackageMaterializationSchemaVersion,
                    note = executeCopy
                        ? "Copies ready model and texture exports into the supplied output root using package-relative destinations; no installed game files or original executable bytes are modified, and raw source paths are omitted from this JSON."
                        : "Preflights ready model and texture package output using package-relative destinations only; no asset bytes are copied, no output root is created, and raw source paths are omitted from this JSON."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return result.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageInspection(string packageRoot)
        {
            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageInspectionSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-inspect",
                mutation = false,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot)
                },
                materialPackageInspection = inspection,
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialPackageInspectionSchemaVersion,
                    note = "Read-only material package inspection. Validates the package manifest and package-relative payload files; raw local paths are omitted from this JSON."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return inspection.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageWorkOrder(string packageRoot)
        {
            AssetMaterialImportPackageWorkOrderResult workOrder =
                new AssetMaterialImportPackageWorkOrderService().Build(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageWorkOrderSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-work-order",
                mutation = false,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot)
                },
                materialPackageWorkOrder = workOrder,
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialPackageWorkOrderSchemaVersion,
                    note = "Read-only material package work order. Converts a validated package manifest into package-relative importer/rebuild tasks; raw local paths are omitted from this JSON."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return workOrder.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageWorkOrderSidecarValidation(string packageRoot)
        {
            AssetMaterialImportPackageWorkOrderSidecarValidationResult validation =
                new AssetMaterialImportPackageWorkOrderService().ValidateSidecar(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageWorkOrderSidecarValidationSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-work-order-sidecar-validate",
                mutation = false,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot)
                },
                materialPackageWorkOrderSidecarValidation = validation,
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialPackageWorkOrderSidecarValidationSchemaVersion,
                    note = "Read-only material package work-order sidecar validation. Reads the saved sidecar and rejects stale or path-leaking importer/rebuild tasks by comparing them with a fresh package-relative work-order build."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return validation.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageImporterBatch(string packageRoot)
        {
            AssetMaterialImportPackageImporterBatchResult batch =
                new AssetMaterialImportPackageImporterBatchService().Build(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageImporterBatchSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-importer-batch",
                mutation = false,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot)
                },
                materialPackageImporterBatch = batch,
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialPackageImporterBatchSchemaVersion,
                    note = "Read-only material package importer batch. Consumes only a validated package work-order sidecar and emits flat package-relative model/texture task rows for future importer/rebuild tooling."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return batch.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageImporterDryRun(string packageRoot)
        {
            AssetMaterialImportPackageImporterDryRunResult dryRun =
                new AssetMaterialImportPackageImporterDryRunService().Build(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageImporterDryRunSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-importer-dry-run",
                mutation = false,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot)
                },
                materialPackageImporterDryRun = dryRun,
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialPackageImporterDryRunSchemaVersion,
                    note = "Read-only material package importer dry-run. Consumes a validated importer batch and emits package-relative adapter rows for future importer/rebuild tooling."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return dryRun.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageImporterDryRunSidecarValidate(string packageRoot)
        {
            AssetMaterialImportPackageImporterDryRunSidecarValidationResult validation =
                new AssetMaterialImportPackageImporterDryRunService().ValidateSidecar(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageImporterDryRunSidecarValidationSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-importer-dry-run-sidecar-validate",
                mutation = false,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot)
                },
                materialPackageImporterDryRunSidecarValidation = validation,
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialPackageImporterDryRunSidecarValidationSchemaVersion,
                    note = "Read-only material package importer dry-run sidecar validation. Reads the saved adapter sidecar and rejects stale or path-leaking importer/rebuild rows by comparing them with a fresh package-relative importer dry-run build."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return validation.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageImporterInputMaterialization(
            string packageRoot,
            bool explicitPreflight,
            string? armPrivateAssetOutput)
        {
            bool executeCopy = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
            if (executeCopy && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
            {
                Console.Error.WriteLine("Error: Refusing to stage private asset bytes: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
                return 1;
            }

            AssetMaterialImportPackageImporterInputService service = new();
            AssetMaterialImportPackageImporterInputMaterializationResult result = executeCopy
                ? service.Materialize(packageRoot)
                : service.Preflight(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageImporterInputMaterializationSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-importer-input-materialize",
                mode = executeCopy ? "copy" : "preflight",
                mutation = executeCopy,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot),
                    explicitPreflight,
                    armedPrivateAssetOutput = executeCopy
                },
                materialPackageImporterInputMaterialization = result,
                artifact = new
                {
                    kind = executeCopy ? "app-owned-materialization" : "preflight",
                    mutation = executeCopy,
                    originalGameMutation = false,
                    schemaVersion = AssetMaterialPackageImporterInputMaterializationSchemaVersion,
                    note = executeCopy
                        ? "Copies validated package-local model/texture payloads into importer-input using package-relative adapter paths; no installed game files or original executable bytes are modified."
                        : "Preflights importer-input staging from a validated package-local dry-run sidecar; no files are copied and no original game files are touched."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return result.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageImporterInputPlan(string packageRoot)
        {
            AssetMaterialImportPackageImporterInputPlanResult plan =
                new AssetMaterialImportPackageImporterInputPlanService().Build(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageImporterInputPlanSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-importer-input-plan",
                mutation = false,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot)
                },
                materialPackageImporterInputPlan = plan,
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = AssetMaterialPackageImporterInputPlanSchemaVersion,
                    note = "Builds a read-only importer/rebuild consumer plan from package-local importer-input files. It validates staged FBX/PNG readability and emits model-import and texture-bind jobs without running an importer, renderer, game executable, or Godot."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return plan.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageRebuildPreviewMaterialization(
            string packageRoot,
            bool explicitPreflight,
            string? armPrivateAssetOutput)
        {
            bool executeWrite = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
            if (executeWrite && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
            {
                Console.Error.WriteLine("Error: Refusing to write rebuild preview outputs: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
                return 1;
            }

            AssetMaterialImportPackageRebuildPreviewService service = new();
            AssetMaterialImportPackageRebuildPreviewResult result = executeWrite
                ? service.Materialize(packageRoot)
                : service.Preflight(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageRebuildPreviewMaterializationSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-rebuild-preview-materialize",
                mode = executeWrite ? "write" : "preflight",
                mutation = executeWrite,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot),
                    explicitPreflight,
                    armedPrivateAssetOutput = executeWrite
                },
                materialPackageRebuildPreview = result,
                artifact = new
                {
                    kind = executeWrite ? "app-owned-rebuild-preview" : "preflight",
                    mutation = executeWrite,
                    originalGameMutation = false,
                    schemaVersion = AssetMaterialPackageRebuildPreviewMaterializationSchemaVersion,
                    note = executeWrite
                        ? "Writes deterministic OBJ wireframe preview files and binding sidecars from staged importer-input files under the app-owned package output. It does not launch the game, run a renderer, execute Godot, or claim rebuild parity."
                        : "Preflights deterministic OBJ wireframe preview and binding sidecar output from staged importer-input files. No files are written and no original game files are touched."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return result.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageRebuildSceneMaterialization(
            string packageRoot,
            bool explicitPreflight,
            string? armPrivateAssetOutput)
        {
            bool executeWrite = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
            if (executeWrite && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
            {
                Console.Error.WriteLine("Error: Refusing to write rebuild scene contract outputs: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
                return 1;
            }

            AssetMaterialImportPackageRebuildSceneService service = new();
            AssetMaterialImportPackageRebuildSceneResult result = executeWrite
                ? service.Materialize(packageRoot)
                : service.Preflight(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageRebuildSceneMaterializationSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-rebuild-scene-materialize",
                mode = executeWrite ? "write" : "preflight",
                mutation = executeWrite,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot),
                    explicitPreflight,
                    armedPrivateAssetOutput = executeWrite
                },
                materialPackageRebuildScene = result,
                artifact = new
                {
                    kind = executeWrite ? "app-owned-rebuild-scene-contract" : "preflight",
                    mutation = executeWrite,
                    originalGameMutation = false,
                    schemaVersion = AssetMaterialPackageRebuildSceneMaterializationSchemaVersion,
                    note = executeWrite
                        ? "Writes deterministic package-relative scene/mesh/material contract JSON from staged importer-input and rebuild-preview files. It does not launch the game, run a renderer, execute Godot, convert full meshes, or claim rebuild parity."
                        : "Preflights package-relative scene/mesh/material contract output from staged importer-input and rebuild-preview files. No files are written and no original game files are touched."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return result.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageRebuildMeshMaterialization(
            string packageRoot,
            bool explicitPreflight,
            string? armPrivateAssetOutput)
        {
            bool executeWrite = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
            if (executeWrite && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
            {
                Console.Error.WriteLine("Error: Refusing to write rebuild mesh outputs: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
                return 1;
            }

            AssetMaterialImportPackageRebuildMeshService service = new();
            AssetMaterialImportPackageRebuildMeshResult result = executeWrite
                ? service.Materialize(packageRoot)
                : service.Preflight(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageRebuildMeshMaterializationSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-rebuild-mesh-materialize",
                mode = executeWrite ? "write" : "preflight",
                mutation = executeWrite,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot),
                    explicitPreflight,
                    armedPrivateAssetOutput = executeWrite
                },
                materialPackageRebuildMesh = result,
                artifact = new
                {
                    kind = executeWrite ? "app-owned-rebuild-mesh" : "preflight",
                    mutation = executeWrite,
                    originalGameMutation = false,
                    schemaVersion = AssetMaterialPackageRebuildMeshMaterializationSchemaVersion,
                    note = executeWrite
                        ? "Writes deterministic package-relative OBJ/MTL mesh outputs from existing rebuild-scene contracts and staged FBX data. It does not launch the game, run a renderer, execute Godot, animate meshes, or claim rebuild parity."
                        : "Preflights package-relative OBJ/MTL mesh output from existing rebuild-scene contracts and staged FBX data. No files are written and no original game files are touched."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return result.Completed ? 0 : 1;
        }

        private static int HandleAssetMaterialPackageRebuildMeshImportMaterialization(
            string packageRoot,
            bool explicitPreflight,
            string? armPrivateAssetOutput)
        {
            bool executeWrite = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
            if (executeWrite && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
            {
                Console.Error.WriteLine("Error: Refusing to write rebuild mesh import contract: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
                return 1;
            }

            AssetMaterialImportPackageRebuildMeshImportService service = new();
            AssetMaterialImportPackageRebuildMeshImportResult result = executeWrite
                ? service.Materialize(packageRoot)
                : service.Preflight(packageRoot);
            var payload = new
            {
                schemaVersion = AssetMaterialPackageRebuildMeshImportSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "asset-material-package-rebuild-mesh-import-materialize",
                mode = executeWrite ? "write" : "preflight",
                mutation = executeWrite,
                input = new
                {
                    packageRootName = BuildOutputRootName(packageRoot),
                    explicitPreflight,
                    armedPrivateAssetOutput = executeWrite
                },
                materialPackageRebuildMeshImport = result,
                artifact = new
                {
                    kind = executeWrite ? "app-owned-rebuild-mesh-import-contract" : "preflight",
                    mutation = executeWrite,
                    originalGameMutation = false,
                    schemaVersion = AssetMaterialPackageRebuildMeshImportSchemaVersion,
                    note = executeWrite
                        ? "Writes a deterministic package-relative import validation manifest after parsing the generated OBJ/MTL rebuild mesh outputs and validating mesh counts, material references, and staged texture paths. It does not launch the game, run a renderer, execute Godot, or claim rebuild parity."
                        : "Preflights generated OBJ/MTL rebuild mesh outputs as importer-consumable package-local data. No files are written and no original game files are touched."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return result.Completed ? 0 : 1;
        }

        private static string BuildOutputRootName(string outputRoot)
        {
            string fullPath = Path.GetFullPath(outputRoot)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            return Path.GetFileName(fullPath);
        }

	        private static int PrintGoodieList(string inputPath, bool showReservedGoodies)
	        {
	            const int careerBase = 0x0002;
	            const int ccareerGoodieBase = 0x1F44;
	            const int goodieBase = careerBase + ccareerGoodieBase; // 0x1F46 in file space
	            const int goodieCount = 300;
	            const int displayableCount = 233;

	            const uint GOODIE_UNKNOWN = 0;
	            const uint GOODIE_INSTRUCTIONS = 1;
	            const uint GOODIE_NEW = 2;
	            const uint GOODIE_OLD = 3;

	            static string classify(int index, uint raw)
	            {
	                if (index >= displayableCount) return "RESERVED";
	                if (raw == GOODIE_NEW) return "NEW";
	                if (raw == GOODIE_OLD) return "OLD";
	                if (raw == GOODIE_UNKNOWN) return "LOCKED";
	                if (raw == GOODIE_INSTRUCTIONS) return "INSTRUCTIONS";
	                return "OTHER";
	            }

	            try
	            {
	                var buf = File.ReadAllBytes(inputPath);
	                if (buf.Length != BesFilePatcher.EXPECTED_FILE_SIZE)
	                {
	                    Console.Error.WriteLine(
	                        $"Error: Invalid file size {buf.Length:N0} bytes (expected {BesFilePatcher.EXPECTED_FILE_SIZE:N0}).");
	                    return 1;
	                }

	                ushort versionWord = BinaryPrimitives.ReadUInt16LittleEndian(buf.AsSpan(0, 2));
	                if (versionWord != BesFilePatcher.VERSION_WORD)
	                {
	                    Console.Error.WriteLine(
	                        $"Error: Invalid version word 0x{versionWord:X4} (expected 0x{BesFilePatcher.VERSION_WORD:X4}).");
	                    return 1;
	                }

	                int countNew = 0, countOld = 0, countLocked = 0, countInstructions = 0, countOther = 0, countReserved = 0;

	                Console.WriteLine("Onslaught Career Editor - Goodie List");
	                Console.WriteLine("=====================================");
	                Console.WriteLine($"File: {inputPath}");
	                Console.WriteLine($"Version: 0x{versionWord:X4}");
	                Console.WriteLine($"Display mode: {(showReservedGoodies ? "all 300 slots" : "displayable slots (0-232)")}");
	                Console.WriteLine();
	                Console.WriteLine($"{"Idx",4} {"Offset",8} {"State",-13} {"Raw",-10} {"Scope",-11}");
	                Console.WriteLine(new string('-', 52));

	                for (int i = 0; i < goodieCount; i++)
	                {
	                    int off = goodieBase + i * 4;
	                    uint raw = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off, 4));
	                    string state = classify(i, raw);
	                    bool reserved = i >= displayableCount;
	                    string scope = reserved ? "Reserved" : "Displayable";

	                    switch (state)
	                    {
	                        case "NEW": countNew++; break;
	                        case "OLD": countOld++; break;
	                        case "LOCKED": countLocked++; break;
	                        case "INSTRUCTIONS": countInstructions++; break;
	                        case "OTHER": countOther++; break;
	                        case "RESERVED": countReserved++; break;
	                    }

	                    if (!showReservedGoodies && reserved)
	                        continue;

	                    Console.WriteLine($"{i,4} 0x{off:X4} {state,-13} 0x{raw:X8} {scope,-11}");
	                }

	                int unlocked = countNew + countOld;
	                Console.WriteLine();
	                Console.WriteLine("Summary (displayable slots 0-232):");
	                Console.WriteLine($"  Unlocked: {unlocked}/{displayableCount} (NEW {countNew}, OLD {countOld})");
	                Console.WriteLine($"  Locked: {countLocked}");
	                Console.WriteLine($"  Instructions: {countInstructions}");
	                if (countOther > 0)
	                    Console.WriteLine($"  Other: {countOther}");
	                Console.WriteLine($"  Reserved slots: {countReserved}");
	                if (!showReservedGoodies)
	                    Console.WriteLine("  Note: Reserved rows hidden; use --show-reserved-goodies to include them.");

	                return 0;
	            }
	            catch (IOException ex)
	            {
	                Console.Error.WriteLine($"Error: Failed to access file: {ex.Message}");
	                return 1;
	            }
	            catch (UnauthorizedAccessException ex)
	            {
	                Console.Error.WriteLine($"Error: Access denied: {ex.Message}");
	                return 1;
	            }
	            catch (Exception ex)
	            {
	                Console.Error.WriteLine($"Error: {ex.Message}");
	                return 1;
            }
        }

        private static bool HasBroadPatchOptions(
            bool useNew,
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
            Dictionary<int, BesFilePatcher.OptionsEntryOverride>? keybindOverrides)
        {
            return useNew ||
                   kills.HasValue ||
                   !string.IsNullOrWhiteSpace(rank) ||
                   killsOnly ||
                   noNodes ||
                   noLinks ||
                   noGoodies ||
                   noKills ||
                   allowCareerSectionsOnOptionsFile ||
                   (levelRanks != null && levelRanks.Length > 0) ||
                   aircraftKills.HasValue ||
                   vehicleKills.HasValue ||
                   emplacementKills.HasValue ||
                   infantryKills.HasValue ||
                   mechKills.HasValue ||
                   soundVolume.HasValue ||
                   musicVolume.HasValue ||
                   !string.IsNullOrWhiteSpace(invertWalkerP1) ||
                   !string.IsNullOrWhiteSpace(invertWalkerP2) ||
                   !string.IsNullOrWhiteSpace(invertFlightP1) ||
                   !string.IsNullOrWhiteSpace(invertFlightP2) ||
                   !string.IsNullOrWhiteSpace(vibrationP1) ||
                   !string.IsNullOrWhiteSpace(vibrationP2) ||
                   controllerConfigP1.HasValue ||
                   controllerConfigP2.HasValue ||
                   experimentalPendingExtraGoodies.HasValue ||
                   copyOptionsFrom != null ||
                   noCopyOptionsEntries ||
                   noCopyOptionsTail ||
                   (keybindOverrides != null && keybindOverrides.Count > 0);
        }

        private static bool TryParseGoodieStateOverrides(
            string[]? entries,
            out Dictionary<int, uint> overrides,
            out string error)
        {
            overrides = new Dictionary<int, uint>();
            error = string.Empty;

            if (entries == null || entries.Length == 0)
            {
                error = "Choose at least one --set-goodie-state INDEX:STATE override.";
                return false;
            }

            foreach (string rawEntry in entries)
            {
                string entry = rawEntry.Trim();
                string[] parts = entry.Split(':', 2, StringSplitOptions.TrimEntries);
                if (parts.Length != 2 ||
                    !int.TryParse(parts[0], NumberStyles.Integer, CultureInfo.InvariantCulture, out int index))
                {
                    error = $"Invalid --set-goodie-state entry '{entry}'. Expected INDEX:STATE, for example 71:new.";
                    return false;
                }

                if (!TryParseGoodieState(parts[1], out uint state))
                {
                    error = $"Invalid Goodie state '{parts[1]}' for index {index}. Use 0, 1, 2, 3, locked, instructions, new, or old.";
                    return false;
                }

                overrides[index] = state;
            }

            return true;
        }

        private static bool TryParseGoodieState(string rawState, out uint state)
        {
            string normalized = rawState.Trim().ToLowerInvariant();
            switch (normalized)
            {
                case "0":
                case "locked":
                case "none":
                    state = 0;
                    return true;
                case "1":
                case "instructions":
                case "instruction":
                    state = 1;
                    return true;
                case "2":
                case "new":
                    state = 2;
                    return true;
                case "3":
                case "old":
                case "viewed":
                    state = 3;
                    return true;
                default:
                    state = 0;
                    return false;
            }
        }

        private static bool? ParseTriBool(string? value, string optionName)
        {
            if (string.IsNullOrWhiteSpace(value))
                return null;

            string v = value.Trim().ToLowerInvariant();
            if (v is "keep" or "preserve" or "unchanged")
                return null;
            if (v is "1" or "true" or "on" or "yes" or "y")
                return true;
            if (v is "0" or "false" or "off" or "no" or "n")
                return false;

            throw new ArgumentException(
                $"Error: Invalid value '{value}' for {optionName}. " +
                "Use on/off/true/false/1/0/yes/no/y/n, or omit to preserve the existing save value."
            );
        }

        private static bool IsOptionsLikePath(string? filePath)
        {
            if (string.IsNullOrWhiteSpace(filePath))
                return false;

            string trimmed = filePath.Trim();
            string fileNameOnly = Path.GetFileName(trimmed);
            return string.Equals(Path.GetExtension(trimmed), ".bea", StringComparison.OrdinalIgnoreCase) ||
                   fileNameOnly.StartsWith("defaultoptions.bea", StringComparison.OrdinalIgnoreCase);
        }

        private static Dictionary<int, BesFilePatcher.OptionsEntryOverride>? ParseKeybindOverridesFromCli(
            string[]? moveForward,
            string[]? moveBackward,
            string[]? moveLeft,
            string[]? moveRight,
            string[]? lookUp,
            string[]? lookDown,
            string[]? lookLeft,
            string[]? lookRight,
            string[]? zoomIn,
            string[]? zoomOut,
            string[]? fireWeapon,
            string[]? selectWeapon,
            string[]? transform,
            string[]? airBrake,
            string[]? special)
        {
            static bool isKeep(string? s)
            {
                if (string.IsNullOrWhiteSpace(s))
                    return true;
                string t = s.Trim();
                return t.Equals("keep", StringComparison.OrdinalIgnoreCase) ||
                       t.Equals("preserve", StringComparison.OrdinalIgnoreCase) ||
                       t.Equals("unchanged", StringComparison.OrdinalIgnoreCase);
            }

            var dict = new Dictionary<int, BesFilePatcher.OptionsEntryOverride>();

            void setSlot(int entryId, int slotIndex, uint deviceCode, uint packedKey)
            {
                if (!dict.TryGetValue(entryId, out var ov))
                {
                    ov = new BesFilePatcher.OptionsEntryOverride();
                    dict[entryId] = ov;
                }

                var slot = slotIndex == 0 ? ov.Slot0 : ov.Slot1;
                slot.DeviceCode = deviceCode;
                slot.PackedKey = packedKey;
            }

            static (uint Dev, uint Key) parseLookMouse(int entryId)
            {
                // Steam preset uses:
                // - device 11: positive direction, device 12: negative direction
                // - packed_key scan: 0 => X axis, 1 => Y axis
                return entryId switch
                {
                    0x1B => (11u, 0u), // Look Right  (MouseX+)
                    0x19 => (12u, 0u), // Look Left   (MouseX-)
                    0x1A => (11u, 1u), // Look Up     (MouseY+)
                    0x1C => (12u, 1u), // Look Down   (MouseY-)
                    _ => throw new ArgumentException($"Internal error: entry_id 0x{entryId:X} is not a Look entry."),
                };
            }

            static (uint Dev, uint Key) parseLookToken(int entryId, string token)
            {
                // Accept the simple UI token ("Mouse") and the more explicit verbose tokens ("MouseX+/MouseY-")
                // that show up in analyzer output.
                string t = token.Trim();
                string tl = t.ToLowerInvariant();
                if (tl is "mouse" or "mousex" or "mousey")
                    return parseLookMouse(entryId);

                if (tl.StartsWith("mousex", StringComparison.Ordinal))
                {
                    // X axis: scan=0
                    uint key = 0u;
                    if (tl.EndsWith("-", StringComparison.Ordinal))
                        return (12u, key);
                    if (tl.EndsWith("+", StringComparison.Ordinal))
                        return (11u, key);
                    return parseLookMouse(entryId);
                }

                if (tl.StartsWith("mousey", StringComparison.Ordinal))
                {
                    // Y axis: scan=1
                    uint key = 1u;
                    if (tl.EndsWith("-", StringComparison.Ordinal))
                        return (12u, key);
                    if (tl.EndsWith("+", StringComparison.Ordinal))
                        return (11u, key);
                    return parseLookMouse(entryId);
                }

                if (tl.StartsWith("mouse(", StringComparison.Ordinal) && tl.EndsWith(")", StringComparison.Ordinal))
                {
                    string inner = tl["mouse(".Length..^1];
                    if (int.TryParse(inner, NumberStyles.Integer, CultureInfo.InvariantCulture, out int scanSigned))
                    {
                        var (devDefault, _) = parseLookMouse(entryId);
                        return (devDefault, unchecked((uint)scanSigned));
                    }
                }

                throw new ArgumentException($"Invalid look binding '{token}'. Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key.");
            }

            static (uint Dev, uint Key) parseZoomMouseWheel(string t)
            {
                if (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase))
                    return (16u, 3u);
                if (t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase))
                    return (16u, 4u);
                throw new ArgumentException($"Invalid zoom binding '{t}'. Use MouseWheelUp/MouseWheelDown or a keyboard key.");
            }

            static (uint Dev, uint Key) parseMouseButton(int entryId, string t)
            {
                if (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase))
                {
                    // Steam build uses these device codes for Fire weapon:
                    // - entry 0x12: dev 17, key 0
                    // - entry 0x13: dev 15, key 0
                    return entryId switch
                    {
                        0x12 => (17u, 0u),
                        0x13 => (15u, 0u),
                        _ => throw new ArgumentException("MouseLeft is only supported for Fire weapon (entry 0x12/0x13)."),
                    };
                }

                if (t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase))
                {
                    // Steam build uses device 16 scan 2 for Select weapon.
                    return entryId switch
                    {
                        0x14 => (16u, 2u),
                        _ => throw new ArgumentException("MouseRight is only supported for Select weapon (entry 0x14)."),
                    };
                }

                throw new ArgumentException($"Invalid mouse button binding '{t}'. Use MouseLeft/MouseRight.");
            }

            static uint parseKeyboardPacked(string t, string label)
            {
                if (!BesFilePatcher.TryParseKeyboardPackedKey(t, out uint packed, out string? err))
                    throw new ArgumentException($"Invalid {label}: {err}");
                return packed;
            }

            void parseRow(
                int entryId,
                uint keyboardDeviceCode,
                bool allowLookMouse,
                bool allowZoomWheel,
                bool allowMouseButtons,
                string[]? values,
                string label)
            {
                if (values == null || values.Length != 2)
                    return;

                void parseOne(int slotIndex, string tokenLabel, string? raw)
                {
                    if (isKeep(raw))
                        return;

                    string t = raw!.Trim();
                    if (allowLookMouse && t.StartsWith("Mouse", StringComparison.OrdinalIgnoreCase))
                    {
                        var (dev, key) = parseLookToken(entryId, t);
                        setSlot(entryId, slotIndex, dev, key);
                        return;
                    }

                    if (allowZoomWheel && (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase) || t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase)))
                    {
                        var (dev, key) = parseZoomMouseWheel(t);
                        setSlot(entryId, slotIndex, dev, key);
                        return;
                    }

                    if (allowMouseButtons && (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase) || t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase)))
                    {
                        var (dev, key) = parseMouseButton(entryId, t);
                        setSlot(entryId, slotIndex, dev, key);
                        return;
                    }

                    uint packed = parseKeyboardPacked(t, tokenLabel);
                    setSlot(entryId, slotIndex, keyboardDeviceCode, packed);
                }

                parseOne(0, $"{label} (P1)", values[0]);
                parseOne(1, $"{label} (P2)", values[1]);
            }

            // Movement (action_code 0x3B..0x3E => entry_id 0x1D..0x20, binding_type 9)
            parseRow(0x1F, 9, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: false, moveForward, "Movement: Forward");
            parseRow(0x20, 9, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: false, moveBackward, "Movement: Backward");
            parseRow(0x1D, 9, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: false, moveLeft, "Movement: Left");
            parseRow(0x1E, 9, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: false, moveRight, "Movement: Right");

            // Look (action_code 0x40..0x43 => entry_id 0x19..0x1C, binding_type 9)
            // Preset uses Mouse look via device_code 11/12 + packed_key 0/1.
            parseRow(0x1A, 9, allowLookMouse: true, allowZoomWheel: false, allowMouseButtons: false, lookUp, "Look: Up");
            parseRow(0x1C, 9, allowLookMouse: true, allowZoomWheel: false, allowMouseButtons: false, lookDown, "Look: Down");
            parseRow(0x19, 9, allowLookMouse: true, allowZoomWheel: false, allowMouseButtons: false, lookLeft, "Look: Left");
            parseRow(0x1B, 9, allowLookMouse: true, allowZoomWheel: false, allowMouseButtons: false, lookRight, "Look: Right");

            // Zoom (action_code 0x45/0x46 => entry_id 0x10/0x11, binding_type 9)
            parseRow(0x10, 9, allowLookMouse: false, allowZoomWheel: true, allowMouseButtons: false, zoomIn, "Zoom: In");
            parseRow(0x11, 9, allowLookMouse: false, allowZoomWheel: true, allowMouseButtons: false, zoomOut, "Zoom: Out");

            // Others:
            // - Fire weapon action_code 0x48 remaps both entry_id 0x12 (binding_type 10) and 0x13 (binding_type 9)
            // - Remaining entries are single (see ControlBindings.md)
            if (fireWeapon != null && fireWeapon.Length == 2)
            {
                parseRow(0x12, 10, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: true, fireWeapon, "Others: Fire weapon");
                parseRow(0x13, 9, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: true, fireWeapon, "Others: Fire weapon");
            }

            parseRow(0x14, 10, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: true, selectWeapon, "Others: Select weapon");
            parseRow(0x21, 8, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: false, transform, "Others: Transform");
            parseRow(0x15, 9, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: false, airBrake, "Others: Air brake");
            parseRow(0x3B, 8, allowLookMouse: false, allowZoomWheel: false, allowMouseButtons: false, special, "Others: Special function");

            return dict.Count == 0 ? null : dict;
        }

        private static void PrintPatchSummary(BesFilePatcher patcher, string outputPath,
            Dictionary<int, string>? levelRanks, Dictionary<int, int>? perCategoryKills)
        {
            Console.WriteLine($"Patched: {outputPath}");

            var patched = new List<string>();
            if (patcher.PatchNodes)
            {
                if (levelRanks != null && levelRanks.Count > 0)
                    patched.Add($"Nodes ({patcher.Rank} + {levelRanks.Count} overrides)");
                else
                    patched.Add($"Nodes ({patcher.Rank}-rank)");
            }
            if (patcher.PatchLinks) patched.Add("Links");
            if (patcher.PatchGoodies) patched.Add($"Goodies ({(patcher.UseNewGoodiesInstead ? "NEW" : "OLD")})");
            if (patcher.PatchKills)
            {
                if (perCategoryKills != null && perCategoryKills.Count > 0)
                    patched.Add("Kills (custom per-category)");
                else
                    patched.Add($"Kills ({patcher.GlobalKillCount} each)");
            }

            bool hasCareerSettings =
                patcher.SoundVolumeOverride.HasValue ||
                patcher.MusicVolumeOverride.HasValue ||
                patcher.InvertYAxisP1Override.HasValue ||
                patcher.InvertYAxisP2Override.HasValue ||
                patcher.InvertFlightP1Override.HasValue ||
                patcher.InvertFlightP2Override.HasValue ||
                patcher.VibrationP1Override.HasValue ||
                patcher.VibrationP2Override.HasValue ||
                patcher.ControllerConfigP1Override.HasValue ||
                patcher.ControllerConfigP2Override.HasValue;
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

            if (patcher.OptionsEntryOverrides != null && patcher.OptionsEntryOverrides.Count > 0)
            {
                patched.Add($"Keybind overrides ({patcher.OptionsEntryOverrides.Count} entries)");
            }

            if (patched.Count > 0)
            {
                Console.WriteLine($"  Patched: {string.Join(", ", patched)}");
            }
            else
            {
                Console.WriteLine("  WARNING: No sections selected for patching!");
            }

            var skipped = new List<string>();
            if (!patcher.PatchNodes) skipped.Add("Nodes");
            if (!patcher.PatchLinks) skipped.Add("Links");
            if (!patcher.PatchGoodies) skipped.Add("Goodies");
            if (!patcher.PatchKills) skipped.Add("Kills");
            if (skipped.Count > 0)
            {
                Console.WriteLine($"  Skipped: {string.Join(", ", skipped)}");
            }

            if (patcher.PatchKills && perCategoryKills != null && perCategoryKills.Count > 0)
            {
                Console.WriteLine($"  Kill counts (default: {patcher.GlobalKillCount}):");
                string[] categories = { "Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs" };
                for (int i = 0; i < categories.Length; i++)
                {
                    int value = perCategoryKills.TryGetValue(i, out int overrideKills) ? overrideKills : patcher.GlobalKillCount;
                    string marker = perCategoryKills.ContainsKey(i) ? " *" : "";
                    Console.WriteLine($"    {categories[i]}: {value}{marker}");
                }
            }
        }

    }
}
