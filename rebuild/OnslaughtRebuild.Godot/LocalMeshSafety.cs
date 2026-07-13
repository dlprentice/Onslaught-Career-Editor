// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Buffers.Binary;
using System.Runtime.InteropServices;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;

namespace OnslaughtRebuild.GodotClient;

public static class LocalMeshSafety
{
    public const long MaxGlbBytes = 128L * 1024 * 1024;
    public const long MaxObjBytes = 32L * 1024 * 1024;
    public const int MaxObjVertices = 100_000;
    public const int MaxObjAttributes = 200_000;
    public const int MaxObjFaces = 200_000;
    public const int MaxObjTriangles = 400_000;
    public const int MaxObjLineChars = 16_384;
    public const int MaxGlbNodes = 10_000;
    public const int MaxGlbMeshes = 5_000;
    public const int MaxGlbAccessors = 50_000;
    public const int MaxGlbPrimitives = 50_000;
    public const int MaxGlbImages = 10_000;
    private const float MaxCoordinateMagnitude = 1_000_000f;

    public static LocalMeshValidation ValidateFile(string path)
    {
        try
        {
            var info = new FileInfo(path);
            if (!info.Exists || info.Attributes.HasFlag(FileAttributes.Directory) || info.Attributes.HasFlag(FileAttributes.ReparsePoint) ||
                !LocalFileSafety.IsRegularSingleLink(path))
                return LocalMeshValidation.Invalid("mesh is not a regular local file");
            return Path.GetExtension(path).ToLowerInvariant() switch
            {
                ".glb" => ValidateGlb(path, info.Length),
                ".obj" => ValidateObj(path),
                _ => LocalMeshValidation.Invalid("mesh extension must be .glb or .obj"),
            };
        }
        catch (Exception exception) when (exception is IOException or InvalidDataException or JsonException or UnauthorizedAccessException or ArgumentException or NotSupportedException)
        {
            return LocalMeshValidation.Invalid(exception.Message);
        }
    }

    public static LocalMeshValidation ValidateObj(string path)
    {
        var info = new FileInfo(path);
        if (!info.Exists || info.Length is <= 0 or > MaxObjBytes) return LocalMeshValidation.Invalid("OBJ size is outside the supported bound");
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (stream.Length is <= 0 or > MaxObjBytes) return LocalMeshValidation.Invalid("OBJ leased size is outside the supported bound");
        using var reader = new StreamReader(stream);
        return ValidateObjReader(reader);
    }

    public static LocalMeshValidation ValidateObjBytes(byte[] bytes)
    {
        if (bytes.LongLength is <= 0 or > MaxObjBytes) return LocalMeshValidation.Invalid("OBJ size is outside the supported bound");
        using var stream = new MemoryStream(bytes, writable: false);
        using var reader = new StreamReader(stream);
        return ValidateObjReader(reader);
    }

    private static LocalMeshValidation ValidateObjReader(TextReader reader)
    {
        int vertices = 0, attributes = 0, faces = 0, triangles = 0;
        string? line;
        while ((line = reader.ReadLine()) is not null)
        {
            if (line.Length > MaxObjLineChars) return LocalMeshValidation.Invalid("OBJ line is too long");
            string trimmed = line.Trim();
            if (trimmed.Length == 0 || trimmed.StartsWith('#')) continue;
            string[] parts = trimmed.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            switch (parts[0])
            {
                case "v":
                    if (parts.Length != 4 || !Finite(parts[1]) || !Finite(parts[2]) || !Finite(parts[3]) || ++vertices > MaxObjVertices)
                        return LocalMeshValidation.Invalid("OBJ vertex is invalid or exceeds the limit");
                    break;
                case "vn":
                    if (parts.Length != 4 || !Finite(parts[1]) || !Finite(parts[2]) || !Finite(parts[3]))
                        return LocalMeshValidation.Invalid("OBJ normal is invalid");
                    if (++attributes > MaxObjAttributes) return LocalMeshValidation.Invalid("OBJ attributes exceed the limit");
                    break;
                case "vt":
                    if (parts.Length != 3 || !Finite(parts[1]) || !Finite(parts[2]))
                        return LocalMeshValidation.Invalid("OBJ texture coordinate is invalid");
                    if (++attributes > MaxObjAttributes) return LocalMeshValidation.Invalid("OBJ attributes exceed the limit");
                    break;
                case "f":
                    if (parts.Length < 4 || ++faces > MaxObjFaces) return LocalMeshValidation.Invalid("OBJ face is invalid or exceeds the limit");
                    triangles = checked(triangles + parts.Length - 3);
                    if (triangles > MaxObjTriangles) return LocalMeshValidation.Invalid("OBJ triangles exceed the limit");
                    break;
                case "o": case "g": case "s":
                    break;
                default:
                    return LocalMeshValidation.Invalid($"unsupported OBJ statement '{parts[0]}'");
            }
        }
        return vertices > 0 && faces > 0 ? LocalMeshValidation.Valid() : LocalMeshValidation.Invalid("OBJ has no usable geometry");
    }

