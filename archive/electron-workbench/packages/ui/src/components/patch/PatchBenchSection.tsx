import { HardDrive, RotateCcw, Route, SearchCheck, ShieldCheck, Wrench } from "lucide-react";
import { DetailGrid, DetailTile, PageIntro, PageSection, StepCard } from "@/components/common/ProductPrimitives";
import { fileNameFromPath, safeSummary, shortHash } from "@/components/common/format";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";
import { StatusPill } from "@/components/StatusPill";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { PatchState, SpecimenVerificationSummary, WorkbenchJobRunSummary } from "@/types/onslaught-api";

interface PatchBenchSectionProps {
  specimen: SpecimenVerificationSummary | null;
  specimenPath: string;
  verifyBusy: boolean;
  verifyError: string | null;
  patchWorkflowSourcePath: string;
  patchIds: string;
  copiedExecutablePath: string;
  copiedExecutableBackupPath: string;
  patchWorkflowRun: WorkbenchJobRunSummary | null;
  patchWorkflowBusy: string | null;
  patchWorkflowError: string | null;
  onSpecimenPathChange: (value: string) => void;
  onPatchWorkflowSourcePathChange: (value: string) => void;
  onPatchIdsChange: (value: string) => void;
  onSelectExecutable: () => void | Promise<void>;
  onVerifyExecutable: () => void | Promise<void>;
  onRunPatchWorkflow: (definitionId: string, patchIdsOverride?: string) => void | Promise<void>;
}

