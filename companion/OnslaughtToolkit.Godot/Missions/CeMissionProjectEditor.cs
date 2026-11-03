// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>Undoable authored-document changes. Revisions bind delayed edits and 3D selections to the document they captured.</summary>
public sealed class CeMissionProjectEditor
{
    public const int HistoryLimit = 64;
    private readonly List<CeMissionProject> _undo = [], _redo = [];
    private CeMissionProject _saved;
    public CeMissionProject Current { get; private set; }
    public long Revision { get; private set; }
    public bool CanUndo => _undo.Count > 0;
    public bool CanRedo => _redo.Count > 0;
    public bool HasUnsavedChanges => !ReferenceEquals(Current, _saved);
    public event Action? Changed;

    public CeMissionProjectEditor(CeMissionProject project) => Current = _saved = project ?? throw new ArgumentNullException(nameof(project));

    public bool TryAddPlacement(CeMissionPlacement placement, long revision, out string message) => Apply(revision,
        project => project.WithPlacements(project.Placements.Append(placement)), out message);

    public bool TryAddScript(CeMissionSource source, long revision, out string message) => Apply(revision,
        project => project.WithScripts(project.Scripts.Append(source)), out message);

    public bool TryMovePlacement(string id, Vector3 position, long revision, out string message) => Apply(revision, project =>
    {
        CeMissionPlacement selected = project.Placement(id);
        if (SamePosition(selected.Position, position)) return project;
        return project.WithPlacements(project.Placements.Select(item => item.Id == id ? item with { Position = position } : item));
    }, out message);

    public bool TryBindScript(string placementId, string? scriptId, long revision, out string message) => Apply(revision, project =>
    {
        CeMissionPlacement selected = project.Placement(placementId);
        return selected.ScriptId == scriptId ? project : project.WithPlacements(project.Placements.Select(item =>
            item.Id == placementId ? item with { ScriptId = scriptId } : item));
    }, out message);

    public bool TrySetSource(string scriptId, string text, long revision, out string message) => Apply(revision, project =>
    {
        CeMissionSource selected = project.Script(scriptId);
        return selected.Text == text ? project : project.WithScripts(project.Scripts.Select(item => item.Id == scriptId ? item with { Text = text } : item));
    }, out message);

    public bool TrySetEntry(string? scriptId, long revision, out string message) => Apply(revision,
        project => project.EntryScriptId == scriptId ? project : project.WithEntry(scriptId), out message);

    public bool TrySetMapLink(CeMissionMapLink? map, long revision, out string message) => Apply(revision,
        project => ReferenceEquals(project.Map, map) ? project : project.WithMap(map), out message);

    /// <summary>Keep all pending inspector/source fields as one change, or keep none when a field is invalid.</summary>
    public bool TryApplyDrafts(string? name, IReadOnlyDictionary<string, Vector3> positions,
        IReadOnlyDictionary<string, string> sources, long revision, out string message) => Apply(revision, project =>
    {
        ArgumentNullException.ThrowIfNull(positions);
        ArgumentNullException.ThrowIfNull(sources);
        bool changed = name is not null && name != project.Name;
        foreach ((string id, Vector3 position) in positions)
            changed |= !SamePosition(project.Placement(id).Position, position);
        foreach ((string id, string text) in sources)
            changed |= project.Script(id).Text != text;
        if (!changed) return project;
        return new CeMissionProject(project.Id, name ?? project.Name,
            project.Placements.Select(item => positions.TryGetValue(item.Id, out Vector3 position) ? item with { Position = position } : item),
            project.Scripts.Select(item => sources.TryGetValue(item.Id, out string? text) ? item with { Text = text } : item), project.EntryScriptId, project.Map);
    }, out message);

    public bool Undo()
    {
        if (!CanUndo) return false;
        _redo.Add(Current);
        Current = _undo[^1];
        _undo.RemoveAt(_undo.Count - 1);
        Announce();
        return true;
    }

    public bool Redo()
    {
        if (!CanRedo) return false;
        _undo.Add(Current);
        Current = _redo[^1];
        _redo.RemoveAt(_redo.Count - 1);
        Announce();
        return true;
    }

    /// <summary>Open/replace is atomic at the document boundary and starts a new history.</summary>
    public void Open(CeMissionProject project)
    {
        ArgumentNullException.ThrowIfNull(project);
        Current = _saved = project;
        _undo.Clear();
        _redo.Clear();
        Announce();
    }

    public bool MarkSaved(long revision)
    {
        if (revision != Revision) return false;
        _saved = Current;
        Changed?.Invoke();
        return true;
    }

    public CeMissionProjectMarkers CaptureMarkers() => new(this);

    private bool Apply(long revision, Func<CeMissionProject, CeMissionProject> change, out string message)
    {
        if (revision != Revision)
        {
            message = "The project changed before this edit was applied. Select it again.";
            return false;
        }
        try
        {
            CeMissionProject next = change(Current);
            if (ReferenceEquals(next, Current)) { message = "Nothing changed."; return true; }
            _undo.Add(Current);
            if (_undo.Count > HistoryLimit) _undo.RemoveAt(0);
            _redo.Clear();
            Current = next;
            Announce();
            message = "Project updated. Undo can take this change back.";
            return true;
        }
        catch (ArgumentException error)
        {
            message = error.Message;
            return false;
        }
    }

    private void Announce() { Revision++; Changed?.Invoke(); }

    private static bool SamePosition(Vector3 left, Vector3 right) =>
        BitConverter.SingleToUInt32Bits(left.X) == BitConverter.SingleToUInt32Bits(right.X) &&
        BitConverter.SingleToUInt32Bits(left.Y) == BitConverter.SingleToUInt32Bits(right.Y) &&
        BitConverter.SingleToUInt32Bits(left.Z) == BitConverter.SingleToUInt32Bits(right.Z);
}

/// <summary>A 3D picking bridge with stable authored IDs. Every document change, including Undo, invalidates its hits.</summary>
public sealed class CeMissionProjectMarkers
{
    private readonly CeMissionProjectEditor _owner;
    private readonly CeMissionProject _document;
    private readonly long _revision;
    private readonly MissionMarkerSnapshot3D _markers;

    internal CeMissionProjectMarkers(CeMissionProjectEditor editor)
    {
        _owner = editor;
        _document = editor.Current;
        _revision = editor.Revision;
        _markers = MissionMarkerSnapshot3D.Capture(_document.Placements.Select((placement, index) =>
            new MissionMarkerSnapshot3D.Marker(index, placement.Position)).ToArray(), CeMissionProject.MaxPlacements);
    }

    public bool TryPick(Vector3 origin, Vector3 direction, float radius, float distance, out MissionMarkerSnapshot3D.Hit hit) =>
        _markers.TryPick(origin, direction, radius, distance, out hit);

    public bool TryResolve(CeMissionProjectEditor editor, MissionMarkerSnapshot3D.Hit hit, out CeMissionPlacement? placement)
    {
        placement = null;
        if (!ReferenceEquals(editor, _owner) || editor.Revision != _revision || !ReferenceEquals(editor.Current, _document) ||
            !_markers.TryResolve(hit, out MissionMarkerSnapshot3D.Marker marker)) return false;
        placement = _document.Placements[marker.Index];
        return true;
    }
}
