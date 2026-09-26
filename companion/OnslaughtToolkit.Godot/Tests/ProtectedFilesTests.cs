// SPDX-License-Identifier: MIT
using System.Diagnostics;
using System.Security.Cryptography;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Direct protected-adapter checks on fresh, invocation-owned copies only. This suite covers
/// filesystem identity and publication; career semantics belong to <see cref="CareerSaveTests"/>,
/// because the adapter deliberately does not interpret save fields.
/// </summary>
internal static class ProtectedFilesTests
{
    private const int Start = 0x2406;

    internal static void Run(byte[] original, string outputDirectory, Checks check)
    {
        check.Suite("protected files");
        if (original.Length != 10004)
        {
            check.Fail("Protected file tests require bytes from an owned real 10,004-byte baseline.");
            return;
        }
        string root = Path.Combine(outputDirectory, "protected-files");
        if (Path.Exists(root))
        {
            check.Fail("Protected file tests require a fresh invocation-owned output directory.");
            return;
        }
        Directory.CreateDirectory(root);
        ProtectedSaveFiles adapter = new();
        string originalHash = Hash(original);

        Case roundTrip = new(root, "roundtrip", original);
        ProtectedRead snapshot = adapter.OpenCareer(roundTrip.Input);
        check.That(snapshot.Ok, "Direct adapter opens the owned baseline.");
        if (!snapshot.Ok)
        {
            check.Fail("Protected baseline open failed: " + snapshot.Message);
            return;
        }
        check.That(snapshot.Bytes is byte[] read && read.AsSpan().SequenceEqual(original) && snapshot.Size == 10004 &&
            snapshot.Sha256 == originalHash, "Open returns exact bytes, size and independently calculated SHA-256.");
        check.That(snapshot.Identity.Length > 0, "Open returns physical file identity.");
        PublicationReceipt copied = Publish(adapter, roundTrip, snapshot, original);
        check.That(copied.Ok && copied.Verified && copied.OriginalVerified,
            "Unchanged copy has explicit publication and original verification.");
        ProtectedRead reopened = adapter.OpenCareer(roundTrip.Output);
        check.That(reopened.Ok && reopened.Bytes is byte[] again && again.AsSpan().SequenceEqual(original),
            "Unchanged output reopens byte-for-byte identical.");
        check.That(reopened.Identity != snapshot.Identity, "The recovery copy has its own physical identity.");
        check.That(Directory.GetFiles(roundTrip.OutputDirectory).Length == 1,
            "Successful publication leaves only the requested named copy.");
        OriginalUnchanged(roundTrip, original, check);

        Case edited = new(root, "edited", original);
        byte[] prepared = original.ToArray();
        // Independent literal layout and three-byte arithmetic; no call to the career codec.
        int target = ((original[Start] | (original[Start + 1] << 8) | (original[Start + 2] << 16)) + 123457) & 0xFFFFFF;
        for (int index = 0; index < 3; index++)
            prepared[Start + index] = (byte)((target >> (index * 8)) & 0xFF);
        snapshot = adapter.OpenCareer(edited.Input);
        PublicationReceipt written = Publish(adapter, edited, snapshot, prepared);
        check.That(written.Ok, "Direct adapter publishes the independently prepared edit.");
        byte[] actual = File.Exists(edited.Output) ? File.ReadAllBytes(edited.Output) : [];
        check.That(actual.AsSpan().SequenceEqual(prepared), "Published output has exact prepared bytes and original length.");
        if (actual.Length == original.Length)
        {
            bool validDiff = true;
            for (int offset = 0; offset < original.Length; offset++)
            {
                if ((offset < Start || offset >= Start + 3) && actual[offset] != original[offset]) validDiff = false;
            }
            int intended = actual[Start] | (actual[Start + 1] << 8) | (actual[Start + 2] << 16);
            check.That(validDiff && intended == target,
                "Independent diff preserves every unknown/unselected byte, including the packed high byte.");
        }
        check.That(written.Bytes is byte[] receipt && receipt.AsSpan().SequenceEqual(prepared) && written.Sha256 == Hash(prepared),
            "Publication receipt contains exact output bytes and independent SHA-256.");
        OriginalUnchanged(edited, original, check);

        Case malformed = new(root, "malformed", original);
        snapshot = adapter.OpenCareer(malformed.Input);
        foreach (byte[] bytes in new[] { Array.Empty<byte>(), original[..10003], [.. original, 0] })
            Refusal(Publish(adapter, malformed, snapshot, bytes), "Incorrect prepared length", check);
        foreach (string badHash in new[] { "", "0", new string('z', 64), new string('0', 64) })
            Refusal(Publish(adapter, malformed, snapshot with { Sha256 = badHash }, original), "Malformed or incorrect source hash", check);
        Refusal(Publish(adapter, malformed, snapshot with { Identity = "" }, original), "Missing source identity", check);
        check.That(Directory.GetFileSystemEntries(malformed.OutputDirectory).Length == 0,
            "Invalid publication arguments create no named output.");
        OriginalUnchanged(malformed, original, check);
        File.WriteAllBytes(malformed.Input, original[..10003]);
        Refusal(adapter.OpenCareer(malformed.Input), "Truncated source", check);
        File.WriteAllBytes(Path.Combine(root, "unsupported.bin"), original);
        foreach (string path in new[] { "", "relative.bes", malformed.Input + " ", Path.Combine(root, "unsupported.bin") })
            Refusal(adapter.OpenCareer(path), "Invalid source path", check);

        Case changed = new(root, "changed-source", original);
        snapshot = adapter.OpenCareer(changed.Input);
        byte[] changedBytes = original.ToArray();
        changedBytes[^1] ^= 1;
        File.WriteAllBytes(changed.Input, changedBytes);
        Refusal(Publish(adapter, changed, snapshot, original), "Changed source content", check);
        check.That(!File.Exists(changed.Output) && File.ReadAllBytes(changed.Input).AsSpan().SequenceEqual(changedBytes),
            "Changed-source refusal preserves the changed source and publishes nothing.");

        Case replaced = new(root, "replaced-source", original);
        snapshot = adapter.OpenCareer(replaced.Input);
        string displaced = Path.Combine(replaced.Root, "displaced.bes");
        File.Move(replaced.Input, displaced);
        File.WriteAllBytes(replaced.Input, original);
        Refusal(Publish(adapter, replaced, snapshot, original), "Same bytes under a new physical source identity", check);
        check.That(!File.Exists(replaced.Output) && File.ReadAllBytes(displaced).AsSpan().SequenceEqual(original),
            "Identity refusal leaves both owned source generations intact.");
        OriginalUnchanged(replaced, original, check);

        Case conflict = new(root, "conflicting-output", original);
        snapshot = adapter.OpenCareer(conflict.Input);
        File.WriteAllBytes(conflict.Output, changedBytes);
        Refusal(Publish(adapter, conflict, snapshot, original), "Existing destination", check);
        check.That(File.ReadAllBytes(conflict.Output).AsSpan().SequenceEqual(changedBytes), "The conflicting destination is never replaced.");
        Refusal(Publish(adapter, conflict with { Output = conflict.Input }, snapshot, original), "Source as destination", check);
        Refusal(Publish(adapter, conflict with { Output = Path.Combine(conflict.Root, "missing", "copy.bes") }, snapshot, original),
            "Missing destination parent", check);
        check.That(!Directory.Exists(Path.Combine(conflict.Root, "missing")), "Publication does not create an unapproved output folder.");
        OriginalUnchanged(conflict, original, check);

        Case game = new(root, "game-tree", original);
        snapshot = adapter.OpenCareer(game.Input);
        File.WriteAllText(Path.Combine(game.OutputDirectory, "BEA.exe"), "Owned test marker; not an executable.");
        Directory.CreateDirectory(Path.Combine(game.OutputDirectory, "data"));
        Refusal(Publish(adapter, game, snapshot, original), "Game-tree destination", check);
        check.That(!File.Exists(game.Output), "Game-tree refusal creates no save.");
        OriginalUnchanged(game, original, check);

        Case options = new(root, "options-file", original);
        string optionsInput = Path.Combine(options.Root, "defaultoptions.bea");
        File.Move(options.Input, optionsInput);
        ProtectedRead optionsRead = adapter.OpenCareer(optionsInput);
        check.That(optionsRead.Ok && optionsRead.Bytes is byte[] optionBytes && optionBytes.AsSpan().SequenceEqual(original),
            "The game's .bea options file opens through the same protected read.");
        Refusal(adapter.PublishCopy(optionsInput, optionsRead.Identity, optionsRead.Sha256, options.Output, original),
            "An options file published under a .bes name", check);
        PublicationReceipt optionsCopy = adapter.PublishCopy(optionsInput, optionsRead.Identity, optionsRead.Sha256,
            Path.Combine(options.OutputDirectory, "defaultoptions-copy.bea"), original);
        check.That(optionsCopy.Ok && optionsCopy.Verified, "An options file copies to a new .bea file.");

        if (OperatingSystem.IsLinux()) LinuxAliases(adapter, root, original, check);
    }

