using System.IO.Compression;
using System.Text;

namespace Onslaught___Career_Editor
{
    public static class FbxModelSummaryReader
    {
        private const int MaxCapturedDoubleArrayValues = 1_000_000;
        private const int MaxCapturedIntArrayValues = 1_000_000;

        private static readonly byte[] BinaryFbxMagic =
        [
            (byte)'K', (byte)'a', (byte)'y', (byte)'d', (byte)'a', (byte)'r', (byte)'a', (byte)' ',
            (byte)'F', (byte)'B', (byte)'X', (byte)' ', (byte)'B', (byte)'i', (byte)'n', (byte)'a',
            (byte)'r', (byte)'y', (byte)' ', (byte)' ', 0x00, 0x1A, 0x00
        ];

        public static AssetModelSummary Read(string? path)
        {
            if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            {
                return AssetModelSummary.Unavailable(0, "FBX export is not available at the recorded local path.");
            }

            try
            {
                using FileStream stream = File.OpenRead(Path.GetFullPath(path));
                return Read(stream);
            }
            catch (Exception ex) when (ex is EndOfStreamException or IOException or InvalidDataException or ArgumentOutOfRangeException)
            {
                return AssetModelSummary.Unavailable(0, "FBX export exists, but model metadata could not be read.");
            }
        }

        public static AssetModelSummary Read(Stream stream)
        {
            ArgumentNullException.ThrowIfNull(stream);
            if (!stream.CanRead || !stream.CanSeek)
                throw new ArgumentException("FBX input stream must be readable and seekable.", nameof(stream));

            long byteSize = stream.Length;
            try
            {
                stream.Position = 0;
                using BinaryReader reader = new(stream, Encoding.ASCII, leaveOpen: true);

                if (stream.Length < BinaryFbxMagic.Length + sizeof(int))
                {
                    return AssetModelSummary.Unavailable(byteSize, "FBX export is too small to inspect.");
                }

                byte[] header = reader.ReadBytes(BinaryFbxMagic.Length);
                if (!header.SequenceEqual(BinaryFbxMagic))
                {
                    return AssetModelSummary.Unavailable(byteSize, "FBX export is not the binary FBX format used by the asset exporter.");
                }

                int version = reader.ReadInt32();
                FbxStats stats = new(byteSize, version);
                long sentinelSize = version >= 7500 ? 25 : 13;

                while (stream.Position <= stream.Length - sentinelSize)
                {
                    long before = stream.Position;
                    if (!ReadNode(reader, version, stats, parentName: string.Empty))
                    {
                        break;
                    }

                    if (stream.Position <= before)
                    {
                        break;
                    }
                }

                return new AssetModelSummary(
                    Format: "Binary FBX",
                    FormatVersion: version,
                    ByteSize: byteSize,
                    GeometryCount: stats.GeometryCount,
                    ModelCount: stats.ModelCount,
                    MaterialCount: stats.MaterialCount,
                    TextureBindingCount: stats.TextureBindingCount,
                    MaterialLayerCount: stats.MaterialLayerCount,
                    MaterialAssignmentIndexCount: stats.MaterialAssignmentIndexCount,
                    MaterialMappingModes: stats.MaterialMappingModes,
                    MaterialReferenceModes: stats.MaterialReferenceModes,
                    ObjectConnectionCount: stats.ObjectConnectionCount,
                    PropertyConnectionCount: stats.PropertyConnectionCount,
                    TextureToMaterialConnectionCount: stats.TextureToMaterialConnectionCount,
                    TextureToMaterialSlotNames: stats.TextureToMaterialSlotNames,
                    MaterialNames: stats.MaterialNames,
                    TextureBindingNames: stats.TextureBindingNames,
                    TextureBindingFileNames: stats.TextureBindingFileNames,
                    VertexCount: stats.VertexCount,
                    PolygonIndexCount: stats.PolygonIndexCount,
                    NormalCount: stats.NormalCount,
                    NormalIndexCount: stats.NormalIndexCount,
                    NormalMappingModes: stats.NormalMappingModes,
                    NormalReferenceModes: stats.NormalReferenceModes,
                    VertexColorCount: stats.VertexColorCount,
                    VertexColorIndexCount: stats.VertexColorIndexCount,
                    VertexColorMappingModes: stats.VertexColorMappingModes,
                    VertexColorReferenceModes: stats.VertexColorReferenceModes,
                    TextureCoordinateCount: stats.TextureCoordinateCount,
                    TextureCoordinateIndexCount: stats.TextureCoordinateIndexCount,
                    TextureCoordinateMappingModes: stats.TextureCoordinateMappingModes,
                    TextureCoordinateReferenceModes: stats.TextureCoordinateReferenceModes,
                    GeometryPreview: stats.BuildGeometryPreview(),
                    MeshPayload: stats.BuildMeshPayload(),
                    MetadataAvailable: true,
                    Status: stats.GeometryCount > 0
                        ? "Model metadata read from the local FBX export."
                        : "Binary FBX metadata was readable, but no geometry nodes were found.");
            }
            catch (Exception ex) when (ex is EndOfStreamException or IOException or InvalidDataException or ArgumentOutOfRangeException)
            {
                return AssetModelSummary.Unavailable(byteSize, "FBX export exists, but model metadata could not be read.");
            }
        }

