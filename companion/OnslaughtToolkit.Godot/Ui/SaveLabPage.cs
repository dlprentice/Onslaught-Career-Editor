// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// Inspect the original, select counts, preview every changed byte, then publish and verify a
/// separate copy. The original always remains the open source.
/// </summary>
internal sealed class SaveLabPage
{
    private readonly CareerWorkspace _workspace;
    private readonly StatusLine _status;
    private readonly Func<string, Task> _openCareer;
    private Outcome<EditPlan> _plan = Outcome<EditPlan>.Refusal("Choose an edit.");

    internal SaveLabPage(CareerWorkspace workspace, StatusLine status, Node popups, Func<string, Task> openCareer)
    {
        (_workspace, _status, _openCareer) = (workspace, status, openCareer);
        Root = new ScrollContainer { Name = "Save Lab", HorizontalScrollMode = ScrollContainer.ScrollMode.Disabled };
        VBoxContainer content = Root.Add(Build.Column(14));
        content.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;

        content.Add(Build.Text("1   Inspect your original", CompanionTheme.SectionSize));
        SourceDetails = content.Add(Build.Detail(
            "Open a career to inspect its version, content fingerprint and stored values.\n" +
            "Your original stays the source for every new copy.", 90));

        content.Add(Build.Text("2   Select the counts to change", CompanionTheme.SectionSize));
        content.Add(Build.Text("Check each category you want to edit. Only its three count bytes can change; " +
            "the packed fourth byte and all other data are preserved."));
        HBoxContainer labels = content.Add(Build.Row(16));
        labels.Add(new Control { CustomMinimumSize = new Vector2(60, 0), MouseFilter = Control.MouseFilterEnum.Ignore });
        labels.Add(Build.Fixed("Category", 148));
        labels.Add(Build.Fixed("Original", 120));
        labels.Add(Build.Fixed("Proposed", 210));
        labels.Add(new Label { Text = "Packed byte" });
        VBoxContainer rows = content.Add(new VBoxContainer());
        Rows = CareerSave.CategoryNames.Select((name, index) => new KillEditRow(index, name)).ToArray();
        foreach (KillEditRow row in Rows)
        {
            rows.Add(row.Root);
            row.SelectionChanged += RefreshPreview;
        }
        Preview = content.Add(Build.Detail("Preview will show the intended values and every byte that changes.", 80));

        content.Add(Build.Text("3   Write and verify a separate copy", CompanionTheme.SectionSize));
        HBoxContainer destinationRow = content.Add(Build.Row(12));
        Destination = destinationRow.Add(new LineEdit
        {
            SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            PlaceholderText = "Choose a new .bes filename in an existing folder",
            TooltipText = "Existing files and paths inside the game installation are refused.",
        });
        ChooseOutput = destinationRow.Add(Build.Button("Choose…", disabled: true));
        HBoxContainer actions = content.Add(Build.Row(12));
        WriteCopy = actions.Add(Build.Button("Write verified edit", disabled: true));
        BackupCopy = actions.Add(Build.Button("Make unchanged recovery copy", disabled: true));
        ReopenCopy = actions.Add(Build.Button("Open verified result", disabled: true));
        Result = content.Add(Build.Detail(
            "A successful copy is reopened and compared with the preview before it is offered for use.", 65));
        OutputDialog = popups.Add(Build.FilePicker("Choose a new copy filename", FileDialog.FileModeEnum.SaveFile,
            "*.bes ; Career saves"));

        ChooseOutput.Pressed += ChooseDestination;
        OutputDialog.FileSelected += path =>
        {
            Destination.Text = path;
            UpdateActions();
        };
        Destination.TextChanged += _ => UpdateActions();
        WriteCopy.Pressed += () => _status.Track(WriteCopyAsync(unchanged: false));
        BackupCopy.Pressed += () => _status.Track(WriteCopyAsync(unchanged: true));
        ReopenCopy.Pressed += () => _status.Track(_openCareer(_workspace.LastVerifiedOutput));
    }

    internal ScrollContainer Root { get; }
    internal IReadOnlyList<KillEditRow> Rows { get; }
    internal RichTextLabel SourceDetails { get; }
    internal RichTextLabel Preview { get; }
    internal RichTextLabel Result { get; }
    internal LineEdit Destination { get; }
    internal Button ChooseOutput { get; }
    internal Button WriteCopy { get; }
    internal Button BackupCopy { get; }
    internal Button ReopenCopy { get; }
    internal FileDialog OutputDialog { get; }

    internal void ShowSession(SaveSession session)
    {
        CareerInspection analysis = session.Analysis;
        _plan = Outcome<EditPlan>.Refusal("Choose an edit.");
        Destination.Text = "";
        Result.Text = "Your original is open. Choose a fresh destination for an edit or an unchanged recovery copy.";
        SourceDetails.Text = $"{session.Path}\n10,004 bytes  •  Version word 0x{analysis.Version:X4}  •  " +
            $"{analysis.MissionCensus.Completed} completed / {analysis.MissionCensus.Used} used mission records\n" +
            $"SHA-256  {session.Sha256}\nFile identity  {session.Identity}";
        foreach (KillEditRow row in Rows) row.SetCurrent(analysis.Kills[row.Category], analysis.PackedBytes[row.Category]);
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
    }

    internal void RefreshPreview()
    {
        if (_workspace.Session is not SaveSession session) return;
        Dictionary<int, int> selected = Rows.Where(row => row.IsSelected).ToDictionary(row => row.Category, row => row.TargetValue);
        _plan = session.Prepare(selected);
        if (_plan.Value is not EditPlan plan)
        {
            Preview.Text = _plan.Message + "\nAn unchanged recovery copy is available separately.";
        }
        else
        {
            string edits = string.Join("   •   ", plan.Selected.Select(edit => $"{edit.Name}: {edit.Before:N0} → {edit.After:N0}"));
            string bytes = string.Join("   ", plan.Changes.Select(change => $"0x{change.Offset:X4}: {change.Before:X2} → {change.After:X2}"));
            Preview.Text = $"{edits}\n{plan.ChangedBytes} changed bytes; length and all unselected bytes preserved.\n{bytes}";
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
        _status.Show("Verifying the original and publishing the separate copy…");
        PublicationReceipt receipt = await _workspace.PublishAsync(destination, prepared);
        if (receipt.Ok)
        {
            Result.Text = $"{receipt.Output}\nReopened and verified: {changed} changed bytes, 10,004 bytes total. " +
                "Original identity/content and every unselected byte verified.\n" +
                $"SHA-256  {receipt.Sha256.ToLowerInvariant()}";
            _status.Show(unchanged
                ? "Unchanged recovery copy reopened and verified."
                : "Edited copy reopened and verified. Your original remains the source.");
        }
        else
        {
            string failure = receipt.Message;
            if (receipt.MayHaveOutput) failure += "\nA copy may exist at: " + (receipt.Output ?? destination);
            Result.Text = failure;
            _status.Show(failure, failed: true);
        }
        UpdateActions();
        await Root.ToSignal(Root.GetTree(), SceneTree.SignalName.ProcessFrame);
        Root.EnsureControlVisible(Result);
        return receipt;
    }

    private void ChooseDestination()
    {
        if (_workspace.Session is not SaveSession session || _workspace.Busy) return;
        OutputDialog.CurrentDir = System.IO.Path.GetDirectoryName(session.Path) ?? "";
        OutputDialog.CurrentFile = System.IO.Path.GetFileNameWithoutExtension(session.Path) + "-copy.bes";
        OutputDialog.PopupCenteredRatio(0.75f);
    }
}
