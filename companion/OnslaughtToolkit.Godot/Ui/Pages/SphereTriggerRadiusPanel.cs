// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// An inspector for one existing spherical trigger. A typed draft belongs to the exact selected record and
/// captured radius; refreshing the same selection never silently rebases it over another radius edit.
/// </summary>
internal sealed partial class SphereTriggerRadiusPanel : VBoxContainer
{
    private sealed record Target(LevelEditorModel Model, EditSession Session, WorldBody Body, int Row,
        PlacedObject Record, ObjectInit Init, SphereTriggerInit Trigger, int ObjectId, float Radius);

    private LevelEditorModel? _model;
    private int? _selectedRow;
    private Target? _target;
    private LevelEditorModel? _listenedModel;
    private EditSession? _listenedSession;
    private string _shownText = "";
    private bool _settingText;
    private bool _reportedDraft;

    internal LineEdit RadiusInput { get; }
    internal Button Apply { get; }
    internal Button UseStoredRadius { get; }
    internal Label Note { get; }

    /// <summary>Unapplied text must be considered before the page discards this selection or session.</summary>
    internal bool HasDraft => _target is not null && RadiusInput.Text != _shownText;
    /// <summary>Every user text edit, including dirty-to-dirty edits, and programmatic draft-state transitions.</summary>
    internal event Action? DraftChanged;
    internal event Action<MoveOutcome>? ResizeResult;

    internal SphereTriggerRadiusPanel()
    {
        AddThemeConstantOverride("separation", 8);
        this.Add(Build.Heading("Trigger radius"));
        this.Add(Build.Text("The distance from this trigger's centre at which its existing rules can apply. Changing the radius does not add or change those rules.", "Muted"));
        HBoxContainer field = this.Add(Build.Row(8));
        field.Add(Build.Text("Radius", wrap: false));
        RadiusInput = field.Add(new LineEdit
        {
            PlaceholderText = "Enter a number at least zero",
            MaxLength = CoordinateInput.MaxLength,
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
            TooltipText = "A finite radius at least zero, in the world's existing units.",
        });
        RadiusInput.TextChanged += DraftEdited;
        RadiusInput.TextSubmitted += _ => ApplyRadius();
        HBoxContainer buttons = this.Add(Build.Row(8));
        Apply = buttons.Add(Build.Button("Apply radius"));
        UseStoredRadius = buttons.Add(Build.Button("Use stored radius"));
        Apply.Pressed += ApplyRadius;
        UseStoredRadius.Pressed += Reload;
        Note = this.Add(Build.Text("", "Muted"));
        Refresh();
    }

    /// <summary>
    /// Repeated binding to the same session and record preserves unapplied text and its expected radius.
    /// A genuinely different selection or session starts from that target's stored radius.
    /// </summary>
    internal void Bind(LevelEditorModel? model, int? selectedRow)
    {
        _model = model;
        _selectedRow = selectedRow;
        Refresh();
    }

    internal void Clear() => Bind(null, null);

    public override void _EnterTree() => Refresh();
    public override void _ExitTree() => StopListening();

    /// <summary>Refreshes stored values after undo or redo, preserving an unapplied draft on the same target.</summary>
    internal void Refresh()
    {
        Listen();
        Target? current = ReadTarget();
        bool same = SameTarget(_target, current);
        if (same && HasDraft)
        {
            if (!ResizeSphereTrigger.SameBits(_target!.Radius, current!.Radius))
                Note.Text = "The stored radius changed. Use stored radius before applying your draft.";
        }
        else if (!same || _target is null || !ResizeSphereTrigger.SameBits(_target.Radius, current!.Radius))
            Show(current);
        Visible = current is not null;
        Apply.Disabled = current is null;
        UseStoredRadius.Disabled = current is null;
        ReportDraft();
    }

