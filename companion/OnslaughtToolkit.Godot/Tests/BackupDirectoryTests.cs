// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Actual backup/game-writer boundary on copies of the tracked career, never a player folder.</summary>
internal static class BackupDirectoryTests
{
    internal static void Run(byte[] original, string root, DateTime now, Checks check)
    {
        if (!OperatingSystem.IsLinux()) return; // The rename/link controls below require Linux.
        check.Suite("backup directory binding");
        foreach (GameTarget target in new[] { GameTarget.Original, GameTarget.OnslaughtCe })
        foreach (bool portable in new[] { false, true })
        {
            bool previous = GameInstaller.UsePortableInstall;
            GameInstaller.UsePortableInstall = portable;
            try
            {
                foreach (string mode in new[] { "control", "link-after-copy", "directory-after-copy", "root-after-copy",
                    "link-before-swap", "directory-before-swap", "corrupt-copy-before-swap", "corrupt-manifest-before-swap",
                    "link-at-running-check", "corrupt-copy-at-running-check",
                    "link-after-publish", "corrupt-copy-after-publish", "corrupt-manifest-after-publish" })
                    InstallCase(original, root, now, check, target, portable, mode);
                foreach (bool replaceWithLink in new[] { false, true })
                    BackupCase(original, root, now, check, target, portable, replaceWithLink);
            }
            finally { GameInstaller.UsePortableInstall = previous; }
        }
    }

    private static void InstallCase(byte[] original, string root, DateTime now, Checks check,
        GameTarget target, bool portable, string mode)
    {
        string name = $"{target}/{(portable ? "portable" : "native")}/{mode}";
        string owner = Path.Combine(root, "backup-binding", name);
        FakeInstall install = FakeInstall.Create(Path.Combine(owner, "game"), original);
        if (target == GameTarget.OnslaughtCe) File.Delete(Path.Combine(install.Game, "BEA.exe")); // CE's user folder is not a retail install.
        GameFolder game = target == GameTarget.Original ? GameFolder.Inspect(install.Game, "fixture") : GameFolder.InspectCe(install.Game);
        string backups = Path.Combine(owner, "backups"), outside = Path.Combine(owner, "outside");
        Directory.CreateDirectory(backups); Directory.CreateDirectory(outside);
        byte[] edited = original.ToArray(); edited[0x2406] ^= 0x5A;
        SwapAfterCopy files = new(mode.EndsWith("after-copy", StringComparison.Ordinal), folder =>
            Change(folder, mode, backups, outside, owner), game.Careers.Count(file => file.Supported) + (game.Options is { Supported: true } ? 1 : 0));
        void ChangeLatest() => Change(Directory.GetDirectories(backups, "onslaught-backup-*").Single(), mode, backups, outside, owner);
        int runningChecks = 0;
        bool Running()
        {
            if (++runningChecks == 2 && mode.EndsWith("at-running-check", StringComparison.Ordinal)) ChangeLatest();
            return false;
        }
        InstallReceipt result = GameInstaller.Install(files, game, "Career One.bes", edited, backups, Running, now,
            beforeSwap: mode.EndsWith("before-swap", StringComparison.Ordinal) ? ChangeLatest : null,
            afterPublish: mode.EndsWith("after-publish", StringComparison.Ordinal) ? ChangeLatest : null);
        bool after = mode.EndsWith("after-publish", StringComparison.Ordinal);
        check.That(result.Ok == (mode == "control") && result.MayHaveChanged == after,
            name + ": only an intact backup permits success; a post-publication loss reports possible change");
        check.That(File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(mode == "control" || after ? edited : original),
            name + ": pre-publication failure preserves every original byte; a later failure leaves the published career for inspection");
        string options = Path.Combine(install.Game, "defaultoptions.bea");
        check.That(File.ReadAllBytes(options).AsSpan().SequenceEqual(original), name + ": all unselected settings bytes remain unchanged");
        check.That(!File.Exists(Path.Combine(outside, Backups.ManifestName)), name + ": no manifest escapes through a replaced directory");
        if (after)
            check.That(result.BackupFolder is not null && result.Message.Contains("recovery backup could not be verified", StringComparison.Ordinal) &&
                !result.Message.Contains("backup holds", StringComparison.Ordinal),
                name + ": an uncertain result names the failed recovery verification without promising that the compromised backup is usable");
        if (mode == "control")
            check.That(result.BackupFolder is string folder &&
                File.ReadAllBytes(Path.Combine(folder, "Career One.bes")).AsSpan().SequenceEqual(original) &&
                Backups.List(backups, game).Count == 1, name + ": the successful set remains reopenable at its receipt path");
    }

