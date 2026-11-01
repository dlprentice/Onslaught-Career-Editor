using System;
using System.Text;
using Godot;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// Shows a mission reference snapshot without editing it. Consumers must discard
/// selections when the snapshot changes and compare event snapshots before use.
/// </summary>
public sealed partial class MissionReferencePanel : VBoxContainer
{
    private readonly Label overview = new() { AutowrapMode = TextServer.AutowrapMode.WordSmart };
    private readonly Label details = new() { AutowrapMode = TextServer.AutowrapMode.WordSmart };
    private readonly Label disclaimer = new()
    {
        Text = "Only recognised references are listed. Resolution does not prove the mission will work.",
        AutowrapMode = TextServer.AutowrapMode.WordSmart
    };
    private readonly ItemList scripts = new() { CustomMinimumSize = new Vector2(0, 120) };
    private readonly ItemList references = new() { CustomMinimumSize = new Vector2(0, 120) };
    private MissionReferenceIndex? snapshot;
    private int selectedScript = -1;

    public MissionReferencePanel()
    {
        AddChild(new Label { Text = "Mission scripts" });
        AddChild(overview);
        AddChild(scripts);
        AddChild(new Label { Text = "References in the selected script" });
        AddChild(details);
        AddChild(references);
        AddChild(disclaimer);
        scripts.ItemSelected += OnScriptSelected;
        references.ItemSelected += OnReferenceSelected;
        SetSnapshot(null);
    }

    /// <summary>The snapshot and zero-based script index that were selected.</summary>
    public event Action<MissionReferenceIndex, int>? ScriptSelected;
    /// <summary>The snapshot, script index and reference index that were selected.</summary>
    public event Action<MissionReferenceIndex, int, int>? ReferenceSelected;

    public MissionReferenceIndex? Snapshot => snapshot;
    public int? SelectedScriptIndex => selectedScript < 0 ? null : selectedScript;
    internal ItemList ScriptItems => scripts;
    internal ItemList ReferenceItems => references;
    internal string OverviewText => overview.Text;
    internal string DetailText => details.Text;
    internal bool ExplanationsWrap => overview.AutowrapMode == TextServer.AutowrapMode.WordSmart
        && details.AutowrapMode == TextServer.AutowrapMode.WordSmart
        && disclaimer.AutowrapMode == TextServer.AutowrapMode.WordSmart;

    /// <summary>Discard old selection when the editor model changes or closes.</summary>
    public void SetSnapshot(MissionReferenceIndex? value)
    {
        snapshot = value;
        selectedScript = -1;
        scripts.Clear();
        references.Clear();
        if (value == null)
        {
            overview.Text = "No mission is open.";
            details.Text = "Select a script to inspect its references.";
            return;
        }
        overview.Text = $"{value.Scripts.Count} scripts; {value.Unresolved.Count} reference occurrences not resolved.";
        details.Text = "Select a script to inspect its references.";
        for (int i = 0; i < value.Scripts.Count; i++)
            scripts.AddItem($"{i + 1}. {Caption(value.Scripts[i].Name)}");
    }

    /// <summary>Clear stale selections when a snapshot cannot be produced.</summary>
    public void SetUnavailable()
    {
        SetSnapshot(null);
        overview.Text = "Mission references are unavailable for this level.";
    }

    /// <summary>Select a script by its snapshot-local index; invalid indices leave the selection unchanged.</summary>
    public bool TrySelectScript(int index)
    {
        var current = snapshot;
        if (current == null || index < 0 || index >= current.Scripts.Count) return false;
        scripts.Select(index);
        selectedScript = index;
        references.Clear();
        var script = current.Scripts[index];
        foreach (var reference in script.References)
        {
            string state = reference.Resolved ? "Resolved" : "Not resolved";
            references.AddItem($"{state}: {Caption(reference.Role)} - {Caption(reference.Name)}");
        }
        details.Text = script.References.Count == 0
            ? "No references were identified in this script."
            : $"{script.References.Count} identified reference occurrences.";
        ScriptSelected?.Invoke(current, index);
        return true;
    }

    /// <summary>Select an identified reference in the selected script.</summary>
    public bool TrySelectReference(int index)
    {
        var current = snapshot;
        int scriptIndex = selectedScript;
        if (current == null || scriptIndex < 0 || scriptIndex >= current.Scripts.Count
            || index < 0 || index >= current.Scripts[scriptIndex].References.Count) return false;
        references.Select(index);
        ReferenceSelected?.Invoke(current, scriptIndex, index);
        return true;
    }

    private void OnScriptSelected(long index)
    {
        if (index >= 0 && index <= int.MaxValue) TrySelectScript((int)index);
    }

    private void OnReferenceSelected(long index)
    {
        if (index >= 0 && index <= int.MaxValue) TrySelectReference((int)index);
    }

    private static string Caption(string? text)
    {
        if (string.IsNullOrEmpty(text)) return "(unnamed)";
        const int limit = 96;
        var result = new StringBuilder();
        int count = 0;
        bool truncated = false;
        foreach (var rune in text.EnumerateRunes())
        {
            if (count == limit) { truncated = true; break; }
            result.Append(Rune.IsControl(rune) ? " " : rune.ToString());
            count++;
        }
        string cleaned = result.ToString().Trim();
        if (cleaned.Length == 0) return "(unnamed)";
        return truncated ? cleaned + "..." : cleaned;
    }
}
