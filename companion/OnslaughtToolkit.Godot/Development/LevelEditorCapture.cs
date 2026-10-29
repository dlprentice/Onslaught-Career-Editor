// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Draws the Level editor against a Steam-shaped game folder and runs the editor's acceptance on it: open level 100, select row 12
/// (a Target Tank), type 276.49, 265.07 and -12.1, save as a mod into the capture's own output, and compare the saved world file's
/// SHA-256 with the one the Toolkit's pipeline gives for the same edit. Run on a GPU output (godot-offscreen):
/// <c>--script res://Development/LevelEditorCapture.cs -- --output=DIR --fixture=ANY_FILE --steam-root=DIR [--sizes=1920x1080]
/// [--level=100] [--row=12] [--expect-sha256=HEX]</c>. The game folder is only read; every file this writes stays inside the output
/// directory. Development builds only.
/// </summary>
public partial class LevelEditorCapture : SceneTree
{
    private const string ToolkitSha256 = "b078e3d29e7916d9785e1985b8addc48d5898444b70b5055da0ca15ba4511f94";
    private string _output = "", _steamRoot = "", _expected = ToolkitSha256;
    private int _shots, _level = 100, _row = 12;
    private bool _passed = true;

    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exitCode = 1;
        try
        {
            string sizes = "1920x1080";
            foreach (string argument in OS.GetCmdlineUserArgs())
            {
                if (argument.StartsWith("--output=", StringComparison.Ordinal)) _output = argument["--output=".Length..];
                if (argument.StartsWith("--sizes=", StringComparison.Ordinal)) sizes = argument["--sizes=".Length..];
                if (argument.StartsWith("--steam-root=", StringComparison.Ordinal)) _steamRoot = argument["--steam-root=".Length..];
                if (argument.StartsWith("--level=", StringComparison.Ordinal)) _level = int.Parse(argument["--level=".Length..]);
                if (argument.StartsWith("--row=", StringComparison.Ordinal)) _row = int.Parse(argument["--row=".Length..]);
                if (argument.StartsWith("--expect-sha256=", StringComparison.Ordinal)) _expected = argument["--expect-sha256=".Length..].ToLowerInvariant();
            }
            if (_output.Length == 0 || _steamRoot.Length == 0 || !Directory.Exists(_steamRoot))
            {
                GD.PrintErr("--output=DIR and --steam-root=DIR (a Steam-shaped folder holding the game) are required.");
                return;
            }
            Directory.CreateDirectory(_output);
            foreach (string size in sizes.Split(',', StringSplitOptions.RemoveEmptyEntries))
            {
                string[] parts = size.Split('x');
                await CaptureAt(new Vector2I(int.Parse(parts[0]), int.Parse(parts[1])));
            }
            GD.Print($"ACCEPTANCE_RESULT {(_passed ? "PASS" : "FAIL")}");
            GD.Print($"CAPTURES_DONE {_shots} screens in {_output}");
            exitCode = _passed ? 0 : 2;
        }
        catch (Exception error)
        {
            GD.PrintErr("Level editor capture stopped: " + error);
        }
        finally
        {
            Quit(exitCode);
        }
    }

    private void Report(bool ok, string what)
    {
        if (!ok) _passed = false;
        GD.Print($"ACCEPTANCE {(ok ? "ok  " : "FAIL")} {what}");
    }

    private async Task CaptureAt(Vector2I size)
    {
        string label = $"{size.X}x{size.Y}";
        string work = Path.Combine(_output, "work-" + label);
        Directory.CreateDirectory(work);
        SubViewport viewport = new() { Size = size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always, TransparentBg = false, GuiEmbedSubwindows = true };
        Root.AddChild(viewport);
        CompanionEnvironment environment = new([_steamRoot], Path.Combine(work, "settings", "settings.json"), () => false, _ => { }, Path.Combine(work, "backups"));
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false, environment);
        viewport.AddChild(app);
        await Settle();
        for (int frame = 0; frame < 600 && (app.Game.Busy || app.Game.Folder is null); frame++) await Settle();
        Report(app.Game.Folder is not null, $"the game folder was found: {app.Game.Folder?.Root}");
        LevelEditorPage page = app.LevelEditor;
        app.Navigate("levels");
        await Settle();
        Report(page.Level.ItemCount > 1, $"the page lists {page.Level.ItemCount - 1} levels");
        await Shot(viewport, label, "level-editor-1-pick-a-level");

        bool opened = page.OpenLevel(_level);
        await Settle();
        Report(opened && page.Model?.Session is not null, $"level {_level} opened: {page.Model?.Session?.Body.Things.Count} objects, subtitle \"{app.PageSubtitle.Text}\"");
        await Shot(viewport, label, "level-editor-2-level-open");

        bool selected = page.SelectRow(_row);
        await Settle();
        string name = page.SelectedName ?? "";
        Report(selected && name.StartsWith("Target Tank", StringComparison.Ordinal), $"row {_row} is \"{name}\" at {page.X.Text}, {page.Y.Text}, {page.Z.Text}");
        await Shot(viewport, label, "level-editor-3-object-selected");

        page.X.Text = "276.49";
        page.Y.Text = "265.07";
        page.Z.Text = "-12.1";
        page.X.EmitSignal(LineEdit.SignalName.TextSubmitted, page.X.Text);
        await Settle();
        Report(page.Note.Contains("now stands at 276.49, 265.07, -12.1", StringComparison.Ordinal), $"typing moved it: \"{page.Note}\"");
        Report(page.Summary.StartsWith("1 object moved", StringComparison.Ordinal), $"summary: \"{page.Summary}\"");
        await Shot(viewport, label, "level-editor-4-moved");

        string mods = Path.Combine(_output, "mods-" + label);
        page.Save.EmitSignal(BaseButton.SignalName.Pressed);
        page.SaveDialog.Destination.Text = mods;
        page.SaveDialog.Destination.EmitSignal(LineEdit.SignalName.TextChanged, mods);
        await Settle();
        Report(page.SaveDialog.Problem.Length == 0, $"the save dialog is ready: \"{page.SaveDialog.ModName.Text}\" / {page.SaveDialog.Id.Text}");
        await Shot(viewport, label, "level-editor-5-save-as-mod");
        page.SaveDialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        page.SaveDialog.Hide();
        await Settle();
        string world = Path.Combine(mods, page.SaveDialog.Id.Text, "data", "worlds", $"world{_level:D3}.wrd");
        string manifest = Path.Combine(mods, page.SaveDialog.Id.Text, "mod.json");
        if (File.Exists(world))
        {
            byte[] bytes = File.ReadAllBytes(world);
            string hash = Convert.ToHexStringLower(SHA256.HashData(bytes));
            Report(hash == _expected, $"{world}: {bytes.Length:N0} bytes, SHA-256 {hash}{(hash == _expected ? " = the Toolkit pipeline's" : $", expected {_expected}")}");
            Report(File.Exists(manifest), $"mod.json written: {File.Exists(manifest)}");
        }
        else
        {
            Report(false, $"no world file was written at {world}: \"{page.SavedText}\"");
        }
        await Shot(viewport, label, "level-editor-6-saved");
        viewport.QueueFree();
        await Settle();
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
