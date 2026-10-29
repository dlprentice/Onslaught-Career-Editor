// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security;
using System.Text;
using Microsoft.Win32.SafeHandles;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>A mission script's installed source text: the file it was read from, its text with <c>\n</c> line ends, and its line count.</summary>
public sealed record ScriptSource(string Path, string Text, int Lines);

/// <param name="Source">The source, or null.</param>
/// <param name="Problem">When there is no source, a sentence saying why.</param>
public sealed record ScriptSourceResult(ScriptSource? Source, string? Problem);

/// <summary>
/// Finds a compiled script's source in a game folder: <c>data/MissionScripts/level&lt;NNN&gt;/&lt;name&gt;.msl</c>, each part in any case (the game's
/// files are named for Windows). The game never reads these files: they are the original compiler's input, shipped with the data, so what
/// they say is what the script was compiled from only if they are the revision that was compiled (<c>tools/msl_gate.py</c> checks that).
/// Read only. A name is matched against the folder's entries, never joined into a path, so a script named like a path finds nothing.
/// The reader holds directories during lookup, refuses links below the chosen root, and bounds reads from verified regular files.
/// A folder that cannot be listed or a file that cannot be read is a reason in the result, never an exception.
/// </summary>
public static class ScriptSources
{
    public const int MaxBytes = 1 << 20;

    public static ScriptSourceResult Find(string gameRoot, int level, string scriptName)
    {
        if (!Directory.Exists(gameRoot)) return new(null, "This game has no data/MissionScripts folder.");
        try
        {
            if (OperatingSystem.IsLinux() && RuntimeInformation.ProcessArchitecture == Architecture.X64)
                return FindLinux(gameRoot, level, scriptName);
            if (OperatingSystem.IsWindows()) return FindWindows(gameRoot, level, scriptName);
            return new(null, "Script sources cannot be read safely on this system.");
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException or
                                      InvalidOperationException or PlatformNotSupportedException or Win32Exception or
                                      EntryPointNotFoundException or DllNotFoundException or SecurityException)
        {
            return new(null, $"The script sources could not be looked up: {error.Message}");
        }
    }

    private sealed record LinuxDirectory(SafeFileHandle Handle, int Parent, string Name, int NameFlags, Stat Identity);
    private const int AtCurrent = -100, NoFollow = 0x100, EmptyPath = 0x1000;
    private const int PathHandle = 0x200000 | 0x20000 | 0x80000; // O_PATH | O_NOFOLLOW | O_CLOEXEC
    private const uint SnapshotMask = 0x3c7; // type, mode, links, mtime, ctime, inode, size

    // Test-only transition point: production leaves it null. It lets authored tests change a file after its size check.
    internal static Action? BeforeReadForTest { get; set; }