        private static bool ReadNode(BinaryReader reader, int version, FbxStats stats, string parentName)
        {
            Stream stream = reader.BaseStream;
            long nodeStart = stream.Position;
            long endOffset = ReadOffset(reader, version);
            long propertyCount = ReadOffset(reader, version);
            _ = ReadOffset(reader, version);
            int nameLength = reader.ReadByte();

            if (endOffset == 0 && propertyCount == 0 && nameLength == 0)
            {
                return false;
            }

            if (endOffset <= nodeStart || endOffset > stream.Length || nameLength > 256)
            {
                throw new InvalidDataException("Invalid FBX node boundary.");
            }

            string name = Encoding.ASCII.GetString(reader.ReadBytes(nameLength));
            long? firstArrayLength = null;
            double[]? doubleArray = null;
            int[]? intArray = null;
            bool arrayTruncated = false;
            List<string> stringValues = [];
            List<long> longValues = [];
            for (long index = 0; index < propertyCount; index++)
            {
                FbxProperty property = ReadProperty(reader, name);
                firstArrayLength ??= property.ArrayLength;
                doubleArray ??= property.DoubleArray;
                intArray ??= property.IntArray;
                arrayTruncated |= property.ArrayTruncated;
                if (property.LongValue is long longValue)
                {
                    longValues.Add(longValue);
                }

                if (!string.IsNullOrWhiteSpace(property.StringValue))
                {
                    stringValues.Add(property.StringValue);
                }
            }

            stats.RecordNode(parentName, name, firstArrayLength, doubleArray, intArray, arrayTruncated, stringValues, longValues);

            long sentinelSize = version >= 7500 ? 25 : 13;
            while (stream.Position < endOffset - sentinelSize)
            {
                long before = stream.Position;
                if (!ReadNode(reader, version, stats, name))
                {
                    break;
                }

                if (stream.Position <= before)
                {
                    break;
                }
            }

            stream.Position = endOffset;
            return true;
        }

        private static long ReadOffset(BinaryReader reader, int version)
        {
            return version >= 7500 ? reader.ReadInt64() : reader.ReadUInt32();
        }

        private static FbxProperty ReadProperty(BinaryReader reader, string nodeName)
        {
            char type = (char)reader.ReadByte();
            switch (type)
            {
                case 'Y':
                    Skip(reader, sizeof(short));
                    return FbxProperty.Empty;
                case 'C':
                    Skip(reader, sizeof(byte));
                    return FbxProperty.Empty;
                case 'I':
                    Skip(reader, sizeof(int));
                    return FbxProperty.Empty;
                case 'F':
                    Skip(reader, sizeof(float));
                    return FbxProperty.Empty;
                case 'D':
                    Skip(reader, sizeof(double));
                    return FbxProperty.Empty;
                case 'L':
                    return new FbxProperty(null, null, null, null, reader.ReadInt64(), false);
                case 'S':
                    uint stringLength = reader.ReadUInt32();
                    byte[] stringBytes = reader.ReadBytes(checked((int)stringLength));
                    if (stringBytes.Length != stringLength)
                    {
                        throw new InvalidDataException("Invalid FBX string property length.");
                    }

                    return new FbxProperty(null, null, null, Encoding.UTF8.GetString(stringBytes), null, false);
                case 'R':
                    Skip(reader, checked((int)reader.ReadUInt32()));
                    return FbxProperty.Empty;
                case 'f':
                case 'd':
                case 'l':
                case 'i':
                case 'b':
                    uint arrayLength = reader.ReadUInt32();
                    uint encoding = reader.ReadUInt32();
                    uint payloadLength = reader.ReadUInt32();
                    if (ShouldCaptureDoubleArray(nodeName, type))
                    {
                        return type == 'f'
                            ? ReadFloatArrayProperty(reader, arrayLength, encoding, payloadLength)
                            : ReadDoubleArrayProperty(reader, arrayLength, encoding, payloadLength);
                    }

                    if (ShouldCaptureIntArray(nodeName, type))
                    {
                        return ReadIntArrayProperty(reader, arrayLength, encoding, payloadLength);
                    }

                    Skip(reader, checked((int)payloadLength));
                    return new FbxProperty(arrayLength, null, null, null, null, false);
                default:
                    throw new InvalidDataException($"Unsupported FBX property type '{type}'.");
            }
        }

        private static bool ShouldCaptureDoubleArray(string nodeName, char type)
        {
            return (type == 'd' || type == 'f') &&
                   nodeName is "Vertices" or "Normals" or "UV" or "Colors";
        }

        private static bool ShouldCaptureIntArray(string nodeName, char type)
        {
            return type == 'i' &&
                   nodeName is "PolygonVertexIndex" or "NormalsIndex" or "UVIndex" or "ColorIndex" or "Materials";
        }

