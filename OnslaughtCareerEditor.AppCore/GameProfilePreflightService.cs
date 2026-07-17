using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.Win32.SafeHandles;

namespace Onslaught___Career_Editor
{
    public sealed record GameProfilePrepareOptions(
        string SourceGameRoot,
        string OutputRoot,
        string ProfileName,
        string? ExecutableOverridePath = null,
        bool ApplyWindowedCompatibilityPatch = true,
        bool AllowByteLayoutOnlyTarget = false,
        bool IncludeSavegames = false,
        IReadOnlyList<string>? PatchKeys = null,
        IReadOnlyList<string>? LaunchArguments = null,
        string? ProfilePresetId = null,
        string? MusicSwapPresetId = null,
        bool ApplyLevel100TutorialTextMod = false);

    public sealed record GameProfileCopiedEntry(
        string Name,
        string SourcePath,
        string TargetPath,
        bool Directory);

    public sealed record GameProfilePatchResult(
        bool Requested,
        bool Success,
        IReadOnlyList<string> PatchKeys,
        string Message);

    public sealed record GameProfileLaunchPlan(
        string ExecutablePath,
        string WorkingDirectory,
        IReadOnlyList<string> Arguments,
        string CommandPreview);

    public sealed record GameProfileLevel100TextModResult(
        string SchemaVersion,
        DateTimeOffset GeneratedAt,
        bool Mutation,
        uint TextId,
        string TargetRelativePath,
        string BackupRelativePath,
        long OriginalSize,
        string OriginalSha256,
        long ModifiedSize,
        string ModifiedSha256,
        int ChangedOffset,
        int ChangedByteCount);

    public sealed record GameProfilePrepareResult(
        string SchemaVersion,
        DateTimeOffset GeneratedAt,
        bool Mutation,
        string SourceGameRoot,
        string TargetGameRoot,
        string ExecutablePath,
        IReadOnlyList<GameProfileCopiedEntry> Entries,
        GameProfilePatchResult PatchResult,
        GameProfileLaunchPlan LaunchPlan,
        string? ProfilePresetId,
        string? ProfilePresetDisplayName,
        string? ProfilePresetProofStatus,
        int? ProfileDefaultControllerConfiguration,
        bool ProfileDefaultPersistControllerConfigInOptions,
        float? ProfileDefaultMouseLookSensitivity,
        uint? ProfileDefaultScreenShape,
        IReadOnlyList<SafeCopyProfileModule> ProfilePresetModules,
        GameProfileMusicReplacementResult? MusicSwapResult,
        string ManifestPath,
        GameProfileLevel100TextModResult? Level100TextModResult = null);

    public sealed record GameProfileReceiptLine(string Label, string Value);

    public sealed record GameProfilePrepareReceipt(
        string Headline,
        IReadOnlyList<GameProfileReceiptLine> Lines,
        IReadOnlyList<string> IncludedChanges,
        IReadOnlyList<string> StillNotIncluded);

    public static class GameProfilePreflightService
    {
        public const string SchemaVersion = "winui-copied-game-profile.v1";
        public const string Level100TextModSchemaVersion = "winui-level100-english-text-mod.v1";

        private const uint Level100TutorialTextId = 4_422_830;
        private const int Level100TutorialTextOffset = 0x3CF58;
        private const string SupportedEnglishDatSha256 = "789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a";
        private const string Level100TutorialOriginalText = "Okay, Hawk? I want you to manoeuvre the Battle Engine to the area marked on your HUD.";
        private const string Level100TutorialReplacementText = "TOOLKIT MOD ACTIVE. Move Aquila into the yellow objective marker visible on your HUD.";
        private const string Level100EnglishDatRelativePath = "data/language/english.dat";
        private const string Level100EnglishDatBackupRelativePath = "data/language/english.dat.original.backup";

        private static readonly Regex s_safeProfileName = new("^[A-Za-z0-9._-]{1,64}$", RegexOptions.Compiled);
        private static readonly string[] s_requiredDirectoryEntries =
        {
            "data",
        };
        private static readonly string[] s_requiredFileEntries =
        {
            "defaultoptions.bea",
            "binkw32.dll",
            "ogg.dll",
            "vorbis.dll",
            "zlib.dll",
        };
        private static readonly string[] s_optionalEntries =
        {
            "cardid.txt",
            "savegames",
            "steam_appid.txt",
        };
        private static readonly string[] s_windowedPatchKeys =
        {
            "resolution_gate",
            "force_windowed",
        };

        public static GameProfilePrepareResult PrepareWindowedCompatibilityProfile(GameProfilePrepareOptions options)
        {
            if (string.IsNullOrWhiteSpace(options.SourceGameRoot) || !Directory.Exists(options.SourceGameRoot))
                throw new DirectoryNotFoundException($"Source game root does not exist: {options.SourceGameRoot}");

            string profileName = options.ProfileName ?? string.Empty;
            if (!s_safeProfileName.IsMatch(profileName))
                throw new InvalidOperationException("ProfileName may contain only letters, numbers, dot, underscore, and dash.");

            string sourceRoot = NormalizeExistingDirectory(options.SourceGameRoot);
            RejectReparsePoint(sourceRoot, "source game root");
            string outputRoot = NormalizeDirectoryForCreation(options.OutputRoot);
            RejectExistingReparseAncestors(outputRoot, "app-owned output root");
            EnsureAppOwnedOutputRoot(sourceRoot, outputRoot);
            RejectProtectedOrSteamInstallOutputRoot(outputRoot);

            string targetRoot = Path.GetFullPath(Path.Combine(outputRoot, profileName));
            if (Directory.Exists(targetRoot))
                throw new InvalidOperationException($"Target playable copied game folder already exists: {targetRoot}");
            RejectExistingReparseAncestors(targetRoot, "playable copied game folder target");

            string executableSource = ResolveExecutableSource(sourceRoot, options.ExecutableOverridePath);
            ValidateRequiredSourceEntries(sourceRoot, executableSource, hasExecutableOverride: !string.IsNullOrWhiteSpace(options.ExecutableOverridePath));
            string[] requestedPatchKeys = BuildRequestedPatchKeys(
                options.ApplyWindowedCompatibilityPatch,
                options.PatchKeys ?? Array.Empty<string>());
            SafeCopyProfilePreset? profilePreset = ValidateRequestedProfilePreset(options.ProfilePresetId, requestedPatchKeys);
            if (requestedPatchKeys.Length > 0)
            {
                string? selectionError = BinaryPatchPlanBuilder.ValidateVisibleSelection(requestedPatchKeys);
                if (!string.IsNullOrWhiteSpace(selectionError))
                    throw new InvalidOperationException(selectionError);
            }

            var entries = BuildCopyEntries(sourceRoot, targetRoot, executableSource, options.IncludeSavegames);
            Directory.CreateDirectory(targetRoot);
            try
            {
                foreach (GameProfileCopiedEntry entry in entries)
                {
                    if (entry.Directory)
                    {
                        CopyDirectory(entry.SourcePath, entry.TargetPath);
                    }
                    else
                    {
                        Directory.CreateDirectory(Path.GetDirectoryName(entry.TargetPath)!);
                        File.Copy(entry.SourcePath, entry.TargetPath, overwrite: false);
                    }
                }

                string copiedExePath = Path.Combine(targetRoot, "BEA.exe");
                GameProfilePatchResult patchResult = ApplyPatchesIfRequested(
                    copiedExePath,
                    targetRoot,
                    options.AllowByteLayoutOnlyTarget,
                    requestedPatchKeys);
                if (patchResult.Requested && !options.AllowByteLayoutOnlyTarget)
                {
                    IReadOnlyList<BinaryPatchSpec> selected = SelectPatchSpecs(patchResult.PatchKeys);
                    ValidatePatchedExecutableAgainstBackupSnapshot(copiedExePath, selected);
                }

                GameProfileLevel100TextModResult? level100TextModResult = ApplyLevel100TutorialTextModIfRequested(
                    targetRoot,
                    options.ApplyLevel100TutorialTextMod,
                    options.AllowByteLayoutOnlyTarget);

                string manifestPath = Path.Combine(targetRoot, "onslaught-profile-manifest.json");
                GameProfileLaunchPlan launchPlan = BuildLaunchPlanCore(targetRoot, options.LaunchArguments ?? Array.Empty<string>());
                var result = new GameProfilePrepareResult(
                    SchemaVersion,
                    DateTimeOffset.UtcNow,
                    Mutation: true,
                    SourceGameRoot: sourceRoot,
                    TargetGameRoot: targetRoot,
                    ExecutablePath: copiedExePath,
                    Entries: entries,
                    PatchResult: patchResult,
                    LaunchPlan: launchPlan,
                    ProfilePresetId: profilePreset?.Id,
                    ProfilePresetDisplayName: profilePreset?.DisplayName,
                    ProfilePresetProofStatus: profilePreset?.ProofStatus,
                    ProfileDefaultControllerConfiguration: profilePreset?.DefaultControllerConfiguration,
                    ProfileDefaultPersistControllerConfigInOptions: profilePreset?.DefaultPersistControllerConfigInOptions ?? false,
                    ProfileDefaultMouseLookSensitivity: profilePreset?.DefaultMouseLookSensitivity,
                    ProfileDefaultScreenShape: profilePreset?.DefaultScreenShape,
                    ProfilePresetModules: profilePreset?.Modules ?? Array.Empty<SafeCopyProfileModule>(),
                    MusicSwapResult: null,
                    ManifestPath: manifestPath,
                    Level100TextModResult: level100TextModResult);

                WriteManifest(result, manifestPath);
                if (!string.IsNullOrWhiteSpace(options.MusicSwapPresetId))
                {
                    GameProfileMusicReplacementOptions musicOptions = GameProfileMusicReplacementService.BuildSafeCopyMusicSwapPresetOptions(
                        targetRoot,
                        outputRoot,
                        options.MusicSwapPresetId);
                    GameProfileMusicReplacementResult musicSwapResult = GameProfileMusicReplacementService.StageReplacement(musicOptions);
                    result = result with
                    {
                        MusicSwapResult = musicSwapResult,
                    };
                    WriteManifest(result, manifestPath);
                }

                return result;
            }
            catch
            {
                DeleteGeneratedTarget(targetRoot, outputRoot);
                throw;
            }
        }

