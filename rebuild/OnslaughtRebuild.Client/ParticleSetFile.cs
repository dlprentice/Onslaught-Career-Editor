// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Text;

namespace OnslaughtRebuild.Client;

/// <summary>
/// The record kinds that appear in the shipped <c>data/ParticleSets/*.par</c>
/// corpus.
///
/// <para>MEASURED 2026-07-28 over all three shipped files
/// (<c>MainSet.par</c> sha256 <c>a51fe441…</c>, <c>Frontend.par</c> sha256
/// <c>01a4c73d…</c>, <c>ModelViewer.par</c> sha256 <c>32d85d1f…</c>, read from
/// <c>local-lab/safe-copy-bea-pristine/data/ParticleSets/</c>): 1,479
/// descriptors across exactly these twelve type ids. Type id <c>3</c> is not
/// used by any shipped descriptor, so the enum deliberately has a hole there
/// rather than inventing a name for it.</para>
///
/// <para>The names are INFERRED from each type's field set and from how the
/// records reference one another. They are labels for our own code; the file
/// itself carries only the integer.</para>
/// </summary>
public enum ParticleDescriptorType
{
    /// <summary>Type 1, 405 records. A textured billboard particle.</summary>
    Sprite = 1,

    /// <summary>Type 2, 338 records. Emits another descriptor over time.</summary>
    Emitter = 2,

    /// <summary>
    /// Type 4, 40 records. Four weighted alternatives
    /// (<c>Particle_Descriptor_0..3</c> with <c>Probability_0..3</c>).
    /// </summary>
    Random = 4,

    /// <summary>Type 5, 97 records. A start/transition/end RGB ramp.</summary>
    ColourRange = 5,

    /// <summary>
    /// Type 6, 258 records. <c>Num_Entries</c> repetitions of
    /// (<c>Particle_Descriptor</c>, <c>Time</c>, <c>Transmit_FoR</c>).
    /// </summary>
    Timeline = 6,

    /// <summary>Type 7, 77 records. A ring/sphere emission volume.</summary>
    Shape = 7,

    /// <summary>Type 8, 100 records. A ribbon/trail.</summary>
    Trail = 8,

    /// <summary>Type 9, 14 records. Gravity plus per-axis rotation.</summary>
    Mover = 9,

    /// <summary>
    /// Type 10, 46 records. A parametric curve used as a modifier on any
    /// <c>float + modifier</c> field.
    /// </summary>
    ParamFunction = 10,

    /// <summary>Type 11, 13 records. A rigid mesh fragment (debris).</summary>
    Mesh = 11,

    /// <summary>Type 12, 24 records. An <c>Initial</c>/<c>Death</c>/<c>Mover</c> triple.</summary>
    System = 12,

    /// <summary>Type 13, 67 records. A cylinder/sphere shell volume.</summary>
    Volume = 13,
}

/// <summary>
/// One authored line of a descriptor, preserved in file order with its raw
/// text. Duplicate keys are legal and common - a <see
/// cref="ParticleDescriptorType.Timeline"/> repeats
/// <c>Particle_Descriptor</c>/<c>Time</c>/<c>Transmit_FoR</c> once per entry -
/// so this is an ordered list, never a dictionary.
/// </summary>
/// <param name="Key">The text before the first space.</param>
/// <param name="Value">
/// The text after the first space, verbatim. <see langword="null"/> only for a
/// line with no space at all; no such line exists in the shipped corpus, and
/// the parser keeps the case so a hand-edited file cannot be silently
/// reshaped.
/// </param>
public readonly record struct ParticleField(string Key, string? Value);

/// <summary>
/// One <c>Particle_Descriptor_Type</c> / <c>Particle_Descriptor_Name</c> record
/// and its authored fields.
/// </summary>
public sealed class ParticleDescriptor
{
    private readonly List<ParticleField> _fields;

    internal ParticleDescriptor(int typeId, string name, List<ParticleField> fields)
    {
        TypeId = typeId;
        Name = name;
        _fields = fields;
    }

    /// <summary>The raw integer after <c>Particle_Descriptor_Type</c>.</summary>
    public int TypeId { get; }

