// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Actual Select Configuration components and live host compared with the
/// retained 7474445c renderer. Synthetic text is display-only; the host keeps
/// its one admitted configuration. This is conversion equivalence, not a new
/// retail-parity claim for the missing model/icons/stars or static-background fit.
/// No saves, gameplay world, physical input or visible desktop are used.
/// </summary>
public sealed partial class ConfigurationSceneChecks : Node
{
    private static readonly string[] Required = ["production_assets_and_glyphs", "frames_and_host", "hit_bounds_and_navigation", "authored_sections", "read_only_and_ownership"];
    private static readonly string[] Passes = ["Background/Rock", "Background/Ring", "Header/Panel", "Header/Title", "Unit/Name",
        "Walker/Title", "Walker/Primary", "Walker/Secondary", "Jet/Title", "Jet/Primary", "Jet/Secondary", "Navigation/Back", "Navigation/Forward"];
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
            const string prefix = "--configuration-render-dir=";
            string[] supplied = arguments.Where(value => value.StartsWith(prefix, StringComparison.Ordinal)).ToArray();
            Check(supplied.Length <= 1, "Only one explicit render directory is admitted.");
            _directory = supplied.SingleOrDefault()?[prefix.Length..];
            if (_directory is not null)
            {
                RequireOwnedDirectory(_directory);
                Check(DisplayServer.GetName() != "headless", "Pixel comparison requires the caller's isolated rendered display.");
            }
            else Check(DisplayServer.GetName() == "headless", "Unrecorded visible runs are outside this harness.");
            GetTree().CreateTimer(120d).Timeout += () =>
            {
                if (_finished) return;
                Report("Configuration comparison did not complete every required group before its bounded timeout.");
                GetTree().Quit(1);
            };
            Input.MouseModeEnum pointer = Input.MouseMode;
            RecordInputs();
            SubViewport nativeView = MakeViewport(), referenceView = MakeViewport(), hostView = MakeViewport();
            views.AddRange([nativeView, referenceView, hostView]);
            Control nativeStage = MakeStage(nativeView), referenceStage = MakeStage(referenceView);
            Control page = GD.Load<PackedScene>("res://Scenes/Frontend/SelectConfiguration.tscn").Instantiate<Control>();
            foreach (string section in ConfigurationReference.Sections.Keys)
                Check(page.GetNodeOrNull<Control>(section) is not null, "Authored production section exists before Play: " + section);
            nativeStage.AddChild(page);
            ConfigurationReference reference = GD.Load<PackedScene>("res://Scenes/Frontend/Tests/ConfigurationReference.tscn").Instantiate<ConfigurationReference>();
            referenceStage.AddChild(reference);
            RetailFrontendFlow host = RetailFrontendFlow.InstantiateScene(); facades.Add(host);
            host.Initialize([]); hostView.AddChild(host.View);
            host.View.SetProcess(false); host.View.SetProcessInput(false);
            host.SetMouseCursorDesignPositionForCapture(new Vector2(-100f, -100f));
            EnterConfiguration(host);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Require(page.Call("configure_assets"));
            CheckAssetsAndGlyphs(page, reference, host); Complete();

