using System.Drawing;
using System.Drawing.Imaging;

namespace OnslaughtCareerEditor.UiTests;

internal sealed record ReceiptBoundAppIdentity(
    int ProcessId,
    DateTime ProcessStartTimeUtc,
    string ExecutablePath,
    string ExecutableSha256,
    string ProductAssemblyPath,
    string ProductAssemblySha256,
    IntPtr MainWindowHandle,
    IntPtr UiaNativeWindowHandle,
    int WindowOwnerProcessId,
    bool ProcessAlive);

internal sealed record ReceiptBoundWindowState(
    Rectangle Bounds,
    int ShowCommand,
    bool IsTopmost,
    bool IsVisible = true,
    Rectangle NormalBounds = default,
    Point MinPosition = default,
    Point MaxPosition = default,
    int PlacementFlags = 0);

internal sealed record GuidedSaveVisualMarker(string Name, Rectangle Bounds);

internal sealed record ReceiptBoundVisualCaptureRequest(
    ReceiptBoundAppIdentity ExpectedIdentity,
    Rectangle TargetBounds,
    string OutputPath,
    IReadOnlyList<string> MarkerAutomationIds,
    TimeSpan WaitTimeout,
    Action? PostResizeRealization = null);

internal interface IReceiptBoundVisualCaptureOperations
{
    ReceiptBoundAppIdentity ReadIdentity();

    ReceiptBoundWindowState ReadWindowState();

    void ShowRestored();

    void PositionWindow(Rectangle bounds);

    void SetForeground();

    void WaitForForegroundAndBounds(Rectangle bounds, TimeSpan timeout);

    void SetTopmost();

    GuidedSaveVisualMarker ReadMarker(string automationId);

    Bitmap CaptureBoundWindow(IntPtr hwnd, Rectangle bounds);

    void RestoreWindowState(ReceiptBoundWindowState state);
}

internal static class ReceiptBoundVisualCapture
{
    public static void Capture(
        IReceiptBoundVisualCaptureOperations operations,
        ReceiptBoundVisualCaptureRequest request)
    {
        ArgumentNullException.ThrowIfNull(operations);
        ArgumentNullException.ThrowIfNull(request);
        Bitmap? bitmap = null;
        try
        {
            AssertIdentity(operations.ReadIdentity(), request.ExpectedIdentity);
            ReceiptBoundWindowState originalState = operations.ReadWindowState();
            IReadOnlyList<GuidedSaveVisualMarker> beforeMarkers = Array.Empty<GuidedSaveVisualMarker>();
            try
            {
                operations.ShowRestored();
                operations.PositionWindow(request.TargetBounds);
                operations.SetForeground();
                operations.WaitForForegroundAndBounds(request.TargetBounds, request.WaitTimeout);
                AssertIdentity(operations.ReadIdentity(), request.ExpectedIdentity);
                if (request.PostResizeRealization is not null)
                {
                    request.PostResizeRealization();
                    operations.WaitForForegroundAndBounds(request.TargetBounds, request.WaitTimeout);
                    AssertIdentity(operations.ReadIdentity(), request.ExpectedIdentity);
                }

                operations.SetTopmost();
                operations.SetForeground();
                operations.WaitForForegroundAndBounds(request.TargetBounds, request.WaitTimeout);
                beforeMarkers = request.MarkerAutomationIds
                    .Select(operations.ReadMarker)
                    .ToArray();
                AssertMarkersInsideBoundWindow(beforeMarkers, request.TargetBounds.Size);
                AssertIdentity(operations.ReadIdentity(), request.ExpectedIdentity);

                bitmap = operations.CaptureBoundWindow(
                    request.ExpectedIdentity.MainWindowHandle,
                    request.TargetBounds);
                Assert.That(bitmap.Width, Is.EqualTo(request.TargetBounds.Width), "Captured bitmap width must match the bound HWND rectangle.");
                Assert.That(bitmap.Height, Is.EqualTo(request.TargetBounds.Height), "Captured bitmap height must match the bound HWND rectangle.");

                IReadOnlyList<GuidedSaveVisualMarker> afterMarkers = request.MarkerAutomationIds
                    .Select(operations.ReadMarker)
                    .ToArray();
                Assert.That(afterMarkers, Is.EqualTo(beforeMarkers), "Guided-save marker bounds changed between UIA sampling and captured pixels.");
                AssertIdentity(operations.ReadIdentity(), request.ExpectedIdentity);
                operations.WaitForForegroundAndBounds(request.TargetBounds, request.WaitTimeout);
            }
            finally
            {
                operations.RestoreWindowState(originalState);
            }

            Assert.That(bitmap, Is.Not.Null, "The receipt-bound capture did not produce a bitmap.");
            GuidedSaveCaptureImagePublisher.Publish(
                bitmap!,
                request.OutputPath,
                request.TargetBounds.Size,
                beforeMarkers);
        }
        catch
        {
            throw;
        }
        finally
        {
            bitmap?.Dispose();
        }
    }

