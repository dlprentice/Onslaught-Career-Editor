// SPDX-License-Identifier: MIT
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>
/// Owns which game folder the companion uses: the folder the player chose, or the one Steam's own
/// records name. Detection and inspection run off the interface thread and only read.
/// </summary>
public sealed class GameLibrary(IReadOnlyList<string> steamRoots, SettingsStore settings)
{
    public GameFolder? Folder { get; private set; }

    /// <summary>The game's own words from the folder's language file, when it can be read.</summary>
    public GameText? Text { get; private set; }
    public bool Busy { get; private set; }
    public SettingsStore Settings { get; } = settings;

    /// <summary>Raised on the main thread when detection starts, finishes or changes the folder.</summary>
    public event Action? Changed;

    public async Task<GameFolder?> DetectAsync()
    {
        if (Busy) return Folder;
        SetBusy(true);
        try
        {
            string? chosen = Settings.Load().GameFolder;
            (Folder, Text) = await Task.Run(() =>
            {
                if (chosen is not null && SteamLibraries.Canonical(chosen) is string real && GameFolder.LooksLikeGame(real))
                    return Read(real, "Chosen by you");
                foreach (GameCandidate candidate in SteamLibraries.FindGame(steamRoots))
                {
                    if (GameFolder.LooksLikeGame(candidate.Root))
                        return Read(candidate.Root, "Found through Steam in " + candidate.Library);
                }
                return (null, null);
            });
            return Folder;
        }
        finally
        {
            SetBusy(false);
        }
    }

    /// <summary>Uses a folder the player chose, if it holds BEA.exe and the data folder, and remembers it.</summary>
    public async Task<Outcome<GameFolder>> ChooseAsync(string path)
    {
        if (Busy) return Outcome<GameFolder>.Refusal("The game folder is still being checked.");
        string? real = SteamLibraries.Canonical(path);
        if (real is null || !GameFolder.LooksLikeGame(real))
            return Outcome<GameFolder>.Refusal("That folder does not contain BEA.exe and a data folder. Choose the folder the game is installed in.");
        SetBusy(true);
        try
        {
            (GameFolder? folder, GameText? text) = await Task.Run(() => Read(real, "Chosen by you"));
            CompanionSettings saved = Settings.Load();
            saved.GameFolder = real;
            string note = Settings.Save(saved) ? "" : " It could not be remembered for next time.";
            (Folder, Text) = (folder, text);
            return Outcome<GameFolder>.Success(folder!, "Game folder set." + note);
        }
        finally
        {
            SetBusy(false);
        }
    }

    /// <summary>Reads the current folder again, for example after the game saved a new career.</summary>
    public async Task<GameFolder?> RescanAsync()
    {
        if (Folder is not GameFolder current) return await DetectAsync();
        if (Busy) return Folder;
        SetBusy(true);
        try
        {
            (Folder, Text) = await Task.Run(() => GameFolder.LooksLikeGame(current.Root) ? Read(current.Root, current.Source) : (null, null));
            return Folder;
        }
        finally
        {
            SetBusy(false);
        }
    }

    private static (GameFolder?, GameText?) Read(string root, string source) => (GameFolder.Inspect(root, source), GameText.Load(root));

    private void SetBusy(bool busy)
    {
        Busy = busy;
        Changed?.Invoke();
    }
}
