// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;
using System.Text;
using Godot;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Missions;
using OnslaughtToolkit.Companion.Ui;
using Position = System.Numerics.Vector3;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Selected-map reads and actual Godot model instances on authored terrain/CMSH only.</summary>
internal static class CeLinkedSceneTests
{
    internal static CeMissionProject Project(Position position) => new("linked_preview", "Authored linked preview",
        [new("anchor", "Authored anchor", "authored.anchor", position)], [], map: new(777, [new("authored.anchor", "AuthoredAnchor")]));

    /// <summary>A world of two authored objects that keep their own names, positions and mesh reference.</summary>
    internal static WorldBody AnchorBody()
    {
        WorldBody body = WorldBody.Read(LevelTests.Body("authored-v50"));
        PlacedObject anchor = body.Things[0].Clone();
        anchor.Init.Name = "AuthoredAnchor";
        anchor.Init.Position = new(8, 9, -2);
        anchor.Init.Orientation = new(0.37f, -0.22f, 0.41f);
        anchor.Init.MeshNumber = 0;
        body.NamedMeshes.Clear(); body.NamedMeshes.Add("authored.msh");
        body.TreeGroups.Clear(); body.TreeTypes.Clear();
        body.Things.Clear(); body.Things.Add(anchor);
        PlacedObject other = anchor.Clone(); other.Init.Name = "OtherAnchor"; other.Init.Position = new(11, 12, -3);
        body.Things.Add(other);
        return body;
    }

    internal static async Task RunAsync(SceneTree tree, string output, Checks check)
    {
        check.Suite("linked-map scene");
        await Loader(Path.Combine(output, "linked-scene-input"), check);
        CeLinkedSceneInputTests.Run(output, check);
        check.Suite("linked-map scene");
        Coordinates(check);
        await Viewport(tree, check);
        await BaseWorldModel(tree, check);
    }

