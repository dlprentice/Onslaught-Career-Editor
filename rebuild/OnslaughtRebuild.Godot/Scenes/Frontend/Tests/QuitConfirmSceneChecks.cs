// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Actual native Quit page and integrated frontend versus the retained
/// 5390cb11 dialog. Its already-validated production Main Menu is the shared
/// backdrop; no alternate backdrop or retail capture is invented here.
/// Pixel checks require an explicitly supplied fresh directory and the
/// caller's isolated display. Headless checks do not assert rendered pixels.
/// </summary>
public sealed partial class QuitConfirmSceneChecks : Node
{
    private const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
    private static readonly string[] Required = ["production_assets", "frames_and_host", "hit_bounds_and_navigation", "authored_overrides", "read_only_and_ownership"];
    private readonly List<string> _completed = [];
    private readonly List<object> _pixels = [];
    private readonly Dictionary<string, int> _counts = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> _inputHashes = new(StringComparer.Ordinal);
    private int _checks, _samples;
    private string _group = Required[0];
    private string? _directory;
    private bool _finished;

    public override async void _Ready()
    {
        List<SubViewport> views = [];
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(!Engine.IsEditorHint() && args.Contains("--skipfmv", StringComparer.Ordinal), "Focused runtime checks require --skipfmv.");
            const string prefix = "--quit-render-dir=";
            string[] outputArguments = args.Where(value => value.StartsWith(prefix, StringComparison.Ordinal)).ToArray();
            Check(outputArguments.Length <= 1, "Only one explicit capture owner is accepted.");
            _directory = outputArguments.SingleOrDefault()?[prefix.Length..];
            if (_directory is not null)
            {
                RequireOwnedDirectory(_directory);
                Check(DisplayServer.GetName() != "headless", "Pixels require the caller's isolated display.");
            }
            else Check(DisplayServer.GetName() == "headless", "An unrecorded rendered run is outside this harness.");
            GetTree().CreateTimer(120d).Timeout += () =>
            {
                if (_finished) return;
                Report("Quit comparison did not complete every required group before its bounded timeout.");
                GetTree().Quit(1);
            };
            Input.MouseModeEnum pointer = Input.MouseMode;
            RecordInputs();
            SubViewport nativeView = MakeViewport(), referenceView = MakeViewport(), hostView = MakeViewport();
            views.AddRange([nativeView, referenceView, hostView]);
            Control nativeStage = MakeStage(nativeView), referenceStage = MakeStage(referenceView);
            Control nativeBackdrop = MainMenu(nativeStage), referenceBackdrop = MainMenu(referenceStage);
            Control page = GD.Load<PackedScene>("res://Scenes/Frontend/QuitConfirm.tscn").Instantiate<Control>();
            foreach (string name in new[] { "Panel", "BorderTop", "BorderBottom", "BorderLeft", "BorderRight", "Prompt", "Yes/Highlight", "Yes/Label", "No/Highlight", "No/Label" })
                Check(page.GetNodeOrNull<Control>("Dialog/" + name) is not null, "Authored production draw pass exists before Ready: " + name);
            Control dialog = page.GetNode<Control>("Dialog");
            Check(dialog.Position == new Vector2(110, 170) && dialog.Size == new Vector2(420, 160), "Original authored Dialog origin and size are retained.");
            nativeStage.AddChild(page);
            Control referencePage = GD.Load<PackedScene>("res://Scenes/Frontend/Tests/QuitConfirmReference.tscn").Instantiate<Control>();
            QuitConfirmReference reference = referencePage.GetNode<QuitConfirmReference>("Dialog");
            reference.Initialize(); referenceStage.AddChild(referencePage);
            RetailFrontendFlow host = RetailFrontendFlow.InstantiateScene(); host.Initialize([]); hostView.AddChild(host);
            host.SetMouseCursorDesignPositionForCapture(new Vector2(-100f, -100f));
            host.SetProcess(false); host.SetProcessInput(false);
            host.ConfirmForSmoke(); EnterQuit(host);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(page.Get("_assets_configured").AsBool() && page.Get("_error").AsString() == "", "Production recipes admit before presentation.");
            Check(Selection(page) == 0 && State(host).SelectedQuitConfirmIndex == 0, "Standalone and host both default to the lower No row.");
            CheckAssets(page, reference);
            using (D paths = new()) Require(page.Call("configure_assets", paths));
            CheckAssets(page, reference);
            Complete();

            _group = Required[1];
            foreach (Vector2I size in new[] { new Vector2I(640, 480), new Vector2I(1280, 720), new Vector2I(801, 601), new Vector2I(320, 240) })
            {
                foreach (SubViewport view in views) view.Size = size;
                Fit(nativeStage, size); Fit(referenceStage, size); host.Size = size;
                for (int selected = 0; selected <= 1; selected++)
                {
                    SetFrame(page, reference, host, nativeBackdrop, referenceBackdrop, selected, _samples * .427d, _samples * .071d);
                    await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                    CheckGeometry(page, reference, selected);
                    CheckGeometry(host.GetNode<Control>("Stage/QuitConfirm"), reference, selected);
                    Check(!nativeBackdrop.GetNode<CanvasItem>("Reflection").Visible && !referenceBackdrop.GetNode<CanvasItem>("Reflection").Visible
                        && !host.GetNode<CanvasItem>("Stage/MainMenu/Reflection").Visible, "Quit keeps the actual Main Menu backdrop and hides its reflection.");
                    if (_directory is not null) await ComparePixels(nativeView, referenceView, hostView, $"{size.X}x{size.Y}-{(selected == 0 ? "no" : "yes")}");
                    _samples++;
                }
            }
            Complete();

            _group = Required[2];
            foreach (Vector2I size in new[] { new Vector2I(640, 480), new Vector2I(1280, 720), new Vector2I(801, 601), new Vector2I(320, 240), new Vector2I(1024, 768) })
            {
                foreach (SubViewport view in views) view.Size = size;
                Fit(nativeStage, size); Fit(referenceStage, size); host.Size = size;
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                CheckHitBoundaries(page, host, size);
            }
            foreach (SubViewport view in views) view.Size = new Vector2I(640, 480);
            Fit(nativeStage, new(640, 480)); Fit(referenceStage, new(640, 480)); host.Size = new(640, 480);
            CheckNavigation(host);
            Complete();

            _group = Required[3];
            foreach (SubViewport view in views) view.Size = new Vector2I(801, 601);
            Fit(nativeStage, new(801, 601)); Fit(referenceStage, new(801, 601)); host.Size = new(801, 601);
            Control hostDialog = host.GetNode<Control>("Stage/QuitConfirm/Dialog");
            for (int edit = 0; edit < 4; edit++)
            {
                Vector2 position = edit == 0 ? new(113.25f, 167.5f) : new(110f, 170f);
                Vector2 size = edit == 1 ? new(431.5f, 153.25f) : new(420f, 160f);
                float rotation = edit == 2 ? .03125f : 0f;
                Vector2 scale = edit == 3 ? new(.9375f, 1.0625f) : Vector2.One;
                foreach (Control target in new[] { dialog, hostDialog, reference })
                {
                    target.Position = position; target.Size = size; target.Rotation = rotation; target.Scale = scale;
                }
                SetFrame(page, reference, host, nativeBackdrop, referenceBackdrop, edit & 1, 3.75d, .427d);
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                Check(dialog.Position == position && dialog.Size == size && dialog.Rotation == rotation && dialog.Scale == scale,
                    "Frame updates retain authored dialog geometry.");
                CheckGeometry(page, reference, edit & 1);
                CheckGeometry(host.GetNode<Control>("Stage/QuitConfirm"), reference, edit & 1);
                if (_directory is not null) await ComparePixels(nativeView, referenceView, hostView, "authored-dialog-" + edit);
                _samples++;
            }
            Complete();

            _group = Required[4];
            using (D detached = page.Call("view_snapshot").AsGodotDictionary()) detached["selected_index"] = 99;
            Check(Selection(page) == 1, "View snapshots are detached from production selection.");
            foreach (Control owner in new[] { page, host.GetNode<Control>("Stage/QuitConfirm") })
            {
                Check(!owner.IsProcessing() && !owner.IsProcessingInput() && !owner.IsProcessingUnhandledInput(), "Native dialog owns no clock or input.");
                foreach (Node node in owner.FindChildren("*", "Control", true, false))
                    Check(!node.IsProcessing() && !node.IsProcessingInput() && !node.IsProcessingUnhandledInput(), "Native draw passes do not acquire clocks/input.");
                Check(owner.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0 && owner.FindChildren("*", "Node3D", true, false).Count == 0,
                    "Dialog has no audio players or gameplay world.");
            }
            Check(Input.MouseMode == pointer, "Synthetic callbacks never acquire the pointer.");
            foreach ((string path, string before) in _inputHashes) Check(Hash(path) == before, "Prepared input unchanged: " + path);
            Complete();
            Check(_completed.SequenceEqual(Required) && Required.All(group => _counts.GetValueOrDefault(group) > 0), "All five groups completed.");
            Check(_samples == 12 && _pixels.Count == (_directory is null ? 0 : 24), "Every headless/rendered state completed without a partial pixel claim.");
            foreach (SubViewport view in views) view.QueueFree(); views.Clear();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Report(null); GetTree().Quit(0);
        }
        catch (Exception error)
        {
            foreach (SubViewport view in views) view.QueueFree();
            Report(error.Message); GD.PushError(error.ToString()); GetTree().Quit(1);
        }
    }

    private void CheckAssets(Control page, QuitConfirmReference reference)
    {
        SameTexture(page.GetNode("Dialog/Panel").Get("texture").As<Texture2D>(), reference.Blank, "FET2_BLANK");
        foreach ((string name, Texture2D texture, int[] widths) in new[] { ("body_font", reference.BodyFont, reference.BodyWidths), ("choice_font", reference.ChoiceFont, reference.ChoiceWidths) })
        {
            using Variant value = page.Get(name);
            GodotObject font = value.AsGodotObject();
            SameTexture(font.Get("page").As<Texture2D>(), texture, name);
            Check(font.Call("glyph_widths").AsInt32Array().SequenceEqual(widths), "Every original 256-slot glyph width: " + name);
        }
    }
    private void CheckGeometry(Control page, QuitConfirmReference reference, int selected)
    {
        Check(Selection(page) == selected, "The one supplied selection fact drives the actual page.");
        Control dialog = page.GetNode<Control>("Dialog");
        Check(dialog.GetGlobalTransformWithCanvas() == reference.GetGlobalTransformWithCanvas(), "Exact authored Dialog canvas transform.");
        Rect2 box = new(RetailFeMessBox.QuitLeft, RetailFeMessBox.BoxTop, RetailFeMessBox.QuitWidth, RetailFeMessBox.ReconstructionHeight);
        float w = RetailFeMessBox.BoxLineWidth;
        foreach ((string name, Rect2 expected) in new[] { ("Panel", box), ("BorderTop", new Rect2(box.Position.X, box.Position.Y, box.Size.X, w)),
            ("BorderBottom", new Rect2(box.Position.X, box.End.Y - w, box.Size.X, w)), ("BorderLeft", new Rect2(box.Position.X, box.Position.Y, w, box.Size.Y)),
            ("BorderRight", new Rect2(box.End.X - w, box.Position.Y, w, box.Size.Y)) })
            Check(page.GetNode("Dialog/" + name).Call("drawing_rect").AsRect2() == expected, "Original panel/edge geometry: " + name);
        foreach ((string path, string text, Vector2 origin) in new[] { ("Prompt", QuitConfirmReference.Prompt, reference.PromptOrigin),
            ("Yes/Label", RetailFeMessBox.YesLabel, reference.ChoiceOrigin(1)), ("No/Label", RetailFeMessBox.NoLabel, reference.ChoiceOrigin(0)) })
        {
            Node label = page.GetNode("Dialog/" + path);
            Check(label.Call("displayed_units").AsInt32Array().SequenceEqual(text.Select(character => (int)character)), "Original prompt/choice UTF-16: " + path);
            Check(label.Call("drawing_origin").AsVector2() == origin, "Exact font-measured draw origin: " + path);
        }
        foreach (string name in new[] { "Panel", "BorderTop", "BorderBottom", "BorderLeft", "BorderRight", "Prompt", "Yes/Highlight", "Yes/Label", "No/Highlight", "No/Label" })
        {
            Control pass = page.GetNode<Control>("Dialog/" + name);
            Check(pass.Get("source_rect").AsRect2() == reference.SourceRect && pass.Call("source_transform").AsTransform2D() == reference.SourceTransform(), "Exact retained source frame: " + name);
            Check(pass.GetGlobalTransformWithCanvas() == reference.GetGlobalTransformWithCanvas(), "Each pass retains the old single-dialog canvas frame: " + name);
        }
        foreach ((string name, int index) in new[] { ("Yes", 1), ("No", 0) })
        {
            Node highlight = page.GetNode("Dialog/" + name + "/Highlight");
            Check(highlight.Call("is_selected").AsBool() == (selected == index), "Only the selected row paints its highlight.");
            Check(highlight.Call("drawing_rect").AsRect2() == reference.HighlightRect(index), "Highlight uses original measured label width and padding.");
        }
    }
    private void CheckHitBoundaries(Control page, RetailFrontendFlow host, Vector2I size)
    {
        float[] xs = [MathF.BitDecrement(120f), 120f, 320f, MathF.BitDecrement(520f), 520f];
        float[] ys = [MathF.BitDecrement(194f), 194f, MathF.BitDecrement(226f), 226f, MathF.BitDecrement(258f), 258f];
        (float scale, Vector2 offset) = DesignTransform(size);
        foreach (float x in xs) foreach (float y in ys)
        {
            Vector2 design = new(x, y);
            Check(page.Call("hit_test", design).AsInt32() == QuitConfirmReference.HitTest(design), $"Exact design-space half-open hit at {size}/{design}.");
            Vector2 canvas = new Vector2(x, y) * scale + offset;
            // The original host divided the viewport point before its static
            // Rect2.HasPoint test. Native presentation must receive that same
            // design point without an extra canvas/inverse-canvas round trip.
            Vector2 originalDesign = (canvas - offset) / scale;
            int expected = QuitConfirmReference.HitTest(originalDesign);
            Check(page.Call("hit_test", originalDesign).AsInt32() == expected, $"Standalone full-width half-open hit at {size}/{canvas}.");
            int actualHost = (int)typeof(RetailFrontendFlow).GetMethod("QuitConfirmIndexAt", Private)!.Invoke(host, [originalDesign])!;
            Check(actualHost == expected, $"Host full-width half-open hit at {size}/{canvas}.");
        }
        if (size == new Vector2I(1024, 768) || size == new Vector2I(801, 601))
        {
            // Concrete original/new-bridge falsifier found during this port:
            // (832,400) -> design (520,250), outside the full-width No row.
            Vector2 point = size.X == 1024 ? new(832f, 400f) : new(650.8125f, 313.015625f);
            Check((point - offset) / scale == new Vector2(520f, 250f), $"Exact retained {size} pointer conversion.");
            int selected = State(host).SelectedQuitConfirmIndex;
            using var input = new InputEventMouseButton { Position = point, Pressed = true, ButtonIndex = MouseButton.Left };
            host._Input(input);
            Check(host.CurrentScreen == RetailFrontendScreen.QuitConfirm && State(host).SelectedQuitConfirmIndex == selected,
                $"The actual pointer route excludes the {size} right boundary.");
        }
    }
    private void CheckNavigation(RetailFrontendFlow host)
    {
        List<string> effects = [];
        int exits = 0;
        void Audio(RetailFrontendAudioCue cue) => effects.Add("audio:" + cue);
        void Cursor(RetailFrontendCursorMode mode) => effects.Add("cursor:" + mode);
        void Exit() { exits++; effects.Add("exit"); }
        host.AudioCueRequested += Audio; host.CursorModeRequested += Cursor; host.ExitRequested += Exit;
        try
        {
            InputKey(host, Key.Escape);
            Check(host.CurrentScreen == RetailFrontendScreen.MainMenu && exits == 0 && effects.SequenceEqual(new[] { "audio:Back", "cursor:Custom" }), "Cancel returns Main Menu with the original callback order.");
            effects.Clear(); EnterQuit(host);
            Check(State(host).SelectedQuitConfirmIndex == 0 && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "Each entry restores No after the selection and cursor callbacks.");
            effects.Clear(); InputKey(host, Key.Enter);
            Check(host.CurrentScreen == RetailFrontendScreen.MainMenu && exits == 0 && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "Confirming No returns Main Menu without requesting exit.");
            effects.Clear(); EnterQuit(host); effects.Clear();
            InputKey(host, Key.Up); InputKey(host, Key.Up);
            Check(State(host).SelectedQuitConfirmIndex == 1 && effects.SequenceEqual(new[] { "audio:Move" }), "Up selects Yes once and repeated Up emits no extra move.");
            effects.Clear(); InputKey(host, Key.Down);
            Check(State(host).SelectedQuitConfirmIndex == 0 && effects.SequenceEqual(new[] { "audio:Move" }), "Down selects the lower No row.");
            effects.Clear();
            using (var outside = new InputEventMouseButton { Position = new(520f, 226f), Pressed = true, ButtonIndex = MouseButton.Left }) host._Input(outside);
            Check(host.CurrentScreen == RetailFrontendScreen.QuitConfirm && effects.Count == 0, "The excluded right boundary neither confirms nor emits audio.");
            using (var no = new InputEventMouseButton { Position = new(120f, 226f), Pressed = true, ButtonIndex = MouseButton.Left }) host._Input(no);
            Check(host.CurrentScreen == RetailFrontendScreen.MainMenu && exits == 0 && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "Full-width No-row pointer confirmation uses the production input route.");
            effects.Clear(); EnterQuit(host); effects.Clear();
            using (var yes = new InputEventMouseButton { Position = new(120f, 194f), Pressed = true, ButtonIndex = MouseButton.Left }) host._Input(yes);
            Check(exits == 1 && host.CurrentScreen == RetailFrontendScreen.QuitConfirm && effects.SequenceEqual(new[] { "audio:Move", "audio:Select", "exit" }), "Yes emits one ordered exit request; the harness never attaches a quit callback.");
            Check(GetTree().CurrentScene == this, "The actual scene remains alive after the exit signal.");
        }
        finally { host.AudioCueRequested -= Audio; host.CursorModeRequested -= Cursor; host.ExitRequested -= Exit; }
    }
    private static void InputKey(RetailFrontendFlow host, Key key)
    {
        using var input = new InputEventKey { Pressed = true, Keycode = key, PhysicalKeycode = key };
        host._Input(input);
    }
    private void EnterQuit(RetailFrontendFlow host)
    {
        Check(host.CurrentScreen == RetailFrontendScreen.MainMenu, "Quit is entered from the actual Main Menu.");
        SetField(host, "_mainTransitionTime", 0); SetField(host, "_mainTransitionCount", 0);
        host.SelectMainIndexForCapture(6); host.ConfirmForSmoke();
        Check(host.CurrentScreen == RetailFrontendScreen.QuitConfirm, "The original session opens Quit confirmation.");
    }
    private static GdFrontendSession State(RetailFrontendFlow host) => (GdFrontendSession)typeof(RetailFrontendFlow).GetField("_session", Private)!.GetValue(host)!;
    private static void SetField(RetailFrontendFlow host, string name, object value) => typeof(RetailFrontendFlow).GetField(name, Private)!.SetValue(host, value);
    private static int Selection(Control page)
    {
        using Variant value = page.Call("view_snapshot"); using D state = value.AsGodotDictionary();
        return state["selected_index"].AsInt32();
    }
    private static void SetFrame(Control page, QuitConfirmReference reference, RetailFrontendFlow host, Control nativeBackdrop, Control referenceBackdrop,
        int selected, double animation, double background)
    {
        using D facts = new() { ["selected_index"] = selected };
        Require(page.Call("set_frame", facts)); reference.SetFrame(selected);
        State(host).SelectQuitConfirmIndex(selected);
        SetField(host, "_mainTransitionTime", 0); SetField(host, "_mainTransitionCount", 0);
        SetField(host, "_animationSeconds", animation); SetField(host, "_feBackSeconds", background);
        host.SelectMainIndexForCapture(6); // Also queues the host's frame while Quit owns selection.
        using Variant snapshot = host.GetNode("Stage/MainMenu").Call("view_snapshot");
        Require(nativeBackdrop.Call("set_frame", snapshot)); Require(referenceBackdrop.Call("set_frame", snapshot));
    }
    private static void Require(Variant returned)
    {
        using (returned)
        {
            if (returned.VariantType != Variant.Type.Dictionary) throw new InvalidDataException("Native presentation returned no result.");
            using D result = returned.AsGodotDictionary();
            if (!result["ok"].AsBool()) throw new InvalidDataException(result["error"].AsString());
        }
    }
    private void SameTexture(Texture2D actual, Texture2D expected, string name)
    {
        using Image a = actual.GetImage(); using Image e = expected.GetImage();
        Check(a.GetSize() == e.GetSize() && a.GetFormat() == e.GetFormat() && a.GetData().SequenceEqual(e.GetData()), "Exact original decoded texture storage: " + name);
    }
    private async Task ComparePixels(SubViewport native, SubViewport reference, SubViewport host, string name)
    {
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image actual = native.GetTexture().GetImage(); using Image expected = reference.GetTexture().GetImage(); using Image integrated = host.GetTexture().GetImage();
        Save(actual, name + "-native.png"); Save(expected, name + "-reference.png"); Save(integrated, name + "-host.png");
        Compare(actual, expected, name, "native"); Compare(integrated, expected, name, "host");
    }
    private void Save(Image image, string name)
    {
        string path = Path.Combine(_directory!, name);
        Check(!File.Exists(path) && !Directory.Exists(path) && new FileInfo(path).LinkTarget is null && image.SavePng(path) == Error.Ok, "Fresh owned capture: " + name);
    }
    private void Compare(Image actual, Image expected, string name, string kind)
    {
        byte[] a = actual.GetData(), e = expected.GetData();
        int differences = a.Length == e.Length ? a.Where((value, index) => value != e[index]).Count() : -1;
        _pixels.Add(new { name, kind, differences, actualHash = Convert.ToHexString(SHA256.HashData(a)), expectedHash = Convert.ToHexString(SHA256.HashData(e)) });
        Check(actual.GetSize() == expected.GetSize() && actual.GetFormat() == expected.GetFormat() && differences == 0, $"{kind} {name} differs in {differences} RGBA bytes.");
    }
    private SubViewport MakeViewport()
    {
        var view = new SubViewport { Size = new(640, 480), Disable3D = true, TransparentBg = false, RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
        AddChild(view);
        var background = new ColorRect { Color = Colors.Black, MouseFilter = Control.MouseFilterEnum.Ignore };
        view.AddChild(background); background.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        return view;
    }
    private static Control MakeStage(SubViewport view)
    {
        var stage = new Control { Size = new(640, 480), MouseFilter = Control.MouseFilterEnum.Ignore };
        view.AddChild(stage); return stage;
    }
    private static Control MainMenu(Control stage)
    {
        Control menu = GD.Load<PackedScene>("res://Scenes/Frontend/MainMenu.tscn").Instantiate<Control>();
        stage.AddChild(menu); return menu;
    }
    private static (float Scale, Vector2 Offset) DesignTransform(Vector2I size)
    {
        float scale = Mathf.Min(size.X / 640f, size.Y / 480f);
        return (scale, new Vector2((size.X - (640f * scale)) * .5f, (size.Y - (480f * scale)) * .5f));
    }
    private static void Fit(Control stage, Vector2I size)
    {
        (float scale, Vector2 offset) = DesignTransform(size);
        stage.Position = offset; stage.Scale = new Vector2(scale, scale);
    }
    private void RecordInputs()
    {
        foreach (string name in new[] { "forseti-writing-large", "fe-arrow", "title-text-box", "title-logo", "reflection-map", "title-bracket-01", "title-bracket-02", "symbol-bracket-01", "symbol-bracket-02",
            "Flags/flag-uk", "Flags/flag-fr", "Flags/flag-gr", "Flags/flag-it", "Flags/flag-sp", "Icons/new-game", "Icons/continue-game", "Icons/load-game", "Icons/multiplayer", "Icons/goodies", "Icons/options", "Icons/quit" })
            Record("res://Assets/Frontend/" + name + ".texture.aya");
        foreach (string path in new[] { "res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya", "res://Assets/PauseMenu/blank.texture.aya", "res://Assets/Frontend/english.json", "res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb" }) Record(path);
    }
    private static void RequireOwnedDirectory(string directory)
    {
        string owner = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
        if (!Path.IsPathFullyQualified(directory) || Path.GetFullPath(directory) != directory || !directory.StartsWith(owner, StringComparison.Ordinal)
            || directory.Contains('\\') || !Directory.Exists(directory) || Directory.EnumerateFileSystemEntries(directory).Any())
            throw new IOException("Render output must be a fresh empty owned directory.");
        for (DirectoryInfo? current = new(directory); current is not null; current = current.Parent)
            if (current.LinkTarget is not null) throw new IOException("Render output ancestry must not contain symlinks.");
    }
    private void Record(string path) => _inputHashes.Add(path, Hash(path));
    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(Godot.FileAccess.GetFileAsBytes(path)));
    private void Check(bool condition, string message)
    {
        _checks++; _counts[_group] = _counts.GetValueOrDefault(_group) + 1;
        if (!condition) throw new InvalidOperationException(message);
    }
    private void Complete() => _completed.Add(_group);
    private void Report(string? error)
    {
        if (_finished) return;
        _finished = true;
        GD.Print("QUIT_CONFIRM_SCENE_CHECKS: " + JsonSerializer.Serialize(new { schema = 1, checks = _checks, samples = _samples,
            completed = _completed, counts = _counts, rendered = _directory is not null, pixels = _pixels,
            reference_revision = "5390cb11", input_sha256 = _inputHashes, failure_count = error is null ? 0 : 1, error }));
    }
}
