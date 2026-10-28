// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Text;
using Microsoft.Win32.SafeHandles;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Options;

/// <summary>
/// A protected snapshot of the launcher's flat ce.ini. Only update_check and record_sessions are editable here.
/// Contract: Onslaught CE 72a44140c6db3e093cc07b1bed40a0584fdfecd2, ce_launch.c ini_get and ce_report.h ce_ini_write.
/// Unknown lines retain their exact UTF-8 bytes; unsupported encodings are refused, never silently converted.
/// </summary>
public sealed class CeSettings
{
    public const int MaximumBytes = 1 << 20;
    private static readonly UTF8Encoding Utf8 = new(false, true);
    private readonly byte[] _bytes;
    private readonly string _text;
    private readonly string? _identity;

    private CeSettings(string path, bool exists, byte[] bytes, string? identity, string text)
        => (Path, Exists, _bytes, _identity, _text) = (path, exists, bytes.ToArray(), identity, text);

    public string Path { get; }
    public bool Exists { get; }
    public string Sha256 => SaveSession.Digest(_bytes);
    public bool UpdateCheck => Value("update_check") != "0";
    public bool RecordSessions => Value("record_sessions") == "1";
    public string? GameDirectory => Value("gamedir");
    public byte[] CopyBytes() => _bytes.ToArray();

    /// <summary>Reads only. A missing user folder or ce.ini reports the launcher's defaults, without creating it.</summary>
    public static Outcome<CeSettings> Read(string userFolder)
    {
        try
        {
            if (!System.IO.Path.IsPathFullyQualified(userFolder))
                return Outcome<CeSettings>.Refusal("CE's user folder must be an absolute path.");
            string path = System.IO.Path.Combine(System.IO.Path.GetFullPath(userFolder), "ce.ini");
            FileMutationSafety.RejectExistingReparseAncestors(path, "CE user folder");
            FileMutationSafety.RejectReparsePoint(path, "CE settings");
            if (!File.Exists(path))
            {
                if (Directory.Exists(path)) return Outcome<CeSettings>.Refusal("ce.ini is a directory, not a settings file.");
                return Parse(path, false, [], null);
            }
            (byte[] bytes, string identity) = ReadProtected(path);
            return Parse(path, true, bytes, identity);
        }
        catch (Exception error) when (IsFileError(error))
        {
            return Outcome<CeSettings>.Refusal("CE settings could not be read safely: " + error.Message);
        }
    }

    internal static Outcome<CeSettings> Parse(string path, bool exists, byte[] bytes, string? identity = null)
    {
        if (bytes.Length > MaximumBytes) return Outcome<CeSettings>.Refusal("ce.ini is larger than the launcher's one-megabyte limit.");
        if (bytes.Contains((byte)0)) return Outcome<CeSettings>.Refusal("ce.ini contains a zero byte. It was left untouched.");
        try
        {
            string text = Utf8.GetString(bytes);
            if (text.StartsWith('\uFEFF'))
                return Outcome<CeSettings>.Refusal("ce.ini has a byte-order mark the launcher does not understand. It was left untouched.");
            return Outcome<CeSettings>.Success(new CeSettings(path, exists, bytes, identity, text),
                exists ? "CE settings read." : "CE has not written ce.ini yet; showing its defaults.");
        }
        catch (DecoderFallbackException)
        {
            return Outcome<CeSettings>.Refusal("ce.ini is not valid UTF-8. It was left untouched rather than changing its encoding.");
        }
    }

    /// <summary>Only these two exact, case-sensitive keys can change. Duplicate copies of those keys collapse to one.</summary>
    public Outcome<byte[]> Prepare(bool updateCheck, bool recordSessions)
    {
        Dictionary<string, string> values = new(StringComparer.Ordinal)
        {
            ["update_check"] = updateCheck ? "1" : "0",
            ["record_sessions"] = recordSessions ? "1" : "0",
        };
        HashSet<string> written = new(StringComparer.Ordinal);
        StringBuilder output = new();
        foreach ((string line, string ending) in Lines(_text))
        {
            string? key = values.Keys.FirstOrDefault(candidate => line.StartsWith(candidate + "=", StringComparison.Ordinal));
            if (key is null) output.Append(line).Append(ending);
            else if (written.Add(key)) output.Append(key).Append('=').Append(values[key]).Append(ending.Length > 0 ? ending : "\n");
        }
        foreach ((string key, string value) in values)
        {
            if (written.Contains(key)) continue;
            if (output.Length > 0 && output[^1] != '\n') output.Append('\n');
            output.Append(key).Append('=').Append(value).Append('\n');
        }
        byte[] bytes = Utf8.GetBytes(output.ToString());
        return bytes.Length > MaximumBytes ? Outcome<byte[]>.Refusal("The edited ce.ini would exceed the launcher's size limit.") :
            Outcome<byte[]>.Success(bytes, "Prepared CE launcher settings; other keys are preserved.");
    }

