// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// A top-down picture of a level's terrain: its 512 x 512 world square, <see cref="PixelsPerUnit"/> pixels to the world unit, as
/// RGBA bytes. Column 0 is world X = 0 and row 0 is the top, world Y = 512, so X runs right and Y runs up, as on the map. The
/// pixel <c>(column, row)</c> shows the terrain at its centre.
/// </summary>
public sealed record ReliefImage(int PixelsPerUnit, int Width, int Height, byte[] Rgba)
{
    /// <summary>The pixel that shows the world position, or null outside the square.</summary>
    public (int Column, int Row)? PixelOf(float x, float y) =>
        x is >= 0 and < Heightfield.Size && y is >= 0 and < Heightfield.Size ? ((int)(x * PixelsPerUnit), Height - 1 - (int)(y * PixelsPerUnit)) : null;

    /// <summary>The pixel's red, green and blue.</summary>
    public (byte R, byte G, byte B) Color(int column, int row)
    {
        int at = (row * Width + column) * 4;
        return (Rgba[at], Rgba[at + 1], Rgba[at + 2]);
    }
}

/// <summary>
/// Hill-shaded relief of a <see cref="Heightfield"/>: the ground is lit from the north-west, coloured by its height from dark to
/// pale, and water (ground whose height is greater than the water's, Z being down) has its own tint that deepens with depth. The
/// heights are the game's own lookup (<see cref="Heightfield.HeightAt"/>), so a pixel shows what the game's code finds there. The
/// slopes are exaggerated for the eye. No retail texture is used.
/// </summary>
public static class TerrainRelief
{
    private const float Exaggeration = 3f;

    public static ReliefImage Build(Heightfield field, int pixelsPerUnit = 1)
    {
        if (pixelsPerUnit is < 1 or > 4) throw new ArgumentOutOfRangeException(nameof(pixelsPerUnit));
        int size = (int)Heightfield.Size * pixelsPerUnit, stride = size + 2;
        float step = 1f / pixelsPerUnit;
        // Elevation (up positive) at every pixel centre and one pixel beyond, with positions clamped into the square.
        float[] up = new float[stride * stride];
        float low = float.MaxValue, high = float.MinValue;
        for (int row = -1; row <= size; row++)
        {
            float y = Math.Clamp(Heightfield.Size - (Math.Clamp(row, 0, size - 1) + 0.5f) * step, 0f, Heightfield.Size - 0.01f);
            for (int column = -1; column <= size; column++)
            {
                float x = Math.Clamp((Math.Clamp(column, 0, size - 1) + 0.5f) * step, 0f, Heightfield.Size - 0.01f);
                float elevation = -field.HeightAt(x, y);
                up[(row + 1) * stride + column + 1] = elevation;
                low = Math.Min(low, elevation);
                high = Math.Max(high, elevation);
            }
        }
        float range = Math.Max(high - low, 0.001f);
        float waterElevation = -field.Water;
        // The light, from the north-west and 45 degrees up: east -0.5, north 0.5, up 0.7071; a flat surface is 0.7071 lit.
        const float lightX = -0.5f, lightY = 0.5f, lightZ = 0.70710677f;
        byte[] rgba = new byte[size * size * 4];
        for (int row = 0; row < size; row++)
        {
            for (int column = 0; column < size; column++)
            {
                int centre = (row + 1) * stride + column + 1;
                float elevation = up[centre];
                float eastSlope = (up[centre + 1] - up[centre - 1]) / (2 * step) * Exaggeration;
                float northSlope = (up[centre - stride] - up[centre + stride]) / (2 * step) * Exaggeration;
                float length = MathF.Sqrt(eastSlope * eastSlope + northSlope * northSlope + 1f);
                float lit = Math.Clamp((-eastSlope * lightX - northSlope * lightY + lightZ) / length / lightZ, 0f, 1.5f);
                float r, g, b;
                if (elevation < waterElevation)
                {
                    float depth = Math.Clamp((waterElevation - elevation) / 4f, 0f, 1f);
                    r = 0.10f - 0.05f * depth;
                    g = 0.24f - 0.11f * depth;
                    b = 0.36f - 0.14f * depth;
                    lit = 0.9f + 0.1f * lit;  // water shows its floor a little, not as hills
                }
                else
                {
                    float t = Math.Clamp((elevation - low) / range, 0f, 1f);
                    r = 0.22f + 0.48f * t;
                    g = 0.30f + 0.36f * t;
                    b = 0.22f + 0.30f * t;
                }
                float shade = 0.55f + 0.45f * lit;
                int at = (row * size + column) * 4;
                rgba[at] = Channel(r * shade);
                rgba[at + 1] = Channel(g * shade);
                rgba[at + 2] = Channel(b * shade);
                rgba[at + 3] = 255;
            }
        }
        return new ReliefImage(pixelsPerUnit, size, size, rgba);
    }

    private static byte Channel(float value) => (byte)Math.Clamp((int)MathF.Round(value * 255f), 0, 255);
}
