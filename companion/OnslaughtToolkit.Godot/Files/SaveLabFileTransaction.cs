using Microsoft.Win32.SafeHandles;
using System.ComponentModel;
using System.Runtime.InteropServices;

namespace OnslaughtCareerEditor.AppCore;

internal sealed class SaveLabPublicationException : IOException
{
    internal SaveLabPublicationException(string outputPath, Exception inner)
        : base("The copy could not be verified after publication started. A new output may exist; inspect it before using it.", inner)
        => OutputPath = outputPath;
    internal string OutputPath { get; }
}

/// <summary>A read-only source held only while opening or writing, never across UI interactions.</summary>
internal sealed class SaveLabSource : IDisposable
{
    private readonly IDisposable _directory;
    private readonly FileStream _stream;
    private SaveLabSource(string path, IDisposable directory, FileStream stream, string identity)
        => (Path, _directory, _stream, Identity) = (path, directory, stream, identity);

    internal string Path { get; }
    internal string Identity { get; }

    internal static SaveLabSource Open(string path)
    {
        if (OperatingSystem.IsLinux())
        {
            LinuxSaveDirectory directory = LinuxSaveDirectory.Open(System.IO.Path.GetDirectoryName(path)!);
            try
            {
                FileStream stream = directory.OpenRead(System.IO.Path.GetFileName(path));
                try
                {
                    LinuxSaveNative.Stat stat = LinuxSaveNative.Inspect(stream.SafeFileHandle);
                    LinuxSaveNative.RequireRegular(stat, links: 1);
                    directory.Verify();
                    return new(path, directory, stream, stat.Identity);
                }
                catch { stream.Dispose(); throw; }
            }
            catch { directory.Dispose(); throw; }
        }
        if (!OperatingSystem.IsWindows())
            throw new PlatformNotSupportedException("Verified save copies currently support Linux and Windows.");

        FileMutationSafety.DirectoryLockSet locks = FileMutationSafety.LockDirectoryTree(
            System.IO.Path.GetDirectoryName(path)!, "Source folder");
        try
        {
            SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(path, "Source save");
            try
            {
                WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, "Source save");
                if (identity.IsReparsePoint || identity.NumberOfLinks != 1)
                    throw new IOException("The source save must be a regular file without links.");
                FileStream stream = new(handle, FileAccess.Read);
                return new(path, locks, stream, $"{identity.VolumeSerialNumber}:{identity.FileIndex}");
            }
            catch { handle.Dispose(); throw; }
        }
        catch { locks.Dispose(); throw; }
    }

    internal byte[] ReadBytes() => ReadSaveBytes(_stream);

    internal static byte[] ReadSaveBytes(FileStream stream)
    {
        if (stream.Length != BesFilePatcher.EXPECTED_FILE_SIZE)
            throw new IOException($"A supported career save must contain exactly {BesFilePatcher.EXPECTED_FILE_SIZE:N0} bytes.");
        byte[] bytes = new byte[BesFilePatcher.EXPECTED_FILE_SIZE];
        stream.Position = 0;
        stream.ReadExactly(bytes);
        if (stream.ReadByte() != -1)
            throw new IOException("The career save changed length while it was being read.");
        return bytes;
    }

    internal void Verify(ReadOnlySpan<byte> baseline, string identity)
    {
        if (!string.Equals(Identity, identity, StringComparison.Ordinal) || !ReadBytes().AsSpan().SequenceEqual(baseline))
            throw new IOException("The original save changed after it was opened. Open it again before editing.");
        if (_directory is LinuxSaveDirectory linux)
        {
            linux.Verify();
            using FileStream named = linux.OpenRead(System.IO.Path.GetFileName(Path));
            LinuxSaveNative.Stat stat = LinuxSaveNative.Inspect(named.SafeFileHandle);
            LinuxSaveNative.RequireRegular(stat, links: 1);
            if (stat.Identity != identity || !ReadSaveBytes(named).AsSpan().SequenceEqual(baseline))
                throw new IOException("The original save changed after it was opened. Open it again before editing.");
        }
        // Windows holds the source and ancestor handles without write/delete sharing.
    }

    public void Dispose()
    {
        _stream.Dispose();
        _directory.Dispose();
    }
}

