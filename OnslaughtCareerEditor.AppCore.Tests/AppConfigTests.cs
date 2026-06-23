using System;
using System.IO;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class AppConfigTests
    {
        [Fact]
        public void GetConfigPath_UsesExplicitConfigRootOverride()
        {
            string? previous = Environment.GetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT");
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-config-root-{Guid.NewGuid():N}");

            try
            {
                Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", root);

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
                Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", previous);
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
            string? previous = Environment.GetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT");
            string root = Path.Combine(Path.GetTempPath(), $"onslaught-config-normalize-{Guid.NewGuid():N}");

            try
            {
                Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", root);
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
                Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", previous);
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
    }
}
