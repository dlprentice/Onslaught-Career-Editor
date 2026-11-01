// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>An exact checkpoint of one panel's draft ownership, including edits between two dirty states.</summary>
internal readonly record struct EditorScriptDraftStamp(ScriptsPanel Owner, long Revision);

/// <summary>A copied, validated script import, tied to the draft checkpoint the player confirmed.</summary>
internal sealed class PreparedScriptProject(ScriptsPanel owner, EditorScriptDraftStamp expected,
    IReadOnlyList<ScriptEntry> entries, IReadOnlyList<EditorProjectScript> scripts, string contentHash, string entriesHash)
{
    internal ScriptsPanel Owner { get; } = owner;
    internal EditorScriptDraftStamp Expected { get; } = expected;
    internal IReadOnlyList<ScriptEntry> Entries { get; } = entries;
    internal IReadOnlyList<EditorProjectScript> Scripts { get; } = scripts;
    internal string ContentHash { get; } = contentHash;
    internal string EntriesHash { get; } = entriesHash;
}

/// <summary>
/// The compiled scripts of the open level beside their opened or project-preserved source text. Typed drafts stay owned by the panel
/// until a confirmed discard or level change. The game runs the compiled record; source text alone does not establish what is in use.
/// </summary>
internal sealed partial class ScriptsPanel : VBoxContainer
{
    private static readonly string[] Keywords = ["vars", "end_vars", "attributes", "end_attributes", "if", "else", "while", "for", "switch", "case", "do_once", "event",
        "init", "arrived", "timer", "died", "hit", "started_dying", "ready", "shutdown"];

    private static readonly string[] Types = ["int", "float", "bool", "string", "thing", "position", "TRUE", "FALSE"];

    private readonly Tree _list;
    private readonly CodeEdit _source;
    private readonly Label _info, _empty;
    private IReadOnlyList<ScriptEntry> _entries = [];
    private string? _root;
    private string _filter = "";
    private ScriptEntry? _current;
    private ScriptSourceResult? _currentSource;
    private SourceToken? _token;
    private bool _wantEditing;
    private readonly Dictionary<string, string> _drafts = new(StringComparer.Ordinal);
    private readonly Dictionary<string, ScriptSourceResult> _sourceBaselines = new(StringComparer.Ordinal);
    private readonly HashSet<string> _projectSources = new(StringComparer.Ordinal);
    private long _draftRevision;
    private bool _settingSource;

    internal ScriptsPanel()
    {
        AddThemeConstantOverride("separation", 8);
        SizeFlagsHorizontal = SizeFlags.ExpandFill;
        SizeFlagsVertical = SizeFlags.ExpandFill;

        _empty = this.Add(Build.Text("", "Muted"));
        _list = this.Add(Build.Table("Script", "Runs on", "Handles"));
        _list.SizeFlagsStretchRatio = 1f;
        _list.CustomMinimumSize = new Vector2(280, 96);
        _list.SetColumnExpand(0, true);
        _list.SetColumnExpandRatio(0, 3);
        _list.SetColumnCustomMinimumWidth(0, 110);
        _list.SetColumnExpand(1, false);
        _list.SetColumnCustomMinimumWidth(1, 86);
        _list.SetColumnExpand(2, true);
        _list.SetColumnExpandRatio(2, 4);
        _list.SetColumnCustomMinimumWidth(2, 80);
        _list.ItemSelected += () => Choose(_list.GetSelected());

        _info = this.Add(Build.Text("", "Faint", wrap: false, clip: true));
        _info.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        _info.MouseFilter = MouseFilterEnum.Pass;  // so that the tooltip, which has the whole path, shows
        _source = this.Add(NewSourceView());
        _source.SizeFlagsStretchRatio = 2.2f;
        _source.CaretChanged += OnCaret;
        _source.TextChanged += OnText;  // the line count and what the text is (the file's, typed, in use) follow what is typed...
        _source.TextSet += OnText;  // ...and what is put in by code (the engine raises a different signal for that)
    }

    /// <summary>Raised when the selected script changes (null: none is selected). The source result is what was found for it.</summary>
    internal event Action<ScriptEntry?, ScriptSourceResult?>? Selected;

