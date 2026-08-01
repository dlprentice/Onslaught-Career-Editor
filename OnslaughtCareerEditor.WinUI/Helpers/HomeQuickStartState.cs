using System;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// Which single step stands between the person in front of the app and a
    /// running game.
    /// </summary>
    public enum HomeQuickStartStage
    {
        /// <summary>Nothing is configured. The app does not know where the game is.</summary>
        FindGame,

        /// <summary>A folder is set but it is not a full install.</summary>
        FixGame,

        /// <summary>The game is known and there is nothing to play yet.</summary>
        MakeCopy,

        /// <summary>A playable copy exists and is not running.</summary>
        Play,

        /// <summary>A copy this app started is running now.</summary>
        Running,
    }

    /// <summary>
    /// The quick-start card's whole content, resolved from state so it can be
    /// tested without a UI.
    ///
    /// The point of this type is that a new player should never have to read a
    /// page to work out what to do. At any moment there is exactly one sensible
    /// next action, it has a button, and the button says what will happen.
    /// </summary>
    public sealed record HomeQuickStartState(
        HomeQuickStartStage Stage,
        string Title,
        string Body,
        string PrimaryActionLabel,
        bool ShowsSecondaryChooseFolder)
    {
        public static HomeQuickStartState Resolve(
            bool gameFolderSet,
            bool gameFolderComplete,
            bool safeCopyExists,
            bool safeCopyRunning)
        {
            if (safeCopyRunning)
            {
                return new HomeQuickStartState(
                    HomeQuickStartStage.Running,
                    "Your game is running",
                    "Battle Engine Aquila is open in a copy this app made, so your installed game is not the one running.",
                    "Stop the game",
                    ShowsSecondaryChooseFolder: false);
            }

            if (!gameFolderSet)
            {
                return new HomeQuickStartState(
                    HomeQuickStartStage.FindGame,
                    "Let's get Battle Engine Aquila running",
                    "First the app needs to know where the game is installed. It reads that folder and works in a separate copy, unless you later choose to patch the game itself.",
                    "Find my game",
                    ShowsSecondaryChooseFolder: true);
            }

            if (!gameFolderComplete)
            {
                return new HomeQuickStartState(
                    HomeQuickStartStage.FixGame,
                    "That folder is missing some of the game",
                    "The folder that was saved does not have both BEA.exe and the data folder in it. Choose the folder you installed the game into.",
                    "Find my game",
                    ShowsSecondaryChooseFolder: true);
            }

            if (!safeCopyExists)
            {
                return new HomeQuickStartState(
                    HomeQuickStartStage.MakeCopy,
                    "Ready when you are",
                    "One button makes a separate playable copy of the game, fixes it for a widescreen monitor, and starts it windowed. It takes a few seconds and leaves your installed game alone.",
                    "Set up and play",
                    ShowsSecondaryChooseFolder: false);
            }

            return new HomeQuickStartState(
                HomeQuickStartStage.Play,
                "Ready to play",
                "Your playable copy is set up, widescreen-corrected, and ready to go.",
                "Play",
                ShowsSecondaryChooseFolder: false);
        }

        /// <summary>
        /// The line shown while the copy is being made. Named here so it is
        /// covered by the same copy tests as everything else on the card.
        /// </summary>
        public const string WorkingLabel = "Setting up your copy...";

        public const string LaunchingLabel = "Starting the game...";
    }
}
