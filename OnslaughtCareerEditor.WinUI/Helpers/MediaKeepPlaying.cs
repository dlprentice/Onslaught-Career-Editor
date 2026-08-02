using System;
using System.Collections.Generic;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// Which track comes after the one that just finished.
    ///
    /// Trivial enough to have written inline, and deliberately not: the Media page holds three and
    /// a half hours of a soundtrack that was never released, and it used to stop dead after every
    /// track. The edge cases are where that gets annoying again - the last track, a track that has
    /// been filtered out from under the player by a search, an empty list - so they are here where
    /// a test can reach them without a running app.
    /// </summary>
    internal static class MediaKeepPlaying
    {
        /// <summary>
        /// The next item after <paramref name="finished"/> in the order shown, or null when there
        /// is nothing sensible to move to.
        ///
        /// Null when the list is empty, when the finished track is the last one, and when the
        /// finished track is no longer in the list at all - which happens if a search narrowed the
        /// tree while it was playing. Guessing a position in that case would start something the
        /// player cannot see.
        /// </summary>
        public static MediaAudioItem? FindNext(
            IReadOnlyList<MediaAudioItem>? order,
            MediaAudioItem? finished)
        {
            if (order is null || order.Count == 0 || finished is null)
                return null;

            for (int index = 0; index < order.Count; index++)
            {
                if (!IsSameTrack(order[index], finished))
                    continue;

                return index + 1 < order.Count ? order[index + 1] : null;
            }

            return null;
        }

        /// <summary>
        /// Identity is the file path. The same track can appear under more than one heading, and
        /// two different tracks can share a display name.
        /// </summary>
        private static bool IsSameTrack(MediaAudioItem left, MediaAudioItem right)
        {
            return string.Equals(left.FilePath, right.FilePath, StringComparison.OrdinalIgnoreCase);
        }
    }
}
