// SPDX-License-Identifier: MIT
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;
using OnslaughtCareerEditor.AppCore;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Files;

public sealed record BackupFile(string Name, string Original, long Size, string Sha256);

public sealed record BackupSet(string Folder, DateTime Created, string Game, IReadOnlyList<BackupFile> Files);

public sealed record BackupReceipt(bool Ok, string Message, BackupSet? Set = null, string? PartialFolder = null);

/// <summary>
/// The outcome of a write into the game folder. <see cref="MayHaveChanged"/> means the game folder may
/// differ from before and must be inspected; the named backup holds the verified earlier bytes.
/// </summary>
public sealed record InstallReceipt(bool Ok, string Message, string Target, string? BackupFolder = null,
    bool Replaced = false, bool MayHaveChanged = false, string? Sha256 = null, bool Exchanged = false);

/// <summary>Whether the game is running; the companion never writes into its folder while it is.</summary>
public static class GameProcess
{
    public static bool IsRunning()
    {
        try
        {
            if (OperatingSystem.IsWindows()) return System.Diagnostics.Process.GetProcessesByName("BEA").Length > 0;
            foreach (string folder in Directory.EnumerateDirectories("/proc"))
            {
                if (!int.TryParse(Path.GetFileName(folder), out _)) continue;
                try
                {
                    // Under Proton the game's arguments name BEA.exe with a Windows-style path.
                    foreach (string argument in File.ReadAllText(Path.Combine(folder, "cmdline")).Split('\0'))
                    {
                        if (argument.EndsWith("BEA.exe", StringComparison.OrdinalIgnoreCase)) return true;
                    }
                }
                catch (Exception error) when (error is IOException or UnauthorizedAccessException)
                {
                }
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
        }
        return false;
    }
}

/// <summary>
/// Verified backup sets: a new folder of protected, no-clobber copies of every supported career and
/// the options file, with a manifest of their hashes. A backup never overwrites or deletes anything.
/// </summary>
public static class Backups
{
    public const string ManifestName = "onslaught-backup.json";
    private static readonly JsonSerializerOptions Json = new() { WriteIndented = true };

    public static BackupReceipt Create(IProtectedSaveFiles files, GameFolder game, string root, DateTime now)
    {
        if (!Path.IsPathFullyQualified(root) || !Directory.Exists(root))
            return new BackupReceipt(false, "Choose an existing backup folder.");
        if (SteamLibraries.Canonical(root) is not string realRoot || IsInside(realRoot, game.Root))
            return new BackupReceipt(false, "Choose a backup folder outside the game folder.");
        string folder = Path.Combine(realRoot, $"onslaught-backup-{now:yyyyMMdd-HHmmss}");
        for (int suffix = 2; Path.Exists(folder); suffix++)
            folder = Path.Combine(realRoot, $"onslaught-backup-{now:yyyyMMdd-HHmmss}-{suffix}");
        try
        {
            Directory.CreateDirectory(folder);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return new BackupReceipt(false, "The backup folder could not be created: " + error.Message);
        }
        List<BackupFile> saved = [];
        IEnumerable<GameFile> sources = game.Careers.Where(file => file.Supported);
        if (game.Options is { Supported: true } options) sources = sources.Append(options);
        foreach (GameFile file in sources)
        {
            ProtectedRead read = files.OpenCareer(file.Path);
            if (!read.Ok || read.Bytes is not byte[] bytes)
                return new BackupReceipt(false, $"{file.Name} could not be read for the backup: {read.Message} Nothing in the game changed.",
                    PartialFolder: folder);
            PublicationReceipt copy = files.PublishCopy(file.Path, read.Identity, read.Sha256, Path.Combine(folder, file.Name), bytes);
            if (!copy.Ok)
                return new BackupReceipt(false, $"{file.Name} could not be backed up: {copy.Message} Nothing in the game changed.",
                    PartialFolder: folder);
            saved.Add(new BackupFile(file.Name, file.Path, bytes.Length, copy.Sha256.ToLowerInvariant()));
        }
        BackupSet set = new(folder, now, game.Root, saved);
        try
        {
            using FileStream manifest = new(Path.Combine(folder, ManifestName), FileMode.CreateNew, FileAccess.Write);
            JsonSerializer.Serialize(manifest, set, Json);
            manifest.Flush(flushToDisk: true);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return new BackupReceipt(false, "The copies were verified but the manifest could not be written: " + error.Message,
                PartialFolder: folder);
        }
        int skipped = game.Careers.Count(file => !file.Supported) + (game.Options is { Supported: false } ? 1 : 0);
        return new BackupReceipt(true, $"Backed up and verified {saved.Count} file{(saved.Count == 1 ? "" : "s")}" +
            (skipped > 0 ? $"; {skipped} unsupported file{(skipped == 1 ? " was" : "s were")} left untouched" : "") + ".", set);
    }

