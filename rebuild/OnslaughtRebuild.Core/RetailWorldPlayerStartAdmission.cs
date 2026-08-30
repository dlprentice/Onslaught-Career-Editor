// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text;

namespace OnslaughtRebuild.Core;

/// <summary>
/// Exact serialized identity and start fields from one authored type-15
/// <c>CStartInitThing</c> record. Float fields remain their retail IEEE-754
/// bits so admission cannot erase negative zero or round an authored value.
/// </summary>
public sealed record RetailWorldPlayerStartRecord(
    string ObjectIdentity,
    int ThingType,
    int SerializedByteLength,
    string SerializedSha256,
    int PositionXBits,
    int PositionYBits,
    int PositionZBits,
    int OrientationXBits,
    int OrientationYBits,
    int OrientationZBits,
    int PlaneMode,
    int PlayerNumber);

/// <summary>
/// The bounded result of resolving a player number against an admitted world's
/// authored serialized starts. An absent match carries only the retail
/// fallback fields proven jointly by <c>CGame::PostLoadProcess</c> and the
/// <c>CStartInitThing</c> source defaults. This is a pre-init plan: it does not
/// invent configuration, orientation, Battle Engine construction or assignment,
/// the height clamp performed by <c>CStart::Init</c>, or presentation coordinates.
/// </summary>
public sealed class RetailWorldPlayerStartResolution
{
    public const int RetailDefaultThingType = 15;
    public const int RetailDefaultPositionXBits = 0x43800000;
    public const int RetailDefaultPositionYBits = 0x43800000;
    public const int RetailDefaultPositionZBits = 0;
    public const int RetailDefaultPlaneMode = 0;

    private RetailWorldPlayerStartResolution(
        int playerNumber,
        int thingType,
        int positionXBits,
        int positionYBits,
        int positionZBits,
        int planeMode,
        IReadOnlyList<RetailWorldPlayerStartRecord> matchingAuthoredStarts)
    {
        PlayerNumber = playerNumber;
        ThingType = thingType;
        PositionXBits = positionXBits;
        PositionYBits = positionYBits;
        PositionZBits = positionZBits;
        PlaneMode = planeMode;
        MatchingAuthoredStarts = Array.AsReadOnly(matchingAuthoredStarts.ToArray());
        AuthoredStart = MatchingAuthoredStarts.Count == 0
            ? null
            : MatchingAuthoredStarts[^1];
    }

    public int PlayerNumber { get; }

    public int ThingType { get; }

    public int PositionXBits { get; }

    public int PositionYBits { get; }

    public int PositionZBits { get; }

    public int PlaneMode { get; }

    /// <summary>
    /// Every serialized start whose player number matched, in the retail list
    /// traversal order. This is resolution evidence, not a transcript of
    /// constructed Battle Engines or player-side assignments.
    /// </summary>
    public IReadOnlyList<RetailWorldPlayerStartRecord> MatchingAuthoredStarts { get; }

    /// <summary>
    /// The final matching serialized start, mirroring retail's retained
    /// player-side selection after the complete list walk.
    /// </summary>
    public RetailWorldPlayerStartRecord? AuthoredStart { get; }

    public bool IsAuthored => AuthoredStart is not null;

    public bool UsesRetailDefault => AuthoredStart is null;

    internal static RetailWorldPlayerStartResolution FromOrderedMatches(
        IReadOnlyList<RetailWorldPlayerStartRecord> matches)
    {
        if (matches.Count == 0)
        {
            throw new ArgumentException(
                "An authored resolution requires at least one matching start.",
                nameof(matches));
        }

        RetailWorldPlayerStartRecord final = matches[^1];
        return new RetailWorldPlayerStartResolution(
            final.PlayerNumber,
            final.ThingType,
            final.PositionXBits,
            final.PositionYBits,
            final.PositionZBits,
            final.PlaneMode,
            matches);
    }

    internal static RetailWorldPlayerStartResolution FromAuthored(
        RetailWorldPlayerStartRecord start) =>
        FromOrderedMatches([start]);

    internal static RetailWorldPlayerStartResolution RetailDefault(
        int playerNumber) =>
        new(
            playerNumber,
            RetailDefaultThingType,
            RetailDefaultPositionXBits,
            RetailDefaultPositionYBits,
            RetailDefaultPositionZBits,
            RetailDefaultPlaneMode,
            matchingAuthoredStarts: []);
}

/// <summary>
/// Immutable deterministic result of admitting one world's exact authored
/// player-start projection. This is serialized pre-init placement evidence for
/// a later world constructor, not an actor registry or a Battle Engine
/// lifecycle owner.
/// </summary>
public sealed class RetailWorldPlayerStartProjection
{
    private static readonly byte[] s_identityMagic =
        Encoding.ASCII.GetBytes("ONSLAUGHT-WORLD-PLAYER-START-PROJECTION");

    private readonly IReadOnlyList<RetailWorldPlayerStartRecord> _starts;

    internal RetailWorldPlayerStartProjection(
        int worldNumber,
        RetailWorldArchiveIdentity archiveIdentity,
        IReadOnlyList<RetailWorldPlayerStartRecord> starts)
    {
        WorldNumber = worldNumber;
        ArchiveIdentity = archiveIdentity;
        _starts = Array.AsReadOnly(starts.ToArray());
        IdentitySha256 = ComputeIdentity();
    }

    public int WorldNumber { get; }

    public RetailWorldArchiveIdentity ArchiveIdentity { get; }

    public IReadOnlyList<RetailWorldPlayerStartRecord> Starts => _starts;

    public string IdentitySha256 { get; }

