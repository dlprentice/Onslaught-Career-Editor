using System;
using System.IO;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Settings and Home used to treat any folder with BEA.exe plus a data directory as a finished
    /// install. That is only a layout check. This is the identity check those pages need: is the
    /// executable the known Steam retail file, something else, or unreadable right now?
    ///
    /// Nothing here writes to a real installation. Wrong-size files are invented; a matching hash
    /// is only asserted when a local clean specimen is already on the machine.
    /// </summary>
    public sealed class RetailExecutableIdentityTests
    {
        private const string KnownCleanSha256 =
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
        private const long KnownRetailSteamSize = 2_506_752;

        [Fact]
        public void MissingPathIsMissing()
        {
            Assert.Equal(
                RetailExecutableIdentity.Missing,
                BinaryPatchEngine.IdentifyRetailExecutable(null));
            Assert.Equal(
                RetailExecutableIdentity.Missing,
                BinaryPatchEngine.IdentifyRetailExecutable("   "));
            Assert.Equal(
                RetailExecutableIdentity.Missing,
                BinaryPatchEngine.IdentifyRetailExecutable(
                    Path.Combine(Path.GetTempPath(), $"absent-{Guid.NewGuid():N}.exe")));
        }

        [Fact]
        public void WrongSizeIsDifferentFromKnownRetail()
        {
            string path = Path.Combine(Path.GetTempPath(), $"bea-wrong-size-{Guid.NewGuid():N}.exe");
            try
            {
                File.WriteAllBytes(path, new byte[2048]);

                Assert.Equal(
                    RetailExecutableIdentity.DifferentFromKnownRetail,
                    BinaryPatchEngine.IdentifyRetailExecutable(path));
                Assert.False(BinaryPatchEngine.LooksLikeCleanRetailExecutable(path));
            }
            finally
            {
                if (File.Exists(path))
                    File.Delete(path);
            }
        }

        [Fact]
        public void RightSizeWrongBytesIsDifferentFromKnownRetail()
        {
            string path = Path.Combine(Path.GetTempPath(), $"bea-wrong-hash-{Guid.NewGuid():N}.exe");
            try
            {
                File.WriteAllBytes(path, new byte[KnownRetailSteamSize]);

                Assert.Equal(
                    RetailExecutableIdentity.DifferentFromKnownRetail,
                    BinaryPatchEngine.IdentifyRetailExecutable(path));
                Assert.False(BinaryPatchEngine.LooksLikeCleanRetailExecutable(path));
            }
            finally
            {
                if (File.Exists(path))
                    File.Delete(path);
            }
        }

        [Fact]
        public void LockedFileIsUnreadableRatherThanSilentlyDifferent()
        {
            string path = Path.Combine(Path.GetTempPath(), $"bea-locked-{Guid.NewGuid():N}.exe");
            try
            {
                File.WriteAllBytes(path, new byte[KnownRetailSteamSize]);
                using var exclusive = new FileStream(
                    path,
                    FileMode.Open,
                    FileAccess.ReadWrite,
                    FileShare.None);

                Assert.Equal(
                    RetailExecutableIdentity.Unreadable,
                    BinaryPatchEngine.IdentifyRetailExecutable(path));
                Assert.False(BinaryPatchEngine.LooksLikeCleanRetailExecutable(path));
            }
            finally
            {
                if (File.Exists(path))
                    File.Delete(path);
            }
        }

        [Fact]
        public void CleanSpecimenIsKnownRetailWhenOneIsOnThisMachine()
        {
            string? specimen = FindCleanSpecimen();
            if (specimen is null)
                return;

            Assert.Equal(
                RetailExecutableIdentity.KnownCleanRetail,
                BinaryPatchEngine.IdentifyRetailExecutable(specimen));
            Assert.True(BinaryPatchEngine.LooksLikeCleanRetailExecutable(specimen));
        }

        [Fact]
        public void TryGetGameExecutablePathFindsBeaBesideData()
        {
            string root = Path.Combine(Path.GetTempPath(), $"bea-dir-{Guid.NewGuid():N}");
            Directory.CreateDirectory(Path.Combine(root, "data"));
            string exe = Path.Combine(root, "BEA.exe");
            File.WriteAllBytes(exe, new byte[16]);

            try
            {
                Assert.Equal(exe, AppConfig.TryGetGameExecutablePath(root));
                Assert.Null(AppConfig.TryGetGameExecutablePath(null));
                Assert.Null(AppConfig.TryGetGameExecutablePath(Path.Combine(root, "missing")));
            }
            finally
            {
                Directory.Delete(root, recursive: true);
            }
        }

        private static string? FindCleanSpecimen()
        {
            DirectoryInfo? directory = new(AppContext.BaseDirectory);
            while (directory is not null && !File.Exists(Path.Combine(directory.FullName, "package.json")))
                directory = directory.Parent;

            if (directory is null)
                return null;

            string candidate = Path.Combine(
                directory.FullName, "local-lab", "safe-copy-bea-pristine", "BEA.exe.original.backup");
            if (!File.Exists(candidate) || new FileInfo(candidate).Length != KnownRetailSteamSize)
                return null;

            string hash = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(candidate)))
                .ToLowerInvariant();
            return string.Equals(hash, KnownCleanSha256, StringComparison.OrdinalIgnoreCase)
                ? candidate
                : null;
        }
    }
}
