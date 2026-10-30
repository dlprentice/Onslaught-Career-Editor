// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Draws the Level editor against a Steam-shaped game folder and runs the editor's acceptance on it, in one of seven modes. Run on a
/// GPU output (godot-offscreen): <c>--script res://Development/LevelEditorCapture.cs -- --output=DIR --fixture=ANY_FILE --steam-root=DIR
/// [--mode=drag|typed|markers|scripts|names|flow|edit] [--sizes=1920x1080] [--level=100] [--row=12] [--expect-sha256=HEX] [--to=276.49,265.07]</c>.
/// <list type="bullet">
/// <item><c>drag</c> (the default): open level 100, click row 12's mark on the map, drag it to the pixel of 276.49, 265.07, let go, save
/// as a mod into the capture's own output, and compare the saved world file's SHA-256 with the one the Toolkit's pipeline gives for the same
/// coordinates (Z stays as stored) and the file's position for the row with the numbers the page shows. The pointer is pushed into the
/// window as events, so they take the engine's own route to the map.</item>
/// <item><c>typed</c>: the earlier acceptance, typing 276.49, 265.07 and -12.1 into the fields.</item>
/// <item><c>markers</c>: for the mirror check. Drags the level's two Target Tanks on the map to known places in front of the player's start (one
/// straight ahead, one 25 degrees to the map's left of it), saves the mod, and writes what was placed to <c>markers.txt</c> beside the
/// frames, which hold the game's data and stay in local-data. Look at them in Onslaught CE to see whether the left of the map is the left
/// of the cockpit.</item>
/// <item><c>scripts</c>: the read-only scripts view. Counts the open level's scripts and how many find their source, selects an object that
/// names a script, follows its script button into the Scripts view, looks at a script that calls the most game functions and at a base
/// world's script if the level has one, and follows a script's object button back to the map. The frames hold the game's script text and
/// stay in local-data.</item>
/// <item><c>names</c>: the links from a script's source. Finds a quoted text in the sources of the level's scripts that names a waypoint path
/// of the level and one that names an object, puts the caret in each, follows the buttons that name offers (the path highlighted on the map,
/// then every path drawn, then the object selected), looks at a text that names only an object of the base world, and at an object that is a point
/// of a path. The frames hold the game's script text and stay in local-data.</item>
/// <item><c>flow</c>: the Scripts view across level changes, in a real window (the engine keeps a source view's first visible line while the view is hidden): a long
/// source scrolled to its end, the Scripts switch off, another level opened, the switch on again, and the same leaving the page; every first script must open at its top
/// and no engine error may be logged.</item>
/// <item><c>edit</c>: editing a script's source on the page. Picks a script of the level with an installed source that compiles, types into it, compiles and uses a changed
/// number, is refused with a line for a name the script does not have, uses a source that adds a call to Damage (the warning), puts the shipped script back, and leaves a
/// draft (the close prompt and the level picker ask). The frames hold the game's script text and stay in local-data.</item>
/// </list>
/// The game folder is only read; every file this writes stays inside the output directory. Development builds only.
/// </summary>
public partial class LevelEditorCapture : SceneTree
{
    /// <summary>The Toolkit pipeline's world body for row 12 of level 100 moved to 276.49, 265.07, -12.1 (the typed acceptance).</summary>
    private const string TypedSha256 = "b078e3d29e7916d9785e1985b8addc48d5898444b70b5055da0ca15ba4511f94";

    /// <summary>
    /// The pipeline's world body for row 12 of level 100 moved to 276.49, 265.07 with its stored -0 for Z: world_edit_move.py's preview
    /// of the retail view's level 100 world body (108,502 bytes, SHA-256 e281c4e7...), 6 changed byte positions.
    /// </summary>
    private const string DragSha256 = "5f40f82f08e058a39458f9807b710318dbc00dccc0ecbd3d9a2d921ffac6d48a";

