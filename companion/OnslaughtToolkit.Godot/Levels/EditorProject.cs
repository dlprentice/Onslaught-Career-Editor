// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>The explicitly selected resources a snapshot depends on. Paths never come from a snapshot.</summary>
internal sealed record EditorProjectBase(int Level, bool SelectedWorld, int BaseLevel, bool IsBaseWorld,
    byte[] World, byte[] AnchorWorld, byte[]? BaseWorld, byte[]? Terrain);

internal sealed record EditorProjectIdentity(int Level, bool SelectedWorld, int BaseLevel, bool IsBaseWorld,
    string World, string AnchorWorld, string? BaseWorld, string? Terrain);

/// <summary>
/// Typed source and an untrusted claim about text associated with the current compiled record. The record hash only
/// identifies that record; after opening a snapshot, recompile the text against the selected inputs and compare the
/// resulting record before telling a player the text is in use.
/// </summary>
internal sealed record EditorProjectScript(int Index, string Name, string SourceHash, string? DraftText,
    string? UsedText, string? UsedRecordHash);

internal sealed record EditorSourceDraft(string Name, string Text, string SourceHash);

/// <summary>A validated in-memory snapshot. Reopening it starts a new undo history.</summary>
internal sealed record RestoredEditorProject(EditSession Session, TerrainDraft? Terrain, IReadOnlyList<EditorProjectScript> Scripts);

/// <summary>
/// Versioned editor-only snapshot. It is not a CE runtime format. Its world delta may contain original-derived world
/// bytes; the caller must tell the player what the project contains. It neither opens files nor chooses base resources.
/// </summary>
internal static class EditorProject
{
    internal const int MaxProjectBytes = 16 << 20, MaxWorldBytes = 32 << 20, MaxTextBytes = 1 << 20, MaxTotalTextBytes = 8 << 20, MaxDrafts = 1024;
    private const int MaxInsertBytes = MaxProjectBytes * 3 / 4;
    private const string Kind = "onslaught-ce-editor-snapshot";
    private const int Version = 1, TerrainGridVersion = 1;
    private static readonly UTF8Encoding StrictUtf8 = new(false, true);

