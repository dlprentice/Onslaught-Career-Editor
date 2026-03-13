using Onslaught___Career_Editor;
using System;
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

        public void Dispose()
        {
            if (Directory.Exists(_tempRoot))
            {
                Directory.Delete(_tempRoot, recursive: true);
            }
        }
    }
}
