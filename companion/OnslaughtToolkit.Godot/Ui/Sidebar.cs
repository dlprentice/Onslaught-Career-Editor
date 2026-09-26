// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>One sidebar group: a heading and its pages. A folding group starts closed and opens on demand.</summary>
internal sealed record NavGroup(string Heading, IReadOnlyList<Page> Pages, bool Folds = false);

/// <summary>The left navigation: the emblem, grouped destinations with icons, and the active marker.</summary>
internal sealed class Sidebar
{
    private readonly Dictionary<string, Button> _items = [];
    private readonly Dictionary<string, (Button Heading, VBoxContainer Items)> _folds = [];

    internal Sidebar(IEnumerable<NavGroup> groups, Action<string> navigate)
    {
        Root = new PanelContainer { ThemeTypeVariation = "Sidebar", CustomMinimumSize = new Vector2(232, 0) };
        VBoxContainer column = Root.Add(Build.Margin(14, 20, 14, 16)).Add(Build.Column(2));
        HBoxContainer brand = column.Add(Build.Margin(4, 0, 0, 0)).Add(Build.Row(12));
        brand.Add(new Emblem { CustomMinimumSize = new Vector2(40, 40) });
        VBoxContainer words = brand.Add(Build.Column(0));
        words.Add(Build.Text("ONSLAUGHT", "Brand", wrap: false));
        words.Add(Build.Text("TOOLKIT", "BrandSub", wrap: false));
        column.Add(Build.Spacer(18));
        // The destinations scroll when the window is too short for them all, so the sidebar never pushes
        // the status bar off the bottom of the window.
        ScrollContainer scroll = column.Add(new ScrollContainer
        {
            HorizontalScrollMode = ScrollContainer.ScrollMode.Disabled, FollowFocus = true,
            SizeFlagsVertical = Control.SizeFlags.ExpandFill,
        });
        VBoxContainer nav = scroll.Add(Build.Column(2));
        nav.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        foreach (NavGroup group in groups)
        {
            VBoxContainer items = Build.Column(2);
            if (group.Folds)
            {
                Button heading = nav.Add(Build.Button(group.Heading.ToUpperInvariant(), "NavGroup"));
                heading.Icon = Icons.Get("right");
                heading.Alignment = HorizontalAlignment.Left;
                heading.TooltipText = "Tools for comparing files and reading raw values.";
                heading.Pressed += () => Fold(group.Heading, !items.Visible);
                items.Visible = false;
                _folds[group.Heading] = (heading, items);
            }
            else if (group.Heading.Length > 0)
            {
                Label heading = nav.Add(Build.Margin(8, 0, 0, 0)).Add(Build.Eyebrow(group.Heading));
                heading.CustomMinimumSize = new Vector2(0, 22);
            }
            nav.Add(items);
            foreach (Page page in group.Pages)
            {
                Button item = items.Add(Build.Button(page.Title, "Nav"));
                item.Icon = Icons.Get(page.Icon);
                item.Alignment = HorizontalAlignment.Left;
                item.Name = "Nav" + page.Key;
                item.Pressed += () => navigate(page.Key);
                _items[page.Key] = item;
            }
            nav.Add(Build.Spacer(12));
        }
        column.Add(Build.Margin(4, 8, 0, 0)).Add(Build.Text("A companion for Battle Engine Aquila", "Faint"));
    }

    internal PanelContainer Root { get; }
    internal IReadOnlyDictionary<string, Button> Items => _items;

    /// <summary>Marks the active page, opening its group if it folds.</summary>
    internal void Select(string key)
    {
        foreach ((string itemKey, Button item) in _items)
            item.ThemeTypeVariation = itemKey == key ? "NavActive" : "Nav";
        foreach ((string heading, (Button _, VBoxContainer items)) in _folds)
        {
            if (_items.TryGetValue(key, out Button? active) && active.GetParent() == items) Fold(heading, true);
        }
    }

    internal bool IsOpen(string heading) => _folds.TryGetValue(heading, out var fold) && fold.Items.Visible;

    internal void Fold(string heading, bool open)
    {
        if (!_folds.TryGetValue(heading, out var fold)) return;
        fold.Items.Visible = open;
        fold.Heading.Icon = Icons.Get(open ? "down" : "right");
    }
}
