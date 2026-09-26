// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// Change the open career: kill counts and Goodies. Nothing is written until the player saves, and then
/// only as a new career in the game, in place of this career (after a verified backup and only if the
/// game has not saved it since it was opened), or as a copy elsewhere. Every save is checked byte for
/// byte against the plan.
/// </summary>
internal sealed class EditCareerPage : Page
{
    private static readonly GoodieState[] Targets = [GoodieState.Locked, GoodieState.Hint, GoodieState.New, GoodieState.Old];
    private const int GoodieRowsShown = 10;

    private readonly AppServices _app;
    private readonly SortedDictionary<int, GoodieState> _goodieTargets = [];
    private readonly VBoxContainer _goodieRows, _changes;
    private readonly CareerCards _choose;
    private readonly List<Control> _needsCareer = [];
    private readonly Label _intro;
    private readonly SaveChoice _saveChoice;
    private readonly ScrollContainer _scroll;
    private Outcome<EditPlan> _plan = Outcome<EditPlan>.Refusal("No changes yet.");

    internal EditCareerPage(AppServices app) : base("edit", "Edit career", "edit")
    {
        _app = app;
        (_scroll, VBoxContainer content) = Build.Scroller();
        Bar = new ChangesBar("Save changes…");
        Root = Bar.Wrap(_scroll);
        _intro = content.Add(Build.Text("Choose a career to change.", "Lead"));
        _choose = new CareerCards(app);
        content.Add(_choose.Root);
        _needsCareer.Add(content.Add(Build.Notice("Nothing changes until you save. Saving into your game always backs up every " +
            "career and your settings first, and you choose whether to add a new career or replace this one.").Panel));

        (PanelContainer kills, VBoxContainer killBody) = Build.Card("Kill counts");
        killBody.Add(Build.Text("Type a new number to change a count. The game keeps up to 16,777,215 in each.", "Muted"));
        Rows = CareerSave.CategoryNames.Select((name, index) => new KillRow(index, name)).ToArray();
        foreach (KillRow row in Rows)
        {
            killBody.Add(row.Root);
            row.Changed += RefreshPreview;
        }
        _needsCareer.Add(content.Add(kills));

        (PanelContainer goodies, VBoxContainer goodieBody) = Build.Card("Goodies");
        goodieBody.Add(Build.Text("Unlock every Goodie at once, or pick them one by one on the Goodies page. Unlocked Goodies show " +
            "gold in the game's gallery until you look at them.", "Muted"));
        HBoxContainer goodieActions = goodieBody.Add(Build.Row(10));
        UnlockAll = goodieActions.Add(Build.Button("Unlock every Goodie"));
        UnlockAll.Icon = Icons.Get("goodies");
        Button pick = goodieActions.Add(Build.Button("Pick on the Goodies page", "Link"));
        pick.Pressed += () => _app.Navigate("goodies");
        ClearGoodies = goodieActions.Add(Build.Button("Clear Goodie changes", "Link"));
        _goodieRows = goodieBody.Add(Build.Column(6));
        goodieBody.Add(Build.Text("A Goodie changed this way was loaded and shown by the game for Goodie 002; the others use the same " +
            "stored values but have not been watched in play.", "Faint"));
        _needsCareer.Add(content.Add(goodies));

        (PanelContainer summary, VBoxContainer summaryBody) = Build.Card("Your changes");
        _changes = summaryBody.Add(Build.Column(4));
        HBoxContainer saveRow = summaryBody.Add(Build.Row(10));
        Save = saveRow.Add(Build.Button("Save changes…", "Primary", disabled: true));
        Save.Icon = Icons.Get("save");
        UndoAll = saveRow.Add(Build.Button("Undo all changes", "Link", disabled: true));
        Button details = summaryBody.Add(Build.Button("Show exactly what changes in the file", "Link"));
        Details = summaryBody.Add(Build.Detail("", bbcode: true));
        Details.Visible = false;
        details.Pressed += () =>
        {
            Details.Visible = !Details.Visible;
            details.Text = Details.Visible ? "Hide the file details" : "Show exactly what changes in the file";
        };
        (ResultPanel, Result) = Build.Notice("");
        ResultPanel.Visible = false;
        summaryBody.Add(ResultPanel);
        OpenResult = summaryBody.Add(Build.Button("Open the saved career", "Link"));
        OpenResult.Visible = false;
        OpenResult.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        _needsCareer.Add(content.Add(summary));

        OutputDialog = app.Popups.Add(Build.FilePicker("Save a copy of your career", FileDialog.FileModeEnum.SaveFile, "*.bes ; Career files"));
        _saveChoice = new SaveChoice(app);
        _saveChoice.Chosen += (target, name) =>
        {
            if (target == SaveTarget.Elsewhere) ChooseElsewhere();
            else _app.Status.Track(SaveIntoGameAsync(target, name));
        };
        OutputDialog.FileSelected += path => _app.Status.Track(SaveElsewhereAsync(path));
        UnlockAll.Pressed += UnlockEveryGoodie;
        ClearGoodies.Pressed += () =>
        {
            _goodieTargets.Clear();
            ShowGoodieRows();
            RefreshPreview();
        };
        Save.Pressed += AskToSave;
        Bar.Save.Pressed += AskToSave;
        UndoAll.Pressed += UndoChanges;
        Bar.Undo.Pressed += UndoChanges;
        OpenResult.Pressed += () => _app.Status.Track(_app.OpenCareer(_app.Workspace.LastVerifiedOutput.Length > 0
            ? _app.Workspace.LastVerifiedOutput : _lastInstalled));
        ShowEmpty();
    }

