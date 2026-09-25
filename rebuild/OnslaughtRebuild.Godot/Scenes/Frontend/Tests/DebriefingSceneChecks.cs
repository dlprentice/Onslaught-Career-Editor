// SPDX-License-Identifier: GPL-3.0-or-later

using System.Runtime.InteropServices;
using System.Security.Cryptography;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The actual production page and its settled C# drawing reference. Synthetic
/// terminal handoffs test the existing frontend seam; they do not demonstrate
/// full Level 100 combat. No game world, save writes or audio playback starts.
/// Optional pixels require an externally isolated display and owned output.
/// </summary>
public sealed partial class DebriefingSceneChecks : Node
{
    private int _checks;
    private readonly List<string> _completed = [];
    private string? _renderDirectory;
    private readonly List<object> _pixels = [];

    public override async void _Ready()
    {
        SubViewport? productionViewport = null, referenceViewport = null;
        List<RetailFrontendFlow> facades = [];
        try
        {
            string[] arguments = OS.GetCmdlineUserArgs();
            Check(arguments.Contains("--skipfmv", StringComparer.Ordinal), "Focused handoff requires --skipfmv.");
            foreach (string argument in arguments)
            {
                const string prefix = "--debriefing-render-dir=";
                if (!argument.StartsWith(prefix, StringComparison.Ordinal)) continue;
                _renderDirectory = argument[prefix.Length..];
                string owned = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
                Check(Path.IsPathFullyQualified(_renderDirectory) && Path.GetFullPath(_renderDirectory).StartsWith(owned, StringComparison.Ordinal)
                    && Directory.Exists(_renderDirectory), "Output exists under this worktree's owned local-data.");
                Check(DisplayServer.GetName() != "headless", "Pixels require the caller's isolated display.");
            }
            Input.MouseModeEnum pointer = Input.MouseMode;
            productionViewport = MakeViewport();
            RetailFrontendFlow flow = RetailFrontendFlow.InstantiateScene(); facades.Add(flow);
            flow.Initialize([]);
            productionViewport.AddChild(flow.View);
            flow.SetMouseCursorDesignPositionForCapture(new Vector2(-100f, -100f));
            flow.View.SetProcess(false);
            flow.View.SetProcessInput(false);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Control page = flow.View.GetNode<Control>("Stage/Debriefing");
            using (Variant script = page.GetScript())
            using (Resource scriptResource = script.As<Resource>())
                Check(scriptResource.ResourcePath == "res://Scenes/Frontend/debriefing_presentation.gd", "Live frontend embeds the native production page.");
            Check(!page.HasNode("MissionReport") && page.GetNode("Report/Labels").GetChildCount() == 3,
                "The old composite draw node is replaced by authored report controls.");
            Check(!page.IsProcessing() && !page.IsProcessingInput() && !page.IsProcessingUnhandledInput(), "Page owns no clock or input process.");
            Check(FrontendHarnessChecks.HasNativeRoot(flow), "The native root and page own Debriefing presentation; the facade cannot draw.");
            referenceViewport = MakeViewport();
            var reference = new DebriefingReference();
            Texture2D[] frames = FrontendHarnessChecks.SharedFrames(flow);
            reference.Initialize(frames);
            referenceViewport.AddChild(reference);
            CheckAssets(flow, page, reference);
            Complete("production_assets_and_fonts");
            CheckHandoff(flow, page);
            Complete("frontend_handoff");
            CheckProjection(page, reference, frames);
            Complete("settled_projection_and_clock");
            if (_renderDirectory is not null)
            {
                await CheckPixels(page, reference, productionViewport, referenceViewport);
                Complete("retained_renderer_pixels");
            }
            // Return via the actual session rather than the synthetic display
            // fixtures supplied to the presentation-only comparisons above.
            FrontendHarnessChecks.Command(flow, "advance", 0d);
            flow.View.SetProcess(false);
            flow.View.SetProcessInput(false);
            flow.ConfirmForSmoke();
            Check(flow.CurrentScreen == RetailFrontendScreen.LevelSelect && !page.Visible,
                "Acknowledging Debriefing keeps the existing Level Select handoff.");
            flow.View.Set("EditorPage", (int)RetailFrontendEditorPage.Debriefing);
            FrontendHarnessChecks.Command(flow, "set_editor_page");
            GdFrontendSession frozen = GdFrontendSession.BorrowExisting(flow.View);
            Check(frozen.Screen == RetailFrontendScreen.ClickToStart && frozen.Debriefing is null,
                "Selecting the editor fixture leaves a cold session without a manufactured Won outcome.");
            Check(Input.MouseMode == pointer, "No pointer ownership changes.");
            Check(flow.View.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0, "Page never creates audio playback.");
            Check(flow.View.FindChildren("*", "Camera3D", true, false).Count == 0, "Terminal fixture never creates a gameplay world.");
            Complete("inactive_safety");
            FrontendHarnessChecks.ReleaseFacades(facades);
            productionViewport.QueueFree(); productionViewport = null;
            referenceViewport.QueueFree(); referenceViewport = null;
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Report(null);
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            FrontendHarnessChecks.ReleaseFacades(facades);
            productionViewport?.QueueFree(); referenceViewport?.QueueFree();
            GD.PushError(error.ToString());
            Report(error.Message);
            GetTree().Quit(1);
        }
    }