        private static FbxProperty ReadDoubleArrayProperty(BinaryReader reader, uint arrayLength, uint encoding, uint payloadLength)
        {
            int valuesToRead = checked((int)Math.Min(arrayLength, MaxCapturedDoubleArrayValues));
            bool truncated = arrayLength > MaxCapturedDoubleArrayValues;
            if (encoding == 1)
            {
                return ReadCompressedArrayProperty(
                    reader,
                    arrayLength,
                    payloadLength,
                    innerReader => ReadDoubleArrayValues(innerReader, valuesToRead),
                    doubleArray => new FbxProperty(arrayLength, doubleArray, null, null, null, truncated));
            }

            if (encoding != 0)
            {
                Skip(reader, checked((int)payloadLength));
                return new FbxProperty(arrayLength, null, null, null, null, truncated);
            }

            int valueByteCount = sizeof(double);
            long bytesToRead = (long)valuesToRead * valueByteCount;
            if (payloadLength < bytesToRead)
            {
                Skip(reader, checked((int)payloadLength));
                return new FbxProperty(arrayLength, null, null, null, null, truncated);
            }

            double[] values = ReadDoubleArrayValues(reader, valuesToRead);
            Skip(reader, checked((int)(payloadLength - bytesToRead)));
            return new FbxProperty(arrayLength, values, null, null, null, truncated);
        }

        private static FbxProperty ReadFloatArrayProperty(BinaryReader reader, uint arrayLength, uint encoding, uint payloadLength)
        {
            int valuesToRead = checked((int)Math.Min(arrayLength, MaxCapturedDoubleArrayValues));
            bool truncated = arrayLength > MaxCapturedDoubleArrayValues;
            if (encoding == 1)
            {
                return ReadCompressedArrayProperty(
                    reader,
                    arrayLength,
                    payloadLength,
                    innerReader => ReadFloatArrayValues(innerReader, valuesToRead),
                    doubleArray => new FbxProperty(arrayLength, doubleArray, null, null, null, truncated));
            }

            if (encoding != 0)
            {
                Skip(reader, checked((int)payloadLength));
                return new FbxProperty(arrayLength, null, null, null, null, truncated);
            }

            int valueByteCount = sizeof(float);
            long bytesToRead = (long)valuesToRead * valueByteCount;
            if (payloadLength < bytesToRead)
            {
                Skip(reader, checked((int)payloadLength));
                return new FbxProperty(arrayLength, null, null, null, null, truncated);
            }

            double[] values = ReadFloatArrayValues(reader, valuesToRead);
            Skip(reader, checked((int)(payloadLength - bytesToRead)));
            return new FbxProperty(arrayLength, values, null, null, null, truncated);
        }

        private static FbxProperty ReadIntArrayProperty(BinaryReader reader, uint arrayLength, uint encoding, uint payloadLength)
        {
            int valuesToRead = checked((int)Math.Min(arrayLength, MaxCapturedIntArrayValues));
            bool truncated = arrayLength > MaxCapturedIntArrayValues;
            if (encoding == 1)
            {
                return ReadCompressedArrayProperty(
                    reader,
                    arrayLength,
                    payloadLength,
                    innerReader => ReadIntArrayValues(innerReader, valuesToRead),
                    intArray => new FbxProperty(arrayLength, null, intArray, null, null, truncated));
            }

            if (encoding != 0)
            {
                Skip(reader, checked((int)payloadLength));
                return new FbxProperty(arrayLength, null, null, null, null, truncated);
            }

            int valueByteCount = sizeof(int);
            long bytesToRead = (long)valuesToRead * valueByteCount;
            if (payloadLength < bytesToRead)
            {
                Skip(reader, checked((int)payloadLength));
                return new FbxProperty(arrayLength, null, null, null, null, truncated);
            }

            int[] values = ReadIntArrayValues(reader, valuesToRead);
            Skip(reader, checked((int)(payloadLength - bytesToRead)));
            return new FbxProperty(arrayLength, null, values, null, null, truncated);
        }

        private static FbxProperty ReadCompressedArrayProperty<T>(
            BinaryReader reader,
            uint arrayLength,
            uint payloadLength,
            Func<BinaryReader, T> readValues,
            Func<T, FbxProperty> buildProperty)
        {
            const int maxCompressedPayloadBytes = 64 * 1024 * 1024;
            if (payloadLength > maxCompressedPayloadBytes)
            {
                Skip(reader, checked((int)payloadLength));
                return new FbxProperty(arrayLength, null, null, null, null, true);
            }

            byte[] compressed = reader.ReadBytes(checked((int)payloadLength));
            if (compressed.Length != payloadLength)
            {
                return new FbxProperty(arrayLength, null, null, null, null, false);
            }

            try
            {
                using MemoryStream compressedStream = new(compressed);
                using ZLibStream zlibStream = new(compressedStream, CompressionMode.Decompress);
                using BinaryReader decompressedReader = new(zlibStream, Encoding.ASCII, leaveOpen: false);
                return buildProperty(readValues(decompressedReader));
            }
            catch (InvalidDataException)
            {
                return new FbxProperty(arrayLength, null, null, null, null, false);
            }
            catch (EndOfStreamException)
            {
                return new FbxProperty(arrayLength, null, null, null, null, false);
            }
        }

        private static double[] ReadDoubleArrayValues(BinaryReader reader, int valueCount)
        {
            double[] values = new double[valueCount];
            for (int index = 0; index < values.Length; index++)
            {
                values[index] = reader.ReadDouble();
            }

            return values;
        }

        private static double[] ReadFloatArrayValues(BinaryReader reader, int valueCount)
        {
            double[] values = new double[valueCount];
            for (int index = 0; index < values.Length; index++)
            {
                values[index] = reader.ReadSingle();
            }

            return values;
        }

