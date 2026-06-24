import { spawn } from "node:child_process";
import { createHash, randomBytes } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import type {
  AppCoreSaveAnalysisPayload,
  AppCoreSaveComparisonPayload,
  AppCoreSavePatchPlanPayload,
  AppCoreSavePatchPreviewPayload,
  AppCoreSavePatchRequestPayload,
  GameWindowFrameCapturePayload,
  GameWindowFrameSequencePayload,
  GameWindowCapturePlanPayload,
  GameWindowInputPayload,
  ManagedProcessKind,
  ManagedProcessRegistryEntry,
  ManagedProcessRegistryPayload,
  ManagedProcessLogTailPayload,
  ManagedProcessStatus,
  ManagedProcessStopPayload,
  OptionsPatchKeybindOverride,
  OptionsPatchRequestInput,
  WorkbenchJobDefinition,
  WorkbenchJobInputValue,
  WorkbenchJobRunDetail,
  WorkbenchJobProgressEvent,
  WorkbenchJobProgressPhase,
  WorkbenchJobRunRequest,
  WorkbenchJobRunSummary,
  WorkbenchJobPolicy
} from "@onslaught/contracts";
import { readContentDocument } from "./content-browser";
import {
  applyCatalogPatchSet,
  planCatalogPatchSet,
  prepareExecutableCopyPath,
  restoreCatalogPatchBackup,
  verifyExecutablePath
} from "./patch-verifier";
import {
  convertExecutableAddress,
  getDebugReadiness,
  getGameHarnessProfile,
  getGhidraReadiness,
  inspectGameHarnessProfilePath,
  readHexRange
} from "./re-workbench";
import { getReleasePolicy } from "./release-policy";
import { applyOptionsPatchPath, planOptionsPatchPath, previewOptionsPatchPath } from "./options-patcher";
import {
  applySavePatchPath,
  planSavePatchPath,
  prepareSaveCopyPath,
  previewSavePatchPath,
  restoreSaveBackupPath
} from "./save-patcher";

const runs = new Map<string, WorkbenchJobRunSummary>();
const activeRuns = new Map<string, AbortController>();
const runnableDefinitionIds = new Set([
  "save.applyPatch",
  "save.prepareCopy",
  "save.planPatch",
  "save.previewPatch",
  "save.restoreBackup",
  "settings.applyOptionsPatch",
  "settings.planOptionsPatch",
  "settings.previewOptionsPatch",
  "appcore.inspectSave",
  "appcore.compareSaves",
  "appcore.planSavePatch",
  "appcore.previewSavePatch",
  "file.hexRead",
  "file.peAddressConvert",
  "patch.verifySpecimen",
  "patch.prepareExecutableCopy",
  "patch.planCatalogPatch",
  "patch.applyCatalogPatch",
  "patch.restoreCatalogBackup",
  "release.inspectPolicy",
  "debug.planProbeSession",
  "debug.startProbeServer",
  "debug.resolveCdb",
  "runtime.listManagedProcesses",
  "runtime.tailManagedLog",
  "runtime.stopManagedProcess",
  "ghidra.exportAddressDecompile",
  "ghidra.exportWeakFunctions",
  "ghidra.validateRenameMap",
  "ghidra.applyRenameMap",
  "game.inventoryProfile",
  "game.captureWindowFrame",
  "game.captureWindowSequence",
  "game.planWindowInput",
  "game.sendWindowInput",
  "game.planWindowCapture",
  "game.planLaunchProfile",
  "game.prepareSafeProfile",
  "game.launchProfile",
  "assets.catalogGameFiles",
  "content.readDocument"
]);
type ProgressSink = (event: WorkbenchJobProgressEvent) => void;
export type GameWindowFrameCaptureMatchedBy = "hwnd" | "hint" | "exact-title" | "loose-title" | "none";

export interface GameWindowFrameCaptureRequest {
  sourceHint: string | null;
  title: string;
  hwndHex: string;
  processId: number;
  maxWidth: number;
  maxHeight: number;
}

export interface GameWindowFrameCaptureResult {
  status: "captured" | "capture-unavailable" | "source-not-found";
  sourceId: string | null;
  sourceName: string | null;
  matchedBy: GameWindowFrameCaptureMatchedBy;
  sourceCount: number;
  width?: number;
  height?: number;
  sizeBytes?: number;
  pngBase64?: string;
  previewWidth?: number;
  previewHeight?: number;
  previewSizeBytes?: number;
  previewPngBase64?: string;
  note: string;
}

export interface WorkbenchJobRunnerCapabilities {
  captureGameWindowFrame?: (request: GameWindowFrameCaptureRequest) => Promise<GameWindowFrameCaptureResult>;
}

export async function startWorkbenchJob(
  appPath: string,
  artifactRoot: string,
  definitions: WorkbenchJobDefinition[],
  request: WorkbenchJobRunRequest,
  onProgress?: ProgressSink,
  capabilities: WorkbenchJobRunnerCapabilities = {}
): Promise<WorkbenchJobRunSummary> {
  const definition = definitions.find((candidate) => candidate.id === request.definitionId);
  if (!definition) {
    throw new Error(`Unknown job definition: ${request.definitionId}`);
  }

  const startedAt = new Date().toISOString();
  const startedMs = Date.now();
  const runId = buildRunId(definition.id, startedAt);
  const policy = resolvePolicy(definition.policy, request.timeoutMs);
  const abortController = new AbortController();
  const progress: WorkbenchJobProgressEvent[] = [];
  const emitProgress = (phase: WorkbenchJobProgressPhase, percent: number, message: string, detail?: string) => {
    const event: WorkbenchJobProgressEvent = {
      runId,
      definitionId: definition.id,
      phase,
      percent: Math.max(0, Math.min(100, Math.round(percent))),
      message,
      detail,
      emittedAt: new Date().toISOString()
    };
    progress.push(event);
    onProgress?.(event);
  };
  let summary: WorkbenchJobRunSummary;

  emitProgress("queued", 5, "Job accepted by the typed runner.", definition.title);

  if (!runnableDefinitionIds.has(definition.id)) {
    emitProgress("rejected", 100, "Job is cataloged but not executable by this runner.");
    summary = buildBaseRun(definition, request.inputs, policy, progress, runId, startedAt, startedMs, "rejected", {
      summary: "Job is cataloged but not executable by the first in-process runner.",
      details: [{ label: "Reason", value: "External process, launch, or mutation job requires a future armed runner." }]
    });
    runs.set(runId, summary);
    return writeJobRunArtifact(summary, artifactRoot);
  }

  try {
    activeRuns.set(runId, abortController);
    emitProgress("running", 15, "Running in-process job.", `Timeout: ${policy.timeoutMs} ms`);
    const result = await withTimeout(
      () =>
        executeJob(
          appPath,
          artifactRoot,
          definition.id,
          request.inputs,
          emitProgress,
          abortController.signal,
          runId,
          capabilities
        ),
      policy.timeoutMs,
      abortController
    );
    emitProgress("artifact", 90, "Writing job-run artifact.");
    emitProgress("completed", 100, "Job completed.");
    summary = buildBaseRun(definition, request.inputs, policy, progress, runId, startedAt, startedMs, "completed", result);
  } catch (error) {
    const status =
      error instanceof JobTimeoutError
        ? "timed-out"
        : error instanceof JobCancelledError
          ? "cancelled"
          : error instanceof JobRejectedError
            ? "rejected"
            : "failed";
    emitProgress(status, 100, statusMessage(status), error instanceof Error ? error.message : String(error));
    summary = buildBaseRun(
      definition,
      request.inputs,
      policy,
      progress,
      runId,
      startedAt,
      startedMs,
      status,
      {
        summary:
          status === "timed-out"
            ? "Job timed out before producing a result."
            : status === "cancelled"
              ? "Job was cancelled before producing a result."
              : "Job failed before producing a result.",
        details: []
      },
      error instanceof Error ? error.message : String(error)
    );
  } finally {
    activeRuns.delete(runId);
  }

  runs.set(runId, summary);
  return writeJobRunArtifact(summary, artifactRoot);
}

export function cancelWorkbenchJob(runId: string): boolean {
  const controller = activeRuns.get(runId);
  if (!controller) {
    return false;
  }

  controller.abort();
  return true;
}

export function getWorkbenchJobRun(runId: string): WorkbenchJobRunSummary | null {
  return runs.get(runId) ?? null;
}

export async function listWorkbenchJobRuns(artifactRoot: string, limit = 12): Promise<WorkbenchJobRunSummary[]> {
  const byId = new Map(runs);
  const runsRoot = path.join(path.resolve(artifactRoot), "artifacts", "job-runs");

  try {
    const entries = await fs.readdir(runsRoot, { withFileTypes: true });
    await Promise.all(
      entries
        .filter((entry) => entry.isDirectory())
        .map(async (entry) => {
          const artifactPath = path.join(runsRoot, entry.name, "job-run.json");
          try {
            const parsed = JSON.parse(await fs.readFile(artifactPath, "utf8"));
            if (isJobRunSummary(parsed)) {
              byId.set(parsed.runId, parsed);
            }
          } catch {
            // Ignore partial or stale artifact folders; valid runs stay readable.
          }
        })
    );
  } catch (error) {
    if (!(error instanceof Error) || !("code" in error) || error.code !== "ENOENT") {
      throw error;
    }
  }

  return [...byId.values()]
    .sort((left, right) => Date.parse(right.startedAt) - Date.parse(left.startedAt))
    .slice(0, limit);
}

