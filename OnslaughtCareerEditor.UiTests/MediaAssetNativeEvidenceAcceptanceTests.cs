using System.Drawing;
using System.Security.Cryptography;

namespace OnslaughtCareerEditor.UiTests;

public class MediaAssetNativeEvidenceAcceptanceTests
{
    [Test]
    public void Validate_AcceptsExactGeneratedWorkflowEvidence()
    {
        using var fixture = ValidEvidence.Create();

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, fixture.Manifest),
            Throws.Nothing);
    }

    [Test]
    public void Validate_RejectsMissingOrRenamedCapture()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetAcceptanceManifest manifest = fixture.Manifest with
        {
            Captures = fixture.Manifest.Captures.Skip(1).ToArray(),
        };

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, manifest),
            Throws.Exception);
    }

    [Test]
    public void Validate_RejectsPlaybackInitialization()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetWorkflowEvidence video = fixture.Manifest.Workflows.Single(row => row.Workflow == "media-video");
        MediaAssetAcceptanceManifest manifest = fixture.Manifest with
        {
            Workflows = fixture.Manifest.Workflows
                .Select(row => row.Workflow == "media-video" ? video with { PlaybackModulesLoaded = true } : row)
                .ToArray(),
        };

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, manifest),
            Throws.Exception);
    }

    [Test]
    public void Validate_RejectsFixtureMutation()
    {
        using var fixture = ValidEvidence.Create();
        string catalog = Path.Combine(
            fixture.StagingDirectory,
            "fixtures",
            "asset-bundle",
            "asset_catalog",
            "catalog.json");
        File.AppendAllText(catalog, " ");

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, fixture.Manifest),
            Throws.Exception);
    }

    [Test]
    public void Validate_RejectsReorderedOrRehashedFixtureReceipts()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetFixtureEvidence reordered = fixture.Manifest.Fixture with
        {
            Files = fixture.Manifest.Fixture.Files.Reverse().ToArray(),
        };
        MediaAssetFixtureEvidence rehashed = fixture.Manifest.Fixture with
        {
            Files = fixture.Manifest.Fixture.Files
                .Select((row, index) => index == 0 ? row with { Sha256 = new string('F', 64) } : row)
                .ToArray(),
        };

        Assert.Multiple(() =>
        {
            Assert.That(
                () => MediaAssetNativeEvidenceAcceptance.Validate(
                    fixture.StagingDirectory,
                    fixture.Manifest with { Fixture = reordered }),
                Throws.Exception);
            Assert.That(
                () => MediaAssetNativeEvidenceAcceptance.Validate(
                    fixture.StagingDirectory,
                    fixture.Manifest with { Fixture = rehashed }),
                Throws.Exception);
        });
    }

    [Test]
    public void Validate_RejectsChangedCaptureHash()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetCaptureEvidence first = fixture.Manifest.Captures[0];
        MediaAssetAcceptanceManifest manifest = fixture.Manifest with
        {
            Captures = fixture.Manifest.Captures
                .Select(row => row == first ? row with { Sha256 = new string('F', 64) } : row)
                .ToArray(),
        };

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, manifest),
            Throws.Exception);
    }

    [Test]
    public void Validate_RejectsEscapingFixtureRoot()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetAcceptanceManifest manifest = fixture.Manifest with
        {
            Fixture = fixture.Manifest.Fixture with { RootRelativePath = "../fixtures" },
        };

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, manifest),
            Throws.Exception);
    }

    [Test]
    public void Validate_RejectsReusedLaunchIdentity()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetAppIdentityEvidence audio = fixture.Manifest.Workflows
            .Single(row => row.Workflow == "media-audio")
            .Identity;
        MediaAssetAcceptanceManifest manifest = fixture.Manifest with
        {
            Workflows = fixture.Manifest.Workflows
                .Select(row => row.Workflow == "media-video" ? row with { Identity = audio } : row)
                .ToArray(),
            Captures = fixture.Manifest.Captures
                .Select(row => row.Workflow == "media-video" ? row with { Identity = audio } : row)
                .ToArray(),
        };

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, manifest),
            Throws.Exception);
    }

    [Test]
    public void Validate_RejectsSingleProcessWithDistinctWindowHandles()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetAppIdentityEvidence audio = fixture.Manifest.Workflows
            .Single(row => row.Workflow == "media-audio")
            .Identity;
        MediaAssetAppIdentityEvidence video = fixture.Manifest.Workflows
            .Single(row => row.Workflow == "media-video")
            .Identity;
        MediaAssetAppIdentityEvidence reusedProcess = video with
        {
            ProcessId = audio.ProcessId,
            ProcessStartTimeUtc = audio.ProcessStartTimeUtc,
            WindowOwnerProcessId = audio.ProcessId,
        };
        MediaAssetAcceptanceManifest manifest = fixture.Manifest with
        {
            Workflows = fixture.Manifest.Workflows
                .Select(row => row.Workflow == "media-video" ? row with { Identity = reusedProcess } : row)
                .ToArray(),
            Captures = fixture.Manifest.Captures
                .Select(row => row.Workflow == "media-video"
                    ? row with
                    {
                        Identity = reusedProcess,
                        FocusBeforeCapture = row.FocusBeforeCapture with { ProcessId = audio.ProcessId },
                        FocusAfterCapture = row.FocusAfterCapture with { ProcessId = audio.ProcessId },
                    }
                    : row)
                .ToArray(),
        };

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, manifest),
            Throws.Exception.With.Message.Contains("distinct process launch identities"));
    }

    [Test]
    public void Validate_RejectsWrongSemanticReadback()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetWorkflowEvidence audio = fixture.Manifest.Workflows.Single(row => row.Workflow == "media-audio");
        MediaAssetAcceptanceManifest manifest = fixture.Manifest with
        {
            Workflows = fixture.Manifest.Workflows
                .Select(row => row.Workflow == "media-audio"
                    ? audio with
                    {
                        Selections =
                        [
                            audio.Selections.Single() with { Title = "ambient-row" },
                        ],
                    }
                    : row)
                .ToArray(),
        };

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, manifest),
            Throws.Exception);
    }

    [Test]
    public void Validate_RejectsFocusOutsideBoundWindow()
    {
        using var fixture = ValidEvidence.Create();
        MediaAssetCaptureEvidence first = fixture.Manifest.Captures[0];
        MediaAssetAcceptanceManifest manifest = fixture.Manifest with
        {
            Captures = fixture.Manifest.Captures
                .Select(row => row == first
                    ? row with
                    {
                        FocusAfterCapture = row.FocusAfterCapture with { X = row.Width },
                    }
                    : row)
                .ToArray(),
        };

        Assert.That(
            () => MediaAssetNativeEvidenceAcceptance.Validate(fixture.StagingDirectory, manifest),
            Throws.Exception);
    }

    [Test]
    public void Publish_WritesCanonicalManifestAndMovesFreshSibling()
    {
        using var fixture = ValidEvidence.Create();
        string accepted = Path.Combine(fixture.RootDirectory, "accepted");

        MediaAssetNativeEvidenceAcceptance.Publish(
            fixture.StagingDirectory,
            accepted,
            fixture.Manifest);

        Assert.Multiple(() =>
        {
            Assert.That(Directory.Exists(fixture.StagingDirectory), Is.False);
            Assert.That(Directory.Exists(accepted), Is.True);
            Assert.That(
                File.Exists(Path.Combine(accepted, MediaAssetNativeEvidenceAcceptance.ManifestFileName)),
                Is.True);
        });
    }

    private sealed class ValidEvidence : IDisposable
    {
        private ValidEvidence(
            string rootDirectory,
            string stagingDirectory,
            MediaAssetAcceptanceManifest manifest)
        {
            RootDirectory = rootDirectory;
            StagingDirectory = stagingDirectory;
            Manifest = manifest;
        }

        internal string RootDirectory { get; }

        internal string StagingDirectory { get; }

        internal MediaAssetAcceptanceManifest Manifest { get; }

        internal static ValidEvidence Create()
        {
            string root = Path.Combine(
                Path.GetTempPath(),
                "onslaught-media-asset-evidence-tests",
                Guid.NewGuid().ToString("N"));
            string staging = Path.Combine(root, "staging");
            Directory.CreateDirectory(staging);
            MediaAssetNativeFixture generated = MediaAssetNativeFixtureBuilder.Build(
                Path.Combine(staging, "fixtures"));

            MediaAssetAppIdentityEvidence audioIdentity = Identity(101, 1001, 'A');
            MediaAssetAppIdentityEvidence videoIdentity = Identity(102, 1002, 'B');
            MediaAssetAppIdentityEvidence assetIdentity = Identity(103, 1003, 'C');
            var workflows = new[]
            {
                new MediaAssetWorkflowEvidence(
                    "media-audio",
                    audioIdentity,
                    PlaybackModulesLoaded: false,
                    [
                        new MediaAssetSelectionEvidence(
                            "audio-selected",
                            "TUTORIAL_intro",
                            "Tutorial • TUTORIAL_intro.ogg",
                            "play-enabled-no-playback"),
                    ]),
                new MediaAssetWorkflowEvidence(
                    "media-video",
                    videoIdentity,
                    PlaybackModulesLoaded: false,
                    [
                        new MediaAssetSelectionEvidence(
                            "video-selected",
                            "Credits Video",
                            "Main Videos • UsTheMovie.vid",
                            "play-enabled-deferred-no-playback"),
                    ]),
                new MediaAssetWorkflowEvidence(
                    "asset-library",
                    assetIdentity,
                    PlaybackModulesLoaded: false,
                    [
                        new MediaAssetSelectionEvidence(
                            "texture-selected",
                            "Texture One",
                            "fixture; 1 packed references; export available.",
                            "texture:fixture/texture_one.tga"),
                        new MediaAssetSelectionEvidence(
                            "model-wireframe",
                            "fixture_mesh.msh",
                            "1 packed references; FBX export available. Use the in-app wireframe for a quick geometry check, then open the FBX for full material review.",
                            "Binary FBX 7400; 3 vertices; 3 polygon index entries; UV mapping: no coordinate data recorded."),
                    ]),
            };

            var captures = MediaAssetNativeEvidenceContract.ExpectedCaptures
                .Select(expected => CreateCapture(staging, expected, workflows.Single(row => row.Workflow == expected.Workflow).Identity))
                .ToArray();
            var manifest = new MediaAssetAcceptanceManifest(
                MediaAssetNativeEvidenceContract.SchemaVersion,
                "0123456789abcdef0123456789abcdef",
                MediaAssetNativeEvidenceContract.InteractionMode,
                new MediaAssetFixtureEvidence("fixtures", generated.Files),
                captures,
                workflows);
            return new ValidEvidence(root, staging, manifest);
        }

        public void Dispose()
        {
            if (Directory.Exists(RootDirectory))
            {
                Directory.Delete(RootDirectory, recursive: true);
            }
        }

        private static MediaAssetCaptureEvidence CreateCapture(
            string staging,
            MediaAssetExpectedCapture expected,
            MediaAssetAppIdentityEvidence identity)
        {
            string path = Path.Combine(staging, expected.RelativeFileName);
            using (var bitmap = new Bitmap(expected.Width, expected.Height))
            {
                using Graphics graphics = Graphics.FromImage(bitmap);
                graphics.Clear(Color.SteelBlue);
                bitmap.Save(path);
            }

            GuidedSaveVisualMarker[] markers = expected.MarkerAutomationIds
                .Select((name, index) => new GuidedSaveVisualMarker(
                    name,
                    new Rectangle(20 + index * 8, 60 + index * 8, 80, 24)))
                .ToArray();
            var focus = new MediaAssetFocusObservation(
                expected.FocusAutomationId,
                identity.ProcessId,
                identity.MainWindowHandle,
                20,
                60,
                80,
                24,
                true);
            return new MediaAssetCaptureEvidence(
                expected.Workflow,
                expected.Phase,
                expected.FocusAutomationId,
                expected.RelativeFileName,
                Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))),
                expected.Width,
                expected.Height,
                identity,
                markers,
                focus,
                focus);
        }

        private static MediaAssetAppIdentityEvidence Identity(int processId, long hwnd, char hash) =>
            new(
                processId,
                new DateTime(2026, 7, 15, 3, 0, processId - 100, DateTimeKind.Utc),
                $@"C:\repo\{processId}\OnslaughtCareerEditor.WinUI.exe",
                new string(hash, 64),
                $@"C:\repo\{processId}\OnslaughtCareerEditor.WinUI.dll",
                new string(hash, 64),
                new string(hash, 64),
                hwnd,
                hwnd,
                processId);
    }
}
