// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Tests;

internal static class CeMissionProjectFilesTests
{
    internal static void Run(string output, Checks check)
    {
        check.Suite("CE mission project files");
        string root = Path.Combine(output, "ce-project-files");
        Directory.CreateDirectory(root);
        CeMissionProjectFiles files = new();
        byte[] bytes = CeMissionProjectJson.Write(CeMissionProjectTests.Authored());
        string path = Path.Combine(root, "authored.ceproject");
        CeProjectWrite saved = files.WriteNew(path, bytes, []);
        check.That(saved.Ok && File.ReadAllBytes(path).AsSpan().SequenceEqual(bytes), "project publication writes exactly the authored document");
        CeProjectRead opened = files.Open(path);
        check.That(opened.Ok && opened.Bytes is { } read && read.AsSpan().SequenceEqual(bytes), "protected reopening reads exactly the saved document");
        check.That(!files.WriteNew(path, bytes, []).Ok && File.ReadAllBytes(path).AsSpan().SequenceEqual(bytes), "an existing project is never replaced");
        string wrongExtension = Path.Combine(root, "not-a-project.txt");
        check.That(!files.WriteNew(wrongExtension, bytes, []).Ok && !File.Exists(wrongExtension), "project publication requires its own extension");
        string invalid = Path.Combine(root, "invalid.ceproject");
        check.That(!files.WriteNew(invalid, "invalid document"u8.ToArray(), []).Ok && !File.Exists(invalid), "malformed documents are refused before publication");
        string guarded = Path.Combine(root, "protected");
        Directory.CreateDirectory(guarded);
        string guardedPath = Path.Combine(guarded, "refused.ceproject");
        check.That(!files.WriteNew(guardedPath, bytes, [guarded]).Ok && !File.Exists(guardedPath), "caller-protected game/profile/backup roots refuse project output");

        string collision = Path.Combine(root, "collision.ceproject");
        byte[] unique = "new external file"u8.ToArray();
        CeMissionProjectFiles race = new(beforePublish: target =>
        {
            using FileStream stream = new(target, FileMode.CreateNew, FileAccess.Write);
            stream.Write(unique);
        });
        CeProjectWrite collided = race.WriteNew(collision, bytes, []);
        check.That(!collided.Ok && !collided.MayHaveOutput && File.ReadAllBytes(collision).AsSpan().SequenceEqual(unique),
            "a file created at publication is preserved and never reported as our output");
        string uncertain = Path.Combine(root, "uncertain.ceproject");
        CeMissionProjectFiles after = new(afterPublish: _ => throw new IOException("authored post-publication failure"));
        CeProjectWrite failure = after.WriteNew(uncertain, bytes, []);
        check.That(!failure.Ok && failure.MayHaveOutput && File.ReadAllBytes(uncertain).AsSpan().SequenceEqual(bytes),
            "a post-publication failure reports uncertainty and keeps the published project for inspection");
        string large = Path.Combine(root, "oversized.ceproject");
        using (FileStream stream = new(large, FileMode.CreateNew, FileAccess.Write)) stream.SetLength(CeMissionProject.MaxDocumentBytes + 1L);
        check.That(!files.Open(large).Ok, "oversized project reads are refused before allocation");

        if (OperatingSystem.IsLinux())
        {
            string alias = Path.Combine(root, "linked.ceproject");
            File.CreateSymbolicLink(alias, path);
            check.That(!files.Open(alias).Ok, "linked project sources are refused");
            string folderAlias = Path.Combine(root, "linked-folder");
            Directory.CreateSymbolicLink(folderAlias, guarded);
            check.That(!files.WriteNew(Path.Combine(folderAlias, "through-link.ceproject"), bytes, [guarded]).Ok &&
                !File.Exists(Path.Combine(guarded, "through-link.ceproject")), "a folder alias cannot redirect project output into a protected root");
        }
    }
}
