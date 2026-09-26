// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The game's own settings file, defaultoptions.bea: read-only first, changes previewed byte for byte,
/// written to a new verified .bea, and put into the game only as a separate confirmed install.
/// </summary>
internal sealed class OptionsPage : Page
{
    private readonly CareerWorkspace _workspace;
    private readonly GameLibrary _game;
    private readonly StatusLine _status;
    private readonly Func<bool> _gameRunning;
    private readonly Label _empty, _fileLine, _rawLine, _previewLines, _resultText, _needsBackups;
    private readonly RichTextLabel _previewBytes;
    private readonly PanelContainer _result;
    private readonly List<Control> _needsFile = [];
    private readonly HSlider _sound, _music;
    private readonly Label _soundValue, _musicValue;
    private readonly CheckBox[] _flight = new CheckBox[2], _walker = new CheckBox[2], _vibration = new CheckBox[2];
    private readonly OptionButton[] _presets = new OptionButton[2];
    private readonly OptionButton _sensitivity, _shape;
    private readonly Dictionary<(int EntryId, int Slot), Button> _keyButtons = [];
    private SaveSession? _file;
    private OptionsReading? _reading;
    private OptionsEdit _edit = new();
    private Outcome<OptionsPlan> _plan = Outcome<OptionsPlan>.Refusal("Choose a setting to change.");
    private (int EntryId, int Slot)? _capturing;
    private bool _loading;

