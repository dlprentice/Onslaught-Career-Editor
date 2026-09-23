// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Production cursor placement and last-draw composition versus the
/// retained 92c1775b renderer. The caller owns the isolated display/output.</summary>
public sealed partial class MouseCursorSceneChecks : Node
{
    private int _checks;
    private readonly List<object> _pixels = [];

    public override async void _Ready()
    {
        var views = new List<SubViewport>();
        List<RetailFrontendFlow> facades = [];
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Contains("--skipfmv", StringComparer.Ordinal), "This check requires --skipfmv.");
            const string option = "--cursor-render-dir=";
            string? directory = args.FirstOrDefault(x => x.StartsWith(option, StringComparison.Ordinal))?[option.Length..];
            if (directory is not null)
            {
                string owner = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
                Check(Path.IsPathFullyQualified(directory) && Path.GetFullPath(directory).StartsWith(owner, StringComparison.Ordinal)
                    && Directory.Exists(directory) && !Directory.EnumerateFileSystemEntries(directory).Any()
                    && DisplayServer.GetName() != "headless", "Rendering requires a fresh owned directory and isolated display.");
            }
            Input.MouseModeEnum pointer = Input.MouseMode;
            SubViewport actualViewport = MakeViewport(), expectedViewport = MakeViewport();
            views.AddRange([actualViewport, expectedViewport]);
            RetailFrontendFlow actual = MakeHost(actualViewport, facades), expected = MakeHost(expectedViewport, facades);
            var reference = new MouseCursorReference { Name = "RetainedCursor", ZIndex = 2 };
            expected.View.AddChild(reference);
            Control cursor = actual.View.GetNode<Control>("MouseCursor");
            Check(cursor.GetNode<Control>("Quad").Get("quad_size").AsVector2() == new Vector2(32, 32), "Actual cursor geometry is an authored Control.");
            Check(cursor.ZIndex == 2 && !cursor.IsProcessing() && !cursor.IsProcessingInput(),
                "Cursor is the final frontend layer and has no clock or input owner.");
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);

            // Main Menu's reflection is the regression this separate last-draw
            // layer originally fixed. Compare the actual composed page, not a
            // cursor over an empty screenshot.
            foreach (RetailFrontendFlow host in new[] { actual, expected })
            {
                host.ConfirmForSmoke();
                SetField(host, "_animation_seconds", 1.25d);
                SetField(host, "_fe_back_seconds", 0.75d);
            }
            (Vector2I Size, Vector2 Position)[] samples =
            [
                (new(640, 480), new(0, 0)),
                (new(640, 480), new(320, 240)),
                (new(640, 480), new(618, 450)),
                (new(1280, 720), new(320, 240)),
                (new(801, 601), new(321.125f, 245.375f)),
                (new(320, 240), new(-12.25f, 17.375f)),
            ];
            for (int index = 0; index < samples.Length; index++)
            {
                (Vector2I size, Vector2 position) = samples[index];
                foreach (SubViewport viewport in views) viewport.Size = size;
                foreach (RetailFrontendFlow host in new[] { actual, expected })
                {
                    host.View.Size = size;
                    host.SetMouseCursorDesignPositionForCapture(position);
                    Refresh(host);
                }
                expected.View.GetNode<Control>("MouseCursor").Visible = false;
                reference.Screen = actual.CurrentScreen;
                reference.CursorPosition = position;
                reference.ViewportSize = size;
                reference.QueueRedraw();
                using Godot.Collections.Dictionary frame = cursor.Call("view_snapshot").AsGodotDictionary();
                Check(frame["screen"].AsInt32() == (int)RetailFrontendScreen.MainMenu
                    && frame["cursor_position"].AsVector2() == position,
                    "Deterministic capture position reaches the production cursor unchanged.");
                Check(cursor.Visible, "Main Menu draws the production cursor.");
                if (directory is null) continue;
                await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
                await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
                using Image a = actualViewport.GetTexture().GetImage();
                using Image e = expectedViewport.GetTexture().GetImage();
                string name = $"{index:D2}-{size.X}x{size.Y}";
                byte[] actualBytes = a.GetData(), expectedBytes = e.GetData();
                int differences = actualBytes.Length == expectedBytes.Length
                    ? actualBytes.Where((value, offset) => value != expectedBytes[offset]).Count() : -1;
                _pixels.Add(new { name, differences, actualHash = Convert.ToHexString(SHA256.HashData(actualBytes)),
                    expectedHash = Convert.ToHexString(SHA256.HashData(expectedBytes)) });
                Check(a.SavePng(Path.Combine(directory, name + "-native.png")) == Error.Ok
                    && e.SavePng(Path.Combine(directory, name + "-reference.png")) == Error.Ok, "Owned captures saved.");
                Check(differences == 0, $"{name} differs in {differences} RGBA bytes.");
            }

            actual.SetMouseCursorDesignPositionForCapture(null);
            using (Godot.Collections.Dictionary live = cursor.Call("view_snapshot").AsGodotDictionary())
                Check(live["cursor_position"].VariantType == Variant.Type.Nil, "Live pointer is explicitly restored without changing pointer mode.");
            actual.SuspendForStartupMedia();
            Check(!cursor.IsVisibleInTree(), "Startup suspension hides the native cursor with the frontend.");
            actual.ResumeAfterStartupMedia();
            Check(cursor.IsVisibleInTree(), "Startup resume restores the same production cursor component.");
            actual.View.SetProcess(false); actual.View.SetProcessInput(false);
            actual.ConfirmForSmoke(); // Career Name
            actual.ConfirmForSmoke(); // Level Select
            actual.ConfirmForSmoke(); // Briefing
            actual.ConfirmForSmoke(); // Configuration
            actual.ConfirmForSmoke(); // Loading
            Check(actual.CurrentScreen == RetailFrontendScreen.Loading && !cursor.GetNode<CanvasItem>("Quad").Visible,
                "The launch edge suppresses the cursor before the first Loading draw.");
            Check(Input.MouseMode == pointer, "Presentation never changes the host pointer mode.");
            FrontendHarnessChecks.ReleaseFacades(facades);
            foreach (SubViewport view in views) view.QueueFree(); views.Clear();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print("MOUSE_CURSOR_SCENE_CHECKS: " + JsonSerializer.Serialize(new { checks = _checks, pixels = _pixels, failures = 0 }));
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            FrontendHarnessChecks.ReleaseFacades(facades);
            foreach (SubViewport view in views) view.QueueFree();
            GD.Print("MOUSE_CURSOR_SCENE_CHECKS: " + JsonSerializer.Serialize(new { checks = _checks, pixels = _pixels, failures = 1 }));
            GD.PushError(error.ToString()); GetTree().Quit(1);
        }
    }

    private SubViewport MakeViewport()
    {
        var view = new SubViewport { Size = new Vector2I(640, 480), Disable3D = true,
            RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
        AddChild(view); return view;
    }

    private static RetailFrontendFlow MakeHost(SubViewport viewport, List<RetailFrontendFlow> facades)
    {
        RetailFrontendFlow host = RetailFrontendFlow.InstantiateScene(); facades.Add(host);
        host.Initialize([]); viewport.AddChild(host.View);
        host.View.SetProcess(false); host.View.SetProcessInput(false);
        return host;
    }

    private static void SetField(RetailFrontendFlow host, string name, Variant value) =>
        host.View.Set(name, value);
    private static void Refresh(RetailFrontendFlow host) =>
        FrontendHarnessChecks.Command(host, "redraw");
    private void Check(bool condition, string message)
    {
        _checks++; if (!condition) throw new InvalidOperationException(message);
    }
}
