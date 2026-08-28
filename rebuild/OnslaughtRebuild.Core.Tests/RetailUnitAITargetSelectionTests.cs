// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Cross-build branch-law checks for PC retail <c>0x004FF710</c>, PC demo
/// <c>0x004FF7C0</c>, Xbox <c>0x001878A0/0x00187910</c>, and PS2
/// <c>0x002BF818/0x002BF8D8/0x002C0040</c>.
/// </summary>
public sealed class RetailUnitAITargetSelectionTests
{
    [Fact]
    public void DeterministicTranscriptPreservesRetailRangeLadderFloorAndTieLaw()
    {
        var profile = new RetailUnitAITargetProfile(
            Indiscriminate128: 0,
            ScoreGate138: 0,
            MaximumDistance158: 2000.0f,
            EmplacementPriority164: 40.0f,
            VehiclePriority168: 10.0f,
            BuildingPriority16C: 50.0f,
            NavalPriority170: 60.0f,
            InfantryPriority174: 20.0f,
            AirUnitPriority178: 30.0f,
            ComponentPriority17C: 20.0f);

        RetailUnitAITargetCandidate[] candidates =
        [
            Candidate(
                RetailUnitAITargetSelection.ThingTypeVehicle |
                RetailUnitAITargetSelection.ThingTypeInfantry,
                distance: 1.0f,
                supportMinimum: 0.0f,
                supportMaximum: 2.0f),
            // Primary rises from 10 to 20, but secondary is exactly zero.
            // Retail keeps A's pointer rather than clearing it here.
            Candidate(
                RetailUnitAITargetSelection.ThingTypeInfantry,
                distance: 1000.0f,
                supportMinimum: 1500.0f,
                supportMaximum: 1600.0f),
            // The post-ladder floor raises 10 to 20; above-band adds 10,000.
            Candidate(
                RetailUnitAITargetSelection.ThingTypeVehicle |
                RetailUnitAITargetSelection.ThingTypeComponent,
                distance: 1500.0f,
                supportMinimum: 1000.0f,
                supportMaximum: 1200.0f),
            Candidate(
                RetailUnitAITargetSelection.ThingTypeInfantry,
                distance: 1999.0f,
                supportMinimum: 1990.0f,
                supportMaximum: 2000.0f),
            // Exact primary/secondary equality retains the earlier D.
            Candidate(
                RetailUnitAITargetSelection.ThingTypeInfantry,
                distance: 1999.0f,
                supportMinimum: 1990.0f,
                supportMaximum: 2000.0f),
            // Strict squared-range equality rejects this otherwise stronger row.
            Candidate(
                RetailUnitAITargetSelection.ThingTypeAirUnit,
                distance: 2000.0f,
                supportMinimum: 0.0f,
                supportMaximum: 3000.0f),
            // Eligibility short-circuits this otherwise stronger row.
            Candidate(
                RetailUnitAITargetSelection.ThingTypeAirUnit,
                distance: 1.0f,
                supportMinimum: 0.0f,
                supportMaximum: 2.0f,
                allegiance138: RetailUnitAITargetSelection.AllegianceForseti),
            // Both raw score gates are zero: primary stays zero and the floor
            // is skipped even though its bit is set.
            Candidate(
                RetailUnitAITargetSelection.ThingTypeAirUnit |
                RetailUnitAITargetSelection.ThingTypeComponent,
                distance: 1.0f,
                supportMinimum: 0.0f,
                supportMaximum: 2.0f,
                scoreGate164: 0),
        ];

        Assert.Null(Select(profile, candidates[1..2], 1));
        Assert.Equal(0, Select(profile, candidates, 1));
        Assert.Equal(0, Select(profile, candidates, 2));
        Assert.Equal(2, Select(profile, candidates, 3));
        Assert.Equal(3, Select(profile, candidates, 4));
        Assert.Equal(3, Select(profile, candidates, 5));
        Assert.Equal(3, Select(profile, candidates, candidates.Length));
    }