    private string _lastInstalled = "";

    internal override Control Root { get; }
    internal override string Subtitle => _app.Workspace.Session is SaveSession session
        ? $"Changing {System.IO.Path.GetFileNameWithoutExtension(session.Path)}"
        : "Change kill counts and Goodies, then save";

    internal IReadOnlyList<KillRow> Rows { get; }
    internal ChangesBar Bar { get; }
    internal IReadOnlyDictionary<int, GoodieState> GoodieTargets => _goodieTargets;
    internal IReadOnlyList<OptionButton> GoodiePickers => _goodieRows.FindChildren("*", nameof(OptionButton), true, false).OfType<OptionButton>().ToArray();
    internal Button UnlockAll { get; }
    internal Button ClearGoodies { get; }
    internal Button Save { get; }
    internal Button UndoAll { get; }
    internal Button OpenResult { get; }
    internal RichTextLabel Details { get; }
    internal PanelContainer ResultPanel { get; }
    internal Label Result { get; }
    internal FileDialog OutputDialog { get; }
    internal SaveChoice SaveChoice => _saveChoice;
    internal Outcome<EditPlan> Plan => _plan;

    /// <summary>Whether the player has changed anything here that is not saved yet.</summary>
    internal bool HasChanges => Rows.Any(row => row.IsChanged) || _goodieTargets.Count > 0;

    /// <summary>The changes in the player's words, one per line.</summary>
    internal string ChangesText => string.Join("\n", _changes.GetChildren().OfType<Label>().Select(label => label.Text));

    internal void ShowSession(SaveSession session)
    {
        CareerInspection analysis = session.Analysis;
        foreach (KillRow row in Rows) row.SetCurrent(analysis.Kills[row.Category]);
        _goodieTargets.Clear();
        ShowGoodieRows();
        foreach (Control section in _needsCareer) section.Visible = true;
        _intro.Text = $"Changing {System.IO.Path.GetFileNameWithoutExtension(session.Path)}.";
        _choose.Root.Visible = false;
        ResultPanel.Visible = OpenResult.Visible = false;
        RefreshPreview();
    }

    internal override void Refresh()
    {
        if (_app.Workspace.Session is null) ShowEmpty();
        UpdateActions();
    }

    internal void UpdateActions()
    {
        bool ready = _app.Workspace.Session is not null && !_app.Workspace.Busy;
        Save.Disabled = !ready || !_plan.Ok;
        UndoAll.Disabled = !ready || !_plan.Ok;
        UnlockAll.Disabled = ClearGoodies.Disabled = !ready;
        foreach (KillRow row in Rows) row.SetLocked(!ready);
        Bar.Show(_app.Workspace.Session is null ? 0 : Rows.Count(row => row.IsChanged) + _goodieTargets.Count, ready && _plan.Ok);
    }

