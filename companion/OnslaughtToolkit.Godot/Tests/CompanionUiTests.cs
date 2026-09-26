// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Drives the code-built interface and the in-process protected adapter, exclusively on the
/// runner-owned fixture copy and fresh outputs.
/// </summary>
internal static class CompanionUiTests
{
    internal static async Task RunAsync(SceneTree tree, string fixture, string outputDirectory, byte[] original, Checks check)
    {
        check.Suite("companion interface");
        SwitchableSaveFiles files = new(new ProtectedSaveFiles());
        FakeInstall install = FakeInstall.Create(Path.Combine(outputDirectory, "ui-install"), original);
        CompanionEnvironment environment = new([install.SteamRoot], Path.Combine(outputDirectory, "ui-settings", "settings.json"));
        CompanionApp app = new(files, managesWindow: false, environment);
        tree.Root.AddChild(app);
        await Frame(tree);
        for (int frame = 0; frame < 600 && (app.Game.Busy || app.Game.Folder is null); frame++) await Frame(tree);
        try
        {
            await Drive(app, files, tree, install, fixture, outputDirectory, original, check);
        }
        finally
        {
            File.WriteAllBytes(fixture, original);
            app.QueueFree();
            await Frame(tree);
        }
        await UnavailableWorker(outputDirectory, original, check);
    }

