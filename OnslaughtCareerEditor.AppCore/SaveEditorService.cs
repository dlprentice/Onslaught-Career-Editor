using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
{
    public sealed class SavePatchRequest
    {
        public string InputPath { get; init; } = string.Empty;
        public string OutputPath { get; init; } = string.Empty;
        public string Rank { get; init; } = "S";
        public bool UseNewGoodiesInstead { get; init; }
        public int GlobalKillCount { get; init; } = 100;
        public bool PatchNodes { get; init; } = true;
        public bool PatchLinks { get; init; } = true;
        public bool PatchGoodies { get; init; } = true;
        public bool PatchKills { get; init; } = true;
        public Dictionary<int, string>? LevelRanks { get; init; }
        public Dictionary<int, int>? PerCategoryKills { get; init; }
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

        public static bool HasAnySelectedSection(SavePatchRequest request)
        {
            return request.PatchNodes || request.PatchLinks || request.PatchGoodies || request.PatchKills;
        }

        public static string BuildPendingChangesSummary(SavePatchRequest request)
        {
            List<string> parts = new();
            if (request.PatchNodes)
            {
                parts.Add("missions");
            }

            if (request.PatchLinks)
            {
                parts.Add("links");
            }

            if (request.PatchGoodies)
            {
                parts.Add(request.UseNewGoodiesInstead ? "goodies as NEW" : "goodies as OLD");
            }

            if (request.PatchKills)
            {
                parts.Add($"kills -> {ClampGlobalKillValue(request.GlobalKillCount):N0}");
            }

            if (request.LevelRanks is { Count: > 0 })
            {
                parts.Add(request.LevelRanks.Count == 1 ? "1 mission rank override" : $"{request.LevelRanks.Count} mission rank overrides");
            }

            if (request.PerCategoryKills is { Count: > 0 })
            {
                parts.Add(request.PerCategoryKills.Count == 1 ? "1 category kill override" : $"{request.PerCategoryKills.Count} category kill overrides");
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

            BesFilePatcher patcher = new()
            {
                Rank = string.IsNullOrWhiteSpace(request.Rank) ? "S" : request.Rank.Trim().ToUpperInvariant(),
                UseNewGoodiesInstead = request.UseNewGoodiesInstead,
                GlobalKillCount = ClampGlobalKillValue(request.GlobalKillCount),
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
                return PatchResult.Fail("Goodie state must be Locked, Instructions, New, or Old.");
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