        private static int[] ReadIntArrayValues(BinaryReader reader, int valueCount)
        {
            int[] values = new int[valueCount];
            for (int index = 0; index < values.Length; index++)
            {
                values[index] = reader.ReadInt32();
            }

            return values;
        }

        private static void Skip(BinaryReader reader, int byteCount)
        {
            Stream stream = reader.BaseStream;
            long next = stream.Position + byteCount;
            if (byteCount < 0 || next > stream.Length)
            {
                throw new InvalidDataException("Invalid FBX property length.");
            }

            stream.Position = next;
        }

        private sealed record FbxProperty(
            long? ArrayLength,
            double[]? DoubleArray,
            int[]? IntArray,
            string? StringValue,
            long? LongValue,
            bool ArrayTruncated)
        {
            public static FbxProperty Empty { get; } = new(null, null, null, null, null, false);
        }

        private sealed class FbxStats(long byteSize, int version)
        {
            private List<AssetModelPreviewVertex> _previewVertices = [];
            private List<int> _previewPolygonIndices = [];
            private List<AssetModelPreviewVertex> _meshVertices = [];
            private List<int> _meshPolygonIndices = [];
            private List<AssetModelPreviewVertex> _meshNormals = [];
            private List<int> _meshNormalIndices = [];
            private List<AssetModelTextureCoordinate> _meshTextureCoordinates = [];
            private List<int> _meshTextureCoordinateIndices = [];
            private List<int> _meshMaterialAssignmentIndices = [];
            private bool _verticesTruncated;
            private bool _polygonIndicesTruncated;
            private bool _normalsTruncated;
            private bool _normalIndicesTruncated;
            private bool _textureCoordinatesTruncated;
            private bool _textureCoordinateIndicesTruncated;
            private bool _materialAssignmentsTruncated;
            private readonly SortedSet<string> _materialNames = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _materialMappingModes = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _materialReferenceModes = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _normalMappingModes = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _normalReferenceModes = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _vertexColorMappingModes = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _vertexColorReferenceModes = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _textureCoordinateMappingModes = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _textureCoordinateReferenceModes = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _textureBindingNames = new(StringComparer.OrdinalIgnoreCase);
            private readonly SortedSet<string> _textureBindingFileNames = new(StringComparer.OrdinalIgnoreCase);
            private readonly Dictionary<long, string> _objectKindById = new();
            private readonly List<FbxConnection> _connections = [];

            public long ByteSize { get; } = byteSize;
            public int Version { get; } = version;
            public int GeometryCount { get; private set; }
            public int ModelCount { get; private set; }
            public int MaterialCount { get; private set; }
            public int TextureBindingCount { get; private set; }
            public int MaterialLayerCount { get; private set; }
            public int MaterialAssignmentIndexCount { get; private set; }
            public int VertexCount { get; private set; }
            public int PolygonIndexCount { get; private set; }
            public int NormalCount { get; private set; }
            public int NormalIndexCount { get; private set; }
            public IReadOnlyList<string> NormalMappingModes => _normalMappingModes.ToList();
            public IReadOnlyList<string> NormalReferenceModes => _normalReferenceModes.ToList();
            public int VertexColorCount { get; private set; }
            public int VertexColorIndexCount { get; private set; }
            public IReadOnlyList<string> VertexColorMappingModes => _vertexColorMappingModes.ToList();
            public IReadOnlyList<string> VertexColorReferenceModes => _vertexColorReferenceModes.ToList();
            public int TextureCoordinateCount { get; private set; }
            public int TextureCoordinateIndexCount { get; private set; }
            public IReadOnlyList<string> TextureCoordinateMappingModes => _textureCoordinateMappingModes.ToList();
            public IReadOnlyList<string> TextureCoordinateReferenceModes => _textureCoordinateReferenceModes.ToList();
            public IReadOnlyList<string> MaterialMappingModes => _materialMappingModes.ToList();
            public IReadOnlyList<string> MaterialReferenceModes => _materialReferenceModes.ToList();
            public int ObjectConnectionCount => _connections.Count(static connection => connection.Kind == "OO");
            public int PropertyConnectionCount => _connections.Count(static connection => connection.Kind == "OP");
            public int TextureToMaterialConnectionCount =>
                _connections.Count(connection =>
                    connection.Kind == "OP" &&
                    _objectKindById.TryGetValue(connection.SourceId, out string? sourceKind) &&
                    _objectKindById.TryGetValue(connection.DestinationId, out string? destinationKind) &&
                    sourceKind == "Texture" &&
                    destinationKind == "Material");
            public IReadOnlyList<string> TextureToMaterialSlotNames => _connections
                .Where(connection =>
                    connection.Kind == "OP" &&
                    !string.IsNullOrWhiteSpace(connection.SlotName) &&
                    _objectKindById.TryGetValue(connection.SourceId, out string? sourceKind) &&
                    _objectKindById.TryGetValue(connection.DestinationId, out string? destinationKind) &&
                    sourceKind == "Texture" &&
                    destinationKind == "Material")
                .Select(static connection => connection.SlotName)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static value => value, StringComparer.OrdinalIgnoreCase)
                .ToList();
            public IReadOnlyList<string> MaterialNames => _materialNames.ToList();
            public IReadOnlyList<string> TextureBindingNames => _textureBindingNames.ToList();
            public IReadOnlyList<string> TextureBindingFileNames => _textureBindingFileNames.ToList();

