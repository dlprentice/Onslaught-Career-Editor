using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.Cli
{
    /// <summary>
    /// Quiet, read-only Lore parity. The GUI reader composes
    /// <see cref="LoreBrowserService"/> with <see cref="LoreSearchService"/>; these verbs hand the
    /// same capability to a headless caller without inventing a second parser, catalog, or output
    /// framework. Nothing here writes: no render files, no pack builds, no settings.
    ///
    /// One <see cref="LoreBrowserService"/> instance serves a whole invocation, because
    /// <c>LoadIndex</c> records which content pack the subsequent document loads come from.
    /// </summary>
    public static class LoreVerbs
    {
        public static int Search(CliContext ctx, string? query, string? root)
        {
            const string command = "lore.search";
            string trimmed = (query ?? string.Empty).Trim();
            if (trimmed.Length == 0)
                return ctx.Usage(command, "A search query is required.", "Example: lore search aquila");

            if (!TryLoadLibrary(ctx, command, root, out LoreBrowserService? service, out LoreIndex? index))
                return CliExit.UsageOrToolError;

            var search = new LoreSearchService(service!);
            IReadOnlyList<LoreSearchHit> hits = search.SearchAllDocuments(index!, trimmed);

            if (ctx.Json)
            {
                return ctx.Ok(command, new
                {
                    query = trimmed,
                    root = index!.ProjectRoot,
                    documentsSearched = index!.Documents.Count,
                    hitCount = hits.Count,
                    hits = hits.Select(hit => new
                    {
                        document = DisplayKey(hit.DocumentPath, index!),
                        documentTitle = hit.DocumentTitle,
                        sectionAnchor = hit.SectionAnchor,
                        sectionHeading = hit.SectionHeading,
                        occurrenceCount = hit.OccurrenceCount,
                        snippet = new
                        {
                            before = hit.SnippetBefore,
                            matched = hit.MatchedText,
                            after = hit.SnippetAfter,
                        },
                    }).ToArray(),
                });
            }

            ctx.Line("Onslaught Career Editor - Lore Search");
            ctx.Line($"Query: {trimmed}");
            ctx.Line($"Documents searched: {index!.Documents.Count}    Hits: {hits.Count}");
            ctx.Line();

            if (hits.Count == 0)
            {
                ctx.Line("No documents match.");
                return CliExit.Success;
            }

            foreach (LoreSearchHit hit in hits)
            {
                ctx.Line($"{hit.DocumentTitle}  ({DisplayKey(hit.DocumentPath, index!)})");
                ctx.Line($"  section: {(hit.SectionHeading.Length > 0 ? hit.SectionHeading : "(document top)")}");
                ctx.Line($"  occurrences: {hit.OccurrenceCount}");
                ctx.Line($"  ...{NormalizeWhitespace(hit.SnippetBefore)}[{hit.MatchedText}]{NormalizeWhitespace(hit.SnippetAfter)}...");
            }

            return CliExit.Success;
        }

        public static int Show(CliContext ctx, string? document, string? root)
        {
            const string command = "lore.show";
            if (string.IsNullOrWhiteSpace(document))
                return ctx.Usage(command, "A document key is required.", "Example: lore show lore/characters.md");

            if (!TryLoadLibrary(ctx, command, root, out LoreBrowserService? service, out LoreIndex? index))
                return CliExit.UsageOrToolError;

            // A well-formed key that names nothing is a verdict about the library, not a bad
            // invocation - the same split as analyzing a file that is not a save.
            string? resolved = ResolveDocumentKey(service!, index!, document);
            if (resolved is null)
                return ctx.Verdict(command, $"No lore document matches that key: {document}", new { document });

            LoreDocumentContent content;
            try
            {
                content = service!.LoadDocumentContent(resolved);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                return ctx.Usage(command, DescribeFileFailure(ex, document));
            }

            IReadOnlyList<LoreOutlineEntry> outline = new LoreSearchService(service).BuildOutline(content);
            string text = RenderPlainText(content.Document.Blocks);

            if (ctx.Json)
            {
                return ctx.Ok(command, new
                {
                    document,
                    title = content.Title,
                    isMarkdown = content.IsMarkdown,
                    blockCount = content.Document.Blocks.Count,
                    outline = outline.Select(entry => new
                    {
                        level = entry.Level,
                        text = entry.Text,
                        id = entry.Id,
                    }).ToArray(),
                    text,
                });
            }

            ctx.Line(content.Title);
            ctx.Line(new string('=', Math.Max(4, content.Title.Length)));

            // The same outline the JSON surface reports, so text mode keeps the documented
            // title/outline/plain-text shape instead of collapsing the document onto one line.
            foreach (LoreOutlineEntry entry in outline)
            {
                string indent = new string(' ', Math.Max(0, entry.Level - 1) * 2);
                string anchor = string.IsNullOrEmpty(entry.Id) ? string.Empty : $"  (#{entry.Id})";
                ctx.Line($"{indent}{entry.Text}{anchor}");
            }

            if (outline.Count > 0)
                ctx.Line();

            // Split before flattening so each source line survives as its own output line;
            // NormalizeWhitespace then only tidies the line itself.
            foreach (string line in BodyLines(text))
                ctx.Line(line);

            return CliExit.Success;
        }

        private static bool TryLoadLibrary(
            CliContext ctx,
            string command,
            string? root,
            out LoreBrowserService? service,
            out LoreIndex? index)
        {
            try
            {
                service = new LoreBrowserService();
                index = service.LoadIndex(root);
                return true;
            }
            catch (Exception ex) when (
                ex is DirectoryNotFoundException or InvalidDataException or IOException or UnauthorizedAccessException)
            {
                // Without a usable library nothing was measured; that is usage/tool territory,
                // not a verdict about a query.
                service = null;
                index = null;
                ctx.Usage(command, ex.Message, "Point --root at the folder holding the lore content.");
                return false;
            }
        }

        /// <summary>
        /// How a caller may address one indexed document: the reader's own key first (an absolute
        /// path or a content-pack URI, exactly what <c>lore search</c> and the GUI hand back),
        /// then either spelling of a relative path - library-root-relative (<c>lore/alpha.md</c>)
        /// or content-directory-relative (<c>alpha.md</c>). Membership is decided only by the
        /// loaded index: a file that merely exists on disk is not addressed by this verb, which is
        /// also the same answer the GUI reader gives.
        /// </summary>
        private static string? ResolveDocumentKey(LoreBrowserService service, LoreIndex index, string document)
        {
            // Reader-key form: anchors are presentation, so "key#section" addresses the same
            // document. NormalizeDocumentKey passes pack URIs through untouched and turns every
            // other spelling into its full path, so this comparison is exact on both sides.
            string request = service.NormalizeDocumentKey(document);
            foreach (LoreDocument candidate in index.Documents)
            {
                if (!string.IsNullOrWhiteSpace(candidate.FilePath) &&
                    string.Equals(service.NormalizeDocumentKey(candidate.FilePath), request, StringComparison.OrdinalIgnoreCase))
                {
                    return candidate.FilePath;
                }
            }

            string relativeRequest = NormalizeRelativeForm(document);
            foreach (LoreDocument candidate in index.Documents)
            {
                if (NormalizeRelativeForm(candidate.RelativePath).Length > 0 &&
                    string.Equals(NormalizeRelativeForm(candidate.RelativePath), relativeRequest, StringComparison.OrdinalIgnoreCase))
                {
                    return candidate.FilePath;
                }

                if (string.Equals(NormalizeRelativeForm(DisplayKey(candidate.FilePath, index)), relativeRequest, StringComparison.OrdinalIgnoreCase))
                {
                    return candidate.FilePath;
                }
            }

            return null;
        }

        private static string NormalizeRelativeForm(string value)
        {
            string uniform = value.Trim().Replace('/', Path.DirectorySeparatorChar);
            if (uniform.StartsWith("." + Path.DirectorySeparatorChar, StringComparison.Ordinal))
                uniform = uniform[2..];

            return uniform.Replace(Path.DirectorySeparatorChar, '/');
        }

        /// <summary>
        /// How a hit's document should be named for the caller: relative to the library root with
        /// forward slashes when it lives there, otherwise the reader's own key (content-pack URIs).
        /// </summary>
        private static string DisplayKey(string documentPath, LoreIndex index)
        {
            string root = Path.GetFullPath(index.ProjectRoot).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string full = Path.GetFullPath(documentPath);
            if (full.StartsWith(root, StringComparison.OrdinalIgnoreCase) &&
                full.Length > root.Length &&
                (full[root.Length] == Path.DirectorySeparatorChar || full[root.Length] == Path.AltDirectorySeparatorChar))
            {
                return full[(root.Length + 1)..].Replace('\\', '/');
            }

            return documentPath;
        }

        private static string DescribeFileFailure(Exception ex, string document)
        {
            return $"The lore document could not be read: {document} ({ex.Message})";
        }

        /// <summary>
        /// Renders the parsed document model to plain text. This is presentation of blocks the
        /// AppCore parser already produced - the same adaptation the native reader performs - not
        /// a second parse of the markdown.
        /// </summary>
        private static string RenderPlainText(IReadOnlyList<LoreBlock> blocks)
        {
            var builder = new StringBuilder();
            AppendBlocks(builder, blocks);
            return builder.ToString();
        }

        private static void AppendBlocks(StringBuilder builder, IReadOnlyList<LoreBlock> blocks)
        {
            foreach (LoreBlock block in blocks)
            {
                switch (block)
                {
                    case LoreHeadingBlock heading:
                        AppendLine(builder, LoreInlineText.Flatten(heading.Inlines));
                        break;
                    case LoreParagraphBlock paragraph:
                        AppendLine(builder, LoreInlineText.Flatten(paragraph.Inlines));
                        break;
                    case LoreListBlock list:
                        foreach (LoreListItem item in list.Items)
                            AppendBlocks(builder, item.Blocks);
                        break;
                    case LoreTableBlock table:
                        foreach (string cellText in table.Headers.Select(header => header.Text)
                                     .Concat(table.Rows.SelectMany(row => row).Select(cell => cell.Text))
                                     .Where(text => !string.IsNullOrWhiteSpace(text)))
                        {
                            AppendLine(builder, cellText);
                        }
                        break;
                    case LoreQuoteBlock quote:
                        AppendBlocks(builder, quote.Blocks);
                        break;
                    case LoreCodeBlock code:
                        AppendLine(builder, code.Text);
                        break;
                }
            }
        }

        private static void AppendLine(StringBuilder builder, string text)
        {
            if (!string.IsNullOrWhiteSpace(text))
                builder.AppendLine(text);
        }

        private static string NormalizeWhitespace(string value)
        {
            return string.Join(" ", value.Split(
                new[] { ' ', '\r', '\n', '\t' },
                StringSplitOptions.RemoveEmptyEntries));
        }

        /// <summary>
        /// One output line per source line of the rendered text. The split happens before any
        /// whitespace normalization - normalizing first would weld the whole document onto a
        /// single line and make the split meaningless.
        /// </summary>
        private static IEnumerable<string> BodyLines(string text)
        {
            foreach (string raw in text.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None))
            {
                string line = NormalizeWhitespace(raw);
                if (line.Length > 0)
                    yield return line;
            }
        }
    }
}
