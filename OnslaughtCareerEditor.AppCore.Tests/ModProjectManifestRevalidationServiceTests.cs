using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Nodes;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class ModProjectManifestRevalidationServiceTests : IDisposable
    {
        private readonly string _tempRoot;

        public ModProjectManifestRevalidationServiceTests()
        {
            _tempRoot = Path.Combine(
                Path.GetTempPath(),
                "oce-mod-project-revalidation-tests",
                Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(_tempRoot);
        }

        public void Dispose()
        {
            try
            {
                Directory.Delete(_tempRoot, recursive: true);
            }
            catch (IOException)
            {
            }
        }

        [Fact]
        public void Review_ClassifiesUnchangedCatalogDriftedAndMissingRows()
        {
            RevalidationFixture fixture = CreateFixture();
            File.WriteAllText(fixture.CatalogPath, BuildCurrentCatalogJson());
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);

            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);

            Assert.True(review.CatalogProvenanceChanged);
            Assert.Equal(3, review.ReviewedCount);
            Assert.Equal(1, review.UnchangedCount);
            Assert.Equal(1, review.CatalogDriftedCount);
            Assert.Equal(1, review.MissingCount);
            Assert.Equal(0, review.AmbiguousOrDuplicateCount);
            Assert.Equal(0, review.LocalExportMissingCount);
            Assert.Equal(0, review.LocalHashMismatchCount);
            Assert.Equal(
                ModProjectRevalidationStatus.Unchanged,
                review.Entries.Single(row => row.CatalogId == "texture:textures/texture_one.tga").Status);
            ModProjectRevalidationEntry unchangedTexture = review.Entries.Single(
                row => row.CatalogId == "texture:textures/texture_one.tga");
            Assert.Equal(unchangedTexture.ManifestExpectedExportSha256, unchangedTexture.CurrentExpectedExportSha256);
            Assert.Equal(unchangedTexture.ManifestExpectedExportSha256, unchangedTexture.CurrentExportSha256);
            Assert.Equal(
                ModProjectRevalidationStatus.CatalogDrifted,
                review.Entries.Single(row => row.CatalogId == "mesh:ship_body.msh").Status);
            Assert.Equal(
                ModProjectRevalidationStatus.Missing,
                review.Entries.Single(row => row.CatalogId == "embedded_mesh:100_res_PC/body00").Status);
            Assert.Equal("mod-project-revalidation-receipt.v1", review.ReceiptVersion);
            Assert.Equal("mod-project-plan.v1", review.OriginalManifest.ManifestVersion);
            Assert.Equal("catalog.json", review.OriginalManifest.CatalogFileName);
            Assert.Equal(Path.GetFileName(fixture.ManifestPath), review.OriginalManifest.ManifestFileName);
            Assert.Equal(64, review.OriginalManifest.ManifestSha256.Length);
        }

        [Fact]
        public void Export_WritesDeterministicMetadataOnlyJsonAndOptionalTsvWithoutChangingInputs()
        {
            RevalidationFixture fixture = CreateFixture();
            File.WriteAllText(fixture.CatalogPath, BuildCurrentCatalogJson());
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);
            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            byte[] manifestBefore = File.ReadAllBytes(fixture.ManifestPath);
            byte[] catalogBefore = File.ReadAllBytes(fixture.CatalogPath);
            byte[] textureBefore = File.ReadAllBytes(Path.Combine(_tempRoot, "generated", "exports", "texture_one.png"));
            string outputDirectory = Path.Combine(_tempRoot, "review-receipts");
            Directory.CreateDirectory(outputDirectory);
            string firstPath = Path.Combine(outputDirectory, "drift-review.json");
            string secondPath = Path.Combine(outputDirectory, "drift-review-copy.json");

            ModProjectRevalidationExportResult first = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                firstPath,
                includeTsv: true);
            ModProjectRevalidationExportResult second = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                secondPath,
                includeTsv: true);

            Assert.True(first.Success, first.Message);
            Assert.True(second.Success, second.Message);
            Assert.Equal(firstPath, first.ReceiptPath);
            Assert.Equal(Path.ChangeExtension(firstPath, ".tsv"), first.TsvPath);
            Assert.Equal(File.ReadAllBytes(firstPath), File.ReadAllBytes(secondPath));
            Assert.Equal(
                File.ReadAllBytes(Path.ChangeExtension(firstPath, ".tsv")),
                File.ReadAllBytes(Path.ChangeExtension(secondPath, ".tsv")));
            using JsonDocument receipt = JsonDocument.Parse(File.ReadAllBytes(firstPath));
            Assert.Equal(
                "mod-project-revalidation-receipt.v1",
                receipt.RootElement.GetProperty("receiptVersion").GetString());
            Assert.Equal(1, receipt.RootElement.GetProperty("unchangedCount").GetInt32());
            Assert.Equal(1, receipt.RootElement.GetProperty("catalogDriftedCount").GetInt32());
            Assert.Equal(1, receipt.RootElement.GetProperty("missingCount").GetInt32());
            Assert.Equal("unchanged", receipt.RootElement.GetProperty("entries")[0].GetProperty("status").GetString());
            Assert.Contains(
                "catalog_id\tdisplay_name\tkind\tstatus",
                File.ReadAllText(Path.ChangeExtension(firstPath, ".tsv")),
                StringComparison.Ordinal);
            Assert.Equal(manifestBefore, File.ReadAllBytes(fixture.ManifestPath));
            Assert.Equal(catalogBefore, File.ReadAllBytes(fixture.CatalogPath));
            Assert.Equal(
                textureBefore,
                File.ReadAllBytes(Path.Combine(_tempRoot, "generated", "exports", "texture_one.png")));
            Assert.DoesNotContain(
                Directory.GetFiles(outputDirectory),
                path => Path.GetExtension(path) is ".png" or ".fbx");
        }

        [Fact]
        public void Export_RejectsStaleLocalFileHashAfterReviewWithoutWriting()
        {
            RevalidationFixture fixture = CreateFixture();
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);
            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            string texturePath = Path.Combine(_tempRoot, "generated", "exports", "texture_one.png");
            File.WriteAllBytes(texturePath, [0x89, 0x50, 0x4E, 0x47, 0x7F]);
            string outputPath = Path.Combine(_tempRoot, "stale-local-review.json");

            ModProjectRevalidationExportResult result = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                outputPath,
                includeTsv: true);

            Assert.False(result.Success);
            Assert.Contains("changed after this review", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(outputPath));
            Assert.False(File.Exists(Path.ChangeExtension(outputPath, ".tsv")));
        }

        [Fact]
        public void Export_RejectsDuplicateNormalizedManifestIdentityAfterShowingAmbiguousCount()
        {
            RevalidationFixture fixture = CreateFixture();
            JsonObject root = JsonNode.Parse(File.ReadAllText(fixture.ManifestPath))!.AsObject();
            JsonArray assets = root["assets"]!.AsArray();
            assets.Add(assets[0]!.DeepClone());
            root["selectedCount"] = assets.Count;
            File.WriteAllText(fixture.ManifestPath, root.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);

            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            string outputPath = Path.Combine(_tempRoot, "duplicate-identity-review.json");
            ModProjectRevalidationExportResult result = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                outputPath,
                includeTsv: false);

            Assert.Equal(2, review.AmbiguousOrDuplicateCount);
            Assert.False(result.Success);
            Assert.Contains("ambiguous", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(outputPath));
        }

        [Fact]
        public void Review_ClassifiesLocalExportMissingAndLocalHashMismatch()
        {
            RevalidationFixture fixture = CreateFixture();
            File.Delete(Path.Combine(_tempRoot, "generated", "exports", "body00_binary.fbx"));
            File.WriteAllBytes(
                Path.Combine(_tempRoot, "generated", "exports", "ship_body.msh_binary.fbx"),
                [0x46, 0x42, 0x58, 0x7F]);
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);

            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);

            Assert.False(review.CatalogProvenanceChanged);
            Assert.Equal(1, review.UnchangedCount);
            Assert.Equal(1, review.LocalExportMissingCount);
            Assert.Equal(1, review.LocalHashMismatchCount);
            Assert.Equal(
                ModProjectRevalidationStatus.LocalExportMissing,
                review.Entries.Single(row => row.CatalogId == "embedded_mesh:100_res_PC/body00").Status);
            Assert.Equal(
                ModProjectRevalidationStatus.LocalHashMismatch,
                review.Entries.Single(row => row.CatalogId == "mesh:ship_body.msh").Status);
        }

        [Fact]
        public void Review_ReportsAmbiguousCurrentCatalogIdentityWithoutChoosingARow()
        {
            RevalidationFixture fixture = CreateFixture();
            AssetCatalogSnapshot loaded = new AssetCatalogService().Load(fixture.CatalogDirectory);
            AssetCatalogSnapshot ambiguous = loaded with
            {
                Textures = loaded.Textures.Concat([loaded.Textures.Single()]).ToArray(),
            };

            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                ambiguous,
                fixture.ManifestPath);

            Assert.Equal(1, review.AmbiguousOrDuplicateCount);
            ModProjectRevalidationEntry entry = review.Entries.Single(
                row => row.CatalogId == "texture:textures/texture_one.tga");
            Assert.Equal(ModProjectRevalidationStatus.AmbiguousOrDuplicate, entry.Status);
            Assert.Null(entry.CurrentExportSha256);
        }

        [Fact]
        public void Review_RejectsUnsupportedManifestVersion()
        {
            RevalidationFixture fixture = CreateFixture();
            JsonObject root = JsonNode.Parse(File.ReadAllText(fixture.ManifestPath))!.AsObject();
            root["manifestVersion"] = "mod-project-plan.v99";
            File.WriteAllText(fixture.ManifestPath, root.ToJsonString());
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);

            NotSupportedException error = Assert.Throws<NotSupportedException>(() =>
                ModProjectManifestRevalidationService.Review(current, fixture.ManifestPath));

            Assert.Contains("not supported", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void Review_RejectsMalformedManifestHash()
        {
            RevalidationFixture fixture = CreateFixture();
            JsonObject root = JsonNode.Parse(File.ReadAllText(fixture.ManifestPath))!.AsObject();
            root["catalogSha256"] = "not-a-sha256";
            File.WriteAllText(fixture.ManifestPath, root.ToJsonString());
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                ModProjectManifestRevalidationService.Review(current, fixture.ManifestPath));

            Assert.Contains("64-character", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void Review_RejectsMissingManifestCatalogProvenance()
        {
            RevalidationFixture fixture = CreateFixture();
            JsonObject root = JsonNode.Parse(File.ReadAllText(fixture.ManifestPath))!.AsObject();
            root.Remove("catalogPathContract");
            File.WriteAllText(fixture.ManifestPath, root.ToJsonString());
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                ModProjectManifestRevalidationService.Review(current, fixture.ManifestPath));

            Assert.Contains("provenance", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void Export_RejectsCatalogChangedAfterReviewWithoutWriting()
        {
            RevalidationFixture fixture = CreateFixture();
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);
            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            File.AppendAllText(fixture.CatalogPath, " ");
            string outputPath = Path.Combine(_tempRoot, "changed-catalog-review.json");

            ModProjectRevalidationExportResult result = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                outputPath,
                includeTsv: false);

            Assert.False(result.Success);
            Assert.Contains("changed after this review", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(outputPath));
        }

        [Fact]
        public void Export_RejectsOutputInsideInstalledGameWithoutWriting()
        {
            RevalidationFixture fixture = CreateFixture();
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);
            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            string gameDirectory = Path.Combine(_tempRoot, "installed-game");
            Directory.CreateDirectory(Path.Combine(gameDirectory, "data"));
            File.WriteAllBytes(Path.Combine(gameDirectory, "BEA.exe"), [0x4D, 0x5A]);
            string outputPath = Path.Combine(gameDirectory, "manifest-review.json");

            ModProjectRevalidationExportResult result = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                outputPath,
                includeTsv: true);

            Assert.False(result.Success);
            Assert.Contains("game", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(outputPath));
            Assert.False(File.Exists(Path.ChangeExtension(outputPath, ".tsv")));
        }

        [Fact]
        public void Export_RefusesToReplaceOriginalManifest()
        {
            RevalidationFixture fixture = CreateFixture();
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);
            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            byte[] manifestBefore = File.ReadAllBytes(fixture.ManifestPath);

            ModProjectRevalidationExportResult result = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                fixture.ManifestPath,
                includeTsv: false);

            Assert.False(result.Success);
            Assert.Contains("cannot replace", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(manifestBefore, File.ReadAllBytes(fixture.ManifestPath));
        }

        [Fact]
        public void Review_CountsCatalogAndLocalDriftIndependentlyForTheSameRow()
        {
            RevalidationFixture fixture = CreateFixture();
            File.WriteAllText(fixture.CatalogPath, BuildCurrentCatalogJson());
            File.Delete(Path.Combine(_tempRoot, "generated", "exports", "ship_body.msh_binary.fbx"));
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);

            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);

            Assert.Equal(1, review.CatalogDriftedCount);
            Assert.Equal(1, review.LocalExportMissingCount);
            ModProjectRevalidationEntry mesh = review.Entries.Single(row => row.CatalogId == "mesh:ship_body.msh");
            Assert.True(mesh.CatalogDrifted);
            Assert.True(mesh.LocalExportMissing);
            Assert.Equal(ModProjectRevalidationStatus.LocalExportMissing, mesh.Status);
        }

        [Fact]
        public void Review_RejectsNullManifestAssetInsteadOfThrowingNullReference()
        {
            RevalidationFixture fixture = CreateFixture();
            JsonObject root = JsonNode.Parse(File.ReadAllText(fixture.ManifestPath))!.AsObject();
            JsonArray assets = root["assets"]!.AsArray();
            assets.Add(null);
            root["selectedCount"] = assets.Count;
            File.WriteAllText(fixture.ManifestPath, root.ToJsonString());
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                ModProjectManifestRevalidationService.Review(current, fixture.ManifestPath));

            Assert.Contains("row", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void Export_DoesNotOverwriteDestinationCreatedAtPublishBoundary()
        {
            RevalidationFixture fixture = CreateFixture();
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);
            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            string outputPath = Path.Combine(_tempRoot, "publish-race.json");
            byte[] competitor = [0x6B, 0x65, 0x65, 0x70];
            var hooks = new ModProjectRevalidationExportTestHooks(
                BeforeJsonPublish: path => File.WriteAllBytes(path, competitor));

            ModProjectRevalidationExportResult result = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                outputPath,
                includeTsv: false,
                hooks);

            Assert.False(result.Success);
            Assert.Equal(competitor, File.ReadAllBytes(outputPath));
        }

        [Fact]
        public void Export_HoldsPresentLocalExportsAgainstPublishBoundaryMutation()
        {
            RevalidationFixture fixture = CreateFixture();
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);
            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            string texturePath = Path.Combine(_tempRoot, "generated", "exports", "texture_one.png");
            byte[] textureBefore = File.ReadAllBytes(texturePath);
            string outputPath = Path.Combine(_tempRoot, "held-source-review.json");
            bool mutationBlocked = false;
            var hooks = new ModProjectRevalidationExportTestHooks(
                BeforeJsonPublish: _ =>
                {
                    try
                    {
                        File.WriteAllBytes(texturePath, [0x7F]);
                    }
                    catch (IOException)
                    {
                        mutationBlocked = true;
                    }
                });

            ModProjectRevalidationExportResult result = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                outputPath,
                includeTsv: false,
                hooks);

            Assert.True(result.Success, result.Message);
            Assert.True(mutationBlocked);
            Assert.Equal(textureBefore, File.ReadAllBytes(texturePath));
        }

        [Fact]
        public void Export_ReportsJsonSuccessWhenOptionalTsvLosesNoClobberRace()
        {
            RevalidationFixture fixture = CreateFixture();
            AssetCatalogSnapshot current = new AssetCatalogService().Load(fixture.CatalogDirectory);
            ModProjectRevalidationReview review = ModProjectManifestRevalidationService.Review(
                current,
                fixture.ManifestPath);
            string outputPath = Path.Combine(_tempRoot, "optional-tsv-race.json");
            string tsvPath = Path.ChangeExtension(outputPath, ".tsv");
            byte[] competitor = [0x6B, 0x65, 0x65, 0x70];
            var hooks = new ModProjectRevalidationExportTestHooks(
                BeforeTsvPublish: path => File.WriteAllBytes(path, competitor));

            ModProjectRevalidationExportResult result = ModProjectManifestRevalidationService.Export(
                current,
                fixture.ManifestPath,
                review,
                outputPath,
                includeTsv: true,
                hooks);

            Assert.True(result.Success, result.Message);
            Assert.True(File.Exists(outputPath));
            Assert.Null(result.TsvPath);
            Assert.Contains("optional TSV was not written", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(competitor, File.ReadAllBytes(tsvPath));
        }

        private RevalidationFixture CreateFixture()
        {
            string catalogDirectory = Path.Combine(_tempRoot, "generated", "asset_catalog");
            string exportsDirectory = Path.Combine(_tempRoot, "generated", "exports");
            string receiptDirectory = Path.Combine(_tempRoot, "receipts");
            Directory.CreateDirectory(catalogDirectory);
            Directory.CreateDirectory(exportsDirectory);
            Directory.CreateDirectory(receiptDirectory);
            File.WriteAllBytes(Path.Combine(exportsDirectory, "texture_one.png"), [0x89, 0x50, 0x4E, 0x47, 0x01]);
            File.WriteAllBytes(Path.Combine(exportsDirectory, "ship_body.msh_binary.fbx"), [0x46, 0x42, 0x58, 0x02]);
            File.WriteAllBytes(Path.Combine(exportsDirectory, "body00_binary.fbx"), [0x46, 0x42, 0x58, 0x03]);

            string catalogPath = Path.Combine(catalogDirectory, "catalog.json");
            File.WriteAllText(catalogPath, BuildOriginalCatalogJson());
            AssetCatalogSnapshot original = new AssetCatalogService().Load(catalogDirectory);
            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                original,
                [
                    new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga"),
                    new ModProjectSelectionEntry("mesh", "mesh:ship_body.msh"),
                    new ModProjectSelectionEntry("embedded-mesh", "embedded_mesh:100_res_PC/body00"),
                ]);
            string manifestPath = Path.Combine(receiptDirectory, "original-plan.json");
            ModProjectPlanExportResult export = ModProjectPlannerService.Export(
                original,
                plan,
                manifestPath,
                includeTsv: false);
            Assert.True(export.Success, export.Message);
            return new RevalidationFixture(catalogDirectory, catalogPath, manifestPath);
        }

        private static string BuildOriginalCatalogJson() => """
            {
              "schema_version": 2,
              "path_contract": "bundle-root-relative",
              "summary": { "texture_catalog_entries": 1, "loose_mesh_catalog_entries": 1, "embedded_mesh_catalog_entries": 1, "video_catalog_entries": 0, "language_catalog_entries": 0, "goodie_catalog_entries": 0, "total_catalog_entries": 3 },
              "textures": [
                {
                  "catalog_id": "texture:textures/texture_one.tga",
                  "kind": "texture",
                  "canonical_ref": "textures/texture_one.tga",
                  "source_roots": ["dxtntextures"],
                  "export_png_paths": ["exports/texture_one.png"],
                  "export_sha256": "871923f8e5535ef938edc1ea710d5cf9e18637ce5d39feccef23030823993e4e",
                  "source_aya_count": 1,
                  "export_png_count": 1,
                  "packed_text_ref_count": 0,
                  "gdie_ref_count": 0,
                  "total_packed_ref_count": 0,
                  "referenced_in_packed": true
                }
              ],
              "loose_meshes": [
                {
                  "catalog_id": "mesh:ship_body.msh",
                  "kind": "loose_mesh",
                  "canonical_ref": "ship_body.msh",
                  "export_fbx_paths": ["exports/ship_body.msh_binary.fbx"],
                  "source_aya_count": 1,
                  "export_fbx_count": 1,
                  "packed_reference_count": 0,
                  "gdie_ref_count": 0,
                  "total_packed_ref_count": 0,
                  "referenced_in_packed": true
                }
              ],
              "embedded_meshes": [
                {
                  "catalog_id": "embedded_mesh:100_res_PC/body00",
                  "kind": "embedded_mesh",
                  "source_archive": "100_res_PC",
                  "body_name": "body00",
                  "export_fbx_path": "exports/body00_binary.fbx"
                }
              ],
              "videos": [],
              "language_rows": [],
              "goodies": []
            }
            """;

        private static string BuildCurrentCatalogJson() => """
            {
              "schema_version": 2,
              "path_contract": "bundle-root-relative",
              "summary": { "texture_catalog_entries": 1, "loose_mesh_catalog_entries": 1, "embedded_mesh_catalog_entries": 0, "video_catalog_entries": 0, "language_catalog_entries": 0, "goodie_catalog_entries": 0, "total_catalog_entries": 2 },
              "textures": [
                {
                  "catalog_id": "texture:textures/texture_one.tga",
                  "kind": "texture",
                  "canonical_ref": "textures/texture_one.tga",
                  "source_roots": ["dxtntextures"],
                  "export_png_paths": ["exports/texture_one.png"],
                  "export_sha256": "871923f8e5535ef938edc1ea710d5cf9e18637ce5d39feccef23030823993e4e",
                  "source_aya_count": 1,
                  "export_png_count": 1,
                  "packed_text_ref_count": 0,
                  "gdie_ref_count": 0,
                  "total_packed_ref_count": 0,
                  "referenced_in_packed": true
                }
              ],
              "loose_meshes": [
                {
                  "catalog_id": "mesh:ship_body.msh",
                  "kind": "loose_mesh",
                  "canonical_ref": "ship_body_v2.msh",
                  "export_fbx_paths": ["exports/ship_body.msh_binary.fbx"],
                  "source_aya_count": 1,
                  "export_fbx_count": 1,
                  "packed_reference_count": 0,
                  "gdie_ref_count": 0,
                  "total_packed_ref_count": 0,
                  "referenced_in_packed": true
                }
              ],
              "embedded_meshes": [],
              "videos": [],
              "language_rows": [],
              "goodies": []
            }
            """;

        private sealed record RevalidationFixture(
            string CatalogDirectory,
            string CatalogPath,
            string ManifestPath);
    }
}
