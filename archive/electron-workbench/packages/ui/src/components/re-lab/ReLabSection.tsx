import { useMemo, useState } from "react";
import { Boxes, Code2, FileText, Image as ImageIcon, Search, Share2 } from "lucide-react";
import { EmptyState, MetricCard, PageIntro, PageSection } from "@/components/common/ProductPrimitives";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";
import { StatusPill } from "@/components/StatusPill";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type {
  DebugReadinessSummary,
  GameHarnessProfileSummary,
  GhidraReadinessSummary,
  WorkbenchJobCatalogSummary,
  WorkbenchJobDefinition
} from "@/types/onslaught-api";

interface ReLabSectionProps {
  ghidraReadiness: GhidraReadinessSummary | null;
  debugReadiness: DebugReadinessSummary | null;
  gameHarnessProfile: GameHarnessProfileSummary | null;
  jobCatalog: WorkbenchJobCatalogSummary | null;
  visibleJobDefinitions: WorkbenchJobDefinition[];
  showParityDiagnostics: boolean;
  parityDiagnosticCount: number;
  readinessBusy: boolean;
  readinessError: string | null;
  onRefreshReadiness: () => void | Promise<void>;
  onShowParityDiagnosticsChange: (value: boolean) => void;
  onRunWorkbenchJob: (job: WorkbenchJobDefinition) => void | Promise<void>;
}

const exampleResults = [
  {
    icon: ImageIcon,
    name: "T_Hawk_Wings_01_D",
    type: "Texture",
    category: "Textures",
    source: "Texture exports",
    sourceLabel: "Sample texture reference",
    body: "Diffuse map for Hawk asset wings.",
    refs: "12 refs"
  },
  {
    icon: Boxes,
    name: "SM_Ancient_Statue",
    type: "Model",
    category: "Models",
    source: "All game archives",
    sourceLabel: "Sample model reference",
    body: "Static mesh with material and texture references.",
    refs: "8 refs"
  },
  {
    icon: Code2,
    name: "RenderHawkWings",
    type: "Function",
    category: "Functions",
    source: "Function symbols",
    sourceLabel: "Sample function reference",
    body: "Renderer path connected to wing material setup.",
    refs: "24 xrefs"
  },
  {
    icon: FileText,
    name: "STR_HAWK_WING_DEPLOY",
    type: "String",
    category: "Strings",
    source: "All game archives",
    sourceLabel: "Sample string reference",
    body: "Localized UI string for Hawk wing deployment.",
    refs: "3 uses"
  }
];

