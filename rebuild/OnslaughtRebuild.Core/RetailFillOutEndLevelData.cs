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
    IReadOnlyList<int> PrimaryStatuses);

/// <summary>
/// <c>CGame::FillOutEndLevelData</c> as it applies to a Level 100 Won —
/// the snapshot career consumes, not the score-time ranking arithmetic.
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
/// <b>Not established here.</b> The score-time multiplier at
/// <c>game.cpp:988-1026</c> (<c>mFullScoreTime</c> /
/// <c>mPercentageScoreTime</c>). Whether Level 100's authored times
/// make that arm live. Base-things copy. The mission-path wire from
/// <c>FrontEndHandoffReady</c>. Kill readout from <c>CPlayer</c>.
/// </para>
/// </remarks>
public static class RetailFillOutEndLevelData
{
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
    /// The post-Won snapshot Level 100 hands to career. Ranking defaults to
    /// the <c>mRanking=1.0f</c> store at <c>game.cpp:967</c> before the
    /// unclaimed score-time arm; callers may override.
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
            thingsKilled ?? new int[RetailCareerCounters.KilledTypeCount],
            FirstPlayTutorialSlotWords(),
            RetailGameObjectiveCount.Level100WonPrimaryStatuses());
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
}
