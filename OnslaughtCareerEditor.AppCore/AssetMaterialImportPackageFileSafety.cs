using Microsoft.Win32.SafeHandles;
using System.Security.Cryptography;

namespace Onslaught___Career_Editor
{
    internal sealed class AssetMaterialImportPackageFileSafety : IDisposable
    {
        private readonly AssetCatalogLoadSession _sources;
        private readonly GuardedPackageOutputRoot _output;
        private readonly AssetCatalogTrustEvidence _snapshotTrust;
        private readonly List<GuardedFileMutation> _heldWrites = [];
        private readonly List<FileStream> _generatedDestinationHolds = [];

        internal AssetMaterialImportPackageFileSafety(
            AssetCatalogSnapshot snapshot,
            string outputRoot,
            bool execute)
        {
            OutputRootExistedAtStart = Directory.Exists(
                FileMutationSafety.NormalizeLocalPath(outputRoot, "Material package output root"));
            AssetCatalogSelection? selection = AssetCatalogFileSafety.ResolveSelection(snapshot.CatalogFilePath);
            if (selection is null || string.IsNullOrWhiteSpace(snapshot.TrustedExportRoot))
            {
                throw new InvalidOperationException(
                    "Material package creation requires a loaded catalog with the generated bundle path contract.");
            }

            AssetCatalogLoadSession? sources = null;
            GuardedPackageOutputRoot? output = null;
            try
            {
                sources = AssetCatalogFileSafety.BeginLoad(selection);
                string expectedRoot = FileMutationSafety.NormalizeLocalPath(
                    snapshot.TrustedExportRoot,
                    "Snapshot trusted asset export root");
                if (!string.Equals(
                        sources.TrustedExportRoot,
                        expectedRoot,
                        FileMutationSafety.PathComparison))
                {
                    throw new InvalidOperationException(
                        "The catalog generated export root changed after the catalog was loaded.");
                }

                sources.ValidateTrust(snapshot.TrustEvidence);

                output = new GuardedPackageOutputRoot(outputRoot, sources.TrustedExportRoot, execute);
                _sources = sources;
                _output = output;
                _snapshotTrust = snapshot.TrustEvidence;
                sources = null;
                output = null;
            }
            finally
            {
                output?.Dispose();
                sources?.Dispose();
            }
        }

        internal string PhysicalOutputRoot => _output.PhysicalRoot;

        internal WindowsFileIdentity OutputRootIdentity => _output.RootIdentity;

        internal StagedPackageSeal CaptureSeal() =>
            StagedPackageSeal.Capture(PhysicalOutputRoot, OutputRootIdentity);

        internal bool OutputRootExistedAtStart { get; }

        internal AssetCatalogSourceRead OpenSource(string sourcePath, string label) =>
            _sources.OpenSource(
                sourcePath,
                label,
                expectedTrust: _snapshotTrust);

        internal string ResolveDestination(string destinationRelativePath, bool createDirectories) =>
            _output.ResolveDestination(destinationRelativePath, createDirectories);

        internal ExistingPackageDestination? HoldExistingDestination(
            string destinationPath,
            AssetCatalogSourceRead source)
        {
            FileStream? existing = _output.HoldExistingFile(destinationPath);
            if (existing is null)
                return null;

            source.Stream.Position = 0;
            byte[] sourceHash = SHA256.HashData(source.Stream);
            source.Stream.Position = 0;
            existing.Position = 0;
            byte[] existingHash = SHA256.HashData(existing);
            existing.Position = 0;
            return new ExistingPackageDestination(
                existing.Length,
                source.Stream.Length == existing.Length &&
                    CryptographicOperations.FixedTimeEquals(sourceHash, existingHash));
        }

        internal void ValidateGeneratedDestination(string destinationRelativePath)
        {
            string destinationPath = _output.ResolveDestination(
                destinationRelativePath,
                createDirectories: false);
            FileStream? existing = _output.HoldExistingFile(destinationPath);
            if (existing is not null)
                _generatedDestinationHolds.Add(existing);
        }

        internal void ReleaseGeneratedDestinationValidation()
        {
            foreach (FileStream stream in _generatedDestinationHolds)
                _output.ReleaseHeldFile(stream);
            _generatedDestinationHolds.Clear();
        }

