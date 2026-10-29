// SPDX-License-Identifier: GPL-3.0-only
using Microsoft.Win32.SafeHandles;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;

namespace OnslaughtToolkit.Companion.Files
{
    /// <summary>
    /// The companion's file-safety primitives: plain-word refusals for links and Windows path forms, folders locked
    /// with their ancestors, no-follow opens, the refusal of output inside a game folder, and the new-file-only
    /// <see cref="GuardedFileMutation"/> that Windows copies publish through.
    /// </summary>
    internal static class FileMutationSafety
    {
        private const uint FileListDirectory = 0x0001;
        private const uint FileReadAttributes = 0x0080;
        private const uint DeleteAccess = 0x00010000;
        private const uint GenericRead = 0x80000000;
        private const uint GenericWrite = 0x40000000;
        private const uint FileFlagOpenReparsePoint = 0x00200000;
        private const uint FileFlagDeleteOnClose = 0x04000000;
        private const uint FileFlagWriteThrough = 0x80000000;
        private const uint FileFlagBackupSemantics = 0x02000000;
        private const uint FileAttributeTemporary = 0x00000100;
        private const int FileDispositionInfoEx = 21;
        private const uint FileDispositionFlagDelete = 0x00000001;
        private const uint FileDispositionFlagPosixSemantics = 0x00000002;

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

        internal const string FileCannotUseLink = "That file cannot use a shortcut or link.";
        internal const string FolderCannotUseLink = "That folder cannot use a shortcut or link.";
        internal const string FileOrFolderRequired = "A file or folder is required.";
        internal const string FileCannotUseDeviceLocation = "That file cannot use a Windows device location.";
        internal const string FileCannotUseDriveRelativeLocation = "That file cannot use a drive-relative location.";
        internal const string FileCannotUseNetworkLocation = "That file cannot use a UNC or network location.";
        internal const string FileCannotUseAlternateStream = "That file cannot use an alternate data stream.";
        internal const string FileCannotUseReservedDevice = "That file cannot use a reserved device name.";
        internal const string FileResolvesToNetwork = "That file resolves to a network location.";
        internal const string FileDoesNotResolveToLocalDrive = "That file does not resolve to a local drive.";
        internal const string OutputInsideGameFolder =
            "Output files inside a Battle Engine Aquila game folder are blocked. Choose the output folder or another non-game folder.";
        internal const string FolderChangedIdentity = "That folder changed identity while it was being secured.";
        internal const string FolderChangedIdentityBeforeGuard = "That folder changed identity before its mutation guard was created.";
        internal const string FileCouldNotBeInspected = "That file could not be inspected.";
        internal const string FileCouldNotBeSecured = "That file could not be secured.";
        internal const string FileCouldNotBeResolved = "That file could not be resolved.";
        internal const string FolderCouldNotBeGuarded = "That folder could not be guarded against in-place change.";
        internal const string FolderGuardCouldNotBeCreated = "That folder guard could not be created.";
        internal const string FolderGuardEscaped = "That folder guard escaped its held folder.";
        internal const string FileTooLargeToRead = "That file is too large to read safely.";
        internal const string StagedOutputCouldNotBeCreated = "That staged output file could not be created.";
        internal const string StagedOutputQuarantineCouldNotBeUpdated = "That staged output quarantine could not be updated.";

