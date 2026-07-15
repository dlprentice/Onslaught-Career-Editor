using System.Drawing;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.RegularExpressions;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

internal static class MediaAssetNativeEvidenceAcceptance
{
    internal const string ManifestFileName = "media-asset-acceptance-manifest.json";

    internal static void Validate(string stagingDirectory, MediaAssetAcceptanceManifest manifest)
    {
        string root = Path.GetFullPath(stagingDirectory);
        Assert.Multiple(() =>
        {
            Assert.That(Directory.Exists(root), Is.True, "Media/Asset evidence staging directory must exist.");
            Assert.That(manifest.SchemaVersion, Is.EqualTo(MediaAssetNativeEvidenceContract.SchemaVersion));
            Assert.That(
                Regex.IsMatch(manifest.HarnessRunId ?? string.Empty, "^[0-9a-f]{32}$"),
                Is.True,
                "Media/Asset harness run ID must be lowercase 32-hex.");
            Assert.That(manifest.InteractionMode, Is.EqualTo(MediaAssetNativeEvidenceContract.InteractionMode));
            Assert.That(manifest.Fixture.RootRelativePath, Is.EqualTo("fixtures"));
            Assert.That(manifest.Captures, Has.Count.EqualTo(8));
            Assert.That(manifest.Workflows, Has.Count.EqualTo(3));
        });
        MediaAssetOwnedPathGuard.RequireReparseFreeTree(root);

        string fixtureRoot = ResolveConfined(root, manifest.Fixture.RootRelativePath, "fixture root");
        var fixture = new MediaAssetNativeFixture(
            fixtureRoot,
            Path.Combine(fixtureRoot, "media-game"),
            Path.Combine(fixtureRoot, "asset-bundle", "asset_catalog", "catalog.json"),
            manifest.Fixture.Files);
        MediaAssetNativeFixtureBuilder.Validate(fixture);

        Dictionary<string, MediaAssetWorkflowEvidence> workflows = manifest.Workflows
            .GroupBy(row => row.Workflow, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Single(), StringComparer.Ordinal);
        Assert.That(workflows.Keys, Is.EquivalentTo(MediaAssetNativeEvidenceContract.ExpectedSelections.Keys));
        Assert.That(
            workflows.Values
                .Select(row => (row.Identity.ProcessId, row.Identity.ProcessStartTimeUtc))
                .Distinct()
                .Count(),
            Is.EqualTo(3),
            "Media audio, Media video, and Asset Library require distinct process launch identities.");
        foreach ((string workflowName, IReadOnlyList<MediaAssetSelectionEvidence> expectedSelections) in
            MediaAssetNativeEvidenceContract.ExpectedSelections)
        {
            MediaAssetWorkflowEvidence workflow = workflows[workflowName];
            ValidateIdentity(workflow.Identity);
            Assert.Multiple(() =>
            {
                Assert.That(workflow.PlaybackModulesLoaded, Is.False, $"{workflowName} must not initialize playback modules.");
                Assert.That(workflow.Selections, Is.EqualTo(expectedSelections));
            });
        }

        Dictionary<string, MediaAssetCaptureEvidence> captures = manifest.Captures
            .GroupBy(capture => capture.RelativeFileName, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.Single(), StringComparer.Ordinal);
        Assert.That(
            captures.Keys,
            Is.EquivalentTo(MediaAssetNativeEvidenceContract.ExpectedCaptures.Select(row => row.RelativeFileName)),
            "Media/Asset capture file set is not exact.");

        foreach (MediaAssetExpectedCapture expected in MediaAssetNativeEvidenceContract.ExpectedCaptures)
        {
            MediaAssetCaptureEvidence capture = captures[expected.RelativeFileName];
            MediaAssetWorkflowEvidence workflow = workflows[expected.Workflow];
            Assert.Multiple(() =>
            {
                Assert.That(capture.Workflow, Is.EqualTo(expected.Workflow));
                Assert.That(capture.Phase, Is.EqualTo(expected.Phase));
                Assert.That(capture.FocusAutomationId, Is.EqualTo(expected.FocusAutomationId));
                Assert.That(capture.Width, Is.EqualTo(expected.Width));
                Assert.That(capture.Height, Is.EqualTo(expected.Height));
                Assert.That(capture.Identity, Is.EqualTo(workflow.Identity));
                Assert.That(
                    capture.Markers.Select(marker => marker.Name),
                    Is.EquivalentTo(expected.MarkerAutomationIds));
            });

            string imagePath = ResolveConfined(root, capture.RelativeFileName, $"capture {capture.RelativeFileName}");
            Assert.That(File.Exists(imagePath), Is.True, $"Missing Media/Asset capture: {capture.RelativeFileName}");
            Assert.That(capture.Sha256, Is.EqualTo(Hash(imagePath)), $"Capture hash changed: {capture.RelativeFileName}");
            using (var bitmap = new Bitmap(imagePath))
            {
                Assert.That(bitmap.Size, Is.EqualTo(new Size(expected.Width, expected.Height)));
            }

            foreach (GuidedSaveVisualMarker marker in capture.Markers)
            {
                Assert.That(
                    IsInside(marker.Bounds.X, marker.Bounds.Y, marker.Bounds.Width, marker.Bounds.Height, capture.Width, capture.Height),
                    Is.True,
                    $"Marker {marker.Name} is outside capture {capture.RelativeFileName}.");
            }

            ValidateFocus(capture.FocusBeforeCapture, capture, workflow.Identity);
            ValidateFocus(capture.FocusAfterCapture, capture, workflow.Identity);
        }
    }

