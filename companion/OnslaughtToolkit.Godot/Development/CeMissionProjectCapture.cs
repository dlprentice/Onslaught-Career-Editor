// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Missions;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>Offscreen production-page evidence using only authored objects/source. No game/profile discovery or runtime loading.</summary>
public partial class CeMissionProjectCapture : SceneTree
{
    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exit = 1;
        try
        {
            string output = "", sizes = "1280x900,760x800";
            foreach (string argument in OS.GetCmdlineUserArgs())
            {
                if (argument.StartsWith("--output=", StringComparison.Ordinal)) output = argument[9..];
                if (argument.StartsWith("--sizes=", StringComparison.Ordinal)) sizes = argument[8..];
            }
            if (!Path.IsPathFullyQualified(output))
                throw new InvalidOperationException("A full owned --output folder is required.");
            Directory.CreateDirectory(output);
            int shots = 0;
            foreach (string specification in sizes.Split(','))
            {
                string[] size = specification.Split('x');
                shots += await Capture(output, new Vector2I(int.Parse(size[0]), int.Parse(size[1])));
            }
            GD.Print($"CAPTURES_DONE {shots} authored project screens in {output}");
            exit = 0;
        }
        catch (Exception error) { GD.PrintErr("CE_PROJECT_CAPTURE stopped: " + error); }
        finally { Quit(exit); }
    }

    private async Task<int> Capture(string output, Vector2I size)
    {
        SubViewport viewport = new() { Size = size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always,
            TransparentBg = false, GuiEmbedSubwindows = true };
        Root.AddChild(viewport);
        PanelContainer background = new() { Theme = CompanionTheme.Build() };
        viewport.AddChild(background); background.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        VBoxContainer column = background.Add(Build.Margin(16, 16, 16, 16)).Add(Build.Column(10));
        column.Add(Build.Heading("Mission project", "Title"));
        Control popups = new(); viewport.AddChild(popups);
        StatusLine status = new();
        CeMissionProjectPage page = new(status, popups, (_, _, _) => throw new InvalidOperationException("Unexpected discard request."));
        column.AddChild(page.Root); page.Root.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        viewport.AddChild(status.Root); status.Root.Visible = false;
        try
        {
            await Frames(3);
            Text(page.ProjectName, "Harbour escort"); Press(page.Apply);
            Text(page.ObjectName, "Rendezvous beacon"); Text(page.Definition, "project.beacon"); Press(page.AddObject);
            string beacon = page.Editor.Current.Placements.Single().Id;
            Text(page.X, "40"); Text(page.Y, "60"); Press(page.Apply);
            Text(page.SourceName, "Arrival"); Press(page.AddSource);
            page.Source.Text = "// Harbour escort: authored mission source\n// The beacon marks the rendezvous.\n// Attach behaviour when the CE runtime contract is ready.\n";
            page.Source.EmitSignal(TextEdit.SignalName.TextChanged); Press(page.Apply);
            Press(page.Bind); page.EntrySource.ButtonPressed = true;
            Text(page.ObjectName, "Escort start"); Text(page.Definition, "project.escort"); Press(page.AddObject);
            Text(page.X, "70"); Text(page.Y, "95"); Press(page.Apply);
            int row = page.Editor.Current.Placements.ToList().FindIndex(item => item.Id == beacon);
            page.Objects.EmitSignal(ItemList.SignalName.ItemSelected, row);
            await Frames(3);
            Camera3D camera = page.View.FindChildren("*", nameof(Camera3D), true, false).OfType<Camera3D>().Single();
            if (!page.View.TryGetMarkerPoint(row, out Vector2 start)) throw new InvalidOperationException("The authored object is not visible.");
            Vector2 target = camera.UnprojectPosition(new Vector3(96, 0, -88));
            Pointer(page.View, start, start, false); Button(page.View, start, true);
            Pointer(page.View, start, target, true); Button(page.View, target, false);
            var moved = page.Editor.Current.Placement(beacon).Position;
            if (Math.Abs(moved.X - 96) > 0.03f || Math.Abs(moved.Y - 88) > 0.03f)
                throw new InvalidOperationException("The real 3D pointer drop did not update the authored object.");
            string label = size.X + "x" + size.Y;
            string path = Path.Combine(output, "authored-" + label + ".ceproject");
            byte[] expected = CeMissionProjectJson.Write(page.Editor.Current);
            if (!await page.SaveFileAsync(path) || !await page.OpenFileAsync(path) ||
                !CeMissionProjectJson.Write(page.Editor.Current).AsSpan().SequenceEqual(expected))
                throw new InvalidOperationException("The authored project did not save and reopen exactly.");
            page.Objects.EmitSignal(ItemList.SignalName.ItemSelected, row);
            page.ObjectName.GrabFocus();
            await Shot(viewport, output, "placement-" + label);
            page.Source.GrabFocus();
            await Shot(viewport, output, "source-" + label);
            GD.Print("CE_PROJECT_CAPTURE verified authored placement, source link and file round trip at " + label);
            return 2;
        }
        finally { viewport.QueueFree(); await Frames(3); }
    }

    private async Task Shot(SubViewport viewport, string output, string name)
    {
        await Frames(3);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image image = viewport.GetTexture().GetImage();
        if (image.SavePng(Path.Combine(output, name + ".png")) != Error.Ok) throw new IOException("The capture could not be saved.");
    }
    private async Task Frames(int count)
    { for (int index = 0; index < count; index++) await ToSignal(this, SignalName.ProcessFrame); }
    private static void Text(LineEdit field, string text) { field.Text = text; field.EmitSignal(LineEdit.SignalName.TextChanged, text); }
    private static void Press(Button button)
    {
        if (button.Disabled) throw new InvalidOperationException("The requested page action is unavailable: " + button.Text);
        button.EmitSignal(BaseButton.SignalName.Pressed);
    }
    private static void Button(LevelTerrainViewport view, Vector2 local, bool pressed)
    {
        Vector2 point = view.GlobalPosition + local;
        view.GetViewport().PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = MouseButton.Left,
            Pressed = pressed, ButtonMask = pressed ? MouseButtonMask.Left : 0 }, true);
    }
    private static void Pointer(LevelTerrainViewport view, Vector2 from, Vector2 to, bool held)
    {
        Vector2 point = view.GlobalPosition + to;
        view.GetViewport().PushInput(new InputEventMouseMotion { Position = point, GlobalPosition = point, Relative = to - from,
            ButtonMask = held ? MouseButtonMask.Left : 0 }, true);
    }
}