            public void RecordNode(
                string parentName,
                string name,
                long? firstArrayLength,
                double[]? doubleArray,
                int[]? intArray,
                bool arrayTruncated,
                IReadOnlyList<string> stringValues,
                IReadOnlyList<long> longValues)
            {
                AddTextureFileNames(stringValues);

                switch (name)
                {
                    case "Geometry":
                        GeometryCount++;
                        break;
                    case "Model":
                        ModelCount++;
                        break;
                    case "Material":
                        MaterialCount++;
                        AddObjectKind("Material", longValues);
                        AddFbxObjectName(_materialNames, stringValues);
                        break;
                    case "Texture":
                        TextureBindingCount++;
                        AddObjectKind("Texture", longValues);
                        AddFbxObjectName(_textureBindingNames, stringValues);
                        break;
                    case "C":
                        AddConnection(stringValues, longValues);
                        break;
                    case "LayerElementMaterial":
                        MaterialLayerCount++;
                        break;
                    case "MappingInformationType" when parentName == "LayerElementNormal":
                        AddFirstString(_normalMappingModes, stringValues);
                        break;
                    case "ReferenceInformationType" when parentName == "LayerElementNormal":
                        AddFirstString(_normalReferenceModes, stringValues);
                        break;
                    case "MappingInformationType" when parentName == "LayerElementColor":
                        AddFirstString(_vertexColorMappingModes, stringValues);
                        break;
                    case "ReferenceInformationType" when parentName == "LayerElementColor":
                        AddFirstString(_vertexColorReferenceModes, stringValues);
                        break;
                    case "MappingInformationType" when parentName == "LayerElementUV":
                        AddFirstString(_textureCoordinateMappingModes, stringValues);
                        break;
                    case "ReferenceInformationType" when parentName == "LayerElementUV":
                        AddFirstString(_textureCoordinateReferenceModes, stringValues);
                        break;
                    case "MappingInformationType" when parentName == "LayerElementMaterial":
                        AddFirstString(_materialMappingModes, stringValues);
                        break;
                    case "ReferenceInformationType" when parentName == "LayerElementMaterial":
                        AddFirstString(_materialReferenceModes, stringValues);
                        break;
                    case "Vertices" when firstArrayLength is long vertexCoordinates:
                        VertexCount += checked((int)(vertexCoordinates / 3));
                        if (_previewVertices.Count == 0 && doubleArray != null)
                        {
                            _previewVertices = BuildPreviewVertices(doubleArray);
                            _meshVertices = _previewVertices;
                            _verticesTruncated = arrayTruncated;
                        }

                        break;
                    case "PolygonVertexIndex" when firstArrayLength is long indexCount:
                        PolygonIndexCount += checked((int)indexCount);
                        if (_previewPolygonIndices.Count == 0 && intArray != null)
                        {
                            _previewPolygonIndices = intArray.ToList();
                            _meshPolygonIndices = _previewPolygonIndices;
                            _polygonIndicesTruncated = arrayTruncated;
                        }

                        break;
                    case "Normals" when firstArrayLength is long normalValues:
                        NormalCount += checked((int)(normalValues / 3));
                        if (_meshNormals.Count == 0 && doubleArray != null)
                        {
                            _meshNormals = BuildPreviewVertices(doubleArray);
                            _normalsTruncated = arrayTruncated;
                        }

                        break;
                    case "NormalsIndex" when firstArrayLength is long normalIndexCount:
                        NormalIndexCount += checked((int)normalIndexCount);
                        if (_meshNormalIndices.Count == 0 && intArray != null)
                        {
                            _meshNormalIndices = intArray.ToList();
                            _normalIndicesTruncated = arrayTruncated;
                        }

                        break;
                    case "Colors" when firstArrayLength is long colorValues:
                        VertexColorCount += checked((int)(colorValues / 4));
                        break;
                    case "ColorIndex" when firstArrayLength is long colorIndexCount:
                        VertexColorIndexCount += checked((int)colorIndexCount);
                        break;
                    case "UV" when firstArrayLength is long textureCoordinateValues:
                        TextureCoordinateCount += checked((int)(textureCoordinateValues / 2));
                        if (_meshTextureCoordinates.Count == 0 && doubleArray != null)
                        {
                            _meshTextureCoordinates = BuildTextureCoordinates(doubleArray);
                            _textureCoordinatesTruncated = arrayTruncated;
                        }

                        break;
                    case "UVIndex" when firstArrayLength is long textureCoordinateIndexCount:
                        TextureCoordinateIndexCount += checked((int)textureCoordinateIndexCount);
                        if (_meshTextureCoordinateIndices.Count == 0 && intArray != null)
                        {
                            _meshTextureCoordinateIndices = intArray.ToList();
                            _textureCoordinateIndicesTruncated = arrayTruncated;
                        }

                        break;
                    case "Materials" when firstArrayLength is long materialAssignmentIndexCount:
                        MaterialAssignmentIndexCount += checked((int)materialAssignmentIndexCount);
                        if (_meshMaterialAssignmentIndices.Count == 0 && intArray != null)
                        {
                            _meshMaterialAssignmentIndices = intArray.ToList();
                            _materialAssignmentsTruncated = arrayTruncated;
                        }

                        break;
                }
            }

