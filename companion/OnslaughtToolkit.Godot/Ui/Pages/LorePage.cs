// SPDX-License-Identifier: MIT
using System.Text;
using Godot;
using OnslaughtCareerEditor.AppCore;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Lore;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The offline lore reader: the front door's shelves with the open article's sections, search across
/// every article, Back, Forward and Home, and links between articles. Links into the repository open
/// its public pages in the browser. The campaign's mission list is read from the player's own game.
/// </summary>
internal sealed class LorePage : Page
{
    /// <summary>The widest the text column grows; wider windows keep a comfortable line length.</summary>
    internal const float Measure = 860;

    private sealed record Visit(string Id, double Scroll);

    private readonly GameLibrary _game;
    private readonly StatusLine _status;
    private readonly Action<string> _openUrl;
    private readonly List<Visit> _back = [], _forward = [];
    private readonly Dictionary<string, string> _labels = [];
    private readonly LoreStyle _style = new(Palette.Data.ToHtml(false), Palette.Quote.ToHtml(false), Palette.Border.ToHtml(false),
        Palette.Raised.ToHtml(false));
    private readonly Label _shelf;
    private readonly PanelContainer _resultsPanel;
    private string _query = "";
    private bool _syncing;

    internal LorePage(GameLibrary game, StatusLine status, Action<string> openUrl) : base("lore", "Lore")
    {
        (_game, _status, _openUrl) = (game, status, openUrl);
        foreach (LoreShelf shelf in LoreLibrary.Shelves)
            foreach (LoreEntry entry in shelf.Entries) _labels[entry.Article.Id] = entry.Label;
        _labels[LoreLibrary.HomeId] = "Onslaught Lore";

        HBoxContainer layout = Build.Row(18);
        layout.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = layout;

        VBoxContainer left = layout.Add(Build.Column(10));
        left.CustomMinimumSize = new Vector2(280, 0);
        Search = left.Add(new LineEdit { PlaceholderText = "Search the lore", ClearButtonEnabled = true });
        Search.TextChanged += _ => ShowSearch();
        Library = left.Add(new Tree { HideRoot = true, SelectMode = Tree.SelectModeEnum.Row, SizeFlagsVertical = Control.SizeFlags.ExpandFill });
        Library.ItemSelected += OnLibrarySelected;
        (_resultsPanel, VBoxContainer results) = Build.Panel("Inset", 0);
        _resultsPanel.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        _resultsPanel.Visible = false;
        left.Add(_resultsPanel);
        Results = results.Add(new RichTextLabel
        {
            BbcodeEnabled = true, ScrollActive = true, SizeFlagsVertical = Control.SizeFlags.ExpandFill, MetaUnderlined = false,
        });
        Results.MetaClicked += meta => OpenHit(meta.AsString());

        VBoxContainer right = layout.Add(Build.Column(10));
        right.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        HBoxContainer toolbar = right.Add(Build.Row(8));
        BackButton = toolbar.Add(Build.Button("‹  Back", tooltip: "The article you were reading before this one (Alt+Left).", disabled: true));
        ForwardButton = toolbar.Add(Build.Button("Forward  ›", tooltip: "Return to where you went Back from (Alt+Right).", disabled: true));
        HomeButton = toolbar.Add(Build.Button("Home", tooltip: "The front door: what this is and where to start."));
        toolbar.Add(Build.Spacer(expand: true));
        _shelf = toolbar.Add(Build.Eyebrow(""));
        _shelf.SizeFlagsVertical = Control.SizeFlags.ShrinkCenter;
        (PanelContainer page, VBoxContainer body) = Build.Panel("Card", 0);
        page.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        right.Add(page);
        Reader = body.Add(new RichTextLabel
        {
            BbcodeEnabled = true, ScrollActive = true, SelectionEnabled = true, MetaUnderlined = true,
            SizeFlagsVertical = Control.SizeFlags.ExpandFill, SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
        });
        Reader.MetaClicked += meta => Follow(meta.AsString());
        Reader.MetaHoverStarted += meta => Reader.TooltipText = IsWeb(meta.AsString()) ? "Opens in your browser: " + meta.AsString() : "";
        Reader.MetaHoverEnded += _ => Reader.TooltipText = "";
        Reader.Resized += FitMeasure;

        BackButton.Pressed += Back;
        ForwardButton.Pressed += Forward;
        HomeButton.Pressed += () => Open(LoreLibrary.HomeId);
        _game.Changed += () =>
        {
            // The campaign article's mission list comes from the game's text; redraw it in place.
            if (!_game.Busy && Current is LoreArticle article && CampaignLoreComposer.WantsMissionList(article.Markdown))
                Show(article, scroll: Reader.GetVScrollBar().Value);
        };
    }