    private string _output = "", _steamRoot = "", _expected = "", _mode = "drag";
    private int _shots, _level = 100, _row = 12;
    private double _toX = 276.49, _toY = 265.07;
    private bool _passed = true;

    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exitCode = 1;
        try
        {
            string sizes = "1920x1080";
            foreach (string argument in OS.GetCmdlineUserArgs())
            {
                if (argument.StartsWith("--output=", StringComparison.Ordinal)) _output = argument["--output=".Length..];
                if (argument.StartsWith("--sizes=", StringComparison.Ordinal)) sizes = argument["--sizes=".Length..];
                if (argument.StartsWith("--steam-root=", StringComparison.Ordinal)) _steamRoot = argument["--steam-root=".Length..];
                if (argument.StartsWith("--level=", StringComparison.Ordinal)) _level = int.Parse(argument["--level=".Length..], CultureInfo.InvariantCulture);
                if (argument.StartsWith("--row=", StringComparison.Ordinal)) _row = int.Parse(argument["--row=".Length..], CultureInfo.InvariantCulture);
                if (argument.StartsWith("--mode=", StringComparison.Ordinal)) _mode = argument["--mode=".Length..];
                if (argument.StartsWith("--expect-sha256=", StringComparison.Ordinal)) _expected = argument["--expect-sha256=".Length..].ToLowerInvariant();
                if (argument.StartsWith("--to=", StringComparison.Ordinal))
                {
                    string[] to = argument["--to=".Length..].Split(',');
                    _toX = double.Parse(to[0], CultureInfo.InvariantCulture);
                    _toY = double.Parse(to[1], CultureInfo.InvariantCulture);
                }
            }
            if (_expected.Length == 0) _expected = _mode == "typed" ? TypedSha256 : DragSha256;
            if (_output.Length == 0 || _steamRoot.Length == 0 || !Directory.Exists(_steamRoot) || _mode is not ("drag" or "typed" or "markers" or "scripts" or "names" or "flow" or "edit"))
            {
                GD.PrintErr("--output=DIR and --steam-root=DIR (a Steam-shaped folder holding the game) are required; --mode is drag, typed, markers, scripts, names, flow or edit.");
                return;
            }
            Directory.CreateDirectory(_output);
            foreach (string size in sizes.Split(',', StringSplitOptions.RemoveEmptyEntries))
            {
                string[] parts = size.Split('x');
                await CaptureAt(new Vector2I(int.Parse(parts[0], CultureInfo.InvariantCulture), int.Parse(parts[1], CultureInfo.InvariantCulture)));
            }
            GD.Print($"ACCEPTANCE_RESULT {(_passed ? "PASS" : "FAIL")}");
            GD.Print($"CAPTURES_DONE {_shots} screens in {_output}");
            exitCode = _passed ? 0 : 2;
        }
        catch (Exception error)
        {
            GD.PrintErr("Level editor capture stopped: " + error);
        }
        finally
        {
            Quit(exitCode);
        }
    }

    private void Report(bool ok, string what)
    {
        if (!ok) _passed = false;
        GD.Print($"ACCEPTANCE {(ok ? "ok  " : "FAIL")} {what}");
    }

    /// <summary>Mouse events pushed into a window at pixels of the map, so they reach it by the engine's own route.</summary>
    private sealed class Pointer(SubViewport window, LevelMap map)
    {
        /// <summary>Where the pointer is, in pixels of the map.</summary>
        public Vector2 At { get; private set; }

        private Vector2 InWindow(Vector2 local) => map.GetGlobalRect().Position + local;

        public void MoveTo(Vector2 local, MouseButtonMask held = 0)
        {
            Vector2 now = InWindow(local);
            window.PushInput(new InputEventMouseMotion { Position = now, GlobalPosition = now, Relative = now - InWindow(At), ButtonMask = held }, true);
            At = local;
        }

        public void Glide(Vector2 to, MouseButtonMask held = 0, float stepPixels = 9)
        {
            Vector2 from = At;
            int steps = Math.Max(1, (int)Math.Ceiling(from.DistanceTo(to) / stepPixels));
            for (int step = 1; step <= steps; step++) MoveTo(from.Lerp(to, step / (float)steps), held);
        }

        public void Press() => Button(MouseButton.Left, true);

        public void Release() => Button(MouseButton.Left, false);

        public void Wheel(bool up)
        {
            Vector2 now = InWindow(At);
            window.PushInput(new InputEventMouseButton { ButtonIndex = up ? MouseButton.WheelUp : MouseButton.WheelDown, Pressed = true, Factor = 1, Position = now, GlobalPosition = now }, true);
        }

        public void Escape() => window.PushInput(new InputEventKey { Keycode = Key.Escape, PhysicalKeycode = Key.Escape, Pressed = true }, true);

        private void Button(MouseButton button, bool pressed)
        {
            Vector2 now = InWindow(At);
            window.PushInput(new InputEventMouseButton { ButtonIndex = button, Pressed = pressed, Position = now, GlobalPosition = now, ButtonMask = pressed ? MouseButtonMask.Left : 0 }, true);
        }
    }

    private async Task CaptureAt(Vector2I size)
    {
        string label = $"{size.X}x{size.Y}";
        string work = Path.Combine(_output, "work-" + label);
        Directory.CreateDirectory(work);
        SubViewport viewport = new() { Size = size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always, TransparentBg = false, GuiEmbedSubwindows = true };
        Root.AddChild(viewport);
        CompanionEnvironment environment = new([_steamRoot], Path.Combine(work, "settings", "settings.json"), () => false, _ => { }, Path.Combine(work, "backups"));
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false, environment);
        viewport.AddChild(app);
        await Settle();
        for (int frame = 0; frame < 600 && (app.Game.Busy || app.Game.Folder is null); frame++) await Settle();
        Report(app.Game.Folder is not null, $"the game folder was found: {app.Game.Folder?.Root}");
        LevelEditorPage page = app.LevelEditor;
        app.Navigate("levels");
        await Settle();
        Report(page.Level.ItemCount > 1, $"the page lists {page.Level.ItemCount - 1} levels");
        await Shot(viewport, label, "level-editor-1-pick-a-level");

        bool opened = page.OpenLevel(_level);
        await Settle();
        Report(opened && page.Model?.Session is not null, $"level {_level} opened: {page.Model?.Session?.Body.Things.Count} objects, subtitle \"{app.PageSubtitle.Text}\"");
        Report(page.Map.HasRelief && page.Map.IsVisibleInTree(), $"the map shows the level's relief: {page.Map.Size.X:0}x{page.Map.Size.Y:0} pixels, {page.Map.View.Scale:0.000} pixels to the unit, " +
            (page.MapBesideTable ? "beside the table" : "below the table"));
        await Shot(viewport, label, "level-editor-2-level-open");

        string mods = Path.Combine(_output, "mods-" + label);
        if (_mode == "typed") await TypedAcceptance(viewport, app, page, label, mods);
        else if (_mode == "drag") await DragAcceptance(viewport, app, page, label, mods);
        else if (_mode == "scripts") await ScriptsView(viewport, app, page, label);
        else if (_mode == "names") await NamesView(viewport, app, page, label);
        else if (_mode == "flow") await ScriptsFlow(viewport, app, page, label);
        else if (_mode == "edit") await EditView(viewport, app, page, label);
        else await Markers(viewport, app, page, label, mods);
        viewport.QueueFree();
        await Settle();
    }

    /// <summary>The scripts view: the list and the source beside it, and the links between scripts and the objects that name them. Writes nothing.</summary>
    private async Task ScriptsView(SubViewport viewport, CompanionApp app, LevelEditorPage page, string label)
    {
        LevelEditorModel model = page.Model!;
        string root = app.Game.Folder!.AssetRoot;
        int own = model.Scripts.Count(entry => !entry.FromBaseWorld), baseScripts = model.Scripts.Count - own;
        List<string> missing = [.. model.Scripts.Where(entry => ScriptSources.Find(root, entry.SourceLevel, entry.Summary.Name).Source is null)
            .Select(entry => $"{(entry.FromBaseWorld ? "base " : "")}{entry.Summary.Name}")];
        Report(own > 0, $"level {_level} has {own} scripts of its own and {baseScripts} of its base world");
        Report(missing.Count == 0, $"{model.Scripts.Count - missing.Count} of {model.Scripts.Count} scripts find their source" + (missing.Count > 0 ? $"; without: {string.Join(", ", missing)}" : ""));

        // An object that names a script: its row, its script button.
        ScriptEntry? named = model.Scripts.Where(entry => !entry.FromBaseWorld && entry.Summary.Uses.Count > 0).OrderByDescending(entry => entry.Summary.Uses.Count).FirstOrDefault();
        Report(named is not null, $"the script named by the most objects is {named?.Summary.Name} ({named?.Summary.Uses.Count} objects)");
        if (named is null) return;
        int row = named.Summary.Uses[0].Row;
        Report(page.SelectIndex(row) && page.ObjectScriptButtons.Count > 0, $"row {row} ({model.Row(row)?.Label}) offers its script: \"{page.ObjectScriptsText}\"");
        await Shot(viewport, label, "level-editor-3-object-names-a-script");

        // Its script button shows the script in the Scripts view, beside its source.
        Button button = page.ObjectScriptButtons.First(candidate => candidate.Text.EndsWith(": " + named.Summary.Name, StringComparison.Ordinal));
        button.EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(page.ScriptsToggle.ButtonPressed && page.Scripts.Current?.Summary.Name == named.Summary.Name && page.Scripts.Source.Text.Length > 0 && !page.Scripts.Source.Editable,
            $"the Scripts view shows {page.Scripts.Current?.Summary.Name}: {page.Scripts.Source.GetLineCount()} lines of source, read only. {page.Scripts.Info}");
        await Shot(viewport, label, "level-editor-4-script-and-source");

        // The script that calls the most game functions, and a base world's script if there is one.
        ScriptEntry busiest = model.Scripts.Where(entry => !entry.FromBaseWorld).OrderByDescending(entry => entry.Summary.Calls.Sum(call => call.Count)).First();
        Report(page.Scripts.Select(busiest.Summary.Name), $"the busiest script, {busiest.Summary.Name}: handles {string.Join(", ", busiest.Summary.Events)}; {busiest.Summary.Calls.Count} functions called");
        await Shot(viewport, label, "level-editor-5-busiest-script");
        if (model.Scripts.FirstOrDefault(entry => entry.FromBaseWorld) is { } baseEntry)
        {
            Report(page.Scripts.Select(baseEntry.Summary.Name, fromBase: true) && page.Scripts.Current!.FromBaseWorld, $"a base world script, {baseEntry.Summary.Name}, is read from level {baseEntry.SourceLevel}'s folder");
            await Shot(viewport, label, "level-editor-6-base-world-script");
        }

        // A script's object button goes back to the map.
        page.Scripts.Select(named.Summary.Name);
        await Settle();
        Button use = page.ScriptUseButtons[0];
        use.EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(!page.ScriptsToggle.ButtonPressed && page.SelectedRow == named.Summary.Uses[0].Row && page.Map.IsVisibleInTree() && page.Map.Selected == page.SelectedRow,
            $"the object button shows row {page.SelectedRow} on the table and the map");
        await Shot(viewport, label, "level-editor-7-object-from-script");
    }

    /// <summary>The links from a source's quoted texts to what they name, and the waypoint paths on the map. Writes nothing.</summary>
    /// <summary>
    /// The Scripts view across level changes, in a real window: the engine keeps a source view's first visible line and refreshes it only while the view is
    /// shown, so a long source scrolled to its end, the Scripts switch turned off, another level opened and the switch turned on again used to open the new level's
    /// first script scrolled into its middle or past its end (Godot logged "Index p_line = N is out of bounds"; this run fails on any engine error line). The
    /// route's headless run cannot show it: the view has no size there. Each step of the chain must open its level's first script at the top.
    /// </summary>
    private async Task ScriptsFlow(SubViewport viewport, CompanionApp app, LevelEditorPage page, string label)
    {
        string root = app.Game.Folder!.AssetRoot;
        int[] wanted = [100, 110, 200, 201, 300, 100];
        int[] levels = [.. wanted.Where(level => page.Model!.Levels.Any(archive => archive.Level == level))];
        Report(levels.Length >= 2, $"the game has the levels the flow goes through: {string.Join(", ", levels)}");
        int top = 0, steps = 0;
        for (int step = 0; step + 1 < levels.Length; step++)
        {
            // the level's own script with the longest source: scrolled to its end, with the caret on the last line
            Report(page.OpenLevel(levels[step]), $"level {levels[step]} opens");
            await Settle();
            page.ScriptsToggle.ButtonPressed = true;
            await Settle();
            ScriptEntry? longest = page.Model!.Scripts.Where(entry => !entry.FromBaseWorld)
                .OrderByDescending(entry => ScriptSources.Find(root, entry.SourceLevel, entry.Summary.Name).Source?.Lines ?? 0).FirstOrDefault();
            if (longest is not null) page.Scripts.Select(longest.Summary.Name);
            await Settle();
            int lines = page.Scripts.Source.GetLineCount();
            page.Scripts.Source.ScrollVertical = Math.Max(0, lines - 5);
            page.Scripts.Source.SetCaretLine(lines - 1);
            await Settle();
            page.ScriptsToggle.ButtonPressed = false;
            await Settle();
            Report(page.OpenLevel(levels[step + 1]), $"level {levels[step + 1]} opens with the Scripts switch off (after {longest?.Summary.Name}, {lines} lines, first visible line {page.Scripts.Source.GetFirstVisibleLine()})");
            await Settle();
            page.ScriptsToggle.ButtonPressed = true;
            await Settle();
            await Settle();
            int first = page.Scripts.Source.GetFirstVisibleLine(), caret = page.Scripts.Source.GetCaretLine();
            double scroll = page.Scripts.Source.ScrollVertical;
            steps++;
            if (first == 0 && caret == 0 && scroll == 0) top++;
            Report(first == 0 && caret == 0 && scroll == 0,
                $"level {levels[step + 1]}'s first script, {page.Scripts.Current?.Summary.Name}, opens at its top: first visible line {first}, caret line {caret}, scroll {scroll} ({page.Scripts.Source.GetLineCount()} lines)");
        }
        Report(steps > 0 && top == steps, $"{top} of {steps} level changes opened the first script at its top");
        // The same with the page left for another (the game folder or the level changed behind it) instead of the Scripts switch turned off.
        for (int step = 0; step + 1 < levels.Length; step++)
        {
            page.OpenLevel(levels[step]);
            await Settle();
            page.ScriptsToggle.ButtonPressed = true;
            await Settle();
            ScriptEntry? longest = page.Model!.Scripts.Where(entry => !entry.FromBaseWorld)
                .OrderByDescending(entry => ScriptSources.Find(root, entry.SourceLevel, entry.Summary.Name).Source?.Lines ?? 0).FirstOrDefault();
            if (longest is not null) page.Scripts.Select(longest.Summary.Name);
            await Settle();
            int lines = page.Scripts.Source.GetLineCount();
            page.Scripts.Source.ScrollVertical = Math.Max(0, lines - 5);
            page.Scripts.Source.SetCaretLine(lines - 1);
            await Settle();
            app.Navigate("home");
            await Settle();
            page.OpenLevel(levels[step + 1]);
            await Settle();
            app.Navigate("levels");
            await Settle();
            await Settle();
            int first = page.Scripts.Source.GetFirstVisibleLine(), caret = page.Scripts.Source.GetCaretLine();
            Report(first == 0 && caret == 0 && page.Scripts.Source.ScrollVertical == 0,
                $"leaving the page: level {levels[step + 1]}'s first script, {page.Scripts.Current?.Summary.Name}, opens at its top: first visible line {first}, caret line {caret} ({page.Scripts.Source.GetLineCount()} lines)");
        }
        await Shot(viewport, label, "level-editor-flow");
    }

    /// <summary>
    /// Editing a script's source on the page, looked at (see the <c>edit</c> mode): read only, typeable, compiled and used with one number raised, refused with a line, used
    /// with an added call to Damage (the warning), the shipped script put back, and a draft that the close prompt and the level picker ask about. Each step reports what the page
    /// says; the frames hold the game's script text.
    /// </summary>
    private async Task EditView(SubViewport viewport, CompanionApp app, LevelEditorPage page, string label)
    {
        LevelEditorModel model = page.Model!;
        string root = app.Game.Folder!.AssetRoot;
        Regex pause = new(@"Pause\(\s*([0-9]+(?:\.[0-9]+)?)\s*\)", RegexOptions.CultureInvariant);

        // The first script of the level with an installed source that holds a Pause call, compiles as it is, and still compiles with its number raised by one.
        ScriptEntry? chosen = null;
        string source = "", raised = "", broken = "", killing = "";
        foreach (ScriptEntry entry in model.Scripts.Where(entry => !entry.FromBaseWorld))
        {
            if (model.OwnScriptIndex(entry) is not int own || ScriptSources.Find(root, entry.SourceLevel, entry.Summary.Name).Source is not { } found) continue;
            Match match = pause.Match(found.Text);
            if (!match.Success) continue;
            string number = (double.Parse(match.Groups[1].Value, CultureInfo.InvariantCulture) + 1).ToString("0.0", CultureInfo.InvariantCulture);
            string up = found.Text[..match.Index] + $"Pause({number})" + found.Text[(match.Index + match.Length)..];
            int semicolon = found.Text.IndexOf(';', match.Index + match.Length);
            if (semicolon < 0 || !model.CompileScript(own, found.Text, root).Ok || !model.CompileScript(own, up, root).Ok) continue;
            (chosen, source, raised) = (entry, found.Text, up);
            broken = found.Text[..match.Index] + "Pause(nosuchname)" + found.Text[(match.Index + match.Length)..];
            killing = found.Text[..(semicolon + 1)] + "\n\tDamage(1.0);" + found.Text[(semicolon + 1)..];
            break;
        }
        Report(chosen is not null, $"a script of level {_level} with an installed source that compiles, holds a Pause call and compiles with its number raised: {chosen?.Summary.Name}");
        if (chosen is null) return;

        page.ScriptsToggle.ButtonPressed = true;
        await Settle();
        page.Scripts.Select(chosen.Summary.Name);
        await Settle();
        Report(!page.Scripts.Source.Editable && !page.EditSource.Disabled && page.CompileScriptButton.Disabled && page.ShippedScriptButton.Disabled,
            $"{chosen.Summary.Name} is on view read only, with Edit source offered: \"{page.Scripts.Info}\"");
        await Shot(viewport, label, "edit-1-read-only");

        page.EditSource.ButtonPressed = true;
        await Settle();
        Report(page.Scripts.Source.Editable && !page.CompileScriptButton.Disabled, $"Edit source makes the view typeable: \"{page.Scripts.Info}\"");
        await Shot(viewport, label, "edit-2-editing");

        page.Scripts.Source.Text = raised;
        page.CompileScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(page.ScriptEditNote.StartsWith("Replaced ", StringComparison.Ordinal) && page.Summary.StartsWith("1 script replaced", StringComparison.Ordinal) && !page.Undo.Disabled && !page.Save.Disabled &&
               !page.ShippedScriptButton.Disabled, $"one number raised, compiled and used: \"{page.ScriptEditNote.Replace('\n', '|')}\" / \"{page.Summary}\"");
        await Shot(viewport, label, "edit-3-compiled-and-used");

        page.Scripts.Source.Text = broken;
        page.CompileScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(page.ScriptEditNote.StartsWith("line ", StringComparison.Ordinal) && page.Summary.StartsWith("1 script replaced", StringComparison.Ordinal) && page.Scripts.Source.GetCaretLine() >= 0,
            $"a name the script does not have is refused with its line, the caret goes there and the level keeps the script it had: \"{page.ScriptEditNote.Replace('\n', '|')}\" (caret line {page.Scripts.Source.GetCaretLine() + 1})");
        await Shot(viewport, label, "edit-4-refused-with-a-line");

        page.Scripts.Source.Text = killing;
        page.CompileScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(page.ScriptEditNote.Contains("calls Damage more often", StringComparison.Ordinal) && page.Summary.StartsWith("1 script replaced", StringComparison.Ordinal),
            $"a source that adds a call to Damage is used and warned about: \"{page.ScriptEditNote.Replace('\n', '|')}\"");
        await Shot(viewport, label, "edit-5-warning");

        page.ShippedScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(page.Summary.StartsWith("No changes yet", StringComparison.Ordinal) && page.Scripts.Source.Text == source && page.ShippedScriptButton.Disabled && !page.HasChanges,
            $"the shipped script is put back and the source file's text shows again: \"{page.ScriptEditNote.Replace('\n', '|')}\"");
        await Shot(viewport, label, "edit-6-shipped-back");

        page.Scripts.Source.Text = raised;
        await Settle();
        int other = model.Levels.Select(archive => archive.Level).FirstOrDefault(level => level != _level);
        page.PickLevel(other);
        await Settle();
        Report(page.HasChanges && page.ChangeCount == 1 && app.DiscardDialog.Visible && app.DiscardDialog.DialogText.Contains("not saved", StringComparison.Ordinal),
            $"text typed and not compiled is a draft, and choosing another level asks first: \"{app.DiscardDialog.DialogText}\"");
        await Shot(viewport, label, "edit-7-draft-asks");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        await Settle();
        Report(page.Model!.Level == _level && page.Scripts.Source.Text == raised, "and the level and the text stay when the player cancels");
        Report(page.DraftNote.StartsWith($"Text typed for {chosen.Summary.Name} is not in use", StringComparison.Ordinal), $"the changes card says which script the unsaved text is for: \"{page.DraftNote}\"");

        // The draft is dropped with the button that puts the shipped script back (the level already uses the shipped script), which lets the unsaved-work prompts go.
        Report(!page.ShippedScriptButton.Disabled, "the button that puts the shipped script back is there for the draft");
        page.ShippedScriptButton.EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(page.Scripts.Source.Text == source && !page.HasChanges && page.ChangeCount == 0 && page.ShippedScriptButton.Disabled, $"the draft is dropped and the source file's text shows again: \"{page.ScriptEditNote}\"");
        await Shot(viewport, label, "edit-8-draft-dropped");
    }

    private async Task NamesView(SubViewport viewport, CompanionApp app, LevelEditorPage page, string label)
    {
        LevelEditorModel model = page.Model!;
        WorldBody world = model.Session!.Body;
        string root = app.Game.Folder!.AssetRoot;
        // The first quoted text, in the order of the scripts, that names a path of the level, the first that names an object and the first that names only an object of the base world.
        (string Script, int Line, int Column, string Text)? forPath = null, forObject = null, forBase = null;
        foreach (ScriptEntry entry in model.Scripts.Where(entry => !entry.FromBaseWorld))
        {
            if (ScriptSources.Find(root, entry.SourceLevel, entry.Summary.Name).Source is not { } source) continue;
            string[] lines = source.Text.Split('\n');
            for (int line = 0; line < lines.Length && (forPath is null || forObject is null || forBase is null); line++)
                for (int column = 0; column <= lines[line].Length; column++)
                    if (ScriptNames.TokenAt(lines[line], column) is { Quoted: true } token)
                    {
                        IReadOnlyList<NameMatch> matches = ScriptNames.Resolve(token.Text, world, model.Scripts, model.BaseWorld);
                        if (forPath is null && matches.Any(match => match.Kind == NameKind.Path)) forPath = (entry.Summary.Name, line, token.Start + 1, token.Text);
                        if (forObject is null && matches.Any(match => match.Kind == NameKind.Object) && !matches.Any(match => match.Kind == NameKind.Path)) forObject = (entry.Summary.Name, line, token.Start + 1, token.Text);
                        if (forBase is null && matches.Count > 0 && matches.All(match => match.Kind == NameKind.BaseObject)) forBase = (entry.Summary.Name, line, token.Start + 1, token.Text);
                        column = token.Start + token.Length + 1;  // past the closing quote (a column just after it is still in the text): on to the rest of the line
                    }
            if (forPath is not null && forObject is not null && forBase is not null) break;
        }
        Report(forPath is not null && forObject is not null && forBase is not null,
            $"a quoted text names a path ({forPath?.Text} in {forPath?.Script}), one names an object ({forObject?.Text} in {forObject?.Script}) and one names only an object of the base world ({forBase?.Text} in {forBase?.Script})");
        if (forPath is null || forObject is null || forBase is null) return;

        async Task Caret((string Script, int Line, int Column, string Text) at)
        {
            page.ShowScript(at.Script);
            await Settle();
            page.Scripts.Source.SetCaretLine(at.Line);
            page.Scripts.Source.SetCaretColumn(at.Column);
            await Settle();
        }

        await Caret(forPath.Value);
        Report(page.Scripts.Token is { Quoted: true } && page.NameButtons.Any(button => button.Text.StartsWith("path ", StringComparison.Ordinal)), $"the caret in \"{forPath.Value.Text}\" offers: {page.NamesTitle} {string.Join(" | ", page.NameButtons.Select(button => button.Text))}");
        await Shot(viewport, label, "level-editor-3-source-names-a-path");
        page.NameButtons.First(button => button.Text.StartsWith("path ", StringComparison.Ordinal)).EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(page.Map.HighlightedPath is not null && !page.ScriptsToggle.ButtonPressed && page.Map.DrawablePaths > 0, $"the path button shows the path on the map: \"{page.HighlightedPathText}\"; {page.Map.DrawablePaths} paths have a line");
        await Shot(viewport, label, "level-editor-4-the-path-on-the-map");
        page.PathsToggle.ButtonPressed = true;
        page.Map.FitToLevel();  // the whole level, so that every path is in view
        await Settle();
        await Shot(viewport, label, "level-editor-5-every-path");
        page.PathsToggle.ButtonPressed = false;
        page.HidePath.EmitSignal(BaseButton.SignalName.Pressed);
        await Caret(forObject.Value);
        Report(page.NameButtons.Any(button => button.Text.StartsWith("unit ", StringComparison.Ordinal) || button.Text.Contains(" · ", StringComparison.Ordinal)), $"the caret in \"{forObject.Value.Text}\" offers: {page.NamesTitle} {string.Join(" | ", page.NameButtons.Select(button => button.Text))}");
        await Shot(viewport, label, "level-editor-6-source-names-an-object");
        page.NameButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
        await Settle();
        Report(!page.ScriptsToggle.ButtonPressed && page.SelectedRow is not null && page.Map.Selected == page.SelectedRow, $"the object button shows row {page.SelectedRow} on the table and the map");
        await Shot(viewport, label, "level-editor-7-the-object");

        // A name only an object of the base world has is said, with nothing to go to.
        await Caret(forBase.Value);
        Report(page.NameButtons.Count == 0 && page.NameLabels.Count > 0 && page.NameLabels.All(label => label.Text.EndsWith(" · base world", StringComparison.Ordinal)),
            $"the caret in \"{forBase.Value.Text}\" says: {page.NamesTitle} {string.Join(" | ", page.NameLabels.Select(label => label.Text))}");
        await Shot(viewport, label, "level-editor-8-source-names-a-base-object");

        // An object that is a point of a path offers the path.
        int onPath = Enumerable.Range(0, world.Things.Count).FirstOrDefault(row => WaypointCatalog.Through(world, row).Count > 0, -1);
        Report(onPath >= 0, $"row {onPath} is a point of a path");
        if (onPath >= 0)
        {
            page.SelectIndex(onPath);
            await Settle();
            Report(page.ObjectPathButtons.Count > 0, $"the object offers: {string.Join(" | ", page.ObjectPathButtons.Select(button => button.Text))}");
            page.ObjectPathButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
            await Settle();
            Report(page.Map.HighlightedPath is not null && page.Map.Selected == onPath, $"its path button shows the path with the object still selected: \"{page.HighlightedPathText}\"");
            await Shot(viewport, label, "level-editor-9-the-objects-path");
        }
    }

    private async Task TypedAcceptance(SubViewport viewport, CompanionApp app, LevelEditorPage page, string label, string mods)
    {
        bool selected = page.SelectRow(_row);
        await Settle();
        string name = page.SelectedName ?? "";
        Report(selected && name.StartsWith("Target Tank", StringComparison.Ordinal), $"row {_row} is \"{name}\" at {page.X.Text}, {page.Y.Text}, {page.Z.Text}");
        await Shot(viewport, label, "level-editor-3-object-selected");

        page.X.Text = "276.49";
        page.Y.Text = "265.07";
        page.Z.Text = "-12.1";
        page.X.EmitSignal(LineEdit.SignalName.TextSubmitted, page.X.Text);
        await Settle();
        Report(page.Note.Contains("now stands at 276.49, 265.07, -12.1", StringComparison.Ordinal), $"typing moved it: \"{page.Note}\"");
        Report(page.Summary.StartsWith("1 object moved", StringComparison.Ordinal), $"summary: \"{page.Summary}\"");
        await Shot(viewport, label, "level-editor-4-moved");
        await SaveAndCompare(viewport, page, label, mods, 5);
    }

    private async Task DragAcceptance(SubViewport viewport, CompanionApp app, LevelEditorPage page, string label, string mods)
    {
        LevelMap map = page.Map;
        LevelEditorModel model = page.Model!;
        ObjectRow? row = model.Row(_row);
        Report(row is not null && row.Label.StartsWith("Target Tank", StringComparison.Ordinal), $"row {_row} is \"{row?.Label}\", stored at {row?.Position.X}, {row?.Position.Y}, {row?.Position.Z}");
        if (row is null) return;
        System.Numerics.Vector3 stored = row.Position;
        Pointer pointer = new(viewport, map);

        // The pointer comes to the mark and clicks it: the row is selected in the map, the table and the fields.
        Vector2 mark = map.ToScreen(stored.X, stored.Y);
        pointer.MoveTo(mark);
        pointer.Press();
        pointer.Release();
        await Settle();
        Report(page.SelectedRow == _row && map.Selected == _row && page.Table.GetSelected()?.GetMetadata(0).AsInt32() == _row,
            $"a click on the mark selected row {page.SelectedRow} (the table's {page.Table.GetSelected()?.GetMetadata(0).AsInt32()}); the fields hold {page.X.Text}, {page.Y.Text}, {page.Z.Text}");
        await Shot(viewport, label, "level-editor-3-object-selected");

        // Drag it to the pixel of the target position: the map's own transform says where that is.
        Vector2 aim = map.ToScreen(_toX, _toY);
        pointer.Press();
        pointer.Glide(mark.Lerp(aim, 0.6f), MouseButtonMask.Left);
        Report(map.Dragging && model.Row(_row)!.Position == stored, "while the mark is dragged it follows the pointer and the page still holds the stored position");
        await Shot(viewport, label, "level-editor-4-dragging");
        pointer.Glide(aim, MouseButtonMask.Left);
        pointer.Release();
        await Settle();
        System.Numerics.Vector3 now = model.Row(_row)!.Position;
        string shown = $"{page.X.Text}, {page.Y.Text}, {page.Z.Text}";
        Report(!map.Dragging && page.Note.Contains($"now stands at {_toX.ToString(CultureInfo.InvariantCulture)}, {_toY.ToString(CultureInfo.InvariantCulture)}, -0", StringComparison.Ordinal),
            $"letting go moved it: \"{page.Note}\"");
        Report(page.X.Text == CoordinateInput.Format(now.X) && page.Y.Text == CoordinateInput.Format(now.Y) && page.Z.Text == CoordinateInput.Format(now.Z) && BitConverter.SingleToUInt32Bits(now.Z) == BitConverter.SingleToUInt32Bits(stored.Z),
            $"the fields show the stored numbers: {shown}; Z is the stored {CoordinateInput.Format(stored.Z)} bit for bit");
        Report(page.Summary.StartsWith("1 object moved", StringComparison.Ordinal), $"summary: \"{page.Summary}\"");
        await Shot(viewport, label, "level-editor-5-moved");
        await SaveAndCompare(viewport, page, label, mods, 6);

        // The numbers the page showed are the numbers in the file it saved.
        string world = Path.Combine(mods, page.SaveDialog.Id.Text, "data", "worlds", $"world{_level:D3}.wrd");
        if (File.Exists(world))
        {
            System.Numerics.Vector3 inFile = WorldBody.Read(File.ReadAllBytes(world)).Things[_row].Init.Position;
            Report(CoordinateInput.Format(inFile.X) == page.X.Text && CoordinateInput.Format(inFile.Y) == page.Y.Text && CoordinateInput.Format(inFile.Z) == page.Z.Text &&
                   inFile.X == now.X && inFile.Y == now.Y && BitConverter.SingleToUInt32Bits(inFile.Z) == BitConverter.SingleToUInt32Bits(now.Z),
                $"the saved file's row {_row} is {CoordinateInput.Format(inFile.X)}, {CoordinateInput.Format(inFile.Y)}, {CoordinateInput.Format(inFile.Z)}, the numbers the page showed");
        }
    }

    /// <summary>
    /// The mirror check's mod: the level's two Target Tanks dragged on the map to places in front of the player's start, one straight
    /// ahead (25 units out, the place the earlier acceptance put a tank that showed near the cockpit's crosshair) and one 25 degrees to the
    /// map's left of that (22 units out), each then given a height 2.1 units above the ground there (the terrain lookup's height, as the
    /// earlier acceptance did by hand), because a tank left at Z 0 stands under the ground. In the game's frames the two tanks are told
    /// apart by place: the one near the crosshair is the one ahead, and if the left of the map is the left of the cockpit the other stands
    /// left of it. Each drag is made with both the tank and its place on the map, zoomed so that the press lands on the tank it means and
    /// not on a neighbouring mark.
    /// </summary>
    private async Task Markers(SubViewport viewport, CompanionApp app, LevelEditorPage page, string label, string mods)
    {
        LevelMap map = page.Map;
        LevelEditorModel model = page.Model!;
        ObjectRow? start = model.Rows().Where(row => row.Kind == "start").OrderBy(row => row.Index).FirstOrDefault();
        Report(start is not null, $"the player's start is row {start?.Index} at {start?.Position.X}, {start?.Position.Y}, {start?.Position.Z}");
        if (start is null) return;
        List<ObjectRow> tanks = [.. model.Rows().Where(row => row.Kind == "unit" && row.Label.StartsWith("Target Tank", StringComparison.Ordinal)).OrderBy(row => row.Index).Take(2)];
        Report(tanks.Count == 2, $"two Target Tanks to place: rows {string.Join(", ", tanks.Select(row => row.Index))}");
        if (tanks.Count < 2 || model.Terrain is null) return;
        double startX = start.Position.X, startY = start.Position.Y;
        double ahead = Math.Atan2(_toY - startY, _toX - startX);
        (string Name, double Degrees, double Units)[] places = [("map-left of ahead", 25, 22), ("ahead", 0, 25)];
        List<string> lines =
        [
            $"level {_level}; start row {start.Index} at {startX:R}, {startY:R}, {start.Position.Z:R}; ahead = toward {_toX:R}, {_toY:R}, bearing {ahead * 180 / Math.PI:0.00} degrees on the map (X right, Y up, angles counter-clockwise)",
            "marker | row | stock x, y | placed x, y, z (as the page shows them) | ground there | map bearing from start | distance",
        ];
        Pointer pointer = new(viewport, map);
        for (int i = 0; i < 2; i++)
        {
            double angle = ahead + places[i].Degrees * Math.PI / 180;
            double targetX = startX + places[i].Units * Math.Cos(angle), targetY = startY + places[i].Units * Math.Sin(angle);
            ObjectRow tank = tanks[i];
            // Bring the tank and its place into view together, as large as will hold both.
            map.FitToLevel();
            await Settle();
            Vector2 middle = (map.ToScreen(tank.Position.X, tank.Position.Y) + map.ToScreen(targetX, targetY)) / 2;
            pointer.MoveTo(middle);
            for (int click = 0; click < 40; click++)
            {
                double scale = map.View.Scale * 1.2;
                Vector2 a = middle + (map.ToScreen(tank.Position.X, tank.Position.Y) - middle) * 1.2f, b = middle + (map.ToScreen(targetX, targetY) - middle) * 1.2f;
                if (scale > MapView.MaxScale || a.X < 40 || b.X < 40 || a.Y < 40 || b.Y < 40 || a.X > map.Size.X - 40 || b.X > map.Size.X - 40 || a.Y > map.Size.Y - 40 || b.Y > map.Size.Y - 40) break;
                pointer.Wheel(up: true);
            }
            await Settle();
            Vector2 mark = map.ToScreen(tank.Position.X, tank.Position.Y), aim = map.ToScreen(targetX, targetY);
            pointer.MoveTo(mark);
            pointer.Press();
            bool picked = page.SelectedRow == tank.Index;
            pointer.Glide(aim, MouseButtonMask.Left);
            pointer.Release();
            await Settle();
            System.Numerics.Vector3 placed = model.Row(tank.Index)!.Position;
            Report(picked && Math.Abs(placed.X - targetX) < 0.6 / map.View.Scale + 0.01 && Math.Abs(placed.Y - targetY) < 0.6 / map.View.Scale + 0.01,
                $"{places[i].Name}: row {tank.Index} dragged from {tank.Position.X:0.##}, {tank.Position.Y:0.##} to {CoordinateInput.Format(placed.X)}, {CoordinateInput.Format(placed.Y)} (wanted {targetX:0.##}, {targetY:0.##}; the pointer's pixel is {1 / map.View.Scale:0.###} unit)");
            // The height: a little above the ground where it now stands, typed as a person would (a second move, the first being the drag).
            float ground = model.Terrain.HeightAt(placed.X, placed.Y);
            string height = CoordinateInput.Format((float)Math.Round(ground - 2.1, 1));
            MoveOutcome raised = model.Move(tank.Index, CoordinateInput.Format(placed.X), CoordinateInput.Format(placed.Y), height);
            Report(raised.Result == MoveResult.Moved, $"row {tank.Index} given height {height} (the ground there is {ground:0.###}): \"{raised.Message}\"");
            placed = model.Row(tank.Index)!.Position;
            double bearing = Math.Atan2(placed.Y - startY, placed.X - startX) * 180 / Math.PI;
            lines.Add($"{places[i].Name} | {tank.Index} | {tank.Position.X:R}, {tank.Position.Y:R} | {CoordinateInput.Format(placed.X)}, {CoordinateInput.Format(placed.Y)}, {CoordinateInput.Format(placed.Z)} | {ground:R} | {bearing:0.00} degrees (ahead {ahead * 180 / Math.PI:0.00} {places[i].Degrees:+0;-0;0}) | {Math.Sqrt((placed.X - startX) * (placed.X - startX) + (placed.Y - startY) * (placed.Y - startY)):0.00}");
            await Shot(viewport, label, $"level-editor-3-marker-{i + 1}-{places[i].Name.Replace(' ', '-')}");
        }
        Report(model.Session!.Changes().Count == 2, $"the edit holds {model.Session.Changes().Count} changes");
        await SaveAndCompare(viewport, page, label, mods, 4, compare: false);
        File.WriteAllLines(Path.Combine(_output, $"markers-{label}.txt"), lines);
        GD.Print("MARKERS " + string.Join(" || ", lines));
    }

    private async Task SaveAndCompare(SubViewport viewport, LevelEditorPage page, string label, string mods, int number, bool compare = true)
    {
        page.Save.EmitSignal(BaseButton.SignalName.Pressed);
        page.SaveDialog.Destination.Text = mods;
        page.SaveDialog.Destination.EmitSignal(LineEdit.SignalName.TextChanged, mods);
        await Settle();
        Report(page.SaveDialog.Problem.Length == 0, $"the save dialog is ready: \"{page.SaveDialog.ModName.Text}\" / {page.SaveDialog.Id.Text}");
        await Shot(viewport, label, $"level-editor-{number}-save-as-mod");
        page.SaveDialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        page.SaveDialog.Hide();
        await Settle();
        string world = Path.Combine(mods, page.SaveDialog.Id.Text, "data", "worlds", $"world{_level:D3}.wrd");
        string manifest = Path.Combine(mods, page.SaveDialog.Id.Text, "mod.json");
        if (File.Exists(world))
        {
            byte[] bytes = File.ReadAllBytes(world);
            string hash = Convert.ToHexStringLower(SHA256.HashData(bytes));
            if (compare) Report(hash == _expected, $"{world}: {bytes.Length:N0} bytes, SHA-256 {hash}{(hash == _expected ? " = the Toolkit pipeline's" : $", expected {_expected}")}");
            else GD.Print($"ACCEPTANCE info {world}: {bytes.Length:N0} bytes, SHA-256 {hash}");
            Report(File.Exists(manifest), $"mod.json written: {File.Exists(manifest)}");
        }
        else
        {
            Report(false, $"no world file was written at {world}: \"{page.SavedText}\"");
        }
        await Shot(viewport, label, $"level-editor-{number + 1}-saved");
    }

    private async Task Shot(SubViewport viewport, string size, string name)
    {
        await Settle();
        Image image = viewport.GetTexture().GetImage();
        string path = Path.Combine(_output, $"{size}-{++_shots:D2}-{name}.png");
        Error saved = image.SavePng(path);
        if (saved != Error.Ok) throw new IOException($"Could not save {path}: {saved}");
        GD.Print($"CAPTURE {path}");
    }

    private async Task Settle()
    {
        for (int frame = 0; frame < 4; frame++) await ToSignal(this, SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
    }
}
