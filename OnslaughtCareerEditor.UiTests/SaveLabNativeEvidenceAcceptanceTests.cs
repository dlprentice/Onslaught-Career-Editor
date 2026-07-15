using System.Drawing;
using System.Drawing.Imaging;
using System.Security.Cryptography;
using System.Text.Json;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class SaveLabNativeEvidenceAcceptanceTests
{
    private string _root = null!;
    private string _staging = null!;
    private string _accepted = null!;

    [SetUp]
    public void SetUp()
    {
        _root = Path.Combine(Path.GetTempPath(), $"save-lab-evidence-{Guid.NewGuid():N}");
        _staging = Path.Combine(_root, ".save-lab-fixture.partial");
        _accepted = Path.Combine(_root, "save-lab-fixture");
        Directory.CreateDirectory(_staging);
    }

    [TearDown]
    public void TearDown()
    {
        if (Directory.Exists(_root))
        {
            Directory.Delete(_root, recursive: true);
        }
    }

    [Test]
    public void Validate_AcceptsExactCompleteEvidenceSet()
    {
        SaveLabAcceptanceManifest manifest = SaveLabNativeEvidenceTestFactory.CreateValid(_staging);

        Assert.DoesNotThrow(() => SaveLabNativeEvidenceAcceptance.Validate(_staging, manifest));
    }

    [Test]
    public void Validate_RejectsArtifactPathOutsideStaging()
    {
        SaveLabAcceptanceManifest valid = SaveLabNativeEvidenceTestFactory.CreateValid(_staging);
        SaveLabAcceptanceManifest manifest = valid with
        {
            Workflows = valid.Workflows
                .Select((row, index) => index == 0
                    ? row with { OutputRelativePath = @"..\escape.bes" }
                    : row)
                .ToArray(),
        };

        Assert.That(
            () => SaveLabNativeEvidenceAcceptance.Validate(_staging, manifest),
            Throws.TypeOf<AssertionException>().With.Message.Contains("confined"));
    }

    [Test]
    public void Validate_RejectsMissingCapture()
    {
        SaveLabAcceptanceManifest valid = SaveLabNativeEvidenceTestFactory.CreateValid(_staging);
        SaveLabAcceptanceManifest manifest = valid with
        {
            Captures = valid.Captures.Skip(1).ToArray(),
        };

        Assert.That(
            () => SaveLabNativeEvidenceAcceptance.Validate(_staging, manifest),
            Throws.Exception.With.Message.Contains("eight captures"));
    }

    [Test]
    public void Validate_RejectsCaptureHashMismatch()
    {
        SaveLabAcceptanceManifest valid = SaveLabNativeEvidenceTestFactory.CreateValid(_staging);
        SaveLabAcceptanceManifest manifest = valid with
        {
            Captures = valid.Captures
                .Select((capture, index) => index == 0
                    ? capture with { Sha256 = new string('A', 64) }
                    : capture)
                .ToArray(),
        };

        Assert.That(
            () => SaveLabNativeEvidenceAcceptance.Validate(_staging, manifest),
            Throws.TypeOf<AssertionException>().With.Message.Contains("capture hash"));
    }

    [Test]
    public void Validate_RejectsCaptureIdentityThatDoesNotMatchWorkflow()
    {
        SaveLabAcceptanceManifest valid = SaveLabNativeEvidenceTestFactory.CreateValid(_staging);
        SaveLabCaptureEvidence first = valid.Captures[0];
        SaveLabAcceptanceManifest manifest = valid with
        {
            Captures = valid.Captures
                .Select((capture, index) => index == 0
                    ? first with { Identity = first.Identity with { ProcessId = 9999 } }
                    : capture)
                .ToArray(),
        };

        Assert.That(
            () => SaveLabNativeEvidenceAcceptance.Validate(_staging, manifest),
            Throws.Exception.With.Message.Contains("workflow identity"));
    }

    [Test]
    public void Publish_RenamesOneCompleteSiblingAndLeavesCanonicalManifest()
    {
        SaveLabAcceptanceManifest manifest = SaveLabNativeEvidenceTestFactory.CreateValid(_staging);

        SaveLabNativeEvidenceAcceptance.Publish(_staging, _accepted, manifest);

        Assert.Multiple(() =>
        {
            Assert.That(Directory.Exists(_staging), Is.False);
            Assert.That(Directory.Exists(_accepted), Is.True);
            Assert.That(
                File.Exists(Path.Combine(_accepted, SaveLabNativeEvidenceAcceptance.ManifestFileName)),
                Is.True);
        });
        using JsonDocument parsed = JsonDocument.Parse(
            File.ReadAllText(Path.Combine(_accepted, SaveLabNativeEvidenceAcceptance.ManifestFileName)));
        Assert.Multiple(() =>
        {
            Assert.That(parsed.RootElement.GetProperty("SchemaVersion").GetInt32(), Is.EqualTo(1));
            Assert.That(parsed.RootElement.GetProperty("HarnessRunId").GetString(), Is.EqualTo(manifest.HarnessRunId));
            Assert.That(parsed.RootElement.GetProperty("Captures").GetArrayLength(), Is.EqualTo(8));
            Assert.That(parsed.RootElement.GetProperty("Workflows").GetArrayLength(), Is.EqualTo(2));
        });
    }

    [Test]
    public void Publish_FailsClosedWhenAcceptedDirectoryAlreadyExists()
    {
        SaveLabAcceptanceManifest manifest = SaveLabNativeEvidenceTestFactory.CreateValid(_staging);
        Directory.CreateDirectory(_accepted);

        Assert.That(
            () => SaveLabNativeEvidenceAcceptance.Publish(_staging, _accepted, manifest),
            Throws.Exception.With.Message.Contains("fresh"));
        Assert.That(Directory.Exists(_staging), Is.True);
        Assert.That(
            Directory.GetFiles(_staging, ".save-lab-acceptance-manifest.*.tmp"),
            Is.Empty);
    }

    private static class SaveLabNativeEvidenceTestFactory
    {
        private const string RunId = "0123456789abcdef0123456789abcdef";

        internal static SaveLabAcceptanceManifest CreateValid(string stagingDirectory)
        {
            string saveInput = "fixtures/first-save-input.bes";
            string saveOutput = "save-session/appdata/OnslaughtCareerEditor/patched-output/first-save-input_patched.bes";
            string optionsInput = "fixtures/synthetic-options.bea";
            string optionsOutput = "options-session/appdata/OnslaughtCareerEditor/patched-output/synthetic-options_patched.bea";

            CopyFile(TestFixturePaths.RequireGoldSavePath(), Resolve(stagingDirectory, saveInput));
            byte[] saveOutputBytes = File.ReadAllBytes(Resolve(stagingDirectory, saveInput));
            saveOutputBytes[^1] ^= 0x01;
            WriteFile(Resolve(stagingDirectory, saveOutput), saveOutputBytes);

            byte[] optionsInputBytes = new byte[BesFilePatcher.EXPECTED_FILE_SIZE];
            optionsInputBytes[0] = 0xD1;
            optionsInputBytes[1] = 0x4B;
            WriteFile(Resolve(stagingDirectory, optionsInput), optionsInputBytes);
            byte[] optionsOutputBytes = (byte[])optionsInputBytes.Clone();
            optionsOutputBytes[0x64] = 1;
            WriteFile(Resolve(stagingDirectory, optionsOutput), optionsOutputBytes);

            SaveLabAppIdentityEvidence saveIdentity = Identity(4101, 0x1101);
            SaveLabAppIdentityEvidence optionsIdentity = Identity(4102, 0x1102);
            SaveLabWorkflowEvidence[] workflows =
            [
                Workflow(
                    "save-editor",
                    saveIdentity,
                    saveInput,
                    saveOutput,
                    stagingDirectory,
                    "goodies-old-output-valid"),
                Workflow(
                    "game-options",
                    optionsIdentity,
                    optionsInput,
                    optionsOutput,
                    stagingDirectory,
                    "controller-config-p1=1"),
            ];

            var expected = new[]
            {
                ("save-ready-normal.png", "save-editor", "ready", "SaveEditorInputFile", 1100, 900,
                    new[] { "SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox" }),
                ("save-ready-760.png", "save-editor", "ready", "SaveEditorInputFile", 760, 820,
                    new[] { "SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox" }),
                ("save-complete-normal.png", "save-editor", "complete", "SaveEditorShowWrittenSaveButton", 1100, 900,
                    new[] { "SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton" }),
                ("save-complete-760.png", "save-editor", "complete", "SaveEditorShowWrittenSaveButton", 760, 820,
                    new[] { "SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton" }),
                ("options-guidance-normal.png", "game-options", "guidance", "OpenZigguratControllerGuideButton", 1100, 900,
                    new[] { "ModernControllerSetupHeading", "ModernControllerSetupBoundary", "OpenZigguratControllerGuideButton" }),
                ("options-guidance-760.png", "game-options", "guidance", "OpenZigguratControllerGuideButton", 760, 820,
                    new[] { "ModernControllerSetupHeading", "ModernControllerSetupBoundary", "OpenZigguratControllerGuideButton" }),
                ("options-complete-normal.png", "game-options", "complete", "ConfigurationPatchButton", 1100, 900,
                    new[] { "ConfigurationSafetyHint", "ConfigurationPatchButton", "ConfigurationOutputLog" }),
                ("options-complete-760.png", "game-options", "complete", "ConfigurationPatchButton", 760, 820,
                    new[] { "ConfigurationSafetyHint", "ConfigurationPatchButton", "ConfigurationOutputLog" }),
            };

            SaveLabCaptureEvidence[] captures = expected.Select(row =>
            {
                string path = Resolve(stagingDirectory, row.Item1);
                Directory.CreateDirectory(Path.GetDirectoryName(path)!);
                using (var bitmap = new Bitmap(row.Item5, row.Item6))
                {
                    bitmap.Save(path, ImageFormat.Png);
                }

                SaveLabAppIdentityEvidence identity = row.Item2 == "save-editor"
                    ? saveIdentity
                    : optionsIdentity;
                SaveLabFocusObservation focus = new(
                    row.Item4,
                    identity.ProcessId,
                    identity.MainWindowHandle,
                    20,
                    20,
                    120,
                    40,
                    true);
                GuidedSaveVisualMarker[] markers = row.Item7
                    .Select((name, index) => new GuidedSaveVisualMarker(
                        name,
                        new Rectangle(20, 80 + index * 80, 240, 48)))
                    .ToArray();
                return new SaveLabCaptureEvidence(
                    row.Item2,
                    row.Item3,
                    row.Item4,
                    row.Item1,
                    Hash(path),
                    row.Item5,
                    row.Item6,
                    identity,
                    markers,
                    focus,
                    focus);
            }).ToArray();

            return new SaveLabAcceptanceManifest(
                SaveLabNativeEvidenceContract.SchemaVersion,
                RunId,
                SaveLabNativeEvidenceContract.InteractionMode,
                SaveLabNativeEvidenceContract.TrackedSaveFixtureSha256,
                new SyntheticOptionsEvidence(
                    BesFilePatcher.EXPECTED_FILE_SIZE,
                    BesFilePatcher.VERSION_WORD,
                    SaveLabNativeEvidenceContract.SyntheticOptionsSha256),
                captures,
                workflows);
        }

        private static SaveLabWorkflowEvidence Workflow(
            string workflow,
            SaveLabAppIdentityEvidence identity,
            string input,
            string output,
            string stagingDirectory,
            string readback)
        {
            string inputHash = Hash(Resolve(stagingDirectory, input));
            string outputPath = Resolve(stagingDirectory, output);
            return new SaveLabWorkflowEvidence(
                workflow,
                identity,
                input,
                inputHash,
                inputHash,
                output,
                Hash(outputPath),
                checked((int)new FileInfo(outputPath).Length),
                true,
                true,
                readback);
        }

        private static SaveLabAppIdentityEvidence Identity(int processId, long handle) => new(
            processId,
            new DateTime(2026, 7, 14, 12, 0, processId % 60, DateTimeKind.Utc),
            @"C:\repo\OnslaughtCareerEditor.WinUI.exe",
            new string('A', 64),
            @"C:\repo\OnslaughtCareerEditor.WinUI.dll",
            new string('B', 64),
            handle,
            handle,
            processId);

        private static void CopyFile(string source, string destination)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
            File.Copy(source, destination, overwrite: false);
        }

        private static void WriteFile(string path, byte[] bytes)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, bytes);
        }

        private static string Resolve(string root, string relativePath) =>
            Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar));

        private static string Hash(string path) =>
            Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
    }
}
