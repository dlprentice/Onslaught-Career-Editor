using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.Cli
{
    /// <summary>
    /// Quiet, read-only Media parity: the catalog, mission names, and voice-line transcripts the
    /// GUI Media page shows, composed entirely from public AppCore services -
    /// <see cref="MediaCatalogService"/> for the snapshot, AppConfig resolution exactly as
    /// <c>saves list</c> resolves its directory - so no decoder, catalog, or join logic is forked
    /// into the Cli project. Nothing here writes, launches, or attaches.
    ///
    /// Disclosure rule: output names media, never where it lives on disk. JSON carries each item's
    /// game-relative file label and nothing more; text mode carries no path at all. No audio or
    /// video bytes are ever emitted.
    /// </summary>
    public static class MediaVerbs
    {
        private const string CommandName = "media.list";

        public static int List(CliContext ctx, string? filter, string? gameDirOption)
        {
            // An omitted filter arrives as empty rather than null here; both mean "list both
            // sections". Only a non-empty word that names neither section is a bad invocation.
            string? section;
            if (string.IsNullOrWhiteSpace(filter))
            {
                section = null;
            }
            else
            {
                section = filter.Trim().ToLowerInvariant() switch
                {
                    "audio" => "audio",
                    "video" => "video",
                    _ => null,
                };

                if (section is null)
                {
                    return ctx.Usage(
                        CommandName,
                        $"Unknown media filter '{filter}'.",
                        "Use 'audio', 'video', or omit the filter to list both.");
                }
            }

            // Explicit --game-dir wins; otherwise resolve exactly like saves list does.
            string? effectiveDir = !string.IsNullOrWhiteSpace(gameDirOption)
                ? gameDirOption
                : AppConfig.Load().GetGameDir() ?? AppConfig.DetectGameDirectory();

            if (effectiveDir is null)
            {
                return ctx.Usage(
                    CommandName,
                    "Game directory not configured and could not be auto-detected.",
                    "Use 'config set-game-dir <path>' to specify the game installation folder.",
                    "Or pass --game-dir <path> to this command for a single invocation.");
            }

            try
            {
                // A directory that is not an installation is a verdict about the data, not a bad
                // invocation - the same split as analyzing a file that is not a save.
                if (!MediaCatalogService.LooksLikeGameDirectory(effectiveDir))
                {
                    return ctx.Verdict(
                        CommandName,
                        "That directory is not a Battle Engine Aquila installation (BEA.exe and a data folder are required).");
                }

                MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(effectiveDir);

                return ctx.Json
                    ? ListJson(ctx, snapshot, section)
                    : ListText(ctx, snapshot, section);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException
                                        or ArgumentException or InvalidOperationException)
            {
                // Nothing about a catalog read is worth crashing a script over; a degraded load is
                // an answer ("the data could not be read"), not an unhandled condition.
                return ctx.Verdict(CommandName, $"The media catalog could not be read: {ex.Message}");
            }
        }

        private static int ListJson(CliContext ctx, MediaCatalogSnapshot snapshot, string? section)
        {
            // Each requested section travels with its own count, so a filtered caller still gets a
            // total without having to length-count the array. Unrequested sections appear nowhere.
            var data = new Dictionary<string, object?>();

            if (section != "video")
            {
                data["audioCount"] = snapshot.AudioItems.Count;
                // Anonymous shapes like lore.search emits: a member the catalog does not carry -
                // e.g. a transcript - is absent rather than present-and-null.
                data["audio"] = snapshot.AudioItems.Select(item => new
                {
                    name = item.Name,
                    groupName = item.GroupName,
                    groupSortOrder = item.GroupSortOrder,
                    durationLabel = item.DurationLabel,
                    file = RelativeLabel(item.FilePath, snapshot.GameDirectory),
                    transcript = item.Transcript,
                }).ToArray();
            }

            if (section != "audio")
            {
                data["videoCount"] = snapshot.VideoItems.Count;
                data["video"] = snapshot.VideoItems.Select(item => new
                {
                    name = item.Name,
                    sectionName = item.SectionName,
                    file = RelativeLabel(item.FilePath, snapshot.GameDirectory),
                }).ToArray();
            }

            return ctx.Ok(CommandName, data);
        }

        private static int ListText(CliContext ctx, MediaCatalogSnapshot snapshot, string? section)
        {
            const string title = "Onslaught Career Editor - Media Catalog";
            ctx.Line(title);
            ctx.Line(new string('=', title.Length));
            ctx.Line();

            if (section != "video")
            {
                ctx.Line($"Audio ({snapshot.AudioItems.Count})");

                string? currentGroup = null;
                foreach (MediaAudioItem item in snapshot.AudioItems)
                {
                    if (!string.Equals(currentGroup, item.GroupName, StringComparison.Ordinal))
                    {
                        currentGroup = item.GroupName;
                        ctx.Line($"  {item.GroupName}:");
                    }

                    string duration = item.DurationLabel.Length > 0 ? $"  [{item.DurationLabel}]" : string.Empty;
                    ctx.Line($"    {item.Name}{duration}");
                    if (!string.IsNullOrWhiteSpace(item.Transcript))
                        ctx.Line($"      \"{item.Transcript}\"");
                }

                ctx.Line();
            }

            if (section != "audio")
            {
                ctx.Line($"Video ({snapshot.VideoItems.Count})");

                string? currentSection = null;
                foreach (MediaVideoItem item in snapshot.VideoItems)
                {
                    if (!string.Equals(currentSection, item.SectionName, StringComparison.Ordinal))
                    {
                        currentSection = item.SectionName;
                        ctx.Line($"  {item.SectionName}:");
                    }

                    ctx.Line($"    {item.Name}");
                }
            }

            return CliExit.Success;
        }

        /// <summary>
        /// The one path-shaped thing output may carry: the file's location under the game root,
        /// forward-slashed, exactly enough for a caller to ask the game for it by name. Anything
        /// that does not sit under the resolved root is blanked rather than allowed to leak an
        /// absolute path.
        /// </summary>
        private static string RelativeLabel(string filePath, string gameRoot)
        {
            string root = Path.GetFullPath(gameRoot)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string full;
            try
            {
                full = Path.GetFullPath(filePath);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException
                                        or ArgumentException or System.Security.SecurityException)
            {
                return string.Empty;
            }

            if (full.StartsWith(root, StringComparison.OrdinalIgnoreCase) &&
                full.Length > root.Length &&
                (full[root.Length] == Path.DirectorySeparatorChar || full[root.Length] == Path.AltDirectorySeparatorChar))
            {
                return full[(root.Length + 1)..].Replace('\\', '/');
            }

            return string.Empty;
        }
    }
}