    /// <summary>Captures the entire supported state without changing the session. Throws rather than dropping a field.</summary>
    internal static byte[] Capture(EditorProjectBase basis, EditSession session, TerrainDraft? terrain,
        IReadOnlyList<EditorProjectScript> scripts)
    {
        ArgumentNullException.ThrowIfNull(basis);
        ArgumentNullException.ThrowIfNull(session);
        ArgumentNullException.ThrowIfNull(scripts);
        CheckBase(basis);
        if (session.IsBaseWorld != basis.IsBaseWorld || !session.Baseline.AsSpan().SequenceEqual(basis.World))
            throw new InvalidDataException("The edit no longer belongs to the selected world.");
        byte[] working = session.ToBytes();
        CheckWorldSize(working);
        EditSession checkedSession = EditSession.Restore(basis.World, working, basis.IsBaseWorld);
        CheckScripts(checkedSession, scripts);
        if (terrain is not null)
        {
            if (!terrain.BelongsTo(session.Body)) throw new InvalidDataException("The terrain preview belongs to another edit.");
            if (basis.Terrain is null) throw new InvalidDataException("The terrain preview has no selected base terrain.");
            TerrainSurface expected = TerrainSurface.Build(Heightfield.Read(basis.Terrain), terrain.Baseline.Divisions);
            if (SurfaceHash(expected) != SurfaceHash(terrain.Baseline))
                throw new InvalidDataException("The terrain preview does not belong to the selected base terrain.");
            TerrainDraft checkedTerrain = TerrainDraft.Restore(checkedSession.Body, expected, terrain.Offsets());
            if (SurfaceHash(checkedTerrain.Surface) != SurfaceHash(terrain.Surface))
                throw new InvalidDataException("The terrain preview cannot be captured without losing a change.");
        }

        int prefix = 0;
        while (prefix < basis.World.Length && prefix < working.Length && basis.World[prefix] == working[prefix]) prefix++;
        int suffix = 0;
        while (suffix < basis.World.Length - prefix && suffix < working.Length - prefix &&
               basis.World[^(suffix + 1)] == working[^(suffix + 1)]) suffix++;
        int removed = basis.World.Length - prefix - suffix;
        int inserted = working.Length - prefix - suffix;
        if (inserted > MaxInsertBytes) throw new InvalidDataException("The changed world is too large for an editor snapshot.");
        byte[] insert = working.AsSpan(prefix, inserted).ToArray();

        using MemoryStream stream = new();
        using (Utf8JsonWriter json = new(stream))
        {
            json.WriteStartObject();
            json.WriteString("kind", Kind);
            json.WriteNumber("version", Version);
            json.WriteStartObject("base");
            json.WriteNumber("level", basis.Level);
            json.WriteBoolean("selected_world", basis.SelectedWorld);
            json.WriteNumber("base_level", basis.BaseLevel);
            json.WriteBoolean("base_world_edit", basis.IsBaseWorld);
            json.WriteString("world_sha256", Hash(basis.World));
            json.WriteString("anchor_sha256", Hash(basis.AnchorWorld));
            WriteHash(json, "base_world_sha256", basis.BaseWorld);
            WriteHash(json, "terrain_sha256", basis.Terrain);
            json.WriteEndObject();
            json.WriteStartObject("world_delta");
            json.WriteNumber("prefix", prefix);
            json.WriteNumber("remove", removed);
            json.WriteBase64String("insert", insert);
            json.WriteNumber("working_length", working.Length);
            json.WriteString("working_sha256", Hash(working));
            json.WriteEndObject();
            if (terrain is null) json.WriteNull("terrain_preview");
            else
            {
                json.WriteStartObject("terrain_preview");
                json.WriteNumber("grid_version", TerrainGridVersion);
                json.WriteNumber("divisions", terrain.Baseline.Divisions);
                json.WriteString("baseline_sha256", SurfaceHash(terrain.Baseline));
                json.WriteString("working_sha256", SurfaceHash(terrain.Surface));
                json.WriteStartArray("points");
                foreach (TerrainOffset offset in terrain.Offsets())
                {
                    json.WriteStartArray(); json.WriteNumberValue(offset.Index); json.WriteNumberValue(offset.Steps); json.WriteEndArray();
                }
                json.WriteEndArray();
                json.WriteEndObject();
            }
            json.WriteStartArray("scripts");
            foreach (EditorProjectScript script in scripts.OrderBy(item => item.Index))
            {
                json.WriteStartObject();
                json.WriteNumber("index", script.Index);
                json.WriteString("name", script.Name);
                json.WriteString("source_sha256", script.SourceHash);
                WriteString(json, "draft", script.DraftText);
                WriteString(json, "used_text", script.UsedText);
                WriteString(json, "used_record_sha256", script.UsedRecordHash);
                json.WriteEndObject();
            }
            json.WriteEndArray();
            json.WriteEndObject();
        }
        if (stream.Length > MaxProjectBytes) throw new InvalidDataException("This editor snapshot is too large to save safely.");
        return stream.ToArray();
    }

