using System;
using System.Collections.Generic;
using System.Linq;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// The complete set of career-section payloads a save patch can carry, together with the section
    /// pass that owns each one.
    ///
    /// Why this type exists (2026-07-26). Three separate defects of the same class shipped, each fixed
    /// in isolation:
    ///   1. <c>LevelRanks</c> supplied with node patching disabled -> success, edit dropped.
    ///   2. <c>PerCategoryKills</c> supplied with kill patching disabled -> success, edit dropped.
    ///   3. <c>Rank</c> / <c>GlobalKillCount</c> / <c>UseNewGoodiesInstead</c> supplied with their
    ///      section disabled -> success, edit dropped. Measured on the CLI as
    ///      <c>--rank A --no-nodes</c>, <c>--kills 999 --no-kills</c>, <c>--new --no-goodies</c>,
    ///      all exit 0, all printing the value as configured.
    ///
    /// The third could not be detected at all while the scalars were non-nullable with defaults: the
    /// patcher could not tell "the user asked for S" from "the user said nothing". Every payload is
    /// now nullable, "not configured" is representable, and this one table is the only place that
    /// knows which section owns which payload. <see cref="SavePatchIntentSnapshot"/> is the shape the
    /// table reads, and both <see cref="SavePatchRequest"/> and <see cref="BesFilePatcher"/> project
    /// into it, so the CLI (which drives the patcher directly) and the WinUI surface (which goes
    /// through <see cref="SaveEditorService"/>) are gated by the same predicate.
    ///
    /// A fourth payload cannot be added silently: <c>SavePatchIntentCoverageTests</c> reflects over
    /// every public property of both <see cref="SavePatchRequest"/> and
    /// <see cref="SavePatchIntentSnapshot"/> and fails unless each one is either a routing property,
    /// a section switch, or a registered intent.
    /// </summary>
    public sealed class SavePatchIntentSnapshot
    {
        /// <summary>Baseline mission grade. Null means "keep each mission's current grade".</summary>
        public string? Rank { get; init; }

        /// <summary>Goodie style. Null means "not configured".</summary>
        public bool? UseNewGoodiesInstead { get; init; }

        /// <summary>Baseline kill count. Null means "keep every untargeted category's current count".</summary>
        public int? GlobalKillCount { get; init; }

        /// <summary>Per-mission grade overrides. Null or empty means "not configured".</summary>
        public IReadOnlyDictionary<int, string>? LevelRanks { get; init; }

        /// <summary>Per-category kill overrides. Null or empty means "not configured".</summary>
        public IReadOnlyDictionary<int, int>? PerCategoryKills { get; init; }

        public bool PatchNodes { get; init; } = true;
        public bool PatchLinks { get; init; } = true;
        public bool PatchGoodies { get; init; } = true;
        public bool PatchKills { get; init; } = true;
    }

    public sealed class SavePatchIntent
    {
        public SavePatchIntent(
            string propertyName,
            string displayName,
            string sectionSwitchPropertyName,
            string sectionDisplayName,
            string sectionDisabledHint,
            Func<SavePatchIntentSnapshot, bool> isConfigured,
            Func<SavePatchIntentSnapshot, bool> isSectionEnabled)
        {
            PropertyName = propertyName;
            DisplayName = displayName;
            SectionSwitchPropertyName = sectionSwitchPropertyName;
            SectionDisplayName = sectionDisplayName;
            SectionDisabledHint = sectionDisabledHint;
            IsConfigured = isConfigured;
            IsSectionEnabled = isSectionEnabled;
        }

        /// <summary>Property name on <see cref="SavePatchRequest"/> and <see cref="SavePatchIntentSnapshot"/>.</summary>
        public string PropertyName { get; }

        public string DisplayName { get; }
        public string SectionSwitchPropertyName { get; }
        public string SectionDisplayName { get; }
        public string SectionDisabledHint { get; }
        public Func<SavePatchIntentSnapshot, bool> IsConfigured { get; }
        public Func<SavePatchIntentSnapshot, bool> IsSectionEnabled { get; }
    }

    public sealed class SavePatchSectionPayloadRule
    {
        public SavePatchSectionPayloadRule(
            string sectionSwitchPropertyName,
            string emptyPassMessage,
            Func<SavePatchIntentSnapshot, bool> isSectionEnabled,
            Func<SavePatchIntentSnapshot, bool> hasPayload)
        {
            SectionSwitchPropertyName = sectionSwitchPropertyName;
            EmptyPassMessage = emptyPassMessage;
            IsSectionEnabled = isSectionEnabled;
            HasPayload = hasPayload;
        }

        public string SectionSwitchPropertyName { get; }
        public string EmptyPassMessage { get; }
        public Func<SavePatchIntentSnapshot, bool> IsSectionEnabled { get; }
        public Func<SavePatchIntentSnapshot, bool> HasPayload { get; }
    }

    public static class SavePatchIntentContract
    {
        /// <summary>Properties that address the operation rather than carry a payload.</summary>
        public static IReadOnlyList<string> RoutingPropertyNames { get; } = new[]
        {
            nameof(SavePatchRequest.InputPath),
            nameof(SavePatchRequest.OutputPath)
        };

        /// <summary>The four section switches. A switch is never itself a droppable payload.</summary>
        public static IReadOnlyList<string> SectionSwitchPropertyNames { get; } = new[]
        {
            nameof(SavePatchIntentSnapshot.PatchNodes),
            nameof(SavePatchIntentSnapshot.PatchLinks),
            nameof(SavePatchIntentSnapshot.PatchGoodies),
            nameof(SavePatchIntentSnapshot.PatchKills)
        };

        public static IReadOnlyList<SavePatchIntent> Intents { get; } = new[]
        {
            new SavePatchIntent(
                nameof(SavePatchIntentSnapshot.Rank),
                "A mission rank baseline",
                nameof(SavePatchIntentSnapshot.PatchNodes),
                "mission (node) patching",
                "Enable mission patching or remove the mission rank baseline.",
                snapshot => snapshot.Rank is not null,
                snapshot => snapshot.PatchNodes),

            new SavePatchIntent(
                nameof(SavePatchIntentSnapshot.LevelRanks),
                "Mission rank overrides",
                nameof(SavePatchIntentSnapshot.PatchNodes),
                "mission (node) patching",
                "Enable mission patching or remove the mission rank overrides.",
                snapshot => snapshot.LevelRanks is { Count: > 0 },
                snapshot => snapshot.PatchNodes),

            new SavePatchIntent(
                nameof(SavePatchIntentSnapshot.UseNewGoodiesInstead),
                "A goodie style (NEW/OLD)",
                nameof(SavePatchIntentSnapshot.PatchGoodies),
                "goodie patching",
                "Enable goodie patching or remove the goodie style.",
                snapshot => snapshot.UseNewGoodiesInstead is not null,
                snapshot => snapshot.PatchGoodies),

            new SavePatchIntent(
                nameof(SavePatchIntentSnapshot.GlobalKillCount),
                "A baseline kill count",
                nameof(SavePatchIntentSnapshot.PatchKills),
                "kill patching",
                "Enable kill patching or remove the baseline kill count.",
                snapshot => snapshot.GlobalKillCount is not null,
                snapshot => snapshot.PatchKills),

            new SavePatchIntent(
                nameof(SavePatchIntentSnapshot.PerCategoryKills),
                "Per-category kill overrides",
                nameof(SavePatchIntentSnapshot.PatchKills),
                "kill patching",
                "Enable kill patching or remove the per-category kill overrides.",
                snapshot => snapshot.PerCategoryKills is { Count: > 0 },
                snapshot => snapshot.PatchKills)
        };

        /// <summary>
        /// Return a failure message when any configured payload would be dropped by a disabled
        /// section pass, or null when every configured payload can reach bytes.
        /// </summary>
        public static string? DescribeDiscardedIntents(SavePatchIntentSnapshot snapshot)
        {
            ArgumentNullException.ThrowIfNull(snapshot);

            foreach (SavePatchIntent intent in Intents)
            {
                if (intent.IsConfigured(snapshot) && !intent.IsSectionEnabled(snapshot))
                {
                    return $"{intent.DisplayName} {(intent.DisplayName.EndsWith('s') ? "were" : "was")} requested while " +
                           $"{intent.SectionDisplayName} is disabled. The patcher applies it through that section pass, " +
                           $"so it would be discarded. {intent.SectionDisabledHint}";
                }
            }

            return null;
        }

        /// <summary>
        /// The mirror of <see cref="DescribeDiscardedIntents"/>. Once a payload can be absent, a
        /// section can be switched on with nothing to write. For the two passes whose every write is
        /// payload-driven that is a success message over an empty edit, so it is refused instead.
        ///
        /// The two sections deliberately absent from this list are recorded in
        /// <see cref="SectionsWithoutPayloadRequirement"/> with the reason, and the coverage test
        /// fails if a section appears in neither list.
        /// </summary>
        public static IReadOnlyList<SavePatchSectionPayloadRule> SectionPayloadRules { get; } = new[]
        {
            new SavePatchSectionPayloadRule(
                nameof(SavePatchIntentSnapshot.PatchNodes),
                "Mission (node) patching is enabled but no mission rank baseline and no per-mission " +
                "override were supplied, so the node pass would write nothing at all. Choose a rank " +
                "baseline, or add at least one per-mission override, or disable mission patching.",
                snapshot => snapshot.PatchNodes,
                snapshot => snapshot.Rank is not null || snapshot.LevelRanks is { Count: > 0 }),

            new SavePatchSectionPayloadRule(
                nameof(SavePatchIntentSnapshot.PatchKills),
                "Kill patching is enabled but no baseline kill count and no per-category override " +
                "were supplied, so the kill pass would write nothing at all. Choose a baseline kill " +
                "count, or add at least one per-category override, or disable kill patching.",
                snapshot => snapshot.PatchKills,
                snapshot => snapshot.GlobalKillCount is not null || snapshot.PerCategoryKills is { Count: > 0 }),

            // gpt-5.6-sol and grok-4.5 disagreed here and the disagreement was worth having.
            // grok-4.5 argued null should keep meaning OLD, because `--new --no-goodies` is already
            // detectable from the true value alone and refusing breaks default-constructed callers.
            // gpt-5.6-sol argued fail-closed, because "interpreting null as OLD would turn absence into
            // a rewrite of all 233 displayable dwords from 0x1F46, defeating the reason for making
            // absence representable". Measured: no shipping caller reaches this state — the CLI applies
            // its own default and WinUI only supplies the style when the section is on — so fail-closed
            // costs nothing a user can see and removes the last place where silence still writes bytes.
            new SavePatchSectionPayloadRule(
                nameof(SavePatchIntentSnapshot.PatchGoodies),
                "Goodie patching is enabled but no goodie style was chosen. That pass rewrites all 233 " +
                "displayable Goodie slots to one state, so it must not run on an unstated choice. " +
                "Choose NEW or OLD, or disable goodie patching. For a single slot, use the focused " +
                "Goodie state write instead.",
                snapshot => snapshot.PatchGoodies,
                snapshot => snapshot.UseNewGoodiesInstead is not null)
        };

        /// <summary>
        /// Sections that are intentionally allowed to run without a payload, with the reason.
        /// </summary>
        public static IReadOnlyDictionary<string, string> SectionsWithoutPayloadRequirement { get; } =
            new Dictionary<string, string>
            {
                [nameof(SavePatchIntentSnapshot.PatchLinks)] =
                    "The link pass is the only one with no payload at all: it completes every link whose " +
                    "target node is used, and enabling it is the whole instruction. There is nothing a " +
                    "caller could state or omit, so there is nothing that could be dropped."
            };

        public static string? DescribeEmptySectionPass(SavePatchIntentSnapshot snapshot)
        {
            ArgumentNullException.ThrowIfNull(snapshot);

            foreach (SavePatchSectionPayloadRule rule in SectionPayloadRules)
            {
                if (rule.IsSectionEnabled(snapshot) && !rule.HasPayload(snapshot))
                {
                    return rule.EmptyPassMessage;
                }
            }

            return null;
        }

        public static IReadOnlyList<SavePatchIntent> DescribeConfiguredIntents(SavePatchIntentSnapshot snapshot)
        {
            ArgumentNullException.ThrowIfNull(snapshot);
            return Intents.Where(intent => intent.IsConfigured(snapshot)).ToArray();
        }
    }
}