        internal static string NormalizeLocalPath(string path, string label)
        {
            if (string.IsNullOrWhiteSpace(path))
                throw new ArgumentException(FileOrFolderRequired, nameof(path));

            string trimmed = path.Trim();
            if (OperatingSystem.IsWindows())
            {
                if (trimmed.StartsWith(@"\\?\", StringComparison.Ordinal) ||
                    trimmed.StartsWith(@"\\.\", StringComparison.Ordinal) ||
                    trimmed.StartsWith(@"\??\", StringComparison.Ordinal))
                {
                    throw new InvalidOperationException(FileCannotUseDeviceLocation);
                }

                if (Path.IsPathRooted(trimmed) && !Path.IsPathFullyQualified(trimmed))
                    throw new InvalidOperationException(FileCannotUseDriveRelativeLocation);
            }

            string fullPath = Path.GetFullPath(trimmed);
            if (OperatingSystem.IsWindows())
            {
                if (fullPath.StartsWith(@"\\", StringComparison.Ordinal))
                    throw new InvalidOperationException(FileCannotUseNetworkLocation);

                if (fullPath.IndexOf(':', startIndex: 2) >= 0)
                    throw new InvalidOperationException(FileCannotUseAlternateStream);

                RejectReservedDosNames(fullPath, label);
            }

            return fullPath;
        }

        internal static bool AreLexicallySamePath(string left, string right)
        {
            return string.Equals(
                NormalizeLocalPath(left, "Input file"),
                NormalizeLocalPath(right, "Output file"),
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
            {
                throw new InvalidOperationException(
                    (attributes & FileAttributes.Directory) != 0
                        ? FolderCannotUseLink
                        : FileCannotUseLink);
            }
        }

        internal static void RejectOutputInGameTree(string outputPath)
        {
            string? current = Path.GetDirectoryName(Path.GetFullPath(outputPath));
            while (!string.IsNullOrWhiteSpace(current))
            {
                if (File.Exists(Path.Combine(current, "BEA.exe")) &&
                    Directory.Exists(Path.Combine(current, "data")))
                {
                    throw new InvalidOperationException(OutputInsideGameFolder);
                }

                string? parent = Path.GetDirectoryName(current);
                if (string.Equals(parent, current, PathComparison))
                    break;

                current = parent;
            }
        }

        internal static GuardedFileMutation BeginGeneratedVacant(
            string outputPath,
            params string?[] protectedInputPaths)
        {
            return new GuardedFileMutation(outputPath, protectedInputPaths);
        }

        internal static FileStream CreateStagedFile(
            string path,
            Action<string>? afterCreateForTest = null)
        {
            if (!OperatingSystem.IsWindows())
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

            SafeFileHandle handle = CreateFileW(
                path,
                GenericRead | GenericWrite | DeleteAccess | FileReadAttributes,
                FileShare.Read,
                IntPtr.Zero,
                FileMode.CreateNew,
                FileFlagWriteThrough | FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (handle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                handle.Dispose();
                throw new IOException(
                    StagedOutputCouldNotBeCreated,
                    new Win32Exception(error));
            }

            FileStream? stream = null;
            try
            {
                stream = new FileStream(handle, FileAccess.ReadWrite);
                handle = null!;
                afterCreateForTest?.Invoke(path);
                SetFileDeleteDisposition(stream.SafeFileHandle, delete: true);
                WindowsFileIdentity identity = GetWindowsIdentity(
                    stream.SafeFileHandle,
                    "staged output quarantine");
                if (OperatingSystem.IsWindows() && identity.NumberOfLinks != 0)
                {
                    throw new InvalidOperationException(
                        "Staged output gained an alias before its content was written.");
                }
                return stream;
            }
            catch
            {
                stream?.Dispose();
                throw;
            }
            finally
            {
                handle?.Dispose();
            }
        }

        internal static void ReleaseStagedFileQuarantine(FileStream stream)
        {
            ArgumentNullException.ThrowIfNull(stream);
            SetFileDeleteDisposition(stream.SafeFileHandle, delete: false);
        }

        internal static WindowsFileIdentity GetWindowsIdentity(SafeFileHandle handle, string label)
        {
            if (!OperatingSystem.IsWindows())
                return default;

            if (!GetFileInformationByHandle(handle, out ByHandleFileInformation info))
                throw new IOException(FileCouldNotBeInspected, new Win32Exception(Marshal.GetLastWin32Error()));

            return new WindowsFileIdentity(
                info.VolumeSerialNumber,
                ((ulong)info.FileIndexHigh << 32) | info.FileIndexLow,
                info.NumberOfLinks,
                info.FileAttributes);
        }

        internal static DirectoryLockSet LockDirectoryTree(
            string directoryPath,
            string label,
            Action? beforeFirstOpenForTest = null,
            bool guardTargetMutation = false)
        {
            string logicalPath = NormalizeLocalPath(directoryPath, label);
            if (!Directory.Exists(logicalPath))
                throw new DirectoryNotFoundException("That folder could not be found.");

            if (!OperatingSystem.IsWindows())
            {
                RejectExistingReparseAncestors(logicalPath, label);
                return new DirectoryLockSet(
                    logicalPath,
                    Array.Empty<SafeFileHandle>(),
                    default,
                    mutationSentinel: null,
                    mutationSentinelPath: null);
            }

            var handles = new List<SafeFileHandle>();
            try
            {
                beforeFirstOpenForTest?.Invoke();

                SafeFileHandle? logicalTargetHandle = null;
                string? previousPhysicalComponent = null;
                foreach (string logicalComponent in EnumerateDirectoryAncestors(logicalPath))
                {
                    SafeFileHandle handle = OpenDirectoryHandle(logicalComponent, label);
                    WindowsFileIdentity identity = GetWindowsIdentity(handle, label);
                    if (identity.IsReparsePoint)
                    {
                        handle.Dispose();
                        throw new InvalidOperationException(FolderCannotUseLink);
                    }

                    string resolved = GetFinalLocalPath(handle, label);
                    if (previousPhysicalComponent is not null &&
                        !string.Equals(
                            Path.GetDirectoryName(resolved),
                            previousPhysicalComponent,
                            PathComparison))
                    {
                        handle.Dispose();
                        throw new InvalidOperationException(FolderChangedIdentity);
                    }

                    handles.Add(handle);
                    logicalTargetHandle = handle;
                    previousPhysicalComponent = resolved;
                }

                if (logicalTargetHandle is null)
                    throw new DirectoryNotFoundException("That folder could not be found.");

                string physicalPath = GetFinalLocalPath(logicalTargetHandle, label);
                WindowsFileIdentity initialIdentity = GetWindowsIdentity(logicalTargetHandle, label);
                foreach (string ancestor in EnumerateDirectoryAncestors(physicalPath))
                {
                    SafeFileHandle handle = OpenDirectoryHandle(ancestor, label);
                    WindowsFileIdentity identity = GetWindowsIdentity(handle, label);
                    if (identity.IsReparsePoint)
                    {
                        handle.Dispose();
                        throw new InvalidOperationException(FolderCannotUseLink);
                    }

                    string resolved = GetFinalLocalPath(handle, label);
                    if (!string.Equals(resolved, ancestor, PathComparison))
                    {
                        handle.Dispose();
                        throw new InvalidOperationException(FolderChangedIdentity);
                    }

                    handles.Add(handle);
                }

                WindowsFileIdentity finalIdentity = GetWindowsIdentity(handles[^1], label);
                if (!initialIdentity.IsSameFile(finalIdentity) ||
                    !string.Equals(GetFinalLocalPath(logicalTargetHandle, label), physicalPath, PathComparison))
                {
                    throw new InvalidOperationException(FolderChangedIdentity);
                }

                (SafeFileHandle Handle, string Path)? mutationSentinel = guardTargetMutation
                    ? CreateDirectoryMutationSentinel(
                        physicalPath,
                        handles[^1],
                        label)
                    : null;
                DirectoryLockSet result = new(
                    physicalPath,
                    handles,
                    finalIdentity,
                    mutationSentinel?.Handle,
                    mutationSentinel?.Path);
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

        private static SafeFileHandle OpenDirectoryHandle(string path, string label)
        {
            SafeFileHandle handle = CreateFileW(
                path,
                FileListDirectory,
                FileShare.Read | FileShare.Write,
                IntPtr.Zero,
                FileMode.Open,
                FileFlagBackupSemantics | FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (handle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                handle.Dispose();
                throw new IOException(FileCouldNotBeSecured, new Win32Exception(error));
            }

            return handle;
        }

        private static (SafeFileHandle Handle, string Path) CreateDirectoryMutationSentinel(
            string physicalPath,
            SafeFileHandle relaxedTargetHandle,
            string label)
        {
            using SafeFileHandle strictHandle = CreateFileW(
                physicalPath,
                FileListDirectory,
                FileShare.Read,
                IntPtr.Zero,
                FileMode.Open,
                FileFlagBackupSemantics | FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (strictHandle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                throw new IOException(
                    FolderCouldNotBeGuarded,
                    new Win32Exception(error));
            }

            WindowsFileIdentity strictIdentity = GetWindowsIdentity(strictHandle, label);
            WindowsFileIdentity relaxedIdentity = GetWindowsIdentity(relaxedTargetHandle, label);
            if (strictIdentity.IsReparsePoint ||
                !strictIdentity.IsSameFile(relaxedIdentity) ||
                !string.Equals(
                    GetFinalLocalPath(strictHandle, label),
                    physicalPath,
                    PathComparison))
            {
                throw new InvalidOperationException(
                    FolderChangedIdentityBeforeGuard);
            }

            string sentinelPath = Path.Combine(
                physicalPath,
                $".onslaught-directory-guard-{Guid.NewGuid():N}.tmp");
            SafeFileHandle sentinel = CreateFileW(
                sentinelPath,
                GenericRead | GenericWrite | DeleteAccess | FileReadAttributes,
                FileShare.Read,
                IntPtr.Zero,
                FileMode.CreateNew,
                FileAttributeTemporary | FileFlagDeleteOnClose | FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (sentinel.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                sentinel.Dispose();
                throw new IOException(
                    FolderGuardCouldNotBeCreated,
                    new Win32Exception(error));
            }

            try
            {
                WindowsFileIdentity sentinelIdentity = GetWindowsIdentity(
                    sentinel,
                    $"{label} mutation guard");
                if (sentinelIdentity.IsReparsePoint ||
                    sentinelIdentity.NumberOfLinks != 1 ||
                    !string.Equals(
                        GetFinalLocalPath(sentinel, $"{label} mutation guard"),
                        sentinelPath,
                        PathComparison))
                {
                    throw new InvalidOperationException(
                        FolderGuardEscaped);
                }
                return (sentinel, sentinelPath);
            }
            catch
            {
                sentinel.Dispose();
                throw;
            }
        }

        internal static SafeFileHandle OpenNoFollowReadHandle(
            string path,
            string label,
            bool allowDeleteShare = false,
            bool allowWriteShare = false)
        {
            FileShare share = FileShare.Read |
                (allowDeleteShare ? FileShare.Delete : 0) |
                (allowWriteShare ? FileShare.Write : 0);
            if (!OperatingSystem.IsWindows())
            {
                RejectReparsePoint(path, label);
                return File.OpenHandle(
                    path,
                    FileMode.Open,
                    FileAccess.Read,
                    share);
            }

            SafeFileHandle handle = CreateFileW(
                path,
                GenericRead,
                share,
                IntPtr.Zero,
                FileMode.Open,
                FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (handle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                handle.Dispose();
                throw new IOException(FileCouldNotBeSecured, new Win32Exception(error));
            }

            return handle;
        }

        internal static string GetFinalLocalPath(SafeFileHandle handle, string label)
        {
            var buffer = new StringBuilder(512);
            uint length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
            if (length == 0)
                throw new IOException(FileCouldNotBeResolved, new Win32Exception(Marshal.GetLastWin32Error()));

            if (length >= buffer.Capacity)
            {
                buffer.EnsureCapacity(checked((int)length + 1));
                length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
                if (length == 0 || length >= buffer.Capacity)
                    throw new IOException(FileCouldNotBeResolved, new Win32Exception(Marshal.GetLastWin32Error()));
            }

            string resolved = buffer.ToString();
            if (resolved.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException(FileResolvesToNetwork);
            if (resolved.StartsWith(@"\\?\", StringComparison.Ordinal))
                resolved = resolved[4..];
            if (resolved.StartsWith(@"\??\", StringComparison.Ordinal))
                resolved = resolved[4..];
            if (resolved.StartsWith(@"\\", StringComparison.Ordinal) ||
                resolved.Length < 3 ||
                resolved[1] != ':' ||
                (resolved[2] != Path.DirectorySeparatorChar && resolved[2] != Path.AltDirectorySeparatorChar))
            {
                throw new InvalidOperationException(FileDoesNotResolveToLocalDrive);
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

        private static void SetFileDeleteDisposition(
            SafeFileHandle handle,
            bool delete)
        {
            if (!OperatingSystem.IsWindows())
                return;

            uint flags = delete
                ? FileDispositionFlagDelete | FileDispositionFlagPosixSemantics
                : 0;
            byte[] buffer = BitConverter.GetBytes(flags);
            IntPtr nativeBuffer = Marshal.AllocHGlobal(buffer.Length);
            try
            {
                Marshal.Copy(buffer, 0, nativeBuffer, buffer.Length);
                if (!SetFileInformationByHandle(
                        handle,
                        FileDispositionInfoEx,
                        nativeBuffer,
                        (uint)buffer.Length))
                {
                    int error = Marshal.GetLastWin32Error();
                    throw new IOException(
                        StagedOutputQuarantineCouldNotBeUpdated,
                        new Win32Exception(error));
                }
            }
            finally
            {
                Marshal.FreeHGlobal(nativeBuffer);
            }
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
                    throw new InvalidOperationException(FileCannotUseReservedDevice);
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

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool SetFileInformationByHandle(
            SafeFileHandle hFile,
            int fileInformationClass,
            IntPtr lpFileInformation,
            uint dwBufferSize);

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
            private SafeFileHandle? _mutationSentinel;
            private readonly string? _mutationSentinelPath;

            internal DirectoryLockSet(
                string physicalPath,
                IReadOnlyList<SafeFileHandle> handles,
                WindowsFileIdentity identity,
                SafeFileHandle? mutationSentinel,
                string? mutationSentinelPath)
            {
                PhysicalPath = physicalPath;
                _handles = handles;
                Identity = identity;
                _mutationSentinel = mutationSentinel;
                _mutationSentinelPath = mutationSentinelPath;
            }

            internal string PhysicalPath { get; }

            internal WindowsFileIdentity Identity { get; }

            internal void ReleaseMutationSentinelIfDirectoryNonEmpty()
            {
                if (_mutationSentinel is null || string.IsNullOrWhiteSpace(_mutationSentinelPath))
                    return;
                if (!Directory.EnumerateFileSystemEntries(PhysicalPath)
                        .Any(path => !string.Equals(
                            path,
                            _mutationSentinelPath,
                            PathComparison)))
                {
                    return;
                }

                _mutationSentinel.Dispose();
                _mutationSentinel = null;
            }

            public void Dispose()
            {
                for (int index = _handles.Count - 1; index >= 0; index--)
                    _handles[index].Dispose();
                _mutationSentinel?.Dispose();
                _mutationSentinel = null;
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
        private FileMutationSafety.DirectoryLockSet? _outputDirectoryLocks;
        private FileStream? _committedStream;
        private string _physicalOutputPath = string.Empty;
        private bool _committed;

        /// <summary>
        /// True once this transaction has moved its file into place, whether or not the checks after the move passed: the file at the
        /// output path is then this transaction's, and a caller whose commit failed removes it with whatever else it made.
        /// </summary>
        internal bool Published { get; private set; }

        /// <summary>
        /// Holds the protected inputs and the output folder for one new file. The output must be vacant: a
        /// guarded mutation never replaces an existing file.
        /// </summary>
        internal GuardedFileMutation(
            string outputPath,
            IReadOnlyList<string?> protectedInputPaths)
        {
            OutputPath = FileMutationSafety.NormalizeLocalPath(outputPath, "Output file");

            try
            {
                string? outputDirectory = Path.GetDirectoryName(OutputPath);
                if (string.IsNullOrWhiteSpace(outputDirectory))
                    throw new DirectoryNotFoundException("That folder could not be found. Choose a folder again.");

                if (!Directory.Exists(outputDirectory))
                    throw new DirectoryNotFoundException("That folder could not be found. Choose a folder again.");
                _outputDirectoryLocks = FileMutationSafety.LockDirectoryTree(
                    outputDirectory,
                    "Output folder",
                    guardTargetMutation: true);
                _physicalOutputPath = Path.Combine(_outputDirectoryLocks.PhysicalPath, Path.GetFileName(OutputPath));
                FileMutationSafety.RejectOutputInGameTree(_physicalOutputPath);

                foreach (string? candidate in protectedInputPaths)
                {
                    if (string.IsNullOrWhiteSpace(candidate))
                        continue;

                    string path = FileMutationSafety.NormalizeLocalPath(candidate, "Protected input file");
                    if (_inputs.ContainsKey(path))
                        continue;
                    if (!File.Exists(path))
                        throw new FileNotFoundException("That protected input file could not be found.");

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
            string normalized = FileMutationSafety.NormalizeLocalPath(path, "Protected input file");
            if (!_inputs.TryGetValue(normalized, out ProtectedInput? input))
                throw new InvalidOperationException("The requested file is not held by this guarded transaction.");

            return ReadAllBytes(input.Stream, "Protected input");
        }

        internal void Commit(
            byte[] bytes,
            Action<string>? beforeCommittedOpen = null,
            Action<string>? beforePublish = null)
        {
            ArgumentNullException.ThrowIfNull(bytes);
            CommitCore(
                write: destination => destination.Write(bytes),
                expectedLength: bytes.LongLength,
                expectedHash: SHA256.HashData(bytes),
                beforeCommittedOpen: beforeCommittedOpen,
                beforePublish: beforePublish);
        }

        private void CommitCore(
            Action<FileStream> write,
            long expectedLength,
            byte[] expectedHash,
            Action<string>? beforeCommittedOpen,
            Action<string>? beforePublish)
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
                write(temp);
                temp.Flush(flushToDisk: true);

                WindowsFileIdentity tempIdentity = FileMutationSafety.GetWindowsIdentity(temp.SafeFileHandle, "staged output identity");
                if (OperatingSystem.IsWindows() && tempIdentity.NumberOfLinks != 0)
                    throw new InvalidOperationException("Staged output gained an alias while it was quarantined.");

                temp.Position = 0;
                byte[] stagedHash = SHA256.HashData(temp);
                if (temp.Length != expectedLength ||
                    !CryptographicOperations.FixedTimeEquals(stagedHash, expectedHash))
                {
                    throw new IOException("Staged output verification failed after commit.");
                }
                WindowsFileIdentity sealedTempIdentity = FileMutationSafety.GetWindowsIdentity(
                    temp.SafeFileHandle,
                    "sealed staged output identity");
                if (OperatingSystem.IsWindows() &&
                    (!tempIdentity.IsSameFile(sealedTempIdentity) || sealedTempIdentity.NumberOfLinks != 0))
                {
                    throw new InvalidOperationException(
                        "Staged output changed identity or gained an alias while it was quarantined.");
                }

                ValidateDestination();
                beforePublish?.Invoke(_physicalOutputPath);
                ValidateDestination();
                FileMutationSafety.ReleaseStagedFileQuarantine(temp);
                temp.Dispose();
                File.Move(tempPath, _physicalOutputPath, overwrite: false);
                tempEntryExists = false;
                Published = true;
                beforeCommittedOpen?.Invoke(_physicalOutputPath);

                SafeFileHandle? committedHandle = FileMutationSafety.OpenNoFollowReadHandle(
                    _physicalOutputPath,
                    "committed output file");
                FileStream? committed = null;
                try
                {
                    WindowsFileIdentity committedIdentity = FileMutationSafety.GetWindowsIdentity(committedHandle, "committed output identity");
                    if (OperatingSystem.IsWindows() && committedIdentity.IsReparsePoint)
                        throw new IOException(FileMutationSafety.FileCannotUseLink);
                    if (OperatingSystem.IsWindows() && !tempIdentity.IsSameFile(committedIdentity))
                        throw new IOException("Committed output identity does not match the staged file.");
                    if (OperatingSystem.IsWindows() && committedIdentity.NumberOfLinks != 1)
                        throw new IOException("Committed output unexpectedly shares a file identity.");
                    if (OperatingSystem.IsWindows() && _inputs.Values.Any(input => input.Identity.IsSameFile(committedIdentity)))
                        throw new IOException("Committed output aliases a protected input file.");

                    string committedPhysicalPath = OperatingSystem.IsWindows()
                        ? FileMutationSafety.GetFinalLocalPath(committedHandle, "committed output file")
                        : _physicalOutputPath;
                    string? committedParent = Path.GetDirectoryName(committedPhysicalPath);
                    if (string.IsNullOrWhiteSpace(committedParent) ||
                        !string.Equals(
                            committedParent.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                            _outputDirectoryLocks!.PhysicalPath.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                            FileMutationSafety.PathComparison))
                    {
                        throw new IOException("Committed output resolved outside the locked physical output folder.");
                    }

                    committed = new FileStream(committedHandle, FileAccess.Read);
                    committedHandle = null;
                    committed.Position = 0;
                    byte[] committedHash = SHA256.HashData(committed);
                    if (committed.Length != expectedLength ||
                        !CryptographicOperations.FixedTimeEquals(committedHash, expectedHash))
                    {
                        throw new IOException("Atomic output verification failed after commit.");
                    }

                    committed.Position = 0;
                    _committedStream = committed;
                    committed = null;
                    _committed = true;
                    _outputDirectoryLocks!.ReleaseMutationSentinelIfDirectoryNonEmpty();
                }
                finally
                {
                    committed?.Dispose();
                    committedHandle?.Dispose();
                }
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
            _committedStream?.Dispose();
            _committedStream = null;
            _outputDirectoryLocks?.Dispose();
            _outputDirectoryLocks = null;
        }

        /// <summary>The output may not be in a game folder, a link, a folder or an existing file (it is always new).</summary>
        private void ValidateDestination()
        {
            FileMutationSafety.RejectOutputInGameTree(_physicalOutputPath);
            FileMutationSafety.RejectReparsePoint(_physicalOutputPath, "Output file");
            if (Directory.Exists(_physicalOutputPath))
                throw new InvalidOperationException("The selected output file is a folder.");
            if (File.Exists(_physicalOutputPath))
                throw new IOException("The selected output file is no longer vacant.");
        }

        private static byte[] ReadAllBytes(FileStream stream, string label)
        {
            if (stream.Length > int.MaxValue)
                throw new IOException(FileMutationSafety.FileTooLargeToRead);

            byte[] bytes = new byte[checked((int)stream.Length)];
            stream.Position = 0;
            stream.ReadExactly(bytes);
            return bytes;
        }

        private sealed record ProtectedInput(FileStream Stream, WindowsFileIdentity Identity);
    }
}
