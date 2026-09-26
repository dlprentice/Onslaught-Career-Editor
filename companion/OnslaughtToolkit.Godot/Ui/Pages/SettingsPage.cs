// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The game's settings: audio, controls, mouse, screen shape and keys. The game keeps them in its default
/// settings file and in every career (loading a career copies that career over the defaults), so the
/// player picks which to change. Files open read-only; saving into the game backs up first and only
/// replaces a file the game has not changed since it was opened.
/// </summary>
internal sealed class SettingsPage : Page
{
    private readonly AppServices _app;
    private readonly Label _empty, _rawLine, _resultText;
    private readonly VBoxContainer _changes;
    private readonly FileDetails _details;
    private readonly PanelContainer _result;
    private readonly List<Control> _needsFile = [];
    private readonly HSlider _sound, _music;
    private readonly Label _soundValue, _musicValue;
    private readonly CheckBox[] _flight = new CheckBox[2], _walker = new CheckBox[2], _vibration = new CheckBox[2];
    private readonly OptionButton[] _presets = new OptionButton[2];
    private readonly OptionButton _sensitivity, _shape;
    private readonly Dictionary<(int EntryId, int Slot), Button> _keyButtons = [];
    private readonly List<string> _sourcePaths = [];
    private readonly SaveChoice _saveChoice;
    private readonly ScrollContainer _scroll;
    private SaveSession? _file;
    private OptionsReading? _reading;
    private OptionsEdit _edit = new();
    private Outcome<OptionsPlan> _plan = Outcome<OptionsPlan>.Refusal("No changes yet.");
    private (int EntryId, int Slot)? _capturing;
    private bool _loading;

