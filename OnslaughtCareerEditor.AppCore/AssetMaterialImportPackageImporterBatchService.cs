using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageImporterBatchService
    {
        public const string ImporterBatchSchema = "onslaught.asset-material-package-importer-batch.v1";

        public AssetMaterialImportPackageImporterBatchResult Build(string packageRoot)
        {
            AssetMaterialImportPackageWorkOrderService workOrderService = new();
            AssetMaterialImportPackageWorkOrderSidecarValidationResult sidecarValidation =
                workOrderService.ValidateSidecar(packageRoot);
            AssetMaterialImportPackageWorkOrderResult workOrder = workOrderService.Build(packageRoot);

            IReadOnlyList<AssetMaterialImportPackageImporterBatchIssue> issues = sidecarValidation.Issues
                .Select(static issue => new AssetMaterialImportPackageImporterBatchIssue(
                    Role: issue.Role,
                    RelativePath: issue.RelativePath,
                    Status: issue.Status))
                .ToList();

            if (!sidecarValidation.Completed)
            {
                return new AssetMaterialImportPackageImporterBatchResult(
                    PackageRootName: sidecarValidation.PackageRootName,
                    SidecarRelativePath: sidecarValidation.SidecarRelativePath,
                    SidecarStatus: sidecarValidation.SidecarStatus,
                    SidecarValidated: false,
                    WorkOrderCompleted: workOrder.Completed,
                    ModelTaskRows: 0,
                    TextureTaskRows: 0,
                    TotalTaskRows: 0,
                    ReadyTaskRows: 0,
                    BlockedTaskRows: 0,
                    Completed: false,
                    Tasks: [],
                    Issues: issues.Count == 0
                        ? [new AssetMaterialImportPackageImporterBatchIssue("sidecar", sidecarValidation.SidecarRelativePath, sidecarValidation.SidecarStatus)]
                        : issues);
            }

            List<AssetMaterialImportPackageImporterBatchTask> tasks = new();
            int ordinal = 1;
            foreach (AssetMaterialImportPackageWorkOrderModel model in workOrder.Models
                .OrderBy(static model => model.ModelDestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                .ThenBy(static model => model.CatalogId, StringComparer.OrdinalIgnoreCase))
            {
                tasks.Add(BuildModelTask(ordinal++, model));
                foreach (AssetMaterialImportPackageWorkOrderTexture texture in model.Textures
                    .OrderBy(static texture => texture.DestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static texture => texture.BindingFileName, StringComparer.OrdinalIgnoreCase))
                {
                    tasks.Add(BuildTextureTask(ordinal++, model, texture));
                }
            }

            int modelTaskRows = tasks.Count(static task => task.Role == "model");
            int textureTaskRows = tasks.Count(static task => task.Role == "texture");
            int readyTaskRows = tasks.Count(static task => task.ReadyForImporter);
            int blockedTaskRows = tasks.Count - readyTaskRows;

            return new AssetMaterialImportPackageImporterBatchResult(
                PackageRootName: sidecarValidation.PackageRootName,
                SidecarRelativePath: sidecarValidation.SidecarRelativePath,
                SidecarStatus: sidecarValidation.SidecarStatus,
                SidecarValidated: true,
                WorkOrderCompleted: workOrder.Completed,
                ModelTaskRows: modelTaskRows,
                TextureTaskRows: textureTaskRows,
                TotalTaskRows: tasks.Count,
                ReadyTaskRows: readyTaskRows,
                BlockedTaskRows: blockedTaskRows,
                Completed: workOrder.Completed && blockedTaskRows == 0,
                Tasks: tasks,
                Issues: []);
        }

        private static AssetMaterialImportPackageImporterBatchTask BuildModelTask(
            int ordinal,
            AssetMaterialImportPackageWorkOrderModel model)
        {
            string packageRelativePath = NormalizeRelativePath(model.ModelDestinationRelativePath);
            bool safePath = IsSafePackageRelativePath(packageRelativePath);
            bool ready = model.ReadyForImporter && safePath;
            string status = safePath ? model.ImportReadiness : "unsafe-package-path";

            return new AssetMaterialImportPackageImporterBatchTask(
                Ordinal: ordinal,
                Role: "model",
                CatalogId: model.CatalogId,
                Label: model.Label,
                BindingFileName: string.Empty,
                ResolutionKind: "model-export",
                PackageRelativePath: packageRelativePath,
                SourceToken: model.ExportFileName,
                ReadyForImporter: ready,
                TaskStatus: status);
        }

        private static AssetMaterialImportPackageImporterBatchTask BuildTextureTask(
            int ordinal,
            AssetMaterialImportPackageWorkOrderModel model,
            AssetMaterialImportPackageWorkOrderTexture texture)
        {
            string packageRelativePath = NormalizeRelativePath(texture.DestinationRelativePath);
            bool safePath = IsSafePackageRelativePath(packageRelativePath);
            bool ready = texture.ReadyForImporter && safePath;
            string status = safePath ? texture.TextureReadiness : "unsafe-package-path";

            return new AssetMaterialImportPackageImporterBatchTask(
                Ordinal: ordinal,
                Role: "texture",
                CatalogId: model.CatalogId,
                Label: model.Label,
                BindingFileName: texture.BindingFileName,
                ResolutionKind: texture.ResolutionKind,
                PackageRelativePath: packageRelativePath,
                SourceToken: texture.SourceToken,
                ReadyForImporter: ready,
                TaskStatus: status);
        }

        private static bool IsSafePackageRelativePath(string value)
        {
            if (string.IsNullOrWhiteSpace(value) ||
                Path.IsPathRooted(value) ||
                value.Contains(':', StringComparison.Ordinal))
            {
                return false;
            }

            return value
                .Split(['/', '\\'], StringSplitOptions.RemoveEmptyEntries)
                .All(static segment => segment != "..");
        }

        private static string NormalizeRelativePath(string value)
        {
            return value.Replace('\\', '/');
        }
    }

    public sealed record AssetMaterialImportPackageImporterBatchResult(
        string PackageRootName,
        string SidecarRelativePath,
        string SidecarStatus,
        bool SidecarValidated,
        bool WorkOrderCompleted,
        int ModelTaskRows,
        int TextureTaskRows,
        int TotalTaskRows,
        int ReadyTaskRows,
        int BlockedTaskRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageImporterBatchTask> Tasks,
        IReadOnlyList<AssetMaterialImportPackageImporterBatchIssue> Issues);

    public sealed record AssetMaterialImportPackageImporterBatchTask(
        int Ordinal,
        string Role,
        string CatalogId,
        string Label,
        string BindingFileName,
        string ResolutionKind,
        string PackageRelativePath,
        string SourceToken,
        bool ReadyForImporter,
        string TaskStatus);

    public sealed record AssetMaterialImportPackageImporterBatchIssue(
        string Role,
        string RelativePath,
        string Status);
}
