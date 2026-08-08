using System.Security.Cryptography;
using System.Text.Json;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// The headless half of the save-durability contract.
    ///
    /// <c>copy delete</c> was the one command in this tool that could destroy something the game
    /// cannot make again, and it did it on <c>--force</c> alone. --force answers "yes, remove
    /// several gigabytes of copied game files"; it was never an answer to "and lose the career
    /// named Maladim". These tests hold those two questions apart.
    /// </summary>
    [Collection(CliCollection.Name)]
    public sealed class CliSaveRescueTests
    {
        [Fact]
        public void CopyDelete_RefusesACopyHoldingACareerSaveEvenWithForce()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "keeper");
            string save = WriteSave(copy, "Maladim.bes");

            CliRun run = Cli.Run("copy", "delete", "keeper", "--force");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("Maladim", run.StdErr);
            Assert.Contains("--keep-saves-in", run.StdErr);
            Assert.Contains("--discard-saves", run.StdErr);
            Assert.True(File.Exists(save), "The career save must survive a refused delete.");
            Assert.True(Directory.Exists(copy));
        }

        [Fact]
        public void CopyDelete_KeepsTheSavesFirstWhenToldWhereToPutThem()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "tidy");
            string save = WriteSave(copy, "Maladim.bes", "a career worth keeping");
            string before = Sha256(save);
            string keep = scratch.Path_("kept");

            CliRun run = Cli.Run("copy", "delete", "tidy", "--force", "--keep-saves-in", keep, "--json");

            Assert.Equal(0, run.ExitCode);
            JsonElement data = run.Envelope().GetProperty("data");
            Assert.True(data.GetProperty("deleted").GetBoolean());
            Assert.Equal(1, data.GetProperty("savesKept").GetInt32());

            Assert.False(Directory.Exists(copy));
            Assert.Equal(before, Sha256(Path.Combine(keep, "Maladim.bes")));
        }

        [Fact]
        public void CopyDelete_LeavesTheCopyStandingWhenTheSavesCouldNotBeKept()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "blocked");
            WriteSave(copy, "Maladim.bes");
            string keep = scratch.Path_("kept-blocked");
            Directory.CreateDirectory(keep);
            File.WriteAllText(Path.Combine(keep, "Maladim.bes"), "a different career of the same name");

            CliRun run = Cli.Run("copy", "delete", "blocked", "--force", "--keep-saves-in", keep);

            Assert.Equal(1, run.ExitCode);
            Assert.True(Directory.Exists(copy), "A failed rescue must never be followed by the delete.");
            Assert.Equal(
                "a different career of the same name",
                File.ReadAllText(Path.Combine(keep, "Maladim.bes")));
        }

        [Fact]
        public void CopyDelete_GoesAheadWhenTheSavesAreDiscardedOnPurpose()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "doomed");
            WriteSave(copy, "Throwaway.bes");

            CliRun run = Cli.Run("copy", "delete", "doomed", "--force", "--discard-saves");

            Assert.Equal(0, run.ExitCode);
            Assert.False(Directory.Exists(copy));
        }

        [Fact]
        public void CopyDelete_RefusesTheTwoContradictoryFlagsTogether()
        {
            using var scratch = new CliScratch();
            MakeCopy(scratch, "confused");

            CliRun run = Cli.Run(
                "copy", "delete", "confused", "--force",
                "--keep-saves-in", scratch.Path_("kept"), "--discard-saves");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("opposite things", run.StdErr);
        }

        [Fact]
        public void CopyDelete_StillRemovesACopyThatIsHoldingNothing()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "empty");

            CliRun run = Cli.Run("copy", "delete", "empty", "--force");

            Assert.Equal(0, run.ExitCode);
            Assert.False(Directory.Exists(copy));
        }

        [Fact]
        public void CopySaves_ShowsWhatADeleteWouldTake()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "inventory");
            WriteSave(copy, "Maladim.bes");
            WriteSave(copy, "Second.bes");

            CliRun run = Cli.Run("copy", "saves", "inventory", "--json");

            Assert.Equal(0, run.ExitCode);
            JsonElement data = run.Envelope().GetProperty("data");
            Assert.Equal(2, data.GetProperty("count").GetInt32());
            string[] names = data.GetProperty("saves")
                .EnumerateArray()
                .Select(save => save.GetProperty("fileName").GetString()!)
                .OrderBy(name => name, StringComparer.Ordinal)
                .ToArray();
            Assert.Equal(new[] { "Maladim.bes", "Second.bes" }, names);
        }

        [Fact]
        public void CopySaves_SweepsEveryCopyWhenNoIdIsGiven()
        {
            using var scratch = new CliScratch();
            WriteSave(MakeCopy(scratch, "one"), "Maladim.bes");
            MakeCopy(scratch, "two");

            CliRun run = Cli.Run("copy", "saves", "--json");

            Assert.Equal(0, run.ExitCode);
            JsonElement copies = run.Envelope().GetProperty("data").GetProperty("copies");
            Assert.Equal(2, copies.GetArrayLength());
        }

        [Fact]
        public void CopyRescue_BringsSavesOutAndLeavesTheCopyPlayable()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "rescue");
            string save = WriteSave(copy, "Maladim.bes", "the career");
            string keep = scratch.Path_("kept-rescue");

            CliRun run = Cli.Run("copy", "rescue", "rescue", "--to", keep, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Equal(1, run.Envelope().GetProperty("data").GetProperty("rescued").GetInt32());
            Assert.Equal(Sha256(save), Sha256(Path.Combine(keep, "Maladim.bes")));
            Assert.True(File.Exists(save), "Rescue copies; the copy stays playable.");
            Assert.True(Directory.Exists(copy));
        }

        [Fact]
        public void CopyRescue_AsksBeforeReplacingAndThenObeys()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "clash");
            WriteSave(copy, "Maladim.bes", "from the copy");
            string keep = scratch.Path_("kept-clash");
            Directory.CreateDirectory(keep);
            File.WriteAllText(Path.Combine(keep, "Maladim.bes"), "already here");

            CliRun asked = Cli.Run("copy", "rescue", "clash", "--to", keep);
            Assert.Equal(1, asked.ExitCode);
            Assert.Contains("--overwrite", asked.StdErr);
            Assert.Equal("already here", File.ReadAllText(Path.Combine(keep, "Maladim.bes")));

            CliRun answered = Cli.Run("copy", "rescue", "clash", "--to", keep, "--overwrite");
            Assert.Equal(0, answered.ExitCode);
            Assert.Contains("from the copy", File.ReadAllText(Path.Combine(keep, "Maladim.bes")));
        }

        [Fact]
        public void CopyRescue_NeedsToBeToldWhereTheSavesShouldGo()
        {
            using var scratch = new CliScratch();
            MakeCopy(scratch, "nowhere");

            CliRun run = Cli.Run("copy", "rescue", "nowhere");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("--to", run.StdErr);
        }

        [Fact]
        public void CopyRescue_RefusesToKeepSavesInsideTheCopyItself()
        {
            using var scratch = new CliScratch();
            string copy = MakeCopy(scratch, "selfish");
            WriteSave(copy, "Maladim.bes");

            CliRun run = Cli.Run("copy", "rescue", "selfish", "--to", Path.Combine(copy, "backup"));

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("outside the copy", run.StdErr);
        }

        /// <summary>
        /// The round trip the Save Lab promises, with real bytes: a genuine career save goes into a
        /// copy's savegames folder the way the app puts it there, comes back out through rescue,
        /// and is byte-for-byte the file that went in.
        ///
        /// Skipped on a machine with no Battle Engine Aquila installation. Saves are never
        /// synthesized for a test - a test that needs valid bytes either gets real ones or does not
        /// run.
        /// </summary>
        [Fact]
        public void RealCareerSave_SurvivesTheTripIntoACopyAndBackOut()
        {
            using var scratch = new CliScratch();
            string? baseline = scratch.TryCopyRealBaselineSave("baseline.bes");
            if (baseline is null)
                return;

            string copy = MakeCopy(scratch, "roundtrip");
            string inside = Path.Combine(copy, "savegames", "RoundTrip.bes");
            File.Copy(baseline, inside);
            string keep = scratch.Path_("kept-roundtrip");

            CliRun run = Cli.Run("copy", "rescue", "roundtrip", "--to", keep, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Equal(Sha256(baseline), Sha256(Path.Combine(keep, "RoundTrip.bes")));
        }

        /// <summary>
        /// A safe copy carrying only the generated manifest, which is what the delete and the
        /// rescue identify a copy by. The location comes from <see cref="AppConfig"/> rather than
        /// being rebuilt here, so a change to where copies live cannot leave these tests quietly
        /// exercising an empty folder.
        /// </summary>
        private static string MakeCopy(CliScratch scratch, string id)
        {
            string copy = Path.Combine(AppConfig.GetGameProfilesDir(), id);
            Directory.CreateDirectory(Path.Combine(copy, "savegames"));
            File.WriteAllText(
                Path.Combine(copy, GameProfilePreflightService.ProfileManifestFileName),
                "{\"schemaVersion\":\"" + GameProfilePreflightService.SchemaVersion + "\"}");
            return copy;
        }

        private static string WriteSave(string copy, string fileName, string? marker = null)
        {
            string path = Path.Combine(copy, "savegames", fileName);
            File.WriteAllText(path, $"career-save-fixture:{marker ?? fileName}");
            return path;
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            return Convert.ToHexString(SHA256.HashData(stream));
        }
    }
}
