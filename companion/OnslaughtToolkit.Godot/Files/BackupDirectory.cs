// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Files;

/// <summary>
/// One operation's recovery directory, copies and manifest. Linux writes relative to the held directory;
/// Windows holds every ancestor without delete sharing. Neither path falls back to an unprotected write.
/// The lease survives the game-file swap; it does not promise immunity to changes after disposal.
/// </summary>
internal sealed class BackupDirectory : IDisposable
{
    private readonly LinuxSaveDirectory? _linuxRoot, _linuxSet;
    private readonly FileMutationSafety.DirectoryLockSet? _windowsRoot, _windowsSet;
    private readonly List<(SaveLabSource Source, byte[] Bytes)> _copies = [];
    private FileStream? _manifest;
    private GuardedFileMutation? _manifestMutation;
    private byte[]? _manifestBytes;
    private string? _manifestIdentity;

    private BackupDirectory(string folder, LinuxSaveDirectory? linuxRoot, LinuxSaveDirectory? linuxSet,
        FileMutationSafety.DirectoryLockSet? windowsRoot, FileMutationSafety.DirectoryLockSet? windowsSet)
        => (Folder, _linuxRoot, _linuxSet, _windowsRoot, _windowsSet) =
            (folder, linuxRoot, linuxSet, windowsRoot, windowsSet);

    internal string Folder { get; }

    internal static BackupDirectory Create(string root, DateTime now)
    {
        LinuxSaveDirectory? linuxRoot = null, linuxSet = null;
        FileMutationSafety.DirectoryLockSet? windowsRoot = null, windowsSet = null;
        try
        {
            if (OperatingSystem.IsLinux()) linuxRoot = LinuxSaveDirectory.Open(root);
            else if (OperatingSystem.IsWindows()) windowsRoot = FileMutationSafety.LockDirectoryTree(root, "Backup root");
            else throw new PlatformNotSupportedException("Verified backups require supported Linux or Windows file protections.");
            string parent = windowsRoot?.PhysicalPath ?? root;
            string stem = $"onslaught-backup-{now:yyyyMMdd-HHmmss}";
            for (int suffix = 1; suffix <= 1000; suffix++)
            {
                string name = suffix == 1 ? stem : $"{stem}-{suffix}";
                string folder = Path.Combine(parent, name);
                try
                {
                    if (linuxRoot is not null) linuxSet = linuxRoot.CreateChild(name);
                    else
                    {
                        if (!CreateDirectory(folder, IntPtr.Zero))
                            throw new IOException("The backup folder could not be created exclusively.", new Win32Exception(Marshal.GetLastWin32Error()));
                        windowsSet = FileMutationSafety.LockDirectoryTree(folder, "Backup set");
                    }
                    BackupDirectory result = new(windowsSet?.PhysicalPath ?? folder, linuxRoot, linuxSet, windowsRoot, windowsSet);
                    result.Verify();
                    return result;
                }
                catch (IOException error) when (error.InnerException is Win32Exception native &&
                    native.NativeErrorCode == (OperatingSystem.IsLinux() ? 17 : 183))
                {
                    // Exclusive creation refused an occupied name. Never reuse or remove somebody else's folder.
                }
            }
            throw new IOException("Too many backup folders share this timestamp. Try again later.");
        }
        catch
        {
            linuxSet?.Dispose(); linuxRoot?.Dispose(); windowsSet?.Dispose(); windowsRoot?.Dispose();
            throw;
        }
    }

    internal void HoldCopy(string name, byte[] expected)
    {
        Verify();
        SaveLabSource source = SaveLabSource.Open(Path.Combine(Folder, name));
        try
        {
            source.Verify(expected, source.Identity);
            _copies.Add((source, expected.ToArray()));
            source = null!;
            Verify();
        }
        finally { source?.Dispose(); }
    }

    internal void PublishManifest(byte[] bytes)
    {
        if (_manifest is not null) throw new InvalidOperationException("This backup already has a manifest.");
        Verify();
        string identity;
        if (_linuxSet is not null)
        {
            _linuxSet.RequireVacant(Backups.ManifestName);
            using FileStream staged = _linuxSet.CreateUnnamed();
            staged.Write(bytes); staged.Flush(flushToDisk: true);
            LinuxSaveNative.Stat stat = LinuxSaveNative.Inspect(staged.SafeFileHandle);
            LinuxSaveNative.RequireRegular(stat, links: 0);
            identity = stat.Identity;
            VerifyBytes(staged, bytes);
            Verify();
            _linuxSet.RequireVacant(Backups.ManifestName);
            _linuxSet.Publish(staged.SafeFileHandle, Backups.ManifestName);
            _linuxSet.Flush();
            _manifest = _linuxSet.OpenRead(Backups.ManifestName);
        }
        else
        {
            _manifestMutation = FileMutationSafety.BeginGeneratedVacant(Path.Combine(Folder, Backups.ManifestName));
            _manifestMutation.Commit(bytes, beforePublish: _ => Verify());
            // Keep the transaction's no-write/no-delete-sharing committed handle for the full lease.
            _manifest = OpenManifest();
            identity = Identity(_manifest);
        }
        _manifestIdentity = identity;
        _manifestBytes = bytes.ToArray();
        Verify();
    }

