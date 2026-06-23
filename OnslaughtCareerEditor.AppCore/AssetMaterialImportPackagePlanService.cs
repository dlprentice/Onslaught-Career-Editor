using System;
using System.Collections.Generic;
using System.Linq;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackagePlanService
    {
        public AssetMaterialImportPackagePlan Build(AssetMaterialImportManifest manifest)
        {
            AssetMaterialImportDryRunPlan dryRunPlan = new AssetMaterialImportDryRunPlanService().Build(manifest);
            List<AssetMaterialImportPackageModelOperation> modelOperations = new();

            for (int index = 0; index < manifest.Models.Count; index++)
            {
                AssetMaterialImportManifestModelRow manifestRow = manifest.Models[index];
                AssetMaterialImportDryRunModelOperation dryRunOperation = dryRunPlan.ModelOperations[index];
                modelOperations.Add(BuildModelOperation(manifestRow, dryRunOperation));
            }

            IReadOnlyList<AssetMaterialImportPackageFile> modelFiles = modelOperations
                .Where(static operation => operation.ReadyForPackage)
                .Select(static operation => new AssetMaterialImportPackageFile(
                    Role: "model",
                    DestinationRelativePath: operation.DestinationRelativePath,
                    SourceFileName: operation.ExportFileName,
                    SourceToken: string.IsNullOrWhiteSpace(operation.CatalogId) ? operation.Label : operation.CatalogId,
                    ResolutionKind: "model-export",
                    ReferenceCount: 1,
                    Status: "ready"))
                .ToList();

            IReadOnlyList<AssetMaterialImportPackageFile> textureFiles = modelOperations
                .Where(static operation => operation.ReadyForPackage)
                .SelectMany(static operation => operation.TextureReferences)
                .Where(static texture => texture.SourceAvailable && !string.IsNullOrWhiteSpace(texture.DestinationRelativePath))
                .GroupBy(static texture => texture.DestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                .OrderBy(static group => group.Key, StringComparer.OrdinalIgnoreCase)
                .Select(static group =>
                {
                    AssetMaterialImportPackageTextureReference first = group.First();
                    return new AssetMaterialImportPackageFile(
                        Role: "texture",
                        DestinationRelativePath: group.Key,
                        SourceFileName: first.SourceFileName,
                        SourceToken: first.SourceToken,
                        ResolutionKind: first.ResolutionKind,
                        ReferenceCount: group.Count(),
                        Status: "ready");
                })
                .ToList();

            int resolvedTextureReferences = modelOperations.Sum(static operation =>
                operation.TextureReferences.Count(static texture => texture.SourceAvailable));
            int uniqueTextureFiles = textureFiles.Count;

            return new AssetMaterialImportPackagePlan(
                TotalModelOperations: modelOperations.Count,
                ReadyPackageModelOperations: modelOperations.Count(static operation => operation.ReadyForPackage),
                BlockedPackageModelOperations: modelOperations.Count(static operation => !operation.ReadyForPackage),
                TotalTextureReferences: modelOperations.Sum(static operation => operation.TextureReferences.Count),
                ResolvedTextureReferences: resolvedTextureReferences,
                UnresolvedTextureReferences: modelOperations.Sum(static operation =>
                    operation.TextureReferences.Count(static texture => !texture.SourceAvailable)),
                ModelPackageFiles: modelFiles.Count,
                TexturePackageFiles: uniqueTextureFiles,
                TotalPackageFiles: modelFiles.Count + uniqueTextureFiles,
                DuplicateTextureReferences: Math.Max(0, resolvedTextureReferences - uniqueTextureFiles),
                ModelOperations: modelOperations,
                PackageFiles: modelFiles.Concat(textureFiles).ToList());
        }

        private static AssetMaterialImportPackageModelOperation BuildModelOperation(
            AssetMaterialImportManifestModelRow manifestRow,
            AssetMaterialImportDryRunModelOperation dryRunOperation)
        {
            bool readyForPackage =
                manifestRow.ExportExists &&
                manifestRow.MetadataAvailable &&
                dryRunOperation.ReadyForImport;
            string status = BuildStatus(manifestRow, dryRunOperation);

            return new AssetMaterialImportPackageModelOperation(
                Kind: dryRunOperation.Kind,
                CatalogId: dryRunOperation.CatalogId,
                Label: dryRunOperation.Label,
                ExportFileName: dryRunOperation.ExportFileName,
                DestinationRelativePath: dryRunOperation.DestinationRelativePath,
                ExportExists: manifestRow.ExportExists,
                MetadataAvailable: manifestRow.MetadataAvailable,
                ReadyForPackage: readyForPackage,
                PackageStatus: status,
                TextureReferences: dryRunOperation.TextureOperations
                    .Select(static texture => new AssetMaterialImportPackageTextureReference(
                        BindingFileName: texture.BindingFileName,
                        ResolutionKind: texture.ResolutionKind,
                        SourceToken: texture.SourceToken,
                        SourceFileName: texture.SourceFileName,
                        DestinationRelativePath: texture.DestinationRelativePath,
                        SourceAvailable: texture.SourceAvailable,
                        Status: texture.Status))
                    .ToList());
        }

        private static string BuildStatus(
            AssetMaterialImportManifestModelRow manifestRow,
            AssetMaterialImportDryRunModelOperation dryRunOperation)
        {
            if (!manifestRow.ExportExists)
            {
                return "blocked-missing-model-export";
            }

            if (!manifestRow.MetadataAvailable)
            {
                return "blocked-missing-model-metadata";
            }

            if (!dryRunOperation.ReadyForImport)
            {
                if (dryRunOperation.ImportReadiness == "no-texture-bindings")
                {
                    return "blocked-no-texture-bindings";
                }

                return "blocked-unresolved-textures";
            }

            return "ready";
        }
    }

    public sealed record AssetMaterialImportPackagePlan(
        int TotalModelOperations,
        int ReadyPackageModelOperations,
        int BlockedPackageModelOperations,
        int TotalTextureReferences,
        int ResolvedTextureReferences,
        int UnresolvedTextureReferences,
        int ModelPackageFiles,
        int TexturePackageFiles,
        int TotalPackageFiles,
        int DuplicateTextureReferences,
        IReadOnlyList<AssetMaterialImportPackageModelOperation> ModelOperations,
        IReadOnlyList<AssetMaterialImportPackageFile> PackageFiles);

    public sealed record AssetMaterialImportPackageModelOperation(
        string Kind,
        string CatalogId,
        string Label,
        string ExportFileName,
        string DestinationRelativePath,
        bool ExportExists,
        bool MetadataAvailable,
        bool ReadyForPackage,
        string PackageStatus,
        IReadOnlyList<AssetMaterialImportPackageTextureReference> TextureReferences);

    public sealed record AssetMaterialImportPackageTextureReference(
        string BindingFileName,
        string ResolutionKind,
        string SourceToken,
        string SourceFileName,
        string DestinationRelativePath,
        bool SourceAvailable,
        string Status);

    public sealed record AssetMaterialImportPackageFile(
        string Role,
        string DestinationRelativePath,
        string SourceFileName,
        string SourceToken,
        string ResolutionKind,
        int ReferenceCount,
        string Status);
}