    public RetailWorldPlayerStartResolution ResolveForPlayer(int playerNumber)
    {
        if (playerNumber is < 1 or > 2)
        {
            throw new ArgumentOutOfRangeException(
                nameof(playerNumber),
                playerNumber,
                "A retail player number must be one or two.");
        }

        var matches = new List<RetailWorldPlayerStartRecord>();
        foreach (RetailWorldPlayerStartRecord start in _starts)
        {
            if (start.PlayerNumber == playerNumber)
            {
                matches.Add(start);
            }
        }

        return matches.Count == 0
            ? RetailWorldPlayerStartResolution.RetailDefault(playerNumber)
            : RetailWorldPlayerStartResolution.FromOrderedMatches(matches);
    }

    private string ComputeIdentity()
    {
        using var stream = new MemoryStream();
        using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true))
        {
            writer.Write(s_identityMagic);
            writer.Write(1);
            writer.Write(WorldNumber);
            writer.Write(ArchiveIdentity.RelativePath);
            writer.Write(ArchiveIdentity.Sha256);
            writer.Write(_starts.Count);
            foreach (RetailWorldPlayerStartRecord start in _starts)
            {
                writer.Write(start.ObjectIdentity);
                writer.Write(start.ThingType);
                writer.Write(start.SerializedByteLength);
                writer.Write(start.SerializedSha256);
                writer.Write(start.PositionXBits);
                writer.Write(start.PositionYBits);
                writer.Write(start.PositionZBits);
                writer.Write(start.OrientationXBits);
                writer.Write(start.OrientationYBits);
                writer.Write(start.OrientationZBits);
                writer.Write(start.PlaneMode);
                writer.Write(start.PlayerNumber);
            }
        }

        return Convert.ToHexString(SHA256.HashData(stream.ToArray())).ToLowerInvariant();
    }
}

/// <summary>
/// World-parameterized fail-closed admission for exact authored player starts.
/// A profile exists only after its archive, ordered records, and raw fields are
/// independently pinned.
/// </summary>
public static class RetailWorldPlayerStartAdmission
{
    public static RetailWorldPlayerStartProjection Admit(
        int worldNumber,
        RetailWorldArchiveIdentity archiveIdentity,
        IEnumerable<RetailWorldPlayerStartRecord> starts)
    {
        ArgumentNullException.ThrowIfNull(archiveIdentity);
        ArgumentNullException.ThrowIfNull(starts);

        (RetailWorldArchiveIdentity ExpectedArchive,
            IReadOnlyList<RetailWorldPlayerStartRecord> ExpectedStarts) profile =
            worldNumber switch
            {
                RetailWorld110LevelActors.WorldNumber =>
                    (RetailWorld110LevelActors.ArchiveIdentity,
                     RetailWorld110LevelActors.AuthoredPlayerStarts),
                _ => throw new ArgumentOutOfRangeException(
                    nameof(worldNumber),
                    $"World {worldNumber} has no admitted authored player-start projection."),
            };

        if (!StringComparer.Ordinal.Equals(
                archiveIdentity.RelativePath,
                profile.ExpectedArchive.RelativePath) ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                archiveIdentity.Sha256,
                profile.ExpectedArchive.Sha256))
        {
            throw new ArgumentException(
                $"World {worldNumber} archive identity is not the admitted retail archive.",
                nameof(archiveIdentity));
        }

        RetailWorldPlayerStartRecord[] supplied = starts.ToArray();
        if (supplied.Length != profile.ExpectedStarts.Count)
        {
            throw new ArgumentException(
                $"World {worldNumber} requires exactly {profile.ExpectedStarts.Count} authored player starts.",
                nameof(starts));
        }

        for (int index = 0; index < supplied.Length; index++)
        {
            RetailWorldPlayerStartRecord actual = supplied[index] ??
                throw new ArgumentException(
                    $"World {worldNumber} authored player start {index} is null.",
                    nameof(starts));
            RetailWorldPlayerStartRecord expected = profile.ExpectedStarts[index];
            ValidateStart(worldNumber, index, actual, expected);
        }

        return new RetailWorldPlayerStartProjection(
            worldNumber,
            profile.ExpectedArchive,
            profile.ExpectedStarts);
    }

    private static void ValidateStart(
        int worldNumber,
        int index,
        RetailWorldPlayerStartRecord actual,
        RetailWorldPlayerStartRecord expected)
    {
        if (!StringComparer.Ordinal.Equals(actual.ObjectIdentity, expected.ObjectIdentity))
        {
            throw Changed(worldNumber, index, "object identity");
        }

        if (actual.ThingType != expected.ThingType ||
            actual.SerializedByteLength != expected.SerializedByteLength ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                actual.SerializedSha256,
                expected.SerializedSha256))
        {
            throw Changed(worldNumber, index, "serialized record identity");
        }

        if (actual.PositionXBits != expected.PositionXBits ||
            actual.PositionYBits != expected.PositionYBits ||
            actual.PositionZBits != expected.PositionZBits)
        {
            throw Changed(worldNumber, index, "serialized position bits");
        }

        if (actual.OrientationXBits != expected.OrientationXBits ||
            actual.OrientationYBits != expected.OrientationYBits ||
            actual.OrientationZBits != expected.OrientationZBits)
        {
            throw Changed(worldNumber, index, "serialized orientation bits");
        }

        if (actual.PlaneMode != expected.PlaneMode ||
            actual.PlayerNumber != expected.PlayerNumber)
        {
            throw Changed(worldNumber, index, "CStart tail");
        }
    }

    private static ArgumentException Changed(
        int worldNumber,
        int index,
        string field) =>
        new(
            $"World {worldNumber} authored player start {index} {field} changed.",
            "starts");
}
