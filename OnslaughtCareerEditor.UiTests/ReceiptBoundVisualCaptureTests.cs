using System.Drawing;

namespace OnslaughtCareerEditor.UiTests;

public class ReceiptBoundVisualCaptureTests
{
    private static readonly ReceiptBoundAppIdentity ExpectedIdentity = new(
        ProcessId: 4242,
        ProcessStartTimeUtc: new DateTime(2026, 7, 13, 21, 9, 13, DateTimeKind.Utc),
        ExecutablePath: @"C:\Toolkit\OnslaughtCareerEditor.WinUI.exe",
        ExecutableSha256: "ABC123",
        ProductAssemblyPath: @"C:\Toolkit\OnslaughtCareerEditor.WinUI.dll",
        ProductAssemblySha256: "DLL123",
        MainWindowHandle: new IntPtr(0x1234),
        UiaNativeWindowHandle: new IntPtr(0x1234),
        WindowOwnerProcessId: 4242,
        ProcessAlive: true);

    [Test]
    public void Capture_RestoresOriginalWindowStateAfterSuccessfulBoundCapture()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        var original = new ReceiptBoundWindowState(
            new Rectangle(40, 50, 1000, 700),
            ShowCommand: 3,
            IsTopmost: true,
            IsVisible: true,
            NormalBounds: new Rectangle(45, 55, 960, 680),
            MinPosition: new Point(-32000, -32000),
            MaxPosition: new Point(0, 0),
            PlacementFlags: 2);
        var operations = new FakeOperations(ExpectedIdentity, original, CreateToolkitBitmap(760, 820));