        public static string ValidateExecutableSourceForWorkspaceCopy(string sourcePath)
        {
            if (string.IsNullOrWhiteSpace(sourcePath))
                throw new InvalidOperationException("Executable source path is required.");

            string fullPath = Path.GetFullPath(sourcePath);
            if (!File.Exists(fullPath))
                throw new FileNotFoundException("Executable source was not found.", fullPath);

            if (!IsSupportedExecutableSourceName(Path.GetFileName(fullPath)))
                throw new InvalidOperationException("Executable source must be named BEA.exe or BEA.exe.original.backup.");

            RejectExistingReparseAncestors(fullPath, "advanced executable source path");
            RejectReparsePoint(fullPath, "advanced executable source");
            RejectMultipleHardLinks(fullPath, "Advanced executable source");
            return fullPath;
        }

        public static string ValidateAppOwnedWorkspaceFileDestination(
            string destinationPath,
            string appOwnedRoot,
            string expectedFileName)
        {
            if (string.IsNullOrWhiteSpace(destinationPath))
                throw new InvalidOperationException("Workspace destination path is required.");

            if (string.IsNullOrWhiteSpace(appOwnedRoot))
                throw new InvalidOperationException("An app-owned workspace root is required.");

            if (string.IsNullOrWhiteSpace(expectedFileName))
                throw new InvalidOperationException("Expected workspace file name is required.");

            string destination = Path.GetFullPath(destinationPath);
            if (!string.Equals(Path.GetFileName(destination), expectedFileName, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException($"Workspace destination must be named {expectedFileName}.");

            string root = NormalizeDirectoryForCreation(appOwnedRoot);
            RejectExistingReparseAncestors(root, "app-owned workspace root");

            if (!IsSameOrUnderRoot(destination, root) ||
                string.Equals(
                    destination.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                    root.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                    StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Workspace destination must stay under the app-owned workspace root.");
            }

            RejectExistingReparseAncestors(destination, "app-owned workspace destination");
            if (File.Exists(destination) || Directory.Exists(destination))
                throw new InvalidOperationException("Workspace destination already exists.");

            return destination;
        }

        public static GameProfileLaunchPlan BuildLaunchPlan(
            string gameRoot,
            IReadOnlyList<string>? arguments = null,
            bool validateMusicReplacementManifest = true)
        {
            string resolvedGameRoot = ValidateGeneratedProfileRoot(gameRoot, validateMusicReplacementManifest);
            return BuildLaunchPlanCore(resolvedGameRoot, arguments ?? Array.Empty<string>());
        }

        public static GameProfilePrepareReceipt BuildPrepareReceipt(
            GameProfilePrepareResult result,
            bool copiedSavegames,
            GameProfileControlOptionsResult? controlOptionsResult)
        {
            ArgumentNullException.ThrowIfNull(result);

            string profileName = !string.IsNullOrWhiteSpace(result.ProfilePresetDisplayName)
                ? result.ProfilePresetDisplayName!
                : "Custom selection";
            string launchModifiers = result.LaunchPlan.Arguments.Count == 0
                ? "none"
                : string.Join(" ", result.LaunchPlan.Arguments);
            string patchRows = result.PatchResult.PatchKeys.Count == 0
                ? "No executable patch rows requested."
                : $"{result.PatchResult.PatchKeys.Count}: {string.Join(", ", result.PatchResult.PatchKeys)}";

            var lines = new List<GameProfileReceiptLine>
            {
                new("Profile", profileName),
                new("Safe copy folder", Path.GetFileName(Path.TrimEndingDirectorySeparator(result.TargetGameRoot))),
                new("Patch rows", patchRows),
                new("Launch modifiers", launchModifiers),
                new(
                    "Savegames",
                    copiedSavegames
                        ? "copied into this safe copy only; source savegames remain read-only."
                        : "not copied into this safe copy."),
                new(
                    "Music swap",
                    result.MusicSwapResult is null
                        ? "none staged during safe-copy creation."
                        : $"staged for {result.MusicSwapResult.TargetMusicFileName}; runtime playback still needs live testing."),
                new(
                    "Level 100 text",
                    result.Level100TextModResult is null
                        ? "original English subtitle retained."
                        : "fixed-size English TUTORIAL_01 replacement staged and hash-verified in this safe copy."),
                new("Control options", BuildReceiptControlOptionsSummary(controlOptionsResult)),
            };

            string[] includedChanges = result.ProfilePresetModules.Count > 0
                ? result.ProfilePresetModules
                    .Select(module => BuildReceiptIncludedChange(result, module, controlOptionsResult))
                    .ToArray()
                : result.PatchResult.PatchKeys
                    .Select(key => $"Patch row: {key}")
                    .ToArray();
            if (result.Level100TextModResult is not null)
            {
                includedChanges = includedChanges
                    .Append("Level 100 English subtitle marker: replaces only TUTORIAL_01 in the copied language table; live retail proof covers this one rendered line.")
                    .ToArray();
            }

            var stillNotIncluded = result.ProfilePresetModules
                .SelectMany(module => module.NonClaims)
                .Where(value => !string.IsNullOrWhiteSpace(value))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList();
            AddReceiptLimit(stillNotIncluded, "No Host/Join or online multiplayer.");
            AddReceiptLimit(stillNotIncluded, "No installed-game mutation.");
            AddReceiptLimit(stillNotIncluded, "No no-noticeable-difference parity claim.");
            if (result.Level100TextModResult is not null)
            {
                AddReceiptLimit(stillNotIncluded, "No general language importer, mission-script override, texture replacement, or AYA repacker.");
            }
            if (HasCopiedControlDefaultsModule(result) &&
                !ControlOptionsMatchProfileDefaults(result, controlOptionsResult))
            {
                AddReceiptLimit(stillNotIncluded, "No fixed Enhanced copied-control-default claim unless the applied control manifest matches the preset defaults.");
            }
            if (result.MusicSwapResult is not null &&
                result.LaunchPlan.Arguments.Any(argument => string.Equals(argument, "-nomusic", StringComparison.OrdinalIgnoreCase)))
            {
                AddReceiptLimit(stillNotIncluded, "Music is muted for this launch, so replacement-audio playback is not being tested.");
            }

            return new GameProfilePrepareReceipt(
                "Safe copy ready",
                lines,
                includedChanges,
                stillNotIncluded);
        }

        private static string BuildReceiptIncludedChange(
            GameProfilePrepareResult result,
            SafeCopyProfileModule module,
            GameProfileControlOptionsResult? controlOptionsResult)
        {
            if (!string.Equals(module.Id, "copied-options-control-defaults", StringComparison.OrdinalIgnoreCase))
            {
                return $"{module.DisplayName}: {module.ClaimBoundary}";
            }

            if (ControlOptionsMatchProfileDefaults(result, controlOptionsResult))
            {
                return $"{module.DisplayName}: {module.ClaimBoundary}";
            }

            if (controlOptionsResult is null)
            {
                return "Copied control options: no control-options manifest was written for this safe copy; current controls remain unchanged.";
            }

            return
                "Copied control options: custom control-options manifest written from current UI selections " +
                $"(P1/P2 config {controlOptionsResult.ControllerConfigP1}/{controlOptionsResult.ControllerConfigP2}, " +
                $"mouse sensitivity {controlOptionsResult.MouseSensitivity:0.###}); not fixed Enhanced defaults.";
        }

        private static bool HasCopiedControlDefaultsModule(GameProfilePrepareResult result)
        {
            return result.ProfilePresetModules.Any(module =>
                string.Equals(module.Id, "copied-options-control-defaults", StringComparison.OrdinalIgnoreCase));
        }

        private static bool ControlOptionsMatchProfileDefaults(
            GameProfilePrepareResult result,
            GameProfileControlOptionsResult? controlOptionsResult)
        {
            if (controlOptionsResult is null)
            {
                return false;
            }

            bool controllerConfigMatches = !result.ProfileDefaultControllerConfiguration.HasValue ||
                (controlOptionsResult.ControllerConfigP1 == result.ProfileDefaultControllerConfiguration.Value &&
                 controlOptionsResult.ControllerConfigP2 == result.ProfileDefaultControllerConfiguration.Value);
            bool mouseLookMatches = !result.ProfileDefaultMouseLookSensitivity.HasValue ||
                Math.Abs(controlOptionsResult.MouseSensitivity - result.ProfileDefaultMouseLookSensitivity.Value) < 0.0001f;
            bool screenShapeMatches = !result.ProfileDefaultScreenShape.HasValue ||
                controlOptionsResult.ScreenShape == result.ProfileDefaultScreenShape.Value;
            bool invertMatches = !controlOptionsResult.InvertWalkerP1 &&
                !controlOptionsResult.InvertWalkerP2 &&
                !controlOptionsResult.InvertFlightP1 &&
                !controlOptionsResult.InvertFlightP2;

            return controllerConfigMatches && mouseLookMatches && screenShapeMatches && invertMatches;
        }

        private static GameProfileLaunchPlan BuildLaunchPlanCore(string gameRoot, IReadOnlyList<string> arguments)
        {
            if (string.IsNullOrWhiteSpace(gameRoot) || !Directory.Exists(gameRoot))
                throw new DirectoryNotFoundException($"Playable copied game folder root does not exist: {gameRoot}");

            string resolvedGameRoot = NormalizeExistingDirectory(gameRoot);
            string executablePath = Path.Combine(resolvedGameRoot, "BEA.exe");
            if (!File.Exists(executablePath))
                throw new FileNotFoundException("BEA.exe was not found under the copied game profile.", executablePath);

            string[] normalizedArguments = NormalizeLaunchArguments(arguments ?? Array.Empty<string>());
            string argumentString = string.Join(" ", normalizedArguments);
            string commandPreview = argumentString.Length == 0
                ? $"Start-Process -FilePath \"{executablePath}\" -WorkingDirectory \"{resolvedGameRoot}\""
                : $"Start-Process -FilePath \"{executablePath}\" -WorkingDirectory \"{resolvedGameRoot}\" -ArgumentList \"{argumentString}\"";

            return new GameProfileLaunchPlan(
                ExecutablePath: executablePath,
                WorkingDirectory: resolvedGameRoot,
                Arguments: normalizedArguments,
                CommandPreview: commandPreview);
        }

        private static string BuildReceiptControlOptionsSummary(GameProfileControlOptionsResult? result)
        {
            return result is null
                ? "no post-create control edit result; profile defaults and selected options are recorded separately."
                : $"safe-copy screen shape {result.ScreenShape} (1=16:9); mouse sensitivity {result.MouseSensitivity:0.###}; controller config P1={result.ControllerConfigP1}, P2={result.ControllerConfigP2}.";
        }

        private static void AddReceiptLimit(List<string> limits, string value)
        {
            if (!limits.Contains(value, StringComparer.OrdinalIgnoreCase))
            {
                limits.Add(value);
            }
        }

        private static string ValidateGeneratedProfileRoot(string gameRoot, bool validateMusicReplacementManifest)
        {
            if (string.IsNullOrWhiteSpace(gameRoot) || !Directory.Exists(gameRoot))
                throw new DirectoryNotFoundException($"Playable copied game folder root does not exist: {gameRoot}");

            string resolvedGameRoot = NormalizeExistingDirectory(gameRoot);
            string manifestPath = Path.Combine(resolvedGameRoot, "onslaught-profile-manifest.json");
            if (!File.Exists(manifestPath))
                throw new InvalidOperationException("Launch plan requires a generated playable copied game folder manifest.");

            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(manifestPath));
            string? schemaVersion = doc.RootElement.TryGetProperty("schemaVersion", out JsonElement schemaEl)
                ? schemaEl.GetString()
                : null;
            string? targetGameRoot = doc.RootElement.TryGetProperty("targetGameRoot", out JsonElement targetEl)
                ? targetEl.GetString()
                : null;

            if (!string.Equals(schemaVersion, SchemaVersion, StringComparison.Ordinal))
                throw new InvalidOperationException("Launch plan requires a current playable copied game folder manifest.");

            if (string.IsNullOrWhiteSpace(targetGameRoot))
                throw new InvalidOperationException("Playable copied game folder manifest is missing its target root marker.");

            if (!string.Equals(targetGameRoot, ".", StringComparison.Ordinal))
            {
                string resolvedManifestRoot = Path.IsPathFullyQualified(targetGameRoot)
                    ? NormalizeExistingDirectory(targetGameRoot)
                    : NormalizeExistingDirectory(Path.Combine(resolvedGameRoot, targetGameRoot));
                if (!string.Equals(resolvedManifestRoot, resolvedGameRoot, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Playable copied game folder manifest does not match the launch root.");
            }

            ValidateManifestExecutableState(doc.RootElement, resolvedGameRoot);
            ValidateOptionalLevel100TextMod(doc.RootElement, resolvedGameRoot);
            ValidateOptionalControlOptionsManifest(resolvedGameRoot);
            if (validateMusicReplacementManifest)
            {
                ValidateOptionalMusicReplacementManifest(resolvedGameRoot);
            }

            return resolvedGameRoot;
        }

        private static void ValidateOptionalLevel100TextMod(JsonElement manifestRoot, string resolvedGameRoot)
        {
            if (!manifestRoot.TryGetProperty("level100TextMod", out JsonElement modEl) ||
                modEl.ValueKind == JsonValueKind.Null)
            {
                return;
            }

            if (modEl.ValueKind != JsonValueKind.Object)
                throw new InvalidOperationException("Playable copied game folder Level 100 text metadata is invalid.");

            string schemaVersion = RequiredString(modEl, "schemaVersion", "Level 100 text metadata");
            if (!string.Equals(schemaVersion, Level100TextModSchemaVersion, StringComparison.Ordinal))
                throw new InvalidOperationException("Playable copied game folder Level 100 text metadata has an unsupported schema.");

            string targetRelativePath = RequiredString(modEl, "targetRelativePath", "Level 100 text metadata");
            string backupRelativePath = RequiredString(modEl, "backupRelativePath", "Level 100 text metadata");
            if (!string.Equals(targetRelativePath, Level100EnglishDatRelativePath, StringComparison.OrdinalIgnoreCase) ||
                !string.Equals(backupRelativePath, Level100EnglishDatBackupRelativePath, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Playable copied game folder Level 100 text metadata does not target the supported English language table.");
            }

            string targetPath = ResolveProfileRelativePath(resolvedGameRoot, targetRelativePath, "Level 100 text target");
            string backupPath = ResolveProfileRelativePath(resolvedGameRoot, backupRelativePath, "Level 100 text backup");
            if (!File.Exists(targetPath))
                throw new FileNotFoundException("Playable copied game folder Level 100 text target is missing.", targetPath);
            if (!File.Exists(backupPath))
                throw new FileNotFoundException("Playable copied game folder Level 100 text backup is missing.", backupPath);

            string originalSha256 = RequiredString(modEl, "originalSha256", "Level 100 text metadata");
            string modifiedSha256 = RequiredString(modEl, "modifiedSha256", "Level 100 text metadata");
            if (!string.Equals(ComputeSha256(backupPath), originalSha256, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Playable copied game folder Level 100 text backup no longer matches its manifest hash.");
            if (!string.Equals(ComputeSha256(targetPath), modifiedSha256, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Playable copied game folder Level 100 text target no longer matches its manifest hash.");

            if (!modEl.TryGetProperty("originalSize", out JsonElement originalSizeEl) ||
                !originalSizeEl.TryGetInt64(out long originalSize) ||
                !modEl.TryGetProperty("modifiedSize", out JsonElement modifiedSizeEl) ||
                !modifiedSizeEl.TryGetInt64(out long modifiedSize) ||
                new FileInfo(backupPath).Length != originalSize ||
                new FileInfo(targetPath).Length != modifiedSize ||
                originalSize != modifiedSize)
            {
                throw new InvalidOperationException("Playable copied game folder Level 100 text file sizes do not match its fixed-size manifest contract.");
            }

            if (!modEl.TryGetProperty("textId", out JsonElement textIdEl) ||
                !textIdEl.TryGetUInt32(out uint textId) ||
                textId != Level100TutorialTextId)
            {
                throw new InvalidOperationException("Playable copied game folder Level 100 text metadata has the wrong text ID.");
            }

            if (!modEl.TryGetProperty("changedOffset", out JsonElement offsetEl) ||
                !offsetEl.TryGetInt32(out int changedOffset) ||
                !modEl.TryGetProperty("changedByteCount", out JsonElement byteCountEl) ||
                !byteCountEl.TryGetInt32(out int changedByteCount))
            {
                throw new InvalidOperationException("Playable copied game folder Level 100 text metadata is missing its changed range.");
            }

            byte[] originalBytes = Encoding.Unicode.GetBytes(Level100TutorialOriginalText);
            byte[] replacementBytes = Encoding.Unicode.GetBytes(Level100TutorialReplacementText);
            if (changedByteCount != originalBytes.Length ||
                changedOffset < 0 ||
                changedOffset > new FileInfo(targetPath).Length - changedByteCount)
            {
                throw new InvalidOperationException("Playable copied game folder Level 100 text metadata has an invalid changed range.");
            }

            byte[] backupData = File.ReadAllBytes(backupPath);
            byte[] targetData = File.ReadAllBytes(targetPath);
            if (!backupData.AsSpan(changedOffset, changedByteCount).SequenceEqual(originalBytes) ||
                !targetData.AsSpan(changedOffset, changedByteCount).SequenceEqual(replacementBytes))
            {
                throw new InvalidOperationException("Playable copied game folder Level 100 text bytes no longer match the expected original/replacement pair.");
            }
        }

        private static void ValidateOptionalMusicReplacementManifest(string resolvedGameRoot)
        {
            string manifestPath = Path.Combine(resolvedGameRoot, GameProfileMusicReplacementService.ManifestFileName);
            if (!File.Exists(manifestPath))
                return;

            JsonDocument doc;
            try
            {
                doc = JsonDocument.Parse(File.ReadAllText(manifestPath));
            }
            catch (JsonException ex)
            {
                throw new InvalidOperationException("Playable copied game folder music replacement manifest is invalid JSON.", ex);
            }

            using (doc)
            {
                JsonElement root = doc.RootElement;
                string schemaVersion = RequiredString(root, "schemaVersion", "music replacement manifest");
                if (!string.Equals(schemaVersion, GameProfileMusicReplacementService.SchemaVersion, StringComparison.Ordinal))
                    throw new InvalidOperationException("Playable copied game folder music replacement manifest has an unsupported schema.");

                string targetMusicFileName = RequiredString(root, "targetMusicFileName", "music replacement manifest");
                string targetRelativePath = RequiredString(root, "targetRelativePath", "music replacement manifest");
                string backupRelativePath = RequiredString(root, "backupRelativePath", "music replacement manifest");
                string originalSha256 = RequiredString(root, "originalSha256", "music replacement manifest");
                string replacementSha256 = RequiredString(root, "replacementSha256", "music replacement manifest");

                string targetPath = ResolveProfileRelativePath(resolvedGameRoot, targetRelativePath, "music replacement target");
                string backupPath = ResolveProfileRelativePath(resolvedGameRoot, backupRelativePath, "music replacement backup");
                if (!string.Equals(Path.GetFileName(targetPath), targetMusicFileName, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Playable copied game folder music replacement manifest target file does not match its target name.");

                if (!File.Exists(targetPath))
                    throw new FileNotFoundException("Playable copied game folder music replacement target is missing.", targetPath);
                if (!File.Exists(backupPath))
                    throw new FileNotFoundException("Playable copied game folder music replacement backup is missing.", backupPath);

                string actualTargetHash = ComputeSha256(targetPath);
                if (!string.Equals(actualTargetHash, replacementSha256, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Playable copied game folder music replacement manifest hash does not match the staged target track.");

                string actualBackupHash = ComputeSha256(backupPath);
                if (!string.Equals(actualBackupHash, originalSha256, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Playable copied game folder music replacement manifest hash does not match the backup track.");

                if (root.TryGetProperty("originalSize", out JsonElement originalSizeEl) &&
                    originalSizeEl.TryGetInt64(out long originalSize) &&
                    new FileInfo(backupPath).Length != originalSize)
                {
                    throw new InvalidOperationException("Playable copied game folder music replacement backup size does not match manifest.");
                }

                if (root.TryGetProperty("replacementSize", out JsonElement replacementSizeEl) &&
                    replacementSizeEl.TryGetInt64(out long replacementSize) &&
                    new FileInfo(targetPath).Length != replacementSize)
                {
                    throw new InvalidOperationException("Playable copied game folder music replacement target size does not match manifest.");
                }
            }
        }

        private static void ValidateOptionalControlOptionsManifest(string resolvedGameRoot)
        {
            string manifestPath = Path.Combine(resolvedGameRoot, GameProfileControlOptionsService.ManifestFileName);
            if (!File.Exists(manifestPath))
                return;

            JsonDocument doc;
            try
            {
                doc = JsonDocument.Parse(File.ReadAllText(manifestPath));
            }
            catch (JsonException ex)
            {
                throw new InvalidOperationException("Playable copied game folder control-options manifest is invalid JSON.", ex);
            }

            using (doc)
            {
                JsonElement root = doc.RootElement;
                string schemaVersion = RequiredString(root, "schemaVersion", "control-options manifest");
                if (!string.Equals(schemaVersion, GameProfileControlOptionsService.ManifestSchemaVersion, StringComparison.Ordinal))
                    throw new InvalidOperationException("Playable copied game folder control-options manifest has an unsupported schema.");

                string proofStatus = RequiredString(root, "proofStatus", "control-options manifest");
                if (!string.Equals(proofStatus, GameProfileControlOptionsService.ProofStatusOptionsByteMaterializedOnly, StringComparison.Ordinal))
                    throw new InvalidOperationException("Playable copied game folder control-options manifest has an unsupported proof status.");

                string targetPath = RequiredString(root, "targetPath", "control-options manifest");
                string resolvedTargetPath = Path.GetFullPath(Path.Combine(resolvedGameRoot, targetPath));
                string expectedOptionsPath = Path.Combine(resolvedGameRoot, "defaultoptions.bea");
                if (!string.Equals(resolvedTargetPath, expectedOptionsPath, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Playable copied game folder control-options manifest target does not match defaultoptions.bea.");

                if (!File.Exists(expectedOptionsPath))
                    throw new FileNotFoundException("Playable copied game folder control-options target is missing.", expectedOptionsPath);

                string expectedHash = RequiredString(root, "hashAfter", "control-options manifest");
                string actualHash = ComputeSha256(expectedOptionsPath);
                if (!string.Equals(expectedHash, actualHash, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Playable copied game folder control-options manifest hash does not match defaultoptions.bea.");

                if (root.TryGetProperty("optionsSize", out JsonElement sizeEl) &&
                    sizeEl.TryGetInt64(out long expectedSize) &&
                    new FileInfo(expectedOptionsPath).Length != expectedSize)
                {
                    throw new InvalidOperationException("Playable copied game folder control-options manifest size does not match defaultoptions.bea.");
                }

                if (!root.TryGetProperty("changedRanges", out JsonElement rangesEl) ||
                    rangesEl.ValueKind != JsonValueKind.Array ||
                    rangesEl.GetArrayLength() == 0)
                {
                    throw new InvalidOperationException("Playable copied game folder control-options manifest is missing changed byte ranges.");
                }

                if (!root.TryGetProperty("backups", out JsonElement backupsEl) ||
                    backupsEl.ValueKind != JsonValueKind.Array ||
                    backupsEl.GetArrayLength() == 0)
                {
                    throw new InvalidOperationException("Playable copied game folder control-options manifest is missing backup metadata.");
                }

                foreach (JsonElement backupEl in backupsEl.EnumerateArray())
                {
                    string relativePath = RequiredString(backupEl, "relativePath", "control-options backup");
                    string backupPath = Path.GetFullPath(Path.Combine(resolvedGameRoot, relativePath));
                    if (!IsSameOrUnderRoot(backupPath, resolvedGameRoot) ||
                        string.Equals(backupPath, resolvedGameRoot, StringComparison.OrdinalIgnoreCase))
                    {
                        throw new InvalidOperationException("Playable copied game folder control-options backup path escapes the generated profile.");
                    }

                    if (!File.Exists(backupPath))
                        throw new FileNotFoundException("Playable copied game folder control-options backup is missing.", backupPath);

                    if (backupEl.TryGetProperty("size", out JsonElement backupSizeEl) &&
                        backupSizeEl.TryGetInt64(out long expectedBackupSize) &&
                        new FileInfo(backupPath).Length != expectedBackupSize)
                    {
                        throw new InvalidOperationException("Playable copied game folder control-options backup size does not match manifest.");
                    }

                    string expectedBackupHash = RequiredString(backupEl, "sha256", "control-options backup");
                    string actualBackupHash = ComputeSha256(backupPath);
                    if (!string.Equals(expectedBackupHash, actualBackupHash, StringComparison.OrdinalIgnoreCase))
                        throw new InvalidOperationException("Playable copied game folder control-options backup hash does not match manifest.");
                }
            }
        }

        private static string RequiredString(JsonElement element, string propertyName, string label)
        {
            if (!element.TryGetProperty(propertyName, out JsonElement child) ||
                child.ValueKind != JsonValueKind.String)
            {
                throw new InvalidOperationException($"Playable copied game folder {label} is missing {propertyName}.");
            }

            string? value = child.GetString();
            if (string.IsNullOrWhiteSpace(value))
                throw new InvalidOperationException($"Playable copied game folder {label} has an empty {propertyName}.");

            return value;
        }

        private static string ResolveProfileRelativePath(string root, string relativePath, string label)
        {
            if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathFullyQualified(relativePath))
                throw new InvalidOperationException($"Playable copied game folder {label} path must be package-relative.");

            string fullPath = Path.GetFullPath(Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar)));
            if (!IsSameOrUnderRoot(fullPath, root) || string.Equals(fullPath, root, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException($"Playable copied game folder {label} path escapes the generated profile.");

            return fullPath;
        }

        private static void ValidateManifestExecutableState(JsonElement manifestRoot, string resolvedGameRoot)
        {
            string executablePath = Path.Combine(resolvedGameRoot, "BEA.exe");
            if (manifestRoot.TryGetProperty("executablePath", out JsonElement exeEl))
            {
                string? manifestExePath = exeEl.GetString();
                string resolvedManifestExePath = string.IsNullOrWhiteSpace(manifestExePath)
                    ? string.Empty
                    : Path.IsPathFullyQualified(manifestExePath)
                        ? Path.GetFullPath(manifestExePath)
                        : Path.GetFullPath(Path.Combine(resolvedGameRoot, manifestExePath));
                if (string.IsNullOrWhiteSpace(manifestExePath) ||
                    !string.Equals(resolvedManifestExePath, executablePath, StringComparison.OrdinalIgnoreCase))
                {
                    throw new InvalidOperationException("Playable copied game folder manifest executable path does not match the launch root.");
                }
            }

            if (!File.Exists(executablePath))
                throw new FileNotFoundException("BEA.exe was not found under the copied game profile.", executablePath);

            if (!manifestRoot.TryGetProperty("patchResult", out JsonElement patchResultEl))
                throw new InvalidOperationException("Playable copied game folder manifest is missing patch result metadata.");

            bool requested = patchResultEl.TryGetProperty("requested", out JsonElement requestedEl) && requestedEl.GetBoolean();
            if (!requested)
            {
                ValidateManifestExecutableIdentity(manifestRoot, executablePath);
                return;
            }

            bool success = patchResultEl.TryGetProperty("success", out JsonElement successEl) && successEl.GetBoolean();
            if (!success)
                throw new InvalidOperationException("Playable copied game folder manifest does not record a successful patch result.");

            if (!patchResultEl.TryGetProperty("patchKeys", out JsonElement keysEl) || keysEl.ValueKind != JsonValueKind.Array)
                throw new InvalidOperationException("Playable copied game folder manifest is missing patch keys.");

            string[] patchKeys = keysEl.EnumerateArray()
                .Select(keyEl => keyEl.GetString())
                .Where(key => !string.IsNullOrWhiteSpace(key))
                .Select(key => key!)
                .ToArray();
            if (!s_windowedPatchKeys.All(required => patchKeys.Contains(required, StringComparer.OrdinalIgnoreCase)))
                throw new InvalidOperationException("Playable copied game folder manifest patch keys do not include the windowed compatibility set.");

            IReadOnlyList<BinaryPatchSpec> selected = SelectPatchSpecs(patchKeys);
            byte[] data = File.ReadAllBytes(executablePath);
            var (_, allPatched, rows) = BinaryPatchEngine.VerifyPatchSpecs(data, selected);
            if (!allPatched)
            {
                string states = string.Join(", ", rows.Select(row => $"{row.Spec.Key}={BinaryPatchEngine.StateLabel(row.State)}"));
                throw new InvalidOperationException($"The current copied executable no longer matches the manifest patch state: {states}");
            }

            ValidatePatchedExecutableAgainstBackupSnapshot(executablePath, selected);
        }

        private static void ValidatePatchedExecutableAgainstBackupSnapshot(string executablePath, IReadOnlyList<BinaryPatchSpec> selected)
        {
            string backupPath = BinaryPatchEngine.BuildBackupPath(executablePath);
            string backupHashPath = BinaryPatchEngine.BuildBackupHashPath(executablePath);
            if (!File.Exists(backupPath) || !File.Exists(backupHashPath))
                throw new InvalidOperationException("Playable copied game folder launch requires the copied executable backup snapshot and hash sidecar.");

            byte[] backupBytes = File.ReadAllBytes(backupPath);
            string expectedBackupHash = File.ReadAllText(backupHashPath).Trim();
            string actualBackupHash = ComputeSha256(backupPath);
            if (!string.Equals(expectedBackupHash, actualBackupHash, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Playable copied game folder executable backup snapshot hash does not match its sidecar.");

            var trustedHashes = selected
                .SelectMany(spec => spec.TargetBinaryHashes ?? Array.Empty<string>())
                .Where(hash => !string.IsNullOrWhiteSpace(hash))
                .ToHashSet(StringComparer.OrdinalIgnoreCase);
            if (!trustedHashes.Contains(actualBackupHash))
                throw new InvalidOperationException("Playable copied game folder executable backup snapshot is not a trusted clean Steam retail specimen.");

            long[] trustedSizes = selected
                .Select(spec => spec.TargetBinarySize)
                .Where(size => size.HasValue)
                .Select(size => size!.Value)
                .Distinct()
                .ToArray();
            if (trustedSizes.Length == 0 || !trustedSizes.Contains(backupBytes.LongLength))
                throw new InvalidOperationException("Playable copied game folder executable backup snapshot size is not a trusted clean Steam retail specimen.");

            var (_, _, backupRows) = BinaryPatchEngine.VerifyPatchSpecs(backupBytes, selected);
            if (backupRows.Any(row => row.State != BinaryPatchState.Original))
            {
                string states = string.Join(", ", backupRows.Select(row => $"{row.Spec.Key}={BinaryPatchEngine.StateLabel(row.State)}"));
                throw new InvalidOperationException($"Playable copied game folder executable backup snapshot is not a clean base for selected patches: {states}");
            }

            byte[] expectedPatchedBytes = backupBytes.ToArray();
            foreach (BinaryPatchSpec spec in selected)
            {
                foreach (BinaryPatchRegion region in BinaryPatchEngine.GetPatchRegions(spec))
                {
                    region.Patched.CopyTo(expectedPatchedBytes, region.FileOffset);
                }
            }

            byte[] actualBytes = File.ReadAllBytes(executablePath);
            if (!actualBytes.SequenceEqual(expectedPatchedBytes))
                throw new InvalidOperationException("The current copied executable no longer matches the backup-derived selected patch bytes.");
        }

        private static void ValidateManifestExecutableIdentity(JsonElement manifestRoot, string executablePath)
        {
            if (!manifestRoot.TryGetProperty("executableSize", out JsonElement sizeEl) ||
                !sizeEl.TryGetInt64(out long expectedSize))
            {
                throw new InvalidOperationException("Playable copied game folder manifest is missing executable size metadata.");
            }

            if (!manifestRoot.TryGetProperty("executableSha256", out JsonElement hashEl) ||
                hashEl.ValueKind != JsonValueKind.String ||
                string.IsNullOrWhiteSpace(hashEl.GetString()))
            {
                throw new InvalidOperationException("Playable copied game folder manifest is missing executable full-file hash metadata.");
            }

            FileInfo info = new(executablePath);
            if (info.Length != expectedSize)
            {
                throw new InvalidOperationException("The current copied executable no longer matches the manifest full-file size.");
            }

            string expectedHash = hashEl.GetString()!.Trim();
            string actualHash = ComputeSha256(executablePath);
            if (!string.Equals(actualHash, expectedHash, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("The current copied executable no longer matches the manifest full-file hash.");
            }
        }

        private static string ResolveExecutableSource(string sourceRoot, string? executableOverridePath)
        {
            string candidate = string.IsNullOrWhiteSpace(executableOverridePath)
                ? Path.Combine(sourceRoot, "BEA.exe")
                : Path.GetFullPath(executableOverridePath);

            if (!File.Exists(candidate))
                throw new FileNotFoundException("BEA.exe source was not found.", candidate);

            if (!IsSupportedExecutableSourceName(Path.GetFileName(candidate)))
                throw new InvalidOperationException("Executable source must be named BEA.exe or BEA.exe.original.backup.");

            if (!IsSameOrUnderRoot(candidate, sourceRoot))
                throw new InvalidOperationException("Executable source must stay inside the source game root.");

            RejectReparsePoint(candidate, "executable source");
            RejectMultipleHardLinks(candidate, "Executable source");

            return candidate;
        }

        private static bool IsSupportedExecutableSourceName(string fileName)
        {
            return string.Equals(fileName, "BEA.exe", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(fileName, "BEA.exe.original.backup", StringComparison.OrdinalIgnoreCase);
        }

        private static void ValidateRequiredSourceEntries(string sourceRoot, string executableSource, bool hasExecutableOverride)
        {
            if (!hasExecutableOverride && !File.Exists(Path.Combine(sourceRoot, "BEA.exe")))
                throw new FileNotFoundException("Required game entry is missing: BEA.exe", Path.Combine(sourceRoot, "BEA.exe"));

            if (hasExecutableOverride && !File.Exists(executableSource))
                throw new FileNotFoundException("Executable override is missing.", executableSource);

            foreach (string entry in s_requiredDirectoryEntries)
            {
                string path = Path.Combine(sourceRoot, entry);
                if (!Directory.Exists(path))
                    throw new DirectoryNotFoundException($"Required game directory is missing: {entry}");
                RejectReparsePoint(path, $"required game directory '{entry}'");
            }

            foreach (string entry in s_requiredFileEntries)
            {
                string path = Path.Combine(sourceRoot, entry);
                if (!File.Exists(path))
                    throw new FileNotFoundException($"Required game file is missing: {entry}", path);
                RejectReparsePoint(path, $"required game file '{entry}'");
                RejectMultipleHardLinks(path, $"Required game file '{entry}'");
            }
        }

        private static IReadOnlyList<GameProfileCopiedEntry> BuildCopyEntries(
            string sourceRoot,
            string targetRoot,
            string executableSource,
            bool includeSavegames)
        {
            var entries = new List<GameProfileCopiedEntry>
            {
                new("BEA.exe", executableSource, Path.Combine(targetRoot, "BEA.exe"), Directory: false),
            };

            IEnumerable<string> optionalEntries = includeSavegames
                ? s_optionalEntries
                : s_optionalEntries.Where(entry => !string.Equals(entry, "savegames", StringComparison.OrdinalIgnoreCase));

            foreach (string entry in s_requiredDirectoryEntries.Concat(s_requiredFileEntries).Concat(optionalEntries))
            {
                string sourcePath = Path.Combine(sourceRoot, entry);
                if (File.Exists(sourcePath) || Directory.Exists(sourcePath))
                {
                    RejectReparsePoint(sourcePath, $"game entry '{entry}'");
                    if (File.Exists(sourcePath))
                    {
                        RejectMultipleHardLinks(sourcePath, $"Game entry '{entry}'");
                    }

                    entries.Add(new GameProfileCopiedEntry(
                        entry,
                        sourcePath,
                        Path.Combine(targetRoot, entry),
                        Directory: Directory.Exists(sourcePath)));
                }
            }

            return entries;
        }

        private static GameProfilePatchResult ApplyPatchesIfRequested(
            string exePath,
            string targetRoot,
            bool allowByteLayoutOnlyTarget,
            IReadOnlyList<string> requestedPatchKeys)
        {
            string[] requestedKeys = requestedPatchKeys
                .Where(key => !string.IsNullOrWhiteSpace(key))
                .Select(key => key.Trim())
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                .ToArray();
            if (requestedKeys.Length == 0)
                return new GameProfilePatchResult(false, true, Array.Empty<string>(), "No executable patches were requested.");

            string? selectionError = BinaryPatchPlanBuilder.ValidateVisibleSelection(requestedKeys);
            if (!string.IsNullOrWhiteSpace(selectionError))
                throw new InvalidOperationException(selectionError);

            IReadOnlyList<BinaryPatchSpec> selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(requestedKeys);
            var (success, message) = BinaryPatchEngine.ApplyPatchesToFile(
                new BinaryPatchTargetOptions(
                    ExePath: exePath,
                    AllowedRoot: targetRoot,
                    AllowByteLayoutOnlyTarget: allowByteLayoutOnlyTarget),
                selected);

            if (!success)
                throw new InvalidOperationException($"Playable copied game folder patch apply failed: {message}");

            byte[] readback = File.ReadAllBytes(exePath);
            var (_, allPatched, rows) = BinaryPatchEngine.VerifyPatchSpecs(readback, selected);
            if (!allPatched)
            {
                string states = string.Join(", ", rows.Select(row => $"{row.Spec.Key}={BinaryPatchEngine.StateLabel(row.State)}"));
                throw new InvalidOperationException($"Playable copied game folder patch verification failed: {states}");
            }

            return new GameProfilePatchResult(
                true,
                true,
                selected.Select(spec => spec.Key).ToArray(),
                message + "\nSelected patch bytes verified on disk.");
        }

        private static string[] BuildRequestedPatchKeys(bool includeWindowedCompatibility, IReadOnlyList<string> visiblePatchKeys)
        {
            var keys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string key in visiblePatchKeys ?? Array.Empty<string>())
            {
                if (!string.IsNullOrWhiteSpace(key))
                    keys.Add(key.Trim());
            }

            if (!includeWindowedCompatibility && keys.Count > 0)
            {
                throw new InvalidOperationException(
                    "Playable copied game folder patch preparation requires the windowed compatibility patch set when any executable patch rows are selected.");
            }

            if (includeWindowedCompatibility)
            {
                foreach (string key in s_windowedPatchKeys)
                    keys.Add(key);
            }

            return keys.OrderBy(key => key, StringComparer.OrdinalIgnoreCase).ToArray();
        }

        private static SafeCopyProfilePreset? ValidateRequestedProfilePreset(
            string? profilePresetId,
            IReadOnlyList<string> requestedPatchKeys)
        {
            if (string.IsNullOrWhiteSpace(profilePresetId))
                return null;

            SafeCopyProfilePreset preset = BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(profilePresetId);
            if (!preset.IsSelectable)
                throw new InvalidOperationException($"{preset.DisplayName} cannot be used to prepare a safe game copy.");

            string[] expectedKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(preset.Id)
                .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                .ToArray();
            string[] actualKeys = (requestedPatchKeys ?? Array.Empty<string>())
                .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                .ToArray();
            if (!expectedKeys.SequenceEqual(actualKeys, StringComparer.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"{preset.DisplayName} profile requires its exact proof-bounded patch row set.");
            }

            return preset;
        }

        private static IReadOnlyList<BinaryPatchSpec> SelectPatchSpecs(IReadOnlyList<string> keys)
        {
            var byKey = BinaryPatchEngine.PatchSpecs.ToDictionary(spec => spec.Key, StringComparer.OrdinalIgnoreCase);
            var selected = new List<BinaryPatchSpec>(keys.Count);
            foreach (string key in keys)
            {
                if (!byKey.TryGetValue(key, out BinaryPatchSpec? spec))
                    throw new InvalidOperationException($"Required patch catalog row is missing: {key}");
                selected.Add(spec);
            }

            return selected;
        }

        private static string[] NormalizeLaunchArguments(IReadOnlyList<string> arguments)
        {
            var normalized = new List<string>();
            for (int index = 0; index < arguments.Count; index++)
            {
                string token = arguments[index]?.Trim() ?? string.Empty;
                if (token.Length == 0)
                    continue;

                if (string.Equals(token, "-forcewindowed", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-skipfmv", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-nomusic", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-nosound", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-norumble", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-nostaticshadows", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-hidetail", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-showdebugtrace", StringComparison.OrdinalIgnoreCase))
                {
                    normalized.Add(token.ToLowerInvariant());
                    continue;
                }

                if (string.Equals(token, "-res", StringComparison.OrdinalIgnoreCase))
                {
                    if (index + 2 >= arguments.Count)
                        throw new InvalidOperationException("-res requires numeric width and height values.");

                    string widthToken = arguments[++index]?.Trim() ?? string.Empty;
                    string heightToken = arguments[++index]?.Trim() ?? string.Empty;
                    if (!int.TryParse(widthToken, out int width) ||
                        !int.TryParse(heightToken, out int height) ||
                        width < 640 || width > 16384 ||
                        height < 480 || height > 16384)
                    {
                        throw new InvalidOperationException("-res requires a width from 640 to 16384 and a height from 480 to 16384.");
                    }

                    normalized.Add("-res");
                    normalized.Add(width.ToString(System.Globalization.CultureInfo.InvariantCulture));
                    normalized.Add(height.ToString(System.Globalization.CultureInfo.InvariantCulture));
                    continue;
                }

                if (string.Equals(token, "-level", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-configuration", StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(token, "-textureramlimit", StringComparison.OrdinalIgnoreCase))
                {
                    if (index + 1 >= arguments.Count)
                        throw new InvalidOperationException($"{token.ToLowerInvariant()} requires a numeric value.");

                    string valueToken = arguments[++index]?.Trim() ?? string.Empty;
                    if (!int.TryParse(valueToken, out int value))
                        throw new InvalidOperationException($"{token.ToLowerInvariant()} requires a numeric value.");

                    string normalizedToken = token.ToLowerInvariant();
                    if (string.Equals(normalizedToken, "-level", StringComparison.Ordinal))
                    {
                        if (value < 1 || value > 9999)
                            throw new InvalidOperationException("-level requires a numeric mission id between 1 and 9999.");
                    }
                    else if (string.Equals(normalizedToken, "-configuration", StringComparison.Ordinal))
                    {
                        if (value < 1 || value > 4)
                            throw new InvalidOperationException("-configuration requires a controller configuration between 1 and 4.");
                    }
                    else if (string.Equals(normalizedToken, "-textureramlimit", StringComparison.Ordinal))
                    {
                        const int minTextureRamBytes = 8 * 1024 * 1024;
                        const int maxTextureRamBytes = 512 * 1024 * 1024;
                        if (value < minTextureRamBytes || value > maxTextureRamBytes)
                            throw new InvalidOperationException("-textureramlimit requires a byte limit between 8388608 and 536870912.");
                    }

                    normalized.Add(normalizedToken);
                    normalized.Add(value.ToString(System.Globalization.CultureInfo.InvariantCulture));
                    continue;
                }

                if (token.StartsWith("-", StringComparison.Ordinal))
                    throw new InvalidOperationException($"Unsupported launch argument '{token}'.");

                throw new InvalidOperationException($"Unexpected launch argument value '{token}'.");
            }

            return normalized.ToArray();
        }

        private static GameProfileLevel100TextModResult? ApplyLevel100TutorialTextModIfRequested(
            string targetRoot,
            bool requested,
            bool allowByteLayoutOnlyTarget)
        {
            if (!requested)
                return null;

            string targetPath = Path.Combine(targetRoot, Level100EnglishDatRelativePath.Replace('/', Path.DirectorySeparatorChar));
            string backupPath = Path.Combine(targetRoot, Level100EnglishDatBackupRelativePath.Replace('/', Path.DirectorySeparatorChar));
            if (!File.Exists(targetPath))
                throw new FileNotFoundException("The copied game does not contain data\\language\\english.dat.", targetPath);

            RejectExistingReparseAncestors(targetPath, "Level 100 English language table path");
            RejectReparsePoint(targetPath, "Level 100 English language table");
            RejectMultipleHardLinks(targetPath, "Level 100 English language table");
            RejectExistingReparseAncestors(backupPath, "Level 100 English language table backup path");
            if (File.Exists(backupPath))
                throw new InvalidOperationException("The copied English language table already has a Level 100 text backup.");

            byte[] originalBytes = File.ReadAllBytes(targetPath);
            string originalSha256 = ComputeSha256(targetPath);
            if (!allowByteLayoutOnlyTarget &&
                !string.Equals(originalSha256, SupportedEnglishDatSha256, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("The copied English language table is not the supported Steam retail specimen.");
            }

            int changedOffset = Level100TutorialTextOffset;
            byte[] expectedBytes = Encoding.Unicode.GetBytes(Level100TutorialOriginalText);
            byte[] replacementBytes = Encoding.Unicode.GetBytes(Level100TutorialReplacementText);
            if (expectedBytes.Length != replacementBytes.Length)
                throw new InvalidOperationException("The Level 100 subtitle replacement must preserve the original UTF-16 byte length.");
            if (changedOffset > originalBytes.Length - expectedBytes.Length - sizeof(ushort) ||
                !originalBytes.AsSpan(changedOffset, expectedBytes.Length).SequenceEqual(expectedBytes) ||
                originalBytes[changedOffset + expectedBytes.Length] != 0 ||
                originalBytes[changedOffset + expectedBytes.Length + 1] != 0)
            {
                throw new InvalidOperationException("The copied English language table does not contain the expected Level 100 TUTORIAL_01 bytes.");
            }

            File.Copy(targetPath, backupPath, overwrite: false);
            byte[] modifiedBytes = originalBytes.ToArray();
            replacementBytes.CopyTo(modifiedBytes, changedOffset);

            string tempPath = Path.Combine(
                Path.GetDirectoryName(targetPath)!,
                $"{Path.GetFileName(targetPath)}.{Guid.NewGuid():N}.tmp");
            try
            {
                File.WriteAllBytes(tempPath, modifiedBytes);
                File.Replace(tempPath, targetPath, null, ignoreMetadataErrors: true);
            }
            finally
            {
                if (File.Exists(tempPath))
                    File.Delete(tempPath);
            }

            RejectReparsePoint(targetPath, "modified Level 100 English language table");
            RejectMultipleHardLinks(targetPath, "Modified Level 100 English language table");
            byte[] readback = File.ReadAllBytes(targetPath);
            if (readback.LongLength != originalBytes.LongLength ||
                !readback.AsSpan().SequenceEqual(modifiedBytes))
            {
                throw new IOException("The copied Level 100 English subtitle replacement did not read back exactly.");
            }

            return new GameProfileLevel100TextModResult(
                Level100TextModSchemaVersion,
                DateTimeOffset.UtcNow,
                Mutation: true,
                TextId: Level100TutorialTextId,
                TargetRelativePath: Level100EnglishDatRelativePath,
                BackupRelativePath: Level100EnglishDatBackupRelativePath,
                OriginalSize: originalBytes.LongLength,
                OriginalSha256: ComputeSha256(backupPath),
                ModifiedSize: readback.LongLength,
                ModifiedSha256: ComputeSha256(targetPath),
                ChangedOffset: changedOffset,
                ChangedByteCount: replacementBytes.Length);
        }

        private static void CopyDirectory(string sourceDirectory, string targetDirectory)
        {
            string sourceRoot = NormalizeExistingDirectory(sourceDirectory);
            RejectReparsePoint(sourceRoot, "source directory");
            Directory.CreateDirectory(targetDirectory);
            var pending = new Stack<string>();
            pending.Push(sourceRoot);
            while (pending.Count > 0)
            {
                string current = pending.Pop();
                RejectReparsePoint(current, "source directory");
                foreach (string directory in Directory.GetDirectories(current))
                {
                    RejectIfOutsideRoot(directory, sourceRoot);
                    RejectReparsePoint(directory, "source directory");
                    string relativePath = Path.GetRelativePath(sourceRoot, directory);
                    Directory.CreateDirectory(Path.Combine(targetDirectory, relativePath));
                    pending.Push(directory);
                }

                foreach (string file in Directory.GetFiles(current))
                {
                    RejectIfOutsideRoot(file, sourceRoot);
                    RejectReparsePoint(file, "source file");
                    RejectMultipleHardLinks(file, "Source file");
                    string relativePath = Path.GetRelativePath(sourceRoot, file);
                    string targetPath = Path.Combine(targetDirectory, relativePath);
                    Directory.CreateDirectory(Path.GetDirectoryName(targetPath)!);
                    File.Copy(file, targetPath, overwrite: false);
                }
            }
        }

        private static void WriteManifest(GameProfilePrepareResult result, string manifestPath)
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            };

            var manifest = new
            {
                result.SchemaVersion,
                result.GeneratedAt,
                result.Mutation,
                SourceGameRoot = "selected-game-root",
                TargetGameRoot = ".",
                ExecutablePath = "BEA.exe",
                ExecutableSize = new FileInfo(result.ExecutablePath).Length,
                ExecutableSha256 = ComputeSha256(result.ExecutablePath),
                Entries = result.Entries.Select(entry => new
                {
                    entry.Name,
                    TargetPath = entry.Name,
                    entry.Directory,
                }).ToArray(),
                PatchResult = new
                {
                    result.PatchResult.Requested,
                    result.PatchResult.Success,
                    result.PatchResult.PatchKeys,
                    Message = result.PatchResult.Success
                        ? "Selected patch bytes verified on disk."
                        : "Patch not applied.",
                },
                ProfilePreset = result.ProfilePresetId is null
                    ? null
                    : new
                    {
                        Id = result.ProfilePresetId,
                        DisplayName = result.ProfilePresetDisplayName,
                        ProofStatus = result.ProfilePresetProofStatus,
                        ProfileCatalogVersion = BinaryPatchPlanBuilder.SafeCopyProfileCatalogVersion,
                        ProfileCatalogSha256 = BinaryPatchPlanBuilder.SafeCopyProfileCatalogSha256,
                        DefaultControllerConfiguration = result.ProfileDefaultControllerConfiguration,
                        DefaultPersistControllerConfigInOptions = result.ProfileDefaultPersistControllerConfigInOptions,
                        DefaultMouseLookSensitivity = result.ProfileDefaultMouseLookSensitivity,
                        DefaultScreenShape = result.ProfileDefaultScreenShape,
                        Modules = result.ProfilePresetModules.Select(module => new
                        {
                            module.Id,
                            module.DisplayName,
                            module.Category,
                            module.ProofStatus,
                            module.ClaimBoundary,
                            module.PatchKeys,
                            module.LaunchArguments,
                            module.CopiedOptionsEdits,
                            module.RestoreStrategy,
                            module.EvidenceRefs,
                            module.NonClaims,
                        }).ToArray(),
                    },
                Level100TextMod = result.Level100TextModResult is null
                    ? null
                    : new
                    {
                        result.Level100TextModResult.SchemaVersion,
                        result.Level100TextModResult.GeneratedAt,
                        result.Level100TextModResult.Mutation,
                        result.Level100TextModResult.TextId,
                        result.Level100TextModResult.TargetRelativePath,
                        result.Level100TextModResult.BackupRelativePath,
                        result.Level100TextModResult.OriginalSize,
                        result.Level100TextModResult.OriginalSha256,
                        result.Level100TextModResult.ModifiedSize,
                        result.Level100TextModResult.ModifiedSha256,
                        result.Level100TextModResult.ChangedOffset,
                        result.Level100TextModResult.ChangedByteCount,
                        ProofStatus = "Rendered in copied Level 100 retail gameplay on the supported Steam English specimen.",
                        ClaimBoundary = "One fixed-size TUTORIAL_01 subtitle replacement only; not a general language importer, script override, texture replacement, or AYA repacker.",
                    },
                MusicSwap = result.MusicSwapResult is null
                    ? null
                    : new
                    {
                        result.MusicSwapResult.SchemaVersion,
                        result.MusicSwapResult.GeneratedAt,
                        result.MusicSwapResult.Mutation,
                        ManifestPath = GameProfileMusicReplacementService.ManifestFileName,
                        result.MusicSwapResult.TargetMusicFileName,
                        result.MusicSwapResult.TargetRelativePath,
                        result.MusicSwapResult.BackupRelativePath,
                        result.MusicSwapResult.OriginalSize,
                        result.MusicSwapResult.OriginalSha256,
                        result.MusicSwapResult.ReplacementSize,
                        result.MusicSwapResult.ReplacementSha256,
                        ProofStatus = "Copied-track staging and restore contract only; runtime playback is not proven.",
                    },
                LaunchPlan = new
                {
                    ExecutablePath = "BEA.exe",
                    WorkingDirectory = ".",
                    result.LaunchPlan.Arguments,
                    CommandPreview = BuildRedactedCommandPreview(result.LaunchPlan.Arguments),
                },
            };

            File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, options));
        }

        private static void EnsureAppOwnedOutputRoot(string sourceRoot, string outputRoot)
        {
            if (IsSameOrUnderRoot(outputRoot, sourceRoot))
            {
                throw new InvalidOperationException("The app-owned output root must not be inside the source game root.");
            }

            if (IsSameOrUnderRoot(sourceRoot, outputRoot))
            {
                throw new InvalidOperationException("The source game root must not be inside the app-owned output root.");
            }
        }

        private static void RejectProtectedOrSteamInstallOutputRoot(string outputRoot)
        {
            if (IsPathUnderProtectedInstallRoot(outputRoot))
            {
                throw new InvalidOperationException("The app-owned output root must not be under Program Files or another protected install root.");
            }

            if (HasKnownSteamInstallShape(outputRoot))
            {
                throw new InvalidOperationException("The app-owned output root must not be under a steamapps/common/Battle Engine Aquila install root.");
            }
        }

        private static string NormalizeExistingDirectory(string path)
        {
            return Path.GetFullPath(path)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        }

        private static string NormalizeDirectoryForCreation(string path)
        {
            if (string.IsNullOrWhiteSpace(path))
                throw new InvalidOperationException("An app-owned output root is required.");

            string normalized = Path.GetFullPath(path)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            if (Directory.Exists(normalized))
                RejectReparsePoint(normalized, "app-owned output root");
            return normalized;
        }

        private static bool IsSameOrUnderRoot(string path, string root)
        {
            string normalizedPath = NormalizeForPrefix(path);
            string normalizedRoot = NormalizeForPrefix(root);
            return string.Equals(normalizedPath.TrimEnd(Path.DirectorySeparatorChar), normalizedRoot.TrimEnd(Path.DirectorySeparatorChar), StringComparison.OrdinalIgnoreCase) ||
                normalizedPath.StartsWith(normalizedRoot, StringComparison.OrdinalIgnoreCase);
        }

        private static bool IsPathUnderProtectedInstallRoot(string path)
        {
            foreach (string root in ProtectedInstallRoots())
            {
                if (IsSameOrUnderRoot(path, root))
                {
                    return true;
                }
            }

            return false;
        }

        private static IEnumerable<string> ProtectedInstallRoots()
        {
            foreach (string key in new[] { "ProgramFiles", "ProgramFiles(x86)" })
            {
                string? raw = Environment.GetEnvironmentVariable(key);
                if (string.IsNullOrWhiteSpace(raw))
                {
                    continue;
                }

                string fullRoot;
                try
                {
                    fullRoot = NormalizeDirectoryForCreation(raw);
                }
                catch (Exception ex) when (ex is ArgumentException or NotSupportedException or PathTooLongException)
                {
                    continue;
                }

                yield return fullRoot;
            }
        }

        private static bool HasKnownSteamInstallShape(string path)
        {
            string fullPath = Path.GetFullPath(path);
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

            return false;
        }

        private static string NormalizeForPrefix(string path)
        {
            return Path.GetFullPath(path)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                + Path.DirectorySeparatorChar;
        }

        private static string BuildRedactedCommandPreview(IReadOnlyList<string> arguments)
        {
            string argumentString = string.Join(" ", arguments);
            return argumentString.Length == 0
                ? "Start-Process -FilePath \"BEA.exe\" -WorkingDirectory \".\""
                : $"Start-Process -FilePath \"BEA.exe\" -WorkingDirectory \".\" -ArgumentList \"{argumentString}\"";
        }

        private static string ComputeSha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
        }

        private static void RejectIfOutsideRoot(string path, string root)
        {
            if (!IsSameOrUnderRoot(path, root))
                throw new InvalidOperationException("Playable copied game folder source traversal escaped the selected game root.");
        }

        private static void RejectReparsePoint(string path, string label)
        {
            FileAttributes attributes = File.GetAttributes(path);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException($"Playable copied game folder preparation refuses reparse points in {label}.");
        }

        private static void RejectMultipleHardLinks(string path, string label)
        {
            if (!OperatingSystem.IsWindows() || !File.Exists(path))
                return;

            uint linkCount = GetWindowsHardLinkCount(path);
            if (linkCount > 1)
                throw new InvalidOperationException($"{label} is hardlinked to another file; refusing to copy a shared file identity into the playable copied game folder.");
        }

        private static uint GetWindowsHardLinkCount(string path)
        {
            using SafeFileHandle handle = File.OpenHandle(
                path,
                FileMode.Open,
                FileAccess.Read,
                FileShare.ReadWrite | FileShare.Delete);

            if (!GetFileInformationByHandle(handle, out ByHandleFileInformation info))
                throw new IOException($"Could not inspect hardlink count for playable copied game folder source. Win32 error: {Marshal.GetLastWin32Error()}");

            return info.NumberOfLinks;
        }

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool GetFileInformationByHandle(
            SafeFileHandle hFile,
            out ByHandleFileInformation lpFileInformation);

        [StructLayout(LayoutKind.Sequential)]
        private struct ByHandleFileInformation
        {
            public uint FileAttributes;
            public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
            public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
            public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
            public uint VolumeSerialNumber;
            public uint FileSizeHigh;
            public uint FileSizeLow;
            public uint NumberOfLinks;
            public uint FileIndexHigh;
            public uint FileIndexLow;
        }

        private static void RejectExistingReparseAncestors(string path, string label)
        {
            string fullPath = Path.GetFullPath(path);
            string? current = Directory.Exists(fullPath)
                ? fullPath
                : Path.GetDirectoryName(fullPath);

            while (!string.IsNullOrWhiteSpace(current))
            {
                if (Directory.Exists(current))
                    RejectReparsePoint(current, label);

                string? parent = Path.GetDirectoryName(current);
                if (string.Equals(parent, current, StringComparison.OrdinalIgnoreCase))
                    break;

                current = parent;
            }
        }

        private static void DeleteGeneratedTarget(string targetRoot, string outputRoot)
        {
            if (!Directory.Exists(targetRoot))
                return;

            string normalizedOutput = NormalizeDirectoryForCreation(outputRoot);
            string normalizedTarget = NormalizeExistingDirectory(targetRoot);
            RejectExistingReparseAncestors(normalizedOutput, "app-owned output root");
            RejectExistingReparseAncestors(normalizedTarget, "playable copied game folder target");
            if (!IsSameOrUnderRoot(normalizedTarget, normalizedOutput) ||
                string.Equals(normalizedTarget, normalizedOutput, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Refusing to clean a playable copied game folder target outside the app-owned output root.");
            }

            Directory.Delete(normalizedTarget, recursive: true);
        }
    }
}
