using System;
using System.IO;
using System.Linq;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The list a person needs before being offered a delete.
    ///
    /// The app could make safe copies and could not show them: each one is most of a game install
    /// in Roaming AppData, nothing reported the space, and the only route that removed one was a
    /// CLI verb. Offering to delete something somebody cannot see is not an offer.
    /// </summary>
    public sealed class SafeCopyCatalogTests
    {
        [Fact]
        public void List_ReportsSizeAndTheCareersInsideEachCopy()
        {
            using var lab = new CopyLab();
            string big = lab.CreateCopy("big", payloadBytes: 4096);
            lab.WriteSave(big, "Maladim.bes");
            lab.CreateCopy("small", payloadBytes: 16);

            var copies = SafeCopyCatalogService.List(lab.ProfilesRoot);

            Assert.Equal(2, copies.Count);
            Assert.Equal("big", copies[0].DisplayName);
            Assert.True(copies[0].SizeBytes > copies[1].SizeBytes, "Largest first is what makes the list useful.");
            Assert.Equal(1, copies[0].CareerSaveCount);
            Assert.Equal(0, copies[1].CareerSaveCount);
        }

        [Fact]
        public void List_LeavesOutFoldersThisAppDidNotGenerate()
        {
            using var lab = new CopyLab();
            lab.CreateCopy("ours", payloadBytes: 32);
            Directory.CreateDirectory(Path.Combine(lab.ProfilesRoot, "somebody-elses-folder"));

            var copies = SafeCopyCatalogService.List(lab.ProfilesRoot);

            Assert.Single(copies);
            Assert.Equal("ours", copies[0].DisplayName);
        }

        [Fact]
        public void List_SaysWhetherACopyCanStillBeLaunched()
        {
            using var lab = new CopyLab();
            string playable = lab.CreateCopy("playable", payloadBytes: 8);
            File.WriteAllBytes(Path.Combine(playable, "BEA.exe"), new byte[8]);
            lab.CreateCopy("broken", payloadBytes: 8);

            var copies = SafeCopyCatalogService.List(lab.ProfilesRoot);

            Assert.True(copies.Single(copy => copy.DisplayName == "playable").Playable);
            Assert.False(copies.Single(copy => copy.DisplayName == "broken").Playable);
        }

        [Fact]
        public void MeasureDirectoryBytes_AddsUpWhatIsActuallyThere()
        {
            using var lab = new CopyLab();
            string copy = lab.CreateCopy("measured", payloadBytes: 1000);
            File.WriteAllBytes(Path.Combine(copy, "savegames", "more.bin"), new byte[2000]);

            long measured = SafeCopyCatalogService.MeasureDirectoryBytes(copy);

            Assert.True(measured >= 3000, $"Expected at least the 3000 bytes written, measured {measured}.");
        }

        [Fact]
        public void MeasureDirectoryBytes_IsZeroForAFolderThatIsNotThere()
        {
            Assert.Equal(0, SafeCopyCatalogService.MeasureDirectoryBytes(
                Path.Combine(Path.GetTempPath(), $"missing-{Guid.NewGuid():N}")));
        }

        [Fact]
        public void TotalSize_IsWhatTheCopiesCostTogether()
        {
            using var lab = new CopyLab();
            lab.CreateCopy("one", payloadBytes: 1024);
            lab.CreateCopy("two", payloadBytes: 2048);

            var copies = SafeCopyCatalogService.List(lab.ProfilesRoot);

            Assert.Equal(copies.Sum(copy => copy.SizeBytes), SafeCopyCatalogService.TotalSizeBytes(copies));
        }

        [Theory]
        [InlineData(0, "0 MB")]
        [InlineData(2048L * 1024 * 1024, "2.0 GB")]
        [InlineData(700L * 1024 * 1024, "700 MB")]
        [InlineData(4096, "4 KB")]
        public void DescribeSize_UsesTheUnitsAPersonUses(long bytes, string expected)
        {
            Assert.Equal(expected, SafeCopyCatalogService.DescribeSize(bytes));
        }

        [Fact]
        public void RoomForACopy_LeavesHeadroomSoTheGameCanStillWriteASave()
        {
            long source = 700L * 1024 * 1024;

            Assert.True(SafeCopyCatalogService.HasRoomForCopy(source + SafeCopyCatalogService.HeadroomBytes, source));
            Assert.False(SafeCopyCatalogService.HasRoomForCopy(source + 1024, source));
        }

        /// <summary>
        /// A volume that will not report its free space is a volume the app knows nothing about.
        /// Refusing a copy on that basis would be inventing a problem, so an unknown must read as
        /// "go ahead" rather than as zero.
        /// </summary>
        [Fact]
        public void UnknownFreeSpaceIsNotTreatedAsNoSpace()
        {
            Assert.True(SafeCopyCatalogService.HasRoomForCopy(null, 900L * 1024 * 1024 * 1024));
        }

        [Fact]
        public void FreeSpace_IsNullForAPathThatMakesNoSense()
        {
            Assert.Null(SafeCopyCatalogService.GetFreeSpaceBytes(string.Empty));
        }

        private sealed class CopyLab : IDisposable
        {
            public CopyLab()
            {
                Root = Path.Combine(Path.GetTempPath(), $"onslaught-copy-catalog-{Guid.NewGuid():N}");
                ProfilesRoot = Path.Combine(Root, "GameProfiles");
                Directory.CreateDirectory(ProfilesRoot);
            }

            public string Root { get; }

            public string ProfilesRoot { get; }

            public string CreateCopy(string name, int payloadBytes)
            {
                string copy = Path.Combine(ProfilesRoot, name);
                Directory.CreateDirectory(Path.Combine(copy, "savegames"));
                File.WriteAllText(
                    Path.Combine(copy, GameProfilePreflightService.ProfileManifestFileName),
                    "{\"schemaVersion\":\"" + GameProfilePreflightService.SchemaVersion + "\"}");
                File.WriteAllBytes(Path.Combine(copy, "payload.bin"), new byte[payloadBytes]);
                return copy;
            }

            public void WriteSave(string copy, string fileName)
            {
                File.WriteAllText(Path.Combine(copy, "savegames", fileName), "career-save-fixture");
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
