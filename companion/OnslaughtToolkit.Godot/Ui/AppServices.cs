// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>What every page may use: the open career, the game, backups, the status line and navigation.</summary>
internal sealed class AppServices
{
    internal required CareerWorkspace Workspace { get; init; }
    internal required GameLibrary Game { get; init; }
    internal required StatusLine Status { get; init; }
    internal required BackupLocation Backups { get; init; }

    /// <summary>Whether Battle Engine Aquila is running now; the companion never writes into its folder while it is.</summary>
    internal required Func<bool> GameRunning { get; init; }

    internal required Action<string> OpenUrl { get; init; }
    internal required Action<string> Navigate { get; init; }
    internal required Func<string, Task<Outcome<SaveSession>>> OpenCareer { get; init; }

    /// <summary>The node dialogs are added to, so they draw above every page.</summary>
    internal required Node Popups { get; init; }

    /// <summary>The backup folder, created if needed, or null with the reason shown to the player.</summary>
    internal string? BackupFolderOrReport()
    {
        if (Backups.Ensure() is string folder) return folder;
        Status.Show($"The backup folder {Backups.Folder} could not be created. Choose another on Backups; nothing was changed.",
            StatusKind.Failure);
        return null;
    }
}
