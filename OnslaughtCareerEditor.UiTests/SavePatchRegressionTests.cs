using System;
using System.Buffers.Binary;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class SavePatchRegressionTests
{
    private static string RepoRoot => TestFixturePaths.RepoRoot;
    private static string GoldSavePath => TestFixturePaths.GoldSavePath;

    [Test]
    public void PatchFile_WritesTailSettingsAtCorrectOffsets_WithNormalBooleanPolarity()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-regression-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);

            var patcher = new BesFilePatcher
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,

                InvertYAxisP1Override = true,
                InvertYAxisP2Override = false,
                InvertFlightP1Override = false,
                InvertFlightP2Override = true,
                VibrationP1Override = true,
                VibrationP2Override = false,
                ControllerConfigP1Override = 123u,
                ControllerConfigP2Override = 456u,
            };

            var result = patcher.PatchFile(input, output);
            Assert.That(result.Success, Is.True, result.Message);

            byte[] buf = File.ReadAllBytes(output);
            AssertUInt(buf, 0x249E, 0u, "Invert Y (Flight) P1 should write OFF as 0");
            AssertUInt(buf, 0x24A2, 1u, "Invert Y (Flight) P2 should write ON as 1");

            AssertUInt(buf, 0x24A6, 1u, "Invert Y (Walker) P1 should write ON as 1");
            AssertUInt(buf, 0x24AA, 0u, "Invert Y (Walker) P2 should write OFF as 0");

            AssertUInt(buf, 0x24AE, 1u, "Controller vibration P1 should write ON as 1");
            AssertUInt(buf, 0x24B2, 0u, "Controller vibration P2 should write OFF as 0");

            AssertUInt(buf, 0x24B6, 123u, "Controller config P1 should be written at 0x24B6");
            AssertUInt(buf, 0x24BA, 456u, "Controller config P2 should be written at 0x24BA");
        }
        finally
        {
            if (Directory.Exists(tempDir))
            {
                Directory.Delete(tempDir, recursive: true);
            }
        }
    }

    [Test]
    public void Cli_LevelRank_OneTargetsFirstNode_NotSecondNode()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-levelrank-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            EnsureNodeIsActive(input, 0);
            EnsureNodeIsActive(input, 1);

            string baselineOutput = Path.Combine(tempDir, "baseline_patch.bes");
            int baselineExitCode = RunCliSuccess(input, baselineOutput, "--rank", "E", "--no-links", "--no-goodies", "--no-kills");
            Assert.That(baselineExitCode, Is.EqualTo(0), "CLI baseline patch run failed");

            int exitCode = RunCliSuccess(input, output, "--rank", "E", "--level-rank", "1:S", "--no-links", "--no-goodies", "--no-kills");

            Assert.That(exitCode, Is.EqualTo(0), "CLI patch run failed");
            Assert.That(File.Exists(output), Is.True, "Output file was not written");

            byte[] baselineBuf = File.ReadAllBytes(baselineOutput);
            byte[] buf = File.ReadAllBytes(output);

            // True-view node base starts at file 0x0006.
            // Node 0 ranking offset: 0x0006 + (0 * 64) + 0x3C = 0x0042
            // Node 1 ranking offset: 0x0006 + (1 * 64) + 0x3C = 0x0082
            uint baselineNode1 = ReadUInt32(baselineBuf, 0x0082);
            uint node0 = ReadUInt32(buf, 0x0042);
            uint node1 = ReadUInt32(buf, 0x0082);

            Assert.That(node0, Is.EqualTo(0x3F800000u), "--level-rank 1:S must target node index 0");
            Assert.That(node1, Is.EqualTo(baselineNode1), "Node index 1 should not be touched by --level-rank 1:S");
        }
        finally
        {
            if (Directory.Exists(tempDir))
            {
                Directory.Delete(tempDir, recursive: true);
            }
        }
    }

    [Test]
    public void Cli_InvalidLevelRankEntry_FailsAndDoesNotWriteOutput()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-levelrank-invalid-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output_invalid_rank.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            var result = RunCliRaw(input, output, "--level-rank", "bad", "--no-links", "--no-goodies", "--no-kills");
            Assert.That(result.ExitCode, Is.Not.EqualTo(0), "CLI should fail for invalid --level-rank input.");
            Assert.That(result.Stderr, Does.Contain("Invalid --level-rank entry").IgnoreCase);
            Assert.That(File.Exists(output), Is.False, "Output file must not be written when CLI validation fails.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void Cli_CopyOptionsFromWithBothNoCopyFlags_FailsAndDoesNotWriteOutput()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-copy-options-invalid-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output_invalid_copy_options.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            var result = RunCliRaw(
                input,
                output,
                "--copy-options-from", input,
                "--no-copy-options-entries",
                "--no-copy-options-tail");
            Assert.That(result.ExitCode, Is.Not.EqualTo(0), "CLI should fail when both no-copy options are set.");
            Assert.That(result.Stderr, Does.Contain("both --no-copy-options-entries and --no-copy-options-tail").IgnoreCase);
            Assert.That(File.Exists(output), Is.False, "Output file must not be written when copy-options validation fails.");
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void PatchFile_RejectsInPlaceOutputPath()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-inplace-guard-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            var patcher = new BesFilePatcher
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = false,
            };

            var result = patcher.PatchFile(input, input);
            Assert.That(result.Success, Is.False, "Patcher must reject in-place writes.");
            Assert.That(result.Message, Does.Contain("Refusing to patch in place").IgnoreCase);
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void TryParseKeyboardPackedKey_AcceptsRawFallbackToken()
    {
        bool ok = BesFilePatcher.TryParseKeyboardPackedKey(
            "vk=0x0000 scan=0x0027",
            out uint packed,
            out string? error);

        Assert.That(ok, Is.True, error ?? "Expected parser success.");
        Assert.That(packed, Is.EqualTo(0x00000027u));
    }

    [Test]
    public void FormatBinding_FallbackToken_RoundTripsThroughParser()
    {
        const uint originalPacked = 0xABCD1234u;
        string token = BesFilePatcher.FormatBinding(deviceCode: 9u, packedKey: originalPacked, entryId: 0x1F);

        Assert.That(token, Is.EqualTo("vk=0xABCD scan=0x1234"));

        bool ok = BesFilePatcher.TryParseKeyboardPackedKey(token, out uint parsedPacked, out string? error);
        Assert.That(ok, Is.True, error ?? "Expected parser success.");
        Assert.That(parsedPacked, Is.EqualTo(originalPacked));
    }

    [Test]
    public void PatchFile_GoodiesBoundary_PatchesSlot232_AndPreservesReservedSlots()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-goodies-boundary-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output.bes");

        try
        {
            File.Copy(GoldSavePath, input, true);
            byte[] before = File.ReadAllBytes(input);

            var patcher = new BesFilePatcher
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = true,
                PatchKills = false,
                UseNewGoodiesInstead = false,
            };

            var result = patcher.PatchFile(input, output);
            Assert.That(result.Success, Is.True, result.Message);

            byte[] after = File.ReadAllBytes(output);
            int slot232Off = 0x1F46 + (232 * 4);
            AssertUInt(after, slot232Off, 3u, "Displayable goodie slot 232 should be unlocked as OLD");

            for (int idx = 233; idx < 300; idx++)
            {
                int off = 0x1F46 + (idx * 4);
                uint oldRaw = ReadUInt32(before, off);
                uint newRaw = ReadUInt32(after, off);
                Assert.That(newRaw, Is.EqualTo(oldRaw), $"Reserved goodie slot {idx} changed unexpectedly.");
            }
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    [Test]
    public void PatchFile_KillPatch_PreservesMetaHighByte()
    {
        Assert.That(File.Exists(GoldSavePath), Is.True, $"Missing baseline save: {GoldSavePath}");

        string tempDir = Path.Combine(Path.GetTempPath(), $"onslaught-killmeta-{Guid.NewGuid():N}");
        Directory.CreateDirectory(tempDir);
        string input = Path.Combine(tempDir, "input.bes");
        string output = Path.Combine(tempDir, "output.bes");

        try
        {
            byte[] buf = File.ReadAllBytes(GoldSavePath);
            byte[] seededMeta = new byte[] { 0xA1, 0xB2, 0xC3, 0xD4, 0xE5 };
            for (int i = 0; i < seededMeta.Length; i++)
            {
                int off = 0x23F6 + (i * 4);
                uint seeded = ((uint)seededMeta[i] << 24) | 7u;
                BinaryPrimitives.WriteUInt32LittleEndian(buf.AsSpan(off, 4), seeded);
            }
            File.WriteAllBytes(input, buf);

            var patcher = new BesFilePatcher
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = true,
                GlobalKillCount = 123,
            };

            var result = patcher.PatchFile(input, output);
            Assert.That(result.Success, Is.True, result.Message);

            byte[] after = File.ReadAllBytes(output);
            for (int i = 0; i < seededMeta.Length; i++)
            {
                int off = 0x23F6 + (i * 4);
                uint raw = ReadUInt32(after, off);
                Assert.That((raw >> 24) & 0xFFu, Is.EqualTo((uint)seededMeta[i]), $"Meta byte changed for kill slot {i}.");
                Assert.That(raw & 0x00FFFFFFu, Is.EqualTo(123u), $"Kill payload mismatch for slot {i}.");
            }
        }
        finally
        {
            if (Directory.Exists(tempDir))
                Directory.Delete(tempDir, recursive: true);
        }
    }

    private static void AssertUInt(byte[] buf, int offset, uint expected, string message)
    {
        uint actual = ReadUInt32(buf, offset);
        Assert.That(actual, Is.EqualTo(expected),
            $"{message}. offset=0x{offset:X4}, expected=0x{expected:X8}, actual=0x{actual:X8}");
    }

    private static uint ReadUInt32(byte[] buf, int offset)
    {
        return BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(offset, 4));
    }

    private static int RunCliSuccess(params string[] args)
    {
        var result = RunCliRaw(args);
        if (result.ExitCode != 0)
        {
            Assert.Fail($"CLI failed with exit code {result.ExitCode}\\nSTDOUT:\\n{result.Stdout}\\nSTDERR:\\n{result.Stderr}");
        }

        return result.ExitCode;
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

    private static void EnsureNodeIsActive(string filePath, int nodeIndex)
    {
        byte[] buf = File.ReadAllBytes(filePath);
        int nodeBase = 0x0006 + (nodeIndex * 64);
        int worldOffset = nodeBase + 0x10;
        WriteUInt32(buf, worldOffset, 1u);
        File.WriteAllBytes(filePath, buf);
    }

    private static void WriteUInt32(byte[] buf, int offset, uint value)
    {
        BinaryPrimitives.WriteUInt32LittleEndian(buf.AsSpan(offset, 4), value);
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
