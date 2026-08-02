using System;
using System.IO;
using System.Linq;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class MediaCatalogServiceTests
    {
        [Fact]
        public void LooksLikeGameDirectory_RequiresBeaExeAndDataFolder()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            string mediaOnly = Path.Combine(Path.GetTempPath(), "oce-media-tests", Guid.NewGuid().ToString("N"));
            string exeOnly = Path.Combine(Path.GetTempPath(), "oce-media-tests", Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(Path.Combine(mediaOnly, "data"));
                Directory.CreateDirectory(exeOnly);
                File.WriteAllText(Path.Combine(exeOnly, "BEA.exe"), string.Empty);

                Assert.True(MediaCatalogService.LooksLikeGameDirectory(temp.RootPath));
                Assert.False(MediaCatalogService.LooksLikeGameDirectory(Path.Combine(temp.RootPath, "data")));
                Assert.False(MediaCatalogService.LooksLikeGameDirectory(mediaOnly));
                Assert.False(MediaCatalogService.LooksLikeGameDirectory(exeOnly));
            }
            finally
            {
                if (Directory.Exists(mediaOnly))
                {
                    Directory.Delete(mediaOnly, recursive: true);
                }
                if (Directory.Exists(exeOnly))
                {
                    Directory.Delete(exeOnly, recursive: true);
                }
            }
        }

        [Fact]
        public void Load_BuildsExpectedAudioGroups()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            temp.WriteFile(@"data\Music\battle_theme (Master).ogg");
            temp.WriteFile(@"data\sounds\english\MessageBox\110_arrival.ogg");
            temp.WriteFile(@"data\sounds\english\MessageBox\TUTORIAL_intro.ogg");
            temp.WriteFile(@"data\sounds\english\MessageBox\HEALTH_low.ogg");

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            Assert.Equal(4, snapshot.AudioItems.Count);
            Assert.Contains(snapshot.AudioItems, item => item.Name == "battle theme" && item.GroupName == "Music");
            Assert.Contains(snapshot.AudioItems, item => item.Name == "110_arrival" && item.GroupName == "Mission 110");
            Assert.Contains(snapshot.AudioItems, item => item.Name == "TUTORIAL_intro" && item.GroupName == "Tutorial");
            Assert.Contains(snapshot.AudioItems, item => item.Name == "HEALTH_low" && item.GroupName == "Status Messages");
        }

        /// <summary>
        /// With the game's own text alongside it, a mission stops being a number.
        ///
        /// "Mission 110" was never a name the game uses - it was the app reading a filename out
        /// loud. The real one is in `data/language/&lt;language&gt;.dat`, which every installation
        /// carries in six languages, so the app can call a mission what the player's own game calls
        /// it rather than shipping an English table.
        /// </summary>
        [Fact]
        public void Load_UsesTheGamesOwnMissionNamesWhenTheLanguageFileIsThere()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            temp.WriteFile(@"data\sounds\english\MessageBox\110_arrival.ogg");
            temp.WriteFile(@"data\sounds\english\MessageBox\211_go.ogg");
            WriteLanguageFile(temp, ("1.10 - Blackout", null), ("2.11 - Assault On Apollo", null));

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            Assert.Contains(snapshot.AudioItems, item => item.GroupName == "1.10 - Blackout");
            Assert.Contains(snapshot.AudioItems, item => item.GroupName == "2.11 - Assault On Apollo");
            Assert.DoesNotContain(snapshot.AudioItems, item => item.GroupName.StartsWith("Mission ", StringComparison.Ordinal));
        }

        /// <summary>
        /// Story order is what makes the list readable, and it used to be recovered by parsing the
        /// digits back out of "Mission 211". Now that the heading is a name, the order has to come
        /// from the number directly - so 1.10 must still sort above 2.11 even though "2" &lt; "B".
        /// </summary>
        [Fact]
        public void Load_KeepsMissionsInStoryOrderOnceTheyHaveNames()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            temp.WriteFile(@"data\sounds\english\MessageBox\211_go.ogg");
            temp.WriteFile(@"data\sounds\english\MessageBox\110_arrival.ogg");
            WriteLanguageFile(temp, ("1.10 - Blackout", null), ("2.11 - Assault On Apollo", null));

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            MediaAudioItem first = snapshot.AudioItems.First();
            Assert.Equal("1.10 - Blackout", first.GroupName);
            Assert.True(
                snapshot.AudioItems.First(item => item.GroupName.StartsWith("1.10", StringComparison.Ordinal)).GroupSortOrder <
                snapshot.AudioItems.First(item => item.GroupName.StartsWith("2.11", StringComparison.Ordinal)).GroupSortOrder);
        }

        /// <summary>
        /// A language file the app cannot read is an ordinary outcome - a different build, a
        /// different region, a partial install - and it must cost the player nothing but the nicer
        /// label.
        /// </summary>
        [Fact]
        public void Load_FallsBackToFilenameLabelsWhenTheLanguageFileIsUnreadable()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            temp.WriteFile(@"data\sounds\english\MessageBox\110_arrival.ogg");
            string unreadable = Path.Combine(temp.RootPath, "data", "language", "english.dat");
            Directory.CreateDirectory(Path.GetDirectoryName(unreadable)!);
            File.WriteAllText(unreadable, "this is not a language table");

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            Assert.Contains(snapshot.AudioItems, item => item.GroupName == "Mission 110");
        }

        /// <summary>
        /// A mission the language file has no name for keeps its number rather than losing its
        /// heading. Retail has 43 named levels; the voice folder has lines that do not all map.
        /// </summary>
        [Fact]
        public void Load_KeepsTheNumberForAMissionTheGameDoesNotName()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            temp.WriteFile(@"data\sounds\english\MessageBox\110_arrival.ogg");
            temp.WriteFile(@"data\sounds\english\MessageBox\999_unknown.ogg");
            WriteLanguageFile(temp, ("1.10 - Blackout", null));

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            Assert.Contains(snapshot.AudioItems, item => item.GroupName == "1.10 - Blackout");
            Assert.Contains(snapshot.AudioItems, item => item.GroupName == "Mission 999");
        }

        /// <summary>
        /// The whole point, against a real installation: the voice lines group under the names the
        /// game itself uses.
        ///
        /// Returns early on a machine with no game, like the other retail-dependent cases. Where
        /// there is one, this is the test that would catch the join breaking - the decoder can be
        /// perfect and the Media page still show numbers if the mission-number mapping drifts.
        /// </summary>
        [Fact]
        public void Load_GroupsRealVoiceLinesUnderTheGamesOwnMissionNames()
        {
            string? gameDirectory = AppConfig.Load().GetGameDir() ?? AppConfig.DetectGameDirectory();
            if (gameDirectory is null || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
            {
                return;
            }

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(gameDirectory);
            if (snapshot.AudioItems.Count == 0)
            {
                return;
            }

            string[] groups = snapshot.AudioItems
                .Select(item => item.GroupName)
                .Distinct(StringComparer.Ordinal)
                .ToArray();

            Assert.Contains(groups, group => group.Contains(" - ", StringComparison.Ordinal) &&
                                             char.IsAsciiDigit(group[0]));
            Assert.DoesNotContain(groups, group => group.StartsWith("Mission 1", StringComparison.Ordinal));
        }

        /// <summary>
        /// The words come from the game, joined to the recording by the audio name the text table
        /// stores beside every spoken string - which is the .ogg's own filename.
        /// </summary>
        [Fact]
        public void Load_AttachesWhatEachVoiceLineActuallySays()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            temp.WriteFile(@"data\sounds\english\MessageBox\512_TATIANA_NEW_1.ogg");
            temp.WriteFile(@"data\sounds\english\MessageBox\110_arrival.ogg");
            WriteLanguageFile(
                temp,
                ("Hawk, Billy! What are you two doing?", "512_TATIANA_NEW_1"),
                ("A line with no recording", null));

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            MediaAudioItem spoken = snapshot.AudioItems.Single(item => item.Name == "512_TATIANA_NEW_1");
            Assert.Equal("Hawk, Billy! What are you two doing?", spoken.Transcript);

            // A recording the table has no line for keeps a null rather than an invented one.
            Assert.Null(snapshot.AudioItems.Single(item => item.Name == "110_arrival").Transcript);
        }

        [Fact]
        public void Load_LeavesTranscriptsNullWhenTheGameTextCannotBeRead()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            temp.WriteFile(@"data\sounds\english\MessageBox\512_TATIANA_NEW_1.ogg");

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            Assert.All(snapshot.AudioItems, item => Assert.Null(item.Transcript));
        }

        /// <summary>
        /// The claim this feature rests on, against retail bytes: measured 2026-08-01, all 607
        /// audio-bearing entries in the English table resolve to a file that exists. If that join
        /// ever degrades, the Media page quietly stops showing what half its clips say.
        /// </summary>
        [Fact]
        public void Load_JoinsTheGamesOwnVoiceLinesToTheirRecordings()
        {
            string? gameDirectory = AppConfig.Load().GetGameDir() ?? AppConfig.DetectGameDirectory();
            if (gameDirectory is null || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
            {
                return;
            }

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(gameDirectory);
            if (snapshot.AudioItems.Count == 0)
            {
                return;
            }

            int withWords = snapshot.AudioItems.Count(item => !string.IsNullOrWhiteSpace(item.Transcript));

            Assert.True(withWords > 500, $"Expected most voice lines to carry their words; got {withWords}.");
        }

        private static void WriteLanguageFile(TempGameDirectory temp, params (string Text, string? Audio)[] entries)
        {
            string path = Path.Combine(temp.RootPath, "data", "language", "english.dat");
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, TestLanguageFile.Build(entries));
        }

        [Fact]
        public void Load_InvalidOgg_ReleasesTheCatalogFileHandle()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            string filePath = temp.WriteFile(@"data\Music\invalid.ogg");

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            Assert.Single(snapshot.AudioItems);
            using FileStream exclusive = new(
                filePath,
                FileMode.Open,
                FileAccess.ReadWrite,
                FileShare.None);
            Assert.True(exclusive.CanRead);
        }

        [Fact]
        public void Load_BuildsExpectedVideoSectionsWithoutDuplicates()
        {
            using TempGameDirectory temp = TempGameDirectory.Create();
            temp.WriteFile(@"data\video\OpeningFMV.vid");
            temp.WriteFile(@"data\video\02.vid");
            temp.WriteFile(@"data\video\cutscenes\03.vid");
            temp.WriteFile(@"data\video\briefings\PC_101_exact.vid");
            temp.WriteFile(@"data\video\PC_101_exact.vid");

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);

            Assert.Contains(snapshot.VideoItems, item => item.Name == "Opening Cinematic" && item.SectionName == "Main Videos");
            Assert.Contains(snapshot.VideoItems, item => item.Name == "Cutscene 02" && item.SectionName == "Cutscenes");
            Assert.Contains(snapshot.VideoItems, item => item.Name == "Cutscene 03" && item.SectionName == "Cutscenes");

            MediaVideoItem briefing = Assert.Single(snapshot.VideoItems, item => item.Name == "Mission 101");
            Assert.Equal("Mission Briefings / Episode 1", briefing.SectionName);
        }

        [Fact]
        public void Cutscenes_AreNamedByNumberOnly_BecauseTheGameShipsNoTitlesForThem()
        {
            // Regression guard for a real honesty defect: this service used to
            // carry 33 invented story titles ("Tatiana Introduction",
            // "Boss Battle", "Plot Twist", ...) that exist nowhere in the game,
            // the lore library, or the evidence store, and presented them to
            // users as fact. A cutscene may only be labelled by its number
            // until a real title is demonstrated.
            using TempGameDirectory temp = TempGameDirectory.Create();
            foreach (string number in new[] { "01", "04", "15", "17", "33" })
            {
                temp.WriteFile($@"data\video\cutscenes\{number}.vid");
            }

            MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(temp.RootPath);
            IReadOnlyList<MediaVideoItem> cutscenes = snapshot.VideoItems
                .Where(item => item.SectionName == "Cutscenes")
                .ToList();

            Assert.Equal(5, cutscenes.Count);
            Assert.All(cutscenes, item => Assert.Matches(@"^Cutscene \d{2}$", item.Name));
        }

        [Fact]
        public void GetMainVideoDisplayName_ExpandsOnlyAbbreviationsCarriedByTheFileName()
        {
            // Each mapped name expands an abbreviation the file itself carries,
            // so the file name is the evidence: LT = Lost Toys, FE = front end,
            // TWIMTBP = NVIDIA's "The Way It's Meant To Be Played".
            Assert.Equal("Lost Toys Logo", MediaCatalogService.GetMainVideoDisplayName("LTLogo"));
            Assert.Equal("NVIDIA Logo", MediaCatalogService.GetMainVideoDisplayName("TWIMTBP_GefFX_640x480_Audio"));

            // "UsTheMovie" -> "Credits Video" is the one mapping that reads a
            // ROLE into the file rather than expanding its name. It is retained
            // for now because it is wired into receipt-bound evidence
            // acceptance; confirm it by watching the video before relying on it.
            Assert.Equal("Credits Video", MediaCatalogService.GetMainVideoDisplayName("UsTheMovie"));

            // Anything unmapped falls back to the raw stem rather than a guess.
            Assert.Equal("UnknownCutscene", MediaCatalogService.GetMainVideoDisplayName("UnknownCutscene"));
        }

        private sealed class TempGameDirectory : IDisposable
        {
            public string RootPath { get; }

            private TempGameDirectory(string rootPath)
            {
                RootPath = rootPath;
            }

            public static TempGameDirectory Create()
            {
                string rootPath = Path.Combine(Path.GetTempPath(), "oce-media-tests", Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(rootPath);
                File.WriteAllText(Path.Combine(rootPath, "BEA.exe"), string.Empty);
                Directory.CreateDirectory(Path.Combine(rootPath, "data"));
                return new TempGameDirectory(rootPath);
            }

            public string WriteFile(string relativePath)
            {
                string fullPath = Path.Combine(RootPath, relativePath);
                string? directory = Path.GetDirectoryName(fullPath);
                if (!string.IsNullOrWhiteSpace(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                File.WriteAllText(fullPath, string.Empty);
                return fullPath;
            }

            public void Dispose()
            {
                try
                {
                    if (Directory.Exists(RootPath))
                    {
                        Directory.Delete(RootPath, recursive: true);
                    }
                }
                catch
                {
                    // Best effort test cleanup only.
                }
            }
        }
    }
}
