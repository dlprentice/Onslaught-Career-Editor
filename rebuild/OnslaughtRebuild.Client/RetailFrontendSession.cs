// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client;

/// <summary>
/// Presentation-owned state for the bounded released-frontend path into Level 100.
/// Gameplay state remains exclusively owned by <see cref="InteractiveSession"/>.
/// </summary>
public sealed class RetailFrontendSession
{
    // Steam-drawn order (CFEPMain__Update / icons): New, Continue, Load,
    // Multiplayer, Goodies, Options, Quit. DoAction pages for sel 3/4/5 are
    // crossed (Options/MP/Goodies) — route by index when those pages land.
    // Index 6: Quit label; DoAction opens FEMessBox with Localization 0xe4.
    private static readonly RetailFrontendMenuItem[] MainMenuItems =
    [
        // IsAvailable models RETAIL's availability, which drives the draw colour -
        // it is not a statement about which pages this reconstruction implements.
        // Measured from the pristine 640x480 main-menu capture: only Continue Game
        // is drawn dim (no career in progress); Load Game, Multiplayer, Goodies and
        // Options are drawn in the normal bright colour exactly like Quit.
        // Confirming a page this reconstruction has not built yet falls through to
        // RetailFrontendSignal.None below, so nothing navigates and nothing throws.
        new(RetailFrontendMenuItemKind.NewGame, IsAvailable: true),
        new(RetailFrontendMenuItemKind.ContinueGame, IsAvailable: false),
        new(RetailFrontendMenuItemKind.LoadGame, IsAvailable: true),
        new(RetailFrontendMenuItemKind.Multiplayer, IsAvailable: true),
        new(RetailFrontendMenuItemKind.Goodies, IsAvailable: true),
        new(RetailFrontendMenuItemKind.Options, IsAvailable: true),
        new(RetailFrontendMenuItemKind.Quit, IsAvailable: true),
    ];

    /// <summary>
    /// Careers this bounded lane knows about on the FEP_DEVSELECT page.
    ///
    /// Retail lists the saved careers found on the selected device. This lane
    /// deliberately carries NO save/career persistence (see
    /// local-lab/STARTUP-FLOW-FINDINGS-2026-07-25.md, "Decision taken"), so the
    /// list is structurally present and always empty. That is a bounded absence,
    /// not a claim that retail shows an empty list.
    /// </summary>
    private static readonly string[] NoCareers = [];

    /// <summary>
    /// Default game name offered by the page. Retail's pristine 640x480
    /// FEP_DEVSELECT capture shows "BEA 1" pre-filled and highlighted in the
    /// name field with no career selected
    /// (local-lab/retail-reference-pristine/choose-game-name/choose-game-name-640x480.png).
    /// </summary>
    public const string DefaultGameName = "BEA 1";

    /// <summary>Retail's name field is bounded; 20 is this lane's bound.</summary>
    public const int MaxGameNameLength = 20;

    private bool _level100LaunchPending;
    private string _gameName = DefaultGameName;

    public RetailFrontendScreen Screen { get; private set; } = RetailFrontendScreen.ClickToStart;

    public int SelectedMainIndex { get; private set; }

    /// <summary>
    /// Active frontend language. data/language ships exactly five sets and
    /// Career.h defines NUM_LANGUAGES 5; CFrontEnd::Init caches all five and
    /// CFrontEnd::SetLanguage swaps the active one.
    /// </summary>
    public RetailFrontendLanguage Language { get; private set; } = RetailFrontendLanguage.English;

    /// <summary>Quit-confirm choice: 0 = No (safe default), 1 = Yes.</summary>
    public int SelectedQuitConfirmIndex { get; private set; }

    public RetailFrontendMenuItem SelectedMainItem => MainMenuItems[SelectedMainIndex];

    public IReadOnlyList<RetailFrontendMenuItem> Items => MainMenuItems;

    public RetailFrontendMenuItemKind? UnavailableSelection { get; private set; }

    /// <summary>Career rows drawn in the FEP_DEVSELECT list panel.</summary>
    public IReadOnlyList<string> CareerNames => NoCareers;

    /// <summary>Highlighted career row, or -1 when no row is highlighted.</summary>
    public int SelectedCareerIndex { get; private set; } = -1;

    /// <summary>Editable contents of the FEP_DEVSELECT name field.</summary>
    public string GameName => _gameName;

    /// <summary>
    /// Moves the FEP_DEVSELECT highlight onto a career row, tracking the
    /// selection into the name field. Observed in the user's live retail frame:
    /// selecting a list entry replaces the field text with that entry.
    /// </summary>
    public bool SelectCareerIndex(int index)
    {
        if (Screen != RetailFrontendScreen.DevSelect ||
            index < 0 ||
            index >= CareerNames.Count ||
            index == SelectedCareerIndex)
        {
            return false;
        }

        SelectedCareerIndex = index;
        _gameName = CareerNames[index];
        return true;
    }

    /// <summary>Types one character into the name field.</summary>
    public bool AppendGameNameCharacter(char character)
    {
        if (Screen != RetailFrontendScreen.DevSelect ||
            _gameName.Length >= MaxGameNameLength ||
            character is < ' ' or > '~')
        {
            return false;
        }

        _gameName += character;
        return true;
    }

    /// <summary>Backspaces one character out of the name field.</summary>
    public bool RemoveGameNameCharacter()
    {
        if (Screen != RetailFrontendScreen.DevSelect || _gameName.Length == 0)
        {
            return false;
        }

        _gameName = _gameName[..^1];
        return true;
    }

