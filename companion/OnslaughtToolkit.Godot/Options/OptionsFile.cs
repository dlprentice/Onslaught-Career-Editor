// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Options;

/// <summary>One action the game lets a player bind, with the keyboard device code the game uses for it.</summary>
/// <param name="MirrorEntryId">An entry the game keeps equal to this one (Fire weapon's second row).</param>
public sealed record BindingAction(string Group, string Name, int EntryId, uint KeyboardDevice, int? MirrorEntryId = null, uint? MirrorDevice = null);

/// <summary>A keyboard key as the game stores it: the character it types (0 for none) and its set-1 scan code.</summary>
public sealed record KeyChoice(string Name, uint Character, uint Scan)
{
    public uint Packed => (Character << 16) | Scan;
}

/// <summary>One stored binding row. Rows are copied by the game as they are; the companion never edits Flags or EntryId.</summary>
public sealed record BindingRow(int Row, int Offset, uint Flags, int EntryId, uint Slot0Device, uint Slot0Key, uint Slot1Device, uint Slot1Key)
{
    public (uint Device, uint Key) Slot(int slot) => slot == 0 ? (Slot0Device, Slot0Key) : (Slot1Device, Slot1Key);
}

/// <summary>The readable settings of a defaultoptions.bea (or the options block of any career).</summary>
public sealed record OptionsReading(float SoundVolume, float MusicVolume, bool[] InvertFlight, bool[] InvertWalker, bool[] Vibration,
    uint[] ControllerPreset, IReadOnlyList<BindingRow> Bindings, float MouseSensitivity, ushort ControlScheme, ushort Language,
    uint ScreenShape, uint DisplayMode);

/// <summary>The explicitly chosen option changes for one copy. Null means keep.</summary>
public sealed class OptionsEdit
{
    public float? SoundVolume { get; set; }
    public float? MusicVolume { get; set; }
    public bool?[] InvertFlight { get; } = new bool?[2];
    public bool?[] InvertWalker { get; } = new bool?[2];
    public bool?[] Vibration { get; } = new bool?[2];
    public uint?[] ControllerPreset { get; } = new uint?[2];
    public float? MouseSensitivity { get; set; }
    public uint? ScreenShape { get; set; }

    /// <summary>Keyboard keys by (entry id, slot); slot 0 is player one, slot 1 player two.</summary>
    public Dictionary<(int EntryId, int Slot), KeyChoice> Keys { get; } = [];

    public bool IsEmpty => SoundVolume is null && MusicVolume is null && MouseSensitivity is null && ScreenShape is null &&
        Keys.Count == 0 && InvertFlight.All(value => value is null) && InvertWalker.All(value => value is null) &&
        Vibration.All(value => value is null) && ControllerPreset.All(value => value is null);
}

public sealed record OptionsPlan(byte[] Bytes, IReadOnlyList<ByteChange> Changes, IReadOnlyList<string> Lines);

/// <summary>
/// The options block shared by <c>defaultoptions.bea</c> and careers (RE save-format.md): career
/// settings at 0x248E–0x24BD, sixteen 32-byte binding rows at 0x24BE, and the tail at 0x26BE.
/// Evidence: the game's startup load copies these into its settings and binding rows without
/// validation (original-code controls), and a Transform key set in a copied options file was seen
/// working in the game. Every other byte is copied unchanged.
/// </summary>
public static class OptionsFile
{
    public const int SoundOffset = 0x248E, MusicOffset = 0x2492, FlightOffset = 0x249E, WalkerOffset = 0x24A6;
    public const int VibrationOffset = 0x24AE, PresetOffset = 0x24B6, RowsOffset = 0x24BE, RowSize = 0x20, RowCount = 16;
    public const int TailOffset = 0x26BE;

    /// <summary>The fifteen bindable actions and their keyboard device codes (MIT ConfigurationEditorService).</summary>
    public static IReadOnlyList<BindingAction> Actions { get; } =
    [
        new("Movement", "Forward", 0x1F, 9), new("Movement", "Backward", 0x20, 9),
        new("Movement", "Left", 0x1D, 9), new("Movement", "Right", 0x1E, 9),
        new("Look", "Up", 0x1A, 9), new("Look", "Down", 0x1C, 9), new("Look", "Left", 0x19, 9), new("Look", "Right", 0x1B, 9),
        new("Zoom", "In", 0x10, 9), new("Zoom", "Out", 0x11, 9),
        new("Actions", "Fire weapon", 0x12, 10, 0x13, 9), new("Actions", "Select weapon", 0x14, 10),
        new("Actions", "Transform", 0x21, 8), new("Actions", "Air brake", 0x15, 9), new("Actions", "Special function", 0x3B, 8),
    ];