    /// <summary>
    /// <see cref="TypeId"/> as a named kind. An unknown id is returned cast
    /// rather than rejected, because the corpus is authored data and a future
    /// file may legitimately carry a type we have not seen.
    /// </summary>
    public ParticleDescriptorType Type => (ParticleDescriptorType)TypeId;

    /// <summary>The raw text after <c>Particle_Descriptor_Name</c>.</summary>
    public string Name { get; }

    /// <summary>Authored fields in file order, excluding type and name.</summary>
    public IReadOnlyList<ParticleField> Fields => _fields;

    /// <summary>
    /// The verbatim value of the first field with <paramref name="key"/>, or
    /// <see langword="null"/> when the key is absent.
    /// </summary>
    public string? Raw(string key)
    {
        foreach (ParticleField field in _fields)
        {
            if (string.Equals(field.Key, key, StringComparison.Ordinal))
            {
                return field.Value;
            }
        }

        return null;
    }

    /// <summary>Every value authored under <paramref name="key"/>, in order.</summary>
    public IReadOnlyList<string> RawAll(string key)
    {
        List<string> values = [];
        foreach (ParticleField field in _fields)
        {
            if (string.Equals(field.Key, key, StringComparison.Ordinal) &&
                field.Value is not null)
            {
                values.Add(field.Value);
            }
        }

        return values;
    }

    /// <summary>Reads <paramref name="key"/> as an integer.</summary>
    public int Int(string key) =>
        int.Parse(Require(key), NumberStyles.Integer, CultureInfo.InvariantCulture);

    /// <summary>Reads <paramref name="key"/> as an integer, or a default when absent.</summary>
    public int IntOrDefault(string key, int fallback) =>
        Raw(key) is { } value
            ? int.Parse(value, NumberStyles.Integer, CultureInfo.InvariantCulture)
            : fallback;

    /// <summary>Reads <paramref name="key"/> as a float.</summary>
    public float Float(string key) =>
        float.Parse(Require(key), NumberStyles.Float, CultureInfo.InvariantCulture);

    /// <summary>
    /// Reads a <c>float + modifier</c> field. The corpus authors 5,166 of
    /// these; the modifier is either the literal <c>NONE</c> or the name of a
    /// <see cref="ParticleDescriptorType.ParamFunction"/> descriptor, and those
    /// names contain spaces, so the split is on the FIRST space only.
    /// </summary>
    public (float Value, string? Modifier) FloatWithModifier(string key)
    {
        string raw = Require(key);
        int space = raw.IndexOf(' ');
        if (space < 0)
        {
            return (
                float.Parse(raw, NumberStyles.Float, CultureInfo.InvariantCulture),
                null);
        }

        float value = float.Parse(
            raw.AsSpan(0, space), NumberStyles.Float, CultureInfo.InvariantCulture);
        string modifier = raw[(space + 1)..];
        return (value, string.Equals(modifier, "NONE", StringComparison.Ordinal)
            ? null
            : modifier);
    }

    /// <summary>
    /// Reads a bare descriptor-name reference. The literal <c>NONE</c> becomes
    /// <see langword="null"/>.
    /// </summary>
    public string? Reference(string key)
    {
        string? raw = Raw(key);
        return raw is null || string.Equals(raw, "NONE", StringComparison.Ordinal)
            ? null
            : raw;
    }

    private string Require(string key) =>
        Raw(key) ?? throw new InvalidDataException(
            $"Particle descriptor '{Name}' (type {TypeId}) has no '{key}' field.");
}