            _group = Required[1];
            RetailFrontendBattleEngineConfiguration production = State(host).SelectedConfiguration;
            async Task Sample(Vector2I size, string label, RetailFrontendBattleEngineConfiguration facts,
                bool includeHost = true, RetailFrontendBattleEngineConfiguration? displayed = null)
            {
                foreach (SubViewport viewport in views) viewport.Size = size;
                Fit(nativeStage, size); Fit(referenceStage, size); host.View.Size = size; host.View.Visible = includeHost;
                using D batch = Facts(facts); Require(page.Call("set_frame", batch));
                reference.SetFrame(displayed ?? facts);
                if (includeHost) host.SelectMainIndexForCapture(0); // Queues the current page without changing its selection.
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                CheckFrame(page, reference, facts, displayed ?? facts);
                if (includeHost) CheckFrame(host.View.GetNode<Control>("Stage/SelectConfiguration"), reference, production, production);
                if (_directory is not null) await ComparePixels(nativeView, referenceView, includeHost ? hostView : null, label);
                _samples++;
            }
            foreach (Vector2I size in Sizes) await Sample(size, $"{size.X}x{size.Y}-production", production);
            foreach ((string label, string text) in new[] { ("empty", ""), ("raw-utf16", "A\0B\ud800\udc00\ufffd\uffff¡¿é"),
                ("atlas-boundaries", "\u001f !?~\u007f\u00ff\u011f\u0120") })
            {
                RetailFrontendBattleEngineConfiguration display = WithText(production, text);
                await Sample(new(640, 480), label, display, includeHost: false);
                Check(State(host).SelectedConfiguration == production && State(host).ConfigurationCount == 1,
                    "Synthetic display facts do not add a selectable host configuration.");
            }
            Complete();

            _group = Required[2];
            host.View.Visible = true;
            CheckHitBounds(page, host, nativeStage, views);
            CheckNavigation(host);
            EnterConfiguration(host); host.View.SetProcess(false); host.View.SetProcessInput(false);
            Complete();

            _group = Required[3];
            int edit = 0;
            foreach (string section in new[] { "Background", "Header", "Walker" })
            {
                Control authored = page.GetNode<Control>(section), old = reference.GetNode<Control>(section);
                Control integrated = host.View.GetNode<Control>("Stage/SelectConfiguration/" + section);
                Vector2 position = authored.Position, extent = authored.Size, scale = authored.Scale; float rotation = authored.Rotation;
                foreach (Control component in new[] { authored, old, integrated })
                {
                    component.Position = position + new Vector2(3.25f + edit, -2.5f);
                    component.Size = extent + new Vector2(7f, 3f);
                    component.Scale = new Vector2(.99f, 1.01f); component.Rotation = .012f;
                }
                await Sample(new(801, 601), "authored-" + section.ToLowerInvariant(), production);
                Check(authored.Position == old.Position && authored.Size == old.Size && authored.Scale == old.Scale && authored.Rotation == old.Rotation,
                    "Submitting a frame retains ordinary authored section edits: " + section);
                foreach (Control component in new[] { authored, old, integrated })
                { component.Position = position; component.Size = extent; component.Scale = scale; component.Rotation = rotation; }
                edit++;
            }
            Node unitLabel = page.GetNode("Unit/Name");
            string importedEditorText = unitLabel.Get("text").AsString();
            unitLabel.Set("text", "Explicit editor override"); unitLabel.Set("override_text", true);
            await Sample(new(640, 480), "explicit-unit-override", production, includeHost: false,
                displayed: production with { DisplayName = "Explicit editor override" });
            CheckSnapshot(page, production);
            unitLabel.Set("override_text", false); unitLabel.Set("text", importedEditorText);
            using (D batch = Facts(production)) Require(page.Call("set_frame", batch));
            Check(unitLabel.Call("displayed_units").AsInt32Array().SequenceEqual(Units(production.DisplayName)),
                "Disabling the explicit editor override restores imported text without rewriting facts.");
            // The old section OverrideText fields were inert for Configuration;
            // this explicit child-label feature is not claimed as old behavior.
            Complete();

