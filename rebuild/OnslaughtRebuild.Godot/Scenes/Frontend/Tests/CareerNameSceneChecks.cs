// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Production Career Name scene and live host against the retained 14f6f72b
/// renderer. The sole save read is the explicit tracked gold fixture, parsed
/// through its verified reader; no discovery, persistence or personal save I/O.
/// Headless checks make no pixel claim. Optional captures require the caller's
/// isolated display and a fresh owned directory. No physical input or game runs.
/// </summary>
public sealed partial class CareerNameSceneChecks : Node
{
    private const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
    private const string Fixture = "res://../../tests_shared/fixtures/gold_career_save.bin";
    private static readonly string[] Required = ["production_assets_and_glyphs", "frames_and_host", "hit_bounds_and_navigation", "authored_sections", "read_only_and_ownership"];
    private static readonly string[] DrawPasses = ["Decoration/Shadow", "Decoration/Body", "Header/Panel", "Header/Title",
        "List/Border", "List/Fill", "List/Guide", "List/Divider", "List/ThumbTop", "List/ThumbBottom", "List/ThumbLeft", "List/ThumbRight",
        "Name/Border", "Name/Fill", "Name/Highlight", "Name/Label", "Navigation/Back", "Navigation/Forward"];
    private readonly List<string> _completed = [];
    private readonly List<object> _pixels = [];
    private readonly List<object> _refusalBoundaries = [];
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
            string[] arguments = OS.GetCmdlineUserArgs();
            Check(!Engine.IsEditorHint() && arguments.Contains("--skipfmv", StringComparer.Ordinal), "Focused runtime checks require --skipfmv.");
            const string prefix = "--career-render-dir=";
            string[] supplied = arguments.Where(value => value.StartsWith(prefix, StringComparison.Ordinal)).ToArray();
            Check(supplied.Length <= 1, "Only one explicit render directory is admitted.");
            _directory = supplied.SingleOrDefault()?[prefix.Length..];
            if (_directory is not null)
            {
                RequireOwnedDirectory(_directory);
                Check(DisplayServer.GetName() != "headless", "Pixels require the caller's isolated rendered display.");
            }
            else Check(DisplayServer.GetName() == "headless", "Unrecorded visible runs are outside this harness.");
            GetTree().CreateTimer(120d).Timeout += () =>
            {
                if (_finished) return;
                Report("Career comparison did not complete every required group before its bounded timeout.");
                GetTree().Quit(1);
            };
            Input.MouseModeEnum pointer = Input.MouseMode;
            RecordInputs();
            byte[] fixtureBytes = Godot.FileAccess.GetFileAsBytes(Fixture);
            RetailCareerSave save = RetailCareerSaveCodec.Read(fixtureBytes);
            string[] names = ["BEA 1", "Slot ¡¿á’–", "Raw\0\ud800\udc00\ufffd", "FOUR", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Hidden twelve", "Overflow selected"];
            var descriptors = names.Select((name, index) => new RetailCareerDescriptor(index + 1, name, save)).ToArray();
            SubViewport nativeView = MakeViewport(), referenceView = MakeViewport(), hostView = MakeViewport();
            views.AddRange([nativeView, referenceView, hostView]);
            Control nativeStage = MakeStage(nativeView), referenceStage = MakeStage(referenceView);
            Control page = GD.Load<PackedScene>("res://Scenes/Frontend/CareerName.tscn").Instantiate<Control>();
            foreach (string section in CareerNameReference.Sections.Keys)
                Check(page.GetNodeOrNull<Control>(section) is not null, "Production authored section exists before Play: " + section);
            nativeStage.AddChild(page);
            CareerNameReference reference = GD.Load<PackedScene>("res://Scenes/Frontend/Tests/CareerNameReference.tscn").Instantiate<CareerNameReference>();
            referenceStage.AddChild(reference);
            var hosts = new Dictionary<int, RetailFrontendFlow>();
            RetailCareerDescriptor[] offscreenNull = descriptors.Take(11).Append(new RetailCareerDescriptor(12, null!, save)).ToArray();
            foreach (int count in new[] { 0, 1, 11, 12, 13 })
            {
                RetailFrontendFlow host = RetailFrontendFlow.InstantiateScene();
                host.Initialize(count == 12 ? offscreenNull : descriptors.Take(count).ToArray()); hostView.AddChild(host);
                host.SetProcess(false); host.SetProcessInput(false);
                host.SetMouseCursorDesignPositionForCapture(new Vector2(-100f, -100f));
                host.ConfirmForSmoke(); host.Visible = false; hosts.Add(count, host);
            }
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            using (D paths = new()) using (D fonts = new()) using (A frames = new()) Require(page.Call("configure_assets", paths, fonts, frames));
            CheckAssetsAndGlyphs(page, reference, hosts[11]); Complete();

            _group = Required[1];
            async Task Sample(RetailFrontendFlow host, Vector2I size, string label, double seconds)
            {
                foreach (RetailFrontendFlow item in hosts.Values) item.Visible = ReferenceEquals(item, host);
                foreach (SubViewport viewport in views) viewport.Size = size;
                Fit(nativeStage, size); Fit(referenceStage, size);
                foreach (RetailFrontendFlow item in hosts.Values) item.Size = size;
                Sync(page, reference, host, seconds);
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                CheckFrame(page, reference, State(host));
                CheckFrame(host.GetNode<Control>("Stage/CareerName"), reference, State(host));
                if (_directory is not null) await ComparePixels(nativeView, referenceView, hostView, label);
                _samples++;
            }
            foreach (Vector2I size in new[] { new Vector2I(640, 480), new Vector2I(1280, 720), new Vector2I(801, 601), new Vector2I(320, 240) })
            {
                Enter(hosts[0], false);
                await Sample(hosts[0], size, $"{size.X}x{size.Y}-new-empty", _samples * .731d);
                Enter(hosts[11], true); Check(State(hosts[11]).SelectCareerIndex(10), "Last visible career can be selected.");
                await Sample(hosts[11], size, $"{size.X}x{size.Y}-load-eleven", _samples * .731d);
            }
            Enter(hosts[1], true); State(hosts[1]).SelectCareerIndex(0);
            await Sample(hosts[1], new(640, 480), "single-career", 19.07d);
            Enter(hosts[13], true); State(hosts[13]).SelectCareerIndex(12);
            await Sample(hosts[13], new(640, 480), "overflow-selected", 1d);
            Enter(hosts[11], true); State(hosts[11]).SelectCareerIndex(2);
            await Sample(hosts[11], new(640, 480), "raw-utf16-selected", .083333333d);
            Enter(hosts[13], false); Character(hosts[13], '¡'); Character(hosts[13], '¿'); Character(hosts[13], 'é');
            await Sample(hosts[13], new(640, 480), "edited-name-fresh-off", .5d);
            Enter(hosts[12], false);
            await Sample(hosts[12], new(640, 480), "offscreen-null-row", .75d);
            Check(State(hosts[12]).CareerNames[11] is null, "The host preserves an offscreen null row without normalizing it.");
            CheckNullRefusals(page, reference, hosts[12], offscreenNull);
            Complete();

            _group = Required[2];
            CheckHitBounds(page, hosts[11], nativeStage, views);
            CheckNavigation(hosts[0], hosts[11], descriptors.Take(11).ToArray(), save);
            Complete();

            _group = Required[3];
            Enter(hosts[11], true); State(hosts[11]).SelectCareerIndex(5);
            int edit = 0;
            foreach (string section in new[] { "Header", "List", "Name" })
            {
                Control authored = page.GetNode<Control>(section), old = reference.GetNode<Control>(section);
                Control integrated = hosts[11].GetNode<Control>("Stage/CareerName/" + section);
                Vector2 position = authored.Position, extent = authored.Size, scale = authored.Scale; float rotation = authored.Rotation;
                foreach (Control component in new[] { authored, old, integrated })
                {
                    component.Position = position + new Vector2(3.25f + edit, -2.5f);
                    component.Size = extent + new Vector2(7f, 3f);
                    component.Scale = new Vector2(.99f, 1.01f);
                    component.Rotation = .012f;
                }
                await Sample(hosts[11], new(801, 601), "authored-" + section.ToLowerInvariant(), .3d + edit);
                Check(authored.Position == old.Position && authored.Size == old.Size && authored.Scale == old.Scale && authored.Rotation == old.Rotation,
                    "Frame submission preserves normal authored transform/size edits: " + section);
                foreach (Control component in new[] { authored, old, integrated })
                { component.Position = position; component.Size = extent; component.Scale = scale; component.Rotation = rotation; }
                edit++;
            }
            Complete();

            _group = Required[4];
            using (D snapshot = page.Call("view_snapshot").AsGodotDictionary())
            {
                snapshot["selected_career_index"] = 99; snapshot["game_name"] = new[] { 88 };
                using A rows = snapshot["career_names"].AsGodotArray(); rows[0] = new[] { 89 };
            }
            CheckSnapshot(page, State(hosts[11]));
            foreach (Control component in new[] { page, hosts[11].GetNode<Control>("Stage/CareerName") })
            {
                foreach (Node owner in component.FindChildren("*", "Control", true, false).Prepend(component))
                    Check(!owner.IsProcessing() && !owner.IsProcessingInput() && !owner.IsProcessingUnhandledInput(), "Production Career controls own no clock or input.");
                Check(component.FindChildren("*Cursor*", "", true, false).Count == 0, "No visual name cursor is invented.");
                Check(component.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0 && component.FindChildren("*", "Node3D", true, false).Count == 0,
                    "Career presentation creates no audio player or game world.");
            }
            Check(Input.MouseMode == pointer, "Synthetic callbacks leave pointer mode unchanged.");
            Check(save.ContainerBytes.SequenceEqual(fixtureBytes), "Verified save owner retains every original byte.");
            foreach ((string path, string before) in _inputHashes) Check(Hash(path) == before, "Input bytes unchanged: " + path);
            Complete();
            Check(_completed.SequenceEqual(Required) && Required.All(group => _counts.GetValueOrDefault(group) > 0), "All five required groups completed.");
            Check(_samples == 16 && _pixels.Count == (_directory is null ? 0 : 32) && _refusalBoundaries.Count == 2,
                "All bounded states and refusal observations completed; headless cannot claim pixels.");
            foreach (SubViewport viewport in views) viewport.QueueFree(); views.Clear();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Report(null); GetTree().Quit(0);
        }
        catch (Exception error)
        {
            foreach (SubViewport viewport in views) viewport.QueueFree();
            GD.PushError(error.ToString()); Report(error.ToString()); GetTree().Quit(1);
        }
    }

    private void CheckAssetsAndGlyphs(Control page, CareerNameReference reference, RetailFrontendFlow host)
    {
        foreach ((string name, Texture2D expected, int[] widths) in new[] { ("body_font", reference.BodyFont, reference.BodyWidths), ("title_font", reference.TitleFont, reference.TitleWidths) })
        {
            using Variant returned = page.Get(name); Resource font = returned.As<Resource>();
            using Variant textureValue = font.Get("page"); SameTexture(textureValue.As<Texture2D>(), expected, name);
            Check(font.Call("glyph_widths").AsInt32Array().SequenceEqual(widths), "Every original atlas glyph width matches: " + name);
        }
        SameTexture(page.GetNode("Decoration/Body").Get("texture").As<Texture2D>(), reference.Bracket, "level-bracket-01");
        SameTexture(page.GetNode("Navigation/Forward").Get("texture").As<Texture2D>(), reference.Arrow, "fe-arrow");
        var texts = new List<string> { "", "BEA 1", "¡¿", "áàâäçéèêëíìîïóòôöœñúùûüÁÀÄÂÇÉÈÍÌÑÓÒÖÜÚÙŒ¡¿©®™«»ºª\u001fßÊËÎÏÔÛ┐┌", "’–", "$@[\\]^_{|}~\u007f", "A\0B\ud800\udc00\ufffd\uffff" };
        texts.AddRange(Enumerable.Range(0, 288).Select(code => new string((char)code, 1)));
        texts.Add(new string(Enumerable.Range(0, 65536).Select(code => (char)code).ToArray()));
        MethodInfo extent = typeof(RetailFrontendFlow).GetMethod("MeasureGameNameExtent", Private)!;
        foreach (string text in texts)
        {
            int expected = reference.MeasureNameExtent(text);
            Check(page.Call("measure_name_extent", Units(text)).AsInt64() == expected, "Font22 input extent retains raw UTF-16 mapping, inverted punctuation and trailing spacing.");
            Check((int)extent.Invoke(host, [text])! == expected, "Live host routes the same exact name extent.");
        }
        using D configured = page.Call("configure_assets").AsGodotDictionary();
        Check(configured["ok"].AsBool(), "Repeat production asset configuration succeeds without a new owner.");
    }

    private void CheckFrame(Control page, CareerNameReference reference, GdFrontendSession state)
    {
        CheckSnapshot(page, state);
        foreach ((string name, Rect2 measured) in CareerNameReference.Sections)
        {
            Control part = page.GetNode<Control>(name), old = reference.GetNode<Control>(name);
            Check(part.Position == old.Position && part.Size == old.Size && part.Scale == old.Scale && part.Rotation == old.Rotation, "Original authored section frame: " + name);
            Check(part.GetGlobalTransformWithCanvas() == old.GetGlobalTransformWithCanvas(), "Actual canvas frame agrees: " + name);
        }
        foreach (string path in DrawPasses.Concat(Enumerable.Range(0, 11).Select(index => "List/Rows/Row" + index.ToString("D2"))))
        {
            Control pass = page.GetNode<Control>(path), old = reference.GetNode<Control>(path.Split('/')[0]);
            Check(pass.Get("source_rect").AsRect2() == CareerNameReference.Sections[old.Name.ToString()], "Draw pass retains original measured source rectangle: " + path);
            Check(pass.Call("source_transform").AsTransform2D() == CareerNameReference.SourceTransform(old), "Source-to-section transform agrees: " + path);
            Check(pass.GetGlobalTransformWithCanvas() == old.GetGlobalTransformWithCanvas(), "Draw pass retains original canvas grouping: " + path);
        }
        Check(page.GetNode("Header/Title").Call("drawing_origin").AsVector2() == reference.TitleOrigin, "Header title uses original centered Font22 extent.");
        Node nameLabel = page.GetNode("Name/Label"), highlight = page.GetNode("Name/Highlight");
        Check(nameLabel.Call("displayed_units").AsInt32Array().SequenceEqual(Units(state.GameName)), "Name display preserves raw UTF-16 units.");
        Check(Bits((float)nameLabel.Call("font_width").AsDouble()) == Bits(reference.NameWidth) && nameLabel.Call("drawing_origin").AsVector2() == reference.NameOrigin,
            "Name width and centered origin retain checked sum and float32 stores.");
        Check(highlight.Call("draws_content").AsBool() == state.GameNameIsFresh && highlight.Call("drawing_rect").AsRect2() == reference.HighlightRect,
            "Only a fresh name paints the original measured highlight.");
        for (int index = 0; index < 11; index++)
        {
            Node row = page.GetNode("List/Rows/Row" + index.ToString("D2"));
            bool present = index < state.CareerNames.Count;
            Check(row.Call("draws_content").AsBool() == present, "Only present rows draw, with exactly eleven authored slots.");
            Check(row.Call("drawing_origin").AsVector2() == new Vector2(132f, 137f + index * 24f), "Original row origin and pitch.");
            if (present) Check(row.Call("displayed_units").AsInt32Array().SequenceEqual(Units(state.CareerNames[index])), "Career rows preserve original order and raw text.");
            Color expected = index == state.SelectedCareerIndex ? Retail(0xff7f7f7f) : Retail(0xff404040);
            Check(row.Call("drawing_color").AsColor() == expected, "Selected-row ink is retained exactly.");
        }
        Check(page.GetNode("List/Rows").GetChildCount() == 11, "Overflow is clipped by the original row-end rule, not new UI rows.");
        foreach ((string path, Rect2 rect) in new (string, Rect2)[] { ("Header/Panel", new(191, 69, 394, 21)),
            ("List/Border", new(128, 130, 403, 272)), ("List/Fill", new(129, 131, 401, 270)), ("List/Guide", new(129, 180, 401, 1)),
            ("List/Divider", new(510, 131, 1, 270)), ("List/ThumbTop", new(515, 135, 11, 1)), ("List/ThumbBottom", new(515, 396, 11, 1)),
            ("List/ThumbLeft", new(515, 135, 1, 262)), ("List/ThumbRight", new(525, 135, 1, 262)),
            ("Name/Border", new(128, 408, 403, 44)), ("Name/Fill", new(129, 409, 401, 42)),
            ("Navigation/Back", new(36, 443, -27, 35)), ("Navigation/Forward", new(604, 437, 27, 35)) })
            Check(page.GetNode(path).Call("drawing_rect").AsRect2() == rect, "Exact original draw rectangle: " + path);
        using D background = page.GetNode("Background").Call("view_snapshot").AsGodotDictionary();
        using D snapshot = page.Call("view_snapshot").AsGodotDictionary();
        Check(background["alpha"].AsDouble() == 1d && background["frame_count"].AsInt32() == reference.BackgroundFrames.Length
            && background["frame"].AsInt32() == CareerNameReference.FeBackFrameIndex(snapshot["background_seconds"].AsDouble(), reference.BackgroundFrames.Length),
            "Settled underlay shares the exact current background phase law.");
    }

    private void CheckHitBounds(Control page, RetailFrontendFlow host, Control stage, IReadOnlyList<SubViewport> views)
    {
        Enter(host, false);
        MethodInfo target = typeof(RetailFrontendFlow).GetMethod("CareerNameTargetAt", Private)!;
        foreach (Vector2I size in new[] { new Vector2I(640, 480), new Vector2I(1280, 720), new Vector2I(801, 601), new Vector2I(320, 240) })
        {
            foreach (SubViewport view in views) view.Size = size; host.Size = size; Fit(stage, size);
            foreach (Rect2 rect in new[] { new Rect2(0, 430, 46, 48), new Rect2(595, 430, 45, 48), new Rect2(128, 408, 403, 44) })
            {
                float cx = rect.Position.X + rect.Size.X * .5f, cy = rect.Position.Y + rect.Size.Y * .5f;
                IEnumerable<Vector2> points = new[] { rect.Position.X, rect.End.X }.SelectMany(x => new[] { MathF.BitDecrement(x), x, MathF.BitIncrement(x) }).Select(x => new Vector2(x, cy))
                    .Concat(new[] { rect.Position.Y, rect.End.Y }.SelectMany(y => new[] { MathF.BitDecrement(y), y, MathF.BitIncrement(y) }).Select(y => new Vector2(cx, y)));
                foreach (Vector2 point in points)
                {
                    int expected = CareerNameReference.HitTest(point);
                    Check(page.Call("hit_test", point).AsInt32() == expected && (int)target.Invoke(host, [point])! == expected,
                        "Native and host preserve exact half-open design-space targets without a Stage roundtrip.");
                }
            }
            Check(page.Call("hit_test", new Vector2(140, 142)).AsInt32() == 0, "No clickable career-row behavior is invented.");
        }
    }

    private void CheckNavigation(RetailFrontendFlow empty, RetailFrontendFlow host, RetailCareerDescriptor[] descriptors, RetailCareerSave save)
    {
        host.Size = new(640, 480); empty.Size = new(640, 480);
        var effects = new List<string>(); RetailCareerDescriptor? selected = null; int exits = 0;
        void Audio(RetailFrontendAudioCue cue) => effects.Add("audio:" + cue);
        void Cursor(RetailFrontendCursorMode mode) => effects.Add("cursor:" + mode);
        void Selected(RetailCareerDescriptor descriptor) { selected = descriptor; effects.Add("career"); }
        void Exit() => exits++;
        host.AudioCueRequested += Audio; host.CursorModeRequested += Cursor; host.CareerSelected += Selected; host.ExitRequested += Exit;
        try
        {
            Enter(host, false); effects.Clear();
            var expected = new RetailFrontendSession(descriptors); expected.Confirm(); expected.Confirm();
            foreach (char character in new[] { 'X', '¡', '¿', 'é', '’', '–', '$', '\ud800' })
            {
                int extent = host.GetNode<Control>("Stage/CareerName").Call("measure_name_extent", Units(expected.GameName)).AsInt32();
                expected.AppendGameNameCharacter(character, extent); Character(host, character);
                CompareState(State(host), expected, "actual key character path");
            }
            string before = State(host).GameName;
            Character(host, 'Z', echo: true); Check(State(host).GameName == before, "Key echo cannot mutate the name.");
            Key(host, Godot.Key.Left); expected.MoveGameNameCursor(false); CompareState(State(host), expected, "cursor-left keeps existing invisible cursor state");
            Key(host, Godot.Key.Backspace); expected.RemoveGameNameCharacter(); CompareState(State(host), expected, "backspace removes the original indexed UTF-16 unit");
            foreach (Godot.Key key in new[] { Godot.Key.Home, Godot.Key.End, Godot.Key.Delete }) Key(host, key);
            CompareState(State(host), expected, "reserved editing keys remain inert");
            Check(effects.Count == 0, "Name editing emits no navigation/audio callback.");
            Click(host, new(531, 420)); Check(host.CurrentScreen == RetailFrontendScreen.DevSelect && effects.Count == 0, "Name-field excluded right edge does not confirm.");
            Click(host, new(128, 408));
            Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect && selected is null && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "Name-field confirmation uses the existing New route without a save handoff.");
            Enter(host, false); effects.Clear(); Click(host, new(0, 430));
            Check(host.CurrentScreen == RetailFrontendScreen.MainMenu && effects.SequenceEqual(new[] { "audio:Back", "cursor:Custom" }), "Back chevron retains ordered callbacks.");
            Enter(host, false); effects.Clear(); Key(host, Godot.Key.Escape);
            Check(host.CurrentScreen == RetailFrontendScreen.MainMenu && effects.SequenceEqual(new[] { "audio:Back", "cursor:Custom" }), "Keyboard cancel returns to Main Menu.");
            Enter(host, true); effects.Clear();
            Key(host, Godot.Key.Down); Key(host, Godot.Key.Down); Key(host, Godot.Key.Up);
            Check(State(host).SelectedCareerIndex == 0 && effects.SequenceEqual(new[] { "audio:Move", "audio:Move", "audio:Move" }), "Load mode retains bounded row keyboard selection.");
            effects.Clear(); before = State(host).GameName; Character(host, 'X'); Key(host, Godot.Key.Backspace);
            Check(State(host).GameName == before && effects.Count == 0, "Load mode never edits the injected name.");
            Click(host, new(140, 166)); Check(State(host).SelectedCareerIndex == 0 && effects.Count == 0, "List rows remain display-only for pointer input.");
            Click(host, new(595, 430));
            Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect && ReferenceEquals(selected, descriptors[0]) && ReferenceEquals(selected!.Career, save)
                && effects.SequenceEqual(new[] { "audio:Select", "career", "cursor:Custom" }), "Forward chevron hands the exact already-verified descriptor to the existing callback once.");
            Check(State(host).ConsumeSelectedCareerLoadRequest() is null && exits == 0, "Load edge is consumed once; harness never requests window quit.");
            Enter(empty, true); Key(empty, Godot.Key.Enter);
            Check(empty.CurrentScreen == RetailFrontendScreen.DevSelect && State(empty).SelectedCareerIndex == -1
                && State(empty).UnavailableSelection == RetailFrontendMenuItemKind.LoadGame, "Empty Load does not fabricate a selected save.");
        }
        finally { host.AudioCueRequested -= Audio; host.CursorModeRequested -= Cursor; host.CareerSelected -= Selected; host.ExitRequested -= Exit; }
    }

    private void CheckNullRefusals(Control page, CareerNameReference reference, RetailFrontendFlow host, RetailCareerDescriptor[] descriptors)
    {
        MethodInfo draw = typeof(CareerNameReference).GetMethod("DrawDevSelect", Private)!;
        string[] safeNames = descriptors.Select(descriptor => descriptor.Name).ToArray();
        string[] visibleNull = [null!];
        try
        {
            reference.SetFrame(visibleNull, -1, "BEA 1", true, 0d);
            // Calling the retained body with no active painting part evaluates
            // the original arithmetic/iteration but submits no Canvas commands.
            // A visible null reaches foreach in DrawAtlasText; offscreen null
            // rows break before text traversal and must have rendered above.
            string original = ErrorType(() => draw.Invoke(reference, null));
            Check(original == nameof(NullReferenceException), "Retained renderer refuses a visible null row at glyph traversal.");
            using A names = new() { default(Variant) };
            using D facts = new() { ["career_names"] = names, ["selected_career_index"] = -1,
                ["game_name"] = Units("BEA 1"), ["game_name_is_fresh"] = true, ["background_seconds"] = 0d };
            using D result = page.Call("set_frame", facts).AsGodotDictionary();
            Check(!result["ok"].AsBool() && result["error_type"].AsString() == nameof(InvalidDataException), "Native display boundary refuses the visible null instead of fabricating text.");
            _refusalBoundaries.Add(new { name = "visible_null_row", original_error = original,
                native_error = result["error_type"].AsString(), original_stage = "DrawDevSelect glyph iteration", native_stage = "set_frame admission" });

            Enter(host, true);
            var expected = new RetailFrontendSession(descriptors); expected.Confirm(); expected.SelectMainIndex(2); expected.Confirm();
            string oldSelection = ErrorType(() => expected.SelectCareerIndex(11));
            string nativeSelection = ErrorType(() => State(host).SelectCareerIndex(11));
            Check(oldSelection == nameof(NullReferenceException) && nativeSelection == oldSelection,
                "Both existing session owners admit the descriptor then fail when selection reads the null name length.");
            Check(State(host).SelectedCareerIndex == expected.SelectedCareerIndex && State(host).GameName is null && expected.GameName is null,
                "Selection failure retains the original partially mutated selected index and null name.");
            reference.SetFrame(safeNames, 11, null!, State(host).GameNameIsFresh, 0d);
            original = ErrorType(() => draw.Invoke(reference, null));
            Check(original == nameof(ArgumentNullException), "Retained name-width LINQ sum refuses the selected offscreen null.");
            using A allNames = new();
            foreach (string value in safeNames) { using Variant raw = value is null ? default(Variant) : Units(value); allNames.Add(raw); }
            using D selectedFacts = new() { ["career_names"] = allNames, ["selected_career_index"] = 11,
                ["game_name"] = default(Variant), ["game_name_is_fresh"] = State(host).GameNameIsFresh, ["background_seconds"] = 0d };
            using D selectedResult = page.Call("set_frame", selectedFacts).AsGodotDictionary();
            Check(!selectedResult["ok"].AsBool() && selectedResult["error_type"].AsString() == nameof(InvalidDataException), "Native display boundary refuses the selected null name.");
            MethodInfo refresh = typeof(RetailFrontendFlow).GetMethod("UpdateCareerNameFrame", Private)!;
            string hostFailure = ErrorType(() => refresh.Invoke(host, null));
            // The retained host adapter projects the current name with LINQ
            // before calling the native view. Preserve and report that actual
            // ArgumentNullException; it is not the native API's refusal stage.
            Check(hostFailure == original, "Live host retains the original selected-null exception type; actual=" + hostFailure);
            _refusalBoundaries.Add(new { name = "selected_offscreen_null_name", original_error = original,
                native_error = selectedResult["error_type"].AsString(), host_error = hostFailure,
                original_stage = "DrawDevSelect checked name-width sum", native_stage = "set_frame admission",
                host_stage = "UpdateCareerNameFrame raw UTF-16 projection" });
        }
        finally
        {
            // Restore before another engine frame can draw either test view.
            Enter(host, false); Sync(page, reference, host, .75d);
        }
    }
    private static string ErrorType(Action action)
    {
        try { action(); return "none"; }
        catch (TargetInvocationException error) when (error.InnerException is not null) { return error.InnerException.GetType().Name; }
        catch (Exception error) { return error.GetType().Name; }
    }
    private void CheckSnapshot(Control page, GdFrontendSession state)
    {
        using D snapshot = page.Call("view_snapshot").AsGodotDictionary(); using A rows = snapshot["career_names"].AsGodotArray();
        Check(rows.Count == state.CareerNames.Count, "Detached frame retains every injected row, including overflow.");
        for (int index = 0; index < rows.Count; index++)
        {
            using Variant row = rows[index];
            Check(state.CareerNames[index] is null ? row.VariantType == Variant.Type.Nil : row.AsInt32Array().SequenceEqual(Units(state.CareerNames[index])),
                "Detached frame retains raw UTF-16 or the original offscreen null without normalization.");
        }
        Check(snapshot["selected_career_index"].AsInt32() == state.SelectedCareerIndex && snapshot["game_name"].AsInt32Array().SequenceEqual(Units(state.GameName))
            && snapshot["game_name_is_fresh"].AsBool() == state.GameNameIsFresh, "Detached display facts match the sole host session.");
    }
    private void CompareState(GdFrontendSession actual, RetailFrontendSession expected, string message) =>
        Check(actual.Screen == expected.Screen && actual.GameName == expected.GameName && actual.GameNameCursor == expected.GameNameCursor
            && actual.GameNameIsFresh == expected.GameNameIsFresh && actual.SelectedCareerIndex == expected.SelectedCareerIndex, message);
    private void Enter(RetailFrontendFlow host, bool load)
    {
        for (int attempts = 0; host.CurrentScreen != RetailFrontendScreen.MainMenu && attempts < 3; attempts++) Key(host, Godot.Key.Escape);
        Check(host.CurrentScreen == RetailFrontendScreen.MainMenu, "Career page is entered through the actual Main Menu.");
        SetField(host, "_mainTransitionTime", 0); SetField(host, "_mainTransitionCount", 0);
        host.SelectMainIndexForCapture(load ? 2 : 0); host.ConfirmForSmoke();
        Check(host.CurrentScreen == RetailFrontendScreen.DevSelect && State(host).CareerPageMode == (load ? RetailFrontendCareerPageMode.Load : RetailFrontendCareerPageMode.New), "Requested existing career mode is active.");
    }
    private static void Sync(Control page, CareerNameReference reference, RetailFrontendFlow host, double seconds)
    {
        SetField(host, "_feBackSeconds", seconds); host.SelectMainIndexForCapture(0); // Queues one display batch even outside Main.
        GdFrontendSession state = State(host);
        using A names = new(); foreach (string name in state.CareerNames)
        { using Variant units = name is null ? default(Variant) : Units(name); names.Add(units); }
        using D facts = new() { ["career_names"] = names, ["selected_career_index"] = state.SelectedCareerIndex,
            ["game_name"] = Units(state.GameName), ["game_name_is_fresh"] = state.GameNameIsFresh, ["background_seconds"] = seconds };
        Require(page.Call("set_frame", facts)); reference.SetFrame(state.CareerNames, state.SelectedCareerIndex, state.GameName, state.GameNameIsFresh, seconds);
    }
    private static GdFrontendSession State(RetailFrontendFlow host) => (GdFrontendSession)typeof(RetailFrontendFlow).GetField("_session", Private)!.GetValue(host)!;
    private static void SetField(RetailFrontendFlow host, string name, object value) => typeof(RetailFrontendFlow).GetField(name, Private)!.SetValue(host, value);
    private static int[] Units(string value) => value.Select(character => (int)character).ToArray();
    private static uint Bits(float value) => unchecked((uint)BitConverter.SingleToInt32Bits(value));
    private static Color Retail(uint argb) => new(Math.Min(255u, (((argb >> 16) & 255u) * 255u) >> 7) / 255f,
        Math.Min(255u, (((argb >> 8) & 255u) * 255u) >> 7) / 255f, Math.Min(255u, ((argb & 255u) * 255u) >> 7) / 255f, (argb >> 24) / 255f);
    private static void Key(RetailFrontendFlow host, Godot.Key key)
    { using var input = new InputEventKey { Pressed = true, Keycode = key, PhysicalKeycode = key }; host._Input(input); }
    private static void Character(RetailFrontendFlow host, char character, bool echo = false)
    { using var input = new InputEventKey { Pressed = true, Unicode = character, Echo = echo }; host._Input(input); }
    private static void Click(RetailFrontendFlow host, Vector2 point)
    { using var input = new InputEventMouseButton { Pressed = true, ButtonIndex = MouseButton.Left, Position = point }; host._Input(input); }
    private static void Require(Variant returned)
    {
        using (returned)
        {
            if (returned.VariantType != Variant.Type.Dictionary) throw new InvalidDataException("Native career presentation returned no result.");
            using D result = returned.AsGodotDictionary(); if (!result["ok"].AsBool()) throw new InvalidDataException(result["error"].AsString());
        }
    }
    private void SameTexture(Texture2D actual, Texture2D expected, string name)
    { using Image a = actual.GetImage(); using Image e = expected.GetImage(); Check(a.GetSize() == e.GetSize() && a.GetFormat() == e.GetFormat() && a.GetData().SequenceEqual(e.GetData()), "Exact original decoded texture bytes: " + name); }
    private async Task ComparePixels(SubViewport native, SubViewport reference, SubViewport host, string name)
    {
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image actual = native.GetTexture().GetImage(); using Image expected = reference.GetTexture().GetImage(); using Image integrated = host.GetTexture().GetImage();
        Save(actual, name + "-native.png"); Save(expected, name + "-reference.png"); Save(integrated, name + "-host.png");
        ComparePixels(actual, expected, name, "native"); ComparePixels(integrated, expected, name, "host");
    }
    private void Save(Image image, string name)
    { string path = Path.Combine(_directory!, name); Check(!File.Exists(path) && !Directory.Exists(path) && new FileInfo(path).LinkTarget is null && image.SavePng(path) == Error.Ok, "Fresh owned capture: " + name); }
    private void ComparePixels(Image actual, Image expected, string name, string kind)
    {
        byte[] a = actual.GetData(), e = expected.GetData(); int differences = a.Length == e.Length ? a.Where((value, index) => value != e[index]).Count() : -1;
        _pixels.Add(new { name, kind, differences, actualHash = Convert.ToHexString(SHA256.HashData(a)), expectedHash = Convert.ToHexString(SHA256.HashData(e)) });
        Check(actual.GetSize() == expected.GetSize() && actual.GetFormat() == expected.GetFormat() && differences == 0, $"{kind} {name} differs in {differences} RGBA bytes.");
    }
    private SubViewport MakeViewport()
    {
        var view = new SubViewport { Size = new(640, 480), Disable3D = true, TransparentBg = false, RenderTargetUpdateMode = SubViewport.UpdateMode.Always }; AddChild(view);
        var black = new ColorRect { Color = Colors.Black, MouseFilter = Control.MouseFilterEnum.Ignore }; view.AddChild(black); black.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect); return view;
    }
    private static Control MakeStage(SubViewport view)
    { var stage = new Control { Size = new(640, 480), MouseFilter = Control.MouseFilterEnum.Ignore }; view.AddChild(stage); return stage; }
    private static void Fit(Control stage, Vector2I size)
    {
        float scale = Mathf.Min(size.X / 640f, size.Y / 480f);
        stage.Position = new Vector2((size.X - 640f * scale) * .5f, (size.Y - 480f * scale) * .5f); stage.Scale = new Vector2(scale, scale);
    }
    private void RecordInputs()
    {
        foreach (string path in new[] { Fixture, "res://Assets/Frontend/level-bracket-01.texture.aya", "res://Assets/Frontend/fe-arrow.texture.aya",
            "res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya", "res://Assets/Frontend/english.json",
            "res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb" }) _inputHashes.Add(path, Hash(path));
    }
    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(Godot.FileAccess.GetFileAsBytes(path)));
    private static void RequireOwnedDirectory(string directory)
    {
        string owner = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
        if (!Path.IsPathFullyQualified(directory) || Path.GetFullPath(directory) != directory || !directory.StartsWith(owner, StringComparison.Ordinal)
            || directory.Contains('\\') || !Directory.Exists(directory) || Directory.EnumerateFileSystemEntries(directory).Any()) throw new IOException("Render output must be a fresh empty owned directory.");
        for (DirectoryInfo? current = new(directory); current is not null; current = current.Parent)
            if (current.LinkTarget is not null) throw new IOException("Render output ancestry must not contain symlinks.");
    }
    private void Check(bool condition, string message) { _checks++; _counts[_group] = _counts.GetValueOrDefault(_group) + 1; if (!condition) throw new InvalidOperationException(message); }
    private void Complete() => _completed.Add(_group);
    private void Report(string? error)
    {
        if (_finished) return; _finished = true;
        GD.Print("CAREER_NAME_SCENE_CHECKS: " + JsonSerializer.Serialize(new { schema = 1, checks = _checks, samples = _samples,
            completed = _completed, counts = _counts, rendered = _directory is not null, pixels = _pixels,
            reference_revision = "14f6f72b", input_sha256 = _inputHashes, refusal_boundaries = _refusalBoundaries,
            failure_count = error is null ? 0 : 1, error }));
    }
}
