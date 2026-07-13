// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Loads local-only preview meshes for First Flight. Supports GLB/GLTF via
/// Godot's GLTFDocument and a minimal triangle OBJ path for AppCore rebuild-mesh
/// outputs. Never mutates Core state.
/// </summary>
internal static class LocalAssetMeshLoader
{
    public static Node3D? TryLoadMeshNode(string absolutePath, LocalMeshRef settings, string nodeName)
    {
        if (string.IsNullOrWhiteSpace(absolutePath) || !File.Exists(absolutePath))
        {
            return null;
        }

        string extension = Path.GetExtension(absolutePath).ToLowerInvariant();
        Node3D? loaded = extension switch
        {
            ".glb" or ".gltf" => TryLoadGltf(absolutePath),
            ".obj" => TryLoadObj(absolutePath),
            _ => null,
        };

        if (loaded is null)
        {
            return null;
        }

        var wrapper = new Node3D { Name = nodeName };
        float scale = settings.Scale <= 0f ? 1f : settings.Scale;
        wrapper.Scale = new Vector3(scale, scale, scale);
        wrapper.RotationDegrees = new Vector3(0f, settings.YawDegrees, 0f);
        wrapper.Position = new Vector3(0f, settings.YOffsetMeters, 0f);
        wrapper.AddChild(loaded);
        return wrapper;
    }

    private static Node3D? TryLoadGltf(string absolutePath)
    {
        var document = new GltfDocument();
        var state = new GltfState();
        Error error = document.AppendFromFile(absolutePath, state);
        if (error != Error.Ok)
        {
            GD.PushWarning($"First Flight local GLTF load failed ({error}): {absolutePath}");
            return null;
        }

        Node? generated = document.GenerateScene(state);
        return generated as Node3D ?? WrapOrNull(generated);
    }

    private static Node3D? WrapOrNull(Node? node)
    {
        if (node is null)
        {
            return null;
        }

        if (node is Node3D node3D)
        {
            return node3D;
        }

        var wrapper = new Node3D { Name = "ImportedRoot" };
        wrapper.AddChild(node);
        return wrapper;
    }

    private static Node3D? TryLoadObj(string absolutePath)
    {
        var positions = new List<Vector3>();
        var normals = new List<Vector3>();
        var uvs = new List<Vector2>();
        var surfaceTool = new SurfaceTool();
        surfaceTool.Begin(Mesh.PrimitiveType.Triangles);

        bool hasFaces = false;
        foreach (string rawLine in File.ReadLines(absolutePath))
        {
            string line = rawLine.Trim();
            if (line.Length == 0 || line.StartsWith('#') || line.StartsWith("mtllib", StringComparison.OrdinalIgnoreCase) ||
                line.StartsWith("usemtl", StringComparison.OrdinalIgnoreCase) ||
                line.StartsWith("o ", StringComparison.OrdinalIgnoreCase) ||
                line.StartsWith("g ", StringComparison.OrdinalIgnoreCase) ||
                line.StartsWith("s ", StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            string[] parts = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length == 0)
            {
                continue;
            }

            switch (parts[0])
            {
                case "v" when parts.Length >= 4:
                    positions.Add(new Vector3(Parse(parts[1]), Parse(parts[2]), Parse(parts[3])));
                    break;
                case "vn" when parts.Length >= 4:
                    normals.Add(new Vector3(Parse(parts[1]), Parse(parts[2]), Parse(parts[3])));
                    break;
                case "vt" when parts.Length >= 3:
                    uvs.Add(new Vector2(Parse(parts[1]), 1f - Parse(parts[2])));
                    break;
                case "f" when parts.Length >= 4:
                    hasFaces = true;
                    EmitFan(surfaceTool, parts, positions, normals, uvs);
                    break;
            }
        }

        if (!hasFaces || positions.Count == 0)
        {
            GD.PushWarning($"First Flight local OBJ had no usable geometry: {absolutePath}");
            return null;
        }

        surfaceTool.GenerateNormals();
        ArrayMesh mesh = surfaceTool.Commit();
        return new MeshInstance3D
        {
            Name = "ObjMesh",
            Mesh = mesh,
            MaterialOverride = VisualPrimitives.CreateMaterial(
                new Color(0.55f, 0.58f, 0.60f),
                0.35f,
                0.55f),
        };
    }

    private static void EmitFan(
        SurfaceTool surfaceTool,
        string[] parts,
        List<Vector3> positions,
        List<Vector3> normals,
        List<Vector2> uvs)
    {
        // Triangulate fan: 0,i,i+1
        ObjVertex first = ParseVertex(parts[1], positions, normals, uvs);
        for (int i = 2; i < parts.Length - 1; i++)
        {
            ObjVertex second = ParseVertex(parts[i], positions, normals, uvs);
            ObjVertex third = ParseVertex(parts[i + 1], positions, normals, uvs);
            AddVertex(surfaceTool, first);
            AddVertex(surfaceTool, second);
            AddVertex(surfaceTool, third);
        }
    }

    private static void AddVertex(SurfaceTool surfaceTool, ObjVertex vertex)
    {
        if (vertex.Normal.HasValue)
        {
            surfaceTool.SetNormal(vertex.Normal.Value);
        }

        if (vertex.Uv.HasValue)
        {
            surfaceTool.SetUV(vertex.Uv.Value);
        }

        surfaceTool.AddVertex(vertex.Position);
    }

    private static ObjVertex ParseVertex(
        string token,
        List<Vector3> positions,
        List<Vector3> normals,
        List<Vector2> uvs)
    {
        string[] bits = token.Split('/');
        int positionIndex = ParseIndex(bits[0], positions.Count);
        Vector3? normal = null;
        Vector2? uv = null;
        if (bits.Length >= 2 && bits[1].Length > 0)
        {
            uv = uvs[ParseIndex(bits[1], uvs.Count)];
        }

        if (bits.Length >= 3 && bits[2].Length > 0)
        {
            normal = normals[ParseIndex(bits[2], normals.Count)];
        }

        return new ObjVertex(positions[positionIndex], normal, uv);
    }

    private static int ParseIndex(string text, int count)
    {
        int index = int.Parse(text, CultureInfo.InvariantCulture);
        if (index < 0)
        {
            index = count + index;
        }
        else
        {
            index -= 1;
        }

        if (index < 0 || index >= count)
        {
            throw new InvalidDataException($"OBJ index {text} out of range for count {count}.");
        }

        return index;
    }

    private static float Parse(string text) =>
        float.Parse(text, CultureInfo.InvariantCulture);

    private readonly record struct ObjVertex(Vector3 Position, Vector3? Normal, Vector2? Uv);
}