    private static async Task Drive(CompanionApp app, SwitchableSaveFiles files, SceneTree tree, FakeInstall install,
        string fixture, string outputDirectory, byte[] original, Checks check)
    {
        check.That(app.Game.Folder?.Root == install.Game && app.Home.OpenButtons.Count == 1 && !app.Home.OpenButtons[0].Disabled,
            "Home finds the game through Steam and lists its career with an Open button.");
        check.That(app.Status.Game.Text.Contains("differs"), "The status bar says the test executable is not the Steam release.");
        EditCopyPage lab = app.EditCopy;
        check.That(app.Pages.Count >= 5 && app.Sidebar.Items.Count == app.Pages.Count, "every page has one sidebar item");
        check.That(app.Current == app.Home && app.Home.Root.Visible, "the companion starts on Home");
        foreach (Page page in app.Pages.Values)
        {
            app.Navigate(page.Key);
            check.That(app.Current == page && page.Root.Visible && app.PageTitle.Text == page.Title.ToUpperInvariant() &&
                app.Pages.Values.Count(other => other.Root.Visible) == 1, "navigation shows exactly one page: " + page.Key);
        }
        app.Navigate("home");
        check.That(lab.Rows.Count == 5, "five code-built editable rows");
        check.That(lab.WriteCopy.Disabled && lab.BackupCopy.Disabled, "writing unavailable before open");
        foreach (FileDialog dialog in new[] { app.OpenDialog, lab.OutputDialog, app.Compare.Dialog, app.MediaFiles.FolderDialog })
        {
            check.That(!dialog.DeletingEnabled && !dialog.FolderCreationEnabled && dialog.Access == FileDialog.AccessEnum.Filesystem,
                "file dialog has no mutation actions: " + dialog.Title);
        }

        app.Home.OpenButtons[0].EmitSignal(BaseButton.SignalName.Pressed);
        for (int frame = 0; frame < 600 && app.Workspace.Session?.Path != install.Career; frame++) await Frame(tree);
        check.That(app.Workspace.Session?.Path == install.Career && app.Current == app.Overview && app.CareerName.Text == "Career One.bes",
            "opening a career from Home shows it in the header and moves to its overview");
        CareerInspection opened1 = app.Workspace.Session!.Analysis;
        check.That(app.Overview.MissionsSummary == $"{opened1.MissionCensus.Completed} / {opened1.MissionCensus.Used}" &&
            app.Overview.Missions.GetRoot()?.GetChildCount() == opened1.MissionCensus.Used, "the overview lists every used mission");
        app.Navigate("goodies");
        check.That(app.Goodies.Cells.Count == 233 && app.Goodies.Selected == 0, "the Goodies gallery shows all 233 displayable slots");
        app.Goodies.Cells[2].EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Goodies.Selected == 2 && app.Goodies.DetailEvidence.StartsWith("Seen in the game") &&
            app.Goodies.DetailRule.Contains("Goodie 001"), "Goodie 2 shows its rule and its in-game evidence");
        app.Goodies.Cells[150].EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Goodies.DetailEvidence.StartsWith("From the developers' source"), "an unchecked rule says it comes from the source only");
        check.That(File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original), "opening a game career changes nothing");

        Outcome<SaveSession> opened = await app.OpenCareerAsync(fixture);
        check.That(opened.Ok && app.CareerName.Text == Path.GetFileName(fixture), "companion opens the protected real fixture");
        if (app.Workspace.Session is not SaveSession session)
        {
            check.Fail("open failed: " + opened.Message);
            return;
        }
        byte[] leaked = session.CopyBytes();
        leaked[12] ^= 1;
        check.That(session.Matches(original), "session bytes are not exposed for mutation");
        check.That(lab.SourceDetails.Text.Contains(session.Sha256), "the open original's fingerprint is shown");

        // An explicit unchanged copy exercises the byte-for-byte round trip and reopen.
        string recovery = Path.Combine(outputDirectory, "recovery.bes");
        lab.Destination.Text = recovery;
        PublicationReceipt backup = await lab.WriteCopyAsync(unchanged: true);
        check.That(backup.Ok, "unchanged copy publishes and reopens");
        check.That(File.Exists(recovery) && File.ReadAllBytes(recovery).AsSpan().SequenceEqual(original), "round trip preserves every byte");
        check.That(!lab.ReopenCopy.Disabled, "a verified result can be opened");

        // Drive the real row controls. A preview never writes, and only two categories change.
        foreach (int index in new[] { 0, 4 })
        {
            lab.Rows[index].Target.Value = 123456 + index;
            lab.Rows[index].Selected.ButtonPressed = true;
        }
        string edited = Path.Combine(outputDirectory, "edited.bes");
        lab.Destination.Text = edited;
        check.That(!File.Exists(edited), "preview does not write");
        check.That(!lab.WriteCopy.Disabled, "valid explicit preview enables write");
        int expectedChanged = 0;
        foreach ((int offset, int value) in new[] { (0x23F6, 123456), (0x2406, 123460) })
        {
            for (int index = 0; index < 3; index++)
                if (original[offset + index] != (byte)(value >> (8 * index))) expectedChanged++;
        }
        check.That(lab.Preview.GetParsedText().Contains($"\n{expectedChanged} changed bytes;"), "the preview counts every changed byte");
        PublicationReceipt written = await lab.WriteCopyAsync(unchanged: false);
        check.That(written.Ok, "selected edit publishes and reopens");
        byte[] actual = File.Exists(edited) ? File.ReadAllBytes(edited) : [];
        check.That(actual.Length == original.Length, "edited length preserved");
        if (actual.Length == original.Length)
        {
            // Independent literal layout, not a call to the codec under test.
            for (int offset = 0; offset < original.Length; offset++)
            {
                bool allowed = offset is >= 0x23F6 and < 0x23F9 or >= 0x2406 and < 0x2409;
                if (!allowed && actual[offset] != original[offset]) check.Fail($"unselected byte changed at {offset}");
            }
            check.That((BinaryPrimitives.ReadUInt32LittleEndian(actual.AsSpan(0x23F6)) & 0xFFFFFF) == 123456,
                "aircraft intended count independently read");
            check.That((BinaryPrimitives.ReadUInt32LittleEndian(actual.AsSpan(0x2406)) & 0xFFFFFF) == 123460,
                "mech intended count independently read");
        }
        check.That(File.ReadAllBytes(fixture).AsSpan().SequenceEqual(original), "original unchanged after publication");

        Outcome<CareerComparison> compared = await app.Compare.CompareAsync(edited);
        check.That(compared.Value is { Bytes.ChangedBytes: > 0 }, "byte comparison reports the output difference");
        check.That(app.Compare.Tree.GetRoot()?.GetChildCount() == compared.Value?.Bytes.ChangedBytes,
            "every differing byte is listed");

        PublicationReceipt duplicate = await lab.WriteCopyAsync(unchanged: false);
        check.That(!duplicate.Ok, "existing output refused");
        check.That(File.ReadAllBytes(edited).AsSpan().SequenceEqual(actual), "conflicting output is unchanged");
        check.That(lab.ReopenCopy.Disabled, "failed publication cannot offer a stale successful result");
        check.That(app.Status.Failed, "the refusal is reported as a failure");

        // Malformed bytes are read safely but refused by the career codec.
        byte[] malformed = original.ToArray();
        malformed[0] ^= 1;
        string malformedPath = Path.Combine(outputDirectory, "malformed.bes");
        File.WriteAllBytes(malformedPath, malformed);
        Outcome<SaveSession> refused = await app.OpenCareerAsync(malformedPath);
        check.That(!refused.Ok, "malformed version refused");
        check.That(app.Workspace.Session?.Path == fixture, "failed open keeps the clearly displayed original session");

        // Source contents changed since open: refuse and leave the destination absent.
        byte[] changed = original.ToArray();
        changed[^1] ^= 1;
        File.WriteAllBytes(fixture, changed);
        string refusedOutput = Path.Combine(outputDirectory, "source-changed.bes");
        lab.Destination.Text = refusedOutput;
        PublicationReceipt sourceChanged = await lab.WriteCopyAsync(unchanged: false);
        check.That(!sourceChanged.Ok, "source change refused");
        check.That(!File.Exists(refusedOutput), "source refusal publishes nothing");
        File.WriteAllBytes(fixture, original);

        // Unavailable protected access must never fall back to an ordinary write.
        files.Available = false;
        PublicationReceipt unavailable = await lab.WriteCopyAsync(unchanged: false);
        check.That(!unavailable.Ok && !unavailable.MayHaveOutput, "unavailable protected access fails closed");
        check.That(!File.Exists(refusedOutput), "unavailable access writes nothing");
        check.That(lab.ReopenCopy.Disabled, "a failed operation cannot offer a verified result");
        files.Available = true;

        // The session independently rejects inconsistent receipts without claiming publication was undone.
        PublicationReceipt noBytes = session.VerifyPublication(new PublicationReceipt(true, "", refusedOutput), original);
        check.That(!noBytes.Ok && noBytes.MayHaveOutput, "missing returned bytes retain publication uncertainty");
        PublicationReceipt unverifiedSource = session.VerifyPublication(new PublicationReceipt(true, "", refusedOutput,
            Sha256: SaveSession.Digest(original), Size: original.Length, Bytes: original, OriginalVerified: false, Verified: true), original);
        check.That(!unverifiedSource.Ok && unverifiedSource.MayHaveOutput, "missing source verification cannot become success");
        PublicationReceipt wrongBytes = session.VerifyPublication(new PublicationReceipt(true, "", refusedOutput,
            Sha256: SaveSession.Digest(changed), Size: changed.Length, Bytes: changed, OriginalVerified: true, Verified: true), original);
        check.That(!wrongBytes.Ok && wrongBytes.MayHaveOutput, "returned bytes that differ from the plan cannot become success");

        // Opening the verified result makes it the new original only when explicitly requested.
        Outcome<SaveSession> reopenedResult = await app.OpenCareerAsync(recovery);
        check.That(reopenedResult.Ok && app.Workspace.Session?.Path == recovery, "an explicitly opened copy becomes the source");
        await Frame(tree);
    }

    private static async Task UnavailableWorker(string outputDirectory, byte[] original, Checks check)
    {
        SaveFileWorker worker = new(files: null);
        string input = Path.Combine(outputDirectory, "recovery.bes");
        string output = Path.Combine(outputDirectory, "unavailable-worker.bes");
        ProtectedRead read = await worker.OpenCareerAsync(input);
        PublicationReceipt write = await worker.PublishCopyAsync(input, "identity", SaveSession.Digest(original), output, original);
        check.That(!worker.IsAvailable && !read.Ok && read.Bytes is null && !write.Ok && !write.MayHaveOutput,
            "a worker without protected access refuses every operation");
        check.That(!File.Exists(output), "a worker without protected access writes nothing");
    }

    private static SignalAwaiter Frame(SceneTree tree) => tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
}

/// <summary>Test access that can become unavailable mid-session, as a missing platform capability would.</summary>
internal sealed class SwitchableSaveFiles(IProtectedSaveFiles inner) : IProtectedSaveFiles
{
    internal bool Available { get; set; } = true;

    public ProtectedRead OpenCareer(string input) =>
        Available ? inner.OpenCareer(input) : new ProtectedRead(false, SaveFileWorker.UnavailableMessage);

    public PublicationReceipt PublishCopy(string input, string identity, string sha256, string output, byte[] prepared) =>
        Available ? inner.PublishCopy(input, identity, sha256, output, prepared) : new PublicationReceipt(false, SaveFileWorker.UnavailableMessage);
}
