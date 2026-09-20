// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Runtime.InteropServices;
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Actual frontend Options host boundary plus unchanged C# arithmetic/drawing
/// comparisons. This harness never starts a game, audio playback or save writes.
/// Run headlessly; optional pixel comparisons require the caller's isolated display.
/// </summary>
public sealed partial class OptionsBridgeChecks : Node
{
    private int _checks;
    private readonly List<string> _completed = [];
    private readonly List<(string Effect, float Sound, float Music, float Mouse)> _events = [];
    private string? _renderDirectory;

    public override async void _Ready()
    {
        RetailFrontendFlow? view = null;
        try
        {
            foreach (string argument in OS.GetCmdlineUserArgs())
            {
                const string prefix = "--options-font-render-dir=";
                if (!argument.StartsWith(prefix, StringComparison.Ordinal)) continue;
                _renderDirectory = argument[prefix.Length..];
                string owned = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
                Check(Path.IsPathFullyQualified(_renderDirectory) && Path.GetFullPath(_renderDirectory).StartsWith(owned, StringComparison.Ordinal)
                    && Directory.Exists(_renderDirectory), "Render output is an existing task-owned local-data directory.");
                Check(DisplayServer.GetName() != "headless", "Pixel checks require the caller's isolated rendered display.");
            }

            Input.MouseModeEnum pointer = Input.MouseMode;
            view = RetailFrontendFlow.InstantiateScene();
            view.Initialize([]);
            AddChild(view);
            view.SetProcess(false);
            view.SetProcessInput(false);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(typeof(RetailFrontendFlow).GetFields(BindingFlags.NonPublic | BindingFlags.Instance)
                .All(field => field.FieldType != typeof(RetailOptionsMenu)), "Live frontend has no C# Options state owner.");
            Check(view.GetNode<Control>("Stage/Options/Pages").GetChildCount() == 4, "The live frontend embeds the four production Options pages.");
            CheckFonts(view);
            CheckLiveFrontendFonts(view);
            Complete("font_arithmetic");
            CheckUnderlay(view);
            Complete("underlay_arithmetic");
            CheckHostHandoff(view);
            Complete("frontend_handoff");
            CheckHostFailureAndReentry(view);
            Complete("observer_failure_and_reentry");
            if (_renderDirectory is not null)
            {
                await CheckRenderedFonts(view);
                Complete("font_pixels");
            }
            // Inspector borrows above must not dispose the decoded handles
            // still used by the retained C# frontend's ordinary draw paths.
            CheckLiveFrontendFonts(view);
            view.QueueRedraw();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            CheckLiveFrontendFonts(view);
            Check(Input.MouseMode == pointer, "Options frontend initialization and navigation leave pointer mode unchanged.");
            Check(view.FindChildren("*", "AudioStreamPlayer", true, false).Count == 0, "The Options scene does not create an audio playback owner.");
            Check(view.FindChildren("*", "Camera3D", true, false).Count == 0, "Options navigation does not start a game world.");
            view.QueueFree();
            view = null;
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print("OPTIONS_BRIDGE_CHECKS: ", System.Text.Json.JsonSerializer.Serialize(new
            { schema = 1, checks = _checks, failure_count = 0, completed = _completed,
                runtime = RuntimeInformation.FrameworkDescription, engine = Engine.GetVersionInfo()["string"].AsString() }));
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            view?.QueueFree();
            GD.PushError(error.ToString());
            GD.Print("OPTIONS_BRIDGE_CHECKS: ", System.Text.Json.JsonSerializer.Serialize(new
            { schema = 1, checks = _checks, failure_count = 1, completed = _completed, error = error.Message,
                runtime = RuntimeInformation.FrameworkDescription, engine = Engine.GetVersionInfo()["string"].AsString() }));
            GetTree().Quit(1);
        }
    }

