using NAudio.Vorbis;
using System.Text.RegularExpressions;

namespace OnslaughtCareerEditor.AppCore
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

            // The game knows what its own missions are called. Read that once here rather than in
            // the two builders, so a single unreadable language file degrades to filename labels
            // everywhere at once instead of half the page.
            MissionNames missionNames = MissionNames.Load(fullGameDirectory);
            VoiceTranscripts transcripts = VoiceTranscripts.Load(fullGameDirectory);

            return new MediaCatalogSnapshot(
                fullGameDirectory,
                BuildAudioItems(fullGameDirectory, missionNames, transcripts),
                BuildVideoItems(fullGameDirectory, missionNames));
        }

        /// <summary>
        /// The mission names the game itself shows, keyed by the three-digit number its filenames
        /// use.
        ///
        /// Everything is optional. A player with no installation, a corrupt language file, or a
        /// build whose names this cannot parse gets exactly what the app showed before - "Mission
        /// 211" - because a label that says less is better than a page that fails to draw.
        /// </summary>
        private sealed class MissionNames
        {
            private static readonly MissionNames None = new(new Dictionary<string, GameLevelName>(StringComparer.Ordinal));

            private readonly Dictionary<string, GameLevelName> _byCode;

            private MissionNames(Dictionary<string, GameLevelName> byCode)
            {
                _byCode = byCode;
            }

            public static MissionNames Load(string gameDirectory)
            {
                try
                {
                    GameTextCatalog? catalog = GameTextCatalogService.TryLoadFromGameDirectory(gameDirectory);
                    IReadOnlyList<GameLevelName> names = GameTextCatalogService.GetLevelNames(catalog);
                    if (names.Count == 0)
                    {
                        return None;
                    }

                    Dictionary<string, GameLevelName> byCode = new(StringComparer.Ordinal);
                    foreach (GameLevelName name in names)
                    {
                        // The (Evo) rows share nothing with a voice-line filename, and the plain
                        // row is the one a player recognises, so first write wins.
                        byCode.TryAdd(name.Code, name);
                    }

                    return new MissionNames(byCode);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
                {
                    return None;
                }
            }

            /// <summary>The game's own label for a mission number, or null to fall back.</summary>
            public string? TryGetDisplay(int missionNumber)
            {
                string? code = GameTextCatalogService.TryGetLevelCodeForMissionNumber(missionNumber);
                if (code is null)
                {
                    return null;
                }

                return _byCode.TryGetValue(code, out GameLevelName? name) ? name.Display : null;
            }
        }

        public static bool LooksLikeGameDirectory(string? gameDirectory)
        {
            return AppConfig.InspectGameDirectory(gameDirectory).Status == GameDirectoryStatus.FullInstall;
        }

        public static string GetMainVideoDisplayName(string videoStem)
        {
            return MainVideoDescriptions.GetValueOrDefault(videoStem, videoStem);
        }

        private static IReadOnlyList<MediaAudioItem> BuildAudioItems(
            string gameDirectory,
            MissionNames missionNames,
            VoiceTranscripts transcripts)
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
                    (string groupName, int groupSortOrder) = GetVoiceGroup(baseName, missionNames);
                    items.Add(new MediaAudioItem(
                        baseName,
                        file,
                        groupName,
                        groupSortOrder,
                        TryGetOggDurationLabel(file),
                        transcripts.TryGetLine(baseName)));
                }
            }

            return items
                .OrderBy(static item => item.GroupSortOrder)
                .ThenBy(static item => item.GroupName, StringComparer.OrdinalIgnoreCase)
                .ThenBy(static item => item.Name, StringComparer.OrdinalIgnoreCase)
                .ToList();
        }

        /// <summary>
        /// What each voice line says, from the game's own text table.
        ///
        /// The table stores an audio name beside every spoken string, and that name is the .ogg's
        /// filename - so a line and its recording can be put back together without guessing.
        /// Measured against the retail English table on 2026-08-01: 607 of 607 audio-bearing
        /// entries resolve to a file that exists on disk.
        ///
        /// Optional, like the mission names. No installation, an unreadable table, or a build
        /// whose names do not match all end as "no transcript", never as a page that will not
        /// draw.
        /// </summary>
        private sealed class VoiceTranscripts
        {
            private static readonly VoiceTranscripts None = new(new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase));

            private readonly Dictionary<string, string> _byAudioName;

            private VoiceTranscripts(Dictionary<string, string> byAudioName)
            {
                _byAudioName = byAudioName;
            }

            public static VoiceTranscripts Load(string gameDirectory)
            {
                try
                {
                    GameTextCatalog? catalog = GameTextCatalogService.TryLoadFromGameDirectory(gameDirectory);
                    if (catalog is null)
                    {
                        return None;
                    }

                    Dictionary<string, string> byAudioName = new(StringComparer.OrdinalIgnoreCase);
                    foreach (GameTextEntry entry in catalog.Entries)
                    {
                        if (string.IsNullOrWhiteSpace(entry.AudioName) || string.IsNullOrWhiteSpace(entry.Text))
                        {
                            continue;
                        }

                        // First write wins: a handful of names carry more than one string, and the
                        // first is the one the table lists against the recording.
                        byAudioName.TryAdd(entry.AudioName, entry.Text.Trim());
                    }

                    return byAudioName.Count == 0 ? None : new VoiceTranscripts(byAudioName);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
                {
                    return None;
                }
            }

            public string? TryGetLine(string audioFileStem)
            {
                return _byAudioName.TryGetValue(audioFileStem, out string? line) ? line : null;
            }
        }

        private static IReadOnlyList<MediaVideoItem> BuildVideoItems(string gameDirectory, MissionNames missionNames)
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
                    string briefingName = int.TryParse(mission, out int missionNumber)
                        ? missionNames.TryGetDisplay(missionNumber) ?? $"Mission {mission}"
                        : $"Mission {mission}";

                    items.Add(CreateVideoItem(
                        filePath,
                        briefingName,
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

        /// <summary>
        /// Which heading a voice line sits under, and where that heading sorts.
        ///
        /// The two used to be derived separately, with the sort order recovered by parsing the
        /// digits back out of "Mission 211". That worked only while the heading was a number in
        /// disguise; now that a heading can read "2.11 - Assault On Apollo", the order travels with
        /// the name instead of being reconstructed from it.
        /// </summary>
        private static (string Name, int SortOrder) GetVoiceGroup(string fileName, MissionNames missionNames)
        {
            string upper = fileName.ToUpperInvariant();
            if (upper.StartsWith("TUTORIAL", StringComparison.Ordinal))
            {
                return ("Tutorial", 10000);
            }

            if (upper.StartsWith("RACING", StringComparison.Ordinal))
            {
                return ("Racing", 10001);
            }

            if (upper.StartsWith("HEALTH_", StringComparison.Ordinal) ||
                upper.StartsWith("UNDER_", StringComparison.Ordinal) ||
                upper.StartsWith("BASE_", StringComparison.Ordinal) ||
                upper.StartsWith("NEED_", StringComparison.Ordinal))
            {
                return ("Status Messages", 10002);
            }

            string prefix = fileName.Split('_')[0];
            if (int.TryParse(prefix, out int missionNumber))
            {
                // Sorting stays on the number either way, so the missions keep their story order
                // whether or not the game's own names were readable.
                return (missionNames.TryGetDisplay(missionNumber) ?? $"Mission {missionNumber}", missionNumber);
            }

            return ("Other", 99999);
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

    /// <param name="Transcript">
    /// What is actually said, when the game's own text table has a line for this file, and null
    /// otherwise. The join is the audio name the text table stores beside each string, which is
    /// the .ogg's own filename - 607 of the 607 audio-bearing entries in the retail English table
    /// resolve to a file that exists.
    /// </param>
    public sealed record MediaAudioItem(
        string Name,
        string FilePath,
        string GroupName,
        int GroupSortOrder,
        string DurationLabel,
        string? Transcript = null);

    public sealed record MediaVideoItem(
        string Name,
        string FilePath,
        string SectionName,
        int SectionSortOrder,
        string SizeText);
}
