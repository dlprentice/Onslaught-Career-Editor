using System.Security.Cryptography;
using System.Text.Json;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// <c>patch install</c> - the verbs that touch the game the user actually installed.
    ///
    /// Everything else in this tool is confined to an app-owned workspace, and for a long time that
    /// confinement was the whole safety story: the installed game could not be a target, so it could
    /// not be broken. The maintainer's position is that the choice belongs to the person who owns
    /// the game. That only holds if the choice is reversible, so the trade is not "off limits" for
    /// "allowed" - it is "off limits" for "costs a verified backup, taken first".
    ///
    /// Nothing here goes near a real installation. Every case builds a folder shaped like one in
    /// temp and copies a clean specimen into it; when this machine has no specimen the case returns
    /// early rather than inventing an executable.
    /// </summary>
    [Collection(CliCollection.Name)]
    public sealed class CliInstallPatchTests
    {
        private const string KnownCleanSha256 =
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";

        [Fact]
        public void Status_ReportsAnInstallThatCannotYetBePutBack()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanExecutable())
                return;

            CliRun run = Cli.Run("patch", "install", "status", install.ExePath, "--json");

            Assert.Equal(0, run.ExitCode);
            JsonElement data = run.Envelope().GetProperty("data");
            Assert.False(data.GetProperty("hasBackup").GetBoolean());
            Assert.False(data.GetProperty("canBeRestored").GetBoolean());
        }

        [Fact]
        public void Backup_MakesTheOriginalAndItsRecordedHashWithoutTouchingTheExecutable()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanExecutable())
                return;

            string before = Sha256(install.ExePath);

            CliRun run = Cli.Run("patch", "install", "backup", install.ExePath, "--json");

            Assert.Equal(0, run.ExitCode);
            JsonElement data = run.Envelope().GetProperty("data");
            Assert.True(data.GetProperty("backupCreatedNow").GetBoolean());
            Assert.Equal(KnownCleanSha256, data.GetProperty("backupSha256").GetString(), ignoreCase: true);

            Assert.Equal(before, Sha256(install.ExePath));
            Assert.Equal(before, Sha256(install.BackupPath));
            Assert.Equal(KnownCleanSha256, File.ReadAllText(install.BackupHashPath).Trim(), ignoreCase: true);
        }

        /// <summary>
        /// The maintainer's own install is in exactly this state: an original kept by hand, and no
        /// tool ever wrote down its hash. The app used to refuse it with a message about internal
        /// lanes; it now recognises the file and records what is already true about it.
        /// </summary>
        [Fact]
        public void Backup_WritesTheMissingHashForAnOriginalSomebodyKeptByHand()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanBackupBesideAModifiedExecutable())
                return;

            CliRun run = Cli.Run("patch", "install", "backup", install.ExePath, "--json");

            Assert.Equal(0, run.ExitCode);
            JsonElement data = run.Envelope().GetProperty("data");
            Assert.True(data.GetProperty("hashSidecarCreatedNow").GetBoolean());
            Assert.False(data.GetProperty("backupCreatedNow").GetBoolean());
            Assert.Equal(KnownCleanSha256, File.ReadAllText(install.BackupHashPath).Trim(), ignoreCase: true);
        }

        [Fact]
        public void Backup_RefusesToInventAnOriginalFromAModifiedExecutable()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            File.WriteAllBytes(install.ExePath, new byte[4096]);

            CliRun run = Cli.Run("patch", "install", "backup", install.ExePath);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("already been changed", run.StdErr);
            Assert.False(File.Exists(install.BackupPath));
        }

        [Fact]
        public void Apply_RefusesUntilSomebodySaysTheyMeanIt()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanExecutable())
                return;

            string before = Sha256(install.ExePath);

            CliRun run = Cli.Run("patch", "install", "apply", install.ExePath);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("--yes", run.StdErr);
            Assert.Contains("not a copy", run.StdErr);
            Assert.Equal(before, Sha256(install.ExePath));
            Assert.False(File.Exists(install.BackupPath), "A refused apply must not leave a backup behind either.");
        }

        [Fact]
        public void Apply_BacksUpFirstThenPatchesAndTheOriginalIsStillThere()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanExecutable())
                return;

            CliRun run = Cli.Run("patch", "install", "apply", install.ExePath, "--yes", "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.True(File.Exists(install.BackupPath));
            Assert.Equal(KnownCleanSha256, Sha256(install.BackupPath), ignoreCase: true);
            Assert.NotEqual(KnownCleanSha256, Sha256(install.ExePath));

            JsonElement data = run.Envelope().GetProperty("data");
            Assert.True(data.GetProperty("backupCreatedNow").GetBoolean());
            Assert.True(data.GetProperty("patchKeys").GetArrayLength() > 0);
        }

        [Fact]
        public void Restore_PutsTheInstalledGameBackByteForByte()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanExecutable())
                return;

            Assert.Equal(0, Cli.Run("patch", "install", "apply", install.ExePath, "--yes").ExitCode);
            Assert.NotEqual(KnownCleanSha256, Sha256(install.ExePath));

            CliRun run = Cli.Run("patch", "install", "restore", install.ExePath);

            Assert.Equal(0, run.ExitCode);
            Assert.Equal(KnownCleanSha256, Sha256(install.ExePath), ignoreCase: true);
        }

        [Fact]
        public void Restore_SaysSoWhenThereIsNothingToPutBack()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanExecutable())
                return;

            CliRun run = Cli.Run("patch", "install", "restore", install.ExePath);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("nothing to put back", run.StdErr);
        }

        [Fact]
        public void Status_ReportsAnInstallThatCanBePutBackOnceItHasABackup()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanExecutable())
                return;

            Assert.Equal(0, Cli.Run("patch", "install", "backup", install.ExePath).ExitCode);

            CliRun run = Cli.Run("patch", "install", "status", install.ExePath, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.True(run.Envelope().GetProperty("data").GetProperty("canBeRestored").GetBoolean());
        }

        [Fact]
        public void EveryInstallVerbRefusesAFolderThatIsNotAGameInstall()
        {
            using var scratch = new CliScratch();
            string notAGame = scratch.Path_("not-a-game");
            Directory.CreateDirectory(notAGame);
            string exe = Path.Combine(notAGame, "BEA.exe");
            File.WriteAllBytes(exe, new byte[64]);

            CliRun run = Cli.Run("patch", "install", "backup", exe);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("data folder", run.StdErr);
        }

        /// <summary>
        /// The ordinary patch verbs stay confined to the app-owned workspace. Opening one door did
        /// not open all of them, and the refusal now names the door that is open.
        /// </summary>
        [Fact]
        public void TheOrdinaryPatchVerbsStillRefuseAnInstalledGame()
        {
            using var scratch = new CliScratch();
            using var install = new FakeInstall(scratch);
            if (!install.TryPlaceCleanExecutable())
                return;

            CliRun run = Cli.Run("patch", "apply", install.ExePath);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("Patch Bench workspace", run.StdErr);
            Assert.Contains("patch install apply", run.StdErr);
            Assert.Equal(KnownCleanSha256, Sha256(install.ExePath), ignoreCase: true);
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
        }

        /// <summary>
        /// A temp folder shaped like an installed game: BEA.exe beside a data folder. Never a real
        /// installation - the specimen is read and copied, never written to.
        /// </summary>
        private sealed class FakeInstall : IDisposable
        {
            public FakeInstall(CliScratch scratch)
            {
                GameRoot = scratch.Path_(Path.Combine("fake-install", Guid.NewGuid().ToString("N")));
                Directory.CreateDirectory(Path.Combine(GameRoot, "data"));
                ExePath = Path.Combine(GameRoot, "BEA.exe");
            }

            public string GameRoot { get; }

            public string ExePath { get; }

            public string BackupPath => BinaryPatchEngine.BuildBackupPath(ExePath);

            public string BackupHashPath => BinaryPatchEngine.BuildBackupHashPath(ExePath);

            public bool TryPlaceCleanExecutable()
            {
                string? specimen = FindCleanSpecimen();
                if (specimen is null)
                    return false;

                File.Copy(specimen, ExePath, overwrite: true);
                return true;
            }

            public bool TryPlaceCleanBackupBesideAModifiedExecutable()
            {
                string? specimen = FindCleanSpecimen();
                if (specimen is null)
                    return false;

                File.Copy(specimen, BackupPath, overwrite: true);
                byte[] modified = File.ReadAllBytes(specimen);
                modified[0x400] ^= 0xFF;
                File.WriteAllBytes(ExePath, modified);
                return true;
            }

            private static string? FindCleanSpecimen()
            {
                foreach (string candidate in EnumerateCandidates())
                {
                    try
                    {
                        if (!File.Exists(candidate) || new FileInfo(candidate).Length != 2_506_752)
                            continue;

                        if (string.Equals(Sha256(candidate), KnownCleanSha256, StringComparison.OrdinalIgnoreCase))
                            return candidate;
                    }
                    catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                    {
                        // Try the next candidate.
                    }
                }

                return null;
            }

            private static IEnumerable<string> EnumerateCandidates()
            {
                string? repoRoot = FindRepoRoot();
                if (repoRoot is not null)
                {
                    yield return Path.Combine(repoRoot, "local-lab", "safe-copy-bea-pristine", "BEA.exe.original.backup");
                    yield return Path.Combine(repoRoot, "local-lab", "safe-copy-bea-pristine", "BEA.exe");
                }

                // The machine's own installation, read only, and only as a source of clean bytes.
                foreach (string root in new[]
                         {
                             @"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila",
                         })
                {
                    yield return Path.Combine(root, "BEA.exe.original.backup");
                }
            }

            private static string? FindRepoRoot()
            {
                DirectoryInfo? directory = new(AppContext.BaseDirectory);
                while (directory is not null && !File.Exists(Path.Combine(directory.FullName, "package.json")))
                    directory = directory.Parent;

                return directory?.FullName;
            }

            public void Dispose()
            {
                try
                {
                    if (Directory.Exists(GameRoot))
                        Directory.Delete(GameRoot, recursive: true);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                {
                    // A leftover temp folder is not worth failing a test over.
                }
            }
        }
    }
}
