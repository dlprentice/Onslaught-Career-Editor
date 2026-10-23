// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;
using System.Text;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>The career publisher also carries small settings files, without relaxing its default or its race checks.</summary>
internal static class CeAtomicWriteTests
{
    internal static void Run(byte[] originalCareer, string outputDirectory, Checks check)
    {
        check.Suite("CE atomic settings publication");
        foreach (bool linux in OperatingSystem.IsLinux() ? new[] { false, true } : new[] { false })
        {
            string root = Path.Combine(outputDirectory, "ce-atomic", linux ? "linux" : "portable");
            Directory.CreateDirectory(root);
            byte[] original = Encoding.UTF8.GetBytes("# keep me\nupdate_check=1\nfuture_setting=untouched\n");
            byte[] prepared = Encoding.UTF8.GetBytes("# keep me\nupdate_check=0\nfuture_setting=untouched\nrecord_sessions=1\n");
            byte[] raced = Encoding.UTF8.GetBytes("update_check=1\n");
            string backup = Path.Combine(root, "backups");
            Directory.CreateDirectory(backup);
            File.WriteAllBytes(Path.Combine(backup, "ce.ini"), original);

            InstallReceipt Write(string target, string? prior, Action? beforeCheck = null, Action? beforeSwap = null,
                Action? afterPublish = null, bool careerReader = false) => linux
                ? LinuxInstall.Write(target, prepared, prior, backup, beforeCheck, beforeSwap, afterPublish,
                    careerReader ? null : ReadSmallFile)
                : PortableInstall.Write(target, prepared, prior, backup, beforeCheck, beforeSwap, afterPublish,
                    careerReader ? null : ReadSmallFile);

            string created = Path.Combine(root, "new.ini");
            InstallReceipt added = Write(created, null);
            check.That(added is { Ok: true, Replaced: false } && Same(created, prepared),
                $"{linux}: the same publisher creates and verifies variable-length settings bytes.");
            string replaced = Path.Combine(root, "replace.ini");
            File.WriteAllBytes(replaced, original);
            InstallReceipt replacement = Write(replaced, Hash(original));
            check.That(replacement is { Ok: true, Replaced: true } && Same(replaced, prepared),
                $"{linux}: a backed-up settings file is atomically replaced and read back.");
            check.That(Same(Path.Combine(backup, "ce.ini"), original), $"{linux}: publication never changes the verified backup.");

            string strict = Path.Combine(root, "strict-reader.ini");
            check.That(Refused(() => Write(strict, null, careerReader: true)) && !File.Exists(strict),
                $"{linux}: callers omitting the settings reader still require a complete 10,004-byte career.");
            check.That(Directory.GetFiles(root, ".onslaught-*").Length == 0,
                $"{linux}: successful writes and the rejected default-reader stage leave no temporary files.");

            string stale = Path.Combine(root, "stale.ini");
            File.WriteAllBytes(stale, original);
            check.That(Refused(() => Write(stale, Hash(original), beforeCheck: () => File.WriteAllBytes(stale, raced))) && Same(stale, raced),
                $"{linux}: bytes changed after backup and before validation are preserved and the write is refused.");

            string inPlace = Path.Combine(root, "in-place.ini");
            File.WriteAllBytes(inPlace, original);
            InstallReceipt inPlaceRace = Write(inPlace, Hash(original), beforeSwap: () => File.WriteAllBytes(inPlace, raced));
            check.That(inPlaceRace is { Ok: false, MayHaveChanged: true } && Same(inPlace, raced),
                $"{linux}: a same-inode write with a changed length immediately before the swap is rolled back intact.");

            string rebound = Path.Combine(root, "rebound.ini");
            string retained = Path.Combine(root, "rebound-retained.ini");
            File.WriteAllBytes(rebound, original);
            InstallReceipt reboundRace = Write(rebound, Hash(original), beforeSwap: () =>
            {
                File.Move(rebound, retained);
                File.WriteAllBytes(rebound, raced);
            });
            check.That(reboundRace is { Ok: false, MayHaveChanged: true } && Same(rebound, raced) && Same(retained, original),
                $"{linux}: a different file taking the target name before exchange is restored, and the earlier file remains.");

            string occupied = Path.Combine(root, "occupied.ini");
            check.That(Refused(() => Write(occupied, null, beforeSwap: () => File.WriteAllBytes(occupied, raced))) && Same(occupied, raced),
                $"{linux}: a new-file publication never overwrites a file that appeared while it was prepared.");

            string twice = Path.Combine(root, "changed-twice.ini");
            byte[] newest = Encoding.UTF8.GetBytes("record_sessions=0\n# newer writer\n");
            File.WriteAllBytes(twice, original);
            InstallReceipt doubleRace = Write(twice, Hash(original), beforeSwap: () => File.WriteAllBytes(twice, raced),
                afterPublish: () => File.WriteAllBytes(twice, newest));
            check.That(doubleRace is { Ok: false, MayHaveChanged: true } && Same(twice, newest),
                $"{linux}: rollback cannot overwrite a second writer's newer published target; it reports uncertainty.");
            check.That(Directory.GetFiles(root, ".onslaught-*").Any(path => Same(path, raced)),
                $"{linux}: the displaced unbacked bytes remain available when safe rollback cannot be established.");

            // The same-inode fix applies to the original career route too, including a change to an unsupported length.
            string career = Path.Combine(root, "career.bes");
            File.WriteAllBytes(career, originalCareer);
            byte[] changedCareer = originalCareer.ToArray();
            changedCareer[^1] ^= 1;
            InstallReceipt careerRace = linux
                ? LinuxInstall.Write(career, changedCareer, Hash(originalCareer), backup, null, () => File.WriteAllBytes(career, raced), null)
                : PortableInstall.Write(career, changedCareer, Hash(originalCareer), backup, null, () => File.WriteAllBytes(career, raced), null);
            check.That(careerRace is { Ok: false, MayHaveChanged: true } && Same(career, raced),
                $"{linux}: a career truncated during publication is restored rather than accepted or discarded.");

            if (OperatingSystem.IsLinux())
            {
                string linkTarget = Path.Combine(root, "link-target.ini"), symbolic = Path.Combine(root, "symbolic.ini");
                File.WriteAllBytes(linkTarget, original);
                File.CreateSymbolicLink(symbolic, linkTarget);
                check.That(Refused(() => Write(symbolic, Hash(original))) && Same(linkTarget, original),
                    $"{linux}: settings publication refuses a symbolic-link target.");
                string hard = Path.Combine(root, "hard.ini");
                int linked = LinuxSaveNative.LinkAt(LinuxSaveNative.AtCurrentDirectory, linkTarget,
                    LinuxSaveNative.AtCurrentDirectory, hard, 0);
                check.That(linked == 0 && Refused(() => Write(hard, Hash(original))) && Same(linkTarget, original),
                    $"{linux}: settings publication refuses a target with another hard link.");
            }
        }
    }

    private static byte[] ReadSmallFile(FileStream stream)
    {
        if (stream.Length > 4096) throw new IOException("The settings file is too large.");
        byte[] bytes = new byte[checked((int)stream.Length)];
        stream.Position = 0;
        stream.ReadExactly(bytes);
        if (stream.ReadByte() != -1) throw new IOException("The settings file changed while reading.");
        return bytes;
    }

    private static bool Refused(Func<InstallReceipt> write)
    {
        try { return !write().Ok; }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidOperationException) { return true; }
    }

    private static bool Same(string path, byte[] bytes) => File.Exists(path) && File.ReadAllBytes(path).AsSpan().SequenceEqual(bytes);
    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes));
}
