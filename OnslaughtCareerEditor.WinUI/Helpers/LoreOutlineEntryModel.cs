using System;
using Microsoft.UI.Xaml;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>One heading in the on-this-page outline.</summary>
    public sealed class LoreOutlineEntryModel
    {
        public LoreOutlineEntryModel(AppCore.LoreOutlineEntry entry)
        {
            Entry = entry;
            Text = string.IsNullOrWhiteSpace(entry.Text) ? "Heading" : entry.Text;
            RowMargin = new Thickness(Math.Max(0, entry.Level - 1) * 12, 0, 0, 0);
            AccessibilityName = $"Jump to heading {Text}";
        }

        public AppCore.LoreOutlineEntry Entry { get; }

        public string Text { get; }

        public Thickness RowMargin { get; }

        public string AccessibilityName { get; }
    }
}