        internal long CopySource(string destinationPath, AssetCatalogSourceRead source)
        {
            var mutation = FileMutationSafety.BeginGenerated(destinationPath);
            try
            {
                mutation.CommitFromHeldSource(
                    source.Stream,
                    source.Evidence.Identity);
                _heldWrites.Add(mutation);
                _output.ReleaseMutationSentinelsForHeldEntry(destinationPath);
                return source.Stream.Length;
            }
            catch
            {
                mutation.Dispose();
                throw;
            }
        }

        internal long WriteGenerated(string destinationRelativePath, byte[] bytes)
        {
            string destinationPath = _output.ResolveDestination(
                destinationRelativePath,
                createDirectories: true);
            var mutation = FileMutationSafety.BeginGenerated(destinationPath);
            try
            {
                mutation.Commit(bytes);
                _heldWrites.Add(mutation);
                _output.ReleaseMutationSentinelsForHeldEntry(destinationPath);
                return bytes.LongLength;
            }
            catch
            {
                mutation.Dispose();
                throw;
            }
        }

        public void Dispose()
        {
            for (int index = _heldWrites.Count - 1; index >= 0; index--)
                _heldWrites[index].Dispose();
            _heldWrites.Clear();
            _output.Dispose();
            _sources.Dispose();
        }
    }

    internal sealed class GuardedPackageOutputRoot : IDisposable
    {
        private readonly Dictionary<string, FileMutationSafety.DirectoryLockSet> _directoryLocks =
            new(FileMutationSafety.PathComparer);
        private readonly List<FileStream> _heldExistingFiles = [];
        private readonly bool _execute;

        internal GuardedPackageOutputRoot(
            string outputRoot,
            string? trustedSourceRoot,
            bool execute,
            bool requireExistingRoot = false)
        {
            _execute = execute;
            string normalizedOutputRoot = FileMutationSafety.NormalizeLocalPath(outputRoot, "Material package output root");
            if (requireExistingRoot && !Directory.Exists(normalizedOutputRoot))
                throw new DirectoryNotFoundException("Material package root disappeared before it could be secured.");
            string volumeRoot = Path.GetPathRoot(normalizedOutputRoot) ?? string.Empty;
            if (string.Equals(
                    normalizedOutputRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                    volumeRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                    FileMutationSafety.PathComparison))
            {
                throw new InvalidOperationException("Material package output root cannot be a volume root.");
            }

            var missingNames = new Stack<string>();
            string? existingAncestor = normalizedOutputRoot;
            while (!string.IsNullOrWhiteSpace(existingAncestor) && !Directory.Exists(existingAncestor))
            {
                FileMutationSafety.RejectReparsePoint(existingAncestor, "Material package output root");
                string name = Path.GetFileName(existingAncestor);
                if (string.IsNullOrWhiteSpace(name))
                    throw new DirectoryNotFoundException("Material package output root has no existing local ancestor.");

                missingNames.Push(name);
                existingAncestor = Path.GetDirectoryName(existingAncestor);
            }

            if (string.IsNullOrWhiteSpace(existingAncestor))
                throw new DirectoryNotFoundException("Material package output root has no existing local ancestor.");

            FileMutationSafety.DirectoryLockSet ancestorLocks = FileMutationSafety.LockDirectoryTree(
                existingAncestor,
                "Material package output ancestor",
                guardTargetMutation: _execute && string.Equals(
                    existingAncestor,
                    normalizedOutputRoot,
                    FileMutationSafety.PathComparison));
            _directoryLocks.Add(ancestorLocks.PhysicalPath, ancestorLocks);
            string currentPhysicalPath = ancestorLocks.PhysicalPath;
            try
            {
                string prospectivePhysicalRoot = missingNames.Aggregate(
                    currentPhysicalPath,
                    static (current, name) => Path.Combine(current, name));
                ValidateRootPlacement(prospectivePhysicalRoot, trustedSourceRoot);

                while (missingNames.Count > 0)
                {
                    string nextPhysicalPath = Path.Combine(currentPhysicalPath, missingNames.Pop());
                    FileMutationSafety.RejectReparsePoint(nextPhysicalPath, "Material package output directory");
                    if (!_execute)
                    {
                        currentPhysicalPath = nextPhysicalPath;
                        continue;
                    }

                    if (!Directory.Exists(nextPhysicalPath))
                        Directory.CreateDirectory(nextPhysicalPath);

                    FileMutationSafety.DirectoryLockSet nextLocks = FileMutationSafety.LockDirectoryTree(
                        nextPhysicalPath,
                        "Material package output directory",
                        guardTargetMutation: true);
                    ValidateDirectChild(nextLocks.PhysicalPath, currentPhysicalPath, "Material package output directory");
                    _directoryLocks.TryAdd(nextLocks.PhysicalPath, nextLocks);
                    if (!_directoryLocks.ContainsValue(nextLocks))
                        nextLocks.Dispose();
                    currentPhysicalPath = nextLocks.PhysicalPath;
                }

                PhysicalRoot = currentPhysicalPath;
                ValidateRootPlacement(PhysicalRoot, trustedSourceRoot);
                if (requireExistingRoot &&
                    (!_directoryLocks.ContainsKey(PhysicalRoot) || !Directory.Exists(PhysicalRoot)))
                {
                    throw new DirectoryNotFoundException(
                        "Material package root disappeared while it was being secured.");
                }
            }
            catch
            {
                Dispose();
                throw;
            }
        }

