// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;
using Frame = OnslaughtRebuild.GodotClient.BriefingReference.Frame;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Native Mission Briefing and its live host against the retained 51477f62
/// renderer. The tracked gold fixture is read through its verified codec only
/// to select World 110; no gameplay, save writing or personal-save discovery.
/// Conversion equivalence preserves the empty-body fallback, missing video and
/// measured art gaps. Headless checks make no pixel or full retail-parity claim.
/// </summary>
public sealed partial class BriefingSceneChecks : Node
{
    private const string Fixture = "res://../../tests_shared/fixtures/gold_career_save.bin";
    private static readonly string[] Required = ["production_assets_and_wrap", "frames_and_host", "hit_bounds_and_navigation", "authored_sections", "read_only_and_ownership"];
    private static readonly string[] Passes = ["Background/Rock", "Background/Ring", "Header/Panel", "Header/Title", "LevelName/Text", "Body/Text", "Navigation/Back", "Navigation/Forward"];
    private static readonly Vector2I[] Sizes = [new(640, 480), new(1280, 720), new(801, 601), new(320, 240)];
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
            const string prefix = "--briefing-render-dir=";
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
                Report("Briefing comparison did not complete every required group before its bounded timeout.");
                GetTree().Quit(1);
            };
            Input.MouseModeEnum pointer = Input.MouseMode;
            RecordInputs();
            byte[] fixtureBytes = Godot.FileAccess.GetFileAsBytes(Fixture);
            RetailCareerSave save = RetailCareerSaveCodec.Read(fixtureBytes);
            Check(save.IsWorldSelectable(110), "The actual verified fixture admits World 110 without synthetic progression.");
            SubViewport nativeView = MakeViewport(), referenceView = MakeViewport(), hostView = MakeViewport();
            views.AddRange([nativeView, referenceView, hostView]);
            Control nativeStage = MakeStage(nativeView), referenceStage = MakeStage(referenceView);
            Control page = GD.Load<PackedScene>("res://Scenes/Frontend/MissionBriefing.tscn").Instantiate<Control>();
            foreach (string section in BriefingReference.Sections.Keys)
                Check(page.GetNodeOrNull<Control>(section) is not null, "Authored production section exists before Play: " + section);
            nativeStage.AddChild(page);
            BriefingReference reference = GD.Load<PackedScene>("res://Scenes/Frontend/Tests/BriefingReference.tscn").Instantiate<BriefingReference>();
            referenceStage.AddChild(reference);
            var hosts = new Dictionary<int, RetailFrontendFlow>();
            foreach (int world in new[] { 100, 110 })
            {
                RetailFrontendFlow host = RetailFrontendFlow.InstantiateScene(); facades.Add(host);
                RetailCareerDescriptor[] suppliedCareers = world == 100 ? [] : [new RetailCareerDescriptor(1, "Read-only gold fixture", save)];
                host.Initialize(suppliedCareers);
                hostView.AddChild(host.View); host.View.SetProcess(false); host.View.SetProcessInput(false);
                host.SetMouseCursorDesignPositionForCapture(new Vector2(-100f, -100f));
                EnterBriefing(host, world, suppliedCareers.SingleOrDefault()); host.View.Visible = false; hosts.Add(world, host);
            }
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Require(page.Call("configure_assets"));
            CheckAssetsAndWrap(page, reference, hosts[100]); Complete();

            _group = Required[1];
            async Task Sample(RetailFrontendFlow host, Vector2I size, string label, Frame facts, bool includeHost = true, Frame? displayed = null)
            {
                foreach (RetailFrontendFlow current in hosts.Values) current.View.Visible = includeHost && ReferenceEquals(current, host);
                foreach (SubViewport viewport in views) viewport.Size = size;
                Fit(nativeStage, size); Fit(referenceStage, size);
                foreach (RetailFrontendFlow current in hosts.Values) current.View.Size = size;
                using D batch = Facts(facts); Require(page.Call("set_frame", batch)); reference.SetFrame(displayed ?? facts);
                if (includeHost) host.SelectMainIndexForCapture(0);
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                CheckFrame(page, reference, facts, displayed ?? facts);
                if (includeHost) CheckFrame(host.View.GetNode<Control>("Stage/MissionBriefing"), reference, ReadFrame(host), ReadFrame(host));
                if (_directory is not null) await ComparePixels(nativeView, referenceView, includeHost ? hostView : null, label);
                _samples++;
            }
            foreach (Vector2I size in Sizes)
                foreach (int world in new[] { 100, 110 })
                {
                    Check(State(hosts[world]).SelectedWorldNumber == world, "The existing session owns the actual selected world.");
                    await Sample(hosts[world], size, $"{size.X}x{size.Y}-world-{world}", ReadFrame(hosts[world]));
                }
            Frame production = ReadFrame(hosts[100]);
            foreach ((string label, Frame facts) in new[] {
                ("empty-body-fallback", new Frame("Empty body keeps the original fallback", [])),
                ("explicit-blank-paragraphs", new Frame(production.SelectedLevelName, ["First paragraph.", "", "", "Last paragraph.", ""])),
                ("spaces-and-long-word", new Frame(production.SelectedLevelName, ["   A  B  ", new string('W', 60), " C\tD E\nF  ", "   "])),
                ("raw-utf16", new Frame("N\0\ud800\udc00\ufffd\uffff¡¿é", ["A\0B \ud800\udc00 \uffff", "\u001f !?~\u007f\u00ff\u011f\u0120"])) })
                await Sample(hosts[100], new(640, 480), label, facts, includeHost: false);
            Check(State(hosts[100]).SelectedWorldNumber == 100 && State(hosts[110]).SelectedWorldNumber == 110,
                "Synthetic display facts cannot replace either host's world or campaign.");
            Complete();

            _group = Required[2];
            hosts[100].View.Visible = true;
            CheckHitBounds(page, hosts[100], nativeStage, views);
            CheckNavigation(hosts[100], 100); CheckNavigation(hosts[110], 110);
            Complete();

            _group = Required[3];
            int edit = 0;
            foreach (string section in new[] { "Body", "Header", "LevelName" })
            {
                Control authored = page.GetNode<Control>(section), old = reference.GetNode<Control>(section);
                Control integrated = hosts[100].View.GetNode<Control>("Stage/MissionBriefing/" + section);
                Vector2 position = authored.Position, extent = authored.Size, scale = authored.Scale; float rotation = authored.Rotation;
                foreach (Control component in new[] { authored, old, integrated })
                {
                    component.Position = position + new Vector2(3.25f + edit, -2.5f);
                    component.Size = extent + new Vector2(7f, 3f);
                    component.Scale = new Vector2(.99f, 1.01f); component.Rotation = .012f;
                }
                await Sample(hosts[100], new(801, 601), "authored-" + section.ToLowerInvariant(), production);
                Check(authored.Position == old.Position && authored.Size == old.Size && authored.Scale == old.Scale && authored.Rotation == old.Rotation,
                    "Frame submission preserves authored section position, size, scale and rotation: " + section);
                foreach (Control component in new[] { authored, old, integrated })
                { component.Position = position; component.Size = extent; component.Scale = scale; component.Rotation = rotation; }
                edit++;
            }
            Node nameLabel = page.GetNode("LevelName/Text"), body = page.GetNode("Body/Text");
            string editorName = nameLabel.Get("text").AsString(); string[] editorParagraphs = body.Get("paragraphs").AsStringArray();
            nameLabel.Set("text", "Explicit enhanced title"); nameLabel.Set("override_text", true);
            string[] overrideBody = ["Explicit enhanced paragraph.", "", "Second explicit paragraph."];
            body.Set("paragraphs", overrideBody); body.Set("override_paragraphs", true);
            Frame enhanced = new("Explicit enhanced title", overrideBody);
            await Sample(hosts[100], new(640, 480), "explicit-editor-overrides", production, includeHost: false, displayed: enhanced);
            CheckSnapshot(page, production);
            nameLabel.Set("override_text", false); nameLabel.Set("text", editorName);
            body.Set("override_paragraphs", false); body.Set("paragraphs", editorParagraphs);
            using (D batch = Facts(production)) Require(page.Call("set_frame", batch));
            reference.SetFrame(production); CheckBody(page, reference);
            Check(nameLabel.Call("displayed_units").AsInt32Array().SequenceEqual(Units(production.SelectedLevelName)), "Disabling enhanced text restores imported level-name facts.");
            // The old section OverrideText fields were not read by this draw;
            // explicit new child overrides are an editor feature, not old behavior.
            Complete();

            _group = Required[4];
            using (D batch = Facts(production))
            {
                batch["unowned_node"] = page; Require(page.Call("set_frame", batch)); batch["level_name"] = new[] { 88 };
                using A paragraphs = batch["paragraphs"].AsGodotArray(); paragraphs[0] = new[] { 89 };
            }
            using (D snapshot = page.Call("view_snapshot").AsGodotDictionary())
            {
                Check(snapshot.Count == 2 && !snapshot.ContainsKey("unowned_node"), "Only the two admitted display fields enter native storage.");
                snapshot["level_name"] = new[] { 90 }; using A paragraphs = snapshot["paragraphs"].AsGodotArray(); paragraphs[0] = new[] { 91 };
            }
            CheckSnapshot(page, production);
            foreach (Control component in new[] { page, hosts[100].View.GetNode<Control>("Stage/MissionBriefing"), hosts[110].View.GetNode<Control>("Stage/MissionBriefing") })
            {
                foreach (Node owner in component.FindChildren("*", "Control", true, false).Prepend(component))
                    Check(!owner.IsProcessing() && !owner.IsProcessingInput() && !owner.IsProcessingUnhandledInput(), "Briefing controls own no clock or input.");
                Check(component.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0 && component.FindChildren("*", "Node3D", true, false).Count == 0,
                    "Briefing has no invented video/audio/world owner.");
            }
            Check(Input.MouseMode == pointer, "Synthetic callbacks leave the physical pointer mode untouched.");
            Check(save.ContainerBytes.SequenceEqual(fixtureBytes), "Verified fixture owner preserves every original save byte.");
            foreach ((string path, string before) in _inputHashes) Check(Hash(path) == before, "Read-only input bytes unchanged: " + path);
            Complete();
            Check(_completed.SequenceEqual(Required) && Required.All(group => _counts.GetValueOrDefault(group) > 0), "Every required group completed.");
            Check(_samples == 16 && _pixels.Count == (_directory is null ? 0 : 27), "All bounded states completed; headless makes no pixel claim.");
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

    private void CheckAssetsAndWrap(Control page, BriefingReference reference, RetailFrontendFlow host)
    {
        foreach ((string name, Texture2D expected, int[] widths) in new[] { ("body_font", reference.BodyFont, reference.BodyWidths), ("title_font", reference.TitleFont, reference.TitleWidths) })
        {
            using Variant returned = page.Get(name); Resource font = returned.As<Resource>();
            using Variant textureValue = font.Get("page"); SameTexture(textureValue.As<Texture2D>(), expected, name);
            Check(font.Call("glyph_widths").AsInt32Array().SequenceEqual(widths), "Every retained atlas glyph width agrees: " + name);
            foreach (string text in new[] { "", "MISSION BRIEFING", "1.00 - Training Level", "1.10 - Blackout", "A\0B\ud800\udc00\ufffd\uffff¡¿é", "\u001f\u0020\u011f\u0120" })
                foreach (float scale in new[] { 1f, .7f, 1.25f })
                    Check(Bits((float)font.Call("measure", Units(text), scale).AsDouble()) == Bits(reference.TextWidth(text, name == "title_font", scale)), "Raw UTF-16 measure retains the original float32 operations.");
        }
        SameTexture(page.GetNode("Background/Rock").Get("texture").As<Texture2D>(), reference.Rock, "rock");
        SameTexture(page.GetNode("Background/Ring").Get("texture").As<Texture2D>(), reference.Ring, "ring");
        SameTexture(page.GetNode("Navigation/Forward").Get("texture").As<Texture2D>(), reference.Arrow, "arrow");
        using Variant shared = host.View.GetNode("Stage/MissionBriefing").Get("body_font"); using Variant existing = host.View.GetNode("Stage/Options").Get("body_font");
        Check(shared.AsGodotObject().GetInstanceId() == existing.AsGodotObject().GetInstanceId(), "The host reuses the admitted body-font recipe.");
        const string ceiling = "Tatiana will take you through the";
        Check(reference.TextWidth(ceiling, false, 1f) == 286f, "The original measured line lies exactly at the retained 286 ceiling.");
        string[][] cases = [[], [""], ["", "", ""], ["First.", "Second."], ["First.", "", "Second."],
            ["   A  B  ", " C\tD E\nF  ", "   "], [new string('W', 80), "short"], [ceiling], [ceiling + " A"],
            ["A\0B \ud800\udc00 \uffff", "\u001f \u011f \u0120"],
            RetailFrontendWorldStrings.Briefing(100).ToArray(), RetailFrontendWorldStrings.Briefing(110).ToArray()];
        foreach (string[] paragraphs in cases)
        {
            var frame = new Frame("Wrap-only display fixture", paragraphs);
            using D facts = Facts(frame); Require(page.Call("set_frame", facts)); reference.SetFrame(frame);
            CheckSnapshot(page, frame); CheckBody(page, reference);
        }
        Check(reference.Wrap([ceiling]).SequenceEqual([ceiling]) && reference.Wrap([ceiling + " A"]).SequenceEqual([ceiling, "A"]),
            "An exactly fitting candidate stays; only a strictly wider candidate wraps.");
        string[] normal = reference.Wrap(RetailFrontendWorldStrings.Briefing(100)); string[] fallback = reference.Wrap([]);
        Check(normal.Length == 8 && !normal.Contains(string.Empty) && fallback.Length == 9 && fallback[6].Length == 0,
            "Executable normal-pair wrapping inserts no gap; the empty-body fallback contains the explicit ninth-entry blank.");
        Require(page.Call("configure_assets"));
    }

    private void CheckFrame(Control page, BriefingReference reference, Frame facts, Frame displayed)
    {
        CheckSnapshot(page, facts);
        foreach ((string name, Rect2 measured) in BriefingReference.Sections)
        {
            Control part = page.GetNode<Control>(name), old = reference.GetNode<Control>(name);
            Check(part.Position == old.Position && part.Size == old.Size && part.Scale == old.Scale && part.Rotation == old.Rotation, "Original authored section frame: " + name);
            Check(part.GetGlobalTransformWithCanvas() == old.GetGlobalTransformWithCanvas(), "Actual canvas frame agrees: " + name);
        }
        foreach (string path in Passes)
        {
            Control pass = page.GetNode<Control>(path), old = reference.GetNode<Control>(path.Split('/')[0]);
            Check(pass.Get("source_rect").AsRect2() == BriefingReference.Sections[old.Name.ToString()], "Original measured source frame: " + path);
            Check(pass.Call("source_transform").AsTransform2D() == BriefingReference.SourceTransform(old), "Source-to-section transform agrees: " + path);
            Check(pass.GetGlobalTransformWithCanvas() == old.GetGlobalTransformWithCanvas(), "Original canvas grouping: " + path);
        }
        foreach ((string path, string text, Vector2 origin, Vector2 scale) in new[] {
            ("Header/Title", "MISSION BRIEFING", reference.HeaderOrigin, Vector2.One),
            ("LevelName/Text", displayed.SelectedLevelName, new Vector2(178.5f, 118), new Vector2(.7f, 1f)) })
        {
            Node label = page.GetNode(path);
            Check(label.Call("displayed_units").AsInt32Array().SequenceEqual(Units(text)), "Raw UTF-16 title/name run: " + path);
            Check(label.Call("drawing_origin").AsVector2() == origin && label.Get("glyph_scale").AsVector2() == scale, "Original title/name origin and nonuniform level-name scale: " + path);
            Check(Bits((float)label.Call("font_width").AsDouble()) == Bits(reference.TextWidth(text, true, scale.X)), "Original run width: " + path);
            Check(label.Call("drawing_color").AsColor() == BriefingReference.TextTint && label.Get("shadow").AsBool() && !label.Get("name_glyphs").AsBool(), "Original title/name tint and ordinary glyph mapping: " + path);
        }
        CheckBody(page, reference);
        foreach ((string path, Rect2 expected, Color ink) in new[] {
            ("Background/Rock", reference.RockRect, BriefingReference.RockTint),
            ("Background/Ring", reference.RingRect, BriefingReference.RingTint),
            ("Header/Panel", new Rect2(191, 69, 394, 21), new Color(0, 0, 0, .5f)),
            ("Navigation/Back", new Rect2(9, 438, -28, 36), BriefingReference.ArrowTint),
            ("Navigation/Forward", new Rect2(604, 437, 28, 36), BriefingReference.ArrowTint) })
        {
            Node pass = page.GetNode(path);
            Check(pass.Call("drawing_rect").AsRect2() == expected && pass.Get("ink_color").AsColor() == ink, "Original background/header/arrow geometry and tint: " + path);
        }
        foreach (string path in new[] { "Navigation/Back", "Navigation/Forward" })
            Check(page.GetNode(path).Get("region").AsRect2() == new Rect2(16, 12, 30, 40), "Original arrow crop: " + path);
    }

    private void CheckBody(Control page, BriefingReference reference)
    {
        Node body = page.GetNode("Body/Text");
        using A wrapped = body.Call("wrap_lines").AsGodotArray(); using A layout = body.Call("layout_snapshot").AsGodotArray();
        var expected = reference.Layout();
        Check(wrapped.Count == expected.Length && layout.Count == expected.Length, "Wrapped-line and layout counts retain the executable fallback/empty-token rules.");
        using Variant fontValue = body.Get("atlas_font"); Resource font = fontValue.As<Resource>();
        for (int index = 0; index < expected.Length; index++)
        {
            var row = expected[index]; using D actual = layout[index].AsGodotDictionary();
            Check(wrapped[index].AsInt32Array().SequenceEqual(Units(row.Text)) && actual["units"].AsInt32Array().SequenceEqual(Units(row.Text)), "Exact wrapped raw UTF-16 line order.");
            Vector2 origin = actual["origin"].AsVector2();
            Check(Bits(origin.X) == Bits(80f) && Bits(origin.Y) == Bits(row.Y) && actual["draw"].AsBool() == row.Drawn,
                "Original float32 line origin, 16px pitch and explicit 10px blank gap.");
            Check(Bits((float)font.Call("measure", actual["units"], 1f).AsDouble()) == Bits(row.Width), "Exact width of every wrapped line, including overlong unsplit words.");
        }
        Check(body.Get("ink_color").AsColor() == BriefingReference.BodyTint && Bits((float)body.Get("wrap_ceiling").AsDouble()) == Bits(286f)
            && Bits((float)body.Get("line_pitch").AsDouble()) == Bits(16f) && Bits((float)body.Get("paragraph_gap").AsDouble()) == Bits(10f),
            "Existing body tint and wrapping/layout laws remain unchanged.");
    }

    private void CheckHitBounds(Control page, RetailFrontendFlow host, Control stage, IReadOnlyList<SubViewport> views)
    {
        foreach (Vector2I size in Sizes.Append(new(1024, 768)))
        {
            foreach (SubViewport view in views) view.Size = size; host.View.Size = size; Fit(stage, size);
            foreach (Rect2 rect in new[] { new Rect2(0, 430, 48, 48), new Rect2(595, 430, 45, 48) })
            {
                float cx = rect.Position.X + rect.Size.X * .5f, cy = rect.Position.Y + rect.Size.Y * .5f;
                IEnumerable<Vector2> points = new[] { rect.Position.X, rect.End.X }.SelectMany(x => new[] { MathF.BitDecrement(x), x, MathF.BitIncrement(x) }).Select(x => new Vector2(x, cy))
                    .Concat(new[] { rect.Position.Y, rect.End.Y }.SelectMany(y => new[] { MathF.BitDecrement(y), y, MathF.BitIncrement(y) }).Select(y => new Vector2(cx, y)));
                foreach (Vector2 point in points)
                {
                    int expected = BriefingReference.HitTest(point);
                    Check(page.Call("hit_test", point).AsInt32() == expected && FrontendHarnessChecks.Hit(host, "briefing_target_at", point) == expected,
                        "Native and host preserve exact half-open design-space hits without a Stage roundtrip.");
                }
            }
            Check(page.Call("hit_test", new Vector2(200, 200)).AsInt32() == 0, "Briefing text remains display-only.");
        }
    }

    private void CheckNavigation(RetailFrontendFlow host, int world)
    {
        host.View.Size = new(640, 480); var effects = new List<string>(); int loads = 0, starts = 0, activations = 0, exits = 0;
        void Audio(RetailFrontendAudioCue cue) => effects.Add("audio:" + cue);
        void Cursor(RetailFrontendCursorMode mode) => effects.Add("cursor:" + mode);
        void Load() => loads++; void Start() => starts++; void Activated() => activations++; void Exit() => exits++;
        host.AudioCueRequested += Audio; host.CursorModeRequested += Cursor; host.Level100LoadRequested += Load;
        host.Level100LoadingStarted += Start; host.GameplayActivated += Activated; host.ExitRequested += Exit;
        try
        {
            foreach (Godot.Key key in new[] { Godot.Key.Up, Godot.Key.Down, Godot.Key.Left, Godot.Key.Right }) Key(host, key);
            Key(host, Godot.Key.Enter, echo: true); Click(host, new(48, 450)); Click(host, new(600, 478)); Click(host, new(200, 200));
            Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing && State(host).SelectedWorldNumber == world && effects.Count == 0,
                "Briefing ignores selection keys, echo, excluded edges and text clicks.");
            foreach (bool pointer in new[] { false, true })
            {
                effects.Clear(); if (pointer) Click(host, new(0, 430)); else Key(host, Godot.Key.Escape);
                Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect && effects.SequenceEqual(new[] { "audio:Back", "cursor:Custom" }) && State(host).SelectedWorldNumber == world,
                    "Back returns to Level Select with the same selected world and original callback order.");
                effects.Clear(); host.ConfirmForSmoke();
                Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "The existing selected world re-enters Briefing.");
                effects.Clear(); if (pointer) Click(host, new(595, 430)); else Key(host, Godot.Key.Enter);
                Check(host.CurrentScreen == RetailFrontendScreen.SelectConfiguration && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }) && State(host).SelectedWorldNumber == world,
                    "Forward reaches Configuration and preserves selected-world ownership.");
                Check(starts == 0 && loads == 0 && activations == 0 && exits == 0 && !State(host).ConsumeLevel100LaunchRequest(),
                    "Briefing confirmation has not queued or performed a gameplay load.");
                Key(host, Godot.Key.Escape);
                Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing, "Existing Configuration Back restores the same Briefing.");
            }
        }
        finally
        {
            host.AudioCueRequested -= Audio; host.CursorModeRequested -= Cursor; host.Level100LoadRequested -= Load;
            host.Level100LoadingStarted -= Start; host.GameplayActivated -= Activated; host.ExitRequested -= Exit;
        }
    }

    private void EnterBriefing(RetailFrontendFlow host, int world, RetailCareerDescriptor? suppliedCareer)
    {
        host.ConfirmForSmoke(); Check(host.CurrentScreen == RetailFrontendScreen.MainMenu, "Cold frontend enters Main Menu.");
        SetField(host, "_main_transition_time", 0); SetField(host, "_main_transition_count", 0);
        host.SelectMainIndexForCapture(world == 100 ? 0 : 2); host.ConfirmForSmoke();
        Check(host.CurrentScreen == RetailFrontendScreen.DevSelect, "Existing New or verified Load route enters Career Name.");
        if (world != 100)
        {
            Check(State(host).CareerPageMode == RetailFrontendCareerPageMode.Load && State(host).SelectedCareerIndex == -1,
                "The existing Load page starts with no implicitly selected career.");
            Key(host, Godot.Key.Down);
            Check(State(host).SelectedCareerIndex == 0, "Actual Down input selects the supplied read-only fixture before Load confirmation.");
        }
        RetailCareerDescriptor? selected = null; int selections = 0;
        void Selected(RetailCareerDescriptor descriptor) { selected = descriptor; selections++; }
        host.CareerSelected += Selected;
        try { host.ConfirmForSmoke(); }
        finally { host.CareerSelected -= Selected; }
        Check(host.CurrentScreen == RetailFrontendScreen.LevelSelect, "Existing career route reaches Level Select.");
        Check(suppliedCareer is null ? selections == 0 : selections == 1 && selected is not null
            && ReferenceEquals(selected, suppliedCareer) && ReferenceEquals(selected.Career, suppliedCareer.Career),
            "Load hands the exact supplied descriptor and verified save to CareerSelected once; New emits no save handoff.");
        if (State(host).SelectedWorldNumber != world) Check(State(host).SelectWorld(world), "Verified campaign admits the requested existing world.");
        host.ConfirmForSmoke();
        Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing && State(host).SelectedWorldNumber == world
            && State(host).SelectedLevelName == RetailFrontendWorldStrings.LevelName(world)
            && State(host).SelectedBriefingBody.SequenceEqual(RetailFrontendWorldStrings.Briefing(world)), "Live host displays the selected world's actual frozen localized definitions.");
    }
    private void CheckSnapshot(Control page, Frame frame)
    {
        using D actual = page.Call("view_snapshot").AsGodotDictionary(); using A paragraphs = actual["paragraphs"].AsGodotArray();
        Check(actual.Count == 2 && actual["level_name"].AsInt32Array().SequenceEqual(Units(frame.SelectedLevelName)), "Detached frame retains only its raw level name and supplied paragraphs.");
        Check(paragraphs.Count == frame.SelectedBriefingBody.Count, "Fallback text is drawn without replacing the supplied empty paragraph list.");
        for (int index = 0; index < paragraphs.Count; index++) Check(paragraphs[index].AsInt32Array().SequenceEqual(Units(frame.SelectedBriefingBody[index])), "Detached paragraph order and raw UTF-16 remain unchanged.");
    }
    private static D Facts(Frame frame)
    {
        using A paragraphs = new(); foreach (string paragraph in frame.SelectedBriefingBody) paragraphs.Add(Units(paragraph));
        return new() { ["level_name"] = Units(frame.SelectedLevelName), ["paragraphs"] = paragraphs };
    }
    private static Frame ReadFrame(RetailFrontendFlow host) => new(State(host).SelectedLevelName, State(host).SelectedBriefingBody);
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
            if (returned.VariantType != Variant.Type.Dictionary) throw new InvalidDataException("Native briefing presentation returned no result.");
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
        foreach (string path in new[] { Fixture, "res://Assets/Frontend/Backgrounds/rock.texture.aya", "res://Assets/Frontend/level-bracket-02.texture.aya",
            "res://Assets/Frontend/fe-arrow.texture.aya", "res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya",
            "res://Assets/Frontend/english.json", "res://Assets/Frontend/english-worlds.json" }) _inputHashes.Add(path, Hash(path));
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
        GD.Print("BRIEFING_SCENE_CHECKS: " + JsonSerializer.Serialize(new { schema = 1, checks = _checks, samples = _samples,
            completed = _completed, counts = _counts, rendered = _directory is not null, pixels = _pixels,
            reference_revision = "51477f62", input_sha256 = _inputHashes,
            failure_count = error is null ? 0 : 1, error }));
    }
}