    private static async Task Loader(string root, Checks check)
    {
        string resources = Path.Combine(root, "DaTa", "Resources");
        string meshes = Path.Combine(resources, "MeShEs");
        Directory.CreateDirectory(meshes);
        WorldBody body = AnchorBody();
        PlacedObject anchor = body.Things[0], other = body.Things[1];
        string archive = Path.Combine(resources, "777_res_PC.aya"), modelFile = Path.Combine(meshes, "M_Authored.MSH.AYA");
        byte[] archiveBytes = Archive(body.Write());
        File.WriteAllBytes(archive, archiveBytes);
        File.WriteAllBytes(modelFile, AssetTests.Member(AssetTests.TwoPartMesh(animated: true)));
        string before = Hash(archive) + Hash(modelFile);
        CeMissionProject project = Project(new(12, 13, -4));
        CeLinkedSceneSnapshot scene = await Task.Run(() => CeLinkedSceneLoader.Load(root, project));
        check.That(scene.Level == 777 && scene.Terrain.Vertices.Length > 4 &&
            scene.Terrain.Vertices.Span.ToArray().Select(v => v.Y).Distinct().Count() > 1,
            "selected archive loads nonflat sampled terrain on a worker thread");
        check.That(scene.Objects.Count == 2 && scene.Models.Count == 1 && scene.Notes.Count == 0,
            "only the selected map and its explicitly referenced mesh are loaded with case-insensitive names");
        IReadOnlyList<CeLinkedSceneInstance> instances = scene.Instances(project);
        check.That(instances[0].Position == project.Placements[0].Position && instances[0].Source.Orientation == anchor.Init.Orientation &&
            instances[1].Position == other.Init.Position && instances[1].PlacementIndex is null,
            "bound position edits retain original orientation and leave other installed objects in place");
        using (GltfDocument document = new())
        using (GltfState state = new())
            check.That(document.AppendFromBuffer(scene.Models[0].Glb.ToArray(), "", state) == Error.Ok && state.GetAnimations().Count == 0,
                "the loaded CMSH becomes actual static model geometry without animation export");
        byte[] caller = scene.Models[0].Glb.ToArray();
        CeLinkedSceneModel captured = new("captured", caller); byte first = captured.Glb.Span[0]; caller[0] ^= 1;
        check.That(captured.Glb.Span[0] == first && before == Hash(archive) + Hash(modelFile),
            "model bytes are independently owned and source map/model files remain unchanged");

        CeMissionProject repeated = new(project.Id, project.Name,
            project.Placements.Append(project.Placements[0] with { Id = "duplicate" }), [], map: project.Map);
        check.That(scene.Instances(repeated)[0].Position == anchor.Init.Position && scene.Instances(repeated)[0].PlacementIndex is null,
            "an ambiguous authoring draft keeps the original object and creates no model clone");
        CeMissionProject unbound = new(project.Id, project.Name,
            project.Placements.Append(new("unbound", "Unbound draft", "authored.other", Position.One)), [], map: project.Map);
        check.That(scene.Instances(unbound).Count == 2 && scene.Instances(unbound).Count(item => item.PlacementIndex is not null) == 1,
            "an unbound added draft does not manufacture installed model geometry");
        Refuses(check, () => scene.Instances(new(project.Id, project.Name, project.Placements, [], map: new(778, project.Map!.Bindings))),
            "a snapshot cannot be rebound to another level");
        Refuses(check, () => scene.Instances(new(project.Id, project.Name, project.Placements, [], map: new(777, [new("authored.anchor", "Missing")]))),
            "a missing named installed object is refused");

        string fallback = Path.Combine(root, "fallback"), worlds = Path.Combine(fallback, "data", "worlds");
        Directory.CreateDirectory(Path.Combine(fallback, "data", "resources", "meshes")); Directory.CreateDirectory(worlds);
        File.WriteAllBytes(Path.Combine(fallback, "data", "resources", "777_res_pc.aya"), Archive(null));
        File.WriteAllBytes(Path.Combine(worlds, "world777.wrd"), body.Write());
        CeLinkedSceneSnapshot loose = CeLinkedSceneLoader.Load(fallback, project);
        check.That(loose.Objects.Count == 2 && loose.Models.Count == 0 && loose.Notes.Count == 1,
            "a selected loose world is read while an unavailable referenced model is reported explicitly");
        WorldBody baseBody = WorldBody.Read(body.Write()); baseBody.Things.RemoveAt(0);
        baseBody.Things[0].Init.Name = "BaseOnly";
        File.WriteAllBytes(Path.Combine(fallback, "data", "resources", "777_res_pc.aya"), Archive(body.Write(), baseBody.Write()));
        CeLinkedSceneSnapshot withBase = CeLinkedSceneLoader.Load(fallback, project);
        check.That(withBase.Objects.Count == 3 && withBase.Objects[0].Id == "base:0" && withBase.Objects[1].Id == "level:0",
            "embedded base and selected worlds keep separate stable object identities");
        File.WriteAllBytes(Path.Combine(worlds, "world000.wrd"), baseBody.Write());
        File.WriteAllBytes(Path.Combine(fallback, "data", "resources", "777_res_pc.aya"), Archive(body.Write(), baseLevel: 0));
        check.That(CeLinkedSceneLoader.Load(fallback, project).Objects.Count == 3,
            "base level zero uses its selected loose fallback rather than being mistaken for no base");
        other.Init.MeshNumber = -1;
        File.WriteAllBytes(Path.Combine(worlds, "world777.wrd"), body.Write());
        File.WriteAllBytes(Path.Combine(fallback, "data", "resources", "777_res_pc.aya"), Archive(null));
        CeLinkedSceneSnapshot omitted = CeLinkedSceneLoader.Load(fallback, project);
        check.That(omitted.Objects[1].ModelKey is null && omitted.Notes.Any(note => note.Contains("no stored model reference", StringComparison.Ordinal)),
            "objects whose geometry is selected elsewhere are explicitly reported rather than assigned an invented mesh");
        other.Init.MeshNumber = 7;
        File.WriteAllBytes(Path.Combine(worlds, "world777.wrd"), body.Write());
        CeLinkedSceneSnapshot unresolved = CeLinkedSceneLoader.Load(fallback, project);
        check.That(unresolved.Objects[1].ModelKey is null && unresolved.Notes.Any(note => note.Contains("outside this world's own model list", StringComparison.Ordinal)) &&
            !unresolved.Notes.Any(note => note.Contains("no stored model reference", StringComparison.Ordinal)),
            "a model number beyond the world's own model list is reported as unresolved, not as a missing reference");
        SelectedLevelBindings(root, check);
        if (OperatingSystem.IsLinux())
        {
            string linked = Path.Combine(root, "linked-input"); Directory.CreateSymbolicLink(linked, root);
            Refuses(check, () => CeLinkedSceneLoader.Load(linked, project), "linked input folders are refused");
            Refuses(check, () => CeLinkedSceneLoader.Load(linked + Path.DirectorySeparatorChar, project), "a final separator does not hide a linked input folder");
            File.WriteAllBytes(Path.Combine(resources, "777_res_pc.aya"), archiveBytes);
            Refuses(check, () => CeLinkedSceneLoader.Load(root, project), "case-ambiguous selected archives are refused");
        }
    }

