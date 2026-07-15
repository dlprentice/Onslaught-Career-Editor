using System.Drawing;

namespace OnslaughtCareerEditor.UiTests;

internal static class HomeVisualEvidenceAcceptance
{
    internal static bool HasMeaningfulFrameCoverage(Bitmap bitmap)
    {
        if (bitmap.Width < 320 || bitmap.Height < 320)
        {
            return false;
        }

        int samples = 0;
        int opaque = 0;
        int nonDark = 0;
        int minimumLuminance = 255;
        int maximumLuminance = 0;
        var colors = new HashSet<int>();
        for (int y = 0; y < bitmap.Height; y += 4)
        {
            for (int x = 0; x < bitmap.Width; x += 4)
            {
                Color pixel = bitmap.GetPixel(x, y);
                samples++;
                if (pixel.A >= 250)
                {
                    opaque++;
                }

                int luminance = Luminance(pixel);
                if (luminance >= 32)
                {
                    nonDark++;
                }

                minimumLuminance = Math.Min(minimumLuminance, luminance);
                maximumLuminance = Math.Max(maximumLuminance, luminance);
                colors.Add(Quantize(pixel));
            }
        }

        return samples > 0
            && opaque >= samples * 99 / 100
            && nonDark >= samples * 7 / 10
            && colors.Count >= 8
            && maximumLuminance - minimumLuminance >= 80;
    }

    internal static bool HasRenderedToolkitHeader(Bitmap bitmap)
    {
        if (bitmap.Width < 320 || bitmap.Height < 117)
        {
            return false;
        }

        int samples = 0;
        int blueOpaque = 0;
        for (int y = 40; y <= 115; y += 4)
        {
            for (int x = 0; x < bitmap.Width; x += 4)
            {
                Color pixel = bitmap.GetPixel(x, y);
                samples++;
                if (pixel.A >= 250 && pixel.B >= pixel.R + 40 && pixel.B >= pixel.G + 30)
                {
                    blueOpaque++;
                }
            }
        }

        return samples > 0 && blueOpaque >= samples * 7 / 10;
    }

    internal static bool HasRenderedActivity(Bitmap bitmap, Rectangle bounds)
    {
        int left = Math.Clamp(bounds.Left, 0, bitmap.Width - 1);
        int top = Math.Clamp(bounds.Top, 0, bitmap.Height - 1);
        int right = Math.Clamp(bounds.Right - 1, left, bitmap.Width - 1);
        int bottom = Math.Clamp(bounds.Bottom - 1, top, bitmap.Height - 1);
        if (right - left < 3 || bottom - top < 3)
        {
            return false;
        }

        int samples = 0;
        int opaque = 0;
        int minimumLuminance = 255;
        int maximumLuminance = 0;
        int transitions = 0;
        var colors = new HashSet<int>();
        var priorRows = new Dictionary<int, Color>();
        for (int y = top; y <= bottom; y += 2)
        {
            Color? prior = null;
            for (int x = left; x <= right; x += 2)
            {
                Color pixel = bitmap.GetPixel(x, y);
                samples++;
                if (pixel.A >= 250)
                {
                    opaque++;
                }

                int luminance = Luminance(pixel);
                minimumLuminance = Math.Min(minimumLuminance, luminance);
                maximumLuminance = Math.Max(maximumLuminance, luminance);
                colors.Add(Quantize(pixel));
                if (prior is Color leftPixel && ColorDistance(pixel, leftPixel) >= 24)
                {
                    transitions++;
                }

                if (priorRows.TryGetValue(x, out Color abovePixel) && ColorDistance(pixel, abovePixel) >= 24)
                {
                    transitions++;
                }

                prior = pixel;
                priorRows[x] = pixel;
            }
        }

        return samples > 0
            && opaque >= samples * 98 / 100
            && colors.Count >= 3
            && maximumLuminance - minimumLuminance >= 20
            && transitions >= Math.Max(8, samples / 100);
    }

    private static int Quantize(Color pixel) =>
        ((pixel.R >> 4) << 8) | ((pixel.G >> 4) << 4) | (pixel.B >> 4);

    private static int Luminance(Color pixel) =>
        (pixel.R * 299 + pixel.G * 587 + pixel.B * 114) / 1000;

    private static int ColorDistance(Color left, Color right) =>
        Math.Abs(left.R - right.R) + Math.Abs(left.G - right.G) + Math.Abs(left.B - right.B);
}
