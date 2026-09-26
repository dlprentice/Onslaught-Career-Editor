// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Files;
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
        string original = Path.Combine(work, "career.bes");
        File.Copy(fixture, original);
        string media = MediaFixture(work);

        SubViewport viewport = new()
        {
            Size = size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always, TransparentBg = false,
        };
        Root.AddChild(viewport);
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false);
        viewport.AddChild(app);
        await Settle();
        foreach (string page in new[] { "home", "edit", "compare", "stored", "media" })
        {
            app.Navigate(page);
            await Shot(viewport, label, page + "-before-open");
        }

        app.Navigate("home");
        await app.OpenCareerAsync(original);
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

        app.Navigate("stored");
        TreeItem? first = app.StoredValues.Tree.GetRoot()?.GetFirstChild();
        if (first?.GetNext() is TreeItem links) links.Collapsed = false;
        await Shot(viewport, label, "stored-values");

        app.Navigate("compare");
        await app.Compare.CompareAsync(Path.Combine(work, "career-edited.bes"));
        await Shot(viewport, label, "compare");

        app.Navigate("media");
        await app.MediaFiles.BrowseAsync(media);
        app.MediaFiles.Files.GetRoot()?.GetFirstChild()?.Select(0);
        await Shot(viewport, label, "media-files");

        app.Navigate("home");
        app.OpenDialog.CurrentDir = work;
        app.OpenDialog.PopupCenteredRatio(0.75f);
        await Shot(viewport, label, "open-dialog");
        app.OpenDialog.Hide();

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

    private async Task Settle()
    {
        for (int frame = 0; frame < 4; frame++) await ToSignal(this, SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
    }
}