    private void Listen()
    {
        if (!IsInsideTree()) return;
        if (!ReferenceEquals(_listenedModel, _model))
        {
            if (_listenedModel is not null) _listenedModel.Changed -= Refresh;
            _listenedModel = _model;
            if (_listenedModel is not null) _listenedModel.Changed += Refresh;
        }
        EditSession? session = _model?.Session;
        if (!ReferenceEquals(_listenedSession, session))
        {
            if (_listenedSession is not null) _listenedSession.Changed -= Refresh;
            _listenedSession = session;
            if (_listenedSession is not null) _listenedSession.Changed += Refresh;
        }
    }

    private void StopListening()
    {
        if (_listenedModel is not null) _listenedModel.Changed -= Refresh;
        if (_listenedSession is not null) _listenedSession.Changed -= Refresh;
        _listenedModel = null;
        _listenedSession = null;
    }

    private Target? ReadTarget()
    {
        if (_model?.Session is not { } session || _selectedRow is not int row || row < 0 || row >= session.Body.Things.Count)
            return null;
        PlacedObject thing = session.Body.Things[row];
        if (!ResizeSphereTrigger.IsSphereTrigger(thing)) return null;
        return new Target(_model, session, session.Body, row, thing, thing.Init, thing.Init.SphereTrigger!,
            thing.ObjectId, thing.Init.SphereTrigger!.Radius);
    }

    private static bool SameTarget(Target? shown, Target? current) => shown is not null && current is not null &&
        ReferenceEquals(shown.Model, current.Model) && ReferenceEquals(shown.Session, current.Session) &&
        ReferenceEquals(shown.Body, current.Body) && shown.Row == current.Row && ReferenceEquals(shown.Record, current.Record) &&
        ReferenceEquals(shown.Init, current.Init) && ReferenceEquals(shown.Trigger, current.Trigger) && shown.ObjectId == current.ObjectId;

    private void Show(Target? target)
    {
        _target = target;
        _shownText = target is null ? "" : CoordinateInput.Format(target.Radius);
        _settingText = true;
        try { RadiusInput.Text = _shownText; }
        finally { _settingText = false; }
        Note.Text = target is not null && !ResizeSphereTrigger.IsRequestedRadius(target.Radius)
            ? "This stored radius is outside the editable range. It stays unchanged unless you apply a finite number at least zero."
            : "";
        ReportDraft();
    }

    private void ReportDraft(bool textChanged = false)
    {
        bool draft = HasDraft;
        if (draft == _reportedDraft && !textChanged) return;
        _reportedDraft = draft;
        DraftChanged?.Invoke();
    }

    private void DraftEdited(string text)
    {
        if (_settingText) return;
        Note.Text = "";
        ReportDraft(textChanged: true);
    }

    private void Reload()
    {
        Show(ReadTarget());
        Refresh();
    }

    private void Result(MoveResult result, string message)
    {
        Note.Text = message;
        ResizeResult?.Invoke(new MoveOutcome(result, message));
    }

    private void ApplyRadius()
    {
        Target? current = ReadTarget();
        if (!SameTarget(_target, current))
        {
            Refresh();
            Result(MoveResult.Refused, "The selected trigger changed. Check the selection before applying a radius.");
            return;
        }
        if (!ResizeSphereTrigger.SameBits(_target!.Radius, current!.Radius))
        {
            Result(MoveResult.Refused, "The stored radius changed. Use stored radius before applying your draft.");
            return;
        }
        CoordinateParse parsed = CoordinateInput.Parse(RadiusInput.Text);
        if (!parsed.Ok)
        {
            Result(MoveResult.Refused, "Radius: " + parsed.Problem);
            return;
        }
        if (!ResizeSphereTrigger.IsRequestedRadius(parsed.Value))
        {
            Result(MoveResult.Refused, "The radius must be a finite number at least zero.");
            return;
        }
        bool changed = current.Session.ResizeTrigger(current.Row, parsed.Value);
        Show(ReadTarget());
        Refresh();
        Result(changed ? MoveResult.Moved : MoveResult.Unchanged,
            changed ? $"Radius set to {CoordinateInput.Format(parsed.Value)}." + (parsed.Rounded ? " Rounded to the stored precision." : "")
                : "This trigger already has that radius.");
    }
}
