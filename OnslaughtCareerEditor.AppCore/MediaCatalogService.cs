using NAudio.Vorbis;
using System.Text.RegularExpressions;

namespace Onslaught___Career_Editor
{
    public sealed class MediaCatalogService
    {
        // Cutscene files are named only by number (01.vid .. 33.vid); the game
        // ships no titles for them. A previous table here invented 33 story
        // titles ("Tatiana Introduction", "Boss Battle", "Plot Twist", ...) that
        // appear nowhere in the game, the lore library, or the evidence store,
        // and showed them to users as fact. They are removed: a cutscene is
        // presented by its number until a real title is demonstrated.
        //
        // The names below are different in kind — each is an expansion of an
        // abbreviation carried in the file's own name (LT = Lost Toys,
        // FE = front end, TWIMTBP = NVIDIA's "The Way It's Meant To Be Played"),
        // so the file itself is the evidence.
        private static readonly Dictionary<string, string> MainVideoDescriptions = new(StringComparer.OrdinalIgnoreCase)
        {
            ["OpeningFMV"] = "Opening Cinematic",
            ["UsTheMovie"] = "Credits Video",
            ["LTLogo"] = "Lost Toys Logo",
            ["FEBack128"] = "Menu Background",
            ["TWIMTBP_GefFX_640x480_Audio"] = "NVIDIA Logo",
            ["gill_m_on_a_fork"] = "Easter Egg: Gill on a Fork!"
        };

        public MediaCatalogSnapshot Load(string gameDirectory)
        {
            if (string.IsNullOrWhiteSpace(gameDirectory))
            {
                return MediaCatalogSnapshot.Empty;
            }

            string fullGameDirectory = Path.GetFullPath(gameDirectory);
            return new MediaCatalogSnapshot(
                fullGameDirectory,
                BuildAudioItems(fullGameDirectory),
                BuildVideoItems(fullGameDirectory));
        }

        public static bool LooksLikeGameDirectory(string? gameDirectory)
        {
            return AppConfig.InspectGameDirectory(gameDirectory).Status == GameDirectoryStatus.FullInstall;
        }

        public static string GetMainVideoDisplayName(string videoStem)
        {
            return MainVideoDescriptions.GetValueOrDefault(videoStem, videoStem);
        }

        private static IReadOnlyList<MediaAudioItem> BuildAudioItems(string gameDirectory)
        {
            List<MediaAudioItem> items = new();

            string musicDirectory = Path.Combine(gameDirectory, "data", "Music");
            if (Directory.Exists(musicDirectory))
            {
                foreach (string file in Directory.GetFiles(musicDirectory, "*.ogg").OrderBy(static path => path, StringComparer.OrdinalIgnoreCase))
                {
                    items.Add(new MediaAudioItem(
                        NormalizeMusicName(file),
                        file,
                        "Music",
                        0,
                        TryGetOggDurationLabel(file)));
                }
            }

            string voiceDirectory = Path.Combine(gameDirectory, "data", "sounds", "english", "MessageBox");
            if (Directory.Exists(voiceDirectory))
            {
                foreach (string file in Directory.GetFiles(voiceDirectory, "*.ogg").OrderBy(static path => path, StringComparer.OrdinalIgnoreCase))
                {
                    string baseName = Path.GetFileNameWithoutExtension(file);
                    string groupName = GetVoiceGroupName(baseName);
                    items.Add(new MediaAudioItem(
                        baseName,
                        file,
                        groupName,
                        GetVoiceGroupSortOrder(groupName),
                        TryGetOggDurationLabel(file)));
                }
            }

            return items
                .OrderBy(static item => item.GroupSortOrder)
                .ThenBy(static item => item.GroupName, StringComparer.OrdinalIgnoreCase)
                .ThenBy(static item => item.Name, StringComparer.OrdinalIgnoreCase)
                .ToList();
        }