    /// <summary>Raised when the text on view changes, typed or put in by code: what depends on it (Put the shipped script back, the unsaved-work count) is refreshed by the page.</summary>
    internal event Action? TextEdited;

    /// <summary>Raised when the quoted text or word under the source's caret changes (null: the caret is on none).</summary>
    internal event Action<SourceToken?>? NameUnderCaret;

    /// <summary>The quoted text or word the caret is on in the source.</summary>
    internal SourceToken? Token => _token;

    /// <summary>
    /// Whether the source can be typed in: the Edit switch is on and the selected script is one of the level's own with a source baseline to start from. The
    /// text typed is kept for the script (a draft) while another is chosen, and is not what the game runs until it is compiled and used.
    /// </summary>
    internal bool Editing => _source.Editable;

    /// <summary>Says whether the open level now uses a replaced script of this name (set by the page, which has the session).</summary>
    internal Func<string, bool>? IsReplaced { get; set; }

    /// <summary>
    /// Says whether the open level's script of this name is exactly what this text made when it was compiled and used (set by the page, which has the session and
    /// what each text made): what "in use" means below. Undo and Redo move the level between scripts without touching the text, so this is asked, never remembered.
    /// </summary>
    internal Func<string, string, bool>? IsInUse { get; set; }

    /// <summary>Whether the player turned Edit source on: it stays on while scripts that cannot be edited are chosen, and applies again to the next one that can.</summary>
    internal bool WantsEditing => _wantEditing;

    /// <summary>Whether the selected script has an unambiguous name and an opened or project-preserved source baseline.</summary>
    internal bool CanEditCurrent => _current is { FromBaseWorld: false } current && _currentSource?.Source is not null &&
        _entries.Count(entry => !entry.FromBaseWorld && string.Equals(entry.Summary.Name, current.Summary.Name, StringComparison.OrdinalIgnoreCase)) == 1;

    /// <summary>The text in the source view (line ends are \n).</summary>
    internal string SourceText => _source.Text;

    /// <summary>
    /// The scripts, by name, that hold text that was typed and is neither the source file's nor in use (what the level uses for the script, compiled from exactly that
    /// text): what leaving the level (or closing the companion) would lose without the level being changed. The text on view counts. Text whose replacement was taken
    /// back with Undo counts again, because the level no longer uses it.
    /// </summary>
    internal IReadOnlyList<string> UnusedDraftNames
    {
        get
        {
            StoreDraft();
            return _drafts.Where(draft => !InUse(draft.Key, draft.Value)).Select(draft => draft.Key).OrderBy(name => name, StringComparer.Ordinal).ToList();
        }
    }

    /// <summary>How many scripts <see cref="UnusedDraftNames"/> lists.</summary>
    internal int UnusedDraftCount => UnusedDraftNames.Count;

    /// <summary>Whether text was typed for the script of this name that differs from its source file (the text on view counts): what Put the shipped script back can drop.</summary>
    internal bool HasDraft(string name)
    {
        StoreDraft();
        return _drafts.ContainsKey(name);
    }

    /// <summary>Records all current typed text before a save, open or discard is prepared.</summary>
    internal EditorScriptDraftStamp CaptureDraftState()
    {
        StoreDraft();
        return new EditorScriptDraftStamp(this, _draftRevision);
    }

    internal bool MatchesDraftState(EditorScriptDraftStamp expected) => CaptureDraftState() == expected;

