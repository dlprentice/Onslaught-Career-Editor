// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Tests;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>Fixed-size GPU comparison on an authored feature only; no game data, game launch, career or publication.</summary>
public partial class TerrainFidelityCapture : SceneTree
{
    public override void _Initialize() => _ = CaptureAsync();
    private async Task CaptureAsync()
    {
        int code = 1; SubViewport? outer = null;
        try
        {
            string output = OS.GetCmdlineUserArgs().FirstOrDefault(a => a.StartsWith("--output-dir=", StringComparison.Ordinal))?["--output-dir=".Length..]
                ?? throw new ArgumentException("An owned --output-dir is required.");
            Directory.CreateDirectory(output);
            Stopwatch watch = Stopwatch.StartNew();
            TerrainSurface baseline = TerrainSurface.Build(TerrainSurfaceFidelityTests.Hill, TerrainSurface.DefaultDivisions);
            double baseMs = watch.Elapsed.TotalMilliseconds;
            long before = GC.GetAllocatedBytesForCurrentThread(); watch.Restart();
            TerrainSurface refined = TerrainSurface.BuildPreview(TerrainSurfaceFidelityTests.Hill, baseline);
            double refinedMs = watch.Elapsed.TotalMilliseconds;
            long allocated = GC.GetAllocatedBytesForCurrentThread() - before;
            await ToSignal(this, SignalName.ProcessFrame);
            outer = new SubViewport { Size = new Vector2I(1440, 900), RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
            Root.AddChild(outer);
            ColorRect backdrop = new() { Color = Palette.Background }; outer.AddChild(backdrop); backdrop.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
            MarginContainer margin = Build.Margin(24, 24, 24, 24); outer.AddChild(margin); margin.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
            margin.Theme = CompanionTheme.Build();
            VBoxContainer body = margin.Add(Build.Column(12));
            body.Add(Build.Heading("Terrain preview · authored detail comparison"));
            body.Add(Build.Text("Approximate preview; actual game-ground agreement and clearance remain unverified.", "Warn"));
            body.Add(Build.Text("This authored peak lies between the editable grid's samples. Refinement retains that grid and adds a bounded render/pick patch.", "Muted"));
            HBoxContainer views = body.Add(Build.Row(18)); views.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
            Pane(views, baseline, "Original sampled grid");
            Pane(views, refined, "Bounded adaptive render and pick mesh");
            body.Add(Build.Text("Authored input only · triangles still approximate the height sampler · below-cadence features can remain invisible · terrain edits remain preview-only", "Faint"));
            for (int i = 0; i < 8; i++) await ToSignal(this, SignalName.ProcessFrame);
            await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
            using Image image = outer.GetTexture().GetImage();
            if (image.SavePng(Path.Combine(output, "authored-adaptive-terrain.png")) != Error.Ok) throw new IOException("The authored comparison image could not be saved.");
            using Process process = Process.GetCurrentProcess();
            GD.Print($"TERRAIN_FIDELITY_CAPTURE: base {baseline.Vertices.Length} vertices/{baseline.Indices.Length / 3} triangles/{TerrainSurfaceFidelityTests.MeshPayload(baseline)} estimated mesh-payload bytes; " +
                $"adaptive {refined.Vertices.Length} vertices/{refined.Indices.Length / 3} triangles/{TerrainSurfaceFidelityTests.MeshPayload(refined)} bytes; " +
                $"CPU build {baseMs:0.###}/{refinedMs:0.###} ms, refinement managed allocation {allocated}, process peak working set {process.PeakWorkingSet64}; authored non-quiet capture, no performance acceptance.");
            code = 0;
        }
        catch (Exception error) { GD.PrintErr("TERRAIN_FIDELITY_CAPTURE stopped: " + error); }
        finally
        {
            if (outer is not null) { outer.QueueFree(); await ToSignal(this, SignalName.ProcessFrame); await ToSignal(this, SignalName.ProcessFrame); }
            Quit(code);
        }
    }

    private static void Pane(HBoxContainer row, TerrainSurface surface, string title)
    {
        VBoxContainer column = row.Add(Build.Column(8)); column.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        column.Add(Build.Text(title, "Strong"));
        SubViewportContainer frame = column.Add(new SubViewportContainer { Stretch = true, SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            SizeFlagsVertical = Control.SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(500, 500) });
        SubViewport viewport = new() { OwnWorld3D = true, RenderTargetUpdateMode = SubViewport.UpdateMode.Always }; frame.AddChild(viewport);
        Node3D world = new(); viewport.AddChild(world);
        TerrainPreviewMesh geometry = TerrainPreviewMesh.Build(surface.Vertices.Span, surface.Indices.Span);
        Vector3[] points = geometry.Vertices.Select(p => new Vector3(p.X, p.Y, p.Z)).ToArray();
        Vector3[] normals = geometry.Normals.Select(p => new Vector3(p.X, p.Y, p.Z)).ToArray();
        var arrays = new Godot.Collections.Array(); arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = points; arrays[(int)Mesh.ArrayType.Normal] = normals; arrays[(int)Mesh.ArrayType.Index] = geometry.Indices;
        ArrayMesh mesh = new(); mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        world.AddChild(new MeshInstance3D { Mesh = mesh, MaterialOverride = new StandardMaterial3D
            { AlbedoColor = new Color(0.38f, 0.46f, 0.31f), Roughness = 0.9f, CullMode = BaseMaterial3D.CullModeEnum.Disabled } });
        world.AddChild(new DirectionalLight3D { RotationDegrees = new Vector3(-55, -35, 0), LightEnergy = 1.2f });
        world.AddChild(new WorldEnvironment { Environment = new Godot.Environment
            { BackgroundMode = Godot.Environment.BGMode.Color, BackgroundColor = Palette.Background,
                AmbientLightSource = Godot.Environment.AmbientSource.Color, AmbientLightColor = Colors.White, AmbientLightEnergy = 0.35f } });
        Camera3D camera = new() { Current = true, Fov = 42, Near = 0.1f, Far = 2000 }; world.AddChild(camera);
        Vector3 target = new(TerrainSurfaceFidelityTests.PeakX, 12, -TerrainSurfaceFidelityTests.PeakY);
        camera.Position = target + new Vector3(1, 0.9f, 1).Normalized() * 75; camera.LookAt(target, Vector3.Up);
        column.Add(Build.Text($"{surface.Vertices.Length:N0} vertices · {surface.Indices.Length / 3:N0} triangles · {TerrainSurfaceFidelityTests.MeshPayload(surface):N0} estimated mesh bytes", "Faint"));
    }
}
