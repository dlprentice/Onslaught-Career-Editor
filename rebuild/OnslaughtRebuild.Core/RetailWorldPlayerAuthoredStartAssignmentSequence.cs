// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// Adapter-supplied identity for the already-constructed Battle Engine owned
/// by one admitted authored player start.
/// </summary>
/// <remarks>
/// Integer identities are stable deterministic tokens, not retail pointers.
/// The adapter remains responsible for proving that the Battle Engine is this
/// authored start's already-constructed <c>GetPlayerObject</c> result and that
/// its engine-side reader cell belongs to that non-null object.
/// </remarks>
public readonly record struct RetailWorldPlayerAuthoredStartEngineBinding(
    string StartObjectIdentity,
    int BattleEngineIdentity,
    int BattleEnginePlayerReaderCellIdentity);

/// <summary>
/// One admitted authored start and its bounded assignment transcript.
/// </summary>
public sealed class RetailWorldPlayerAuthoredStartAssignmentStep
{
    internal RetailWorldPlayerAuthoredStartAssignmentStep(
        RetailWorldPlayerStartRecord authoredStart,
        RetailWorldPlayerAuthoredStartEngineBinding binding,
        RetailPlayerBattleEngineAssignmentResult assignment)
    {
        ArgumentNullException.ThrowIfNull(authoredStart);
        ArgumentNullException.ThrowIfNull(assignment);

        AuthoredStart = authoredStart;
        Binding = binding;
        Assignment = assignment;
    }

    public RetailWorldPlayerStartRecord AuthoredStart { get; }

    public RetailWorldPlayerAuthoredStartEngineBinding Binding { get; }

    public RetailPlayerBattleEngineAssignmentResult Assignment { get; }
}

/// <summary>
/// Deeply immutable ordered result of assigning every admitted authored
/// player-start match.
/// </summary>
public sealed class RetailWorldPlayerAuthoredStartAssignmentSequenceResult
{
    private readonly IReadOnlyList<RetailWorldPlayerAuthoredStartAssignmentStep>
        _assignments;

    internal RetailWorldPlayerAuthoredStartAssignmentSequenceResult(
        IReadOnlyList<RetailWorldPlayerAuthoredStartAssignmentStep> assignments)
    {
        ArgumentNullException.ThrowIfNull(assignments);
        _assignments = Array.AsReadOnly(assignments.ToArray());
    }

    public IReadOnlyList<RetailWorldPlayerAuthoredStartAssignmentStep>
        Assignments => _assignments;
}

