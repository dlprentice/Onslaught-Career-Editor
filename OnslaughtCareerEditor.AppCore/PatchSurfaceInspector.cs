using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// How much runtime weight the catalog itself puts behind a row. This grades the
    /// row's own accepted evidence; it never claims the visible effect works on any
    /// machine, which is the boundary the Patch Lab repeats beside every row.
    /// </summary>
    public enum PatchLabRisk
    {
        Low,
        Medium,
        Experimental,
    }

    /// <summary>One byte region of a patch row, presented for inspection.</summary>
    public sealed record PatchLabRegionRow(
        int FileOffset,
        string OriginalHex,
        string PatchedHex);

    /// <summary>
    /// One inspectable patch row: identity, bytes, evidence, and graph facts joined
    /// from <c>patches/catalog/patches.v2.json</c> and the compiled
    /// <see cref="BinaryPatchEngine"/> specs. Read-only; nothing here can mutate a file.
    /// </summary>
    public sealed record PatchLabRow(
        string Key,
        string Title,
        string Track,
        string Purpose,
        string Confidence,
        string ProofLevel,
        IReadOnlyList<string> EvidenceRefs,
        string RollbackStrategy,
        IReadOnlyList<PatchLabRegionRow> Regions,
        bool IsHiddenCompanion,
        bool RequiresWindowedPair,
        string? ExclusiveGroup,
        IReadOnlyList<string> Dependencies,
        IReadOnlyList<string> Conflicts,
        PatchLabRisk Risk,
        string RiskSummary);

    /// <summary>The whole inspectable patch surface plus the engine's own load verdict.</summary>
    public sealed record PatchLabCatalog(
        string CatalogVersion,
        string Status,
        bool UsingFallback,
        IReadOnlyList<PatchLabRow> Rows)
    {
        public int TotalRegions => Rows.Sum(row => row.Regions.Count);
    }

    /// <summary>
    /// A read-only inspection surface over the executable patch catalog for the
    /// WinUI Patch Lab. The compiled specs stay the authority for bytes and graph
    /// policy - the same objects selection validation runs against - while the JSON
    /// contributes the prose evidence fields the compiled record does not carry.
    /// Nothing here stages or applies anything; the Lab's only write-shaped action
    /// routes the row key back into the page's existing guarded selection path.
    /// </summary>
    public static class PatchSurfaceInspector
    {
        private const string CatalogRelativePath = "patches/catalog/patches.v2.json";

        public const string MissingProseNote =
            "The catalog file could not be read right now; showing compiled row facts only.";

        /// <summary>Loads every compiled patch row joined with its catalog prose.</summary>
        public static PatchLabCatalog Load()
        {
            Dictionary<string, JsonElement> proseByKey = TryLoadCatalogProse(out string catalogVersion, out string proseError);

            var visibleKeys = BinaryPatchPlanBuilder.GetVisibleSpecs()
                .Select(spec => spec.Key)
                .ToHashSet(StringComparer.OrdinalIgnoreCase);

            var rows = new List<PatchLabRow>();
            foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs)
            {
                rows.Add(BuildRow(spec, visibleKeys, proseByKey));
            }

            return new PatchLabCatalog(
                catalogVersion,
                string.IsNullOrWhiteSpace(proseError) ? BinaryPatchEngine.CatalogStatus : proseError,
                BinaryPatchEngine.UsingFallbackCatalog || proseByKey.Count == 0,
                rows);
        }

        /// <summary>
        /// Case-insensitive containment filter across the fields a person would
        /// actually search: key, title, purpose, track, and evidence class.
        /// </summary>
        public static IReadOnlyList<PatchLabRow> FilterRows(IReadOnlyList<PatchLabRow> rows, string? query)
        {
            string trimmed = (query ?? string.Empty).Trim();
            if (trimmed.Length == 0)
            {
                return rows;
            }

            return rows
                .Where(row =>
                    row.Key.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.Title.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.Purpose.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.Track.Contains(trimmed, StringComparison.OrdinalIgnoreCase) ||
                    row.ProofLevel.Contains(trimmed, StringComparison.OrdinalIgnoreCase))
                .ToArray();
        }

        private static PatchLabRow BuildRow(
            BinaryPatchSpec spec,
            HashSet<string> visibleKeys,
            Dictionary<string, JsonElement> proseByKey)
        {
            proseByKey.TryGetValue(spec.Key, out JsonElement prose);

            bool hiddenCompanion = !visibleKeys.Contains(spec.Key);
            string track = GetString(prose, "track", spec.Track);
            string proofLevel = GetString(prose, "proof_level", spec.ProofLevel ?? string.Empty);
            string confidence = GetString(prose, "confidence", string.Empty);

            var evidenceRefs = new List<string>();
            if (prose.ValueKind == JsonValueKind.Object &&
                prose.TryGetProperty("evidence_refs", out JsonElement refsEl) &&
                refsEl.ValueKind == JsonValueKind.Array)
            {
                foreach (JsonElement refEl in refsEl.EnumerateArray())
                {
                    if (refEl.ValueKind == JsonValueKind.String)
                    {
                        evidenceRefs.Add(refEl.GetString() ?? string.Empty);
                    }
                }
            }

            var regions = BinaryPatchEngine.GetPatchRegions(spec)
                .Select(region => new PatchLabRegionRow(
                    region.FileOffset,
                    FormatBytes(region.Original),
                    FormatBytes(region.Patched)))
                .ToArray();

            PatchLabRisk risk = ClassifyRisk(track, proofLevel, confidence);

            return new PatchLabRow(
                spec.Key,
                GetString(prose, "title", spec.DisplayName),
                track,
                GetString(prose, "purpose", MissingProseNote),
                confidence,
                proofLevel,
                evidenceRefs.Where(reference => reference.Length > 0).ToArray(),
                GetString(prose, "rollback_strategy",
                    "Restore the copied executable from its verified full-file backup snapshot."),
                regions,
                hiddenCompanion,
                spec.RequiresWindowedPair,
                spec.ExclusiveGroup,
                (spec.Dependencies ?? Array.Empty<string>()).ToArray(),
                (spec.Conflicts ?? Array.Empty<string>()).ToArray(),
                risk,
                DescribeRisk(risk, track, proofLevel, confidence));
        }

        private static PatchLabRisk ClassifyRisk(string track, string proofLevel, string confidence)
        {
            bool experimental =
                string.Equals(track, "experimental", StringComparison.OrdinalIgnoreCase) ||
                proofLevel.StartsWith("experimental_", StringComparison.OrdinalIgnoreCase);
            if (experimental)
            {
                return PatchLabRisk.Experimental;
            }

            return string.Equals(confidence, "high", StringComparison.OrdinalIgnoreCase)
                ? PatchLabRisk.Low
                : PatchLabRisk.Medium;
        }

        private static string DescribeRisk(PatchLabRisk risk, string track, string proofLevel, string confidence)
        {
            return risk switch
            {
                PatchLabRisk.Experimental =>
                    $"Experimental row ('{track}', evidence class '{proofLevel}'). The bytes are checked exactly, but the claimed benefit has bounded or no runtime proof.",
                PatchLabRisk.Low =>
                    $"Accepted evidence class '{proofLevel}' with high confidence. Applied only inside a created safe copy; restore swaps the whole copied executable from its verified backup.",
                _ =>
                    $"Accepted evidence class '{proofLevel}' with {(confidence.Length > 0 ? confidence : "unstated")} confidence. Compare the visible result on your own machine before relying on it.",
            };
        }

        private static string FormatBytes(byte[] bytes)
        {
            return bytes is null || bytes.Length == 0
                ? "(none)"
                : string.Join(" ", bytes.Select(value => value.ToString("X2")));
        }

        private static string GetString(JsonElement prose, string propertyName, string fallback)
        {
            if (prose.ValueKind == JsonValueKind.Object &&
                prose.TryGetProperty(propertyName, out JsonElement element) &&
                element.ValueKind == JsonValueKind.String)
            {
                return element.GetString() ?? fallback;
            }

            return fallback;
        }

        /// <summary>
        /// Reads the catalog JSON once for its prose fields. Resolution mirrors the
        /// engine's own candidate walk (base directory, current directory, then
        /// ancestors) so the Lab and the engine always agree on which file they read;
        /// a miss degrades to compiled facts instead of failing the surface.
        /// </summary>
        private static Dictionary<string, JsonElement> TryLoadCatalogProse(out string catalogVersion, out string error)
        {
            catalogVersion = string.Empty;
            error = string.Empty;

            string? catalogPath = ResolveCatalogPath();
            if (catalogPath is null)
            {
                error = "Catalog file not found.";
                return new Dictionary<string, JsonElement>(StringComparer.OrdinalIgnoreCase);
            }

            try
            {
                using var document = JsonDocument.Parse(File.ReadAllBytes(catalogPath));
                var prose = new Dictionary<string, JsonElement>(StringComparer.OrdinalIgnoreCase);
                if (!document.RootElement.TryGetProperty("patches", out JsonElement patchesEl) ||
                    patchesEl.ValueKind != JsonValueKind.Array)
                {
                    error = "Catalog payload missing patch list.";
                    return prose;
                }

                catalogVersion = document.RootElement.TryGetProperty("catalog_version", out JsonElement versionEl) &&
                    versionEl.ValueKind == JsonValueKind.String
                        ? versionEl.GetString() ?? string.Empty
                        : string.Empty;

                foreach (JsonElement patchEl in patchesEl.EnumerateArray())
                {
                    if (patchEl.ValueKind == JsonValueKind.Object &&
                        patchEl.TryGetProperty("id", out JsonElement idEl) &&
                        idEl.ValueKind == JsonValueKind.String)
                    {
                        prose[idEl.GetString()!] = patchEl.Clone();
                    }
                }

                return prose;
            }
            catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or JsonException)
            {
                error = "The catalog file could not be read for evidence text.";
                return new Dictionary<string, JsonElement>(StringComparer.OrdinalIgnoreCase);
            }
        }

        private static string? ResolveCatalogPath()
        {
            var candidates = new List<string>
            {
                Path.Combine(AppContext.BaseDirectory, CatalogRelativePath),
                Path.Combine(Environment.CurrentDirectory, CatalogRelativePath),
            };

            AddAncestorCandidates(candidates, AppContext.BaseDirectory);
            AddAncestorCandidates(candidates, Environment.CurrentDirectory);

            return candidates
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .FirstOrDefault(File.Exists);
        }

        private static void AddAncestorCandidates(List<string> candidates, string startDirectory)
        {
            DirectoryInfo? current = new(Path.GetFullPath(startDirectory));
            if (File.Exists(current.FullName))
            {
                current = current.Parent;
            }

            while (current is not null)
            {
                candidates.Add(Path.Combine(current.FullName, CatalogRelativePath));
                current = current.Parent;
            }
        }
    }
}
