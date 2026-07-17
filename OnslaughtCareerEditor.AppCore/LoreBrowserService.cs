using Markdig;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Onslaught___Career_Editor
{
    public sealed partial class LoreBrowserService
    {
        private const string LorePackDirectoryName = "lore-pack";
        private const string LorePackIndexFileName = "onslaught-lore.v1.index.json";
        private const string LorePackContentFileName = "onslaught-lore.v1.jsonl";
        private const string LorePackSourcePrefix = "lore-pack://";
        private const string LorePackNavigationScheme = "onslaught-lore";
        private const string MissingLoreBookMessage = "Lore content directory not found.";
        private const string InvalidLorePackDocumentIdMessage = "Lore content pack contains an invalid document identifier.";
        private const string InvalidLorePackDocumentPathMessage = "Lore content pack contains an invalid document path.";
        private const string InvalidLorePackIndexMessage = "Lore content pack index is invalid.";
        private const string InvalidLorePackContentMessage = "Lore content pack content is invalid.";
        private const string LorePackIndexContentMismatchMessage = "Lore content pack index and content do not match.";
        private const string DuplicateLorePackDocumentIdMessage = "Lore content pack contains duplicate document identifiers.";
        private const string DuplicateLorePackDocumentPathMessage = "Lore content pack contains duplicate document paths.";
        private const string LorePackContentHashMismatchMessage = "Lore content pack content hash mismatch.";
        private const string LorePackSchema = "onslaught-lore-pack.v1";

        private static readonly Regex BookEntryRegex = new(@"^(?<indent>\s*)-\s+(?<content>.+?)\s*$", RegexOptions.Compiled);
        private static readonly Regex MarkdownLinkRegex = new(@"\[(?<title>[^\]]+)\]\((?<path>[^)]+)\)", RegexOptions.Compiled);
        private static readonly Regex HtmlAnchorRegex = new(
            @"<a\s+(?<attrs>[^>]*\bhref=(?<quote>[""'])(?<href>[^""']+)\k<quote>[^>]*)>(?<content>.*?)</a>",
            RegexOptions.Compiled | RegexOptions.IgnoreCase | RegexOptions.Singleline);
        private readonly MarkdownPipeline _pipeline;
        private LoreContentPack? _contentPack;

        public LoreBrowserService()
        {
            _pipeline = new MarkdownPipelineBuilder()
                .UseAdvancedExtensions()
                .Build();
        }

        public LoreIndex LoadIndex(string? startDirectory = null)
        {
            string projectRoot = FindProjectRoot(startDirectory)
                ?? throw new DirectoryNotFoundException("Could not locate Lore content or a Lore pack.");

            _contentPack = null;
            if (TryLoadContentPack(projectRoot, out LoreContentPack? contentPack, out List<LoreTreeItem> packRootItems, out Dictionary<string, LoreDocument> packDocumentMap))
            {
                _contentPack = contentPack;
                IReadOnlyList<LoreDocument> packDocuments = packDocumentMap.Values
                    .OrderBy(static doc => doc.Order ?? int.MaxValue)
                    .ThenBy(static doc => doc.Title, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                LoreDocument? packHome = packDocuments.FirstOrDefault(static doc => doc.RelativePath.Equals("lore-book/BOOK.md", StringComparison.OrdinalIgnoreCase))
                    ?? packDocuments.FirstOrDefault(static doc => doc.RelativePath.Equals("BOOK.md", StringComparison.OrdinalIgnoreCase))
                    ?? packDocuments.FirstOrDefault();
                return new LoreIndex(projectRoot, packDocuments, CloneTree(packRootItems), true, packHome, "content-pack");
            }

            string canonicalLoreDirectory = Path.Combine(projectRoot, "lore");
            if (Directory.Exists(canonicalLoreDirectory))
            {
                BuildFallbackIndex(canonicalLoreDirectory, out List<LoreTreeItem> canonicalRootItems, out Dictionary<string, LoreDocument> canonicalDocumentMap);
                IReadOnlyList<LoreDocument> canonicalDocuments = canonicalDocumentMap.Values
                    .OrderBy(static doc => doc.Order ?? int.MaxValue)
                    .ThenBy(static doc => doc.Title, StringComparer.OrdinalIgnoreCase)
                    .ToList();
                LoreDocument? canonicalHome = canonicalDocuments.FirstOrDefault(static doc => doc.RelativePath.Equals("_index.md", StringComparison.OrdinalIgnoreCase))
                    ?? canonicalDocuments.FirstOrDefault();
                return new LoreIndex(projectRoot, canonicalDocuments, CloneTree(canonicalRootItems), false, canonicalHome, "canonical-files");
            }

            string loreBookDirectory = Path.Combine(projectRoot, "lore-book");
            if (!Directory.Exists(loreBookDirectory))
            {
                throw new DirectoryNotFoundException(MissingLoreBookMessage);
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
            return new LoreIndex(projectRoot, documents, CloneTree(rootItems), usingLoreBook, homeDocument, usingLoreBook ? "book-files" : "fallback-files");
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

        public bool DocumentExists(string sourcePath)
        {
            string normalized = NormalizeDocumentKey(sourcePath);
            if (TryGetPackedDocument(normalized, out _))
            {
                return true;
            }

            return File.Exists(normalized);
        }

        public string NormalizeDocumentKey(string sourcePath)
        {
            if (string.IsNullOrWhiteSpace(sourcePath))
            {
                return string.Empty;
            }

            string withoutAnchor = RemoveAnchor(sourcePath.Trim());
            if (IsLorePackDocumentUri(withoutAnchor))
            {
                return withoutAnchor;
            }

            return Path.GetFullPath(withoutAnchor);
        }

        public RenderedLoreDocument RenderDocument(string sourcePath, string? anchor = null)
        {
            string normalizedSource = NormalizeDocumentKey(sourcePath);
            if (TryGetPackedDocument(normalizedSource, out LorePackDocument? packedDocument))
            {
                string packedMarkdown = RewritePackedMarkdownLinks(packedDocument!);
                string contentHtml = Markdown.ToHtml(packedMarkdown, _pipeline);
                contentHtml = AnnotateSourceLinks(contentHtml);
                string renderPath = GetRenderPathForDocument(normalizedSource);
                string wrappedHtml = WrapHtmlDocument(packedDocument!.Title, contentHtml, renderPath);

                Directory.CreateDirectory(Path.GetDirectoryName(renderPath)!);
                File.WriteAllText(renderPath, wrappedHtml, Encoding.UTF8);

                string renderUri = AppendAnchor(new Uri(renderPath).AbsoluteUri, anchor);
                return new RenderedLoreDocument(packedDocument.Title, normalizedSource, renderUri, true, anchor);
            }

            string extension = Path.GetExtension(normalizedSource);
            if (extension.Equals(".html", StringComparison.OrdinalIgnoreCase) ||
                extension.Equals(".htm", StringComparison.OrdinalIgnoreCase))
            {
                return new RenderedLoreDocument(
                    Path.GetFileNameWithoutExtension(normalizedSource),
                    normalizedSource,
                    new Uri(normalizedSource).AbsoluteUri,
                    false,
                    anchor);
            }

            string markdown = File.ReadAllText(normalizedSource);
            string title = ResolveMarkdownTitle(markdown, normalizedSource);
            string fileContentHtml = Markdown.ToHtml(markdown, _pipeline);
            fileContentHtml = AnnotateSourceLinks(fileContentHtml);
            string fileRenderPath = GetRenderPathForDocument(normalizedSource);
            string fileWrappedHtml = WrapHtmlDocument(title, fileContentHtml, normalizedSource);

            Directory.CreateDirectory(Path.GetDirectoryName(fileRenderPath)!);
            File.WriteAllText(fileRenderPath, fileWrappedHtml, Encoding.UTF8);

            string fileRenderUri = AppendAnchor(new Uri(fileRenderPath).AbsoluteUri, anchor);
            return new RenderedLoreDocument(title, normalizedSource, fileRenderUri, true, anchor);
        }

        public string? ResolveInternalTarget(string currentSourcePath, string? target)
        {
            if (string.IsNullOrWhiteSpace(target))
            {
                return null;
            }

            string currentNormalized = NormalizeDocumentKey(currentSourcePath);
            string trimmed = target.Trim();
            string targetWithoutAnchor = RemoveAnchor(trimmed);
            if (trimmed.StartsWith("#", StringComparison.Ordinal))
            {
                return currentNormalized;
            }

            if (TryResolveLorePackNavigationUri(targetWithoutAnchor, out string? packedUri))
            {
                return packedUri;
            }

            if (TryGetPackedDocument(currentNormalized, out LorePackDocument? currentPacked))
            {
                return ResolvePackedInternalTarget(currentPacked!, targetWithoutAnchor);
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
            if (Uri.TryCreate(targetWithoutAnchor, UriKind.Absolute, out Uri? absoluteUri))
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
                string candidate = Path.IsPathRooted(targetWithoutAnchor)
                    ? targetWithoutAnchor
                    : Path.GetFullPath(Path.Combine(Path.GetDirectoryName(currentNormalized)!, targetWithoutAnchor));
                resolved = candidate;
            }

            string? loreBookRoot = TryFindLoreBookRootForDocument(currentNormalized);
            if (loreBookRoot != null && !IsSameOrUnderRoot(resolved, loreBookRoot))
            {
                return null;
            }

            string? resolvedPath = ResolveMarkdownOrHtmlPath(resolved);
            if (resolvedPath != null &&
                loreBookRoot != null &&
                !IsSameOrUnderRoot(resolvedPath, loreBookRoot))
            {
                return null;
            }

            return resolvedPath;
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
                string canonicalLore = Path.Combine(directory.FullName, "lore");
                string lorePack = Path.Combine(directory.FullName, LorePackDirectoryName);
                if (Directory.Exists(canonicalLore) || Directory.Exists(loreBook) || Directory.Exists(lorePack))
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
                if (!IsSameOrUnderRoot(filePath, loreBookDirectory))
                {
                    return new LoreTreeItem
                    {
                        Title = title,
                        Order = order
                    };
                }

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
                Title = "Lore library",
                Order = 0
            };
            rootItems.Add(root);

            int order = 0;
            foreach (string file in Directory.GetFiles(loreBookDirectory, "*.md", SearchOption.AllDirectories)
                .OrderBy(static path => path, StringComparer.OrdinalIgnoreCase))
            {
                string relativePath = Path.GetRelativePath(loreBookDirectory, file).Replace('\\', '/');
                LoreDocument document = new()
                {
                    Title = ResolveMarkdownTitle(File.ReadAllText(file), file),
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

        private static bool TryLoadContentPack(
            string projectRoot,
            out LoreContentPack? pack,
            out List<LoreTreeItem> rootItems,
            out Dictionary<string, LoreDocument> documentMap)
        {
            pack = null;
            rootItems = new List<LoreTreeItem>();
            documentMap = new Dictionary<string, LoreDocument>(StringComparer.OrdinalIgnoreCase);

            string packDirectory = Path.Combine(projectRoot, LorePackDirectoryName);
            string indexPath = Path.Combine(packDirectory, LorePackIndexFileName);
            string contentPath = Path.Combine(packDirectory, LorePackContentFileName);
            bool hasPackDirectory = Directory.Exists(packDirectory);
            bool hasPackIndex = File.Exists(indexPath);
            bool hasPackContent = File.Exists(contentPath);
            if (!hasPackDirectory && !hasPackIndex && !hasPackContent)
            {
                return false;
            }

            if (!hasPackIndex)
            {
                throw new InvalidDataException(InvalidLorePackIndexMessage);
            }

            if (!hasPackContent)
            {
                throw new InvalidDataException(InvalidLorePackContentMessage);
            }

            IReadOnlyDictionary<string, LorePackIndexEntry> indexById = LoadPackIndex(indexPath);
            Dictionary<string, LorePackDocument> documentsById = new(StringComparer.OrdinalIgnoreCase);
            Dictionary<string, LorePackDocument> documentsByRelativePath = new(StringComparer.OrdinalIgnoreCase);

            foreach (string line in File.ReadLines(contentPath, Encoding.UTF8))
            {
                if (string.IsNullOrWhiteSpace(line))
                {
                    continue;
                }

                LorePackLine? row;
                try
                {
                    row = JsonSerializer.Deserialize<LorePackLine>(
                        line,
                        new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                }
                catch (JsonException)
                {
                    throw new InvalidDataException(InvalidLorePackContentMessage);
                }

                if (row == null ||
                    string.IsNullOrWhiteSpace(row.Id) ||
                    string.IsNullOrWhiteSpace(row.RelativePath) ||
                    string.IsNullOrWhiteSpace(row.Sha256) ||
                    !row.ByteLength.HasValue ||
                    row.Content == null)
                {
                    throw new InvalidDataException(InvalidLorePackContentMessage);
                }

                string id = ValidateLorePackDocumentId(row.Id);
                string normalizedRelativePath = ValidateLorePackRelativePath(row.RelativePath);
                if (!indexById.TryGetValue(id, out LorePackIndexEntry? indexEntry))
                {
                    throw new InvalidDataException(LorePackIndexContentMismatchMessage);
                }

                if (!normalizedRelativePath.Equals(indexEntry.RelativePath, StringComparison.Ordinal))
                {
                    throw new InvalidDataException(LorePackIndexContentMismatchMessage);
                }

                if (documentsById.ContainsKey(id))
                {
                    throw new InvalidDataException(DuplicateLorePackDocumentIdMessage);
                }

                if (documentsByRelativePath.ContainsKey(normalizedRelativePath))
                {
                    throw new InvalidDataException(DuplicateLorePackDocumentPathMessage);
                }

                string title = string.IsNullOrWhiteSpace(row.Title)
                    ? Path.GetFileNameWithoutExtension(normalizedRelativePath).Replace('-', ' ')
                    : row.Title.Trim();
                string sha256 = ComputeContentSha256(row.Content);
                int byteLength = Encoding.UTF8.GetByteCount(row.Content);
                if (!sha256.Equals(row.Sha256, StringComparison.OrdinalIgnoreCase) ||
                    !sha256.Equals(indexEntry.Sha256, StringComparison.OrdinalIgnoreCase) ||
                    row.ByteLength.Value != byteLength ||
                    indexEntry.ByteLength != byteLength)
                {
                    throw new InvalidDataException(LorePackContentHashMismatchMessage);
                }

                LorePackDocument document = new(id, normalizedRelativePath, title, row.Content, sha256, byteLength, indexEntry.Order);
                documentsById[id] = document;
                documentsByRelativePath[normalizedRelativePath] = document;
            }

            if (indexById.Count != documentsById.Count)
            {
                throw new InvalidDataException(LorePackIndexContentMismatchMessage);
            }

            if (documentsById.Count == 0)
            {
                throw new InvalidDataException(InvalidLorePackIndexMessage);
            }

            ValidatePackedMarkdownLinks(documentsById.Values, documentsByRelativePath);

            pack = new LoreContentPack(documentsById, documentsByRelativePath);
            foreach (LorePackDocument packedDocument in documentsById.Values.OrderBy(static doc => doc.Order).ThenBy(static doc => doc.RelativePath, StringComparer.OrdinalIgnoreCase))
            {
                string sourcePath = ToLorePackSourcePath(packedDocument.Id);
                LoreDocument document = new()
                {
                    Title = packedDocument.Title,
                    FilePath = sourcePath,
                    RelativePath = packedDocument.RelativePath,
                    IsIndex = IsIndexFile(packedDocument.RelativePath),
                    Order = packedDocument.Order
                };
                documentMap[sourcePath] = document;
                AddPackedDocumentToTree(rootItems, document);
            }

            return true;
        }

        private static string ValidateLorePackDocumentId(string id)
        {
            if (string.IsNullOrWhiteSpace(id) ||
                !string.Equals(id, id.Trim(), StringComparison.Ordinal) ||
                !LORE_PACK_DOCUMENT_ID_REGEX().IsMatch(id))
            {
                throw new InvalidDataException(InvalidLorePackDocumentIdMessage);
            }

            return id;
        }

        private static string ValidateLorePackRelativePath(string relativePath)
        {
            if (string.IsNullOrWhiteSpace(relativePath))
            {
                throw new InvalidDataException(InvalidLorePackDocumentPathMessage);
            }

            if (!string.Equals(relativePath, relativePath.Trim(), StringComparison.Ordinal))
            {
                throw new InvalidDataException(InvalidLorePackDocumentPathMessage);
            }

            if (relativePath.Any(static character => char.IsControl(character)))
            {
                throw new InvalidDataException(InvalidLorePackDocumentPathMessage);
            }

            if (relativePath.Contains('\\', StringComparison.Ordinal) ||
                relativePath.StartsWith("/", StringComparison.Ordinal) ||
                relativePath.Contains(':', StringComparison.Ordinal))
            {
                throw new InvalidDataException(InvalidLorePackDocumentPathMessage);
            }

            string[] parts = relativePath.Split('/');
            if (parts.Any(static part =>
                    part.Length == 0 ||
                    part.Equals(".", StringComparison.Ordinal) ||
                    part.Equals("..", StringComparison.Ordinal) ||
                    !string.Equals(part, part.Trim(), StringComparison.Ordinal)))
            {
                throw new InvalidDataException(InvalidLorePackDocumentPathMessage);
            }

            return relativePath;
        }

        private static IReadOnlyDictionary<string, LorePackIndexEntry> LoadPackIndex(string indexPath)
        {
            Dictionary<string, LorePackIndexEntry> indexById = new(StringComparer.OrdinalIgnoreCase);
            HashSet<string> relativePaths = new(StringComparer.OrdinalIgnoreCase);
            using JsonDocument document = ParseLorePackIndex(indexPath);
            if (!document.RootElement.TryGetProperty("schema", out JsonElement schemaElement) ||
                schemaElement.ValueKind != JsonValueKind.String ||
                !LorePackSchema.Equals(schemaElement.GetString(), StringComparison.Ordinal))
            {
                throw new InvalidDataException(InvalidLorePackIndexMessage);
            }

            if (!document.RootElement.TryGetProperty("documents", out JsonElement documents) ||
                documents.ValueKind != JsonValueKind.Array)
            {
                throw new InvalidDataException(InvalidLorePackIndexMessage);
            }

            if (!document.RootElement.TryGetProperty("documentCount", out JsonElement countElement) ||
                !countElement.TryGetInt32(out int documentCount) ||
                documentCount != documents.GetArrayLength())
            {
                throw new InvalidDataException(InvalidLorePackIndexMessage);
            }

            int fallbackOrder = 0;
            foreach (JsonElement item in documents.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.Object ||
                    !item.TryGetProperty("id", out JsonElement idElement) ||
                    !item.TryGetProperty("relativePath", out JsonElement relativePathElement) ||
                    !item.TryGetProperty("sha256", out JsonElement shaElement) ||
                    !item.TryGetProperty("byteLength", out JsonElement byteLengthElement))
                {
                    throw new InvalidDataException(InvalidLorePackIndexMessage);
                }

                if (idElement.ValueKind != JsonValueKind.String ||
                    relativePathElement.ValueKind != JsonValueKind.String ||
                    shaElement.ValueKind != JsonValueKind.String)
                {
                    throw new InvalidDataException(InvalidLorePackIndexMessage);
                }

                string? id = idElement.GetString();
                string? sha256 = shaElement.GetString();
                if (string.IsNullOrWhiteSpace(id) ||
                    string.IsNullOrWhiteSpace(sha256) ||
                    !byteLengthElement.TryGetInt32(out int byteLength) ||
                    byteLength < 0)
                {
                    throw new InvalidDataException(InvalidLorePackIndexMessage);
                }

                string normalizedId = ValidateLorePackDocumentId(id);
                string normalizedRelativePath = ValidateLorePackRelativePath(relativePathElement.GetString() ?? string.Empty);
                if (indexById.ContainsKey(normalizedId))
                {
                    throw new InvalidDataException(DuplicateLorePackDocumentIdMessage);
                }

                if (!relativePaths.Add(normalizedRelativePath))
                {
                    throw new InvalidDataException(DuplicateLorePackDocumentPathMessage);
                }

                int order = item.TryGetProperty("order", out JsonElement orderElement) && orderElement.TryGetInt32(out int parsedOrder)
                    ? parsedOrder
                    : fallbackOrder;
                indexById[normalizedId] = new LorePackIndexEntry(normalizedId, normalizedRelativePath, sha256.Trim(), byteLength, order);
                fallbackOrder++;
            }

            return indexById;
        }

        private static JsonDocument ParseLorePackIndex(string indexPath)
        {
            try
            {
                return JsonDocument.Parse(File.ReadAllText(indexPath, Encoding.UTF8));
            }
            catch (JsonException)
            {
                throw new InvalidDataException(InvalidLorePackIndexMessage);
            }
        }

        private static void AddPackedDocumentToTree(List<LoreTreeItem> rootItems, LoreDocument document)
        {
            string[] parts = document.RelativePath.Split('/', StringSplitOptions.RemoveEmptyEntries);
            if (parts.Length == 0)
            {
                rootItems.Add(new LoreTreeItem
                {
                    Title = document.Title,
                    FilePath = document.FilePath,
                    RelativePath = document.RelativePath,
                    IsIndex = document.IsIndex,
                    Order = document.Order
                });
                return;
            }

            List<LoreTreeItem> currentItems = rootItems;
            for (int index = 0; index < parts.Length - 1; index++)
            {
                string directoryTitle = FormatTreeSegment(parts[index]);
                LoreTreeItem? existing = currentItems.FirstOrDefault(item =>
                    string.IsNullOrWhiteSpace(item.FilePath) &&
                    item.Title.Equals(directoryTitle, StringComparison.OrdinalIgnoreCase));
                if (existing == null)
                {
                    existing = new LoreTreeItem
                    {
                        Title = directoryTitle,
                        Order = document.Order
                    };
                    currentItems.Add(existing);
                    currentItems.Sort(CompareTreeItems);
                }

                currentItems = existing.Children;
            }

            currentItems.Add(new LoreTreeItem
            {
                Title = document.Title,
                FilePath = document.FilePath,
                RelativePath = document.RelativePath,
                IsIndex = document.IsIndex,
                Order = document.Order
            });
            currentItems.Sort(CompareTreeItems);
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

        private bool MatchesQuery(LoreTreeItem item, string query)
        {
            if (item.Title.Contains(query, StringComparison.OrdinalIgnoreCase) ||
                (!string.IsNullOrWhiteSpace(item.RelativePath) &&
                 item.RelativePath.Contains(query, StringComparison.OrdinalIgnoreCase)))
            {
                return true;
            }

            if (string.IsNullOrWhiteSpace(item.FilePath))
            {
                return false;
            }

            if (TryGetPackedDocument(item.FilePath, out LorePackDocument? packedDocument))
            {
                return packedDocument!.Content.Contains(query, StringComparison.OrdinalIgnoreCase);
            }

            if (!File.Exists(item.FilePath))
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

        private bool TryGetPackedDocument(string sourcePath, out LorePackDocument? document)
        {
            document = null;
            if (_contentPack == null || !TryGetLorePackDocumentId(sourcePath, out string? id))
            {
                return false;
            }

            return id != null && _contentPack.DocumentsById.TryGetValue(id, out document);
        }

        private string? ResolvePackedInternalTarget(LorePackDocument currentDocument, string target)
        {
            if (_contentPack == null ||
                string.IsNullOrWhiteSpace(target) ||
                target.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                target.StartsWith("https://", StringComparison.OrdinalIgnoreCase) ||
                target.StartsWith("mailto:", StringComparison.OrdinalIgnoreCase) ||
                target.StartsWith("data:", StringComparison.OrdinalIgnoreCase) ||
                target.StartsWith("javascript:", StringComparison.OrdinalIgnoreCase))
            {
                return null;
            }

            string decodedTarget = DecodeLoreLinkPathPart(target);
            string candidate = decodedTarget.StartsWith("/", StringComparison.Ordinal)
                ? decodedTarget.TrimStart('/')
                : Path.Combine(Path.GetDirectoryName(currentDocument.RelativePath) ?? string.Empty, decodedTarget).Replace('\\', '/');

            LorePackDocument? resolved = ResolvePackedRelativeDocument(candidate);
            return resolved == null ? null : ToLorePackSourcePath(resolved.Id);
        }

        private LorePackDocument? ResolvePackedRelativeDocument(string candidate)
        {
            if (_contentPack == null)
            {
                return null;
            }

            return ResolvePackedRelativeDocument(candidate, _contentPack.DocumentsByRelativePath);
        }

        private static LorePackDocument? ResolvePackedRelativeDocument(string candidate, IReadOnlyDictionary<string, LorePackDocument> documentsByRelativePath)
        {
            if (!TryNormalizeRelativePath(candidate, out string normalized))
            {
                return null;
            }

            string[] candidates =
            {
                normalized,
                $"{normalized}.md",
                $"{normalized}.html",
                $"{normalized}/_index.md",
                $"{normalized}/README.md",
                $"{normalized}/index.md"
            };

            foreach (string item in candidates)
            {
                if (TryNormalizeRelativePath(item, out string candidateKey) &&
                    documentsByRelativePath.TryGetValue(candidateKey, out LorePackDocument? document))
                {
                    return document;
                }
            }

            return null;
        }

        private static void ValidatePackedMarkdownLinks(IEnumerable<LorePackDocument> documents, IReadOnlyDictionary<string, LorePackDocument> documentsByRelativePath)
        {
            foreach (LorePackDocument document in documents)
            {
                foreach (Match match in LORE_BOOK_MARKDOWN_LINK_REGEX().Matches(document.Content))
                {
                    string target = match.Groups["target"].Value.Trim();
                    string pathPart = DecodeLoreLinkPathPart(RemoveAnchor(target));
                    if (string.IsNullOrWhiteSpace(pathPart) ||
                        pathPart.StartsWith("#", StringComparison.Ordinal) ||
                        IsExternalLoreLinkTarget(pathPart))
                    {
                        continue;
                    }

                    string candidate = pathPart.StartsWith("/", StringComparison.Ordinal)
                        ? pathPart.TrimStart('/')
                        : Path.Combine(Path.GetDirectoryName(document.RelativePath) ?? string.Empty, pathPart).Replace('\\', '/');
                    if (ResolvePackedRelativeDocument(candidate, documentsByRelativePath) == null)
                    {
                        throw new InvalidDataException(InvalidLorePackContentMessage);
                    }
                }
            }
        }

        private static bool IsExternalLoreLinkTarget(string value)
        {
            return Regex.IsMatch(value, @"^[a-zA-Z][a-zA-Z0-9+.-]*:", RegexOptions.CultureInvariant);
        }

        private static string DecodeLoreLinkPathPart(string value)
        {
            try
            {
                return Uri.UnescapeDataString(value);
            }
            catch (UriFormatException)
            {
                return value;
            }
        }

        private string RewritePackedMarkdownLinks(LorePackDocument document)
        {
            return LORE_BOOK_MARKDOWN_LINK_REGEX().Replace(document.Content, match =>
            {
                string target = match.Groups["target"].Value.Trim();
                string pathPart = RemoveAnchor(target);
                string anchor = ExtractAnchor(target) is { } extractedAnchor ? $"#{Uri.EscapeDataString(extractedAnchor)}" : string.Empty;
                if (string.IsNullOrWhiteSpace(pathPart) ||
                    pathPart.StartsWith("#", StringComparison.Ordinal) ||
                    pathPart.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                    pathPart.StartsWith("https://", StringComparison.OrdinalIgnoreCase) ||
                    pathPart.StartsWith("mailto:", StringComparison.OrdinalIgnoreCase))
                {
                    return match.Value;
                }

                LorePackDocument? resolved = ResolvePackedInternalTarget(document, pathPart) is { } packedTarget &&
                    TryGetPackedDocument(packedTarget, out LorePackDocument? targetDocument)
                        ? targetDocument
                        : null;
                if (resolved == null)
                {
                    return match.Value;
                }

                string packedUri = $"{LorePackNavigationScheme}://document/{Uri.EscapeDataString(resolved.Id)}{anchor}";
                return $"{match.Groups["prefix"].Value}{packedUri}{match.Groups["suffix"].Value}";
            });
        }

        [GeneratedRegex(@"(?<prefix>\[[^\]]+\]\()(?<target>[^)]+)(?<suffix>\))", RegexOptions.Compiled)]
        private static partial Regex LORE_BOOK_MARKDOWN_LINK_REGEX();

        [GeneratedRegex(@"^[A-Za-z0-9][A-Za-z0-9._-]*$", RegexOptions.Compiled)]
        private static partial Regex LORE_PACK_DOCUMENT_ID_REGEX();

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

        private static string? TryFindLoreBookRootForDocument(string documentPath)
        {
            if (string.IsNullOrWhiteSpace(documentPath))
            {
                return null;
            }

            string fullPath;
            try
            {
                fullPath = Path.GetFullPath(documentPath);
            }
            catch
            {
                return null;
            }

            DirectoryInfo? directory = File.Exists(fullPath)
                ? new FileInfo(fullPath).Directory
                : new DirectoryInfo(Path.GetDirectoryName(fullPath) ?? fullPath);
            while (directory != null)
            {
                if (directory.Name.Equals("lore-book", StringComparison.OrdinalIgnoreCase))
                {
                    return directory.FullName;
                }

                directory = directory.Parent;
            }

            return null;
        }

        private static bool IsSameOrUnderRoot(string candidatePath, string rootPath)
        {
            if (string.IsNullOrWhiteSpace(candidatePath) || string.IsNullOrWhiteSpace(rootPath))
            {
                return false;
            }

            string candidate = Path.GetFullPath(candidatePath)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string root = Path.GetFullPath(rootPath)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            return candidate.Equals(root, StringComparison.OrdinalIgnoreCase) ||
                   candidate.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) ||
                   candidate.StartsWith(root + Path.AltDirectorySeparatorChar, StringComparison.OrdinalIgnoreCase);
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
    .source-link {
      display: inline-flex;
      align-items: baseline;
      gap: 0.35rem;
    }
    .source-link-badge {
      display: inline-block;
      padding: 0.05rem 0.32rem;
      border: 1px solid #b7c6eb;
      border-radius: 999px;
      background: #eef3ff;
      color: #334f91;
      font-size: 0.72rem;
      font-weight: 600;
      line-height: 1.35;
      text-decoration: none;
      vertical-align: baseline;
    }
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

        private static string AnnotateSourceLinks(string html)
        {
            return HtmlAnchorRegex.Replace(html, match =>
            {
                string href = match.Groups["href"].Value;
                if (IsProjectSourceLink(href))
                {
                    return AnnotateBrowserLink(
                        match,
                        "source-link",
                        "Opens GitHub source in your browser",
                        "Source link; opens GitHub in your browser",
                        "Source");
                }

                if (IsExternalBrowserLink(href))
                {
                    return AnnotateBrowserLink(
                        match,
                        "external-link",
                        "Opens external site in your browser",
                        "External link; opens in your browser",
                        "External");
                }

                return match.Value;
            });
        }

        private static string AnnotateBrowserLink(Match match, string className, string title, string ariaLabel, string badge)
        {
            string attrs = match.Groups["attrs"].Value;
            if (!Regex.IsMatch(attrs, @"\bclass\s*=", RegexOptions.IgnoreCase))
            {
                attrs += $" class=\"{className}\"";
            }

            if (!Regex.IsMatch(attrs, @"\btitle\s*=", RegexOptions.IgnoreCase))
            {
                attrs += $" title=\"{title}\"";
            }

            if (!Regex.IsMatch(attrs, @"\baria-label\s*=", RegexOptions.IgnoreCase))
            {
                attrs += $" aria-label=\"{ariaLabel}\"";
            }

            string content = match.Groups["content"].Value;
            return $"<a {attrs}>{content}<span class=\"source-link-badge\" aria-hidden=\"true\">{badge}</span></a>";
        }

        private static bool IsProjectSourceLink(string value)
        {
            return Uri.TryCreate(value, UriKind.Absolute, out Uri? uri) &&
                   (uri.Scheme.Equals("https", StringComparison.OrdinalIgnoreCase) ||
                    uri.Scheme.Equals("http", StringComparison.OrdinalIgnoreCase)) &&
                   uri.Host.Equals("github.com", StringComparison.OrdinalIgnoreCase) &&
                   uri.AbsolutePath.StartsWith("/dlprentice/Onslaught-Career-Editor/", StringComparison.OrdinalIgnoreCase);
        }

        private static bool IsExternalBrowserLink(string value)
        {
            return Uri.TryCreate(value, UriKind.Absolute, out Uri? uri) &&
                   (uri.Scheme.Equals("https", StringComparison.OrdinalIgnoreCase) ||
                    uri.Scheme.Equals("http", StringComparison.OrdinalIgnoreCase) ||
                    uri.Scheme.Equals("mailto", StringComparison.OrdinalIgnoreCase));
        }

        private static string GetRenderPathForDocument(string sourcePath)
        {
            string fileName = TryGetLorePackDocumentId(sourcePath, out string? id)
                ? id ?? "packed-document"
                : Path.GetFileNameWithoutExtension(sourcePath) ?? "document";
            string safeName = Regex.Replace(fileName, @"[^a-zA-Z0-9_-]", "_");
            string hash = ComputeShortHash(sourcePath);
            return Path.Combine(Path.GetTempPath(), "OnslaughtCareerEditor", "LoreRender", $"{safeName}-{hash}.html");
        }

        private static string ComputeShortHash(string value)
        {
            using SHA1 sha1 = SHA1.Create();
            byte[] hash = sha1.ComputeHash(Encoding.UTF8.GetBytes(value));
            return string.Concat(hash.Take(6).Select(static value => value.ToString("x2")));
        }

        private static string ComputeContentSha256(string value)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(value);
            return Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
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

        private static string RemoveAnchor(string value)
        {
            int anchorIndex = value.IndexOf('#');
            return anchorIndex >= 0 ? value[..anchorIndex] : value;
        }

        private static bool IsLorePackDocumentUri(string value)
        {
            return value.StartsWith(LorePackSourcePrefix, StringComparison.OrdinalIgnoreCase);
        }

        private static bool TryGetLorePackDocumentId(string sourcePath, out string? id)
        {
            id = null;
            if (!IsLorePackDocumentUri(sourcePath))
            {
                return false;
            }

            id = sourcePath[LorePackSourcePrefix.Length..];
            return !string.IsNullOrWhiteSpace(id);
        }

        private static string ToLorePackSourcePath(string id)
        {
            return $"{LorePackSourcePrefix}{id}";
        }

        private static bool TryResolveLorePackNavigationUri(string value, out string? packedUri)
        {
            packedUri = null;
            if (!Uri.TryCreate(value, UriKind.Absolute, out Uri? uri) ||
                !uri.Scheme.Equals(LorePackNavigationScheme, StringComparison.OrdinalIgnoreCase) ||
                !uri.Host.Equals("document", StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            string id = Uri.UnescapeDataString(uri.AbsolutePath.Trim('/'));
            if (string.IsNullOrWhiteSpace(id))
            {
                return false;
            }

            packedUri = ToLorePackSourcePath(id);
            return true;
        }

        private static string NormalizeRelativePath(string value)
        {
            return TryNormalizeRelativePath(value, out string normalized)
                ? normalized
                : string.Empty;
        }

        private static bool TryNormalizeRelativePath(string value, out string normalized)
        {
            string current = value.Replace('\\', '/').Trim().TrimStart('/');
            while (current.Contains("//", StringComparison.Ordinal))
            {
                current = current.Replace("//", "/", StringComparison.Ordinal);
            }

            List<string> parts = new();
            foreach (string part in current.Split('/', StringSplitOptions.RemoveEmptyEntries))
            {
                if (part.Equals(".", StringComparison.Ordinal))
                {
                    continue;
                }

                if (part.Equals("..", StringComparison.Ordinal))
                {
                    if (parts.Count == 0)
                    {
                        normalized = string.Empty;
                        return false;
                    }

                    parts.RemoveAt(parts.Count - 1);
                    continue;
                }

                parts.Add(part);
            }

            normalized = string.Join("/", parts);
            return true;
        }

        private static string FormatTreeSegment(string value)
        {
            return value.Replace('-', ' ').Replace('_', ' ');
        }

        private static int CompareTreeItems(LoreTreeItem left, LoreTreeItem right)
        {
            int leftOrder = left.Order ?? int.MaxValue;
            int rightOrder = right.Order ?? int.MaxValue;
            int orderCompare = leftOrder.CompareTo(rightOrder);
            return orderCompare != 0
                ? orderCompare
                : string.Compare(left.Title, right.Title, StringComparison.OrdinalIgnoreCase);
        }

        private sealed record LoreContentPack(
            IReadOnlyDictionary<string, LorePackDocument> DocumentsById,
            IReadOnlyDictionary<string, LorePackDocument> DocumentsByRelativePath);

        private sealed record LorePackIndexEntry(
            string Id,
            string RelativePath,
            string Sha256,
            int ByteLength,
            int Order);

        private sealed record LorePackDocument(
            string Id,
            string RelativePath,
            string Title,
            string Content,
            string Sha256,
            int ByteLength,
            int Order);

        private sealed class LorePackLine
        {
            public string Id { get; set; } = string.Empty;
            public string RelativePath { get; set; } = string.Empty;
            public string Title { get; set; } = string.Empty;
            public string Content { get; set; } = string.Empty;
            public string Sha256 { get; set; } = string.Empty;
            public int? ByteLength { get; set; }
        }
    }

    public sealed record LoreIndex(
        string ProjectRoot,
        IReadOnlyList<LoreDocument> Documents,
        IReadOnlyList<LoreTreeItem> RootItems,
        bool UsingLoreBook,
        LoreDocument? HomeDocument,
        string SourceKind)
    {
        public bool UsingContentPack => SourceKind.Equals("content-pack", StringComparison.OrdinalIgnoreCase);
    }

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
