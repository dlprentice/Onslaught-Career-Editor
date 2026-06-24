import { BookOpen, Loader2 } from "lucide-react";
import { StatusPill } from "@/components/StatusPill";
import { MarkdownRenderer, type MarkdownLinkClick } from "@/components/lore/MarkdownRenderer";
import type { ContentDocumentSummary, ContentIndexItem } from "@/types/onslaught-api";

export interface LoreLinkNotice {
  tone: "good" | "warn" | "neutral";
  message: string;
}

interface ArticleReaderProps {
  document: ContentDocumentSummary | null;
  item: ContentIndexItem | null;
  busy: boolean;
  linkNotice: LoreLinkNotice | null;
  onMarkdownLinkClick: (link: MarkdownLinkClick) => void;
}

export function ArticleReader({ document, item, busy, linkNotice, onMarkdownLinkClick }: ArticleReaderProps) {
  return (
    <section data-testid="lore-article-reader" className="min-w-0 rounded-lg border border-workbench-border/65 bg-white p-4 shadow-panel">
      {document ? (
        <div className="mx-auto max-w-[780px]">
          <div className="mb-4 rounded-lg border border-[#d5dbe5] bg-[#f8fafc] p-6 text-[#172033]">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-sm font-medium text-[#60708a]">{document.group}</p>
                <h2 className="mt-2 text-3xl font-semibold leading-tight tracking-normal text-[#111827]">{document.title}</h2>
                {item?.description ? <p className="mt-3 text-base leading-7 text-[#526175]">{item.description}</p> : null}
              </div>
              <div className="flex flex-wrap gap-2">
                <StatusPill tone={document.communitySafe ? "good" : "warn"}>
                  {document.communitySafe ? "Community" : "Maintainer"}
                </StatusPill>
                <StatusPill tone={document.truncated ? "warn" : "good"}>{document.truncated ? "Preview" : "Complete"}</StatusPill>
              </div>
            </div>
          </div>

          {linkNotice ? (
            <div
              data-testid="lore-link-notice"
              role="status"
              className={`mb-4 rounded-lg border px-4 py-3 text-sm leading-6 ${
                linkNotice.tone === "warn"
                  ? "border-[#f0cf8b] bg-[#fff7e3] text-[#6f4a0a]"
                  : linkNotice.tone === "good"
                    ? "border-[#b8d8bf] bg-[#edf8ef] text-[#295b34]"
                    : "border-[#cfd8e5] bg-[#f5f7fb] text-[#40506a]"
              }`}
            >
              {linkNotice.message}
            </div>
          ) : null}

          <article
            data-testid="content-markdown-preview"
            className="rounded-lg border border-[#d5dbe5] bg-[#fbfaf7] px-7 py-7 text-[#263140] shadow-sm md:px-10 md:py-9"
          >
            <MarkdownRenderer markdown={document.markdown} onLinkClick={onMarkdownLinkClick} />
          </article>
        </div>
      ) : (
        <div className="grid min-h-[34rem] place-items-center rounded-lg border border-dashed border-workbench-border/75 bg-workbench-panel2 p-8 text-center">
          <div>
            {busy ? (
              <Loader2 className="mx-auto h-12 w-12 animate-spin text-workbench-muted" aria-hidden="true" />
            ) : (
              <BookOpen className="mx-auto h-12 w-12 text-workbench-muted" aria-hidden="true" />
            )}
            <p className="mt-4 text-xl font-semibold text-workbench-text">{busy ? "Loading document..." : "Choose a document to read."}</p>
            <p className="mt-2 max-w-md text-sm leading-6 text-workbench-muted">
              Select a title from the library. The article will open here with a comfortable reading width.
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
