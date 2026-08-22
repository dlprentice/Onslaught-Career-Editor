using System;
using System.IO;
using System.Linq;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Lore depth services: whole-word full-text search with snippets, and the
    /// "what links here" cross-link index, both over the same loader the reader uses.
    /// </summary>
    public sealed class LoreSearchServiceTests : IDisposable
    {
        private readonly string _tempRoot;
        private readonly LoreBrowserService _browser = new();

        public LoreSearchServiceTests()
        {
            _tempRoot = Path.Combine(Path.GetTempPath(), "OnslaughtCareerEditorTests", Guid.NewGuid().ToString("N"));
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

        private LoreIndex LoadIndex()
        {
            return _browser.LoadIndex(_tempRoot);
        }

        private void WriteLore(params (string Name, string Content)[] files)
        {
            string lore = Path.Combine(_tempRoot, "lore");
            Directory.CreateDirectory(lore);
            File.WriteAllText(Path.Combine(lore, "_index.md"), "# Lore Index");
            foreach ((string name, string content) in files)
            {
                File.WriteAllText(Path.Combine(lore, name), content);
            }
        }

        [Fact]
        public void Search_FindsWholeWordsOnly_WithSnippetsAndCounts()
        {
            WriteLore(
                ("world-lore.md", "# World Lore\n\nThe Aquila is a battle engine. AQUILA flies. Aquiline wings are unrelated."),
                ("characters.md", "# Characters\n\nAquila is the pilot."));

            LoreSearchService service = new(_browser);
            var hits = service.SearchAllDocuments(LoadIndex(), "Aquila");

            // "Aquila" (case-insensitive, whole word) appears twice in World Lore and
            // once in Characters; "Aquiline" must never match.
            Assert.Equal(3, hits.Count);
            Assert.All(hits, hit => Assert.Equal("Aquila", hit.MatchedText, ignoreCase: true));

            var worldHits = hits.Where(hit => hit.DocumentTitle == "World Lore").ToArray();
            Assert.Equal(2, worldHits.Length);
            Assert.All(worldHits, hit => Assert.Equal(2, hit.OccurrenceCount));
            // The flattened text carries the document heading ahead of the paragraph,
            // so the first hit's leading snippet names that heading.
            Assert.Contains("World Lore", worldHits[0].SnippetBefore, StringComparison.Ordinal);
            Assert.Contains("battle engine", worldHits[0].SnippetAfter, StringComparison.Ordinal);

            LoreSearchHit characters = Assert.Single(hits, hit => hit.DocumentTitle == "Characters");
            Assert.Contains("pilot", characters.SnippetAfter, StringComparison.Ordinal);
        }

        [Fact]
        public void Search_EmptyQueryAndMissingWordsReturnNothing()
        {
            WriteLore(("world-lore.md", "# World Lore\n\nPlain text."));

            LoreSearchService service = new(_browser);
            Assert.Empty(service.SearchAllDocuments(LoadIndex(), ""));
            Assert.Empty(service.SearchAllDocuments(LoadIndex(), null));
            Assert.Empty(service.SearchAllDocuments(LoadIndex(), "not-present-anywhere"));
        }

        [Fact]
        public void Search_CoversOnlyIndexedDocuments()
        {
            WriteLore(("world-lore.md", "# World Lore\n\nThe Aquila waits."));

            LoreIndex index = LoadIndex();
            Assert.True(index.Documents.Count >= 1);

            LoreSearchService service = new(_browser);
            var hits = service.SearchAllDocuments(index, "Aquila");

            // Every hit resolves back to a real indexed document path.
            var indexedPaths = index.Documents.Select(document => _browser.NormalizeDocumentKey(document.FilePath)).ToHashSet(StringComparer.OrdinalIgnoreCase);
            Assert.NotEmpty(hits);
            Assert.All(hits, hit =>
                Assert.Contains(_browser.NormalizeDocumentKey(hit.DocumentPath), indexedPaths));

            // And a second search over the same index is stable (no hidden state).
            var again = service.SearchAllDocuments(index, "Aquila");
            Assert.Equal(hits.Count, again.Count);
        }

        [Fact]
        public void Backlinks_IndexInternalLinksAndAnchors()
        {
            WriteLore(
                ("world-lore.md", "# World Lore\n\nSee [characters](characters.md) and [the pilot](characters.md#chuck)."),
                ("characters.md", "# Characters\n\nBack to [world](world-lore.md)."));

            LoreSearchService service = new(_browser);
            LoreBacklinkIndex index = service.BuildBacklinkIndex(LoadIndex());

            string charactersPath = Path.Combine(_tempRoot, "lore", "characters.md");
            var backlinks = service.GetBacklinks(index, charactersPath);

            LoreBacklink fromWorld = Assert.Single(backlinks);
            Assert.Equal("World Lore", fromWorld.SourceDocumentTitle);
            Assert.Equal(2, fromWorld.AnchorTargets.Count);
            Assert.Contains("", fromWorld.AnchorTargets);
            Assert.Contains("chuck", fromWorld.AnchorTargets);

            // The world document has one backlink from characters.
            var worldBacklinks = service.GetBacklinks(index, Path.Combine(_tempRoot, "lore", "world-lore.md"));
            LoreBacklink fromCharacters = Assert.Single(worldBacklinks);
            Assert.Equal("Characters", fromCharacters.SourceDocumentTitle);
        }

        [Fact]
        public void Backlinks_IgnoreExternalLinksAndSelfAnchors()
        {
            WriteLore(
                ("world-lore.md", "# World Lore\n\n[GitHub](https://example.com) and [same page](#section) stay out."),
                ("characters.md", "# Characters"));

            LoreSearchService service = new(_browser);
            LoreBacklinkIndex index = service.BuildBacklinkIndex(LoadIndex());

            Assert.Empty(service.GetBacklinks(index, Path.Combine(_tempRoot, "lore", "characters.md")));
        }

        [Fact]
        public void Backlinks_ForUnlinkedDocumentAreEmpty()
        {
            WriteLore(("world-lore.md", "# World Lore"), ("characters.md", "# Characters"));

            LoreSearchService service = new(_browser);
            LoreBacklinkIndex index = service.BuildBacklinkIndex(LoadIndex());

            Assert.Empty(service.GetBacklinks(index, Path.Combine(_tempRoot, "lore", "world-lore.md")));
            Assert.Empty(service.GetBacklinks(index, null));
            Assert.Empty(service.GetBacklinks(null, "anything"));
        }
    }
}