    /// <summary>Copies available source baselines and every draft; a missing source cannot silently drop typed or used text.</summary>
    internal IReadOnlyList<EditorProjectScript> CaptureProjectScripts(EditSession session, Func<int, string?>? usedText = null)
    {
        StoreDraft();
        ScriptEntry[] own = OwnEntries(_entries);
        if (own.Length != session.Body.Scripts.Count || own.Where((entry, index) => entry.Summary.Name != session.Body.Scripts[index].Name).Any())
            throw new InvalidDataException("The source panel no longer belongs to the open world.");
        List<EditorProjectScript> scripts = [];
        for (int index = 0; index < own.Length; index++)
        {
            string name = own[index].Summary.Name;
            _drafts.TryGetValue(name, out string? draft);
            string? used = usedText?.Invoke(index);
            if (SourceFor(own[index]).Source is not { } source)
            {
                if (draft is not null || used is not null) throw new InvalidDataException("A script with typed or used text has no source baseline to save.");
                continue;
            }
            scripts.Add(new EditorProjectScript(index, name, EditorProject.TextHash(source.Text), source.Text, draft, used,
                used is null ? null : EditorProject.Hash(WorldBodyWriter.ScriptBytes(session.Body.Scripts[index]))));
        }
        if (_drafts.Keys.Any(name => !own.Any(entry => entry.Summary.Name == name)))
            throw new InvalidDataException("A typed script no longer belongs to the open world.");
        EditorProject.CheckScriptTexts(scripts);
        return Array.AsReadOnly(scripts.ToArray());
    }

    /// <summary>Validates imported text without replacing the current sources, selection or drafts.</summary>
    internal bool TryPrepareProjectScripts(IReadOnlyList<ScriptEntry> entries, IReadOnlyList<EditorProjectScript> scripts,
        out PreparedScriptProject? prepared, out string message)
    {
        prepared = null;
        try
        {
            ScriptEntry[] copiedEntries = entries.ToArray();
            EditorProjectScript[] copiedScripts = scripts.ToArray();
            CheckProjectEntries(copiedEntries, copiedScripts);
            prepared = new PreparedScriptProject(this, CaptureDraftState(), Array.AsReadOnly(copiedEntries), Array.AsReadOnly(copiedScripts),
                EditorProject.ScriptStateHash(copiedScripts), EntryHash(copiedEntries));
            message = "The project's script sources and drafts are ready to open.";
            return true;
        }
        catch (Exception error) when (error is InvalidDataException or ArgumentException or InvalidOperationException)
        {
            message = error is InvalidDataException ? error.Message : "The project's script sources could not be prepared safely.";
            return false;
        }
    }

    /// <summary>Checks the current draft checkpoint and both copied import identities immediately before a model swap.</summary>
    internal bool IsPreparedProjectCurrent(PreparedScriptProject prepared)
    {
        if (!ReferenceEquals(prepared.Owner, this) || !MatchesDraftState(prepared.Expected)) return false;
        try
        {
            CheckProjectEntries(prepared.Entries, prepared.Scripts);
            return EditorProject.ScriptStateHash(prepared.Scripts) == prepared.ContentHash && EntryHash(prepared.Entries) == prepared.EntriesHash;
        }
        catch (Exception error) when (error is InvalidDataException or ArgumentException or InvalidOperationException) { return false; }
    }

    /// <summary>The caller prechecks the model and suppresses its panel refresh while both prepared states are committed.</summary>
    internal bool CommitProjectScripts(PreparedScriptProject prepared)
    {
        if (!IsPreparedProjectCurrent(prepared)) return false;
        _entries = prepared.Entries;
        _current = null;
        _currentSource = null;
        _drafts.Clear();
        _sourceBaselines.Clear();
        _projectSources.Clear();
        ScriptEntry[] own = OwnEntries(_entries);
        foreach (EditorProjectScript script in prepared.Scripts)
        {
            ScriptEntry entry = own[script.Index];
            string path = Path.Combine(_root ?? ".", "data", "MissionScripts", $"level{entry.SourceLevel:D3}", script.Name + ".msl");
            int lines = script.SourceText.Count(c => c == '\n') + (script.SourceText.Length > 0 && script.SourceText[^1] != '\n' ? 1 : 0);
            _sourceBaselines.Add(script.Name, new ScriptSourceResult(new ScriptSource(path, script.SourceText, lines), null));
            _projectSources.Add(script.Name);
            if (script.DraftText is not null && script.DraftText != script.SourceText) _drafts.Add(script.Name, script.DraftText);
        }
        _draftRevision++;
        Fill(keep: null);
        TextEdited?.Invoke();
        return true;
    }

