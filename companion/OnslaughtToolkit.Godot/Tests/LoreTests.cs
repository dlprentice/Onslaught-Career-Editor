// SPDX-License-Identifier: MIT
using System.Text.RegularExpressions;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Lore;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The embedded lore library and its Markdown renderer: reading order, shelves, header removal, every
/// link in every article, balanced markup, search and the mission list read from a synthetic game table.
/// </summary>
internal static partial class LoreTests
{
    private static readonly LoreStyle Style = new("c0de00", "a0a0a0", "b0b0b0", "d0d0d0");

    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("lore library");
        IReadOnlyList<LoreArticle> articles = LoreLibrary.Articles;
        check.That(articles.Count >= 17 && articles[0].Id == LoreLibrary.HomeId && articles[1].Id == "game-overview",
            "The front door comes first and its own link list sets the reading order.");
        string[] curated = LoreLibrary.Shelves.Where(shelf => shelf.Name != LoreLibrary.MoreShelf)
            .SelectMany(shelf => shelf.Entries).Select(entry => entry.Article.Id).ToArray();
        check.That(curated.Length >= 13 && curated.SequenceEqual(articles.Skip(1).Take(curated.Length).Select(article => article.Id)),
            "Curated articles follow the front door in its order; unlisted ones come after.");
        check.That(LoreLibrary.Shelves.Select(shelf => shelf.Name).SequenceEqual(["Start here", "How it was made", "What survived", LoreLibrary.MoreShelf]),
            "Shelves are the front door's own sections, then the articles it does not list.");
        check.That(articles.Skip(1).All(article => LoreLibrary.Shelves.Sum(shelf => shelf.Entries.Count(entry => entry.Article == article)) == 1),
            "Every article sits on exactly one shelf.");
        check.That(LoreLibrary.Shelves[0].Entries[0] is { Label: "The game" } first && first.Blurb.StartsWith("what it was", StringComparison.Ordinal),
            "A shelf entry carries the front door's short label and its description.");
        check.That(articles.All(article => !article.Markdown.Contains("- **Status:**", StringComparison.Ordinal)),
            "No reader sees a maintainer header.");
        check.That(LoreLibrary.StripHeader("# Title\n\n- **Status:** live record\n  continued\n- **Last updated:** 2026-08-22\n- **Summary:** what\n\nBody.\n")
            == "# Title\n\nBody.\n", "The header block beneath a title is removed, continuation lines included.");
        const string plainList = "# Plain\n\n- a bullet that is not a header block\n\nBody text.\n";
        const string laterStatus = "# Guide\n\nIntro paragraph.\n\n- **Status:** not a header here\n";
        check.That(LoreLibrary.StripHeader(plainList) == plainList && LoreLibrary.StripHeader(laterStatus) == laterStatus,
            "A document without a header block, or with a Status bullet after prose, is untouched.");

        check.That(LoreLibrary.Resolve(LoreLibrary.HomeId, "../lore/game-overview.md") == "lore:game-overview" &&
            LoreLibrary.Resolve("_index", "community-preservation.md#active-community-contacts") == "lore:community-preservation#active-community-contacts" &&
            LoreLibrary.Resolve("weapons", "#top") == "lore:weapons#top",
            "Links between articles, and to a section, stay in the reader.");
        check.That(LoreLibrary.Resolve("_index", "../reverse-engineering/RE-INDEX.md") == LoreLibrary.Repository + "reverse-engineering/RE-INDEX.md" &&
            LoreLibrary.Resolve("x", "https://example.org/a") == "https://example.org/a",
            "Other repository files open their public page; web links stay web links.");
        check.That(LoreLibrary.Resolve("weapons", "../../outside.md") is null && LoreLibrary.Resolve("weapons", "mailto:someone") is null,
            "A path above the repository or an unknown scheme is plain text.");

        // Render everything, then check every link lands on a real article and section.
        Dictionary<string, RenderedArticle> rendered = [];
        List<(string From, string Url)> links = [];
        List<string> unresolved = [];
        foreach (LoreArticle article in articles)
        {
            rendered[article.Id] = Markdown.Render(LoreLibrary.Compose(article, null), target =>
            {
                string? url = LoreLibrary.Resolve(article.Id, target);
                if (url is null) unresolved.Add($"{article.Id}: {target}");
                else links.Add((article.Id, url));
                return url;
            }, Style);
        }
        check.That(links.Count > 50 && unresolved.Count == 0, "Every link target in every article resolves: " + string.Join(", ", unresolved));
        List<string> broken = [];
        foreach ((string from, string url) in links.Where(link => link.Url.StartsWith("lore:", StringComparison.Ordinal)))
        {
            string[] parts = url[5..].Split('#', 2);
            if (!rendered.TryGetValue(parts[0], out RenderedArticle? target) || (parts.Length > 1 && !target.Anchors.ContainsKey(parts[1])))
                broken.Add($"{from} → {url}");
        }
        check.That(broken.Count == 0, "Every link between articles reaches its article and section: " + string.Join(", ", broken));
        foreach ((string id, RenderedArticle article) in rendered)
        {
            string outsideCode = CodeBlock().Replace(article.Bbcode, "");
            string[] unbalanced = new[] { "b", "i", "url", "code", "table", "cell", "ul", "ol", "indent", "color", "font_size" }
                .Where(tag => Regex.Count(article.Bbcode, $@"\[{tag}[\]= ]") != Regex.Count(article.Bbcode, $@"\[/{tag}\]")).ToArray();
            check.That(unbalanced.Length == 0, $"{id} renders balanced markup: {string.Join(", ", unbalanced)}");
            // An unparsed link would survive escaping as "[lb]label](target)".
            check.That(!outsideCode.Contains("**", StringComparison.Ordinal) && !UnparsedLink().IsMatch(outsideCode),
                $"{id} leaves no Markdown emphasis or link syntax behind");
            check.That(article.Headings.Count > 0 && article.Headings[0].Level == 1, $"{id} opens with its title");
        }