    private void CheckFonts(RetailFrontendFlow view)
    {
        int[] units = Enumerable.Range(0, 288).Concat([0x300, 0xd800, 0xdc00, 0xfffd, 0xffff]).ToArray();
        var samples = units.Select(unit => new[] { unit }).ToList();
        samples.AddRange([[], [65, 0, 66], [0xfeff, 65], [65, 0xd83d, 0xde80, 66],
            "Controller Options".Select(c => (int)c).ToArray(), "High (Recommended)".Select(c => (int)c).ToArray()]);
        MethodInfo widthOracle = typeof(RetailFrontendFlow).GetMethod("MeasureGlyphWidths", BindingFlags.NonPublic | BindingFlags.Static)!;
        float[] scales = [0f, 1f, 0.63f, 1.5f, -1f, 0.000001f, 5.7f];
        foreach (bool title in new[] { false, true })
        {
            using Variant fontValue = view.OptionsView.Get(title ? "title_font" : "body_font");
            using Resource font = fontValue.As<Resource>();
            using Variant pageValue = font.Get("page");
            using Texture2D page = pageValue.As<Texture2D>();
            using Image image = page.GetImage();
            int cell = title ? 32 : 16;
            int[] expected = (int[])widthOracle.Invoke(null, [image, cell, 16])!;
            int[] actual = font.Call("glyph_widths").AsInt32Array();
            Check(actual.SequenceEqual(expected), "Every atlas width matches the retained C# scan for " + cell);
            Check(Field<int[]>(view, title ? "_font22Widths" : "_glyphWidths").SequenceEqual(expected), "The retained frontend consumes the same admitted width batch.");
            foreach (int[] sample in samples)
            foreach (float scale in scales)
            {
                float oracle = Measure(sample, expected, scale);
                float value = (float)font.Call("measure", sample, scale).AsDouble();
                Check(BitConverter.SingleToInt32Bits(value) == BitConverter.SingleToInt32Bits(oracle),
                    $"Font {cell} measured extent is bit exact for {sample.Length} units at {scale}.");
            }
            actual[0] = 999;
            Check(font.Call("glyph_widths").AsInt32Array()[0] == expected[0], "Returned font widths are detached.");
        }
        using Variant systemValue = view.OptionsView.Get("bindings_font");
        using Resource system = systemValue.As<Resource>();
        foreach (int[] sample in samples)
            Check(system.Call("measure", sample).AsDouble() == sample.Length * 7f, "SystemFont retains fixed seven-pixel UTF-16 advance.");
    }

    private void CheckLiveFrontendFonts(RetailFrontendFlow view)
    {
        foreach (string field in new[] { "_titleFont", "_font22" })
        {
            Texture2D texture = Field<Texture2D>(view, field);
            Check(GodotObject.IsInstanceValid(texture) && texture.GetRid().IsValid,
                "Temporary font inspection preserves the live frontend handle " + field + ".");
            using Image image = texture.GetImage();
            Check(!image.IsEmpty(), "The retained frontend can still read its decoded font " + field + ".");
        }
    }

