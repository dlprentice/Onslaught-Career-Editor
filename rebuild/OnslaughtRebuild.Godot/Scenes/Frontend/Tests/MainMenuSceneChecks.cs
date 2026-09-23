// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;
namespace OnslaughtRebuild.GodotClient;

/// <summary>Actual native page and integrated frontend versus the retained
/// original authored Main Menu. Rendering requires the caller's isolated
/// display; all outputs are fresh and contained in its worktree local-data.</summary>
public sealed partial class MainMenuSceneChecks : Node
{
    private int _checks, _samples;
    private readonly List<string> _completed = [];
    private readonly List<object> _pixels = [];
    private readonly Dictionary<string, string> _inputHashes = new(StringComparer.Ordinal);
    private string? _directory;

    public override async void _Ready()
    {
        List<SubViewport> views = [];
        List<RetailFrontendFlow> facades = [];
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Contains("--skipfmv", StringComparer.Ordinal), "Focused checks require --skipfmv.");
            const string prefix = "--main-menu-render-dir=";
            _directory = args.FirstOrDefault(value => value.StartsWith(prefix, StringComparison.Ordinal))?[prefix.Length..];
            if (_directory is not null)
            {
                RequireOwnedDirectory(_directory);
                Check(DisplayServer.GetName() != "headless", "Pixels require the caller's isolated display.");
            }
            Input.MouseModeEnum pointer = Input.MouseMode;
            foreach (string name in new[] { "forseti-writing-large", "fe-arrow", "title-text-box", "title-logo", "reflection-map", "title-bracket-01", "title-bracket-02", "symbol-bracket-01", "symbol-bracket-02",
                "Flags/flag-uk", "Flags/flag-fr", "Flags/flag-gr", "Flags/flag-it", "Flags/flag-sp", "Icons/new-game", "Icons/continue-game", "Icons/load-game", "Icons/multiplayer", "Icons/goodies", "Icons/options", "Icons/quit" })
                Record("res://Assets/Frontend/" + name + ".texture.aya");
            Record("res://Assets/Hud/font-13ps.texture.aya"); Record("res://Assets/Frontend/english.json"); Record("res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb");
            SubViewport nativeViewport = MakeViewport(), referenceViewport = MakeViewport(), hostViewport = MakeViewport();
            views.AddRange([nativeViewport, referenceViewport, hostViewport]);
            Control stage = MakeStage(nativeViewport);
            Control page = GD.Load<PackedScene>("res://Scenes/Frontend/MainMenu.tscn").Instantiate<Control>();
            Check(page.GetNode("Decoration/Left").GetChildCount() == 2 && page.GetNode("Decoration/RightTwin").GetChildCount() == 2,
                "All four body/shadow arc pairs exist before Ready.");
            stage.AddChild(page);
            MainMenuReference reference = GD.Load<PackedScene>("res://Scenes/Frontend/Tests/MainMenuReference.tscn").Instantiate<MainMenuReference>();
            reference.Initialize(); referenceViewport.AddChild(reference);
            RetailFrontendFlow host = RetailFrontendFlow.InstantiateScene(); facades.Add(host); host.Initialize([]); hostViewport.AddChild(host.View);
            host.SetMouseCursorDesignPositionForCapture(new Vector2(-100f, -100f));
            host.View.SetProcess(false); host.View.SetProcessInput(false);
            host.ConfirmForSmoke();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(page.Get("_assets_configured").AsBool() && page.Get("_error").AsString() == "", "Production native recipes admit before readiness.");
            Check(!page.IsProcessing() && !page.IsProcessingInput() && !page.IsProcessingUnhandledInput(), "Native page owns no input or clock.");
            CheckAssets(page, reference);
            _completed.Add("production_assets");
            string[] labels = reference.Labels;
            bool[] availability = [true, false, true, true, true, true, true];
            int[] counts = [0, 1, 5, 9, 10, 14, 15, 20, 25, 30, 34, 35, 37, 38, 39, 40, 41, 44, 45, 47, 50];
            foreach (Vector2I size in new[] { new Vector2I(640, 480), new Vector2I(1280, 720), new Vector2I(801, 601), new Vector2I(320, 240) })
            {
                foreach (SubViewport view in views) view.Size = size;
                Fit(stage, size); reference.Size = size; host.View.Size = size;
                for (int index = 0; index < counts.Length; index++)
                {
                    float transition = counts[index] / 50f;
                    double animation = index * 0.427d, background = index * 0.071d;
                    int selected = index % 7;
                    using D facts = Frame(transition, animation, background, selected, 0, availability, labels, true);
                    Require(page.Call("set_frame", facts));
                    reference.SetFrame(transition, animation, background, selected, 0, availability, labels, true);
                    SetHost(host, counts[index], animation, background, selected);
                    Check(page.GetNode<CanvasItem>("Selector").Visible && page.GetNode<CanvasItem>("Reflection").Visible,
                        "Selector object and reflection retain their distinct draw-time visibility gates.");
                    Transform2D sheen = page.GetNode<Node2D>("Reflection").GetGlobalTransformWithCanvas();
                    Transform2D referenceSheen = reference.GetNode<Node2D>("TitleLogoReflection").GetGlobalTransformWithCanvas();
                    Check(sheen == referenceSheen, $"Exact reflection canvas transform at {size}: native={sheen}, reference={referenceSheen}.");
                    var nativeMaterial = (ShaderMaterial)page.GetNode<Node2D>("Reflection").Material;
                    var oldMaterial = (ShaderMaterial)reference.GetNode<Node2D>("TitleLogoReflection").Material;
                    foreach (string parameter in new[] { "gain", "scroll" })
                        Check(nativeMaterial.GetShaderParameter(parameter).AsDouble() == oldMaterial.GetShaderParameter(parameter).AsDouble(), "Exact reflection uniform: " + parameter);
                    Check(page.GetNode<Control>("TitleLogo/Body").GetGlobalTransformWithCanvas() == reference.GetNode<Control>("Stage/MainMenu/TitleLogo/Body").GetGlobalTransformWithCanvas(), "Exact title body canvas transform.");
                    CheckFrame(page, reference, selected, transition, labels);
                    if (_directory is not null && size == new Vector2I(801, 601) && index == 0)
                    {
                        using D withoutReflection = Frame(transition, animation, background, selected, 0, availability, labels, false);
                        Require(page.Call("set_frame", withoutReflection));
                        Require(host.View.GetNode("Stage/MainMenu").Call("set_frame", withoutReflection));
                        reference.SetFrame(transition, animation, background, selected, 0, availability, labels, false);
                        await ComparePixels(nativeViewport, referenceViewport, hostViewport, "fractional-without-reflection", true);
                        Require(page.Call("set_frame", facts));
                        Require(host.View.GetNode("Stage/MainMenu").Call("set_frame", facts));
                        reference.SetFrame(transition, animation, background, selected, 0, availability, labels, true);
                    }
                    if (_directory is not null) await ComparePixels(nativeViewport, referenceViewport, hostViewport, $"{size.X}x{size.Y}-{index:D2}", true);
                    _samples++;
                }
            }
            _completed.Add("transition_and_host_frames");
            // Languages and raw text are explicit presentation fixtures. The
            // current session intentionally has no language mutation API.
            foreach (int language in new[] { 0, 1, 2, 3, 4 })
            {
                using D facts = Frame(1f, 17.25, 10.2, language, language, availability, labels, true);
                Require(page.Call("set_frame", facts));
                reference.SetFrame(1f, 17.25, 10.2, language, language, availability, labels, true);
                if (_directory is not null) await ComparePixels(nativeViewport, referenceViewport, hostViewport, $"language-{language}", false);
                _samples++;
            }
            string[] rawLabels = labels.ToArray(); rawLabels[3] = "A\0B\ud83d\ude80\ufeff\u00e9\u0100";
            using (D facts = Frame(1f, 2.5, 3.1, 3, 0, availability, rawLabels, false)) Require(page.Call("set_frame", facts));
            reference.SetFrame(1f, 2.5, 3.1, 3, 0, availability, rawLabels, false);
            CheckFrame(page, reference, 3, 1f, rawLabels);
            if (_directory is not null) await ComparePixels(nativeViewport, referenceViewport, hostViewport, "raw-utf16-no-reflection", false);
            _samples++;
            _completed.Add("language_utf16_and_reflection");
            // Text override changes only the row, not imported selector width.
            Control nativeRow = page.GetNode<Control>("NewGame");
            MainMenuReferencePart oldRow = reference.Parts["Main.Row0"];
            nativeRow.Set("override_text", true); nativeRow.Set("text", "Agent-authored caption");
            oldRow.OverrideText = true; oldRow.Text = "Agent-authored caption";
            using (D facts = Frame(1f, 5.1, 0.7, 0, 0, availability, labels, true)) Require(page.Call("set_frame", facts));
            reference.SetFrame(1f, 5.1, 0.7, 0, 0, availability, labels, true);
            if (_directory is not null) await ComparePixels(nativeViewport, referenceViewport, hostViewport, "authored-row-caption", false);
            _samples++;
            nativeRow.Position += new Vector2(3.25f, -2.5f); oldRow.Position = nativeRow.Position;
            nativeRow.Size = new Vector2(217.5f, 23.25f); oldRow.Size = nativeRow.Size;
            if (_directory is not null) await ComparePixels(nativeViewport, referenceViewport, hostViewport, "authored-row-transform", false);
            _samples++;
            _completed.Add("authored_overrides");
            Check(Input.MouseMode == pointer && page.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0 && page.FindChildren("*", "Node3D", true, false).Count == 0,
                "Presentation never acquires pointer, starts audio or constructs gameplay.");
            foreach ((string path, string before) in _inputHashes) Check(Hash(path) == before, "Read-only input unchanged: " + path);
            _completed.Add("read_only_and_ownership");
            FrontendHarnessChecks.ReleaseFacades(facades);
            foreach (SubViewport view in views) view.QueueFree(); views.Clear();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Report(null); GetTree().Quit(0);
        }
        catch (Exception error)
        {
            FrontendHarnessChecks.ReleaseFacades(facades);
            foreach (SubViewport view in views) view.QueueFree();
            Report(error.Message); GD.PushError(error.ToString()); GetTree().Quit(1);
        }
    }

    private void CheckAssets(Control page, MainMenuReference reference)
    {
        foreach ((string path, string key) in new[] { ("Writing/Tile0", "forseti-writing-large"), ("Language/LeftChevron", "fe-arrow"), ("Selector", "title-text-box"),
            ("TitleLogo/Body", "title-logo"), ("Decoration/Left/Body", "title-bracket-01"), ("Decoration/LeftTwin/Body", "title-bracket-02"),
            ("Decoration/Right/Body", "symbol-bracket-01"), ("Decoration/RightTwin/Body", "symbol-bracket-02") })
            SameTexture(page.GetNode(path).Get("texture").As<Texture2D>(), reference.Art[key], path);
        SameTexture(page.GetNode("Reflection").Get("reflection").As<Texture2D>(), reference.Art["reflection-map"], "reflection map");
        using A flags = page.Get("language_flags").AsGodotArray(); using A icons = page.Get("menu_icons").AsGodotArray();
        for (int index = 0; index < flags.Count; index++) SameTexture(flags[index].As<Texture2D>(), reference.Flags[index], "flag " + index);
        for (int index = 0; index < icons.Count; index++) SameTexture(icons[index].As<Texture2D>(), reference.Icons[index], "icon " + index);
        using GodotObject font = page.Get("font").AsGodotObject();
        SameTexture(font.Get("page").As<Texture2D>(), reference.Font, "Font13");
        Check(font.Call("glyph_widths").AsInt32Array().SequenceEqual(reference.Widths), "All 256 measured font widths match.");
    }
    private void SameTexture(Texture2D actual, Texture2D expected, string name)
    {
        using Image a = actual.GetImage(); using Image e = expected.GetImage();
        Check(a.GetSize() == e.GetSize() && a.GetFormat() == e.GetFormat() && a.GetData().SequenceEqual(e.GetData()), "Exact admitted texture/image storage: " + name);
    }
    private void CheckFrame(Control page, MainMenuReference reference, int selection, float transition, string[] labels)
    {
        string[] names = ["NewGame", "ContinueGame", "LoadGame", "Multiplayer", "Goodies", "Options", "Quit"];
        for (int index = 0; index < 7; index++)
        {
            int[] text = page.GetNode(names[index]).Call("displayed_units").AsInt32Array();
            Check(text.SequenceEqual(labels[index].Select(value => (int)value)), "Every displayed raw UTF-16 unit stays in the ordered row.");
            Vector2 origin = page.GetNode(names[index]).Call("drawing_origin").AsVector2();
            Check(origin == new Vector2(219f - reference.Measure(labels[index]) * 0.5f, 296f + index * 20f), "Actual label draw origin follows retained font measurement.");
        }
        Rect2 selector = page.GetNode("Selector").Call("drawing_rect").AsRect2();
        float width = reference.Measure(labels[selection]) + 31f;
        Check(selector == new Rect2(219f - width * 0.5f, 288f + selection * 20f, width, 32f), "Selector remains before every row and uses imported label ink+31.");
        float alpha = transition < 0.75f ? 0f : Math.Min(1f, (transition - 0.75f) * 4f);
        Check(page.GetNode<CanvasItem>("NewGame").Visible == (alpha > 0f), "Row reveal branch remains exact.");
    }
    private static D Frame(float transition, double animation, double background, int selected, int language, bool[] available, string[] labels, bool reflection)
    {
        using A rows = new();
        for (int index = 0; index < 7; index++) rows.Add(new D { ["text"] = labels[index].Select(value => (int)value).ToArray(), ["available"] = available[index] });
        return new D { ["transition"] = transition, ["animation_seconds"] = animation, ["background_seconds"] = background,
            ["selected_index"] = selected, ["language"] = language, ["rows"] = rows, ["reflection_visible"] = reflection };
    }
    private static void SetHost(RetailFrontendFlow host, int count, double animation, double background, int selected)
    {
        host.View.Set("_main_transition_count", count);
        host.View.Set("_main_transition_time", 50);
        host.View.Set("_animation_seconds", animation);
        host.View.Set("_fe_back_seconds", background);
        host.SelectMainIndexForCapture(selected);
    }
    private async Task ComparePixels(SubViewport native, SubViewport reference, SubViewport host, string name, bool includeHost)
    {
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image actual = native.GetTexture().GetImage(); using Image expected = reference.GetTexture().GetImage();
        Save(actual, name + "-native.png"); Save(expected, name + "-reference.png");
        Compare(actual, expected, name, "native");
        if (includeHost)
        {
            using Image integrated = host.GetTexture().GetImage();
            Save(integrated, name + "-host.png"); Compare(integrated, expected, name, "host");
        }
    }
    private void Save(Image image, string name)
    {
        string path = Path.Combine(_directory!, name);
        Check(!File.Exists(path) && !Directory.Exists(path) && new FileInfo(path).LinkTarget is null && image.SavePng(path) == Error.Ok, "Fresh owned capture saved: " + name);
    }
    private void Compare(Image actual, Image expected, string name, string kind)
    {
        byte[] a = actual.GetData(), e = expected.GetData();
        int differences = a.Length == e.Length ? a.Where((value, index) => value != e[index]).Count() : -1;
        _pixels.Add(new { name, kind, differences, actualHash = Convert.ToHexString(SHA256.HashData(a)), expectedHash = Convert.ToHexString(SHA256.HashData(e)) });
        Check(differences == 0, $"{kind} {name} differs in {differences} RGBA bytes.");
    }
    private SubViewport MakeViewport()
    {
        var view = new SubViewport { Size = new Vector2I(640, 480), Disable3D = true, TransparentBg = false, RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
        AddChild(view);
        var background = new ColorRect { Color = Colors.Black, MouseFilter = Control.MouseFilterEnum.Ignore };
        view.AddChild(background); background.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        return view;
    }
    private static Control MakeStage(SubViewport view)
    {
        var stage = new Control { Size = new Vector2(640, 480), MouseFilter = Control.MouseFilterEnum.Ignore };
        view.AddChild(stage); return stage;
    }
    private static void Fit(Control stage, Vector2I size)
    {
        float scale = Mathf.Min(size.X / 640f, size.Y / 480f);
        stage.Scale = Vector2.One * scale; stage.Position = ((Vector2)size - new Vector2(640, 480) * scale) * 0.5f;
    }
    private static void Require(Variant value)
    {
        using D result = value.AsGodotDictionary();
        if (!result["ok"].AsBool()) throw new InvalidDataException(result["error"].AsString());
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
    private void Check(bool condition, string message) { _checks++; if (!condition) throw new InvalidOperationException(message); }
    private void Report(string? error) => GD.Print("MAIN_MENU_SCENE_CHECKS: " + JsonSerializer.Serialize(new { schema = 1, checks = _checks, samples = _samples,
        completed = _completed, pixels = _pixels, failure_count = error is null ? 0 : 1, error }));
}
