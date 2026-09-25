// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;
using Frame = OnslaughtRebuild.GodotClient.LevelSelectReference.Frame;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Actual Level Select and live host versus the independent 51477f62 draw
/// bodies. The tracked gold fixture is verified/read-only; no gameplay, saves,
/// physical input or personal data discovery. Static node-zero highlighting,
/// existing selection quirks and measured rendering gaps remain unchanged.
/// Headless checks make no pixel or full retail-parity claim.
/// </summary>
public sealed partial class LevelSelectSceneChecks : Node
{
    private const string Fixture = "res://../../tests_shared/fixtures/gold_career_save.bin";
    private static readonly string[] Required = ["production_assets_and_geometry", "frames_and_host", "hit_bounds_and_navigation", "authored_content", "read_only_and_ownership"];
    private static readonly Vector2I[] Sizes = [new(640, 480), new(1280, 720), new(801, 601), new(320, 240)];
    private static readonly string[] RingPaths = Enumerable.Range(1, 11).Select(index => $"Graph/Nodes/Node{index:D2}/Outer")
        .Concat(["Graph/Nodes/Node00/Outer", "Graph/Nodes/Node00/Inner"]).ToArray();
    private static readonly string[] Passes = new[] { "Background", "Guides/Vertical", "Guides/Horizontal", "SweepArcs/Current", "SweepArcs/Middle", "SweepArcs/Last" }
        .Concat(Enumerable.Range(0, 16).Select(index => $"Graph/Links/Link{index:D2}"))
        .Concat(RingPaths).Concat(["Columns/One", "Columns/Two", "Columns/Three", "Decoration/Shadow", "Decoration/Body", "Header/Panel", "Header/Title", "Episode", "LevelName", "Navigation/Back", "Navigation/Forward"]).ToArray();
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
        List<RetailFrontendFlow> facades = [];
        try
        {
            string[] arguments = OS.GetCmdlineUserArgs();
            Check(!Engine.IsEditorHint() && arguments.Contains("--skipfmv", StringComparer.Ordinal), "Focused runtime checks require --skipfmv.");
            const string prefix = "--level-select-render-dir=";
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
                Report("Level Select comparison did not complete every required group before its bounded timeout."); GetTree().Quit(1);
            };
            Input.MouseModeEnum pointer = Input.MouseMode;
            RecordInputs(); byte[] fixtureBytes = Godot.FileAccess.GetFileAsBytes(Fixture);
            Check(_inputHashes[Fixture] == "0C17E47DB9D666E9B26EF88D43D0A25E7CBFBF4F88C8005CC748965050E506FB",
                "The tracked gold career is the exact retained comparison fixture.");
            RetailCareerSave save = RetailCareerSaveCodec.Read(fixtureBytes);
            Check(save.IsWorldSelectable(100) && save.IsWorldSelectable(110), "The unchanged verified fixture admits both existing worlds.");
            SubViewport nativeView = MakeViewport(), referenceView = MakeViewport(), hostView = MakeViewport();
            views.AddRange([nativeView, referenceView, hostView]);
            Control nativeStage = MakeStage(nativeView), referenceStage = MakeStage(referenceView);
            Control page = GD.Load<PackedScene>("res://Scenes/Frontend/LevelSelect.tscn").Instantiate<Control>();
            foreach (string path in Passes) Check(page.GetNodeOrNull<Control>(path) is not null, "Actual production draw control exists before Play: " + path);
            foreach (string path in new[] { "Graph/Nodes/Node00/Target", "Graph/Nodes/Node01/Target" })
                Check(page.GetNodeOrNull<Control>(path) is not null, "The original offset hit region is an authored node child: " + path);
            nativeStage.AddChild(page);
            LevelSelectReference reference = GD.Load<PackedScene>("res://Scenes/Frontend/Tests/LevelSelectReference.tscn").Instantiate<LevelSelectReference>();
            referenceStage.AddChild(reference);
            var hosts = new Dictionary<int, RetailFrontendFlow>();
            foreach (int world in new[] { 100, 110 })
            {
                RetailFrontendFlow host = RetailFrontendFlow.InstantiateScene(); facades.Add(host);
                RetailCareerDescriptor[] careers = world == 100 ? [] : [new RetailCareerDescriptor(1, "Read-only gold fixture", save)];
                host.Initialize(careers); hostView.AddChild(host.View); host.View.SetProcess(false); host.View.SetProcessInput(false);
                host.SetMouseCursorDesignPositionForCapture(new Vector2(-100, -100));
                EnterLevelSelect(host, world, careers.SingleOrDefault()); host.View.Visible = false; hosts.Add(world, host);
            }
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            string title = reference.LocalizedTitle;
            Configure(page, title);
            CheckAssetsAndGeometry(page, reference, hosts[100]); Complete();