export function PatchBenchSection({
  specimen,
  specimenPath,
  verifyBusy,
  verifyError,
  patchWorkflowSourcePath,
  patchIds,
  copiedExecutablePath,
  copiedExecutableBackupPath,
  patchWorkflowRun,
  patchWorkflowBusy,
  patchWorkflowError,
  onSpecimenPathChange,
  onPatchWorkflowSourcePathChange,
  onPatchIdsChange,
  onSelectExecutable,
  onVerifyExecutable,
  onRunPatchWorkflow
}: PatchBenchSectionProps) {
  const displayRows = specimen?.rows.filter((row) => /window|aspect|display|fullscreen/i.test(`${row.spec.title} ${row.spec.purpose ?? ""}`)).slice(0, 3) ?? [];
  const graphicsRows = specimen?.rows.filter((row) => /graphics|texture|intro|default|shadow/i.test(`${row.spec.title} ${row.spec.purpose ?? ""}`)).slice(0, 3) ?? [];
  const advancedRows = specimen?.rows.filter((row) => !displayRows.includes(row) && !graphicsRows.includes(row)).slice(0, 3) ?? [];
  const stableCount = specimen?.rows.filter((row) => row.spec.track === "Stable").length ?? 0;
  const selectedCount = patchIds === "all" ? specimen?.rows.length ?? 0 : stableCount;
  const sourcePath = patchWorkflowSourcePath || specimenPath || specimen?.selectedPath || "";
  const canApply = Boolean(copiedExecutablePath.trim()) && patchWorkflowBusy === null;

  return (
    <PageSection testId="patch-bench-page">
      <PageIntro
        eyebrow="Patch Bench"
        title="Apply safe patches to a copied executable"
        body="All changes are applied to a copy of your file. The original stays unchanged, and a backup is created before any write."
      />

      <div className="grid gap-5 xl:grid-cols-[minmax(0,0.86fr)_minmax(0,1fr)_minmax(0,0.86fr)]" data-testid="patch-workflow">
        <StepCard
          number={1}
          title="Choose and verify executable"
          body="Select the game executable, confirm it matches the supported retail specimen, then prepare a copy."
          active
          status={<StatusPill tone={specimen ? (specimen.counts.mismatch || specimen.counts.outOfRange ? "warn" : "good") : "warn"}>{specimen ? "Verified" : "Copy required"}</StatusPill>}
        >
          <div data-testid="specimen-verifier" className="grid gap-4">
            <label className="grid gap-2 text-sm text-workbench-muted">
              <span className="font-medium text-workbench-text">Executable</span>
              <input
                className="min-h-10 rounded-md border border-workbench-border bg-white px-3 text-sm text-workbench-text outline-none focus:border-[#9db7f5] focus:ring-2 focus:ring-[#dbe7ff]"
                placeholder="Choose BEA.exe"
                value={specimenPath}
                onChange={(event) => {
                  onSpecimenPathChange(event.target.value);
                  onPatchWorkflowSourcePathChange(event.target.value);
                }}
              />
            </label>
            <div className="grid gap-2">
              <PatchStatusRow label="File found" value={specimen ? "Verified" : "Not checked"} tone={specimen ? "good" : "warn"} />
              <PatchStatusRow label="Integrity" value={specimen?.isKnownRetailSteamHash ? "Known retail build" : specimen ? "Unmatched build" : "Pending"} tone={specimen?.isKnownRetailSteamHash ? "good" : specimen ? "warn" : "neutral"} />
              <PatchStatusRow label="Original file" value="Unchanged" tone="good" />
              <PatchStatusRow label="Copy target" value={copiedExecutablePath ? "Copy ready" : "Copy required"} tone={copiedExecutablePath ? "good" : "warn"} />
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => void onSelectExecutable()} disabled={verifyBusy}>
                <HardDrive className="h-4 w-4" aria-hidden="true" />
                Select BEA.exe
              </Button>
              <Button variant="secondary" onClick={() => void onVerifyExecutable()} disabled={verifyBusy || !specimenPath.trim()}>
                <SearchCheck className="h-4 w-4" aria-hidden="true" />
                Verify
              </Button>
              <Button onClick={() => void onRunPatchWorkflow("patch.prepareExecutableCopy")} disabled={patchWorkflowBusy !== null || !sourcePath.trim()}>
                <ShieldCheck className="h-4 w-4" aria-hidden="true" />
                Prepare copied executable
              </Button>
            </div>
            {verifyError ? <p className="rounded-md border border-[#fecdca] bg-[#fef3f2] p-3 text-sm text-[#b42318]">{verifyError}</p> : null}
            <DetailsDisclosure title="Executable details" summary="Show file hashes and paths">
              <DetailGrid>
                <DetailTile label="Selected file" value={fileNameFromPath(specimen?.selectedPath ?? sourcePath)} detail={safeSummary(specimen?.selectedPath ?? sourcePath)} />
                <DetailTile label="SHA-256" value={shortHash(specimen?.sha256)} />
                <DetailTile label="Patch catalog" value={specimen ? `${specimen.catalog.patchCount} patches` : "Not loaded"} />
              </DetailGrid>
            </DetailsDisclosure>
          </div>
        </StepCard>

        <StepCard
          number={2}
          title="Choose patches"
          body="Start with recommended display and graphics fixes. Advanced and experimental patches stay opt-in."
          status={<StatusPill tone={selectedCount > 0 ? "good" : "warn"}>{selectedCount || "No"} selected</StatusPill>}
        >
          <div className="mb-4 flex items-center justify-between gap-3 rounded-lg border border-workbench-border bg-workbench-panel2 p-3">
            <div>
              <p className="font-medium text-workbench-text">Recommended set</p>
              <p className="text-sm text-workbench-muted">Stable patches are selected by default.</p>
            </div>
            <select
              className="min-h-10 rounded-md border border-workbench-border bg-white px-3 text-sm"
              value={patchIds}
              onChange={(event) => onPatchIdsChange(event.target.value)}
            >
              <option value="stable">Recommended</option>
              <option value="all">Include experimental</option>
            </select>
          </div>
          <PatchGroup title="Display Fixes" rows={displayRows} fallback={["Force windowed startup", "Widescreen display flow"]} />
          <PatchGroup title="Graphics & Defaults" rows={graphicsRows} fallback={["Skip startup movie", "Safer graphics defaults"]} />
          <PatchGroup title="Advanced" rows={advancedRows} fallback={["Optional diagnostics", "Memory/compatibility helpers"]} />
          <DetailsDisclosure className="mt-3" title="Technical patch details" summary="Show offsets and byte checks">
            <div className="grid gap-2 text-xs text-workbench-muted">
              {(specimen?.rows ?? []).slice(0, 12).map((row) => (
                <p key={row.spec.id}>
                  {row.spec.title}: {row.spec.fileOffsetHex} / {row.currentBytesHex ?? "not read"}
                </p>
              ))}
            </div>
          </DetailsDisclosure>
        </StepCard>

        <StepCard
          number={3}
          title="Review and apply to copy"
          body="Confirm the copy target, backup, and selected patch set before applying."
          status={<StatusPill tone={canApply ? "good" : "warn"}>{canApply ? "Ready" : "Waiting"}</StatusPill>}
        >
          <div className="grid gap-3">
            <ReviewRow label="Source file" value={fileNameFromPath(sourcePath)} detail="Original stays unchanged." />
            <ReviewRow label="Copy target" value={copiedExecutablePath ? fileNameFromPath(copiedExecutablePath) : "Copy required"} detail={copiedExecutablePath ? safeSummary(copiedExecutablePath) : "Prepare a copied executable first."} />
            <ReviewRow label="Backup" value={copiedExecutableBackupPath ? "Backup available" : "Created before write"} detail={copiedExecutableBackupPath ? safeSummary(copiedExecutableBackupPath) : "Onslaught keeps restore data beside the copy."} />
            <ReviewRow label="Selected patches" value={`${selectedCount} patches`} detail={patchIds === "all" ? "Includes experimental rows." : "Recommended rows only."} />
            <ReviewRow label="Safety status" value="Original safe" detail="Patches apply only to the copied executable." />
          </div>
          <div className="mt-4 grid gap-2">
            <Button onClick={() => void onRunPatchWorkflow("patch.planCatalogPatch")} disabled={patchWorkflowBusy !== null || !copiedExecutablePath.trim()}>
              <Route className="h-4 w-4" aria-hidden="true" />
              Preview plan
            </Button>
            <Button onClick={() => void onRunPatchWorkflow("patch.applyCatalogPatch")} disabled={!canApply}>
              <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              Apply to Copied Executable
            </Button>
            <Button variant="secondary" onClick={() => void onRunPatchWorkflow("patch.restoreCatalogBackup")} disabled={patchWorkflowBusy !== null || !copiedExecutablePath.trim() || !copiedExecutableBackupPath.trim()}>
              <RotateCcw className="h-4 w-4" aria-hidden="true" />
              Restore backup
            </Button>
          </div>
          {patchWorkflowError ? <p className="mt-3 rounded-md border border-[#fecdca] bg-[#fef3f2] p-3 text-sm text-[#b42318]">{patchWorkflowError}</p> : null}
          {patchWorkflowRun ? (
            <div className="mt-4 rounded-lg border border-workbench-border bg-workbench-panel2 p-4">
              <p className="font-semibold text-workbench-text">{patchWorkflowRun.title}</p>
              <p className="mt-1 text-sm leading-6 text-workbench-muted">{patchWorkflowRun.result.summary}</p>
              <DetailsDisclosure className="mt-3" title="Detailed log" summary="Show run details">
                {patchWorkflowRun.result.details.map((detail) => (
                  <p key={detail.label} className="text-xs text-workbench-muted">
                    {detail.label}: {detail.value}
                  </p>
                ))}
              </DetailsDisclosure>
            </div>
          ) : null}
        </StepCard>
      </div>
    </PageSection>
  );
}

