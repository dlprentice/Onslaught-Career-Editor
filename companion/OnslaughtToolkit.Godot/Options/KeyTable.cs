// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Options;

/// <summary>
/// Keyboard keys as the game stores them in binding rows: <c>(character &lt;&lt; 16) | scan</c>, where
/// the character is what the key types (0 for keys that type nothing) and the scan code is set 1, with
/// 0x80 added for extended keys (DirectInput's key numbers). The convention is taken from rows the game
/// itself wrote in the tracked fixture: the letters A, D, E, G, Q, S, T and W, Space, Tab, numpad 1, the
/// four arrows and left Shift. Only those classes are <see cref="KeyChoice.GameWritten"/>; the rest
/// (top-row digits, the other numpad digits, punctuation, Caps Lock, left Control and the right-hand
/// Shift and Control) follow the same convention but no game-written row confirms them yet. Godot reports
/// left and right Shift (and Control) as one key with a location, so the right-hand keys are told apart
/// by that location and stored with their own scan codes (Right Shift 0x36, Right Control 0x9D), never
/// as the left-hand key. Keys outside this table cannot be bound here.
/// </summary>
public static class KeyTable
{
    private static readonly Dictionary<Key, KeyChoice> ByGodotKey = Build();
    private static readonly KeyChoice RightShift = new("Right Shift", 0, 0x36), RightControl = new("Right Control", 0, 0x9D);
    private static readonly Dictionary<uint, string> NamesByPacked = ByGodotKey.Values.Append(RightShift).Append(RightControl)
        .GroupBy(choice => choice.Packed).ToDictionary(group => group.Key, group => group.First().Name);

    public static IReadOnlyCollection<KeyChoice> Keys => [.. ByGodotKey.Values, RightShift, RightControl];

    /// <summary>The stored form of a physical key, or null when the game's form of it is not established.</summary>
    public static KeyChoice? For(Key physical) => ByGodotKey.GetValueOrDefault(physical);

    /// <summary>
    /// The stored form of a physical key pressed at a location: Godot's <see cref="Key.Shift"/> and
    /// <see cref="Key.Ctrl"/> cover both sides, and a right-hand press must not be stored as the left-hand key.
    /// </summary>
    public static KeyChoice? For(Key physical, KeyLocation location) => (physical, location) switch
    {
        (Key.Shift, KeyLocation.Right) => RightShift,
        (Key.Ctrl, KeyLocation.Right) => RightControl,
        _ => For(physical),
    };

    public static string Name(uint packed) => packed == 0 ? "None" :
        NamesByPacked.GetValueOrDefault(packed) ?? $"Key (character 0x{packed >> 16:X2}, scan 0x{packed & 0xFFFF:X2})";

    private static Dictionary<Key, KeyChoice> Build()
    {
        Dictionary<Key, KeyChoice> keys = [];
        uint[] letterScans = [0x1E, 0x30, 0x2E, 0x20, 0x12, 0x21, 0x22, 0x23, 0x17, 0x24, 0x25, 0x26, 0x32, 0x31, 0x18, 0x19,
            0x10, 0x13, 0x1F, 0x14, 0x16, 0x2F, 0x11, 0x2D, 0x15, 0x2C];
        for (int letter = 0; letter < 26; letter++)
            keys[Key.A + letter] = new(((char)('A' + letter)).ToString(), (uint)('A' + letter), letterScans[letter], GameWritten: true);
        uint[] digitScans = [0x0B, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A];
        uint[] padScans = [0x52, 0x4F, 0x50, 0x51, 0x4B, 0x4C, 0x4D, 0x47, 0x48, 0x49];
        for (int digit = 0; digit < 10; digit++)
        {
            keys[Key.Key0 + digit] = new(digit.ToString(), (uint)('0' + digit), digitScans[digit]);
            keys[Key.Kp0 + digit] = new("Numpad " + digit, (uint)('0' + digit), padScans[digit], GameWritten: digit == 1);
        }
        keys[Key.Space] = new("Space", ' ', 0x39, GameWritten: true);
        keys[Key.Tab] = new("Tab", 0x09, 0x0F, GameWritten: true);
        keys[Key.Up] = new("Up", 0, 0xC8, GameWritten: true);
        keys[Key.Down] = new("Down", 0, 0xD0, GameWritten: true);
        keys[Key.Left] = new("Left", 0, 0xCB, GameWritten: true);
        keys[Key.Right] = new("Right", 0, 0xCD, GameWritten: true);
        keys[Key.Shift] = new("Left Shift", 0, 0x2A, GameWritten: true);
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
