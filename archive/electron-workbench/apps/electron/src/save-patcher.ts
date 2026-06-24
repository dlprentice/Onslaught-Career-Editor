import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import type {
  SaveComparisonRange,
  SaveCopyPayload,
  SavePatchApplyPayload,
  SavePatchPlanPayload,
  SavePatchPreviewPayload,
  SavePatchRestorePayload,
  SavePatchRequestInput
} from "@onslaught/contracts";
import { compareSaveBuffers, inspectSaveBuffer } from "./save-inspector";

const expectedFileSize = 10004;
const versionWord = 0x4bd1;
const careerBase = 0x0002;
const nodeBase = careerBase + 0x0004;
const linkBase = careerBase + 0x1904;
const goodieBase = careerBase + 0x1f44;
const killsBase = careerBase + 0x23f4;

const nodeSize = 64;
const nodeCount = 100;
const linkSize = 8;
const linkCount = 200;
const goodieDisplayableCount = 233;

const rankFloatBits = new Map<string, number>([
  ["S", 0x3f800000],
  ["A", 0x3f4ccccd],
  ["B", 0x3f19999a],
  ["C", 0x3eb33333],
  ["D", 0x3e19999a],
  ["E", 0x00000000],
  ["NONE", 0xbf800000]
]);

const killCategories = ["Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs"];

export function normalizeSavePatchInput(
  rawInput: Partial<SavePatchRequestInput> & Pick<SavePatchRequestInput, "path">
): SavePatchRequestInput {
  return {
    path: stringValue(rawInput.path, "path"),
    rank: normalizeRank(rawInput.rank ?? "S"),
    kills: validateKillCount(rawInput.kills ?? 100, "kills"),
    useNewGoodies: rawInput.useNewGoodies ?? false,
    killsOnly: rawInput.killsOnly ?? false,
    patchNodes: rawInput.patchNodes ?? true,
    patchLinks: rawInput.patchLinks ?? true,
    patchGoodies: rawInput.patchGoodies ?? true,
    patchKills: rawInput.patchKills ?? true,
    allowCareerSectionsOnOptionsFile: rawInput.allowCareerSectionsOnOptionsFile ?? false,
    levelRanks: normalizeLevelRanks(rawInput.levelRanks ?? []),
    perCategoryKills: normalizePerCategoryKills(rawInput.perCategoryKills ?? [])
  };
}

