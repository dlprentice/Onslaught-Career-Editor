// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtToolkit.Companion.Missions;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Explicit local-only installed-model evidence. The production page reads the selected game and project, changes one
/// placement in memory and writes only a new project and captures below the caller's output. No game is started.
/// Captures contain the selected installation's assets and belong in private local evidence, never in Git or a package.
/// </summary>
public partial class CeInstalledSceneCapture : SceneTree
{
    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exit = 1;
        try
        {
            string Arg(string name) => OS.GetCmdlineUserArgs().SingleOrDefault(a => a.StartsWith(name + "=", StringComparison.Ordinal))?[(name.Length + 1)..]
                ?? throw new InvalidOperationException("Missing explicit capture input: " + name);
            string output = Arg("--output"), game = Arg("--game"), project = Arg("--project");
            if (!Path.IsPathFullyQualified(output) || !Path.IsPathFullyQualified(game) || !Path.IsPathFullyQualified(project))
                throw new InvalidOperationException("Capture paths must be absolute.");
            Directory.CreateDirectory(output);
            await Capture(output, game, project);
            GD.Print("CAPTURES_DONE 2 installed-model screens; private local evidence only");
            exit = 0;
        }
        catch (Exception error) { GD.PrintErr("INSTALLED_SCENE_CAPTURE stopped: " + error); }
        finally { Quit(exit); }
    }

    private async Task Capture(string output, string game, string projectPath)
    {
        SubViewport viewport = new() { Size = new(1440, 1000), RenderTargetUpdateMode = SubViewport.UpdateMode.Always, GuiEmbedSubwindows = true };
        Root.AddChild(viewport);
        PanelContainer background = new() { Theme = CompanionTheme.Build() };
        viewport.AddChild(background); background.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        VBoxContainer column = background.Add(Build.Margin(16, 16, 16, 16)).Add(Build.Column(10));
        column.Add(Build.Heading("Mission project · installed model preview", "Title"));
        Control popups = new(); viewport.AddChild(popups);
        StatusLine status = new();
        CeMissionProjectPage page = new(status, popups, (_, _, _) => throw new InvalidOperationException("Unexpected discard request."));
        column.AddChild(page.Root); page.Root.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        viewport.AddChild(status.Root); status.Root.Visible = false;
        try
        {
            await Frames(3);
            if (!await page.OpenFileAsync(projectPath) || !await page.LoadLinkedSceneAsync(game))
                throw new InvalidOperationException("The explicit installed project did not load: " + page.Notice);
            await Frames(4);
            CeLinkedSceneSnapshot initial = page.LinkedScene ?? throw new InvalidOperationException("No linked scene.");
            CeLinkedSceneInstance bound = initial.Instances(page.Editor.Current).FirstOrDefault(i => i.PlacementIndex is not null && i.Source.ModelKey is not null)
                ?? throw new InvalidOperationException("This project has no placement with resolved model geometry.");
            int row = bound.PlacementIndex!.Value;
            page.Objects.EmitSignal(ItemList.SignalName.ItemSelected, row);
            LinkedSceneModelLayer layer = page.View.FindChildren("*", nameof(Node3D), true, false).OfType<LinkedSceneModelLayer>().Single();
            Node3D[] models = layer.GetChildren().OfType<Node3D>().ToArray();
            Node3D actor = models.Single(n => n.Position.IsEqualApprox(LinkedSceneCoordinates.View(bound.Position)) &&
                n.Basis.IsEqualApprox(LinkedSceneCoordinates.Transform(bound.Source.Orientation, bound.Position).Basis));
            int geometries = actor.FindChildren("*", nameof(MeshInstance3D), true, false).OfType<MeshInstance3D>().Count(m => m.Mesh is { } mesh && mesh.GetSurfaceCount() > 0);
            if (page.View.LinkedModelCount == 0 || geometries == 0 || initial.Models.Any(m => m.Source is null))
                throw new InvalidOperationException("Installed models must be real geometry with local source identities.");
            await Shot(viewport, Path.Combine(output, "installed-overview.png"));

            CeMissionPlacement original = page.Editor.Current.Placements[row];
            var moved = original.Position + new System.Numerics.Vector3(2, 0, 0);
            if (!page.Editor.TryMovePlacement(original.Id, moved, page.Editor.Revision, out _) || !page.Editor.Undo() || !page.Editor.Redo())
                throw new InvalidOperationException("The installed model placement must support move, Undo and Redo.");
            await Frames(3);
            if (!actor.Position.IsEqualApprox(LinkedSceneCoordinates.View(moved))) throw new InvalidOperationException("The live model did not follow the placement.");
            byte[] expected = CeMissionProjectJson.Write(page.Editor.Current);
            string saved = Path.Combine(output, "installed-placement.ceproject");
            if (!await page.SaveFileAsync(saved) || !await page.OpenFileAsync(saved) || !await page.LoadLinkedSceneAsync(game) ||
                !CeMissionProjectJson.Write(page.Editor.Current).AsSpan().SequenceEqual(expected))
                throw new InvalidOperationException("The installed model project failed its Save/Open round trip.");
            await Frames(4);
            CeLinkedSceneSnapshot reopened = page.LinkedScene!;
            if (!initial.Models.Select(m => m.Source).SequenceEqual(reopened.Models.Select(m => m.Source)) ||
                reopened.Instances(page.Editor.Current).Single(i => i.PlacementIndex == row).Position != moved)
                throw new InvalidOperationException("Save/Open changed the installed model or placement identity.");
            page.Objects.EmitSignal(ItemList.SignalName.ItemSelected, row);

            // A second evidence image frames the selected model directly. This is capture framing, not an editor control claim.
            layer = page.View.FindChildren("*", nameof(Node3D), true, false).OfType<LinkedSceneModelLayer>().Single();
            actor = layer.GetChildren().OfType<Node3D>().Single(n => n.Position.IsEqualApprox(LinkedSceneCoordinates.View(moved)) &&
                n.Basis.IsEqualApprox(LinkedSceneCoordinates.Transform(bound.Source.Orientation, moved).Basis));
            MeshInstance3D[] pieces = actor.FindChildren("*", nameof(MeshInstance3D), true, false).OfType<MeshInstance3D>().ToArray();
            Aabb bounds = pieces.Select(m => m.GlobalTransform * m.GetAabb()).Aggregate((a, b) => a.Merge(b));
            Camera3D camera = page.View.FindChildren("*", nameof(Camera3D), true, false).OfType<Camera3D>().Single();
            float distance = Math.Max(8, bounds.Size.Length() * 1.8f);
            camera.Position = bounds.GetCenter() + new Vector3(0.6f, 0.6f, 0.7f).Normalized() * distance;
            camera.LookAt(bounds.GetCenter(), Vector3.Up);
            await Shot(viewport, Path.Combine(output, "installed-selected.png"));
            File.WriteAllText(Path.Combine(output, "result.private.json"), JsonSerializer.Serialize(new
            {
                status = "pass", level = initial.Level, objects = initial.Objects.Count, models = initial.Models.Count,
                instances = page.View.LinkedModelCount, selectedGeometryParts = geometries, notes = initial.Notes.Count,
                placementMoveUndoRedo = true, saveOpenSourceIdentity = true,
                projectSha256 = Convert.ToHexStringLower(SHA256.HashData(expected)),
                modelSourceIdentities = initial.Models.Select(m => m.Source).ToArray(),
                scope = "Production page, installed static untextured models, scripted inputs; no game, animation, human-input or Windows acceptance."
            }, new JsonSerializerOptions { WriteIndented = true }) + "\n");
            GD.Print($"INSTALLED_SCENE_CAPTURE pass objects={initial.Objects.Count} models={initial.Models.Count} instances={page.View.LinkedModelCount}");
        }
        finally { viewport.QueueFree(); await Frames(3); }
    }

    private async Task Frames(int count) { for (int i = 0; i < count; i++) await ToSignal(this, SignalName.ProcessFrame); }
    private async Task Shot(SubViewport viewport, string file)
    {
        await Frames(3);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image image = viewport.GetTexture().GetImage();
        if (image.SavePng(file) != Error.Ok) throw new IOException("Could not write the private capture.");
    }
}
