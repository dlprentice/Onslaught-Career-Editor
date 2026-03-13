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

            Assert.True(MediaCatalogService.LooksLikeGameDirectory(temp.RootPath));
            Assert.False(MediaCatalogService.LooksLikeGameDirectory(Path.Combine(temp.RootPath, "data")));
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
            Assert.Contains(snapshot.VideoItems, item => item.Name == "02 - Mission Briefing 1" && item.SectionName == "Cutscenes");
            Assert.Contains(snapshot.VideoItems, item => item.Name == "03 - Battle Aftermath" && item.SectionName == "Cutscenes");

            MediaVideoItem briefing = Assert.Single(snapshot.VideoItems, item => item.Name == "Mission 101");
            Assert.Equal("Mission Briefings / Episode 1", briefing.SectionName);
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

            public void WriteFile(string relativePath)
            {
                string fullPath = Path.Combine(RootPath, relativePath);
                string? directory = Path.GetDirectoryName(fullPath);
                if (!string.IsNullOrWhiteSpace(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                File.WriteAllText(fullPath, string.Empty);
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
