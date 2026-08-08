using System;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// What a memory handle is allowed to do. This exists so "open with the least access that
    /// works" is a value the caller passes rather than a comment somebody has to obey: a reading
    /// session asks for <see cref="Read"/> and physically cannot write.
    /// </summary>
    [Flags]
    public enum ProcessMemoryAccess
    {
        Read = 1,
        Write = 2,
        ReadWrite = Read | Write,
    }

    /// <summary>
    /// A handle to one process's address space, reduced to the two operations the trainer needs.
    ///
    /// Every Win32 call in the live-trainer lane sits behind this interface so the reader, the
    /// write gate, and the hold loop can all be unit-tested against a fake address space with no
    /// game running and no process opened. Implementations must never kill, suspend, or signal
    /// the process, and must never open more access than they were asked for.
    /// </summary>
    public interface IProcessMemoryAccessor : IDisposable
    {
        int ProcessId { get; }

        ProcessMemoryAccess Access { get; }

        /// <summary>
        /// Fills <paramref name="destination"/> from <paramref name="address"/>, or returns false
        /// and leaves the caller with nothing. A partial read is a failed read: half a pointer is
        /// worse than no pointer.
        /// </summary>
        bool TryRead(uint address, Span<byte> destination);

        /// <summary>
        /// Writes <paramref name="source"/> at <paramref name="address"/>. Returns false when the
        /// handle cannot write or the write did not complete.
        /// </summary>
        bool TryWrite(uint address, ReadOnlySpan<byte> source);
    }

    /// <summary>
    /// Opens accessors. Separated from <see cref="IProcessMemoryAccessor"/> because the attach
    /// gate has to be able to refuse before anything is opened, and a test needs to prove that
    /// nothing was opened when it refused.
    /// </summary>
    public interface IProcessMemoryAccessorFactory
    {
        bool TryOpen(
            int processId,
            ProcessMemoryAccess access,
            out IProcessMemoryAccessor? accessor,
            out string failure);
    }

    /// <summary>
    /// The real one: <c>OpenProcess</c> plus <c>ReadProcessMemory</c>/<c>WriteProcessMemory</c>.
    ///
    /// It asks for <c>PROCESS_VM_READ | PROCESS_QUERY_INFORMATION</c> to read, and only adds
    /// <c>PROCESS_VM_OPERATION | PROCESS_VM_WRITE</c> when the caller has actually asked for a
    /// write. It never asks for <c>PROCESS_ALL_ACCESS</c>, never asks for terminate rights, and
    /// holds nothing but a <see cref="SafeProcessHandle"/> that closes itself.
    ///
    /// This type is the only place in the toolkit that touches another process's memory. Keeping
    /// it that small is deliberate: it is the part that cannot be tested without a running game,
    /// so everything decidable is decided somewhere else.
    /// </summary>
    internal sealed class Win32ProcessMemoryAccessorFactory : IProcessMemoryAccessorFactory
    {
        public static Win32ProcessMemoryAccessorFactory Instance { get; } = new();

        public bool TryOpen(
            int processId,
            ProcessMemoryAccess access,
            out IProcessMemoryAccessor? accessor,
            out string failure)
        {
            accessor = null;
            failure = string.Empty;

            if (processId <= 0)
            {
                failure = "A positive process id is required.";
                return false;
            }

            uint desired = Win32ProcessMemoryAccessor.ProcessQueryInformation | Win32ProcessMemoryAccessor.ProcessVmRead;
            if ((access & ProcessMemoryAccess.Write) != 0)
            {
                desired |= Win32ProcessMemoryAccessor.ProcessVmOperation | Win32ProcessMemoryAccessor.ProcessVmWrite;
            }

            SafeProcessHandle handle = Win32ProcessMemoryAccessor.OpenProcess(desired, false, (uint)processId);
            if (handle.IsInvalid)
            {
                int error = Marshal.GetLastPInvokeError();
                handle.Dispose();
                failure = $"Could not open the game process for {(((access & ProcessMemoryAccess.Write) != 0) ? "reading and writing" : "reading")} (Win32 error {error}).";
                return false;
            }

            accessor = new Win32ProcessMemoryAccessor(processId, access, handle);
            return true;
        }
    }

    internal sealed class Win32ProcessMemoryAccessor : IProcessMemoryAccessor
    {
        internal const uint ProcessVmOperation = 0x0008;
        internal const uint ProcessVmRead = 0x0010;
        internal const uint ProcessVmWrite = 0x0020;
        internal const uint ProcessQueryInformation = 0x0400;

        private readonly SafeProcessHandle _handle;
        private bool _disposed;

        internal Win32ProcessMemoryAccessor(int processId, ProcessMemoryAccess access, SafeProcessHandle handle)
        {
            ProcessId = processId;
            Access = access;
            _handle = handle;
        }

        public int ProcessId { get; }

        public ProcessMemoryAccess Access { get; }

        public bool TryRead(uint address, Span<byte> destination)
        {
            if (_disposed || destination.Length == 0 || !FitsInAddressSpace(address, destination.Length))
                return false;

            if (!ReadProcessMemory(
                    _handle,
                    (IntPtr)address,
                    ref MemoryMarshal.GetReference(destination),
                    (IntPtr)destination.Length,
                    out IntPtr read))
            {
                return false;
            }

            // A short read is a failure, not a smaller answer.
            return (long)read == destination.Length;
        }

        public bool TryWrite(uint address, ReadOnlySpan<byte> source)
        {
            if (_disposed ||
                (Access & ProcessMemoryAccess.Write) == 0 ||
                source.Length == 0 ||
                !FitsInAddressSpace(address, source.Length))
            {
                return false;
            }

            if (!WriteProcessMemory(
                    _handle,
                    (IntPtr)address,
                    ref MemoryMarshal.GetReference(source),
                    (IntPtr)source.Length,
                    out IntPtr written))
            {
                return false;
            }

            return (long)written == source.Length;
        }

        public void Dispose()
        {
            if (_disposed)
                return;

            _disposed = true;
            _handle.Dispose();
        }

        private static bool FitsInAddressSpace(uint address, int length) =>
            (ulong)address + (ulong)length <= uint.MaxValue;

        [DllImport("kernel32.dll", SetLastError = true)]
        internal static extern SafeProcessHandle OpenProcess(
            uint dwDesiredAccess,
            [MarshalAs(UnmanagedType.Bool)] bool bInheritHandle,
            uint dwProcessId);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool ReadProcessMemory(
            SafeProcessHandle hProcess,
            IntPtr lpBaseAddress,
            ref byte lpBuffer,
            IntPtr nSize,
            out IntPtr lpNumberOfBytesRead);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool WriteProcessMemory(
            SafeProcessHandle hProcess,
            IntPtr lpBaseAddress,
            ref byte lpBuffer,
            IntPtr nSize,
            out IntPtr lpNumberOfBytesWritten);
    }
}
