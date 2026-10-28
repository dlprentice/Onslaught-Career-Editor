// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>What every page may use: the open career, the game, backups, the status line and navigation.</summary>
internal sealed class AppServices
{
    internal const string GameWriteGuidance = "Close Battle Engine Aquila and Onslaught CE before continuing. " +
        "Wait until the operation finishes before starting either.";
    internal const string GameWriteChecks = "The companion checks for either game before backup and just before writing.";

    internal required CareerWorkspace Workspace { get; init; }
    internal required GameLibrary Game { get; init; }
    internal required StatusLine Status { get; init; }
    internal required BackupLocation Backups { get; init; }

    /// <summary>Whether either game is detected now; this check cannot prevent a later start.</summary>
    internal required Func<bool> GameRunning { get; init; }

    internal required Action<string> OpenUrl { get; init; }
    internal Func<GameTarget, Task>? SelectTarget { get; init; }

    internal required Action<string> Navigate { get; init; }
    /// <summary>Opens a career read-only as the open one, without asking; for the companion's own reopen after a save.</summary>
    internal required Func<string, Task<Outcome<SaveSession>>> OpenCareer { get; init; }

    /// <summary>Opens a career the player chose, asking first if Edit career holds unsaved changes.</summary>
    internal required Func<string, Task<Outcome<SaveSession>>> ChooseCareer { get; init; }

    /// <summary>Asks for a career file anywhere on the computer and opens it read-only.</summary>
    internal required Action OpenCareerFile { get; init; }

    /// <summary>Where the retired Windows toolkit kept its copied installs (<see cref="OldSafeCopies"/>), or null.</summary>
    internal string? OldCopiesFolder { get; init; }

    /// <summary>The node dialogs are added to, so they draw above every page.</summary>
    internal required Node Popups { get; init; }

    /// <summary>Reads the game folder again after a write and brings the open career and settings up to date.</summary>
    internal required Func<Task> CatchUp { get; init; }

    /// <summary>The backup folder, created if needed, or null with the reason shown to the player.</summary>
    internal string? BackupFolderOrReport()
    {
        if (Backups.Ensure(Game.CePackageRoot, Game.CeOriginalRoot) is string folder) return folder;
        Status.Show($"The backup folder {Backups.Folder} could not be created. Choose another on Backups; nothing was changed.",
            StatusKind.Failure);
        return null;
    }

    /// <summary>Why a new career cannot have this name in the game (a name Windows refuses, or one a career already has), or null.</summary>
    internal string? CareerNameProblem(string name) =>
        GameInstaller.PortableNameProblem(name) ?? (Game.Folder?.Careers.Any(career =>
            string.Equals(career.DisplayName, name, StringComparison.OrdinalIgnoreCase)) == true
            ? $"Your game already has a career called {name}." : null);

    /// <summary>A name no career in the game has yet: "Pilot", then "Pilot (2)" and so on.</summary>
    internal string NewCareerName(string wanted)
    {
        string name = wanted.Trim();
        for (int number = 2; CareerNameProblem(name) is not null && number < 100; number++) name = $"{wanted.Trim()} ({number})";
        return name;
    }
}
