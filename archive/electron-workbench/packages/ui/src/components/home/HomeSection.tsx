import { BookOpenText, CheckCircle2, FileSearch, Gamepad2, Image as ImageIcon, Layers3 } from "lucide-react";
import { MetricCard, PageIntro, PageSection, TaskCard } from "@/components/common/ProductPrimitives";
import { StatusPill } from "@/components/StatusPill";
import { Card } from "@/components/ui/card";
import type { RuntimeSnapshot } from "@/types/onslaught-api";
import type { WorkbenchSectionId } from "@/workbenchNav";

interface HomeSectionProps {
  snapshot: RuntimeSnapshot;
  onNavigate: (section: WorkbenchSectionId) => void;
}

export function HomeSection({ snapshot, onNavigate }: HomeSectionProps) {
  const functionMetric = snapshot.metrics.find((metric) => metric.label.toLowerCase().includes("function"));
  const mediaMetric = snapshot.metrics.find((metric) => metric.label.toLowerCase().includes("media"));
  const gateMetric = snapshot.metrics.find((metric) => metric.label.toLowerCase().includes("gate"));

  return (
    <PageSection testId="command-hero">
      <PageIntro
        eyebrow="Battle Engine Aquila"
        title="Start with the task you want to do"
        body="Onslaught helps you explore, modify, and understand Battle Engine Aquila. Choose a task below or continue from the latest readiness summary."
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" data-testid="home-task-cards">
        <TaskCard
          icon={FileSearch}
          title="Edit a Save"
          body="Open a save, inspect progress and settings, then save changes to a copy."
          action="Open Save Lab"
          onClick={() => onNavigate("saves")}
        />
        <TaskCard
          icon={ImageIcon}
          title="Browse Media"
          body="Preview audio, video, textures, models, and language rows from local game files."
          action="Browse Media"
          tone="teal"
          onClick={() => onNavigate("media")}
        />
        <TaskCard
          icon={BookOpenText}
          title="Read Lore"
          body="Explore curated docs, preservation notes, team context, and community lore."
          action="Open Lore"
          tone="violet"
          onClick={() => onNavigate("lore")}
        />
        <TaskCard
          icon={Layers3}
          title="Reverse Engineer Assets"
          body="Search assets, strings, functions, and structures with bounded investigation plans."
          action="Open RE Lab"
          tone="amber"
          onClick={() => onNavigate("re-lab")}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <Card data-testid="home-setup-status">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold text-workbench-text">Setup and system status</h3>
              <p className="mt-1 text-sm text-workbench-muted">The core workbench lanes are ready for local use.</p>
            </div>
            <StatusPill tone="good">All systems go</StatusPill>
          </div>
          <div className="grid gap-3">
            {[
              ["Game folder connected", "Use your local install as read-only input."],
              ["Save support ready", "Career saves and options files are recognized."],
              ["Media preview ready", "Audio, texture, and prepared video previews stay in app."],
              ["Agentic loop available", "Observe, plan, act, and review with explicit boundaries."]
            ].map(([title, detail]) => (
              <div key={title} className="flex items-start gap-3 rounded-lg border border-workbench-border bg-workbench-panel2 p-3">
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-[#16a34a]" aria-hidden="true" />
                <div>
                  <p className="font-medium text-workbench-text">{title}</p>
                  <p className="text-sm text-workbench-muted">{detail}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold text-workbench-text">Readiness summary</h3>
              <p className="mt-1 text-sm text-workbench-muted">A compact view of the current workbench posture.</p>
            </div>
            <StatusPill tone="neutral">Updated {new Date(snapshot.generatedAt).toLocaleDateString()}</StatusPill>
          </div>
          <div className="grid gap-3 md:grid-cols-3">
            <MetricCard label={functionMetric?.label ?? "Function symbols"} value={functionMetric?.value ?? "Ready"} detail="Maintainer lookup coverage" tone="good" />
            <MetricCard label={mediaMetric?.label ?? "Media catalog"} value={mediaMetric?.value ?? "Ready"} detail="Local preview index" tone="good" />
            <MetricCard label={gateMetric?.label ?? "App gates"} value={gateMetric?.value ?? "Passing"} detail="Build and smoke posture" tone="good" />
          </div>
        </Card>
      </div>

      <Card data-testid="home-agentic-loop">
        <div className="grid gap-5 lg:grid-cols-[18rem_minmax(0,1fr)] lg:items-center">
          <div>
            <Gamepad2 className="h-8 w-8 text-[#2457c5]" aria-hidden="true" />
            <h3 className="mt-3 text-lg font-semibold text-workbench-text">How the agentic loop works</h3>
            <p className="mt-2 text-sm leading-6 text-workbench-muted">
              Onslaught guides complex reverse-engineering tasks through bounded, reviewable steps.
            </p>
          </div>
          <div className="grid gap-3 md:grid-cols-4">
            {[
              ["Observe", "Gather signals and data from the game."],
              ["Plan", "Select the right tool and bounded action."],
              ["Act", "Execute safely in the workspace."],
              ["Review", "Verify results and decide the next step."]
            ].map(([title, body], index) => (
              <div key={title} className="rounded-lg border border-workbench-border bg-workbench-panel2 p-4">
                <div className="mb-3 grid h-7 w-7 place-items-center rounded-full bg-[#eaf1ff] text-sm font-semibold text-[#2457c5]">
                  {index + 1}
                </div>
                <p className="font-semibold text-workbench-text">{title}</p>
                <p className="mt-1 text-sm leading-6 text-workbench-muted">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </PageSection>
  );
}