    private static void BackupCase(byte[] original, string root, DateTime now, Checks check,
        GameTarget target, bool portable, bool replaceWithLink)
    {
        string owner = Path.Combine(root, "backup-binding-direct", $"{target}-{portable}-{replaceWithLink}");
        FakeInstall install = FakeInstall.Create(Path.Combine(owner, "game"), original);
        if (target == GameTarget.OnslaughtCe) File.Delete(Path.Combine(install.Game, "BEA.exe"));
        GameFolder game = target == GameTarget.Original ? GameFolder.Inspect(install.Game, "fixture") : GameFolder.InspectCe(install.Game);
        string backups = Path.Combine(owner, "backups"), outside = Path.Combine(owner, "outside");
        Directory.CreateDirectory(backups); Directory.CreateDirectory(outside);
        SwapAfterCopy files = new(true, folder => Change(folder, replaceWithLink ? "link-after-copy" : "directory-after-copy", backups, outside, owner), game.Careers.Count(file => file.Supported) + (game.Options is { Supported: true } ? 1 : 0));
        BackupReceipt result = Backups.Create(files, game, backups, now);
        check.That(!result.Ok && result.Set is null && result.PartialFolder is not null &&
            !File.Exists(Path.Combine(outside, Backups.ManifestName)) &&
            File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original),
            $"{target}/{portable}/{replaceWithLink}: direct backup refuses a changed directory before manifest publication and leaves the source intact");
    }

    private static void Change(string folder, string mode, string backups, string outside, string owner)
    {
        if (mode.StartsWith("corrupt-copy", StringComparison.Ordinal))
        {
            string path = Path.Combine(folder, "Career One.bes"); byte[] bytes = File.ReadAllBytes(path);
            bytes[^1] ^= 0x5A; File.WriteAllBytes(path, bytes); return;
        }
        if (mode.StartsWith("corrupt-manifest", StringComparison.Ordinal))
        { File.AppendAllText(Path.Combine(folder, Backups.ManifestName), "\nchanged"); return; }
        if (mode.StartsWith("root-", StringComparison.Ordinal))
        {
            Directory.Move(backups, Path.Combine(owner, "retained-root"));
            Directory.CreateSymbolicLink(backups, outside); return;
        }
        Directory.Move(folder, Path.Combine(owner, "retained-set")); // Preserve the exact recovery files.
        if (mode.StartsWith("link-", StringComparison.Ordinal)) Directory.CreateSymbolicLink(folder, outside);
        else Directory.CreateDirectory(folder);
    }

    private sealed class SwapAfterCopy(bool change, Action<string> action, int copies) : IProtectedSaveFiles
    {
        private readonly ProtectedSaveFiles _inner = new();
        private int _copies;
        public ProtectedRead OpenCareer(string input) => _inner.OpenCareer(input);
        public PublicationReceipt PublishCopy(string input, string identity, string sha256, string output, byte[] prepared)
        {
            PublicationReceipt result = _inner.PublishCopy(input, identity, sha256, output, prepared);
            if (result.Ok && change && ++_copies == copies) action(Path.GetDirectoryName(output)!);
            return result;
        }
    }
}