    /// <summary>
    /// The binding rule CE's PortCeProjectApplyPlacement and PortCeProjectEndWorld apply: base-world objects are skipped,
    /// a placement's object must appear exactly once in the selected level, and a binding no placement uses is never read.
    /// </summary>
    private static void SelectedLevelBindings(string root, Checks check)
    {
        string game = Path.Combine(root, "selected-level"), resources = Path.Combine(game, "data", "resources"),
            archive = Path.Combine(resources, "777_res_pc.aya");
        Directory.CreateDirectory(Path.Combine(resources, "meshes"));
        WorldBody level = AnchorBody(), baseWorld = AnchorBody();
        PlacedObject sharedBase = baseWorld.Things[0], baseOnly = baseWorld.Things[1];
        sharedBase.Init.Position = new(30, 31, -6); sharedBase.Init.Orientation = new(0.2f, 0.1f, -0.3f);
        baseOnly.Init.Name = "BaseOnly"; baseOnly.Init.Position = new(33, 34, -7);
        File.WriteAllBytes(archive, Archive(level.Write(), baseWorld.Write()));
        CeMissionProject Bound(string sourceObject, params CeMissionObjectBinding[] others) => new("linked_preview", "Authored linked preview",
            [new("anchor", "Authored anchor", "authored.anchor", new(12, 13, -4))], [], map: new(777, [new("authored.anchor", sourceObject), .. others]));
        CeLinkedSceneSnapshot? Loaded(CeMissionProject project)
        {
            try { return CeLinkedSceneLoader.Load(game, project); }
            catch (InvalidDataException) { return null; }
        }

        CeLinkedSceneSnapshot? levelOnly = Loaded(Bound("OtherAnchor"));
        check.That(levelOnly is not null && levelOnly.Objects.Count == 4 && levelOnly.Instances(Bound("OtherAnchor"))
            .Single(item => item.Source.Id == "level:1").PlacementIndex == 0, "a selected-level object with a unique name is bound");

        check.That(Loaded(Bound("BaseOnly")) is null, "a base-world object is not a placement target, so CE's missing-object refusal is reported here too");
        if (levelOnly is not null) Refuses(check, () => levelOnly.Instances(Bound("BaseOnly")), "a loaded preview cannot be rebound to a base-world object");

        CeMissionProject shared = Bound("AuthoredAnchor");
        CeLinkedSceneSnapshot? both = Loaded(shared);
        check.That(both is not null, "a selected-level object may share its name with a base-world object");
        if (both is not null)
        {
            IReadOnlyList<CeLinkedSceneInstance> items = both.Instances(shared);
            CeLinkedSceneInstance own = items.Single(item => item.Source.Id == "level:0"), installed = items.Single(item => item.Source.Id == "base:0");
            check.That(own.PlacementIndex == 0 && own.Position == shared.Placements[0].Position, "the shared name binds the selected level's object");
            check.That(installed.PlacementIndex is null && installed.Position == sharedBase.Init.Position && installed.Source.Orientation == sharedBase.Init.Orientation,
                "the base-world object of that name keeps its installed position and orientation");
            check.That(items.Count(item => item.PlacementIndex is not null) == 1 && items.Where(item => item.PlacementIndex is null).All(item => item.Position == item.Source.Position),
                "every object except the one bound keeps its installed position");
        }

        CeMissionProject unplaced = Bound("OtherAnchor", new CeMissionObjectBinding("authored.unplaced", "NoSuchObject"));
        CeLinkedSceneSnapshot? loose = Loaded(unplaced);
        check.That(loose is not null && loose.Instances(unplaced).Count(item => item.PlacementIndex is not null) == 1,
            "a binding no placement uses is ignored, as CE ignores it");
        CeMissionProject placedAgain = new(unplaced.Id, unplaced.Name, unplaced.Placements.Append(new("second", "Second", "authored.unplaced", Position.One)), [], map: unplaced.Map);
        if (loose is not null) Refuses(check, () => loose.Instances(placedAgain), "a binding becomes checked as soon as a placement uses it");

        level.Things[1].Init.Name = "AuthoredAnchor";
        File.WriteAllBytes(archive, Archive(level.Write(), baseWorld.Write()));
        check.That(Loaded(shared) is null, "two selected-level objects of one name are refused, as CE refuses a second match");
    }