    /// <summary>The values the game's own mouse-sensitivity slider stores: 3 to 63 in steps of 3 (retail, static).</summary>
    public static IReadOnlyList<float> SliderSensitivities { get; } = Enumerable.Range(1, 21).Select(step => step * 3f).ToArray();

    public static Outcome<OptionsReading> Read(ReadOnlySpan<byte> bytes)
    {
        if (CareerSave.Inspect(bytes) is { Ok: false } refused) return Outcome<OptionsReading>.Refusal(refused.Message);
        List<BindingRow> rows = [];
        for (int row = 0; row < RowCount; row++)
        {
            int offset = RowsOffset + row * RowSize;
            rows.Add(new BindingRow(row, offset, U32(bytes, offset), (int)U32(bytes, offset + 4),
                U32(bytes, offset + 0x0C), U32(bytes, offset + 0x10), U32(bytes, offset + 0x18), U32(bytes, offset + 0x1C)));
        }
        return Outcome<OptionsReading>.Success(new OptionsReading(
            F32(bytes, SoundOffset), F32(bytes, MusicOffset),
            [U32(bytes, FlightOffset) != 0, U32(bytes, FlightOffset + 4) != 0],
            [U32(bytes, WalkerOffset) != 0, U32(bytes, WalkerOffset + 4) != 0],
            [U32(bytes, VibrationOffset) != 0, U32(bytes, VibrationOffset + 4) != 0],
            [U32(bytes, PresetOffset), U32(bytes, PresetOffset + 4)],
            rows, F32(bytes, TailOffset + 0x04), BinaryPrimitives.ReadUInt16LittleEndian(bytes[(TailOffset + 0x08)..]),
            BinaryPrimitives.ReadUInt16LittleEndian(bytes[(TailOffset + 0x0A)..]), U32(bytes, TailOffset + 0x20), U32(bytes, TailOffset + 0x28)),
            "Options read.");
    }

