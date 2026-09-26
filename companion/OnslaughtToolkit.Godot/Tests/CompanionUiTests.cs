// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Lore;
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
        List<string> openedUrls = [];
        CompanionEnvironment environment = new([install.SteamRoot], Path.Combine(outputDirectory, "ui-settings", "settings.json"),
            OpenUrl: openedUrls.Add);
        CompanionApp app = new(files, managesWindow: false, environment);
        tree.Root.AddChild(app);
        await Frame(tree);
        for (int frame = 0; frame < 600 && (app.Game.Busy || app.Game.Folder is null); frame++) await Frame(tree);
        try
        {
            await Drive(app, files, tree, install, fixture, outputDirectory, original, check);
            await DriveLore(app, tree, openedUrls, check);
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
        check.That(app.Goodies.Cells.Count == 233 && app.Goodies.Selected == 0 && app.Overview.Missions.Columns == 4,
            "the gallery has a cell for each slot of the game's table, and the overview has no attempts column");
        app.Goodies.Cells[72].EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Goodies.DetailEvidence.StartsWith("The game's gallery has no cell", StringComparison.Ordinal) &&
            app.Goodies.ChangeInCopy.Disabled, "Goodie 072, which the gallery never shows, says so and cannot be changed");
        app.Goodies.Cells[2].EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Goodies.Selected == 2 && app.Goodies.DetailEvidence.StartsWith("Seen in the game") &&
            app.Goodies.DetailRule.Contains("Goodie 001"), "Goodie 2 shows its rule and its in-game evidence");
        app.Goodies.Cells[150].EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Goodies.DetailEvidence.StartsWith("From the developers' source"), "an unchecked rule says it comes from the source only");
        check.That(app.Goodies.Cells.Count(cell => cell.ButtonPressed) == 1 && app.Goodies.Cells[150].ButtonPressed,
            "exactly one Goodie cell shows as selected");
        check.That(File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original), "opening a game career changes nothing");
        check.That(app.StoredValues.Tree.GetRoot()?.GetChildren().Count(row => row.GetText(0).Contains("god flag")) == 2,
            "stored values shows both players' god flags");

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

        // A Goodie chosen in the gallery arrives on Edit a copy and changes only its own four bytes.
        app.Navigate("goodies");
        app.Goodies.Cells[2].EmitSignal(BaseButton.SignalName.Pressed);
        app.Goodies.ChangeInCopy.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Current == app.EditCopy && lab.GoodieTargets.ContainsKey(2) && lab.GoodiePickers.Count == 1,
            "a Goodie chosen in the gallery is added to Edit a copy");
        GoodieState before = app.Workspace.Session!.Analysis.Goodies[2].State;
        GoodieState target = before == GoodieState.Hint ? GoodieState.Locked : GoodieState.Hint;
        lab.GoodiePickers[0].Select(target == GoodieState.Hint ? 1 : 0);
        lab.GoodiePickers[0].EmitSignal(OptionButton.SignalName.ItemSelected, target == GoodieState.Hint ? 1 : 0);
        check.That(lab.GoodieTargets[2] == target && lab.Preview.GetParsedText().Contains("Goodie 002"), "the picker sets the target and the preview names it");
        string goodieCopy = Path.Combine(outputDirectory, "goodie-edit.bes");
        lab.Destination.Text = goodieCopy;
        PublicationReceipt goodieWritten = await lab.WriteCopyAsync(unchanged: false);
        byte[] goodieBytes = File.Exists(goodieCopy) ? File.ReadAllBytes(goodieCopy) : [];
        bool onlyGoodie = goodieBytes.Length == original.Length;
        for (int offset = 0; onlyGoodie && offset < original.Length; offset++)
            if (goodieBytes[offset] != original[offset] && offset is < 0x1F4E or > 0x1F51) onlyGoodie = false;
        check.That(goodieWritten.Ok && onlyGoodie && BinaryPrimitives.ReadUInt32LittleEndian(goodieBytes.AsSpan(0x1F4E)) ==
            (target == GoodieState.Hint ? 1u : 0u), "the Goodie copy changes only Goodie 002's dword, to the chosen state");

        // Install & backups: a verified backup set, then the last verified copy added to the game after confirmation.
        app.Navigate("install");
        InstallPage installPage = app.Install;
        string backupRoot = Path.Combine(outputDirectory, "ui-backups");
        Directory.CreateDirectory(backupRoot);
        installPage.SetBackupFolder(backupRoot);
        BackupReceipt backedUp = await installPage.BackUpAsync();
        check.That(backedUp.Ok && Backups.List(backupRoot).Count == 1 && installPage.RestoreButtons.Count == 2,
            "a backup set of the game's career and options file is made and listed with restore actions");
        check.That(app.Game.Settings.Load().BackupFolder == backupRoot, "the backup folder is remembered");
        installPage.UseLastCopy.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(installPage.Source.Text == goodieCopy, "the last verified copy can be chosen for installing");
        int newItem = Enumerable.Range(0, installPage.Target.ItemCount).First(item => installPage.Target.GetItemText(item) == "A new career…");
        installPage.Target.Select(newItem);
        installPage.Target.EmitSignal(OptionButton.SignalName.ItemSelected, newItem);
        installPage.NewName.Text = "Installed Career";
        installPage.NewName.EmitSignal(LineEdit.SignalName.TextChanged, installPage.NewName.Text);
        check.That(!installPage.Install.Disabled, "a named new career can be installed");
        installPage.AskToInstall();
        check.That(installPage.Confirm.Visible && installPage.Confirm.DialogText.Contains("Installed Career.bes") &&
            installPage.Confirm.DialogText.Contains(backupRoot), "the confirmation names the exact target and backup folder");
        string installed = Path.Combine(install.Game, "savegames", "Installed Career.bes");
        check.That(!File.Exists(installed), "nothing is written before the confirmation");
        InstallReceipt installedReceipt = await installPage.ConfirmAsync();
        check.That(installedReceipt.Ok && File.ReadAllBytes(installed).AsSpan().SequenceEqual(goodieBytes) && Backups.List(backupRoot).Count == 2,
            "the confirmed copy is backed up around, written into savegames and verified");
        check.That(app.Game.Folder?.Careers.Any(career => career.Name == "Installed Career.bes") == true && app.Home.OpenButtons.Count == 2,
            "Home lists the installed career after the write");

        // Cheat names: a byte-identical copy whose name carries a code seen working in the game.
        app.Navigate("cheats");
        CheatsPage cheats = app.Cheats;
        check.That(cheats.Choices.Count == 3, "only the three cheats seen working in the Steam game are offered");
        check.That(cheats.WriteCopy.Disabled, "no cheat chosen means no copy");
        cheats.BaseName.Text = "Pilot";
        cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "Pilot");
        cheats.Choices[0].ButtonPressed = true;
        check.That(cheats.Composed.FileName == "PilotMALLOY.bes" && !cheats.WriteCopy.Disabled && !cheats.AddToGame.Disabled,
            "choosing All goodies names the copy PilotMALLOY.bes");
        cheats.BaseName.Text = "Bad:Name";
        cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "Bad:Name");
        check.That(cheats.WriteCopy.Disabled && cheats.AddToGame.Disabled, "a name the game cannot use under Windows rules is refused");
        cheats.BaseName.Text = "Pilot";
        cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "Pilot");
        string cheatFolder = Path.Combine(outputDirectory, "cheat-copies");
        Directory.CreateDirectory(cheatFolder);
        PublicationReceipt cheatCopy = await cheats.WriteCopyAsync(cheatFolder);
        byte[] sourceBytes = app.Workspace.Session!.CopyBytes();
        check.That(cheatCopy.Ok && File.ReadAllBytes(Path.Combine(cheatFolder, "PilotMALLOY.bes")).AsSpan().SequenceEqual(sourceBytes),
            "the cheat copy is byte-identical to the open career");
        cheats.AskToAdd();
        check.That(cheats.Confirm.Visible && cheats.Confirm.DialogText.Contains("PilotMALLOY.bes"), "adding to the game asks first, naming the file");
        InstallReceipt cheatInstall = await cheats.ConfirmAddAsync();
        check.That(cheatInstall.Ok && File.ReadAllBytes(Path.Combine(install.Game, "savegames", "PilotMALLOY.bes")).AsSpan().SequenceEqual(sourceBytes),
            "the confirmed cheat career is added to savegames after a verified backup");

        // Options: read the game's defaultoptions.bea, change music and one key, write a verified .bea, then install it.
        app.Navigate("options");
        OptionsPage optionsPage = app.Options;
        check.That(!optionsPage.OpenGameOptions.Disabled, "the game's options file can be opened");
        byte[] optionsBefore = File.ReadAllBytes(install.Options);
        Outcome<SaveSession> openedOptions = await optionsPage.OpenAsync(install.Options);
        check.That(openedOptions.Ok && optionsPage.Reading is not null && app.Workspace.Session?.Path != install.Options,
            "the options file opens read-only without replacing the open career");
        double newMusic = optionsPage.Music.Value > 50 ? 20 : 80;
        optionsPage.Music.Value = newMusic;
        optionsPage.StartCapture(0x21, 1);
        check.That(optionsPage.Capture(Key.T), "a captured key is accepted");
        check.That(optionsPage.PreviewText.Contains("Music volume") && optionsPage.PreviewText.Contains("transform → T"),
            "the preview names the music change and the new key");
        string optionsCopy = Path.Combine(outputDirectory, "options-copy.bea");
        optionsPage.Destination.Text = optionsCopy;
        PublicationReceipt optionsWritten = await optionsPage.WriteCopyAsync();
        byte[] optionsBytes = File.Exists(optionsCopy) ? File.ReadAllBytes(optionsCopy) : [];
        int transformRow = optionsPage.Reading!.Bindings.Single(row => row.EntryId == 0x21).Offset;
        bool optionsConfined = optionsBytes.Length == optionsBefore.Length;
        for (int offset = 0; optionsConfined && offset < optionsBefore.Length; offset++)
        {
            bool allowed = offset is >= 0x2492 and < 0x2496 || (offset >= transformRow + 0x18 && offset < transformRow + 0x20);
            if (!allowed && optionsBytes[offset] != optionsBefore[offset]) optionsConfined = false;
        }
        check.That(optionsWritten.Ok && optionsConfined && Math.Abs(BinaryPrimitives.ReadSingleLittleEndian(optionsBytes.AsSpan(0x2492)) -
            (float)(newMusic / 100)) < 1e-6, "the options copy changes only the music float and the chosen key's two dwords");
        optionsPage.AskToInstall();
        check.That(optionsPage.Confirm.Visible && File.ReadAllBytes(install.Options).AsSpan().SequenceEqual(optionsBefore),
            "installing the options asks first and writes nothing yet");
        InstallReceipt optionsInstalled = await optionsPage.ConfirmInstallAsync();
        check.That(optionsInstalled is { Ok: true, Replaced: true } && File.ReadAllBytes(install.Options).AsSpan().SequenceEqual(optionsBytes),
            "the confirmed options copy replaces defaultoptions.bea after a verified backup");

        // Music & voices lists the install's own audio; damaged files and Bink cutscenes are refused without the decoder.
        app.Navigate("music");
        check.That(app.Music.Items.Count == 3 && app.Music.List.GetRoot()?.GetChildCount() == 3, "music, voices and cutscenes are listed");
        check.That(!app.Music.Load(app.Music.Items.First(item => item.Kind == OnslaughtToolkit.Companion.Media.AudioKind.Music)) &&
            app.Music.PlayPause.Disabled, "a file without a Vorbis header is refused and cannot play");
        check.That(!app.Music.Load(app.Music.Items.First(item => !item.Playable)) && app.Music.Player.Stream is null,
            "a Bink cutscene is listed but not played");
        await Frame(tree);
    }

    private static async Task DriveLore(CompanionApp app, SceneTree tree, List<string> openedUrls, Checks check)
    {
        check.Suite("lore reader");
        app.Navigate("lore");
        LorePage lore = app.Lore;
        check.That(lore.Current?.Id == LoreLibrary.HomeId && lore.Reader.GetParsedText().Contains("Lost Toys") &&
            app.PageSubtitle.Text.StartsWith("Onslaught Lore", StringComparison.Ordinal), "Lore opens on the front door and names it in the header");
        check.That(lore.BackButton.Disabled && lore.ForwardButton.Disabled, "a fresh reading session has nowhere to go back to");
        lore.Follow("lore:characters");
        TreeItem? selected = lore.Library.GetSelected();
        check.That(lore.Current?.Id == "characters" && lore.Reader.GetParsedText().Contains("Kiralova") && !lore.BackButton.Disabled &&
            app.PageSubtitle.Text.StartsWith("The people in it", StringComparison.Ordinal), "a link opens another article and can be retraced");
        check.That(selected?.GetMetadata(0).AsString() == "characters" &&
            selected.GetChildCount() == lore.Rendered!.Headings.Count(heading => heading.Level == 2),
            "the open article is selected in the library with its sections beneath it");
        lore.Back();
        check.That(lore.Current?.Id == LoreLibrary.HomeId && !lore.ForwardButton.Disabled, "Back returns to the front door");
        lore.Forward();
        check.That(lore.Current?.Id == "characters", "Forward returns to the article");
        lore.Open("the-campaign");
        check.That(lore.Reader.GetParsedText().Contains("Choose your Battle Engine Aquila folder on Home") &&
            !lore.Reader.Text.Contains("LIVE:CAMPAIGN"), "without the game's text the campaign page says where to set the game folder");
        string page = LoreLibrary.Repository + "reverse-engineering/RE-INDEX.md";
        lore.Follow(page);
        check.That(openedUrls.SequenceEqual([page]) && lore.Current?.Id == "the-campaign", "a repository link opens in the browser; the reader stays put");
        lore.Search.Text = "Kiralova";
        lore.Search.EmitSignal(LineEdit.SignalName.TextChanged, "Kiralova");
        check.That(!lore.Library.Visible && lore.Results.GetParsedText().Contains("The people in it"), "search lists the articles that mention a phrase");
        lore.Results.EmitSignal(RichTextLabel.SignalName.MetaClicked, "hit:battle-engine-tech");
        check.That(lore.Current?.Id == "battle-engine-tech", "a search result opens its article");
        lore.Search.Text = "";
        lore.Search.EmitSignal(LineEdit.SignalName.TextChanged, "");
        check.That(lore.Library.Visible, "clearing the search shows the library again");
        lore.Open("community-preservation", "active-community-contacts");
        for (int frame = 0; frame < 3; frame++) await Frame(tree);
        check.That(lore.Reader.GetVScrollBar().Value > 0, "a link to a section scrolls the reader to it");
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
