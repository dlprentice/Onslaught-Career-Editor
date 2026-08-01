using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor.Cli
{
    /// <summary>
    /// The career-section options exactly as the user typed them, before any defaulting.
    ///
    /// <see cref="UseNew"/> is nullable on purpose and must stay that way. <c>--new</c> is a boolean
    /// flag, so its <c>false</c> cannot be told apart from silence by value alone; only the presence of
    /// the token distinguishes "the user asked for OLD" from "the user said nothing about goodies". That
    /// distinction is what lets <c>--new --no-goodies</c> be refused instead of silently dropped.
    /// </summary>
    public sealed class CareerPatchOptions
    {
        public bool? UseNew { get; init; }
        public int? Kills { get; init; }
        public string? Rank { get; init; }
        public bool KillsOnly { get; init; }
        public bool NoNodes { get; init; }
        public bool NoLinks { get; init; }
        public bool NoGoodies { get; init; }
        public bool NoKills { get; init; }
        public IReadOnlyList<string>? LevelRanks { get; init; }
        public int? AircraftKills { get; init; }
        public int? VehicleKills { get; init; }
        public int? EmplacementKills { get; init; }
        public int? InfantryKills { get; init; }
        public int? MechKills { get; init; }
    }

    /// <summary>The career options after validation, defaulting, and the discard checks.</summary>
    public sealed class ResolvedCareerPatch
    {
        public string? Rank { get; set; }
        public bool? UseNewGoodiesInstead { get; set; }
        public int? GlobalKillCount { get; set; }
        public Dictionary<int, string>? LevelRanks { get; init; }
        public Dictionary<int, int>? PerCategoryKills { get; init; }
        public bool KillsOnly { get; init; }
        public bool PatchNodes { get; set; }
        public bool PatchLinks { get; set; }
        public bool PatchGoodies { get; set; }
        public bool PatchKills { get; set; }

        /// <summary>
        /// Whether any career pass would run. This gates the .bea guard: an options file must not have
        /// career sections written into it unless the caller asks for that explicitly.
        /// </summary>
        public bool AnyCareerSectionEnabled =>
            PatchNodes || PatchLinks || PatchGoodies || PatchKills;
    }

    public static class CareerPatchPlan
    {
        public static readonly IReadOnlySet<string> ValidRanks =
            new HashSet<string>(StringComparer.Ordinal) { "S", "A", "B", "C", "D", "E", "NONE" };

        /// <summary>
        /// Turn typed options into a plan, or explain the refusal.
        ///
        /// The order of the steps here is load-bearing and matches the original CLI exactly: validate,
        /// then set section switches, then apply the CLI's documented unlock defaults, then run the
        /// discard checks. Defaults are applied only when the owning section is enabled AND the user
        /// configured neither a baseline nor a targeted override for it, which is what keeps a bare
        /// invocation writing what it always wrote (S / 100 / OLD) while stopping
        /// <c>--mech-kills 2000</c> from dragging the other four categories to 100.
        ///
        /// The defaults cannot mask a discarded value: they only fire when the owning section is on, and
        /// the discard check only fires when it is off.
        /// </summary>
        public static bool TryResolve(
            CareerPatchOptions options,
            out ResolvedCareerPatch resolved,
            out string error,
            out IReadOnlyList<string> errorDetails)
        {
            resolved = null!;
            error = string.Empty;
            errorDetails = Array.Empty<string>();

            // Rank validation. `null` means "the user did not pass --rank" and is carried through as
            // such; coercing it to "S" here is what once made `--rank A --no-nodes` and the per-mission
            // overwrite undetectable.
            string? effectiveRank = options.Rank?.ToUpperInvariant();
            if (effectiveRank is not null && !ValidRanks.Contains(effectiveRank))
            {
                error = $"Invalid rank '{options.Rank}'. Valid values: S, A, B, C, D, E, NONE";
                return false;
            }

            Dictionary<int, string>? parsedLevelRanks = null;
            if (options.LevelRanks is { Count: > 0 })
            {
                parsedLevelRanks = new Dictionary<int, string>();
                var levelRankErrors = new List<string>();
                foreach (string entry in options.LevelRanks)
                {
                    string[] parts = entry.Split(':');
                    if (parts.Length == 2 &&
                        int.TryParse(parts[0], out int level) &&
                        level >= 1 && level <= 43)
                    {
                        string levelRank = parts[1].ToUpperInvariant();
                        if (ValidRanks.Contains(levelRank))
                        {
                            // The CLI contract is 1-based (1..43); the patcher indexes nodes from zero.
                            parsedLevelRanks[level - 1] = levelRank;
                        }
                        else
                        {
                            levelRankErrors.Add($"Invalid rank '{parts[1]}' for node index {level}. Valid values: S, A, B, C, D, E, NONE.");
                        }
                    }
                    else
                    {
                        levelRankErrors.Add($"Invalid --level-rank entry '{entry}', expected NODE_INDEX:GRADE (e.g., 1:S).");
                    }
                }

                if (levelRankErrors.Count > 0)
                {
                    // The first specific complaint is the headline, not a generic summary: the existing
                    // CLI regression suite matches on this text, and a caller reading only the first line
                    // of stderr should still learn which entry was wrong.
                    error = levelRankErrors[0];
                    errorDetails = levelRankErrors.Skip(1).ToArray();
                    return false;
                }
            }

            Dictionary<int, int>? perCategoryKills = null;
            if (options.AircraftKills.HasValue || options.VehicleKills.HasValue || options.EmplacementKills.HasValue ||
                options.InfantryKills.HasValue || options.MechKills.HasValue)
            {
                perCategoryKills = new Dictionary<int, int>();
                if (options.AircraftKills.HasValue) perCategoryKills[BesFilePatcher.KILL_AIRCRAFT] = options.AircraftKills.Value;
                if (options.VehicleKills.HasValue) perCategoryKills[BesFilePatcher.KILL_VEHICLES] = options.VehicleKills.Value;
                if (options.EmplacementKills.HasValue) perCategoryKills[BesFilePatcher.KILL_EMPLACEMENTS] = options.EmplacementKills.Value;
                if (options.InfantryKills.HasValue) perCategoryKills[BesFilePatcher.KILL_INFANTRY] = options.InfantryKills.Value;
                if (options.MechKills.HasValue) perCategoryKills[BesFilePatcher.KILL_MECHS] = options.MechKills.Value;
            }

            var plan = new ResolvedCareerPatch
            {
                Rank = effectiveRank,
                UseNewGoodiesInstead = options.UseNew,
                GlobalKillCount = options.Kills,
                LevelRanks = parsedLevelRanks,
                PerCategoryKills = perCategoryKills,
                KillsOnly = options.KillsOnly,
            };

            if (options.KillsOnly)
            {
                // BesFilePatcher.KillsOnly is a computed property whose setter clears the other three
                // switches, so "kills only" really is nodes/links/goodies off with kills on. Expanding it
                // here rather than carrying a separate flag keeps every downstream rule - the defaults
                // and both discard checks - reading the same four switches, which is what makes
                // `--kills-only --level-rank 1:A` refuse for the same reason `--no-nodes` does.
                plan.PatchNodes = false;
                plan.PatchLinks = false;
                plan.PatchGoodies = false;
                plan.PatchKills = true;
            }
            else
            {
                plan.PatchNodes = !options.NoNodes;
                plan.PatchLinks = !options.NoLinks;
                plan.PatchGoodies = !options.NoGoodies;
                plan.PatchKills = !options.NoKills;
            }

            // The CLI's documented "unlock everything" defaults live here, in the layer that also prints
            // them, rather than in AppCore where a default is indistinguishable from silence. Each fires
            // only when its own section is enabled and nothing was configured for it.
            if (plan.PatchNodes && plan.Rank is null && parsedLevelRanks is null or { Count: 0 })
                plan.Rank = "S";

            if (plan.PatchKills && plan.GlobalKillCount is null && perCategoryKills is null or { Count: 0 })
                plan.GlobalKillCount = 100;

            if (plan.PatchGoodies && plan.UseNewGoodiesInstead is null)
                plan.UseNewGoodiesInstead = false;

            // Reject override requests that the section passes would silently discard. These fire before
            // any byte is written, so the user is told rather than handed a green success over a dropped
            // edit.
            if (parsedLevelRanks is { Count: > 0 } && !plan.PatchNodes)
            {
                error = "--level-rank was provided, but node patching is disabled (--no-nodes / --kills-only).";
                errorDetails = new[]
                {
                    "Per-mission ranks are applied through the node pass and would be discarded. " +
                    "Remove --no-nodes/--kills-only or drop --level-rank.",
                };
                return false;
            }

            if (perCategoryKills is { Count: > 0 } && !plan.PatchKills)
            {
                error = "Per-category kill options were provided, but kill patching is disabled (--no-kills).";
                errorDetails = new[]
                {
                    "Per-category kill values are applied through the kill pass and would be discarded. " +
                    "Remove --no-kills or drop the per-category kill options.",
                };
                return false;
            }

            resolved = plan;
            return true;
        }

        public static bool IsOptionsLikePath(string? filePath)
        {
            if (string.IsNullOrWhiteSpace(filePath))
                return false;

            string trimmed = filePath.Trim();
            return string.Equals(Path.GetExtension(trimmed), ".bea", StringComparison.OrdinalIgnoreCase) ||
                   Path.GetFileName(trimmed).StartsWith("defaultoptions.bea", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Project onto the shape <see cref="SavePatchIntentContract"/> reads, so a plan can be checked
        /// for discarded payloads before anything is printed or written.
        ///
        /// <see cref="BesFilePatcher"/> runs the same check internally, but by then it can only report
        /// it as a patch failure. Asking here keeps a contradictory invocation classified as what it is -
        /// a usage error, exit 1 - instead of a verdict about the data.
        /// </summary>
        public static SavePatchIntentSnapshot ToIntentSnapshot(ResolvedCareerPatch plan) => new()
        {
            Rank = plan.Rank,
            UseNewGoodiesInstead = plan.UseNewGoodiesInstead,
            GlobalKillCount = plan.GlobalKillCount,
            LevelRanks = plan.LevelRanks,
            PerCategoryKills = plan.PerCategoryKills,
            PatchNodes = plan.PatchNodes,
            PatchLinks = plan.PatchLinks,
            PatchGoodies = plan.PatchGoodies,
            PatchKills = plan.PatchKills,
        };

        public static object Project(ResolvedCareerPatch plan) => new
        {
            rank = plan.Rank,
            globalKillCount = plan.GlobalKillCount,
            goodieStyle = plan.PatchGoodies
                ? (plan.UseNewGoodiesInstead == true ? "NEW" : "OLD")
                : null,
            killsOnly = plan.KillsOnly,
            patchNodes = plan.PatchNodes,
            patchLinks = plan.PatchLinks,
            patchGoodies = plan.PatchGoodies,
            patchKills = plan.PatchKills,
            levelRanks = plan.LevelRanks?
                .OrderBy(pair => pair.Key)
                .Select(pair => new { nodeIndex = pair.Key + 1, rank = pair.Value })
                .ToArray(),
            perCategoryKills = plan.PerCategoryKills?
                .OrderBy(pair => pair.Key)
                .Select(pair => new { category = KillCategoryName(pair.Key), kills = pair.Value })
                .ToArray(),
        };

        public static string KillCategoryName(int index) => index switch
        {
            BesFilePatcher.KILL_AIRCRAFT => "Aircraft",
            BesFilePatcher.KILL_VEHICLES => "Vehicles",
            BesFilePatcher.KILL_EMPLACEMENTS => "Emplacements",
            BesFilePatcher.KILL_INFANTRY => "Infantry",
            BesFilePatcher.KILL_MECHS => "Mechs",
            _ => $"Category{index}",
        };
    }
}
