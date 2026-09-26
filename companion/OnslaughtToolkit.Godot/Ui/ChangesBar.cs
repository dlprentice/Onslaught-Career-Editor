// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// A strip under a page that appears while the page has unsaved changes: how many, Save and Undo. It
/// stays in view however far the page is scrolled, so saving is never a hunt for a button.
/// </summary>
internal sealed class ChangesBar
{
    internal ChangesBar(string saveText)
    {
        Root = new PanelContainer { ThemeTypeVariation = "ChangesBar", Visible = false };
        HBoxContainer row = Root.Add(Build.Row(14));
        Summary = row.Add(Build.Text("", "Strong", wrap: false, clip: true));
        Summary.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        Summary.SizeFlagsVertical = Control.SizeFlags.ShrinkCenter;
        Undo = row.Add(Build.Button("Undo all changes", "Link"));
        Save = row.Add(Build.Button(saveText, "Primary"));
        Save.Icon = Icons.Get("save");
    }

    internal PanelContainer Root { get; }
    internal Label Summary { get; }
    internal Button Save { get; }
    internal Button Undo { get; }

    /// <summary>Shows the bar for this many unsaved changes, or hides it; <paramref name="ready"/> false disables its buttons.</summary>
    internal void Show(int changes, bool ready)
    {
        Root.Visible = changes > 0;
        Summary.Text = $"{Build.Count(changes, "change")} not saved yet. Nothing in your game changes until you save.";
        Save.Disabled = Undo.Disabled = !ready;
    }

    /// <summary>A page: its scroller above, the bar below.</summary>
    internal VBoxContainer Wrap(ScrollContainer scroll)
    {
        VBoxContainer page = Build.Column(10);
        scroll.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        page.Add(scroll);
        page.Add(Root);
        return page;
    }
}