    private static void Coordinates(Checks check)
    {
        Position point = new(2.5f, -1.25f, 3.75f), translation = new(7, 11, -5), angles = new(0.37f, -0.22f, 0.41f);
        Position converted = GltfExport.Convert(point);
        Vector3 actual = LinkedSceneCoordinates.Transform(angles, translation) *
            (LinkedSceneCoordinates.GltfToViewport * new Vector3(converted.X, converted.Y, converted.Z));
        Position rolled = new(MathF.Cos(angles.Z) * point.X + MathF.Sin(angles.Z) * point.Z, point.Y,
            -MathF.Sin(angles.Z) * point.X + MathF.Cos(angles.Z) * point.Z);
        Position pitched = new(rolled.X, MathF.Cos(angles.Y) * rolled.Y - MathF.Sin(angles.Y) * rolled.Z,
            MathF.Sin(angles.Y) * rolled.Y + MathF.Cos(angles.Y) * rolled.Z);
        Position rotated = new(MathF.Cos(angles.X) * pitched.X - MathF.Sin(angles.X) * pitched.Y,
            MathF.Sin(angles.X) * pitched.X + MathF.Cos(angles.X) * pitched.Y, pitched.Z);
        check.That(actual.DistanceTo(LinkedSceneCoordinates.View(rotated + translation)) < 0.00001f,
            "nonidentity yaw/pitch/roll and translation compose above the glTF 180-degree basis correction");
        foreach (Position axis in new[] { Position.UnitX, Position.UnitY, Position.UnitZ })
        {
            Position gltf = GltfExport.Convert(axis);
            check.That((LinkedSceneCoordinates.GltfToViewport * new Vector3(gltf.X, gltf.Y, gltf.Z)).IsEqualApprox(LinkedSceneCoordinates.View(axis)),
                "every mesh axis agrees with the terrain coordinate basis");
        }
    }

