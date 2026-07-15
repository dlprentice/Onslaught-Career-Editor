using System.Drawing;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.RegularExpressions;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

internal static class SaveLabNativeEvidenceAcceptance
{
    internal const string ManifestFileName = "save-lab-acceptance-manifest.json";

    private sealed record ExpectedCapture(
        string Workflow,
        string Phase,
        string FocusAutomationId,
        int Width,
        int Height,
        IReadOnlySet<string> MarkerAutomationIds);

    private static readonly IReadOnlyDictionary<string, ExpectedCapture> ExpectedCaptures =
        new Dictionary<string, ExpectedCapture>(StringComparer.Ordinal)
        {
            ["save-ready-normal.png"] = Expected(
                "save-editor", "ready", "SaveEditorInputFile", 1100, 900,
                "SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox"),
            ["save-ready-760.png"] = Expected(
                "save-editor", "ready", "SaveEditorInputFile", 760, 820,
                "SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox"),
            ["save-complete-normal.png"] = Expected(
                "save-editor", "complete", "SaveEditorShowWrittenSaveButton", 1100, 900,
                "SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton"),
            ["save-complete-760.png"] = Expected(
                "save-editor", "complete", "SaveEditorShowWrittenSaveButton", 760, 820,
                "SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton"),
            ["options-guidance-normal.png"] = Expected(
                "game-options", "guidance", "OpenZigguratControllerGuideButton", 1100, 900,
                "ModernControllerSetupHeading", "ModernControllerSetupBoundary", "OpenZigguratControllerGuideButton"),
            ["options-guidance-760.png"] = Expected(
                "game-options", "guidance", "OpenZigguratControllerGuideButton", 760, 820,
                "ModernControllerSetupHeading", "ModernControllerSetupBoundary", "OpenZigguratControllerGuideButton"),
            ["options-complete-normal.png"] = Expected(
                "game-options", "complete", "ConfigurationPatchButton", 1100, 900,
                "ConfigurationSafetyHint", "ConfigurationPatchButton", "ConfigurationOutputLog"),
            ["options-complete-760.png"] = Expected(
                "game-options", "complete", "ConfigurationPatchButton", 760, 820,
                "ConfigurationSafetyHint", "ConfigurationPatchButton", "ConfigurationOutputLog"),
        };

