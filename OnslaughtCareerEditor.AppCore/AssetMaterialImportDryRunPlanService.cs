using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportDryRunPlanService
    {
        public AssetMaterialImportDryRunPlan Build(AssetMaterialImportManifest manifest)
        {
            List<AssetMaterialImportDryRunModelOperation> modelOperations = manifest.Models
                .Select(BuildModelOperation)
                .ToList();
            int totalTextureOperations = modelOperations.Sum(static operation => operation.TextureOperations.Count);
            int catalogTextureOperations = modelOperations.Sum(static operation =>
                operation.TextureOperations.Count(static texture => texture.ResolutionKind == "catalog"));
            int sidecarTextureOperations = modelOperations.Sum(static operation =>
                operation.TextureOperations.Count(static texture => texture.ResolutionKind == "sidecar"));
            int unresolvedTextureOperations = modelOperations.Sum(static operation =>
                operation.TextureOperations.Count(static texture => texture.ResolutionKind == "unresolved"));

            return new AssetMaterialImportDryRunPlan(
                TotalModelOperations: modelOperations.Count,
                ReadyModelOperations: modelOperations.Count(static operation => operation.ReadyForImport),
                BlockedModelOperations: modelOperations.Count(static operation => !operation.ReadyForImport),
                TotalTextureOperations: totalTextureOperations,
                CatalogTextureOperations: catalogTextureOperations,
                SidecarTextureOperations: sidecarTextureOperations,
                UnresolvedTextureOperations: unresolvedTextureOperations,
                ModelOperations: modelOperations);
        }

        private static AssetMaterialImportDryRunModelOperation BuildModelOperation(AssetMaterialImportManifestModelRow row)
        {
            string kindFolder = BuildRelativeSegment(row.Kind);
            string modelStem = BuildRelativeSegment(string.IsNullOrWhiteSpace(row.CatalogId) ? row.Label : row.CatalogId);
            string exportFileName = BuildSafeFileName(row.ExportFileName, fallbackFileName: "model.fbx");
            string destinationRelativePath = $"models/{kindFolder}/{modelStem}/{exportFileName}";
            IReadOnlyList<AssetMaterialImportDryRunTextureOperation> textureOperations = row.TextureBindings
                .Select(binding => BuildTextureOperation(modelStem, binding))
                .ToList();

            return new AssetMaterialImportDryRunModelOperation(
                Kind: row.Kind,
                CatalogId: row.CatalogId,
                Label: row.Label,
                ExportFileName: exportFileName,
                DestinationRelativePath: destinationRelativePath,
                ReadyForImport: row.ImportReadiness == "ready",
                ImportReadiness: row.ImportReadiness,
                TextureOperations: textureOperations);
        }

        private static AssetMaterialImportDryRunTextureOperation BuildTextureOperation(
            string modelStem,
            AssetModelTextureBindingResolution binding)
        {
            string bindingFileName = BuildSafeFileName(binding.BindingFileName, fallbackFileName: "texture.png");
            string sourceFileName = binding.ResolutionKind switch
            {
                "catalog" => BuildSafeFileName(binding.CatalogTextureExportFileName, bindingFileName),
                "sidecar" => BuildSafeFileName(binding.SidecarTextureFileName, bindingFileName),
                _ => string.Empty
            };
            string sourceToken = binding.ResolutionKind switch
            {
                "catalog" => string.IsNullOrWhiteSpace(binding.CatalogTextureId) ? binding.CatalogTextureName : binding.CatalogTextureId,
                "sidecar" => sourceFileName,
                _ => bindingFileName
            };
            string destinationRelativePath = binding.ResolutionKind switch
            {
                "catalog" => $"textures/catalog/{BuildRelativeSegment(sourceToken)}/{sourceFileName}",
                "sidecar" => $"textures/sidecar/{modelStem}/{sourceFileName}",
                _ => string.Empty
            };

            return new AssetMaterialImportDryRunTextureOperation(
                BindingFileName: bindingFileName,
                ResolutionKind: binding.ResolutionKind,
                SourceToken: SanitizeToken(sourceToken),
                SourceFileName: sourceFileName,
                DestinationRelativePath: destinationRelativePath,
                SourceAvailable: binding.ResolutionKind is "catalog" or "sidecar",
                Status: binding.Status);
        }

        private static string BuildSafeFileName(string value, string fallbackFileName)
        {
            string fileName = Path.GetFileName(value.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar));
            if (string.IsNullOrWhiteSpace(fileName))
            {
                fileName = fallbackFileName;
            }

            string sanitized = SanitizeToken(fileName);
            return string.IsNullOrWhiteSpace(sanitized) ? fallbackFileName : sanitized;
        }

        private static string BuildRelativeSegment(string value)
        {
            string sanitized = SanitizeToken(value);
            return string.IsNullOrWhiteSpace(sanitized) ? "unknown" : sanitized;
        }

        private static string SanitizeToken(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return string.Empty;
            }

            StringBuilder builder = new(value.Length);
            foreach (char ch in value.Trim())
            {
                if (char.IsLetterOrDigit(ch) || ch is '.' or '-' or '_')
                {
                    builder.Append(ch);
                }
                else
                {
                    builder.Append('_');
                }
            }

            string result = builder.ToString().Trim('_');
            while (result.Contains("__", StringComparison.Ordinal))
            {
                result = result.Replace("__", "_", StringComparison.Ordinal);
            }

            return result;
        }
    }

    public sealed record AssetMaterialImportDryRunPlan(
        int TotalModelOperations,
        int ReadyModelOperations,
        int BlockedModelOperations,
        int TotalTextureOperations,
        int CatalogTextureOperations,
        int SidecarTextureOperations,
        int UnresolvedTextureOperations,
        IReadOnlyList<AssetMaterialImportDryRunModelOperation> ModelOperations);

    public sealed record AssetMaterialImportDryRunModelOperation(
        string Kind,
        string CatalogId,
        string Label,
        string ExportFileName,
        string DestinationRelativePath,
        bool ReadyForImport,
        string ImportReadiness,
        IReadOnlyList<AssetMaterialImportDryRunTextureOperation> TextureOperations);

    public sealed record AssetMaterialImportDryRunTextureOperation(
        string BindingFileName,
        string ResolutionKind,
        string SourceToken,
        string SourceFileName,
        string DestinationRelativePath,
        bool SourceAvailable,
        string Status);
}
