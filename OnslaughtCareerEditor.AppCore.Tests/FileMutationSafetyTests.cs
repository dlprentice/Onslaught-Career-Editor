using System.Buffers.Binary;
using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class FileMutationSafetyTests
    {
        [Fact]
        public void PatchFile_RejectsNonBesOutput()
        {
            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = Path.Combine(root.Path, "not-a-save.exe");

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains(".bes output", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(output));
        }

        [Fact]
        public void PatchFile_RejectsHardlinkOutputAliasOfInput()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = Path.Combine(root.Path, "alias.bes");
            byte[] before = File.ReadAllBytes(input);
            Assert.True(
                CreateHardLink(output, input, IntPtr.Zero),
                new Win32Exception(Marshal.GetLastWin32Error()).Message);

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains("hardlink", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(before, File.ReadAllBytes(input));
        }

        [Fact]
        public void PatchGoodieStates_RejectsHardlinkOutputAliasOfInput()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = Path.Combine(root.Path, "alias.bes");
            byte[] before = File.ReadAllBytes(input);
            Assert.True(
                CreateHardLink(output, input, IntPtr.Zero),
                new Win32Exception(Marshal.GetLastWin32Error()).Message);

            PatchResult result = BesFilePatcher.PatchGoodieStates(
                input,
                output,
                new Dictionary<int, uint> { [71] = 3 });

            Assert.False(result.Success);
            Assert.Contains("hardlink", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(before, File.ReadAllBytes(input));
        }

        [Fact]
        public void PatchFile_RejectsSymlinkOutputAliasOfInput()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = Path.Combine(root.Path, "alias.bes");
            byte[] before = File.ReadAllBytes(input);
            File.CreateSymbolicLink(output, input);

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains("reparse", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(before, File.ReadAllBytes(input));
        }

        [Fact]
        public void PatchFile_RejectsDanglingSymlinkOutput()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = Path.Combine(root.Path, "dangling.bes");
            string missingTarget = Path.Combine(root.Path, "missing-target.bes");
            File.CreateSymbolicLink(output, missingTarget);

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains("reparse", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(missingTarget));
        }

        [Fact]
        public void PatchFile_RejectsReparsePointOutputAncestor()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string realOutputDirectory = Path.Combine(root.Path, "real-output");
            string linkedOutputDirectory = Path.Combine(root.Path, "linked-output");
            Directory.CreateDirectory(realOutputDirectory);
            Directory.CreateSymbolicLink(linkedOutputDirectory, realOutputDirectory);
            string output = Path.Combine(linkedOutputDirectory, "output.bes");

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains("reparse", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(Path.Combine(realOutputDirectory, "output.bes")));
        }

        [Fact]
        public void PatchFile_RejectsOutputInsideGameTree()
        {
            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string gameRoot = Path.Combine(root.Path, "fake-game");
            Directory.CreateDirectory(Path.Combine(gameRoot, "data"));
            Directory.CreateDirectory(Path.Combine(gameRoot, "savegames"));
            File.WriteAllBytes(Path.Combine(gameRoot, "BEA.exe"), [0x4D, 0x5A]);
            string output = Path.Combine(gameRoot, "savegames", "output.bes");

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains("game folder", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(output));
        }

        [Fact]
        public void DirectoryLockSet_BlocksPhysicalDirectoryRename()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string lockedDirectory = Path.Combine(root.Path, "locked");
            string movedDirectory = Path.Combine(root.Path, "moved");
            Directory.CreateDirectory(lockedDirectory);

            using FileMutationSafety.DirectoryLockSet _ =
                FileMutationSafety.LockDirectoryTree(lockedDirectory, "Test directory");

            Assert.ThrowsAny<IOException>(() => Directory.Move(lockedDirectory, movedDirectory));
            Assert.True(Directory.Exists(lockedDirectory));
        }

        [Fact]
        public void DirectoryLockSet_WritableTargetGuardPersistsUntilAnotherEntryExists()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string lockedDirectory = Path.Combine(root.Path, "guarded-output");
            Directory.CreateDirectory(lockedDirectory);

            using FileMutationSafety.DirectoryLockSet locks =
                FileMutationSafety.LockDirectoryTree(
                    lockedDirectory,
                    "Guarded output directory",
                    guardTargetMutation: true);
            Assert.Single(Directory.EnumerateFiles(
                lockedDirectory,
                ".onslaught-directory-guard-*.tmp",
                SearchOption.TopDirectoryOnly));

            File.WriteAllText(Path.Combine(lockedDirectory, "payload.bin"), "payload");
            locks.ReleaseMutationSentinelIfDirectoryNonEmpty();

            Assert.Empty(Directory.EnumerateFiles(
                lockedDirectory,
                ".onslaught-directory-guard-*.tmp",
                SearchOption.TopDirectoryOnly));
            Assert.Equal("payload", File.ReadAllText(Path.Combine(lockedDirectory, "payload.bin")));
        }

        [Fact]
        public void DirectoryLockSet_RejectsRootSwapBeforeFirstHandleAcquisition()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string selectedDirectory = Path.Combine(root.Path, "selected");
            string originalDirectory = Path.Combine(root.Path, "selected-original");
            string outsideDirectory = Path.Combine(root.Path, "outside");
            Directory.CreateDirectory(selectedDirectory);
            Directory.CreateDirectory(outsideDirectory);

            try
            {
                InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                {
                    using FileMutationSafety.DirectoryLockSet _ = FileMutationSafety.LockDirectoryTree(
                        selectedDirectory,
                        "Test directory",
                        beforeFirstOpenForTest: () =>
                        {
                            Directory.Move(selectedDirectory, originalDirectory);
                            Directory.CreateSymbolicLink(selectedDirectory, outsideDirectory);
                        });
                });

                Assert.Contains("reparse", error.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(selectedDirectory) &&
                    (File.GetAttributes(selectedDirectory) & FileAttributes.ReparsePoint) != 0)
                {
                    Directory.Delete(selectedDirectory);
                }

                if (Directory.Exists(originalDirectory))
                    Directory.Move(originalDirectory, selectedDirectory);
            }
        }

        [Fact]
        public void StagedFile_DeniesRenameWhileWritable()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string stagedPath = Path.Combine(root.Path, "staged.tmp");
            string movedPath = Path.Combine(root.Path, "moved.tmp");
            using FileStream staged = FileMutationSafety.CreateStagedFile(stagedPath);
            staged.Write([0x01, 0x02, 0x03]);

            Exception? error = Record.Exception(() => File.Move(stagedPath, movedPath));
            Assert.True(error is IOException or UnauthorizedAccessException, error?.ToString());
            Assert.True(File.Exists(stagedPath));
            Assert.False(File.Exists(movedPath));
        }

        [Fact]
        public void StagedFile_RejectsPreWriteHardlinkWithoutWritingAlias()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string stagedPath = Path.Combine(root.Path, "staged.tmp");
            string aliasPath = Path.Combine(root.Path, "outside-alias.tmp");

            Exception? error = Record.Exception(() =>
                FileMutationSafety.CreateStagedFile(
                    stagedPath,
                    createdPath => Assert.True(
                        CreateHardLink(aliasPath, createdPath, IntPtr.Zero),
                        new Win32Exception(Marshal.GetLastWin32Error()).Message)));

            Assert.True(error is IOException or InvalidOperationException, error?.ToString());
            Assert.True(File.Exists(aliasPath));
            Assert.Equal(0, new FileInfo(aliasPath).Length);
            Assert.False(File.Exists(stagedPath));
        }

        [Fact]
        public void Commit_RejectsPostRenameSymlinkSwap()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = Path.Combine(root.Path, "output.bes");
            string escaped = Path.Combine(root.Path, "escaped.bes");
            byte[] before = File.ReadAllBytes(input);
            using GuardedFileMutation mutation = FileMutationSafety.Begin(output, input);

            IOException error = Assert.Throws<IOException>(() =>
                mutation.Commit(before, committedPath =>
                {
                    File.Move(committedPath, escaped);
                    File.CreateSymbolicLink(committedPath, escaped);
                }));

            Assert.Contains("reparse", error.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(before, File.ReadAllBytes(input));
            Assert.Equal(before, File.ReadAllBytes(escaped));
        }

        [Theory]
        [InlineData("output.bes:payload", "alternate data stream")]
        [InlineData("NUL.bes", "reserved DOS device")]
        public void PatchFile_RejectsAlternateStreamsAndReservedDeviceNames(string outputName, string expected)
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = Path.Combine(root.Path, outputName);

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains(expected, result.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void PatchFile_RejectsSubstAliasIntoGameTree()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string gameRoot = Path.Combine(root.Path, "fake-game");
            string saveDirectory = Path.Combine(gameRoot, "savegames");
            Directory.CreateDirectory(Path.Combine(gameRoot, "data"));
            Directory.CreateDirectory(saveDirectory);
            File.WriteAllBytes(Path.Combine(gameRoot, "BEA.exe"), [0x4D, 0x5A]);

            char driveLetter = FindFreeDriveLetter();
            (int createExitCode, string createOutput) = RunSubst(driveLetter, saveDirectory, remove: false);
            Assert.True(createExitCode == 0, createOutput);
            try
            {
                string output = $"{driveLetter}:\\output.bes";

                PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

                Assert.False(result.Success);
                Assert.Contains("game folder", result.Message, StringComparison.OrdinalIgnoreCase);
                Assert.False(File.Exists(Path.Combine(saveDirectory, "output.bes")));
            }
            finally
            {
                (int removeExitCode, string removeOutput) = RunSubst(driveLetter, target: null, remove: true);
                Assert.True(removeExitCode == 0, removeOutput);
            }
        }

        [Fact]
        public void PatchConfiguration_RejectsOutputAliasOfCopySource()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bea");
            string copySource = root.WriteValidFile("copy-source.bea");
            string output = Path.Combine(root.Path, "output.bea");
            byte[] before = File.ReadAllBytes(copySource);
            Assert.True(
                CreateHardLink(output, copySource, IntPtr.Zero),
                new Win32Exception(Marshal.GetLastWin32Error()).Message);

            PatchResult result = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
            {
                InputPath = input,
                OutputPath = output,
                CopyOptionsFromPath = copySource,
                CopyOptionsTail = true
            });

            Assert.False(result.Success);
            Assert.Contains("hardlink", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(before, File.ReadAllBytes(copySource));
        }

        [Theory]
        [InlineData(@"\\server\share\output.bes", "UNC")]
        [InlineData(@"C:output.bes", "drive-relative")]
        public void PatchFile_RejectsAmbiguousOrNetworkOutputPaths(string output, string expected)
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains(expected, result.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void PatchFile_RejectsDeviceOutputPath()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = @"\\?\" + Path.Combine(root.Path, "output.bes");

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.False(result.Success);
            Assert.Contains("device path", result.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void PatchFile_AtomicallyReplacesDistinctOutputAndPreservesInput()
        {
            using TempMutationRoot root = TempMutationRoot.Create();
            string input = root.WriteValidFile("input.bes");
            string output = root.WriteValidFile("output.bes", fill: 0x7A);
            byte[] before = File.ReadAllBytes(input);

            PatchResult result = CreateNoOpPatcher().PatchFile(input, output);

            Assert.True(result.Success, result.Message);
            Assert.Equal(before, File.ReadAllBytes(input));
            Assert.Equal(before, File.ReadAllBytes(output));
            Assert.Empty(Directory.GetFiles(root.Path, ".onslaught-*.tmp"));
        }

        private static BesFilePatcher CreateNoOpPatcher() => new()
        {
            PatchNodes = false,
            PatchLinks = false,
            PatchGoodies = false,
            PatchKills = false
        };

        private static char FindFreeDriveLetter()
        {
            for (char drive = 'Z'; drive >= 'P'; drive--)
            {
                if (!Directory.Exists($"{drive}:\\"))
                    return drive;
            }

            throw new InvalidOperationException("No free drive letter is available for the SUBST safety test.");
        }

        private static (int ExitCode, string Output) RunSubst(char driveLetter, string? target, bool remove)
        {
            var startInfo = new ProcessStartInfo
            {
                FileName = "subst.exe",
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            startInfo.ArgumentList.Add($"{driveLetter}:");
            startInfo.ArgumentList.Add(remove ? "/D" : target ?? string.Empty);

            using Process process = Process.Start(startInfo)
                ?? throw new InvalidOperationException("Could not start subst.exe.");
            string standardOutput = process.StandardOutput.ReadToEnd();
            string standardError = process.StandardError.ReadToEnd();
            process.WaitForExit();
            return (process.ExitCode, standardOutput + standardError);
        }

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool CreateHardLink(
            string lpFileName,
            string lpExistingFileName,
            IntPtr lpSecurityAttributes);

        private sealed class TempMutationRoot : IDisposable
        {
            private TempMutationRoot(string path)
            {
                Path = path;
            }

            internal string Path { get; }

            internal static TempMutationRoot Create()
            {
                string path = System.IO.Path.Combine(
                    System.IO.Path.GetTempPath(),
                    "onslaught-file-mutation-tests",
                    Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(path);
                return new TempMutationRoot(path);
            }

            internal string WriteValidFile(string name, byte fill = 0)
            {
                string path = System.IO.Path.Combine(Path, name);
                byte[] bytes = Enumerable.Repeat(fill, BesFilePatcher.EXPECTED_FILE_SIZE).ToArray();
                BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(0, 2), BesFilePatcher.VERSION_WORD);
                File.WriteAllBytes(path, bytes);
                return path;
            }

            public void Dispose()
            {
                if (Directory.Exists(Path))
                    Directory.Delete(Path, recursive: true);
            }
        }
    }
}