    /// <summary>Backup sets found in a folder, newest first. Folders without a readable manifest are ignored.</summary>
    public static IReadOnlyList<BackupSet> List(string root)
    {
        List<BackupSet> sets = [];
        try
        {
            if (!Directory.Exists(root)) return sets;
            foreach (string folder in Directory.GetDirectories(root, "onslaught-backup-*"))
            {
                try
                {
                    string manifest = Path.Combine(folder, ManifestName);
                    if (File.Exists(manifest) && JsonSerializer.Deserialize<BackupSet>(File.ReadAllText(manifest)) is BackupSet set)
                        sets.Add(set with { Folder = folder });
                }
                catch (Exception error) when (error is IOException or UnauthorizedAccessException or JsonException)
                {
                }
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
        }
        return sets.OrderByDescending(set => set.Created).ToArray();
    }

    internal static bool IsInside(string path, string folder)
    {
        StringComparison comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        string parent = Path.TrimEndingDirectorySeparator(folder) + Path.DirectorySeparatorChar;
        return string.Equals(Path.TrimEndingDirectorySeparator(path), Path.TrimEndingDirectorySeparator(folder), comparison) ||
            path.StartsWith(parent, comparison);
    }
}

/// <summary>
/// Writes into the game folder, the one place the companion changes the player's install. Only a
/// career in <c>savegames/</c> or <c>defaultoptions.bea</c> can be written, never while the game runs,
/// and only after a verified backup of every career and the options file. Replacing a file checks it
/// still matches its backup, then swaps atomically and verifies both sides of the swap.
/// </summary>
public static class GameInstaller
{
    public const string OptionsName = "defaultoptions.bea";

    public static InstallReceipt Install(IProtectedSaveFiles files, GameFolder game, string targetName, byte[] prepared,
        string backupRoot, Func<bool> gameRunning, DateTime now, Action? beforeCheck = null, Action? beforeSwap = null)
    {
        // The page's list may be stale; every decision below uses a fresh read of the folder.
        if (!GameFolder.LooksLikeGame(game.Root))
            return new InstallReceipt(false, "The game folder is no longer there.", targetName);
        game = GameFolder.Inspect(game.Root, game.Source);
        string target = Target(game, targetName) ?? "";
        if (target.Length == 0)
            return new InstallReceipt(false, "Only a .bes career in the game's savegames folder, or defaultoptions.bea, can be written.", targetName);
        if (!OperatingSystem.IsLinux())
            return new InstallReceipt(false, "Writing into the game folder has only been tested on Linux so far. Copy the verified file " +
                "yourself, or use Linux.", target);
        if (gameRunning())
            return new InstallReceipt(false, "Battle Engine Aquila is running. Close the game first; it writes these files itself.", target);
        if (!CareerSave.Inspect(prepared).Ok)
            return new InstallReceipt(false, "That file is not a supported 10,004-byte career; nothing was written.", target);
        if (!Directory.Exists(Path.GetDirectoryName(target)))
            return new InstallReceipt(false, "The game has no savegames folder yet. Save a career in the game once, then try again.", target);
        FileInfo existing = new(target);
        if (existing.LinkTarget is not null)
            return new InstallReceipt(false, "The file in the game folder is a link; replace it yourself after checking where it points.", target);
        GameFile? current = game.Careers.Append(game.Options).OfType<GameFile>()
            .FirstOrDefault(file => string.Equals(file.Path, target, StringComparison.Ordinal));
        if (existing.Exists && current is not { Supported: true })
            return new InstallReceipt(false, "The file being replaced is not a supported career, so no verified backup of it can be made. " +
                "Nothing was written.", target);

        BackupReceipt backup = Backups.Create(files, game, backupRoot, now);
        if (backup.Set is not BackupSet set)
            return new InstallReceipt(false, "No verified backup could be made, so nothing was written. " + backup.Message, target,
                backup.PartialFolder);
        BackupFile? saved = set.Files.FirstOrDefault(file => file.Name == Path.GetFileName(target));
        if (existing.Exists && saved is null)
            return new InstallReceipt(false, "The backup does not contain the file being replaced, so nothing was written.", target, set.Folder);
        try
        {
            return LinuxInstall.Write(target, prepared, saved?.Sha256, set.Folder, beforeCheck, beforeSwap);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or Win32Exception or InvalidOperationException)
        {
            return new InstallReceipt(false, $"Nothing was written: {error.Message}", target, set.Folder);
        }
    }