    private static void AssertMarkersInsideBoundWindow(
        IReadOnlyList<GuidedSaveVisualMarker> markers,
        Size windowSize)
    {
        foreach (GuidedSaveVisualMarker marker in markers)
        {
            Assert.That(
                marker.Bounds.Width > 0 &&
                marker.Bounds.Height > 0 &&
                marker.Bounds.Left >= 0 &&
                marker.Bounds.Top >= 0 &&
                marker.Bounds.Right <= windowSize.Width &&
                marker.Bounds.Bottom <= windowSize.Height,
                Is.True,
                $"Guided-save marker '{marker.Name}' must be simultaneously inside the exact receipt-bound HWND before capture. " +
                $"Marker={marker.Bounds}; HWND=0,0,{windowSize.Width},{windowSize.Height}.");
        }
    }

    private static void AssertIdentity(ReceiptBoundAppIdentity actual, ReceiptBoundAppIdentity expected)
    {
        Assert.That(actual.ProcessAlive, Is.True, "The receipt-bound Toolkit process must still be alive.");
        Assert.That(actual.ProcessId, Is.EqualTo(expected.ProcessId), "The capture process ID changed from the launch receipt.");
        Assert.That(actual.ProcessStartTimeUtc, Is.EqualTo(expected.ProcessStartTimeUtc), "The capture process start time changed from the launch receipt.");
        Assert.That(actual.ExecutablePath, Is.EqualTo(expected.ExecutablePath).IgnoreCase, "The live executable path changed from the launch receipt.");
        Assert.That(actual.ExecutableSha256, Is.EqualTo(expected.ExecutableSha256).IgnoreCase, "The capture executable hash changed from the launch receipt.");
        Assert.That(actual.ProductAssemblyPath, Is.EqualTo(expected.ProductAssemblyPath).IgnoreCase, "The loaded product assembly path changed from the launch receipt.");
        Assert.That(actual.ProductAssemblySha256, Is.EqualTo(expected.ProductAssemblySha256).IgnoreCase, "The loaded product assembly hash changed from the launch receipt.");
        Assert.That(actual.MainWindowHandle, Is.EqualTo(expected.MainWindowHandle), "The app MainWindowHandle changed from the launch receipt.");
        Assert.That(actual.UiaNativeWindowHandle, Is.EqualTo(expected.MainWindowHandle), "UIA NativeWindowHandle must equal app.MainWindowHandle.");
        Assert.That(actual.UiaNativeWindowHandle, Is.EqualTo(expected.UiaNativeWindowHandle), "UIA NativeWindowHandle changed from the launch receipt.");
        Assert.That(actual.WindowOwnerProcessId, Is.EqualTo(expected.WindowOwnerProcessId), "The HWND owner PID changed from the launch receipt.");
        Assert.That(actual.WindowOwnerProcessId, Is.EqualTo(actual.ProcessId), "The HWND owner PID must equal the live process PID.");
    }
}

internal static class GuidedSaveCaptureImagePublisher
{
    public static void Publish(
        Bitmap bitmap,
        string outputPath,
        Size expectedSize,
        IReadOnlyList<GuidedSaveVisualMarker> markers,
        Func<string, Bitmap>? reopen = null)
    {
        ArgumentNullException.ThrowIfNull(bitmap);
        string? outputDirectory = Path.GetDirectoryName(outputPath);
        if (!string.IsNullOrEmpty(outputDirectory))
        {
            Directory.CreateDirectory(outputDirectory);
        }

        string temporaryPath = $"{outputPath}.{Guid.NewGuid():N}.tmp";
        try
        {
            Assert.That(
                GuidedSaveToolkitImageValidator.IsValid(bitmap, markers, out string rejectionReason),
                Is.True,
                rejectionReason);
            using (FileStream encoded = new(
                       temporaryPath,
                       FileMode.CreateNew,
                       FileAccess.Write,
                       FileShare.None))
            {
                bitmap.Save(encoded, ImageFormat.Png);
                encoded.Flush(flushToDisk: true);
            }
            using (Bitmap reopened = (reopen ?? OpenDetachedBitmap)(temporaryPath))
            {
                Assert.That(
                    reopened.Size,
                    Is.EqualTo(expectedSize),
                    "The reopened screenshot dimensions must match the exact bound HWND rectangle.");
                Assert.That(
                    GuidedSaveToolkitImageValidator.IsValid(reopened, markers, out string reopenedRejectionReason),
                    Is.True,
                    reopenedRejectionReason);
            }

            File.Move(temporaryPath, outputPath, overwrite: true);
        }
        catch
        {
            File.Delete(temporaryPath);
            throw;
        }
    }

