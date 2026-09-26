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
        check.That(census is { Used: 4, Locked: 1, Complete: 1, Broken: 1, Unknown: 1 },
            "Broken/unknown links are not counted as complete, and destination zero is used.");
        byte[] mixedGoodies = original.ToArray();
        BinaryPrimitives.WriteUInt32LittleEndian(mixedGoodies.AsSpan(0x1F46 + 232 * 4), 99);
        BinaryPrimitives.WriteUInt32LittleEndian(mixedGoodies.AsSpan(0x1F46 + 233 * 4), 2);
        CareerInspection? goodieInfo = CareerSave.Inspect(mixedGoodies).Value;
        check.That(goodieInfo?.Goodies[232].State == GoodieState.Unknown && goodieInfo.Goodies[233].State == GoodieState.Reserved,
            "Reserved slots are never presented as earned/unlocked.");
        byte[] unusual = original.ToArray();
        BinaryPrimitives.WriteUInt32LittleEndian(unusual.AsSpan(0x0006 + 0x3C), 0x7FC00000);
        BinaryPrimitives.WriteUInt32LittleEndian(unusual.AsSpan(0x248E), 0x7F800000);
        CareerInspection? unusualInfo = CareerSave.Inspect(unusual).Value;
        check.That(unusualInfo is not null && !unusualInfo.Missions[0].RankKnown && !unusualInfo.SoundVolume.Finite,
            "Unmapped rank and nonfinite stored volume remain visible as unsupported values.");
        check.That(original.AsSpan().SequenceEqual(untouched),
            "Inspection, previews and malformed-input checks never mutate the baseline.");
    }

    private static Dictionary<int, int> One() => new() { [0] = 1 };

    private static string Describe(Dictionary<int, int> selection) =>
        "{" + string.Join(", ", selection.Select(pair => $"{pair.Key}: {pair.Value}")) + "}";
}
