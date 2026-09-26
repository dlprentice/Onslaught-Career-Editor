// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// Select changes, preview every byte that moves, then publish and verify a separate copy.
/// The open original always remains the source.
/// </summary>
internal sealed class EditCopyPage : Page
{
    private static readonly GoodieState[] Targets = [GoodieState.Locked, GoodieState.Hint, GoodieState.New, GoodieState.Old];

    private readonly CareerWorkspace _workspace;
    private readonly GameLibrary _game;
    private readonly SortedDictionary<int, GoodieState> _goodieTargets = [];
    private readonly VBoxContainer _goodieRows;
    private readonly SpinBox _goodieIndex;
    private readonly Button _addGoodie;
    private readonly StatusLine _status;
    private readonly Func<string, Task> _openCareer;
    private readonly VBoxContainer _content;
    private readonly Label _empty;
    private readonly List<Control> _needsCareer = [];
    private Outcome<EditPlan> _plan = Outcome<EditPlan>.Refusal("Choose a change.");

    internal EditCopyPage(CareerWorkspace workspace, GameLibrary game, StatusLine status, Node popups, Func<string, Task> openCareer)
        : base("edit", "Edit a copy")
    {
        (_workspace, _game, _status, _openCareer) = (workspace, game, status, openCareer);
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        (Root, _content) = (scroll, content);
        content.Add(Build.Notice("Every change is written to a new file that is checked byte for byte. " +
            "Your original is never modified and stays the source for every copy.").Panel);
        _empty = content.Add(Build.Text("Open a career to choose changes.", "Muted"));

        (PanelContainer source, VBoxContainer sourceBody) = Build.Card("Source career");
        SourceDetails = sourceBody.Add(Build.Detail("", bbcode: true));
        _needsCareer.Add(content.Add(source));

        (PanelContainer kills, VBoxContainer killBody) = Build.Card("Kill counts");
        killBody.Add(Build.Text("Tick a category to change it. Only the three count bytes change; the fourth byte, which " +
            "holds the stored screen-position setting on the first two rows, is kept.", "Muted"));
        HBoxContainer header = killBody.Add(Build.Row(16));
        header.Add(Build.Spacer()).CustomMinimumSize = new Vector2(34, 0);
        header.Add(Build.Text("CATEGORY", "Eyebrow", false, 150));
        header.Add(Build.Text("NOW", "Eyebrow", false, 110));
        header.Add(Build.Text("NEW VALUE", "Eyebrow", false, 210));
        header.Add(Build.Text("TOP BYTE", "Eyebrow", false));
        Rows = CareerSave.CategoryNames.Select((name, index) => new KillEditRow(index, name)).ToArray();
        foreach (KillEditRow row in Rows)
        {
            killBody.Add(row.Root);
            row.SelectionChanged += RefreshPreview;
        }
        _needsCareer.Add(content.Add(kills));

        (PanelContainer goodies, VBoxContainer goodieBody) = Build.Card("Goodie states");
        goodieBody.Add(Build.Text("Add Goodies from the Goodies page or by number. Only each chosen Goodie's four bytes change. " +
            "Loading a Goodie as new has been seen in the game only for Goodie 002; how the game handles other changes has not " +
            "been watched in play.", "Muted"));
        _goodieRows = goodieBody.Add(Build.Column(6));
        HBoxContainer addRow = goodieBody.Add(Build.Row(10));
        addRow.Add(Build.Text("Goodie number", "Muted", wrap: false));
        _goodieIndex = addRow.Add(new SpinBox { MaxValue = CareerSave.GoodieTable - 1, CustomMinimumSize = new Vector2(110, 0) });
        _addGoodie = addRow.Add(Build.Button("Add Goodie", disabled: true));
        _addGoodie.Pressed += () => AddGoodie((int)_goodieIndex.Value);
        _needsCareer.Add(content.Add(goodies));

        (PanelContainer preview, VBoxContainer previewBody) = Build.Card("Preview");
        Preview = previewBody.Add(Build.Detail("", bbcode: true));
        _needsCareer.Add(content.Add(preview));

        (PanelContainer write, VBoxContainer writeBody) = Build.Card("Write a new copy");
        writeBody.Add(Build.Text("Choose a new file name in an existing folder outside the game. Existing files are never " +
            "replaced; to put a copy into the game, use Install & backups.", "Muted"));
        HBoxContainer destinationRow = writeBody.Add(Build.Row(10));
        Destination = destinationRow.Add(new LineEdit
        {
            SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, ThemeTypeVariation = "MonoField",
            PlaceholderText = "/path/to/a-new-career.bes",
        });
        ChooseOutput = destinationRow.Add(Build.Button("Choose…", disabled: true));
        HBoxContainer actions = writeBody.Add(Build.Row(10));
        WriteCopy = actions.Add(Build.Button("Write verified copy", "Primary", disabled: true));
        BackupCopy = actions.Add(Build.Button("Unchanged recovery copy", disabled: true,
            tooltip: "A byte-identical copy of the original, ignoring the changes above."));
        ReopenCopy = actions.Add(Build.Button("Open the new copy", disabled: true,
            tooltip: "Make the verified copy the open career."));
        (PanelContainer resultPanel, Label result) = Build.Notice(
            "A new copy is reopened and compared with the preview before it is offered for use.");
        (ResultPanel, Result) = (resultPanel, result);
        writeBody.Add(resultPanel);
        _needsCareer.Add(content.Add(write));

        OutputDialog = popups.Add(Build.FilePicker("Choose a new copy file name", FileDialog.FileModeEnum.SaveFile, "*.bes ; Career saves"));
        ChooseOutput.Pressed += ChooseDestination;
        OutputDialog.FileSelected += path =>
        {
            Build.ShowPath(Destination, path);
            UpdateActions();
        };
        Destination.TextChanged += _ => UpdateActions();
        WriteCopy.Pressed += () => _status.Track(WriteCopyAsync(unchanged: false));
        BackupCopy.Pressed += () => _status.Track(WriteCopyAsync(unchanged: true));
        ReopenCopy.Pressed += () => _status.Track(_openCareer(_workspace.LastVerifiedOutput));
        ShowEmpty();
    }