    /// <summary>The full target path for an allowed name, or null.</summary>
    public static string? Target(GameFolder game, string name)
    {
        if (string.Equals(name, OptionsName, StringComparison.OrdinalIgnoreCase)) return game.OptionsPath;
        if (name.Length is < 5 or > 128 || !name.EndsWith(".bes", StringComparison.OrdinalIgnoreCase) ||
            PortableNameProblem(name[..^4]) is not null)
            return null;
        return Path.Combine(game.SavegamesPath, name);
    }

    /// <summary>
    /// Why a career name cannot be used in the game's folder on every system, or null. The game runs
    /// under Windows rules even through Proton, so Windows-invalid characters are refused everywhere.
    /// </summary>
    public static string? PortableNameProblem(string name)
    {
        if (name.Length == 0) return "Type a name.";
        if (name.Trim() != name || name.StartsWith('.') || name.EndsWith('.'))
            return "A name cannot start or end with a space or a dot.";
        if (name.Any(character => character < ' ' || "<>:\"/\\|?*".Contains(character)))
            return "A name cannot contain < > : \" / \\ | ? * or control characters.";
        return null;
    }
}

/// <summary>
/// The Linux side of a game-folder write, on descriptor-relative, link-refusing handles reused from the
/// linked MIT safety source (LinuxSaveNative). New files are published with a no-clobber link; replaced
/// files are swapped with renameat2(RENAME_EXCHANGE) so the displaced file can be identified and the
/// swap undone if it was not the backed-up original.
/// </summary>
internal static class LinuxInstall
{
    private const uint RenameExchange = 2;
    private const int NotSupported = 22, NoSystemCall = 38, NotDirectoryTypeSupported = 95;

