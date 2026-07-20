// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using System.Reflection;
using System.Security.Cryptography;

namespace OnslaughtRebuild.Core;

/// <summary>
/// The one retained Level 100 HFLD and the released Steam height sampler used
/// for deterministic simulation. Presentation clients may adapt its metadata,
/// but do not own a second terrain sampler.
/// </summary>
public sealed class Level100Terrain
{
    public const string SourceSha256 =
        "7A4C7C5B9400E2C8D2325CECB5C44701CD8A6E6F8609CBC8BC31D449C0620F5D";
    public const int FixedPointUnitsPerRetailUnit = 256;
    public const int MapExtentRetailUnits = 512;
    public const int PlayerStartRetailXFixed = 73_904;
    public const int PlayerStartRetailYFixed = 62_272;
    public const int PlayerStartReferenceElevationMillimeters = -10_000;
    public const int WalkerCenterOfGravityMillimeters = 1_900;

    private const string ResourceName =
        "OnslaughtRebuild.Core.Assets.Level100.level100-heightfield.hfld.bin";
    private const int HfldPayloadSize = 668_652;
    private const int ChfdPayloadSize = 5_084;
    private const int HfdtPayloadSize = 663_552;
    private const int HeightScaleOffset = 0x102C;
    private const int MixerSetOffset = 0x1030;
    private const int WaterLevelOffset = 0x1034;
    private const int FogColorOffset = 0x1078;
    private const int SunColorOffset = 0x107C;
    private const int AntiSunColorOffset = 0x1080;
    private const int AmbientColorOffset = 0x108C;
    private const int SkyCubeOffset = 0x1090;
    private const int DetailTextureOffset = 0x1094;
    private const int WaterTextureOffset = 0x1095;
    private const int FogDensityOffset = 0x1098;
    private const int SunPositionOffset = 0x10A4;
    private const int TileCountPerAxis = 64;
    private const int TileWidth = 8;
    private const int SamplesPerTileAxis = 9;
    private const int SamplesPerTile = SamplesPerTileAxis * SamplesPerTileAxis;
    private const int MaximumFixedCoordinate =
        MapExtentRetailUnits * FixedPointUnitsPerRetailUnit;

    private static readonly uint s_hfldTag = Tag("HFLD");
    private static readonly uint s_chfdTag = Tag("CHFD");
    private static readonly uint s_hfdtTag = Tag("HFDT");

    private readonly short[] _heightSamples;
    private readonly int _heightScaleSignificand;
    private readonly long _heightScaleDenominator;

    private Level100Terrain(
        short[] heightSamples,
        int heightScaleBits,
        byte mixerSet,
        byte skyCube,
        byte detailTexture,
        float waterLevel,
        byte waterTexture,
        uint fogColor,
        float fogDensity,
        uint sunColor,
        uint antiSunColor,
        uint ambientColor,
        float sunPositionX,
        float sunPositionY,
        float sunPositionZ)
    {
        _heightSamples = heightSamples;
        HeightScale = BitConverter.Int32BitsToSingle(heightScaleBits);
        (_heightScaleSignificand, _heightScaleDenominator) =
            DecodePositiveFloatScale(heightScaleBits);
        MixerSet = mixerSet;
        SkyCube = skyCube;
        DetailTexture = detailTexture;
        WaterLevel = waterLevel;
        WaterTexture = waterTexture;
        FogColorRgb24 = fogColor;
        FogDensity = fogDensity;
        SunColorRgb24 = sunColor;
        AntiSunColorRgb24 = antiSunColor;
        AmbientColorRgb24 = ambientColor;
        SunPositionX = sunPositionX;
        SunPositionY = sunPositionY;
        SunPositionZ = sunPositionZ;
    }

    public static Level100Terrain Instance { get; } = LoadEmbedded();

    public float HeightScale { get; }

    public byte MixerSet { get; }

    public byte SkyCube { get; }

    public byte DetailTexture { get; }

    public float WaterLevel { get; }

    public byte WaterTexture { get; }

    public uint FogColorRgb24 { get; }

    public float FogDensity { get; }

    public uint SunColorRgb24 { get; }

    public uint AntiSunColorRgb24 { get; }

    public uint AmbientColorRgb24 { get; }

    public float SunPositionX { get; }

    public float SunPositionY { get; }

    public float SunPositionZ { get; }

