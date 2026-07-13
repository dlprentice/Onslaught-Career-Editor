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
    public const int MaxGlbBufferViews = 50_000;
    public const int MaxGlbPrimitives = 50_000;
    public const int MaxGlbImages = 10_000;
    public const int MaxGlbMaterials = 10_000;
    public const int MaxGlbTextures = 10_000;
    public const long MaxGlbAggregateAccessorElements = 5_000_000;
    public const long MaxGlbAggregatePrimitiveVertices = 2_000_000;
    public const long MaxGlbAggregatePrimitiveIndices = 6_000_000;
    private const int MaxGlbTotalJsonValues = 250_000;
    private const int MaxGlbAnyArrayElements = 50_000;
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
            ReadOnlySpan<byte> bin = default;
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
                else
                {
                    bin = bytes.Slice(offset, (int)chunkLength);
                }
                offset += (int)chunkLength;
                chunkCount++;
            }
            if (offset != bytes.Length || chunkCount == 0) return LocalMeshValidation.Invalid("GLB chunks do not cover the declared file");

            using JsonDocument document = JsonDocument.Parse(json.ToArray(), new JsonDocumentOptions { MaxDepth = 32 });
            JsonElement root = document.RootElement;
            if (root.ValueKind != JsonValueKind.Object) return LocalMeshValidation.Invalid("GLB JSON root must be an object");
            if (ContainsExternalUri(root)) return LocalMeshValidation.Invalid("GLB must be self-contained and cannot reference external URI dependencies");
            int jsonValues = 0;
            if (!ValidateJsonShape(root, ref jsonValues)) return LocalMeshValidation.Invalid("GLB JSON object graph, extension data, or array length exceeds the supported core-profile bound");
            return ValidateGlbSemantics(root, bin);
        }
        catch (Exception exception) when (exception is JsonException or InvalidDataException or ArgumentException or OverflowException)
        {
            return LocalMeshValidation.Invalid(exception.Message);
        }
    }

    private static LocalMeshValidation ValidateGlbSemantics(JsonElement root, ReadOnlySpan<byte> bin)
    {
        if (!root.TryGetProperty("asset", out JsonElement asset) || asset.ValueKind != JsonValueKind.Object ||
            !asset.TryGetProperty("version", out JsonElement version) || version.ValueKind != JsonValueKind.String || version.GetString() != "2.0")
            return LocalMeshValidation.Invalid("GLB asset.version must be 2.0");

        if (!TryGetBoundedArray(root, "scenes", 256, required: false, out JsonElement scenes) ||
            !TryGetBoundedArray(root, "nodes", MaxGlbNodes, required: false, out JsonElement nodes) ||
            !TryGetBoundedArray(root, "meshes", MaxGlbMeshes, required: true, out JsonElement meshes) ||
            !TryGetBoundedArray(root, "accessors", MaxGlbAccessors, required: true, out JsonElement accessors) ||
            !TryGetBoundedArray(root, "bufferViews", MaxGlbBufferViews, required: true, out JsonElement bufferViewsJson) ||
            !TryGetBoundedArray(root, "buffers", 1, required: true, out JsonElement buffers) || buffers.GetArrayLength() != 1 ||
            !TryGetBoundedArray(root, "images", MaxGlbImages, required: false, out JsonElement images) ||
            !TryGetBoundedArray(root, "textures", MaxGlbTextures, required: false, out _) ||
            !TryGetBoundedArray(root, "materials", MaxGlbMaterials, required: false, out _) ||
            !TryGetBoundedArray(root, "samplers", 1_000, required: false, out _) ||
            !TryGetBoundedArray(root, "animations", 1_000, required: false, out JsonElement animations) ||
            !TryGetBoundedArray(root, "skins", 1_000, required: false, out JsonElement skins) ||
            !TryGetBoundedArray(root, "cameras", 1_000, required: false, out _) ||
            !TryGetBoundedArray(root, "extensionsUsed", 64, required: false, out _) ||
            !TryGetBoundedArray(root, "extensionsRequired", 64, required: false, out _))
            return LocalMeshValidation.Invalid("GLB semantic array is missing, malformed, or exceeds its limit");

        JsonElement buffer = buffers[0];
        if (buffer.ValueKind != JsonValueKind.Object || !TryGetRequiredNonNegativeInteger(buffer, "byteLength", out long bufferLength) ||
            bufferLength <= 0 || bufferLength > MaxGlbBytes || bin.Length < bufferLength || bin.Length - bufferLength > 3)
            return LocalMeshValidation.Invalid("GLB buffer length does not match the exact embedded BIN chunk");

        var bufferViews = new GlbBufferView[bufferViewsJson.GetArrayLength()];
        for (int index = 0; index < bufferViews.Length; index++)
        {
            JsonElement view = bufferViewsJson[index];
            if (view.ValueKind != JsonValueKind.Object || !TryGetOptionalNonNegativeInteger(view, "buffer", 0, out long bufferIndex) || bufferIndex != 0 ||
                !TryGetOptionalNonNegativeInteger(view, "byteOffset", 0, out long byteOffset) ||
                !TryGetRequiredNonNegativeInteger(view, "byteLength", out long byteLength) || byteLength <= 0 ||
                !TryGetOptionalNonNegativeInteger(view, "byteStride", 0, out long byteStride) || byteStride > 252 ||
                (byteStride != 0 && (byteStride < 4 || (byteStride & 3) != 0)) ||
                !RangeFits(byteOffset, byteLength, bufferLength) || !RangeFits(byteOffset, byteLength, bin.Length))
                return LocalMeshValidation.Invalid("GLB bufferView offset, length, buffer, or stride is invalid");
            bufferViews[index] = new GlbBufferView(byteOffset, byteLength, checked((int)byteStride));
        }

        var accessorInfo = new GlbAccessor[accessors.GetArrayLength()];
        long aggregateAccessorElements = 0;
        long aggregateSparseElements = 0;
        for (int index = 0; index < accessorInfo.Length; index++)
        {
            JsonElement accessor = accessors[index];
            if (accessor.ValueKind != JsonValueKind.Object || !TryGetRequiredNonNegativeInteger(accessor, "count", out long count) || count <= 0 ||
                !TryGetRequiredInteger(accessor, "componentType", out int componentType) || ComponentByteSize(componentType) is not int componentBytes ||
                !accessor.TryGetProperty("type", out JsonElement typeValue) || typeValue.ValueKind != JsonValueKind.String ||
                typeValue.GetString() is not string accessorType || ElementByteSize(accessorType, componentBytes) is not int elementBytes ||
                ElementComponentCount(accessorType) is not int componentCount ||
                !TryGetOptionalNonNegativeInteger(accessor, "byteOffset", 0, out long accessorOffset) ||
                !ValidateAccessorBoundsArray(accessor, "min", componentCount) || !ValidateAccessorBoundsArray(accessor, "max", componentCount))
                return LocalMeshValidation.Invalid("GLB accessor count, component type, element type, or offset is invalid");

            aggregateAccessorElements = checked(aggregateAccessorElements + count);
            if (aggregateAccessorElements > MaxGlbAggregateAccessorElements)
                return LocalMeshValidation.Invalid("GLB aggregate accessor element count exceeds the supported limit");

            bool hasView = accessor.TryGetProperty("bufferView", out JsonElement accessorViewValue);
            bool hasSparse = accessor.TryGetProperty("sparse", out JsonElement sparse);
            if (!hasView && !hasSparse) return LocalMeshValidation.Invalid("GLB accessor must have a bufferView or bounded sparse storage");
            if (hasView)
            {
                if (!accessorViewValue.TryGetInt32(out int viewIndex) || viewIndex < 0 || viewIndex >= bufferViews.Length ||
                    !AccessorFits(bufferViews[viewIndex], accessorOffset, count, elementBytes, componentBytes))
                    return LocalMeshValidation.Invalid("GLB accessor range or stride escapes its bufferView/BIN storage");
            }

            if (hasSparse)
            {
                if (!ValidateSparseAccessor(sparse, count, elementBytes, componentBytes, bufferViews, ref aggregateSparseElements))
                    return LocalMeshValidation.Invalid("GLB sparse accessor indices or values escape their bufferView/BIN storage");
            }
            accessorInfo[index] = new GlbAccessor(count, componentType, accessorType);
        }

        if (!ValidateNestedAllocationArrays(scenes, nodes, meshes, animations, skins))
            return LocalMeshValidation.Invalid("GLB nested allocation-driving array exceeds the supported limit");

        foreach (JsonElement image in images.ValueKind == JsonValueKind.Array ? images.EnumerateArray() : default)
        {
            if (image.ValueKind != JsonValueKind.Object || !image.TryGetProperty("bufferView", out JsonElement imageView) ||
                !imageView.TryGetInt32(out int imageViewIndex) || imageViewIndex < 0 || imageViewIndex >= bufferViews.Length || bufferViews[imageViewIndex].Stride != 0 ||
                !image.TryGetProperty("mimeType", out JsonElement mimeType) || mimeType.ValueKind != JsonValueKind.String || mimeType.GetString() is not ("image/png" or "image/jpeg"))
                return LocalMeshValidation.Invalid("GLB embedded image must reference a valid bounded bufferView");
        }

        int primitiveCount = 0;
        long aggregateVertices = 0;
        long aggregateIndices = 0;
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
                    attributes.EnumerateObject().Count() > 32 || !ValidateAccessorReferences(attributes, accessorInfo.Length) ||
                    !position.TryGetInt32(out int accessorIndex) || accessorIndex < 0 || accessorIndex >= accessorInfo.Length)
                    return LocalMeshValidation.Invalid("GLB primitive attributes or POSITION accessor are invalid");
                GlbAccessor positionAccessor = accessorInfo[accessorIndex];
                if (positionAccessor.Type != "VEC3" || positionAccessor.ComponentType != 5126)
                    return LocalMeshValidation.Invalid("GLB POSITION accessor must use float VEC3 elements");
                aggregateVertices = checked(aggregateVertices + positionAccessor.Count);
                if (aggregateVertices > MaxGlbAggregatePrimitiveVertices) return LocalMeshValidation.Invalid("GLB aggregate primitive vertex count exceeds the supported limit");
                if (primitive.TryGetProperty("indices", out JsonElement indices))
                {
                    if (!indices.TryGetInt32(out int indicesIndex) || indicesIndex < 0 || indicesIndex >= accessorInfo.Length) return LocalMeshValidation.Invalid("GLB primitive indices accessor is invalid");
                    GlbAccessor indexAccessor = accessorInfo[indicesIndex];
                    if (indexAccessor.Type != "SCALAR" || indexAccessor.ComponentType is not (5121 or 5123 or 5125)) return LocalMeshValidation.Invalid("GLB primitive indices accessor type is invalid");
                    aggregateIndices = checked(aggregateIndices + indexAccessor.Count);
                    if (aggregateIndices > MaxGlbAggregatePrimitiveIndices) return LocalMeshValidation.Invalid("GLB aggregate primitive index count exceeds the supported limit");
                }
                if (primitive.TryGetProperty("targets", out JsonElement targets) &&
                    (targets.ValueKind != JsonValueKind.Array || targets.GetArrayLength() > 16 || targets.EnumerateArray().Any(target => target.ValueKind != JsonValueKind.Object || target.EnumerateObject().Count() > 32 || !ValidateAccessorReferences(target, accessorInfo.Length))))
                    return LocalMeshValidation.Invalid("GLB morph targets exceed the supported allocation bound");
                hasRenderablePrimitive = true;
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

    private static bool ValidateJsonShape(JsonElement element, ref int total)
    {
        if (++total > MaxGlbTotalJsonValues) return false;
        if (element.ValueKind == JsonValueKind.Object)
        {
            foreach (JsonProperty property in element.EnumerateObject())
            {
                if (property.NameEquals("extensions")) return false;
                if (!ValidateJsonShape(property.Value, ref total)) return false;
            }
        }
        else if (element.ValueKind == JsonValueKind.Array)
        {
            if (element.GetArrayLength() > MaxGlbAnyArrayElements) return false;
            foreach (JsonElement child in element.EnumerateArray()) if (!ValidateJsonShape(child, ref total)) return false;
        }
        return true;
    }

    private static bool ValidateNestedAllocationArrays(JsonElement scenes, JsonElement nodes, JsonElement meshes, JsonElement animations, JsonElement skins)
    {
        long references = 0;
        foreach (JsonElement scene in scenes.ValueKind == JsonValueKind.Array ? scenes.EnumerateArray() : default)
            if (!AccumulateArray(scene, "nodes", MaxGlbNodes, ref references, MaxGlbAnyArrayElements)) return false;
        foreach (JsonElement node in nodes.ValueKind == JsonValueKind.Array ? nodes.EnumerateArray() : default)
            if (!AccumulateArray(node, "children", MaxGlbNodes, ref references, MaxGlbAnyArrayElements) || !BoundOptionalArray(node, "weights", 256) ||
                !BoundOptionalArray(node, "matrix", 16, exact: true) || !BoundOptionalArray(node, "translation", 3, exact: true) ||
                !BoundOptionalArray(node, "rotation", 4, exact: true) || !BoundOptionalArray(node, "scale", 3, exact: true)) return false;
        foreach (JsonElement mesh in meshes.EnumerateArray()) if (!BoundOptionalArray(mesh, "weights", 256)) return false;
        foreach (JsonElement animation in animations.ValueKind == JsonValueKind.Array ? animations.EnumerateArray() : default)
            if (!AccumulateArray(animation, "channels", 10_000, ref references, MaxGlbAnyArrayElements) || !AccumulateArray(animation, "samplers", 10_000, ref references, MaxGlbAnyArrayElements)) return false;
        foreach (JsonElement skin in skins.ValueKind == JsonValueKind.Array ? skins.EnumerateArray() : default)
            if (!AccumulateArray(skin, "joints", MaxGlbNodes, ref references, MaxGlbAnyArrayElements)) return false;
        return true;
    }

    private static bool AccumulateArray(JsonElement owner, string name, int perArrayMaximum, ref long aggregate, long aggregateMaximum)
    {
        if (owner.ValueKind != JsonValueKind.Object || !owner.TryGetProperty(name, out JsonElement array)) return owner.ValueKind == JsonValueKind.Object;
        if (array.ValueKind != JsonValueKind.Array || array.GetArrayLength() > perArrayMaximum) return false;
        aggregate = checked(aggregate + array.GetArrayLength());
        return aggregate <= aggregateMaximum;
    }

    private static bool BoundOptionalArray(JsonElement owner, string name, int maximum, bool exact = false) =>
        owner.ValueKind == JsonValueKind.Object && (!owner.TryGetProperty(name, out JsonElement array) ||
            (array.ValueKind == JsonValueKind.Array && (exact ? array.GetArrayLength() == maximum : array.GetArrayLength() <= maximum)));

    private static bool ValidateAccessorReferences(JsonElement attributes, int accessorCount)
    {
        foreach (JsonProperty attribute in attributes.EnumerateObject())
            if (!attribute.Value.TryGetInt32(out int index) || index < 0 || index >= accessorCount) return false;
        return true;
    }

    private static bool ValidateSparseAccessor(JsonElement sparse, long accessorCount, int elementBytes, int componentBytes, GlbBufferView[] views, ref long aggregateSparse)
    {
        if (sparse.ValueKind != JsonValueKind.Object || !TryGetRequiredNonNegativeInteger(sparse, "count", out long sparseCount) || sparseCount <= 0 || sparseCount > accessorCount ||
            !sparse.TryGetProperty("indices", out JsonElement indices) || indices.ValueKind != JsonValueKind.Object ||
            !sparse.TryGetProperty("values", out JsonElement values) || values.ValueKind != JsonValueKind.Object ||
            !TryGetRequiredInteger(indices, "componentType", out int indexComponent) || indexComponent is not (5121 or 5123 or 5125) ||
            ComponentByteSize(indexComponent) is not int indexBytes ||
            !TryGetRequiredView(indices, views, out GlbBufferView indexView) || indexView.Stride != 0 ||
            !TryGetOptionalNonNegativeInteger(indices, "byteOffset", 0, out long indexOffset) ||
            !TryGetRequiredView(values, views, out GlbBufferView valueView) || valueView.Stride != 0 ||
            !TryGetOptionalNonNegativeInteger(values, "byteOffset", 0, out long valueOffset) ||
            !ContiguousRangeFits(indexView, indexOffset, sparseCount, indexBytes, indexBytes) ||
            !ContiguousRangeFits(valueView, valueOffset, sparseCount, elementBytes, componentBytes)) return false;
        aggregateSparse = checked(aggregateSparse + sparseCount);
        return aggregateSparse <= MaxGlbAggregateAccessorElements;
    }

    private static bool TryGetRequiredView(JsonElement owner, GlbBufferView[] views, out GlbBufferView view)
    {
        view = default;
        if (!owner.TryGetProperty("bufferView", out JsonElement value) || !value.TryGetInt32(out int index) || index < 0 || index >= views.Length) return false;
        view = views[index];
        return true;
    }

    private static bool AccessorFits(GlbBufferView view, long offset, long count, int elementBytes, int componentBytes)
    {
        int stride = view.Stride == 0 ? elementBytes : view.Stride;
        return stride >= elementBytes && offset % componentBytes == 0 && (view.Offset + offset) % componentBytes == 0 &&
            RequiredRangeFits(view, offset, count, stride, elementBytes);
    }

    private static bool ContiguousRangeFits(GlbBufferView view, long offset, long count, int elementBytes, int alignment) =>
        offset % alignment == 0 && (view.Offset + offset) % alignment == 0 && RequiredRangeFits(view, offset, count, elementBytes, elementBytes);

    private static bool RequiredRangeFits(GlbBufferView view, long offset, long count, int stride, int elementBytes)
    {
        if (offset < 0 || count <= 0) return false;
        long required = checked((count - 1) * stride + elementBytes);
        return RangeFits(offset, required, view.Length);
    }

    private static bool RangeFits(long offset, long length, long containerLength) =>
        offset >= 0 && length >= 0 && offset <= containerLength && length <= containerLength - offset;

    private static int? ComponentByteSize(int componentType) => componentType switch
    {
        5120 or 5121 => 1,
        5122 or 5123 => 2,
        5125 or 5126 => 4,
        _ => null,
    };

    private static int? ElementByteSize(string type, int componentBytes)
    {
        int columns;
        int rows;
        switch (type)
        {
            case "SCALAR": columns = 1; rows = 1; break;
            case "VEC2": columns = 1; rows = 2; break;
            case "VEC3": columns = 1; rows = 3; break;
            case "VEC4": columns = 1; rows = 4; break;
            case "MAT2": columns = 2; rows = 2; break;
            case "MAT3": columns = 3; rows = 3; break;
            case "MAT4": columns = 4; rows = 4; break;
            default: return null;
        }
        int columnBytes = checked(rows * componentBytes);
        if (columns == 1) return columnBytes;
        int alignedColumnBytes = checked((columnBytes + 3) & ~3);
        return checked(columns * alignedColumnBytes);
    }

    private static int? ElementComponentCount(string type) => type switch
    {
        "SCALAR" => 1,
        "VEC2" => 2,
        "VEC3" => 3,
        "VEC4" or "MAT2" => 4,
        "MAT3" => 9,
        "MAT4" => 16,
        _ => null,
    };

    private static bool ValidateAccessorBoundsArray(JsonElement accessor, string name, int componentCount)
    {
        if (!accessor.TryGetProperty(name, out JsonElement values)) return true;
        if (values.ValueKind != JsonValueKind.Array || values.GetArrayLength() != componentCount) return false;
        foreach (JsonElement value in values.EnumerateArray())
            if (value.ValueKind != JsonValueKind.Number || !value.TryGetDouble(out double number) || !double.IsFinite(number)) return false;
        return true;
    }

    private static bool TryGetRequiredInteger(JsonElement owner, string name, out int result)
    {
        result = default;
        return owner.TryGetProperty(name, out JsonElement value) && value.ValueKind == JsonValueKind.Number && value.TryGetInt32(out result);
    }

    private static bool TryGetRequiredNonNegativeInteger(JsonElement owner, string name, out long result)
    {
        result = default;
        return owner.TryGetProperty(name, out JsonElement value) && value.ValueKind == JsonValueKind.Number && value.TryGetInt64(out result) && result >= 0;
    }

    private static bool TryGetOptionalNonNegativeInteger(JsonElement owner, string name, long defaultValue, out long result)
    {
        if (!owner.TryGetProperty(name, out JsonElement value)) { result = defaultValue; return true; }
        result = default;
        return value.ValueKind == JsonValueKind.Number && value.TryGetInt64(out result) && result >= 0;
    }

    private readonly record struct GlbBufferView(long Offset, long Length, int Stride);
    private readonly record struct GlbAccessor(long Count, int ComponentType, string Type);

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
