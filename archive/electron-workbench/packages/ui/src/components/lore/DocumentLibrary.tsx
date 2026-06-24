import { BookOpen, SearchCheck } from "lucide-react";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";
import { StatusPill } from "@/components/StatusPill";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { ContentIndexItem, ContentIndexSummary } from "@/types/onslaught-api";

type AudienceFilter = "all" | "community" | "maintainer";

interface DocumentLibraryProps {
  contentIndex: ContentIndexSummary | null;
  items: ContentIndexItem[];
  selectedId: string | null;
  query: string;
  audienceFilter: AudienceFilter;
  audienceCounts: Record<AudienceFilter, number>;
  busy: boolean;
  error: string | null;
  onQueryChange: (value: string) => void;
  onAudienceFilterChange: (value: AudienceFilter) => void;
  onSelectDocument: (id: string) => void | Promise<void>;
  onRetry: () => void | Promise<void>;
}

export function DocumentLibrary({
  contentIndex,
  items,
  selectedId,
  query,
  audienceFilter,
  audienceCounts,
  busy,
  error,
  onQueryChange,
  onAudienceFilterChange,
  onSelectDocument,
  onRetry
}: DocumentLibraryProps) {
  const filters: Array<{ id: AudienceFilter; label: string }> = [
    { id: "all", label: "All" },
    { id: "community", label: "Community" },
    { id: "maintainer", label: "Maintainer" }
  ];

  return (
    <aside data-testid="lore-document-library" className="grid min-w-0 gap-4 self-start rounded-lg border border-workbench-border/65 bg-workbench-panel2/82 p-4">
      <div>
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold text-workbench-text">Library</h2>
            <p className="mt-1 text-sm leading-6 text-workbench-muted">Search curated reading material.</p>
          </div>
          <StatusPill tone={contentIndex ? "good" : "neutral"}>{contentIndex ? `${contentIndex.items.length} docs` : "Loading"}</StatusPill>
        </div>
        <label className="mt-4 flex min-h-11 items-center gap-2 rounded-md border border-workbench-border/75 bg-white px-3" htmlFor="content-search">
          <SearchCheck className="h-4 w-4 text-workbench-muted" aria-hidden="true" />
          <span className="sr-only">Search docs</span>
          <input
            id="content-search"
            data-testid="content-search"
            className="min-w-0 flex-1 bg-transparent text-sm text-workbench-text outline-none placeholder:text-workbench-muted"
            placeholder="Search docs"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
          />
        </label>
      </div>

      <div className="grid grid-cols-3 gap-1 rounded-md border border-workbench-border/65 bg-white p-1" role="group" aria-label="Content audience">
        {filters.map((filter) => {
          const active = audienceFilter === filter.id;
          return (
            <button
              key={filter.id}
              type="button"
              aria-pressed={active}
              className={cn(
                "min-h-10 rounded px-2 text-xs font-semibold transition",
                active ? "bg-workbench-amber text-[#18130a]" : "text-workbench-muted hover:bg-workbench-panel2 hover:text-workbench-text"
              )}
              onClick={() => onAudienceFilterChange(filter.id)}
            >
              <span>{filter.label}</span>
              <span className="ml-1 tabular-nums opacity-75">{audienceCounts[filter.id]}</span>
            </button>
          );
        })}
      </div>

      <div className="grid max-h-[48rem] gap-3 overflow-auto pr-1">
        {items.map((item) => {
          const selected = selectedId === item.id;
          return (
            <div
              key={item.id}
              className={cn(
                "rounded-lg border p-4 transition",
                selected
                  ? "border-workbench-amber/75 bg-workbench-amber/12"
                  : "border-workbench-border/65 bg-white hover:border-workbench-amber/55"
              )}
            >
              <button className="w-full text-left" type="button" onClick={() => void onSelectDocument(item.id)}>
                <div className="flex items-start gap-3">
                  <span
                    className={cn(
                      "grid h-9 w-9 shrink-0 place-items-center rounded-md border",
                      selected ? "border-workbench-amber/70 bg-workbench-amber/15" : "border-workbench-border/65 bg-workbench-panel2"
                    )}
                  >
                    <BookOpen className="h-4 w-4 text-workbench-muted" aria-hidden="true" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-base font-semibold text-workbench-text">{item.title}</span>
                    <span className="mt-1 block text-sm leading-6 text-workbench-muted">{item.description}</span>
                    <span className="mt-3 flex flex-wrap gap-2">
                      <StatusPill tone={item.communitySafe ? "good" : "warn"}>{item.communitySafe ? "Community" : "Maintainer"}</StatusPill>
                      <StatusPill tone="neutral">{item.group}</StatusPill>
                    </span>
                  </span>
                </div>
              </button>
              <DetailsDisclosure title="Details" summary="document source" className="mt-3">
                <div className="grid gap-2 text-xs leading-5 text-workbench-muted">
                  <div className="grid gap-1">
                    <span className="font-medium text-workbench-text">Relative path</span>
                    <span className="break-all font-mono">{item.relativePath}</span>
                  </div>
                  <div className="grid gap-1">
                    <span className="font-medium text-workbench-text">Document id</span>
                    <span className="break-all font-mono">{item.id}</span>
                  </div>
                </div>
              </DetailsDisclosure>
            </div>
          );
        })}
      </div>

      {contentIndex && items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-workbench-border/70 bg-white p-4 text-sm leading-6 text-workbench-muted">
          No documents match this filter. Clear the search or switch the audience filter.
        </div>
      ) : null}

      {!contentIndex && !busy ? (
        <div className="rounded-lg border border-dashed border-workbench-border/70 bg-white p-4 text-sm leading-6 text-workbench-muted">
          Choose a document to read after the library loads.
        </div>
      ) : null}

      {busy ? <div className="rounded-lg border border-workbench-border/65 bg-white p-4 text-sm text-workbench-muted">Loading document...</div> : null}

      {error ? (
        <div className="rounded-lg border border-[#fecdca] bg-[#fef3f2] p-4 text-sm leading-6 text-[#b42318]">
          <p>{error}</p>
          <Button type="button" size="sm" variant="secondary" className="mt-3" onClick={() => void onRetry()}>
            Retry
          </Button>
        </div>
      ) : null}
    </aside>
  );
}
