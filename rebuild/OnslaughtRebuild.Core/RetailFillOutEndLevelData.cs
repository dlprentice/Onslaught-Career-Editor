// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// The fields <c>CGame::FillOutEndLevelData</c> writes on a Level 100
/// win. Career <c>Update</c> / <c>ReCalcLinks</c> consume the world,
/// state, ranking, secondaries, kills, and slots; the primary table is
/// copied too and is not a career input.
/// </summary>
public readonly record struct RetailEndLevelSnapshot(
    int WorldFinished,
    int FinalState,
    float Ranking,
    IReadOnlyList<int> SecondaryStatuses,
    IReadOnlyList<int> ThingsKilled,
    IReadOnlyList<int> SlotWords,
    IReadOnlyList<int> PrimaryStatuses,
    IReadOnlyList<int> BaseThingsLeft);

/// <summary>
/// <c>CGame::FillOutEndLevelData</c> as it applies to a Level 100 Won —
/// the snapshot career consumes, plus the already-measured score-time
/// rewrite. First-play elapsed and score stay unclaimed, so
/// <see cref="ForLevel100Won"/> still carries the pre-arm 1.0f store.
/// </summary>
/// <remarks>
/// <para>
/// Owner in the pinned drop: <c>references/Onslaught/game.cpp:910-1043</c>.
/// Retail identity: <c>0x0046D470</c>. Callers include
/// <c>CGame::RestartLoopRunLevel</c>. The secondary predicate at
/// <c>0x004496E0</c> is already pinned; this type only records when
/// FillOut consults it.
/// </para>
/// <para>
/// <b>Level 100 copies four primaries and no secondaries.</b>
/// <c>mWorldFinished = mCurrentLevel</c> is 100.
/// <c>mFinalState = mGameState</c> is <c>GAME_STATE_LEVEL_WON</c> (5).
/// The ten primary <c>GetStatus()</c> words are four
/// <c>MOS_COMPLETE</c> (1) then six unset — already pinned on
/// <see cref="RetailGameObjectiveCount.Level100WonPrimaryStatuses"/>.
/// That is not the rebuild mission enum's
/// <c>Level100PrimaryObjectiveStatus.Complete = 2</c>.
/// <c>mSecondaryObjectives</c> is the ten-entry array with every
/// <c>GetStatus()</c> unset. Do not invent secondary content.
/// </para>
/// <para>
/// <b>A first-play win SetSlotSave's four tutorial bits.</b>
/// <c>SLOT_TUTORIAL_1..4</c> are 63..66. FillOut copies
/// <c>END_LEVEL_DATA.mSlots = GAME.mSlots</c> (<c>game.cpp:971</c>),
/// so those four bits are the only addressable ones on this
/// snapshot. Do not invent other slots. The 32-dword career
/// assignment stays on <see cref="RetailCareerSlotHandoff"/>.
/// </para>
/// <para>
/// <b>The ranking clamp is gated on a non-zero secondary count.</b>
/// <c>game.cpp:1028</c> is <c>if (GetNumSecondaryObjectives())</c>.
/// When that count is 0 the 0.4 floor and 0.6 cap never run, even
/// though <c>IsAllSecondaryObjectivesComplete</c> would return FALSE.
/// The 0.4 / 0.6 immediates are therefore not claimed here.
/// </para>
/// <para>
/// <b>The score-time arm is live on Level 100.</b> Last
/// <c>CWorld::LoadWorld</c> is the outer RLWD parse. <c>this+0x108</c>
/// / <c>+0x10c</c> / <c>+0x110</c> are RLWD <c>+0x147ba</c> /
/// <c>+0x147be</c> / next dword = 300.0 / 500.0 / 1.0, so
/// <c>0x0046d638</c> <c>fld [this+0x10c]</c> / <c>fsub [this+0x108]</c>
/// / <c>fcomp 0.0</c> / <c>test ah,0x41</c> / <c>jne 0x0046d79b</c>
/// does not skip. Last-wins S/D ints at <c>this+0xf8/+0xfc</c> are
/// 210 / 70. A zero score stores ranking 0 at <c>0x0046d772</c> and
/// skips the <c>0x3a83126f</c> (0.001f) replacement that source
/// <c>game.cpp:1021-1024</c> would apply after clamping −1. First-play
/// elapsed and <c>this+0xf4</c> stay unclaimed — do not rewrite the
/// snapshot ranking from an invented score.
/// </para>
/// <para>
/// <b>Not established here.</b> A player who wrecks an iceberg
/// and still Wins would store 0 on those type-35 indices.
/// First-play elapsed and score. ConfirmedKill increments when
/// the player actually scores those bits. Career
/// <c>UpdateBaseWorldExistsStuffForNode</c> onto world 110 is
/// the already-pinned <see cref="RetailCareerCampaign"/> slice.
/// </para>
/// </remarks>
public static class RetailFillOutEndLevelData
{
    /// <summary>
    /// Last-wins RLWD <c>+0x147ba</c> into <c>CGame+0x108</c>.
    /// </summary>
    public const float Level100FullScoreTime = 300.0f;