        internal string PhysicalRoot { get; }

        internal WindowsFileIdentity RootIdentity =>
            _directoryLocks.TryGetValue(PhysicalRoot, out FileMutationSafety.DirectoryLockSet? locks)
                ? locks.Identity
                : default;

        internal string ResolveDestination(string destinationRelativePath, bool createDirectories)
        {
            if (string.IsNullOrWhiteSpace(destinationRelativePath) ||
                Path.IsPathRooted(destinationRelativePath))
            {
                throw new InvalidOperationException("Material package destination must be a relative path.");
            }

            string normalizedRelativePath = destinationRelativePath
                .Replace('/', Path.DirectorySeparatorChar)
                .Replace('\\', Path.DirectorySeparatorChar);
            string[] components = normalizedRelativePath.Split(
                Path.DirectorySeparatorChar,
                StringSplitOptions.RemoveEmptyEntries);
            if (components.Length == 0 || components.Any(static component => component is "." or ".."))
                throw new InvalidOperationException("Material package destination contains an unsafe path component.");

            string candidate = FileMutationSafety.NormalizeLocalPath(
                Path.Combine(PhysicalRoot, Path.Combine(components)),
                "Material package destination");
            if (!FileMutationSafety.IsSameOrUnderRoot(candidate, PhysicalRoot) ||
                string.Equals(candidate, PhysicalRoot, FileMutationSafety.PathComparison))
            {
                throw new InvalidOperationException("Material package destination escapes the output root.");
            }

            string? parent = Path.GetDirectoryName(candidate);
            if (string.IsNullOrWhiteSpace(parent))
                throw new InvalidOperationException("Material package destination has no containing directory.");

            EnsureDirectory(parent, createDirectories && _execute);
            FileMutationSafety.RejectOutputInGameTree(candidate);
            FileMutationSafety.RejectReparsePoint(candidate, "Material package destination");
            if (Directory.Exists(candidate))
                throw new InvalidOperationException("Material package destination is a directory.");
            return candidate;
        }

        internal void ReleaseMutationSentinelsForHeldEntry(string heldEntryPath)
        {
            string? current = Path.GetDirectoryName(
                FileMutationSafety.NormalizeLocalPath(heldEntryPath, "Held package output entry"));
            while (!string.IsNullOrWhiteSpace(current) &&
                FileMutationSafety.IsSameOrUnderRoot(current, PhysicalRoot))
            {
                if (_directoryLocks.TryGetValue(current, out FileMutationSafety.DirectoryLockSet? locks))
                    locks.ReleaseMutationSentinelIfDirectoryNonEmpty();
                if (string.Equals(current, PhysicalRoot, FileMutationSafety.PathComparison))
                    break;
                current = Path.GetDirectoryName(current);
            }
        }

        internal FileStream? HoldExistingFile(string destinationPath)
        {
            if (!File.Exists(destinationPath))
                return null;

            SafeFileHandle? handle = FileMutationSafety.OpenNoFollowReadHandle(
                destinationPath,
                "Existing material package file");
            try
            {
                WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(
                    handle,
                    "Existing material package file");
                if (identity.IsReparsePoint)
                    throw new InvalidOperationException("Existing material package file is a reparse point.");
                if (OperatingSystem.IsWindows() && identity.NumberOfLinks > 1)
                    throw new InvalidOperationException("Existing material package file is hardlinked to another file.");

                string physicalPath = OperatingSystem.IsWindows()
                    ? FileMutationSafety.GetFinalLocalPath(handle, "Existing material package file")
                    : destinationPath;
                if (!string.Equals(physicalPath, destinationPath, FileMutationSafety.PathComparison) ||
                    !FileMutationSafety.IsSameOrUnderRoot(physicalPath, PhysicalRoot))
                {
                    throw new InvalidOperationException(
                        "Existing material package file resolves outside the held output root.");
                }

                var stream = new FileStream(handle, FileAccess.Read);
                handle = null;
                _heldExistingFiles.Add(stream);
                ReleaseMutationSentinelsForHeldEntry(destinationPath);
                return stream;
            }
            finally
            {
                handle?.Dispose();
            }
        }

