// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Lore;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Drives the code-built interface and the in-process protected adapter, exclusively on the
/// runner-owned fixture copy, a game-shaped folder of owned copies, and fresh outputs.
/// </summary>
internal static class CompanionUiTests
{
    private sealed class Flag
    {
        internal bool On { get; set; }
    }

    internal static async Task RunAsync(SceneTree tree, string fixture, string outputDirectory, byte[] original, Checks check)
    {
        check.Suite("companion interface");
        SwitchableSaveFiles files = new(new ProtectedSaveFiles());
        FakeInstall install = FakeInstall.Create(Path.Combine(outputDirectory, "ui-install"), original);
        List<string> openedUrls = [];
        Flag running = new();
        string defaultBackups = Path.Combine(outputDirectory, "ui-backups");
        CompanionEnvironment environment = new([install.SteamRoot], Path.Combine(outputDirectory, "ui-settings", "settings.json"),
            GameRunning: () => running.On, OpenUrl: openedUrls.Add, DefaultBackupFolder: defaultBackups);
        CompanionApp app = new(files, managesWindow: false, environment);
        tree.Root.AddChild(app);
        await Frame(tree);
        for (int frame = 0; frame < 600 && (app.Game.Busy || app.Game.Folder is null || app.Workspace.Session is null); frame++)
            await Frame(tree);
        try
        {
            await Start(app, tree, install, check);
            await Edit(app, files, tree, install, fixture, outputDirectory, original, running, check);
            await CheatsAndSettings(app, tree, install, outputDirectory, check);
            await BackupsAndHome(app, tree, install, outputDirectory, original, defaultBackups, openedUrls, running, check);
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

    private static async Task Start(CompanionApp app, SceneTree tree, FakeInstall install, Checks check)
    {
        check.That(app.Game.Folder?.Root == install.Game && app.Home.OpenButtons.Count == 1,
            "Home finds the game through Steam and shows its career");
        check.That(app.Workspace.Session?.Path == install.Career && app.Current == app.Home && app.CareerMenu.Text == "Career One",
            "the most recent career opens by itself, read-only, without leaving Home");
        check.That(app.Status.Game.Text.Contains("changed BEA.exe"), "the status bar says the test executable is not the Steam release");
        check.That(app.Home.AskingAboutBackups, "Home asks once whether to keep automatic backups");
        check.That(app.Home.ShowsGameArt && app.Home.Manual.Visible, "Home shows the game's own art and offers its manual when the install has them");
        check.That(!app.Sidebar.IsOpen("Advanced") && app.Sidebar.Items.Count == app.Pages.Count,
            "every page has one sidebar item, and the Advanced tools start folded away");
        foreach (Page page in app.Pages.Values)
        {
            app.Navigate(page.Key);
            check.That(app.Current == page && page.Root.Visible && app.PageTitle.Text == page.Title.ToUpperInvariant() &&
                app.Pages.Values.Count(other => other.Root.Visible) == 1, "navigation shows exactly one page: " + page.Key);
        }
        check.That(app.Sidebar.IsOpen("Advanced"), "going to an Advanced page opens its group");
        // The window may be as short as its 700-pixel minimum: no page, with every sidebar group open, may need more.
        List<string> tall = [];
        foreach (Page page in app.Pages.Values)
        {
            app.Navigate(page.Key);
            for (int frame = 0; frame < 2; frame++) await Frame(tree);
            if (app.GetCombinedMinimumSize().Y > 700) tall.Add($"{page.Key} {app.GetCombinedMinimumSize().Y}");
        }
        check.That(tall.Count == 0, "every page fits the smallest window, 700 pixels tall, with the sidebar open" +
            (tall.Count > 0 ? ": too tall " + string.Join(", ", tall) : ""));
        app.Navigate("home");
        for (int frame = 0; frame < 3; frame++) await Frame(tree);
        check.That(app.Home.Promises.Count == 3 && app.Home.Promises.All(promise => promise.Size.X > 200 && promise.GetLineCount() <= 3),
            "Home's three promises read as lines of text, not a letter per line");
        for (int frame = 0; frame < 600 && app.Workspace.Busy; frame++) await Frame(tree);
        FileDialog[] dialogs = app.FindChildren("*", nameof(FileDialog), true, false).OfType<FileDialog>().ToArray();
        check.That(dialogs.Length >= 8 && dialogs.All(dialog => !dialog.DeletingEnabled && !dialog.FolderCreationEnabled &&
            dialog.Access == FileDialog.AccessEnum.Filesystem), "no file dialog can delete files or create folders");

        CareerInspection opened = app.Workspace.Session!.Analysis;
        check.That(app.Summary.MissionsSummary == $"{opened.MissionCensus.Completed} / {opened.MissionCensus.Used}" &&
            app.Summary.Missions.GetRoot()?.GetChildCount() == opened.MissionCensus.Used && app.Summary.Missions.Columns == 4,
            "the summary lists every used mission, with no attempts column");
        app.Navigate("summary");
        CampaignMap map = app.Summary.Map;
        CampaignNode? training = map.Graph?.Nodes.FirstOrDefault(node => node.World == 100);
        check.That(map.Graph?.Nodes.Count == opened.MissionCensus.Used && map.IsVisibleInTree() && training is not null &&
            map.Describe(training).StartsWith("1.00", StringComparison.Ordinal) && map.CustomMinimumSize.Y > 100,
            "the summary draws the career's path through the campaign, and a mission names itself");
        app.Navigate("goodies");
        check.That(app.Goodies.Cells.Count == 233, "the gallery has a cell for each slot of the game's table");
        app.Goodies.Cells[2].EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Goodies.Selected == 2 && app.Goodies.DetailEvidence.StartsWith("Seen in the game") &&
            app.Goodies.DetailRule.Contains("Goodie 001"), "Goodie 2 shows its rule and its in-game evidence");
        app.Goodies.Cells[150].EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Goodies.DetailEvidence.StartsWith("From the developers' source") &&
            app.Goodies.Cells.Count(cell => cell.ButtonPressed) == 1 && app.Goodies.Cells[150].ButtonPressed,
            "an unchecked rule says it comes from the source only, and exactly one cell is selected");
        app.Goodies.Cells[72].EmitSignal(BaseButton.SignalName.Pressed);
        check.That(app.Goodies.DetailEvidence.StartsWith("The game's gallery has no place", StringComparison.Ordinal) &&
            app.Goodies.ChangeInCopy.Disabled, "Goodie 072, which the gallery never shows, says so and cannot be changed");
        check.That(app.RawValues.Tree.GetRoot()?.GetChildren().Count(row => row.GetText(0).Contains("god flag")) == 2,
            "raw values show both players' god flags");
    }

