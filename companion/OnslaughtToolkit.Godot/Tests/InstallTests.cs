// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Writes into a game-shaped folder built from fixture copies: refusals leave everything untouched,
/// every write is preceded by a verified backup, and races are refused or undone.
/// </summary>
internal static class InstallTests
{
    internal static void Run(byte[] original, string outputDirectory, Checks check)
    {
        check.Suite("game writes");
        string root = Path.Combine(outputDirectory, "game-writes");
        FakeInstall install = FakeInstall.Create(Path.Combine(root, "case"), original);
        string backups = Path.Combine(root, "backups");
        Directory.CreateDirectory(backups);
        ProtectedSaveFiles files = new();
        GameFolder game = GameFolder.Inspect(install.Game, "test");
        DateTime now = new(2026, 9, 25, 12, 0, 0);
        byte[] edited = original.ToArray();
        edited[0x2406] ^= 0x5A; // an owned in-memory change inside a kill count's low bytes
        if (!OperatingSystem.IsLinux())
        {
            check.That(!GameInstaller.Install(files, game, "New.bes", edited, backups, () => false, now).Ok,
                "Writing into the game folder is refused where it has not been tested.");
            return;
        }

        foreach ((string comm, string[] argv, bool isGame) in new (string, string[], bool)[]
        {
            ("BEA.exe\n", ["C:\\Program Files\\Battle Engine Aquila\\BEA.exe"], true),
            ("wine64-preload", ["Z:\\home\\player\\Battle Engine Aquila\\BEA.exe", "-window"], true),
            ("wine64-preload", ["/usr/bin/wine64-preloader", "/usr/bin/wine64", "BEA.exe"], true),
            ("bash", ["bash", "/opt/ghidra/support/analyzeHeadless", "project", "-import", "/lab/BEA.exe"], false),
            ("java", ["/usr/bin/java", "-jar", "ghidra.jar", "BEA.exe"], false),
            ("sha256sum", ["sha256sum", "BEA.exe"], false),
            ("python", ["python", "tools/run.py", "--exe=/lab/BEA.exe.original.backup"], false),
        })
        {
            check.That(GameProcess.IsGame(comm, argv) == isGame, $"The running-game check {(isGame ? "finds" : "ignores")} {argv[0]}.");
        }
        OnslaughtCeProcesses(root, check);
        OnslaughtCeFolders(original, root, files, check);
        foreach (string name in new[] { "../escape.bes", "sub/dir.bes", "career.txt", "BEA.exe", ".hidden.bes", " padded.bes", "x.bes " })
            check.That(!GameInstaller.Install(files, game, name, edited, backups, () => false, now).Ok, $"The target name '{name}' is refused.");
        check.That(!GameInstaller.Install(files, game, "New.bes", edited, backups, () => true, now).Ok, "Nothing is written while the game runs.");
        byte[] wrong = edited.ToArray();
        wrong[0] ^= 1;
        check.That(!GameInstaller.Install(files, game, "New.bes", wrong, backups, () => false, now).Ok, "An unsupported file is never installed.");
        check.That(!GameInstaller.Install(files, game, "New.bes", edited, Path.Combine(install.Game, "savegames"), () => false, now).Ok,
            "A backup folder inside the game is refused, so nothing is written.");
        check.That(Backups.List(backups).Count == 0 && !File.Exists(Path.Combine(install.Game, "savegames", "New.bes")) &&
            Unchanged(install, original), "Refusals leave the game folder and backups untouched.");

        InstallReceipt added = GameInstaller.Install(files, game, "Fresh Career.bes", edited, backups, () => false, now);
        string fresh = Path.Combine(install.Game, "savegames", "Fresh Career.bes");
        check.That(added is { Ok: true, Replaced: false } && File.ReadAllBytes(fresh).AsSpan().SequenceEqual(edited),
            "A new career is added to savegames and verified.");
        IReadOnlyList<BackupSet> sets = Backups.List(backups);
        check.That(sets.Count == 1 && sets[0].Files.Count == 2 && Unchanged(install, original) &&
            File.ReadAllBytes(Path.Combine(sets[0].Folder, "Career One.bes")).AsSpan().SequenceEqual(original) &&
            File.ReadAllBytes(Path.Combine(sets[0].Folder, "defaultoptions.bea")).AsSpan().SequenceEqual(original),
            "Even a new file is preceded by a verified backup of every career and settings file the companion can read.");

        InstallReceipt replaced = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Career One.bes", edited, backups,
            () => false, now.AddSeconds(1));
        check.That(replaced is { Ok: true, Replaced: true } && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(edited),
            "An existing career is replaced and verified.");
        check.That(replaced.BackupFolder is string replacedBackup &&
            File.ReadAllBytes(Path.Combine(replacedBackup, "Career One.bes")).AsSpan().SequenceEqual(original),
            "The replaced career's earlier bytes are in that write's verified backup.");
        check.That(Leftovers(install).Length == 0, "No temporary entry is left in savegames.");
        InstallReceipt options = GameInstaller.Install(files, game, "defaultoptions.bea", edited, backups, () => false, now.AddSeconds(2));
        check.That(options.Ok && File.ReadAllBytes(install.Options).AsSpan().SequenceEqual(edited), "The options file is replaced and verified.");

