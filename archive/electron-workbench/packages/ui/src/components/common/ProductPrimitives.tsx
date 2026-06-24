import type { LucideIcon } from "lucide-react";
import { ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { Tone } from "@/types/onslaught-api";

export function PageSection({
  children,
  className = "",
  testId
}: {
  children: React.ReactNode;
  className?: string;
  testId?: string;
}) {
  return (
    <section data-testid={testId} className={cn("mx-auto grid w-full max-w-[1540px] gap-5", className)}>
      {children}
    </section>
  );
}

export function PageIntro({
  eyebrow,
  title,
  body,
  action
}: {
  eyebrow?: string;
  title: string;
  body: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div className="max-w-4xl">
        {eyebrow ? <div className="mb-4 h-1 w-12 rounded-full bg-workbench-amber" aria-hidden="true" /> : null}
        {eyebrow ? <p className="text-sm font-semibold text-workbench-amber">{eyebrow}</p> : null}
        <h2 className="text-3xl font-semibold leading-tight text-workbench-text md:text-4xl">{title}</h2>
        <p className="mt-3 max-w-3xl text-base leading-7 text-workbench-muted">{body}</p>
      </div>
      {action ? <div className="flex shrink-0 flex-wrap gap-2">{action}</div> : null}
    </div>
  );
}

export function TaskCard({
  icon: Icon,
  title,
  body,
  action,
  tone = "blue",
  onClick
}: {
  icon: LucideIcon;
  title: string;
  body: string;
  action: string;
  tone?: "blue" | "teal" | "amber" | "violet";
  onClick: () => void;
}) {
  const toneClass =
    tone === "amber"
      ? "bg-[#fff7e8] text-[#b54708]"
      : tone === "teal"
        ? "bg-[#e8f5f3] text-[#0f766e]"
        : tone === "violet"
          ? "bg-[#f0eafe] text-[#5b21b6]"
          : "bg-[#eaf1ff] text-[#2457c5]";
  return (
    <Card className="group flex h-full flex-col justify-between gap-6 p-5 transition hover:-translate-y-0.5 hover:border-[#9db7f5] hover:shadow-[0_22px_50px_rgba(36,87,197,0.12)]">
      <div>
        <div className={cn("grid h-12 w-12 place-items-center rounded-lg", toneClass)}>
          <Icon className="h-6 w-6" aria-hidden="true" />
        </div>
        <h3 className="mt-5 text-lg font-semibold text-workbench-text">{title}</h3>
        <p className="mt-2 text-sm leading-6 text-workbench-muted">{body}</p>
      </div>
      <Button type="button" onClick={onClick} className="w-fit">
        {action}
        <ChevronRight className="h-4 w-4" aria-hidden="true" />
      </Button>
    </Card>
  );
}

export function MetricCard({
  label,
  value,
  detail,
  tone = "neutral"
}: {
  label: string;
  value: React.ReactNode;
  detail?: React.ReactNode;
  tone?: Tone;
}) {
  const accent =
    tone === "good"
      ? "border-l-[#16a34a]"
      : tone === "warn"
        ? "border-l-workbench-amber"
        : tone === "danger"
          ? "border-l-workbench-red"
          : "border-l-[#9db7f5]";
  return (
    <div className={cn("rounded-lg border border-workbench-border bg-white p-4 shadow-sm border-l-4", accent)}>
      <p className="text-sm font-medium text-workbench-muted">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-workbench-text">{value}</p>
      {detail ? <p className="mt-1 text-sm leading-5 text-workbench-muted">{detail}</p> : null}
    </div>
  );
}

export function StepCard({
  number,
  title,
  body,
  status,
  action,
  active = false,
  children
}: {
  number: number;
  title: string;
  body: string;
  status?: React.ReactNode;
  action?: React.ReactNode;
  active?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <div
      className={cn(
        "rounded-lg border bg-white p-4 shadow-sm",
        active ? "border-[#9db7f5] ring-2 ring-[#dbe7ff]" : "border-workbench-border"
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn("grid h-8 w-8 shrink-0 place-items-center rounded-full text-sm font-semibold", active ? "bg-[#2457c5] text-white" : "bg-workbench-panel2 text-workbench-muted")}>
          {number}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <h3 className="font-semibold text-workbench-text">{title}</h3>
            {status}
          </div>
          <p className="mt-1 text-sm leading-6 text-workbench-muted">{body}</p>
          {children ? <div className="mt-3">{children}</div> : null}
          {action ? <div className="mt-4">{action}</div> : null}
        </div>
      </div>
    </div>
  );
}

export function EmptyState({
  icon: Icon,
  title,
  body,
  action
}: {
  icon: LucideIcon;
  title: string;
  body: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="grid min-h-48 place-items-center rounded-lg border border-dashed border-workbench-border bg-white p-8 text-center">
      <div>
        <Icon className="mx-auto h-10 w-10 text-workbench-muted" aria-hidden="true" />
        <p className="mt-4 text-lg font-semibold text-workbench-text">{title}</p>
        <p className="mt-2 max-w-md text-sm leading-6 text-workbench-muted">{body}</p>
        {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
      </div>
    </div>
  );
}

export function DetailGrid({ children }: { children: React.ReactNode }) {
  return <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{children}</div>;
}

export function DetailTile({ label, value, detail }: { label: string; value: React.ReactNode; detail?: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-workbench-border bg-workbench-panel2 p-3">
      <p className="text-sm font-medium text-workbench-muted">{label}</p>
      <div className="mt-1 text-sm font-semibold text-workbench-text">{value}</div>
      {detail ? <p className="mt-1 text-xs leading-5 text-workbench-muted">{detail}</p> : null}
    </div>
  );
}
