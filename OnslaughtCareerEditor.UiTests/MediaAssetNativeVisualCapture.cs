using System.Drawing;
using System.Drawing.Imaging;
using System.Security.Cryptography;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

internal static class MediaAssetNativeVisualCapture
{
    internal static MediaAssetCaptureEvidence Capture(
        MediaAssetNativeSession session,
        string workflow,
        string phase,
        string focusAutomationId,
        Rectangle targetBounds,
        string outputPath,
        IReadOnlyList<string> markerAutomationIds,
        Action postResizeRealization)
    {
        ArgumentNullException.ThrowIfNull(session);
        ArgumentNullException.ThrowIfNull(postResizeRealization);
        Assert.That(markerAutomationIds, Is.Not.Empty);

        var operations = new FlaUiReceiptBoundVisualCaptureOperations(
            session.App,
            session.Window,
            session.ExecutablePath);
        Assert.That(operations.ReadIdentity(), Is.EqualTo(session.Identity));
        ReceiptBoundWindowState originalState = operations.ReadWindowState();
        Bitmap? bitmap = null;
        IReadOnlyList<GuidedSaveVisualMarker>? capturedMarkers = null;
        MediaAssetFocusObservation? focusBefore = null;
        MediaAssetFocusObservation? focusAfter = null;
        Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
        Assert.That(File.Exists(outputPath), Is.False, $"Media/Asset capture destination must be fresh: {outputPath}");
        string temporaryPath = $"{outputPath}.{Guid.NewGuid():N}.tmp";
        try
        {
            try
            {
                operations.ShowRestored();
                operations.PositionWindow(targetBounds);
                operations.SetForeground();
                operations.WaitForForegroundAndBounds(targetBounds, TimeSpan.FromSeconds(5));
                Assert.That(operations.ReadIdentity(), Is.EqualTo(session.Identity));

                postResizeRealization();
                WaitForMarkerStability(operations, markerAutomationIds, targetBounds.Size);
                FocusExactTarget(session, focusAutomationId);
                WaitForMarkerStability(operations, markerAutomationIds, targetBounds.Size);

                operations.SetTopmost();
                operations.SetForeground();
                operations.WaitForForegroundAndBounds(targetBounds, TimeSpan.FromSeconds(5));
                Assert.That(operations.ReadIdentity(), Is.EqualTo(session.Identity));
                focusBefore = ReadExactFocus(session, focusAutomationId, targetBounds);
                IReadOnlyList<GuidedSaveVisualMarker> beforeMarkers = markerAutomationIds
                    .Select(operations.ReadMarker)
                    .ToArray();
                AssertMarkersInsideImage(beforeMarkers, targetBounds.Size);

                bitmap = operations.CaptureBoundWindow(session.Identity.MainWindowHandle, targetBounds);
                IReadOnlyList<GuidedSaveVisualMarker> afterMarkers = markerAutomationIds
                    .Select(operations.ReadMarker)
                    .ToArray();
                Assert.That(afterMarkers, Is.EqualTo(beforeMarkers));
                Assert.That(operations.ReadIdentity(), Is.EqualTo(session.Identity));
                focusAfter = ReadExactFocus(session, focusAutomationId, targetBounds);
                try
                {
                    AssertToolkitImage(bitmap, beforeMarkers);
                }
                catch
                {
                    string rejectedPath = $"{outputPath}.rejected.png";
                    using FileStream rejected = new(rejectedPath, FileMode.CreateNew, FileAccess.Write, FileShare.None);
                    bitmap.Save(rejected, ImageFormat.Png);
                    rejected.Flush(flushToDisk: true);
                    throw;
                }
                capturedMarkers = beforeMarkers;

                using (FileStream encoded = new(temporaryPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                {
                    bitmap.Save(encoded, ImageFormat.Png);
                    encoded.Flush(flushToDisk: true);
                }

                using (FileStream stream = File.Open(temporaryPath, FileMode.Open, FileAccess.Read, FileShare.Read))
                using (var source = new Bitmap(stream))
                using (var reopened = new Bitmap(source))
                {
                    Assert.That(reopened.Size, Is.EqualTo(targetBounds.Size));
                    AssertToolkitImage(reopened, beforeMarkers);
                }
            }
            finally
            {
                bitmap?.Dispose();
                bitmap = null;
                operations.RestoreWindowState(originalState);
            }

            File.Move(temporaryPath, outputPath);
            return new MediaAssetCaptureEvidence(
                workflow,
                phase,
                focusAutomationId,
                Path.GetFileName(outputPath),
                Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(outputPath))),
                targetBounds.Width,
                targetBounds.Height,
                ToEvidence(session.Identity),
                capturedMarkers!,
                focusBefore!,
                focusAfter!);
        }
        catch
        {
            File.Delete(temporaryPath);
            throw;
        }
        finally
        {
            bitmap?.Dispose();
            File.Delete(temporaryPath);
        }
    }

    internal static MediaAssetAppIdentityEvidence ToEvidence(ReceiptBoundAppIdentity identity) => new(
        identity.ProcessId,
        identity.ProcessStartTimeUtc,
        identity.ExecutablePath,
        identity.ExecutableSha256,
        identity.ProductAssemblyPath,
        identity.ProductAssemblySha256,
        identity.MainWindowHandle.ToInt64(),
        identity.UiaNativeWindowHandle.ToInt64(),
        identity.WindowOwnerProcessId);

