// SPDX-License-Identifier: MIT
using System.Buffers.Binary;

namespace OnslaughtToolkit.Companion.Careers;

/// <summary>A domain result: success with a value, or a refusal that names what to do next.</summary>
public readonly record struct Outcome<T>(bool Ok, string Message, T? Value) where T : class
{
    public static Outcome<T> Success(T value, string message) => new(true, message, value);
    public static Outcome<T> Refusal(string message) => new(false, message, null);
}

/// <summary>
/// The companion's career byte codec. It performs no filesystem operations. Layout facts come
/// from the MIT AppCore BesFilePatcher and its tests, not the GPL rebuild. Recognizing the
/// container proves neither that the game generated the bytes nor that it will accept them.
/// </summary>
public static class CareerSave
{
    public const int Size = 10004;
    public const int VersionWord = 0x4BD1;
    public const int MaxKills = 0x00FFFFFF;
    public const int MissionOffset = 0x0006, MissionStride = 64, MissionCount = 100;
    public const int LinkOffset = 0x1906, LinkStride = 8, LinkCount = 200;
    public const int GoodieOffset = 0x1F46, GoodieSlots = 300, DisplayableGoodies = 233;
    public const int KillsOffset = 0x23F6;
    public const int TechOffset = 0x240A, TechSlotCount = 32;
    public const int CareerInProgressOffset = 0x248A, SoundVolumeOffset = 0x248E;
    public const int MusicVolumeOffset = 0x2492, GodModeOffset = 0x2496, OptionsOffset = 0x24BE;
    public const uint UnusedLink = 0xFFFFFFFF;

    public static IReadOnlyList<string> CategoryNames { get; } = ["Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs"];

    private static readonly Dictionary<uint, string> RankNames = new()
    {
        [0x3F800000] = "S", [0x3F4CCCCD] = "A", [0x3F19999A] = "B",
        [0x3EB33333] = "C", [0x3E19999A] = "D", [0x00000000] = "E", [0xBF800000] = "None",
    };

    public static IReadOnlyList<string> Notes { get; } =
    [
        "The version word and length recognize this container; they do not prove its origin or gameplay validity.",
        "Packed bytes above the five kill counts are preserved. The first two store screen-position data; the other three have no known consumer.",
        "Reserved Goodie slots 233–299, unmapped rank values, options and all unselected bytes remain unchanged.",
        "Raw tech slots and god-mode state are inspection only. A save flag does not establish active game cheats.",
        "Stored sound/music values do not establish the settings that a running game will apply.",
    ];

    public static string RankName(uint bits) => RankNames.GetValueOrDefault(bits, "Unmapped");

    public static bool IsKnownRank(uint bits) => RankNames.ContainsKey(bits);

