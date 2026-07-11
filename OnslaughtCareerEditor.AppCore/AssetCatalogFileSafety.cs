using Microsoft.Win32.SafeHandles;
using System.Security.Cryptography;

namespace Onslaught___Career_Editor
{
    internal static class AssetCatalogFileSafety
    {
        private const string CatalogFileName = "catalog.json";
        private const string AssetCatalogDirectoryName = "asset_catalog";

        internal static AssetCatalogSelection? ResolveSelection(string? pathOrDirectory)
        {
            if (string.IsNullOrWhiteSpace(pathOrDirectory))
                return null;

            try
            {
                string selectedPath = FileMutationSafety.NormalizeLocalPath(pathOrDirectory, "Asset catalog path");
                if (File.Exists(selectedPath))
                {
                    if (!string.Equals(Path.GetFileName(selectedPath), CatalogFileName, StringComparison.OrdinalIgnoreCase))
                        return null;

                    return BuildCanonicalSelection(selectedPath);
                }

                if (!Directory.Exists(selectedPath))
                    return null;

                string directCatalog = Path.Combine(selectedPath, CatalogFileName);
                string nestedCatalog = Path.Combine(selectedPath, AssetCatalogDirectoryName, CatalogFileName);
                if (string.Equals(
                        Path.GetFileName(selectedPath),
                        AssetCatalogDirectoryName,
                        StringComparison.OrdinalIgnoreCase) &&
                    File.Exists(directCatalog))
                {
                    return BuildCanonicalSelection(directCatalog);
                }

                if (File.Exists(directCatalog) && File.Exists(nestedCatalog))
                    return null;

                return File.Exists(nestedCatalog)
                    ? BuildCanonicalSelection(nestedCatalog)
                    : null;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return null;
            }
        }

        internal static AssetCatalogLoadSession BeginLoad(AssetCatalogSelection selection)
        {
            ArgumentNullException.ThrowIfNull(selection);
            return new AssetCatalogLoadSession(selection);
        }

        internal static AssetCatalogSelection? ResolveValidatedSelection(string? pathOrDirectory)
        {
            AssetCatalogSelection? selection = ResolveSelection(pathOrDirectory);
            if (selection is null)
                return null;

            try
            {
                using AssetCatalogLoadSession session = BeginLoad(selection);
                return new AssetCatalogSelection(session.CatalogFilePath, session.TrustedExportRoot);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return null;
            }
        }

        internal static string ResolveSourcePath(string trustedRoot, string catalogPath)
        {
            if (string.IsNullOrWhiteSpace(catalogPath))
                return string.Empty;

            string normalizedRoot = FileMutationSafety.NormalizeLocalPath(trustedRoot, "Trusted asset export root");
            string normalizedPath = catalogPath.Replace('/', Path.DirectorySeparatorChar);
            string resolvedPath = Path.IsPathRooted(normalizedPath)
                ? FileMutationSafety.NormalizeLocalPath(normalizedPath, "Catalog export path")
                : FileMutationSafety.NormalizeLocalPath(
                    Path.Combine(normalizedRoot, normalizedPath),
                    "Catalog export path");

            if (!FileMutationSafety.IsSameOrUnderRoot(resolvedPath, normalizedRoot) ||
                string.Equals(resolvedPath, normalizedRoot, FileMutationSafety.PathComparison))
            {
                throw new InvalidOperationException(
                    "Catalog export paths must remain below the selected generated export root.");
            }

            return resolvedPath;
        }

        private static AssetCatalogSelection? BuildSelection(string catalogPath, string trustedRoot)
        {
            if (string.IsNullOrWhiteSpace(trustedRoot))
                return null;

            string normalizedCatalog = FileMutationSafety.NormalizeLocalPath(catalogPath, "Asset catalog file");
            string normalizedRoot = FileMutationSafety.NormalizeLocalPath(trustedRoot, "Trusted asset export root");
            string volumeRoot = Path.GetPathRoot(normalizedRoot) ?? string.Empty;
            if (string.Equals(
                    normalizedRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                    volumeRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar),
                    FileMutationSafety.PathComparison))
            {
                return null;
            }

