using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Permission to patch an installed game, and the backup that has to exist before it.
    ///
    /// The app used to refuse this outright and force a multi-gigabyte copy of the whole game. The
    /// maintainer's position is that the choice belongs to the person who owns the game - but a
    /// choice you cannot undo is not a choice, so permission is expressed as an object that cannot
    /// be constructed until a verified original is sitting beside the executable. A caller that
    /// skips the backup has nothing to pass.
    ///
    /// The refusal these tests care most about is the third one: a modified executable with no
    /// backup beside it. Snapshotting that and naming it <c>.original.backup</c> would destroy the
    /// only route back, quietly, and every later restore would put the modification back.
    ///
    /// Nothing here writes to a real installation. Every case copies a specimen into a temp folder
    /// first; the pristine specimen itself is only ever read.
    /// </summary>
    public sealed class InstalledGameWriteAuthorizationTests
    {
        private const string KnownCleanSha256 =
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";

        // ------------------------------------------------ refusals that need no retail bytes

        [Fact]
        public void RefusesAFileThatIsNotThere()
        {
            var (success, message, authorization) = BinaryPatchEngine.AuthorizeInstalledGameWrite(
                Path.Combine(Path.GetTempPath(), $"missing-{Guid.NewGuid():N}", "BEA.exe"));

            Assert.False(success);
            Assert.Null(authorization);
            Assert.Contains("installed game folder", message);
        }

        [Fact]
        public void RefusesAnythingThatIsNotBeaExeItself()
        {
            using var lab = new InstallLab();
            string other = Path.Combine(lab.GameRoot, "Message.exe");
            File.WriteAllBytes(other, new byte[16]);

            var (success, message, _) = BinaryPatchEngine.AuthorizeInstalledGameWrite(other);

            Assert.False(success);
            Assert.Contains("BEA.exe", message);
        }

        [Fact]
        public void RefusesAFolderThatIsNotAGameInstall()
        {
            using var lab = new InstallLab(createDataFolder: false);
            File.WriteAllBytes(lab.ExePath, new byte[16]);

            var (success, message, _) = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);

            Assert.False(success);
            Assert.Contains("data folder", message);
        }

        /// <summary>
        /// The one that matters. A modified executable with nothing beside it cannot be turned into
        /// its own original, and the app must say so rather than making a backup that lies.
        /// </summary>
        [Fact]
        public void RefusesToInventAnOriginalFromAnAlreadyModifiedExecutable()
        {
            using var lab = new InstallLab();
            File.WriteAllBytes(lab.ExePath, new byte[2048]);

            var (success, message, authorization) = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);

            Assert.False(success);
            Assert.Null(authorization);
            Assert.Contains("already been changed", message);
            Assert.Contains("Nothing was changed", message);
            Assert.False(
                File.Exists(BinaryPatchEngine.BuildBackupPath(lab.ExePath)),
                "Refusing must not leave a backup of the modified file behind.");
        }

        [Fact]
        public void RefusesABackupBesideTheGameThatIsNotACleanRetailExecutable()
        {
            using var lab = new InstallLab();
            File.WriteAllBytes(lab.ExePath, new byte[2048]);
            File.WriteAllBytes(BinaryPatchEngine.BuildBackupPath(lab.ExePath), new byte[4096]);

            var (success, message, _) = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);

            Assert.False(success);
            Assert.Contains("not a clean retail BEA.exe", message);
        }

        // ------------------------------------------------ the paths that grant permission

        [Fact]
        public void MakesTheBackupAndVerifiesItWhenTheGameIsStillClean()
        {
            using var lab = new InstallLab();
            if (!lab.TryPlaceCleanExecutable())
                return;

            var (success, message, authorization) = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);

            Assert.True(success, message);
            Assert.NotNull(authorization);
            Assert.True(authorization!.BackupWasCreatedNow);
            Assert.Equal(KnownCleanSha256, authorization.BackupSha256, ignoreCase: true);
            Assert.True(File.Exists(authorization.BackupPath));
            Assert.True(File.Exists(authorization.BackupHashPath));
            Assert.Equal(
                KnownCleanSha256,
                File.ReadAllText(authorization.BackupHashPath).Trim(),
                ignoreCase: true);
            Assert.Equal(Sha256(lab.ExePath), Sha256(authorization.BackupPath));
        }

        /// <summary>
        /// The state a hand-patched install is actually in: somebody kept the original by hand,
        /// and no tool ever wrote down its hash. Recording it states something already true.
        /// </summary>
        [Fact]
        public void WritesTheMissingHashSidecarForAHandKeptOriginalAndSaysSo()
        {
            using var lab = new InstallLab();
            if (!lab.TryPlaceCleanBackupBesideAModifiedExecutable())
                return;

            string sidecar = BinaryPatchEngine.BuildBackupHashPath(lab.ExePath);
            Assert.False(File.Exists(sidecar), "This case starts with no sidecar.");

            var (success, message, authorization) = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);

            Assert.True(success, message);
            Assert.NotNull(authorization);
            Assert.True(authorization!.HashSidecarWasCreatedNow);
            Assert.False(authorization.BackupWasCreatedNow);
            Assert.True(File.Exists(sidecar));
            Assert.Equal(KnownCleanSha256, File.ReadAllText(sidecar).Trim(), ignoreCase: true);
            Assert.Contains("recorded its hash", message);
        }

        [Fact]
        public void LeavesAnAlreadyBackedUpInstallExactlyAsItFoundIt()
        {
            using var lab = new InstallLab();
            if (!lab.TryPlaceCleanExecutable())
                return;

            var first = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);
            Assert.True(first.success, first.message);
            DateTime backupWrittenAt = File.GetLastWriteTimeUtc(first.authorization!.BackupPath);

            var second = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);

            Assert.True(second.success, second.message);
            Assert.False(second.authorization!.BackupWasCreatedNow);
            Assert.False(second.authorization.HashSidecarWasCreatedNow);
            Assert.Equal(backupWrittenAt, File.GetLastWriteTimeUtc(second.authorization.BackupPath));
        }

        [Fact]
        public void RefusesWhenTheRecordedHashDoesNotDescribeTheBackupBesideIt()
        {
            using var lab = new InstallLab();
            if (!lab.TryPlaceCleanExecutable())
                return;

            var first = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);
            Assert.True(first.success, first.message);
            File.WriteAllText(first.authorization!.BackupHashPath, new string('a', 64));

            var (success, message, _) = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);

            Assert.False(success);
            Assert.Contains("does not match the file it describes", message);
        }

        // ------------------------------------------------ what the permission then allows

        [Fact]
        public void WithoutPermissionAnInstalledGameIsStillRefused()
        {
            using var lab = new InstallLab();
            if (!lab.TryPlaceCleanExecutable())
                return;

            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(lab.ExePath, lab.GameRoot));

            Assert.False(success);
            Assert.Contains("Backup file not found", message);
        }

        [Fact]
        public void PermissionGrantedForOneExecutableDoesNotCoverAnother()
        {
            using var lab = new InstallLab();
            using var otherLab = new InstallLab();
            if (!lab.TryPlaceCleanExecutable() || !otherLab.TryPlaceCleanExecutable())
                return;

            var granted = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);
            Assert.True(granted.success, granted.message);

            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(
                    otherLab.ExePath,
                    AllowedRoot: string.Empty,
                    InstalledGame: granted.authorization));

            Assert.False(success);
            Assert.Contains("different executable", message);
        }

        [Fact]
        public void RestoreWithPermissionPutsTheOriginalBackOverAModifiedInstall()
        {
            using var lab = new InstallLab();
            if (!lab.TryPlaceCleanExecutable())
                return;

            var granted = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);
            Assert.True(granted.success, granted.message);

            // Something else changed the executable after the backup was taken.
            byte[] modified = File.ReadAllBytes(lab.ExePath);
            modified[0x400] ^= 0xFF;
            File.WriteAllBytes(lab.ExePath, modified);
            Assert.NotEqual(KnownCleanSha256, Sha256(lab.ExePath));

            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(
                    lab.ExePath,
                    AllowedRoot: string.Empty,
                    InstalledGame: granted.authorization));

            Assert.True(success, message);
            Assert.Equal(KnownCleanSha256, Sha256(lab.ExePath), ignoreCase: true);
        }

        [Fact]
        public void RestoreRefusesOncePermissionsBackupHasBeenTakenAway()
        {
            using var lab = new InstallLab();
            if (!lab.TryPlaceCleanExecutable())
                return;

            var granted = BinaryPatchEngine.AuthorizeInstalledGameWrite(lab.ExePath);
            Assert.True(granted.success, granted.message);
            File.Delete(granted.authorization!.BackupPath);

            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(
                    lab.ExePath,
                    AllowedRoot: string.Empty,
                    InstalledGame: granted.authorization));

            Assert.False(success);
            Assert.Contains("no longer beside the game", message);
        }

        /// <summary>
        /// Guards the cases above from passing vacuously.
        ///
        /// Half this suite returns early when the machine has no clean specimen, which is right -
        /// executables are not synthesized here any more than saves are. But a broken specimen
        /// finder would turn every one of those tests into a silent pass, and nobody would notice.
        /// So: if the pristine specimen is sitting where this repository keeps it, the finder has
        /// to find it. On a machine without one this passes and says nothing.
        /// </summary>
        [Fact]
        public void WhenThisMachineHasThePristineSpecimenTheSuiteActuallyUsesIt()
        {
            using var lab = new InstallLab();
            string? repoRoot = InstallLab.RepoRootForTest;
            if (repoRoot is null)
                return;

            string pristine = Path.Combine(
                repoRoot, "local-lab", "safe-copy-bea-pristine", "BEA.exe.original.backup");
            if (!File.Exists(pristine) ||
                !string.Equals(Sha256(pristine), KnownCleanSha256, StringComparison.OrdinalIgnoreCase))
            {
                return;
            }

            Assert.True(
                lab.TryPlaceCleanExecutable(),
                "The pristine specimen is on this machine, so every specimen-backed case above ran for real.");
            Assert.Equal(KnownCleanSha256, Sha256(lab.ExePath), ignoreCase: true);
        }

        private static string Sha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
        }

        /// <summary>
        /// A throwaway folder shaped like an installed game.
        ///
        /// Cases that need real retail bytes copy a clean specimen in and return false when this
        /// machine has none, the same way the CLI suite handles real save bytes. The specimen is
        /// only ever read - nothing here writes to a real installation, and nothing here
        /// synthesizes an executable and calls it retail.
        /// </summary>
        private sealed class InstallLab : IDisposable
        {
            public InstallLab(bool createDataFolder = true)
            {
                GameRoot = Path.Combine(Path.GetTempPath(), $"onslaught-install-lab-{Guid.NewGuid():N}");
                Directory.CreateDirectory(GameRoot);
                if (createDataFolder)
                    Directory.CreateDirectory(Path.Combine(GameRoot, "data"));

                ExePath = Path.Combine(GameRoot, "BEA.exe");
            }

            public string GameRoot { get; }

            public string ExePath { get; }

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

                File.Copy(specimen, BinaryPatchEngine.BuildBackupPath(ExePath), overwrite: true);

                byte[] modified = File.ReadAllBytes(specimen);
                modified[0x400] ^= 0xFF;
                File.WriteAllBytes(ExePath, modified);
                return true;
            }

            /// <summary>
            /// A file on this machine whose bytes really are the clean retail build, verified by
            /// hash before being handed back. Null when there is none, and the caller returns.
            /// </summary>
            private static string? FindCleanSpecimen()
            {
                foreach (string candidate in EnumerateCandidates())
                {
                    try
                    {
                        if (!File.Exists(candidate))
                            continue;

                        if (new FileInfo(candidate).Length != 2_506_752)
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
                    yield return Path.Combine(
                        repoRoot, "local-lab", "safe-copy-bea-pristine", "BEA.exe.original.backup");
                    yield return Path.Combine(repoRoot, "local-lab", "safe-copy-bea-pristine", "BEA.exe");
                }

                string? gameDir = AppConfig.Load().GetGameDir() ?? AppConfig.DetectGameDirectory();
                if (gameDir is not null)
                {
                    yield return Path.Combine(gameDir, "BEA.exe.original.backup");
                    yield return Path.Combine(gameDir, "BEA.exe");
                }
            }

            internal static string? RepoRootForTest => FindRepoRoot();

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
