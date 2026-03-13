using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;

namespace Onslaught___Career_Editor
{
    public sealed class ConfigurationKeybindRow : INotifyPropertyChanged
    {
        private string _player1Token = string.Empty;
        private string _player2Token = string.Empty;

        public string GroupLabel { get; init; } = string.Empty;
        public string ActionLabel { get; init; } = string.Empty;
        public int EntryId { get; init; }
        public uint KeyboardDeviceCode { get; init; }
        public bool AllowLookMouse { get; init; }
        public bool AllowZoomWheel { get; init; }
        public bool AllowMouseButtons { get; init; }
        public int? MirrorEntryId { get; init; }
        public uint? MirrorKeyboardDeviceCode { get; init; }
        public string CurrentPlayer1Token { get; init; } = string.Empty;
        public string CurrentPlayer2Token { get; init; } = string.Empty;

        public string Player1Token
        {
            get => _player1Token;
            set => SetField(ref _player1Token, value);
        }

        public string Player2Token
        {
            get => _player2Token;
            set => SetField(ref _player2Token, value);
        }

        public event PropertyChangedEventHandler? PropertyChanged;

        public ConfigurationKeybindRow CloneForEditing()
        {
            return new ConfigurationKeybindRow
            {
                GroupLabel = GroupLabel,
                ActionLabel = ActionLabel,
                EntryId = EntryId,
                KeyboardDeviceCode = KeyboardDeviceCode,
                AllowLookMouse = AllowLookMouse,
                AllowZoomWheel = AllowZoomWheel,
                AllowMouseButtons = AllowMouseButtons,
                MirrorEntryId = MirrorEntryId,
                MirrorKeyboardDeviceCode = MirrorKeyboardDeviceCode,
                CurrentPlayer1Token = CurrentPlayer1Token,
                CurrentPlayer2Token = CurrentPlayer2Token,
                Player1Token = Player1Token,
                Player2Token = Player2Token
            };
        }

