using System.Text;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// How a lore link should be treated when the reader activates it. The
    /// classification is computed once during parsing so presentation code never
    /// has to re-derive the source/external boundary.
    /// </summary>
    public enum LoreLinkKind
    {
        /// <summary>A link into another included lore document.</summary>
        Internal,

        /// <summary>A same-document fragment link ("#heading").</summary>
        Anchor,

        /// <summary>An http/https/mailto link that leaves the app.</summary>
        External,

        /// <summary>An external link into this project's own GitHub source.</summary>
        Source
    }

    /// <summary>Base type for a run of inline lore content.</summary>
    public abstract record LoreInline;

    /// <summary>Plain text.</summary>
    public sealed record LoreTextInline(string Text) : LoreInline;

    /// <summary>Strong emphasis.</summary>
    public sealed record LoreBoldInline(IReadOnlyList<LoreInline> Inlines) : LoreInline;

    /// <summary>Ordinary emphasis.</summary>
    public sealed record LoreItalicInline(IReadOnlyList<LoreInline> Inlines) : LoreInline;

    /// <summary>An inline code span.</summary>
    public sealed record LoreCodeInline(string Text) : LoreInline;

    /// <summary>A hard line break inside a paragraph.</summary>
    public sealed record LoreLineBreakInline : LoreInline;

    /// <summary>A link. <see cref="Target"/> is the raw markdown target.</summary>
    public sealed record LoreLinkInline(IReadOnlyList<LoreInline> Inlines, string Target, LoreLinkKind Kind) : LoreInline
    {
        /// <summary>The link's visible text with all formatting flattened away.</summary>
        public string Text => LoreInlineText.Flatten(Inlines);
    }

    /// <summary>Base type for a block of lore content.</summary>
    public abstract record LoreBlock;

    /// <summary>A heading. <see cref="Id"/> is the anchor other documents link to.</summary>
    public sealed record LoreHeadingBlock(int Level, IReadOnlyList<LoreInline> Inlines, string Id) : LoreBlock
    {
        /// <summary>The heading text with all formatting flattened away.</summary>
        public string Text => LoreInlineText.Flatten(Inlines);
    }

    /// <summary>A paragraph of prose.</summary>
    public sealed record LoreParagraphBlock(IReadOnlyList<LoreInline> Inlines) : LoreBlock
    {
        /// <summary>The paragraph text with all formatting flattened away.</summary>
        public string Text => LoreInlineText.Flatten(Inlines);
    }

    /// <summary>One entry in a bullet or numbered list; entries hold blocks so nesting works.</summary>
    public sealed record LoreListItem(IReadOnlyList<LoreBlock> Blocks);

    /// <summary>A bullet or numbered list.</summary>
    public sealed record LoreListBlock(bool IsOrdered, int StartNumber, IReadOnlyList<LoreListItem> Items) : LoreBlock;

    /// <summary>One table cell.</summary>
    public sealed record LoreTableCell(IReadOnlyList<LoreInline> Inlines)
    {
        /// <summary>The cell text with all formatting flattened away.</summary>
        public string Text => LoreInlineText.Flatten(Inlines);
    }

    /// <summary>A table. <see cref="Headers"/> is empty when the source table had no header row.</summary>
    public sealed record LoreTableBlock(
        IReadOnlyList<LoreTableCell> Headers,
        IReadOnlyList<IReadOnlyList<LoreTableCell>> Rows) : LoreBlock;

    /// <summary>A fenced or indented code block.</summary>
    public sealed record LoreCodeBlock(string Text, string? Language) : LoreBlock;

    /// <summary>A block quote.</summary>
    public sealed record LoreQuoteBlock(IReadOnlyList<LoreBlock> Blocks) : LoreBlock;

    /// <summary>A horizontal rule.</summary>
    public sealed record LoreThematicBreakBlock : LoreBlock;

    /// <summary>A standalone image.</summary>
    public sealed record LoreImageBlock(string Uri, string Alt) : LoreBlock;

    /// <summary>
    /// A presentation-neutral lore document: a title and an ordered list of
    /// blocks. Nothing here depends on a UI framework, so the same model can be
    /// rendered natively, exercised in tests, or serialized.
    /// </summary>
    public sealed record LoreDocumentModel(string Title, IReadOnlyList<LoreBlock> Blocks)
    {
        /// <summary>An empty document with the supplied title.</summary>
        public static LoreDocumentModel Empty(string title)
        {
            return new LoreDocumentModel(title, Array.Empty<LoreBlock>());
        }
    }

    /// <summary>Flattens inline trees down to their visible text.</summary>
    public static class LoreInlineText
    {
        /// <summary>Returns the visible text of an inline run, ignoring formatting.</summary>
        public static string Flatten(IReadOnlyList<LoreInline>? inlines)
        {
            if (inlines == null || inlines.Count == 0)
            {
                return string.Empty;
            }

            StringBuilder builder = new();
            Append(builder, inlines);
            return builder.ToString();
        }

        private static void Append(StringBuilder builder, IReadOnlyList<LoreInline> inlines)
        {
            foreach (LoreInline inline in inlines)
            {
                switch (inline)
                {
                    case LoreTextInline text:
                        builder.Append(text.Text);
                        break;
                    case LoreCodeInline code:
                        builder.Append(code.Text);
                        break;
                    case LoreBoldInline bold:
                        Append(builder, bold.Inlines);
                        break;
                    case LoreItalicInline italic:
                        Append(builder, italic.Inlines);
                        break;
                    case LoreLinkInline link:
                        Append(builder, link.Inlines);
                        break;
                    case LoreLineBreakInline:
                        builder.Append(' ');
                        break;
                }
            }
        }
    }
}
