// SPDX-License-Identifier: GPL-3.0-only
using System.Text.Json;
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Focused headless entry and ordinary-suite regressions, using only owned real-fixture copies.</summary>
public partial class FoundationSafetyTests : SceneTree
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
            await RunAsync(this, original, output, check);
            check.That(File.ReadAllBytes(fixture).AsSpan().SequenceEqual(original), "The owned input fixture remains unchanged.");
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"FOUNDATION_TESTS: {check.Failures.Count} failures in {check.Count} checks.");
            exit = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr(error); }
        finally { Quit(exit); }
    }

    internal static async Task RunAsync(SceneTree tree, byte[] original, string output, Checks check)
    {
        string root = Path.Combine(output, "foundation-safety");
        check.Suite("foundation safety");
        foreach (GameTarget target in Enum.GetValues<GameTarget>()) await NewCareerIntent(tree, original, root, target, check);
        NewCareerPublication(original, root, check);
        ManifestAdmission(original, root, check);
        await OriginalCareerCase(original, root, check);
    }

    private static async Task NewCareerIntent(SceneTree tree, byte[] original, string output, GameTarget target, Checks check)
    {
        string root = Path.Combine(output, "new-" + target);
        FakeInstall install = FakeInstall.Create(Path.Combine(root, "retail"), original);
        string user = Path.Combine(root, "ce-user"), backups = Path.Combine(root, "backups");
        Directory.CreateDirectory(Path.Combine(user, "savegames"));
        string ceCareer = Path.Combine(user, "savegames", "Career One.bes");
        File.WriteAllBytes(ceCareer, original);
        SettingsStore settings = new(Path.Combine(root, "settings.json"));
        settings.Save(new CompanionSettings { GameFolder = install.Game, Target = target, AutoBackup = false });
        CompanionApp app = new(new ProtectedSaveFiles(), false,
            new CompanionEnvironment([install.SteamRoot], settings.FilePath, GameRunning: () => false,
                OpenUrl: _ => throw new InvalidOperationException("Tests cannot launch another application."),
                DefaultBackupFolder: backups, CeUserFolder: user, CeInstallSupported: GameFolder.LooksLikeGame));
        tree.Root.AddChild(app);
        async Task Frame() => await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        await Frame();
        try
        {
            for (int frame = 0; frame < 600 && (app.Game.Busy || app.Workspace.Busy || app.Workspace.Session is null); frame++) await Frame();
            check.That(app.Workspace.Session is not null && app.Game.Folder?.Target == target, $"{target}: owned career is ready.");
            if (app.Workspace.Session is null || app.Game.Folder is not GameFolder game) return;
            byte[] external = original.ToArray(); external[^1] ^= 0x5A;
            string collision = Path.Combine(game.SavegamesPath, "Confirmed new.bes");
            app.Navigate("edit");
            app.EditCareer.Rows[0].Target.Value = 123456;
            app.EditCareer.AskToSave();
            app.EditCareer.SaveChoice.Name.Text = "Confirmed new";
            check.That(!app.EditCareer.SaveChoice.Dialog.GetOkButton().Disabled, $"{target}: the new name was vacant at confirmation.");
            File.WriteAllBytes(collision, external);
            // Await the same action called by the confirmation, after an external file appeared.
            app.EditCareer.SaveChoice.Dialog.Hide();
            InstallReceipt edited = await app.EditCareer.SaveIntoGameAsync(SaveTarget.NewCareer, "Confirmed new");
            check.That(!edited.Ok && !edited.MayHaveChanged && File.ReadAllBytes(collision).AsSpan().SequenceEqual(external),
                $"{target}: New career cannot replace a file appearing after its confirmation opened.");

            app.Home.AskToAdd(install.Career);
            app.Home.AddChoice.Name.Text = "Confirmed import";
            string imported = Path.Combine(game.SavegamesPath, "Confirmed import.bes");
            File.WriteAllBytes(imported, external);
            app.Home.AddChoice.Dialog.Hide();
            InstallReceipt added = await app.Home.AddCareerAsync("Confirmed import");
            check.That(!added.Ok && !added.MayHaveChanged && File.ReadAllBytes(imported).AsSpan().SequenceEqual(external),
                $"{target}: Home import retains create-only intent through its fresh folder read.");

            app.Cheats.BaseName.Text = "Confirmed cheat";
            app.Cheats.Choices[0].ButtonPressed = true;
            app.Cheats.AskToAdd();
            string cheat = Path.Combine(game.SavegamesPath, app.Cheats.Composed.FileName);
            File.WriteAllBytes(cheat, external);
            InstallReceipt cheated = await app.Cheats.ConfirmAddAsync();
            check.That(!cheated.Ok && !cheated.MayHaveChanged && File.ReadAllBytes(cheat).AsSpan().SequenceEqual(external),
                $"{target}: a confirmed cheat copy cannot replace a newly occupied name.");

            app.EditCareer.Rows[0].Target.Value = 123456;
            InstallReceipt replaced = await app.EditCareer.SaveIntoGameAsync(SaveTarget.Replace, "");
            string career = target == GameTarget.Original ? install.Career : ceCareer;
            byte[] changed = File.ReadAllBytes(career);
            check.That(replaced.Ok && replaced.Replaced && replaced.BackupFolder is not null &&
                File.ReadAllBytes(Path.Combine(replaced.BackupFolder, "Career One.bes")).AsSpan().SequenceEqual(original) &&
                !changed.AsSpan().SequenceEqual(original) && changed.Where((_, i) => i < CareerSave.KillsOffset || i >= CareerSave.KillsOffset + 3)
                    .SequenceEqual(original.Where((_, i) => i < CareerSave.KillsOffset || i >= CareerSave.KillsOffset + 3)),
                $"{target}: intentional replacement still backs up the original and preserves every unselected byte.");
            if (replaced.BackupFolder is not null)
            {
                BackupSet set = Backups.List(backups).Single(value => value.Folder == replaced.BackupFolder);
                app.Backups.AskToRestore(set, set.Files.Single(file => file.Name == "Career One.bes"));
                InstallReceipt restored = await app.Backups.ConfirmAsync();
                check.That(restored.Ok && File.ReadAllBytes(career).AsSpan().SequenceEqual(original) && restored.BackupFolder is not null &&
                    File.ReadAllBytes(Path.Combine(restored.BackupFolder, "Career One.bes")).AsSpan().SequenceEqual(changed),
                    $"{target}: intentional restore still preserves the displaced edit and reopens original bytes.");
            }
        }
        finally
        {
            for (int frame = 0; frame < 600 && (app.Game.Busy || app.Workspace.Busy); frame++) await Frame();
            await app.PendingCatchUp;
            app.QueueFree(); await Frame();
        }
    }

    private static void ManifestAdmission(byte[] original, string output, Checks check)
    {
        string root = Path.Combine(output, "manifests");
        FakeInstall install = FakeInstall.Create(Path.Combine(root, "retail"), original);
        GameFolder game = GameFolder.Inspect(install.Game, "test");
        BackupFile file = new("Career One.bes", install.Career, original.Length, SaveSession.Digest(original));
        BackupSet valid = new("ignored manifest folder", new DateTime(2026, 10, 25), install.Game, [file]);
        (string Name, string Json)[] invalid =
        [
            ("missing", "{}"),
            ("null-files", JsonSerializer.Serialize(valid with { Files = null! })),
            ("null-entry", JsonSerializer.Serialize(valid with { Files = [null!] })),
            ("duplicate", JsonSerializer.Serialize(valid with { Files = [file, file] })),
            ("null-name", JsonSerializer.Serialize(valid with { Files = [file with { Name = null! }] })),
            ("traversal", JsonSerializer.Serialize(valid with { Files = [file with { Name = "../Escape.bes" }] })),
            ("backslash", JsonSerializer.Serialize(valid with { Files = [file with { Name = "sub\\Escape.bes" }] })),
            ("kind", JsonSerializer.Serialize(valid with { Files = [file with { Name = "notes.txt" }] })),
            ("hash", JsonSerializer.Serialize(valid with { Files = [file with { Sha256 = "not a fingerprint" }] })),
            ("size", JsonSerializer.Serialize(valid with { Files = [file with { Size = 3 }] })),
            ("original", JsonSerializer.Serialize(valid with { Files = [file with { Original = "relative.bes" }] })),
            ("game", JsonSerializer.Serialize(valid with { Game = "relative" })),
            ("date", JsonSerializer.Serialize(valid with { Created = default })),
            ("target", JsonSerializer.Serialize(valid with { Target = (GameTarget)77 })),
        ];
        foreach ((string name, string json) in invalid)
        {
            string owner = Path.Combine(root, name), folder = Path.Combine(owner, "onslaught-backup-invalid");
            Directory.CreateDirectory(folder);
            File.WriteAllText(Path.Combine(folder, Backups.ManifestName), json);
            check.That(Backups.List(owner).Count == 0, $"Invalid manifest {name} is refused before UI consumers.");
            bool changed;
            try { changed = Backups.ChangedSinceLatest(game, owner); }
            catch (Exception) { changed = false; }
            check.That(changed, $"Invalid manifest {name} cannot fault or suppress a fresh automatic backup.");
        }
        string accepted = Path.Combine(root, "accepted"), legacy = Path.Combine(accepted, "onslaught-backup-legacy"),
            foreign = Path.Combine(accepted, "onslaught-backup-foreign");
        Directory.CreateDirectory(legacy); Directory.CreateDirectory(foreign);
        File.WriteAllText(Path.Combine(legacy, Backups.ManifestName), JsonSerializer.Serialize(valid));
        File.WriteAllText(Path.Combine(foreign, Backups.ManifestName), JsonSerializer.Serialize(valid with
        {
            Game = @"C:\Games\BEA", Files = [file with { Original = @"C:\Games\BEA\savegames\Career One.bes" }],
        }));
        check.That(Backups.List(accepted).Count == 2 && Backups.List(accepted, game).Count == 1,
            "Valid legacy and foreign-platform backup manifests remain readable without conflating their game roots.");
        string oversized = Path.Combine(root, "large", "onslaught-backup-oversized");
        Directory.CreateDirectory(oversized);
        using (FileStream stream = File.Create(Path.Combine(oversized, Backups.ManifestName))) stream.SetLength(16 * 1024 * 1024 + 1);
        check.That(Backups.List(Path.GetDirectoryName(oversized)!).Count == 0, "An oversized manifest is refused without reading its entire body.");
    }

    private static void NewCareerPublication(byte[] original, string output, Checks check)
    {
        bool previous = GameInstaller.UsePortableInstall;
        try
        {
            foreach (bool portable in OperatingSystem.IsLinux() ? new[] { false, true } : new[] { false })
            {
                GameInstaller.UsePortableInstall = portable;
                string root = Path.Combine(output, "new-publication-" + portable);
                FakeInstall install = FakeInstall.Create(Path.Combine(root, "retail"), original);
                string backups = Path.Combine(root, "backups"); Directory.CreateDirectory(backups);
                GameFolder game = GameFolder.Inspect(install.Game, "test");
                ProtectedSaveFiles files = new();
                byte[] external = original.ToArray(); external[^1] ^= 0x55;
                string taken = Path.Combine(game.SavegamesPath, "CASE CLASH.BES");
                File.WriteAllBytes(taken, external);
                InstallReceipt existing = GameInstaller.Install(files, game, "case clash.bes", original, backups,
                    () => false, DateTime.Now, requireNew: true);
                check.That(!existing.Ok && !existing.MayHaveChanged && File.ReadAllBytes(taken).AsSpan().SequenceEqual(external) &&
                    Directory.GetDirectories(backups).Length == 0 && Directory.EnumerateFiles(game.SavegamesPath).Count(path =>
                        Path.GetFileName(path).Equals("case clash.bes", StringComparison.OrdinalIgnoreCase)) == 1,
                    $"Portable={portable}: a fresh case-insensitive collision refuses Add before creating a backup.");
                string late = Path.Combine(game.SavegamesPath, "Late.bes");
                InstallReceipt raced = GameInstaller.Install(files, game, "Late.bes", original, backups, () => false, DateTime.Now,
                    beforeSwap: () => File.WriteAllBytes(late, external), requireNew: true);
                check.That(!raced.Ok && !raced.MayHaveChanged && File.ReadAllBytes(late).AsSpan().SequenceEqual(external),
                    $"Portable={portable}: Add remains no-clobber when the name is occupied immediately before publication.");
                InstallReceipt fresh = GameInstaller.Install(files, game, "Vacant.bes", original, backups, () => false, DateTime.Now,
                    requireNew: true);
                check.That(fresh is { Ok: true, Replaced: false } && File.ReadAllBytes(fresh.Target).AsSpan().SequenceEqual(original),
                    $"Portable={portable}: an actually vacant Add still publishes and verifies exact fixture bytes.");
            }
        }
        finally { GameInstaller.UsePortableInstall = previous; }
    }

    private static async Task OriginalCareerCase(byte[] original, string output, Checks check)
    {
        string root = Path.Combine(output, "original-case");
        FakeInstall install = FakeInstall.Create(Path.Combine(root, "retail"), original);
        SettingsStore settings = new(Path.Combine(root, "settings.json"));
        settings.Save(new CompanionSettings { GameFolder = install.Game });
        GameLibrary library = new([install.SteamRoot], settings, ceUserFolder: "");
        await library.DetectAsync();
        check.That(!library.FilesChanged(), "An unchanged original folder starts with no pending file changes.");
        string upper = Path.Combine(install.Game, "savegames", "Upper.BES"), mixed = Path.Combine(install.Game, "savegames", "Mixed.bEs");
        File.WriteAllBytes(upper, original); File.WriteAllBytes(mixed, original);
        check.That(library.FilesChanged(), "Uppercase career additions participate in original-game change detection.");
        await library.RescanAsync();
        GameFolder game = library.Folder!;
        check.That(game.Careers.Any(file => file.Path == upper) && game.Careers.Any(file => file.Path == mixed),
            "Original-game discovery includes uppercase and mixed-case career extensions.");
        string backups = Path.Combine(root, "backups"); Directory.CreateDirectory(backups);
        BackupReceipt backed = Backups.Create(new ProtectedSaveFiles(), game, backups, DateTime.Now);
        check.That(backed.Ok && backed.Set is not null && new[] { upper, mixed }.All(path =>
            backed.Set.Files.Any(file => file.Original == path) &&
            File.ReadAllBytes(Path.Combine(backed.Set.Folder, Path.GetFileName(path))).AsSpan().SequenceEqual(original)),
            "Original-game backups preserve both case variants as exact fixture copies.");
        check.That(!library.FilesChanged(), "A rescan and backup leave original-game discovery in agreement.");
        if (OperatingSystem.IsLinux())
        {
            string lower = Path.Combine(game.SavegamesPath, "upper.bes");
            File.WriteAllBytes(lower, original);
            byte[] edited = original.ToArray(); edited[CareerSave.KillsOffset] ^= 0x7A;
            InstallReceipt replaced = GameInstaller.Install(new ProtectedSaveFiles(), game, "upper.bes", edited, backups,
                () => false, DateTime.Now, expectedSha256: SaveSession.Digest(original));
            check.That(replaced.Ok && replaced.Target == lower && File.ReadAllBytes(lower).AsSpan().SequenceEqual(edited) &&
                File.ReadAllBytes(upper).AsSpan().SequenceEqual(original),
                "An intentional replacement prefers its exact filename when Linux holds distinct letter-case variants.");
        }
    }
}
