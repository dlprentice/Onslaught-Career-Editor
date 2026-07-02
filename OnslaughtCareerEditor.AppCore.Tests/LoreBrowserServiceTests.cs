using Onslaught___Career_Editor;
using System;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.IO;
using System.Linq;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class LoreBrowserServiceTests : IDisposable
    {
        private readonly string _tempRoot;
        private readonly string _repoRoot;

        public LoreBrowserServiceTests()
        {
            _tempRoot = Path.Combine(Path.GetTempPath(), "OnslaughtCareerEditorTests", Guid.NewGuid().ToString("N"));
            _repoRoot = Path.Combine(_tempRoot, "repo");
            Directory.CreateDirectory(_repoRoot);
        }

        [Fact]
        public void LoadIndex_UsesBookOrderAndFindsHomeDocument()
        {
            string loreBook = CreateLoreBookSkeleton();
            File.WriteAllText(Path.Combine(loreBook, "BOOK.md"), """
# Test Lore Book
- [Start Here](Start-Here.md)
- Part I
  - [World Lore](lore/world-lore.md)
  - [Characters](lore/characters.md)
""");
            File.WriteAllText(Path.Combine(loreBook, "Start-Here.md"), "# Start Here\n\nWelcome.");
            Directory.CreateDirectory(Path.Combine(loreBook, "lore"));
            File.WriteAllText(Path.Combine(loreBook, "lore", "world-lore.md"), "# World Lore");
            File.WriteAllText(Path.Combine(loreBook, "lore", "characters.md"), "# Characters");

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_repoRoot);

            Assert.True(index.UsingLoreBook);
            Assert.NotNull(index.HomeDocument);
            Assert.Equal("Start Here", index.HomeDocument!.Title);
            Assert.Equal(3, index.Documents.Count);
            Assert.Equal("Part I", index.RootItems[1].Title);
            Assert.Equal("World Lore", index.RootItems[1].Children[0].Title);
        }

        [Fact]
        public void LoadIndex_FindsPackagedLoreBookSiblingFromAppFolder()
        {
            string bundleRoot = Path.Combine(_tempRoot, "bundle");
            string appFolder = Path.Combine(bundleRoot, "app");
            string loreBook = Path.Combine(bundleRoot, "lore-book");
            Directory.CreateDirectory(appFolder);
            Directory.CreateDirectory(loreBook);
            File.WriteAllText(Path.Combine(loreBook, "BOOK.md"), "- [Packaged Home](Packaged-Home.md)");
            File.WriteAllText(Path.Combine(loreBook, "Packaged-Home.md"), "# Packaged Home");

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(appFolder);

            Assert.True(index.UsingLoreBook);
            Assert.Equal(bundleRoot, index.ProjectRoot);
            Assert.NotNull(index.HomeDocument);
            Assert.Equal("Packaged Home", index.HomeDocument!.Title);
        }

        [Fact]
        public void LoadIndex_IncompleteLorePackWithoutLoreBookFailsClosedWithoutEchoingResolvedDirectory()
        {
            string packDirectory = Path.Combine(_repoRoot, "lore-pack");
            Directory.CreateDirectory(packDirectory);
            File.WriteAllText(Path.Combine(packDirectory, "onslaught-lore.v1.index.json"), "{}", Encoding.UTF8);

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            Assert.Equal("Lore content pack content is invalid.", ex.Message);
            Assert.DoesNotContain(_repoRoot, ex.Message, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("lore-book", ex.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void LoadIndex_IncompleteLorePackDoesNotFallbackToLoreBook()
        {
            string loreBook = CreateLoreBookSkeleton();
            File.WriteAllText(Path.Combine(loreBook, "BOOK.md"), "- [Fallback](Fallback.md)");
            File.WriteAllText(Path.Combine(loreBook, "Fallback.md"), "# Fallback");
            string packDirectory = Path.Combine(_repoRoot, "lore-pack");
            Directory.CreateDirectory(packDirectory);
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.index.json"),
                JsonSerializer.Serialize(new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-start",
                            relativePath = "Start.md",
                            title = "Start",
                            sha256 = Sha256Text("# Start"),
                            byteLength = Encoding.UTF8.GetByteCount("# Start"),
                            order = 0
                        }
                    }
                }),
                Encoding.UTF8);

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "content is invalid", "Fallback.md", loreBook);
        }

        [Fact]
        public void LoadIndex_ContentOnlyLorePackDoesNotFallbackToLoreBook()
        {
            string loreBook = CreateLoreBookSkeleton();
            File.WriteAllText(Path.Combine(loreBook, "BOOK.md"), "- [Fallback](Fallback.md)");
            File.WriteAllText(Path.Combine(loreBook, "Fallback.md"), "# Fallback");
            string packDirectory = Path.Combine(_repoRoot, "lore-pack");
            Directory.CreateDirectory(packDirectory);
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.jsonl"),
                SerializeLorePackContentRow("doc-start", "Start.md", "# Start") + Environment.NewLine,
                Encoding.UTF8);

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "index is invalid", "Fallback.md", loreBook);
        }

        [Fact]
        public void LoadIndex_EmptyLorePackDoesNotFallbackToLoreBook()
        {
            string loreBook = CreateLoreBookSkeleton();
            File.WriteAllText(Path.Combine(loreBook, "BOOK.md"), "- [Fallback](Fallback.md)");
            File.WriteAllText(Path.Combine(loreBook, "Fallback.md"), "# Fallback");
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 0,
                    documents = Array.Empty<object>()
                });

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "index is invalid", "Fallback.md", loreBook);
        }


        [Fact]
        public void FilterTree_MatchesDocumentTextAndKeepsBranch()
        {
            string loreBook = CreateLoreBookSkeleton();
            File.WriteAllText(Path.Combine(loreBook, "BOOK.md"), """
- [Start Here](Start-Here.md)
- Part I
  - [World Lore](lore/world-lore.md)
""");
            File.WriteAllText(Path.Combine(loreBook, "Start-Here.md"), "# Start Here");
            Directory.CreateDirectory(Path.Combine(loreBook, "lore"));
            File.WriteAllText(Path.Combine(loreBook, "lore", "world-lore.md"), "# World Lore\n\nAquila sector reference.");

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_repoRoot);
            var filtered = service.FilterTree(index.RootItems, "Aquila");

            Assert.Single(filtered);
            Assert.Equal("Part I", filtered[0].Title);
            Assert.Single(filtered[0].Children);
            Assert.Equal("World Lore", filtered[0].Children[0].Title);
        }

        [Fact]
        public void LoadIndex_UsesLorePackWhenPresent()
        {
            string loreBook = CreateLoreBookSkeleton();
            File.WriteAllText(Path.Combine(loreBook, "BOOK.md"), "- [Start Here](Start-Here.md)");
            File.WriteAllText(Path.Combine(loreBook, "Start-Here.md"), "# Start Here");
            WriteLorePack(
                ("BOOK.md", "# Book\n\nWelcome."),
                ("deep/Deep-Research.md", "# Deep Research\n\nAquila sector content."));

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_repoRoot);

            Assert.True(index.UsingContentPack);
            Assert.Equal("content-pack", index.SourceKind);
            Assert.Equal(2, index.Documents.Count);
            Assert.Contains(index.Documents, doc => doc.RelativePath == "deep/Deep-Research.md");

            var filtered = service.FilterTree(index.RootItems, "Aquila sector");
            Assert.Single(filtered);
            Assert.Equal("deep", filtered[0].Title);
        }

        [Theory]
        [InlineData("C:/Users/Alice/private.md", "C:", "Users")]
        [InlineData(@"C:\Users\Alice\private.md", @"C:\", "Users")]
        [InlineData(@"\\server\share\private.md", @"\\server", "share")]
        [InlineData("../private.md", "..", "private.md")]
        [InlineData("safe/../../private.md", "..", "private.md")]
        [InlineData(@"safe\private.md", @"\", "private.md")]
        [InlineData("safe//private.md", "safe//", "private.md")]
        public void LoadIndex_RejectsMalformedLorePackRelativePathsWithoutEchoingInput(
            string relativePath,
            string firstForbiddenToken,
            string secondForbiddenToken)
        {
            WriteLorePackRows(new LorePackFixtureRow("doc-LEAKPROBE", relativePath, "# Unsafe"));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(
                ex,
                "invalid document path",
                relativePath,
                firstForbiddenToken,
                secondForbiddenToken,
                "LEAKPROBE");
        }

        [Fact]
        public void LoadIndex_RejectsDuplicateLorePackIdWithoutEchoingId()
        {
            const string maliciousId = "doc-duplicate-id-leak";
            WriteLorePackRows(
                new LorePackFixtureRow(maliciousId, "One.md", "# One"),
                new LorePackFixtureRow(maliciousId, "Two.md", "# Two"));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "duplicate document identifiers", maliciousId, "duplicate-id-leak");
        }

        [Theory]
        [InlineData("doc-fragment#LEAK", "fragment", "LEAK")]
        [InlineData("doc/path/LEAK", "path", "LEAK")]
        [InlineData("doc:LEAK", "doc:", "LEAK")]
        [InlineData(" doc-LEAK ", "doc-LEAK", "LEAK")]
        public void LoadIndex_RejectsMalformedLorePackDocumentIdWithoutEchoingId(
            string documentId,
            string firstForbiddenToken,
            string secondForbiddenToken)
        {
            WriteLorePackRows(new LorePackFixtureRow(documentId, "Start.md", "# Start"));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "invalid document identifier", firstForbiddenToken, secondForbiddenToken);
        }

        [Fact]
        public void LoadIndex_RejectsDuplicateLorePackIndexIdCaseInsensitiveWithoutEchoingId()
        {
            string content = "# One";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 2,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-trim-leak",
                            relativePath = "One.md",
                            title = "One",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        },
                        new
                        {
                            id = "DOC-TRIM-LEAK",
                            relativePath = "Two.md",
                            title = "Two",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 1
                        }
                    }
                },
                SerializeLorePackContentRow("doc-trim-leak", "One.md", content));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "duplicate document identifiers", "doc-trim-leak");
        }

        [Fact]
        public void LoadIndex_RejectsDuplicateLorePackRelativePathWithoutEchoingPathOrId()
        {
            const string duplicatePath = "safe/DuplicateLeakProbe.md";
            WriteLorePackRows(
                new LorePackFixtureRow("doc-one", duplicatePath, "# One"),
                new LorePackFixtureRow("doc-two", duplicatePath, "# Two"));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "duplicate document paths", duplicatePath, "DuplicateLeakProbe", "doc-two");
        }

        [Fact]
        public void LoadIndex_RejectsDuplicateLorePackRelativePathCaseInsensitive()
        {
            WriteLorePackRows(
                new LorePackFixtureRow("doc-one", "safe/CaseProbe.md", "# One"),
                new LorePackFixtureRow("doc-two", "safe/caseprobe.md", "# Two"));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "duplicate document paths", "CaseProbe", "caseprobe", "doc-two");
        }

        [Fact]
        public void LoadIndex_RejectsLorePackHashMismatchWithoutEchoingPath()
        {
            const string relativePath = "safe/HashLeakProbe.md";
            WriteLorePackRows(new LorePackFixtureRow("doc-hash", relativePath, "# Hash", "bad-hash"));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "hash mismatch", relativePath, "HashLeakProbe", "doc-hash");
        }

        [Fact]
        public void LoadIndex_RejectsLorePackIndexSchemaMismatchWithoutEchoingInput()
        {
            string content = "# Start";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = @"onslaught-lore-pack.v0-C:\Users\Alice",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-start",
                            relativePath = "Start.md",
                            title = "Start",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        }
                    }
                },
                SerializeLorePackContentRow("doc-start", "Start.md", content));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            Assert.Equal("Lore content pack index is invalid.", ex.Message);
        }

        [Fact]
        public void LoadIndex_RejectsLorePackIndexDocumentCountMismatch()
        {
            string content = "# Start";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 2,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-start",
                            relativePath = "Start.md",
                            title = "Start",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        }
                    }
                },
                SerializeLorePackContentRow("doc-start", "Start.md", content));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            Assert.Equal("Lore content pack index is invalid.", ex.Message);
        }

        [Fact]
        public void LoadIndex_RejectsLorePackContentRowUnknownToIndexWithoutEchoingId()
        {
            string indexedContent = "# Start";
            string indexedDigest = Sha256Text(indexedContent);
            string extraContent = "# Extra";
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-start",
                            relativePath = "Start.md",
                            title = "Start",
                            sha256 = indexedDigest,
                            byteLength = Encoding.UTF8.GetByteCount(indexedContent),
                            order = 0
                        }
                    }
                },
                SerializeLorePackContentRow("doc-unknown-leak", "Extra.md", extraContent));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "index and content do not match", "unknown-leak");
        }

        [Fact]
        public void LoadIndex_AcceptsCaseVariantLorePackContentId()
        {
            string content = "# Start";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-start",
                            relativePath = "Start.md",
                            title = "Start",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        }
                    }
                },
                SerializeLorePackContentRow("DOC-START", "Start.md", content));

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_repoRoot);
            LoreDocument document = Assert.Single(index.Documents);

            Assert.True(index.UsingContentPack);
            Assert.Equal("Start.md", document.RelativePath);
            Assert.True(service.DocumentExists("lore-pack://doc-start"));
            Assert.True(service.DocumentExists("lore-pack://DOC-START"));
        }

        [Fact]
        public void LoadIndex_RejectsLorePackIndexContentRelativePathMismatchWithoutEchoingPath()
        {
            string content = "# Start";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-start",
                            relativePath = "IndexPathLeak.md",
                            title = "Start",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        }
                    }
                },
                SerializeLorePackContentRow("doc-start", "ContentPathLeak.md", content));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "index and content do not match", "IndexPathLeak", "ContentPathLeak", "doc-start");
        }

        [Fact]
        public void LoadIndex_RejectsMissingLorePackContentRowsWithoutRetainingPreviousPack()
        {
            LoreBrowserService service = new();
            WriteLorePackRows(new LorePackFixtureRow("doc-valid", "Valid.md", "# Valid"));
            LoreIndex index = service.LoadIndex(_repoRoot);
            string validSourcePath = Assert.Single(index.Documents).FilePath;
            Assert.True(service.DocumentExists(validSourcePath));

            string content = "# Missing";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-missing-leak",
                            relativePath = "Missing.md",
                            title = "Missing",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        }
                    }
                });

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => service.LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "index and content do not match", "missing-leak");
            Assert.False(service.DocumentExists(validSourcePath));
        }

        [Fact]
        public void LoadIndex_RejectsDuplicateLorePackIndexRelativePathWithoutEchoingPathOrId()
        {
            string content = "# One";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 2,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-one",
                            relativePath = "safe/DuplicateIndexLeak.md",
                            title = "One",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        },
                        new
                        {
                            id = "doc-two-leak",
                            relativePath = "safe/duplicateindexleak.md",
                            title = "Two",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 1
                        }
                    }
                },
                SerializeLorePackContentRow("doc-one", "safe/DuplicateIndexLeak.md", content));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "duplicate document paths", "DuplicateIndexLeak", "doc-two-leak");
        }

        [Fact]
        public void LoadIndex_RejectsLorePackIndexHashMismatchWithoutEchoingHash()
        {
            string content = "# Start";
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-start",
                            relativePath = "Start.md",
                            title = "Start",
                            sha256 = "bad-hash-leak",
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        }
                    }
                },
                SerializeLorePackContentRow("doc-start", "Start.md", content));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "hash mismatch", "bad-hash-leak", "doc-start");
        }

        [Fact]
        public void LoadIndex_RejectsMalformedLorePackContentJsonWithoutEchoingPayload()
        {
            string content = "# Start";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-start",
                            relativePath = "Start.md",
                            title = "Start",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        }
                    }
                },
                "{\"id\":\"doc-start\",\"relativePath\":\"C:\\\\Users\\\\Alice\\\\Leak.md\"");

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "content is invalid", "C:", "Users", "Alice", "Leak.md");
        }

        [Fact]
        public void LoadIndex_RejectsLorePackContentRowMissingByteLengthWithoutEchoingContent()
        {
            string content = "# Byte Length Probe";
            string digest = Sha256Text(content);
            WriteLorePackFixture(
                new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = 1,
                    documents = new[]
                    {
                        new
                        {
                            id = "doc-byte-length",
                            relativePath = "ByteLength.md",
                            title = "Byte Length",
                            sha256 = digest,
                            byteLength = Encoding.UTF8.GetByteCount(content),
                            order = 0
                        }
                    }
                },
                JsonSerializer.Serialize(new
                {
                    id = "doc-byte-length",
                    relativePath = "ByteLength.md",
                    title = "Byte Length",
                    sha256 = digest,
                    content = @"C:\Users\Alice\ByteLengthLeak"
                }));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "content is invalid", "C:", "Users", "Alice", "ByteLengthLeak");
        }

        [Fact]
        public void LoadIndex_ClearsPreviousLorePackWhenNextPackFailsClosed()
        {
            LoreBrowserService service = new();
            WriteLorePackRows(new LorePackFixtureRow("doc-valid", "Valid.md", "# Valid"));
            LoreIndex index = service.LoadIndex(_repoRoot);
            string validSourcePath = Assert.Single(index.Documents).FilePath;
            Assert.True(service.DocumentExists(validSourcePath));

            const string invalidPath = "../LeakProbe.md";
            WriteLorePackRows(new LorePackFixtureRow("doc-invalid", invalidPath, "# Invalid"));
            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => service.LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "invalid document path", invalidPath, "LeakProbe", "..");
            Assert.False(service.DocumentExists(validSourcePath));
        }

        [Fact]
        public void RenderDocument_RewritesPackedInternalLinksToReaderNavigation()
        {
            CreateLoreBookSkeleton();
            WriteLorePack(
                ("Start-Here.md", "# Start\n\nSee [Deep](deep/Deep.md#anchor)."),
                ("deep/Deep.md", "# Deep\n\nPacked target."));

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_repoRoot);
            LoreDocument start = Assert.Single(index.Documents, doc => doc.RelativePath == "Start-Here.md");

            RenderedLoreDocument rendered = service.RenderDocument(start.FilePath);
            string html = File.ReadAllText(new Uri(rendered.DisplayUri).LocalPath);
            string? target = service.ResolveInternalTarget(start.FilePath, "deep/Deep.md#anchor");

            Assert.Contains("onslaught-lore://document/", html);
            Assert.NotNull(target);
            Assert.StartsWith("lore-pack://", target, StringComparison.OrdinalIgnoreCase);
            Assert.True(service.DocumentExists(target!));
        }

        [Fact]
        public void RenderDocument_RewritesPackedDotSegmentLinksToReaderNavigation()
        {
            CreateLoreBookSkeleton();
            WriteLorePack(
                ("Start-Here.md", "# Start\n\nHome document."),
                ("deep/Deep.md", "# Deep\n\nSee [Home](../Start-Here.md#top) and [Peer](./Peer.md)."),
                ("deep/Peer.md", "# Peer\n\nSibling document."));

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_repoRoot);
            LoreDocument deep = Assert.Single(index.Documents, doc => doc.RelativePath == "deep/Deep.md");

            RenderedLoreDocument rendered = service.RenderDocument(deep.FilePath);
            string html = File.ReadAllText(new Uri(rendered.DisplayUri).LocalPath);
            string? homeTarget = service.ResolveInternalTarget(deep.FilePath, "../Start-Here.md#top");
            string? peerTarget = service.ResolveInternalTarget(deep.FilePath, "./Peer.md");

            Assert.Contains("onslaught-lore://document/", html);
            Assert.NotNull(homeTarget);
            Assert.NotNull(peerTarget);
            Assert.StartsWith("lore-pack://", homeTarget!, StringComparison.OrdinalIgnoreCase);
            Assert.StartsWith("lore-pack://", peerTarget!, StringComparison.OrdinalIgnoreCase);
            Assert.True(service.DocumentExists(homeTarget!));
            Assert.True(service.DocumentExists(peerTarget!));
        }

        [Fact]
        public void RenderDocument_RewritesPackedEncodedDotSegmentLinksToReaderNavigation()
        {
            CreateLoreBookSkeleton();
            WriteLorePack(
                ("Start-Here.md", "# Start\n\nHome document."),
                ("deep/Deep.md", "# Deep\n\nSee [Home](%2e%2e/Start-Here.md#top) and [Peer](%2e/Peer.md)."),
                ("deep/Peer.md", "# Peer\n\nSibling document."));

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_repoRoot);
            LoreDocument deep = Assert.Single(index.Documents, doc => doc.RelativePath == "deep/Deep.md");

            RenderedLoreDocument rendered = service.RenderDocument(deep.FilePath);
            string html = File.ReadAllText(new Uri(rendered.DisplayUri).LocalPath);
            string? homeTarget = service.ResolveInternalTarget(deep.FilePath, "%2e%2e/Start-Here.md#top");
            string? peerTarget = service.ResolveInternalTarget(deep.FilePath, "%2e/Peer.md");

            Assert.Contains("onslaught-lore://document/", html);
            Assert.NotNull(homeTarget);
            Assert.NotNull(peerTarget);
            Assert.StartsWith("lore-pack://", homeTarget!, StringComparison.OrdinalIgnoreCase);
            Assert.StartsWith("lore-pack://", peerTarget!, StringComparison.OrdinalIgnoreCase);
            Assert.True(service.DocumentExists(homeTarget!));
            Assert.True(service.DocumentExists(peerTarget!));
        }

        [Fact]
        public void LoadIndex_RejectsPackedLinksAbovePackRootWithoutEchoingTarget()
        {
            CreateLoreBookSkeleton();
            WriteLorePack(
                ("Start-Here.md", "# Start\n\nSee [Deep](../Deep.md)."),
                ("Deep.md", "# Deep\n\nRoot document."));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "content is invalid", "../Deep.md", "Deep.md");
        }

        [Fact]
        public void LoadIndex_RejectsEncodedPackedLinksAbovePackRootWithoutEchoingTarget()
        {
            CreateLoreBookSkeleton();
            WriteLorePack(
                ("Start-Here.md", "# Start\n\nSee [Deep](%2e%2e/SecretLeakProbe.md)."),
                ("SecretLeakProbe.md", "# Secret Leak Probe\n\nRoot document."));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "content is invalid", "%2e%2e/SecretLeakProbe.md", "SecretLeakProbe");
        }

        [Fact]
        public void ResolveInternalTarget_DoesNotResolveAboveRootPackedLinksThroughRootIndexFallback()
        {
            CreateLoreBookSkeleton();
            WriteLorePack(
                ("Start-Here.md", "# Start\n\nHome document."),
                ("deep/Deep.md", "# Deep\n\nDeep document."),
                ("_index.md", "# Root Index\n\nRoot fallback document."));

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_repoRoot);
            LoreDocument deep = Assert.Single(index.Documents, doc => doc.RelativePath == "deep/Deep.md");

            string? target = service.ResolveInternalTarget(deep.FilePath, "../../_index.md");

            Assert.Null(target);
        }

        [Fact]
        public void RenderDocument_CreatesStyledHtmlOutput()
        {
            string loreBook = CreateLoreBookSkeleton();
            string markdownPath = Path.Combine(loreBook, "Start-Here.md");
            File.WriteAllText(markdownPath, """
# Start Here

See the [world](lore/world-lore.md).
""");
            Directory.CreateDirectory(Path.Combine(loreBook, "lore"));
            File.WriteAllText(Path.Combine(loreBook, "lore", "world-lore.md"), "# World Lore");

            LoreBrowserService service = new();
            RenderedLoreDocument rendered = service.RenderDocument(markdownPath);

            Assert.True(rendered.IsMarkdown);
            Assert.Contains("Start Here", rendered.Title);
            Assert.True(File.Exists(new Uri(rendered.DisplayUri).LocalPath));
            string html = File.ReadAllText(new Uri(rendered.DisplayUri).LocalPath);
            Assert.Contains("<base href=", html);
            Assert.Contains("linear-gradient", html);
            Assert.Contains("See the", html);
        }

        [Fact]
        public void RenderDocument_MarksGitHubSourceLinksAsExternalSource()
        {
            string loreBook = CreateLoreBookSkeleton();
            string markdownPath = Path.Combine(loreBook, "Start-Here.md");
            File.WriteAllText(markdownPath, """
# Start Here

See the [deep source](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/lore-book/deep/Deep.md).
""");

            LoreBrowserService service = new();
            RenderedLoreDocument rendered = service.RenderDocument(markdownPath);

            string html = File.ReadAllText(new Uri(rendered.DisplayUri).LocalPath);
            Assert.Contains("class=\"source-link\"", html);
            Assert.Contains("Source link; opens GitHub in your browser", html);
            Assert.Contains("<span class=\"source-link-badge\" aria-hidden=\"true\">Source</span>", html);
        }

        [Fact]
        public void RenderDocument_MarksExternalLinksAsBrowserLinks()
        {
            string loreBook = CreateLoreBookSkeleton();
            string markdownPath = Path.Combine(loreBook, "Start-Here.md");
            File.WriteAllText(markdownPath, """
# Start Here

See the [reference](https://example.com/reference).
""");

            LoreBrowserService service = new();
            RenderedLoreDocument rendered = service.RenderDocument(markdownPath);

            string html = File.ReadAllText(new Uri(rendered.DisplayUri).LocalPath);
            Assert.Contains("class=\"external-link\"", html);
            Assert.Contains("External link; opens in your browser", html);
            Assert.Contains("<span class=\"source-link-badge\" aria-hidden=\"true\">External</span>", html);
        }

        [Fact]
        public void ResolveInternalTarget_HandlesRelativeMarkdownAndDirectories()
        {
            string loreBook = CreateLoreBookSkeleton();
            string startHere = Path.Combine(loreBook, "Start-Here.md");
            File.WriteAllText(startHere, "# Start Here");
            Directory.CreateDirectory(Path.Combine(loreBook, "lore"));
            File.WriteAllText(Path.Combine(loreBook, "lore", "_index.md"), "# Lore Index");
            File.WriteAllText(Path.Combine(loreBook, "lore", "world-lore.md"), "# World Lore");

            LoreBrowserService service = new();

            Assert.Equal(
                Path.Combine(loreBook, "lore", "world-lore.md"),
                service.ResolveInternalTarget(startHere, "lore/world-lore.md"));
            Assert.Equal(
                Path.Combine(loreBook, "lore", "_index.md"),
                service.ResolveInternalTarget(startHere, "lore"));
            Assert.Equal(
                Path.Combine(loreBook, "lore", "world-lore.md"),
                service.ResolveInternalTarget(
                    startHere,
                    new Uri(Path.Combine(loreBook, "lore", "world-lore.md")).AbsoluteUri));
        }

        private string CreateLoreBookSkeleton()
        {
            string loreBook = Path.Combine(_repoRoot, "lore-book");
            Directory.CreateDirectory(loreBook);
            return loreBook;
        }

        private void WriteLorePack(params (string RelativePath, string Content)[] documents)
        {
            string packDirectory = Path.Combine(_repoRoot, "lore-pack");
            Directory.CreateDirectory(packDirectory);
            var indexRows = documents.Select((doc, index) =>
            {
                string id = $"doc-{index + 1:000000}";
                string sha256 = Sha256Text(doc.Content);
                return new
                {
                    id,
                    relativePath = doc.RelativePath,
                    title = ResolveTitle(doc.Content, doc.RelativePath),
                    sha256,
                    byteLength = Encoding.UTF8.GetByteCount(doc.Content),
                    order = index
                };
            }).ToArray();
            var contentRows = documents.Select((doc, index) =>
            {
                string id = $"doc-{index + 1:000000}";
                return JsonSerializer.Serialize(new
                {
                    id,
                    relativePath = doc.RelativePath,
                    title = ResolveTitle(doc.Content, doc.RelativePath),
                    sha256 = Sha256Text(doc.Content),
                    byteLength = Encoding.UTF8.GetByteCount(doc.Content),
                    content = doc.Content
                });
            });
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.index.json"),
                JsonSerializer.Serialize(new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = documents.Length,
                    documents = indexRows
                }),
                Encoding.UTF8);
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.jsonl"),
                string.Join(Environment.NewLine, contentRows) + Environment.NewLine,
                Encoding.UTF8);
        }

        private void WriteLorePackRows(params LorePackFixtureRow[] documents)
        {
            string packDirectory = Path.Combine(_repoRoot, "lore-pack");
            Directory.CreateDirectory(packDirectory);
            var indexRows = documents.Select((doc, index) =>
            {
                string sha256 = doc.Sha256Override ?? Sha256Text(doc.Content);
                return new
                {
                    id = doc.Id,
                    relativePath = doc.RelativePath,
                    title = ResolveTitle(doc.Content, doc.RelativePath),
                    sha256,
                    byteLength = Encoding.UTF8.GetByteCount(doc.Content),
                    order = index
                };
            }).ToArray();
            var contentRows = documents.Select(doc =>
            {
                string sha256 = doc.Sha256Override ?? Sha256Text(doc.Content);
                return JsonSerializer.Serialize(new
                {
                    id = doc.Id,
                    relativePath = doc.RelativePath,
                    title = ResolveTitle(doc.Content, doc.RelativePath),
                    sha256,
                    byteLength = Encoding.UTF8.GetByteCount(doc.Content),
                    content = doc.Content
                });
            });
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.index.json"),
                JsonSerializer.Serialize(new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = documents.Length,
                    documents = indexRows
                }),
                Encoding.UTF8);
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.jsonl"),
                string.Join(Environment.NewLine, contentRows) + Environment.NewLine,
                Encoding.UTF8);
        }

        private void WriteLorePackFixture(object index, params string[] contentLines)
        {
            string packDirectory = Path.Combine(_repoRoot, "lore-pack");
            Directory.CreateDirectory(packDirectory);
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.index.json"),
                JsonSerializer.Serialize(index),
                Encoding.UTF8);
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.jsonl"),
                contentLines.Length == 0
                    ? string.Empty
                    : string.Join(Environment.NewLine, contentLines) + Environment.NewLine,
                Encoding.UTF8);
        }

        private static string SerializeLorePackContentRow(string id, string relativePath, string content)
        {
            return JsonSerializer.Serialize(new
            {
                id,
                relativePath,
                title = ResolveTitle(content, relativePath),
                sha256 = Sha256Text(content),
                byteLength = Encoding.UTF8.GetByteCount(content),
                content
            });
        }

        private static void AssertSafeLorePackException(InvalidDataException ex, string expectedFragment, params string[] forbiddenTokens)
        {
            Assert.Contains(expectedFragment, ex.Message, StringComparison.OrdinalIgnoreCase);
            foreach (string token in forbiddenTokens.Where(static value => !string.IsNullOrWhiteSpace(value)))
            {
                Assert.DoesNotContain(token, ex.Message, StringComparison.OrdinalIgnoreCase);
            }
        }

        private static string Sha256Text(string value)
        {
            return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
        }

        private static string ResolveTitle(string content, string relativePath)
        {
            string? heading = content.Split('\n')
                .Select(static line => line.Trim())
                .FirstOrDefault(static line => line.StartsWith("# ", StringComparison.Ordinal));
            return heading == null
                ? Path.GetFileNameWithoutExtension(relativePath)
                : heading.TrimStart('#', ' ');
        }

        private sealed record LorePackFixtureRow(string Id, string RelativePath, string Content, string? Sha256Override = null);

        public void Dispose()
        {
            if (Directory.Exists(_tempRoot))
            {
                Directory.Delete(_tempRoot, recursive: true);
            }
        }
    }
}
