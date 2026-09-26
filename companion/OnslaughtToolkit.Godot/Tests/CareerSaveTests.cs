// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Career codec contracts. The caller supplies bytes read from its own copy of the real
/// tracked baseline; every mutation below happens in memory and no save file is created.
/// Offsets are written as literals so the checks do not reuse the codec's own layout.
/// </summary>
internal static class CareerSaveTests
{
    internal static void Run(byte[] original, Checks check)
    {
        check.Suite("career codec");
        byte[] untouched = original.ToArray();
        Outcome<CareerInspection> opened = CareerSave.Inspect(original);
        check.That(opened.Ok, "The owned real baseline must be recognized.");
        if (opened.Value is not CareerInspection info) return;
        check.That(info.Size == 10004 && info.Version == 0x4BD1, "Exact baseline size and version word.");
        check.That(info.Kills.Count == 5 && info.Missions.Count == 100, "Expected inspection record counts.");
        check.That(info.Goodies.Count == 300 && info.GoodieCensus.Reserved == 67,
            "Reserved Goodie slots remain distinguishable.");
        ByteComparison same = CareerSave.Compare(original, original.ToArray());
        check.That(same.Equal && same.ChangedBytes == 0 && same.Ranges.Count == 0,
            "No-edit round trip is byte-for-byte identical.");

        for (int category = 0; category < 5; category++)
        {
            foreach (int target in new[] { 0, 1, 0x00FFFFFF })
            {
                if (target == info.Kills[category]) continue;
                Outcome<EditPlan> result = CareerSave.Preview(original, new Dictionary<int, int> { [category] = target });
                check.That(result.Ok, $"Category {category} accepts boundary {target}.");
                if (result.Value is not EditPlan plan) continue;
                byte[] output = plan.CopyBytes();
                check.That(output.Length == 10004, "Preview preserves exact file length.");
                int first = 0x23F6 + category * 4;
                int decoded = output[first] | (output[first + 1] << 8) | (output[first + 2] << 16);
                check.That(decoded == target, $"Independent intended count check for category {category}.");
                bool allowed = true;
                int changed = 0;
                for (int offset = 0; offset < original.Length; offset++)
                {
                    if (original[offset] == output[offset]) continue;
                    changed++;
                    if (offset < first || offset >= first + 3) allowed = false;
                }
                check.That(allowed && changed > 0 && changed <= 3,
                    "Every unselected/unknown byte survives, including the packed high byte.");
                check.That(plan.ChangedBytes == changed, "Preview describes the actual byte diff.");
                check.That(CareerSave.Inspect(output).Value?.Kills[category] == target,
                    "Result reinspection agrees with the independent check.");
                output[0] ^= 0x01;
                check.That(original.AsSpan().SequenceEqual(untouched), "Mutating returned output cannot mutate the original.");
                check.That(plan.CopyBytes()[0] == untouched[0], "Mutating returned output cannot mutate the plan.");
            }
        }

        Dictionary<int, int> allSelected = [];
        for (int category = 0; category < 5; category++)
            allSelected[category] = (info.Kills[category] + 257) & 0xFFFFFF;
        Outcome<EditPlan> combined = CareerSave.Preview(original, allSelected);
        check.That(combined.Ok && combined.Value!.Selected.Count == 5, "All five explicit category selections compose.");
        if (combined.Value is EditPlan all)
        {
            byte[] output = all.CopyBytes();
            bool allAllowed = true;
            for (int offset = 0; offset < original.Length; offset++)
            {
                if (original[offset] != output[offset] &&
                    (offset < 0x23F6 || offset >= 0x240A || (offset - 0x23F6) % 4 == 3))
                    allAllowed = false;
            }
            check.That(allAllowed, "Combined edits preserve every byte outside the selected low 24-bit fields.");
            for (int category = 0; category < 5; category++)
            {
                int first = 0x23F6 + category * 4;
                int decoded = output[first] | (output[first + 1] << 8) | (output[first + 2] << 16);
                check.That(decoded == allSelected[category], "Combined selection applies every intended count.");
            }
        }

        // Typed selections make GDScript's string-key, float and bool cases unrepresentable;
        // every representable invalid or unchanged selection must still be refused.
        Dictionary<int, int>[] invalid =
        [
            [], new() { [-1] = 1 }, new() { [5] = 1 }, new() { [0] = -1 }, new() { [0] = 0x01000000 },
            new() { [0] = info.Kills[0] },
            new() { [0] = 1, [1] = 1, [2] = 1, [3] = 1, [4] = 1, [5] = 1 },
        ];
        foreach (Dictionary<int, int> selection in invalid)
        {
            check.That(!CareerSave.Preview(original, selection).Ok,
                $"Invalid or unchanged selection is refused: {Describe(selection)}");
        }
        Dictionary<int, int> mixedUnchanged = new()
        {
            [0] = info.Kills[0], [1] = (info.Kills[1] + 1) & 0xFFFFFF,
        };
        check.That(!CareerSave.Preview(original, mixedUnchanged).Ok,
            "An unchanged explicit selection is not silently ignored in a mixed plan.");

        byte[] wrongVersion = original.ToArray();
        wrongVersion[0] ^= 1;
        check.That(!CareerSave.Inspect(wrongVersion).Ok && !CareerSave.Preview(wrongVersion, One()).Ok,
            "Bad version is refused before inspection/preview.");
        byte[] shortBytes = original[..^1];
        byte[] longBytes = [.. original, 0];
        foreach (byte[] malformed in new[] { Array.Empty<byte>(), shortBytes, longBytes })
        {
            check.That(!CareerSave.Inspect(malformed).Ok && !CareerSave.Preview(malformed, One()).Ok,
                "Incorrect lengths cannot be edited.");
        }
        byte[] changedHeader = original.ToArray();
        changedHeader[2] ^= 0x80;
        check.That(CareerSave.Inspect(changedHeader).Ok, "Only the 16-bit version is magic; career header bytes are not magic.");
        ByteComparison tail = CareerSave.Compare(original, shortBytes);
        check.That(!tail.Equal && !tail.SameLength && tail.ChangedBytes == 1, "Comparison counts a missing trailing byte.");
        check.That(tail.Changes.Count == 1 && tail.Changes[0].Offset == 10003 && tail.Changes[0].After == ByteComparison.MissingByte,
            "Missing bytes use an explicit sentinel, not an invented zero.");

        // Alter an owned in-memory baseline to exercise mixed known/unknown state handling.
        byte[] mixedLinks = original.ToArray();
        for (int index = 0; index < 200; index++)
            BinaryPrimitives.WriteUInt32LittleEndian(mixedLinks.AsSpan(0x1906 + index * 8 + 4), 0xFFFFFFFF);
        uint[] states = [0, 1, 2, 99];
        for (int index = 0; index < 4; index++)
        {
            BinaryPrimitives.WriteUInt32LittleEndian(mixedLinks.AsSpan(0x1906 + index * 8), states[index]);
            BinaryPrimitives.WriteUInt32LittleEndian(mixedLinks.AsSpan(0x1906 + index * 8 + 4), (uint)index);
        }
        LinkCensus? census = CareerSave.Inspect(mixedLinks).Value?.LinkCensus;
        check.That(census is { Used: 4, Locked: 1, Complete: 1, AlternateRoutes: 1, Unknown: 1 },
            "Alternate-route and unknown links are not counted as complete, and destination zero is used.");
        byte[] mixedGoodies = original.ToArray();
        BinaryPrimitives.WriteUInt32LittleEndian(mixedGoodies.AsSpan(0x1F46 + 232 * 4), 99);
        BinaryPrimitives.WriteUInt32LittleEndian(mixedGoodies.AsSpan(0x1F46 + 233 * 4), 2);
        CareerInspection? goodieInfo = CareerSave.Inspect(mixedGoodies).Value;
        check.That(goodieInfo?.Goodies[232].State == GoodieState.Unknown && goodieInfo.Goodies[233].State == GoodieState.Reserved,
            "Reserved slots are never presented as earned/unlocked.");
        byte[] unusual = original.ToArray();
        BinaryPrimitives.WriteUInt32LittleEndian(unusual.AsSpan(0x0006 + 0x3C), 0x3FC00000); // 1.5
        BinaryPrimitives.WriteUInt32LittleEndian(unusual.AsSpan(0x0006 + 0x40 + 0x3C), 0x7FC00000); // NaN
        BinaryPrimitives.WriteUInt32LittleEndian(unusual.AsSpan(0x248E), 0x7F800000);
        CareerInspection? unusualInfo = CareerSave.Inspect(unusual).Value;
        check.That(unusualInfo is not null && unusualInfo.Missions[0].RankLetter is null && unusualInfo.Missions[1].RankLetter == "S"
            && !unusualInfo.SoundVolume.Finite,
            "A stored rank above 1 has no letter, NaN reads as S like the game's rule, and a nonfinite volume stays visible.");

        // The game's rank rule: exactly 1.0 or NaN is S, zero or below E, otherwise 'D' - floor(4f).
        (float Value, string? Letter)[] ranks =
        [
            (1.0f, "S"), (float.NaN, "S"), (0f, "E"), (-1f, "E"), (float.NegativeInfinity, "E"),
            (0.75f, "A"), (0.9999999f, "A"), (0.7499999f, "B"), (0.5f, "B"), (0.4999999f, "C"), (0.25f, "C"),
            (0.2499999f, "D"), (0.0000001f, "D"), (1.0000001f, null), (1.5f, null), (float.PositiveInfinity, null),
            (0.8f, "A"), (0.6f, "B"), (0.35f, "C"), (0.15f, "D"),
        ];
        foreach ((float value, string? letter) in ranks)
            check.That(CareerSave.RankLetter(value) == letter, $"Rank {value:R} reads as {letter ?? "no letter"}.");
        check.That(info.PendingGoodiesRaw == BinaryPrimitives.ReadUInt32LittleEndian(original.AsSpan(0x0002)),
            "The pending extra Goodies dword is read from offset 0x0002.");
        check.That(CareerSave.RegionOf(0x0006 + 0x40 + 0x14) == "Surviving base buildings" && CareerSave.RegionOf(0x0006 + 0x40 + 0x37) ==
            "Surviving base buildings" && CareerSave.RegionOf(0x0006 + 0x40 + 0x38) == "Mission records",
            "A node's base-building bitmap is named apart from its mission fields.");
        check.That(CareerSave.RegionOf(0x0002) == "Pending extra Goodies" && CareerSave.RegionOf(0x0006) == "Mission records",
            "Byte regions name the pending Goodies dword.");
        GoodieEdits(original, info, check);
        check.That(original.AsSpan().SequenceEqual(untouched),
            "Inspection, previews and malformed-input checks never mutate the baseline.");
    }

