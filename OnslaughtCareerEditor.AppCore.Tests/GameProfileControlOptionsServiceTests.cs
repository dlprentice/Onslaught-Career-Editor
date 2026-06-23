using System.Buffers.Binary;
using System.Runtime.InteropServices;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class GameProfileControlOptionsServiceTests
    {
        [Fact]
        public void ConfigurationKeybindRow_PlayerOverrideAccessibleNamesAreDistinct()
        {
            ConfigurationKeybindRow row = new()
            {
                GroupLabel = "Movement",
                ActionLabel = "Forward",
            };

            Assert.Equal("Player 1 override for Movement Forward", row.Player1AccessibleName);
            Assert.Equal("Player 2 override for Movement Forward", row.Player2AccessibleName);
            Assert.NotEqual(row.Player1AccessibleName, row.Player2AccessibleName);
        }

        [Fact]
        public void ApplyToSafeCopy_WritesCopiedDefaultOptionsOnlyAndCreatesBackup()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            PrepareSourceGameRoot(sourceRoot);
            string sourceOptionsPath = Path.Combine(sourceRoot, "defaultoptions.bea");
            byte[] sourceOptionsBefore = File.ReadAllBytes(sourceOptionsPath);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options",
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileControlOptionsResult result = GameProfileControlOptionsService.ApplyToSafeCopy(
                    new GameProfileControlOptionsRequest(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        MouseSensitivityOverride: GameProfileControlOptionsService.SharperMouseLookSensitivity,
                        ControllerConfigP1Override: 2u,
                        ControllerConfigP2Override: 3u));

                Assert.Equal(Path.Combine(prepared.TargetGameRoot, "defaultoptions.bea"), result.OptionsPath);
                Assert.Equal(2.25f, result.MouseSensitivity, precision: 3);
                Assert.Equal(2u, result.ControllerConfigP1);
                Assert.Equal(3u, result.ControllerConfigP2);
                Assert.NotEqual(result.HashBefore, result.HashAfter);
                Assert.Contains(
                    result.ChangedRanges,
                    range => RangeIntersects(range, 0x26C2, 4));
                Assert.Contains(
                    result.ChangedRanges,
                    range => RangeIntersects(range, 0x24B6, 4));
                Assert.Contains(
                    result.ChangedRanges,
                    range => RangeIntersects(range, 0x24BA, 4));
                Assert.Single(result.Backups);
                Assert.True(File.Exists(result.ManifestPath));
                Assert.Equal(GameProfileControlOptionsService.ProofStatusOptionsByteMaterializedOnly, result.ProofStatus);
                Assert.Contains(GameProfileControlOptionsService.ManifestSchemaVersion, File.ReadAllText(result.ManifestPath));
                Assert.Contains(result.HashAfter, File.ReadAllText(result.ManifestPath));
                Assert.Contains("does not prove runtime input feel", result.Message);
                Assert.Equal(sourceOptionsBefore, File.ReadAllBytes(sourceOptionsPath));
                Assert.Single(Directory.GetFiles(prepared.TargetGameRoot, "defaultoptions.bea.*.bak"));
                _ = GameProfilePreflightService.BuildLaunchPlan(prepared.TargetGameRoot, Array.Empty<string>());
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
        public void ApplyToSafeCopy_ManifestMakesLaunchPlanRejectOptionsDrift()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-drift-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-drift",
                        ApplyWindowedCompatibilityPatch: false));

                _ = GameProfileControlOptionsService.ApplyToSafeCopy(
                    new GameProfileControlOptionsRequest(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        MouseSensitivityOverride: GameProfileControlOptionsService.SharperMouseLookSensitivity,
                        ControllerConfigP1Override: 2u,
                        ControllerConfigP2Override: 2u));

                string optionsPath = Path.Combine(prepared.TargetGameRoot, "defaultoptions.bea");
                byte[] bytes = File.ReadAllBytes(optionsPath);
                bytes[0x26C4] ^= 0x01;
                File.WriteAllBytes(optionsPath, bytes);

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfilePreflightService.BuildLaunchPlan(prepared.TargetGameRoot, Array.Empty<string>()));

                Assert.Contains("control-options manifest hash", ex.Message, StringComparison.OrdinalIgnoreCase);
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
        public void ApplyToSafeCopy_RejectsUnsupportedMouseSensitivityPreset()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-mouse-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-mouse",
                        ApplyWindowedCompatibilityPatch: false));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileControlOptionsService.ApplyToSafeCopy(
                        new GameProfileControlOptionsRequest(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        MouseSensitivityOverride: 1.75f)));

                Assert.Contains("mouse sensitivity preset", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(Directory.GetFiles(prepared.TargetGameRoot, "defaultoptions.bea.*.bak"));
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
        [InlineData(GameProfileControlOptionsService.BalancedMouseLookSensitivity)]
        [InlineData(GameProfileControlOptionsService.FastMouseLookSensitivity)]
        public void ApplyToSafeCopy_AllowsBoundedMouseSensitivityPresets(float mouseSensitivity)
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-bounded-mouse-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-bounded-mouse",
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileControlOptionsResult result = GameProfileControlOptionsService.ApplyToSafeCopy(
                    new GameProfileControlOptionsRequest(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        MouseSensitivityOverride: mouseSensitivity));

                Assert.Equal(mouseSensitivity, result.MouseSensitivity, precision: 3);
                Assert.Contains(
                    result.ChangedRanges,
                    range => RangeIntersects(range, 0x26C2, 4));
                Assert.Single(result.Backups);
                Assert.True(File.Exists(result.ManifestPath));
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
        public void ApplyToSafeCopy_WritesCopiedInvertOptionsOnly()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-invert-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            PrepareSourceGameRoot(sourceRoot);
            string sourceOptionsPath = Path.Combine(sourceRoot, "defaultoptions.bea");
            byte[] sourceOptionsBefore = File.ReadAllBytes(sourceOptionsPath);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-invert",
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileControlOptionsResult result = GameProfileControlOptionsService.ApplyToSafeCopy(
                    new GameProfileControlOptionsRequest(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        InvertWalkerP1Override: true,
                        InvertWalkerP2Override: true,
                        InvertFlightP1Override: true,
                        InvertFlightP2Override: true));

                Assert.True(result.InvertWalkerP1);
                Assert.True(result.InvertWalkerP2);
                Assert.True(result.InvertFlightP1);
                Assert.True(result.InvertFlightP2);
                Assert.Contains(result.ChangedRanges, range => RangeIntersects(range, 0x24A6, 4));
                Assert.Contains(result.ChangedRanges, range => RangeIntersects(range, 0x24AA, 4));
                Assert.Contains(result.ChangedRanges, range => RangeIntersects(range, 0x249E, 4));
                Assert.Contains(result.ChangedRanges, range => RangeIntersects(range, 0x24A2, 4));
                Assert.Single(result.Backups);
                Assert.True(File.Exists(result.ManifestPath));
                string manifest = File.ReadAllText(result.ManifestPath);
                Assert.Contains("\"invertWalkerP1\": true", manifest);
                Assert.Contains("\"invertFlightP1\": true", manifest);
                Assert.Equal(sourceOptionsBefore, File.ReadAllBytes(sourceOptionsPath));
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
        public void ApplyToSafeCopy_WritesCopiedInputIsolationForwardKeybindsOnly()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-input-isolation-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            PrepareSourceGameRoot(sourceRoot);
            string sourceOptionsPath = Path.Combine(sourceRoot, "defaultoptions.bea");
            byte[] sourceOptionsBefore = File.ReadAllBytes(sourceOptionsPath);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-input-isolation",
                        ApplyWindowedCompatibilityPatch: false));

                GameProfileControlOptionsResult result = GameProfileControlOptionsService.ApplyToSafeCopy(
                    new GameProfileControlOptionsRequest(
                        ProfileRoot: prepared.TargetGameRoot,
                        AppOwnedProfilesRoot: outputRoot,
                        KeybindRows: new[]
                        {
                            new ConfigurationKeybindRow
                            {
                                GroupLabel = "Movement",
                                ActionLabel = "Forward",
                                EntryId = 0x1f,
                                KeyboardDeviceCode = 9u,
                                Player1Token = "Q",
                                Player2Token = "E",
                            },
                        }));

                ConfigurationSnapshot snapshot = ConfigurationEditorService.LoadConfigurationSnapshot(result.OptionsPath);
                ConfigurationKeybindRow forward = Assert.Single(snapshot.KeybindRows, row => row.EntryId == 0x1f);
                Assert.Equal("Key Q", forward.CurrentPlayer1Token);
                Assert.Equal("Key E", forward.CurrentPlayer2Token);
                Assert.Contains(result.ChangedRanges, range => RangeIntersects(range, 0x24CA, 8));
                Assert.Contains(result.ChangedRanges, range => RangeIntersects(range, 0x24D6, 8));
                Assert.Single(result.Backups);
                string manifest = File.ReadAllText(result.ManifestPath);
                Assert.Contains("\"entryId\": 31", manifest);
                Assert.Contains("\"player1Token\": \"Q\"", manifest);
                Assert.Contains("\"player2Token\": \"E\"", manifest);
                Assert.Equal(sourceOptionsBefore, File.ReadAllBytes(sourceOptionsPath));
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
        public void ApplyToSafeCopy_RejectsHardlinkedDefaultOptionsWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-hardlink-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsidePath = Path.Combine(tempRoot, "outside-defaultoptions.bea");
            PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-hardlink",
                        ApplyWindowedCompatibilityPatch: false));

                string optionsPath = Path.Combine(prepared.TargetGameRoot, "defaultoptions.bea");
                if (!CreateHardLink(outsidePath, optionsPath, IntPtr.Zero))
                    return;

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileControlOptionsService.ApplyToSafeCopy(
                        new GameProfileControlOptionsRequest(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            MouseSensitivityOverride: GameProfileControlOptionsService.SharperMouseLookSensitivity)));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(Directory.GetFiles(prepared.TargetGameRoot, "defaultoptions.bea.*.bak"));
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
        public void ApplyToSafeCopy_RejectsHardlinkedControlOptionsManifestBeforeOptionsMutationWhenSupported()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-manifest-hardlink-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsidePath = Path.Combine(tempRoot, "outside-control-manifest.json");
            PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-manifest-hardlink",
                        ApplyWindowedCompatibilityPatch: false));

                string optionsPath = Path.Combine(prepared.TargetGameRoot, "defaultoptions.bea");
                byte[] optionsBefore = File.ReadAllBytes(optionsPath);
                string manifestPath = Path.Combine(prepared.TargetGameRoot, GameProfileControlOptionsService.ManifestFileName);
                File.WriteAllText(outsidePath, "{}");
                if (!CreateHardLink(manifestPath, outsidePath, IntPtr.Zero))
                    return;

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileControlOptionsService.ApplyToSafeCopy(
                        new GameProfileControlOptionsRequest(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            MouseSensitivityOverride: GameProfileControlOptionsService.SharperMouseLookSensitivity)));

                Assert.Contains("hardlinked", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(optionsBefore, File.ReadAllBytes(optionsPath));
                Assert.Empty(Directory.GetFiles(prepared.TargetGameRoot, "defaultoptions.bea.*.bak"));
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
        public void ApplyToSafeCopy_RejectsReparsePointControlOptionsManifestBeforeOptionsMutationWhenSupported()
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-manifest-reparse-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            string outsidePath = Path.Combine(tempRoot, "outside-control-manifest.json");
            PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-manifest-reparse",
                        ApplyWindowedCompatibilityPatch: false));

                string optionsPath = Path.Combine(prepared.TargetGameRoot, "defaultoptions.bea");
                byte[] optionsBefore = File.ReadAllBytes(optionsPath);
                string manifestPath = Path.Combine(prepared.TargetGameRoot, GameProfileControlOptionsService.ManifestFileName);
                File.WriteAllText(outsidePath, "{}");
                try
                {
                    File.CreateSymbolicLink(manifestPath, outsidePath);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
                {
                    return;
                }

                InvalidOperationException reparseEx = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileControlOptionsService.ApplyToSafeCopy(
                        new GameProfileControlOptionsRequest(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            MouseSensitivityOverride: GameProfileControlOptionsService.SharperMouseLookSensitivity)));

                Assert.Contains("reparse", reparseEx.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(optionsBefore, File.ReadAllBytes(optionsPath));
                Assert.Empty(Directory.GetFiles(prepared.TargetGameRoot, "defaultoptions.bea.*.bak"));
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
        [InlineData(0u)]
        [InlineData(5u)]
        public void ApplyToSafeCopy_RejectsOutOfRangeControllerConfigurations(uint controllerConfig)
        {
            string tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-control-options-range-{Guid.NewGuid():N}");
            string sourceRoot = Path.Combine(tempRoot, "source-game");
            string outputRoot = Path.Combine(tempRoot, "profiles");
            PrepareSourceGameRoot(sourceRoot);

            try
            {
                GameProfilePrepareResult prepared = GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceRoot,
                        OutputRoot: outputRoot,
                        ProfileName: "control-options-range",
                        ApplyWindowedCompatibilityPatch: false));

                InvalidOperationException ex = Assert.Throws<InvalidOperationException>(() =>
                    GameProfileControlOptionsService.ApplyToSafeCopy(
                        new GameProfileControlOptionsRequest(
                            ProfileRoot: prepared.TargetGameRoot,
                            AppOwnedProfilesRoot: outputRoot,
                            ControllerConfigP1Override: controllerConfig)));

                Assert.Contains("controller configuration", ex.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Empty(Directory.GetFiles(prepared.TargetGameRoot, "defaultoptions.bea.*.bak"));
            }
            finally
            {
                if (Directory.Exists(tempRoot))
                {
                    Directory.Delete(tempRoot, recursive: true);
                }
            }
        }

        private static void PrepareSourceGameRoot(string sourceRoot)
        {
            Directory.CreateDirectory(sourceRoot);
            Directory.CreateDirectory(Path.Combine(sourceRoot, "data", "Resources"));

            File.WriteAllBytes(Path.Combine(sourceRoot, "BEA.exe"), new byte[] { 0x4D, 0x5A, 0x90, 0x00 });
            WriteValidOptionsFile(Path.Combine(sourceRoot, "defaultoptions.bea"));
            File.WriteAllText(Path.Combine(sourceRoot, "data", "Resources", "base_res_PC.aya"), "resource");
            File.WriteAllBytes(Path.Combine(sourceRoot, "binkw32.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "ogg.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "vorbis.dll"), new byte[] { 1 });
            File.WriteAllBytes(Path.Combine(sourceRoot, "zlib.dll"), new byte[] { 1 });
        }

        private static void WriteValidOptionsFile(string path)
        {
            byte[] buffer = new byte[BesFilePatcher.EXPECTED_FILE_SIZE];
            BinaryPrimitives.WriteUInt16LittleEndian(buffer.AsSpan(0, 2), BesFilePatcher.VERSION_WORD);
            BinaryPrimitives.WriteUInt32LittleEndian(buffer.AsSpan(0x24BE, 4), 1u);
            BinaryPrimitives.WriteInt32LittleEndian(buffer.AsSpan(0x24BE + 0x04, 4), 0x1F);
            BinaryPrimitives.WriteSingleLittleEndian(buffer.AsSpan(0x26BE + 0x04, 4), 1.0f);
            File.WriteAllBytes(path, buffer);
        }

        private static bool RangeIntersects(GameProfileControlOptionsChangeRange range, int offset, int length)
        {
            return range.Offset < offset + length && range.Offset + range.Length > offset;
        }

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        private static extern bool CreateHardLink(
            string lpFileName,
            string lpExistingFileName,
            IntPtr lpSecurityAttributes);
    }
}
