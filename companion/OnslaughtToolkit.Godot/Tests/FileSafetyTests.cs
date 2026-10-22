// SPDX-License-Identifier: GPL-3.0-only
using System.ComponentModel;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The file-safety primitives the companion keeps (Files/FileMutationSafety.cs), carried over from the retired
/// AppCore FileMutationSafetyTests. Link, game-folder and blank-path cases run everywhere; the Windows handle,
/// lock and path-form cases run only on Windows and add no checks elsewhere, since this machine cannot run them.
/// </summary>
internal static class FileSafetyTests
{
    internal static void Run(byte[] original, string outputDirectory, Checks check)
    {
        check.Suite("file safety");
        string root = Path.Combine(outputDirectory, "file-safety");
        Directory.CreateDirectory(root);

        // Refusals name the thing in plain words, never the caller's internal label.
        Exception? blank = Catch(() => FileMutationSafety.NormalizeLocalPath("  ", "Generated profile root"));
        check.That(blank is ArgumentException { ParamName: "path" } argument &&
            argument.Message.StartsWith(FileMutationSafety.FileOrFolderRequired, StringComparison.Ordinal) &&
            !argument.Message.Contains("Generated profile root"), "A blank path is refused as 'a file or folder is required'.");

        string real = Path.Combine(root, "real.bes");
        File.WriteAllBytes(real, original);
        string fileLink = Path.Combine(root, "link.bes");
        string realFolder = Directory.CreateDirectory(Path.Combine(root, "real-folder")).FullName;
        string folderLink = Path.Combine(root, "linked-folder");
        if (TryLink(() => File.CreateSymbolicLink(fileLink, real)))
        {
            Exception? linked = Catch(() => FileMutationSafety.RejectReparsePoint(fileLink, "app-owned output root"));
            check.That(linked is InvalidOperationException && linked.Message == "That file cannot use a shortcut or link." &&
                Plain(linked.Message, "app-owned output root"), "A linked file is refused in plain words.");
            // On Windows the open takes the link itself, and its callers refuse it by identity; elsewhere the open refuses.
            if (!OperatingSystem.IsWindows())
            {
                Exception? opened = Catch(() => FileMutationSafety.OpenNoFollowReadHandle(fileLink, "Generated profile root").Dispose());
                check.That(opened is not null && opened.Message.Contains("shortcut or link") && Plain(opened.Message, "Generated profile root"),
                    "A protected open refuses a linked file.");
            }
        }
        else if (!OperatingSystem.IsWindows()) check.Fail("A file symbolic link could not be made for the link cases.");
        if (TryLink(() => Directory.CreateSymbolicLink(folderLink, realFolder)))
        {
            Exception? linked = Catch(() => FileMutationSafety.RejectReparsePoint(folderLink, "app-owned output root"));
            check.That(linked is InvalidOperationException && linked.Message == "That folder cannot use a shortcut or link." &&
                Plain(linked.Message, "app-owned output root"), "A linked folder is refused in plain words.");
            string inside = Directory.CreateDirectory(Path.Combine(realFolder, "inside")).FullName;
            Exception? locked = Catch(() => FileMutationSafety.LockDirectoryTree(Path.Combine(folderLink, "inside"), "Test directory").Dispose());
            check.That(locked is InvalidOperationException && locked.Message == FileMutationSafety.FolderCannotUseLink && Directory.Exists(inside),
                "A folder reached through a linked folder cannot be locked for writing.");
        }
        else if (!OperatingSystem.IsWindows()) check.Fail("A folder symbolic link could not be made for the link cases.");

        string game = Directory.CreateDirectory(Path.Combine(root, "game", "data")).Parent!.FullName;
        File.WriteAllText(Path.Combine(game, "BEA.exe"), "not a game");
        Exception? inGame = Catch(() => FileMutationSafety.RejectOutputInGameTree(Path.Combine(game, "savegames", "copy.bes")));
        check.That(inGame is InvalidOperationException && inGame.Message == FileMutationSafety.OutputInsideGameFolder &&
            Catch(() => FileMutationSafety.RejectOutputInGameTree(Path.Combine(root, "copy.bes"))) is null,
            "A copy may not go anywhere inside a folder holding BEA.exe and data/, and may go beside it.");

        // A committed copy swapped for a link before its read-back is refused, and neither file is overwritten.
        string input = Path.Combine(root, "input.bes"), output = Path.Combine(root, "output.bes"), escaped = Path.Combine(root, "escaped.bes");
        File.WriteAllBytes(input, original);
        Exception? swapped = Catch(() =>
        {
            using GuardedFileMutation mutation = FileMutationSafety.BeginGeneratedVacant(output, input);
            mutation.Commit(original, committed =>
            {
                File.Move(committed, escaped);
                File.CreateSymbolicLink(committed, escaped);
            });
        });
        check.That(swapped is not null && swapped.Message.Contains("shortcut or link") && !swapped.Message.Contains("reparse", StringComparison.OrdinalIgnoreCase) &&
            File.ReadAllBytes(input).AsSpan().SequenceEqual(original) && File.ReadAllBytes(escaped).AsSpan().SequenceEqual(original),
            "A copy replaced by a link after publication fails its read-back, and the input and the moved copy keep their bytes.");

        if (OperatingSystem.IsWindows()) Windows(root, check);
    }

