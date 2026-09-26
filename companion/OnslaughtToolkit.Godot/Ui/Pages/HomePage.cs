// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>The landing page: what the companion does and how it keeps your files safe.</summary>
internal sealed class HomePage : Page
{
    internal HomePage(Action openCareer) : base("home", "Home")
    {
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;
        (PanelContainer welcome, VBoxContainer body) = Build.Card("Battle Engine Aquila companion");
        body.Add(Build.Text("Inspect careers, change them in verified copies, compare saves and browse the game's media. " +
            "Everything works on copies of your files, and every copy is checked byte for byte."));
        HBoxContainer actions = body.Add(Build.Row(12));
        OpenCareer = actions.Add(Build.Button("Open a career…", "Primary", "Choose a .bes career save (Ctrl+O)."));
        OpenCareer.Pressed += openCareer;
        content.Add(welcome);
        (PanelContainer safety, VBoxContainer rules) = Build.Card("How your files stay safe");
        foreach (string rule in new[]
        {
            "Careers open read-only; the original is never modified.",
            "Changes go to a new file that is reopened and compared with the preview before it is offered.",
            "Existing files are never replaced by an edit, and nothing is deleted automatically.",
            "Each value shows how we know what it means: proven in the game, read from the game's code, or unproven.",
        })
        {
            rules.Add(Build.Text("—  " + rule, "Muted"));
        }
        content.Add(safety);
    }

    internal override Control Root { get; }
    internal override string Subtitle => "Careers, verified copies and the game's own media";
    internal Button OpenCareer { get; }
}