    private void CheckAssets(RetailFrontendFlow flow, Control page, DebriefingReference reference)
    {
        foreach (bool title in new[] { false, true })
        {
            using Variant fontValue = page.Get(title ? "title_font" : "body_font");
            using Variant sharedValue = flow.OptionsView.Get(title ? "title_font" : "body_font");
            Check(fontValue.AsGodotObject().GetInstanceId() == sharedValue.AsGodotObject().GetInstanceId(),
                "Debriefing and the existing frontend share the production font resource.");
            using Resource font = fontValue.As<Resource>();
            using Variant textureValue = font.Get("page");
            using Texture2D texture = textureValue.As<Texture2D>();
            using Image actual = texture.GetImage();
            using Image expected = reference.Font(title).GetImage();
            Check(actual.GetSize() == expected.GetSize() && actual.GetData().SequenceEqual(expected.GetData()),
                "Every decoded font byte equals the retained C# loader.");
            Check(font.Call("glyph_widths").AsInt32Array().SequenceEqual(reference.Widths(title)), "All 256 measured glyph extents match C#.");
            foreach (string word in new[] { "", "DEBRIEFING", "Mission Status", "Primary Objectives", "Secondary Objectives",
                "Mission Status: ", "Victory", "Defeat", "Aborted", "Complete", "Incomplete", "Grade:", "A\0B\ud83d\ude80\ufeff" })
            {
                int[] units = word.Select(character => (int)character).ToArray();
                int[] widths = reference.Widths(title);
                float width = 0f;
                foreach (char character in word)
                {
                    int glyph = character is >= (char)32 and < (char)288 ? character - 32 : 31;
                    width += widths[glyph] + 1;
                }
                width = MathF.Max(0f, width - 1f);
                Check((float)font.Call("measure", units).AsDouble() == width, "Page font word extent equals retained C#.");
            }
        }
        using Variant gradeValue = page.Get("grade_textures");
        using Godot.Collections.Array grades = gradeValue.AsGodotArray();
        foreach ((string name, Texture2D texture) in reference.Art)
        {
            Texture2D native;
            Variant carrier = default;
            if (name.StartsWith("grade_", StringComparison.Ordinal))
            {
                carrier = grades["abcdes".IndexOf(name[^1])];
                native = carrier.As<Texture2D>();
            }
            else native = page.GetNode<TextureRect>(name switch
            { "metal_ring" => "MetalRingOrigin/MetalRing", "writing" => "Writing/Tile0", _ => "Grade/BracketBody" }).Texture;
            using (carrier)
            using (native)
            using (Image actual = native.GetImage())
            using (Image expected = texture.GetImage())
            {
                Check(actual.GetSize() == expected.GetSize() && actual.GetData().SequenceEqual(expected.GetData()),
                    "Every private art pixel equals the retained C# decode: " + name);
                Check(native.Get("compression").AsInt32() == (int)LegacyCuratedAyaTextureReference.Compression.Dxt2,
                    "Retained DXT2 admission is explicit: " + name);
            }
        }
    }