function PatchStatusRow({ label, value, tone }: { label: string; value: string; tone: "good" | "warn" | "neutral" }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-md border border-workbench-border bg-workbench-panel2 p-3 text-sm">
      <span className="text-workbench-muted">{label}</span>
      <StatusPill tone={tone}>{value}</StatusPill>
    </div>
  );
}

function PatchGroup({
  title,
  rows,
  fallback
}: {
  title: string;
  rows: SpecimenVerificationSummary["rows"];
  fallback: string[];
}) {
  const visibleRows = rows.length
    ? rows
    : fallback.map((title, index) => ({
        spec: { id: `${title}-${index}`, title, track: "Stable", optional: false, fileOffset: 0, fileOffsetHex: "", byteLength: 0, purpose: "Recommended compatibility improvement." },
        state: "original" as PatchState,
        stateLabel: "Ready",
        tone: "ready" as const
      }));
  return (
    <div className="mt-3 rounded-lg border border-workbench-border bg-white p-3">
      <div className="mb-2 flex items-center justify-between gap-2">
        <h4 className="font-semibold text-workbench-text">{title}</h4>
        <StatusPill tone="good">Recommended</StatusPill>
      </div>
      <div className="grid gap-2">
        {visibleRows.map((row) => (
          <div key={row.spec.id} className="flex items-start gap-3 rounded-md bg-workbench-panel2 p-3">
            <input type="checkbox" checked readOnly className="mt-1 h-4 w-4 accent-[#2457c5]" />
            <div className="min-w-0 flex-1">
              <p className="font-medium text-workbench-text">{row.spec.title}</p>
              <p className="mt-1 text-sm leading-5 text-workbench-muted">{row.spec.purpose ?? "Curated compatibility patch."}</p>
            </div>
            <StatusPill tone={row.state === "patched" ? "good" : "neutral"}>{row.state === "patched" ? "Applied" : "Safe"}</StatusPill>
          </div>
        ))}
      </div>
    </div>
  );
}

function ReviewRow({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-md border border-workbench-border bg-workbench-panel2 p-3">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-workbench-muted">{label}</p>
        <p className="text-sm font-semibold text-workbench-text">{value}</p>
      </div>
      <p className="mt-1 text-xs leading-5 text-workbench-muted">{detail}</p>
    </div>
  );
}
