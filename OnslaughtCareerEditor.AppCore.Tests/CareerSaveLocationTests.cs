using System;
using System.IO;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Save Lab used to show only a path. That hid the only fact a person needs before they
    /// write: is this career sitting in the installed game, in a playable copy this app made,
    /// or in a folder they chose? Classification is layout only and never writes.
    /// </summary>
    public sealed class CareerSaveLocationTests
    {
        [Fact]
        public void MissingPathIsMissing()
        {
            Assert.Equal(CareerSaveLocationKind.Missing, CareerSaveLocation.Classify(null));
            Assert.Equal(CareerSaveLocationKind.Missing, CareerSaveLocation.Classify("   "));
            Assert.Equal(
                CareerSaveLocationKind.Missing,
                CareerSaveLocation.Classify(Path.Combine(Path.GetTempPath(), $"absent-{Guid.NewGuid():N}.bes")));
        }

        [Fact]
        public void ASaveUnderBeaExeAndDataIsTheInstalledGame()
        {
            using var lab = new LocationLab();
            lab.MakeInstalledGame();
            string save = lab.WriteSave("savegames", "career.bes");

            Assert.Equal(CareerSaveLocationKind.InstalledGame, CareerSaveLocation.Classify(save));
        }

        [Fact]
        public void ASaveUnderAProfileManifestIsASafeCopyEvenThoughTheCopyAlsoHasBeaExe()
        {
            using var lab = new LocationLab();
            lab.MakeInstalledGame();
            lab.WriteFile(GameProfilePreflightService.ProfileManifestFileName, "{}");
            string save = lab.WriteSave("savegames", "career.bes");

            Assert.Equal(CareerSaveLocationKind.SafeCopy, CareerSaveLocation.Classify(save));
        }

        [Fact]
        public void ASaveInAnOrdinaryFolderIsAChosenFolder()
        {
            using var lab = new LocationLab();
            string save = lab.WriteSave("Documents", "career.bes");

            Assert.Equal(CareerSaveLocationKind.ChosenFolder, CareerSaveLocation.Classify(save));
        }

        [Fact]
        public void SafeCopyWinsOverANestedInstalledLayout()
        {
            using var lab = new LocationLab();
            lab.WriteFile(GameProfilePreflightService.ProfileManifestFileName, "{}");
            Directory.CreateDirectory(Path.Combine(lab.Root, "nested", "data"));
            File.WriteAllBytes(Path.Combine(lab.Root, "nested", "BEA.exe"), new byte[16]);
            string save = Path.Combine(lab.Root, "nested", "savegames", "career.bes");
            Directory.CreateDirectory(Path.GetDirectoryName(save)!);
            File.WriteAllBytes(save, new byte[16]);

            Assert.Equal(CareerSaveLocationKind.SafeCopy, CareerSaveLocation.Classify(save));
        }

        [Fact]
        public void ADirectoryIsClassifiedTheSameWayAsAFileInsideIt()
        {
            using var lab = new LocationLab();
            lab.MakeInstalledGame();
            string installedSave = lab.WriteSave("savegames", "career.bes");
            Assert.Equal(
                CareerSaveLocationKind.InstalledGame,
                CareerSaveLocation.Classify(Path.GetDirectoryName(installedSave)));

            using var copy = new LocationLab();
            copy.MakeInstalledGame();
            copy.WriteFile(GameProfilePreflightService.ProfileManifestFileName, "{}");
            string copySave = copy.WriteSave("savegames", "career.bes");
            Assert.Equal(
                CareerSaveLocationKind.SafeCopy,
                CareerSaveLocation.Classify(Path.GetDirectoryName(copySave)));

            using var chosen = new LocationLab();
            string chosenSave = chosen.WriteSave("Documents", "career.bes");
            Assert.Equal(
                CareerSaveLocationKind.ChosenFolder,
                CareerSaveLocation.Classify(Path.GetDirectoryName(chosenSave)));
        }

        private sealed class LocationLab : IDisposable
        {
            public LocationLab()
            {
                Root = Path.Combine(Path.GetTempPath(), $"bea-save-loc-{Guid.NewGuid():N}");
                Directory.CreateDirectory(Root);
            }

            public string Root { get; }

            public void MakeInstalledGame()
            {
                Directory.CreateDirectory(Path.Combine(Root, "data"));
                File.WriteAllBytes(Path.Combine(Root, "BEA.exe"), new byte[16]);
            }

            public void WriteFile(string relativePath, string contents)
            {
                string path = Path.Combine(Root, relativePath);
                Directory.CreateDirectory(Path.GetDirectoryName(path)!);
                File.WriteAllText(path, contents);
            }

            public string WriteSave(string folder, string fileName)
            {
                string dir = Path.Combine(Root, folder);
                Directory.CreateDirectory(dir);
                string path = Path.Combine(dir, fileName);
                File.WriteAllBytes(path, new byte[16]);
                return path;
            }

            public void Dispose()
            {
                try
                {
                    if (Directory.Exists(Root))
                        Directory.Delete(Root, recursive: true);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                {
                }
            }
        }
    }
}
