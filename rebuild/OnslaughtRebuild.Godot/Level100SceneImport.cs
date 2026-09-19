// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Explicit, offline import of the production presentation. Never runs as an
/// editor tool or starts a game. Converted resources stay in ignored Assets.
/// </summary>
public sealed partial class Level100SceneImport : Node
{
    internal const string DirectoryPath = "res://Assets/Level100/Scenes";
    private const string ReceiptPath = DirectoryPath + "/import.json";
    private readonly HashSet<ulong> _savedResources = [];
    private readonly List<string> _writtenFiles = [];
    private int _resourceNumber;

    private sealed record ImportedFile(string Name, string Sha256);
    private sealed record ImportReceipt(string CodeIdentity, string ActorManifest, ImportedFile[] Files);

    public override void _Ready()
    {
        if (Engine.IsEditorHint()) return;
        if (!OS.GetCmdlineUserArgs().Contains("--prepare-level100-scene", StringComparer.Ordinal))
        {
            GD.Print("Use npm run build:rebuild-godot to prepare the private Level 100 production scene.");
            GetTree().Quit();
            return;
        }
        try
        {
            if (!string.IsNullOrWhiteSpace(OS.GetEnvironment("ONSLAUGHT_TERRAIN_PROBE")))
                throw new InvalidOperationException("A diagnostic terrain probe cannot be baked into faithful production assets.");
            RequireLocalOutput(DirectoryPath);
            ImportReceipt? receipt = TryReadReceipt();
            if (receipt is not null)
            {
                VerifyFiles(receipt);
                if (receipt.CodeIdentity == CurrentCodeIdentity() &&
                    receipt.ActorManifest == Level100ActorDefinitionManifest.ExpectedManifestSha256)
                {
                    GD.Print("Level 100 production scenes are current.");
                    GetTree().Quit();
                    return;
                }
            }
            else if (System.IO.Directory.Exists(ProjectSettings.GlobalizePath(DirectoryPath)) &&
                System.IO.Directory.EnumerateFileSystemEntries(ProjectSettings.GlobalizePath(DirectoryPath)).Any())
            {
                throw new InvalidDataException("Scene output exists without an import receipt. Preserve it separately before importing.");
            }
            Import(receipt);
            VerifyCurrentImport();
            GD.Print("Level 100 production scenes imported and verified: " + FirstFlightWorldView.ProductionScenePath);
            GetTree().Quit();
        }
        catch (Exception error)
        {
            GD.PushError("Level 100 scene import failed: " + error);
            GetTree().Quit(1);
        }
    }

    public static void VerifyCurrentImport()
    {
        ImportReceipt receipt = TryReadReceipt() ?? throw new InvalidDataException(
            "Level 100 production scene is missing. Run npm run build:rebuild-godot.");
        if (receipt.CodeIdentity != CurrentCodeIdentity() ||
            receipt.ActorManifest != Level100ActorDefinitionManifest.ExpectedManifestSha256)
        {
            throw new InvalidDataException("Level 100 production scenes are stale. Run npm run build:rebuild-godot.");
        }
        VerifyFiles(receipt);
    }

    private static string CurrentCodeIdentity()
    {
        using IncrementalHash hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        foreach (Type type in new[] { typeof(FirstFlightWorldView), typeof(InteractiveSession), typeof(Simulation) })
        {
            // Godot loads the managed assembly from memory, so Location may be
            // empty. Deterministic .NET builds derive the module ID from content.
            hash.AppendData(type.Assembly.ManifestModule.ModuleVersionId.ToByteArray());
        }
        return Convert.ToHexString(hash.GetHashAndReset());
    }

    private static ImportReceipt? TryReadReceipt()
    {
        RequireLocalOutput(ReceiptPath);
        string path = ProjectSettings.GlobalizePath(ReceiptPath);
        return System.IO.File.Exists(path)
            ? JsonSerializer.Deserialize<ImportReceipt>(System.IO.File.ReadAllText(path))
                ?? throw new InvalidDataException("Invalid Level 100 import receipt.")
            : null;
    }

