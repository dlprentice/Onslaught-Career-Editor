// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Small constructors that keep code-built layouts readable. Styling comes only from the theme.</summary>
internal static class Build
{
    internal static T Add<T>(this Node parent, T child) where T : Node
    {
        parent.AddChild(child);
        return child;
    }

    /// <summary>Detaches and frees every child at once, so a rebuilt list never shows stale rows.</summary>
    internal static void Clear(this Node parent)
    {
        foreach (Node child in parent.GetChildren())
        {
            parent.RemoveChild(child);
            child.QueueFree();
        }
    }

    /// <summary>A label using one of the theme's label variations (Title, Section, Eyebrow, Muted, Mono…).</summary>
    /// <param name="clip">Trim with an ellipsis instead of growing; give the label room (ExpandFill or a width).</param>
    internal static Label Text(string text, string variation = "", bool wrap = true, float width = 0, bool clip = false)
    {
        Label label = new()
        {
            Text = text, ThemeTypeVariation = variation,
            AutowrapMode = wrap ? TextServer.AutowrapMode.WordSmart : TextServer.AutowrapMode.Off,
            CustomMinimumSize = new Vector2(width, 0), VerticalAlignment = VerticalAlignment.Center,
        };
        if (clip) label.TextOverrunBehavior = TextServer.OverrunBehavior.TrimEllipsis;
        return label;
    }

    /// <summary>Shows a path in a one-line field with its file name in view and the whole path as a tooltip.</summary>
    internal static void ShowPath(LineEdit field, string path)
    {
        field.Text = path;
        field.TooltipText = path;
        field.CaretColumn = path.Length;
    }

    /// <summary>A time as a player would say it: "today 14:32", "yesterday 09:10", "6 Sep 2026".</summary>
    internal static string When(DateTime time)
    {
        if (time == default) return "at an unknown time";
        DateTime today = DateTime.Today;
        if (time.Date == today) return $"today {time:HH:mm}";
        if (time.Date == today.AddDays(-1)) return $"yesterday {time:HH:mm}";
        return time.Year == today.Year ? time.ToString("d MMM") : time.ToString("d MMM yyyy");
    }

    /// <summary>"1 voice line", "2,340 voice lines".</summary>
    internal static string Count(int count, string singular, string? plural = null) =>
        $"{count:N0} {(count == 1 ? singular : plural ?? singular + "s")}";

    /// <summary>Spaced capitals for headings, the Flight-deck signature.</summary>
    internal static Label Heading(string text, string variation = "Section") =>
        Text(text.ToUpperInvariant(), variation, wrap: false);

    internal static Label Eyebrow(string text) => Text(text.ToUpperInvariant(), "Eyebrow", wrap: false);

    internal static RichTextLabel Detail(string text, float minimumHeight = 0, bool bbcode = false) => new()
    {
        Text = text, BbcodeEnabled = bbcode, FitContent = true, SelectionEnabled = true, ScrollActive = false,
        CustomMinimumSize = new Vector2(0, minimumHeight), SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
    };

    internal static Button Button(string text, string variation = "", string tooltip = "", bool disabled = false) =>
        new() { Text = text, ThemeTypeVariation = variation, TooltipText = tooltip, Disabled = disabled };

    internal static VBoxContainer Column(int separation = 12)
    {
        VBoxContainer column = new();
        column.AddThemeConstantOverride("separation", separation);
        return column;
    }

    internal static HBoxContainer Row(int separation = 12)
    {
        HBoxContainer row = new();
        row.AddThemeConstantOverride("separation", separation);
        return row;
    }

    internal static MarginContainer Margin(int left, int top, int right, int bottom)
    {
        MarginContainer margin = new();
        margin.AddThemeConstantOverride("margin_left", left);
        margin.AddThemeConstantOverride("margin_top", top);
        margin.AddThemeConstantOverride("margin_right", right);
        margin.AddThemeConstantOverride("margin_bottom", bottom);
        return margin;
    }