    private static async Task Viewport(SceneTree tree, Checks check)
    {
        TerrainSurface surface = TerrainSurface.Flat(0, 0, 24, 24).WithVertexHeight(3, 3);
        CeMissionProjectEditor editor = new(Project(new(9, 11, -4)));
        CmshMesh mesh = ViewportMesh();
        CeLinkedSceneObject original = new("level:0", "AuthoredAnchor", "authored.anchor", "authored", new(5, 7, -3), new(0.37f, -0.22f, 0.41f), FromBaseWorld: false);
        CeLinkedSceneSnapshot? scene = new(777, surface, [original], [CeLinkedSceneModel.FromMesh("authored", mesh)]);
        IReadOnlyList<ObjectRow> Rows() => editor.Current.Placements.Select((item, index) => new ObjectRow(index, "unit", item.Name, item.Definition,
            item.Position, item.Position)).ToArray();
        IReadOnlyList<ObjectRow> rows = Rows(); int? selected = null; int requests = 0;
        LevelTerrainViewport view = new() { Size = new(640, 480), UseAuthoredSurface = true,
            PreviewSurfaceProvider = () => scene?.Terrain, LinkedSceneProvider = () => scene, LinkedProjectProvider = () => editor.Current,
            RowsProvider = () => rows, SelectedRowProvider = () => selected };
        view.RowPicked += row => selected = row;
        view.MoveRequested += (row, x, y) => { requests++; CeMissionPlacement item = editor.Current.Placements[row];
            editor.TryMovePlacement(item.Id, new(x, y, item.Position.Z), editor.Revision, out _); rows = Rows(); };
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        SubViewport sandbox = new() { Size = new(640, 480), GuiEmbedSubwindows = true };
        tree.Root.AddChild(sandbox); sandbox.AddChild(view);
        try
        {
            await Frame(tree);
            LinkedSceneModelLayer layer = view.FindChildren("*", nameof(Node3D), true, false).OfType<LinkedSceneModelLayer>().Single();
            Camera3D camera = view.FindChildren("*", nameof(Camera3D), true, false).OfType<Camera3D>().Single();
            Node3D actor = layer.GetChildren().OfType<Node3D>().Single();
            MeshInstance3D[] geometryNodes = actor.FindChildren("*", nameof(MeshInstance3D), true, false).OfType<MeshInstance3D>().ToArray();
            MeshInstance3D geometry = geometryNodes[0];
            check.That(view.LinkedModelCount == 1 && geometryNodes.Length == 2 && geometry.Mesh is { } actualMesh && actualMesh.GetSurfaceCount() > 0,
                "the linked viewport contains actual imported CMSH geometry, not just authoring markers");
            check.That(actor.Position.IsEqualApprox(LinkedSceneCoordinates.View(editor.Current.Placements[0].Position)) &&
                actor.Basis.IsEqualApprox(LinkedSceneCoordinates.Transform(original.Orientation, Position.Zero).Basis),
                "the displayed object uses project translation and its installed orientation");
            var arrays = geometry.Mesh.SurfaceGetArrays(0);
            Vector3 vertex = arrays[(int)Mesh.ArrayType.Vertex].AsVector3Array()[1];
            PartTransform partPose = mesh.ModelSpace(0, 0);
            Position modelVertex = partPose.Position + partPose.Orientation.Apply(mesh.Parts[0].Positions[1]);
            Vector3 expected = LinkedSceneCoordinates.Transform(original.Orientation, editor.Current.Placements[0].Position) * LinkedSceneCoordinates.View(modelVertex);
            check.That((geometry.GlobalTransform * vertex).DistanceTo(expected) < 0.0001f,
                "an actual imported vertex keeps its part hierarchy and agrees with terrain/world orientation");

            Aabb box = geometry.GlobalTransform * geometry.GetAabb();
            Vector2 modelAt = camera.UnprojectPosition(box.GetCenter());
            check.That(layer.RowAt(camera, modelAt) == 0 && view._GetTooltip(modelAt).Contains("Authored anchor", StringComparison.Ordinal),
                "the bound model's geometry bounds participate in row picking");
            Vector2 childAt = camera.UnprojectPosition((geometryNodes[1].GlobalTransform * geometryNodes[1].GetAabb()).GetCenter());
            check.That(layer.RowAt(camera, childAt) == 0, "reference-part child geometry is included in the model's picking bounds");
            Vector2 at = camera.UnprojectPosition(actor.Position), drop = camera.UnprojectPosition(new Vector3(16, 1, -16));
            Button(view, at, true); Motion(view, at, drop);
            check.That(actor.Position.DistanceTo(LinkedSceneCoordinates.View(editor.Current.Placements[0].Position)) > 1,
                "dragging previews the actual model at the terrain hit");
            view._GuiInput(new InputEventKey { Keycode = Key.Escape, Pressed = true });
            check.That(requests == 0 && actor.Position.IsEqualApprox(LinkedSceneCoordinates.View(editor.Current.Placements[0].Position)),
                "Escape restores the real model without committing a position edit");
            Button(view, at, true); Motion(view, at, drop); Button(view, drop, false); await Frame(tree);
            check.That(requests == 1 && editor.Current.Placements[0].Position.Z == -4 &&
                actor.Position.IsEqualApprox(LinkedSceneCoordinates.View(editor.Current.Placements[0].Position)) &&
                ReferenceEquals(layer.GetChildren().OfType<Node3D>().Single(), actor),
                "a committed drag updates the existing model, preserves authored Z and avoids rebuilding geometry");
            check.That(editor.Undo(), "linked position edits remain undoable"); rows = Rows(); await Frame(tree);
            check.That(actor.Position.IsEqualApprox(LinkedSceneCoordinates.View(editor.Current.Placements[0].Position)),
                "Undo also restores the displayed model position");
            CeMissionProject valid = editor.Current;
            editor.Open(new(valid.Id, valid.Name, valid.Placements.Append(valid.Placements[0] with { Id = "duplicate" }), [], map: valid.Map));
            rows = Rows(); await Frame(tree);
            check.That(view.LinkedModelCount == 1 && actor.Position.IsEqualApprox(LinkedSceneCoordinates.View(original.Position)) &&
                layer.RowAt(camera, camera.UnprojectPosition(actor.Position)) is null,
                "ambiguous authoring drafts retain terrain/original geometry and never clone or move it");
            editor.Open(valid); rows = Rows(); await Frame(tree);
            check.That(actor.Position.IsEqualApprox(LinkedSceneCoordinates.View(valid.Placements[0].Position)),
                "a corrected unique binding restores model placement without reloading the map");
            editor.TryMovePlacement("anchor", new(80, 80, -60), editor.Revision, out _); rows = Rows(); await Frame(tree);
            view.Refit(); await Frame(tree);
            bool framed = layer.WorldBounds is { } all && Enumerable.Range(0, 8).All(index =>
            {
                Vector3 corner = all.GetEndpoint(index); Vector2 screen = camera.UnprojectPosition(corner);
                return !camera.IsPositionBehind(corner) && screen.X >= 0 && screen.X <= view.Size.X && screen.Y >= 0 && screen.Y <= view.Size.Y &&
                    -(camera.GlobalTransform.AffineInverse() * corner).Z < camera.Far;
            });
            check.That(framed, "Frame all includes actual model bounds far beyond the terrain and retains adequate clip planes");
            scene = null; await Frame(tree);
            check.That(view.LinkedModelCount == 0 && !GodotObject.IsInstanceValid(actor),
                "closing the linked preview releases its instantiated model nodes");
        }
        finally { sandbox.QueueFree(); await Frame(tree); }
    }