    internal static void Validate(string stagingDirectory, SaveLabAcceptanceManifest manifest)
    {
        string root = Path.GetFullPath(stagingDirectory);
        Assert.Multiple(() =>
        {
            Assert.That(Directory.Exists(root), Is.True, "Save Lab evidence staging directory must exist.");
            Assert.That(manifest.SchemaVersion, Is.EqualTo(SaveLabNativeEvidenceContract.SchemaVersion));
            Assert.That(
                Regex.IsMatch(manifest.HarnessRunId ?? string.Empty, "^[0-9a-f]{32}$"),
                Is.True,
                "Save Lab harness run ID must be lowercase 32-hex.");
            Assert.That(manifest.InteractionMode, Is.EqualTo(SaveLabNativeEvidenceContract.InteractionMode));
            Assert.That(
                manifest.TrackedSaveFixtureSha256,
                Is.EqualTo(SaveLabNativeEvidenceContract.TrackedSaveFixtureSha256));
            Assert.That(manifest.SyntheticOptions.Length, Is.EqualTo(SaveLabNativeEvidenceContract.ArtifactLength));
            Assert.That(
                manifest.SyntheticOptions.VersionWord,
                Is.EqualTo(SaveLabNativeEvidenceContract.SyntheticOptionsVersionWord));
            Assert.That(
                manifest.SyntheticOptions.Sha256,
                Is.EqualTo(SaveLabNativeEvidenceContract.SyntheticOptionsSha256));
            Assert.That(manifest.Captures, Has.Count.EqualTo(8), "Save Lab evidence requires exactly eight captures.");
            Assert.That(manifest.Workflows, Has.Count.EqualTo(2), "Save Lab evidence requires exactly two workflows.");
        });

        Dictionary<string, SaveLabWorkflowEvidence> workflows = manifest.Workflows
            .GroupBy(row => row.Workflow, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Single(), StringComparer.Ordinal);
        Assert.That(workflows.Keys, Is.EquivalentTo(new[] { "save-editor", "game-options" }));
        Assert.That(
            workflows.Values.Select(row => (row.Identity.ProcessId, row.Identity.ProcessStartTimeUtc, row.Identity.MainWindowHandle)).Distinct().Count(),
            Is.EqualTo(2),
            "Each Save Lab workflow must bind a distinct launch identity.");

        foreach (SaveLabWorkflowEvidence workflow in workflows.Values)
        {
            ValidateIdentity(workflow.Identity);
            string inputPath = ResolveConfined(root, workflow.InputRelativePath, $"{workflow.Workflow} input");
            string outputPath = ResolveConfined(root, workflow.OutputRelativePath, $"{workflow.Workflow} output");
            Assert.Multiple(() =>
            {
                Assert.That(inputPath, Is.Not.EqualTo(outputPath).IgnoreCase);
                Assert.That(File.Exists(inputPath), Is.True, $"Missing {workflow.Workflow} input artifact.");
                Assert.That(File.Exists(outputPath), Is.True, $"Missing {workflow.Workflow} output artifact.");
            });
            string inputHash = Hash(inputPath);
            string outputHash = Hash(outputPath);
            Assert.Multiple(() =>
            {
                Assert.That(new FileInfo(inputPath).Length, Is.EqualTo(SaveLabNativeEvidenceContract.ArtifactLength));
                Assert.That(new FileInfo(outputPath).Length, Is.EqualTo(SaveLabNativeEvidenceContract.ArtifactLength));
                Assert.That(workflow.InputSha256Before, Is.EqualTo(inputHash), "Workflow input-before hash changed.");
                Assert.That(workflow.InputSha256After, Is.EqualTo(inputHash), "Workflow input-after hash changed.");
                Assert.That(workflow.InputPreserved, Is.True, "Workflow input preservation was not accepted.");
                Assert.That(workflow.OutputSha256, Is.EqualTo(outputHash), "Workflow output hash changed.");
                Assert.That(workflow.OutputLength, Is.EqualTo(SaveLabNativeEvidenceContract.ArtifactLength));
                Assert.That(workflow.OutputValidated, Is.True, "Workflow output validation was not accepted.");
                Assert.That(outputHash, Is.Not.EqualTo(inputHash), "Workflow output must differ from its input.");
            });
            ValidateSemanticOutput(workflow.Workflow, outputPath);
            string expectedReadback = workflow.Workflow == "save-editor"
                ? "goodies-old-output-valid"
                : "controller-config-p1=1";
            Assert.That(workflow.Readback, Is.EqualTo(expectedReadback));
        }

        Assert.Multiple(() =>
        {
            Assert.That(
                workflows["save-editor"].InputSha256Before,
                Is.EqualTo(SaveLabNativeEvidenceContract.TrackedSaveFixtureSha256));
            Assert.That(
                workflows["game-options"].InputSha256Before,
                Is.EqualTo(SaveLabNativeEvidenceContract.SyntheticOptionsSha256));
        });

        Dictionary<string, SaveLabCaptureEvidence> captures = manifest.Captures
            .GroupBy(capture => capture.RelativeFileName, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Single(), StringComparer.Ordinal);
        Assert.That(captures.Keys, Is.EquivalentTo(ExpectedCaptures.Keys), "Save Lab capture file set is not exact.");
        foreach ((string relativeFileName, ExpectedCapture expected) in ExpectedCaptures)
        {
            SaveLabCaptureEvidence capture = captures[relativeFileName];
            SaveLabWorkflowEvidence workflow = workflows[expected.Workflow];
            Assert.Multiple(() =>
            {
                Assert.That(capture.Workflow, Is.EqualTo(expected.Workflow));
                Assert.That(capture.Phase, Is.EqualTo(expected.Phase));
                Assert.That(capture.FocusAutomationId, Is.EqualTo(expected.FocusAutomationId));
                Assert.That(capture.Width, Is.EqualTo(expected.Width));
                Assert.That(capture.Height, Is.EqualTo(expected.Height));
                Assert.That(capture.Identity, Is.EqualTo(workflow.Identity), "Capture workflow identity mismatch.");
                Assert.That(
                    capture.Markers.Select(marker => marker.Name),
                    Is.EquivalentTo(expected.MarkerAutomationIds));
            });
            string imagePath = ResolveConfined(root, relativeFileName, $"capture {relativeFileName}");
            Assert.That(File.Exists(imagePath), Is.True, $"Missing Save Lab capture: {relativeFileName}");
            Assert.That(capture.Sha256, Is.EqualTo(Hash(imagePath)), $"Save Lab capture hash changed: {relativeFileName}");
            using (var bitmap = new Bitmap(imagePath))
            {
                Assert.That(bitmap.Size, Is.EqualTo(new Size(expected.Width, expected.Height)));
            }

            foreach (GuidedSaveVisualMarker marker in capture.Markers)
            {
                Assert.That(
                    marker.Bounds.Width > 0 && marker.Bounds.Height > 0 &&
                    marker.Bounds.Left >= 0 && marker.Bounds.Top >= 0 &&
                    marker.Bounds.Right <= expected.Width && marker.Bounds.Bottom <= expected.Height,
                    Is.True,
                    $"Marker {marker.Name} is outside capture {relativeFileName}.");
            }

            ValidateFocus(capture.FocusBeforeCapture, capture, workflow.Identity);
            ValidateFocus(capture.FocusAfterCapture, capture, workflow.Identity);
        }
    }