        check.Suite("lore rendering");
        RenderedArticle sample = Markdown.Render(
            "## Same\n\n**the `x_y` rule** and snake_case_word and _italic_ [b]not markup[/b]\n\n## Same\n\n<a id=\"here\"></a>\n\n" +
            "1. **One**\n   - sub a\n   - sub b\n\n2. Two\n\n| A | B |\n|---|---|\n| 1 | x \\| y |\n\n> **From**: A\n> **To**: B\n",
            _ => null, Style);
        check.That(sample.Bbcode.Contains("[b]the [color=#c0de00][code]x_y[/code][/color] rule[/b]") &&
            sample.Bbcode.Contains("snake_case_word and [i]italic[/i]"), "Emphasis spans code spans; underscores inside words stay text.");
        check.That(sample.Bbcode.Contains("[lb]b]not markup[lb]/b]"), "Brackets in article text are escaped, never markup.");
        check.That(sample.Anchors.ContainsKey("same") && sample.Anchors.ContainsKey("same-1") && sample.Anchors.ContainsKey("here"),
            "Repeated headings get GitHub's numbered anchors; HTML anchors are kept.");
        check.That(sample.Bbcode.Contains("[ol type=1]\u200B[b]One[/b]\n[ul]\u200Bsub a\n\u200Bsub b[/ul]\n\u200BTwo[/ol]"),
            "Nested and numbered lists keep their structure.");
        RenderedArticle prose = Markdown.Render("> **Note.** This is wrapped prose that goes on long enough to be a line\n" +
            "> of its own and then continues here.\n>\n> A second paragraph.\n\n> \"A quote.\"\n> — Someone", _ => null, Style);
        check.That(prose.Bbcode.Contains("be a line of its own") && prose.Bbcode.Contains("continues here.\nA second paragraph.") &&
            prose.Bbcode.Contains("\"A quote.\"\n— Someone"), "Wrapped quoted prose is joined; paragraphs and attributions keep their breaks.");
        check.That(sample.Bbcode.Contains("[table=2]") && sample.Bbcode.Contains("x | y"), "Tables keep escaped bars inside cells.");
        check.That(sample.Bbcode.Contains("[b]From[/b]: A\n[b]To[/b]: B"), "Quoted memo lines keep their line breaks.");
        check.That(Markdown.Slug("3. Planning Localization and Porting in Advance") == "3-planning-localization-and-porting-in-advance",
            "Anchors follow GitHub's heading slugs.");

        check.Suite("lore search and missions");
        IReadOnlyList<LoreHit> hits = LoreLibrary.Search("Kiralova");
        check.That(hits.All(hit => !hit.Snippet.Contains("|--", StringComparison.Ordinal) && !hit.Snippet.Contains("###", StringComparison.Ordinal) &&
            !hit.Snippet.Contains("> ", StringComparison.Ordinal)), "Search snippets read as text, without table or heading markup.");
        check.That(hits.Any(hit => hit.Article.Id == "characters") && hits.Any(hit => hit.Article.Id == "battle-engine-tech") &&
            hits.All(hit => hit.Snippet.Contains("Kiralova", StringComparison.OrdinalIgnoreCase)) &&
            hits.Zip(hits.Skip(1)).All(pair => pair.First.Matches >= pair.Second.Matches),
            "Search finds every article naming a phrase, most mentions first, with the mention in context.");
        check.That(LoreLibrary.Search("k").Count == 0 && LoreLibrary.Search("zzqqxxv").Count == 0, "Single letters and absent phrases find nothing.");

        LoreArticle campaign = LoreLibrary.Find("the-campaign")!;
        string missing = LoreLibrary.Compose(campaign, null);
        check.That(!missing.Contains("LIVE:CAMPAIGN", StringComparison.Ordinal) && missing.Contains("Choose your Battle Engine Aquila folder on Home"),
            "Without the game's text the mission list says how to find the game.");
        GameText? text = GameTextTests.LoadSample(Path.Combine(outputDirectory, "lore-text"));
        string composed = text is null ? "" : LoreLibrary.Compose(campaign, text.Levels);
        check.That(composed.Contains("Test Flight") && composed.Contains("harder version of the same map") &&
            composed.Contains($"There are {text?.Levels.Count} of them in your copy."), "With the game's text the mission list is the game's own names.");
    }

    [GeneratedRegex(@"\[code\].*?\[/code\]", RegexOptions.Singleline)]
    private static partial Regex CodeBlock();

    [GeneratedRegex(@"\[lb\][^\[\]]*\]\(")]
    private static partial Regex UnparsedLink();
}
