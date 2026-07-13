# SPDX-License-Identifier: GPL-3.0-or-later

Set-StrictMode -Version Latest

if (-not ('Onslaught.LocalFileInfo' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;
namespace Onslaught {
  public static class LocalFileInfo {
    [StructLayout(LayoutKind.Sequential)] private struct BY_HANDLE_FILE_INFORMATION {
      public uint FileAttributes; public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
      public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime; public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
      public uint VolumeSerialNumber; public uint FileSizeHigh; public uint FileSizeLow; public uint NumberOfLinks;
      public uint FileIndexHigh; public uint FileIndexLow;
    }
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool GetFileInformationByHandle(SafeFileHandle h, out BY_HANDLE_FILE_INFORMATION i);
    public static uint LinkCount(string path) {
      using (FileStream s = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read)) {
        BY_HANDLE_FILE_INFORMATION i; if (!GetFileInformationByHandle(s.SafeFileHandle, out i)) throw new IOException("GetFileInformationByHandle failed.");
        return i.NumberOfLinks;
      }
    }
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

function Get-NormalizedPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { throw 'Path cannot be empty.' }
    return [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
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
    foreach ($segment in $full.Substring($root.Length).Split(@([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar), [StringSplitOptions]::RemoveEmptyEntries)) {
        $current = Join-Path $current $segment
        if (-not (Test-Path -LiteralPath $current)) {
            if ($AllowMissingLeaf) { continue }
            throw "Path does not exist: $current"
        }
        $item = Get-Item -LiteralPath $current -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Path traverses reparse point: $current" }
    }
    return $full
}

function Assert-RegularSingleLinkFile {
    param([Parameter(Mandatory)][string]$Path, [string]$Label = 'file')
    $full = Assert-NoReparseTraversal -Path $Path
    $item = Get-Item -LiteralPath $full -Force
    if ($item.PSIsContainer) { throw "$Label must be a regular local file: $full" }
    if ([Onslaught.LocalFileInfo]::LinkCount($full) -ne 1) { throw "$Label must be a single link and cannot be a hardlink alias: $full" }
    return $full
}

function Assert-LocalAssetOutputRoot {
    param([Parameter(Mandatory)][string]$RepoRoot, [Parameter(Mandatory)][string]$OutputRoot)
    $repo = Get-NormalizedPath $RepoRoot
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
        if (Test-Path -LiteralPath $Destination) { Assert-RegularSingleLinkFile -Path $Destination -Label 'destination' | Out-Null }
        [IO.File]::Move($temp, $Destination, $true)
    } finally { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }
}

function Copy-GuardedFile {
    param([Parameter(Mandatory)][string]$RepoRoot, [Parameter(Mandatory)][string]$OutputRoot, [Parameter(Mandatory)][string]$Source, [Parameter(Mandatory)][string]$Destination)
    Assert-LocalAssetWritePlan -RepoRoot $RepoRoot -OutputRoot $OutputRoot -DestinationPaths @($Destination) | Out-Null
    Assert-RegularSingleLinkFile -Path $Source -Label 'source mesh' | Out-Null
    $parent = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw "Validated destination parent is missing: $parent" }
    $temp = Join-Path $parent ('.' + [IO.Path]::GetFileName($Destination) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        $input = [IO.File]::Open($Source, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
        $output = [IO.File]::Open($temp, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $input.CopyTo($output); $output.Flush($true) } finally { $output.Dispose(); $input.Dispose() }
        if (Test-Path -LiteralPath $Destination) { Assert-RegularSingleLinkFile -Path $Destination -Label 'destination' | Out-Null }
        [IO.File]::Move($temp, $Destination, $true)
    } finally { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Force } }
}

Export-ModuleMember -Function Assert-NoReparseTraversal, Assert-RegularSingleLinkFile, Assert-LocalAssetOutputRoot, Assert-LocalAssetWritePlan, Write-GuardedTextFile, Copy-GuardedFile
