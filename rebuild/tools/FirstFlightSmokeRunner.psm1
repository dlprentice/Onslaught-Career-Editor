# SPDX-License-Identifier: GPL-3.0-or-later

Set-StrictMode -Version Latest

if ($null -eq ('OnslaughtRebuild.Tools.OwnedJobProcess' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;

namespace OnslaughtRebuild.Tools
{
    public sealed class OwnedJobProcess : IDisposable
    {
        private const uint CREATE_SUSPENDED = 0x00000004;
        private const uint CREATE_NO_WINDOW = 0x08000000;
        private const uint JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000;
        private const int JobObjectExtendedLimitInformation = 9;
        private const uint WAIT_OBJECT_0 = 0;
        private const uint WAIT_TIMEOUT = 258;
        private const uint Infinite = 0xFFFFFFFF;

        private IntPtr _jobHandle;
        private IntPtr _processHandle;
        private bool _disposed;

        private OwnedJobProcess(IntPtr jobHandle, IntPtr processHandle, int processId)
        {
            _jobHandle = jobHandle;
            _processHandle = processHandle;
            ProcessId = processId;
        }

        public int ProcessId { get; private set; }

        public static OwnedJobProcess Start(string fileName, string[] arguments)
        {
            if (string.IsNullOrWhiteSpace(fileName))
            {
                throw new ArgumentException("Process filename is required.", "fileName");
            }

            IntPtr jobHandle = CreateJobObjectW(IntPtr.Zero, null);
            if (jobHandle == IntPtr.Zero)
            {
                throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateJobObject failed.");
            }

            PROCESS_INFORMATION processInfo = new PROCESS_INFORMATION();
            bool processCreated = false;
            bool processAssigned = false;
            try
            {
                ConfigureKillOnClose(jobHandle);

                STARTUPINFO startupInfo = new STARTUPINFO();
                startupInfo.cb = Marshal.SizeOf(typeof(STARTUPINFO));
                StringBuilder commandLine = BuildCommandLine(fileName, arguments ?? new string[0]);
                processCreated = CreateProcessW(
                    fileName,
                    commandLine,
                    IntPtr.Zero,
                    IntPtr.Zero,
                    false,
                    CREATE_SUSPENDED | CREATE_NO_WINDOW,
                    IntPtr.Zero,
                    null,
                    ref startupInfo,
                    out processInfo);
                if (!processCreated)
                {
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "CreateProcess failed.");
                }

                if (!AssignProcessToJobObject(jobHandle, processInfo.hProcess))
                {
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "AssignProcessToJobObject failed.");
                }
                processAssigned = true;

                uint resumeResult = ResumeThread(processInfo.hThread);
                if (resumeResult == uint.MaxValue)
                {
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "ResumeThread failed.");
                }

                CloseHandle(processInfo.hThread);
                processInfo.hThread = IntPtr.Zero;
                return new OwnedJobProcess(jobHandle, processInfo.hProcess, checked((int)processInfo.dwProcessId));
            }
            catch
            {
                if (processCreated)
                {
                    if (processAssigned)
                    {
                        TerminateJobObject(jobHandle, 137);
                    }
                    else
                    {
                        TerminateProcess(processInfo.hProcess, 137);
                    }
                }
                if (processInfo.hThread != IntPtr.Zero)
                {
                    CloseHandle(processInfo.hThread);
                }
                if (processInfo.hProcess != IntPtr.Zero)
                {
                    CloseHandle(processInfo.hProcess);
                }
                CloseHandle(jobHandle);
                throw;
            }
        }

        public bool WaitForExit(int timeoutMilliseconds)
        {
            ThrowIfDisposed();
            uint result = WaitForSingleObject(_processHandle, checked((uint)timeoutMilliseconds));
            if (result == WAIT_OBJECT_0)
            {
                return true;
            }
            if (result == WAIT_TIMEOUT)
            {
                return false;
            }
            throw new Win32Exception(Marshal.GetLastWin32Error(), "WaitForSingleObject failed.");
        }

        public int GetExitCode()
        {
            ThrowIfDisposed();
            uint exitCode;
            if (!GetExitCodeProcess(_processHandle, out exitCode))
            {
                throw new Win32Exception(Marshal.GetLastWin32Error(), "GetExitCodeProcess failed.");
            }
            return unchecked((int)exitCode);
        }

        public void TerminateAndWait(int timeoutMilliseconds)
        {
            ThrowIfDisposed();
            if (!TerminateJobObject(_jobHandle, 137))
            {
                int error = Marshal.GetLastWin32Error();
                if (error != 5)
                {
                    throw new Win32Exception(error, "TerminateJobObject failed.");
                }
            }
            if (!WaitForExit(timeoutMilliseconds))
            {
                throw new TimeoutException("Owned process did not terminate after its job was stopped.");
            }
        }

        public void Dispose()
        {
            if (_disposed)
            {
                return;
            }
            _disposed = true;

            if (_jobHandle != IntPtr.Zero)
            {
                CloseHandle(_jobHandle);
                _jobHandle = IntPtr.Zero;
            }
            if (_processHandle != IntPtr.Zero)
            {
                CloseHandle(_processHandle);
                _processHandle = IntPtr.Zero;
            }
        }

        private static void ConfigureKillOnClose(IntPtr jobHandle)
        {
            JOBOBJECT_EXTENDED_LIMIT_INFORMATION limits = new JOBOBJECT_EXTENDED_LIMIT_INFORMATION();
            limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
            int size = Marshal.SizeOf(typeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION));
            IntPtr buffer = Marshal.AllocHGlobal(size);
            try
            {
                Marshal.StructureToPtr(limits, buffer, false);
                if (!SetInformationJobObject(jobHandle, JobObjectExtendedLimitInformation, buffer, (uint)size))
                {
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "SetInformationJobObject failed.");
                }
            }
            finally
            {
                Marshal.FreeHGlobal(buffer);
            }
        }

        private static StringBuilder BuildCommandLine(string fileName, string[] arguments)
        {
            StringBuilder commandLine = new StringBuilder();
            commandLine.Append(QuoteArgument(fileName));
            foreach (string argument in arguments)
            {
                commandLine.Append(' ');
                commandLine.Append(QuoteArgument(argument ?? string.Empty));
            }
            return commandLine;
        }

        private static string QuoteArgument(string argument)
        {
            if (argument.Length > 0 && argument.IndexOfAny(new[] { ' ', '\t', '\n', '\v', '"' }) < 0)
            {
                return argument;
            }

            StringBuilder quoted = new StringBuilder();
            quoted.Append('"');
            int backslashes = 0;
            foreach (char character in argument)
            {
                if (character == '\\')
                {
                    backslashes++;
                }
                else if (character == '"')
                {
                    quoted.Append('\\', backslashes * 2 + 1);
                    quoted.Append('"');
                    backslashes = 0;
                }
                else
                {
                    quoted.Append('\\', backslashes);
                    quoted.Append(character);
                    backslashes = 0;
                }
            }
            quoted.Append('\\', backslashes * 2);
            quoted.Append('"');
            return quoted.ToString();
        }

        private void ThrowIfDisposed()
        {
            if (_disposed)
            {
                throw new ObjectDisposedException("OwnedJobProcess");
            }
        }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
        private struct STARTUPINFO
        {
            public int cb;
            public string lpReserved;
            public string lpDesktop;
            public string lpTitle;
            public int dwX;
            public int dwY;
            public int dwXSize;
            public int dwYSize;
            public int dwXCountChars;
            public int dwYCountChars;
            public int dwFillAttribute;
            public int dwFlags;
            public short wShowWindow;
            public short cbReserved2;
            public IntPtr lpReserved2;
            public IntPtr hStdInput;
            public IntPtr hStdOutput;
            public IntPtr hStdError;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct PROCESS_INFORMATION
        {
            public IntPtr hProcess;
            public IntPtr hThread;
            public uint dwProcessId;
            public uint dwThreadId;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct JOBOBJECT_BASIC_LIMIT_INFORMATION
        {
            public long PerProcessUserTimeLimit;
            public long PerJobUserTimeLimit;
            public uint LimitFlags;
            public UIntPtr MinimumWorkingSetSize;
            public UIntPtr MaximumWorkingSetSize;
            public uint ActiveProcessLimit;
            public UIntPtr Affinity;
            public uint PriorityClass;
            public uint SchedulingClass;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct IO_COUNTERS
        {
            public ulong ReadOperationCount;
            public ulong WriteOperationCount;
            public ulong OtherOperationCount;
            public ulong ReadTransferCount;
            public ulong WriteTransferCount;
            public ulong OtherTransferCount;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
        {
            public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
            public IO_COUNTERS IoInfo;
            public UIntPtr ProcessMemoryLimit;
            public UIntPtr JobMemoryLimit;
            public UIntPtr PeakProcessMemoryUsed;
            public UIntPtr PeakJobMemoryUsed;
        }

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern IntPtr CreateJobObjectW(IntPtr jobAttributes, string name);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool SetInformationJobObject(IntPtr job, int infoClass, IntPtr info, uint length);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);

        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        private static extern bool CreateProcessW(
            string applicationName,
            StringBuilder commandLine,
            IntPtr processAttributes,
            IntPtr threadAttributes,
            bool inheritHandles,
            uint creationFlags,
            IntPtr environment,
            string currentDirectory,
            ref STARTUPINFO startupInfo,
            out PROCESS_INFORMATION processInformation);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern uint ResumeThread(IntPtr thread);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern uint WaitForSingleObject(IntPtr handle, uint milliseconds);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool GetExitCodeProcess(IntPtr process, out uint exitCode);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool TerminateJobObject(IntPtr job, uint exitCode);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool TerminateProcess(IntPtr process, uint exitCode);

        [DllImport("kernel32.dll")]
        private static extern bool CloseHandle(IntPtr handle);
    }
}
'@
}