    public static Outcome<CareerInspection> Inspect(ReadOnlySpan<byte> bytes)
    {
        if (Validate(bytes) is string refusal) return Outcome<CareerInspection>.Refusal(refusal);
        int[] kills = new int[CategoryNames.Count];
        int[] packed = new int[CategoryNames.Count];
        for (int category = 0; category < kills.Length; category++)
        {
            uint raw = U32(bytes, KillsOffset + category * 4);
            kills[category] = (int)(raw & MaxKills);
            packed[category] = (int)(raw >> 24);
        }
        MissionRecord[] missions = new MissionRecord[MissionCount];
        for (int index = 0; index < MissionCount; index++)
        {
            int offset = MissionOffset + index * MissionStride;
            missions[index] = new MissionRecord(index, offset, U32(bytes, offset + 0x10), U32(bytes, offset + 0x04),
                U32(bytes, offset + 0x38), U32(bytes, offset + 0x3C), BinaryPrimitives.ReadSingleLittleEndian(bytes[(offset + 0x3C)..]));
        }
        LinkRecord[] links = new LinkRecord[LinkCount];
        for (int index = 0; index < LinkCount; index++)
        {
            int offset = LinkOffset + index * LinkStride;
            links[index] = new LinkRecord(index, offset, U32(bytes, offset), U32(bytes, offset + 4));
        }
        GoodieRecord[] goodies = new GoodieRecord[GoodieSlots];
        for (int index = 0; index < GoodieSlots; index++)
        {
            int offset = GoodieOffset + index * 4;
            goodies[index] = new GoodieRecord(index, offset, U32(bytes, offset));
        }
        uint[] tech = new uint[TechSlotCount];
        for (int index = 0; index < TechSlotCount; index++) tech[index] = U32(bytes, TechOffset + index * 4);
        CareerInspection inspection = new()
        {
            Size = bytes.Length,
            Version = BinaryPrimitives.ReadUInt16LittleEndian(bytes),
            Kills = kills,
            PackedBytes = packed,
            Missions = missions,
            MissionCensus = new MissionCensus(
                missions.Count(record => record.Used), missions.Count(record => record.Completed),
                missions.Count(record => record.Used && !record.Completed), missions.Count(record => !record.Used)),
            Links = links,
            LinkCensus = new LinkCensus(
                links.Count(record => record.Used), Count(links, LinkState.Locked), Count(links, LinkState.Complete),
                Count(links, LinkState.Broken), Count(links, LinkState.Unknown), Count(links, LinkState.Unused)),
            Goodies = goodies,
            GoodieCensus = new GoodieCensus(DisplayableGoodies,
                Count(goodies, GoodieState.Locked), Count(goodies, GoodieState.Hint), Count(goodies, GoodieState.New),
                Count(goodies, GoodieState.Old), Count(goodies, GoodieState.Unknown), Count(goodies, GoodieState.Reserved)),
            TechSlots = tech,
            CareerInProgressRaw = U32(bytes, CareerInProgressOffset),
            GodModeRaw = U32(bytes, GodModeOffset),
            SoundVolume = StoredFloat.Read(bytes, SoundVolumeOffset),
            MusicVolume = StoredFloat.Read(bytes, MusicVolumeOffset),
        };
        return Outcome<CareerInspection>.Success(inspection,
            "Supported career container. Unselected and unknown bytes are preserved.");
    }

    /// <summary>
    /// Plans a copy with explicitly selected kill counts. Exactly the low three bytes of each
    /// selected category may change; the packed fourth byte is never authored.
    /// </summary>
    public static Outcome<EditPlan> Preview(ReadOnlySpan<byte> original, IReadOnlyDictionary<int, int> selections)
    {
        if (Validate(original) is string refusal) return Outcome<EditPlan>.Refusal(refusal);
        if (selections.Count == 0 || selections.Count > CategoryNames.Count)
            return Outcome<EditPlan>.Refusal("Select between one and five kill categories explicitly.");
        foreach ((int category, int count) in selections)
        {
            if (category < 0 || category >= CategoryNames.Count)
                return Outcome<EditPlan>.Refusal("A kill category must be a number from 0 to 4.");
            if (count < 0 || count > MaxKills)
                return Outcome<EditPlan>.Refusal("Kill counts must be whole numbers from 0 to 16,777,215.");
            if ((U32(original, KillsOffset + category * 4) & MaxKills) == count)
                return Outcome<EditPlan>.Refusal(
                    $"The selected {CategoryNames[category]} count is unchanged. Remove that selection or choose a different count.");
        }
        byte[] output = original.ToArray();
        List<KillEdit> selected = [];
        foreach ((int category, int count) in selections.OrderBy(pair => pair.Key))
        {
            int offset = KillsOffset + category * 4;
            for (int index = 0; index < 3; index++) output[offset + index] = (byte)((count >> (index * 8)) & 0xFF);
            selected.Add(new KillEdit(category, CategoryNames[category], offset,
                (int)(U32(original, offset) & MaxKills), count));
        }
        ByteComparison difference = Compare(original, output);
        return Outcome<EditPlan>.Success(new EditPlan(output, difference.Changes, selected),
            "Preview only. No file has been written.");
    }