    /// <summary>
    /// Samples the signed HFLD unit used by Steam at 0x0047EB80. Coordinates
    /// are unsigned 24.8 fixed point; interpolation truncates after each axis.
    /// Outside the 512-unit map, the released helper returns the flat zero.
    /// </summary>
    public int SampleHeightUnitsAtFixed(int retailXFixed, int retailYFixed)
    {
        if ((uint)retailXFixed >= MaximumFixedCoordinate ||
            (uint)retailYFixed >= MaximumFixedCoordinate)
        {
            return 0;
        }

        int tileX = (retailXFixed >> 11) & 0x3F;
        int tileY = (retailYFixed >> 11) & 0x3F;
        int localX = (retailXFixed >> 8) & 0x07;
        int localY = (retailYFixed >> 8) & 0x07;
        int sampleIndex =
            (((tileX * TileCountPerAxis) + tileY) * SamplesPerTile) +
            (localY * SamplesPerTileAxis) +
            localX;
        int fractionX = retailXFixed & 0xFF;
        int fractionY = retailYFixed & 0xFF;

        int nearLeft = _heightSamples[sampleIndex];
        int near = nearLeft +
            (((_heightSamples[sampleIndex + 1] - nearLeft) * fractionX) >> 8);
        int farLeft = _heightSamples[sampleIndex + SamplesPerTileAxis];
        int far = farLeft +
            (((_heightSamples[sampleIndex + SamplesPerTileAxis + 1] - farLeft) * fractionX) >> 8);
        return near + (((far - near) * fractionY) >> 8);
    }

    /// <summary>
    /// Returns an exact integer HFLD sample for the released 65×65 coarse
    /// render grid, including its 512-unit far edge.
    /// </summary>
    public int SampleGridHeightUnits(int retailX, int retailY)
    {
        if ((uint)retailX > MapExtentRetailUnits)
        {
            throw new ArgumentOutOfRangeException(
                nameof(retailX),
                "Level 100 grid coordinates must be between 0 and 512.");
        }
        if ((uint)retailY > MapExtentRetailUnits)
        {
            throw new ArgumentOutOfRangeException(
                nameof(retailY),
                "Level 100 grid coordinates must be between 0 and 512.");
        }

        int tileX = Math.Min(retailX / TileWidth, TileCountPerAxis - 1);
        int tileY = Math.Min(retailY / TileWidth, TileCountPerAxis - 1);
        int localX = retailX == MapExtentRetailUnits ? TileWidth : retailX % TileWidth;
        int localY = retailY == MapExtentRetailUnits ? TileWidth : retailY % TileWidth;
        int sampleIndex =
            (((tileX * TileCountPerAxis) + tileY) * SamplesPerTile) +
            (localY * SamplesPerTileAxis) +
            localX;
        return _heightSamples[sampleIndex];
    }

    /// <summary>
    /// Returns Level 100 ground elevation relative to the authored -10-unit
    /// presentation plane. Core positions are millimetres from player start.
    /// </summary>
    public int SampleGroundElevationMillimeters(SimVector2 relativePosition)
    {
        int retailXFixed = checked(
            PlayerStartRetailXFixed +
            (int)FloorDivide((long)relativePosition.X * FixedPointUnitsPerRetailUnit, 1_000));
        int retailYFixed = checked(
            PlayerStartRetailYFixed +
            (int)FloorDivide((long)relativePosition.Z * FixedPointUnitsPerRetailUnit, 1_000));
        int heightUnits = SampleHeightUnitsAtFixed(retailXFixed, retailYFixed);

        long relativeGroundNumerator =
            ((long)PlayerStartReferenceElevationMillimeters * _heightScaleDenominator) -
            ((long)heightUnits * _heightScaleSignificand * 1_000L);
        return checked((int)RoundDivideAwayFromZero(
            relativeGroundNumerator,
            _heightScaleDenominator));
    }

