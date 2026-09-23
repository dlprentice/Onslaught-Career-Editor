// SPDX-License-Identifier: GPL-3.0-or-later

using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json.Nodes;
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Actual Loading scene, source admission and existing two-frame launch seam.
/// The optional baseline mode measures the old composed page before its removal.
/// Software pixels prove a bounded renderer comparison, never combat completion.
/// </summary>
public sealed partial class LoadingSceneChecks : Node
{
    private int _checks;
    private readonly List<string> _completed = [];
    private readonly List<object> _pixels = [], _legacyComposition = [];
    private string? _renderDirectory;
    private bool _baseline;

    public override async void _Ready()
    {
        SubViewport? flowViewport = null, nativeViewport = null, referenceViewport = null;
        List<RetailFrontendFlow> facades = [];
        try
        {
            string[] arguments = OS.GetCmdlineUserArgs();
            Check(arguments.Contains("--skipfmv", StringComparer.Ordinal), "Focused loading handoff requires --skipfmv.");
            _baseline = arguments.Contains("--loading-measure-existing-composition", StringComparer.Ordinal);
            foreach (string argument in arguments)
            {
                const string prefix = "--loading-render-dir=";
                if (!argument.StartsWith(prefix, StringComparison.Ordinal)) continue;
                _renderDirectory = argument[prefix.Length..];
                string owned = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
                Check(Path.IsPathFullyQualified(_renderDirectory) && Path.GetFullPath(_renderDirectory).StartsWith(owned, StringComparison.Ordinal)
                    && Directory.Exists(_renderDirectory), "Render output exists below the owning worktree's local-data.");
                Check(DisplayServer.GetName() != "headless", "Pixels require the caller's isolated display.");
            }
            Input.MouseModeEnum pointer = Input.MouseMode;
            flowViewport = MakeViewport();
            RetailFrontendFlow flow = RetailFrontendFlow.InstantiateScene(); facades.Add(flow);
            flow.Initialize([]);
            flowViewport.AddChild(flow.View);
            flow.SetMouseCursorDesignPositionForCapture(new Vector2(-100, -100));
            flow.View.SetProcess(false); flow.View.SetProcessInput(false);
            for (int index = 0; index < 6; index++) flow.ConfirmForSmoke();
            Control page;
            Control? nativeStage = null;
            if (_baseline)
            {
                Check(false, "Historical pre-conversion baseline mode requires its original checkpoint; this root is now entirely native.");
                nativeViewport = MakeViewport();
                nativeStage = MakeStage(nativeViewport);
                page = GD.Load<PackedScene>("res://Scenes/Frontend/Loading.tscn").Instantiate<Control>();
                nativeStage.AddChild(page);
            }
            else
            {
                page = flow.View.GetNode<Control>("Stage/Loading");
                using Variant script = page.GetScript();
                using Resource resource = script.As<Resource>();
                Check(resource.ResourcePath == "res://Scenes/Frontend/loading_presentation.gd", "Live frontend embeds the native production page.");
                Check(FrontendHarnessChecks.HasNativeRoot(flow), "The native root and page own Loading presentation; the facade cannot draw.");
            }
            referenceViewport = MakeViewport();
            Control referenceStage = MakeStage(referenceViewport);
            var reference = new LoadingReference();
            reference.Initialize();
            referenceStage.AddChild(reference);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(!page.IsProcessing() && !page.IsProcessingInput() && !page.IsProcessingUnhandledInput(), "Page introduces no timing or input owner.");
            Check(page.GetNode("Caption").GetChildCount() == 5 && page.GetNode("Caption") is Node2D,
                "The real source anchor and five ordered caption passes are editable.");
            CheckAssets(flow, page, reference);
            Complete("production_assets_and_font");
            CheckReceiptAdmission();
            Complete("source_admission");
            if (_renderDirectory is not null)
            {
                await CheckPixels(flow, page, reference, flowViewport, nativeViewport, nativeStage, referenceViewport, referenceStage);
                Complete("retained_renderer_pixels");
            }
            CheckHandoff(flow, page);
            Complete("loading_handoff");
            Check(Input.MouseMode == pointer && flow.View.FindChildren("*", "Camera3D", true, false).Count == 0
                && flow.View.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0,
                "Synthetic load readiness starts no world, playback or pointer ownership.");
            Complete("inactive_safety");
            FrontendHarnessChecks.ReleaseFacades(facades);
            flowViewport.QueueFree(); flowViewport = null;
            nativeViewport?.QueueFree(); nativeViewport = null;
            referenceViewport.QueueFree(); referenceViewport = null;
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Report(null); GetTree().Quit(0);
        }
        catch (Exception error)
        {
            FrontendHarnessChecks.ReleaseFacades(facades);
            flowViewport?.QueueFree(); nativeViewport?.QueueFree(); referenceViewport?.QueueFree();
            GD.PushError(error.ToString()); Report(error.Message); GetTree().Quit(1);
        }
    }