    private static ScriptEntry[] OwnEntries(IReadOnlyList<ScriptEntry> entries)
    {
        ScriptEntry[] own = [.. entries.Where(entry => !entry.FromBaseWorld)];
        if (own.Any(entry => !EditorProject.IsScriptName(entry.Summary.Name)) ||
            own.Select(entry => entry.Summary.Name).Distinct(StringComparer.OrdinalIgnoreCase).Count() != own.Length)
            throw new InvalidDataException("The open world has ambiguous script source names.");
        return own;
    }

    private static void CheckProjectEntries(IReadOnlyList<ScriptEntry> entries, IReadOnlyList<EditorProjectScript> scripts)
    {
        EditorProject.CheckScriptTexts(scripts);
        ScriptEntry[] own = OwnEntries(entries);
        if (scripts.Any(script => script.Index >= own.Length || own[script.Index].Summary.Name != script.Name))
            throw new InvalidDataException("A project source does not belong to the selected script record.");
    }

    private static string EntryHash(IReadOnlyList<ScriptEntry> entries) => EditorProject.TextHash(System.Text.Json.JsonSerializer.Serialize(
        entries.Select(entry => new { entry.Summary.Name, entry.SourceLevel, entry.FromBaseWorld })));

    private bool InUse(string name, string text) => IsInUse?.Invoke(name, text) == true;

    internal Tree List => _list;
    internal CodeEdit Source => _source;
    internal string Info => _info.Text;
    internal Label InfoLabel => _info;
    internal string EmptyText => _empty.Visible ? _empty.Text : "";
    internal ScriptEntry? Current => _current;
    internal ScriptSourceResult? CurrentSource => _currentSource;
    internal bool CurrentSourceFromProject => _current is { FromBaseWorld: false } current && _projectSources.Contains(current.Summary.Name);

    /// <summary>How many scripts the list shows with the current search.</summary>
    internal int ShownCount => _list.GetRoot()?.GetChildCount() ?? 0;

    private static CodeEdit NewSourceView()
    {
        CodeHighlighter highlighter = new()
        {
            NumberColor = Palette.Warn, SymbolColor = Palette.Muted, FunctionColor = Palette.Data, MemberVariableColor = Palette.Text,
        };
        highlighter.AddColorRegion("//", "", Palette.Faint, lineOnly: true);
        highlighter.AddColorRegion("\"", "\"", Palette.Good);
        foreach (string word in Keywords) highlighter.AddKeywordColor(word, Palette.Accent);
        foreach (string word in Types) highlighter.AddKeywordColor(word, Palette.ViewedBlue);
        CodeEdit view = new()
        {
            Editable = false, GuttersDrawLineNumbers = true, WrapMode = TextEdit.LineWrappingMode.None, CaretBlink = false, ScrollSmooth = false,
            HighlightCurrentLine = false, MinimapDraw = false, SyntaxHighlighter = highlighter, SizeFlagsVertical = SizeFlags.ExpandFill,
            SizeFlagsHorizontal = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(280, 120), AutoBraceCompletionEnabled = false,
            TooltipText = "The script's source, read only. The game does not read this file.",
        };
        view.AddThemeFontOverride("font", CompanionTheme.MonoFont);
        view.AddThemeFontSizeOverride("font_size", 13);
        foreach (string color in new[] { "font_color", "font_readonly_color", "font_selected_color" }) view.AddThemeColorOverride(color, Palette.Text);
        view.AddThemeColorOverride("line_number_color", Palette.Faint);
        view.AddThemeColorOverride("selection_color", new Color(Palette.Accent, 0.28f));
        view.AddThemeColorOverride("caret_color", Palette.Accent);
        view.AddThemeColorOverride("current_line_color", new Color(Palette.Hover, 0.5f));
        StyleBoxFlat box = CompanionTheme.Box(Palette.Field, 8, Palette.Border);
        box.ContentMarginLeft = box.ContentMarginRight = 8;
        box.ContentMarginTop = box.ContentMarginBottom = 6;
        foreach (string style in new[] { "normal", "read_only", "focus" }) view.AddThemeStyleboxOverride(style, box);
        return view;
    }

