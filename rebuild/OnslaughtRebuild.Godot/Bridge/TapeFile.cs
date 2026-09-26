// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The create-new / no-overwrite persistence control for command tapes, beside
/// the simulation bridge because GDScript file access has no exclusive create
/// (Core itself is filesystem-free by contract). Every write goes through
/// <see cref="System.IO.FileMode.CreateNew"/>, so an existing file at the
/// destination path can never be opened for writing, truncated, or replaced.
/// Callers hand this a path the user chose explicitly; there is deliberately no
/// discovery or default destination anywhere in this owner.
/// </summary>
public static class TapeFile
{
    /// <summary>
    /// Persists <paramref name="tape"/> as LF-canonical JSON, creating missing
    /// parent directories, and refuses any path that already exists. The
    /// refusal throws before a byte of tape JSON is produced, so a failed call
    /// leaves the destination untouched.
    /// </summary>
    public static void WriteNew(string path, CommandTape tape)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);
        ArgumentNullException.ThrowIfNull(tape);

        if (!Path.IsPathFullyQualified(path) ||
            !string.Equals(Path.GetExtension(path), ".json", StringComparison.OrdinalIgnoreCase))
        {
            throw new ArgumentException(
                "Command tapes require an absolute .json destination path; career saves and retail files are never valid destinations.",
                nameof(path));
        }

        // Fail-closed destination boundary: canonicalize and refuse protected
        // storage BEFORE any parent directory is created or the destination is
        // opened. A fresh absolute .json that lexical checks alone would admit
        // must still be refused when it lies inside a retail install or career
        // save layout, or behind an existing reparse-point ancestor. The
        // boundary itself refuses device-namespace spellings that alias no
        // ordinary path, so the later create-new open can never use an
        // identity this boundary did not evaluate.
        string fullPath = Path.GetFullPath(path);
        EnsureSafeDestination(fullPath);

        if (File.Exists(path))
        {
            throw new IOException(
                $"Command tape persistence refuses to overwrite '{path}'. Choose a fresh destination path.");
        }

        string? directory = Path.GetDirectoryName(Path.GetFullPath(path));
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        // CreateNew is the load-bearing control: it fails at the OS level if
        // anything raced the File.Exists check above, so the no-overwrite
        // guarantee does not depend on either check alone.
        using FileStream stream = new(
            path,
            FileMode.CreateNew,
            FileAccess.Write,
            FileShare.None);
        byte[] bytes = Encoding.UTF8.GetBytes(CommandTapeCodec.Serialize(tape));
        stream.Write(bytes);
        stream.Flush(flushToDisk: true);
    }

    /// <summary>
    /// The fail-closed destination boundary. Runs before any directory
    /// creation or file open and refuses a canonicalized destination that
    /// (1) has an existing ancestor carrying the retail-install shape —
    /// <c>BEA.exe</c> beside a <c>data</c> directory — or (2) reaches through
    /// an existing reparse point / symbolic link ancestor, which could divert a
    /// lexical-safe path into protected storage. Every refusal throws before
    /// the destination's parents are created.
    /// </summary>
    private static void EnsureSafeDestination(string fullPath)
    {
        // One identity per OS: on Windows every DOS device and extended-namespace
        // spelling (\\?\C:\..., \\.\C:\..., \\?\UNC\...) is folded to its plain
        // Win32 form before the ancestor walk, so a destination can never carry
        // an identity the boundary did not evaluate.
        bool osSensitive = OperatingSystem.IsWindows();

        bool identitySupported = true;
        string identityPath = osSensitive ? NormalizeWindowsNamespace(fullPath, out identitySupported) : fullPath;
        if (osSensitive && !identitySupported)
        {
            // The destination names a device namespace rather than an
            // ordinary path; there is no evaluated identity to compare.
            throw new ArgumentException(
                $"Command tape persistence refuses destinations in the Windows device namespace ('{fullPath}'); " +
                "command tapes are written only to ordinary file-system paths.");
        }
        if (osSensitive)
        {
            // The extended prefix suppresses GetFullPath normalization, so the
            // folded identity of a destination like \\?\C:\sibling\..\known\x
            // still carries dot segments the later create-new open WOULD
            // resolve. Re-canonicalize the folded identity so the boundary
            // always evaluates exactly what the open would use.
            identityPath = Path.GetFullPath(identityPath);
        }

        string? currentDirectory = Path.GetDirectoryName(identityPath);
        while (!string.IsNullOrEmpty(currentDirectory))
        {
            if (osSensitive)
            {
                currentDirectory = currentDirectory.TrimEnd(
                    Path.DirectorySeparatorChar,
                    Path.AltDirectorySeparatorChar);
                if (string.IsNullOrEmpty(currentDirectory))
                {
                    break;
                }
            }

            // Existing retail-install shape: BEA.exe directly beside a data
            // directory marks a retail install root regardless of whether this
            // host ever saw the real game there.
            string beaCandidate = Path.Combine(currentDirectory, "BEA.exe");
            string dataCandidate = Path.Combine(currentDirectory, "data");
            if (File.Exists(beaCandidate) && Directory.Exists(dataCandidate))
            {
                throw new ArgumentException(
                    $"Command tape persistence refuses destinations inside a retail install layout ('{currentDirectory}'); " +
                    "retail files are never valid recording targets.");
            }

            // Existing reparse-point ancestor: a junction or symlink above the
            // destination could resolve into protected storage even though the
            // written path looks safe lexically. Fail closed instead. A
            // non-null immediate target proves this path segment IS a link.
            FileSystemInfo? immediateLinkTarget;
            try
            {
                immediateLinkTarget =
                    Directory.ResolveLinkTarget(currentDirectory, returnFinalTarget: false);
            }
            catch (IOException)
            {
                // A path with unreadable metadata stays subject to the
                // remaining checks; only a PROVEN reparse point refuses here.
                immediateLinkTarget = null;
            }

            if (immediateLinkTarget is not null)
            {
                throw new ArgumentException(
                    $"Command tape persistence refuses destinations behind a reparse point or symbolic link ('{currentDirectory}'); " +
                    "a linked path can escape into career saves or a retail install.");
            }

            currentDirectory = Path.GetDirectoryName(currentDirectory);
        }
    }

    /// <summary>
    /// Folds the Windows DOS-device / extended-namespace ALIASES of ordinary
    /// file-system paths onto the one plain Win32 identity the boundary
    /// compares: <c>\\.\C:\...</c> and <c>\\?\C:\...</c> become
    /// <c>C:\...</c>, and <c>\\?\UNC\server\share\...</c> becomes
    /// <c>\\server\share\...</c>. A body that is NOT a proven alias of an
    /// ordinary path (for example <c>\\?\GLOBALROOT\...</c> or a volume GUID)
    /// is left untouched and reported in <paramref name="isSupported"/>;
    /// callers must refuse those rather than compare a fabricated identity.
    /// </summary>
    private static string NormalizeWindowsNamespace(string path, out bool isSupported)
    {
        const string DevicePrefix = @"\\.\";
        const string ExtendedPrefix = @"\\?\";
        isSupported = true;

        if (path.StartsWith(DevicePrefix, StringComparison.Ordinal))
        {
            path = ExtendedPrefix + path[DevicePrefix.Length..];
        }

        if (!path.StartsWith(ExtendedPrefix, StringComparison.Ordinal))
        {
            return path;
        }

        string body = path[ExtendedPrefix.Length..];
        const string UncPrefix = "UNC\\";
        if (body.StartsWith(UncPrefix, StringComparison.OrdinalIgnoreCase) && body.Length > UncPrefix.Length)
        {
            return @"\\" + body[UncPrefix.Length..];
        }

        // A drive-letter absolute body is the one other proven alias: the
        // extended prefix only removes parsing, never relocates the target.
        if (body.Length >= 3 &&
            char.IsAsciiLetter(body[0]) &&
            body[1] == Path.VolumeSeparatorChar &&
            (body[2] == Path.DirectorySeparatorChar || body[2] == Path.AltDirectorySeparatorChar))
        {
            return body;
        }

        // Anything else names something that is not an alias of an ordinary
        // path; refuse instead of comparing an unevaluated identity.
        isSupported = false;
        return body;
    }
}
