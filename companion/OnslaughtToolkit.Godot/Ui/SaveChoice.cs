// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

internal enum SaveTarget { NewCareer, Replace, Elsewhere }

/// <summary>
/// How a change is saved, asked in one dialog: as a new career in the game, in place of the file it came
/// from, or as a copy somewhere else. Game writes always back up first and never happen while the game
/// runs; the dialog says so before anything is chosen.
/// </summary>
internal sealed class SaveChoice
{
    private readonly AppServices _app;
    private readonly List<(PanelContainer Panel, CheckBox Radio, SaveTarget Target)> _choices = [];
    private readonly ButtonGroup _group = new();
    private readonly Label _replaceTitle, _replaceText, _note, _problem;
    private readonly HBoxContainer _nameRow;
    private Func<string, string?> _nameProblem = _ => null;

    internal SaveChoice(AppServices app)
    {
        _app = app;
        Dialog = app.Popups.Add(new ConfirmationDialog { Title = "Save your changes", OkButtonText = "Save", MinSize = new Vector2I(600, 0) });
        Dialog.GetLabel().Visible = false;
        Dialog.GetOkButton().ThemeTypeVariation = "Primary";
        VBoxContainer content = Dialog.Add(Build.Column(10));
        content.CustomMinimumSize = new Vector2(560, 0);

        (PanelContainer newPanel, VBoxContainer newBody, _, _) = Choice(SaveTarget.NewCareer, "Add to your game as a new career",
            "Your current careers stay as they are. The new career appears in the game's Load menu.");
        _nameRow = newBody.Add(Build.Row(10));
        _nameRow.Add(Build.Text("Name", "Muted", wrap: false, width: 60));
        Name = _nameRow.Add(new LineEdit { SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, MaxLength = 100 });
        Name.TextChanged += _ => Validate();
        // Enter in the name saves, as the Save button would (and only when it could).
        Dialog.RegisterTextEnter(Name);
        content.Add(newPanel);

        (PanelContainer replacePanel, _, _replaceTitle, _replaceText) = Choice(SaveTarget.Replace, "", "");
        content.Add(replacePanel);

        (PanelContainer elsewherePanel, _, _, _) = Choice(SaveTarget.Elsewhere, "Save a copy somewhere else…",
            "Nothing in your game changes. Useful for sharing, or to keep a copy of your own.");
        content.Add(elsewherePanel);

        _problem = content.Add(Build.Text("", "Bad"));
        _note = content.Add(Build.Text("", "Muted"));
        Dialog.Confirmed += () => Chosen?.Invoke(Target, Name.Text.Trim());
    }

    /// <summary>Raised when the player confirms: where to save, and the new career's name when that was chosen.</summary>
    internal event Action<SaveTarget, string>? Chosen;

    internal ConfirmationDialog Dialog { get; }
    internal LineEdit Name { get; }
    internal SaveTarget Target => _choices.FirstOrDefault(choice => choice.Radio.ButtonPressed).Target;

    /// <summary>Whether a choice that writes into the game is on offer and usable right now.</summary>
    internal bool InGameAvailable => _choices.Any(choice => choice.Target != SaveTarget.Elsewhere && choice.Panel.Visible && !choice.Radio.Disabled);

    /// <summary>Whether a choice is shown in the dialog.</summary>
    internal bool Offers(SaveTarget target) => _choices.Any(choice => choice.Target == target && choice.Panel.Visible);

