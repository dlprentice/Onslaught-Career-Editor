// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Levels;
using Numerics = System.Numerics;
using OnslaughtToolkit.Companion.Missions;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Offscreen production-page evidence using only authored objects/source. No game/profile discovery or runtime loading; the scene comes from
/// the authored loader below, so the linked-map file reads are the tests' to prove. Run with
/// <c>python tools/companion_godot.py capture --capture-script Development/CeMissionProjectCapture.cs --sizes 1280x900,760x800 --beside-gpu-jobs</c>.
/// </summary>
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
        CeMissionProjectPage page = new(status, popups, (_, _, _) => throw new InvalidOperationException("Unexpected discard request."),
            sceneLoader: (_, project) => AuthoredScene(project.Map?.Level ?? throw new InvalidOperationException("Authored map link required.")));
        column.AddChild(page.Root); page.Root.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        viewport.AddChild(status.Root); status.Root.Visible = false;
        try
        {
            await Frames(3);
            Text(page.ProjectName, "Harbour escort"); Press(page.Apply);
            Text(page.ObjectName, "Rendezvous beacon"); Text(page.Definition, "project.beacon"); Press(page.AddObject);
            string beacon = page.Editor.Current.Placements.Single().Id;
            Text(page.X, Coordinate(40 * Scale)); Text(page.Y, Coordinate(60 * Scale)); Press(page.Apply);
            Text(page.MapLevel, "777"); Text(page.MapObject, "AuthoredBeacon"); Press(page.LinkMapObject);
            Text(page.SourceName, "Arrival"); Press(page.AddSource);
            page.Source.Text = "// Harbour escort: authored mission source\n// The beacon marks the rendezvous.\n// Source is preserved; this placement consumer does not execute it.\n";
            page.Source.EmitSignal(TextEdit.SignalName.TextChanged); Press(page.Apply);
            Press(page.Bind); page.EntrySource.ButtonPressed = true;
            Text(page.ObjectName, "Escort start"); Text(page.Definition, "project.escort"); Press(page.AddObject);
            Text(page.X, Coordinate(70 * Scale)); Text(page.Y, Coordinate(95 * Scale)); Press(page.Apply);
            Text(page.MapObject, "AuthoredEscort"); Press(page.LinkMapObject);
            int row = page.Editor.Current.Placements.ToList().FindIndex(item => item.Id == beacon);
            page.Objects.EmitSignal(ItemList.SignalName.ItemSelected, row);
            string sceneRoot = Path.Combine(output, "scene-source.authored");
            Directory.CreateDirectory(sceneRoot);
            page.LinkedMapDialog.EmitSignal(FileDialog.SignalName.DirSelected, sceneRoot);
            await Settled(page);
            if (page.LinkedScene is null) throw new InvalidOperationException("The authored linked scene did not load: " + page.Notice);
            await Frames(4);
            MeshInstance3D[] geometry = page.View.FindChildren("*", nameof(MeshInstance3D), true, false).OfType<MeshInstance3D>().ToArray();
            if (page.View.LinkedModelCount != 3 || geometry.Count(item => item.Mesh is { } mesh && mesh.GetSurfaceCount() > 0) < 4)
                throw new InvalidOperationException("The linked terrain and all three authored object models must be real scene geometry.");
            Node3D[] models = page.View.FindChildren("*", nameof(Node3D), true, false).OfType<LinkedSceneModelLayer>().Single().GetChildren().OfType<Node3D>().ToArray();
            Camera3D camera = page.View.FindChildren("*", nameof(Camera3D), true, false).OfType<Camera3D>().Single();
            if (!page.View.TryGetMarkerPoint(row, out Vector2 start)) throw new InvalidOperationException("The authored object is not visible.");
            Vector2 target = camera.UnprojectPosition(new Vector3(96 * Scale, AuthoredGround(96 * Scale, 88 * Scale), -88 * Scale));
            Pointer(page.View, start, start, false); Button(page.View, start, true);
            Pointer(page.View, start, target, true); Button(page.View, target, false);
            var moved = page.Editor.Current.Placement(beacon).Position;
            if (Math.Abs(moved.X - 96 * Scale) > 0.03f || Math.Abs(moved.Y - 88 * Scale) > 0.03f)
                throw new InvalidOperationException("The real 3D pointer drop did not update the authored object.");
            await Frames(2);
            if (!models[1].Position.IsEqualApprox(LinkedSceneCoordinates.View(moved)) || !models[0].Position.IsEqualApprox(LinkedSceneCoordinates.View(BaseBeacon)))
                throw new InvalidOperationException("The drop must move the bound model and leave the base-world model of that name in place.");
            string label = size.X + "x" + size.Y;
            string path = Path.Combine(output, "authored-" + label + ".ceproject");
            byte[] expected = CeMissionProjectJson.Write(page.Editor.Current);
            if (!await page.SaveFileAsync(path) || !await page.OpenFileAsync(path) ||
                !CeMissionProjectJson.Write(page.Editor.Current).AsSpan().SequenceEqual(expected))
                throw new InvalidOperationException("The authored project did not save and reopen exactly.");
            page.Objects.EmitSignal(ItemList.SignalName.ItemSelected, row);
            Press(page.ReloadLinkedMap);
            await Settled(page);
            if (page.LinkedScene is null) throw new InvalidOperationException("The reopened project did not reload its explicit local scene: " + page.Notice);
            page.ObjectName.GrabFocus();
            await Shot(viewport, output, "placement-" + label);
            page.MapObject.GrabFocus();
            await Shot(viewport, output, "map-link-" + label);
            Vector2 coordinatesAt = page.X.GlobalPosition;
            page.Source.GrabFocus();
            await Shot(viewport, output, "source-" + label);
            if (page.X.GlobalPosition != coordinatesAt || new[] { page.X, page.Y, page.Z }.Any(field =>
                field.GetParent().GetParent() is not HBoxContainer row || row.GlobalPosition.Y < page.Root.GlobalPosition.Y ||
                row.GetGlobalRect().End.Y > page.Root.GetGlobalRect().End.Y))
                throw new InvalidOperationException("The coordinate labels and fields must stay visible while mission source has focus.");
            GD.Print("CE_PROJECT_CAPTURE verified linked terrain/model geometry, spatial drag, preserved source and file round trip at " + label);
            return 3;
        }
        finally { viewport.QueueFree(); await Frames(3); }
    }

    private static float Scale => Heightfield.Size / 128f;
    private static string Coordinate(float value) => value.ToString("R", System.Globalization.CultureInfo.InvariantCulture);

    // A base-world object with the bound object's name, so each picture shows which of the two a placement moves.
    private static Numerics.Vector3 BaseBeacon => new(18 * Scale, 100 * Scale, 0);

    private static CeLinkedSceneSnapshot AuthoredScene(int level) => new(level, AuthoredTerrain(),
        [new("scene_base_beacon", "AuthoredBeacon", "original.authored.base", "authored-pyramid", BaseBeacon, new(0.2f, 0, 0), FromBaseWorld: true),
         new("scene_beacon", "AuthoredBeacon", "original.authored.beacon", "authored-pyramid", new(40 * Scale, 60 * Scale, 0), new(0.6f, 0, 0), FromBaseWorld: false),
         new("scene_escort", "AuthoredEscort", "original.authored.escort", "authored-pyramid", new(70 * Scale, 95 * Scale, 0), new(-0.4f, 0.1f, 0), FromBaseWorld: false)],
        [CeLinkedSceneModel.FromMesh("authored-pyramid", AuthoredModel())]);

    // The lower half is flat for the actual drag/drop; a sampled hill makes terrain depth visible behind it.
    private static float AuthoredGround(float x, float y)
    {
        float u = x / Scale, v = y / Scale;
        if (v >= 54) return 0;
        float a = MathF.Sin(MathF.PI * u / 128), b = MathF.Sin(MathF.PI * v / 54);
        return 30 * Scale * a * a * b * b;
    }

    private static TerrainSurface AuthoredTerrain() => TerrainSurface.Build((x, y) => -AuthoredGround(x, y), 32);

    private static CmshMesh AuthoredModel()
    {
        Numerics.Vector3[] corners = [new(-7, -5, 0), new(7, -5, 0), new(7, 5, 0), new(-7, 5, 0), new(2, -1, -20)];
        Numerics.Vector3 centre = corners.Aggregate(Numerics.Vector3.Zero, (sum, point) => sum + point) / corners.Length;
        List<Numerics.Vector3> positions = [], normals = [];
        List<uint> colors = [];
        List<CmshPiece> pieces = [];
        foreach ((int first, int second, int third) in new[] { (0, 4, 1), (1, 4, 2), (2, 4, 3), (3, 4, 0), (0, 1, 2), (0, 2, 3) })
        {
            Numerics.Vector3 a = corners[first], b = corners[second], c = corners[third];
            Numerics.Vector3 normal = Numerics.Vector3.Normalize(Numerics.Vector3.Cross(b - a, c - a));
            if (Numerics.Vector3.Dot(normal, (a + b + c) / 3 - centre) < 0) { (b, c) = (c, b); normal = -normal; }
            int at = positions.Count;
            positions.AddRange([a * Scale, b * Scale, c * Scale]);
            normals.AddRange([normal, normal, normal]);
            uint color = (255u << 24) | (220u << 16) | (150u << 8) | 56u;
            colors.AddRange([color, color, color]);
            pieces.Add(new([(ushort)at, (ushort)(at + 1), (ushort)(at + 2)], [-1, -1, -1]));
        }
        return new CmshMesh
        {
            Name = "Authored beacon model", Textures = [], Modes = [],
            Parts = [new CmshPart
            {
                Index = 0, Name = "Authored pyramid", Type = (int)PartType.Normal, VirtualFrames = 1, CachedFrameCount = 0,
                Positions = positions.ToArray(), Normals = normals.ToArray(), Colors = colors.ToArray(), UVs = new Numerics.Vector2[positions.Count],
                Pieces = pieces.ToArray(),
            }],
        };
    }

    private async Task Shot(SubViewport viewport, string output, string name)
    {
        await Frames(3);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image image = viewport.GetTexture().GetImage();
        if (image.SavePng(Path.Combine(output, name + ".png")) != Error.Ok) throw new IOException("The capture could not be saved.");
    }
    private async Task Settled(CeMissionProjectPage page) { while (page.Busy) await Frames(1); }
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
