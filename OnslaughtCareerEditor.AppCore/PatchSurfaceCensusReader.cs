using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// One candidate site from <c>patches/patch-surface-rows.tsv</c>. The nine
    /// fields are the census lane's columns exactly; this type does not invent a
    /// tenth. Census rows are research experiments, not product patches; the
    /// staging service can write them into a safe copy, never an installed game.
    /// </summary>
    public sealed record PatchCensusRow(
        string Va,
        string Offset,
        string OriginalBytes,
        string PatchedBytes,
        string Effect,
        string Confidence,
        string EvidencePath,
        string Risk,
        string CheapestVerification)
    {
        /// <summary>Evidence refs split on the census lane's ';' separator.</summary>
        public IReadOnlyList<string> EvidenceRefs =>
            string.IsNullOrWhiteSpace(EvidencePath)
                ? Array.Empty<string>()
                : EvidencePath.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        public string OriginalHexDisplay => FormatHex(OriginalBytes);

        public string PatchedHexDisplay => FormatHex(PatchedBytes);

        private static string FormatHex(string compact)
        {
            if (string.IsNullOrWhiteSpace(compact))
            {
                return "(none)";
            }

            string hex = compact.Trim();
            if (hex.Length % 2 != 0)
            {
                return hex;
            }

            var parts = new string[hex.Length / 2];
            for (int i = 0; i < parts.Length; i++)
            {
                parts[i] = hex.Substring(i * 2, 2).ToUpperInvariant();
            }

            return string.Join(" ", parts);
        }
    }

    /// <summary>The census TSV when present, or an honest miss when it is not.</summary>
    public sealed record PatchCensusCatalog(
        bool Found,
        string Status,
        string? SourceKind,
        IReadOnlyList<PatchCensusRow> Rows)
    {
        public int MeasuredCount =>
            Rows.Count(row => string.Equals(row.Confidence, "MEASURED", StringComparison.OrdinalIgnoreCase));

        public int StaticOnlyCount =>
            Rows.Count(row => string.Equals(row.Confidence, "STATIC_ONLY", StringComparison.OrdinalIgnoreCase));

        public int SpeculativeCount =>
            Rows.Count(row => string.Equals(row.Confidence, "SPECULATIVE", StringComparison.OrdinalIgnoreCase));
    }

    /// <summary>
    /// Read-only consumer of the census lane's <c>patches/patch-surface-rows.tsv</c>.
    /// The header and nine columns are the census owner's contract; this reader
    /// refuses a forked header instead of inventing a second format. Nothing here
    /// writes, or treats a census row as a product patch; staging is the separate
    /// <see cref="PatchCensusStagingService"/>, safe copies only.
    /// </summary>
    public static class PatchSurfaceCensusReader
    {
        public const string RelativePath = "patches/patch-surface-rows.tsv";

        public static readonly IReadOnlyList<string> RequiredColumns = new[]
        {
            "va",
            "offset",
            "original_bytes",
            "patched_bytes",
            "effect",
            "confidence",
            "evidence_path",
            "risk",
            "cheapest_verification",
        };

        public const string MissingStatus =
            "Census TSV not present in this checkout. The Lab still inspects product catalog rows above. Candidates appear here when patches/patch-surface-rows.tsv sits in this repo or a sibling worktree.";

        public const string HeaderMismatchStatus =
            "Census TSV header does not match the census lane's contract (va, offset, original_bytes, patched_bytes, effect, confidence, evidence_path, risk, cheapest_verification). Nothing was read.";

        /// <summary>
        /// Resolves <see cref="RelativePath"/> the same way the catalog prose walk
        /// does, then also looks at sibling git worktrees under <c>.worktrees/</c>
        /// so a companion checkout can consume the census branch's file without
        /// copying or forking it.
        /// </summary>
        public static PatchCensusCatalog Load()
        {
            string? path = ResolveCensusPath();
            if (path is null)
            {
                return new PatchCensusCatalog(false, MissingStatus, null, Array.Empty<PatchCensusRow>());
            }

            return LoadFrom(path);
        }

        /// <summary>Parses one TSV file. Used by tests and by <see cref="Load"/>.</summary>
        public static PatchCensusCatalog LoadFrom(string path)
        {
            if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            {
                return new PatchCensusCatalog(false, MissingStatus, null, Array.Empty<PatchCensusRow>());
            }

            try
            {
                string[] lines = File.ReadAllLines(path);
                if (lines.Length == 0)
                {
                    return new PatchCensusCatalog(false, HeaderMismatchStatus, null, Array.Empty<PatchCensusRow>());
                }

                string[] header = SplitTsv(StripBom(lines[0]));
                if (!HeaderMatches(header))
                {
                    return new PatchCensusCatalog(false, HeaderMismatchStatus, null, Array.Empty<PatchCensusRow>());
                }

                var rows = new List<PatchCensusRow>();
                for (int i = 1; i < lines.Length; i++)
                {
                    string line = lines[i];
                    if (string.IsNullOrWhiteSpace(line))
                    {
                        continue;
                    }

                    string[] cells = SplitTsv(line);
                    if (cells.Length < RequiredColumns.Count)
                    {
                        continue;
                    }

                    rows.Add(new PatchCensusRow(
                        cells[0].Trim(),
                        cells[1].Trim(),
                        cells[2].Trim(),
                        cells[3].Trim(),
                        cells[4].Trim(),
                        cells[5].Trim(),
                        cells[6].Trim(),
                        cells[7].Trim(),
                        cells[8].Trim()));
                }

                string sourceKind = ClassifySource(path);
                string status =
                    $"{rows.Count} census candidate{(rows.Count == 1 ? "" : "s")} from patch-surface-rows.tsv" +
                    $" ({sourceKind}; MEASURED {rows.Count(row => string.Equals(row.Confidence, "MEASURED", StringComparison.OrdinalIgnoreCase))}" +
                    $", STATIC_ONLY {rows.Count(row => string.Equals(row.Confidence, "STATIC_ONLY", StringComparison.OrdinalIgnoreCase))}" +
                    $", SPECULATIVE {rows.Count(row => string.Equals(row.Confidence, "SPECULATIVE", StringComparison.OrdinalIgnoreCase))}" +
                    "). These are research experiments, not product patches: staging writes their bytes into a safe copy only.";

                return new PatchCensusCatalog(true, status, sourceKind, rows);
            }
            catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
            {
                return new PatchCensusCatalog(
                    false,
                    "The census TSV could not be read right now. Product catalog rows above are unchanged.",
                    null,
                    Array.Empty<PatchCensusRow>());
            }
        }

        /// <summary>
        /// Case-insensitive containment across the fields a person would search:
        /// VA, offset, effect, confidence, evidence path, risk, and verification.
        /// </summary>
        public static IReadOnlyList<PatchCensusRow> FilterRows(IReadOnlyList<PatchCensusRow> rows, string? query)
        {
            string trimmed = (query ?? string.Empty).Trim();
            if (trimmed.Length == 0)
            {
                return rows;
            }

            return rows
                .Where(row =>
                    row.Va.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.Offset.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.Effect.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.Confidence.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.EvidencePath.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.Risk.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.CheapestVerification.Contains(trimmed, StringComparison.OrdinalIgnoreCase))
                .ToArray();
        }

        private static bool HeaderMatches(string[] header)
        {
            if (header.Length < RequiredColumns.Count)
            {
                return false;
            }

            for (int i = 0; i < RequiredColumns.Count; i++)
            {
                if (!string.Equals(header[i].Trim(), RequiredColumns[i], StringComparison.OrdinalIgnoreCase))
                {
                    return false;
                }
            }

            return true;
        }

        private static string[] SplitTsv(string line)
        {
            return line.Split('\t');
        }

        private static string StripBom(string value)
        {
            return value.Length > 0 && value[0] == '\uFEFF' ? value[1..] : value;
        }

        private static string ClassifySource(string path)
        {
            try
            {
                string full = Path.GetFullPath(path);
                return full.IndexOf($"{Path.DirectorySeparatorChar}.worktrees{Path.DirectorySeparatorChar}", StringComparison.OrdinalIgnoreCase) >= 0
                    || full.IndexOf($"{Path.AltDirectorySeparatorChar}.worktrees{Path.AltDirectorySeparatorChar}", StringComparison.OrdinalIgnoreCase) >= 0
                    ? "sibling or this worktree"
                    : "this checkout";
            }
            catch (Exception exception) when (exception is ArgumentException or PathTooLongException)
            {
                return "this checkout";
            }
        }

        private static string? ResolveCensusPath()
        {
            var candidates = new List<string>
            {
                Path.Combine(AppContext.BaseDirectory, RelativePath),
                Path.Combine(Environment.CurrentDirectory, RelativePath),
            };

            AddAncestorCandidates(candidates, AppContext.BaseDirectory);
            AddAncestorCandidates(candidates, Environment.CurrentDirectory);
            AddSiblingWorktreeCandidates(candidates, AppContext.BaseDirectory);
            AddSiblingWorktreeCandidates(candidates, Environment.CurrentDirectory);

            return candidates
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .FirstOrDefault(File.Exists);
        }

        private static void AddAncestorCandidates(List<string> candidates, string startDirectory)
        {
            DirectoryInfo? current = StartDirectory(startDirectory);
            while (current is not null)
            {
                candidates.Add(Path.Combine(current.FullName, RelativePath));
                current = current.Parent;
            }
        }

        private static void AddSiblingWorktreeCandidates(List<string> candidates, string startDirectory)
        {
            DirectoryInfo? current = StartDirectory(startDirectory);
            while (current is not null)
            {
                if (string.Equals(current.Name, ".worktrees", StringComparison.OrdinalIgnoreCase))
                {
                    try
                    {
                        foreach (DirectoryInfo sibling in current.EnumerateDirectories())
                        {
                            candidates.Add(Path.Combine(sibling.FullName, RelativePath));
                        }
                    }
                    catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
                    {
                        // A locked sibling is skipped; the miss status covers it.
                    }
                }

                current = current.Parent;
            }
        }

        private static DirectoryInfo? StartDirectory(string startDirectory)
        {
            try
            {
                DirectoryInfo current = new(Path.GetFullPath(startDirectory));
                return File.Exists(current.FullName) ? current.Parent : current;
            }
            catch (Exception exception) when (exception is ArgumentException or PathTooLongException or IOException)
            {
                return null;
            }
        }
    }
}
