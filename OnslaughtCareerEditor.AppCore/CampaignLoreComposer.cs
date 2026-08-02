using System;
using System.Collections.Generic;
using System.Text;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Fills in the campaign list on a lore page from the player's own installed game.
    ///
    /// The mission names are the game's text, not this project's. There are 2,571 strings in
    /// <c>data/language/english.dat</c> and none of them may be baked into the shipped Lore pack -
    /// that would be redistributing the game's content in a package anyone can download, which is
    /// a different thing from reading a file the player already owns. So the document that ships
    /// carries a marker and nothing else, and the real names are read off the player's disk at the
    /// moment the page is opened.
    ///
    /// The consequence is deliberate and has to be handled rather than hidden: on a machine with
    /// no game configured, there is no list. The page says so plainly and says what to do about
    /// it, because a lore page that silently loses its middle looks broken.
    /// </summary>
    public static class CampaignLoreComposer
    {
        /// <summary>
        /// The marker a lore document uses to ask for the campaign list. An HTML comment, so the
        /// document is still valid Markdown and renders as nothing if this never runs.
        /// </summary>
        public const string MissionListMarker = "<!-- LIVE:CAMPAIGN-MISSIONS -->";

        /// <summary>True when a document is asking for live campaign data.</summary>
        public static bool WantsMissionList(string? markdown) =>
            markdown is not null && markdown.Contains(MissionListMarker, StringComparison.Ordinal);

        /// <summary>
        /// The document with its marker replaced. Returns the input unchanged when there is no
        /// marker, so this is safe to call on every document the reader opens.
        /// </summary>
        public static string Compose(string? markdown, IReadOnlyList<GameLevelName>? levels)
        {
            if (markdown is null)
                return string.Empty;

            if (!WantsMissionList(markdown))
                return markdown;

            return markdown.Replace(MissionListMarker, BuildMissionSection(levels), StringComparison.Ordinal);
        }

        /// <summary>
        /// The replacement block: a table when the game is there, and an explanation when it is
        /// not. Never an empty string - a page that loses its middle silently reads as a bug.
        /// </summary>
        public static string BuildMissionSection(IReadOnlyList<GameLevelName>? levels)
        {
            if (levels is null || levels.Count == 0)
            {
                return
                    "> **The mission list is missing because this app cannot see your game.**\n" +
                    "> These names are the game's own text, so they are read from your installed\n" +
                    "> copy rather than shipped with this app. Open Settings and choose your\n" +
                    "> Battle Engine Aquila folder, then come back to this page.\n";
            }

            var builder = new StringBuilder();
            builder.Append("*Read from your own installed copy of the game, in its own words.*\n\n");
            builder.Append("| Mission | Name |\n");
            builder.Append("|---|---|\n");

            foreach (GameLevelName level in levels)
            {
                // A pipe in a title would end the cell early and shear the table. Nothing in the
                // retail English file contains one, which is exactly why it is worth handling -
                // the other languages have not been read, and a broken table is a silent failure.
                string title = level.Title.Replace("|", "\\|", StringComparison.Ordinal);
                string code = level.Code.Replace("|", "\\|", StringComparison.Ordinal);

                builder.Append("| ").Append(code).Append(" | ").Append(title);
                if (level.IsEvolvedVariant)
                {
                    builder.Append(" *(the harder version of the same map)*");
                }

                builder.Append(" |\n");
            }

            builder.Append('\n');
            builder.Append("There are ").Append(levels.Count).Append(" of them in your copy.\n");
            return builder.ToString();
        }
    }
}