    private void CheckUnderlay(RetailFrontendFlow view)
    {
        using GDScript script = GD.Load<GDScript>("res://Scenes/Frontend/frontend_underlay.gd");
        using Godot.Collections.Array tables = script.Call("composite_tables").AsGodotArray();
        float[] gain = [0.2610f, 0.2590f, 0.2420f];
        byte[] fill = [23, 23, 48];
        for (int channel = 0; channel < 3; channel++)
        {
            byte[] actual = tables[channel].AsByteArray();
            Check(actual.Length == 256, "Every byte channel has a complete production composite table.");
            for (int value = 0; value < 256; value++)
            {
                // Original LoadFeBackFrames: the RHS is float before assignment
                // to double. Keep these stores explicit in the comparison.
                float product = gain[channel] * value;
                double composite = fill[channel] + product;
                byte expected = (byte)Math.Clamp(Math.Round(composite), 0d, 255d);
                Check(actual[value] == expected, $"FEBack composite byte {channel}/{value} matches C#.");
            }
        }
        double[] seconds = [-10d, -0d, 0d, 0.016d, 0.05d, 0.083333333d, 0.1d, 0.15d, 0.5d, 1d, 19.07d,
            67.531d, 10_000d, 1e20d, double.NaN, double.PositiveInfinity, double.NegativeInfinity];
        foreach (int count in new[] { -1, 0, 1, 2, 205, 572 })
        foreach (double time in seconds.Concat(Enumerable.Range(0, 90).Select(index => (index + 0.5d) / 30d)))
        {
            int actual = script.Call("frame_index", time, count).AsInt32();
            int expected = RetailFrontendFlow.FeBackFrameIndex(time, count);
            Check(actual == expected, $"FEBack phase matches C# at {time}/{count}: expected {expected}, actual {actual}.");
        }

        Texture2D[] frames = Field<Texture2D[]>(view, "_feBackFrames");
        string path = ProjectSettings.GlobalizePath("res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb");
        byte[] strip = File.ReadAllBytes(path);
        const int frameBytes = 128 * 128 * 3;
        Check(frames.Length == strip.Length / frameBytes && frames.Length > 1, "Live frontend receives the complete production strip.");
        foreach (int frame in new[] { 0, 1, 17, frames.Length - 1 }.Distinct())
        {
            using Image image = frames[frame].GetImage();
            byte[] actual = image.GetData();
            byte[] expected = strip.AsSpan(frame * frameBytes, frameBytes).ToArray();
            for (int index = 0; index < expected.Length; index++)
            {
                int channel = index % 3;
                double value = fill[channel] + gain[channel] * expected[index];
                expected[index] = (byte)Math.Clamp(Math.Round(value), 0d, 255d);
            }
            Check(actual.SequenceEqual(expected), $"Every RGB byte of production frame {frame} matches the retained decoder.");
        }
        foreach (double time in new[] { 0d, 1d, 19.07d })
        {
            view.OptionsView.Call("set_frame", 0.25d, time);
            Texture2D selected = view.OptionsView.GetNode<TextureRect>("Underlay/Video").Texture;
            Check(selected.GetRid() == frames[RetailFrontendFlow.FeBackFrameIndex(time, frames.Length)].GetRid(),
                "Options displays the same production frame instance as the retained frontend.");
        }
    }

    private void CheckHostHandoff(RetailFrontendFlow view)
    {
        view.AudioCueRequested += cue => Record("audio:" + (int)cue, view.OptionsSettings);
        view.OptionsSettingsChanged += settings =>
        {
            Record("settings", settings);
            Check(Same(settings, view.OptionsSettings), "Settings callback and detached getter expose the same source state.");
            settings.SoundVolume = 99f;
            Check(view.OptionsSettings.SoundVolume != 99f, "Host callback cannot mutate the native settings owner.");
        };
        Check(Key(view, Godot.Key.Enter), "Actual frontend accepts click-to-start.");
        view.SelectMainIndexForCapture(5);
        view.ConfirmForSmoke();
        Check(view.CurrentScreen == RetailFrontendScreen.Options, "Actual frontend opens Options.");
        view.SelectOptionsRowForCapture(1);
        view.ConfirmOptionsForCapture();
        Check(view.OptionsView.GetNode<Control>("Pages/Sound").Visible, "Controller state drives the authored Sound page.");
        view.SelectOptionsRowForCapture(1);
        _events.Clear();
        Check(PointerConfirm(view, new Vector2(0f, 196f)), "Actual pointer dispatch selects and decrements the volume bar.");
        Check(_events.Count == 3 && _events[0] == ("audio:0", 0.8f, 0.9f, 7f)
            && _events[1] == ("audio:0", 0.7f, 0.9f, 7f) && _events[2] == ("settings", 0.7f, 0.9f, 7f),
            "Hover Move exposes old settings before adjustment Move and settings handoff.");
        Check(view.OptionsSettings.SoundVolume == 0.7f, "Final native settings survive host snapshot mutation.");
        for (int i = 0; i < 7; i++) Key(view, Godot.Key.Left);
        _events.Clear();
        Check(Key(view, Godot.Key.Left) && _events.Count == 0, "Clamped adjustment is consumed without audio or settings effects.");
        view.SelectOptionsRowForCapture(4);
        Key(view, Godot.Key.Right);
        Key(view, Godot.Key.Enter);
        Check(view.OptionsSettings.SoundQuality == 0, "Closing a deferred dropdown does not hand off its pending setting.");
        view.SelectOptionsRowForCapture(7);
        Key(view, Godot.Key.Enter);
        Check(view.OptionsSettings.SoundQuality == 1, "Apply hands off deferred sound quality.");
        view.SelectOptionsRowForCapture(4);
        Key(view, Godot.Key.Right);
        _events.Clear();
        Check(view.CancelOptionsForCapture(), "The live cancel route closes the expanded dropdown.");
        Check(_events.Count == 1 && _events[0].Effect == "audio:2" && view.OptionsSettings.SoundQuality == 1,
            "Right cancel restores the committed value with Back audio only.");
        _events.Clear();
        view.BackFromOptionsForCapture();
        Check(view.CurrentScreen == RetailFrontendScreen.Options && view.OptionsView.GetNode<Control>("Pages/Root").Visible,
            "Child Back remains within Options.");
        Check(_events.Count == 1 && _events[0].Effect == "audio:2", "Child Back emits one Back cue.");
        _events.Clear();
        view.BackFromOptionsForCapture();
        Check(view.CurrentScreen == RetailFrontendScreen.MainMenu && _events.Count == 1 && _events[0].Effect == "audio:2",
            "Root Back hands control to the existing frontend state owner exactly once.");
        view.SelectMainIndexForCapture(5);
        view.ConfirmForSmoke();
        Check(view.OptionsView.Call("view_snapshot").AsGodotDictionary()["selected_index"].AsInt32() == 0,
            "Entering Options resets root selection.");
        Check(view.OptionsSettings.SoundVolume == 0f && view.OptionsSettings.SoundQuality == 1,
            "Options reentry preserves committed settings.");
        view.BackFromOptionsForCapture();
    }