            _group = Required[1];
            async Task Sample(RetailFrontendFlow host, Vector2I size, string label, Frame facts, bool includeHost = true, Frame? displayed = null)
            {
                foreach (RetailFrontendFlow current in hosts.Values) current.View.Visible = includeHost && ReferenceEquals(current, host);
                foreach (SubViewport viewport in views) viewport.Size = size;
                Fit(nativeStage, size); Fit(referenceStage, size);
                foreach (RetailFrontendFlow current in hosts.Values) current.View.Size = size;
                Configure(page, facts.Title); using D batch = Facts(facts); Require(page.Call("set_frame", batch)); reference.SetFrame(displayed ?? facts);
                if (includeHost) { SetField(host, "_fe_back_seconds", facts.BackgroundSeconds); host.SelectMainIndexForCapture(0); }
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                CheckFrame(page, reference, facts, displayed ?? facts);
                if (includeHost) CheckFrame(host.View.GetNode<Control>("Stage/LevelSelect"), reference, facts, facts);
                if (_directory is not null) await ComparePixels(nativeView, referenceView, includeHost ? hostView : null, label);
                _samples++;
            }
            double[] times = [0d, .1d, .5166666666666667d, 19.17d];
            for (int index = 0; index < Sizes.Length; index++)
                foreach (int world in new[] { 100, 110 })
                {
                    Check(State(hosts[world]).SelectedWorldNumber == world, "The existing session owns world selection.");
                    await Sample(hosts[world], Sizes[index], $"{Sizes[index].X}x{Sizes[index].Y}-world-{world}", new(title, State(hosts[world]).SelectedLevelName, times[index]));
                }
            foreach ((string label, Frame facts) in new[] {
                ("empty-raw-name", new Frame(title, "", .15d)),
                ("raw-utf16", new Frame("A\0B\ud800\udc00\ufffd\uffff¡¿é\u011f\u0120", "A\0B\ud800\udc00\ufffd\uffff¡¿é\u011f\u0120", .15d)) })
                await Sample(hosts[100], new(640, 480), label, facts, includeHost: false);
            Check(State(hosts[100]).SelectedWorldNumber == 100 && State(hosts[110]).SelectedWorldNumber == 110, "Synthetic labels do not alter either host's campaign.");
            Complete();

            _group = Required[2];
            hosts[100].View.Visible = true;
            CheckHitBounds(page, hosts[100], nativeStage, views);
            CheckNavigation(hosts[100], false); CheckNavigation(hosts[110], true);
            Complete();