    /// <summary>
    /// Last-wins RLWD <c>+0x147be</c> into <c>CGame+0x10c</c>.
    /// </summary>
    public const float Level100PercentageScoreTime = 500.0f;

    /// <summary>
    /// Last-wins RLWD dword after the percentage time, into
    /// <c>CGame+0x110</c>. With this 1.0 the time multiplier is
    /// identically 1.0, so elapsed does not change the scaled score.
    /// </summary>
    public const float Level100ScorePercentage = 1.0f;

    /// <summary>
    /// Last-wins RLWD int at the <c>this+0xf8</c> S-grade slot.
    /// </summary>
    public const int Level100SGradeScore = 210;

    /// <summary>
    /// Last-wins RLWD int at the <c>this+0xfc</c> D-grade slot.
    /// </summary>
    public const int Level100DGradeScore = 70;

    /// <summary>
    /// <c>[0x0085515c]</c> after a first-play Level 100 Won — BSWD
    /// At() membership (27 type-8 + 6 type-35 + 2 type-37
    /// <c>CSafeSide</c>). Not the materializer's 33 visible units.
    /// </summary>
    public const int Level100BaseWorldThingCount = 35;

    /// <summary>Shipped Level 100 primary count — <c>LevelScript.msl</c>.</summary>
    public const int Level100PrimaryCount = 4;

    /// <summary>Shipped Level 100 secondary count — there are none.</summary>
    public const int Level100SecondaryCount = 0;

    /// <summary>The ten unset <c>GetStatus()</c> words FillOut copies for Level 100.</summary>
    public static int[] UnsetSecondaryStatuses() =>
        new int[RetailEndLevelObjectives.SecondaryObjectiveCount];

    /// <summary>
    /// <c>GAME.mSlots</c> after a first-play Level 100 win
    /// <c>SetSlotSave</c>'d <c>SLOT_TUTORIAL_1..4</c>. FillOut copies
    /// these 32 words into <c>END_LEVEL_DATA.mSlots</c>.
    /// </summary>
    public static int[] FirstPlayTutorialSlotWords()
    {
        var slots = new RetailCareerSlots();
        slots.SetSlot(RetailCareerSlotHandoff.TutorialIntroductionSlot, 1);
        slots.SetSlot(RetailCareerSlotHandoff.TutorialPulseCannonSlot, 1);
        slots.SetSlot(RetailCareerSlotHandoff.TutorialVulcanCannonSlot, 1);
        slots.SetSlot(RetailCareerSlotHandoff.TutorialStatusBarsSlot, 1);
        var words = new int[RetailCareerSlots.SlotWords];
        for (int index = 0; index < words.Length; index++)
        {
            words[index] = slots.Words[index];
        }

        return words;
    }

    /// <summary>
    /// FillOut <c>mBaseThingsLeft</c> after a first-play Level 100 Won
    /// that does not wreck a list member. Size is 35; slots 0..34 are
    /// 1; 35..287 stay 0. Iceberg player-kill store-0 stays open.
    /// </summary>
    public static int[] FirstPlayBaseThingsLeft()
    {
        var left = new int[RetailCareerNode.BaseThingsExistsSize];
        for (int index = 0; index < Level100BaseWorldThingCount; index++)
        {
            left[index] = 1;
        }

        return left;
    }

    /// <summary>
    /// FillOut copies five dwords from <c>player+8</c>. Those start at
    /// ctor-zero and only <c>0x004d30d0</c> increments them. A first-play
    /// Won that never takes ConfirmedKill is therefore five zeros.
    /// Career still skips world 100.
    /// </summary>
    public static int[] FirstPlayThingsKilled() =>
        new int[RetailCareerCounters.KilledTypeCount];

