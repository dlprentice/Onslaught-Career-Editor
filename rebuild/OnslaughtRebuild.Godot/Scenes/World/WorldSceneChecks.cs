// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Round-trip the actual private production world, without a game host or input owner.</summary>
public sealed partial class WorldSceneChecks : Node
{
    private int _checks;
    private readonly HashSet<(ulong, ulong)> _comparedMaterials = [];
    private readonly HashSet<(ulong, ulong)> _comparedTextures = [];

    public override async void _Ready()
    {
        try
        {
            CheckImportOutputOwnership();
            var session = new InteractiveSession(0x4F4E534Cu, Level100StaticWorldAsset.LoadActorDefinitions());
            Input.MouseModeEnum pointer = Input.MouseMode;
            string initialHash = StateHasher.ComputeHex(session.CurrentSnapshot);
            var production = FirstFlightWorldView.InstantiateScene();
            Node[] authored = Descendants(production).ToArray();
            Check(authored.Length > 200, "World has an inspectable hierarchy before initialization.");
            Check(authored.OfType<MeshInstance3D>().Count(node => node.Mesh is not null) > 70,
                "Terrain, objects and Aquila already have production geometry.");
            foreach (Node3D actor in production.GetChildren().OfType<Node3D>()
                .Where(node => node.Name.ToString().StartsWith("RetailLevel100TargetActor", StringComparison.Ordinal)))
                Check(actor.GetNode<MeshInstance3D>("Geometry").Mesh is not null, "Packed actor overrides preserve geometry.");
            Check(production.GetNode<Camera3D>("RetailOpeningAndFirstPersonCamera").Far == 700f,
                "Camera projection is authored in the production scene.");
            Mesh terrain = production.GetNode<MeshInstance3D>("RetailLevel100HeightField").Mesh;
            int countBefore = authored.Length;
            AddChild(production);

            var recipe = new FirstFlightWorldView();
            AddChild(recipe);
            recipe.BuildImportedScene(session.CurrentSnapshot);
            // Check the frozen editor resources before binding refreshes the
            // terrain's runtime texture cache. A successful runtime refresh
            // alone would hide a broken saved texture from the editor check.
            Compare(recipe, production, compareGeometry: true, compareBindings: false);
            _comparedMaterials.Clear();
            _comparedTextures.Clear();
            production.Initialize(session.CurrentSnapshot);
            Check(Descendants(production).Count() == countBefore, "Binding does not build a second world.");
            Check(production.GetNode<MeshInstance3D>("RetailLevel100HeightField").Mesh == terrain,
                "Runtime LOD updates the same authored terrain resource.");
            Check(StateHasher.ComputeHex(session.CurrentSnapshot) == initialHash,
                "Scene binding cannot change deterministic state.");

            Compare(recipe, production, compareGeometry: true);
            foreach (int tick in new[] { 180, 1_000, 1_100 })
            {
                while (session.CurrentSnapshot.Tick < tick)
                {
                    session.ObserveInput(FirstFlightSmokeScenario.GetInputForTick(session.CurrentSnapshot.Tick));
                    session.AdvanceFrameTicks(500_000);
                }
                string before = StateHasher.ComputeHex(session.CurrentSnapshot);
                recipe.Render(session.PreviousSnapshot, session.CurrentSnapshot, 0.5f, 0.05f);
                production.Render(session.PreviousSnapshot, session.CurrentSnapshot, 0.5f, 0.05f);
                Compare(recipe, production, compareGeometry: false);
                Check(StateHasher.ComputeHex(session.CurrentSnapshot) == before, "Rendering leaves the snapshot hash unchanged.");
            }
            var retry = FirstFlightWorldView.InstantiateScene();
            var liveMaterial = production.GetNode<MeshInstance3D>("RetailLevel100HeightField").MaterialOverride;
            var retryMaterial = retry.GetNode<MeshInstance3D>("RetailLevel100HeightField").MaterialOverride;
            Check(liveMaterial != retryMaterial, "Retry owns independent animated materials.");
            Check(retry.GetNode<MeshInstance3D>("RetailLevel100HeightField").Mesh != terrain,
                "Retry owns independent terrain LOD geometry.");
            retry.Free();
            Check(Input.MouseMode == pointer, "Import/binding/render checks never acquire the pointer.");
            Level100SceneImport.VerifyCurrentImport();
            GD.Print($"WORLD_SCENE_CHECKS: {_checks} passed; authored content, geometry round-trip, bindings, selected snapshot poses, retry isolation and unchanged simulation hashes.");
            recipe.QueueFree();
            production.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GetTree().Quit();
        }
        catch (Exception error)
        {
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private void CheckImportOutputOwnership()
    {
        string resourceDirectory = Level100SceneImport.DirectoryPath + "/ownership-check-" + Guid.NewGuid().ToString("N");
        string directory = ProjectSettings.GlobalizePath(resourceDirectory);
        System.IO.Directory.CreateDirectory(directory);
        try
        {
            string[] files = ["0000_Mesh.res", "0211_ShaderMaterial.res", "AquilaWalker.tscn", "changed.res", "notes.txt"];
            foreach (string name in files) System.IO.File.WriteAllText(Path.Combine(directory, name), "Keep " + name);
            System.IO.Directory.CreateDirectory(Path.Combine(directory, "StaticWorld.tscn"));
            string Hash(string name) => Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(
                System.IO.File.ReadAllBytes(Path.Combine(directory, name))));
            var before = files.ToDictionary(name => name, Hash, StringComparer.Ordinal);
            var owned = new Dictionary<string, string>(StringComparer.Ordinal)
            {
                ["0000_Mesh.res"] = before["0000_Mesh.res"],
                ["changed.res"] = "stale hash"
            };
            foreach (string collision in new[] { "0211_ShaderMaterial.res", "AquilaWalker.tscn", "changed.res", "StaticWorld.tscn" })
            {
                bool rejected = false;
                try
                {
                    Level100SceneImport.VerifyOutputOwnership(resourceDirectory, owned,
                        ["0000_Mesh.res", "new.res", collision]);
                }
                catch (InvalidDataException) { rejected = true; }
                Check(rejected, "Import refuses an unowned, edited or directory destination: " + collision);
                Check(files.All(name => Hash(name) == before[name]), "Preflight refusal leaves every output unchanged.");
                Check(!System.IO.File.Exists(Path.Combine(directory, "new.res")), "Preflight does not publish partial output.");
            }
            Level100SceneImport.VerifyOutputOwnership(resourceDirectory, owned, ["0000_Mesh.res", "new.res"]);
            Check(files.All(name => Hash(name) == before[name]), "Unrelated noncolliding private files are preserved.");
        }
        finally
        {
            // Only this check's uniquely named fixture directory is disposable.
            System.IO.Directory.Delete(directory, recursive: true);
        }
    }

    private void Compare(FirstFlightWorldView recipe, FirstFlightWorldView production,
        bool compareGeometry, bool compareBindings = true)
    {
        foreach (Node expected in Descendants(recipe))
        {
            NodePath path = recipe.GetPathTo(expected);
            Node? actual = production.GetNodeOrNull(path);
            Check(actual is not null, "Saved scene contains production node " + path);
            if (expected is Node3D left && actual is Node3D right)
            {
                Check(left.Transform.IsEqualApprox(right.Transform), "Retained presentation transform at " + path);
                Check(left.Visible == right.Visible, "Retained visibility at " + path);
            }
            if (compareGeometry && expected is MeshInstance3D mesh && actual is MeshInstance3D other)
            {
                Check(mesh.Mesh is not null && other.Mesh is not null, "Mesh retained at " + path);
                Check(mesh.Mesh!.GetSurfaceCount() == other.Mesh!.GetSurfaceCount(), "Surface count at " + path);
                CompareMaterial(mesh.MaterialOverride, other.MaterialOverride, path);
                for (int surface = 0; surface < mesh.Mesh.GetSurfaceCount(); surface++)
                {
                    CompareMaterial(mesh.Mesh.SurfaceGetMaterial(surface), other.Mesh.SurfaceGetMaterial(surface), path);
                    var source = mesh.Mesh.SurfaceGetArrays(surface);
                    var loaded = other.Mesh.SurfaceGetArrays(surface);
                    Check(source[(int)Mesh.ArrayType.Vertex].AsVector3Array()
                        .SequenceEqual(loaded[(int)Mesh.ArrayType.Vertex].AsVector3Array()),
                        "Lossless vertex round-trip at " + path);
                    Check(source[(int)Mesh.ArrayType.Index].AsInt32Array()
                        .SequenceEqual(loaded[(int)Mesh.ArrayType.Index].AsInt32Array()),
                        "Lossless index round-trip at " + path);
                }
            }
            if (expected is MultiMeshInstance3D forest && actual is MultiMeshInstance3D otherForest)
            {
                Check(forest.Multimesh.InstanceCount == otherForest.Multimesh.InstanceCount, "Pine instance count at " + path);
                if (compareGeometry)
                {
                    Check(forest.Multimesh.Mesh.GetSurfaceCount() == otherForest.Multimesh.Mesh.GetSurfaceCount(),
                        "Pine surface count at " + path);
                    CompareMaterial(forest.MaterialOverride, otherForest.MaterialOverride, path);
                    for (int surface = 0; surface < forest.Multimesh.Mesh.GetSurfaceCount(); surface++)
                        CompareMaterial(forest.Multimesh.Mesh.SurfaceGetMaterial(surface),
                            otherForest.Multimesh.Mesh.SurfaceGetMaterial(surface), path);
                }
                for (int i = 0; i < forest.Multimesh.InstanceCount; i++)
                    Check(forest.Multimesh.GetInstanceTransform(i).IsEqualApprox(otherForest.Multimesh.GetInstanceTransform(i)),
                        "Pine placement at " + path);
            }
        }
        if (!compareBindings) return;
        Check(recipe.RetailLevel100StaticObjectSurfaceCount == production.RetailLevel100StaticObjectSurfaceCount,
            "Static hierarchy surface totals agree.");
        Check(recipe.RetailLevel100TargetSurfaceCount == production.RetailLevel100TargetSurfaceCount,
            "Actor surface totals agree.");
        Check(recipe.ShowHud == production.ShowHud && recipe.OpeningPanActive == production.OpeningPanActive,
            "Camera state and HUD gate agree.");
    }

    private void CompareMaterial(Material? expected, Material? actual, NodePath path)
    {
        Check((expected is null) == (actual is null), "Material retained at " + path);
        if (expected is null || actual is null ||
            !_comparedMaterials.Add((expected.GetInstanceId(), actual.GetInstanceId()))) return;
        foreach (Godot.Collections.Dictionary property in expected.GetPropertyList())
        {
            if (((PropertyUsageFlags)property["usage"].AsInt64() & PropertyUsageFlags.Storage) == 0) continue;
            StringName name = property["name"].AsStringName();
            Variant value = expected.Get(name);
            if (value.VariantType != Variant.Type.Object || value.AsGodotObject() is not Texture2D texture) continue;
            Texture2D? loaded = actual.Get(name).AsGodotObject() as Texture2D;
            Check(loaded is not null, "Material texture retained at " + path + ":" + name);
            if (!_comparedTextures.Add((texture.GetInstanceId(), loaded!.GetInstanceId()))) continue;
            using Image? original = texture.GetImage();
            using Image? copy = loaded.GetImage();
            Check(original is not null && copy is not null, "Private texture pixels survived serialization.");
            Check(original!.GetSize() == copy!.GetSize() && original.GetFormat() == copy.GetFormat(),
                "Private texture dimensions/format retained.");
            Check(original.GetData().SequenceEqual(copy.GetData()), "Lossless private texture round-trip.");
        }
    }

    private static IEnumerable<Node> Descendants(Node root)
    {
        foreach (Node child in root.GetChildren())
        {
            yield return child;
            foreach (Node descendant in Descendants(child)) yield return descendant;
        }
    }

    private void Check(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
        _checks++;
    }
}
