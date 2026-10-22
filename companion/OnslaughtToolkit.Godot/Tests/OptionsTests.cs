// SPDX-License-Identifier: GPL-3.0-only
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
        Only(original, keyEdit, [transform + 0x18, transform + 0x1C], check, "slot 2 transform key");
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
            "Changing a key sets the control scheme index to 0.");
        GameWrittenKeys(original, read, check);
        RightHandModifiers(original, read, keyEdit, check);
        NoOpFields(original, read, check);
        byte[] unknownScheme = original.ToArray();
        BinaryPrimitives.WriteUInt16LittleEndian(unknownScheme.AsSpan(0x26BE + 8), 7);
        check.That(OptionsFile.Preview(unknownScheme, keyEdit) is { Ok: false } refusedScheme && refusedScheme.Message.Contains("control scheme index is 7") &&
            OptionsFile.Preview(unknownScheme, Edit(edit => edit.MusicVolume = read.MusicVolume > 0.5f ? 0.25f : 0.75f)).Ok,
            "A key edit is refused for a control-scheme index the companion does not know; other settings still change.");

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

    /// <summary>
    /// Every keyboard binding the game itself wrote in the fixture (keyboard devices 8 to 10, a nonzero key) decodes to a
    /// key-table name, and that entry packs to exactly the stored dword and is marked as game-written.
    /// </summary>
    private static void GameWrittenKeys(byte[] original, OptionsReading read, Checks check)
    {
        int keyboard = 0;
        foreach (BindingRow row in read.Bindings)
        {
            for (int slot = 0; slot < 2; slot++)
            {
                (uint device, uint key) = row.Slot(slot);
                if (device is not (8 or 9 or 10) || key == 0) continue;
                keyboard++;
                KeyChoice? entry = KeyTable.Keys.FirstOrDefault(choice => choice.Packed == key);
                check.That(entry is { GameWritten: true } && entry.Name == KeyTable.Name(key) &&
                    U(original, row.Offset + (slot == 0 ? 0x10 : 0x1C)) == entry.Packed,
                    $"The game-written key 0x{key:X8} (entry 0x{row.EntryId:X2}, slot {slot + 1}) is in the key table exactly as stored.");
            }
        }
        check.That(keyboard == 16, $"The fixture holds the sixteen game-written keyboard bindings the key table was checked against (found {keyboard}).");
        check.That(KeyTable.For(Key.W)?.Packed == 0x00570011 && KeyTable.For(Key.Kp1)?.Packed == 0x0031004F && KeyTable.For(Key.Up)?.Packed == 0xC8,
            "W, numpad 1 and the up arrow pack as the game wrote them.");
        check.That(KeyTable.For(Key.Key1) is { GameWritten: false } && KeyTable.For(Key.Kp2) is { GameWritten: false } &&
            KeyTable.For(Key.Comma) is { GameWritten: false } && KeyTable.For(Key.Ctrl) is { GameWritten: false },
            "Key classes no game-written row confirms are marked as not yet seen.");
    }

    /// <summary>Right Shift and Right Control are their own keys to the game, never stored as the left-hand ones.</summary>
    private static void RightHandModifiers(byte[] original, OptionsReading read, OptionsEdit keyEdit, Checks check)
    {
        KeyChoice? rightShift = KeyTable.For(Key.Shift, KeyLocation.Right), leftShift = KeyTable.For(Key.Shift, KeyLocation.Left);
        KeyChoice? rightControl = KeyTable.For(Key.Ctrl, KeyLocation.Right), leftControl = KeyTable.For(Key.Ctrl, KeyLocation.Left);
        check.That(rightShift is { Packed: 0x36, Name: "Right Shift", GameWritten: false } && leftShift?.Packed == 0x2A &&
            rightShift.Packed != leftShift.Packed, "Right Shift is stored as scan 0x36, not as Left Shift (0x2A).");
        check.That(rightControl is { Packed: 0x9D, Name: "Right Control", GameWritten: false } && leftControl?.Packed == 0x1D,
            "Right Control is stored as extended scan 0x9D, not as Left Control (0x1D).");
        check.That(KeyTable.Name(0x36) == "Right Shift" && KeyTable.Name(0x9D) == "Right Control", "Stored right-hand keys read back by name.");
        int transform = read.Bindings.Single(row => row.EntryId == 0x21).Offset;
        if (OptionsFile.Preview(original, Edit(edit => edit.Keys[(0x21, 1)] = rightShift!)).Value is OptionsPlan plan)
            check.That(U(plan.Bytes, transform + 0x1C) == 0x36 && plan.Lines.Single().EndsWith("→ Right Shift", StringComparison.Ordinal),
                "A Right Shift edit writes 0x36 into the slot.");
        else
            check.Fail("A Right Shift edit must plan.");
    }

    /// <summary>A field set to the value it already holds is not listed as a change, and changes no byte.</summary>
    private static void NoOpFields(byte[] original, OptionsReading read, Checks check)
    {
        float music = read.MusicVolume > 0.5f ? 0.25f : 0.75f;
        KeyChoice space = KeyTable.For(Key.Space)!;
        OptionsEdit mixed = Edit(edit =>
        {
            edit.MusicVolume = music;
            edit.SoundVolume = read.SoundVolume;
            edit.InvertFlight[0] = read.InvertFlight[0];
            edit.ControllerPreset[1] = read.ControllerPreset[1];
            edit.ScreenShape = read.ScreenShape;
            edit.Keys[(0x21, 1)] = space; // the fixture's own Transform key
        });
        if (OptionsFile.Preview(original, mixed).Value is OptionsPlan plan)
        {
            check.That(plan.Lines.Count == 1 && plan.Lines[0].StartsWith("Music volume", StringComparison.Ordinal) &&
                plan.Changes.All(change => change.Offset is >= 0x2492 and < 0x2496),
                "A mixed edit lists only the field that changes; the fields set to their current values change no byte and get no line.");
        }
        else
        {
            check.Fail("A mixed edit with one real change must plan.");
        }
        check.That(!OptionsFile.Preview(original, Edit(edit => edit.Keys[(0x21, 1)] = space)).Ok,
            "Setting a key to the key it already has is no change, and is refused as one.");
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
