using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Application configuration for Onslaught Career Editor.
    /// Stores settings in %APPDATA%/OnslaughtCareerEditor/config.json
    /// </summary>
    public class AppConfig
    {
        private static readonly string ConfigDirName = "OnslaughtCareerEditor";
        private static readonly string LegacyConfigDirName = "onslaught-career-editor";
        private static readonly string ConfigFileName = "config.json";
        private const int MinRecentFiles = 1;
        private const int MaxRecentFilesLimit = 50;

        public const int MinWindowWidth = 900;
        public const int MinWindowHeight = 600;
        public const int MaxWindowWidth = 2200;
        public const int MaxWindowHeight = 1400;

        /// <summary>
        /// Default Steam installation paths to check for Battle Engine Aquila
        /// </summary>
        private static readonly string[] DefaultSteamPaths = new[]
        {
            @"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila",
            @"C:\Program Files\Steam\steamapps\common\Battle Engine Aquila",
            @"D:\Steam\steamapps\common\Battle Engine Aquila",
            @"D:\SteamLibrary\steamapps\common\Battle Engine Aquila",
            @"E:\Steam\steamapps\common\Battle Engine Aquila",
            @"E:\SteamLibrary\steamapps\common\Battle Engine Aquila",
        };
        private const string GameDirectoryCandidatesEnvironmentVariable = "ONSLAUGHT_GAME_DIR_CANDIDATES";
        private const string SteamRootCandidatesEnvironmentVariable = "ONSLAUGHT_STEAM_ROOT_CANDIDATES";

        /// <summary>
        /// Subdirectories to search for save files within the game directory
        /// </summary>
        private static readonly string[] SaveSubdirs = new[]
        {
            "",          // Root of game folder
            "saves",     // Common save folder
            "Save",      // Alternative
            "savegames", // What BEA Steam version uses
        };

        // Configuration properties
        [JsonPropertyName("gameDirectory")]
        public string? GameDirectory { get; set; }

        [JsonPropertyName("recentFiles")]
        public List<string> RecentFiles { get; set; } = new();

        [JsonPropertyName("maxRecentFiles")]
        public int MaxRecentFiles { get; set; } = 10;

        [JsonPropertyName("windowWidth")]
        public int WindowWidth { get; set; } = 1100;

        [JsonPropertyName("windowHeight")]
        public int WindowHeight { get; set; } = 720;

        [JsonPropertyName("lastTab")]
        public int LastTab { get; set; } = -1;

        [JsonPropertyName("lastSaveSubTab")]
        public int LastSaveSubTab { get; set; } = 0;

        [JsonPropertyName("lastMediaSubTab")]
        public int LastMediaSubTab { get; set; } = 0;

        [JsonPropertyName("assetCatalogPath")]
        public string? AssetCatalogPath { get; set; }

        [JsonPropertyName("allowBackgroundAudio")]
        public bool AllowBackgroundAudio { get; set; } = true;

        [JsonPropertyName("allowBackgroundVideo")]
        public bool AllowBackgroundVideo { get; set; } = false;

        [JsonPropertyName("preventAudioVideoOverlap")]
        public bool PreventAudioVideoOverlap { get; set; } = true;


        /// <summary>
        /// Get the configuration directory path
        /// </summary>
        public static string GetConfigDir()
        {
            string configDir = GetConfigDirPath();
            Directory.CreateDirectory(configDir); // Ensure it exists
            return configDir;
        }

        public static string GetConfigDirPath()
        {
            return Path.Combine(GetConfigRoot(), ConfigDirName);
        }

        /// <summary>
        /// Get the configuration file path
        /// </summary>
        public static string GetConfigPath()
        {
            return Path.Combine(GetConfigDir(), ConfigFileName);
        }

        public static string GetPatchedOutputDir()
        {
            return Path.Combine(GetConfigDirPath(), "patched-output");
        }

        public static string GetGameProfilesDir()
        {
            return Path.Combine(GetConfigDirPath(), "GameProfiles");
        }

        /// <summary>
        /// Get the legacy configuration file path (pre-parity naming).
        /// </summary>
        public static string GetLegacyConfigPath()
        {
            string appData = GetConfigRoot();
            string legacyDir = Path.Combine(appData, LegacyConfigDirName);
            return Path.Combine(legacyDir, ConfigFileName);
        }

        private static string GetConfigRoot()
        {
            string? overrideRoot = Environment.GetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT");
            return string.IsNullOrWhiteSpace(overrideRoot)
                ? Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData)
                : Path.GetFullPath(overrideRoot);
        }

        /// <summary>
        /// Load configuration from disk, or create default if not exists
        /// </summary>
        public static AppConfig Load()
        {
            string configPath = GetConfigPath();
            string legacyPath = GetLegacyConfigPath();

            string? loadPath = null;
            if (File.Exists(configPath))
            {
                loadPath = configPath;
            }
            else if (File.Exists(legacyPath))
            {
                loadPath = legacyPath;
            }

            if (loadPath != null)
            {
                try
                {
                    string json = File.ReadAllText(loadPath);
                    var config = JsonSerializer.Deserialize<AppConfig>(json);
                    if (config != null)
                    {
                        config.NormalizeForUse();
                        if (loadPath == legacyPath && !File.Exists(configPath))
                        {
                            config.Save();
                        }
                        return config;
                    }
                    return new AppConfig();
                }
                catch (JsonException ex)
                {
                    Debug.WriteLine($"Config load failed (invalid JSON): {ex.Message}");
                }
                catch (IOException ex)
                {
                    Debug.WriteLine($"Config load failed (IO error): {ex.Message}");
                }
            }
            return new AppConfig();
        }

        /// <summary>
        /// Save configuration to disk
        /// </summary>
        /// <returns>True if save succeeded, false if an error occurred</returns>
        public bool Save()
        {
            try
            {
                NormalizeForUse();
                string configPath = GetConfigPath();
                var options = new JsonSerializerOptions
                {
                    WriteIndented = true
                };
                string json = JsonSerializer.Serialize(this, options);
                File.WriteAllText(configPath, json);
                return true;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Config save failed: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Get the configured game directory, or null if not set
        /// </summary>
        public string? GetGameDir()
        {
            if (!string.IsNullOrEmpty(GameDirectory) && Directory.Exists(GameDirectory))
            {
                return GameDirectory;
            }
            return null;
        }

        /// <summary>
        /// Get the configured game directory, or auto-detect and optionally persist it.
        /// </summary>
        public string? GetGameDirOrDetect(bool persistDetection = false)
        {
            string? configured = GetGameDir();
            if (!string.IsNullOrWhiteSpace(configured))
            {
                return configured;
            }

            string? detected = DetectGameDirectory();
            if (string.IsNullOrWhiteSpace(detected))
            {
                return null;
            }

            if (persistDetection)
            {
                GameDirectory = detected;
                Save();
            }

            return detected;
        }

        /// <summary>
        /// Set and persist the game directory
        /// </summary>
        /// <param name="path">Path to the game directory</param>
        /// <returns>True if path exists and was saved successfully, false otherwise</returns>
        public bool SetGameDir(string path)
        {
            if (!Directory.Exists(path))
                return false;
            GameDirectory = path;
            return Save();
        }

        /// <summary>
        /// Add a file to the recent files list
        /// </summary>
        public void AddRecentFile(string path)
        {
            NormalizeForUse();
            // Remove if already exists (to move to front)
            RecentFiles.Remove(path);
            RecentFiles.Insert(0, path);

            // Trim to max size
            if (RecentFiles.Count > MaxRecentFiles)
            {
                RecentFiles = RecentFiles.GetRange(0, MaxRecentFiles);
            }

            Save();
        }

        private void NormalizeForUse()
        {
            RecentFiles ??= new List<string>();
            MaxRecentFiles = Math.Clamp(MaxRecentFiles, MinRecentFiles, MaxRecentFilesLimit);
            WindowWidth = Math.Clamp(WindowWidth, MinWindowWidth, MaxWindowWidth);
            WindowHeight = Math.Clamp(WindowHeight, MinWindowHeight, MaxWindowHeight);

            if (RecentFiles.Count > MaxRecentFiles)
            {
                RecentFiles = RecentFiles.GetRange(0, MaxRecentFiles);
            }
        }

        /// <summary>
        /// Auto-detect a full Battle Engine Aquila installation directory.
        /// </summary>
        public static string? DetectGameDirectory()
        {
            foreach (string path in GetGameDirectoryCandidates())
            {
                if (InspectGameDirectory(path).Status == GameDirectoryStatus.FullInstall)
                {
                    return path;
                }
            }
            return null;
        }

        public static GameDirectoryInspection InspectGameDirectory(string? path)
        {
            if (string.IsNullOrWhiteSpace(path) || !Directory.Exists(path))
            {
                return new GameDirectoryInspection(GameDirectoryStatus.Missing, null, false, false, false, false);
            }

            string fullPath = Path.GetFullPath(path);
            bool hasExe = File.Exists(Path.Combine(fullPath, "BEA.exe")) || File.Exists(Path.Combine(fullPath, "bea.exe"));
            bool hasData = Directory.Exists(Path.Combine(fullPath, "data"));
            bool hasMusic = Directory.Exists(Path.Combine(fullPath, "data", "Music"));
            bool hasVideo = Directory.Exists(Path.Combine(fullPath, "data", "video"));

            GameDirectoryStatus status = (hasExe, hasData) switch
            {
                (true, true) => GameDirectoryStatus.FullInstall,
                (true, false) => GameDirectoryStatus.ExecutableOnly,
                (false, true) => GameDirectoryStatus.MediaOnly,
                _ => GameDirectoryStatus.Missing
            };

            return new GameDirectoryInspection(status, fullPath, hasExe, hasData, hasMusic, hasVideo);
        }

        private static IEnumerable<string> GetGameDirectoryCandidates()
        {
            string? overrideCandidates = Environment.GetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable);
            if (overrideCandidates != null)
            {
                if (!string.IsNullOrWhiteSpace(overrideCandidates))
                {
                    foreach (string path in overrideCandidates.Split(
                        Path.PathSeparator,
                        StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
                    {
                        yield return path;
                    }
                }

                foreach (string path in GetSteamLibraryGameDirectoryCandidates())
                {
                    yield return path;
                }
                yield break;
            }

            foreach (string path in DefaultSteamPaths)
            {
                yield return path;
            }
            foreach (string path in GetSteamLibraryGameDirectoryCandidates())
            {
                yield return path;
            }
        }

        private static IEnumerable<string> GetSteamLibraryGameDirectoryCandidates()
        {
            var libraryRoots = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string steamRoot in GetSteamRootCandidates())
            {
                libraryRoots.Add(steamRoot);
                string libraryFoldersPath = Path.Combine(steamRoot, "steamapps", "libraryfolders.vdf");
                foreach (string libraryRoot in ReadSteamLibraryRoots(libraryFoldersPath))
                {
                    libraryRoots.Add(libraryRoot);
                }
            }

            foreach (string libraryRoot in libraryRoots)
            {
                yield return Path.Combine(libraryRoot, "steamapps", "common", "Battle Engine Aquila");
            }
        }

        private static IEnumerable<string> GetSteamRootCandidates()
        {
            string? overrideCandidates = Environment.GetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable);
            if (!string.IsNullOrWhiteSpace(overrideCandidates))
            {
                foreach (string path in overrideCandidates.Split(
                    Path.PathSeparator,
                    StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
                {
                    yield return path;
                }
                yield break;
            }

            var candidates = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
            {
                @"C:\Program Files (x86)\Steam",
                @"C:\Program Files\Steam",
                @"D:\Steam",
                @"D:\SteamLibrary",
                @"E:\Steam",
                @"E:\SteamLibrary",
            };

            foreach (string defaultGamePath in DefaultSteamPaths)
            {
                DirectoryInfo? directory = new(defaultGamePath);
                DirectoryInfo? steamApps = directory.Parent?.Parent;
                DirectoryInfo? steamRoot = steamApps?.Parent;
                if (steamRoot != null)
                {
                    candidates.Add(steamRoot.FullName);
                }
            }

            foreach (string path in candidates)
            {
                yield return path;
            }
        }

        private static IEnumerable<string> ReadSteamLibraryRoots(string libraryFoldersPath)
        {
            if (!File.Exists(libraryFoldersPath))
            {
                yield break;
            }

            string text;
            try
            {
                text = File.ReadAllText(libraryFoldersPath);
            }
            catch (IOException)
            {
                yield break;
            }
            catch (UnauthorizedAccessException)
            {
                yield break;
            }

            foreach (string value in ReadVdfQuotedPairs(text, key: "path"))
            {
                yield return value;
            }

            foreach (string value in ReadVdfNumericLibraryRows(text))
            {
                yield return value;
            }
        }

        private static IEnumerable<string> ReadVdfQuotedPairs(string text, string key)
        {
            string quotedKey = $"\"{key}\"";
            foreach (string line in text.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                string trimmed = line.Trim();
                if (!trimmed.StartsWith(quotedKey, StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                string remainder = trimmed[quotedKey.Length..].Trim();
                string? value = ReadLeadingQuotedValue(remainder);
                if (!string.IsNullOrWhiteSpace(value))
                {
                    yield return value.Replace(@"\\", @"\");
                }
            }
        }

        private static IEnumerable<string> ReadVdfNumericLibraryRows(string text)
        {
            foreach (string line in text.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries))
            {
                string trimmed = line.Trim();
                if (!trimmed.StartsWith('"'))
                {
                    continue;
                }

                int endKey = trimmed.IndexOf('"', 1);
                if (endKey <= 1)
                {
                    continue;
                }

                string key = trimmed.Substring(1, endKey - 1);
                if (!int.TryParse(key, out _))
                {
                    continue;
                }

                string? value = ReadLeadingQuotedValue(trimmed[(endKey + 1)..].Trim());
                if (!string.IsNullOrWhiteSpace(value) &&
                    value.Contains("Steam", StringComparison.OrdinalIgnoreCase))
                {
                    yield return value.Replace(@"\\", @"\");
                }
            }
        }

        private static string? ReadLeadingQuotedValue(string text)
        {
            if (!text.StartsWith('"'))
            {
                return null;
            }

            int end = text.IndexOf('"', 1);
            return end <= 1 ? null : text.Substring(1, end - 1);
        }

        /// <summary>
        /// Find all BEA save / options files in the game directory and common locations.
        ///
        /// Files of interest:
        /// - Career saves: *.bes (typically in savegames/)
        /// - Global options: defaultoptions.bea (in game root for the Steam build)
        /// </summary>
        public static List<SaveFileInfo> FindSaveFiles(string? gameDir = null)
        {
            var saves = new List<SaveFileInfo>();
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var dirsToSearch = new List<string>();

            // If no game dir provided, try to get from config or detect
            if (string.IsNullOrEmpty(gameDir))
            {
                var config = Load();
                gameDir = config.GetGameDir() ?? DetectGameDirectory();
            }

            // Add game directory subdirectories
            if (!string.IsNullOrEmpty(gameDir) && Directory.Exists(gameDir))
            {
                foreach (string subdir in SaveSubdirs)
                {
                    string searchDir = string.IsNullOrEmpty(subdir)
                        ? gameDir
                        : Path.Combine(gameDir, subdir);
                    dirsToSearch.Add(searchDir);
                }
            }

            // Also search Documents folder
            string docsPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments),
                "Battle Engine Aquila");
            dirsToSearch.Add(docsPath);

            // Also search LocalAppData
            string localAppData = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "Battle Engine Aquila");
            dirsToSearch.Add(localAppData);

            // Search all directories
            foreach (string searchDir in dirsToSearch)
            {
                if (!Directory.Exists(searchDir))
                {
                    continue;
                }

                try
                {
                    foreach (string pattern in new[] { "*.bes", "*.bea" })
                    {
                        foreach (string file in Directory.GetFiles(searchDir, pattern))
                        {
                            // Avoid duplicates
                            if (seen.Contains(file))
                            {
                                continue;
                            }
                            seen.Add(file);

                            try
                            {
                                var info = new FileInfo(file);
                                saves.Add(new SaveFileInfo
                                {
                                    Path = file,
                                    Name = Path.GetFileNameWithoutExtension(file),
                                    Size = info.Length,
                                    Modified = info.LastWriteTime,
                                    IsValid = BesFilePatcher.IsValidBesFile(file)
                                });
                            }
                            catch (IOException)
                            {
                                // Skip files we can't access
                            }
                        }
                    }
                }
                catch (UnauthorizedAccessException)
                {
                    // Skip directories we can't access
                }
            }

            // Sort by modification time (newest first), then stable tie-break by name/path.
            saves.Sort((a, b) =>
            {
                int byModified = b.Modified.CompareTo(a.Modified);
                if (byModified != 0)
                    return byModified;
                int byName = string.Compare(a.Name, b.Name, StringComparison.OrdinalIgnoreCase);
                if (byName != 0)
                    return byName;
                return string.Compare(a.Path, b.Path, StringComparison.OrdinalIgnoreCase);
            });
            return saves;
        }
    }

    /// <summary>
    /// Information about a save file
    /// </summary>
    public class SaveFileInfo
    {
        public string Path { get; set; } = "";
        public string Name { get; set; } = "";
        public long Size { get; set; }
        public DateTime Modified { get; set; }
        public bool IsValid { get; set; }
    }

    public enum GameDirectoryStatus
    {
        Missing,
        MediaOnly,
        ExecutableOnly,
        FullInstall
    }

    public sealed record GameDirectoryInspection(
        GameDirectoryStatus Status,
        string? FullPath,
        bool HasExecutable,
        bool HasData,
        bool HasMusic,
        bool HasVideo);
}