    private async Task CheckRenderedFonts(RetailFrontendFlow view)
    {
        using GDScript probeScript = GD.Load<GDScript>("res://Scenes/Frontend/Tests/options_font_probe.gd");
        foreach (string name in new[] { "body_font", "title_font", "bindings_font" })
        {
            using Variant fontValue = view.OptionsView.Get(name);
            using Resource font = fontValue.As<Resource>();
            bool system = name == "bindings_font";
            int cell = name == "title_font" ? 32 : 16;
            using Variant pageValue = font.Get("page");
            using Texture2D recipe = pageValue.As<Texture2D>();
            using Variant textureValue = recipe.Call("_texture");
            Texture2D texture = textureValue.As<Texture2D>();
            int[] widths = font.Call("glyph_widths").AsInt32Array();
            int[] units = [32, 65, 77, 0, 66, 127, 161, 255, 287, 288, 0xd83d, 0xde80, 63];
            var native = new Control();
            native.SetScript(probeScript);
            var reference = new OptionsFontReference();
            var nativeViewport = Viewport();
            var referenceViewport = Viewport();
            nativeViewport.AddChild(native);
            referenceViewport.AddChild(reference);
            foreach (bool shadow in new[] { false, true })
            foreach (Vector2 scale in new[] { Vector2.One, new Vector2(0.63f, 1.25f) })
            {
                // The SystemFont consumer has no scale parameter; exercise only
                // its actual fixed-pitch shadowless production path.
                if (system && (shadow || scale != Vector2.One)) continue;
                var origin = new Vector2(7.25f, 9.5f);
                var tint = new Color(0.7f, 0.9f, 0.2f, 0.51f);
                using Variant fontArgument = font;
                native.Call("configure", fontArgument, units, origin, tint, shadow, scale);
                reference.Configure(texture, widths, units, origin, tint, shadow, scale, cell, system);
                await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
                using Image actual = nativeViewport.GetTexture().GetImage();
                using Image expected = referenceViewport.GetTexture().GetImage();
                Check(actual.GetData().SequenceEqual(expected.GetData()), "Native frontend glyph pixels match the retained C# draw law: " + name + "/" + shadow + "/" + scale);
                if (scale == Vector2.One && !shadow)
                {
                    string path = Path.Combine(_renderDirectory!, name + ".png");
                    Check(!File.Exists(path), "Font capture refuses replacing an earlier result.");
                    Check(actual.SavePng(path) == Error.Ok, "Font comparison capture saved in the owned output directory.");
                }
            }
            nativeViewport.QueueFree();
            referenceViewport.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        }
    }