            private void AddObjectKind(string kind, IReadOnlyList<long> longValues)
            {
                if (longValues.Count > 0)
                {
                    _objectKindById[longValues[0]] = kind;
                }
            }

            private void AddConnection(IReadOnlyList<string> stringValues, IReadOnlyList<long> longValues)
            {
                if (stringValues.Count == 0 || longValues.Count < 2)
                {
                    return;
                }

                string kind = stringValues[0].Trim();
                if (kind is "OO" or "OP")
                {
                    string slotName = kind == "OP" && stringValues.Count > 1
                        ? stringValues[1].Trim()
                        : string.Empty;
                    _connections.Add(new FbxConnection(kind, longValues[0], longValues[1], slotName));
                }
            }

            private static void AddFbxObjectName(SortedSet<string> target, IReadOnlyList<string> stringValues)
            {
                if (stringValues.Count == 0)
                {
                    return;
                }

                string name = stringValues[0];
                int nullIndex = name.IndexOf('\0');
                if (nullIndex >= 0)
                {
                    name = name[..nullIndex];
                }

                name = name.Trim();
                if (!string.IsNullOrWhiteSpace(name))
                {
                    target.Add(name);
                }
            }

            private static void AddFirstString(SortedSet<string> target, IReadOnlyList<string> stringValues)
            {
                if (stringValues.Count == 0)
                {
                    return;
                }

                string value = stringValues[0].Trim();
                if (!string.IsNullOrWhiteSpace(value))
                {
                    target.Add(value);
                }
            }

            private void AddTextureFileNames(IReadOnlyList<string> stringValues)
            {
                foreach (string value in stringValues)
                {
                    string fileName = ExtractTextureFileName(value);
                    if (!string.IsNullOrWhiteSpace(fileName))
                    {
                        _textureBindingFileNames.Add(fileName);
                    }
                }
            }

            private static string ExtractTextureFileName(string value)
            {
                if (string.IsNullOrWhiteSpace(value))
                {
                    return string.Empty;
                }

                string normalized = value
                    .Replace('\\', Path.DirectorySeparatorChar)
                    .Replace('/', Path.DirectorySeparatorChar)
                    .Trim();
                string fileName = Path.GetFileName(normalized);
                if (!LooksLikeTextureFileName(fileName))
                {
                    return string.Empty;
                }

                return fileName;
            }

            private static bool LooksLikeTextureFileName(string value)
            {
                return value.EndsWith(".png", StringComparison.OrdinalIgnoreCase)
                    || value.EndsWith(".tga", StringComparison.OrdinalIgnoreCase)
                    || value.EndsWith(".dds", StringComparison.OrdinalIgnoreCase)
                    || value.EndsWith(".bmp", StringComparison.OrdinalIgnoreCase)
                    || value.EndsWith(".jpg", StringComparison.OrdinalIgnoreCase)
                    || value.EndsWith(".jpeg", StringComparison.OrdinalIgnoreCase);
            }

            public AssetModelGeometryPreview BuildGeometryPreview()
            {
                if (_previewVertices.Count == 0 || _previewPolygonIndices.Count == 0)
                {
                    return AssetModelGeometryPreview.Empty;
                }

                List<AssetModelPreviewEdge> edges = [];
                List<int> polygon = [];
                HashSet<(int Start, int End)> seenEdges = [];
                foreach (int rawIndex in _previewPolygonIndices)
                {
                    int index = rawIndex < 0 ? -rawIndex - 1 : rawIndex;
                    if (index >= 0 && index < _previewVertices.Count)
                    {
                        polygon.Add(index);
                    }

                    if (rawIndex < 0)
                    {
                        AddPolygonEdges(polygon, edges, seenEdges);
                        polygon.Clear();
                    }
                }

                AddPolygonEdges(polygon, edges, seenEdges);
                return edges.Count == 0
                    ? AssetModelGeometryPreview.Empty
                    : new AssetModelGeometryPreview(_previewVertices, edges);
            }

            public AssetModelMeshPayload BuildMeshPayload()
            {
                if (_meshVertices.Count == 0 || _meshPolygonIndices.Count == 0)
                {
                    return AssetModelMeshPayload.Empty with { Status = "mesh-payload-unavailable" };
                }

                List<AssetModelMeshFace> faces = BuildFaces(_meshPolygonIndices, _meshVertices.Count);
                bool baseComplete = faces.Count > 0 &&
                                    !_verticesTruncated &&
                                    !_polygonIndicesTruncated &&
                                    VertexCount == _meshVertices.Count &&
                                    PolygonIndexCount == _meshPolygonIndices.Count;
                bool secondaryComplete =
                    (!_normalsTruncated && (NormalCount == 0 || NormalCount == _meshNormals.Count)) &&
                    (!_normalIndicesTruncated && (NormalIndexCount == 0 || NormalIndexCount == _meshNormalIndices.Count)) &&
                    (!_textureCoordinatesTruncated && (TextureCoordinateCount == 0 || TextureCoordinateCount == _meshTextureCoordinates.Count)) &&
                    (!_textureCoordinateIndicesTruncated && (TextureCoordinateIndexCount == 0 || TextureCoordinateIndexCount == _meshTextureCoordinateIndices.Count)) &&
                    (!_materialAssignmentsTruncated && (MaterialAssignmentIndexCount == 0 || MaterialAssignmentIndexCount == _meshMaterialAssignmentIndices.Count));
                bool coversSingleGeometry = GeometryCount <= 1;
                bool complete = baseComplete && secondaryComplete && coversSingleGeometry;
                string status = complete
                    ? "complete-mesh-payload"
                    : baseComplete
                        ? "partial-mesh-payload"
                        : "incomplete-mesh-payload";

                return new AssetModelMeshPayload(
                    Vertices: _meshVertices,
                    Faces: ApplyMaterialAssignments(faces),
                    Normals: _meshNormals,
                    NormalIndices: _meshNormalIndices,
                    TextureCoordinates: _meshTextureCoordinates,
                    TextureCoordinateIndices: _meshTextureCoordinateIndices,
                    MaterialAssignmentIndices: _meshMaterialAssignmentIndices,
                    CoversSingleGeometry: coversSingleGeometry,
                    BaseGeometryComplete: baseComplete,
                    SecondaryGeometryComplete: secondaryComplete,
                    Complete: complete,
                    Status: status);
            }