        private static IReadOnlyList<MediaVideoItem> BuildVideoItems(string gameDirectory)
        {
            List<MediaVideoItem> items = new();
            HashSet<string> addedPaths = new(StringComparer.OrdinalIgnoreCase);
            HashSet<string> addedCutsceneNumbers = new(StringComparer.OrdinalIgnoreCase);
            HashSet<string> addedBriefingMissions = new(StringComparer.OrdinalIgnoreCase);

            string videoDirectory = Path.Combine(gameDirectory, "data", "video");
            if (!Directory.Exists(videoDirectory))
            {
                return items;
            }

            foreach (string file in Directory.GetFiles(videoDirectory, "*.vid").OrderBy(static path => path, StringComparer.OrdinalIgnoreCase))
            {
                string baseName = Path.GetFileNameWithoutExtension(file);
                if ((baseName.Length == 2 && int.TryParse(baseName, out _)) ||
                    (baseName.StartsWith("PC_", StringComparison.OrdinalIgnoreCase) && baseName.EndsWith("_exact", StringComparison.OrdinalIgnoreCase)))
                {
                    continue;
                }

                if (addedPaths.Add(file))
                {
                    items.Add(CreateVideoItem(
                        file,
                        GetMainVideoDisplayName(baseName),
                        "Main Videos",
                        0));
                }
            }

            string cutsceneDirectory = Path.Combine(videoDirectory, "cutscenes");
            if (Directory.Exists(cutsceneDirectory))
            {
                foreach (string file in Directory.GetFiles(cutsceneDirectory, "*.vid").OrderBy(GetCutsceneSortKey))
                {
                    AddCutscene(items, addedPaths, addedCutsceneNumbers, file);
                }
            }

            foreach (string file in Directory.GetFiles(videoDirectory, "*.vid")
                .Where(static path =>
                {
                    string stem = Path.GetFileNameWithoutExtension(path);
                    return stem.Length == 2 && int.TryParse(stem, out _);
                })
                .OrderBy(static path => int.Parse(Path.GetFileNameWithoutExtension(path))))
            {
                AddCutscene(items, addedPaths, addedCutsceneNumbers, file);
            }

            Dictionary<string, List<(string FilePath, string Mission)>> briefingsByEpisode = new(StringComparer.OrdinalIgnoreCase);
            void AddBriefings(IEnumerable<string> files)
            {
                foreach (string file in files)
                {
                    if (!addedPaths.Add(file))
                    {
                        continue;
                    }

                    string fileName = Path.GetFileNameWithoutExtension(file);
                    Match match = Regex.Match(fileName, @"^PC_(?<mission>\d+)_exact$", RegexOptions.IgnoreCase);
                    if (!match.Success)
                    {
                        addedPaths.Remove(file);
                        continue;
                    }

                    string mission = match.Groups["mission"].Value;
                    if (!addedBriefingMissions.Add(mission))
                    {
                        addedPaths.Remove(file);
                        continue;
                    }

                    string episode = mission[0].ToString();
                    if (!briefingsByEpisode.TryGetValue(episode, out List<(string FilePath, string Mission)>? existing))
                    {
                        existing = new List<(string FilePath, string Mission)>();
                        briefingsByEpisode[episode] = existing;
                    }

                    existing.Add((file, mission));
                }
            }

            string briefingsDirectory = Path.Combine(videoDirectory, "briefings");
            if (Directory.Exists(briefingsDirectory))
            {
                AddBriefings(Directory.GetFiles(briefingsDirectory, "*.vid"));
            }

            AddBriefings(Directory.GetFiles(videoDirectory, "PC_*_exact.vid"));

            foreach ((string episode, List<(string FilePath, string Mission)> files) in briefingsByEpisode.OrderBy(static pair => pair.Key, StringComparer.OrdinalIgnoreCase))
            {
                foreach ((string filePath, string mission) in files.OrderBy(static entry => entry.Mission, StringComparer.OrdinalIgnoreCase))
                {
                    items.Add(CreateVideoItem(
                        filePath,
                        $"Mission {mission}",
                        $"Mission Briefings / Episode {episode}",
                        2000 + int.Parse(episode)));
                }
            }

            return items
                .OrderBy(static item => item.SectionSortOrder)
                .ThenBy(static item => item.SectionName, StringComparer.OrdinalIgnoreCase)
                .ThenBy(static item => item.Name, StringComparer.OrdinalIgnoreCase)
                .ToList();
        }

        private static void AddCutscene(
            List<MediaVideoItem> items,
            HashSet<string> addedPaths,
            HashSet<string> addedCutsceneNumbers,
            string file)
        {
            if (!addedPaths.Add(file))
            {
                return;
            }

            string number = Path.GetFileNameWithoutExtension(file);
            if (!addedCutsceneNumbers.Add(number))
            {
                addedPaths.Remove(file);
                return;
            }

            items.Add(CreateVideoItem(file, $"Cutscene {number}", "Cutscenes", 1000));
        }

