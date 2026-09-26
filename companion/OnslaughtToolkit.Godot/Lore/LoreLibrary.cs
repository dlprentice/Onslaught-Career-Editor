// SPDX-License-Identifier: MIT
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.Companion.Lore;

public sealed record LoreArticle(string Id, string Title, string Markdown);

/// <summary>An article as the front door lists it: its short label and the line that follows it.</summary>
public sealed record LoreEntry(LoreArticle Article, string Label, string Blurb);

public sealed record LoreShelf(string Name, IReadOnlyList<LoreEntry> Entries);

public sealed record LoreHit(LoreArticle Article, string Snippet, int Matches);

/// <summary>
/// The project's own lore (<c>lore/*.md</c>, project-written preservation records) and the reader's
/// front door (<c>lore-book/BOOK.md</c>), embedded in the application when it is built. As in the
/// retained pack builder, each article's maintainer header is removed and BOOK.md's link list is the
/// reading order. The mission list is read from the player's own game text at run time and is never
/// bundled (<see cref="CampaignLoreComposer"/>).
/// </summary>
public static partial class LoreLibrary
{
    public const string Repository = "https://github.com/dlprentice/Onslaught-Career-Editor/blob/main/";
    public const string HomeId = "BOOK";
    public const string MoreShelf = "Also in the library";

    private static readonly Lazy<(IReadOnlyList<LoreArticle> Articles, IReadOnlyList<LoreShelf> Shelves)> Loaded = new(Load);
    private static readonly System.Collections.Concurrent.ConcurrentDictionary<string, string> SearchText = new();
    private static readonly LoreStyle TextOnly = new("", "", "", "");

    /// <summary>Every article in reading order: the front door, then BOOK.md's list, then anything it does not list.</summary>
    public static IReadOnlyList<LoreArticle> Articles => Loaded.Value.Articles;

    /// <summary>The front door's own sections, then the articles it does not list.</summary>
    public static IReadOnlyList<LoreShelf> Shelves => Loaded.Value.Shelves;

    public static LoreArticle? Home => Find(HomeId);

    public static LoreArticle? Find(string id) => Articles.FirstOrDefault(article => article.Id == id);

    /// <summary>
    /// A Markdown link target as a reader URL: another article becomes <c>lore:id#anchor</c>, any other
    /// repository file its public page on GitHub, a web link itself. Anything else is plain text.
    /// </summary>
    public static string? Resolve(string currentId, string target) => Resolve(currentId, target, id => Find(id) is not null);