    private void UndoChanges()
    {
        if (_app.Workspace.Session is SaveSession session) ShowSession(session);
    }

    /// <summary>Adds a Goodie aiming at the opposite of what it has now: locked ones become unlocked, unlocked ones locked.</summary>
    internal void AddGoodie(int index)
    {
        if (_app.Workspace.Session is not SaveSession session || index < 0 || index >= CareerSave.GoodieTable) return;
        if (!CareerSave.IsShown(index))
        {
            _app.Status.Show($"Goodie {index:D3} is never shown in the game's gallery, so its state is kept as it is.", StatusKind.Failure);
            return;
        }
        if (!_goodieTargets.ContainsKey(index))
            _goodieTargets[index] = session.Analysis.Goodies[index].State is GoodieState.New or GoodieState.Old ? GoodieState.Locked : GoodieState.New;
        ShowGoodieRows();
        RefreshPreview();
    }

    internal void SetGoodieTarget(int index, GoodieState state)
    {
        if (!_goodieTargets.ContainsKey(index)) return;
        _goodieTargets[index] = state;
        ShowGoodieRows();
        RefreshPreview();
    }

    internal void RemoveGoodie(int index)
    {
        _goodieTargets.Remove(index);
        ShowGoodieRows();
        RefreshPreview();
    }

    /// <summary>Every Goodie the gallery shows that is locked (with or without its hint) becomes unlocked and new.</summary>
    internal void UnlockEveryGoodie()
    {
        if (_app.Workspace.Session is not SaveSession session) return;
        foreach (GoodieRecord goodie in session.Analysis.Goodies.Where(goodie => goodie.Shown && goodie.State is GoodieState.Locked or GoodieState.Hint))
            _goodieTargets[goodie.Index] = GoodieState.New;
        ShowGoodieRows();
        RefreshPreview();
        if (_goodieTargets.Count == 0) _app.Status.Show("Every Goodie in this career is already unlocked.");
    }

    internal void RefreshPreview()
    {
        _changes.Clear();
        if (_app.Workspace.Session is not SaveSession session) return;
        Dictionary<int, int> kills = Rows.Where(row => row.IsChanged).ToDictionary(row => row.Category, row => row.TargetValue);
        _plan = kills.Count + _goodieTargets.Count == 0
            ? Outcome<EditPlan>.Refusal("No changes yet.")
            : session.Prepare(new EditRequest(kills, new Dictionary<int, GoodieState>(_goodieTargets)));
        if (_plan.Value is not EditPlan plan)
        {
            _changes.Add(Build.Text(_plan.Message == "No changes yet." ? "No changes yet. Change a count or a Goodie above." : _plan.Message,
                _plan.Message == "No changes yet." ? "Muted" : "Bad"));
            Details.Text = "";
        }
        else
        {
            foreach (KillEdit edit in plan.Selected)
                _changes.Add(Build.Text($"•  {edit.Name} kills: {edit.Before:N0} → {edit.After:N0}", "Strong"));
            foreach (IGrouping<GoodieState, GoodieEdit> group in plan.Goodies.GroupBy(edit => edit.After))
            {
                string names = group.Count() <= 3 ? string.Join(", ", group.Select(edit => GoodieName(edit.Index))) : "";
                _changes.Add(Build.Text($"•  {Build.Count(group.Count(), "Goodie")} {Verb(group.Key)}{(names.Length > 0 ? $": {names}" : "")}", "Strong"));
            }
            Details.Text = $"[color=#{Palette.Data.ToHtml(false)}]{plan.ChangedBytes} bytes change;[/color] the file keeps its length " +
                "and every other byte.\n[code]" + string.Join("   ", plan.Changes.Select(change =>
                    $"0x{change.Offset:X4} {change.Before:X2}→{change.After:X2}")) + "[/code]";
        }
        UpdateActions();
    }

    internal void AskToSave()
    {
        if (_app.Workspace.Session is not SaveSession session || _plan.Value is null) return;
        string name = System.IO.Path.GetFileNameWithoutExtension(session.Path);
        bool inGame = InGame(session) is not null;
        _saveChoice.Open("Save your changes", _app.NewCareerName($"{name} (edited)"), inGame ? name : null,
            "The career in your game gets these changes. Its current version goes into the backup first.", _app.CareerNameProblem);
    }