    private static void LinuxAliases(ProtectedSaveFiles adapter, string root, byte[] original, Checks check)
    {
        Case links = new(root, "symlinks", original);
        ProtectedRead snapshot = adapter.OpenCareer(links.Input);
        File.CreateSymbolicLink(Path.Combine(links.Root, "source-link.bes"), links.Input);
        Refusal(adapter.OpenCareer(Path.Combine(links.Root, "source-link.bes")), "Linked source", check);
        Directory.CreateSymbolicLink(Path.Combine(links.Root, "output-link"), links.OutputDirectory);
        Refusal(Publish(adapter, links with { Output = Path.Combine(links.Root, "output-link", "copy.bes") }, snapshot, original),
            "Linked output parent", check);
        check.That(Directory.GetFileSystemEntries(links.OutputDirectory).Length == 0, "Linked-parent refusal creates no output.");
        string dangling = Path.Combine(links.Root, "absent-target.bes");
        File.CreateSymbolicLink(links.Output, dangling);
        Refusal(Publish(adapter, links, snapshot, original), "Dangling destination symlink", check);
        check.That(new FileInfo(links.Output).LinkTarget is not null && !File.Exists(dangling),
            "Dangling destination link survives and its target is not created.");
        OriginalUnchanged(links, original, check);

        Case hard = new(root, "hardlinks", original);
        snapshot = adapter.OpenCareer(hard.Input);
        string alias = Path.Combine(hard.Root, "alias.bes");
        // Linux-only test setup: an explicit absolute executable and argument vector, no shell.
        using Process? link = Process.Start(new ProcessStartInfo("/usr/bin/ln") { ArgumentList = { "--", hard.Input, alias } });
        link?.WaitForExit();
        check.That(link?.ExitCode == 0, "Owned hardlink fixture created with /usr/bin/ln.");
        if (link?.ExitCode == 0)
        {
            Refusal(adapter.OpenCareer(alias), "Hardlinked source before open", check);
            Refusal(Publish(adapter, hard, snapshot, original), "Hardlink added after source open", check);
            check.That(!File.Exists(hard.Output) && File.ReadAllBytes(alias).AsSpan().SequenceEqual(original),
                "Hardlink refusal leaves alias bytes unchanged and publishes nothing.");
        }
        OriginalUnchanged(hard, original, check);
    }

