using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed record BinaryPatchSpec(
        string Key,
        string Track,
        string DisplayName,
        int FileOffset,
        byte[] Original,
        byte[] Patched,
        bool Optional = false);

    public enum BinaryPatchState
    {
        Original,
        Patched,
        Mismatch,
        OutOfRange,
    }

    public sealed record BinaryPatchVerifyRow(BinaryPatchSpec Spec, BinaryPatchState State);

    internal sealed record BinaryPatchCatalogLoadResult(
        BinaryPatchSpec[] Specs,
        bool UsingFallback,
        string Status);

    /// <summary>
    /// Core byte-verified patch engine for BEA.exe catalog-driven patches.
    /// </summary>
    public static class BinaryPatchEngine
    {
        public const string BackupSuffix = ".original.backup";
        private const string CatalogRelativePath = "patches/catalog/patches.v2.json";

        private static readonly BinaryPatchSpec[] s_fallbackPatchSpecs =
        {
            new(
                Key: "resolution_gate",
                Track: "Stable",
                DisplayName: "Allow widescreen resolutions (remove 4:3-only rejection)",
                FileOffset: 0x129696,
                Original: new byte[] { 0xCC },
                Patched: new byte[] { 0x00 }),
            new(
                Key: "force_windowed",
                Track: "Stable",
                DisplayName: "Prefer windowed startup (when windowed-capable)",
                FileOffset: 0x12A644,
                Original: new byte[] { 0xA1, 0xF0, 0x2D, 0x66, 0x00 },
                Patched: new byte[] { 0xB8, 0x01, 0x00, 0x00, 0x00 }),
            new(
                Key: "extra_graphics_default_on",
                Track: "Stable",
                DisplayName: "Unlock extra graphics features by default (disable cardid gate default)",
                FileOffset: 0x0CDD40,
                Original: new byte[] { 0x6A, 0x00 },
                Patched: new byte[] { 0x6A, 0x01 }),
            new(
                Key: "ignore_cardid_tweak_overrides",
                Track: "Stable",
                DisplayName: "Ignore cardid.txt vendor/device tweak overrides",
                FileOffset: 0x12AF3F,
                Original: new byte[] { 0xE8, 0x9C, 0xD7, 0xFF, 0xFF },
                Patched: new byte[] { 0x90, 0x90, 0x90, 0x90, 0x90 }),
            new(
                Key: "version_overlay_use_patched_format_pointer",
                Track: "Stable",
                DisplayName: "Version overlay pointer -> patched format cave",
                FileOffset: 0x6416F,
                Original: new byte[] { 0x54, 0x94, 0x62, 0x00 },
                Patched: new byte[] { 0x44, 0xA4, 0x5A, 0x00 }),
            new(
                Key: "version_overlay_patched_format_cave_string",
                Track: "Stable",
                DisplayName: "Version overlay cave format payload (V%1d.%02d - PATCHED)",
                FileOffset: 0x1AA444,
                Original: new byte[] { 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC },
                Patched: new byte[] { 0x56, 0x25, 0x31, 0x64, 0x2E, 0x25, 0x30, 0x32, 0x64, 0x20, 0x2D, 0x20, 0x50, 0x41, 0x54, 0x43, 0x48, 0x45, 0x44, 0x00 }),
            new(
                Key: "skip_auto_toggle",
                Track: "Experimental",
                DisplayName: "Optional: prevent auto-switch back to fullscreen",
                FileOffset: 0x12BB97,
                Original: new byte[] { 0x75, 0x20 },
                Patched: new byte[] { 0xEB, 0x20 },
                Optional: true),
        };

        private static readonly BinaryPatchCatalogLoadResult s_catalogLoad = LoadPatchSpecsFromCatalog();

        public static IReadOnlyList<BinaryPatchSpec> PatchSpecs => s_catalogLoad.Specs;
        public static bool UsingFallbackCatalog => s_catalogLoad.UsingFallback;
        public static string CatalogStatus => s_catalogLoad.Status;

        public static string BuildBackupPath(string exePath) => exePath + BackupSuffix;

        private static BinaryPatchCatalogLoadResult LoadPatchSpecsFromCatalog()
        {
            string? catalogPath = ResolveCatalogPath();
            if (catalogPath is null)
            {
                return new BinaryPatchCatalogLoadResult(
                    s_fallbackPatchSpecs,
                    UsingFallback: true,
                    Status: "Catalog unavailable; using built-in fallback patch specs.");
            }

            try
            {
                using var doc = JsonDocument.Parse(File.ReadAllText(catalogPath));
                if (!doc.RootElement.TryGetProperty("patches", out JsonElement patchesEl) ||
                    patchesEl.ValueKind != JsonValueKind.Array)
                {
                    return new BinaryPatchCatalogLoadResult(
                        s_fallbackPatchSpecs,
                        UsingFallback: true,
                        Status: "Catalog payload missing patch list; using built-in fallback patch specs.");
                }

                var loaded = new List<BinaryPatchSpec>();
                foreach (JsonElement patchEl in patchesEl.EnumerateArray())
                {
                    if (!TryParsePatchSpec(patchEl, out BinaryPatchSpec? spec) || spec is null)
                        continue;

                    loaded.Add(spec);
                }

                if (loaded.Count == 0)
                {
                    return new BinaryPatchCatalogLoadResult(
                        s_fallbackPatchSpecs,
                        UsingFallback: true,
                        Status: "Catalog contained no valid patch rows; using built-in fallback patch specs.");
                }

                return new BinaryPatchCatalogLoadResult(
                    loaded.ToArray(),
                    UsingFallback: false,
                    Status: $"Loaded patch catalog from {catalogPath}");
            }
            catch (Exception ex)
            {
                return new BinaryPatchCatalogLoadResult(
                    s_fallbackPatchSpecs,
                    UsingFallback: true,
                    Status: $"Catalog read failed ({ex.Message}); using built-in fallback patch specs.");
            }
        }

        private static string? ResolveCatalogPath()
        {
            string[] candidates =
            {
                Path.Combine(AppContext.BaseDirectory, CatalogRelativePath),
                Path.Combine(Environment.CurrentDirectory, CatalogRelativePath),
            };

            foreach (string candidate in candidates.Distinct(StringComparer.OrdinalIgnoreCase))
            {
                if (File.Exists(candidate))
                    return candidate;
            }

            return null;
        }

        private static bool TryParsePatchSpec(JsonElement patchEl, out BinaryPatchSpec? spec)
        {
            spec = null;

            if (!TryGetString(patchEl, "id", out string key) ||
                !TryGetString(patchEl, "title", out string displayName) ||
                !TryGetString(patchEl, "track", out string track) ||
                !patchEl.TryGetProperty("file_offset", out JsonElement fileOffsetEl) ||
                !TryParseOffset(fileOffsetEl, out int fileOffset) ||
                !TryGetString(patchEl, "expected_original_bytes", out string originalHex) ||
                !TryGetString(patchEl, "patched_bytes", out string patchedHex) ||
                !TryParseHexBytes(originalHex, out byte[]? originalBytesMaybe) ||
                !TryParseHexBytes(patchedHex, out byte[]? patchedBytesMaybe))
            {
                return false;
            }
            byte[] originalBytes = originalBytesMaybe!;
            byte[] patchedBytes = patchedBytesMaybe!;
            if (originalBytes.Length != patchedBytes.Length)
                return false;

            bool optional = false;
            if (patchEl.TryGetProperty("optional", out JsonElement optionalEl) &&
                optionalEl.ValueKind == JsonValueKind.True)
            {
                optional = true;
            }

            spec = new BinaryPatchSpec(
                Key: key,
                Track: NormalizeTrack(track),
                DisplayName: displayName,
                FileOffset: fileOffset,
                Original: originalBytes,
                Patched: patchedBytes,
                Optional: optional);
            return true;
        }

        private static string NormalizeTrack(string track)
        {
            if (string.Equals(track, "stable", StringComparison.OrdinalIgnoreCase))
                return "Stable";
            if (string.Equals(track, "experimental", StringComparison.OrdinalIgnoreCase))
                return "Experimental";
            return track.Trim();
        }

        private static bool TryGetString(JsonElement parent, string propertyName, out string value)
        {
            value = string.Empty;
            if (!parent.TryGetProperty(propertyName, out JsonElement el) || el.ValueKind != JsonValueKind.String)
                return false;

            string? raw = el.GetString();
            if (string.IsNullOrWhiteSpace(raw))
                return false;

            value = raw.Trim();
            return true;
        }

        private static bool TryParseOffset(JsonElement el, out int offset)
        {
            offset = 0;
            try
            {
                if (el.ValueKind == JsonValueKind.Number)
                {
                    return el.TryGetInt32(out offset);
                }

                if (el.ValueKind != JsonValueKind.String)
                    return false;

                string raw = (el.GetString() ?? string.Empty).Trim();
                if (raw.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
                {
                    return int.TryParse(
                        raw.AsSpan(2),
                        System.Globalization.NumberStyles.HexNumber,
                        System.Globalization.CultureInfo.InvariantCulture,
                        out offset);
                }

                return int.TryParse(raw, out offset);
            }
            catch
            {
                return false;
            }
        }

        private static bool TryParseHexBytes(string raw, out byte[]? bytes)
        {
            bytes = null;
            if (string.IsNullOrWhiteSpace(raw))
                return false;

            string[] tokens = raw.Split(new[] { ' ', '\t', '\r', '\n', ',', ';', '-' }, StringSplitOptions.RemoveEmptyEntries);
            var list = new List<byte>(tokens.Length);

            foreach (string token in tokens)
            {
                string t = token.Trim();
                if (t.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
                    t = t.Substring(2);

                if (t.Length == 0)
                    continue;

                if (!byte.TryParse(
                        t,
                        System.Globalization.NumberStyles.HexNumber,
                        System.Globalization.CultureInfo.InvariantCulture,
                        out byte b))
                {
                    return false;
                }

                list.Add(b);
            }

            if (list.Count == 0)
                return false;

            bytes = list.ToArray();
            return true;
        }

        public static BinaryPatchState GetPatchState(byte[] data, BinaryPatchSpec spec)
        {
            int length = spec.Original.Length;
            if (length != spec.Patched.Length)
                return BinaryPatchState.Mismatch;
            if (spec.FileOffset < 0 || spec.FileOffset + length > data.Length)
                return BinaryPatchState.OutOfRange;

            ReadOnlySpan<byte> current = data.AsSpan(spec.FileOffset, length);
            if (current.SequenceEqual(spec.Patched))
                return BinaryPatchState.Patched;
            if (current.SequenceEqual(spec.Original))
                return BinaryPatchState.Original;
            return BinaryPatchState.Mismatch;
        }

        public static (bool allKnown, bool allPatched, List<BinaryPatchVerifyRow> rows) VerifyPatchSpecs(
            byte[] data,
            IReadOnlyList<BinaryPatchSpec> specs)
        {
            var rows = new List<BinaryPatchVerifyRow>(specs.Count);
            bool allKnown = true;
            bool allPatched = true;

            foreach (var spec in specs)
            {
                BinaryPatchState state = GetPatchState(data, spec);
                rows.Add(new BinaryPatchVerifyRow(spec, state));
                if (state == BinaryPatchState.Original)
                    allPatched = false;
                if (state is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange)
                {
                    allKnown = false;
                    allPatched = false;
                }
            }

            return (allKnown, allPatched, rows);
        }

        public static (bool success, string message) ApplyPatchesToFile(string exePath, IReadOnlyList<BinaryPatchSpec> selected)
        {
            if (string.IsNullOrWhiteSpace(exePath) || !File.Exists(exePath))
                return (false, "Select a valid BEA.exe path first.");

            if (selected.Count == 0)
                return (false, "Select at least one patch to apply.");

            byte[] data = File.ReadAllBytes(exePath);
            var (_, _, rows) = VerifyPatchSpecs(data, selected);

            if (rows.Any(r => r.State is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange))
            {
                var abortSb = new StringBuilder();
                abortSb.AppendLine("Apply aborted: unexpected patch state detected.");
                abortSb.AppendLine();
                foreach (var row in rows)
                    abortSb.AppendLine($"[{row.Spec.Track} | {row.Spec.DisplayName}] @ 0x{row.Spec.FileOffset:X}: {StateLabel(row.State)}");
                return (false, abortSb.ToString());
            }

            if (rows.All(r => r.State == BinaryPatchState.Patched))
            {
                return (true, "No changes needed. All selected patches are already applied.");
            }

            string backupPath = BuildBackupPath(exePath);
            if (!File.Exists(backupPath))
            {
                File.Copy(exePath, backupPath, overwrite: false);
            }

            foreach (var row in rows)
            {
                if (row.State == BinaryPatchState.Original)
                {
                    row.Spec.Patched.CopyTo(data, row.Spec.FileOffset);
                }
            }

            File.WriteAllBytes(exePath, data);

            var (_, _, afterRows) = VerifyPatchSpecs(data, selected);
            var outSb = new StringBuilder();
            outSb.AppendLine("Patch apply complete.");
            outSb.AppendLine($"Target: {exePath}");
            outSb.AppendLine($"Backup: {backupPath}");
            outSb.AppendLine("Restore uses the first full-file backup snapshot, not per-patch undo.");
            outSb.AppendLine();
            outSb.AppendLine("Selected patch states:");
            foreach (var row in afterRows)
                outSb.AppendLine($"[{row.Spec.Track} | {row.Spec.DisplayName}] @ 0x{row.Spec.FileOffset:X}: {StateLabel(row.State)}");
            return (true, outSb.ToString());
        }

        public static (bool success, string message) RestoreFromBackup(string exePath)
        {
            if (string.IsNullOrWhiteSpace(exePath))
                return (false, "Select a valid BEA.exe path first.");

            string backupPath = BuildBackupPath(exePath);
            if (!File.Exists(backupPath))
                return (false, $"Backup file not found: {backupPath}");

            File.Copy(backupPath, exePath, overwrite: true);
            return (true,
                "Restore complete.\n" +
                $"Target: {exePath}\n" +
                $"Backup source: {backupPath}\n" +
                "Result: full executable restored from the original backup snapshot.");
        }

        public static string RenderStateReport(string exePath, IReadOnlyList<BinaryPatchVerifyRow> rows, string summary)
        {
            var sb = new StringBuilder();
            sb.AppendLine($"Target: {exePath}");
            sb.AppendLine();

            foreach (var row in rows)
                sb.AppendLine($"[{row.Spec.Track} | {row.Spec.DisplayName}] @ 0x{row.Spec.FileOffset:X}: {StateLabel(row.State)}");

            sb.AppendLine();
            sb.AppendLine(summary);
            return sb.ToString();
        }

        public static string StateLabel(BinaryPatchState state) => state switch
        {
            BinaryPatchState.Original => "ready (original)",
            BinaryPatchState.Patched => "already patched",
            BinaryPatchState.Mismatch => "unexpected bytes",
            BinaryPatchState.OutOfRange => "offset out of range",
            _ => "unknown",
        };
    }
}