function Assert-NoReparsePathComponents {
    param([Parameter(Mandatory)][string]$Path)

    $fullPath = [IO.Path]::GetFullPath($Path)
    $current = $fullPath
    while (-not [string]::IsNullOrWhiteSpace($current)) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "First Flight smoke path contains a reparse point: $($item.FullName)"
            }
        }

        $parent = [IO.Path]::GetDirectoryName($current)
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) {
            break
        }
        $current = $parent
    }
}

function New-BoundedFirstFlightSmokeRoot {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$RepoRoot)

    $repo = [IO.Path]::GetFullPath($RepoRoot)
    if (-not (Test-Path -LiteralPath $repo -PathType Container)) {
        throw "First Flight repo root does not exist: $repo"
    }
    Assert-NoReparsePathComponents -Path $repo

    $proofRoot = [IO.Path]::GetFullPath((Join-Path $repo 'local-proofs\rebuild-godot'))
    $requiredPrefix = $repo.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (-not $proofRoot.StartsWith($requiredPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'First Flight proof root escaped the repository.'
    }
    Assert-NoReparsePathComponents -Path $proofRoot
    $null = [IO.Directory]::CreateDirectory($proofRoot)
    Assert-NoReparsePathComponents -Path $proofRoot

    $runName = 'smoke-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + [guid]::NewGuid().ToString('N')
    $runRoot = Join-Path $proofRoot $runName
    if (Test-Path -LiteralPath $runRoot) {
        throw "First Flight smoke output root already exists: $runRoot"
    }
    $null = [IO.Directory]::CreateDirectory($runRoot)
    Assert-NoReparsePathComponents -Path $runRoot
    return [IO.Path]::GetFullPath($runRoot)
}