    private static PublicationReceipt Publish(ProtectedSaveFiles adapter, Case fixture, ProtectedRead snapshot, byte[] prepared) =>
        adapter.PublishCopy(fixture.Input, snapshot.Identity, snapshot.Sha256, fixture.Output, prepared);

    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes));

    private static void OriginalUnchanged(Case fixture, byte[] original, Checks check) =>
        check.That(File.ReadAllBytes(fixture.Input).AsSpan().SequenceEqual(original),
            "Original remains byte-identical: " + Path.GetFileName(fixture.Root));

    private static void Refusal(ProtectedRead reply, string context, Checks check) =>
        check.That(!reply.Ok && reply.Bytes is null, context + " is refused without returning save bytes.");

    private static void Refusal(PublicationReceipt reply, string context, Checks check)
    {
        check.That(!reply.Ok && !reply.Verified, context + " is refused without a success receipt.");
        check.That(!reply.MayHaveOutput, context + " is rejected before publication.");
    }

    private sealed record Case(string Root, string Input, string OutputDirectory, string Output)
    {
        internal Case(string parent, string name, byte[] original)
            : this(Path.Combine(parent, name), Path.Combine(parent, name, "original.bes"),
                Path.Combine(parent, name, "output"), Path.Combine(parent, name, "output", "copy.bes"))
        {
            Directory.CreateDirectory(OutputDirectory);
            File.WriteAllBytes(Input, original);
        }
    }
}