    private static void FocusExactTarget(MediaAssetNativeSession session, string automationId)
    {
        AutomationElement target = FindByAutomationId(session.Window, automationId);
        target.Focus();
        bool focused = Retry.WhileFalse(
            () => TryReadExactFocus(session, automationId, out _),
            TimeSpan.FromSeconds(5),
            TimeSpan.FromMilliseconds(100)).Success;
        Assert.That(focused, Is.True, $"Media/Asset focus did not settle on {automationId}.");
    }

    private static MediaAssetFocusObservation ReadExactFocus(
        MediaAssetNativeSession session,
        string automationId,
        Rectangle windowBounds)
    {
        Assert.That(
            TryReadExactFocus(session, automationId, out AutomationElement? focused),
            Is.True,
            $"Media/Asset focus is not bound to exact target {automationId}.");
        Rectangle bounds = focused!.BoundingRectangle;
        var relative = new Rectangle(
            bounds.Left - windowBounds.Left,
            bounds.Top - windowBounds.Top,
            bounds.Width,
            bounds.Height);
        Assert.That(IsInside(relative, windowBounds.Size), Is.True);
        return new MediaAssetFocusObservation(
            automationId,
            session.Identity.ProcessId,
            session.Identity.MainWindowHandle.ToInt64(),
            relative.X,
            relative.Y,
            relative.Width,
            relative.Height,
            true);
    }

    private static bool TryReadExactFocus(
        MediaAssetNativeSession session,
        string automationId,
        out AutomationElement? focused)
    {
        focused = null;
        try
        {
            AutomationElement? global = session.Automation.FocusedElement();
            AutomationElement? scoped = session.Window.FindFirstDescendant(cf => cf.ByAutomationId(automationId));
            if (global is null || scoped is null)
            {
                return false;
            }

            bool exact =
                string.Equals(global.AutomationId, automationId, StringComparison.Ordinal) &&
                string.Equals(scoped.AutomationId, automationId, StringComparison.Ordinal) &&
                global.Properties.ProcessId.ValueOrDefault == session.Identity.ProcessId &&
                scoped.Properties.ProcessId.ValueOrDefault == session.Identity.ProcessId &&
                global.BoundingRectangle == scoped.BoundingRectangle &&
                global.Properties.HasKeyboardFocus.ValueOrDefault &&
                scoped.Properties.HasKeyboardFocus.ValueOrDefault;
            if (exact)
            {
                focused = global;
            }
            return exact;
        }
        catch
        {
            return false;
        }
    }

    private static void WaitForMarkerStability(
        FlaUiReceiptBoundVisualCaptureOperations operations,
        IReadOnlyList<string> automationIds,
        Size imageSize)
    {
        IReadOnlyList<GuidedSaveVisualMarker>? prior = null;
        int stableSamples = 0;
        bool stable = Retry.WhileFalse(
            () =>
            {
                IReadOnlyList<GuidedSaveVisualMarker> current = automationIds
                    .Select(operations.ReadMarker)
                    .ToArray();
                bool allInside = current.All(marker => IsInside(marker.Bounds, imageSize));
                if (allInside && prior is not null && current.SequenceEqual(prior))
                {
                    stableSamples++;
                }
                else
                {
                    stableSamples = 0;
                }
                prior = current;
                return stableSamples >= 2;
            },
            TimeSpan.FromSeconds(5),
            TimeSpan.FromMilliseconds(100)).Success;
        string finalObservations = prior is null
            ? "no marker observations"
            : string.Join(
                "; ",
                prior.Select(marker =>
                    $"{marker.Name}={marker.Bounds} inside={IsInside(marker.Bounds, imageSize)}"));
        Assert.That(
            stable,
            Is.True,
            $"Media/Asset markers did not become visible and stable inside the bound HWND: {finalObservations}.");
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () => window.FindFirstDescendant(cf => cf.ByAutomationId(automationId)),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected Media/Asset automation element: {automationId}");
        return element!;
    }

    private static void AssertMarkersInsideImage(
        IReadOnlyList<GuidedSaveVisualMarker> markers,
        Size imageSize)
    {
        foreach (GuidedSaveVisualMarker marker in markers)
        {
            Assert.That(
                IsInside(marker.Bounds, imageSize),
                Is.True,
                $"Media/Asset marker {marker.Name} is outside the receipt-bound image.");
        }
    }

    private static bool IsInside(Rectangle bounds, Size imageSize) =>
        bounds.Width > 0 && bounds.Height > 0 &&
        bounds.Left >= 0 && bounds.Top >= 0 &&
        bounds.Right <= imageSize.Width && bounds.Bottom <= imageSize.Height;

    private static void AssertToolkitImage(Bitmap bitmap, IReadOnlyList<GuidedSaveVisualMarker> markers)
    {
        Assert.That(HasKnownCodexDesktopSignature(bitmap), Is.False);
        Assert.That(ToolkitVisualEvidenceAcceptance.HasMeaningfulFrameCoverage(bitmap), Is.True);
        Assert.That(ToolkitVisualEvidenceAcceptance.HasRenderedToolkitHeader(bitmap), Is.True);
        foreach (GuidedSaveVisualMarker marker in markers)
        {
            Assert.That(
                ToolkitVisualEvidenceAcceptance.HasRenderedActivity(bitmap, marker.Bounds),
                Is.True,
                $"Media/Asset marker {marker.Name} at {marker.Bounds} is not visibly rendered.");
        }
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
}