function Invoke-BoundedProcess {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$FileName,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][ValidateRange(1, 600000)][int]$TimeoutMilliseconds,
        [Parameter(Mandatory)][string]$Description
    )

    $ownedProcess = $null
    $failure = $null
    $result = $null
    try {
        $ownedProcess = [OnslaughtRebuild.Tools.OwnedJobProcess]::Start($FileName, $Arguments)
        if (-not $ownedProcess.WaitForExit($TimeoutMilliseconds)) {
            $failure = "$Description timed out after $TimeoutMilliseconds ms."
        }
        else {
            $exitCode = $ownedProcess.GetExitCode()
            if ($exitCode -ne 0) {
                $failure = "$Description exited with code $exitCode."
            }
            else {
                $result = [pscustomobject]@{
                    ExitCode = $exitCode
                    ProcessId = $ownedProcess.ProcessId
                    StandardOutput = ''
                    StandardError = ''
                }
            }
        }
    }
    catch {
        $failure = "$Description failed to start or execute. $($_.Exception.Message)"
    }
    finally {
        if ($null -ne $ownedProcess) {
            if (-not $ownedProcess.WaitForExit(0)) {
                $ownedProcess.TerminateAndWait(5000)
            }
            $ownedProcess.Dispose()
        }
    }

    if ($null -ne $failure) {
        throw $failure
    }
    return $result
}

Export-ModuleMember -Function @(
    'Invoke-BoundedProcess',
    'New-BoundedFirstFlightSmokeRoot'
)
