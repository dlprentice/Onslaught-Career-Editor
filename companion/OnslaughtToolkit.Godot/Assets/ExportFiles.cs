// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Assets;

/// <summary>The outcome of writing one exported file.</summary>
public sealed record ExportReceipt(bool Ok, string Message, string? Path = null);

/// <summary>
/// Writes exported files: always a new file, in a folder the player chose, never inside the game folder or the
/// companion's backup folder (both checked after resolving links, so a link cannot lead there). A name that already
/// exists is refused, never replaced; the bytes are written to a temporary name, read back, then moved into place
/// without replacing anything.
/// </summary>
public static class ExportFiles
{
    public static ExportReceipt Write(string folder, string fileName, byte[] bytes, IEnumerable<string?> protectedFolders)
    {
        if (fileName.Length == 0 || fileName != Path.GetFileName(fileName) || fileName.StartsWith('.') ||
            fileName.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 || fileName.IndexOfAny(['\\', ':', '*', '?', '"', '<', '>', '|']) >= 0)
            return new(false, $"\"{fileName}\" cannot be used as a file name.");
        if (!Path.IsPathFullyQualified(folder) || !Directory.Exists(folder))
            return new(false, "Choose an existing folder to export into.");
        string real = RealPath(folder);
        foreach (string? guarded in protectedFolders)
        {
            if (string.IsNullOrEmpty(guarded) || !Directory.Exists(guarded)) continue;
            if (Inside(real, RealPath(guarded)))
                return new(false, "Exports never go into your game folder or the companion's backups. Choose another folder.");
        }
        string target = Path.Combine(real, fileName);
        if (File.Exists(target) || Directory.Exists(target) || new FileInfo(target).LinkTarget is not null)
            return new(false, $"{fileName} already exists there; nothing was replaced.");
        string temporary = Path.Combine(real, $".onslaught-export-{Guid.NewGuid():N}.tmp");
        try
        {
            using (FileStream stream = new(temporary, FileMode.CreateNew, FileAccess.ReadWrite, FileShare.None))
            {
                stream.Write(bytes);
                stream.Flush(flushToDisk: true);
                stream.Position = 0;
                byte[] check = new byte[bytes.Length];
                stream.ReadExactly(check);
                if (!check.AsSpan().SequenceEqual(bytes)) throw new IOException("The written file did not read back the same.");
            }
            File.Move(temporary, target, overwrite: false);
            return new(true, $"Saved {fileName}.", target);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            try
            {
                if (File.Exists(temporary)) File.Delete(temporary);
            }
            catch (Exception cleanup) when (cleanup is IOException or UnauthorizedAccessException)
            {
                return new(false, $"{fileName} was not saved ({error.Message}); a temporary file may remain in that folder.");
            }
            return new(false, $"{fileName} was not saved: {error.Message}");
        }
    }

    /// <summary>The path with every link along it resolved.</summary>
    public static string RealPath(string path)
    {
        string full = Path.GetFullPath(path);
        string root = Path.GetPathRoot(full) ?? "/";
        string current = root;
        foreach (string part in full[root.Length..].Split(Path.DirectorySeparatorChar, StringSplitOptions.RemoveEmptyEntries))
        {
            string next = Path.Combine(current, part);
            FileSystemInfo info = new DirectoryInfo(next);
            if (info.LinkTarget is not null && info.ResolveLinkTarget(returnFinalTarget: true) is { } target)
                next = RealPath(target.FullName);
            current = next;
        }
        return Path.TrimEndingDirectorySeparator(current);
    }

    private static bool Inside(string path, string folder)
    {
        StringComparison comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        folder = Path.TrimEndingDirectorySeparator(folder);
        return string.Equals(path, folder, comparison) || path.StartsWith(folder + Path.DirectorySeparatorChar, comparison);
    }
}