    private void CheckHandoff(RetailFrontendFlow flow, Control page)
    {
        GdFrontendSession session = GdFrontendSession.BorrowExisting(flow.View);
        int returns = 0, activations = 0;
        flow.ReturnToMainMenuRequested += () => returns++;
        flow.GameplayActivated += () => activations++;
        flow.Level100LoadRequested += flow.MarkLevel100Ready;
        for (int index = 0; index < 6; index++) flow.ConfirmForSmoke();
        session.Refresh();
        Check(session.Screen == RetailFrontendScreen.Loading, "Existing navigation reaches the loading seam.");
        FrontendHarnessChecks.Command(flow, "advance", 0d); FrontendHarnessChecks.Command(flow, "advance", 0d);
        session.Refresh();
        Check(session.Screen == RetailFrontendScreen.Gameplay && activations == 1, "Synthetic ready callback uses the actual two-frame handoff.");
        flow.AcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.SuccessCountdown);
        session.Refresh();
        Check(session.Screen == RetailFrontendScreen.Gameplay && !page.Visible, "Incomplete terminal countdown does not show Debriefing.");
        flow.AcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.FrontEndHandoffReady);
        flow.View.SetProcess(false); flow.View.SetProcessInput(false);
        var expected = new RetailFrontendSession();
        for (int index = 0; index < 6; index++) expected.Confirm();
        expected.ConsumeLevel100LaunchRequest();
        expected.CompleteLevel100Load();
        Check(expected.TryAcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.FrontEndHandoffReady),
            "Reference accepts the same synthetic terminal handoff.");
        session.Refresh();
        Check(session.Screen == RetailFrontendScreen.Debriefing && page.Visible && returns == 1 && session.Debriefing == expected.Debriefing,
            "Actual native session remains the sole owner of the settled campaign projection.");
        using Variant snapshotValue = page.Call("view_snapshot");
        using Godot.Collections.Dictionary snapshot = snapshotValue.AsGodotDictionary();
        using Variant projectionValue = snapshot["projection"];
        using Godot.Collections.Dictionary projection = projectionValue.AsGodotDictionary();
        using Godot.Collections.Dictionary exact = RetailFrontendFlow.DebriefingFrame(expected.Debriefing!);
        Check(projection.Count == exact.Count && exact.All(pair => projection.TryGetValue(pair.Key, out Variant value) && value.Equals(pair.Value)), "The production page receives the exact existing projection batch.");
        byte[] beforeFrames = session.SnapshotBytes();
        int calls = flow.NativeCallCount;
        for (int index = 0; index < 3; index++) FrontendHarnessChecks.Command(flow, "advance", 0.125d);
        Check(flow.NativeCallCount == calls + 3 && beforeFrames.SequenceEqual(session.SnapshotBytes()),
            "Three explicit frame batches leave Session untouched and make no extra managed-to-native calls.");
        flow.AcceptWonHandoff(Level100MissionOutcome.Won, Level100MissionTerminalState.FrontEndHandoffReady);
        Check(returns == 1, "Repeated terminal handoff does not apply campaign progress twice.");
    }

    private void CheckProjection(Control page, DebriefingReference reference, Texture2D[] frames)
    {
        foreach (int status in new[] { -1, 0, 1, 2, int.MaxValue })
        foreach (int primary in new[] { 0, 1, 2 })
        foreach (int secondary in new[] { 0, 1, 2 })
        {
            var projection = Projection(status, primary, secondary, null);
            SetFrame(page, projection, "fallback", 1d);
            Check(page.GetNode<Control>("Report/ValuesOrigin").Position.X == reference.LabelColumn, "Measured column is bit-exact against C#.");
            Color expected = RetailColor(status == 2 ? 0xff3fff2fu : status == 1 ? 0xffff3f1fu : 0xff3f3f3fu);
            Check(page.GetNode<Control>("Report/ValuesOrigin/Layout/MissionStatus").Get("_tint").AsColor() == expected,
                "Outcome tint preserves the exact MODULATE2X color words.");
            Check(page.GetNode<Control>("Report/Labels/MissionStatus").Get("ink_color").AsColor() == RetailColor(0xffffaf3f),
                "Label tint preserves its exact MODULATE2X word.");
        }
        Check(page.GetNode<TextureRect>("Writing/Tile0").SelfModulate == RetailColor(0x3e7f7f7f), "Writing retains the current submitted chrome tint.");
        Check(page.GetNode<Control>("Header/Title").Get("ink_color").AsColor() == RetailColor(0xff7f7f7f), "Header retains the current title tint.");
        foreach (double seconds in new[] { 0d, 0.05d, 0.1d, 0.15d, 1d, 19.07d, 67.531d })
        {
            SetFrame(page, Projection(2, 1, 2, (byte)'A'), "", seconds);
            Check(page.GetNode<TextureRect>("Underlay/Video").Texture.GetInstanceId() == frames[LevelSelectReference.FeBackFrameIndex(seconds, frames.Length)].GetInstanceId(),
                "Page selects the same shared FEBack frame at the batched clock.");
        }
    }

    private async Task CheckPixels(Control page, DebriefingReference reference, SubViewport nativeViewport, SubViewport referenceViewport)
    {
        (string Name, RetailDebriefingProjection Projection, string Fallback, double Seconds)[] cases =
        [
            ("aborted-hidden", Projection(0, 0, 0, null), "", 0d),
            ("defeat-secondary", Projection(1, 0, 2, null), "", 1d),
            ("defeat-primary", Projection(1, 2, 0, null), "", 19.07d),
            ("victory-a", Projection(2, 1, 2, (byte)'A'), "", 0d),
            ("victory-b", Projection(2, 2, 1, (byte)'B'), "", 1d),
            ("victory-c", Projection(2, 1, 1, (byte)'C'), "", 19.07d),
            ("victory-d", Projection(2, 2, 2, (byte)'D'), "", 0.15d),
            ("victory-e", Projection(2, 0, 1, (byte)'E'), "", 0.05d),
            ("victory-s", Projection(2, 1, 0, (byte)'S'), "", 67.531d),
            ("raw-unknown-level", Projection(-9, 1, 2, null) with { WorldFinished = 999999 }, "A\0B\ud83d\ude80\ufeff", 1d),
        ];
        foreach (var sample in cases)
        {
            SetFrame(page, sample.Projection, sample.Fallback, sample.Seconds);
            reference.SetFrame(sample.Projection, sample.Fallback, sample.Seconds);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
            using Image actual = nativeViewport.GetTexture().GetImage();
            using Image expected = referenceViewport.GetTexture().GetImage();
            actual.Convert(Image.Format.Rgba8); expected.Convert(Image.Format.Rgba8);
            byte[] actualBytes = actual.GetData(), expectedBytes = expected.GetData();
            int differences = actualBytes.Zip(expectedBytes).Count(pair => pair.First != pair.Second);
            string actualHash = Convert.ToHexString(SHA256.HashData(actualBytes));
            string expectedHash = Convert.ToHexString(SHA256.HashData(expectedBytes));
            SaveOwned(actual, sample.Name + "-native.png");
            SaveOwned(expected, sample.Name + "-reference.png");
            _pixels.Add(new { name = sample.Name, differences, actualHash, expectedHash });
            Check(actualBytes.Any(value => value is > 0 and < 255), "Rendered page is nonblank.");
            Check(actual.GetSize() == expected.GetSize() && actualBytes.Length == expectedBytes.Length && differences == 0,
                $"Full RGBA page equals retained C# for {sample.Name}: {differences} differing bytes.");
        }
    }

    private void SaveOwned(Image image, string name)
    {
        string destination = Path.Combine(_renderDirectory!, name);
        Check(!File.Exists(destination), "Capture refuses overwriting an existing result.");
        Check(image.SavePng(destination) == Error.Ok, "Owned capture saved.");
    }

    private static RetailDebriefingProjection Projection(int status, int primary, int secondary, byte? grade) =>
        new(100, (RetailDebriefingMissionStatus)status, (RetailDebriefingObjectiveSummary)primary,
            (RetailDebriefingObjectiveSummary)secondary, grade, 99, true);

    private static void SetFrame(Control page, RetailDebriefingProjection value, string fallback, double seconds)
    {
        using Godot.Collections.Dictionary projection = RetailFrontendFlow.DebriefingFrame(value);
        using Variant batch = projection;
        using Variant text = fallback.Select(character => (int)character).ToArray();
        using Variant returned = page.Call("set_frame", batch, text, seconds);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        if (!result["ok"].AsBool()) throw new InvalidOperationException(result["error"].AsString());
    }

    private SubViewport MakeViewport()
    {
        var viewport = new SubViewport { Size = new Vector2I(640, 480), Disable3D = true,
            RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
        AddChild(viewport);
        return viewport;
    }

    private static Color RetailColor(uint word) => new(Channel(word >> 16), Channel(word >> 8), Channel(word), ((word >> 24) & 255) / 255f);
    private static float Channel(uint value) => Math.Min(255u, ((value & 255) * 255) >> 7) / 255f;
    private void Check(bool value, string message)
    {
        _checks++;
        if (!value) throw new InvalidOperationException(message);
    }
    private void Complete(string section) { _completed.Add(section); GD.Print("DEBRIEFING_HOST_SECTION: ", section); }
    private void Report(string? error) => GD.Print("DEBRIEFING_HOST_CHECKS: ", System.Text.Json.JsonSerializer.Serialize(new
    { schema = 1, checks = _checks, failure_count = error is null ? 0 : 1, completed = _completed, pixels = _pixels,
        error, runtime = RuntimeInformation.FrameworkDescription, engine = Engine.GetVersionInfo()["string"].AsString() }));
}
