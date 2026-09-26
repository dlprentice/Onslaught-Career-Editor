// SPDX-License-Identifier: MIT
using System.Text;
using System.Text.RegularExpressions;

namespace OnslaughtToolkit.Companion.Lore;

/// <summary>A heading in a rendered article, with its link anchor and the paragraph it starts.</summary>
public sealed record LoreHeading(int Level, string Text, string Anchor, int Paragraph);

/// <summary>A rendered block's first paragraph and its plain text, so a reader can scroll to a search match.</summary>
public sealed record LoreBlock(int Paragraph, string Text);

public sealed record RenderedArticle(string Bbcode, IReadOnlyList<LoreHeading> Headings, IReadOnlyDictionary<string, int> Anchors,
    IReadOnlyList<LoreBlock> Blocks)
{
    /// <summary>The paragraph where the first block mentioning <paramref name="term"/> starts.</summary>
    public int? FirstMention(string term) =>
        Blocks.FirstOrDefault(block => block.Text.Contains(term, StringComparison.OrdinalIgnoreCase))?.Paragraph;
}

/// <summary>Colours (hex, no #) the renderer writes into markup; the page supplies the theme's.</summary>
public sealed record LoreStyle(string Code, string Quote, string Rule, string TableHeader);

/// <summary>
/// The Markdown the lore articles use, rendered as Godot rich text: headings, paragraphs, emphasis,
/// inline code and code blocks, nested bulleted and numbered lists, block quotes, tables, rules, links
/// and HTML anchors. Anything else is shown as text. Brackets in article text are escaped, so no
/// article can inject markup.
/// </summary>
public static partial class Markdown
{
    public const int TitleSize = 28, SectionSize = 21, SubsectionSize = 17, MinorSize = 15;

    /// <summary>Renders an article; <paramref name="link"/> turns a Markdown target into a URL the reader handles, or null for plain text.</summary>
    public static RenderedArticle Render(string markdown, Func<string, string?> link, LoreStyle style)
    {
        StringBuilder output = new();
        List<LoreHeading> headings = [];
        Dictionary<string, int> anchors = new(StringComparer.Ordinal);
        List<LoreBlock> blocks = [];
        int paragraph = 0;
        string[] lines = markdown.Replace("\r\n", "\n").Split('\n');
        for (int index = 0; index < lines.Length; index++)
        {
            string line = lines[index];
            string trimmed = line.Trim();
            if (trimmed.StartsWith("```", StringComparison.Ordinal))
            {
                List<string> code = [];
                for (index++; index < lines.Length && !lines[index].Trim().StartsWith("```", StringComparison.Ordinal); index++)
                    code.Add(lines[index].TrimEnd());
                Emit($"[indent][color=#{style.Code}][code]{Escape(string.Join("\n", code))}[/code][/color][/indent]", string.Join(" ", code));
                continue;
            }
            if (trimmed.Length == 0) continue;
            if (HtmlAnchor().Match(trimmed) is { Success: true } anchor)
            {
                anchors.TryAdd(anchor.Groups[1].Value, paragraph);
                continue;
            }
            if (Heading().Match(trimmed) is { Success: true } heading)
            {
                int level = heading.Groups[1].Value.Length;
                string text = heading.Groups[2].Value.Trim().TrimEnd('#').Trim();
                string plain = Plain(text);
                string slug = Slug(plain);
                for (int suffix = 1; anchors.ContainsKey(slug); suffix++) slug = $"{Slug(plain)}-{suffix}";
                anchors[slug] = paragraph;
                headings.Add(new LoreHeading(level, plain, slug, paragraph));
                int size = level switch { 1 => TitleSize, 2 => SectionSize, 3 => SubsectionSize, _ => MinorSize };
                Emit($"[font_size={size}][b]{Inline(text, link, style)}[/b][/font_size]", plain);
                continue;
            }
            if (Rule().IsMatch(trimmed))
            {
                Emit($"[color=#{style.Rule}]{new string('─', 32)}[/color]", "");
                continue;
            }
            if (trimmed.StartsWith('|'))
            {
                List<string[]> rows = [];
                for (; index < lines.Length && lines[index].Trim().StartsWith('|'); index++)
                {
                    string row = lines[index].Trim();
                    if (!TableSeparator().IsMatch(row)) rows.Add(Cells(row));
                }
                index--;
                Emit(Table(rows, link, style), string.Join(" ", rows.SelectMany(row => row).Select(Plain)));
                continue;
            }
            if (trimmed.StartsWith('>'))
            {
                // Quoted memos and interviews keep their line breaks (headers, signatures).
                List<string> quote = [];
                for (; index < lines.Length && lines[index].Trim().StartsWith('>'); index++)
                    quote.Add(lines[index].Trim()[1..].Trim());
                index--;
                Emit($"[indent][color=#{style.Quote}]{string.Join("\n", quote.Select(text => Inline(text, link, style)))}[/color][/indent]",
                    Plain(string.Join(" ", quote)));
                continue;
            }
            if (ListItem().IsMatch(line))
            {
                List<(int Depth, bool Ordered, string Text)> items = [];
                for (; index < lines.Length; index++)
                {
                    if (lines[index].Trim().Length == 0)
                    {
                        // A blank line between items keeps one list; anything else ends it.
                        if (index + 1 < lines.Length && ListItem().IsMatch(lines[index + 1])) continue;
                        break;
                    }
                    if (ListItem().Match(lines[index]) is not { Success: true } item) break;
                    StringBuilder text = new(item.Groups[3].Value.Trim());
                    for (; index + 1 < lines.Length && char.IsWhiteSpace(lines[index + 1].FirstOrDefault('x')) &&
                        lines[index + 1].Trim().Length > 0 && !ListItem().IsMatch(lines[index + 1]); index++)
                        text.Append(' ').Append(lines[index + 1].Trim());
                    int indent = item.Groups[1].Value.Replace("\t", "    ").Length;
                    items.Add((Math.Min(3, (indent + 1) / 3), char.IsDigit(item.Groups[2].Value[0]), text.ToString()));
                }
                index--;
                Emit(List(items, link, style), Plain(string.Join(" ", items.Select(item => item.Text))));
                continue;
            }
            StringBuilder paragraphText = new(trimmed);
            for (; index + 1 < lines.Length && IsContinuation(lines[index + 1]); index++)
                paragraphText.Append(' ').Append(lines[index + 1].Trim());
            Emit(Inline(paragraphText.ToString(), link, style), Plain(paragraphText.ToString()));
        }
        return new RenderedArticle(output.ToString().TrimEnd('\n'), headings, anchors, blocks);

        void Emit(string block, string plain)
        {
            blocks.Add(new LoreBlock(paragraph, plain));
            output.Append(block).Append("\n\n");
            paragraph += 2 + block.Count(character => character == '\n');
        }
    }

