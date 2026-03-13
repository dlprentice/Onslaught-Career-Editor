using Markdig;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;

namespace Onslaught___Career_Editor
{
    public sealed class LoreBrowserService
    {
        private static readonly Regex BookEntryRegex = new(@"^(?<indent>\s*)-\s+(?<content>.+?)\s*$", RegexOptions.Compiled);
        private static readonly Regex MarkdownLinkRegex = new(@"\[(?<title>[^\]]+)\]\((?<path>[^)]+)\)", RegexOptions.Compiled);
        private readonly MarkdownPipeline _pipeline;

        public LoreBrowserService()
        {
            _pipeline = new MarkdownPipelineBuilder()
                .UseAdvancedExtensions()
                .Build();
        }

        public LoreIndex LoadIndex(string? startDirectory = null)
        {
            string projectRoot = FindProjectRoot(startDirectory)
                ?? throw new DirectoryNotFoundException("Could not locate repo root containing lore-book.");

            string loreBookDirectory = Path.Combine(projectRoot, "lore-book");
            if (!Directory.Exists(loreBookDirectory))
            {
                throw new DirectoryNotFoundException($"Lore book directory not found: {loreBookDirectory}");
            }

            bool usingLoreBook = TryLoadBookIndex(loreBookDirectory, out List<LoreTreeItem> rootItems, out Dictionary<string, LoreDocument> documentMap);
            if (!usingLoreBook)
            {
                BuildFallbackIndex(loreBookDirectory, out rootItems, out documentMap);
            }

            IReadOnlyList<LoreDocument> documents = documentMap.Values
                .OrderBy(static doc => doc.Order ?? int.MaxValue)
                .ThenBy(static doc => doc.Title, StringComparer.OrdinalIgnoreCase)
                .ToList();

            LoreDocument? homeDocument = documents.FirstOrDefault();
            return new LoreIndex(projectRoot, documents, CloneTree(rootItems), usingLoreBook, homeDocument);
        }

        public IReadOnlyList<LoreTreeItem> FilterTree(IReadOnlyList<LoreTreeItem> rootItems, string? query)
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                return CloneTree(rootItems);
            }

            string normalizedQuery = query.Trim();
            List<LoreTreeItem> filtered = new();
            foreach (LoreTreeItem item in rootItems)
            {
                LoreTreeItem? match = FilterNode(item, normalizedQuery);
                if (match != null)
                {
                    filtered.Add(match);
                }
            }