            _group = Required[4];
            using (D batch = Facts(production))
            {
                batch["unowned_node"] = page; Require(page.Call("set_frame", batch)); batch["unit_name"] = new[] { 88 };
            }
            using (D snapshot = page.Call("view_snapshot").AsGodotDictionary())
            {
                Check(snapshot.Count == 5 && !snapshot.ContainsKey("unowned_node"), "Only the five admitted display fields enter native storage.");
                int[] units = snapshot["walker_primary"].AsInt32Array(); units[0] = 89;
                snapshot["walker_primary"] = units; snapshot["unit_name"] = new[] { 90 };
            }
            CheckSnapshot(page, production);
            foreach (Control component in new[] { page, host.View.GetNode<Control>("Stage/SelectConfiguration") })
            {
                foreach (Node owner in component.FindChildren("*", "Control", true, false).Prepend(component))
                    Check(!owner.IsProcessing() && !owner.IsProcessingInput() && !owner.IsProcessingUnhandledInput(), "Configuration controls own no clock or input.");
                Check(component.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0 && component.FindChildren("*", "Node3D", true, false).Count == 0,
                    "Configuration remains presentation only; no missing model or audio owner is invented.");
            }
            Check(Input.MouseMode == pointer, "Synthetic host callbacks never change physical pointer mode.");
            foreach ((string path, string before) in _inputHashes) Check(Hash(path) == before, "Read-only input bytes unchanged: " + path);
            Complete();
            Check(_completed.SequenceEqual(Required) && Required.All(group => _counts.GetValueOrDefault(group) > 0), "Every required group completed.");
            Check(_samples == 11 && _pixels.Count == (_directory is null ? 0 : 18), "All bounded states completed; headless makes no pixel claim.");
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

    private void CheckAssetsAndGlyphs(Control page, ConfigurationReference reference, RetailFrontendFlow host)
    {
        foreach ((string name, Texture2D expected, int[] widths) in new[] { ("body_font", reference.BodyFont, reference.BodyWidths), ("title_font", reference.TitleFont, reference.TitleWidths) })
        {
            using Variant fontValue = page.Get(name); Resource font = fontValue.As<Resource>();
            using Variant textureValue = font.Get("page"); SameTexture(textureValue.As<Texture2D>(), expected, name);
            Check(font.Call("glyph_widths").AsInt32Array().SequenceEqual(widths), "Every retained atlas glyph width agrees: " + name);
            foreach (string text in new[] { "", "SELECT CONFIGURATION", "Walker Mode", "Jet Mode", "Pulse Cannon", "A\0B\ud800\udc00\ufffd\uffff¡¿é", "\u001f\u0020\u011f\u0120" })
                foreach (float scale in new[] { 1f, .7f, 1.25f })
                    Check(Bits((float)font.Call("measure", Units(text), scale).AsDouble()) == Bits(reference.TextWidth(text, name == "title_font", scale)),
                        "Raw UTF-16 atlas measurement retains the original float32 operation order.");
        }
        SameTexture(page.GetNode("Background/Rock").Get("texture").As<Texture2D>(), reference.Rock, "rock");
        SameTexture(page.GetNode("Background/Ring").Get("texture").As<Texture2D>(), reference.Ring, "ring");
        SameTexture(page.GetNode("Navigation/Forward").Get("texture").As<Texture2D>(), reference.Arrow, "arrow");
        using Variant shared = host.View.GetNode("Stage/SelectConfiguration").Get("body_font");
        using Variant existing = host.View.GetNode("Stage/Options").Get("body_font");
        Check(shared.AsGodotObject().GetInstanceId() == existing.AsGodotObject().GetInstanceId(), "Live host reuses the admitted body font resource.");
        Require(page.Call("configure_assets"));
        Check(State(host).ConfigurationCount == 1 && State(host).SelectedConfigurationIndex == 0
            && State(host).SelectedConfiguration == new RetailFrontendSession().SelectedConfiguration, "The one released configuration and authored identities remain unchanged.");
    }

