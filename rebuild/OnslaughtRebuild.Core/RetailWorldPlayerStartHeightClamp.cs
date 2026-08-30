// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// One observable call to the released heightfield sampler while applying the
/// bounded <c>CStart::Init</c> terrain-height prefix.
/// </summary>
public sealed record RetailWorldPlayerStartHeightSample(
    int CallOrdinal,
    int PositionXFixed,
    int PositionYFixed,
    int HeightUnits,
    int HeightScaleBits,
    int HeightBits);

/// <summary>
/// Immutable output from the bounded player-start terrain clamp. The source
/// resolution remains available so authored identity, raw XY/Euler fields,
/// plane mode, and player number are not normalized into a runtime actor.
/// </summary>
public sealed class RetailWorldPlayerStartHeightClampResult
{
    private readonly IReadOnlyList<RetailWorldPlayerStartHeightSample> _samples;

    internal RetailWorldPlayerStartHeightClampResult(
        RetailWorldPlayerStartResolution resolution,
        string terrainPayloadSha256,
        int positionXFixed,
        int positionYFixed,
        int finalPositionZBits,
        bool heightWasClamped,
        IReadOnlyList<RetailWorldPlayerStartHeightSample> samples)
    {
        Resolution = resolution;
        TerrainPayloadSha256 = terrainPayloadSha256;
        PositionXFixed = positionXFixed;
        PositionYFixed = positionYFixed;
        FinalPositionZBits = finalPositionZBits;
        HeightWasClamped = heightWasClamped;
        _samples = Array.AsReadOnly(samples.ToArray());
    }

    public RetailWorldPlayerStartResolution Resolution { get; }

    public string TerrainPayloadSha256 { get; }

    public int ThingType => Resolution.ThingType;

    public int PositionXBits => Resolution.PositionXBits;

    public int PositionYBits => Resolution.PositionYBits;

    public int SerializedPositionZBits => Resolution.PositionZBits;

    public int PositionXFixed { get; }

    public int PositionYFixed { get; }

    public int FinalPositionZBits { get; }

    public int PlaneMode => Resolution.PlaneMode;

    public int PlayerNumber => Resolution.PlayerNumber;

    public RetailWorldPlayerStartRecord? AuthoredStart => Resolution.AuthoredStart;

    public string? AuthoredObjectIdentity => AuthoredStart?.ObjectIdentity;

    public int? OrientationXBits => AuthoredStart?.OrientationXBits;

    public int? OrientationYBits => AuthoredStart?.OrientationYBits;

    public int? OrientationZBits => AuthoredStart?.OrientationZBits;

    public bool HeightWasClamped { get; }

    public int SampleCallCount => _samples.Count;

    public IReadOnlyList<RetailWorldPlayerStartHeightSample> Samples => _samples;
}

/// <summary>
/// Carries only the 37-byte terrain-height prefix at pristine
/// <c>[0x004eae27, 0x004eae4c)</c>. Retail samples once, compares the sampled
/// height strictly below serialized Z, then samples again and stores that
/// second result only on the clamp arm. This owner excludes the setup bytes at
/// <c>0x004eae4c..0x004eae4e</c> and <c>CComplexThing::Init</c> at
/// <c>0x004eae4f</c>.
/// </summary>
public static class RetailWorldPlayerStartHeightClamp
{
    public static RetailWorldPlayerStartHeightClampResult Apply(
        RetailWorldPlayerStartResolution resolution,
        Level100Terrain terrain)
    {
        ArgumentNullException.ThrowIfNull(resolution);
        ArgumentNullException.ThrowIfNull(terrain);

        return Apply(
            resolution,
            terrain,
            terrain.SampleHeightUnitsAtFixed);
    }

    /// <summary>
    /// Internal seam for proving the released sampler call count and ordering.
    /// Production callers cannot supply a sampler; the public overload above
    /// always binds <see cref="Level100Terrain.SampleHeightUnitsAtFixed"/>.
    /// </summary>
    internal static RetailWorldPlayerStartHeightClampResult Apply(
        RetailWorldPlayerStartResolution resolution,
        Level100Terrain terrain,
        Func<int, int, int> sampleHeightUnitsAtFixed)
    {
        ArgumentNullException.ThrowIfNull(resolution);
        ArgumentNullException.ThrowIfNull(terrain);
        ArgumentNullException.ThrowIfNull(sampleHeightUnitsAtFixed);

        if (!StringComparer.OrdinalIgnoreCase.Equals(
                terrain.PayloadSha256,
                Level100Terrain.World110SourceSha256))
        {
            throw new ArgumentException(
                "The player-start height clamp requires the admitted world-110 HFLD.",
                nameof(terrain));
        }

        int positionXFixed = ToRetailFixed(
            resolution.PositionXBits,
            nameof(resolution));
        int positionYFixed = ToRetailFixed(
            resolution.PositionYBits,
            nameof(resolution));
        float serializedZ = BitConverter.Int32BitsToSingle(
            resolution.PositionZBits);
        if (!float.IsFinite(serializedZ))
        {
            throw new ArgumentException(
                "The player-start serialized Z must be finite.",
                nameof(resolution));
        }

        var samples = new List<RetailWorldPlayerStartHeightSample>(capacity: 2);
        RetailWorldPlayerStartHeightSample first = Sample(
            terrain,
            sampleHeightUnitsAtFixed,
            positionXFixed,
            positionYFixed,
            callOrdinal: 1);
        samples.Add(first);

        float firstHeight = BitConverter.Int32BitsToSingle(first.HeightBits);
        bool heightWasClamped = firstHeight < serializedZ;
        int finalPositionZBits = resolution.PositionZBits;
        if (heightWasClamped)
        {
            RetailWorldPlayerStartHeightSample second = Sample(
                terrain,
                sampleHeightUnitsAtFixed,
                positionXFixed,
                positionYFixed,
                callOrdinal: 2);
            samples.Add(second);
            finalPositionZBits = second.HeightBits;
        }

        return new RetailWorldPlayerStartHeightClampResult(
            resolution,
            Level100Terrain.World110SourceSha256,
            positionXFixed,
            positionYFixed,
            finalPositionZBits,
            heightWasClamped,
            samples);
    }

    private static RetailWorldPlayerStartHeightSample Sample(
        Level100Terrain terrain,
        Func<int, int, int> sampleHeightUnitsAtFixed,
        int positionXFixed,
        int positionYFixed,
        int callOrdinal)
    {
        int heightUnits = sampleHeightUnitsAtFixed(
            positionXFixed,
            positionYFixed);
        int heightScaleBits = BitConverter.SingleToInt32Bits(
            terrain.HeightScale);
        float height = heightUnits * terrain.HeightScale;
        return new RetailWorldPlayerStartHeightSample(
            callOrdinal,
            positionXFixed,
            positionYFixed,
            heightUnits,
            heightScaleBits,
            BitConverter.SingleToInt32Bits(height));
    }

    private static int ToRetailFixed(int coordinateBits, string parameterName)
    {
        float coordinate = BitConverter.Int32BitsToSingle(coordinateBits);
        float fixedCoordinate = MathF.Floor(
            coordinate * Level100Terrain.FixedPointUnitsPerRetailUnit);
        if (!float.IsFinite(fixedCoordinate) ||
            fixedCoordinate < int.MinValue ||
            fixedCoordinate > int.MaxValue)
        {
            throw new ArgumentException(
                "The player-start XY coordinates must be finite and representable.",
                parameterName);
        }

        return (int)fixedCoordinate;
    }
}
