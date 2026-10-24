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
                "Phase must be prepare, launch, restore or settings.");
            string[] receipts = Directory.GetFiles(admitted, "unknown-result-*.json");
            Require(receipts.Length == 1, "Invalid phase produces one bounded unknown-phase receipt inside admitted owner");
            Require(Directory.GetFiles(root, "escaped*").Length == 0, "Invalid phase cannot escape owner in receipt path");
            using (JsonDocument receipt = JsonDocument.Parse(File.ReadAllText(receipts.Single())))
                Require(!receipt.RootElement.GetProperty("passed").GetBoolean(), "Invalid-phase receipt records failure");

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
        ProcessStartInfo start = new("/bin/sh") { UseShellExecute = false, RedirectStandardOutput = true };
        start.ArgumentList.Add("-c");
        start.ArgumentList.Add("sleep 30 </dev/null >/dev/null 2>&1 & echo $!; sleep 1");
        using Process parent = Process.Start(start) ?? throw new IOException("Cannot start owned dummy parent.");
        DateTime parentStarted = parent.StartTime.ToUniversalTime();
        string parentImage = parent.MainModule!.FileName;
        int childPid = int.Parse((await parent.StandardOutput.ReadLineAsync())!);
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
