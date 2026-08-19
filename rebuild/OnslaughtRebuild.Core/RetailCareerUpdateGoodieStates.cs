// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// One <c>CGoodie::mState</c> dword — <c>Career.h:40-55</c>.
/// </summary>
public static class RetailCareerGoodieState
{
    /// <summary><c>GS_UNKNOWN</c> — <c>Career.h:42</c>.</summary>
    public const int Unknown = 0;

    /// <summary><c>GS_INSTRUCTIONS</c> — <c>Career.h:43</c>.</summary>
    public const int Instructions = 1;

    /// <summary><c>GS_NEW</c> — <c>Career.h:44</c>; the store at <c>0x0041c527</c>.</summary>
    public const int New = 2;

    /// <summary><c>GS_OLD</c> — <c>Career.h:45</c>.</summary>
    public const int Old = 3;
}

/// <summary>
/// <c>mGoodies[300]</c> — the dword array at <c>CCareer + 0x1F44</c>.
/// </summary>
public sealed class RetailCareerGoodies
{
    private readonly int[] _states = new int[RetailCareerRecordLayout.GoodieCount];

    /// <summary>The 300 state dwords in index order.</summary>
    public IReadOnlyList<int> States => _states;

    /// <summary><c>GetGoodieState</c> — index into <c>mGoodies</c>.</summary>
    public int Get(int index) => _states[index];

    /// <summary>
    /// Direct store of one <c>mGoodies[i].mState</c> dword. Tests seed
    /// <c>GS_OLD</c> so <c>SET_GOODIE_NEW</c>'s overwrite guard is unique.
    /// </summary>
    public void Set(int index, int state) => _states[index] = state;

    /// <summary>
    /// <c>SET_GOODIE_NEW</c> — <c>Career.cpp:566</c>. Stores
    /// <c>GS_NEW</c> only when <c>mState &lt;= GS_INSTRUCTIONS</c>.
    /// </summary>
    public void SetNewIfNotDone(int index)
    {
        if (_states[index] <= RetailCareerGoodieState.Instructions)
        {
            _states[index] = RetailCareerGoodieState.New;
        }
    }
}

/// <summary>
/// The Level 100 slice of <c>CCareer::UpdateGoodieStates</c>.
/// </summary>
/// <remarks>
/// <para>
/// Owner in the pinned drop: <c>references/Onslaught/Career.cpp:684-902</c>.
/// Retail identity: <c>0x0041c470</c>. Training is not exempt — world 100
/// is not an early-out. Kill accumulation still skips world 100
/// (<c>0x0041c188</c>); this body still runs.
/// </para>
/// <para>
/// <b>A first-play S unlocks five slots.</b> <c>COMPLETE_LEVEL(100)</c>
/// writes <c>GS_NEW</c> on 0 and 8. <c>GRADE(100) &gt;= C/B/A</c> writes
/// 78, 121, and 164. <c>GRADE(110) &gt;= C</c> writes goodie 1, but
/// world 110 stays incomplete / BlankRanking so that arm is the
/// already-pinned incomplete <c>'E'</c> and goodie 1 stays
/// <c>GS_UNKNOWN</c>. <c>CGrade::operator&gt;=</c> treats <c>'S'</c> as
/// above every other grade, so the already-pinned FillOut 1.0f unlocks
/// the five world-100 slots together. <c>SET_GOODIE_NEW</c> stores 2
/// only when <c>mState &lt;= GS_INSTRUCTIONS</c>.
/// </para>
/// <para>
/// <b>Do not invent the rest of the table.</b> Other worlds are not in
/// the cold training slice; <c>COMPLETE_LEVEL</c> / <c>GRADE</c> of a
/// missing world is a NULL deref at <c>0x0041C370</c>. Kill thresholds,
/// <c>TOTAL_S_GRADES</c>, episode instruction marks, and the
/// <c>mPendingExtraGoodies</c> latch stay unclaimed. The first-play
/// CountGoodies delta into <c>new_goodie_count</c> is the already-cited
/// Career.cpp:895-897 arm.
/// </para>
/// </remarks>
public static class RetailCareerUpdateGoodieStates
{
    /// <summary>Goodie 0 — complete world 100 — <c>Career.cpp:690</c>.</summary>
    public const int CompleteWorld100Bio = 0;

    /// <summary>Goodie 1 — <c>GRADE(110) &gt;= C</c> — <c>Career.cpp:691</c>.</summary>
    public const int GradeCOnWorld110 = 1;

    /// <summary>Goodie 8 — complete world 100 — <c>Career.cpp:698</c>.</summary>
    public const int CompleteWorld100Second = 8;

    /// <summary>Goodie 78 — <c>GRADE(100) &gt;= C</c> — <c>Career.cpp:769</c>.</summary>
    public const int GradeCOnWorld100 = 78;