    internal override Control Root { get; }
    internal override string Subtitle => Current is null ? "The project's record of the game, its war and the people who made it"
        : $"{LabelOf(Current.Id)}  ·  about {Math.Max(1, (int)Math.Round(Words / 230.0))} min read";
    internal LineEdit Search { get; }
    internal Tree Library { get; }
    internal RichTextLabel Results { get; }
    internal RichTextLabel Reader { get; }
    internal Button BackButton { get; }
    internal Button ForwardButton { get; }
    internal Button HomeButton { get; }
    internal LoreArticle? Current { get; private set; }
    internal RenderedArticle? Rendered { get; private set; }
    internal int Words { get; private set; }

    internal override void Refresh()
    {
        if (Current is null) Open(LoreLibrary.HomeId, remember: false);
    }

    /// <summary>Opens an article, optionally at an anchor or at its first mention of a search phrase.</summary>
    internal void Open(string id, string? anchor = null, string? mention = null, bool remember = true)
    {
        if (LoreLibrary.Find(id) is not LoreArticle article)
        {
            _status.Show("That lore article is not part of this build.", StatusKind.Failure);
            return;
        }
        if (article == Current && anchor is not null)
        {
            ScrollTo(Rendered!.Anchors.TryGetValue(anchor, out int target) ? target : 0);
            return;
        }
        if (remember && Current is not null && article != Current)
        {
            _back.Add(new Visit(Current.Id, Reader.GetVScrollBar().Value));
            _forward.Clear();
        }
        Show(article);
        int? paragraph = anchor is not null && Rendered!.Anchors.TryGetValue(anchor, out int at) ? at
            : mention is not null ? Rendered!.FirstMention(mention) : null;
        ScrollTo(paragraph ?? 0);
    }

    internal void Back() => Step(_back, _forward);

    internal void Forward() => Step(_forward, _back);

    /// <summary>A link in an article: another article opens here; a web page opens in the browser.</summary>
    internal void Follow(string url)
    {
        if (url.StartsWith("lore:", StringComparison.Ordinal))
        {
            string[] parts = url[5..].Split('#', 2);
            Open(parts[0], parts.Length > 1 ? parts[1] : null);
        }
        else if (IsWeb(url))
        {
            _openUrl(url);
            _status.Show($"Opened {new Uri(url).Host} in your browser.", StatusKind.Info);
        }
    }

    private void Step(List<Visit> from, List<Visit> to)
    {
        if (from.Count == 0 || Current is null || LoreLibrary.Find(from[^1].Id) is not LoreArticle article) return;
        Visit visit = from[^1];
        from.RemoveAt(from.Count - 1);
        to.Add(new Visit(Current.Id, Reader.GetVScrollBar().Value));
        Show(article, scroll: visit.Scroll);
    }