    internal SettingsPage(AppServices app) : base("settings", "Game settings", "settings")
    {
        _app = app;
        (_scroll, VBoxContainer content) = Build.Scroller();
        Bar = new ChangesBar("Save settings…");
        Root = Bar.Wrap(_scroll);

        (PanelContainer which, VBoxContainer whichBody) = Build.Card("Which settings");
        whichBody.Add(Build.Text("The game starts with its default settings. Each career also keeps its own, and loading a career " +
            "in the game uses that career's settings from then on. Pick the one to change.", "Muted"));
        HBoxContainer sourceRow = whichBody.Add(Build.Row(10));
        Source = sourceRow.Add(new OptionButton { CustomMinimumSize = new Vector2(360, 0) });
        Source.ItemSelected += item => OpenSelected((int)item);
        OpenOther = sourceRow.Add(Build.Button("Open a settings file…", "Link", "Look at any .bea or .bes file's settings, read-only."));
        _rawLine = whichBody.Add(Build.Text("", "Faint"));
        content.Add(which);
        _empty = content.Add(Build.Text("Choose your game folder on Home, or open a settings file, to change settings.", "Muted"));

        (PanelContainer audio, VBoxContainer audioBody) = Build.Card("Sound");
        (_sound, _soundValue) = Slider(audioBody, "Sound effects");
        (_music, _musicValue) = Slider(audioBody, "Music");
        _needsFile.Add(content.Add(audio));

        (PanelContainer controls, VBoxContainer controlBody) = Build.Card("Controls");
        GridContainer grid = controlBody.Add(new GridContainer { Columns = 5 });
        grid.AddThemeConstantOverride("h_separation", 20);
        grid.AddThemeConstantOverride("v_separation", 8);
        foreach (string heading in new[] { "", "Invert flight", "Invert walking", "Vibration", "Controller layout" })
            grid.Add(Build.Eyebrow(heading));
        for (int player = 0; player < 2; player++)
        {
            grid.Add(Build.Text($"Player {player + 1}", "Strong", wrap: false));
            _flight[player] = grid.Add(new CheckBox());
            _walker[player] = grid.Add(new CheckBox());
            _vibration[player] = grid.Add(new CheckBox());
            _presets[player] = grid.Add(new OptionButton { CustomMinimumSize = new Vector2(130, 0) });
            for (int preset = 1; preset <= 4; preset++) _presets[player].AddItem($"Layout {preset}", preset);
            foreach (BaseButton toggle in new BaseButton[] { _flight[player], _walker[player], _vibration[player] })
                toggle.Toggled += _ => Changed();
            _presets[player].ItemSelected += _ => Changed();
        }
        controlBody.Add(Build.Text("The four layouts are the game's own controller presets; the game's Controller Options show " +
            "what each one does.", "Faint"));
        _needsFile.Add(content.Add(controls));

        (PanelContainer mouse, VBoxContainer mouseBody) = Build.Card("Mouse and screen");
        HBoxContainer sensitivityRow = mouseBody.Add(Build.Row(10));
        sensitivityRow.Add(Build.Text("Mouse sensitivity", "Muted", wrap: false, width: 160));
        _sensitivity = sensitivityRow.Add(new OptionButton { CustomMinimumSize = new Vector2(160, 0) });
        _sensitivity.ItemSelected += _ => Changed();
        HBoxContainer shapeRow = mouseBody.Add(Build.Row(10));
        shapeRow.Add(Build.Text("Screen shape", "Muted", wrap: false, width: 160));
        _shape = shapeRow.Add(new OptionButton { CustomMinimumSize = new Vector2(160, 0) });
        _shape.ItemSelected += _ => Changed();
        mouseBody.Add(Build.Text("Sensitivity uses the game's own slider steps, 3 to 63.", "Faint"));
        _needsFile.Add(content.Add(mouse));

        (PanelContainer keys, VBoxContainer keyBody) = Build.Card("Keyboard");
        keyBody.Add(Build.Text("Click a key, then press the key you want (Esc cancels). Controller and mouse buttons stay as they are " +
            "unless you replace them with a key.", "Muted"));
        GridContainer keyGrid = keyBody.Add(new GridContainer { Columns = 3 });
        keyGrid.AddThemeConstantOverride("h_separation", 16);
        keyGrid.AddThemeConstantOverride("v_separation", 6);
        foreach (string heading in new[] { "Action", "Player 1", "Player 2" }) keyGrid.Add(Build.Eyebrow(heading));
        foreach (BindingAction action in OptionsFile.Actions)
        {
            keyGrid.Add(Build.Text($"{action.Group} · {action.Name}", "", wrap: false, width: 220));
            for (int slot = 0; slot < 2; slot++)
            {
                (int, int) key = (action.EntryId, slot);
                Button button = keyGrid.Add(Build.Button("—"));
                button.CustomMinimumSize = new Vector2(220, 0);
                button.Pressed += () => StartCapture(key.Item1, key.Item2);
                button.GuiInput += input => OnKeyInput(input, button);
                _keyButtons[key] = button;
            }
        }
        UndoKeys = keyBody.Add(Build.Button("Undo key changes", "Link"));
        UndoKeys.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        UndoKeys.Pressed += () =>
        {
            _edit.Keys.Clear();
            ShowKeys();
            Refresh();
        };
        keyBody.Add(Build.Text("A new Transform key was seen working in the game; the other keys are stored the same way.", "Faint"));
        _needsFile.Add(content.Add(keys));

        (PanelContainer summary, VBoxContainer summaryBody) = Build.Card("Your changes");
        ChangesCard = summary;
        _changes = summaryBody.Add(Build.Column(4));
        _details = new FileDetails(summaryBody);
        (_result, _resultText) = Build.Notice("");
        summaryBody.Add(_result).Visible = false;
        _needsFile.Add(content.Add(summary));

        OpenDialog = app.Popups.Add(Build.FilePicker("Open a settings file", FileDialog.FileModeEnum.OpenFile,
            "*.bea ; Settings files", "*.bes ; Career files"));
        SaveDialog = app.Popups.Add(Build.FilePicker("Save a copy of these settings", FileDialog.FileModeEnum.SaveFile, "*.bea ; Settings files"));
        _saveChoice = new SaveChoice(app);
        _saveChoice.Chosen += (target, _) =>
        {
            if (target == SaveTarget.Elsewhere) SaveDialog.PopupCenteredRatio(0.75f);
            else _app.Status.Track(SaveIntoGameAsync());
        };
        OpenOther.Pressed += () => OpenDialog.PopupCenteredRatio(0.75f);
        OpenDialog.FileSelected += path => _app.Status.Track(OpenAsync(path));
        SaveDialog.FileSelected += path => _app.Status.Track(SaveElsewhereAsync(path));
        Bar.Save.Pressed += AskToSave;
        Bar.Undo.Pressed += UndoChanges;
        _app.Game.Changed += ShowSources;
        foreach (Control section in _needsFile) section.Visible = false;
    }

    internal override Control Root { get; }
    internal override string Subtitle => _file is SaveSession file ? $"Changing {Describe(file.Path)}" : "Sound, controls, mouse, screen and keys";
    internal OptionButton Source { get; }
    internal ChangesBar Bar { get; }
    internal Button OpenOther { get; }
    internal Button UndoKeys { get; }
    internal Button Save => Bar.Save;
    internal Button UndoAll => Bar.Undo;
    internal PanelContainer ChangesCard { get; }
    internal FileDialog OpenDialog { get; }
    internal FileDialog SaveDialog { get; }
    internal SaveChoice SaveChoice => _saveChoice;
    internal HSlider Music => _music;
    internal OptionsReading? Reading => _reading;
    internal SaveSession? Opened => _file;
    internal string PreviewText => string.Join("\n", _changes.GetChildren().OfType<Label>().Select(label => label.Text));
    internal string ResultText => _resultText.Text;