/// <summary>
/// Composes the admitted ordered authored-start matches with the bounded
/// valid-object <see cref="RetailPlayerBattleEngineAssignment"/> operation.
/// </summary>
/// <remarks>
/// This owner accepts only adapter-supplied, already-constructed object and
/// reader-cell identities. It does not construct a <c>CStart</c>, Battle
/// Engine, or player; execute policy virtuals; handle the no-start fallback;
/// call <c>CPlayer::Init</c>; or publish a playable world. All deterministic
/// input and graph checks complete before the first graph mutation. That
/// preflight is not rollback parity for concurrent mutation, resource
/// exhaustion, or arbitrary corruption outside <see cref="RetailActiveReaderGraph"/>'s
/// public operations.
/// The adapter must prove that <c>playerIdentity</c> represents the resolution's
/// player number, that the player-side reader cell belongs to that player, and
/// that every binding identifies the corresponding start's already-constructed
/// <c>GetPlayerObject</c> result.
/// </remarks>
public static class RetailWorldPlayerAuthoredStartAssignmentSequence
{
    public static RetailWorldPlayerAuthoredStartAssignmentSequenceResult Assign(
        RetailActiveReaderGraph graph,
        RetailWorldPlayerStartResolution resolution,
        int playerIdentity,
        int playerBattleEngineReaderCellIdentity,
        int playerGodWord,
        IEnumerable<RetailWorldPlayerAuthoredStartEngineBinding> bindings)
    {
        ArgumentNullException.ThrowIfNull(graph);
        ArgumentNullException.ThrowIfNull(resolution);
        ArgumentNullException.ThrowIfNull(bindings);

        RetailWorldPlayerAuthoredStartEngineBinding[] bindingSnapshot =
            bindings.ToArray();
        IReadOnlyList<RetailWorldPlayerStartRecord> matches =
            resolution.MatchingAuthoredStarts;

        if (!resolution.IsAuthored ||
            matches.Count == 0 ||
            resolution.AuthoredStart is null ||
            !ReferenceEquals(resolution.AuthoredStart, matches[^1]))
        {
            throw new ArgumentException(
                "An internally consistent authored player-start resolution is required.",
                nameof(resolution));
        }

        if (bindingSnapshot.Length != matches.Count)
        {
            throw new ArgumentException(
                $"The authored resolution requires exactly {matches.Count} " +
                "ordered Battle Engine bindings.",
                nameof(bindings));
        }

        var engineToReaderCell = new Dictionary<int, int>();
        var readerCellToEngine = new Dictionary<int, int>();

        for (int index = 0; index < bindingSnapshot.Length; index++)
        {
            RetailWorldPlayerAuthoredStartEngineBinding binding =
                bindingSnapshot[index];
            RetailWorldPlayerStartRecord match = matches[index];

            if (!StringComparer.Ordinal.Equals(
                    binding.StartObjectIdentity,
                    match.ObjectIdentity))
            {
                throw new ArgumentException(
                    $"Battle Engine binding {index} does not correspond to " +
                    $"authored start '{match.ObjectIdentity}'.",
                    nameof(bindings));
            }

            if (binding.BattleEnginePlayerReaderCellIdentity ==
                playerBattleEngineReaderCellIdentity)
            {
                throw new ArgumentException(
                    "Player and Battle Engine reader-cell identities must be distinct.",
                    nameof(bindings));
            }

            if (engineToReaderCell.TryGetValue(
                    binding.BattleEngineIdentity,
                    out int priorReaderCell) &&
                priorReaderCell != binding.BattleEnginePlayerReaderCellIdentity)
            {
                throw new ArgumentException(
                    $"Battle Engine {binding.BattleEngineIdentity} is bound to " +
                    "more than one player-reader cell.",
                    nameof(bindings));
            }

            if (readerCellToEngine.TryGetValue(
                    binding.BattleEnginePlayerReaderCellIdentity,
                    out int priorEngine) &&
                priorEngine != binding.BattleEngineIdentity)
            {
                throw new ArgumentException(
                    $"Battle Engine player-reader cell " +
                    $"{binding.BattleEnginePlayerReaderCellIdentity} is bound " +
                    "to more than one Battle Engine.",
                    nameof(bindings));
            }

            engineToReaderCell[binding.BattleEngineIdentity] =
                binding.BattleEnginePlayerReaderCellIdentity;
            readerCellToEngine[binding.BattleEnginePlayerReaderCellIdentity] =
                binding.BattleEngineIdentity;
        }

        ValidateReaderCell(
            graph,
            playerBattleEngineReaderCellIdentity,
            nameof(playerBattleEngineReaderCellIdentity));
        var validatedReaderCells = new HashSet<int>
        {
            playerBattleEngineReaderCellIdentity,
        };
        foreach (RetailWorldPlayerAuthoredStartEngineBinding binding in
                 bindingSnapshot)
        {
            int readerCellIdentity = binding.BattleEnginePlayerReaderCellIdentity;
            if (validatedReaderCells.Add(readerCellIdentity))
            {
                ValidateReaderCell(graph, readerCellIdentity, nameof(bindings));
            }
        }

        var assignments =
            new List<RetailWorldPlayerAuthoredStartAssignmentStep>(matches.Count);
        for (int index = 0; index < matches.Count; index++)
        {
            RetailWorldPlayerAuthoredStartEngineBinding binding =
                bindingSnapshot[index];
            var request = new RetailPlayerBattleEngineAssignmentRequest(
                playerIdentity,
                playerBattleEngineReaderCellIdentity,
                binding.BattleEngineIdentity,
                binding.BattleEnginePlayerReaderCellIdentity,
                playerGodWord);
            RetailPlayerBattleEngineAssignmentResult assignment =
                RetailPlayerBattleEngineAssignment.Assign(graph, request);
            assignments.Add(new(
                matches[index],
                binding,
                assignment));
        }

        return new(assignments);
    }

    private static void ValidateReaderCell(
        RetailActiveReaderGraph graph,
        int readerCellIdentity,
        string missingIdentityParameterName)
    {
        if (!graph.ContainsReaderCell(readerCellIdentity))
        {
            throw new ArgumentException(
                $"Required reader cell {readerCellIdentity} does not exist.",
                missingIdentityParameterName);
        }

        int? target = graph.TargetOf(readerCellIdentity);
        if (target is null)
        {
            return;
        }

        int membershipCount = graph.ReadersNewestFirst(target.Value)
            .Count(identity => identity == readerCellIdentity);
        if (membershipCount != 1)
        {
            throw new ArgumentException(
                $"Reader cell {readerCellIdentity} has an inconsistent reverse " +
                $"membership for target {target.Value}.",
                nameof(graph));
        }
    }
}
