// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The game's careers as cards with their progress and an Open button. Used on Home and wherever a career
/// is needed; away from Home it also offers to open a career file from anywhere.
/// </summary>
internal sealed class CareerCards
{
    private readonly AppServices _app;
    private readonly bool _onHome;
    private readonly List<Button> _open = [];

    internal CareerCards(AppServices app, bool onHome = false)
    {
        (_app, _onHome) = (app, onHome);
        Root = Build.Column(10);
    }

    internal VBoxContainer Root { get; }
    internal IReadOnlyList<Button> OpenButtons => _open;

    internal void Show()
    {
        Root.Clear();
        _open.Clear();
        if (_app.Game.Folder is not GameFolder folder)
        {
            Root.Add(Build.Text(_app.Game.Busy ? "Looking for your game…" : _onHome
                ? "Choose your game folder above to see your careers here." : "Choose your game folder on Home to see your careers here.", "Muted"));
            OfferFile();
            return;
        }
        if (folder.Careers.Count == 0)
        {
            Root.Add(Build.Text("No careers yet. Start a career in the game and save it; it appears here.", "Muted"));
            OfferFile();
            return;
        }
        string? open = _app.Workspace.Session?.Path;
        foreach (GameFile career in folder.Careers.OrderByDescending(file => file.Modified))
        {
            (PanelContainer card, VBoxContainer body) = Build.Panel("Inset", 6);
            HBoxContainer row = body.Add(Build.Row(16));
            VBoxContainer words = row.Add(Build.Column(4));
            words.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            Label name = words.Add(Build.Text(career.DisplayName, "CardTitle", wrap: false, clip: true));
            name.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            name.TooltipText = career.Path;
            if (career.Summary is CareerSummary summary)
            {
                words.Add(Build.Text($"{summary.MissionsDone} of {summary.MissionsUsed} missions  ·  " +
                    $"{summary.GoodiesEarned} of {summary.GoodiesShown} Goodies  ·  saved {Build.When(career.Modified)}", "Muted"));
                ProgressBar progress = words.Add(Build.Meter(summary.MissionsUsed == 0 ? 0 : summary.MissionsDone / (double)summary.MissionsUsed));
                progress.TooltipText = "Missions complete";
            }
            else
            {
                words.Add(Build.Text("This file can't be opened: " + (career.Problem ?? "unknown format"), "Warn"));
            }
            bool isOpen = string.Equals(open, career.Path, StringComparison.Ordinal);
            Button action = row.Add(Build.Button(isOpen ? "Viewing" : "Open", isOpen ? "" : "Primary", disabled: !career.Supported));
            action.SizeFlagsVertical = Control.SizeFlags.ShrinkCenter;
            action.TooltipText = isOpen ? "This career is open. Its pages are in the sidebar under Your career." : "Opens the career read-only.";
            string path = career.Path;
            action.Pressed += () =>
            {
                if (isOpen) _app.Navigate("summary");
                else _app.Status.Track(_app.OpenCareer(path));
            };
            _open.Add(action);
            Root.Add(card);
        }
        OfferFile();
    }

    /// <summary>Away from Home, a way to open a career kept anywhere else (Home has its own).</summary>
    private void OfferFile()
    {
        if (_onHome) return;
        Button file = Root.Add(Build.Button("Open a career file…", "Link", "Look at a career file anywhere on your computer, read-only."));
        file.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        file.Pressed += _app.OpenCareerFile;
    }
}