        internal void ReleaseHeldFile(FileStream stream)
        {
            if (_heldExistingFiles.Remove(stream))
                stream.Dispose();
        }

        private void EnsureDirectory(string directoryPath, bool create)
        {
            if (string.Equals(directoryPath, PhysicalRoot, FileMutationSafety.PathComparison))
                return;
            if (!FileMutationSafety.IsSameOrUnderRoot(directoryPath, PhysicalRoot))
                throw new InvalidOperationException("Material package directory escapes the output root.");

            string relative = Path.GetRelativePath(PhysicalRoot, directoryPath);
            string[] components = relative.Split(
                [Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar],
                StringSplitOptions.RemoveEmptyEntries);
            string current = PhysicalRoot;
            foreach (string component in components)
            {
                string next = Path.Combine(current, component);
                if (_directoryLocks.ContainsKey(next))
                {
                    current = next;
                    continue;
                }

                FileMutationSafety.RejectReparsePoint(next, "Material package directory");
                if (!Directory.Exists(next))
                {
                    if (!create)
                        return;
                    Directory.CreateDirectory(next);
                }

                FileMutationSafety.DirectoryLockSet locks = FileMutationSafety.LockDirectoryTree(
                    next,
                    "Material package directory",
                    guardTargetMutation: true);
                ValidateDirectChild(locks.PhysicalPath, current, "Material package directory");
                if (_directoryLocks.TryAdd(locks.PhysicalPath, locks))
                {
                    current = locks.PhysicalPath;
                    ReleaseMutationSentinelsForHeldEntry(locks.PhysicalPath);
                }
                else
                {
                    current = locks.PhysicalPath;
                    locks.Dispose();
                }
            }
        }

        private static void ValidateDirectChild(string child, string parent, string label)
        {
            if (!string.Equals(
                    Path.GetDirectoryName(child),
                    parent,
                    FileMutationSafety.PathComparison))
            {
                throw new InvalidOperationException($"{label} changed identity while it was being secured.");
            }
        }

        private static void ValidateRootPlacement(string physicalRoot, string? trustedSourceRoot)
        {
            FileMutationSafety.RejectOutputInGameTree(
                Path.Combine(physicalRoot, ".onslaught-material-package-root-probe"));
            if (string.IsNullOrWhiteSpace(trustedSourceRoot))
                return;

            string physicalSourceRoot = FileMutationSafety.NormalizeLocalPath(
                trustedSourceRoot,
                "Trusted asset export root");
            if (FileMutationSafety.IsSameOrUnderRoot(physicalRoot, physicalSourceRoot) ||
                FileMutationSafety.IsSameOrUnderRoot(physicalSourceRoot, physicalRoot))
            {
                throw new InvalidOperationException(
                    "Material package output root cannot overlap the trusted generated asset export root.");
            }
        }

        public void Dispose()
        {
            for (int index = _heldExistingFiles.Count - 1; index >= 0; index--)
                _heldExistingFiles[index].Dispose();
            _heldExistingFiles.Clear();

            foreach (FileMutationSafety.DirectoryLockSet locks in _directoryLocks.Values.Reverse())
                locks.Dispose();
            _directoryLocks.Clear();
        }
    }

    internal readonly record struct ExistingPackageDestination(long Length, bool MatchesSource);

    internal sealed class StagedPackageSeal : IDisposable
    {
        private readonly IReadOnlyList<SealedPackageFile> _files;
        private readonly HashSet<string> _relativePaths;
        private bool _disposed;
        private bool _preparedForRename;

        private StagedPackageSeal(
            WindowsFileIdentity rootIdentity,
            IReadOnlyList<SealedPackageFile> files)
        {
            RootIdentity = rootIdentity;
            _files = files;
            _relativePaths = files
                .Select(static file => file.RelativePath)
                .ToHashSet(StringComparer.OrdinalIgnoreCase);
        }

        internal WindowsFileIdentity RootIdentity { get; }