            _group = Required[3];
            Control old = reference.GetNode<Control>("CareerGraph"), integrated = hosts[100].View.GetNode<Control>("Stage/LevelSelect");
            Vector2 position = page.Position, extent = page.Size, scale = page.Scale; float rotation = page.Rotation;
            Frame production = new(title, State(hosts[100]).SelectedLevelName, .35d);
            foreach (string edit in new[] { "position", "size", "scale-rotation" })
            {
                foreach (Control component in new[] { page, old, integrated })
                {
                    if (edit == "position") component.Position = position + new Vector2(3.25f, -2.5f);
                    if (edit == "size") component.Size = extent + new Vector2(7f, 3f);
                    if (edit == "scale-rotation") { component.Scale = new Vector2(.99f, 1.01f); component.Rotation = .012f; }
                }
                await Sample(hosts[100], new(801, 601), "authored-" + edit, production);
                Check(page.Position == old.Position && page.Size == old.Size && page.Scale == old.Scale && page.Rotation == old.Rotation,
                    "Production frames retain authored root changes matching the original CareerGraph frame.");
                foreach (Control component in new[] { page, old, integrated })
                { component.Position = position; component.Size = extent; component.Scale = scale; component.Rotation = rotation; }
            }
            Node titleLabel = page.GetNode("Header/Title"), levelLabel = page.GetNode("LevelName");
            string editorTitle = titleLabel.Get("text").AsString(), editorName = levelLabel.Get("text").AsString();
            titleLabel.Set("text", "Explicit enhanced title"); titleLabel.Set("override_text", true);
            levelLabel.Set("text", "Explicit enhanced level"); levelLabel.Set("override_text", true);
            await Sample(hosts[100], new(640, 480), "explicit-editor-text", production, includeHost: false,
                displayed: new("Explicit enhanced title", "Explicit enhanced level", production.BackgroundSeconds));
            CheckSnapshot(page, production);
            titleLabel.Set("override_text", false); titleLabel.Set("text", editorTitle);
            levelLabel.Set("override_text", false); levelLabel.Set("text", editorName);
            Configure(page, production.Title); using (D batch = Facts(production)) Require(page.Call("set_frame", batch));
            Check(levelLabel.Call("displayed_units").AsInt32Array().SequenceEqual(Units(production.LevelName)), "Disabling enhanced text restores imported facts.");
            // The old monolithic CareerGraph override field was unused. New
            // explicit label overrides are an editor feature, not old behavior.
            Complete();

