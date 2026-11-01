// SPDX-License-Identifier: GPL-3.0-only
using System.Text;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Protected transport checks on new authored project files only.</summary>
internal static class EditorProjectFilesTests
{
    internal static void Run(string output, Checks check)
    {
        check.Suite("editor project files");
        string folder = Path.Combine(output, "project-file-fixture");
        Directory.CreateDirectory(folder);
        string FileAt(string name) => Path.Combine(folder, name + EditorProjectFiles.Extension);
        byte[] bytes = Encoding.UTF8.GetBytes("{\"authored\":\"editor fixture\"}\n");
        EditorProjectFiles files = new();
        string first = FileAt("first");
        EditorProjectWrite saved = files.WriteNew(first, bytes, []);
        EditorProjectRead read = files.Open(first);
        check.That(saved.Ok && read.Ok && read.Bytes is not null && read.Bytes.AsSpan().SequenceEqual(bytes) && read.Sha256 == EditorProject.Hash(bytes),
                   "a new authored project is published and independently reopened with the exact bytes");
        byte[] changed = Encoding.UTF8.GetBytes("changed authored project");
        check.That(!files.WriteNew(first, changed, []).Ok && File.ReadAllBytes(first).AsSpan().SequenceEqual(bytes),
                   "saving to an existing project refuses without changing its bytes");
        check.That(!files.Open(FileAt("missing")).Ok && !files.Open("relative" + EditorProjectFiles.Extension).Ok &&
                   !files.WriteNew(Path.Combine(folder, "other.bes"), bytes, []).Ok,
                   "missing files, relative paths and non-project filenames are refused");
        string protectedFolder = Path.Combine(folder, "protected-data-only");
        Directory.CreateDirectory(protectedFolder);
        string protectedOutput = Path.Combine(protectedFolder, "private" + EditorProjectFiles.Extension);
        check.That(!files.WriteNew(protectedOutput, bytes, [protectedFolder]).Ok && !File.Exists(protectedOutput),
                   "a selected protected data-only folder refuses project output");
        string tooLarge = FileAt("too-large");
        using (FileStream stream = new(tooLarge, FileMode.CreateNew)) stream.SetLength(EditorProject.MaxProjectBytes + 1L);
        check.That(!files.Open(tooLarge).Ok, "an oversized project refuses before its content is allocated");
        string changedOnRead = FileAt("changed-on-read");
        File.WriteAllBytes(changedOnRead, bytes);
        bool readMutation = false;
        EditorProjectFiles changingRead = new(afterRead: path => { File.WriteAllBytes(path, changed); readMutation = true; });
        check.That(!changingRead.Open(changedOnRead).Ok && File.ReadAllBytes(changedOnRead).AsSpan().SequenceEqual(readMutation ? changed : bytes),
                   "a file changed between its first read and identity verification is refused without repair or deletion");
        if (OperatingSystem.IsLinux())
        {
            string link = FileAt("linked-input");
            File.CreateSymbolicLink(link, first);
            string linkedFolder = Path.Combine(folder, "linked-folder");
            Directory.CreateSymbolicLink(linkedFolder, folder);
            check.That(!files.Open(link).Ok && !files.WriteNew(link, changed, []).Ok &&
                       !files.WriteNew(Path.Combine(linkedFolder, "through-link" + EditorProjectFiles.Extension), bytes, []).Ok &&
                       File.ReadAllBytes(first).AsSpan().SequenceEqual(bytes),
                       "linked input, existing linked output and linked output ancestors refuse without touching their targets");
            string hardLink = FileAt("hard-link");
            int linked = LinuxSaveNative.LinkAt(LinuxSaveNative.AtCurrentDirectory, first, LinuxSaveNative.AtCurrentDirectory, hardLink, 0);
            check.That(linked == 0 && !files.Open(first).Ok && !files.Open(hardLink).Ok,
                       "both names of a hard-linked project refuse protected input");
        }
        string race = FileAt("racing-output");
        EditorProjectFiles racing = new(beforePublish: path => File.WriteAllBytes(path, changed));
        EditorProjectWrite raceResult = racing.WriteNew(race, bytes, []);
        check.That(!raceResult.Ok && !raceResult.MayHaveOutput && File.ReadAllBytes(race).AsSpan().SequenceEqual(changed),
                   "a competing output created at publication is preserved and our new project is not published");
        string uncertain = FileAt("uncertain-output");
        bool outputMutation = false;
        EditorProjectFiles after = new(afterPublish: path => { File.WriteAllBytes(path, changed); outputMutation = true; });
        EditorProjectWrite uncertainResult = after.WriteNew(uncertain, bytes, []);
        check.That(!uncertainResult.Ok && uncertainResult.MayHaveOutput && File.ReadAllBytes(uncertain).AsSpan().SequenceEqual(outputMutation ? changed : bytes),
                   "failure after publication reports uncertainty and preserves the file for inspection");
    }
}
