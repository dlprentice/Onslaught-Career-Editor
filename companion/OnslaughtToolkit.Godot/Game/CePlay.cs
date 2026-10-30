// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Globalization;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>What a test play came to: whether CE was started and finished, what its log says about the mod, and a sentence for the player.</summary>
/// <param name="Started">Whether Onslaught CE was started.</param>
/// <param name="ExitCode">What the launcher exited with, or null if it was not started or the run was a stand-in.</param>
/// <param name="ModServed">Whether CE's log says it served the mod's world file to the game.</param>
/// <param name="ModLines">The lines of CE's log that are about mods (at most a few).</param>
/// <param name="LogCopy">Where CE's log of this play was kept, or null.</param>
/// <param name="Message">A sentence for the player.</param>
/// <param name="Left">What was left behind in the play folder (a link or a special file), if anything.</param>
internal sealed record CePlayReport(bool Started, int? ExitCode, bool ModServed, IReadOnlyList<string> ModLines, string? LogCopy, string Message, IReadOnlyList<string> Left);

/// <summary>Seams for tests and captures; the app itself passes none.</summary>
/// <param name="Parent">The play folder, instead of the companion's own.</param>
/// <param name="Run">Runs the launcher and returns its exit code, instead of starting a process.</param>
/// <param name="ReadVersion">Answers <c>--version</c> instead of running the launcher.</param>
/// <param name="Environment">Variables to set (or, with a null value, remove) for the launcher, after the companion's own changes.</param>
/// <param name="BeforeRemoval">Called with the play folder after CE closed and before it is removed (a capture keeps its frames here).</param>
/// <param name="Alive">Whether a process id is running, for the stale sweep.</param>
/// <param name="OnWindows">Whether to behave as on Windows.</param>
/// <param name="Now">The clock.</param>
/// <param name="OnStart">Called with the launcher's start (arguments and environment) just before it is run, so a capture can record what CE was given.</param>
internal sealed record CePlayHooks(string? Parent = null, Func<ProcessStartInfo, Task<int>>? Run = null,
    Func<ProcessStartInfo, CancellationToken, Task<string>>? ReadVersion = null, IReadOnlyDictionary<string, string?>? Environment = null,
    Action<string>? BeforeRemoval = null, Func<int, bool>? Alive = null, Func<bool>? OnWindows = null, Func<DateTime>? Now = null, Action<ProcessStartInfo>? OnStart = null);

/// <summary>
/// "Play this level with the mod": starts Onslaught CE at a level with the edit being tried, without writing anything of the player's. It makes a
/// temporary CE user folder (see <see cref="CePlayFolder"/>) holding a copy of the player's ce.ini with <c>mods=</c> naming the mod, recording
/// and the update check off, a copy of their options file (never a career) and the mod itself, starts CE's launcher with <c>BEA_USER_DIR</c> and
/// <c>BEA_GAME_DIR</c> pointing at that folder and at the game folder the Level editor read, waits for CE to close, keeps CE's log, and removes
/// the folder. The player's own CE folder, ce.ini and careers are never written, and no mod stays switched on in them if the companion or CE dies.
/// </summary>
internal sealed class CePlay
{
    /// <summary>The first Onslaught CE that takes a level's world file from a mod.</summary>
    internal const string FirstVersionWithWorldMods = "0.1.11";

    /// <summary>The variables that make CE switch mods off (port/platform/common/mods.cpp): a test play must never inherit one.</summary>
    internal static readonly IReadOnlyList<string> FenceVariables =
    [
        "BEA_PORT_CLOCK", "BEA_PORT_TAPE", "BEA_PORT_PROBES", "BEA_PORT_RECORD", "BEA_PORT_PILOT", "BEA_PORT_AUTOPILOT", "BEA_NET_HOST", "BEA_NET_JOIN", "BEA_NET_HANDOFF",
    ];

    private const long LogLimit = 1 << 20, OptionsLimit = 1 << 20;
    private readonly GameLibrary _game;
    private readonly CePlayHooks _hooks;
    private string? _current;

    internal CePlay(GameLibrary game, string defaultParent, CePlayHooks? hooks = null)
    {
        _game = game;
        _hooks = hooks ?? new CePlayHooks();
        Parent = _hooks.Parent ?? defaultParent;
    }

