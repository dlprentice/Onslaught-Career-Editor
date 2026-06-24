import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import type {
  PatchCatalogSummary,
  PatchApplyPayload,
  ExecutableCopyPayload,
  PatchPlanPayload,
  PatchSpecSummary,
  PatchRestorePayload,
  PatchState,
  PatchTone,
  PatchVerifyRow,
  SpecimenVerificationSummary
} from "@onslaught/contracts";

const catalogRelativePath = path.join("patches", "catalog", "patches.v2.json");
const knownRetailSteamSha256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";

interface CatalogPatchJson {
  id?: unknown;
  title?: unknown;
  track?: unknown;
  file_offset?: unknown;
  expected_original_bytes?: unknown;
  patched_bytes?: unknown;
  purpose?: unknown;
  optional?: unknown;
}

interface CatalogJson {
  catalog_version?: unknown;
  generated_at?: unknown;
  patches?: unknown;
}

interface ParsedPatchSpec extends PatchSpecSummary {
  originalBytes: Buffer;
  patchedBytes: Buffer;
}

interface LoadedPatchCatalog {
  summary: PatchCatalogSummary;
  specs: ParsedPatchSpec[];
}

export async function verifyExecutablePath(
  executablePath: string,
  appPath: string,
  artifactRoot?: string
): Promise<SpecimenVerificationSummary> {
  const normalizedPath = path.resolve(executablePath);
  const stat = await fs.stat(normalizedPath);
  if (!stat.isFile()) {
    throw new Error("Selected path is not a file.");
  }

  if (path.basename(normalizedPath).toLowerCase() !== "bea.exe") {
    throw new Error("Select BEA.exe so patch offsets are interpreted against the expected retail binary layout.");
  }

  const [data, catalog] = await Promise.all([fs.readFile(normalizedPath), loadPatchCatalog(appPath)]);
  const sha256 = createHash("sha256").update(data).digest("hex");
  const verifiedAt = new Date().toISOString();
  const rows = catalog.specs.map((spec) => verifyPatch(data, spec));
  const counts = {
    original: rows.filter((row) => row.state === "original").length,
    patched: rows.filter((row) => row.state === "patched").length,
    mismatch: rows.filter((row) => row.state === "mismatch").length,
    outOfRange: rows.filter((row) => row.state === "out-of-range").length
  };

  const summary: SpecimenVerificationSummary = {
    selectedPath: normalizedPath,
    fileName: path.basename(normalizedPath),
    fileSize: data.length,
    sha256,
    verifiedAt,
    isKnownRetailSteamHash: sha256.toLowerCase() === knownRetailSteamSha256,
    catalog: catalog.summary,
    counts,
    rows,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "specimen-verification.v1",
      note: "Read-only verification only. No bytes were changed."
    }
  };

  if (!artifactRoot) {
    return summary;
  }

  return writeVerificationArtifact(summary, artifactRoot);
}

export async function planCatalogPatchSet(
  executablePath: string,
  appPath: string,
  artifactRoot: string,
  patchIdsInput = "stable"
): Promise<PatchPlanPayload> {
  const verification = await verifyExecutablePath(executablePath, appPath);
  const patchIds = resolvePatchIds(verification.rows, patchIdsInput);
  const selectedRows = patchIds.map((id) => {
    const row = verification.rows.find((candidate) => candidate.spec.id === id);
    if (!row) {
      throw new Error(`Patch id is not in the catalog: ${id}`);
    }
    return row;
  });

  if (selectedRows.length === 0) {
    throw new Error("Patch plan must include at least one catalog patch.");
  }

  const rows: PatchPlanPayload["rows"] = selectedRows.map((row) => ({
    id: row.spec.id,
    title: row.spec.title,
    track: row.spec.track,
    optional: row.spec.optional,
    fileOffsetHex: row.spec.fileOffsetHex,
    byteLength: row.spec.byteLength,
    currentState: row.state,
    action: planActionFor(row.state),
    reason: planReasonFor(row.state)
  }));
  const counts = {
    selected: rows.length,
    readyToApply: rows.filter((row) => row.action === "would-apply").length,
    alreadyApplied: rows.filter((row) => row.action === "already-applied").length,
    blocked: rows.filter((row) => row.action === "blocked").length,
    optional: rows.filter((row) => row.optional).length
  };
  const plannedAt = new Date().toISOString();
  const summary: PatchPlanPayload = {
    executablePath: verification.selectedPath,
    fileName: verification.fileName,
    fileSize: verification.fileSize,
    sha256: verification.sha256,
    plannedAt,
    patchIds,
    canApplyAll: counts.blocked === 0,
    counts,
    rows,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "patch-plan.v1",
      note: "Read-only patch plan. No bytes were changed."
    }
  };

  return writePatchPlanArtifact(summary, artifactRoot);
}