        try
        {
            ReceiptBoundVisualCapture.Capture(
                operations,
                BuildRequest(outputPath, new Rectangle(16, 16, 760, 820)));

            Assert.That(File.Exists(outputPath), Is.True);
            Assert.That(operations.RestoredStates, Is.EqualTo(new[] { original }));
            Assert.That(operations.Events, Is.EqualTo(new[]
            {
                "read-identity",
                "read-window-state",
                "show-restored",
                "position:16,16,760,820",
                "foreground",
                "wait:16,16,760,820",
                "read-identity",
                "topmost",
                "foreground",
                "wait:16,16,760,820",
                "marker:SaveEditorOutputLog",
                "marker:SaveEditorShowWrittenSaveButton",
                "read-identity",
                "capture:4660:16,16,760,820",
                "marker:SaveEditorOutputLog",
                "marker:SaveEditorShowWrittenSaveButton",
                "read-identity",
                "wait:16,16,760,820",
                "restore:40,50,1000,700:3:topmost",
            }));
        }
        finally
        {
            File.Delete(outputPath);
        }
    }

    [Test]
    public void Capture_RealizesMarkersAfterResizeBeforeRequiringSimultaneousVisibility()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        var original = new ReceiptBoundWindowState(
            new Rectangle(40, 50, 1280, 820),
            ShowCommand: 1,
            IsTopmost: false);
        var withoutRealization = new FakeOperations(ExpectedIdentity, original, CreateToolkitBitmap(760, 820))
        {
            MarkersRequirePostResizeRealization = true,
        };
        Assert.That(withoutRealization.AreMarkersInsideCurrentWindow, Is.True, "Both markers start visible at the pre-resize bounds.");
        AssertionException missingRealization = Assert.Throws<AssertionException>(() =>
            ReceiptBoundVisualCapture.Capture(
                withoutRealization,
                BuildRequest(outputPath, new Rectangle(16, 16, 760, 820))))!;
        Assert.That(missingRealization.Message, Does.Contain("simultaneously inside"));
        Assert.That(withoutRealization.Events, Does.Not.Contain("capture:4660:16,16,760,820"));

        var operations = new FakeOperations(ExpectedIdentity, original, CreateToolkitBitmap(760, 820))
        {
            MarkersRequirePostResizeRealization = true,
        };
        ReceiptBoundVisualCaptureRequest request = BuildRequest(outputPath, new Rectangle(16, 16, 760, 820)) with
        {
            PostResizeRealization = () => operations.CompletePostResizeRealization(),
        };

        try
        {
            ReceiptBoundVisualCapture.Capture(operations, request);

            Assert.That(File.Exists(outputPath), Is.True);
            int realizationIndex = operations.Events.IndexOf("post-resize-realization");
            Assert.That(realizationIndex, Is.GreaterThanOrEqualTo(0));
            Assert.That(
                operations.Events.IndexOf("position:16,16,760,820"),
                Is.LessThan(realizationIndex));
            Assert.That(
                operations.Events.IndexOf("wait:16,16,760,820"),
                Is.LessThan(realizationIndex));
            Assert.That(realizationIndex, Is.LessThan(operations.Events.IndexOf("marker:SaveEditorOutputLog")));
            Assert.That(realizationIndex, Is.LessThan(operations.Events.IndexOf("capture:4660:16,16,760,820")));
        }
        finally
        {
            File.Delete(outputPath);
        }
    }

    [Test]
    public void Capture_RestoresOriginalWindowStateWhenCaptureFails()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        File.WriteAllText(outputPath, "stale screenshot evidence");
        var original = new ReceiptBoundWindowState(
            new Rectangle(80, 90, 1200, 800),
            ShowCommand: 1,
            IsTopmost: false,
            IsVisible: false,
            NormalBounds: new Rectangle(85, 95, 1180, 780),
            MinPosition: new Point(-32000, -32000),
            MaxPosition: new Point(0, 0),
            PlacementFlags: 1);
        var operations = new FakeOperations(ExpectedIdentity, original, CreateToolkitBitmap(760, 820))
        {
            CaptureFailure = new InvalidOperationException("capture failed"),
        };

        InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
            ReceiptBoundVisualCapture.Capture(
                operations,
                BuildRequest(outputPath, new Rectangle(16, 16, 760, 820))))!;

        Assert.Multiple(() =>
        {
            Assert.That(error.Message, Is.EqualTo("capture failed"));
            Assert.That(operations.Events.Last(), Is.EqualTo("restore:80,90,1200,800:1:not-topmost"));
            Assert.That(File.ReadAllText(outputPath), Is.EqualTo("stale screenshot evidence"));
            Assert.That(operations.RestoredStates, Is.EqualTo(new[] { original }));
        });
        File.Delete(outputPath);
    }

    [Test]
    public void Capture_FailsClosedBeforeCaptureWhenReceiptIdentityChanges()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        var operations = new FakeOperations(
            ExpectedIdentity,
            new ReceiptBoundWindowState(new Rectangle(0, 0, 1000, 700), ShowCommand: 1, IsTopmost: false),
            CreateToolkitBitmap(760, 820));
        operations.Identities.Enqueue(ExpectedIdentity);
        operations.Identities.Enqueue(ExpectedIdentity with { UiaNativeWindowHandle = new IntPtr(0x9999) });

        AssertionException error = Assert.Throws<AssertionException>(() =>
            ReceiptBoundVisualCapture.Capture(
                operations,
                BuildRequest(outputPath, new Rectangle(16, 16, 760, 820))))!;

        Assert.Multiple(() =>
        {
            Assert.That(error.Message, Does.Contain("UIA NativeWindowHandle"));
            Assert.That(operations.Events, Does.Not.Contain("capture:4660:16,16,760,820"));
            Assert.That(operations.Events.Last(), Does.StartWith("restore:"));
        });
    }

    [Test]
    public void Capture_FailsClosedWhenIdentityChangesImmediatelyBeforeCapture()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        var operations = new FakeOperations(
            ExpectedIdentity,
            new ReceiptBoundWindowState(new Rectangle(0, 0, 1000, 700), ShowCommand: 1, IsTopmost: false),
            CreateToolkitBitmap(760, 820));
        operations.Identities.Enqueue(ExpectedIdentity);
        operations.Identities.Enqueue(ExpectedIdentity);
        operations.Identities.Enqueue(ExpectedIdentity with { ExecutableSha256 = "CHANGED" });

        AssertionException error = Assert.Throws<AssertionException>(() =>
            ReceiptBoundVisualCapture.Capture(
                operations,
                BuildRequest(outputPath, new Rectangle(16, 16, 760, 820))))!;

        Assert.Multiple(() =>
        {
            Assert.That(error.Message, Does.Contain("executable hash changed"));
            Assert.That(operations.Events.Any(entry => entry.StartsWith("capture:", StringComparison.Ordinal)), Is.False);
            Assert.That(operations.Events.Last(), Does.StartWith("restore:"));
        });
    }

    [Test]
    public void Capture_FailsClosedWhenLiveLauncherPathChangesWithTheSameHash()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        var operations = new FakeOperations(
            ExpectedIdentity,
            new ReceiptBoundWindowState(new Rectangle(0, 0, 1000, 700), ShowCommand: 1, IsTopmost: false),
            CreateToolkitBitmap(760, 820));
        operations.Identities.Enqueue(ExpectedIdentity);
        operations.Identities.Enqueue(ExpectedIdentity with { ExecutablePath = @"C:\Other\OnslaughtCareerEditor.WinUI.exe" });

        AssertionException error = Assert.Throws<AssertionException>(() =>
            ReceiptBoundVisualCapture.Capture(
                operations,
                BuildRequest(outputPath, new Rectangle(16, 16, 760, 820))))!;

        Assert.Multiple(() =>
        {
            Assert.That(error.Message, Does.Contain("executable path changed"));
            Assert.That(operations.Events.Any(entry => entry.StartsWith("capture:", StringComparison.Ordinal)), Is.False);
            Assert.That(operations.Events.Last(), Does.StartWith("restore:"));
        });
    }

    [Test]
    public void Capture_FailsClosedWhenExeIsUnchangedButProductDllChanges()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        var operations = new FakeOperations(
            ExpectedIdentity,
            new ReceiptBoundWindowState(new Rectangle(0, 0, 1000, 700), ShowCommand: 1, IsTopmost: false),
            CreateToolkitBitmap(760, 820));
        operations.Identities.Enqueue(ExpectedIdentity);
        operations.Identities.Enqueue(ExpectedIdentity);
        operations.Identities.Enqueue(ExpectedIdentity with { ProductAssemblySha256 = "DLL-CHANGED" });

        AssertionException error = Assert.Throws<AssertionException>(() =>
            ReceiptBoundVisualCapture.Capture(
                operations,
                BuildRequest(outputPath, new Rectangle(16, 16, 760, 820))))!;

        Assert.Multiple(() =>
        {
            Assert.That(error.Message, Does.Contain("product assembly hash changed"));
            Assert.That(operations.Events.Any(entry => entry.StartsWith("capture:", StringComparison.Ordinal)), Is.False);
            Assert.That(File.Exists(outputPath), Is.False);
            Assert.That(operations.Events.Last(), Does.StartWith("restore:"));
        });
    }

    [Test]
    public void Capture_RejectsMarkerMovementBetweenSamplingAndPixels()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        File.WriteAllText(outputPath, "prior accepted evidence");
        var operations = new FakeOperations(
            ExpectedIdentity,
            new ReceiptBoundWindowState(new Rectangle(0, 0, 1000, 700), ShowCommand: 1, IsTopmost: false),
            CreateToolkitBitmap(760, 820))
        {
            ShiftMarkersAfterCapture = true,
        };

        AssertionException error = Assert.Throws<AssertionException>(() =>
            ReceiptBoundVisualCapture.Capture(
                operations,
                BuildRequest(outputPath, new Rectangle(16, 16, 760, 820))))!;

        Assert.Multiple(() =>
        {
            Assert.That(error.Message, Does.Contain("marker bounds changed"));
            Assert.That(File.ReadAllText(outputPath), Is.EqualTo("prior accepted evidence"));
            Assert.That(operations.Events.Last(), Does.StartWith("restore:"));
        });
        File.Delete(outputPath);
    }

    [Test]
    public void ImagePublisher_CleansTemporaryOutputAndPreservesPriorAcceptedEvidenceWhenReopenIsInvalid()
    {
        string outputPath = Path.Combine(Path.GetTempPath(), $"onslaught-capture-{Guid.NewGuid():N}.png");
        File.WriteAllText(outputPath, "prior accepted evidence");
        using Bitmap bitmap = CreateToolkitBitmap(760, 820);

        AssertionException error = Assert.Throws<AssertionException>(() =>
            GuidedSaveCaptureImagePublisher.Publish(
                bitmap,
                outputPath,
                new Size(760, 820),
                BuildMarkers(760, 820),
                _ => new Bitmap(10, 10)))!;

        Assert.Multiple(() =>
        {
            Assert.That(error.Message, Does.Contain("reopened screenshot dimensions"));
            Assert.That(File.ReadAllText(outputPath), Is.EqualTo("prior accepted evidence"));
            Assert.That(
                Directory.GetFiles(Path.GetDirectoryName(outputPath)!, $"{Path.GetFileName(outputPath)}.*.tmp"),
                Is.Empty);
        });
        File.Delete(outputPath);
    }

    [Test]
    public void NativeAdapterSource_BindsLiveImageAndHwndOwnerAndRestoresFullPlacement()
    {
        string source = File.ReadAllText(Path.Combine(
            ResolveRepoRoot(),
            "OnslaughtCareerEditor.UiTests",
            "FlaUiReceiptBoundVisualCaptureOperations.cs"));

        Assert.Multiple(() =>
        {
            Assert.That(source, Does.Contain("process.MainModule"));
            Assert.That(source, Does.Contain("GetWindowThreadProcessId"));
            Assert.That(source, Does.Contain("SetWindowPlacement"));
            Assert.That(source, Does.Contain("HwndTopmost"));
            Assert.That(source, Does.Contain("HwndNotTopmost"));
            Assert.That(source, Does.Contain("Capture.Element(_window)"));
            Assert.That(source, Does.Not.Contain("PrintWindow"));
            Assert.That(source, Does.Not.Contain("CopyFromScreen"));
            Assert.That(source, Does.Not.Contain("Windows.Graphics.Capture"));
        });
    }

    [TestCase(1936, 1048)]
    [TestCase(760, 820)]
    public void GuidedSaveValidator_AcceptsToolkitMarkersAtNormalAndCompactSizes(int width, int height)
    {
        using Bitmap bitmap = CreateToolkitBitmap(width, height);

        Assert.That(
            GuidedSaveToolkitImageValidator.IsValid(
                bitmap,
                BuildMarkers(width, height),
                out string reason),
            Is.True,
            reason);
    }

    [TestCase(1936, 1048)]
    [TestCase(760, 820)]
    public void GuidedSaveValidator_RejectsKnownCodexDesktopSignature(int width, int height)
    {
        using Bitmap bitmap = CreateCodexDesktopBitmap(width, height);

        Assert.That(
            GuidedSaveToolkitImageValidator.IsValid(
                bitmap,
                BuildMarkers(width, height),
                out string reason),
            Is.False);
        Assert.That(reason, Does.Contain("Codex Desktop"));
    }

    private static ReceiptBoundVisualCaptureRequest BuildRequest(string outputPath, Rectangle targetBounds)
    {
        return new ReceiptBoundVisualCaptureRequest(
            ExpectedIdentity,
            targetBounds,
            outputPath,
            new[] { "SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton" },
            TimeSpan.FromSeconds(2));
    }

    private static IReadOnlyList<GuidedSaveVisualMarker> BuildMarkers(int width, int height)
    {
        return new[]
        {
            new GuidedSaveVisualMarker("SaveEditorOutputLog", new Rectangle(width / 2, height / 2, Math.Max(120, width / 3), 180)),
            new GuidedSaveVisualMarker("SaveEditorShowWrittenSaveButton", new Rectangle(32, height / 2, Math.Max(140, width / 4), 48)),
        };
    }

    private static Bitmap CreateToolkitBitmap(int width, int height)
    {
        var bitmap = new Bitmap(width, height);
        using Graphics graphics = Graphics.FromImage(bitmap);
        graphics.Clear(Color.FromArgb(255, 20, 26, 38));
        using var headerBrush = new SolidBrush(Color.FromArgb(255, 20, 72, 118));
        graphics.FillRectangle(headerBrush, 0, 36, width, 80);
        foreach (GuidedSaveVisualMarker marker in BuildMarkers(width, height))
        {
            using var cardBrush = new SolidBrush(Color.FromArgb(255, 35, 46, 62));
            using var accentPen = new Pen(Color.FromArgb(255, 70, 170, 235), 3);
            graphics.FillRectangle(cardBrush, marker.Bounds);
            graphics.DrawRectangle(accentPen, marker.Bounds);
            graphics.DrawLine(Pens.White, marker.Bounds.Left + 12, marker.Bounds.Top + 16, marker.Bounds.Right - 12, marker.Bounds.Top + 16);
            graphics.DrawLine(Pens.LightGray, marker.Bounds.Left + 12, marker.Bounds.Top + 28, marker.Bounds.Left + marker.Bounds.Width / 2, marker.Bounds.Top + 28);
        }

        return bitmap;
    }

    private static Bitmap CreateCodexDesktopBitmap(int width, int height)
    {
        var bitmap = new Bitmap(width, height);
        using Graphics graphics = Graphics.FromImage(bitmap);
        graphics.Clear(Color.FromArgb(255, 39, 41, 54));
        using var chromeBrush = new SolidBrush(Color.FromArgb(255, 30, 29, 34));
        graphics.FillRectangle(chromeBrush, 0, 0, width, 42);
        graphics.FillRectangle(chromeBrush, 0, 0, Math.Min(310, width / 2), height);
        using var magentaBrush = new SolidBrush(Color.FromArgb(255, 238, 110, 185));
        graphics.FillEllipse(magentaBrush, 245, 160, 10, 10);
        graphics.FillEllipse(magentaBrush, 245, 260, 10, 10);
        return bitmap;
    }

    private sealed class FakeOperations : IReceiptBoundVisualCaptureOperations
    {
        private readonly ReceiptBoundAppIdentity _defaultIdentity;
        private readonly ReceiptBoundWindowState _windowState;
        private readonly Bitmap _bitmap;
        private Rectangle _positionedBounds;

        public FakeOperations(ReceiptBoundAppIdentity defaultIdentity, ReceiptBoundWindowState windowState, Bitmap bitmap)
        {
            _defaultIdentity = defaultIdentity;
            _windowState = windowState;
            _bitmap = bitmap;
            _positionedBounds = windowState.Bounds;
        }

        public List<string> Events { get; } = new();

        public List<ReceiptBoundWindowState> RestoredStates { get; } = new();

        public Queue<ReceiptBoundAppIdentity> Identities { get; } = new();

        public Exception? CaptureFailure { get; init; }

        public bool ShiftMarkersAfterCapture { get; init; }

        public bool MarkersRequirePostResizeRealization { get; init; }

        public bool AreMarkersInsideCurrentWindow =>
            BuildMarkers(_positionedBounds.Width, _positionedBounds.Height)
                .Select(marker => ResolveMarkerBounds(marker))
                .All(bounds => bounds.Left >= 0 &&
                               bounds.Top >= 0 &&
                               bounds.Right <= _positionedBounds.Width &&
                               bounds.Bottom <= _positionedBounds.Height);

        private bool PostResizeRealizationCompleted { get; set; }

        private bool HasCaptured { get; set; }

        public ReceiptBoundAppIdentity ReadIdentity()
        {
            Events.Add("read-identity");
            return Identities.Count > 0 ? Identities.Dequeue() : _defaultIdentity;
        }

        public ReceiptBoundWindowState ReadWindowState()
        {
            Events.Add("read-window-state");
            return _windowState;
        }

        public void ShowRestored() => Events.Add("show-restored");

        public void PositionWindow(Rectangle bounds)
        {
            _positionedBounds = bounds;
            Events.Add($"position:{bounds.X},{bounds.Y},{bounds.Width},{bounds.Height}");
        }

        public void SetForeground() => Events.Add("foreground");

        public void WaitForForegroundAndBounds(Rectangle bounds, TimeSpan timeout) =>
            Events.Add($"wait:{bounds.X},{bounds.Y},{bounds.Width},{bounds.Height}");

        public void SetTopmost() => Events.Add("topmost");

        public GuidedSaveVisualMarker ReadMarker(string automationId)
        {
            Events.Add($"marker:{automationId}");
            GuidedSaveVisualMarker marker = BuildMarkers(_positionedBounds.Width, _positionedBounds.Height)
                .Single(candidate => candidate.Name == automationId);
            marker = marker with { Bounds = ResolveMarkerBounds(marker) };

            return ShiftMarkersAfterCapture && HasCaptured
                ? marker with { Bounds = new Rectangle(marker.Bounds.X + 5, marker.Bounds.Y, marker.Bounds.Width, marker.Bounds.Height) }
                : marker;
        }

        public void CompletePostResizeRealization()
        {
            Events.Add("post-resize-realization");
            PostResizeRealizationCompleted = true;
        }

        private Rectangle ResolveMarkerBounds(GuidedSaveVisualMarker marker)
        {
            return MarkersRequirePostResizeRealization &&
                   _positionedBounds.Width == 760 &&
                   !PostResizeRealizationCompleted
                ? new Rectangle(
                    marker.Bounds.X,
                    _positionedBounds.Height + 20,
                    marker.Bounds.Width,
                    marker.Bounds.Height)
                : marker.Bounds;
        }

        public Bitmap CaptureBoundWindow(IntPtr hwnd, Rectangle bounds)
        {
            Events.Add($"capture:{hwnd.ToInt64()}:{bounds.X},{bounds.Y},{bounds.Width},{bounds.Height}");
            if (CaptureFailure is not null)
            {
                throw CaptureFailure;
            }

            HasCaptured = true;
            return (Bitmap)_bitmap.Clone();
        }

        public void RestoreWindowState(ReceiptBoundWindowState state)
        {
            RestoredStates.Add(state);
            Events.Add($"restore:{state.Bounds.X},{state.Bounds.Y},{state.Bounds.Width},{state.Bounds.Height}:{state.ShowCommand}:{(state.IsTopmost ? "topmost" : "not-topmost")}");
        }

    }

    private static string ResolveRepoRoot()
    {
        return Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
    }
}
