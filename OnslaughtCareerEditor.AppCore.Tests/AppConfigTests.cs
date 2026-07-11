using System;
using System.IO;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    [Collection(AppConfigEnvironmentCollection.Name)]
    public sealed class AppConfigTests
    {
        private const string ConfigRootEnvironmentVariable = "ONSLAUGHT_APP_CONFIG_ROOT";
        private const string GameDirectoryCandidatesEnvironmentVariable = "ONSLAUGHT_GAME_DIR_CANDIDATES";
        private const string SteamRootCandidatesEnvironmentVariable = "ONSLAUGHT_STEAM_ROOT_CANDIDATES";

        [Fact]
        public void GetConfigPath_UsesExplicitConfigRootOverride()
        {
            string? previous = Environment.GetEnvironmentVariable(ConfigRootEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-config-root-{Guid.NewGuid():N}");

            try
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, root);

                string expectedPath = Path.Combine(Path.GetFullPath(root), "OnslaughtCareerEditor", "config.json");
                Assert.Equal(expectedPath, AppConfig.GetConfigPath());

                var config = new AppConfig
                {
                    AllowBackgroundAudio = false,
                    LastTab = -1
                };

                Assert.True(config.Save());
                Assert.True(File.Exists(expectedPath));
                Assert.False(AppConfig.Load().AllowBackgroundAudio);
                Assert.Equal(-1, AppConfig.Load().LastTab);
            }
            finally
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, previous);
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        [Fact]
        public void BuildDefaultSaveOutputPath_UsesAppOwnedConfigRootWithoutCreatingIt()
        {
            string? previous = Environment.GetEnvironmentVariable(ConfigRootEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-patched-output-{Guid.NewGuid():N}");

            try
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, root);

                string output = SaveEditorService.BuildDefaultSaveOutputPath(@"C:\game\savegames\career.bes");

                Assert.Equal(
                    Path.Combine(Path.GetFullPath(root), "OnslaughtCareerEditor", "patched-output", "career_patched.bes"),
                    output);
                Assert.False(Directory.Exists(root));
                Assert.False(Directory.Exists(Path.Combine(root, "OnslaughtCareerEditor")));
                Assert.False(Directory.Exists(Path.GetDirectoryName(output)));
            }
            finally
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, previous);
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        [Fact]
        public void PatchFile_CreatesValidatedAppOwnedDefaultOutputDirectory()
        {
            string? previous = Environment.GetEnvironmentVariable(ConfigRootEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-patched-output-write-{Guid.NewGuid():N}");
            Directory.CreateDirectory(root);
            string input = Path.Combine(root, "input.bes");
            WriteValidSaveLikeFile(input);

            try
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, root);
                string output = SaveEditorService.BuildDefaultSaveOutputPath(input);
                Assert.False(Directory.Exists(Path.GetDirectoryName(output)));

                PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

                Assert.True(result.Success, result.Message);
                Assert.True(File.Exists(output));
                Assert.Equal(File.ReadAllBytes(input), File.ReadAllBytes(output));
            }
            finally
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, previous);
                if (Directory.Exists(root))
                    Directory.Delete(root, recursive: true);
            }
        }

        [Fact]
        public void PatchFile_RejectsDefaultOutputRootInsideGameTreeBeforeDirectoryCreation()
        {
            string? previous = Environment.GetEnvironmentVariable(ConfigRootEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-patched-output-game-{Guid.NewGuid():N}");
            string gameRoot = Path.Combine(root, "fake-game");
            Directory.CreateDirectory(Path.Combine(gameRoot, "data"));
            File.WriteAllBytes(Path.Combine(gameRoot, "BEA.exe"), [0x4D, 0x5A]);
            string input = Path.Combine(root, "input.bes");
            WriteValidSaveLikeFile(input);

            try
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, gameRoot);
                string output = SaveEditorService.BuildDefaultSaveOutputPath(input);

                PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

                Assert.False(result.Success);
                Assert.Contains("game folder", result.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(gameRoot, "OnslaughtCareerEditor")));
            }
            finally
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, previous);
                if (Directory.Exists(root))
                    Directory.Delete(root, recursive: true);
            }
        }

        [Fact]
        public void PatchFile_RejectsReparseConfigRootBeforeDirectoryCreation()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string? previous = Environment.GetEnvironmentVariable(ConfigRootEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-patched-output-link-{Guid.NewGuid():N}");
            string realRoot = Path.Combine(root, "real-root");
            string linkedRoot = Path.Combine(root, "linked-root");
            Directory.CreateDirectory(realRoot);
            Directory.CreateSymbolicLink(linkedRoot, realRoot);
            string input = Path.Combine(root, "input.bes");
            WriteValidSaveLikeFile(input);

            try
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, linkedRoot);
                string output = SaveEditorService.BuildDefaultSaveOutputPath(input);

                PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

                Assert.False(result.Success);
                Assert.Contains("reparse", result.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(Directory.Exists(Path.Combine(realRoot, "OnslaughtCareerEditor")));
            }
            finally
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, previous);
                if (Directory.Exists(root))
                    Directory.Delete(root, recursive: true);
            }
        }

        [Fact]
        public void DetectGameDirectory_UsesOverrideCandidatesForPortableTests()
        {
            string? previousCandidates = Environment.GetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable);
            string gameDir = Path.Combine(Path.GetTempPath(), $"onslaught-detect-game-{Guid.NewGuid():N}");
            Directory.CreateDirectory(Path.Combine(gameDir, "data"));
            File.WriteAllText(Path.Combine(gameDir, "BEA.exe"), string.Empty);

            try
            {
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, gameDir);

                Assert.Equal(gameDir, AppConfig.DetectGameDirectory());
            }
            finally
            {
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, previousCandidates);
                if (Directory.Exists(gameDir))
                {
                    Directory.Delete(gameDir, recursive: true);
                }
            }
        }

        [Fact]
        public void DetectGameDirectory_DoesNotPersistPartialInstallFolders()
        {
            string? previousRoot = Environment.GetEnvironmentVariable(ConfigRootEnvironmentVariable);
            string? previousCandidates = Environment.GetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable);
            string? previousSteamRoots = Environment.GetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-config-partial-{Guid.NewGuid():N}");
            string mediaOnlyDir = Path.Combine(Path.GetTempPath(), $"onslaught-media-only-{Guid.NewGuid():N}");
            string exeOnlyDir = Path.Combine(Path.GetTempPath(), $"onslaught-exe-only-{Guid.NewGuid():N}");
            string emptySteamRoot = Path.Combine(Path.GetTempPath(), $"onslaught-empty-steam-root-{Guid.NewGuid():N}");
            Directory.CreateDirectory(Path.Combine(mediaOnlyDir, "data", "Music"));
            Directory.CreateDirectory(exeOnlyDir);
            Directory.CreateDirectory(emptySteamRoot);
            File.WriteAllText(Path.Combine(exeOnlyDir, "BEA.exe"), string.Empty);

            try
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, root);
                Environment.SetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable, emptySteamRoot);
                Environment.SetEnvironmentVariable(
                    GameDirectoryCandidatesEnvironmentVariable,
                    string.Join(Path.PathSeparator, mediaOnlyDir, exeOnlyDir));

                Assert.Null(AppConfig.DetectGameDirectory());
                var config = new AppConfig();
                Assert.Null(config.GetGameDirOrDetect(persistDetection: true));
                Assert.False(File.Exists(AppConfig.GetConfigPath()));
                Assert.Equal(GameDirectoryStatus.MediaOnly, AppConfig.InspectGameDirectory(mediaOnlyDir).Status);
                Assert.Equal(GameDirectoryStatus.ExecutableOnly, AppConfig.InspectGameDirectory(exeOnlyDir).Status);
            }
            finally
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, previousRoot);
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, previousCandidates);
                Environment.SetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable, previousSteamRoots);
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
                if (Directory.Exists(mediaOnlyDir))
                {
                    Directory.Delete(mediaOnlyDir, recursive: true);
                }
                if (Directory.Exists(exeOnlyDir))
                {
                    Directory.Delete(exeOnlyDir, recursive: true);
                }
                if (Directory.Exists(emptySteamRoot))
                {
                    Directory.Delete(emptySteamRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void GetGameDirOrDetect_PersistsDetectedGameDirectory()
        {
            string? previousRoot = Environment.GetEnvironmentVariable(ConfigRootEnvironmentVariable);
            string? previousCandidates = Environment.GetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-config-detect-{Guid.NewGuid():N}");
            string gameDir = Path.Combine(Path.GetTempPath(), $"onslaught-detect-persist-game-{Guid.NewGuid():N}");
            Directory.CreateDirectory(Path.Combine(gameDir, "data"));
            File.WriteAllText(Path.Combine(gameDir, "BEA.exe"), string.Empty);

            try
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, root);
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, gameDir);

                var config = new AppConfig();
                Assert.Equal(gameDir, config.GetGameDirOrDetect(persistDetection: true));

                AppConfig loaded = AppConfig.Load();
                Assert.Equal(gameDir, loaded.GetGameDir());
            }
            finally
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, previousRoot);
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, previousCandidates);
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
                if (Directory.Exists(gameDir))
                {
                    Directory.Delete(gameDir, recursive: true);
                }
            }
        }

        [Fact]
        public void DetectGameDirectory_ReadsSteamLibraryFoldersForCustomLibraries()
        {
            string? previousGameCandidates = Environment.GetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable);
            string? previousSteamRoots = Environment.GetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-steam-root-{Guid.NewGuid():N}");
            string steamRoot = Path.Combine(root, "Steam");
            string customLibrary = Path.Combine(root, "CustomSteamLibrary");
            string gameDir = Path.Combine(customLibrary, "steamapps", "common", "Battle Engine Aquila");
            Directory.CreateDirectory(Path.Combine(steamRoot, "steamapps"));
            Directory.CreateDirectory(Path.Combine(gameDir, "data"));
            File.WriteAllText(Path.Combine(gameDir, "BEA.exe"), string.Empty);
            File.WriteAllText(
                Path.Combine(steamRoot, "steamapps", "libraryfolders.vdf"),
                $$"""
                "libraryfolders"
                {
                    "0"
                    {
                        "path" "{{customLibrary.Replace(@"\", @"\\")}}"
                    }
                }
                """);

            try
            {
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, string.Empty);
                Environment.SetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable, steamRoot);

                Assert.Equal(gameDir, AppConfig.DetectGameDirectory());
            }
            finally
            {
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, previousGameCandidates);
                Environment.SetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable, previousSteamRoots);
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        [Fact]
        public void FindSaveFiles_DetectsRootOptionsAndSavegamesCareerFiles()
        {
            string gameDir = Path.Combine(Path.GetTempPath(), $"onslaught-save-detect-{Guid.NewGuid():N}");
            string savegamesDir = Path.Combine(gameDir, "savegames");
            Directory.CreateDirectory(savegamesDir);
            string optionsPath = Path.Combine(gameDir, "defaultoptions.bea");
            string careerPath = Path.Combine(savegamesDir, "career01.bes");
            string corruptPath = Path.Combine(savegamesDir, "notes.bea");

            try
            {
                WriteValidSaveLikeFile(optionsPath);
                WriteValidSaveLikeFile(careerPath);
                File.WriteAllText(corruptPath, "not a BEA save/options buffer");

                var localRows = AppConfig.FindSaveFiles(gameDir)
                    .FindAll(row => row.Path.StartsWith(gameDir, StringComparison.OrdinalIgnoreCase));

                Assert.Contains(localRows, row => row.Path == optionsPath && row.Name == "defaultoptions" && row.IsValid);
                Assert.Contains(localRows, row => row.Path == careerPath && row.Name == "career01" && row.IsValid);
                Assert.Contains(localRows, row => row.Path == corruptPath && row.Name == "notes" && !row.IsValid);
            }
            finally
            {
                if (Directory.Exists(gameDir))
                {
                    Directory.Delete(gameDir, recursive: true);
                }
            }
        }

        [Fact]
        public void Load_NormalizesMalformedUserConfig()
        {
            string? previous = Environment.GetEnvironmentVariable(ConfigRootEnvironmentVariable);
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-config-normalize-{Guid.NewGuid():N}");

            try
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, root);
                string configDir = Path.Combine(root, "OnslaughtCareerEditor");
                Directory.CreateDirectory(configDir);
                File.WriteAllText(
                    Path.Combine(configDir, "config.json"),
                    """
                    {
                      "gameDirectory": null,
                      "recentFiles": null,
                      "maxRecentFiles": -8,
                      "windowWidth": 1,
                      "windowHeight": 99999
                    }
                    """);

                AppConfig config = AppConfig.Load();

                Assert.NotNull(config.RecentFiles);
                Assert.Equal(1, config.MaxRecentFiles);
                Assert.Equal(AppConfig.MinWindowWidth, config.WindowWidth);
                Assert.Equal(AppConfig.MaxWindowHeight, config.WindowHeight);

                config.AddRecentFile("first.bes");
                config.AddRecentFile("second.bes");

                Assert.Single(config.RecentFiles);
                Assert.Equal("second.bes", config.RecentFiles[0]);
            }
            finally
            {
                Environment.SetEnvironmentVariable(ConfigRootEnvironmentVariable, previous);
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        private static void WriteValidSaveLikeFile(string path)
        {
            byte[] data = new byte[10_004];
            data[0] = 0xD1;
            data[1] = 0x4B;
            File.WriteAllBytes(path, data);
        }

        private static BesFilePatcher CreateNoOpPatcher() => new()
        {
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = false,
        };
    }
}