    /// <summary>Validates a snapshot against selected resources and returns a separate session; script-text associations remain untrusted claims.</summary>
    internal static RestoredEditorProject Restore(ReadOnlyMemory<byte> bytes, EditorProjectBase basis)
    {
        ArgumentNullException.ThrowIfNull(basis);
        CheckBase(basis);
        if (bytes.Length is 0 or > MaxProjectBytes) throw new InvalidDataException("This editor snapshot is empty or too large.");
        try
        {
            _ = StrictUtf8.GetCharCount(bytes.Span);
            using JsonDocument document = JsonDocument.Parse(bytes, new JsonDocumentOptions { MaxDepth = 16 });
            JsonElement root = document.RootElement;
            Fields(root, "kind", "version", "base", "world_delta", "terrain_preview", "scripts");
            if (String(root, "kind") != Kind || Number(root, "version") != Version)
                throw new InvalidDataException("This is not a supported editor snapshot version.");
            JsonElement b = root.GetProperty("base");
            Fields(b, "level", "selected_world", "base_level", "base_world_edit", "world_sha256", "anchor_sha256", "base_world_sha256", "terrain_sha256");
            if (Number(b, "level") != basis.Level || Boolean(b, "selected_world") != basis.SelectedWorld ||
                Number(b, "base_level") != basis.BaseLevel || Boolean(b, "base_world_edit") != basis.IsBaseWorld ||
                Digest(b, "world_sha256") != Hash(basis.World) || Digest(b, "anchor_sha256") != Hash(basis.AnchorWorld) ||
                OptionalDigest(b, "base_world_sha256") != OptionalHash(basis.BaseWorld) || OptionalDigest(b, "terrain_sha256") != OptionalHash(basis.Terrain))
                throw new InvalidDataException("The selected level, world or terrain does not match this snapshot.");

            JsonElement delta = root.GetProperty("world_delta");
            Fields(delta, "prefix", "remove", "insert", "working_length", "working_sha256");
            int prefix = Number(delta, "prefix"), removed = Number(delta, "remove"), length = Number(delta, "working_length");
            if (prefix < 0 || prefix > basis.World.Length || removed < 0 || removed > basis.World.Length - prefix || length is <= 0 or > MaxWorldBytes)
                throw new InvalidDataException("The saved world delta is outside its bounds.");
            string encoded = String(delta, "insert");
            if (encoded.Length > ((MaxInsertBytes + 2) / 3) * 4)
                throw new InvalidDataException("The saved world delta is too large.");
            byte[] insert = Convert.FromBase64String(encoded);
            if (insert.Length > MaxInsertBytes) throw new InvalidDataException("The saved world delta is too large.");
            int suffix = basis.World.Length - prefix - removed;
            if ((long)prefix + insert.Length + suffix != length)
                throw new InvalidDataException("The saved world delta has an inconsistent length.");
            byte[] working = new byte[length];
            basis.World.AsSpan(0, prefix).CopyTo(working);
            insert.CopyTo(working, prefix);
            basis.World.AsSpan(prefix + removed, suffix).CopyTo(working.AsSpan(prefix + insert.Length));
            if (Digest(delta, "working_sha256") != Hash(working)) throw new InvalidDataException("The saved world did not verify.");
            EditSession session = EditSession.Restore(basis.World, working, basis.IsBaseWorld);

            TerrainDraft? terrain = null;
            JsonElement t = root.GetProperty("terrain_preview");
            if (t.ValueKind != JsonValueKind.Null)
            {
                Fields(t, "grid_version", "divisions", "baseline_sha256", "working_sha256", "points");
                int divisions = Number(t, "divisions");
                if (Number(t, "grid_version") != TerrainGridVersion || divisions is < 1 or > TerrainSurface.MaxDivisions || basis.Terrain is null)
                    throw new InvalidDataException("The terrain preview uses an unsupported grid or has no matching terrain.");
                TerrainSurface baseline = TerrainSurface.Build(Heightfield.Read(basis.Terrain), divisions);
                if (Digest(t, "baseline_sha256") != SurfaceHash(baseline)) throw new InvalidDataException("The sampled base terrain did not verify.");
                JsonElement points = t.GetProperty("points");
                if (points.ValueKind != JsonValueKind.Array || points.GetArrayLength() > baseline.Vertices.Length)
                    throw new InvalidDataException("The saved terrain points are invalid or too numerous.");
                List<TerrainOffset> offsets = [];
                foreach (JsonElement point in points.EnumerateArray())
                {
                    if (point.ValueKind != JsonValueKind.Array || point.GetArrayLength() != 2 || !point[0].TryGetInt32(out int index) || !point[1].TryGetInt32(out int steps))
                        throw new InvalidDataException("A saved terrain point is invalid.");
                    offsets.Add(new TerrainOffset(index, steps));
                }
                terrain = TerrainDraft.Restore(session.Body, baseline, offsets);
                if (Digest(t, "working_sha256") != SurfaceHash(terrain.Surface)) throw new InvalidDataException("The edited terrain preview did not verify.");
            }

            JsonElement entries = root.GetProperty("scripts");
            if (entries.ValueKind != JsonValueKind.Array || entries.GetArrayLength() > MaxDrafts)
                throw new InvalidDataException("The saved script drafts are invalid or too numerous.");
            List<EditorProjectScript> scripts = [];
            foreach (JsonElement entry in entries.EnumerateArray())
            {
                Fields(entry, "index", "name", "source_sha256", "draft", "used_text", "used_record_sha256");
                scripts.Add(new EditorProjectScript(Number(entry, "index"), String(entry, "name"), Digest(entry, "source_sha256"),
                    OptionalString(entry, "draft"), OptionalString(entry, "used_text"), OptionalDigest(entry, "used_record_sha256")));
            }
            CheckScripts(session, scripts);
            return new RestoredEditorProject(session, terrain, scripts);
        }
        catch (Exception error) when (error is JsonException or FormatException or InvalidOperationException or OverflowException or DecoderFallbackException)
        {
            throw new InvalidDataException("This editor snapshot is malformed or unsupported.", error);
        }
    }

