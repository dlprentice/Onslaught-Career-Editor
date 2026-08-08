using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.Cli
{
    /// <summary>
    /// Keybind and tri-state token parsing, shared by the legacy invocation and the new
    /// <c>options edit</c> verb so the two can never accept different tokens for the same binding.
    ///
    /// The device/scan encodings below are the Steam build's, recovered from the shipped options entries;
    /// they are not guesses and must not be "tidied". See the per-case comments.
    /// </summary>
    public static class KeybindTokens
    {
        /// <summary>Canonical binding names and the options entry ids they write.</summary>
        public static readonly IReadOnlyDictionary<string, int> BindingEntryIds = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase)
        {
            ["move-forward"] = 0x1F,
            ["move-backward"] = 0x20,
            ["move-left"] = 0x1D,
            ["move-right"] = 0x1E,
            ["look-up"] = 0x1A,
            ["look-down"] = 0x1C,
            ["look-left"] = 0x19,
            ["look-right"] = 0x1B,
            ["zoom-in"] = 0x10,
            ["zoom-out"] = 0x11,
            ["fire-weapon"] = 0x12,
            ["select-weapon"] = 0x14,
            ["transform"] = 0x21,
            ["air-brake"] = 0x15,
            ["special"] = 0x3B,
        };

        public static bool IsKeep(string? value)
        {
            if (string.IsNullOrWhiteSpace(value))
                return true;

            string trimmed = value.Trim();
            return trimmed.Equals("keep", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.Equals("preserve", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.Equals("unchanged", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Three-state parse: null means "the user said nothing, preserve what the file already has".
        /// An unrecognised value throws rather than defaulting, because silently treating a typo as
        /// "off" would write a byte the user never asked for.
        /// </summary>
        public static bool? ParseTriBool(string? value, string optionName)
        {
            if (string.IsNullOrWhiteSpace(value))
                return null;

            string v = value.Trim().ToLowerInvariant();
            if (v is "keep" or "preserve" or "unchanged")
                return null;
            if (v is "1" or "true" or "on" or "yes" or "y")
                return true;
            if (v is "0" or "false" or "off" or "no" or "n")
                return false;

            throw new ArgumentException(
                $"Invalid value '{value}' for {optionName}. " +
                "Use on/off/true/false/1/0/yes/no/y/n, or omit to preserve the existing save value.");
        }

        /// <summary>
        /// Apply CLI binding tokens onto the GUI's editable keybind rows. A "keep" side is left exactly
        /// as loaded, so a row the user did not mention is never counted as an override.
        /// </summary>
        public static bool TryApplyBindings(
            IReadOnlyList<ConfigurationKeybindRow> rows,
            IReadOnlyDictionary<string, string[]> bindings,
            out string error)
        {
            error = string.Empty;
            foreach (KeyValuePair<string, string[]> binding in bindings)
            {
                if (binding.Value is null || binding.Value.Length != 2)
                    continue;

                if (!BindingEntryIds.TryGetValue(binding.Key, out int entryId))
                {
                    error = $"Unknown binding '{binding.Key}'.";
                    return false;
                }

                ConfigurationKeybindRow? row = rows.FirstOrDefault(candidate => candidate.EntryId == entryId);
                if (row is null)
                {
                    error = $"Binding '{binding.Key}' has no editable row in this options file.";
                    return false;
                }

                if (!IsKeep(binding.Value[0]))
                    row.Player1Token = binding.Value[0].Trim();

                if (!IsKeep(binding.Value[1]))
                    row.Player2Token = binding.Value[1].Trim();
            }

            return true;
        }

        /// <summary>
        /// Build raw options-entry overrides for the .bes settings path, where the row-based
        /// configuration service cannot be used.
        /// </summary>
        public static Dictionary<int, BesFilePatcher.OptionsEntryOverride>? ParseEntryOverrides(
            IReadOnlyDictionary<string, string[]> bindings)
        {
            var dict = new Dictionary<int, BesFilePatcher.OptionsEntryOverride>();

            void SetSlot(int entryId, int slotIndex, uint deviceCode, uint packedKey)
            {
                if (!dict.TryGetValue(entryId, out BesFilePatcher.OptionsEntryOverride? ov))
                {
                    ov = new BesFilePatcher.OptionsEntryOverride();
                    dict[entryId] = ov;
                }

                BesFilePatcher.BindingSlotOverride slot = slotIndex == 0 ? ov.Slot0 : ov.Slot1;
                slot.DeviceCode = deviceCode;
                slot.PackedKey = packedKey;
            }

            void ParseRow(
                int entryId,
                uint keyboardDeviceCode,
                bool allowLookMouse,
                bool allowZoomWheel,
                bool allowMouseButtons,
                string[]? values,
                string label)
            {
                if (values is null || values.Length != 2)
                    return;

                void ParseOne(int slotIndex, string tokenLabel, string? raw)
                {
                    if (IsKeep(raw))
                        return;

                    string t = raw!.Trim();
                    if (allowLookMouse && t.StartsWith("Mouse", StringComparison.OrdinalIgnoreCase))
                    {
                        (uint dev, uint key) = ParseLookToken(entryId, t);
                        SetSlot(entryId, slotIndex, dev, key);
                        return;
                    }

                    if (allowZoomWheel &&
                        (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase) ||
                         t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase)))
                    {
                        (uint dev, uint key) = ParseZoomMouseWheel(t);
                        SetSlot(entryId, slotIndex, dev, key);
                        return;
                    }

                    if (allowMouseButtons &&
                        (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase) ||
                         t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase)))
                    {
                        (uint dev, uint key) = ParseMouseButton(entryId, t);
                        SetSlot(entryId, slotIndex, dev, key);
                        return;
                    }

                    if (!BesFilePatcher.TryParseKeyboardPackedKey(t, out uint packed, out string? err))
                        throw new ArgumentException($"Invalid {tokenLabel}: {err}");

                    SetSlot(entryId, slotIndex, keyboardDeviceCode, packed);
                }

                ParseOne(0, $"{label} (P1)", values[0]);
                ParseOne(1, $"{label} (P2)", values[1]);
            }

            string[]? Get(string name) => bindings.TryGetValue(name, out string[]? value) ? value : null;

            // Movement (action_code 0x3B..0x3E => entry_id 0x1D..0x20, binding_type 9)
            ParseRow(0x1F, 9, false, false, false, Get("move-forward"), "Movement: Forward");
            ParseRow(0x20, 9, false, false, false, Get("move-backward"), "Movement: Backward");
            ParseRow(0x1D, 9, false, false, false, Get("move-left"), "Movement: Left");
            ParseRow(0x1E, 9, false, false, false, Get("move-right"), "Movement: Right");

            // Look (action_code 0x40..0x43 => entry_id 0x19..0x1C, binding_type 9).
            // The shipped preset drives look via device 11/12 plus packed_key 0/1.
            ParseRow(0x1A, 9, true, false, false, Get("look-up"), "Look: Up");
            ParseRow(0x1C, 9, true, false, false, Get("look-down"), "Look: Down");
            ParseRow(0x19, 9, true, false, false, Get("look-left"), "Look: Left");
            ParseRow(0x1B, 9, true, false, false, Get("look-right"), "Look: Right");

            // Zoom (action_code 0x45/0x46 => entry_id 0x10/0x11, binding_type 9)
            ParseRow(0x10, 9, false, true, false, Get("zoom-in"), "Zoom: In");
            ParseRow(0x11, 9, false, true, false, Get("zoom-out"), "Zoom: Out");

            // Fire weapon action_code 0x48 remaps BOTH entry 0x12 (binding_type 10) and 0x13
            // (binding_type 9); writing only one leaves the pair inconsistent.
            if (Get("fire-weapon") is { Length: 2 } fireWeapon)
            {
                ParseRow(0x12, 10, false, false, true, fireWeapon, "Others: Fire weapon");
                ParseRow(0x13, 9, false, false, true, fireWeapon, "Others: Fire weapon");
            }

            ParseRow(0x14, 10, false, false, true, Get("select-weapon"), "Others: Select weapon");
            ParseRow(0x21, 8, false, false, false, Get("transform"), "Others: Transform");
            ParseRow(0x15, 9, false, false, false, Get("air-brake"), "Others: Air brake");
            ParseRow(0x3B, 8, false, false, false, Get("special"), "Others: Special function");

            return dict.Count == 0 ? null : dict;
        }

        private static (uint Dev, uint Key) ParseLookMouse(int entryId)
        {
            // Steam preset: device 11 is the positive direction, device 12 the negative;
            // packed_key scan 0 is the X axis and 1 is the Y axis.
            return entryId switch
            {
                0x1B => (11u, 0u), // Look Right (MouseX+)
                0x19 => (12u, 0u), // Look Left  (MouseX-)
                0x1A => (11u, 1u), // Look Up    (MouseY+)
                0x1C => (12u, 1u), // Look Down  (MouseY-)
                _ => throw new ArgumentException($"Internal error: entry_id 0x{entryId:X} is not a Look entry."),
            };
        }

        private static (uint Dev, uint Key) ParseLookToken(int entryId, string token)
        {
            string t = token.Trim();
            string tl = t.ToLowerInvariant();
            if (tl is "mouse" or "mousex" or "mousey")
                return ParseLookMouse(entryId);

            if (tl.StartsWith("mousex", StringComparison.Ordinal))
            {
                if (tl.EndsWith("-", StringComparison.Ordinal)) return (12u, 0u);
                if (tl.EndsWith("+", StringComparison.Ordinal)) return (11u, 0u);
                return ParseLookMouse(entryId);
            }

            if (tl.StartsWith("mousey", StringComparison.Ordinal))
            {
                if (tl.EndsWith("-", StringComparison.Ordinal)) return (12u, 1u);
                if (tl.EndsWith("+", StringComparison.Ordinal)) return (11u, 1u);
                return ParseLookMouse(entryId);
            }

            if (tl.StartsWith("mouse(", StringComparison.Ordinal) && tl.EndsWith(")", StringComparison.Ordinal))
            {
                string inner = tl["mouse(".Length..^1];
                if (int.TryParse(inner, NumberStyles.Integer, CultureInfo.InvariantCulture, out int scanSigned))
                {
                    (uint devDefault, _) = ParseLookMouse(entryId);
                    return (devDefault, unchecked((uint)scanSigned));
                }
            }

            throw new ArgumentException(
                $"Invalid look binding '{token}'. Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key.");
        }

        private static (uint Dev, uint Key) ParseZoomMouseWheel(string t)
        {
            if (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase))
                return (16u, 3u);
            if (t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase))
                return (16u, 4u);

            throw new ArgumentException($"Invalid zoom binding '{t}'. Use MouseWheelUp/MouseWheelDown or a keyboard key.");
        }

        private static (uint Dev, uint Key) ParseMouseButton(int entryId, string t)
        {
            if (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase))
            {
                // Steam build device codes for Fire weapon differ per entry.
                return entryId switch
                {
                    0x12 => (17u, 0u),
                    0x13 => (15u, 0u),
                    _ => throw new ArgumentException("MouseLeft is only supported for Fire weapon (entry 0x12/0x13)."),
                };
            }

            if (t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase))
            {
                // Steam build uses device 16 scan 2 for Select weapon.
                return entryId switch
                {
                    0x14 => (16u, 2u),
                    _ => throw new ArgumentException("MouseRight is only supported for Select weapon (entry 0x14)."),
                };
            }

            throw new ArgumentException($"Invalid mouse button binding '{t}'. Use MouseLeft/MouseRight.");
        }
    }
}