        internal void PrepareForRename(
            string stagedRoot,
            WindowsFileIdentity stagedRootIdentity)
        {
            ThrowIfDisposed();
            if (!stagedRootIdentity.IsSameFile(RootIdentity))
                throw new IOException("Staged package root identity changed before publication.");

            string normalizedRoot = FileMutationSafety.NormalizeLocalPath(
                stagedRoot,
                "Staged material package root");
            var currentPaths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            CollectRelativePaths(normalizedRoot, normalizedRoot, currentPaths);
            if (!_relativePaths.SetEquals(currentPaths))
                throw new IOException("Staged package contents changed after the package was sealed.");

            foreach (SealedPackageFile file in _files)
                file.VerifyHeld(normalizedRoot);
            foreach (SealedPackageFile file in _files)
                file.ReleaseForRename();
            _preparedForRename = true;
        }

        internal static StagedPackageSeal Capture(
            string stagedRoot,
            WindowsFileIdentity expectedRootIdentity)
        {
            string normalizedRoot = FileMutationSafety.NormalizeLocalPath(
                stagedRoot,
                "Staged material package root");
            var files = new List<SealedPackageFile>();
            try
            {
                CaptureDirectory(normalizedRoot, normalizedRoot, files);
                return new StagedPackageSeal(expectedRootIdentity, files);
            }
            catch
            {
                foreach (SealedPackageFile file in files)
                    file.Dispose();
                throw;
            }
        }

        internal void VerifyPublished(
            string publishedRoot,
            WindowsFileIdentity publishedRootIdentity)
        {
            ThrowIfDisposed();
            if (!_preparedForRename)
                throw new InvalidOperationException("Staged package seal was not prepared for rename.");
            if (!publishedRootIdentity.IsSameFile(RootIdentity))
                throw new IOException("Published package root identity does not match the sealed staging root.");

            string normalizedRoot = FileMutationSafety.NormalizeLocalPath(
                publishedRoot,
                "Published material package root");
            var currentPaths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            CollectRelativePaths(normalizedRoot, normalizedRoot, currentPaths);
            if (!_relativePaths.SetEquals(currentPaths))
                throw new IOException("Published package contents changed after the staged package was sealed.");

            foreach (SealedPackageFile file in _files)
                file.VerifyPublished(normalizedRoot);
        }

        private static void CaptureDirectory(
            string root,
            string directory,
            List<SealedPackageFile> files)
        {
            foreach (string entry in Directory.EnumerateFileSystemEntries(directory))
            {
                FileAttributes attributes = File.GetAttributes(entry);
                if ((attributes & FileAttributes.ReparsePoint) != 0)
                    throw new InvalidOperationException("Staged package cannot contain a reparse point.");
                if ((attributes & FileAttributes.Directory) != 0)
                {
                    CaptureDirectory(root, entry, files);
                    continue;
                }

                SafeFileHandle? handle = FileMutationSafety.OpenNoFollowReadHandle(
                    entry,
                    "Staged package file");
                try
                {
                    WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(
                        handle,
                        "Staged package file");
                    if (identity.IsReparsePoint ||
                        (OperatingSystem.IsWindows() && identity.NumberOfLinks != 1))
                    {
                        throw new InvalidOperationException(
                            "Staged package files must be regular single-link files.");
                    }

                    string physicalPath = OperatingSystem.IsWindows()
                        ? FileMutationSafety.GetFinalLocalPath(handle, "Staged package file")
                        : FileMutationSafety.NormalizeLocalPath(entry, "Staged package file");
                    if (!string.Equals(
                            physicalPath,
                            FileMutationSafety.NormalizeLocalPath(entry, "Staged package file"),
                            FileMutationSafety.PathComparison))
                    {
                        throw new InvalidOperationException(
                            "Staged package file resolved outside its expected path.");
                    }

                    var stream = new FileStream(handle, FileAccess.Read);
                    handle = null;
                    stream.Position = 0;
                    byte[] digest = SHA256.HashData(stream);
                    stream.Position = 0;
                    files.Add(new SealedPackageFile(
                        Path.GetRelativePath(root, physicalPath).Replace('\\', '/'),
                        identity,
                        digest,
                        stream.Length,
                        stream));
                }
                finally
                {
                    handle?.Dispose();
                }
            }
        }

