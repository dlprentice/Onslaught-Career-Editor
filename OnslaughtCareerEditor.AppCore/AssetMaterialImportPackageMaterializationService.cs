using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageMaterializationService
    {
        public const string ManifestFileName = "material-package-manifest.v1.json";
        public const string ManifestSchema = "onslaught.asset-material-package-manifest.v1";
        private readonly Action<string>? _beforeManifestWriteForTest;
        private readonly Action<string>? _afterExistingRootBranchForTest;
        private readonly Action<string>? _beforeFirstPublicationForTest;
        private readonly Action<string>? _afterSealPreparedForTest;

        public AssetMaterialImportPackageMaterializationService()
        {
        }

        internal AssetMaterialImportPackageMaterializationService(
            Action<string> beforeManifestWriteForTest,
            Action<string>? afterExistingRootBranchForTest = null,
            Action<string>? beforeFirstPublicationForTest = null,
            Action<string>? afterSealPreparedForTest = null)
        {
            _beforeManifestWriteForTest = beforeManifestWriteForTest;
            _afterExistingRootBranchForTest = afterExistingRootBranchForTest;
            _beforeFirstPublicationForTest = beforeFirstPublicationForTest;
            _afterSealPreparedForTest = afterSealPreparedForTest;
        }

        public AssetMaterialImportPackageMaterializationResult Preflight(
            AssetCatalogSnapshot snapshot,
            string outputRoot)
        {
            return Build(snapshot, outputRoot, executeCopy: false);
        }

        public AssetMaterialImportPackageMaterializationResult Materialize(
            AssetCatalogSnapshot snapshot,
            string outputRoot)
        {
            string normalizedOutputRoot = FileMutationSafety.NormalizeLocalPath(
                outputRoot,
                "Material package output root");
            if (Directory.Exists(normalizedOutputRoot))
            {
                _afterExistingRootBranchForTest?.Invoke(normalizedOutputRoot);
                using var existingRootLease = new GuardedPackageOutputRoot(
                    normalizedOutputRoot,
                    snapshot.TrustedExportRoot,
                    execute: false,
                    requireExistingRoot: true);
                return Build(snapshot, normalizedOutputRoot, executeCopy: true);
            }

            string? parent = Path.GetDirectoryName(normalizedOutputRoot);
            string finalName = Path.GetFileName(normalizedOutputRoot);
            if (string.IsNullOrWhiteSpace(parent) || string.IsNullOrWhiteSpace(finalName))
                throw new InvalidOperationException("Material package output root is invalid.");

            string stagingContainer = Path.Combine(
                parent,
                $".onslaught-package-stage-{Guid.NewGuid():N}");
            string stagingRoot = Path.Combine(stagingContainer, finalName);
            try
            {
                AssetMaterialImportPackageMaterializationResult result =
                    Build(
                        snapshot,
                        stagingRoot,
                        executeCopy: true,
                        out WindowsFileIdentity stagedRootIdentity,
                        captureSeal: true,
                        out StagedPackageSeal? stagedSeal);
                if (!result.Completed)
                {
                    stagedSeal?.Dispose();
                    CleanupStagingContainer(stagingContainer);
                    return result;
                }
                using StagedPackageSeal seal = stagedSeal
                    ?? throw new IOException("Completed staged package did not produce publication seal evidence.");

                using (AssetMaterialImportPackageFileSafety finalPlacement = new(
                    snapshot,
                    normalizedOutputRoot,
                    execute: false))
                {
                    finalPlacement.ValidateGeneratedDestination(ManifestFileName);
                    finalPlacement.ValidateGeneratedDestination(AssetMaterialImportPackageWorkOrderService.WorkOrderFileName);
                    finalPlacement.ValidateGeneratedDestination(AssetMaterialImportPackageImporterDryRunService.DryRunFileName);
                }

                if (Directory.Exists(normalizedOutputRoot) || File.Exists(normalizedOutputRoot))
                    throw new IOException("Material package output root appeared while the staged package was being published.");

                _beforeFirstPublicationForTest?.Invoke(stagingRoot);
                FileMutationSafety.PublishDirectoryToVacantPath(
                    stagingRoot,
                    normalizedOutputRoot,
                    stagedRootIdentity,
                    snapshot.TrustedExportRoot,
                    seal.PrepareForRename,
                    _afterSealPreparedForTest,
                    seal.VerifyPublished);
                if (Directory.Exists(stagingContainer) &&
                    !Directory.EnumerateFileSystemEntries(stagingContainer).Any())
                {
                    Directory.Delete(stagingContainer);
                }
                return result;
            }
            catch
            {
                CleanupStagingContainer(stagingContainer);
                throw;
            }
        }

        private AssetMaterialImportPackageMaterializationResult Build(
            AssetCatalogSnapshot snapshot,
            string outputRoot,
            bool executeCopy)
        {
            return Build(
                snapshot,
                outputRoot,
                executeCopy,
                out _,
                captureSeal: false,
                out _);
        }

        private AssetMaterialImportPackageMaterializationResult Build(
            AssetCatalogSnapshot snapshot,
            string outputRoot,
            bool executeCopy,
            out WindowsFileIdentity outputRootIdentity,
            bool captureSeal,
            out StagedPackageSeal? stagedSeal)
        {
            stagedSeal = null;
            if (string.IsNullOrWhiteSpace(outputRoot))
            {
                throw new ArgumentException("Output root is required.", nameof(outputRoot));
            }

            using AssetMaterialImportPackageFileSafety fileSafety = new(snapshot, outputRoot, executeCopy);
            outputRootIdentity = fileSafety.OutputRootIdentity;
            string fullOutputRoot = fileSafety.PhysicalOutputRoot;
            fileSafety.ValidateGeneratedDestination(ManifestFileName);
            fileSafety.ValidateGeneratedDestination(AssetMaterialImportPackageWorkOrderService.WorkOrderFileName);
            fileSafety.ValidateGeneratedDestination(AssetMaterialImportPackageImporterDryRunService.DryRunFileName);

            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);
            AssetMaterialImportPackagePlan packagePlan = new AssetMaterialImportPackagePlanService().Build(manifest);
            ValidateUniquePackageDestinations(packagePlan);
            SourceIndex sourceIndex = SourceIndex.Build(snapshot);
            List<AssetMaterialImportPackageMaterializedFile> files = new();
            HashSet<string> packageDestinations = new(StringComparer.OrdinalIgnoreCase);

            foreach (AssetMaterialImportPackageModelOperation operation in packagePlan.ModelOperations)
            {
                if (!operation.ReadyForPackage)
                {
                    continue;
                }

                MaterializeModel(operation, sourceIndex, fileSafety, executeCopy, packageDestinations, files);
                MaterializeTextures(operation, sourceIndex, fileSafety, executeCopy, packageDestinations, files);
            }

            bool completed = files.Count(static file =>
                file.Status is "missing-source" or "blocked-unsafe-source" or "blocked-unsafe-destination" or "blocked-existing-different" or "blocked-incomplete-existing-package") == 0 &&
                packagePlan.BlockedPackageModelOperations == 0 &&
                packagePlan.UnresolvedTextureReferences == 0;
            fileSafety.ReleaseGeneratedDestinationValidation();
            (bool manifestWritten, string manifestStatus, long manifestBytes) = WriteManifestIfRequested(
                executeCopy,
                fileSafety,
                packagePlan,
                files,
                completed,
                _beforeManifestWriteForTest);
            (bool workOrderSidecarWritten, string workOrderSidecarStatus, long workOrderSidecarBytes) =
                WriteWorkOrderSidecarIfRequested(executeCopy, fileSafety, manifestWritten);
            (bool importerDryRunSidecarWritten, string importerDryRunSidecarStatus, long importerDryRunSidecarBytes) =
                WriteImporterDryRunSidecarIfRequested(executeCopy, fileSafety, workOrderSidecarWritten);
            bool finalCompleted = completed &&
                (!executeCopy ||
                    (manifestWritten && workOrderSidecarWritten && importerDryRunSidecarWritten));

            var result = new AssetMaterialImportPackageMaterializationResult(
                Executed: executeCopy,
                TotalPackageFiles: packagePlan.TotalPackageFiles,
                PlannedFiles: files.Count,
                WouldCopyFiles: files.Count(static file => file.Status == "would-copy"),
                CopiedFiles: files.Count(static file => file.Status == "copied"),
                ExistingFilesSkipped: files.Count(static file => file.Status == "skipped-existing"),
                ExistingFilesDetected: files.Count(static file => file.Status is "skipped-existing" or "would-skip-existing"),
                MissingSourceFiles: files.Count(static file => file.Status == "missing-source"),
                UnsafeSourceFiles: files.Count(static file => file.Status == "blocked-unsafe-source"),
                UnsafeDestinationFiles: files.Count(static file =>
                    file.Status is "blocked-unsafe-destination" or "blocked-existing-different" or "blocked-incomplete-existing-package"),
                ModelFilesReady: files.Count(static file => file.Role == "model" && file.Status is "would-copy" or "copied" or "would-skip-existing" or "skipped-existing"),
                TextureFilesReady: files.Count(static file => file.Role == "texture" && file.Status is "would-copy" or "copied" or "would-skip-existing" or "skipped-existing"),
                ModelFilesCopied: files.Count(static file => file.Role == "model" && file.Status == "copied"),
                TextureFilesCopied: files.Count(static file => file.Role == "texture" && file.Status == "copied"),
                BlockedPackageModelOperations: packagePlan.BlockedPackageModelOperations,
                UnresolvedTextureReferences: packagePlan.UnresolvedTextureReferences,
                ManifestRelativePath: ManifestFileName,
                ManifestWritten: manifestWritten,
                ManifestStatus: manifestStatus,
                ManifestBytes: manifestBytes,
                WorkOrderSidecarRelativePath: AssetMaterialImportPackageWorkOrderService.WorkOrderFileName,
                WorkOrderSidecarWritten: workOrderSidecarWritten,
                WorkOrderSidecarStatus: workOrderSidecarStatus,
                WorkOrderSidecarBytes: workOrderSidecarBytes,
                ImporterDryRunSidecarRelativePath: AssetMaterialImportPackageImporterDryRunService.DryRunFileName,
                ImporterDryRunSidecarWritten: importerDryRunSidecarWritten,
                ImporterDryRunSidecarStatus: importerDryRunSidecarStatus,
                ImporterDryRunSidecarBytes: importerDryRunSidecarBytes,
                Completed: finalCompleted,
                Files: files
                    .OrderBy(static file => file.DestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                    .ToList());
            if (captureSeal && finalCompleted)
                stagedSeal = fileSafety.CaptureSeal();
            return result;
        }

        private static (bool Written, string Status, long Bytes) WriteManifestIfRequested(
            bool executeCopy,
            AssetMaterialImportPackageFileSafety fileSafety,
            AssetMaterialImportPackagePlan packagePlan,
            IReadOnlyList<AssetMaterialImportPackageMaterializedFile> files,
            bool completed,
            Action<string>? beforeManifestWriteForTest)
        {
            if (!executeCopy)
            {
                return (false, "preflight-not-written", 0);
            }

            if (!completed)
                return (false, "payload-incomplete-not-written", 0);

            AssetMaterialImportPackageOutputManifest manifest = new(
                Schema: ManifestSchema,
                GeneratedAtUtc: DateTimeOffset.UtcNow,
                TotalPackageFiles: packagePlan.TotalPackageFiles,
                PlannedFiles: files.Count,
                ModelPackageFiles: packagePlan.ModelPackageFiles,
                TexturePackageFiles: packagePlan.TexturePackageFiles,
                BlockedPackageModelOperations: packagePlan.BlockedPackageModelOperations,
                UnresolvedTextureReferences: packagePlan.UnresolvedTextureReferences,
                Completed: completed,
                Models: packagePlan.ModelOperations
                    .OrderBy(static model => model.DestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static model => model.CatalogId, StringComparer.OrdinalIgnoreCase)
                    .ToList(),
                Files: files
                    .OrderBy(static file => file.DestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                    .ToList());
            JsonSerializerOptions options = new(JsonSerializerDefaults.Web)
            {
                WriteIndented = true
            };
            try
            {
                beforeManifestWriteForTest?.Invoke(fileSafety.PhysicalOutputRoot);
                byte[] bytes = JsonSerializer.SerializeToUtf8Bytes(manifest, options);
                long writtenBytes = fileSafety.WriteGenerated(ManifestFileName, bytes);
                return (true, "written", writtenBytes);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return (false, "blocked-unsafe-manifest", 0);
            }
        }

        private static (bool Written, string Status, long Bytes) WriteWorkOrderSidecarIfRequested(
            bool executeCopy,
            AssetMaterialImportPackageFileSafety fileSafety,
            bool manifestWritten)
        {
            if (!executeCopy)
            {
                return (false, "preflight-not-written", 0);
            }

            if (!manifestWritten)
            {
                return (false, "manifest-not-written", 0);
            }

            try
            {
                AssetMaterialImportPackageWorkOrderResult workOrder =
                    new AssetMaterialImportPackageWorkOrderService().Build(fileSafety.PhysicalOutputRoot);
                AssetMaterialImportPackageWorkOrderSidecar sidecar = new(
                    Schema: AssetMaterialImportPackageWorkOrderService.WorkOrderSchema,
                    GeneratedAtUtc: DateTimeOffset.UtcNow,
                    MaterialPackageWorkOrder: workOrder);
                byte[] bytes = JsonSerializer.SerializeToUtf8Bytes(
                    sidecar,
                    new JsonSerializerOptions(JsonSerializerDefaults.Web) { WriteIndented = true });
                long writtenBytes = fileSafety.WriteGenerated(
                    AssetMaterialImportPackageWorkOrderService.WorkOrderFileName,
                    bytes);
                return (true, "written", writtenBytes);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return (false, "blocked-unsafe-work-order-sidecar", 0);
            }
        }

        private static (bool Written, string Status, long Bytes) WriteImporterDryRunSidecarIfRequested(
            bool executeCopy,
            AssetMaterialImportPackageFileSafety fileSafety,
            bool workOrderSidecarWritten)
        {
            if (!executeCopy)
            {
                return (false, "preflight-not-written", 0);
            }

            if (!workOrderSidecarWritten)
            {
                return (false, "work-order-sidecar-not-written", 0);
            }

            try
            {
                AssetMaterialImportPackageImporterDryRunResult dryRun =
                    new AssetMaterialImportPackageImporterDryRunService().Build(fileSafety.PhysicalOutputRoot);
                if (!dryRun.Completed)
                    return (false, dryRun.SourceBatchStatus, 0);

                AssetMaterialImportPackageImporterDryRunSidecar sidecar = new(
                    Schema: AssetMaterialImportPackageImporterDryRunService.DryRunSchema,
                    GeneratedAtUtc: DateTimeOffset.UtcNow,
                    MaterialPackageImporterDryRun: dryRun);
                byte[] bytes = JsonSerializer.SerializeToUtf8Bytes(
                    sidecar,
                    new JsonSerializerOptions(JsonSerializerDefaults.Web) { WriteIndented = true });
                long writtenBytes = fileSafety.WriteGenerated(
                    AssetMaterialImportPackageImporterDryRunService.DryRunFileName,
                    bytes);
                return (true, "written", writtenBytes);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return (false, "blocked-unsafe-importer-dry-run-sidecar", 0);
            }
        }

        private static void MaterializeModel(
            AssetMaterialImportPackageModelOperation operation,
            SourceIndex sourceIndex,
            AssetMaterialImportPackageFileSafety fileSafety,
            bool executeCopy,
            HashSet<string> packageDestinations,
            List<AssetMaterialImportPackageMaterializedFile> files)
        {
            if (!packageDestinations.Add(operation.DestinationRelativePath))
            {
                return;
            }

            string sourcePath = sourceIndex.FindModelSource(operation);
            files.Add(PlanOrCopyPackageFile(
                role: "model",
                sourcePath,
                operation.DestinationRelativePath,
                operation.ExportFileName,
                operation.CatalogId,
                resolutionKind: "model-export",
                fileSafety,
                executeCopy));
        }

        private static void MaterializeTextures(
            AssetMaterialImportPackageModelOperation operation,
            SourceIndex sourceIndex,
            AssetMaterialImportPackageFileSafety fileSafety,
            bool executeCopy,
            HashSet<string> packageDestinations,
            List<AssetMaterialImportPackageMaterializedFile> files)
        {
            foreach (AssetMaterialImportPackageTextureReference texture in operation.TextureReferences)
            {
                if (!texture.SourceAvailable ||
                    string.IsNullOrWhiteSpace(texture.DestinationRelativePath) ||
                    !packageDestinations.Add(texture.DestinationRelativePath))
                {
                    continue;
                }

                string sourcePath = sourceIndex.FindTextureSource(operation, texture);
                files.Add(PlanOrCopyPackageFile(
                    role: "texture",
                    sourcePath,
                    texture.DestinationRelativePath,
                    texture.SourceFileName,
                    texture.SourceToken,
                    texture.ResolutionKind,
                    fileSafety,
                    executeCopy));
            }
        }

        private static AssetMaterialImportPackageMaterializedFile PlanOrCopyPackageFile(
            string role,
            string sourcePath,
            string destinationRelativePath,
            string sourceFileName,
            string sourceToken,
            string resolutionKind,
            AssetMaterialImportPackageFileSafety fileSafety,
            bool executeCopy)
        {
            string fullDestinationPath;
            try
            {
                fullDestinationPath = fileSafety.ResolveDestination(
                    destinationRelativePath,
                    createDirectories: executeCopy && !fileSafety.OutputRootExistedAtStart);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return BuildFile(
                    role,
                    destinationRelativePath,
                    sourceFileName,
                    sourceToken,
                    resolutionKind,
                    "blocked-unsafe-destination",
                    0);
            }

            if (string.IsNullOrWhiteSpace(sourcePath))
            {
                return BuildFile(
                    role,
                    destinationRelativePath,
                    sourceFileName,
                    sourceToken,
                    resolutionKind,
                    "missing-source",
                    0);
            }

            AssetCatalogSourceRead source;
            try
            {
                source = fileSafety.OpenSource(sourcePath, $"Material package {role} source");
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return BuildFile(
                    role,
                    destinationRelativePath,
                    sourceFileName,
                    sourceToken,
                    resolutionKind,
                    "blocked-unsafe-source",
                    0);
            }

            using (source)
            {
                if (!source.Exists)
                {
                    return BuildFile(
                        role,
                        destinationRelativePath,
                        sourceFileName,
                        sourceToken,
                        resolutionKind,
                        "missing-source",
                        0);
                }

                try
                {
                    ExistingPackageDestination? existingDestination =
                        fileSafety.HoldExistingDestination(fullDestinationPath, source);
                    if (existingDestination is ExistingPackageDestination existing)
                    {
                        return BuildFile(
                            role,
                            destinationRelativePath,
                            sourceFileName,
                            sourceToken,
                            resolutionKind,
                            existing.MatchesSource
                                ? executeCopy ? "skipped-existing" : "would-skip-existing"
                                : "blocked-existing-different",
                            existing.Length);
                    }

                    if (!executeCopy)
                    {
                        return BuildFile(
                            role,
                            destinationRelativePath,
                            sourceFileName,
                            sourceToken,
                            resolutionKind,
                            "would-copy",
                            0);
                    }

                    if (fileSafety.OutputRootExistedAtStart)
                    {
                        return BuildFile(
                            role,
                            destinationRelativePath,
                            sourceFileName,
                            sourceToken,
                            resolutionKind,
                            "blocked-incomplete-existing-package",
                            0);
                    }

                    long copiedBytes = fileSafety.CopySource(fullDestinationPath, source);
                    return BuildFile(
                        role,
                        destinationRelativePath,
                        sourceFileName,
                        sourceToken,
                        resolutionKind,
                        "copied",
                        copiedBytes);
                }
                catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
                {
                    return BuildFile(
                        role,
                        destinationRelativePath,
                        sourceFileName,
                        sourceToken,
                        resolutionKind,
                        "blocked-unsafe-destination",
                        0);
                }
            }
        }

        private static AssetMaterialImportPackageMaterializedFile BuildFile(
            string role,
            string destinationRelativePath,
            string sourceFileName,
            string sourceToken,
            string resolutionKind,
            string status,
            long outputBytes)
        {
            return new AssetMaterialImportPackageMaterializedFile(
                Role: role,
                DestinationRelativePath: NormalizeRelativePath(destinationRelativePath),
                SourceFileName: Path.GetFileName(sourceFileName),
                SourceToken: sourceToken,
                ResolutionKind: resolutionKind,
                Status: status,
                OutputBytes: outputBytes);
        }

        private static string NormalizeRelativePath(string value)
        {
            return value.Replace('\\', '/');
        }

        private static void ValidateUniquePackageDestinations(AssetMaterialImportPackagePlan packagePlan)
        {
            IReadOnlyList<string> destinations = packagePlan.PackageFiles
                .Select(static file => NormalizeRelativePath(file.DestinationRelativePath))
                .ToList();
            if (destinations.Any(string.IsNullOrWhiteSpace) ||
                destinations.Distinct(StringComparer.OrdinalIgnoreCase).Count() != destinations.Count)
            {
                throw new InvalidOperationException(
                    "Material package plan contains empty or colliding normalized destinations.");
            }
        }

        private static void CleanupStagingContainer(string stagingContainer)
        {
            FileMutationSafety.DirectoryLockSet? stagingLocks = null;
            try
            {
                if (!Directory.Exists(stagingContainer))
                    return;

                string normalizedStagingContainer = FileMutationSafety.NormalizeLocalPath(
                    stagingContainer,
                    "Material package staging container");
                stagingLocks = FileMutationSafety.LockDirectoryTree(
                    normalizedStagingContainer,
                    "Material package staging container");
                if (!string.Equals(
                        stagingLocks.PhysicalPath,
                        normalizedStagingContainer,
                        FileMutationSafety.PathComparison))
                {
                    throw new InvalidOperationException(
                        "Material package staging cleanup resolved outside its expected local path.");
                }

                DeleteGeneratedDirectoryContentsNoFollow(
                    stagingLocks.PhysicalPath,
                    stagingLocks.PhysicalPath);
                stagingLocks.Dispose();
                stagingLocks = null;
                Directory.Delete(normalizedStagingContainer, recursive: false);
            }
            catch
            {
                // Best effort cleanup. The authoritative output path is never published on failure.
            }
            finally
            {
                stagingLocks?.Dispose();
            }
        }

        private static void DeleteGeneratedDirectoryContentsNoFollow(
            string directory,
            string stagingRoot)
        {
            foreach (string entry in Directory.EnumerateFileSystemEntries(directory).ToList())
            {
                string normalizedEntry = FileMutationSafety.NormalizeLocalPath(
                    entry,
                    "Material package staging cleanup entry");
                if (!FileMutationSafety.IsSameOrUnderRoot(normalizedEntry, stagingRoot) ||
                    string.Equals(normalizedEntry, stagingRoot, FileMutationSafety.PathComparison))
                {
                    throw new InvalidOperationException(
                        "Material package staging cleanup entry escapes its staging root.");
                }

                FileAttributes attributes = File.GetAttributes(normalizedEntry);
                bool isDirectory = (attributes & FileAttributes.Directory) != 0;
                if ((attributes & FileAttributes.ReparsePoint) != 0)
                {
                    if (isDirectory)
                        Directory.Delete(normalizedEntry, recursive: false);
                    else
                        File.Delete(normalizedEntry);
                    continue;
                }

                if (!isDirectory)
                {
                    File.Delete(normalizedEntry);
                    continue;
                }

                FileMutationSafety.DirectoryLockSet? childLocks = null;
                try
                {
                    childLocks = FileMutationSafety.LockDirectoryTree(
                        normalizedEntry,
                        "Material package staging cleanup directory");
                    if (!string.Equals(
                            childLocks.PhysicalPath,
                            normalizedEntry,
                            FileMutationSafety.PathComparison) ||
                        !FileMutationSafety.IsSameOrUnderRoot(childLocks.PhysicalPath, stagingRoot))
                    {
                        throw new InvalidOperationException(
                            "Material package staging cleanup directory changed identity.");
                    }

                    DeleteGeneratedDirectoryContentsNoFollow(childLocks.PhysicalPath, stagingRoot);
                    childLocks.Dispose();
                    childLocks = null;
                    Directory.Delete(normalizedEntry, recursive: false);
                }
                finally
                {
                    childLocks?.Dispose();
                }
            }
        }

        private sealed class SourceIndex
        {
            private readonly IReadOnlyDictionary<string, AssetLooseMeshItem> _looseMeshesByCatalogId;
            private readonly IReadOnlyDictionary<string, AssetEmbeddedMeshItem> _embeddedMeshesByCatalogId;
            private readonly IReadOnlyDictionary<string, AssetTextureItem> _texturesByCatalogId;
            private readonly IReadOnlyDictionary<string, AssetTextureItem> _texturesByFileName;
            private readonly IReadOnlyDictionary<string, AssetTextureItem> _texturesBySanitizedCatalogId;
            private readonly IReadOnlyDictionary<string, AssetTextureItem> _texturesBySanitizedFileName;
            private readonly AssetModelTextureLinkService _textureLinkService = new();
            private readonly AssetCatalogSnapshot _snapshot;

            private SourceIndex(
                IReadOnlyDictionary<string, AssetLooseMeshItem> looseMeshesByCatalogId,
                IReadOnlyDictionary<string, AssetEmbeddedMeshItem> embeddedMeshesByCatalogId,
                IReadOnlyDictionary<string, AssetTextureItem> texturesByCatalogId,
                IReadOnlyDictionary<string, AssetTextureItem> texturesByFileName,
                IReadOnlyDictionary<string, AssetTextureItem> texturesBySanitizedCatalogId,
                IReadOnlyDictionary<string, AssetTextureItem> texturesBySanitizedFileName,
                AssetCatalogSnapshot snapshot)
            {
                _looseMeshesByCatalogId = looseMeshesByCatalogId;
                _embeddedMeshesByCatalogId = embeddedMeshesByCatalogId;
                _texturesByCatalogId = texturesByCatalogId;
                _texturesByFileName = texturesByFileName;
                _texturesBySanitizedCatalogId = texturesBySanitizedCatalogId;
                _texturesBySanitizedFileName = texturesBySanitizedFileName;
                _snapshot = snapshot;
            }

            public static SourceIndex Build(AssetCatalogSnapshot snapshot)
            {
                return new SourceIndex(
                    snapshot.LooseMeshes
                        .Where(static mesh => !string.IsNullOrWhiteSpace(mesh.CatalogId))
                        .GroupBy(static mesh => mesh.CatalogId, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase),
                    snapshot.EmbeddedMeshes
                        .Where(static mesh => !string.IsNullOrWhiteSpace(mesh.CatalogId))
                        .GroupBy(static mesh => mesh.CatalogId, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase),
                    snapshot.Textures
                        .Where(static texture => !string.IsNullOrWhiteSpace(texture.CatalogId))
                        .GroupBy(static texture => texture.CatalogId, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase),
                    snapshot.Textures
                        .Where(static texture => !string.IsNullOrWhiteSpace(texture.ExportFileName))
                        .GroupBy(static texture => texture.ExportFileName, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase),
                    snapshot.Textures
                        .Select(static texture => new { Key = SanitizeToken(texture.CatalogId), Texture = texture })
                        .Where(static row => !string.IsNullOrWhiteSpace(row.Key))
                        .GroupBy(static row => row.Key, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First().Texture, StringComparer.OrdinalIgnoreCase),
                    snapshot.Textures
                        .Select(static texture => new { Key = SanitizeToken(texture.ExportFileName), Texture = texture })
                        .Where(static row => !string.IsNullOrWhiteSpace(row.Key))
                        .GroupBy(static row => row.Key, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First().Texture, StringComparer.OrdinalIgnoreCase),
                    snapshot);
            }

            public string FindModelSource(AssetMaterialImportPackageModelOperation operation)
            {
                if (operation.Kind.Equals("loose mesh", StringComparison.OrdinalIgnoreCase) &&
                    _looseMeshesByCatalogId.TryGetValue(operation.CatalogId, out AssetLooseMeshItem? looseMesh))
                {
                    return looseMesh.ExportPath;
                }

                if (operation.Kind.Equals("embedded mesh", StringComparison.OrdinalIgnoreCase) &&
                    _embeddedMeshesByCatalogId.TryGetValue(operation.CatalogId, out AssetEmbeddedMeshItem? embeddedMesh))
                {
                    return embeddedMesh.ExportPath;
                }

                return string.Empty;
            }

            public string FindTextureSource(
                AssetMaterialImportPackageModelOperation operation,
                AssetMaterialImportPackageTextureReference texture)
            {
                if (texture.ResolutionKind.Equals("catalog", StringComparison.OrdinalIgnoreCase))
                {
                    if (_texturesByCatalogId.TryGetValue(texture.SourceToken, out AssetTextureItem? byCatalogId))
                    {
                        return byCatalogId.ExportPath;
                    }

                    if (_texturesBySanitizedCatalogId.TryGetValue(texture.SourceToken, out AssetTextureItem? bySanitizedCatalogId))
                    {
                        return bySanitizedCatalogId.ExportPath;
                    }

                    if (_texturesByFileName.TryGetValue(texture.SourceFileName, out AssetTextureItem? byFileName))
                    {
                        return byFileName.ExportPath;
                    }

                    if (_texturesBySanitizedFileName.TryGetValue(texture.SourceFileName, out AssetTextureItem? bySanitizedFileName))
                    {
                        return bySanitizedFileName.ExportPath;
                    }

                    return string.Empty;
                }

                if (!texture.ResolutionKind.Equals("sidecar", StringComparison.OrdinalIgnoreCase))
                {
                    return string.Empty;
                }

                string modelSource = FindModelSource(operation);
                IReadOnlyList<AssetModelSidecarTexture> sidecars =
                    _textureLinkService.ResolveSidecarTextures(_snapshot, modelSource, [texture.BindingFileName]);
                return sidecars.FirstOrDefault(sidecar =>
                        sidecar.FileName.Equals(texture.SourceFileName, StringComparison.OrdinalIgnoreCase) ||
                        SanitizeToken(sidecar.FileName).Equals(texture.SourceFileName, StringComparison.OrdinalIgnoreCase))
                    ?.ExportPath ?? string.Empty;
            }

            private static string SanitizeToken(string value)
            {
                if (string.IsNullOrWhiteSpace(value))
                {
                    return string.Empty;
                }

                char[] chars = value.Trim().Select(static ch =>
                    char.IsLetterOrDigit(ch) || ch is '.' or '-' or '_' ? ch : '_').ToArray();
                string result = new string(chars).Trim('_');
                while (result.Contains("__", StringComparison.Ordinal))
                {
                    result = result.Replace("__", "_", StringComparison.Ordinal);
                }

                return result;
            }
        }
    }

    public sealed record AssetMaterialImportPackageMaterializationResult(
        bool Executed,
        int TotalPackageFiles,
        int PlannedFiles,
        int WouldCopyFiles,
        int CopiedFiles,
        int ExistingFilesSkipped,
        int ExistingFilesDetected,
        int MissingSourceFiles,
        int UnsafeSourceFiles,
        int UnsafeDestinationFiles,
        int ModelFilesReady,
        int TextureFilesReady,
        int ModelFilesCopied,
        int TextureFilesCopied,
        int BlockedPackageModelOperations,
        int UnresolvedTextureReferences,
        string ManifestRelativePath,
        bool ManifestWritten,
        string ManifestStatus,
        long ManifestBytes,
        string WorkOrderSidecarRelativePath,
        bool WorkOrderSidecarWritten,
        string WorkOrderSidecarStatus,
        long WorkOrderSidecarBytes,
        string ImporterDryRunSidecarRelativePath,
        bool ImporterDryRunSidecarWritten,
        string ImporterDryRunSidecarStatus,
        long ImporterDryRunSidecarBytes,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageMaterializedFile> Files);

    public sealed record AssetMaterialImportPackageMaterializedFile(
        string Role,
        string DestinationRelativePath,
        string SourceFileName,
        string SourceToken,
        string ResolutionKind,
        string Status,
        long OutputBytes);

    public sealed record AssetMaterialImportPackageOutputManifest(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        int TotalPackageFiles,
        int PlannedFiles,
        int ModelPackageFiles,
        int TexturePackageFiles,
        int BlockedPackageModelOperations,
        int UnresolvedTextureReferences,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageModelOperation> Models,
        IReadOnlyList<AssetMaterialImportPackageMaterializedFile> Files);
}