        byte[] other = original.ToArray();
        other[^1] ^= 1;
        InstallReceipt changed = GameInstaller.Install(files, game, "Career One.bes", original, backups, () => false, now.AddSeconds(3),
            beforeCheck: () => File.WriteAllBytes(install.Career, other));
        check.That(!changed.Ok && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(other) && Leftovers(install).Length == 0,
            "A career that changes after its backup is refused and left as it is.");

        if (replaced.Exchanged)
        {
            string moved = install.Career + ".moved";
            InstallReceipt raced = GameInstaller.Install(files, game, "Career One.bes", original, backups, () => false, now.AddSeconds(4),
                beforeSwap: () =>
                {
                    File.Move(install.Career, moved);
                    File.WriteAllBytes(install.Career, other);
                });
            check.That(raced is { Ok: false, MayHaveChanged: true } && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(other) &&
                File.ReadAllBytes(moved).AsSpan().SequenceEqual(other) && Leftovers(install).Length == 0,
                "A file that takes the name just before the swap is swapped back, and ours is withdrawn.");
        }
        else
        {
            check.Fail("This filesystem lacks RENAME_EXCHANGE, so the swap-back case did not run.");
        }
        check.That(Backups.List(backups).Select(set => set.Created).SequenceEqual(Backups.List(backups).Select(set => set.Created)
            .OrderByDescending(created => created)), "Backup sets list newest first.");
        foreach (string name in new[] { "CON", "con", "NUL.bak", "COM1", "LPT9" })
            check.That(GameInstaller.PortableNameProblem(name) is not null, $"The Windows device name '{name}' is refused everywhere.");
        check.That(GameInstaller.PortableNameProblem("Console") is null && GameInstaller.PortableNameProblem("COM10") is null,
            "Ordinary names that only start like a device name are allowed.");