            _group = Required[4];
            using (D batch = Facts(production))
            { batch["unowned_node"] = page; Require(page.Call("set_frame", batch)); batch["level_name"] = new[] { 88 }; batch["background_seconds"] = 99d; }
            using (D snapshot = page.Call("view_snapshot").AsGodotDictionary())
            {
                Check(snapshot.Count == 2 && !snapshot.ContainsKey("unowned_node"), "Only the two admitted display facts enter storage.");
                snapshot["level_name"] = new[] { 89 }; snapshot["background_seconds"] = 99d;
            }
            CheckSnapshot(page, production);
            using (D graph = page.Call("graph_snapshot").AsGodotDictionary())
            { using A links = graph["links"].AsGodotArray(); using D first = links[0].AsGodotDictionary(); first["from"] = new Vector2(99, 99); }
            CheckGeometry(page, reference);
            foreach (Control component in new[] { page, hosts[100].View.GetNode<Control>("Stage/LevelSelect"), hosts[110].View.GetNode<Control>("Stage/LevelSelect") })
            {
                foreach (Node owner in component.FindChildren("*", "Control", true, false).Prepend(component))
                    Check(!owner.IsProcessing() && !owner.IsProcessingInput() && !owner.IsProcessingUnhandledInput(), "Level Select owns no clock or input.");
                Check(component.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0 && component.FindChildren("*", "Node3D", true, false).Count == 0,
                    "Display controls create no audio or gameplay world.");
            }
            Check(Input.MouseMode == pointer, "Synthetic callbacks leave physical pointer mode unchanged.");
            Check(save.ContainerBytes.SequenceEqual(fixtureBytes), "Verified career owner retains all original bytes.");
            foreach ((string path, string before) in _inputHashes) Check(Hash(path) == before, "Read-only input bytes unchanged: " + path);
            Complete();
            Check(_completed.SequenceEqual(Required) && Required.All(group => _counts.GetValueOrDefault(group) > 0), "Every required group completed.");
            Check(_samples == 14 && _pixels.Count == (_directory is null ? 0 : 25), "Every bounded state completed; headless cannot claim pixel checks.");
            FrontendHarnessChecks.ReleaseFacades(facades);
            foreach (SubViewport viewport in views) viewport.QueueFree(); views.Clear();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Report(null); GetTree().Quit(0);
        }
        catch (Exception error)
        {
            FrontendHarnessChecks.ReleaseFacades(facades);
            foreach (SubViewport viewport in views) viewport.QueueFree();
            GD.PushError(error.ToString()); Report(error.ToString()); GetTree().Quit(1);
        }
    }

    private void CheckAssetsAndGeometry(Control page, LevelSelectReference reference, RetailFrontendFlow host)
    {
        foreach ((string name, Texture2D expected, int[] widths) in new[] { ("body_font", reference.BodyFont, reference.BodyWidths), ("title_font", reference.TitleFont, reference.TitleWidths) })
        {
            using Variant fontValue = page.Get(name); Resource font = fontValue.As<Resource>();
            using Variant textureValue = font.Get("page"); SameTexture(textureValue.As<Texture2D>(), expected, name);
            Check(font.Call("glyph_widths").AsInt32Array().SequenceEqual(widths), "All retained glyph widths agree: " + name);
            foreach (string text in new[] { "", "SELECT LEVEL", "1.00 - Training Level", "1.10 - Blackout", "Episode 1", "A\0B\ud800\udc00\ufffd\uffff¡¿é\u011f\u0120" })
                foreach (float scale in new[] { 1f, 1.4f, 1.5f })
                    Check(Bits((float)font.Call("measure", Units(text), scale).AsDouble()) == Bits(reference.TextWidth(text, name == "title_font", scale)), "Raw UTF-16 width retains all original float32 stores.");
        }
        SameTexture(page.GetNode("Decoration/Body").Get("texture").As<Texture2D>(), reference.Bracket, "level-bracket-01");
        SameTexture(page.GetNode("Navigation/Forward").Get("texture").As<Texture2D>(), reference.Arrow, "fe-arrow");
        for (int index = 0; index < RingPaths.Length; index++)
            SameTexture(page.GetNode(RingPaths[index]).Get("texture").As<Texture2D>(), reference.Rings[index].Texture, "ordered node ring " + index);
        using Variant shared = host.View.GetNode("Stage/LevelSelect").Get("body_font"); using Variant existing = host.View.GetNode("Stage/Options").Get("body_font");
        Check(shared.AsGodotObject().GetInstanceId() == existing.AsGodotObject().GetInstanceId(), "Live host shares the existing admitted font resource.");
        CheckGeometry(page, reference);
        double tie = 3.5d / 30d;
        foreach (double seconds in new[] { -1d, -0d, 0d, Math.BitDecrement(tie), tie, Math.BitIncrement(tie), .15d, .5d, 19.07d, 19.17d, 123.4d })
        {
            Frame facts = new(reference.LocalizedTitle, "Clock-only display fixture", seconds);
            using D batch = Facts(facts); Require(page.Call("set_frame", batch)); CheckSnapshot(page, facts);
            CheckBackground(page, reference, seconds);
        }
    }

    private void CheckGeometry(Control page, LevelSelectReference reference)
    {
        using D actual = page.Call("graph_snapshot").AsGodotDictionary();
        using A arcs = actual["arcs"].AsGodotArray(), links = actual["links"].AsGodotArray(), rings = actual["rings"].AsGodotArray();
        Check(reference.Arcs.Count == 3 && reference.Lines.Count == 16 && reference.Rings.Count == 13
            && arcs.Count == 3 && links.Count == 16 && rings.Count == 13, "All original ordered geometry submissions are present.");
        for (int index = 0; index < arcs.Count; index++)
        {
            LevelSelectReference.ArcCall expected = reference.Arcs[index]; using D row = arcs[index].AsGodotDictionary();
            CheckVector(row["center"].AsVector2(), expected.Center, "Arc center");
            Check(Bits((float)row["radius"].AsDouble()) == Bits(expected.Radius) && Bits((float)row["start"].AsDouble()) == Bits(expected.Start)
                && Bits((float)row["end"].AsDouble()) == Bits(expected.End) && row["points"].AsInt32() == expected.Points
                && row["ink"].AsColor() == expected.Ink && Bits((float)row["width"].AsDouble()) == Bits(expected.Width)
                && row["antialiased"].AsBool() == expected.Antialiased, "Exact retained DrawArc arguments and order.");
        }
        for (int index = 0; index < links.Count; index++)
        {
            LevelSelectReference.LineCall expected = reference.Lines[index]; using D row = links[index].AsGodotDictionary();
            CheckVector(row["from"].AsVector2(), expected.Start, "Trimmed link start"); CheckVector(row["to"].AsVector2(), expected.End, "Trimmed link end");
            Check(row["ink"].AsColor() == expected.Ink && Bits((float)row["width"].AsDouble()) == Bits(expected.Width)
                && row["antialiased"].AsBool() == expected.Antialiased, "Exact retained DrawLine ink/width/antialiasing and order.");
        }
        for (int index = 0; index < rings.Count; index++)
        {
            LevelSelectReference.TextureCall expected = reference.Rings[index]; using D row = rings[index].AsGodotDictionary();
            Rect2 rectangle = row["rectangle"].AsRect2();
            CheckVector(rectangle.Position, expected.Rectangle.Position, "Ordered ring origin"); CheckVector(rectangle.Size, expected.Rectangle.Size, "Ordered ring size");
            Check(row["ink"].AsColor() == expected.Ink, "Original node ring tint; current ring stays at node 0.");
        }
    }

    private void CheckFrame(Control page, LevelSelectReference reference, Frame facts, Frame displayed)
    {
        CheckSnapshot(page, facts);
        Control old = reference.GetNode<Control>("CareerGraph");
        Check(page.Position == old.Position && page.Size == old.Size && page.Scale == old.Scale && page.Rotation == old.Rotation,
            "The native page retains the original single authored CareerGraph frame.");
        Check(page.GetGlobalTransformWithCanvas() == old.GetGlobalTransformWithCanvas(), "Actual page and retained canvas frames agree.");
        foreach (string path in Passes)
        {
            Control pass = page.GetNode<Control>(path);
            Check(pass.Get("source_rect").AsRect2() == LevelSelectReference.SourceRect, "Original full-stage source rectangle: " + path);
            Check(pass.Call("source_transform").AsTransform2D() == LevelSelectReference.SourceTransform(old), "Source mapping keeps original grouped drawing: " + path);
            Check(pass.GetGlobalTransformWithCanvas() == old.GetGlobalTransformWithCanvas(), "Actual draw pass canvas transform: " + path);
        }
        foreach ((string path, string text, Vector2 origin, float scale, Color ink, bool title) in new[] {
            ("Header/Title", displayed.Title, reference.TitleOrigin, 1f, LevelSelectReference.TitleTint, true),
            ("Episode", "Episode 1", new Vector2(130f, 130.2f), 1.4f, Colors.White, false),
            ("LevelName", displayed.LevelName, new Vector2(130f, 156.8f), 1.4f, LevelSelectReference.SelectedTint, false),
            ("Columns/One", "1", new Vector2(163f, 182.5f), 1.5f, LevelSelectReference.BlueTint, false),
            ("Columns/Two", "2", new Vector2(283f, 182.5f), 1.5f, LevelSelectReference.BlueTint, false),
            ("Columns/Three", "3", new Vector2(524f, 182.5f), 1.5f, LevelSelectReference.BlueTint, false) })
        {
            Node label = page.GetNode(path);
            Check(label.Call("displayed_units").AsInt32Array().SequenceEqual(Units(text)), "Exact raw UTF-16 label: " + path);
            CheckVector(label.Call("drawing_origin").AsVector2(), origin, "Original label origin: " + path);
            Check(label.Get("glyph_scale").AsVector2() == new Vector2(scale, scale) && label.Call("drawing_color").AsColor() == ink,
                "Original label scale and ink: " + path);
            Check(Bits((float)label.Call("font_width").AsDouble()) == Bits(reference.TextWidth(text, title, scale)), "Original measured width: " + path);
            Check(label.Get("shadow").AsBool() && !label.Get("name_glyphs").AsBool(), "Original ordinary glyph mapping and shadow: " + path);
        }
        foreach ((string path, Rect2 expected) in new[] { ("Guides/Vertical", new Rect2(123, 0, 1, 480)), ("Guides/Horizontal", new Rect2(0, 180, 640, 1)),
            ("Header/Panel", new Rect2(191, 69, 394, 21)), ("Navigation/Back", new Rect2(9, 438, -28, 36)), ("Navigation/Forward", new Rect2(604, 437, 28, 36)) })
            Check(page.GetNode(path).Call("drawing_rect").AsRect2() == expected, "Original measured rectangle: " + path);
        foreach (string path in new[] { "Navigation/Back", "Navigation/Forward" })
            Check(page.GetNode(path).Get("region").AsRect2() == new Rect2(16, 12, 30, 40) && page.GetNode(path).Get("ink_color").AsColor() == LevelSelectReference.ArrowTint, "Original arrow crop/tint.");
        CheckGeometry(page, reference); CheckBackground(page, reference, facts.BackgroundSeconds);
    }

    private void CheckBackground(Control page, LevelSelectReference reference, double seconds)
    {
        using D background = page.GetNode("Background").Call("view_snapshot").AsGodotDictionary();
        int count = reference.BackgroundFrames.Length;
        Check(count > 0 && background["frame_count"].AsInt32() == count && background["alpha"].AsDouble() == 1d
            && background["frame"].AsInt32() == LevelSelectReference.FeBackFrameIndex(seconds, count), "Settled FEBack uses the unchanged 30fps/ties-even/phase3 law and complete production strip.");
    }
    private void CheckHitBounds(Control page, RetailFrontendFlow host, Control stage, IReadOnlyList<SubViewport> views)
    {
        foreach (Vector2I size in Sizes.Append(new(1024, 768)))
        {
            foreach (SubViewport view in views) view.Size = size; host.View.Size = size; Fit(stage, size);
            foreach (Rect2 rect in new[] { new Rect2(0, 430, 48, 48), new Rect2(595, 430, 45, 48), new Rect2(120, 265, 60, 60), new Rect2(180, 265, 60, 60) })
            {
                float cx = rect.Position.X + rect.Size.X * .5f, cy = rect.Position.Y + rect.Size.Y * .5f;
                IEnumerable<Vector2> points = new[] { rect.Position.X, rect.End.X }.SelectMany(x => new[] { MathF.BitDecrement(x), x, MathF.BitIncrement(x) }).Select(x => new Vector2(x, cy))
                    .Concat(new[] { rect.Position.Y, rect.End.Y }.SelectMany(y => new[] { MathF.BitDecrement(y), y, MathF.BitIncrement(y) }).Select(y => new Vector2(cx, y)));
                foreach (Vector2 point in points)
                {
                    int expected = LevelSelectReference.HitTest(point);
                    Check(page.Call("hit_test", point).AsInt32() == expected && FrontendHarnessChecks.Hit(host, "level_select_target_at", point) == expected,
                        "Native and actual host retain half-open target precedence without a Stage roundtrip.");
                }
            }
            Check(page.Call("hit_test", new Vector2(268, 295)).AsInt32() == 0, "Other drawn nodes gain no invented click behavior.");
        }
    }

    private void CheckNavigation(RetailFrontendFlow host, bool loaded)
    {
        host.View.Size = new(640, 480); var effects = new List<string>(); int loads = 0, starts = 0, activations = 0, exits = 0;
        void Audio(RetailFrontendAudioCue cue) => effects.Add("audio:" + cue);
        void Cursor(RetailFrontendCursorMode mode) => effects.Add("cursor:" + mode);
        void Load() => loads++; void Start() => starts++; void Activated() => activations++; void Exit() => exits++;
        host.AudioCueRequested += Audio; host.CursorModeRequested += Cursor; host.Level100LoadRequested += Load;
        host.Level100LoadingStarted += Start; host.GameplayActivated += Activated; host.ExitRequested += Exit;
        try
        {
            int initialWorld = State(host).SelectedWorldNumber;
            foreach (Godot.Key key in new[] { Godot.Key.Up, Godot.Key.Down, Godot.Key.Left, Godot.Key.Right }) Key(host, key);
            Key(host, Godot.Key.Enter, echo: true); Click(host, new(48, 450)); Click(host, new(600, 478)); Click(host, new(268, 295));
            Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect && State(host).SelectedWorldNumber == initialWorld && effects.Count == 0,
                "Arrow keys, echoes, excluded edges and unimplemented graph nodes remain inert.");
            Click(host, new(210, 295));
            Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect && effects.Count == 0,
                loaded ? "Clicking already-selected 110 remains unconfirmed because SelectWorld returns false." : "Locked 110 does not confirm the root as a substitute.");
            Click(host, new(148, 295));
            Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing && State(host).SelectedWorldNumber == 100
                && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "Root-node click confirms even when the root is already selected.");
            Key(host, Godot.Key.Escape); effects.Clear();
            if (loaded)
            {
                Click(host, new(210, 295));
                Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing && State(host).SelectedWorldNumber == 110
                    && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "An unlocked different 110 node selects then confirms using the existing callback order.");
                Key(host, Godot.Key.Escape); effects.Clear();
                Click(host, new(210, 295));
                Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect && effects.Count == 0, "The second 110 click remains a no-op on identical selection.");
            }
            foreach (bool pointer in new[] { false, true })
            {
                effects.Clear(); if (pointer) Click(host, new(595, 430)); else Key(host, Godot.Key.Enter);
                Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "Keyboard/forward chevron confirms the selected world.");
                Key(host, Godot.Key.Escape); effects.Clear();
                if (pointer) Click(host, new(0, 430)); else Key(host, Godot.Key.Escape);
                Check(host.CurrentScreen == RetailFrontendScreen.DevSelect && effects.SequenceEqual(new[] { "audio:Back", "cursor:Custom" }), "Back returns to the existing career-name page in order.");
                host.ConfirmForSmoke(); Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect, "Retained New/Load career selection re-enters Level Select.");
                if (loaded) Check(State(host).SelectWorld(110), "Read-only loaded campaign restores 110 after its original suggested-world reset.");
            }
            Check(starts == 0 && loads == 0 && activations == 0 && exits == 0 && !State(host).ConsumeLevel100LaunchRequest(), "Level Select never starts gameplay or window quit.");
        }
        finally
        {
            host.AudioCueRequested -= Audio; host.CursorModeRequested -= Cursor; host.Level100LoadRequested -= Load;
            host.Level100LoadingStarted -= Start; host.GameplayActivated -= Activated; host.ExitRequested -= Exit;
        }
    }
    private void EnterLevelSelect(RetailFrontendFlow host, int world, RetailCareerDescriptor? suppliedCareer)
    {
        host.ConfirmForSmoke(); Check(host.CurrentScreen == RetailFrontendScreen.MainMenu, "Cold frontend enters Main Menu.");
        SetField(host, "_main_transition_time", 0); SetField(host, "_main_transition_count", 0);
        host.SelectMainIndexForCapture(suppliedCareer is null ? 0 : 2); host.ConfirmForSmoke();
        Check(host.CurrentScreen == RetailFrontendScreen.DevSelect, "Actual New/Load entry reaches Career Name.");
        if (suppliedCareer is not null)
        {
            Check(State(host).SelectedCareerIndex == -1, "Load initially selects no descriptor implicitly.");
            Key(host, Godot.Key.Down); Check(State(host).SelectedCareerIndex == 0, "Actual Down selects the supplied verified fixture.");
        }
        RetailCareerDescriptor? selected = null; int selections = 0;
        void Selected(RetailCareerDescriptor descriptor) { selected = descriptor; selections++; }
        host.CareerSelected += Selected;
        try { host.ConfirmForSmoke(); } finally { host.CareerSelected -= Selected; }
        Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect, "Actual career confirmation reaches Level Select.");
        Check(suppliedCareer is null ? selections == 0 : selections == 1 && selected is not null
            && ReferenceEquals(selected, suppliedCareer) && ReferenceEquals(selected.Career, suppliedCareer.Career), "Load hands off the exact supplied descriptor/save; New has no save handoff.");
        if (State(host).SelectedWorldNumber != world) Check(State(host).SelectWorld(world), "Actual verified career admits the requested existing world.");
        Check(State(host).SelectedWorldNumber == world && State(host).SelectedLevelName == RetailFrontendWorldStrings.LevelName(world), "Display text follows the existing selected-world owner.");
        host.SelectMainIndexForCapture(0);
    }
    private void CheckSnapshot(Control page, Frame frame)
    {
        using D actual = page.Call("view_snapshot").AsGodotDictionary();
        Check(actual.Count == 2 && actual["level_name"].AsInt32Array().SequenceEqual(Units(frame.LevelName))
            && BitConverter.DoubleToInt64Bits(actual["background_seconds"].AsDouble()) == BitConverter.DoubleToInt64Bits(frame.BackgroundSeconds),
            "Detached raw name/clock facts retain exact UTF-16 and binary64 words.");
    }
    private void CheckVector(Vector2 actual, Vector2 expected, string name) => Check(Bits(actual.X) == Bits(expected.X) && Bits(actual.Y) == Bits(expected.Y), name + " retains both float32 words.");
    private static D Facts(Frame frame) => new() { ["level_name"] = Units(frame.LevelName), ["background_seconds"] = frame.BackgroundSeconds };
    private static void Configure(Control page, string title)
    { using D paths = new(); using D fonts = new(); using A frames = new(); Require(page.Call("configure_assets", paths, fonts, frames, Units(title))); }
    private static GdFrontendSession State(RetailFrontendFlow host) => GdFrontendSession.BorrowExisting(host.View);
    private static void SetField(RetailFrontendFlow host, string name, Variant value) => host.View.Set(name, value);
    private static int[] Units(string value) => value.Select(character => (int)character).ToArray();
    private static uint Bits(float value) => unchecked((uint)BitConverter.SingleToInt32Bits(value));
    private static void Key(RetailFrontendFlow host, Godot.Key key, bool echo = false)
    { using var input = new InputEventKey { Pressed = true, Keycode = key, PhysicalKeycode = key, Echo = echo }; FrontendHarnessChecks.Command(host, "handle_input", input); }
    private static void Click(RetailFrontendFlow host, Vector2 point)
    { using var input = new InputEventMouseButton { Pressed = true, ButtonIndex = MouseButton.Left, Position = point }; FrontendHarnessChecks.Command(host, "handle_input", input); }
    private static void Require(Variant returned)
    {
        using (returned)
        {
            if (returned.VariantType != Variant.Type.Dictionary) throw new InvalidDataException("Native level-select presentation returned no result.");
            using D result = returned.AsGodotDictionary(); if (!result["ok"].AsBool()) throw new InvalidDataException(result["error"].AsString());
        }
    }
    private void SameTexture(Texture2D actual, Texture2D expected, string name)
    { using Image a = actual.GetImage(); using Image e = expected.GetImage(); Check(a.GetSize() == e.GetSize() && a.GetFormat() == e.GetFormat() && a.GetData().SequenceEqual(e.GetData()), "Exact original decoded texture bytes: " + name); }
    private async Task ComparePixels(SubViewport native, SubViewport reference, SubViewport? host, string name)
    {
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image actual = native.GetTexture().GetImage(); using Image expected = reference.GetTexture().GetImage();
        Save(actual, name + "-native.png"); Save(expected, name + "-reference.png"); ComparePixels(actual, expected, name, "native");
        if (host is null) return;
        using Image integrated = host.GetTexture().GetImage(); Save(integrated, name + "-host.png"); ComparePixels(integrated, expected, name, "host");
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
        foreach (string path in new[] { Fixture, "res://Assets/Frontend/level-bracket-01.texture.aya", "res://Assets/Frontend/level-ring-01.texture.aya",
            "res://Assets/Frontend/level-ring-02.texture.aya", "res://Assets/Frontend/fe-arrow.texture.aya", "res://Assets/Hud/font-13ps.texture.aya",
            "res://Assets/Hud/font-22.texture.aya", "res://Assets/Frontend/english.json", "res://Assets/Frontend/english-worlds.json",
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
        GD.Print("LEVEL_SELECT_SCENE_CHECKS: " + JsonSerializer.Serialize(new { schema = 1, checks = _checks, samples = _samples,
            completed = _completed, counts = _counts, rendered = _directory is not null, pixels = _pixels,
            reference_revision = "51477f62", input_sha256 = _inputHashes,
            failure_count = error is null ? 0 : 1, error }));
    }
}
