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
            return new GuardedFileMutation(
                outputPath,
                authorization: null,
                protectedInputPaths,
                requireProtectedInput: true);
        }

        internal static GuardedFileMutation BeginGenerated(string outputPath)
        {
            return new GuardedFileMutation(
                outputPath,
                authorization: null,
                Array.Empty<string?>(),
                requireProtectedInput: false);
        }

        internal static GuardedFileMutation BeginInAppOwnedProfile(
            string outputPath,
            AppOwnedProfileMutationAuthorization authorization,
            params string?[] protectedInputPaths)
        {
            authorization.EnsureUsable();
            return new GuardedFileMutation(
                outputPath,
                authorization,
                protectedInputPaths,
                requireProtectedInput: true);
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
                    $"Could not create staged output. Win32 error: {error}",
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

        internal static DirectoryLockSet LockDirectoryTree(
            string directoryPath,
            string label,
            Action? beforeFirstOpenForTest = null,
            bool guardTargetMutation = false)
        {
            string logicalPath = NormalizeLocalPath(directoryPath, label);
            if (!Directory.Exists(logicalPath))
                throw new DirectoryNotFoundException($"{label} does not exist.");

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
                        throw new InvalidOperationException(
                            $"{label} cannot contain a symbolic link, junction, or other reparse point.");
                    }

                    string resolved = GetFinalLocalPath(handle, label);
                    if (previousPhysicalComponent is not null &&
                        !string.Equals(
                            Path.GetDirectoryName(resolved),
                            previousPhysicalComponent,
                            PathComparison))
                    {
                        handle.Dispose();
                        throw new InvalidOperationException($"{label} changed identity while it was being secured.");
                    }

                    handles.Add(handle);
                    logicalTargetHandle = handle;
                    previousPhysicalComponent = resolved;
                }

                if (logicalTargetHandle is null)
                    throw new DirectoryNotFoundException($"{label} does not exist.");

                string physicalPath = GetFinalLocalPath(logicalTargetHandle, label);
                WindowsFileIdentity initialIdentity = GetWindowsIdentity(logicalTargetHandle, label);
                foreach (string ancestor in EnumerateDirectoryAncestors(physicalPath))
                {
                    SafeFileHandle handle = OpenDirectoryHandle(ancestor, label);
                    WindowsFileIdentity identity = GetWindowsIdentity(handle, label);
                    if (identity.IsReparsePoint)
                    {
                        handle.Dispose();
                        throw new InvalidOperationException(
                            $"{label} cannot contain a symbolic link, junction, or other reparse point.");
                    }

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
                    !string.Equals(GetFinalLocalPath(logicalTargetHandle, label), physicalPath, PathComparison))
                {
                    throw new InvalidOperationException($"{label} changed identity while it was being secured.");
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
                    DirectoryLockSet nextLocks = LockDirectoryTree(
                        nextPhysicalPath,
                        "App-owned output folder",
                        guardTargetMutation: true);
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
                FileFlagBackupSemantics | FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (handle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                handle.Dispose();
                throw new IOException($"Could not secure {label}. Win32 error: {error}", new Win32Exception(error));
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
                    $"Could not guard {label} against in-place directory mutation. Win32 error: {error}",
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
                    $"{label} changed identity before its mutation guard was created.");
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
                    $"Could not create {label} mutation guard. Win32 error: {error}",
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
                        $"{label} mutation guard escaped its held directory.");
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
                throw new IOException($"Could not secure {label}. Win32 error: {error}", new Win32Exception(error));
            }

            return handle;
        }

        internal static WindowsFileIdentity PublishDirectoryToVacantPath(
            string sourceDirectory,
            string destinationDirectory,
            WindowsFileIdentity expectedSourceIdentity,
            string? trustedSourceRoot,
            Action<string, WindowsFileIdentity>? prepareSourceDirectory = null,
            Action<string>? afterSourcePrepared = null,
            Action<string, WindowsFileIdentity>? verifyPublishedDirectory = null)
        {
            string normalizedSource = NormalizeLocalPath(sourceDirectory, "Staged package directory");
            string normalizedDestination = NormalizeLocalPath(destinationDirectory, "Published package directory");
            if (!Directory.Exists(normalizedSource))
                throw new DirectoryNotFoundException("The staged package directory no longer exists.");
            if (Directory.Exists(normalizedDestination) || File.Exists(normalizedDestination))
                throw new IOException("The published package path is no longer vacant.");

            string? destinationParent = Path.GetDirectoryName(normalizedDestination);
            string destinationName = Path.GetFileName(normalizedDestination);
            if (string.IsNullOrWhiteSpace(destinationParent) || string.IsNullOrWhiteSpace(destinationName))
                throw new InvalidOperationException("The published package path is invalid.");

            if (!OperatingSystem.IsWindows())
            {
                RejectReparsePoint(normalizedSource, "Staged package directory");
                RejectOutputInGameTree(Path.Combine(normalizedDestination, ".onslaught-package-root-probe"));
                Directory.Move(normalizedSource, normalizedDestination);
                return default;
            }

            using DirectoryLockSet destinationParentLocks = LockDirectoryTree(
                destinationParent,
                "Published package parent",
                guardTargetMutation: true);
            string physicalDestination = NormalizeLocalPath(
                Path.Combine(destinationParentLocks.PhysicalPath, destinationName),
                "Published package directory");
            RejectOutputInGameTree(Path.Combine(physicalDestination, ".onslaught-package-root-probe"));

            if (!string.IsNullOrWhiteSpace(trustedSourceRoot))
            {
                using DirectoryLockSet trustedSourceLocks = LockDirectoryTree(
                    trustedSourceRoot,
                    "Trusted asset export root");
                if (IsSameOrUnderRoot(physicalDestination, trustedSourceLocks.PhysicalPath) ||
                    IsSameOrUnderRoot(trustedSourceLocks.PhysicalPath, physicalDestination))
                {
                    throw new InvalidOperationException(
                        "Published package directory cannot overlap the trusted generated asset export root.");
                }
            }

            using SafeFileHandle sourceHandle = OpenDirectoryRenameHandle(
                normalizedSource,
                "Staged package directory");
            WindowsFileIdentity sourceIdentity = GetWindowsIdentity(
                sourceHandle,
                "Staged package directory");
            if (sourceIdentity.IsReparsePoint ||
                !sourceIdentity.IsSameFile(expectedSourceIdentity) ||
                !string.Equals(
                    GetFinalLocalPath(sourceHandle, "Staged package directory"),
                    normalizedSource,
                    PathComparison))
            {
                throw new InvalidOperationException(
                    "The staged package directory changed identity before publication.");
            }

            prepareSourceDirectory?.Invoke(normalizedSource, sourceIdentity);
            afterSourcePrepared?.Invoke(normalizedSource);

            if (Directory.Exists(physicalDestination) || File.Exists(physicalDestination))
                throw new IOException("The published package path appeared during publication.");

            RenameDirectoryHandle(sourceHandle, physicalDestination);
            WindowsFileIdentity publishedIdentity = GetWindowsIdentity(
                sourceHandle,
                "Published package directory");
            string publishedPath = GetFinalLocalPath(sourceHandle, "Published package directory");
            if (!publishedIdentity.IsSameFile(sourceIdentity))
            {
                throw new IOException("The published package directory did not retain the staged directory identity.");
            }
            if (!string.Equals(publishedPath, physicalDestination, PathComparison))
            {
                throw new IOException(
                    $"The published package directory resolved to '{publishedPath}' instead of '{physicalDestination}'.");
            }

            try
            {
                verifyPublishedDirectory?.Invoke(physicalDestination, publishedIdentity);
            }
            catch
            {
                RenameDirectoryHandle(sourceHandle, normalizedSource);
                throw;
            }

            return publishedIdentity;
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

        private static SafeFileHandle OpenDirectoryRenameHandle(string path, string label)
        {
            SafeFileHandle handle = CreateFileW(
                path,
                DeleteAccess | FileReadAttributes,
                FileShare.Read | FileShare.Write,
                IntPtr.Zero,
                FileMode.Open,
                FileFlagBackupSemantics | FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (handle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                handle.Dispose();
                throw new IOException($"Could not secure {label} for publication. Win32 error: {error}", new Win32Exception(error));
            }

            return handle;
        }

        private static void RenameDirectoryHandle(SafeFileHandle sourceHandle, string destinationPath)
        {
            byte[] nameBytes = Encoding.Unicode.GetBytes(destinationPath);
            int rootDirectoryOffset = IntPtr.Size == 8 ? 8 : 4;
            int fileNameLengthOffset = rootDirectoryOffset + IntPtr.Size;
            int fileNameOffset = fileNameLengthOffset + sizeof(uint);
            byte[] buffer = new byte[checked(fileNameOffset + nameBytes.Length + sizeof(char))];
            BitConverter.GetBytes(FileRenameFlagPosixSemantics).CopyTo(buffer, 0);
            BitConverter.GetBytes(nameBytes.Length).CopyTo(buffer, fileNameLengthOffset);
            nameBytes.CopyTo(buffer, fileNameOffset);

            IntPtr nativeBuffer = Marshal.AllocHGlobal(buffer.Length);
            try
            {
                Marshal.Copy(buffer, 0, nativeBuffer, buffer.Length);
                if (!SetFileInformationByHandle(
                        sourceHandle,
                        FileRenameInfoEx,
                        nativeBuffer,
                        (uint)buffer.Length))
                {
                    int error = Marshal.GetLastWin32Error();
                    throw new IOException(
                        $"Could not publish the staged package directory. Win32 error: {error}",
                        new Win32Exception(error));
                }
            }
            finally
            {
                Marshal.FreeHGlobal(nativeBuffer);
            }
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
                        $"Could not update staged output quarantine state. Win32 error: {error}",
                        new Win32Exception(error));
                }
            }
            finally
            {
                Marshal.FreeHGlobal(nativeBuffer);
            }
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

        private const int FileRenameInfoEx = 22;
        private const uint FileRenameFlagPosixSemantics = 0x00000002;

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
        private readonly List<WindowsFileIdentity> _externalInputIdentities = [];
        private readonly FileMutationSafety.AppOwnedProfileMutationAuthorization? _authorization;
        private FileMutationSafety.DirectoryLockSet? _outputDirectoryLocks;
        private FileStream? _committedStream;
        private string _physicalOutputPath = string.Empty;
        private bool _committed;

        internal GuardedFileMutation(
            string outputPath,
            FileMutationSafety.AppOwnedProfileMutationAuthorization? authorization,
            IReadOnlyList<string?> protectedInputPaths,
            bool requireProtectedInput)
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
                _outputDirectoryLocks = FileMutationSafety.LockDirectoryTree(
                    directoryToLock,
                    "Output folder",
                    guardTargetMutation: true);
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

                if (requireProtectedInput && _inputs.Count == 0)
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
            ArgumentNullException.ThrowIfNull(bytes);
            CommitCore(
                write: destination => destination.Write(bytes),
                expectedLength: bytes.LongLength,
                expectedHash: SHA256.HashData(bytes),
                beforeCommittedOpen: beforeCommittedOpen);
        }

        internal void CommitFromProtectedInput(
            string path,
            Action<string>? beforeCommittedOpen = null)
        {
            string normalized = FileMutationSafety.NormalizeLocalPath(path, "Protected input path");
            if (!_inputs.TryGetValue(normalized, out ProtectedInput? input))
                throw new InvalidOperationException("The requested file is not held by this guarded transaction.");

            input.Stream.Position = 0;
            byte[] expectedHash = SHA256.HashData(input.Stream);
            input.Stream.Position = 0;
            CommitCore(
                write: destination => input.Stream.CopyTo(destination),
                expectedLength: input.Stream.Length,
                expectedHash: expectedHash,
                beforeCommittedOpen: beforeCommittedOpen);
        }

        internal void CommitFromHeldSource(
            Stream source,
            WindowsFileIdentity sourceIdentity,
            Action<string>? beforeCommittedOpen = null)
        {
            ArgumentNullException.ThrowIfNull(source);
            if (!source.CanRead || !source.CanSeek)
                throw new ArgumentException("Held source stream must be readable and seekable.", nameof(source));

            source.Position = 0;
            byte[] expectedHash = SHA256.HashData(source);
            source.Position = 0;
            _externalInputIdentities.Add(sourceIdentity);
            CommitCore(
                write: destination => source.CopyTo(destination),
                expectedLength: source.Length,
                expectedHash: expectedHash,
                beforeCommittedOpen: beforeCommittedOpen);
        }

        private void CommitCore(
            Action<FileStream> write,
            long expectedLength,
            byte[] expectedHash,
            Action<string>? beforeCommittedOpen)
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
                FileMutationSafety.ReleaseStagedFileQuarantine(temp);
                temp.Dispose();
                File.Move(tempPath, _physicalOutputPath, overwrite: true);
                tempEntryExists = false;
                beforeCommittedOpen?.Invoke(_physicalOutputPath);

                SafeFileHandle? committedHandle = FileMutationSafety.OpenNoFollowReadHandle(
                    _physicalOutputPath,
                    "committed output file");
                FileStream? committed = null;
                try
                {
                    WindowsFileIdentity committedIdentity = FileMutationSafety.GetWindowsIdentity(committedHandle, "committed output identity");
                    if (OperatingSystem.IsWindows() && committedIdentity.IsReparsePoint)
                        throw new IOException("Committed output is a symbolic link, junction, or other reparse point.");
                    if (OperatingSystem.IsWindows() && !tempIdentity.IsSameFile(committedIdentity))
                        throw new IOException("Committed output identity does not match the staged file.");
                    if (OperatingSystem.IsWindows() && committedIdentity.NumberOfLinks != 1)
                        throw new IOException("Committed output unexpectedly shares a file identity.");
                    if (OperatingSystem.IsWindows() && _inputs.Values.Any(input => input.Identity.IsSameFile(committedIdentity)))
                        throw new IOException("Committed output aliases a protected input file.");
                    if (OperatingSystem.IsWindows() && _externalInputIdentities.Any(identity => identity.IsSameFile(committedIdentity)))
                        throw new IOException("Committed output aliases a held source file.");

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
            _externalInputIdentities.Clear();
            _committedStream?.Dispose();
            _committedStream = null;
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
            if (OperatingSystem.IsWindows() && _externalInputIdentities.Any(identity => identity.IsSameFile(outputIdentity)))
                throw new InvalidOperationException("Refusing to overwrite a held source file identity.");

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
