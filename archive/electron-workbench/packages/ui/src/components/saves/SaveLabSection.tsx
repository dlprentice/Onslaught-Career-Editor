import { FileSearch, HardDrive, MonitorPlay, RotateCcw, Save, SearchCheck, ShieldCheck, Wrench } from "lucide-react";
import { DetailGrid, DetailTile, EmptyState, MetricCard, PageIntro, PageSection } from "@/components/common/ProductPrimitives";
import { fileNameFromPath, safeSummary, shortHash } from "@/components/common/format";
import { DetailsDisclosure } from "@/components/DetailsDisclosure";
import { StatusPill } from "@/components/StatusPill";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { SaveInspectionSummary, WorkbenchJobRunSummary } from "@/types/onslaught-api";

type GoodieStateFilter = "all" | "unlocked" | "locked" | "new" | "old" | "instructions";

interface SaveLabSectionProps {
  saveInspection: SaveInspectionSummary | null;
  savePath: string;
  goodieQuery: string;
  goodieStateFilter: GoodieStateFilter;
  visibleGoodieRows: SaveInspectionSummary["goodieRows"];
  inspectBusy: boolean;
  inspectError: string | null;
  copiedSavePath: string;
  copiedSaveBackupPath: string;
  savePatchRun: WorkbenchJobRunSummary | null;
  savePatchBusy: string | null;
  savePatchError: string | null;
  optionsSoundVolumeEnabled: boolean;
  optionsSoundVolume: string;
  optionsMusicVolumeEnabled: boolean;
  optionsMusicVolume: string;
  optionsScreenShapeEnabled: boolean;
  optionsScreenShape: string;
  optionsD3dDeviceEnabled: boolean;
  optionsD3dDeviceIndex: string;
  optionsCopyFromPath: string;
  optionsCopyEntries: boolean;
  optionsPatchRun: WorkbenchJobRunSummary | null;
  optionsPatchBusy: string | null;
  optionsPatchError: string | null;
  onSavePathChange: (value: string) => void;
  onGoodieQueryChange: (value: string) => void;
  onGoodieStateFilterChange: (value: GoodieStateFilter) => void;
  onBrowseSave: () => void | Promise<void>;
  onInspectSave: () => void | Promise<void>;
  onOpenGoodieMedia: (row: SaveInspectionSummary["goodieRows"][number]) => void | Promise<void>;
  onRunSavePatchWorkflow: (definitionId: string) => void | Promise<void>;
  onRunOptionsPatchWorkflow: (definitionId: string) => void | Promise<void>;
  onOptionsSoundVolumeEnabledChange: (value: boolean) => void;
  onOptionsSoundVolumeChange: (value: string) => void;
  onOptionsMusicVolumeEnabledChange: (value: boolean) => void;
  onOptionsMusicVolumeChange: (value: string) => void;
  onOptionsScreenShapeEnabledChange: (value: boolean) => void;
  onOptionsScreenShapeChange: (value: string) => void;
  onOptionsD3dDeviceEnabledChange: (value: boolean) => void;
  onOptionsD3dDeviceIndexChange: (value: string) => void;
  onOptionsCopyFromPathChange: (value: string) => void;
  onOptionsCopyEntriesChange: (value: boolean) => void;
}

