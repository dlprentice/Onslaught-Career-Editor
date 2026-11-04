// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Authored definition/resource joins through the same loader the mission page uses.</summary>
internal static class InstalledModelReferenceTests
{
    internal static void Run(string root, Checks check)
    {
        string game = Path.Combine(root, "definition-models"), data = Path.Combine(game, "data"), resources = Path.Combine(data, "resources"),
            shelves = Path.Combine(resources, "meshes"), archive = Path.Combine(resources, "777_res_pc.aya"), physics = Path.Combine(data, "default physics.dat");
        Directory.CreateDirectory(shelves);
        byte[] mesh = AssetTests.TwoPartMesh(), packed = AssetTests.Member(mesh);
        File.WriteAllBytes(Path.Combine(shelves, "m_authored-unit.msh.aya"), packed);
        File.WriteAllBytes(Path.Combine(shelves, "m_authored-feature.msh.aya"), packed);
        WorldBody body = CeLinkedSceneTests.AnchorBody();
        body.NamedMeshes.Clear();
        body.Things[0].ObjectId = 8; body.Things[0].Definition = "SharedDefinition"; body.Things[0].Init.MeshNumber = -1;
        body.Things[1].ObjectId = 35; body.Things[1].Definition = "SharedDefinition"; body.Things[1].Init.MeshNumber = -1;
        byte[] definitionBytes = Physics(Definition(1, "SharedDefinition", "authored-unit.msh"), Definition(8, "SharedDefinition", "authored-feature.msh"));
        File.WriteAllBytes(physics, definitionBytes);
        void Archive(params byte[][] references) => File.WriteAllBytes(archive,
            [.. CeLinkedSceneTests.Archive(body.Write()), .. AssetTests.Member([.. references.SelectMany(x => x)])]);
        void Both() => Archive(Reference("authored-unit.msh"), Reference("authored-feature.msh"));
        CeMissionProject project = CeLinkedSceneTests.Project(new(12, 13, -4));
        CeLinkedSceneSnapshot Load() => CeLinkedSceneLoader.Load(game, project);
        Both();
        string before = Hash(archive) + Hash(physics);
        CeLinkedSceneSnapshot scene = Load();
        check.That(scene.Models.Count == 2 && scene.Objects[0].ModelKey == "authored-unit" && scene.Objects[1].ModelKey == "authored-feature" && scene.Notes.Count == 0,
            "installed definitions resolve actual unit and feature models even when the world's named-mesh list is empty");
        check.That(scene.Instances(project)[0].Position == project.Placements[0].Position && scene.Instances(project)[1].Position == body.Things[1].Init.Position,
            "definition geometry retains the named placement target and does not move unrelated objects");
        CeLinkedModelSource? source = scene.Models.Single(m => m.Key == "authored-unit").Source;
        check.That(source is { AssetId: "mesh:data/resources/meshes/m_authored-unit.msh.aya" } &&
            source.ContainerSha256 == Digest(packed) && source.ContentSha256 == Digest(mesh) && before == Hash(archive) + Hash(physics),
            "model source identity binds the actual packed and decoded inputs without modifying them");
        byte[] projectBytes = CeMissionProjectJson.Write(project);
        CeMissionProject reopened = CeMissionProjectJson.Read(projectBytes);
        check.That(Load().Instances(reopened)[0].Source.SourceObject == "AuthoredAnchor" &&
            CeMissionProjectJson.Write(reopened).SequenceEqual(projectBytes) && !Encoding.UTF8.GetString(projectBytes).Contains(source!.ContainerSha256, StringComparison.Ordinal),
            "Save/Open preserves project and source-object identity without embedding model data or preview fingerprints");

        foreach (int kind in new[] { 25, 28 })
        {
            body.Things[0].ObjectId = kind;
            body.Things[0].Init.Squad = kind == 28 ? new SquadInit() : null;
            Both();
            check.That(Load().Objects[0].ModelKey == "authored-unit", "building and squad records use the unit-definition mesh lookup");
        }
        body.Things[0].ObjectId = 8;
        body.Things[0].Init.Squad = null;
        body.Things[0].Definition = "shareddefinition";
        Both();
        check.That(Load().Objects[0].ModelKey is null, "definition names retain the game's case-sensitive identity");
        body.Things[0].Definition = "SharedDefinition";
        Archive(Reference("AUTHORED-UNIT.MSH"), Reference("authored-feature.msh", legacy: true));
        check.That(Load().Models.Count == 2, "mesh names use case-insensitive shelf matching and support the legacy PMSH reference envelope");

        Archive(Reference("authored-feature.msh"));
        check.That(Load().Objects[0].ModelKey is null && Load().Notes.Any(n => n.Contains("no unique definition-to-model", StringComparison.Ordinal)),
            "a loose model file alone is not evidence that the selected archive loads it");
        Archive(Reference("authored-unit.msh"), Reference("AUTHORED-UNIT.MSH"), Reference("authored-feature.msh"));
        check.That(Load().Objects[0].ModelKey is null, "duplicate archive references are ambiguous rather than silently choosing the first model");
        Both();
        File.WriteAllBytes(physics, Physics(Definition(1, "SharedDefinition", "authored-unit.msh"), Definition(1, "SharedDefinition", "authored-unit.msh"),
            Definition(8, "SharedDefinition", "authored-feature.msh")));
        check.That(Load().Objects[0].ModelKey is null && Load().Objects[1].ModelKey is not null,
            "duplicate definitions cannot silently choose a model and do not confuse a feature of the same name");
        File.WriteAllBytes(physics, definitionBytes);

        // The 'm_' shelf prefix is not part of the requested model name. A requested name may itself begin with m_.
        File.WriteAllBytes(Path.Combine(shelves, "m_m_prefixed.msh.aya"), packed);
        File.WriteAllBytes(physics, Physics(Definition(1, "SharedDefinition", "m_prefixed.msh"), Definition(8, "SharedDefinition", "authored-feature.msh")));
        Archive(Reference("m_prefixed.msh"), Reference("authored-feature.msh"));
        check.That(Load().Objects[0].ModelKey == "m_prefixed" && Load().Models.Any(m => m.Source!.AssetId.EndsWith("/m_m_prefixed.msh.aya", StringComparison.Ordinal)),
            "a genuine m_ in a requested name is preserved separately from the shelf filename prefix");

        byte[] refs = Reference("authored-unit.msh");
        byte[] unknown = Definition(99, "SharedDefinition", "authored-unit.msh");
        int unknownFieldAt = 8 + Encoding.ASCII.GetByteCount("SharedDefinition") + 1;
        BinaryPrimitives.WriteInt32LittleEndian(unknown.AsSpan(unknownFieldAt), -1);
        check.That(new InstalledModelReferences(Physics(unknown), refs).Resolve(8, "SharedDefinition") is null,
            "an unknown record kind cannot become a unit through an unrecognized field number");
        Refuses(check, () => new InstalledModelReferences(definitionBytes[..^1], refs), "truncated definition terminal is refused");
        Refuses(check, () => new InstalledModelReferences([.. definitionBytes, 0], refs), "definition trailing data is refused");
        byte[] version = [.. definitionBytes]; version[0]++;
        Refuses(check, () => new InstalledModelReferences(version, refs), "unsupported definition format is refused");
        Refuses(check, () => new InstalledModelReferences(Physics(Definition(1, "SharedDefinition", "authored-unit.msh", duplicateMesh: true)), refs),
            "repeated mesh fields are refused instead of choosing a later value");
        Refuses(check, () => new InstalledModelReferences(definitionBytes, refs[..^1]), "truncated archive references are refused");
        byte[] invalidName = Reference("authored-unit.msh"); invalidName[24] = 1;
        Refuses(check, () => new InstalledModelReferences(definitionBytes, invalidName), "control characters in resource names are refused");
        byte[] invalidFrame = [.. refs]; BinaryPrimitives.WriteInt32LittleEndian(invalidFrame.AsSpan(12), 0);
        Refuses(check, () => new InstalledModelReferences(definitionBytes, invalidFrame), "a nested reference must cover its payload exactly");
        InstalledModelReferences embedded = new(definitionBytes, Reference(""));
        check.That(embedded.Resolve(8, "SharedDefinition") is null, "unnamed inline resources do not become invented loose filenames");
    }

