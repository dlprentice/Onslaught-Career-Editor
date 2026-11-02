// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Files;

internal sealed record CeProjectRead(bool Ok, string Message, byte[]? Bytes = null);
internal sealed record CeProjectWrite(bool Ok, string Message, string? Path = null, bool MayHaveOutput = false);

internal interface ICeMissionProjectFiles
{
    CeProjectRead Open(string path);
    CeProjectWrite WriteNew(string path, byte[] bytes, IReadOnlyList<string?> protectedFolders);
}

/// <summary>Protected bounded project reads and verified new-file publication. Existing project and game files are never replaced.</summary>
internal sealed class CeMissionProjectFiles(Action<string>? beforePublish = null, Action<string>? afterPublish = null) : ICeMissionProjectFiles
{
    internal const string Extension = ".ceproject";

    public CeProjectRead Open(string path)
    {
        try
        {
            using SaveLabSource source = SaveLabSource.Open(Normalize(path), ReadBounded);
            byte[] bytes = source.ReadBytes();
            source.Verify(bytes, source.Identity);
            return new(true, "Project read with verified identity and content.", bytes);
        }
        catch (Exception error) when (Expected(error)) { return new(false, Describe(error)); }
    }

    public CeProjectWrite WriteNew(string path, byte[] bytes, IReadOnlyList<string?> protectedFolders)
    {
        bool published = false;
        GuardedFileMutation? portable = null;
        try
        {
            string output = Normalize(path);
            if (bytes.Length is 0 or > CeMissionProject.MaxDocumentBytes) throw new InvalidDataException("The project is empty or too large.");
            byte[] owned = bytes.ToArray();
            _ = CeMissionProjectJson.Read(owned);
            string?[] protectedCopy = protectedFolders.ToArray();
            void Guard() => GuardOutput(output, protectedCopy);
            Guard();
            if (OperatingSystem.IsLinux())
            {
                using LinuxSaveDirectory directory = LinuxSaveDirectory.Open(Path.GetDirectoryName(output)!);
                string name = Path.GetFileName(output);
                directory.RequireVacant(name);
                using FileStream staged = directory.CreateUnnamed();
                staged.Write(owned);
                staged.Flush(flushToDisk: true);
                LinuxSaveNative.Stat identity = LinuxSaveNative.Inspect(staged.SafeFileHandle);
                LinuxSaveNative.RequireRegular(identity, links: 0);
                VerifyBytes(staged, owned);
                beforePublish?.Invoke(output);
                directory.Verify();
                Guard();
                directory.RequireVacant(name);
                LinuxSaveNative.Stat sealedIdentity = LinuxSaveNative.Inspect(staged.SafeFileHandle);
                LinuxSaveNative.RequireRegular(sealedIdentity, links: 0);
                if (identity.Identity != sealedIdentity.Identity) throw new IOException("The staged project changed identity.");
                directory.Publish(staged.SafeFileHandle, name);
                published = true;
                afterPublish?.Invoke(output);
                directory.Flush();
                directory.Verify();
                Guard();
                using FileStream reopened = directory.OpenRead(name);
                if (LinuxSaveNative.Inspect(reopened.SafeFileHandle).Identity != identity.Identity)
                    throw new IOException("The saved project changed identity before verification.");
                VerifyBytes(reopened, owned);
            }
            else if (OperatingSystem.IsWindows())
            {
                portable = FileMutationSafety.BeginGeneratedVacant(output);
                portable.Commit(owned, afterPublish, target => { beforePublish?.Invoke(target); Guard(); });
            }
            else throw new PlatformNotSupportedException("Protected project files support Linux and Windows.");
            return new(true, "Saved a new project and reopened it to verify every byte.", output);
        }
        catch (Exception error) when (Expected(error))
        {
            bool uncertain = published || portable?.Published == true;
            return new(false, uncertain ? "A project file may exist, but final verification failed. Keep it for inspection and choose a new filename. " + Describe(error)
                : Describe(error), MayHaveOutput: uncertain);
        }
        finally { portable?.Dispose(); }
    }

    private static string Normalize(string path)
    {
        if (string.IsNullOrWhiteSpace(path) || path != path.Trim() || !Path.IsPathFullyQualified(path))
            throw new InvalidDataException("Choose a full local project path without leading or trailing whitespace.");
        string normalized = FileMutationSafety.NormalizeLocalPath(path, "CE project");
        string name = Path.GetFileName(normalized);
        if (!string.Equals(Path.GetExtension(normalized), Extension, StringComparison.OrdinalIgnoreCase) ||
            name.StartsWith('.') || name.IndexOfAny(['\\', ':', '*', '?', '"', '<', '>', '|']) >= 0)
            throw new InvalidDataException("Choose a project filename ending in " + Extension + ".");
        return normalized;
    }

    private static void GuardOutput(string output, IReadOnlyList<string?> protectedFolders)
    {
        OutputGuard.Reject(output);
        string parent = Path.GetDirectoryName(output)!;
        string real = ExportFiles.RealPath(parent);
        foreach (string? folder in protectedFolders)
        {
            if (string.IsNullOrWhiteSpace(folder)) continue;
            string full = Path.GetFullPath(folder);
            if (ExportFiles.Inside(parent, full) || ExportFiles.Inside(real, ExportFiles.RealPath(full)))
                throw new InvalidDataException("Save projects outside the game, CE package, CE user folder and companion backups.");
        }
    }

    private static byte[] ReadBounded(FileStream stream)
    {
        long length = stream.Length;
        if (length is <= 0 or > CeMissionProject.MaxDocumentBytes) throw new InvalidDataException("The project is empty or too large.");
        byte[] bytes = new byte[(int)length];
        stream.Position = 0;
        stream.ReadExactly(bytes);
        if (stream.ReadByte() != -1 || stream.Length != length) throw new IOException("The project changed length while being read.");
        return bytes;
    }

    private static void VerifyBytes(FileStream stream, byte[] expected)
    {
        if (!ReadBounded(stream).AsSpan().SequenceEqual(expected)) throw new IOException("The saved project did not match the prepared bytes.");
    }

    private static bool Expected(Exception error) => error is IOException or InvalidDataException or UnauthorizedAccessException or ArgumentException or
        InvalidOperationException or NotSupportedException or System.Security.SecurityException or System.ComponentModel.Win32Exception or
        EntryPointNotFoundException or DllNotFoundException;

    private static string Describe(Exception error) => error switch
    {
        FileNotFoundException => "The selected project could not be found. Choose it again.",
        DirectoryNotFoundException => "Choose an existing local folder for the project.",
        UnauthorizedAccessException => "The project or its folder could not be accessed.",
        EntryPointNotFoundException or DllNotFoundException => "This system lacks the required project-file protections.",
        _ => error.Message,
    };
}
