// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Runtime.InteropServices;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Cooperative lock and publication controls on authored settings and directories only.</summary>
internal static class CeSettingsWriteLockTests
{
    private const string Initial = "update_check=1\nrecord_sessions=0\nunknown=keep\n";
    private const string Changed = "update_check=0\nrecord_sessions=1\nunknown=keep\n";
    private static readonly DateTime Now = new(2026, 10, 28, 0, 0, 0, DateTimeKind.Utc);

    internal static void Run(string output, Checks check)
    {
        if (!OperatingSystem.IsLinux() && !OperatingSystem.IsWindows()) return;
        check.Suite("CE cooperative settings lock");
        string root = Path.Combine(output, "ce-settings-cooperative-lock");
        BusyRefuses(root, check);
        HeldAcrossTransaction(root, check);
        StaleSnapshotRefuses(root, check);
        FailedWriteReleases(root, check);
        if (OperatingSystem.IsLinux())
        {
            foreach (bool portable in new[] { false, true })
            {
                bool previous = GameInstaller.UsePortableInstall;
                GameInstaller.UsePortableInstall = portable;
                try { ReplacedLock(root, check, portable, afterPublish: false); ReplacedLock(root, check, portable, afterPublish: true); }
                finally { GameInstaller.UsePortableInstall = previous; }
            }
            foreach (string kind in new[] { "symlink", "hardlink", "fifo", "directory" }) UnsafeLock(root, check, kind);
        }
    }

    private static (string User, string Backup, string Ini, string Lock) Fixture(string root, string name)
    {
        string folder = Path.Combine(root, name), user = Path.Combine(folder, "user"), backup = Path.Combine(folder, "backup");
        Directory.CreateDirectory(user); Directory.CreateDirectory(backup);
        string ini = Path.Combine(user, "ce.ini"), fileLock = Path.Combine(user, "ce.ini.lock");
        File.WriteAllText(ini, Initial);
        return (user, backup, ini, fileLock);
    }

    private static CeSettings Read(string user) => CeSettings.Read(user).Value ?? throw new IOException("Authored settings could not be read.");

    private static void BusyRefuses(string root, Checks check)
    {
        var f = Fixture(root, "busy");
        CeSettings snapshot = Read(f.User);
        using CeSettingsWriteLock holder = CeSettingsWriteLock.TryAcquire(f.User) ?? throw new IOException("Fixture lock was busy.");
        Stopwatch time = Stopwatch.StartNew();
        InstallReceipt result = snapshot.Save(false, true, f.Backup, () => false, Now);
        time.Stop();
        check.That(!result.Ok && !result.MayHaveChanged && result.Message.Contains("another program", StringComparison.Ordinal),
            "A contended sidecar refuses a settings save with a retry message.");
        check.That(time.Elapsed < TimeSpan.FromSeconds(3), "Contention is bounded rather than waiting for the holder.");
        check.That(File.ReadAllText(f.Ini) == Initial && Directory.GetFileSystemEntries(f.Backup).Length == 0,
            "A busy lock leaves settings and backup folder unchanged.");
        check.That(File.Exists(f.Lock), "The sidecar remains in place while locked.");
    }

    private static void HeldAcrossTransaction(string root, Checks check)
    {
        var f = Fixture(root, "transaction");
        bool beforeCheck = false, beforeSwap = false, afterPublish = false;
        void Probe(ref bool observed)
        {
            using CeSettingsWriteLock? competitor = CeSettingsWriteLock.TryAcquire(f.User);
            observed = competitor is null;
        }
        int externalWhileLocked = -1;
        InstallReceipt result = Read(f.User).Save(false, true, f.Backup, () => false, Now,
            beforeCheck: () => Probe(ref beforeCheck),
            beforeSwap: () => { Probe(ref beforeSwap); if (OperatingSystem.IsLinux()) externalWhileLocked = ExternalFlock(f.Lock); },
            afterPublish: () => Probe(ref afterPublish));
        check.That(result.Ok && beforeCheck && beforeSwap && afterPublish,
            "The sidecar stays locked through stale check, staging, swap, and post-publication verification.");
        check.That(File.ReadAllText(f.Ini) == Changed && result.BackupFolder is string folder &&
            File.ReadAllText(Path.Combine(folder, "ce.ini")) == Initial,
            "A successful locked save retains unknown settings and its verified original backup.");
        using (CeSettingsWriteLock? after = CeSettingsWriteLock.TryAcquire(f.User))
            check.That(after is not null && File.Exists(f.Lock), "The lock is released after saving; its sidecar is not deleted.");
        if (OperatingSystem.IsLinux())
            check.That(externalWhileLocked == 1 && ExternalFlock(f.Lock) == 0,
                "An independent flock process sees the transaction as busy, then can acquire the released sidecar.");
    }