    public bool MovePrevious()
    {
        if (Screen == RetailFrontendScreen.QuitConfirm)
        {
            if (SelectedQuitConfirmIndex == 0)
            {
                return false;
            }

            SelectedQuitConfirmIndex = 0;
            return true;
        }

        if (Screen == RetailFrontendScreen.DevSelect)
        {
            return SelectCareerIndex(SelectedCareerIndex - 1);
        }

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
        if (Screen == RetailFrontendScreen.QuitConfirm)
        {
            if (SelectedQuitConfirmIndex == 1)
            {
                return false;
            }

            SelectedQuitConfirmIndex = 1;
            return true;
        }

        if (Screen == RetailFrontendScreen.DevSelect)
        {
            return SelectCareerIndex(SelectedCareerIndex + 1);
        }

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

    public bool SelectQuitConfirmIndex(int index)
    {
        if (Screen != RetailFrontendScreen.QuitConfirm ||
            index is < 0 or > 1 ||
            index == SelectedQuitConfirmIndex)
        {
            return false;
        }

        SelectedQuitConfirmIndex = index;
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
                    // Retail's New Game entry goes to FEP_DEVSELECT, not level
                    // select: CFrontEnd::Init drives the "new career" entry with
                    // SetPage(FEP_DEVSELECT, 0) (references/Onslaught/FrontEnd.cpp:182),
                    // and the pristine 640x480 capture of the page that follows
                    // New Game is the "CHOOSE GAME NAME" screen.
                    Screen = RetailFrontendScreen.DevSelect;
                    SelectedCareerIndex = -1;
                    _gameName = DefaultGameName;
                    return RetailFrontendSignal.PageChanged;
                }

                if (SelectedMainItem.Kind == RetailFrontendMenuItemKind.Quit)
                {
                    Screen = RetailFrontendScreen.QuitConfirm;
                    SelectedQuitConfirmIndex = 0;
                    return RetailFrontendSignal.PageChanged;
                }

                return RetailFrontendSignal.None;

            case RetailFrontendScreen.QuitConfirm:
                if (SelectedQuitConfirmIndex == 0)
                {
                    Screen = RetailFrontendScreen.MainMenu;
                    return RetailFrontendSignal.PageChanged;
                }

                return RetailFrontendSignal.ExitRequested;

            case RetailFrontendScreen.DevSelect:
                Screen = RetailFrontendScreen.LevelSelect;
                return RetailFrontendSignal.PageChanged;

            case RetailFrontendScreen.LevelSelect:
                // Retail does NOT go from level select to loading. The pristine
                // 640x480 capture chain taken 2026-07-25 records
                // SELECT LEVEL -> MISSION BRIEFING -> SELECT CONFIGURATION ->
                // LOADING (local-lab/STARTUP-FLOW-FINDINGS-2026-07-25.md), with a
                // reference frame for each of the three intermediate pages.
                Screen = RetailFrontendScreen.MissionBriefing;
                return RetailFrontendSignal.PageChanged;

            case RetailFrontendScreen.MissionBriefing:
                Screen = RetailFrontendScreen.SelectConfiguration;
                return RetailFrontendSignal.PageChanged;

            case RetailFrontendScreen.SelectConfiguration:
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

        if (Screen == RetailFrontendScreen.QuitConfirm)
        {
            Screen = RetailFrontendScreen.MainMenu;
            return RetailFrontendSignal.PageChanged;
        }

        if (Screen == RetailFrontendScreen.DevSelect)
        {
            Screen = RetailFrontendScreen.MainMenu;
            SelectedCareerIndex = -1;
            _gameName = DefaultGameName;
            return RetailFrontendSignal.PageChanged;
        }

        if (Screen == RetailFrontendScreen.SelectConfiguration)
        {
            Screen = RetailFrontendScreen.MissionBriefing;
            return RetailFrontendSignal.PageChanged;
        }

        if (Screen == RetailFrontendScreen.MissionBriefing)
        {
            Screen = RetailFrontendScreen.LevelSelect;
            return RetailFrontendSignal.PageChanged;
        }

        if (Screen != RetailFrontendScreen.LevelSelect)
        {
            return RetailFrontendSignal.None;
        }

        Screen = RetailFrontendScreen.DevSelect;
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
        SelectedQuitConfirmIndex = 0;
        UnavailableSelection = null;
        SelectedCareerIndex = -1;
        _gameName = DefaultGameName;
        _level100LaunchPending = false;
        Screen = RetailFrontendScreen.MainMenu;
    }
}

public enum RetailFrontendScreen
{
    ClickToStart,
    MainMenu,
    QuitConfirm,

    /// <summary>
    /// Retail FEP_DEVSELECT — the "CHOOSE GAME NAME" page New Game enters
    /// (references/Onslaught/FrontEnd.cpp:120/182/782). Implemented here
    /// visually and sequentially only: no save or career persistence.
    /// </summary>
    DevSelect,
    LevelSelect,

    /// <summary>
    /// Retail's MISSION BRIEFING page, reached from SELECT LEVEL. Reference
    /// frame: local-lab/retail-reference-pristine/mission-briefing/
    /// 05-mission-briefing-640x480.png.
    /// </summary>
    MissionBriefing,

    /// <summary>
    /// Retail's SELECT CONFIGURATION page, between briefing and loading. It was
    /// first observed on 2026-07-25 and the reconstruction had never modelled
    /// it. Reference frame: local-lab/retail-reference-pristine/
    /// select-configuration/06-select-configuration-640x480.png.
    /// </summary>
    SelectConfiguration,
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

/// <summary>
/// The five released frontend languages, ordered to match data/language and the
/// released Flag_UK / Flag_FR / Flag_GR / Flag_IT / Flag_SP texture set.
/// </summary>
public enum RetailFrontendLanguage
{
    English,
    French,
    German,
    Italian,
    Spanish,
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
