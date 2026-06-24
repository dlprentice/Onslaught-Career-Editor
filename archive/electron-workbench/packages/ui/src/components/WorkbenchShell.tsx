import type { ReactNode } from "react";
import { Hexagon, SearchCheck, Settings } from "lucide-react";
import { StatusPill } from "@/components/StatusPill";
import { formatWorkbenchMode, navItems, type WorkbenchCommandResult } from "@/workbenchNav";
import type { RuntimeSnapshot } from "@/types/onslaught-api";

interface WorkbenchShellProps {
  snapshot: RuntimeSnapshot;
  activeNav: string;
  activeSection: string;
  commandQuery: string;
  commandResults: WorkbenchCommandResult[];
  verifyBusy: boolean;
  inspectBusy: boolean;
  children: ReactNode;
  aside: ReactNode;
  focusMode?: "default" | "reader";
  onCommandQueryChange: (value: string) => void;
  onNavigate: (sectionId: string) => void;
  onVerifyExecutable: () => void | Promise<void>;
  onInspectSaveFile: () => void | Promise<void>;
}

export function WorkbenchShell({
  snapshot,
  activeNav,
  activeSection,
  commandQuery,
  commandResults,
  verifyBusy: _verifyBusy,
  inspectBusy: _inspectBusy,
  children,
  aside,
  focusMode = "default",
  onCommandQueryChange,
  onNavigate,
  onVerifyExecutable: _onVerifyExecutable,
  onInspectSaveFile: _onInspectSaveFile
}: WorkbenchShellProps) {
  const modeLabel = formatWorkbenchMode(snapshot.mode);
  const activeItem = navItems.find((item) => item.id === activeNav);
  const pageTitle = activeItem?.label ?? activeSection;
  const pagePurpose = activeItem?.purpose ?? "Choose a workbench section to continue.";
  const nextAction = activeItem?.nextAction ?? "Use the action buttons or section navigation to continue.";
  const readerMode = focusMode === "reader";

  return (
    <div className="min-h-screen overflow-hidden bg-workbench-base text-workbench-text">
      <div className="relative flex min-h-screen">
        <aside className="hidden w-[17.5rem] shrink-0 border-r border-[#173456] bg-[#0b1728] p-4 text-white lg:block">
          <div className="mb-7 border-b border-white/10 pb-5">
            <div className="mb-5 flex items-center gap-3">
              <div className="grid h-12 w-12 place-items-center rounded-lg border border-white/10 bg-[#11243b]">
                <Hexagon className="h-6 w-6 text-workbench-amber" aria-hidden="true" />
              </div>
              <div>
                <p className="text-lg font-semibold tracking-[0.12em] text-white">ONSLAUGHT</p>
                <p className="text-xs font-medium tracking-[0.16em] text-[#b7c5d8]">BATTLE ENGINE AQUILA</p>
              </div>
            </div>
            <div className="flex items-center justify-between gap-3 rounded-lg border border-white/10 bg-white/5 p-3 text-sm">
              <span className="text-[#cbd5e1]">Workspace</span>
              <StatusPill tone="good">Ready</StatusPill>
            </div>
            <details className="mt-3 rounded-lg border border-white/10 bg-white/5 p-3 text-sm text-[#cbd5e1]">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-3 font-semibold text-[#eef5ff] marker:hidden">
                <span>Session details</span>
                <span className="text-xs font-normal text-[#9fb0c4]">Show mode</span>
              </summary>
              <div className="mt-3 grid gap-1 border-t border-white/10 pt-3 font-mono text-[11px] text-[#cbd5e1]">
                <span>mode: {snapshot.mode}</span>
                <span>repoRoot: {snapshot.repoRoot}</span>
                <span>generatedAt: {snapshot.generatedAt}</span>
              </div>
            </details>
          </div>

          <nav className="space-y-1.5" aria-label="Workbench sections">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = item.id === activeNav;
              return (
                <button
                  key={item.id}
                  data-nav-id={item.id}
                  className={`group flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left transition ${
                    active
                      ? "bg-[#284a73] text-white shadow-sm"
                      : "text-[#cbd5e1] hover:bg-white/8 hover:text-white"
                  }`}
                  type="button"
                  onClick={() => onNavigate(item.id)}
                >
                  <span
                    className={`grid h-9 w-9 shrink-0 place-items-center rounded-md border ${
                      active ? "border-white/15 bg-white/12" : "border-white/10 bg-[#11243b]"
                    }`}
                  >
                    <Icon className="h-4 w-4" aria-hidden="true" />
                  </span>
                  <span className="min-w-0">
                    <span className="block text-sm font-semibold">{item.label}</span>
                    <span className="block truncate text-xs text-[#9fb0c4]">{item.detail}</span>
                  </span>
                </button>
              );
            })}
          </nav>
          <div className="absolute bottom-4 left-4 right-4 hidden rounded-lg border border-white/10 bg-white/5 p-3 text-sm text-[#dbe6f3] lg:block">
            <div className="flex items-center justify-between gap-2">
              <div>
                <p className="font-semibold">Battle Engine Aquila</p>
                <p className="mt-1 text-xs text-[#9fb0c4]">{modeLabel}</p>
              </div>
              <Settings className="h-4 w-4 text-[#9fb0c4]" aria-hidden="true" />
            </div>
          </div>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col">
          <header className="border-b border-workbench-border bg-white/92 px-6 py-5 backdrop-blur">
            <div
              className={
                readerMode
                  ? "grid gap-4 2xl:grid-cols-[minmax(0,1fr)_minmax(20rem,0.55fr)] 2xl:items-start"
                  : "grid gap-4 2xl:grid-cols-[minmax(0,1fr)_minmax(20rem,0.55fr)] 2xl:items-start"
              }
            >
              <div>
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <StatusPill tone="neutral">{modeLabel}</StatusPill>
                  <StatusPill tone={snapshot.migration.status === "active" ? "good" : "warn"}>
                    {snapshot.migration.status === "active" ? "App ready" : snapshot.migration.status}
                  </StatusPill>
                </div>
                <h1 className="text-3xl font-semibold tracking-normal text-workbench-text">{pageTitle}</h1>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-workbench-muted">{pagePurpose}</p>
                <p className="mt-3 max-w-3xl text-sm font-medium text-workbench-text">Next: {nextAction}</p>
              </div>
              <div className="relative" data-testid="command-bar">
                <label className="flex min-h-11 items-center gap-3 rounded-lg border border-workbench-border bg-white px-3 shadow-sm">
                  <SearchCheck className="h-4 w-4 text-workbench-muted" aria-hidden="true" />
                  <span className="sr-only">Find a page or tool</span>
                  <input
                    className="min-w-0 flex-1 bg-transparent text-sm text-workbench-text outline-none placeholder:text-workbench-muted"
                    placeholder="Find a page or tool..."
                    value={commandQuery}
                    onChange={(event) => onCommandQueryChange(event.target.value)}
                  />
                </label>
                {commandResults.length > 0 ? (
                  <div className="absolute left-0 right-0 top-full z-30 mt-2 overflow-hidden rounded-lg border border-workbench-border bg-white shadow-panel">
                    {commandResults.map((result) => (
                      <button
                        key={result.id}
                        type="button"
                        className="flex w-full items-center justify-between gap-3 border-b border-workbench-border px-3 py-2 text-left text-sm text-workbench-text last:border-b-0 hover:bg-workbench-panel2"
                        onClick={() => {
                          onNavigate(result.navId);
                          onCommandQueryChange("");
                        }}
                      >
                        <span>
                          <span className="block font-semibold">{result.label}</span>
                          <span className="block text-xs text-workbench-muted">{result.detail}</span>
                        </span>
                        <StatusPill tone={result.kind === "job" ? "warn" : "good"}>{result.kind === "job" ? "Tool" : "Page"}</StatusPill>
                      </button>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          </header>

          <nav
            className="flex gap-2 overflow-x-auto border-b border-workbench-border bg-white px-4 py-3 lg:hidden"
            aria-label="Workbench sections"
          >
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = item.id === activeNav;
              return (
                <button
                  key={item.id}
                  data-nav-id={item.id}
                  className={`flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                    active
                      ? "bg-[#eaf1ff] text-[#2457c5] ring-1 ring-[#9db7f5]"
                      : "bg-transparent text-workbench-muted"
                  }`}
                  type="button"
                  onClick={() => onNavigate(item.id)}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  {item.shortLabel}
                </button>
              );
            })}
          </nav>

          <div className={readerMode ? "p-6" : "p-6"}>
            {children}
            {readerMode ? null : <div className="hidden">{aside}</div>}
          </div>
        </main>
      </div>
    </div>
  );
}
