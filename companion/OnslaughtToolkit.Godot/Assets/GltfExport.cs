// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using System.Numerics;
using System.Text;
using System.Text.Json.Nodes;

namespace OnslaughtToolkit.Companion.Assets;

/// <summary>
/// Writes a mesh as one binary glTF 2.0 file (.glb), following reverse-engineering/asset-formats/cmsh-animation-keys.md:
/// one node per part, parented as the file says, each holding its key at virtual frame 0 as translation, rotation and
/// (for the game's reflected keys) a negative scale; one glTF mesh per part with geometry, one primitive per
/// vertex-buffer piece, its first texture layer as the base colour; one skin per skeletal part; one animation per mode.
///
/// Skeletal parts: the game skins a vertex as bone_now · bone_at_frame_0⁻¹ applied to the vertex placed by the
/// skeletal part's own transform (cmsh-matrix-normal-deformation.md), with weights 0, 2/3 and 1/3 for its three
/// palette slots (cmsh-matrix-palette-skinning.md). Every installed skeletal part and its ancestors hold one key, so
/// the vertices are written already placed by that transform, each joint's inverse bind matrix is the inverse of
/// the bone at frame 0, and glTF's skinning then reproduces the game's positions. The game does not deform normals;
/// glTF viewers do, so lighting on a moving limb can differ slightly.
///
/// Animations: each mode is sampled at every virtual frame from start to start + frame_scaler, at
/// (frame − start) / frame_scaler × duration, duration = 1 / (20 · rate) (one virtual frame per tick when the stored
/// rate is 0). The game interpolates its matrices element by element; glTF interpolates quaternions, so poses agree
/// exactly at every sample and differ slightly between them.
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
        JsonArray nodes = [], meshes = [], materials = [], images = [], textures = [], skins = [];
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
            bool skinned = Skinned(part, mesh.Parts.Count);
            PartTransform place = skinned ? mesh.ModelSpace(part.Index, 0) : new(MeshBasis.Identity, Vector3.Zero);
            Vector3[] positions = part.Positions.Select(v => Convert(place.Position + place.Orientation.Apply(v))).ToArray();
            int position = b.Floats(positions.SelectMany(Flat), 3, "VEC3", Bounds(positions));
            int normal = b.Floats(part.Normals.SelectMany(n => Flat(UnitOrUp(Convert(place.Orientation.Apply(n))))), 3, "VEC3");
            int uv = b.Floats(part.UVs.SelectMany(t => new[] { t.X, t.Y }), 2, "VEC2");
            JsonObject attributes = new() { ["POSITION"] = position, ["NORMAL"] = normal, ["TEXCOORD_0"] = uv };
            if (skinned)
            {
                attributes["JOINTS_0"] = b.Shorts(part.PaletteOffsets.SelectMany(slots => new[] { Joint(slots.X, part), Joint(slots.Y, part), Joint(slots.Z, part), (ushort)0 }), "VEC4");
                attributes["WEIGHTS_0"] = b.Floats(part.PaletteOffsets.SelectMany(_ => new[] { 0f, 2f / 3f, 1f / 3f, 0f }), 4, "VEC4");
            }
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
            JsonObject node = new() { ["name"] = part.Name.Length > 0 ? part.Name : $"Part {i}" };
            SetTrs(node, Trs(part.Key(0)));
            CmshPart? geometry = part.Positions.Length > 0 ? part
                : part.ReferenceTo is int r && r >= 0 && r < parts.Count && parts[r].Positions.Length > 0 ? parts[r] : null;
            if (geometry is not null && MeshOf(geometry) is int m and >= 0)
            {
                node["mesh"] = m;
                if (geometry == part && Skinned(part, parts.Count))
                {
                    skins.Add(new JsonObject
                    {
                        ["name"] = part.Name,
                        ["joints"] = new JsonArray(part.Bones.Select(bone => (JsonNode)bone).ToArray()),
                        ["inverseBindMatrices"] = b.Floats(part.Bones.SelectMany(bone => InverseMatrix(mesh.ModelSpace(bone, 0))), 16, "MAT4", vertexData: false),
                    });
                    node["skin"] = skins.Count - 1;
                }
            }
            nodes.Add(node);
        }
        for (int i = 0; i < parts.Count; i++)
        {
            int[] children = Enumerable.Range(0, parts.Count).Where(c => parent[c] == i).ToArray();
            if (children.Length > 0) ((JsonObject)nodes[i]!)["children"] = new JsonArray(children.Select(c => (JsonNode)c).ToArray());
        }
        JsonArray roots = new(Enumerable.Range(0, parts.Count).Where(i => parent[i] < 0).Select(i => (JsonNode)i).ToArray());

        JsonArray animations = Animations(mesh, parts, b);

        JsonObject gltf = new()
        {
            ["asset"] = new JsonObject { ["version"] = "2.0", ["generator"] = "Onslaught Toolkit companion" },
            ["scene"] = 0,
            ["scenes"] = new JsonArray(new JsonObject { ["name"] = mesh.Name, ["nodes"] = roots }),
            ["nodes"] = nodes,
        };
        if (meshes.Count > 0) gltf["meshes"] = meshes;
        if (skins.Count > 0) gltf["skins"] = skins;
        if (animations.Count > 0) gltf["animations"] = animations;
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

    /// <summary>Whether a part is drawn through its bones: 48-byte vertices and a valid BONE list.</summary>
    private static bool Skinned(CmshPart part, int partCount) =>
        part.VertexStride == 48 && part.Bones.Length > 0 && part.Bones.All(bone => bone >= 0 && bone < partCount) &&
        part.PaletteOffsets.Length == part.Positions.Length;

    /// <summary>A palette offset (3 × a BONE index) as the joint index glTF wants.</summary>
    private static ushort Joint(float offset, CmshPart part)
    {
        int index = (int)MathF.Round(offset / 3f);
        return (ushort)Math.Clamp(index, 0, part.Bones.Length - 1);
    }

    /// <summary>The game's evaluation rate: one mode's duration in seconds.</summary>
    public static float Duration(CmshAnimMode mode) =>
        mode.Rate > 0.0001f ? 1f / (20f * mode.Rate) : Math.Max(1, mode.FrameScaler) / 20f;

    private static JsonArray Animations(CmshMesh mesh, IReadOnlyList<CmshPart> parts, Builder b)
    {
        JsonArray animations = [];
        foreach (CmshAnimMode mode in mesh.Modes)
        {
            if (mode.FrameScaler <= 0) continue;
            int samples = mode.FrameScaler + 1;
            float duration = Duration(mode);
            float[] times = Enumerable.Range(0, samples).Select(k => k * duration / mode.FrameScaler).ToArray();
            int input = -1;
            JsonArray channels = [], samplers = [];
            for (int p = 0; p < parts.Count; p++)
            {
                (Vector3 T, Quaternion R, Vector3 S)[] keys = Enumerable.Range(0, samples).Select(k => Trs(parts[p].Key(mode.Start + k))).ToArray();
                // A part needs channels when any sample differs from its node's rest pose (its frame-0 key), even if it
                // holds still during the mode: a mode can start on a different key from frame 0.
                (Vector3 T, Quaternion R, Vector3 S) rest = Trs(parts[p].Key(0));
                if (keys.All(k => k == rest)) continue;
                if (input < 0) input = b.Floats(times, 1, "SCALAR", ([times[0]], [times[^1]]), vertexData: false);
                for (int k = 1; k < keys.Length; k++)
                    if (Quaternion.Dot(keys[k].R, keys[k - 1].R) < 0) keys[k].R = Quaternion.Negate(keys[k].R);
                void Channel(string path, IEnumerable<float> values, int width, string type, string interpolation)
                {
                    samplers.Add(new JsonObject { ["input"] = input, ["output"] = b.Floats(values, width, type, vertexData: false), ["interpolation"] = interpolation });
                    channels.Add(new JsonObject { ["sampler"] = samplers.Count - 1, ["target"] = new JsonObject { ["node"] = p, ["path"] = path } });
                }
                Channel("translation", keys.SelectMany(k => Flat(k.T)), 3, "VEC3", "LINEAR");
                Channel("rotation", keys.SelectMany(k => new[] { k.R.X, k.R.Y, k.R.Z, k.R.W }), 4, "VEC4", "LINEAR");
                if (keys.Any(k => k.S != Vector3.One)) Channel("scale", keys.SelectMany(k => Flat(k.S)), 3, "VEC3", "STEP");
            }
            if (channels.Count == 0) continue;
            string name = mode.Name.Length > 0 ? mode.Name : $"Mode {mode.Id}";
            for (int n = 2; animations.Any(a => (string?)a!["name"] == name); n++) name = $"{mode.Name} ({n})";
            animations.Add(new JsonObject
            {
                ["name"] = name, ["channels"] = channels, ["samplers"] = samplers,
                // The game's own description of the mode, so a tool can find the frames it came from.
                ["extras"] = new JsonObject
                {
                    ["modeId"] = mode.Id, ["startFrame"] = mode.Start, ["frameScaler"] = mode.FrameScaler, ["lastFrame"] = mode.Last, ["rate"] = mode.Rate,
                },
            });
        }
        return animations;
    }

    /// <summary>
    /// A part transform in glTF's frame as translation, rotation and scale. A reflected orientation (determinant −1)
    /// becomes a rotation with a scale of −1 on Z.
    /// </summary>
    public static (Vector3 T, Quaternion R, Vector3 S) Trs(PartTransform t)
    {
        (Vector3 c0, Vector3 c1, Vector3 c2) = Columns(t);
        Vector3 scale = Vector3.One;
        if (Vector3.Dot(c0, Vector3.Cross(c1, c2)) < 0)
        {
            c2 = -c2;
            scale = new Vector3(1, 1, -1);
        }
        Matrix4x4 rows = new(c0.X, c0.Y, c0.Z, 0, c1.X, c1.Y, c1.Z, 0, c2.X, c2.Y, c2.Z, 0, 0, 0, 0, 1);
        return (Convert(t.Position), Quaternion.Normalize(Quaternion.CreateFromRotationMatrix(rows)), scale);
    }

    private static void SetTrs(JsonObject node, (Vector3 T, Quaternion R, Vector3 S) trs)
    {
        if (trs.T != Vector3.Zero) node["translation"] = new JsonArray(trs.T.X, trs.T.Y, trs.T.Z);
        if (trs.R != Quaternion.Identity) node["rotation"] = new JsonArray(trs.R.X, trs.R.Y, trs.R.Z, trs.R.W);
        if (trs.S != Vector3.One) node["scale"] = new JsonArray(trs.S.X, trs.S.Y, trs.S.Z);
    }

    /// <summary>The columns of C·O·Cᵀ (O as the game stores it, C the reflection in <see cref="Convert"/>).</summary>
    private static (Vector3, Vector3, Vector3) Columns(PartTransform t) =>
        (Convert(t.Orientation.Apply(Back(Vector3.UnitX))), Convert(t.Orientation.Apply(Back(Vector3.UnitY))),
            Convert(t.Orientation.Apply(Back(Vector3.UnitZ))));

    /// <summary>The inverse of a model-space transform in glTF's frame, column-major (the orientation is orthonormal).</summary>
    private static float[] InverseMatrix(PartTransform t)
    {
        (Vector3 c0, Vector3 c1, Vector3 c2) = Columns(t);
        Vector3 p = Convert(t.Position);
        // Inverse of [O p] is [Oᵀ, −Oᵀp]: Oᵀ's columns are O's rows, i.e. (c0.i, c1.i, c2.i).
        Vector3 q = -new Vector3(Vector3.Dot(c0, p), Vector3.Dot(c1, p), Vector3.Dot(c2, p));
        return [c0.X, c1.X, c2.X, 0, c0.Y, c1.Y, c2.Y, 0, c0.Z, c1.Z, c2.Z, 0, q.X, q.Y, q.Z, 1];
    }

    /// <summary>Game (x, y, z) to glTF (−x, −z, y).</summary>
    public static Vector3 Convert(Vector3 v) => new(-v.X, -v.Z, v.Y);

    /// <summary>Cᵀ: glTF (X, Y, Z) back to game (−X, Z, −Y).</summary>
    public static Vector3 Back(Vector3 v) => new(-v.X, v.Z, -v.Y);

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

        public int Floats(IEnumerable<float> values, int width, string type, (float[] Min, float[] Max)? bounds = null, bool vertexData = true)
        {
            float[] data = values.ToArray();
            byte[] bytes = new byte[data.Length * 4];
            for (int i = 0; i < data.Length; i++) BinaryPrimitives.WriteSingleLittleEndian(bytes.AsSpan(4 * i), data[i]);
            JsonObject accessor = new()
            {
                ["bufferView"] = View(bytes, vertexData ? 34962 : null), ["componentType"] = 5126, ["count"] = data.Length / width, ["type"] = type,
            };
            if (bounds is { } b)
            {
                accessor["min"] = new JsonArray(b.Min.Select(v => (JsonNode)v).ToArray());
                accessor["max"] = new JsonArray(b.Max.Select(v => (JsonNode)v).ToArray());
            }
            _accessors.Add(accessor);
            return _accessors.Count - 1;
        }

        public int Shorts(IEnumerable<ushort> values, string type)
        {
            ushort[] data = values.ToArray();
            byte[] bytes = new byte[data.Length * 2];
            for (int i = 0; i < data.Length; i++) BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(2 * i), data[i]);
            _accessors.Add(new JsonObject { ["bufferView"] = View(bytes, 34962), ["componentType"] = 5123, ["count"] = data.Length / 4, ["type"] = type });
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
