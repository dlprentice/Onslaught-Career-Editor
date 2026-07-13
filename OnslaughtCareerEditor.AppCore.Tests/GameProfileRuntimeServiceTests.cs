using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class GameProfileRuntimeServiceTests
    {
        [Fact]
        public void LaunchCopiedProfile_StartsOnlyGeneratedProfileUnderAppOwnedRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "runtime-launch",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true));

                GameProfileManagedProcess launched = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        LaunchArguments: new[] { "-skipfmv", "-showdebugtrace" }),
                    runner);

                Assert.Equal(1234, launched.ProcessId);
                Assert.Equal(prepared.ExecutablePath, launched.ExecutablePath);
                Assert.Equal(prepared.TargetGameRoot, launched.WorkingDirectory);
                Assert.Equal(new[] { "-skipfmv", "-showdebugtrace" }, launched.Arguments);
                Assert.Equal(prepared.ManifestPath, launched.ManifestPath);
                Assert.Single(runner.Starts);
                Assert.Equal(prepared.ExecutablePath, runner.Starts[0].FileName);
                Assert.Equal(prepared.TargetGameRoot, runner.Starts[0].WorkingDirectory);
                Assert.Equal("-skipfmv -showdebugtrace", runner.Starts[0].ArgumentString);
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
        public void LaunchCopiedProfile_RejectsProfilesOutsideAppOwnedRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-root-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string wrongRoot = Path.Combine(tempRoot, "other-profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "outside-root",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileRuntimeService.LaunchCopiedProfile(
                        new GameProfileLaunchOptions(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: wrongRoot,
                            LaunchArguments: Array.Empty<string>()),
                        runner));

        Assert.Contains("app-owned playable copied game folder root", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(runner.Starts);
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
        public void LaunchCopiedProfile_RevalidatesManifestAndPatchBytesBeforeStarting()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-patch-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "patch-recheck",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true));

                BinaryPatchSpec forceWindowed = BinaryPatchEngine.PatchSpecs.Single(row => row.Key == "force_windowed");
                byte[] data = File.ReadAllBytes(prepared.ExecutablePath);
                forceWindowed.Original.CopyTo(data, forceWindowed.FileOffset);
                File.WriteAllBytes(prepared.ExecutablePath, data);

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileRuntimeService.LaunchCopiedProfile(
                        new GameProfileLaunchOptions(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            LaunchArguments: Array.Empty<string>()),
                        runner));

                Assert.Contains("current copied executable no longer matches", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(runner.Starts);
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
        public void LaunchCopiedProfile_RevalidatesStagedMusicReplacementManifestBeforeStarting()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-music-drift-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            Directory.CreateDirectory(Path.Combine(sourceRoot, "data", "Music"));
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x11));
            File.WriteAllBytes(Path.Combine(sourceRoot, "data", "Music", "BEA_02(Master).ogg"), OggBytes(0x22));
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "runtime-music-drift",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true,
                        MusicSwapPresetId: GameProfileMusicReplacementService.UseBea02ForBea01PresetId));

                File.WriteAllBytes(Path.Combine(prepared.TargetGameRoot, "data", "Music", "BEA_01(Master).ogg"), OggBytes(0x77));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileRuntimeService.LaunchCopiedProfile(
                        new GameProfileLaunchOptions(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            LaunchArguments: Array.Empty<string>()),
                        runner));

                Assert.Contains("music replacement manifest hash", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(runner.Starts);
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
        public void PrepareWindowedCompatibilityProfile_RejectsVisiblePatchesWithoutWindowedCompatibilitySet()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-patch-selection-{Guid.NewGuid():N}");
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
                            ProfileName: "patch-without-windowed",
                            ExecutableOverridePath: sourceExe,
                            ApplyWindowedCompatibilityPatch: false,
                            AllowByteLayoutOnlyTarget: true,
                            PatchKeys: new[] { "extra_graphics_default_on" })));

                Assert.Contains("windowed compatibility patch set", ex.Message, StringComparison.OrdinalIgnoreCase);
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
        public void LaunchCopiedProfile_RevalidatesBackupDerivedExecutableHashBeforeStarting()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-hash-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "hash-recheck",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true));

                byte[] data = File.ReadAllBytes(prepared.ExecutablePath);
                data[0x10] = (byte)(data[0x10] ^ 0x7F);
                File.WriteAllBytes(prepared.ExecutablePath, data);

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileRuntimeService.LaunchCopiedProfile(
                        new GameProfileLaunchOptions(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            LaunchArguments: Array.Empty<string>()),
                        runner));

                Assert.Contains("trusted clean Steam retail specimen", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(runner.Starts);
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
        public void LaunchCopiedProfile_DoesNotTrustDriftedManifestExecutableHash()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-manifest-hash-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "manifest-hash-drift",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: true));

                byte[] data = File.ReadAllBytes(prepared.ExecutablePath);
                data[0x10] = (byte)(data[0x10] ^ 0x33);
                File.WriteAllBytes(prepared.ExecutablePath, data);

                string driftHash = Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();
                string manifest = File.ReadAllText(prepared.ManifestPath);
                string originalHash = manifest.Split("\"executableSha256\": \"", StringSplitOptions.None)[1].Split('"')[0];
                File.WriteAllText(prepared.ManifestPath, manifest.Replace(originalHash, driftHash, StringComparison.Ordinal));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileRuntimeService.LaunchCopiedProfile(
                        new GameProfileLaunchOptions(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            LaunchArguments: Array.Empty<string>()),
                        runner));

                Assert.Contains("trusted clean Steam retail specimen", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(runner.Starts);
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
        public void LaunchCopiedProfile_RejectsUnsupportedArgumentsBeforeStarting()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-args-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "bad-args",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileRuntimeService.LaunchCopiedProfile(
                        new GameProfileLaunchOptions(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            LaunchArguments: new[] { "-devmode" }),
                        runner));

                Assert.Contains("Unsupported launch argument", ex.Message);
                Assert.Empty(runner.Starts);
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
        public void StopCopiedProfile_RequiresManagedRecordUnderAppOwnedRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-stop-root-{Guid.NewGuid():N}");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            Directory.CreateDirectory(outputRoot);
            var runner = new FakeGameProfileProcessRunner();
            var outside = new GameProfileManagedProcess(
                ProcessId: 999,
                ExecutablePath: Path.Combine(tempRoot, "outside", "BEA.exe"),
                WorkingDirectory: Path.Combine(tempRoot, "outside"),
                Arguments: Array.Empty<string>(),
                StartedAt: DateTimeOffset.UtcNow,
                ManifestPath: Path.Combine(tempRoot, "outside", "onslaught-profile-manifest.json"));

            try
            {
                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileRuntimeService.StopCopiedProfile(outside, outputRoot, runner));

        Assert.Contains("managed playable copied game folder", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(runner.Stops);
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
        public void StopCopiedProfile_DelegatesOnlyForValidatedManagedRecord()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-stop-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "stop-good",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true));

                GameProfileManagedProcess launched = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        LaunchArguments: Array.Empty<string>()),
                    runner);

                GameProfileStopResult stopped = GameProfileRuntimeService.StopCopiedProfile(launched, outputRoot, runner);

                Assert.True(stopped.Success, stopped.Message);
                Assert.Equal(1234, stopped.ProcessId);
                Assert.Single(runner.Stops);
                Assert.Equal(launched, runner.Stops[0]);
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
        public void StopCopiedProfile_DoesNotRevalidateMutableManifestOrPatchBytesBeforeStopping()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-stop-drift-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "stop-drift",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true));

                GameProfileManagedProcess launched = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        LaunchArguments: Array.Empty<string>()),
                    runner);

                File.WriteAllText(prepared.ManifestPath, "{ drifted manifest");
                byte[] data = File.ReadAllBytes(prepared.ExecutablePath);
                data[0x20] = (byte)(data[0x20] ^ 0x22);
                File.WriteAllBytes(prepared.ExecutablePath, data);

                GameProfileStopResult stopped = GameProfileRuntimeService.StopCopiedProfile(launched, outputRoot, runner);

                Assert.True(stopped.Success, stopped.Message);
                Assert.Equal(1234, stopped.ProcessId);
                Assert.Single(runner.Stops);
                Assert.Equal(launched, runner.Stops[0]);
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
        public void ManagedProcessRegistry_StopsRegisteredSafeCopiesAndForgetsSuccessfulStops()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-registry-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();
            var registry = new GameProfileManagedProcessRegistry();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "registry-stop",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true));

                GameProfileManagedProcess launched = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        LaunchArguments: Array.Empty<string>()),
                    runner);

                registry.Register(launched, outputRoot);

                Assert.True(registry.TryGetLatest(out GameProfileRegisteredProcess registered));
                Assert.Equal(launched, registered.Process);
                Assert.Single(registry.Snapshot());

                IReadOnlyList<GameProfileStopResult> results = registry.StopAll(runner);

                Assert.Single(results);
                Assert.True(results[0].Success, results[0].Message);
                Assert.Equal(1234, results[0].ProcessId);
                Assert.Single(runner.Stops);
                Assert.Equal(launched, runner.Stops[0]);
                Assert.Empty(registry.Snapshot());
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
        public void ManagedProcessRegistry_PersistsAndRestoresAppOwnedLease()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-lease-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string leasePath = Path.Combine(outputRoot, GameProfileManagedProcessRegistry.LeaseFileName);
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "registry-lease",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true));

                GameProfileManagedProcess launched = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        LaunchArguments: new[] { "-skipfmv", "-hidetail" }),
                    runner);

                var registry = new GameProfileManagedProcessRegistry(leasePath);
                registry.Register(launched, outputRoot);

                Assert.True(File.Exists(leasePath));

                var restored = new GameProfileManagedProcessRegistry(leasePath);

                Assert.True(restored.TryGetLatest(out GameProfileRegisteredProcess registered));
                Assert.Equal(launched.ProcessId, registered.Process.ProcessId);
                Assert.Equal(Path.GetFullPath(prepared.ExecutablePath), registered.Process.ExecutablePath);
                Assert.Equal(Path.GetFullPath(prepared.TargetGameRoot).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar), registered.Process.WorkingDirectory);
                Assert.Equal(new[] { "-skipfmv", "-hidetail" }, registered.Process.Arguments);
                Assert.Equal(Path.GetFullPath(outputRoot).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar), registered.AppOwnedProfilesRoot);
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
        public void ManagedProcessRegistry_RemovesPersistedLeaseAfterSuccessfulStop()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-lease-stop-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string leasePath = Path.Combine(outputRoot, GameProfileManagedProcessRegistry.LeaseFileName);
            string sourceExe = PrepareSourceGameRoot(sourceRoot);
            var runner = new FakeGameProfileProcessRunner();

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "registry-lease-stop",
                        ExecutableOverridePath: sourceExe,
                        ApplyWindowedCompatibilityPatch: false,
                        AllowByteLayoutOnlyTarget: true));

                GameProfileManagedProcess launched = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        LaunchArguments: Array.Empty<string>()),
                    runner);

                var registry = new GameProfileManagedProcessRegistry(leasePath);
                registry.Register(launched, outputRoot);

                var restored = new GameProfileManagedProcessRegistry(leasePath);
                IReadOnlyList<GameProfileStopResult> results = restored.StopAll(runner);

                Assert.Single(results);
                Assert.True(results[0].Success, results[0].Message);
                Assert.Empty(restored.Snapshot());
                Assert.Empty(new GameProfileManagedProcessRegistry(leasePath).Snapshot());
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
        public void ManagedProcessRegistry_IgnoresPersistedLeaseOutsideAppOwnedRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-lease-outside-{Guid.NewGuid():N}");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsideRoot = Path.Combine(tempRoot, "outside-game");
            string leasePath = Path.Combine(outputRoot, GameProfileManagedProcessRegistry.LeaseFileName);

            try
            {
                Directory.CreateDirectory(outputRoot);
                Directory.CreateDirectory(outsideRoot);
                File.WriteAllBytes(Path.Combine(outsideRoot, "BEA.exe"), new byte[] { 1, 2, 3 });
                File.WriteAllText(Path.Combine(outsideRoot, "onslaught-profile-manifest.json"), "{}");

                var payload = new
                {
                    SchemaVersion = GameProfileManagedProcessRegistry.LeaseSchemaVersion,
                    WrittenAt = DateTimeOffset.UtcNow,
                    Processes = new[]
                    {
                        new
                        {
                            ProcessId = 4321,
                            ExecutablePath = Path.Combine(outsideRoot, "BEA.exe"),
                            WorkingDirectory = outsideRoot,
                            Arguments = Array.Empty<string>(),
                            StartedAt = DateTimeOffset.UtcNow,
                            ManifestPath = Path.Combine(outsideRoot, "onslaught-profile-manifest.json"),
                            AppOwnedProfilesRoot = outputRoot,
                        },
                    },
                };
                File.WriteAllText(
                    leasePath,
                    JsonSerializer.Serialize(
                        payload,
                        new JsonSerializerOptions
                        {
                            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                            WriteIndented = true,
                        }));

                var registry = new GameProfileManagedProcessRegistry(leasePath);

                Assert.Empty(registry.Snapshot());
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
        public void ManagedProcessRegistry_IgnoresPersistedLeaseWithDifferentAppOwnedRoot()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-lease-root-drift-{Guid.NewGuid():N}");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsideProfilesRoot = Path.Combine(tempRoot, "other-profiles");
            string outsideProfile = Path.Combine(outsideProfilesRoot, "safe-copy");
            string leasePath = Path.Combine(outputRoot, GameProfileManagedProcessRegistry.LeaseFileName);

            try
            {
                Directory.CreateDirectory(outputRoot);
                Directory.CreateDirectory(outsideProfile);
                File.WriteAllBytes(Path.Combine(outsideProfile, "BEA.exe"), new byte[] { 1, 2, 3 });
                File.WriteAllText(Path.Combine(outsideProfile, "onslaught-profile-manifest.json"), "{}");

                var payload = new
                {
                    SchemaVersion = GameProfileManagedProcessRegistry.LeaseSchemaVersion,
                    WrittenAt = DateTimeOffset.UtcNow,
                    Processes = new[]
                    {
                        new
                        {
                            ProcessId = 4321,
                            ExecutablePath = Path.Combine(outsideProfile, "BEA.exe"),
                            WorkingDirectory = outsideProfile,
                            Arguments = Array.Empty<string>(),
                            StartedAt = DateTimeOffset.UtcNow,
                            ManifestPath = Path.Combine(outsideProfile, "onslaught-profile-manifest.json"),
                            AppOwnedProfilesRoot = outsideProfilesRoot,
                        },
                    },
                };
                File.WriteAllText(
                    leasePath,
                    JsonSerializer.Serialize(
                        payload,
                        new JsonSerializerOptions
                        {
                            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                            WriteIndented = true,
                        }));

                var registry = new GameProfileManagedProcessRegistry(leasePath);

                Assert.Empty(registry.Snapshot());
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
        public void ManagedProcessRegistry_RegisterRequiresLeaseRootWhenPersisted()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-profile-runtime-register-root-drift-{Guid.NewGuid():N}");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsideProfilesRoot = Path.Combine(tempRoot, "other-profiles");
            string outsideProfile = Path.Combine(outsideProfilesRoot, "safe-copy");
            string leasePath = Path.Combine(outputRoot, GameProfileManagedProcessRegistry.LeaseFileName);

            try
            {
                Directory.CreateDirectory(outputRoot);
                Directory.CreateDirectory(outsideProfile);
                File.WriteAllBytes(Path.Combine(outsideProfile, "BEA.exe"), new byte[] { 1, 2, 3 });
                File.WriteAllText(Path.Combine(outsideProfile, "onslaught-profile-manifest.json"), "{}");

                var process = new GameProfileManagedProcess(
                    ProcessId: 4321,
                    ExecutablePath: Path.Combine(outsideProfile, "BEA.exe"),
                    WorkingDirectory: outsideProfile,
                    Arguments: Array.Empty<string>(),
                    StartedAt: DateTimeOffset.UtcNow,
                    ManifestPath: Path.Combine(outsideProfile, "onslaught-profile-manifest.json"));

                var registry = new GameProfileManagedProcessRegistry(leasePath);

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    registry.Register(process, outsideProfilesRoot));

                Assert.Contains("lease root", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(registry.Snapshot());
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
        public void ManagedProcessRegistry_StopRejectsUnregisteredProcess()
        {
            var registry = new GameProfileManagedProcessRegistry();
            var process = new GameProfileManagedProcess(
                ProcessId: 1234,
                ExecutablePath: Path.Combine(Path.GetTempPath(), "safe-copy", "BEA.exe"),
                WorkingDirectory: Path.Combine(Path.GetTempPath(), "safe-copy"),
                Arguments: Array.Empty<string>(),
                StartedAt: DateTimeOffset.UtcNow,
                ManifestPath: Path.Combine(Path.GetTempPath(), "safe-copy", "onslaught-profile-manifest.json"));

            GameProfileStopResult result = registry.Stop(process, new FakeGameProfileProcessRunner());

            Assert.False(result.Success);
            Assert.Contains("not registered", result.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void DefaultRunnerIdentityRequiresExactStartTimeForPidReuseSafety()
        {
            DateTimeOffset startedAt = DateTimeOffset.UtcNow;
            string exePath = Path.Combine(Path.GetTempPath(), "safe-copy", "BEA.exe");
            var expected = new GameProfileManagedProcess(
                ProcessId: 1234,
                ExecutablePath: exePath,
                WorkingDirectory: Path.GetDirectoryName(exePath)!,
                Arguments: Array.Empty<string>(),
                StartedAt: startedAt,
                ManifestPath: Path.Combine(Path.GetDirectoryName(exePath)!, "onslaught-profile-manifest.json"));

            Assert.True(InvokeDefaultRunnerIdentityMatch(startedAt, exePath, expected));
            Assert.False(InvokeDefaultRunnerIdentityMatch(startedAt.AddTicks(1), exePath, expected));
            Assert.False(InvokeDefaultRunnerIdentityMatch(startedAt.AddSeconds(1), exePath, expected));
            Assert.False(InvokeDefaultRunnerIdentityMatch(startedAt.AddSeconds(5), exePath, expected));
            Assert.False(InvokeDefaultRunnerIdentityMatch(startedAt.AddSeconds(-5), exePath, expected));
            Assert.False(InvokeDefaultRunnerIdentityMatch(startedAt, Path.Combine(Path.GetTempPath(), "other", "BEA.exe"), expected));
            Assert.False(InvokeDefaultRunnerIdentityMatch(startedAt, null, expected));
            Assert.False(InvokeDefaultRunnerIdentityMatch(startedAt.AddSeconds(1), Path.Combine(Path.GetTempPath(), "other", "BEA.exe"), expected));
            Assert.False(InvokeDefaultRunnerIdentityMatch(startedAt.AddSeconds(1), null, expected));
        }

        [Fact]
        public void DefaultRunnerStopReportsAlreadyGoneWithoutClaimingAnExactStop()
        {
            string exePath = Path.Combine(Path.GetTempPath(), "safe-copy", "BEA.exe");
            var expected = new GameProfileManagedProcess(
                ProcessId: int.MaxValue,
                ExecutablePath: exePath,
                WorkingDirectory: Path.GetDirectoryName(exePath)!,
                Arguments: Array.Empty<string>(),
                StartedAt: DateTimeOffset.UtcNow,
                ManifestPath: Path.Combine(Path.GetDirectoryName(exePath)!, "onslaught-profile-manifest.json"));

            GameProfileStopResult result = InvokeDefaultRunnerStop(expected);

            Assert.True(result.Success);
            Assert.True(result.AlreadyGone);
            Assert.False(result.StopRequested);
            Assert.False(result.ExitObserved);
        }

        [Fact]
        public void DefaultRunnerStopRetainsExactHandleAfterReacquiringDisposedProcess()
        {
            string executablePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System), "PING.EXE");
            GameProfileManagedProcess? expected = null;
            TimeSpan stopTimeout = TimeSpan.FromSeconds(5);

            try
            {
                using (Process started = Process.Start(new ProcessStartInfo
                {
                    FileName = executablePath,
                    Arguments = "-n 60 127.0.0.1",
                    CreateNoWindow = true,
                    UseShellExecute = false,
                }) ?? throw new InvalidOperationException("Test ping process did not start."))
                {
                    Assert.False(started.HasExited);
                    string startedExecutablePath = WaitForExactTestProcessPath(started, TimeSpan.FromSeconds(5));
                    expected = new GameProfileManagedProcess(
                        ProcessId: started.Id,
                        ExecutablePath: startedExecutablePath,
                        WorkingDirectory: Path.GetDirectoryName(startedExecutablePath)!,
                        Arguments: Array.Empty<string>(),
                        StartedAt: new DateTimeOffset(started.StartTime),
                        ManifestPath: Path.Combine(Path.GetDirectoryName(startedExecutablePath)!, "onslaught-profile-manifest.json"));
                }

                GameProfileStopResult result = InvokeDefaultRunnerStop(expected, stopTimeout);

                Assert.True(result.Success, result.Message);
                Assert.Equal(expected.ProcessId, result.ProcessId);
                Assert.True(result.LiveBeforeStop);
                Assert.True(result.StopRequested);
                Assert.True(result.ExitObserved);
                Assert.False(result.AlreadyGone);
                Assert.NotNull(result.ExitTime);
                Assert.Throws<ArgumentException>(() => Process.GetProcessById(expected.ProcessId));
            }
            finally
            {
                if (expected is not null)
                    StopExactTestProcess(expected, stopTimeout);
            }
        }

        [Fact]
        public void DefaultRunnerStopRejectsInvalidTimeoutBeforeTouchingExactProcess()
        {
            string executablePath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System), "PING.EXE");
            GameProfileManagedProcess? expected = null;
            TimeSpan cleanupTimeout = TimeSpan.FromSeconds(5);

            try
            {
                using (Process started = Process.Start(new ProcessStartInfo
                {
                    FileName = executablePath,
                    Arguments = "-n 60 127.0.0.1",
                    CreateNoWindow = true,
                    UseShellExecute = false,
                }) ?? throw new InvalidOperationException("Test ping process did not start."))
                {
                    Assert.False(started.HasExited);
                    string startedExecutablePath = WaitForExactTestProcessPath(started, TimeSpan.FromSeconds(5));
                    expected = new GameProfileManagedProcess(
                        ProcessId: started.Id,
                        ExecutablePath: startedExecutablePath,
                        WorkingDirectory: Path.GetDirectoryName(startedExecutablePath)!,
                        Arguments: Array.Empty<string>(),
                        StartedAt: new DateTimeOffset(started.StartTime),
                        ManifestPath: Path.Combine(Path.GetDirectoryName(startedExecutablePath)!, "onslaught-profile-manifest.json"));
                }

                GameProfileStopResult result = InvokeDefaultRunnerStop(expected, TimeSpan.FromMilliseconds(-2));

                Assert.True(IsExactTestProcessLive(expected));
                Assert.False(result.Success);
                Assert.False(result.AlreadyGone);
                Assert.False(result.StopRequested);
                Assert.False(result.ExitObserved);
            }
            finally
            {
                if (expected is not null)
                    StopExactTestProcess(expected, cleanupTimeout);
            }
        }

        private static string PrepareSourceGameRoot(string sourceRoot)
        {
            Directory.CreateDirectory(sourceRoot);
            Directory.CreateDirectory(Path.Combine(sourceRoot, "data", "Resources"));

            string exePath = Path.Combine(sourceRoot, "BEA.exe");
            SeedExe(exePath);
            File.WriteAllBytes(Path.Combine(sourceRoot, "defaultoptions.bea"), new byte[10_004]);
            File.WriteAllText(Path.Combine(sourceRoot, "data", "Resources", "base_res_PC.aya"), "resource");
            File.WriteAllBytes(Path.Combine(sourceRoot, "binkw32.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "ogg.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "vorbis.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "zlib.dll"), new byte[] { 1 });
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

        private sealed class FakeGameProfileProcessRunner : IGameProfileProcessRunner
        {
            public List<GameProfileProcessStartRequest> Starts { get; } = new();

            public List<GameProfileManagedProcess> Stops { get; } = new();

            public GameProfileProcessStartResult Start(GameProfileProcessStartRequest request)
            {
                Starts.Add(request);
                return new GameProfileProcessStartResult(1234);
            }

            public GameProfileStopResult Stop(GameProfileManagedProcess process, TimeSpan gracefulTimeout)
            {
                Stops.Add(process);
        return new GameProfileStopResult(true, process.ProcessId, "Stopped managed playable copied game folder.");
            }
        }

        private static bool InvokeDefaultRunnerIdentityMatch(
            DateTimeOffset runningStartedAt,
            string? modulePath,
            GameProfileManagedProcess expected)
        {
            Type runnerType = typeof(GameProfileRuntimeService).Assembly.GetType("Onslaught___Career_Editor.DefaultGameProfileProcessRunner")
                ?? throw new InvalidOperationException("Default runner type was not found.");
            MethodInfo method = runnerType.GetMethod("MatchesManagedProcessIdentity", BindingFlags.NonPublic | BindingFlags.Static)
                ?? throw new InvalidOperationException("Default runner identity helper was not found.");
            return (bool)method.Invoke(null, new object?[] { runningStartedAt, modulePath, expected })!;
        }

        private static GameProfileStopResult InvokeDefaultRunnerStop(GameProfileManagedProcess expected, TimeSpan? timeout = null)
        {
            Type runnerType = typeof(GameProfileRuntimeService).Assembly.GetType("Onslaught___Career_Editor.DefaultGameProfileProcessRunner")
                ?? throw new InvalidOperationException("Default runner type was not found.");
            object instance = runnerType.GetProperty("Instance", BindingFlags.Public | BindingFlags.Static)?.GetValue(null)
                ?? throw new InvalidOperationException("Default runner instance was not found.");
            MethodInfo method = runnerType.GetMethod("Stop", BindingFlags.Public | BindingFlags.Instance)
                ?? throw new InvalidOperationException("Default runner stop method was not found.");
            return (GameProfileStopResult)method.Invoke(instance, new object[] { expected, timeout ?? TimeSpan.FromMilliseconds(50) })!;
        }

        private static void StopExactTestProcess(GameProfileManagedProcess expected, TimeSpan timeout)
        {
            try
            {
                bool exactProcessHandlePinned = false;
                using Process remaining = Process.GetProcessById(expected.ProcessId);
                var exactProcessHandle = remaining.SafeHandle;
                try
                {
                    exactProcessHandle.DangerousAddRef(ref exactProcessHandlePinned);
                    DateTimeOffset startedAt = new(remaining.StartTime);
                    string? executablePath = remaining.MainModule?.FileName;
                    if (!InvokeDefaultRunnerIdentityMatch(startedAt, executablePath, expected) || remaining.HasExited)
                        return;

                    remaining.Kill(entireProcessTree: false);
                    remaining.WaitForExit((int)timeout.TotalMilliseconds);
                }
                finally
                {
                    if (exactProcessHandlePinned)
                        exactProcessHandle.DangerousRelease();
                }
            }
            catch (Exception ex) when (ex is ArgumentException or System.ComponentModel.Win32Exception or InvalidOperationException)
            {
            }
        }

        private static bool IsExactTestProcessLive(GameProfileManagedProcess expected)
        {
            try
            {
                bool exactProcessHandlePinned = false;
                using Process remaining = Process.GetProcessById(expected.ProcessId);
                var exactProcessHandle = remaining.SafeHandle;
                try
                {
                    exactProcessHandle.DangerousAddRef(ref exactProcessHandlePinned);
                    DateTimeOffset startedAt = new(remaining.StartTime);
                    string? executablePath = remaining.MainModule?.FileName;
                    return InvokeDefaultRunnerIdentityMatch(startedAt, executablePath, expected) && !remaining.HasExited;
                }
                finally
                {
                    if (exactProcessHandlePinned)
                        exactProcessHandle.DangerousRelease();
                }
            }
            catch (Exception ex) when (ex is ArgumentException or System.ComponentModel.Win32Exception or InvalidOperationException)
            {
                return false;
            }
        }

        private static string WaitForExactTestProcessPath(Process process, TimeSpan timeout)
        {
            bool exactProcessHandlePinned = false;
            var exactProcessHandle = process.SafeHandle;
            try
            {
                exactProcessHandle.DangerousAddRef(ref exactProcessHandlePinned);
                Stopwatch wait = Stopwatch.StartNew();
                while (wait.Elapsed < timeout)
                {
                    process.Refresh();
                    if (process.HasExited)
                        throw new InvalidOperationException("Test ping process exited before its exact path was available.");

                    string? executablePath = process.MainModule?.FileName;
                    if (!string.IsNullOrWhiteSpace(executablePath))
                        return executablePath;

                    process.WaitForExit(10);
                }

                throw new InvalidOperationException("Test ping process path was unavailable before the readiness timeout.");
            }
            finally
            {
                if (exactProcessHandlePinned)
                    exactProcessHandle.DangerousRelease();
            }
        }
    }
}
