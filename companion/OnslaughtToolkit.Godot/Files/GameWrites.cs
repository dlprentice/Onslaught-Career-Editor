// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.Win32.SafeHandles;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Files;

public sealed record BackupFile(string Name, string Original, long Size, string Sha256);

/// <summary>A verified backup set. <see cref="Reason"/> says why it was made, in the player's words.</summary>
public sealed record BackupSet(string Folder, DateTime Created, string Game, IReadOnlyList<BackupFile> Files, string? Reason = null);

public sealed record BackupReceipt(bool Ok, string Message, BackupSet? Set = null, string? PartialFolder = null);

/// <summary>
/// The outcome of a write into the game folder. <see cref="MayHaveChanged"/> means the game folder may
/// differ from before and must be inspected; the named backup holds the verified earlier bytes.
/// </summary>
public sealed record InstallReceipt(bool Ok, string Message, string Target, string? BackupFolder = null,
    bool Replaced = false, bool MayHaveChanged = false, string? Sha256 = null, bool Exchanged = false);

/// <summary>
/// Whether the game is running: the original game, or Onslaught CE, which reads the same install's careers. The
/// companion never writes into the game folder while either runs.
/// </summary>
public static class GameProcess
{
    public static bool IsRunning() => Running().Count > 0;

    /// <summary>The processes the check counts as the game, as "pid: name (first argument) game"; read-only.</summary>
    public static IReadOnlyList<string> Running()
    {
        List<string> found = [];
        try
        {
            // Windows names a process after its program: BEA covers the original game and CE's bea.exe alike.
            if (OperatingSystem.IsWindows())
                return System.Diagnostics.Process.GetProcessesByName("BEA").Select(process => $"{process.Id}: {process.ProcessName} (the game)")
                    .Concat(System.Diagnostics.Process.GetProcessesByName("onslaught-ce")
                        .Select(process => $"{process.Id}: {process.ProcessName} (Onslaught CE)")).ToArray();
            foreach (string folder in Directory.EnumerateDirectories("/proc"))
            {
                if (!int.TryParse(Path.GetFileName(folder), out int pid)) continue;
                try
                {
                    string comm = File.ReadAllText(Path.Combine(folder, "comm"));
                    string[] argv = File.ReadAllText(Path.Combine(folder, "cmdline")).Split('\0', StringSplitOptions.RemoveEmptyEntries);
                    string first = argv.Length > 0 ? argv[0] : "";
                    if (IsGame(comm, argv)) found.Add($"{pid}: {comm.Trim()} ({first}) original game");
                    else if (IsOnslaughtCe(comm, argv, Program(folder), File.Exists)) found.Add($"{pid}: {comm.Trim()} ({first}) Onslaught CE");
                }
                catch (Exception error) when (error is IOException or UnauthorizedAccessException)
                {
                }
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidOperationException)
        {
        }
        return found;
    }

    /// <summary>
    /// Whether a Linux process is the game itself. Wine names a Windows program's process after its
    /// executable (comm <c>BEA.exe</c>) and shows its Windows path as argv[0]; a Wine loader may carry the
    /// path as an argument while it starts. A tool that only names the file (a disassembler, a hash, a
    /// copy) is not the game. Seen on 2026-09-26 with the Steam game under Proton: the game's process has
    /// comm <c>BEA.exe</c> and argv[0] <c>S:\steamapps\common\Battle Engine Aquila\BEA.exe</c>, while
    /// Steam's <c>steam.exe</c> shim, the Proton script and the runtime wrapper, which name the file, are not
    /// counted.
    /// </summary>
    public static bool IsGame(string comm, IReadOnlyList<string> argv)
    {
        if (comm.Trim().Equals("BEA.exe", StringComparison.OrdinalIgnoreCase)) return true;
        if (argv.Count == 0) return false;
        if (IsExecutable(argv[0])) return true;
        return FileName(argv[0]).StartsWith("wine", StringComparison.OrdinalIgnoreCase) && argv.Skip(1).Any(IsExecutable);
    }

    /// <summary>
    /// Whether a Linux process is Onslaught CE: its launcher, or its game program <c>bea</c> started from a CE package
    /// folder (<see cref="OnslaughtCe.IsCeProgram"/>). The program is read from <c>/proc/PID/exe</c>; when that cannot be
    /// read, argv[0] counts only if it is a full path, so a relative <c>./bea</c> is never resolved against the
    /// companion's own folder. A program replaced or deleted while it runs (a CE update) reads as
    /// <c>/…/bea (deleted)</c>: the suffix is dropped, and a full-path argv[0] is tried as well, so a running CE whose
    /// files changed under it still counts.
    /// </summary>
    public static bool IsOnslaughtCe(string comm, IReadOnlyList<string> argv, string? program, Func<string, bool> fileExists)
    {
        const string deleted = " (deleted)";
        if (program is not null && program.EndsWith(deleted, StringComparison.Ordinal)) program = program[..^deleted.Length];
        string? first = argv.Count > 0 && Path.IsPathFullyQualified(argv[0]) ? argv[0] : null;
        return OnslaughtCe.IsCeProgram(comm, program ?? first, fileExists) ||
            (program is not null && first is not null && first != program && OnslaughtCe.IsCeProgram(comm, first, fileExists));
    }

    private static string? Program(string procFolder)
    {
        try
        {
            return new FileInfo(Path.Combine(procFolder, "exe")).LinkTarget;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    private static bool IsExecutable(string argument) => FileName(argument).Equals("BEA.exe", StringComparison.OrdinalIgnoreCase);

    private static string FileName(string path) => path[(path.LastIndexOfAny(['/', '\\']) + 1)..];
}

/// <summary>
/// Verified backup sets: a new folder of protected, no-clobber copies of every supported career and
/// the options file, with a manifest of their hashes. A backup never overwrites or deletes anything.
/// </summary>
public static class Backups
{
    public const string ManifestName = "onslaught-backup.json";
    private static readonly JsonSerializerOptions Json = new() { WriteIndented = true };

    public static BackupReceipt Create(IProtectedSaveFiles files, GameFolder game, string root, DateTime now, string reason = "Backup")
    {
        if (!Path.IsPathFullyQualified(root) || !Directory.Exists(root))
            return new BackupReceipt(false, "Choose an existing backup folder.");
        if (SteamLibraries.Canonical(root) is not string realRoot || (IsInside(realRoot, game.Root) || IsInside(realRoot, game.AssetRoot)))
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
        BackupSet set = new(folder, now, game.Root, saved, reason);
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

    /// <summary>
    /// Whether any career or the options file differs from the newest backup set made from this game folder (a
    /// file added, removed or changed), so an automatic backup is only made when there is something new. Sets
    /// made from another game folder in the same backup folder are not compared. Reads only.
    /// </summary>
    public static bool ChangedSinceLatest(GameFolder game, string root)
    {
        if (List(root, game).FirstOrDefault() is not BackupSet latest) return true;
        Dictionary<string, string> backed = latest.Files.ToDictionary(file => file.Name, file => file.Sha256, StringComparer.Ordinal);
        List<GameFile> current = [.. game.Careers.Where(file => file.Supported)];
        if (game.Options is { Supported: true } options) current.Add(options);
        if (current.Count != backed.Count) return true;
        foreach (GameFile file in current)
        {
            try
            {
                if (!backed.TryGetValue(file.Name, out string? sha) ||
                    !string.Equals(Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(file.Path))), sha, StringComparison.OrdinalIgnoreCase))
                    return true;
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
                return true;
            }
        }
        return false;
    }

    /// <summary>Backup sets in a folder that were made from this game folder, newest first.</summary>
    public static IReadOnlyList<BackupSet> List(string root, GameFolder game) => List(root).Where(set => SameGame(set, game)).ToArray();

    /// <summary>
    /// Whether a backup set was made from this game folder: its manifest's game root names the same folder. A set
    /// from another install never stands in for this one's latest backup, and is put back into this one only after the
    /// player confirms a prompt naming both folders.
    /// </summary>
    public static bool SameGame(BackupSet set, GameFolder game) => SameRoot(set.Game, game.Root);

    internal static bool SameRoot(string? recorded, string root)
    {
        if (string.IsNullOrWhiteSpace(recorded) || !Path.IsPathFullyQualified(recorded)) return false;
        StringComparison comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        static string Normal(string path) => Path.TrimEndingDirectorySeparator(Path.GetFullPath(path));
        return string.Equals(Normal(recorded), Normal(root), comparison) ||
            SteamLibraries.Canonical(recorded) is string real && SteamLibraries.Canonical(root) is string current &&
            string.Equals(Normal(real), Normal(current), comparison);
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
/// career in <c>savegames/</c> or <c>defaultoptions.bea</c> can be written, never while the game runs
/// (checked before the backup and again just before the swap), and only after a verified backup of every
/// career and the options file. Replacing a file checks it
/// still matches its backup, then swaps atomically and verifies both sides of the swap.
/// </summary>
public static partial class GameInstaller
{
    public const string OptionsName = "defaultoptions.bea";

    /// <summary>Runs the portable write path on Linux as well; tests use it to check that path's logic.</summary>
    internal static bool UsePortableInstall { get; set; }

    /// <summary>Makes the Linux swap report RENAME_EXCHANGE as unsupported; tests use it to check that case.</summary>
    internal static bool ExchangeUnsupported { get; set; }

    /// <param name="expectedSha256">
    /// For a replacement made from a career the player opened: the content they opened. If the file in the
    /// game differs (the game saved it since), nothing is written.
    /// </param>
    public static InstallReceipt Install(IProtectedSaveFiles files, GameFolder game, string targetName, byte[] prepared,
        string backupRoot, Func<bool> gameRunning, DateTime now, Action? beforeCheck = null, Action? beforeSwap = null,
        string? expectedSha256 = null, string reason = "Before a change to your game", Action? afterPublish = null)
    {
        // The page's list may be stale; every decision below uses a fresh read of the folder.
        if (!game.IsAvailable)
            return new InstallReceipt(false, "The game folder is no longer there.", targetName);
        game = game.Refresh();
        string target = Target(game, targetName) ?? "";
        if (target.Length == 0)
            return new InstallReceipt(false, "Only a .bes career in the game's savegames folder, or defaultoptions.bea, can be written.", targetName);
        if (game.Target == GameTarget.OnslaughtCe)
        {
            try { FileMutationSafety.RejectOutputInGameTree(target); }
            catch (Exception error) when (error is IOException or InvalidOperationException or UnauthorizedAccessException)
            { return new InstallReceipt(false, error.Message, target); }
        }
        if (gameRunning())
            return new InstallReceipt(false, RunningMessage, target);
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

        if (expectedSha256 is not null && !existing.Exists)
            return new InstallReceipt(false, $"{Path.GetFileName(target)} is no longer in your game, so it was not replaced.", target);
        BackupReceipt backup = Backups.Create(files, game, backupRoot, now, reason);
        if (backup.Set is not BackupSet set)
            return new InstallReceipt(false, "No verified backup could be made, so nothing was written. " + backup.Message, target,
                backup.PartialFolder);
        BackupFile? saved = set.Files.FirstOrDefault(file => file.Name == Path.GetFileName(target));
        if (existing.Exists && saved is null)
            return new InstallReceipt(false, "The backup does not contain the file being replaced, so nothing was written.", target, set.Folder);
        if (expectedSha256 is not null && !string.Equals(saved?.Sha256, expectedSha256, StringComparison.OrdinalIgnoreCase))
            return new InstallReceipt(false, $"{Path.GetFileNameWithoutExtension(target)} has changed since you opened it; the game probably " +
                "saved it. Nothing was written. Open it again to change the latest version.", target, set.Folder);
        try
        {
            // Each writer handles every failure after its file is in place itself (AfterPublication), so an
            // exception reaching this catch happened before anything in the game folder was published.
            // The backup takes a while; the game may have started meanwhile, so each writer checks again just before
            // its swap or link, after its last change check, and refuses with nothing written.
            Action beforeSwapChecked = () =>
            {
                beforeSwap?.Invoke();
                if (gameRunning()) throw new GameStartedException();
            };
            return OperatingSystem.IsLinux() && !UsePortableInstall
                ? LinuxInstall.Write(target, prepared, saved?.Sha256, set.Folder, beforeCheck, beforeSwapChecked, afterPublish)
                : PortableInstall.Write(target, prepared, saved?.Sha256, set.Folder, beforeCheck, beforeSwapChecked, afterPublish);
        }
        catch (GameStartedException)
        {
            return new InstallReceipt(false, "The game started while the backup was being made, so nothing was written. " + RunningMessage,
                target, set.Folder);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or Win32Exception or InvalidOperationException)
        {
            return new InstallReceipt(false, $"Nothing was written: {error.Message}", target, set.Folder);
        }
    }

    /// <summary>
    /// Runs the steps after a file was published into the game folder. Any failure there is reported as a
    /// possible change, with the target and the backup: the file is left as it is, never deleted or retried.
    /// </summary>
    internal static InstallReceipt AfterPublication(string target, string backupFolder, bool replaced, Func<InstallReceipt> steps)
    {
        try
        {
            return steps();
        }
        catch (Exception error)
        {
            string name = Path.GetFileName(target);
            return new InstallReceipt(false, $"{name} was written into your game, but a check afterwards failed ({error.Message}). " +
                $"It may not hold what you saved, and it was left as it is. Look at {name} before playing; the backup holds the " +
                "earlier files.", target, backupFolder, replaced, MayHaveChanged: true);
        }
    }

    internal const string RunningMessage = "Battle Engine Aquila or Onslaught CE is running. Close the game first; it writes these files itself.";

    /// <summary>Raised by the check just before the swap; nothing in the game folder has changed when it is.</summary>
    private sealed class GameStartedException() : IOException("The game started during the write.");

    /// <summary>The full target path for an allowed name, or null.</summary>
    public static string? Target(GameFolder game, string name)
    {
        if (string.Equals(name, OptionsName, StringComparison.OrdinalIgnoreCase))
            return game.Target == GameTarget.Original ? game.OptionsPath : null;
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
        if (ReservedWindowsName().IsMatch(name))
            return "Windows keeps that name for devices; choose another.";
        return null;
    }

    [GeneratedRegex(@"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?$", RegexOptions.IgnoreCase)]
    private static partial Regex ReservedWindowsName();
}

/// <summary>
/// The game-folder write on every system but Linux, in portable .NET file calls: the prepared bytes are
/// staged and verified beside the target; a new file is moved into place without replacing anything;
/// a replaced file is swapped with <see cref="File.Replace(string, string, string?, bool)"/>, which keeps
/// the displaced file under a temporary name so it can be compared with the backed-up original and the
/// swap undone if another program changed it in between. On Windows the folder's ancestors are held by
/// FileMutationSafety's directory locks. Tests run this same path on Linux to check its logic; it
/// has not been executed on Windows.
/// </summary>
internal static class PortableInstall
{
    /// <summary>
    /// Publishes bytes already admitted by the caller. The default reader requires a complete career;
    /// settings callers supply their own bounded reader, used for every comparison and the final read-back.
    /// The caller supplies the verified backup hash and checks the running game in <paramref name="beforeSwap"/>.
    /// </summary>
    internal static InstallReceipt Write(string target, byte[] prepared, string? backedUpSha256, string backupFolder,
        Action? beforeCheck, Action? beforeSwap, Action? afterPublish, Func<FileStream, byte[]>? readBytes = null)
    {
        readBytes ??= SaveLabSource.ReadSaveBytes;
        using FileMutationSafety.DirectoryLockSet locks = FileMutationSafety.LockDirectoryTree(Path.GetDirectoryName(target)!, "Game folder");
        string folder = locks.PhysicalPath;
        string name = Path.GetFileName(target);
        string destination = Path.Combine(folder, name);
        string staged = Path.Combine(folder, $".onslaught-install-{Guid.NewGuid():N}.tmp");
        try
        {
            using (FileStream stream = new(staged, FileMode.CreateNew, FileAccess.ReadWrite, FileShare.None, 4096, FileOptions.WriteThrough))
            {
                stream.Write(prepared);
                stream.Flush(flushToDisk: true);
                if (!readBytes(stream).AsSpan().SequenceEqual(prepared))
                    throw new IOException("The staged copy did not match the prepared bytes.");
            }
            beforeCheck?.Invoke();
            if (backedUpSha256 is null)
            {
                RequireVacant(destination, name);
                beforeSwap?.Invoke();
                RequireVacant(destination, name);
                File.Move(staged, destination, overwrite: false);
                return GameInstaller.AfterPublication(target, backupFolder, replaced: false, () =>
                {
                    afterPublish?.Invoke();
                    return Verified(destination, name, prepared, target, backupFolder, replaced: false, readBytes);
                });
            }

            FileMutationSafety.RejectReparsePoint(destination, "Game file");
            if (!string.Equals(Hash(ReadFile(destination, readBytes)), backedUpSha256, StringComparison.OrdinalIgnoreCase))
                throw new IOException($"{name} changed after it was backed up. Back up again before writing.");
            beforeSwap?.Invoke();
            string displaced = Path.Combine(folder, $".onslaught-displaced-{Guid.NewGuid():N}.tmp");
            try
            {
                File.Replace(staged, destination, displaced, ignoreMetadataErrors: true);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
                // A failed swap usually changes nothing; if the original is no longer in place, say so.
                if (string.Equals(TryHash(destination, readBytes), backedUpSha256, StringComparison.OrdinalIgnoreCase)) throw;
                return new InstallReceipt(false, $"{name} could not be swapped cleanly ({error.Message}). Check the game folder; the " +
                    "backup holds the earlier files.", target, backupFolder, MayHaveChanged: true);
            }
            return GameInstaller.AfterPublication(target, backupFolder, replaced: true, () =>
            {
                afterPublish?.Invoke();
                if (!string.Equals(TryHash(displaced, readBytes), backedUpSha256, StringComparison.OrdinalIgnoreCase))
                {
                    // Another program wrote the file between the check and the swap: put its file back and withdraw ours.
                    // If it has also changed our published file, preserve both files for inspection instead of overwriting it.
                    if (!string.Equals(TryHash(destination, readBytes), Hash(prepared), StringComparison.OrdinalIgnoreCase))
                        throw new IOException("The published file changed before rollback; the displaced file was kept at " + displaced);
                    string withdrawn = Path.Combine(folder, $".onslaught-withdrawn-{Guid.NewGuid():N}.tmp");
                    File.Replace(displaced, destination, withdrawn, ignoreMetadataErrors: true);
                    File.Delete(withdrawn);
                    return new InstallReceipt(false, $"{name} was replaced by another program during the write. It was put back " +
                        "unchanged and nothing was installed.", target, backupFolder, MayHaveChanged: true);
                }
                File.Delete(displaced);
                return Verified(destination, name, prepared, target, backupFolder, replaced: true, readBytes);
            });
        }
        finally
        {
            // Only our own staged name can still be here, if the move or swap did not happen.
            if (File.Exists(staged)) File.Delete(staged);
        }
    }

    private static InstallReceipt Verified(string destination, string name, byte[] prepared, string target, string backupFolder, bool replaced,
        Func<FileStream, byte[]> readBytes)
    {
        byte[] bytes = ReadFile(destination, readBytes);
        if (!bytes.AsSpan().SequenceEqual(prepared))
            return new InstallReceipt(false, "The write finished but the file in the game folder did not verify. Inspect it; the backup " +
                "holds the earlier bytes.", target, backupFolder, replaced, MayHaveChanged: true);
        return new InstallReceipt(true, (replaced ? "Replaced and verified" : "Added and verified") +
            $" {name}. The earlier files are in the verified backup.", target, backupFolder, replaced, Sha256: Hash(bytes));
    }

    private static void RequireVacant(string destination, string name)
    {
        if (File.Exists(destination) || Directory.Exists(destination) || new FileInfo(destination).LinkTarget is not null)
            throw new IOException($"{name} already exists; nothing was replaced.");
    }

    private static byte[] ReadFile(string path, Func<FileStream, byte[]> readBytes)
    {
        if (OperatingSystem.IsLinux())
        {
            using LinuxSaveDirectory directory = LinuxSaveDirectory.Open(Path.GetDirectoryName(path)!);
            using FileStream stream = directory.OpenRead(Path.GetFileName(path));
            LinuxSaveNative.RequireRegular(LinuxSaveNative.Inspect(stream.SafeFileHandle), links: 1);
            byte[] bytes = readBytes(stream);
            directory.Verify();
            return bytes;
        }
        using SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(path, "Game file");
        WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, "Game file");
        if (identity.IsReparsePoint || identity.NumberOfLinks != 1)
            throw new IOException("The game file must be a regular file without links.");
        using FileStream source = new(handle, FileAccess.Read);
        return readBytes(source);
    }

    private static string? TryHash(string path, Func<FileStream, byte[]> readBytes)
    {
        try
        {
            return File.Exists(path) ? Hash(ReadFile(path, readBytes)) : null;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
}

/// <summary>
/// The Linux side of a game-folder write, on descriptor-relative, link-refusing handles from the
/// companion's safety source (LinuxSaveNative). New files are published with a no-clobber link; replaced
/// files are swapped with renameat2(RENAME_EXCHANGE) so the displaced file can be identified and the
/// swap undone if it was not the backed-up original. Where the filesystem has no exchange, a replacement is
/// refused before anything changes; new files are still published.
/// </summary>
internal static class LinuxInstall
{
    private const uint RenameExchange = 2;
    private const int NotSupported = 22, NoSystemCall = 38, NotDirectoryTypeSupported = 95;

    /// <summary>Same contract as <see cref="PortableInstall.Write"/>, using descriptor-relative Linux publication.</summary>
    internal static InstallReceipt Write(string target, byte[] prepared, string? backedUpSha256, string backupFolder,
        Action? beforeCheck, Action? beforeSwap, Action? afterPublish, Func<FileStream, byte[]>? readBytes = null)
    {
        readBytes ??= SaveLabSource.ReadSaveBytes;
        string name = Path.GetFileName(target);
        using Folder folder = Folder.Open(Path.GetDirectoryName(target)!);
        using FileStream staged = folder.CreateUnnamed();
        staged.Write(prepared);
        staged.Flush(flushToDisk: true);
        LinuxSaveNative.Stat stagedStat = LinuxSaveNative.Inspect(staged.SafeFileHandle);
        if (!readBytes(staged).AsSpan().SequenceEqual(prepared))
            throw new IOException("The staged copy did not match the prepared bytes.");
        beforeCheck?.Invoke();

        if (backedUpSha256 is null)
        {
            folder.RequireVacant(name);
            beforeSwap?.Invoke();
            folder.RequireVacant(name);
            folder.Link(staged.SafeFileHandle, name);
            return GameInstaller.AfterPublication(target, backupFolder, replaced: false, () =>
            {
                afterPublish?.Invoke();
                return Verified(folder, target, name, prepared, stagedStat, backupFolder, replaced: false, exchanged: false, readBytes);
            });
        }

        (LinuxSaveNative.Stat original, byte[] originalBytes) = folder.ReadFile(name, readBytes);
        if (!string.Equals(Hash(originalBytes), backedUpSha256, StringComparison.OrdinalIgnoreCase))
            throw new IOException($"{name} changed after it was backed up. Back up again before writing.");
        string temporary = $".onslaught-install-{Guid.NewGuid():N}.tmp";
        folder.RequireVacant(temporary);
        folder.Link(staged.SafeFileHandle, temporary);
        bool exchanged;
        try
        {
            (LinuxSaveNative.Stat again, byte[] againBytes) = folder.ReadFile(name, readBytes);
            if (again.Identity != original.Identity || !againBytes.AsSpan().SequenceEqual(originalBytes))
                throw new IOException($"{name} changed after it was backed up. Back up again before writing.");
            beforeSwap?.Invoke();
            exchanged = folder.TryExchange(temporary, name);
        }
        catch
        {
            // Nothing was swapped: the temporary name still holds only our staged copy.
            folder.RemoveOwn(temporary, stagedStat);
            throw;
        }
        if (!exchanged)
        {
            // Without an exchange the displaced file could not be checked against its backup or put back, so a
            // plain rename over it is never used: the career stays as it is.
            folder.RemoveOwn(temporary, stagedStat);
            return new InstallReceipt(false, $"{name} was not replaced: the drive holding your game cannot swap two files in one " +
                "step, which the companion needs to check the file it replaces. Nothing was written. Adding a new career, or " +
                "saving a copy elsewhere, still works.", target, backupFolder);
        }

        return GameInstaller.AfterPublication(target, backupFolder, replaced: true, () =>
        {
            afterPublish?.Invoke();
            LinuxSaveNative.Stat displaced = folder.Inspect(temporary);
            if (displaced.Identity != original.Identity || !folder.Matches(temporary, originalBytes, readBytes))
            {
                // Both replacement and an in-place write to the same inode must be restored. Identity alone
                // does not show that the bytes displaced by our swap are the bytes in the verified backup.
                if (folder.Inspect(name).Identity != stagedStat.Identity || !folder.Matches(name, prepared, readBytes))
                    throw new IOException("The published file changed before rollback; the displaced file was kept at " + temporary);
                if (!folder.TryExchange(temporary, name))
                    throw new IOException("The rollback exchange was unavailable; the displaced file was kept at " + temporary);
                folder.RemoveOwn(temporary, stagedStat);
                folder.Flush();
                return new InstallReceipt(false, $"{name} was replaced by another program during the write. It was put back " +
                    "unchanged and nothing was installed.", target, backupFolder, MayHaveChanged: true);
            }
            folder.RemoveOwn(temporary, original);
            return Verified(folder, target, name, prepared, stagedStat, backupFolder, replaced: true, exchanged: true, readBytes);
        });
    }

    private static InstallReceipt Verified(Folder folder, string target, string name, byte[] prepared, LinuxSaveNative.Stat staged,
        string backupFolder, bool replaced, bool exchanged, Func<FileStream, byte[]> readBytes)
    {
        folder.Flush();
        (LinuxSaveNative.Stat written, byte[] bytes) = folder.ReadFile(name, readBytes);
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

        internal (LinuxSaveNative.Stat Stat, byte[] Bytes) ReadFile(string name, Func<FileStream, byte[]> readBytes)
        {
            VerifyFolder();
            SafeFileHandle handle = LinuxSaveNative.OpenAt(Descriptor, name, LinuxSaveNative.ReadFile, 0);
            using FileStream stream = new(handle, FileAccess.Read);
            LinuxSaveNative.Stat stat = LinuxSaveNative.Inspect(handle);
            LinuxSaveNative.RequireRegular(stat, links: 1);
            return (stat, readBytes(stream));
        }

        internal bool Matches(string name, byte[] expected, Func<FileStream, byte[]> readBytes)
        {
            try
            {
                return ReadFile(name, readBytes).Bytes.AsSpan().SequenceEqual(expected);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException)
            {
                // A changed length or unreadable displaced file is not a verified match; keep it intact.
                return false;
            }
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
            if (GameInstaller.ExchangeUnsupported) return false;
            if (RenameAt2(Descriptor, first, Descriptor, second, RenameExchange) == 0) return true;
            int error = Marshal.GetLastWin32Error();
            if (error is NotSupported or NoSystemCall or NotDirectoryTypeSupported) return false;
            throw LinuxSaveNative.Failure("The files could not be swapped safely.", error);
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