    private void CheckAssets(RetailFrontendFlow flow, Control page, LoadingReference reference)
    {
        using Variant fontValue = page.Get("title_font");
        if (!_baseline)
        {
            using Variant shared = flow.OptionsView.Get("title_font");
            Check(fontValue.AsGodotObject().GetInstanceId() == shared.AsGodotObject().GetInstanceId(),
                "Integrated Loading shares the existing production frontend font resource.");
        }
        using Resource font = fontValue.As<Resource>();
        using Variant textureValue = font.Get("page");
        using Texture2D texture = textureValue.As<Texture2D>();
        using Image nativeFont = texture.GetImage();
        using Image expectedFont = reference.Font.GetImage();
        Check(nativeFont.GetSize() == expectedFont.GetSize() && nativeFont.GetData().SequenceEqual(expectedFont.GetData()),
            "Every native font22 pixel equals the retained C# decode.");
        using Variant measured = font.Call("glyph_widths");
        Check(measured.AsInt32Array().SequenceEqual(reference.Widths), "All 256 original measured glyph extents agree.");
        foreach (string word in new[] { "", "Loading...", "A\0B\ud83d\ude80\ufeff", "\u001f !\u011f\u0120" })
        {
            int width = 0;
            foreach (char character in word) width += reference.Widths[character is >= (char)32 and < (char)288 ? character - 32 : 31] + 1;
            using Variant units = Units(word);
            using Variant actual = font.Call("measure", units);
            Check((float)actual.AsDouble() == Math.Max(0, width - 1), "Font words retain raw UTF-16 glyph indices and extents.");
        }
        using Texture2D background = page.GetNode<TextureRect>("Background").Texture;
        using Image nativeBackground = background.GetImage();
        using Image expectedBackground = reference.Background.GetImage();
        Check(nativeBackground.GetSize() == expectedBackground.GetSize() && nativeBackground.GetData().SequenceEqual(expectedBackground.GetData()),
            "Every LoadingScreen pixel equals the original admitted DXT1 decode.");
        using Variant compression = background.Get("compression");
        Check(compression.AsInt32() == (int)CuratedAyaTextureLoader.Compression.Dxt1, "The actual production background keeps DXT1 admission.");
    }

