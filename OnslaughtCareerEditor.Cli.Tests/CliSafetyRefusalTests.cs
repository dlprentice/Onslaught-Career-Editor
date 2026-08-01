using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// The refusals the original CLI earned the hard way, pinned so a restructure cannot quietly drop
    /// them. Each one exists because its absence previously produced a green success over a write that
    /// was wrong, discarded, or aimed at something the tool must never touch.
    /// </summary>
    [Collection(CliCollection.Name)]
    public class CliSafetyRefusalTests
    {
        // ---------------------------------------------------------------- discarded intents

        /// <summary>
        /// <c>--new</c> is a boolean flag, so its value alone cannot distinguish "the user asked for OLD"
        /// from "the user said nothing about goodies". Only the presence of the token separates them.
        ///
        /// The assertion is the exit-code difference: with the flag the run is refused as a usage error
        /// before anything is read; without it the run proceeds far enough to reach the file. If the
        /// flag's presence stopped being tracked, both would take the same path.
        /// </summary>
        [Theory]
        [InlineData(true)]
        [InlineData(false)]
        public void AGoodieStyleRequestedWithGoodiePatchingOffIsRefused(bool legacyForm)
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("in.bes");
            string output = scratch.Path_("out.bes");

            CliRun withFlag = legacyForm
                ? Cli.Run(input, output, "--new", "--no-goodies")
                : Cli.Run("saves", "patch", input, output, "--new", "--no-goodies");

            Assert.Equal(1, withFlag.ExitCode);
            Assert.Contains("goodie", withFlag.StdErr, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(output), "A refused patch must not produce an output file.");

            CliRun withoutFlag = legacyForm
                ? Cli.Run(input, output, "--no-goodies")
                : Cli.Run("saves", "patch", input, output, "--no-goodies");

            // Silence about goodies is not a request for OLD, so this is not refused for that reason.
            Assert.NotEqual(1, withoutFlag.ExitCode);
        }

        [Theory]
        [InlineData(true)]
        [InlineData(false)]
        public void PerMissionRanksRequestedWithNodePatchingOffAreRefused(bool legacyForm)
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("in.bes");
            string output = scratch.Path_("out.bes");

            CliRun run = legacyForm
                ? Cli.Run(input, output, "--level-rank", "1:A", "--no-nodes")
                : Cli.Run("saves", "patch", input, output, "--level-rank", "1:A", "--no-nodes");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("--level-rank", run.StdErr);
            Assert.Contains("discarded", run.StdErr, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(output));
        }

        [Theory]
        [InlineData(true)]
        [InlineData(false)]
        public void PerCategoryKillsRequestedWithKillPatchingOffAreRefused(bool legacyForm)
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("in.bes");
            string output = scratch.Path_("out.bes");

            CliRun run = legacyForm
                ? Cli.Run(input, output, "--mech-kills", "40", "--no-kills")
                : Cli.Run("saves", "patch", input, output, "--mech-kills", "40", "--no-kills");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("discarded", run.StdErr, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(output));
        }

        /// <summary>
        /// Kills-only really is nodes/links/goodies off, so a per-mission rank supplied alongside it is
        /// dropped by the same pass and refused for the same reason.
        /// </summary>
        [Fact]
        public void PerMissionRanksRequestedWithKillsOnlyAreRefused()
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("in.bes");
            string output = scratch.Path_("out.bes");

            CliRun run = Cli.Run(input, output, "--level-rank", "1:A", "--kills-only");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("--level-rank", run.StdErr);
            Assert.False(File.Exists(output));
        }

        // ---------------------------------------------------------------- in-place writes

        [Theory]
        [InlineData(true)]
        [InlineData(false)]
        public void PatchingASaveOntoItselfIsRefused(bool legacyForm)
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("in.bes");
            byte[] before = File.ReadAllBytes(input);

            CliRun run = legacyForm
                ? Cli.Run(input, input, "--rank", "S")
                : Cli.Run("saves", "patch", input, input, "--rank", "S");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("In-place", run.StdErr, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(before, File.ReadAllBytes(input));
        }

        [Fact]
        public void WritingGoodieStatesOntoTheInputIsRefused()
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("in.bes");
            byte[] before = File.ReadAllBytes(input);

            CliRun run = Cli.Run("goodies", "set", input, input, "--goodie", "71:new");

            Assert.Equal(1, run.ExitCode);
            Assert.Equal(before, File.ReadAllBytes(input));
        }

        // ---------------------------------------------------------------- options-file guard

        [Fact]
        public void CareerPatchingAnOptionsFileIsBlockedByDefaultInTheLegacyForm()
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("defaultoptions.bea");
            string output = scratch.Path_("out.bea");

            CliRun run = Cli.Run(input, output, "--rank", "S");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("blocked for .bea", run.StdErr);
            Assert.Contains("--allow-career-sections-on-options-file", run.StdErr);
            Assert.False(File.Exists(output));
        }

        /// <summary>
        /// The verb form is deliberately stricter: it has no override at all, because
        /// <c>SaveEditorService</c> requires .bes on both sides.
        /// </summary>
        [Fact]
        public void TheSavesPatchVerbRefusesOptionsFilesOutright()
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("defaultoptions.bea");
            string output = scratch.Path_("out.bea");

            CliRun run = Cli.Run("saves", "patch", input, output, "--rank", "S",
                "--allow-career-sections-on-options-file");

            Assert.NotEqual(0, run.ExitCode);
            Assert.False(File.Exists(output));
        }

        // ---------------------------------------------------------------- targeted goodie mode

        [Fact]
        public void TargetedGoodieStatesCannotBeMixedWithBroadPatchOptions()
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("in.bes");
            string output = scratch.Path_("out.bes");

            CliRun run = Cli.Run(input, output, "--set-goodie-state", "71:new", "--rank", "S");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("--set-goodie-state", run.StdErr);
            Assert.False(File.Exists(output));
        }

        [Fact]
        public void AMalformedGoodieOverrideIsRejectedBeforeAnythingIsWritten()
        {
            using var scratch = new CliScratch();
            string input = scratch.NonSaveFixture("in.bes");
            string output = scratch.Path_("out.bes");

            CliRun run = Cli.Run("goodies", "set", input, output, "--goodie", "71:banana");

            Assert.Equal(1, run.ExitCode);
            Assert.False(File.Exists(output));
        }

        // ---------------------------------------------------------------- app-owned root containment

        /// <summary>
        /// The destructive verb must never reach outside the app-owned root. This is the one that would
        /// be catastrophic rather than merely wrong.
        /// </summary>
        [Theory]
        [InlineData("..")]
        [InlineData("../..")]
        public void DeletingASafeCopyRefusesPathsOutsideTheAppOwnedRoot(string escape)
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("copy", "delete", escape, "--force");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("outside the app-owned safe copy root", run.StdErr);
        }

        [Fact]
        public void DeletingASafeCopyRefusesAnAbsolutePathElsewhereOnDisk()
        {
            using var scratch = new CliScratch();
            string elsewhere = Path.Combine(scratch.Root, "not-a-safe-copy");
            Directory.CreateDirectory(elsewhere);

            CliRun run = Cli.Run("copy", "delete", elsewhere, "--force");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("outside the app-owned safe copy root", run.StdErr);
            Assert.True(Directory.Exists(elsewhere), "The refused folder must still be there.");
        }

        /// <summary>
        /// Inside the root but not app-generated: without the manifest this is somebody else's folder,
        /// and deleting it is not the tool's business.
        /// </summary>
        [Fact]
        public void DeletingRefusesAFolderInsideTheRootThatHasNoGeneratedManifest()
        {
            using var scratch = new CliScratch();
            string profilesRoot = Path.Combine(scratch.ConfigRoot, "OnslaughtCareerEditor", "GameProfiles");
            string impostor = Path.Combine(profilesRoot, "not-generated-by-us");
            Directory.CreateDirectory(impostor);
            File.WriteAllText(Path.Combine(impostor, "something-precious.txt"), "keep me");

            CliRun run = Cli.Run("copy", "delete", "not-generated-by-us", "--force");

            Assert.Equal(1, run.ExitCode);
            Assert.True(Directory.Exists(impostor), "A folder without the generated manifest must survive.");
            Assert.True(File.Exists(Path.Combine(impostor, "something-precious.txt")));
        }

        /// <summary>
        /// An irreversible delete is not something to do because an argument was mistyped.
        /// </summary>
        [Fact]
        public void DeletingRequiresExplicitConfirmation()
        {
            using var scratch = new CliScratch();
            string profilesRoot = Path.Combine(scratch.ConfigRoot, "OnslaughtCareerEditor", "GameProfiles");
            string profile = Path.Combine(profilesRoot, "safe-copy-under-test");
            Directory.CreateDirectory(profile);
            File.WriteAllText(Path.Combine(profile, "onslaught-profile-manifest.json"), "{}");
            File.WriteAllText(Path.Combine(profile, "BEA.exe"), "placeholder");

            CliRun run = Cli.Run("copy", "delete", "safe-copy-under-test");

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("--force", run.StdErr);
            Assert.True(Directory.Exists(profile), "Without --force the copy must still be there.");
        }

        [Fact]
        public void LaunchAndStopRefusePathsOutsideTheAppOwnedRoot()
        {
            using var scratch = new CliScratch();
            string elsewhere = Path.Combine(scratch.Root, "elsewhere");
            Directory.CreateDirectory(elsewhere);

            Assert.Equal(1, Cli.Run("copy", "launch", elsewhere).ExitCode);
            Assert.Equal(1, Cli.Run("copy", "stop", elsewhere).ExitCode);
        }

        /// <summary>
        /// The patch lane must never be pointed at an installed game. The engine refuses this too; this
        /// check is the outer gate, and it is the one that reports it as a refusal rather than a verdict.
        /// </summary>
        [Fact]
        public void PatchVerbsRefuseTargetsOutsideThePatchBenchWorkspace()
        {
            using var scratch = new CliScratch();
            string outsider = scratch.NonSaveFixture("pretend-install/BEA.exe");
            byte[] before = File.ReadAllBytes(outsider);

            foreach (string verb in new[] { "plan", "verify", "apply", "restore" })
            {
                CliRun run = Cli.Run("patch", verb, outsider);
                Assert.Equal(1, run.ExitCode);
                Assert.Contains("Patch Bench", run.StdErr);
            }

            Assert.Equal(before, File.ReadAllBytes(outsider));
        }

        [Fact]
        public void StagingRefusesASourceThatIsNotABeaExecutable()
        {
            using var scratch = new CliScratch();
            string wrongName = scratch.NonSaveFixture("something-else.exe");

            CliRun run = Cli.Run("patch", "stage", wrongName);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("BEA.exe", run.StdErr);
        }

        [Fact]
        public void AnUnknownPatchKeyIsRejectedBeforeTheEngineIsCalled()
        {
            using var scratch = new CliScratch();

            CliRun run = Cli.Run("patch", "verify", "some-workspace", "--patch", "no-such-patch-key");

            Assert.Equal(1, run.ExitCode);
        }
    }
}
