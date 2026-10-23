// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

internal static class CeOverlayTests
{
    internal static async Task RunAsync(SceneTree tree, byte[] original, string output, Checks check)
    {
        check.Suite("CE original-career overlay");
        string root = Path.Combine(output, "ce-overlay");
        FakeInstall retail = FakeInstall.Create(Path.Combine(root, "retail"), original);
        FakeInstall other = FakeInstall.Create(Path.Combine(root, "other"), original);
        string user = Path.Combine(root, "ce-user"), saves = Path.Combine(user, "SaveGames"), backups = Path.Combine(root, "backups");
        Directory.CreateDirectory(saves); Directory.CreateDirectory(backups);
        string own = Path.Combine(saves, "CAREER ONE.BES");
        File.WriteAllBytes(own, original);
        string inherited = Path.Combine(retail.Game, "savegames", "Original only.BES");
        File.WriteAllBytes(inherited, original);
        File.WriteAllText(Path.Combine(user, "ce.ini"), "gamedir=" + retail.Game + "\nupdate_check=1\nrecord_sessions=0\n");
        GameFolder folder = GameFolder.InspectCe(user, other.Game, retail.Game);
        check.That(folder.Careers.Count == 2 && folder.Careers.Single(f => f.Name == "CAREER ONE.BES").Path == own &&
            !folder.Careers.Single(f => f.Path == own).FromOriginalInstall && folder.Careers.Single(f => f.Path == inherited).FromOriginalInstall,
            "CE combines careers case-insensitively, with user copies first and original sources marked");
        check.That(folder.SavegamesPath == saves && GameInstaller.Target(folder, "career one.bes") == own,
            "CE resolves the existing case-insensitive save directory and writable filename");
        ProtectedSaveFiles files = new();
        BackupReceipt backed = Backups.Create(files, folder, backups, DateTime.Now);
        check.That(backed.Set is { Target: GameTarget.OnslaughtCe } set && set.Files.Count == 2 &&
            set.Files.Single(f => f.Original == inherited).Sha256 == OnslaughtToolkit.Companion.Careers.SaveSession.Digest(original) &&
            File.ReadAllBytes(Path.Combine(set.Folder, "Original only.BES")).AsSpan().SequenceEqual(original),
            "CE backups record their game and preserve the inherited original career too");
        check.That(!Backups.ChangedSinceLatest(folder, backups), "The combined CE list compares correctly with its last backup");
        BackupSet manifest = Backups.List(backups, folder).Single();
        check.That(!Backups.SameGame(manifest with { Target = GameTarget.Original }, folder) &&
            (manifest with { Target = null }).GameName.Contains("not recorded"), "Backup identity distinguishes games and labels legacy identity unknown");

        SettingsStore settings = new(Path.Combine(root, "settings.json"));
        settings.Save(new CompanionSettings { GameFolder = other.Game, Target = GameTarget.OnslaughtCe, AutoBackup = false });
        GameLibrary library = new([], settings, user, _ => null, GameFolder.LooksLikeGame);
        await library.DetectAsync();
        check.That(library.Folder?.CeOriginalRoot == retail.Game && library.Folder.Careers.Any(f => f.Path == inherited),
            "ce.ini's original game folder supplies CE careers instead of the unrelated media choice");
        GameLibrary productionAdmission = new([], settings, user, _ => null);
        await productionAdmission.DetectAsync();
        check.That(productionAdmission.Folder?.CeOriginalRoot == "" && productionAdmission.Folder.Careers.Count == 1,
            "A marker BEA.exe and data folder alone are not admitted as CE's actual original-data source");
        GameLibrary overrideLibrary = new([], settings, user, name => name == "BEA_GAME_DIR" ? other.Game : null, GameFolder.LooksLikeGame);
        await overrideLibrary.DetectAsync();
        check.That(overrideLibrary.Folder?.CeOriginalRoot == other.Game && !overrideLibrary.Folder.Careers.Any(f => f.Path == inherited),
            "An explicit original-game environment choice takes precedence over ce.ini");
        string blocked = Path.Combine(saves, "ORIGINAL ONLY.bes");
        File.WriteAllText(blocked, "unsupported owned fixture");
        check.That(library.FilesChanged(), "A new CE shadow is detected even when the original file did not change");
        await library.RescanAsync();
        check.That(library.Folder!.Careers.Single(f => f.Name.Equals("original only.bes", StringComparison.OrdinalIgnoreCase)) is
            { Supported: false, FromOriginalInstall: false }, "An unsupported user shadow never silently falls back to another career");
        File.Delete(blocked); // This test's own marker only.
        await library.RescanAsync();

        CompanionApp app = new(files, false, new CompanionEnvironment([], settings.FilePath, GameRunning: () => false,
            OpenUrl: _ => throw new InvalidOperationException("No launcher in this test"), DefaultBackupFolder: backups,
            CeUserFolder: user, OldCopiesFolder: Path.Combine(root, "no-old-copies"), CeInstallSupported: GameFolder.LooksLikeGame));
        tree.Root.AddChild(app);
        async Task Frame() => await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        try
        {
            for (int n = 0; n < 600 && (app.Game.Busy || app.Workspace.Busy || app.Workspace.Session is null); n++) await Frame();
            await app.OpenCareerAsync(inherited);
            app.Navigate("edit"); app.EditCareer.Rows[0].Target.Value = 123456;
            app.EditCareer.AskToSave();
            check.That(!app.EditCareer.SaveChoice.Offers(SaveTarget.Replace) && app.EditCareer.SaveChoice.Offers(SaveTarget.NewCareer),
                "Original-install career offers a new CE copy, never replacement of the original");
            app.EditCareer.SaveChoice.Dialog.Hide();
            InstallReceipt refused = await app.EditCareer.SaveIntoGameAsync(SaveTarget.Replace, "");
            check.That(!refused.Ok && File.ReadAllBytes(inherited).AsSpan().SequenceEqual(original),
                "A direct replacement request also leaves the inherited original untouched");
            InstallReceipt copied = await app.EditCareer.SaveIntoGameAsync(SaveTarget.NewCareer, "My CE copy");
            check.That(copied.Ok && copied.Target == Path.Combine(saves, "My CE copy.bes") &&
                File.ReadAllBytes(inherited).AsSpan().SequenceEqual(original) &&
                File.ReadAllBytes(Path.Combine(copied.BackupFolder!, "Original only.BES")).AsSpan().SequenceEqual(original),
                "An edited original career becomes a new CE file after a verified backup, without changing the source");
            await app.OpenCareerAsync(inherited);
            File.WriteAllBytes(Path.Combine(saves, "original only.bes"), original);
            await app.CatchUpAsync(force: false, backUp: false);
            check.That(app.Workspace.Session?.Path == Path.Combine(saves, "original only.bes"),
                "A new user copy becomes the viewed career even when its bytes equal the old original source");
            app.Backups.AskToRestore(manifest, manifest.Files.First());
            check.That(app.Backups.Confirm.DialogText.Contains("From: Onslaught CE") &&
                app.Backups.Confirm.DialogText.Contains("To: Onslaught CE") && !app.Backups.Confirm.DialogText.Contains("settings"),
                "Restore confirmation identifies both games without promising a CE-settings backup");
            app.Backups.Confirm.Hide();
            app.Backups.AskToRestore(manifest, manifest.Files.First());
            await app.SelectTargetAsync(GameTarget.Original);
            InstallReceipt switched = await app.Backups.ConfirmAsync();
            check.That(!switched.Ok && File.ReadAllBytes(other.Career).AsSpan().SequenceEqual(original),
                "Switching games after a restore prompt invalidates its destination confirmation");
            app.Backups.AskToRestore(manifest with { Target = null }, manifest.Files.First());
            check.That(app.Backups.Confirm.DialogText.Contains("Game not recorded (older backup)"),
                "A legacy backup is not silently called an original-game or CE backup");
            app.Backups.Confirm.Hide();
        }
        finally { app.QueueFree(); await Frame(); }

        // Restoring an inherited backup to CE creates a user copy; its backup hash is not an existing-destination hash.
        string restoreName = "Restore inherited.bes";
        File.WriteAllBytes(Path.Combine(retail.Game, "savegames", restoreName), original);
        InstallReceipt restored = GameInstaller.Install(files, GameFolder.InspectCe(user, retail.Game), restoreName,
            original, backups, () => false, DateTime.Now);
        check.That(restored.Ok && !restored.Replaced && File.Exists(Path.Combine(saves, restoreName)) &&
            File.ReadAllBytes(Path.Combine(retail.Game, "savegames", restoreName)).AsSpan().SequenceEqual(original),
            "Publishing an inherited backup writes a new CE shadow and leaves its original source unchanged");

        string package = Path.Combine(root, "package"), unsafeUser = Path.Combine(package, "user");
        Directory.CreateDirectory(Path.Combine(unsafeUser, "savegames"));
        File.WriteAllText(Path.Combine(package, "onslaught-ce"), "owned marker; never run");
        File.WriteAllText(Path.Combine(package, OnslaughtCe.LinuxLauncher), "owned marker; never run");
        string unsafeCareer = Path.Combine(unsafeUser, "savegames", "Pilot.bes");
        File.WriteAllBytes(unsafeCareer, original);
        GameFolder unsafeGame = GameFolder.InspectCe(unsafeUser);
        check.That(!Backups.Create(files, unsafeGame, backups, DateTime.Now).Ok &&
            !GameInstaller.Install(files, unsafeGame, "Pilot.bes", original, backups, () => false, DateTime.Now).Ok &&
            File.ReadAllBytes(unsafeCareer).AsSpan().SequenceEqual(original),
            "Career backup and publication refuse user folders in CE packages even without a selected launcher");
        string unsafeBackups = Path.Combine(package, "new-backups");
        check.That(new BackupLocation(new SettingsStore(Path.Combine(root, "empty-settings.json")), unsafeBackups).Ensure() is null &&
            !Directory.Exists(unsafeBackups), "Backup-folder selection cannot create a folder inside an unselected CE package");
        settings.Save(new CompanionSettings { GameFolder = other.Game, Target = GameTarget.OnslaughtCe, AutoBackup = false });
        GameLibrary unsafeLibrary = new([], settings, unsafeUser, _ => null);
        await unsafeLibrary.DetectAsync();
        check.That(unsafeLibrary.Folder is null && unsafeLibrary.CeVersionMessage.Contains("outside the CE package folder"),
            "CE browsing reports an unsafe user folder before offering write paths");

        // CE admits data-only installs: an absent executable must not turn their files into writable CE data.
        string dataOnly = Path.Combine(root, "data-only"), dataCareer = Path.Combine(dataOnly, "savegames", "Pilot.bes");
        Directory.CreateDirectory(Path.GetDirectoryName(dataCareer)!);
        Directory.CreateDirectory(Path.Combine(dataOnly, "DaTa"));
        File.WriteAllBytes(dataCareer, original);
        string dataIni = Path.Combine(dataOnly, "ce.ini");
        File.WriteAllText(dataIni, "update_check=1\n");
        GameFolder unsafeOriginal = GameFolder.InspectCe(dataOnly, other.Game, dataOnly);
        int backupCount = Backups.List(backups).Count;
        check.That(!Backups.Create(files, unsafeOriginal, backups, DateTime.Now).Ok &&
            !GameInstaller.Install(files, unsafeOriginal, "Pilot.bes", original, backups, () => false, DateTime.Now).Ok &&
            File.ReadAllBytes(dataCareer).AsSpan().SequenceEqual(original) && Backups.List(backups).Count == backupCount,
            "A data-only original cannot become CE's writable user folder or generate backup side effects");
        GameFolder validUser = GameFolder.InspectCe(user, other.Game, dataOnly);
        check.That(!Backups.Create(files, validUser, dataOnly, DateTime.Now).Ok &&
            !GameInstaller.Install(files, validUser, "Blocked.bes", original, dataOnly, () => false, DateTime.Now).Ok &&
            !File.Exists(Path.Combine(saves, "Blocked.bes")),
            "CE careers refuse backups inside the separate data-only original folder");
        string nestedBackup = Path.Combine(dataOnly, "new-backups");
        check.That(new BackupLocation(new SettingsStore(Path.Combine(root, "data-only-settings.json")), nestedBackup)
            .Ensure(ceOriginalRoot: dataOnly) is null && !Directory.Exists(nestedBackup),
            "Backup-folder selection refuses data-only originals before creating any directory");
        check.That(!Options.CeSettings.Read(dataOnly).Value!.Save(false, false, backups, () => false, DateTime.Now,
                originalRoot: dataOnly).Ok && File.ReadAllText(dataIni) == "update_check=1\n" &&
            !Options.CeSettings.Read(user).Value!.Save(false, false, dataOnly, () => false, DateTime.Now,
                originalRoot: dataOnly).Ok,
            "CE settings protect both user and backup destinations against a data-only original root");
        GameLibrary sameOriginal = new([], settings, dataOnly, name => name == "BEA_GAME_DIR" ? dataOnly : null,
            path => path == dataOnly);
        await sameOriginal.DetectAsync();
        check.That(sameOriginal.Folder is null && sameOriginal.CeOriginalRoot == dataOnly &&
            sameOriginal.CeVersionMessage.Contains("outside CE's original game data folder"),
            "CE retains its data-only original identity while refusing unsafe user-folder browsing and writes");
    }
}