    /// <summary>Lists these scripts (the open level's); the first is selected. <paramref name="gameRoot"/> is where sources are looked for.</summary>
    internal void SetScripts(string? gameRoot, IReadOnlyList<ScriptEntry> entries)
    {
        _root = gameRoot;
        _entries = entries;
        _current = null;
        _drafts.Clear();
        _sourceBaselines.Clear();
        _projectSources.Clear();
        _draftRevision++;
        Fill(keep: null);
    }

    /// <summary>
    /// Lists the scripts again after an edit (the same level, new compiled scripts): the same script stays selected, and the text and place in the view stay as
    /// they were, so that compiling does not take the player's place away.
    /// </summary>
    internal void Refresh(IReadOnlyList<ScriptEntry> entries)
    {
        ScriptEntry? previous = _current;
        StoreDraft();
        int line = _source.GetCaretLine(), column = _source.GetCaretColumn();
        double scroll = _source.ScrollVertical;
        _entries = entries;
        _draftRevision++;
        _current = null;
        ScriptEntry? keep = previous is null ? null : entries.FirstOrDefault(entry => entry.FromBaseWorld == previous.FromBaseWorld && entry.Summary.Name == previous.Summary.Name);
        Fill(keep);
        if (keep is null || !ReferenceEquals(_current, keep)) return;
        _source.SetCaretLine(Math.Min(line, _source.GetLineCount() - 1));
        _source.SetCaretColumn(Math.Min(column, _source.GetLine(_source.GetCaretLine()).Length));
        _source.ScrollVertical = Math.Min(scroll, Math.Max(0, _source.GetLineCount() - 1));
    }

    /// <summary>Turns typing in the source on or off (it stays off for a script that cannot be edited).</summary>
    internal void SetEditing(bool on)
    {
        _wantEditing = on;
        StoreDraft();
        ApplyEditable();
    }

    /// <summary>Shows the state of the text on view again: the page calls it when what the level runs changed without the text changing (a compile that was used).</summary>
    internal void RefreshInfo() => UpdateInfo();

    /// <summary>Forgets what was typed for a script and shows its source baseline's text again.</summary>
    internal void DiscardEdit(string name)
    {
        StoreDraft();
        if (_drafts.Remove(name)) _draftRevision++;
        if (_current is { FromBaseWorld: false } current && current.Summary.Name == name && _currentSource?.Source is { } source)
        {
            SetSourceText(source.Text);
            UpdateInfo();
        }
    }

    /// <summary>A delayed discard cannot drop text typed since its confirmation was requested.</summary>
    internal bool TryDiscardEdit(string name, EditorScriptDraftStamp expected)
    {
        if (!MatchesDraftState(expected)) return false;
        DiscardEdit(name);
        return true;
    }

    /// <summary>Puts the caret at the start of a line (0-based), in view.</summary>
    internal void GoToLine(int line)
    {
        _source.SetCaretLine(Math.Clamp(line, 0, _source.GetLineCount() - 1));
        _source.SetCaretColumn(0);
        _source.CenterViewportToCaret();
    }

    private void ApplyEditable()
    {
        bool on = _wantEditing && CanEditCurrent;
        _source.Editable = on;
        _source.TooltipText = on ? "Type here, then Compile and use. The game does not read this file: it runs the compiled script."
            : "The script's source, read only. The game does not read this file.";
        UpdateInfo();
    }

    private void OnText()
    {
        if (!_settingSource) StoreDraft();
        UpdateInfo();
        TextEdited?.Invoke();
    }