    private static async Task Edit(CompanionApp app, SwitchableSaveFiles files, SceneTree tree, FakeInstall install, string fixture,
        string outputDirectory, byte[] original, Flag running, Checks check)
    {
        check.Suite("edit career");
        EditCareerPage edit = app.EditCareer;
        app.Navigate("edit");
        check.That(edit.Save.Disabled && edit.ChangesText.StartsWith("No changes yet"), "nothing can be saved before a change");
        byte[] leaked = app.Workspace.Session!.CopyBytes();
        leaked[12] ^= 1;
        check.That(app.Workspace.Session.Matches(original), "the open career's bytes are not exposed for mutation");

        // An unchanged recovery copy round-trips every byte.
        string recovery = Path.Combine(outputDirectory, "recovery.bes");
        PublicationReceipt copy = await app.Workspace.PublishAsync(recovery, app.Workspace.Session.CopyBytes());
        check.That(copy.Ok && File.ReadAllBytes(recovery).AsSpan().SequenceEqual(original), "a copy round-trips every byte and is read back");

        edit.Rows[0].Target.Value = 123456;
        edit.Rows[4].Target.Value = 123460;
        app._UnhandledKeyInput(new InputEventKey { Keycode = Key.S, CtrlPressed = true, Pressed = true });
        check.That(edit.SaveChoice.Dialog.Visible, "Ctrl+S on Edit career opens the save choice");
        edit.SaveChoice.Name.Text = "Bad:Name";
        edit.SaveChoice.Name.EmitSignal(LineEdit.SignalName.TextChanged, "Bad:Name");
        edit.SaveChoice.Name.EmitSignal(LineEdit.SignalName.TextSubmitted, "Bad:Name");
        check.That(edit.SaveChoice.Dialog.Visible && edit.SaveChoice.Dialog.GetOkButton().Disabled,
            "Enter in the name field does not save a name the game cannot use");
        edit.SaveChoice.Dialog.Hide();
        check.That(edit.Plan.Ok && !edit.Save.Disabled && edit.ChangesText.Contains("Aircraft kills: 3,221 → 123,456"),
            "a changed count is listed in the player's words and can be saved");
        check.That(edit.Bar.Root.Visible && edit.Bar.Summary.Text.StartsWith("2 changes not saved yet", StringComparison.Ordinal) &&
            !edit.Bar.Save.Disabled, "a bar under the page counts the unsaved changes and offers Save");
        edit.AskToSave();
        for (int frame = 0; frame < 4; frame++) await Frame(tree);
        check.That(edit.SaveChoice.Dialog.Size.Y is > 200 and < 640 && edit.SaveChoice.Dialog.GetOkButton().ThemeTypeVariation == "Primary",
            $"the save dialog fits its content, well inside the window ({edit.SaveChoice.Dialog.Size.Y} px tall), with its action in amber");
        check.That(edit.SaveChoice.Dialog.Visible && edit.SaveChoice.Offers(SaveTarget.NewCareer) && edit.SaveChoice.Offers(SaveTarget.Replace) &&
            edit.SaveChoice.Offers(SaveTarget.Elsewhere) && edit.SaveChoice.Name.Text == "Career One (edited)" && edit.SaveChoice.InGameAvailable,
            "saving offers a new career, replacing this one, or a copy elsewhere, with a sensible new name");
        edit.SaveChoice.Dialog.Hide();

        string edited = Path.Combine(outputDirectory, "edited.bes");
        PublicationReceipt written = await edit.SaveElsewhereAsync(edited);
        byte[] actual = File.Exists(edited) ? File.ReadAllBytes(edited) : [];
        bool confined = written.Ok && actual.Length == original.Length;
        for (int offset = 0; confined && offset < original.Length; offset++)
        {
            // Independent literal layout, not a call to the codec under test.
            bool allowed = offset is >= 0x23F6 and < 0x23F9 or >= 0x2406 and < 0x2409;
            if (!allowed && actual[offset] != original[offset]) confined = false;
        }
        check.That(confined && (BinaryPrimitives.ReadUInt32LittleEndian(actual.AsSpan(0x23F6)) & 0xFFFFFF) == 123456 &&
            (BinaryPrimitives.ReadUInt32LittleEndian(actual.AsSpan(0x2406)) & 0xFFFFFF) == 123460,
            "a copy elsewhere changes only the chosen counts' low three bytes");
        check.That(File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original), "saving elsewhere leaves the game's career unchanged");
        check.That(!edit.HasChanges && !edit.Bar.Root.Visible && edit.ResultPanel.Visible && edit.Result.Text.StartsWith("Saved a copy"),
            "saved changes are done: the page starts again from the career and the result stays in view");
        edit.Rows[0].Target.Value = 123456;
        edit.Rows[4].Target.Value = 123460;
        PublicationReceipt duplicate = await edit.SaveElsewhereAsync(edited);
        check.That(!duplicate.Ok && File.ReadAllBytes(edited).AsSpan().SequenceEqual(actual), "an existing file is never replaced");

