// SPDX-License-Identifier: GPL-3.0-only
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>What removing a play folder did: whether it is gone, what was left in place and why, and a sentence for the player.</summary>
internal sealed record CePlayRemoval(bool Removed, IReadOnlyList<string> Left, string Message);

/// <summary>What the stale sweep did: the folders it removed and the ones it kept, with the reason for each.</summary>
internal sealed record CePlaySweep(IReadOnlyList<string> Removed, IReadOnlyList<string> Kept);

/// <summary>The words in a play folder's marker file: whose folder it is and which processes may still be using it.</summary>
internal sealed record CePlayMarker(string Format, string Folder, string Created, int CompanionPid, int LauncherPid, int Level, string Mod);

/// <summary>
/// One temporary Onslaught CE user folder, made for one test play of a level with the mod being tried. It holds a copy of the player's
/// ce.ini (changed), their options file and the mod, never a career. The folder is made exclusively inside the companion's own play folder
/// (mkdir fails if the name exists), carries a marker file only this class writes, and is removed only by path: the one folder it
/// made, after checking that it is a direct child of the play folder, that nothing on the way is a link and that the marker is its own;
/// a link or a special file inside it (CE writes none) is left where it is and reported, never followed.
/// </summary>
internal sealed class CePlayFolder
{
    internal const string MarkerName = ".onslaught-toolkit-ce-play";
    internal const string MarkerFormat = "onslaught-toolkit-ce-play-1";
    internal const string NamePrefix = "play-";
    private const int MaxMarkerBytes = 4096;
    private const int FileExists = 17;
    private const uint PrivateFolder = 0x1C0;   // 0700
    private const int RemoveFolderFlag = 0x200;   // AT_REMOVEDIR

    /// <summary>Test hook: called with an entry's name after its kind was read and before it is opened or removed, so a test can swap it for a link at the worst moment.</summary>
    internal static Action<string>? AfterKind { get; set; }

    [DllImport("libc", EntryPoint = "unlinkat", SetLastError = true)]
    private static extern int UnlinkAt(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string name, int flags);

    // Every entry, the marker and other dot files included (the default skips hidden ones on some paths).
    private static readonly EnumerationOptions AllEntries = new() { AttributesToSkip = 0, IgnoreInaccessible = false, RecurseSubdirectories = false, ReturnSpecialDirectories = false };

    private readonly List<string> _files = [];
    private readonly List<string> _folders = [];
    private CePlayMarker _marker;

    private CePlayFolder(string parent, string root, CePlayMarker marker) => (Parent, Root, _marker) = (parent, root, marker);

    /// <summary>The companion's play folder, which holds every one of these.</summary>
    internal string Parent { get; }

    /// <summary>The folder CE is told to use as its user folder.</summary>
    internal string Root { get; }

    internal CePlayMarker Marker => _marker;

    /// <summary>The files and folders this companion made in the folder (CE's own are not listed), for the tests and the report.</summary>
    internal IReadOnlyList<string> Written => _files;

    internal IReadOnlyList<string> Made => _folders;

    private enum Kind { Missing, Folder, File, Link, Other }

    /// <summary>What a path is, without following a link (a link is a link, whatever it points at).</summary>
    private static Kind KindOf(string path)
    {
        if (!OperatingSystem.IsLinux()) throw new PlatformNotSupportedException("A test play needs Linux.");
        if (LinuxSaveNative.StatAt(LinuxSaveNative.AtCurrentDirectory, path, LinuxSaveNative.NoFollow, 0x3, out LinuxSaveNative.Stat stat) != 0)
        {
            int error = Marshal.GetLastWin32Error();
            if (error == 2 || error == 20) return Kind.Missing;   // ENOENT, ENOTDIR
            throw LinuxSaveNative.Failure($"{path} could not be inspected.", error);
        }
        return (stat.Mode & 0xF000) switch { 0x4000 => Kind.Folder, 0x8000 => Kind.File, 0xA000 => Kind.Link, _ => Kind.Other };
    }

    /// <summary>What an entry of an open folder is, by name, without following a link.</summary>
    private static Kind KindAt(SafeFileHandle folder, string name)
    {
        if (LinuxSaveNative.StatAt((int)folder.DangerousGetHandle(), name, LinuxSaveNative.NoFollow, 0x3, out LinuxSaveNative.Stat stat) != 0)
        {
            int error = Marshal.GetLastWin32Error();
            if (error == 2 || error == 20) return Kind.Missing;
            throw LinuxSaveNative.Failure($"{name} could not be inspected.", error);
        }
        return (stat.Mode & 0xF000) switch { 0x4000 => Kind.Folder, 0x8000 => Kind.File, 0xA000 => Kind.Link, _ => Kind.Other };
    }