    internal OptionsPage(CareerWorkspace workspace, GameLibrary game, StatusLine status, Node popups, Func<bool> gameRunning)
        : base("options", "Options")
    {
        (_workspace, _game, _status, _gameRunning) = (workspace, game, status, gameRunning);
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;
        content.Add(Build.Notice("Reads the game's options file read-only. Changes go to a new, verified .bea copy; putting that " +
            "copy into the game is a separate, confirmed step with a backup first.").Panel);

        (PanelContainer fileCard, VBoxContainer fileBody) = Build.Card("Options file");
        _fileLine = fileBody.Add(Build.Text("No options file open.", "Mono"));
        _rawLine = fileBody.Add(Build.Text("", "Faint"));
        HBoxContainer fileActions = fileBody.Add(Build.Row(10));
        OpenGameOptions = fileActions.Add(Build.Button("Open the game's options", "Primary", disabled: true));
        OpenOther = fileActions.Add(Build.Button("Open another .bea…"));
        content.Add(fileCard);
        _empty = content.Add(Build.Text("Open an options file to change its settings.", "Muted"));

        (PanelContainer audio, VBoxContainer audioBody) = Build.Card("Audio");
        (_sound, _soundValue) = Slider(audioBody, "Sound effects");
        (_music, _musicValue) = Slider(audioBody, "Music");
        audioBody.Add(Build.Text("Seen in the game's original code: loading copies these values into its settings; a changed value " +
            "resets the audio.", "Faint"));
        _needsFile.Add(content.Add(audio));

        (PanelContainer controls, VBoxContainer controlBody) = Build.Card("Controls");
        GridContainer grid = controlBody.Add(new GridContainer { Columns = 5 });
        grid.AddThemeConstantOverride("h_separation", 20);
        grid.AddThemeConstantOverride("v_separation", 8);
        foreach (string heading in new[] { "", "Flight invert Y", "Walker invert Y", "Vibration", "Controller preset" })
            grid.Add(Build.Eyebrow(heading));
        for (int player = 0; player < 2; player++)
        {
            grid.Add(Build.Text($"Player {player + 1}", "Strong", wrap: false));
            _flight[player] = grid.Add(new CheckBox());
            _walker[player] = grid.Add(new CheckBox());
            _vibration[player] = grid.Add(new CheckBox());
            _presets[player] = grid.Add(new OptionButton { CustomMinimumSize = new Vector2(120, 0) });
            for (int preset = 1; preset <= 4; preset++) _presets[player].AddItem($"Preset {preset}", preset);
            foreach (BaseButton toggle in new BaseButton[] { _flight[player], _walker[player], _vibration[player] })
                toggle.Toggled += _ => Changed();
            _presets[player].ItemSelected += _ => Changed();
        }
        controlBody.Add(Build.Text("Stored as the game lays them out; how each preset plays has not been watched in the game.", "Faint"));
        _needsFile.Add(content.Add(controls));

        (PanelContainer mouse, VBoxContainer mouseBody) = Build.Card("Mouse and display");
        HBoxContainer sensitivityRow = mouseBody.Add(Build.Row(10));
        sensitivityRow.Add(Build.Text("Mouse sensitivity", "Muted", wrap: false, width: 160));
        _sensitivity = sensitivityRow.Add(new OptionButton { CustomMinimumSize = new Vector2(160, 0) });
        _sensitivity.ItemSelected += _ => Changed();
        HBoxContainer shapeRow = mouseBody.Add(Build.Row(10));
        shapeRow.Add(Build.Text("Screen shape", "Muted", wrap: false, width: 160));
        _shape = shapeRow.Add(new OptionButton { CustomMinimumSize = new Vector2(160, 0) });
        _shape.ItemSelected += _ => Changed();
        mouseBody.Add(Build.Text("Sensitivity uses the game's own slider steps, 3 to 63. The language and display-mode values are " +
            "shown above but not offered: which language each number selects is not established.", "Faint"));
        _needsFile.Add(content.Add(mouse));

        (PanelContainer keys, VBoxContainer keyBody) = Build.Card("Key bindings");
        keyBody.Add(Build.Text("Choose a binding, then press a key (Esc cancels). Controller and mouse bindings are kept unless " +
            "you replace them with a key. Rows are copied by the game as they are, so a row's other fields never change.", "Muted"));
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
        keyBody.Add(Build.Text("A Transform key set in a copied options file was seen working in the game; the other rows follow " +
            "the same stored form, read from rows the game itself wrote.", "Faint"));
        _needsFile.Add(content.Add(keys));

        (PanelContainer preview, VBoxContainer previewBody) = Build.Card("Preview");
        _previewLines = previewBody.Add(Build.Text("", "Strong"));
        _previewBytes = previewBody.Add(Build.Detail("", bbcode: true));
        _needsFile.Add(content.Add(preview));

        (PanelContainer write, VBoxContainer writeBody) = Build.Card("Write");
        HBoxContainer destinationRow = writeBody.Add(Build.Row(10));
        Destination = destinationRow.Add(new LineEdit
        {
            SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, ThemeTypeVariation = "MonoField", PlaceholderText = "/path/to/new-options.bea",
        });
        ChooseDestination = destinationRow.Add(Build.Button("Choose…"));
        HBoxContainer writeActions = writeBody.Add(Build.Row(10));
        WriteCopy = writeActions.Add(Build.Button("Write verified copy", "Primary", disabled: true));
        InstallCopy = writeActions.Add(Build.Button("Use this copy as the game's options…", "Caution", disabled: true));
        _needsBackups = writeBody.Add(Build.Text("Using a copy as the game's options backs up first: choose a backup folder on " +
            "Install & backups.", "Faint"));
        (_result, _resultText) = Build.Notice("");
        writeBody.Add(_result).Visible = false;
        _needsFile.Add(content.Add(write));

        OpenDialog = popups.Add(Build.FilePicker("Open an options file", FileDialog.FileModeEnum.OpenFile, "*.bea ; Options files"));
        SaveDialog = popups.Add(Build.FilePicker("Choose a new options file name", FileDialog.FileModeEnum.SaveFile, "*.bea ; Options files"));
        Confirm = popups.Add(new ConfirmationDialog { Title = "Replace the game's options?", OkButtonText = "Back up, then replace" });
        Confirm.GetLabel().AutowrapMode = TextServer.AutowrapMode.WordSmart;
        Confirm.MinSize = new Vector2I(560, 0);
        OpenGameOptions.Pressed += () =>
        {
            if (_game.Folder?.Options is GameFile options) _status.Track(OpenAsync(options.Path));
        };
        OpenOther.Pressed += () => OpenDialog.PopupCenteredRatio(0.75f);
        OpenDialog.FileSelected += path => _status.Track(OpenAsync(path));
        ChooseDestination.Pressed += () => SaveDialog.PopupCenteredRatio(0.75f);
        SaveDialog.FileSelected += path =>
        {
            Build.ShowPath(Destination, path);
            Refresh();
        };
        Destination.TextChanged += _ => Refresh();
        WriteCopy.Pressed += () => _status.Track(WriteCopyAsync());
        InstallCopy.Pressed += AskToInstall;
        Confirm.Confirmed += () => _status.Track(ConfirmInstallAsync());
        foreach (Control section in _needsFile) section.Visible = false;
    }

