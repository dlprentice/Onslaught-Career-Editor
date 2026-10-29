// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>Text made from file paths for the page to show. No interface types.</summary>
public static class PathText
{
    private const char Ellipsis = '…';

    /// <summary>
    /// The path in at most <paramref name="max"/> characters. A longer one has its middle cut out (…), keeping the folders it starts in and,
    /// longer, the folder and the name it ends with, so it still points at the same place to the eye; a path that fits is returned as it is.
    /// What the player copies is the full path, never this.
    /// </summary>
    public static string Elide(string path, int max)
    {
        if (max < 5) throw new ArgumentOutOfRangeException(nameof(max), "a path needs five characters to be cut");
        if (path.Length <= max) return path;
        int tail = (max - 1) * 2 / 3, head = max - 1 - tail;
        // Neither half starts or ends inside a surrogate pair.
        if (char.IsHighSurrogate(path[head - 1])) head--;
        if (char.IsLowSurrogate(path[^tail])) tail--;
        return path[..head] + Ellipsis + path[^tail..];
    }
}