    public static ByteComparison Compare(ReadOnlySpan<byte> left, ReadOnlySpan<byte> right)
    {
        List<ByteChange> changes = [];
        List<ByteRange> ranges = [];
        Dictionary<string, int> regions = [];
        int rangeStart = -1;
        int maximum = Math.Max(left.Length, right.Length);
        for (int offset = 0; offset < maximum; offset++)
        {
            int before = offset < left.Length ? left[offset] : ByteComparison.MissingByte;
            int after = offset < right.Length ? right[offset] : ByteComparison.MissingByte;
            if (before != after)
            {
                changes.Add(new ByteChange(offset, before, after));
                string region = RegionOf(offset);
                regions[region] = regions.GetValueOrDefault(region) + 1;
                if (rangeStart == -1) rangeStart = offset;
            }
            else if (rangeStart != -1)
            {
                ranges.Add(new ByteRange(rangeStart, offset - 1));
                rangeStart = -1;
            }
        }
        if (rangeStart != -1) ranges.Add(new ByteRange(rangeStart, maximum - 1));
        return new ByteComparison(left.Length, right.Length, changes, ranges, regions);
    }

    public static string RegionOf(int offset) => offset switch
    {
        < 0x0002 => "Version word",
        < MissionOffset => "Career header",
        < LinkOffset => "Mission records",
        < GoodieOffset => "Campaign links",
        < KillsOffset => offset < GoodieOffset + DisplayableGoodies * 4 ? "Goodie states" : "Reserved Goodie slots",
        < TechOffset => (offset - KillsOffset) % 4 == 3 ? "Packed kill bytes" : "Kill counts",
        < CareerInProgressOffset => "Raw tech slots",
        < OptionsOffset => "Career settings",
        < Size => "Stored options",
        _ => "Outside supported length",
    };

    private static string? Validate(ReadOnlySpan<byte> bytes)
    {
        if (bytes.Length != Size)
            return $"Unsupported length: {bytes.Length:N0} bytes. A supported career contains exactly 10,004 bytes.";
        int version = BinaryPrimitives.ReadUInt16LittleEndian(bytes);
        return version == VersionWord ? null : $"Unsupported version word 0x{version:X4}; expected 0x4BD1.";
    }

    internal static uint U32(ReadOnlySpan<byte> bytes, int offset) => BinaryPrimitives.ReadUInt32LittleEndian(bytes[offset..]);

    private static int Count(IEnumerable<LinkRecord> records, LinkState state) => records.Count(record => record.State == state);

    private static int Count(IEnumerable<GoodieRecord> records, GoodieState state) => records.Count(record => record.State == state);
}

/// <summary>An immutable read of every interpreted career region. Raw values stay visible.</summary>
public sealed class CareerInspection
{
    public required int Size { get; init; }
    public required int Version { get; init; }
    public required IReadOnlyList<int> Kills { get; init; }
    public required IReadOnlyList<int> PackedBytes { get; init; }
    public required IReadOnlyList<MissionRecord> Missions { get; init; }
    public required MissionCensus MissionCensus { get; init; }
    public required IReadOnlyList<LinkRecord> Links { get; init; }
    public required LinkCensus LinkCensus { get; init; }
    public required IReadOnlyList<GoodieRecord> Goodies { get; init; }
    public required GoodieCensus GoodieCensus { get; init; }
    public required IReadOnlyList<uint> TechSlots { get; init; }
    public required uint CareerInProgressRaw { get; init; }
    public required uint GodModeRaw { get; init; }
    public required StoredFloat SoundVolume { get; init; }
    public required StoredFloat MusicVolume { get; init; }
}

public sealed record MissionRecord(int Index, int Offset, uint World, uint CompleteRaw, uint Attempts, uint RankBits, float RankValue)
{
    public bool Used => World != 0;
    public bool Completed => Used && CompleteRaw != 0;
    public string Rank => CareerSave.RankName(RankBits);
    public bool RankKnown => CareerSave.IsKnownRank(RankBits);
}