    /// <summary>Goodie 121 — <c>GRADE(100) &gt;= B</c> — <c>Career.cpp:813</c>.</summary>
    public const int GradeBOnWorld100 = 121;

    /// <summary>Goodie 164 — <c>GRADE(100) &gt;= A</c> — <c>Career.cpp:857</c>.</summary>
    public const int GradeAOnWorld100 = 164;

    /// <summary>
    /// The Level 100 arms of <c>CCareer::UpdateGoodieStates</c> —
    /// <c>Career.cpp:690 / 691 / 698 / 769 / 813 / 857</c>,
    /// <c>0x0041c470</c>, then the already-cited <c>CountGoodies</c>
    /// delta into <c>new_goodie_count</c> and the goodie-0
    /// <c>first_goodie</c> latch (<c>Career.cpp:686 / 688 / 895-900</c>).
    /// After <c>GetAndResetGoodieNewCount</c> /
    /// <c>GetAndResetFirstGoodie</c> a replay <c>ApplyUpdate</c> leaves
    /// both at 0: the count add is delta 0 and the latch is
    /// transition-only. Lost still runs this body
    /// (<c>Career.cpp:382-385</c>) but world 100 stays incomplete, so
    /// both globals stay ctor 0. <c>GRADE(110) &gt;= C</c> stays closed
    /// after first-play: world 110 is incomplete so the lookup is
    /// <c>'E'</c> and goodie 1 stays <c>GS_UNKNOWN</c>.
    /// <c>mPendingExtraGoodies</c> and episode instruction marks stay
    /// unclaimed.
    /// </summary>
    public static void Update(RetailCareerCampaign career)
    {
        ArgumentNullException.ThrowIfNull(career);

        int previouslyNew = CountGoodies(career);
        bool goodieZeroWasNotDone =
            career.Goodies.Get(CompleteWorld100Bio) <= RetailCareerGoodieState.Instructions;

        if (career.Nodes.CompleteFlagOf(RetailCareerReCalcLinks.TrainingWorldNumber) == 1)
        {
            career.Goodies.SetNewIfNotDone(CompleteWorld100Bio);
            career.Goodies.SetNewIfNotDone(CompleteWorld100Second);
        }

        List<RetailWorldGradeNode> gradeNodes = GradeNodes(career);
        byte grade = RetailWorldGrade.GradeByteForWorld(
            gradeNodes,
            RetailCareerReCalcLinks.TrainingWorldNumber);
        var held = new RetailGrade(unchecked((sbyte)grade));
        if (held.IsAtLeast(new RetailGrade((sbyte)'C')))
        {
            career.Goodies.SetNewIfNotDone(GradeCOnWorld100);
        }

        if (held.IsAtLeast(new RetailGrade((sbyte)'B')))
        {
            career.Goodies.SetNewIfNotDone(GradeBOnWorld100);
        }

        if (held.IsAtLeast(new RetailGrade((sbyte)'A')))
        {
            career.Goodies.SetNewIfNotDone(GradeAOnWorld100);
        }

        byte grade110 = RetailWorldGrade.GradeByteForWorld(
            gradeNodes,
            RetailCareerReCalcLinks.TrainingLowerChildWorldNumber);
        var held110 = new RetailGrade(unchecked((sbyte)grade110));
        if (held110.IsAtLeast(new RetailGrade((sbyte)'C')))
        {
            career.Goodies.SetNewIfNotDone(GradeCOnWorld110);
        }

        career.Counters.NewGoodieCount += CountGoodies(career) - previouslyNew;
        if (goodieZeroWasNotDone &&
            career.Goodies.Get(CompleteWorld100Bio) > RetailCareerGoodieState.Instructions)
        {
            career.Counters.FirstGoodie = 1;
        }
    }

    /// <summary>
    /// <c>CCareer::CountGoodies</c> — <c>Career.cpp:670-680</c>. Counts
    /// slots whose <c>mState &gt;= GS_NEW</c>.
    /// </summary>
    public static int CountGoodies(RetailCareerCampaign career)
    {
        ArgumentNullException.ThrowIfNull(career);

        int total = 0;
        for (int index = 0; index < career.Goodies.States.Count; index++)
        {
            if (career.Goodies.Get(index) >= RetailCareerGoodieState.New)
            {
                total++;
            }
        }

        return total;
    }

    private static List<RetailWorldGradeNode> GradeNodes(RetailCareerCampaign career)
    {
        var nodes = new List<RetailWorldGradeNode>(career.Nodes.NodeCount);
        for (int index = 0; index < career.Nodes.NodeCount; index++)
        {
            RetailCareerNode node = career.Nodes.Nodes[index];
            nodes.Add(new RetailWorldGradeNode(node.WorldNumber, node.Complete, node.Ranking));
        }

        return nodes;
    }
}
