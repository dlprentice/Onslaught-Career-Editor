using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class CliReadOnlyAndOptionsSafetyTests
{
    private static string RepoRoot => TestFixturePaths.RepoRoot;
    private static string GoldSavePath => TestFixturePaths.GoldSavePath;

    [Test]
    public void CliReadOnly_AnalyzeMode_SucceedsWithExpectedMarkers()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing fixture: {GoldSavePath}");
        var result = RunCliRaw(GoldSavePath, "--analyze");

        Assert.That(result.ExitCode, Is.EqualTo(0), result.Stderr);
        Assert.That(result.Stdout, Does.Contain("SAVE FILE ANALYSIS"));
        Assert.That(result.Stdout, Does.Contain("OPTIONS (bindings + tail snapshot)"));
    }

    [Test]
    public void CliReadOnly_CompareMode_SucceedsForIdenticalFiles()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing fixture: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-cli-compare-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string left = Path.Combine(tempDir, "left.bes");
        string right = Path.Combine(tempDir, "right.bes");

        try
        {
            File.Copy(GoldSavePath, left, true);
            File.Copy(GoldSavePath, right, true);

            var result = RunCliRaw(left, "--compare", right);
            Assert.That(result.ExitCode, Is.EqualTo(0), result.Stderr);
            Assert.That(result.Stdout, Does.Contain("COMPARISON"));
            Assert.That(result.Stdout, Does.Contain("Files are identical!"));
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void CliReadOnly_ListGoodiesMode_SucceedsWithSummary()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing fixture: {GoldSavePath}");
        var result = RunCliRaw(GoldSavePath, "--list-goodies");

        Assert.That(result.ExitCode, Is.EqualTo(0), result.Stderr);
        Assert.That(result.Stdout, Does.Contain("Onslaught Career Editor - Goodie List"));
        Assert.That(result.Stdout, Does.Contain("Summary (displayable slots 0-232):"));
    }

    [Test]
    public void CliOptionsFile_BlocksCareerSectionsByDefault()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing fixture: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-options-block-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string inputBea = Path.Combine(tempDir, "defaultoptions.bea");
        string outputBea = Path.Combine(tempDir, "defaultoptions_patched.bea");

        try
        {
            File.Copy(GoldSavePath, inputBea, true);
            var result = RunCliRaw(inputBea, outputBea, "--rank", "S");

            Assert.That(result.ExitCode, Is.Not.EqualTo(0));
            Assert.That(result.Stderr, Does.Contain("Career section patching is blocked"));
            Assert.That(File.Exists(outputBea), Is.False, "Output must not be created when options safety guard blocks.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void CliOptionsFile_SettingsOnlyMode_IsAllowed()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing fixture: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-options-settings-only-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string inputBea = Path.Combine(tempDir, "defaultoptions.bea");
        string outputBea = Path.Combine(tempDir, "defaultoptions_settings_only.bea");

        try
        {
            File.Copy(GoldSavePath, inputBea, true);
            var result = RunCliRaw(
                inputBea,
                outputBea,
                "--no-nodes",
                "--no-links",
                "--no-goodies",
                "--no-kills",
                "--sound-volume",
                "0.5");

            Assert.That(result.ExitCode, Is.EqualTo(0), result.Stderr);
            Assert.That(File.Exists(outputBea), Is.True);
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void CliOptionsFile_Override_AllowsCareerSections()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing fixture: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-options-override-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string inputBea = Path.Combine(tempDir, "defaultoptions.bea");
        string outputBea = Path.Combine(tempDir, "defaultoptions_override.bea");

        try
        {
            File.Copy(GoldSavePath, inputBea, true);
            var result = RunCliRaw(
                inputBea,
                outputBea,
                "--allow-career-sections-on-options-file",
                "--rank",
                "S",
                "--kills",
                "100");

            Assert.That(result.ExitCode, Is.EqualTo(0), result.Stderr);
            Assert.That(File.Exists(outputBea), Is.True);
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    private static CliRunResult RunCliRaw(params string[] args)
    {
        string repoRoot = RepoRoot;
        string projectPath = Path.Combine(repoRoot, "OnslaughtCareerEditor.Cli", "OnslaughtCareerEditor.Cli.csproj");
        string? dotnetExe = ResolveDotnetExe();
        if (dotnetExe == null)
            Assert.Ignore("dotnet runtime not found for CLI regression test.");

        var psi = new ProcessStartInfo
        {
            FileName = dotnetExe,
            WorkingDirectory = repoRoot,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        psi.ArgumentList.Add("run");
        psi.ArgumentList.Add("--project");
        psi.ArgumentList.Add(projectPath);
        psi.ArgumentList.Add("--");
        foreach (var arg in args)
            psi.ArgumentList.Add(arg);

        using var process = Process.Start(psi);
        Assert.That(process, Is.Not.Null, "Failed to start dotnet process.");
        var stdoutTask = process!.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();

        if (!process.WaitForExit(120_000))
        {
            try { process.Kill(entireProcessTree: true); } catch { }
            Assert.Fail("CLI process timed out after 120s.");
        }

        Task.WaitAll(stdoutTask, stderrTask);
        return new CliRunResult(process.ExitCode, stdoutTask.Result, stderrTask.Result);
    }

    private readonly struct CliRunResult(int exitCode, string stdout, string stderr)
    {
        public int ExitCode { get; } = exitCode;
        public string Stdout { get; } = stdout;
        public string Stderr { get; } = stderr;
    }

    private static string? ResolveDotnetExe()
    {
        var env = Environment.GetEnvironmentVariable("DOTNET_EXE");
        if (!string.IsNullOrWhiteSpace(env) && File.Exists(env))
            return env;

        var candidates = new[]
        {
            @"C:\\Program Files\\dotnet\\dotnet.exe",
            @"/mnt/c/Program Files/dotnet/dotnet.exe",
            "/usr/bin/dotnet",
            "/usr/local/bin/dotnet"
        };

        foreach (var candidate in candidates)
        {
            if (File.Exists(candidate))
                return candidate;
        }

        return null;
    }
}
