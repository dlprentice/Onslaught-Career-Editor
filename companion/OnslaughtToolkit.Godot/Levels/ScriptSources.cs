// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;

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
/// Read only. A name is matched against the folder's entries, never joined into a path, so a script named like a path finds nothing; links
/// are ignored, as the level archive reader ignores them, and only a regular file is read (a named pipe would wait for a writer for ever).
/// A folder that cannot be listed or a file that cannot be read is a reason in the result, never an exception.
/// </summary>
public static class ScriptSources
{
    public const int MaxBytes = 1 << 20;

    public static ScriptSourceResult Find(string gameRoot, int level, string scriptName)
    {
        string file;
        try
        {
            string? scripts = ChildFolder(gameRoot, "data") is { } data ? ChildFolder(data, "MissionScripts") : null;
            if (scripts is null) return new(null, "This game has no data/MissionScripts folder.");
            string folderName = $"level{level:D3}";
            if (ChildFolder(scripts, folderName) is not { } folder) return new(null, $"This game has no MissionScripts folder for level {level}.");
            if (ChildFile(folder, scriptName + ".msl") is not { } found) return new(null, $"No file named {scriptName}.msl in {System.IO.Path.GetFileName(folder)}.");
            file = found;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            // A folder with no permission to list it (or one that went away) is a reason to show, not an error for the page to meet.
            return new(null, $"The script sources could not be looked up: {error.Message}");
        }
        try
        {
            if (!IsRegularFile(file)) return new(null, $"{System.IO.Path.GetFileName(file)} is not a regular file, so it is not read.");
        }
        catch (IOException error)
        {
            return new(null, $"{System.IO.Path.GetFileName(file)} could not be examined: {error.Message}");
        }
        try
        {
            FileInfo info = new(file);
            if (info.Length > MaxBytes) return new(null, $"{info.Name} is larger than {MaxBytes / 1024} KiB, so it is not shown.");
            string text = Encoding.Latin1.GetString(System.IO.File.ReadAllBytes(file)).Replace("\r\n", "\n").Replace('\r', '\n');
            int lines = text.Count(c => c == '\n') + (text.Length > 0 && text[^1] != '\n' ? 1 : 0);
            return new(new ScriptSource(file, text, lines), null);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return new(null, $"{System.IO.Path.GetFileName(file)} could not be read: {error.Message}");
        }
    }

    // Linux statx has the same 256-byte layout on every architecture; of it only the mask and the mode are read.
    [StructLayout(LayoutKind.Explicit, Size = 256)]
    private struct Stat
    {
        [FieldOffset(0)] internal uint Mask;
        [FieldOffset(28)] internal ushort Mode;
    }

    [DllImport("libc", EntryPoint = "statx", SetLastError = true)]
    private static extern int StatAt(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string path, int flags, uint mask, out Stat stat);

    /// <summary>
    /// Whether the entry is a regular file, asked of the file system without opening it: opening a named pipe waits for a writer, and a
    /// device may never end. A link is not one (it is asked about itself, not its target). Elsewhere than Linux (Windows folders hold no
    /// pipes) every file a folder lists is taken as one. The answer is for the moment it is given: an entry swapped for a pipe afterwards is
    /// not guarded against. When the system cannot be asked (the call refused, or a C library without statx) nothing is read.
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
        return Pick(new DirectoryInfo(parent).EnumerateDirectories().Where(folder => folder.LinkTarget is null).Select(folder => folder.Name), name) is { } found
            ? System.IO.Path.Combine(parent, found) : null;
    }

    private static string? ChildFile(string parent, string name) =>
        Pick(new DirectoryInfo(parent).EnumerateFiles().Where(file => file.LinkTarget is null).Select(file => file.Name), name) is { } found
            ? System.IO.Path.Combine(parent, found) : null;

    private static string? Pick(IEnumerable<string> names, string wanted) =>
        names.Where(name => string.Equals(name, wanted, StringComparison.OrdinalIgnoreCase)).OrderBy(name => name != wanted).ThenBy(name => name, StringComparer.Ordinal).FirstOrDefault();
}
