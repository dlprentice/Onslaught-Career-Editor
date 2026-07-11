using Microsoft.Win32.SafeHandles;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;

namespace Onslaught___Career_Editor
{
    internal static class FileMutationSafety
    {
        private const uint FileListDirectory = 0x0001;
        private const uint GenericRead = 0x80000000;
        private const uint FileFlagOpenReparsePoint = 0x00200000;
        private const uint FileFlagBackupSemantics = 0x02000000;
        private static readonly object s_authorizationKey = new();

        private static readonly HashSet<string> s_reservedDosNames = new(StringComparer.OrdinalIgnoreCase)
        {
            "CON", "PRN", "AUX", "NUL", "CLOCK$", "CONIN$", "CONOUT$",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
        };

        internal static StringComparison PathComparison => OperatingSystem.IsWindows()
            ? StringComparison.OrdinalIgnoreCase
            : StringComparison.Ordinal;

        internal static StringComparer PathComparer => OperatingSystem.IsWindows()
            ? StringComparer.OrdinalIgnoreCase
            : StringComparer.Ordinal;

        internal static string NormalizeLocalPath(string path, string label)
        {
            if (string.IsNullOrWhiteSpace(path))
                throw new ArgumentException($"{label} is required.", nameof(path));

            string trimmed = path.Trim();
            if (OperatingSystem.IsWindows())
            {
                if (trimmed.StartsWith(@"\\?\", StringComparison.Ordinal) ||
                    trimmed.StartsWith(@"\\.\", StringComparison.Ordinal) ||
                    trimmed.StartsWith(@"\??\", StringComparison.Ordinal))
                {
                    throw new InvalidOperationException($"{label} cannot use a Windows device path.");
                }

                if (Path.IsPathRooted(trimmed) && !Path.IsPathFullyQualified(trimmed))
                    throw new InvalidOperationException($"{label} cannot use a drive-relative path.");
            }

            string fullPath = Path.GetFullPath(trimmed);
            if (OperatingSystem.IsWindows())
            {
                if (fullPath.StartsWith(@"\\", StringComparison.Ordinal))
                    throw new InvalidOperationException($"{label} cannot use a UNC or network path.");

                if (fullPath.IndexOf(':', startIndex: 2) >= 0)
                    throw new InvalidOperationException($"{label} cannot use an alternate data stream.");

                RejectReservedDosNames(fullPath, label);
            }

            return fullPath;
        }

        internal static bool IsSameOrUnderRoot(string path, string root)
        {
            string normalizedPath = NormalizeForPrefix(path);
            string normalizedRoot = NormalizeForPrefix(root);
            return normalizedPath.StartsWith(normalizedRoot, PathComparison);
        }

        internal static bool AreLexicallySamePath(string left, string right)
        {
            return string.Equals(
                NormalizeLocalPath(left, "Input path"),
                NormalizeLocalPath(right, "Output path"),
                PathComparison);
        }

        internal static void RejectExistingReparseAncestors(string path, string label)
        {
            string fullPath = Path.GetFullPath(path);
            string? current = Directory.Exists(fullPath)
                ? fullPath
                : Path.GetDirectoryName(fullPath);

            while (!string.IsNullOrWhiteSpace(current))
            {
                if (Directory.Exists(current))
                    RejectReparsePoint(current, label);

                string? parent = Path.GetDirectoryName(current);
                if (string.Equals(parent, current, PathComparison))
                    break;

                current = parent;
            }
        }

        internal static void RejectReparsePoint(string path, string label)
        {
            FileAttributes attributes;
            try
            {
                attributes = File.GetAttributes(path);
            }
            catch (FileNotFoundException)
            {
                return;
            }
            catch (DirectoryNotFoundException)
            {
                return;
            }

            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException($"{label} cannot be a symbolic link, junction, or other reparse point.");
        }

        internal static void RejectMultipleHardLinks(string path, string label)
        {
            if (!OperatingSystem.IsWindows() || !File.Exists(path))
                return;

            WindowsFileIdentity identity = GetWindowsIdentity(path);
            if (identity.NumberOfLinks > 1)
                throw new InvalidOperationException($"{label} is hardlinked to another file; refusing to mutate a shared file identity.");
        }

        internal static void RejectOutputInGameTree(string outputPath)
        {
            string? current = Path.GetDirectoryName(Path.GetFullPath(outputPath));
            while (!string.IsNullOrWhiteSpace(current))
            {
                if (File.Exists(Path.Combine(current, "BEA.exe")) &&
                    Directory.Exists(Path.Combine(current, "data")))
                {
                    throw new InvalidOperationException(
                        "Output paths inside a Battle Engine Aquila game folder are blocked. Choose the app-owned patched-output folder or another non-game folder.");
                }

                string? parent = Path.GetDirectoryName(current);
                if (string.Equals(parent, current, PathComparison))
                    break;

                current = parent;
            }
        }

        internal static GuardedFileMutation Begin(
            string outputPath,
            params string?[] protectedInputPaths)
        {
            return new GuardedFileMutation(outputPath, authorization: null, protectedInputPaths);
        }

        internal static GuardedFileMutation BeginInAppOwnedProfile(
            string outputPath,
            AppOwnedProfileMutationAuthorization authorization,
            params string?[] protectedInputPaths)
        {
            authorization.EnsureUsable();
            return new GuardedFileMutation(outputPath, authorization, protectedInputPaths);
        }

        internal static FileStream CreateStagedFile(string path)
        {
            return new FileStream(
                path,
                new FileStreamOptions
                {
                    Mode = FileMode.CreateNew,
                    Access = FileAccess.ReadWrite,
                    Share = FileShare.Read,
                    Options = FileOptions.WriteThrough,
                });
        }

        internal static AppOwnedProfileMutationAuthorization AuthorizeAppOwnedProfileRoot(
            string profileRoot,
            string appOwnedProfilesRoot)
        {
            string normalizedProfileRoot = NormalizeLocalPath(profileRoot, "Generated profile root");
            string normalizedAppRoot = NormalizeLocalPath(appOwnedProfilesRoot, "App-owned profiles root");
            string canonicalAppRoot = NormalizeLocalPath(AppConfig.GetGameProfilesDir(), "Canonical app-owned profiles root");
            if (!string.Equals(normalizedAppRoot, canonicalAppRoot, PathComparison))
            {
                throw new InvalidOperationException(
                    "Safe-copy mutation requires the canonical app-owned GameProfiles root.");
            }

            DirectoryLockSet? appLocks = null;
            DirectoryLockSet? profileLocks = null;
            try
            {
                appLocks = LockDirectoryTree(normalizedAppRoot, "App-owned profiles root");
                RejectOutputInGameTree(Path.Combine(appLocks.PhysicalPath, ".onslaught-profile-root-probe"));

                profileLocks = LockDirectoryTree(normalizedProfileRoot, "Generated profile root");
                if (!IsSameOrUnderRoot(profileLocks.PhysicalPath, appLocks.PhysicalPath) ||
                    string.Equals(profileLocks.PhysicalPath, appLocks.PhysicalPath, PathComparison))
                {
                    throw new InvalidOperationException(
                        "Generated profile root must remain below the canonical app-owned GameProfiles root.");
                }

                AppOwnedProfileMutationAuthorization authorization = new(
                    appLocks,
                    profileLocks,
                    s_authorizationKey);
                appLocks = null;
                profileLocks = null;
                return authorization;
            }
            finally
            {
                profileLocks?.Dispose();
                appLocks?.Dispose();
            }
        }

        internal static WindowsFileIdentity GetWindowsIdentity(SafeFileHandle handle, string label)
        {
            if (!OperatingSystem.IsWindows())
                return default;

            if (!GetFileInformationByHandle(handle, out ByHandleFileInformation info))
                throw new IOException($"Could not inspect {label}. Win32 error: {Marshal.GetLastWin32Error()}");

            return new WindowsFileIdentity(
                info.VolumeSerialNumber,
                ((ulong)info.FileIndexHigh << 32) | info.FileIndexLow,
                info.NumberOfLinks,
                info.FileAttributes);
        }

        internal static DirectoryLockSet LockDirectoryTree(string directoryPath, string label)
        {
            string logicalPath = NormalizeLocalPath(directoryPath, label);
            if (!Directory.Exists(logicalPath))
                throw new DirectoryNotFoundException($"{label} does not exist.");

            RejectExistingReparseAncestors(logicalPath, label);
            if (!OperatingSystem.IsWindows())
                return new DirectoryLockSet(logicalPath, Array.Empty<SafeFileHandle>());

            using SafeFileHandle initialHandle = OpenDirectoryHandle(logicalPath, label);
            string physicalPath = GetFinalLocalPath(initialHandle, label);
            WindowsFileIdentity initialIdentity = GetWindowsIdentity(initialHandle, label);
            var handles = new List<SafeFileHandle>();
            try
            {
                foreach (string ancestor in EnumerateDirectoryAncestors(physicalPath))
                {
                    SafeFileHandle handle = OpenDirectoryHandle(ancestor, label);
                    string resolved = GetFinalLocalPath(handle, label);
                    if (!string.Equals(resolved, ancestor, PathComparison))
                    {
                        handle.Dispose();
                        throw new InvalidOperationException($"{label} changed identity while it was being secured.");
                    }

                    handles.Add(handle);
                }

                WindowsFileIdentity finalIdentity = GetWindowsIdentity(handles[^1], label);
                if (!initialIdentity.IsSameFile(finalIdentity) ||
                    !string.Equals(GetFinalLocalPath(initialHandle, label), physicalPath, PathComparison))
                {
                    throw new InvalidOperationException($"{label} changed identity while it was being secured.");
                }

                DirectoryLockSet result = new(physicalPath, handles);
                handles = null!;
                return result;
            }
            finally
            {
                if (handles is not null)
                {
                    foreach (SafeFileHandle handle in handles)
                        handle.Dispose();
                }
            }
        }

        internal static string EnsureDefaultOutputDirectory(string outputDirectory)
        {
            string normalizedOutputDirectory = NormalizeLocalPath(outputDirectory, "Output folder");
            string expectedDirectory = NormalizeLocalPath(AppConfig.GetPatchedOutputDir(), "App-owned patched-output folder");
            if (!string.Equals(normalizedOutputDirectory, expectedDirectory, PathComparison))
                throw new DirectoryNotFoundException("The selected output folder does not exist.");

            var missingNames = new Stack<string>();
            string? existingAncestor = normalizedOutputDirectory;
            while (!string.IsNullOrWhiteSpace(existingAncestor) && !Directory.Exists(existingAncestor))
            {
                string name = Path.GetFileName(existingAncestor);
                if (string.IsNullOrWhiteSpace(name))
                    throw new DirectoryNotFoundException("The app-owned patched-output folder has no existing local ancestor.");

                missingNames.Push(name);
                existingAncestor = Path.GetDirectoryName(existingAncestor);
            }

            if (string.IsNullOrWhiteSpace(existingAncestor))
                throw new DirectoryNotFoundException("The app-owned patched-output folder has no existing local ancestor.");

            var heldLocks = new List<DirectoryLockSet>();
            try
            {
                DirectoryLockSet currentLocks = LockDirectoryTree(existingAncestor, "App-owned output ancestor");
                heldLocks.Add(currentLocks);
                string currentPhysicalPath = currentLocks.PhysicalPath;
                RejectOutputInGameTree(Path.Combine(currentPhysicalPath, ".onslaught-output-root-probe"));

                while (missingNames.Count > 0)
                {
                    string nextPhysicalPath = Path.Combine(currentPhysicalPath, missingNames.Pop());
                    RejectReparsePoint(nextPhysicalPath, "App-owned output folder");
                    if (!Directory.Exists(nextPhysicalPath))
                        Directory.CreateDirectory(nextPhysicalPath);

                    RejectReparsePoint(nextPhysicalPath, "App-owned output folder");
                    DirectoryLockSet nextLocks = LockDirectoryTree(nextPhysicalPath, "App-owned output folder");
                    heldLocks.Add(nextLocks);
                    if (!string.Equals(nextLocks.PhysicalPath, Path.GetFullPath(nextPhysicalPath), PathComparison))
                        throw new InvalidOperationException("App-owned output folder resolved outside its expected local path.");

                    currentPhysicalPath = nextLocks.PhysicalPath;
                    RejectOutputInGameTree(Path.Combine(currentPhysicalPath, ".onslaught-output-root-probe"));
                }

                return currentPhysicalPath;
            }
            finally
            {
                for (int index = heldLocks.Count - 1; index >= 0; index--)
                    heldLocks[index].Dispose();
            }
        }

        private static SafeFileHandle OpenDirectoryHandle(string path, string label)
        {
            SafeFileHandle handle = CreateFileW(
                path,
                FileListDirectory,
                FileShare.Read | FileShare.Write,
                IntPtr.Zero,
                FileMode.Open,
                FileFlagBackupSemantics,
                IntPtr.Zero);
            if (handle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                handle.Dispose();
                throw new IOException($"Could not secure {label}. Win32 error: {error}", new Win32Exception(error));
            }

            return handle;
        }

        internal static SafeFileHandle OpenNoFollowReadHandle(string path, string label)
        {
            SafeFileHandle handle = CreateFileW(
                path,
                GenericRead,
                FileShare.Read,
                IntPtr.Zero,
                FileMode.Open,
                FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (handle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                handle.Dispose();
                throw new IOException($"Could not secure {label}. Win32 error: {error}", new Win32Exception(error));
            }

            return handle;
        }

        internal static string GetFinalLocalPath(SafeFileHandle handle, string label)
        {
            var buffer = new StringBuilder(512);
            uint length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
            if (length == 0)
                throw new IOException($"Could not resolve {label}. Win32 error: {Marshal.GetLastWin32Error()}");

            if (length >= buffer.Capacity)
            {
                buffer.EnsureCapacity(checked((int)length + 1));
                length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
                if (length == 0 || length >= buffer.Capacity)
                    throw new IOException($"Could not resolve {label}. Win32 error: {Marshal.GetLastWin32Error()}");
            }

            string resolved = buffer.ToString();
            if (resolved.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException($"{label} resolves to a network path.");
            if (resolved.StartsWith(@"\\?\", StringComparison.Ordinal))
                resolved = resolved[4..];
            if (resolved.StartsWith(@"\??\", StringComparison.Ordinal))
                resolved = resolved[4..];
            if (resolved.StartsWith(@"\\", StringComparison.Ordinal) ||
                resolved.Length < 3 ||
                resolved[1] != ':' ||
                (resolved[2] != Path.DirectorySeparatorChar && resolved[2] != Path.AltDirectorySeparatorChar))
            {
                throw new InvalidOperationException($"{label} does not resolve to a local DOS drive path.");
            }

            return TrimDirectoryPath(NormalizeLocalPath(resolved, label));
        }

        private static IReadOnlyList<string> EnumerateDirectoryAncestors(string directoryPath)
        {
            var stack = new Stack<string>();
            DirectoryInfo? current = new(directoryPath);
            while (current is not null)
            {
                stack.Push(TrimDirectoryPath(current.FullName));
                current = current.Parent;
            }

            return stack.ToArray();
        }

        private static WindowsFileIdentity GetWindowsIdentity(string path)
        {
            using SafeFileHandle handle = File.OpenHandle(
                path,
                FileMode.Open,
                FileAccess.Read,
                FileShare.Read | FileShare.Delete);
            return GetWindowsIdentity(handle, "file identity");
        }

        private static string NormalizeForPrefix(string path)
        {
            return Path.GetFullPath(path)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                + Path.DirectorySeparatorChar;
        }

        private static string TrimDirectoryPath(string path)
        {
            string fullPath = Path.GetFullPath(path);
            string root = Path.GetPathRoot(fullPath) ?? string.Empty;
            return string.Equals(fullPath, root, PathComparison)
                ? root
                : fullPath.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        }

        private static void RejectReservedDosNames(string path, string label)
        {
            string root = Path.GetPathRoot(path) ?? string.Empty;
            string remainder = path[root.Length..];
            foreach (string component in remainder.Split(
                [Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar],
                StringSplitOptions.RemoveEmptyEntries))
            {
                string trimmed = component.TrimEnd(' ', '.');
                string stem = trimmed.Split('.', 2)[0];
                if (s_reservedDosNames.Contains(stem))
                    throw new InvalidOperationException($"{label} cannot use the reserved DOS device name '{stem}'.");
            }
        }

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern SafeFileHandle CreateFileW(
            string lpFileName,
            uint dwDesiredAccess,
            FileShare dwShareMode,
            IntPtr lpSecurityAttributes,
            FileMode dwCreationDisposition,
            uint dwFlagsAndAttributes,
            IntPtr hTemplateFile);

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern uint GetFinalPathNameByHandleW(
            SafeFileHandle hFile,
            StringBuilder lpszFilePath,
            uint cchFilePath,
            uint dwFlags);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool GetFileInformationByHandle(
            SafeFileHandle hFile,
            out ByHandleFileInformation lpFileInformation);

        [StructLayout(LayoutKind.Sequential)]
        private struct ByHandleFileInformation
        {
            public uint FileAttributes;
            public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
            public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
            public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
            public uint VolumeSerialNumber;
            public uint FileSizeHigh;
            public uint FileSizeLow;
            public uint NumberOfLinks;
            public uint FileIndexHigh;
            public uint FileIndexLow;
        }

        internal sealed class DirectoryLockSet : IDisposable
        {
            private readonly IReadOnlyList<SafeFileHandle> _handles;

            internal DirectoryLockSet(string physicalPath, IReadOnlyList<SafeFileHandle> handles)
            {
                PhysicalPath = physicalPath;
                _handles = handles;
            }

            internal string PhysicalPath { get; }

            public void Dispose()
            {
                for (int index = _handles.Count - 1; index >= 0; index--)
                    _handles[index].Dispose();
            }
        }

        internal sealed class AppOwnedProfileMutationAuthorization : IDisposable
        {
            private readonly DirectoryLockSet _appRootLocks;
            private readonly DirectoryLockSet _profileRootLocks;
            private bool _disposed;

            internal AppOwnedProfileMutationAuthorization(
                DirectoryLockSet appRootLocks,
                DirectoryLockSet profileRootLocks,
                object authorizationKey)
            {
                if (!ReferenceEquals(authorizationKey, s_authorizationKey))
                    throw new InvalidOperationException("App-owned profile authorization can only be minted by the validated factory.");

                _appRootLocks = appRootLocks;
                _profileRootLocks = profileRootLocks;
            }

            internal string PhysicalProfileRoot => _profileRootLocks.PhysicalPath;

            internal void EnsureUsable()
            {
                ObjectDisposedException.ThrowIf(_disposed, this);
            }

            public void Dispose()
            {
                if (_disposed)
                    return;

                _disposed = true;
                _profileRootLocks.Dispose();
                _appRootLocks.Dispose();
            }
        }
    }

    internal readonly record struct WindowsFileIdentity(
        uint VolumeSerialNumber,
        ulong FileIndex,
        uint NumberOfLinks,
        uint Attributes)
    {
        internal bool IsSameFile(WindowsFileIdentity other) =>
            VolumeSerialNumber == other.VolumeSerialNumber && FileIndex == other.FileIndex;

        internal bool IsReparsePoint =>
            ((FileAttributes)Attributes & FileAttributes.ReparsePoint) != 0;
    }

    internal sealed class GuardedFileMutation : IDisposable
    {
        private readonly Dictionary<string, ProtectedInput> _inputs = new(FileMutationSafety.PathComparer);
        private readonly FileMutationSafety.AppOwnedProfileMutationAuthorization? _authorization;
        private FileMutationSafety.DirectoryLockSet? _outputDirectoryLocks;
        private string _physicalOutputPath = string.Empty;
        private bool _committed;

        internal GuardedFileMutation(
            string outputPath,
            FileMutationSafety.AppOwnedProfileMutationAuthorization? authorization,
            IReadOnlyList<string?> protectedInputPaths)
        {
            OutputPath = FileMutationSafety.NormalizeLocalPath(outputPath, "Output path");
            _authorization = authorization;

            try
            {
                string? outputDirectory = Path.GetDirectoryName(OutputPath);
                if (string.IsNullOrWhiteSpace(outputDirectory))
                    throw new DirectoryNotFoundException("The selected output folder does not exist.");

                string directoryToLock = Directory.Exists(outputDirectory)
                    ? outputDirectory
                    : FileMutationSafety.EnsureDefaultOutputDirectory(outputDirectory);
                _outputDirectoryLocks = FileMutationSafety.LockDirectoryTree(directoryToLock, "Output folder");
                _physicalOutputPath = Path.Combine(_outputDirectoryLocks.PhysicalPath, Path.GetFileName(OutputPath));
                ValidateOutputLocation();

                foreach (string? candidate in protectedInputPaths)
                {
                    if (string.IsNullOrWhiteSpace(candidate))
                        continue;

                    string path = FileMutationSafety.NormalizeLocalPath(candidate, "Protected input path");
                    if (_inputs.ContainsKey(path))
                        continue;
                    if (!File.Exists(path))
                        throw new FileNotFoundException("Protected input file was not found.", path);

                    FileMutationSafety.RejectReparsePoint(path, "Protected input file");
                    FileStream stream = new(
                        path,
                        new FileStreamOptions
                        {
                            Mode = FileMode.Open,
                            Access = FileAccess.Read,
                            Share = FileShare.Read,
                            Options = FileOptions.SequentialScan,
                        });
                    WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(stream.SafeFileHandle, "protected input identity");
                    _inputs.Add(path, new ProtectedInput(stream, identity));
                }

                if (_inputs.Count == 0)
                    throw new InvalidOperationException("At least one protected input file is required.");

                ValidateDestination();
            }
            catch
            {
                Dispose();
                throw;
            }
        }

        internal string OutputPath { get; }

        internal byte[] ReadAllBytes(string path)
        {
            string normalized = FileMutationSafety.NormalizeLocalPath(path, "Protected input path");
            if (!_inputs.TryGetValue(normalized, out ProtectedInput? input))
                throw new InvalidOperationException("The requested file is not held by this guarded transaction.");

            return ReadAllBytes(input.Stream, "Protected input");
        }

        internal void Commit(byte[] bytes, Action<string>? beforeCommittedOpen = null)
        {
            if (_committed)
                throw new InvalidOperationException("This guarded transaction has already committed.");

            string directory = Path.GetDirectoryName(_physicalOutputPath)!;
            string tempPath = Path.Combine(directory, $".onslaught-{Guid.NewGuid():N}.tmp");
            bool tempEntryExists = false;
            try
            {
                using FileStream temp = FileMutationSafety.CreateStagedFile(tempPath);
                tempEntryExists = true;
                temp.Write(bytes);
                temp.Flush(flushToDisk: true);

                WindowsFileIdentity tempIdentity = FileMutationSafety.GetWindowsIdentity(temp.SafeFileHandle, "staged output identity");
                if (OperatingSystem.IsWindows() && tempIdentity.NumberOfLinks != 1)
                    throw new InvalidOperationException("Staged output unexpectedly shares a file identity.");

                byte[] stagedReadback = ReadAllBytes(temp, "Staged output");
                if (stagedReadback.Length != bytes.Length ||
                    !CryptographicOperations.FixedTimeEquals(SHA256.HashData(stagedReadback), SHA256.HashData(bytes)))
                {
                    throw new IOException("Staged output verification failed after commit.");
                }

                ValidateDestination();
                temp.Dispose();
                File.Move(tempPath, _physicalOutputPath, overwrite: true);
                tempEntryExists = false;
                beforeCommittedOpen?.Invoke(_physicalOutputPath);

                using SafeFileHandle committedHandle = FileMutationSafety.OpenNoFollowReadHandle(
                    _physicalOutputPath,
                    "committed output file");
                WindowsFileIdentity committedIdentity = FileMutationSafety.GetWindowsIdentity(committedHandle, "committed output identity");
                if (OperatingSystem.IsWindows() && committedIdentity.IsReparsePoint)
                    throw new IOException("Committed output is a symbolic link, junction, or other reparse point.");
                if (OperatingSystem.IsWindows() && !tempIdentity.IsSameFile(committedIdentity))
                    throw new IOException("Committed output identity does not match the staged file.");
                if (OperatingSystem.IsWindows() && committedIdentity.NumberOfLinks != 1)
                    throw new IOException("Committed output unexpectedly shares a file identity.");
                if (OperatingSystem.IsWindows() && _inputs.Values.Any(input => input.Identity.IsSameFile(committedIdentity)))
                    throw new IOException("Committed output aliases a protected input file.");

                string committedPhysicalPath = FileMutationSafety.GetFinalLocalPath(
                    committedHandle,
                    "committed output file");
                string? committedParent = Path.GetDirectoryName(committedPhysicalPath);
                if (string.IsNullOrWhiteSpace(committedParent) ||
                    !string.Equals(
                        committedParent.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                        _outputDirectoryLocks!.PhysicalPath.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                        FileMutationSafety.PathComparison))
                {
                    throw new IOException("Committed output resolved outside the locked physical output folder.");
                }

                using FileStream committed = new(committedHandle, FileAccess.Read);
                byte[] readback = ReadAllBytes(committed, "Committed output");
                if (readback.Length != bytes.Length ||
                    !CryptographicOperations.FixedTimeEquals(SHA256.HashData(readback), SHA256.HashData(bytes)))
                {
                    throw new IOException("Atomic output verification failed after commit.");
                }

                _committed = true;
            }
            finally
            {
                if (tempEntryExists && File.Exists(tempPath))
                    File.Delete(tempPath);
            }
        }

        public void Dispose()
        {
            foreach (ProtectedInput input in _inputs.Values)
                input.Stream.Dispose();
            _inputs.Clear();
            _outputDirectoryLocks?.Dispose();
            _outputDirectoryLocks = null;
        }

        private void ValidateDestination()
        {
            ValidateOutputLocation();

            FileMutationSafety.RejectReparsePoint(_physicalOutputPath, "Output file");
            if (Directory.Exists(_physicalOutputPath))
                throw new InvalidOperationException("The selected output path is a directory.");
            if (!File.Exists(_physicalOutputPath))
                return;

            using SafeFileHandle outputHandle = File.OpenHandle(
                _physicalOutputPath,
                FileMode.Open,
                FileAccess.Read,
                FileShare.Read);
            WindowsFileIdentity outputIdentity = FileMutationSafety.GetWindowsIdentity(outputHandle, "output identity");
            if (OperatingSystem.IsWindows() && outputIdentity.NumberOfLinks > 1)
                throw new InvalidOperationException("Output file is hardlinked to another file; refusing to replace a shared file identity.");

            if (OperatingSystem.IsWindows() && _inputs.Values.Any(input => input.Identity.IsSameFile(outputIdentity)))
                throw new InvalidOperationException("Refusing to patch in place. Output file must be different from every protected input file; aliased writes are also blocked.");

            if (_inputs.Keys.Any(path => string.Equals(path, OutputPath, FileMutationSafety.PathComparison)))
                throw new InvalidOperationException("Refusing to patch in place. Output file must be different from every protected input file.");
        }

        private void ValidateOutputLocation()
        {
            _authorization?.EnsureUsable();
            if (_authorization is null)
            {
                FileMutationSafety.RejectOutputInGameTree(_physicalOutputPath);
                return;
            }

            if (!FileMutationSafety.IsSameOrUnderRoot(_physicalOutputPath, _authorization.PhysicalProfileRoot))
                throw new InvalidOperationException("Output path must remain inside the verified app-owned profile root.");
        }

        private static byte[] ReadAllBytes(FileStream stream, string label)
        {
            if (stream.Length > int.MaxValue)
                throw new IOException($"{label} is too large to read safely.");

            byte[] bytes = new byte[checked((int)stream.Length)];
            stream.Position = 0;
            stream.ReadExactly(bytes);
            return bytes;
        }

        private sealed record ProtectedInput(FileStream Stream, WindowsFileIdentity Identity);
    }
}
