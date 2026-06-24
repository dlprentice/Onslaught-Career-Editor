using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class GameProfilePreflightServiceTests
    {
        [Fact]
        public void BuildPrepareReceipt_SummarizesEnhancedProfileWithoutRuntimeOrOnlineClaims()
        {
            SafeCopyProfilePreset preset = BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.EnhancedPreviewProfileId);
            string[] enhancedKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(preset.Id).ToArray();
            var result = new GameProfilePrepareResult(
                GameProfilePreflightService.SchemaVersion,
                DateTimeOffset.UnixEpoch,
                Mutation: true,
                SourceGameRoot: "selected-game-root",
                TargetGameRoot: @"X:\AppOwnedProfiles\safe-game-copy-test",
                ExecutablePath: @"X:\AppOwnedProfiles\safe-game-copy-test\BEA.exe",
                Entries: new[]
                {
                    new GameProfileCopiedEntry("BEA.exe", @"C:\Source\BEA.exe", @"C:\Target\BEA.exe", Directory: false),
                    new GameProfileCopiedEntry("data", @"C:\Source\data", @"C:\Target\data", Directory: true),
                    new GameProfileCopiedEntry("savegames", @"C:\Source\savegames", @"C:\Target\savegames", Directory: true),
                },
                PatchResult: new GameProfilePatchResult(
                    Requested: true,
                    Success: true,
                    PatchKeys: enhancedKeys,
                    Message: "Selected patch bytes verified on disk."),
                LaunchPlan: new GameProfileLaunchPlan(
                    ExecutablePath: @"C:\Target\BEA.exe",
                    WorkingDirectory: @"C:\Target",
                    Arguments: new[] { "-skipfmv", "-level", "850" },
                    CommandPreview: "\"BEA.exe\" -skipfmv -level 850"),
                ProfilePresetId: preset.Id,
                ProfilePresetDisplayName: preset.DisplayName,
                ProfilePresetProofStatus: preset.ProofStatus,
                ProfileDefaultControllerConfiguration: preset.DefaultControllerConfiguration,
                ProfileDefaultPersistControllerConfigInOptions: preset.DefaultPersistControllerConfigInOptions,
                ProfileDefaultSharpenMouseLook: preset.DefaultSharpenMouseLook,
                ProfilePresetModules: preset.Modules,
                MusicSwapResult: null,
                ManifestPath: @"C:\Target\onslaught-profile-manifest.json");

            GameProfilePrepareReceipt receipt = GameProfilePreflightService.BuildPrepareReceipt(
                result,
                copiedSavegames: true,
                controlOptionsResult: null);

            Assert.Equal("Safe copy ready", receipt.Headline);
            Assert.Contains(receipt.Lines, line => line.Label == "Profile" && line.Value == "Enhanced Profile Preview");
            Assert.Contains(receipt.Lines, line => line.Label == "Safe copy folder" && line.Value == "safe-game-copy-test");
            Assert.Contains(receipt.Lines, line => line.Label == "Launch modifiers" && line.Value.Contains("-level 850", StringComparison.Ordinal));
            Assert.Contains(receipt.Lines, line => line.Label == "Savegames" && line.Value.Contains("copied into this safe copy only", StringComparison.Ordinal));
            Assert.Contains(receipt.IncludedChanges, change => change.Contains("Windowed compatibility", StringComparison.Ordinal));
            Assert.Contains(receipt.IncludedChanges, change => change.Contains("Red frontend margins", StringComparison.Ordinal));
            Assert.DoesNotContain(receipt.IncludedChanges, change => change.Contains("Copied control defaults", StringComparison.Ordinal));
            Assert.Contains(receipt.IncludedChanges, change => change.Contains("no control-options manifest was written", StringComparison.Ordinal));
            Assert.Contains(receipt.StillNotIncluded, item => item.Contains("No Host/Join or online multiplayer", StringComparison.Ordinal));
            Assert.Contains(receipt.StillNotIncluded, item => item.Contains("No installed-game mutation", StringComparison.Ordinal));
            Assert.Contains(receipt.StillNotIncluded, item => item.Contains("No fixed Enhanced copied-control-default claim", StringComparison.Ordinal));
            Assert.DoesNotContain(receipt.StillNotIncluded, item => item.Contains("online ready", StringComparison.OrdinalIgnoreCase));
            Assert.DoesNotContain(receipt.Lines, line => line.Value.Contains(@"C:\Users", StringComparison.OrdinalIgnoreCase));
            Assert.DoesNotContain(receipt.Lines, line => line.Value.Contains("AppData", StringComparison.OrdinalIgnoreCase));
            Assert.DoesNotContain(receipt.Lines, line => line.Value.Contains("selected-game-root", StringComparison.OrdinalIgnoreCase));
            string receiptText = FlattenPrepareReceipt(receipt);
            Assert.DoesNotContain("accepted combined safe-copy launch/capture/source-safety proof", receiptText, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("Proof-bounded preset", receiptText, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(@"X:\AppOwnedProfiles", receiptText, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(@"C:\Source", receiptText, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(@"C:\Target", receiptText, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void BuildPrepareReceipt_OnlyListsEnhancedControlDefaultsWhenAppliedOptionsMatchPreset()
        {
            SafeCopyProfilePreset preset = BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.EnhancedPreviewProfileId);
            string[] enhancedKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(preset.Id).ToArray();
            var result = new GameProfilePrepareResult(
                GameProfilePreflightService.SchemaVersion,
                DateTimeOffset.UnixEpoch,
                Mutation: true,
                SourceGameRoot: "selected-game-root",
                TargetGameRoot: @"X:\AppOwnedProfiles\safe-game-copy-test",
                ExecutablePath: @"X:\AppOwnedProfiles\safe-game-copy-test\BEA.exe",
                Entries: new[]
                {
                    new GameProfileCopiedEntry("BEA.exe", @"C:\Source\BEA.exe", @"C:\Target\BEA.exe", Directory: false),
                },
                PatchResult: new GameProfilePatchResult(
                    Requested: true,
                    Success: true,
                    PatchKeys: enhancedKeys,
                    Message: "Selected patch bytes verified on disk."),
                LaunchPlan: new GameProfileLaunchPlan(
                    ExecutablePath: @"C:\Target\BEA.exe",
                    WorkingDirectory: @"C:\Target",
                    Arguments: Array.Empty<string>(),
                    CommandPreview: "\"BEA.exe\""),
                ProfilePresetId: preset.Id,
                ProfilePresetDisplayName: preset.DisplayName,
                ProfilePresetProofStatus: preset.ProofStatus,
                ProfileDefaultControllerConfiguration: preset.DefaultControllerConfiguration,
                ProfileDefaultPersistControllerConfigInOptions: preset.DefaultPersistControllerConfigInOptions,
                ProfileDefaultSharpenMouseLook: preset.DefaultSharpenMouseLook,
                ProfilePresetModules: preset.Modules,
                MusicSwapResult: null,
                ManifestPath: @"C:\Target\onslaught-profile-manifest.json");
            var matchingControls = new GameProfileControlOptionsResult(
                OptionsPath: @"X:\AppOwnedProfiles\safe-game-copy-test\defaultoptions.bea",
                MouseSensitivity: GameProfileControlOptionsService.SharperMouseLookSensitivity,
                ControllerConfigP1: 1,
                ControllerConfigP2: 1,
                InvertWalkerP1: false,
                InvertWalkerP2: false,
                InvertFlightP1: false,
                InvertFlightP2: false,
                HashBefore: new string('a', 64),
                HashAfter: new string('b', 64),
                ChangedRanges: Array.Empty<GameProfileControlOptionsChangeRange>(),
                Backups: Array.Empty<GameProfileControlOptionsBackup>(),
                ManifestPath: @"X:\AppOwnedProfiles\safe-game-copy-test\onslaught-control-options-manifest.json",
                ProofStatus: GameProfileControlOptionsService.ProofStatusOptionsByteMaterializedOnly,
                Message: "Control options materialized.");
            var customControls = matchingControls with
            {
                MouseSensitivity = GameProfileControlOptionsService.FastMouseLookSensitivity,
            };

            GameProfilePrepareReceipt matchingReceipt = GameProfilePreflightService.BuildPrepareReceipt(
                result,
                copiedSavegames: false,
                matchingControls);
            GameProfilePrepareReceipt customReceipt = GameProfilePreflightService.BuildPrepareReceipt(
                result,
                copiedSavegames: false,
                customControls);

            Assert.Contains(matchingReceipt.IncludedChanges, change => change.Contains("Copied control defaults", StringComparison.Ordinal));
            Assert.DoesNotContain(matchingReceipt.IncludedChanges, change => change.Contains("custom control-options manifest", StringComparison.Ordinal));
            Assert.DoesNotContain(customReceipt.IncludedChanges, change => change.Contains("Copied control defaults", StringComparison.Ordinal));
            Assert.Contains(customReceipt.IncludedChanges, change => change.Contains("custom control-options manifest", StringComparison.Ordinal));
            Assert.Contains(customReceipt.StillNotIncluded, item => item.Contains("No fixed Enhanced copied-control-default claim", StringComparison.Ordinal));
        }

        [Fact]
        public void BuildPrepareReceipt_RecordsMutedMusicWhenSwapIsStagedWithNoMusicLaunchArg()
        {
            SafeCopyProfilePreset preset = BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.RecommendedProfileId);
            var musicSwap = new GameProfileMusicReplacementResult(
                SchemaVersion: "winui-safe-copy-music-replacement.v1",
                GeneratedAt: DateTimeOffset.UnixEpoch,
                Mutation: true,
                TargetMusicFileName: "BEA_01(Master).ogg",
                TargetRelativePath: @"data\Music\BEA_01(Master).ogg",
                BackupRelativePath: @"data\Music\BEA_01(Master).ogg.original",
                TargetPath: @"X:\AppOwnedProfiles\safe-game-copy-test\data\Music\BEA_01(Master).ogg",
                BackupPath: @"X:\AppOwnedProfiles\safe-game-copy-test\data\Music\BEA_01(Master).ogg.original",
                ManifestPath: @"X:\AppOwnedProfiles\safe-game-copy-test\onslaught-music-replacement-manifest.json",
                OriginalSize: 10,
                OriginalSha256: new string('a', 64),
                ReplacementSize: 10,
                ReplacementSha256: new string('b', 64));
            var result = new GameProfilePrepareResult(
                GameProfilePreflightService.SchemaVersion,
                DateTimeOffset.UnixEpoch,
                Mutation: true,
                SourceGameRoot: "selected-game-root",
                TargetGameRoot: @"X:\AppOwnedProfiles\safe-game-copy-test",
                ExecutablePath: @"X:\AppOwnedProfiles\safe-game-copy-test\BEA.exe",
                Entries: new[]
                {
                    new GameProfileCopiedEntry("BEA.exe", @"X:\Source\BEA.exe", @"X:\Target\BEA.exe", Directory: false),
                },
                PatchResult: new GameProfilePatchResult(
                    Requested: true,
                    Success: true,
                    PatchKeys: BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(preset.Id).ToArray(),
                    Message: "Selected patch bytes verified on disk."),
                LaunchPlan: new GameProfileLaunchPlan(
                    ExecutablePath: @"X:\Target\BEA.exe",
                    WorkingDirectory: @"X:\Target",
                    Arguments: new[] { "-skipfmv", "-nomusic" },
                    CommandPreview: "\"BEA.exe\" -skipfmv -nomusic"),
                ProfilePresetId: preset.Id,
                ProfilePresetDisplayName: preset.DisplayName,
                ProfilePresetProofStatus: preset.ProofStatus,
                ProfileDefaultControllerConfiguration: preset.DefaultControllerConfiguration,
                ProfileDefaultPersistControllerConfigInOptions: preset.DefaultPersistControllerConfigInOptions,
                ProfileDefaultSharpenMouseLook: preset.DefaultSharpenMouseLook,
                ProfilePresetModules: preset.Modules,
                MusicSwapResult: musicSwap,
                ManifestPath: @"X:\Target\onslaught-profile-manifest.json");

            GameProfilePrepareReceipt receipt = GameProfilePreflightService.BuildPrepareReceipt(
                result,
                copiedSavegames: false,
                controlOptionsResult: null);

            Assert.Contains(receipt.Lines, line => line.Label == "Music swap" && line.Value.Contains("BEA_01(Master).ogg", StringComparison.Ordinal));
            Assert.Contains(receipt.Lines, line => line.Label == "Launch modifiers" && line.Value.Contains("-nomusic", StringComparison.Ordinal));
            Assert.Contains(receipt.StillNotIncluded, item => item.Contains("Music is muted for this launch", StringComparison.Ordinal));
        }

        private static string FlattenPrepareReceipt(GameProfilePrepareReceipt receipt)
        {
            return string.Join(
                "\n",
                receipt.Lines.Select(line => $"{line.Label}: {line.Value}")
                    .Concat(receipt.IncludedChanges)
                    .Concat(receipt.StillNotIncluded));
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_CopiesGameRootAppliesPatchAndLeavesSourceUnchanged()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-proof-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] sourceHashBefore = SHA256.HashData(File.ReadAllBytes(sourceExe));

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "windowed-proof",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true));

                Assert.Equal("winui-copied-game-profile.v1", result.SchemaVersion);
                Assert.Equal(Path.GetFullPath(Path.Combine(outputRoot, "windowed-proof")), result.TargetGameRoot);
                Assert.True(File.Exists(result.ExecutablePath));
                Assert.True(File.Exists(Path.Combine(result.TargetGameRoot, "defaultoptions.bea")));
                Assert.True(File.Exists(Path.Combine(result.TargetGameRoot, "data", "Resources", "base_res_PC.aya")));
                Assert.True(File.Exists(Path.Combine(result.TargetGameRoot, "cardid.txt")));
                Assert.False(Directory.Exists(Path.Combine(result.TargetGameRoot, "savegames")), "Private save folders should not be copied by default.");
                Assert.True(File.Exists(result.ManifestPath));
                Assert.True(File.Exists(BinaryPatchEngine.BuildBackupPath(result.ExecutablePath)));
                Assert.Equal(sourceHashBefore, SHA256.HashData(File.ReadAllBytes(sourceExe)));

                Assert.True(result.PatchResult.Requested);
                Assert.True(result.PatchResult.Success, result.PatchResult.Message);
                Assert.Equal(new[] { "resolution_gate", "force_windowed" }, result.PatchResult.PatchKeys);

                byte[] targetData = File.ReadAllBytes(result.ExecutablePath);
                foreach (string patchKey in result.PatchResult.PatchKeys)
                {
                    BinaryPatchSpec spec = BinaryPatchEngine.PatchSpecs.Single(row => row.Key == patchKey);
                    Assert.Equal(spec.Patched, targetData.Skip(spec.FileOffset).Take(spec.Patched.Length).ToArray());
                }

                Assert.Equal(result.ExecutablePath, result.LaunchPlan.ExecutablePath);
                Assert.Equal(result.TargetGameRoot, result.LaunchPlan.WorkingDirectory);
                Assert.Empty(result.LaunchPlan.Arguments);
                Assert.Contains("Start-Process", result.LaunchPlan.CommandPreview);
                Assert.DoesNotContain("-forcewindowed", result.LaunchPlan.CommandPreview, StringComparison.OrdinalIgnoreCase);

                using JsonDocument manifest = JsonDocument.Parse(File.ReadAllText(result.ManifestPath));
                Assert.Equal("winui-copied-game-profile.v1", manifest.RootElement.GetProperty("schemaVersion").GetString());
                Assert.True(manifest.RootElement.GetProperty("mutation").GetBoolean());
                Assert.Equal(".", manifest.RootElement.GetProperty("targetGameRoot").GetString());
                Assert.Equal("BEA.exe", manifest.RootElement.GetProperty("executablePath").GetString());
                Assert.DoesNotContain(tempRoot, File.ReadAllText(result.ManifestPath), StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_CopiesSavegamesOnlyWhenExplicitlySelected()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-savegames-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            string sourceSave = Path.Combine(sourceRoot, "savegames", "career01.bes");
            byte[] sourceSaveBefore = File.ReadAllBytes(sourceSave);

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "with-savegames",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true,
                        IncludeSavegames: true));

                string copiedSave = Path.Combine(result.TargetGameRoot, "savegames", "career01.bes");
                Assert.True(File.Exists(copiedSave));
                Assert.Equal(sourceSaveBefore, File.ReadAllBytes(copiedSave));
                Assert.Equal(sourceSaveBefore, File.ReadAllBytes(sourceSave));
                Assert.Contains(result.Entries, entry =>
                    string.Equals(entry.Name, "savegames", StringComparison.OrdinalIgnoreCase) &&
                    entry.Directory);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsSteamInstallShapedOutputRootBeforeCopy()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-output-steam-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "steamapps", "common", "Battle Engine Aquila", "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);

            try
            {
                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "steam-output",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("steamapps/common/Battle Engine Aquila", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(outputRoot, "steam-output")));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsProtectedInstallOutputRootBeforeCopy()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-output-protected-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string fakeProtectedRoot = Path.Combine(tempRoot, "FakeProgramFiles");
            string outputRoot = Path.Combine(fakeProtectedRoot, "OnslaughtProfiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            string? originalProgramFiles = Environment.GetEnvironmentVariable("ProgramFiles");
            string? originalProgramFilesX86 = Environment.GetEnvironmentVariable("ProgramFiles(x86)");

            try
            {
                Directory.CreateDirectory(fakeProtectedRoot);
                Environment.SetEnvironmentVariable("ProgramFiles", fakeProtectedRoot);
                Environment.SetEnvironmentVariable("ProgramFiles(x86)", Path.Combine(tempRoot, "FakeProgramFilesX86"));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "protected-output",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("protected install root", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(outputRoot, "protected-output")));
            }
            finally
            {
                Environment.SetEnvironmentVariable("ProgramFiles", originalProgramFiles);
                Environment.SetEnvironmentVariable("ProgramFiles(x86)", originalProgramFilesX86);

                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_AppliesSelectedVisiblePatchRowsToSafeCopyOnly()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-selected-patches-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] sourceHashBefore = SHA256.HashData(File.ReadAllBytes(sourceExe));

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "selected-patches",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true,
                        PatchKeys: new[]
                        {
                            "extra_graphics_default_on",
                            "version_overlay_use_patched_format_pointer"
                        }));

                string[] expectedPatchKeys =
                {
                    "extra_graphics_default_on",
                    "version_overlay_use_patched_format_pointer",
                    "resolution_gate",
                    "force_windowed",
                    "version_overlay_patched_format_cave_string"
                };

                Assert.Equal(expectedPatchKeys.OrderBy(x => x), result.PatchResult.PatchKeys.OrderBy(x => x));
                Assert.Equal(sourceHashBefore, SHA256.HashData(File.ReadAllBytes(sourceExe)));

                byte[] targetData = File.ReadAllBytes(result.ExecutablePath);
                foreach (string patchKey in expectedPatchKeys)
                {
                    BinaryPatchSpec spec = BinaryPatchEngine.PatchSpecs.Single(row => row.Key == patchKey);
                    Assert.Equal(spec.Patched, targetData.Skip(spec.FileOffset).Take(spec.Patched.Length).ToArray());
                }
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RecordsEnhancedPreviewPresetInManifest()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-enhanced-preview-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] sourceHashBefore = SHA256.HashData(File.ReadAllBytes(sourceExe));
            string[] enhancedVisibleKeys = BinaryPatchPlanBuilder
                .BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.EnhancedPreviewProfileId)
                .ToArray();

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "enhanced-preview",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true,
                        PatchKeys: enhancedVisibleKeys,
                        ProfilePresetId: BinaryPatchPlanBuilder.EnhancedPreviewProfileId));

                string[] expectedAppliedKeys = BinaryPatchPlanBuilder
                    .BuildSelectedSpecs(enhancedVisibleKeys)
                    .Select(spec => spec.Key)
                    .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                    .ToArray();

                Assert.Equal(expectedAppliedKeys, result.PatchResult.PatchKeys.OrderBy(key => key, StringComparer.OrdinalIgnoreCase));
                Assert.DoesNotContain("skip_auto_toggle", result.PatchResult.PatchKeys);
                Assert.DoesNotContain("free_camera_aurore_gate_bypass", result.PatchResult.PatchKeys);
                Assert.Equal(BinaryPatchPlanBuilder.EnhancedPreviewProfileId, result.ProfilePresetId);
                Assert.Equal("Enhanced Profile Preview", result.ProfilePresetDisplayName);
                Assert.Contains("Proof-bounded", result.ProfilePresetProofStatus);
                Assert.Equal(1, result.ProfileDefaultControllerConfiguration);
                Assert.True(result.ProfileDefaultPersistControllerConfigInOptions);
                Assert.True(result.ProfileDefaultSharpenMouseLook);
                Assert.Equal(
                    new[]
                    {
                        "windowed-compatibility",
                        "graphics-defaults",
                        "title-marker",
                        "frontend-red-margins",
                        "goodies-display-preview",
                        "copied-options-control-defaults",
                    },
                    result.ProfilePresetModules.Select(module => module.Id));
                Assert.Contains(result.ProfilePresetModules, module =>
                    module.Id == "copied-options-control-defaults" &&
                    module.PatchKeys.Count == 0 &&
                    module.CopiedOptionsEdits.Contains("controllerConfiguration=1") &&
                    module.CopiedOptionsEdits.Contains("mouseLookSensitivity=2.25") &&
                    module.ClaimBoundary.Contains("does not prove improved feel", StringComparison.OrdinalIgnoreCase) &&
                    module.RestoreStrategy.Contains("copied defaultoptions.bea backup", StringComparison.OrdinalIgnoreCase) &&
                    module.EvidenceRefs.Contains("release/readiness/winui_safe_copy_control_options_2026-06-17.md") &&
                    module.NonClaims.Contains("No improved control-feel proof."));
                Assert.All(result.ProfilePresetModules, module =>
                {
                    Assert.False(string.IsNullOrWhiteSpace(module.RestoreStrategy));
                    Assert.NotEmpty(module.EvidenceRefs);
                    Assert.NotEmpty(module.NonClaims);
                });
                Assert.Equal(sourceHashBefore, SHA256.HashData(File.ReadAllBytes(sourceExe)));

                byte[] targetData = File.ReadAllBytes(result.ExecutablePath);
                foreach (string patchKey in expectedAppliedKeys)
                {
                    BinaryPatchSpec spec = BinaryPatchEngine.PatchSpecs.Single(row => row.Key == patchKey);
                    Assert.Equal(spec.Patched, targetData.Skip(spec.FileOffset).Take(spec.Patched.Length).ToArray());
                }

                using JsonDocument manifest = JsonDocument.Parse(File.ReadAllText(result.ManifestPath));
                JsonElement profilePreset = manifest.RootElement.GetProperty("profilePreset");
                Assert.Equal(BinaryPatchPlanBuilder.EnhancedPreviewProfileId, profilePreset.GetProperty("id").GetString());
                Assert.Equal("Enhanced Profile Preview", profilePreset.GetProperty("displayName").GetString());
                Assert.Contains("not a full overhaul", profilePreset.GetProperty("proofStatus").GetString(), StringComparison.OrdinalIgnoreCase);
                Assert.Equal("safe-copy-profiles.v1", profilePreset.GetProperty("profileCatalogVersion").GetString());
                string profileCatalogSha256 = profilePreset.GetProperty("profileCatalogSha256").GetString()!;
                Assert.Equal(64, profileCatalogSha256.Length);
                Assert.True(profileCatalogSha256.All(Uri.IsHexDigit));
                Assert.Equal(1, profilePreset.GetProperty("defaultControllerConfiguration").GetInt32());
                Assert.True(profilePreset.GetProperty("defaultPersistControllerConfigInOptions").GetBoolean());
                Assert.True(profilePreset.GetProperty("defaultSharpenMouseLook").GetBoolean());
                JsonElement modules = profilePreset.GetProperty("modules");
                string[] moduleIds = modules
                    .EnumerateArray()
                    .Select(element => element.GetProperty("id").GetString()!)
                    .ToArray();
                Assert.Equal(
                    new[]
                    {
                        "windowed-compatibility",
                        "graphics-defaults",
                        "title-marker",
                        "frontend-red-margins",
                        "goodies-display-preview",
                        "copied-options-control-defaults",
                    },
                    moduleIds);

                JsonElement copiedControlModule = modules
                    .EnumerateArray()
                    .Single(element => element.GetProperty("id").GetString() == "copied-options-control-defaults");
                Assert.Empty(copiedControlModule.GetProperty("patchKeys").EnumerateArray());
                Assert.Contains("runtime control feel remains unproven", copiedControlModule.GetProperty("proofStatus").GetString(), StringComparison.OrdinalIgnoreCase);
                Assert.Contains("copied defaultoptions.bea backup", copiedControlModule.GetProperty("restoreStrategy").GetString(), StringComparison.OrdinalIgnoreCase);
                Assert.Equal(
                    new[] { "controllerConfiguration=1", "mouseLookSensitivity=2.25" },
                    copiedControlModule.GetProperty("copiedOptionsEdits").EnumerateArray().Select(element => element.GetString()!).ToArray());
                Assert.Contains(
                    "release/readiness/winui_safe_copy_control_options_2026-06-17.md",
                    copiedControlModule.GetProperty("evidenceRefs").EnumerateArray().Select(element => element.GetString()!).ToArray());
                Assert.Contains(
                    "No improved control-feel proof.",
                    copiedControlModule.GetProperty("nonClaims").EnumerateArray().Select(element => element.GetString()!).ToArray());

                foreach (JsonElement module in modules.EnumerateArray())
                {
                    Assert.False(string.IsNullOrWhiteSpace(module.GetProperty("restoreStrategy").GetString()));
                    Assert.NotEmpty(module.GetProperty("evidenceRefs").EnumerateArray());
                    Assert.NotEmpty(module.GetProperty("nonClaims").EnumerateArray());
                }

                string[] manifestPatchKeys = manifest.RootElement
                    .GetProperty("patchResult")
                    .GetProperty("patchKeys")
                    .EnumerateArray()
                    .Select(element => element.GetString()!)
                    .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                    .ToArray();
                Assert.Equal(expectedAppliedKeys, manifestPatchKeys);

                InvalidOperationException mismatch = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "enhanced-preview-mismatch",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true,
                            PatchKeys: BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.RecommendedProfileId),
                            ProfilePresetId: BinaryPatchPlanBuilder.EnhancedPreviewProfileId)));
                Assert.Contains("exact proof-bounded patch row set", mismatch.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RecordsDebugCameraPreviewPresetBoundary()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-debug-camera-preview-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] sourceHashBefore = SHA256.HashData(File.ReadAllBytes(sourceExe));
            string[] debugCameraVisibleKeys = BinaryPatchPlanBuilder
                .BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.DebugCameraPreviewProfileId)
                .ToArray();

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "debug-camera-preview",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true,
                        PatchKeys: debugCameraVisibleKeys,
                        ProfilePresetId: BinaryPatchPlanBuilder.DebugCameraPreviewProfileId));

                string[] expectedAppliedKeys = BinaryPatchPlanBuilder
                    .BuildSelectedSpecs(debugCameraVisibleKeys)
                    .Select(spec => spec.Key)
                    .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                    .ToArray();

                Assert.Equal(
                    new[]
                    {
                        "force_windowed",
                        "free_camera_aurore_gate_bypass",
                        "free_camera_keyboard_forward_q_cave",
                        "free_camera_keyboard_forward_q_hook",
                        "resolution_gate",
                    },
                    expectedAppliedKeys);
                Assert.Equal(expectedAppliedKeys, result.PatchResult.PatchKeys.OrderBy(key => key, StringComparer.OrdinalIgnoreCase));
                Assert.Equal(BinaryPatchPlanBuilder.DebugCameraPreviewProfileId, result.ProfilePresetId);
                Assert.Equal("Debug Camera Preview", result.ProfilePresetDisplayName);
                Assert.Contains("one Q-forward movement path", result.ProfilePresetProofStatus, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(new[] { "windowed-compatibility", "debug-camera-q-forward" }, result.ProfilePresetModules.Select(module => module.Id));

                SafeCopyProfileModule debugCameraModule = result.ProfilePresetModules.Single(module => module.Id == "debug-camera-q-forward");
                Assert.Equal(new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_forward_q_hook" }, debugCameraModule.PatchKeys);
                Assert.Contains("Q-forward", debugCameraModule.ClaimBoundary, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("release/readiness/winui_free_camera_q_forward_runtime_2026-06-18.md", debugCameraModule.EvidenceRefs);
                Assert.Contains("No full free-camera control scheme proof.", debugCameraModule.NonClaims);
                Assert.DoesNotContain("free_camera_keyboard_backward_q_hook", debugCameraVisibleKeys);
                Assert.DoesNotContain("pause_o_scan_initializer_experiment", debugCameraVisibleKeys);
                Assert.Equal(sourceHashBefore, SHA256.HashData(File.ReadAllBytes(sourceExe)));

                using JsonDocument manifest = JsonDocument.Parse(File.ReadAllText(result.ManifestPath));
                JsonElement profilePreset = manifest.RootElement.GetProperty("profilePreset");
                Assert.Equal(BinaryPatchPlanBuilder.DebugCameraPreviewProfileId, profilePreset.GetProperty("id").GetString());
                Assert.Equal("Debug Camera Preview", profilePreset.GetProperty("displayName").GetString());
                Assert.Contains("not a full free-camera mode", profilePreset.GetProperty("proofStatus").GetString(), StringComparison.OrdinalIgnoreCase);
                string[] manifestPatchKeys = manifest.RootElement
                    .GetProperty("patchResult")
                    .GetProperty("patchKeys")
                    .EnumerateArray()
                    .Select(element => element.GetString()!)
                    .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                    .ToArray();
                Assert.Equal(expectedAppliedKeys, manifestPatchKeys);

                JsonElement debugModule = profilePreset
                    .GetProperty("modules")
                    .EnumerateArray()
                    .Single(element => element.GetProperty("id").GetString() == "debug-camera-q-forward");
                Assert.Equal(
                    new[] { "free_camera_aurore_gate_bypass", "free_camera_keyboard_forward_q_hook" },
                    debugModule.GetProperty("patchKeys").EnumerateArray().Select(element => element.GetString()!).ToArray());
                Assert.Contains("Q-forward", debugModule.GetProperty("claimBoundary").GetString(), StringComparison.OrdinalIgnoreCase);
                Assert.Contains(
                    "No full free-camera control scheme proof.",
                    debugModule.GetProperty("nonClaims").EnumerateArray().Select(element => element.GetString()!).ToArray());

                GameProfilePrepareReceipt receipt = GameProfilePreflightService.BuildPrepareReceipt(
                    result,
                    copiedSavegames: false,
                    controlOptionsResult: null);
                string receiptText = string.Join("\n", receipt.IncludedChanges.Concat(receipt.StillNotIncluded));
                Assert.Contains("Debug camera Q-forward path", receiptText, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("No full free-camera control scheme proof", receiptText, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("No joystick or analog camera proof", receiptText, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("No gameplay safety or long-session proof", receiptText, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_CanStageMusicSwapPresetDuringProfileCreation()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-create-music-swap-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] firstTrackBytes = OggBytes(0x11);
            byte[] secondTrackBytes = OggBytes(0x22);
            Directory.CreateDirectory(Path.Combine(sourceRoot, "data", "Music"));
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), firstTrackBytes);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), secondTrackBytes);

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-create",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        MusicSwapPresetId: GameProfileMusicReplacementService.UseBea02ForBea01PresetId));

                Assert.NotNull(result.MusicSwapResult);
                Assert.Equal("BEA_01(Master).ogg", result.MusicSwapResult.TargetMusicFileName);
                Assert.True(File.Exists(result.MusicSwapResult.ManifestPath));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(Path.Combine(result.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg")));
                Assert.Equal(firstTrackBytes, File.ReadAllBytes(result.MusicSwapResult.BackupPath));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(Path.Combine(result.TargetGameRoot, "data", "Music", "BEA_02(Master).ogg")));
                Assert.Equal(firstTrackBytes, File.ReadAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg")));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg")));

                using JsonDocument manifest = JsonDocument.Parse(File.ReadAllText(result.ManifestPath));
                JsonElement musicSwap = manifest.RootElement.GetProperty("musicSwap");
                Assert.Equal(GameProfileMusicReplacementService.SchemaVersion, musicSwap.GetProperty("schemaVersion").GetString());
                Assert.Equal(GameProfileMusicReplacementService.ManifestFileName, musicSwap.GetProperty("manifestPath").GetString());
                Assert.Equal("BEA_01(Master).ogg", musicSwap.GetProperty("targetMusicFileName").GetString());
                Assert.Contains("runtime playback is not proven", musicSwap.GetProperty("proofStatus").GetString(), StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(tempRoot, File.ReadAllText(result.ManifestPath), StringComparison.OrdinalIgnoreCase);

                GameProfileLaunchPlan launchPlan = GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot);
                Assert.Equal(result.TargetGameRoot, launchPlan.WorkingDirectory);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void BuildLaunchPlan_RejectsTamperedMusicReplacementManifestTarget()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-music-manifest-drift-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            Directory.CreateDirectory(Path.Combine(sourceRoot, "data", "Music"));
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), OggBytes(0x22));

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-drift",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        MusicSwapPresetId: GameProfileMusicReplacementService.UseBea02ForBea01PresetId));

                File.WriteAllBytes(Path.Combine(result.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x77));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot));
                Assert.Contains("music replacement manifest hash", ex.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsExperimentalFullscreenFallbackWithoutWindowedPair()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-skip-auto-guard-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);

            try
            {
                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "skip-auto-guard",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: false,
                            AllowByteLayoutOnlyTarget: true,
                            PatchKeys: new[]
                            {
                                "skip_auto_toggle",
                                "version_overlay_use_patched_format_pointer"
                            })));

                Assert.Contains("windowed compatibility patch set", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(outputRoot, "skip-auto-guard")));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_AllowsCleanBackupExecutableOverrideInsideSourceRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-clean-backup-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string installedExe = PrepareSourceGameRoot(sourceRoot);
            string cleanBackup = Path.Combine(sourceRoot, "BEA.exe.original.backup");
            SeedExe(cleanBackup);
            byte[] backupBytes = File.ReadAllBytes(cleanBackup);
            byte[] installedHashBefore = SHA256.HashData(File.ReadAllBytes(installedExe));

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "clean-backup-source",
                        ExecutableOverridePath: cleanBackup,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true));

                Assert.Equal("BEA.exe", Path.GetFileName(result.ExecutablePath));
                Assert.Equal(installedHashBefore, SHA256.HashData(File.ReadAllBytes(installedExe)));

                byte[] copiedBytes = File.ReadAllBytes(result.ExecutablePath);
                foreach (string patchKey in result.PatchResult.PatchKeys)
                {
                    BinaryPatchSpec spec = BinaryPatchEngine.PatchSpecs.Single(row => row.Key == patchKey);
                    spec.Patched.CopyTo(backupBytes, spec.FileOffset);
                }

                Assert.Equal(backupBytes, copiedBytes);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void ValidateExecutableSourceForWorkspaceCopy_AllowsCleanBackupSourceName()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-workspace-source-clean-backup-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            PrepareSourceGameRoot(sourceRoot);
            string cleanBackup = Path.Combine(sourceRoot, "BEA.exe.original.backup");
            SeedExe(cleanBackup);

            try
            {
                string resolved = GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy(cleanBackup);

                Assert.Equal(Path.GetFullPath(cleanBackup), resolved);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void ValidateExecutableSourceForWorkspaceCopy_RejectsUnsupportedFileName()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-workspace-source-name-{Guid.NewGuid():N}");
            Directory.CreateDirectory(tempRoot);
            string wrongName = Path.Combine(tempRoot, "not-bea.exe");
            SeedExe(wrongName);

            try
            {
                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy(wrongName));

                Assert.Contains("BEA.exe", ex.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void ValidateExecutableSourceForWorkspaceCopy_RejectsHardlinkedSourceWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
            {
                return;
            }

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-workspace-source-hardlink-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source");
            string outsideRoot = Path.Combine(tempRoot, "outside");
            Directory.CreateDirectory(sourceRoot);
            Directory.CreateDirectory(outsideRoot);
            string outsideExe = Path.Combine(outsideRoot, "outside.exe");
            string linkedExe = Path.Combine(sourceRoot, "BEA.exe");
            SeedExe(outsideExe);

            try
            {
                if (!CreateHardLink(linkedExe, outsideExe, IntPtr.Zero))
                {
                    return;
                }

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy(linkedExe));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void ValidateAppOwnedWorkspaceFileDestination_AllowsNewFileUnderWorkspaceRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-workspace-destination-{Guid.NewGuid():N}");
            string workspaceRoot = Path.Combine(tempRoot, "PatchBench");
            string destination = Path.Combine(workspaceRoot, "copy", "BEA.exe");

            try
            {
                string resolved = GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination(
                    destination,
                    workspaceRoot,
                    "BEA.exe");

                Assert.Equal(Path.GetFullPath(destination), resolved);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void ValidateAppOwnedWorkspaceFileDestination_RejectsReparseWorkspaceRootWhenSupported()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-workspace-destination-reparse-{Guid.NewGuid():N}");
            string realRoot = Path.Combine(tempRoot, "real");
            string linkedRoot = Path.Combine(tempRoot, "PatchBench");
            string destination = Path.Combine(linkedRoot, "copy", "BEA.exe");

            try
            {
                Directory.CreateDirectory(realRoot);
                try
                {
                    Directory.CreateSymbolicLink(linkedRoot, realRoot);
                }
                catch (Exception createEx) when (createEx is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
                {
                    return;
                }

                InvalidOperationException thrown = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination(
                        destination,
                        linkedRoot,
                        "BEA.exe"));

                Assert.Contains("reparse", thrown.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsOutputInsideSourceRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-reject-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            string outputRoot = Path.Combine(sourceRoot, "profiles");

            try
            {
                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "bad-profile",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("app-owned output root", ex.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void BuildLaunchPlan_AllowsOnlyBoundedArguments()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-launch-plan-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "launch-plan",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileLaunchPlan plan = GameProfilePreflightService.BuildLaunchPlan(
                    result.TargetGameRoot,
                    new[]
                    {
                        "-skipfmv",
                        "-nomusic",
                        "-nosound",
                        "-hidetail",
                        "-nostaticshadows",
                        "-norumble",
                        "-showdebugtrace",
                        "-level",
                        "3",
                        "-configuration",
                        "2",
                        "-textureramlimit",
                        "33554432",
                    });

                Assert.Equal(
                    new[]
                    {
                        "-skipfmv",
                        "-nomusic",
                        "-nosound",
                        "-hidetail",
                        "-nostaticshadows",
                        "-norumble",
                        "-showdebugtrace",
                        "-level",
                        "3",
                        "-configuration",
                        "2",
                        "-textureramlimit",
                        "33554432",
                    },
                    plan.Arguments);
                Assert.Contains("-skipfmv -nomusic -nosound -hidetail -nostaticshadows -norumble -showdebugtrace -level 3 -configuration 2 -textureramlimit 33554432", plan.CommandPreview);

                for (int configuration = 1; configuration <= 4; configuration++)
                {
                    GameProfileLaunchPlan configurationPlan = GameProfilePreflightService.BuildLaunchPlan(
                        result.TargetGameRoot,
                        new[] { "-configuration", configuration.ToString() });
                    Assert.Equal(new[] { "-configuration", configuration.ToString() }, configurationPlan.Arguments);
                }

                InvalidOperationException resourceBuildEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot, new[] { "-buildresources" }));
                Assert.Contains("Unsupported launch argument", resourceBuildEx.Message);

                InvalidOperationException demoRecordEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot, new[] { "-record", "demo.dem" }));
                Assert.Contains("Unsupported launch argument", demoRecordEx.Message);

                foreach (string sourceOnlyFlag in new[] { "-devmode", "-killhud", "-modelviewer", "-cutsceneeditor", "-artists", "-stresstest", "-mem", "-largeram" })
                {
                    InvalidOperationException blockedEx = Assert.Throws<InvalidOperationException>(() =>
                        GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot, new[] { sourceOnlyFlag }));
                    Assert.Contains("Unsupported launch argument", blockedEx.Message);
                }

                InvalidOperationException zeroConfigurationEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot, new[] { "-configuration", "0" }));
                Assert.Contains("configuration", zeroConfigurationEx.Message, StringComparison.OrdinalIgnoreCase);

                InvalidOperationException configurationEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot, new[] { "-configuration", "5" }));
                Assert.Contains("configuration", configurationEx.Message, StringComparison.OrdinalIgnoreCase);

                InvalidOperationException textureRamEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot, new[] { "-textureramlimit", "1024" }));
                Assert.Contains("textureramlimit", textureRamEx.Message, StringComparison.OrdinalIgnoreCase);

                InvalidOperationException manifestEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(sourceRoot, Array.Empty<string>()));
        Assert.Contains("generated playable copied game folder manifest", manifestEx.Message);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void BuildLaunchPlan_RevalidatesManifestAndCurrentPatchBytes()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-launch-revalidate-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult result = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "launch-revalidate",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true));

                BinaryPatchSpec spec = BinaryPatchEngine.PatchSpecs.Single(row => row.Key == "force_windowed");
                byte[] data = File.ReadAllBytes(result.ExecutablePath);
                spec.Original.CopyTo(data, spec.FileOffset);
                File.WriteAllBytes(result.ExecutablePath, data);

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(result.TargetGameRoot, Array.Empty<string>()));
                Assert.Contains("current copied executable no longer matches", ex.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsAlreadyPatchedSourceWithoutCleanBackupSnapshot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-already-patched-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);

            try
            {
                byte[] data = File.ReadAllBytes(sourceExe);
                Array.Resize(ref data, 2_506_752);
                foreach (BinaryPatchSpec spec in BinaryPatchPlanBuilder.BuildSelectedSpecs(new[] { "resolution_gate", "force_windowed" }))
                {
                    spec.Patched.CopyTo(data, spec.FileOffset);
                }

                File.WriteAllBytes(sourceExe, data);

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "already-patched",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true)));

                Assert.Contains("known clean Steam retail BEA.exe", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(outputRoot, "already-patched")));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_DefaultIdentityPolicyRejectsSyntheticSpecimen()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-identity-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);

            try
            {
                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "identity-reject",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true)));

                Assert.Contains("known clean Steam retail BEA.exe", ex.Message);
                Assert.False(Directory.Exists(Path.Combine(outputRoot, "identity-reject")));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsRequiredEntryTypeMismatch()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-entry-type-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);

            try
            {
                Directory.Delete(Path.Combine(sourceRoot, "data"), recursive: true);
                File.WriteAllText(Path.Combine(sourceRoot, "data"), "not a directory");

                DirectoryNotFoundException ex = Assert.Throws<DirectoryNotFoundException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "entry-type",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("Required game directory", ex.Message);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsExecutableOverrideOutsideSourceRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-exe-escape-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            PrepareSourceGameRoot(sourceRoot);
            string outsideRoot = Path.Combine(tempRoot, "outside");
            Directory.CreateDirectory(outsideRoot);
            string outsideExe = Path.Combine(outsideRoot, "BEA.exe");
            SeedExe(outsideExe);

            try
            {
                InvalidOperationException escapeEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "exe-escape",
                            ExecutableOverridePath: outsideExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("source game root", escapeEx.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsReparsePointEntriesWhenSupported()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-reparse-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            string privateRoot = Path.Combine(tempRoot, "private");
            Directory.CreateDirectory(privateRoot);
            File.WriteAllText(Path.Combine(privateRoot, "private.txt"), "private");
            string linkPath = Path.Combine(sourceRoot, "data", "linked-private");

            try
            {
                try
                {
                    Directory.CreateSymbolicLink(linkPath, privateRoot);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
                {
                    return;
                }

                InvalidOperationException reparseEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "reparse",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("reparse", reparseEx.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsHardlinkedExecutableSourceWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
            {
                return;
            }

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-exe-hardlink-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            string outsideRoot = Path.Combine(tempRoot, "outside");
            Directory.CreateDirectory(outsideRoot);
            string outsideExe = Path.Combine(outsideRoot, "outside.exe");
            SeedExe(outsideExe);

            try
            {
                File.Delete(sourceExe);
                if (!CreateHardLink(sourceExe, outsideExe, IntPtr.Zero))
                {
                    return;
                }

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "exe-hardlink",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(outputRoot, "exe-hardlink")));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsHardlinkedRecursiveDataFileWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
            {
                return;
            }

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-data-hardlink-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            string outsideRoot = Path.Combine(tempRoot, "outside");
            Directory.CreateDirectory(outsideRoot);
            string outsideFile = Path.Combine(outsideRoot, "private.bin");
            File.WriteAllText(outsideFile, "private");
            string linkedFile = Path.Combine(sourceRoot, "data", "Resources", "base_res_PC.aya");

            try
            {
                File.Delete(linkedFile);
                if (!CreateHardLink(linkedFile, outsideFile, IntPtr.Zero))
                {
                    return;
                }

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "data-hardlink",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(outputRoot, "data-hardlink")));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void PrepareWindowedCompatibilityProfile_RejectsReparsePointOutputAncestorsWhenSupported()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-output-reparse-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string realOutputRoot = Path.Combine(tempRoot, "real-output");
            string linkedOutputParent = Path.Combine(tempRoot, "linked-output");
            string outputRoot = Path.Combine(linkedOutputParent, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);

            try
            {
                Directory.CreateDirectory(realOutputRoot);
                try
                {
                    Directory.CreateSymbolicLink(linkedOutputParent, realOutputRoot);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
                {
                    return;
                }

                InvalidOperationException outputReparseEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                        new GameProfilePrepareOptions(
                            SourceGameRoot: sourceRoot,
                            OutputRoot: outputRoot,
                            ProfileName: "output-reparse",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: true,
                            AllowByteLayoutOnlyTarget: true)));

                Assert.Contains("reparse", outputReparseEx.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(realOutputRoot, "profiles", "output-reparse")));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        private static string PrepareSourceGameRoot(string sourceRoot)
        {
            Directory.CreateDirectory(sourceRoot);
            Directory.CreateDirectory(Path.Combine(sourceRoot, "data", "Resources"));
            Directory.CreateDirectory(Path.Combine(sourceRoot, "savegames"));

            string exePath = Path.Combine(sourceRoot, "BEA.exe");
            SeedExe(exePath);
            File.WriteAllBytes(Path.Combine(sourceRoot, "defaultoptions.bea"), new byte[10_004]);
            File.WriteAllText(Path.Combine(sourceRoot, "data", "Resources", "base_res_PC.aya"), "resource");
            File.WriteAllText(Path.Combine(sourceRoot, "savegames", "career01.bes"), "save");
            File.WriteAllBytes(Path.Combine(sourceRoot, "binkw32.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "ogg.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "vorbis.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "zlib.dll"), new byte[] { 1 });
            File.WriteAllText(Path.Combine(sourceRoot, "cardid.txt"), "card profile");
            File.WriteAllText(Path.Combine(sourceRoot, "steam_appid.txt"), "55100");
            return exePath;
        }

        private static void SeedExe(string exePath)
        {
            int maxEnd = BinaryPatchEngine.PatchSpecs
                .Select(spec => spec.FileOffset + spec.Original.Length)
                .Max();
            byte[] data = Enumerable.Repeat((byte)0x90, maxEnd + 0x100).ToArray();
            foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs)
            {
                spec.Original.CopyTo(data, spec.FileOffset);
            }

            File.WriteAllBytes(exePath, data);
        }

        private static byte[] OggBytes(byte marker)
        {
            byte[] bytes = Enumerable.Repeat(marker, 32).ToArray();
            bytes[0] = (byte)'O';
            bytes[1] = (byte)'g';
            bytes[2] = (byte)'g';
            bytes[3] = (byte)'S';
            return bytes;
        }

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        private static extern bool CreateHardLink(
            string lpFileName,
            string lpExistingFileName,
            IntPtr lpSecurityAttributes);
    }
}