export async function prepareSaveCopyPath(
  sourcePathInput: string,
  artifactRoot: string,
  runId = buildStandaloneRunId("save-copy")
): Promise<SaveCopyPayload> {
  const root = path.resolve(artifactRoot);
  const sourcePath = path.resolve(stringValue(sourcePathInput, "sourcePath"));
  if (!isSupportedSavePath(sourcePath)) {
    throw new Error("Copy source must be a .bes career save, .bea options file, or defaultoptions.bea backup.");
  }

  const sourceData = await fs.readFile(sourcePath);
  assertValidSaveBuffer(sourceData, "copy source");
  const sourceInspection = inspectSaveBuffer(sourcePath, sourceData);

  const targetDir = path.join(root, "artifacts", "save-copy", runId, "target");
  const targetPath = path.join(targetDir, path.basename(sourcePath));
  await fs.mkdir(targetDir, { recursive: true });
  await fs.writeFile(targetPath, sourceData);

  const readback = await fs.readFile(targetPath);
  const readbackVerified = readback.equals(sourceData);
  if (!readbackVerified) {
    throw new Error("Save copy read-back verification failed.");
  }
  const copiedInspection = inspectSaveBuffer(targetPath, readback);
  const payload: SaveCopyPayload = {
    schemaVersion: "save-copy.v1",
    generatedAt: new Date().toISOString(),
    command: "copy-save-file",
    mutation: false,
    input: {
      sourcePath
    },
    source: {
      path: sourcePath,
      fileName: path.basename(sourcePath),
      fileSize: sourceData.length,
      sha256: sha256Buffer(sourceData),
      isValid: sourceInspection.isValid,
      isOptionsFile: sourceInspection.isOptionsFile,
      versionWordHex: sourceInspection.versionWordHex,
      versionValid: sourceInspection.versionValid
    },
    copy: {
      path: targetPath,
      fileName: path.basename(targetPath),
      fileSize: readback.length,
      sha256: sha256Buffer(readback),
      readbackVerified
    },
    inspection: {
      completedNodes: copiedInspection.counts.completedNodes,
      displayableGoodiesUnlocked: copiedInspection.goodies.displayableUnlocked,
      totalKills: totalKills(copiedInspection.kills),
      optionsEntryCount: copiedInspection.options.entryCount
    },
    artifact: {
      kind: "local-file-copy",
      mutation: false,
      schemaVersion: "save-copy.v1",
      note: "Copied a valid save/options file into the app artifact root. The source file was not modified."
    }
  };

  const artifactPath = await writePatchArtifact(root, "save-copy", runId, "copy.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

export async function planSavePatchPath(
  rawInput: Partial<SavePatchRequestInput> & Pick<SavePatchRequestInput, "path">,
  artifactRoot?: string,
  runId = buildStandaloneRunId("save-patch-plan")
): Promise<SavePatchPlanPayload> {
  const input = normalizeSavePatchInput(rawInput);
  const prepared = await preparePatchSource(input);
  const sections = plannedPatchSections(input);
  const payload: SavePatchPlanPayload = {
    schemaVersion: "save-patch-plan.v1",
    generatedAt: new Date().toISOString(),
    command: "plan-save-patch",
    mutation: false,
    input,
    source: prepared.source,
    current: prepared.current,
    plan: {
      accepted: true,
      targetKind: prepared.source.isOptionsFile ? "global-options" : "career-save",
      sections,
      sectionCount: sections.length,
      levelRankCount: input.levelRanks.length,
      perCategoryKillCount: input.perCategoryKills.length,
      willPatchCareerSections: hasCareerSectionPatches(input),
      requiresCopiedApply: true,
      sourceUnchanged: true,
      notes: [
        "Plan-only TypeScript payload. No source bytes were changed.",
        "Future apply jobs must run against an explicit copied target or backup-backed workflow.",
        "This native plan mirrors the AppCore request subset before C#/Python archival."
      ]
    },
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "save-patch-plan.v1",
      note: "Read-only TypeScript save/options patch plan. The source file was not modified."
    }
  };

  if (!artifactRoot) {
    return payload;
  }

  const artifactPath = await writePatchArtifact(artifactRoot, "save-patch-plan", runId, "plan.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

export async function previewSavePatchPath(
  rawInput: Partial<SavePatchRequestInput> & Pick<SavePatchRequestInput, "path">,
  artifactRoot?: string,
  runId = buildStandaloneRunId("save-patch-preview")
): Promise<SavePatchPreviewPayload> {
  const input = normalizeSavePatchInput(rawInput);
  const prepared = await preparePatchSource(input);
  const candidate = Buffer.from(prepared.data);
  applySavePatchBuffer(candidate, input);

  const candidatePath = artifactRoot
    ? path.join(path.resolve(artifactRoot), "artifacts", "save-patch-preview", runId, `candidate${path.extname(prepared.path) || ".bes"}`)
    : `${prepared.path}.candidate`;
  const candidateSha256 = sha256Buffer(candidate);
  const after = inspectSaveBuffer(candidatePath, candidate);
  const comparison = compareSaveBuffers(prepared.path, candidatePath, prepared.data, candidate);
  const topRegion = comparison.topRegions[0]?.region;
  const payload: SavePatchPreviewPayload = {
    schemaVersion: "save-patch-preview.v1",
    generatedAt: new Date().toISOString(),
    command: "preview-save-patch",
    mutation: false,
    input,
    source: prepared.source,
    preview: {
      success: true,
      message: "TypeScript save patch preview completed against an artifact-owned candidate copy.",
      wouldChange: comparison.differingBytes > 0,
      tempOutputDeleted: false,
      candidateSha256,
      differingBytes: comparison.differingBytes,
      topRegion,
      candidateArtifactPath: artifactRoot ? candidatePath : undefined
    },
    beforeAfter: {
      completedNodes: { before: prepared.before.counts.completedNodes, after: after.counts.completedNodes },
      partialNodes: { before: prepared.before.counts.partialNodes, after: after.counts.partialNodes },
      displayableGoodiesUnlocked: {
        before: prepared.before.goodies.displayableUnlocked,
        after: after.goodies.displayableUnlocked
      },
      totalKills: {
        before: totalKills(prepared.before.kills),
        after: totalKills(after.kills)
      },
      rankDistribution: {
        before: prepared.before.rankDistribution,
        after: after.rankDistribution
      }
    },
    comparison: {
      sameSize: comparison.sameSize,
      identical: comparison.identical,
      differingBytes: comparison.differingBytes,
      topRegions: comparison.topRegions,
      diffRanges: comparison.diffRanges.map(withExclusiveEnd)
    },
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "save-patch-preview.v1",
      candidateArtifactPath: artifactRoot ? candidatePath : undefined,
      note: "Read-only TypeScript save/options patch preview. The source file was not modified; the candidate is an artifact copy."
    }
  };

  if (!artifactRoot) {
    return payload;
  }

  await fs.mkdir(path.dirname(candidatePath), { recursive: true });
  await fs.writeFile(candidatePath, candidate);
  const artifactPath = await writePatchArtifact(artifactRoot, "save-patch-preview", runId, "preview.json", payload);
  return {
    ...payload,
    preview: {
      ...payload.preview,
      candidateArtifactPath: candidatePath
    },
    artifact: {
      ...payload.artifact,
      artifactPath,
      candidateArtifactPath: candidatePath
    }
  };
}

export async function applySavePatchPath(
  rawInput: Partial<SavePatchRequestInput> & Pick<SavePatchRequestInput, "path">,
  artifactRoot: string,
  runId = buildStandaloneRunId("save-patch-apply")
): Promise<SavePatchApplyPayload> {
  const root = path.resolve(artifactRoot);
  const input = normalizeSavePatchInput(rawInput);
  assertArtifactContainedPath(input.path, root, "save patch apply target");

  const prepared = await preparePatchSource(input);
  const candidate = Buffer.from(prepared.data);
  applySavePatchBuffer(candidate, input);
  const changed = !candidate.equals(prepared.data);

  const backupDir = path.join(root, "artifacts", "save-patch-apply", runId, "backup");
  const backupPath = path.join(backupDir, `${path.basename(prepared.path)}.bak`);
  await fs.mkdir(backupDir, { recursive: true });
  await fs.writeFile(backupPath, prepared.data);

  if (changed) {
    await fs.writeFile(prepared.path, candidate);
  }

  const readback = await fs.readFile(prepared.path);
  const readbackVerified = readback.equals(candidate);
  if (!readbackVerified) {
    throw new Error("Save patch apply read-back verification failed.");
  }

  const after = inspectSaveBuffer(prepared.path, readback);
  const comparison = compareSaveBuffers(backupPath, prepared.path, prepared.data, readback);
  const payload: SavePatchApplyPayload = {
    schemaVersion: "save-patch-apply.v1",
    generatedAt: new Date().toISOString(),
    command: "apply-save-patch",
    mutation: true,
    input,
    target: {
      ...prepared.source,
      path: prepared.path,
      changed,
      beforeSha256: prepared.source.sha256,
      afterSha256: sha256Buffer(readback),
      readbackVerified
    },
    backup: {
      backupPath,
      sha256: sha256Buffer(prepared.data),
      fileSize: prepared.data.length
    },
    beforeAfter: {
      completedNodes: { before: prepared.before.counts.completedNodes, after: after.counts.completedNodes },
      partialNodes: { before: prepared.before.counts.partialNodes, after: after.counts.partialNodes },
      displayableGoodiesUnlocked: {
        before: prepared.before.goodies.displayableUnlocked,
        after: after.goodies.displayableUnlocked
      },
      totalKills: {
        before: totalKills(prepared.before.kills),
        after: totalKills(after.kills)
      },
      rankDistribution: {
        before: prepared.before.rankDistribution,
        after: after.rankDistribution
      }
    },
    comparison: {
      sameSize: comparison.sameSize,
      identical: comparison.identical,
      differingBytes: comparison.differingBytes,
      topRegions: comparison.topRegions,
      diffRanges: comparison.diffRanges.map(withExclusiveEnd)
    },
    artifact: {
      kind: "local-file-write",
      mutation: true,
      schemaVersion: "save-patch-apply.v1",
      backupPath,
      note: "Applied a TypeScript save/options patch only to an artifact-root copied target after writing a backup and verifying read-back bytes."
    }
  };

  const artifactPath = await writePatchArtifact(root, "save-patch-apply", runId, "apply.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

export async function restoreSaveBackupPath(
  targetPathInput: string,
  backupPathInput: string,
  artifactRoot: string,
  runId = buildStandaloneRunId("save-patch-restore")
): Promise<SavePatchRestorePayload> {
  const root = path.resolve(artifactRoot);
  const targetPath = path.resolve(stringValue(targetPathInput, "targetPath"));
  const backupPath = path.resolve(stringValue(backupPathInput, "backupPath"));
  assertArtifactContainedPath(targetPath, root, "save restore target");
  assertArtifactContainedPath(backupPath, root, "save restore backup");
  if (!isSupportedSavePath(targetPath)) {
    throw new Error("Restore target must be a .bes career save, .bea options file, or defaultoptions.bea backup.");
  }

  const backupData = await fs.readFile(backupPath);
  assertValidSaveBuffer(backupData, "restore backup");
  const beforeData = await fs.readFile(targetPath);
  assertValidSaveBuffer(beforeData, "restore target");

  const preRestoreDir = path.join(root, "artifacts", "save-patch-restore", runId, "pre-restore-backup");
  const preRestoreBackupPath = path.join(preRestoreDir, `${path.basename(targetPath)}.pre-restore.bak`);
  await fs.mkdir(preRestoreDir, { recursive: true });
  await fs.writeFile(preRestoreBackupPath, beforeData);

  await fs.writeFile(targetPath, backupData);
  const readback = await fs.readFile(targetPath);
  const readbackVerified = readback.equals(backupData);
  if (!readbackVerified) {
    throw new Error("Save restore read-back verification failed.");
  }

  const payload: SavePatchRestorePayload = {
    schemaVersion: "save-patch-restore.v1",
    generatedAt: new Date().toISOString(),
    command: "restore-save-backup",
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
    artifact: {
      kind: "local-file-write",
      mutation: true,
      schemaVersion: "save-patch-restore.v1",
      note: "Restored an artifact-root backup to an artifact-root copied target and retained a pre-restore backup."
    }
  };

  const artifactPath = await writePatchArtifact(root, "save-patch-restore", runId, "restore.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

export function applySavePatchBuffer(data: Buffer, input: SavePatchRequestInput): Buffer {
  if (data.length !== expectedFileSize) {
    throw new Error(`Invalid save/options size: expected ${expectedFileSize} bytes, got ${data.length}.`);
  }
  if (data.readUInt16LE(0) !== versionWord) {
    throw new Error(`Invalid save/options version word: ${toHex16(data.readUInt16LE(0))}; expected ${toHex16(versionWord)}.`);
  }

  if (input.killsOnly) {
    patchKills(data, input);
    return data;
  }

  if (input.patchNodes) {
    patchNodes(data, input);
  }
  if (input.patchLinks) {
    patchLinks(data);
  }
  if (input.patchGoodies) {
    patchGoodies(data, input.useNewGoodies);
  }
  if (input.patchKills) {
    patchKills(data, input);
  }
  return data;
}

function assertValidSaveBuffer(data: Buffer, label: string) {
  if (data.length !== expectedFileSize) {
    throw new Error(`Invalid ${label} size: expected ${expectedFileSize} bytes, got ${data.length}.`);
  }
  if (data.readUInt16LE(0) !== versionWord) {
    throw new Error(`Invalid ${label} version word: ${toHex16(data.readUInt16LE(0))}; expected ${toHex16(versionWord)}.`);
  }
}

async function preparePatchSource(input: SavePatchRequestInput) {
  const normalizedPath = path.resolve(input.path);
  if (!isSupportedSavePath(normalizedPath)) {
    throw new Error("Input must be a .bes career save, .bea options file, or defaultoptions.bea backup.");
  }

  const data = await fs.readFile(normalizedPath);
  if (data.length !== expectedFileSize) {
    throw new Error(`Invalid save/options size: expected ${expectedFileSize} bytes, got ${data.length}.`);
  }
  const fileVersionWord = data.readUInt16LE(0);
  if (fileVersionWord !== versionWord) {
    throw new Error(`Invalid save/options version word: ${toHex16(fileVersionWord)}; expected ${toHex16(versionWord)}.`);
  }
  if (isOptionsLikePath(normalizedPath) && hasCareerSectionPatches(input) && !input.allowCareerSectionsOnOptionsFile) {
    throw new Error(
      "Career section patching is blocked for .bea/defaultoptions files by default. Disable career sections or set allowCareerSectionsOnOptionsFile intentionally."
    );
  }
  if (input.killsOnly && !input.patchKills) {
    throw new Error("killsOnly cannot be combined with patchKills=false.");
  }

  const before = inspectSaveBuffer(normalizedPath, data);
  const source = {
    path: normalizedPath,
    fileName: path.basename(normalizedPath),
    fileSize: data.length,
    sha256: sha256Buffer(data),
    isValid: before.isValid,
    isOptionsFile: before.isOptionsFile,
    versionWordHex: before.versionWordHex,
    versionValid: before.versionValid
  };
  const current = {
    completedNodes: before.counts.completedNodes,
    partialNodes: before.counts.partialNodes,
    displayableGoodiesUnlocked: before.goodies.displayableUnlocked,
    totalKills: totalKills(before.kills),
    kills: before.kills.map((row) => ({
      categoryIndex: row.categoryIndex,
      categoryName: row.categoryName,
      kills: row.kills,
      meta: row.meta
    })),
    rankDistribution: before.rankDistribution
  };

  return {
    path: normalizedPath,
    data,
    before,
    source,
    current
  };
}

function patchNodes(data: Buffer, input: SavePatchRequestInput) {
  const levelRanks = new Map(input.levelRanks.map((row) => [row.nodeIndex - 1, row.rank]));
  for (let index = 0; index < nodeCount; index++) {
    const offset = nodeBase + index * nodeSize;
    const world = data.readUInt32LE(offset + 0x10);
    if (world === 0) {
      continue;
    }

    const rank = levelRanks.get(index) ?? input.rank;
    data.writeUInt32LE(1, offset + 0x04);
    data.writeUInt32LE(0, offset + 0x38);
    data.writeUInt32LE(rankBits(rank), offset + 0x3c);
  }
}

function patchLinks(data: Buffer) {
  for (let index = 0; index < linkCount; index++) {
    const offset = linkBase + index * linkSize;
    const current = data.readUInt32LE(offset);
    const toNode = data.readUInt32LE(offset + 4);
    if (toNode === 0xffffffff || current !== 0) {
      continue;
    }
    data.writeUInt32LE(1, offset);
  }
}

function patchGoodies(data: Buffer, useNewGoodies: boolean) {
  const state = useNewGoodies ? 2 : 3;
  for (let index = 0; index < goodieDisplayableCount; index++) {
    data.writeUInt32LE(state, goodieBase + index * 4);
  }
}

function patchKills(data: Buffer, input: SavePatchRequestInput) {
  const perCategory = new Map(input.perCategoryKills.map((row) => [row.categoryIndex, row.kills]));
  for (let index = 0; index < killCategories.length; index++) {
    const offset = killsBase + index * 4;
    const current = data.readUInt32LE(offset);
    const meta = current & 0xff000000;
    const kills = validateKillCount(perCategory.get(index) ?? input.kills, `kills.${index}`);
    data.writeUInt32LE((meta | (kills & 0x00ffffff)) >>> 0, offset);
  }
}

function plannedPatchSections(input: SavePatchRequestInput) {
  if (input.killsOnly) {
    return ["kills"];
  }
  const sections: string[] = [];
  if (input.patchNodes) sections.push("nodes");
  if (input.patchLinks) sections.push("links");
  if (input.patchGoodies) sections.push("goodies");
  if (input.patchKills) sections.push("kills");
  return sections;
}

function hasCareerSectionPatches(input: SavePatchRequestInput) {
  return input.killsOnly || input.patchNodes || input.patchLinks || input.patchGoodies || input.patchKills;
}

function normalizeLevelRanks(rows: SavePatchRequestInput["levelRanks"]) {
  const byNode = new Map<number, string>();
  for (const row of rows) {
    if (!Number.isSafeInteger(row.nodeIndex) || row.nodeIndex < 1 || row.nodeIndex > 43) {
      throw new Error(`Invalid level rank node index ${row.nodeIndex}; expected 1-43.`);
    }
    byNode.set(row.nodeIndex, normalizeRank(row.rank));
  }
  return [...byNode.entries()]
    .sort((left, right) => left[0] - right[0])
    .map(([nodeIndex, rank]) => ({ nodeIndex, rank }));
}

function normalizePerCategoryKills(rows: SavePatchRequestInput["perCategoryKills"]) {
  const byCategory = new Map<number, { categoryName: string; kills: number }>();
  for (const row of rows) {
    if (!Number.isSafeInteger(row.categoryIndex) || row.categoryIndex < 0 || row.categoryIndex >= killCategories.length) {
      throw new Error(`Invalid kill category ${row.categoryIndex}; expected 0-${killCategories.length - 1}.`);
    }
    byCategory.set(row.categoryIndex, {
      categoryName: killCategories[row.categoryIndex],
      kills: validateKillCount(row.kills, `perCategoryKills.${row.categoryIndex}`)
    });
  }
  return [...byCategory.entries()]
    .sort((left, right) => left[0] - right[0])
    .map(([categoryIndex, row]) => ({ categoryIndex, categoryName: row.categoryName, kills: row.kills }));
}

function normalizeRank(value: string) {
  const rank = stringValue(value, "rank").toUpperCase();
  if (!rankFloatBits.has(rank)) {
    throw new Error(`Invalid save patch rank: ${value}.`);
  }
  return rank;
}

function rankBits(rank: string) {
  return rankFloatBits.get(normalizeRank(rank)) ?? rankFloatBits.get("S")!;
}

function validateKillCount(value: number, label: string) {
  if (!Number.isSafeInteger(value) || value < 0 || value > 0x00ffffff) {
    throw new Error(`${label} must be an integer from 0 to 16777215.`);
  }
  return value;
}

function stringValue(value: string, label: string) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`Save patch ${label} is required.`);
  }
  return value.trim();
}

function totalKills(rows: Array<{ kills: number }>) {
  return rows.reduce((sum, row) => sum + row.kills, 0);
}

function isSupportedSavePath(filePath: string) {
  const fileName = path.basename(filePath).toLowerCase();
  const extension = path.extname(fileName);
  return extension === ".bes" || extension === ".bea" || fileName.startsWith("defaultoptions.bea");
}

function isOptionsLikePath(filePath: string) {
  const fileName = path.basename(filePath).toLowerCase();
  return path.extname(fileName) === ".bea" || fileName.startsWith("defaultoptions.bea");
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

function withExclusiveEnd(range: SaveComparisonRange) {
  const start = parseHexOffset(range.startOffsetHex);
  return {
    ...range,
    endOffsetExclusiveHex: toHexOffset(start + range.byteLength)
  };
}

async function writePatchArtifact(
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

function sha256Buffer(data: Buffer) {
  return createHash("sha256").update(data).digest("hex");
}

function buildStandaloneRunId(prefix: string) {
  return `${prefix}-${new Date().toISOString().replace(/\D/g, "").slice(0, 14)}`;
}

function parseHexOffset(value: string) {
  const raw = value.trim().toLowerCase();
  return raw.startsWith("0x") ? Number.parseInt(raw.slice(2), 16) : Number.parseInt(raw, 10);
}

function toHexOffset(value: number) {
  return `0x${value.toString(16).toUpperCase()}`;
}

function toHex16(value: number) {
  return `0x${value.toString(16).toUpperCase().padStart(4, "0")}`;
}
