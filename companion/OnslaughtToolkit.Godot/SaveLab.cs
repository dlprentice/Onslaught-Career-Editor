// SPDX-License-Identifier: MIT

using System.Globalization;
using Godot;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.Companion;

/// <summary>Presentation for AppCore's explicit, verified career-copy workflow.</summary>
public sealed partial class SaveLab : Control
{
    private Color Ink => GetThemeColor("font_color", "Label");
    private Color Muted => GetThemeColor("font_color", "MutedLabel");
    private Color Accent => GetThemeColor("font_color", "SuccessLabel");
    private Color ErrorInk => GetThemeColor("font_color", "ErrorLabel");
    private static readonly string[] CategoryNames = ["Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs"];
    private static readonly int[] Categories =
    [
        BesFilePatcher.KILL_AIRCRAFT, BesFilePatcher.KILL_VEHICLES,
        BesFilePatcher.KILL_EMPLACEMENTS, BesFilePatcher.KILL_INFANTRY, BesFilePatcher.KILL_MECHS,
    ];

    private SaveLabSession? _session;
    private SaveAnalysis? _analysis;
    private FileDialog _openDialog = null!;
    private FileDialog _outputDialog = null!;
    private Button _openButton = null!;
    private Button _chooseOutput = null!;
    private Button _writeButton = null!;
    private OptionButton _category = null!;
    private SpinBox _kills = null!;
    private LineEdit _sourcePath = null!;
    private LineEdit _sourceHash = null!;
    private LineEdit _outputPath = null!;
    private LineEdit _verifiedPath = null!;
    private LineEdit _verifiedHash = null!;
    private Label _sourceDetails = null!;
    private Label _changeSummary = null!;
    private Label _outputIssue = null!;
    private Label _status = null!;
    private Label _verification = null!;
    private readonly Label[] _counts = new Label[5];

    public override void _Ready()
    {
        // The scene owns the production controls, layout and theme. This script
        // is deliberately not a [Tool]: editor inspection never opens a save.
        if (Engine.IsEditorHint())
            return;

        GetWindow().MinSize = new Vector2I(900, 680);
        _openDialog = GetNode<FileDialog>("%OpenDialog");
        _outputDialog = GetNode<FileDialog>("%OutputDialog");
        _openButton = GetNode<Button>("%OpenButton");
        _chooseOutput = GetNode<Button>("%ChooseOutput");
        _writeButton = GetNode<Button>("%WriteButton");
        _category = GetNode<OptionButton>("%Category");
        _kills = GetNode<SpinBox>("%Kills");
        _sourcePath = GetNode<LineEdit>("%SourcePath");
        _sourceHash = GetNode<LineEdit>("%SourceHash");
        _outputPath = GetNode<LineEdit>("%OutputPath");
        _verifiedPath = GetNode<LineEdit>("%VerifiedPath");
        _verifiedHash = GetNode<LineEdit>("%VerifiedHash");
        _sourceDetails = GetNode<Label>("%SourceDetails");
        _changeSummary = GetNode<Label>("%ChangeSummary");
        _outputIssue = GetNode<Label>("%OutputIssue");
        _status = GetNode<Label>("%Status");
        _verification = GetNode<Label>("%Verification");
        for (int index = 0; index < CategoryNames.Length; index++)
            _counts[index] = GetNode<Label>("%" + CategoryNames[index] + "Count");

        // Backend limits and destructive-dialog restrictions are safety policy,
        // so a layout edit cannot silently relax them.
        _kills.MaxValue = SaveLabService.MaximumKillCount;
        ConfigurePathSelection(_openDialog, FileDialog.FileModeEnum.OpenFile);
        ConfigurePathSelection(_outputDialog, FileDialog.FileModeEnum.SaveFile);
        _outputDialog.OverwriteWarningEnabled = false;
        _openButton.Pressed += OpenDialog;
        _chooseOutput.Pressed += ChooseOutputDialog;
        _writeButton.Pressed += WriteCopy;
        _category.ItemSelected += _ => SelectCategory();
        _kills.ValueChanged += _ => RefreshPlan();
        _outputPath.TextChanged += _ => RefreshPlan();
        _openDialog.FileSelected += OpenSelected;
        _outputDialog.FileSelected += path =>
        {
            _outputPath.Text = path;
            _outputPath.TooltipText = path;
            RefreshPlan();
            if (!_writeButton.Disabled)
                _writeButton.GrabFocus();
        };
        _openButton.GrabFocus();
    }

    public override void _UnhandledKeyInput(InputEvent inputEvent)
    {
        if (inputEvent is InputEventKey { Pressed: true, Echo: false, CtrlPressed: true } key &&
            (key.Keycode == Key.O || key.PhysicalKeycode == Key.O))
        {
            OpenDialog();
            GetViewport().SetInputAsHandled();
        }
    }

    private void OpenDialog() => ShowDialog(_openDialog);

    private void ChooseOutputDialog()
    {
        if (_session is null)
            return;
        _outputDialog.CurrentDir = Path.GetDirectoryName(_session.InputPath)!;
        _outputDialog.CurrentFile = Path.GetFileNameWithoutExtension(_session.InputPath) + "-edited.bes";
        ShowDialog(_outputDialog);
    }

    private void ShowDialog(FileDialog dialog)
    {
        Vector2I size = GetWindow().Size;
        dialog.PopupCentered(new Vector2I(Math.Min(880, size.X - 48), Math.Min(620, size.Y - 48)));
    }

