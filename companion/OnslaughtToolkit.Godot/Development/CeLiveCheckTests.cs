// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using System.Text.Json;
using Godot;
using OnslaughtToolkit.Companion.Files;
using Environment = System.Environment;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>Opt-in Linux failure-path checks for CeLiveCheck. Uses private empty directories and owned sleep
/// processes only; never launches a game. Run through companion_godot.py test --script Development/CeLiveCheckTests.cs.</summary>
public partial class CeLiveCheckTests : SceneTree
{
    private int _checks;

    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exit = 1;
        try
        {
            if (!OperatingSystem.IsLinux()) throw new IOException("This owned-process check is Linux-only.");
            string output = OS.GetCmdlineUserArgs().Single(arg => arg.StartsWith("--output-dir="))[13..];
            string root = Path.Combine(output, "ce-hook-negatives");
            Directory.CreateDirectory(root);
            string unadmitted = Path.Combine(root, "unadmitted");
            Directory.CreateDirectory(unadmitted);
            await RefuseConfiguration(root, "unadmitted", new { owner = unadmitted }, "Prepared isolated owner marker required.");
            Require(!Directory.EnumerateFileSystemEntries(unadmitted).Any(), "Unadmitted owner receives no files or receipt");

            string admitted = Path.Combine(root, "admitted");
            Directory.CreateDirectory(admitted);
            File.WriteAllText(Path.Combine(admitted, ".companion-owned"), "Owned failure-path test\n");
            await RefuseConfiguration(root, "invalid-phase", new { owner = admitted, phase = "../escaped" },
                "Phase must be prepare, launch, restore, settings or workflow.");
            string[] receipts = Directory.GetFiles(admitted, "unknown-result-*.json");
            Require(receipts.Length == 1, "Invalid phase produces one bounded unknown-phase receipt inside admitted owner");
            Require(Directory.GetFiles(root, "escaped*").Length == 0, "Invalid phase cannot escape owner in receipt path");
            using (JsonDocument receipt = JsonDocument.Parse(File.ReadAllText(receipts.Single())))
                Require(!receipt.RootElement.GetProperty("passed").GetBoolean(), "Invalid-phase receipt records failure");
            WorkflowAdmission(root);
            await WorkflowControls(root);

            await ParentExitCleanup(root);
            InstallReceipt refused = new(false, GameInstaller.RunningMessage, "unused");
            Require(CeLiveCheck.IsRunningRefusal(refused), "Specific safe running refusal admitted");
            Require(!CeLiveCheck.IsRunningRefusal(refused with { Message = "Different failure" }), "Unrelated failure rejected");
            Require(!CeLiveCheck.IsRunningRefusal(refused with { MayHaveChanged = true }), "Changed-target warning rejected");
            Require(!CeLiveCheck.IsRunningRefusal(refused with { BackupFolder = "unexpected" }), "Unexpected backup rejected");
            Require(!CeLiveCheck.IsRunningRefusal(refused with { Ok = true }), "Successful receipt rejected as refusal");
            exit = 0;
        }
        catch (Exception error) { GD.PrintErr(error); }
        GD.Print($"CE_HOOK_NEGATIVES checks={_checks} exit={exit}");
        Quit(exit);
    }

    private void WorkflowAdmission(string root)
    {
        string fixture = OS.GetCmdlineUserArgs().Single(arg => arg.StartsWith("--fixture="))[10..];
        string launcher = Path.Combine(root, "launcher-marker"), baseline = Path.Combine(root, "baseline.bes"), career = Path.Combine(root, "career.bes");
        File.WriteAllText(launcher, "owned inert launcher marker; never executed");
        File.Copy(fixture, baseline); File.Copy(fixture, career);
        string launcherHash = Careers.SaveSession.Digest(File.ReadAllBytes(launcher)), baselineHash = Careers.SaveSession.Digest(File.ReadAllBytes(baseline));
        void Admit(string version, string launchHash, string careerHash)
        {
            using JsonDocument config = JsonDocument.Parse(JsonSerializer.Serialize(new
                { expectedVersion = version, launcherSha256 = launchHash, baselineSha256 = careerHash }));
            CeLiveCheck.AdmitWorkflow(config.RootElement, launcher, baseline, career);
        }
        void Refuse(Action action, string label)
        {
            try { action(); throw new InvalidOperationException("Incorrectly admitted: " + label); }
            catch (IOException) { Require(true, label); }
        }
        Admit("0.1.5", launcherHash, baselineHash);
        Require(true, "Pinned workflow baseline, career and launcher hashes admitted without executing a launcher");
        Refuse(() => Admit("", launcherHash, baselineHash), "Missing expected version refused before UI initialization");
        Refuse(() => Admit("0.1.5", new string('0', 64), baselineHash), "Changed selected launcher refused before UI initialization");
        Refuse(() => Admit("0.1.5", launcherHash, new string('0', 64)), "Changed baseline hash refused before UI initialization");
        File.AppendAllText(career, "changed");
        Refuse(() => Admit("0.1.5", launcherHash, baselineHash), "Changed initial copied career refused before UI initialization");
        File.Copy(fixture, career, true);
        File.WriteAllBytes(baseline, new byte[10004]);
        File.Copy(baseline, career, true);
        Refuse(() => Admit("0.1.5", launcherHash, Careers.SaveSession.Digest(File.ReadAllBytes(baseline))), "Unsupported career container refused even with matching hashes");
    }

    private async Task WorkflowControls(string root)
    {
        if (!OperatingSystem.IsLinux()) throw new IOException("The owned shell-launcher control is Linux-only.");
        string fixture = OS.GetCmdlineUserArgs().Single(arg => arg.StartsWith("--fixture="))[10..];
        string owner = Path.Combine(root, "workflow-controls");
        Directory.CreateDirectory(owner);
        File.WriteAllText(Path.Combine(owner, ".companion-owned"), "Owned workflow-control root\n");
        Tests.FakeInstall install = Tests.FakeInstall.Create(Path.Combine(owner, "original"), File.ReadAllBytes(fixture));
        string package = Path.Combine(owner, "package"), user = Path.Combine(owner, "user"), backups = Path.Combine(owner, "backups");
        Directory.CreateDirectory(package); Directory.CreateDirectory(backups); Directory.CreateDirectory(Path.Combine(user, "savegames"));
        string launcher = Path.Combine(package, "onslaught-ce"), baseline = Path.Combine(owner, "baseline.bes");
        File.WriteAllText(launcher, "#!/bin/sh\n[ \"$#\" = 1 ] && [ \"$1\" = --version ] || exit 23\nprintf 'Onslaught CE v0.1.7, build workflow-fixture\\n'\n");
        File.SetUnixFileMode(launcher, UnixFileMode.UserRead | UnixFileMode.UserWrite | UnixFileMode.UserExecute);
        File.WriteAllText(Path.Combine(package, "onslaught-ce-launch"), "Owned inert package marker; never executed");
        File.WriteAllText(Path.Combine(package, "README.txt"), "Onslaught CE 0.1.7 (preview)\n");
        File.Copy(fixture, baseline); File.Copy(fixture, Path.Combine(user, "savegames", "Companion Pilot.bes"));
        File.WriteAllText(Path.Combine(user, "ce.ini"), "update_check=0\nrecord_sessions=0\nfuture_kept=acceptance\n");
        string path = Path.Combine(root, "workflow-controls.json");
        File.WriteAllText(path, JsonSerializer.Serialize(new { owner, phase = "workflow", launcher, user, baseline, backups,
            game = install.Game, expectedVersion = "0.1.7", launcherSha256 = Careers.SaveSession.Digest(File.ReadAllBytes(launcher)),
            baselineSha256 = Careers.SaveSession.Digest(File.ReadAllBytes(baseline)) }));
        ProcessStartInfo start = new(Environment.GetEnvironmentVariable("ONSLAUGHT_GODOT_HEADLESS") ??
            throw new IOException("ONSLAUGHT_GODOT_HEADLESS wrapper is required."))
        { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true };
        start.ArgumentList.Add("--path"); start.ArgumentList.Add(ProjectSettings.GlobalizePath("res://"));
        start.ArgumentList.Add("--script"); start.ArgumentList.Add("res://Development/CeLiveCheck.cs");
        start.Environment["ONSLAUGHT_CE_LIVE_CHECK"] = path;
        using Process child = Process.Start(start) ?? throw new IOException("Cannot start bounded headless workflow control.");
        Task<string> stdout = child.StandardOutput.ReadToEndAsync(), stderr = child.StandardError.ReadToEndAsync();
        await child.WaitForExitAsync();
        string transcript = await stdout + await stderr;
        File.WriteAllText(Path.Combine(root, "workflow-controls.log"), transcript);
        Require(child.ExitCode == 0, "Fixture workflow completed its production UI-control edit/settings/restore path");
        using JsonDocument result = JsonDocument.Parse(File.ReadAllText(Directory.GetFiles(owner, "workflow-result-*.json").Single()));
        Require(result.RootElement.GetProperty("passed").GetBoolean() && result.RootElement.GetProperty("phase").GetString() == "workflow",
            "Fixture workflow emitted a successful explicit workflow receipt; no real CE/game/Windows claim");
        Require(File.ReadAllBytes(Path.Combine(user, "savegames", "Companion Pilot.bes")).AsSpan().SequenceEqual(File.ReadAllBytes(fixture)),
            "Fixture workflow finished with byte-exact restored career");
        Dictionary<string, object> rendering = JsonSerializer.Deserialize<Dictionary<string, object>>(File.ReadAllText(path))!;
        rendering["capture"] = true;
        await RefuseConfiguration(root, "workflow-rendering-required", rendering,
            "Workflow screenshots require rendering; headless execution cannot establish visual acceptance.");
        rendering["capture"] = false;
        rendering["expectedVersion"] = "0.1.6-wrong-fixture";
        await RefuseConfiguration(root, "workflow-wrong-version", rendering,
            "Actual selected launcher version equals the pinned expected version");
        Require(File.ReadAllBytes(Path.Combine(user, "savegames", "Companion Pilot.bes")).AsSpan().SequenceEqual(File.ReadAllBytes(fixture)),
            "Wrong actual version refuses before workflow career edits");
    }

    private async Task RefuseConfiguration(string root, string label, object configuration, string expectedError)
    {
        string path = Path.Combine(root, label + ".json");
        File.WriteAllText(path, JsonSerializer.Serialize(configuration));
        ProcessStartInfo start = new(Environment.GetEnvironmentVariable("ONSLAUGHT_GODOT_HEADLESS") ??
            throw new IOException("ONSLAUGHT_GODOT_HEADLESS wrapper is required."))
        { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true };
        start.ArgumentList.Add("--path"); start.ArgumentList.Add(ProjectSettings.GlobalizePath("res://"));
        start.ArgumentList.Add("--script"); start.ArgumentList.Add("res://Development/CeLiveCheck.cs");
        start.Environment["ONSLAUGHT_CE_LIVE_CHECK"] = path;
        using Process process = Process.Start(start) ?? throw new IOException("Cannot start bounded headless child.");
        Task<string> stdout = process.StandardOutput.ReadToEndAsync(), stderr = process.StandardError.ReadToEndAsync();
        // Config admission runs before any CE launch or UI construction. The outer test runner supplies its timeout.
        await process.WaitForExitAsync();
        string transcript = await stdout + await stderr;
        File.WriteAllText(Path.Combine(root, label + ".log"), transcript);
        Require(process.ExitCode == 1 && transcript.Contains(expectedError), label + " refused for the expected reason");
    }

    private async Task ParentExitCleanup(string root)
    {
        ProcessStartInfo start = new("/bin/sh") { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardInput = true };
        start.ArgumentList.Add("-c");
        start.ArgumentList.Add("sleep 30 </dev/null >/dev/null 2>&1 & echo $!; read finish");
        using Process parent = Process.Start(start) ?? throw new IOException("Cannot start owned dummy parent.");
        // The echo proves that /bin/sh finished exec before its MainModule is inspected. Hold it until both
        // exact identities are observed instead of racing startup or assuming a one-second observation budget.
        int childPid = int.Parse((await parent.StandardOutput.ReadLineAsync())!);
        DateTime parentStarted = parent.StartTime.ToUniversalTime();
        string parentImage = parent.MainModule?.FileName ?? throw new IOException("Owned dummy parent image was not observed.");
        DateTime childStarted = default;
        string childImage = "";
        List<object> observations = [];
        void Observe(string label, object value) => observations.Add(new { label, value });
        try
        {
            Stopwatch wait = Stopwatch.StartNew();
            while (wait.Elapsed < TimeSpan.FromSeconds(3))
            {
                using Process child = Process.GetProcessById(childPid);
                if (Path.GetFileName(child.MainModule?.FileName) == "sleep")
                { childStarted = child.StartTime.ToUniversalTime(); childImage = child.MainModule!.FileName; break; }
                await Task.Delay(10);
            }
            Require(childImage.Length > 0, "Recorded owned dummy child's PID, executable and start time after exec");
            await parent.StandardInput.WriteLineAsync("finish");
            parent.StandardInput.Close();
            await parent.WaitForExitAsync().WaitAsync(TimeSpan.FromSeconds(5));
            Require(parent.HasExited && Alive(childPid), "Owned parent exited while owned child remains running");

            await CeLiveCheck.CleanupOwned(parent, parentStarted, parentImage,
                new Dictionary<int, (DateTime, string)> { [childPid] = (childStarted, childImage + ".wrong") }, Observe);
            Require(Alive(childPid), "Wrong executable identity refuses cleanup despite parent exit");
            await CeLiveCheck.CleanupOwned(parent, parentStarted, parentImage,
                new Dictionary<int, (DateTime, string)> { [childPid] = (childStarted.AddSeconds(-1), childImage) }, Observe);
            Require(Alive(childPid), "Wrong start-time identity refuses cleanup despite parent exit");
            await CeLiveCheck.CleanupOwned(parent, parentStarted, parentImage,
                new Dictionary<int, (DateTime, string)> { [childPid] = (childStarted, childImage) }, Observe);
            Require(!Alive(childPid), "Exact owned child cleaned after its parent exited");
        }
        finally
        {
            if (childImage.Length > 0)
                await CeLiveCheck.CleanupOwned(parent, parentStarted, parentImage,
                    new Dictionary<int, (DateTime, string)> { [childPid] = (childStarted, childImage) }, Observe);
            File.WriteAllText(Path.Combine(root, "owned-cleanup.json"), JsonSerializer.Serialize(observations,
                new JsonSerializerOptions { WriteIndented = true }));
        }
    }

    private static bool Alive(int pid)
    {
        try { using Process process = Process.GetProcessById(pid); return !process.HasExited; }
        catch (ArgumentException) { return false; }
    }

    private void Require(bool condition, string label)
    {
        if (!condition) throw new IOException(label);
        _checks++;
        GD.Print("CE_HOOK_PASS " + label);
    }
}
