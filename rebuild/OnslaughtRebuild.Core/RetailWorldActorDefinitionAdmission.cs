// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text;

namespace OnslaughtRebuild.Core;

/// <summary>
/// Exact user-supplied retail archive identity consumed by a bounded authored
/// definition projection. The relative path names the archive; the digest binds
/// the bytes without giving Core filesystem ownership.
/// </summary>
public sealed record RetailWorldArchiveIdentity(string RelativePath, string Sha256);

/// <summary>
/// The authored world shape distinguishes a definition-bearing actor row from
/// a type-19 spawner's unit-definition binding. This projection preserves that
/// distinction without inventing unmeasured runtime actor or spawner semantics.
/// </summary>
public enum RetailWorldAuthoredDefinitionKind
{
    Actor = 1,
    Spawner = 2,
}

/// <summary>
/// One definition-bearing authored WRES object. <c>ObjectIdentity</c>
/// follows the existing <c>wres:bswd:NNNN</c> / <c>wres:rlwd:NNNN</c> identity
/// law used by the Level 100 actor-definition manifest.
/// </summary>
public sealed record RetailWorldAuthoredDefinitionIdentity(
    string ObjectIdentity,
    int ThingType,
    string DefinitionName,
    RetailWorldAuthoredDefinitionKind Kind);

/// <summary>
/// Immutable deterministic result of admitting one exact authored definition
/// projection. It is evidence for a future world constructor, not a mission,
/// actor registry, player spawn, or product lifecycle.
/// </summary>
public sealed class RetailWorldActorDefinitionProjection
{
    private static readonly byte[] s_identityMagic =
        Encoding.ASCII.GetBytes("ONSLAUGHT-WORLD-ACTOR-DEFINITION-PROJECTION");

    private readonly IReadOnlyList<RetailWorldAuthoredDefinitionIdentity> _definitions;

    internal RetailWorldActorDefinitionProjection(
        int worldNumber,
        RetailWorldArchiveIdentity archiveIdentity,
        IReadOnlyList<RetailWorldAuthoredDefinitionIdentity> definitions)
    {
        WorldNumber = worldNumber;
        ArchiveIdentity = archiveIdentity;
        _definitions = Array.AsReadOnly(definitions.ToArray());
        ActorDefinitionCount = _definitions.Count(item =>
            item.Kind == RetailWorldAuthoredDefinitionKind.Actor);
        SpawnerDefinitionCount = _definitions.Count(item =>
            item.Kind == RetailWorldAuthoredDefinitionKind.Spawner);
        IdentitySha256 = ComputeIdentity();
    }

    public int WorldNumber { get; }

    public RetailWorldArchiveIdentity ArchiveIdentity { get; }

    public IReadOnlyList<RetailWorldAuthoredDefinitionIdentity> Definitions => _definitions;

    public int ActorDefinitionCount { get; }

    public int SpawnerDefinitionCount { get; }

    public string IdentitySha256 { get; }

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
            writer.Write(_definitions.Count);
            foreach (RetailWorldAuthoredDefinitionIdentity definition in _definitions)
            {
                writer.Write(definition.ObjectIdentity);
                writer.Write(definition.ThingType);
                writer.Write(definition.DefinitionName);
                writer.Write((int)definition.Kind);
            }
        }

        return Convert.ToHexString(SHA256.HashData(stream.ToArray())).ToLowerInvariant();
    }
}

/// <summary>
/// World-parameterized fail-closed admission for exact authored actor-definition
/// projections. Profiles are added only when a released world has an exact
/// archive identity and a complete definition-bearing object projection.
/// </summary>
public static class RetailWorldActorDefinitionAdmission
{
    public static RetailWorldActorDefinitionProjection Admit(
        int worldNumber,
        RetailWorldArchiveIdentity archiveIdentity,
        IEnumerable<RetailWorldAuthoredDefinitionIdentity> definitions)
    {
        ArgumentNullException.ThrowIfNull(archiveIdentity);
        ArgumentNullException.ThrowIfNull(definitions);

        (RetailWorldArchiveIdentity ExpectedArchive,
            IReadOnlyList<RetailWorldAuthoredDefinitionIdentity> ExpectedDefinitions) profile =
            worldNumber switch
            {
                RetailWorld110LevelActors.WorldNumber =>
                    (RetailWorld110LevelActors.ArchiveIdentity,
                     RetailWorld110LevelActors.AuthoredDefinitions),
                _ => throw new ArgumentOutOfRangeException(
                    nameof(worldNumber),
                    $"World {worldNumber} has no admitted authored actor-definition projection."),
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

        RetailWorldAuthoredDefinitionIdentity[] supplied = definitions.ToArray();
        if (supplied.Length != profile.ExpectedDefinitions.Count)
        {
            throw new ArgumentException(
                $"World {worldNumber} requires exactly {profile.ExpectedDefinitions.Count} authored definitions.",
                nameof(definitions));
        }

        for (int index = 0; index < supplied.Length; index++)
        {
            RetailWorldAuthoredDefinitionIdentity actual = supplied[index] ??
                throw new ArgumentException(
                    $"World {worldNumber} authored definition {index} is null.",
                    nameof(definitions));
            RetailWorldAuthoredDefinitionIdentity expected =
                profile.ExpectedDefinitions[index];
            if (!StringComparer.Ordinal.Equals(
                    actual.ObjectIdentity,
                    expected.ObjectIdentity))
            {
                throw new ArgumentException(
                    $"World {worldNumber} object identity at authored order {index} changed.",
                    nameof(definitions));
            }
            if (!StringComparer.Ordinal.Equals(
                    actual.DefinitionName,
                    expected.DefinitionName))
            {
                throw new ArgumentException(
                    $"World {worldNumber} definition identity at authored order {index} changed.",
                    nameof(definitions));
            }
            if (actual.ThingType != expected.ThingType || actual.Kind != expected.Kind)
            {
                throw new ArgumentException(
                    $"World {worldNumber} authored definition shape at order {index} changed.",
                    nameof(definitions));
            }
        }

        return new RetailWorldActorDefinitionProjection(
            worldNumber,
            profile.ExpectedArchive,
            profile.ExpectedDefinitions);
    }
}