    private static Bitmap OpenDetachedBitmap(string path)
    {
        using FileStream stream = File.Open(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        using var loaded = new Bitmap(stream);
        return new Bitmap(loaded);
    }
}

internal static class GuidedSaveToolkitImageValidator
{
    private static readonly string[] RequiredMarkers =
    {
        "SaveEditorOutputLog",
        "SaveEditorShowWrittenSaveButton",
    };

    public static bool IsValid(
        Bitmap bitmap,
        IReadOnlyList<GuidedSaveVisualMarker> markers,
        out string rejectionReason)
    {
        ArgumentNullException.ThrowIfNull(bitmap);
        ArgumentNullException.ThrowIfNull(markers);

        if (HasKnownCodexDesktopSignature(bitmap))
        {
            rejectionReason = "Screenshot matches the known Codex Desktop chrome/status-dot signature.";
            return false;
        }

        if (!HasRenderedToolkitHeader(bitmap))
        {
            rejectionReason = "Screenshot does not contain the rendered Toolkit blue header signature.";
            return false;
        }

        foreach (string requiredMarker in RequiredMarkers)
        {
            GuidedSaveVisualMarker? marker = markers.FirstOrDefault(candidate =>
                string.Equals(candidate.Name, requiredMarker, StringComparison.Ordinal));
            if (marker is null)
            {
                rejectionReason = $"Screenshot validation is missing guided-save marker '{requiredMarker}'.";
                return false;
            }

            if (!ContainsRectangle(bitmap, marker.Bounds) || !HasRenderedMarkerActivity(bitmap, marker.Bounds))
            {
                rejectionReason = $"Guided-save marker '{requiredMarker}' is outside the bound HWND image or is not visibly rendered.";
                return false;
            }
        }

        rejectionReason = string.Empty;
        return true;
    }

    private static bool HasKnownCodexDesktopSignature(Bitmap bitmap)
    {
        int leftWidth = Math.Min(bitmap.Width / 2, 310);
        int magentaSamples = 0;
        for (int y = 0; y < bitmap.Height; y += 3)
        {
            for (int x = 0; x < leftWidth; x += 3)
            {
                Color pixel = bitmap.GetPixel(x, y);
                if (pixel.R >= 180 && pixel.B >= 130 && pixel.G <= 150 && pixel.R > pixel.G + 30)
                {
                    magentaSamples++;
                }
            }
        }

        int darkChromeSamples = 0;
        int chromeSampleCount = 0;
        for (int x = 0; x < bitmap.Width; x += Math.Max(1, bitmap.Width / 32))
        {
            Color pixel = bitmap.GetPixel(x, Math.Min(24, bitmap.Height - 1));
            chromeSampleCount++;
            if (pixel.R < 55 && pixel.G < 55 && pixel.B < 70 && Math.Abs(pixel.R - pixel.G) < 18)
            {
                darkChromeSamples++;
            }
        }

        return magentaSamples >= 4 && darkChromeSamples >= chromeSampleCount * 3 / 4;
    }

    private static bool HasRenderedToolkitHeader(Bitmap bitmap)
    {
        if (bitmap.Width < 4 || bitmap.Height < 117)
        {
            return false;
        }

        int renderedSamples = 0;
        foreach (int x in new[] { bitmap.Width / 4, bitmap.Width / 2, bitmap.Width * 3 / 4 })
        {
            foreach (int y in new[] { 50, 70, 90 })
            {
                Color pixel = bitmap.GetPixel(x, y);
                if (pixel.A > 240 && pixel.B > pixel.R && pixel.R + pixel.G + pixel.B > 100)
                {
                    renderedSamples++;
                }
            }
        }

        return renderedSamples >= 6;
    }

    private static bool HasRenderedMarkerActivity(Bitmap bitmap, Rectangle bounds)
    {
        var buckets = new HashSet<int>();
        int brightOrAccentSamples = 0;
        int xStep = Math.Max(1, bounds.Width / 24);
        int yStep = Math.Max(1, bounds.Height / 12);
        for (int y = bounds.Top; y < bounds.Bottom; y += yStep)
        {
            for (int x = bounds.Left; x < bounds.Right; x += xStep)
            {
                Color pixel = bitmap.GetPixel(x, y);
                buckets.Add((pixel.R / 32 << 10) | (pixel.G / 32 << 5) | (pixel.B / 32));
                if (pixel.R + pixel.G + pixel.B >= 420 || pixel.B >= pixel.R + 35)
                {
                    brightOrAccentSamples++;
                }
            }
        }

        return buckets.Count >= 2 && brightOrAccentSamples >= 2;
    }

    private static bool ContainsRectangle(Bitmap bitmap, Rectangle bounds)
    {
        return bounds.Width >= 24 &&
               bounds.Height >= 24 &&
               bounds.Left >= 0 &&
               bounds.Top >= 0 &&
               bounds.Right <= bitmap.Width &&
               bounds.Bottom <= bitmap.Height;
    }
}
