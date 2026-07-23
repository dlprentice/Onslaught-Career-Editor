// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.Client.Tests;

public sealed class RetailFrontendSessionTests
{
    [Fact]
    public void ReleasedEntryPathRequiresClickMainMenuAndLevelSelection()
    {
        var frontend = new RetailFrontendSession();

        Assert.Equal(RetailFrontendScreen.ClickToStart, frontend.Screen);
        Assert.Equal(RetailFrontendSignal.PageChanged, frontend.Confirm());
        Assert.Equal(RetailFrontendScreen.MainMenu, frontend.Screen);
        Assert.Equal(RetailFrontendMenuItemKind.NewGame, frontend.SelectedMainItem.Kind);

        Assert.Equal(RetailFrontendSignal.PageChanged, frontend.Confirm());
        Assert.Equal(RetailFrontendScreen.LevelSelect, frontend.Screen);
        Assert.False(frontend.ConsumeLevel100LaunchRequest());

        Assert.Equal(RetailFrontendSignal.Level100LaunchRequested, frontend.Confirm());
        Assert.Equal(RetailFrontendScreen.Loading, frontend.Screen);
        Assert.True(frontend.ConsumeLevel100LaunchRequest());
        Assert.False(frontend.ConsumeLevel100LaunchRequest());

        frontend.CompleteLevel100Load();
        Assert.Equal(RetailFrontendScreen.Gameplay, frontend.Screen);
    }

    [Fact]
    public void MainNavigationIsBoundedAndBackReturnsFromLevelSelect()
    {
        var frontend = AtMainMenu();

        Assert.False(frontend.MovePrevious());
        for (int index = 1; index < frontend.Items.Count; index++)
        {
            Assert.True(frontend.MoveNext());
        }

        Assert.Equal(RetailFrontendMenuItemKind.Quit, frontend.SelectedMainItem.Kind);
        Assert.False(frontend.MoveNext());

        while (frontend.MovePrevious())
        {
        }

        Assert.Equal(RetailFrontendMenuItemKind.NewGame, frontend.SelectedMainItem.Kind);
        frontend.Confirm();
        Assert.Equal(RetailFrontendSignal.PageChanged, frontend.Back());
        Assert.Equal(RetailFrontendScreen.MainMenu, frontend.Screen);
    }

    [Fact]
    public void UnavailableItemsStayOnMainMenuAndIdentifyTheSelection()
    {
        var frontend = AtMainMenu();
        Assert.True(frontend.MoveNext());

        Assert.Equal(RetailFrontendSignal.Unavailable, frontend.Confirm());
        Assert.Equal(RetailFrontendScreen.MainMenu, frontend.Screen);
        Assert.Equal(
            RetailFrontendMenuItemKind.ContinueGame,
            frontend.UnavailableSelection);
        Assert.False(frontend.ConsumeLevel100LaunchRequest());

        Assert.True(frontend.MoveNext());
        Assert.Null(frontend.UnavailableSelection);
    }

    [Fact]
    public void PointerSelectionUsesTheSameBoundedMainMenuState()
    {
        var frontend = AtMainMenu();

        Assert.True(frontend.SelectMainIndex(5));
        Assert.Equal(RetailFrontendMenuItemKind.Options, frontend.SelectedMainItem.Kind);
        Assert.False(frontend.SelectMainIndex(5));
        Assert.False(frontend.SelectMainIndex(-1));
        Assert.False(frontend.SelectMainIndex(frontend.Items.Count));
    }

    [Fact]
    public void QuitIsTheOnlyOtherAvailableMainAction()
    {
        var frontend = AtMainMenu();
        while (frontend.MoveNext())
        {
        }

        Assert.Equal(RetailFrontendMenuItemKind.Quit, frontend.SelectedMainItem.Kind);
        Assert.True(frontend.SelectedMainItem.IsAvailable);
        Assert.Equal(RetailFrontendSignal.ExitRequested, frontend.Confirm());
        Assert.Equal(RetailFrontendScreen.MainMenu, frontend.Screen);

        Assert.Equal(
            [
                RetailFrontendMenuItemKind.ContinueGame,
                RetailFrontendMenuItemKind.LoadGame,
                RetailFrontendMenuItemKind.Multiplayer,
                RetailFrontendMenuItemKind.Goodies,
                RetailFrontendMenuItemKind.Options,
            ],
            frontend.Items.Where(item => !item.IsAvailable).Select(item => item.Kind));
    }

    [Fact]
    public void LoadingCannotCompleteBeforeTheLaunchIsClaimed()
    {
        var frontend = AtMainMenu();
        frontend.Confirm();
        frontend.Confirm();

        Assert.Throws<InvalidOperationException>(frontend.CompleteLevel100Load);
    }

    [Fact]
    public void GameplayTransitionsExposePauseOwnedRestartAndExitLevelSeams()
    {
        var frontend = AtGameplay();

        Assert.Equal(
            RetailFrontendSignal.Level100LaunchRequested,
            frontend.RestartLevel100());
        Assert.Equal(RetailFrontendScreen.Loading, frontend.Screen);
        Assert.True(frontend.ConsumeLevel100LaunchRequest());
        frontend.CompleteLevel100Load();

        Assert.Equal(
            RetailFrontendSignal.ReturnToMainMenuRequested,
            frontend.LeaveLevel100ForMainMenu());
        Assert.Equal(RetailFrontendScreen.MainMenu, frontend.Screen);
    }

    [Fact]
    public void LifecycleTransitionsRequireActiveGameplay()
    {
        var frontend = AtMainMenu();
        Assert.Throws<InvalidOperationException>(() =>
        {
            _ = frontend.RestartLevel100();
        });
        Assert.Throws<InvalidOperationException>(() =>
        {
            _ = frontend.LeaveLevel100ForMainMenu();
        });
    }

    private static RetailFrontendSession AtMainMenu()
    {
        var frontend = new RetailFrontendSession();
        frontend.Confirm();
        return frontend;
    }

    private static RetailFrontendSession AtGameplay()
    {
        RetailFrontendSession frontend = AtMainMenu();
        frontend.Confirm();
        frontend.Confirm();
        frontend.ConsumeLevel100LaunchRequest();
        frontend.CompleteLevel100Load();
        return frontend;
    }
}
