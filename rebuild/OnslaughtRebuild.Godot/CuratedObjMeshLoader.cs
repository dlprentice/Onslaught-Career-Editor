// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using Godot;

namespace OnslaughtRebuild.GodotClient;

internal static class CuratedObjMeshLoader
{
    private const int MaximumVertices = 100_000;
    private const int MaximumTriangles = 200_000;

    public static ArrayMesh Load(string resourcePath)
    {
        string source = Godot.FileAccess.GetFileAsString(resourcePath);
        if (string.IsNullOrEmpty(source))
        {
            throw new InvalidDataException($"Curated mesh '{resourcePath}' is missing or empty.");
        }

        var vertices = new List<Vector3>();
        var normals = new List<Vector3>();
        var textureCoordinates = new List<Vector2>();
        var indices = new List<int>();

        foreach (string rawLine in source.Split('\n'))
        {
            string line = rawLine.TrimEnd('\r');
            if (line.Length == 0)
            {
                continue;
            }

            string[] fields = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            switch (fields[0])
            {
                case "v":
                    RequireFieldCount(fields, 4, "vertex");
                    vertices.Add(new Vector3(ParseFloat(fields[1]), ParseFloat(fields[2]), ParseFloat(fields[3])));
                    if (vertices.Count > MaximumVertices)
                    {
                        throw new InvalidDataException("Curated mesh exceeds the vertex limit.");
                    }
                    break;

                case "vt":
                    RequireFieldCount(fields, 3, "texture coordinate");
                    textureCoordinates.Add(new Vector2(ParseFloat(fields[1]), ParseFloat(fields[2])));
                    break;

                case "vn":
                    RequireFieldCount(fields, 4, "normal");
                    normals.Add(new Vector3(ParseFloat(fields[1]), ParseFloat(fields[2]), ParseFloat(fields[3])));
                    break;

                case "f":
                    RequireFieldCount(fields, 4, "triangle");
                    for (int field = 1; field < fields.Length; field++)
                    {
                        indices.Add(ParseUnifiedIndex(fields[field]));
                    }
                    if (indices.Count / 3 > MaximumTriangles)
                    {
                        throw new InvalidDataException("Curated mesh exceeds the triangle limit.");
                    }
                    break;

                default:
                    throw new InvalidDataException($"Curated mesh contains unsupported OBJ record '{fields[0]}'.");
            }
        }

        if (vertices.Count == 0 || indices.Count == 0 ||
            normals.Count != vertices.Count || textureCoordinates.Count != vertices.Count ||
            indices.Any(index => index < 0 || index >= vertices.Count))
        {
            throw new InvalidDataException("Curated mesh has inconsistent geometry arrays.");
        }

        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = vertices.ToArray();
        arrays[(int)Mesh.ArrayType.Normal] = normals.ToArray();
        arrays[(int)Mesh.ArrayType.TexUV] = textureCoordinates.ToArray();
        arrays[(int)Mesh.ArrayType.Index] = indices.ToArray();

        var mesh = new ArrayMesh();
        mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        return mesh;
    }

    private static int ParseUnifiedIndex(string value)
    {
        string[] fields = value.Split('/');
        if (fields.Length != 3 ||
            !int.TryParse(fields[0], NumberStyles.None, CultureInfo.InvariantCulture, out int vertex) ||
            !int.TryParse(fields[1], NumberStyles.None, CultureInfo.InvariantCulture, out int textureCoordinate) ||
            !int.TryParse(fields[2], NumberStyles.None, CultureInfo.InvariantCulture, out int normal) ||
            vertex <= 0 || vertex != textureCoordinate || vertex != normal)
        {
            throw new InvalidDataException("Curated mesh requires unified positive OBJ indices.");
        }

        return vertex - 1;
    }

    private static float ParseFloat(string value)
    {
        if (!float.TryParse(value, NumberStyles.Float, CultureInfo.InvariantCulture, out float result) ||
            !float.IsFinite(result))
        {
            throw new InvalidDataException("Curated mesh contains a non-finite numeric value.");
        }

        return result;
    }

    private static void RequireFieldCount(string[] fields, int expected, string role)
    {
        if (fields.Length != expected)
        {
            throw new InvalidDataException($"Curated mesh has an invalid {role} record.");
        }
    }
}
