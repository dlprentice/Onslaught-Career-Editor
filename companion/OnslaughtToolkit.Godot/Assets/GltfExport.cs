// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using System.Numerics;
using System.Text;
using System.Text.Json.Nodes;

namespace OnslaughtToolkit.Companion.Assets;

/// <summary>
/// Writes a mesh as one binary glTF 2.0 file (.glb), following reverse-engineering/asset-formats/cmsh-animation-keys.md:
/// one node per part, parented as the file says, each holding its key at virtual frame 0; one glTF mesh per part with
/// geometry, one primitive per vertex-buffer piece, its first texture layer as the base colour.
///
/// The game's model space is left-handed (Direct3D; its default culling keeps faces that wind clockwise on screen), with
/// -Z up. glTF is right-handed with +Y up, so every position and direction goes through one reflection,
/// (x, y, z) → (−x, −z, y), every orientation O becomes C·O·Cᵀ, and every triangle's winding is reversed. That is the
/// handedness change, not a mirror image of the model.
/// </summary>
public static class GltfExport
{
    /// <summary>Encodes a decoded texture as PNG bytes (the companion passes Godot's encoder).</summary>
    public delegate byte[] PngEncoder(DdsImage image);

    public static byte[] Write(CmshMesh mesh, Func<string, DdsImage?> loadTexture, PngEncoder png)
    {
        Builder b = new();
        JsonArray nodes = [], meshes = [], materials = [], images = [], textures = [];
        Dictionary<int, int> materialForTexture = [];
        Dictionary<int, int> meshForPart = [];

        int Material(int textureIndex)
        {
            if (materialForTexture.TryGetValue(textureIndex, out int found)) return found;
            JsonObject pbr = new() { ["metallicFactor"] = 0.0, ["roughnessFactor"] = 1.0 };
            JsonObject material = new() { ["pbrMetallicRoughness"] = pbr };
            string name = textureIndex >= 0 && textureIndex < mesh.Textures.Count ? mesh.Textures[textureIndex].Name : "untextured";
            material["name"] = name;
            DdsImage? image = textureIndex >= 0 && textureIndex < mesh.Textures.Count ? loadTexture(mesh.Textures[textureIndex].Name) : null;
            if (image is not null)
            {
                int view = b.View(png(image));
                images.Add(new JsonObject { ["bufferView"] = view, ["mimeType"] = "image/png", ["name"] = name });
                textures.Add(new JsonObject { ["source"] = images.Count - 1, ["sampler"] = 0 });
                pbr["baseColorTexture"] = new JsonObject { ["index"] = textures.Count - 1 };
                if (image.HasTransparency)
                {
                    bool binary = true;
                    for (int i = 3; i < image.Rgba.Length && binary; i += 4) binary = image.Rgba[i] is 0 or 255;
                    material["alphaMode"] = binary ? "MASK" : "BLEND";
                }
            }
            materials.Add(material);
            return materialForTexture[textureIndex] = materials.Count - 1;
        }

        int MeshOf(CmshPart part)
        {
            if (meshForPart.TryGetValue(part.Index, out int found)) return found;
            JsonArray primitives = [];
            int position = b.Floats(part.Positions.SelectMany(v => Flat(Convert(v))), 3, "VEC3", Bounds(part.Positions.Select(Convert)));
            int normal = b.Floats(part.Normals.SelectMany(n => Flat(UnitOrUp(Convert(n)))), 3, "VEC3");
            int uv = b.Floats(part.UVs.SelectMany(t => new[] { t.X, t.Y }), 2, "VEC2");
            JsonObject attributes = new() { ["POSITION"] = position, ["NORMAL"] = normal, ["TEXCOORD_0"] = uv };
            if (part.Colors.Any(c => c != 0xFFFFFFFF))
                attributes["COLOR_0"] = b.Bytes(part.Colors.SelectMany(c => new[] { (byte)(c >> 16), (byte)(c >> 8), (byte)c, (byte)(c >> 24) }), "VEC4");
            foreach ((CmshPiece piece, int[] triangles) in part.Triangles())
            {
                if (triangles.Length == 0) continue;
                int[] reversed = new int[triangles.Length];
                for (int t = 0; t < triangles.Length; t += 3) (reversed[t], reversed[t + 1], reversed[t + 2]) = (triangles[t], triangles[t + 2], triangles[t + 1]);
                primitives.Add(new JsonObject
                {
                    ["attributes"] = attributes.DeepClone(),
                    ["indices"] = b.Indices(reversed, part.Positions.Length),
                    ["material"] = Material(piece.TextureSlots.Length > 0 ? piece.TextureSlots[0] : -1),
                });
            }
            if (primitives.Count == 0) return meshForPart[part.Index] = -1;
            meshes.Add(new JsonObject { ["name"] = part.Name, ["primitives"] = primitives });
            return meshForPart[part.Index] = meshes.Count - 1;
        }

        IReadOnlyList<CmshPart> parts = mesh.Parts;
        int[] parent = ParentsWithoutLoops(parts);
        for (int i = 0; i < parts.Count; i++)
        {
            CmshPart part = parts[i];
            PartTransform rest = part.Key(0);
            JsonObject node = new() { ["name"] = part.Name.Length > 0 ? part.Name : $"Part {i}", ["matrix"] = Matrix(rest) };
            CmshPart? geometry = part.Positions.Length > 0 ? part
                : part.ReferenceTo is int r && r >= 0 && r < parts.Count && parts[r].Positions.Length > 0 ? parts[r] : null;
            if (geometry is not null && MeshOf(geometry) is int m and >= 0) node["mesh"] = m;
            nodes.Add(node);
        }
        for (int i = 0; i < parts.Count; i++)
        {
            int[] children = Enumerable.Range(0, parts.Count).Where(c => parent[c] == i).ToArray();
            if (children.Length > 0) ((JsonObject)nodes[i]!)["children"] = new JsonArray(children.Select(c => (JsonNode)c).ToArray());
        }
        JsonArray roots = new(Enumerable.Range(0, parts.Count).Where(i => parent[i] < 0).Select(i => (JsonNode)i).ToArray());

        JsonObject gltf = new()
        {
            ["asset"] = new JsonObject { ["version"] = "2.0", ["generator"] = "Onslaught Toolkit companion" },
            ["scene"] = 0,
            ["scenes"] = new JsonArray(new JsonObject { ["name"] = mesh.Name, ["nodes"] = roots }),
            ["nodes"] = nodes,
        };
        if (meshes.Count > 0) gltf["meshes"] = meshes;
        if (materials.Count > 0) gltf["materials"] = materials;
        if (images.Count > 0)
        {
            gltf["images"] = images;
            gltf["textures"] = textures;
            gltf["samplers"] = new JsonArray(new JsonObject { ["wrapS"] = 10497, ["wrapT"] = 10497 });
        }
        b.Finish(gltf);
        return Glb(gltf, b.Bin);
    }