    private static void VerifyFiles(ImportReceipt receipt)
    {
        if (receipt.Files.Length == 0 || !receipt.Files.Any(file => file.Name == "Level100.tscn"))
            throw new InvalidDataException("Incomplete Level 100 import receipt.");
        foreach (ImportedFile file in receipt.Files)
        {
            if (Path.GetFileName(file.Name) != file.Name)
                throw new InvalidDataException("Invalid imported resource name.");
            string path = ProjectSettings.GlobalizePath(DirectoryPath + "/" + file.Name);
            RequireLocalOutput(DirectoryPath + "/" + file.Name);
            if (!System.IO.File.Exists(path) || Hash(path) != file.Sha256)
                throw new InvalidDataException(
                    $"Imported faithful resource changed: {file.Name}. Preserve deliberate edits separately; " +
                    "the faithful runtime does not silently adopt overrides.");
        }
    }

    private static void RequireLocalOutput(string resourcePath)
    {
        string project = Path.TrimEndingDirectorySeparator(ProjectSettings.GlobalizePath("res://"));
        string? path = Path.TrimEndingDirectorySeparator(ProjectSettings.GlobalizePath(resourcePath));
        while (path is not null && path != project)
        {
            if (new FileInfo(path).LinkTarget is not null)
                throw new InvalidDataException("Generated scene output must not follow a file or directory link: " + path);
            if (System.IO.File.Exists(path) || System.IO.Directory.Exists(path))
            {
                if ((System.IO.File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
                    throw new InvalidDataException("Generated scene output must not follow a file or directory link: " + path);
            }
            path = Path.GetDirectoryName(path);
        }
        if (path != project) throw new InvalidDataException("Scene output escaped the project.");
    }

    private void Import(ImportReceipt? previous)
    {
        System.IO.Directory.CreateDirectory(ProjectSettings.GlobalizePath(DirectoryPath));
        var session = new InteractiveSession(0x4F4E534Cu, Level100StaticWorldAsset.LoadActorDefinitions());
        var world = new FirstFlightWorldView();
        AddChild(world);
        world.BuildImportedScene(session.CurrentSnapshot);
        world.AddImportedActorResources();
        world.SetMeta("source", "Faithful imported Level 100; generated by the production import recipe");
        world.SetMeta("simulation_owner", "C# Core; scene transforms never become simulation inputs");
        world.SetMeta("actor_manifest_sha256", Level100ActorDefinitionManifest.ExpectedManifestSha256);
        world.GetNode<MeshInstance3D>("RetailLevel100HeightField").Mesh.ResourceLocalToScene = true;
        SaveNodeResources(world);

        // Gameplay loads these actual packed components through Level100.tscn.
        // The editor can open each independently without any runtime bootstrap.
        ReplaceWithComponent(world.GetNode<Node3D>("PlayerVisual/BodyPivot/RetailAquilaWalker"), "AquilaWalker.tscn");
        ReplaceWithComponent(world.GetNode<Node3D>("PlayerVisual/BodyPivot/RetailAquilaJet"), "AquilaJet.tscn");
        ReplaceWithComponent(world.GetNode<Node3D>("RetailOpeningAndFirstPersonCamera/RetailAquilaCockpit"), "AquilaCockpit.tscn");
        ReplaceWithComponent(world.GetNode<Node3D>("RetailLevel100StaticWorld"), "StaticWorld.tscn");
        OwnChildren(world, world);
        SaveScene(world, "Level100.tscn");
        var receipt = new ImportReceipt(CurrentCodeIdentity(),
            Level100ActorDefinitionManifest.ExpectedManifestSha256,
            _writtenFiles.Distinct().Order(StringComparer.Ordinal)
                .Select(name => new ImportedFile(name, Hash(ProjectSettings.GlobalizePath(DirectoryPath + "/" + name))))
                .ToArray());
        System.IO.File.WriteAllText(ProjectSettings.GlobalizePath(ReceiptPath),
            JsonSerializer.Serialize(receipt, new JsonSerializerOptions { WriteIndented = true }) + "\n");
        // Retire only this importer's obsolete, unchanged generated files. An
        // editor modification or an unrelated file is never a cleanup target.
        foreach (ImportedFile old in previous?.Files ?? [])
        {
            if (_writtenFiles.Contains(old.Name, StringComparer.Ordinal)) continue;
            string resourcePath = DirectoryPath + "/" + old.Name;
            RequireLocalOutput(resourcePath);
            string path = ProjectSettings.GlobalizePath(resourcePath);
            if (System.IO.File.Exists(path) && Hash(path) == old.Sha256)
                System.IO.File.Delete(path);
        }
        world.Free();
    }

    private void ReplaceWithComponent(Node3D node, string name)
    {
        Node parent = node.GetParent();
        int index = node.GetIndex();
        OwnChildren(node, node);
        SaveScene(node, name);
        Node3D instance = ResourceLoader.Load<PackedScene>(DirectoryPath + "/" + name,
            cacheMode: ResourceLoader.CacheMode.Ignore).Instantiate<Node3D>();
        parent.RemoveChild(node);
        parent.AddChild(instance);
        parent.MoveChild(instance, index);
        node.Free();
    }

    private static void OwnChildren(Node node, Node owner)
    {
        foreach (Node child in node.GetChildren())
        {
            child.Owner = owner;
            // Keep nested production instances, not flattened duplicate trees.
            if (string.IsNullOrEmpty(child.SceneFilePath)) OwnChildren(child, owner);
        }
    }

    private void SaveScene(Node root, string name)
    {
        RequireLocalOutput(DirectoryPath + "/" + name);
        using var scene = new PackedScene();
        RequireOk(scene.Pack(root), "pack " + name);
        RequireOk(ResourceSaver.Save(scene, DirectoryPath + "/" + name), "save " + name);
        _writtenFiles.Add(name);
    }

    private void SaveNodeResources(Node node)
    {
        foreach (Godot.Collections.Dictionary property in node.GetPropertyList())
        {
            if (((PropertyUsageFlags)property["usage"].AsInt64() & PropertyUsageFlags.Storage) != 0)
                SaveVariant(node.Get(property["name"].AsStringName()));
        }
        foreach (Node child in node.GetChildren()) SaveNodeResources(child);
    }

    private void SaveVariant(Variant value)
    {
        if (value.VariantType == Variant.Type.Object && value.AsGodotObject() is Resource resource)
        {
            // ImageTexture owns its Image payload. Externalizing that internal
            // property produces a broken external index in Godot 4.8 dev6's
            // binary saver (a minimal 4x4 texture reproduces it). Keep pixels
            // embedded in their private Texture2D resource instead.
            if (resource is Image) return;
            if (!_savedResources.Add(resource.GetInstanceId())) return;
            if (!string.IsNullOrEmpty(resource.ResourcePath) && !resource.ResourcePath.Contains("::", StringComparison.Ordinal))
                return;
            foreach (Godot.Collections.Dictionary property in resource.GetPropertyList())
                if (((PropertyUsageFlags)property["usage"].AsInt64() & PropertyUsageFlags.Storage) != 0)
                    SaveVariant(resource.Get(property["name"].AsStringName()));
            if (resource is Material) resource.ResourceLocalToScene = true;
            string name = $"{_resourceNumber++:D4}_{resource.GetClass()}.res";
            RequireLocalOutput(DirectoryPath + "/" + name);
            RequireOk(ResourceSaver.Save(resource, DirectoryPath + "/" + name,
                ResourceSaver.SaverFlags.Compress | ResourceSaver.SaverFlags.ChangePath), "save " + name);
            // Keep the live object external when its containing scene is packed.
            resource.TakeOverPath(DirectoryPath + "/" + name);
            _writtenFiles.Add(name);
        }
        else if (value.VariantType == Variant.Type.Array)
        {
            foreach (Variant item in value.AsGodotArray()) SaveVariant(item);
        }
        else if (value.VariantType == Variant.Type.Dictionary)
        {
            foreach (Variant item in value.AsGodotDictionary().Values) SaveVariant(item);
        }
    }

    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(System.IO.File.ReadAllBytes(path)));
    private static void RequireOk(Error result, string action)
    {
        if (result != Error.Ok) throw new IOException($"Could not {action}: {result}");
    }
}