    private void CheckHostFailureAndReentry(RetailFrontendFlow view)
    {
        view.SelectMainIndexForCapture(5);
        view.ConfirmForSmoke();
        view.SelectOptionsRowForCapture(1);
        view.ConfirmOptionsForCapture();
        view.SelectOptionsRowForCapture(1);
        float before = view.OptionsSettings.SoundVolume;
        var audioError = new InvalidOperationException("synthetic audio observer failure");
        void ThrowAudio(RetailFrontendAudioCue cue) { if (cue == RetailFrontendAudioCue.Move) throw audioError; }
        view.AudioCueRequested += ThrowAudio;
        _events.Clear();
        Exception? failure;
        try { failure = ObserveFailure(() => PointerConfirm(view, new Vector2(639f, 196f))); }
        finally { view.AudioCueRequested -= ThrowAudio; }
        Check(ReferenceEquals(failure, audioError), "Native abort rethrows the original audio exception object.");
        Check(view.OptionsSettings.SoundVolume == before && _events.Count == 1,
            "A failed hover cue stops before value adjustment or later settings callbacks.");
        Godot.Collections.Dictionary state = view.OptionsView.Call("view_snapshot").AsGodotDictionary();
        Check(state["selected_index"].AsInt32() == 0 && (float)state["settings"].AsGodotDictionary()["sound_volume"].AsDouble() == before,
            "Audio failure retains the original partial selection mutation and aligned host/native settings.");

        var settingsError = new IOException("synthetic settings observer failure");
        void ThrowSettings(RetailOptionsSettings _) => throw settingsError;
        view.OptionsSettingsChanged += ThrowSettings;
        _events.Clear();
        try { failure = ObserveFailure(() => Key(view, Godot.Key.Right)); }
        finally { view.OptionsSettingsChanged -= ThrowSettings; }
        Check(ReferenceEquals(failure, settingsError), "Native abort rethrows the exact settings exception.");
        state = view.OptionsView.Call("view_snapshot").AsGodotDictionary();
        float changed = (float)state["settings"].AsGodotDictionary()["sound_volume"].AsDouble();
        Check(changed == 0.1f && view.OptionsSettings.SoundVolume == changed && _events.Count == 2,
            "Settings failure retains the already-committed source value and prevents later effects.");

        view.SelectOptionsRowForCapture(1);
        bool nested = false;
        void Reenter(RetailFrontendAudioCue cue)
        {
            if (cue != RetailFrontendAudioCue.Move || nested) return;
            nested = true;
            Key(view, Godot.Key.Right);
        }
        view.AudioCueRequested += Reenter;
        _events.Clear();
        try { Check(PointerConfirm(view, new Vector2(639f, 196f)), "Outer pointer action completes after observer reentry."); }
        finally { view.AudioCueRequested -= Reenter; }
        Check(nested && _events.Count == 5
            && _events[0].Effect == "audio:0" && _events[0].Sound == 0.1f
            && _events[1].Effect == "audio:0" && _events[1].Sound == 0.2f
            && _events[2].Effect == "settings" && _events[2].Sound == 0.2f
            && _events[3].Effect == "audio:0" && _events[3].Sound == 0.3f
            && _events[4].Effect == "settings" && _events[4].Sound == 0.3f,
            "Nested action callbacks retain source ordering and independent effect journals.");
        state = view.OptionsView.Call("view_snapshot").AsGodotDictionary();
        Check(view.OptionsSettings.SoundVolume == 0.3f && (float)state["settings"].AsGodotDictionary()["sound_volume"].AsDouble() == 0.3f,
            "Reentrant actions leave the host cache and native owner aligned.");
        Check(Field<Dictionary<int, System.Runtime.ExceptionServices.ExceptionDispatchInfo>>(view, "_optionsEffectFailures").Count == 0,
            "Handled observer failures leave no retained exception transport records.");
        view.BackFromOptionsForCapture();
        view.BackFromOptionsForCapture();
    }