export function SaveLabSection({
  saveInspection,
  savePath,
  goodieQuery,
  goodieStateFilter,
  visibleGoodieRows,
  inspectBusy,
  inspectError,
  copiedSavePath,
  copiedSaveBackupPath,
  savePatchRun,
  savePatchBusy,
  savePatchError,
  optionsSoundVolumeEnabled,
  optionsSoundVolume,
  optionsMusicVolumeEnabled,
  optionsMusicVolume,
  optionsScreenShapeEnabled,
  optionsScreenShape,
  optionsD3dDeviceEnabled,
  optionsD3dDeviceIndex,
  optionsCopyFromPath,
  optionsCopyEntries,
  optionsPatchRun,
  optionsPatchBusy,
  optionsPatchError,
  onSavePathChange,
  onGoodieQueryChange,
  onGoodieStateFilterChange,
  onBrowseSave,
  onInspectSave,
  onOpenGoodieMedia,
  onRunSavePatchWorkflow,
  onRunOptionsPatchWorkflow,
  onOptionsSoundVolumeEnabledChange,
  onOptionsSoundVolumeChange,
  onOptionsMusicVolumeEnabledChange,
  onOptionsMusicVolumeChange,
  onOptionsScreenShapeEnabledChange,
  onOptionsScreenShapeChange,
  onOptionsD3dDeviceEnabledChange,
  onOptionsD3dDeviceIndexChange,
  onOptionsCopyFromPathChange,
  onOptionsCopyEntriesChange
}: SaveLabSectionProps) {
  const totalGoodies = saveInspection ? saveInspection.goodies.displayableUnlocked + saveInspection.goodies.locked : 233;
  const completion =
    saveInspection && saveInspection.counts.completedNodes + saveInspection.counts.partialNodes > 0
      ? Math.round((saveInspection.counts.completedNodes / (saveInspection.counts.completedNodes + saveInspection.counts.partialNodes)) * 100)
      : null;
  const selectedGoodie = visibleGoodieRows[0] ?? null;

  return (
    <PageSection testId="save-lab-page">
      <PageIntro
        eyebrow="Save Lab"
        title="Inspect and edit a save safely"
        body="Open a real save or options file, inspect what it contains, then save changes to a copy. The original file stays unchanged."
        action={
          <>
            <Button variant="secondary" onClick={() => void onBrowseSave()} disabled={inspectBusy}>
              <HardDrive className="h-4 w-4" aria-hidden="true" />
              Open save
            </Button>
            <Button onClick={() => void onInspectSave()} disabled={inspectBusy || !savePath.trim()} data-testid="inspect-save-button">
              <FileSearch className="h-4 w-4" aria-hidden="true" />
              {inspectBusy ? "Inspecting..." : "Inspect file"}
            </Button>
          </>
        }
      />

      <Card data-testid="save-inspector" className="p-0">
        <div className="grid gap-0 divide-y divide-workbench-border lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)_auto] lg:divide-x lg:divide-y-0">
          <div className="p-5">
            <p className="text-sm font-semibold text-workbench-text">{fileNameFromPath(savePath, "No save selected")}</p>
            <p className="mt-1 text-sm text-workbench-muted">
              {saveInspection ? (saveInspection.isOptionsFile ? "Options profile" : "Career save") : "Choose a file to inspect"}
            </p>
            <label className="mt-4 block" htmlFor="save-path-input">
              <span className="sr-only">Save or options file path</span>
              <input
                id="save-path-input"
                data-testid="save-path-input"
                className="min-h-10 w-full rounded-md border border-workbench-border bg-white px-3 text-sm text-workbench-text outline-none transition placeholder:text-workbench-muted focus:border-[#9db7f5] focus:ring-2 focus:ring-[#dbe7ff]"
                placeholder="Choose a .bes, .bea, or defaultoptions.bea file"
                value={savePath}
                onChange={(event) => onSavePathChange(event.target.value)}
              />
            </label>
          </div>
          <div className="p-5">
            <p className="text-sm font-medium text-workbench-muted">Validation status</p>
            <p className="mt-2">
              <StatusPill tone={saveInspection ? (saveInspection.isValid ? "good" : "danger") : "warn"}>
                {saveInspection ? (saveInspection.isValid ? "All checks passed" : "Needs attention") : "Not inspected"}
              </StatusPill>
            </p>
            <p className="mt-3 text-sm text-workbench-muted">
              {completion === null ? "Open a file to see campaign and options summaries." : `${completion}% campaign progression in inspected data.`}
            </p>
          </div>
          <div className="flex flex-wrap gap-2 p-5 lg:items-center">
            <Button variant="secondary" onClick={() => void onRunSavePatchWorkflow("save.prepareCopy")} disabled={savePatchBusy !== null || !savePath.trim()}>
              <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              Create Safe Copy
            </Button>
          </div>
        </div>
      </Card>

      {inspectError ? <div className="rounded-lg border border-[#fecdca] bg-[#fef3f2] p-4 text-sm text-[#b42318]">{inspectError}</div> : null}

      {saveInspection ? (
        <div className="grid gap-5 xl:grid-cols-[18rem_minmax(0,1fr)_24rem]">
          <aside className="grid gap-3">
            <MetricCard label="Current Rank" value={saveInspection.rankDistribution[0]?.rank ?? "Not ranked"} detail={`${saveInspection.rankDistribution[0]?.count ?? 0} missions at top rank`} tone="good" />
            <MetricCard label="Worlds Unlocked" value={`${saveInspection.counts.completedLinks}/${saveInspection.counts.totalLinks}`} detail="Campaign links completed" tone="good" />
            <MetricCard label="Goodies Collected" value={`${saveInspection.goodies.displayableUnlocked}/${totalGoodies}`} detail={`${saveInspection.goodies.new + saveInspection.goodies.old} unlocked entries`} tone="warn" />
            <MetricCard label="Loadout Slots" value={`${saveInspection.counts.activeTechSlots}/${saveInspection.counts.totalTechSlots}`} detail="Active technology slots" tone="neutral" />
            <MetricCard label="Backup Status" value={copiedSaveBackupPath ? "Ready" : "Pending"} detail={copiedSavePath ? safeSummary(copiedSavePath) : "Create a safe copy before writing."} tone={copiedSaveBackupPath ? "good" : "warn"} />
          </aside>

          <Card data-testid="goodie-grid">
            <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <h3 className="text-lg font-semibold text-workbench-text">Campaign and collected items</h3>
                <p className="mt-1 text-sm text-workbench-muted">Search collected items and jump to related media without exposing save internals.</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <label className="min-w-56">
                  <span className="sr-only">Find item</span>
                  <input
                    data-testid="goodie-search"
                    className="min-h-10 w-full rounded-md border border-workbench-border bg-white px-3 text-sm outline-none focus:border-[#9db7f5] focus:ring-2 focus:ring-[#dbe7ff]"
                    placeholder="Find item, vehicle, or mission"
                    value={goodieQuery}
                    onChange={(event) => onGoodieQueryChange(event.target.value)}
                  />
                </label>
                <select
                  data-testid="goodie-state-filter"
                  className="min-h-10 rounded-md border border-workbench-border bg-white px-3 text-sm text-workbench-text"
                  value={goodieStateFilter}
                  onChange={(event) => onGoodieStateFilterChange(event.target.value as GoodieStateFilter)}
                >
                  <option value="all">All states</option>
                  <option value="unlocked">Unlocked</option>
                  <option value="new">New</option>
                  <option value="old">Old</option>
                  <option value="instructions">Instructions</option>
                  <option value="locked">Locked</option>
                </select>
              </div>
            </div>

            <div className="grid max-h-[34rem] gap-3 overflow-auto pr-1">
              {visibleGoodieRows.slice(0, 18).map((row) => (
                <div key={`${row.index}-${row.fileOffsetHex}`} className="grid gap-3 rounded-lg border border-workbench-border bg-workbench-panel2 p-3 md:grid-cols-[minmax(0,1fr)_auto]">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-semibold text-workbench-text">{row.title}</p>
                      <StatusPill tone={row.stateGroup === "new" || row.stateGroup === "old" ? "good" : row.stateGroup === "instructions" ? "warn" : "neutral"}>
                        {row.stateLabel}
                      </StatusPill>
                    </div>
                    <p className="mt-1 text-sm leading-6 text-workbench-muted">{row.unlockHint}</p>
                    <p className="mt-1 text-xs text-workbench-muted">{row.contentType}</p>
                  </div>
                  <Button variant="secondary" size="sm" data-testid="goodie-media-lookup" onClick={() => void onOpenGoodieMedia(row)}>
                    <MonitorPlay className="h-3.5 w-3.5" aria-hidden="true" />
                    Find media
                  </Button>
                </div>
              ))}
            </div>

            <DetailsDisclosure className="mt-4" title="Save file details" summary="Show offsets and hashes">
              <DetailGrid>
                <DetailTile label="File" value={saveInspection.fileName} detail={safeSummary(saveInspection.selectedPath)} />
                <DetailTile label="Version" value={saveInspection.versionWordHex} detail={saveInspection.versionValid ? "Version accepted" : "Unexpected version"} />
                <DetailTile label="File size" value={`${saveInspection.fileSize.toLocaleString()} bytes`} />
                <DetailTile label="SHA-256" value={shortHash(saveInspection.sha256)} />
              </DetailGrid>
            </DetailsDisclosure>
          </Card>

          <Card data-testid="save-selected-detail">
            <h3 className="text-lg font-semibold text-workbench-text">Selected detail</h3>
            {selectedGoodie ? (
              <div className="mt-4 grid gap-4">
                <div className="rounded-lg border border-workbench-border bg-workbench-panel2 p-4">
                  <p className="font-semibold text-workbench-text">{selectedGoodie.title}</p>
                  <p className="mt-2 text-sm leading-6 text-workbench-muted">{selectedGoodie.unlockHint}</p>
                  <p className="mt-2 text-sm text-workbench-muted">State: {selectedGoodie.stateLabel}</p>
                </div>
                <Button variant="secondary" onClick={() => void onOpenGoodieMedia(selectedGoodie)}>
                  <MonitorPlay className="h-4 w-4" aria-hidden="true" />
                  Find related media
                </Button>
              </div>
            ) : (
              <EmptyState icon={FileSearch} title="Choose an item to edit." body="Select an item from the campaign list to inspect or find related media." />
            )}
          </Card>
        </div>
      ) : (
        <EmptyState icon={FileSearch} title="Choose a save or options file." body="Open a real baseline file first. Onslaught reads it, summarizes it, and keeps the original unchanged." />
      )}

      <Card data-testid="options-patch-workflow">
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <div>
            <h3 className="text-lg font-semibold text-workbench-text">Safe edit controls</h3>
            <p className="mt-1 text-sm leading-6 text-workbench-muted">Choose a few common settings. More byte-level save fields stay in details and parity tools.</p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <OptionControl label="Sound volume" enabled={optionsSoundVolumeEnabled} value={optionsSoundVolume} onEnabledChange={onOptionsSoundVolumeEnabledChange} onValueChange={onOptionsSoundVolumeChange} />
              <OptionControl label="Music volume" enabled={optionsMusicVolumeEnabled} value={optionsMusicVolume} onEnabledChange={onOptionsMusicVolumeEnabledChange} onValueChange={onOptionsMusicVolumeChange} />
              <OptionControl label="Screen shape" enabled={optionsScreenShapeEnabled} value={optionsScreenShape} testId="options-screen-shape" onEnabledChange={onOptionsScreenShapeEnabledChange} onValueChange={onOptionsScreenShapeChange} />
              <OptionControl label="Display device" enabled={optionsD3dDeviceEnabled} value={optionsD3dDeviceIndex} testId="options-d3d-device" onEnabledChange={onOptionsD3dDeviceEnabledChange} onValueChange={onOptionsD3dDeviceIndexChange} />
            </div>
            <label className="mt-4 grid gap-2 text-sm text-workbench-muted">
              <span className="font-medium text-workbench-text">Copy settings from another file</span>
              <input
                data-testid="options-copy-from-path"
                className="min-h-10 rounded-md border border-workbench-border bg-white px-3 text-sm text-workbench-text outline-none focus:border-[#9db7f5] focus:ring-2 focus:ring-[#dbe7ff]"
                placeholder="Optional source file"
                value={optionsCopyFromPath}
                onChange={(event) => onOptionsCopyFromPathChange(event.target.value)}
              />
            </label>
            <label className="mt-3 flex items-center gap-2 text-sm text-workbench-text">
              <input
                data-testid="options-copy-entries"
                type="checkbox"
                checked={optionsCopyEntries}
                onChange={(event) => onOptionsCopyEntriesChange(event.target.checked)}
                className="h-4 w-4 accent-[#2457c5]"
              />
              Copy controller and display entries
            </label>
          </div>
          <div className="rounded-lg border border-workbench-border bg-workbench-panel2 p-4">
            <h4 className="font-semibold text-workbench-text">Save actions</h4>
            <p className="mt-1 text-sm leading-6 text-workbench-muted">Preview changes before applying them to the copied file.</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => void onRunSavePatchWorkflow("save.previewPatch")} disabled={savePatchBusy !== null || !copiedSavePath.trim()}>
                <SearchCheck className="h-4 w-4" aria-hidden="true" />
                Preview changes
              </Button>
              <Button onClick={() => void onRunSavePatchWorkflow("save.applyPatch")} disabled={savePatchBusy !== null || !copiedSavePath.trim()}>
                <Save className="h-4 w-4" aria-hidden="true" />
                Save copy
              </Button>
              <Button variant="secondary" onClick={() => void onRunSavePatchWorkflow("save.restoreBackup")} disabled={savePatchBusy !== null || !copiedSavePath.trim() || !copiedSaveBackupPath.trim()}>
                <RotateCcw className="h-4 w-4" aria-hidden="true" />
                Restore backup
              </Button>
              <Button variant="secondary" onClick={() => void onRunOptionsPatchWorkflow("settings.applyOptionsPatch")} disabled={optionsPatchBusy !== null}>
                <Wrench className="h-4 w-4" aria-hidden="true" />
                Apply options to copy
              </Button>
            </div>
            {savePatchError || optionsPatchError ? (
              <p className="mt-3 rounded-md border border-[#fecdca] bg-[#fef3f2] p-3 text-sm text-[#b42318]">{savePatchError ?? optionsPatchError}</p>
            ) : null}
            {savePatchRun || optionsPatchRun ? (
              <div className="mt-4 rounded-lg border border-workbench-border bg-white p-4">
                <p className="font-semibold text-workbench-text">{savePatchRun?.title ?? optionsPatchRun?.title}</p>
                <p className="mt-1 text-sm leading-6 text-workbench-muted">{savePatchRun?.result.summary ?? optionsPatchRun?.result.summary}</p>
              </div>
            ) : null}
          </div>
        </div>
      </Card>
    </PageSection>
  );
}

function OptionControl({
  label,
  enabled,
  value,
  testId,
  onEnabledChange,
  onValueChange
}: {
  label: string;
  enabled: boolean;
  value: string;
  testId?: string;
  onEnabledChange: (value: boolean) => void;
  onValueChange: (value: string) => void;
}) {
  return (
    <div className="rounded-lg border border-workbench-border bg-white p-3">
      <label className="flex items-center gap-2 text-sm font-medium text-workbench-text">
        <input type="checkbox" checked={enabled} onChange={(event) => onEnabledChange(event.target.checked)} className="h-4 w-4 accent-[#2457c5]" />
        {label}
      </label>
      <input
        data-testid={testId}
        className="mt-2 min-h-10 w-full rounded-md border border-workbench-border bg-workbench-panel2 px-3 text-sm text-workbench-text outline-none focus:border-[#9db7f5] focus:ring-2 focus:ring-[#dbe7ff] disabled:opacity-55"
        value={value}
        disabled={!enabled}
        onChange={(event) => onValueChange(event.target.value)}
      />
    </div>
  );
}
