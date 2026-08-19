using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The save-durability contract for safe copies.
    ///
    /// Before this suite existed, <c>DeleteGeneratedProfile</c> was a recursive delete of the whole
    /// copy folder and the careers a player had built inside it went with it, with no warning and
    /// no way to get them back. Everything else in a copy is a duplicate of the installed game and
    /// can be made again; the saves cannot. So the tests here are mostly about what must NOT
    /// happen, and the important ones are the orderings: a failed rescue must leave the copy
    /// standing, and a delete must refuse rather than take a career with it.
    /// </summary>
    public sealed class SafeCopySaveRescueTests
    {
        private const string SaveBytesMarker = "career-save-fixture";

        [Fact]
        public void Inventory_FindsCareerSavesInSavegamesAndAtTheCopyRoot()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-a");
            lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));
            lab.WriteSave(copy, Path.Combine("savegames", "Second.bes"));
            lab.WriteSave(copy, "StrayAtTheRoot.bes");

            SafeCopySaveInventory inventory = SafeCopySaveRescueService.Inventory(copy, lab.ProfilesRoot);

            Assert.True(inventory.HasSaves);
            Assert.Equal(
                new[] { "Maladim.bes", "Second.bes", "StrayAtTheRoot.bes" },
                inventory.Saves.Select(save => save.FileName).OrderBy(name => name, StringComparer.Ordinal));
            Assert.Equal("copy-a", inventory.DisplayName);
            Assert.All(inventory.Saves, save => Assert.True(save.Length > 0));
        }

        [Fact]
        public void Inventory_IgnoresTheShippedOptionsFileSoTheWarningStillMeansSomething()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-options");

            // Every copy of the game has this file at its root. If it counted as a save, every
            // delete would raise the warning and the warning would stop being read.
            File.WriteAllBytes(Path.Combine(copy, "defaultoptions.bea"), new byte[10004]);

            SafeCopySaveInventory inventory = SafeCopySaveRescueService.Inventory(copy, lab.ProfilesRoot);

            Assert.False(inventory.HasSaves);
            Assert.Null(SafeCopySaveRescueService.DescribeSavesAtRisk(inventory));
        }

        [Fact]
        public void Inventory_RefusesAFolderOutsideTheAppOwnedRoot()
        {
            using var lab = new SafeCopyLab();
            string outside = Path.Combine(lab.Root, "outside");
            Directory.CreateDirectory(outside);
            File.WriteAllText(
                Path.Combine(outside, GameProfilePreflightService.ProfileManifestFileName),
                "{}");

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(
                () => SafeCopySaveRescueService.Inventory(outside, lab.ProfilesRoot));
            Assert.Contains("outside the app-owned", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void Inventory_RefusesAFolderThisAppDidNotGenerate()
        {
            using var lab = new SafeCopyLab();
            string stranger = Path.Combine(lab.ProfilesRoot, "not-ours");
            Directory.CreateDirectory(stranger);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(
                () => SafeCopySaveRescueService.Inventory(stranger, lab.ProfilesRoot));
            Assert.Contains(GameProfilePreflightService.ProfileManifestFileName, error.Message);
        }

        [Fact]
        public void DescribeSavesAtRisk_NamesTheCareersRatherThanSayingDataMayBeLost()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-named");
            lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));

            string? described = SafeCopySaveRescueService.DescribeSavesAtRisk(
                SafeCopySaveRescueService.Inventory(copy, lab.ProfilesRoot));

            Assert.NotNull(described);
            Assert.Contains("Maladim", described);
            Assert.Contains("1 career save", described);
            Assert.Contains("copy-named", described);
        }

        [Fact]
        public void DescribeSavesAtRisk_CountsTheRestRatherThanListingAWallOfNames()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-many");
            foreach (int index in Enumerable.Range(1, 6))
                lab.WriteSave(copy, Path.Combine("savegames", $"Career{index}.bes"));

            string described = SafeCopySaveRescueService.DescribeSavesAtRisk(
                SafeCopySaveRescueService.Inventory(copy, lab.ProfilesRoot))!;

            Assert.Contains("6 career saves", described);
            Assert.Contains("and 3 more", described);
        }

        // ---------------------------------------------------------------- delete

        [Fact]
        public void DeleteGeneratedProfile_RefusesWhileACareerSaveIsStillInside()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-with-career");
            string save = lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));

            // Superseded 2026-08-01: this call used to delete the folder and the career with it,
            // reported success, and told nobody. The old behaviour is what this asserts against.
            InvalidOperationException error = Assert.Throws<InvalidOperationException>(
                () => GameProfilePreflightService.DeleteGeneratedProfile(copy, lab.ProfilesRoot));

            Assert.Contains("Maladim", error.Message);
            Assert.True(File.Exists(save), "The save must still be there after a refused delete.");
            Assert.True(Directory.Exists(copy), "The copy must still be there after a refused delete.");
        }

        [Fact]
        public void DeleteGeneratedProfile_StillRemovesACopyThatIsHoldingNothing()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-empty");

            string deleted = GameProfilePreflightService.DeleteGeneratedProfile(copy, lab.ProfilesRoot);

            Assert.False(Directory.Exists(copy));
            Assert.Equal(Path.GetFullPath(copy), Path.GetFullPath(deleted));
        }

        [Fact]
        public void DeleteGeneratedProfile_AMissingCopyFolderNamesTheFolderNotAPath()
        {
            using var lab = new SafeCopyLab();
            string missing = Path.Combine(lab.ProfilesRoot, "gone-copy");

            DirectoryNotFoundException error = Assert.Throws<DirectoryNotFoundException>(
                () => GameProfilePreflightService.DeleteGeneratedProfile(missing, lab.ProfilesRoot));

            Assert.Equal(GameProfilePreflightService.CopyFolderMissing, error.Message);
            Assert.DoesNotContain(missing, error.Message);
            Assert.DoesNotContain(lab.Root, error.Message);
            Assert.DoesNotContain(":\\", error.Message);
        }

        [Fact]
        public void DeleteGeneratedProfile_TakesTheSavesOnlyWhenTheCallerSaysSoExplicitly()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-discard");
            lab.WriteSave(copy, Path.Combine("savegames", "Doomed.bes"));

            GameProfilePreflightService.DeleteGeneratedProfile(
                copy,
                lab.ProfilesRoot,
                SafeCopySaveDisposition.DiscardSaves);

            Assert.False(Directory.Exists(copy));
        }

        // ---------------------------------------------------------------- rescue

        [Fact]
        public void Rescue_BringsSavesOutByteForByteAndLeavesTheOriginalsAlone()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-rescue");
            string first = lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));
            string second = lab.WriteSave(copy, Path.Combine("savegames", "Other.bes"));
            string keep = Path.Combine(lab.Root, "kept-saves");

            SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest { ProfileRoot = copy, DestinationDirectory = keep },
                lab.ProfilesRoot);

            Assert.True(result.Success, result.Message);
            Assert.Equal(2, result.RescuedCount);
            Assert.Empty(result.Failures);

            foreach (string source in new[] { first, second })
            {
                string landed = Path.Combine(keep, Path.GetFileName(source));
                Assert.True(File.Exists(landed), $"{Path.GetFileName(source)} should have been kept.");
                Assert.Equal(Sha256(source), Sha256(landed));
                Assert.True(File.Exists(source), "Rescue must copy, never move - the copy is still playable.");
            }
        }

        [Fact]
        public void Rescue_RefusesToKeepSavesInsideTheCopyThatIsAboutToGo()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-self");
            lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));

            SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest
                {
                    ProfileRoot = copy,
                    DestinationDirectory = Path.Combine(copy, "backup"),
                },
                lab.ProfilesRoot);

            Assert.False(result.Success);
            Assert.Contains("outside the copy", result.Message);
        }

        [Fact]
        public void Rescue_AsksBeforeReplacingASaveAlreadySittingInTheDestination()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-clash");
            lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"), "from the copy");
            string keep = Path.Combine(lab.Root, "kept-clash");
            Directory.CreateDirectory(keep);
            File.WriteAllText(Path.Combine(keep, "Maladim.bes"), "already here");

            SafeCopySaveRescueResult asked = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest { ProfileRoot = copy, DestinationDirectory = keep },
                lab.ProfilesRoot);

            Assert.False(asked.Success);
            Assert.True(asked.NeedsOverwriteConfirmation);
            Assert.Equal("already here", File.ReadAllText(Path.Combine(keep, "Maladim.bes")));

            SafeCopySaveRescueResult answered = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest
                {
                    ProfileRoot = copy,
                    DestinationDirectory = keep,
                    AllowOverwrite = true,
                },
                lab.ProfilesRoot);

            Assert.True(answered.Success, answered.Message);
            Assert.Contains("from the copy", File.ReadAllText(Path.Combine(keep, "Maladim.bes")));
        }

        [Fact]
        public void Rescue_FailsLoudlyWhenAskedForASaveTheCopyDoesNotHave()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-missing");
            lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));

            SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest
                {
                    ProfileRoot = copy,
                    DestinationDirectory = Path.Combine(lab.Root, "kept-missing"),
                    FileNames = new[] { "NotThere" },
                },
                lab.ProfilesRoot);

            // Silence here would be the dangerous outcome: a caller that asked for one save,
            // was told "rescued 0 of 0", and went on to delete the copy.
            Assert.False(result.Success);
            Assert.Contains("NotThere", result.Message);
        }

        [Fact]
        public void Rescue_TakesJustTheNamedSaveWhenNamesAreGiven()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-subset");
            lab.WriteSave(copy, Path.Combine("savegames", "Wanted.bes"));
            lab.WriteSave(copy, Path.Combine("savegames", "Unwanted.bes"));
            string keep = Path.Combine(lab.Root, "kept-subset");

            SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest
                {
                    ProfileRoot = copy,
                    DestinationDirectory = keep,
                    FileNames = new[] { "Wanted" },
                },
                lab.ProfilesRoot);

            Assert.True(result.Success, result.Message);
            Assert.True(File.Exists(Path.Combine(keep, "Wanted.bes")));
            Assert.False(File.Exists(Path.Combine(keep, "Unwanted.bes")));
        }

        [Fact]
        public void Rescue_RefusesAnInstalledGameFolderAndDoesNotCreateOne()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-installed");
            string source = lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));
            string game = lab.CreateInstalledGame("steam-game");
            string savegames = Path.Combine(game, "savegames");
            string wouldCreate = Path.Combine(game, "kept-from-copy");

            SafeCopySaveRescueResult existing = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest { ProfileRoot = copy, DestinationDirectory = savegames },
                lab.ProfilesRoot);
            SafeCopySaveRescueResult missing = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest { ProfileRoot = copy, DestinationDirectory = wouldCreate },
                lab.ProfilesRoot);

            Assert.False(existing.Success);
            Assert.Equal(CareerSaveLocation.InstalledDestinationRefused, existing.Message);
            Assert.False(File.Exists(Path.Combine(savegames, "Maladim.bes")));
            Assert.True(File.Exists(source));

            Assert.False(missing.Success);
            Assert.Equal(CareerSaveLocation.InstalledDestinationRefused, missing.Message);
            Assert.False(Directory.Exists(wouldCreate));
        }

        [Fact]
        public void Rescue_AMissingCopyFolderNamesTheFolderNotAPath()
        {
            using var lab = new SafeCopyLab();
            string missing = Path.Combine(lab.ProfilesRoot, "gone-copy");
            string keep = Path.Combine(lab.Root, "kept-gone");

            SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest { ProfileRoot = missing, DestinationDirectory = keep },
                lab.ProfilesRoot);

            Assert.False(result.Success);
            Assert.Equal(SafeCopySaveRescueService.CopyFolderMissing, result.Message);
            Assert.DoesNotContain(missing, result.Message);
            Assert.DoesNotContain(lab.Root, result.Message);
            Assert.DoesNotContain(":\\", result.Message);
            Assert.DoesNotContain("Playable copied game folder does not exist", result.Message);
        }

        [Fact]
        public void Rescue_AnUnusableDestinationDoesNotDumpThePath()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-blocked-folder");
            string source = lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));
            string blocker = Path.Combine(lab.Root, "not-a-folder");
            File.WriteAllBytes(blocker, new byte[] { 1 });
            string keep = Path.Combine(blocker, "kept-saves");

            SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest { ProfileRoot = copy, DestinationDirectory = keep },
                lab.ProfilesRoot);

            Assert.False(result.Success);
            Assert.Equal(SafeCopySaveRescueService.CouldNotKeep, result.Message);
            Assert.DoesNotContain(keep, result.Message);
            Assert.DoesNotContain(lab.Root, result.Message);
            Assert.DoesNotContain(":\\", result.Message);
            Assert.DoesNotContain("exception", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.True(File.Exists(source));
            Assert.False(Directory.Exists(keep));
        }

        // ---------------------------------------------------- rescue then delete

        [Fact]
        public void RescueThenDelete_KeepsEveryCareerAndThenRemovesTheCopy()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-roundtrip");
            string save = lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"), "the career");
            string before = Sha256(save);
            string keep = Path.Combine(lab.Root, "kept-roundtrip");

            SafeCopyRemovalResult result = SafeCopySaveRescueService.RescueThenDelete(
                copy,
                lab.ProfilesRoot,
                keep);

            Assert.True(result.Success, result.Message);
            Assert.False(Directory.Exists(copy));
            Assert.Equal(before, Sha256(Path.Combine(keep, "Maladim.bes")));
            Assert.NotNull(result.Rescue);
            Assert.Equal(1, result.Rescue!.RescuedCount);
        }

        [Fact]
        public void RescueThenDelete_LeavesTheCopyStandingWhenTheSavesCouldNotBeKept()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-blocked");
            string save = lab.WriteSave(copy, Path.Combine("savegames", "Maladim.bes"));
            string keep = Path.Combine(lab.Root, "kept-blocked");
            Directory.CreateDirectory(keep);
            File.WriteAllText(Path.Combine(keep, "Maladim.bes"), "a different career of the same name");

            SafeCopyRemovalResult result = SafeCopySaveRescueService.RescueThenDelete(
                copy,
                lab.ProfilesRoot,
                keep);

            // The whole ordering exists for this case. There must be no arrangement of failures
            // that ends with the career gone and nothing holding a copy of it.
            Assert.False(result.Success);
            Assert.True(Directory.Exists(copy));
            Assert.True(File.Exists(save));
            Assert.Null(result.DeletedProfileRoot);
            Assert.Contains("still here", result.Message);
            Assert.Equal("a different career of the same name", File.ReadAllText(Path.Combine(keep, "Maladim.bes")));
        }

        [Fact]
        public void RescueThenDelete_SkipsStraightToTheDeleteForACopyHoldingNothing()
        {
            using var lab = new SafeCopyLab();
            string copy = lab.CreateCopy("copy-nothing");

            SafeCopyRemovalResult result = SafeCopySaveRescueService.RescueThenDelete(
                copy,
                lab.ProfilesRoot,
                Path.Combine(lab.Root, "kept-nothing"));

            Assert.True(result.Success, result.Message);
            Assert.False(Directory.Exists(copy));
            Assert.Null(result.Rescue);
            Assert.False(Directory.Exists(Path.Combine(lab.Root, "kept-nothing")));
        }

        [Fact]
        public void InventoryAll_ListsEveryGeneratedCopyAndSkipsFoldersThisAppDidNotMake()
        {
            using var lab = new SafeCopyLab();
            string first = lab.CreateCopy("copy-one");
            lab.WriteSave(first, Path.Combine("savegames", "Maladim.bes"));
            lab.CreateCopy("copy-two");
            Directory.CreateDirectory(Path.Combine(lab.ProfilesRoot, "stranger"));

            var all = SafeCopySaveRescueService.InventoryAll(lab.ProfilesRoot);

            Assert.Equal(2, all.Count);
            Assert.Contains(all, row => row.DisplayName == "copy-one" && row.HasSaves);
            Assert.Contains(all, row => row.DisplayName == "copy-two" && !row.HasSaves);
            Assert.DoesNotContain(all, row => row.DisplayName == "stranger");
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            return Convert.ToHexString(SHA256.HashData(stream));
        }

        /// <summary>
        /// A throwaway app-owned profiles root with real folders in it.
        ///
        /// The copies here carry only the generated manifest file, which is exactly what the delete
        /// and the rescue require: both identify an app-generated copy by the manifest's presence,
        /// not by its contents. That is deliberate - a copy whose manifest has gone stale is still
        /// a copy whose saves must come out.
        /// </summary>
        private sealed class SafeCopyLab : IDisposable
        {
            public SafeCopyLab()
            {
                Root = Path.Combine(Path.GetTempPath(), $"onslaught-save-rescue-{Guid.NewGuid():N}");
                ProfilesRoot = Path.Combine(Root, "GameProfiles");
                Directory.CreateDirectory(ProfilesRoot);
            }

            public string Root { get; }

            public string ProfilesRoot { get; }

            public string CreateCopy(string name)
            {
                string copy = Path.Combine(ProfilesRoot, name);
                Directory.CreateDirectory(Path.Combine(copy, "savegames"));
                File.WriteAllText(
                    Path.Combine(copy, GameProfilePreflightService.ProfileManifestFileName),
                    "{\"schemaVersion\":\"" + GameProfilePreflightService.SchemaVersion + "\"}");
                return copy;
            }

            public string CreateInstalledGame(string name)
            {
                string game = Path.Combine(Root, name);
                Directory.CreateDirectory(Path.Combine(game, "data"));
                Directory.CreateDirectory(Path.Combine(game, "savegames"));
                File.WriteAllBytes(Path.Combine(game, "BEA.exe"), new byte[16]);
                return game;
            }

            public string WriteSave(string copy, string relativePath, string? marker = null)
            {
                string path = Path.Combine(copy, relativePath);
                Directory.CreateDirectory(Path.GetDirectoryName(path)!);
                File.WriteAllText(path, $"{SaveBytesMarker}:{marker ?? relativePath}", Encoding.ASCII);
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
                    // A leftover temp folder is not worth failing a test over.
                }
            }
        }
    }
}
