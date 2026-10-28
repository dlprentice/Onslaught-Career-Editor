// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Settings recovery copies remain bound through publication; every file here is authored test data.</summary>
internal static class CeSettingsBackupTests
{
    internal static void Run(string output, Checks check)
    {
        if (!OperatingSystem.IsLinux()) return; // These adversarial rename/link controls need Linux.
        check.Suite("CE settings backup binding");
        foreach (bool portable in new[] { false, true })
        {
            bool previous = GameInstaller.UsePortableInstall;
            GameInstaller.UsePortableInstall = portable;
            try
            {
                foreach (string mode in new[] { "control", "corrupt-before-swap", "replace-before-swap",
                    "link-directory-before-swap", "corrupt-at-running-check", "corrupt-after-publish", "absence-before-swap" })
                    Case(output, check, portable, mode);
            }
            finally { GameInstaller.UsePortableInstall = previous; }
        }
    }

    private static void Case(string output, Checks check, bool portable, string mode)
    {
        string root = Path.Combine(output, "ce-settings-backup-binding", portable ? "portable" : "linux", mode);
        string user = Path.Combine(root, "user"), backups = Path.Combine(root, "backups"), outside = Path.Combine(root, "outside");
        Directory.CreateDirectory(user); Directory.CreateDirectory(backups); Directory.CreateDirectory(outside);
        string ini = Path.Combine(user, "ce.ini");
        const string original = "# unknown retained\r\nupdate_check=1\r\nrecord_sessions=0\r\nother=unchanged";
        const string edited = "# unknown retained\r\nupdate_check=0\r\nrecord_sessions=1\r\nother=unchanged";
        bool absent = mode == "absence-before-swap";
        if (!absent) File.WriteAllText(ini, original);
        CeSettings settings = CeSettings.Read(user).Value ?? throw new InvalidOperationException("Fixture settings could not be opened.");
        string backupName = absent ? "ce.ini.did-not-exist.txt" : "ce.ini";
        void Alter()
        {
            string set = Directory.GetDirectories(backups, "onslaught-ce-settings-*").Single();
            string copy = Path.Combine(set, backupName);
            if (mode == "replace-before-swap")
            {
                File.Move(copy, Path.Combine(root, "retained-copy"));
                File.WriteAllText(copy, "replacement");
            }
            else if (mode == "link-directory-before-swap")
            {
                Directory.Move(set, Path.Combine(root, "retained-set"));
                Directory.CreateSymbolicLink(set, outside);
            }
            else File.WriteAllText(copy, "changed recovery bytes");
        }
        int runningChecks = 0;
        bool Running()
        {
            if (++runningChecks == 2 && mode == "corrupt-at-running-check") Alter();
            return false;
        }
        bool before = mode.EndsWith("before-swap", StringComparison.Ordinal);
        bool after = mode == "corrupt-after-publish";
        InstallReceipt result = settings.Save(false, true, backups, Running, new DateTime(2026, 10, 28),
            beforeSwap: before ? Alter : null, afterPublish: after ? Alter : null);
        string description = (portable ? "portable" : "Linux") + " " + mode;
        check.That(result.Ok == (mode == "control") && result.MayHaveChanged == after,
            description + ": only an intact recovery copy permits success; post-publication loss is uncertain.");
        check.That(absent ? !File.Exists(ini) : File.ReadAllText(ini) == (mode == "control" || after ? edited : original),
            description + ": pre-publication failures preserve the exact source, and later failure leaves the published file for inspection.");
        if (after)
            check.That(result.BackupFolder is not null && result.Message.Contains("recovery backup could not be verified", StringComparison.Ordinal),
                description + ": the uncertain result states that the recovery backup is not verified.");
        if (mode == "control")
            check.That(result.BackupFolder is string folder && File.ReadAllText(Path.Combine(folder, backupName)) == original,
                description + ": the receipt identifies an intact, reopenable recovery copy.");
    }
}
