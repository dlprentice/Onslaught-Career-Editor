// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Text;

namespace OnslaughtToolkit.Companion.Assets;

/// <summary>
/// The bounded definition-to-model join also used by tools/content_catalog.py: unit/building/squad objects use a
/// unit definition's mesh field, features use a feature definition's mesh field, and the selected archive must name
/// that mesh exactly once. This reads identities only, not behaviour or simulation state.
/// </summary>
internal sealed class InstalledModelReferences
{
    private readonly Dictionary<(int Kind, string Name), List<string?>> _definitions = [];
    private readonly Dictionary<string, List<string>> _archiveNames = new(StringComparer.OrdinalIgnoreCase);

    internal static bool DefinedKind(int kind) => kind is 8 or 25 or 28 or 35;

    internal InstalledModelReferences(ReadOnlySpan<byte> definitions, ReadOnlySpan<byte> archive)
    {
        ReadDefinitions(definitions);
        ReadArchive(archive);
    }

    /// <summary>Null means absent or ambiguous. Definition names are case-sensitive, mesh names are not.</summary>
    internal string? Resolve(int kind, string definition)
    {
        if (!DefinedKind(kind) || !_definitions.TryGetValue((kind == 35 ? 35 : 8, definition), out List<string?>? names) ||
            names.Count != 1 || string.IsNullOrEmpty(names[0])) return null;
        // Availability cannot disambiguate duplicate definitions, including ones without a mesh field.
        return _archiveNames.TryGetValue(Key(names[0]!), out List<string>? records) && records.Count == 1 ? records[0] : null;
    }

    /// <summary>The installed shelf spelling, preserving directory flattening rather than choosing a basename.</summary>
    internal static string Key(string name)
    {
        string key = name.Replace('\\', '%').Replace('/', '%');
        if (key.EndsWith(".aya", StringComparison.OrdinalIgnoreCase)) key = key[..^4];
        if (key.EndsWith(".msh", StringComparison.OrdinalIgnoreCase)) key = key[..^4];
        if (string.IsNullOrWhiteSpace(key) || key.Length > 512 || key.Any(char.IsControl))
            throw new InvalidDataException("A map model reference cannot be previewed.");
        return key;
    }

    internal static string ShelfKey(string filename) => Key(filename.StartsWith("m_", StringComparison.OrdinalIgnoreCase) ? filename[2..] : filename);

    private void ReadDefinitions(ReadOnlySpan<byte> bytes)
    {
        if (bytes.Length is < 6 or > (16 << 20) || BinaryPrimitives.ReadUInt16LittleEndian(bytes) != 18)
            throw new InvalidDataException("The model-definition table has unsupported framing.");
        int at = 2, records = 0;
        while (true)
        {
            int type = Word(bytes, ref at);
            if (type == -1) break;
            if (++records > 10000) throw new InvalidDataException("The model-definition table exceeds its record limit.");
            _ = Word(bytes, ref at); // The catalogued loader walks fields; the stored record size is not its framing.
            string name = Text(bytes, ref at, 4096);
            int fieldNumber = type == 1 ? 9 : type == 8 ? 2 : -1;
            string? mesh = null;
            int fields = 0;
            while (true)
            {
                if (++fields > 1024) throw new InvalidDataException("A model definition exceeds its field limit.");
                int field = Word(bytes, ref at), length = Word(bytes, ref at);
                if (length is < 0 or > (1 << 20) || length > bytes.Length - at)
                    throw new InvalidDataException("A model-definition field exceeds its bounds.");
                ReadOnlySpan<byte> value = bytes.Slice(at, length);
                at += length;
                int continuation = Word(bytes, ref at);
                if (fieldNumber >= 0 && field == fieldNumber)
                {
                    if (mesh is not null) throw new InvalidDataException("A model definition repeats its mesh field.");
                    int position = 0;
                    mesh = Text(value, ref position, 512);
                    if (position != value.Length) throw new InvalidDataException("A model name has trailing data.");
                }
                if (continuation == -1) break;
                if (continuation != 0) throw new InvalidDataException("A model definition has an invalid continuation.");
            }
            if (fieldNumber >= 0)
            {
                (int, string) key = (type == 8 ? 35 : 8, name);
                if (!_definitions.TryGetValue(key, out List<string?>? values)) _definitions.Add(key, values = []);
                values.Add(mesh);
            }
        }
        if (at != bytes.Length) throw new InvalidDataException("The model-definition table has trailing data.");
    }

    private void ReadArchive(ReadOnlySpan<byte> bytes)
    {
        int at = 0, count = 0;
        while (at < bytes.Length)
        {
            if (++count > 8192 || bytes.Length - at < 8) throw new InvalidDataException("The map resource list exceeds its bounds.");
            bool isMesh = bytes.Slice(at, 4).SequenceEqual("MESH"u8);
            at += 4;
            int size = Word(bytes, ref at);
            if (size < 0 || size > bytes.Length - at) throw new InvalidDataException("A map resource exceeds its bounds.");
            ReadOnlySpan<byte> payload = bytes.Slice(at, size);
            at += size;
            if (!isMesh) continue;
            payload = Unwrap(payload, "PMSH"u8);
            if (payload.Length >= 8 && payload[..4].SequenceEqual("PMS2"u8)) payload = Unwrap(payload, "PMS2"u8);
            if (payload.Length < 309) throw new InvalidDataException("A map model header is incomplete.");
            int nameAt = 0;
            string name = Text(payload[..300], ref nameAt, 300);
            if (name.Length == 0) continue; // Inline models are a separate preview path; never guess a loose filename.
            string key = Key(name);
            if (!_archiveNames.TryGetValue(key, out List<string>? values)) _archiveNames.Add(key, values = []);
            values.Add(name);
        }
    }

    private static ReadOnlySpan<byte> Unwrap(ReadOnlySpan<byte> bytes, ReadOnlySpan<byte> tag)
    {
        if (bytes.Length < 8 || !bytes[..4].SequenceEqual(tag) || BinaryPrimitives.ReadInt32LittleEndian(bytes[4..]) != bytes.Length - 8)
            throw new InvalidDataException("A map model reference has unsupported framing.");
        return bytes[8..];
    }

    private static int Word(ReadOnlySpan<byte> bytes, ref int at)
    {
        if (bytes.Length - at < 4) throw new InvalidDataException("A model-definition word is incomplete.");
        int value = BinaryPrimitives.ReadInt32LittleEndian(bytes[at..]);
        at += 4;
        return value;
    }

    private static string Text(ReadOnlySpan<byte> bytes, ref int at, int maximum)
    {
        int length = bytes[at..].IndexOf((byte)0);
        if (length < 0 || length > maximum) throw new InvalidDataException("A model-definition name is incomplete or too long.");
        ReadOnlySpan<byte> text = bytes.Slice(at, length);
        foreach (byte value in text)
            if (value is < 32 or > 126) throw new InvalidDataException("A model-definition name is not printable ASCII.");
        at += length + 1;
        return Encoding.ASCII.GetString(text);
    }
}