export function ReLabSection({
  ghidraReadiness,
  debugReadiness,
  gameHarnessProfile,
  jobCatalog,
  visibleJobDefinitions,
  showParityDiagnostics,
  parityDiagnosticCount,
  readinessBusy,
  readinessError,
  onRefreshReadiness,
  onShowParityDiagnosticsChange,
  onRunWorkbenchJob
}: ReLabSectionProps) {
  const firstReadOnlyJob = visibleJobDefinitions.find((job) => job.safety === "read-only" && job.status === "available") ?? null;
  const [query, setQuery] = useState("");
  const [sourceFilter, setSourceFilter] = useState("All game archives");
  const [typeFilter, setTypeFilter] = useState("Textures");
  const [selectedName, setSelectedName] = useState(exampleResults[0].name);
  const [planCreated, setPlanCreated] = useState(false);
  const filteredResults = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const rows = exampleResults.filter((result) => {
      const sourceMatches = sourceFilter === "All game archives" || result.source === sourceFilter;
      const typeMatches = result.category === typeFilter;
      const textMatches =
        !normalizedQuery ||
        result.name.toLowerCase().includes(normalizedQuery) ||
        result.body.toLowerCase().includes(normalizedQuery) ||
        result.type.toLowerCase().includes(normalizedQuery);
      return sourceMatches && typeMatches && textMatches;
    });
    return rows.length > 0 ? rows : exampleResults.filter((result) => result.category === typeFilter);
  }, [query, sourceFilter, typeFilter]);
  const selectedResult = filteredResults.find((result) => result.name === selectedName) ?? filteredResults[0] ?? exampleResults[0];

  return (
    <PageSection testId="section-re-lab">
      <PageIntro
        eyebrow="RE Lab"
        title="Explore assets, functions, and structures"
        body="Search and inspect game data to understand how Battle Engine Aquila works. Ask Onslaught for a bounded plan before running deeper tools."
        action={
          <>
            <Button variant="secondary" onClick={() => void onRefreshReadiness()} disabled={readinessBusy}>
              <Search className="h-4 w-4" aria-hidden="true" />
              {readinessBusy ? "Checking..." : "Check tools"}
            </Button>
            <Button disabled={!firstReadOnlyJob} onClick={() => firstReadOnlyJob && void onRunWorkbenchJob(firstReadOnlyJob)}>
              <Share2 className="h-4 w-4" aria-hidden="true" />
              Run safe tool
            </Button>
          </>
        }
      />

      {readinessError ? <div className="rounded-lg border border-[#fecdca] bg-[#fef3f2] p-4 text-sm text-[#b42318]">{readinessError}</div> : null}

      <div className="grid gap-5 xl:grid-cols-[18rem_minmax(0,1fr)_26rem]">
        <Card data-testid="re-filters" className="self-start">
          <h3 className="text-lg font-semibold text-workbench-text">Source and type filters</h3>
          <div className="mt-4 grid gap-4">
            <label className="grid gap-2 text-sm">
              <span className="font-medium text-workbench-text">Data source</span>
              <select
                className="min-h-10 rounded-md border border-workbench-border bg-white px-3 text-workbench-text"
                value={sourceFilter}
                onChange={(event) => {
                  setSourceFilter(event.target.value);
                  setPlanCreated(false);
                }}
              >
                <option>All game archives</option>
                <option>Texture exports</option>
                <option>Function symbols</option>
              </select>
            </label>
            <div className="grid gap-2">
              {[
                ["Textures", "2,134"],
                ["Models", "612"],
                ["Strings", "4,892"],
                ["Functions", "3,421"],
                ["Structures", "798"]
              ].map(([label, count], index) => (
                <button
                  key={label}
                  className={`flex items-center justify-between rounded-md border px-3 py-2 text-sm ${
                    typeFilter === label ? "border-[#9db7f5] bg-[#eaf1ff] text-[#2457c5]" : "border-workbench-border bg-white text-workbench-muted"
                  }`}
                  type="button"
                  onClick={() => {
                    setTypeFilter(label);
                    setPlanCreated(false);
                  }}
                >
                  <span>{label}</span>
                  <span>{count}</span>
                </button>
              ))}
            </div>
          </div>
          <DetailsDisclosure className="mt-4" title="Maintainer tool catalog" summary="Show available tool details">
            <div data-testid="job-catalog" className="grid gap-2 text-sm">
              <p>{jobCatalog ? `${jobCatalog.counts.available} safe tools available` : "Tool list loading"}</p>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showParityDiagnostics}
                  onChange={(event) => onShowParityDiagnosticsChange(event.target.checked)}
                />
                Include parity diagnostics ({parityDiagnosticCount})
              </label>
              {visibleJobDefinitions.slice(0, 8).map((job) => (
                <p key={job.id} className="text-xs text-workbench-muted">
                  {job.title} - {job.status}
                </p>
              ))}
            </div>
          </DetailsDisclosure>
        </Card>

        <main className="grid gap-4">
          <Card>
            <label className="flex min-h-12 items-center gap-3 rounded-md border border-[#9db7f5] bg-white px-3 shadow-sm">
              <Search className="h-5 w-5 text-workbench-muted" aria-hidden="true" />
              <span className="sr-only">Search RE Lab</span>
              <input
                data-testid="re-search"
                className="min-w-0 flex-1 bg-transparent text-sm text-workbench-text outline-none placeholder:text-workbench-muted"
                placeholder="Search textures, models, strings, functions, symbols..."
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setPlanCreated(false);
                }}
              />
            </label>
          </Card>

          <Card data-testid="re-lab-data-honesty" className="border-[#fedf89] bg-[#fffbeb]">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-workbench-text">Example investigation</h3>
                <p className="mt-1 text-sm leading-6 text-workbench-muted">
                  The rows below show the shape of an investigation. They are sample data, not live extracted game results.
                </p>
              </div>
              <StatusPill tone="warn">Sample query</StatusPill>
            </div>
          </Card>

          <Card data-testid="re-results">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-workbench-text">Example results</h3>
                <p className="mt-1 text-sm text-workbench-muted">Select a sample row to inspect how references and bounded tasks will be reviewed.</p>
              </div>
              <StatusPill tone="warn">Example investigation</StatusPill>
            </div>
            <div className="grid gap-3">
              {filteredResults.map((result) => {
                const Icon = result.icon;
                const selected = selectedResult.name === result.name;
                return (
                  <button
                    key={result.name}
                    type="button"
                    data-testid="re-result-row"
                    className={`grid gap-3 rounded-lg border p-3 text-left transition md:grid-cols-[4.5rem_minmax(0,1fr)_auto] ${
                      selected ? "border-[#9db7f5] bg-[#eaf1ff]" : "border-workbench-border bg-white hover:border-[#9db7f5]"
                    }`}
                    onClick={() => {
                      setSelectedName(result.name);
                      setPlanCreated(false);
                    }}
                  >
                    <div className="grid h-16 w-16 place-items-center rounded-lg bg-white text-[#2457c5]">
                      <Icon className="h-7 w-7" aria-hidden="true" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-semibold text-workbench-text">{result.name}</p>
                        <StatusPill tone="neutral">{result.type}</StatusPill>
                      </div>
                      <p className="mt-1 text-sm text-workbench-muted">{result.sourceLabel}</p>
                      <p className="mt-1 text-sm leading-6 text-workbench-muted">{result.body}</p>
                    </div>
                    <p className="text-sm font-semibold text-[#2457c5]">{result.refs}</p>
                  </button>
                );
              })}
            </div>
          </Card>
        </main>

        <aside className="grid gap-4 self-start">
          <Card data-testid="re-inspector">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-workbench-text">Inspector</h3>
                <p className="mt-1 text-sm text-workbench-muted">Selected item details and references.</p>
              </div>
              <StatusPill tone="neutral">Texture</StatusPill>
            </div>
            <div className="rounded-lg border border-workbench-border bg-workbench-panel2 p-4">
              <p className="font-semibold text-workbench-text">{selectedResult.name}</p>
              <p className="mt-2 text-sm leading-6 text-workbench-muted">{selectedResult.body}</p>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-1">
              <MetricCard label="References" value={selectedResult.refs.replace(/\s.*/, "")} detail={selectedResult.sourceLabel} tone="good" />
              <MetricCard label="Preview" value={gameHarnessProfile?.ready ? "Available" : "Needs folder"} detail="Connect game folder for live file previews" tone={gameHarnessProfile?.ready ? "good" : "warn"} />
            </div>
          </Card>

          <Card data-testid="ask-agent-panel">
            <h3 className="text-lg font-semibold text-workbench-text">Ask the agent</h3>
            <p className="mt-2 rounded-lg bg-[#eaf1ff] p-3 text-sm text-[#2457c5]">
              Example objective: understand references for {selectedResult.name}
            </p>
            <p className="mt-4 text-sm font-semibold text-workbench-text">What this panel can do</p>
            <ul className="mt-2 grid gap-2 text-sm text-workbench-muted">
              <li>Create a bounded plan</li>
              <li>Run safe read-only tools</li>
              <li>Export a summary</li>
            </ul>
            <p className="mt-3 text-sm leading-6 text-workbench-muted">
              This does not start uncontrolled automation. Deeper planning stays bounded and reviewable.
            </p>
            {planCreated ? (
              <div data-testid="re-plan-created" className="mt-3 rounded-lg border border-[#b8d8bf] bg-[#edf8ef] p-3 text-sm leading-6 text-[#295b34]">
                Bounded plan ready for review. Next step: run a safe read-only tool or export the summary.
              </div>
            ) : null}
            <div className="mt-4 flex gap-2">
              <Button disabled={!firstReadOnlyJob} onClick={() => firstReadOnlyJob && void onRunWorkbenchJob(firstReadOnlyJob)}>
                Run safe tool
              </Button>
              <Button data-testid="create-bounded-plan" variant="secondary" onClick={() => setPlanCreated(true)}>
                Create bounded plan
              </Button>
            </div>
          </Card>

          {!jobCatalog ? <EmptyState icon={Search} title="Tool list loading." body="Readiness checks populate safe maintainer tools without giving the renderer direct shell access." /> : null}
          <div className="hidden">
            {ghidraReadiness ? ghidraReadiness.ready ? "Ghidra ready" : "Ghidra check" : null}
            {debugReadiness ? debugReadiness.ready ? "Debugger ready" : "Debugger check" : null}
          </div>
        </aside>
      </div>
    </PageSection>
  );
}