    /// <summary>Saves the planned changes into the game: as a new career, or in place of the open one.</summary>
    internal async Task<InstallReceipt> SaveIntoGameAsync(SaveTarget target, string newName)
    {
        if (_app.Workspace.Session is not SaveSession session || _plan.Value is not EditPlan plan || _app.Game.Folder is not GameFolder game)
            return new InstallReceipt(false, "Open a career and make a change first.", newName);
        if (_app.BackupFolderOrReport() is not string backups) return new InstallReceipt(false, "No backup folder.", newName);
        string name = System.IO.Path.GetFileNameWithoutExtension(session.Path);
        bool replace = target == SaveTarget.Replace;
        if (replace && InGame(session) is null)
            return new InstallReceipt(false, "This career is not in your game's career list, so it cannot be replaced there.", name);
        string targetName = (replace ? name : newName) + ".bes";
        _app.Status.Show("Backing up, then saving into your game…");
        InstallReceipt receipt = await _app.Workspace.InstallBytesAsync(game, targetName, plan.CopyBytes(), backups, _app.GameRunning,
            replace ? session.Sha256 : null, replace ? $"Before changing {name}" : $"Before adding {newName}");
        string saved = System.IO.Path.GetFileNameWithoutExtension(targetName);
        if (receipt.Ok)
        {
            _lastInstalled = receipt.Target;
            ShowResult(replace ? $"Saved. {saved} in your game now has your changes. Its previous version is in your backups."
                : $"Saved. {saved} is now in your game's career list. Your other careers are unchanged.", "SuccessNotice");
            _app.Status.Show(replace ? $"{saved} saved into your game." : $"{saved} added to your game.", StatusKind.Success);
        }
        else
        {
            ShowResult(receipt.Message, "FailureNotice");
            _app.Status.Show(receipt.Message, StatusKind.Failure);
        }
        await _app.Game.RescanAsync();
        // A replaced career is reopened so further changes start from what is now in the game; the reopen
        // resets the page, so the result is shown again afterwards.
        if (receipt.Ok && replace)
        {
            string shown = Result.Text;
            await _app.OpenCareer(receipt.Target);
            ShowResult(shown, "SuccessNotice");
        }
        OpenResult.Visible = receipt.Ok && !replace;
        return receipt;
    }

    /// <summary>Publishes the planned changes as a new file outside the game, then reopens it to check every byte.</summary>
    internal async Task<PublicationReceipt> SaveElsewhereAsync(string destination)
    {
        if (_app.Workspace.Busy || _app.Workspace.Session is null || _plan.Value is not EditPlan plan)
            return new PublicationReceipt(false, "Open a career and make a change first.");
        _app.Status.Show("Saving a checked copy…");
        PublicationReceipt receipt = await _app.Workspace.PublishAsync(destination, plan.CopyBytes());
        if (receipt.Ok)
        {
            _lastInstalled = "";
            ShowResult($"Saved a copy with your changes to {receipt.Output}. It was read back and matches byte for byte; your career " +
                "is unchanged.", "SuccessNotice");
            _app.Status.Show("Copy saved and checked. Your career is unchanged.", StatusKind.Success);
        }
        else
        {
            string failure = receipt.Message + (receipt.MayHaveOutput ? "\nA copy may exist at: " + (receipt.Output ?? destination) : "");
            ShowResult(failure, "FailureNotice");
            _app.Status.Show(failure, StatusKind.Failure);
        }
        OpenResult.Visible = receipt.Ok;
        UpdateActions();
        return receipt;
    }

    private void ChooseElsewhere()
    {
        if (_app.Workspace.Session is not SaveSession session) return;
        OutputDialog.CurrentDir = System.Environment.GetFolderPath(System.Environment.SpecialFolder.MyDocuments) is { Length: > 0 } documents
            ? documents : System.IO.Path.GetDirectoryName(session.Path) ?? "";
        OutputDialog.CurrentFile = System.IO.Path.GetFileNameWithoutExtension(session.Path) + " (edited).bes";
        OutputDialog.PopupCenteredRatio(0.75f);
    }

