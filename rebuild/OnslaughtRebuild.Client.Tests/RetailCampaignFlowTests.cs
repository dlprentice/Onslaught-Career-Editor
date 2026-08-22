// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Campaign-flow parity for the released selector law across the first two
/// career nodes: New Game → SELECT LEVEL offers only the root on a cold
/// career; a Level 100 Won update applied to the same career unlocks world
/// 110; and the launch edge carries the selected world number
/// (<see cref="RetailFrontendSession.SelectedWorldNumber"/>) so the client
/// constructs the world the player chose, not always world 100.
///
/// <para>Selectability is the measured ReCalcLinks unlock
/// (<c>references/Onslaught/Career.cpp:379-515</c>): the child node's own
/// <c>mComplete</c> stays 0 while its incoming link leaves CN_NOT_COMPLETE.
/// The FillOut snapshot is the already-pinned
/// <see cref="RetailFillOutEndLevelData.ForLevel100Won"/>.</para>
/// </summary>
public sealed class RetailCampaignFlowTests
{
    [Fact]
    public void ColdCareer_SelectorOffersOnlyWorld100_AndLaunchCarriesIt()
    {
        var frontend = AtLevelSelect();

        Assert.False(frontend.SelectWorld(110));
        Assert.False(frontend.SelectWorld(200));
        Assert.Equal(100, frontend.ConsumeLaunchWorldNumber);

        DriveToLoading(frontend);
        Assert.Equal(RetailFrontendScreen.Loading, frontend.Screen);
        Assert.True(frontend.ConsumeLevel100LaunchRequest());
        Assert.Equal(100, frontend.ConsumeLaunchWorldNumber);
    }

    [Fact]
    public void WonRoot_UnlocksWorld110_AndLaunchCarriesIt()
    {
        var frontend = AtLevelSelect();

        // The released post-Won career state: FillOut + ReCalcLinks ran when
        // the mission reached FrontEndHandoffReady after Won.
        frontend.Career.ApplyUpdate(RetailFillOutEndLevelData.ForLevel100Won());

        Assert.True(frontend.SelectWorld(110));
        Assert.Equal(110, frontend.ConsumeLaunchWorldNumber);

        DriveToLoading(frontend);
        Assert.Equal(RetailFrontendSignal.LevelLaunchRequested, _lastConfirmSignal);
        Assert.True(frontend.ConsumeLevel100LaunchRequest());
        Assert.Equal(110, frontend.ConsumeLaunchWorldNumber);

        // The distant graph stays locked even after one Won.
        Assert.False(frontend.SelectWorld(200));
        Assert.False(frontend.SelectWorld(500));
        Assert.Equal(110, frontend.ConsumeLaunchWorldNumber);
    }

    [Fact]
    public void SelectWorld_IsRejectedOutsideLevelSelect()
    {
        var frontend = new RetailFrontendSession();

        Assert.False(frontend.SelectWorld(100));

        frontend.Confirm(); // ClickToStart -> MainMenu
        Assert.False(frontend.SelectWorld(100));
    }

    private static RetailFrontendSignal _lastConfirmSignal;

    /// <summary>ClickToStart → MainMenu → DevSelect → LevelSelect.</summary>
    private static RetailFrontendSession AtLevelSelect()
    {
        var frontend = new RetailFrontendSession();
        frontend.Confirm();
        frontend.Confirm();
        frontend.Confirm();
        Assert.Equal(RetailFrontendScreen.LevelSelect, frontend.Screen);
        return frontend;
    }

    /// <summary>
    /// LevelSelect → MissionBriefing → SelectConfiguration → Loading,
    /// recording each Confirm signal for assertions.
    /// </summary>
    private static void DriveToLoading(RetailFrontendSession frontend)
    {
        _lastConfirmSignal = frontend.Confirm();
        Assert.Equal(RetailFrontendScreen.MissionBriefing, frontend.Screen);
        _lastConfirmSignal = frontend.Confirm();
        Assert.Equal(RetailFrontendScreen.SelectConfiguration, frontend.Screen);
        _lastConfirmSignal = frontend.Confirm();
        Assert.Equal(RetailFrontendScreen.Loading, frontend.Screen);
    }
}
