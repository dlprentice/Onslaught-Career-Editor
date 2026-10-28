// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Options;

/// <summary>
/// Cooperative lock shared with CE's settings writer. The sidecar persists: deleting it can split writers
/// across different lock objects. This serializes only writers using the protocol and the same directory.
/// </summary>
internal sealed class CeSettingsWriteLock : IDisposable
{
    private const string LockName = "ce.ini.lock";
    private const int LinuxCreateReadWrite = 0x40 | 2 | 0x800 | 0x20000 | 0x80000;
    private const int LinuxExclusiveNonblocking = 2 | 4;
    private const uint GenericReadWrite = 0xC0000000, ShareReadWrite = 3, OpenExisting = 3, OpenAlways = 4;
    private const uint WindowsNormalNoFollow = 0x80 | 0x00200000;
    private readonly string _folder;
    private readonly SafeFileHandle _file;
    private readonly SafeFileHandle? _linuxDirectory;
    private readonly FileMutationSafety.DirectoryLockSet? _windowsDirectory;

    private CeSettingsWriteLock(string folder, SafeFileHandle file, SafeFileHandle? linuxDirectory,
        FileMutationSafety.DirectoryLockSet? windowsDirectory)
        => (_folder, _file, _linuxDirectory, _windowsDirectory) = (folder, file, linuxDirectory, windowsDirectory);

    /// <summary>Return null immediately if another cooperating writer holds the lock; unsafe files are refused.</summary>
    internal static CeSettingsWriteLock? TryAcquire(string folder)
    {
        if (OperatingSystem.IsLinux()) return TryAcquireLinux(folder);
        if (OperatingSystem.IsWindows()) return TryAcquireWindows(folder);
        throw new PlatformNotSupportedException("CE settings writes support Linux and Windows.");
    }

    private static CeSettingsWriteLock? TryAcquireLinux(string folder)
    {
        SafeFileHandle? directory = OpenLinuxDirectory(folder);
        SafeFileHandle? file = null;
        try
        {
            file = LinuxSaveNative.OpenAt(directory.DangerousGetHandle().ToInt32(), LockName, LinuxCreateReadWrite, 0x180);
            LinuxSaveNative.RequireRegular(LinuxSaveNative.Inspect(file), links: 1);
            if (Flock(file, LinuxExclusiveNonblocking) != 0)
            {
                int error = Marshal.GetLastWin32Error();
                if (error == 11) return null; // EWOULDBLOCK / EAGAIN
                throw LinuxSaveNative.Failure("The CE settings lock could not be acquired.", error);
            }
            CeSettingsWriteLock result = new(folder, file, directory, null);
            result.Verify();
            file = null; directory = null;
            return result;
        }
        finally { file?.Dispose(); directory?.Dispose(); }
    }

    private static SafeFileHandle OpenLinuxDirectory(string folder)
    {
        if (!System.IO.Path.IsPathFullyQualified(folder))
            throw new IOException("CE's user folder must be an absolute path.");
        string full = System.IO.Path.GetFullPath(folder);
        SafeFileHandle current = LinuxSaveNative.OpenAt(LinuxSaveNative.AtCurrentDirectory, "/", LinuxSaveNative.ReadDirectory, 0);
        try
        {
            foreach (string segment in full.Split('/', StringSplitOptions.RemoveEmptyEntries))
            {
                SafeFileHandle next = LinuxSaveNative.OpenAt(current.DangerousGetHandle().ToInt32(), segment,
                    LinuxSaveNative.ReadDirectory, 0);
                current.Dispose();
                current = next;
            }
            return current;
        }
        catch { current.Dispose(); throw; }
    }

