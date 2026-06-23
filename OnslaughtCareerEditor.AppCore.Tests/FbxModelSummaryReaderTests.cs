using System;
using System.IO;
using System.IO.Compression;
using System.Text;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class FbxModelSummaryReaderTests
    {
        [Fact]
        public void Read_ReturnsCountsForBinaryFbxExport()
        {
            string path = Path.Combine(Path.GetTempPath(), "oce-fbx-summary-tests", $"{Guid.NewGuid():N}.fbx");
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, BuildMinimalBinaryFbx());

            try
            {
                AssetModelSummary summary = FbxModelSummaryReader.Read(path);

                Assert.True(summary.MetadataAvailable);
                Assert.Equal("Binary FBX", summary.Format);
                Assert.Equal(7400, summary.FormatVersion);
                Assert.True(summary.ByteSize > 0);
                Assert.Equal(1, summary.GeometryCount);
                Assert.Equal(1, summary.ModelCount);
                Assert.Equal(1, summary.MaterialCount);
                Assert.Equal(1, summary.TextureBindingCount);
                Assert.Equal(1, summary.MaterialLayerCount);
                Assert.Equal(1, summary.MaterialAssignmentIndexCount);
                Assert.Contains("AllSame", summary.MaterialMappingModes);
                Assert.Contains("IndexToDirect", summary.MaterialReferenceModes);
                Assert.Equal(1, summary.ObjectConnectionCount);
                Assert.Equal(1, summary.PropertyConnectionCount);
                Assert.Equal(1, summary.TextureToMaterialConnectionCount);
                Assert.Contains("DiffuseColor", summary.TextureToMaterialSlotNames);
                Assert.Contains("Material1", summary.MaterialNames);
                Assert.Contains("base_color_texture", summary.TextureBindingNames);
                Assert.Contains("texture_one.png", summary.TextureBindingFileNames);
                Assert.Equal(3, summary.VertexCount);
                Assert.Equal(3, summary.PolygonIndexCount);
                Assert.Equal(3, summary.NormalCount);
                Assert.Equal(3, summary.NormalIndexCount);
                Assert.Contains("ByPolygonVertex", summary.NormalMappingModes);
                Assert.Contains("IndexToDirect", summary.NormalReferenceModes);
                Assert.Equal(3, summary.VertexColorCount);
                Assert.Equal(3, summary.VertexColorIndexCount);
                Assert.Contains("ByPolygonVertex", summary.VertexColorMappingModes);
                Assert.Contains("IndexToDirect", summary.VertexColorReferenceModes);
                Assert.Equal(3, summary.TextureCoordinateCount);
                Assert.Equal(3, summary.TextureCoordinateIndexCount);
                Assert.Contains("ByPolygonVertex", summary.TextureCoordinateMappingModes);
                Assert.Contains("IndexToDirect", summary.TextureCoordinateReferenceModes);
                Assert.True(summary.GeometryPreview.Available);
                Assert.Equal(3, summary.GeometryPreview.Vertices.Count);
                Assert.Equal(3, summary.GeometryPreview.Edges.Count);
                Assert.Contains(summary.GeometryPreview.Vertices, vertex => vertex.X == 1 && vertex.Y == 0 && vertex.Z == 0);
                Assert.True(summary.MeshPayload.Available);
                Assert.True(summary.MeshPayload.Complete);
                Assert.Equal("complete-mesh-payload", summary.MeshPayload.Status);
                AssetModelMeshFace face = Assert.Single(summary.MeshPayload.Faces);
                Assert.Equal([0, 1, 2], face.VertexIndices);
                Assert.Equal([0, 1, 2], face.PolygonVertexIndices);
                Assert.Equal(0, face.MaterialIndex);
                Assert.Equal(3, summary.MeshPayload.Normals.Count);
                Assert.Equal([0, 1, 2], summary.MeshPayload.NormalIndices);
                Assert.Equal(3, summary.MeshPayload.TextureCoordinates.Count);
                Assert.Equal([0, 1, 2], summary.MeshPayload.TextureCoordinateIndices);
                Assert.Equal([0], summary.MeshPayload.MaterialAssignmentIndices);
            }
            finally
            {
                File.Delete(path);
            }
        }

        [Fact]
        public void Read_ReturnsPreviewForCompressedBinaryFbxArrays()
        {
            string path = Path.Combine(Path.GetTempPath(), "oce-fbx-summary-tests", $"{Guid.NewGuid():N}.fbx");
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, BuildMinimalBinaryFbx(compressArrays: true));

            try
            {
                AssetModelSummary summary = FbxModelSummaryReader.Read(path);

                Assert.True(summary.MetadataAvailable);
                Assert.Equal(3, summary.VertexCount);
                Assert.Equal(3, summary.PolygonIndexCount);
                Assert.Equal(3, summary.NormalCount);
                Assert.Equal(3, summary.NormalIndexCount);
                Assert.Contains("ByPolygonVertex", summary.NormalMappingModes);
                Assert.Contains("IndexToDirect", summary.NormalReferenceModes);
                Assert.Equal(3, summary.VertexColorCount);
                Assert.Equal(3, summary.VertexColorIndexCount);
                Assert.Contains("ByPolygonVertex", summary.VertexColorMappingModes);
                Assert.Contains("IndexToDirect", summary.VertexColorReferenceModes);
                Assert.Equal(3, summary.TextureCoordinateCount);
                Assert.Equal(3, summary.TextureCoordinateIndexCount);
                Assert.Contains("ByPolygonVertex", summary.TextureCoordinateMappingModes);
                Assert.Contains("IndexToDirect", summary.TextureCoordinateReferenceModes);
                Assert.Equal(1, summary.MaterialLayerCount);
                Assert.Equal(1, summary.MaterialAssignmentIndexCount);
                Assert.Contains("AllSame", summary.MaterialMappingModes);
                Assert.Contains("IndexToDirect", summary.MaterialReferenceModes);
                Assert.Equal(1, summary.ObjectConnectionCount);
                Assert.Equal(1, summary.PropertyConnectionCount);
                Assert.Equal(1, summary.TextureToMaterialConnectionCount);
                Assert.Contains("DiffuseColor", summary.TextureToMaterialSlotNames);
                Assert.True(summary.GeometryPreview.Available);
                Assert.Equal(3, summary.GeometryPreview.Vertices.Count);
                Assert.Equal(3, summary.GeometryPreview.Edges.Count);
                Assert.True(summary.MeshPayload.Available);
                Assert.True(summary.MeshPayload.Complete);
                Assert.Single(summary.MeshPayload.Faces);
            }
            finally
            {
                File.Delete(path);
            }
        }

        [Fact]
        public void Read_ReturnsUnavailableForNonBinaryFbx()
        {
            string path = Path.Combine(Path.GetTempPath(), "oce-fbx-summary-tests", $"{Guid.NewGuid():N}.fbx");
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllText(path, "not a binary fbx");

            try
            {
                AssetModelSummary summary = FbxModelSummaryReader.Read(path);

                Assert.False(summary.MetadataAvailable);
                Assert.Equal("FBX", summary.Format);
                Assert.Equal("FBX export is too small to inspect.", summary.Status);
            }
            finally
            {
                File.Delete(path);
            }
        }

        private static byte[] BuildMinimalBinaryFbx(bool compressArrays = false)
        {
            using MemoryStream stream = new();
            using BinaryWriter writer = new(stream, Encoding.ASCII, leaveOpen: true);

            writer.Write(Encoding.ASCII.GetBytes("Kaydara FBX Binary  "));
            writer.Write((byte)0);
            writer.Write((byte)0x1A);
            writer.Write((byte)0);
            writer.Write(7400);

            WriteNode(
                writer,
                "Objects",
                props: [],
                children:
                [
                    () => WriteNode(
                        writer,
                        "Geometry",
                        props:
                        [
                            () => WriteLongProperty(writer, 1),
                            () => WriteStringProperty(writer, "Cube\0\u0001Geometry"),
                            () => WriteStringProperty(writer, "Mesh")
                        ],
                        children:
                        [
                            () => WriteNode(
                                writer,
                                "Vertices",
                                props:
                                [
                                    () => WriteDoubleArrayProperty(writer, [0, 0, 0, 1, 0, 0, 0, 1, 0], compressArrays)
                                ],
                                children: []),
                            () => WriteNode(
                                writer,
                                "PolygonVertexIndex",
                                props:
                                [
                                    () => WriteIntArrayProperty(writer, [0, 1, -3], compressArrays)
                                ],
                                children: []),
                            () => WriteNode(
                                writer,
                                "LayerElementNormal",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Normals",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [0, 0, 1, 0, 0, 1, 0, 0, 1], compressArrays)
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "NormalsIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2], compressArrays)
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementUV",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "UV",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [0, 0, 1, 0, 0, 1], compressArrays)
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "UVIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2], compressArrays)
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementColor",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Colors",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1], compressArrays)
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ColorIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2], compressArrays)
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementMaterial",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "AllSame")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Materials",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0], compressArrays)
                                        ],
                                        children: [])
                                ])
                        ]),
                    () => WriteNode(
                        writer,
                        "Model",
                        props:
                        [
                            () => WriteLongProperty(writer, 2),
                            () => WriteStringProperty(writer, "Cube\0\u0001Model"),
                            () => WriteStringProperty(writer, "Mesh")
                        ],
                        children: []),
                    () => WriteNode(
                        writer,
                        "Material",
                        props:
                        [
                            () => WriteLongProperty(writer, 3),
                            () => WriteStringProperty(writer, "Material1\0\u0001Material"),
                            () => WriteStringProperty(writer, string.Empty)
                        ],
                        children: []),
                    () => WriteNode(
                        writer,
                        "Texture",
                        props:
                        [
                            () => WriteLongProperty(writer, 4),
                            () => WriteStringProperty(writer, "base_color_texture\0\u0001Texture"),
                            () => WriteStringProperty(writer, string.Empty)
                        ],
                        children:
                        [
                            () => WriteNode(
                                writer,
                                "Properties70",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "P",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "FileName"),
                                            () => WriteStringProperty(writer, "KString"),
                                            () => WriteStringProperty(writer, string.Empty),
                                            () => WriteStringProperty(writer, "A"),
                                            () => WriteStringProperty(writer, @"C:\exports\texture_one.png")
                                        ],
                                        children: [])
                                ])
                        ])
                ]);
            WriteNode(
                writer,
                "Connections",
                props: [],
                children:
                [
                    () => WriteNode(
                        writer,
                        "C",
                        props:
                        [
                            () => WriteStringProperty(writer, "OO"),
                            () => WriteLongProperty(writer, 3),
                            () => WriteLongProperty(writer, 2)
                        ],
                        children: []),
                    () => WriteNode(
                        writer,
                        "C",
                        props:
                        [
                            () => WriteStringProperty(writer, "OP"),
                            () => WriteLongProperty(writer, 4),
                            () => WriteLongProperty(writer, 3),
                            () => WriteStringProperty(writer, "DiffuseColor")
                        ],
                        children: [])
                ]);
            WriteSentinel(writer);

            return stream.ToArray();
        }

        private static void WriteNode(BinaryWriter writer, string name, Action[] props, Action[] children)
        {
            long headerPosition = writer.BaseStream.Position;
            writer.Write((uint)0);
            writer.Write((uint)props.Length);
            writer.Write((uint)0);
            writer.Write((byte)name.Length);
            writer.Write(Encoding.ASCII.GetBytes(name));

            long propertyStart = writer.BaseStream.Position;
            foreach (Action prop in props)
            {
                prop();
            }

            long propertyEnd = writer.BaseStream.Position;
            foreach (Action child in children)
            {
                child();
            }

            if (children.Length > 0)
            {
                WriteSentinel(writer);
            }

            long endPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = headerPosition;
            writer.Write((uint)endPosition);
            writer.Write((uint)props.Length);
            writer.Write((uint)(propertyEnd - propertyStart));
            writer.Write((byte)name.Length);
            writer.BaseStream.Position = endPosition;
        }

        private static void WriteLongProperty(BinaryWriter writer, long value)
        {
            writer.Write((byte)'L');
            writer.Write(value);
        }

        private static void WriteStringProperty(BinaryWriter writer, string value)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(value);
            writer.Write((byte)'S');
            writer.Write((uint)bytes.Length);
            writer.Write(bytes);
        }

        private static void WriteDoubleArrayProperty(BinaryWriter writer, double[] values, bool compress)
        {
            writer.Write((byte)'d');
            writer.Write((uint)values.Length);
            WriteArrayPayload(writer, compress, innerWriter =>
            {
                foreach (double value in values)
                {
                    innerWriter.Write(value);
                }
            });
        }

        private static void WriteIntArrayProperty(BinaryWriter writer, int[] values, bool compress)
        {
            writer.Write((byte)'i');
            writer.Write((uint)values.Length);
            WriteArrayPayload(writer, compress, innerWriter =>
            {
                foreach (int value in values)
                {
                    innerWriter.Write(value);
                }
            });
        }

        private static void WriteArrayPayload(BinaryWriter writer, bool compress, Action<BinaryWriter> writeRawPayload)
        {
            using MemoryStream rawStream = new();
            using (BinaryWriter rawWriter = new(rawStream, Encoding.ASCII, leaveOpen: true))
            {
                writeRawPayload(rawWriter);
            }

            byte[] payload = rawStream.ToArray();
            if (compress)
            {
                using MemoryStream compressedStream = new();
                using (ZLibStream zlibStream = new(compressedStream, CompressionLevel.SmallestSize, leaveOpen: true))
                {
                    zlibStream.Write(payload);
                }

                payload = compressedStream.ToArray();
                writer.Write((uint)1);
            }
            else
            {
                writer.Write((uint)0);
            }

            writer.Write((uint)payload.Length);
            writer.Write(payload);
        }

        private static void WriteSentinel(BinaryWriter writer)
        {
            writer.Write(new byte[13]);
        }
    }
}
