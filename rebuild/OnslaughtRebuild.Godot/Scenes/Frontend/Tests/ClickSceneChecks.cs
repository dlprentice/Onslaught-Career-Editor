// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using System.Text.Json;
using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>The native page versus retained drawing and, before integration,
/// the actual composed frontend. Displays and outputs belong to the caller.</summary>
public sealed partial class ClickSceneChecks : Node
{
    private int _checks;
    private readonly List<object> _pixels = [];
    public override async void _Ready()
    {
        var views = new List<SubViewport>();
        List<RetailFrontendFlow> facades = [];
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Contains("--skipfmv", StringComparer.Ordinal), "Focused checks require --skipfmv.");
            string? directory = args.FirstOrDefault(x => x.StartsWith("--click-render-dir=", StringComparison.Ordinal))?[19..];
            if (directory is not null)
            {
                string owner = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
                Check(Path.IsPathFullyQualified(directory) && Path.GetFullPath(directory).StartsWith(owner, StringComparison.Ordinal)
                    && Directory.Exists(directory) && DisplayServer.GetName() != "headless", "Caller owns isolated rendering and output directory.");
            }
            Input.MouseModeEnum pointer = Input.MouseMode;
            SubViewport nativeViewport = MakeViewport(), referenceViewport = MakeViewport(), hostViewport = MakeViewport();
            views.AddRange([nativeViewport, referenceViewport, hostViewport]);
            Control stage = MakeStage(nativeViewport), referenceStage = MakeStage(referenceViewport);
            Control page = GD.Load<PackedScene>("res://Scenes/Frontend/ClickToStart.tscn").Instantiate<Control>();
            Check(page.GetChildCount() == 5 && page.GetNode("Prompt").GetChildCount() == 5
                && page.GetNode("Title").GetChildCount() == 5, "Five production sections and all caption/title passes exist before Ready.");
            stage.AddChild(page);
            var reference = new ClickReference(); reference.Initialize(); referenceStage.AddChild(reference);
            RetailFrontendFlow host = RetailFrontendFlow.InstantiateScene(); facades.Add(host); host.Initialize([]); hostViewport.AddChild(host.View);
            host.SetMouseCursorDesignPositionForCapture(new Vector2(-100, -100));
            host.View.SetProcess(false); host.View.SetProcessInput(false);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            using Variant configured = page.Get("_assets_configured");
            Check(configured.AsBool() && !page.IsProcessing() && !page.IsProcessingInput()
                && !page.IsProcessingUnhandledInput(), "Native page admits production recipes without a clock or input owner.");
            foreach ((string path, Texture2D expected) in new[] { ("Splash/Motion/Image", reference.Splash),
                ("Slide/Body/Motion/Image", reference.Slide), ("Title/Body/Motion/Image", reference.Title) })
            {
                using Variant boundTexture = page.GetNode(path).Get("texture");
                Texture2D actual = boundTexture.As<Texture2D>();
                using Image a = actual.GetImage(); using Image e = expected.GetImage();
                Check(a.GetData().SequenceEqual(e.GetData()) && a.GetSize() == e.GetSize(), "Exact production pixels: " + path);
            }
            using (Variant font = page.Get("font"))
            using (Variant texture = font.AsGodotObject().Get("page"))
            using (Image actual = texture.As<Texture2D>().GetImage())
            using (Image expected = reference.Font.GetImage())
                Check(actual.GetData().SequenceEqual(expected.GetData()), "Every font13 pixel matches.");
            (double Timer, double Page)[] samples = [(0, 0), (0.25, 0.125), (0.333984375, 1.1669921875),
                (0.5, 1.25), (1, 1.5), (2, 1.7), (2.5, 1.9), (3, 2), (3.02, 2.01), (3.25, 2.125),
                (3.5, 2.25), (4, 3), (4.001, 3.1), (5, 5), (6, 6), (8, 8)];
            foreach (Vector2I size in new[] { new Vector2I(640, 480), new Vector2I(1280, 720), new Vector2I(801, 601), new Vector2I(320, 240) })
            {
                foreach (SubViewport view in views) view.Size = size;
                Fit(stage, size); Fit(referenceStage, size); host.View.Size = size;
                for (int index = 0; index < samples.Length; index++)
                {
                    (double timer, double seconds) = samples[index];
                    using var facts = new Godot.Collections.Dictionary { ["pulse_timer"] = timer, ["page_seconds"] = seconds };
                    using Variant batch = facts; using Variant returned = page.Call("set_frame", batch);
                    using Godot.Collections.Dictionary result = returned.AsGodotDictionary(); using Variant ok = result["ok"];
                    Check(ok.AsBool(), "Explicit time batch accepted.");
                    reference.SetFrame(timer, seconds);
                    host.View.Set("_click_pulse_timer", timer);
                    host.View.Set("_click_page_seconds", seconds);
                    FrontendHarnessChecks.Command(host, "redraw");
                    Check(page.GetNode<CanvasItem>("Prompt").Visible == RetailClickToStartGlyphs.ShouldDraw(timer)
                        && page.GetNode<CanvasItem>("Title").Visible == RetailClickToStartTitle.ShouldDraw(seconds)
                        && page.GetNode<CanvasItem>("TitleFlash").Visible == RetailClickToStartTitle.ShouldDrawSixth(seconds), "All strict visibility gates match.");
                    if (directory is null) continue;
                    await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                    await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
                    using Image actual = nativeViewport.GetTexture().GetImage();
                    using Image expected = referenceViewport.GetTexture().GetImage();
                    using Image composed = hostViewport.GetTexture().GetImage();
                    string name = $"{size.X}x{size.Y}-{index:D2}";
                    Check(actual.SavePng(Path.Combine(directory, name + "-native.png")) == Error.Ok
                        && expected.SavePng(Path.Combine(directory, name + "-reference.png")) == Error.Ok, "Owned captures saved.");
                    Compare(actual, expected, name, "native"); Compare(composed, expected, name, "host");
                }
            }
            Check(Input.MouseMode == pointer && page.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0,
                "Page never acquires pointer or audio.");
            FrontendHarnessChecks.ReleaseFacades(facades);
            foreach (SubViewport view in views) view.QueueFree(); views.Clear();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print("CLICK_SCENE_CHECKS: " + JsonSerializer.Serialize(new { checks = _checks, pixels = _pixels, failures = 0 }));
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            FrontendHarnessChecks.ReleaseFacades(facades);
            foreach (SubViewport view in views) view.QueueFree();
            GD.Print("CLICK_SCENE_CHECKS: " + JsonSerializer.Serialize(new { checks = _checks, pixels = _pixels, failures = 1 }));
            GD.PushError(error.ToString()); GetTree().Quit(1);
        }
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
        var view = new SubViewport { Size = new Vector2I(640, 480), Disable3D = true,
            TransparentBg = false, RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
        AddChild(view);
        // The production frontend clears its whole viewport to black, including
        // letterboxing. Give both standalone components that same background.
        var background = new ColorRect { Color = Colors.Black, MouseFilter = Control.MouseFilterEnum.Ignore };
        view.AddChild(background);
        background.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
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
        stage.Scale = Vector2.One * scale;
        stage.Position = ((Vector2)size - new Vector2(640, 480) * scale) * 0.5f;
    }
    private void Check(bool condition, string message)
    {
        _checks++; if (!condition) throw new InvalidOperationException(message);
    }
}
