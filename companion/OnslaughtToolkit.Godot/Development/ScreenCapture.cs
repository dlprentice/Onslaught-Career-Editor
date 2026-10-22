// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Tests;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Renders every companion screen at fixed sizes through SubViewports, so a tiling window
/// manager cannot resize the capture. Run on a GPU output (godot-offscreen):
/// <c>--script res://Development/ScreenCapture.cs -- --output=DIR --fixture=OWNED_COPY [--sizes=1280x800,1920x1080] [--steam-root=DIR]</c>.
/// Every file it writes stays inside the owned output directory; a real Steam library is only read,
/// and no game write is confirmed against it. Development builds only.
/// </summary>
public partial class ScreenCapture : SceneTree
{
    private string _output = "";
    private string _steamRoot = "";
    private int _shots;

    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exitCode = 1;
        try
        {
            string fixture = "", sizes = "1280x800,1920x1080";
            foreach (string argument in OS.GetCmdlineUserArgs())
            {
                if (argument.StartsWith("--output=", StringComparison.Ordinal)) _output = argument["--output=".Length..];
                if (argument.StartsWith("--fixture=", StringComparison.Ordinal)) fixture = argument["--fixture=".Length..];
                if (argument.StartsWith("--sizes=", StringComparison.Ordinal)) sizes = argument["--sizes=".Length..];
                if (argument.StartsWith("--steam-root=", StringComparison.Ordinal)) _steamRoot = argument["--steam-root=".Length..];
            }
            if (_output.Length == 0 || fixture.Length == 0 || !File.Exists(fixture))
            {
                GD.PrintErr("--output=DIR and an owned --fixture=COPY are required.");
                return;
            }
            Directory.CreateDirectory(_output);
            foreach (string size in sizes.Split(',', StringSplitOptions.RemoveEmptyEntries))
            {
                string[] parts = size.Split('x');
                await CaptureAll(new Vector2I(int.Parse(parts[0]), int.Parse(parts[1])), fixture);
            }
            GD.Print($"CAPTURES_DONE {_shots} screens in {_output}");
            exitCode = 0;
        }
        catch (Exception error)
        {
            GD.PrintErr("Screen capture stopped: " + error);
        }
        finally
        {
            Quit(exitCode);
        }
    }

    private async Task CaptureAll(Vector2I size, string fixture)
    {
        string label = $"{size.X}x{size.Y}";
        string work = Path.Combine(_output, "work-" + label);
        Directory.CreateDirectory(work);
        bool fake = _steamRoot.Length == 0;

        // First run on a machine without the game: Home says so and the career pages wait for a career.
        (SubViewport bare, CompanionApp empty) = await Start(size, work, "no-game", [Path.Combine(work, "no-steam")]);
        await Shot(bare, label, "first-run-no-game");
        empty.Navigate("summary");
        await Shot(bare, label, "summary-no-career");
        bare.QueueFree();
        await Settle();

        FakeInstall install = FakeInstall.Create(Path.Combine(work, "install"), File.ReadAllBytes(fixture));
        AssetTests.WriteGoodies(install.Game);
        (SubViewport viewport, CompanionApp app) = await Start(size, work, "game", [fake ? install.SteamRoot : _steamRoot]);
        for (int frame = 0; frame < 600 && app.Workspace.Session is null; frame++) await Settle();
        await Shot(viewport, label, "home-first-run");
        app.Navigate("summary");
        await Shot(viewport, label, "summary");
        app.Navigate("goodies");
        // A picture, a model and a video Goodie, shown even where the open career has not earned them.
        foreach ((int number, string name) in new[] { (2, "goodies"), (8, "goodies-model"), (201, "goodies-video") })
        {
            app.Goodies.Cells[number].EmitSignal(BaseButton.SignalName.Pressed);
            if (app.Goodies.ShowAnyway.Visible) app.Goodies.ShowAnyway.EmitSignal(BaseButton.SignalName.Pressed);
            await Reveal(app.Goodies.Cells[number]);
            await Shot(viewport, label, name);
        }
        if (app.Workspace.Session?.Analysis.Goodies.FirstOrDefault(goodie => goodie.Shown &&
            goodie.State is not (Careers.GoodieState.New or Careers.GoodieState.Old)) is { } unearned)
        {
            app.Goodies.Cells[unearned.Index].EmitSignal(BaseButton.SignalName.Pressed);
            await Reveal(app.Goodies.Cells[unearned.Index]);
            await Shot(viewport, label, "goodies-unearned");
        }

        app.Navigate("edit");
        app.EditCareer.Rows[0].Target.Value = 123456;
        app.EditCareer.Rows[3].Target.Value = 4242;
        app.EditCareer.UnlockEveryGoodie();
        await Reveal(app.EditCareer.ChangesCard);
        await Shot(viewport, label, "edit-changes");
        app.EditCareer.AskToSave();
        await Shot(viewport, label, "edit-save-dialog");
        app.EditCareer.SaveChoice.Dialog.Hide();
        if (fake)
        {
            await app.EditCareer.SaveIntoGameAsync(SaveTarget.NewCareer, "Career One (edited)");
            await Reveal(app.EditCareer.ResultPanel);
            await Shot(viewport, label, "edit-saved");
        }

        app.Navigate("cheats");
        app.Cheats.BaseName.Text = "Pilot";
        app.Cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "Pilot");
        app.Cheats.Choices[0].ButtonPressed = true;
        await Reveal(app.Cheats.AddToGame);
        await Shot(viewport, label, "cheats");
        app.Cheats.AskToAdd();
        await Shot(viewport, label, "cheats-confirm");
        app.Cheats.Confirm.Hide();

        app.Navigate("settings");
        for (int frame = 0; frame < 600 && (app.Settings.Reading is null || app.Workspace.Busy); frame++) await Settle();
        await Shot(viewport, label, "settings");
        app.Settings.Music.Value = app.Settings.Music.Value > 50 ? 20 : 80;
        app.Settings.StartCapture(0x21, 1);
        await Shot(viewport, label, "settings-key");
        app.Settings.Capture(Key.T);
        await Reveal(app.Settings.ChangesCard);
        await Shot(viewport, label, "settings-changes");
        app.Settings.AskToSave();
        await Shot(viewport, label, "settings-save-dialog");
        app.Settings.SaveChoice.Dialog.Hide();

        app.Navigate("backups");
        if (Backups.List(app.Services.Backups.Folder).Count == 0) await app.Backups.BackUpAsync();
        app.Backups.Refresh();
        await Shot(viewport, label, "backups");
        IReadOnlyList<BackupSet> sets = Backups.List(app.Services.Backups.Folder);
        if (sets.Count > 0)
        {
            app.Backups.AskToRestore(sets[^1], sets[^1].Files[0]);
            await Shot(viewport, label, "backups-put-back");
            app.Backups.Confirm.Hide();
        }

        app.Navigate("home");
        await Shot(viewport, label, "home");

        app.Navigate("music");
        if (app.Music.Items.FirstOrDefault(item => item.Kind == Media.AudioKind.Voice) is Media.GameAudioItem voice)
        {
            // Only loaded to show the player; nothing is played during a capture.
            app.Music.Load(voice);
            for (TreeItem? group = app.Music.List.GetRoot()?.GetFirstChild(); group is not null; group = group.GetNext())
                if (group.GetText(0) == voice.Group) group.Collapsed = false;
        }
        await Shot(viewport, label, "music");

        app.Navigate("lore");
        await Shot(viewport, label, "lore-front-door");
        app.Lore.Open("battle-engine-tech");
        await Shot(viewport, label, "lore-memo");
        app.Lore.Open("community-preservation", "active-community-contacts");
        await Shot(viewport, label, "lore-table");
        app.Lore.Open("the-campaign", "the-missions");
        await Shot(viewport, label, "lore-campaign-missions");
        app.Lore.Search.Text = "Kiralova";
        app.Lore.Search.EmitSignal(LineEdit.SignalName.TextChanged, "Kiralova");
        await Shot(viewport, label, "lore-search");
        app.Lore.Search.Text = "";
        app.Lore.Search.EmitSignal(LineEdit.SignalName.TextChanged, "");

        app.Navigate("bytes");
        app.Bytes.ShowView(0);
        await Shot(viewport, label, "advanced-stored-values");
        string other = Path.Combine(work, "other.bes");
        byte[] otherBytes = File.ReadAllBytes(fixture);
        otherBytes[0x23F6] ^= 0x10;
        File.WriteAllBytes(other, otherBytes);
        await app.Bytes.CompareAsync(other);
        await Shot(viewport, label, "advanced-compare");
        app.Bytes.ShowView(0);
        app.Navigate("assets");
        app.Assets.Refresh();
        await Shot(viewport, label, "extras-models");
        if (app.Assets.List.GetRoot()?.GetChildren() is { Count: > 0 } models)
        {
            TreeItem model = models.FirstOrDefault(row => row.GetText(0) == "arachnid") ?? models[0];
            app.Assets.Select(model);
            await Shot(viewport, label, "extras-model-preview");
            string? used = app.Assets.ModelTextureTitle();
            app.Assets.Kind.Select(1);
            app.Assets.Kind.EmitSignal(OptionButton.SignalName.ItemSelected, 1);
            if (app.Assets.List.GetRoot()?.GetChildren() is { Count: > 0 } textures)
            {
                app.Assets.Select(textures.FirstOrDefault(row => row.GetText(0) == used) ?? textures[0]);
                await Shot(viewport, label, "extras-texture-preview");
            }
            app.Assets.Kind.Select(2);
            app.Assets.Kind.EmitSignal(OptionButton.SignalName.ItemSelected, 2);
            if (app.Assets.List.GetRoot()?.GetChildren() is { Count: > 0 } sounds)
            {
                app.Assets.Select(sounds.FirstOrDefault(row => row.GetText(0).Contains("Ammunition", StringComparison.OrdinalIgnoreCase)) ?? sounds[0]);
                await Shot(viewport, label, "extras-sound");
            }
            app.Assets.Kind.Select(0);
            app.Assets.Kind.EmitSignal(OptionButton.SignalName.ItemSelected, 0);
        }
        app.Navigate("home");
        app.Home.OpenDialog.CurrentDir = work;
        app.Home.OpenDialog.PopupCenteredRatio(0.75f);
        await Shot(viewport, label, "open-dialog");
        app.Home.OpenDialog.Hide();

        if (fake)
        {
            // A career partway through the campaign, so the map's open and not-yet-reached missions are seen too.
            File.WriteAllBytes(Path.Combine(install.Game, "savegames", "Career Two.bes"), MidCampaign(File.ReadAllBytes(fixture)));
            await app.Game.RescanAsync();
            await app.OpenCareerAsync(Path.Combine(install.Game, "savegames", "Career Two.bes"));
            app.Navigate("summary");
            await Shot(viewport, label, "summary-mid-campaign");
        }

        viewport.QueueFree();
        await Settle();
    }

    private async Task<(SubViewport, CompanionApp)> Start(Vector2I size, string work, string name, IReadOnlyList<string> steamRoots)
    {
        SubViewport viewport = new()
        {
            Size = size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always, TransparentBg = false,
            // Dialogs render inside the capture, as they do inside the application's own window.
            GuiEmbedSubwindows = true,
        };
        Root.AddChild(viewport);
        // The fake install is closed by definition; a real library keeps the real running-game check.
        CompanionEnvironment environment = new(steamRoots, Path.Combine(work, name + "-settings", "settings.json"),
            _steamRoot.Length > 0 ? null : () => false, _ => { }, Path.Combine(work, name + "-backups"));
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false, environment);
        viewport.AddChild(app);
        await Settle();
        for (int frame = 0; frame < 600 && (app.Game.Busy || (steamRoots.Count > 0 && app.Game.Folder is null && frame < 60)); frame++)
            await Settle();
        return (viewport, app);
    }

    /// <summary>
    /// The real fixture as a career that has finished chapters 1 to 4 and reached 5.00: every mission from
    /// 5.00 on loses its win and rank, and every route leading past 5.00 is closed again. Length and every other
    /// byte are the fixture's. Written only into this capture's own fake install.
    /// </summary>
    private static byte[] MidCampaign(byte[] career)
    {
        byte[] bytes = career.ToArray();
        uint World(int node) => BitConverter.ToUInt32(bytes, 0x0006 + node * 0x40 + 0x10);
        for (int node = 0; node < 100; node++)
        {
            if (World(node) < 500) continue;
            Array.Clear(bytes, 0x0006 + node * 0x40 + 0x04, 4);
            Array.Clear(bytes, 0x0006 + node * 0x40 + 0x3C, 4);
        }
        for (int link = 0; link < 200; link++)
        {
            uint to = BitConverter.ToUInt32(bytes, 0x1906 + link * 8 + 4);
            if (to < 100 && World((int)to) > 500) Array.Clear(bytes, 0x1906 + link * 8, 4);
        }
        return bytes;
    }

    private async Task Shot(SubViewport viewport, string size, string name)
    {
        await Settle();
        Image image = viewport.GetTexture().GetImage();
        string path = Path.Combine(_output, $"{size}-{++_shots:D2}-{name}.png");
        Error saved = image.SavePng(path);
        if (saved != Error.Ok) throw new IOException($"Could not save {path}: {saved}");
        GD.Print($"CAPTURE {path}");
    }

    /// <summary>Scrolls the page so a control is on screen, as a player would before looking at it.</summary>
    private async Task Reveal(Control control)
    {
        await Settle();
        for (Node? node = control.GetParent(); node is not null; node = node.GetParent())
        {
            if (node is not ScrollContainer scroll) continue;
            scroll.EnsureControlVisible(control);
            break;
        }
    }

    private async Task Settle()
    {
        for (int frame = 0; frame < 4; frame++) await ToSignal(this, SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
    }
}