    public static Outcome<OptionsPlan> Preview(ReadOnlySpan<byte> original, OptionsEdit edit)
    {
        if (Read(original).Value is not OptionsReading current) return Outcome<OptionsPlan>.Refusal(Read(original).Message);
        if (edit.IsEmpty) return Outcome<OptionsPlan>.Refusal("Choose a setting to change.");
        byte[] output = original.ToArray();
        List<string> lines = [];
        if (!Volume(edit.SoundVolume, SoundOffset, "Sound volume", current.SoundVolume) ||
            !Volume(edit.MusicVolume, MusicOffset, "Music volume", current.MusicVolume))
            return Outcome<OptionsPlan>.Refusal("Volumes run from 0 to 100%.");
        for (int player = 0; player < 2; player++)
        {
            Flag(edit.InvertFlight[player], FlightOffset + player * 4, $"Player {player + 1} flight invert Y");
            Flag(edit.InvertWalker[player], WalkerOffset + player * 4, $"Player {player + 1} walker invert Y");
            Flag(edit.Vibration[player], VibrationOffset + player * 4, $"Player {player + 1} vibration");
            if (edit.ControllerPreset[player] is uint preset)
            {
                if (preset is < 1 or > 4) return Outcome<OptionsPlan>.Refusal("Controller presets run from 1 to 4.");
                Word(PresetOffset + player * 4, preset, $"Player {player + 1} controller preset {current.ControllerPreset[player]} → {preset}");
            }
        }
        if (edit.MouseSensitivity is float sensitivity)
        {
            if (!SliderSensitivities.Contains(sensitivity))
                return Outcome<OptionsPlan>.Refusal("Mouse sensitivity uses the game's own slider values, 3 to 63 in steps of 3.");
            BinaryPrimitives.WriteSingleLittleEndian(output.AsSpan(TailOffset + 0x04), sensitivity);
            lines.Add($"Mouse sensitivity {current.MouseSensitivity:0.###} → {sensitivity:0}");
        }
        if (edit.ScreenShape is uint shape)
        {
            if (shape > 1) return Outcome<OptionsPlan>.Refusal("Screen shape can be 4:3 or 16:9.");
            Word(TailOffset + 0x20, shape, $"Screen shape {ShapeName(current.ScreenShape)} → {ShapeName(shape)}");
        }
        foreach (((int entryId, int slot), KeyChoice key) in edit.Keys)
        {
            if (slot is < 0 or > 1 || Actions.FirstOrDefault(action => action.EntryId == entryId) is not BindingAction action)
                return Outcome<OptionsPlan>.Refusal("That binding is not one the game offers.");
            if (!SetKey(entryId, slot, action.KeyboardDevice, key)) return Outcome<OptionsPlan>.Refusal($"This file has no row for {action.Name}.");
            if (action.MirrorEntryId is int mirror && !SetKey(mirror, slot, action.MirrorDevice ?? action.KeyboardDevice, key))
                return Outcome<OptionsPlan>.Refusal($"This file has no second row for {action.Name}.");
            lines.Add($"Player {slot + 1} {action.Group.ToLowerInvariant()} {action.Name.ToLowerInvariant()} → {key.Name}");
        }
        if (edit.Keys.Count > 0 && current.ControlScheme != 0)
        {
            BinaryPrimitives.WriteUInt16LittleEndian(output.AsSpan(TailOffset + 0x08), 0);
            lines.Add("Control scheme → custom, so the game keeps the chosen keys");
        }
        ByteComparison difference = CareerSave.Compare(original, output);
        if (difference.Equal) return Outcome<OptionsPlan>.Refusal("Those settings already have the chosen values.");
        return Outcome<OptionsPlan>.Success(new OptionsPlan(output, difference.Changes, lines), "Preview only. No file has been written.");

        bool Volume(float? value, int offset, string name, float before)
        {
            if (value is not float volume) return true;
            if (!float.IsFinite(volume) || volume is < 0 or > 1) return false;
            BinaryPrimitives.WriteSingleLittleEndian(output.AsSpan(offset), volume);
            lines.Add($"{name} {before * 100:0}% → {volume * 100:0}%");
            return true;
        }

        void Flag(bool? value, int offset, string name)
        {
            if (value is bool on) Word(offset, on ? 1u : 0u, $"{name} → {(on ? "on" : "off")}");
        }

        void Word(int offset, uint value, string line)
        {
            BinaryPrimitives.WriteUInt32LittleEndian(output.AsSpan(offset), value);
            lines.Add(line);
        }

        bool SetKey(int entryId, int slot, uint device, KeyChoice key)
        {
            if (current.Bindings.FirstOrDefault(row => row.EntryId == entryId) is not BindingRow row) return false;
            int at = row.Offset + (slot == 0 ? 0x0C : 0x18);
            BinaryPrimitives.WriteUInt32LittleEndian(output.AsSpan(at), device);
            BinaryPrimitives.WriteUInt32LittleEndian(output.AsSpan(at + 4), key.Packed);
            return true;
        }
    }

    public static string ShapeName(uint shape) => shape switch { 0 => "4:3", 1 => "16:9", _ => $"value {shape}" };

    /// <summary>A readable name for a stored binding; controller and unknown devices are named by number.</summary>
    public static string Describe(uint device, uint key)
    {
        if (device is 8 or 9 or 10) return KeyTable.Name(key);
        return (device, key) switch
        {
            (11, 0) => "Mouse X+", (12, 0) => "Mouse X−", (11, 1) => "Mouse Y+", (12, 1) => "Mouse Y−",
            (16, 3) => "Mouse wheel up", (16, 4) => "Mouse wheel down", (16, 2) => "Right mouse button",
            (17, 0) or (15, 0) => "Left mouse button",
            (>= 4 and <= 7, _) => "Controller",
            _ => "Other input",
        };
    }

    /// <summary>The stored device and key, for anyone who wants the raw values behind a binding's name.</summary>
    public static string Raw(uint device, uint key) => $"Stored as device {device}, key 0x{key:X8}";

    private static uint U32(ReadOnlySpan<byte> bytes, int offset) => BinaryPrimitives.ReadUInt32LittleEndian(bytes[offset..]);

    private static float F32(ReadOnlySpan<byte> bytes, int offset) => BinaryPrimitives.ReadSingleLittleEndian(bytes[offset..]);
}