    /// <summary>A Goodie edit changes exactly its own four bytes; reserved slots and other states are refused.</summary>
    private static void GoodieEdits(byte[] original, CareerInspection info, Checks check)
    {
        Dictionary<int, int> noKills = [];
        foreach (int index in new[] { 0, 2, 5, 232 })
        {
            foreach (GoodieState target in new[] { GoodieState.Locked, GoodieState.Hint, GoodieState.New, GoodieState.Old })
            {
                int offset = 0x1F46 + index * 4;
                uint before = BinaryPrimitives.ReadUInt32LittleEndian(original.AsSpan(offset));
                uint value = target switch { GoodieState.Locked => 0u, GoodieState.Hint => 1u, GoodieState.New => 2u, _ => 3u };
                Outcome<EditPlan> plan = CareerSave.Preview(original, new EditRequest(noKills, new Dictionary<int, GoodieState> { [index] = target }));
                if (before == value)
                {
                    check.That(!plan.Ok, $"Goodie {index} already {target} is refused as unchanged.");
                    continue;
                }
                check.That(plan.Ok, $"Goodie {index} can become {target}.");
                if (plan.Value is not EditPlan edit) continue;
                byte[] output = edit.CopyBytes();
                bool confined = true;
                for (int at = 0; at < original.Length; at++)
                {
                    if (output[at] != original[at] && (at < offset || at >= offset + 4)) confined = false;
                }
                check.That(confined && BinaryPrimitives.ReadUInt32LittleEndian(output.AsSpan(offset)) == value &&
                    edit.Goodies.Count == 1 && edit.Goodies[0].Before == before, $"Goodie {index} → {target} changes only its own dword.");
            }
        }
        foreach (int index in new[] { -1, 233, 299, 300 })
        {
            check.That(!CareerSave.Preview(original, new EditRequest(noKills, new Dictionary<int, GoodieState> { [index] = GoodieState.New })).Ok,
                $"Goodie slot {index} cannot change.");
        }
        foreach (GoodieState target in new[] { GoodieState.Unknown, GoodieState.Reserved })
        {
            check.That(!CareerSave.Preview(original, new EditRequest(noKills, new Dictionary<int, GoodieState> { [3] = target })).Ok,
                $"A Goodie cannot be set to {target}.");
        }
        check.That(!CareerSave.Preview(original, new EditRequest(noKills, new Dictionary<int, GoodieState>())).Ok, "An empty request is refused.");
        int newAircraft = (info.Kills[0] + 1) & 0xFFFFFF;
        GoodieState flipped = info.Goodies[7].State == GoodieState.Locked ? GoodieState.New : GoodieState.Locked;
        Outcome<EditPlan> combined = CareerSave.Preview(original,
            new EditRequest(new Dictionary<int, int> { [0] = newAircraft }, new Dictionary<int, GoodieState> { [7] = flipped }));
        check.That(combined.Value is { Selected.Count: 1, Goodies.Count: 1 } && CareerSave.Inspect(combined.Value.CopyBytes()).Value is
            CareerInspection after && after.Kills[0] == newAircraft && after.Goodies[7].State == flipped,
            "A kill count and a Goodie state compose in one copy.");
    }

    private static Dictionary<int, int> One() => new() { [0] = 1 };

    private static string Describe(Dictionary<int, int> selection) =>
        "{" + string.Join(", ", selection.Select(pair => $"{pair.Key}: {pair.Value}")) + "}";
}
