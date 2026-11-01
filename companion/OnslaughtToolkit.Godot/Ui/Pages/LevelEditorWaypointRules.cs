// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

internal sealed partial class LevelEditorPage
{
    private VBoxContainer? _waypointRulePanel;
    private Label? _waypointRuleSummary;
    private Tree? _waypointRuleList;
    private EditSession? _waypointRuleSession;
    private string? _waypointRuleText;
    private ScriptEntry? _waypointRuleScript;
    internal Button CheckWaypointRules { get; private set; } = null!;
    internal WaypointRuleReport? WaypointRules { get; private set; }
    internal string WaypointRulesText => _waypointRuleSummary?.Text ?? "";

    private void BuildWaypointRuleControls(VBoxContainer parent)
    {
        CheckWaypointRules = _scriptEditActions.Add(Build.Button("Check waypoint rules", tooltip: "Read-only check of direct literal targets in this source against selected world data. Dynamic expressions, includes/macros and runtime behavior are not checked."));
        CheckWaypointRules.Pressed += () => RunWaypointRuleCheck();
        _waypointRulePanel = parent.Add(Build.Column(6));
        _waypointRulePanel.Visible = false;
        _waypointRuleSummary = _waypointRulePanel.Add(Build.Text("", "Muted"));
        _waypointRuleList = _waypointRulePanel.Add(Build.Table("Line", "Waypoint rule"));
        _waypointRuleList.Name = "WaypointRuleFindings";
        _waypointRuleList.CustomMinimumSize = new Vector2(0, 130);
        _waypointRuleList.SetColumnExpand(0, false);
        _waypointRuleList.SetColumnCustomMinimumWidth(0, 44);
        _waypointRuleList.SetColumnExpand(1, true);
        _waypointRuleList.ItemSelected += () =>
        {
            TreeItem? item = _waypointRuleList.GetSelected();
            if (item is not null) GoToWaypointRule(item.GetMetadata(0).AsInt32());
        };
    }

    private void SyncWaypointRuleControls()
    {
        if (CheckWaypointRules is null) return;
        CheckWaypointRules.Disabled = _services.Game.Busy || _model?.Session is null || _scripts.CurrentSource?.Source is null;
    }

    private void ClearWaypointRules()
    {
        WaypointRules = null; _waypointRuleSession = null; _waypointRuleText = null; _waypointRuleScript = null;
        if (_waypointRuleSummary is not null) _waypointRuleSummary.Text = "";
        _waypointRuleList?.Clear();
        if (_waypointRulePanel is not null) _waypointRulePanel.Visible = false;
    }

    internal WaypointRuleReport? RunWaypointRuleCheck()
    {
        SyncWaypointRuleControls();
        if (CheckWaypointRules.Disabled || _model is null) return null;
        ClearWaypointRules();
        string source = _scripts.SourceText;
        WaypointRuleReport report = _model.CheckWaypointRules(source);
        WaypointRules = report;
        _waypointRuleSession = _model.Session; _waypointRuleScript = _scripts.Current; _waypointRuleText = source;
        _waypointRuleSummary!.Text = !report.Available ? "Waypoint check unavailable. " + WaypointRuleReport.Scope
            : $"{report.Calls} waypoint calls in source. Found literal targets: {report.Resolved}; missing or empty: {report.Unresolved}; dynamic/indirect unchecked: {report.Unchecked}." +
              (report.UnshownCalls > 0 ? $" {report.UnshownCalls} additional calls are not shown or checked." : "") +
              (report.SkippedDirectives > 0 ? $" {report.SkippedDirectives} include/define directives were skipped." : "") + "\n" + WaypointRuleReport.Scope;
        _waypointRuleSummary.ThemeTypeVariation = !report.Available || report.Unresolved > 0 || report.Unchecked > 0 || report.UnshownCalls > 0 || report.SkippedDirectives > 0 ? "Warn" : "Muted";
        _waypointRuleList!.Clear();
        TreeItem root = _waypointRuleList.CreateItem();
        for (int index = 0; index < report.Findings.Count; index++)
        {
            WaypointRuleFinding finding = report.Findings[index];
            string status = finding.Kind switch { WaypointRuleKind.Resolved => "found", WaypointRuleKind.MissingPath => "missing", WaypointRuleKind.EmptyPath => "empty", WaypointRuleKind.UncheckedExpression => "unchecked", _ => "unavailable" };
            string target = finding.Target is { } text ? PathText.Elide(text, 48) : finding.Function.Length > 0 ? "expression" : "source/data";
            TreeItem row = Build.TableRow(_waypointRuleList, root, (finding.Line + 1).ToString(System.Globalization.CultureInfo.InvariantCulture), target + " · " + status);
            row.SetMetadata(0, index);
            row.SetTooltipText(1, finding.Function + (finding.Target is { } name ? " · " + name : "") + "\n" + finding.Message);
        }
        _waypointRuleList.Visible = report.Findings.Count > 0;
        _waypointRulePanel!.Visible = true;
        BringIntoView(_waypointRulePanel);
        return report;
    }

    internal bool GoToWaypointRule(int index)
    {
        if (WaypointRules is not { } report || index < 0 || index >= report.Findings.Count || !ReferenceEquals(_waypointRuleSession, _model?.Session) ||
            !ReferenceEquals(_waypointRuleScript, _scripts.Current) || _waypointRuleText != _scripts.SourceText || _services.Game.Busy)
        { ClearWaypointRules(); return false; }
        _scripts.GoToLine(report.Findings[index].Line);
        return true;
    }
}
