// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

internal static class CeTargetTests
{
    internal static async Task RunAsync(SceneTree tree, byte[] original, string output, Checks check)
    {
        check.Suite("CE target separation");
        string root = Path.Combine(output, "ce-target");
        FakeInstall retail = FakeInstall.Create(Path.Combine(root, "retail"), original);
        string user = Path.Combine(root, "ce-user"), backups = Path.Combine(root, "backups");
        Directory.CreateDirectory(Path.Combine(user, "savegames"));
        Directory.CreateDirectory(backups);
        string career = Path.Combine(user, "savegames", "CE Pilot.bes");
        File.WriteAllBytes(career, original);
        File.WriteAllText(Path.Combine(user, "ce.ini"), "gamedir=" + retail.Game + "\nupdate_check=1\nrecord_sessions=0\nfuture=keep\n");
        SettingsStore settings = new(Path.Combine(root, "settings.json"));
        settings.Save(new CompanionSettings { GameFolder = retail.Game, Target = GameTarget.OnslaughtCe, AutoBackup = false });
        SettingsStore badBackupSettings = new(Path.Combine(root, "bad-backup-settings.json"));
        string forbidden = Path.Combine(retail.Game, "must-not-create");
        badBackupSettings.Save(new CompanionSettings { BackupFolder = forbidden });
        check.That(new BackupLocation(badBackupSettings, forbidden).Ensure() is null && !Directory.Exists(forbidden),
            "Choosing a backup root inside the original game creates nothing there");
        bool running = false;
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false,
            new CompanionEnvironment([retail.SteamRoot], settings.FilePath, GameRunning: () => running,
                OpenUrl: _ => throw new InvalidOperationException("Tests must not launch Steam"), DefaultBackupFolder: backups,
                CeUserFolder: user, OldCopiesFolder: Path.Combine(root, "no-old-copies")));
        tree.Root.AddChild(app);
        async Task Frame() => await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        try
        {
            for (int n = 0; n < 600 && (app.Game.Busy || app.Workspace.Session is null); n++) await Frame();
            check.That(app.Game.Target == GameTarget.OnslaughtCe && app.Game.Folder?.Root == user &&
                app.Game.Folder?.AssetRoot == retail.Game && app.Workspace.Session?.Path == career,
                "CE selection opens its own career while assets stay in the original installation");
            check.That(!app.Home.Play.Visible && app.Home.CePanel.Root.Visible &&
                app.Home.CePanel.FolderGuidanceText.Contains("bind mount") && app.Home.CePanel.FolderGuidanceText.Contains("not every folder alias can be detected"),
                "CE Home warns about custom folder aliases and cannot start the original game by mistake");
            app.Navigate("edit");
            app.EditCareer.Rows[0].Target.Value = 123456;
            app.EditCareer.AskToSave();
            check.That(app.EditCareer.SaveChoice.NoteText.Contains("supported careers") &&
                app.EditCareer.SaveChoice.NoteText.Contains("CE settings are backed up separately when edited") &&
                !app.EditCareer.SaveChoice.NoteText.Contains("original-game settings"),
                "CE career save guidance separates career backups from CE settings backups");
            app.EditCareer.SaveChoice.Dialog.Hide();
            await app.SelectTargetAsync(GameTarget.Original);
            check.That(app.Game.Target == GameTarget.OnslaughtCe, "Unsaved career edits refuse a target switch");
            running = true;
            InstallReceipt refused = await app.EditCareer.SaveIntoGameAsync(SaveTarget.Replace, "");
            check.That(!refused.Ok && File.ReadAllBytes(career).AsSpan().SequenceEqual(original), "Running CE blocks career changes");
            running = false;
            InstallReceipt saved = await app.EditCareer.SaveIntoGameAsync(SaveTarget.Replace, "");
            check.That(saved.Ok && saved.BackupFolder is not null &&
                File.ReadAllBytes(Path.Combine(saved.BackupFolder!, "CE Pilot.bes")).AsSpan().SequenceEqual(original),
                "CE career replacement has a verified pre-edit backup");
            check.That(File.ReadAllBytes(retail.Career).AsSpan().SequenceEqual(original) && File.ReadAllBytes(retail.Options).AsSpan().SequenceEqual(original),
                "CE career writes leave original careers and default options unchanged");
            byte[] changed = File.ReadAllBytes(career);
            check.That(app.Workspace.Session?.Matches(changed) == true && app.Workspace.Session.Path == career,
                "CE career save reopens the verified result as the current career");
            app.Navigate("cheats");
            app.Cheats.BaseName.Text = "CE Review";
            app.Cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "CE Review");
            app.Cheats.Choices[0].ButtonPressed = true;
            app.Cheats.AskToAdd();
            check.That(app.Cheats.Confirm.Visible && app.Cheats.Confirm.DialogText.Contains("supported careers") &&
                app.Cheats.Confirm.DialogText.Contains("CE settings are backed up separately when edited") &&
                !app.Cheats.Confirm.DialogText.Contains("original-game settings"),
                "CE cheat-copy confirmation describes the separate settings backup accurately");
            app.Cheats.Confirm.Hide();
            check.That(changed.Length == original.Length && changed.Where((value, index) => index < CareerSave.KillsOffset || index >= CareerSave.KillsOffset + 3).SequenceEqual(
                    original.Where((value, index) => index < CareerSave.KillsOffset || index >= CareerSave.KillsOffset + 3)),
                "Unselected CE career bytes are preserved");
            GameFolder ce = app.Game.Folder!;
            InstallReceipt options = GameInstaller.Install(new ProtectedSaveFiles(), ce, "defaultoptions.bea", original, backups, () => false, DateTime.Now);
            check.That(!options.Ok && !File.Exists(Path.Combine(user, "defaultoptions.bea")), "CE target never exposes retail default-options writes");
            string snapshot = SaveSession.Digest(changed);
            changed[^1] ^= 1;
            File.WriteAllBytes(career, changed);
            InstallReceipt stale = GameInstaller.Install(new ProtectedSaveFiles(), ce, "CE Pilot.bes", original, backups, () => false,
                DateTime.Now, expectedSha256: snapshot);
            check.That(!stale.Ok && File.ReadAllBytes(career).AsSpan().SequenceEqual(changed), "A newer CE save cannot be overwritten from stale edits");
            BackupSet firstBackup = Backups.List(backups, ce).Single(set => set.Folder == saved.BackupFolder);
            app.Backups.AskToRestore(firstBackup, firstBackup.Files.Single(file => file.Name == "CE Pilot.bes"));
            InstallReceipt restored = await app.Backups.ConfirmAsync();
            check.That(restored.Ok && File.ReadAllBytes(career).AsSpan().SequenceEqual(original) &&
                app.Workspace.Session?.Matches(original) == true && restored.BackupFolder is string beforeRestore &&
                File.ReadAllBytes(Path.Combine(beforeRestore, "CE Pilot.bes")).AsSpan().SequenceEqual(changed),
                "Restoring a CE backup through the UI first preserves the newer file, then reopens the verified restored career");
            byte[] unsupported = original.ToArray(); unsupported[0] = 0xff;
            InstallReceipt invalid = GameInstaller.Install(new ProtectedSaveFiles(), ce, "Invalid.bes", unsupported, backups,
                () => false, DateTime.Now);
            check.That(!invalid.Ok && !File.Exists(Path.Combine(user, "savegames", "Invalid.bes")),
                "CE rejects an unsupported save version even when its length is correct");
            app.Navigate("settings");
            await app.Settings.CePanel.LoadAsync();
            File.AppendAllText(Path.Combine(user, "ce.ini"), "external=arrived\n");
            await app.CatchUpAsync(force: false, backUp: false);
            app.Settings.CePanel.UpdateCheck.ButtonPressed = false;
            await app.SelectTargetAsync(GameTarget.Original);
            check.That(app.Game.Target == GameTarget.OnslaughtCe, "Unsaved launcher settings refuse target switching");
            await app.Settings.CePanel.SaveAsync();
            check.That(File.ReadAllText(Path.Combine(user, "ce.ini")).Contains("update_check=0") &&
                File.ReadAllText(Path.Combine(user, "ce.ini")).Contains("future=keep"), "CE settings UI saves the documented key and preserves unknown entries");
            bool crossed = false;
            app.Game.Changed += () => crossed |= app.Game.Folder is GameFolder visible && visible.Target != app.Game.Target;
            await app.SelectTargetAsync(GameTarget.Original);
            check.That(!crossed, "Target switching never exposes the previous game's folder under the new selection");
            for (int n = 0; n < 600 && (app.Game.Busy || app.Workspace.Session is null); n++) await Frame();
            check.That(app.Game.Folder?.Root == retail.Game && app.Workspace.Session?.Path == retail.Career,
                "Switching back opens only the original target's career");
            check.That(!Backups.List(backups, app.Game.Folder!).Any(), "CE backups are not shown as original-game backups");
        }
        finally { app.QueueFree(); await Frame(); }
    }
}
