// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>CE UI routes on owned fixture copies; feed access is injected and no launcher or game executes.</summary>
public partial class CePanelTests : SceneTree
{
    public override void _Initialize() => _ = RunEntryAsync();

    private async Task RunEntryAsync()
    {
        int exit = 1;
        try
        {
            string Argument(string key) => OS.GetCmdlineUserArgs().Single(value => value.StartsWith(key, StringComparison.Ordinal))[key.Length..];
            string fixture = Argument("--fixture="), output = Argument("--output-dir=");
            byte[] original = File.ReadAllBytes(fixture);
            Checks check = new();
            await Frame(this);
            await RunAsync(this, original, output, check);
            check.That(File.ReadAllBytes(fixture).AsSpan().SequenceEqual(original), "The owned input fixture remains unchanged.");
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"CE_PANEL_TESTS: {check.Failures.Count} failures in {check.Count} checks.");
            exit = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr(error); }
        finally { Quit(exit); }
    }

    internal static async Task RunAsync(SceneTree tree, byte[] original, string output, Checks check)
    {
        check.Suite("CE panels");
        string root = Path.Combine(output, "ce-panels");
        string user = Path.Combine(root, "ce-user");
        Directory.CreateDirectory(Path.Combine(user, "savegames"));
        File.WriteAllBytes(Path.Combine(user, "savegames", "CE Pilot.bes"), original);
        string ini = Path.Combine(user, "ce.ini");
        string baseline = "# retained comment\ngamedir=/original/data\nunknown=leave-me\nupdate_check=1\nrecord_sessions=0\n";
        File.WriteAllText(ini, baseline);
        string settingsPath = Path.Combine(root, "settings.json");
        new SettingsStore(settingsPath).Save(new CompanionSettings { Target = GameTarget.OnslaughtCe, AutoBackup = false });
        bool running = false, stopAfterBackup = false;
        string backups = Path.Combine(root, "backups");
        int priorSettingsBackups = 0;
        CompanionEnvironment environment = new([], settingsPath, GameRunning: () => running ||
            (stopAfterBackup && Directory.GetDirectories(backups, "onslaught-ce-settings-*").Length > priorSettingsBackups),
            DefaultBackupFolder: backups, CeUserFolder: user);
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false, environment);
        tree.Root.AddChild(app);
        try
        {
            for (int i = 0; i < 600 && (app.Game.Busy || app.Workspace.Session is null || app.Workspace.Busy); i++) await Frame(tree);
            check.That(app.Game.Target == GameTarget.OnslaughtCe && app.Workspace.Session?.Path == Path.Combine(user, "savegames", "CE Pilot.bes"),
                "CE target opens its own career without an original install or launcher");

            int requests = 0;
            CeHomePanel home = new(app.Services, (_, _) =>
            {
                requests++;
                return Task.FromResult(new CeUpdateState(true, "1.2.3", CeUpdateAvailability.Unknown,
                    "Signed release: CE 1.2.3. Your installed version could not be compared."));
            });
            app.AddChild(home.Root);
            await Frame(tree);
            home.Refresh();
            check.That(requests == 0 && home.Root.Visible, "showing the CE panel never contacts the feed automatically");
            await home.CheckUpdatesAsync();
            check.That(requests == 1 && home.UpdateText.Contains("Signed release: CE 1.2.3") && File.ReadAllText(ini) == baseline,
                "explicit update check displays authenticated state and never changes CE settings");

            CeSettingsPanel panel = new(app.Services);
            app.AddChild(panel.Root);
            await panel.LoadAsync();
            panel.Refresh();
            check.That(panel.SettingsPath == ini && panel.UpdateCheck.ButtonPressed && !panel.RecordSessions.ButtonPressed && !panel.HasChanges,
                "CE settings panel shows the actual launcher switches");
            panel.RecordSessions.ButtonPressed = true;
            panel.Refresh();
            check.That(panel.HasChanges && panel.ChangeCount == 1 && !panel.Save.Disabled,
                "refresh preserves an unsaved CE setting and offers the protected save");
            running = true;
            panel.Refresh();
            check.That(panel.Save.Disabled, "running-game state disables CE settings save");
            InstallReceipt refused = await panel.SaveAsync();
            check.That(!refused.Ok && File.ReadAllText(ini) == baseline && panel.HasChanges,
                "even a direct save request while running is refused without losing edits");
            running = false;
            panel.Refresh();
            panel.AskToSave();
            check.That(panel.Confirm.Visible && panel.Confirm.DialogText.Contains(ini) && panel.Confirm.DialogText.Contains("backed up") &&
                panel.Confirm.DialogText.Contains("before starting either") && panel.Confirm.DialogText.Contains("again before putting the changed file in place"),
                "CE settings confirmation identifies the target and recovery, checks and safe timing");
            panel.Confirm.Hide();
            InstallReceipt saved = await panel.SaveAsync();
            string changed = File.ReadAllText(ini);
            check.That(saved.Ok && saved.BackupFolder is not null && changed.Contains("record_sessions=1") &&
                changed.Contains("unknown=leave-me") && changed.Contains("# retained comment") && !panel.HasChanges,
                "CE UI save reopens the verified result, preserves unknown text and reports its backup");
            check.That(saved.BackupFolder is string savedFolder && Occurrences(panel.ResultText, savedFolder) == 1 &&
                panel.ResultText.Contains("saved and verified", StringComparison.Ordinal),
                "saved CE settings show verified status and the complete backup location exactly once");
            check.That(app.Status.Kind == StatusKind.Success && app.Status.Label.Text.Contains("saved and verified", StringComparison.Ordinal) &&
                saved.BackupFolder is string footerFolder && !app.Status.Label.Text.Contains(footerFolder, StringComparison.Ordinal),
                "the success footer keeps verified status while the settings panel owns the backup location");

            priorSettingsBackups = Directory.GetDirectories(backups, "onslaught-ce-settings-*").Length;
            stopAfterBackup = true;
            panel.RecordSessions.ButtonPressed = false;
            InstallReceipt afterBackup = await panel.SaveAsync();
            stopAfterBackup = false;
            check.That(!afterBackup.Ok && !afterBackup.MayHaveChanged && afterBackup.BackupFolder is string refusedFolder &&
                File.ReadAllText(Path.Combine(refusedFolder, "ce.ini")) == changed && File.ReadAllText(ini) == changed,
                "a real game-start refusal after backup preserves both settings and their recovery copy");
            check.That(afterBackup.BackupFolder is string recoveryFolder && Occurrences(panel.ResultText, recoveryFolder) == 1 &&
                panel.ResultText.Contains(afterBackup.Message, StringComparison.Ordinal) &&
                app.Status.Kind == StatusKind.Failure && app.Status.Label.TooltipText == afterBackup.Message,
                "a failed CE save keeps its complete failure reason and full recovery location");
            panel.UpdateCheck.ButtonPressed = false;
            await panel.LoadAsync();
            check.That(!panel.HasChanges && panel.UpdateCheck.ButtonPressed, "undo reloads the current CE settings without writing");
            panel.ResetTarget();
            check.That(panel.SettingsPath.Length == 0 && !panel.HasChanges && panel.Save.Disabled,
                "changing target clears the previous CE snapshot and disables its save");
        }
        finally
        {
            for (int frame = 0; frame < 600 && (app.Game.Busy || app.Workspace.Busy); frame++) await Frame(tree);
            await app.PendingCatchUp;
            app.QueueFree();
            await Frame(tree);
        }
    }

    private static async Task Frame(SceneTree tree) => await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);

    private static int Occurrences(string text, string value) => text.Split(value, StringSplitOptions.None).Length - 1;
}