    private static LocalMeshValidation ValidateGlb(string path, long size)
    {
        if (size is < 20 or > MaxGlbBytes) return LocalMeshValidation.Invalid("GLB size is outside the supported bound");
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (stream.Length is < 20 or > MaxGlbBytes || stream.Length != size) return LocalMeshValidation.Invalid("GLB leased size changed or is outside the supported bound");
        byte[] bytes = new byte[checked((int)stream.Length)];
        stream.ReadExactly(bytes);
        return ValidateGlbBytes(bytes);
    }

    public static LocalMeshValidation ValidateGlbBytes(ReadOnlySpan<byte> bytes)
    {
        try
        {
            if (bytes.Length is < 20 || bytes.Length > MaxGlbBytes) return LocalMeshValidation.Invalid("GLB size is outside the supported bound");
            if (!bytes[..4].SequenceEqual("glTF"u8) || BinaryPrimitives.ReadUInt32LittleEndian(bytes[4..8]) != 2 ||
                BinaryPrimitives.ReadUInt32LittleEndian(bytes[8..12]) != bytes.Length)
                return LocalMeshValidation.Invalid("GLB header is invalid");

            int offset = 12;
            int chunkCount = 0;
            ReadOnlySpan<byte> json = default;
            while (offset < bytes.Length)
            {
                if (bytes.Length - offset < 8) return LocalMeshValidation.Invalid("GLB chunk header is truncated");
                uint chunkLength = BinaryPrimitives.ReadUInt32LittleEndian(bytes.Slice(offset, 4));
                uint chunkType = BinaryPrimitives.ReadUInt32LittleEndian(bytes.Slice(offset + 4, 4));
                offset += 8;
                if (chunkLength == 0 || chunkLength > int.MaxValue || chunkLength > bytes.Length - offset || (chunkLength & 3) != 0)
                    return LocalMeshValidation.Invalid("GLB chunk length is invalid");
                if (chunkCount == 0)
                {
                    if (chunkType != 0x4E4F534A) return LocalMeshValidation.Invalid("GLB first chunk must be JSON");
                    json = bytes.Slice(offset, (int)chunkLength);
                }
                else if (chunkCount > 1 || chunkType != 0x004E4942)
                {
                    return LocalMeshValidation.Invalid("GLB supports only one optional embedded BIN chunk");
                }
                offset += (int)chunkLength;
                chunkCount++;
            }
            if (offset != bytes.Length || chunkCount == 0) return LocalMeshValidation.Invalid("GLB chunks do not cover the declared file");

            using JsonDocument document = JsonDocument.Parse(json.ToArray(), new JsonDocumentOptions { MaxDepth = 32 });
            JsonElement root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object) return LocalMeshValidation.Invalid("GLB JSON root must be an object");
            if (ContainsExternalUri(root)) return LocalMeshValidation.Invalid("GLB must be self-contained and cannot reference external URI dependencies");
            return ValidateGlbSemantics(root);
        }
        catch (Exception exception) when (exception is JsonException or InvalidDataException or ArgumentException or OverflowException)
        {
            return LocalMeshValidation.Invalid(exception.Message);
        }
    }

    private static LocalMeshValidation ValidateGlbSemantics(JsonElement root)
    {
        if (!TryGetBoundedArray(root, "nodes", MaxGlbNodes, required: false, out _) ||
            !TryGetBoundedArray(root, "meshes", MaxGlbMeshes, required: true, out JsonElement meshes) ||
            !TryGetBoundedArray(root, "accessors", MaxGlbAccessors, required: true, out JsonElement accessors) ||
            !TryGetBoundedArray(root, "images", MaxGlbImages, required: false, out _))
            return LocalMeshValidation.Invalid("GLB semantic array is missing, malformed, or exceeds its limit");

        int primitiveCount = 0;
        bool hasRenderablePrimitive = false;
        foreach (JsonElement mesh in meshes.EnumerateArray())
        {
            if (mesh.ValueKind != JsonValueKind.Object || !mesh.TryGetProperty("primitives", out JsonElement primitives) || primitives.ValueKind != JsonValueKind.Array)
                return LocalMeshValidation.Invalid("GLB mesh primitives are malformed");
            primitiveCount = checked(primitiveCount + primitives.GetArrayLength());
            if (primitiveCount > MaxGlbPrimitives) return LocalMeshValidation.Invalid("GLB primitives exceed the supported limit");
            foreach (JsonElement primitive in primitives.EnumerateArray())
            {
                if (primitive.ValueKind != JsonValueKind.Object || !primitive.TryGetProperty("attributes", out JsonElement attributes) ||
                    attributes.ValueKind != JsonValueKind.Object || !attributes.TryGetProperty("POSITION", out JsonElement position) ||
                    !position.TryGetInt32(out int accessorIndex) || accessorIndex < 0 || accessorIndex >= accessors.GetArrayLength()) continue;
                JsonElement accessor = accessors[accessorIndex];
                if (accessor.ValueKind == JsonValueKind.Object && accessor.TryGetProperty("count", out JsonElement count) &&
                    count.TryGetInt32(out int vertexCount) && vertexCount > 0) hasRenderablePrimitive = true;
            }
        }
        return hasRenderablePrimitive
            ? LocalMeshValidation.Valid()
            : LocalMeshValidation.Invalid("GLB contains no mesh primitive with a nonempty POSITION accessor");
    }

    private static bool TryGetBoundedArray(JsonElement root, string name, int maximum, bool required, out JsonElement array)
    {
        if (!root.TryGetProperty(name, out array)) return !required;
        return array.ValueKind == JsonValueKind.Array && array.GetArrayLength() <= maximum;
    }

    private static bool ContainsExternalUri(JsonElement element)
    {
        if (element.ValueKind == JsonValueKind.Object)
        {
            foreach (JsonProperty property in element.EnumerateObject())
            {
                if (string.Equals(property.Name, "uri", StringComparison.Ordinal)) return true;
                if (ContainsExternalUri(property.Value)) return true;
            }
        }
        else if (element.ValueKind == JsonValueKind.Array)
        {
            foreach (JsonElement child in element.EnumerateArray()) if (ContainsExternalUri(child)) return true;
        }
        return false;
    }

    private static bool Finite(string value) =>
        float.TryParse(value, NumberStyles.Float, CultureInfo.InvariantCulture, out float parsed) &&
        float.IsFinite(parsed) && Math.Abs(parsed) <= MaxCoordinateMagnitude;
}

public readonly record struct LocalMeshValidation(bool IsValid, string? Error)
{
    public static LocalMeshValidation Valid() => new(true, null);
    public static LocalMeshValidation Invalid(string error) => new(false, error);
}

internal static class LocalFileSafety
{
    public static bool IsRegularSingleLink(string path)
    {
        if (!OperatingSystem.IsWindows()) return false;
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        return GetFileInformationByHandle(stream.SafeFileHandle, out ByHandleFileInformation information) && information.NumberOfLinks == 1;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetFileInformationByHandle(SafeFileHandle handle, out ByHandleFileInformation information);

    [StructLayout(LayoutKind.Sequential)]
    private struct ByHandleFileInformation
    {
        public uint FileAttributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
        public uint VolumeSerialNumber;
        public uint FileSizeHigh;
        public uint FileSizeLow;
        public uint NumberOfLinks;
        public uint FileIndexHigh;
        public uint FileIndexLow;
    }
}