    private GameFile? InGame(SaveSession session) => _app.Game.Folder?.Careers.FirstOrDefault(career =>
        string.Equals(career.Path, session.Path, StringComparison.Ordinal));

    private string GoodieName(int index) => _app.Game.Text?.GoodieTitle(index) is string title ? $"{index:D3} {title}" : $"{index:D3}";

    private static string Verb(GoodieState state) => state switch
    {
        GoodieState.New => "unlocked (new)",
        GoodieState.Old => "unlocked (seen)",
        GoodieState.Hint => "locked with a hint",
        _ => "locked",
    };

    private void ShowGoodieRows()
    {
        _goodieRows.Clear();
        if (_app.Workspace.Session is not SaveSession session) return;
        if (_goodieTargets.Count == 0)
        {
            _goodieRows.Add(Build.Text("No Goodie changes yet.", "Faint"));
            return;
        }
        if (_goodieTargets.Count > GoodieRowsShown)
        {
            _goodieRows.Add(Build.Text($"{Build.Count(_goodieTargets.Count, "Goodie")} will change. They are listed under Your changes below.", "Strong"));
            return;
        }
        foreach ((int index, GoodieState target) in _goodieTargets)
        {
            GoodieRecord current = session.Analysis.Goodies[index];
            HBoxContainer row = _goodieRows.Add(Build.Row(12));
            Label name = row.Add(Build.Text(GoodieName(index), "Strong", wrap: false, clip: true));
            name.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            row.Add(Build.Text("now " + Verb(current.State), "Faint", wrap: false));
            OptionButton picker = row.Add(new OptionButton { CustomMinimumSize = new Vector2(190, 0) });
            foreach (GoodieState state in Targets) picker.AddItem(Capitalised(Verb(state)));
            picker.Selected = Array.IndexOf(Targets, target);
            int goodie = index;
            picker.ItemSelected += item => SetGoodieTarget(goodie, Targets[item]);
            Button remove = row.Add(Build.Button("Remove", "Link"));
            remove.Pressed += () => RemoveGoodie(goodie);
        }
    }

    private static string Capitalised(string text) => char.ToUpperInvariant(text[0]) + text[1..];

    private void ShowEmpty()
    {
        foreach (Control section in _needsCareer) section.Visible = false;
        _intro.Text = "Choose a career to change. Opening it only reads it.";
        _choose.Root.Visible = true;
        _choose.Show();
    }

    private void ShowResult(string text, string variation)
    {
        Result.Text = text;
        ResultPanel.ThemeTypeVariation = variation;
        ResultPanel.Visible = true;
        // The result sits under the changes; bring it into view wherever the player saved from.
        Callable.From(() => _scroll.EnsureControlVisible(ResultPanel)).CallDeferred();
    }
}

/// <summary>One kill category: the current count and the count it will have. A different number is a change.</summary>
internal sealed class KillRow
{
    private readonly Label _current;
    private readonly Button _reset;
    private int _value;

    internal KillRow(int category, string name)
    {
        Category = category;
        Root = Build.Row(16);
        Root.Name = name;
        Root.Add(Build.Text(name, "Strong", false, 150));
        _current = Root.Add(Build.Text("—", "Muted", false, 120));
        Root.Add(Build.Text("→", "Faint", false));
        Target = Root.Add(new SpinBox
        {
            MaxValue = CareerSave.MaxKills, Editable = false, UpdateOnTextChanged = true, CustomMinimumSize = new Vector2(200, 0),
            TooltipText = "The count the career will have.",
        });
        _reset = Root.Add(Build.Button("Reset", "Link"));
        _reset.Visible = false;
        _reset.Pressed += () => Target.Value = _value;
        Target.ValueChanged += _ =>
        {
            _reset.Visible = IsChanged;
            Changed?.Invoke();
        };
    }

    internal event Action? Changed;

    internal int Category { get; }
    internal HBoxContainer Root { get; }
    internal SpinBox Target { get; }
    internal bool IsChanged => TargetValue != _value;
    internal int TargetValue => (int)Target.Value;

    internal void SetCurrent(int value)
    {
        _value = value;
        _current.Text = $"now {value:N0}";
        Target.SetValueNoSignal(value);
        _reset.Visible = false;
    }

    internal void SetLocked(bool locked) => Target.Editable = !locked;
}