    private static CmshMesh ViewportMesh()
    {
        CmshMesh mesh = CmshReader.Read(AssetTests.TwoPartMesh())[0];
        foreach (CmshPart part in mesh.Parts) { part.Positions = part.Positions.Select(v => v * 3).ToArray(); part.KeyPositions = part.KeyPositions.Select(v => v * 3).ToArray(); }
        mesh.Parts[1].ReferenceTo = 0;
        return mesh;
    }

    /// <summary>A base-world model of the bound name, in the real viewport: it stays visible at its installed transform and cannot be picked or dragged.</summary>
    private static async Task BaseWorldModel(SceneTree tree, Checks check)
    {
        TerrainSurface surface = TerrainSurface.Flat(0, 0, 24, 24);
        CeMissionProjectEditor editor = new(Project(new(6, 7, -3)));
        CeLinkedSceneObject installed = new("base:0", "AuthoredAnchor", "authored.base", "authored", new(18, 17, -3), new(0.37f, -0.22f, 0.41f), FromBaseWorld: true),
            own = new("level:0", "AuthoredAnchor", "authored.anchor", "authored", new(12, 12, -3), Position.Zero, FromBaseWorld: false);
        CeLinkedSceneSnapshot scene = new(777, surface, [installed, own], [CeLinkedSceneModel.FromMesh("authored", ViewportMesh())]);
        IReadOnlyList<ObjectRow> Rows() => editor.Current.Placements.Select((item, index) => new ObjectRow(index, "unit", item.Name, item.Definition,
            item.Position, item.Position)).ToArray();
        IReadOnlyList<ObjectRow> rows = Rows(); int? selected = null; int requests = 0;
        LevelTerrainViewport view = new() { Size = new(640, 480), UseAuthoredSurface = true,
            PreviewSurfaceProvider = () => scene.Terrain, LinkedSceneProvider = () => scene, LinkedProjectProvider = () => editor.Current,
            RowsProvider = () => rows, SelectedRowProvider = () => selected };
        view.RowPicked += row => selected = row;
        view.MoveRequested += (row, x, y) => { requests++; CeMissionPlacement item = editor.Current.Placements[row];
            editor.TryMovePlacement(item.Id, new(x, y, item.Position.Z), editor.Revision, out _); rows = Rows(); };
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        SubViewport sandbox = new() { Size = new(640, 480), GuiEmbedSubwindows = true };
        tree.Root.AddChild(sandbox); sandbox.AddChild(view);
        try
        {
            await Frame(tree);
            LinkedSceneModelLayer layer = view.FindChildren("*", nameof(Node3D), true, false).OfType<LinkedSceneModelLayer>().Single();
            Camera3D camera = view.FindChildren("*", nameof(Camera3D), true, false).OfType<Camera3D>().Single();
            Node3D[] actors = layer.GetChildren().OfType<Node3D>().ToArray();
            Transform3D home = LinkedSceneCoordinates.Transform(installed.Orientation, installed.Position);
            check.That(view.LinkedModelCount == 2 && actors.Length == 2 && actors[0].Transform.IsEqualApprox(home) &&
                actors[1].Position.IsEqualApprox(LinkedSceneCoordinates.View(editor.Current.Placements[0].Position)),
                "a base-world model stays at its installed transform while the selected level's object of that name takes the placement");
            if (actors.Length != 2) return;
            Vector2 baseAt = camera.UnprojectPosition(actors[0].Position), at = camera.UnprojectPosition(actors[1].Position);
            check.That(layer.RowAt(camera, baseAt) is null && layer.RowAt(camera, at) == 0, "only the bound selected-level model is picked as the placement");
            Button(view, baseAt, true); Motion(view, baseAt, camera.UnprojectPosition(new Vector3(2, 0, -2))); Button(view, baseAt, false); await Frame(tree);
            check.That(requests == 0 && actors[0].Transform.IsEqualApprox(home), "pressing on the base-world model starts no placement drag");
            // That press orbited the camera, so both points are projected again.
            at = camera.UnprojectPosition(actors[1].Position);
            Vector2 drop = camera.UnprojectPosition(new Vector3(16, 0, -4));
            Button(view, at, true); Motion(view, at, drop); Button(view, drop, false); await Frame(tree);
            check.That(requests == 1 && actors[1].Position.IsEqualApprox(LinkedSceneCoordinates.View(editor.Current.Placements[0].Position)) &&
                editor.Current.Placements[0].Position != new Position(6, 7, -3) && actors[0].Transform.IsEqualApprox(home),
                "dragging the bound model leaves the base-world model untouched");
        }
        finally { sandbox.QueueFree(); await Frame(tree); }
    }