internal static class SaveLabFileTransaction
{
    internal static byte[] PublishNew(string output, SaveLabSource source, byte[] bytes,
        ReadOnlySpan<byte> baseline, string sourceIdentity, Action? beforePublish)
    {
        FileMutationSafety.RejectOutputInGameTree(output);
        if (OperatingSystem.IsLinux())
            return PublishLinux(output, source, bytes, baseline, sourceIdentity, beforePublish);
        if (!OperatingSystem.IsWindows())
            throw new PlatformNotSupportedException("Verified save copies currently support Linux and Windows.");

        // Reuse the Windows transaction, including its physical directory locks, staged quarantine,
        // protected-source identities and committed-file hash. Vacant output is enforced at publication.
        using GuardedFileMutation mutation = FileMutationSafety.BeginGeneratedVacant(output, source.Path);
        if (!mutation.ReadAllBytes(source.Path).AsSpan().SequenceEqual(baseline))
            throw new IOException("The original save changed after it was opened. Open it again before editing.");
        byte[] baselineBytes = baseline.ToArray();
        bool publicationStarted = false;
        try
        {
            mutation.Commit(bytes, beforePublish: _ =>
            {
                beforePublish?.Invoke();
                source.Verify(baselineBytes, sourceIdentity);
                publicationStarted = true;
            });
            source.Verify(baseline, sourceIdentity);
            using SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(output, "New save copy");
            using FileStream reopened = new(handle, FileAccess.Read);
            return VerifyCopy(reopened, bytes);
        }
        catch (Exception error) when (publicationStarted)
        {
            throw new SaveLabPublicationException(output, error);
        }
    }

    private static byte[] PublishLinux(string output, SaveLabSource source, byte[] bytes,
        ReadOnlySpan<byte> baseline, string sourceIdentity, Action? beforePublish)
    {
        using LinuxSaveDirectory directory = LinuxSaveDirectory.Open(System.IO.Path.GetDirectoryName(output)!);
        string name = System.IO.Path.GetFileName(output);
        directory.RequireVacant(name);
        // O_TMPFILE keeps incomplete data unnamed. No named staging path is exposed for alias swaps.
        using FileStream staged = directory.CreateUnnamed();
        staged.Write(bytes);
        staged.Flush(flushToDisk: true);
        LinuxSaveNative.Stat identity = LinuxSaveNative.Inspect(staged.SafeFileHandle);
        LinuxSaveNative.RequireRegular(identity, links: 0);
        VerifyCopy(staged, bytes);
        beforePublish?.Invoke();
        directory.Verify();
        FileMutationSafety.RejectOutputInGameTree(output);
        source.Verify(baseline, sourceIdentity);
        directory.RequireVacant(name);
        LinuxSaveNative.Stat sealedIdentity = LinuxSaveNative.Inspect(staged.SafeFileHandle);
        LinuxSaveNative.RequireRegular(sealedIdentity, links: 0);
        if (identity.Identity != sealedIdentity.Identity)
            throw new IOException("The staged save changed identity before publication.");

        // linkat creates the destination entry atomically and fails if any entry already exists,
        // including a dangling symbolic link. /proc/self/fd avoids privileged AT_EMPTY_PATH linking.
        directory.Publish(staged.SafeFileHandle, name);
        try
        {
            directory.Flush();
            directory.Verify();
            FileMutationSafety.RejectOutputInGameTree(output);
            using FileStream reopened = directory.OpenRead(name);
            LinuxSaveNative.Stat committed = LinuxSaveNative.Inspect(reopened.SafeFileHandle);
            LinuxSaveNative.RequireRegular(committed, links: 1);
            if (committed.Identity != identity.Identity)
                throw new IOException("The new output changed identity after publication.");
            byte[] verified = VerifyCopy(reopened, bytes);
            source.Verify(baseline, sourceIdentity);
            return verified;
        }
        catch (Exception error)
        {
            // Never delete by output name after publication: another process may have replaced it.
            throw new SaveLabPublicationException(output, error);
        }
    }

