// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Tests;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Renders every companion screen at fixed sizes through SubViewports, so a tiling window
/// manager cannot resize the capture. Run on a GPU output (godot-offscreen):
/// <c>--script res://Development/ScreenCapture.cs -- --output=DIR --fixture=OWNED_COPY [--sizes=1280x800,1920x1080]</c>.
/// Every file it writes stays inside the owned output directory. Development builds only.
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
            string fixture = "", sizes = "1280x800,1920x1080", steamRoot = "";
            foreach (string argument in OS.GetCmdlineUserArgs())
            {
                if (argument.StartsWith("--output=", StringComparison.Ordinal)) _output = argument["--output=".Length..];
                if (argument.StartsWith("--fixture=", StringComparison.Ordinal)) fixture = argument["--fixture=".Length..];
                if (argument.StartsWith("--sizes=", StringComparison.Ordinal)) sizes = argument["--sizes=".Length..];
                if (argument.StartsWith("--steam-root=", StringComparison.Ordinal)) steamRoot = argument["--steam-root=".Length..];
            }
            _steamRoot = steamRoot;
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
        string original = Path.Combine(work, "career.bes");
        File.Copy(fixture, original);
        string media = MediaFixture(work);

        SubViewport viewport = new()
        {
            Size = size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always, TransparentBg = false,
            // Dialogs render inside the capture, as they do inside the application's own window.
            GuiEmbedSubwindows = true,
        };
        Root.AddChild(viewport);
        // A fake Steam library by default; --steam-root points at a real one, which is only read.
        FakeInstall install = FakeInstall.Create(Path.Combine(work, "install"), File.ReadAllBytes(fixture));
        // The fake install is closed by definition; a real library keeps the real running-game check.
        CompanionEnvironment environment = new([_steamRoot.Length > 0 ? _steamRoot : install.SteamRoot],
            Path.Combine(work, "settings", "settings.json"), _steamRoot.Length > 0 ? null : () => false);
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false, environment);
        viewport.AddChild(app);
        await Settle();
        for (int frame = 0; frame < 600 && (app.Game.Busy || app.Game.Folder is null); frame++) await Settle();
        foreach (string page in app.Pages.Keys)
        {
            app.Navigate(page);
            await Shot(viewport, label, page + "-empty");
        }

        app.Navigate("home");
        await app.OpenCareerAsync(original);
        await Shot(viewport, label, "overview");
        app.Navigate("goodies");
        app.Goodies.Cells[2].EmitSignal(BaseButton.SignalName.Pressed);
        await Shot(viewport, label, "goodies");
        app.Goodies.ChangeInCopy.EmitSignal(BaseButton.SignalName.Pressed);
        foreach ((int row, int count) in new[] { (0, 123456), (3, 4242) })
        {
            app.EditCopy.Rows[row].Target.Value = count;
            app.EditCopy.Rows[row].Selected.ButtonPressed = true;
        }
        await Shot(viewport, label, "edit-preview");
        app.EditCopy.Destination.Text = Path.Combine(work, "career-edited.bes");
        await app.EditCopy.WriteCopyAsync(unchanged: false);
        await Shot(viewport, label, "edit-verified-copy");
        await app.EditCopy.WriteCopyAsync(unchanged: true);
        await Shot(viewport, label, "edit-refused-existing");

        app.Navigate("compare");
        await app.Compare.CompareAsync(Path.Combine(work, "career-edited.bes"));
        await Shot(viewport, label, "compare");
        app.Navigate("stored");
        TreeItem? first = app.StoredValues.Tree.GetRoot()?.GetFirstChild();
        if (first?.GetNext() is TreeItem links) links.Collapsed = false;
        await Shot(viewport, label, "stored-values");
        app.Navigate("media");
        await app.MediaFiles.BrowseAsync(media);
        app.MediaFiles.Files.GetRoot()?.GetFirstChild()?.Select(0);
        await Shot(viewport, label, "media-files");
        app.Navigate("home");
        await Shot(viewport, label, "home-career-open");
        app.OpenDialog.CurrentDir = work;
        app.OpenDialog.PopupCenteredRatio(0.75f);
        await Shot(viewport, label, "open-dialog");
        app.OpenDialog.Hide();

        // Game writes are only confirmed against the fake install; a real --steam-root is only read.
        bool fake = _steamRoot.Length == 0;
        app.Navigate("cheats");
        app.Cheats.BaseName.Text = "Pilot";
        app.Cheats.BaseName.EmitSignal(LineEdit.SignalName.TextChanged, "Pilot");
        app.Cheats.Choices[0].ButtonPressed = true;
        await Settle();
        if (app.Cheats.Root is ScrollContainer cheatsScroll) cheatsScroll.ScrollVertical = (int)cheatsScroll.GetVScrollBar().MaxValue;
        await Shot(viewport, label, "cheats-needs-backup-folder");
        string backups = Path.Combine(work, "backups");
        Directory.CreateDirectory(backups);
        app.Install.SetBackupFolder(backups);
        app.Cheats.Refresh();
        app.Cheats.AskToAdd();
        await Shot(viewport, label, "cheats-confirm");
        app.Cheats.Confirm.Hide();

        app.Navigate("options");
        app.Options.OpenGameOptions.EmitSignal(BaseButton.SignalName.Pressed);
        for (int frame = 0; frame < 600 && (app.Options.Reading is null || app.Workspace.Busy); frame++) await Settle();
        await Shot(viewport, label, "options-open");
        app.Options.Music.Value = app.Options.Music.Value > 50 ? 20 : 80;
        app.Options.StartCapture(0x21, 1);
        await Shot(viewport, label, "options-capturing-key");
        app.Options.Capture(Key.T);
        app.Options.Destination.Text = Path.Combine(work, "options-copy.bea");
        await app.Options.WriteCopyAsync();
        await Reveal(app.Options.InstallCopy);
        await Shot(viewport, label, "options-verified-copy");
        app.Options.AskToInstall();
        await Shot(viewport, label, "options-confirm");
        app.Options.Confirm.Hide();

        app.Navigate("install");
        await app.Install.BackUpAsync();
        await Shot(viewport, label, "install-backed-up");
        app.Install.SetSource(Path.Combine(work, "career-edited.bes"));
        int newItem = Enumerable.Range(0, app.Install.Target.ItemCount).FirstOrDefault(item => app.Install.Target.GetItemText(item) == "A new career…", -1);
        if (newItem >= 0)
        {
            app.Install.Target.Select(newItem);
            app.Install.Target.EmitSignal(OptionButton.SignalName.ItemSelected, newItem);
        }
        app.Install.NewName.Text = "Edited Career";
        app.Install.NewName.EmitSignal(LineEdit.SignalName.TextChanged, app.Install.NewName.Text);
        await Reveal(app.Install.Install);
        await Shot(viewport, label, "install-ready");
        app.Install.AskToInstall();
        await Shot(viewport, label, "install-confirm");
        if (fake)
        {
            await app.Install.ConfirmAsync();
            await Reveal(app.Install.Install);
            await Shot(viewport, label, "install-done");
        }
        else
        {
            app.Install.Confirm.Hide();
        }

        app.Navigate("music");
        if (app.Music.Items.FirstOrDefault(item => item.Kind == Media.AudioKind.Voice) is Media.GameAudioItem voice)
        {
            // Only loaded to show the player; nothing is played during a capture.
            app.Music.Load(voice);
            for (TreeItem? group = app.Music.List.GetRoot()?.GetFirstChild(); group is not null; group = group.GetNext())
                if (group.GetText(0) == voice.Group) group.Collapsed = false;
        }
        await Shot(viewport, label, "music-voice-selected");

        app.Navigate("lore");
        app.Lore.Open("battle-engine-tech");
        await Shot(viewport, label, "lore-memo");
        app.Lore.Open("worlds", "world-500--career-node-23");
        await Shot(viewport, label, "lore-section");
        app.Lore.Open("community-preservation", "active-community-contacts");
        await Shot(viewport, label, "lore-table");
        app.Lore.Open("the-campaign", "the-missions");
        await Shot(viewport, label, "lore-campaign-missions");
        app.Lore.Search.Text = "Kiralova";
        app.Lore.Search.EmitSignal(LineEdit.SignalName.TextChanged, "Kiralova");
        await Shot(viewport, label, "lore-search");
        app.Lore.Search.Text = "";
        app.Lore.Search.EmitSignal(LineEdit.SignalName.TextChanged, "");

        viewport.QueueFree();
        await Settle();
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
