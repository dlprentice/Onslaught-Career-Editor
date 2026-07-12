Set-StrictMode -Version Latest

$script:ReceiptSchema = "runtime-process-receipt.v1"

function Assert-ExactPropertySet {
    param(
        [object]$Value,
        [string[]]$Expected,
        [string]$Label
    )

    if ($null -eq $Value -or $Value.GetType() -ne [System.Management.Automation.PSCustomObject]) {
        throw "$Label must be a JSON object with exact keys."
    }

    $actual = @($Value.PSObject.Properties | ForEach-Object { $_.Name })
    $difference = @(Compare-Object -ReferenceObject $Expected -DifferenceObject $actual -CaseSensitive)
    if ($difference.Count -ne 0 -or $actual.Count -ne $Expected.Count) {
        throw ("{0} must have exact keys [{1}]; found [{2}]." -f
            $Label, ($Expected -join ", "), ($actual -join ", "))
    }
}

function Assert-JsonString {
    param([object]$Value, [string]$Label, [switch]$AllowEmpty)

    if ($null -eq $Value -or $Value.GetType() -ne [string]) {
        throw "$Label must be a JSON string."
    }
    if (-not $AllowEmpty -and [string]::IsNullOrWhiteSpace($Value)) {
        throw "$Label must be a non-empty JSON string."
    }
    return $Value
}

function Assert-Sha256 {
    param([object]$Value, [string]$Label)

    $text = Assert-JsonString -Value $Value -Label $Label
    if ($text -cnotmatch '^[0-9a-f]{64}$') {
        throw "$Label must be a lowercase 64-character SHA-256 digest."
    }
    return $text
}

function Assert-PositiveInt64 {
    param([object]$Value, [string]$Label)

    $integerTypes = @(
        [byte], [sbyte], [int16], [uint16], [int32], [uint32], [int64], [uint64]
    )
    if ($null -eq $Value -or $integerTypes -notcontains $Value.GetType()) {
        throw "$Label must be a positive JSON integer number."
    }
    if ([decimal]$Value -le 0 -or [decimal]$Value -gt [long]::MaxValue) {
        throw "$Label must be a positive JSON integer number within the Int64 range."
    }
    return [long]$Value
}

function Assert-NoReparsePoint {
    param([string]$Path, [string]$Label)

    $currentPath = [System.IO.Path]::GetFullPath($Path)
    while (-not [string]::IsNullOrWhiteSpace($currentPath)) {
        if (Test-Path -LiteralPath $currentPath) {
            $item = Get-Item -LiteralPath $currentPath -Force -ErrorAction Stop
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw ("{0} traverses reparse point '{1}'." -f $Label, $currentPath)
            }
        }

        $parent = Split-Path -Parent $currentPath
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $currentPath) {
            break
        }
        $currentPath = $parent
    }
}

function Resolve-ReceiptFilePath {
    param([object]$Value, [string]$Label)

    $text = Assert-JsonString -Value $Value -Label $Label
    $pathRoot = if ([string]::IsNullOrWhiteSpace($text)) { "" } else { [System.IO.Path]::GetPathRoot($text) }
    if ([string]::IsNullOrWhiteSpace($text) -or
        -not [System.IO.Path]::IsPathRooted($text) -or
        $pathRoot -match '^[A-Za-z]:$') {
        throw "$Label must be an absolute file path."
    }
    Assert-NoReparsePoint -Path $text -Label $Label
    if (-not (Test-Path -LiteralPath $text -PathType Leaf)) {
        throw ("{0} '{1}' does not exist." -f $Label, $text)
    }
    $resolved = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $text -ErrorAction Stop).Path)
    Assert-NoReparsePoint -Path $resolved -Label $Label
    return $resolved
}

