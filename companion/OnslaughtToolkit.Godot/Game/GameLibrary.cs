// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>
/// Owns which game folder the companion uses: the folder the player chose, or the one Steam's own
/// records name. Detection and inspection run off the interface thread and only read.
/// </summary>
public sealed class GameLibrary(IReadOnlyList<string> steamRoots, SettingsStore settings, string? ceUserFolder = null,
    Func<string, string?>? ceEnvironment = null, Func<string, bool>? ceInstallSupported = null)
{
    public GameFolder? Folder { get; private set; }
    public GameFolder? Original { get; private set; }
    public CeInstallation? Ce { get; private set; }
    public string? CePackageRoot { get; private set; }
    public string? CeOriginalRoot { get; private set; }
    public CeVersion? CeVersion { get; private set; }
    public string CeVersionMessage { get; private set; } = "Choose a CE launcher to read its version.";

    public async Task<Outcome<CeInstallation>> ChooseCeAsync(string path)
    {
        if (Busy) return Outcome<CeInstallation>.Refusal("A game folder is still being read.");
        Outcome<CeInstallation> selected = CeInstallation.Inspect(path, CeUserFolder);
        if (selected.Value is not CeInstallation ce) return selected;
        SetBusy(true);
        try
        {
            Ce = ce;
            CePackageRoot = ce.Folder;
            CompanionSettings saved = Settings.Load();
            saved.CeLauncher = ce.LauncherPath;
            bool remembered = Settings.Save(saved);
            await ReadCeVersionAsync();
            SelectFolder();
            return Outcome<CeInstallation>.Success(ce, remembered ? "CE launcher selected." : "CE launcher selected, but could not be remembered.");
        }
        finally { SetBusy(false); }
    }

    private async Task ReadCeVersionAsync()
    {
        CeVersion = null;
        if (Ce is null) { CeVersionMessage = "Choose a CE launcher to read its version."; return; }
        Outcome<CeVersion> version = await Ce.ReadVersionAsync();
        CeVersion = version.Value;
        CeVersionMessage = version.Value?.Display ?? version.Message;
    }

    public GameTarget Target { get; private set; } = settings.Load().Target;
    public string CeUserFolder { get; } = ceUserFolder ?? CeInstallation.ResolveUserFolder().Value ?? "";

    public async Task SelectTargetAsync(GameTarget target)
    {
        if (Busy) return;
        Folder = null;
        Target = target;
        CompanionSettings saved = Settings.Load();
        saved.Target = target;
        Settings.Save(saved);
        await DetectAsync();
    }

    private void SelectFolder()
    {
        CeOriginalRoot = Target == GameTarget.OnslaughtCe && CeUserFolder.Length > 0 ? CeOriginalFolder() : null;
        if (Target == GameTarget.OnslaughtCe && CeUserFolder.Length > 0)
        {
            try
            {
                CeInstallation.RejectFolderInAnyPackage(CeUserFolder, "CE's user folder");
                CeGameData.RejectWriteFolder(CeUserFolder, CeOriginalRoot, "CE's user folder");
                if (CePackageRoot is not null) CeInstallation.RejectFolderInPackage(CeUserFolder, CePackageRoot, "CE's user folder");
            }
            catch (IOException error) { Folder = null; CeVersionMessage = error.Message; return; }
        }
        Folder = Target == GameTarget.OnslaughtCe && CeUserFolder.Length > 0
            ? GameFolder.InspectCe(CeUserFolder, Original?.Root, CeOriginalRoot, CePackageRoot) : Original;
        if (Target == GameTarget.OnslaughtCe && CeUserFolder.Length == 0) Folder = null;
    }

    private string CeOriginalFolder()
    {
        // Launcher find_game: valid BEA_GAME_DIR, then ce.ini gamedir, then discovery.
        string? env = (ceEnvironment ?? Environment.GetEnvironmentVariable)("BEA_GAME_DIR");
        string? ini = CeSettings.Read(CeUserFolder).Value?.GameDirectory;
        return CeGameData.Resolve(ceEnvironment is null ? SteamLibraries.DefaultRoots(ceOnly: true) : steamRoots,
            env, ini, ceInstallSupported) ?? "";
    }

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
            (Original, Text) = await Task.Run(() =>
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
            if (CeUserFolder.Length > 0)
            {
                CePackageRoot = CeInstallation.FindPackageFolder(Settings.Load().CeLauncher, ceEnvironment, home: ceEnvironment is null ? null : "");
                Ce = CeInstallation.Find(Settings.Load().CeLauncher, CeUserFolder, ceEnvironment, home: ceEnvironment is null ? null : "");
            }
            if (Target == GameTarget.OnslaughtCe) await ReadCeVersionAsync();
            SelectFolder();
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
            (Original, Text) = (folder, text);
            SelectFolder();
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
            if (Target == GameTarget.OnslaughtCe)
                SelectFolder();
            else
            {
                (Original, Text) = await Task.Run(() => GameFolder.LooksLikeGame(current.Root) ? Read(current.Root, current.Source) : (null, null));
                Folder = Original;
            }
            return Folder;
        }
        finally
        {
            SetBusy(false);
        }
    }

    /// <summary>
    /// Whether the careers or the settings file differ from the last reading by name, size or time: a cheap
    /// check that decides whether the folder needs reading again. Reads only file listings.
    /// </summary>
    public bool FilesChanged()
    {
        if (Busy || Folder is not GameFolder folder) return false;
        try
        {
            HashSet<(string, long, DateTime)> now = [];
            if (folder.Target == GameTarget.OnslaughtCe)
            {
                HashSet<string> seen = new(StringComparer.OrdinalIgnoreCase);
                foreach (string root in new[] { folder.Root, CeOriginalFolder() }.Where(root => root.Length > 0))
                    foreach (FileInfo file in GameFolder.CeCareerFiles(root))
                        if (seen.Add(file.Name)) now.Add((file.FullName, file.Length, file.LastWriteTime));
            }
            else if (Directory.Exists(folder.SavegamesPath))
            {
                foreach (FileInfo file in new DirectoryInfo(folder.SavegamesPath).EnumerateFiles("*.bes"))
                    now.Add((file.FullName, file.Length, file.LastWriteTime));
            }
            FileInfo options = new(folder.OptionsPath);
            if (folder.Target == GameTarget.Original && options.Exists) now.Add((options.FullName, options.Length, options.LastWriteTime));
            return !now.SetEquals(folder.Careers.Append(folder.Options).OfType<GameFile>().Select(file => (file.Path, file.Size, file.Modified)));
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return true;
        }
    }

    private static (GameFolder?, GameText?) Read(string root, string source) => (GameFolder.Inspect(root, source), GameText.Load(root));

    private void SetBusy(bool busy)
    {
        Busy = busy;
        Changed?.Invoke();
    }
}