/// <summary>
/// A decoder for the shipped <c>data/ParticleSets/*.par</c> particle-set files.
///
/// <para><b>Format, MEASURED 2026-07-28</b> from the three shipped files read
/// out of <c>local-lab/safe-copy-bea-pristine/data/ParticleSets/</c>. It is a
/// CRLF-terminated 8-bit text format:</para>
/// <code>
/// ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd
/// File_Version 1.000000
/// Num_Particle_Descriptors &lt;count&gt;
/// Particle_Descriptor_Type &lt;id&gt;
/// Particle_Descriptor_Name &lt;name with spaces&gt;
/// &lt;Key&gt; &lt;value with spaces&gt;
/// ...
/// *****************************************************************   (65 stars)
/// ... one such block per descriptor, each terminated by the star line ...
/// </code>
///
/// <para><b>The decoder is falsifiable and was falsified against the shipped
/// bytes.</b> <see cref="ToBytes"/> re-emits the file and
/// <c>ParticleSetFileTests.ShippedFilesRoundTripByteIdentically</c> asserts the
/// result equals the input byte for byte on all three shipped files, including
/// the 685,194-byte <c>MainSet.par</c>. A parser that merely accepted the input
/// would pass no such check.</para>
///
/// <para><b>Corpus census, MEASURED.</b> 1,479 descriptors (1,405 + 65 + 9),
/// 25,698 record lines of which 22,740 are authored key/value pairs once the
/// type and name lines of each record are excluded, 12 distinct record types,
/// and 3,025 bare name-reference slots.</para>
/// </summary>
public sealed class ParticleSetFile
{
    /// <summary>The 65-character record separator the files actually use.</summary>
    public const string RecordSeparator =
        "*****************************************************************";

    private const string HeaderPrefix = "ParticleSystemEd_File_";
    private const string VersionPrefix = "File_Version ";
    private const string CountPrefix = "Num_Particle_Descriptors ";
    private const string TypePrefix = "Particle_Descriptor_Type ";
    private const string NamePrefix = "Particle_Descriptor_Name ";

    private readonly List<ParticleDescriptor> _descriptors;
    private readonly Dictionary<string, ParticleDescriptor> _byName;

    private ParticleSetFile(
        string header,
        string versionLine,
        int declaredCount,
        List<ParticleDescriptor> descriptors)
    {
        Header = header;
        VersionLine = versionLine;
        DeclaredCount = declaredCount;
        _descriptors = descriptors;
        _byName = new Dictionary<string, ParticleDescriptor>(StringComparer.Ordinal);
        foreach (ParticleDescriptor descriptor in descriptors)
        {
            // Later duplicates lose, which is what a name lookup over a
            // sequentially loaded table does. No shipped file has one.
            _byName.TryAdd(descriptor.Name, descriptor);
        }
    }

    /// <summary>The verbatim first line, including its copyright text.</summary>
    public string Header { get; }

    /// <summary>The verbatim <c>File_Version</c> line.</summary>
    public string VersionLine { get; }

    /// <summary>The count the file declares. All three shipped files are exact.</summary>
    public int DeclaredCount { get; }

    /// <summary>Descriptors in file order.</summary>
    public IReadOnlyList<ParticleDescriptor> Descriptors => _descriptors;

    /// <summary>
    /// Looks a descriptor up by its authored name. Names are matched exactly:
    /// the corpus is case-inconsistent in texture PATHS but not in descriptor
    /// names, and a loose match would silently bind the wrong record.
    /// </summary>
    public ParticleDescriptor? Find(string name) =>
        _byName.TryGetValue(name, out ParticleDescriptor? descriptor)
            ? descriptor
            : null;

    /// <summary>
    /// Looks a descriptor up and throws with the name when it is absent, so a
    /// stale reference names itself rather than turning into a silent no-op.
    /// </summary>
    public ParticleDescriptor Require(string name) =>
        Find(name) ?? throw new InvalidDataException(
            $"Particle set has no descriptor named '{name}'.");

    /// <summary>
    /// Parses a particle-set file from its exact shipped bytes.
    /// </summary>
    /// <remarks>
    /// The shipped files are 8-bit text containing Windows-1252-range bytes
    /// only inside texture paths, so Latin-1 is used: it is the one encoding
    /// that round-trips every byte 0x00-0xFF unchanged, which the byte-identical
    /// re-emission check depends on.
    /// </remarks>
    public static ParticleSetFile Parse(ReadOnlySpan<byte> bytes) =>
        Parse(Latin1.GetString(bytes));