    private static string? Resolve(string currentId, string target, Func<string, bool> exists)
    {
        if (target.StartsWith("http://", StringComparison.OrdinalIgnoreCase) || target.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
            return target;
        if (target.StartsWith('#')) return $"lore:{currentId}{target}";
        if (Scheme().IsMatch(target)) return null;
        string[] parts = target.Split('#', 2);
        string anchor = parts.Length > 1 && parts[1].Length > 0 ? "#" + parts[1] : "";
        string? path = Normalize((currentId == HomeId ? "lore-book/" : "lore/") + Uri.UnescapeDataString(parts[0]).Replace('\\', '/'));
        if (path is null) return null;
        if (path == "lore-book/BOOK.md") return $"lore:{HomeId}{anchor}";
        if (path.StartsWith("lore/", StringComparison.Ordinal) && path.EndsWith(".md", StringComparison.Ordinal) && path.Count(c => c == '/') == 1 &&
            exists(path[5..^3]))
            return $"lore:{path[5..^3]}{anchor}";
        return Repository + string.Join("/", path.Split('/').Select(Uri.EscapeDataString)) + anchor;
    }

    /// <summary>An article's Markdown ready to render: comments removed and the mission list read from the player's game.</summary>
    public static string Compose(LoreArticle article, IReadOnlyList<GameLevelName>? levels)
    {
        string markdown = article.Markdown;
        if (CampaignLoreComposer.WantsMissionList(markdown))
        {
            // The linked composer writes the table; the way to fix a missing game is this app's own.
            markdown = levels is { Count: > 0 } ? CampaignLoreComposer.Compose(markdown, levels) : markdown.Replace(
                CampaignLoreComposer.MissionListMarker,
                "> **The mission list is missing because this app cannot see your game.**\n" +
                "> These names are the game's own text, so they are read from your installed copy rather than shipped\n" +
                "> with this app. Choose your Battle Engine Aquila folder on Home, then come back to this page.\n",
                StringComparison.Ordinal);
        }
        return Comment().Replace(markdown, "");
    }

    /// <summary>Articles mentioning a phrase, most mentions first, each with the first mention in context.</summary>
    public static IReadOnlyList<LoreHit> Search(string query)
    {
        string term = query.Trim();
        if (term.Length < 2) return [];
        List<LoreHit> hits = [];
        foreach (LoreArticle article in Articles)
        {
            string plain = SearchText.GetOrAdd(article.Id, _ => Spaces().Replace(string.Join(" ", Markdown.Render(
                Comment().Replace(article.Markdown, ""), _ => null, TextOnly).Blocks.Select(block => block.Text)), " "));
            int first = plain.IndexOf(term, StringComparison.OrdinalIgnoreCase);
            if (first < 0) continue;
            int count = 0;
            for (int at = first; at >= 0; at = plain.IndexOf(term, at + term.Length, StringComparison.OrdinalIgnoreCase)) count++;
            int start = Math.Max(0, first - 70);
            while (start > 0 && start < first && plain[start - 1] != ' ') start++;
            int end = Math.Min(plain.Length, first + term.Length + 110);
            while (end < plain.Length && end > first + term.Length && plain[end] != ' ') end--;
            string snippet = plain[start..end].Trim();
            hits.Add(new LoreHit(article, (start > 0 ? "…" : "") + snippet + (end < plain.Length ? "…" : ""), count));
        }
        return hits.OrderByDescending(hit => hit.Matches).ToArray();
    }

    /// <summary>
    /// Drops the repository's maintainer block (<c>- **Status:**</c>, Last updated, Summary) that sits
    /// directly beneath the title, as the retained pack builder did; any other document is untouched.
    /// </summary>
    public static string StripHeader(string markdown)
    {
        string[] lines = markdown.Replace("\r\n", "\n").Split('\n');
        int start = 0;
        for (; start < lines.Length && !lines[start].StartsWith("- **Status:**", StringComparison.Ordinal); start++)
        {
            string trimmed = lines[start].Trim();
            if (trimmed.Length > 0 && !trimmed.StartsWith('#')) return markdown;
        }
        if (start >= lines.Length) return markdown;
        int end = start + 1;
        while (end < lines.Length && (lines[end].StartsWith("- ", StringComparison.Ordinal) ||
            (lines[end].StartsWith(' ') && lines[end].Trim().Length > 0)))
            end++;
        string head = string.Join("\n", lines[..start]).TrimEnd('\n');
        string rest = string.Join("\n", lines[end..]).TrimStart('\n');
        return head.Length == 0 ? rest : rest.Length == 0 ? head + "\n" : head + "\n\n" + rest;
    }

    private static (IReadOnlyList<LoreArticle>, IReadOnlyList<LoreShelf>) Load()
    {
        Assembly assembly = typeof(LoreLibrary).Assembly;
        Dictionary<string, LoreArticle> articles = new(StringComparer.Ordinal);
        foreach (string resource in assembly.GetManifestResourceNames())
        {
            bool lore = resource.StartsWith("lore/", StringComparison.Ordinal) && resource.Count(c => c == '/') == 1;
            if (!resource.EndsWith(".md", StringComparison.Ordinal) || !(lore || resource == "lore-book/BOOK.md")) continue;
            using Stream stream = assembly.GetManifestResourceStream(resource)!;
            using StreamReader reader = new(stream, Encoding.UTF8);
            string markdown = StripHeader(reader.ReadToEnd());
            string id = resource == "lore-book/BOOK.md" ? HomeId : resource[5..^3];
            string title = markdown.Split('\n').FirstOrDefault(line => line.StartsWith("# ", StringComparison.Ordinal))?[2..].Trim() ?? id;
            articles[id] = new LoreArticle(id, Markdown.Plain(title), markdown);
        }

        List<LoreArticle> ordered = [];
        List<LoreShelf> shelves = [];
        if (articles.TryGetValue(HomeId, out LoreArticle? book))
        {
            ordered.Add(book);
            string shelf = "";
            List<LoreEntry> entries = [];
            string[] lines = book.Markdown.Split('\n');
            for (int index = 0; index < lines.Length; index++)
            {
                if (lines[index].StartsWith("## ", StringComparison.Ordinal))
                {
                    if (entries.Count > 0) shelves.Add(new LoreShelf(shelf, entries));
                    (shelf, entries) = (Markdown.Plain(lines[index][3..].Trim()), []);
                    continue;
                }
                if (!lines[index].StartsWith("- ", StringComparison.Ordinal)) continue;
                StringBuilder item = new(lines[index][2..].Trim());
                for (; index + 1 < lines.Length && lines[index + 1].StartsWith(' ') && lines[index + 1].Trim().Length > 0; index++)
                    item.Append(' ').Append(lines[index + 1].Trim());
                if (BookEntry().Match(item.ToString()) is not { Success: true } entry ||
                    Resolve(HomeId, entry.Groups[2].Value, articles.ContainsKey) is not string url || !url.StartsWith("lore:", StringComparison.Ordinal) ||
                    !articles.TryGetValue(url[5..].Split('#')[0], out LoreArticle? article) || ordered.Contains(article))
                    continue;
                ordered.Add(article);
                entries.Add(new LoreEntry(article, Markdown.Plain(entry.Groups[1].Value), Markdown.Plain(entry.Groups[3].Value).Trim()));
            }
            if (entries.Count > 0) shelves.Add(new LoreShelf(shelf, entries));
        }
        // An unlisted article still ships, after everything curated, as the retained builder did.
        LoreArticle[] rest = articles.Values.Where(article => !ordered.Contains(article))
            .OrderBy(article => article.Id.ToLowerInvariant(), StringComparer.Ordinal).ToArray();
        ordered.AddRange(rest);
        if (rest.Length > 0) shelves.Add(new LoreShelf(MoreShelf, rest.Select(article => new LoreEntry(article, article.Title, "")).ToArray()));
        return (ordered, shelves);
    }

    private static string? Normalize(string path)
    {
        List<string> parts = [];
        foreach (string part in path.Split('/'))
        {
            if (part is "" or ".") continue;
            if (part == "..")
            {
                if (parts.Count == 0) return null;
                parts.RemoveAt(parts.Count - 1);
                continue;
            }
            parts.Add(part);
        }
        return parts.Count == 0 ? null : string.Join("/", parts);
    }

    [GeneratedRegex(@"<!--.*?-->", RegexOptions.Singleline)]
    private static partial Regex Comment();

    [GeneratedRegex(@"^\[([^\]]+)\]\(([^)\s]+)\)\s*(?:[—–-]\s*)?(.*)$")]
    private static partial Regex BookEntry();

    [GeneratedRegex(@"^[a-zA-Z][a-zA-Z0-9+.-]*:")]
    private static partial Regex Scheme();

    [GeneratedRegex(@"\s+")]
    private static partial Regex Spaces();
}