        private void SetField(ref string field, string value, [CallerMemberName] string? propertyName = null)
        {
            if (string.Equals(field, value, StringComparison.Ordinal))
            {
                return;
            }

            field = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    public sealed class ConfigurationSnapshot
    {
        public string FilePath { get; init; } = string.Empty;
        public string FileName { get; init; } = string.Empty;
        public float SoundVolume { get; init; }
        public float MusicVolume { get; init; }
        public bool InvertWalkerP1 { get; init; }
        public bool InvertWalkerP2 { get; init; }
        public bool InvertFlightP1 { get; init; }
        public bool InvertFlightP2 { get; init; }
        public bool VibrationP1 { get; init; }
        public bool VibrationP2 { get; init; }
        public uint ControllerConfigP1 { get; init; }
        public uint ControllerConfigP2 { get; init; }
        public int OptionsEntryCount { get; init; }
        public float MouseSensitivity { get; init; }
        public ushort ControlSchemeIndex { get; init; }
        public ushort LanguageIndex { get; init; }
        public uint ScreenShape { get; init; }
        public uint D3DDeviceIndex { get; init; }
        public IReadOnlyList<ConfigurationKeybindRow> KeybindRows { get; init; } = Array.Empty<ConfigurationKeybindRow>();
    }

    public sealed class ConfigurationPatchRequest
    {
        public string InputPath { get; init; } = string.Empty;
        public string OutputPath { get; init; } = string.Empty;
        public float? SoundVolumeOverride { get; init; }
        public float? MusicVolumeOverride { get; init; }
        public bool? InvertWalkerP1Override { get; init; }
        public bool? InvertWalkerP2Override { get; init; }
        public bool? InvertFlightP1Override { get; init; }
        public bool? InvertFlightP2Override { get; init; }
        public bool? VibrationP1Override { get; init; }
        public bool? VibrationP2Override { get; init; }
        public uint? ControllerConfigP1Override { get; init; }
        public uint? ControllerConfigP2Override { get; init; }
        public string? CopyOptionsFromPath { get; init; }
        public bool CopyOptionsEntries { get; init; }
        public bool CopyOptionsTail { get; init; }
        public IReadOnlyList<ConfigurationKeybindRow> KeybindRows { get; init; } = Array.Empty<ConfigurationKeybindRow>();
    }

    public static class ConfigurationEditorService
    {
        private sealed record KeybindDefinition(
            string GroupLabel,
            string ActionLabel,
            int EntryId,
            uint KeyboardDeviceCode,
            bool AllowLookMouse,
            bool AllowZoomWheel,
            bool AllowMouseButtons,
            int? MirrorEntryId,
            uint? MirrorKeyboardDeviceCode);

        private static readonly IReadOnlyList<KeybindDefinition> KeybindDefinitions = new[]
        {
            new KeybindDefinition("Movement", "Forward", 0x1F, 9u, false, false, false, null, null),
            new KeybindDefinition("Movement", "Backward", 0x20, 9u, false, false, false, null, null),
            new KeybindDefinition("Movement", "Left", 0x1D, 9u, false, false, false, null, null),
            new KeybindDefinition("Movement", "Right", 0x1E, 9u, false, false, false, null, null),
            new KeybindDefinition("Look", "Up", 0x1A, 9u, true, false, false, null, null),
            new KeybindDefinition("Look", "Down", 0x1C, 9u, true, false, false, null, null),
            new KeybindDefinition("Look", "Left", 0x19, 9u, true, false, false, null, null),
            new KeybindDefinition("Look", "Right", 0x1B, 9u, true, false, false, null, null),
            new KeybindDefinition("Zoom", "In", 0x10, 9u, false, true, false, null, null),
            new KeybindDefinition("Zoom", "Out", 0x11, 9u, false, true, false, null, null),
            new KeybindDefinition("Actions", "Fire weapon", 0x12, 10u, false, false, true, 0x13, 9u),
            new KeybindDefinition("Actions", "Select weapon", 0x14, 10u, false, false, true, null, null),
            new KeybindDefinition("Actions", "Transform", 0x21, 8u, false, false, false, null, null),
            new KeybindDefinition("Actions", "Air brake", 0x15, 9u, false, false, false, null, null),
            new KeybindDefinition("Actions", "Special function", 0x3B, 8u, false, false, false, null, null)
        };

        public static IReadOnlyList<SaveAnalyzerFileItem> GetDetectedOptionsFiles(string? gameDir = null)
        {
            return SaveAnalyzerService.GetDetectedFiles(gameDir)
                .Where(item => SaveEditorService.IsOptionsLikeFilePath(item.Path))
                .ToArray();
        }

        public static ConfigurationSnapshot LoadConfigurationSnapshot(string filePath)
        {
            if (!SaveEditorService.IsOptionsLikeFilePath(filePath))
            {
                throw new InvalidDataException("Configuration mode requires a .bea options file (typically defaultoptions.bea).");
            }

            SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(filePath);
            if (!analysis.IsValid)
            {
                throw new InvalidDataException(analysis.ErrorMessage ?? "Invalid save/options file.");
            }

            var bindings = ReadBindings(filePath, analysis);
            return new ConfigurationSnapshot
            {
                FilePath = filePath,
                FileName = Path.GetFileName(filePath) ?? "defaultoptions.bea",
                SoundVolume = analysis.SoundVolume,
                MusicVolume = analysis.MusicVolume,
                InvertWalkerP1 = analysis.InvertYAxisRaw[0] != 0,
                InvertWalkerP2 = analysis.InvertYAxisRaw[1] != 0,
                InvertFlightP1 = analysis.InvertFlightRaw[0] != 0,
                InvertFlightP2 = analysis.InvertFlightRaw[1] != 0,
                VibrationP1 = analysis.VibrationRaw[0] != 0,
                VibrationP2 = analysis.VibrationRaw[1] != 0,
                ControllerConfigP1 = analysis.ControllerConfigNum[0],
                ControllerConfigP2 = analysis.ControllerConfigNum[1],
                OptionsEntryCount = analysis.OptionsEntryCount,
                MouseSensitivity = analysis.OptionsMouseSensitivity,
                ControlSchemeIndex = analysis.OptionsControlSchemeIndex,
                LanguageIndex = analysis.OptionsLanguageIndex,
                ScreenShape = analysis.OptionsScreenShape,
                D3DDeviceIndex = analysis.OptionsD3DDeviceIndex,
                KeybindRows = CreateKeybindRows(bindings)
            };
        }

        public static IReadOnlyList<ConfigurationKeybindRow> LoadKeybindRowsFromFile(string filePath)
        {
            SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(filePath);
            if (!analysis.IsValid)
            {
                throw new InvalidDataException(analysis.ErrorMessage ?? "Invalid save/options file.");
            }

            return CreateKeybindRows(ReadBindings(filePath, analysis));
        }

        public static string BuildPendingChangesSummary(ConfigurationPatchRequest request)
        {
            List<string> parts = new();
            if (request.SoundVolumeOverride.HasValue || request.MusicVolumeOverride.HasValue ||
                request.InvertWalkerP1Override.HasValue || request.InvertWalkerP2Override.HasValue ||
                request.InvertFlightP1Override.HasValue || request.InvertFlightP2Override.HasValue ||
                request.VibrationP1Override.HasValue || request.VibrationP2Override.HasValue ||
                request.ControllerConfigP1Override.HasValue || request.ControllerConfigP2Override.HasValue)
            {
                parts.Add("settings overrides");
            }

            if (request.CopyOptionsEntries)
            {
                parts.Add("copied options entries");
            }

            if (request.CopyOptionsTail)
            {
                parts.Add("copied options tail");
            }

            int keybindCount = CountKeybindOverrideRows(request.KeybindRows);
            if (keybindCount > 0)
            {
                parts.Add(keybindCount == 1 ? "1 keybind row" : $"{keybindCount} keybind rows");
            }

            if (parts.Count == 0)
            {
                return "No pending configuration changes selected yet.";
            }

            return "Pending: " + string.Join(", ", parts) + ".";
        }

        public static bool HasPendingChanges(ConfigurationPatchRequest request)
        {
            return request.SoundVolumeOverride.HasValue ||
                   request.MusicVolumeOverride.HasValue ||
                   request.InvertWalkerP1Override.HasValue ||
                   request.InvertWalkerP2Override.HasValue ||
                   request.InvertFlightP1Override.HasValue ||
                   request.InvertFlightP2Override.HasValue ||
                   request.VibrationP1Override.HasValue ||
                   request.VibrationP2Override.HasValue ||
                   request.ControllerConfigP1Override.HasValue ||
                   request.ControllerConfigP2Override.HasValue ||
                   request.CopyOptionsEntries ||
                   request.CopyOptionsTail ||
                   CountKeybindOverrideRows(request.KeybindRows) > 0;
        }

        public static IReadOnlyList<string> ValidateKeybindRows(IReadOnlyList<ConfigurationKeybindRow>? rows)
        {
            if (rows is null || rows.Count == 0)
            {
                return Array.Empty<string>();
            }

            List<string> errors = new();
            foreach (ConfigurationKeybindRow row in rows)
            {
                ValidateToken(row, row.Player1Token, "P1", errors);
                ValidateToken(row, row.Player2Token, "P2", errors);
            }

            return errors;
        }

        public static PatchResult PatchConfiguration(ConfigurationPatchRequest request)
        {
            string inputPath = request.InputPath?.Trim() ?? string.Empty;
            string outputPath = request.OutputPath?.Trim() ?? string.Empty;
            if (inputPath.Length == 0 || outputPath.Length == 0)
            {
                return PatchResult.Fail("Select both input and output .bea paths before patching configuration.");
            }

            if (!SaveEditorService.IsOptionsLikeFilePath(inputPath) || !SaveEditorService.IsOptionsLikeFilePath(outputPath))
            {
                return PatchResult.Fail("Configuration mode requires .bea/defaultoptions.bea input and output paths.");
            }

            if (!File.Exists(inputPath))
            {
                return PatchResult.Fail($"Input file not found: {inputPath}");
            }

            if (!BesFilePatcher.IsValidBesFile(inputPath))
            {
                return PatchResult.Fail($"Input file is not a valid BEA save/options file: {inputPath}");
            }

            if (!HasPendingChanges(request))
            {
                return PatchResult.Fail("Choose at least one configuration override, copied setting, or keybind change to enable patching.");
            }

            IReadOnlyList<string> keybindErrors = ValidateKeybindRows(request.KeybindRows);
            if (keybindErrors.Count > 0)
            {
                return PatchResult.Fail("Invalid keybind overrides:\n" + string.Join("\n", keybindErrors));
            }

            Dictionary<int, BesFilePatcher.OptionsEntryOverride>? keybindOverrides = BuildOptionsEntryOverrides(request.KeybindRows);
            BesFilePatcher patcher = new()
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,
                SoundVolumeOverride = request.SoundVolumeOverride,
                MusicVolumeOverride = request.MusicVolumeOverride,
                InvertYAxisP1Override = request.InvertWalkerP1Override,
                InvertYAxisP2Override = request.InvertWalkerP2Override,
                InvertFlightP1Override = request.InvertFlightP1Override,
                InvertFlightP2Override = request.InvertFlightP2Override,
                VibrationP1Override = request.VibrationP1Override,
                VibrationP2Override = request.VibrationP2Override,
                ControllerConfigP1Override = request.ControllerConfigP1Override,
                ControllerConfigP2Override = request.ControllerConfigP2Override,
                CopyOptionsFromPath = NormalizeOptionalPath(request.CopyOptionsFromPath),
                CopyOptionsEntries = request.CopyOptionsEntries,
                CopyOptionsTail = request.CopyOptionsTail,
                OptionsEntryOverrides = keybindOverrides
            };

            bool inPlacePatch = AreSamePaths(inputPath, outputPath);
            if (!inPlacePatch)
            {
                return patcher.PatchFile(inputPath, outputPath);
            }

            string tempOutput = Path.Combine(
                Path.GetDirectoryName(outputPath) ?? string.Empty,
                Path.GetFileName(outputPath) + ".tmp." + Guid.NewGuid().ToString("N"));

            PatchResult result = patcher.PatchFile(inputPath, tempOutput);
            if (!result.Success)
            {
                TryDeleteTemp(tempOutput);
                return result;
            }

            try
            {
                string backupPath = BuildTimestampedBackupPath(outputPath);
                File.Copy(outputPath, backupPath, overwrite: false);
                File.Copy(tempOutput, outputPath, overwrite: true);
                File.Delete(tempOutput);
                return PatchResult.Ok(
                    $"Successfully patched configuration in place:\n{outputPath}\n\nBackup created:\n{backupPath}");
            }
            catch (Exception ex)
            {
                return PatchResult.Fail(
                    "Patched output was created, but in-place replace failed.\n" +
                    $"Temp patched file: {tempOutput}\n" +
                    $"Error: {ex.Message}");
            }
        }

        public static void LoadOverridesFromSnapshot(IReadOnlyList<ConfigurationKeybindRow> rows)
        {
            foreach (ConfigurationKeybindRow row in rows)
            {
                row.Player1Token = row.CurrentPlayer1Token == "-" ? string.Empty : row.CurrentPlayer1Token;
                row.Player2Token = row.CurrentPlayer2Token == "-" ? string.Empty : row.CurrentPlayer2Token;
            }
        }

        public static void ClearOverrideTokens(IReadOnlyList<ConfigurationKeybindRow> rows)
        {
            foreach (ConfigurationKeybindRow row in rows)
            {
                row.Player1Token = string.Empty;
                row.Player2Token = string.Empty;
            }
        }

        private static ConfigurationKeybindRow CreateKeybindRow(
            KeybindDefinition definition,
            IReadOnlyDictionary<int, (uint Slot0Device, uint Slot0Key, uint Slot1Device, uint Slot1Key)> bindings)
        {
            int loadEntryId = definition.EntryId;
            if (!bindings.ContainsKey(loadEntryId) &&
                definition.MirrorEntryId.HasValue &&
                bindings.ContainsKey(definition.MirrorEntryId.Value))
            {
                loadEntryId = definition.MirrorEntryId.Value;
            }

            string currentP1 = "-";
            string currentP2 = "-";
            if (bindings.TryGetValue(loadEntryId, out var binding))
            {
                currentP1 = BesFilePatcher.FormatBinding(binding.Slot0Device, binding.Slot0Key, loadEntryId);
                currentP2 = BesFilePatcher.FormatBinding(binding.Slot1Device, binding.Slot1Key, loadEntryId);
            }

            return new ConfigurationKeybindRow
            {
                GroupLabel = definition.GroupLabel,
                ActionLabel = definition.ActionLabel,
                EntryId = definition.EntryId,
                KeyboardDeviceCode = definition.KeyboardDeviceCode,
                AllowLookMouse = definition.AllowLookMouse,
                AllowZoomWheel = definition.AllowZoomWheel,
                AllowMouseButtons = definition.AllowMouseButtons,
                MirrorEntryId = definition.MirrorEntryId,
                MirrorKeyboardDeviceCode = definition.MirrorKeyboardDeviceCode,
                CurrentPlayer1Token = currentP1,
                CurrentPlayer2Token = currentP2,
                Player1Token = string.Empty,
                Player2Token = string.Empty
            };
        }

        private static IReadOnlyList<ConfigurationKeybindRow> CreateKeybindRows(
            IReadOnlyDictionary<int, (uint Slot0Device, uint Slot0Key, uint Slot1Device, uint Slot1Key)> bindings)
        {
            return KeybindDefinitions.Select(definition => CreateKeybindRow(definition, bindings)).ToArray();
        }

        private static IReadOnlyDictionary<int, (uint Slot0Device, uint Slot0Key, uint Slot1Device, uint Slot1Key)> ReadBindings(
            string path,
            SaveAnalysis analysis)
        {
            if (analysis.OptionsTailStart == 0 || analysis.OptionsEntryCount <= 0)
            {
                return new Dictionary<int, (uint, uint, uint, uint)>();
            }

            byte[] buf = File.ReadAllBytes(path);
            Dictionary<int, (uint Slot0Device, uint Slot0Key, uint Slot1Device, uint Slot1Key)> bindings = new();
            const int optionsStart = 0x24BE;
            const int entrySize = 0x20;
            for (int i = 0; i < analysis.OptionsEntryCount; i++)
            {
                int off = optionsStart + (entrySize * i);
                if (off + entrySize > buf.Length)
                {
                    break;
                }

                int entryId = BinaryPrimitives.ReadInt32LittleEndian(buf.AsSpan(off + 0x04, 4));
                bindings[entryId] = (
                    BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off + 0x0C, 4)),
                    BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off + 0x10, 4)),
                    BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off + 0x18, 4)),
                    BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off + 0x1C, 4)));
            }

            return bindings;
        }

        private static int CountKeybindOverrideRows(IReadOnlyList<ConfigurationKeybindRow>? rows)
        {
            if (rows is null || rows.Count == 0)
            {
                return 0;
            }

            return rows.Count(row =>
                !string.IsNullOrWhiteSpace(row.Player1Token) ||
                !string.IsNullOrWhiteSpace(row.Player2Token));
        }

        private static void ValidateToken(
            ConfigurationKeybindRow row,
            string? token,
            string slotLabel,
            ICollection<string> errors)
        {
            if (TryValidateKeybindToken(row.EntryId, row.AllowLookMouse, row.AllowZoomWheel, row.AllowMouseButtons, token ?? string.Empty, out string? error))
            {
                return;
            }

            errors.Add($"{row.GroupLabel}: {row.ActionLabel} ({slotLabel}) - {error}");
        }

        private static bool TryValidateKeybindToken(
            int entryId,
            bool allowLookMouse,
            bool allowZoomWheel,
            bool allowMouseButtons,
            string token,
            out string? error)
        {
            error = null;
            if (string.IsNullOrWhiteSpace(token))
            {
                return true;
            }

            string t = token.Trim();
            if (IsKeepToken(t))
            {
                return true;
            }

            if (allowLookMouse && t.StartsWith("Mouse", StringComparison.OrdinalIgnoreCase))
            {
                if (TryValidateLookToken(t))
                {
                    return true;
                }

                error = "Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key.";
                return false;
            }

            if (allowZoomWheel &&
                (t.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase) ||
                 t.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase)))
            {
                return true;
            }

            if (allowMouseButtons &&
                (t.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase) ||
                 t.Equals("MouseRight", StringComparison.OrdinalIgnoreCase)))
            {
                return TryValidateMouseButtonToken(entryId, t, out error);
            }

            if (BesFilePatcher.TryParseKeyboardPackedKey(t, out _, out string? parseError))
            {
                return true;
            }

            error = parseError ?? "Unrecognized key token.";
            return false;
        }

        private static bool TryValidateLookToken(string token)
        {
            string tl = token.Trim().ToLowerInvariant();
            if (tl is "mouse" or "mousex" or "mousey" or "mousex+" or "mousex-" or "mousey+" or "mousey-")
            {
                return true;
            }

            if (tl.StartsWith("mouse(", StringComparison.Ordinal) && tl.EndsWith(")", StringComparison.Ordinal))
            {
                string inner = tl["mouse(".Length..^1];
                return int.TryParse(inner, NumberStyles.Integer, CultureInfo.InvariantCulture, out _);
            }

            return false;
        }

        private static bool TryValidateMouseButtonToken(int entryId, string token, out string? error)
        {
            error = null;
            string normalized = token.Trim().ToLowerInvariant();
            if (normalized == "mouseleft")
            {
                if (entryId is 0x12 or 0x13)
                {
                    return true;
                }

                error = "MouseLeft is only supported for Fire weapon.";
                return false;
            }

            if (normalized == "mouseright")
            {
                if (entryId == 0x14)
                {
                    return true;
                }

                error = "MouseRight is only supported for Select weapon.";
                return false;
            }

            error = "Use MouseLeft/MouseRight.";
            return false;
        }

        private static Dictionary<int, BesFilePatcher.OptionsEntryOverride>? BuildOptionsEntryOverrides(
            IReadOnlyList<ConfigurationKeybindRow>? rows)
        {
            if (rows is null || rows.Count == 0)
            {
                return null;
            }

            Dictionary<int, BesFilePatcher.OptionsEntryOverride> dict = new();

            void setSlot(int entryId, int slotIndex, uint deviceCode, uint packedKey)
            {
                if (!dict.TryGetValue(entryId, out BesFilePatcher.OptionsEntryOverride? overrideEntry))
                {
                    overrideEntry = new BesFilePatcher.OptionsEntryOverride();
                    dict[entryId] = overrideEntry;
                }

                BesFilePatcher.BindingSlotOverride slot = slotIndex == 0 ? overrideEntry.Slot0 : overrideEntry.Slot1;
                slot.DeviceCode = deviceCode;
                slot.PackedKey = packedKey;
            }

            foreach (ConfigurationKeybindRow row in rows)
            {
                if (string.IsNullOrWhiteSpace(row.Player1Token) && string.IsNullOrWhiteSpace(row.Player2Token))
                {
                    continue;
                }

                ParseRow(row, row.EntryId, row.KeyboardDeviceCode, setSlot);
                if (row.MirrorEntryId.HasValue)
                {
                    ParseRow(row, row.MirrorEntryId.Value, row.MirrorKeyboardDeviceCode ?? row.KeyboardDeviceCode, setSlot);
                }
            }

            return dict.Count == 0 ? null : dict;
        }

        private static void ParseRow(
            ConfigurationKeybindRow row,
            int entryId,
            uint keyboardDeviceCode,
            Action<int, int, uint, uint> setSlot)
        {
            if (!string.IsNullOrWhiteSpace(row.Player1Token) && !IsKeepToken(row.Player1Token))
            {
                (uint deviceCode, uint packedKey) = ParseToken(entryId, keyboardDeviceCode, row.AllowLookMouse, row.AllowZoomWheel, row.AllowMouseButtons, row.Player1Token, $"{row.ActionLabel} (P1)");
                setSlot(entryId, 0, deviceCode, packedKey);
            }

            if (!string.IsNullOrWhiteSpace(row.Player2Token) && !IsKeepToken(row.Player2Token))
            {
                (uint deviceCode, uint packedKey) = ParseToken(entryId, keyboardDeviceCode, row.AllowLookMouse, row.AllowZoomWheel, row.AllowMouseButtons, row.Player2Token, $"{row.ActionLabel} (P2)");
                setSlot(entryId, 1, deviceCode, packedKey);
            }
        }

        private static (uint DeviceCode, uint PackedKey) ParseToken(
            int entryId,
            uint keyboardDeviceCode,
            bool allowLookMouse,
            bool allowZoomWheel,
            bool allowMouseButtons,
            string token,
            string fieldName)
        {
            string trimmed = token.Trim();
            if (allowLookMouse && trimmed.StartsWith("Mouse", StringComparison.OrdinalIgnoreCase))
            {
                return ParseLookToken(entryId, trimmed);
            }

            if (allowZoomWheel &&
                (trimmed.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase) ||
                 trimmed.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase)))
            {
                return ParseZoomMouseWheel(trimmed);
            }

            if (allowMouseButtons &&
                (trimmed.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase) ||
                 trimmed.Equals("MouseRight", StringComparison.OrdinalIgnoreCase)))
            {
                return ParseMouseButton(entryId, trimmed);
            }

            if (!BesFilePatcher.TryParseKeyboardPackedKey(trimmed, out uint packed, out string? error))
            {
                throw new ArgumentException($"Invalid {fieldName}: {error}");
            }

            return (keyboardDeviceCode, packed);
        }

        private static (uint DeviceCode, uint PackedKey) ParseLookToken(int entryId, string token)
        {
            static (uint DeviceCode, uint PackedKey) DefaultLookBinding(int currentEntryId)
            {
                return currentEntryId switch
                {
                    0x1B => (11u, 0u),
                    0x19 => (12u, 0u),
                    0x1A => (11u, 1u),
                    0x1C => (12u, 1u),
                    _ => throw new ArgumentException($"Internal error: entry_id 0x{currentEntryId:X} is not a Look entry.")
                };
            }

            string normalized = token.Trim().ToLowerInvariant();
            if (normalized is "mouse" or "mousex" or "mousey")
            {
                return DefaultLookBinding(entryId);
            }

            if (normalized.StartsWith("mousex", StringComparison.Ordinal))
            {
                return normalized.EndsWith("-", StringComparison.Ordinal) ? (12u, 0u) :
                    normalized.EndsWith("+", StringComparison.Ordinal) ? (11u, 0u) :
                    DefaultLookBinding(entryId);
            }

            if (normalized.StartsWith("mousey", StringComparison.Ordinal))
            {
                return normalized.EndsWith("-", StringComparison.Ordinal) ? (12u, 1u) :
                    normalized.EndsWith("+", StringComparison.Ordinal) ? (11u, 1u) :
                    DefaultLookBinding(entryId);
            }

            if (normalized.StartsWith("mouse(", StringComparison.Ordinal) && normalized.EndsWith(")", StringComparison.Ordinal))
            {
                string inner = normalized["mouse(".Length..^1];
                if (int.TryParse(inner, NumberStyles.Integer, CultureInfo.InvariantCulture, out int scanSigned))
                {
                    (uint deviceCode, _) = DefaultLookBinding(entryId);
                    return (deviceCode, unchecked((uint)scanSigned));
                }
            }

            throw new ArgumentException($"Invalid look binding '{token}'. Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key.");
        }

        private static (uint DeviceCode, uint PackedKey) ParseZoomMouseWheel(string token)
        {
            return token.Equals("MouseWheelUp", StringComparison.OrdinalIgnoreCase)
                ? (16u, 3u)
                : token.Equals("MouseWheelDown", StringComparison.OrdinalIgnoreCase)
                    ? (16u, 4u)
                    : throw new ArgumentException($"Invalid zoom binding '{token}'. Use MouseWheelUp/MouseWheelDown or a keyboard key.");
        }

        private static (uint DeviceCode, uint PackedKey) ParseMouseButton(int entryId, string token)
        {
            if (token.Equals("MouseLeft", StringComparison.OrdinalIgnoreCase))
            {
                return entryId switch
                {
                    0x12 => (17u, 0u),
                    0x13 => (15u, 0u),
                    _ => throw new ArgumentException("MouseLeft is only supported for Fire weapon (entry 0x12/0x13).")
                };
            }

            if (token.Equals("MouseRight", StringComparison.OrdinalIgnoreCase))
            {
                return entryId switch
                {
                    0x14 => (16u, 2u),
                    _ => throw new ArgumentException("MouseRight is only supported for Select weapon (entry 0x14).")
                };
            }

            throw new ArgumentException($"Invalid mouse button binding '{token}'. Use MouseLeft/MouseRight.");
        }

        private static bool IsKeepToken(string? token)
        {
            if (string.IsNullOrWhiteSpace(token))
            {
                return true;
            }

            string trimmed = token.Trim();
            return trimmed.Equals("keep", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.Equals("preserve", StringComparison.OrdinalIgnoreCase) ||
                   trimmed.Equals("unchanged", StringComparison.OrdinalIgnoreCase);
        }

        private static string? NormalizeOptionalPath(string? value)
        {
            return string.IsNullOrWhiteSpace(value) ? null : value.Trim();
        }

        private static bool AreSamePaths(string? left, string? right)
        {
            if (string.IsNullOrWhiteSpace(left) || string.IsNullOrWhiteSpace(right))
            {
                return false;
            }

            try
            {
                return string.Equals(
                    Path.GetFullPath(left.Trim()),
                    Path.GetFullPath(right.Trim()),
                    StringComparison.OrdinalIgnoreCase);
            }
            catch
            {
                return false;
            }
        }

        private static string BuildTimestampedBackupPath(string path)
        {
            string directory = Path.GetDirectoryName(path) ?? string.Empty;
            string fileName = Path.GetFileName(path);
            string timestamp = DateTime.Now.ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
            return Path.Combine(directory, $"{fileName}.{timestamp}.bak");
        }

        private static void TryDeleteTemp(string path)
        {
            try
            {
                if (File.Exists(path))
                {
                    File.Delete(path);
                }
            }
            catch
            {
            }
        }
    }
}
