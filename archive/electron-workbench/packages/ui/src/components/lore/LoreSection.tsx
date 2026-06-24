import { useCallback, useMemo, useState } from "react";
import { ArticleOutline } from "@/components/lore/ArticleOutline";
import { ArticleReader, type LoreLinkNotice } from "@/components/lore/ArticleReader";
import { DocumentLibrary } from "@/components/lore/DocumentLibrary";
import { extractMarkdownHeadings, markdownHeadingId, type MarkdownLinkClick } from "@/components/lore/MarkdownRenderer";
import type { ContentDocumentSummary, ContentIndexSummary } from "@/types/onslaught-api";

type AudienceFilter = "all" | "community" | "maintainer";

interface LoreSectionProps {
  contentIndex: ContentIndexSummary | null;
  contentDocument: ContentDocumentSummary | null;
  visibleContentItems: ContentIndexSummary["items"];
  contentAudienceCounts: Record<AudienceFilter, number>;
  contentQuery: string;
  contentAudienceFilter: AudienceFilter;
  contentBusy: boolean;
  contentError: string | null;
  onContentQueryChange: (value: string) => void;
  onContentAudienceFilterChange: (value: AudienceFilter) => void;
  onSelectContentDocument: (id: string) => Promise<void>;
  onRefreshContentIndex: () => Promise<void>;
  onOpenExternal: (url: string) => Promise<void>;
}