    private void CheckReceiptAdmission()
    {
        using Resource receipt = GD.Load<Resource>("res://Scenes/Frontend/LoadingStrings.tres");
        string original = Godot.FileAccess.GetFileAsString("res://Assets/Frontend/english.json");
        var samples = new List<string> { original, "", " ", "{", "{}", "[]", "null", "1", "true", "\"text\"", original + "{}" };
        foreach (string key in new[] { "schema", "culture", "sourceSha256", "strings" })
        {
            samples.Add(Mutate(original, root => root.Remove(key)));
            foreach (JsonNode? value in new JsonNode?[] { null, JsonValue.Create(3), JsonValue.Create("wrong"), new JsonArray() })
                samples.Add(Mutate(original, root => root[key] = value?.DeepClone()));
        }
        foreach (string key in new[] { "newGame", "continueGame", "loadGame", "multiplayer", "goodies", "options", "quit", "selectLevel", "level100", "loading" })
        {
            samples.Add(Mutate(original, root => root["strings"]!.AsObject().Remove(key)));
            foreach (JsonNode? value in new JsonNode?[] { null, JsonValue.Create(3), JsonValue.Create(""), new JsonArray() })
                samples.Add(Mutate(original, root => root["strings"]![key] = value?.DeepClone()));
        }
        foreach (string encoded in new[] { "\"A\\u0000B\"", "\"\\ufeffLoading\"", "\"\\ud83d\\ude80\"", "\"\\ud800\"", "\"\\udc00\"", "\"\\u011f\\u0120\"" })
            samples.Add(original.Replace("\"Loading...\"", encoded, StringComparison.Ordinal));
        samples.Add(original.Insert(original.LastIndexOf('}'), ",\"culture\":\"wrong\""));
        samples.Add(original.Insert(original.LastIndexOf('}'), ",\"culture\":\"en\""));
        samples.Add(Mutate(original, root => { root["strings"]!["level100"] = "Wrong"; root["strings"]!.AsObject().Remove("loading"); }));
        foreach (string source in samples)
        {
            string? expected = null; Exception? error = null;
            try { expected = LoadingReference.AdmitCaption(source); }
            catch (Exception caught) { error = caught; }
            using Variant returned = receipt.Call("admit_source", source);
            using Godot.Collections.Dictionary actual = returned.AsGodotDictionary();
            Check(actual["ok"].AsBool() == (error is null), "Native receipt success/rejection agrees with the original loader.");
            if (error is null)
            {
                using Variant value = actual["value"];
                Check(value.AsInt32Array().SequenceEqual(Units(expected!)), "Admitted caption preserves exact original UTF-16 units.");
            }
            else
            {
                Check(actual["error_type"].AsString() == error.GetType().Name, "Source error kind and admission order agree: " + error.GetType().Name);
                if (error is InvalidDataException)
                    Check(actual["error"].AsString() == error.Message, "Explicit identity/required-row diagnostic preserves the original ordering.");
            }
        }
    }

    private void CheckHandoff(RetailFrontendFlow flow, Control page)
    {
        GdFrontendSession session = GdFrontendSession.BorrowExisting(flow.View);
        int requests = 0, activations = 0;
        flow.Level100LoadRequested += () => requests++;
        flow.GameplayActivated += () => activations++;
        Check(flow.CurrentScreen == RetailFrontendScreen.Loading && flow.View.Get("_loading_frames").AsInt32() == 0,
            "Actual frontend enters Loading before its two frame seam.");
        if (!_baseline) CheckFacts(page, 0, false, false);
        FrontendHarnessChecks.Command(flow, "advance", 0d);
        Check(requests == 0 && flow.View.Get("_loading_frames").AsInt32() == 1, "The first loading frame cannot consume the launch request.");
        if (!_baseline) CheckFacts(page, 1, false, false);
        FrontendHarnessChecks.Command(flow, "advance", 0d);
        Check(requests == 1 && flow.CurrentScreen == RetailFrontendScreen.Loading, "The second loading frame requests exactly one launch and waits for readiness.");
        if (!_baseline) CheckFacts(page, 2, true, false);
        FrontendHarnessChecks.Command(flow, "advance", 0d);
        Check(requests == 1 && activations == 0, "Waiting never repeats the consumed request or activates gameplay.");
        byte[] beforeDisplay = session.SnapshotBytes();
        int calls = flow.NativeCallCount;
        SetFrame(page, 2, true, true, "Loading...");
        SetFrame(page, int.MaxValue, false, false, "Loading...");
        Check(flow.NativeCallCount == calls && beforeDisplay.SequenceEqual(session.SnapshotBytes()) && requests == 1 && activations == 0, "Display batches never mutate the frontend session or trigger loading.");
        flow.MarkLevel100Ready();
        FrontendHarnessChecks.Command(flow, "advance", 0d);
        flow.View.SetProcess(false); flow.View.SetProcessInput(false);
        Check(flow.CurrentScreen == RetailFrontendScreen.Gameplay && activations == 1 && !flow.View.Visible
            && !flow.View.GetNode<Control>("Stage/Loading").IsVisibleInTree(),
            "Existing ready handoff activates once and hides the frontend root before any page visibility refresh.");
        bool rejected = false;
        try { flow.MarkLevel100Ready(); }
        catch (InvalidOperationException) { rejected = true; }
        Check(rejected && flow.CurrentScreen == RetailFrontendScreen.Gameplay, "Invalid late readiness fails and leaves the completed handoff unchanged.");
    }

