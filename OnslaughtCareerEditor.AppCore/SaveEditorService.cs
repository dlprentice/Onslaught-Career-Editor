using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    public sealed class SavePatchRequest
    {
        public string InputPath { get; init; } = string.Empty;
        public string OutputPath { get; init; } = string.Empty;
        /// <summary>Baseline mission grade. Null means "keep": untargeted missions are not written at all.</summary>
        public string? Rank { get; init; }

        /// <summary>Goodie style. Null means "not configured".</summary>
        public bool? UseNewGoodiesInstead { get; init; }

        /// <summary>Baseline kill count. Null means "keep": untargeted categories are not written at all.</summary>
        public int? GlobalKillCount { get; init; }

        public bool PatchNodes { get; init; } = true;
        public bool PatchLinks { get; init; } = true;
        public bool PatchGoodies { get; init; } = true;
        public bool PatchKills { get; init; } = true;
        public Dictionary<int, string>? LevelRanks { get; init; }
        public Dictionary<int, int>? PerCategoryKills { get; init; }

        /// <summary>
        /// Project onto the shape <see cref="SavePatchIntentContract"/> reads. Every payload property
        /// above must appear here; <c>SavePatchIntentCoverageTests</c> fails otherwise.
        /// </summary>
        public SavePatchIntentSnapshot ToIntentSnapshot() => new()
        {
            Rank = Rank,
            UseNewGoodiesInstead = UseNewGoodiesInstead,
            GlobalKillCount = GlobalKillCount,
            LevelRanks = LevelRanks,
            PerCategoryKills = PerCategoryKills,
            PatchNodes = PatchNodes,
            PatchLinks = PatchLinks,
            PatchGoodies = PatchGoodies,
            PatchKills = PatchKills
        };
    }

    public sealed class FocusedGoodieStatePatchRequest
    {
        public string InputPath { get; init; } = string.Empty;
        public string OutputPath { get; init; } = string.Empty;
        public int GoodieId { get; init; }
        public MissionScriptGoodieState State { get; init; } = MissionScriptGoodieState.New;
    }

    public static class SaveEditorService
    {
        public static IReadOnlyList<SaveAnalyzerFileItem> GetDetectedCareerSaves(string? gameDir = null)
        {
            return SaveAnalyzerService.GetDetectedFiles(gameDir)
                .Where(item => !IsOptionsLikeFilePath(item.Path))
                .ToArray();
        }

        public static bool IsOptionsLikeFilePath(string? filePath)
        {
            if (string.IsNullOrWhiteSpace(filePath))
            {
                return false;
            }

            string trimmed = filePath.Trim();
            string fileNameOnly = Path.GetFileName(trimmed);
            return string.Equals(Path.GetExtension(trimmed), ".bea", StringComparison.OrdinalIgnoreCase)
                || fileNameOnly.StartsWith("defaultoptions.bea", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Say why a chosen input is not usable, or null when it is.
        ///
        /// The UI used to collapse "file missing", "that is a .bea options file", "wrong length" and
        /// "wrong version word" into one sentence, and <see cref="BesFilePatcher.IsValidBesFile"/>
        /// swallowed its exception into <c>Debug.WriteLine</c>, which is invisible in a release build.
        /// The user was told the input was invalid and never told why.
        /// </summary>
        public static string? DescribeCareerSaveInputRejection(string? filePath)
        {
            string trimmed = (filePath ?? string.Empty).Trim();
            if (trimmed.Length == 0)
            {
                return "Choose a .bes career save.";
            }

            if (IsOptionsLikeFilePath(trimmed))
            {
                return "That file is a game options file (.bea / defaultoptions), not a career save. " +
                       "Game Options edits those; the Save Editor needs a .bes career save.";
            }

            if (!IsCareerSaveFilePath(trimmed))
            {
                return $"A career save must have the .bes extension. This one ends in " +
                       $"'{Path.GetExtension(trimmed)}'.";
            }

            FileInfo info;
            try
            {
                info = new FileInfo(trimmed);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or NotSupportedException
                                        or UnauthorizedAccessException or System.Security.SecurityException)
            {
                return $"That path could not be read: {ex.Message}";
            }

            if (!info.Exists)
            {
                return "No file exists at that path.";
            }

            if (info.Length != BesFilePatcher.EXPECTED_FILE_SIZE)
            {
                return $"A Battle Engine Aquila career save is exactly {BesFilePatcher.EXPECTED_FILE_SIZE:N0} bytes. " +
                       $"This file is {info.Length:N0}.";
            }

            try
            {
                using FileStream stream = File.OpenRead(trimmed);
                Span<byte> header = stackalloc byte[2];
                if (stream.Read(header) != 2)
                {
                    return "That file is the right size but its first two bytes could not be read.";
                }

                ushort versionWord = System.Buffers.Binary.BinaryPrimitives.ReadUInt16LittleEndian(header);
                if (versionWord != BesFilePatcher.VERSION_WORD)
                {
                    return $"That file is the right size but its version word is 0x{versionWord:X4}; a career save " +
                           $"starts with 0x{BesFilePatcher.VERSION_WORD:X4}.";
                }
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or NotSupportedException
                                        or System.Security.SecurityException)
            {
                return $"That file could not be opened: {ex.Message}";
            }

            return null;
        }

        public static bool IsCareerSaveFilePath(string? filePath)
        {
            return !string.IsNullOrWhiteSpace(filePath) &&
                string.Equals(Path.GetExtension(filePath.Trim()), ".bes", StringComparison.OrdinalIgnoreCase);
        }

        public static string BuildDefaultSaveOutputPath(string inputPath, string? outputDirectory = null)
        {
            string fileName = Path.GetFileNameWithoutExtension(inputPath);
            string extension = Path.GetExtension(inputPath);
            if (string.IsNullOrWhiteSpace(fileName))
                fileName = "patched-output";
            if (!string.Equals(extension, ".bes", StringComparison.OrdinalIgnoreCase) &&
                !string.Equals(extension, ".bea", StringComparison.OrdinalIgnoreCase))
            {
                extension = ".bes";
            }

            string directory = string.IsNullOrWhiteSpace(outputDirectory)
                ? AppConfig.GetPatchedOutputDir()
                : Path.GetFullPath(outputDirectory);
            return Path.Combine(directory, $"{fileName}_patched{extension}");
        }

        /// <summary>
        /// Which of the Save Editor's two write actions produced a file.
        /// </summary>
        public enum SaveEditorWriteKind
        {
            FullPatch,
            FocusedGoodieState
        }

        /// <summary>
        /// Warn when the write about to run would erase the other write action's result.
        ///
        /// Both Save Editor write buttons read the same output path box and both re-read the *input*
        /// save, so they do not compose: running one after the other replaces the first result instead
        /// of building on it, and both report success with a green InfoBar. A user who writes a focused
        /// Goodie and then clicks Patch loses the Goodie edit with nothing said.
        ///
        /// Returns null when there is nothing to lose: no previous write, a different destination, or
        /// the same action re-running (which genuinely does just redo itself from the same input).
        /// </summary>
        public static string? DescribeWriteCompositionLoss(
            SaveEditorWriteKind? previousWriteKind,
            string? previousOutputPath,
            SaveEditorWriteKind nextWriteKind,
            string? nextOutputPath)
        {
            if (previousWriteKind is not { } previous || previous == nextWriteKind)
            {
                return null;
            }

            string previousPath = (previousOutputPath ?? string.Empty).Trim();
            string nextPath = (nextOutputPath ?? string.Empty).Trim();
            if (previousPath.Length == 0 || nextPath.Length == 0)
            {
                return null;
            }

            bool samePath;
            try
            {
                samePath = FileMutationSafety.AreLexicallySamePath(previousPath, nextPath);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException
                                        or NotSupportedException)
            {
                samePath = string.Equals(previousPath, nextPath, StringComparison.OrdinalIgnoreCase);
            }

            if (!samePath)
            {
                return null;
            }

            string previousLabel = previous == SaveEditorWriteKind.FocusedGoodieState
                ? "the focused Goodie state"
                : "the section patch";
            string nextLabel = nextWriteKind == SaveEditorWriteKind.FocusedGoodieState
                ? "Writing the focused Goodie state"
                : "Patching the selected sections";

            return $"{nextLabel} re-reads the input save from scratch, so it does not build on {previousLabel} " +
                   "you already wrote to this same output file - that earlier edit will be gone. " +
                   "To combine both, point this write at the file you produced last time instead of at the " +
                   "original input.";
        }

        public static bool HasAnySelectedSection(SavePatchRequest request)
        {
            return request.PatchNodes || request.PatchLinks || request.PatchGoodies || request.PatchKills;
        }

        public static string BuildPendingChangesSummary(SavePatchRequest request)
        {
            List<string> parts = new();
            if (request.PatchNodes)
            {
                // Do not claim "missions" when the baseline is Keep: under keep semantics only the
                // missions carrying an explicit override are written at all.
                parts.Add(request.Rank is null
                    ? "only the missions overridden below (all other missions untouched)"
                    : "missions");
            }

            if (request.PatchLinks)
            {
                parts.Add("links");
            }

            if (request.PatchGoodies)
            {
                parts.Add(request.UseNewGoodiesInstead == true ? "goodies as NEW" : "goodies as OLD");
            }

            if (request.PatchKills)
            {
                parts.Add(request.GlobalKillCount is { } globalKills
                    ? $"kills -> {ClampGlobalKillValue(globalKills):N0}"
                    : "kills kept except the categories overridden below");
            }

            if (request.LevelRanks is { Count: > 0 })
            {
                string label = request.LevelRanks.Count == 1 ? "1 mission rank override" : $"{request.LevelRanks.Count} mission rank overrides";
                parts.Add(request.PatchNodes ? label : $"{label} (blocked: needs missions)");
            }

            if (request.PerCategoryKills is { Count: > 0 })
            {
                string label = request.PerCategoryKills.Count == 1 ? "1 category kill override" : $"{request.PerCategoryKills.Count} category kill overrides";
                parts.Add(request.PatchKills ? label : $"{label} (blocked: needs kill counts)");
            }

            if (parts.Count == 0)
            {
                return "No pending save changes selected yet.";
            }

            return "Pending: " + string.Join(", ", parts) + ".";
        }

        public static PatchResult PatchSave(SavePatchRequest request)
        {
            string inputPath = request.InputPath?.Trim() ?? string.Empty;
            string outputPath = request.OutputPath?.Trim() ?? string.Empty;
            if (inputPath.Length == 0 || outputPath.Length == 0)
            {
                return PatchResult.Fail("Select both input and output files before patching.");
            }

            if (!IsCareerSaveFilePath(inputPath) || !IsCareerSaveFilePath(outputPath))
            {
                return PatchResult.Fail("Save Editor requires .bes career save input and output paths.");
            }

            try
            {
                if (FileMutationSafety.AreLexicallySamePath(inputPath, outputPath))
                    return PatchResult.Fail("Output file must be different from input file. In-place save patching is blocked.");
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException)
            {
                return PatchResult.Fail(ex.Message);
            }

            if (!File.Exists(inputPath))
            {
                return PatchResult.Fail($"Input file not found: {inputPath}");
            }

            if (!HasAnySelectedSection(request))
            {
                return PatchResult.Fail("Choose at least one save section to patch.");
            }

            // This adapter must never manufacture a value the caller did not supply. It used to coerce a
            // null/blank Rank back to "S" and a defaulted GlobalKillCount straight through, which would
            // have re-opened the exact hole the nullable request shape exists to close.
            BesFilePatcher patcher = new()
            {
                Rank = string.IsNullOrWhiteSpace(request.Rank) ? null : request.Rank.Trim().ToUpperInvariant(),
                UseNewGoodiesInstead = request.UseNewGoodiesInstead,
                GlobalKillCount = request.GlobalKillCount is { } killCount ? ClampGlobalKillValue(killCount) : null,
                PatchNodes = request.PatchNodes,
                PatchLinks = request.PatchLinks,
                PatchGoodies = request.PatchGoodies,
                PatchKills = request.PatchKills,
                LevelRanks = request.LevelRanks,
                PerCategoryKills = request.PerCategoryKills
            };

            return patcher.PatchFile(inputPath, outputPath);
        }

        public static PatchResult PatchFocusedGoodieState(FocusedGoodieStatePatchRequest request)
        {
            ArgumentNullException.ThrowIfNull(request);

            string inputPath = request.InputPath?.Trim() ?? string.Empty;
            string outputPath = request.OutputPath?.Trim() ?? string.Empty;
            if (inputPath.Length == 0 || outputPath.Length == 0)
            {
                return PatchResult.Fail("Select both input and output files before patching.");
            }

            if (!IsCareerSaveFilePath(inputPath) || !IsCareerSaveFilePath(outputPath))
            {
                return PatchResult.Fail("Focused Goodie state patching requires .bes input and output paths.");
            }

            if ((uint)request.GoodieId >= MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount)
            {
                return PatchResult.Fail(
                    $"Goodie ID must be from 0 to {MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount - 1}.");
            }

            if ((uint)request.State > MissionScriptGoodieStateSaveCodec.MaxKnownStateValue)
            {
                return PatchResult.Fail("Goodie state must be Locked, Locked with hint, New, or Old.");
            }

            try
            {
                inputPath = FileMutationSafety.NormalizeLocalPath(inputPath, "Input path");
                outputPath = FileMutationSafety.NormalizeLocalPath(outputPath, "Output path");
                if (FileMutationSafety.AreLexicallySamePath(inputPath, outputPath))
                {
                    return PatchResult.Fail("Output file must be different from input file. In-place save patching is blocked.");
                }

                if (!File.Exists(inputPath))
                {
                    return PatchResult.Fail($"Input file not found: {inputPath}");
                }

                IReadOnlyDictionary<int, uint> stateOverride = new Dictionary<int, uint>
                {
                    [request.GoodieId] = (uint)request.State
                };

                string appOwnedProfilesRoot = FileMutationSafety.NormalizeLocalPath(
                    AppConfig.GetGameProfilesDir(),
                    "App-owned profiles root");
                if (!FileMutationSafety.IsSameOrUnderRoot(outputPath, appOwnedProfilesRoot))
                {
                    return BesFilePatcher.PatchGoodieStates(inputPath, outputPath, stateOverride);
                }

                string relativeOutput = Path.GetRelativePath(appOwnedProfilesRoot, outputPath);
                string[] segments = relativeOutput.Split(
                    new[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar },
                    StringSplitOptions.RemoveEmptyEntries);
                if (segments.Length != 3 ||
                    !string.Equals(segments[1], "savegames", StringComparison.OrdinalIgnoreCase))
                {
                    return PatchResult.Fail(
                        "Safe-copy Goodie output must be one .bes file directly inside a verified profile's savegames folder.");
                }

                string profileRoot = Path.Combine(appOwnedProfilesRoot, segments[0]);
                _ = GameProfilePreflightService.ValidateSaveStagingProfileRoot(profileRoot);
                using FileMutationSafety.AppOwnedProfileMutationAuthorization outputAuthorization =
                    FileMutationSafety.AuthorizeAppOwnedProfileRoot(profileRoot, appOwnedProfilesRoot);

                string savegamesDirectory = Path.Combine(profileRoot, "savegames");
                Directory.CreateDirectory(savegamesDirectory);
                FileMutationSafety.RejectExistingReparseAncestors(
                    savegamesDirectory,
                    "Safe-copy savegames folder");

                return BesFilePatcher.PatchGoodieStates(
                    inputPath,
                    outputPath,
                    stateOverride,
                    outputAuthorization);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException)
            {
                return PatchResult.Fail(ex.Message);
            }
        }

        private static int ClampGlobalKillValue(int value)
        {
            if (value < 0)
            {
                return 0;
            }

            if (value > 0x00FFFFFF)
            {
                return 0x00FFFFFF;
            }

            return value;
        }

    }
}