    internal static void Publish(
        string stagingDirectory,
        string acceptedDirectory,
        MediaAssetAcceptanceManifest manifest)
    {
        string staging = Path.GetFullPath(stagingDirectory);
        string accepted = Path.GetFullPath(acceptedDirectory);
        string ownedRoot = Path.GetDirectoryName(staging)!;
        MediaAssetOwnedPathGuard.RequireDirectChild(ownedRoot, staging);
        MediaAssetOwnedPathGuard.RequireDirectChild(ownedRoot, accepted);
        Assert.Multiple(() =>
        {
            Assert.That(Directory.Exists(staging), Is.True);
            Assert.That(Directory.Exists(accepted), Is.False, "Accepted Media/Asset evidence destination must be fresh.");
            Assert.That(Path.GetDirectoryName(staging), Is.EqualTo(Path.GetDirectoryName(accepted)).IgnoreCase);
        });
        Validate(staging, manifest);

        string canonicalPath = Path.Combine(staging, ManifestFileName);
        Assert.That(File.Exists(canonicalPath), Is.False, "Canonical Media/Asset manifest destination must be fresh.");
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

            MediaAssetAcceptanceManifest? roundTrip = JsonSerializer.Deserialize<MediaAssetAcceptanceManifest>(
                File.ReadAllText(temporaryPath));
            Assert.That(roundTrip, Is.Not.Null, "Canonical Media/Asset manifest did not deserialize.");
            File.Move(temporaryPath, canonicalPath);
            MediaAssetOwnedPathGuard.RequireReparseFreeTree(staging);
            Validate(staging, roundTrip!);
            MediaAssetOwnedPathGuard.RequireDirectChild(ownedRoot, staging);
            MediaAssetOwnedPathGuard.RequireDirectChild(ownedRoot, accepted);
            Directory.Move(staging, accepted);
        }
        finally
        {
            if (Directory.Exists(staging))
            {
                MediaAssetOwnedPathGuard.RequireDirectChild(ownedRoot, staging);
                File.Delete(temporaryPath);
            }
        }
    }

    private static void ValidateIdentity(MediaAssetAppIdentityEvidence identity)
    {
        Assert.Multiple(() =>
        {
            Assert.That(identity.ProcessId, Is.GreaterThan(0));
            Assert.That(identity.ProcessStartTimeUtc, Is.Not.EqualTo(default(DateTime)));
            Assert.That(identity.ExecutablePath, Is.Not.Empty);
            Assert.That(identity.ProductAssemblyPath, Is.Not.Empty);
            Assert.That(IsUpperHexSha256(identity.ExecutableSha256), Is.True);
            Assert.That(IsUpperHexSha256(identity.ProductAssemblySha256), Is.True);
            Assert.That(IsUpperHexSha256(identity.ApplicationPayloadSha256), Is.True);
            Assert.That(identity.MainWindowHandle, Is.Not.Zero);
            Assert.That(identity.UiaNativeWindowHandle, Is.EqualTo(identity.MainWindowHandle));
            Assert.That(identity.WindowOwnerProcessId, Is.EqualTo(identity.ProcessId));
        });
    }

    private static void ValidateFocus(
        MediaAssetFocusObservation focus,
        MediaAssetCaptureEvidence capture,
        MediaAssetAppIdentityEvidence identity)
    {
        Assert.Multiple(() =>
        {
            Assert.That(focus.AutomationId, Is.EqualTo(capture.FocusAutomationId));
            Assert.That(focus.ProcessId, Is.EqualTo(identity.ProcessId));
            Assert.That(focus.MainWindowHandle, Is.EqualTo(identity.MainWindowHandle));
            Assert.That(focus.HasKeyboardFocus, Is.True);
            Assert.That(
                IsInside(focus.X, focus.Y, focus.Width, focus.Height, capture.Width, capture.Height),
                Is.True,
                "Owner-bound focus must remain inside the receipt-bound HWND image.");
        });
    }

    private static bool IsInside(int x, int y, int width, int height, int imageWidth, int imageHeight) =>
        width > 0 && height > 0 && x >= 0 && y >= 0 &&
        x + width <= imageWidth && y + height <= imageHeight;

    private static string ResolveConfined(string root, string relativePath, string label)
    {
        Assert.That(relativePath, Is.Not.Null.And.Not.Empty, $"{label} relative path is missing.");
        Assert.That(Path.IsPathRooted(relativePath), Is.False, $"{label} path must be relative.");
        Assert.That(relativePath.Contains('\\'), Is.False, $"{label} path must use normalized separators.");
        Assert.That(
            relativePath.Split('/').Any(segment => segment is "" or "." or ".."),
            Is.False,
            $"{label} path contains a forbidden segment.");
        string fullRoot = Path.GetFullPath(root);
        string combined = Path.GetFullPath(Path.Combine(
            fullRoot,
            relativePath.Replace('/', Path.DirectorySeparatorChar)));
        string relative = Path.GetRelativePath(fullRoot, combined);
        Assert.That(
            relative != ".." && !relative.StartsWith($"..{Path.DirectorySeparatorChar}", StringComparison.Ordinal),
            Is.True,
            $"{label} path escaped Media/Asset staging.");
        return combined;
    }

    private static bool IsUpperHexSha256(string value) =>
        Regex.IsMatch(value ?? string.Empty, "^[0-9A-F]{64}$");

    private static string Hash(string path) =>
        Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
}