    internal override Control Root { get; }
    internal override string Subtitle => _workspace.Session is SaveSession session
        ? $"From {System.IO.Path.GetFileName(session.Path)}"
        : "Changes are always written to a new, verified file";

    internal IReadOnlyList<KillEditRow> Rows { get; }
    internal IReadOnlyDictionary<int, GoodieState> GoodieTargets => _goodieTargets;
    internal IReadOnlyList<OptionButton> GoodiePickers => _goodieRows.GetChildren().OfType<HBoxContainer>()
        .SelectMany(row => row.GetChildren().OfType<OptionButton>()).ToArray();
    internal RichTextLabel SourceDetails { get; }
    internal RichTextLabel Preview { get; }
    internal PanelContainer ResultPanel { get; }
    internal Label Result { get; }
    internal LineEdit Destination { get; }
    internal Button ChooseOutput { get; }
    internal Button WriteCopy { get; }
    internal Button BackupCopy { get; }
    internal Button ReopenCopy { get; }
    internal FileDialog OutputDialog { get; }

    internal void ShowSession(SaveSession session)
    {
        CareerInspection analysis = session.Analysis;
        _plan = Outcome<EditPlan>.Refusal("Choose a change.");
        Destination.Text = "";
        ShowResult("Your original is open. Choose a new file name for an edited or unchanged copy.", "Notice");
        SourceDetails.Text = $"[b]{Escape(session.Path)}[/b]\n" +
            $"10,004 bytes  ·  version 0x{analysis.Version:X4}  ·  {analysis.MissionCensus.Completed} of " +
            $"{analysis.MissionCensus.Used} missions complete\n[code]SHA-256 {session.Sha256}\nfile identity {session.Identity}[/code]";
        foreach (KillEditRow row in Rows) row.SetCurrent(analysis.Kills[row.Category], analysis.PackedBytes[row.Category]);
        _goodieTargets.Clear();
        ShowGoodieRows();
        foreach (Control section in _needsCareer) section.Visible = true;
        _empty.Visible = false;
        RefreshPreview();
    }

    internal void UpdateActions()
    {
        bool ready = _workspace.Session is not null && !_workspace.Busy;
        bool hasDestination = Destination.Text.Trim().Length > 0;
        ChooseOutput.Disabled = !ready;
        Destination.Editable = !_workspace.Busy;
        WriteCopy.Disabled = !ready || !_plan.Ok || !hasDestination;
        BackupCopy.Disabled = !ready || !hasDestination;
        ReopenCopy.Disabled = _workspace.Busy || _workspace.LastVerifiedOutput.Length == 0;
        foreach (KillEditRow row in Rows) row.SetLocked(!ready);
        _addGoodie.Disabled = !ready;
    }