    private static byte[] VerifyCopy(FileStream stream, byte[] expected)
    {
        byte[] actual = SaveLabSource.ReadSaveBytes(stream);
        if (!actual.AsSpan().SequenceEqual(expected))
            throw new IOException("The new copy did not match the prepared save bytes.");
        return actual;
    }
}

/// <summary>Only the Linux descriptor operations needed by create-new Save Lab copies.</summary>
internal sealed class LinuxSaveDirectory : IDisposable
{
    private readonly SafeFileHandle _handle;
    private readonly string _identity;
    private readonly string _path;
    private LinuxSaveDirectory(string path, SafeFileHandle handle)
        => (_path, _handle, _identity) = (path, handle, LinuxSaveNative.Inspect(handle).Identity);

    internal static LinuxSaveDirectory Open(string path)
    {
        if (!OperatingSystem.IsLinux() || RuntimeInformation.ProcessArchitecture is not Architecture.X64)
            throw new PlatformNotSupportedException("Verified save copies require a supported Linux x64 file system.");
        string fullPath = System.IO.Path.GetFullPath(path);
        SafeFileHandle current = LinuxSaveNative.OpenAt(LinuxSaveNative.AtCurrentDirectory, "/",
            LinuxSaveNative.ReadDirectory, 0);
        try
        {
            foreach (string segment in fullPath.Split('/', StringSplitOptions.RemoveEmptyEntries))
            {
                SafeFileHandle next = LinuxSaveNative.OpenAt(current.DangerousGetHandle().ToInt32(), segment,
                    LinuxSaveNative.ReadDirectory, 0);
                current.Dispose();
                current = next;
            }
            return new(fullPath, current);
        }
        catch { current.Dispose(); throw; }
    }

    internal void Verify()
    {
        using LinuxSaveDirectory current = Open(_path);
        if (_identity != current._identity)
            throw new IOException("The selected folder changed. Choose it again before writing a copy.");
    }

    internal FileStream OpenRead(string name)
    {
        SafeFileHandle handle = LinuxSaveNative.OpenAt(_handle.DangerousGetHandle().ToInt32(), name,
            LinuxSaveNative.ReadFile, 0);
        try
        {
            LinuxSaveNative.RequireRegular(LinuxSaveNative.Inspect(handle), links: 1);
            return new FileStream(handle, FileAccess.Read);
        }
        catch { handle.Dispose(); throw; }
    }

    internal FileStream CreateUnnamed()
    {
        SafeFileHandle handle = LinuxSaveNative.OpenAt(_handle.DangerousGetHandle().ToInt32(), ".",
            LinuxSaveNative.UnnamedFile, 0x180); // 0600
        try
        {
            LinuxSaveNative.RequireRegular(LinuxSaveNative.Inspect(handle), links: 0);
            return new FileStream(handle, FileAccess.ReadWrite);
        }
        catch { handle.Dispose(); throw; }
    }

    internal void RequireVacant(string name)
    {
        int result = LinuxSaveNative.StatAt(_handle.DangerousGetHandle().ToInt32(), name,
            LinuxSaveNative.NoFollow, LinuxSaveNative.RequiredStatMask, out _);
        int error = Marshal.GetLastWin32Error();
        if (result == 0)
            throw new IOException("The output file already exists. Choose a new filename; existing files are never replaced.");
        if (error != 2) // ENOENT is the only accepted absence result.
            throw LinuxSaveNative.Failure("The output location could not be inspected safely.", error);
    }