    private void OpenSelected(string path)
    {
        ClearReceipt();
        SaveLabOpenResult result = SaveLabService.Open(path);
        _session = result.Session;
        _analysis = _session?.Analysis;
        _sourcePath.Text = _session?.InputPath ?? path;
        _sourcePath.TooltipText = _sourcePath.Text;
        _sourceHash.Text = _session?.InputSha256 ?? string.Empty;
        _sourceDetails.Text = _analysis is null ? "No supported career is open." :
            $"{_session!.FileSize:N0} bytes   •   Version 0x{_analysis.VersionWord:X4}   •   " +
            $"{_analysis.CompletedNodes} completed levels   •   Career in progress: {(_analysis.CareerInProgressOn ? "yes" : "no")}";
        for (int index = 0; index < _counts.Length; index++)
            _counts[index].Text = _analysis?.KillCounts[Categories[index]].ToString("N0", CultureInfo.CurrentCulture) ?? "—";
        _category.Disabled = _session is null;
        _kills.Editable = _session is not null;
        _chooseOutput.Disabled = _session is null;
        _outputPath.Text = string.Empty;
        _outputPath.TooltipText = string.Empty;
        SelectCategory();
        SetStatus(result.Message, result.Success ? Accent : ErrorInk);
        if (result.Success)
            _category.GrabFocus();
    }

    private void SelectCategory()
    {
        if (_analysis is not null)
            _kills.Value = _analysis.KillCounts[Categories[_category.Selected]];
        RefreshPlan();
    }

    private void RefreshPlan()
    {
        if (_analysis is null)
        {
            _changeSummary.Text = "Choose a career first.";
            _outputIssue.Text = "Choose an existing folder and a fresh filename.";
            _outputIssue.AddThemeColorOverride("font_color", Muted);
            _writeButton.Disabled = true;
            return;
        }
        int selected = _category.Selected;
        int original = _analysis.KillCounts[Categories[selected]];
        int proposed = (int)_kills.Value;
        _changeSummary.Text = original == proposed
            ? $"Current count: {original:N0}. Enter a different value."
            : $"{CategoryNames[selected]}: {original:N0} → {proposed:N0}. Other counts stay as opened.";
        bool hasOutput = !string.IsNullOrWhiteSpace(_outputPath.Text);
        bool exists = hasOutput && (File.Exists(_outputPath.Text) || Directory.Exists(_outputPath.Text));
        _writeButton.Disabled = original == proposed || !hasOutput || exists;
        _outputIssue.Text = exists ? "That output already exists. Choose a new filename." :
            hasOutput ? "A new file will be created at the selected path." : "Choose an existing folder and a fresh filename.";
        _outputIssue.AddThemeColorOverride("font_color", exists ? ErrorInk : Muted);
    }

    private void WriteCopy()
    {
        if (_session is null)
            return;
        _kills.Apply();
        int category = Categories[_category.Selected];
        int kills = (int)_kills.Value;
        ClearReceipt();
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(_session, _outputPath.Text, category, kills);
        _verifiedPath.Text = result.OutputPath ?? string.Empty;
        _verifiedPath.TooltipText = _verifiedPath.Text;
        if (!result.Success || result.OutputPath is null)
        {
            RefreshPlan();
            SetStatus(result.Message, ErrorInk);
            return;
        }

        // Reopen through the same service after its write-time verification.
        // The UI never parses or modifies save bytes itself.
        SaveLabOpenResult reopened = SaveLabService.Open(result.OutputPath);
        if (!reopened.Success || reopened.Session is null ||
            !string.Equals(reopened.Session.InputSha256, result.OutputSha256, StringComparison.OrdinalIgnoreCase) ||
            reopened.Session.Analysis.KillCounts[category] != kills)
        {
            RefreshPlan();
            SetStatus("The new copy exists, but reopening it did not confirm the written result. " + reopened.Message, ErrorInk);
            return;
        }
        _verifiedHash.Text = reopened.Session.InputSha256;
        _verification.Text =
            $"Original matched at write time: {(result.OriginalVerified ? "verified" : "not verified")}\n" +
            $"Every untargeted byte preserved: {(result.UntargetedBytesVerified ? "verified" : "not verified")}\n" +
            $"Changed bytes: {result.ChangedBytes:N0}   •   Reopened {CategoryNames[_category.Selected]} count: {kills:N0}";
        _verification.AddThemeColorOverride("font_color", Ink);
        RefreshPlan();
        SetStatus("New copy reopened and verified.", Accent);
    }

    private void ClearReceipt()
    {
        _verifiedPath.Text = string.Empty;
        _verifiedHash.Text = string.Empty;
        _verification.Text = "Verification results will appear here after a new copy is written.";
        _verification.AddThemeColorOverride("font_color", Muted);
    }

    private void SetStatus(string message, Color color)
    {
        _status.Text = message;
        _status.AddThemeColorOverride("font_color", color);
    }

    private static void ConfigurePathSelection(FileDialog dialog, FileDialog.FileModeEnum mode)
    {
        dialog.Access = FileDialog.AccessEnum.Filesystem;
        dialog.FileMode = mode;
        dialog.UseNativeDialog = false;
        dialog.DeletingEnabled = false;
        dialog.FolderCreationEnabled = false;
        dialog.RecentListEnabled = false;
    }
}
