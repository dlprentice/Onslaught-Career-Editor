using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Threading;
using System.Threading.Tasks;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class AssetCatalogServiceTests
    {
        [Fact]
        public void Load_ParsesGeneratedCatalogAndResolvesLocalExports()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create();

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            Assert.Equal(catalog.CatalogFilePath, snapshot.CatalogFilePath);
            Assert.Equal(catalog.RootPath, snapshot.TrustedExportRoot);
            Assert.Equal(3_820, snapshot.Summary.TotalCatalogEntries);
            Assert.Equal(828, snapshot.Summary.TextureCount);
            Assert.Equal(213, snapshot.Summary.LooseMeshCount);
            Assert.Equal(139, snapshot.Summary.EmbeddedMeshCount);
            Assert.Equal(3, snapshot.Summary.GoodieCount);

            AssetTextureItem texture = Assert.Single(snapshot.Textures);
            Assert.Equal("Texture One", texture.DisplayName);
            Assert.Equal("textures/texture_one.tga", texture.CanonicalRef);
            Assert.Equal("texture_one.png", texture.ExportFileName);
            Assert.True(texture.ExportExists);
            Assert.Equal(Path.Combine(catalog.RootPath, "exports", "texture_one.png"), texture.ExportPath);
            Assert.Equal("dxtntextures", texture.SourceGroup);
            Assert.Equal(7, texture.PackedReferenceCount);

            AssetLooseMeshItem mesh = Assert.Single(snapshot.LooseMeshes);
            Assert.Equal("ship_body.msh", mesh.DisplayName);
            Assert.Equal("ship_body.msh_binary.fbx", mesh.ExportFileName);
            Assert.True(mesh.ExportExists);
            Assert.Equal(4, mesh.PackedReferenceCount);
            Assert.False(mesh.ModelSummary.MetadataAvailable);
            Assert.Equal("FBX", mesh.ModelSummary.Format);

            Assert.Equal(3, snapshot.Goodies.Count);
            AssetGoodieItem modelGoodie = snapshot.Goodies[0];
            Assert.Equal(8, modelGoodie.Index);
            Assert.Equal("Model", modelGoodie.ContentKind);
            Assert.Equal("BE:A Unit-00 'Prototype'", modelGoodie.SourceTitle);
            Assert.Equal("ship_body.msh", modelGoodie.PrimaryMeshRef);
            Assert.True(modelGoodie.HasModel);
            Assert.True(modelGoodie.HasTexture);
            Assert.Equal("Complete level 100.", modelGoodie.UnlockRequirement);
            Assert.Equal("CCareer__UpdateGoodieStates 0x0041c470", modelGoodie.UnlockEvidenceLabel);
            Assert.True(modelGoodie.IsSourceGridVisible);
            Assert.Equal("FEPGoodies get_goodie_number 0x0045cb80", modelGoodie.WallVisibilityEvidenceLabel);
            Assert.Equal("Unit viewer", modelGoodie.WallGroupLabel);
            Assert.Equal("row 2, slot 1", modelGoodie.WallPositionLabel);

            AssetGoodieItem hiddenGoodie = snapshot.Goodies[1];
            Assert.Equal(71, hiddenGoodie.Index);
            Assert.Equal("Artwork", hiddenGoodie.ContentKind);
            Assert.False(hiddenGoodie.IsSourceGridVisible);
            Assert.Contains("does not expose this slot", hiddenGoodie.WallVisibilitySummary);
            Assert.Equal("Not on known wall", hiddenGoodie.WallGroupLabel);
            Assert.Equal("No wall position", hiddenGoodie.WallPositionLabel);

            AssetGoodieItem videoGoodie = snapshot.Goodies[2];
            Assert.Equal(232, videoGoodie.Index);
            Assert.Equal("Video", videoGoodie.ContentKind);
            Assert.Equal("33", videoGoodie.VideoSequenceId);
            Assert.True(videoGoodie.HasVideo);
            Assert.Equal("Watch cutscene 33 during normal play.", videoGoodie.UnlockRequirement);
            Assert.Equal("CGame cutscene handlers", videoGoodie.UnlockEvidenceLabel);
            Assert.True(videoGoodie.IsSourceGridVisible);
            Assert.Contains("FMV slot 33", videoGoodie.WallVisibilitySummary);
            Assert.Equal("Cutscenes", videoGoodie.WallGroupLabel);
            Assert.Equal("row 3, slot 32", videoGoodie.WallPositionLabel);
        }

        [Fact]
        public void CatalogProducerAndAppCoreConsumer_RoundTripCurrentRelativePathContract()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string bundleRoot = CreateTemporaryDirectory("oce-asset-catalog-producer-consumer");
            try
            {
                string repoRoot = FindRepoRoot();
                string producerPath = Path.Combine(repoRoot, "tools", "export_asset_catalog.py");
                ProcessStartInfo startInfo = new("py")
                {
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = repoRoot,
                };
                startInfo.ArgumentList.Add("-3");
                startInfo.ArgumentList.Add(producerPath);
                startInfo.ArgumentList.Add("--emit-consumer-contract-fixture");
                startInfo.ArgumentList.Add(bundleRoot);
                using Process process = Process.Start(startInfo)!;
                string standardOutput = process.StandardOutput.ReadToEnd();
                string standardError = process.StandardError.ReadToEnd();
                process.WaitForExit();
                Assert.True(
                    process.ExitCode == 0,
                    $"Catalog producer failed ({process.ExitCode}).\n{standardOutput}\n{standardError}");

                string catalogPath = Path.Combine(bundleRoot, "asset_catalog", "catalog.json");
                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(catalogPath, snapshot.CatalogFilePath);
                Assert.Equal(bundleRoot, snapshot.TrustedExportRoot);
                AssetTextureItem texture = Assert.Single(snapshot.Textures);
                Assert.Equal("texture:producer-contract", texture.CatalogId);
                Assert.Equal(
                    Path.Combine(bundleRoot, "exports", "producer_texture.png"),
                    texture.ExportPath);
                Assert.True(texture.ExportExists);
                AssetTextureReadabilityRow readability = Assert.Single(
                    new AssetCatalogReadabilityService().Build(snapshot, sampleLimit: 1).TextureSamples);
                Assert.True(readability.ReadablePng);
                Assert.Equal(1, readability.Width);
                Assert.Equal(1, readability.Height);
            }
            finally
            {
                DeleteTestDirectory(bundleRoot);
            }
        }

        [Theory]
        [InlineData(66, "Earn C or better on 26 campaign missions.", "CCareer__UpdateGoodieStates 0x0041c470")]
        [InlineData(78, "Earn C or better on level 100.", "CCareer__UpdateGoodieStates 0x0041c470")]
        [InlineData(121, "Earn B or better on level 100.", "CCareer__UpdateGoodieStates 0x0041c470")]
        [InlineData(164, "Earn A or better on level 100.", "CCareer__UpdateGoodieStates 0x0041c470")]
        [InlineData(201, "Watch cutscene 1 during normal play.", "CGame cutscene handlers")]
        [InlineData(232, "Watch cutscene 33 during normal play.", "CGame cutscene handlers")]
        public void GoodieUnlockRequirementService_MapsSourceBackedRules(
            int index,
            string expectedSummary,
            string expectedEvidence)
        {
            GoodieUnlockRequirement requirement = GoodieUnlockRequirementService.Describe(index);

            Assert.Equal(expectedSummary, requirement.Summary);
            Assert.Equal(expectedEvidence, requirement.EvidenceLabel);
        }

        [Theory]
        [InlineData(70, true, "known in-game Goodies wall")]
        [InlineData(71, false, "does not expose this slot")]
        [InlineData(73, false, "does not expose this slot")]
        [InlineData(74, true, "developer item")]
        [InlineData(78, true, "concept art")]
        [InlineData(232, true, "FMV slot 33")]
        [InlineData(233, false, "Reserved save slot")]
        public void GoodieWallVisibilityService_MapsSourceGridQuirks(
            int index,
            bool expectedVisible,
            string expectedSummaryFragment)
        {
            GoodieWallVisibility visibility = GoodieWallVisibilityService.Describe(index);

            Assert.Equal(expectedVisible, visibility.IsSourceGridVisible);
            Assert.Contains(expectedSummaryFragment, visibility.Summary);
            Assert.NotEmpty(visibility.EvidenceLabel);
        }

        [Theory]
        [InlineData(0, 0, 0)]
        [InlineData(7, 0, 7)]
        [InlineData(8, 0, 66)]
        [InlineData(12, 0, 70)]
        [InlineData(13, 0, 74)]
        [InlineData(16, 0, 77)]
        [InlineData(0, 1, 8)]
        [InlineData(57, 1, 65)]
        [InlineData(0, 2, 201)]
        [InlineData(31, 2, 232)]
        [InlineData(0, 3, 78)]
        [InlineData(122, 3, 200)]
        public void GoodieWallGridMappingService_ResolvesCompiledVisibleWallCoordinates(
            int x,
            int y,
            int expectedIndex)
        {
            Assert.Equal(expectedIndex, GoodieWallGridMappingService.Resolve(x, y));
        }

        [Fact]
        public void GoodieWallGridMappingService_RaceRowSkipsHiddenGoodiesToDeveloperItems()
        {
            int[] topRowSequence = Enumerable.Range(8, 6)
                .Select(x => GoodieWallGridMappingService.Resolve(x, 0))
                .ToArray();

            Assert.Equal(new[] { 66, 67, 68, 69, 70, 74 }, topRowSequence);
            Assert.DoesNotContain(71, topRowSequence);
            Assert.DoesNotContain(72, topRowSequence);
            Assert.DoesNotContain(73, topRowSequence);
        }

        [Theory]
        [InlineData(17, 0)]
        [InlineData(58, 1)]
        [InlineData(32, 2)]
        [InlineData(123, 3)]
        [InlineData(0, 4)]
        public void GoodieWallGridMappingService_ReturnsMinusOneForUnmappedCoordinates(
            int x,
            int y)
        {
            Assert.Equal(-1, GoodieWallGridMappingService.Resolve(x, y));
        }

        [Theory]
        [InlineData(71)]
        [InlineData(72)]
        [InlineData(73)]
        public void GoodieWallGridMappingService_KeepsShippedHiddenArchivesOutOfVisibleIndexSet(int index)
        {
            Assert.False(GoodieWallGridMappingService.IsSourceGridVisible(index));
        }

        [Theory]
        [InlineData(0, "Character bios", "row 1, slot 1")]
        [InlineData(8, "Unit viewer", "row 2, slot 1")]
        [InlineData(66, "Race levels", "row 1, slot 9")]
        [InlineData(74, "Developer items", "row 1, slot 14")]
        [InlineData(78, "Concept art", "row 4, slot 1")]
        [InlineData(201, "Cutscenes", "row 3, slot 1")]
        [InlineData(232, "Cutscenes", "row 3, slot 32")]
        public void GoodieWallGridMappingService_LocatesVisibleWallSlots(
            int index,
            string expectedGroup,
            string expectedPosition)
        {
            GoodieWallSlot? slot = GoodieWallGridMappingService.Locate(index);

            Assert.NotNull(slot);
            Assert.Equal(index, slot.Index);
            Assert.Equal(expectedGroup, slot.GroupLabel);
            Assert.Equal(expectedPosition, slot.PositionLabel);
        }

        [Fact]
        public void GoodieWallGridMappingService_LocatesEveryVisibleIndexWithCompiledRoundTrip()
        {
            for (int index = 0; index <= 232; index++)
            {
                bool expectedVisible = index is >= 0 and <= 70 or >= 74 and <= 232;
                GoodieWallSlot? slot = GoodieWallGridMappingService.Locate(index);

                if (!expectedVisible)
                {
                    Assert.Null(slot);
                    continue;
                }

                Assert.NotNull(slot);
                Assert.Equal(index, slot.Index);
                Assert.Equal(index, GoodieWallGridMappingService.Resolve(slot.X, slot.Y));
                Assert.False(string.IsNullOrWhiteSpace(slot.GroupLabel));
                Assert.False(string.IsNullOrWhiteSpace(slot.PositionLabel));
            }
        }

        [Fact]
        public void GoodieWallGridMappingService_CompiledVisibleCoordinatesAreUnique()
        {
            HashSet<int> resolved = new();

            for (int y = 0; y <= 3; y++)
            {
                for (int x = 0; x <= 122; x++)
                {
                    int index = GoodieWallGridMappingService.Resolve(x, y);
                    if (index == -1)
                    {
                        continue;
                    }

                    Assert.InRange(index, 0, 232);
                    Assert.True(
                        resolved.Add(index),
                        $"Duplicate Goodies wall mapping for index {index} at x={x}, y={y}.");
                }
            }

            Assert.Equal(230, resolved.Count);
            Assert.DoesNotContain(71, resolved);
            Assert.DoesNotContain(72, resolved);
            Assert.DoesNotContain(73, resolved);
            Assert.Contains(232, resolved);
        }

        [Theory]
        [InlineData(71)]
        [InlineData(73)]
        [InlineData(233)]
        public void GoodieWallGridMappingService_ReturnsNullForHiddenOrReservedSlots(int index)
        {
            Assert.Null(GoodieWallGridMappingService.Locate(index));
        }

        [Fact]
        public void Load_AcceptsCatalogDirectoryOrCatalogFile()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create();

            AssetCatalogSnapshot byFile = new AssetCatalogService().Load(catalog.CatalogFilePath);
            AssetCatalogSnapshot byDirectory = new AssetCatalogService().Load(Path.GetDirectoryName(catalog.CatalogFilePath)!);

            Assert.Equal(byFile.CatalogFilePath, byDirectory.CatalogFilePath);
            Assert.Equal(byFile.Summary.TotalCatalogEntries, byDirectory.Summary.TotalCatalogEntries);
        }

        [Fact]
        public void Load_DoesNotSearchParentDirectoriesForRelativeExports()
        {
            string parent = CreateTemporaryDirectory("oce-asset-catalog-parent-search");
            string root = Path.Combine(parent, "bundle");
            string parentExport = Path.Combine(parent, "exports", "outside.png");
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(parentExport)!);
                File.WriteAllBytes(parentExport, BuildMinimalPng());
                string catalogPath = WriteSingleTextureCatalog(root, "exports/outside.png");

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                AssetTextureItem texture = Assert.Single(snapshot.Textures);
                Assert.Equal(root, snapshot.TrustedExportRoot);
                Assert.False(texture.ExportExists);
                Assert.Equal(Path.Combine(root, "exports", "outside.png"), texture.ExportPath);
            }
            finally
            {
                DeleteTestDirectory(parent);
            }
        }

        [Theory]
        [InlineData("../outside.png")]
        [InlineData("exports/../../outside.png")]
        public void Load_RejectsRelativeExportEscapes(string exportPath)
        {
            string root = CreateTemporaryDirectory("oce-asset-catalog-relative-escape");
            try
            {
                string catalogPath = WriteSingleTextureCatalog(root, exportPath);

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(AssetCatalogSnapshot.Empty, snapshot);
            }
            finally
            {
                DeleteTestDirectory(root);
            }
        }

        [Fact]
        public void Load_RejectsAbsoluteExportOutsideTrustedRoot()
        {
            string parent = CreateTemporaryDirectory("oce-asset-catalog-absolute-escape");
            string root = Path.Combine(parent, "bundle");
            string outsidePath = Path.Combine(parent, "outside.png");
            try
            {
                File.WriteAllBytes(outsidePath, BuildMinimalPng());
                string catalogPath = WriteSingleTextureCatalog(root, outsidePath);

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(AssetCatalogSnapshot.Empty, snapshot);
            }
            finally
            {
                DeleteTestDirectory(parent);
            }
        }

        [Fact]
        public void Load_RejectsAbsoluteExportEvenWhenItIsInsideTrustedRoot()
        {
            string root = CreateTemporaryDirectory("oce-asset-catalog-absolute-inside");
            try
            {
                string exportPath = Path.Combine(root, "exports", "inside.png");
                Directory.CreateDirectory(Path.GetDirectoryName(exportPath)!);
                File.WriteAllBytes(exportPath, BuildMinimalPng());
                string catalogPath = WriteSingleTextureCatalog(root, exportPath);

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(AssetCatalogSnapshot.Empty, snapshot);
            }
            finally
            {
                DeleteTestDirectory(root);
            }
        }

        [Fact]
        public void Load_RejectsUnsafeAlternativeExportPath()
        {
            string parent = CreateTemporaryDirectory("oce-asset-catalog-alternative-escape");
            string root = Path.Combine(parent, "bundle");
            try
            {
                string validPath = Path.Combine(root, "exports", "valid.png");
                Directory.CreateDirectory(Path.GetDirectoryName(validPath)!);
                File.WriteAllBytes(validPath, BuildMinimalPng());
                string catalogPath = WriteSingleTextureCatalog(
                    root,
                    "exports/valid.png",
                    "../outside.png");

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(AssetCatalogSnapshot.Empty, snapshot);
            }
            finally
            {
                DeleteTestDirectory(parent);
            }
        }

        [Fact]
        public void Load_RejectsHardlinkedExportSource()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string parent = CreateTemporaryDirectory("oce-asset-catalog-hardlink");
            string root = Path.Combine(parent, "bundle");
            string outsidePath = Path.Combine(parent, "outside.png");
            try
            {
                string catalogPath = WriteSingleTextureCatalog(root, "exports/linked.png");
                string linkedPath = Path.Combine(root, "exports", "linked.png");
                Directory.CreateDirectory(Path.GetDirectoryName(linkedPath)!);
                File.WriteAllBytes(outsidePath, BuildMinimalPng());
                Assert.True(CreateHardLink(linkedPath, outsidePath, IntPtr.Zero));

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(AssetCatalogSnapshot.Empty, snapshot);
            }
            finally
            {
                DeleteTestDirectory(parent);
            }
        }

        [Fact]
        public void Load_RejectsSymlinkedExportSource()
        {
            string parent = CreateTemporaryDirectory("oce-asset-catalog-symlink");
            string root = Path.Combine(parent, "bundle");
            string outsidePath = Path.Combine(parent, "outside.png");
            try
            {
                string catalogPath = WriteSingleTextureCatalog(root, "exports/linked.png");
                string linkedPath = Path.Combine(root, "exports", "linked.png");
                Directory.CreateDirectory(Path.GetDirectoryName(linkedPath)!);
                File.WriteAllBytes(outsidePath, BuildMinimalPng());
                try
                {
                    File.CreateSymbolicLink(linkedPath, outsidePath);
                }
                catch (Exception ex) when (ex is UnauthorizedAccessException or PlatformNotSupportedException)
                {
                    return;
                }

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(AssetCatalogSnapshot.Empty, snapshot);
            }
            finally
            {
                DeleteTestDirectory(parent);
            }
        }

        [Fact]
        public void Load_RejectsDanglingDirectorySymlinkAncestor()
        {
            string parent = CreateTemporaryDirectory("oce-asset-catalog-dangling-directory-link");
            string root = Path.Combine(parent, "bundle");
            try
            {
                string catalogPath = WriteSingleTextureCatalog(root, "exports/linked/missing.png");
                string linkedDirectory = Path.Combine(root, "exports", "linked");
                Directory.CreateDirectory(Path.GetDirectoryName(linkedDirectory)!);
                try
                {
                    Directory.CreateSymbolicLink(linkedDirectory, Path.Combine(parent, "missing-outside"));
                }
                catch (Exception ex) when (ex is UnauthorizedAccessException or PlatformNotSupportedException)
                {
                    return;
                }

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(AssetCatalogSnapshot.Empty, snapshot);
            }
            finally
            {
                DeleteTestDirectory(parent);
            }
        }

        [Fact]
        public void ResolveCatalogFilePath_RejectsHardlinkedCatalog()
        {
            if (!OperatingSystem.IsWindows())
                return;

            string parent = CreateTemporaryDirectory("oce-asset-catalog-hardlinked-catalog");
            string root = Path.Combine(parent, "bundle");
            string outsideCatalog = Path.Combine(parent, "outside-catalog.json");
            try
            {
                string catalogPath = WriteSingleTextureCatalog(root, "exports/missing.png");
                string catalogJson = File.ReadAllText(catalogPath);
                File.Delete(catalogPath);
                File.WriteAllText(outsideCatalog, catalogJson);
                Assert.True(CreateHardLink(catalogPath, outsideCatalog, IntPtr.Zero));

                Assert.Null(AssetCatalogService.ResolveCatalogFilePath(catalogPath));
                Assert.Equal(AssetCatalogSnapshot.Empty, new AssetCatalogService().Load(catalogPath));
            }
            finally
            {
                DeleteTestDirectory(parent);
            }
        }

        [Fact]
        public void ResolveCatalogFilePath_RejectsSymlinkedCatalog()
        {
            string parent = CreateTemporaryDirectory("oce-asset-catalog-symlinked-catalog");
            string root = Path.Combine(parent, "bundle");
            string outsideCatalog = Path.Combine(parent, "outside-catalog.json");
            try
            {
                string catalogPath = WriteSingleTextureCatalog(root, "exports/missing.png");
                string catalogJson = File.ReadAllText(catalogPath);
                File.Delete(catalogPath);
                File.WriteAllText(outsideCatalog, catalogJson);
                try
                {
                    File.CreateSymbolicLink(catalogPath, outsideCatalog);
                }
                catch (Exception ex) when (ex is UnauthorizedAccessException or PlatformNotSupportedException)
                {
                    return;
                }

                Assert.Null(AssetCatalogService.ResolveCatalogFilePath(catalogPath));
                Assert.Equal(AssetCatalogSnapshot.Empty, new AssetCatalogService().Load(catalogPath));
            }
            finally
            {
                DeleteTestDirectory(parent);
            }
        }

        [Fact]
        public void Load_RejectsCatalogInsideGameTree()
        {
            string root = CreateTemporaryDirectory("oce-asset-catalog-game-tree");
            try
            {
                Directory.CreateDirectory(Path.Combine(root, "data"));
                File.WriteAllText(Path.Combine(root, "BEA.exe"), "placeholder executable marker");
                string catalogPath = WriteSingleTextureCatalog(root, "exports/missing.png");

                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);

                Assert.Equal(AssetCatalogSnapshot.Empty, snapshot);
                Assert.Null(AssetCatalogService.ResolveCatalogFilePath(catalogPath));
            }
            finally
            {

                DeleteTestDirectory(root);
            }
        }

        [Theory]
        [InlineData(@"\\server\share\asset_catalog\catalog.json")]
        [InlineData(@"\\?\C:\asset_catalog\catalog.json")]
        [InlineData(@"C:asset_catalog\catalog.json")]
        [InlineData(@"C:\asset_catalog\catalog.json:alternate")]
        public void ResolveCatalogFilePath_RejectsNonLocalOrAmbiguousWindowsPaths(string path)
        {
            if (!OperatingSystem.IsWindows())
                return;

            Assert.Null(AssetCatalogService.ResolveCatalogFilePath(path));
        }

        [Fact]
        public void Load_RejectsCatalogWithoutCurrentBundlePathContract()
        {
            string root = CreateTemporaryDirectory("oce-asset-catalog-legacy-contract");
            try
            {
                string catalogPath = WriteSingleTextureCatalog(root, "exports/missing.png");
                JsonObject catalog = JsonNode.Parse(File.ReadAllText(catalogPath))!.AsObject();
                catalog.Remove("path_contract");
                File.WriteAllText(catalogPath, catalog.ToJsonString());

                Assert.Equal(AssetCatalogSnapshot.Empty, new AssetCatalogService().Load(catalogPath));
            }
            finally
            {
                DeleteTestDirectory(root);
            }
        }

        [Theory]
        [InlineData("null")]
        [InlineData("{}")]
        [InlineData("[null]")]
        public void Load_RejectsMalformedRequiredCatalogSection(string malformedSectionJson)
        {
            string root = CreateTemporaryDirectory("oce-asset-catalog-malformed-section");
            try
            {
                string catalogPath = WriteSingleTextureCatalog(root, "exports/missing.png");
                JsonObject catalog = JsonNode.Parse(File.ReadAllText(catalogPath))!.AsObject();
                catalog["textures"] = JsonNode.Parse(malformedSectionJson);
                File.WriteAllText(catalogPath, catalog.ToJsonString());

                Assert.Equal(AssetCatalogSnapshot.Empty, new AssetCatalogService().Load(catalogPath));
                Assert.Null(AssetCatalogService.ResolveCatalogFilePath(catalogPath));
            }
            finally
            {
                DeleteTestDirectory(root);
            }
        }

        [Fact]
        public void ResolveCatalogFilePath_RejectsDirectAndDualCatalogLayouts()
        {
            string root = CreateTemporaryDirectory("oce-asset-catalog-layout-contract");
            try
            {
                string nestedCatalog = WriteSingleTextureCatalog(root, "exports/missing.png");
                string directCatalog = Path.Combine(root, "catalog.json");
                File.Copy(nestedCatalog, directCatalog);

                Assert.Null(AssetCatalogService.ResolveCatalogFilePath(root));
                Assert.Null(AssetCatalogService.ResolveCatalogFilePath(nestedCatalog));
                Assert.Equal(AssetCatalogSnapshot.Empty, new AssetCatalogService().Load(root));

                File.Delete(directCatalog);
                File.Move(nestedCatalog, directCatalog);
                Directory.Delete(Path.GetDirectoryName(nestedCatalog)!);

                Assert.Null(AssetCatalogService.ResolveCatalogFilePath(root));
                Assert.Null(AssetCatalogService.ResolveCatalogFilePath(directCatalog));
                Assert.Equal(AssetCatalogSnapshot.Empty, new AssetCatalogService().Load(directCatalog));
            }
            finally
            {
                DeleteTestDirectory(root);
            }
        }

        [Fact]
        public void Readability_RejectsPostLoadHardlinkSourceSwap()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempAssetCatalog catalog = TempAssetCatalog.Create();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string originalPath = Assert.Single(snapshot.Textures).ExportPath;
            string outsideRoot = CreateTemporaryDirectory("oce-asset-catalog-post-load-swap");
            try
            {
                Directory.CreateDirectory(Path.Combine(outsideRoot, "data"));
                File.WriteAllText(Path.Combine(outsideRoot, "BEA.exe"), "placeholder executable marker");
                string outsidePath = Path.Combine(outsideRoot, "outside.png");
                byte[] outsidePng = BuildMinimalPng();
                outsidePng[19] = 7;
                outsidePng[23] = 9;
                File.WriteAllBytes(outsidePath, outsidePng);
                File.Delete(originalPath);
                Assert.True(CreateHardLink(originalPath, outsidePath, IntPtr.Zero));

                AssetCatalogReadability readability = new AssetCatalogReadabilityService().Build(snapshot, sampleLimit: 10);

                AssetTextureReadabilityRow row = Assert.Single(readability.TextureSamples);
                Assert.False(row.ExportExists);
                Assert.False(row.ReadablePng);
                Assert.Null(row.Width);
                Assert.Null(row.Height);
                Assert.Contains("validation", row.Status, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                DeleteTestDirectory(outsideRoot);
            }
        }

        [Fact]
        public void SourceLease_RejectsPostLoadNormalSourceReplacement()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string sourcePath = Assert.Single(snapshot.Textures).ExportPath;
            byte[] replacement = BuildMinimalPng();
            replacement[23] = 9;
            File.Delete(sourcePath);
            File.WriteAllBytes(sourcePath, replacement);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
            {
                using AssetCatalogSourceLease _ = AssetCatalogSourceAccessService.Open(snapshot, sourcePath);
            });

            Assert.Contains("changed identity", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void SourceLease_HoldsIntermediateSourceDirectoryAgainstRetarget()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempAssetCatalog catalog = TempAssetCatalog.Create();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string sourcePath = Assert.Single(snapshot.Textures).ExportPath;
            string sourceDirectory = Path.GetDirectoryName(sourcePath)!;
            string movedDirectory = $"{sourceDirectory}-moved";

            using AssetCatalogSourceLease lease = AssetCatalogSourceAccessService.Open(snapshot, sourcePath);
            Assert.True(lease.Stream.CanRead);
            Exception? retargetError = Record.Exception(() => Directory.Move(sourceDirectory, movedDirectory));

            Assert.NotNull(retargetError);
            Assert.True(
                retargetError is IOException or UnauthorizedAccessException,
                $"Unexpected retarget failure: {retargetError}");
            Assert.True(File.Exists(sourcePath));
            Assert.False(Directory.Exists(movedDirectory));
        }

        [Fact]
        public void SourceLease_RejectsPostLoadInPlaceSourceContentChange()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string sourcePath = Assert.Single(snapshot.Textures).ExportPath;
            byte[] changed = BuildMinimalPng();
            changed[23] = 9;
            File.WriteAllBytes(sourcePath, changed);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
            {
                using AssetCatalogSourceLease _ = AssetCatalogSourceAccessService.Open(snapshot, sourcePath);
            });

            Assert.Contains("changed identity", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void SourceLease_RejectsPostLoadCatalogReplacement()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string sourcePath = Assert.Single(snapshot.Textures).ExportPath;
            byte[] catalogBytes = File.ReadAllBytes(catalog.CatalogFilePath);
            File.Delete(catalog.CatalogFilePath);
            File.WriteAllBytes(catalog.CatalogFilePath, catalogBytes);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
            {
                using AssetCatalogSourceLease _ = AssetCatalogSourceAccessService.Open(snapshot, sourcePath);
            });

            Assert.Contains("catalog", error.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Contains("identity", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void SourceLease_RejectsPostLoadRootReplacement()
        {
            if (!OperatingSystem.IsWindows())
                return;

            using TempAssetCatalog catalog = TempAssetCatalog.Create();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string sourcePath = Assert.Single(snapshot.Textures).ExportPath;
            string originalRoot = $"{catalog.RootPath}-original";
            Directory.Move(catalog.RootPath, originalRoot);
            try
            {
                Directory.CreateDirectory(Path.Combine(catalog.RootPath, "asset_catalog"));
                Directory.CreateDirectory(Path.Combine(catalog.RootPath, "exports"));
                File.Copy(
                    Path.Combine(originalRoot, "asset_catalog", "catalog.json"),
                    catalog.CatalogFilePath);
                File.Copy(
                    Path.Combine(originalRoot, "exports", "texture_one.png"),
                    sourcePath);

                InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                {
                    using AssetCatalogSourceLease _ = AssetCatalogSourceAccessService.Open(snapshot, sourcePath);
                });

                Assert.Contains("root", error.Message, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("identity", error.Message, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                DeleteTestDirectory(catalog.RootPath);
                Directory.Move(originalRoot, catalog.RootPath);
            }
        }

        [Fact]
        public void FindCatalogCandidates_ResolvesGeneratedCatalogsFromCandidateRoots()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create();
            string missing = Path.Combine(catalog.RootPath, "missing");

            IReadOnlyList<string> candidates = AssetCatalogService.FindCatalogCandidates(
                null,
                "",
                missing,
                catalog.RootPath,
                catalog.CatalogFilePath,
                Path.GetDirectoryName(catalog.CatalogFilePath)!);

            string resolved = Path.GetFullPath(catalog.CatalogFilePath);
            Assert.Equal(new[] { resolved }, candidates);
        }

        [Fact]
        public void FindCatalogCandidates_DoesNotTreatGameInstallFolderAsGeneratedCatalog()
        {
            string fakeGameRoot = Path.Combine(Path.GetTempPath(), "oce-fake-bea-install", Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(Path.Combine(fakeGameRoot, "data"));
                File.WriteAllText(Path.Combine(fakeGameRoot, "BEA.exe"), "placeholder executable marker");
                File.WriteAllText(Path.Combine(fakeGameRoot, "defaultoptions.bea"), "placeholder options marker");

                IReadOnlyList<string> candidates = AssetCatalogService.FindCatalogCandidates(fakeGameRoot);

                Assert.Empty(candidates);
            }
            finally
            {
                if (Directory.Exists(fakeGameRoot))
                {
                    Directory.Delete(fakeGameRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void BuildMissingCatalogStatus_CallsOutSelectedGameInstallWithoutLeakingPath()
        {
            string fakeGameRoot = Path.Combine(Path.GetTempPath(), "oce-fake-bea-install", Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(Path.Combine(fakeGameRoot, "data"));
                File.WriteAllText(Path.Combine(fakeGameRoot, "BEA.exe"), "placeholder executable marker");

                string status = AssetCatalogLoadStatusText.BuildMissingCatalogStatus(fakeGameRoot, detectedGameDirectory: fakeGameRoot);

                Assert.Contains("That is the game install, not an export catalog.", status);
                Assert.Contains("Asset Library is a catalog viewer, not an extractor.", status);
                Assert.Contains("asset_catalog/catalog.json", status);
                Assert.Contains("legacy extractor's local runtime dependencies", status);
                Assert.DoesNotContain(fakeGameRoot, status, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(fakeGameRoot))
                {
                    Directory.Delete(fakeGameRoot, recursive: true);
                }
            }
        }

        [Fact]
        public void Load_ReturnsEmptyForMissingCatalog()
        {
            string missing = Path.Combine(Path.GetTempPath(), "oce-missing-assets", Guid.NewGuid().ToString("N"));

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(missing);

            Assert.Equal(string.Empty, snapshot.CatalogFilePath);
            Assert.Empty(snapshot.Textures);
            Assert.Empty(snapshot.LooseMeshes);
            Assert.Empty(snapshot.EmbeddedMeshes);
            Assert.Empty(snapshot.Goodies);
        }

        [Fact]
        public void ModelPreviewCoverage_SummarizesWireframeAvailability()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            AssetModelPreviewCoverage coverage = new AssetModelPreviewCoverageService().Build(snapshot, sampleLimit: 5);

            Assert.Equal(2, coverage.TotalModelRows);
            Assert.Equal(1, coverage.LooseMeshRows);
            Assert.Equal(1, coverage.EmbeddedMeshRows);
            Assert.Equal(2, coverage.ExistingExportRows);
            Assert.Equal(2, coverage.MetadataAvailableRows);
            Assert.Equal(2, coverage.WireframeAvailableRows);
            Assert.Equal(2, coverage.RowsWithTextureCoordinates);
            Assert.Equal(2, coverage.RowsWithTextureCoordinateIndices);
            Assert.Equal(6, coverage.TotalTextureCoordinates);
            Assert.Equal(6, coverage.TotalTextureCoordinateIndices);
            Assert.Equal(2, coverage.RowsWithNormals);
            Assert.Equal(2, coverage.RowsWithNormalIndices);
            Assert.Equal(6, coverage.TotalNormals);
            Assert.Equal(6, coverage.TotalNormalIndices);
            Assert.Equal(2, coverage.RowsWithNormalMappingModes);
            Assert.Equal(2, coverage.RowsWithNormalReferenceModes);
            Assert.Contains("ByPolygonVertex", coverage.NormalMappingModes);
            Assert.Contains("IndexToDirect", coverage.NormalReferenceModes);
            Assert.Equal(2, coverage.RowsWithVertexColors);
            Assert.Equal(2, coverage.RowsWithVertexColorIndices);
            Assert.Equal(6, coverage.TotalVertexColors);
            Assert.Equal(6, coverage.TotalVertexColorIndices);
            Assert.Equal(2, coverage.RowsWithVertexColorMappingModes);
            Assert.Equal(2, coverage.RowsWithVertexColorReferenceModes);
            Assert.Contains("ByPolygonVertex", coverage.VertexColorMappingModes);
            Assert.Contains("IndexToDirect", coverage.VertexColorReferenceModes);
            Assert.Equal(2, coverage.RowsWithTextureCoordinateMappingModes);
            Assert.Equal(2, coverage.RowsWithTextureCoordinateReferenceModes);
            Assert.Contains("ByPolygonVertex", coverage.TextureCoordinateMappingModes);
            Assert.Contains("IndexToDirect", coverage.TextureCoordinateReferenceModes);
            Assert.Equal(2, coverage.RowsWithMaterialLayers);
            Assert.Equal(2, coverage.RowsWithMaterialAssignmentIndices);
            Assert.Equal(2, coverage.TotalMaterialLayerNodes);
            Assert.Equal(2, coverage.TotalMaterialAssignmentIndices);
            Assert.Equal(2, coverage.RowsWithMaterialMappingModes);
            Assert.Equal(2, coverage.RowsWithMaterialReferenceModes);
            Assert.Contains("AllSame", coverage.MaterialMappingModes);
            Assert.Contains("IndexToDirect", coverage.MaterialReferenceModes);
            Assert.Equal(2, coverage.RowsWithObjectConnections);
            Assert.Equal(2, coverage.RowsWithPropertyConnections);
            Assert.Equal(2, coverage.RowsWithTextureToMaterialConnections);
            Assert.Equal(2, coverage.TotalObjectConnections);
            Assert.Equal(2, coverage.TotalPropertyConnections);
            Assert.Equal(2, coverage.TotalTextureToMaterialConnections);
            Assert.Equal(2, coverage.RowsWithTextureToMaterialSlotNames);
            Assert.Contains("DiffuseColor", coverage.TextureToMaterialSlotNames);
            Assert.Equal(2, coverage.RowsWithMaterials);
            Assert.Equal(2, coverage.RowsWithTextureBindings);
            Assert.Equal(2, coverage.TotalMaterialNodes);
            Assert.Equal(2, coverage.TotalTextureBindingNodes);
            Assert.Equal(2, coverage.RowsWithCatalogMatchedTextureBindingFiles);
            Assert.Equal(0, coverage.RowsWithoutCatalogMatchedTextureBindingFiles);
            Assert.Equal(2, coverage.RowsWithAllTextureBindingFilesCatalogMatched);
            Assert.Equal(0, coverage.RowsWithAnyMissingCatalogTextureBindingFiles);
            Assert.Equal(2, coverage.TotalCatalogMatchedTextureBindingFiles);
            Assert.Equal(0, coverage.UnreadableExportRows);
            Assert.Empty(coverage.UnmatchedSamples);
            Assert.All(coverage.Samples, sample =>
            {
                Assert.DoesNotContain(catalog.RootPath, sample.SourceLabel, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(1, sample.MaterialCount);
                Assert.Equal(1, sample.TextureBindingCount);
                Assert.Contains("texture_one.png", sample.TextureBindingFileNames);
                Assert.Contains("Texture One", sample.CatalogMatchedTextureNames);
                Assert.Empty(sample.CatalogMissingTextureFileNames);
                Assert.Equal(3, sample.TextureCoordinateCount);
                Assert.Equal(3, sample.TextureCoordinateIndexCount);
                Assert.Equal(3, sample.NormalCount);
                Assert.Equal(3, sample.NormalIndexCount);
                Assert.Contains("ByPolygonVertex", sample.NormalMappingModes);
                Assert.Contains("IndexToDirect", sample.NormalReferenceModes);
                Assert.Equal(3, sample.VertexColorCount);
                Assert.Equal(3, sample.VertexColorIndexCount);
                Assert.Contains("ByPolygonVertex", sample.VertexColorMappingModes);
                Assert.Contains("IndexToDirect", sample.VertexColorReferenceModes);
                Assert.Contains("ByPolygonVertex", sample.TextureCoordinateMappingModes);
                Assert.Contains("IndexToDirect", sample.TextureCoordinateReferenceModes);
                Assert.Equal(1, sample.MaterialLayerCount);
                Assert.Equal(1, sample.MaterialAssignmentIndexCount);
                Assert.Contains("AllSame", sample.MaterialMappingModes);
                Assert.Contains("IndexToDirect", sample.MaterialReferenceModes);
                Assert.Equal(1, sample.ObjectConnectionCount);
                Assert.Equal(1, sample.PropertyConnectionCount);
                Assert.Equal(1, sample.TextureToMaterialConnectionCount);
                Assert.Contains("DiffuseColor", sample.TextureToMaterialSlotNames);
                Assert.True(sample.PreviewEdgeCount > 0);
            });
        }

        [Fact]
        public void ModelTextureLinks_ResolvesSelectedModelTextureNames()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            AssetLooseMeshItem mesh = Assert.Single(snapshot.LooseMeshes);

            AssetModelTextureLinks links = new AssetModelTextureLinkService().Build(snapshot.Textures, mesh.ModelSummary);

            Assert.Contains("texture_one.png", links.TextureBindingFileNames);
            Assert.Contains("Texture One", links.CatalogMatchedTextureNames);
            Assert.Single(links.CatalogMatchedTextureNames);
        }

        [Fact]
        public void ModelTextureLinks_IgnoresBlankBindingsAndMatchesPathVariants()
        {
            AssetTextureItem texture = new(
                "texture:textures/texture_one.tga",
                "textures/texture_one.tga",
                "Texture One",
                "dxtntextures",
                string.Empty,
                "texture_one.png",
                ExportExists: false,
                SourceFileCount: 1,
                ExportFileCount: 0,
                PackedReferenceCount: 1);
            AssetModelSummary summary = new(
                Format: "Binary FBX",
                FormatVersion: 7400,
                ByteSize: 1,
                GeometryCount: 0,
                ModelCount: 0,
                MaterialCount: 1,
                TextureBindingCount: 4,
                MaterialLayerCount: 0,
                MaterialAssignmentIndexCount: 0,
                MaterialMappingModes: Array.Empty<string>(),
                MaterialReferenceModes: Array.Empty<string>(),
                ObjectConnectionCount: 0,
                PropertyConnectionCount: 0,
                TextureToMaterialConnectionCount: 0,
                TextureToMaterialSlotNames: Array.Empty<string>(),
                MaterialNames: Array.Empty<string>(),
                TextureBindingNames: Array.Empty<string>(),
                TextureBindingFileNames:
                [
                    " ",
                    "\t",
                    "default10.png",
                    "base_color_texture.png",
                    @"textures\texture_one.tga.png",
                    "Texture One.dds"
                ],
                VertexCount: 0,
                PolygonIndexCount: 0,
                NormalCount: 0,
                NormalIndexCount: 0,
                NormalMappingModes: Array.Empty<string>(),
                NormalReferenceModes: Array.Empty<string>(),
                VertexColorCount: 0,
                VertexColorIndexCount: 0,
                VertexColorMappingModes: Array.Empty<string>(),
                VertexColorReferenceModes: Array.Empty<string>(),
                TextureCoordinateCount: 0,
                TextureCoordinateIndexCount: 0,
                TextureCoordinateMappingModes: Array.Empty<string>(),
                TextureCoordinateReferenceModes: Array.Empty<string>(),
                GeometryPreview: AssetModelGeometryPreview.Empty,
                MeshPayload: AssetModelMeshPayload.Empty,
                MetadataAvailable: true,
                Status: "metadata available.");

            AssetModelTextureLinks links = new AssetModelTextureLinkService().Build([texture], summary);

            Assert.DoesNotContain(links.TextureBindingFileNames, string.IsNullOrWhiteSpace);
            Assert.DoesNotContain("default10.png", links.TextureBindingFileNames);
            Assert.DoesNotContain("base_color_texture.png", links.TextureBindingFileNames);
            Assert.Contains("texture_one.tga.png", links.TextureBindingFileNames);
            Assert.Contains("Texture One.dds", links.TextureBindingFileNames);
            Assert.Equal(["Texture One"], links.CatalogMatchedTextureNames);
            Assert.Empty(links.CatalogMissingTextureFileNames);
        }

        [Fact]
        public void ModelTextureLinks_ReportsCatalogMissingTextureBindings()
        {
            AssetTextureItem texture = new(
                "texture:textures/texture_one.tga",
                "textures/texture_one.tga",
                "Texture One",
                "dxtntextures",
                string.Empty,
                "texture_one.png",
                ExportExists: false,
                SourceFileCount: 1,
                ExportFileCount: 0,
                PackedReferenceCount: 1);
            AssetModelSummary summary = new(
                Format: "Binary FBX",
                FormatVersion: 7400,
                ByteSize: 1,
                GeometryCount: 0,
                ModelCount: 0,
                MaterialCount: 1,
                TextureBindingCount: 2,
                MaterialLayerCount: 0,
                MaterialAssignmentIndexCount: 0,
                MaterialMappingModes: Array.Empty<string>(),
                MaterialReferenceModes: Array.Empty<string>(),
                ObjectConnectionCount: 0,
                PropertyConnectionCount: 0,
                TextureToMaterialConnectionCount: 0,
                TextureToMaterialSlotNames: Array.Empty<string>(),
                MaterialNames: Array.Empty<string>(),
                TextureBindingNames: Array.Empty<string>(),
                TextureBindingFileNames:
                [
                    "texture_one.png",
                    "sidecar_only_diffuse.png"
                ],
                VertexCount: 0,
                PolygonIndexCount: 0,
                NormalCount: 0,
                NormalIndexCount: 0,
                NormalMappingModes: Array.Empty<string>(),
                NormalReferenceModes: Array.Empty<string>(),
                VertexColorCount: 0,
                VertexColorIndexCount: 0,
                VertexColorMappingModes: Array.Empty<string>(),
                VertexColorReferenceModes: Array.Empty<string>(),
                TextureCoordinateCount: 0,
                TextureCoordinateIndexCount: 0,
                TextureCoordinateMappingModes: Array.Empty<string>(),
                TextureCoordinateReferenceModes: Array.Empty<string>(),
                GeometryPreview: AssetModelGeometryPreview.Empty,
                MeshPayload: AssetModelMeshPayload.Empty,
                MetadataAvailable: true,
                Status: "metadata available.");

            AssetModelTextureLinks links = new AssetModelTextureLinkService().Build([texture], summary);

            Assert.Equal(["Texture One"], links.CatalogMatchedTextureNames);
            Assert.Equal(["sidecar_only_diffuse.png"], links.CatalogMissingTextureFileNames);
        }

        [Fact]
        public void ModelPreviewCoverage_DistinguishesAllCatalogMatchedRowsFromSidecarNeededRows()
        {
            AssetTextureItem texture = new(
                "texture:textures/texture_one.tga",
                "textures/texture_one.tga",
                "Texture One",
                "dxtntextures",
                string.Empty,
                "texture_one.png",
                ExportExists: false,
                SourceFileCount: 1,
                ExportFileCount: 0,
                PackedReferenceCount: 1);
            AssetModelSummary directSummary = CreateModelSummary(["texture_one.png"]);
            AssetModelSummary sidecarSummary = CreateModelSummary(["texture_one.png", "sidecar_only_diffuse.png"]);
            AssetCatalogSnapshot snapshot = new(
                string.Empty,
                AssetCatalogSummary.Empty,
                [texture],
                [
                    new AssetLooseMeshItem(
                        "mesh:direct",
                        "mesh/direct.msh",
                        "Direct model",
                        string.Empty,
                        "direct.fbx",
                        ExportExists: true,
                        SourceFileCount: 1,
                        ExportFileCount: 1,
                        PackedReferenceCount: 1,
                        directSummary),
                    new AssetLooseMeshItem(
                        "mesh:sidecar",
                        "mesh/sidecar.msh",
                        "Sidecar model",
                        string.Empty,
                        "sidecar.fbx",
                        ExportExists: true,
                        SourceFileCount: 1,
                        ExportFileCount: 1,
                        PackedReferenceCount: 1,
                        sidecarSummary)
                ],
                Array.Empty<AssetEmbeddedMeshItem>(),
                Array.Empty<AssetGoodieItem>());

            AssetModelPreviewCoverage coverage = new AssetModelPreviewCoverageService().Build(snapshot, sampleLimit: 10);

            Assert.Equal(2, coverage.RowsWithCatalogMatchedTextureBindingFiles);
            Assert.Equal(2, coverage.RowsWithTextureBindings);
            Assert.Equal(1, coverage.RowsWithAllTextureBindingFilesCatalogMatched);
            Assert.Equal(1, coverage.RowsWithAnyMissingCatalogTextureBindingFiles);
            Assert.Contains(coverage.Samples, row =>
                row.Label == "Sidecar model" &&
                row.CatalogMissingTextureFileNames.SequenceEqual(["sidecar_only_diffuse.png"]));
        }


        [Fact]
        public void ModelTextureLinks_ResolvesSidecarTexturesFromExportRoot()
        {
            string root = Path.Combine(Path.GetTempPath(), $"asset-sidecars-{Guid.NewGuid():N}");
            try
            {
                string looseMeshRoot = Path.Combine(root, "asset_export", "loose_meshes");
                string embeddedMeshRoot = Path.Combine(root, "asset_export", "embedded_meshes");
                string meshTextureRoot = Path.Combine(looseMeshRoot, "MeshTextures");
                Directory.CreateDirectory(looseMeshRoot);
                Directory.CreateDirectory(embeddedMeshRoot);
                Directory.CreateDirectory(meshTextureRoot);
                string looseModelPath = Path.Combine(looseMeshRoot, "ship_body.msh_binary.fbx");
                string embeddedModelPath = Path.Combine(embeddedMeshRoot, "body00_binary.fbx");
                File.WriteAllText(looseModelPath, "fbx");
                File.WriteAllText(embeddedModelPath, "fbx");
                File.WriteAllText(Path.Combine(meshTextureRoot, "texture_one.png"), "png");
                File.WriteAllText(Path.Combine(meshTextureRoot, "texture_two.png"), "png");
                File.WriteAllText(Path.Combine(meshTextureRoot, "notes.txt"), "ignore");
                string catalogPath = WriteSingleTextureCatalog(root, "exports/missing.png");
                AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogPath);
                snapshot = snapshot with
                {
                    LooseMeshes =
                    [
                        new AssetLooseMeshItem(
                            "mesh:loose",
                            "mesh/loose.msh",
                            "Loose model",
                            looseModelPath,
                            Path.GetFileName(looseModelPath),
                            ExportExists: true,
                            SourceFileCount: 1,
                            ExportFileCount: 1,
                            PackedReferenceCount: 1,
                            CreateModelSummary(["texture_one.png", "texture_two.tga"])),
                    ],
                    EmbeddedMeshes =
                    [
                        new AssetEmbeddedMeshItem(
                            "mesh:embedded",
                            "archive.aya",
                            "body00",
                            "Embedded model",
                            embeddedModelPath,
                            Path.GetFileName(embeddedModelPath),
                            ExportExists: true,
                            CreateModelSummary(["texture_one.png"])),
                    ],
                };
                snapshot = AttachTrustedCatalog(root, snapshot);

                AssetModelTextureLinkService service = new();
                IReadOnlyList<AssetModelSidecarTexture> looseMatches = service.ResolveSidecarTextures(
                    snapshot,
                    looseModelPath,
                    [@"textures\texture_one.png", "texture_two.tga"]);
                IReadOnlyList<AssetModelSidecarTexture> embeddedMatches = service.ResolveSidecarTextures(
                    snapshot,
                    embeddedModelPath,
                    ["texture_one.png"]);

                Assert.Equal(2, looseMatches.Count);
                Assert.Contains(looseMatches, match => match.FileName == "texture_one.png" && match.ExactFileNameMatch);
                Assert.Contains(looseMatches, match => match.FileName == "texture_two.png" && !match.ExactFileNameMatch);
                Assert.Single(embeddedMatches);
                Assert.Equal("texture_one.png", embeddedMatches[0].FileName);
            }
            finally
            {
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        [Fact]
        public void GoodiePreviewCoverage_SummarizesGoodiePreviewReadiness()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            GoodiePreviewCoverage coverage = new GoodiePreviewCoverageService().Build(snapshot, sampleLimit: 10);

            Assert.Equal(3, coverage.TotalGoodieRows);
            Assert.Equal(2, coverage.SourceGridVisibleRows);
            Assert.Equal(1, coverage.SourceGridHiddenRows);
            Assert.Equal(2, coverage.TextureBearingRows);
            Assert.Equal(2, coverage.TextureMatchedRows);
            Assert.Equal(2, coverage.TexturePreviewReadyRows);
            Assert.Equal(1, coverage.ModelBearingRows);
            Assert.Equal(1, coverage.ModelMatchedRows);
            Assert.Equal(1, coverage.ModelExportReadyRows);
            Assert.Equal(1, coverage.ModelWireframeReadyRows);
            Assert.Equal(1, coverage.VideoRows);
            Assert.Equal(1, coverage.VideoCatalogLinkedRows);
            Assert.Equal(0, coverage.RowsWithoutLocalPreview);
            Assert.Contains(coverage.Samples, row =>
                row.Index == 71 &&
                !row.IsSourceGridVisible &&
                row.TexturePreviewReady &&
                row.Status.Contains("not exposed", StringComparison.OrdinalIgnoreCase));
        }

        [Fact]
        public void ReadabilityCoverage_SummarizesTextureAndModelExportsWithoutLocalPaths()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            AssetCatalogReadability readability = new AssetCatalogReadabilityService().Build(snapshot, sampleLimit: 10);

            Assert.Equal(1, readability.TextureRows);
            Assert.Equal(1, readability.TextureExportRows);
            Assert.Equal(1, readability.TextureReadablePngRows);
            Assert.Equal(0, readability.TextureMissingExportRows);
            Assert.Equal(0, readability.TextureUnreadableExportRows);
            AssetTextureReadabilityRow textureSample = Assert.Single(readability.TextureSamples);
            Assert.Equal(1, textureSample.Width);
            Assert.Equal(1, textureSample.Height);
            Assert.True(textureSample.ReadablePng);
            Assert.DoesNotContain(catalog.RootPath, textureSample.SourceLabel, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(catalog.RootPath, textureSample.Label, StringComparison.OrdinalIgnoreCase);

            Assert.Equal(2, readability.TotalModelRows);
            Assert.Equal(2, readability.ModelExportRows);
            Assert.Equal(2, readability.ModelMetadataAvailableRows);
            Assert.Equal(2, readability.ModelWireframeAvailableRows);
            Assert.Equal(0, readability.ModelMissingExportRows);
            Assert.Equal(0, readability.ModelUnreadableExportRows);
            Assert.All(readability.ModelSamples, sample =>
            {
                Assert.True(sample.MetadataAvailable);
                Assert.True(sample.WireframeAvailable);
                Assert.DoesNotContain(catalog.RootPath, sample.SourceLabel, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, sample.Label, StringComparison.OrdinalIgnoreCase);
            });
        }

        private sealed class TempAssetCatalog : IDisposable
        {
            public string RootPath { get; }
            public string PackageRootPath { get; }
            public string CatalogFilePath { get; }

            private TempAssetCatalog(
                string rootPath,
                string packageRootPath,
                string catalogFilePath)
            {
                RootPath = rootPath;
                PackageRootPath = packageRootPath;
                CatalogFilePath = catalogFilePath;
            }

            public static TempAssetCatalog Create(bool withModelPreviewExports = false)
            {
                string root = Path.Combine(Path.GetTempPath(), "oce-asset-catalog-tests", Guid.NewGuid().ToString("N"));
                string catalogDir = Path.Combine(root, "asset_catalog");
                string exportsDir = Path.Combine(root, "exports");
                Directory.CreateDirectory(catalogDir);
                Directory.CreateDirectory(exportsDir);
                File.WriteAllBytes(Path.Combine(exportsDir, "texture_one.png"), BuildMinimalPng());
                if (withModelPreviewExports)
                {
                    byte[] fbx = BuildMinimalBinaryFbx();
                    File.WriteAllBytes(Path.Combine(exportsDir, "ship_body.msh_binary.fbx"), fbx);
                    File.WriteAllBytes(Path.Combine(exportsDir, "body00_binary.fbx"), fbx);
                }
                else
                {
                    File.WriteAllText(Path.Combine(exportsDir, "ship_body.msh_binary.fbx"), "not a real fbx");
                }

                string catalogPath = Path.Combine(catalogDir, "catalog.json");
                File.WriteAllText(catalogPath, """
                {
                  "schema_version": 2,
                  "path_contract": "bundle-root-relative",
                  "summary": {
                    "texture_catalog_entries": 828,
                    "loose_mesh_catalog_entries": 213,
                    "embedded_mesh_catalog_entries": 139,
                    "video_catalog_entries": 66,
                    "language_catalog_entries": 2571,
                    "goodie_catalog_entries": 3,
                    "total_catalog_entries": 3820
                  },
                  "textures": [
                    {
                      "catalog_id": "texture:textures/texture_one.tga",
                      "kind": "texture",
                      "canonical_ref": "textures/texture_one.tga",
                      "source_roots": ["dxtntextures"],
                      "export_png_paths": ["exports/texture_one.png"],
                      "source_aya_count": 2,
                      "export_png_count": 1,
                      "packed_text_ref_count": 5,
                      "gdie_ref_count": 2,
                      "total_packed_ref_count": 7,
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
                      "packed_reference_count": 3,
                      "gdie_ref_count": 1,
                      "total_packed_ref_count": 4,
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
                  "goodies": [
                    {
                      "catalog_id": "goodie:008",
                      "kind": "goodie",
                      "index": 8,
                      "display_name": "Goodie 008 - BE:A Unit-00 'Prototype'",
                      "content_kind": "Model",
                      "source_title": "BE:A Unit-00 'Prototype'",
                      "source_archive": "goodie_08_res_PC.aya",
                      "gdie_family": "goodie_08_res_PC.aya",
                      "texture_refs": ["textures/texture_one.tga"],
                      "mesh_refs": ["ship_body.msh"],
                      "primary_texture_ref": "textures/texture_one.tga",
                      "primary_mesh_ref": "ship_body.msh",
                      "video_sequence_id": "",
                      "video_catalog_id": "",
                      "video_relative_path": ""
                    },
                    {
                      "catalog_id": "goodie:071",
                      "kind": "goodie",
                      "index": 71,
                      "display_name": "Goodie 071 - All Configurations",
                      "content_kind": "Artwork",
                      "source_title": "All Configurations",
                      "source_archive": "goodie_71_res_PC.aya",
                      "gdie_family": "goodie_71_res_PC.aya",
                      "texture_refs": ["textures/texture_one.tga"],
                      "mesh_refs": [],
                      "primary_texture_ref": "textures/texture_one.tga",
                      "primary_mesh_ref": "",
                      "video_sequence_id": "",
                      "video_catalog_id": "",
                      "video_relative_path": ""
                    },
                    {
                      "catalog_id": "goodie:232",
                      "kind": "goodie",
                      "index": 232,
                      "display_name": "Goodie 232 - Cutscene 33",
                      "content_kind": "Video",
                      "source_archive": "",
                      "gdie_family": "",
                      "texture_refs": [],
                      "mesh_refs": [],
                      "primary_texture_ref": "",
                      "primary_mesh_ref": "",
                      "video_sequence_id": "33",
                      "video_catalog_id": "video:cutscene:33",
                      "video_relative_path": "FMV/33.vid"
                    }
                  ]
                }
                """);

                string packageRoot = Path.Combine(
                    Path.GetDirectoryName(root)!,
                    $"{Path.GetFileName(root)}-material-package");
                return new TempAssetCatalog(root, packageRoot, catalogPath);
            }

            public void Dispose()
            {
                try
                {
                    if (Directory.Exists(RootPath))
                    {
                        Directory.Delete(RootPath, recursive: true);
                    }
                    if (Directory.Exists(PackageRootPath))
                    {
                        Directory.Delete(PackageRootPath, recursive: true);
                    }
                }
                catch
                {
                    // Best effort test cleanup only.
                }
            }
        }

        private static string FindRepoRoot()
        {
            DirectoryInfo? current = new(AppContext.BaseDirectory);
            while (current is not null)
            {
                if (File.Exists(Path.Combine(current.FullName, "tools", "export_asset_catalog.py")))
                    return current.FullName;
                current = current.Parent;
            }

            throw new DirectoryNotFoundException("Could not locate the repository root for the catalog producer contract test.");
        }

        private static string CreateTemporaryDirectory(string prefix)
        {
            string path = Path.Combine(Path.GetTempPath(), prefix, Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(path);
            return path;
        }

        private static IReadOnlyList<string> CaptureDirectoryTree(string root)
        {
            return Directory
                .EnumerateFileSystemEntries(root, "*", SearchOption.AllDirectories)
                .Select(path =>
                {
                    string relativePath = Path.GetRelativePath(root, path).Replace('\\', '/');
                    if (Directory.Exists(path))
                        return $"D|{relativePath}";

                    byte[] hash = System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(path));
                    return $"F|{relativePath}|{new FileInfo(path).Length}|{Convert.ToHexString(hash)}";
                })
                .OrderBy(static entry => entry, StringComparer.Ordinal)
                .ToList();
        }

        private static string WriteSingleTextureCatalog(string root, params string[] exportPaths)
        {
            string catalogDirectory = Path.Combine(root, "asset_catalog");
            Directory.CreateDirectory(catalogDirectory);
            string catalogPath = Path.Combine(catalogDirectory, "catalog.json");
            File.WriteAllText(catalogPath, JsonSerializer.Serialize(new
            {
                schema_version = 2,
                path_contract = "bundle-root-relative",
                summary = new
                {
                    texture_catalog_entries = 1,
                    total_catalog_entries = 1,
                },
                textures = new[]
                {
                    new
                    {
                        catalog_id = "texture:test",
                        canonical_ref = "textures/test.tga",
                        export_png_paths = exportPaths,
                    },
                },
                loose_meshes = Array.Empty<object>(),
                embedded_meshes = Array.Empty<object>(),
                goodies = Array.Empty<object>(),
            }));
            return catalogPath;
        }

        private static AssetCatalogSnapshot AttachTrustedCatalog(
            string root,
            AssetCatalogSnapshot snapshot)
        {
            string catalogPath = WriteSingleTextureCatalog(root, "exports/missing.png");
            AssetCatalogSelection selection = AssetCatalogFileSafety.ResolveSelection(catalogPath)
                ?? throw new InvalidOperationException("Synthetic test catalog selection was rejected.");
            using AssetCatalogLoadSession session = AssetCatalogFileSafety.BeginLoad(selection);
            IReadOnlyList<string> sourcePaths = snapshot.Textures
                .Select(static item => item.ExportPath)
                .Concat(snapshot.LooseMeshes.Select(static item => item.ExportPath))
                .Concat(snapshot.EmbeddedMeshes.Select(static item => item.ExportPath))
                .Where(static path => !string.IsNullOrWhiteSpace(path))
                .Distinct(FileMutationSafety.PathComparer)
                .ToList();
            foreach (string sourcePath in sourcePaths)
            {
                using AssetCatalogSourceRead _ = session.OpenSource(
                    sourcePath,
                    "Synthetic catalog snapshot source");
            }
            IReadOnlyDictionary<string, IReadOnlyList<AssetModelSidecarTexture>> sidecars =
                AssetModelTextureLinkService.CaptureSnapshotSidecars(
                    session,
                    snapshot.LooseMeshes.Select(static item => item.ExportPath)
                        .Concat(snapshot.EmbeddedMeshes.Select(static item => item.ExportPath)));
            AssetCatalogTrustEvidence trust = session.CaptureTrustEvidence();
            if (string.IsNullOrWhiteSpace(session.CatalogFilePath) ||
                string.IsNullOrWhiteSpace(session.TrustedExportRoot))
            {
                throw new InvalidOperationException("Synthetic test catalog did not establish a trusted export root.");
            }

            return snapshot with
            {
                CatalogFilePath = session.CatalogFilePath,
                TrustedExportRoot = session.TrustedExportRoot,
                TrustEvidence = trust,
                SealedSidecarTexturesByModelPath = sidecars,
            };
        }

        private static void DeleteTestDirectory(string path)
        {
            try
            {
                if (Directory.Exists(path))
                    Directory.Delete(path, recursive: true);
            }
            catch
            {
                // Best effort test cleanup only.
            }
        }

        private static byte[] BuildMinimalPng()
        {
            return
            [
                137, 80, 78, 71, 13, 10, 26, 10,
                0, 0, 0, 13, 73, 72, 68, 82,
                0, 0, 0, 1, 0, 0, 0, 1,
                8, 6, 0, 0, 0, 31, 21, 196,
                137, 0, 0, 0, 13, 73, 68, 65,
                84, 120, 156, 99, 248, 207, 192,
                240, 31, 0, 5, 0, 1, 255, 137,
                153, 61, 29, 0, 0, 0, 0, 73,
                69, 78, 68, 174, 66, 96, 130
            ];
        }

        private static AssetModelSummary CreateModelSummary(IReadOnlyList<string> textureBindingFileNames)
        {
            return new AssetModelSummary(
                Format: "Binary FBX",
                FormatVersion: 7400,
                ByteSize: 1,
                GeometryCount: 0,
                ModelCount: 0,
                MaterialCount: 1,
                TextureBindingCount: textureBindingFileNames.Count,
                MaterialLayerCount: 1,
                MaterialAssignmentIndexCount: 1,
                MaterialMappingModes: ["AllSame"],
                MaterialReferenceModes: ["IndexToDirect"],
                ObjectConnectionCount: 1,
                PropertyConnectionCount: textureBindingFileNames.Count == 0 ? 0 : 1,
                TextureToMaterialConnectionCount: textureBindingFileNames.Count == 0 ? 0 : 1,
                TextureToMaterialSlotNames: textureBindingFileNames.Count == 0 ? Array.Empty<string>() : ["DiffuseColor"],
                MaterialNames: Array.Empty<string>(),
                TextureBindingNames: Array.Empty<string>(),
                TextureBindingFileNames: textureBindingFileNames,
                VertexCount: 3,
                PolygonIndexCount: 3,
                NormalCount: 3,
                NormalIndexCount: 3,
                NormalMappingModes: ["ByPolygonVertex"],
                NormalReferenceModes: ["IndexToDirect"],
                VertexColorCount: 3,
                VertexColorIndexCount: 3,
                VertexColorMappingModes: ["ByPolygonVertex"],
                VertexColorReferenceModes: ["IndexToDirect"],
                TextureCoordinateCount: 3,
                TextureCoordinateIndexCount: 3,
                TextureCoordinateMappingModes: ["ByPolygonVertex"],
                TextureCoordinateReferenceModes: ["IndexToDirect"],
                GeometryPreview: AssetModelGeometryPreview.Empty,
                MeshPayload: AssetModelMeshPayload.Empty,
                MetadataAvailable: true,
                Status: "metadata available.");
        }

        private static byte[] BuildMinimalBinaryFbx()
        {
            using MemoryStream stream = new();
            using BinaryWriter writer = new(stream, Encoding.ASCII, leaveOpen: true);

            writer.Write(Encoding.ASCII.GetBytes("Kaydara FBX Binary  "));
            writer.Write((byte)0);
            writer.Write((byte)0x1A);
            writer.Write((byte)0);
            writer.Write(7400);


            WriteNode(
                writer,
                "Objects",
                props: [],
                children:
                [
                    () => WriteNode(
                        writer,
                        "Geometry",
                        props:
                        [
                            () => WriteLongProperty(writer, 1),
                            () => WriteStringProperty(writer, "Triangle\0\u0001Geometry"),
                            () => WriteStringProperty(writer, "Mesh")
                        ],
                        children:
                        [
                            () => WriteNode(
                                writer,
                                "Vertices",
                                props:
                                [
                                    () => WriteDoubleArrayProperty(writer, [0, 0, 0, 1, 0, 0, 0, 1, 0])
                                ],
                                children: []),
                            () => WriteNode(
                                writer,
                                "PolygonVertexIndex",
                                props:
                                [
                                    () => WriteIntArrayProperty(writer, [0, 1, -3])
                                ],
                                children: []),
                            () => WriteNode(
                                writer,
                                "LayerElementNormal",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Normals",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [0, 0, 1, 0, 0, 1, 0, 0, 1])
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "NormalsIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2])
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementUV",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "UV",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [0, 0, 1, 0, 0, 1])
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "UVIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2])
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementColor",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Colors",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1])
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ColorIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2])
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementMaterial",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "AllSame")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Materials",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0])
                                        ],
                                        children: [])
                                ])
                        ]),
                    () => WriteNode(
                        writer,
                        "Material",
                        props:
                        [
                            () => WriteLongProperty(writer, 2),
                            () => WriteStringProperty(writer, "Material1\0\u0001Material"),
                            () => WriteStringProperty(writer, string.Empty)
                        ],
                        children: []),
                    () => WriteNode(
                        writer,
                        "Texture",
                        props:
                        [
                            () => WriteLongProperty(writer, 3),
                            () => WriteStringProperty(writer, "base_color_texture\0\u0001Texture"),
                            () => WriteStringProperty(writer, string.Empty)
                        ],
                        children:
                        [
                            () => WriteNode(
                                writer,
                                "Properties70",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "P",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "FileName"),
                                            () => WriteStringProperty(writer, "KString"),
                                            () => WriteStringProperty(writer, string.Empty),
                                            () => WriteStringProperty(writer, "A"),
                                            () => WriteStringProperty(writer, @"C:\exports\texture_one.png")
                                        ],
                                        children: [])
                                ])
                        ])
                ]);
            WriteNode(
                writer,
                "Connections",
                props: [],
                children:
                [
                    () => WriteNode(
                        writer,
                        "C",
                        props:
                        [
                            () => WriteStringProperty(writer, "OO"),
                            () => WriteLongProperty(writer, 2),
                            () => WriteLongProperty(writer, 1)
                        ],
                        children: []),
                    () => WriteNode(
                        writer,
                        "C",
                        props:
                        [
                            () => WriteStringProperty(writer, "OP"),
                            () => WriteLongProperty(writer, 3),
                            () => WriteLongProperty(writer, 2),
                            () => WriteStringProperty(writer, "DiffuseColor")
                        ],
                        children: [])
                ]);
            WriteSentinel(writer);

            return stream.ToArray();
        }

        private static void WriteNode(BinaryWriter writer, string name, Action[] props, Action[] children)
        {
            long headerPosition = writer.BaseStream.Position;
            writer.Write((uint)0);
            writer.Write((uint)props.Length);
            writer.Write((uint)0);
            writer.Write((byte)name.Length);
            writer.Write(Encoding.ASCII.GetBytes(name));

            long propertyStart = writer.BaseStream.Position;
            foreach (Action prop in props)
            {
                prop();
            }

            long propertyEnd = writer.BaseStream.Position;
            foreach (Action child in children)
            {
                child();
            }

            if (children.Length > 0)
            {
                WriteSentinel(writer);
            }

            long endPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = headerPosition;
            writer.Write((uint)endPosition);
            writer.Write((uint)props.Length);
            writer.Write((uint)(propertyEnd - propertyStart));
            writer.Write((byte)name.Length);
            writer.BaseStream.Position = endPosition;
        }

        private static void WriteLongProperty(BinaryWriter writer, long value)
        {
            writer.Write((byte)'L');
            writer.Write(value);
        }

        private static void WriteStringProperty(BinaryWriter writer, string value)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(value);
            writer.Write((byte)'S');
            writer.Write((uint)bytes.Length);
            writer.Write(bytes);
        }

        private static void WriteDoubleArrayProperty(BinaryWriter writer, double[] values)
        {
            writer.Write((byte)'d');
            writer.Write((uint)values.Length);
            writer.Write((uint)0);
            writer.Write((uint)(values.Length * sizeof(double)));
            foreach (double value in values)
            {
                writer.Write(value);
            }
        }

        private static void WriteIntArrayProperty(BinaryWriter writer, int[] values)
        {
            writer.Write((byte)'i');
            writer.Write((uint)values.Length);
            writer.Write((uint)0);
            writer.Write((uint)(values.Length * sizeof(int)));
            foreach (int value in values)
            {
                writer.Write(value);
            }
        }

        private static void WriteSentinel(BinaryWriter writer)
        {
            writer.Write(new byte[13]);
        }

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool CreateHardLink(
            string lpFileName,
            string lpExistingFileName,
            IntPtr lpSecurityAttributes);
    }
}
