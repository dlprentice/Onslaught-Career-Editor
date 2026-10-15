// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The companion's mark, drawn as vectors: a diamond with two stacked chevrons, amber over cyan.
/// <see cref="Icon"/> rasterises the same shapes for the window icon, so no image file exists.
/// </summary>
internal sealed partial class Emblem : Control
{
    // Unit-square geometry shared by the control and the icon.
    private static readonly Vector2[] Diamond = [new(0.5f, 0.08f), new(0.94f, 0.5f), new(0.5f, 0.92f), new(0.06f, 0.5f)];
    private static readonly Vector2[] Upper = [new(0.22f, 0.57f), new(0.5f, 0.32f), new(0.78f, 0.57f)];
    private static readonly Vector2[] Lower = [new(0.3f, 0.73f), new(0.5f, 0.55f), new(0.7f, 0.73f)];

    public override void _Draw()
    {
        Vector2 size = Size;
        DrawPolygon(ToSize(Diamond, size), [new Color(Palette.Accent, 0.14f)]);
        DrawPolyline(ToSize([.. Diamond, Diamond[0]], size), new Color(Palette.Accent, 0.45f), 1.2f, true);
        DrawPolyline(ToSize(Upper, size), Palette.Accent, Math.Max(2f, size.X * 0.085f), true);
        DrawPolyline(ToSize(Lower, size), Palette.Data, Math.Max(1.6f, size.X * 0.068f), true);
    }

    /// <summary>The window icon, rasterised with anti-aliased distance tests.</summary>
    internal static Image Icon(int pixels = 128)
    {
        Image image = Image.CreateEmpty(pixels, pixels, false, Image.Format.Rgba8);
        float feather = 1.2f / pixels;
        for (int y = 0; y < pixels; y++)
        {
            for (int x = 0; x < pixels; x++)
            {
                Vector2 point = new((x + 0.5f) / pixels, (y + 0.5f) / pixels);
                // A rounded, chamfered tile in the page colour carries the mark on any desktop.
                float tile = Coverage(ChamferedSquare(point, 0.06f, 0.16f), feather);
                Color color = new(Palette.Background, tile);
                color = Over(color, new Color(Palette.Accent, 0.16f * Coverage(-InsideDiamond(point), feather)));
                color = Over(color, new Color(Palette.Accent, Coverage(PolylineDistance(point, Upper) - 0.045f, feather)));
                color = Over(color, new Color(Palette.Data, Coverage(PolylineDistance(point, Lower) - 0.036f, feather)));
                image.SetPixel(x, y, color);
            }
        }
        return image;
    }

    private static Vector2[] ToSize(Vector2[] points, Vector2 size) => points.Select(point => point * size).ToArray();

    private static float Coverage(float signedDistance, float feather) => Math.Clamp(0.5f - signedDistance / feather, 0f, 1f);

    private static Color Over(Color below, Color above)
    {
        float alpha = above.A + below.A * (1 - above.A);
        if (alpha <= 0) return new Color(0, 0, 0, 0);
        Color mixed = (above * above.A + below * below.A * (1 - above.A)) / alpha;
        return new Color(mixed.R, mixed.G, mixed.B, alpha);
    }

    private static float ChamferedSquare(Vector2 point, float margin, float cut)
    {
        Vector2 q = (point - new Vector2(0.5f, 0.5f)).Abs();
        float half = 0.5f - margin;
        float box = Math.Max(q.X, q.Y) - half;
        float corner = (q.X + q.Y - (2 * half - cut)) / MathF.Sqrt(2);
        return Math.Max(box, corner);
    }

    private static float InsideDiamond(Vector2 point) =>
        -(Math.Abs(point.X - 0.5f) + Math.Abs(point.Y - 0.5f) - 0.42f);

    private static float PolylineDistance(Vector2 point, Vector2[] line)
    {
        float best = float.MaxValue;
        for (int index = 0; index + 1 < line.Length; index++)
        {
            Vector2 a = line[index], b = line[index + 1];
            Vector2 ab = b - a;
            float t = Math.Clamp((point - a).Dot(ab) / ab.LengthSquared(), 0f, 1f);
            best = Math.Min(best, point.DistanceTo(a + ab * t));
        }
        return best;
    }
}