    /// <summary>
    /// The post-Won snapshot Level 100 hands to career. Ranking defaults to
    /// the <c>mRanking=1.0f</c> store at <c>game.cpp:967</c> before the
    /// score-time arm; callers may override. First-play elapsed and score
    /// stay unclaimed, so this does not run
    /// <see cref="AfterScoreTimeArm"/>.
    /// </summary>
    public static RetailEndLevelSnapshot ForLevel100Won(
        float ranking = 1.0f,
        IReadOnlyList<int>? thingsKilled = null)
    {
        return new RetailEndLevelSnapshot(
            RetailCareerReCalcLinks.TrainingWorldNumber,
            RetailCareerReCalcLinks.GameStateLevelWon,
            ranking,
            UnsetSecondaryStatuses(),
            thingsKilled ?? FirstPlayThingsKilled(),
            FirstPlayTutorialSlotWords(),
            RetailGameObjectiveCount.Level100WonPrimaryStatuses(),
            FirstPlayBaseThingsLeft());
    }

    /// <summary>
    /// The <c>game.cpp:1028-1042</c> ranking clamp. A zero secondary count
    /// is a skip. Non-zero counts are a different, unmeasured arm.
    /// </summary>
    public static float AfterSecondaryRankingClamp(
        float ranking,
        int secondaryCount,
        IReadOnlyList<int> secondaryObjectiveStatuses)
    {
        if (secondaryObjectiveStatuses is null)
        {
            throw new ArgumentNullException(nameof(secondaryObjectiveStatuses));
        }

        if (secondaryCount == 0)
        {
            return ranking;
        }

        throw new InvalidOperationException(
            "FillOutEndLevelData only consults IsAllSecondaryObjectivesComplete " +
            "when GetNumSecondaryObjectives() is non-zero. The 0.4 / 0.6 " +
            "immediates are not measured for this owner; Level 100 never " +
            "reaches that arm.");
    }

    /// <summary>
    /// <c>0x0046d638</c> <c>fcomp 0.0</c> / <c>test ah,0x41</c> /
    /// <c>jne 0x0046d79b</c> — skip when (percentage − full) ≤ 0.
    /// </summary>
    public static bool ScoreTimeArmSkips(float fullScoreTime, float percentageScoreTime)
    {
        return !(percentageScoreTime - fullScoreTime > 0.0f);
    }

    /// <summary>
    /// Live score-time rewrite at <c>0x0046d659</c>–<c>0x0046d79b</c>.
    /// A skip returns <paramref name="preArmRanking"/>. Below D stores
    /// 0 and does not apply the 0.001 replacement.
    /// </summary>
    public static float AfterScoreTimeArm(
        float preArmRanking,
        float elapsedTime,
        float fullScoreTime,
        float percentageScoreTime,
        float scorePercentage,
        int score,
        int sGradeScore,
        int dGradeScore)
    {
        if (ScoreTimeArmSkips(fullScoreTime, percentageScoreTime))
        {
            return preArmRanking;
        }

        float multiplier;
        if (elapsedTime < fullScoreTime)
        {
            multiplier = 1.0f;
        }
        else if (elapsedTime < percentageScoreTime)
        {
            float delta = percentageScoreTime - fullScoreTime;
            multiplier = scorePercentage
                - ((elapsedTime - percentageScoreTime) / delta)
                * (1.0f - scorePercentage);
        }
        else
        {
            multiplier = scorePercentage;
        }

        if (!(multiplier <= 1.0f))
        {
            multiplier = 1.0f;
        }
        else if (multiplier < 0.0f)
        {
            multiplier = 0.0f;
        }

        int scaled = LowDwordOfFistp(score * (double)multiplier);
        if (scaled >= sGradeScore)
        {
            return 1.0f;
        }

        if (scaled < dGradeScore)
        {
            return 0.0f;
        }

        float ranking = (scaled - (float)dGradeScore)
            / (sGradeScore - (float)dGradeScore);
        if (!(ranking <= 1.0f))
        {
            return 1.0f;
        }

        if (ranking < 0.0f)
        {
            return 0.0f;
        }

        if (ranking == 0.0f)
        {
            return PointZeroZeroOne;
        }

        return ranking;
    }

    private const float PointZeroZeroOne = 0.001f;

    /// <summary>
    /// <c>0x0046d6ed</c> <c>fistp qword ptr [esp+0x18]</c> under ambient
    /// <c>/QIfist</c> — round-to-nearest-even, then the low dword.
    /// </summary>
    private static int LowDwordOfFistp(double value)
    {
        double rounded = Math.Round(value, MidpointRounding.ToEven);
        if (double.IsNaN(rounded) ||
            rounded < -9223372036854775808.0 ||
            rounded >= 9223372036854775808.0)
        {
            return unchecked((int)long.MinValue);
        }

        return unchecked((int)(long)rounded);
    }
}
