import type { ReactNode } from "react";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";

interface MediaDetailsProps {
  children: ReactNode;
  summary?: string;
}

export function MediaDetails({ children, summary = "source and playback fields" }: MediaDetailsProps) {
  return (
    <DetailsDisclosure title="Details" summary={summary} className="mt-3">
      <div className="grid gap-2 text-xs leading-5 text-workbench-muted">{children}</div>
    </DetailsDisclosure>
  );
}

export function DetailLine({ label, value, mono = false }: { label: string; value: ReactNode; mono?: boolean }) {
  return (
    <div className="grid gap-1 sm:grid-cols-[9rem_minmax(0,1fr)]">
      <span className="font-medium text-workbench-text">{label}</span>
      <span className={mono ? "min-w-0 break-all font-mono" : "min-w-0 break-words"}>{value}</span>
    </div>
  );
}