    /// <summary>Whether the player has changed anything here that is not saved yet.</summary>
    internal bool HasChanges => !_edit.IsEmpty;

    internal override void Refresh()
    {
        if (_file is null && _app.Game.Folder is not null && !_app.Workspace.Busy && Source.ItemCount > 0 && Source.Selected >= 0)
        {
            OpenSelected(Source.Selected);
            return;
        }
        Preview();
    }

    internal async Task<Outcome<SaveSession>> OpenAsync(string path)
    {
        Outcome<SaveSession> opened = await _app.Workspace.ReadSnapshotAsync(path);
        if (opened.Value is not SaveSession file || OptionsFile.Read(file.CopyBytes()).Value is not OptionsReading reading)
        {
            _app.Status.Show(opened.Ok ? "That file has no readable settings." : opened.Message, StatusKind.Failure);
            return opened;
        }
        (_file, _reading, _edit) = (file, reading, new OptionsEdit());
        _loading = true;
        // A file from the game is named by the list above; one from elsewhere shows where it is.
        _rawLine.Text = (InGame(file.Path) is null ? file.Path + "\n" : "") + "Language and display mode are kept as they are.";
        _rawLine.TooltipText = file.Path;
        _sound.Value = Math.Round(reading.SoundVolume * 100);
        _music.Value = Math.Round(reading.MusicVolume * 100);
        for (int player = 0; player < 2; player++)
        {
            _flight[player].ButtonPressed = reading.InvertFlight[player];
            _walker[player].ButtonPressed = reading.InvertWalker[player];
            _vibration[player].ButtonPressed = reading.Vibration[player];
            _presets[player].Selected = _presets[player].GetItemIndex((int)reading.ControllerPreset[player]);
        }
        _sensitivity.Clear();
        _sensitivity.AddItem($"Keep ({reading.MouseSensitivity:0.###})");
        foreach (float step in OptionsFile.SliderSensitivities) _sensitivity.AddItem(step.ToString("0"));
        _sensitivity.Selected = 0;
        _shape.Clear();
        _shape.AddItem($"Keep ({OptionsFile.ShapeName(reading.ScreenShape)})");
        _shape.AddItem("4:3");
        _shape.AddItem("16:9");
        _shape.Selected = 0;
        _loading = false;
        _result.Visible = false;
        _empty.Visible = false;
        foreach (Control section in _needsFile) section.Visible = true;
        ShowKeys();
        Changed();
        SelectSource(file.Path);
        HeaderChanged?.Invoke();
        return opened;
    }

    /// <summary>Reopens the settings shown if the game changed their file since, unless something here is unsaved.</summary>
    internal async Task CatchUpAsync()
    {
        if (_file is not SaveSession file || HasChanges || InGame(file.Path) is not { Sha256: string now } || now == file.Sha256) return;
        await OpenAsync(file.Path);
    }

    internal void StartCapture(int entryId, int slot)
    {
        if (_reading is null) return;
        _capturing = (entryId, slot);
        _keyButtons[(entryId, slot)].Text = "Press a key…";
        _keyButtons[(entryId, slot)].GrabFocus();
    }

    /// <summary>Applies a captured physical key; Escape cancels. Returns whether the key was usable.</summary>
    internal bool Capture(Key physical)
    {
        if (_capturing is not (int EntryId, int Slot) target) return false;
        _capturing = null;
        if (physical != Godot.Key.Escape && KeyTable.For(physical) is KeyChoice choice) _edit.Keys[target] = choice;
        else if (physical != Godot.Key.Escape) _app.Status.Show("That key can't be stored by the game, so it cannot be used here.", StatusKind.Failure);
        ShowKeys();
        Preview();
        return physical != Godot.Key.Escape && KeyTable.For(physical) is not null;
    }

    internal void AskToSave()
    {
        if (_file is not SaveSession file || _plan.Value is null) return;
        bool inGame = InGame(file.Path) is not null;
        _saveChoice.Open("Save your settings", null, inGame ? Describe(file.Path) : null,
            "These settings replace the ones in that file. Its current version goes into the backup first.");
    }