public sealed record MissionCensus(int Used, int Completed, int Incomplete, int Unused);

public enum LinkState { Unused, Locked, Complete, Broken, Unknown }

public sealed record LinkRecord(int Index, int Offset, uint RawState, uint ToNode)
{
    public bool Used => ToNode != CareerSave.UnusedLink;

    public LinkState State => !Used ? LinkState.Unused : RawState switch
    {
        0 => LinkState.Locked,
        1 => LinkState.Complete,
        2 => LinkState.Broken,
        _ => LinkState.Unknown,
    };
}

public sealed record LinkCensus(int Used, int Locked, int Complete, int Broken, int Unknown, int Unused);

public enum GoodieState { Locked, Hint, New, Old, Unknown, Reserved }

public sealed record GoodieRecord(int Index, int Offset, uint RawState)
{
    public bool Reserved => Index >= CareerSave.DisplayableGoodies;

    public GoodieState State => Reserved ? GoodieState.Reserved : RawState switch
    {
        0 => GoodieState.Locked,
        1 => GoodieState.Hint,
        2 => GoodieState.New,
        3 => GoodieState.Old,
        _ => GoodieState.Unknown,
    };
}

public sealed record GoodieCensus(int Displayable, int Locked, int Hint, int New, int Old, int Unknown, int Reserved);

public sealed record StoredFloat(int Offset, uint RawBits, float Value)
{
    public bool Finite => float.IsFinite(Value);

    internal static StoredFloat Read(ReadOnlySpan<byte> bytes, int offset) =>
        new(offset, CareerSave.U32(bytes, offset), BinaryPrimitives.ReadSingleLittleEndian(bytes[offset..]));
}

public sealed record KillEdit(int Category, string Name, int Offset, int Before, int After);

/// <summary>A previewed copy. Its bytes are private; callers receive copies.</summary>
public sealed class EditPlan
{
    private readonly byte[] _bytes;

    internal EditPlan(byte[] bytes, IReadOnlyList<ByteChange> changes, IReadOnlyList<KillEdit> selected)
        => (_bytes, Changes, Selected) = (bytes, changes, selected);

    public IReadOnlyList<ByteChange> Changes { get; }
    public IReadOnlyList<KillEdit> Selected { get; }
    public int ChangedBytes => Changes.Count;
    public string Summary => $"{Selected.Count} selected categories; {ChangedBytes} changed bytes; all other bytes preserved.";

    public byte[] CopyBytes() => _bytes.ToArray();
}

/// <summary>One differing offset. A byte beyond the end of a shorter file is <see cref="ByteComparison.MissingByte"/>.</summary>
public sealed record ByteChange(int Offset, int Before, int After);

public sealed record ByteRange(int Start, int End)
{
    public int Length => End - Start + 1;
}

public sealed class ByteComparison(int leftSize, int rightSize, IReadOnlyList<ByteChange> changes,
    IReadOnlyList<ByteRange> ranges, IReadOnlyDictionary<string, int> regions)
{
    public const int MissingByte = -1;

    public int LeftSize { get; } = leftSize;
    public int RightSize { get; } = rightSize;
    public IReadOnlyList<ByteChange> Changes { get; } = changes;
    public IReadOnlyList<ByteRange> Ranges { get; } = ranges;
    public IReadOnlyDictionary<string, int> Regions { get; } = regions;
    public int ChangedBytes => Changes.Count;
    public bool Equal => Changes.Count == 0;
    public bool SameLength => LeftSize == RightSize;

    public string Summary => Equal
        ? $"Byte-for-byte identical ({LeftSize:N0} bytes)."
        : $"{ChangedBytes:N0} changed bytes across {Ranges.Count:N0} ranges; length {LeftSize:N0} → {RightSize:N0} bytes.";
}
