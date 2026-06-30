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
            const string maliciousId = @"C:\Users\Alice\duplicate-id";
            WriteLorePackRows(
                new LorePackFixtureRow(maliciousId, "One.md", "# One"),
                new LorePackFixtureRow(maliciousId, "Two.md", "# Two"));

            InvalidDataException ex = Assert.Throws<InvalidDataException>(() => new LoreBrowserService().LoadIndex(_repoRoot));

            AssertSafeLorePackException(ex, "duplicate document identifiers", maliciousId, "C:", "Users", "duplicate-id");
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