    /// <summary>Adds a Goodie to the plan, aiming at a different state than it has now.</summary>
    internal void AddGoodie(int index)
    {
        if (_workspace.Session is not SaveSession session || index < 0 || index >= CareerSave.GoodieTable) return;
        if (!CareerSave.IsShown(index))
        {
            _status.Show($"Goodie {index:D3} is never shown in the game's gallery, so its state is kept as it is.", StatusKind.Failure);
            return;
        }
        if (!_goodieTargets.ContainsKey(index))
            _goodieTargets[index] = session.Analysis.Goodies[index].State == GoodieState.New ? GoodieState.Old : GoodieState.New;
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

    private void ShowGoodieRows()
    {
        _goodieRows.Clear();
        if (_workspace.Session is not SaveSession session) return;
        if (_goodieTargets.Count == 0) _goodieRows.Add(Build.Text("No Goodies chosen.", "Faint"));
        foreach ((int index, GoodieState target) in _goodieTargets)
        {
            GoodieRecord current = session.Analysis.Goodies[index];
            HBoxContainer row = _goodieRows.Add(Build.Row(12));
            row.Add(Build.Text($"GOODIE {index:D3}", "Strong", wrap: false, width: 104));
            Label title = row.Add(Build.Text(_game.Text?.GoodieTitle(index) ?? "", "Muted", wrap: false, clip: true));
            title.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            row.Add(Build.Text("now " + GoodieFacts.StateName(current.State).Split(' ')[0].ToLowerInvariant(), "Faint", wrap: false, width: 90));
            OptionButton picker = row.Add(new OptionButton { CustomMinimumSize = new Vector2(150, 0) });
            foreach (GoodieState state in Targets) picker.AddItem(state == GoodieState.Hint ? "Hint shown" : state == GoodieState.Old ? "Viewed" : state.ToString());
            picker.Selected = Array.IndexOf(Targets, target);
            int goodie = index;
            picker.ItemSelected += item => SetGoodieTarget(goodie, Targets[item]);
            GoodieEvidence evidence = GoodieFacts.Evidence(index);
            row.Add(Build.Text(evidence == GoodieEvidence.SeenInGame ? "seen in the game" : "not watched in play",
                evidence == GoodieEvidence.SeenInGame ? "Good" : "Faint", wrap: false, width: 130));
            Button remove = row.Add(Build.Button("Remove", "Link"));
            remove.Pressed += () => RemoveGoodie(goodie);
        }
    }

    internal void RefreshPreview()
    {
        if (_workspace.Session is not SaveSession session) return;
        Dictionary<int, int> selected = Rows.Where(row => row.IsSelected).ToDictionary(row => row.Category, row => row.TargetValue);
        _plan = session.Prepare(new EditRequest(selected, new Dictionary<int, GoodieState>(_goodieTargets)));
        if (_plan.Value is not EditPlan plan)
        {
            Preview.Text = $"[color=#{Palette.Muted.ToHtml(false)}]{Escape(_plan.Message)} An unchanged recovery copy is " +
                "available below without choosing a change.[/color]";
        }
        else
        {
            string edits = string.Join("\n", plan.Selected.Select(edit => $"{edit.Name}: {edit.Before:N0} → [b]{edit.After:N0}[/b]")
                .Concat(plan.Goodies.Select(edit => $"Goodie {edit.Index:D3}: {GoodieFacts.StateName(new GoodieRecord(edit.Index, edit.Offset, edit.Before).State)} → " +
                    $"[b]{GoodieFacts.StateName(edit.After)}[/b]")));
            string bytes = string.Join("   ", plan.Changes.Select(change => $"0x{change.Offset:X4} {change.Before:X2}→{change.After:X2}"));
            Preview.Text = $"{edits}\n[color=#{Palette.Data.ToHtml(false)}]{plan.ChangedBytes} changed bytes;[/color] length and " +
                $"every other byte preserved.\n[code]{bytes}[/code]";
        }
        UpdateActions();
    }

    /// <summary>Publishes the previewed edit, or an unchanged copy of the original, to the chosen new file.</summary>
    internal async Task<PublicationReceipt> WriteCopyAsync(bool unchanged)
    {
        if (_workspace.Busy || _workspace.Session is not SaveSession session)
            return new PublicationReceipt(false, "Open a career first.");
        RefreshPreview();
        if (!unchanged && _plan.Value is null) return new PublicationReceipt(false, _plan.Message);
        string destination = Destination.Text.Trim();
        if (destination.Length == 0) return new PublicationReceipt(false, "Choose a new destination.");
        byte[] prepared = unchanged ? session.CopyBytes() : _plan.Value!.CopyBytes();
        int changed = unchanged ? 0 : _plan.Value!.ChangedBytes;
        _status.Show("Checking the original and publishing the separate copy…");
        PublicationReceipt receipt = await _workspace.PublishAsync(destination, prepared);
        if (receipt.Ok)
        {
            ShowResult($"Written and verified: {receipt.Output}\n{changed} changed bytes, 10,004 bytes in total. The original's " +
                $"identity and content were checked again, and every unselected byte is unchanged.\nSHA-256 {receipt.Sha256.ToLowerInvariant()}",
                "SuccessNotice");
            _status.Show(unchanged ? "Unchanged recovery copy written and verified." : "Edited copy written and verified. Your original is unchanged.",
                StatusKind.Success);
        }
        else
        {
            string failure = receipt.Message;
            if (receipt.MayHaveOutput) failure += "\nA copy may exist at: " + (receipt.Output ?? destination);
            ShowResult(failure, "FailureNotice");
            _status.Show(failure, StatusKind.Failure);
        }
        UpdateActions();
        await Root.ToSignal(Root.GetTree(), SceneTree.SignalName.ProcessFrame);
        ((ScrollContainer)Root).EnsureControlVisible(ResultPanel);
        return receipt;
    }

    internal override void Refresh() => UpdateActions();

    private void ShowEmpty()
    {
        foreach (Control section in _needsCareer) section.Visible = false;
        _empty.Visible = true;
    }

    private void ShowResult(string text, string variation)
    {
        Result.Text = text;
        ResultPanel.ThemeTypeVariation = variation;
    }

    private void ChooseDestination()
    {
        if (_workspace.Session is not SaveSession session || _workspace.Busy) return;
        OutputDialog.CurrentDir = System.IO.Path.GetDirectoryName(session.Path) ?? "";
        OutputDialog.CurrentFile = System.IO.Path.GetFileNameWithoutExtension(session.Path) + "-copy.bes";
        OutputDialog.PopupCenteredRatio(0.75f);
    }

    private static string Escape(string text) => text.Replace("[", "[lb]");
}

/// <summary>One kill category. Only a ticked row enters an edit plan.</summary>
internal sealed class KillEditRow
{
    private readonly Label _current;
    private readonly Label _packed;

