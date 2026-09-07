// SPDX-License-Identifier: MIT

using System.Globalization;
using Godot;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.Companion;

/// <summary>Presentation for AppCore's explicit, verified career-copy workflow.</summary>
public sealed partial class SaveLab : Control
{
    private static readonly Color Ink = new("e6edf5");
    private static readonly Color Muted = new("9daec2");
    private static readonly Color Accent = new("79dbc7");
    private static readonly Color ErrorInk = new("ffb3a9");
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
        Theme = CreateTheme();
        GetWindow().MinSize = new Vector2I(900, 680);

        var scroll = new ScrollContainer
        {
            HorizontalScrollMode = ScrollContainer.ScrollMode.Disabled,
            FollowFocus = true,
        };
        AddChild(scroll);
        scroll.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        var margin = new MarginContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill };
        foreach (string side in new[] { "left", "top", "right", "bottom" })
            margin.AddThemeConstantOverride($"margin_{side}", 28);
        scroll.AddChild(margin);
        var page = Stack(18);
        margin.AddChild(page);

        page.AddChild(MakeLabel("ONSLAUGHT TOOLKIT", 13, Accent));
        page.AddChild(MakeLabel("Save Lab", 32));
        page.AddChild(MakeLabel("Inspect a career and change one kill count in a new, verified copy.", 16, Muted));

        var source = Card(page, "1   Open a career");
        var openRow = new HBoxContainer();
        openRow.AddThemeConstantOverride("separation", 12);
        source.AddChild(openRow);
        _openButton = MakeButton("Open career…", OpenDialog, "Choose a real .bes file. Ctrl+O");
        openRow.AddChild(_openButton);
        var sourceHint = MakeLabel("Your chosen file is the source for each new copy.", 14, Muted);
        sourceHint.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        sourceHint.SizeFlagsVertical = SizeFlags.ShrinkCenter;
        openRow.AddChild(sourceHint);
        _sourcePath = PathField(source, "Original file", "No career selected");
        _sourceDetails = MakeLabel("Open a supported career save to inspect its contents.", 14, Muted);
        source.AddChild(_sourceDetails);
        _sourceHash = PathField(source, "Original SHA-256", "Shown after opening");

        var edit = Card(page, "2   Prepare a new copy");
        var columns = new HBoxContainer();
        columns.AddThemeConstantOverride("separation", 32);
        edit.AddChild(columns);
        var counts = new GridContainer { Columns = 2, CustomMinimumSize = new Vector2(290, 0) };
        counts.AddThemeConstantOverride("h_separation", 32);
        counts.AddThemeConstantOverride("v_separation", 10);
        columns.AddChild(counts);
        for (int index = 0; index < CategoryNames.Length; index++)
        {
            Label categoryLabel = MakeLabel(CategoryNames[index], 16, Muted);
            categoryLabel.CustomMinimumSize = new Vector2(150, 0);
            counts.AddChild(categoryLabel);
            _counts[index] = MakeLabel("—", 16);
            _counts[index].CustomMinimumSize = new Vector2(105, 0);
            _counts[index].HorizontalAlignment = HorizontalAlignment.Right;
            _counts[index].SizeFlagsHorizontal = SizeFlags.ExpandFill;
            counts.AddChild(_counts[index]);
        }

        var controls = Stack(9);
        controls.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        columns.AddChild(controls);
        controls.AddChild(MakeLabel("Category to change", 13, Muted));
        _category = new OptionButton { Disabled = true, CustomMinimumSize = new Vector2(0, 38) };
        foreach (string category in CategoryNames)
            _category.AddItem(category);
        _category.ItemSelected += _ => SelectCategory();
        controls.AddChild(_category);
        controls.AddChild(MakeLabel("New kill count", 13, Muted));
        _kills = new SpinBox
        {
            MinValue = 0, MaxValue = SaveLabService.MaximumKillCount, Step = 1,
            Rounded = true, Editable = false, SelectAllOnFocus = true,
            UpdateOnTextChanged = true, CustomMinimumSize = new Vector2(0, 38),
        };
        _kills.ValueChanged += _ => RefreshPlan();
        controls.AddChild(_kills);
        _changeSummary = MakeLabel("Choose a career first.", 14, Muted);
        controls.AddChild(_changeSummary);

        var outputRow = new HBoxContainer();
        outputRow.AddThemeConstantOverride("separation", 12);
        edit.AddChild(MakeLabel("New output filename", 13, Muted));
        edit.AddChild(outputRow);
        _outputPath = new LineEdit
        {
            Editable = false, PlaceholderText = "Choose a new .bes filename…",
            SizeFlagsHorizontal = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(0, 38),
        };
        _outputPath.TextChanged += _ => RefreshPlan();
        outputRow.AddChild(_outputPath);
        _chooseOutput = MakeButton("Choose output…", ChooseOutputDialog, "Choose where to create the new .bes file.");
        _chooseOutput.Disabled = true;
        outputRow.AddChild(_chooseOutput);
        _outputIssue = MakeLabel("Choose an existing folder and a fresh filename.", 13, Muted);
        edit.AddChild(_outputIssue);
        var actionRow = new HBoxContainer();
        edit.AddChild(actionRow);
        _writeButton = MakeButton("Write verified copy", WriteCopy, "Create the selected new file, then reopen and verify it.");
        _writeButton.Disabled = true;
        _writeButton.AddThemeColorOverride("font_color", new Color("092c28"));
        _writeButton.AddThemeStyleboxOverride("normal", Box(Accent, Accent));
        _writeButton.AddThemeStyleboxOverride("hover", Box(new Color("a2f1e0"), Accent));
        _writeButton.AddThemeStyleboxOverride("pressed", Box(new Color("51bba5"), Accent));
        actionRow.AddChild(_writeButton);

        var result = Card(page, "3   Verification");
        _status = MakeLabel("Ready to open a career save.", 16, Muted);
        result.AddChild(_status);
        _verification = MakeLabel("A successful write checks the original and every byte outside the selected count.", 14, Muted);
        result.AddChild(_verification);
        _verifiedPath = PathField(result, "Output file", "No copy written");
        _verifiedHash = PathField(result, "Reopened output SHA-256", "Shown after verification");
        page.AddChild(MakeLabel("Ctrl+O: open career     •     Tab / Shift+Tab: move between controls     •     Enter: activate", 13, Muted));

        _openDialog = MakeDialog(FileDialog.FileModeEnum.OpenFile, "Open a career save");
        _openDialog.FileSelected += OpenSelected;
        _outputDialog = MakeDialog(FileDialog.FileModeEnum.SaveFile, "Choose a new copy filename");
        // This dialog selects a destination only. The service refuses existing
        // files; an overwrite confirmation would offer an action we never take.
        _outputDialog.OverwriteWarningEnabled = false;
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

    private FileDialog MakeDialog(FileDialog.FileModeEnum mode, string title)
    {
        var dialog = new FileDialog
        {
            Access = FileDialog.AccessEnum.Filesystem, FileMode = mode,
            ModeOverridesTitle = false, Title = title, Filters = ["*.bes ; Battle Engine Aquila career saves"],
            UseNativeDialog = false, Exclusive = true, DeletingEnabled = false,
            FolderCreationEnabled = false, RecentListEnabled = false,
        };
        AddChild(dialog);
        return dialog;
    }

    private static VBoxContainer Stack(int separation)
    {
        var stack = new VBoxContainer();
        stack.AddThemeConstantOverride("separation", separation);
        return stack;
    }

    private static VBoxContainer Card(VBoxContainer parent, string title)
    {
        var panel = new PanelContainer();
        panel.AddThemeStyleboxOverride("panel", Box(new Color("121d2b"), new Color("27384a"), 20));
        parent.AddChild(panel);
        var content = Stack(12);
        panel.AddChild(content);
        content.AddChild(MakeLabel(title, 19));
        return content;
    }

    private static Label MakeLabel(string text, int size, Color? color = null)
    {
        var label = new Label { Text = text, AutowrapMode = TextServer.AutowrapMode.WordSmart };
        label.AddThemeFontSizeOverride("font_size", size);
        label.AddThemeColorOverride("font_color", color ?? Ink);
        return label;
    }

    private static LineEdit PathField(VBoxContainer parent, string caption, string placeholder)
    {
        parent.AddChild(MakeLabel(caption, 12, Muted));
        var field = new LineEdit
        {
            Editable = false, PlaceholderText = placeholder,
            CustomMinimumSize = new Vector2(0, 32), SizeFlagsHorizontal = SizeFlags.ExpandFill,
        };
        field.AddThemeFontSizeOverride("font_size", 13);
        parent.AddChild(field);
        return field;
    }

    private static Button MakeButton(string text, Action action, string tooltip)
    {
        var button = new Button { Text = text, TooltipText = tooltip, CustomMinimumSize = new Vector2(0, 40) };
        button.Pressed += action;
        return button;
    }

    private static Theme CreateTheme()
    {
        var theme = new Theme { DefaultFontSize = 16 };
        theme.SetColor("font_color", "Label", Ink);
        foreach (string type in new[] { "Button", "OptionButton", "LineEdit" })
        {
            theme.SetColor("font_color", type, Ink);
            theme.SetColor("font_readonly_color", type, Muted);
            theme.SetStylebox("normal", type, Box(new Color("1c2d40"), new Color("39516a")));
            theme.SetStylebox("read_only", type, Box(new Color("0c1520"), new Color("253447")));
            theme.SetStylebox("hover", type, Box(new Color("294158"), new Color("6ba69e")));
            theme.SetStylebox("pressed", type, Box(new Color("142435"), Accent));
            theme.SetStylebox("disabled", type, Box(new Color("182333"), new Color("29384a")));
            var focus = Box(Colors.Transparent, Accent);
            focus.BorderWidthLeft = focus.BorderWidthRight = focus.BorderWidthTop = focus.BorderWidthBottom = 2;
            theme.SetStylebox("focus", type, focus);
        }
        return theme;
    }

    private static StyleBoxFlat Box(Color background, Color border, int padding = 12) => new()
    {
        BgColor = background, BorderColor = border,
        BorderWidthLeft = 1, BorderWidthRight = 1, BorderWidthTop = 1, BorderWidthBottom = 1,
        CornerRadiusTopLeft = 8, CornerRadiusTopRight = 8, CornerRadiusBottomLeft = 8, CornerRadiusBottomRight = 8,
        ContentMarginLeft = padding, ContentMarginRight = padding,
        ContentMarginTop = padding / 2f, ContentMarginBottom = padding / 2f,
    };
}
