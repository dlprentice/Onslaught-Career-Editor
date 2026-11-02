// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Text;
using System.Text.Json;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>Bounded source-preserving JSON. It opens no paths, compiles nothing and produces no retail world data.</summary>
public static class CeMissionProjectJson
{
    private static readonly UTF8Encoding Utf8 = new(false, true);

    public static byte[] Write(CeMissionProject project)
    {
        ArgumentNullException.ThrowIfNull(project);
        using MemoryStream stream = new();
        using (Utf8JsonWriter json = new(stream, new JsonWriterOptions { Indented = true }))
        {
            json.WriteStartObject();
            json.WriteString("kind", CeMissionProject.Kind);
            json.WriteNumber("version", CeMissionProject.Version);
            json.WriteString("coordinates", CeMissionProject.CoordinateFrame);
            json.WriteString("source_language", CeMissionProject.SourceLanguage);
            json.WriteString("id", project.Id);
            json.WriteString("name", project.Name);
            WriteReference(json, "entry_script", project.EntryScriptId);
            json.WriteStartArray("placements");
            foreach (CeMissionPlacement placement in project.Placements)
            {
                json.WriteStartObject();
                json.WriteString("id", placement.Id);
                json.WriteString("name", placement.Name);
                json.WriteString("definition", placement.Definition);
                json.WriteStartArray("position");
                json.WriteNumberValue(placement.Position.X);
                json.WriteNumberValue(placement.Position.Y);
                json.WriteNumberValue(placement.Position.Z);
                json.WriteEndArray();
                WriteReference(json, "script", placement.ScriptId);
                json.WriteEndObject();
            }
            json.WriteEndArray();
            json.WriteStartArray("scripts");
            foreach (CeMissionSource script in project.Scripts)
            {
                json.WriteStartObject();
                json.WriteString("id", script.Id);
                json.WriteString("name", script.Name);
                json.WriteString("source", script.Text);
                json.WriteEndObject();
            }
            json.WriteEndArray();
            json.WriteEndObject();
        }
        if (stream.Length >= CeMissionProject.MaxDocumentBytes)
            throw new InvalidDataException("The project exceeds the editor's document-size limit.");
        stream.WriteByte((byte)'\n');
        return stream.ToArray();
    }

    public static CeMissionProject Read(ReadOnlyMemory<byte> bytes)
    {
        if (bytes.Length is 0 or > CeMissionProject.MaxDocumentBytes)
            throw new InvalidDataException("The project is empty or exceeds the editor's document-size limit.");
        try
        {
            _ = Utf8.GetCharCount(bytes.Span);
            using JsonDocument document = JsonDocument.Parse(bytes, new JsonDocumentOptions { MaxDepth = 16 });
            JsonElement root = document.RootElement;
            Fields(root, "kind", "version", "coordinates", "source_language", "id", "name", "entry_script", "placements", "scripts");
            if (Text(root, "kind") != CeMissionProject.Kind || root.GetProperty("version").GetInt32() != CeMissionProject.Version)
                throw new InvalidDataException("This is not a supported CE mission-project document.");
            if (Text(root, "coordinates") != CeMissionProject.CoordinateFrame || Text(root, "source_language") != CeMissionProject.SourceLanguage)
                throw new InvalidDataException("The project's coordinate frame or source language is unsupported.");
            JsonElement placements = root.GetProperty("placements"), scripts = root.GetProperty("scripts");
            ArrayLimit(placements, CeMissionProject.MaxPlacements, "placement");
            ArrayLimit(scripts, CeMissionProject.MaxScripts, "script");
            List<CeMissionPlacement> objects = [];
            foreach (JsonElement placement in placements.EnumerateArray())
            {
                Fields(placement, "id", "name", "definition", "position", "script");
                JsonElement position = placement.GetProperty("position");
                if (position.ValueKind != JsonValueKind.Array || position.GetArrayLength() != 3)
                    throw new InvalidDataException("A placement needs exactly three coordinates.");
                objects.Add(new(Text(placement, "id"), Text(placement, "name"), Text(placement, "definition"),
                    new Vector3(position[0].GetSingle(), position[1].GetSingle(), position[2].GetSingle()), Reference(placement, "script")));
            }
            List<CeMissionSource> sources = [];
            foreach (JsonElement script in scripts.EnumerateArray())
            {
                Fields(script, "id", "name", "source");
                sources.Add(new(Text(script, "id"), Text(script, "name"), Text(script, "source")));
            }
            return new(Text(root, "id"), Text(root, "name"), objects, sources, Reference(root, "entry_script"));
        }
        catch (Exception error) when (error is JsonException or ArgumentException or InvalidOperationException or FormatException or OverflowException)
        {
            throw new InvalidDataException("The CE mission project is malformed or contains unsupported data.", error);
        }
    }

    private static void WriteReference(Utf8JsonWriter json, string name, string? value)
    {
        if (value is null) json.WriteNull(name);
        else json.WriteString(name, value);
    }

    private static void ArrayLimit(JsonElement value, int limit, string label)
    {
        if (value.ValueKind != JsonValueKind.Array || value.GetArrayLength() > limit)
            throw new InvalidDataException($"The project's {label} list is invalid or exceeds the editor's limit.");
    }

    private static string Text(JsonElement element, string name) => element.GetProperty(name).ValueKind == JsonValueKind.String
        ? element.GetProperty(name).GetString()! : throw new InvalidDataException($"The {name} field must be text.");

    private static string? Reference(JsonElement element, string name) => element.GetProperty(name).ValueKind == JsonValueKind.Null
        ? null : Text(element, name);

    private static void Fields(JsonElement element, params string[] expected)
    {
        if (element.ValueKind != JsonValueKind.Object) throw new InvalidDataException("A project record must be an object.");
        HashSet<string> allowed = new(expected, StringComparer.Ordinal), seen = new(StringComparer.Ordinal);
        foreach (JsonProperty field in element.EnumerateObject())
            if (!allowed.Contains(field.Name) || !seen.Add(field.Name))
                throw new InvalidDataException("A project record has an unknown or duplicate field.");
        if (!seen.SetEquals(allowed)) throw new InvalidDataException("A project record is missing a required field.");
    }
}
