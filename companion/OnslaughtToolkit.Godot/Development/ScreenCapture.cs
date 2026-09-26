// SPDX-License-Identifier: MIT
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
        (SubViewport viewport, CompanionApp app) = await Start(size, work, "game", [fake ? install.SteamRoot : _steamRoot]);
        for (int frame = 0; frame < 600 && app.Workspace.Session is null; frame++) await Settle();
        await Shot(viewport, label, "home-first-run");
        app.Navigate("summary");
        await Shot(viewport, label, "summary");
        app.Navigate("goodies");
        app.Goodies.Cells[2].EmitSignal(BaseButton.SignalName.Pressed);
        await Shot(viewport, label, "goodies");

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

        app.Navigate("compare");
        string other = Path.Combine(work, "other.bes");
        byte[] otherBytes = File.ReadAllBytes(fixture);
        otherBytes[0x23F6] ^= 0x10;
        File.WriteAllBytes(other, otherBytes);
        await app.Compare.CompareAsync(other);
        await Shot(viewport, label, "advanced-compare");
        app.Navigate("raw");
        await Shot(viewport, label, "advanced-raw-values");
        app.Navigate("media");
        await app.MediaFiles.BrowseAsync(MediaFixture(work));
        await Shot(viewport, label, "advanced-media-files");
        app.Navigate("home");
        app.Home.OpenDialog.CurrentDir = work;
        app.Home.OpenDialog.PopupCenteredRatio(0.75f);
        await Shot(viewport, label, "open-dialog");
        app.Home.OpenDialog.Hide();

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

    private static string MediaFixture(string work)
    {
        // Tiny original byte headers under owned output; never retail assets.
        string root = Path.Combine(work, "media");
        Directory.CreateDirectory(Path.Combine(root, "voice"));
        File.WriteAllBytes(Path.Combine(root, "theme.ogg"), Convert.FromHexString("4f67675300020000"));
        File.WriteAllBytes(Path.Combine(root, "voice", "briefing.ogg"), Convert.FromHexString("4f67675300020000"));
        File.WriteAllBytes(Path.Combine(root, "intro.vid"), Convert.FromHexString("56494400"));
        File.WriteAllBytes(Path.Combine(root, "cover.png"), Convert.FromHexString("89504e470d0a1a0a"));
        File.WriteAllText(Path.Combine(root, "notes.txt"), "not media");
        return root;
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