            return filtered;
        }

        public RenderedLoreDocument RenderDocument(string filePath, string? anchor = null)
        {
            string extension = Path.GetExtension(filePath);
            if (extension.Equals(".html", StringComparison.OrdinalIgnoreCase) ||
                extension.Equals(".htm", StringComparison.OrdinalIgnoreCase))
            {
                return new RenderedLoreDocument(
                    Path.GetFileNameWithoutExtension(filePath),
                    filePath,
                    new Uri(filePath).AbsoluteUri,
                    false,
                    anchor);
            }

            string markdown = File.ReadAllText(filePath);
            string title = ResolveMarkdownTitle(markdown, filePath);
            string contentHtml = Markdown.ToHtml(markdown, _pipeline);
            string wrappedHtml = WrapHtmlDocument(title, contentHtml, filePath);

            string renderPath = GetRenderPathForDocument(filePath);
            Directory.CreateDirectory(Path.GetDirectoryName(renderPath)!);
            File.WriteAllText(renderPath, wrappedHtml, Encoding.UTF8);

            string renderUri = AppendAnchor(new Uri(renderPath).AbsoluteUri, anchor);
            return new RenderedLoreDocument(title, filePath, renderUri, true, anchor);
        }

        public string? ResolveInternalTarget(string currentFilePath, string? target)
        {
            if (string.IsNullOrWhiteSpace(target))
            {
                return null;
            }

            string trimmed = target.Trim();
            if (trimmed.StartsWith("#", StringComparison.Ordinal))
            {
                return currentFilePath;
            }

            if (trimmed.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                trimmed.StartsWith("https://", StringComparison.OrdinalIgnoreCase) ||
                trimmed.StartsWith("mailto:", StringComparison.OrdinalIgnoreCase) ||
                trimmed.StartsWith("data:", StringComparison.OrdinalIgnoreCase) ||
                trimmed.StartsWith("javascript:", StringComparison.OrdinalIgnoreCase))
            {
                return null;
            }

            string? resolved = null;
            if (Uri.TryCreate(trimmed, UriKind.Absolute, out Uri? absoluteUri))
            {
                if (absoluteUri.IsFile)
                {
                    resolved = absoluteUri.LocalPath;
                }
                else
                {
                    return null;
                }
            }
            else
            {
                string candidate = Path.IsPathRooted(trimmed)
                    ? trimmed
                    : Path.GetFullPath(Path.Combine(Path.GetDirectoryName(currentFilePath)!, trimmed));
                resolved = candidate;
            }

            return ResolveMarkdownOrHtmlPath(resolved);
        }

        public static string? ExtractAnchor(string? uriOrPath)
        {
            if (string.IsNullOrWhiteSpace(uriOrPath))
            {
                return null;
            }

            int hashIndex = uriOrPath.IndexOf('#');
            if (hashIndex < 0 || hashIndex == uriOrPath.Length - 1)
            {
                return null;
            }

            return Uri.UnescapeDataString(uriOrPath[(hashIndex + 1)..]);
        }

        public static string? FindProjectRoot(string? startDirectory = null)
        {
            string initialPath = string.IsNullOrWhiteSpace(startDirectory)
                ? AppContext.BaseDirectory
                : startDirectory;

            DirectoryInfo? directory = new(initialPath);
            if (!directory.Exists)
            {
                directory = directory.Parent;
            }

            while (directory != null)
            {
                string loreBook = Path.Combine(directory.FullName, "lore-book");
                if (Directory.Exists(loreBook))
                {
                    return directory.FullName;
                }

                directory = directory.Parent;
            }

            return null;
        }

        private static bool TryLoadBookIndex(string loreBookDirectory, out List<LoreTreeItem> rootItems, out Dictionary<string, LoreDocument> documentMap)
        {
            rootItems = new List<LoreTreeItem>();
            documentMap = new Dictionary<string, LoreDocument>(StringComparer.OrdinalIgnoreCase);

            string bookPath = Path.Combine(loreBookDirectory, "BOOK.md");
            if (!File.Exists(bookPath))
            {
                return false;
            }

            Stack<(int Depth, LoreTreeItem Item)> stack = new();
            int order = 0;
            foreach (string rawLine in File.ReadAllLines(bookPath))
            {
                Match match = BookEntryRegex.Match(rawLine);
                if (!match.Success)
                {
                    continue;
                }

                int depth = match.Groups["indent"].Value.Replace("\t", "    ", StringComparison.Ordinal).Length / 2;
                string content = match.Groups["content"].Value.Trim();

                LoreTreeItem item = CreateBookTreeItem(content, loreBookDirectory, order++, documentMap);

                while (stack.Count > 0 && stack.Peek().Depth >= depth)
                {
                    stack.Pop();
                }

                if (stack.Count == 0)
                {
                    rootItems.Add(item);
                }
                else
                {
                    stack.Peek().Item.Children.Add(item);
                }

                stack.Push((depth, item));
            }

            return rootItems.Count > 0;
        }

        private static LoreTreeItem CreateBookTreeItem(string content, string loreBookDirectory, int order, IDictionary<string, LoreDocument> documentMap)
        {
            Match linkMatch = MarkdownLinkRegex.Match(content);
            if (linkMatch.Success)
            {
                string title = linkMatch.Groups["title"].Value.Trim();
                string relativePath = Uri.UnescapeDataString(linkMatch.Groups["path"].Value.Trim());
                string filePath = Path.GetFullPath(Path.Combine(loreBookDirectory, relativePath.Replace('/', Path.DirectorySeparatorChar)));
                bool isIndex = IsIndexFile(filePath);

                if (!documentMap.TryGetValue(filePath, out LoreDocument? document))
                {
                    document = new LoreDocument
                    {
                        Title = title,
                        FilePath = filePath,
                        RelativePath = relativePath.Replace('\\', '/'),
                        IsIndex = isIndex,
                        Order = order
                    };
                    documentMap[filePath] = document;
                }
                else if (document.Order is null || order < document.Order)
                {
                    document.Order = order;
                }

                return new LoreTreeItem
                {
                    Title = title,
                    FilePath = filePath,
                    RelativePath = document.RelativePath,
                    IsIndex = isIndex,
                    Order = order
                };
            }

            return new LoreTreeItem
            {
                Title = StripMarkdownFormatting(content),
                Order = order
            };
        }

        private static void BuildFallbackIndex(string loreBookDirectory, out List<LoreTreeItem> rootItems, out Dictionary<string, LoreDocument> documentMap)
        {
            rootItems = new List<LoreTreeItem>();
            documentMap = new Dictionary<string, LoreDocument>(StringComparer.OrdinalIgnoreCase);

            LoreTreeItem root = new()
            {
                Title = "Lore Book",
                Order = 0
            };
            rootItems.Add(root);

            int order = 0;
            foreach (string file in Directory.GetFiles(loreBookDirectory, "*.md", SearchOption.AllDirectories))
            {
                string relativePath = Path.GetRelativePath(loreBookDirectory, file).Replace('\\', '/');
                LoreDocument document = new()
                {
                    Title = Path.GetFileNameWithoutExtension(file).Replace('-', ' '),
                    FilePath = file,
                    RelativePath = relativePath,
                    IsIndex = IsIndexFile(file),
                    Order = order++
                };
                documentMap[file] = document;

                root.Children.Add(new LoreTreeItem
                {
                    Title = document.Title,
                    FilePath = file,
                    RelativePath = relativePath,
                    IsIndex = document.IsIndex,
                    Order = document.Order
                });
            }
        }

        private LoreTreeItem? FilterNode(LoreTreeItem item, string query)
        {
            List<LoreTreeItem> filteredChildren = new();
            foreach (LoreTreeItem child in item.Children)
            {
                LoreTreeItem? match = FilterNode(child, query);
                if (match != null)
                {
                    filteredChildren.Add(match);
                }
            }

            if (filteredChildren.Count > 0 || MatchesQuery(item, query))
            {
                return item with
                {
                    Children = filteredChildren
                };
            }

            return null;
        }

        private static bool MatchesQuery(LoreTreeItem item, string query)
        {
            if (item.Title.Contains(query, StringComparison.OrdinalIgnoreCase) ||
                (!string.IsNullOrWhiteSpace(item.RelativePath) &&
                 item.RelativePath.Contains(query, StringComparison.OrdinalIgnoreCase)))
            {
                return true;
            }

            if (string.IsNullOrWhiteSpace(item.FilePath) || !File.Exists(item.FilePath))
            {
                return false;
            }

            try
            {
                return File.ReadAllText(item.FilePath).Contains(query, StringComparison.OrdinalIgnoreCase);
            }
            catch
            {
                return false;
            }
        }

        private static IReadOnlyList<LoreTreeItem> CloneTree(IReadOnlyList<LoreTreeItem> rootItems)
        {
            return rootItems.Select(static item => item.DeepCopy()).ToList();
        }

        private static bool IsIndexFile(string path)
        {
            string fileName = Path.GetFileNameWithoutExtension(path);
            return fileName.Equals("_index", StringComparison.OrdinalIgnoreCase) ||
                   fileName.Equals("readme", StringComparison.OrdinalIgnoreCase) ||
                   fileName.Equals("book", StringComparison.OrdinalIgnoreCase);
        }

        private static string? ResolveMarkdownOrHtmlPath(string? candidate)
        {
            if (string.IsNullOrWhiteSpace(candidate))
            {
                return null;
            }

            string trimmed = candidate.Split('#')[0];
            if (File.Exists(trimmed))
            {
                return Path.GetFullPath(trimmed);
            }

            if (Directory.Exists(trimmed))
            {
                string[] directoryCandidates =
                {
                    Path.Combine(trimmed, "_index.md"),
                    Path.Combine(trimmed, "README.md"),
                    Path.Combine(trimmed, "index.md")
                };

                return directoryCandidates.FirstOrDefault(File.Exists);
            }

            string baseWithoutExtension = Path.ChangeExtension(trimmed, null) ?? trimmed;
            string[] candidates =
            {
                trimmed + ".md",
                trimmed + ".html",
                trimmed + ".htm",
                baseWithoutExtension + ".md",
                baseWithoutExtension + ".html",
                baseWithoutExtension + ".htm"
            };

            return candidates.FirstOrDefault(File.Exists);
        }

        private static string ResolveMarkdownTitle(string markdown, string filePath)
        {
            foreach (string line in markdown.Split('\n'))
            {
                string trimmed = line.Trim();
                if (trimmed.StartsWith("#", StringComparison.Ordinal))
                {
                    return trimmed.TrimStart('#', ' ');
                }
            }

            return Path.GetFileNameWithoutExtension(filePath);
        }

        private static string WrapHtmlDocument(string title, string contentHtml, string filePath)
        {
            string baseUri = new Uri(Path.GetDirectoryName(filePath)! + Path.DirectorySeparatorChar).AbsoluteUri;
            string escapedTitle = System.Net.WebUtility.HtmlEncode(title);

            return $$"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <base href="{{baseUri}}" />
  <title>{{escapedTitle}}</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4f6fa;
      --surface: #ffffff;
      --border: #dfe5ef;
      --text: #1d2433;
      --muted: #556176;
      --accent: #1248d3;
      --code-bg: #eef3fb;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 32px;
      background: linear-gradient(180deg, #f7f9fc 0%, #eef2f8 100%);
      color: var(--text);
      font-family: "Segoe UI", "Segoe UI Variable Text", sans-serif;
      line-height: 1.65;
    }
    main {
      max-width: 960px;
      margin: 0 auto;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 32px 36px 40px;
      box-shadow: 0 24px 64px rgba(17, 24, 39, 0.08);
    }
    h1, h2, h3, h4, h5, h6 { color: var(--text); line-height: 1.2; }
    h1 { font-size: 2rem; margin-top: 0; }
    h2 { margin-top: 2rem; padding-top: 0.5rem; border-top: 1px solid var(--border); }
    p, li { font-size: 0.98rem; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    code, pre {
      font-family: "Cascadia Code", Consolas, monospace;
      font-size: 0.92rem;
    }
    code {
      background: var(--code-bg);
      padding: 0.12rem 0.35rem;
      border-radius: 6px;
    }
    pre {
      background: #0f172a;
      color: #e5eefb;
      padding: 16px;
      border-radius: 14px;
      overflow-x: auto;
    }
    pre code {
      background: transparent;
      padding: 0;
      color: inherit;
    }
    blockquote {
      margin: 1rem 0;
      padding: 0.75rem 1rem;
      border-left: 4px solid #90a9e8;
      background: #f6f8fd;
      color: var(--muted);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 1.2rem 0;
      overflow: hidden;
      border-radius: 14px;
      border: 1px solid var(--border);
    }
    th, td {
      padding: 0.75rem 0.9rem;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: top;
    }
    th {
      background: #f7f9fd;
      font-weight: 600;
    }
    img {
      max-width: 100%;
      border-radius: 14px;
    }
    hr {
      border: 0;
      border-top: 1px solid var(--border);
      margin: 2rem 0;
    }
  </style>
</head>
<body>
  <main>
    {{contentHtml}}
  </main>
</body>
</html>
""";
        }

        private static string GetRenderPathForDocument(string filePath)
        {
            string fileName = Path.GetFileNameWithoutExtension(filePath);
            string safeName = Regex.Replace(fileName, @"[^a-zA-Z0-9_-]", "_");
            string hash = ComputeShortHash(filePath);
            return Path.Combine(Path.GetTempPath(), "OnslaughtCareerEditor", "LoreRender", $"{safeName}-{hash}.html");
        }

        private static string ComputeShortHash(string value)
        {
            using SHA1 sha1 = SHA1.Create();
            byte[] hash = sha1.ComputeHash(Encoding.UTF8.GetBytes(value));
            return string.Concat(hash.Take(6).Select(static value => value.ToString("x2")));
        }

        private static string StripMarkdownFormatting(string value)
        {
            string text = MarkdownLinkRegex.Replace(value, "${title}");
            return text.Replace("**", string.Empty, StringComparison.Ordinal)
                .Replace("__", string.Empty, StringComparison.Ordinal)
                .Replace("`", string.Empty, StringComparison.Ordinal)
                .Trim();
        }

        private static string AppendAnchor(string uri, string? anchor)
        {
            return string.IsNullOrWhiteSpace(anchor)
                ? uri
                : $"{uri}#{Uri.EscapeDataString(anchor)}";
        }
    }

    public sealed record LoreIndex(
        string ProjectRoot,
        IReadOnlyList<LoreDocument> Documents,
        IReadOnlyList<LoreTreeItem> RootItems,
        bool UsingLoreBook,
        LoreDocument? HomeDocument);

    public sealed class LoreDocument
    {
        public string Title { get; set; } = string.Empty;
        public string FilePath { get; set; } = string.Empty;
        public string RelativePath { get; set; } = string.Empty;
        public bool IsIndex { get; set; }
        public int? Order { get; set; }
    }

    public sealed record LoreTreeItem
    {
        public string Title { get; init; } = string.Empty;
        public string? FilePath { get; init; }
        public string? RelativePath { get; init; }
        public bool IsIndex { get; init; }
        public int? Order { get; init; }
        public List<LoreTreeItem> Children { get; init; } = new();

        public LoreTreeItem DeepCopy()
        {
            return this with
            {
                Children = Children.Select(static child => child.DeepCopy()).ToList()
            };
        }

        public override string ToString()
        {
            return Title;
        }
    }

    public sealed record RenderedLoreDocument(
        string Title,
        string SourcePath,
        string DisplayUri,
        bool IsMarkdown,
        string? Anchor);
}
