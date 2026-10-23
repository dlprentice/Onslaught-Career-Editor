// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>CE UI routes on owned fixture copies; feed access is injected and no launcher or game executes.</summary>
internal static class CePanelTests
{
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
        bool running = false;
        CompanionEnvironment environment = new([], settingsPath, GameRunning: () => running,
            DefaultBackupFolder: Path.Combine(root, "backups"), CeUserFolder: user);
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
            check.That(panel.Confirm.Visible && panel.Confirm.DialogText.Contains(ini) && panel.Confirm.DialogText.Contains("backed up"),
                "CE settings confirmation identifies the target and recovery step");
            panel.Confirm.Hide();
            InstallReceipt saved = await panel.SaveAsync();
            string changed = File.ReadAllText(ini);
            check.That(saved.Ok && saved.BackupFolder is not null && changed.Contains("record_sessions=1") &&
                changed.Contains("unknown=leave-me") && changed.Contains("# retained comment") && !panel.HasChanges,
                "CE UI save reopens the verified result, preserves unknown text and reports its backup");
            panel.UpdateCheck.ButtonPressed = false;
            await panel.LoadAsync();
            check.That(!panel.HasChanges && panel.UpdateCheck.ButtonPressed, "undo reloads the current CE settings without writing");
            panel.ResetTarget();
            check.That(panel.SettingsPath.Length == 0 && !panel.HasChanges && panel.Save.Disabled,
                "changing target clears the previous CE snapshot and disables its save");
        }
        finally
        {
            app.QueueFree();
            await Frame(tree);
        }
    }

    private static async Task Frame(SceneTree tree) => await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
}
