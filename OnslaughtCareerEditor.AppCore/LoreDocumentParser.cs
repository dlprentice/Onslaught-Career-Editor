using Markdig;
using Markdig.Extensions.Tables;
using Markdig.Extensions.TaskLists;
using Markdig.Renderers.Html;
using Markdig.Syntax;
using Markdig.Syntax.Inlines;
using System.Text;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// Turns markdown into a <see cref="LoreDocumentModel"/> by walking Markdig's
    /// syntax tree. This is the reader's only content path: no HTML is produced
    /// and no presentation type is referenced, so the result can be rendered with
    /// native controls and asserted directly in tests.
    /// </summary>
    public static class LoreDocumentParser
    {
        private const string ProjectSourceHost = "github.com";
        private const string ProjectSourcePathPrefix = "/dlprentice/Onslaught-Career-Editor/";

        private static readonly MarkdownPipeline DefaultPipeline = new MarkdownPipelineBuilder()
            .UseAdvancedExtensions()
            .Build();

        /// <summary>Parses markdown into the reader model.</summary>
        public static LoreDocumentModel Parse(string? markdown, string? title = null)
        {
            return Parse(markdown, title, DefaultPipeline);
        }

        /// <summary>
        /// Parses markdown with a caller-supplied pipeline so the reader and the
        /// "open in browser" HTML path stay on identical extension settings
        /// (heading identifiers in particular).
        /// </summary>
        public static LoreDocumentModel Parse(string? markdown, string? title, MarkdownPipeline pipeline)
        {
            ArgumentNullException.ThrowIfNull(pipeline);

            string source = markdown ?? string.Empty;
            MarkdownDocument document = Markdown.Parse(source, pipeline);
            List<LoreBlock> blocks = ConvertBlocks(document);
            string resolvedTitle = string.IsNullOrWhiteSpace(title)
                ? ResolveTitle(blocks)
                : title!;

            return new LoreDocumentModel(resolvedTitle, blocks);
        }

        /// <summary>
        /// Classifies a raw markdown link target. Kept public because the reader
        /// chrome needs the same source/external boundary the renderer paints.
        /// </summary>
        public static LoreLinkKind ClassifyLink(string? target)
        {
            if (string.IsNullOrWhiteSpace(target))
            {
                return LoreLinkKind.Internal;
            }

            string trimmed = target.Trim();
            if (trimmed.StartsWith("#", StringComparison.Ordinal))
            {
                return LoreLinkKind.Anchor;
            }

            if (!Uri.TryCreate(trimmed, UriKind.Absolute, out Uri? uri))
            {
                return LoreLinkKind.Internal;
            }

            if (uri.Scheme.Equals("mailto", StringComparison.OrdinalIgnoreCase))
            {
                return LoreLinkKind.External;
            }

            if (!uri.Scheme.Equals("http", StringComparison.OrdinalIgnoreCase) &&
                !uri.Scheme.Equals("https", StringComparison.OrdinalIgnoreCase))
            {
                return LoreLinkKind.Internal;
            }

            return uri.Host.Equals(ProjectSourceHost, StringComparison.OrdinalIgnoreCase) &&
                   uri.AbsolutePath.StartsWith(ProjectSourcePathPrefix, StringComparison.OrdinalIgnoreCase)
                ? LoreLinkKind.Source
                : LoreLinkKind.External;
        }

        /// <summary>
        /// Produces the anchor identifier Markdig's auto-identifier extension
        /// would emit for a heading. Used only when the parsed heading carries no
        /// identifier of its own.
        /// </summary>
        public static string Slugify(string? value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return string.Empty;
            }

            StringBuilder builder = new(value.Length);
            bool pendingSeparator = false;
            foreach (char character in value)
            {
                if (char.IsLetterOrDigit(character))
                {
                    if (pendingSeparator && builder.Length > 0)
                    {
                        builder.Append('-');
                    }

                    pendingSeparator = false;
                    builder.Append(char.ToLowerInvariant(character));
                    continue;
                }

                pendingSeparator = true;
            }

            return builder.ToString();
        }

        private static string ResolveTitle(IReadOnlyList<LoreBlock> blocks)
        {
            foreach (LoreBlock block in blocks)
            {
                if (block is LoreHeadingBlock heading && !string.IsNullOrWhiteSpace(heading.Text))
                {
                    return heading.Text;
                }
            }

            return string.Empty;
        }

        private static List<LoreBlock> ConvertBlocks(ContainerBlock container)
        {
            List<LoreBlock> blocks = new();
            foreach (Block child in container)
            {
                AppendBlock(blocks, child);
            }

            return blocks;
        }

        private static void AppendBlock(List<LoreBlock> target, Block block)
        {
            switch (block)
            {
                case HeadingBlock heading:
                {
                    List<LoreInline> inlines = ConvertInlines(heading.Inline);
                    target.Add(new LoreHeadingBlock(
                        Math.Clamp(heading.Level, 1, 6),
                        inlines,
                        ResolveHeadingId(heading, inlines)));
                    break;
                }

                case ParagraphBlock paragraph:
                    AppendParagraph(target, paragraph);
                    break;

                case ThematicBreakBlock:
                    target.Add(new LoreThematicBreakBlock());
                    break;

                case FencedCodeBlock fenced:
                    target.Add(new LoreCodeBlock(
                        ReadCodeText(fenced),
                        string.IsNullOrWhiteSpace(fenced.Info) ? null : fenced.Info!.Trim()));
                    break;

                case CodeBlock code:
                    target.Add(new LoreCodeBlock(ReadCodeText(code), null));
                    break;

                case QuoteBlock quote:
                    target.Add(new LoreQuoteBlock(ConvertBlocks(quote)));
                    break;

                case Table table:
                    target.Add(ConvertTable(table));
                    break;

                case ListBlock list:
                    target.Add(ConvertList(list));
                    break;

                case HtmlBlock html:
                {
                    string text = StripHtmlTags(ReadCodeText(html));
                    if (!string.IsNullOrWhiteSpace(text))
                    {
                        target.Add(new LoreParagraphBlock(new LoreInline[] { new LoreTextInline(text.Trim()) }));
                    }

                    break;
                }

                case ContainerBlock container:
                    // Footnote groups, custom containers, figures, and link
                    // reference definitions all arrive as containers; their
                    // children are ordinary blocks.
                    foreach (Block child in container)
                    {
                        AppendBlock(target, child);
                    }

                    break;

                case LeafBlock leaf when leaf.Inline is not null:
                {
                    List<LoreInline> inlines = ConvertInlines(leaf.Inline);
                    if (inlines.Count > 0)
                    {
                        target.Add(new LoreParagraphBlock(inlines));
                    }

                    break;
                }
            }
        }

        private static void AppendParagraph(List<LoreBlock> target, ParagraphBlock paragraph)
        {
            if (TryGetStandaloneImage(paragraph, out LinkInline? image))
            {
                target.Add(new LoreImageBlock(
                    ResolveUrl(image!),
                    LoreInlineText.Flatten(ConvertInlines(image!))));
                return;
            }

            List<LoreInline> inlines = ConvertInlines(paragraph.Inline);
            if (inlines.Count > 0)
            {
                target.Add(new LoreParagraphBlock(inlines));
            }
        }

        private static bool TryGetStandaloneImage(ParagraphBlock paragraph, out LinkInline? image)
        {
            image = null;
            if (paragraph.Inline is null)
            {
                return false;
            }

            foreach (Inline inline in paragraph.Inline)
            {
                if (inline is LiteralInline literal && literal.Content.ToString().Trim().Length == 0)
                {
                    continue;
                }

                if (inline is LinkInline { IsImage: true } candidate && image is null)
                {
                    image = candidate;
                    continue;
                }

                image = null;
                return false;
            }

            return image is not null;
        }

        private static LoreBlock ConvertList(ListBlock list)
        {
            List<LoreListItem> items = new();
            foreach (Block child in list)
            {
                if (child is ListItemBlock item)
                {
                    items.Add(new LoreListItem(ConvertBlocks(item)));
                }
            }

            int start = 1;
            if (list.IsOrdered && !string.IsNullOrWhiteSpace(list.OrderedStart) &&
                int.TryParse(list.OrderedStart, out int parsedStart))
            {
                start = parsedStart;
            }

            return new LoreListBlock(list.IsOrdered, start, items);
        }

        private static LoreBlock ConvertTable(Table table)
        {
            List<LoreTableCell> headers = new();
            List<IReadOnlyList<LoreTableCell>> rows = new();

            foreach (Block child in table)
            {
                if (child is not TableRow row)
                {
                    continue;
                }

                List<LoreTableCell> cells = new();
                foreach (Block cellBlock in row)
                {
                    if (cellBlock is TableCell cell)
                    {
                        cells.Add(new LoreTableCell(ConvertCellInlines(cell)));
                    }
                }

                if (row.IsHeader && headers.Count == 0 && rows.Count == 0)
                {
                    headers = cells;
                    continue;
                }

                rows.Add(cells);
            }

            return new LoreTableBlock(headers, rows);
        }

        private static List<LoreInline> ConvertCellInlines(TableCell cell)
        {
            List<LoreInline> inlines = new();
            foreach (Block child in cell)
            {
                if (child is not LeafBlock leaf || leaf.Inline is null)
                {
                    continue;
                }

                if (inlines.Count > 0)
                {
                    inlines.Add(new LoreLineBreakInline());
                }

                inlines.AddRange(ConvertInlines(leaf.Inline));
            }

            return inlines;
        }

        private static List<LoreInline> ConvertInlines(ContainerInline? container)
        {
            List<LoreInline> result = new();
            if (container is null)
            {
                return result;
            }

            foreach (Inline inline in container)
            {
                AppendInline(result, inline);
            }

            return result;
        }

        private static void AppendInline(List<LoreInline> target, Inline inline)
        {
            switch (inline)
            {
                case LiteralInline literal:
                    AppendText(target, literal.Content.ToString());
                    break;

                case CodeInline code:
                    target.Add(new LoreCodeInline(code.Content ?? string.Empty));
                    break;

                case TaskList task:
                    AppendText(target, task.Checked ? "[x] " : "[ ] ");
                    break;

                case EmphasisInline emphasis:
                {
                    List<LoreInline> children = ConvertInlines(emphasis);
                    if (children.Count == 0)
                    {
                        break;
                    }

                    if (emphasis.DelimiterChar is '*' or '_')
                    {
                        target.Add(emphasis.DelimiterCount >= 2
                            ? new LoreBoldInline(children)
                            : new LoreItalicInline(children));
                        break;
                    }

                    // Strikethrough, subscript, superscript, inserted and marked
                    // spans have no native reader treatment; keep their text.
                    target.AddRange(children);
                    break;
                }

                case LinkInline link:
                {
                    string url = ResolveUrl(link);
                    List<LoreInline> children = ConvertInlines(link);
                    if (link.IsImage)
                    {
                        string alt = LoreInlineText.Flatten(children);
                        AppendText(target, string.IsNullOrWhiteSpace(alt) ? "[image]" : $"[image: {alt}]");
                        break;
                    }

                    if (children.Count == 0)
                    {
                        children.Add(new LoreTextInline(url));
                    }

                    target.Add(new LoreLinkInline(children, url, ClassifyLink(url)));
                    break;
                }

                case AutolinkInline autolink:
                {
                    string url = autolink.IsEmail ? $"mailto:{autolink.Url}" : autolink.Url;
                    target.Add(new LoreLinkInline(
                        new LoreInline[] { new LoreTextInline(autolink.Url) },
                        url,
                        ClassifyLink(url)));
                    break;
                }

                case LineBreakInline lineBreak:
                    if (lineBreak.IsHard)
                    {
                        target.Add(new LoreLineBreakInline());
                    }
                    else
                    {
                        AppendText(target, " ");
                    }

                    break;

                case HtmlEntityInline entity:
                    AppendText(target, entity.Transcoded.ToString());
                    break;

                case HtmlInline:
                    // Raw markup has no native equivalent; the text around it is
                    // still delivered by the surrounding literals.
                    break;

                case ContainerInline container:
                    foreach (Inline child in container)
                    {
                        AppendInline(target, child);
                    }

                    break;
            }
        }

        private static void AppendText(List<LoreInline> target, string? text)
        {
            if (string.IsNullOrEmpty(text))
            {
                return;
            }

            if (target.Count > 0 && target[^1] is LoreTextInline previous)
            {
                target[^1] = new LoreTextInline(previous.Text + text);
                return;
            }

            target.Add(new LoreTextInline(text));
        }

        private static string ResolveUrl(LinkInline link)
        {
            string? dynamicUrl = link.GetDynamicUrl?.Invoke();
            return (string.IsNullOrWhiteSpace(dynamicUrl) ? link.Url : dynamicUrl) ?? string.Empty;
        }

        private static string ResolveHeadingId(HeadingBlock heading, IReadOnlyList<LoreInline> inlines)
        {
            string? id = heading.GetAttributes().Id;
            return string.IsNullOrWhiteSpace(id)
                ? Slugify(LoreInlineText.Flatten(inlines))
                : id!;
        }

        private static string ReadCodeText(LeafBlock block)
        {
            StringBuilder builder = new();
            for (int index = 0; index < block.Lines.Count; index++)
            {
                if (index > 0)
                {
                    builder.Append('\n');
                }

                builder.Append(block.Lines.Lines[index].Slice.ToString());
            }

            return builder.ToString().TrimEnd('\n');
        }

        private static string StripHtmlTags(string value)
        {
            StringBuilder builder = new(value.Length);
            bool insideTag = false;
            foreach (char character in value)
            {
                if (character == '<')
                {
                    insideTag = true;
                    continue;
                }

                if (character == '>')
                {
                    insideTag = false;
                    continue;
                }

                if (!insideTag)
                {
                    builder.Append(character);
                }
            }

            return builder.ToString();
        }
    }
}