    internal void Verify()
    {
        _linuxRoot?.Verify(); _linuxSet?.Verify();
        if (_windowsRoot is not null && _windowsSet is not null)
        {
            VerifyWindowsDirectory(_windowsRoot); VerifyWindowsDirectory(_windowsSet);
        }
        foreach ((SaveLabSource source, byte[] bytes) in _copies) source.Verify(bytes, source.Identity);
        if (_manifest is not null && _manifestBytes is not null)
        {
            if (Identity(_manifest) != _manifestIdentity) throw new IOException("The backup manifest changed identity.");
            VerifyBytes(_manifest, _manifestBytes);
            using FileStream current = OpenManifest();
            if (Identity(current) != _manifestIdentity) throw new IOException("The backup manifest was replaced.");
            VerifyBytes(current, _manifestBytes);
        }
        _linuxRoot?.Verify(); _linuxSet?.Verify();
    }

    private static void VerifyWindowsDirectory(FileMutationSafety.DirectoryLockSet held)
    {
        using FileMutationSafety.DirectoryLockSet current = FileMutationSafety.LockDirectoryTree(held.PhysicalPath, "Backup folder");
        if (!held.Identity.IsSameFile(current.Identity)) throw new IOException("The backup folder changed identity.");
    }

    private FileStream OpenManifest()
    {
        if (_linuxSet is not null) return _linuxSet.OpenRead(Backups.ManifestName);
        SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(Path.Combine(Folder, Backups.ManifestName), "Backup manifest");
        try
        {
            WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, "Backup manifest");
            if (identity.IsReparsePoint || identity.NumberOfLinks != 1) throw new IOException("The backup manifest must not use aliases.");
            return new FileStream(handle, FileAccess.Read);
        }
        catch { handle.Dispose(); throw; }
    }

    private static string Identity(FileStream stream)
    {
        if (OperatingSystem.IsLinux())
        {
            LinuxSaveNative.Stat stat = LinuxSaveNative.Inspect(stream.SafeFileHandle);
            LinuxSaveNative.RequireRegular(stat, links: 1);
            return stat.Identity;
        }
        WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(stream.SafeFileHandle, "Backup manifest");
        if (identity.IsReparsePoint || identity.NumberOfLinks != 1) throw new IOException("The backup manifest must not use aliases.");
        return $"{identity.VolumeSerialNumber}:{identity.FileIndex}";
    }

    private static void VerifyBytes(FileStream stream, byte[] expected)
    {
        if (stream.Length != expected.Length) throw new IOException("The backup manifest changed length.");
        stream.Position = 0;
        byte[] current = new byte[expected.Length]; stream.ReadExactly(current);
        if (!current.AsSpan().SequenceEqual(expected) || stream.ReadByte() != -1)
            throw new IOException("The backup manifest could not be verified.");
    }

    public void Dispose()
    {
        _manifest?.Dispose(); _manifestMutation?.Dispose();
        foreach ((SaveLabSource source, _) in _copies) source.Dispose();
        _linuxSet?.Dispose(); _linuxRoot?.Dispose(); _windowsSet?.Dispose(); _windowsRoot?.Dispose();
    }

    [DllImport("kernel32.dll", EntryPoint = "CreateDirectoryW", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool CreateDirectory(string path, IntPtr securityAttributes);
}

internal sealed class HeldBackup(BackupReceipt receipt, BackupDirectory? directory) : IDisposable
{
    internal BackupReceipt Receipt { get; } = receipt;
    internal void Verify()
    {
        try { (directory ?? throw new IOException("No verified backup is held.")).Verify(); }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidOperationException or NotSupportedException)
        { throw new BackupVerificationException(error); }
    }
    public void Dispose() => directory?.Dispose();
}

internal sealed class BackupVerificationException(Exception inner) : IOException(
    "The recovery backup could not be verified. Its folder or files changed; inspect it before relying on it.", inner);