        private static string NormalizeMusicName(string filePath)
        {
            return Path.GetFileNameWithoutExtension(filePath)
                .Replace(" (Master)", string.Empty, StringComparison.Ordinal)
                .Replace("_", " ", StringComparison.Ordinal);
        }

        private static string GetVoiceGroupName(string fileName)
        {
            string upper = fileName.ToUpperInvariant();
            if (upper.StartsWith("TUTORIAL", StringComparison.Ordinal))
            {
                return "Tutorial";
            }

            if (upper.StartsWith("RACING", StringComparison.Ordinal))
            {
                return "Racing";
            }

            if (upper.StartsWith("HEALTH_", StringComparison.Ordinal) ||
                upper.StartsWith("UNDER_", StringComparison.Ordinal) ||
                upper.StartsWith("BASE_", StringComparison.Ordinal) ||
                upper.StartsWith("NEED_", StringComparison.Ordinal))
            {
                return "Status Messages";
            }

            string prefix = fileName.Split('_')[0];
            if (int.TryParse(prefix, out int missionNumber))
            {
                return $"Mission {missionNumber}";
            }

            return "Other";
        }

        private static int GetVoiceGroupSortOrder(string groupName)
        {
            if (groupName.StartsWith("Mission ", StringComparison.OrdinalIgnoreCase) &&
                int.TryParse(groupName.Replace("Mission ", string.Empty, StringComparison.OrdinalIgnoreCase), out int missionNumber))
            {
                return missionNumber;
            }

            return groupName switch
            {
                "Tutorial" => 10000,
                "Racing" => 10001,
                "Status Messages" => 10002,
                "Other" => 99999,
                _ => 50000
            };
        }

        private static string TryGetOggDurationLabel(string filePath)
        {
            try
            {
                // Own the stream outside VorbisWaveReader so a constructor failure
                // cannot strand the library's internally opened file handle.
                using FileStream stream = new(
                    filePath,
                    FileMode.Open,
                    FileAccess.Read,
                    FileShare.Read);
                using VorbisWaveReader reader = new(stream, closeOnDispose: false);
                return reader.TotalTime.TotalSeconds <= 0
                    ? string.Empty
                    : FormatDuration(reader.TotalTime);
            }
            catch
            {
                return string.Empty;
            }
        }

        private static string FormatDuration(TimeSpan duration)
        {
            return $"{(int)duration.TotalMinutes}:{duration.Seconds:D2}";
        }

        private static MediaVideoItem CreateVideoItem(string filePath, string name, string sectionName, int sectionSortOrder)
        {
            FileInfo info = new(filePath);
            return new MediaVideoItem(
                name,
                filePath,
                sectionName,
                sectionSortOrder,
                FormatFileSize(info.Exists ? info.Length : 0));
        }

        private static string FormatFileSize(long bytes)
        {
            if (bytes <= 0)
            {
                return string.Empty;
            }

            string[] sizes = ["B", "KB", "MB", "GB"];
            double length = bytes;
            int order = 0;
            while (length >= 1024 && order < sizes.Length - 1)
            {
                order++;
                length /= 1024;
            }

            return $"{length:0.#} {sizes[order]}";
        }

        private static int GetCutsceneSortKey(string path)
        {
            string stem = Path.GetFileNameWithoutExtension(path);
            return int.TryParse(stem, out int number) ? number : int.MaxValue;
        }
    }

    public sealed record MediaCatalogSnapshot(
        string GameDirectory,
        IReadOnlyList<MediaAudioItem> AudioItems,
        IReadOnlyList<MediaVideoItem> VideoItems)
    {
        public static MediaCatalogSnapshot Empty { get; } = new(string.Empty, Array.Empty<MediaAudioItem>(), Array.Empty<MediaVideoItem>());
    }

    public sealed record MediaAudioItem(
        string Name,
        string FilePath,
        string GroupName,
        int GroupSortOrder,
        string DurationLabel);

    public sealed record MediaVideoItem(
        string Name,
        string FilePath,
        string SectionName,
        int SectionSortOrder,
        string SizeText);
}
