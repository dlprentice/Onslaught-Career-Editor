// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client;

/// <summary>
/// Presentation-owned state for the bounded released-frontend path into Level 100.
/// Gameplay state remains exclusively owned by <see cref="InteractiveSession"/>.
/// </summary>
public sealed class RetailFrontendSession
{
    private static readonly RetailFrontendMenuItem[] MainMenuItems =
    [
        new(RetailFrontendMenuItemKind.NewGame, IsAvailable: true),
        new(RetailFrontendMenuItemKind.ContinueGame, IsAvailable: false),
        new(RetailFrontendMenuItemKind.LoadGame, IsAvailable: false),
        new(RetailFrontendMenuItemKind.Multiplayer, IsAvailable: false),
        new(RetailFrontendMenuItemKind.Goodies, IsAvailable: false),
        new(RetailFrontendMenuItemKind.Options, IsAvailable: false),
        new(RetailFrontendMenuItemKind.Quit, IsAvailable: true),
    ];

    private bool _level100LaunchPending;

    public RetailFrontendScreen Screen { get; private set; } = RetailFrontendScreen.ClickToStart;

    public int SelectedMainIndex { get; private set; }

    public RetailFrontendMenuItem SelectedMainItem => MainMenuItems[SelectedMainIndex];

    public IReadOnlyList<RetailFrontendMenuItem> Items => MainMenuItems;

    public RetailFrontendMenuItemKind? UnavailableSelection { get; private set; }

    public bool MovePrevious()
    {
        if (Screen != RetailFrontendScreen.MainMenu || SelectedMainIndex == 0)
        {
            return false;
        }

        SelectedMainIndex--;
        UnavailableSelection = null;
        return true;
    }

    public bool MoveNext()
    {
        if (Screen != RetailFrontendScreen.MainMenu || SelectedMainIndex == MainMenuItems.Length - 1)
        {
            return false;
        }

        SelectedMainIndex++;
        UnavailableSelection = null;
        return true;
    }

    public bool SelectMainIndex(int index)
    {
        if (Screen != RetailFrontendScreen.MainMenu ||
            index < 0 ||
            index >= MainMenuItems.Length ||
            index == SelectedMainIndex)
        {
            return false;
        }

        SelectedMainIndex = index;
        UnavailableSelection = null;
        return true;
    }

    public RetailFrontendSignal Confirm()
    {
        UnavailableSelection = null;

        switch (Screen)
        {
            case RetailFrontendScreen.ClickToStart:
                Screen = RetailFrontendScreen.MainMenu;
                SelectedMainIndex = 0;
                return RetailFrontendSignal.PageChanged;

            case RetailFrontendScreen.MainMenu:
                if (!SelectedMainItem.IsAvailable)
                {
                    UnavailableSelection = SelectedMainItem.Kind;
                    return RetailFrontendSignal.Unavailable;
                }

                if (SelectedMainItem.Kind == RetailFrontendMenuItemKind.NewGame)
                {
                    Screen = RetailFrontendScreen.LevelSelect;
                    return RetailFrontendSignal.PageChanged;
                }

                return SelectedMainItem.Kind == RetailFrontendMenuItemKind.Quit
                    ? RetailFrontendSignal.ExitRequested
                    : RetailFrontendSignal.None;

            case RetailFrontendScreen.LevelSelect:
                Screen = RetailFrontendScreen.Loading;
                _level100LaunchPending = true;
                return RetailFrontendSignal.Level100LaunchRequested;

            default:
                return RetailFrontendSignal.None;
        }
    }

    public RetailFrontendSignal Back()
    {
        UnavailableSelection = null;

        if (Screen != RetailFrontendScreen.LevelSelect)
        {
            return RetailFrontendSignal.None;
        }

        Screen = RetailFrontendScreen.MainMenu;
        return RetailFrontendSignal.PageChanged;
    }

    public bool ConsumeLevel100LaunchRequest()
    {
        if (!_level100LaunchPending)
        {
            return false;
        }

        _level100LaunchPending = false;
        return true;
    }

    public void CompleteLevel100Load()
    {
        if (Screen != RetailFrontendScreen.Loading || _level100LaunchPending)
        {
            throw new InvalidOperationException(
                "Level 100 can complete only after its pending launch request is consumed.");
        }

        Screen = RetailFrontendScreen.Gameplay;
    }

    /// <summary>
    /// Restarts the bounded Level 100 run from a pause owned by the gameplay
    /// presenter. Pause is intentionally not a second frontend state machine:
    /// it leaves this lifecycle in Gameplay.
    /// </summary>
    public RetailFrontendSignal RestartLevel100()
    {
        RequireLevel100Transition(nameof(RestartLevel100));
        Screen = RetailFrontendScreen.Loading;
        _level100LaunchPending = true;
        return RetailFrontendSignal.Level100LaunchRequested;
    }

    /// <summary>
    /// Leaves a gameplay-owned pause for the existing startup/main-menu shell.
    /// </summary>
    public RetailFrontendSignal LeaveLevel100ForMainMenu()
    {
        RequireLevel100Transition(nameof(LeaveLevel100ForMainMenu));
        ReturnToMainMenu();
        return RetailFrontendSignal.ReturnToMainMenuRequested;
    }

    private void RequireLevel100Transition(string operation)
    {
        if (Screen != RetailFrontendScreen.Gameplay)
        {
            throw new InvalidOperationException(
                $"{operation} requires an active Level 100 lifecycle.");
        }
    }

    private void ReturnToMainMenu()
    {
        SelectedMainIndex = 0;
        UnavailableSelection = null;
        _level100LaunchPending = false;
        Screen = RetailFrontendScreen.MainMenu;
    }
}

public enum RetailFrontendScreen
{
    ClickToStart,
    MainMenu,
    LevelSelect,
    Loading,
    Gameplay,
}

public enum RetailFrontendSignal
{
    None,
    PageChanged,
    Unavailable,
    Level100LaunchRequested,
    ReturnToMainMenuRequested,
    ExitRequested,
}

public enum RetailFrontendAudioCue
{
    Move,
    Select,
    Back,
}

public enum RetailFrontendCursorMode
{
    Visible,
    Hidden,
    Captured,
}

public enum RetailFrontendMenuItemKind
{
    NewGame,
    ContinueGame,
    LoadGame,
    Multiplayer,
    Goodies,
    Options,
    Quit,
}

public sealed record RetailFrontendMenuItem(
    RetailFrontendMenuItemKind Kind,
    bool IsAvailable);