async function executeJob(
  appPath: string,
  artifactRoot: string,
  definitionId: string,
  inputs: Record<string, WorkbenchJobInputValue>,
  emitProgress: (phase: WorkbenchJobProgressPhase, percent: number, message: string, detail?: string) => void,
  signal: AbortSignal,
  runId: string,
  capabilities: WorkbenchJobRunnerCapabilities = {}
): Promise<{ summary: string; payloadSchema?: string; details: WorkbenchJobRunDetail[] }> {
  switch (definitionId) {
    case "file.hexRead": {
      emitProgress("running", 35, "Reading bounded byte window.");
      const result = await readHexRange(
        stringInput(inputs.path, "path"),
        stringOrNumberInput(inputs.offset ?? "0", "offset"),
        stringOrNumberInput(inputs.length ?? "64", "length"),
        artifactRoot
      );
      emitProgress("running", 75, "Hex artifact created.", result.artifact.artifactPath);
      return {
        summary: `Read ${result.byteLength} bytes from ${result.fileName} at ${result.offsetHex}.`,
        payloadSchema: result.artifact.schemaVersion,
        details: [
          { label: "File", value: result.fileName },
          { label: "Offset", value: result.offsetHex },
          { label: "Bytes", value: `${result.byteLength}/${result.requestedLength}` },
          { label: "SHA-256", value: result.sha256 },
          { label: "Artifact", value: result.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "file.peAddressConvert": {
      emitProgress("running", 35, "Parsing PE headers.");
      const result = await convertExecutableAddress(
        stringInput(inputs.executablePath, "executablePath"),
        stringOrNumberInput(inputs.virtualAddress ?? "0x00529696", "virtualAddress")
      );
      emitProgress("running", 75, "Virtual address converted.", result.fileOffsetHex);
      return {
        summary: `Mapped ${result.virtualAddressHex} to file offset ${result.fileOffsetHex}.`,
        payloadSchema: "address-conversion.v1",
        details: [
          { label: "Executable", value: result.fileName },
          { label: "Image base", value: result.imageBaseHex },
          { label: "RVA", value: result.rvaHex },
          { label: "Section", value: result.section?.name ?? "unknown" },
          { label: "Note", value: result.note }
        ]
      };
    }
    case "save.planPatch": {
      emitProgress("running", 30, "Building TypeScript save patch intent.");
      const requestPayload = buildAppCoreSavePatchRequestPayload(inputs);
      emitProgress("running", 55, "Planning native TypeScript save patch.", requestPayload.input.path);
      const payload = await planSavePatchPath(requestPayload.input, artifactRoot, runId);
      emitProgress("running", 80, "TypeScript save patch plan artifact ready.", payload.artifact.artifactPath);
      return {
        summary: `TypeScript planned ${payload.source.fileName}: ${payload.plan.sections.join(", ") || "no sections"}; source unchanged.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "File", value: payload.source.fileName },
          { label: "Target kind", value: payload.plan.targetKind },
          { label: "Rank", value: payload.input.rank },
          { label: "Kill count", value: String(payload.input.kills) },
          { label: "Sections", value: payload.plan.sections.join(", ") || "none" },
          { label: "Level ranks", value: String(payload.plan.levelRankCount) },
          { label: "Per-category kills", value: String(payload.plan.perCategoryKillCount) },
          { label: "Current kills", value: String(payload.current.totalKills) },
          { label: "Requires copied apply", value: payload.plan.requiresCopiedApply ? "yes" : "no" },
          { label: "Source unchanged", value: payload.plan.sourceUnchanged ? "yes" : "no" },
          { label: "Plan artifact", value: payload.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "save.prepareCopy": {
      requireArmPhrase(inputs.armPhrase, "COPY SAVE FILE", "save file copy");
      requireTrueInput(inputs.acceptsLocalCopy, "acceptsLocalCopy", "save file copy");
      const sourcePath = stringInput(inputs.sourcePath ?? inputs.path, "sourcePath");
      emitProgress("running", 35, "Copying save/options file into app artifact root.", sourcePath);
      const payload = await prepareSaveCopyPath(sourcePath, artifactRoot, runId);
      emitProgress("running", 82, "Save copy artifact ready.", payload.artifact.artifactPath);
      return {
        summary: `Copied ${payload.source.fileName} into the app artifact root; source unchanged and read-back verified.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Source", value: payload.source.path },
          { label: "Copied target", value: payload.copy.path },
          { label: "Kind", value: payload.source.isOptionsFile ? "options/defaultoptions" : "career save" },
          { label: "Version", value: `${payload.source.versionWordHex} (${payload.source.versionValid ? "valid" : "invalid"})` },
          { label: "Goodies", value: String(payload.inspection.displayableGoodiesUnlocked) },
          { label: "Kill total", value: String(payload.inspection.totalKills) },
          { label: "Read-back verified", value: payload.copy.readbackVerified ? "yes" : "no" },
          { label: "Copy artifact", value: payload.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "save.previewPatch": {
      emitProgress("running", 30, "Building TypeScript save patch intent.");
      const requestPayload = buildAppCoreSavePatchRequestPayload(inputs);
      emitProgress("running", 55, "Previewing native TypeScript save patch.", requestPayload.input.path);
      const payload = await previewSavePatchPath(requestPayload.input, artifactRoot, runId);
      const topRegion = payload.comparison.topRegions[0];
      emitProgress("running", 80, "TypeScript save patch preview artifact ready.", payload.artifact.artifactPath);
      return {
        summary: payload.preview.wouldChange
          ? `TypeScript previewed ${payload.source.fileName}: ${payload.preview.differingBytes} bytes would change, source unchanged.`
          : `TypeScript previewed ${payload.source.fileName}: no byte changes needed.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "File", value: payload.source.fileName },
          { label: "Rank", value: payload.input.rank },
          { label: "Kill count", value: String(payload.input.kills) },
          { label: "Sections", value: plannedSectionsFromInput(payload.input).join(", ") || "none" },
          { label: "Would change", value: payload.preview.wouldChange ? "yes" : "no" },
          { label: "Differing bytes", value: String(payload.preview.differingBytes) },
          { label: "Top region", value: topRegion ? `${topRegion.region}: ${topRegion.differingBytes}` : "none" },
          {
            label: "Goodies",
            value: `${payload.beforeAfter.displayableGoodiesUnlocked.before} -> ${payload.beforeAfter.displayableGoodiesUnlocked.after}`
          },
          { label: "Kill total", value: `${payload.beforeAfter.totalKills.before} -> ${payload.beforeAfter.totalKills.after}` },
          { label: "Source unchanged", value: "yes" },
          { label: "Candidate artifact", value: payload.artifact.candidateArtifactPath ?? "not written" },
          { label: "Preview artifact", value: payload.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "save.applyPatch": {
      requireArmPhrase(inputs.armPhrase, "APPLY SAVE PATCH", "save patch apply");
      requireTrueInput(inputs.acceptsSaveWrite, "acceptsSaveWrite", "save patch apply");
      emitProgress("running", 25, "Building TypeScript save patch apply intent.");
      const requestPayload = buildAppCoreSavePatchRequestPayload(inputs);
      emitProgress("running", 45, "Applying patch to artifact-root copied save.", requestPayload.input.path);
      const payload = await applySavePatchPath(requestPayload.input, artifactRoot, runId);
      const topRegion = payload.comparison.topRegions[0];
      emitProgress("running", 82, "Save patch apply artifact ready.", payload.artifact.artifactPath);
      return {
        summary: payload.target.changed
          ? `Applied TypeScript save patch to copied target ${payload.target.fileName}; backup and read-back verification succeeded.`
          : `TypeScript save patch apply found ${payload.target.fileName} already matched the requested bytes; backup retained.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Target", value: payload.target.path },
          { label: "Rank", value: payload.input.rank },
          { label: "Kill count", value: String(payload.input.kills) },
          { label: "Sections", value: plannedSectionsFromInput(payload.input).join(", ") || "none" },
          { label: "Changed", value: payload.target.changed ? "yes" : "no" },
          { label: "Differing bytes", value: String(payload.comparison.differingBytes) },
          { label: "Top region", value: topRegion ? `${topRegion.region}: ${topRegion.differingBytes}` : "none" },
          { label: "Backup", value: payload.backup.backupPath },
          { label: "Read-back verified", value: payload.target.readbackVerified ? "yes" : "no" },
          { label: "Apply artifact", value: payload.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "save.restoreBackup": {
      requireArmPhrase(inputs.armPhrase, "RESTORE SAVE BACKUP", "save backup restore");
      requireTrueInput(inputs.acceptsSaveWrite, "acceptsSaveWrite", "save backup restore");
      const targetPath = stringInput(inputs.targetPath, "targetPath");
      const backupPath = stringInput(inputs.backupPath, "backupPath");
      emitProgress("running", 35, "Restoring artifact-root save backup.", backupPath);
      const payload = await restoreSaveBackupPath(targetPath, backupPath, artifactRoot, runId);
      emitProgress("running", 82, "Save restore artifact ready.", payload.artifact.artifactPath);
      return {
        summary: `Restored ${payload.backup.fileName} to copied target ${payload.target.fileName}; read-back verification succeeded.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Target", value: payload.target.path },
          { label: "Backup", value: payload.backup.path },
          { label: "Pre-restore backup", value: payload.preRestoreBackup?.backupPath ?? "not written" },
          { label: "Read-back verified", value: payload.target.readbackVerified ? "yes" : "no" },
          { label: "Target SHA-256", value: payload.target.afterSha256 },
          { label: "Restore artifact", value: payload.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "settings.planOptionsPatch": {
      emitProgress("running", 30, "Building TypeScript global-options patch intent.");
      const input = buildOptionsPatchRequestInput(inputs);
      emitProgress("running", 55, "Planning native TypeScript global-options patch.", input.path);
      const payload = await planOptionsPatchPath(input, artifactRoot, runId);
      emitProgress("running", 80, "TypeScript global-options patch plan artifact ready.", payload.artifact.artifactPath);
      return {
        summary: `TypeScript planned global options patch for ${payload.source.fileName}: ${payload.plan.sections.join(", ") || "no sections"}; source unchanged.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "File", value: payload.source.fileName },
          { label: "Target kind", value: payload.plan.targetKind },
          { label: "Sections", value: payload.plan.sections.join(", ") || "none" },
          { label: "Settings overrides", value: String(payload.plan.settingsOverrideCount) },
          { label: "Tail overrides", value: String(payload.plan.tailOverrideCount) },
          { label: "Keybind rows", value: String(payload.plan.keybindOverrideCount) },
          { label: "Copy entries", value: payload.plan.copyOptionsEntries ? "yes" : "no" },
          { label: "Copy tail", value: payload.plan.copyOptionsTail ? "yes" : "no" },
          { label: "Requires copied apply", value: payload.plan.requiresCopiedApply ? "yes" : "no" },
          { label: "Source unchanged", value: payload.plan.sourceUnchanged ? "yes" : "no" },
          { label: "Plan artifact", value: payload.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "settings.previewOptionsPatch": {
      emitProgress("running", 30, "Building TypeScript global-options patch intent.");
      const input = buildOptionsPatchRequestInput(inputs);
      emitProgress("running", 55, "Previewing native TypeScript global-options patch.", input.path);
      const payload = await previewOptionsPatchPath(input, artifactRoot, runId);
      const topRegion = payload.comparison.topRegions[0];
      emitProgress("running", 80, "TypeScript global-options patch preview artifact ready.", payload.artifact.artifactPath);
      return {
        summary: payload.preview.wouldChange
          ? `TypeScript previewed ${payload.source.fileName}: ${payload.preview.differingBytes} option bytes would change, source unchanged.`
          : `TypeScript previewed ${payload.source.fileName}: no option byte changes needed.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "File", value: payload.source.fileName },
          { label: "Sections", value: plannedOptionsSectionsFromInput(payload.input).join(", ") || "none" },
          { label: "Would change", value: payload.preview.wouldChange ? "yes" : "no" },
          { label: "Differing bytes", value: String(payload.preview.differingBytes) },
          { label: "Top region", value: topRegion ? `${topRegion.region}: ${topRegion.differingBytes}` : "none" },
          {
            label: "Sound",
            value: `${payload.beforeAfter.before.settings.soundVolume} -> ${payload.beforeAfter.after.settings.soundVolume}`
          },
          {
            label: "Music",
            value: `${payload.beforeAfter.before.settings.musicVolume} -> ${payload.beforeAfter.after.settings.musicVolume}`
          },
          {
            label: "Control scheme",
            value: `${payload.beforeAfter.before.options.controlSchemeIndex ?? "n/a"} -> ${payload.beforeAfter.after.options.controlSchemeIndex ?? "n/a"}`
          },
          { label: "Keybind rows", value: String(payload.input.keybindOverrides.length) },
          { label: "Source unchanged", value: "yes" },
          { label: "Candidate artifact", value: payload.artifact.candidateArtifactPath ?? "not written" },
          { label: "Preview artifact", value: payload.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "settings.applyOptionsPatch": {
      requireArmPhrase(inputs.armPhrase, "APPLY OPTIONS PATCH", "global-options patch apply");
      requireTrueInput(inputs.acceptsOptionsWrite, "acceptsOptionsWrite", "global-options patch apply");
      emitProgress("running", 25, "Building TypeScript global-options patch apply intent.");
      const input = buildOptionsPatchRequestInput(inputs);
      emitProgress("running", 45, "Applying options patch to artifact-root copied file.", input.path);
      const payload = await applyOptionsPatchPath(input, artifactRoot, runId);
      const topRegion = payload.comparison.topRegions[0];
      emitProgress("running", 82, "Global-options patch apply artifact ready.", payload.artifact.artifactPath);
      return {
        summary: payload.target.changed
          ? `Applied TypeScript global-options patch to copied target ${payload.target.fileName}; backup and read-back verification succeeded.`
          : `TypeScript global-options patch apply found ${payload.target.fileName} already matched the requested bytes; backup retained.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Target", value: payload.target.path },
          { label: "Sections", value: plannedOptionsSectionsFromInput(payload.input).join(", ") || "none" },
          { label: "Changed", value: payload.target.changed ? "yes" : "no" },
          { label: "Differing bytes", value: String(payload.comparison.differingBytes) },
          { label: "Top region", value: topRegion ? `${topRegion.region}: ${topRegion.differingBytes}` : "none" },
          { label: "Sound", value: `${payload.beforeAfter.before.settings.soundVolume} -> ${payload.beforeAfter.after.settings.soundVolume}` },
          { label: "Music", value: `${payload.beforeAfter.before.settings.musicVolume} -> ${payload.beforeAfter.after.settings.musicVolume}` },
          { label: "Control scheme", value: `${payload.beforeAfter.before.options.controlSchemeIndex ?? "n/a"} -> ${payload.beforeAfter.after.options.controlSchemeIndex ?? "n/a"}` },
          { label: "Backup", value: payload.backup.backupPath },
          { label: "Read-back verified", value: payload.target.readbackVerified ? "yes" : "no" },
          { label: "Apply artifact", value: payload.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "appcore.inspectSave": {
      emitProgress("running", 25, "Resolving AppCore host project.");
      const repoRoot = await resolveJobRepoRoot(appPath);
      const hostProject = path.join(repoRoot, "OnslaughtCareerEditor.AppCore.Host", "OnslaughtCareerEditor.AppCore.Host.csproj");
      await fs.access(hostProject);

      const selectedPath = stringInput(inputs.path, "path");
      emitProgress("running", 45, "Running allowlisted AppCore save analysis host.", selectedPath);
      const { command, args } = dotnetCommand(hostProject, ["inspect-save", selectedPath]);
      const result = await runAllowlistedProcess(command, args, repoRoot, signal);
      const payload = parseJsonProcessStdout(result.stdout) as AppCoreSaveAnalysisPayload;
      if (payload.schemaVersion !== "appcore-save-analysis.v1") {
        throw new Error(`Unexpected AppCore host payload schema: ${payload.schemaVersion}`);
      }

      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "appcore-save-analysis",
        runId,
        "analysis.json",
        payload as unknown as Record<string, unknown>
      );
      const usedNodes = payload.analysis.counts.completedNodes + payload.analysis.counts.partialNodes;
      const totalKills = payload.analysis.kills.reduce((sum, row) => sum + row.kills, 0);
      emitProgress("running", 80, "AppCore host artifact ready.", artifactPath);
      return {
        summary: `AppCore inspected ${payload.analysis.fileName}: ${payload.analysis.counts.completedNodes}/${usedNodes} missions, ${totalKills} kills.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Host project", value: hostProject },
          { label: "File", value: payload.analysis.fileName },
          { label: "Valid", value: payload.analysis.isValid ? "yes" : "no" },
          { label: "Kind", value: payload.analysis.isOptionsFile ? "global options" : "career save" },
          { label: "Version", value: `${payload.analysis.versionWordHex} (${payload.analysis.versionValid ? "valid" : "invalid"})` },
          { label: "Missions", value: `${payload.analysis.counts.completedNodes}/${usedNodes}` },
          {
            label: "Goodies",
            value: `${payload.analysis.goodies.newCount + payload.analysis.goodies.old}/${payload.analysis.goodies.displayableTotal}`
          },
          { label: "Kill total", value: String(totalKills) },
          { label: "AppCore artifact", value: artifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "appcore.compareSaves": {
      emitProgress("running", 25, "Resolving AppCore host project.");
      const repoRoot = await resolveJobRepoRoot(appPath);
      const hostProject = path.join(repoRoot, "OnslaughtCareerEditor.AppCore.Host", "OnslaughtCareerEditor.AppCore.Host.csproj");
      await fs.access(hostProject);

      const leftPath = stringInput(inputs.leftPath, "leftPath");
      const rightPath = stringInput(inputs.rightPath, "rightPath");
      emitProgress("running", 45, "Running allowlisted AppCore save comparison host.", `${leftPath} :: ${rightPath}`);
      const { command, args } = dotnetCommand(hostProject, ["compare-saves", leftPath, rightPath]);
      const result = await runAllowlistedProcess(command, args, repoRoot, signal);
      const payload = parseJsonProcessStdout(result.stdout) as AppCoreSaveComparisonPayload;
      if (payload.schemaVersion !== "appcore-save-comparison.v1") {
        throw new Error(`Unexpected AppCore host payload schema: ${payload.schemaVersion}`);
      }

      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "appcore-save-comparison",
        runId,
        "comparison.json",
        payload as unknown as Record<string, unknown>
      );
      const topRegion = payload.comparison.topRegions[0];
      emitProgress("running", 80, "AppCore comparison artifact ready.", artifactPath);
      return {
        summary: payload.comparison.identical
          ? `AppCore compared ${payload.comparison.leftFileName} and ${payload.comparison.rightFileName}: identical.`
          : `AppCore compared ${payload.comparison.leftFileName} and ${payload.comparison.rightFileName}: ${payload.comparison.differingBytes} differing bytes.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Host project", value: hostProject },
          { label: "Left", value: payload.comparison.leftFileName },
          { label: "Right", value: payload.comparison.rightFileName },
          { label: "Same size", value: payload.comparison.sameSize ? "yes" : "no" },
          { label: "Identical", value: payload.comparison.identical ? "yes" : "no" },
          { label: "Differing bytes", value: String(payload.comparison.differingBytes) },
          { label: "Ranges", value: String(payload.comparison.diffRanges.length) },
          { label: "Top region", value: topRegion ? `${topRegion.region}: ${topRegion.differingBytes}` : "none" },
          { label: "AppCore artifact", value: artifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "appcore.planSavePatch": {
      emitProgress("running", 25, "Resolving AppCore host project.");
      const repoRoot = await resolveJobRepoRoot(appPath);
      const hostProject = path.join(repoRoot, "OnslaughtCareerEditor.AppCore.Host", "OnslaughtCareerEditor.AppCore.Host.csproj");
      await fs.access(hostProject);

      const requestPayload = buildAppCoreSavePatchRequestPayload(inputs);
      const requestArtifactPath = await writePlanArtifact(
        artifactRoot,
        "appcore-save-patch-plan",
        runId,
        "request.json",
        requestPayload as unknown as Record<string, unknown>
      );
      emitProgress("running", 45, "Running allowlisted AppCore save patch planner host.", requestArtifactPath);
      const { command, args } = dotnetCommand(hostProject, ["plan-save-patch", requestArtifactPath]);
      const result = await runAllowlistedProcess(command, args, repoRoot, signal);
      const payload = parseJsonProcessStdout(result.stdout) as AppCoreSavePatchPlanPayload;
      if (payload.schemaVersion !== "appcore-save-patch-plan.v1") {
        throw new Error(`Unexpected AppCore host payload schema: ${payload.schemaVersion}`);
      }

      const planArtifactPath = await writePlanArtifact(
        artifactRoot,
        "appcore-save-patch-plan",
        runId,
        "plan.json",
        payload as unknown as Record<string, unknown>
      );
      emitProgress("running", 80, "AppCore patch plan artifact ready.", planArtifactPath);
      return {
        summary: `AppCore planned ${payload.source.fileName}: ${payload.plan.sections.join(", ") || "no sections"}; source unchanged.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Host project", value: hostProject },
          { label: "File", value: payload.source.fileName },
          { label: "Target kind", value: payload.plan.targetKind },
          { label: "Rank", value: payload.input.rank },
          { label: "Kill count", value: String(payload.input.kills) },
          { label: "Sections", value: payload.plan.sections.join(", ") || "none" },
          { label: "Level ranks", value: String(payload.plan.levelRankCount) },
          { label: "Per-category kills", value: String(payload.plan.perCategoryKillCount) },
          { label: "Current kills", value: String(payload.current.totalKills) },
          { label: "Requires copied apply", value: payload.plan.requiresCopiedApply ? "yes" : "no" },
          { label: "Source unchanged", value: payload.plan.sourceUnchanged ? "yes" : "no" },
          { label: "Request artifact", value: requestArtifactPath },
          { label: "Plan artifact", value: planArtifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "appcore.previewSavePatch": {
      emitProgress("running", 25, "Resolving AppCore host project.");
      const repoRoot = await resolveJobRepoRoot(appPath);
      const hostProject = path.join(repoRoot, "OnslaughtCareerEditor.AppCore.Host", "OnslaughtCareerEditor.AppCore.Host.csproj");
      await fs.access(hostProject);

      const selectedPath = stringInput(inputs.path, "path");
      const rank = optionalStringInput(inputs.rank, "rank") ?? "S";
      const kills = String(stringOrNumberInput(inputs.kills ?? "100", "kills"));
      emitProgress("running", 45, "Running allowlisted AppCore save patch preview host.", selectedPath);
      const { command, args } = dotnetCommand(hostProject, ["preview-save-patch", selectedPath, "--rank", rank, "--kills", kills]);
      const result = await runAllowlistedProcess(command, args, repoRoot, signal);
      const payload = parseJsonProcessStdout(result.stdout) as AppCoreSavePatchPreviewPayload;
      if (payload.schemaVersion !== "appcore-save-patch-preview.v1") {
        throw new Error(`Unexpected AppCore host payload schema: ${payload.schemaVersion}`);
      }

      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "appcore-save-patch-preview",
        runId,
        "preview.json",
        payload as unknown as Record<string, unknown>
      );
      const topRegion = payload.comparison.topRegions[0];
      emitProgress("running", 80, "AppCore patch preview artifact ready.", artifactPath);
      return {
        summary: payload.preview.wouldChange
          ? `AppCore previewed ${payload.source.fileName}: ${payload.preview.differingBytes} bytes would change, source unchanged.`
          : `AppCore previewed ${payload.source.fileName}: no byte changes needed.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Host project", value: hostProject },
          { label: "File", value: payload.source.fileName },
          { label: "Rank", value: payload.input.rank },
          { label: "Kill count", value: String(payload.input.kills) },
          {
            label: "Sections",
            value: [
              payload.input.patchNodes ? "nodes" : null,
              payload.input.patchLinks ? "links" : null,
              payload.input.patchGoodies ? "goodies" : null,
              payload.input.patchKills ? "kills" : null
            ]
              .filter(Boolean)
              .join(", ") || "none"
          },
          { label: "Would change", value: payload.preview.wouldChange ? "yes" : "no" },
          { label: "Differing bytes", value: String(payload.preview.differingBytes) },
          { label: "Top region", value: topRegion ? `${topRegion.region}: ${topRegion.differingBytes}` : "none" },
          { label: "Goodies", value: `${payload.beforeAfter.displayableGoodiesUnlocked.before} -> ${payload.beforeAfter.displayableGoodiesUnlocked.after}` },
          { label: "Kill total", value: `${payload.beforeAfter.totalKills.before} -> ${payload.beforeAfter.totalKills.after}` },
          { label: "Temp copy deleted", value: payload.preview.tempOutputDeleted ? "yes" : "no" },
          { label: "Preview artifact", value: artifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "patch.verifySpecimen": {
      emitProgress("running", 30, "Hashing executable and loading patch catalog.");
      const result = await verifyExecutablePath(stringInput(inputs.executablePath, "executablePath"), appPath, artifactRoot);
      emitProgress("running", 80, "Patch catalog states classified.", `${result.catalog.patchCount} patch rows`);
      return {
        summary: `Verified ${result.fileName}: ${result.counts.original} original, ${result.counts.patched} patched, ${result.counts.mismatch} mismatch.`,
        payloadSchema: result.artifact.schemaVersion,
        details: [
          { label: "File", value: result.fileName },
          { label: "Known Steam hash", value: result.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Catalog patches", value: String(result.catalog.patchCount) },
          { label: "Artifact", value: result.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "patch.planCatalogPatch": {
      emitProgress("running", 30, "Verifying executable bytes before planning.");
      const result = await planCatalogPatchSet(
        stringInput(inputs.executablePath, "executablePath"),
        appPath,
        artifactRoot,
        optionalStringInput(inputs.patchIds, "patchIds") ?? "stable"
      );
      emitProgress(
        "running",
        78,
        "Patch plan generated.",
        `${result.counts.readyToApply} ready, ${result.counts.alreadyApplied} already applied, ${result.counts.blocked} blocked`
      );
      return {
        summary: `Planned ${result.counts.selected} patch rows for ${result.fileName}: ${result.counts.readyToApply} ready, ${result.counts.alreadyApplied} already applied, ${result.counts.blocked} blocked.`,
        payloadSchema: result.artifact.schemaVersion,
        details: [
          { label: "File", value: result.fileName },
          { label: "Patch IDs", value: result.patchIds.join(", ") },
          { label: "Ready to apply", value: String(result.counts.readyToApply) },
          { label: "Already applied", value: String(result.counts.alreadyApplied) },
          { label: "Blocked", value: String(result.counts.blocked) },
          { label: "Can apply all", value: result.canApplyAll ? "yes" : "no" },
          { label: "Plan artifact", value: result.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "patch.prepareExecutableCopy": {
      requireArmPhrase(inputs.armPhrase, "COPY BEA EXE", "executable copy");
      requireTrueInput(inputs.acceptsLocalCopy, "acceptsLocalCopy", "executable copy");
      const sourcePath = stringInput(inputs.sourcePath ?? inputs.executablePath, "sourcePath");
      emitProgress("running", 35, "Copying BEA.exe into app artifact root.", sourcePath);
      const result = await prepareExecutableCopyPath(sourcePath, appPath, artifactRoot, runId);
      emitProgress("running", 82, "Executable copy artifact ready.", result.artifact.artifactPath);
      return {
        summary: `Copied ${result.source.fileName} into the app artifact root; source unchanged and read-back verified.`,
        payloadSchema: result.schemaVersion,
        details: [
          { label: "Source", value: result.source.path },
          { label: "Copied target", value: result.copy.path },
          { label: "Known Steam hash", value: result.source.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Catalog patches", value: String(result.catalog.patchCount) },
          { label: "Original rows", value: String(result.source.counts.original) },
          { label: "Patched rows", value: String(result.source.counts.patched) },
          { label: "Read-back verified", value: result.copy.readbackVerified ? "yes" : "no" },
          { label: "Copy artifact", value: result.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "patch.applyCatalogPatch": {
      requireArmPhrase(inputs.armPhrase, "APPLY CATALOG PATCH", "catalog patch apply");
      requireTrueInput(inputs.acceptsExecutableWrite, "acceptsExecutableWrite", "catalog patch apply");
      emitProgress("running", 28, "Verifying copied executable bytes before patch apply.");
      const result = await applyCatalogPatchSet(
        stringInput(inputs.executablePath, "executablePath"),
        appPath,
        artifactRoot,
        optionalStringInput(inputs.patchIds, "patchIds") ?? "stable",
        runId
      );
      emitProgress(
        "running",
        82,
        "Catalog patch apply artifact ready.",
        `${result.counts.applied} applied, ${result.counts.alreadyApplied} already applied`
      );
      return {
        summary: result.target.changed
          ? `Applied ${result.counts.applied} curated patch rows to copied ${result.target.fileName}; backup and read-back verification succeeded.`
          : `Copied ${result.target.fileName} already matched the selected curated patch bytes; backup retained.`,
        payloadSchema: result.schemaVersion,
        details: [
          { label: "Target", value: result.target.path },
          { label: "Patch IDs", value: result.rows.map((row) => row.id).join(", ") },
          { label: "Applied", value: String(result.counts.applied) },
          { label: "Already applied", value: String(result.counts.alreadyApplied) },
          { label: "Changed", value: result.target.changed ? "yes" : "no" },
          { label: "Backup", value: result.backup.backupPath },
          { label: "Read-back verified", value: result.target.readbackVerified ? "yes" : "no" },
          { label: "Known Steam hash before", value: result.verification.before.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Known Steam hash after", value: result.verification.after.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Apply artifact", value: result.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "patch.restoreCatalogBackup": {
      requireArmPhrase(inputs.armPhrase, "RESTORE CATALOG BACKUP", "catalog patch restore");
      requireTrueInput(inputs.acceptsExecutableWrite, "acceptsExecutableWrite", "catalog patch restore");
      emitProgress("running", 30, "Restoring copied executable backup.");
      const result = await restoreCatalogPatchBackup(
        stringInput(inputs.targetPath, "targetPath"),
        stringInput(inputs.backupPath, "backupPath"),
        appPath,
        artifactRoot,
        runId
      );
      emitProgress("running", 82, "Catalog patch restore artifact ready.", result.artifact.artifactPath);
      return {
        summary: `Restored copied ${result.target.fileName} from backup; read-back verification succeeded.`,
        payloadSchema: result.schemaVersion,
        details: [
          { label: "Target", value: result.target.path },
          { label: "Backup", value: result.backup.path },
          { label: "Pre-restore backup", value: result.preRestoreBackup.backupPath },
          { label: "Read-back verified", value: result.target.readbackVerified ? "yes" : "no" },
          { label: "Known Steam hash after", value: result.verification.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Restore artifact", value: result.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "release.inspectPolicy": {
      emitProgress("running", 35, "Reading release and content policy.");
      const result = await getReleasePolicy(appPath, artifactRoot);
      emitProgress(
        "running",
        78,
        "Release policy artifact created.",
        `${result.counts.communityDocs} community docs, ${result.counts.existingDeniedPaths} existing hard-deny paths`
      );
      return {
        summary: `Classified ${result.counts.contentTotal} curated content rows and ${result.pathRules.length} release path rules.`,
        payloadSchema: result.artifact.schemaVersion,
        details: [
          { label: "Community docs", value: String(result.counts.communityDocs) },
          { label: "Maintainer docs", value: String(result.counts.maintainerDocs) },
          { label: "Hard-deny paths", value: String(result.counts.deny) },
          { label: "Existing hard-deny paths", value: String(result.counts.existingDeniedPaths) },
          { label: "Source tree", value: result.profiles.find((profile) => profile.id === "source-tree")?.status ?? "unknown" },
          { label: "Portable bundle", value: result.profiles.find((profile) => profile.id === "portable-bundle")?.status ?? "unknown" },
          { label: "Policy artifact", value: result.artifact.artifactPath ?? "not written" }
        ]
      };
    }
    case "game.inventoryProfile": {
      emitProgress("running", 35, "Inspecting game profile.");
      const gameRoot = typeof inputs.gameRoot === "string" && inputs.gameRoot.trim() ? inputs.gameRoot : null;
      const result = gameRoot
        ? await inspectGameHarnessProfilePath(appPath, gameRoot)
        : await getGameHarnessProfile(appPath, artifactRoot);
      emitProgress("running", 75, "Game profile inventory complete.", result.gameRoot);
      return {
        summary: `Game profile ${result.ready ? "is ready" : "has missing required files"}: ${result.gameRoot}`,
        payloadSchema: result.artifact.schemaVersion,
        details: [
          { label: "Source", value: result.profileSource },
          { label: "Executable", value: result.executablePath },
          { label: "Required files", value: `${result.files.filter((file) => file.required && file.exists).length}/${result.files.filter((file) => file.required).length}` },
          { label: "Launch status", value: result.launchPlan.status }
        ]
      };
    }
    case "game.captureWindowFrame": {
      emitProgress("running", 22, "Planning managed BEA window before still-frame capture.");
      const maxWidth = parseCaptureDimensionInput(inputs.maxWidth, "maxWidth", 960, 160, 1280);
      const maxHeight = parseCaptureDimensionInput(inputs.maxHeight, "maxHeight", 540, 120, 720);
      const planResult = await executeJob(
        appPath,
        artifactRoot,
        "game.planWindowCapture",
        inputs,
        emitProgress,
        signal,
        runId,
        capabilities
      );
      const planArtifactPath = planResult.details.find((detail) => detail.label === "Plan artifact")?.value ?? null;
      if (!planArtifactPath) {
        throw new Error("Window-capture plan did not return an artifact path.");
      }
      const planPayload = JSON.parse(await fs.readFile(planArtifactPath, "utf8")) as GameWindowCapturePlanPayload;
      if (planPayload.schemaVersion !== "game-window-capture-plan.v1") {
        throw new Error(`Unexpected game-window capture plan schema: ${planPayload.schemaVersion}`);
      }

      const inputNote =
        "Scoped keyboard input is available through game.planWindowInput and explicitly armed game.sendWindowInput.";
      const writeFrameArtifact = async (
        status: GameWindowFrameCapturePayload["status"],
        capture: GameWindowFrameCapturePayload["capture"],
        frame: GameWindowFrameCapturePayload["frame"],
        note: string
      ) => {
        const payload: GameWindowFrameCapturePayload = {
          schemaVersion: "game-window-frame-capture.v1",
          generatedAt: new Date().toISOString(),
          mutation: false,
          processName: planPayload.processName,
          targetRunId: planPayload.targetRunId,
          status,
          selectedWindow: planPayload.selectedWindow,
          planArtifactPath,
          capture,
          frame,
          input: {
            status: "planned",
            method: "scoped-window-input",
            note: inputNote
          },
          artifact: {
            kind: "read-only",
            mutation: false,
            schemaVersion: "game-window-frame-capture.v1",
            note
          }
        };
        const artifactPath = await writePlanArtifact(
          artifactRoot,
          "game-window-frame-capture",
          runId,
          "frame.json",
          payload as unknown as Record<string, unknown>
        );
        return { payload, artifactPath };
      };
      const buildDetails = (payload: GameWindowFrameCapturePayload, artifactPath: string): WorkbenchJobRunDetail[] => {
        const details: WorkbenchJobRunDetail[] = [
          { label: "Target run", value: payload.targetRunId ?? "none" },
          { label: "Process", value: `${payload.processName} (game)` },
          { label: "Process ID", value: payload.selectedWindow ? String(payload.selectedWindow.processId) : "none" },
          { label: "Frame status", value: payload.status },
          {
            label: "Window",
            value: payload.selectedWindow ? payload.selectedWindow.title || payload.selectedWindow.hwndHex : "none"
          },
          { label: "Window handle", value: payload.selectedWindow?.hwndHex ?? "none" },
          { label: "Source", value: payload.capture.sourceName ?? payload.capture.sourceId ?? "none" },
          { label: "Source count", value: String(payload.capture.sourceCount) }
        ];
        if (payload.frame) {
          details.push(
            { label: "Frame size", value: `${payload.frame.width}x${payload.frame.height}` },
            { label: "Frame bytes", value: String(payload.frame.sizeBytes) },
            { label: "Frame SHA-256", value: payload.frame.sha256 },
            { label: "Frame PNG", value: payload.frame.pngPath },
            { label: "Frame preview data URL", value: payload.frame.previewDataUrl ?? "none" }
          );
        }
        details.push(
          { label: "Input status", value: payload.input.status },
          { label: "Frame artifact", value: artifactPath },
          { label: "Note", value: payload.capture.note }
        );
        return details;
      };

      if (planPayload.status !== "ready" || !planPayload.selectedWindow) {
        const status = planPayload.status === "ready" ? "capture-unavailable" : planPayload.status;
        const note = `No frame captured because window discovery returned ${planPayload.status}. Retail BEA usually needs the windowed/display patch before fullscreen Direct3D exposes a useful capturable top-level window.`;
        const { payload, artifactPath } = await writeFrameArtifact(
          status,
          {
            status,
            method: "electron-desktop-capturer",
            sourceHint: planPayload.capture.sourceHint,
            sourceId: null,
            sourceName: null,
            matchedBy: "none",
            sourceCount: planPayload.counts.candidates,
            note
          },
          null,
          "Read-only still-frame capture attempt. No desktop stream was opened and no input was sent."
        );
        emitProgress("running", 82, "Game-window still-frame capture skipped after planning.", artifactPath);
        return {
          summary: `No BEA frame captured because window planning returned ${planPayload.status}.`,
          payloadSchema: "game-window-frame-capture.v1",
          details: buildDetails(payload, artifactPath)
        };
      }

      if (!capabilities.captureGameWindowFrame) {
        const note =
          "Desktop capture is unavailable in this runtime. Run the packaged/dev desktop app to capture a bounded frame; Node parity runs stop at the typed artifact boundary.";
        const { payload, artifactPath } = await writeFrameArtifact(
          "capture-unavailable",
          {
            status: "capture-unavailable",
            method: "electron-desktop-capturer",
            sourceHint: planPayload.capture.sourceHint,
            sourceId: null,
            sourceName: null,
            matchedBy: "none",
            sourceCount: planPayload.counts.candidates,
            note
          },
          null,
          "Read-only still-frame capture attempt. No desktop stream was opened and no input was sent."
        );
        emitProgress("running", 82, "Game-window still-frame capture capability is unavailable.", artifactPath);
        return {
          summary: "BEA window was planned, but this runtime cannot capture desktop thumbnails.",
          payloadSchema: "game-window-frame-capture.v1",
          details: buildDetails(payload, artifactPath)
        };
      }

      emitProgress("running", 62, "Requesting bounded desktop thumbnail.", `${maxWidth}x${maxHeight}`);
      const captureResult = await capabilities.captureGameWindowFrame({
        sourceHint: planPayload.capture.sourceHint,
        title: planPayload.selectedWindow.title,
        hwndHex: planPayload.selectedWindow.hwndHex,
        processId: planPayload.selectedWindow.processId,
        maxWidth,
        maxHeight
      });

      if (captureResult.status !== "captured" || !captureResult.pngBase64) {
        const note =
          captureResult.note ||
          "The desktop capture layer did not return a capturable window thumbnail. If BEA is fullscreen, apply the windowed/display patch before retrying.";
        const { payload, artifactPath } = await writeFrameArtifact(
          captureResult.status,
          {
            status: captureResult.status,
            method: "electron-desktop-capturer",
            sourceHint: planPayload.capture.sourceHint,
            sourceId: captureResult.sourceId,
            sourceName: captureResult.sourceName,
            matchedBy: captureResult.matchedBy,
            sourceCount: captureResult.sourceCount,
            note
          },
          null,
          "Read-only still-frame capture attempt. No input was sent."
        );
        emitProgress("running", 82, "Game-window still-frame capture did not return an image.", artifactPath);
        return {
          summary: `BEA window frame was not captured: ${captureResult.status}.`,
          payloadSchema: "game-window-frame-capture.v1",
          details: buildDetails(payload, artifactPath)
        };
      }

      const png = Buffer.from(captureResult.pngBase64, "base64");
      const sha256 = createHash("sha256").update(png).digest("hex");
      const frameDir = path.join(path.resolve(artifactRoot), "artifacts", "game-window-frame-capture", runId);
      const pngPath = path.join(frameDir, "frame.png");
      await fs.mkdir(frameDir, { recursive: true });
      await fs.writeFile(pngPath, png);
      const frame: GameWindowFrameCapturePayload["frame"] = {
        capturedAt: new Date().toISOString(),
        width: captureResult.width ?? maxWidth,
        height: captureResult.height ?? maxHeight,
        sizeBytes: png.byteLength,
        mimeType: "image/png",
        sha256,
        pngPath,
        previewDataUrl: captureResult.previewPngBase64
          ? `data:image/png;base64,${captureResult.previewPngBase64}`
          : null,
        previewWidth: captureResult.previewWidth ?? null,
        previewHeight: captureResult.previewHeight ?? null,
        previewSizeBytes: captureResult.previewSizeBytes ?? null
      };
      const note =
        captureResult.note ||
        "Captured one bounded PNG still through the desktop capture layer. Continuous streaming and input injection remain separate planned gates.";
      const { payload, artifactPath } = await writeFrameArtifact(
        "captured",
        {
          status: "captured",
          method: "electron-desktop-capturer",
          sourceHint: planPayload.capture.sourceHint,
          sourceId: captureResult.sourceId,
          sourceName: captureResult.sourceName,
          matchedBy: captureResult.matchedBy,
          sourceCount: captureResult.sourceCount,
          note
        },
        frame,
        "Read-only still-frame capture. No input was sent and no continuous stream remains open."
      );
      emitProgress("running", 82, "Game-window still-frame artifact ready.", pngPath);
      return {
        summary: `Captured a ${frame.width}x${frame.height} BEA window still frame.`,
        payloadSchema: "game-window-frame-capture.v1",
        details: buildDetails(payload, artifactPath)
      };
    }
    case "game.captureWindowSequence": {
      emitProgress("running", 18, "Planning managed BEA window before bounded frame sequence.");
      const frameCount = parseFrameSequenceCount(inputs.frameCount);
      const intervalMs = parseFrameSequenceInterval(inputs.intervalMs);
      const maxWidth = parseCaptureDimensionInput(inputs.maxWidth, "maxWidth", 960, 160, 1280);
      const maxHeight = parseCaptureDimensionInput(inputs.maxHeight, "maxHeight", 540, 120, 720);
      const planResult = await executeJob(
        appPath,
        artifactRoot,
        "game.planWindowCapture",
        inputs,
        emitProgress,
        signal,
        runId,
        capabilities
      );
      const planArtifactPath = planResult.details.find((detail) => detail.label === "Plan artifact")?.value ?? null;
      if (!planArtifactPath) {
        throw new Error("Window-capture plan did not return an artifact path.");
      }
      const planPayload = JSON.parse(await fs.readFile(planArtifactPath, "utf8")) as GameWindowCapturePlanPayload;
      const sequenceDir = path.join(path.resolve(artifactRoot), "artifacts", "game-window-frame-sequence", runId);
      const frameDir = path.join(sequenceDir, "frames");
      await fs.mkdir(frameDir, { recursive: true });
      const frames: GameWindowFrameSequencePayload["frames"] = [];

      if (planPayload.status === "ready" && planPayload.selectedWindow) {
        if (!capabilities.captureGameWindowFrame) {
          throw new Error("Desktop capture capability is not available in this Electron context.");
        }
        for (let index = 0; index < frameCount; index++) {
          if (signal.aborted) {
            throw new JobCancelledError();
          }
          if (index > 0 && intervalMs > 0) {
            await delay(intervalMs, signal);
          }
          emitProgress("running", 35 + Math.floor((index / frameCount) * 45), `Capturing frame ${index + 1} of ${frameCount}.`);
          const captureResult = await capabilities.captureGameWindowFrame({
            sourceHint: planPayload.capture.sourceHint,
            title: planPayload.selectedWindow.title,
            hwndHex: planPayload.selectedWindow.hwndHex,
            processId: planPayload.selectedWindow.processId,
            maxWidth,
            maxHeight
          });
          if (captureResult.status !== "captured" || !captureResult.pngBase64) {
            frames.push({
              index,
              status: captureResult.status,
              capturedAt: new Date().toISOString(),
              pngPath: null,
              width: null,
              height: null,
              sizeBytes: null,
              sha256: null,
              sourceId: captureResult.sourceId,
              sourceName: captureResult.sourceName,
              previewDataUrl: null
            });
            continue;
          }
          const frameBuffer = Buffer.from(captureResult.pngBase64, "base64");
          const pngPath = path.join(frameDir, `frame-${String(index + 1).padStart(3, "0")}.png`);
          await fs.writeFile(pngPath, frameBuffer);
          frames.push({
            index,
            status: "captured",
            capturedAt: new Date().toISOString(),
            pngPath,
            width: captureResult.width ?? null,
            height: captureResult.height ?? null,
            sizeBytes: captureResult.sizeBytes ?? frameBuffer.byteLength,
            sha256: createHash("sha256").update(frameBuffer).digest("hex"),
            sourceId: captureResult.sourceId,
            sourceName: captureResult.sourceName,
            previewDataUrl: captureResult.previewPngBase64 ? `data:image/png;base64,${captureResult.previewPngBase64}` : null
          });
        }
      }

      const capturedCount = frames.filter((frame) => frame.status === "captured").length;
      const status: GameWindowFrameSequencePayload["status"] =
        planPayload.status !== "ready"
          ? planPayload.status
          : capturedCount === frameCount
            ? "captured"
            : capturedCount > 0
              ? "partial"
              : "capture-unavailable";
      const payload: GameWindowFrameSequencePayload = {
        schemaVersion: "game-window-frame-sequence.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        processName: planPayload.processName,
        targetRunId: planPayload.targetRunId,
        status,
        selectedWindow: planPayload.selectedWindow,
        requested: {
          frameCount,
          intervalMs,
          maxWidth,
          maxHeight
        },
        capturedCount,
        frames,
        input: {
          status: "available",
          method: "scoped-window-input",
          note: "Use game.planWindowInput and armed game.sendWindowInput between bounded frame-sequence observations."
        },
        artifact: {
          kind: "read-only",
          mutation: false,
          schemaVersion: "game-window-frame-sequence.v1",
          note: "Bounded frame sequence. No live stream remains open and no input was sent."
        }
      };
      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "game-window-frame-sequence",
        runId,
        "sequence.json",
        payload as unknown as Record<string, unknown>
      );
      emitProgress("running", 86, "Game-window frame sequence artifact ready.", artifactPath);
      return {
        summary: `Captured ${capturedCount}/${frameCount} bounded BEA window frames.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Target run", value: payload.targetRunId ?? "none" },
          { label: "Process", value: `${payload.processName} (game)` },
          { label: "Process ID", value: payload.selectedWindow ? String(payload.selectedWindow.processId) : "none" },
          { label: "Sequence status", value: payload.status },
          { label: "Captured frames", value: `${capturedCount}/${frameCount}` },
          { label: "Interval", value: `${intervalMs} ms` },
          { label: "Window", value: payload.selectedWindow ? payload.selectedWindow.title || payload.selectedWindow.hwndHex : "none" },
          { label: "Window handle", value: payload.selectedWindow?.hwndHex ?? "none" },
          { label: "Frame directory", value: frameDir },
          { label: "First frame preview data URL", value: frames.find((frame) => frame.previewDataUrl)?.previewDataUrl ?? "none" },
          { label: "Sequence artifact", value: artifactPath }
        ]
      };
    }
    case "game.planWindowCapture": {
      emitProgress("running", 25, "Resolving managed game process and capture helper.");
      const repoRoot = await resolveJobRepoRoot(appPath);
      const helperPath = path.join(repoRoot, "tools", "list_game_windows.ps1");
      const requestedRunId = optionalStringInput(inputs.targetRunId, "targetRunId");
      const requestedProcessId = optionalProcessIdInput(inputs.processId, "processId");
      const processName = optionalStringInput(inputs.processName, "processName") ?? "BEA.exe";
      if (processName.toLowerCase() !== "bea.exe") {
        throw new JobRejectedError("Game window capture planning is restricted to BEA.exe.");
      }
      const registry = await refreshManagedProcessRegistry(artifactRoot);
      const target = selectManagedProcessTarget(
        registry,
        requestedRunId,
        requestedProcessId,
        "game",
        false,
        "No managed game process is available for capture planning."
      );
      if (process.platform !== "win32") {
        const payload: GameWindowCapturePlanPayload = {
          schemaVersion: "game-window-capture-plan.v1",
          generatedAt: new Date().toISOString(),
          mutation: false,
          processName,
          targetRunId: target.runId,
          status: "unsupported",
          counts: {
            candidates: 0,
            visible: 0,
            minimized: 0
          },
          selectedWindow: null,
          windows: [],
          capture: {
            status: "unsupported",
            method: "electron-desktop-capturer",
            sourceHint: null,
            note: "Game-window capture planning currently requires Windows window enumeration."
          },
          input: {
            status: "planned",
            method: "scoped-window-input",
            note: "Scoped keyboard input is available through game.planWindowInput and explicitly armed game.sendWindowInput."
          },
          artifact: {
            kind: "read-only",
            mutation: false,
            schemaVersion: "game-window-capture-plan.v1",
            note: "Read-only window scan and capture plan. No desktop stream was opened and no input was sent."
          }
        };
        const artifactPath = await writePlanArtifact(
          artifactRoot,
          "game-window-capture-plan",
          runId,
          "plan.json",
          payload as unknown as Record<string, unknown>
        );
        emitProgress("running", 80, "Game-window capture planning is unsupported on this platform.", artifactPath);
        return {
          summary: "Game-window capture planning currently requires Windows window enumeration.",
          payloadSchema: "game-window-capture-plan.v1",
          details: [
            { label: "Target run", value: target.runId },
            { label: "Process", value: `${target.processName} (${target.kind})` },
            { label: "Process ID", value: String(target.processId) },
            { label: "Capture status", value: "unsupported" },
            { label: "Candidates", value: "0" },
            { label: "Selected window", value: "none" },
            { label: "Capture source", value: "none" },
            { label: "Input status", value: "planned" },
            { label: "Plan artifact", value: artifactPath },
            { label: "stderr", value: "none" }
          ]
        };
      }
      emitProgress("running", 45, "Scanning top-level windows for the recorded BEA process.", `PID ${target.processId}`);
      await fs.access(helperPath);
      const result = await runAllowlistedProcess(
        "powershell.exe",
        [
          "-NoProfile",
          "-ExecutionPolicy",
          "Bypass",
          "-File",
          helperPath,
          "-ProcessName",
          processName,
          "-Limit",
          "20"
        ],
        repoRoot,
        signal
      );
      const helperPayload = parseJsonProcessStdout(result.stdout) as {
        schemaVersion?: string;
        status?: GameWindowCapturePlanPayload["status"];
        windows?: GameWindowCapturePlanPayload["windows"];
      };
      if (helperPayload.schemaVersion !== "game-window-scan-helper.v1") {
        throw new Error(`Unexpected game-window scan helper schema: ${helperPayload.schemaVersion}`);
      }
      const windows = (helperPayload.windows ?? []).filter((window) => window.processId === target.processId);
      const selectedWindow =
        windows.length === 1 && windows[0] && !windows[0].minimized && windows[0].visible ? windows[0] : null;
      const status: GameWindowCapturePlanPayload["status"] =
        process.platform !== "win32"
          ? "unsupported"
          : windows.length === 0
            ? "no-window"
            : windows.length > 1
              ? "multiple-candidates"
              : selectedWindow
                ? "ready"
                : "no-window";
      const payload: GameWindowCapturePlanPayload = {
        schemaVersion: "game-window-capture-plan.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        processName,
        targetRunId: target.runId,
        status,
        counts: {
          candidates: windows.length,
          visible: windows.filter((window) => window.visible).length,
          minimized: windows.filter((window) => window.minimized).length
        },
        selectedWindow,
        windows,
        capture: {
          status,
          method: "electron-desktop-capturer",
          sourceHint: selectedWindow?.captureSourceHint ?? null,
          note:
            status === "ready"
              ? "A BEA window candidate is available for a future desktop capture stream."
              : "No capture stream was opened. The next step requires a visible non-minimized BEA window candidate."
        },
        input: {
          status: "planned",
          method: "scoped-window-input",
          note: "Scoped keyboard input is available through game.planWindowInput and explicitly armed game.sendWindowInput."
        },
        artifact: {
          kind: "read-only",
          mutation: false,
          schemaVersion: "game-window-capture-plan.v1",
          note: "Read-only window scan and capture plan. No desktop stream was opened and no input was sent."
        }
      };
      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "game-window-capture-plan",
        runId,
        "plan.json",
        payload as unknown as Record<string, unknown>
      );
      emitProgress("running", 80, "Game-window capture plan artifact ready.", artifactPath);
      return {
        summary:
          status === "ready"
            ? `Found BEA window candidate for managed PID ${target.processId}.`
            : `No ready BEA window candidate for managed PID ${target.processId}: ${status}.`,
        payloadSchema: "game-window-capture-plan.v1",
        details: [
          { label: "Target run", value: target.runId },
          { label: "Process", value: `${target.processName} (${target.kind})` },
          { label: "Process ID", value: String(target.processId) },
          { label: "Capture status", value: status },
          { label: "Candidates", value: String(payload.counts.candidates) },
          { label: "Selected window", value: selectedWindow ? selectedWindow.title || selectedWindow.hwndHex : "none" },
          { label: "Window handle", value: selectedWindow?.hwndHex ?? "none" },
          { label: "Capture source", value: payload.capture.sourceHint ?? "none" },
          { label: "Input status", value: "planned" },
          { label: "Plan artifact", value: artifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "game.planWindowInput":
    case "game.sendWindowInput": {
      const sendingInput = definitionId === "game.sendWindowInput";
      if (sendingInput) {
        requireArmPhrase(inputs.armPhrase, "SEND GAME INPUT", "game window input");
        requireTrueInput(inputs.acceptsWindowInput, "acceptsWindowInput", "game window input");
      }
      emitProgress("running", 24, "Resolving managed game process and input helper.");
      const repoRoot = await resolveJobRepoRoot(appPath);
      const helperPath = path.join(repoRoot, "tools", "send_game_window_input.ps1");
      const requestedRunId = optionalStringInput(inputs.targetRunId, "targetRunId");
      const requestedProcessId = optionalProcessIdInput(inputs.processId, "processId");
      const processName = optionalStringInput(inputs.processName, "processName") ?? "BEA.exe";
      if (processName.toLowerCase() !== "bea.exe") {
        throw new JobRejectedError("Game window input is restricted to BEA.exe.");
      }
      const sequence = stringInput(inputs.sequence, "sequence");
      const stepDelayMs = parseInputStepDelay(inputs.stepDelayMs);
      const registry = await refreshManagedProcessRegistry(artifactRoot);
      const target = selectManagedProcessTarget(
        registry,
        requestedRunId,
        requestedProcessId,
        "game",
        false,
        "No running managed game process is available for scoped input."
      );
      await fs.access(helperPath);
      const hwndHex = optionalStringInput(inputs.hwndHex, "hwndHex");
      emitProgress(
        "running",
        sendingInput ? 45 : 48,
        sendingInput ? "Sending allowlisted scoped keyboard input." : "Planning allowlisted scoped keyboard input.",
        `PID ${target.processId}`
      );
      const args = [
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        helperPath,
        "-ProcessName",
        processName,
        "-ProcessId",
        String(target.processId),
        "-Sequence",
        sequence,
        "-StepDelayMs",
        String(stepDelayMs)
      ];
      if (hwndHex) {
        args.push("-HwndHex", hwndHex);
      }
      if (!sendingInput) {
        args.push("-PrintOnly");
      }
      const result = await runAllowlistedProcess("powershell.exe", args, repoRoot, signal);
      const helperPayload = parseJsonProcessStdout(result.stdout) as Partial<GameWindowInputPayload> & {
        schemaVersion?: string;
        status?: GameWindowInputPayload["status"];
      };
      if (helperPayload.schemaVersion !== "game-window-input.v1") {
        throw new Error(`Unexpected game-window input helper schema: ${helperPayload.schemaVersion}`);
      }
      const payload: GameWindowInputPayload = {
        schemaVersion: "game-window-input.v1",
        generatedAt: helperPayload.generatedAt ?? new Date().toISOString(),
        mutation: false,
        processName: helperPayload.processName ?? processName,
        processId: helperPayload.processId ?? target.processId,
        hwndHex: helperPayload.hwndHex ?? hwndHex ?? null,
        status: helperPayload.status ?? (sendingInput ? "sent" : "ready"),
        plannedOnly: helperPayload.plannedOnly ?? !sendingInput,
        focused: helperPayload.focused,
        actionCount: helperPayload.actionCount ?? 0,
        keyEventsSent: helperPayload.keyEventsSent,
        actions: helperPayload.actions ?? [],
        selectedWindow: helperPayload.selectedWindow ?? null,
        note:
          helperPayload.note ??
          (sendingInput
            ? "Sent scoped keyboard input only to a managed BEA.exe window."
            : "Planned scoped keyboard input only. No input was sent."),
        artifact: {
          kind: sendingInput ? "external-process" : "read-only",
          mutation: false,
          schemaVersion: "game-window-input.v1",
          note: sendingInput
            ? "Armed scoped keyboard input through the allowlisted helper. Renderer did not provide a raw command."
            : "Read-only scoped input plan. No input was sent."
        }
      };
      const artifactPath = await writePlanArtifact(
        artifactRoot,
        sendingInput ? "game-window-input" : "game-window-input-plan",
        runId,
        sendingInput ? "input.json" : "plan.json",
        payload as unknown as Record<string, unknown>
      );
      emitProgress("running", 82, "Game-window input artifact ready.", artifactPath);
      return {
        summary: sendingInput && payload.status === "sent"
          ? `Sent ${payload.actionCount} scoped input actions to managed BEA.exe PID ${target.processId}.`
          : `Planned ${payload.actionCount} scoped input actions for managed BEA.exe PID ${target.processId}.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Target run", value: target.runId },
          { label: "Process", value: `${target.processName} (${target.kind})` },
          { label: "Process ID", value: String(target.processId) },
          { label: "Window handle", value: payload.hwndHex ?? "none" },
          { label: "Input status", value: payload.status },
          { label: "Planned only", value: payload.plannedOnly ? "yes" : "no" },
          { label: "Actions", value: String(payload.actionCount) },
          { label: "Key events sent", value: String(payload.keyEventsSent ?? 0) },
          { label: "Focused", value: typeof payload.focused === "boolean" ? (payload.focused ? "yes" : "no") : "n/a" },
          { label: "Sequence", value: sequence },
          { label: sendingInput ? "Input artifact" : "Input plan artifact", value: artifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "game.prepareSafeProfile": {
      requireArmPhrase(inputs.armPhrase, "COPY GAME PROFILE", "safe profile preparation");
      requireTrueInput(inputs.acceptsLocalCopy, "acceptsLocalCopy", "safe profile preparation");
      emitProgress("running", 25, "Inspecting source game profile before copy.");
      const sourceGameRoot = typeof inputs.sourceGameRoot === "string" && inputs.sourceGameRoot.trim()
        ? inputs.sourceGameRoot
        : typeof inputs.gameRoot === "string" && inputs.gameRoot.trim()
          ? inputs.gameRoot
          : null;
      const profile = sourceGameRoot
        ? await inspectGameHarnessProfilePath(appPath, sourceGameRoot)
        : await getGameHarnessProfile(appPath, artifactRoot);
      if (!profile.ready) {
        throw new JobRejectedError("Source game profile is missing required files; copied profile was not created.");
      }

      const repoRoot = await resolveJobRepoRoot(appPath);
      const helperPath = path.join(repoRoot, "tools", "prepare_game_profile.ps1");
      await fs.access(helperPath);
      const outputRoot = path.join(path.resolve(artifactRoot), "game-profiles");
      const profileName = sanitizeProfileName(optionalStringInput(inputs.profileName, "profileName") ?? `bea-${runId}`);
      emitProgress("running", 50, "Copying validated game profile through allowlisted helper.", outputRoot);
      const result = await runAllowlistedProcess(
        process.platform === "win32" ? "powershell.exe" : "pwsh",
        [
          "-NoProfile",
          "-ExecutionPolicy",
          "Bypass",
          "-File",
          helperPath,
          "-SourceGameRoot",
          profile.gameRoot,
          "-OutputRoot",
          outputRoot,
          "-ProfileName",
          profileName
        ],
        repoRoot,
        signal
      );
      const payload = parseJsonProcessStdout(result.stdout) as {
        schemaVersion?: string;
        mutation?: boolean;
        targetGameRoot?: string;
        entries?: Array<{ name: string }>;
      };
      if (payload.schemaVersion !== "game-profile-prepare.v1") {
        throw new Error(`Unexpected safe-profile payload schema: ${payload.schemaVersion}`);
      }
      if (!payload.targetGameRoot) {
        throw new Error("Safe-profile helper did not return a target game root.");
      }
      assertCopiedSafeProfile(payload.targetGameRoot, profile.repoRoot, "Prepared game profile");
      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "game-profile-prepare",
        runId,
        "prepare.json",
        payload as unknown as Record<string, unknown>
      );
      emitProgress("running", 82, "Copied game profile artifact ready.", artifactPath);

      return {
        summary: `Prepared copied game profile at ${payload.targetGameRoot}.`,
        payloadSchema: "game-profile-prepare.v1",
        details: [
          { label: "Source game root", value: profile.gameRoot },
          { label: "Target game root", value: payload.targetGameRoot },
          { label: "Profile name", value: profileName },
          { label: "Entries copied", value: String(payload.entries?.length ?? 0) },
          { label: "Prepare artifact", value: artifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "game.planLaunchProfile": {
      emitProgress("running", 30, "Inspecting game profile before launch planning.");
      const gameRoot = typeof inputs.gameRoot === "string" && inputs.gameRoot.trim() ? inputs.gameRoot : null;
      const profile = gameRoot
        ? await inspectGameHarnessProfilePath(appPath, gameRoot)
        : await getGameHarnessProfile(appPath, artifactRoot);
      const args = parseLaunchArgs(inputs.args);
      if (!profile.ready) {
        throw new Error("Game profile is missing required files; launch plan was not created.");
      }
      emitProgress("running", 55, "Verifying executable specimen before launch planning.", profile.executablePath);
      const verification = await verifyExecutablePath(profile.executablePath, appPath);
      const plan = {
        schemaVersion: "game-launch-plan.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        gameRoot: profile.gameRoot,
        executablePath: profile.executablePath,
        workingDirectory: profile.workingDirectory,
        args,
        commandPreview: buildPowerShellStartProcessPreview(profile.executablePath, profile.workingDirectory, args),
        sha256: verification.sha256,
        knownRetailSteamHash: verification.isKnownRetailSteamHash,
        profileSource: profile.profileSource,
        note: "Read-only launch plan. No game process was started."
      };
      const planPath = await writePlanArtifact(artifactRoot, "game-launch-plan", runId, "plan.json", plan);
      emitProgress("running", 80, "Game launch plan artifact ready.", planPath);

      return {
        summary: `Planned verified game launch for ${profile.executablePath}.`,
        payloadSchema: "game-launch-plan.v1",
        details: [
          { label: "Executable", value: profile.executablePath },
          { label: "Working directory", value: profile.workingDirectory },
          { label: "Arguments", value: args.join(" ") || "none" },
          { label: "Known Steam hash", value: verification.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Command preview", value: plan.commandPreview },
          { label: "Plan artifact", value: planPath }
        ]
      };
    }
    case "game.launchProfile": {
      requireArmPhrase(inputs.armPhrase, "LAUNCH BEA", "game launch");
      requireTrueInput(inputs.acceptsProfileWrites, "acceptsProfileWrites", "game launch");
      emitProgress("running", 25, "Inspecting armed game profile.");
      const gameRoot = typeof inputs.gameRoot === "string" && inputs.gameRoot.trim() ? inputs.gameRoot : null;
      const profile = gameRoot
        ? await inspectGameHarnessProfilePath(appPath, gameRoot)
        : await getGameHarnessProfile(appPath, artifactRoot);
      if (!profile.ready) {
        throw new JobRejectedError("Game profile is missing required files; launch was not started.");
      }
      assertCopiedSafeProfile(profile.gameRoot, profile.repoRoot, "Game launch");

      const args = parseLaunchArgs(inputs.args);
      const repoRoot = await resolveJobRepoRoot(appPath);
      const launcherPath = path.join(repoRoot, "tools", "start_game_profile.ps1");
      await fs.access(launcherPath);
      emitProgress("running", 45, "Verifying executable specimen before launch.", profile.executablePath);
      const verification = await verifyExecutablePath(profile.executablePath, appPath);
      emitProgress("running", 65, "Starting allowlisted game launcher.", launcherPath);
      const result = await runAllowlistedProcess(
        process.platform === "win32" ? "powershell.exe" : "pwsh",
        [
          "-NoProfile",
          "-ExecutionPolicy",
          "Bypass",
          "-File",
          launcherPath,
          "-GameRoot",
          profile.gameRoot,
          "-Arguments",
          args.join(" ")
        ],
        repoRoot,
        signal
      );
      const launched = parseJsonProcessStdout(result.stdout) as {
        processId?: number;
        executablePath?: string;
        workingDirectory?: string;
        commandPreview?: string;
      };
      const payload = {
        schemaVersion: "game-launch.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        armed: true,
        gameRoot: profile.gameRoot,
        executablePath: profile.executablePath,
        workingDirectory: profile.workingDirectory,
        args,
        processId: launched.processId ?? null,
        sha256: verification.sha256,
        knownRetailSteamHash: verification.isKnownRetailSteamHash,
        profileSource: profile.profileSource,
        commandPreview:
          launched.commandPreview ?? buildPowerShellStartProcessPreview(profile.executablePath, profile.workingDirectory, args),
        stdout: tailText(result.stdout),
        stderr: tailText(result.stderr),
        note: "Armed game launch through the allowlisted helper. Renderer did not provide a raw command."
      };
      const artifactPath = await writePlanArtifact(artifactRoot, "game-launch", runId, "launch.json", payload);
      if (payload.processId) {
        await recordManagedProcess(artifactRoot, {
          runId,
          definitionId,
          kind: "game",
          processId: payload.processId,
          processName: "BEA.exe",
          startedAt: payload.generatedAt,
          gameRoot: profile.gameRoot,
          executablePath: profile.executablePath,
          workingDirectory: profile.workingDirectory,
          sourceArtifactPath: artifactPath,
          commandPreview: payload.commandPreview
        });
      }
      emitProgress("running", 82, "Game launch artifact ready.", artifactPath);

      return {
        summary: `Started BEA.exe${payload.processId ? ` as PID ${payload.processId}` : ""} from a copied/safe profile.`,
        payloadSchema: "game-launch.v1",
        details: [
          { label: "Executable", value: profile.executablePath },
          { label: "Working directory", value: profile.workingDirectory },
          { label: "Arguments", value: args.join(" ") || "none" },
          { label: "Process ID", value: payload.processId ? String(payload.processId) : "unknown" },
          { label: "Known Steam hash", value: verification.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Safe profile", value: "outside repo root" },
          { label: "Launch artifact", value: artifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "debug.resolveCdb": {
      emitProgress("running", 30, "Checking debugger readiness.");
      const readiness = await getDebugReadiness(appPath);
      const resolver = readiness.paths.find((item) => item.label === "CDB path resolver");
      if (!resolver?.exists) {
        throw new Error("CDB path resolver script is not available.");
      }

      emitProgress("running", 55, "Running allowlisted CDB path resolver.", resolver.path);
      const result = await runAllowlistedProcess(
        process.platform === "win32" ? "powershell.exe" : "pwsh",
        ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", resolver.path, "-AsLiteral"],
        readiness.repoRoot,
        signal
      );
      const cdbPath = firstNonEmptyLine(result.stdout);
      if (!cdbPath) {
        throw new Error("CDB resolver completed without printing a debugger path.");
      }

      emitProgress("running", 80, "CDB path resolved.", cdbPath);
      return {
        summary: `Resolved cdb.exe at ${cdbPath}.`,
        payloadSchema: "debug-cdb-resolve.v1",
        details: [
          { label: "Helper", value: resolver.path },
          { label: "CDB path", value: cdbPath },
          { label: "Exit code", value: String(result.exitCode) },
          { label: "stderr", value: result.stderr.trim() || "none" }
        ]
      };
    }
    case "debug.planProbeSession": {
      emitProgress("running", 25, "Checking debugger and game profile readiness.");
      const [readiness, profile] = await Promise.all([
        getDebugReadiness(appPath),
        typeof inputs.gameRoot === "string" && inputs.gameRoot.trim()
          ? inspectGameHarnessProfilePath(appPath, inputs.gameRoot)
          : getGameHarnessProfile(appPath, artifactRoot)
      ]);
      const server = readiness.paths.find((item) => item.label === "CDB server launcher");
      const connector = readiness.paths.find((item) => item.label === "CDB client connector");
      const tail = readiness.paths.find((item) => item.label === "WinDbg tail helper");
      if (!server?.exists || !connector?.exists) {
        throw new Error("CDB probe helpers are not available.");
      }
      if (!profile.ready) {
        throw new Error("Game profile is missing required files; debug probe plan was not created.");
      }

      const probe = selectProbeScript(readiness.probeScripts, optionalStringInput(inputs.probeId, "probeId"));
      const port = parsePort(inputs.port);
      const sessionPassword = buildCdbSessionPassword(runId);
      const logPath = path.join(path.resolve(artifactRoot), "artifacts", "debug-probe-plan", runId, "cdb.log");
      const planDir = path.dirname(logPath);
      await fs.mkdir(planDir, { recursive: true });
      emitProgress("running", 55, "Verifying executable specimen before debug probe planning.", profile.executablePath);
      const verification = await verifyExecutablePath(profile.executablePath, appPath);
      const plan = {
        schemaVersion: "debug-probe-plan.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        processName: "BEA.exe",
        gameRoot: profile.gameRoot,
        executablePath: profile.executablePath,
        probeId: probe.label,
        commandFile: probe.path,
        port,
        password: sessionPassword,
        logPath,
        knownRetailSteamHash: verification.isKnownRetailSteamHash,
        serverCommandPreview: buildPowerShellScriptPreview(server.path, {
          ProcessName: "BEA.exe",
          LogPath: logPath,
          Port: String(port),
          Password: sessionPassword,
          CommandFile: probe.path
        }),
        clientCommandPreview: buildPowerShellScriptPreview(connector.path, {
          Server: "127.0.0.1",
          Port: String(port),
          Password: sessionPassword
        }),
        tailCommandPreview: tail?.exists ? `python "${tail.path}" "${logPath}"` : "tail helper unavailable",
        note: "Read-only debug probe plan. No game, debugger, server, or client process was started."
      };
      const planPath = await writePlanArtifact(artifactRoot, "debug-probe-plan", runId, "plan.json", plan);
      emitProgress("running", 80, "Debug probe plan artifact ready.", planPath);

      return {
        summary: `Planned CDB probe ${probe.label} for BEA.exe on port ${port}.`,
        payloadSchema: "debug-probe-plan.v1",
        details: [
          { label: "Probe", value: probe.label },
          { label: "Command file", value: probe.path },
          { label: "Executable", value: profile.executablePath },
          { label: "Port", value: String(port) },
          { label: "Log path", value: logPath },
          { label: "Known Steam hash", value: verification.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Server command", value: plan.serverCommandPreview },
          { label: "Client command", value: plan.clientCommandPreview },
          { label: "Plan artifact", value: planPath }
        ]
      };
    }
    case "debug.startProbeServer": {
      requireArmPhrase(inputs.armPhrase, "ATTACH CDB", "CDB probe server");
      requireTrueInput(inputs.acceptsRuntimeAttach, "acceptsRuntimeAttach", "CDB probe server");
      emitProgress("running", 25, "Checking armed debugger and game profile readiness.");
      const [readiness, profile] = await Promise.all([
        getDebugReadiness(appPath),
        typeof inputs.gameRoot === "string" && inputs.gameRoot.trim()
          ? inspectGameHarnessProfilePath(appPath, inputs.gameRoot)
          : getGameHarnessProfile(appPath, artifactRoot)
      ]);
      const server = readiness.paths.find((item) => item.label === "CDB server launcher");
      if (!server?.exists) {
        throw new Error("CDB server launcher script is not available.");
      }
      if (!profile.ready) {
        throw new JobRejectedError("Game profile is missing required files; CDB attach was not started.");
      }
      assertCopiedSafeProfile(profile.gameRoot, profile.repoRoot, "CDB attach");

      const processName = optionalStringInput(inputs.processName, "processName") ?? "BEA.exe";
      if (processName.toLowerCase() !== "bea.exe") {
        throw new JobRejectedError("CDB attach is restricted to BEA.exe.");
      }
      const probe = selectProbeScript(readiness.probeScripts, optionalStringInput(inputs.probeId, "probeId"));
      const port = parsePort(inputs.port);
      const sessionPassword = buildCdbSessionPassword(runId);
      const sessionDir = path.join(path.resolve(artifactRoot), "artifacts", "debug-session", runId);
      const logPath = path.join(sessionDir, "cdb.log");
      await fs.mkdir(sessionDir, { recursive: true });
      emitProgress("running", 48, "Verifying executable specimen before CDB attach.", profile.executablePath);
      const verification = await verifyExecutablePath(profile.executablePath, appPath);
      emitProgress("running", 68, "Starting allowlisted CDB server attach helper.", server.path);
      const result = await runAllowlistedProcess(
        process.platform === "win32" ? "powershell.exe" : "pwsh",
        [
          "-NoProfile",
          "-ExecutionPolicy",
          "Bypass",
          "-File",
          server.path,
          "-ProcessName",
          processName,
          "-LogPath",
          logPath,
          "-Port",
          String(port),
          "-Password",
          sessionPassword,
          "-CommandFile",
          probe.path
        ],
        readiness.repoRoot,
        signal
      );
      const pidMatch = result.stdout.match(/CDB PID:\s*(\d+)/i);
      const payload = {
        schemaVersion: "debug-session.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        armed: true,
        processName,
        gameRoot: profile.gameRoot,
        executablePath: profile.executablePath,
        probeId: probe.label,
        commandFile: probe.path,
        port,
        password: sessionPassword,
        logPath,
        cdbProcessId: pidMatch ? Number.parseInt(pidMatch[1], 10) : null,
        knownRetailSteamHash: verification.isKnownRetailSteamHash,
        serverCommandPreview: buildPowerShellScriptPreview(server.path, {
          ProcessName: processName,
          LogPath: logPath,
          Port: String(port),
          Password: sessionPassword,
          CommandFile: probe.path
        }),
        stdout: tailText(result.stdout),
        stderr: tailText(result.stderr),
        note: "Armed CDB attach-server start through the allowlisted helper. Renderer did not provide a raw command."
      };
      const artifactPath = await writePlanArtifact(artifactRoot, "debug-session", runId, "session.json", payload);
      if (payload.cdbProcessId) {
        await recordManagedProcess(artifactRoot, {
          runId,
          definitionId,
          kind: "debugger",
          processId: payload.cdbProcessId,
          processName: "cdb.exe",
          startedAt: payload.generatedAt,
          gameRoot: profile.gameRoot,
          executablePath: profile.executablePath,
          port,
          logPath,
          sourceArtifactPath: artifactPath,
          commandPreview: payload.serverCommandPreview
        });
      }
      emitProgress("running", 82, "CDB session artifact ready.", artifactPath);

      return {
        summary: `Started CDB attach server for ${processName} on port ${port}.`,
        payloadSchema: "debug-session.v1",
        details: [
          { label: "Probe", value: probe.label },
          { label: "Process", value: processName },
          { label: "CDB PID", value: payload.cdbProcessId ? String(payload.cdbProcessId) : "unknown" },
          { label: "Log path", value: logPath },
          { label: "Port", value: String(port) },
          { label: "Safe profile", value: "outside repo root" },
          { label: "Known Steam hash", value: verification.isKnownRetailSteamHash ? "yes" : "no" },
          { label: "Session artifact", value: artifactPath },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "runtime.listManagedProcesses": {
      emitProgress("running", 35, "Reading managed process registry.");
      const payload = await buildManagedProcessRegistryPayload(artifactRoot);
      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "managed-process-registry",
        runId,
        "processes.json",
        payload as unknown as Record<string, unknown>
      );
      const latest = payload.processes[0];
      emitProgress("running", 80, "Managed process registry artifact ready.", artifactPath);
      return {
        summary: `Found ${payload.counts.total} managed runtime process record${payload.counts.total === 1 ? "" : "s"}.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Managed processes", value: String(payload.counts.total) },
          { label: "Running", value: String(payload.counts.running) },
          { label: "Exited", value: String(payload.counts.exited) },
          { label: "Stop requested", value: String(payload.counts.stopRequested) },
          { label: "Latest", value: latest ? `${latest.kind} PID ${latest.processId} (${latest.status})` : "none" },
          { label: "Registry artifact", value: artifactPath }
        ]
      };
    }
    case "runtime.tailManagedLog": {
      emitProgress("running", 30, "Resolving managed log target.");
      const registry = await refreshManagedProcessRegistry(artifactRoot);
      const target = selectManagedLogTarget(
        registry,
        optionalStringInput(inputs.targetRunId, "targetRunId"),
        optionalProcessIdInput(inputs.processId, "processId")
      );
      const byteLimit = parseLogTailByteLimit(inputs.byteLimit);
      const logPath = resolveManagedLogPath(artifactRoot, target);
      emitProgress("running", 55, "Reading bounded managed log tail.", logPath);
      const tail = await readBoundedTextTail(logPath, byteLimit);
      const payload: ManagedProcessLogTailPayload = {
        schemaVersion: "managed-process-log-tail.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        target,
        logPath,
        exists: tail.exists,
        requestedBytes: byteLimit,
        fileSizeBytes: tail.fileSizeBytes,
        byteLength: tail.byteLength,
        truncated: tail.truncated,
        lineCount: tail.lineCount,
        text: tail.text,
        artifact: {
          kind: "read-only",
          mutation: false,
          schemaVersion: "managed-process-log-tail.v1",
          note: "Read-only bounded tail of a log path recorded by a managed launch/debug job. The renderer did not provide a raw file path."
        }
      };
      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "managed-process-log-tail",
        runId,
        "tail.json",
        payload as unknown as Record<string, unknown>
      );
      emitProgress("running", 82, "Managed log tail artifact ready.", artifactPath);
      return {
        summary: payload.exists
          ? `Read ${payload.byteLength} bytes from managed ${target.kind} log ${path.basename(logPath)}.`
          : `Managed ${target.kind} log does not exist yet: ${logPath}.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Target run", value: target.runId },
          { label: "Process", value: `${target.processName} (${target.kind})` },
          { label: "Process ID", value: String(target.processId) },
          { label: "Status", value: target.status },
          { label: "Log path", value: logPath },
          { label: "Exists", value: payload.exists ? "yes" : "no" },
          { label: "File size", value: String(payload.fileSizeBytes) },
          { label: "Tail bytes", value: String(payload.byteLength) },
          { label: "Lines", value: String(payload.lineCount) },
          { label: "Truncated", value: payload.truncated ? "yes" : "no" },
          { label: "Tail artifact", value: artifactPath },
          { label: "Tail text", value: tailText(payload.text, 1200) || "empty" }
        ]
      };
    }
    case "runtime.stopManagedProcess": {
      requireArmPhrase(inputs.armPhrase, "STOP PROCESS", "managed process stop");
      requireTrueInput(inputs.acceptsProcessStop, "acceptsProcessStop", "managed process stop");
      emitProgress("running", 30, "Resolving managed process target.");
      const registry = await refreshManagedProcessRegistry(artifactRoot);
      const target = selectManagedProcessTarget(
        registry,
        optionalStringInput(inputs.targetRunId, "targetRunId"),
        optionalProcessIdInput(inputs.processId, "processId")
      );
      const previousStatus = target.status;
      emitProgress("running", 55, "Stopping recorded managed process.", `${target.processName} PID ${target.processId}`);
      const stopped = await requestManagedProcessStop(target);
      const currentStatus: ManagedProcessStatus = await isProcessRunning(target.processId)
        ? stopped
          ? "stop-requested"
          : previousStatus
        : "exited";
      const updated = await updateManagedProcess(artifactRoot, target.runId, target.processId, {
        status: currentStatus,
        lastCheckedAt: new Date().toISOString(),
        stopRequestedAt: stopped ? new Date().toISOString() : target.stopRequestedAt
      });
      const payload: ManagedProcessStopPayload = {
        schemaVersion: "managed-process-stop.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        stopped,
        previousStatus,
        currentStatus,
        target: updated,
        artifact: {
          kind: "external-process",
          mutation: false,
          schemaVersion: "managed-process-stop.v1",
          note: "Stopped only a process recorded by this workbench registry. Renderer did not provide a raw PID command."
        }
      };
      const artifactPath = await writePlanArtifact(
        artifactRoot,
        "managed-process-stop",
        runId,
        "stop.json",
        payload as unknown as Record<string, unknown>
      );
      emitProgress("running", 82, "Managed process stop artifact ready.", artifactPath);
      return {
        summary: stopped
          ? `Stop requested for managed ${target.kind} process PID ${target.processId}.`
          : `Managed ${target.kind} process PID ${target.processId} was already not running.`,
        payloadSchema: payload.schemaVersion,
        details: [
          { label: "Target run", value: target.runId },
          { label: "Process", value: `${target.processName} (${target.kind})` },
          { label: "Process ID", value: String(target.processId) },
          { label: "Previous status", value: previousStatus },
          { label: "Current status", value: currentStatus },
          { label: "Stop requested", value: stopped ? "yes" : "no" },
          { label: "Stop artifact", value: artifactPath }
        ]
      };
    }
    case "ghidra.exportWeakFunctions": {
      const mode = optionalStringInput(inputs.mode, "mode") || "weak";
      if (!["weak", "all"].includes(mode)) {
        throw new Error("Ghidra export mode must be `weak` or `all`.");
      }

      emitProgress("running", 25, "Checking Ghidra headless export readiness.");
      const readiness = await getGhidraReadiness(appPath);
      const runner = readiness.paths.find((item) => item.label === "Headless postscript runner");
      const script = readiness.paths.find((item) => item.label === "ExportWeakFunctionList.java");
      if (!runner?.exists) {
        throw new Error("Ghidra headless postscript runner is not available.");
      }
      if (!script?.exists) {
        throw new Error("ExportWeakFunctionList.java is not available.");
      }

      const exportDir = path.join(path.resolve(artifactRoot), "artifacts", "ghidra-export", runId);
      const outPath = path.join(exportDir, `weak-functions-${mode}.tsv`);
      await fs.mkdir(exportDir, { recursive: true });

      emitProgress("running", 45, "Starting allowlisted Ghidra weak-function export.", mode);
      const result = await runGhidraHeadlessPostscript(readiness.repoRoot, runner.path, outPath, mode, signal);
      emitProgress("running", 80, "Reading exported function list.", outPath);
      const exportSummary = await summarizeTsv(outPath);
      const stats = parseGhidraExportStats(result.stdout);
      emitProgress("running", 88, "Ghidra export artifact ready.", `${exportSummary.rows} rows`);

      return {
        summary: `Exported ${exportSummary.rows} ${mode} function rows with Ghidra headless.`,
        payloadSchema: "ghidra-export.v1",
        details: [
          { label: "Script", value: "ExportWeakFunctionList.java" },
          { label: "Mode", value: mode },
          { label: "Total functions", value: stats.totalFunctions ?? "unknown" },
          { label: "Weak functions", value: stats.weakFunctions ?? "unknown" },
          { label: "Rows", value: String(exportSummary.rows) },
          { label: "Output TSV", value: outPath },
          { label: "Exit code", value: String(result.exitCode) },
          { label: "stdout", value: tailText(result.stdout) || "none" },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "ghidra.exportAddressDecompile": {
      emitProgress("running", 25, "Checking Ghidra decompile export readiness.");
      const readiness = await getGhidraReadiness(appPath);
      const runner = readiness.paths.find((item) => item.label === "Headless postscript runner");
      const script = readiness.paths.find((item) => item.label === "ExportFunctionsByAddressDecompile.java");
      if (!runner?.exists) {
        throw new Error("Ghidra headless postscript runner is not available.");
      }
      if (!script?.exists) {
        throw new Error("ExportFunctionsByAddressDecompile.java is not available.");
      }

      const addresses = parseAddressListInput(inputs.addresses);
      const timeoutSec = parseTimeoutSeconds(inputs.timeoutSec);
      const exportDir = path.join(path.resolve(artifactRoot), "artifacts", "ghidra-decompile", runId);
      const addressListPath = path.join(exportDir, "addresses.txt");
      const outDir = path.join(exportDir, "decompile");
      await fs.mkdir(outDir, { recursive: true });
      await fs.writeFile(addressListPath, `${addresses.join("\n")}\n`, "utf8");

      emitProgress("running", 45, "Starting allowlisted Ghidra address decompile export.", `${addresses.length} addresses`);
      const result = await runGhidraAddressDecompile(
        readiness.repoRoot,
        runner.path,
        addressListPath,
        outDir,
        timeoutSec,
        signal
      );
      const indexPath = path.join(outDir, "index.tsv");
      emitProgress("running", 80, "Reading Ghidra decompile export index.", indexPath);
      const exportSummary = await summarizeGhidraDecompileIndex(indexPath);
      emitProgress(
        "running",
        88,
        "Ghidra decompile export artifact ready.",
        `${exportSummary.ok} OK, ${exportSummary.missing} missing, ${exportSummary.failed} failed`
      );

      return {
        summary: `Exported decompile evidence for ${addresses.length} addresses: ${exportSummary.ok} OK, ${exportSummary.missing} missing, ${exportSummary.failed} failed.`,
        payloadSchema: "ghidra-decompile-export.v1",
        details: [
          { label: "Script", value: "ExportFunctionsByAddressDecompile.java" },
          { label: "Addresses", value: addresses.join(", ") },
          { label: "OK", value: String(exportSummary.ok) },
          { label: "Missing", value: String(exportSummary.missing) },
          { label: "Failed", value: String(exportSummary.failed) },
          { label: "Address list", value: addressListPath },
          { label: "Index TSV", value: indexPath },
          { label: "Output directory", value: outDir },
          { label: "Exit code", value: String(result.exitCode) },
          { label: "stdout", value: tailText(result.stdout) || "none" },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "ghidra.validateRenameMap": {
      emitProgress("running", 25, "Checking Ghidra rename-map dry-run readiness.");
      const readiness = await getGhidraReadiness(appPath);
      const runner = readiness.paths.find((item) => item.label === "Batch rename runner");
      const script = readiness.paths.find((item) => item.label === "GhidraBatchRename.java");
      if (!runner?.exists) {
        throw new Error("Ghidra batch rename runner is not available.");
      }
      if (!script?.exists) {
        throw new Error("GhidraBatchRename.java is not available.");
      }
      const artifactRootPath = path.resolve(artifactRoot);
      const mapPath = path.resolve(stringInput(inputs.mapPath, "mapPath"));
      if (!isInsidePath(artifactRootPath, mapPath)) {
        throw new JobRejectedError("Ghidra rename map must be inside the app artifact root.");
      }
      await fs.access(mapPath);
      emitProgress("running", 45, "Starting allowlisted Ghidra rename-map dry-run.", mapPath);
      const result = await runGhidraBatchRename(readiness.repoRoot, runner.path, mapPath, "dry", signal);
      const dryRunDir = path.join(artifactRootPath, "artifacts", "ghidra-rename-dry-run", runId);
      await fs.mkdir(dryRunDir, { recursive: true });
      const stdoutPath = path.join(dryRunDir, "stdout.txt");
      const stderrPath = path.join(dryRunDir, "stderr.txt");
      await Promise.all([fs.writeFile(stdoutPath, result.stdout, "utf8"), fs.writeFile(stderrPath, result.stderr, "utf8")]);
      const renameReport = parseGhidraBatchRenameReport(result.stdout);
      const saveSucceeded = /REPORT:\s*Save succeeded/i.test(result.stdout);
      const lockException = /LockException/i.test(`${result.stdout}\n${result.stderr}`);
      const applyReady =
        result.exitCode === 0 &&
        saveSucceeded &&
        !lockException &&
        renameReport.summarySeen &&
        renameReport.missing === 0 &&
        renameReport.bad === 0 &&
        renameReport.failed === 0;
      const payload = {
        schemaVersion: "ghidra-rename-dry-run.v1",
        generatedAt: new Date().toISOString(),
        mutation: false,
        mapPath,
        mode: "dry",
        exitCode: result.exitCode,
        stdoutPath,
        stderrPath,
        saveSucceeded,
        lockException,
        renameReport,
        applyReady,
        note: "Headless Ghidra rename dry-run only. No apply mutation was requested by this job."
      };
      const artifactPath = await writePlanArtifact(artifactRoot, "ghidra-rename-dry-run", runId, "dry-run.json", payload);
      emitProgress("running", 82, "Ghidra rename-map dry-run artifact ready.", artifactPath);
      return {
        summary: `Dry-ran Ghidra rename map ${path.basename(mapPath)} with exit code ${result.exitCode}.`,
        payloadSchema: "ghidra-rename-dry-run.v1",
        details: [
          { label: "Runner", value: runner.path },
          { label: "Map", value: mapPath },
          { label: "Mode", value: "dry" },
          { label: "Exit code", value: String(result.exitCode) },
          { label: "Save succeeded", value: payload.saveSucceeded ? "yes" : "no" },
          { label: "Lock exception", value: payload.lockException ? "yes" : "no" },
          { label: "Missing", value: String(renameReport.missing) },
          { label: "Bad", value: String(renameReport.bad) },
          { label: "Failed", value: String(renameReport.failed) },
          { label: "Apply ready", value: applyReady ? "yes" : "no" },
          { label: "stdout", value: stdoutPath },
          { label: "stderr", value: stderrPath },
          { label: "Dry-run artifact", value: artifactPath }
        ]
      };
    }
    case "ghidra.applyRenameMap": {
      requireArmPhrase(inputs.armPhrase, "APPLY GHIDRA RENAME MAP", "Ghidra rename-map apply");
      requireTrueInput(inputs.acceptsGhidraMutation, "acceptsGhidraMutation", "Ghidra rename-map apply");
      emitProgress("running", 22, "Checking Ghidra rename-map apply readiness.");
      const readiness = await getGhidraReadiness(appPath);
      const runner = readiness.paths.find((item) => item.label === "Batch rename runner");
      const script = readiness.paths.find((item) => item.label === "GhidraBatchRename.java");
      if (!runner?.exists) {
        throw new Error("Ghidra batch rename runner is not available.");
      }
      if (!script?.exists) {
        throw new Error("GhidraBatchRename.java is not available.");
      }
      const artifactRootPath = path.resolve(artifactRoot);
      const mapPath = path.resolve(stringInput(inputs.mapPath, "mapPath"));
      const dryRunArtifactPath = path.resolve(stringInput(inputs.dryRunArtifactPath, "dryRunArtifactPath"));
      if (!isInsidePath(artifactRootPath, mapPath)) {
        throw new JobRejectedError("Ghidra rename map must be inside the app artifact root.");
      }
      if (!isInsidePath(artifactRootPath, dryRunArtifactPath)) {
        throw new JobRejectedError("Ghidra rename dry-run artifact must be inside the app artifact root.");
      }
      await fs.access(mapPath);
      const dryRunPayload = JSON.parse(await fs.readFile(dryRunArtifactPath, "utf8")) as {
        schemaVersion?: string;
        mapPath?: string;
        saveSucceeded?: boolean;
        lockException?: boolean;
        applyReady?: boolean;
        renameReport?: ReturnType<typeof parseGhidraBatchRenameReport>;
      };
      if (dryRunPayload.schemaVersion !== "ghidra-rename-dry-run.v1") {
        throw new JobRejectedError("Ghidra rename-map apply requires a ghidra-rename-dry-run.v1 artifact.");
      }
      if (path.resolve(dryRunPayload.mapPath ?? "") !== mapPath) {
        throw new JobRejectedError("Ghidra rename-map apply requires a dry-run artifact for the same map path.");
      }
      if (dryRunPayload.lockException) {
        throw new JobRejectedError("Ghidra rename-map dry-run reported a project lock exception; apply is blocked.");
      }
      if (!dryRunPayload.saveSucceeded) {
        throw new JobRejectedError("Ghidra rename-map dry-run did not report save success; apply is blocked.");
      }
      const dryRunReport = dryRunPayload.renameReport ?? parseGhidraBatchRenameReport("");
      if (
        !dryRunPayload.applyReady ||
        !dryRunReport.summarySeen ||
        dryRunReport.missing > 0 ||
        dryRunReport.bad > 0 ||
        dryRunReport.failed > 0
      ) {
        throw new JobRejectedError(
          `Ghidra rename-map dry-run is not clean: ${dryRunReport.missing} missing, ${dryRunReport.bad} bad, ${dryRunReport.failed} failed.`
        );
      }
      emitProgress("running", 45, "Starting allowlisted Ghidra rename-map apply.", mapPath);
      const result = await runGhidraBatchRename(readiness.repoRoot, runner.path, mapPath, "apply", signal);
      const applyDir = path.join(artifactRootPath, "artifacts", "ghidra-rename-apply", runId);
      await fs.mkdir(applyDir, { recursive: true });
      const stdoutPath = path.join(applyDir, "stdout.txt");
      const stderrPath = path.join(applyDir, "stderr.txt");
      await Promise.all([fs.writeFile(stdoutPath, result.stdout, "utf8"), fs.writeFile(stderrPath, result.stderr, "utf8")]);
      const renameReport = parseGhidraBatchRenameReport(result.stdout);
      const saveSucceeded = /REPORT:\s*Save succeeded/i.test(result.stdout);
      const lockException = /LockException/i.test(`${result.stdout}\n${result.stderr}`);
      const payload = {
        schemaVersion: "ghidra-rename-apply.v1",
        generatedAt: new Date().toISOString(),
        mutation: true,
        mapPath,
        dryRunArtifactPath,
        mode: "apply",
        exitCode: result.exitCode,
        stdoutPath,
        stderrPath,
        saveSucceeded,
        lockException,
        renameReport,
        note: "Headless Ghidra rename-map apply through an explicitly armed typed job."
      };
      const artifactPath = await writePlanArtifact(artifactRoot, "ghidra-rename-apply", runId, "apply.json", payload);
      emitProgress("running", 82, "Ghidra rename-map apply artifact ready.", artifactPath);
      if (result.exitCode !== 0 || lockException || !saveSucceeded || renameReport.bad > 0 || renameReport.failed > 0) {
        throw new Error(
          `Ghidra rename-map apply did not finish cleanly: exit=${result.exitCode}, save=${saveSucceeded ? "yes" : "no"}, lock=${lockException ? "yes" : "no"}, bad=${renameReport.bad}, failed=${renameReport.failed}. Artifact: ${artifactPath}`
        );
      }
      return {
        summary: `Applied Ghidra rename map ${path.basename(mapPath)} with exit code ${result.exitCode}.`,
        payloadSchema: "ghidra-rename-apply.v1",
        details: [
          { label: "Runner", value: runner.path },
          { label: "Map", value: mapPath },
          { label: "Dry-run artifact", value: dryRunArtifactPath },
          { label: "Mode", value: "apply" },
          { label: "Exit code", value: String(result.exitCode) },
          { label: "Save succeeded", value: payload.saveSucceeded ? "yes" : "no" },
          { label: "Lock exception", value: payload.lockException ? "yes" : "no" },
          { label: "Applied", value: String(renameReport.applied) },
          { label: "Skipped", value: String(renameReport.skipped) },
          { label: "Missing", value: String(renameReport.missing) },
          { label: "Bad", value: String(renameReport.bad) },
          { label: "Failed", value: String(renameReport.failed) },
          { label: "stdout", value: stdoutPath },
          { label: "stderr", value: stderrPath },
          { label: "Apply artifact", value: artifactPath }
        ]
      };
    }
    case "assets.catalogGameFiles": {
      emitProgress("running", 25, "Checking asset catalog inputs.");
      const repoRoot = await resolveJobRepoRoot(appPath);
      const scriptPath = path.join(repoRoot, "tools", "export_asset_catalog.py");
      await fs.access(scriptPath);

      const outDir = path.join(path.resolve(artifactRoot), "artifacts", "asset-catalog", runId);
      await fs.mkdir(outDir, { recursive: true });
      emitProgress("running", 45, "Running allowlisted asset catalog builder.", outDir);
      const { command, args } = pythonCommand(scriptPath, [
        "--repo-root",
        repoRoot,
        "--out-dir",
        outDir
      ]);
      const result = await runAllowlistedProcess(command, args, repoRoot, signal);
      emitProgress("running", 80, "Reading asset catalog summary.", outDir);
      const summaryPath = path.join(outDir, "summary.json");
      const summary = JSON.parse(await fs.readFile(summaryPath, "utf8")) as Record<string, unknown>;
      const totalEntries = numberSummary(summary, "total_catalog_entries");
      emitProgress("running", 88, "Asset catalog artifact ready.", `${totalEntries} entries`);

      return {
        summary: `Cataloged ${totalEntries} asset rows from the existing exported corpus.`,
        payloadSchema: "asset-catalog.v1",
        details: [
          { label: "Catalog entries", value: String(totalEntries) },
          { label: "Textures", value: String(numberSummary(summary, "texture_catalog_entries")) },
          { label: "Loose meshes", value: String(numberSummary(summary, "loose_mesh_catalog_entries")) },
          { label: "Embedded meshes", value: String(numberSummary(summary, "embedded_mesh_catalog_entries")) },
          { label: "Videos", value: String(numberSummary(summary, "video_catalog_entries")) },
          { label: "Language rows", value: String(numberSummary(summary, "language_catalog_entries")) },
          { label: "Output directory", value: outDir },
          { label: "Exit code", value: String(result.exitCode) },
          { label: "stdout", value: tailText(result.stdout) || "none" },
          { label: "stderr", value: tailText(result.stderr) || "none" }
        ]
      };
    }
    case "content.readDocument": {
      emitProgress("running", 35, "Reading curated document.");
      const result = await readContentDocument(appPath, stringInput(inputs.id, "id"));
      emitProgress("running", 75, "Document loaded.", result.relativePath);
      return {
        summary: `Read ${result.title} (${result.relativePath}).`,
        payloadSchema: result.artifact.schemaVersion,
        details: [
          { label: "Audience", value: result.audience },
          { label: "Group", value: result.group },
          { label: "Path", value: result.relativePath },
          { label: "Bytes", value: String(result.byteLength) },
          { label: "Truncated", value: result.truncated ? "yes" : "no" }
        ]
      };
    }
    default:
      throw new Error(`No executor registered for ${definitionId}.`);
  }
}

interface ManagedProcessRegistryFile {
  schemaVersion: "managed-process-registry.v1";
  updatedAt: string;
  processes: ManagedProcessRegistryEntry[];
}

async function recordManagedProcess(
  artifactRoot: string,
  processRecord: Omit<ManagedProcessRegistryEntry, "lastCheckedAt" | "status">
) {
  if (!isValidProcessId(processRecord.processId)) {
    return;
  }

  const checkedAt = new Date().toISOString();
  const registry = await readManagedProcessRegistry(artifactRoot);
  const entry: ManagedProcessRegistryEntry = {
    ...processRecord,
    status: (await isProcessRunning(processRecord.processId)) ? "running" : "unknown",
    lastCheckedAt: checkedAt
  };
  const next = registry.processes.filter(
    (processEntry) => processEntry.runId !== entry.runId || processEntry.processId !== entry.processId
  );
  next.unshift(entry);
  await writeManagedProcessRegistry(artifactRoot, next);
}

async function buildManagedProcessRegistryPayload(artifactRoot: string): Promise<ManagedProcessRegistryPayload> {
  const processes = await refreshManagedProcessRegistry(artifactRoot);
  return {
    schemaVersion: "managed-process-registry.v1",
    generatedAt: new Date().toISOString(),
    mutation: false,
    counts: countManagedProcesses(processes),
    processes,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "managed-process-registry.v1",
      note: "Read-only managed process registry. Only PIDs created by typed launch/debug jobs are listed."
    }
  };
}

async function refreshManagedProcessRegistry(artifactRoot: string): Promise<ManagedProcessRegistryEntry[]> {
  const registry = await readManagedProcessRegistry(artifactRoot);
  const refreshed = await Promise.all(
    registry.processes.map(async (processEntry) => {
      if (!isValidProcessId(processEntry.processId)) {
        return {
          ...processEntry,
          status: "unknown" as ManagedProcessStatus,
          lastCheckedAt: new Date().toISOString()
        };
      }

      const running = await isProcessRunning(processEntry.processId);
      const status: ManagedProcessStatus = running
        ? processEntry.status === "stop-requested"
          ? "stop-requested"
          : "running"
        : "exited";
      return {
        ...processEntry,
        status,
        lastCheckedAt: new Date().toISOString()
      };
    })
  );
  await writeManagedProcessRegistry(artifactRoot, refreshed);
  return refreshed.sort((left, right) => Date.parse(right.startedAt) - Date.parse(left.startedAt));
}

async function updateManagedProcess(
  artifactRoot: string,
  targetRunId: string,
  targetProcessId: number,
  patch: Partial<ManagedProcessRegistryEntry>
) {
  const registry = await readManagedProcessRegistry(artifactRoot);
  let updated: ManagedProcessRegistryEntry | undefined;
  const processes = registry.processes.map((processEntry) => {
    if (processEntry.runId !== targetRunId || processEntry.processId !== targetProcessId) {
      return processEntry;
    }
    updated = {
      ...processEntry,
      ...patch
    };
    return updated;
  });
  if (!updated) {
    throw new JobRejectedError("Managed process target disappeared before it could be updated.");
  }
  await writeManagedProcessRegistry(artifactRoot, processes);
  return updated;
}

function selectManagedProcessTarget(
  processes: ManagedProcessRegistryEntry[],
  targetRunId: string | null,
  targetProcessId: number | null,
  kind?: ManagedProcessKind,
  allowExited = true,
  missingMessage = "No managed process is available for this stop request."
) {
  const candidates = kind ? processes.filter((processEntry) => processEntry.kind === kind) : processes;
  const target = targetRunId
    ? candidates.find((processEntry) => processEntry.runId === targetRunId)
    : targetProcessId
      ? candidates.find((processEntry) => processEntry.processId === targetProcessId)
      : candidates.find((processEntry) => processEntry.status === "running" || processEntry.status === "stop-requested") ??
        (allowExited ? candidates[0] : undefined);

  if (!target) {
    throw new JobRejectedError(missingMessage);
  }
  if (!isValidProcessId(target.processId)) {
    throw new JobRejectedError("Managed process record has an invalid PID.");
  }
  if (!allowExited && target.status === "exited") {
    throw new JobRejectedError("Managed process target is no longer running.");
  }
  return target;
}

function selectManagedLogTarget(
  processes: ManagedProcessRegistryEntry[],
  targetRunId: string | null,
  targetProcessId: number | null
) {
  const target = targetRunId
    ? processes.find((processEntry) => processEntry.runId === targetRunId)
    : targetProcessId
      ? processes.find((processEntry) => processEntry.processId === targetProcessId)
      : processes.find((processEntry) => typeof processEntry.logPath === "string" && processEntry.logPath.trim().length > 0);

  if (!target) {
    throw new JobRejectedError("No managed process with a recorded log path is available.");
  }
  if (!isValidProcessId(target.processId)) {
    throw new JobRejectedError("Managed process record has an invalid PID.");
  }
  if (typeof target.logPath !== "string" || target.logPath.trim().length === 0) {
    throw new JobRejectedError("Managed process target does not have a recorded log path.");
  }
  return target;
}

function resolveManagedLogPath(artifactRoot: string, target: ManagedProcessRegistryEntry) {
  const resolvedArtifactRoot = path.resolve(artifactRoot);
  const resolvedLogPath = path.resolve(target.logPath ?? "");
  if (!isInsidePath(resolvedArtifactRoot, resolvedLogPath)) {
    throw new JobRejectedError("Managed log path is outside the app artifact root.");
  }
  return resolvedLogPath;
}

async function readBoundedTextTail(filePath: string, byteLimit: number) {
  try {
    const stat = await fs.stat(filePath);
    if (!stat.isFile()) {
      throw new JobRejectedError("Managed log path is not a file.");
    }
    const readLength = Math.min(byteLimit, stat.size);
    const buffer = Buffer.alloc(readLength);
    if (readLength > 0) {
      const handle = await fs.open(filePath, "r");
      try {
        await handle.read(buffer, 0, readLength, Math.max(0, stat.size - readLength));
      } finally {
        await handle.close();
      }
    }
    const text = buffer.toString("utf8");
    return {
      exists: true,
      fileSizeBytes: stat.size,
      byteLength: readLength,
      truncated: stat.size > readLength,
      lineCount: countLines(text),
      text
    };
  } catch (error) {
    if (error instanceof JobRejectedError) {
      throw error;
    }
    const code = error instanceof Error && "code" in error ? String(error.code) : "";
    if (code === "ENOENT") {
      return {
        exists: false,
        fileSizeBytes: 0,
        byteLength: 0,
        truncated: false,
        lineCount: 0,
        text: ""
      };
    }
    throw error;
  }
}

function parseLogTailByteLimit(value: WorkbenchJobInputValue) {
  if (value === null || typeof value === "undefined" || value === "") {
    return 8192;
  }
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, "byteLimit"), 10);
  if (!Number.isSafeInteger(parsed) || parsed < 256 || parsed > 65536) {
    throw new Error("Managed log tail byteLimit must be between 256 and 65536.");
  }
  return parsed;
}

function parseInputStepDelay(value: WorkbenchJobInputValue) {
  if (value === null || typeof value === "undefined" || value === "") {
    return 60;
  }
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, "stepDelayMs"), 10);
  if (!Number.isSafeInteger(parsed) || parsed < 0 || parsed > 1000) {
    throw new Error("Game window input stepDelayMs must be between 0 and 1000.");
  }
  return parsed;
}

function countLines(text: string) {
  if (text.length === 0) {
    return 0;
  }
  return text.split(/\r?\n/).filter((line) => line.length > 0).length;
}

function isInsidePath(root: string, candidate: string) {
  const relative = path.relative(root, candidate);
  return relative.length === 0 || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

async function requestManagedProcessStop(target: ManagedProcessRegistryEntry) {
  if (!(await isProcessRunning(target.processId))) {
    return false;
  }

  try {
    process.kill(target.processId);
    return true;
  } catch (error) {
    const code = error instanceof Error && "code" in error ? String(error.code) : "";
    if (code === "ESRCH") {
      return false;
    }
    throw error;
  }
}

async function readManagedProcessRegistry(artifactRoot: string): Promise<ManagedProcessRegistryFile> {
  try {
    const parsed = JSON.parse(await fs.readFile(managedProcessRegistryPath(artifactRoot), "utf8"));
    if (isManagedProcessRegistryFile(parsed)) {
      return parsed;
    }
  } catch (error) {
    if (!(error instanceof Error) || !("code" in error) || error.code !== "ENOENT") {
      throw error;
    }
  }

  return {
    schemaVersion: "managed-process-registry.v1",
    updatedAt: new Date().toISOString(),
    processes: []
  };
}

async function writeManagedProcessRegistry(artifactRoot: string, processes: ManagedProcessRegistryEntry[]) {
  const registryPath = managedProcessRegistryPath(artifactRoot);
  const registry: ManagedProcessRegistryFile = {
    schemaVersion: "managed-process-registry.v1",
    updatedAt: new Date().toISOString(),
    processes: processes.slice(0, 50)
  };
  await fs.mkdir(path.dirname(registryPath), { recursive: true });
  await fs.writeFile(registryPath, `${JSON.stringify(registry, null, 2)}\n`, "utf8");
}

function managedProcessRegistryPath(artifactRoot: string) {
  return path.join(path.resolve(artifactRoot), "artifacts", "process-registry", "managed-processes.json");
}

function countManagedProcesses(processes: ManagedProcessRegistryEntry[]): ManagedProcessRegistryPayload["counts"] {
  return {
    total: processes.length,
    running: processes.filter((processEntry) => processEntry.status === "running").length,
    exited: processes.filter((processEntry) => processEntry.status === "exited").length,
    unknown: processes.filter((processEntry) => processEntry.status === "unknown").length,
    stopRequested: processes.filter((processEntry) => processEntry.status === "stop-requested").length
  };
}

async function isProcessRunning(processId: number) {
  if (!isValidProcessId(processId)) {
    return false;
  }

  try {
    process.kill(processId, 0);
    return true;
  } catch (error) {
    const code = error instanceof Error && "code" in error ? String(error.code) : "";
    return code === "EPERM";
  }
}

function isValidProcessId(processId: number) {
  return Number.isSafeInteger(processId) && processId > 0;
}

function isManagedProcessRegistryFile(value: unknown): value is ManagedProcessRegistryFile {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Partial<ManagedProcessRegistryFile>;
  return candidate.schemaVersion === "managed-process-registry.v1" && Array.isArray(candidate.processes);
}

function buildBaseRun(
  definition: WorkbenchJobDefinition,
  inputs: Record<string, WorkbenchJobInputValue>,
  policy: WorkbenchJobPolicy,
  progress: WorkbenchJobProgressEvent[],
  runId: string,
  startedAt: string,
  startedMs: number,
  status: WorkbenchJobRunSummary["status"],
  result: WorkbenchJobRunSummary["result"],
  errorMessage?: string
): WorkbenchJobRunSummary {
  const finishedAt = new Date().toISOString();
  const artifactKind = jobRunArtifactKind(definition);
  const artifactMutation =
    artifactKind === "local-file-copy" || artifactKind === "local-file-write" || definition.id === "ghidra.applyRenameMap";
  return {
    runId,
    definitionId: definition.id,
    title: definition.title,
    lane: definition.lane,
    safety: definition.safety,
    status,
    startedAt,
    finishedAt,
    durationMs: Date.now() - startedMs,
    inputs,
    policy,
    progress,
    result,
    errorMessage,
    artifact: {
      kind: artifactKind,
      mutation: artifactMutation,
      schemaVersion: "job-run.v1",
      jobId: runId,
      note: "Typed in-process workbench job. No raw renderer shell command was accepted."
    }
  };
}

function jobRunArtifactKind(definition: WorkbenchJobDefinition): WorkbenchJobRunSummary["artifact"]["kind"] {
  if (definition.id === "game.prepareSafeProfile" || definition.id === "save.prepareCopy" || definition.id === "patch.prepareExecutableCopy") {
    return "local-file-copy";
  }
  if (definition.id === "ghidra.applyRenameMap") {
    return "external-process";
  }
  if (
    definition.id === "save.applyPatch" ||
    definition.id === "save.restoreBackup" ||
    definition.id === "settings.applyOptionsPatch" ||
    definition.id === "patch.applyCatalogPatch" ||
    definition.id === "patch.restoreCatalogBackup"
  ) {
    return "local-file-write";
  }
  if (definition.safety === "launch-gated") {
    return "external-process";
  }
  return "read-only";
}

function statusMessage(status: WorkbenchJobRunSummary["status"]) {
  switch (status) {
    case "timed-out":
      return "Job timed out.";
    case "cancelled":
      return "Job was cancelled.";
    case "rejected":
      return "Job was rejected.";
    case "failed":
      return "Job failed.";
    case "completed":
      return "Job completed.";
  }
}

function resolvePolicy(policy: WorkbenchJobPolicy, requestedTimeoutMs?: number): WorkbenchJobPolicy {
  if (typeof requestedTimeoutMs !== "number" || !Number.isFinite(requestedTimeoutMs) || requestedTimeoutMs <= 0) {
    return policy;
  }

  return {
    ...policy,
    timeoutMs: Math.min(Math.floor(requestedTimeoutMs), policy.timeoutMs)
  };
}

async function withTimeout<T>(startWork: () => Promise<T>, timeoutMs: number, controller: AbortController): Promise<T> {
  if (controller.signal.aborted) {
    throw new JobCancelledError();
  }

  let timeout: NodeJS.Timeout | undefined;
  let abortHandler: (() => void) | undefined;
  let timeoutFired = false;
  const timeoutPromise = new Promise<never>((_resolve, reject) => {
    timeout = setTimeout(() => {
      timeoutFired = true;
      reject(new JobTimeoutError(timeoutMs));
      controller.abort();
    }, timeoutMs);
    abortHandler = () => {
      if (!timeoutFired) {
        reject(new JobCancelledError());
      }
    };
    controller.signal.addEventListener("abort", abortHandler, { once: true });
  });

  try {
    const work = startWork();
    try {
      return await Promise.race([work, timeoutPromise]);
    } finally {
      work.catch(() => {
        // The timeout branch aborts active child processes; consume the later process rejection.
      });
    }
  } finally {
    if (timeout) {
      clearTimeout(timeout);
    }
    if (abortHandler) {
      controller.signal.removeEventListener("abort", abortHandler);
    }
  }
}

class JobTimeoutError extends Error {
  constructor(timeoutMs: number) {
    super(`Job timed out after ${timeoutMs} ms.`);
  }
}

function delay(ms: number, signal: AbortSignal) {
  if (signal.aborted) {
    return Promise.reject(new JobCancelledError());
  }
  return new Promise<void>((resolve, reject) => {
    const timeout = setTimeout(resolve, ms);
    const abortHandler = () => {
      clearTimeout(timeout);
      reject(new JobCancelledError());
    };
    signal.addEventListener("abort", abortHandler, { once: true });
  });
}

class JobCancelledError extends Error {
  constructor() {
    super("Job was cancelled.");
  }
}

class JobRejectedError extends Error {
  constructor(message: string) {
    super(message);
  }
}

async function writeJobRunArtifact(
  summary: WorkbenchJobRunSummary,
  artifactRoot: string
): Promise<WorkbenchJobRunSummary> {
  const artifactDir = path.join(path.resolve(artifactRoot), "artifacts", "job-runs", summary.runId);
  const artifactPath = path.join(artifactDir, "job-run.json");
  const summaryWithArtifact: WorkbenchJobRunSummary = {
    ...summary,
    artifact: {
      ...summary.artifact,
      artifactPath
    }
  };

  await fs.mkdir(artifactDir, { recursive: true });
  await fs.writeFile(artifactPath, `${JSON.stringify(summaryWithArtifact, null, 2)}\n`, "utf8");
  runs.set(summary.runId, summaryWithArtifact);
  return summaryWithArtifact;
}

function stringInput(value: WorkbenchJobInputValue, label: string): string {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`Job input ${label} is required.`);
  }
  return value.trim();
}

function stringOrNumberInput(value: WorkbenchJobInputValue, label: string): string | number {
  if (typeof value === "number") {
    return value;
  }
  return stringInput(value, label);
}

function optionalStringInput(value: WorkbenchJobInputValue, label: string): string | null {
  if (value === null || typeof value === "undefined") {
    return null;
  }
  if (typeof value !== "string") {
    throw new Error(`Job input ${label} must be a string when provided.`);
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

function buildAppCoreSavePatchRequestPayload(inputs: Record<string, WorkbenchJobInputValue>): AppCoreSavePatchRequestPayload {
  return {
    schemaVersion: "appcore-save-patch-request.v1",
    generatedAt: new Date().toISOString(),
    mutation: false,
    input: {
      path: stringInput(inputs.path, "path"),
      rank: normalizeSaveRankInput(optionalStringInput(inputs.rank, "rank") ?? "S"),
      kills: parseSavePatchKillInput(inputs.kills ?? 100, "kills"),
      useNewGoodies: optionalBooleanInput(inputs.useNewGoodies, "useNewGoodies", false),
      killsOnly: optionalBooleanInput(inputs.killsOnly, "killsOnly", false),
      patchNodes: optionalBooleanInput(inputs.patchNodes, "patchNodes", true),
      patchLinks: optionalBooleanInput(inputs.patchLinks, "patchLinks", true),
      patchGoodies: optionalBooleanInput(inputs.patchGoodies, "patchGoodies", true),
      patchKills: optionalBooleanInput(inputs.patchKills, "patchKills", true),
      allowCareerSectionsOnOptionsFile: optionalBooleanInput(
        inputs.allowCareerSectionsOnOptionsFile,
        "allowCareerSectionsOnOptionsFile",
        false
      ),
      levelRanks: parseLevelRankRows(inputs.levelRanks),
      perCategoryKills: parsePerCategoryKillRows(inputs.perCategoryKills)
    },
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "appcore-save-patch-request.v1",
      note: "Host-owned request JSON for AppCore save/options patch planning. This file describes intent only and does not mutate source bytes."
    }
  };
}

function buildOptionsPatchRequestInput(inputs: Record<string, WorkbenchJobInputValue>): OptionsPatchRequestInput {
  const copyOptionsFromPath = optionalStringInput(inputs.copyOptionsFromPath, "copyOptionsFromPath");
  return {
    path: stringInput(inputs.path, "path"),
    soundVolume: optionalNumberInput(inputs.soundVolume, "soundVolume"),
    musicVolume: optionalNumberInput(inputs.musicVolume, "musicVolume"),
    invertWalkerP1: optionalNullableBooleanInput(inputs.invertWalkerP1, "invertWalkerP1"),
    invertWalkerP2: optionalNullableBooleanInput(inputs.invertWalkerP2, "invertWalkerP2"),
    invertFlightP1: optionalNullableBooleanInput(inputs.invertFlightP1, "invertFlightP1"),
    invertFlightP2: optionalNullableBooleanInput(inputs.invertFlightP2, "invertFlightP2"),
    vibrationP1: optionalNullableBooleanInput(inputs.vibrationP1, "vibrationP1"),
    vibrationP2: optionalNullableBooleanInput(inputs.vibrationP2, "vibrationP2"),
    controllerConfigP1: optionalIntegerInput(inputs.controllerConfigP1, "controllerConfigP1"),
    controllerConfigP2: optionalIntegerInput(inputs.controllerConfigP2, "controllerConfigP2"),
    mouseSensitivity: optionalNumberInput(inputs.mouseSensitivity, "mouseSensitivity"),
    controlSchemeIndex: optionalIntegerInput(inputs.controlSchemeIndex, "controlSchemeIndex"),
    languageIndex: optionalIntegerInput(inputs.languageIndex, "languageIndex"),
    screenShape: optionalIntegerInput(inputs.screenShape, "screenShape"),
    d3dDeviceIndex: optionalIntegerInput(inputs.d3dDeviceIndex, "d3dDeviceIndex"),
    copyOptionsFromPath,
    copyOptionsEntries: copyOptionsFromPath ? optionalBooleanInput(inputs.copyOptionsEntries, "copyOptionsEntries", true) : false,
    copyOptionsTail: copyOptionsFromPath ? optionalBooleanInput(inputs.copyOptionsTail, "copyOptionsTail", true) : false,
    keybindOverrides: parseOptionsKeybindRows(inputs.keybindOverrides)
  };
}

function plannedSectionsFromInput(input: AppCoreSavePatchRequestPayload["input"]) {
  if (input.killsOnly) {
    return ["kills"];
  }
  return [
    input.patchNodes ? "nodes" : null,
    input.patchLinks ? "links" : null,
    input.patchGoodies ? "goodies" : null,
    input.patchKills ? "kills" : null
  ].filter((section): section is string => Boolean(section));
}

function plannedOptionsSectionsFromInput(input: OptionsPatchRequestInput) {
  return [
    [
      input.soundVolume,
      input.musicVolume,
      input.invertWalkerP1,
      input.invertWalkerP2,
      input.invertFlightP1,
      input.invertFlightP2,
      input.vibrationP1,
      input.vibrationP2,
      input.controllerConfigP1,
      input.controllerConfigP2
    ].some((value) => value !== null)
      ? "career-settings"
      : null,
    input.copyOptionsFromPath ? "options-copy" : null,
    [input.mouseSensitivity, input.controlSchemeIndex, input.languageIndex, input.screenShape, input.d3dDeviceIndex].some(
      (value) => value !== null
    )
      ? "options-tail"
      : null,
    input.keybindOverrides.length > 0 ? "keybinds" : null
  ].filter((section): section is string => Boolean(section));
}

function optionalBooleanInput(value: WorkbenchJobInputValue, label: string, defaultValue: boolean) {
  if (value === null || typeof value === "undefined" || value === "") {
    return defaultValue;
  }
  if (typeof value === "boolean") {
    return value;
  }
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (["true", "yes", "1", "on"].includes(normalized)) {
      return true;
    }
    if (["false", "no", "0", "off"].includes(normalized)) {
      return false;
    }
  }
  throw new Error(`Job input ${label} must be a boolean.`);
}

function optionalNullableBooleanInput(value: WorkbenchJobInputValue, label: string) {
  if (value === null || typeof value === "undefined" || value === "") {
    return null;
  }
  return optionalBooleanInput(value, label, false);
}

function optionalNumberInput(value: WorkbenchJobInputValue, label: string) {
  if (value === null || typeof value === "undefined" || value === "") {
    return null;
  }
  const parsed = typeof value === "number" ? value : Number.parseFloat(stringInput(value, label));
  if (!Number.isFinite(parsed)) {
    throw new Error(`Job input ${label} must be a finite number.`);
  }
  return parsed;
}

function optionalIntegerInput(value: WorkbenchJobInputValue, label: string) {
  if (value === null || typeof value === "undefined" || value === "") {
    return null;
  }
  const parsed =
    typeof value === "number"
      ? value
      : stringInput(value, label).trim().toLowerCase().startsWith("0x")
        ? Number.parseInt(stringInput(value, label).trim().slice(2), 16)
        : Number.parseInt(stringInput(value, label), 10);
  if (!Number.isSafeInteger(parsed)) {
    throw new Error(`Job input ${label} must be an integer.`);
  }
  return parsed;
}

function parseOptionsKeybindRows(value: WorkbenchJobInputValue): OptionsPatchKeybindOverride[] {
  const raw = optionalStringInput(value, "keybindOverrides");
  if (!raw) {
    return [];
  }

  return raw
    .split(/[;\n]+/)
    .map((row) => row.trim())
    .filter((row) => row.length > 0)
    .map((row) => {
      const separator = row.indexOf("=");
      if (separator <= 0) {
        throw new Error(`Invalid keybind override '${row}', expected action=slot0,slot1.`);
      }
      const action = row.slice(0, separator).trim();
      const slotText = row.slice(separator + 1);
      const [slot0, slot1] = slotText.split(",", 2).map((slot) => slot.trim());
      return {
        action,
        slot0: slot0 || null,
        slot1: slot1 || null
      };
    });
}

function parseSavePatchKillInput(value: WorkbenchJobInputValue, label: string) {
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, label), 10);
  if (!Number.isSafeInteger(parsed) || parsed < 0 || parsed > 0x00ffffff) {
    throw new Error(`Job input ${label} must be an integer from 0 to 16777215.`);
  }
  return parsed;
}

function normalizeSaveRankInput(value: string) {
  const rank = value.trim().toUpperCase();
  if (!["S", "A", "B", "C", "D", "E", "NONE"].includes(rank)) {
    throw new Error(`Invalid save patch rank: ${value}.`);
  }
  return rank;
}

function parseLevelRankRows(value: WorkbenchJobInputValue) {
  const raw = optionalStringInput(value, "levelRanks");
  if (!raw) {
    return [];
  }
  return raw
    .split(/[\s,;]+/)
    .filter((token) => token.length > 0)
    .map((token) => {
      const [nodeText, rankText] = token.split(":", 2);
      const nodeIndex = Number.parseInt(nodeText, 10);
      if (!Number.isSafeInteger(nodeIndex) || nodeIndex < 1 || nodeIndex > 43 || !rankText) {
        throw new Error(`Invalid level rank token '${token}', expected NODE_INDEX:RANK with node index 1-43.`);
      }
      return {
        nodeIndex,
        rank: normalizeSaveRankInput(rankText)
      };
    });
}

function parsePerCategoryKillRows(value: WorkbenchJobInputValue) {
  const raw = optionalStringInput(value, "perCategoryKills");
  if (!raw) {
    return [];
  }
  return raw
    .split(/[\s,;]+/)
    .filter((token) => token.length > 0)
    .map((token) => {
      const [categoryText, killsText] = token.split(":", 2);
      if (!categoryText || !killsText) {
        throw new Error(`Invalid per-category kill token '${token}', expected CATEGORY:KILLS.`);
      }
      const categoryIndex = parseKillCategoryIndex(categoryText);
      return {
        categoryIndex,
        categoryName: killCategoryName(categoryIndex),
        kills: parseSavePatchKillInput(killsText, `perCategoryKills.${categoryText}`)
      };
    });
}

function parseKillCategoryIndex(value: string) {
  const names = ["aircraft", "vehicles", "emplacements", "infantry", "mechs"];
  const normalized = value.trim().toLowerCase();
  const namedIndex = names.indexOf(normalized);
  if (namedIndex >= 0) {
    return namedIndex;
  }
  const parsed = Number.parseInt(normalized, 10);
  if (!Number.isSafeInteger(parsed) || parsed < 0 || parsed >= names.length) {
    throw new Error(`Invalid kill category '${value}'. Use 0-4 or aircraft/vehicles/emplacements/infantry/mechs.`);
  }
  return parsed;
}

function killCategoryName(index: number) {
  return ["Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs"][index] ?? `Category ${index}`;
}

function requireArmPhrase(value: WorkbenchJobInputValue, expected: string, label: string) {
  const actual = optionalStringInput(value, "armPhrase");
  if (actual !== expected) {
    throw new JobRejectedError(`${label} requires the explicit arm phrase ${expected}.`);
  }
}

function requireTrueInput(value: WorkbenchJobInputValue, inputName: string, label: string) {
  if (value !== true) {
    throw new JobRejectedError(`${label} requires ${inputName}=true.`);
  }
}

function assertCopiedSafeProfile(gameRoot: string, repoRoot: string, label: string) {
  const relativeToRepo = path.relative(path.resolve(repoRoot), path.resolve(gameRoot));
  const insideRepo = relativeToRepo === "" || (!relativeToRepo.startsWith("..") && !path.isAbsolute(relativeToRepo));
  if (insideRepo) {
    throw new JobRejectedError(`${label} requires a copied/safe game profile outside the repo root.`);
  }
}

function sanitizeProfileName(value: string) {
  const trimmed = value.trim();
  if (!/^[A-Za-z0-9._-]{1,64}$/.test(trimmed)) {
    throw new JobRejectedError("Profile name may contain only letters, numbers, dot, underscore, and dash.");
  }
  return trimmed;
}

function runGhidraHeadlessPostscript(
  repoRoot: string,
  runnerPath: string,
  outPath: string,
  mode: string,
  signal: AbortSignal
) {
  if (process.platform === "win32") {
    const repoRootWsl = `"$(wslpath -u ${quoteForBash(repoRoot)})"`;
    const runnerPathWsl = `"$(wslpath -u ${quoteForBash(runnerPath)})"`;
    const outPathWsl = `"$(wslpath -u ${quoteForBash(outPath)})"`;
    const bashCommand = [
      `cd ${repoRootWsl}`,
      `${runnerPathWsl} ExportWeakFunctionList.java ${outPathWsl} ${quoteForBash(mode)}`
    ].join(" && ");
    return runAllowlistedProcess("wsl.exe", ["bash", "-lc", bashCommand], repoRoot, signal);
  }

  return runAllowlistedProcess("bash", [runnerPath, "ExportWeakFunctionList.java", outPath, mode], repoRoot, signal);
}

function runGhidraAddressDecompile(
  repoRoot: string,
  runnerPath: string,
  addressListPath: string,
  outDir: string,
  timeoutSec: number,
  signal: AbortSignal
) {
  if (process.platform === "win32") {
    const repoRootWsl = `"$(wslpath -u ${quoteForBash(repoRoot)})"`;
    const runnerPathWsl = `"$(wslpath -u ${quoteForBash(runnerPath)})"`;
    const addressListWsl = `"$(wslpath -u ${quoteForBash(addressListPath)})"`;
    const outDirWsl = `"$(wslpath -u ${quoteForBash(outDir)})"`;
    const bashCommand = [
      `cd ${repoRootWsl}`,
      `${runnerPathWsl} ExportFunctionsByAddressDecompile.java ${addressListWsl} ${outDirWsl} ${quoteForBash(String(timeoutSec))}`
    ].join(" && ");
    return runAllowlistedProcess("wsl.exe", ["bash", "-lc", bashCommand], repoRoot, signal);
  }

  return runAllowlistedProcess(
    "bash",
    [runnerPath, "ExportFunctionsByAddressDecompile.java", addressListPath, outDir, String(timeoutSec)],
    repoRoot,
    signal
  );
}

function runGhidraBatchRename(
  repoRoot: string,
  runnerPath: string,
  mapPath: string,
  mode: "dry" | "apply",
  signal: AbortSignal
) {
  if (process.platform === "win32") {
    const repoRootWsl = `"$(wslpath -u ${quoteForBash(repoRoot)})"`;
    const runnerPathWsl = `"$(wslpath -u ${quoteForBash(runnerPath)})"`;
    const mapPathWsl = `"$(wslpath -u ${quoteForBash(mapPath)})"`;
    const bashCommand = [`cd ${repoRootWsl}`, `${runnerPathWsl} ${mapPathWsl} ${quoteForBash(mode)}`].join(" && ");
    return runAllowlistedProcess("wsl.exe", ["bash", "-lc", bashCommand], repoRoot, signal, { rejectOnNonZero: false });
  }

  return runAllowlistedProcess("bash", [runnerPath, mapPath, mode], repoRoot, signal, { rejectOnNonZero: false });
}

async function resolveJobRepoRoot(appPath: string) {
  const candidates = [
    process.cwd(),
    appPath,
    path.resolve(appPath, "..", ".."),
    path.resolve(process.cwd(), "..", "..")
  ];
  for (const candidate of candidates) {
    try {
      await fs.access(path.join(candidate, "package.json"));
      await fs.access(path.join(candidate, "patches", "catalog"));
      return path.resolve(candidate);
    } catch {
      // Try the next dev/packaged root.
    }
  }
  return path.resolve(process.cwd());
}

function pythonCommand(scriptPath: string, scriptArgs: string[]) {
  if (process.platform === "win32") {
    return {
      command: "py.exe",
      args: ["-3", scriptPath, ...scriptArgs]
    };
  }

  return {
    command: "python3",
    args: [scriptPath, ...scriptArgs]
  };
}

function dotnetCommand(projectPath: string, hostArgs: string[]) {
  const command = (process.env.DOTNET_EXE?.trim() || "dotnet").replace(/^"|"$/g, "");
  return {
    command,
    args: ["run", "--no-launch-profile", "--project", projectPath, "--", ...hostArgs]
  };
}

function numberSummary(summary: Record<string, unknown>, key: string) {
  const value = summary[key];
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`Asset catalog summary is missing numeric ${key}.`);
  }
  return value;
}

async function summarizeTsv(filePath: string) {
  const raw = await fs.readFile(filePath, "utf8");
  const lines = raw.split(/\r?\n/).filter((line) => line.trim().length > 0);
  const header = lines[0] ?? "";
  if (header !== "address\tname\tsignature") {
    throw new Error("Ghidra export did not write the expected TSV header.");
  }

  return {
    rows: Math.max(0, lines.length - 1)
  };
}

async function summarizeGhidraDecompileIndex(filePath: string) {
  const raw = await fs.readFile(filePath, "utf8");
  const lines = raw.split(/\r?\n/).filter((line) => line.trim().length > 0);
  const header = lines[0] ?? "";
  if (header !== "address\tname\tsignature\tstatus") {
    throw new Error("Ghidra decompile export did not write the expected index header.");
  }

  const rows = lines.slice(1).map((line) => line.split("\t"));
  return {
    rows: rows.length,
    ok: rows.filter((row) => row[3] === "OK").length,
    missing: rows.filter((row) => row[3] === "MISSING").length,
    failed: rows.filter((row) => row[3] === "FAILED").length
  };
}

function parseAddressListInput(value: WorkbenchJobInputValue) {
  const raw = optionalStringInput(value, "addresses") ?? "0x00421200";
  const tokens = raw.split(/[\s,;]+/).filter((token) => token.trim().length > 0);
  if (tokens.length === 0) {
    throw new Error("At least one address is required.");
  }
  if (tokens.length > 25) {
    throw new Error("Address decompile export is capped at 25 addresses per job.");
  }

  const seen = new Set<string>();
  return tokens
    .map(normalizeAddressToken)
    .filter((address) => {
      if (seen.has(address)) {
        return false;
      }
      seen.add(address);
      return true;
    });
}

function normalizeAddressToken(token: string) {
  const trimmed = token.trim();
  const raw = trimmed.toLowerCase().startsWith("0x") ? trimmed.slice(2) : trimmed;
  if (!/^[0-9a-f]+$/i.test(raw)) {
    throw new Error(`Invalid Ghidra address: ${token}`);
  }
  const parsed = Number.parseInt(raw, 16);
  if (!Number.isSafeInteger(parsed) || parsed <= 0 || parsed > 0xffffffff) {
    throw new Error(`Invalid Ghidra address: ${token}`);
  }
  return `0x${parsed.toString(16).padStart(8, "0")}`;
}

function parseTimeoutSeconds(value: WorkbenchJobInputValue) {
  if (value === null || typeof value === "undefined") {
    return 60;
  }
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, "timeoutSec"), 10);
  if (!Number.isSafeInteger(parsed) || parsed < 5 || parsed > 120) {
    throw new Error("Ghidra decompile timeout must be between 5 and 120 seconds.");
  }
  return parsed;
}

function parseLaunchArgs(value: WorkbenchJobInputValue) {
  const raw = optionalStringInput(value, "args") ?? "";
  const tokens = raw.split(/\s+/).filter((token) => token.length > 0);
  // Keep the old retail argument allowlisted for diagnostics only; windowed mode is owned by the patch catalog.
  const allowed = new Set(["-forcewindowed"]);
  for (const token of tokens) {
    if (!allowed.has(token)) {
      throw new Error(`Unsupported game launch argument: ${token}`);
    }
  }
  return tokens;
}

function parsePort(value: WorkbenchJobInputValue) {
  if (value === null || typeof value === "undefined") {
    return 5005;
  }
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, "port"), 10);
  if (!Number.isSafeInteger(parsed) || parsed < 1024 || parsed > 65535) {
    throw new Error("Debug probe port must be between 1024 and 65535.");
  }
  return parsed;
}

function optionalProcessIdInput(value: WorkbenchJobInputValue, label: string): number | null {
  if (value === null || typeof value === "undefined" || value === "") {
    return null;
  }
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, label), 10);
  if (!isValidProcessId(parsed)) {
    throw new JobRejectedError(`Managed process ${label} must be a positive integer PID.`);
  }
  return parsed;
}

function parseCaptureDimensionInput(
  value: WorkbenchJobInputValue,
  label: string,
  fallback: number,
  min: number,
  max: number
) {
  if (value === null || typeof value === "undefined" || value === "") {
    return fallback;
  }
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, label), 10);
  if (!Number.isInteger(parsed) || parsed < min || parsed > max) {
    throw new JobRejectedError(`Capture ${label} must be an integer between ${min} and ${max}.`);
  }
  return parsed;
}

function parseFrameSequenceCount(value: WorkbenchJobInputValue) {
  if (value === null || typeof value === "undefined" || value === "") {
    return 3;
  }
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, "frameCount"), 10);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 12) {
    throw new JobRejectedError("Frame sequence count must be an integer between 1 and 12.");
  }
  return parsed;
}

function parseFrameSequenceInterval(value: WorkbenchJobInputValue) {
  if (value === null || typeof value === "undefined" || value === "") {
    return 250;
  }
  const parsed = typeof value === "number" ? value : Number.parseInt(stringInput(value, "intervalMs"), 10);
  if (!Number.isInteger(parsed) || parsed < 0 || parsed > 5000) {
    throw new JobRejectedError("Frame sequence intervalMs must be an integer between 0 and 5000.");
  }
  return parsed;
}

function selectProbeScript(probes: Array<{ label: string; path: string; exists: boolean }>, requestedProbe: string | null) {
  const available = probes.filter((probe) => probe.exists);
  const probeId = requestedProbe ?? "pause-persist-wave1.cdb.txt";
  const selected = available.find((probe) => probe.label === probeId);
  if (!selected) {
    throw new Error(`Probe is not allowlisted or unavailable: ${probeId}`);
  }
  return selected;
}

async function writePlanArtifact(
  artifactRoot: string,
  family: string,
  runId: string,
  fileName: string,
  payload: Record<string, unknown>
) {
  const planDir = path.join(path.resolve(artifactRoot), "artifacts", family, runId);
  const planPath = path.join(planDir, fileName);
  await fs.mkdir(planDir, { recursive: true });
  await fs.writeFile(planPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  return planPath;
}

function buildPowerShellStartProcessPreview(executablePath: string, workingDirectory: string, args: string[]) {
  const argList = args.length > 0 ? ` -ArgumentList ${quoteForPowerShell(args.join(" "))}` : "";
  return `Start-Process -FilePath ${quoteForPowerShell(executablePath)} -WorkingDirectory ${quoteForPowerShell(workingDirectory)}${argList}`;
}

function buildPowerShellScriptPreview(scriptPath: string, args: Record<string, string>) {
  const argText = Object.entries(args)
    .map(([key, value]) => `-${key} ${quoteForPowerShell(value)}`)
    .join(" ");
  return `powershell -NoProfile -ExecutionPolicy Bypass -File ${quoteForPowerShell(scriptPath)} ${argText}`;
}

function buildCdbSessionPassword(runId: string) {
  const runSuffix = runId.replace(/[^a-zA-Z0-9]+/g, "").slice(-12);
  return `bea-${runSuffix}-${randomBytes(12).toString("hex")}`;
}

function quoteForPowerShell(value: string) {
  return `"${value.replace(/"/g, '`"')}"`;
}

function runAllowlistedProcess(
  command: string,
  args: string[],
  cwd: string,
  signal: AbortSignal,
  options: { rejectOnNonZero?: boolean } = {}
): Promise<{ exitCode: number; stdout: string; stderr: string }> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      windowsHide: true,
      signal
    });
    let stdout = "";
    let stderr = "";
    const append = (current: string, chunk: Buffer) => `${current}${chunk.toString("utf8")}`.slice(-64 * 1024);

    child.stdout.on("data", (chunk: Buffer) => {
      stdout = append(stdout, chunk);
    });
    child.stderr.on("data", (chunk: Buffer) => {
      stderr = append(stderr, chunk);
    });
    child.on("error", reject);
    child.on("close", (code) => {
      const exitCode = code ?? -1;
      if (exitCode !== 0 && options.rejectOnNonZero !== false) {
        reject(new Error(`Allowlisted process exited with code ${exitCode}: ${stderr.trim() || stdout.trim()}`));
        return;
      }
      resolve({ exitCode, stdout, stderr });
    });
  });
}

function firstNonEmptyLine(value: string) {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .find((line) => line.length > 0);
}

function parseJsonProcessStdout(stdout: string) {
  const trimmed = stdout.trim();
  const start = trimmed.indexOf("{");
  const end = trimmed.lastIndexOf("}");
  if (start < 0 || end < start) {
    throw new Error(`Allowlisted process did not emit JSON: ${tailText(stdout) || "empty stdout"}`);
  }
  return JSON.parse(trimmed.slice(start, end + 1));
}

function parseGhidraExportStats(stdout: string) {
  const match = stdout.match(/mode=\S+\s+total_functions=(\d+)\s+weak_functions=(\d+)/);
  return {
    totalFunctions: match?.[1],
    weakFunctions: match?.[2]
  };
}

function parseGhidraBatchRenameReport(stdout: string) {
  const lines = stdout.split(/\r?\n/);
  const summary = stdout.match(/applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)/i);
  const missingRows = lines.filter((line) => /^MISSING:/i.test(line.trim())).length;
  const badAddressRows = lines.filter((line) => /^BADADDR:/i.test(line.trim())).length;
  const failedRows = lines.filter((line) => /^FAIL:/i.test(line.trim())).length;
  const parsedMissing = summary ? Number.parseInt(summary[3] ?? "0", 10) : missingRows;
  const parsedBad = summary ? Number.parseInt(summary[4] ?? "0", 10) : badAddressRows + failedRows;

  return {
    summarySeen: Boolean(summary),
    applied: summary ? Number.parseInt(summary[1] ?? "0", 10) : lines.filter((line) => /^OK:/i.test(line.trim())).length,
    skipped: summary
      ? Number.parseInt(summary[2] ?? "0", 10)
      : lines.filter((line) => /^(SKIP|DRY):/i.test(line.trim())).length,
    missing: parsedMissing,
    bad: parsedBad,
    failed: failedRows,
    missingRows,
    badAddressRows
  };
}

function quoteForBash(value: string) {
  return `'${value.replace(/'/g, "'\\''")}'`;
}

function tailText(value: string, maxLength = 1200) {
  const trimmed = value.trim();
  return trimmed.length > maxLength ? trimmed.slice(-maxLength) : trimmed;
}

function buildRunId(definitionId: string, timestamp: string) {
  const compactTimestamp = timestamp.replace(/\D/g, "").slice(0, 17);
  const safeDefinition = definitionId.replace(/[^a-zA-Z0-9]+/g, "-");
  const entropy = randomBytes(3).toString("hex");
  return `job-${compactTimestamp}-${safeDefinition}-${entropy}`;
}

function isJobRunSummary(value: unknown): value is WorkbenchJobRunSummary {
  if (!value || typeof value !== "object") {
    return false;
  }

  const candidate = value as Partial<WorkbenchJobRunSummary>;
  return (
    typeof candidate.runId === "string" &&
    typeof candidate.definitionId === "string" &&
    typeof candidate.startedAt === "string" &&
    typeof candidate.title === "string" &&
    !!candidate.policy &&
    Array.isArray(candidate.progress) &&
    !!candidate.artifact &&
    candidate.artifact.schemaVersion === "job-run.v1"
  );
}
