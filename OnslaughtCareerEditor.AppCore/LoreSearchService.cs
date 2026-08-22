using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>One full-text search hit inside one lore document.</summary>
    public sealed record LoreSearchHit(
        string DocumentPath,
        string DocumentTitle,
        string SnippetBefore,
        string MatchedText,
        string SnippetAfter,
        int OccurrenceCount);

    /// <summary>
    /// The documents that link to one document, plus the anchors they use, so the
    /// reader can show "what links here" without reparsing on every page turn.
    /// Keys are normalized document keys, exactly what
    /// <see cref="LoreBrowserService.NormalizeDocumentKey"/> produces.
    /// </summary>
    public sealed record LoreBacklinkIndex(IReadOnlyDictionary<string, IReadOnlyList<LoreBacklink>> ByTarget);

    /// <summary>One "what links here" entry.</summary>
    public sealed record LoreBacklink(
        string SourceDocumentPath,
        string SourceDocumentTitle,
        IReadOnlyList<string> AnchorTargets);

    /// <summary>One heading in the open document, for the on-this-page outline.</summary>
    public sealed record LoreOutlineEntry(int Level, string Text, string Id);

    /// <summary>One included document this page links to, plus the anchors it uses.</summary>
    public sealed record LoreOutgoingLink(
        string TargetDocumentPath,
        string TargetDocumentTitle,
        IReadOnlyList<string> AnchorTargets);

    /// <summary>
    /// Read-only lore depth services for the WinUI reader: whole-word full-text
    /// search over every included document with match snippets, and a cross-link
    /// ("what links here") index built from each document's parsed internal links.
    ///
    /// Both go through <see cref="LoreBrowserService.LoadDocumentContent"/>, so
    /// packed libraries, repository libraries, and live-composed sections behave
    /// exactly as the reader itself sees them, and link resolution reuses the
    /// service's own <see cref="LoreBrowserService.ResolveInternalTarget"/> rather
    /// than a second copy of its path rules. Nothing here writes.
    /// </summary>
    public sealed class LoreSearchService
    {
        private const int SnippetPadding = 60;

        private readonly LoreBrowserService _service;

        public LoreSearchService(LoreBrowserService service)
        {
            _service = service ?? throw new ArgumentNullException(nameof(service));
        }

        /// <summary>
        /// Searches every included document for <paramref name="query"/> as a whole
        /// word (word characters bound both sides), returning at most
        /// <paramref name="maxHitsPerDocument"/> snippets per document.
        /// </summary>
        public IReadOnlyList<LoreSearchHit> SearchAllDocuments(LoreIndex index, string? query, int maxHitsPerDocument = 3)
        {
            string trimmed = (query ?? string.Empty).Trim();
            if (index is null || trimmed.Length == 0)
            {
                return Array.Empty<LoreSearchHit>();
            }

            var hits = new List<LoreSearchHit>();
            foreach (LoreDocument document in index.Documents)
            {
                string plainText = GetPlainText(document.FilePath);
                List<(int Start, int End)> occurrences = FindWholeWordOccurrences(plainText, trimmed);
                if (occurrences.Count == 0)
                {
                    continue;
                }

                foreach ((int start, int end) in occurrences.Take(maxHitsPerDocument))
                {
                    (string before, string matched, string after) = BuildSnippet(plainText, start, end);
                    hits.Add(new LoreSearchHit(
                        document.FilePath,
                        document.Title,
                        before,
                        matched,
                        after,
                        occurrences.Count));
                }
            }

            return hits;
        }

        /// <summary>
        /// Builds the cross-link index once per library load: for every document,
        /// which documents link to it through internal links, and which anchors they
        /// point at. Documents that cannot be loaded are skipped, matching search.
        /// </summary>
        public LoreBacklinkIndex BuildBacklinkIndex(LoreIndex index)
        {
            var knownKeys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (LoreDocument document in index.Documents)
            {
                knownKeys.Add(_service.NormalizeDocumentKey(document.FilePath));
            }

            var byTarget = new Dictionary<string, List<LoreBacklink>>(StringComparer.OrdinalIgnoreCase);
            foreach (LoreDocument source in index.Documents)
            {
                Dictionary<string, List<string>> targetsByKey = CollectInternalLinkTargets(source.FilePath);
                foreach (KeyValuePair<string, List<string>> entry in targetsByKey)
                {
                    if (!knownKeys.Contains(entry.Key))
                    {
                        continue;
                    }

                    if (!byTarget.TryGetValue(entry.Key, out List<LoreBacklink>? list))
                    {
                        list = new List<LoreBacklink>();
                        byTarget[entry.Key] = list;
                    }

                    list.Add(new LoreBacklink(
                        source.FilePath,
                        source.Title,
                        entry.Value.Distinct(StringComparer.Ordinal).ToArray()));
                }
            }

            return new LoreBacklinkIndex(
                byTarget.ToDictionary(pair => pair.Key, pair => (IReadOnlyList<LoreBacklink>)pair.Value, StringComparer.OrdinalIgnoreCase));
        }

        /// <summary>Returns the backlinks recorded for one document path or key.</summary>
        public IReadOnlyList<LoreBacklink> GetBacklinks(LoreBacklinkIndex? index, string? documentPath)
        {
            if (index is null || string.IsNullOrWhiteSpace(documentPath))
            {
                return Array.Empty<LoreBacklink>();
            }

            string key = _service.NormalizeDocumentKey(documentPath);
            return index.ByTarget.TryGetValue(key, out IReadOnlyList<LoreBacklink>? links)
                ? links
                : Array.Empty<LoreBacklink>();
        }

        /// <summary>
        /// Headings in document order for the on-this-page outline. Empty documents
        /// and documents with no headings return an empty list.
        /// </summary>
        public IReadOnlyList<LoreOutlineEntry> BuildOutline(LoreDocumentContent? content)
        {
            if (content is null)
            {
                return Array.Empty<LoreOutlineEntry>();
            }

            var entries = new List<LoreOutlineEntry>();
            CollectHeadings(content.Document.Blocks, entries);
            return entries;
        }

        /// <summary>
        /// Included documents this page links to, using the same resolver as the
        /// backlink index. External, source, and same-page anchors stay out.
        /// </summary>
        public IReadOnlyList<LoreOutgoingLink> GetOutgoingLinks(LoreIndex? index, string? documentPath)
        {
            if (index is null || string.IsNullOrWhiteSpace(documentPath))
            {
                return Array.Empty<LoreOutgoingLink>();
            }

            Dictionary<string, List<string>> targetsByKey = CollectInternalLinkTargets(documentPath);
            if (targetsByKey.Count == 0)
            {
                return Array.Empty<LoreOutgoingLink>();
            }

            var titleByKey = new Dictionary<string, (string Path, string Title)>(StringComparer.OrdinalIgnoreCase);
            foreach (LoreDocument document in index.Documents)
            {
                titleByKey[_service.NormalizeDocumentKey(document.FilePath)] = (document.FilePath, document.Title);
            }

            var result = new List<LoreOutgoingLink>();
            foreach (KeyValuePair<string, List<string>> entry in targetsByKey)
            {
                if (!titleByKey.TryGetValue(entry.Key, out (string Path, string Title) info))
                {
                    continue;
                }

                result.Add(new LoreOutgoingLink(
                    info.Path,
                    info.Title,
                    entry.Value.Distinct(StringComparer.Ordinal).ToArray()));
            }

            return result;
        }

        private static void CollectHeadings(IReadOnlyList<LoreBlock> blocks, List<LoreOutlineEntry> entries)
        {
            foreach (LoreBlock block in blocks)
            {
                switch (block)
                {
                    case LoreHeadingBlock heading when !string.IsNullOrWhiteSpace(heading.Text):
                        entries.Add(new LoreOutlineEntry(heading.Level, heading.Text, heading.Id));
                        break;
                    case LoreListBlock list:
                        foreach (LoreListItem item in list.Items)
                        {
                            CollectHeadings(item.Blocks, entries);
                        }

                        break;
                    case LoreQuoteBlock quote:
                        CollectHeadings(quote.Blocks, entries);
                        break;
                }
            }
        }

        private string GetPlainText(string filePath)
        {
            try
            {
                LoreDocumentContent content = _service.LoadDocumentContent(filePath);
                var builder = new StringBuilder();
                AppendBlocksText(builder, content.Document.Blocks);
                return builder.ToString();
            }
            catch (Exception exception) when (
                exception is IOException or UnauthorizedAccessException or FileNotFoundException ||
                exception.Message.Contains("could not be found", StringComparison.OrdinalIgnoreCase))
            {
                // A document the reader cannot open contributes no search hits; that
                // is the same boundary the tree itself shows.
                return string.Empty;
            }
        }

        private static void AppendBlocksText(StringBuilder builder, IReadOnlyList<LoreBlock> blocks)
        {
            foreach (LoreBlock block in blocks)
            {
                switch (block)
                {
                    case LoreHeadingBlock heading:
                        AppendLine(builder, heading.Text);
                        break;
                    case LoreParagraphBlock paragraph:
                        AppendLine(builder, paragraph.Text);
                        break;
                    case LoreListBlock list:
                        foreach (LoreListItem item in list.Items)
                        {
                            AppendBlocksText(builder, item.Blocks);
                        }

                        break;
                    case LoreTableBlock table:
                        foreach (LoreTableCell header in table.Headers)
                        {
                            AppendInlineText(builder, header.Inlines);
                            builder.Append(' ');
                        }

                        if (table.Headers.Count > 0)
                        {
                            builder.AppendLine();
                        }

                        foreach (IReadOnlyList<LoreTableCell> row in table.Rows)
                        {
                            foreach (LoreTableCell cell in row)
                            {
                                AppendInlineText(builder, cell.Inlines);
                                builder.Append(' ');
                            }

                            builder.AppendLine();
                        }

                        break;
                    case LoreQuoteBlock quote:
                        AppendBlocksText(builder, quote.Blocks);
                        break;
                    case LoreCodeBlock code:
                        AppendLine(builder, code.Text);
                        break;
                }
            }
        }

        private static void AppendInlineText(StringBuilder builder, IReadOnlyList<LoreInline> inlines)
        {
            builder.Append(LoreInlineText.Flatten(inlines));
        }

        private static void AppendLine(StringBuilder builder, string text)
        {
            if (!string.IsNullOrWhiteSpace(text))
            {
                builder.AppendLine(text);
            }
        }

        private Dictionary<string, List<string>> CollectInternalLinkTargets(string sourceFilePath)
        {
            var result = new Dictionary<string, List<string>>(StringComparer.OrdinalIgnoreCase);
            LoreDocumentContent content;
            try
            {
                content = _service.LoadDocumentContent(sourceFilePath);
            }
            catch (Exception exception) when (
                exception is IOException or UnauthorizedAccessException or FileNotFoundException ||
                exception.Message.Contains("could not be found", StringComparison.OrdinalIgnoreCase))
            {
                return result;
            }

            var targets = new List<string>();
            CollectInternalTargets(content.Document.Blocks, targets);
            foreach (string target in targets)
            {
                string anchor = LoreBrowserService.ExtractAnchor(target) ?? string.Empty;
                string? resolved = _service.ResolveInternalTarget(sourceFilePath, target);
                if (string.IsNullOrWhiteSpace(resolved))
                {
                    continue;
                }

                string key = _service.NormalizeDocumentKey(resolved);
                if (!result.TryGetValue(key, out List<string>? anchors))
                {
                    anchors = new List<string>();
                    result[key] = anchors;
                }

                anchors.Add(anchor);
            }

            return result;
        }

        private static void CollectInternalTargets(IReadOnlyList<LoreBlock> blocks, List<string> targets)
        {
            foreach (LoreBlock block in blocks)
            {
                switch (block)
                {
                    case LoreParagraphBlock paragraph:
                        CollectInlineTargets(paragraph.Inlines, targets);
                        break;
                    case LoreHeadingBlock heading:
                        CollectInlineTargets(heading.Inlines, targets);
                        break;
                    case LoreListBlock list:
                        foreach (LoreListItem item in list.Items)
                        {
                            CollectInternalTargets(item.Blocks, targets);
                        }

                        break;
                    case LoreTableBlock table:
                        foreach (LoreTableCell cell in table.Headers.Concat(table.Rows.SelectMany(row => row)))
                        {
                            CollectInlineTargets(cell.Inlines, targets);
                        }

                        break;
                    case LoreQuoteBlock quote:
                        CollectInternalTargets(quote.Blocks, targets);
                        break;
                }
            }
        }

        private static void CollectInlineTargets(IReadOnlyList<LoreInline> inlines, List<string> targets)
        {
            foreach (LoreInline inline in inlines)
            {
                switch (inline)
                {
                    case LoreLinkInline link when link.Kind == LoreLinkKind.Internal:
                        targets.Add(link.Target);
                        break;
                    case LoreBoldInline bold:
                        CollectInlineTargets(bold.Inlines, targets);
                        break;
                    case LoreItalicInline italic:
                        CollectInlineTargets(italic.Inlines, targets);
                        break;
                }
            }
        }

        private static List<(int Start, int End)> FindWholeWordOccurrences(string text, string query)
        {
            var occurrences = new List<(int Start, int End)>();
            int position = 0;
            while (position <= text.Length - query.Length)
            {
                int found = text.IndexOf(query, position, StringComparison.OrdinalIgnoreCase);
                if (found < 0)
                {
                    break;
                }

                bool leftBoundary = found == 0 || !IsWordCharacter(text[found - 1]);
                int end = found + query.Length;
                bool rightBoundary = end >= text.Length || !IsWordCharacter(text[end]);
                if (leftBoundary && rightBoundary)
                {
                    occurrences.Add((found, end));
                }

                position = Math.Max(found + 1, end);
            }

            return occurrences;
        }

        private static bool IsWordCharacter(char value)
        {
            return char.IsLetterOrDigit(value) || value == '_';
        }

        private static (string Before, string Matched, string After) BuildSnippet(string text, int start, int end)
        {
            int snippetStart = Math.Max(0, start - SnippetPadding);
            int snippetEnd = Math.Min(text.Length, end + SnippetPadding);

            string before = CollapseWhitespace(text[snippetStart..start]);
            string matched = CollapseWhitespace(text[start..end]);
            string after = CollapseWhitespace(text[end..snippetEnd]);

            if (snippetStart > 0 && before.Length > 0)
            {
                before = "\u2026" + before;
            }

            if (snippetEnd < text.Length && after.Length > 0)
            {
                after = after + "\u2026";
            }

            return (before, matched, after);
        }

        private static string CollapseWhitespace(string value)
        {
            var builder = new StringBuilder(value.Length);
            bool pendingSpace = false;
            foreach (char character in value)
            {
                if (char.IsWhiteSpace(character))
                {
                    pendingSpace = builder.Length > 0;
                    continue;
                }

                if (pendingSpace)
                {
                    builder.Append(' ');
                    pendingSpace = false;
                }

                builder.Append(character);
            }

            return builder.ToString();
        }
    }
}
