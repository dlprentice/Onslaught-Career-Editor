// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

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

    [Theory]
    [InlineData(Level100MissionFailureReason.TutorialBroken)]
    [InlineData(Level100MissionFailureReason.PlayerDeath)]
    [InlineData(Level100MissionFailureReason.WaterLoss)]
    public void FailureHandoffConsumesTheAuthoritativeMissionSnapshot(
        Level100MissionFailureReason reason)
    {
        var frontend = AtGameplay();
        Level100MissionSnapshot terminal = FailureTerminal(reason);

        Assert.True(frontend.TryAcceptMissionTerminal(terminal));

        Assert.Equal(RetailFrontendScreen.TerminalHandoff, frontend.Screen);
        Assert.Equal(RetailFrontendSignal.None, frontend.Confirm());
        Assert.Equal(RetailFrontendSignal.None, frontend.Back());
        Assert.False(frontend.MovePrevious());
        Assert.False(frontend.MoveNext());

        Assert.Equal(RetailFrontendSignal.Level100LaunchRequested, frontend.RestartLevel100());
        Assert.Equal(RetailFrontendScreen.Loading, frontend.Screen);
        Assert.True(frontend.ConsumeLevel100LaunchRequest());
    }

    [Fact]
    public void SuccessHandoffUsesMissionTypesAndHasNoFrontendButtonDefaults()
    {
        var frontend = AtGameplay();
        Level100MissionSnapshot terminal = CreateMission().Snapshot with
        {
            Outcome = Level100MissionOutcome.Won,
            TerminalState = Level100MissionTerminalState.FrontEndHandoffReady,
            FailureReason = Level100MissionFailureReason.None,
        };

        Assert.True(frontend.TryAcceptMissionTerminal(terminal));

        Assert.Equal(RetailFrontendScreen.TerminalHandoff, frontend.Screen);
        Assert.Equal(RetailFrontendSignal.None, frontend.Confirm());
        Assert.Equal(
            RetailFrontendSignal.ReturnToMainMenuRequested,
            frontend.LeaveLevel100ForMainMenu());
        Assert.Equal(RetailFrontendScreen.MainMenu, frontend.Screen);
        Assert.Equal(RetailFrontendMenuItemKind.NewGame, frontend.SelectedMainItem.Kind);
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
    public void TerminalHandoffRejectsPrematureOrInconsistentMissionState()
    {
        var frontend = AtMainMenu();
        Assert.False(frontend.TryAcceptMissionTerminal(CreateMission().Snapshot));
        Assert.Throws<InvalidOperationException>(() =>
        {
            _ = frontend.RestartLevel100();
        });
        Assert.Throws<InvalidOperationException>(() =>
        {
            _ = frontend.LeaveLevel100ForMainMenu();
        });

        frontend = AtGameplay();
        Level100Mission mission = CreateMission();
        Assert.True(mission.ReportPlayerDeath());
        Assert.False(frontend.TryAcceptMissionTerminal(mission.Snapshot));

        Level100MissionSnapshot inconsistent = mission.Snapshot with
        {
            TerminalState = Level100MissionTerminalState.FailureMenuReady,
            FailureReason = Level100MissionFailureReason.None,
        };
        Assert.False(frontend.TryAcceptMissionTerminal(inconsistent));
    }

    private static Level100MissionSnapshot FailureTerminal(
        Level100MissionFailureReason reason)
    {
        Level100Mission mission = CreateMission();
        mission.DrainEvents();
        switch (reason)
        {
            case Level100MissionFailureReason.TutorialBroken:
                Assert.True(mission.SubmitInput(Level100MissionInput.BrokeTutorial));
                for (int tick = 0;
                     mission.Snapshot.Outcome == Level100MissionOutcome.Running && tick < 500;
                     tick++)
                {
                    mission.AdvanceTick(SimulationConstants.MaximumHull);
                }
                Assert.Equal(Level100MissionOutcome.Lost, mission.Snapshot.Outcome);
                break;
            case Level100MissionFailureReason.PlayerDeath:
                Assert.True(mission.ReportPlayerDeath());
                break;
            case Level100MissionFailureReason.WaterLoss:
                Assert.True(mission.ReportWaterLoss());
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(reason));
        }

        for (int tick = 0; tick < Level100MissionTiming.FailureMenuDelayTicks; tick++)
        {
            mission.AdvanceTick(SimulationConstants.MaximumHull);
        }
        Assert.Equal(reason, mission.Snapshot.FailureReason);
        Assert.Equal(
            Level100MissionTerminalState.FailureMenuReady,
            mission.Snapshot.TerminalState);
        return mission.Snapshot;
    }

    private static Level100Mission CreateMission()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1") ??
            throw new InvalidOperationException("Test actor definitions omitted Player 1.");
        return new Level100Mission(actors, player);
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