    private static void ValidateSemanticOutput(string workflow, string outputPath)
    {
        if (workflow == "save-editor")
        {
            SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(outputPath);
            GoodieStateDetail[] displayableGoodies = analysis.GoodieStates
                .Where(row => row.IsDisplayable)
                .ToArray();
            Assert.Multiple(() =>
            {
                Assert.That(analysis.IsValid, Is.True, analysis.ErrorMessage);
                Assert.That(
                    displayableGoodies,
                    Has.Length.EqualTo(SaveLabNativeEvidenceContract.DisplayableGoodieCount),
                    "Save Editor output must independently expose exactly 233 displayable Goodies.");
                Assert.That(
                    displayableGoodies,
                    Has.All.Property(nameof(GoodieStateDetail.RawState)).EqualTo(3u),
                    "Every displayable Goodies state must independently parse as OLD (3).");
            });
            return;
        }

        ConfigurationSnapshot snapshot = ConfigurationEditorService.LoadConfigurationSnapshot(outputPath);
        Assert.That(
            snapshot.ControllerConfigP1,
            Is.EqualTo(1u),
            "Game Options output ControllerConfigP1 must independently parse as 1.");
    }

    internal static void Publish(
        string stagingDirectory,
        string acceptedDirectory,
        SaveLabAcceptanceManifest manifest)
    {
        string staging = Path.GetFullPath(stagingDirectory);
        string accepted = Path.GetFullPath(acceptedDirectory);
        string ownedRoot = Path.GetDirectoryName(staging)!;
        SaveLabOwnedPathGuard.RequireDirectChild(ownedRoot, staging);
        SaveLabOwnedPathGuard.RequireDirectChild(ownedRoot, accepted);
        Assert.Multiple(() =>
        {
            Assert.That(Directory.Exists(staging), Is.True);
            Assert.That(Directory.Exists(accepted), Is.False, "Accepted Save Lab evidence destination must be fresh.");
            Assert.That(
                Path.GetDirectoryName(staging),
                Is.EqualTo(Path.GetDirectoryName(accepted)).IgnoreCase,
                "Save Lab staging and accepted directories must be siblings.");
        });
        Validate(staging, manifest);

        string canonicalPath = Path.Combine(staging, ManifestFileName);
        Assert.That(File.Exists(canonicalPath), Is.False, "Canonical Save Lab manifest destination must be fresh.");
        string temporaryPath = Path.Combine(
            staging,
            $".{Path.GetFileNameWithoutExtension(ManifestFileName)}.{Guid.NewGuid():N}.tmp");
        try
        {
            using (FileStream stream = new(temporaryPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                JsonSerializer.Serialize(stream, manifest, new JsonSerializerOptions { WriteIndented = true });
                stream.Flush(flushToDisk: true);
            }

            using (JsonDocument document = JsonDocument.Parse(File.ReadAllText(temporaryPath)))
            {
                Assert.Multiple(() =>
                {
                    Assert.That(document.RootElement.GetProperty("SchemaVersion").GetInt32(), Is.EqualTo(1));
                    Assert.That(document.RootElement.GetProperty("HarnessRunId").GetString(), Is.EqualTo(manifest.HarnessRunId));
                    Assert.That(document.RootElement.GetProperty("Captures").GetArrayLength(), Is.EqualTo(8));
                    Assert.That(document.RootElement.GetProperty("Workflows").GetArrayLength(), Is.EqualTo(2));
                });
            }

            SaveLabOwnedPathGuard.RequireDirectChild(ownedRoot, staging);
            SaveLabOwnedPathGuard.RequireDirectChild(ownedRoot, accepted);
            File.Move(temporaryPath, canonicalPath);
            Directory.Move(staging, accepted);
        }
        finally
        {
            if (Directory.Exists(staging))
            {
                SaveLabOwnedPathGuard.RequireDirectChild(ownedRoot, staging);
                File.Delete(temporaryPath);
            }
        }
    }

    private static ExpectedCapture Expected(
        string workflow,
        string phase,
        string focusAutomationId,
        int width,
        int height,
        params string[] markerAutomationIds) =>
        new(
            workflow,
            phase,
            focusAutomationId,
            width,
            height,
            markerAutomationIds.ToHashSet(StringComparer.Ordinal));

    private static void ValidateIdentity(SaveLabAppIdentityEvidence identity)
    {
        Assert.Multiple(() =>
        {
            Assert.That(identity.ProcessId, Is.GreaterThan(0));
            Assert.That(identity.ProcessStartTimeUtc, Is.Not.EqualTo(default(DateTime)));
            Assert.That(identity.ExecutablePath, Is.Not.Empty);
            Assert.That(identity.ProductAssemblyPath, Is.Not.Empty);
            Assert.That(IsUpperHexSha256(identity.ExecutableSha256), Is.True);
            Assert.That(IsUpperHexSha256(identity.ProductAssemblySha256), Is.True);
            Assert.That(identity.MainWindowHandle, Is.Not.Zero);
            Assert.That(identity.UiaNativeWindowHandle, Is.EqualTo(identity.MainWindowHandle));
            Assert.That(identity.WindowOwnerProcessId, Is.EqualTo(identity.ProcessId));
        });
    }

    private static void ValidateFocus(
        SaveLabFocusObservation focus,
        SaveLabCaptureEvidence capture,
        SaveLabAppIdentityEvidence identity)
    {
        Assert.Multiple(() =>
        {
            Assert.That(focus.AutomationId, Is.EqualTo(capture.FocusAutomationId));
            Assert.That(focus.ProcessId, Is.EqualTo(identity.ProcessId));
            Assert.That(focus.MainWindowHandle, Is.EqualTo(identity.MainWindowHandle));
            Assert.That(focus.HasKeyboardFocus, Is.True);
            Assert.That(focus.Width, Is.GreaterThan(0));
            Assert.That(focus.Height, Is.GreaterThan(0));
            Assert.That(focus.X, Is.GreaterThanOrEqualTo(0));
            Assert.That(focus.Y, Is.GreaterThanOrEqualTo(0));
            Assert.That(focus.X + focus.Width, Is.LessThanOrEqualTo(capture.Width));
            Assert.That(focus.Y + focus.Height, Is.LessThanOrEqualTo(capture.Height));
        });
    }

    private static string ResolveConfined(string root, string relativePath, string label)
    {
        Assert.That(relativePath, Is.Not.Null.And.Not.Empty, $"{label} relative path is missing.");
        Assert.That(Path.IsPathRooted(relativePath), Is.False, $"{label} path must be relative and confined.");
        string fullRoot = Path.GetFullPath(root);
        string combined = Path.GetFullPath(Path.Combine(
            fullRoot,
            relativePath.Replace('/', Path.DirectorySeparatorChar)));
        string relative = Path.GetRelativePath(fullRoot, combined);
        Assert.That(
            relative != ".." && !relative.StartsWith($"..{Path.DirectorySeparatorChar}", StringComparison.Ordinal),
            Is.True,
            $"{label} path must remain confined to Save Lab staging.");
        return combined;
    }

    private static bool IsUpperHexSha256(string value) =>
        Regex.IsMatch(value ?? string.Empty, "^[0-9A-F]{64}$");

    private static string Hash(string path) =>
        Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
}