    private void Show(LoreArticle article, double scroll = 0)
    {
        Current = article;
        string markdown = LoreLibrary.Compose(article, _game.Text?.Levels);
        Rendered = Markdown.Render(markdown, target => LoreLibrary.Resolve(article.Id, target), _style);
        Words = Markdown.Plain(markdown).Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries).Length;
        Reader.Text = Rendered.Bbcode;
        _shelf.Text = (LoreLibrary.Shelves.FirstOrDefault(shelf => shelf.Entries.Any(entry => entry.Article == article))?.Name ??
            "Front door").ToUpperInvariant();
        BackButton.Disabled = _back.Count == 0;
        ForwardButton.Disabled = _forward.Count == 0;
        ShowLibrary();
        Callable.From(() => Reader.GetVScrollBar().Value = scroll).CallDeferred();
        HeaderChanged?.Invoke();
    }

    private void ScrollTo(int paragraph) => Callable.From(() => Reader.ScrollToParagraph(paragraph)).CallDeferred();

    private void ShowLibrary()
    {
        _syncing = true;
        Library.Clear();
        TreeItem root = Library.CreateItem();
        if (LoreLibrary.Home is LoreArticle home) Entry(root, home, _labels[home.Id], "What this is, the shelves, and where to start.");
        foreach (LoreShelf shelf in LoreLibrary.Shelves)
        {
            TreeItem group = Library.CreateItem(root);
            group.SetText(0, shelf.Name.ToUpperInvariant());
            group.SetSelectable(0, false);
            group.SetCustomColor(0, Palette.Accent);
            group.SetCustomFont(0, CompanionTheme.HeadingFont);
            group.SetCustomFontSize(0, 11);
            foreach (LoreEntry entry in shelf.Entries) Entry(group, entry.Article, entry.Label, entry.Blurb);
        }
        _syncing = false;
    }

    private void Entry(TreeItem parent, LoreArticle article, string label, string blurb)
    {
        TreeItem item = Library.CreateItem(parent);
        item.SetText(0, label);
        item.SetTooltipText(0, blurb.Length > 0 ? blurb : article.Title);
        item.SetMetadata(0, article.Id);
        if (article != Current || Rendered is null) return;
        // The open article lists its sections beneath it, as an outline.
        foreach (LoreHeading heading in Rendered.Headings.Where(heading => heading.Level == 2))
        {
            TreeItem section = Library.CreateItem(item);
            section.SetText(0, heading.Text);
            section.SetTooltipText(0, heading.Text);
            section.SetMetadata(0, article.Id + "#" + heading.Anchor);
            section.SetCustomColor(0, Palette.Muted);
        }
        Library.SetSelected(item, 0);
        Library.ScrollToItem(item);
    }

    private void OnLibrarySelected()
    {
        if (_syncing || Library.GetSelected()?.GetMetadata(0).AsString() is not string target || target.Length == 0) return;
        string[] parts = target.Split('#', 2);
        Open(parts[0], parts.Length > 1 ? parts[1] : null);
    }

    private void ShowSearch()
    {
        _query = Search.Text.Trim();
        bool searching = _query.Length >= 2;
        Library.Visible = !searching;
        _resultsPanel.Visible = searching;
        if (!searching) return;
        IReadOnlyList<LoreHit> hits = LoreLibrary.Search(_query);
        string muted = Palette.Muted.ToHtml(false), faint = Palette.Faint.ToHtml(false);
        StringBuilder text = new();
        if (hits.Count == 0)
        {
            text.Append($"[color=#{muted}]No article mentions “{Escape(_query)}”. Try another word, or clear the search.[/color]");
        }
        else
        {
            text.Append($"[color=#{muted}]{hits.Count} {(hits.Count == 1 ? "article mentions" : "articles mention")} “{Escape(_query)}”[/color]\n\n");
            foreach (LoreHit hit in hits)
            {
                text.Append($"[url=hit:{hit.Article.Id}][b]{Escape(LabelOf(hit.Article.Id))}[/b][/url]  ")
                    .Append($"[color=#{faint}]{hit.Matches} {(hit.Matches == 1 ? "mention" : "mentions")}[/color]\n")
                    .Append($"[color=#{muted}]{Highlight(hit.Snippet, _query)}[/color]\n\n");
            }
        }
        Results.Text = text.ToString().TrimEnd('\n');
    }

    private void OpenHit(string meta)
    {
        if (meta.StartsWith("hit:", StringComparison.Ordinal)) Open(meta[4..], mention: _query);
    }

    /// <summary>Keeps the text column readable in a wide window; the scroll bar stays at the card's edge.</summary>
    private void FitMeasure()
    {
        float spare = Math.Max(0, Reader.Size.X - Measure - 16);
        Reader.AddThemeStyleboxOverride("normal", new StyleBoxEmpty { ContentMarginLeft = spare / 2, ContentMarginRight = 16 + spare / 2 });
    }

    private string LabelOf(string id) => _labels.GetValueOrDefault(id) ?? LoreLibrary.Find(id)?.Title ?? id;

    private static bool IsWeb(string url) =>
        url.StartsWith("https://", StringComparison.OrdinalIgnoreCase) || url.StartsWith("http://", StringComparison.OrdinalIgnoreCase);

    private static string Escape(string text) => text.Replace("[", "[lb]");

    private static string Highlight(string snippet, string term)
    {
        StringBuilder output = new();
        string accent = Palette.Accent.ToHtml(false);
        int at = 0;
        for (int found = snippet.IndexOf(term, StringComparison.OrdinalIgnoreCase); found >= 0;
            found = snippet.IndexOf(term, at, StringComparison.OrdinalIgnoreCase))
        {
            output.Append(Escape(snippet[at..found])).Append($"[color=#{accent}]{Escape(snippet.Substring(found, term.Length))}[/color]");
            at = found + term.Length;
        }
        return output.Append(Escape(snippet[at..])).ToString();
    }
}
