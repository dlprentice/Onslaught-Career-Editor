import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface DetailsDisclosureProps {
  title?: string;
  summary?: string;
  children: ReactNode;
  className?: string;
}

export function DetailsDisclosure({
  title = "Details",
  summary = "Show technical details",
  children,
  className = ""
}: DetailsDisclosureProps) {
  return (
    <details
      className={cn(
        "rounded-lg border border-workbench-border bg-workbench-panel2 p-3 text-sm text-workbench-muted",
        className
      )}
    >
      <summary className="flex cursor-pointer select-none list-none items-center justify-between gap-3 text-sm font-medium text-workbench-text marker:hidden">
        <span>{title}</span>
        <span className="text-xs font-normal text-workbench-muted">{summary}</span>
      </summary>
      <div className="mt-3 grid gap-2 border-t border-workbench-border pt-3">{children}</div>
    </details>
  );
}
