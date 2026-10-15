// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Options;

/// <summary>
/// Keyboard keys as the game stores them in binding rows: <c>(character &lt;&lt; 16) | scan</c>, where
/// the character is what the key types (0 for keys that type nothing) and the scan code is set 1, with
/// 0x80 added for extended keys. The convention is taken from rows the game itself wrote in the tracked
/// fixture (W, A, S, D, Space, Tab, numpad 1, arrows, left Shift) and the retained MIT key table; keys
/// outside this table cannot be bound here.
/// </summary>
public static class KeyTable
{
    private static readonly Dictionary<Key, KeyChoice> ByGodotKey = Build();
    private static readonly Dictionary<uint, string> NamesByPacked = ByGodotKey.Values
        .GroupBy(choice => choice.Packed).ToDictionary(group => group.Key, group => group.First().Name);

    public static IReadOnlyCollection<KeyChoice> Keys => ByGodotKey.Values;

    /// <summary>The stored form of a physical key, or null when the game's form of it is not established.</summary>
    public static KeyChoice? For(Key physical) => ByGodotKey.GetValueOrDefault(physical);

    public static string Name(uint packed) => packed == 0 ? "None" :
        NamesByPacked.GetValueOrDefault(packed) ?? $"Key (character 0x{packed >> 16:X2}, scan 0x{packed & 0xFFFF:X2})";

    private static Dictionary<Key, KeyChoice> Build()
    {
        Dictionary<Key, KeyChoice> keys = [];
        uint[] letterScans = [0x1E, 0x30, 0x2E, 0x20, 0x12, 0x21, 0x22, 0x23, 0x17, 0x24, 0x25, 0x26, 0x32, 0x31, 0x18, 0x19,
            0x10, 0x13, 0x1F, 0x14, 0x16, 0x2F, 0x11, 0x2D, 0x15, 0x2C];
        for (int letter = 0; letter < 26; letter++)
            keys[Key.A + letter] = new(((char)('A' + letter)).ToString(), (uint)('A' + letter), letterScans[letter]);
        uint[] digitScans = [0x0B, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A];
        uint[] padScans = [0x52, 0x4F, 0x50, 0x51, 0x4B, 0x4C, 0x4D, 0x47, 0x48, 0x49];
        for (int digit = 0; digit < 10; digit++)
        {
            keys[Key.Key0 + digit] = new(digit.ToString(), (uint)('0' + digit), digitScans[digit]);
            keys[Key.Kp0 + digit] = new("Numpad " + digit, (uint)('0' + digit), padScans[digit]);
        }
        keys[Key.Space] = new("Space", ' ', 0x39);
        keys[Key.Tab] = new("Tab", 0x09, 0x0F);
        keys[Key.Up] = new("Up", 0, 0xC8);
        keys[Key.Down] = new("Down", 0, 0xD0);
        keys[Key.Left] = new("Left", 0, 0xCB);
        keys[Key.Right] = new("Right", 0, 0xCD);
        keys[Key.Shift] = new("Left Shift", 0, 0x2A);
        keys[Key.Ctrl] = new("Left Control", 0, 0x1D);
        keys[Key.Capslock] = new("Caps Lock", 0, 0x3A);
        foreach ((Key key, char character, uint scan) in new[]
        {
            (Key.Minus, '-', 0x0Cu), (Key.Equal, '=', 0x0Du), (Key.Semicolon, ';', 0x27u), (Key.Apostrophe, '\'', 0x28u),
            (Key.Comma, ',', 0x33u), (Key.Period, '.', 0x34u), (Key.Slash, '/', 0x35u), (Key.Backslash, '\\', 0x2Bu),
            (Key.Quoteleft, '`', 0x29u),
        })
        {
            keys[key] = new(character.ToString(), character, scan);
        }
        return keys;
    }
}