    /// <summary>Game (x, y, z) to glTF (−x, −z, y).</summary>
    public static Vector3 Convert(Vector3 v) => new(-v.X, -v.Z, v.Y);

    /// <summary>C·O·Cᵀ for the reflection C in <see cref="Convert"/>: as a glTF column-major 4×4 with the position.</summary>
    public static JsonArray Matrix(PartTransform t)
    {
        // Columns of O' are C applied to the columns of O, re-ordered by Cᵀ: O'[:, j] = C·O·Cᵀ[:, j].
        Vector3 c0 = Convert(t.Orientation.Apply(Back(Vector3.UnitX)));
        Vector3 c1 = Convert(t.Orientation.Apply(Back(Vector3.UnitY)));
        Vector3 c2 = Convert(t.Orientation.Apply(Back(Vector3.UnitZ)));
        Vector3 p = Convert(t.Position);
        return new JsonArray(c0.X, c0.Y, c0.Z, 0f, c1.X, c1.Y, c1.Z, 0f, c2.X, c2.Y, c2.Z, 0f, p.X, p.Y, p.Z, 1f);
    }

    /// <summary>Cᵀ: glTF (X, Y, Z) back to game (−X, Z, −Y).</summary>
    private static Vector3 Back(Vector3 v) => new(-v.X, v.Z, -v.Y);

    private static int[] ParentsWithoutLoops(IReadOnlyList<CmshPart> parts)
    {
        int[] parent = parts.Select(p => p.Parent is int q && q >= 0 && q < parts.Count && q != p.Index ? q : -1).ToArray();
        for (int i = 0; i < parts.Count; i++)
        {
            HashSet<int> seen = [i];
            for (int q = parent[i]; q >= 0; q = parent[q])
                if (!seen.Add(q))
                {
                    parent[i] = -1;
                    break;
                }
        }
        return parent;
    }

    private static Vector3 UnitOrUp(Vector3 n) => n.LengthSquared() > 1e-12f && float.IsFinite(n.LengthSquared()) ? Vector3.Normalize(n) : Vector3.UnitY;
    private static float[] Flat(Vector3 v) => [v.X, v.Y, v.Z];