    /// <summary>The companion's own play folder: every temporary CE user folder is a child of it.</summary>
    internal string Parent { get; }

    /// <summary>Where the log of the last test play is kept.</summary>
    internal string LastLog => Path.Combine(Parent, "last-session.log");

    /// <summary>Whether a test play is running now.</summary>
    internal bool Running { get; private set; }

    /// <summary>What the latest test play (or refused one) came to, or null before the first.</summary>
    internal CePlayReport? Last { get; private set; }

    /// <summary>Raised when a test play starts or ends, so a page can enable and disable its button.</summary>
    internal event Action? Changed;

    private bool OnWindows => _hooks.OnWindows?.Invoke() ?? OperatingSystem.IsWindows();

    /// <summary>The reason a test play cannot start now, as a sentence for the player, or null if it can (the launcher's version is read when it starts).</summary>
    internal string? Unavailable()
    {
        if (OnWindows) return "Onslaught CE loads a level's world from a mod on Linux only for now.";
        if (Running) return "Onslaught CE is running a test play already.";
        if (_game.Ce is null) return "Choose the Onslaught CE launcher on Home first: a test play starts CE.";
        if (_game.CeUserFolder.Length == 0) return "Onslaught CE's user folder is not known, so a test play has no settings to start from.";
        if (_game.Folder?.AssetRoot is not string assets || !Directory.Exists(assets)) return "The companion has no game folder to give Onslaught CE.";
        if (_game.CeVersion is { } version && !CeInstallation.IsAtLeast(version.Version, FirstVersionWithWorldMods)) return TooOld(version.Version);
        return null;
    }

    private static string TooOld(string version) =>
        $"This is Onslaught CE {version}. Taking a level's world from a mod needs {FirstVersionWithWorldMods} or later, so a test play would show the unchanged level. Update CE first.";

    /// <summary>
    /// Removes the temporary folders an earlier companion left behind. Only direct children of the play folder that carry this companion's marker
    /// are touched, and none whose companion or CE is still running.
    /// </summary>
    internal CePlaySweep SweepStale() => CePlayFolder.SweepStale(Parent, Environment.ProcessId, _current,
        _hooks.Alive ?? (pid => OperatingSystem.IsLinux() && Directory.Exists("/proc/" + pid.ToString(CultureInfo.InvariantCulture))));

    private CePlayReport Refused(string message) => Last = new CePlayReport(false, null, false, [], null, message, []);