    private static CeSettingsWriteLock? TryAcquireWindows(string folder)
    {
        FileMutationSafety.DirectoryLockSet? directory = FileMutationSafety.LockDirectoryTree(folder, "CE user folder");
        SafeFileHandle? file = null;
        try
        {
            string path = System.IO.Path.Combine(directory.PhysicalPath, LockName);
            file = OpenWindows(path, OpenAlways);
            RequireWindowsRegular(file);
            Overlapped overlap = new();
            if (!LockFileEx(file, 3, 0, 1, 0, ref overlap)) // exclusive, fail immediately, byte range [0, 1)
            {
                int error = Marshal.GetLastWin32Error();
                if (error == 33) return null; // ERROR_LOCK_VIOLATION
                throw new IOException("The CE settings lock could not be acquired.", new Win32Exception(error));
            }
            CeSettingsWriteLock result = new(directory.PhysicalPath, file, null, directory);
            result.Verify();
            file = null; directory = null;
            return result;
        }
        finally { file?.Dispose(); directory?.Dispose(); }
    }

    /// <summary>Check that the still-held sidecar and folder remain the ones other writers will see.</summary>
    internal void Verify()
    {
        if (_linuxDirectory is not null)
        {
            using SafeFileHandle namedDirectory = OpenLinuxDirectory(_folder);
            if (LinuxSaveNative.Inspect(_linuxDirectory).Identity != LinuxSaveNative.Inspect(namedDirectory).Identity)
                throw new IOException("CE's user folder changed while settings were being saved.");
            using SafeFileHandle namedFile = LinuxSaveNative.OpenAt(namedDirectory.DangerousGetHandle().ToInt32(), LockName,
                LinuxSaveNative.ReadFile, 0);
            LinuxSaveNative.Stat held = LinuxSaveNative.Inspect(_file), named = LinuxSaveNative.Inspect(namedFile);
            LinuxSaveNative.RequireRegular(held, links: 1);
            LinuxSaveNative.RequireRegular(named, links: 1);
            if (held.Identity != named.Identity)
                throw new IOException("The CE settings lock changed while settings were being saved.");
            return;
        }
        if (_windowsDirectory is null) throw new IOException("The CE settings lock has no protected folder.");
        using SafeFileHandle current = OpenWindows(System.IO.Path.Combine(_folder, LockName), OpenExisting);
        WindowsFileIdentity heldWindows = RequireWindowsRegular(_file), namedWindows = RequireWindowsRegular(current);
        if (!heldWindows.IsSameFile(namedWindows))
            throw new IOException("The CE settings lock changed while settings were being saved.");
    }

    private static SafeFileHandle OpenWindows(string path, uint disposition)
    {
        SafeFileHandle handle = CreateFileW(path, GenericReadWrite, ShareReadWrite, IntPtr.Zero, disposition,
            WindowsNormalNoFollow, IntPtr.Zero);
        if (!handle.IsInvalid) return handle;
        int error = Marshal.GetLastWin32Error();
        handle.Dispose();
        throw new IOException("The CE settings lock could not be opened safely.", new Win32Exception(error));
    }

    private static WindowsFileIdentity RequireWindowsRegular(SafeFileHandle handle)
    {
        WindowsFileIdentity identity = FileMutationSafety.GetWindowsIdentity(handle, "CE settings lock");
        if (GetFileType(handle) != 1 || identity.IsReparsePoint || identity.NumberOfLinks != 1 ||
            ((FileAttributes)identity.Attributes & FileAttributes.Directory) != 0)
            throw new IOException("The CE settings lock must be a regular file without links.");
        return identity;
    }

    public void Dispose()
    {
        _file.Dispose(); // Closing this handle releases the OS lock, including after an abnormal process exit.
        _linuxDirectory?.Dispose();
        _windowsDirectory?.Dispose();
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct Overlapped { public UIntPtr Internal, InternalHigh; public uint Offset, OffsetHigh; public IntPtr Event; }

    [DllImport("libc", EntryPoint = "flock", SetLastError = true)]
    private static extern int Flock(SafeFileHandle file, int operation);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateFileW(string name, uint access, uint share, IntPtr security,
        uint disposition, uint flags, IntPtr template);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool LockFileEx(SafeFileHandle file, uint flags, uint reserved,
        uint low, uint high, ref Overlapped overlap);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint GetFileType(SafeFileHandle file);
}