    /// <summary>A folder opened without following a link (the open fails if it is one), by name in an open folder or by full path.</summary>
    private static SafeFileHandle OpenFolder(int directory, string name) => LinuxSaveNative.OpenAt(directory, name, LinuxSaveNative.ReadDirectory, 0);

    /// <summary>The names in an open folder, dot files included. The folder is read through its descriptor, so it is the one that was opened whatever happens to its path.</summary>
    private static List<string> NamesIn(SafeFileHandle folder) =>
        [.. Directory.EnumerateFileSystemEntries($"/proc/self/fd/{(int)folder.DangerousGetHandle()}", "*", AllEntries).Select(Path.GetFileName).OfType<string>()];

    /// <summary>
    /// Makes a new folder <c>PARENT/play-STAMP-RANDOM</c> (the parent too, if it is not there yet) and writes its marker. Refuses, with nothing
    /// left behind, when the parent is not a full path, is or has a link on the way, or cannot be made.
    /// </summary>
    internal static Outcome<CePlayFolder> Create(string parent, int level, string mod, int companionPid, DateTime now, Func<string>? randomPart = null)
    {
        if (!OperatingSystem.IsLinux()) return Outcome<CePlayFolder>.Refusal("Onslaught CE loads a level's world from a mod on Linux only for now.");
        if (!Path.IsPathFullyQualified(parent)) return Outcome<CePlayFolder>.Refusal("The play folder must be a full path.");
        string made = "";
        try
        {
            string full = Path.TrimEndingDirectorySeparator(Path.GetFullPath(parent));
            FileMutationSafety.RejectExistingReparseAncestors(Path.Combine(full, "x"), "The play folder");
            if (!MakeParent(full)) return Outcome<CePlayFolder>.Refusal($"{full} is not a folder the companion can keep test plays in.");
            string name = "";
            for (int attempt = 0; attempt < 8 && made.Length == 0; attempt++)
            {
                name = $"{NamePrefix}{now:yyyyMMdd-HHmmss}-{(randomPart is null ? RandomNumberGenerator.GetHexString(8, lowercase: true) : randomPart())}";
                string candidate = Path.Combine(full, name);
                if (LinuxSaveNative.MakeDirectoryAt(LinuxSaveNative.AtCurrentDirectory, candidate, PrivateFolder) == 0) made = candidate;
                else if (Marshal.GetLastWin32Error() != FileExists)
                    return Outcome<CePlayFolder>.Refusal($"The folder for a test play could not be made in {full}: " +
                        new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error()).Message);
            }
            if (made.Length == 0) return Outcome<CePlayFolder>.Refusal("No new folder name for a test play was free.");
            CePlayFolder folder = new(full, made, new CePlayMarker(MarkerFormat, name, now.ToUniversalTime().ToString("O"), companionPid, 0, level, mod));
            folder._folders.Add(made);
            folder.WriteMarker(create: true);
            return Outcome<CePlayFolder>.Success(folder, "A folder for the test play was made.");
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException or JsonException or InvalidOperationException)
        {
            // (InvalidOperationException is what the link check throws for a folder that is, or lies behind, a link.)
            if (made.Length > 0) TryRemoveJustMade(Path.GetDirectoryName(made)!, Path.GetFileName(made));
            return Outcome<CePlayFolder>.Refusal("The folder for a test play could not be made: " + error.Message);
        }
    }

    /// <summary>The play folder itself: made (private, one level) if it is missing, and refused if it is a link or not a folder.</summary>
    private static bool MakeParent(string full)
    {
        switch (KindOf(full))
        {
            case Kind.Folder: return true;
            case Kind.Missing:
                string? above = Path.GetDirectoryName(full);
                if (above is null || KindOf(above) != Kind.Folder) return false;
                if (LinuxSaveNative.MakeDirectoryAt(LinuxSaveNative.AtCurrentDirectory, full, PrivateFolder) != 0 && Marshal.GetLastWin32Error() != FileExists)
                    return false;
                return KindOf(full) == Kind.Folder;
            default: return false;
        }
    }

    /// <summary>Writes a file in the folder, which must not exist yet (the open fails if anything, a link included, is there), and records it.</summary>
    internal void WriteFile(string relative, byte[] bytes)
    {
        string path = Combine(relative);
        EnsureFolders(Path.GetDirectoryName(path)!);
        using (FileStream stream = CreateNewPrivate(path))
        {
            stream.Write(bytes);
            stream.Flush(true);
        }
        _files.Add(path);
    }

    /// <summary>A new file only the player can read (the open fails if anything, a link included, is already there).</summary>
    private static FileStream CreateNewPrivate(string path)
    {
        FileStreamOptions options = new() { Mode = FileMode.CreateNew, Access = FileAccess.Write, Share = FileShare.None };
        if (OperatingSystem.IsLinux()) options.UnixCreateMode = UnixFileMode.UserRead | UnixFileMode.UserWrite;
        return new FileStream(path, options);
    }

    /// <summary>
    /// Copies one regular file of the player's into this folder under <paramref name="relative"/>, or says why not (it is a link or
    /// not a regular file, or is larger than <paramref name="limit"/> bytes). Returns the sentence for the player, or null when it was copied (or there was nothing to copy).
    /// </summary>
    internal string? CopyRegular(string source, string relative, long limit)
    {
        try
        {
            switch (KindOf(source))
            {
                case Kind.Missing: return null;   // nothing of theirs to copy: nothing to say
                case Kind.File: break;
                default: return $"{Path.GetFileName(source)} is not a plain file, so it was not copied.";
            }
            using FileStream stream = new(source, new FileStreamOptions { Mode = FileMode.Open, Access = FileAccess.Read, Share = FileShare.ReadWrite });
            if (stream.Length > limit) return $"{Path.GetFileName(source)} is larger than expected, so it was not copied.";
            byte[] bytes = new byte[stream.Length];
            stream.ReadExactly(bytes);
            WriteFile(relative, bytes);
            return null;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return $"{Path.GetFileName(source)} could not be copied: {error.Message}";
        }
    }

    /// <summary>Records the launcher's process id in the marker, so a later sweep leaves the folder alone while CE runs.</summary>
    internal void RecordLauncher(int launcherPid)
    {
        _marker = _marker with { LauncherPid = launcherPid };
        WriteMarker(create: false);
    }

    private string Combine(string relative)
    {
        if (Path.IsPathRooted(relative) || relative.Split('/', '\\').Any(part => part is ".." or "")) throw new ArgumentException("A play folder's files are named inside it.");
        return Path.Combine(Root, relative.Replace('/', Path.DirectorySeparatorChar));
    }

    private void EnsureFolders(string folder)
    {
        if (string.Equals(folder, Root, StringComparison.Ordinal)) return;
        if (!folder.StartsWith(Root + Path.DirectorySeparatorChar, StringComparison.Ordinal)) throw new ArgumentException("A folder outside the play folder was named.");
        if (KindOf(folder) == Kind.Folder) return;
        EnsureFolders(Path.GetDirectoryName(folder)!);
        if (LinuxSaveNative.MakeDirectoryAt(LinuxSaveNative.AtCurrentDirectory, folder, PrivateFolder) != 0)
            throw LinuxSaveNative.Failure($"{folder} could not be made.", Marshal.GetLastWin32Error());
        _folders.Add(folder);
    }

    private void WriteMarker(bool create)
    {
        byte[] bytes = JsonSerializer.SerializeToUtf8Bytes(_marker);
        string marker = Path.Combine(Root, MarkerName);
        if (create)
        {
            WriteFile(MarkerName, bytes);
            return;
        }
        string temporary = marker + ".new";
        using (FileStream stream = CreateNewPrivate(temporary))
        {
            stream.Write(bytes);
            stream.Flush(true);
        }
        File.Move(temporary, marker, overwrite: true);
    }

    /// <summary>The marker of a folder, if it has a well-formed one of this class's format that names the folder it is in; else null.</summary>
    internal static CePlayMarker? ReadMarker(string folder)
    {
        try
        {
            string path = Path.Combine(folder, MarkerName);
            if (KindOf(path) != Kind.File) return null;
            using FileStream stream = new(path, new FileStreamOptions { Mode = FileMode.Open, Access = FileAccess.Read, Share = FileShare.ReadWrite });
            if (stream.Length is 0 or > MaxMarkerBytes) return null;
            byte[] bytes = new byte[stream.Length];
            stream.ReadExactly(bytes);
            CePlayMarker? marker = JsonSerializer.Deserialize<CePlayMarker>(bytes);
            return marker is { Format: MarkerFormat } && marker.Folder == Path.GetFileName(folder) && marker.Folder.StartsWith(NamePrefix, StringComparison.Ordinal)
                ? marker : null;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or JsonException or PlatformNotSupportedException)
        {
            return null;
        }
    }

    /// <summary>The marker of an open folder, read by name in it without following a link: the same checks as <see cref="ReadMarker"/>, on the folder that was opened.</summary>
    private static CePlayMarker? ReadMarkerIn(SafeFileHandle folder, string folderName)
    {
        try
        {
            if (KindAt(folder, MarkerName) != Kind.File) return null;
            using SafeFileHandle file = LinuxSaveNative.OpenAt((int)folder.DangerousGetHandle(), MarkerName, LinuxSaveNative.ReadFile, 0);
            using FileStream stream = new(file, FileAccess.Read, 1);
            if (stream.Length is 0 or > MaxMarkerBytes) return null;
            byte[] bytes = new byte[stream.Length];
            stream.ReadExactly(bytes);
            CePlayMarker? marker = JsonSerializer.Deserialize<CePlayMarker>(bytes);
            return marker is { Format: MarkerFormat } && marker.Folder == folderName && marker.Folder.StartsWith(NamePrefix, StringComparison.Ordinal) ? marker : null;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or JsonException or PlatformNotSupportedException)
        {
            return null;
        }
    }

    /// <summary>
    /// Removes this folder and what is inside it. Refuses, leaving everything, unless the folder is a direct child of the play folder, is a real
    /// folder (not a link), and holds this class's marker naming it. Inside, files and folders go; a link or a special file stays, with the
    /// folders above it, and is reported.
    /// </summary>
    internal CePlayRemoval Remove()
    {
        if (!OperatingSystem.IsLinux()) return new CePlayRemoval(false, [Root], "A test play needs Linux.");
        return RemoveFolder(Parent, Root);
    }

    private static CePlayRemoval RemoveFolder(string parent, string root)
    {
        try
        {
            if (!string.Equals(Path.GetDirectoryName(root), parent, StringComparison.Ordinal) ||
                !Path.GetFileName(root).StartsWith(NamePrefix, StringComparison.Ordinal))
                return new CePlayRemoval(false, [root], $"{root} is not a folder of the companion's test plays, so it was left.");
            string name = Path.GetFileName(root);
            // The play folder is opened without following a link, then the folder by name inside it (the open fails for a link or a file): from here on every step is by name in an open folder.
            using SafeFileHandle play = OpenFolder(LinuxSaveNative.AtCurrentDirectory, parent);
            SafeFileHandle made;
            try
            {
                made = OpenFolder((int)play.DangerousGetHandle(), name);
            }
            catch (IOException)
            {
                return new CePlayRemoval(false, [root], $"{root} is not a plain folder (a link, or gone), so it was left.");
            }
            using (made)
            {
                if (ReadMarkerIn(made, name) is null)
                    return new CePlayRemoval(false, [root], $"{root} does not carry the companion's marker, so it was left.");
                List<string> left = [];
                Sweep(made, root, left, MarkerName);
                if (left.Count == 0 && UnlinkAt((int)play.DangerousGetHandle(), name, RemoveFolderFlag) != 0) left.Add(root);
                return left.Count == 0
                    ? new CePlayRemoval(true, [], "The folder of the test play was removed.")
                    : new CePlayRemoval(false, left, $"The test play's folder was not removed completely; left in place: {string.Join(", ", left.Take(3))}" +
                        (left.Count > 3 ? $" and {left.Count - 3} more" : "") + ".");
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
        {
            return new CePlayRemoval(false, [root], $"The test play's folder could not be removed: {error.Message}");
        }
    }

    /// <summary>
    /// Removes what is inside the open folder <paramref name="folder"/> (shown as <paramref name="display"/> in messages), every step by name in an open folder: a file is unlinked, a
    /// folder is opened without following a link (the open fails if it was swapped for one in the meantime), emptied the same way and then removed; a link, a special file or
    /// anything that cannot go is added to <paramref name="left"/>. The marker (named by <paramref name="marker"/>, in the outermost folder) goes last, and only when nothing else is left,
    /// so a folder that could not be removed whole is still known as ours to the next start's sweep. The caller removes the folder itself.
    /// </summary>
    private static void Sweep(SafeFileHandle folder, string display, List<string> left, string? marker = null)
    {
        int descriptor = (int)folder.DangerousGetHandle();
        bool blocked = false;
        foreach (string name in NamesIn(folder))
        {
            if (marker is not null && string.Equals(name, marker, StringComparison.Ordinal)) continue;
            string shown = Path.Combine(display, name);
            Kind kind = KindAt(folder, name);
            AfterKind?.Invoke(shown);
            switch (kind)
            {
                case Kind.Folder:
                    SafeFileHandle child;
                    try
                    {
                        child = OpenFolder(descriptor, name);
                    }
                    catch (IOException)
                    {
                        left.Add(shown);   // swapped for a link, or gone, since its kind was read
                        blocked = true;
                        break;
                    }
                    int before = left.Count;
                    using (child) Sweep(child, shown, left);
                    if (left.Count > before || UnlinkAt(descriptor, name, RemoveFolderFlag) != 0)
                    {
                        if (left.Count == before) left.Add(shown);
                        blocked = true;
                    }
                    break;
                case Kind.File:
                    if (UnlinkAt(descriptor, name, 0) != 0 && Marshal.GetLastWin32Error() != 2)
                    {
                        left.Add(shown);
                        blocked = true;
                    }
                    break;
                case Kind.Missing:
                    break;
                default:
                    left.Add(shown);
                    blocked = true;
                    break;
            }
        }
        if (!blocked && marker is not null && UnlinkAt(descriptor, marker, 0) != 0 && Marshal.GetLastWin32Error() != 2) left.Add(Path.Combine(display, marker));
    }

    /// <summary>
    /// Removes the play folders an earlier companion left (it was closed, or crashed, while CE ran): only direct children of <paramref name="parent"/> that
    /// are real folders and carry a marker of this class naming themselves, and only when neither the companion that made them nor CE is still
    /// running (<paramref name="alive"/> says whether a process id is) and the folder is not the one this companion holds now
    /// (<paramref name="current"/>). Anything else in the play folder is left alone.
    /// </summary>
    internal static CePlaySweep SweepStale(string parent, int companionPid, string? current, Func<int, bool> alive)
    {
        List<string> removed = [], kept = [];
        try
        {
            if (!OperatingSystem.IsLinux() || !Path.IsPathFullyQualified(parent) || KindOf(parent) != Kind.Folder) return new CePlaySweep(removed, kept);
            string full = Path.TrimEndingDirectorySeparator(Path.GetFullPath(parent));
            foreach (string entry in Directory.EnumerateFileSystemEntries(full, "*", AllEntries).Order(StringComparer.Ordinal).ToList())
            {
                string name = Path.GetFileName(entry);
                if (!name.StartsWith(NamePrefix, StringComparison.Ordinal) || KindOf(entry) != Kind.Folder) continue;
                if (ReadMarker(entry) is not CePlayMarker marker)
                {
                    kept.Add($"{name}: no marker of ours");
                    continue;
                }
                if (string.Equals(entry, current, StringComparison.Ordinal)) kept.Add($"{name}: in use by this companion");
                else if (marker.CompanionPid == companionPid) kept.Add($"{name}: made by this companion");
                else if (marker.CompanionPid > 0 && alive(marker.CompanionPid)) kept.Add($"{name}: its companion is still running");
                else if (marker.LauncherPid > 0 && alive(marker.LauncherPid)) kept.Add($"{name}: CE is still running in it");
                else
                {
                    CePlayRemoval outcome = RemoveFolder(full, entry);
                    (outcome.Removed ? removed : kept).Add(outcome.Removed ? name : $"{name}: {outcome.Message}");
                }
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            kept.Add($"the play folder could not be read: {error.Message}");
        }
        return new CePlaySweep(removed, kept);
    }

    /// <summary>A folder this call just made that failed before it held anything but its marker: the marker and the folder are removed again, by name in the open play folder; if anything else is in it, it stays.</summary>
    private static void TryRemoveJustMade(string parent, string name)
    {
        try
        {
            using SafeFileHandle play = OpenFolder(LinuxSaveNative.AtCurrentDirectory, parent);
            using (SafeFileHandle made = OpenFolder((int)play.DangerousGetHandle(), name)) UnlinkAt((int)made.DangerousGetHandle(), MarkerName, 0);
            UnlinkAt((int)play.DangerousGetHandle(), name, RemoveFolderFlag);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            // What could not go stays; the next start's sweep finds it by its marker (or leaves it, if it has none).
        }
    }
}