            private static List<AssetModelPreviewVertex> BuildPreviewVertices(double[] coordinates)
            {
                List<AssetModelPreviewVertex> vertices = [];
                int coordinateCount = coordinates.Length - (coordinates.Length % 3);
                for (int index = 0; index < coordinateCount; index += 3)
                {
                    vertices.Add(new AssetModelPreviewVertex(coordinates[index], coordinates[index + 1], coordinates[index + 2]));
                }

                return vertices;
            }

            private static List<AssetModelTextureCoordinate> BuildTextureCoordinates(double[] coordinates)
            {
                List<AssetModelTextureCoordinate> textureCoordinates = [];
                int coordinateCount = coordinates.Length - (coordinates.Length % 2);
                for (int index = 0; index < coordinateCount; index += 2)
                {
                    textureCoordinates.Add(new AssetModelTextureCoordinate(coordinates[index], coordinates[index + 1]));
                }

                return textureCoordinates;
            }

            private static void AddPolygonEdges(
                IReadOnlyList<int> polygon,
                List<AssetModelPreviewEdge> edges,
                HashSet<(int Start, int End)> seenEdges)
            {
                if (polygon.Count < 2)
                {
                    return;
                }

                for (int index = 0; index < polygon.Count; index++)
                {
                    int start = polygon[index];
                    int end = polygon[(index + 1) % polygon.Count];
                    if (start == end)
                    {
                        continue;
                    }

                    (int Start, int End) key = start < end ? (start, end) : (end, start);
                    if (seenEdges.Add(key))
                    {
                        edges.Add(new AssetModelPreviewEdge(start, end));
                    }
                }
            }

            private static List<AssetModelMeshFace> BuildFaces(IReadOnlyList<int> polygonIndices, int vertexCount)
            {
                List<AssetModelMeshFace> faces = [];
                List<int> polygon = [];
                List<int> polygonVertexOrdinals = [];
                for (int ordinal = 0; ordinal < polygonIndices.Count; ordinal++)
                {
                    int rawIndex = polygonIndices[ordinal];
                    int index = rawIndex < 0 ? -rawIndex - 1 : rawIndex;
                    if (index >= 0 && index < vertexCount)
                    {
                        polygon.Add(index);
                        polygonVertexOrdinals.Add(ordinal);
                    }

                    if (rawIndex < 0)
                    {
                        AddFace(polygon, polygonVertexOrdinals, faces);
                        polygon.Clear();
                        polygonVertexOrdinals.Clear();
                    }
                }

                AddFace(polygon, polygonVertexOrdinals, faces);
                return faces;
            }

            private static void AddFace(
                IReadOnlyList<int> polygon,
                IReadOnlyList<int> polygonVertexOrdinals,
                List<AssetModelMeshFace> faces)
            {
                if (polygon.Count >= 3)
                {
                    faces.Add(new AssetModelMeshFace(polygon.ToArray(), polygonVertexOrdinals.ToArray(), MaterialIndex: null));
                }
            }

            private IReadOnlyList<AssetModelMeshFace> ApplyMaterialAssignments(IReadOnlyList<AssetModelMeshFace> faces)
            {
                if (_meshMaterialAssignmentIndices.Count == 0 || faces.Count == 0)
                {
                    return faces;
                }

                if (_materialMappingModes.Contains("AllSame") && _meshMaterialAssignmentIndices.Count > 0)
                {
                    int materialIndex = _meshMaterialAssignmentIndices[0];
                    return faces
                        .Select(face => face with { MaterialIndex = materialIndex })
                        .ToList();
                }

                if (_materialMappingModes.Contains("ByPolygon") && _meshMaterialAssignmentIndices.Count >= faces.Count)
                {
                    return faces
                        .Select((face, index) => face with { MaterialIndex = _meshMaterialAssignmentIndices[index] })
                        .ToList();
                }

                return faces;
            }
        }

