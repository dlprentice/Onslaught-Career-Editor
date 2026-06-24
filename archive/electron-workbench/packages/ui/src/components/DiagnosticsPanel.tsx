import type { ReactNode } from "react";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";

interface DiagnosticsPanelProps {
  title?: string;
  summary?: string;
  children: ReactNode;
  className?: string;
}

export function DiagnosticsPanel({
  title = "Diagnostics",
  summary = "Show technical details",
  children,
  className = ""
}: DiagnosticsPanelProps) {
  return (
    <DetailsDisclosure title={title} summary={summary} className={className}>
      {children}
    </DetailsDisclosure>
  );
}