    /// <summary>
    /// Starts CE at <paramref name="level"/> with the mod that <paramref name="stage"/> writes into the folder it is given, under the id and name it is given
    /// (the mod's own folder is made there), waits for CE to close, and reports. Nothing the player owns is written; whatever the temporary folder held is removed.
    /// </summary>
    internal async Task<CePlayReport> PlayAsync(int level, Func<string, ModInfo, SaveOutcome> stage, CancellationToken cancellationToken = default)
    {
        if (Unavailable() is string why) return Refused(why);
        CeInstallation ce = _game.Ce!;
        string gameFolder = _game.Folder!.AssetRoot;
        Running = true;
        Changed?.Invoke();
        CePlayFolder? folder = null;
        bool settled = false;   // the folder has had its removal (the one after CE closed); anything else is removed on the way out
        try
        {
            Outcome<string> safety = ce.CheckLauncherSafety();
            if (!safety.Ok) return Refused(safety.Message);
            string versionText;
            if (_game.CeVersion is { } known) versionText = known.Version;
            else
            {
                Outcome<CeVersion> read = await ce.ReadVersionAsync(cancellationToken, _hooks.ReadVersion);
                if (read.Value is not CeVersion got) return Refused(read.Message);
                versionText = got.Version;
            }
            if (!CeInstallation.IsAtLeast(versionText, FirstVersionWithWorldMods)) return Refused(TooOld(versionText));

            if (SharesAFolderWithTheRealOne(Parent) is string before)
                return Refused($"The play folder ({Parent}) and {before} are the same place or one is inside the other, so nothing was started.");
            string id = $"play-level-{level.ToString(CultureInfo.InvariantCulture)}";
            Outcome<CePlayFolder> made = CePlayFolder.Create(Parent, level, id, Environment.ProcessId, _hooks.Now?.Invoke() ?? DateTime.UtcNow);
            if (made.Value is not CePlayFolder created) return Refused(made.Message);
            folder = created;
            _current = folder.Root;
            if (SharesAFolderWithTheRealOne(folder.Root) is string clash)
                return Refused($"The folder made for the test play ({folder.Root}) and {clash} are the same place or one is inside the other, so nothing was started.");   // links resolved: the check above is on the names

            SaveOutcome staged = stage(Path.Combine(folder.Root, "mods"),
                new ModInfo(id, $"Test play of level {level.ToString(CultureInfo.InvariantCulture)}", "1", "", "Made by the Onslaught Companion for one test play; it is not kept."));
            if (!staged.Ok) return Refused(staged.Message);

            string settingsNote = WriteSettings(folder, id);
            string? optionsNote = folder.CopyRegular(Path.Combine(_game.CeUserFolder, "defaultoptions.bea"), "defaultoptions.bea", OptionsLimit);

            ProcessStartInfo start = StartInfo(ce, folder.Root, gameFolder, level);
            _hooks.OnStart?.Invoke(start);
            int? exit;
            if (_hooks.Run is { } run) exit = await run(start);
            else exit = await RunProcessAsync(start, folder, cancellationToken);
            if (exit is null) return Refused("The CE launcher could not be started.");

            string log = Path.Combine(folder.Root, "onslaught-ce.log");
            (IReadOnlyList<string> modLines, bool served) = ReadModLines(log, id);
            string? kept = KeepLog(log);
            _hooks.BeforeRemoval?.Invoke(folder.Root);
            CePlayRemoval removal = folder.Remove();
            settled = true;
            string message = Compose(level, exit.Value, served, kept, settingsNote, optionsNote, removal);
            return Last = new CePlayReport(true, exit, served, modLines, kept, message, removal.Left);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or System.ComponentModel.Win32Exception or InvalidOperationException)
        {
            return Refused("The test play stopped: " + error.Message);
        }
        finally
        {
            // A folder that was made and never got as far as CE (a refusal, a failure on the way) is removed here; one CE ran in was removed, or reported, above.
            if (folder is not null && !settled)
            {
                try
                {
                    folder.Remove();
                }
                catch (Exception error) when (error is IOException or UnauthorizedAccessException)
                {
                    // What cannot go stays, with its marker, for the next start's sweep.
                }
            }
            _current = null;
            Running = false;
            Changed?.Invoke();
        }
    }

    /// <summary>The launcher's start: the package folder as the working folder, BEA_USER_DIR and BEA_GAME_DIR set, the variables that switch mods off removed.</summary>
    internal ProcessStartInfo StartInfo(CeInstallation ce, string userFolder, string gameFolder, int level)
    {
        ProcessStartInfo start = new(ce.LauncherPath) { UseShellExecute = false, WorkingDirectory = ce.Folder };
        // The launcher reads its own options first and takes everything from the first other argument on as the game's: CE's own switches before the level.
        foreach (string argument in new[] { "--no-update-check", "-level", level.ToString(CultureInfo.InvariantCulture), "-skipfmv", "-forcewindowed" })
            start.ArgumentList.Add(argument);
        foreach (string name in FenceVariables) start.Environment.Remove(name);
        start.Environment["BEA_USER_DIR"] = userFolder;
        start.Environment["BEA_GAME_DIR"] = gameFolder;
        if (_hooks.Environment is { } more)
            foreach ((string name, string? value) in more)
            {
                if (value is null) start.Environment.Remove(name);
                else start.Environment[name] = value;
            }
        return start;
    }

    private async Task<int?> RunProcessAsync(ProcessStartInfo start, CePlayFolder folder, CancellationToken cancellationToken)
    {
        using Process? process = Process.Start(start);
        if (process is null) return null;
        folder.RecordLauncher(process.Id);
        await process.WaitForExitAsync(cancellationToken);
        return process.ExitCode;
    }

