using Microsoft.UI.Text;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Documents;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Media.Imaging;
using OnslaughtCareerEditor.AppCore;
using System;
using System.Collections.Generic;
using System.IO;

namespace OnslaughtCareerEditor.WinUI.Helpers;

/// <summary>
/// The result of rendering a lore document: the visual root to host, and the
/// heading anchors the reader scrolls to when a "#fragment" link is activated.
/// </summary>
internal sealed record LoreRenderedDocument(
    FrameworkElement Root,
    IReadOnlyDictionary<string, FrameworkElement> Anchors);

/// <summary>
/// Turns a <see cref="LoreDocumentModel"/> into native WinUI content. Prose is
/// rendered with <see cref="RichTextBlock"/> so it stays selectable and reaches
/// screen readers as text; tables become real grids and code blocks become
/// bordered monospace panels. Colors come from the shell's theme resources so
/// the reader follows light and dark chrome.
/// </summary>
internal static class LoreDocumentRenderer
{
    /// <summary>
    /// Builds the visual tree for <paramref name="document"/>. Link activation is
    /// routed to <paramref name="linkActivated"/> with the raw markdown target;
    /// the page decides whether that means scroll, load, or hand off to the shell.
    /// <paramref name="baseDirectory"/> scopes local image resolution and may be
    /// null for documents that do not come from a directory on disk.
    /// </summary>
    public static LoreRenderedDocument Render(
        LoreDocumentModel document,
        string? baseDirectory,
        Action<string> linkActivated)
    {
        ArgumentNullException.ThrowIfNull(document);
        ArgumentNullException.ThrowIfNull(linkActivated);

        return Render(document, baseDirectory, linkActivated, textScale: 1.0);
    }

    /// <summary>
    /// Renders at a reader-chosen text scale (1.0 is the default size; each step of
    /// the page's A-/A+ control moves it by 10%). Anchors and link handling are
    /// unchanged by the scale.
    /// </summary>
    public static LoreRenderedDocument Render(
        LoreDocumentModel document,
        string? baseDirectory,
        Action<string> linkActivated,
        double textScale)
    {
        ArgumentNullException.ThrowIfNull(document);
        ArgumentNullException.ThrowIfNull(linkActivated);
        if (!double.IsFinite(textScale) || textScale <= 0)
        {
            textScale = 1.0;
        }

        return new Renderer(baseDirectory, linkActivated, textScale).Build(document);
    }

    private sealed class Renderer
    {
        private static readonly FontFamily CodeFont = new("Consolas");

        private readonly string? _baseDirectory;
        private readonly Action<string> _linkActivated;
        private readonly double _textScale;
        private readonly Dictionary<string, FrameworkElement> _anchors = new(StringComparer.OrdinalIgnoreCase);

        public Renderer(string? baseDirectory, Action<string> linkActivated, double textScale)
        {
            _baseDirectory = string.IsNullOrWhiteSpace(baseDirectory) ? null : baseDirectory;
            _linkActivated = linkActivated;
            _textScale = Math.Clamp(textScale, 0.7, 1.8);
        }

        public LoreRenderedDocument Build(LoreDocumentModel document)
        {
            StackPanel root = new()
            {
                Spacing = 12,
                HorizontalAlignment = HorizontalAlignment.Stretch
            };

            AppendBlocks(root, document.Blocks);
            return new LoreRenderedDocument(root, _anchors);
        }

        private void AppendBlocks(Panel host, IReadOnlyList<LoreBlock> blocks)
        {
            foreach (LoreBlock block in blocks)
            {
                UIElement? element = BuildBlock(block);
                if (element != null)
                {
                    host.Children.Add(element);
                }
            }
        }

        private UIElement? BuildBlock(LoreBlock block)
        {
            return block switch
            {
                LoreHeadingBlock heading => BuildHeading(heading),
                LoreParagraphBlock paragraph => BuildParagraph(paragraph),
                LoreListBlock list => BuildList(list),
                LoreTableBlock table => BuildTable(table),
                LoreCodeBlock code => BuildCode(code),
                LoreQuoteBlock quote => BuildQuote(quote),
                LoreThematicBreakBlock => BuildThematicBreak(),
                LoreImageBlock image => BuildImage(image),
                _ => null
            };
        }