    /// <summary>Text with Markdown markers removed, for search, headings and outlines.</summary>
    public static string Plain(string markdown) =>
        Italic().Replace(Bold().Replace(LinkPattern().Replace(markdown.Replace("`", ""), "$1"), "$1"), "$2")
            .Replace("<!--", "").Replace("-->", "");

    /// <summary>The anchor GitHub gives a heading: lower case, punctuation dropped, spaces as hyphens.</summary>
    public static string Slug(string heading)
    {
        StringBuilder slug = new();
        foreach (char character in heading.Trim().ToLowerInvariant())
        {
            if (char.IsLetterOrDigit(character) || character is '-' or '_') slug.Append(character);
            else if (character == ' ') slug.Append('-');
        }
        return slug.ToString();
    }

    private static string List(List<(int Depth, bool Ordered, string Text)> items, Func<string, string?> link, LoreStyle style)
    {
        StringBuilder list = new();
        Stack<bool> open = new();
        bool first = true;
        foreach ((int depth, bool ordered, string text) in items)
        {
            while (open.Count > depth + 1) list.Append(open.Pop() ? "[/ol]" : "[/ul]");
            if (open.Count == depth + 1 && open.Peek() != ordered) list.Append(open.Pop() ? "[/ol]" : "[/ul]");
            if (!first) list.Append('\n');
            while (open.Count < depth + 1)
            {
                list.Append(ordered ? "[ol type=1]" : "[ul]");
                open.Push(ordered);
            }
            list.Append(Inline(text, link, style));
            first = false;
        }
        while (open.Count > 0) list.Append(open.Pop() ? "[/ol]" : "[/ul]");
        return list.ToString();
    }

    private static string Table(List<string[]> rows, Func<string, string?> link, LoreStyle style)
    {
        int columns = rows.Max(row => row.Length);
        StringBuilder table = new($"[table={columns}]");
        for (int row = 0; row < rows.Count; row++)
        {
            for (int column = 0; column < columns; column++)
            {
                string cell = column < rows[row].Length ? Inline(rows[row][column], link, style) : "";
                // Wider columns take more of the spare width; every column may wrap.
                string expand = row == 0 ? $" expand={Weight(rows, column)}" : "";
                table.Append(row == 0
                    ? $"[cell{expand} padding=8,6,8,6 bg=#{style.TableHeader}][b]{cell}[/b][/cell]"
                    : $"[cell padding=8,5,8,5]{cell}[/cell]");
            }
        }
        return table.Append("[/table]").ToString();
    }

