// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security;
using System.Text;
using Microsoft.Win32.SafeHandles;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>
/// Read-only, bounded source-file access. An include is resolved below the selected game directory and never through a link;
/// the file is opened without following the final entry, and its type and size are checked on that open handle.
/// </summary>
internal static class ScriptSourceReader
{
    private const int AtCurrent = -100, ReadDirectory = 0x10000 | 0x80000, NoFollow = 0x20000, ReadFile = 0x80000 | 0x800 | NoFollow;
    private const uint StatTypeAndSize = 0x201;
    private const uint FileFlagBackupSemantics = 0x02000000, FileReadAttributes = 0x80;

    internal static string ReadPath(string path)
    {
        string shown = Path.GetFileName(path);
        try
        {
            if (OperatingSystem.IsLinux())
            {
                using SafeFileHandle handle = OpenLinux(AtCurrent, path, ReadFile, shown);
                return ReadLinux(handle, shown, shown);
            }
            if (OperatingSystem.IsWindows())
            {
                using SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(path, "Script source");
                return ReadWindows(handle, shown, shown);
            }
            throw new CompileError($"{shown} could not be read");
        }
        catch (CompileError error) when (error.Message == Unreadable(shown).Message)
        {
            throw new CompileError($"{shown} could not be read");
        }
        catch (CompileError) { throw; }
        catch (Exception error) when (Expected(error)) { throw new CompileError($"{shown} could not be read"); }
    }

    internal static string ReadInGame(string gameRoot, string path)
    {
        if (string.IsNullOrEmpty(gameRoot)) throw new CompileError("no game folder is given");
        try
        {
            string[] parts = Parts(path);
            if (parts.Length == 0) throw NotFile(path);
            if (OperatingSystem.IsLinux()) return ReadInGameLinux(gameRoot, path, parts);
            if (OperatingSystem.IsWindows()) return ReadInGameWindows(gameRoot, path, parts);
            throw Unreadable(path);
        }
        catch (CompileError) { throw; }
        catch (Exception error) when (Expected(error)) { throw Unreadable(path); }
    }

    /// <summary>Looks up a path for display. A caller reading it must still use <see cref="ReadInGame"/> so the open stays protected.</summary>
    internal static string Locate(string gameRoot, string path)
    {
        if (string.IsNullOrEmpty(gameRoot)) throw new CompileError("no game folder is given");
        try
        {
            string at = Path.GetFullPath(gameRoot);
            string[] parts = Parts(path);
            foreach (string part in parts)
            {
                CheckPart(part, path);
                FileSystemInfo entry = Pick(at, part, path);
                if (IsLink(entry)) throw Link(path);
                at = entry.FullName;
            }
            if (parts.Length == 0 || !File.Exists(at) || !OnslaughtToolkit.Companion.Levels.ScriptSources.IsRegularFile(at)) throw NotFile(path);
            return at;
        }
        catch (CompileError) { throw; }
        catch (Exception error) when (Expected(error)) { throw Unreadable(path); }
    }

    private static string[] Parts(string path)
    {
        return path.Replace('\\', '/').Split('/', StringSplitOptions.RemoveEmptyEntries).Where(part => part != ".").ToArray();
    }

    private static void CheckPart(string part, string shown)
    {
        if (part == "..") throw new CompileError($"a path cannot climb out of the game folder: {shown}");
    }

    private static bool SameAsciiCase(string left, string right)
    {
        if (left.Length != right.Length) return false;
        static char Fold(char c) => c is >= 'A' and <= 'Z' ? (char)(c + ('a' - 'A')) : c;
        for (int i = 0; i < left.Length; i++) if (Fold(left[i]) != Fold(right[i])) return false;
        return true;
    }

    private static FileSystemInfo Pick(string directory, string name, string shown)
    {
        try
        {
            FileSystemInfo? found = new DirectoryInfo(directory).EnumerateFileSystemInfos()
                .Where(entry => SameAsciiCase(entry.Name, name))
                .OrderBy(entry => !string.Equals(entry.Name, name, StringComparison.Ordinal))
                .ThenBy(entry => entry.Name, StringComparer.Ordinal).FirstOrDefault();
            return found ?? throw new MissingInclude(shown);
        }
        catch (DirectoryNotFoundException) { throw new MissingInclude(shown); }
    }

    private static bool IsLink(FileSystemInfo entry) => entry.LinkTarget is not null || (entry.Attributes & FileAttributes.ReparsePoint) != 0;
    private static CompileError Link(string shown) => new($"{shown} is a link or goes through one, which is not followed");
    private static CompileError NotFile(string shown) => new($"{shown} is not a file inside the game folder");
    private static CompileError Unreadable(string shown) => new($"the included file {shown} could not be read");
    private static bool Expected(Exception error) => error is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException or
        SecurityException or Win32Exception or DllNotFoundException or EntryPointNotFoundException or InvalidOperationException;

    private static string ReadInGameLinux(string root, string shown, string[] parts)
    {
        SafeFileHandle current = OpenLinux(AtCurrent, Path.GetFullPath(root), ReadDirectory, shown, root: true);
        try
        {
            for (int i = 0; i < parts.Length; i++)
            {
                CheckPart(parts[i], shown);
                string directory = $"/proc/self/fd/{current.DangerousGetHandle().ToInt32()}";
                FileSystemInfo entry = Pick(directory, parts[i], shown);
                if (IsLink(entry)) throw Link(shown);
                bool last = i == parts.Length - 1;
                if (!last)
                {
                    CheckPart(parts[i + 1], shown);
                    if ((entry.Attributes & FileAttributes.Directory) == 0) throw new MissingInclude(shown);
                }
                SafeFileHandle next = OpenLinux(current.DangerousGetHandle().ToInt32(), entry.Name,
                    last ? ReadFile : ReadDirectory | NoFollow, shown);
                current.Dispose();
                current = next;
                if (last) return ReadLinux(current, shown, entry.Name);
            }
            throw NotFile(shown);
        }
        finally { current.Dispose(); }
    }