    private static void CheckBase(EditorProjectBase basis)
    {
        if (basis.Level is < 0 or > 999 || basis.BaseLevel is < -1 or > 999 || basis.World is null || basis.AnchorWorld is null)
            throw new InvalidDataException("The selected level and world are invalid.");
        CheckWorldSize(basis.World);
        CheckWorldSize(basis.AnchorWorld);
        if (!basis.SelectedWorld && !basis.World.AsSpan().SequenceEqual(basis.AnchorWorld))
            throw new InvalidDataException("The level's selected world does not match its archive.");
        // An ERES or world chunk may span members: the per-member limit does not bound the joined resource.
        if (basis.BaseWorld is { Length: > LevelArchive.MaxInflatedBytes } || basis.Terrain is { Length: > LevelArchive.MaxInflatedBytes })
            throw new InvalidDataException("A selected level resource is too large.");
    }

    private static void CheckWorldSize(byte[] bytes)
    {
        if (bytes.Length is 0 or > MaxWorldBytes) throw new InvalidDataException("The world is empty or too large for a snapshot.");
    }

    private static void CheckScripts(EditSession session, IReadOnlyList<EditorProjectScript> scripts)
    {
        if (scripts.Count > MaxDrafts) throw new InvalidDataException("There are too many script drafts to save safely.");
        HashSet<int> indices = [];
        Dictionary<string, int> nameCounts = new(StringComparer.Ordinal);
        foreach (MissionScript item in session.Body.Scripts)
        {
            if (item?.Name is not { } name) throw new InvalidDataException("A script in the world has no name.");
            nameCounts[name] = nameCounts.GetValueOrDefault(name) + 1;
        }
        long total = 0;
        foreach (EditorProjectScript script in scripts)
        {
            if (script is null || script.Index < 0 || script.Index >= session.Body.Scripts.Count || !indices.Add(script.Index) ||
                script.Name != session.Body.Scripts[script.Index].Name || !nameCounts.TryGetValue(script.Name, out int count) || count != 1 ||
                !IsDigest(script.SourceHash) || (script.DraftText is null && script.UsedText is null) ||
                (script.UsedText is null) != (script.UsedRecordHash is null))
                throw new InvalidDataException("A script draft is ambiguous or does not belong to the selected world.");
            total += TextSize(script.Name) + TextSize(script.DraftText) + TextSize(script.UsedText);
            if (total > MaxTotalTextBytes) throw new InvalidDataException("The script drafts are too large to save safely.");
            if (script.UsedRecordHash is not null && (!IsDigest(script.UsedRecordHash) ||
                script.UsedRecordHash != Hash(WorldBodyWriter.ScriptBytes(session.Body.Scripts[script.Index]))))
                throw new InvalidDataException("A script's recorded compiled state no longer matches the world.");
        }
    }