        private UIElement BuildHeading(LoreHeadingBlock heading)
        {
            RichTextBlock text = new()
            {
                IsTextSelectionEnabled = true,
                TextWrapping = TextWrapping.Wrap,
                FontSize = Scale(HeadingFontSize(heading.Level)),
                FontWeight = FontWeights.SemiBold,
                Margin = new Thickness(0, heading.Level <= 2 ? 10 : 6, 0, 0)
            };

            Paragraph paragraph = new();
            foreach (Inline inline in BuildInlines(heading.Inlines))
            {
                paragraph.Inlines.Add(inline);
            }

            text.Blocks.Add(paragraph);
            AutomationProperties.SetHeadingLevel(text, ToHeadingLevel(heading.Level));

            if (!string.IsNullOrWhiteSpace(heading.Id))
            {
                _anchors[heading.Id] = text;
            }

            return text;
        }

        private UIElement BuildParagraph(LoreParagraphBlock block)
        {
            return BuildRichText(block.Inlines);
        }

        private RichTextBlock BuildRichText(IReadOnlyList<LoreInline> inlines)
        {
            RichTextBlock text = new()
            {
                IsTextSelectionEnabled = true,
                TextWrapping = TextWrapping.Wrap
            };

            Paragraph paragraph = new()
            {
                LineHeight = Scale(22)
            };

            foreach (Inline inline in BuildInlines(inlines))
            {
                paragraph.Inlines.Add(inline);
            }

            text.Blocks.Add(paragraph);
            return text;
        }

        private UIElement BuildList(LoreListBlock list)
        {
            Grid grid = new()
            {
                RowSpacing = 4,
                Margin = new Thickness(4, 0, 0, 0)
            };
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });

            for (int index = 0; index < list.Items.Count; index++)
            {
                grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

                TextBlock marker = new()
                {
                    Text = list.IsOrdered ? $"{list.StartNumber + index}." : "•",
                    Margin = new Thickness(0, 0, 10, 0),
                    VerticalAlignment = VerticalAlignment.Top,
                    Foreground = MutedTextBrush
                };
                Grid.SetRow(marker, index);
                Grid.SetColumn(marker, 0);
                grid.Children.Add(marker);

                StackPanel content = new()
                {
                    Spacing = 6,
                    HorizontalAlignment = HorizontalAlignment.Stretch
                };
                AppendBlocks(content, list.Items[index].Blocks);
                Grid.SetRow(content, index);
                Grid.SetColumn(content, 1);
                grid.Children.Add(content);
            }