export async function prepareExecutableCopyPath(
  sourcePathInput: string,
  appPath: string,
  artifactRoot: string,
  runId = buildStandaloneRunId("patch-executable-copy")
): Promise<ExecutableCopyPayload> {
  const root = path.resolve(artifactRoot);
  const sourcePath = path.resolve(sourcePathInput);
  const sourceVerification = await verifyExecutablePath(sourcePath, appPath);
  const sourceData = await fs.readFile(sourcePath);
  const targetDir = path.join(root, "artifacts", "patch-executable-copy", runId, "target");
  const targetPath = path.join(targetDir, "BEA.exe");
  await fs.mkdir(targetDir, { recursive: true });
  await fs.copyFile(sourcePath, targetPath);

  const readback = await fs.readFile(targetPath);
  const readbackVerified = readback.equals(sourceData);
  if (!readbackVerified) {
    throw new Error("Executable copy read-back verification failed.");
  }
  const copyVerification = await verifyExecutablePath(targetPath, appPath);

  const payload: ExecutableCopyPayload = {
    schemaVersion: "patch-executable-copy.v1",
    generatedAt: new Date().toISOString(),
    command: "copy-executable",
    mutation: true,
    source: {
      path: sourceVerification.selectedPath,
      fileName: sourceVerification.fileName,
      fileSize: sourceVerification.fileSize,
      sha256: sourceVerification.sha256,
      isKnownRetailSteamHash: sourceVerification.isKnownRetailSteamHash,
      counts: sourceVerification.counts
    },
    copy: {
      path: targetPath,
      fileName: copyVerification.fileName,
      fileSize: readback.length,
      sha256: copyVerification.sha256,
      readbackVerified
    },
    catalog: sourceVerification.catalog,
    artifact: {
      kind: "local-file-copy",
      mutation: true,
      schemaVersion: "patch-executable-copy.v1",
      note: "Copied BEA.exe into the app artifact root for safe catalog patch apply/restore workflows."
    }
  };

  const artifactPath = await writePatchMutationArtifact(root, "patch-executable-copy", runId, "copy.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

export async function applyCatalogPatchSet(
  executablePath: string,
  appPath: string,
  artifactRoot: string,
  patchIdsInput = "stable",
  runId = buildStandaloneRunId("patch-apply")
): Promise<PatchApplyPayload> {
  const root = path.resolve(artifactRoot);
  const targetPath = path.resolve(executablePath);
  assertArtifactContainedPath(targetPath, root, "catalog patch apply target");

  const [sourceData, catalog] = await Promise.all([fs.readFile(targetPath), loadPatchCatalog(appPath)]);
  const before = await verifyExecutablePath(targetPath, appPath);
  const patchIds = resolvePatchIds(before.rows, patchIdsInput);
  if (patchIds.length === 0) {
    throw new Error("Catalog patch apply must include at least one patch.");
  }

  const rows = patchIds.map((id) => {
    const verificationRow = before.rows.find((candidate) => candidate.spec.id === id);
    const spec = catalog.specs.find((candidate) => candidate.id === id);
    if (!verificationRow || !spec) {
      throw new Error(`Patch id is not in the catalog: ${id}`);
    }
    return { verificationRow, spec };
  });
  const blocked = rows.filter(({ verificationRow }) => verificationRow.state === "mismatch" || verificationRow.state === "out-of-range");
  if (blocked.length > 0) {
    throw new Error(`Catalog patch apply is blocked by unsafe current bytes: ${blocked.map(({ spec }) => spec.id).join(", ")}`);
  }

  const backupPath = `${targetPath}.original.backup`;
  let backupData = sourceData;
  try {
    backupData = await fs.readFile(backupPath);
  } catch {
    await fs.writeFile(backupPath, sourceData);
  }

  const candidate = Buffer.from(sourceData);
  for (const { verificationRow, spec } of rows) {
    if (verificationRow.state === "original") {
      spec.patchedBytes.copy(candidate, spec.fileOffset);
    }
  }

  const changed = !candidate.equals(sourceData);
  if (changed) {
    await fs.writeFile(targetPath, candidate);
  }

  const readback = await fs.readFile(targetPath);
  const readbackVerified = readback.equals(candidate);
  if (!readbackVerified) {
    throw new Error("Catalog patch apply read-back verification failed.");
  }

  const after = await verifyExecutablePath(targetPath, appPath);
  const payloadRows: PatchApplyPayload["rows"] = rows.map(({ verificationRow }) => {
    const afterRow = after.rows.find((candidateRow) => candidateRow.spec.id === verificationRow.spec.id);
    return {
      id: verificationRow.spec.id,
      title: verificationRow.spec.title,
      track: verificationRow.spec.track,
      optional: verificationRow.spec.optional,
      fileOffsetHex: verificationRow.spec.fileOffsetHex,
      byteLength: verificationRow.spec.byteLength,
      currentState: verificationRow.state,
      action: planActionFor(verificationRow.state),
      reason: planReasonFor(verificationRow.state),
      afterState: afterRow?.state ?? "mismatch"
    };
  });
  const notPatched = payloadRows.filter((row) => row.afterState !== "patched");
  if (notPatched.length > 0) {
    throw new Error(`Catalog patch apply post-write verification failed: ${notPatched.map((row) => row.id).join(", ")}`);
  }

  const generatedAt = new Date().toISOString();
  const payload: PatchApplyPayload = {
    schemaVersion: "patch-apply.v1",
    generatedAt,
    command: "apply-catalog-patch",
    mutation: true,
    input: {
      executablePath: targetPath,
      patchIds: patchIdsInput
    },
    target: {
      path: targetPath,
      fileName: path.basename(targetPath),
      fileSize: readback.length,
      beforeSha256: before.sha256,
      afterSha256: after.sha256,
      changed,
      readbackVerified
    },
    backup: {
      backupPath,
      sha256: sha256Buffer(backupData),
      fileSize: backupData.length
    },
    counts: {
      selected: payloadRows.length,
      applied: payloadRows.filter((row) => row.currentState === "original").length,
      alreadyApplied: payloadRows.filter((row) => row.currentState === "patched").length,
      blocked: 0
    },
    rows: payloadRows,
    verification: {
      before: verificationSnapshot(before),
      after: verificationSnapshot(after)
    },
    artifact: {
      kind: "local-file-write",
      mutation: true,
      schemaVersion: "patch-apply.v1",
      backupPath,
      note: "Applied curated patch bytes only to an artifact-root copied BEA.exe after byte preimage checks, backup, and read-back verification."
    }
  };

  const artifactPath = await writePatchMutationArtifact(root, "patch-apply", runId, "apply.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

export async function restoreCatalogPatchBackup(
  targetPathInput: string,
  backupPathInput: string,
  appPath: string,
  artifactRoot: string,
  runId = buildStandaloneRunId("patch-restore")
): Promise<PatchRestorePayload> {
  const root = path.resolve(artifactRoot);
  const targetPath = path.resolve(targetPathInput);
  const backupPath = path.resolve(backupPathInput);
  assertArtifactContainedPath(targetPath, root, "catalog patch restore target");
  assertArtifactContainedPath(backupPath, root, "catalog patch restore backup");
  const backupName = path.basename(backupPath).toLowerCase();
  if (
    path.basename(targetPath).toLowerCase() !== "bea.exe" ||
    (backupName !== "bea.exe.original.backup" && backupName !== "bea.exe.bak")
  ) {
    throw new Error("Catalog patch restore requires a copied BEA.exe target and a BEA.exe backup.");
  }

  const [beforeData, backupData] = await Promise.all([fs.readFile(targetPath), fs.readFile(backupPath)]);
  await verifyExecutablePath(targetPath, appPath);
  await verifyExecutableBuffer(backupData, backupPath, appPath);

  const preRestoreDir = path.join(root, "artifacts", "patch-restore", runId, "pre-restore-backup");
  const preRestoreBackupPath = path.join(preRestoreDir, `${path.basename(targetPath)}.pre-restore.bak`);
  await fs.mkdir(preRestoreDir, { recursive: true });
  await fs.writeFile(preRestoreBackupPath, beforeData);

  await fs.writeFile(targetPath, backupData);
  const readback = await fs.readFile(targetPath);
  const readbackVerified = readback.equals(backupData);
  if (!readbackVerified) {
    throw new Error("Catalog patch restore read-back verification failed.");
  }
  const after = await verifyExecutablePath(targetPath, appPath);

  const payload: PatchRestorePayload = {
    schemaVersion: "patch-restore.v1",
    generatedAt: new Date().toISOString(),
    command: "restore-catalog-patch-backup",
    mutation: true,
    input: {
      targetPath,
      backupPath
    },
    target: {
      path: targetPath,
      fileName: path.basename(targetPath),
      fileSize: readback.length,
      beforeSha256: sha256Buffer(beforeData),
      afterSha256: sha256Buffer(readback),
      readbackVerified
    },
    backup: {
      path: backupPath,
      fileName: path.basename(backupPath),
      fileSize: backupData.length,
      sha256: sha256Buffer(backupData)
    },
    preRestoreBackup: {
      backupPath: preRestoreBackupPath,
      sha256: sha256Buffer(beforeData),
      fileSize: beforeData.length
    },
    verification: verificationSnapshot(after),
    artifact: {
      kind: "local-file-write",
      mutation: true,
      schemaVersion: "patch-restore.v1",
      note: "Restored an artifact-root BEA.exe backup to an artifact-root copied target and retained a pre-restore backup."
    }
  };

  const artifactPath = await writePatchMutationArtifact(root, "patch-restore", runId, "restore.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

async function loadPatchCatalog(appPath: string): Promise<LoadedPatchCatalog> {
  const candidateRoots = [
    path.resolve(appPath),
    path.resolve(process.cwd()),
    path.resolve(process.cwd(), "..", "..")
  ];

  for (const root of candidateRoots) {
    const catalogPath = path.join(root, catalogRelativePath);
    try {
      const raw = await fs.readFile(catalogPath, "utf8");
      return parseCatalog(raw, catalogPath);
    } catch {
      // Keep looking through known app/dev roots.
    }
  }

  throw new Error(`Patch catalog not found: ${catalogRelativePath}`);
}

function resolvePatchIds(rows: PatchVerifyRow[], input: string) {
  const trimmed = input.trim();
  if (trimmed.length === 0 || trimmed.toLowerCase() === "stable") {
    return rows.filter((row) => String(row.spec.track).toLowerCase() === "stable").map((row) => row.spec.id);
  }
  if (trimmed.toLowerCase() === "all") {
    return rows.map((row) => row.spec.id);
  }

  const seen = new Set<string>();
  return trimmed
    .split(/[\s,;]+/)
    .map((id) => id.trim())
    .filter((id) => id.length > 0)
    .filter((id) => {
      if (seen.has(id)) {
        return false;
      }
      seen.add(id);
      return true;
    });
}

function planActionFor(state: PatchState): PatchPlanPayload["rows"][number]["action"] {
  switch (state) {
    case "original":
      return "would-apply";
    case "patched":
      return "already-applied";
    case "mismatch":
    case "out-of-range":
      return "blocked";
  }
}

function planReasonFor(state: PatchState) {
  switch (state) {
    case "original":
      return "Target bytes match expected original bytes.";
    case "patched":
      return "Target already contains the curated patched bytes.";
    case "mismatch":
      return "Target bytes are neither expected original nor patched bytes.";
    case "out-of-range":
      return "Patch offset is outside this executable specimen.";
  }
}

function parseCatalog(raw: string, catalogPath: string): LoadedPatchCatalog {
  const catalog = JSON.parse(raw) as CatalogJson;
  if (!Array.isArray(catalog.patches)) {
    throw new Error("Patch catalog is missing a patches array.");
  }

  const specs = catalog.patches.map((patch, index) => parsePatchSpec(patch as CatalogPatchJson, index));

  return {
    summary: {
      catalogVersion: stringValue(catalog.catalog_version, "unknown"),
      generatedAt: typeof catalog.generated_at === "string" ? catalog.generated_at : undefined,
      catalogPath,
      patchCount: specs.length
    },
    specs
  };
}

function parsePatchSpec(patch: CatalogPatchJson, index: number): ParsedPatchSpec {
  const id = requiredString(patch.id, `patches[${index}].id`);
  const title = requiredString(patch.title, `patches[${index}].title`);
  const trackRaw = requiredString(patch.track, `patches[${index}].track`);
  const fileOffset = parseOffset(patch.file_offset, `patches[${index}].file_offset`);
  const originalBytes = parseHexBytes(
    requiredString(patch.expected_original_bytes, `patches[${index}].expected_original_bytes`)
  );
  const patchedBytes = parseHexBytes(requiredString(patch.patched_bytes, `patches[${index}].patched_bytes`));

  if (originalBytes.length !== patchedBytes.length) {
    throw new Error(`Patch ${id} has unequal original/patched byte lengths.`);
  }

  return {
    id,
    title,
    track: normalizeTrack(trackRaw),
    fileOffset,
    fileOffsetHex: `0x${fileOffset.toString(16).toUpperCase()}`,
    byteLength: originalBytes.length,
    optional: patch.optional === true,
    purpose: typeof patch.purpose === "string" ? patch.purpose : undefined,
    originalBytes,
    patchedBytes
  };
}

function verifyPatch(data: Buffer, spec: ParsedPatchSpec): PatchVerifyRow {
  if (spec.fileOffset < 0 || spec.fileOffset + spec.byteLength > data.length) {
    return buildRow(spec, "out-of-range");
  }

  const currentBytes = data.subarray(spec.fileOffset, spec.fileOffset + spec.byteLength);
  if (currentBytes.equals(spec.patchedBytes)) {
    return buildRow(spec, "patched", currentBytes);
  }

  if (currentBytes.equals(spec.originalBytes)) {
    return buildRow(spec, "original", currentBytes);
  }

  return buildRow(spec, "mismatch", currentBytes);
}

function buildRow(spec: ParsedPatchSpec, state: PatchState, currentBytes?: Buffer): PatchVerifyRow {
  const { originalBytes: _originalBytes, patchedBytes: _patchedBytes, ...summary } = spec;
  return {
    spec: summary,
    state,
    stateLabel: stateLabel(state),
    tone: stateTone(state),
    currentBytesHex: currentBytes ? toHex(currentBytes) : undefined
  };
}

function normalizeTrack(track: string) {
  if (track.toLowerCase() === "stable") return "Stable";
  if (track.toLowerCase() === "experimental") return "Experimental";
  return track.trim();
}

function stateLabel(state: PatchState) {
  switch (state) {
    case "original":
      return "ready (original)";
    case "patched":
      return "already patched";
    case "mismatch":
      return "unexpected bytes";
    case "out-of-range":
      return "offset out of range";
  }
}

function stateTone(state: PatchState): PatchTone {
  switch (state) {
    case "original":
      return "ready";
    case "patched":
      return "applied";
    case "mismatch":
    case "out-of-range":
      return "danger";
  }
}

function requiredString(value: unknown, label: string) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`Expected string at ${label}.`);
  }
  return value.trim();
}

function stringValue(value: unknown, fallback: string) {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : fallback;
}

function parseOffset(value: unknown, label: string) {
  if (typeof value === "number" && Number.isInteger(value)) {
    return value;
  }

  if (typeof value !== "string") {
    throw new Error(`Expected numeric offset at ${label}.`);
  }

  const raw = value.trim();
  const parsed = raw.toLowerCase().startsWith("0x") ? Number.parseInt(raw.slice(2), 16) : Number.parseInt(raw, 10);
  if (!Number.isInteger(parsed) || parsed < 0) {
    throw new Error(`Invalid offset at ${label}: ${value}`);
  }

  return parsed;
}

function parseHexBytes(raw: string) {
  const tokens = raw.split(/[\s,;-]+/).filter(Boolean);
  const bytes = tokens.map((token) => {
    const normalized = token.toLowerCase().startsWith("0x") ? token.slice(2) : token;
    const value = Number.parseInt(normalized, 16);
    if (!Number.isInteger(value) || value < 0 || value > 0xff) {
      throw new Error(`Invalid hex byte: ${token}`);
    }
    return value;
  });

  if (bytes.length === 0) {
    throw new Error("Expected at least one hex byte.");
  }

  return Buffer.from(bytes);
}

function toHex(bytes: Buffer) {
  return Array.from(bytes)
    .map((byte) => byte.toString(16).padStart(2, "0").toUpperCase())
    .join(" ");
}

async function writeVerificationArtifact(
  summary: SpecimenVerificationSummary,
  artifactRoot: string
): Promise<SpecimenVerificationSummary> {
  const jobId = buildJobId(summary.verifiedAt, summary.sha256);
  const artifactDir = path.join(path.resolve(artifactRoot), "artifacts", "specimen-verification", jobId);
  const artifactPath = path.join(artifactDir, "verification.json");
  const summaryWithArtifact: SpecimenVerificationSummary = {
    ...summary,
    artifact: {
      ...summary.artifact,
      jobId,
      artifactPath
    }
  };

  const record = {
    schemaVersion: summary.artifact.schemaVersion,
    jobId,
    generatedAt: summary.verifiedAt,
    mutation: false,
    input: {
      selectedPath: summary.selectedPath,
      fileName: summary.fileName,
      fileSize: summary.fileSize,
      sha256: summary.sha256
    },
    result: summaryWithArtifact
  };

  await fs.mkdir(artifactDir, { recursive: true });
  await fs.writeFile(artifactPath, `${JSON.stringify(record, null, 2)}\n`, "utf8");
  return summaryWithArtifact;
}

async function writePatchPlanArtifact(summary: PatchPlanPayload, artifactRoot: string): Promise<PatchPlanPayload> {
  const jobId = buildPatchPlanJobId(summary.plannedAt, summary.sha256);
  const artifactDir = path.join(path.resolve(artifactRoot), "artifacts", "patch-plan", jobId);
  const artifactPath = path.join(artifactDir, "plan.json");
  const summaryWithArtifact: PatchPlanPayload = {
    ...summary,
    artifact: {
      ...summary.artifact,
      jobId,
      artifactPath
    }
  };

  const record = {
    schemaVersion: summary.artifact.schemaVersion,
    jobId,
    generatedAt: summary.plannedAt,
    mutation: false,
    input: {
      executablePath: summary.executablePath,
      fileName: summary.fileName,
      fileSize: summary.fileSize,
      sha256: summary.sha256,
      patchIds: summary.patchIds
    },
    result: summaryWithArtifact
  };

  await fs.mkdir(artifactDir, { recursive: true });
  await fs.writeFile(artifactPath, `${JSON.stringify(record, null, 2)}\n`, "utf8");
  return summaryWithArtifact;
}

function buildJobId(verifiedAt: string, sha256: string) {
  const compactTimestamp = verifiedAt.replace(/\D/g, "").slice(0, 14);
  return `specimen-${compactTimestamp}-${sha256.slice(0, 8)}`;
}

function buildPatchPlanJobId(plannedAt: string, sha256: string) {
  const compactTimestamp = plannedAt.replace(/\D/g, "").slice(0, 14);
  return `patch-plan-${compactTimestamp}-${sha256.slice(0, 8)}`;
}

async function verifyExecutableBuffer(data: Buffer, filePath: string, appPath: string): Promise<SpecimenVerificationSummary> {
  const tempRoot = await fs.mkdtemp(path.join(path.dirname(filePath), ".verify-"));
  const tempExe = path.join(tempRoot, "BEA.exe");
  try {
    await fs.writeFile(tempExe, data);
    return await verifyExecutablePath(tempExe, appPath);
  } finally {
    await fs.rm(tempRoot, { recursive: true, force: true });
  }
}

async function writePatchMutationArtifact(
  artifactRoot: string,
  family: string,
  runId: string,
  fileName: string,
  payload: unknown
) {
  const artifactDir = path.join(path.resolve(artifactRoot), "artifacts", family, runId);
  const artifactPath = path.join(artifactDir, fileName);
  await fs.mkdir(artifactDir, { recursive: true });
  await fs.writeFile(artifactPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  return artifactPath;
}

function verificationSnapshot(summary: SpecimenVerificationSummary) {
  return {
    counts: summary.counts,
    sha256: summary.sha256,
    isKnownRetailSteamHash: summary.isKnownRetailSteamHash
  };
}

function assertArtifactContainedPath(filePath: string, artifactRoot: string, label: string) {
  const resolvedRoot = path.resolve(artifactRoot);
  const resolvedPath = path.resolve(filePath);
  const relative = path.relative(resolvedRoot, resolvedPath);
  const insideRoot = relative !== "" && !relative.startsWith("..") && !path.isAbsolute(relative);
  if (!insideRoot) {
    throw new Error(`${label} must be inside the app artifact/profile root.`);
  }
}

function sha256Buffer(data: Buffer) {
  return createHash("sha256").update(data).digest("hex");
}

function buildStandaloneRunId(prefix: string) {
  return `${prefix}-${new Date().toISOString().replace(/\D/g, "").slice(0, 14)}`;
}