    internal KillEditRow(int category, string name)
    {
        Category = category;
        Root = Build.Row(16);
        Root.Name = name;
        Selected = Root.Add(new CheckBox { Disabled = true, TooltipText = "Include this category in the preview and copy." });
        Selected.CustomMinimumSize = new Vector2(34, 0);
        Root.Add(Build.Text(name, "Strong", false, 150));
        _current = Root.Add(Build.Text("—", "Mono", false, 110));
        Target = Root.Add(new SpinBox
        {
            MaxValue = CareerSave.MaxKills, Editable = false, UpdateOnTextChanged = true, CustomMinimumSize = new Vector2(210, 0),
        });
        _packed = Root.Add(Build.Text("", "MonoMuted", false));
        Selected.Toggled += _ => SelectionChanged?.Invoke();
        Target.ValueChanged += _ => SelectionChanged?.Invoke();
    }

    internal event Action? SelectionChanged;

    internal int Category { get; }
    internal HBoxContainer Root { get; }
    internal CheckBox Selected { get; }
    internal SpinBox Target { get; }
    internal bool IsSelected => Selected.ButtonPressed;
    internal int TargetValue => (int)Target.Value;

    internal void SetCurrent(int value, int packed)
    {
        _current.Text = value.ToString("N0");
        _packed.Text = $"0x{packed:X2} kept";
        Selected.SetPressedNoSignal(false);
        Target.SetValueNoSignal(value);
    }

    internal void SetLocked(bool locked)
    {
        Selected.Disabled = locked;
        Target.Editable = !locked;
    }
}
