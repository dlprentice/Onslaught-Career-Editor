// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// The post-Won seam from <see cref="Level100Mission"/> onto the already-pinned
/// FillOut snapshot and <c>CCareer::Update</c>.
/// </summary>
/// <remarks>
/// <para>
/// After <c>CGame::DeclareLevelWon</c> the 5.0 f countdown elapses,
/// <c>CGame::RestartLoopRunLevel</c> calls
/// <c>CGame::FillOutEndLevelData</c> (<c>0x0046D470</c>) and then
/// <c>CCareer::Update</c> (<c>0x0041BD00</c>). Mission
/// <see cref="Level100MissionTerminalState.FrontEndHandoffReady"/> is that
/// seam for Level 100. This type does not reimplement FillOut, ReCalcLinks,
/// or the ranking-clamp skip — it only applies
/// <see cref="RetailFillOutEndLevelData.ForLevel100Won"/> to a cold
/// training slice.
/// </para>
/// <para>
/// <b>Do not invent secondaries.</b> Level 100 ships four primaries and
/// none. The snapshot's ten status words stay unset.
/// </para>
/// <para>
/// <b>Lost does not take this path.</b>
/// <c>END_LEVEL_DATA.mFinalState != GAME_STATE_LEVEL_WON</c> returns
/// from <c>Update</c> before the graph moves
/// (<c>Career.cpp:382-385</c>).
/// </para>
/// <para>
/// <b>SuccessCountdown does not take this path either.</b>
/// <c>RestartLoopRunLevel</c> calls FillOut only after the main
/// loop quits (<c>game.cpp:1552</c>), and that quit waits for the
/// already-pinned 5.0 f Won store (<c>game.cpp:1997-2004</c>).
/// <c>CFrontEnd::Init</c> then calls <c>CAREER.Update</c>
/// (<c>FrontEnd.cpp:67</c>).
/// </para>
/// </remarks>
public sealed class Level100WonCareerHandoff
{
    private bool _applied;

    /// <summary>
    /// A fresh world-100 / world-110 training slice. Stays cold until
    /// <see cref="TryApply"/> sees Won plus FrontEndHandoffReady.
    /// </summary>
    public RetailCareerCampaign Career { get; } =
        RetailCareerReCalcLinks.CreateColdTrainingSlice();

    /// <summary>
    /// Apply the FillOut Won snapshot once, and only when the mission has
    /// reached the frontend handoff after a win.
    /// </summary>
    public bool TryApply(
        Level100MissionOutcome outcome,
        Level100MissionTerminalState terminalState)
    {
        if (_applied ||
            outcome != Level100MissionOutcome.Won ||
            terminalState != Level100MissionTerminalState.FrontEndHandoffReady)
        {
            return false;
        }

        Career.ApplyUpdate(RetailFillOutEndLevelData.ForLevel100Won());
        _applied = true;
        return true;
    }
}