    private static ScriptSourceResult FindLinux(string gameRoot, int level, string scriptName)
    {
        string absoluteRoot = System.IO.Path.GetFullPath(gameRoot);
        List<LinuxDirectory> directories = [];
        try
        {
            // The selected root itself may be reached through a link; all descendants use no-follow opens.
            SafeFileHandle root = LinuxSaveNative.OpenAt(AtCurrent, absoluteRoot, LinuxSaveNative.ReadDirectory & ~0x20000, 0);
            try { directories.Add(new(root, AtCurrent, absoluteRoot, 0, ReadStat(Descriptor(root), "", EmptyPath))); }
            catch { root.Dispose(); throw; }
            string display = gameRoot;
            string[] names = ["data", "MissionScripts", $"level{level:D3}"];
            for (int i = 0; i < names.Length; i++)
            {
                LinuxDirectory parent = directories[^1];
                string anchor = $"/proc/self/fd/{Descriptor(parent.Handle)}";
                string? chosen = ChildFolder(anchor, names[i]);
                if (chosen is null) return i < 2 ? new(null, "This game has no data/MissionScripts folder.")
                    : new(null, $"This game has no MissionScripts folder for level {level}.");
                string name = System.IO.Path.GetFileName(chosen);
                Stat listed = ReadStat(Descriptor(parent.Handle), name, NoFollow);
                SafeFileHandle next = LinuxSaveNative.OpenAt(Descriptor(parent.Handle), name, LinuxSaveNative.ReadDirectory, 0);
                try
                {
                    Stat opened = ReadStat(Descriptor(next), "", EmptyPath);
                    if (!SameIdentity(listed, opened)) throw new IOException("A script source folder changed during lookup.");
                    directories.Add(new(next, Descriptor(parent.Handle), name, NoFollow, opened));
                }
                catch { next.Dispose(); throw; }
                display = System.IO.Path.Combine(display, name);
            }
            LinuxDirectory folder = directories[^1];
            string path = $"/proc/self/fd/{Descriptor(folder.Handle)}";
            string? found = ChildFile(path, scriptName + ".msl");
            if (found is null) return new(null, $"No file named {scriptName}.msl in {System.IO.Path.GetFileName(display)}.");
            string fileName = System.IO.Path.GetFileName(found);
            Stat listedFile = ReadStat(Descriptor(folder.Handle), fileName, NoFollow);
            try
            {
                if (!IsRegularFile(found)) return NotRegular(fileName);
            }
            catch (IOException error) { return new(null, $"{fileName} could not be examined: {error.Message}"); }
            try
            {
                // O_PATH pins the selected inode without opening a possible replacement device or pipe for reading.
                using SafeFileHandle selected = LinuxSaveNative.OpenAt(Descriptor(folder.Handle), fileName, PathHandle, 0);
                Stat selectedInfo = ReadStat(Descriptor(selected), "", EmptyPath);
                if (!IsRegular(selectedInfo) || !SameVersion(listedFile, selectedInfo))
                    throw new IOException("The script source changed during lookup.");
                VerifyLinuxDirectories(directories);
                // The procfs handle refers to the already-opened inode, not a user-provided path component.
                using SafeFileHandle data = LinuxSaveNative.OpenAt(AtCurrent, $"/proc/self/fd/{Descriptor(selected)}",
                    LinuxSaveNative.ReadFile & ~0x20000, 0);
                if (!SameVersion(selectedInfo, ReadStat(Descriptor(data), "", EmptyPath)))
                    throw new IOException("The script source changed during lookup.");
                using FileStream stream = new(data, FileAccess.Read);
                if (selectedInfo.Size > MaxBytes) return TooLarge(fileName);
                (byte[]? bytes, string? problem) = ReadBounded(stream, fileName);
                if (problem is not null) return new(null, problem);
                VerifyLinuxDirectories(directories);
                if (!SameVersion(selectedInfo, ReadStat(Descriptor(data), "", EmptyPath)) ||
                    !SameVersion(selectedInfo, ReadStat(Descriptor(folder.Handle), fileName, NoFollow)))
                    throw new IOException("The script source changed during reading.");
                return Result(System.IO.Path.Combine(display, fileName), bytes!);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidOperationException or
                                          PlatformNotSupportedException or Win32Exception or EntryPointNotFoundException or DllNotFoundException)
            {
                return new(null, $"{fileName} could not be read: {error.Message}");
            }
        }
        finally
        {
            for (int i = directories.Count - 1; i >= 0; i--) directories[i].Handle.Dispose();
        }
    }

    private static int Descriptor(SafeFileHandle handle) => handle.DangerousGetHandle().ToInt32();

    private static void VerifyLinuxDirectories(List<LinuxDirectory> directories)
    {
        foreach (LinuxDirectory directory in directories)
        {
            if (!SameIdentity(directory.Identity, ReadStat(Descriptor(directory.Handle), "", EmptyPath)) ||
                !SameIdentity(directory.Identity, ReadStat(directory.Parent, directory.Name, directory.NameFlags)))
                throw new IOException("A script source folder changed during lookup.");
        }
    }

    private static Stat ReadStat(int directory, string path, int flags)
    {
        if (StatAt(directory, path, flags, SnapshotMask, out Stat result) != 0)
            throw new IOException(new Win32Exception(Marshal.GetLastWin32Error()).Message);
        if ((result.Mask & SnapshotMask) != SnapshotMask) throw new IOException("This file system cannot provide the required file identity.");
        return result;
    }

    private static bool IsRegular(Stat stat) => (stat.Mode & 0xf000) == 0x8000;
    private static bool SameIdentity(Stat a, Stat b) => a.DeviceMajor == b.DeviceMajor && a.DeviceMinor == b.DeviceMinor &&
        a.Inode == b.Inode && (a.Mode & 0xf000) == (b.Mode & 0xf000);
    private static bool SameVersion(Stat a, Stat b) => SameIdentity(a, b) && a.Mode == b.Mode && a.Links == b.Links &&
        a.Size == b.Size && a.MTimeSeconds == b.MTimeSeconds && a.MTimeNanoseconds == b.MTimeNanoseconds &&
        a.CTimeSeconds == b.CTimeSeconds && a.CTimeNanoseconds == b.CTimeNanoseconds;