export function LoreSection({
  contentIndex,
  contentDocument,
  visibleContentItems,
  contentAudienceCounts,
  contentQuery,
  contentAudienceFilter,
  contentBusy,
  contentError,
  onContentQueryChange,
  onContentAudienceFilterChange,
  onSelectContentDocument,
  onRefreshContentIndex,
  onOpenExternal
}: LoreSectionProps) {
  const [linkNotice, setLinkNotice] = useState<LoreLinkNotice | null>(null);
  const selectedItem = useMemo(
    () => contentIndex?.items.find((item) => item.id === contentDocument?.id) ?? null,
    [contentDocument?.id, contentIndex]
  );
  const headings = useMemo(
    () => (contentDocument ? extractMarkdownHeadings(contentDocument.markdown).slice(0, 14) : []),
    [contentDocument]
  );
  const resolveContentLink = useMemo(() => {
    const items = contentIndex?.items ?? [];
    return (href: string) => {
      const { pathPart } = splitMarkdownHref(href);
      if (!pathPart) return null;

      const decodedPath = decodeHref(pathPart).replace(/\\/g, "/");
      const normalizedRootPath = normalizeDocPath(decodedPath);
      const normalizedCurrentPath = selectedItem
        ? normalizeDocPath(`${dirname(selectedItem.relativePath)}/${decodedPath}`)
        : normalizedRootPath;
      const normalizedId = normalizedRootPath.replace(/\.md$/i, "").toLowerCase();

      return (
        items.find((item) => {
          const itemPath = normalizeDocPath(item.relativePath);
          const itemName = itemPath.split("/").at(-1)?.replace(/\.md$/i, "").toLowerCase();
          const titleSlug = item.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
          return (
            item.id.toLowerCase() === normalizedId ||
            itemPath.toLowerCase() === normalizedRootPath.toLowerCase() ||
            itemPath.toLowerCase() === normalizedCurrentPath.toLowerCase() ||
            itemName === normalizedId.split("/").at(-1) ||
            titleSlug === normalizedId.split("/").at(-1)
          );
        }) ?? null
      );
    };
  }, [contentIndex?.items, selectedItem]);

  const scrollToHeading = useCallback((hash: string, noticeText = "Jumped within this document.") => {
    const targetId = markdownHeadingId(decodeHref(hash));
    window.setTimeout(() => {
      const element = document.getElementById(targetId);
      if (element) {
        element.scrollIntoView({ block: "start", behavior: "smooth" });
        setLinkNotice({ tone: "good", message: noticeText });
      } else {
        setLinkNotice({ tone: "warn", message: "That section is not visible in the current document." });
      }
    }, 0);
  }, []);

  const handleMarkdownLinkClick = useCallback(
    async ({ href, text }: MarkdownLinkClick) => {
      const cleanHref = href.trim();
      if (!cleanHref) {
        setLinkNotice({ tone: "warn", message: "That link is empty." });
        return;
      }

      if (isUnsafeHref(cleanHref)) {
        setLinkNotice({ tone: "warn", message: "That link type is blocked in the reader." });
        return;
      }

      if (isExternalHref(cleanHref)) {
        try {
          await onOpenExternal(cleanHref);
          setLinkNotice({ tone: "neutral", message: "Opened the link in your browser." });
        } catch {
          setLinkNotice({ tone: "warn", message: "Could not open that link from the workbench." });
        }
        return;
      }

      const { pathPart, hash } = splitMarkdownHref(cleanHref);
      if (!pathPart && hash) {
        scrollToHeading(hash);
        return;
      }

      const target = resolveContentLink(cleanHref);
      if (!target) {
        setLinkNotice({
          tone: "warn",
          message: `"${text}" is not in the curated reader yet.`
        });
        return;
      }

      try {
        await onSelectContentDocument(target.id);
        setLinkNotice({ tone: "good", message: `Opened ${target.title}.` });
        if (hash) {
          window.setTimeout(() => scrollToHeading(hash, `Opened ${target.title} and jumped to the section.`), 80);
        }
      } catch {
        setLinkNotice({ tone: "warn", message: `Could not open ${target.title}.` });
      }
    },
    [onOpenExternal, onSelectContentDocument, resolveContentLink, scrollToHeading]
  );

  return (
    <section data-testid="section-lore" className="mx-auto grid w-full max-w-[1540px] gap-5">
      <div className="grid gap-2">
        <h2 className="text-2xl font-semibold text-workbench-text">Lore reader</h2>
        <p className="max-w-3xl text-sm leading-6 text-workbench-muted">
          Read curated lore, preservation notes, and selected maintainer docs without losing the article in tool chrome.
        </p>
      </div>

      <div className="grid gap-5 xl:grid-cols-[20rem_minmax(0,1fr)] 2xl:grid-cols-[20rem_minmax(0,1fr)_18rem]">
        <DocumentLibrary
          contentIndex={contentIndex}
          items={visibleContentItems}
          selectedId={contentDocument?.id ?? null}
          query={contentQuery}
          audienceFilter={contentAudienceFilter}
          audienceCounts={contentAudienceCounts}
          busy={contentBusy}
          error={contentError}
          onQueryChange={onContentQueryChange}
          onAudienceFilterChange={onContentAudienceFilterChange}
          onSelectDocument={onSelectContentDocument}
          onRetry={onRefreshContentIndex}
        />
        <ArticleReader
          document={contentDocument}
          item={selectedItem}
          busy={contentBusy}
          linkNotice={linkNotice}
          onMarkdownLinkClick={handleMarkdownLinkClick}
        />
        <ArticleOutline document={contentDocument} headings={headings} className="xl:col-start-2 2xl:col-start-auto" />
      </div>
    </section>
  );
}

function splitMarkdownHref(href: string) {
  const trimmed = href.trim();
  const hashIndex = trimmed.indexOf("#");
  const pathWithQuery = hashIndex >= 0 ? trimmed.slice(0, hashIndex) : trimmed;
  const hash = hashIndex >= 0 ? trimmed.slice(hashIndex + 1) : "";
  return {
    pathPart: pathWithQuery.split("?")[0].trim(),
    hash: hash.trim()
  };
}

function normalizeDocPath(value: string) {
  const parts: string[] = [];
  for (const rawSegment of value.replace(/\\/g, "/").replace(/^\/+/, "").split("/")) {
    const segment = rawSegment.trim();
    if (!segment || segment === ".") continue;
    if (segment === "..") {
      parts.pop();
      continue;
    }
    parts.push(segment);
  }
  return parts.join("/");
}

function dirname(value: string) {
  return value.replace(/\\/g, "/").split("/").slice(0, -1).join("/");
}

function decodeHref(value: string) {
  try {
    return decodeURIComponent(value.replace(/^#/, ""));
  } catch {
    return value.replace(/^#/, "");
  }
}

function isExternalHref(value: string) {
  return /^https:\/\//i.test(value);
}

function isUnsafeHref(value: string) {
  return /^(javascript:|data:|file:|vbscript:)/i.test(value) || /^[a-z]:[\\/]/i.test(value);
}
