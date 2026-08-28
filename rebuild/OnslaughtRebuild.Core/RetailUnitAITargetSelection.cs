// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// Released <c>CUnitAI</c> close-target profile fields. The seven priority
/// cells are the exact output array of <c>CUnitAttackPriority</c> indices
/// 0..6; <c>CUnitIndiscriminate</c> owns <c>config+0x128</c>.
/// </summary>
/// <remarks>
/// Offsets remain in the names so the semantic labels cannot drift away from
/// the measured retail layout.
/// </remarks>
public readonly record struct RetailUnitAITargetProfile(
    int Indiscriminate128,
    int ScoreGate138,
    float MaximumDistance158,
    float EmplacementPriority164,
    float VehiclePriority168,
    float BuildingPriority16C,
    float NavalPriority170,
    float InfantryPriority174,
    float AirUnitPriority178,
    float ComponentPriority17C);

/// <summary>
/// One ordered, resolved candidate transcript for the scoring kernel.
/// Candidate pointer resolution, side-list selection, and the capability
/// helper remain outside this type. The state and allegiance gates are reduced
/// here from their exact raw retail fields.
/// </summary>
public readonly record struct RetailUnitAITargetCandidate(
    uint ThingFlags2C,
    uint TypeFlags34,
    int UnitMode244,
    int Allegiance138,
    float DistanceSquared,
    float RangeReductionPercent,
    int CandidateCapabilityGate,
    int ScoreGate164,
    float SupportMinimum,
    float SupportMaximum);

/// <summary>
/// The finite-domain scoring kernel in retail PC
/// <c>0x004FF710..0x004FFB57</c>, independently corresponding to the PC demo,
/// two Xbox builds, and three PS2 builds.
/// </summary>
/// <remarks>
/// This is deliberately a transcript reducer, not autonomous UnitAI. It does
/// not traverse retail lists, mutate the lifecycle-aware target reader, run
/// support/escort helpers, populate ballistic-result cells, or replace
/// script-authored <c>Attack(target)</c>. Its indiscriminate arm consumes the
/// caller-supplied released gameplay stream; the caller remains responsible
/// for that shared stream's global draw order.
/// </remarks>
public static class RetailUnitAITargetSelection
{
    public const uint ThingFlagDying = 0x00000004u;

    public const int AllegianceForseti = 0;
    public const int AllegianceMuspell = 1;
    public const int AllegianceNeutral = 2;
    public const int AllegianceIndependent = 6;

    public const uint ThingTypeVehicle = 0x00020000u;
    public const uint ThingTypeInfantry = 0x00004000u;
    public const uint ThingTypeAirUnit = 0x00000400u;
    public const uint ThingTypeEmplacement = 0x00040000u;
    public const uint ThingTypeBuilding = 0x00000100u;
    public const uint ThingTypeNaval = 0x00008000u;
    public const uint ThingTypeComponent = 0x00080000u;

    private const float IndiscriminateScoreScale = 1.0f / 8192.0f;

    /// <summary>
    /// Reduces candidates in their supplied list order. Returns
    /// <c>null</c> when no candidate raises retail's zero-initialized secondary
    /// best. Numeric inputs and all intermediate results must be finite. The
    /// focused contract covers well-separated transcripts; PC x87 versus
    /// binary32 equality/rounding knife edges remain open inside that domain.
    /// </summary>
    public static int? Select(
        RetailUnitAITargetProfile profile,
        int ownerAllegiance138,
        IReadOnlyList<RetailUnitAITargetCandidate> candidates,
        Level100ReleasedRandom? random = null)
    {
        ArgumentNullException.ThrowIfNull(candidates);
        if (profile.Indiscriminate128 != 0)
        {
            ArgumentNullException.ThrowIfNull(random);
        }

        RequireFinite(profile.MaximumDistance158, nameof(profile));
        RequireFinite(profile.EmplacementPriority164, nameof(profile));
        RequireFinite(profile.VehiclePriority168, nameof(profile));
        RequireFinite(profile.BuildingPriority16C, nameof(profile));
        RequireFinite(profile.NavalPriority170, nameof(profile));
        RequireFinite(profile.InfantryPriority174, nameof(profile));
        RequireFinite(profile.AirUnitPriority178, nameof(profile));
        RequireFinite(profile.ComponentPriority17C, nameof(profile));

        float bestPrimary = -999999.0f;
        float bestSecondary = 0.0f;
        int? selectedIndex = null;

        for (int index = 0; index < candidates.Count; index++)
        {
            RetailUnitAITargetCandidate candidate = candidates[index];

            // Retail short-circuits state, allegiance, then capability.
            if (!PassesResolvedCandidateStateGate(
                    candidate.ThingFlags2C,
                    candidate.UnitMode244))
            {
                continue;
            }

            if (!PassesTargetAllegianceGate(
                    ownerAllegiance138,
                    candidate.Allegiance138,
                    profile.Indiscriminate128))
            {
                continue;
            }

            if (candidate.CandidateCapabilityGate == 0)
            {
                continue;
            }

            RequireFinite(candidate.DistanceSquared, nameof(candidates));
            RequireFinite(candidate.RangeReductionPercent, nameof(candidates));
            RequireFinite(candidate.SupportMinimum, nameof(candidates));
            RequireFinite(candidate.SupportMaximum, nameof(candidates));
            if (candidate.DistanceSquared < 0.0f)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(candidates),
                    candidate.DistanceSquared,
                    "A captured squared distance cannot be negative.");
            }

