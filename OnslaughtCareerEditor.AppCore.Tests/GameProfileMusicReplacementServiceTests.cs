using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class GameProfileMusicReplacementServiceTests
    {
        [Fact]
        public void StageReplacement_CopiesOggIntoSafeCopyCreatesBackupManifestAndLeavesSourcesUnchanged()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-replace-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            string sourceTrack = Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg");
            byte[] originalTrackBytes = OggBytes(0x11);
            File.WriteAllBytes(sourceTrack, originalTrackBytes);
            string replacementPath = Path.Combine(tempRoot, "user-music", "red-menu-theme.ogg");
            Directory.CreateDirectory(Path.GetDirectoryName(replacementPath)!);
            byte[] replacementBytes = OggBytes(0x44);
            File.WriteAllBytes(replacementPath, replacementBytes);

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-safe-copy",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementResult result = GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));

                string targetTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg");
                Assert.Equal(replacementBytes, File.ReadAllBytes(targetTrack));
                Assert.Equal(originalTrackBytes, File.ReadAllBytes(result.BackupPath));
                Assert.Equal(originalTrackBytes, File.ReadAllBytes(sourceTrack));
                Assert.Equal(replacementBytes, File.ReadAllBytes(replacementPath));
                Assert.True(File.Exists(result.ManifestPath));
                Assert.True(result.Mutation);
                Assert.Equal("BEA_01(Master).ogg", result.TargetMusicFileName);
                Assert.Equal("data/Music/BEA_01(Master).ogg", result.TargetRelativePath);
                Assert.Equal("data/Music/BEA_01(Master).ogg.original.backup", result.BackupRelativePath);
                Assert.Equal(SHA256.HashData(replacementBytes).ToHexStringLower(), result.ReplacementSha256);

                string manifest = File.ReadAllText(result.ManifestPath);
                Assert.Contains("\"schemaVersion\": \"winui-safe-copy-music-replacement.v1\"", manifest);
                Assert.Contains("\"targetMusicFileName\": \"BEA_01(Master).ogg\"", manifest);
                Assert.DoesNotContain(tempRoot, manifest, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(replacementPath, manifest, StringComparison.OrdinalIgnoreCase);
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
        public void ListSafeCopyMusicTracks_ReturnsGeneratedSafeCopyOggTracksSortedWithoutBackups()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-list-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), OggBytes(0x22));
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            File.WriteAllText(Path.Combine(sourceRoot, "data", "Music", "notes.txt"), "not music");

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-list",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                File.WriteAllBytes(Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg.original.backup"), OggBytes(0x33));

                IReadOnlyList<GameProfileMusicTrack> tracks = GameProfileMusicReplacementService.ListSafeCopyMusicTracks(
                    profile.TargetGameRoot,
                    outputRoot);

                Assert.Collection(
                    tracks,
                    first =>
                    {
                        Assert.Equal("BEA_01(Master).ogg", first.FileName);
                        Assert.Equal("data/Music/BEA_01(Master).ogg", first.RelativePath);
                        Assert.True(first.Size > 0);
                    },
                    second =>
                    {
                        Assert.Equal("BEA_02(Master).ogg", second.FileName);
                        Assert.Equal("data/Music/BEA_02(Master).ogg", second.RelativePath);
                        Assert.True(second.Size > 0);
                    });
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
        public void StageReplacement_CanUseAnotherSafeCopyTrackAsReplacement()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-swap-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] firstTrackBytes = OggBytes(0x11);
            byte[] secondTrackBytes = OggBytes(0x22);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), firstTrackBytes);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), secondTrackBytes);

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-swap",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                string copiedSecondTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_02(Master).ogg");
                GameProfileMusicReplacementResult result = GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: copiedSecondTrack));

                string copiedFirstTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg");
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(copiedFirstTrack));
                Assert.Equal(firstTrackBytes, File.ReadAllBytes(result.BackupPath));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(copiedSecondTrack));
                Assert.Equal(firstTrackBytes, File.ReadAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg")));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg")));
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
        public void StageReplacement_CanUseNamedSafeCopyMusicSwapPreset()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-preset-swap-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] firstTrackBytes = OggBytes(0x11);
            byte[] secondTrackBytes = OggBytes(0x22);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), firstTrackBytes);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), secondTrackBytes);

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-preset-swap",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicSwapPreset preset = GameProfileMusicReplacementService.GetSafeCopyMusicSwapPreset(
                    GameProfileMusicReplacementService.UseBea02ForBea01PresetId);
                Assert.Equal("BEA_01(Master).ogg", preset.TargetMusicFileName);
                Assert.Equal("BEA_02(Master).ogg", preset.ReplacementMusicFileName);
                Assert.Contains("runtime playback is not proven", preset.ProofStatus, StringComparison.OrdinalIgnoreCase);

                GameProfileMusicReplacementOptions options =
                    GameProfileMusicReplacementService.BuildSafeCopyMusicSwapPresetOptions(
                        profile.TargetGameRoot,
                        outputRoot,
                        GameProfileMusicReplacementService.UseBea02ForBea01PresetId);
                GameProfileMusicReplacementResult result = GameProfileMusicReplacementService.StageReplacement(options);

                string copiedFirstTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg");
                string copiedSecondTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_02(Master).ogg");
                Assert.Equal("BEA_01(Master).ogg", result.TargetMusicFileName);
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(copiedFirstTrack));
                Assert.Equal(firstTrackBytes, File.ReadAllBytes(result.BackupPath));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(copiedSecondTrack));
                Assert.Equal(firstTrackBytes, File.ReadAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg")));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg")));
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
        public void StageReplacement_CanUseLevel100DecodeBackedMusicSwapPreset()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-preset-decode-swap-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] secondTrackBytes = OggBytes(0x22);
            byte[] fourthTrackBytes = OggBytes(0x44);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), secondTrackBytes);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_04(Master).ogg"), fourthTrackBytes);

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-preset-decode-swap",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicSwapPreset preset = GameProfileMusicReplacementService.GetSafeCopyMusicSwapPreset(
                    GameProfileMusicReplacementService.UseBea02ForBea04PresetId);
                Assert.Equal("BEA_04(Master).ogg", preset.TargetMusicFileName);
                Assert.Equal("BEA_02(Master).ogg", preset.ReplacementMusicFileName);
                Assert.Contains("selection/decode", preset.ProofStatus, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("audible output", preset.ClaimBoundary, StringComparison.OrdinalIgnoreCase);

                GameProfileMusicReplacementOptions options =
                    GameProfileMusicReplacementService.BuildSafeCopyMusicSwapPresetOptions(
                        profile.TargetGameRoot,
                        outputRoot,
                        GameProfileMusicReplacementService.UseBea02ForBea04PresetId);
                GameProfileMusicReplacementResult result = GameProfileMusicReplacementService.StageReplacement(options);

                string copiedSecondTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_02(Master).ogg");
                string copiedFourthTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_04(Master).ogg");
                Assert.Equal("BEA_04(Master).ogg", result.TargetMusicFileName);
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(copiedFourthTrack));
                Assert.Equal(fourthTrackBytes, File.ReadAllBytes(result.BackupPath));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(copiedSecondTrack));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg")));
                Assert.Equal(fourthTrackBytes, File.ReadAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_04(Master).ogg")));
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
        public void BuildSafeCopyMusicSwapPresetOptions_RejectsMissingPresetTrack()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-preset-missing-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-preset-missing",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                string missingTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_02(Master).ogg");
                if (File.Exists(missingTrack))
                {
                    File.Delete(missingTrack);
                }

                FileNotFoundException ex = Assert.Throws<FileNotFoundException>(() =>
                    GameProfileMusicReplacementService.BuildSafeCopyMusicSwapPresetOptions(
                        profile.TargetGameRoot,
                        outputRoot,
                        GameProfileMusicReplacementService.UseBea02ForBea01PresetId));

                Assert.Contains("Preset replacement music file", ex.Message, StringComparison.OrdinalIgnoreCase);
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
        public void BuildSafeCopyMusicSwapPresetOptions_RejectsPresetTargetWithoutOggHeader()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-preset-bad-target-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), OggBytes(0x22));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-preset-bad-target",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                File.WriteAllBytes(
                    Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg"),
                    new byte[] { 0x4E, 0x4F, 0x50, 0x45 });

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.BuildSafeCopyMusicSwapPresetOptions(
                        profile.TargetGameRoot,
                        outputRoot,
                        GameProfileMusicReplacementService.UseBea02ForBea01PresetId));

                Assert.Contains("Preset target music file", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("OggS", ex.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Theory]
        [InlineData("..\\BEA.exe")]
        [InlineData("subdir\\track.ogg")]
        [InlineData("track.mp3")]
        public void StageReplacement_RejectsUnsafeTargetMusicNames(string targetName)
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-reject-name-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-reject-name",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            TargetMusicFileName: targetName,
                            ReplacementOggPath: replacementPath)));

                Assert.Contains("music file name", ex.Message, StringComparison.OrdinalIgnoreCase);
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
        public void StageReplacement_RejectsNonGeneratedGameRoots()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-nongenerated-{Guid.NewGuid():N}");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            Directory.CreateDirectory(outputRoot);
            string sourceRoot = Path.Combine(outputRoot, "raw-game-without-manifest");
            PrepareSourceGameRoot(sourceRoot);
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: sourceRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            TargetMusicFileName: "BEA_01(Master).ogg",
                            ReplacementOggPath: replacementPath)));

        Assert.Contains("generated playable copied game folder manifest", ex.Message, StringComparison.OrdinalIgnoreCase);
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
        public void StageReplacement_RejectsProfilesRootAsSafeGameRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-root-equality-{Guid.NewGuid():N}");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            Directory.CreateDirectory(outputRoot);
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: outputRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            TargetMusicFileName: "BEA_01(Master).ogg",
                            ReplacementOggPath: replacementPath)));

                Assert.Contains("app-owned profiles root", ex.Message, StringComparison.OrdinalIgnoreCase);
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
        public void StageReplacement_RejectsReplacementWithoutOggHeader()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-bad-header-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, new byte[] { 0x4E, 0x4F, 0x50, 0x45, 0x44 });

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-bad-header",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            TargetMusicFileName: "BEA_01(Master).ogg",
                            ReplacementOggPath: replacementPath)));

                Assert.Contains("OggS", ex.Message, StringComparison.OrdinalIgnoreCase);
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
        public void RestoreReplacement_RestoresCopiedTrackFromBackup()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-restore-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] originalTrackBytes = OggBytes(0x11);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), originalTrackBytes);
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-restore",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));

                GameProfileMusicReplacementRestoreResult restore = GameProfileMusicReplacementService.RestoreReplacement(
                    new GameProfileMusicReplacementRestoreOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot));

                string targetTrack = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg");
                Assert.True(restore.Success);
                Assert.Equal(originalTrackBytes, File.ReadAllBytes(targetTrack));
                Assert.False(File.Exists(Path.Combine(profile.TargetGameRoot, GameProfileMusicReplacementService.ManifestFileName)));
                Assert.Contains("restored", restore.Message, StringComparison.OrdinalIgnoreCase);
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
        public void StageReplacement_RejectsSequentialDifferentTargetWhileManifestIsActive()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-active-manifest-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] firstTrackBytes = OggBytes(0x11);
            byte[] secondTrackBytes = OggBytes(0x22);
            byte[] replacementBytes = OggBytes(0x44);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), firstTrackBytes);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), secondTrackBytes);
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, replacementBytes);

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-active-manifest",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            TargetMusicFileName: "BEA_02(Master).ogg",
                            ReplacementOggPath: replacementPath)));

                Assert.Contains("active", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("restore", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(replacementBytes, File.ReadAllBytes(Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg")));
                Assert.Equal(secondTrackBytes, File.ReadAllBytes(Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_02(Master).ogg")));
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
        public void StageReplacement_RejectsHardlinkedExistingManifestBeforeChangingTargetWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-manifest-hardlink-stage-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsideManifestPath = Path.Combine(tempRoot, "outside-manifest-link.json");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            byte[] originalTrackBytes = OggBytes(0x11);
            byte[] replacementBytes = OggBytes(0x44);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), originalTrackBytes);
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, replacementBytes);

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-hardlinked-manifest-stage",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                File.WriteAllText(outsideManifestPath, "{}");
                string manifestPath = Path.Combine(profile.TargetGameRoot, GameProfileMusicReplacementService.ManifestFileName);
                if (!CreateHardLink(manifestPath, outsideManifestPath, IntPtr.Zero))
                    return;

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            TargetMusicFileName: "BEA_01(Master).ogg",
                            ReplacementOggPath: replacementPath)));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(originalTrackBytes, File.ReadAllBytes(Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg")));
                Assert.Equal("{}", File.ReadAllText(outsideManifestPath));
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
        public void RestoreReplacement_RejectsHardlinkedManifestBeforeDeletingOrChangingTargetWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-manifest-hardlink-restore-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsideManifestPath = Path.Combine(tempRoot, "outside-manifest-link.json");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            byte[] replacementBytes = OggBytes(0x44);
            File.WriteAllBytes(replacementPath, replacementBytes);

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-hardlinked-manifest-restore",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementResult stage = GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));

                File.Copy(stage.ManifestPath, outsideManifestPath);
                File.Delete(stage.ManifestPath);
                if (!CreateHardLink(stage.ManifestPath, outsideManifestPath, IntPtr.Zero))
                    return;

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.RestoreReplacement(
                        new GameProfileMusicReplacementRestoreOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot)));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.True(File.Exists(stage.ManifestPath));
                Assert.Equal(replacementBytes, File.ReadAllBytes(stage.TargetPath));
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
        public void StageReplacement_RejectsExistingBackupWhenCurrentTargetDrifted()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-drift-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));
            string secondReplacementPath = Path.Combine(tempRoot, "second.ogg");
            File.WriteAllBytes(secondReplacementPath, OggBytes(0x55));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-drift",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));
                File.Delete(Path.Combine(profile.TargetGameRoot, GameProfileMusicReplacementService.ManifestFileName));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            TargetMusicFileName: "BEA_01(Master).ogg",
                            ReplacementOggPath: secondReplacementPath)));

                Assert.Contains("no longer matches", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(OggBytes(0x44), File.ReadAllBytes(Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg")));
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
        public void RestoreReplacement_RejectsCorruptBackup()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-corrupt-backup-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-corrupt-backup",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementResult stage = GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));

                File.WriteAllBytes(stage.BackupPath, OggBytes(0x66));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.RestoreReplacement(
                        new GameProfileMusicReplacementRestoreOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot)));

                Assert.Contains("backup", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(OggBytes(0x44), File.ReadAllBytes(Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg")));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        [Theory]
        [InlineData("\"targetRelativePath\": \"data/Music/BEA_01(Master).ogg\"", "\"targetRelativePath\": \"BEA.exe\"")]
        [InlineData("\"targetRelativePath\": \"data/Music/BEA_01(Master).ogg\"", "\"targetRelativePath\": \"../outside.ogg\"")]
        [InlineData("\"targetRelativePath\": \"data/Music/BEA_01(Master).ogg\"", "\"targetRelativePath\": \"C:/outside.ogg\"")]
        [InlineData("\"backupRelativePath\": \"data/Music/BEA_01(Master).ogg.original.backup\"", "\"backupRelativePath\": \"defaultoptions.bea\"")]
        [InlineData("\"targetMusicFileName\": \"BEA_01(Master).ogg\"", "\"targetMusicFileName\": \"Other.ogg\"")]
        public void RestoreReplacement_RejectsTamperedManifestPaths(string oldText, string newText)
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-tampered-manifest-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-tampered-manifest",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementResult stage = GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));

                string manifest = File.ReadAllText(stage.ManifestPath).Replace(oldText, newText, StringComparison.Ordinal);
                File.WriteAllText(stage.ManifestPath, manifest);

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.RestoreReplacement(
                        new GameProfileMusicReplacementRestoreOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot)));

                Assert.Contains("manifest", ex.Message, StringComparison.OrdinalIgnoreCase);
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
        public void RestoreReplacement_RejectsPostStageReparseMusicDirectoryWhenSupported()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-restore-reparse-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsideRoot = Path.Combine(tempRoot, "outside-music");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-restore-reparse",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementResult stage = GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));

                Directory.CreateDirectory(outsideRoot);
                File.Copy(stage.TargetPath, Path.Combine(outsideRoot, "BEA_01(Master).ogg"));
                File.Copy(stage.BackupPath, Path.Combine(outsideRoot, "BEA_01(Master).ogg.original.backup"));
                string musicDirectory = Path.Combine(profile.TargetGameRoot, "data", "Music");
                Directory.Delete(musicDirectory, recursive: true);

                try
                {
                    Directory.CreateSymbolicLink(musicDirectory, outsideRoot);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
                {
                    return;
                }

                InvalidOperationException reparseEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.RestoreReplacement(
                        new GameProfileMusicReplacementRestoreOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot)));

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
        public void StageReplacement_RejectsHardlinkedTargetWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-target-hardlink-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsidePath = Path.Combine(tempRoot, "outside-target-link.ogg");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-target-hardlink",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                string targetPath = Path.Combine(profile.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg");
                if (!CreateHardLink(outsidePath, targetPath, IntPtr.Zero))
                    return;

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            TargetMusicFileName: "BEA_01(Master).ogg",
                            ReplacementOggPath: replacementPath)));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(OggBytes(0x11), File.ReadAllBytes(outsidePath));
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
        public void RestoreReplacement_RejectsHardlinkedBackupWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-music-backup-hardlink-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsidePath = Path.Combine(tempRoot, "outside-backup-link.ogg");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            string replacementPath = Path.Combine(tempRoot, "replacement.ogg");
            File.WriteAllBytes(replacementPath, OggBytes(0x44));

            try
            {
                GameProfilePrepareResult profile = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "music-backup-hardlink",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileMusicReplacementResult stage = GameProfileMusicReplacementService.StageReplacement(
                    new GameProfileMusicReplacementOptions(
                        SafeGameRoot: profile.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        TargetMusicFileName: "BEA_01(Master).ogg",
                        ReplacementOggPath: replacementPath));

                if (!CreateHardLink(outsidePath, stage.BackupPath, IntPtr.Zero))
                    return;

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileMusicReplacementService.RestoreReplacement(
                        new GameProfileMusicReplacementRestoreOptions(
                            SafeGameRoot: profile.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot)));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(OggBytes(0x44), File.ReadAllBytes(stage.TargetPath));
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
            Directory.CreateDirectory(Path.Combine(sourceRoot, "data", "Music"));

            string exePath = Path.Combine(sourceRoot, "BEA.exe");
            File.WriteAllBytes(exePath, new byte[] { 0x4D, 0x5A, 0x90, 0x00 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "defaultoptions.bea"), new byte[10_004]);
            File.WriteAllText(Path.Combine(sourceRoot, "data", "Resources", "base_res_PC.aya"), "resource");
            File.WriteAllBytes(Path.Combine(sourceRoot, "binkw32.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "ogg.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "vorbis.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "zlib.dll"), new byte[] { 1 });
            return exePath;
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

    internal static class TestHashExtensions
    {
        public static string ToHexStringLower(this byte[] bytes)
        {
            return Convert.ToHexString(bytes).ToLowerInvariant();
        }
    }
}
