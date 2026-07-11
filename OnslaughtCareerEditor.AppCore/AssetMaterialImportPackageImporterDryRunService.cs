using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageImporterDryRunService
    {
        public const string DryRunFileName = "material-package-importer-dry-run.v1.json";
        public const string DryRunSchema = "onslaught.asset-material-package-importer-dry-run.v1";

        private static readonly JsonSerializerOptions WriteJsonOptions = new(JsonSerializerDefaults.Web)
        {
            WriteIndented = true
        };

        private static readonly JsonSerializerOptions ReadJsonOptions = new()
        {
            PropertyNameCaseInsensitive = true
        };

        public AssetMaterialImportPackageImporterDryRunResult Build(string packageRoot)
        {
            AssetMaterialImportPackageImporterBatchResult batch =
                new AssetMaterialImportPackageImporterBatchService().Build(packageRoot);
            IReadOnlyList<AssetMaterialImportPackageImporterDryRunIssue> issues = batch.Issues
                .Select(static issue => new AssetMaterialImportPackageImporterDryRunIssue(
                    issue.Role,
                    issue.RelativePath,
                    issue.Status))
                .ToList();

            if (!batch.Completed)
            {
                return new AssetMaterialImportPackageImporterDryRunResult(
                    PackageRootName: batch.PackageRootName,
                    SourceBatchSidecarRelativePath: batch.SidecarRelativePath,
                    SourceBatchStatus: batch.SidecarStatus,
                    SourceBatchValidated: batch.SidecarValidated,
                    SourceBatchCompleted: batch.Completed,
                    ModelTaskRows: batch.ModelTaskRows,
                    TextureTaskRows: batch.TextureTaskRows,
                    TotalTaskRows: batch.TotalTaskRows,
                    ReadyTaskRows: batch.ReadyTaskRows,
                    BlockedTaskRows: batch.BlockedTaskRows,
                    PlannedAdapterRows: 0,
                    ReadyAdapterRows: 0,
                    Completed: false,
                    Rows: [],
                    Issues: issues.Count == 0
                        ? [new AssetMaterialImportPackageImporterDryRunIssue("batch", batch.SidecarRelativePath, batch.SidecarStatus)]
                        : issues);
            }

            List<AssetMaterialImportPackageImporterDryRunRow> rows = batch.Tasks
                .OrderBy(static task => task.Ordinal)
                .Select(static task => BuildRow(task))
                .ToList();
            int readyAdapterRows = rows.Count(static row => row.ReadyForAdapter);

            return new AssetMaterialImportPackageImporterDryRunResult(
                PackageRootName: batch.PackageRootName,
                SourceBatchSidecarRelativePath: batch.SidecarRelativePath,
                SourceBatchStatus: batch.SidecarStatus,
                SourceBatchValidated: batch.SidecarValidated,
                SourceBatchCompleted: batch.Completed,
                ModelTaskRows: batch.ModelTaskRows,
                TextureTaskRows: batch.TextureTaskRows,
                TotalTaskRows: batch.TotalTaskRows,
                ReadyTaskRows: batch.ReadyTaskRows,
                BlockedTaskRows: batch.BlockedTaskRows,
                PlannedAdapterRows: rows.Count,
                ReadyAdapterRows: readyAdapterRows,
                Completed: readyAdapterRows == rows.Count && batch.Completed,
                Rows: rows,
                Issues: []);
        }

        public AssetMaterialImportPackageImporterDryRunSidecarWriteResult WriteSidecar(string packageRoot)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            if (!Directory.Exists(fullPackageRoot))
            {
                AssetMaterialImportPackageImporterDryRunResult missingDryRun = Build(fullPackageRoot);
                return new AssetMaterialImportPackageImporterDryRunSidecarWriteResult(
                    SidecarRelativePath: DryRunFileName,
                    SidecarWritten: false,
                    SidecarStatus: "missing-package-root",
                    SidecarBytes: 0,
                    ImporterDryRun: missingDryRun);
            }

            try
            {
                using var operationRoot = new GuardedPackageOutputRoot(
                    fullPackageRoot,
                    trustedSourceRoot: null,
                    execute: false,
                    requireExistingRoot: true);
                AssetMaterialImportPackageImporterDryRunResult dryRun = Build(fullPackageRoot);

                if (!dryRun.Completed)
                {
                    return new AssetMaterialImportPackageImporterDryRunSidecarWriteResult(
                        SidecarRelativePath: DryRunFileName,
                        SidecarWritten: false,
                        SidecarStatus: "source-not-ready-not-written",
                        SidecarBytes: 0,
                        ImporterDryRun: dryRun);
                }

                AssetMaterialImportPackageImporterDryRunSidecar sidecar = new(
                    Schema: DryRunSchema,
                    GeneratedAtUtc: DateTimeOffset.UtcNow,
                    MaterialPackageImporterDryRun: dryRun);
                GuardedArtifactWriteResult write = GuardedPackageArtifactWriter.ReplaceText(
                    fullPackageRoot,
                    DryRunFileName,
                    JsonSerializer.Serialize(sidecar, WriteJsonOptions),
                    System.Text.Encoding.UTF8);
                return new AssetMaterialImportPackageImporterDryRunSidecarWriteResult(
                    SidecarRelativePath: DryRunFileName,
                    SidecarWritten: true,
                    SidecarStatus: "written",
                    SidecarBytes: write.Bytes,
                    ImporterDryRun: dryRun);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                AssetMaterialImportPackageImporterDryRunResult unsafeDryRun = Build(fullPackageRoot);
                return new AssetMaterialImportPackageImporterDryRunSidecarWriteResult(
                    SidecarRelativePath: DryRunFileName,
                    SidecarWritten: false,
                    SidecarStatus: "unsafe-sidecar-path",
                    SidecarBytes: 0,
                    ImporterDryRun: unsafeDryRun);
            }
        }

        public AssetMaterialImportPackageImporterDryRunSidecarValidationResult ValidateSidecar(string packageRoot)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            string packageRootName = BuildRootName(fullPackageRoot);
            AssetMaterialImportPackageImporterDryRunResult freshDryRun = Build(fullPackageRoot);

            if (!Directory.Exists(fullPackageRoot))
            {
                return BuildSidecarValidationFailure(
                    packageRootName,
                    "missing-package-root",
                    sidecarExists: false,
                    freshDryRun,
                    [new AssetMaterialImportPackageImporterDryRunSidecarValidationIssue("sidecar", DryRunFileName, "missing-package-root")]);
            }

            string sidecarJson;
            long sidecarBytes;
            try
            {
                using GuardedPackageArtifactRead sidecarRead = GuardedPackageArtifactReader.Open(
                    fullPackageRoot,
                    DryRunFileName,
                    "Material package importer dry-run sidecar");
                if (!sidecarRead.Exists)
                {
                    return BuildSidecarValidationFailure(
                        packageRootName,
                        "missing-sidecar",
                        sidecarExists: false,
                        freshDryRun,
                        [new AssetMaterialImportPackageImporterDryRunSidecarValidationIssue("sidecar", DryRunFileName, "missing-sidecar")]);
                }

                sidecarJson = sidecarRead.ReadAllText(System.Text.Encoding.UTF8);
                sidecarBytes = sidecarRead.Length;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return BuildSidecarValidationFailure(
                    packageRootName,
                    "unsafe-sidecar-path",
                    sidecarExists: false,
                    freshDryRun,
                    [new AssetMaterialImportPackageImporterDryRunSidecarValidationIssue("sidecar", DryRunFileName, "unsafe-sidecar-path")]);
            }

            bool sidecarContainsPackageRoot = ContainsPathToken(sidecarJson, fullPackageRoot);
            AssetMaterialImportPackageImporterDryRunSidecar? sidecar;
            try
            {
                sidecar = JsonSerializer.Deserialize<AssetMaterialImportPackageImporterDryRunSidecar>(
                    sidecarJson,
                    ReadJsonOptions);
            }
            catch (JsonException)
            {
                return BuildSidecarValidationFailure(
                    packageRootName,
                    "invalid-json",
                    sidecarExists: true,
                    freshDryRun,
                    [new AssetMaterialImportPackageImporterDryRunSidecarValidationIssue("sidecar", DryRunFileName, "invalid-json")],
                    sidecarBytes: sidecarBytes,
                    sidecarContainsPackageRoot: sidecarContainsPackageRoot);
            }

            if (sidecar is null || sidecar.MaterialPackageImporterDryRun is null)
            {
                return BuildSidecarValidationFailure(
                    packageRootName,
                    "empty-sidecar",
                    sidecarExists: true,
                    freshDryRun,
                    [new AssetMaterialImportPackageImporterDryRunSidecarValidationIssue("sidecar", DryRunFileName, "empty-sidecar")],
                    sidecarBytes: sidecarBytes,
                    sidecarContainsPackageRoot: sidecarContainsPackageRoot);
            }

            AssetMaterialImportPackageImporterDryRunResult sidecarDryRun = sidecar.MaterialPackageImporterDryRun;
            bool schemaValid = string.Equals(sidecar.Schema, DryRunSchema, StringComparison.Ordinal);
            bool dryRunMatchesFreshBuild = DryRunPayloadsMatch(sidecarDryRun, freshDryRun);
            List<AssetMaterialImportPackageImporterDryRunSidecarValidationIssue> issues = new();
            if (!schemaValid)
            {
                issues.Add(new AssetMaterialImportPackageImporterDryRunSidecarValidationIssue("sidecar", DryRunFileName, "invalid-schema"));
            }

            if (sidecarContainsPackageRoot)
            {
                issues.Add(new AssetMaterialImportPackageImporterDryRunSidecarValidationIssue("sidecar", DryRunFileName, "package-root-leak"));
            }

            if (!dryRunMatchesFreshBuild)
            {
                issues.Add(new AssetMaterialImportPackageImporterDryRunSidecarValidationIssue("sidecar", DryRunFileName, "importer-dry-run-mismatch"));
            }

            bool completed =
                schemaValid &&
                !sidecarContainsPackageRoot &&
                sidecarDryRun.Completed &&
                freshDryRun.Completed &&
                dryRunMatchesFreshBuild;
            string status = completed
                ? "ok"
                : schemaValid && dryRunMatchesFreshBuild
                    ? "issues-found"
                    : schemaValid
                        ? "stale-importer-dry-run-sidecar"
                        : "invalid-schema";

            return new AssetMaterialImportPackageImporterDryRunSidecarValidationResult(
                PackageRootName: packageRootName,
                SidecarRelativePath: DryRunFileName,
                SidecarExists: true,
                SidecarStatus: status,
                SidecarBytes: sidecarBytes,
                Schema: sidecar.Schema,
                SchemaValid: schemaValid,
                SidecarContainsPackageRoot: sidecarContainsPackageRoot,
                SidecarCompletedFlag: sidecarDryRun.Completed,
                FreshDryRunCompleted: freshDryRun.Completed,
                DryRunMatchesFreshBuild: dryRunMatchesFreshBuild,
                SidecarPlannedAdapterRows: sidecarDryRun.PlannedAdapterRows,
                FreshPlannedAdapterRows: freshDryRun.PlannedAdapterRows,
                SidecarReadyAdapterRows: sidecarDryRun.ReadyAdapterRows,
                FreshReadyAdapterRows: freshDryRun.ReadyAdapterRows,
                SidecarTotalTaskRows: sidecarDryRun.TotalTaskRows,
                FreshTotalTaskRows: freshDryRun.TotalTaskRows,
                SidecarReadyTaskRows: sidecarDryRun.ReadyTaskRows,
                FreshReadyTaskRows: freshDryRun.ReadyTaskRows,
                SidecarBlockedTaskRows: sidecarDryRun.BlockedTaskRows,
                FreshBlockedTaskRows: freshDryRun.BlockedTaskRows,
                Completed: completed,
                Issues: issues);
        }

        private static AssetMaterialImportPackageImporterDryRunRow BuildRow(
            AssetMaterialImportPackageImporterBatchTask task)
        {
            return new AssetMaterialImportPackageImporterDryRunRow(
                Ordinal: task.Ordinal,
                Role: task.Role,
                CatalogId: task.CatalogId,
                Label: task.Label,
                BindingFileName: task.BindingFileName,
                AdapterAction: BuildAdapterAction(task.Role),
                PackageRelativePath: task.PackageRelativePath,
                AdapterRelativePath: $"importer-input/{task.PackageRelativePath}",
                SourceToken: task.SourceToken,
                ReadyForAdapter: task.ReadyForImporter,
                TaskStatus: task.TaskStatus);
        }

        private static string BuildAdapterAction(string role)
        {
            return role.Equals("model", StringComparison.OrdinalIgnoreCase)
                ? "queue-model-import"
                : role.Equals("texture", StringComparison.OrdinalIgnoreCase)
                    ? "queue-texture-bind"
                    : "inspect-task";
        }

        private static AssetMaterialImportPackageImporterDryRunSidecarValidationResult BuildSidecarValidationFailure(
            string packageRootName,
            string status,
            bool sidecarExists,
            AssetMaterialImportPackageImporterDryRunResult freshDryRun,
            IReadOnlyList<AssetMaterialImportPackageImporterDryRunSidecarValidationIssue> issues,
            long sidecarBytes = 0,
            bool sidecarContainsPackageRoot = false)
        {
            return new AssetMaterialImportPackageImporterDryRunSidecarValidationResult(
                PackageRootName: packageRootName,
                SidecarRelativePath: DryRunFileName,
                SidecarExists: sidecarExists,
                SidecarStatus: status,
                SidecarBytes: sidecarBytes,
                Schema: string.Empty,
                SchemaValid: false,
                SidecarContainsPackageRoot: sidecarContainsPackageRoot,
                SidecarCompletedFlag: false,
                FreshDryRunCompleted: freshDryRun.Completed,
                DryRunMatchesFreshBuild: false,
                SidecarPlannedAdapterRows: 0,
                FreshPlannedAdapterRows: freshDryRun.PlannedAdapterRows,
                SidecarReadyAdapterRows: 0,
                FreshReadyAdapterRows: freshDryRun.ReadyAdapterRows,
                SidecarTotalTaskRows: 0,
                FreshTotalTaskRows: freshDryRun.TotalTaskRows,
                SidecarReadyTaskRows: 0,
                FreshReadyTaskRows: freshDryRun.ReadyTaskRows,
                SidecarBlockedTaskRows: 0,
                FreshBlockedTaskRows: freshDryRun.BlockedTaskRows,
                Completed: false,
                Issues: issues);
        }

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }

        private static bool DryRunPayloadsMatch(
            AssetMaterialImportPackageImporterDryRunResult sidecarDryRun,
            AssetMaterialImportPackageImporterDryRunResult freshDryRun)
        {
            return string.Equals(
                JsonSerializer.Serialize(sidecarDryRun, WriteJsonOptions),
                JsonSerializer.Serialize(freshDryRun, WriteJsonOptions),
                StringComparison.Ordinal);
        }

        private static bool ContainsPathToken(string text, string fullPackageRoot)
        {
            string normalized = fullPackageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            return text.Contains(normalized, StringComparison.OrdinalIgnoreCase) ||
                   text.Contains(normalized.Replace("\\", "\\\\"), StringComparison.OrdinalIgnoreCase) ||
                   text.Contains(normalized.Replace('\\', '/'), StringComparison.OrdinalIgnoreCase);
        }
    }

    public sealed record AssetMaterialImportPackageImporterDryRunResult(
        string PackageRootName,
        string SourceBatchSidecarRelativePath,
        string SourceBatchStatus,
        bool SourceBatchValidated,
        bool SourceBatchCompleted,
        int ModelTaskRows,
        int TextureTaskRows,
        int TotalTaskRows,
        int ReadyTaskRows,
        int BlockedTaskRows,
        int PlannedAdapterRows,
        int ReadyAdapterRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageImporterDryRunRow> Rows,
        IReadOnlyList<AssetMaterialImportPackageImporterDryRunIssue> Issues);

    public sealed record AssetMaterialImportPackageImporterDryRunRow(
        int Ordinal,
        string Role,
        string CatalogId,
        string Label,
        string BindingFileName,
        string AdapterAction,
        string PackageRelativePath,
        string AdapterRelativePath,
        string SourceToken,
        bool ReadyForAdapter,
        string TaskStatus);

    public sealed record AssetMaterialImportPackageImporterDryRunIssue(
        string Role,
        string RelativePath,
        string Status);

    public sealed record AssetMaterialImportPackageImporterDryRunSidecar(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        AssetMaterialImportPackageImporterDryRunResult MaterialPackageImporterDryRun);

    public sealed record AssetMaterialImportPackageImporterDryRunSidecarWriteResult(
        string SidecarRelativePath,
        bool SidecarWritten,
        string SidecarStatus,
        long SidecarBytes,
        AssetMaterialImportPackageImporterDryRunResult ImporterDryRun);

    public sealed record AssetMaterialImportPackageImporterDryRunSidecarValidationResult(
        string PackageRootName,
        string SidecarRelativePath,
        bool SidecarExists,
        string SidecarStatus,
        long SidecarBytes,
        string Schema,
        bool SchemaValid,
        bool SidecarContainsPackageRoot,
        bool SidecarCompletedFlag,
        bool FreshDryRunCompleted,
        bool DryRunMatchesFreshBuild,
        int SidecarPlannedAdapterRows,
        int FreshPlannedAdapterRows,
        int SidecarReadyAdapterRows,
        int FreshReadyAdapterRows,
        int SidecarTotalTaskRows,
        int FreshTotalTaskRows,
        int SidecarReadyTaskRows,
        int FreshReadyTaskRows,
        int SidecarBlockedTaskRows,
        int FreshBlockedTaskRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageImporterDryRunSidecarValidationIssue> Issues);

    public sealed record AssetMaterialImportPackageImporterDryRunSidecarValidationIssue(
        string Role,
        string RelativePath,
        string Status);
}