    /// <summary>A themed panel (Card, Inset, Notice, CautionNotice…) holding a column.</summary>
    internal static (PanelContainer Panel, VBoxContainer Body) Panel(string variation = "Card", int separation = 10)
    {
        PanelContainer panel = new() { ThemeTypeVariation = variation };
        VBoxContainer body = panel.Add(Column(separation));
        return (panel, body);
    }

    /// <summary>A card with a spaced-capital heading.</summary>
    internal static (PanelContainer Panel, VBoxContainer Body) Card(string heading, int separation = 10)
    {
        (PanelContainer panel, VBoxContainer body) = Panel("Card", separation);
        body.Add(Heading(heading));
        return (panel, body);
    }

    /// <summary>A callout: Notice (information), CautionNotice (game write), FailureNotice, SuccessNotice.</summary>
    internal static (PanelContainer Panel, Label Text) Notice(string text, string variation = "Notice")
    {
        PanelContainer panel = new() { ThemeTypeVariation = variation };
        Label label = panel.Add(Text(text));
        return (panel, label);
    }

    /// <summary>A vertical page scroller whose content fills the width.</summary>
    internal static (ScrollContainer Scroll, VBoxContainer Content) Scroller(int separation = 16)
    {
        ScrollContainer scroll = new()
        {
            HorizontalScrollMode = ScrollContainer.ScrollMode.Disabled, FollowFocus = true,
            SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, SizeFlagsVertical = Control.SizeFlags.ExpandFill,
        };
        // A right margin keeps cards clear of the scroll bar.
        MarginContainer gutter = scroll.Add(Margin(0, 0, 14, 0));
        gutter.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        VBoxContainer content = gutter.Add(Column(separation));
        content.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        return (scroll, content);
    }

    internal static Control Spacer(float height = 0, bool expand = false) => new()
    {
        CustomMinimumSize = new Vector2(0, height), MouseFilter = Control.MouseFilterEnum.Ignore,
        SizeFlagsVertical = expand ? Control.SizeFlags.ExpandFill : Control.SizeFlags.Fill,
        SizeFlagsHorizontal = expand ? Control.SizeFlags.ExpandFill : Control.SizeFlags.Fill,
    };

    internal static Tree Table(params string[] titles)
    {
        Tree tree = new()
        {
            Columns = titles.Length, ColumnTitlesVisible = true, HideRoot = true,
            SelectMode = Tree.SelectModeEnum.Row, SizeFlagsVertical = Control.SizeFlags.ExpandFill,
        };
        for (int column = 0; column < titles.Length; column++) tree.SetColumnTitle(column, titles[column].ToUpperInvariant());
        return tree;
    }

    internal static TreeItem TableRow(Tree tree, TreeItem? parent, params string[] cells)
    {
        TreeItem item = tree.CreateItem(parent);
        for (int column = 0; column < cells.Length; column++)
        {
            item.SetText(column, cells[column]);
            item.SetTooltipText(column, cells[column]);
        }
        return item;
    }

    internal static ProgressBar Meter(double fraction, bool accent = false) => new()
    {
        MinValue = 0, MaxValue = 1, Value = Math.Clamp(fraction, 0, 1), ShowPercentage = false,
        ThemeTypeVariation = accent ? "AccentBar" : "", CustomMinimumSize = new Vector2(0, 6),
        SizeFlagsVertical = Control.SizeFlags.ShrinkCenter,
    };

    /// <summary>A filesystem dialog that cannot delete, create folders or offer to overwrite.</summary>
    internal static FileDialog FilePicker(string title, FileDialog.FileModeEnum mode, params string[] filters) => new()
    {
        Title = title, ModeOverridesTitle = false, FileMode = mode, Access = Godot.FileDialog.AccessEnum.Filesystem, Filters = filters,
        Size = new Vector2I(860, 580), DeletingEnabled = false, FolderCreationEnabled = false,
        OverwriteWarningEnabled = false, RecentListEnabled = false, FavoritesEnabled = false,
    };
}
