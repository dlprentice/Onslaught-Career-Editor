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

    /// <summary>Shows the bar for this many unsaved changes, or hides it, with Save and Undo enabled as given.</summary>
    internal void Show(int changes, bool canSave, bool canUndo)
    {
        Root.Visible = changes > 0;
        Summary.Text = $"{Build.Count(changes, "change")} not saved yet. Nothing in your game changes until you save.";
        Save.Disabled = !canSave;
        Undo.Disabled = !canUndo;
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

/// <summary>
/// "Show exactly what changes in the file": a link that opens the byte-level detail of the changes, offered
/// only while there are changes to show.
/// </summary>
internal sealed class FileDetails
{
    private const string ShowText = "Show exactly what changes in the file", HideText = "Hide the file details";

    internal FileDetails(VBoxContainer parent)
    {
        Toggle = parent.Add(Build.Button(ShowText, "Link"));
        Toggle.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        Toggle.Visible = false;
        Panel = parent.Add(Build.Detail("", bbcode: true));
        Panel.Visible = false;
        Toggle.Pressed += () =>
        {
            Panel.Visible = !Panel.Visible;
            Toggle.Text = Panel.Visible ? HideText : ShowText;
        };
    }

    internal Button Toggle { get; }
    internal RichTextLabel Panel { get; }

    /// <summary>Sets the detail to show, or closes and hides it all when there are no changes (null).</summary>
    internal void Show(string? bbcode)
    {
        Panel.Text = bbcode ?? "";
        Toggle.Visible = bbcode is not null;
        if (bbcode is not null) return;
        Panel.Visible = false;
        Toggle.Text = ShowText;
    }
}
