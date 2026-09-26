// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Options codec contracts on the real fixture's options block; offsets are written as literals.</summary>
internal static class OptionsTests
{
    internal static void Run(byte[] original, Checks check)
    {
        check.Suite("options");
        if (OptionsFile.Read(original).Value is not OptionsReading read)
        {
            check.Fail("The fixture's options block must read.");
            return;
        }
        check.That(Math.Abs(read.SoundVolume - F(original, 0x248E)) < 1e-6 && Math.Abs(read.MusicVolume - F(original, 0x2492)) < 1e-6,
            "Volumes read from 0x248E and 0x2492.");
        check.That(read.Bindings.Count == 16 && read.Bindings.All(row => row.Offset == 0x24BE + row.Row * 0x20) &&
            read.Bindings.Select(row => row.EntryId).Distinct().Count() == 16, "Sixteen binding rows with distinct ids.");
        check.That(read.MouseSensitivity == F(original, 0x26BE + 4) && read.ScreenShape == U(original, 0x26BE + 0x20),
            "Mouse sensitivity and screen shape read from the tail.");
        foreach (BindingAction action in OptionsFile.Actions)
            check.That(read.Bindings.Any(row => row.EntryId == action.EntryId), $"The fixture has a row for {action.Name}.");

        Only(original, Edit(edit => edit.MusicVolume = read.MusicVolume > 0.5f ? 0.25f : 0.75f), [0x2492], check, "music volume");
        Only(original, Edit(edit => edit.SoundVolume = read.SoundVolume > 0.5f ? 0.25f : 0.75f), [0x248E], check, "sound volume");
        Only(original, Edit(edit => edit.InvertFlight[1] = !read.InvertFlight[1]), [0x24A2], check, "player 2 flight invert");
        Only(original, Edit(edit => edit.InvertWalker[0] = !read.InvertWalker[0]), [0x24A6], check, "player 1 walker invert");
        Only(original, Edit(edit => edit.Vibration[1] = !read.Vibration[1]), [0x24B2], check, "player 2 vibration");
        Only(original, Edit(edit => edit.ControllerPreset[0] = read.ControllerPreset[0] == 3 ? 2u : 3u), [0x24B6], check, "player 1 preset");
        Only(original, Edit(edit => edit.MouseSensitivity = read.MouseSensitivity == 63f ? 3f : 63f), [0x26C2], check, "mouse sensitivity");
        Only(original, Edit(edit => edit.ScreenShape = read.ScreenShape == 1 ? 0u : 1u), [0x26DE], check, "screen shape");

        KeyChoice t = KeyTable.For(Key.T)!;
        int transform = read.Bindings.Single(row => row.EntryId == 0x21).Offset;
        OptionsEdit keyEdit = Edit(edit => edit.Keys[(0x21, 1)] = t);
        Only(original, keyEdit, [transform + 0x18, transform + 0x1C], check, "player 2 transform key");
        if (OptionsFile.Preview(original, keyEdit).Value is OptionsPlan plan)
        {
            check.That(U(plan.Bytes, transform + 0x18) == 8 && U(plan.Bytes, transform + 0x1C) == (('T' << 16) | 0x14u) &&
                U(plan.Bytes, transform) == U(original, transform) && U(plan.Bytes, transform + 4) == 0x21,
                "A key is stored as (character << 16) | scan with the action's keyboard device; flags and id stay.");
        }
        KeyChoice f = KeyTable.For(Key.F)!;
        int fire = read.Bindings.Single(row => row.EntryId == 0x12).Offset, fireMirror = read.Bindings.Single(row => row.EntryId == 0x13).Offset;
        if (OptionsFile.Preview(original, Edit(edit => edit.Keys[(0x12, 0)] = f)).Value is OptionsPlan firePlan)
        {
            check.That(U(firePlan.Bytes, fire + 0x0C) == 10 && U(firePlan.Bytes, fireMirror + 0x0C) == 9 &&
                U(firePlan.Bytes, fire + 0x10) == f.Packed && U(firePlan.Bytes, fireMirror + 0x10) == f.Packed,
                "Fire weapon's key is mirrored into the game's second Fire row.");
        }
        else
        {
            check.Fail("A Fire key edit must plan.");
        }
        byte[] preset = original.ToArray();
        BinaryPrimitives.WriteUInt16LittleEndian(preset.AsSpan(0x26BE + 8), 1);
        check.That(OptionsFile.Preview(preset, keyEdit).Value is OptionsPlan custom && BinaryPrimitives.ReadUInt16LittleEndian(custom.Bytes.AsSpan(0x26BE + 8)) == 0,
            "Changing a key sets the control scheme to custom so the game keeps it.");
        check.That(KeyTable.For(Key.W)?.Packed == U(original, read.Bindings.Single(row => row.EntryId == 0x1F).Offset + 0x1C) ||
            read.Bindings.Single(row => row.EntryId == 0x1F).Slot1Device != 9, "The key table packs W the way the game wrote it.");

        foreach ((string name, OptionsEdit edit) in new[]
        {
            ("sensitivity 4", Edit(edit => edit.MouseSensitivity = 4f)), ("screen shape 2", Edit(edit => edit.ScreenShape = 2)),
            ("preset 5", Edit(edit => edit.ControllerPreset[1] = 5)), ("volume 150%", Edit(edit => edit.MusicVolume = 1.5f)),
            ("no change", new OptionsEdit()), ("an unknown action", Edit(edit => edit.Keys[(0x99, 0)] = t)),
            ("the current value", Edit(edit => edit.MusicVolume = read.MusicVolume)),
        })
        {
            check.That(!OptionsFile.Preview(original, edit).Ok, $"Options refuse {name}.");
        }
        check.That(OptionsFile.Describe(9, KeyTable.For(Key.W)!.Packed) == "W" && OptionsFile.Describe(17, 0) == "Left mouse button" &&
            OptionsFile.Describe(5, 0xFFFF).StartsWith("Controller"), "Stored bindings have readable names.");
    }

    private static OptionsEdit Edit(Action<OptionsEdit> change)
    {
        OptionsEdit edit = new();
        change(edit);
        return edit;
    }

    private static void Only(byte[] original, OptionsEdit edit, int[] dwords, Checks check, string name)
    {
        if (OptionsFile.Preview(original, edit).Value is not OptionsPlan plan)
        {
            check.Fail($"The {name} edit must plan.");
            return;
        }
        bool confined = plan.Bytes.Length == original.Length;
        for (int offset = 0; confined && offset < original.Length; offset++)
        {
            if (plan.Bytes[offset] != original[offset] && !dwords.Any(start => offset >= start && offset < start + 4)) confined = false;
        }
        check.That(confined && plan.Changes.Count > 0 && plan.Lines.Count > 0, $"The {name} edit changes only its own bytes.");
    }

    private static uint U(byte[] bytes, int offset) => BinaryPrimitives.ReadUInt32LittleEndian(bytes.AsSpan(offset));

    private static float F(byte[] bytes, int offset) => BinaryPrimitives.ReadSingleLittleEndian(bytes.AsSpan(offset));
}