    private static Exception? ObserveFailure(Action action)
    {
        try { action(); return null; }
        catch (TargetInvocationException error) { return error.InnerException; }
        catch (Exception error) { return error; }
    }

    private SubViewport Viewport()
    {
        var result = new SubViewport { Size = new Vector2I(640, 96), Disable3D = true,
            RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
        AddChild(result);
        return result;
    }
    private static float Measure(int[] text, int[] widths, float scale)
    {
        float width = 0f;
        foreach (int code in text) width += (widths[code >= 32 && code < 288 ? code - 32 : 31] + 1) * scale;
        return Mathf.Max(0f, width - scale);
    }
    private static T Field<T>(object owner, string name) => (T)owner.GetType().GetField(name, BindingFlags.NonPublic | BindingFlags.Instance)!.GetValue(owner)!;
    private static bool Same(RetailOptionsSettings a, RetailOptionsSettings b) => a.SoundVolume == b.SoundVolume
        && a.MusicVolume == b.MusicVolume && a.MouseSensitivity == b.MouseSensitivity && a.SoundQuality == b.SoundQuality && a.VSync == b.VSync;
    private void Record(string effect, RetailOptionsSettings value) => _events.Add((effect, value.SoundVolume, value.MusicVolume, value.MouseSensitivity));
    private static bool Key(RetailFrontendFlow view, Key key)
    {
        using var input = new InputEventKey { Pressed = true, Keycode = key, PhysicalKeycode = key };
        return (bool)typeof(RetailFrontendFlow).GetMethod("HandleKey", BindingFlags.NonPublic | BindingFlags.Instance)!.Invoke(view, [input])!;
    }
    private static bool PointerConfirm(RetailFrontendFlow view, Vector2 point) => (bool)typeof(RetailFrontendFlow)
        .GetMethod("HandleOptionsPointerConfirm", BindingFlags.NonPublic | BindingFlags.Instance)!.Invoke(view, [point])!;
    private void Check(bool condition, string message)
    {
        _checks++;
        if (!condition) throw new InvalidOperationException(message);
    }
    private void Complete(string section) { _completed.Add(section); GD.Print("OPTIONS_BRIDGE_SECTION: ", section); }
}

/// <summary>Unchanged frontend DrawAtlasText/DrawSystemText laws, only in the comparison harness.</summary>
public sealed partial class OptionsFontReference : Control
{
    private Texture2D _atlas = null!;
    private int[] _widths = [], _units = [];
    private Vector2 _origin, _scale;
    private Color _tint;
    private bool _shadow, _system;
    private int _cell;
    public void Configure(Texture2D atlas, int[] widths, int[] units, Vector2 origin, Color tint, bool shadow, Vector2 scale, int cell, bool system)
    {
        _atlas = atlas; _widths = widths; _units = units; _origin = origin; _tint = tint;
        _shadow = shadow; _scale = scale; _cell = cell; _system = system; QueueRedraw();
    }
    public override void _Draw()
    {
        DrawRect(new Rect2(0, 0, 640, 96), new Color(0.09f, 0.09f, 0.19f));
        if (_atlas is null) return;
        float x = _origin.X;
        foreach (int code in _units)
        {
            int glyph = code >= 32 && code < (_system ? 127 : 288) ? code - 32 : 31;
            int width = _system ? 7 : _widths[glyph];
            int columns = _system ? 36 : 16;
            int height = _system ? 9 : _cell;
            var source = new Rect2((glyph % columns) * (_system ? 7 : _cell), (glyph / columns) * height, width, height);
            var destination = new Rect2(x, _origin.Y, width * _scale.X, height * _scale.Y);
            if (_shadow && !_system)
            {
                DrawTextureRectRegion(_atlas, destination, source, new Color(0, 0, 0, _tint.A));
                DrawTextureRectRegion(_atlas, new Rect2(destination.Position - Vector2.One, destination.Size), source, _tint);
            }
            else DrawTextureRectRegion(_atlas, destination, source, _tint);
            x += destination.Size.X + (_system ? 0f : _scale.X);
        }
    }
}