    /// <summary>The path, line count and state of the source shown: read only, or what was typed.</summary>
    private void UpdateInfo()
    {
        if (_currentSource?.Source is not { } source) return;
        string text = _source.Text;
        int lines = text.Count(c => c == '\n') + (text.Length > 0 && text[^1] != '\n' ? 1 : 0);
        bool own = _current is { FromBaseWorld: false };
        bool differs = own && text != source.Text, used = own && InUse(_current!.Summary.Name, text);
        bool notUsed = own && !used && (differs || IsReplaced?.Invoke(_current!.Summary.Name) == true);  // the level runs something else than this text
        string state = (_source.Editable ? "editing" : "read only") + (used ? " · in use" : notUsed ? " · not in use" : "");  // short: the line is one clipped line, as the column narrows
        bool projectSource = own && _projectSources.Contains(_current!.Summary.Name);
        string relative = Path.GetRelativePath(_root ?? ".", source.Path).Replace('\\', '/');
        const string folder = "data/MissionScripts/";
        string shown = relative.StartsWith(folder, StringComparison.OrdinalIgnoreCase) ? relative[folder.Length..] : relative;  // the folder is the same for every script
        _info.Text = $"{shown} · {Build.Count(lines, "line")} · {state}" + (projectSource ? " · project source" : "");
        _info.TooltipText = (projectSource ? $"{_current!.Summary.Name}.msl · source preserved in the editor project" : source.Path) +
            "\nThe game runs the compiled script in the level's world, not this file." +
            (used ? "\nIn use: the level runs the script compiled from this text." : notUsed ? "\nNot in use: the level does not run this text. Compile and use makes it run." : "");
    }

    /// <summary>Notes what is typed for the script on view: a text that differs from its source file is a draft, one that matches it is not.</summary>
    private void StoreDraft()
    {
        if (_current is not { FromBaseWorld: false } current || _currentSource?.Source is not { } source || !_source.Editable) return;
        if (_source.Text != source.Text)
        {
            if (_drafts.TryGetValue(current.Summary.Name, out string? before) && before == _source.Text) return;
            _drafts[current.Summary.Name] = _source.Text;
            _draftRevision++;
        }
        else if (_drafts.Remove(current.Summary.Name)) _draftRevision++;
    }

    /// <summary>Shows the scripts whose name, events or functions hold this text (all of them when it is empty).</summary>
    internal void Filter(string text)
    {
        _filter = text.Trim();
        Fill(keep: _current);
    }

    /// <summary>Selects the script called <paramref name="name"/> in the level's own world (or the base world's), clearing the search if it hides it.</summary>
    internal bool Select(string name, bool fromBase = false)
    {
        ScriptEntry? wanted = _entries.FirstOrDefault(entry => entry.FromBaseWorld == fromBase && string.Equals(entry.Summary.Name, name, StringComparison.Ordinal));
        if (wanted is null) return false;
        if (_filter.Length > 0 && !Matches(wanted)) _filter = "";
        Fill(keep: wanted);
        return _current == wanted;
    }

    private bool Matches(ScriptEntry entry) =>
        _filter.Length == 0 || entry.Summary.Name.Contains(_filter, StringComparison.OrdinalIgnoreCase) ||
        entry.Summary.Events.Any(name => name.Contains(_filter, StringComparison.OrdinalIgnoreCase)) ||
        entry.Summary.Calls.Any(call => call.Name.Contains(_filter, StringComparison.OrdinalIgnoreCase));

    private void Fill(ScriptEntry? keep)
    {
        StoreDraft();
        _list.Clear();
        TreeItem root = _list.CreateItem();
        TreeItem? wanted = null, first = null;
        for (int index = 0; index < _entries.Count; index++)
        {
            ScriptEntry entry = _entries[index];
            if (!Matches(entry)) continue;
            string runsOn = entry.FromBaseWorld ? "base world" : entry.Summary.Uses.Count switch { 0 => "—", 1 => "1 object", int n => $"{n} objects" };
            TreeItem item = Build.TableRow(_list, root, entry.Summary.Name, runsOn, string.Join(", ", entry.Summary.Events));
            item.SetMetadata(0, index);
            item.SetTooltipText(2, entry.Summary.Events.Count == 0 ? "No entry point: nothing starts this script by itself." : string.Join(", ", entry.Summary.Events));
            if (entry.FromBaseWorld)
            {
                for (int column = 0; column < 3; column++) item.SetCustomColor(column, Palette.Muted);
                item.SetTooltipText(0, $"{entry.Summary.Name}: a script of the base world of level {entry.SourceLevel}, which this level loads too.");
            }
            else if (entry.Summary.Uses.Count == 0)
            {
                item.SetCustomColor(1, Palette.Faint);
            }
            first ??= item;
            if (keep is not null && ReferenceEquals(entry, keep)) wanted = item;
        }
        bool any = first is not null;
        _empty.Text = _entries.Count == 0 ? "This level has no compiled scripts." : any ? "" : "No script matches the search.";
        _empty.Visible = _empty.Text.Length > 0;
        _list.Visible = any;
        TreeItem? target = wanted ?? first;
        if (target is null)
        {
            ClearSelection();
            return;
        }
        target.Select(0);
        _list.ScrollToItem(target);
        Choose(target);
    }

