// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Text;
using System.Text.Json;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Options;

// Run natively on Windows. No platform override, injected process detector or alternate publisher.
// Every write is confined to an explicitly created disposable test root, never an install/profile.
internal static class Program
{
    private const string Marker = "Onslaught Companion disposable native acceptance v1\n";
    private const string UnicodeName = "CE Élan 日本語.bes";
    private static readonly List<object> Checks = [];
    private static readonly ProtectedSaveFiles Files = new();

    public static async Task<int> Main(string[] args)
    {
        string phase = args.FirstOrDefault() ?? "";
        try
        {
            Check(OperatingSystem.IsWindows(), "native-windows", Environment.OSVersion.ToString());
            Check(phase is "files" or "running" or "version", "phase", phase);
            Dictionary<string, string> options = [];
            for (int i = 1; i < args.Length; i += 2)
            {
                if (i + 1 >= args.Length || !args[i].StartsWith("--", StringComparison.Ordinal) ||
                    !options.TryAdd(args[i][2..], args[i + 1])) throw new ArgumentException("Expected unique --key value pairs.");
            }
            Check(options.Keys.All(key => key is "root" or "fixture" or "fixture-sha256" or "launcher" or "pid" or "expected-version"), "known-arguments", options.Keys.ToArray());
            string Get(string key) => options.TryGetValue(key, out string? value) ? value : throw new ArgumentException("Missing --" + key);
            string root = Absolute(Get("root")), fixture = Absolute(Get("fixture")), launcher = Absolute(Get("launcher"));
            string fixtureHash = Get("fixture-sha256").ToLowerInvariant();
            Check(fixtureHash.Length == 64 && fixtureHash.All(Uri.IsHexDigit), "fixture-pin", fixtureHash);
            FileMutationSafety.RejectExistingReparseAncestors(root, "test root");
            string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            Check(!root.Equals(Path.TrimEndingDirectorySeparator(Path.GetPathRoot(root)!), StringComparison.OrdinalIgnoreCase) && !Inside(root, home) && !Inside(home, root), "outside-real-profile", root);
            Check(!Inside(root, Path.GetDirectoryName(launcher)!) && !Inside(Path.GetDirectoryName(launcher)!, root),
                "separate-package", launcher);
            Check(!Inside(fixture, root), "external-fixture", fixture);
            byte[] original = File.ReadAllBytes(fixture);
            Check(SaveSession.Digest(original) == fixtureHash && CareerSave.Inspect(original).Ok, "real-career-pin", fixtureHash);
            string marker = Path.Combine(root, "native-check.marker");
            if (phase == "files")
            {
                Check(!Directory.Exists(root) && !File.Exists(root), "fresh-root", root);
                Directory.CreateDirectory(root);
                File.WriteAllText(marker, Marker);
            }
            else Check(File.ReadAllText(marker) == Marker, "owned-root", root);
            string user = Path.Combine(root, "user"), backups = Path.Combine(root, "backups");
            Environment.SetEnvironmentVariable("BEA_USER_DIR", user);
            Environment.SetEnvironmentVariable("APPDATA", Path.Combine(root, "profile"));
            CeInstallation ce = Need(CeInstallation.Inspect(launcher, user));
            Check(Need(CeInstallation.ResolveUserFolder()) == user, "native-user-folder", user);
            GameFolder Game() => GameFolder.InspectCe(user, assetRoot: "", originalRoot: "", packageRoot: ce.Folder);
            string career = Path.Combine(user, "savegames", "baseline.bes");
            byte[] edited = Need(CareerSave.Preview(original, new Dictionary<int, int>
                { [0] = (CareerSave.Inspect(original).Value!.Kills[0] + 123) % CareerSave.MaxKills })).CopyBytes();
            Check(!edited.AsSpan().SequenceEqual(original), "nonempty-edit", SaveSession.Digest(edited));
            Check(Enumerable.Range(0, original.Length).All(i => i >= CareerSave.KillsOffset && i < CareerSave.KillsOffset + 3 ||
                original[i] == edited[i]), "unknown-bytes-preserved", "Only the selected three kill-counter bytes may differ.");
            if (phase == "files")
            {
                Check(!GameProcess.IsRunning(), "game-stopped", GameProcess.Running());
                Directory.CreateDirectory(Path.GetDirectoryName(career)!);
                Directory.CreateDirectory(backups);
                File.Copy(fixture, career, false);
                SaveSession opened = Need(SaveSession.FromRead(Files.OpenCareer(career)));
                Check(opened.Sha256 == fixtureHash, "protected-open", new { opened.Identity, opened.Sha256 });
                InstallReceipt edit = GameInstaller.Install(Files, Game(), "baseline.bes", edited, backups,
                    GameProcess.IsRunning, DateTime.Now, expectedSha256: opened.Sha256);
                Check(edit.Ok && edit.Replaced && !edit.MayHaveChanged, "verified-edit", edit);
                Check(Need(SaveSession.FromRead(Files.OpenCareer(career))).Matches(edited), "edit-reopen", SaveSession.Digest(File.ReadAllBytes(career)));
                Check(edit.BackupFolder is not null && File.ReadAllBytes(Path.Combine(edit.BackupFolder, "baseline.bes")).AsSpan().SequenceEqual(original),
                    "verified-original-backup", edit.BackupFolder);
                string unicode = Path.Combine(user, "savegames", UnicodeName);
                InstallReceipt named = GameInstaller.Install(Files, Game(), UnicodeName, edited, backups, GameProcess.IsRunning, DateTime.Now);
                Check(named.Ok && Need(SaveSession.FromRead(Files.OpenCareer(unicode))).Matches(edited), "unicode-publication", named);
                Check(Game().Careers.Any(file => file.Name == UnicodeName && file.Supported), "unicode-discovery", UnicodeName);
                InstallReceipt stale = GameInstaller.Install(Files, Game(), "baseline.bes", original, backups,
                    GameProcess.IsRunning, DateTime.Now, expectedSha256: opened.Sha256);
                Check(!stale.Ok && !stale.MayHaveChanged && File.ReadAllBytes(career).AsSpan().SequenceEqual(edited), "stale-install-refusal", stale);
                string rejected = Path.Combine(root, "stale-output.bes");
                PublicationReceipt publication = Files.PublishCopy(career, opened.Identity, opened.Sha256, rejected, original);
                Check(!publication.Ok && !publication.MayHaveOutput && !File.Exists(rejected), "stale-copy-refusal", publication);
                using (FileStream locked = new(career, FileMode.Open, FileAccess.Read, FileShare.None))
                    Check(!Files.OpenCareer(career).Ok, "windows-sharing-refusal", "OpenCareer refused a file held with FileShare.None.");
                byte[] restoredBytes = File.ReadAllBytes(Path.Combine(edit.BackupFolder!, "baseline.bes"));
                InstallReceipt restored = GameInstaller.Install(Files, Game(), "baseline.bes", restoredBytes, backups,
                    GameProcess.IsRunning, DateTime.Now, expectedSha256: SaveSession.Digest(edited), reason: "Native check restore");
                Check(restored.Ok && Need(SaveSession.FromRead(Files.OpenCareer(career))).Matches(original), "backup-restore-reopen", restored);
                Settings(ce, backups);
            }
            else if (phase == "running")
            {
                int pid = int.Parse(Get("pid"));
                using Process process = Process.GetProcessById(pid);
                string image = process.MainModule?.FileName ?? "";
                Check(!process.HasExited && Path.GetFullPath(image).Equals(Path.Combine(ce.Folder, "bea.exe"), StringComparison.OrdinalIgnoreCase),
                    "actual-ce-image", new { pid, image });
                IReadOnlyList<string> running = GameProcess.Running();
                Check(running.Any(line => line.StartsWith(pid + ":", StringComparison.Ordinal)) && GameProcess.IsRunning(), "actual-ce-detected", running);
                byte[] before = File.ReadAllBytes(career), settingsBefore = File.ReadAllBytes(ce.SettingsPath);
                string[] backupBefore = Directory.GetDirectories(backups).Order().ToArray();
                InstallReceipt refused = GameInstaller.Install(Files, Game(), "baseline.bes", edited, backups, GameProcess.IsRunning,
                    DateTime.Now, expectedSha256: SaveSession.Digest(before));
                Check(!refused.Ok && refused.Message == GameInstaller.RunningMessage && !refused.MayHaveChanged && refused.BackupFolder is null &&
                    File.ReadAllBytes(career).AsSpan().SequenceEqual(before), "running-career-refusal", refused);
                CeSettings settings = Need(CeSettings.Read(user));
                InstallReceipt settingsRefused = settings.Save(!settings.UpdateCheck, !settings.RecordSessions, backups,
                    GameProcess.IsRunning, DateTime.Now, packageRoot: ce.Folder);
                Check(!settingsRefused.Ok && settingsRefused.Message == GameInstaller.RunningMessage && !settingsRefused.MayHaveChanged && settingsRefused.BackupFolder is null &&
                    File.ReadAllBytes(ce.SettingsPath).AsSpan().SequenceEqual(settingsBefore), "running-settings-refusal", settingsRefused);
                Check(backupBefore.SequenceEqual(Directory.GetDirectories(backups).Order()), "running-no-backup-write", backups);
            }
            else
            {
                CeVersion version = Need(await ce.ReadVersionAsync());
                Check(version.Version == Get("expected-version"), "redirected-launcher-version", version);
            }
            Check(SaveSession.Digest(File.ReadAllBytes(fixture)) == fixtureHash, "fixture-unchanged", fixtureHash);
            Console.WriteLine(JsonSerializer.Serialize(new { ok = true, phase, runtime = Environment.Version.ToString(), checks = Checks }, JsonOptions));
            return 0;
        }
        catch (Exception error)
        {
            Console.WriteLine(JsonSerializer.Serialize(new { ok = false, phase, error = error.ToString(), checks = Checks }, JsonOptions));
            return 1;
        }
    }