    private static void StaleSnapshotRefuses(string root, Checks check)
    {
        var f = Fixture(root, "stale");
        CeSettings old = Read(f.User);
        const string peer = "update_check=1\nrecord_sessions=0\nunknown=peer-change\n";
        using (CeSettingsWriteLock holder = CeSettingsWriteLock.TryAcquire(f.User) ?? throw new IOException("Fixture lock was busy."))
            File.WriteAllText(f.Ini, peer);
        InstallReceipt result = old.Save(false, true, f.Backup, () => false, Now);
        check.That(!result.Ok && File.ReadAllText(f.Ini) == peer && Directory.GetFileSystemEntries(f.Backup).Length == 0,
            "A stale UI snapshot refuses after a cooperating peer completes its write.");
    }

    private static void FailedWriteReleases(string root, Checks check)
    {
        var f = Fixture(root, "failed-write");
        InstallReceipt result = Read(f.User).Save(false, true, f.Backup, () => false, Now,
            beforeSwap: () => throw new IOException("authored refusal"));
        using CeSettingsWriteLock? after = CeSettingsWriteLock.TryAcquire(f.User);
        check.That(!result.Ok && !result.MayHaveChanged && after is not null && File.ReadAllText(f.Ini) == Initial && File.Exists(f.Lock),
            "A pre-publication failure releases the persistent lock and leaves the original settings in place.");
    }

    private static void ReplacedLock(string root, Checks check, bool portable, bool afterPublish)
    {
        string name = (portable ? "portable" : "linux") + (afterPublish ? "-lock-replaced-after" : "-lock-replaced-before");
        var f = Fixture(root, name);
        void Replace()
        {
            File.Move(f.Lock, f.Lock + ".retained-original");
            File.WriteAllText(f.Lock, "replacement");
        }
        InstallReceipt result = Read(f.User).Save(false, true, f.Backup, () => false, Now,
            beforeSwap: afterPublish ? null : Replace, afterPublish: afterPublish ? Replace : null);
        check.That(!result.Ok && result.MayHaveChanged == afterPublish &&
            File.ReadAllText(f.Ini) == (afterPublish ? Changed : Initial),
            name + ": sidecar replacement before publication is refused; replacement after it is reported as uncertain.");
        check.That(result.BackupFolder is string folder && File.ReadAllText(Path.Combine(folder, "ce.ini")) == Initial,
            name + ": the original backup remains available after refusing or reporting uncertainty.");
    }

    private static void UnsafeLock(string root, Checks check, string kind)
    {
        var f = Fixture(root, "unsafe-" + kind);
        string other = Path.Combine(f.User, "authored-other");
        File.WriteAllText(other, "do not change");
        if (kind == "symlink") File.CreateSymbolicLink(f.Lock, other);
        else if (kind == "hardlink" && Link(other, f.Lock) != 0) throw new IOException("Could not create fixture hard link.");
        else if (kind == "fifo" && MkFifo(f.Lock, 0x180) != 0) throw new IOException("Could not create fixture FIFO.");
        else if (kind == "directory") Directory.CreateDirectory(f.Lock);
        InstallReceipt result = Read(f.User).Save(false, true, f.Backup, () => false, Now);
        check.That(!result.Ok && !result.MayHaveChanged && File.ReadAllText(f.Ini) == Initial &&
            File.ReadAllText(other) == "do not change" && Directory.GetFileSystemEntries(f.Backup).Length == 0,
            kind + " lock files fail closed without altering the settings, linked file or backups.");
    }

    private static int ExternalFlock(string path)
    {
        ProcessStartInfo start = new("/usr/bin/flock") { UseShellExecute = false, CreateNoWindow = true };
        foreach (string argument in new[] { "-x", "-n", path, "/usr/bin/true" }) start.ArgumentList.Add(argument);
        using Process process = Process.Start(start) ?? throw new IOException("The authored flock contender did not start.");
        if (!process.WaitForExit(3000)) throw new IOException($"The authored flock contender timed out; inspect PID {process.Id}.");
        return process.ExitCode;
    }

    [DllImport("libc", EntryPoint = "link", SetLastError = true)]
    private static extern int Link([MarshalAs(UnmanagedType.LPUTF8Str)] string oldPath, [MarshalAs(UnmanagedType.LPUTF8Str)] string newPath);

    [DllImport("libc", EntryPoint = "mkfifo", SetLastError = true)]
    private static extern int MkFifo([MarshalAs(UnmanagedType.LPUTF8Str)] string path, uint mode);
}
