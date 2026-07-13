// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text;
using System.Runtime.InteropServices;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

public sealed class LocalPresentationContractTests : IDisposable
{
    private readonly string _root = Path.Combine(Path.GetTempPath(), "onslaught-local-presentation-tests", Guid.NewGuid().ToString("N"));

    public LocalPresentationContractTests() => Directory.CreateDirectory(_root);

    [Fact]
    public void TryResolve_RequiresExactExplicitRootAndIgnoresEnvironment()
    {
        WriteManifest("player/aquila.glb");
        WriteMinimalGlb();
        LocalMeshValidation meshValidation = LocalMeshSafety.ValidateFile(Path.Combine(_root, "player", "aquila.glb"));
        Assert.True(meshValidation.IsValid, meshValidation.Error);
        const string legacyEnvVar = "ONSLAUGHT_REBUILD_GODOT_ASSETS";
        string? previous = Environment.GetEnvironmentVariable(legacyEnvVar);
        try
        {
            Environment.SetEnvironmentVariable(legacyEnvVar, _root);
            Assert.Null(LocalPresentationConfig.TryResolve(null, smokeMode: false));
            LocalPresentationConfig? config = LocalPresentationConfig.TryResolve(_root, smokeMode: false, out string? error);
            Assert.True(config is not null, error);
            Assert.Null(error);
        }
        finally
        {
            Environment.SetEnvironmentVariable(legacyEnvVar, previous);
        }
    }

    [Fact]
    public void TryResolve_SmokeAlwaysRejectsLocalAssets()
    {
        WriteManifest("player/aquila.glb");
        WriteMinimalGlb();
        Assert.Null(LocalPresentationConfig.TryResolve(_root, smokeMode: true));
    }

    [Theory]
    [InlineData("../outside.glb")]
    [InlineData("C:/outside.glb")]
    [InlineData("//server/share/outside.glb")]
    [InlineData("player/aquila.gltf")]
    [InlineData("player/aquila.fbx")]
    public void TryResolve_RejectsEscapesAndUnsupportedDependencies(string mesh)
    {
        WriteManifest(mesh);
        Assert.Null(LocalPresentationConfig.TryResolve(_root, smokeMode: false));
    }

    [Theory]
    [InlineData("NaN", "0", "0")]
    [InlineData("1", "Infinity", "0")]
    [InlineData("0", "0", "0")]
    [InlineData("1001", "0", "0")]
    [InlineData("1", "36001", "0")]
    [InlineData("1", "0", "10001")]
    public void TryResolve_RejectsInvalidOrUnboundedTransforms(string scale, string yaw, string offset)
    {
        WriteManifest("player/aquila.glb", scale, yaw, offset);
        WriteMinimalGlb();
        Assert.Null(LocalPresentationConfig.TryResolve(_root, smokeMode: false));
    }

    [Fact]
    public void TryResolve_RejectsOversizedAndDeepManifests()
    {
        Directory.CreateDirectory(Path.Combine(_root, "player"));
        File.WriteAllText(Path.Combine(_root, "manifest.json"), new string(' ', LocalPresentationConfig.MaxManifestBytes + 1));
        Assert.Null(LocalPresentationConfig.TryResolve(_root, smokeMode: false));

        File.WriteAllText(Path.Combine(_root, "manifest.json"), "{\"x\":" + new string('[', 20) + "0" + new string(']', 20) + "}");
        Assert.Null(LocalPresentationConfig.TryResolve(_root, smokeMode: false));
    }

    [Fact]
    public void TryResolve_RejectsDuplicateManifestProperties()
    {
        Directory.CreateDirectory(Path.Combine(_root, "player"));
        WriteMinimalGlb();
        File.WriteAllText(Path.Combine(_root, "manifest.json"), """
        {"schemaVersion":"onslaught-rebuild-local-godot-assets-manifest.v1","presentationMode":"local-user-mesh-preview","nonParityClaim":true,
         "player":{"mesh":"player/aquila.glb"},"player":{"mesh":"player/aquila.glb"}}
        """);
        Assert.Null(LocalPresentationConfig.TryResolve(_root, smokeMode: false));
    }

