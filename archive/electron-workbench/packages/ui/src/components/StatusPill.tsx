import type { ReactNode } from "react";
import type { Tone } from "@/types/onslaught-api";
import { cn } from "@/lib/utils";

interface StatusPillProps {
  tone?: Tone;
  children: ReactNode;
  className?: string;
}

export function StatusPill({ tone = "neutral", children, className = "" }: StatusPillProps) {
  const toneClass =
    tone === "good"
      ? "border-[#bbf7d0] bg-[#ecfdf3] text-[#067647]"
      : tone === "warn"
        ? "border-[#fedf89] bg-[#fffaeb] text-[#b54708]"
        : tone === "danger"
          ? "border-[#fecdca] bg-[#fef3f2] text-[#b42318]"
          : "border-workbench-border bg-workbench-panel2 text-workbench-muted";

  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium", toneClass, className)}>
      {children}
    </span>
  );
}