    /// <summary>Parses a particle-set file from decoded text.</summary>
    public static ParticleSetFile Parse(string text)
    {
        ArgumentNullException.ThrowIfNull(text);

        string[] lines = text.Split("\r\n");
        int lineCount = lines.Length;
        if (lineCount > 0 && lines[^1].Length == 0)
        {
            // The shipped files end with a trailing CRLF after the last
            // separator, which Split turns into an empty final element.
            lineCount--;
        }

        if (lineCount < 3)
        {
            throw new InvalidDataException("Particle set file is truncated.");
        }

        if (!lines[0].StartsWith(HeaderPrefix, StringComparison.Ordinal))
        {
            throw new InvalidDataException(
                "Particle set file does not start with a ParticleSystemEd header.");
        }

        if (!lines[1].StartsWith(VersionPrefix, StringComparison.Ordinal))
        {
            throw new InvalidDataException("Particle set file has no File_Version line.");
        }

        if (!lines[2].StartsWith(CountPrefix, StringComparison.Ordinal))
        {
            throw new InvalidDataException(
                "Particle set file has no Num_Particle_Descriptors line.");
        }

        int declaredCount = int.Parse(
            lines[2].AsSpan(CountPrefix.Length),
            NumberStyles.Integer,
            CultureInfo.InvariantCulture);

        List<ParticleDescriptor> descriptors = [];
        List<string> current = [];
        for (int index = 3; index < lineCount; index++)
        {
            string line = lines[index];
            if (!string.Equals(line, RecordSeparator, StringComparison.Ordinal))
            {
                current.Add(line);
                continue;
            }

            descriptors.Add(BuildDescriptor(current));
            current.Clear();
        }

        if (current.Count > 0)
        {
            throw new InvalidDataException(
                "Particle set file has trailing lines after its last record separator.");
        }

        return new ParticleSetFile(lines[0], lines[1], declaredCount, descriptors);
    }

    /// <summary>
    /// Re-emits the file. For every shipped input this returns the input bytes
    /// exactly; see the class remarks.
    /// </summary>
    public byte[] ToBytes() => Latin1.GetBytes(ToText());

    /// <summary>Re-emits the file as text.</summary>
    public string ToText()
    {
        StringBuilder builder = new();
        builder.Append(Header).Append("\r\n");
        builder.Append(VersionLine).Append("\r\n");
        builder.Append(CountPrefix)
            .Append(DeclaredCount.ToString(CultureInfo.InvariantCulture))
            .Append("\r\n");
        foreach (ParticleDescriptor descriptor in _descriptors)
        {
            builder.Append(TypePrefix)
                .Append(descriptor.TypeId.ToString(CultureInfo.InvariantCulture))
                .Append("\r\n");
            builder.Append(NamePrefix).Append(descriptor.Name).Append("\r\n");
            foreach (ParticleField field in descriptor.Fields)
            {
                builder.Append(field.Key);
                if (field.Value is not null)
                {
                    builder.Append(' ').Append(field.Value);
                }

                builder.Append("\r\n");
            }

            builder.Append(RecordSeparator).Append("\r\n");
        }

        return builder.ToString();
    }

    private static Encoding Latin1 => Encoding.Latin1;

    private static ParticleDescriptor BuildDescriptor(List<string> lines)
    {
        if (lines.Count < 2)
        {
            throw new InvalidDataException(
                "Particle descriptor record is missing its type or name line.");
        }

        if (!lines[0].StartsWith(TypePrefix, StringComparison.Ordinal))
        {
            throw new InvalidDataException(
                $"Particle descriptor record does not start with a type: '{lines[0]}'.");
        }

        if (!lines[1].StartsWith(NamePrefix, StringComparison.Ordinal))
        {
            throw new InvalidDataException(
                $"Particle descriptor record has no name line: '{lines[1]}'.");
        }

        int typeId = int.Parse(
            lines[0].AsSpan(TypePrefix.Length),
            NumberStyles.Integer,
            CultureInfo.InvariantCulture);
        string name = lines[1][NamePrefix.Length..];

        List<ParticleField> fields = new(lines.Count - 2);
        for (int index = 2; index < lines.Count; index++)
        {
            string line = lines[index];
            int space = line.IndexOf(' ');
            fields.Add(space < 0
                ? new ParticleField(line, null)
                : new ParticleField(line[..space], line[(space + 1)..]));
        }

        return new ParticleDescriptor(typeId, name, fields);
    }
}