    [Theory]
    [InlineData("[]")]
    [InlineData("{}")]
    [InlineData("{\"schemaVersion\":1}")]
    [InlineData("{\"schemaVersion\":\"onslaught-rebuild-local-godot-assets-manifest.v1\",\"presentationMode\":\"local-user-mesh-preview\",\"nonParityClaim\":\"true\",\"player\":{\"mesh\":\"player/aquila.glb\"}}")]
    [InlineData("{\"schemaVersion\":\"onslaught-rebuild-local-godot-assets-manifest.v1\",\"presentationMode\":\"local-user-mesh-preview\",\"nonParityClaim\":true,\"player\":\"player/aquila.glb\"}")]
    [InlineData("{\"schemaVersion\":\"onslaught-rebuild-local-godot-assets-manifest.v1\",\"presentationMode\":\"local-user-mesh-preview\",\"nonParityClaim\":true,\"player\":{\"mesh\":7}}")]
    [InlineData("{\"schemaVersion\":\"onslaught-rebuild-local-godot-assets-manifest.v1\",\"presentationMode\":\"local-user-mesh-preview\",\"nonParityClaim\":true,\"player\":{\"mesh\":\"player/aquila.glb\",\"scale\":1e999}}")]
    [InlineData("{\"schemaVersion\":\"onslaught-rebuild-local-godot-assets-manifest.v1\",\"presentationMode\":\"local-user-mesh-preview\",\"nonParityClaim\":true,\"unknown\":true,\"player\":{\"mesh\":\"player/aquila.glb\"}}")]
    public void TryResolve_MalformedBoundedJsonNeverThrows(string json)
    {
        Directory.CreateDirectory(Path.Combine(_root, "player"));
        WriteMinimalGlb();
        File.WriteAllText(Path.Combine(_root, "manifest.json"), json);

        LocalPresentationConfig? result = null;
        string? error = null;
        Exception? exception = Record.Exception(() => result = LocalPresentationConfig.TryResolve(_root, smokeMode: false, out error));

        Assert.Null(exception);
        Assert.Null(result);
        Assert.False(string.IsNullOrWhiteSpace(error));
    }

    [Fact]
    public void ValidateObj_RejectsExcessiveComplexity()
    {
        string path = Path.Combine(_root, "mesh.obj");
        File.WriteAllText(path, "v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n");
        Assert.True(LocalMeshSafety.ValidateObj(path).IsValid);

        File.WriteAllText(path, string.Join('\n', Enumerable.Repeat("v 0 0 0", LocalMeshSafety.MaxObjVertices + 1)));
        Assert.False(LocalMeshSafety.ValidateObj(path).IsValid);
    }

    [Theory]
    [InlineData("v 0 0 0 1")]
    [InlineData("v NaN 0 0")]
    [InlineData("v 0 Infinity 0")]
    [InlineData("v 1000001 0 0")]
    [InlineData("vn 0 1")]
    [InlineData("vn 0 1 0 1")]
    [InlineData("vn 0 NaN 0")]
    [InlineData("vn 0 1000001 0")]
    [InlineData("vt 0")]
    [InlineData("vt 0 1 2")]
    [InlineData("vt -Infinity 0")]
    [InlineData("vt 0 1000001")]
    public void ValidateObj_RejectsWrongArityOrUnsafeNumericComponents(string malformedLine)
    {
        string path = Path.Combine(_root, "mesh.obj");
        File.WriteAllText(path, $"{malformedLine}\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n");
        Assert.False(LocalMeshSafety.ValidateObj(path).IsValid);
    }

    [Fact]
    public void TryResolve_RejectsMeshHardlinkedFromOutsideDeclaredRoot()
    {
        WriteManifest("player/aquila.glb");
        string outside = Path.Combine(Path.GetDirectoryName(_root)!, Guid.NewGuid().ToString("N") + ".glb");
        try
        {
            File.WriteAllBytes(outside, BuildGlb("{\"asset\":{\"version\":\"2.0\"}}"));
            Assert.True(CreateHardLink(Path.Combine(_root, "player", "aquila.glb"), outside, IntPtr.Zero));
            Assert.Null(LocalPresentationConfig.TryResolve(_root, smokeMode: false));
        }
        finally
        {
            if (File.Exists(outside)) File.Delete(outside);
        }
    }