    private void CheckFrame(Control page, ConfigurationReference reference, RetailFrontendBattleEngineConfiguration facts, RetailFrontendBattleEngineConfiguration displayed)
    {
        CheckSnapshot(page, facts);
        foreach ((string name, Rect2 measured) in ConfigurationReference.Sections)
        {
            Control part = page.GetNode<Control>(name), old = reference.GetNode<Control>(name);
            Check(part.Position == old.Position && part.Size == old.Size && part.Scale == old.Scale && part.Rotation == old.Rotation, "Original authored section frame: " + name);
            Check(part.GetGlobalTransformWithCanvas() == old.GetGlobalTransformWithCanvas(), "Actual canvas frame agrees: " + name);
        }
        foreach (string path in Passes)
        {
            Control pass = page.GetNode<Control>(path), old = reference.GetNode<Control>(path.Split('/')[0]);
            Check(pass.Get("source_rect").AsRect2() == ConfigurationReference.Sections[old.Name.ToString()], "Original measured source frame: " + path);
            Check(pass.Call("source_transform").AsTransform2D() == ConfigurationReference.SourceTransform(old), "Source-to-section transform agrees: " + path);
            Check(pass.GetGlobalTransformWithCanvas() == old.GetGlobalTransformWithCanvas(), "Draw pass retains original canvas grouping: " + path);
        }
        foreach ((string path, string text, Vector2 origin, bool title, bool mode) in new[] {
            ("Header/Title", "SELECT CONFIGURATION", reference.HeaderOrigin, true, false),
            ("Unit/Name", displayed.DisplayName, new Vector2(260.5f, 99.5f), true, false),
            ("Walker/Title", "Walker Mode", new Vector2(280, 210), false, true),
            ("Walker/Primary", displayed.WalkerPrimary.DisplayName, new Vector2(280, 226), false, false),
            ("Walker/Secondary", displayed.WalkerSecondary.DisplayName, new Vector2(280, 242), false, false),
            ("Jet/Title", "Jet Mode", new Vector2(280, 274), false, true),
            ("Jet/Primary", displayed.JetPrimary.DisplayName, new Vector2(280, 290), false, false),
            ("Jet/Secondary", displayed.JetSecondary.DisplayName, new Vector2(280, 306), false, false) })
        {
            Node label = page.GetNode(path);
            Check(label.Call("displayed_units").AsInt32Array().SequenceEqual(Units(text)), "Original raw UTF-16 run: " + path);
            Check(label.Call("drawing_origin").AsVector2() == origin && label.Get("glyph_scale").AsVector2() == Vector2.One, "Original glyph origin and scale: " + path);
            Check(Bits((float)label.Call("font_width").AsDouble()) == Bits(reference.TextWidth(text, title, 1f)), "Original measured run width: " + path);
            Check(label.Call("drawing_color").AsColor() == (mode ? ConfigurationReference.ModeTint : ConfigurationReference.TextTint)
                && label.Get("shadow").AsBool() && !label.Get("name_glyphs").AsBool(), "Original tint, shadow and ordinary glyph mapping: " + path);
        }
        foreach ((string path, Rect2 expected, Color ink) in new[] {
            ("Background/Rock", reference.RockRect, ConfigurationReference.RockTint),
            ("Background/Ring", reference.RingRect, ConfigurationReference.RingTint),
            ("Header/Panel", new Rect2(191, 69, 394, 21), new Color(0, 0, 0, .5f)),
            ("Navigation/Back", new Rect2(9, 438, -28, 36), ConfigurationReference.ArrowTint),
            ("Navigation/Forward", new Rect2(604, 437, 28, 36), ConfigurationReference.ArrowTint) })
        {
            Node pass = page.GetNode(path);
            Check(pass.Call("drawing_rect").AsRect2() == expected && pass.Get("ink_color").AsColor() == ink,
                "Original rectangle and raw float tint, including unclamped ring gain: " + path);
        }
        Check(page.GetNode("Navigation/Back").Get("region").AsRect2() == new Rect2(16, 12, 30, 40)
            && page.GetNode("Navigation/Forward").Get("region").AsRect2() == new Rect2(16, 12, 30, 40), "Original arrow atlas crop is unchanged.");
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
                    int expected = ConfigurationReference.HitTest(point);
                    Check(page.Call("hit_test", point).AsInt32() == expected && FrontendHarnessChecks.Hit(host, "configuration_target_at", point) == expected,
                        "Native and actual host preserve half-open design targets without another Stage roundtrip.");
                }
            }
            Check(page.Call("hit_test", new Vector2(280, 230)).AsInt32() == 0, "Weapon rows remain display-only.");
        }
    }

    private void CheckNavigation(RetailFrontendFlow host)
    {
        host.View.Size = new(640, 480); var effects = new List<string>(); int exits = 0;
        void Audio(RetailFrontendAudioCue cue) => effects.Add("audio:" + cue);
        void Cursor(RetailFrontendCursorMode mode) => effects.Add("cursor:" + mode);
        void Started() => effects.Add("loading");
        void Load() { effects.Add("load"); Check(host.LaunchWorldNumber == 100, "Existing launch carries Level 100."); host.MarkLevel100Ready(); }
        void Gameplay() => effects.Add("gameplay");
        void Exit() => exits++;
        host.AudioCueRequested += Audio; host.CursorModeRequested += Cursor; host.Level100LoadingStarted += Started;
        host.Level100LoadRequested += Load; host.GameplayActivated += Gameplay; host.ExitRequested += Exit;
        try
        {
            Check(!State(host).SelectConfigurationIndex(-1) && !State(host).SelectConfigurationIndex(1) && !State(host).SelectConfigurationIndex(0),
                "The sole configuration cannot change to an invalid or identical index.");
            foreach (Godot.Key key in new[] { Godot.Key.Up, Godot.Key.Down, Godot.Key.Left, Godot.Key.Right }) Key(host, key);
            Key(host, Godot.Key.Enter, echo: true); Click(host, new(48, 450)); Click(host, new(600, 478)); Click(host, new(280, 230));
            Check(host.CurrentScreen == RetailFrontendScreen.SelectConfiguration && State(host).SelectedConfigurationIndex == 0 && effects.Count == 0,
                "No extra configuration, echo confirmation, excluded-boundary click or weapon-row action is invented.");
            Key(host, Godot.Key.Escape);
            Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing && effects.SequenceEqual(new[] { "audio:Back", "cursor:Custom" }), "Keyboard back preserves callback order.");
            effects.Clear(); Click(host, new(595, 430));
            Check(host.CurrentScreen == RetailFrontendScreen.SelectConfiguration && effects.SequenceEqual(new[] { "audio:Select", "cursor:Custom" }), "Briefing forward re-enters the same configuration.");
            effects.Clear(); Click(host, new(0, 430));
            Check(host.CurrentScreen == RetailFrontendScreen.MissionBriefing && effects.SequenceEqual(new[] { "audio:Back", "cursor:Custom" }), "Configuration back chevron preserves callback order.");
            Key(host, Godot.Key.Enter);
            foreach (bool pointer in new[] { false, true })
            {
                effects.Clear();
                if (pointer) Click(host, new(595, 430)); else Key(host, Godot.Key.Enter);
                Check(host.CurrentScreen == RetailFrontendScreen.Loading && effects.SequenceEqual(new[] { "audio:Select", "loading", "cursor:Hidden" }),
                    "Configuration confirm emits Select, loading-start, then hidden cursor before any load.");
                FrontendHarnessChecks.Command(host, "advance", 0d);
                Check(host.CurrentScreen == RetailFrontendScreen.Loading && effects.Count == 3, "The first loading frame never raises the construction edge.");
                FrontendHarnessChecks.Command(host, "advance", 0d);
                Check(host.CurrentScreen == RetailFrontendScreen.Gameplay && effects.SequenceEqual(new[] { "audio:Select", "loading", "cursor:Hidden", "load", "cursor:Captured", "gameplay" }),
                    "The second loading frame consumes the edge and invokes the ready handoff in its original order.");
                FrontendHarnessChecks.Command(host, "advance", 0d);
                Check(effects.Count == 6 && !State(host).ConsumeLevel100LaunchRequest(), "Load and gameplay edges fire exactly once.");
                host.LeaveLevel100ForMainMenu(); host.View.SetProcess(false); host.View.SetProcessInput(false);
                EnterConfiguration(host);
            }
            Check(exits == 0, "No configuration path requests window quit.");
        }
        finally
        {
            host.AudioCueRequested -= Audio; host.CursorModeRequested -= Cursor; host.Level100LoadingStarted -= Started;
            host.Level100LoadRequested -= Load; host.GameplayActivated -= Gameplay; host.ExitRequested -= Exit;
        }
    }

    private void EnterConfiguration(RetailFrontendFlow host)
    {
        if (host.CurrentScreen == RetailFrontendScreen.SelectConfiguration) return;
        if (host.CurrentScreen == RetailFrontendScreen.ClickToStart) host.ConfirmForSmoke();
        Check(host.CurrentScreen == RetailFrontendScreen.MainMenu, "Configuration route begins at the actual Main Menu.");
        SetField(host, "_main_transition_time", 0); SetField(host, "_main_transition_count", 0);
        host.SelectMainIndexForCapture(0);
        foreach (RetailFrontendScreen screen in new[] { RetailFrontendScreen.DevSelect, RetailFrontendScreen.LevelSelect, RetailFrontendScreen.MissionBriefing, RetailFrontendScreen.SelectConfiguration })
        { host.ConfirmForSmoke(); Check(host.CurrentScreen == screen, "Original New-to-configuration route: " + screen); }
    }
    private void CheckSnapshot(Control page, RetailFrontendBattleEngineConfiguration configuration)
    {
        using D expected = Facts(configuration); using D actual = page.Call("view_snapshot").AsGodotDictionary();
        Check(actual.Count == expected.Count, "Detached display frame has exactly five fields.");
        foreach (Variant key in expected.Keys) Check(actual[key].AsInt32Array().SequenceEqual(expected[key].AsInt32Array()), "Detached raw UTF-16 field agrees: " + key.AsString());
    }
    private static D Facts(RetailFrontendBattleEngineConfiguration value) => new() {
        ["unit_name"] = Units(value.DisplayName), ["walker_primary"] = Units(value.WalkerPrimary.DisplayName),
        ["walker_secondary"] = Units(value.WalkerSecondary.DisplayName), ["jet_primary"] = Units(value.JetPrimary.DisplayName), ["jet_secondary"] = Units(value.JetSecondary.DisplayName) };
    private static RetailFrontendBattleEngineConfiguration WithText(RetailFrontendBattleEngineConfiguration value, string text) => value with {
        DisplayName = text, WalkerPrimary = value.WalkerPrimary with { DisplayName = text }, WalkerSecondary = value.WalkerSecondary with { DisplayName = text },
        JetPrimary = value.JetPrimary with { DisplayName = text }, JetSecondary = value.JetSecondary with { DisplayName = text } };
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
            if (returned.VariantType != Variant.Type.Dictionary) throw new InvalidDataException("Native configuration presentation returned no result.");
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
        foreach (string path in new[] { "res://Assets/Frontend/Backgrounds/rock.texture.aya", "res://Assets/Frontend/level-bracket-02.texture.aya",
            "res://Assets/Frontend/fe-arrow.texture.aya", "res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya",
            "res://Assets/Frontend/english.json" }) _inputHashes.Add(path, Hash(path));
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
        GD.Print("CONFIGURATION_SCENE_CHECKS: " + JsonSerializer.Serialize(new { schema = 1, checks = _checks, samples = _samples,
            completed = _completed, counts = _counts, rendered = _directory is not null, pixels = _pixels,
            reference_revision = "7474445c", input_sha256 = _inputHashes,
            failure_count = error is null ? 0 : 1, error }));
    }
}
