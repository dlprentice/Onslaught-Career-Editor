// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Text.Json;
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Options;
using OnslaughtToolkit.Companion.Ui;
using Environment = System.Environment;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Opt-in acceptance on an explicitly prepared, disposable CE package/profile. Calls production services and
/// UI actions, without a fake running-game check. The ordinary suite never executes this entry. The caller owns
/// GPU/resource locks and supplies ONSLAUGHT_CE_LIVE_CHECK pointing to a private JSON configuration. This entry
/// does not copy installations, fabricate saves, download packages, or operate on a player's normal profile.
/// </summary>
public partial class CeLiveCheck : SceneTree
{
    private readonly List<object> _observations = [];
    private CompanionApp? _app;
    private string _owner = "";
    private bool _ownerAdmitted;

    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exit = 1;
        string phase = "unknown";
        try
        {
            string configPath = Environment.GetEnvironmentVariable("ONSLAUGHT_CE_LIVE_CHECK") ??
                throw new IOException("Explicit ONSLAUGHT_CE_LIVE_CHECK configuration required.");
            using JsonDocument config = JsonDocument.Parse(File.ReadAllText(configPath));
            string Required(string key) => config.RootElement.GetProperty(key).GetString() ?? throw new IOException(key);
            _owner = Path.GetFullPath(Required("owner"));
            if (!File.Exists(Path.Combine(_owner, ".companion-owned")))
                throw new IOException("Prepared isolated owner marker required.");
            _ownerAdmitted = true;
            string requestedPhase = Required("phase");
            if (requestedPhase is not ("prepare" or "launch" or "restore" or "settings" or "workflow"))
                throw new IOException("Phase must be prepare, launch, restore, settings or workflow.");
            phase = requestedPhase;
            string launcher = Owned(Required("launcher")), user = Owned(Required("user")),
                baseline = Owned(Required("baseline")), backups = Owned(Required("backups"));
            string career = Owned(Path.Combine(user, "savegames", "Companion Pilot.bes"));
            string game = Path.GetFullPath(Required("game"));
            if (!File.Exists(baseline) || !File.Exists(career) || !Directory.Exists(backups))
                throw new IOException("Prepare the copied real career, baseline and backup directory first.");
            bool captureWorkflow = phase == "workflow" && config.RootElement.TryGetProperty("capture", out JsonElement capture) && capture.GetBoolean();
            if (phase == "workflow")
            {
                AdmitWorkflow(config.RootElement, launcher, baseline, career);
                if (captureWorkflow && DisplayServer.GetName() == "headless")
                    throw new IOException("Workflow screenshots require rendering; headless execution cannot establish visual acceptance.");
            }
            if (GameProcess.IsRunning()) throw new IOException("A game is already running; acceptance must have exclusive game ownership.");
            Environment.SetEnvironmentVariable("BEA_USER_DIR", user);
            Environment.SetEnvironmentVariable("BEA_GAME_DIR", game);
            SettingsStore settings = new(Owned(Path.Combine(_owner, "settings.json")));
            settings.Save(new CompanionSettings { Target = GameTarget.OnslaughtCe, CeLauncher = launcher,
                GameFolder = game, AutoBackup = false });
            _app = new CompanionApp(new ProtectedSaveFiles(), false, new CompanionEnvironment([], settings.FilePath,
                DefaultBackupFolder: backups, CeUserFolder: user, OldCopiesFolder: Owned(Path.Combine(_owner, "old-copies"))));
            Root.AddChild(_app);
            await Frame();
            await Until(() => !_app.Game.Busy && _app.Game.CeVersion is not null, 15, "CE discovery and actual --version");
            Require(_app.Game.Ce is not null && _app.Game.Folder?.Root == user, "CE package and user folder discovered");
            if (phase == "workflow")
                Require(_app.Game.CeVersion?.Version == Required("expectedVersion"), "Actual selected launcher version equals the pinned expected version");
            Observe("version", _app.Game.CeVersion!);
            await Until(() => !_app.Game.Busy && !_app.Workspace.Busy && _app.Workspace.Session is not null, 15,
                "Automatic career opening completed");
            Outcome<SaveSession> opened = await _app.Workspace.OpenAsync(career);
            Observe("open", opened.Message);
            Require(opened.Ok, "Copied real career opened through protected service");
            byte[] original = File.ReadAllBytes(baseline);
            Require(CareerSave.Inspect(original).Ok, "Baseline is an admitted career container");
            Observe("baseline", new { path = baseline, sha256 = SaveSession.Digest(original), bytes = original.Length });
            if (phase == "prepare") await Prepare(career, baseline, backups, original);
            else if (phase == "launch") await Launch(config.RootElement, career);
            else if (phase == "restore") await Restore(career, backups, original);
            else if (phase == "settings") await Settings();
            else if (phase == "workflow")
            {
                _app.Navigate("home");
                if (captureWorkflow) await WorkflowShot("home");
                await Prepare(career, baseline, backups, original);
                await Settings();
                if (captureWorkflow) await WorkflowShot("settings");
                await Restore(career, backups, original);
                if (captureWorkflow) await WorkflowShot("restored");
                Require(File.ReadAllBytes(baseline).AsSpan().SequenceEqual(original), "Preserved workflow baseline remains byte-identical");
                Observe("workflow-limit", "Production Godot controls and byte workflow only; no game launch/load, physical input, audio or visual acceptance is established.");
            }
            exit = 0;
        }
        catch (Exception error) { Observe("failure", error.ToString()); GD.PrintErr(error); }
        finally
        {
            if (_ownerAdmitted)
                File.WriteAllText(Owned(Path.Combine(_owner, phase + "-result-" + DateTime.UtcNow.ToString("yyyyMMddTHHmmssfff") + ".json")), JsonSerializer.Serialize(
                    new { passed = exit == 0, phase, utc = DateTime.UtcNow, observations = _observations }, new JsonSerializerOptions { WriteIndented = true }));
            if (_app is not null)
            {
                for (int frame = 0; frame < 1200 && (_app.Workspace?.Busy == true || _app.Game?.Busy == true); frame++) await Frame();
                await _app.PendingCatchUp;
                await Frame();
                _app.QueueFree(); await Frame();
            }
            GD.Print($"CE_LIVE_DONE {phase} exit={exit}");
            Quit(exit);
        }
    }

    private async Task WorkflowShot(string label)
    {
        string path = Owned(Path.Combine(_owner, "workflow-" + label + ".png"));
        if (File.Exists(path)) throw new IOException("Workflow screenshot already exists; use a fresh owned root.");
        for (int frame = 0; frame < 6; frame++) await Frame();
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image image = Root.GetTexture().GetImage();
        if (image.IsEmpty() || image.SavePng(path) != Error.Ok) throw new IOException("Workflow screenshot could not be captured.");
        Observe("screenshot", new { path, width = image.GetWidth(), height = image.GetHeight(), firstHandInspection = "pending" });
    }

    internal static void AdmitWorkflow(JsonElement config, string launcher, string baseline, string career)
    {
        static void ExactHash(JsonElement config, string key, string path)
        {
            FileMutationSafety.RejectExistingReparseAncestors(path, "Workflow input");
            string expected = config.GetProperty(key).GetString() ?? "";
            if (expected.Length != 64 || expected.Any(c => !char.IsAsciiHexDigitLower(c)) ||
                !File.Exists(path) || (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0 ||
                SaveSession.Digest(File.ReadAllBytes(path)) != expected)
                throw new IOException("Workflow input hash differs: " + key);
        }
        string expectedVersion = config.GetProperty("expectedVersion").GetString() ?? "";
        if (expectedVersion.Length is < 1 or > 128 || expectedVersion.Any(char.IsWhiteSpace))
            throw new IOException("Workflow needs an exact expectedVersion.");
        ExactHash(config, "launcherSha256", launcher);
        ExactHash(config, "baselineSha256", baseline);
        ExactHash(config, "baselineSha256", career);
        if (!CareerSave.Inspect(File.ReadAllBytes(baseline)).Ok)
            throw new IOException("Workflow baseline is not an admitted career container.");
    }

    private async Task Prepare(string career, string baseline, string backups, byte[] original)
    {
        CompanionApp app = _app!;
        Require(File.ReadAllBytes(career).AsSpan().SequenceEqual(original), "Initial copied career equals preserved baseline");
        app.Navigate("edit");
        app.EditCareer.Rows[0].Target.Value = 123456;
        InstallReceipt edited = await app.EditCareer.SaveIntoGameAsync(SaveTarget.Replace, "");
        Observe("edit", edited);
        Require(edited.Ok && edited.BackupFolder is not null, "UI edit succeeded with backup");
        Require(File.ReadAllBytes(Path.Combine(edited.BackupFolder!, Path.GetFileName(career))).AsSpan().SequenceEqual(original),
            "Backup equals exact pre-edit bytes");
        byte[] changed = File.ReadAllBytes(career);
        Require(app.Workspace.Session?.Matches(changed) == true, "UI reopened edited career");
        Require(changed.Where((_, index) => index < CareerSave.KillsOffset || index >= CareerSave.KillsOffset + 3)
            .SequenceEqual(original.Where((_, index) => index < CareerSave.KillsOffset || index >= CareerSave.KillsOffset + 3)),
            "Every unselected and unknown byte preserved");
        Observe("edited", new { path = career, sha256 = SaveSession.Digest(changed), kills = 123456 });

        app.EditCareer.Rows[1].Target.Value = 234567;
        InstallReceipt unicode = await app.EditCareer.SaveIntoGameAsync(SaveTarget.NewCareer, "CE Élan");
        Observe("unicode", unicode);
        Require(unicode.Ok && File.Exists(Path.Combine(Path.GetDirectoryName(career)!, "CE Élan.bes")),
            "Unicode named career added through UI and verified");

        GameFolder folder = app.Game.Folder!;
        InstallReceipt stale = GameInstaller.Install(new ProtectedSaveFiles(), folder, Path.GetFileName(career), original,
            backups, GameProcess.IsRunning, DateTime.Now, expectedSha256: SaveSession.Digest(original));
        Observe("changed-source", stale);
        Require(!stale.Ok && File.ReadAllBytes(career).AsSpan().SequenceEqual(changed), "Stale snapshot replacement refused without changing edited career");

        string failedBackup = Owned(Path.Combine(_owner, "unwritable-backups"));
        Directory.CreateDirectory(failedBackup);
        if (OperatingSystem.IsLinux())
        {
            UnixFileMode previous = File.GetUnixFileMode(failedBackup);
            try
            {
                File.SetUnixFileMode(failedBackup, UnixFileMode.UserRead | UnixFileMode.UserExecute);
                InstallReceipt failed = GameInstaller.Install(new ProtectedSaveFiles(), folder, Path.GetFileName(career), original,
                    failedBackup, GameProcess.IsRunning, DateTime.Now, expectedSha256: SaveSession.Digest(changed));
                Observe("actual-backup-permission-failure", failed);
                Require(!failed.Ok && File.ReadAllBytes(career).AsSpan().SequenceEqual(changed), "Actual backup permission failure leaves career unchanged");
            }
            finally { File.SetUnixFileMode(failedBackup, previous); }
        }
        Require(File.ReadAllBytes(baseline).AsSpan().SequenceEqual(original), "Preserved baseline remains unchanged");
    }

    private async Task Launch(JsonElement config, string career)
    {
        if (Environment.GetEnvironmentVariable("SDL_VIDEO_DRIVER") != "offscreen" ||
            Environment.GetEnvironmentVariable("BEA_PORT_REQUIRE_OFFSCREEN") != "1" ||
            Environment.GetEnvironmentVariable("SDL_AUDIO_DRIVER") != "dummy" ||
            Environment.GetEnvironmentVariable("BEA_PORT_REQUIRE_DUMMY_AUDIO") != "1")
            throw new IOException("CE launch requires explicit offscreen video and dummy-audio guards.");
        Environment.SetEnvironmentVariable("DISPLAY", null);
        Environment.SetEnvironmentVariable("WAYLAND_DISPLAY", null);
        if (config.TryGetProperty("useIniGameDirectory", out JsonElement ini) && ini.GetBoolean())
            Environment.SetEnvironmentVariable("BEA_GAME_DIR", null);
        foreach (string key in new[] { "BEA_PORT_TAPE", "BEA_PORT_PROBES" })
            if (config.TryGetProperty(key, out JsonElement value))
                Environment.SetEnvironmentVariable(key, Owned(value.GetString()!));
        if (config.TryGetProperty("BEA_PORT_SHOT", out JsonElement shot))
        {
            string text = shot.GetString()!;
            int colon = text.IndexOf(':');
            if (colon < 1 || !int.TryParse(text[..colon], out int frame) || frame < 1 || frame > 10000)
                throw new IOException("Screenshot needs a bounded frame and an owned output path.");
            Environment.SetEnvironmentVariable("BEA_PORT_SHOT", frame + ":" + Owned(text[(colon + 1)..]));
        }
        foreach (string key in new[] { "BEA_PORT_REPLAY_MAX", "BEA_PORT_PROBE_EVERY", "BEA_PORT_CLOCK", "BEA_PORT_REPLAY_SLEEP_US" })
            if (config.TryGetProperty(key, out JsonElement value)) Environment.SetEnvironmentVariable(key, value.GetString());
        if (Environment.GetEnvironmentVariable("BEA_PORT_REPLAY_MAX") is not string maximum ||
            !int.TryParse(maximum, out int limit) || limit < 1 || limit > 10000)
            throw new IOException("An explicit bounded replay maximum is required.");
        byte[] before = File.ReadAllBytes(career);
        string expectedCareer = Owned(config.GetProperty("expectedLoadedCareer").GetString()!);
        byte[] expected = File.ReadAllBytes(expectedCareer);
        string options = Path.Combine(_app!.Game.Ce!.UserFolder, "defaultoptions.bea");
        Require(File.Exists(options) && !File.ReadAllBytes(options).AsSpan().SequenceEqual(expected),
            "Before launch, options differ from the career whose load must be proven");
        Observe("expected-loaded-career", new { path = expectedCareer, sha256 = SaveSession.Digest(expected) });
        Process? launcher = null;
        DateTime launcherStarted = default;
        Dictionary<int, (DateTime Started, string Image)> gameProcesses = [];
        bool FindOwnedGame()
        {
            string image = Path.Combine(_app.Game.Ce!.Folder, OperatingSystem.IsWindows() ? OnslaughtCe.WindowsGame : OnslaughtCe.LinuxGame);
            foreach (string entry in GameProcess.Running())
            {
                if (!int.TryParse(entry.Split(':')[0], out int pid)) continue;
                try
                {
                    using Process process = Process.GetProcessById(pid);
                    if (process.MainModule?.FileName != image || process.StartTime.ToUniversalTime() < launcherStarted) continue;
                    if (gameProcesses.TryAdd(pid, (process.StartTime.ToUniversalTime(), image)))
                        Observe("owned-game-process", new { pid, image, started = gameProcesses[pid].Started });
                }
                catch (Exception error) when (error is ArgumentException or InvalidOperationException or System.ComponentModel.Win32Exception) { }
            }
            return gameProcesses.Count > 0;
        }
        try
        {
            Outcome<string> started = _app!.Game.Ce!.Launch(start =>
            {
                if (config.TryGetProperty("gameArguments", out JsonElement args))
                {
                    start.ArgumentList.Add("--");
                    foreach (JsonElement arg in args.EnumerateArray()) start.ArgumentList.Add(arg.GetString()!);
                    Observe("diagnostic-game-arguments", start.ArgumentList);
                }
                launcher = Process.Start(start);
                if (launcher is not null) launcherStarted = launcher.StartTime.ToUniversalTime();
                return launcher is not null;
            });
            Require(started.Ok && launcher is not null, "Actual production CE launcher started");
            Observe("launcher", new { pid = launcher!.Id, path = _app.Game.Ce!.LauncherPath });
            await Until(FindOwnedGame, 20, "Actual owned CE game process detected");
            Observe("running", GameProcess.Running());
            InstallReceipt refused = GameInstaller.Install(new ProtectedSaveFiles(), _app.Game.Folder!, Path.GetFileName(career),
                before, Owned(Path.Combine(_owner, "backups")), GameProcess.IsRunning, DateTime.Now,
                expectedSha256: SaveSession.Digest(before));
            Observe("actual-running-refusal", refused);
            Require(IsRunningRefusal(refused) && File.ReadAllBytes(career).AsSpan().SequenceEqual(before), "Write refused while actual CE launcher/game runs");
            await _app.Settings.CePanel.LoadAsync();
            byte[] settingsBefore = File.ReadAllBytes(_app.Game.Ce.SettingsPath);
            _app.Settings.CePanel.RecordSessions.ButtonPressed = !_app.Settings.CePanel.RecordSessions.ButtonPressed;
            InstallReceipt settingsRefused = await _app.Settings.CePanel.SaveAsync();
            Observe("actual-running-settings-refusal", settingsRefused);
            Require(IsRunningRefusal(settingsRefused) && File.ReadAllBytes(_app.Game.Ce.SettingsPath).AsSpan().SequenceEqual(settingsBefore),
                "Settings write refused while actual CE runs");
            await _app.Settings.CePanel.LoadAsync();
            await Until(() => launcher.HasExited, 150, "Bounded CE run exited normally");
            Require(launcher.ExitCode == 0, "CE launcher exit is zero");
            await Until(() => !GameProcess.IsRunning(), 5, "Game process no longer running");
            Require(File.ReadAllBytes(expectedCareer).AsSpan().SequenceEqual(expected), "Loaded career file remains unchanged");
            Require(File.ReadAllBytes(options).AsSpan().SequenceEqual(expected),
                "CE successful-load output equals the exact edited career, including unknown bytes");
            Observe("options-after-run", new { sha256 = SaveSession.Digest(File.ReadAllBytes(options)),
                equalsExpectedCareer = true });
        }
        finally
        {
            if (launcher is not null)
            {
                try
                {
                    // A launcher can exit before its game. Discover and clean recorded game identities
                    // independently of parent liveness; no process-tree signal is ever sent.
                    FindOwnedGame();
                    await CleanupOwned(launcher, launcherStarted, OperatingSystem.IsWindows() ? _app.Game.Ce!.LauncherPath :
                        Path.Combine(_app.Game.Ce!.Folder, OnslaughtCe.LinuxLauncher), gameProcesses, Observe);
                }
                finally { launcher.Dispose(); }
            }
        }
    }

    private async Task Settings()
    {
        CompanionApp app = _app!;
        string path = app.Game.Ce!.SettingsPath;
        app.Navigate("settings");
        await app.Settings.CePanel.LoadAsync();
        byte[] before = File.ReadAllBytes(path);
        app.Settings.CePanel.UpdateCheck.ButtonPressed = true;
        app.Settings.CePanel.RecordSessions.ButtonPressed = true;
        InstallReceipt enabled = await app.Settings.CePanel.SaveAsync();
        Observe("settings-enabled", enabled);
        Require(enabled.Ok && enabled.BackupFolder is not null &&
            File.ReadAllBytes(Path.Combine(enabled.BackupFolder, "ce.ini")).AsSpan().SequenceEqual(before),
            "Actual ce.ini UI save has an exact verified backup");
        CeSettings saved = CeSettings.Read(app.Game.Ce.UserFolder).Value ?? throw new IOException("Cannot read saved settings.");
        Require(saved.UpdateCheck && saved.RecordSessions && File.ReadAllText(path).Contains("future_kept=acceptance"),
            "Documented keys changed and unknown settings line remained intact");
        File.AppendAllText(path, "external_added=kept\n"); // Simulates a second writer on this isolated profile only.
        byte[] external = File.ReadAllBytes(path);
        app.Settings.CePanel.RecordSessions.ButtonPressed = false;
        InstallReceipt stale = await app.Settings.CePanel.SaveAsync();
        Observe("settings-changed-source", stale);
        Require(!stale.Ok && File.ReadAllBytes(path).AsSpan().SequenceEqual(external),
            "Changed ce.ini snapshot refused without overwriting the newer file");
        await app.Settings.CePanel.LoadAsync();
        app.Settings.CePanel.UpdateCheck.ButtonPressed = false;
        app.Settings.CePanel.RecordSessions.ButtonPressed = false;
        InstallReceipt disabled = await app.Settings.CePanel.SaveAsync();
        Observe("settings-disabled", disabled);
        saved = CeSettings.Read(app.Game.Ce.UserFolder).Value ?? throw new IOException("Cannot reopen settings.");
        Require(disabled.Ok && !saved.UpdateCheck && !saved.RecordSessions && File.ReadAllText(path).Contains("external_added=kept") &&
            File.ReadAllText(path).Contains("future_kept=acceptance"), "UI reopened disabled test settings and preserved both unknown lines");
    }

    internal static bool IsRunningRefusal(InstallReceipt receipt) =>
        !receipt.Ok && receipt.Message == GameInstaller.RunningMessage && !receipt.MayHaveChanged && receipt.BackupFolder is null;

    internal static async Task CleanupOwned(Process launcher, DateTime launcherStarted, string launcherImage,
        IReadOnlyDictionary<int, (DateTime Started, string Image)> gameProcesses, Action<string, object> observe)
    {
        foreach ((int pid, (DateTime started, string image)) in gameProcesses)
            await StopOwned(pid, started, image, observe);
        if (!launcher.HasExited) await StopOwned(launcher.Id, launcherStarted, launcherImage, observe);
    }

    private static async Task StopOwned(int pid, DateTime started, string image, Action<string, object> observe)
    {
        try
        {
            using Process process = Process.GetProcessById(pid);
            if (process.HasExited) return;
            if (process.StartTime.ToUniversalTime() != started || process.MainModule?.FileName != image)
            {
                observe("cleanup-refused", new { pid, expectedImage = image, reason = "Process identity changed; no signal sent." });
                return;
            }
            observe("cleanup-owned-pid", new { pid, image, started });
            process.Kill();
            await process.WaitForExitAsync().WaitAsync(TimeSpan.FromSeconds(5));
        }
        catch (ArgumentException) { } // It exited between checks.
    }

    private async Task Restore(string career, string backups, byte[] original)
    {
        CompanionApp app = _app!;
        byte[] before = File.ReadAllBytes(career);
        BackupSet set = Backups.List(backups, app.Game.Folder!).First(candidate => candidate.Files.Any(file =>
            file.Name == Path.GetFileName(career) && file.Sha256 == SaveSession.Digest(original)));
        app.Navigate("backups");
        app.Backups.AskToRestore(set, set.Files.Single(file => file.Name == Path.GetFileName(career)));
        InstallReceipt restored = await app.Backups.ConfirmAsync();
        Observe("restore", restored);
        Require(restored.Ok && app.Workspace.Session?.Matches(original) == true && File.ReadAllBytes(career).AsSpan().SequenceEqual(original),
            "Backup UI restored and reopened exact original bytes");
        Require(restored.BackupFolder is not null && File.ReadAllBytes(Path.Combine(restored.BackupFolder, Path.GetFileName(career)))
            .AsSpan().SequenceEqual(before), "Restore preserved the displaced edited career in its own verified backup");
    }

    private string Owned(string path)
    {
        string full = Path.GetFullPath(path);
        if (!full.StartsWith(_owner + Path.DirectorySeparatorChar, StringComparison.Ordinal))
            throw new IOException("Acceptance writable paths must be below the prepared isolated owner.");
        return full;
    }

    private void Observe(string label, object value)
    {
        _observations.Add(new { label, value });
        GD.Print("CE_LIVE " + label + " " + JsonSerializer.Serialize(value));
    }

    private void Require(bool condition, string label)
    {
        Observe(condition ? "pass" : "FAIL", label);
        if (!condition) throw new IOException(label);
    }

    private async Task Until(Func<bool> predicate, int seconds, string label)
    {
        Stopwatch time = Stopwatch.StartNew();
        while (!predicate() && time.Elapsed.TotalSeconds < seconds) await Frame();
        Require(predicate(), label);
    }

    private async Task Frame() => await ToSignal(this, SignalName.ProcessFrame);
}