    private static int Weight(List<string[]> rows, int column)
    {
        double average = rows.Average(row => column < row.Length ? Plain(row[column]).Length : 0);
        return (int)Math.Clamp(Math.Round(average / 12), 1, 8);
    }

    /// <summary>A table row's cells; <c>\|</c> is a literal bar inside a cell.</summary>
    private static string[] Cells(string row)
    {
        string inner = row.Trim();
        if (inner.StartsWith('|')) inner = inner[1..];
        if (inner.EndsWith('|') && !inner.EndsWith("\\|", StringComparison.Ordinal)) inner = inner[..^1];
        return CellSplit().Split(inner).Select(cell => cell.Replace("\\|", "|").Trim()).ToArray();
    }

    private static bool IsContinuation(string next)
    {
        string trimmed = next.Trim();
        return trimmed.Length > 0 && !trimmed.StartsWith('#') && !trimmed.StartsWith('|') && !trimmed.StartsWith('>') &&
            !trimmed.StartsWith("```", StringComparison.Ordinal) && !ListItem().IsMatch(next) && !Rule().IsMatch(trimmed) &&
            !HtmlAnchor().IsMatch(trimmed);
    }

    /// <summary>
    /// Code spans, images and links become placeholders first, so emphasis can span them
    /// (<c>**the `x` rule**</c>) and nothing inside a code span is read as emphasis.
    /// </summary>
    private static string Inline(string text, Func<string, string?> link, LoreStyle style)
    {
        List<string> tokens = [];
        string masked = InlineToken().Replace(text, token =>
        {
            tokens.Add(Token(token, link, style));
            return $"\uE000{tokens.Count - 1}\uE001";
        });
        return Placeholder().Replace(Emphasize(Escape(masked)), match => tokens[int.Parse(match.Groups[1].Value)]);
    }

    private static string Token(Match token, Func<string, string?> link, LoreStyle style)
    {
        if (token.Groups["code"].Success) return $"[color=#{style.Code}][code]{Escape(token.Groups["code"].Value)}[/code][/color]";
        if (token.Groups["image"].Success) return $"[i]{Escape(token.Groups["image"].Value)}[/i]";
        string label = Emphasize(InlineCode(Escape(token.Groups["label"].Value), style));
        return link(token.Groups["target"].Value) is string url ? $"[url={url.Replace("]", "%5D")}]{label}[/url]" : label;
    }

    private static string InlineCode(string label, LoreStyle style) =>
        CodeSpan().Replace(label, match => $"[color=#{style.Code}][code]{match.Groups[1].Value}[/code][/color]");

    private static string Emphasize(string text) =>
        Italic().Replace(Bold().Replace(text, "[b]$1[/b]"), "[i]$2[/i]");

    private static string Escape(string text) => text.Replace("[", "[lb]");

    [GeneratedRegex(@"^(#{1,6})\s+(.*)$")]
    private static partial Regex Heading();

    [GeneratedRegex(@"^(-{3,}|\*{3,}|_{3,})$")]
    private static partial Regex Rule();

    [GeneratedRegex(@"^\|?\s*:?-{3,}")]
    private static partial Regex TableSeparator();

    [GeneratedRegex(@"(?<!\\)\|")]
    private static partial Regex CellSplit();

    [GeneratedRegex(@"^(\s*)([-*+]|\d+\.)\s+(.*)$")]
    private static partial Regex ListItem();

    [GeneratedRegex(@"^<a\s+(?:id|name)=""([^""]+)""\s*>\s*</a>$")]
    private static partial Regex HtmlAnchor();

    [GeneratedRegex(@"`(?<code>[^`]+)`|!\[(?<image>[^\]]*)\]\([^)]*\)|\[(?<label>(?:[^\[\]]|`[^`]*`)+)\]\((?<target>[^)\s]+)(?:\s+""[^""]*"")?\)")]
    private static partial Regex InlineToken();

    [GeneratedRegex(@"`([^`]+)`")]
    private static partial Regex CodeSpan();

    [GeneratedRegex("\uE000(\\d+)\uE001")]
    private static partial Regex Placeholder();

    [GeneratedRegex(@"\*\*(.+?)\*\*")]
    private static partial Regex Bold();

    [GeneratedRegex(@"(?<![\w*])([*_])(?![\s*_])(.+?)(?<![\s*_])\1(?![\w*])")]
    private static partial Regex Italic();

    [GeneratedRegex(@"!?\[([^\]]*)\]\(([^)]*)\)")]
    private static partial Regex LinkPattern();
}
