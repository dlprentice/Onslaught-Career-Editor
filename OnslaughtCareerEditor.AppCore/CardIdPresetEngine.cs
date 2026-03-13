using System;
using System.IO;
using System.Text;

namespace Onslaught___Career_Editor
{
    public enum CardIdPresetState
    {
        Absent,
        Applied,
        CustomManagedBlock,
        MalformedMarkers,
    }

    /// <summary>
    /// Backup-safe manager for cardid.txt preset block used by modern-setup graphics tweaks.
    /// </summary>
    public static class CardIdPresetEngine
    {
        public const string BeginMarker = "// BEGIN OCE_PRESET_MODERN";
        public const string EndMarker = "// END OCE_PRESET_MODERN";
        public const string BackupSuffix = ".original.backup";

        private static string ModernBlock =>
            BeginMarker + "\n" +
            "// Managed by CardIdPresetEngine (Onslaught Toolkit)\n" +
            "// Stable companion lane: modern high-quality tweak defaults.\n" +
            "Tweak:GEFORCE_FX_POWER 1\n" +
            "Tweak:SRT_ENABLE 1\n" +
            "Tweak:IMPOSTOR_ENABLE 1\n" +
            "Tweak:LANDSCAPE_LIGHTING 1\n" +
            "Tweak:SNOW_ENABLE 1\n" +
            "Tweak:GEFORCE_PARTICLE_FOG 1\n" +
            EndMarker + "\n";

        public static string BuildBackupPath(string cardIdPath) => cardIdPath + BackupSuffix;

        public static (bool success, string message, CardIdPresetState state) VerifyFile(string cardIdPath)
        {
            if (string.IsNullOrWhiteSpace(cardIdPath) || !File.Exists(cardIdPath))
                return (false, "Select a valid cardid.txt path first.", CardIdPresetState.Absent);

            string text = File.ReadAllText(cardIdPath, Encoding.UTF8);
            var state = GetState(text);
            string message = state switch
            {
                CardIdPresetState.Absent => "Managed modern preset block is not present in cardid.txt.",
                CardIdPresetState.Applied => "Managed modern preset block is present and current.",
                CardIdPresetState.CustomManagedBlock => "Managed markers found, but block content differs from current preset.",
                CardIdPresetState.MalformedMarkers => "Malformed managed markers found (missing BEGIN or END partner).",
                _ => "Unknown preset state.",
            };

            return (true, message, state);
        }

        public static (bool success, string message) ApplyModernPresetToFile(string cardIdPath)
        {
            if (string.IsNullOrWhiteSpace(cardIdPath) || !File.Exists(cardIdPath))
                return (false, "Select a valid cardid.txt path first.");

            string original = File.ReadAllText(cardIdPath, Encoding.UTF8);
            var state = GetState(original);
            if (state == CardIdPresetState.MalformedMarkers)
                return (false, "Apply aborted: malformed managed markers detected in cardid.txt. Restore from backup or fix markers first.");

            string updated;
            string action;
            if (TryGetManagedBlockBounds(original, out int blockStart, out int blockEnd, out _))
            {
                updated = original.Substring(0, blockStart) + ModernBlock + original.Substring(blockEnd);
                action = "replaced";
            }
            else
            {
                string sep = original.EndsWith("\n", StringComparison.Ordinal) ? string.Empty : "\n";
                updated = original + sep + ModernBlock;
                action = "appended";
            }

            if (NormalizeNewlines(updated) == NormalizeNewlines(original))
                return (true, "No changes needed: managed modern preset block is already current.");

            string backupPath = BuildBackupPath(cardIdPath);
            if (!File.Exists(backupPath))
                File.Copy(cardIdPath, backupPath, overwrite: false);

            File.WriteAllText(cardIdPath, updated, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));

            return (true,
                "cardid.txt preset apply complete.\n" +
                $"Target: {cardIdPath}\n" +
                $"Backup: {backupPath}\n" +
                $"Action: {action}");
        }

        public static (bool success, string message) RestoreFromBackup(string cardIdPath)
        {
            if (string.IsNullOrWhiteSpace(cardIdPath) || !File.Exists(cardIdPath))
                return (false, "Select a valid cardid.txt path first.");

            string backupPath = BuildBackupPath(cardIdPath);
            if (!File.Exists(backupPath))
                return (false, $"Backup file not found: {backupPath}");

            File.Copy(backupPath, cardIdPath, overwrite: true);
            return (true,
                "Restore complete.\n" +
                $"Target: {cardIdPath}\n" +
                $"Backup source: {backupPath}");
        }

        private static CardIdPresetState GetState(string text)
        {
            bool hasBegin = text.Contains(BeginMarker, StringComparison.Ordinal);
            bool hasEnd = text.Contains(EndMarker, StringComparison.Ordinal);

            if (!hasBegin && !hasEnd)
                return CardIdPresetState.Absent;
            if (hasBegin != hasEnd)
                return CardIdPresetState.MalformedMarkers;

            if (!TryGetManagedBlockBounds(text, out int start, out int end, out _))
                return CardIdPresetState.MalformedMarkers;

            string currentBlock = text.Substring(start, end - start);
            return NormalizeNewlines(currentBlock) == NormalizeNewlines(ModernBlock)
                ? CardIdPresetState.Applied
                : CardIdPresetState.CustomManagedBlock;
        }

        private static bool TryGetManagedBlockBounds(string text, out int start, out int endExclusive, out string error)
        {
            start = -1;
            endExclusive = -1;
            error = string.Empty;

            int begin = text.IndexOf(BeginMarker, StringComparison.Ordinal);
            int end = text.IndexOf(EndMarker, StringComparison.Ordinal);

            if (begin < 0 || end < 0)
                return false;
            if (end < begin)
            {
                error = "END marker appears before BEGIN marker.";
                return false;
            }

            endExclusive = end + EndMarker.Length;
            while (endExclusive < text.Length && (text[endExclusive] == '\r' || text[endExclusive] == '\n'))
                endExclusive++;

            start = begin;
            return true;
        }

        private static string NormalizeNewlines(string value) =>
            value.Replace("\r\n", "\n", StringComparison.Ordinal)
                 .Replace("\r", "\n", StringComparison.Ordinal);
    }
}