    /// <summary>
    /// Holds the cooperative settings lock and a verified external backup through the staged, checked exchange.
    /// A source race detected during the exchange is refused or rolled back. A first file gets an absence receipt,
    /// not a fake original. The lock cannot serialize older or otherwise uncooperative writers.
    /// </summary>
    public InstallReceipt Save(bool updateCheck, bool recordSessions, string backupRoot, Func<bool> gameRunning, DateTime now,
        Action? beforeCheck = null, Action? beforeSwap = null, string? packageRoot = null, string? originalRoot = null,
        Action? afterPublish = null)
    {
        string? backupFolder = null;
        try
        {
            if (gameRunning()) return Refuse(GameInstaller.RunningMessage);
            string userFolder = System.IO.Path.GetDirectoryName(Path)!;
            void CheckPackageFolders()
            {
                CeGameData.RejectWriteFolder(userFolder, originalRoot, "CE's user folder");
                CeGameData.RejectWriteFolder(backupRoot, originalRoot, "The backup folder");
                CeInstallation.RejectFolderInAnyPackage(userFolder, "CE's user folder");
                CeInstallation.RejectFolderInAnyPackage(backupRoot, "The backup folder");
                if (packageRoot is null) return;
                CeInstallation.RejectFolderInPackage(userFolder, packageRoot, "CE's user folder");
                CeInstallation.RejectFolderInPackage(backupRoot, packageRoot, "The backup folder");
            }
            CheckPackageFolders();
            if (!Directory.Exists(userFolder)) return Refuse("Start CE once so it can create its user folder, then try again.");
            FileMutationSafety.RejectExistingReparseAncestors(Path, "CE user folder");
            FileMutationSafety.RejectOutputInGameTree(Path);
            if (!System.IO.Path.IsPathFullyQualified(backupRoot) || !Directory.Exists(backupRoot))
                return Refuse("Choose an existing backup folder outside CE's user folder.");
            FileMutationSafety.RejectExistingReparseAncestors(backupRoot, "Backup folder");
            FileMutationSafety.RejectOutputInGameTree(System.IO.Path.Combine(backupRoot, "ce.ini"));
            string realBackup = System.IO.Path.TrimEndingDirectorySeparator(System.IO.Path.GetFullPath(backupRoot));
            if (Backups.IsInside(realBackup, userFolder)) return Refuse("Choose a backup folder outside CE's user folder.");
            using CeSettingsWriteLock? settingsLock = CeSettingsWriteLock.TryAcquire(userFolder);
            if (settingsLock is null) return Refuse("CE settings are being changed by another program. Wait and try again.");
            settingsLock.Verify();
            if (Read(userFolder).Value is not CeSettings current || !SameSnapshot(current))
                return Refuse("ce.ini changed since you opened it. Read the latest settings before saving.");
            Outcome<byte[]> plan = Prepare(updateCheck, recordSessions);
            if (plan.Value is not byte[] bytes) return Refuse(plan.Message);
            if (_bytes.AsSpan().SequenceEqual(bytes)) return Refuse("The CE settings already have those values.");
            using BackupDirectory heldBackup = BackupDirectory.Create(realBackup, now, "onslaught-ce-settings");
            backupFolder = heldBackup.Folder;
            string backupName = Exists ? "ce.ini" : "ce.ini.did-not-exist.txt";
            byte[] preserved = Exists ? _bytes : Utf8.GetBytes("ce.ini did not exist before this change. No earlier settings file was replaced.\n");
            InstallReceipt backup = Write(System.IO.Path.Combine(backupFolder, backupName), preserved, null, backupFolder, null, null);
            if (!backup.Ok) return Refuse("No verified settings backup could be made. " + backup.Message, backupFolder);
            heldBackup.HoldCopy(backupName, preserved, ReadBounded);
            // The UI snapshot and the backup must still describe this exact file, not a newer save.
            settingsLock.Verify();
            if (Read(userFolder).Value is not CeSettings again || !SameSnapshot(again))
                return Refuse("ce.ini changed while it was being backed up. Nothing was written to it.", backupFolder);
            Action beforeCheckChecked = () => { settingsLock.Verify(); beforeCheck?.Invoke(); settingsLock.Verify(); };
            Action beforeSwapChecked = () =>
            {
                settingsLock.Verify();
                beforeSwap?.Invoke();
                settingsLock.Verify();
                CheckPackageFolders();
                if (gameRunning()) throw new IOException(GameInstaller.RunningMessage);
                VerifyBackup(heldBackup);
                settingsLock.Verify();
            };
            Action afterPublishChecked = () => { settingsLock.Verify(); afterPublish?.Invoke(); settingsLock.Verify(); VerifyBackup(heldBackup); };
            InstallReceipt result = Write(Path, bytes, Exists ? Sha256 : null, backupFolder, beforeCheckChecked, beforeSwapChecked,
                afterPublishChecked);
            // The caller presents the structured BackupFolder; keep the status free of a second recovery path.
            if (result.Ok)
                return GameInstaller.AfterPublication(Path, backupFolder, Exists, () =>
                {
                    settingsLock.Verify();
                    VerifyBackup(heldBackup);
                    return result with { Message = "CE launcher settings saved and verified." };
                });
            if (result.MayHaveChanged)
            {
                try { VerifyBackup(heldBackup); }
                catch (IOException)
                {
                    return result with { Message = "CE settings may have changed and the recovery backup could not be verified. " +
                        "Inspect both before using or attempting recovery. Earlier failure: " + result.Message };
                }
            }
            return result;
        }
        catch (Exception error) when (IsFileError(error))
        {
            return Refuse("CE settings were not saved: " + error.Message, backupFolder);
        }
    }

