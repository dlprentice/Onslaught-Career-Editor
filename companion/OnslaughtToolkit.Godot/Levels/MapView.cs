// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// Where the world sits in a map control of a given size: the one pair of functions between world positions (X right, Y up) and
/// pixels (x right, y down), with pan and zoom. The control draws and hit-tests through it, and nothing else converts between the
/// two, so what is tested here is what is on screen. No interface types.
/// </summary>
public sealed class MapView
{
    /// <summary>The world square the terrain covers.</summary>
    public const double WorldSize = 512;

    /// <summary>The most pixels to a world unit the map zooms in to.</summary>
    public const double MaxScale = 32;

    /// <summary>Whether the player has zoomed or panned since the view last fitted the square: until then a new size shows the whole square again.</summary>
    private bool _moved;

    public double Width { get; private set; }
    public double Height { get; private set; }

    /// <summary>Pixels to the world unit.</summary>
    public double Scale { get; private set; } = 1;

    /// <summary>The world position at the middle of the view.</summary>
    public double CenterX { get; private set; } = WorldSize / 2;

    public double CenterY { get; private set; } = WorldSize / 2;

    /// <summary>The scale at which the whole square fits the view with a small margin.</summary>
    public double FitScale => Math.Max(Math.Min(Width, Height) / (WorldSize * 1.04), 0.01);

    /// <summary>The smallest scale: half what fits the square.</summary>
    public double MinScale => FitScale / 2;

    /// <summary>
    /// A new size. Until the player zooms or pans, the whole square is shown again at the new size (a control is laid out more than once on
    /// its way to its final size, and a window can be resized); after that the world position at the middle stays there and the scale
    /// stays within its limits for the new size.
    /// </summary>
    public void Resize(double width, double height)
    {
        Width = Math.Max(width, 1);
        Height = Math.Max(height, 1);
        if (!_moved) Fit();
        else Scale = Math.Clamp(Scale, MinScale, MaxScale);
    }

    /// <summary>Shows the whole square, centred.</summary>
    public void Fit()
    {
        Scale = FitScale;
        CenterX = CenterY = WorldSize / 2;
        _moved = false;
    }

    /// <summary>
    /// The coordinate a pointer position means, to a hundredth of a world unit as the float32 nearest that decimal, so that the number
    /// shown for it is the number written (a float multiplied by 0.01f, 24002f * 0.01f, is 240.01999 and not 240.02).
    /// </summary>
    public static float ToHundredths(double value) => (float)(Math.Round(value / 0.01) * 0.01);

    /// <summary>The pixel that shows a world position.</summary>
    public (double X, double Y) ToScreen(double x, double y) => ((x - CenterX) * Scale + Width / 2, (CenterY - y) * Scale + Height / 2);

    /// <summary>The world position under a pixel.</summary>
    public (double X, double Y) ToWorld(double screenX, double screenY) => (CenterX + (screenX - Width / 2) / Scale, CenterY - (screenY - Height / 2) / Scale);

    /// <summary>Zooms by a factor about a pixel: the world position under it stays under it (until the scale hits its limits).</summary>
    public void ZoomAbout(double screenX, double screenY, double factor)
    {
        (double wx, double wy) = ToWorld(screenX, screenY);
        Scale = Math.Clamp(Scale * factor, MinScale, MaxScale);
        // Put (wx, wy) back under the pixel: the centre is wx minus the pixel's offset from the middle, in world units at the new scale.
        CenterX = wx - (screenX - Width / 2) / Scale;
        CenterY = wy + (screenY - Height / 2) / Scale;
        KeepCentreInside();
        _moved = true;
    }

    /// <summary>Moves the content by a number of pixels (a drag of the background to the right shows more of the left).</summary>
    public void Pan(double dx, double dy)
    {
        CenterX -= dx / Scale;
        CenterY += dy / Scale;
        KeepCentreInside();
        _moved = true;
    }

    private void KeepCentreInside()
    {
        CenterX = Math.Clamp(CenterX, 0, WorldSize);
        CenterY = Math.Clamp(CenterY, 0, WorldSize);
    }

    /// <summary>
    /// The index of the position nearest a pixel within <paramref name="maxPixels"/> of it, or null: <paramref name="positions"/>
    /// holds each candidate's index and world position. On a tie the one listed first wins.
    /// </summary>
    public int? Nearest(IEnumerable<(int Index, double X, double Y)> positions, double screenX, double screenY, double maxPixels)
    {
        int? best = null;
        double bestDistance = maxPixels * maxPixels;
        foreach ((int index, double x, double y) in positions)
        {
            (double sx, double sy) = ToScreen(x, y);
            double distance = (sx - screenX) * (sx - screenX) + (sy - screenY) * (sy - screenY);
            if (distance < bestDistance)
            {
                bestDistance = distance;
                best = index;
            }
        }
        return best;
    }
}
