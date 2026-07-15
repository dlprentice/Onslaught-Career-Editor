using System.Drawing;

namespace OnslaughtCareerEditor.UiTests;

public class HomeVisualEvidenceAcceptanceTests
{
    [Test]
    public void GenericToolkitChecks_MatchHomeCompatibilityWrapper()
    {
        using var bitmap = new Bitmap(760, 820);
        using (Graphics graphics = Graphics.FromImage(bitmap))
        {
            graphics.Clear(Color.FromArgb(255, 244, 246, 252));
            using var headerBrush = new SolidBrush(Color.FromArgb(255, 32, 52, 154));
            graphics.FillRectangle(headerBrush, 0, 36, bitmap.Width, 90);
            using var cardBrush = new SolidBrush(Color.White);
            graphics.FillRectangle(cardBrush, 64, 170, 632, 72);
            using var textBrush = new SolidBrush(Color.FromArgb(255, 28, 35, 55));
            graphics.FillRectangle(textBrush, 84, 190, 420, 12);
            graphics.FillRectangle(textBrush, 84, 216, 260, 8);
        }

        var marker = new Rectangle(64, 170, 632, 72);
        Assert.Multiple(() =>
        {
            Assert.That(
                ToolkitVisualEvidenceAcceptance.HasMeaningfulFrameCoverage(bitmap),
                Is.EqualTo(HomeVisualEvidenceAcceptance.HasMeaningfulFrameCoverage(bitmap)));
            Assert.That(
                ToolkitVisualEvidenceAcceptance.HasRenderedToolkitHeader(bitmap),
                Is.EqualTo(HomeVisualEvidenceAcceptance.HasRenderedToolkitHeader(bitmap)));
            Assert.That(
                ToolkitVisualEvidenceAcceptance.HasRenderedActivity(bitmap, marker),
                Is.EqualTo(HomeVisualEvidenceAcceptance.HasRenderedActivity(bitmap, marker)));
        });
    }

    [Test]
    public void NearBlackBitmapWithLegacyProbePixels_IsRejected()
    {
        using var bitmap = new Bitmap(760, 820);
        using (Graphics graphics = Graphics.FromImage(bitmap))
        {
            graphics.Clear(Color.Black);
        }

        foreach (int x in new[] { bitmap.Width / 4, bitmap.Width / 2, bitmap.Width * 3 / 4 })
        {
            foreach (int y in new[] { 50, 70, 90 })
            {
                bitmap.SetPixel(x, y, Color.FromArgb(255, 32, 52, 154));
            }
        }

        var marker = new Rectangle(100, 220, 240, 64);
        bitmap.SetPixel(marker.Left + marker.Width / 2, marker.Top + marker.Height / 2, Color.White);

        Assert.Multiple(() =>
        {
            Assert.That(HomeVisualEvidenceAcceptance.HasRenderedToolkitHeader(bitmap), Is.False);
            Assert.That(HomeVisualEvidenceAcceptance.HasMeaningfulFrameCoverage(bitmap), Is.False);
            Assert.That(HomeVisualEvidenceAcceptance.HasRenderedActivity(bitmap, marker), Is.False);
        });
    }

    [Test]
    public void OpaqueStructuredToolkitLikeBitmap_IsAccepted()
    {
        using var bitmap = new Bitmap(760, 820);
        using (Graphics graphics = Graphics.FromImage(bitmap))
        {
            graphics.Clear(Color.FromArgb(255, 244, 246, 252));
            using var headerBrush = new SolidBrush(Color.FromArgb(255, 32, 52, 154));
            graphics.FillRectangle(headerBrush, 0, 36, bitmap.Width, 90);
            using var cardBrush = new SolidBrush(Color.White);
            using var borderPen = new Pen(Color.FromArgb(255, 100, 110, 145), 2);
            using var textBrush = new SolidBrush(Color.FromArgb(255, 28, 35, 55));
            for (int row = 0; row < 6; row++)
            {
                var card = new Rectangle(64, 170 + row * 94, 632, 72);
                graphics.FillRectangle(cardBrush, card);
                graphics.DrawRectangle(borderPen, card);
                graphics.FillRectangle(textBrush, card.Left + 18, card.Top + 16, 260 + row * 24, 9);
                graphics.FillRectangle(textBrush, card.Left + 18, card.Top + 38, 150 + row * 18, 6);
                using var accentBrush = new SolidBrush(Color.FromArgb(255, 48 + row * 18, 82 + row * 13, 156 + row * 11));
                graphics.FillRectangle(accentBrush, card.Right - 54, card.Top + 18, 26, 26);
            }
        }

        var marker = new Rectangle(64, 170, 632, 72);
        Assert.Multiple(() =>
        {
            Assert.That(HomeVisualEvidenceAcceptance.HasRenderedToolkitHeader(bitmap), Is.True);
            Assert.That(HomeVisualEvidenceAcceptance.HasMeaningfulFrameCoverage(bitmap), Is.True);
            Assert.That(HomeVisualEvidenceAcceptance.HasRenderedActivity(bitmap, marker), Is.True);
        });
    }

    [Test]
    public void TransparentFrame_IsRejectedEvenWhenRgbLooksStructured()
    {
        using var bitmap = new Bitmap(760, 820);
        using (Graphics graphics = Graphics.FromImage(bitmap))
        {
            graphics.Clear(Color.FromArgb(40, 244, 246, 252));
            using var headerBrush = new SolidBrush(Color.FromArgb(40, 32, 52, 154));
            graphics.FillRectangle(headerBrush, 0, 36, bitmap.Width, 90);
        }

        Assert.That(HomeVisualEvidenceAcceptance.HasMeaningfulFrameCoverage(bitmap), Is.False);
    }
}