    private void Choose(TreeItem? item)
    {
        if (item is null) return;
        ScriptEntry entry = _entries[item.GetMetadata(0).AsInt32()];
        if (ReferenceEquals(entry, _current)) return;
        StoreDraft();
        _current = entry;
        _currentSource = SourceFor(entry);
        if (_currentSource.Source is { } source)
        {
            SetSourceText(!entry.FromBaseWorld && _drafts.TryGetValue(entry.Summary.Name, out string? draft) ? draft : source.Text);
            ApplyEditable();
        }
        else
        {
            SetSourceText("");
            ApplyEditable();  // a script with no source file is not typeable, whatever the Edit switch says
            _info.Text = _currentSource.Problem ?? "";
            _info.TooltipText = "";
        }
        Selected?.Invoke(entry, _currentSource);
    }

    private ScriptSourceResult SourceFor(ScriptEntry entry)
    {
        if (!entry.FromBaseWorld && _sourceBaselines.TryGetValue(entry.Summary.Name, out ScriptSourceResult? baseline)) return baseline;
        ScriptSourceResult found = _root is null
            ? new ScriptSourceResult(null, "Choose your game folder on Home to see script sources.")
            : ScriptSources.Find(_root, entry.SourceLevel, entry.Summary.Name);
        if (!entry.FromBaseWorld && found.Source is not null) _sourceBaselines[entry.Summary.Name] = found;
        return found;
    }

    /// <summary>
    /// Puts new text in the source view, at its first line, whether the view is shown or not: the scroll position and the first visible line kept from a
    /// longer text would lie past the end of a shorter one.
    /// </summary>
    private void SetSourceText(string text)
    {
        _source.SetLineAsFirstVisible(0);
        _source.SetCaretLine(0);
        _source.SetCaretColumn(0);
        _source.ScrollVertical = 0;
        _source.ScrollHorizontal = 0;
        _settingSource = true;
        try { _source.Text = text; }
        finally { _settingSource = false; }
        _source.SetLineAsFirstVisible(0);
        _source.SetCaretLine(0);
        _source.ScrollVertical = 0;
        _source.ScrollHorizontal = 0;
    }

    /// <summary>
    /// Brings the source view to its first line and left edge. Call it while the panel is shown, before it is hidden: the engine keeps the view's first
    /// visible line and updates it only while the view is shown, whoever moves the scroll bar or names the line, so a view hidden while scrolled far down
    /// keeps that line, and a text swapped in while it is hidden is shown from it, past its end when it is shorter (Godot logs "Index p_line = N is out
    /// of bounds" and the view sits on the last line).
    /// </summary>
    internal void ScrollToTop()
    {
        _source.SetLineAsFirstVisible(0);
        _source.ScrollVertical = 0;
        _source.ScrollHorizontal = 0;
        _source.SetCaretLine(0);
        _source.SetCaretColumn(0);
    }

    private void OnCaret()
    {
        int line = _source.GetCaretLine();
        SourceToken? token = line >= 0 && line < _source.GetLineCount() ? ScriptNames.TokenAt(_source.GetLine(line), _source.GetCaretColumn()) : null;
        if (token == _token) return;
        _token = token;
        NameUnderCaret?.Invoke(token);
    }

    private void ClearSelection()
    {
        bool had = _current is not null;
        _current = null;
        _currentSource = null;
        SetSourceText("");
        _info.Text = "";
        _info.TooltipText = "";
        if (had) Selected?.Invoke(null, null);
    }
}