    /// <summary>Replaces the chosen file in the game with the changed settings, after a verified backup.</summary>
    internal async Task<InstallReceipt> SaveIntoGameAsync()
    {
        if (_file is not SaveSession file || _plan.Value is not OptionsPlan plan || _app.Game.Folder is not GameFolder game)
            return new InstallReceipt(false, "Open settings and change something first.", "");
        if (InGame(file.Path) is not GameFile target) return new InstallReceipt(false, "That file is not in your game.", file.Path);
        if (_app.BackupFolderOrReport() is not string backups) return new InstallReceipt(false, "No backup folder.", target.Name);
        _app.Status.Show("Backing up, then saving your settings…");
        InstallReceipt receipt = await _app.Workspace.InstallBytesAsync(game, target.Name, plan.Bytes, backups, _app.GameRunning,
            file.Sha256, $"Before changing the settings in {Describe(file.Path)}");
        await _app.Game.RescanAsync();
        if (receipt.Ok)
        {
            await OpenAsync(target.Path);
            ShowResult($"Saved. The settings in {Describe(target.Path)} are changed; the previous version is in your backups.", true);
            _app.Status.Show("Settings saved into your game.", StatusKind.Success);
        }
        else
        {
            ShowResult(receipt.Message, false);
            _app.Status.Show(receipt.Message, StatusKind.Failure);
        }
        return receipt;
    }

