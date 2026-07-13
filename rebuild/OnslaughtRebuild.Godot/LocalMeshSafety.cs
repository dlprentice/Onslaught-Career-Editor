// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
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
        int vertices = 0, attributes = 0, faces = 0, triangles = 0;
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        using var reader = new StreamReader(stream);
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
                    if (parts.Length < 4 || !Finite(parts[1]) || !Finite(parts[2]) || !Finite(parts[3]) || ++vertices > MaxObjVertices)
                        return LocalMeshValidation.Invalid("OBJ vertex is invalid or exceeds the limit");
                    break;
                case "vn":
                case "vt":
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
        Span<byte> header = stackalloc byte[20];
        using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (stream.Read(header) != header.Length || header[0] != (byte)'g' || header[1] != (byte)'l' || header[2] != (byte)'T' || header[3] != (byte)'F')
            return LocalMeshValidation.Invalid("GLB header is invalid");
        uint version = BitConverter.ToUInt32(header[4..8]);
        uint declaredLength = BitConverter.ToUInt32(header[8..12]);
        uint jsonLength = BitConverter.ToUInt32(header[12..16]);
        uint jsonType = BitConverter.ToUInt32(header[16..20]);
        if (version != 2 || declaredLength != size || jsonType != 0x4E4F534A || jsonLength == 0 || jsonLength > size - 20)
            return LocalMeshValidation.Invalid("GLB version, length, or JSON chunk is invalid");
        byte[] json = new byte[checked((int)jsonLength)];
        stream.ReadExactly(json);
        using JsonDocument document = JsonDocument.Parse(json, new JsonDocumentOptions { MaxDepth = 32 });
        return ContainsExternalUri(document.RootElement)
            ? LocalMeshValidation.Invalid("GLB must be self-contained and cannot reference external URI dependencies")
            : LocalMeshValidation.Valid();
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