    [Fact]
    public void ValidateFile_RejectsGlbWithExternalUriDependency()
    {
        string path = Path.Combine(_root, "external.glb");
        File.WriteAllBytes(path, BuildGlb("{\"asset\":{\"version\":\"2.0\"},\"buffers\":[{\"uri\":\"outside.bin\",\"byteLength\":4}]}"));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Fact]
    public void ValidateFile_RejectsGlbWithoutMeshPrimitive()
    {
        string path = Path.Combine(_root, "empty.glb");
        File.WriteAllBytes(path, BuildGlb("{\"asset\":{\"version\":\"2.0\"}}"));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Fact]
    public void ValidateFile_RejectsGlbPrimitiveWithEmptyPositionAccessor()
    {
        string path = Path.Combine(_root, "empty-accessor.glb");
        File.WriteAllBytes(path, BuildGlb("{\"asset\":{\"version\":\"2.0\"},\"meshes\":[{\"primitives\":[{\"attributes\":{\"POSITION\":0}}]}],\"accessors\":[{\"count\":0}]}"));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Fact]
    public void ValidateFile_RejectsGlbObjectGraphBeyondSemanticCaps()
    {
        string path = Path.Combine(_root, "many-nodes.glb");
        string nodes = string.Join(',', Enumerable.Repeat("{}", 10_001));
        File.WriteAllBytes(path, BuildGlb($"{{\"asset\":{{\"version\":\"2.0\"}},\"nodes\":[{nodes}],\"meshes\":[{{\"primitives\":[{{\"attributes\":{{\"POSITION\":0}}}}]}}],\"accessors\":[{{\"count\":3}}]}}"));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Fact]
    public void ValidateFile_RejectsExtremeAndAggregateAccessorCounts()
    {
        string path = Path.Combine(_root, "extreme-accessors.glb");
        const string extreme = "{\"asset\":{\"version\":\"2.0\"},\"buffers\":[{\"byteLength\":36}],\"bufferViews\":[{\"buffer\":0,\"byteLength\":36}],\"accessors\":[{\"bufferView\":0,\"componentType\":5126,\"count\":2147483647,\"type\":\"VEC3\"}],\"meshes\":[{\"primitives\":[{\"attributes\":{\"POSITION\":0}}]}]}";
        File.WriteAllBytes(path, BuildGlb(extreme, new byte[36]));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);

