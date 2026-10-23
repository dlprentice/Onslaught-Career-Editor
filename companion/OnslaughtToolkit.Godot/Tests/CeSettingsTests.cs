// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Text;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Launcher contracts and isolated ce.ini writes; no CE process, install or real player folder is used.</summary>
internal static class CeSettingsTests
{
    internal static async Task RunAsync(string outputDirectory, Checks check)
    {
        check.Suite("CE launcher and settings");
        string root = Path.Combine(outputDirectory, "ce-launcher-settings");
        Directory.CreateDirectory(root);
        string user = Path.Combine(root, "user"), home = Path.Combine(root, "home"), data = Path.Combine(root, "xdg");
        Dictionary<string, string?> environment = new(StringComparer.Ordinal);
        string? Env(string key) => environment.GetValueOrDefault(key);
        check.That(CeInstallation.ResolveUserFolder(Env, false, home).Value == Path.Combine(home, ".local", "share", "onslaught-ce"),
            "CE defaults to the Linux user-data directory, without creating it.");
        environment["XDG_DATA_HOME"] = data;
        check.That(CeInstallation.ResolveUserFolder(Env, false, home).Value == Path.Combine(data, "onslaught-ce"), "CE respects XDG_DATA_HOME.");
        environment["BEA_USER_DIR"] = user;
        check.That(CeInstallation.ResolveUserFolder(Env, false, home).Value == user, "BEA_USER_DIR takes precedence over XDG_DATA_HOME.");
        environment["BEA_USER_DIR"] = "relative-user";
        check.That(!CeInstallation.ResolveUserFolder(Env, false, home).Ok, "An unsafe relative user override is refused rather than silently ignored.");
        environment["BEA_USER_DIR"] = home;
        check.That(!CeInstallation.ResolveUserFolder(Env, false, home).Ok, "The home folder itself is not accepted as the CE user folder.");
        environment.Remove("BEA_USER_DIR");
        environment["APPDATA"] = Path.Combine(root, "roaming");
        check.That(CeInstallation.ResolveUserFolder(Env, true, home).Value == Path.Combine(root, "roaming", "Onslaught CE"),
            "Windows CE uses the documented APPDATA folder.");

        string package = Path.Combine(root, "package");
        Directory.CreateDirectory(package);
        string launcher = Path.Combine(package, "onslaught-ce"), binary = Path.Combine(package, "bea");
        File.WriteAllText(launcher, "test-only launcher marker; never run");
        File.WriteAllText(Path.Combine(package, "onslaught-ce-launch"), "test-only binary marker");
        File.WriteAllText(binary, "test-only game marker");
        environment["PATH"] = package;
        CeInstallation? installation = CeInstallation.Find(null, user, Env, false, home);
        check.That(installation?.LauncherPath == launcher && installation.UserFolder == user && !Directory.Exists(user),
            "PATH discovery reads the portable launcher package without creating the CE user folder.");
        check.That(!CeInstallation.Inspect(binary, user, false).Ok, "The underlying bea program is never accepted as the launcher.");
        check.That(CeInstallation.ParseVersion("Onslaught CE v0.1.2 (preview), build abcd1234\n").Value is { Version: "0.1.2", Build: "abcd1234" } &&
            CeInstallation.ParseVersion("Onslaught CE vdev (preview), build unknown").Ok && !CeInstallation.ParseVersion("not CE").Ok &&
            !CeInstallation.ParseVersion("Onslaught CE v0.1.2, build abc\nextra output").Ok, "Version parsing admits only a complete CE version response.");
        if (installation is not null && OperatingSystem.IsLinux())
        {
            ProcessStartInfo? requested = null;
            var version = await installation.ReadVersionAsync(read: (start, _) =>
            {
                requested = start;
                return Task.FromResult("Onslaught CE v0.1.2 (preview), build abcd1234");
            });
            check.That(version.Ok && requested?.FileName == launcher && requested.ArgumentList.SequenceEqual(["--version"]) &&
                requested.Environment["BEA_USER_DIR"] == user && !requested.UseShellExecute,
                "Version inspection requests --version first and only, with the selected user folder.");
            bool launched = false;
            check.That(installation.Launch(start =>
            {
                launched = start.FileName == launcher && start.ArgumentList.Count == 0 && start.Environment["BEA_USER_DIR"] == user;
                return true;
            }).Ok && launched, "Play starts the launcher with no direct bea invocation or update arguments.");
            File.WriteAllText(launcher, "#!/bin/sh\n[ \"$#\" = 1 ] && [ \"$1\" = --version ] || exit 23\nprintf 'Onslaught CE v0.1.2 (preview), build fixture\\n'\n");
            File.SetUnixFileMode(launcher, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
            check.That((await installation.ReadVersionAsync()).Value is { Build: "fixture" } && !Directory.Exists(user),
                "The actual version process reader captures a tiny isolated fixture script without initializing user data.");
            File.WriteAllText(launcher, "#!/bin/sh\nexec sleep 30\n");
            using CancellationTokenSource cancel = new(TimeSpan.FromMilliseconds(100));
            check.That(!(await installation.ReadVersionAsync(cancel.Token)).Ok,
                "A canceled version query terminates only its owned fixture process and returns a refusal.");
        }

        const string original = "# preserved\r\ngamedir=/original/data\r\nunknown=π\r\n update_check=0\r\nupdate_check=0\r\nupdate_check=1\r\nrecord_sessions=1\r\ncheat_malloy=1\r\nlast=keep";
        CeSettings model = CeSettings.Parse(Path.Combine(user, "ce.ini"), true, Encoding.UTF8.GetBytes(original)).Value!;
        check.That(!model.UpdateCheck && model.RecordSessions && model.GameDirectory == "/original/data", "The first exact lowercase key wins, as in the launcher.");
        byte[] prepared = model.Prepare(true, false).Value!;
        string changed = Encoding.UTF8.GetString(prepared);
        check.That(changed == "# preserved\r\ngamedir=/original/data\r\nunknown=π\r\n update_check=0\r\nupdate_check=1\r\nrecord_sessions=0\r\ncheat_malloy=1\r\nlast=keep",
            "Only editable key lines change; duplicates collapse and every unknown line and ending is retained.");
        check.That(CeSettings.Parse("unused", false, []).Value is { UpdateCheck: true, RecordSessions: false } &&
            CeSettings.Parse("unused", true, Encoding.UTF8.GetBytes("update_check=false\nrecord_sessions=true\n")).Value is { UpdateCheck: true, RecordSessions: false },
            "Defaults and noncanonical values follow the launcher's exact 0/1 comparisons.");
        foreach (byte[] bad in new byte[][] { [0xFF], [0], [0xEF, 0xBB, 0xBF, 0x61], new byte[CeSettings.MaximumBytes + 1] })
            check.That(!CeSettings.Parse("unused", true, bad).Ok, "Invalid encoding, zero bytes, BOMs and oversized settings refuse editing.");
        check.That(CeSettings.Read(user).Value is { Exists: false, UpdateCheck: true } && !Directory.Exists(user),
            "Reading defaults does not create the user folder.");

        if (!OperatingSystem.IsLinux() && !OperatingSystem.IsWindows()) return;
        Directory.CreateDirectory(user);
        string path = Path.Combine(user, "ce.ini"), backups = Path.Combine(root, "backups");
        Directory.CreateDirectory(backups);
        File.WriteAllText(path, original, new UTF8Encoding(false));
        CeSettings opened = CeSettings.Read(user).Value!;
        DateTime now = new(2026, 10, 23, 12, 0, 0);
        check.That(!opened.Save(true, false, backups, () => true, now).Ok && File.ReadAllText(path) == original && Directory.GetDirectories(backups).Length == 0,
            "Running CE refuses before creating backups or changing ce.ini.");
        check.That(!opened.Save(true, false, user, () => false, now).Ok, "Settings backups cannot be placed inside CE's user folder.");
        InstallReceipt saved = opened.Save(true, false, backups, () => false, now);
        check.That(saved.Ok && File.ReadAllBytes(path).AsSpan().SequenceEqual(prepared) && saved.BackupFolder is string folder &&
            File.ReadAllText(Path.Combine(folder, "ce.ini")) == original,
            "Settings are backed up, atomically replaced and read-back verified.");
        check.That(!opened.Save(false, true, backups, () => false, now).Ok && File.ReadAllBytes(path).AsSpan().SequenceEqual(prepared),
            "A stale settings snapshot cannot overwrite a later save.");
        CeSettings latest = CeSettings.Read(user).Value!;
        string other = "update_check=0\nrecord_sessions=1\nother=external\n";
        InstallReceipt race = latest.Save(false, true, backups, () => false, now, beforeSwap: () => File.WriteAllText(path, other));
        check.That(!race.Ok && File.ReadAllText(path) == other,
            "An in-place change immediately before publication is preserved, never silently overwritten.");
        CeSettings raceAfter = CeSettings.Read(user).Value!;
        bool running = false;
        InstallReceipt started = raceAfter.Save(true, false, backups, () => running, now, beforeSwap: () => running = true);
        check.That(!started.Ok && File.ReadAllText(path) == other, "A game start after backup refuses the settings swap.");

        string fresh = Path.Combine(root, "first-run");
        Directory.CreateDirectory(fresh);
        CeSettings first = CeSettings.Read(fresh).Value!;
        InstallReceipt created = first.Save(false, true, backups, () => false, now);
        check.That(created.Ok && !created.Replaced && created.BackupFolder is string absence && File.Exists(Path.Combine(absence, "ce.ini.did-not-exist.txt")) &&
            !File.Exists(Path.Combine(absence, "ce.ini")), "A first ce.ini gets an honest absence receipt, not a fabricated original.");
        if (OperatingSystem.IsLinux())
        {
            string linked = Path.Combine(root, "linked");
            Directory.CreateSymbolicLink(linked, user);
            check.That(!CeSettings.Read(linked).Ok, "A symbolic user-folder alias cannot be edited.");
            string linkedFile = Path.Combine(root, "linked-file");
            Directory.CreateDirectory(linkedFile);
            File.CreateSymbolicLink(Path.Combine(linkedFile, "ce.ini"), path);
            check.That(!CeSettings.Read(linkedFile).Ok, "A symbolic ce.ini alias cannot be edited.");
        }
        await CePackageSafetyTests.RunAsync(outputDirectory, check);
    }
}