    private static async Task Frame(SceneTree tree) { await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame); await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame); }
    private static void Button(LevelTerrainViewport view, Vector2 at, bool pressed) => view._GuiInput(new InputEventMouseButton { ButtonIndex = MouseButton.Left, Position = at, Pressed = pressed });
    private static void Motion(LevelTerrainViewport view, Vector2 from, Vector2 to) => view._GuiInput(new InputEventMouseMotion { Position = to, Relative = to - from, ButtonMask = MouseButtonMask.Left });
    private static string Hash(string path) => Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(path)));
    private static void Refuses(Checks check, Action action, string message)
    {
        bool refused = false; try { action(); } catch (InvalidDataException) { refused = true; }
        check.That(refused, message);
    }

    internal static byte[] Archive(byte[]? body, byte[]? baseBody = null, int? baseLevel = null)
    {
        byte[] world = [.. Chunk("WDAT", [.. BitConverter.GetBytes(baseLevel ?? (baseBody is null ? -1 : 123)), .. BitConverter.GetBytes(body is null ? -1 : 777)]),
            .. (baseBody is null ? [] : Chunk("BSWD", baseBody)), .. (body is null ? [] : Chunk("RLWD", body))];
        return AuthoredTerrainFixture.WithAuthoredTerrain(AssetTests.Member(Chunk("WRES", Chunk("WRLD", world))));
    }
    private static byte[] Chunk(string name, byte[] data) => [.. Encoding.ASCII.GetBytes(name), .. BitConverter.GetBytes(data.Length), .. data];
}
