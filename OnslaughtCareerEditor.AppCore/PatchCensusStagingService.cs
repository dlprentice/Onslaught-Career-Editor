using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>Why a census row cannot be staged onto the chosen safe copy.</summary>
    public enum PatchCensusStageRefusal
    {
        None,
        NoRows,
        DuplicateVa,
        BadOffset,
        BadBytes,
        Overlap,
        NoSafeCopy,
        WrongFileName,
        UnsafePath,
        ForbiddenInstallShape,
        OutsideWorkspace,
        UnreadableCopy,
        SizeMismatchAgainstBackup,
    }

    /// <summary>
    /// One accepted census staging candidate after validation: the parsed region plus
    /// what the UI shows about it.
    /// </summary>
    public sealed record PatchCensusStagingCandidate(
        PatchCensusRow Row,
        int FileOffset,
        byte[] Original,
        byte[] Patched);

    /// <summary>The outcome of validating one batch of selected census rows.</summary>
    public sealed record PatchCensusStagingPlan(
        bool Success,
        string Message,
        IReadOnlyList<PatchCensusStagingCandidate> Candidates)
    {
        public static readonly PatchCensusStagingPlan Empty =
            new(false, string.Empty, Array.Empty<PatchCensusStagingCandidate>());
    }

    /// <summary>The result of a completed stage or undo write.</summary>
    public sealed record PatchCensusStagingResult(
        bool Success,
        string Message,
        IReadOnlyList<string> AppliedSummaries)
    {
        public static readonly PatchCensusStagingResult Empty =
            new(false, string.Empty, Array.Empty<string>());
    }

    /// <summary>
    /// What the Lab can do right now with the current safe copy.
    /// </summary>
    public sealed record PatchCensusStagingReadiness(
        bool CanStage,
        string Status,
        bool CanUndo)
    {
        public static PatchCensusStagingReadiness MissingCopy(string status) =>
            new(false, status, false);
    }

    /// <summary>
    /// One undoable census experiment already written into this safe copy's
    /// executable, as recorded in the sidecar manifest.
    /// </summary>
    public sealed record PatchCensusStagedEntry(
        string Va,
        string Offset,
        string Effect,
        string Confidence,
        string Risk,
        string EvidencePath,
        string OriginalBytes,
        string PatchedBytes);

    /// <summary>The parsed sidecar manifest for one safe copy.</summary>
    public sealed record PatchCensusStagingManifest(
        bool Present,
        IReadOnlyList<PatchCensusStagedEntry> Entries)
    {
        public static readonly PatchCensusStagingManifest None =
            new(false, Array.Empty<PatchCensusStagedEntry>());
    }

    /// <summary>
    /// Stages Patch-Lab census candidate bytes into an app-owned BEA.exe-only safe
    /// copy so an RE claim can be exercised in a copied runtime - the cheapest
    /// falsifier column of the census made runnable.
    ///
    /// The rules this service exists to enforce:
    ///
    /// 1. Safe copies only. Installed-game shapes are refused structurally (protected
    ///    roots, known Steam library layouts); the
    ///    <see cref="BinaryPatchEngine.AuthorizeInstalledGameWrite"/> precondition
    ///    model is deliberately NOT used here because experiments never target an
    ///    installed game. The workspace-root check keeps every write inside the
    ///    app-owned patch folder even if the path text changes underneath us.
    /// 2. Bytes are checked exactly. Every staged row must find its original bytes at
    ///    its file offset in the copy before anything is written; a mismatch aborts
    ///    the whole batch before the first write.
    /// 3. A verified full-file backup snapshot always exists beside the copy before
    ///    the first census write, created from the pre-experiment bytes when absent.
    /// 4. Undo is per-batch: each stage writes a JSON sidecar manifest of the rows it
    ///    applied; undo rewrites those exact offsets back to their original bytes and
    ///    removes the batch from the manifest. The product Restore button still does
    ///    whole-file restore from that same verified snapshot.
    /// 5. Census rows stay experiments. Nothing here claims a visible benefit; the
    ///    Lab says in player terms what each row changes and how to check it.
    /// </summary>
    public static class PatchCensusStagingService
    {
        private const string ManifestSuffix = ".census-staged.json";

        public const string TargetFileName = "BEA.exe";

        public const string NoSafeCopyMessage =
            "Create or choose a BEA.exe-only safe copy above first. Census experiments are written into a safe copy only.";

        public const string ForbiddenInstallShapeMessage =
            "That path looks like an installed game, not an app-owned safe copy. Census experiments are never written to an installed game.";

        public static string BuildManifestPath(string exePath) => exePath + ManifestSuffix;

        /// <summary>
        /// Validates one batch of selected census rows against the chosen safe copy
        /// without writing anything. Every refusal names the reason and says nothing
        /// was changed.
        /// </summary>
        public static PatchCensusStagingPlan BuildStagingPlan(
            IReadOnlyList<PatchCensusRow> rows,
            string? exePath,
            string? allowedRoot)
        {
            if (rows is null || rows.Count == 0)
                return PatchCensusStagingPlan.Empty;

            if (string.IsNullOrWhiteSpace(exePath) || !File.Exists(exePath))
                return new PatchCensusStagingPlan(false, NoSafeCopyMessage, Array.Empty<PatchCensusStagingCandidate>());

            string fullExePath;
            try
            {
                fullExePath = Path.GetFullPath(exePath);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or NotSupportedException)
            {
                return new PatchCensusStagingPlan(false, NoSafeCopyMessage, Array.Empty<PatchCensusStagingCandidate>());
            }

            if (!string.Equals(Path.GetFileName(fullExePath), TargetFileName, StringComparison.OrdinalIgnoreCase))
            {
                return new PatchCensusStagingPlan(
                    false,
                    $"The census experiment writes to {TargetFileName}. Choose the safe copy's executable itself.",
                    Array.Empty<PatchCensusStagingCandidate>());
            }

            // Structural refusals first: an installed game is never a census target,
            // whatever folder it was reached from.
            if (BinaryPatchEngine.CensusStagingTargetHasForbiddenInstallShape(fullExePath))
            {
                return new PatchCensusStagingPlan(
                    false,
                    ForbiddenInstallShapeMessage,
                    Array.Empty<PatchCensusStagingCandidate>());
            }

            if (!TryNormalizeRoot(allowedRoot, out string normalizedRoot))
            {
                return new PatchCensusStagingPlan(false, NoSafeCopyMessage, Array.Empty<PatchCensusStagingCandidate>());
            }

            if (!BinaryPatchEngine.IsPathUnderRootPublic(fullExePath, normalizedRoot))
            {
                return new PatchCensusStagingPlan(
                    false,
                    "That safe copy is not inside the app-owned patch workspace, so nothing was changed.",
                    Array.Empty<PatchCensusStagingCandidate>());
            }

            string backupPath = BinaryPatchEngine.BuildBackupPath(fullExePath);
            string backupHashPath = BinaryPatchEngine.BuildBackupHashPath(fullExePath);
            var filesystemSafety = BinaryPatchEngine.ValidateCensusStagingFilesystemSafety(
                fullExePath, backupPath, backupHashPath, normalizedRoot);
            if (!filesystemSafety.success)
            {
                return new PatchCensusStagingPlan(false, filesystemSafety.message, Array.Empty<PatchCensusStagingCandidate>());
            }

            byte[] data;
            try
            {
                data = File.ReadAllBytes(fullExePath);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                return new PatchCensusStagingPlan(
                    false,
                    "The safe copy's BEA.exe could not be read right now. Nothing was changed.",
                    Array.Empty<PatchCensusStagingCandidate>());
            }

            var candidates = new List<(PatchCensusRow Row, int Offset, byte[] Original, byte[] Patched)>();
            var seenOffsets = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (PatchCensusRow row in rows)
            {
                if (!TryParseOffset(row.Offset, out int offset))
                {
                    return PlanRefusal(row, $"could not be read as a file offset ('{row.Offset}')");
                }

                if (!TryParseBytes(row.OriginalBytes, out byte[] original) ||
                    !TryParseBytes(row.PatchedBytes, out byte[] patched) ||
                    original.Length == 0 ||
                    original.Length != patched.Length)
                {
                    return PlanRefusal(row, "has original/patched bytes this tool could not parse");
                }

                // Same-VA duplicates are normal in the census (alternative values for
                // one site). Identical mutations collapse; different patched values
                // for one offset are competing alternatives and cannot both land -
                // refusing beats silently staging whichever came first.
                string offsetKey = offset.ToString(CultureInfo.InvariantCulture);
                if (seenOffsets.Contains(offsetKey))
                {
                    (PatchCensusRow Row, int Offset, byte[] Original, byte[] Patched) first =
                        candidates.First(candidate => candidate.Offset == offset);
                    if (!first.Original.SequenceEqual(original))
                    {
                        return new PatchCensusStagingPlan(
                            false,
                            $"Two selected census rows disagree about the original bytes at 0x{offset:X} ('{Truncate(row.Effect)}' and '{Truncate(first.Row.Effect)}'). Select one of them, not both. Nothing was changed.",
                            Array.Empty<PatchCensusStagingCandidate>());
                    }

                    if (!first.Patched.SequenceEqual(patched))
                    {
                        return new PatchCensusStagingPlan(
                            false,
                            $"Two selected census rows change overlapping bytes ('{Truncate(row.Effect)}' and '{Truncate(first.Row.Effect)}'). Stage them one at a time. Nothing was changed.",
                            Array.Empty<PatchCensusStagingCandidate>());
                    }

                    continue;
                }

                seenOffsets.Add(offsetKey);

                if (offset > data.Length - original.Length)
                {
                    return new PatchCensusStagingPlan(
                        false,
                        $"Census row '{Truncate(row.Effect)}' sits outside this safe copy ({data.Length:N0} bytes). Nothing was changed.",
                        Array.Empty<PatchCensusStagingCandidate>());
                }

                if (!data.AsSpan(offset, original.Length).SequenceEqual(original))
                {
                    return new PatchCensusStagingPlan(
                        false,
                        $"Census row '{Truncate(row.Effect)}' expects different bytes than the ones at 0x{offset:X} in this copy. " +
                        "Undo any earlier experiment first, or start from a fresh copy. Nothing was changed.",
                        Array.Empty<PatchCensusStagingCandidate>());
                }

                candidates.Add((row, offset, original, patched));
            }

            // Cross-row overlap: two selected rows writing overlapping ranges that
            // are not the identical mutation cannot both land honestly.
            for (int i = 0; i < candidates.Count; i++)
            {
                for (int j = i + 1; j < candidates.Count; j++)
                {
                    var left = candidates[i];
                    var right = candidates[j];
                    bool overlaps = left.Offset < right.Offset + right.Patched.Length &&
                        right.Offset < left.Offset + left.Patched.Length;
                    if (!overlaps)
                    {
                        continue;
                    }

                    bool identical = left.Offset == right.Offset &&
                        left.Original.SequenceEqual(right.Original) &&
                        left.Patched.SequenceEqual(right.Patched);
                    if (!identical)
                    {
                        return new PatchCensusStagingPlan(
                            false,
                            $"Two selected census rows change overlapping bytes ('{Truncate(left.Row.Effect)}' and '{Truncate(right.Row.Effect)}'). Stage them one at a time. Nothing was changed.",
                            Array.Empty<PatchCensusStagingCandidate>());
                    }
                }
            }

            return new PatchCensusStagingPlan(
                true,
                $"{candidates.Count} census experiment{(candidates.Count == 1 ? "" : "s")} checked against this safe copy.",
                candidates
                    .Select(candidate => new PatchCensusStagingCandidate(
                        candidate.Row,
                        candidate.Offset,
                        candidate.Original,
                        candidate.Patched))
                    .ToArray());
        }

        /// <summary>
        /// Stages a validated plan into the safe copy: verifies the backup snapshot
        /// (or creates one from the untouched bytes), applies every region, publishes
        /// atomically, reads the file back, and records the batch in the sidecar
        /// manifest. Any failure leaves the previous on-disk state intact.
        /// </summary>
        public static PatchCensusStagingResult StageBatch(
            PatchCensusStagingPlan plan,
            string? exePath,
            string? allowedRoot)
        {
            if (!plan.Success ||
                plan.Candidates.Count == 0 ||
                string.IsNullOrWhiteSpace(exePath) ||
                !File.Exists(exePath))
            {
                return PatchCensusStagingResult.Empty;
            }

            string fullExePath;
            try
            {
                fullExePath = Path.GetFullPath(exePath);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or NotSupportedException)
            {
                return PatchCensusStagingResult.Empty;
            }

            if (!TryNormalizeRoot(allowedRoot, out string normalizedRoot))
            {
                return PatchCensusStagingResult.Empty;
            }

            // Defense-in-depth: StageBatch re-runs the structural refusals
            // BuildStagingPlan made, because a plan object can arrive stale,
            // hand-built, or aimed at a different path than the one it was
            // validated against. Nothing here trusts the caller's earlier walk.
            if (!string.Equals(Path.GetFileName(fullExePath), TargetFileName, StringComparison.OrdinalIgnoreCase))
            {
                return new PatchCensusStagingResult(
                    false,
                    $"The census experiment writes to {TargetFileName}. Choose the safe copy's executable itself.",
                    Array.Empty<string>());
            }

            if (BinaryPatchEngine.CensusStagingTargetHasForbiddenInstallShape(fullExePath))
            {
                return new PatchCensusStagingResult(false, ForbiddenInstallShapeMessage, Array.Empty<string>());
            }

            if (!BinaryPatchEngine.IsPathUnderRootPublic(fullExePath, normalizedRoot))
            {
                return new PatchCensusStagingResult(
                    false,
                    "That safe copy is not inside the app-owned patch workspace, so nothing was changed.",
                    Array.Empty<string>());
            }

            string backupPath = BinaryPatchEngine.BuildBackupPath(fullExePath);
            string backupHashPath = BinaryPatchEngine.BuildBackupHashPath(fullExePath);
            var filesystemSafety = BinaryPatchEngine.ValidateCensusStagingFilesystemSafety(
                fullExePath, backupPath, backupHashPath, normalizedRoot);
            if (!filesystemSafety.success)
            {
                return new PatchCensusStagingResult(false, filesystemSafety.message, Array.Empty<string>());
            }

            byte[] data;
            try
            {
                data = File.ReadAllBytes(fullExePath);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                return new PatchCensusStagingResult(
                    false,
                    "The safe copy's BEA.exe could not be read right now. Nothing was changed.",
                    Array.Empty<string>());
            }

            // Re-check every row against the freshly-read bytes: the file may have
            // changed between plan and stage.
            foreach (PatchCensusStagingCandidate candidate in plan.Candidates)
            {
                if (candidate.FileOffset > data.Length - candidate.Original.Length ||
                    !data.AsSpan(candidate.FileOffset, candidate.Original.Length).SequenceEqual(candidate.Original))
                {
                    return new PatchCensusStagingResult(
                        false,
                        $"Census row '{Truncate(candidate.Row.Effect)}' no longer matches the bytes in this copy. Nothing was changed.",
                        Array.Empty<string>());
                }
            }

            try
            {
                if (File.Exists(backupPath))
                {
                    byte[] backupBytes = File.ReadAllBytes(backupPath);
                    var integrity = BinaryPatchEngine.ValidateBackupSnapshotIntegrityInternal(backupHashPath, backupBytes);
                    if (!integrity.success)
                    {
                        return new PatchCensusStagingResult(false, integrity.message, Array.Empty<string>());
                    }
                }
                else
                {
                    BinaryPatchEngine.PublishCensusStagingBytesAtomically(
                        backupPath, data, overwrite: false, "pre-experiment backup snapshot");
                    BinaryPatchEngine.WriteBackupHashInternal(backupHashPath, data);
                }
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return new PatchCensusStagingResult(
                    false,
                    "The verified backup snapshot could not be created, so the safe copy was not modified.",
                    Array.Empty<string>());
            }

            foreach (PatchCensusStagingCandidate candidate in plan.Candidates)
            {
                candidate.Patched.CopyTo(data, candidate.FileOffset);
            }

            byte[] readBack;
            try
            {
                readBack = BinaryPatchEngine.PublishCensusStagingBytesAtomically(
                    fullExePath, data, overwrite: true, "census-staged BEA.exe-only copy");
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return new PatchCensusStagingResult(
                    false,
                    "Census staging failed before atomic publication completed. The verified backup remains available.",
                    Array.Empty<string>());
            }

            foreach (PatchCensusStagingCandidate candidate in plan.Candidates)
            {
                if (candidate.FileOffset > readBack.Length - candidate.Patched.Length ||
                    !readBack.AsSpan(candidate.FileOffset, candidate.Patched.Length).SequenceEqual(candidate.Patched))
                {
                    return new PatchCensusStagingResult(
                        false,
                        "Census staging failed its on-disk verification. Use Restore to put the last good executable back.",
                        Array.Empty<string>());
                }
            }

            List<PatchCensusStagedEntry> entries = LoadManifestEntries(fullExePath);
            foreach (PatchCensusStagingCandidate candidate in plan.Candidates)
            {
                entries.RemoveAll(entry => string.Equals(
                    entry.Offset,
                    candidate.Row.Offset.Trim(),
                    StringComparison.OrdinalIgnoreCase));
                entries.Add(new PatchCensusStagedEntry(
                    candidate.Row.Va.Trim(),
                    candidate.Row.Offset.Trim(),
                    candidate.Row.Effect,
                    candidate.Row.Confidence,
                    candidate.Row.Risk,
                    candidate.Row.EvidencePath,
                    candidate.Row.OriginalBytes.Trim(),
                    candidate.Row.PatchedBytes.Trim()));
            }

            try
            {
                WriteManifest(fullExePath, entries);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                // The bytes landed and were verified on disk; the manifest is the
                // honest bookkeeping layer, so a failure there must be surfaced, not
                // swallowed - but it does not roll back the verified write.
                return new PatchCensusStagingResult(
                    true,
                    "Census experiments applied and verified on disk, but the undo manifest could not be updated. Whole-file Restore still works.",
                    SummariesFor(plan.Candidates));
            }

            return new PatchCensusStagingResult(
                true,
                $"{plan.Candidates.Count} census experiment{(plan.Candidates.Count == 1 ? "" : "s")} applied to the safe copy and verified on disk. The installed game is untouched. Undo reverses exactly these bytes; Restore swaps the whole executable from its backup.",
                SummariesFor(plan.Candidates));
        }

        /// <summary>
        /// Reverses the recorded batches in this safe copy: every manifest entry has
        /// its original bytes rewritten at its offset. Entries whose current bytes are
        /// already original are skipped silently; entries whose bytes match neither
        /// original nor patched value fail the undo without writing.
        /// </summary>
        public static PatchCensusStagingResult UndoAll(string? exePath, string? allowedRoot)
        {
            if (string.IsNullOrWhiteSpace(exePath) || !File.Exists(exePath))
                return PatchCensusStagingResult.Empty;

            PatchCensusStagingManifest manifest = ReadManifest(exePath);
            if (!manifest.Present || manifest.Entries.Count == 0)
            {
                return new PatchCensusStagingResult(
                    false,
                    "There is no census experiment manifest for this copy, so there is nothing to undo. Restore still swaps the whole executable from its backup.",
                    Array.Empty<string>());
            }

            string fullExePath;
            try
            {
                fullExePath = Path.GetFullPath(exePath);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or NotSupportedException)
            {
                return PatchCensusStagingResult.Empty;
            }

            if (!TryNormalizeRoot(allowedRoot, out string normalizedRoot))
            {
                return PatchCensusStagingResult.Empty;
            }

            string backupPath = BinaryPatchEngine.BuildBackupPath(fullExePath);
            string backupHashPath = BinaryPatchEngine.BuildBackupHashPath(fullExePath);
            var filesystemSafety = BinaryPatchEngine.ValidateCensusStagingFilesystemSafety(
                fullExePath, backupPath, backupHashPath, normalizedRoot);
            if (!filesystemSafety.success)
            {
                return new PatchCensusStagingResult(false, filesystemSafety.message, Array.Empty<string>());
            }

            byte[] data;
            try
            {
                data = File.ReadAllBytes(fullExePath);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                return new PatchCensusStagingResult(
                    false,
                    "The safe copy's BEA.exe could not be read right now. Nothing was changed.",
                    Array.Empty<string>());
            }

            var plannedWrites = new List<(int Offset, byte[] Original, PatchCensusStagedEntry Entry)>();
            foreach (PatchCensusStagedEntry entry in manifest.Entries)
            {
                if (!TryParseOffset(entry.Offset, out int offset) ||
                    !TryParseBytes(entry.OriginalBytes, out byte[] original))
                {
                    return new PatchCensusStagingResult(
                        false,
                        "The undo manifest holds a row whose bytes could not be parsed. Use whole-file Restore instead.",
                        Array.Empty<string>());
                }

                // Current bytes equal to the original mean this entry is already
                // undone (for example by whole-file Restore) and can be dropped.
                if (offset > data.Length - original.Length)
                {
                    return new PatchCensusStagingResult(
                        false,
                        "The undo manifest points outside this copy. Use whole-file Restore instead.",
                        Array.Empty<string>());
                }

                ReadOnlySpan<byte> current = data.AsSpan(offset, original.Length);
                if (current.SequenceEqual(original))
                {
                    continue;
                }

                // Current bytes must equal the patched value this entry claims to
                // have written; anything else means somebody else touched these bytes
                // and undo refuses to guess.
                if (!TryParseBytes(entry.PatchedBytes, out byte[] patched) ||
                    patched.Length != original.Length ||
                    !current.SequenceEqual(patched))
                {
                    return new PatchCensusStagingResult(
                        false,
                        "These bytes no longer match what the experiment wrote. Use whole-file Restore instead of guessing an undo.",
                        Array.Empty<string>());
                }

                plannedWrites.Add((offset, original, entry));
            }

            if (plannedWrites.Count == 0)
            {
                try
                {
                    WriteManifest(fullExePath, new List<PatchCensusStagedEntry>());
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
                {
                    return new PatchCensusStagingResult(
                        false,
                        "Everything recorded was already undone, but the manifest could not be cleared.",
                        Array.Empty<string>());
                }

                return new PatchCensusStagingResult(
                    true,
                    "Nothing to reverse: every recorded experiment already reads its original bytes.",
                    Array.Empty<string>());
            }

            try
            {
                if (File.Exists(backupPath))
                {
                    byte[] backupBytes = File.ReadAllBytes(backupPath);
                    var integrity = BinaryPatchEngine.ValidateBackupSnapshotIntegrityInternal(backupHashPath, backupBytes);
                    if (!integrity.success)
                    {
                        return new PatchCensusStagingResult(false, integrity.message, Array.Empty<string>());
                    }
                }
                else
                {
                    // A manifest without a backup should not happen; refusing keeps
                    // the guarantee that a backup always precedes any census write.
                    return new PatchCensusStagingResult(
                        false,
                        "The pre-experiment backup snapshot is missing, so undo refuses to proceed. Use whole-file Restore once a backup exists.",
                        Array.Empty<string>());
                }
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return new PatchCensusStagingResult(
                    false,
                    "The backup snapshot could not be checked, so the safe copy was not modified.",
                    Array.Empty<string>());
            }

            foreach ((int Offset, byte[] Original, PatchCensusStagedEntry _) write in plannedWrites)
            {
                write.Original.CopyTo(data, write.Offset);
            }

            byte[] readBack;
            try
            {
                readBack = BinaryPatchEngine.PublishCensusStagingBytesAtomically(
                    fullExePath, data, overwrite: true, "undo-census BEA.exe-only copy");
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return new PatchCensusStagingResult(
                    false,
                    "Undo failed before atomic publication completed. The verified backup remains available.",
                    Array.Empty<string>());
            }

            foreach ((int Offset, byte[] Original, PatchCensusStagedEntry _) write in plannedWrites)
            {
                if (!readBack.AsSpan(write.Offset, write.Original.Length).SequenceEqual(write.Original))
                {
                    return new PatchCensusStagingResult(
                        false,
                        "Undo failed its on-disk verification. Use whole-file Restore instead.",
                        Array.Empty<string>());
                }
            }

            try
            {
                WriteManifest(fullExePath, new List<PatchCensusStagedEntry>());
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return new PatchCensusStagingResult(
                    true,
                    "Census experiments reversed and verified on disk, but the undo manifest could not be cleared. Whole-file Restore still works.",
                    SummariesFor(plannedWrites));
            }

            return new PatchCensusStagingResult(
                true,
                $"{plannedWrites.Count} census experiment{(plannedWrites.Count == 1 ? "" : "s")} reversed in the safe copy and verified on disk. Restore can still swap the whole executable from its backup.",
                SummariesFor(plannedWrites));
        }

        /// <summary>Reads the sidecar manifest for this safe copy, if any.</summary>
        public static PatchCensusStagingManifest ReadManifest(string exePath)
        {
            string manifestPath = BuildManifestPath(exePath);
            if (string.IsNullOrWhiteSpace(exePath) || !File.Exists(manifestPath))
            {
                return PatchCensusStagingManifest.None;
            }

            try
            {
                using var document = System.Text.Json.JsonDocument.Parse(File.ReadAllBytes(manifestPath));
                if (!document.RootElement.TryGetProperty("entries", out System.Text.Json.JsonElement entriesEl) ||
                    entriesEl.ValueKind != System.Text.Json.JsonValueKind.Array)
                {
                    return PatchCensusStagingManifest.None;
                }

                var entries = new List<PatchCensusStagedEntry>();
                foreach (System.Text.Json.JsonElement entryEl in entriesEl.EnumerateArray())
                {
                    if (entryEl.ValueKind != System.Text.Json.JsonValueKind.Object)
                    {
                        continue;
                    }

                    entries.Add(new PatchCensusStagedEntry(
                        GetStringProperty(entryEl, "va"),
                        GetStringProperty(entryEl, "offset"),
                        GetStringProperty(entryEl, "effect"),
                        GetStringProperty(entryEl, "confidence"),
                        GetStringProperty(entryEl, "risk"),
                        GetStringProperty(entryEl, "evidence_path"),
                        GetStringProperty(entryEl, "original_bytes"),
                        GetStringProperty(entryEl, "patched_bytes")));
                }

                return new PatchCensusStagingManifest(true, entries);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or System.Text.Json.JsonException)
            {
                return PatchCensusStagingManifest.None;
            }
        }

        private static void WriteManifest(string exePath, List<PatchCensusStagedEntry> entries)
        {
            string manifestPath = BuildManifestPath(exePath);
            string payload = System.Text.Json.JsonSerializer.Serialize(
                new ManifestPayload(
                    SchemaVersion: "winui-census-staged.v1",
                    Entries: entries
                        .Select(entry => new ManifestEntry(
                            entry.Va,
                            entry.Offset,
                            entry.Effect,
                            entry.Confidence,
                            entry.Risk,
                            entry.EvidencePath,
                            entry.OriginalBytes,
                            entry.PatchedBytes))
                        .ToArray()),
                new System.Text.Json.JsonSerializerOptions
                {
                    PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.SnakeCaseLower,
                });

            BinaryPatchEngine.PublishCensusStagingBytesAtomically(
                manifestPath,
                System.Text.Encoding.UTF8.GetBytes(payload),
                overwrite: true,
                "census undo manifest");
        }

        private sealed record ManifestPayload(string SchemaVersion, ManifestEntry[] Entries);

        private sealed record ManifestEntry(
            string Va,
            string Offset,
            string Effect,
            string Confidence,
            string Risk,
            string EvidencePath,
            string OriginalBytes,
            string PatchedBytes);

        private static List<PatchCensusStagedEntry> LoadManifestEntries(string exePath)
        {
            PatchCensusStagingManifest existing = ReadManifest(exePath);
            return existing.Present ? existing.Entries.ToList() : new List<PatchCensusStagedEntry>();
        }

        private static IReadOnlyList<string> SummariesFor(IReadOnlyList<PatchCensusStagingCandidate> candidates)
        {
            return candidates
                .Select(candidate => $"{candidate.Row.Va}: {candidate.Row.Effect}")
                .ToArray();
        }

        private static IReadOnlyList<string> SummariesFor(
            List<(int Offset, byte[] Original, PatchCensusStagedEntry Entry)> writes)
        {
            return writes
                .Select(write => $"{write.Entry.Va}: {write.Entry.Effect}")
                .ToArray();
        }

        private static PatchCensusStagingPlan PlanRefusal(PatchCensusRow row, string reason)
        {
            return new PatchCensusStagingPlan(
                false,
                $"Census row '{Truncate(row.Effect)}' {reason}. Nothing was changed.",
                Array.Empty<PatchCensusStagingCandidate>());
        }

        private static bool TryNormalizeRoot(string? allowedRoot, out string normalizedRoot)
        {
            normalizedRoot = string.Empty;
            if (string.IsNullOrWhiteSpace(allowedRoot))
            {
                return false;
            }

            try
            {
                normalizedRoot = Path.GetFullPath(allowedRoot)
                    .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                    + Path.DirectorySeparatorChar;
                return true;
            }
            catch (Exception ex) when (ex is ArgumentException or NotSupportedException or PathTooLongException)
            {
                return false;
            }
        }

        internal static bool TryParseOffset(string raw, out int offset)
        {
            offset = 0;
            return TryParseOffsetPublic(raw, out offset);
        }

        /// <summary>Test-visible wrapper around the offset parser.</summary>
        public static bool TryParseOffsetPublic(string raw, out int offset)
        {
            offset = 0;
            string trimmed = (raw ?? string.Empty).Trim();
            if (trimmed.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
            {
                trimmed = trimmed[2..];
            }

            if (trimmed.Length == 0 || trimmed.Length > 8 ||
                !trimmed.All(char.IsAsciiHexDigit))
            {
                return false;
            }

            // HexNumber silently accepts the two's-complement form ("FFFFFFFF" reads
            // as -1), which would slip a negative offset past every bounds check.
            if (!int.TryParse(trimmed, NumberStyles.HexNumber, CultureInfo.InvariantCulture, out offset) ||
                offset < 0)
            {
                offset = 0;
                return false;
            }

            return true;
        }

        private static bool TryParseBytes(string raw, out byte[] bytes)
        {
            bytes = Array.Empty<byte>();
            string hex = (raw ?? string.Empty).Trim();
            if (hex.Length == 0 || hex.Length % 2 != 0 || hex.Any(value => !char.IsAsciiHexDigit(value)))
            {
                return false;
            }

            bytes = new byte[hex.Length / 2];
            for (int i = 0; i < bytes.Length; i++)
            {
                bytes[i] = byte.Parse(hex.AsSpan(i * 2, 2), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
            }

            return true;
        }

        private static string Truncate(string value)
        {
            string trimmed = value?.Trim() ?? string.Empty;
            return trimmed.Length <= 80 ? trimmed : trimmed[..77] + "...";
        }

        private static string GetStringProperty(System.Text.Json.JsonElement element, string propertyName)
        {
            return element.TryGetProperty(propertyName, out System.Text.Json.JsonElement property) &&
                property.ValueKind == System.Text.Json.JsonValueKind.String
                ? property.GetString() ?? string.Empty
                : string.Empty;
        }
    }
}