    /// <summary>Publishes the changed settings as a new file outside the game and reads it back.</summary>
    internal async Task<PublicationReceipt> SaveElsewhereAsync(string destination)
    {
        if (_file is not SaveSession file || _plan.Value is not OptionsPlan plan)
            return new PublicationReceipt(false, _plan.Message);
        _app.Status.Show("Saving a checked copy of your settings…");
        PublicationReceipt receipt = await _app.Workspace.PublishFromAsync(file, destination, plan.Bytes);
        // Saved changes are done: start again from the file shown (reopening hides the result, so show it after).
        if (receipt.Ok) await OpenAsync(file.Path);
        ShowResult(receipt.Ok ? $"Saved a copy with your settings to {destination}. It was read back and matches byte for byte."
            : receipt.Message + (receipt.MayHaveOutput ? $"\nA copy may exist at: {receipt.Output ?? destination}" : ""), receipt.Ok);
        _app.Status.Show(receipt.Ok ? "Settings copy saved and checked." : receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        return receipt;
    }

    private void ShowSources()
    {
        if (_app.Game.Busy) return;
        _sourcePaths.Clear();
        Source.Clear();
        if (_app.Game.Folder is GameFolder game)
        {
            if (game.Options is { Supported: true } options)
            {
                Source.AddItem("The game's default settings");
                _sourcePaths.Add(options.Path);
            }
            foreach (GameFile career in game.Careers.Where(file => file.Supported))
            {
                Source.AddItem($"Settings in {career.DisplayName}");
                _sourcePaths.Add(career.Path);
            }
        }
        if (_file is SaveSession file && !_sourcePaths.Contains(file.Path))
        {
            Source.AddItem($"File: {System.IO.Path.GetFileName(file.Path)}");
            _sourcePaths.Add(file.Path);
        }
        Source.Disabled = Source.ItemCount == 0;
        if (Source.ItemCount > 0) SelectSource(_file?.Path ?? _sourcePaths[0]);
    }

    private void SelectSource(string path)
    {
        if (!_sourcePaths.Contains(path)) ShowSources();
        int index = _sourcePaths.IndexOf(path);
        if (index >= 0) Source.Selected = index;
    }

    private void OpenSelected(int index)
    {
        if (index >= 0 && index < _sourcePaths.Count && _sourcePaths[index] != _file?.Path) _app.Status.Track(OpenAsync(_sourcePaths[index]));
    }

    private GameFile? InGame(string path) => _app.Game.Folder is GameFolder game
        ? game.Careers.Append(game.Options).OfType<GameFile>().FirstOrDefault(file => string.Equals(file.Path, path, StringComparison.Ordinal))
        : null;

    private string Describe(string path) => InGame(path) is GameFile file
        ? string.Equals(file.Name, GameInstaller.OptionsName, StringComparison.OrdinalIgnoreCase) ? "the game's default settings" : file.DisplayName
        : System.IO.Path.GetFileName(path);

    private void Preview()
    {
        _changes.Clear();
        if (_file is not SaveSession file)
        {
            Bar.Show(0, false, false);
            return;
        }
        _plan = OptionsFile.Preview(file.CopyBytes(), _edit);
        if (_plan.Value is OptionsPlan plan)
        {
            foreach (string line in plan.Lines) _changes.Add(Build.Text("•  " + line, "Strong"));
            _details.Show($"[color=#{Palette.Data.ToHtml(false)}]{plan.Changes.Count} bytes change;[/color] every other byte is kept.\n[code]" +
                string.Join("   ", plan.Changes.Select(change => $"0x{change.Offset:X4} {change.Before:X2}→{change.After:X2}")) + "[/code]");
        }
        else
        {
            bool none = _edit.IsEmpty;
            _changes.Add(Build.Text(none ? "No changes yet." : _plan.Message, none ? "Muted" : "Bad"));
            _details.Show(null);
        }
        bool ready = !_app.Workspace.Busy;
        Bar.Show(_plan.Value is OptionsPlan changed ? changed.Lines.Count : 0, ready && _plan.Ok, ready && HasChanges);
    }

    private void UndoChanges()
    {
        if (_file is SaveSession file) _app.Status.Track(OpenAsync(file.Path));
    }

    private (HSlider Slider, Label Value) Slider(VBoxContainer parent, string name)
    {
        HBoxContainer row = parent.Add(Build.Row(12));
        row.Add(Build.Text(name, "Muted", wrap: false, width: 160));
        HSlider slider = row.Add(new HSlider { MinValue = 0, MaxValue = 100, Step = 1, CustomMinimumSize = new Vector2(280, 0),
            SizeFlagsVertical = Control.SizeFlags.ShrinkCenter });
        Label value = row.Add(Build.Text("", "Strong", wrap: false, width: 60));
        slider.ValueChanged += _ => Changed();
        return (slider, value);
    }

    private void Changed()
    {
        if (_loading || _reading is not OptionsReading reading) return;
        _soundValue.Text = $"{_sound.Value:0}%";
        _musicValue.Text = $"{_music.Value:0}%";
        _edit.SoundVolume = Math.Abs(_sound.Value - Math.Round(reading.SoundVolume * 100)) < 0.5 ? null : (float)(_sound.Value / 100);
        _edit.MusicVolume = Math.Abs(_music.Value - Math.Round(reading.MusicVolume * 100)) < 0.5 ? null : (float)(_music.Value / 100);
        for (int player = 0; player < 2; player++)
        {
            _edit.InvertFlight[player] = _flight[player].ButtonPressed == reading.InvertFlight[player] ? null : _flight[player].ButtonPressed;
            _edit.InvertWalker[player] = _walker[player].ButtonPressed == reading.InvertWalker[player] ? null : _walker[player].ButtonPressed;
            _edit.Vibration[player] = _vibration[player].ButtonPressed == reading.Vibration[player] ? null : _vibration[player].ButtonPressed;
            uint preset = (uint)_presets[player].GetSelectedId();
            _edit.ControllerPreset[player] = _presets[player].Selected < 0 || preset == reading.ControllerPreset[player] ? null : preset;
        }
        _edit.MouseSensitivity = _sensitivity.Selected <= 0 ? null : OptionsFile.SliderSensitivities[_sensitivity.Selected - 1];
        _edit.ScreenShape = _shape.Selected <= 0 ? null : (uint)(_shape.Selected - 1);
        Preview();
    }

    private void ShowKeys()
    {
        if (_reading is not OptionsReading reading) return;
        foreach (((int entryId, int slot), Button button) in _keyButtons)
        {
            if (_edit.Keys.TryGetValue((entryId, slot), out KeyChoice? chosen))
            {
                button.Text = chosen.Name + "  (new)";
                button.ThemeTypeVariation = "Primary";
                continue;
            }
            button.ThemeTypeVariation = "";
            BindingRow? row = reading.Bindings.FirstOrDefault(row => row.EntryId == entryId);
            button.Text = row is null ? "Not set" : OptionsFile.Describe(row.Slot(slot).Device, row.Slot(slot).Key);
            button.TooltipText = row is null ? "" : "Click, then press a key to change it. " + OptionsFile.Raw(row.Slot(slot).Device, row.Slot(slot).Key) + ".";
        }
    }

    private void OnKeyInput(InputEvent input, Button button)
    {
        if (_capturing is null || input is not InputEventKey { Pressed: true, Echo: false } key) return;
        Capture(key.PhysicalKeycode);
        button.AcceptEvent();
    }

    private void ShowResult(string text, bool ok)
    {
        _result.Visible = true;
        _result.ThemeTypeVariation = ok ? "SuccessNotice" : "FailureNotice";
        _resultText.Text = text;
        Callable.From(() => _scroll.EnsureControlVisible(_result)).CallDeferred();
    }
}
