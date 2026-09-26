// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>The left navigation: the emblem, grouped destinations and the active marker.</summary>
internal sealed class Sidebar
{
    private readonly Dictionary<string, Button> _items = [];

    internal Sidebar(IEnumerable<(string Group, IReadOnlyList<Page> Pages)> groups, Action<string> navigate)
    {
        Root = new PanelContainer { ThemeTypeVariation = "Sidebar", CustomMinimumSize = new Vector2(236, 0) };
        VBoxContainer column = Root.Add(Build.Margin(16, 20, 16, 16)).Add(Build.Column(2));
        HBoxContainer brand = column.Add(Build.Row(12));
        brand.Add(new Emblem { CustomMinimumSize = new Vector2(40, 40) });
        VBoxContainer words = brand.Add(Build.Column(0));
        words.Add(Build.Text("ONSLAUGHT", "Brand", wrap: false));
        words.Add(Build.Text("TOOLKIT", "BrandSub", wrap: false));
        column.Add(Build.Spacer(18));
        foreach ((string group, IReadOnlyList<Page> pages) in groups)
        {
            Label heading = column.Add(Build.Eyebrow(group));
            heading.CustomMinimumSize = new Vector2(0, 22);
            foreach (Page page in pages)
            {
                Button item = column.Add(Build.Button(page.Title, "Nav"));
                item.Alignment = HorizontalAlignment.Left;
                item.Name = "Nav" + page.Key;
                item.Pressed += () => navigate(page.Key);
                _items[page.Key] = item;
            }
            column.Add(Build.Spacer(12));
        }
        column.Add(Build.Spacer(0, expand: true));
        column.Add(Build.Text("Careers, verified copies and the game's own media.", "Faint"));
    }

    internal PanelContainer Root { get; }
    internal IReadOnlyDictionary<string, Button> Items => _items;

    internal void Select(string key)
    {
        foreach ((string itemKey, Button item) in _items)
            item.ThemeTypeVariation = itemKey == key ? "NavActive" : "Nav";
    }
}