    private static int TextSize(string? text)
    {
        if (text is null) return 0;
        int size;
        try { size = StrictUtf8.GetByteCount(text); }
        catch (EncoderFallbackException error) { throw new InvalidDataException("A script draft cannot be stored without changing its text.", error); }
        if (size > MaxTextBytes) throw new InvalidDataException("A script draft is too large to save safely.");
        return size;
    }

    private static string SurfaceHash(TerrainSurface surface)
    {
        using IncrementalHash hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        Span<byte> bytes = stackalloc byte[12];
        BinaryPrimitives.WriteInt32LittleEndian(bytes, surface.Divisions);
        hash.AppendData(bytes[..4]);
        foreach (var vertex in surface.Vertices.Span)
        {
            BinaryPrimitives.WriteUInt32LittleEndian(bytes, BitConverter.SingleToUInt32Bits(vertex.X));
            BinaryPrimitives.WriteUInt32LittleEndian(bytes[4..], BitConverter.SingleToUInt32Bits(vertex.Y));
            BinaryPrimitives.WriteUInt32LittleEndian(bytes[8..], BitConverter.SingleToUInt32Bits(vertex.Z));
            hash.AppendData(bytes);
        }
        return Convert.ToHexStringLower(hash.GetHashAndReset());
    }

    internal static string Hash(ReadOnlySpan<byte> bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    internal static EditorProjectIdentity Identity(EditorProjectBase basis) => new(basis.Level, basis.SelectedWorld, basis.BaseLevel,
        basis.IsBaseWorld, Hash(basis.World), Hash(basis.AnchorWorld), OptionalHash(basis.BaseWorld), OptionalHash(basis.Terrain));
    internal static string TextHash(string text)
    {
        try { return Hash(StrictUtf8.GetBytes(text)); }
        catch (EncoderFallbackException error) { throw new InvalidDataException("Source text cannot be identified without changing it.", error); }
    }
    private static string? OptionalHash(byte[]? bytes) => bytes is null ? null : Hash(bytes);
    private static bool IsDigest(string? value) => value is { Length: 64 } && value.All(c => c is >= '0' and <= '9' or >= 'a' and <= 'f');
    private static void WriteHash(Utf8JsonWriter json, string name, byte[]? bytes) => WriteString(json, name, OptionalHash(bytes));
    private static void WriteString(Utf8JsonWriter json, string name, string? value) { if (value is null) json.WriteNull(name); else json.WriteString(name, value); }

    private static void Fields(JsonElement value, params string[] names)
    {
        if (value.ValueKind != JsonValueKind.Object) throw new InvalidDataException("A snapshot section is not an object.");
        HashSet<string> missing = new(names, StringComparer.Ordinal);
        foreach (JsonProperty field in value.EnumerateObject())
            if (!missing.Remove(field.Name)) throw new InvalidDataException("A snapshot field is unknown or repeated.");
        if (missing.Count != 0) throw new InvalidDataException("A required snapshot field is missing.");
    }

    private static string String(JsonElement parent, string name) => parent.GetProperty(name).ValueKind == JsonValueKind.String
        ? parent.GetProperty(name).GetString()! : throw new InvalidDataException("A snapshot text field is invalid.");
    private static string? OptionalString(JsonElement parent, string name) => parent.GetProperty(name).ValueKind == JsonValueKind.Null ? null : String(parent, name);
    private static string Digest(JsonElement parent, string name) => String(parent, name) is { } value && IsDigest(value)
        ? value : throw new InvalidDataException("A snapshot identity is invalid.");
    private static string? OptionalDigest(JsonElement parent, string name) => parent.GetProperty(name).ValueKind == JsonValueKind.Null ? null : Digest(parent, name);
    private static int Number(JsonElement parent, string name) => parent.GetProperty(name).TryGetInt32(out int value)
        ? value : throw new InvalidDataException("A snapshot number is invalid.");
    private static bool Boolean(JsonElement parent, string name) => parent.GetProperty(name).ValueKind switch
    {
        JsonValueKind.True => true,
        JsonValueKind.False => false,
        _ => throw new InvalidDataException("A snapshot flag is invalid."),
    };
}