            float rangeFactor = 1.0f - (candidate.RangeReductionPercent * 0.01f);
            float rangeLimit = rangeFactor * profile.MaximumDistance158;
            float rangeLimitSquared = rangeLimit * rangeLimit;
            RequireFinite(rangeFactor, nameof(candidates));
            RequireFinite(rangeLimit, nameof(candidates));
            RequireFinite(rangeLimitSquared, nameof(candidates));
            if (!(candidate.DistanceSquared < rangeLimitSquared))
            {
                continue;
            }

            float primary = PrimaryScore(profile, candidate, random);
            if (primary < bestPrimary)
            {
                continue;
            }

            if (primary > bestPrimary)
            {
                bestPrimary = primary;
                bestSecondary = 0.0f;
                // Retail does not clear its prior winner here. A higher-primary
                // candidate with a non-positive secondary can leave it intact.
            }

            float distance = MathF.Sqrt(candidate.DistanceSquared);
            float secondary = 1000.0f - distance;
            if (candidate.SupportMinimum <= distance)
            {
                secondary += distance <= candidate.SupportMaximum
                    ? 1000000.0f
                    : 10000.0f;
            }

            RequireFinite(distance, nameof(candidates));
            RequireFinite(secondary, nameof(candidates));
            if (secondary > bestSecondary)
            {
                bestSecondary = secondary;
                selectedIndex = index;
            }
        }

        return selectedIndex;
    }

    /// <summary>
    /// Exact field predicate of PC retail <c>0x004FD5B0</c> after the caller
    /// has resolved and null-checked the candidate pointer.
    /// </summary>
    public static bool PassesResolvedCandidateStateGate(
        uint thingFlags2C,
        int unitMode244) =>
        (thingFlags2C & ThingFlagDying) == 0 &&
        unitMode244 is not 1 and not 2;

    /// <summary>
    /// Exact allegiance/indiscriminate truth table of PC retail
    /// <c>0x004FD3D0</c>. The source spelling is
    /// <c>IsTargetAlligence</c> (sic).
    /// </summary>
    public static bool PassesTargetAllegianceGate(
        int ownerAllegiance138,
        int candidateAllegiance138,
        int indiscriminate128)
    {
        if (candidateAllegiance138 == AllegianceNeutral)
        {
            return indiscriminate128 != 0;
        }

        return candidateAllegiance138 switch
        {
            AllegianceForseti =>
                ownerAllegiance138 is AllegianceMuspell or AllegianceIndependent,
            AllegianceMuspell =>
                ownerAllegiance138 is AllegianceForseti or AllegianceIndependent,
            AllegianceIndependent =>
                ownerAllegiance138 is AllegianceForseti or AllegianceMuspell,
            _ => false,
        };
    }

    private static float PrimaryScore(
        RetailUnitAITargetProfile profile,
        RetailUnitAITargetCandidate candidate,
        Level100ReleasedRandom? random)
    {
        if (profile.Indiscriminate128 == 0 &&
            candidate.ScoreGate164 == 0 &&
            profile.ScoreGate138 == 0)
        {
            // This gate bypasses both the ladder and the independent floor.
            return 0.0f;
        }

        uint flags = candidate.TypeFlags34;
        if (profile.Indiscriminate128 != 0)
        {
            // All measured builds jump from this arm directly to the primary
            // comparison, bypassing the deterministic component floor.
            return (random!.Next() %
                    SimulationConstants.Level100ReleasedRandomUnitModulus) *
                IndiscriminateScoreScale;
        }

        float score = (flags & ThingTypeVehicle) != 0 ? profile.VehiclePriority168
            : (flags & ThingTypeInfantry) != 0 ? profile.InfantryPriority174
            : (flags & ThingTypeAirUnit) != 0 ? profile.AirUnitPriority178
            : (flags & ThingTypeEmplacement) != 0 ? profile.EmplacementPriority164
            : (flags & ThingTypeBuilding) != 0 ? profile.BuildingPriority16C
            : (flags & ThingTypeNaval) != 0 ? profile.NavalPriority170
            : 0.0f;

        if ((flags & ThingTypeComponent) != 0 && score < profile.ComponentPriority17C)
        {
            score = profile.ComponentPriority17C;
        }

        return score;
    }

    private static void RequireFinite(float value, string parameterName)
    {
        if (!float.IsFinite(value))
        {
            throw new ArgumentOutOfRangeException(
                parameterName,
                value,
                "The reproduced UnitAI selector currently admits only finite values.");
        }
    }
}