    [Fact]
    public void IndiscriminateArmConsumesOnlyAdmittedCandidatesAndBypassesComponentFloor()
    {
        RetailUnitAITargetProfile profile = DefaultProfile() with
        {
            Indiscriminate128 = 1,
            ComponentPriority17C = 7.0f,
        };
        RetailUnitAITargetCandidate[] candidates =
        [
            Candidate(
                0,
                distance: 1.0f,
                supportMinimum: 0.0f,
                supportMaximum: 2.0f,
                thingFlags2C: RetailUnitAITargetSelection.ThingFlagDying),
            Candidate(
                0,
                distance: 1.0f,
                supportMinimum: 0.0f,
                supportMaximum: 2.0f),
            Candidate(
                0,
                distance: 2.0f,
                supportMinimum: 0.0f,
                supportMaximum: 3.0f),
            Candidate(
                0,
                distance: 2000.0f,
                supportMinimum: 0.0f,
                supportMaximum: 3000.0f),
            Candidate(
                RetailUnitAITargetSelection.ThingTypeComponent,
                distance: 3.0f,
                supportMinimum: 0.0f,
                supportMaximum: 4.0f,
                scoreGate164: 0),
        ];
        var random = new Level100ReleasedRandom();

        Assert.Equal(
            2,
            RetailUnitAITargetSelection.Select(
                profile,
                RetailUnitAITargetSelection.AllegianceForseti,
                candidates,
                random));
        Assert.Equal(-1_136_790_067, random.Seed);
    }

    [Theory]
    [InlineData(0u, 0, true)]
    [InlineData(0u, 3, true)]
    [InlineData(RetailUnitAITargetSelection.ThingFlagDying, 0, false)]
    [InlineData(RetailUnitAITargetSelection.ThingFlagDying, 3, false)]
    [InlineData(0u, 1, false)]
    [InlineData(0u, 2, false)]
    public void ResolvedCandidateStateGateMatchesReleasedPredicate(
        uint thingFlags2C,
        int unitMode244,
        bool expected) => Assert.Equal(
            expected,
            RetailUnitAITargetSelection.PassesResolvedCandidateStateGate(
                thingFlags2C,
                unitMode244));

    [Theory]
    [InlineData(0, 1, 0, true)]
    [InlineData(0, 6, 0, true)]
    [InlineData(1, 0, 0, true)]
    [InlineData(1, 6, 0, true)]
    [InlineData(6, 0, 0, true)]
    [InlineData(6, 1, 0, true)]
    [InlineData(0, 0, 0, false)]
    [InlineData(1, 1, 1, false)]
    [InlineData(6, 6, 1, false)]
    [InlineData(0, 2, 0, false)]
    [InlineData(99, 2, 1, true)]
    [InlineData(0, 3, 1, false)]
    public void TargetAllegianceGateMatchesReleasedTruthTable(
        int ownerAllegiance138,
        int candidateAllegiance138,
        int indiscriminate128,
        bool expected) => Assert.Equal(
            expected,
            RetailUnitAITargetSelection.PassesTargetAllegianceGate(
                ownerAllegiance138,
                candidateAllegiance138,
                indiscriminate128));

    private static int? Select(
        RetailUnitAITargetProfile profile,
        RetailUnitAITargetCandidate[] candidates,
        int count) => RetailUnitAITargetSelection.Select(
            profile,
            RetailUnitAITargetSelection.AllegianceForseti,
            candidates[..count]);

    private static RetailUnitAITargetProfile DefaultProfile() => new(
        Indiscriminate128: 0,
        ScoreGate138: 0,
        MaximumDistance158: 2000.0f,
        EmplacementPriority164: 40.0f,
        VehiclePriority168: 10.0f,
        BuildingPriority16C: 50.0f,
        NavalPriority170: 60.0f,
        InfantryPriority174: 20.0f,
        AirUnitPriority178: 30.0f,
        ComponentPriority17C: 20.0f);

    private static RetailUnitAITargetCandidate Candidate(
        uint flags,
        float distance,
        float supportMinimum,
        float supportMaximum,
        uint thingFlags2C = 0,
        int unitMode244 = 0,
        int allegiance138 = RetailUnitAITargetSelection.AllegianceMuspell,
        int candidateCapabilityGate = 1,
        int scoreGate164 = 1) => new(
            ThingFlags2C: thingFlags2C,
            TypeFlags34: flags,
            UnitMode244: unitMode244,
            Allegiance138: allegiance138,
            DistanceSquared: distance * distance,
            RangeReductionPercent: 0.0f,
            CandidateCapabilityGate: candidateCapabilityGate,
            ScoreGate164: scoreGate164,
            SupportMinimum: supportMinimum,
            SupportMaximum: supportMaximum);
}