    private static SafeFileHandle OpenLinux(int directory, string path, int flags, string shown, bool root = false)
    {
        if (RuntimeInformation.ProcessArchitecture is not Architecture.X64) throw Unreadable(shown);
        int descriptor = OpenAt(directory, path, flags, 0);
        if (descriptor < 0)
        {
            int error = Marshal.GetLastWin32Error();
            if (error == 40) throw Link(shown); // ELOOP: a final entry changed to a link
            if (root && error is 2 or 20) throw new MissingInclude(shown);
            throw Unreadable(shown);
        }
        return new SafeFileHandle(new IntPtr(descriptor), ownsHandle: true);
    }

    private static string ReadLinux(SafeFileHandle handle, string shown, string filename)
    {
        if (StatAt(handle.DangerousGetHandle().ToInt32(), "", 0x1000, StatTypeAndSize, out Stat stat) != 0 ||
            (stat.Mask & StatTypeAndSize) != StatTypeAndSize) throw Unreadable(shown);
        if ((stat.Mode & 0xF000) != 0x8000) throw NotFile(shown);
        if (stat.Size > ScriptCompiler.MaxSource) throw new CompileError($"{filename} is longer than a million bytes");
        using FileStream stream = new(handle, FileAccess.Read);
        return ReadBounded(stream, shown, filename);
    }

    private static string ReadInGameWindows(string root, string shown, string[] parts)
    {
        using SafeFileHandle initial = OpenWindowsDirectory(Path.GetFullPath(root));
        if (initial.IsInvalid) throw Unreadable(shown);
        WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(initial, "Game folder");
        string physical = FileMutationSafety.GetFinalLocalPath(initial, "Game folder");
        using FileMutationSafety.DirectoryLockSet rootGuard = FileMutationSafety.LockDirectoryTree(physical, "Game folder");
        if (!identity.IsSameFile(rootGuard.Identity)) throw Unreadable(shown);
        FileMutationSafety.DirectoryLockSet? childGuard = null;
        try
        {
            string at = rootGuard.PhysicalPath;
            for (int i = 0; i < parts.Length; i++)
            {
                CheckPart(parts[i], shown);
                FileSystemInfo entry = Pick(at, parts[i], shown);
                if (IsLink(entry)) throw Link(shown);
                if (i == parts.Length - 1)
                {
                    using SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(entry.FullName, "Script source");
                    return ReadWindows(handle, shown, entry.Name);
                }
                CheckPart(parts[i + 1], shown);
                if ((entry.Attributes & FileAttributes.Directory) == 0) throw new MissingInclude(shown);
                FileMutationSafety.DirectoryLockSet next = FileMutationSafety.LockDirectoryTree(entry.FullName, "Script source folder");
                childGuard?.Dispose();
                childGuard = next;
                at = next.PhysicalPath;
            }
            throw NotFile(shown);
        }
        finally { childGuard?.Dispose(); }
    }

    private static string ReadWindows(SafeFileHandle handle, string shown, string filename)
    {
        WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, "Script source");
        if (identity.IsReparsePoint) throw Link(shown);
        if (GetFileType(handle) != 1) throw NotFile(shown); // FILE_TYPE_DISK
        using FileStream stream = new(handle, FileAccess.Read);
        if (stream.Length > ScriptCompiler.MaxSource) throw new CompileError($"{filename} is longer than a million bytes");
        return ReadBounded(stream, shown, filename);
    }

    private static string ReadBounded(FileStream stream, string shown, string filename)
    {
        using MemoryStream data = new();
        byte[] chunk = new byte[65536];
        while (data.Length <= ScriptCompiler.MaxSource)
        {
            int read = stream.Read(chunk, 0, (int)Math.Min(chunk.Length, ScriptCompiler.MaxSource + 1L - data.Length));
            if (read == 0) break;
            data.Write(chunk, 0, read);
        }
        if (data.Length > ScriptCompiler.MaxSource) throw new CompileError($"{filename} is longer than a million bytes");
        return Encoding.Latin1.GetString(data.ToArray());
    }

    [StructLayout(LayoutKind.Explicit, Size = 256)]
    private struct Stat
    {
        [FieldOffset(0)] internal uint Mask;
        [FieldOffset(28)] internal ushort Mode;
        [FieldOffset(40)] internal ulong Size;
    }

    [DllImport("libc", EntryPoint = "openat", SetLastError = true)]
    private static extern int OpenAt(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string path, int flags, uint mode);

    [DllImport("libc", EntryPoint = "statx", SetLastError = true)]
    private static extern int StatAt(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string path, int flags, uint mask, out Stat stat);

    [DllImport("kernel32.dll", EntryPoint = "CreateFileW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle OpenWindowsDirectory(string path, uint access = FileReadAttributes,
        FileShare share = FileShare.Read | FileShare.Write | FileShare.Delete, IntPtr security = default,
        FileMode mode = FileMode.Open, uint flags = FileFlagBackupSemantics, IntPtr template = default);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint GetFileType(SafeFileHandle handle);
}
