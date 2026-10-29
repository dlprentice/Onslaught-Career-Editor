// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using System.Security.Cryptography;
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Draws the Level editor against a Steam-shaped game folder and runs the editor's acceptance on it, in one of four modes. Run on a
/// GPU output (godot-offscreen): <c>--script res://Development/LevelEditorCapture.cs -- --output=DIR --fixture=ANY_FILE --steam-root=DIR
/// [--mode=drag|typed|markers|scripts] [--sizes=1920x1080] [--level=100] [--row=12] [--expect-sha256=HEX] [--to=276.49,265.07]</c>.
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
            if (_output.Length == 0 || _steamRoot.Length == 0 || !Directory.Exists(_steamRoot) || _mode is not ("drag" or "typed" or "markers" or "scripts"))
            {
                GD.PrintErr("--output=DIR and --steam-root=DIR (a Steam-shaped folder holding the game) are required; --mode is drag, typed, markers or scripts.");
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