    internal static InstallReceipt Write(string target, byte[] prepared, string? backedUpSha256, string backupFolder,
        Action? beforeCheck, Action? beforeSwap)
    {
        string name = Path.GetFileName(target);
        using Folder folder = Folder.Open(Path.GetDirectoryName(target)!);
        using FileStream staged = folder.CreateUnnamed();
        staged.Write(prepared);
        staged.Flush(flushToDisk: true);
        LinuxSaveNative.Stat stagedStat = LinuxSaveNative.Inspect(staged.SafeFileHandle);
        if (!SaveLabSource.ReadSaveBytes(staged).AsSpan().SequenceEqual(prepared))
            throw new IOException("The staged copy did not match the prepared bytes.");
        beforeCheck?.Invoke();

        if (backedUpSha256 is null)
        {
            folder.RequireVacant(name);
            beforeSwap?.Invoke();
            folder.RequireVacant(name);
            folder.Link(staged.SafeFileHandle, name);
            return Verified(folder, target, name, prepared, stagedStat, backupFolder, replaced: false, exchanged: false);
        }

        (LinuxSaveNative.Stat original, byte[] originalBytes) = folder.ReadCareer(name);
        if (!string.Equals(Hash(originalBytes), backedUpSha256, StringComparison.OrdinalIgnoreCase))
            throw new IOException($"{name} changed after it was backed up. Back up again before writing.");
        string temporary = $".onslaught-install-{Guid.NewGuid():N}.tmp";
        folder.RequireVacant(temporary);
        folder.Link(staged.SafeFileHandle, temporary);
        bool exchanged;
        try
        {
            (LinuxSaveNative.Stat again, byte[] againBytes) = folder.ReadCareer(name);
            if (again.Identity != original.Identity || !againBytes.AsSpan().SequenceEqual(originalBytes))
                throw new IOException($"{name} changed after it was backed up. Back up again before writing.");
            beforeSwap?.Invoke();
            exchanged = folder.TryExchange(temporary, name);
            if (!exchanged) folder.Replace(temporary, name);
        }
        catch
        {
            // Nothing was swapped: the temporary name still holds only our staged copy.
            folder.RemoveOwn(temporary, stagedStat);
            throw;
        }

        if (exchanged)
        {
            LinuxSaveNative.Stat displaced = folder.Inspect(temporary);
            if (displaced.Identity != original.Identity)
            {
                // Another file took the name between the check and the swap: put it back and withdraw ours.
                folder.TryExchange(temporary, name);
                folder.RemoveOwn(temporary, stagedStat);
                return new InstallReceipt(false, $"{name} was replaced by another program during the write. It was put back " +
                    "unchanged and nothing was installed.", target, backupFolder, MayHaveChanged: true);
            }
            folder.RemoveOwn(temporary, original);
        }
        return Verified(folder, target, name, prepared, stagedStat, backupFolder, replaced: true, exchanged);
    }

    private static InstallReceipt Verified(Folder folder, string target, string name, byte[] prepared, LinuxSaveNative.Stat staged,
        string backupFolder, bool replaced, bool exchanged)
    {
        folder.Flush();
        (LinuxSaveNative.Stat written, byte[] bytes) = folder.ReadCareer(name);
        if (written.Identity != staged.Identity || !bytes.AsSpan().SequenceEqual(prepared))
            return new InstallReceipt(false, "The write finished but the file in the game folder did not verify. Inspect it; the backup " +
                "holds the earlier bytes.", target, backupFolder, replaced, MayHaveChanged: true);
        return new InstallReceipt(true, (replaced ? "Replaced and verified" : "Added and verified") +
            $" {name}. The earlier files are in the verified backup.", target, backupFolder, replaced, Sha256: Hash(bytes), Exchanged: exchanged);
    }

    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

    /// <summary>A folder opened component by component without following links.</summary>
    private sealed class Folder : IDisposable
    {
        private readonly SafeFileHandle _handle;
        private readonly string _path;
        private readonly string _identity;

        private Folder(string path, SafeFileHandle handle) => (_path, _handle, _identity) = (path, handle, LinuxSaveNative.Inspect(handle).Identity);

        private int Descriptor => _handle.DangerousGetHandle().ToInt32();

        internal static Folder Open(string path)
        {
            string full = Path.GetFullPath(path);
            SafeFileHandle current = LinuxSaveNative.OpenAt(LinuxSaveNative.AtCurrentDirectory, "/", LinuxSaveNative.ReadDirectory, 0);
            try
            {
                foreach (string segment in full.Split('/', StringSplitOptions.RemoveEmptyEntries))
                {
                    SafeFileHandle next = LinuxSaveNative.OpenAt(current.DangerousGetHandle().ToInt32(), segment, LinuxSaveNative.ReadDirectory, 0);
                    current.Dispose();
                    current = next;
                }
                return new Folder(full, current);
            }
            catch
            {
                current.Dispose();
                throw;
            }
        }

        internal (LinuxSaveNative.Stat Stat, byte[] Bytes) ReadCareer(string name)
        {
            VerifyFolder();
            SafeFileHandle handle = LinuxSaveNative.OpenAt(Descriptor, name, LinuxSaveNative.ReadFile, 0);
            using FileStream stream = new(handle, FileAccess.Read);
            LinuxSaveNative.Stat stat = LinuxSaveNative.Inspect(handle);
            LinuxSaveNative.RequireRegular(stat, links: 1);
            return (stat, SaveLabSource.ReadSaveBytes(stream));
        }