        private static void CollectRelativePaths(
            string root,
            string directory,
            HashSet<string> relativePaths)
        {
            foreach (string entry in Directory.EnumerateFileSystemEntries(directory))
            {
                FileAttributes attributes = File.GetAttributes(entry);
                if ((attributes & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("Published package contains a reparse point.");
                if ((attributes & FileAttributes.Directory) != 0)
                    CollectRelativePaths(root, entry, relativePaths);
                else
                    relativePaths.Add(Path.GetRelativePath(root, entry).Replace('\\', '/'));
            }
        }

        private void ThrowIfDisposed()
        {
            if (_disposed)
                throw new ObjectDisposedException(nameof(StagedPackageSeal));
        }

        public void Dispose()
        {
            if (_disposed)
                return;
            foreach (SealedPackageFile file in _files.Reverse())
                file.Dispose();
            _disposed = true;
        }

        private sealed class SealedPackageFile : IDisposable
        {
            private readonly byte[] _digest;
            private FileStream? _stream;

            internal SealedPackageFile(
                string relativePath,
                WindowsFileIdentity identity,
                byte[] digest,
                long length,
                FileStream stream)
            {
                RelativePath = relativePath;
                Identity = identity;
                _digest = digest;
                Length = length;
                _stream = stream;
            }

            internal string RelativePath { get; }

            internal WindowsFileIdentity Identity { get; }

            internal long Length { get; }

            internal void VerifyHeld(string root)
            {
                FileStream stream = _stream
                    ?? throw new ObjectDisposedException(nameof(SealedPackageFile));
                WindowsFileIdentity currentIdentity = FileMutationSafety.GetWindowsIdentity(
                    stream.SafeFileHandle,
                    "Sealed package file");
                if (!currentIdentity.IsSameFile(Identity) || stream.Length != Length)
                    throw new IOException("A sealed package file changed identity or length before publication.");

                string expectedPath = FileMutationSafety.NormalizeLocalPath(
                    Path.Combine(
                        root,
                        RelativePath.Replace('/', Path.DirectorySeparatorChar)),
                    "Sealed package file");
                string currentPath = OperatingSystem.IsWindows()
                    ? FileMutationSafety.GetFinalLocalPath(stream.SafeFileHandle, "Sealed package file")
                    : expectedPath;
                if (!string.Equals(currentPath, expectedPath, FileMutationSafety.PathComparison))
                    throw new IOException("A sealed package file moved or was replaced before publication.");

                stream.Position = 0;
                byte[] currentDigest = SHA256.HashData(stream);
                stream.Position = 0;
                if (!CryptographicOperations.FixedTimeEquals(currentDigest, _digest))
                    throw new IOException("A sealed package file changed content before publication.");
            }

            internal void ReleaseForRename()
            {
                _stream?.Dispose();
                _stream = null;
            }

            internal void VerifyPublished(string publishedRoot)
            {
                string expectedPath = FileMutationSafety.NormalizeLocalPath(
                    Path.Combine(
                        publishedRoot,
                        RelativePath.Replace('/', Path.DirectorySeparatorChar)),
                    "Published package file");
                using SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(
                    expectedPath,
                    "Published package file");
                WindowsFileIdentity currentIdentity = FileMutationSafety.GetWindowsIdentity(
                    handle,
                    "Published package file");
                if (!currentIdentity.IsSameFile(Identity))
                    throw new IOException("A sealed package file was replaced during publication.");

                string currentPath = OperatingSystem.IsWindows()
                    ? FileMutationSafety.GetFinalLocalPath(handle, "Published package file")
                    : expectedPath;
                if (!string.Equals(currentPath, expectedPath, FileMutationSafety.PathComparison))
                    throw new IOException("A published package file resolved outside its sealed path.");

                using var stream = new FileStream(handle, FileAccess.Read);
                if (stream.Length != Length)
                    throw new IOException("A sealed package file changed length during publication.");
                byte[] currentDigest = SHA256.HashData(stream);
                if (!CryptographicOperations.FixedTimeEquals(currentDigest, _digest))
                    throw new IOException("A sealed package file changed content during publication.");
            }

            public void Dispose()
            {
                _stream?.Dispose();
                _stream = null;
            }
        }
    }

    internal static class GuardedPackageArtifactReader
    {
        internal static bool TryResolveRelativePath(
            string packageRoot,
            string? relativePath,
            out string fullPath)
        {
            fullPath = string.Empty;
            if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathRooted(relativePath))
                return false;

            try
            {
                string normalized = relativePath
                    .Replace('/', Path.DirectorySeparatorChar)
                    .Replace('\\', Path.DirectorySeparatorChar);
                string[] components = normalized.Split(Path.DirectorySeparatorChar, StringSplitOptions.None);
                if (components.Length == 0 ||
                    components.Any(static component => string.IsNullOrWhiteSpace(component) || component is "." or ".."))
                {
                    return false;
                }

                string normalizedRoot = FileMutationSafety.NormalizeLocalPath(
                    packageRoot,
                    "Material package root");
                string candidate = FileMutationSafety.NormalizeLocalPath(
                    Path.Combine(normalizedRoot, Path.Combine(components)),
                    "Material package relative path");
                if (!FileMutationSafety.IsSameOrUnderRoot(candidate, normalizedRoot) ||
                    string.Equals(candidate, normalizedRoot, FileMutationSafety.PathComparison))
                {
                    return false;
                }

                fullPath = candidate;
                return true;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException)
            {
                return false;
            }
        }

        internal static GuardedPackageArtifactRead Open(
            string packageRoot,
            string relativePath,
            string label = "Package artifact")
        {
            if (!Directory.Exists(packageRoot))
                throw new DirectoryNotFoundException("Material package root does not exist.");

            GuardedPackageOutputRoot? output = null;
            try
            {
                output = new GuardedPackageOutputRoot(
                    packageRoot,
                    trustedSourceRoot: null,
                    execute: false);
                string path = output.ResolveDestination(relativePath, createDirectories: false);
                FileStream? stream = output.HoldExistingFile(path);
                var read = new GuardedPackageArtifactRead(output, stream, relativePath, label);
                output = null;
                return read;
            }
            finally
            {
                output?.Dispose();
            }
        }
    }