        ChangeGuards(original, root, now, files, check);
        GameStartsDuringWrite(original, root, now, files, check);
        BackupsPerGameFolder(original, root, now, files, check);
        BackupRecoveryIntegrity(original, root, now, files, check);
        BackupCompletion(original, root, now, files, check);
        PublicationBoundary(original, root, now, files, check);
        PortableWrites(original, root, now, files, check);
    }

    /// <summary>
    /// Onslaught CE counts as the game while it runs: its launcher, or its game program <c>bea</c> in a folder that
    /// also holds the launcher, as a CE package lays them out. A program called <c>bea</c> anywhere else does not.
    /// </summary>
    private static void OnslaughtCeProcesses(string root, Checks check)
    {
        string package = Path.Combine(root, "onslaught-ce-1.0-linux-i686");
        string elsewhere = Path.Combine(root, "unrelated-tools");
        Directory.CreateDirectory(package);
        Directory.CreateDirectory(elsewhere);
        foreach (string name in new[] { "bea", "onslaught-ce-launch", "onslaught-ce" }) File.WriteAllText(Path.Combine(package, name), "marker");
        File.WriteAllText(Path.Combine(elsewhere, "bea"), "marker");
        string game = Path.Combine(package, "bea"), launcher = Path.Combine(package, "onslaught-ce-launch");
        foreach ((string comm, string[] argv, string? program, bool isCe, string what) in new (string, string[], string?, bool, string)[]
        {
            ("onslaught-ce-la", [launcher], launcher, true, "CE's launcher"),
            ("bea", ["./bea"], game, true, "CE's bea in its package folder"),
            ("bea", ["./bea"], game + " (deleted)", true, "CE's bea replaced by an update while it runs (/proc/PID/exe ends in (deleted))"),
            ("bea", [game], Path.Combine(root, "gone", "bea") + " (deleted)", true,
                "CE's bea whose old file is gone, placed by its full-path argv[0]"),
            ("bea", ["./bea"], Path.Combine(elsewhere, "bea") + " (deleted)", false, "a deleted program called bea outside a CE package"),
            ("bea", [game, "--windowed"], null, true, "CE's bea named by its full path when /proc/PID/exe cannot be read"),
            ("onslaught-ce", ["bash", Path.Combine(package, "onslaught-ce")], "/usr/bin/bash", true, "CE's start script"),
            ("bea", ["./bea"], Path.Combine(elsewhere, "bea"), false, "a program called bea outside a CE package"),
            ("bea", ["bea"], null, false, "a relative bea that cannot be placed"),
            ("python3", ["python3", game], "/usr/bin/python3", false, "a tool that only names CE's bea"),
            ("beam.smp", ["/usr/lib/erlang/erts/bin/beam.smp"], "/usr/lib/erlang/erts/bin/beam.smp", false, "a program whose name starts like bea"),
        })
        {
            check.That(GameProcess.IsOnslaughtCe(comm, argv, program, File.Exists) == isCe,
                $"The running-game check {(isCe ? "finds" : "ignores")} {what}.");
        }
        check.That(!GameProcess.IsGame("bea", [game]) && GameProcess.IsGame("bea.exe", ["Z:\\games\\onslaught-ce\\bea.exe"]),
            "The BEA.exe rule does not take CE's Linux bea for the original game, and CE's Windows bea.exe under Wine counts as the game.");
    }

    /// <summary>CE's own careers folder is never a place for a copy saved elsewhere, wherever CE's environment puts it.</summary>
    private static void OnslaughtCeFolders(byte[] original, string root, ProtectedSaveFiles files, Checks check)
    {
        Dictionary<string, string?> linux = new() { ["XDG_DATA_HOME"] = "/data/xdg", ["BEA_USER_DIR"] = "/srv/ce-user" };
        IReadOnlyList<string> folders = OnslaughtCe.UserFolders(name => linux.GetValueOrDefault(name), windows: false, "/home/player");
        check.That(folders.SequenceEqual(["/srv/ce-user", "/data/xdg/onslaught-ce", "/home/player/.local/share/onslaught-ce"]),
            "CE's folders on Linux: BEA_USER_DIR, $XDG_DATA_HOME/onslaught-ce and ~/.local/share/onslaught-ce.");
        foreach (string broad in new[] { "/", "/home/player", "/home", "relative/ce" })
            check.That(!OnslaughtCe.UserFolders(name => name == "BEA_USER_DIR" ? broad : null, windows: false, "/home/player").Contains(broad),
                $"A BEA_USER_DIR of '{broad}' is not taken as CE's folder, so it cannot refuse everything under it.");
        check.That(OnslaughtCe.UserFolders(name => name == "APPDATA" ? "/appdata" : null, windows: true, "/home/player")
            .SequenceEqual([Path.Combine("/appdata", "Onslaught CE")]), "CE's folder on Windows is %APPDATA%\\Onslaught CE.");

        string source = Path.Combine(root, "ce-copy-source.bes");
        File.WriteAllBytes(source, original);
        ProtectedRead read = files.OpenCareer(source);
        string custom = Path.Combine(root, "ce-user-dir");
        string xdg = Path.Combine(root, "ce-xdg-data");
        string xdgCe = Path.Combine(xdg, "onslaught-ce");
        string allowed = Path.Combine(root, "ce-neighbour");
        foreach (string folder in new[] { Path.Combine(custom, "savegames"), Path.Combine(xdgCe, "savegames"), allowed })
            Directory.CreateDirectory(folder);
        // The test sets both variables itself, so it never depends on (or writes into) the runner's real data folder.
        string? before = Environment.GetEnvironmentVariable("BEA_USER_DIR"), xdgBefore = Environment.GetEnvironmentVariable("XDG_DATA_HOME");
        Environment.SetEnvironmentVariable("BEA_USER_DIR", custom);
        Environment.SetEnvironmentVariable("XDG_DATA_HOME", xdg);
        try
        {
            foreach (string output in new[] { Path.Combine(custom, "savegames", "Copy.bes"), Path.Combine(custom, "Copy.bes"),
                Path.Combine(xdgCe, "savegames", "Copy.bes") })
            {
                PublicationReceipt refused = files.PublishCopy(source, read.Identity, read.Sha256, output, original);
                check.That(!refused.Ok && !refused.MayHaveOutput && refused.Message.Contains("Onslaught CE") && !File.Exists(output),
                    $"A copy is refused inside Onslaught CE's folder ({Path.GetRelativePath(root, output)}), and nothing is written.");
            }
            string fine = Path.Combine(allowed, "Copy.bes");
            check.That(files.PublishCopy(source, read.Identity, read.Sha256, fine, original).Ok && File.Exists(fine),
                "A copy beside CE's folder, not inside it, is still saved.");
        }
        finally
        {
            Environment.SetEnvironmentVariable("BEA_USER_DIR", before);
            Environment.SetEnvironmentVariable("XDG_DATA_HOME", xdgBefore);
        }
    }

    /// <summary>
    /// The game starting while the backup is made: the second running check, just before the swap or link, refuses the
    /// write and nothing changes, on the Linux and the portable path, for a new career and a replacement.
    /// </summary>
    private static void GameStartsDuringWrite(byte[] original, string root, DateTime now, ProtectedSaveFiles files, Checks check)
    {
        byte[] edited = original.ToArray();
        edited[0x2406] ^= 0x5A;
        int second = 0;
        foreach (bool portable in new[] { false, true })
        {
            GameInstaller.UsePortableInstall = portable;
            try
            {
                string path = portable ? "Portable path" : "Linux path";
                FakeInstall install = FakeInstall.Create(Path.Combine(root, portable ? "starts-portable" : "starts-linux"), original);
                string backups = Path.Combine(root, portable ? "starts-portable-backups" : "starts-linux-backups");
                Directory.CreateDirectory(backups);
                foreach (string target in new[] { "Started.bes", "Career One.bes" })
                {
                    int checks = 0;
                    bool StartsAfterFirstCheck() => ++checks > 1;
                    InstallReceipt refused = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), target, edited, backups,
                        StartsAfterFirstCheck, now.AddSeconds(second++), beforeSwap: () => { });
                    check.That(refused is { Ok: false, MayHaveChanged: false, BackupFolder: not null } && checks == 2 &&
                        refused.Message.Contains("started while the backup was being made") &&
                        !File.Exists(Path.Combine(install.Game, "savegames", "Started.bes")) && Unchanged(install, original) &&
                        Leftovers(install).Length == 0,
                        $"{path}: a game that starts during the backup stops the write of {target} just before the swap; nothing is written.");
                }
            }
            finally
            {
                GameInstaller.UsePortableInstall = false;
            }
        }
    }

    /// <summary>
    /// Two game folders sharing one backup folder: each one's automatic backup compares only with its own latest set, and
    /// a set is matched to the game folder it was made from.
    /// </summary>
    private static void BackupsPerGameFolder(byte[] original, string root, DateTime now, ProtectedSaveFiles files, Checks check)
    {
        FakeInstall first = FakeInstall.Create(Path.Combine(root, "two-games-first"), original);
        FakeInstall second = FakeInstall.Create(Path.Combine(root, "two-games-second"), original);
        string backups = Path.Combine(root, "two-games-backups");
        Directory.CreateDirectory(backups);
        GameFolder one = GameFolder.Inspect(first.Game, "test"), two = GameFolder.Inspect(second.Game, "test");
        BackupReceipt made = Backups.Create(files, one, backups, now, "Automatic backup");
        check.That(made.Ok && !Backups.ChangedSinceLatest(one, backups) && Backups.ChangedSinceLatest(two, backups),
            "A backup of one game folder does not count as the latest backup of another holding the same files.");
        Backups.Create(files, two, backups, now.AddSeconds(1), "Automatic backup");
        IReadOnlyList<BackupSet> ones = Backups.List(backups, one), twos = Backups.List(backups, two);
        check.That(ones.Count == 1 && twos.Count == 1 && Backups.SameGame(ones[0], one) && !Backups.SameGame(ones[0], two) &&
            !Backups.SameGame(twos[0], one) && Backups.List(backups).Count == 2, "Each backup set is matched to the game folder it came from.");
        check.That(!Backups.SameGame(ones[0] with { Game = "" }, one) && !Backups.SameGame(ones[0] with { Game = "relative/game" }, one) &&
            Backups.SameGame(ones[0] with { Game = first.Game + Path.DirectorySeparatorChar }, one),
            "A set without a full game folder path matches no game; a trailing separator does not matter.");
    }

    /// <summary>An unchanged game still needs a fresh backup if its recorded recovery copy is no longer usable.</summary>
    private static void BackupRecoveryIntegrity(byte[] original, string root, DateTime now, ProtectedSaveFiles files, Checks check)
    {
        foreach (GameTarget target in new[] { GameTarget.Original, GameTarget.OnslaughtCe })
        {
            string owner = Path.Combine(root, "backup-recovery-" + target);
            FakeInstall install = FakeInstall.Create(Path.Combine(owner, "game"), original);
            GameFolder game = target == GameTarget.Original ? GameFolder.Inspect(install.Game, "test") : GameFolder.InspectCe(install.Game);
            string backups = Path.Combine(owner, "backups"); Directory.CreateDirectory(backups);
            BackupReceipt made = Backups.Create(files, game, backups, now);
            check.That(made.Ok && made.Set is not null && !Backups.ChangedSinceLatest(game, backups),
                $"{target}: an intact verified recovery set avoids a duplicate automatic backup.");
            if (made.Set is not BackupSet set) continue;
            string copy = Path.Combine(set.Folder, "Career One.bes");
            File.Delete(copy);
            check.That(Backups.ChangedSinceLatest(game, backups), $"{target}: a deleted recovery copy cannot suppress a fresh automatic backup.");
            byte[] changed = original.ToArray(); changed[^1] ^= 0x5A;
            File.WriteAllBytes(copy, changed);
            check.That(Backups.ChangedSinceLatest(game, backups), $"{target}: a changed recovery copy cannot stand in for the manifest's recorded bytes.");
            File.WriteAllBytes(copy, [1, 2, 3]);
            check.That(Backups.ChangedSinceLatest(game, backups), $"{target}: a truncated recovery copy is not a usable backup.");
            File.Delete(copy); Directory.CreateDirectory(copy);
            check.That(Backups.ChangedSinceLatest(game, backups), $"{target}: a directory at the recovery filename is not a usable backup.");
            Directory.Delete(copy);
            if (OperatingSystem.IsLinux())
            {
                File.CreateSymbolicLink(copy, install.Career);
                check.That(Backups.ChangedSinceLatest(game, backups), $"{target}: a recovery symlink to unchanged game bytes is refused.");
                File.Delete(copy);
                string alias = Path.Combine(owner, "linked-source.bes"); File.WriteAllBytes(alias, original);
                check.That(LinuxSaveNative.LinkAt(LinuxSaveNative.AtCurrentDirectory, alias,
                    LinuxSaveNative.AtCurrentDirectory, copy, 0) == 0, $"{target}: the owned hardlink control was created.");
                check.That(Backups.ChangedSinceLatest(game, backups), $"{target}: a linked recovery file is not an independent verified backup.");
                File.Delete(copy);
            }
            File.WriteAllBytes(copy, original);
            check.That(!Backups.ChangedSinceLatest(game, backups), $"{target}: the exact restored recovery set avoids unnecessary backup duplication.");
            check.That(Unchanged(install, original), $"{target}: recovery inspection leaves all original game files untouched.");
        }
    }

    /// <summary>Each copy can succeed before the set's folder or payload changes; no such set licenses a game write.</summary>
    private static void BackupCompletion(byte[] original, string root, DateTime now, ProtectedSaveFiles files, Checks check)
    {
        if (!OperatingSystem.IsLinux()) return; // Native Windows handle ownership needs a Windows run, not these Linux races.
        foreach (GameTarget target in new[] { GameTarget.Original, GameTarget.OnslaughtCe })
        foreach (bool installCareer in new[] { false, true })
        foreach (string scenario in new[] { "normal", "linked-folder", "replacement-folder", "changed-payload", "manifest-collision" })
        {
            string name = $"{target}-{installCareer}-{scenario}";
            string owner = Path.Combine(root, "backup-completion-" + name);
            FakeInstall install = FakeInstall.Create(Path.Combine(owner, "game"), original);
            string career = install.Career;
            GameFolder game;
            if (target == GameTarget.OnslaughtCe)
            {
                string user = Path.Combine(owner, "ce-user");
                Directory.CreateDirectory(Path.Combine(user, "savegames"));
                career = Path.Combine(user, "savegames", "Career One.bes");
                File.WriteAllBytes(career, original);
                game = GameFolder.InspectCe(user, install.Game, install.Game);
            }
            else game = GameFolder.Inspect(install.Game, "test");
            string backups = Path.Combine(owner, "backups"), outside = Path.Combine(owner, "outside");
            string retained = Path.Combine(owner, "retained-payloads");
            Directory.CreateDirectory(backups); Directory.CreateDirectory(outside);
            int copies = game.Careers.Count(file => file.Supported) + (game.Options is { Supported: true } ? 1 : 0);
            string? completed = null;
            bool triggered = false;
            AfterBackupCopies boundary = new(files, copies, afterCopies: folder =>
            {
                completed = folder;
                if (scenario is "linked-folder" or "replacement-folder")
                {
                    Directory.Move(folder, retained); // Keep the real, verified copies at a known owned path.
                    if (scenario == "linked-folder") Directory.CreateSymbolicLink(folder, outside);
                    else Directory.CreateDirectory(folder);
                    triggered = true;
                }
                if (scenario == "changed-payload")
                {
                    string copy = Path.Combine(folder, "Career One.bes");
                    File.Copy(copy, Path.Combine(owner, "retained-original-payload.bes"));
                    byte[] changed = original.ToArray(); changed[0x2406] ^= 0x5A;
                    File.WriteAllBytes(copy, changed);
                    triggered = true;
                }
                if (scenario == "manifest-collision")
                {
                    File.WriteAllText(Path.Combine(folder, Backups.ManifestName), "Owned preexisting manifest; keep it.");
                    triggered = true;
                }
            });
            byte[] prepared = original.ToArray(); prepared[0x2406] ^= 0x5A;
            bool ok = installCareer
                ? GameInstaller.Install(boundary, game, "Career One.bes", prepared, backups, () => false, now,
                    expectedSha256: files.OpenCareer(career).Sha256).Ok
                : Backups.Create(boundary, game, backups, now).Ok;
            check.That(ok == (scenario == "normal"), $"{name}: only an intact completed backup permits success.");
            check.That(scenario == "normal" || triggered, $"{name}: the owned completion fault actually ran.");
            byte[] expectedCareer = installCareer && scenario == "normal" ? prepared : original;
            check.That(File.ReadAllBytes(career).AsSpan().SequenceEqual(expectedCareer) &&
                File.ReadAllBytes(install.Options).AsSpan().SequenceEqual(original) &&
                (target != GameTarget.OnslaughtCe || File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original)),
                $"{name}: a failed backup cannot change the game's career or options.");
            check.That(!File.Exists(Path.Combine(outside, Backups.ManifestName)), $"{name}: no manifest escapes the selected backup root.");
            if (scenario is "linked-folder" or "replacement-folder")
                check.That(completed is not null && !File.Exists(Path.Combine(completed, Backups.ManifestName)) &&
                    File.Exists(Path.Combine(retained, "Career One.bes")) &&
                    File.ReadAllBytes(Path.Combine(retained, "Career One.bes")).AsSpan().SequenceEqual(original),
                    $"{name}: a replaced directory gets no manifest and the real copied bytes are retained.");
            if (scenario == "manifest-collision")
                check.That(completed is not null && File.Exists(Path.Combine(completed, Backups.ManifestName)) &&
                    File.ReadAllText(Path.Combine(completed, Backups.ManifestName)) == "Owned preexisting manifest; keep it.",
                    $"{name}: manifest publication never overwrites an existing file.");
        }
    }

    private sealed class AfterBackupCopies(IProtectedSaveFiles inner, int count, Action<string> afterCopies) : IProtectedSaveFiles
    {
        private int _copies;
        public ProtectedRead OpenCareer(string path) => inner.OpenCareer(path);
        public PublicationReceipt PublishCopy(string input, string identity, string hash, string output, byte[] prepared)
        {
            PublicationReceipt receipt = inner.PublishCopy(input, identity, hash, output, prepared);
            if (receipt.Ok && ++_copies == count) afterCopies(Path.GetDirectoryName(output)!);
            return receipt;
        }
    }

    /// <summary>
    /// Where the swap cannot be checked, a career is not replaced at all; and once a file is in place, a
    /// later failure is reported as a possible change, never as "nothing was written", and the file is
    /// left alone rather than deleted or retried.
    /// </summary>
    private static void PublicationBoundary(byte[] original, string root, DateTime now, ProtectedSaveFiles files, Checks check)
    {
        FakeInstall install = FakeInstall.Create(Path.Combine(root, "boundary"), original);
        string backups = Path.Combine(root, "boundary-backups");
        Directory.CreateDirectory(backups);
        byte[] edited = original.ToArray();
        edited[0x2406] ^= 0x5A;
        GameInstaller.ExchangeUnsupported = true;
        try
        {
            InstallReceipt refused = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Career One.bes", edited, backups,
                () => false, now);
            check.That(refused is { Ok: false, MayHaveChanged: false } && Unchanged(install, original) && Leftovers(install).Length == 0,
                "Without RENAME_EXCHANGE a career is not replaced, and nothing is left in savegames.");
            InstallReceipt added = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Added Anyway.bes", edited, backups,
                () => false, now.AddSeconds(1));
            check.That(added.Ok && File.ReadAllBytes(Path.Combine(install.Game, "savegames", "Added Anyway.bes")).AsSpan().SequenceEqual(edited),
                "Without RENAME_EXCHANGE a new career is still added with its no-clobber link.");
        }
        finally
        {
            GameInstaller.ExchangeUnsupported = false;
        }
        LateFailures(install, edited, backups, now.AddSeconds(2), files, check, "Linux path");
    }

    /// <summary>A failure injected just after the file is in place, for a new career and for a replacement.</summary>
    private static void LateFailures(FakeInstall install, byte[] edited, string backups, DateTime now, ProtectedSaveFiles files, Checks check,
        string path)
    {
        static void Fail() => throw new IOException("injected failure after the file was in place");
        string late = Path.Combine(install.Game, "savegames", "Late Fault.bes");
        InstallReceipt added = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Late Fault.bes", edited, backups,
            () => false, now, afterPublish: Fail);
        check.That(added is { Ok: false, MayHaveChanged: true, BackupFolder: not null } && !added.Message.Contains("Nothing was written") &&
            File.Exists(late) && File.ReadAllBytes(late).AsSpan().SequenceEqual(edited),
            $"{path}: a failure after a new career is in place is reported as a possible change, and the career is kept.");
        byte[] before = File.ReadAllBytes(install.Career);
        InstallReceipt replaced = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Career One.bes", edited, backups,
            () => false, now.AddSeconds(1), afterPublish: Fail);
        check.That(replaced is { Ok: false, MayHaveChanged: true, BackupFolder: string backup } && !replaced.Message.Contains("Nothing was written") &&
            File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(edited) &&
            File.ReadAllBytes(Path.Combine(backup, "Career One.bes")).AsSpan().SequenceEqual(before),
            $"{path}: a failure after a replacement is reported as a possible change; the new bytes stay and the backup holds the old.");
    }

    /// <summary>A replacement from an opened career is refused when the game saved that career since; backups record why.</summary>
    private static void ChangeGuards(byte[] original, string root, DateTime now, ProtectedSaveFiles files, Checks check)
    {
        FakeInstall install = FakeInstall.Create(Path.Combine(root, "guards"), original);
        string backups = Path.Combine(root, "guard-backups");
        Directory.CreateDirectory(backups);
        GameFolder game = GameFolder.Inspect(install.Game, "test");
        byte[] edited = original.ToArray();
        edited[0x2406] ^= 0x5A;
        string opened = Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(original)).ToLowerInvariant();
        byte[] saved = original.ToArray();
        saved[^1] ^= 1;
        File.WriteAllBytes(install.Career, saved);
        InstallReceipt stale = GameInstaller.Install(files, game, "Career One.bes", edited, backups, () => false, now, expectedSha256: opened,
            reason: "Before changing Career One");
        check.That(!stale.Ok && stale.Message.Contains("changed since you opened it") && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(saved),
            "A career the game saved after it was opened is not replaced.");
        check.That(Backups.List(backups).FirstOrDefault()?.Reason == "Before changing Career One", "A backup set records why it was made.");
        File.WriteAllBytes(install.Career, original);
        InstallReceipt fresh = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Career One.bes", edited, backups,
            () => false, now.AddSeconds(1), expectedSha256: opened);
        check.That(fresh.Ok && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(edited), "An unchanged career is replaced as asked.");
        InstallReceipt gone = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Missing.bes", edited, backups,
            () => false, now.AddSeconds(2), expectedSha256: opened);
        check.That(!gone.Ok && !File.Exists(Path.Combine(install.Game, "savegames", "Missing.bes")),
            "A career that is no longer in the game is not recreated by a replacement.");

        check.That(Backups.ChangedSinceLatest(GameFolder.Inspect(install.Game, "test"), Path.Combine(root, "no-backups-yet")),
            "With no backups yet, there is always something to back up.");
        BackupReceipt set = Backups.Create(files, GameFolder.Inspect(install.Game, "test"), backups, now.AddSeconds(3), "Automatic backup");
        check.That(set.Ok && !Backups.ChangedSinceLatest(GameFolder.Inspect(install.Game, "test"), backups),
            "Right after a backup, nothing has changed.");
        File.WriteAllBytes(install.Options, edited);
        check.That(Backups.ChangedSinceLatest(GameFolder.Inspect(install.Game, "test"), backups), "A changed file is noticed.");
    }

    /// <summary>
    /// The write path used on Windows, run here through the same cases: a new career, a replacement, a file
    /// changed after its backup, and a file that takes the name just before the swap.
    /// </summary>
    private static void PortableWrites(byte[] original, string root, DateTime now, ProtectedSaveFiles files, Checks check)
    {
        GameInstaller.UsePortableInstall = true;
        try
        {
            FakeInstall install = FakeInstall.Create(Path.Combine(root, "portable"), original);
            string backups = Path.Combine(root, "portable-backups");
            Directory.CreateDirectory(backups);
            byte[] edited = original.ToArray();
            edited[0x2406] ^= 0x5A;
            InstallReceipt added = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Fresh.bes", edited, backups,
                () => false, now);
            string fresh = Path.Combine(install.Game, "savegames", "Fresh.bes");
            check.That(added is { Ok: true, Replaced: false } && File.ReadAllBytes(fresh).AsSpan().SequenceEqual(edited) && Leftovers(install).Length == 0,
                "Portable path: a new career is added and verified, leaving nothing behind.");
            InstallReceipt replaced = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Career One.bes", edited, backups,
                () => false, now.AddSeconds(2));
            check.That(replaced is { Ok: true, Replaced: true } && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(edited) &&
                replaced.BackupFolder is string backup && File.ReadAllBytes(Path.Combine(backup, "Career One.bes")).AsSpan().SequenceEqual(original) &&
                Leftovers(install).Length == 0, "Portable path: a career is replaced after a backup of its earlier bytes.");
            byte[] other = original.ToArray();
            other[^1] ^= 1;
            InstallReceipt changed = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Career One.bes", original, backups,
                () => false, now.AddSeconds(3), beforeCheck: () => File.WriteAllBytes(install.Career, other));
            check.That(!changed.Ok && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(other) && Leftovers(install).Length == 0,
                "Portable path: a career changed after its backup is refused and left as it is.");
            byte[] racer = other.ToArray();
            racer[^2] ^= 1;
            InstallReceipt raced = GameInstaller.Install(files, GameFolder.Inspect(install.Game, "test"), "Career One.bes", original, backups,
                () => false, now.AddSeconds(4), beforeSwap: () => File.WriteAllBytes(install.Career, racer));
            check.That(raced is { Ok: false, MayHaveChanged: true } && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(racer) &&
                Leftovers(install).Length == 0, "Portable path: a file written just before the swap is put back, and ours withdrawn.");
            LateFailures(install, edited, backups, now.AddSeconds(5), files, check, "Portable path");
        }
        finally
        {
            GameInstaller.UsePortableInstall = false;
        }
    }

    private static bool Unchanged(FakeInstall install, byte[] original) =>
        File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original) && File.ReadAllBytes(install.Options).AsSpan().SequenceEqual(original);

    private static string[] Leftovers(FakeInstall install) =>
        Directory.GetFiles(Path.Combine(install.Game, "savegames"), ".onslaught-*").Concat(
            Directory.GetFiles(install.Game, ".onslaught-*")).ToArray();
}