    private static Level100Terrain LoadEmbedded()
    {
        Assembly assembly = typeof(Level100Terrain).Assembly;
        using Stream stream = assembly.GetManifestResourceStream(ResourceName) ??
            throw new InvalidDataException("The retained Level 100 HFLD resource is missing.");
        if (stream.Length != HfldPayloadSize + 8)
        {
            throw new InvalidDataException("The retained Level 100 HFLD has an unexpected length.");
        }

        var source = new byte[stream.Length];
        stream.ReadExactly(source);
        string hash = Convert.ToHexString(SHA256.HashData(source));
        if (!StringComparer.Ordinal.Equals(hash, SourceSha256))
        {
            throw new InvalidDataException("The retained Level 100 HFLD hash does not match its provenance.");
        }

        if (ReadUInt32(source, 0) != s_hfldTag || ReadUInt32(source, 4) != HfldPayloadSize)
        {
            throw new InvalidDataException("The retained Level 100 HFLD has an unexpected envelope.");
        }

        const int chfdHeaderOffset = 8;
        const int chfdPayloadOffset = chfdHeaderOffset + 8;
        if (ReadUInt32(source, chfdHeaderOffset) != s_chfdTag ||
            ReadUInt32(source, chfdHeaderOffset + 4) != ChfdPayloadSize)
        {
            throw new InvalidDataException("The retained Level 100 HFLD is missing CHFD metadata.");
        }

        int hfdtHeaderOffset = chfdPayloadOffset + ChfdPayloadSize;
        int hfdtPayloadOffset = hfdtHeaderOffset + 8;
        if (ReadUInt32(source, hfdtHeaderOffset) != s_hfdtTag ||
            ReadUInt32(source, hfdtHeaderOffset + 4) != HfdtPayloadSize ||
            hfdtPayloadOffset + HfdtPayloadSize != source.Length)
        {
            throw new InvalidDataException("The retained Level 100 HFLD is missing its exact sample block.");
        }

        int heightScaleBits = BinaryPrimitives.ReadInt32LittleEndian(
            source.AsSpan(chfdPayloadOffset + HeightScaleOffset, sizeof(int)));
        float heightScale = BitConverter.Int32BitsToSingle(heightScaleBits);
        if (!float.IsFinite(heightScale) || heightScale <= 0f)
        {
            throw new InvalidDataException("The retained Level 100 HFLD has an invalid height scale.");
        }

        float fogDensity = ReadSingle(source, chfdPayloadOffset + FogDensityOffset);
        float waterLevel = ReadSingle(source, chfdPayloadOffset + WaterLevelOffset);
        float sunPositionX = ReadSingle(source, chfdPayloadOffset + SunPositionOffset);
        float sunPositionY = ReadSingle(source, chfdPayloadOffset + SunPositionOffset + sizeof(float));
        float sunPositionZ = ReadSingle(source, chfdPayloadOffset + SunPositionOffset + (sizeof(float) * 2));
        if (!float.IsFinite(fogDensity) || fogDensity < 0f ||
            !float.IsFinite(waterLevel) ||
            !float.IsFinite(sunPositionX) ||
            !float.IsFinite(sunPositionY) ||
            !float.IsFinite(sunPositionZ) ||
            (sunPositionX == 0f && sunPositionY == 0f && sunPositionZ == 0f))
        {
            throw new InvalidDataException("The retained Level 100 HFLD has invalid environment metadata.");
        }

        var samples = new short[HfdtPayloadSize / sizeof(short)];
        for (int index = 0; index < samples.Length; index++)
        {
            samples[index] = BinaryPrimitives.ReadInt16LittleEndian(
                source.AsSpan(hfdtPayloadOffset + (index * sizeof(short)), sizeof(short)));
        }

        return new Level100Terrain(
            samples,
            heightScaleBits,
            source[chfdPayloadOffset + MixerSetOffset],
            source[chfdPayloadOffset + SkyCubeOffset],
            source[chfdPayloadOffset + DetailTextureOffset],
            waterLevel,
            source[chfdPayloadOffset + WaterTextureOffset],
            ReadUInt32(source, chfdPayloadOffset + FogColorOffset),
            fogDensity,
            ReadUInt32(source, chfdPayloadOffset + SunColorOffset),
            ReadUInt32(source, chfdPayloadOffset + AntiSunColorOffset),
            ReadUInt32(source, chfdPayloadOffset + AmbientColorOffset),
            sunPositionX,
            sunPositionY,
            sunPositionZ);
    }

    private static (int Significand, long Denominator) DecodePositiveFloatScale(int bits)
    {
        int exponentBits = (bits >> 23) & 0xFF;
        int fraction = bits & 0x7FFFFF;
        if (bits < 0 || exponentBits is 0 or 0xFF)
        {
            throw new InvalidDataException("The Level 100 height scale is not a positive normal float.");
        }

        int significand = (1 << 23) | fraction;
        int binaryExponent = exponentBits - 127 - 23;
        if (binaryExponent > 0 || binaryExponent < -62)
        {
            throw new InvalidDataException("The Level 100 height scale is outside the exact fixed range.");
        }

        return (significand, 1L << -binaryExponent);
    }

    private static long FloorDivide(long value, long denominator)
    {
        long quotient = value / denominator;
        return value % denominator < 0 ? quotient - 1 : quotient;
    }

    private static long RoundDivideAwayFromZero(long value, long denominator)
    {
        if (value >= 0)
        {
            return (value + (denominator / 2)) / denominator;
        }

        return -((-value + (denominator / 2)) / denominator);
    }

    private static uint ReadUInt32(byte[] source, int offset) =>
        BinaryPrimitives.ReadUInt32LittleEndian(source.AsSpan(offset, sizeof(uint)));

    private static float ReadSingle(byte[] source, int offset) =>
        BitConverter.Int32BitsToSingle(
            BinaryPrimitives.ReadInt32LittleEndian(source.AsSpan(offset, sizeof(float))));

    private static uint Tag(string value) =>
        (uint)value[0] |
        ((uint)value[1] << 8) |
        ((uint)value[2] << 16) |
        ((uint)value[3] << 24);
}