    private static ScriptSourceResult FindWindows(string gameRoot, int level, string scriptName)
    {
        string absoluteRoot = System.IO.Path.GetFullPath(gameRoot);
        using SafeFileHandle selectedRoot = OpenWindowsDirectory(absoluteRoot);
        WindowsFileIdentity rootIdentity = FileMutationSafety.GetWindowsIdentity(selectedRoot, "Game folder");
        string physicalRoot = FileMutationSafety.GetFinalLocalPath(selectedRoot, "Game folder");
        List<FileMutationSafety.DirectoryLockSet> directories = [];
        try
        {
            FileMutationSafety.DirectoryLockSet first = FileMutationSafety.LockDirectoryTree(physicalRoot, "Game folder");
            directories.Add(first);
            if (!rootIdentity.IsSameFile(first.Identity)) throw new IOException("The game folder changed during lookup.");
            string display = gameRoot;
            string[] names = ["data", "MissionScripts", $"level{level:D3}"];
            for (int i = 0; i < names.Length; i++)
            {
                string? chosen = ChildFolder(directories[^1].PhysicalPath, names[i]);
                if (chosen is null) return i < 2 ? new(null, "This game has no data/MissionScripts folder.")
                    : new(null, $"This game has no MissionScripts folder for level {level}.");
                string name = System.IO.Path.GetFileName(chosen);
                directories.Add(FileMutationSafety.LockDirectoryTree(chosen, "Script source folder"));
                display = System.IO.Path.Combine(display, name);
            }
            string? found = ChildFile(directories[^1].PhysicalPath, scriptName + ".msl");
            if (found is null) return new(null, $"No file named {scriptName}.msl in {System.IO.Path.GetFileName(display)}.");
            string fileName = System.IO.Path.GetFileName(found);
            try
            {
                using SafeFileHandle file = FileMutationSafety.OpenNoFollowReadHandle(found, "Script source");
                WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(file, "Script source");
                if (identity.IsReparsePoint || ((FileAttributes)identity.Attributes & FileAttributes.Directory) != 0 || GetFileType(file) != 1)
                    return NotRegular(fileName);
                using FileStream stream = new(file, FileAccess.Read);
                (byte[]? bytes, string? problem) = ReadBounded(stream, fileName);
                if (problem is not null) return new(null, problem);
                using SafeFileHandle currentRoot = OpenWindowsDirectory(absoluteRoot);
                if (!rootIdentity.IsSameFile(FileMutationSafety.GetWindowsIdentity(currentRoot, "Game folder")))
                    throw new IOException("The game folder changed during lookup.");
                return Result(System.IO.Path.Combine(display, fileName), bytes!);
            }
            catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidOperationException or
                                          PlatformNotSupportedException or Win32Exception or SecurityException)
            {
                return new(null, $"{fileName} could not be read: {error.Message}");
            }
        }
        finally
        {
            for (int i = directories.Count - 1; i >= 0; i--) directories[i].Dispose();
        }
    }

    private static SafeFileHandle OpenWindowsDirectory(string path)
    {
        SafeFileHandle handle = CreateFileW(System.IO.Path.GetFullPath(path), 0x80, FileShare.Read | FileShare.Write | FileShare.Delete,
            IntPtr.Zero, FileMode.Open, 0x02000000, IntPtr.Zero); // FILE_READ_ATTRIBUTES, FILE_FLAG_BACKUP_SEMANTICS
        if (!handle.IsInvalid) return handle;
        int error = Marshal.GetLastWin32Error();
        handle.Dispose();
        throw new IOException("The game folder could not be opened safely.", new Win32Exception(error));
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateFileW(string name, uint access, FileShare share, IntPtr security,
        FileMode creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint GetFileType(SafeFileHandle handle);

    private static (byte[]? Bytes, string? Problem) ReadBounded(FileStream stream, string name)
    {
        long length = stream.Length;
        if (length > MaxBytes) return (null, TooLarge(name).Problem);
        BeforeReadForTest?.Invoke();
        using MemoryStream content = new((int)length);
        byte[] buffer = new byte[8192];
        int total = 0;
        while (total <= MaxBytes)
        {
            int count = stream.Read(buffer, 0, Math.Min(buffer.Length, MaxBytes + 1 - total));
            if (count == 0) break;
            total += count;
            if (total > MaxBytes) return (null, TooLarge(name).Problem);
            content.Write(buffer, 0, count);
        }
        return (content.ToArray(), null);
    }

    private static ScriptSourceResult TooLarge(string name) => new(null, $"{name} is larger than {MaxBytes / 1024} KiB, so it is not shown.");
    private static ScriptSourceResult NotRegular(string name) => new(null, $"{name} is not a regular file, so it is not read.");
    private static ScriptSourceResult Result(string path, byte[] bytes)
    {
        string text = Encoding.Latin1.GetString(bytes).Replace("\r\n", "\n").Replace('\r', '\n');
        int lines = text.Count(c => c == '\n') + (text.Length > 0 && text[^1] != '\n' ? 1 : 0);
        return new(new ScriptSource(path, text, lines), null);
    }

    // Linux statx has a fixed 256-byte layout; the supported reader is fenced to Linux x64 by LinuxSaveNative.
    [StructLayout(LayoutKind.Explicit, Size = 256)]
    private struct Stat
    {
        [FieldOffset(0)] internal uint Mask;
        [FieldOffset(16)] internal uint Links;
        [FieldOffset(28)] internal ushort Mode;
        [FieldOffset(32)] internal ulong Inode;
        [FieldOffset(40)] internal ulong Size;
        [FieldOffset(96)] internal long CTimeSeconds;
        [FieldOffset(104)] internal uint CTimeNanoseconds;
        [FieldOffset(112)] internal long MTimeSeconds;
        [FieldOffset(120)] internal uint MTimeNanoseconds;
        [FieldOffset(136)] internal uint DeviceMajor;
        [FieldOffset(140)] internal uint DeviceMinor;
    }

    [DllImport("libc", EntryPoint = "statx", SetLastError = true)]
    private static extern int StatAt(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string path, int flags, uint mask, out Stat stat);

    /// <summary>
    /// Whether a Linux entry is regular at the instant it is examined; a link is asked about itself, not its target. This precheck alone
    /// does not secure a later read: Find also checks the opened handle. On other systems Find uses its own handle-based checks.
    /// </summary>
    /// <exception cref="IOException">The entry could not be examined; the message says why.</exception>
    internal static bool IsRegularFile(string path)
    {
        if (!OperatingSystem.IsLinux()) return true;
        const uint typeMask = 0x1;  // STATX_TYPE
        (int Failed, int Errno, uint Mask, ushort Mode) answer;
        try
        {
            answer = Statx(path);
        }
        catch (Exception error) when (error is EntryPointNotFoundException or DllNotFoundException)
        {
            // Failing open here would bring the wait for a pipe back, so a system that cannot be asked reads nothing.
            throw new IOException("this system's C library has no statx to ask with", error);
        }
        if (answer.Failed != 0) throw new IOException(new Win32Exception(answer.Errno).Message);
        return (answer.Mask & typeMask) != 0 && (answer.Mode & 0xF000) == 0x8000;
    }

    /// <summary>The call that asks the system what an entry is: (the call's result, its errno, the mask and the mode it filled in). The tests put their own here to make the system refuse or lack the call; it is the native one otherwise.</summary>
    internal static Func<string, (int Failed, int Errno, uint Mask, ushort Mode)> Statx { get; set; } = NativeStatx;

    private static (int Failed, int Errno, uint Mask, ushort Mode) NativeStatx(string path)
    {
        const int atCurrentDirectory = -100, noFollow = 0x100;
        int failed = StatAt(atCurrentDirectory, path, noFollow, 0x1, out Stat stat);
        return (failed, failed != 0 ? Marshal.GetLastWin32Error() : 0, stat.Mask, stat.Mode);
    }

    /// <summary>The subfolder of <paramref name="parent"/> with this name in any case (the exact spelling first), or null; links are ignored.</summary>
    private static string? ChildFolder(string parent, string name)
    {
        if (!Directory.Exists(parent)) return null;
        return Pick(new DirectoryInfo(parent).EnumerateDirectories().Where(folder => !IsLink(folder)).Select(folder => folder.Name), name) is { } found
            ? System.IO.Path.Combine(parent, found) : null;
    }

    private static string? ChildFile(string parent, string name) =>
        Pick(new DirectoryInfo(parent).EnumerateFiles().Where(file => !IsLink(file)).Select(file => file.Name), name) is { } found
            ? System.IO.Path.Combine(parent, found) : null;

    private static bool IsLink(FileSystemInfo entry) => entry.LinkTarget is not null || (entry.Attributes & FileAttributes.ReparsePoint) != 0;

    private static string? Pick(IEnumerable<string> names, string wanted) =>
        names.Where(name => string.Equals(name, wanted, StringComparison.OrdinalIgnoreCase)).OrderBy(name => name != wanted).ThenBy(name => name, StringComparer.Ordinal).FirstOrDefault();
}
