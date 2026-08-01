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