    internal sealed class GuardedPackageArtifactRead : IDisposable
    {
        private GuardedPackageOutputRoot? _output;
        private FileStream? _stream;
        private readonly string _label;

        internal GuardedPackageArtifactRead(
            GuardedPackageOutputRoot output,
            FileStream? stream,
            string relativePath,
            string label)
        {
            _output = output;
            _stream = stream;
            RelativePath = relativePath.Replace('\\', '/');
            _label = label;
        }

        internal string RelativePath { get; }

        internal bool Exists => _stream is not null;

        internal long Length => _stream?.Length ?? 0;

        internal Stream Stream => _stream
            ?? throw new FileNotFoundException($"{_label} does not exist.", RelativePath);

        internal byte[] ReadAllBytes(long maxBytes = 64L * 1024 * 1024)
        {
            FileStream stream = RequiredStream(maxBytes);
            byte[] bytes = new byte[checked((int)stream.Length)];
            stream.Position = 0;
            stream.ReadExactly(bytes);
            stream.Position = 0;
            return bytes;
        }

        internal string ReadAllText(
            System.Text.Encoding encoding,
            long maxBytes = 64L * 1024 * 1024)
        {
            ArgumentNullException.ThrowIfNull(encoding);
            FileStream stream = RequiredStream(maxBytes);
            stream.Position = 0;
            using var reader = new StreamReader(
                stream,
                encoding,
                detectEncodingFromByteOrderMarks: true,
                leaveOpen: true);
            string text = reader.ReadToEnd();
            stream.Position = 0;
            return text;
        }

        internal string ComputeSha256Hex(long maxBytes = 1L * 1024 * 1024 * 1024)
        {
            FileStream stream = RequiredStream(maxBytes);
            stream.Position = 0;
            string hash = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
            stream.Position = 0;
            return hash;
        }

        private FileStream RequiredStream(long maxBytes)
        {
            FileStream stream = _stream
                ?? throw new FileNotFoundException($"{_label} does not exist.", RelativePath);
            if (maxBytes < 0 || stream.Length > maxBytes || stream.Length > int.MaxValue)
                throw new IOException($"{_label} is too large to read safely.");
            return stream;
        }

        public void Dispose()
        {
            _stream = null;
            _output?.Dispose();
            _output = null;
        }
    }

    internal static class GuardedPackageArtifactWriter
    {
        internal static GuardedArtifactWriteResult WriteText(
            string packageRoot,
            string destinationRelativePath,
            string content,
            System.Text.Encoding encoding)
        {
            ArgumentNullException.ThrowIfNull(content);
            ArgumentNullException.ThrowIfNull(encoding);
            return WriteBytes(packageRoot, destinationRelativePath, encoding.GetBytes(content));
        }

