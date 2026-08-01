using Onslaught___Career_Editor;
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Writes a minimal valid lore content pack so reader-model tests can exercise
    /// the packed document path without depending on the shipped pack.
    /// </summary>
    internal static class LorePackFixture
    {
        public static void Write(string packDirectory, params (string RelativePath, string Title, string Content)[] documents)
        {
            Directory.CreateDirectory(packDirectory);

            var rows = documents.Select((doc, index) => new
            {
                id = $"doc-{index:D6}",
                relativePath = doc.RelativePath,
                title = doc.Title,
                sha256 = Sha256Text(doc.Content),
                byteLength = Encoding.UTF8.GetByteCount(doc.Content),
                order = index,
                content = doc.Content
            }).ToArray();

            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.index.json"),
                JsonSerializer.Serialize(new
                {
                    schema = "onslaught-lore-pack.v1",
                    sourceRoot = "lore-book",
                    documentCount = rows.Length,
                    documents = rows.Select(row => new
                    {
                        row.id,
                        row.relativePath,
                        row.title,
                        row.sha256,
                        row.byteLength,
                        row.order
                    })
                }),
                Encoding.UTF8);

            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.jsonl"),
                string.Join(Environment.NewLine, rows.Select(row => JsonSerializer.Serialize(new
                {
                    row.id,
                    row.relativePath,
                    row.title,
                    row.sha256,
                    row.byteLength,
                    row.content
                }))) + Environment.NewLine,
                Encoding.UTF8);
        }

        private static string Sha256Text(string value)
        {
            return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
        }
    }

    /// <summary>
    /// Structure tests for the native Lore reader's document model. The reader no
    /// longer renders HTML, so these assertions are the contract between markdown
    /// on disk and the controls the user actually sees.
    /// </summary>
    public sealed class LoreDocumentParserTests : IDisposable
    {
        private readonly string _tempRoot;

        public LoreDocumentParserTests()
        {
            _tempRoot = Path.Combine(
                Path.GetTempPath(),
                "OnslaughtCareerEditorTests",
                Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(_tempRoot);
        }

        [Fact]
        public void Parse_HeadingsKeepLevelTextAndAnchorIdentifier()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("""
# Start Here

## The Battle Engine

### Walker Frames
""");

            LoreHeadingBlock[] headings = document.Blocks.OfType<LoreHeadingBlock>().ToArray();

            Assert.Equal(3, headings.Length);
            Assert.Equal(1, headings[0].Level);
            Assert.Equal("Start Here", headings[0].Text);
            Assert.Equal("start-here", headings[0].Id);
            Assert.Equal(2, headings[1].Level);
            Assert.Equal("the-battle-engine", headings[1].Id);
            Assert.Equal(3, headings[2].Level);
            Assert.Equal("walker-frames", headings[2].Id);
        }

        [Fact]
        public void Parse_UsesFirstHeadingAsTitleWhenNoTitleIsSupplied()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("# Aquila\n\nBody text.");

            Assert.Equal("Aquila", document.Title);
        }

        [Fact]
        public void Parse_PrefersTheCallerSuppliedTitle()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("# Aquila\n\nBody.", "Library title");

            Assert.Equal("Library title", document.Title);
        }

        [Fact]
        public void Parse_ParagraphKeepsBoldItalicAndCodeRuns()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("Plain **bold** then *italic* then `code`.");

            LoreParagraphBlock paragraph = Assert.IsType<LoreParagraphBlock>(Assert.Single(document.Blocks));

            Assert.Collection(
                paragraph.Inlines,
                inline => Assert.Equal("Plain ", Assert.IsType<LoreTextInline>(inline).Text),
                inline => Assert.Equal("bold", LoreInlineText.Flatten(Assert.IsType<LoreBoldInline>(inline).Inlines)),
                inline => Assert.Equal(" then ", Assert.IsType<LoreTextInline>(inline).Text),
                inline => Assert.Equal("italic", LoreInlineText.Flatten(Assert.IsType<LoreItalicInline>(inline).Inlines)),
                inline => Assert.Equal(" then ", Assert.IsType<LoreTextInline>(inline).Text),
                inline => Assert.Equal("code", Assert.IsType<LoreCodeInline>(inline).Text),
                inline => Assert.Equal(".", Assert.IsType<LoreTextInline>(inline).Text));
        }

        [Fact]
        public void Parse_HardLineBreakBecomesALineBreakInline()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("first line  \nsecond line");

            LoreParagraphBlock paragraph = Assert.IsType<LoreParagraphBlock>(Assert.Single(document.Blocks));

            Assert.Collection(
                paragraph.Inlines,
                inline => Assert.Equal("first line", Assert.IsType<LoreTextInline>(inline).Text),
                inline => Assert.IsType<LoreLineBreakInline>(inline),
                inline => Assert.Equal("second line", Assert.IsType<LoreTextInline>(inline).Text));
        }

        [Fact]
        public void Parse_NestedBulletListsKeepTheirStructure()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("""
- Alpha
  - Beta
- Gamma
""");

            LoreListBlock list = Assert.IsType<LoreListBlock>(Assert.Single(document.Blocks));

            Assert.False(list.IsOrdered);
            Assert.Equal(2, list.Items.Count);

            LoreParagraphBlock alpha = Assert.IsType<LoreParagraphBlock>(list.Items[0].Blocks[0]);
            Assert.Equal("Alpha", alpha.Text);

            LoreListBlock nested = Assert.IsType<LoreListBlock>(list.Items[0].Blocks[1]);
            LoreParagraphBlock beta = Assert.IsType<LoreParagraphBlock>(Assert.Single(nested.Items).Blocks[0]);
            Assert.Equal("Beta", beta.Text);

            LoreParagraphBlock gamma = Assert.IsType<LoreParagraphBlock>(list.Items[1].Blocks[0]);
            Assert.Equal("Gamma", gamma.Text);
        }

        [Fact]
        public void Parse_NumberedListsKeepTheirStartNumber()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("""
3. Third
4. Fourth
""");

            LoreListBlock list = Assert.IsType<LoreListBlock>(Assert.Single(document.Blocks));

            Assert.True(list.IsOrdered);
            Assert.Equal(3, list.StartNumber);
            Assert.Equal(2, list.Items.Count);
        }

        [Fact]
        public void Parse_PipeTableSplitsHeadersFromRows()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("""
| Frame | Role |
| --- | --- |
| Aquila | Walker |
| Corvus | Flyer |
""");

            LoreTableBlock table = Assert.IsType<LoreTableBlock>(Assert.Single(document.Blocks));

            Assert.Equal(new[] { "Frame", "Role" }, table.Headers.Select(cell => cell.Text));
            Assert.Equal(2, table.Rows.Count);
            Assert.Equal(new[] { "Aquila", "Walker" }, table.Rows[0].Select(cell => cell.Text));
            Assert.Equal(new[] { "Corvus", "Flyer" }, table.Rows[1].Select(cell => cell.Text));
        }

        [Fact]
        public void Parse_FencedCodeBlockKeepsTextAndLanguage()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("""
```csharp
var frame = 20;
var tick = 1;
```
""");

            LoreCodeBlock code = Assert.IsType<LoreCodeBlock>(Assert.Single(document.Blocks));

            Assert.Equal("csharp", code.Language);
            Assert.Equal("var frame = 20;\nvar tick = 1;", code.Text);
        }

        [Fact]
        public void Parse_IndentedCodeBlockHasNoLanguage()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("    plain indented code");

            LoreCodeBlock code = Assert.IsType<LoreCodeBlock>(Assert.Single(document.Blocks));

            Assert.Null(code.Language);
            Assert.Equal("plain indented code", code.Text);
        }

        [Fact]
        public void Parse_BlockQuotesKeepTheirInnerBlocks()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("> Quoted **line**.");

            LoreQuoteBlock quote = Assert.IsType<LoreQuoteBlock>(Assert.Single(document.Blocks));
            LoreParagraphBlock paragraph = Assert.IsType<LoreParagraphBlock>(Assert.Single(quote.Blocks));

            Assert.Equal("Quoted line.", paragraph.Text);
            Assert.Contains(paragraph.Inlines, inline => inline is LoreBoldInline);
        }

        [Fact]
        public void Parse_ThematicBreakBecomesItsOwnBlock()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("Above\n\n---\n\nBelow");

            Assert.Collection(
                document.Blocks,
                block => Assert.Equal("Above", Assert.IsType<LoreParagraphBlock>(block).Text),
                block => Assert.IsType<LoreThematicBreakBlock>(block),
                block => Assert.Equal("Below", Assert.IsType<LoreParagraphBlock>(block).Text));
        }

        [Fact]
        public void Parse_StandaloneImageBecomesAnImageBlock()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("![Aquila walker](images/aquila.png)");

            LoreImageBlock image = Assert.IsType<LoreImageBlock>(Assert.Single(document.Blocks));

            Assert.Equal("images/aquila.png", image.Uri);
            Assert.Equal("Aquila walker", image.Alt);
        }

        [Fact]
        public void Parse_LinksCarryTheirRawTargetAndClassification()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse(
                "See [World](lore/world.md), [Top](#start-here), " +
                "[Repo](https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/README.MD), " +
                "and [Docs](https://example.com/manual).");

            LoreParagraphBlock paragraph = Assert.IsType<LoreParagraphBlock>(Assert.Single(document.Blocks));
            LoreLinkInline[] links = paragraph.Inlines.OfType<LoreLinkInline>().ToArray();

            Assert.Equal(4, links.Length);

            Assert.Equal("World", links[0].Text);
            Assert.Equal("lore/world.md", links[0].Target);
            Assert.Equal(LoreLinkKind.Internal, links[0].Kind);

            Assert.Equal("#start-here", links[1].Target);
            Assert.Equal(LoreLinkKind.Anchor, links[1].Kind);

            Assert.Equal(LoreLinkKind.Source, links[2].Kind);
            Assert.Equal(LoreLinkKind.External, links[3].Kind);
        }

        [Fact]
        public void Parse_LinkTextKeepsItsInlineFormatting()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("Read [**the** guide](guide.md).");

            LoreParagraphBlock paragraph = Assert.IsType<LoreParagraphBlock>(Assert.Single(document.Blocks));
            LoreLinkInline link = Assert.Single(paragraph.Inlines.OfType<LoreLinkInline>());

            Assert.Equal("the guide", link.Text);
            Assert.IsType<LoreBoldInline>(link.Inlines[0]);
        }

        [Fact]
        public void Parse_AutolinksBecomeExternalLinks()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse("Contact <https://example.com/support>.");

            LoreParagraphBlock paragraph = Assert.IsType<LoreParagraphBlock>(Assert.Single(document.Blocks));
            LoreLinkInline link = Assert.Single(paragraph.Inlines.OfType<LoreLinkInline>());

            Assert.Equal("https://example.com/support", link.Target);
            Assert.Equal(LoreLinkKind.External, link.Kind);
        }

        [Fact]
        public void Parse_EmptyMarkdownProducesAnEmptyDocument()
        {
            LoreDocumentModel document = LoreDocumentParser.Parse(string.Empty, "Nothing");

            Assert.Equal("Nothing", document.Title);
            Assert.Empty(document.Blocks);
        }

        [Theory]
        [InlineData("mailto:someone@example.com", LoreLinkKind.External)]
        [InlineData("http://example.com/page", LoreLinkKind.External)]
        [InlineData("https://github.com/dlprentice/Onslaught-Career-Editor/issues", LoreLinkKind.Source)]
        [InlineData("https://github.com/someone-else/other-project", LoreLinkKind.External)]
        [InlineData("onslaught-lore://document/doc-000004", LoreLinkKind.Internal)]
        [InlineData("lore/world.md", LoreLinkKind.Internal)]
        [InlineData("#heading", LoreLinkKind.Anchor)]
        [InlineData("", LoreLinkKind.Internal)]
        public void ClassifyLink_SeparatesInternalAnchorExternalAndSourceTargets(string target, LoreLinkKind expected)
        {
            Assert.Equal(expected, LoreDocumentParser.ClassifyLink(target));
        }

        [Fact]
        public void Slugify_MatchesTheAnchorShapeMarkdownLinksUse()
        {
            Assert.Equal("the-battle-engine", LoreDocumentParser.Slugify("The Battle Engine"));
            Assert.Equal("aquila-mk-ii", LoreDocumentParser.Slugify("  Aquila: Mk. II  "));
            Assert.Equal(string.Empty, LoreDocumentParser.Slugify("   "));
        }

        [Fact]
        public void LoadDocumentContent_ReturnsAParsedModelForFileBackedMarkdown()
        {
            string loreDirectory = Path.Combine(_tempRoot, "lore");
            Directory.CreateDirectory(loreDirectory);
            File.WriteAllText(Path.Combine(loreDirectory, "_index.md"), """
# Lore Index

Body paragraph with a [link](world.md).
""");
            File.WriteAllText(Path.Combine(loreDirectory, "world.md"), "# World\n\nWorld body.");

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_tempRoot);
            LoreDocument home = Assert.IsType<LoreDocument>(index.HomeDocument);

            LoreDocumentContent content = service.LoadDocumentContent(home.FilePath);

            Assert.True(content.IsMarkdown);
            Assert.Equal("Lore Index", content.Title);
            Assert.Equal("Lore Index", Assert.IsType<LoreHeadingBlock>(content.Document.Blocks[0]).Text);
            LoreParagraphBlock body = Assert.IsType<LoreParagraphBlock>(content.Document.Blocks[1]);
            Assert.Single(body.Inlines.OfType<LoreLinkInline>());
        }

        [Fact]
        public void LoadDocumentContent_RewritesPackedLinksToReaderNavigationTargets()
        {
            string packDirectory = Path.Combine(_tempRoot, "lore-pack");
            Directory.CreateDirectory(packDirectory);
            LorePackFixture.Write(
                packDirectory,
                ("Start-Here.md", "Start Here", "# Start Here\n\nGo to [Deep](deep/Deep.md#detail)."),
                ("deep/Deep.md", "Deep", "# Deep\n\n## Detail\n\nDeep body."));

            LoreBrowserService service = new();
            LoreIndex index = service.LoadIndex(_tempRoot);
            LoreDocument start = Assert.Single(index.Documents, doc => doc.RelativePath == "Start-Here.md");

            LoreDocumentContent content = service.LoadDocumentContent(start.FilePath);
            LoreParagraphBlock paragraph = Assert.IsType<LoreParagraphBlock>(content.Document.Blocks[1]);
            LoreLinkInline link = Assert.Single(paragraph.Inlines.OfType<LoreLinkInline>());

            Assert.StartsWith("onslaught-lore://document/", link.Target, StringComparison.Ordinal);
            Assert.EndsWith("#detail", link.Target, StringComparison.Ordinal);
            Assert.Equal(LoreLinkKind.Internal, link.Kind);

            string? resolved = service.ResolveInternalTarget(start.FilePath, link.Target);
            Assert.NotNull(resolved);
            Assert.True(service.DocumentExists(resolved!));
        }

        [Fact]
        public void LoadDocumentContent_FlagsStoredHtmlAsNotNativelyRenderable()
        {
            string loreDirectory = Path.Combine(_tempRoot, "lore");
            Directory.CreateDirectory(loreDirectory);
            File.WriteAllText(Path.Combine(loreDirectory, "_index.md"), "# Index");
            string htmlPath = Path.Combine(loreDirectory, "legacy.html");
            File.WriteAllText(htmlPath, "<html><body>legacy</body></html>");

            LoreBrowserService service = new();
            service.LoadIndex(_tempRoot);

            LoreDocumentContent content = service.LoadDocumentContent(htmlPath);

            Assert.False(content.IsMarkdown);
            Assert.Equal("legacy", content.Title);
            LoreParagraphBlock paragraph = Assert.IsType<LoreParagraphBlock>(Assert.Single(content.Document.Blocks));
            Assert.Contains("Open in browser", paragraph.Text, StringComparison.Ordinal);
        }

        public void Dispose()
        {
            try
            {
                if (Directory.Exists(_tempRoot))
                {
                    Directory.Delete(_tempRoot, recursive: true);
                }
            }
            catch (IOException)
            {
            }
            catch (UnauthorizedAccessException)
            {
            }
        }
    }
}
