import { ListTree } from "lucide-react";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";
import { StatusPill } from "@/components/StatusPill";
import type { MarkdownHeading } from "@/components/lore/MarkdownRenderer";
import type { ContentDocumentSummary } from "@/types/onslaught-api";

interface ArticleOutlineProps {
  document: ContentDocumentSummary | null;
  headings: MarkdownHeading[];
  className?: string;
}

export function ArticleOutline({ document, headings, className = "" }: ArticleOutlineProps) {
  return (
    <aside
      data-testid="lore-article-outline"
      className={`grid gap-4 self-start rounded-lg border border-workbench-border/65 bg-workbench-panel2/82 p-4 ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <ListTree className="h-4 w-4 text-workbench-muted" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-workbench-text">Outline</h2>
          </div>
          <p className="mt-1 text-sm leading-6 text-workbench-muted">Jump within the current document.</p>
        </div>
        <StatusPill tone={headings.length ? "good" : "neutral"}>{headings.length ? `${headings.length} links` : "Quiet"}</StatusPill>
      </div>

      {document && headings.length ? (
        <nav className="grid gap-1" aria-label="Current document outline">
          {headings.slice(0, 14).map((heading) => (
            <a
              key={`${document.id}-${heading.id}`}
              className={`rounded-md px-2 py-2 text-sm leading-5 text-workbench-muted transition hover:bg-[#eaf1ff] hover:text-workbench-text ${
                heading.level > 1 ? "ml-3" : ""
              }`}
              href={`#${heading.id}`}
              title={heading.title}
            >
              {heading.title}
            </a>
          ))}
        </nav>
      ) : (
        <div className="rounded-lg border border-dashed border-workbench-border/70 bg-white p-4 text-sm leading-6 text-workbench-muted">
          {document ? "This document has no headings in the current preview." : "Choose a document to see its outline."}
        </div>
      )}

      {document ? (
        <DetailsDisclosure title="Details" summary="document metadata">
          <div className="grid gap-2 text-xs leading-5 text-workbench-muted">
            <DetailLine label="Relative path" value={document.relativePath} mono />
            <DetailLine label="Audience" value={document.audience} />
            <DetailLine label="Group" value={document.group} />
            <DetailLine label="Byte count" value={document.byteLength.toLocaleString()} />
            <DetailLine label="Read at" value={document.readAt} mono />
            <DetailLine label="Schema" value={document.artifact.schemaVersion} mono />
            <DetailLine label="Note" value={document.artifact.note} />
          </div>
        </DetailsDisclosure>
      ) : null}
    </aside>
  );
}

function DetailLine({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="grid gap-1">
      <span className="font-medium text-workbench-text">{label}</span>
      <span className={mono ? "break-all font-mono" : "break-words"}>{value}</span>
    </div>
  );
}