    /// <summary>
    /// The temporary ce.ini: the player's own lines kept as they are, with mods= naming only the mod being tried, recording off and the update check
    /// off. If theirs cannot be read safely, CE's defaults stand in and the sentence says so.
    /// </summary>
    private string WriteSettings(CePlayFolder folder, string id)
    {
        Outcome<CeSettings> read = CeSettings.Read(_game.CeUserFolder);
        string note = "";
        CeSettings settings;
        if (read.Value is CeSettings theirs) settings = theirs;
        else
        {
            settings = CeSettings.Parse(Path.Combine(_game.CeUserFolder, "ce.ini"), false, []).Value!;
            note = " Your ce.ini could not be read safely, so CE's own defaults were used: " + read.Message;
        }
        Outcome<byte[]> prepared = settings.PrepareValues([("mods", id), ("record_sessions", "0"), ("update_check", "0")]);
        if (prepared.Value is not byte[] bytes) throw new InvalidOperationException(prepared.Message);
        folder.WriteFile("ce.ini", bytes);
        return note;
    }

    /// <summary>The first real folder of CE's that <paramref name="playRoot"/> is, is inside or holds, or null: a test play never runs in the player's own.</summary>
    private string? SharesAFolderWithTheRealOne(string playRoot)
    {
        IEnumerable<string> real = OnslaughtCe.UserFolders().Append(_game.CeUserFolder).Append(_game.Folder?.Root ?? "").Where(path => path.Length > 0);
        foreach (string candidate in real)
        {
            string a = Path.TrimEndingDirectorySeparator(ExportFiles.RealPath(playRoot)), b = Path.TrimEndingDirectorySeparator(ExportFiles.RealPath(candidate));
            if (string.Equals(a, b, StringComparison.Ordinal) || ExportFiles.Inside(a, b) || ExportFiles.Inside(b, a)) return candidate;
        }
        return null;
    }

    /// <summary>The lines of CE's log about mods (the first few) and whether it says it served this mod's world file to the game.</summary>
    private static (IReadOnlyList<string>, bool) ReadModLines(string log, string id)
    {
        List<string> lines = [];
        bool served = false;
        try
        {
            if (!File.Exists(log)) return (lines, false);
            using FileStream stream = new(log, new FileStreamOptions { Mode = FileMode.Open, Access = FileAccess.Read, Share = FileShare.ReadWrite });
            byte[] head = new byte[Math.Min(stream.Length, LogLimit)];
            stream.ReadExactly(head);
            foreach (string line in System.Text.Encoding.UTF8.GetString(head).Split('\n'))
            {
                string text = line.TrimEnd('\r');
                if (!text.Contains(" mods: ", StringComparison.Ordinal) && !text.StartsWith("mods:", StringComparison.Ordinal)) continue;
                if (text.Contains($"{id} serves ", StringComparison.Ordinal) && text.Contains("data/worlds/world", StringComparison.Ordinal)) served = true;
                if (lines.Count < 6) lines.Add(text.Length > 240 ? text[..240] + "…" : text);
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            // No log to read: the report says CE's log was not found.
        }
        return (lines, served);
    }

    /// <summary>Keeps the first megabyte of CE's log as <see cref="LastLog"/>, beside the temporary folders, for diagnosis. Null if there was none.</summary>
    private string? KeepLog(string log)
    {
        try
        {
            if (!File.Exists(log)) return null;
            using FileStream source = new(log, new FileStreamOptions { Mode = FileMode.Open, Access = FileAccess.Read, Share = FileShare.ReadWrite });
            byte[] head = new byte[Math.Min(source.Length, LogLimit)];
            source.ReadExactly(head);
            string temporary = LastLog + ".new";
            File.WriteAllBytes(temporary, head);
            File.Move(temporary, LastLog, overwrite: true);
            return LastLog;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    private static string Compose(int level, int exit, bool served, string? kept, string settingsNote, string? optionsNote, CePlayRemoval removal)
    {
        string text = exit == 0 ? $"Onslaught CE ran level {level} with your changes and closed." : $"Onslaught CE closed with exit code {exit}.";
        text += served ? " Its log says it loaded the mod's world file." :
            " Its log does not say it loaded the mod's world file, so the level may have been the unchanged one" + (kept is null ? " (CE wrote no log)." : $" (see {kept}).");
        if (optionsNote is not null) text += " Your options were not copied (" + optionsNote.TrimEnd('.') + ").";
        text += settingsNote;
        if (!removal.Removed) text += " " + removal.Message;
        return text;
    }
}