    private async Task CheckPixels(RetailFrontendFlow flow, Control page, LoadingReference reference,
        SubViewport flowViewport, SubViewport? nativeViewport, Control? nativeStage, SubViewport referenceViewport, Control referenceStage)
    {
        (string Name, int Frames, bool Requested, bool Ready, string Text)[] samples =
        [
            ("entry", 0, false, false, "Loading..."), ("first-frame", 1, false, false, "Loading..."),
            ("requested", 2, true, false, "Loading..."), ("ready", 2, true, true, "Loading..."),
            ("raw-caption", int.MaxValue, false, false, "A\0B\ud83d\ude80\ufeff"),
        ];
        foreach (Vector2I size in new[] { new Vector2I(640, 480), new Vector2I(1280, 720), new Vector2I(801, 601), new Vector2I(320, 240) })
        {
            flowViewport.Size = size;
            referenceViewport.Size = size;
            if (nativeViewport is not null) nativeViewport.Size = size;
            flow.View.Size = size;
            Fit(referenceStage, size);
            if (nativeStage is not null) Fit(nativeStage, size);
            foreach (var sample in samples)
            {
                SetFrame(page, sample.Frames, sample.Requested, sample.Ready, sample.Text);
                reference.SetCaption(sample.Text);
                if (_baseline)
                {
                    FrontendHarnessChecks.SetLoadingCaption(flow, sample.Text);
                    foreach (Node part in flow.View.FindChildren("*", "Control", true, false))
                        if (part is Control authored) authored.QueueRedraw();
                }
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
                using Image actual = (nativeViewport ?? flowViewport).GetTexture().GetImage();
                using Image expected = referenceViewport.GetTexture().GetImage();
                actual.Convert(Image.Format.Rgba8); expected.Convert(Image.Format.Rgba8);
                byte[] actualBytes = actual.GetData(), expectedBytes = expected.GetData();
                int differences = Difference(actualBytes, expectedBytes);
                string name = $"{size.X}x{size.Y}-{sample.Name}";
                SaveOwned(actual, name + "-native.png"); SaveOwned(expected, name + "-reference.png");
                _pixels.Add(new { name, differences, actualHash = Hash(actualBytes), expectedHash = Hash(expectedBytes) });
                Check(actualBytes.Any(value => value is > 0 and < 255), "Rendered Loading page contains production pixels.");
                Check(actual.GetSize() == expected.GetSize() && differences == 0, $"Full RGBA source comparison {name}: {differences} differing bytes.");
                if (_baseline)
                {
                    using Image composed = flowViewport.GetTexture().GetImage();
                    composed.Convert(Image.Format.Rgba8);
                    byte[] oldBytes = composed.GetData();
                    SaveOwned(composed, name + "-previous-composition.png");
                    _legacyComposition.Add(new { name, differences = Difference(oldBytes, expectedBytes),
                        actualHash = Hash(oldBytes), expectedHash = Hash(expectedBytes), bounds = DifferenceBounds(oldBytes, expectedBytes, size) });
                }
            }
        }
        FrontendHarnessChecks.SetLoadingCaption(flow, "Loading...");
        SetFrame(page, 0, false, false, "Loading...");
    }