    /// <summary>Shows the choices that apply: game choices need a game folder and a closed game; a copy elsewhere is always offered.</summary>
    /// <param name="replace">The file's name in the game, e.g. "Linux Test 1" or "the game's default settings"; null hides that choice.</param>
    internal void Open(string title, string? newName, string? replace, string replaceWhat, Func<string, string?>? nameProblem = null,
        bool elsewhere = true)
    {
        Dialog.Title = title;
        _nameProblem = nameProblem ?? (_ => null);
        bool game = _app.Game.Folder is not null;
        bool running = game && _app.GameRunning();
        Show(SaveTarget.NewCareer, newName is not null && game, !running);
        Show(SaveTarget.Replace, replace is not null && game, !running);
        Show(SaveTarget.Elsewhere, elsewhere, true);
        Name.Text = newName ?? "";
        _replaceTitle.Text = $"Replace {replace} in your game";
        _replaceText.Text = replaceWhat;
        // The first choice that can be used; if the game is running, the game choices show disabled.
        SaveTarget first = _choices.FirstOrDefault(choice => choice.Panel.Visible && !choice.Radio.Disabled,
            _choices.First(choice => choice.Panel.Visible)).Target;
        Select(first);
        _note.Text = running ? "Battle Engine Aquila is running. Close it to save into your game; a copy can still be saved elsewhere."
            : game ? $"Before anything in your game changes, every career and your settings are backed up to {_app.Backups.Folder}. " +
              "You can put them back from Backups at any time."
            : "Choose your game folder on Home to save into your game.";
        Validate();
        Dialog.PopupCentered();
        Name.CallDeferred(Control.MethodName.GrabFocus);
        FitToContent();
    }

    /// <summary>
    /// Wrapped text knows its height only once it is laid out, and a dialog grows to fit but never shrinks:
    /// fit the dialog to its content after the first layout, so it never runs off the window.
    /// </summary>
    private async void FitToContent()
    {
        for (int pass = 0; pass < 2; pass++)
        {
            await Dialog.ToSignal(Dialog.GetTree(), SceneTree.SignalName.ProcessFrame);
            if (!Dialog.Visible) return;
            Dialog.ResetSize();
        }
        Dialog.MoveToCenter();
    }

    internal void Select(SaveTarget target)
    {
        foreach ((PanelContainer panel, CheckBox radio, SaveTarget choice) in _choices)
        {
            radio.SetPressedNoSignal(choice == target);
            panel.ThemeTypeVariation = choice == target ? "ChoiceChosen" : "Choice";
        }
        _nameRow.Visible = target == SaveTarget.NewCareer;
        Dialog.OkButtonText = target switch
        {
            SaveTarget.NewCareer => "Back up and add",
            SaveTarget.Replace => "Back up and replace",
            _ => "Choose where…",
        };
        Validate();
    }

    private void Validate()
    {
        bool usable = _choices.Any(choice => choice.Radio.ButtonPressed && !choice.Radio.Disabled);
        string? problem = !usable ? "" : Target == SaveTarget.NewCareer ? _nameProblem(Name.Text.Trim()) : null;
        _problem.Text = problem ?? "";
        _problem.Visible = !string.IsNullOrEmpty(problem);
        Dialog.GetOkButton().Disabled = problem is not null;
    }

    private void Show(SaveTarget target, bool visible, bool enabled)
    {
        (PanelContainer panel, CheckBox radio, SaveTarget _) = _choices.First(choice => choice.Target == target);
        panel.Visible = visible;
        radio.Disabled = !enabled;
    }

    private (PanelContainer Panel, VBoxContainer Body, Label Title, Label Text) Choice(SaveTarget target, string title, string text)
    {
        (PanelContainer panel, VBoxContainer body) = Build.Panel("Choice", 6);
        HBoxContainer head = body.Add(Build.Row(8));
        CheckBox radio = head.Add(new CheckBox { ButtonGroup = _group, FocusMode = Control.FocusModeEnum.All });
        Label heading = head.Add(Build.Text(title, "Strong"));
        heading.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        Label description = body.Add(Build.Text(text, "Muted"));
        radio.Pressed += () => Select(target);
        panel.GuiInput += input =>
        {
            if (input is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left } && !radio.Disabled) Select(target);
        };
        _choices.Add((panel, radio, target));
        return (panel, body, heading, description);
    }
}