        internal LinuxSaveNative.Stat Inspect(string name)
        {
            SafeFileHandle handle = LinuxSaveNative.OpenAt(Descriptor, name, LinuxSaveNative.ReadFile, 0);
            using FileStream stream = new(handle, FileAccess.Read);
            return LinuxSaveNative.Inspect(handle);
        }

        internal FileStream CreateUnnamed()
        {
            SafeFileHandle handle = LinuxSaveNative.OpenAt(Descriptor, ".", LinuxSaveNative.UnnamedFile, 0x1A4); // 0644, as the game's own files
            try
            {
                LinuxSaveNative.RequireRegular(LinuxSaveNative.Inspect(handle), links: 0);
                return new FileStream(handle, FileAccess.ReadWrite);
            }
            catch
            {
                handle.Dispose();
                throw;
            }
        }

        internal void RequireVacant(string name)
        {
            int result = LinuxSaveNative.StatAt(Descriptor, name, LinuxSaveNative.NoFollow, LinuxSaveNative.RequiredStatMask, out _);
            int error = Marshal.GetLastWin32Error();
            if (result == 0) throw new IOException($"{name} already exists; nothing was replaced.");
            if (error != 2) throw LinuxSaveNative.Failure("The game folder could not be inspected safely.", error);
        }

        internal void Link(SafeFileHandle staged, string name)
        {
            VerifyFolder();
            if (LinuxSaveNative.LinkAt(LinuxSaveNative.AtCurrentDirectory, $"/proc/self/fd/{staged.DangerousGetHandle().ToInt32()}",
                Descriptor, name, 0x400) != 0)
                throw LinuxSaveNative.Failure($"{name} could not be created without replacing another entry.", Marshal.GetLastWin32Error());
        }

        internal bool TryExchange(string first, string second)
        {
            VerifyFolder();
            if (RenameAt2(Descriptor, first, Descriptor, second, RenameExchange) == 0) return true;
            int error = Marshal.GetLastWin32Error();
            if (error is NotSupported or NoSystemCall or NotDirectoryTypeSupported) return false;
            throw LinuxSaveNative.Failure("The files could not be swapped safely.", error);
        }

        internal void Replace(string source, string destination)
        {
            VerifyFolder();
            if (RenameAt2(Descriptor, source, Descriptor, destination, 0) != 0)
                throw LinuxSaveNative.Failure("The file could not be replaced atomically.", Marshal.GetLastWin32Error());
        }

        /// <summary>Removes a name only if it still names the expected file (our staged copy or the backed-up original).</summary>
        internal void RemoveOwn(string name, LinuxSaveNative.Stat expected)
        {
            try
            {
                if (Inspect(name).Identity != expected.Identity) return;
            }
            catch (IOException)
            {
                return;
            }
            if (UnlinkAt(Descriptor, name, 0) != 0)
                throw LinuxSaveNative.Failure($"The temporary entry {name} could not be removed; it can be deleted by hand.", Marshal.GetLastWin32Error());
        }

        internal void Flush()
        {
            if (LinuxSaveNative.Sync(Descriptor) != 0)
                throw LinuxSaveNative.Failure("The game folder could not be flushed to storage.", Marshal.GetLastWin32Error());
        }

        private void VerifyFolder()
        {
            using Folder current = Open(_path);
            if (current._identity != _identity) throw new IOException("The game folder changed during the write. Nothing further was done.");
        }

        public void Dispose() => _handle.Dispose();

        [DllImport("libc", EntryPoint = "renameat2", SetLastError = true)]
        private static extern int RenameAt2(int oldDirectory, [MarshalAs(UnmanagedType.LPUTF8Str)] string oldName,
            int newDirectory, [MarshalAs(UnmanagedType.LPUTF8Str)] string newName, uint flags);

        [DllImport("libc", EntryPoint = "unlinkat", SetLastError = true)]
        private static extern int UnlinkAt(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string name, int flags);
    }
}