        const string aggregate = "{\"asset\":{\"version\":\"2.0\"},\"buffers\":[{\"byteLength\":36}],\"bufferViews\":[{\"buffer\":0,\"byteLength\":36}],\"accessors\":[{\"bufferView\":0,\"componentType\":5126,\"count\":3000000,\"type\":\"VEC3\"},{\"bufferView\":0,\"componentType\":5126,\"count\":3000000,\"type\":\"VEC3\"}],\"meshes\":[{\"primitives\":[{\"attributes\":{\"POSITION\":0}}]}]}";
        File.WriteAllBytes(path, BuildGlb(aggregate, new byte[36]));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Theory]
    [InlineData("{\"asset\":{\"version\":\"2.0\"},\"buffers\":[{\"byteLength\":36}],\"bufferViews\":[{\"buffer\":0,\"byteOffset\":20,\"byteLength\":20}],\"accessors\":[{\"bufferView\":0,\"componentType\":5126,\"count\":3,\"type\":\"VEC3\"}],\"meshes\":[{\"primitives\":[{\"attributes\":{\"POSITION\":0}}]}]}")]
    [InlineData("{\"asset\":{\"version\":\"2.0\"},\"buffers\":[{\"byteLength\":36}],\"bufferViews\":[{\"buffer\":0,\"byteLength\":36,\"byteStride\":8}],\"accessors\":[{\"bufferView\":0,\"componentType\":5126,\"count\":3,\"type\":\"VEC3\"}],\"meshes\":[{\"primitives\":[{\"attributes\":{\"POSITION\":0}}]}]}")]
    public void ValidateFile_RejectsBufferViewAndAccessorRanges(string json)
    {
        string path = Path.Combine(_root, "bad-range.glb");
        File.WriteAllBytes(path, BuildGlb(json, new byte[36]));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Fact]
    public void ValidateFile_RejectsSparseAccessorOutsideExactBinRange()
    {
        string path = Path.Combine(_root, "bad-sparse.glb");
        const string json = "{\"asset\":{\"version\":\"2.0\"},\"buffers\":[{\"byteLength\":40}],\"bufferViews\":[{\"buffer\":0,\"byteLength\":4},{\"buffer\":0,\"byteOffset\":4,\"byteLength\":36}],\"accessors\":[{\"componentType\":5126,\"count\":3,\"type\":\"VEC3\",\"sparse\":{\"count\":3,\"indices\":{\"bufferView\":0,\"byteOffset\":3,\"componentType\":5123},\"values\":{\"bufferView\":1}}}],\"meshes\":[{\"primitives\":[{\"attributes\":{\"POSITION\":0}}]}]}";
        File.WriteAllBytes(path, BuildGlb(json, new byte[40]));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Fact]
    public void ValidateFile_RejectsOversizedAllocationDrivingArrays()
    {
        string path = Path.Combine(_root, "many-materials.glb");
        string materials = string.Join(',', Enumerable.Repeat("{}", 10_001));
        string json = $"{{\"asset\":{{\"version\":\"2.0\"}},\"buffers\":[{{\"byteLength\":36}}],\"bufferViews\":[{{\"buffer\":0,\"byteLength\":36}}],\"accessors\":[{{\"bufferView\":0,\"componentType\":5126,\"count\":3,\"type\":\"VEC3\"}}],\"meshes\":[{{\"primitives\":[{{\"attributes\":{{\"POSITION\":0}}}}]}}],\"materials\":[{materials}]}}";
        File.WriteAllBytes(path, BuildGlb(json, new byte[36]));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Fact]
    public void ValidateFile_RejectsAggregatePrimitiveVertexAndIndexBudgets()
    {
        string path = Path.Combine(_root, "aggregate-primitives.glb");
        const int vertexBytes = 1_100_000 * 12;
        string vertices = $"{{\"asset\":{{\"version\":\"2.0\"}},\"buffers\":[{{\"byteLength\":{vertexBytes}}}],\"bufferViews\":[{{\"buffer\":0,\"byteLength\":{vertexBytes}}}],\"accessors\":[{{\"bufferView\":0,\"componentType\":5126,\"count\":1100000,\"type\":\"VEC3\"}}],\"meshes\":[{{\"primitives\":[{{\"attributes\":{{\"POSITION\":0}}}},{{\"attributes\":{{\"POSITION\":0}}}}]}}]}}";
        File.WriteAllBytes(path, BuildGlb(vertices, new byte[vertexBytes]));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);

        const int indexCount = 3_100_000;
        const int indexBufferBytes = 36 + indexCount;
        string indices = $"{{\"asset\":{{\"version\":\"2.0\"}},\"buffers\":[{{\"byteLength\":{indexBufferBytes}}}],\"bufferViews\":[{{\"buffer\":0,\"byteLength\":36}},{{\"buffer\":0,\"byteOffset\":36,\"byteLength\":{indexCount}}}],\"accessors\":[{{\"bufferView\":0,\"componentType\":5126,\"count\":3,\"type\":\"VEC3\"}},{{\"bufferView\":1,\"componentType\":5121,\"count\":{indexCount},\"type\":\"SCALAR\"}}],\"meshes\":[{{\"primitives\":[{{\"attributes\":{{\"POSITION\":0}},\"indices\":1}},{{\"attributes\":{{\"POSITION\":0}},\"indices\":1}}]}}]}}";
        File.WriteAllBytes(path, BuildGlb(indices, new byte[indexBufferBytes]));
        Assert.False(LocalMeshSafety.ValidateFile(path).IsValid);
    }

    [Fact]
    public void GodotLoader_ConsumesHeldGlbBytesAndRequiresRenderableMesh()
    {
        string source = File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "godot-source", "LocalAssetMeshLoader.cs"));
        Assert.Contains("AppendFromBuffer", source, StringComparison.Ordinal);
        Assert.DoesNotContain("AppendFromFile", source, StringComparison.Ordinal);
        Assert.Contains("ContainsRenderableMesh", source, StringComparison.Ordinal);
    }

    [Fact]
    public void Hud_DescribesUnreceiptedMeshesNeutrally()
    {
        string source = File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "godot-source", "FirstFlightHud.cs"));
        Assert.Contains("user-supplied local mesh", source, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("retail-derived", source, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void LocalPresentationLabels_AreOriginNeutralWithoutReceiptBinding()
    {
        string[] files =
        [
            Path.Combine(AppContext.BaseDirectory, "godot-source", "FirstFlightHud.cs"),
            Path.Combine(AppContext.BaseDirectory, "local-presentation", "README.md"),
            Path.Combine(AppContext.BaseDirectory, "local-presentation", "local-assets.layout.json"),
            Path.Combine(AppContext.BaseDirectory, "local-presentation", "Initialize-LocalGodotAssets.ps1"),
        ];
        foreach (string file in files)
        {
            string source = File.ReadAllText(file);
            Assert.DoesNotContain("retail mesh preview", source, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("retail preview assets", source, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("retail-derived presentation", source, StringComparison.OrdinalIgnoreCase);
        }
        Assert.Contains("user-supplied local", File.ReadAllText(files[1]), StringComparison.OrdinalIgnoreCase);
        Assert.Contains("user-supplied local", File.ReadAllText(files[2]), StringComparison.OrdinalIgnoreCase);
    }

    public void Dispose()
    {
        if (Directory.Exists(_root)) Directory.Delete(_root, recursive: true);
    }

    private void WriteManifest(string mesh, string scale = "1", string yaw = "0", string offset = "0")
    {
        Directory.CreateDirectory(Path.Combine(_root, "player"));
        string json = $$"""
        {
          "schemaVersion": "onslaught-rebuild-local-godot-assets-manifest.v1",
          "presentationMode": "local-user-mesh-preview",
          "nonParityClaim": true,
          "player": { "mesh": "{{mesh}}", "scale": {{scale}}, "yawDegrees": {{yaw}}, "yOffsetMeters": {{offset}} }
        }
        """;
        File.WriteAllText(Path.Combine(_root, "manifest.json"), json, Encoding.UTF8);
    }

    private void WriteMinimalGlb()
    {
        const string json = "{\"asset\":{\"version\":\"2.0\"},\"scene\":0,\"scenes\":[{\"nodes\":[0]}],\"nodes\":[{\"mesh\":0}],\"meshes\":[{\"primitives\":[{\"attributes\":{\"POSITION\":0}}]}],\"accessors\":[{\"bufferView\":0,\"componentType\":5126,\"count\":3,\"type\":\"VEC3\",\"max\":[1,1,0],\"min\":[0,0,0]}],\"bufferViews\":[{\"buffer\":0,\"byteOffset\":0,\"byteLength\":36}],\"buffers\":[{\"byteLength\":36}]}";
        byte[] triangle = new byte[36];
        new float[] { 0, 0, 0, 1, 0, 0, 0, 1, 0 }.CopyTo(MemoryMarshal.Cast<byte, float>(triangle));
        File.WriteAllBytes(Path.Combine(_root, "player", "aquila.glb"), BuildGlb(json, triangle));
    }

    private static byte[] BuildGlb(string json, byte[]? binary = null)
    {
        byte[] jsonBytes = Encoding.UTF8.GetBytes(json);
        int jsonPadded = (jsonBytes.Length + 3) & ~3;
        int binaryPadded = binary is null ? 0 : (binary.Length + 3) & ~3;
        int binaryChunkBytes = binary is null ? 0 : 8 + binaryPadded;
        byte[] bytes = new byte[20 + jsonPadded + binaryChunkBytes];
        Encoding.ASCII.GetBytes("glTF").CopyTo(bytes, 0);
        BitConverter.GetBytes(2u).CopyTo(bytes, 4);
        BitConverter.GetBytes((uint)bytes.Length).CopyTo(bytes, 8);
        BitConverter.GetBytes((uint)jsonPadded).CopyTo(bytes, 12);
        BitConverter.GetBytes(0x4E4F534Au).CopyTo(bytes, 16);
        jsonBytes.CopyTo(bytes, 20);
        Array.Fill(bytes, (byte)0x20, 20 + jsonBytes.Length, jsonPadded - jsonBytes.Length);
        if (binary is not null)
        {
            int chunkOffset = 20 + jsonPadded;
            BitConverter.GetBytes((uint)binaryPadded).CopyTo(bytes, chunkOffset);
            BitConverter.GetBytes(0x004E4942u).CopyTo(bytes, chunkOffset + 4);
            binary.CopyTo(bytes, chunkOffset + 8);
        }
        return bytes;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool CreateHardLink(string newFileName, string existingFileName, IntPtr securityAttributes);
}
