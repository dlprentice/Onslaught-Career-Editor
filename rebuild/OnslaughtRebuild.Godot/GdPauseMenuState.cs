// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary host adapter while FirstFlightGame remains managed. The sole
/// production pause state and its behavior live in Client/pause_menu.gd.
/// </summary>
public sealed class GdPauseMenuState : IDisposable
{
    private GodotObject? _state;
    private bool _disposed;

    private GodotObject State
    {
        get
        {
            ObjectDisposedException.ThrowIf(_disposed, this);
            return _state ??= GD.Load<GDScript>("res://Client/pause_menu.gd").New().AsGodotObject();
        }
    }

    public bool IsOpen => State.Call("is_open").AsBool();
    public Level100PausePage Page => (Level100PausePage)State.Call("get_page").AsInt32();
    public int SelectedIndex => State.Call("get_selected_index").AsInt32();
    public int UnderlyingRootSelection => State.Call("get_underlying_root_selection").AsInt32();
    public IReadOnlyList<Level100PauseEntry> Entries => ReadEntries("get_entries");
    public IReadOnlyList<Level100PauseEntry> RootEntries => ReadEntries("get_root_entries");
    public Godot.Collections.Dictionary ViewSnapshot => State.Call("view_snapshot").AsGodotDictionary();

    public void Open() => State.Call("open");
    public void Reset() => State.Call("reset");
    public bool MoveSelection(int direction) => State.Call("move_selection", direction).AsBool();
    public bool Hover(int index) => State.Call("hover", index).AsBool();
    public Level100PauseAction ActivateSelected() => (Level100PauseAction)State.Call("activate_selected").AsInt32();
    public Level100PauseAction Cancel() => (Level100PauseAction)State.Call("cancel").AsInt32();

    private IReadOnlyList<Level100PauseEntry> ReadEntries(string method)
    {
        Godot.Collections.Array rows = State.Call(method).AsGodotArray();
        var entries = new Level100PauseEntry[rows.Count];
        for (int index = 0; index < rows.Count; index++)
        {
            Godot.Collections.Dictionary row = rows[index].AsGodotDictionary();
            entries[index] = new((Level100PauseEntryId)row["id"].AsInt32(),
                row["label"].AsString(), row["enabled"].AsBool());
        }
        return entries;
    }

    public void Dispose()
    {
        if (_disposed) return;
        _state?.Dispose();
        _state = null;
        _disposed = true;
    }
}