    private static void Settings(CeInstallation ce, string backups)
    {
        string text = "# private native check\r\nfuture_key=Élan\r\nupdate_check=0\r\nrecord_sessions=0\r\n";
        byte[] before = Encoding.UTF8.GetBytes(text);
        File.WriteAllBytes(ce.SettingsPath, before);
        CeSettings first = Need(CeSettings.Read(ce.UserFolder));
        byte[] expected = Need(first.Prepare(updateCheck: true, recordSessions: true));
        InstallReceipt saved = first.Save(true, true, backups, GameProcess.IsRunning, DateTime.Now, packageRoot: ce.Folder);
        Check(saved.Ok && File.ReadAllBytes(ce.SettingsPath).AsSpan().SequenceEqual(expected) &&
            File.ReadAllBytes(Path.Combine(saved.BackupFolder!, "ce.ini")).AsSpan().SequenceEqual(before), "settings-save-backup-reopen", saved);
        Check(Encoding.UTF8.GetString(expected).Contains("future_key=Élan\r\n", StringComparison.Ordinal), "settings-unknown-key-preserved", ce.SettingsPath);
        InstallReceipt stale = first.Save(false, false, backups, GameProcess.IsRunning, DateTime.Now, packageRoot: ce.Folder);
        Check(!stale.Ok && !stale.MayHaveChanged && File.ReadAllBytes(ce.SettingsPath).AsSpan().SequenceEqual(expected), "settings-stale-refusal", stale);
        // Leave update checks disabled in the copied profile before the lead launches CE in the offline VM.
        CeSettings current = Need(CeSettings.Read(ce.UserFolder));
        InstallReceipt final = current.Save(false, true, backups, GameProcess.IsRunning, DateTime.Now, packageRoot: ce.Folder);
        Check(final.Ok && !Need(CeSettings.Read(ce.UserFolder)).UpdateCheck, "private-profile-offline", final);
    }

    private static readonly JsonSerializerOptions JsonOptions = new() { WriteIndented = true };
    private static T Need<T>(Outcome<T> value) where T : class => value.Ok && value.Value is T result ? result : throw new InvalidOperationException(value.Message);
    private static void Check(bool pass, string name, object? detail)
    {
        Checks.Add(new { name, pass, detail });
        if (!pass) throw new InvalidOperationException(name + " failed");
    }
    private static string Absolute(string value) => Path.IsPathFullyQualified(value) ? Path.TrimEndingDirectorySeparator(Path.GetFullPath(value)) :
        throw new ArgumentException("All paths must be absolute.");
    private static bool Inside(string path, string folder) => path.Equals(folder, StringComparison.OrdinalIgnoreCase) ||
        path.StartsWith(Path.TrimEndingDirectorySeparator(folder) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase);
}
