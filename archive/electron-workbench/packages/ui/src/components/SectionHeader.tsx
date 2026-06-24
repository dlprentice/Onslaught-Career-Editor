import type { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Tone } from "@/types/onslaught-api";

interface SectionHeaderProps {
  title: string;
  description: ReactNode;
  nextAction?: ReactNode;
  badge?: ReactNode;
  badgeTone?: Tone;
  actions?: ReactNode;
}

export function SectionHeader({ title, description, nextAction, badge, badgeTone = "neutral", actions }: SectionHeaderProps) {
  return (
    <CardHeader>
      <div>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
        {nextAction ? <p className="mt-3 text-sm font-medium text-workbench-text">{nextAction}</p> : null}
      </div>
      {actions ?? (badge ? <Badge tone={badgeTone}>{badge}</Badge> : null)}
    </CardHeader>
  );
}
