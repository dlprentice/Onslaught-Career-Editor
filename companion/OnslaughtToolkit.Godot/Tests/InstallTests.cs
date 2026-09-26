// SPDX-License-Identifier: MIT
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
            "Even a new file is preceded by a verified backup of every career and the options file.");

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
        PortableWrites(original, root, now, files, check);
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