    /// <summary>The Windows-only members: path forms, handle errors, directory locks and the staged-file quarantine.</summary>
    private static void Windows(string root, Checks check)
    {
        (string Path, string Expected)[] forms =
        [
            (@"\\?\C:\gone.bes", FileMutationSafety.FileCannotUseDeviceLocation),
            (System.IO.Path.Combine(root, "NUL.bes"), FileMutationSafety.FileCannotUseReservedDevice),
            (System.IO.Path.Combine(root, "output.bes:payload"), FileMutationSafety.FileCannotUseAlternateStream),
            (@"\\server\share\output.bes", FileMutationSafety.FileCannotUseNetworkLocation),
            (@"C:output.bes", FileMutationSafety.FileCannotUseDriveRelativeLocation),
        ];
        foreach ((string path, string expected) in forms)
        {
            Exception? error = Catch(() => FileMutationSafety.NormalizeLocalPath(path, "Generated profile root"));
            check.That(error is InvalidOperationException && error.Message == expected && Plain(error.Message, "Generated profile root") &&
                !error.Message.Contains("NUL") && !error.Message.Contains("DOS"), $"{path} is refused as: {expected}");
        }

        using (SafeFileHandle invalid = new(IntPtr.Zero, ownsHandle: false))
        {
            Exception? error = Catch(() => FileMutationSafety.GetWindowsIdentity(invalid, "Generated profile root"));
            check.That(error is IOException && error.Message == FileMutationSafety.FileCouldNotBeInspected &&
                Plain(error.Message, "Generated profile root") && !error.Message.Contains("Win32"), "A failed identity read names the file, not Win32.");
        }
        string missing = System.IO.Path.Combine(root, Guid.NewGuid().ToString("N"), "gone.bes");
        Exception? open = Catch(() => FileMutationSafety.OpenNoFollowReadHandle(missing, "Generated profile root").Dispose());
        check.That(open is IOException { InnerException: Win32Exception } && open.Message == FileMutationSafety.FileCouldNotBeSecured &&
            !open.Message.Contains(missing, StringComparison.OrdinalIgnoreCase), "A failed protected open names the file, not Win32.");

        string lockedDirectory = Directory.CreateDirectory(System.IO.Path.Combine(root, "locked")).FullName;
        using (FileMutationSafety.LockDirectoryTree(lockedDirectory, "Test directory"))
        {
            Exception? moved = Catch(() => Directory.Move(lockedDirectory, System.IO.Path.Combine(root, "moved")));
            check.That(moved is IOException && Directory.Exists(lockedDirectory), "A locked folder cannot be renamed.");
        }

        string guarded = Directory.CreateDirectory(System.IO.Path.Combine(root, "guarded-output")).FullName;
        using (FileMutationSafety.DirectoryLockSet locks = FileMutationSafety.LockDirectoryTree(guarded, "Guarded output", guardTargetMutation: true))
        {
            bool sentinel = Directory.EnumerateFiles(guarded, ".onslaught-directory-guard-*.tmp").Count() == 1;
            File.WriteAllText(System.IO.Path.Combine(guarded, "payload.bin"), "payload");
            locks.ReleaseMutationSentinelIfDirectoryNonEmpty();
            check.That(sentinel && !Directory.EnumerateFiles(guarded, ".onslaught-directory-guard-*.tmp").Any() &&
                File.ReadAllText(System.IO.Path.Combine(guarded, "payload.bin")) == "payload",
                "An empty output folder keeps its guard until another entry exists.");
        }

        string selected = Directory.CreateDirectory(System.IO.Path.Combine(root, "selected")).FullName;
        string originalDirectory = System.IO.Path.Combine(root, "selected-original");
        string outside = Directory.CreateDirectory(System.IO.Path.Combine(root, "outside")).FullName;
        try
        {
            Exception? swap = Catch(() => FileMutationSafety.LockDirectoryTree(selected, "Test directory", beforeFirstOpenForTest: () =>
            {
                Directory.Move(selected, originalDirectory);
                Directory.CreateSymbolicLink(selected, outside);
            }).Dispose());
            check.That(swap is InvalidOperationException && swap.Message.Contains("shortcut or link") &&
                !swap.Message.Contains("reparse", StringComparison.OrdinalIgnoreCase), "A folder swapped for a link before locking is refused.");
        }
        finally
        {
            if (Directory.Exists(selected) && (File.GetAttributes(selected) & FileAttributes.ReparsePoint) != 0) Directory.Delete(selected);
            if (Directory.Exists(originalDirectory)) Directory.Move(originalDirectory, selected);
        }

        string staged = System.IO.Path.Combine(root, "staged.tmp");
        using (FileStream stream = FileMutationSafety.CreateStagedFile(staged))
        {
            stream.Write([0x01, 0x02, 0x03]);
            Exception? moved = Catch(() => File.Move(staged, System.IO.Path.Combine(root, "moved.tmp")));
            check.That(moved is IOException or UnauthorizedAccessException && File.Exists(staged), "A staged file cannot be renamed while it is written.");
        }
        string alias = System.IO.Path.Combine(root, "outside-alias.tmp"), aliased = System.IO.Path.Combine(root, "aliased.tmp");
        Exception? hardlinked = Catch(() => FileMutationSafety.CreateStagedFile(aliased,
            created => { if (!CreateHardLink(alias, created, IntPtr.Zero)) throw new Win32Exception(Marshal.GetLastWin32Error()); }).Dispose());
        check.That(hardlinked is IOException or InvalidOperationException && File.Exists(alias) && new FileInfo(alias).Length == 0 && !File.Exists(aliased),
            "A staged file that gains a hard link before it is written is refused, and nothing is written through the link.");
    }

    private static bool Plain(string message, string label) =>
        !message.Contains(label, StringComparison.Ordinal) && !message.Contains("reparse", StringComparison.OrdinalIgnoreCase) &&
        !message.Contains("path", StringComparison.OrdinalIgnoreCase);

    private static Exception? Catch(Action action)
    {
        try
        {
            action();
            return null;
        }
        catch (Exception error)
        {
            return error;
        }
    }

    /// <summary>Makes a link; Windows without the privilege to make one skips those cases, as the AppCore tests did.</summary>
    private static bool TryLink(Action make)
    {
        try
        {
            make();
            return true;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
        {
            return false;
        }
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool CreateHardLink(string lpFileName, string lpExistingFileName, IntPtr lpSecurityAttributes);
}
