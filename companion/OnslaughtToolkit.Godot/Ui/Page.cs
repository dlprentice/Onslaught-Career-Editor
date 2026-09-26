// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// One sidebar destination. Pages are plain objects that own a control tree; the shell shows one at
/// a time and calls <see cref="Refresh"/> when it appears or when shared state changes.
/// </summary>
internal abstract class Page(string key, string title)
{
    internal string Key { get; } = key;
    internal string Title { get; } = title;
    internal abstract Control Root { get; }

    /// <summary>The line under the page title; pages describe their current subject here.</summary>
    internal virtual string Subtitle => "";

    internal virtual void Refresh()
    {
    }
}
