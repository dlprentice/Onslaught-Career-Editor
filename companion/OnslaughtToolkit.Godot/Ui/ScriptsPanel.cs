// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The compiled scripts of the open level, and the selected script's installed source beside them, read only. The list says what each script
/// runs on and handles; the source is the <c>.msl</c> file the script was compiled from, with line numbers. The game never reads that file
/// (it runs the compiled script in the level's world), so the panel says so, and says when a file is missing.
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
    private readonly Dictionary<string, string> _compiled = new(StringComparer.Ordinal);

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
    }

    /// <summary>Raised when the selected script changes (null: none is selected). The source result is what was found for it.</summary>
    internal event Action<ScriptEntry?, ScriptSourceResult?>? Selected;

    /// <summary>Raised when the quoted text or word under the source's caret changes (null: the caret is on none).</summary>
    internal event Action<SourceToken?>? NameUnderCaret;

    /// <summary>The quoted text or word the caret is on in the source.</summary>
    internal SourceToken? Token => _token;

    /// <summary>
    /// Whether the source can be typed in: the Edit switch is on and the selected script is one of the level's own with a source file to start from. The
    /// text typed is kept for the script (a draft) while another is chosen, and is not what the game runs until it is compiled and used.
    /// </summary>
    internal bool Editing => _source.Editable;

    /// <summary>Whether the selected script can be edited at all: one of the level's own, with a source file found.</summary>
    internal bool CanEditCurrent => _current is { FromBaseWorld: false } && _currentSource?.Source is not null;

    /// <summary>The text in the source view (line ends are \n).</summary>
    internal string SourceText => _source.Text;

    /// <summary>The text that last compiled and was used for each of the level's own scripts, by name: what a mod keeps as that script's source.</summary>
    internal IReadOnlyDictionary<string, string> CompiledSources => _compiled;

    internal Tree List => _list;
    internal CodeEdit Source => _source;
    internal string Info => _info.Text;
    internal Label InfoLabel => _info;
    internal string EmptyText => _empty.Visible ? _empty.Text : "";
    internal ScriptEntry? Current => _current;
    internal ScriptSourceResult? CurrentSource => _currentSource;

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
        _compiled.Clear();
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

    /// <summary>Records that this text compiled and was used for the script of this name.</summary>
    internal void MarkCompiled(string name, string text) => _compiled[name] = text;

    /// <summary>Forgets what was typed and compiled for a script and shows its source file's text again.</summary>
    internal void DiscardEdit(string name)
    {
        _drafts.Remove(name);
        _compiled.Remove(name);
        if (_current is { FromBaseWorld: false } current && current.Summary.Name == name && _currentSource?.Source is { } source)
        {
            SetSourceText(source.Text);
            UpdateInfo();
        }
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

    /// <summary>The path, line count and state of the source shown: read only, or what was typed.</summary>
    private void UpdateInfo()
    {
        if (_currentSource?.Source is not { } source) return;
        string text = _source.Text;
        int lines = text.Count(c => c == '\n') + (text.Length > 0 && text[^1] != '\n' ? 1 : 0);
        bool edited = _current is not null && _drafts.ContainsKey(_current.Summary.Name) && !_current.FromBaseWorld;
        string state = _source.Editable ? "editing, not used until compiled" : edited ? "your edit, read only" : "read only";
        string relative = Path.GetRelativePath(_root!, source.Path).Replace('\\', '/');
        const string folder = "data/MissionScripts/";
        string shown = relative.StartsWith(folder, StringComparison.OrdinalIgnoreCase) ? relative[folder.Length..] : relative;  // the folder is the same for every script
        _info.Text = $"{shown} · {Build.Count(lines, "line")} · {state}";
        _info.TooltipText = $"{source.Path}\nThe game runs the compiled script in the level's world, not this file.";
    }

    /// <summary>Notes what is typed for the script on view: a text that differs from its source file is a draft, one that matches it is not.</summary>
    private void StoreDraft()
    {
        if (_current is not { FromBaseWorld: false } current || _currentSource?.Source is not { } source || !_source.Editable) return;
        if (_source.Text != source.Text) _drafts[current.Summary.Name] = _source.Text;
        else _drafts.Remove(current.Summary.Name);
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
        if (_root is null)
        {
            _currentSource = new ScriptSourceResult(null, "Choose your game folder on Home to see script sources.");
        }
        else
        {
            _currentSource = ScriptSources.Find(_root, entry.SourceLevel, entry.Summary.Name);
        }
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

    /// <summary>
    /// Puts new text in the source view, at its first line. The view is brought to its top while the old text is still there: the scroll position or first
    /// visible line kept from a longer text would lie past the end of a shorter one, and Godot reports a line past the end as an engine error.
    /// </summary>
    private void SetSourceText(string text)
    {
        _source.SetCaretLine(0);
        _source.SetCaretColumn(0);
        _source.ScrollVertical = 0;
        _source.ScrollHorizontal = 0;
        _source.Text = text;
        _source.SetCaretLine(0);
        _source.ScrollVertical = 0;
        _source.ScrollHorizontal = 0;
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