        byte[] plan = edit.Plan.Value!.CopyBytes();
        InstallReceipt added = await edit.SaveIntoGameAsync(SaveTarget.NewCareer, "Career One (edited)");
        string addedPath = Path.Combine(install.Game, "savegames", "Career One (edited).bes");
        IReadOnlyList<BackupSet> sets = Backups.List(app.Services.Backups.Folder);
        check.That(added.Ok && File.ReadAllBytes(addedPath).AsSpan().SequenceEqual(plan) && sets.Count == 1 &&
            sets[0].Reason == "Before adding Career One (edited)" && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original),
            "a new career is added to the game after a backup made for it; the open career is unchanged");
        check.That(app.Game.Folder?.Careers.Count == 2 && app.Home.OpenButtons.Count == 2, "Home lists the new career");
        edit.Rows[0].Target.Value = 123456;
        edit.Rows[4].Target.Value = 123460;

        InstallReceipt replaced = await edit.SaveIntoGameAsync(SaveTarget.Replace, "");
        IReadOnlyList<BackupSet> after = Backups.List(app.Services.Backups.Folder);
        check.That(replaced.Ok && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(plan) && after.Count == 2 &&
            File.ReadAllBytes(Path.Combine(after[0].Folder, "Career One.bes")).AsSpan().SequenceEqual(original),
            "replacing the career in the game backs up its earlier version first");
        check.That(app.Workspace.Session?.Path == install.Career && app.Workspace.Session.Matches(plan) && edit.ResultPanel.Visible &&
            edit.Result.Text.StartsWith("Saved."), "after replacing, the career reopens with the change and says it was saved");

        // The game saved the career after it was opened: replacing it now would lose that, so it is refused.
        edit.Rows[3].Target.Value = 999;
        byte[] gameSaved = plan.ToArray();
        gameSaved[^1] ^= 1;
        File.WriteAllBytes(install.Career, gameSaved);
        InstallReceipt stale = await edit.SaveIntoGameAsync(SaveTarget.Replace, "");
        check.That(!stale.Ok && stale.Message.Contains("changed since you opened it") &&
            File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(gameSaved), "a career the game saved since it was opened is not replaced");
        await app.OpenCareerAsync(install.Career);

        running.On = true;
        app.CheckRunning();
        edit.Rows[3].Target.Value = 999;
        edit.AskToSave();
        bool offered = edit.SaveChoice.InGameAvailable;
        edit.SaveChoice.Dialog.Hide();
        InstallReceipt blocked = await edit.SaveIntoGameAsync(SaveTarget.NewCareer, "Blocked");
        check.That(!offered && !blocked.Ok && blocked.Message.Contains("running") && app.RunningBadge.Visible &&
            !File.Exists(Path.Combine(install.Game, "savegames", "Blocked.bes")), "nothing is written into the game while it runs");
        running.On = false;
        app.CheckRunning();

        // The open career changed on disk: a copy made from it is refused.
        byte[] changedSource = File.ReadAllBytes(install.Career);
        changedSource[^2] ^= 1;
        File.WriteAllBytes(install.Career, changedSource);
        string refusedOutput = Path.Combine(outputDirectory, "source-changed.bes");
        PublicationReceipt sourceChanged = await edit.SaveElsewhereAsync(refusedOutput);
        check.That(!sourceChanged.Ok && !File.Exists(refusedOutput), "a copy is refused when the open career changed on disk");
        changedSource[^2] ^= 1;
        File.WriteAllBytes(install.Career, changedSource);

        files.Available = false;
        PublicationReceipt unavailable = await edit.SaveElsewhereAsync(refusedOutput);
        check.That(!unavailable.Ok && !unavailable.MayHaveOutput && !File.Exists(refusedOutput), "unavailable protected access fails closed");
        files.Available = true;

        SaveSession session = app.Workspace.Session!;
        byte[] sessionBytes = session.CopyBytes();
        PublicationReceipt noBytes = session.VerifyPublication(new PublicationReceipt(true, "", refusedOutput), sessionBytes);
        check.That(!noBytes.Ok && noBytes.MayHaveOutput, "missing returned bytes keep publication uncertain");
        PublicationReceipt unverified = session.VerifyPublication(new PublicationReceipt(true, "", refusedOutput,
            Sha256: SaveSession.Digest(sessionBytes), Size: sessionBytes.Length, Bytes: sessionBytes, OriginalVerified: false, Verified: true), sessionBytes);
        check.That(!unverified.Ok && unverified.MayHaveOutput, "missing source verification cannot become success");

        byte[] malformed = original.ToArray();
        malformed[0] ^= 1;
        string malformedPath = Path.Combine(outputDirectory, "malformed.bes");
        File.WriteAllBytes(malformedPath, malformed);
        Outcome<SaveSession> refused = await app.OpenCareerAsync(malformedPath);
        check.That(!refused.Ok && app.Workspace.Session?.Path == install.Career, "a malformed file is refused and the open career stays");
        Outcome<SaveSession> fromElsewhere = await app.OpenCareerAsync(fixture);
        check.That(fromElsewhere.Ok && app.CareerMenu.Text == Path.GetFileNameWithoutExtension(fixture), "a career file elsewhere opens read-only");
        edit.Rows[1].Target.Value = 7;
        edit.AskToSave();
        check.That(!edit.SaveChoice.Offers(SaveTarget.Replace) && edit.SaveChoice.Offers(SaveTarget.NewCareer),
            "a career file outside the game can be added to it but not 'replaced' there");
        edit.SaveChoice.Dialog.Hide();
        await app.OpenCareerAsync(install.Career);

        // A Goodie chosen in the gallery arrives on Edit career and changes only its own four bytes.
        app.Navigate("goodies");
        app.Goodies.Cells[2].EmitSignal(BaseButton.SignalName.Pressed);
        app.Goodies.ChangeInCopy.EmitSignal(BaseButton.SignalName.Pressed);
        GoodieState before = app.Workspace.Session!.Analysis.Goodies[2].State;
        check.That(app.Current == app.EditCareer && edit.GoodieTargets.ContainsKey(2) && edit.GoodiePickers.Count == 1,
            "a Goodie chosen in the gallery is added to Edit career");
        GoodieState target = before == GoodieState.Hint ? GoodieState.Locked : GoodieState.Hint;
        int item = target == GoodieState.Hint ? 1 : 0;
        edit.GoodiePickers[0].Select(item);
        edit.GoodiePickers[0].EmitSignal(OptionButton.SignalName.ItemSelected, item);
        byte[] baseline = app.Workspace.Session.CopyBytes();
        string goodieCopy = Path.Combine(outputDirectory, "goodie-edit.bes");
        PublicationReceipt goodieWritten = await edit.SaveElsewhereAsync(goodieCopy);
        byte[] goodieBytes = File.Exists(goodieCopy) ? File.ReadAllBytes(goodieCopy) : [];
        bool onlyGoodie = goodieBytes.Length == baseline.Length;
        for (int offset = 0; onlyGoodie && offset < baseline.Length; offset++)
            if (goodieBytes[offset] != baseline[offset] && offset is < 0x1F4E or > 0x1F51) onlyGoodie = false;
        check.That(goodieWritten.Ok && onlyGoodie && BinaryPrimitives.ReadUInt32LittleEndian(goodieBytes.AsSpan(0x1F4E)) ==
            (target == GoodieState.Hint ? 1u : 0u), "the Goodie copy changes only Goodie 002's four bytes, to the chosen state");

        edit.Bar.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(!edit.Bar.Root.Visible && !edit.HasChanges, "Undo on the bar clears every change and hides the bar");
        edit.UnlockEveryGoodie();
        int locked = app.Workspace.Session.Analysis.Goodies.Count(goodie => goodie.Shown && goodie.State is GoodieState.Locked or GoodieState.Hint);
        check.That(edit.GoodieTargets.Count == locked && locked > 0 && edit.ChangesText.Contains("unlocked (new)"),
            "Unlock every Goodie targets exactly the shown Goodies that are locked");
        edit.UndoAll.EmitSignal(BaseButton.SignalName.Pressed);
        await Frame(tree);
    }

    private static async Task CheatsAndSettings(CompanionApp app, SceneTree tree, FakeInstall install, string outputDirectory, Checks check)
    {
        check.Suite("cheats and settings");
        app.Navigate("cheats");
        CheatsPage cheats = app.Cheats;
        check.That(cheats.Choices.Count == 3 && cheats.AddToGame.Disabled, "only the three cheats seen working are offered, and none is chosen");
        cheats.BaseName.Text = "Pilot";
        cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "Pilot");
        cheats.Choices[0].ButtonPressed = true;
        check.That(cheats.Composed.FileName == "PilotMALLOY.bes" && !cheats.WriteCopy.Disabled && !cheats.AddToGame.Disabled,
            "choosing All goodies names the new career PilotMALLOY");
        cheats.BaseName.Text = "Bad:Name";
        cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "Bad:Name");
        check.That(cheats.WriteCopy.Disabled && cheats.AddToGame.Disabled, "a name Windows cannot use is refused");
        cheats.BaseName.Text = "Pilot";
        cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "Pilot");
        string cheatFolder = Path.Combine(outputDirectory, "cheat-copies");
        Directory.CreateDirectory(cheatFolder);
        PublicationReceipt cheatCopy = await cheats.WriteCopyAsync(cheatFolder);
        byte[] sourceBytes = app.Workspace.Session!.CopyBytes();
        check.That(cheatCopy.Ok && File.ReadAllBytes(Path.Combine(cheatFolder, "PilotMALLOY.bes")).AsSpan().SequenceEqual(sourceBytes),
            "the cheat copy is byte-identical to the open career");
        cheats.AskToAdd();
        check.That(cheats.Confirm.Visible && cheats.Confirm.DialogText.Contains("PilotMALLOY"), "adding to the game asks first, naming the career");
        InstallReceipt cheatInstall = await cheats.ConfirmAddAsync();
        check.That(cheatInstall.Ok && File.ReadAllBytes(Path.Combine(install.Game, "savegames", "PilotMALLOY.bes")).AsSpan().SequenceEqual(sourceBytes),
            "the cheat career is added to the game after a backup");
        check.That(cheats.AddToGame.Disabled && cheats.Switches.Contains("already has a career called PilotMALLOY"),
            "a name already in the game cannot be added twice");

        app.Navigate("settings");
        SettingsPage settings = app.Settings;
        for (int frame = 0; frame < 600 && (settings.Reading is null || app.Workspace.Busy); frame++) await Frame(tree);
        check.That(settings.Opened?.Path == install.Options && settings.Source.ItemCount == (app.Game.Folder?.Careers.Count ?? 0) + 1,
            "Settings opens the game's defaults and lists every career's settings too");
        byte[] optionsBefore = File.ReadAllBytes(install.Options);
        double newMusic = settings.Music.Value > 50 ? 20 : 80;
        settings.Music.Value = newMusic;
        settings.StartCapture(0x21, 1);
        check.That(settings.Capture(Key.T), "a captured key is accepted");
        check.That(settings.PreviewText.Contains("Music volume") && settings.PreviewText.Contains("transform → T"),
            "the changes name the music volume and the new key");
        check.That(settings.Bar.Root.Visible && settings.Bar.Summary.Text.StartsWith("2 changes", StringComparison.Ordinal),
            "the settings page's bar counts its unsaved changes");
        string optionsCopy = Path.Combine(outputDirectory, "options-copy.bea");
        PublicationReceipt optionsWritten = await settings.SaveElsewhereAsync(optionsCopy);
        byte[] optionsBytes = File.Exists(optionsCopy) ? File.ReadAllBytes(optionsCopy) : [];
        int transformRow = settings.Reading!.Bindings.Single(row => row.EntryId == 0x21).Offset;
        bool optionsConfined = optionsBytes.Length == optionsBefore.Length;
        for (int offset = 0; optionsConfined && offset < optionsBefore.Length; offset++)
        {
            bool allowed = offset is >= 0x2492 and < 0x2496 || (offset >= transformRow + 0x18 && offset < transformRow + 0x20);
            if (!allowed && optionsBytes[offset] != optionsBefore[offset]) optionsConfined = false;
        }
        check.That(optionsWritten.Ok && optionsConfined && Math.Abs(BinaryPrimitives.ReadSingleLittleEndian(optionsBytes.AsSpan(0x2492)) -
            (float)(newMusic / 100)) < 1e-6, "a settings copy changes only the music float and the chosen key's two dwords");
        check.That(!settings.HasChanges && settings.ResultText.StartsWith("Saved a copy", StringComparison.Ordinal),
            "after a settings copy is saved the page starts again from the file, the result still shown");
        settings.Music.Value = newMusic;
        settings.StartCapture(0x21, 1);
        settings.Capture(Key.T);
        settings.AskToSave();
        check.That(settings.SaveChoice.Dialog.Visible && settings.SaveChoice.Offers(SaveTarget.Replace) &&
            !settings.SaveChoice.Offers(SaveTarget.NewCareer), "saving settings offers to replace them in the game, or a copy");
        settings.SaveChoice.Dialog.Hide();
        InstallReceipt optionsInstalled = await settings.SaveIntoGameAsync();
        check.That(optionsInstalled is { Ok: true, Replaced: true } && File.ReadAllBytes(install.Options).AsSpan().SequenceEqual(optionsBytes) &&
            settings.Opened?.Matches(optionsBytes) == true, "the game's default settings are replaced after a backup and reopened");
        int careerSource = 1;
        settings.Source.Select(careerSource);
        settings.Source.EmitSignal(OptionButton.SignalName.ItemSelected, careerSource);
        for (int frame = 0; frame < 600 && (app.Workspace.Busy || settings.Opened?.Path == install.Options); frame++) await Frame(tree);
        check.That(settings.Opened?.Path.EndsWith(".bes", StringComparison.Ordinal) == true, "a career's own settings can be chosen and opened");
    }

    private static async Task BackupsAndHome(CompanionApp app, SceneTree tree, FakeInstall install, string outputDirectory, byte[] original,
        string defaultBackups, List<string> openedUrls, Flag running, Checks check)
    {
        check.Suite("backups and home");
        app.Navigate("backups");
        BackupsPage backups = app.Backups;
        check.That(app.Services.Backups.Folder == defaultBackups && backups.RestoreButtons.Count > 0,
            "backups go to the default folder and every backed-up file can be put back");
        backups.Automatic.ButtonPressed = true;
        check.That(app.Game.Settings.Load().AutoBackup == true, "automatic backups can be turned on");
        BackupReceipt made = await backups.BackUpAsync();
        check.That(made is { Ok: true, Set.Reason: "Backed up by you" }, "a backup made by hand says so");
        BackupReceipt again = await app.Workspace.AutoBackUpAsync(app.Game.Folder!, defaultBackups);
        check.That(again is { Ok: true, Set: null }, "an automatic backup is skipped when nothing changed since the last one");

        BackupSet oldest = Backups.List(defaultBackups)[^1];
        BackupFile first = oldest.Files.Single(file => file.Name == "Career One.bes");
        backups.AskToRestore(oldest, first);
        check.That(backups.Confirm.Visible && backups.Confirm.DialogText.Contains("Career One"), "putting a file back asks first");
        InstallReceipt restored = await backups.ConfirmAsync();
        check.That(restored.Ok && File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original) &&
            Backups.List(defaultBackups)[0].Reason!.StartsWith("Before putting back", StringComparison.Ordinal),
            "a backed-up career is put back, after a backup of what it replaced");
        check.That(app.Workspace.Session?.Path == install.Career && app.Workspace.Session.Matches(original),
            "the open career follows a file put back from a backup");

        // Playing while the companion is open: when the game closes, what it saved is backed up and shown.
        running.On = true;
        app.CheckRunning();
        byte[] played = original.ToArray();
        played[0x23F6] ^= 0x01;
        File.WriteAllBytes(install.Career, played);
        File.SetLastWriteTime(install.Career, DateTime.Now.AddMinutes(1));
        string settingsPath = app.Settings.Opened!.Path;
        byte[] settingsPlayed = File.ReadAllBytes(settingsPath);
        settingsPlayed[0x2492] ^= 0x01;
        File.WriteAllBytes(settingsPath, settingsPlayed);
        running.On = false;
        app.CheckRunning();
        await app.PendingCatchUp;
        BackupSet latest = Backups.List(defaultBackups)[0];
        check.That(app.Workspace.Session?.Matches(played) == true && app.Settings.Opened?.Matches(settingsPlayed) == true &&
            latest.Reason == "Automatic backup" && latest.Files.Single(file => file.Name == "Career One.bes").Sha256 == SaveSession.Digest(played),
            "when the game closes, the companion backs up what it saved and shows the latest career and settings");
        app.EditCareer.Rows[2].Target.Value = app.EditCareer.Rows[2].Target.Value + 1;
        File.WriteAllBytes(install.Career, original);
        File.SetLastWriteTime(install.Career, DateTime.Now.AddMinutes(2));
        app.CheckRunning(catchUp: true);
        await app.PendingCatchUp;
        check.That(app.Workspace.Session?.Matches(played) == true && app.EditCareer.HasChanges && app.Status.Label.Text.Contains("Undo your changes"),
            "unsaved changes are never thrown away to show what the game saved; the player is told instead");
        app.EditCareer.UndoAll.EmitSignal(BaseButton.SignalName.Pressed);
        await app.OpenCareerAsync(install.Career);
        app.Navigate("home");
        HomePage home = app.Home;
        check.That(!home.AskingAboutBackups && home.HeroStatus.Contains("last backed up"), "Home shows the safety net once it is set up");
        string shared = Path.Combine(outputDirectory, "shared-career.bes");
        File.WriteAllBytes(shared, original);
        home.AskToAdd(shared);
        check.That(home.AddChoice.Dialog.Visible && home.AddChoice.Offers(SaveTarget.NewCareer) && !home.AddChoice.Offers(SaveTarget.Elsewhere) &&
            home.AddChoice.Name.Text == "shared-career", "adding a career file asks for its name in the game");
        home.AddChoice.Dialog.Hide();
        InstallReceipt sharedAdded = await home.AddCareerAsync("Shared Career");
        check.That(sharedAdded.Ok && File.ReadAllBytes(Path.Combine(install.Game, "savegames", "Shared Career.bes")).AsSpan().SequenceEqual(original),
            "a career file is added to the game under the chosen name, after a backup");
        check.That(home.Play.Visible, "Play is offered for a Steam install");
        home.Play.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(openedUrls.Contains($"steam://rungameid/{SteamLibraries.AppId}"), "Play asks Steam to start the game");
        string otherFolder = Path.Combine(outputDirectory, "ui-backups-chosen");
        Directory.CreateDirectory(otherFolder);
        app.Backups.SetBackupFolder(otherFolder);
        check.That(app.Services.Backups.Folder == otherFolder && !app.Services.Backups.IsDefault, "another backup folder can be chosen and is remembered");

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
        check.That(openedUrls.Contains(page) && lore.Current?.Id == "the-campaign", "a repository link opens in the browser; the reader stays put");
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
        lore.Open(LorePage.MapId);
        check.That(lore.ShowingMap && lore.Map.Visible && lore.Map.Texture is not null && !lore.Reader.Visible &&
            app.PageSubtitle.Text.Contains("map of Allium"), "the map from the game's manual opens in the reader");
        lore.Back();
        check.That(!lore.ShowingMap && lore.Current?.Id == "community-preservation" && lore.Reader.Visible,
            "Back returns from the map to the article");
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
