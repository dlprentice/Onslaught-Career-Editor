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
        public int WindowWidth { get; set; } = 900;

        [JsonPropertyName("windowHeight")]
        public int WindowHeight { get; set; } = 600;

        [JsonPropertyName("lastTab")]
        public int LastTab { get; set; } = 0;

        [JsonPropertyName("lastSaveSubTab")]
        public int LastSaveSubTab { get; set; } = 0;

        [JsonPropertyName("lastMediaSubTab")]
        public int LastMediaSubTab { get; set; } = 0;

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
            string appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            string configDir = Path.Combine(appData, ConfigDirName);
            Directory.CreateDirectory(configDir); // Ensure it exists
            return configDir;
        }

        /// <summary>
        /// Get the configuration file path
        /// </summary>
        public static string GetConfigPath()
        {
            return Path.Combine(GetConfigDir(), ConfigFileName);
        }

        /// <summary>
        /// Get the legacy configuration file path (pre-parity naming).
        /// </summary>
        public static string GetLegacyConfigPath()
        {
            string appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            string legacyDir = Path.Combine(appData, LegacyConfigDirName);
            return Path.Combine(legacyDir, ConfigFileName);
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

        /// <summary>
        /// Auto-detect Battle Engine Aquila installation directory
        /// </summary>
        public static string? DetectGameDirectory()
        {
            foreach (string path in DefaultSteamPaths)
            {
                if (Directory.Exists(path))
                {
                    // Verify it's actually BEA by checking for known files
                    string beaExe = Path.Combine(path, "BEA.exe");
                    string dataDir = Path.Combine(path, "data");
                    if (File.Exists(beaExe) || Directory.Exists(dataDir))
                    {
                        return path;
                    }
                }
            }
            return null;
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
}
