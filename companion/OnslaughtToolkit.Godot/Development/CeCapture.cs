// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Tests;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>CE screens from owned fixture copies. Never starts a launcher; --live-feed explicitly checks the public feed.</summary>
public partial class CeCapture : SceneTree
{
    public override void _Initialize() => _ = CaptureAsync();
    private async Task CaptureAsync()
    {
        int exit = 1;
        try
        {
            string Arg(string name, string fallback = "") => OS.GetCmdlineUserArgs().FirstOrDefault(a => a.StartsWith(name + "=", StringComparison.Ordinal))?[(name.Length + 1)..] ?? fallback;
            string output = Arg("--output"), fixture = Arg("--fixture");
            if (output.Length == 0 || !File.Exists(fixture)) throw new IOException("Owned output and fixture are required.");
            Directory.CreateDirectory(output);
            foreach (string dimensions in Arg("--sizes", "1280x800").Split(','))
            {
                int[] xy = dimensions.Split('x').Select(int.Parse).ToArray();
                string work = Path.Combine(output, "work-" + dimensions);
                FakeInstall install = FakeInstall.Create(Path.Combine(work, "original"), File.ReadAllBytes(fixture));
                string user = Path.Combine(work, "ce-user");
                Directory.CreateDirectory(Path.Combine(user, "savegames"));
                File.Copy(fixture, Path.Combine(user, "savegames", "CE Pilot.bes"));
                File.WriteAllText(Path.Combine(user, "ce.ini"), "update_check=1\nrecord_sessions=0\n");
                SettingsStore settings = new(Path.Combine(work, "settings.json"));
                settings.Save(new CompanionSettings { GameFolder = install.Game, Target = GameTarget.OnslaughtCe, AutoBackup = false });
                SubViewport viewport = new() { Size = new Vector2I(xy[0], xy[1]), RenderTargetUpdateMode = SubViewport.UpdateMode.Always,
                    GuiEmbedSubwindows = true };
                Root.AddChild(viewport);
                CompanionApp app = new(new ProtectedSaveFiles(), false, new CompanionEnvironment([install.SteamRoot], settings.FilePath,
                    GameRunning: () => false, OpenUrl: _ => { }, DefaultBackupFolder: Path.Combine(work, "backups"), CeUserFolder: user,
                    CeInstallSupported: GameFolder.LooksLikeGame));
                viewport.AddChild(app);
                await Frame();
                await Frame();
                for (int n = 0; n < 600 && (app.Game.Busy || app.Workspace.Session is null); n++) await Frame();
                async Task Shot(string label)
                {
                    for (int n = 0; n < 6; n++) await Frame();
                    await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
                    using Image picture = viewport.GetTexture().GetImage();
                    if (picture.SavePng(Path.Combine(output, dimensions + "-" + label + ".png")) != Error.Ok) throw new IOException("Capture failed");
                }
                app.Navigate("home");
                if (Arg("--live-feed") == "1") await app.Home.CePanel.CheckUpdatesAsync();
                await Shot("ce-home");
                ((ScrollContainer)app.Home.Root).ScrollVertical = 540;
                await Shot("ce-original-careers");
                ((ScrollContainer)app.Home.Root).ScrollVertical = 0;
                app.Navigate("summary"); await Shot("ce-career");
                app.Navigate("settings"); await app.Settings.CePanel.LoadAsync(); await Shot("ce-settings");
                app.Settings.CePanel.RecordSessions.ButtonPressed = true;
                app.Settings.CePanel.AskToSave(); await Shot("ce-settings-confirm");
                app.Settings.CePanel.Confirm.Hide();
                InstallReceipt saved = await app.Settings.CePanel.SaveAsync();
                if (!saved.Ok || saved.BackupFolder is not string settingsBackup ||
                    app.Settings.CePanel.ResultText.Split(settingsBackup, StringSplitOptions.None).Length != 2)
                    throw new IOException("The saved settings must show their complete backup location exactly once.");
                await Shot("ce-settings-saved");
                string backups = Path.Combine(work, "backups");
                Directory.CreateDirectory(backups);
                BackupSet originalBackup = Backups.Create(new ProtectedSaveFiles(), app.Game.Original!, backups,
                    DateTime.Now).Set ?? throw new IOException("Fixture backup failed");
                app.Navigate("backups");
                app.Backups.AskToRestore(originalBackup, originalBackup.Files.First(file => file.Name.EndsWith(".bes")));
                await Shot("ce-backup-confirm");
                app.Backups.Confirm.Hide();
                viewport.QueueFree(); await Frame();
            }
            GD.Print("CAPTURES_DONE CE isolated screens");
            exit = 0;
        }
        catch (Exception error) { GD.PrintErr(error); }
        finally { Quit(exit); }
    }
    private async Task Frame() => await ToSignal(this, SignalName.ProcessFrame);
}