        internal static GuardedArtifactWriteResult WriteBytes(
            string packageRoot,
            string destinationRelativePath,
            byte[] bytes)
        {
            ArgumentNullException.ThrowIfNull(bytes);
            if (!Directory.Exists(packageRoot))
                throw new DirectoryNotFoundException("Material package root does not exist.");

            using var output = new GuardedPackageOutputRoot(
                packageRoot,
                trustedSourceRoot: null,
                execute: true);
            string destinationPath = output.ResolveDestination(
                destinationRelativePath,
                createDirectories: true);
            FileStream? existing = output.HoldExistingFile(destinationPath);
            if (existing is not null)
            {
                bool matches = StreamMatchesBytes(existing, bytes);
                if (!matches)
                    throw new InvalidOperationException("Existing package artifact does not match the requested content.");
                return new GuardedArtifactWriteResult(Existing: true, Bytes: existing.Length);
            }

            using GuardedFileMutation mutation = FileMutationSafety.BeginGenerated(destinationPath);
            mutation.Commit(bytes);
            return new GuardedArtifactWriteResult(Existing: false, Bytes: bytes.LongLength);
        }

        internal static GuardedArtifactWriteResult ReplaceText(
            string packageRoot,
            string destinationRelativePath,
            string content,
            System.Text.Encoding encoding)
        {
            ArgumentNullException.ThrowIfNull(content);
            ArgumentNullException.ThrowIfNull(encoding);
            return ReplaceBytes(packageRoot, destinationRelativePath, encoding.GetBytes(content));
        }

        internal static GuardedArtifactWriteResult ReplaceBytes(
            string packageRoot,
            string destinationRelativePath,
            byte[] bytes)
        {
            ArgumentNullException.ThrowIfNull(bytes);
            if (!Directory.Exists(packageRoot))
                throw new DirectoryNotFoundException("Material package root does not exist.");

            using var output = new GuardedPackageOutputRoot(
                packageRoot,
                trustedSourceRoot: null,
                execute: true);
            string destinationPath = output.ResolveDestination(
                destinationRelativePath,
                createDirectories: true);
            bool existing = File.Exists(destinationPath);
            using GuardedFileMutation mutation = FileMutationSafety.BeginGenerated(destinationPath);
            mutation.Commit(bytes);
            return new GuardedArtifactWriteResult(Existing: existing, Bytes: bytes.LongLength);
        }

        internal static GuardedArtifactWriteResult CopyFile(
            string packageRoot,
            string sourceRelativePath,
            string destinationRelativePath)
        {
            if (!Directory.Exists(packageRoot))
                throw new DirectoryNotFoundException("Material package root does not exist.");

            using var output = new GuardedPackageOutputRoot(
                packageRoot,
                trustedSourceRoot: null,
                execute: true);
            string sourcePath = output.ResolveDestination(sourceRelativePath, createDirectories: false);
            FileStream source = output.HoldExistingFile(sourcePath)
                ?? throw new FileNotFoundException("Package source file does not exist.", sourcePath);
            string destinationPath = output.ResolveDestination(
                destinationRelativePath,
                createDirectories: true);
            FileStream? existing = output.HoldExistingFile(destinationPath);
            if (existing is not null)
            {
                if (!StreamsMatch(source, existing))
                    throw new InvalidOperationException("Existing package artifact does not match the package source.");
                return new GuardedArtifactWriteResult(Existing: true, Bytes: existing.Length);
            }

            WindowsFileIdentity sourceIdentity = FileMutationSafety.GetWindowsIdentity(
                source.SafeFileHandle,
                "Package source file");
            using GuardedFileMutation mutation = FileMutationSafety.BeginGenerated(destinationPath);
            mutation.CommitFromHeldSource(source, sourceIdentity);
            return new GuardedArtifactWriteResult(Existing: false, Bytes: source.Length);
        }

        private static bool StreamMatchesBytes(FileStream stream, byte[] bytes)
        {
            if (stream.Length != bytes.LongLength)
                return false;
            stream.Position = 0;
            byte[] actualHash = SHA256.HashData(stream);
            stream.Position = 0;
            return CryptographicOperations.FixedTimeEquals(actualHash, SHA256.HashData(bytes));
        }

        private static bool StreamsMatch(FileStream left, FileStream right)
        {
            if (left.Length != right.Length)
                return false;
            left.Position = 0;
            right.Position = 0;
            byte[] leftHash = SHA256.HashData(left);
            byte[] rightHash = SHA256.HashData(right);
            left.Position = 0;
            right.Position = 0;
            return CryptographicOperations.FixedTimeEquals(leftHash, rightHash);
        }
    }

    internal readonly record struct GuardedArtifactWriteResult(bool Existing, long Bytes);
}
