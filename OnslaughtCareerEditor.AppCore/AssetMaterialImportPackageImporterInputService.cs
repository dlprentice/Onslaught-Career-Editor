using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageImporterInputService
    {
        public const string ImporterInputRootRelativePath = "importer-input";
        public const string ImporterInputManifestFileName = "material-package-importer-input.v1.json";
        public const string ImporterInputManifestSchema = "onslaught.asset-material-package-importer-input.v1";

        private static readonly JsonSerializerOptions WriteJsonOptions = new(JsonSerializerDefaults.Web)
        {
            WriteIndented = true
        };

        public AssetMaterialImportPackageImporterInputMaterializationResult Preflight(string packageRoot)
        {
            return Build(packageRoot, executeCopy: false);
        }

        public AssetMaterialImportPackageImporterInputMaterializationResult Materialize(string packageRoot)
        {
            return Build(packageRoot, executeCopy: true);
        }

        private static AssetMaterialImportPackageImporterInputMaterializationResult Build(
            string packageRoot,
            bool executeCopy)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            string packageRootName = BuildRootName(fullPackageRoot);
            AssetMaterialImportPackageImporterDryRunService dryRunService = new();
            AssetMaterialImportPackageImporterDryRunSidecarValidationResult validation =
                dryRunService.ValidateSidecar(fullPackageRoot);
            AssetMaterialImportPackageImporterDryRunResult dryRun = dryRunService.Build(fullPackageRoot);
            List<AssetMaterialImportPackageImporterInputIssue> issues = validation.Issues
                .Select(static issue => new AssetMaterialImportPackageImporterInputIssue(
                    issue.Role,
                    issue.RelativePath,
                    issue.Status))
                .ToList();

            if (!validation.Completed)
            {
                if (issues.Count == 0)
                {
                    issues.Add(new AssetMaterialImportPackageImporterInputIssue(
                        "sidecar",
                        validation.SidecarRelativePath,
                        validation.SidecarStatus));
                }

                return BuildResult(
                    executeCopy,
                    packageRootName,
                    validation,
                    dryRun,
                    manifestWritten: false,
                    manifestStatus: validation.SidecarStatus,
                    manifestBytes: 0,
                    rows: [],
                    issues);
            }

            HashSet<string> plannedAdapterPaths = new(StringComparer.OrdinalIgnoreCase);
            List<AssetMaterialImportPackageImporterInputRow> rows = dryRun.Rows
                .OrderBy(static row => row.Ordinal)
                .Select(row => BuildRow(
                    fullPackageRoot,
                    row,
                    executeCopy,
                    plannedAdapterPaths,
                    issues))
                .ToList();

            bool completed = rows.All(static row => IsReadyStatus(row.Status)) && issues.Count == 0;
            (bool manifestWritten, string manifestStatus, long manifestBytes) = WriteManifestIfRequested(
                executeCopy,
                fullPackageRoot,
                packageRootName,
                validation,
                rows,
                completed);

            return BuildResult(
                executeCopy,
                packageRootName,
                validation,
                dryRun,
                manifestWritten,
                manifestStatus,
                manifestBytes,
                rows,
                issues);
        }

        private static AssetMaterialImportPackageImporterInputMaterializationResult BuildResult(
            bool executeCopy,
            string packageRootName,
            AssetMaterialImportPackageImporterDryRunSidecarValidationResult validation,
            AssetMaterialImportPackageImporterDryRunResult dryRun,
            bool manifestWritten,
            string manifestStatus,
            long manifestBytes,
            IReadOnlyList<AssetMaterialImportPackageImporterInputRow> rows,
            IReadOnlyList<AssetMaterialImportPackageImporterInputIssue> issues)
        {
            int copiedFiles = rows.Count(static row => row.Status == "copied");
            int wouldCopyFiles = rows.Count(static row => row.Status == "would-copy");
            int existingFilesSkipped = rows.Count(static row => row.Status == "skipped-existing");
            int wouldUsePlannedCopyRows = rows.Count(static row => row.Status == "would-use-planned-copy");
            int existingFilesDetected = rows.Count(static row => row.Status is "skipped-existing" or "would-skip-existing");
            int missingSourceFiles = rows.Count(static row => row.Status == "missing-source");
            int unsafeSourcePaths = rows.Count(static row => row.Status == "unsafe-source-path");
            int unsafeDestinationPaths = rows.Count(static row => row.Status == "unsafe-destination-path");
            int existingHashMismatches = rows.Count(static row => row.Status == "blocked-existing-mismatch");
            int readyInputRows = rows.Count(static row => IsReadyStatus(row.Status));
            int uniqueAdapterFiles = rows
                .Where(static row => IsReadyStatus(row.Status))
                .Select(static row => row.AdapterRelativePath)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .Count();

            return new AssetMaterialImportPackageImporterInputMaterializationResult(
                Executed: executeCopy,
                PackageRootName: packageRootName,
                SourceDryRunSidecarRelativePath: validation.SidecarRelativePath,
                SourceDryRunSidecarStatus: validation.SidecarStatus,
                SourceDryRunSidecarValidated: validation.Completed,
                SourceDryRunCompleted: dryRun.Completed,
                ImporterInputRootRelativePath: ImporterInputRootRelativePath,
                ManifestRelativePath: ImporterInputManifestFileName,
                ManifestWritten: manifestWritten,
                ManifestStatus: manifestStatus,
                ManifestBytes: manifestBytes,
                PlannedAdapterRows: dryRun.PlannedAdapterRows,
                ReadyAdapterRows: dryRun.ReadyAdapterRows,
                InputRowsReady: readyInputRows,
                ModelInputRows: rows.Count(static row => row.Role == "model"),
                TextureInputRows: rows.Count(static row => row.Role == "texture"),
                UniqueAdapterFiles: uniqueAdapterFiles,
                WouldCopyFiles: wouldCopyFiles,
                WouldUsePlannedCopyRows: wouldUsePlannedCopyRows,
                CopiedFiles: copiedFiles,
                ExistingFilesSkipped: existingFilesSkipped,
                ExistingFilesDetected: existingFilesDetected,
                ExistingHashMismatches: existingHashMismatches,
                MissingSourceFiles: missingSourceFiles,
                UnsafeSourcePaths: unsafeSourcePaths,
                UnsafeDestinationPaths: unsafeDestinationPaths,
                Completed: validation.Completed && dryRun.Completed && readyInputRows == dryRun.PlannedAdapterRows && issues.Count == 0,
                Rows: rows,
                Issues: issues);
        }

        private static AssetMaterialImportPackageImporterInputRow BuildRow(
            string fullPackageRoot,
            AssetMaterialImportPackageImporterDryRunRow dryRunRow,
            bool executeCopy,
            HashSet<string> plannedAdapterPaths,
            List<AssetMaterialImportPackageImporterInputIssue> issues)
        {
            string sourceRelativePath = NormalizeRelativePath(dryRunRow.PackageRelativePath);
            string adapterRelativePath = NormalizeRelativePath(dryRunRow.AdapterRelativePath);
            bool sourceSafe = TryResolveInsidePackage(fullPackageRoot, sourceRelativePath, out string fullSourcePath);
            bool adapterSafe = TryResolveInsidePackage(fullPackageRoot, adapterRelativePath, out string fullAdapterPath) &&
                adapterRelativePath.StartsWith(ImporterInputRootRelativePath + "/", StringComparison.OrdinalIgnoreCase);

            if (!sourceSafe)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputIssue(dryRunRow.Role, sourceRelativePath, "unsafe-source-path"));
                return BuildRowResult(dryRunRow, sourceRelativePath, adapterRelativePath, "unsafe-source-path", 0);
            }

            if (!adapterSafe)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputIssue(dryRunRow.Role, adapterRelativePath, "unsafe-destination-path"));
                return BuildRowResult(dryRunRow, sourceRelativePath, adapterRelativePath, "unsafe-destination-path", 0);
            }

            if (!File.Exists(fullSourcePath))
            {
                issues.Add(new AssetMaterialImportPackageImporterInputIssue(dryRunRow.Role, sourceRelativePath, "missing-source"));
                return BuildRowResult(dryRunRow, sourceRelativePath, adapterRelativePath, "missing-source", 0);
            }

            string sourceHash = HashFileSha256(fullSourcePath);
            long sourceBytes = new FileInfo(fullSourcePath).Length;
            bool adapterAlreadyPlanned = !plannedAdapterPaths.Add(adapterRelativePath);

            if (File.Exists(fullAdapterPath))
            {
                string outputHash = HashFileSha256(fullAdapterPath);
                string status = string.Equals(sourceHash, outputHash, StringComparison.OrdinalIgnoreCase)
                    ? executeCopy ? "skipped-existing" : "would-skip-existing"
                    : "blocked-existing-mismatch";
                if (status == "blocked-existing-mismatch")
                {
                    issues.Add(new AssetMaterialImportPackageImporterInputIssue(dryRunRow.Role, adapterRelativePath, status));
                }

                return BuildRowResult(
                    dryRunRow,
                    sourceRelativePath,
                    adapterRelativePath,
                    status,
                    new FileInfo(fullAdapterPath).Length);
            }

            if (adapterAlreadyPlanned && !executeCopy)
            {
                return BuildRowResult(
                    dryRunRow,
                    sourceRelativePath,
                    adapterRelativePath,
                    "would-use-planned-copy",
                    sourceBytes);
            }

            if (!executeCopy)
            {
                return BuildRowResult(
                    dryRunRow,
                    sourceRelativePath,
                    adapterRelativePath,
                    "would-copy",
                    sourceBytes);
            }

            Directory.CreateDirectory(Path.GetDirectoryName(fullAdapterPath)!);
            File.Copy(fullSourcePath, fullAdapterPath, overwrite: false);
            return BuildRowResult(
                dryRunRow,
                sourceRelativePath,
                adapterRelativePath,
                "copied",
                new FileInfo(fullAdapterPath).Length);
        }

        private static (bool Written, string Status, long Bytes) WriteManifestIfRequested(
            bool executeCopy,
            string fullPackageRoot,
            string packageRootName,
            AssetMaterialImportPackageImporterDryRunSidecarValidationResult validation,
            IReadOnlyList<AssetMaterialImportPackageImporterInputRow> rows,
            bool completed)
        {
            if (!executeCopy)
            {
                return (false, "preflight-not-written", 0);
            }

            Directory.CreateDirectory(fullPackageRoot);
            string manifestPath = Path.Combine(fullPackageRoot, ImporterInputManifestFileName);
            AssetMaterialImportPackageImporterInputManifest manifest = new(
                Schema: ImporterInputManifestSchema,
                GeneratedAtUtc: DateTimeOffset.UtcNow,
                PackageRootName: packageRootName,
                SourceDryRunSidecarRelativePath: validation.SidecarRelativePath,
                SourceDryRunSidecarStatus: validation.SidecarStatus,
                ImporterInputRootRelativePath: ImporterInputRootRelativePath,
                PlannedAdapterRows: validation.FreshPlannedAdapterRows,
                ReadyAdapterRows: validation.FreshReadyAdapterRows,
                UniqueAdapterFiles: rows
                    .Where(static row => IsReadyStatus(row.Status))
                    .Select(static row => row.AdapterRelativePath)
                    .Distinct(StringComparer.OrdinalIgnoreCase)
                    .Count(),
                Completed: completed,
                Rows: rows
                    .OrderBy(static row => row.Ordinal)
                    .ToList());
            File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, WriteJsonOptions));
            return (true, "written", new FileInfo(manifestPath).Length);
        }

        private static AssetMaterialImportPackageImporterInputRow BuildRowResult(
            AssetMaterialImportPackageImporterDryRunRow dryRunRow,
            string sourceRelativePath,
            string adapterRelativePath,
            string status,
            long outputBytes)
        {
            return new AssetMaterialImportPackageImporterInputRow(
                Ordinal: dryRunRow.Ordinal,
                Role: dryRunRow.Role,
                CatalogId: dryRunRow.CatalogId,
                Label: dryRunRow.Label,
                BindingFileName: dryRunRow.BindingFileName,
                AdapterAction: dryRunRow.AdapterAction,
                SourcePackageRelativePath: sourceRelativePath,
                AdapterRelativePath: adapterRelativePath,
                Status: status,
                OutputBytes: outputBytes);
        }

        private static bool TryResolveInsidePackage(string fullPackageRoot, string relativePath, out string fullPath)
        {
            fullPath = string.Empty;
            if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathRooted(relativePath))
            {
                return false;
            }

            string candidate = Path.GetFullPath(Path.Combine(
                fullPackageRoot,
                relativePath.Replace('/', Path.DirectorySeparatorChar).Replace('\\', Path.DirectorySeparatorChar)));
            string root = fullPackageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) +
                Path.DirectorySeparatorChar;
            if (!candidate.StartsWith(root, StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            fullPath = candidate;
            return true;
        }

        private static bool IsReadyStatus(string status)
        {
            return status is "would-copy" or "would-use-planned-copy" or "would-skip-existing" or "copied" or "skipped-existing";
        }

        private static string HashFileSha256(string path)
        {
            using FileStream stream = File.OpenRead(path);
            return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
        }

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }

        private static string NormalizeRelativePath(string value)
        {
            return value.Replace('\\', '/');
        }
    }

    public sealed record AssetMaterialImportPackageImporterInputMaterializationResult(
        bool Executed,
        string PackageRootName,
        string SourceDryRunSidecarRelativePath,
        string SourceDryRunSidecarStatus,
        bool SourceDryRunSidecarValidated,
        bool SourceDryRunCompleted,
        string ImporterInputRootRelativePath,
        string ManifestRelativePath,
        bool ManifestWritten,
        string ManifestStatus,
        long ManifestBytes,
        int PlannedAdapterRows,
        int ReadyAdapterRows,
        int InputRowsReady,
        int ModelInputRows,
        int TextureInputRows,
        int UniqueAdapterFiles,
        int WouldCopyFiles,
        int WouldUsePlannedCopyRows,
        int CopiedFiles,
        int ExistingFilesSkipped,
        int ExistingFilesDetected,
        int ExistingHashMismatches,
        int MissingSourceFiles,
        int UnsafeSourcePaths,
        int UnsafeDestinationPaths,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageImporterInputRow> Rows,
        IReadOnlyList<AssetMaterialImportPackageImporterInputIssue> Issues);

    public sealed record AssetMaterialImportPackageImporterInputRow(
        int Ordinal,
        string Role,
        string CatalogId,
        string Label,
        string BindingFileName,
        string AdapterAction,
        string SourcePackageRelativePath,
        string AdapterRelativePath,
        string Status,
        long OutputBytes);

    public sealed record AssetMaterialImportPackageImporterInputIssue(
        string Role,
        string RelativePath,
        string Status);

    public sealed record AssetMaterialImportPackageImporterInputManifest(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        string PackageRootName,
        string SourceDryRunSidecarRelativePath,
        string SourceDryRunSidecarStatus,
        string ImporterInputRootRelativePath,
        int PlannedAdapterRows,
        int ReadyAdapterRows,
        int UniqueAdapterFiles,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageImporterInputRow> Rows);
}