    private InstallReceipt Refuse(string message, string? backup = null) => new(false, message, Path, backup);

    private static void VerifyBackup(BackupDirectory backup)
    {
        try { backup.Verify(); }
        catch (Exception error) when (IsFileError(error))
        { throw new IOException("The recovery backup could not be verified. Its folder or file changed; inspect it before relying on it.", error); }
    }

    private bool SameSnapshot(CeSettings other) => other.Exists == Exists && other._identity == _identity &&
        other._bytes.AsSpan().SequenceEqual(_bytes);

    private static InstallReceipt Write(string path, byte[] bytes, string? earlier, string backup,
        Action? beforeCheck, Action? beforeSwap, Action? afterPublish = null) => OperatingSystem.IsLinux() && !GameInstaller.UsePortableInstall
        ? LinuxInstall.Write(path, bytes, earlier, backup, beforeCheck, beforeSwap, afterPublish, ReadBounded)
        : PortableInstall.Write(path, bytes, earlier, backup, beforeCheck, beforeSwap, afterPublish, ReadBounded);

    internal static byte[] ReadBounded(FileStream stream)
    {
        if (stream.Length > MaximumBytes) throw new IOException("ce.ini exceeds the launcher's one-megabyte limit.");
        byte[] bytes = new byte[checked((int)stream.Length)];
        stream.Position = 0;
        stream.ReadExactly(bytes);
        if (stream.ReadByte() != -1) throw new IOException("ce.ini changed length while being read.");
        return bytes;
    }

    private static (byte[] Bytes, string Identity) ReadProtected(string path)
    {
        if (OperatingSystem.IsLinux())
        {
            using LinuxSaveDirectory folder = LinuxSaveDirectory.Open(System.IO.Path.GetDirectoryName(path)!);
            using FileStream stream = folder.OpenRead(System.IO.Path.GetFileName(path));
            string identity = LinuxSaveNative.Inspect(stream.SafeFileHandle).Identity;
            byte[] bytes = ReadBounded(stream);
            folder.Verify();
            using FileStream named = folder.OpenRead(System.IO.Path.GetFileName(path));
            if (LinuxSaveNative.Inspect(named.SafeFileHandle).Identity != identity || !ReadBounded(named).AsSpan().SequenceEqual(bytes))
                throw new IOException("ce.ini changed while being read.");
            return (bytes, identity);
        }
        if (!OperatingSystem.IsWindows()) throw new PlatformNotSupportedException("CE settings writes support Linux and Windows.");
        using FileMutationSafety.DirectoryLockSet locks = FileMutationSafety.LockDirectoryTree(System.IO.Path.GetDirectoryName(path)!, "CE user folder");
        using SafeFileHandle handle = FileMutationSafety.OpenNoFollowReadHandle(path, "CE settings");
        WindowsFileIdentity file = FileMutationSafety.GetWindowsIdentity(handle, "CE settings");
        if (file.IsReparsePoint || file.NumberOfLinks != 1) throw new IOException("ce.ini must be a regular file without links.");
        using FileStream read = new(handle, FileAccess.Read);
        return (ReadBounded(read), $"{file.VolumeSerialNumber}:{file.FileIndex}");
    }

    private string? Value(string key)
    {
        foreach ((string line, _) in Lines(_text))
        {
            if (!line.StartsWith(key + "=", StringComparison.Ordinal)) continue;
            string value = line[(key.Length + 1)..];
            int cr = value.IndexOf('\r');
            return cr >= 0 ? value[..cr] : value;
        }
        return null;
    }

    private static IEnumerable<(string Line, string Ending)> Lines(string text)
    {
        int start = 0;
        while (start < text.Length)
        {
            int end = text.IndexOf('\n', start);
            if (end < 0) { yield return (text[start..], ""); yield break; }
            bool crlf = end > start && text[end - 1] == '\r';
            yield return (text[start..(crlf ? end - 1 : end)], crlf ? "\r\n" : "\n");
            start = end + 1;
        }
    }

    private static bool IsFileError(Exception error) => error is IOException or UnauthorizedAccessException or ArgumentException or
        InvalidOperationException or Win32Exception or NotSupportedException;
}