    internal override Control Root { get; }
    internal override string Subtitle => _file is SaveSession file ? System.IO.Path.GetFileName(file.Path) + " · read-only"
        : "The game's own settings file, changed only in verified copies";
    internal Button OpenGameOptions { get; }
    internal Button OpenOther { get; }
    internal Button UndoKeys { get; }
    internal LineEdit Destination { get; }
    internal Button ChooseDestination { get; }
    internal Button WriteCopy { get; }
    internal Button InstallCopy { get; }
    internal FileDialog OpenDialog { get; }
    internal FileDialog SaveDialog { get; }
    internal ConfirmationDialog Confirm { get; }
    internal HSlider Music => _music;
    internal OptionsReading? Reading => _reading;
    internal string PreviewText => _previewLines.Text;
    internal string LastCopy { get; private set; } = "";

    internal async Task<Outcome<SaveSession>> OpenAsync(string path)
    {
        _status.Show("Opening the options file read-only…");
        Outcome<SaveSession> opened = await _workspace.ReadSnapshotAsync(path);
        if (opened.Value is not SaveSession file || OptionsFile.Read(file.CopyBytes()).Value is not OptionsReading reading)
        {
            _status.Show(opened.Ok ? "That file has no readable options block." : opened.Message, StatusKind.Failure);
            return opened;
        }
        (_file, _reading, _edit, LastCopy) = (file, reading, new OptionsEdit(), "");
        _loading = true;
        _fileLine.Text = file.Path;
        _rawLine.Text = $"Stored language index {reading.Language}  ·  display mode 0x{reading.DisplayMode:X8}  ·  control scheme " +
            (reading.ControlScheme == 0 ? "custom" : $"preset ({reading.ControlScheme})");
        _sound.Value = Math.Round(reading.SoundVolume * 100);
        _music.Value = Math.Round(reading.MusicVolume * 100);
        for (int player = 0; player < 2; player++)
        {
            _flight[player].ButtonPressed = reading.InvertFlight[player];
            _walker[player].ButtonPressed = reading.InvertWalker[player];
            _vibration[player].ButtonPressed = reading.Vibration[player];
            int preset = _presets[player].GetItemIndex((int)reading.ControllerPreset[player]);
            _presets[player].Selected = preset;
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
        Destination.Text = "";
        _result.Visible = false;
        _empty.Visible = false;
        foreach (Control section in _needsFile) section.Visible = true;
        ShowKeys();
        Changed();
        _status.Show("Options file opened read-only.", StatusKind.Success);
        return opened;
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
        else if (physical != Godot.Key.Escape) _status.Show("That key's stored form is not established, so it cannot be bound here.", StatusKind.Failure);
        ShowKeys();
        Refresh();
        return physical != Godot.Key.Escape && KeyTable.For(physical) is not null;
    }

    internal override void Refresh()
    {
        OpenGameOptions.Disabled = _game.Folder?.Options is not { Supported: true } || _workspace.Busy;
        if (_file is not SaveSession file) return;
        _plan = OptionsFile.Preview(file.CopyBytes(), _edit);
        if (_plan.Value is OptionsPlan plan)
        {
            _previewLines.Text = string.Join("\n", plan.Lines);
            _previewBytes.Text = $"[color=#{Palette.Data.ToHtml(false)}]{plan.Changes.Count} changed bytes;[/color] every other byte " +
                "is kept.\n[code]" + string.Join("   ", plan.Changes.Select(change => $"0x{change.Offset:X4} {change.Before:X2}→{change.After:X2}")) + "[/code]";
        }
        else
        {
            _previewLines.Text = _plan.Message;
            _previewBytes.Text = "";
        }
        bool ready = !_workspace.Busy;
        WriteCopy.Disabled = !ready || !_plan.Ok || Destination.Text.Trim().Length == 0;
        bool backups = !string.IsNullOrEmpty(_game.Settings.Load().BackupFolder);
        InstallCopy.Disabled = !ready || LastCopy.Length == 0 || _game.Folder is null || !backups;
        _needsBackups.Visible = !backups;
    }

    internal async Task<PublicationReceipt> WriteCopyAsync()
    {
        if (_file is not SaveSession file || _plan.Value is not OptionsPlan plan)
            return new PublicationReceipt(false, _plan.Message);
        string destination = Destination.Text.Trim();
        _status.Show("Writing and verifying the options copy…");
        PublicationReceipt receipt = await _workspace.PublishFromAsync(file, destination, plan.Bytes);
        if (receipt.Ok) LastCopy = destination;
        ShowResult(receipt.Ok ? $"Written and verified: {destination}\n{plan.Changes.Count} changed bytes; SHA-256 {receipt.Sha256.ToLowerInvariant()}"
            : receipt.Message + (receipt.MayHaveOutput ? $"\nA copy may exist at: {receipt.Output ?? destination}" : ""), receipt.Ok);
        _status.Show(receipt.Ok ? "Options copy written and verified." : receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        Refresh();
        return receipt;
    }

    internal void AskToInstall()
    {
        if (LastCopy.Length == 0 || _game.Folder is null || string.IsNullOrEmpty(_game.Settings.Load().BackupFolder)) return;
        Confirm.DialogText = $"Replace the game's defaultoptions.bea with\n{LastCopy}?\n\nFirst, every career and the options file are " +
            $"copied and verified into a new set in\n{_game.Settings.Load().BackupFolder}\n\nThe current options file is compared with " +
            "that backup immediately before an atomic swap. Close Battle Engine Aquila first; nothing is written while it runs.";
        Confirm.PopupCentered();
    }

    internal async Task<InstallReceipt> ConfirmInstallAsync()
    {
        Confirm.Hide();
        if (_game.Folder is not GameFolder game || LastCopy.Length == 0)
            return new InstallReceipt(false, "Write a verified copy first.", GameInstaller.OptionsName);
        _status.Show("Backing up, then replacing the game's options…");
        InstallReceipt receipt = await _workspace.InstallAsync(game, LastCopy, GameInstaller.OptionsName,
            _game.Settings.Load().BackupFolder ?? "", _gameRunning);
        ShowResult(receipt.Message + (receipt.BackupFolder is string backup ? $"\nBackup: {backup}" : ""), receipt.Ok);
        _status.Show(receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        await _game.RescanAsync();
        return receipt;
    }

    private (HSlider Slider, Label Value) Slider(VBoxContainer parent, string name)
    {
        HBoxContainer row = parent.Add(Build.Row(12));
        row.Add(Build.Text(name, "Muted", wrap: false, width: 160));
        HSlider slider = row.Add(new HSlider { MinValue = 0, MaxValue = 100, Step = 1, CustomMinimumSize = new Vector2(260, 0),
            SizeFlagsVertical = Control.SizeFlags.ShrinkCenter });
        Label value = row.Add(Build.Text("", "Mono", wrap: false, width: 60));
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
        Refresh();
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
            button.Text = reading.Bindings.FirstOrDefault(row => row.EntryId == entryId) is BindingRow row
                ? OptionsFile.Describe(row.Slot(slot).Device, row.Slot(slot).Key) : "No row";
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
    }
}
