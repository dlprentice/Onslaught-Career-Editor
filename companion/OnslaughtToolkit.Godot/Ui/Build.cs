// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Small constructors that keep code-built layouts readable.</summary>
internal static class Build
{
    internal static T Add<T>(this Node parent, T child) where T : Node
    {
        parent.AddChild(child);
        return child;
    }

    internal static Label Text(string text, int fontSize = 0, Color? color = null, bool wrap = true)
    {
        Label label = new() { Text = text, AutowrapMode = wrap ? TextServer.AutowrapMode.WordSmart : TextServer.AutowrapMode.Off };
        if (fontSize > 0) label.AddThemeFontSizeOverride("font_size", fontSize);
        if (color is Color tint) label.AddThemeColorOverride("font_color", tint);
        return label;
    }

    internal static Label Fixed(string text, float width) =>
        new() { Text = text, CustomMinimumSize = new Vector2(width, 0) };

    internal static RichTextLabel Detail(string text, float minimumHeight) => new()
    {
        Text = text, FitContent = true, SelectionEnabled = true, ScrollActive = false,
        CustomMinimumSize = new Vector2(0, minimumHeight),
    };

    internal static Button Button(string text, string tooltip = "", bool disabled = false) =>
        new() { Text = text, TooltipText = tooltip, Disabled = disabled };

    internal static VBoxContainer Column(int separation)
    {
        VBoxContainer column = new();
        column.AddThemeConstantOverride("separation", separation);
        return column;
    }

    internal static HBoxContainer Row(int separation)
    {
        HBoxContainer row = new();
        row.AddThemeConstantOverride("separation", separation);
        return row;
    }

    internal static Tree Table(params string[] titles)
    {
        Tree tree = new()
        {
            Columns = titles.Length, ColumnTitlesVisible = true, HideRoot = true,
            SelectMode = Tree.SelectModeEnum.Row, SizeFlagsVertical = Control.SizeFlags.ExpandFill,
        };
        for (int column = 0; column < titles.Length; column++) tree.SetColumnTitle(column, titles[column]);
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

    /// <summary>A filesystem dialog that cannot delete, create folders or offer to overwrite.</summary>
    internal static FileDialog FilePicker(string title, FileDialog.FileModeEnum mode, params string[] filters) => new()
    {
        Title = title, FileMode = mode, Access = Godot.FileDialog.AccessEnum.Filesystem, Filters = filters,
        Size = new Vector2I(840, 560), DeletingEnabled = false, FolderCreationEnabled = false,
        OverwriteWarningEnabled = false, RecentListEnabled = false, FavoritesEnabled = false,
    };
}
