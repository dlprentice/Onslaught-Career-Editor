# SPDX-License-Identifier: GPL-3.0-or-later

Set-StrictMode -Version Latest

if (-not ('Onslaught.LocalFileInfo' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.ComponentModel;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32.SafeHandles;
namespace Onslaught {
  public sealed class LocalFileLease : IDisposable {
    private const uint GENERIC_READ = 0x80000000;
    private const uint FILE_SHARE_READ = 0x1;
    private const uint OPEN_EXISTING = 3;
    private const uint FILE_ATTRIBUTE_NORMAL = 0x80;
    private const uint FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000;
    private const uint FILE_FLAG_SEQUENTIAL_SCAN = 0x08000000;
    [StructLayout(LayoutKind.Sequential)] private struct BY_HANDLE_FILE_INFORMATION {
      public uint FileAttributes; public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
      public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime; public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
      public uint VolumeSerialNumber; public uint FileSizeHigh; public uint FileSizeLow; public uint NumberOfLinks;
      public uint FileIndexHigh; public uint FileIndexLow;
    }
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern SafeFileHandle CreateFileW(string name, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", SetLastError=true)]
    private static extern bool GetFileInformationByHandle(SafeFileHandle handle, out BY_HANDLE_FILE_INFORMATION information);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern uint GetFinalPathNameByHandleW(SafeFileHandle handle, StringBuilder path, uint length, uint flags);
    private readonly SafeFileHandle handle;
    private readonly FileStream stream;
    private readonly uint volume;
    private readonly ulong index;
    private readonly long length;
    public string Identity { get { return volume.ToString("X8") + ":" + index.ToString("X16"); } }
    public long Length { get { return length; } }
    private LocalFileLease(SafeFileHandle opened, BY_HANDLE_FILE_INFORMATION information) {
      handle = opened;
      stream = new FileStream(handle, FileAccess.Read);
      volume = information.VolumeSerialNumber;
      index = ((ulong)information.FileIndexHigh << 32) | information.FileIndexLow;
      length = ((long)information.FileSizeHigh << 32) | information.FileSizeLow;
    }
    public static LocalFileLease OpenRead(string path) {
      string expected = Normalize(path);
      var opened = CreateFileW(expected, GENERIC_READ, FILE_SHARE_READ, IntPtr.Zero, OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_SEQUENTIAL_SCAN, IntPtr.Zero);
      if (opened.IsInvalid) { int error = Marshal.GetLastWin32Error(); opened.Dispose(); throw new Win32Exception(error, "Could not open guarded local file: " + expected); }
      try {
        BY_HANDLE_FILE_INFORMATION information;
        if (!GetFileInformationByHandle(opened, out information)) throw new Win32Exception(Marshal.GetLastWin32Error(), "Could not inspect guarded local file.");
        const uint DIRECTORY = 0x10, REPARSE = 0x400;
        if ((information.FileAttributes & (DIRECTORY | REPARSE)) != 0) throw new IOException("Guarded path is not a regular no-follow local file: " + expected);
        if (information.NumberOfLinks != 1) throw new IOException("Guarded file must be a single link and cannot be a hardlink alias: " + expected);
        if (!String.Equals(expected, Normalize(Resolve(opened)), StringComparison.OrdinalIgnoreCase)) throw new IOException("Guarded file path changed identity: " + expected);
        return new LocalFileLease(opened, information);
      } catch { opened.Dispose(); throw; }
    }
    public string ComputeHash() {
      stream.Position = 0;
      string result = Convert.ToHexString(SHA256.HashData(stream));
      stream.Position = 0;
      return result;
    }
    public string CopyToAndHash(Stream destination) {
      stream.Position = 0;
      using (IncrementalHash hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256)) {
        byte[] buffer = new byte[128 * 1024]; int read;
        while ((read = stream.Read(buffer, 0, buffer.Length)) != 0) { destination.Write(buffer, 0, read); hash.AppendData(buffer, 0, read); }
        return Convert.ToHexString(hash.GetHashAndReset());
      }
    }
    public void Revalidate() {
      BY_HANDLE_FILE_INFORMATION current;
      if (!GetFileInformationByHandle(handle, out current)) throw new Win32Exception(Marshal.GetLastWin32Error(), "Could not revalidate guarded local file.");
      ulong currentIndex = ((ulong)current.FileIndexHigh << 32) | current.FileIndexLow;
      long currentLength = ((long)current.FileSizeHigh << 32) | current.FileSizeLow;
      if (current.VolumeSerialNumber != volume || currentIndex != index || currentLength != length || current.NumberOfLinks != 1)
        throw new IOException("Guarded local file identity, size, or link count changed while leased.");
    }
    private static string Resolve(SafeFileHandle opened) {
      var b = new StringBuilder(512); uint n = GetFinalPathNameByHandleW(opened, b, (uint)b.Capacity, 0);
      if (n == 0) throw new Win32Exception(Marshal.GetLastWin32Error(), "Could not resolve guarded local file identity.");
      if (n >= b.Capacity) { b.Capacity = checked((int)n + 1); n = GetFinalPathNameByHandleW(opened, b, (uint)b.Capacity, 0); if (n == 0 || n >= b.Capacity) throw new IOException("Could not resolve guarded local file identity."); }
      string p = b.ToString(); return p.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase) ? @"\\" + p.Substring(8) : p.StartsWith(@"\\?\", StringComparison.OrdinalIgnoreCase) ? p.Substring(4) : p;
    }
    private static string Normalize(string path) { return Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar); }
    public void Dispose() { stream.Dispose(); }
  }
  public sealed class DirectoryLeaseSet : IDisposable {
    private const uint FILE_READ_ATTRIBUTES = 0x80;
    private const uint FILE_SHARE_READ = 0x1;
    private const uint OPEN_EXISTING = 3;
    private const uint FILE_FLAG_BACKUP_SEMANTICS = 0x02000000;
    private const uint FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000;
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern SafeFileHandle CreateFileW(string name, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern uint GetFinalPathNameByHandleW(SafeFileHandle handle, StringBuilder path, uint length, uint flags);
    private readonly List<SafeFileHandle> handles = new List<SafeFileHandle>();
    private DirectoryLeaseSet() {}
    public static DirectoryLeaseSet Open(string repoRoot, string[] directories) {
      var result = new DirectoryLeaseSet();
      try {
        string repo = Normalize(repoRoot);
        result.OpenOne(repo);
        var unique = new SortedSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (string requested in directories) {
          string target = Normalize(requested);
          if (!target.StartsWith(repo + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("Leased directory escapes repository root.");
          string current = repo;
          foreach (string segment in target.Substring(repo.Length + 1).Split(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)) {
            if (segment.Length == 0) continue;
            current = Path.Combine(current, segment);
            unique.Add(current);
          }
        }
        foreach (string path in unique) {
          Directory.CreateDirectory(path);
          result.OpenOne(path);
        }
        return result;
      } catch { result.Dispose(); throw; }
    }
    private void OpenOne(string path) {
      var handle = CreateFileW(path, FILE_READ_ATTRIBUTES, FILE_SHARE_READ, IntPtr.Zero, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, IntPtr.Zero);
      if (handle.IsInvalid) { handle.Dispose(); throw new IOException("Could not lease local asset directory: " + path); }
      var attrs = File.GetAttributes(path);
      if ((attrs & FileAttributes.ReparsePoint) != 0 || !String.Equals(Normalize(Resolve(handle)), Normalize(path), StringComparison.OrdinalIgnoreCase)) {
        handle.Dispose(); throw new IOException("Local asset directory changed identity or is a reparse point: " + path);
      }
      handles.Add(handle);
    }
    private static string Resolve(SafeFileHandle handle) {
      var b = new StringBuilder(512); uint n = GetFinalPathNameByHandleW(handle, b, (uint)b.Capacity, 0);
      if (n == 0) throw new IOException("Could not resolve leased directory identity.");
      if (n >= b.Capacity) { b.Capacity = checked((int)n + 1); n = GetFinalPathNameByHandleW(handle, b, (uint)b.Capacity, 0); if (n == 0 || n >= b.Capacity) throw new IOException("Could not resolve leased directory identity."); }
      string p = b.ToString(); return p.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase) ? @"\\" + p.Substring(8) : p.StartsWith(@"\\?\", StringComparison.OrdinalIgnoreCase) ? p.Substring(4) : p;
    }
    private static string Normalize(string path) { return Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar); }
    public void Dispose() { for (int i = handles.Count - 1; i >= 0; --i) handles[i].Dispose(); handles.Clear(); }
  }
}
'@
}

$script:LocalAssetRepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..')).TrimEnd('\', '/')

function Get-NormalizedPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { throw 'Path cannot be empty.' }
    if ($Path.StartsWith('\\', [StringComparison]::Ordinal) -or $Path.StartsWith('//', [StringComparison]::Ordinal) -or $Path -match '^[\\/](\?\?|Device)[\\/]') {
        throw "UNC and device paths are not supported: $Path"
    }
    $full = [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    if ([IO.Path]::GetPathRoot($full) -notmatch '^[A-Za-z]:\\$') { throw "Path must use a local drive root: $Path" }
    return $full
}

function Assert-ExactRepoRoot([string]$RepoRoot) {
    $repo = Get-NormalizedPath $RepoRoot
    if (-not [string]::Equals($repo, $script:LocalAssetRepoRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "RepoRoot must be the checkout containing LocalAssetWorkspace.psm1: $script:LocalAssetRepoRoot"
    }
    return $repo
}

function Test-PathContained([string]$Parent, [string]$Child, [switch]$AllowEqual) {
    $parentFull = Get-NormalizedPath $Parent
    $childFull = Get-NormalizedPath $Child
    if ($AllowEqual -and [string]::Equals($parentFull, $childFull, [StringComparison]::OrdinalIgnoreCase)) { return $true }
    return $childFull.StartsWith($parentFull + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)
}

function Assert-NoReparseTraversal {
    param([Parameter(Mandatory)][string]$Path, [switch]$AllowMissingLeaf)
    $full = Get-NormalizedPath $Path
    $root = [IO.Path]::GetPathRoot($full)
    $current = $root
    $separators = [char[]]@([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    foreach ($segment in $full.Substring($root.Length).Split($separators, [StringSplitOptions]::RemoveEmptyEntries)) {
        $current = Join-Path $current $segment
        $item = Get-Item -LiteralPath $current -Force -ErrorAction SilentlyContinue
        if ($null -eq $item) {
            if ($AllowMissingLeaf) { continue }
            throw "Path does not exist: $current"
        }
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Path traverses reparse point: $current" }
    }
    return $full
}

function Assert-RegularSingleLinkFile {
    param([Parameter(Mandatory)][string]$Path, [string]$Label = 'file')
    $full = Assert-NoReparseTraversal -Path $Path
    $lease = $null
    try { $lease = [Onslaught.LocalFileLease]::OpenRead($full) }
    catch { throw "$Label must be a regular local single-link file: $full. $($_.Exception.Message)" }
    finally { if ($null -ne $lease) { $lease.Dispose() } }
    return $full
}

function Assert-LocalAssetOutputRoot {
    param([Parameter(Mandatory)][string]$RepoRoot, [Parameter(Mandatory)][string]$OutputRoot)
    $repo = Assert-ExactRepoRoot $RepoRoot
    $workspace = Join-Path $repo 'local-lab\rebuild-godot'
    $output = Get-NormalizedPath $OutputRoot
    if (-not (Test-PathContained -Parent $workspace -Child $output -AllowEqual)) { throw "Output must stay contained under the ignored local-lab/rebuild-godot workspace: $output" }
    Assert-NoReparseTraversal -Path $repo | Out-Null
    Assert-NoReparseTraversal -Path $output -AllowMissingLeaf | Out-Null
    return $output
}

function Assert-LocalAssetWritePlan {
    param(
        [Parameter(Mandatory)][string]$RepoRoot,
        [Parameter(Mandatory)][string]$OutputRoot,
        [string[]]$ForbiddenRoots = @(),
        [string[]]$DestinationPaths = @()
    )
    $output = Assert-LocalAssetOutputRoot -RepoRoot $RepoRoot -OutputRoot $OutputRoot
    foreach ($forbidden in $ForbiddenRoots) {
        if ([string]::IsNullOrWhiteSpace($forbidden)) { continue }
        $blocked = Get-NormalizedPath $forbidden
        if ((Test-PathContained -Parent $blocked -Child $output -AllowEqual) -or (Test-PathContained -Parent $output -Child $blocked -AllowEqual)) {
            throw "Output overlaps an installed-game, BEA.exe, or source/dependency root: $blocked"
        }
    }
    foreach ($destination in $DestinationPaths) {
        $full = Get-NormalizedPath $destination
        if (-not (Test-PathContained -Parent $output -Child $full)) { throw "Destination escapes the validated output root: $full" }
        Assert-NoReparseTraversal -Path $full -AllowMissingLeaf | Out-Null
        if (Test-Path -LiteralPath $full -PathType Leaf) { Assert-RegularSingleLinkFile -Path $full -Label 'destination' | Out-Null }
        elseif (Test-Path -LiteralPath $full) { throw "Destination is not a regular file: $full" }
    }
    return $output
}

function Write-GuardedTextFile {
    param([Parameter(Mandatory)][string]$RepoRoot, [Parameter(Mandatory)][string]$OutputRoot, [Parameter(Mandatory)][string]$Destination, [Parameter(Mandatory)][string]$Content)
    Assert-LocalAssetWritePlan -RepoRoot $RepoRoot -OutputRoot $OutputRoot -DestinationPaths @($Destination) | Out-Null
    $parent = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw "Validated destination parent is missing: $parent" }
    $temp = Join-Path $parent ('.' + [IO.Path]::GetFileName($Destination) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Content)
        $stream = [IO.File]::Open($temp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
        $expectedHash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes))
        $staged = [Onslaught.LocalFileLease]::OpenRead($temp)
        try {
            if ($staged.Length -ne $bytes.Length -or $staged.ComputeHash() -ne $expectedHash) { throw 'Staged text output failed identity, size, or hash validation.' }
            $stagedIdentity = $staged.Identity
        } finally { $staged.Dispose() }
        if (Test-Path -LiteralPath $Destination) { Assert-RegularSingleLinkFile -Path $Destination -Label 'destination' | Out-Null }
        [IO.File]::Move($temp, $Destination, $true)
        $final = [Onslaught.LocalFileLease]::OpenRead($Destination)
        try {
            if ($final.Identity -ne $stagedIdentity -or $final.Length -ne $bytes.Length -or $final.ComputeHash() -ne $expectedHash) { throw 'Final text output failed identity, size, or hash validation.' }
        } finally { $final.Dispose() }
    } finally { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }
}

function Copy-GuardedFile {
    param([Parameter(Mandatory)][string]$RepoRoot, [Parameter(Mandatory)][string]$OutputRoot, [Parameter(Mandatory)][string]$Source, [Parameter(Mandatory)][string]$Destination)
    Assert-LocalAssetWritePlan -RepoRoot $RepoRoot -OutputRoot $OutputRoot -DestinationPaths @($Destination) | Out-Null
    $sourceFull = Get-NormalizedPath $Source
    $destinationFull = Get-NormalizedPath $Destination
    if ([string]::Equals($sourceFull, $destinationFull, [StringComparison]::OrdinalIgnoreCase)) { throw 'Source and destination must be different files.' }
    $parent = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw "Validated destination parent is missing: $parent" }
    $temp = Join-Path $parent ('.' + [IO.Path]::GetFileName($Destination) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    $input = $null
    try {
        $input = [Onslaught.LocalFileLease]::OpenRead($sourceFull)
        if (Test-Path -LiteralPath $destinationFull -PathType Leaf) {
            $existing = [Onslaught.LocalFileLease]::OpenRead($destinationFull)
            try { if ($existing.Identity -eq $input.Identity) { throw 'Source and destination are physical aliases of the same file.' } } finally { $existing.Dispose() }
        }
        $output = [IO.File]::Open($temp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $sourceHash = $input.CopyToAndHash($output); $output.Flush($true) } finally { $output.Dispose() }
        $input.Revalidate()
        if ($input.ComputeHash() -ne $sourceHash) { throw 'Source mesh contents changed while held for copy.' }
        $staged = [Onslaught.LocalFileLease]::OpenRead($temp)
        try {
            if ($staged.Length -ne $input.Length -or $staged.ComputeHash() -ne $sourceHash) { throw 'Staged mesh failed identity, size, or hash validation.' }
            $stagedIdentity = $staged.Identity
        } finally { $staged.Dispose() }
        if (Test-Path -LiteralPath $destinationFull) { Assert-RegularSingleLinkFile -Path $destinationFull -Label 'destination' | Out-Null }
        [IO.File]::Move($temp, $destinationFull, $true)
        $final = [Onslaught.LocalFileLease]::OpenRead($destinationFull)
        try {
            if ($final.Identity -ne $stagedIdentity -or $final.Length -ne $input.Length -or $final.ComputeHash() -ne $sourceHash) { throw 'Final mesh failed identity, size, or hash validation.' }
        } finally { $final.Dispose() }
        $input.Revalidate()
        if ($input.ComputeHash() -ne $sourceHash) { throw 'Source mesh contents changed before copy completion.' }
    } finally {
        if ($null -ne $input) { $input.Dispose() }
        if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force }
    }
}

Export-ModuleMember -Function Assert-NoReparseTraversal, Assert-RegularSingleLinkFile, Assert-LocalAssetOutputRoot, Assert-LocalAssetWritePlan, Write-GuardedTextFile, Copy-GuardedFile