            if (!FileMutationSafety.IsSameOrUnderRoot(normalizedCatalog, normalizedRoot) ||
                !string.Equals(Path.GetFileName(normalizedCatalog), CatalogFileName, StringComparison.OrdinalIgnoreCase))
            {
                return null;
            }

            return new AssetCatalogSelection(normalizedCatalog, normalizedRoot);
        }

        private static AssetCatalogSelection? BuildCanonicalSelection(string catalogPath)
        {
            string catalogDirectory = Path.GetDirectoryName(catalogPath) ?? string.Empty;
            if (!string.Equals(
                    Path.GetFileName(catalogDirectory),
                    AssetCatalogDirectoryName,
                    StringComparison.OrdinalIgnoreCase))
            {
                return null;
            }

            string trustedRoot = Path.GetDirectoryName(catalogDirectory) ?? string.Empty;
            if (string.IsNullOrWhiteSpace(trustedRoot) ||
                File.Exists(Path.Combine(trustedRoot, CatalogFileName)))
            {
                return null;
            }

            return BuildSelection(catalogPath, trustedRoot);
        }
    }

    internal sealed record AssetCatalogSelection(string CatalogFilePath, string TrustedExportRoot);

    internal sealed class AssetCatalogLoadSession : IDisposable
    {
        private FileMutationSafety.DirectoryLockSet? _rootLocks;
        private FileMutationSafety.DirectoryLockSet? _catalogDirectoryLocks;
        private FileStream? _catalogStream;
        private WindowsFileIdentity _catalogIdentity;
        private readonly Dictionary<string, AssetCatalogSourceEvidence> _observedSources =
            new(FileMutationSafety.PathComparer);

        internal AssetCatalogLoadSession(AssetCatalogSelection selection)
        {
            try
            {
                _rootLocks = FileMutationSafety.LockDirectoryTree(
                    selection.TrustedExportRoot,
                    "Trusted asset export root");
                FileMutationSafety.RejectOutputInGameTree(
                    Path.Combine(_rootLocks.PhysicalPath, ".onslaught-asset-root-probe"));

                string catalogDirectory = Path.GetDirectoryName(selection.CatalogFilePath)
                    ?? throw new DirectoryNotFoundException("The asset catalog has no containing directory.");
                _catalogDirectoryLocks = FileMutationSafety.LockDirectoryTree(
                    catalogDirectory,
                    "Asset catalog directory");
                if (!FileMutationSafety.IsSameOrUnderRoot(
                        _catalogDirectoryLocks.PhysicalPath,
                        _rootLocks.PhysicalPath))
                {
                    throw new InvalidOperationException(
                        "The asset catalog directory resolves outside the selected generated export root.");
                }

                SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(
                    selection.CatalogFilePath,
                    "Asset catalog file");
                try
                {
                    WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, "Asset catalog file");
                    if (identity.IsReparsePoint)
                        throw new InvalidOperationException("The asset catalog file cannot be a symbolic link or other reparse point.");
                    if (OperatingSystem.IsWindows() && identity.NumberOfLinks > 1)
                        throw new InvalidOperationException("The asset catalog file cannot be hardlinked to another file.");

                    string physicalCatalogPath = OperatingSystem.IsWindows()
                        ? FileMutationSafety.GetFinalLocalPath(handle, "Asset catalog file")
                        : selection.CatalogFilePath;
                    string expectedPhysicalPath = Path.Combine(
                        _catalogDirectoryLocks.PhysicalPath,
                        Path.GetFileName(selection.CatalogFilePath));
                    if (!string.Equals(
                            physicalCatalogPath,
                            expectedPhysicalPath,
                            FileMutationSafety.PathComparison) ||
                        !FileMutationSafety.IsSameOrUnderRoot(physicalCatalogPath, _rootLocks.PhysicalPath))
                    {
                        throw new InvalidOperationException(
                            "The asset catalog file resolves outside the selected generated export root.");
                    }

                    _catalogStream = new FileStream(handle, FileAccess.Read);
                    _catalogIdentity = identity;
                    handle = null!;
                }
                finally
                {
                    handle?.Dispose();
                }

                CatalogFilePath = selection.CatalogFilePath;
                TrustedExportRoot = _rootLocks.PhysicalPath;
            }
            catch
            {
                Dispose();
                throw;
            }
        }

        internal string CatalogFilePath { get; }

        internal string TrustedExportRoot { get; }

        internal Stream CatalogStream => _catalogStream
            ?? throw new ObjectDisposedException(nameof(AssetCatalogLoadSession));

        internal AssetCatalogTrustEvidence CaptureTrustEvidence()
        {
            if (_rootLocks is null || _catalogStream is null)
                throw new ObjectDisposedException(nameof(AssetCatalogLoadSession));

            _catalogStream.Position = 0;
            byte[] catalogSha256 = SHA256.HashData(_catalogStream);
            _catalogStream.Position = 0;
            return new AssetCatalogTrustEvidence(
                _rootLocks.Identity,
                _catalogIdentity,
                catalogSha256,
                new Dictionary<string, AssetCatalogSourceEvidence>(
                    _observedSources,
                    FileMutationSafety.PathComparer));
        }

        internal void ValidateTrust(AssetCatalogTrustEvidence evidence)
        {
            if (_rootLocks is null || _catalogStream is null)
                throw new ObjectDisposedException(nameof(AssetCatalogLoadSession));
            if (!evidence.IsPresent)
                throw new InvalidOperationException("The catalog snapshot does not contain trusted identity evidence.");

            if (OperatingSystem.IsWindows() &&
                (!_rootLocks.Identity.IsSameFile(evidence.RootIdentity) ||
                    !_catalogIdentity.IsSameFile(evidence.CatalogIdentity)))
            {
                throw new InvalidOperationException(
                    "The catalog root or catalog file changed identity after the catalog was loaded.");
            }

            _catalogStream.Position = 0;
            byte[] currentCatalogSha256 = SHA256.HashData(_catalogStream);
            _catalogStream.Position = 0;
            if (!CryptographicOperations.FixedTimeEquals(
                    currentCatalogSha256,
                    evidence.CatalogSha256))
            {
                throw new InvalidOperationException(
                    "The catalog file contents changed after the catalog was loaded.");
            }
        }

        internal AssetCatalogSourceRead OpenSource(
            string catalogPath,
            string label,
            bool requireRelative = false,
            AssetCatalogTrustEvidence? expectedTrust = null)
        {
            if (_rootLocks is null)
                throw new ObjectDisposedException(nameof(AssetCatalogLoadSession));
            if (string.IsNullOrWhiteSpace(catalogPath))
                return AssetCatalogSourceRead.Missing(string.Empty, AssetCatalogSourceEvidence.Missing);
            if (requireRelative && Path.IsPathRooted(catalogPath))
                throw new InvalidOperationException("Catalog export paths must be bundle-root-relative.");

            string sourcePath = AssetCatalogFileSafety.ResolveSourcePath(TrustedExportRoot, catalogPath);
            FileMutationSafety.RejectOutputInGameTree(sourcePath);
            if (expectedTrust is not null && !expectedTrust.Sources.ContainsKey(sourcePath))
            {
                throw new InvalidOperationException(
                    "The requested catalog export was not part of the sealed catalog snapshot.");
            }
            if (!File.Exists(sourcePath))
            {
                FileMutationSafety.RejectExistingReparseAncestors(sourcePath, label);
                AssetCatalogSourceEvidence missing = AssetCatalogSourceEvidence.Missing;
                RecordAndValidateSource(sourcePath, missing, expectedTrust);
                return AssetCatalogSourceRead.Missing(sourcePath, missing);
            }

            string sourceDirectory = Path.GetDirectoryName(sourcePath)
                ?? throw new DirectoryNotFoundException($"{label} has no containing directory.");
            FileMutationSafety.DirectoryLockSet? sourceDirectoryLocks =
                FileMutationSafety.LockDirectoryTree(sourceDirectory, $"{label} directory");
            SafeFileHandle? handle = null;
            FileStream? stream = null;
            try
            {
                if (!FileMutationSafety.IsSameOrUnderRoot(
                        sourceDirectoryLocks.PhysicalPath,
                        TrustedExportRoot))
                {
                    throw new InvalidOperationException(
                        $"{label} directory resolves outside the selected generated export root.");
                }

                string expectedPhysicalPath = Path.Combine(
                    sourceDirectoryLocks.PhysicalPath,
                    Path.GetFileName(sourcePath));
                handle = FileMutationSafety.OpenNoFollowReadHandle(sourcePath, label);
                WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, label);
                if (identity.IsReparsePoint)
                    throw new InvalidOperationException($"{label} cannot be a symbolic link or other reparse point.");
                if (OperatingSystem.IsWindows() && identity.NumberOfLinks > 1)
                    throw new InvalidOperationException($"{label} cannot be hardlinked to another file.");

                string physicalPath = OperatingSystem.IsWindows()
                    ? FileMutationSafety.GetFinalLocalPath(handle, label)
                    : sourcePath;
                if (!string.Equals(
                        physicalPath,
                        expectedPhysicalPath,
                        FileMutationSafety.PathComparison) ||
                    !FileMutationSafety.IsSameOrUnderRoot(physicalPath, TrustedExportRoot) ||
                    string.Equals(physicalPath, TrustedExportRoot, FileMutationSafety.PathComparison))
                {
                    throw new InvalidOperationException(
                        $"{label} resolves outside the selected generated export root.");
                }

                stream = new FileStream(handle, FileAccess.Read);
                handle = null!;
                bool captureHash = expectedTrust is null || expectedTrust.Sources.ContainsKey(sourcePath);
                byte[] sha256 = Array.Empty<byte>();
                if (captureHash)
                {
                    stream.Position = 0;
                    sha256 = SHA256.HashData(stream);
                    stream.Position = 0;
                }
                AssetCatalogSourceEvidence evidence = new(
                    Exists: true,
                    Identity: identity,
                    Length: stream.Length,
                    Sha256: sha256);
                RecordAndValidateSource(sourcePath, evidence, expectedTrust);
                AssetCatalogSourceRead result = new(
                    sourcePath,
                    physicalPath,
                    stream,
                    evidence,
                    sourceDirectoryLocks);
                stream = null;
                sourceDirectoryLocks = null;
                return result;
            }
            finally
            {
                handle?.Dispose();
                stream?.Dispose();
                sourceDirectoryLocks?.Dispose();
            }
        }

        private void RecordAndValidateSource(
            string sourcePath,
            AssetCatalogSourceEvidence current,
            AssetCatalogTrustEvidence? expectedTrust)
        {
            if (_observedSources.TryGetValue(sourcePath, out AssetCatalogSourceEvidence? observed) &&
                !observed.Matches(current))
            {
                throw new InvalidOperationException(
                    "A catalog export changed identity during catalog snapshot creation.");
            }

            if (expectedTrust is not null &&
                (!expectedTrust.Sources.TryGetValue(sourcePath, out AssetCatalogSourceEvidence? expected) ||
                    !expected.Matches(current)))
            {
                throw new InvalidOperationException(
                    "A catalog export changed identity after the catalog was loaded.");
            }

            _observedSources[sourcePath] = current;
        }

        public void Dispose()
        {
            _catalogStream?.Dispose();
            _catalogStream = null;
            _catalogDirectoryLocks?.Dispose();
            _catalogDirectoryLocks = null;
            _rootLocks?.Dispose();
            _rootLocks = null;
        }
    }

    internal sealed class AssetCatalogSourceRead : IDisposable
    {
        private FileStream? _stream;
        private FileMutationSafety.DirectoryLockSet? _directoryLocks;

        internal AssetCatalogSourceRead(
            string path,
            string physicalPath,
            FileStream stream,
            AssetCatalogSourceEvidence evidence,
            FileMutationSafety.DirectoryLockSet directoryLocks)
        {
            Path = path;
            PhysicalPath = physicalPath;
            _stream = stream;
            _directoryLocks = directoryLocks;
            Evidence = evidence;
        }

        private AssetCatalogSourceRead(string path, AssetCatalogSourceEvidence evidence)
        {
            Path = path;
            PhysicalPath = path;
            Evidence = evidence;
        }

        internal string Path { get; }

        internal string PhysicalPath { get; }

        internal bool Exists => _stream is not null;

        internal AssetCatalogSourceEvidence Evidence { get; }

        internal Stream Stream => _stream
            ?? throw new FileNotFoundException("The catalog export file does not exist.", Path);

        internal static AssetCatalogSourceRead Missing(
            string path,
            AssetCatalogSourceEvidence? evidence = null) =>
            new(path, evidence ?? AssetCatalogSourceEvidence.Missing);

        public void Dispose()
        {
            _stream?.Dispose();
            _stream = null;
            _directoryLocks?.Dispose();
            _directoryLocks = null;
        }
    }

    public static class AssetCatalogSourceAccessService
    {
        public static AssetCatalogSourceLease Open(
            AssetCatalogSnapshot snapshot,
            string sourcePath,
            string label = "Catalog export file")
        {
            ArgumentNullException.ThrowIfNull(snapshot);
            if (string.IsNullOrWhiteSpace(snapshot.CatalogFilePath) ||
                string.IsNullOrWhiteSpace(snapshot.TrustedExportRoot))
            {
                throw new InvalidOperationException(
                    "Catalog source access requires a loaded catalog with a trusted generated export root.");
            }

            AssetCatalogSelection? selection = AssetCatalogFileSafety.ResolveSelection(snapshot.CatalogFilePath);
            if (selection is null)
                throw new InvalidOperationException("The catalog no longer has the required generated bundle layout.");

            AssetCatalogLoadSession? session = null;
            AssetCatalogSourceRead? source = null;
            try
            {
                session = AssetCatalogFileSafety.BeginLoad(selection);
                string expectedRoot = FileMutationSafety.NormalizeLocalPath(
                    snapshot.TrustedExportRoot,
                    "Snapshot trusted asset export root");
                if (!string.Equals(
                        session.TrustedExportRoot,
                        expectedRoot,
                        FileMutationSafety.PathComparison))
                {
                    throw new InvalidOperationException(
                        "The catalog generated export root changed after the catalog was loaded.");
                }

                session.ValidateTrust(snapshot.TrustEvidence);
                source = session.OpenSource(
                    sourcePath,
                    label,
                    expectedTrust: snapshot.TrustEvidence);
                AssetCatalogSourceLease lease = new(session, source);
                session = null;
                source = null;
                return lease;
            }
            finally
            {
                source?.Dispose();
                session?.Dispose();
            }
        }
    }

    public sealed class AssetCatalogSourceLease : IDisposable
    {
        private AssetCatalogLoadSession? _session;
        private AssetCatalogSourceRead? _source;

        internal AssetCatalogSourceLease(
            AssetCatalogLoadSession session,
            AssetCatalogSourceRead source)
        {
            _session = session;
            _source = source;
        }

        public string Path => Source.Path;

        public string PhysicalPath => Source.PhysicalPath;

        public bool Exists => Source.Exists;

        public Stream Stream => Source.Stream;

        private AssetCatalogSourceRead Source => _source
            ?? throw new ObjectDisposedException(nameof(AssetCatalogSourceLease));

        public void Dispose()
        {
            _source?.Dispose();
            _source = null;
            _session?.Dispose();
            _session = null;
        }
    }

    internal sealed record AssetCatalogTrustEvidence(
        WindowsFileIdentity RootIdentity,
        WindowsFileIdentity CatalogIdentity,
        byte[] CatalogSha256,
        IReadOnlyDictionary<string, AssetCatalogSourceEvidence> Sources)
    {
        internal static AssetCatalogTrustEvidence Empty { get; } = new(
            default,
            default,
            Array.Empty<byte>(),
            new Dictionary<string, AssetCatalogSourceEvidence>(FileMutationSafety.PathComparer));

        internal bool IsPresent => CatalogSha256.Length == 32;
    }

    internal sealed record AssetCatalogSourceEvidence(
        bool Exists,
        WindowsFileIdentity Identity,
        long Length,
        byte[] Sha256)
    {
        internal static AssetCatalogSourceEvidence Missing { get; } = new(
            false,
            default,
            0,
            Array.Empty<byte>());

        internal bool Matches(AssetCatalogSourceEvidence other)
        {
            if (Exists != other.Exists || Length != other.Length)
                return false;
            if (!Exists)
                return true;
            if (OperatingSystem.IsWindows() && !Identity.IsSameFile(other.Identity))
                return false;
            return Sha256.Length != 32 ||
                (other.Sha256.Length == 32 &&
                    CryptographicOperations.FixedTimeEquals(Sha256, other.Sha256));
        }
    }
}