function Resolve-ReceiptDirectoryPath {
    param([object]$Value, [string]$Label)

    $text = Assert-JsonString -Value $Value -Label $Label
    $pathRoot = if ([string]::IsNullOrWhiteSpace($text)) { "" } else { [System.IO.Path]::GetPathRoot($text) }
    if ([string]::IsNullOrWhiteSpace($text) -or
        -not [System.IO.Path]::IsPathRooted($text) -or
        $pathRoot -match '^[A-Za-z]:$') {
        throw "$Label must be an absolute directory path."
    }
    Assert-NoReparsePoint -Path $text -Label $Label
    if (-not (Test-Path -LiteralPath $text -PathType Container)) {
        throw ("{0} '{1}' does not exist." -f $Label, $text)
    }
    $resolved = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $text -ErrorAction Stop).Path)
    Assert-NoReparsePoint -Path $resolved -Label $Label
    return $resolved.TrimEnd(
        [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
}

function Get-FileSha256 {
    param([string]$Path)

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
}

function Assert-ReceiptFileIdentity {
    param(
        [object]$Identity,
        [string]$Label
    )

    Assert-ExactPropertySet -Value $Identity -Expected @("path", "sha256", "size") -Label $Label
    $path = Resolve-ReceiptFilePath -Value $Identity.path -Label "$Label path"
    $expectedHash = Assert-Sha256 -Value $Identity.sha256 -Label "$Label sha256"
    $expectedSize = Assert-PositiveInt64 -Value $Identity.size -Label "$Label size"
    $file = Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if ([long]$file.Length -ne $expectedSize) {
        throw ("{0} size mismatch: expected {1}, found {2}." -f $Label, $expectedSize, $file.Length)
    }
    $actualHash = Get-FileSha256 -Path $path
    Assert-NoReparsePoint -Path $path -Label "$Label path"
    if ($actualHash -cne $expectedHash) {
        throw ("{0} sha256 mismatch: expected {1}, found {2}." -f $Label, $expectedHash, $actualHash)
    }

    return [PSCustomObject]@{
        Path = $path
        Sha256 = $actualHash
        Size = [long]$file.Length
    }
}

function Get-ExactProcessExecutablePath {
    param([System.Diagnostics.Process]$Process)

    $Process.Refresh()
    try {
        if ($Process.Path) {
            return [System.IO.Path]::GetFullPath($Process.Path)
        }
    } catch {
        # Fall through to MainModule for Windows PowerShell compatibility.
    }
    try {
        return [System.IO.Path]::GetFullPath($Process.MainModule.FileName)
    } catch {
        throw ("Could not resolve executable path for receipt process id {0}: {1}" -f
            $Process.Id, $_.Exception.Message)
    }
}

if (-not ([System.Management.Automation.PSTypeName]"RuntimeProcessIdentityNative").Type) {
    Add-Type -TypeDefinition @"
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

public static class RuntimeProcessIdentityNative {
    private const uint ProcessQueryInformation = 0x0400;
    private const uint ProcessVmRead = 0x0010;

    [StructLayout(LayoutKind.Sequential)]
    private struct ProcessBasicInformation {
        public IntPtr Reserved1;
        public IntPtr PebBaseAddress;
        public IntPtr Reserved2_0;
        public IntPtr Reserved2_1;
        public IntPtr UniqueProcessId;
        public IntPtr Reserved3;
    }

    [DllImport("shell32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern IntPtr CommandLineToArgvW(string commandLine, out int argc);

    [DllImport("kernel32.dll")]
    private static extern IntPtr LocalFree(IntPtr memory);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr OpenProcess(uint desiredAccess, bool inheritHandle, int processId);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool ReadProcessMemory(
        IntPtr process,
        IntPtr baseAddress,
        byte[] buffer,
        IntPtr size,
        out IntPtr bytesRead);

    [DllImport("kernel32.dll")]
    private static extern bool CloseHandle(IntPtr handle);

    [DllImport("ntdll.dll")]
    private static extern int NtQueryInformationProcess(
        IntPtr process,
        int informationClass,
        out ProcessBasicInformation information,
        int informationLength,
        out int returnLength);

    [DllImport("ntdll.dll", EntryPoint = "NtQueryInformationProcess")]
    private static extern int NtQueryInformationProcessWow64(
        IntPtr process,
        int informationClass,
        out IntPtr information,
        int informationLength,
        out int returnLength);

    [DllImport("user32.dll")]
    public static extern bool IsWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    public sealed class ProcessParametersSnapshot {
        public string WorkingDirectory { get; private set; }
        public string CommandLine { get; private set; }

        public ProcessParametersSnapshot(string workingDirectory, string commandLine) {
            WorkingDirectory = workingDirectory;
            CommandLine = commandLine;
        }
    }

    public static string[] ParseCommandLine(string commandLine) {
        int argc;
        IntPtr argv = CommandLineToArgvW(commandLine, out argc);
        if (argv == IntPtr.Zero) {
            throw new Win32Exception(Marshal.GetLastWin32Error());
        }
        try {
            string[] result = new string[argc];
            for (int index = 0; index < argc; index++) {
                IntPtr value = Marshal.ReadIntPtr(argv, index * IntPtr.Size);
                result[index] = Marshal.PtrToStringUni(value);
            }
            return result;
        } finally {
            LocalFree(argv);
        }
    }

    private static byte[] ReadBytes(IntPtr process, long address, int count) {
        byte[] result = new byte[count];
        IntPtr bytesRead;
        if (!ReadProcessMemory(process, new IntPtr(address), result, new IntPtr(count), out bytesRead) ||
            bytesRead.ToInt64() != count) {
            throw new Win32Exception(Marshal.GetLastWin32Error(), "ReadProcessMemory failed");
        }
        return result;
    }

    private static long ReadPointer(IntPtr process, long address, int pointerSize) {
        byte[] value = ReadBytes(process, address, pointerSize);
        return pointerSize == 4 ? BitConverter.ToUInt32(value, 0) : BitConverter.ToInt64(value, 0);
    }

    private static string ReadUnicodeString(
        IntPtr process, long address, int pointerSize, string label) {
        ushort length = BitConverter.ToUInt16(ReadBytes(process, address, 2), 0);
        if ((length & 1) != 0 || length > 32766) {
            throw new InvalidOperationException("Remote " + label + " string length is invalid.");
        }
        int bufferOffset = pointerSize == 4 ? 4 : 8;
        long buffer = ReadPointer(process, address + bufferOffset, pointerSize);
        if (length == 0) {
            return String.Empty;
        }
        if (buffer == 0) {
            throw new InvalidOperationException("Remote " + label + " string has a null buffer.");
        }
        return System.Text.Encoding.Unicode.GetString(ReadBytes(process, buffer, length));
    }

    public static ProcessParametersSnapshot GetProcessParameters(int processId) {
        IntPtr process = OpenProcess(ProcessQueryInformation | ProcessVmRead, false, processId);
        if (process == IntPtr.Zero) {
            throw new Win32Exception(Marshal.GetLastWin32Error(), "OpenProcess failed");
        }
        try {
            int returnLength;
            IntPtr wow64Peb;
            int wow64Status = NtQueryInformationProcessWow64(
                process, 26, out wow64Peb, IntPtr.Size, out returnLength);
            int pointerSize;
            long pebAddress;
            if (wow64Status == 0 && wow64Peb != IntPtr.Zero) {
                pointerSize = 4;
                pebAddress = wow64Peb.ToInt64();
            } else {
                ProcessBasicInformation basicInformation;
                int status = NtQueryInformationProcess(
                    process,
                    0,
                    out basicInformation,
                    Marshal.SizeOf(typeof(ProcessBasicInformation)),
                    out returnLength);
                if (status != 0 || basicInformation.PebBaseAddress == IntPtr.Zero) {
                    throw new InvalidOperationException(
                        String.Format("NtQueryInformationProcess failed with status 0x{0:X8}.", status));
                }
                pointerSize = IntPtr.Size;
                pebAddress = basicInformation.PebBaseAddress.ToInt64();
            }

            long processParameters = ReadPointer(
                process,
                pebAddress + (pointerSize == 4 ? 0x10 : 0x20),
                pointerSize);
            if (processParameters == 0) {
                throw new InvalidOperationException("Remote process parameters pointer is null.");
            }
            long currentDirectory = processParameters + (pointerSize == 4 ? 0x24 : 0x38);
            long commandLine = processParameters + (pointerSize == 4 ? 0x40 : 0x70);
            return new ProcessParametersSnapshot(
                ReadUnicodeString(process, currentDirectory, pointerSize, "current-directory"),
                ReadUnicodeString(process, commandLine, pointerSize, "command-line"));
        } finally {
            CloseHandle(process);
        }
    }
}
"@
}

function Get-CurrentLaunchArguments {
    param([string]$CommandLine, [int]$ProcessId)

    if ([string]::IsNullOrWhiteSpace($CommandLine)) {
        throw ("Could not resolve launch arguments for receipt process id {0}." -f $ProcessId)
    }
    $allArguments = @([RuntimeProcessIdentityNative]::ParseCommandLine($CommandLine))
    if ($allArguments.Count -lt 1) {
        throw ("Process id {0} has an empty command line." -f $ProcessId)
    }
    if ($allArguments.Count -eq 1) {
        return @()
    }
    return @($allArguments[1..($allArguments.Count - 1)])
}

function Assert-LaunchArguments {
    param([object]$ReceiptArguments, [string]$LiveCommandLine, [int]$ProcessId)

    if ($null -eq $ReceiptArguments -or $ReceiptArguments -isnot [System.Array]) {
        throw "process launchArguments must be a JSON array of strings."
    }
    $expected = @($ReceiptArguments)
    foreach ($argument in $expected) {
        if ($null -eq $argument -or $argument -isnot [string]) {
            throw "process launchArguments must contain only JSON strings."
        }
    }
    $actual = @(Get-CurrentLaunchArguments -CommandLine $LiveCommandLine -ProcessId $ProcessId)
    if ($actual.Count -ne $expected.Count) {
        throw ("Process launch arguments mismatch: expected {0} arguments, found {1}." -f
            $expected.Count, $actual.Count)
    }
    for ($index = 0; $index -lt $expected.Count; $index++) {
        if (-not [string]::Equals(
            [string]$expected[$index],
            [string]$actual[$index],
            [System.StringComparison]::Ordinal)) {
            throw ("Process launch arguments mismatch at index {0}." -f $index)
        }
    }
}

function Assert-UniqueExecutableProcess {
    param([System.Diagnostics.Process]$ExpectedProcess, [string]$ExecutablePath)

    $candidates = @(Get-Process -Name $ExpectedProcess.ProcessName -ErrorAction SilentlyContinue)
    $matches = New-Object System.Collections.Generic.List[int]
    foreach ($candidate in $candidates) {
        try {
            $candidatePath = Get-ExactProcessExecutablePath -Process $candidate
        } catch {
            throw ("Could not resolve executable path for same-name process id {0}; identity is ambiguous: {1}" -f
                $candidate.Id, $_.Exception.Message)
        }
        if ([string]::Equals(
            $candidatePath,
            $ExecutablePath,
            [System.StringComparison]::OrdinalIgnoreCase)) {
            $matches.Add($candidate.Id)
        }
    }
    if ($candidates.Count -ne 1 -or $matches.Count -ne 1 -or $matches[0] -ne $ExpectedProcess.Id) {
        throw ("Found multiple running processes using executable path '{0}' or the exact receipt process was ambiguous: {1}." -f
            $ExecutablePath, (($candidates | ForEach-Object { $_.Id }) -join ", "))
    }
}

function Assert-RuntimeProcessReceipt {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ReceiptPath,
        [Parameter(Mandatory = $true)]
        [string]$ExpectedReceiptSha256,
        [switch]$RequireWindow
    )

    $expectedReceiptHash = Assert-Sha256 -Value $ExpectedReceiptSha256 -Label "Expected receipt SHA-256"
    $resolvedReceiptPath = Resolve-ReceiptFilePath -Value $ReceiptPath -Label "Runtime receipt path"
    $receiptBytes = [System.IO.File]::ReadAllBytes($resolvedReceiptPath)
    Assert-NoReparsePoint -Path $resolvedReceiptPath -Label "Runtime receipt path"
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $actualReceiptHash = ([System.BitConverter]::ToString($sha256.ComputeHash($receiptBytes))).Replace("-", "").ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
    if ($actualReceiptHash -cne $expectedReceiptHash) {
        throw ("Runtime receipt SHA-256 mismatch: expected {0}, found {1}." -f
            $expectedReceiptHash, $actualReceiptHash)
    }

    try {
        $utf8 = [System.Text.UTF8Encoding]::new($false, $true)
        $receiptText = $utf8.GetString($receiptBytes)
        $convertFromJsonArguments = @{ ErrorAction = "Stop" }
        if ((Get-Command ConvertFrom-Json).Parameters.ContainsKey("DateKind")) {
            $convertFromJsonArguments.DateKind = "String"
        }
        $receipt = $receiptText | ConvertFrom-Json @convertFromJsonArguments
    } catch {
        throw ("Runtime receipt is not valid UTF-8 JSON: {0}" -f $_.Exception.Message)
    }

    Assert-ExactPropertySet -Value $receipt -Expected @(
        "schemaVersion",
        "runId",
        "process",
        "profileManifest",
        "window",
        "module",
        "sourceExecutableSha256",
        "copiedExecutableSha256",
        "commandTemplateSha256",
        "generatedCommandSha256"
    ) -Label "runtime receipt"
    $schemaVersion = Assert-JsonString -Value $receipt.schemaVersion -Label "Runtime receipt schemaVersion"
    if ($schemaVersion -cne $script:ReceiptSchema) {
        throw ("Runtime receipt schema must be exactly '{0}'." -f $script:ReceiptSchema)
    }
    [void](Assert-JsonString -Value $receipt.runId -Label "Runtime receipt runId")

    Assert-ExactPropertySet -Value $receipt.process -Expected @(
        "id", "startedAtUtc", "executable", "workingDirectory", "launchArguments"
    ) -Label "runtime receipt process"
    [long]$receiptProcessId = Assert-PositiveInt64 -Value $receipt.process.id -Label "process id"
    if ($receiptProcessId -gt [int]::MaxValue) {
        throw "Runtime receipt process id is outside the Windows process-id range."
    }
    $process = Get-Process -Id ([int]$receiptProcessId) -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        throw ("Runtime receipt process id {0} is not running." -f $receiptProcessId)
    }

    $startText = Assert-JsonString -Value $receipt.process.startedAtUtc -Label "Process startedAtUtc"
    [DateTimeOffset]$expectedStart = [DateTimeOffset]::MinValue
    if (-not $startText.EndsWith("Z", [System.StringComparison]::Ordinal) -or
        -not [DateTimeOffset]::TryParseExact(
            $startText,
            "o",
            [System.Globalization.CultureInfo]::InvariantCulture,
            [System.Globalization.DateTimeStyles]::RoundtripKind,
            [ref]$expectedStart)) {
        throw "Process startedAtUtc must be an exact UTC round-trip timestamp."
    }
    $actualStart = [DateTimeOffset]::new($process.StartTime.ToUniversalTime())
    if ($actualStart.UtcTicks -ne $expectedStart.UtcTicks) {
        throw ("Process start time mismatch for id {0}; refusing possible PID reuse." -f $process.Id)
    }

    $executableIdentity = Assert-ReceiptFileIdentity -Identity $receipt.process.executable -Label "executable"
    $actualExecutablePath = Get-ExactProcessExecutablePath -Process $process
    if (-not [string]::Equals(
        $actualExecutablePath,
        $executableIdentity.Path,
        [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("Executable path mismatch: process uses '{0}', receipt requires '{1}'." -f
            $actualExecutablePath, $executableIdentity.Path)
    }

    $workingDirectory = Resolve-ReceiptDirectoryPath -Value $receipt.process.workingDirectory -Label "working directory"
    $executableDirectory = [System.IO.Path]::GetDirectoryName($executableIdentity.Path).TrimEnd(
        [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
    if (-not [string]::Equals(
        $workingDirectory,
        $executableDirectory,
        [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("Working directory mismatch: receipt directory '{0}' is not executable directory '{1}'." -f
            $workingDirectory, $executableDirectory)
    }
    try {
        $liveParameters = [RuntimeProcessIdentityNative]::GetProcessParameters($process.Id)
        $liveWorkingDirectory = [System.IO.Path]::GetFullPath(
            $liveParameters.WorkingDirectory).TrimEnd(
                [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar))
    } catch {
        throw ("Could not inspect live process working directory for id {0}: {1}" -f
            $process.Id, $_.Exception.Message)
    }
    if (-not [string]::Equals(
        $liveWorkingDirectory,
        $workingDirectory,
        [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("Live process working directory mismatch: process uses '{0}', receipt requires '{1}'." -f
            $liveWorkingDirectory, $workingDirectory)
    }
    Assert-LaunchArguments `
        -ReceiptArguments $receipt.process.launchArguments `
        -LiveCommandLine $liveParameters.CommandLine `
        -ProcessId $process.Id

    $manifestIdentity = Assert-ReceiptFileIdentity -Identity $receipt.profileManifest -Label "manifest"
    $expectedManifestPath = [System.IO.Path]::GetFullPath((Join-Path $workingDirectory "onslaught-profile-manifest.json"))
    if (-not [string]::Equals(
        $manifestIdentity.Path,
        $expectedManifestPath,
        [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("Manifest path mismatch: expected '{0}', receipt names '{1}'." -f
            $expectedManifestPath, $manifestIdentity.Path)
    }

    Assert-ExactPropertySet -Value $receipt.module -Expected @("path", "baseAddressHex", "size") -Label "runtime receipt module"
    $modulePath = Resolve-ReceiptFilePath -Value $receipt.module.path -Label "module path"
    $baseAddressText = Assert-JsonString -Value $receipt.module.baseAddressHex -Label "Module baseAddressHex"
    if ($baseAddressText -cnotmatch '^0x[0-9A-F]+$') {
        throw "Module baseAddressHex must use canonical uppercase 0x hexadecimal form."
    }
    [long]$expectedModuleBase = [Convert]::ToInt64($baseAddressText.Substring(2), 16)
    [long]$expectedModuleSize = Assert-PositiveInt64 -Value $receipt.module.size -Label "module size"
    $process.Refresh()
    try {
        $mainModule = $process.MainModule
        $actualModulePath = [System.IO.Path]::GetFullPath($mainModule.FileName)
        $actualModuleBase = $mainModule.BaseAddress.ToInt64()
        $actualModuleSize = [long]$mainModule.ModuleMemorySize
    } catch {
        throw ("Could not inspect main module for receipt process id {0}: {1}" -f
            $process.Id, $_.Exception.Message)
    }
    if (-not [string]::Equals($actualModulePath, $modulePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("Module path mismatch: process uses '{0}', receipt requires '{1}'." -f $actualModulePath, $modulePath)
    }
    if ($actualModuleBase -ne $expectedModuleBase) {
        throw ("Module baseAddressHex mismatch: expected {0}, found 0x{1:X}." -f
            $baseAddressText, $actualModuleBase)
    }
    if ($actualModuleSize -ne $expectedModuleSize) {
        throw ("Module size mismatch: expected {0}, found {1}." -f $expectedModuleSize, $actualModuleSize)
    }

    Assert-ExactPropertySet -Value $receipt.window -Expected @("hwndHex") -Label "runtime receipt window"
    $hwndText = Assert-JsonString -Value $receipt.window.hwndHex -Label "Window hwndHex"
    if ($hwndText -cnotmatch '^0x(?:0|[1-9A-F][0-9A-F]*)$') {
        throw "Window hwndHex must use canonical uppercase 0x hexadecimal form."
    }
    [long]$hwndValue = [Convert]::ToInt64($hwndText.Substring(2), 16)
    if ($RequireWindow) {
        if ($hwndValue -le 0) {
            throw "Window ownership validation requires a nonzero hwndHex."
        }
        $handle = [IntPtr]::new($hwndValue)
        [uint32]$windowProcessId = 0
        if (-not [RuntimeProcessIdentityNative]::IsWindow($handle)) {
            throw ("Window {0} is no longer a valid top-level window." -f $hwndText)
        }
        [void][RuntimeProcessIdentityNative]::GetWindowThreadProcessId($handle, [ref]$windowProcessId)
        if ([int]$windowProcessId -ne $process.Id) {
            throw ("Window {0} is owned by process id {1}, not receipt process id {2}." -f
                $hwndText, $windowProcessId, $process.Id)
        }
    }

    $sourceHash = Assert-Sha256 -Value $receipt.sourceExecutableSha256 -Label "sourceExecutableSha256"
    $copyHash = Assert-Sha256 -Value $receipt.copiedExecutableSha256 -Label "copiedExecutableSha256"
    [void](Assert-Sha256 -Value $receipt.commandTemplateSha256 -Label "commandTemplateSha256")
    [void](Assert-Sha256 -Value $receipt.generatedCommandSha256 -Label "generatedCommandSha256")
    if ($sourceHash -cne $executableIdentity.Sha256) {
        throw "sourceExecutableSha256 does not match the validated executable hash."
    }
    if ($copyHash -cne $executableIdentity.Sha256) {
        throw "copiedExecutableSha256 does not match the validated executable hash."
    }

    Assert-UniqueExecutableProcess -ExpectedProcess $process -ExecutablePath $executableIdentity.Path

    return [PSCustomObject]@{
        Receipt = $receipt
        Process = $process
    }
}

Export-ModuleMember -Function Assert-RuntimeProcessReceipt