    private void CheckFacts(Control page, int frames, bool requested, bool ready)
    {
        using Variant returned = page.Call("view_snapshot");
        using Godot.Collections.Dictionary snapshot = returned.AsGodotDictionary();
        using Variant factsValue = snapshot["facts"];
        using Godot.Collections.Dictionary facts = factsValue.AsGodotDictionary();
        Check(facts["loading_frames"].AsInt32() == frames && facts["launch_requested"].AsBool() == requested && facts["ready"].AsBool() == ready,
            "Native page facts match the actual host loading boundary.");
    }
    private static void SetFrame(Control page, int frames, bool requested, bool ready, string text)
    {
        using var facts = new Godot.Collections.Dictionary { ["loading_frames"] = frames, ["launch_requested"] = requested, ["ready"] = ready };
        using Variant batch = facts;
        using Variant caption = Units(text);
        using Variant returned = page.Call("set_frame", batch, caption);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (!result["ok"].AsBool()) throw new InvalidOperationException(result["error"].AsString());
    }
    private SubViewport MakeViewport()
    {
        var viewport = new SubViewport { Size = new Vector2I(640, 480), Disable3D = true, RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
        AddChild(viewport); return viewport;
    }
    private static Control MakeStage(SubViewport viewport)
    {
        var clear = new ColorRect { Name = "Clear", Color = Colors.Black, MouseFilter = Control.MouseFilterEnum.Ignore };
        viewport.AddChild(clear); clear.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        var stage = new Control { Name = "Stage", Size = new Vector2(640, 480), MouseFilter = Control.MouseFilterEnum.Ignore };
        viewport.AddChild(stage); return stage;
    }
    private static void Fit(Control stage, Vector2I size)
    {
        float scale = Math.Min(size.X / 640f, size.Y / 480f);
        stage.Scale = new Vector2(scale, scale);
        stage.Position = new Vector2((size.X - 640f * scale) * 0.5f, (size.Y - 480f * scale) * 0.5f);
    }
    private void SaveOwned(Image image, string filename)
    {
        string path = Path.Combine(_renderDirectory!, filename);
        Check(!File.Exists(path) && image.SavePng(path) == Error.Ok, "Owned Loading capture refuses overwriting another result.");
    }
    private static string Mutate(string original, Action<JsonObject> change)
    { JsonObject root = JsonNode.Parse(original)!.AsObject(); change(root); return root.ToJsonString(); }
    private static int[] Units(string text) => text.Select(character => (int)character).ToArray();
    private static int Difference(byte[] first, byte[] second) => first.Length != second.Length ? int.MaxValue : first.Zip(second).Count(pair => pair.First != pair.Second);
    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes));
    private static int[]? DifferenceBounds(byte[] first, byte[] second, Vector2I size)
    {
        int left = size.X, top = size.Y, right = -1, bottom = -1;
        for (int pixel = 0; pixel < size.X * size.Y; pixel++)
            if (!first.AsSpan(pixel * 4, 4).SequenceEqual(second.AsSpan(pixel * 4, 4)))
            { left = Math.Min(left, pixel % size.X); top = Math.Min(top, pixel / size.X); right = Math.Max(right, pixel % size.X); bottom = Math.Max(bottom, pixel / size.X); }
        return right < 0 ? null : [left, top, right, bottom];
    }
    private void Check(bool value, string message) { _checks++; if (!value) throw new InvalidOperationException(message); }
    private void Complete(string section) { _completed.Add(section); GD.Print("LOADING_HOST_SECTION: ", section); }
    private void Report(string? error) => GD.Print("LOADING_HOST_CHECKS: ", System.Text.Json.JsonSerializer.Serialize(new
    { schema = 1, checks = _checks, failure_count = error is null ? 0 : 1, completed = _completed, pixels = _pixels, legacy_composition = _legacyComposition,
        baseline = _baseline, error, runtime = RuntimeInformation.FrameworkDescription, engine = Engine.GetVersionInfo()["string"].AsString() }));
}
