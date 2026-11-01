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
        Text = "This lists object script assignments in the current world, not references inside scripts. Another world may supply a missing name; this does not prove the mission will work.",
        AutowrapMode = TextServer.AutowrapMode.WordSmart
    };
    private readonly ItemList scripts = new() { CustomMinimumSize = new Vector2(0, 120) };
    private readonly ItemList uses = new() { CustomMinimumSize = new Vector2(0, 120) };
    private readonly ItemList missing = new() { CustomMinimumSize = new Vector2(0, 80) };
    private readonly ScrollContainer scroll = new()
    {
        SizeFlagsHorizontal = SizeFlags.ExpandFill,
        SizeFlagsVertical = SizeFlags.ExpandFill,
        HorizontalScrollMode = ScrollContainer.ScrollMode.Disabled,
        FollowFocus = true
    };
    private MissionReferenceIndex? snapshot;
    private int selectedScript = -1;

    public MissionReferencePanel()
    {
        AddChild(scroll);
        var content = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill };
        scroll.AddChild(content);
        content.AddChild(new Label { Text = "Mission scripts" });
        content.AddChild(overview);
        content.AddChild(scripts);
        content.AddChild(new Label { Text = "Objects using the selected script" });
        content.AddChild(details);
        content.AddChild(uses);
        content.AddChild(new Label { Text = "Script assignments not found in this world" });
        content.AddChild(missing);
        content.AddChild(disclaimer);
        scripts.ItemSelected += OnScriptSelected;
        uses.ItemSelected += OnUseSelected;
        missing.ItemSelected += OnMissingSelected;
        SetSnapshot(null);
    }

    /// <summary>The snapshot and zero-based script index that were selected.</summary>
    public event Action<MissionReferenceIndex, int>? ScriptSelected;
    /// <summary>The snapshot, script index and index into that script's object uses.</summary>
    public event Action<MissionReferenceIndex, int, int>? UseSelected;
    /// <summary>The snapshot and index into its assignments missing from this world.</summary>
    public event Action<MissionReferenceIndex, int>? MissingSelected;

    public MissionReferenceIndex? Snapshot => snapshot;
    public int? SelectedScriptIndex => selectedScript < 0 ? null : selectedScript;
    internal ItemList ScriptItems => scripts;
    internal ItemList UseItems => uses;
    internal ItemList MissingItems => missing;
    internal ScrollContainer ContentScroll => scroll;
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
        uses.Clear();
        missing.Clear();
        if (value == null)
        {
            overview.Text = "No mission is open.";
            details.Text = "Select a script to see which objects use it.";
            return;
        }
        string scriptCount = value.Scripts.Count == 1 ? "1 script" : $"{value.Scripts.Count} scripts";
        string missingCount = value.Unresolved.Count == 1 ? "1 object assignment" : $"{value.Unresolved.Count} object assignments";
        overview.Text = $"{scriptCount}; {missingCount} not found in this world.";
        details.Text = "Select a script to see which objects use it.";
        for (int i = 0; i < value.Scripts.Count; i++)
            scripts.AddItem($"{i + 1}. {Caption(value.Scripts[i].Name)}");
        foreach (var assignment in value.Unresolved)
            missing.AddItem($"Object row {assignment.Row}: {Caption(assignment.Role)} - {Caption(assignment.Name)}");
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
        uses.Clear();
        var script = current.Scripts[index];
        foreach (var use in script.Uses)
            uses.AddItem($"Object row {use.Row}: {Caption(use.Role)}");
        details.Text = script.Uses.Count switch
        {
            0 => "No object in this world uses this script.",
            1 => "1 object assignment uses this script.",
            _ => $"{script.Uses.Count} object assignments use this script."
        };
        ScriptSelected?.Invoke(current, index);
        return true;
    }

    /// <summary>Select an object use of the selected script.</summary>
    public bool TrySelectUse(int index)
    {
        var current = snapshot;
        int scriptIndex = selectedScript;
        if (current == null || scriptIndex < 0 || scriptIndex >= current.Scripts.Count
            || index < 0 || index >= current.Scripts[scriptIndex].Uses.Count) return false;
        uses.Select(index);
        UseSelected?.Invoke(current, scriptIndex, index);
        return true;
    }

    /// <summary>Select an assignment not found among scripts in this world.</summary>
    public bool TrySelectMissing(int index)
    {
        var current = snapshot;
        if (current == null || index < 0 || index >= current.Unresolved.Count) return false;
        missing.Select(index);
        MissingSelected?.Invoke(current, index);
        return true;
    }

    private void OnScriptSelected(long index)
    {
        if (index >= 0 && index <= int.MaxValue) TrySelectScript((int)index);
    }

    private void OnUseSelected(long index)
    {
        if (index >= 0 && index <= int.MaxValue) TrySelectUse((int)index);
    }

    private void OnMissingSelected(long index)
    {
        if (index >= 0 && index <= int.MaxValue) TrySelectMissing((int)index);
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