    internal static byte[] Physics(params byte[][] records) => [18, 0, .. records.SelectMany(r => r), .. BitConverter.GetBytes(-1)];
    internal static byte[] Definition(int type, string name, string mesh, bool duplicateMesh = false)
    {
        byte[] value = Encoding.ASCII.GetBytes(mesh + "\0");
        int field = type == 1 ? 9 : 2;
        byte[] meshField = [.. BitConverter.GetBytes(field), .. BitConverter.GetBytes(value.Length), .. value];
        return [.. BitConverter.GetBytes(type), .. BitConverter.GetBytes(0), .. Encoding.ASCII.GetBytes(name + "\0"),
            .. (type == 1 ? (byte[])[.. BitConverter.GetBytes(8), .. BitConverter.GetBytes(4), .. BitConverter.GetBytes(1), .. BitConverter.GetBytes(0)] : []),
            .. meshField, .. BitConverter.GetBytes(duplicateMesh ? 0 : -1), .. (duplicateMesh ? (byte[])[.. meshField, .. BitConverter.GetBytes(-1)] : [])];
    }
    internal static byte[] Reference(string name, bool legacy = false)
    {
        byte[] header = new byte[309];
        Encoding.ASCII.GetBytes(name).CopyTo(header, 0);
        return Chunk("MESH", Chunk("PMSH", legacy ? header : Chunk("PMS2", header)));
    }
    private static byte[] Chunk(string tag, byte[] body) => [.. Encoding.ASCII.GetBytes(tag), .. BitConverter.GetBytes(body.Length), .. body];
    private static string Digest(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    private static string Hash(string path) => Digest(File.ReadAllBytes(path));
    private static void Refuses(Checks check, Action operation, string label)
    {
        bool refused = false;
        try { operation(); } catch (InvalidDataException) { refused = true; }
        check.That(refused, label);
    }
}