    internal void Publish(SafeFileHandle staged, string name)
    {
        if (LinuxSaveNative.LinkAt(LinuxSaveNative.AtCurrentDirectory,
            $"/proc/self/fd/{staged.DangerousGetHandle().ToInt32()}",
            _handle.DangerousGetHandle().ToInt32(), name, 0x400) != 0) // AT_SYMLINK_FOLLOW on own fd
        {
            int error = Marshal.GetLastWin32Error();
            throw LinuxSaveNative.Failure(error == 17
                ? "The output file already exists. Choose a new filename; existing files are never replaced."
                : "This folder cannot publish a protected new copy. Choose another local folder.", error);
        }
    }

    internal void Flush()
    {
        if (LinuxSaveNative.Sync(_handle.DangerousGetHandle().ToInt32()) != 0)
            throw LinuxSaveNative.Failure("The new copy's folder could not be flushed to storage.", Marshal.GetLastWin32Error());
    }

    public void Dispose() => _handle.Dispose();
}

internal static class LinuxSaveNative
{
    internal const int AtCurrentDirectory = -100;
    internal const int NoFollow = 0x100;
    internal const uint RequiredStatMask = 0x307; // type, mode, links, inode, size
    internal const int ReadDirectory = 0x10000 | 0x20000 | 0x80000; // O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC
    internal const int ReadFile = 0x20000 | 0x80000 | 0x800; // O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK
    internal const int UnnamedFile = 0x410000 | 0x80000 | 2; // O_TMPFILE | O_CLOEXEC | O_RDWR

    // Linux statx has a fixed 256-byte ABI, unlike architecture-specific libc struct stat.
    [StructLayout(LayoutKind.Explicit, Size = 256)]
    internal struct Stat
    {
        [FieldOffset(0)] internal uint Mask;
        [FieldOffset(16)] internal uint Links;
        [FieldOffset(28)] internal ushort Mode;
        [FieldOffset(32)] internal ulong Inode;
        [FieldOffset(40)] internal ulong Size;
        [FieldOffset(136)] internal uint DeviceMajor;
        [FieldOffset(140)] internal uint DeviceMinor;
        internal readonly string Identity => $"{DeviceMajor}:{DeviceMinor}:{Inode}";
    }

    internal static SafeFileHandle OpenAt(int directory, string name, int flags, uint mode)
    {
        int fd = OpenAtNative(directory, name, flags, mode);
        if (fd < 0)
        {
            int error = Marshal.GetLastWin32Error();
            throw Failure(error == 40 ? "Files and folders must not use symbolic links."
                : "The selected file or folder could not be opened with the required protections.", error);
        }
        return new SafeFileHandle(new IntPtr(fd), ownsHandle: true);
    }

    internal static Stat Inspect(SafeFileHandle handle)
    {
        if (StatAt(handle.DangerousGetHandle().ToInt32(), "", 0x1000, RequiredStatMask, out Stat stat) != 0)
            throw Failure("This file system cannot provide the required file identity.", Marshal.GetLastWin32Error());
        if ((stat.Mask & RequiredStatMask) != RequiredStatMask)
            throw new IOException("This file system cannot provide the required file identity.");
        return stat;
    }

    internal static void RequireRegular(Stat stat, uint links)
    {
        if ((stat.Mode & 0xF000) != 0x8000 || stat.Links != links)
            throw new IOException("The save must be a regular file without aliases.");
    }

    internal static IOException Failure(string message, int error) => new(message, new Win32Exception(error));

    [DllImport("libc", EntryPoint = "openat", SetLastError = true)]
    private static extern int OpenAtNative(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string name, int flags, uint mode);

    [DllImport("libc", EntryPoint = "statx", SetLastError = true)]
    internal static extern int StatAt(int directory, [MarshalAs(UnmanagedType.LPUTF8Str)] string name,
        int flags, uint mask, out Stat stat);

    [DllImport("libc", EntryPoint = "linkat", SetLastError = true)]
    internal static extern int LinkAt(int oldDirectory, [MarshalAs(UnmanagedType.LPUTF8Str)] string oldName,
        int newDirectory, [MarshalAs(UnmanagedType.LPUTF8Str)] string newName, int flags);

    [DllImport("libc", EntryPoint = "fsync", SetLastError = true)]
    internal static extern int Sync(int fd);
}