        private sealed record FbxConnection(string Kind, long SourceId, long DestinationId, string SlotName);
    }

    public sealed record AssetModelSummary(
        string Format,
        int? FormatVersion,
        long ByteSize,
        int GeometryCount,
        int ModelCount,
        int MaterialCount,
        int TextureBindingCount,
        int MaterialLayerCount,
        int MaterialAssignmentIndexCount,
        IReadOnlyList<string> MaterialMappingModes,
        IReadOnlyList<string> MaterialReferenceModes,
        int ObjectConnectionCount,
        int PropertyConnectionCount,
        int TextureToMaterialConnectionCount,
        IReadOnlyList<string> TextureToMaterialSlotNames,
        IReadOnlyList<string> MaterialNames,
        IReadOnlyList<string> TextureBindingNames,
        IReadOnlyList<string> TextureBindingFileNames,
        int VertexCount,
        int PolygonIndexCount,
        int NormalCount,
        int NormalIndexCount,
        IReadOnlyList<string> NormalMappingModes,
        IReadOnlyList<string> NormalReferenceModes,
        int VertexColorCount,
        int VertexColorIndexCount,
        IReadOnlyList<string> VertexColorMappingModes,
        IReadOnlyList<string> VertexColorReferenceModes,
        int TextureCoordinateCount,
        int TextureCoordinateIndexCount,
        IReadOnlyList<string> TextureCoordinateMappingModes,
        IReadOnlyList<string> TextureCoordinateReferenceModes,
        AssetModelGeometryPreview GeometryPreview,
        AssetModelMeshPayload MeshPayload,
        bool MetadataAvailable,
        string Status)
    {
        public static AssetModelSummary Unavailable(long byteSize, string status)
        {
            return new AssetModelSummary(
                Format: "FBX",
                FormatVersion: null,
                ByteSize: byteSize,
                GeometryCount: 0,
                ModelCount: 0,
                MaterialCount: 0,
                TextureBindingCount: 0,
                MaterialLayerCount: 0,
                MaterialAssignmentIndexCount: 0,
                MaterialMappingModes: Array.Empty<string>(),
                MaterialReferenceModes: Array.Empty<string>(),
                ObjectConnectionCount: 0,
                PropertyConnectionCount: 0,
                TextureToMaterialConnectionCount: 0,
                TextureToMaterialSlotNames: Array.Empty<string>(),
                MaterialNames: Array.Empty<string>(),
                TextureBindingNames: Array.Empty<string>(),
                TextureBindingFileNames: Array.Empty<string>(),
                VertexCount: 0,
                PolygonIndexCount: 0,
                NormalCount: 0,
                NormalIndexCount: 0,
                NormalMappingModes: Array.Empty<string>(),
                NormalReferenceModes: Array.Empty<string>(),
                VertexColorCount: 0,
                VertexColorIndexCount: 0,
                VertexColorMappingModes: Array.Empty<string>(),
                VertexColorReferenceModes: Array.Empty<string>(),
                TextureCoordinateCount: 0,
                TextureCoordinateIndexCount: 0,
                TextureCoordinateMappingModes: Array.Empty<string>(),
                TextureCoordinateReferenceModes: Array.Empty<string>(),
                GeometryPreview: AssetModelGeometryPreview.Empty,
                MeshPayload: AssetModelMeshPayload.Empty,
                MetadataAvailable: false,
                Status: status);
        }
    }

    public sealed record AssetModelGeometryPreview(
        IReadOnlyList<AssetModelPreviewVertex> Vertices,
        IReadOnlyList<AssetModelPreviewEdge> Edges)
    {
        public static AssetModelGeometryPreview Empty { get; } = new(
            Array.Empty<AssetModelPreviewVertex>(),
            Array.Empty<AssetModelPreviewEdge>());

        public bool Available => Vertices.Count > 0 && Edges.Count > 0;
    }

    public sealed record AssetModelPreviewVertex(double X, double Y, double Z);

    public sealed record AssetModelPreviewEdge(int StartIndex, int EndIndex);

    public sealed record AssetModelMeshPayload(
        IReadOnlyList<AssetModelPreviewVertex> Vertices,
        IReadOnlyList<AssetModelMeshFace> Faces,
        IReadOnlyList<AssetModelPreviewVertex> Normals,
        IReadOnlyList<int> NormalIndices,
        IReadOnlyList<AssetModelTextureCoordinate> TextureCoordinates,
        IReadOnlyList<int> TextureCoordinateIndices,
        IReadOnlyList<int> MaterialAssignmentIndices,
        bool CoversSingleGeometry,
        bool BaseGeometryComplete,
        bool SecondaryGeometryComplete,
        bool Complete,
        string Status)
    {
        public static AssetModelMeshPayload Empty { get; } = new(
            Array.Empty<AssetModelPreviewVertex>(),
            Array.Empty<AssetModelMeshFace>(),
            Array.Empty<AssetModelPreviewVertex>(),
            Array.Empty<int>(),
            Array.Empty<AssetModelTextureCoordinate>(),
            Array.Empty<int>(),
            Array.Empty<int>(),
            CoversSingleGeometry: false,
            BaseGeometryComplete: false,
            SecondaryGeometryComplete: false,
            Complete: false,
            Status: "mesh-payload-unavailable");

        public bool Available => Vertices.Count > 0 && Faces.Count > 0;
    }

    public sealed record AssetModelMeshFace(
        IReadOnlyList<int> VertexIndices,
        IReadOnlyList<int> PolygonVertexIndices,
        int? MaterialIndex);

    public sealed record AssetModelTextureCoordinate(double U, double V);
}