            return grid;
        }

        private UIElement BuildTable(LoreTableBlock table)
        {
            int columnCount = table.Headers.Count;
            foreach (IReadOnlyList<LoreTableCell> row in table.Rows)
            {
                columnCount = Math.Max(columnCount, row.Count);
            }

            if (columnCount == 0)
            {
                return new Border { Height = 0 };
            }

            List<IReadOnlyList<LoreTableCell>> rows = new();
            bool hasHeader = table.Headers.Count > 0;
            if (hasHeader)
            {
                rows.Add(table.Headers);
            }

            rows.AddRange(table.Rows);

            Grid grid = new();
            for (int column = 0; column < columnCount; column++)
            {
                grid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            }

            for (int rowIndex = 0; rowIndex < rows.Count; rowIndex++)
            {
                grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
                bool isHeaderRow = hasHeader && rowIndex == 0;
                bool isLastRow = rowIndex == rows.Count - 1;

                for (int column = 0; column < columnCount; column++)
                {
                    IReadOnlyList<LoreTableCell> row = rows[rowIndex];
                    IReadOnlyList<LoreInline> inlines = column < row.Count
                        ? row[column].Inlines
                        : Array.Empty<LoreInline>();

                    RichTextBlock cellText = BuildRichText(inlines);
                    if (isHeaderRow)
                    {
                        cellText.FontWeight = FontWeights.SemiBold;
                    }

                    Border cell = new()
                    {
                        BorderBrush = BorderBrush,
                        BorderThickness = new Thickness(
                            0,
                            0,
                            column == columnCount - 1 ? 0 : 1,
                            isLastRow ? 0 : 1),
                        Padding = new Thickness(12, 9, 12, 9),
                        Child = cellText
                    };

                    if (isHeaderRow)
                    {
                        cell.Background = MutedSurfaceBrush;
                    }

                    Grid.SetRow(cell, rowIndex);
                    Grid.SetColumn(cell, column);
                    grid.Children.Add(cell);
                }
            }

            return new Border
            {
                BorderBrush = BorderBrush,
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(10),
                Margin = new Thickness(0, 4, 0, 4),
                Child = grid
            };
        }

        private UIElement BuildCode(LoreCodeBlock code)
        {
            TextBlock text = new()
            {
                Text = code.Text,
                FontFamily = CodeFont,
                FontSize = 13,
                IsTextSelectionEnabled = true,
                TextWrapping = TextWrapping.NoWrap
            };

            if (!string.IsNullOrWhiteSpace(code.Language))
            {
                AutomationProperties.SetName(text, $"{code.Language} code block");
            }

            ScrollViewer scroll = new()
            {
                HorizontalScrollBarVisibility = ScrollBarVisibility.Auto,
                HorizontalScrollMode = ScrollMode.Auto,
                VerticalScrollBarVisibility = ScrollBarVisibility.Disabled,
                VerticalScrollMode = ScrollMode.Disabled,
                Content = text
            };

            return new Border
            {
                Background = MutedSurfaceBrush,
                BorderBrush = BorderBrush,
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(10),
                Padding = new Thickness(14, 12, 14, 12),
                Margin = new Thickness(0, 4, 0, 4),
                Child = scroll
            };
        }

        private UIElement BuildQuote(LoreQuoteBlock quote)
        {
            StackPanel content = new()
            {
                Spacing = 8,
                HorizontalAlignment = HorizontalAlignment.Stretch
            };
            AppendBlocks(content, quote.Blocks);

            return new Border
            {
                BorderBrush = AccentBrush,
                BorderThickness = new Thickness(4, 0, 0, 0),
                Padding = new Thickness(14, 6, 0, 6),
                Margin = new Thickness(0, 4, 0, 4),
                Child = content
            };
        }

        private UIElement BuildThematicBreak()
        {
            return new Border
            {
                Height = 1,
                Background = BorderBrush,
                Margin = new Thickness(0, 12, 0, 12),
                HorizontalAlignment = HorizontalAlignment.Stretch
            };
        }

        private UIElement BuildImage(LoreImageBlock image)
        {
            string? localPath = ResolveLocalImagePath(image.Uri);
            if (localPath != null)
            {
                Image element = new()
                {
                    Source = new BitmapImage(new Uri(localPath)),
                    Stretch = Stretch.Uniform,
                    HorizontalAlignment = HorizontalAlignment.Left,
                    Margin = new Thickness(0, 4, 0, 4)
                };
                AutomationProperties.SetName(
                    element,
                    string.IsNullOrWhiteSpace(image.Alt) ? "Lore illustration" : image.Alt);
                return element;
            }

            return new TextBlock
            {
                Text = string.IsNullOrWhiteSpace(image.Alt) ? "[image]" : $"[image: {image.Alt}]",
                FontStyle = Windows.UI.Text.FontStyle.Italic,
                Foreground = MutedTextBrush,
                TextWrapping = TextWrapping.Wrap,
                IsTextSelectionEnabled = true
            };
        }

        private List<Inline> BuildInlines(IReadOnlyList<LoreInline> inlines)
        {
            List<Inline> result = new();
            foreach (LoreInline inline in inlines)
            {
                AppendInline(result, inline);
            }

            return result;
        }

        private void AppendInline(IList<Inline> target, LoreInline inline)
        {
            switch (inline)
            {
                case LoreTextInline text:
                    target.Add(new Run { Text = text.Text });
                    break;

                case LoreBoldInline bold:
                {
                    Bold element = new();
                    foreach (Inline child in BuildInlines(bold.Inlines))
                    {
                        element.Inlines.Add(child);
                    }

                    target.Add(element);
                    break;
                }

                case LoreItalicInline italic:
                {
                    Italic element = new();
                    foreach (Inline child in BuildInlines(italic.Inlines))
                    {
                        element.Inlines.Add(child);
                    }

                    target.Add(element);
                    break;
                }

                case LoreCodeInline code:
                    target.Add(new Run
                    {
                        Text = code.Text,
                        FontFamily = CodeFont
                    });
                    break;

                case LoreLineBreakInline:
                    target.Add(new LineBreak());
                    break;

                case LoreLinkInline link:
                    target.Add(BuildHyperlink(link));
                    break;
            }
        }

        private Inline BuildHyperlink(LoreLinkInline link)
        {
            Hyperlink hyperlink = new()
            {
                UnderlineStyle = UnderlineStyle.Single
            };

            foreach (Inline child in BuildInlines(link.Inlines))
            {
                hyperlink.Inlines.Add(child);
            }

            string linkText = link.Text;
            if (link.Kind is LoreLinkKind.Source or LoreLinkKind.External)
            {
                string badge = link.Kind == LoreLinkKind.Source ? "Source" : "External";
                hyperlink.Inlines.Add(new Run
                {
                    Text = $" [{badge}]",
                    FontSize = 11,
                    Foreground = MutedTextBrush
                });

                string description = link.Kind == LoreLinkKind.Source
                    ? "source link; opens GitHub in your browser"
                    : "external link; opens in your browser";
                AutomationProperties.SetName(hyperlink, $"{linkText} ({description})");
                ToolTipService.SetToolTip(
                    hyperlink,
                    link.Kind == LoreLinkKind.Source
                        ? "Opens GitHub source in your browser"
                        : "Opens external site in your browser");
            }
            else if (!string.IsNullOrWhiteSpace(linkText))
            {
                AutomationProperties.SetName(hyperlink, linkText);
            }

            string target = link.Target;
            hyperlink.Click += (_, _) => _linkActivated(target);
            return hyperlink;
        }

        private string? ResolveLocalImagePath(string uri)
        {
            if (string.IsNullOrWhiteSpace(uri))
            {
                return null;
            }

            try
            {
                if (Uri.TryCreate(uri, UriKind.Absolute, out Uri? absolute))
                {
                    return absolute.IsFile && File.Exists(absolute.LocalPath)
                        ? absolute.LocalPath
                        : null;
                }

                if (_baseDirectory == null)
                {
                    return null;
                }

                string root = Path.GetFullPath(_baseDirectory)
                    .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                string candidate = Path.GetFullPath(Path.Combine(
                    root,
                    Uri.UnescapeDataString(uri).Replace('/', Path.DirectorySeparatorChar)));

                bool insideRoot = candidate.StartsWith(
                    root + Path.DirectorySeparatorChar,
                    StringComparison.OrdinalIgnoreCase);
                return insideRoot && File.Exists(candidate) ? candidate : null;
            }
            catch
            {
                return null;
            }
        }

        private static double HeadingFontSize(int level)
        {
            return level switch
            {
                1 => 27,
                2 => 23,
                3 => 20,
                4 => 18,
                5 => 16,
                _ => 15
            };
        }

        /// <summary>Scales reader font sizes by the chosen text scale.</summary>
        private double Scale(double size) => Math.Round(size * _textScale, 1);

        private static AutomationHeadingLevel ToHeadingLevel(int level)
        {
            return level switch
            {
                1 => AutomationHeadingLevel.Level1,
                2 => AutomationHeadingLevel.Level2,
                3 => AutomationHeadingLevel.Level3,
                4 => AutomationHeadingLevel.Level4,
                5 => AutomationHeadingLevel.Level5,
                _ => AutomationHeadingLevel.Level6
            };
        }

        private static Brush BorderBrush => ThemeBrush("ShellBorderBrush", 0xE1, 0xE6, 0xEF);

        private static Brush MutedSurfaceBrush => ThemeBrush("ShellMutedSurfaceBrush", 0xF5, 0xF7, 0xFA);

        private static Brush MutedTextBrush => ThemeBrush("ShellMutedTextBrush", 0x5C, 0x66, 0x7A);

        private static Brush AccentBrush => ThemeBrush("ShellAccentBrush", 0x12, 0x48, 0xD3);

        private static Brush ThemeBrush(string key, byte red, byte green, byte blue)
        {
            if (Application.Current?.Resources is ResourceDictionary resources &&
                resources.ContainsKey(key) &&
                resources[key] is Brush brush)
            {
                return brush;
            }

            return new SolidColorBrush(Microsoft.UI.ColorHelper.FromArgb(0xFF, red, green, blue));
        }
    }
}