    private static (float[] Min, float[] Max) Bounds(IEnumerable<Vector3> points)
    {
        Vector3 min = new(float.MaxValue), max = new(float.MinValue);
        foreach (Vector3 p in points) (min, max) = (Vector3.Min(min, p), Vector3.Max(max, p));
        return (Flat(min), Flat(max));
    }

    private static byte[] Glb(JsonObject gltf, MemoryStream bin)
    {
        byte[] json = Encoding.UTF8.GetBytes(gltf.ToJsonString());
        int jsonPadded = (json.Length + 3) & ~3, binPadded = ((int)bin.Length + 3) & ~3;
        using MemoryStream glb = new();
        byte[] word = new byte[4];
        void U32(uint value)
        {
            BinaryPrimitives.WriteUInt32LittleEndian(word, value);
            glb.Write(word);
        }
        U32(0x46546C67);
        U32(2);
        U32((uint)(12 + 8 + jsonPadded + (bin.Length > 0 ? 8 + binPadded : 0)));
        U32((uint)jsonPadded);
        U32(0x4E4F534A);
        glb.Write(json);
        for (int i = json.Length; i < jsonPadded; i++) glb.WriteByte(0x20);
        if (bin.Length > 0)
        {
            U32((uint)binPadded);
            U32(0x004E4942);
            bin.Position = 0;
            bin.CopyTo(glb);
            for (long i = bin.Length; i < binPadded; i++) glb.WriteByte(0);
        }
        return glb.ToArray();
    }

    /// <summary>Accumulates the binary buffer, its views and accessors.</summary>
    private sealed class Builder
    {
        public MemoryStream Bin { get; } = new();
        private readonly JsonArray _views = [], _accessors = [];

        public int View(byte[] bytes, int? target = null)
        {
            while (Bin.Length % 4 != 0) Bin.WriteByte(0);
            JsonObject view = new() { ["buffer"] = 0, ["byteOffset"] = Bin.Length, ["byteLength"] = bytes.Length };
            if (target is int t) view["target"] = t;
            Bin.Write(bytes);
            _views.Add(view);
            return _views.Count - 1;
        }

        public int Floats(IEnumerable<float> values, int width, string type, (float[] Min, float[] Max)? bounds = null)
        {
            float[] data = values.ToArray();
            byte[] bytes = new byte[data.Length * 4];
            for (int i = 0; i < data.Length; i++) BinaryPrimitives.WriteSingleLittleEndian(bytes.AsSpan(4 * i), data[i]);
            JsonObject accessor = new()
            {
                ["bufferView"] = View(bytes, 34962), ["componentType"] = 5126, ["count"] = data.Length / width, ["type"] = type,
            };
            if (bounds is { } b)
            {
                accessor["min"] = new JsonArray(b.Min.Select(v => (JsonNode)v).ToArray());
                accessor["max"] = new JsonArray(b.Max.Select(v => (JsonNode)v).ToArray());
            }
            _accessors.Add(accessor);
            return _accessors.Count - 1;
        }

        public int Bytes(IEnumerable<byte> values, string type)
        {
            byte[] data = values.ToArray();
            _accessors.Add(new JsonObject
            {
                ["bufferView"] = View(data, 34962), ["componentType"] = 5121, ["normalized"] = true, ["count"] = data.Length / 4, ["type"] = type,
            });
            return _accessors.Count - 1;
        }

        public int Indices(int[] indices, int vertexCount)
        {
            bool small = vertexCount <= ushort.MaxValue;
            byte[] bytes = new byte[indices.Length * (small ? 2 : 4)];
            for (int i = 0; i < indices.Length; i++)
                if (small) BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(2 * i), (ushort)indices[i]);
                else BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(4 * i), (uint)indices[i]);
            _accessors.Add(new JsonObject
            {
                ["bufferView"] = View(bytes, 34963), ["componentType"] = small ? 5123 : 5125, ["count"] = indices.Length, ["type"] = "SCALAR",
            });
            return _accessors.Count - 1;
        }

        public void Finish(JsonObject gltf)
        {
            while (Bin.Length % 4 != 0) Bin.WriteByte(0);
            if (Bin.Length == 0) return;
            gltf["buffers"] = new JsonArray(new JsonObject { ["byteLength"] = Bin.Length });
            gltf["bufferViews"] = _views;
            gltf["accessors"] = _accessors;
        }
    }
}
