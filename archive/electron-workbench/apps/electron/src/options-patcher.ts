import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import type {
  OptionsPatchApplyPayload,
  OptionsPatchKeybindOverride,
  OptionsPatchPlanPayload,
  OptionsPatchPreviewPayload,
  OptionsPatchRequestInput,
  OptionsPatchSnapshot,
  SaveComparisonRange
} from "@onslaught/contracts";
import { compareSaveBuffers, inspectSaveBuffer } from "./save-inspector";

const expectedFileSize = 10004;
const versionWord = 0x4bd1;
const careerBase = 0x0002;
const soundVolumeOffset = careerBase + 0x248c;
const musicVolumeOffset = careerBase + 0x2490;
const flightInvertYP1Offset = careerBase + 0x249c;
const flightInvertYP2Offset = careerBase + 0x24a0;
const walkerInvertYP1Offset = careerBase + 0x24a4;
const walkerInvertYP2Offset = careerBase + 0x24a8;
const vibrationP1Offset = careerBase + 0x24ac;
const vibrationP2Offset = careerBase + 0x24b0;
const controllerConfigP1Offset = careerBase + 0x24b4;
const controllerConfigP2Offset = careerBase + 0x24b8;

const optionsStart = 0x24be;
const optionsBaseSize = 0x2514;
const optionsEntrySize = 0x20;
const optionsTailSize = 0x56;

interface OptionsLayout {
  entryCount: number;
  tailStart: number;
  entriesSize: number;
  tailSize: number;
}

interface BindingSlotPatch {
  deviceCode: number;
  packedKey: number;
}

interface NormalizedOptionsEntryOverride {
  entryId: number;
  actionName: string;
  slot0?: BindingSlotPatch;
  slot1?: BindingSlotPatch;
}

interface KeybindDefinition {
  slug: string;
  aliases: string[];
  groupLabel: string;
  actionLabel: string;
  entryId: number;
  keyboardDeviceCode: number;
  allowLookMouse: boolean;
  allowZoomWheel: boolean;
  allowMouseButtons: boolean;
  mirrorEntryId?: number;
  mirrorKeyboardDeviceCode?: number;
}

const keybindDefinitions: KeybindDefinition[] = [
  definition("move-forward", ["forward", "movement-forward"], "Movement", "Forward", 0x1f, 9),
  definition("move-backward", ["backward", "movement-backward"], "Movement", "Backward", 0x20, 9),
  definition("move-left", ["movement-left"], "Movement", "Left", 0x1d, 9),
  definition("move-right", ["movement-right"], "Movement", "Right", 0x1e, 9),
  definition("look-up", ["view-up"], "Look", "Up", 0x1a, 9, { allowLookMouse: true }),
  definition("look-down", ["view-down"], "Look", "Down", 0x1c, 9, { allowLookMouse: true }),
  definition("look-left", ["view-left"], "Look", "Left", 0x19, 9, { allowLookMouse: true }),
  definition("look-right", ["view-right"], "Look", "Right", 0x1b, 9, { allowLookMouse: true }),
  definition("zoom-in", ["zoom"], "Zoom", "In", 0x10, 9, { allowZoomWheel: true }),
  definition("zoom-out", [], "Zoom", "Out", 0x11, 9, { allowZoomWheel: true }),
  definition("fire-weapon", ["fire", "primary-fire"], "Actions", "Fire weapon", 0x12, 10, {
    allowMouseButtons: true,
    mirrorEntryId: 0x13,
    mirrorKeyboardDeviceCode: 9
  }),
  definition("fire-weapon-b", ["fire-b", "secondary-fire-entry"], "Actions", "Fire weapon (B)", 0x13, 9, {
    allowMouseButtons: true
  }),
  definition("select-weapon", ["weapon-select"], "Actions", "Select weapon", 0x14, 10, {
    allowMouseButtons: true
  }),
  definition("transform", ["toggle-transform"], "Actions", "Transform", 0x21, 8),
  definition("air-brake", ["airbrake", "brake"], "Actions", "Air brake", 0x15, 9),
  definition("special-function", ["special"], "Actions", "Special function", 0x3b, 8)
];

const definitionsByEntryId = new Map(keybindDefinitions.map((row) => [row.entryId, row]));
const definitionsByAction = new Map<string, KeybindDefinition>();
for (const row of keybindDefinitions) {
  definitionsByAction.set(normalizeActionKey(row.slug), row);
  definitionsByAction.set(normalizeActionKey(`${row.groupLabel}-${row.actionLabel}`), row);
  definitionsByAction.set(normalizeActionKey(row.actionLabel), row);
  for (const alias of row.aliases) {
    definitionsByAction.set(normalizeActionKey(alias), row);
  }
}

const keyNameMap = new Map<string, { vk: number; scan: number }>([
  ["UP", { vk: 0, scan: 0x00c8 }],
  ["DOWN", { vk: 0, scan: 0x00d0 }],
  ["LEFT", { vk: 0, scan: 0x00cb }],
  ["RIGHT", { vk: 0, scan: 0x00cd }],
  ["TAB", { vk: 0, scan: 0x000f }],
  ["SPACE", { vk: " ".charCodeAt(0), scan: 0x0039 }],
  ["CAPSLOCK", { vk: 0, scan: 0x003a }],
  ["LSHIFT", { vk: 0, scan: 0x002a }],
  ["RSHIFT", { vk: 0, scan: 0x0036 }],
  ["RCONTROL", { vk: 0, scan: 0x009d }],
  ["MINUS", { vk: "-".charCodeAt(0), scan: 0x000c }],
  ["-", { vk: "-".charCodeAt(0), scan: 0x000c }],
  ["EQUALS", { vk: "=".charCodeAt(0), scan: 0x000d }],
  ["=", { vk: "=".charCodeAt(0), scan: 0x000d }],
  ["+", { vk: "+".charCodeAt(0), scan: 0x000d }]
]);

const letterScan = new Map<string, number>([
  ["A", 0x001e],
  ["B", 0x0030],
  ["C", 0x002e],
  ["D", 0x0020],
  ["E", 0x0012],
  ["F", 0x0021],
  ["G", 0x0022],
  ["H", 0x0023],
  ["I", 0x0017],
  ["J", 0x0024],
  ["K", 0x0025],
  ["L", 0x0026],
  ["M", 0x0032],
  ["N", 0x0031],
  ["O", 0x0018],
  ["P", 0x0019],
  ["Q", 0x0010],
  ["R", 0x0013],
  ["S", 0x001f],
  ["T", 0x0014],
  ["U", 0x0016],
  ["V", 0x002f],
  ["W", 0x0011],
  ["X", 0x002d],
  ["Y", 0x0015],
  ["Z", 0x002c]
]);

const digitScan = new Map<string, number>([
  ["1", 0x0002],
  ["2", 0x0003],
  ["3", 0x0004],
  ["4", 0x0005],
  ["5", 0x0006],
  ["6", 0x0007],
  ["7", 0x0008],
  ["8", 0x0009],
  ["9", 0x000a],
  ["0", 0x000b]
]);

const numpadDigitScan = new Map<string, number>([
  ["7", 0x0047],
  ["8", 0x0048],
  ["9", 0x0049],
  ["4", 0x004b],
  ["5", 0x004c],
  ["6", 0x004d],
  ["1", 0x004f],
  ["2", 0x0050],
  ["3", 0x0051],
  ["0", 0x0052]
]);

export function normalizeOptionsPatchInput(
  rawInput: Partial<OptionsPatchRequestInput> & Pick<OptionsPatchRequestInput, "path">
): OptionsPatchRequestInput {
  const copyOptionsFromPath = optionalStringValue(rawInput.copyOptionsFromPath ?? null);
  const copyOptionsEntries = copyOptionsFromPath ? rawInput.copyOptionsEntries ?? true : false;
  const copyOptionsTail = copyOptionsFromPath ? rawInput.copyOptionsTail ?? true : false;
  if (copyOptionsFromPath && !copyOptionsEntries && !copyOptionsTail) {
    throw new Error("Options copy requires copyOptionsEntries or copyOptionsTail.");
  }

  return {
    path: stringValue(rawInput.path, "path"),
    soundVolume: normalizeOptionalUnitFloat(rawInput.soundVolume, "soundVolume"),
    musicVolume: normalizeOptionalUnitFloat(rawInput.musicVolume, "musicVolume"),
    invertWalkerP1: normalizeOptionalBoolean(rawInput.invertWalkerP1, "invertWalkerP1"),
    invertWalkerP2: normalizeOptionalBoolean(rawInput.invertWalkerP2, "invertWalkerP2"),
    invertFlightP1: normalizeOptionalBoolean(rawInput.invertFlightP1, "invertFlightP1"),
    invertFlightP2: normalizeOptionalBoolean(rawInput.invertFlightP2, "invertFlightP2"),
    vibrationP1: normalizeOptionalBoolean(rawInput.vibrationP1, "vibrationP1"),
    vibrationP2: normalizeOptionalBoolean(rawInput.vibrationP2, "vibrationP2"),
    controllerConfigP1: normalizeOptionalUInt32(rawInput.controllerConfigP1, "controllerConfigP1"),
    controllerConfigP2: normalizeOptionalUInt32(rawInput.controllerConfigP2, "controllerConfigP2"),
    mouseSensitivity: normalizeOptionalFiniteFloat(rawInput.mouseSensitivity, "mouseSensitivity", 0, 10),
    controlSchemeIndex: normalizeOptionalUInt16(rawInput.controlSchemeIndex, "controlSchemeIndex"),
    languageIndex: normalizeOptionalUInt16(rawInput.languageIndex, "languageIndex"),
    screenShape: normalizeOptionalUInt32(rawInput.screenShape, "screenShape"),
    d3dDeviceIndex: normalizeOptionalUInt32(rawInput.d3dDeviceIndex, "d3dDeviceIndex"),
    copyOptionsFromPath,
    copyOptionsEntries,
    copyOptionsTail,
    keybindOverrides: normalizeKeybindRequestRows(rawInput.keybindOverrides ?? [])
  };
}

export async function planOptionsPatchPath(
  rawInput: Partial<OptionsPatchRequestInput> & Pick<OptionsPatchRequestInput, "path">,
  artifactRoot?: string,
  runId = buildStandaloneRunId("options-patch-plan")
): Promise<OptionsPatchPlanPayload> {
  const input = normalizeOptionsPatchInput(rawInput);
  const prepared = await prepareOptionsPatchSource(input);
  const sections = plannedOptionsSections(input);
  const payload: OptionsPatchPlanPayload = {
    schemaVersion: "options-patch-plan.v1",
    generatedAt: new Date().toISOString(),
    command: "plan-options-patch",
    mutation: false,
    input,
    source: prepared.source,
    current: prepared.current,
    plan: {
      accepted: true,
      targetKind: "global-options",
      sections,
      sectionCount: sections.length,
      settingsOverrideCount: countSettingsOverrides(input),
      tailOverrideCount: countTailOverrides(input),
      keybindOverrideCount: input.keybindOverrides.length,
      copyOptionsEntries: input.copyOptionsFromPath !== null && input.copyOptionsEntries,
      copyOptionsTail: input.copyOptionsFromPath !== null && input.copyOptionsTail,
      requiresCopiedApply: true,
      sourceUnchanged: true,
      notes: [
        "Plan-only TypeScript payload. No source bytes were changed.",
        "Target is restricted to .bea/defaultoptions files because defaultoptions.bea is authoritative at boot.",
        "Apply jobs must run against an explicit artifact-root copied target."
      ]
    },
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "options-patch-plan.v1",
      note: "Read-only TypeScript global-options patch plan. The source file was not modified."
    }
  };

  if (!artifactRoot) {
    return payload;
  }

  const artifactPath = await writeOptionsPatchArtifact(artifactRoot, "options-patch-plan", runId, "plan.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

export async function previewOptionsPatchPath(
  rawInput: Partial<OptionsPatchRequestInput> & Pick<OptionsPatchRequestInput, "path">,
  artifactRoot?: string,
  runId = buildStandaloneRunId("options-patch-preview")
): Promise<OptionsPatchPreviewPayload> {
  const input = normalizeOptionsPatchInput(rawInput);
  const prepared = await prepareOptionsPatchSource(input);
  const candidate = Buffer.from(prepared.data);
  applyOptionsPatchBuffer(candidate, input, prepared.copyOptionsData);

  const candidatePath = artifactRoot
    ? path.join(path.resolve(artifactRoot), "artifacts", "options-patch-preview", runId, `candidate${optionsExtension(prepared.path)}`)
    : `${prepared.path}.candidate`;
  const candidateSha256 = sha256Buffer(candidate);
  const afterInspection = inspectSaveBuffer(candidatePath, candidate);
  const after = snapshotFromInspection(afterInspection);
  const comparison = compareSaveBuffers(prepared.path, candidatePath, prepared.data, candidate);
  const topRegion = comparison.topRegions[0]?.region;
  const payload: OptionsPatchPreviewPayload = {
    schemaVersion: "options-patch-preview.v1",
    generatedAt: new Date().toISOString(),
    command: "preview-options-patch",
    mutation: false,
    input,
    source: prepared.source,
    preview: {
      success: true,
      message: "TypeScript global-options patch preview completed against an artifact-owned candidate copy.",
      wouldChange: comparison.differingBytes > 0,
      candidateSha256,
      differingBytes: comparison.differingBytes,
      topRegion,
      candidateArtifactPath: artifactRoot ? candidatePath : undefined
    },
    beforeAfter: {
      before: prepared.current,
      after
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
      schemaVersion: "options-patch-preview.v1",
      candidateArtifactPath: artifactRoot ? candidatePath : undefined,
      note: "Read-only TypeScript global-options patch preview. The source file was not modified; the candidate is an artifact copy."
    }
  };

  if (!artifactRoot) {
    return payload;
  }

  await fs.mkdir(path.dirname(candidatePath), { recursive: true });
  await fs.writeFile(candidatePath, candidate);
  const artifactPath = await writeOptionsPatchArtifact(artifactRoot, "options-patch-preview", runId, "preview.json", payload);
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

export async function applyOptionsPatchPath(
  rawInput: Partial<OptionsPatchRequestInput> & Pick<OptionsPatchRequestInput, "path">,
  artifactRoot: string,
  runId = buildStandaloneRunId("options-patch-apply")
): Promise<OptionsPatchApplyPayload> {
  const root = path.resolve(artifactRoot);
  const input = normalizeOptionsPatchInput(rawInput);
  assertArtifactContainedPath(input.path, root, "options patch apply target");

  const prepared = await prepareOptionsPatchSource(input);
  const candidate = Buffer.from(prepared.data);
  applyOptionsPatchBuffer(candidate, input, prepared.copyOptionsData);
  const changed = !candidate.equals(prepared.data);

  const backupDir = path.join(root, "artifacts", "options-patch-apply", runId, "backup");
  const backupPath = path.join(backupDir, `${path.basename(prepared.path)}.bak`);
  await fs.mkdir(backupDir, { recursive: true });
  await fs.writeFile(backupPath, prepared.data);

  if (changed) {
    await fs.writeFile(prepared.path, candidate);
  }

  const readback = await fs.readFile(prepared.path);
  const readbackVerified = readback.equals(candidate);
  if (!readbackVerified) {
    throw new Error("Options patch apply read-back verification failed.");
  }

  const after = snapshotFromInspection(inspectSaveBuffer(prepared.path, readback));
  const comparison = compareSaveBuffers(backupPath, prepared.path, prepared.data, readback);
  const payload: OptionsPatchApplyPayload = {
    schemaVersion: "options-patch-apply.v1",
    generatedAt: new Date().toISOString(),
    command: "apply-options-patch",
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
      before: prepared.current,
      after
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
      schemaVersion: "options-patch-apply.v1",
      backupPath,
      note: "Applied a TypeScript global-options patch only to an artifact-root copied target after writing a backup and verifying read-back bytes."
    }
  };

  const artifactPath = await writeOptionsPatchArtifact(root, "options-patch-apply", runId, "apply.json", payload);
  return {
    ...payload,
    artifact: {
      ...payload.artifact,
      artifactPath
    }
  };
}

export function applyOptionsPatchBuffer(
  data: Buffer,
  input: OptionsPatchRequestInput,
  copyOptionsData?: Buffer
): Buffer {
  assertValidOptionsBuffer(data, "options target");
  const layout = computeOptionsLayout(data);

  applyCareerSettingsOverrides(data, input);
  applyOptionsCopy(data, layout, input, copyOptionsData);
  applyOptionsTailOverrides(data, layout, input);
  applyOptionsEntryOverrides(data, layout, input);
  return data;
}

async function prepareOptionsPatchSource(input: OptionsPatchRequestInput) {
  const normalizedPath = path.resolve(input.path);
  if (!isOptionsTargetPath(normalizedPath)) {
    throw new Error("Options patch target must be a .bea file or defaultoptions.bea backup.");
  }

  const data = await fs.readFile(normalizedPath);
  assertValidOptionsBuffer(data, "options target");
  const layout = computeOptionsLayout(data);
  const before = inspectSaveBuffer(normalizedPath, data);
  if (!before.isOptionsFile) {
    throw new Error("Options patch target must inspect as a global options file.");
  }

  let copyOptionsData: Buffer | undefined;
  if (input.copyOptionsFromPath) {
    const copyPath = path.resolve(input.copyOptionsFromPath);
    if (!isSupportedSaveLikePath(copyPath)) {
      throw new Error("copyOptionsFromPath must be a .bes career save, .bea options file, or defaultoptions.bea backup.");
    }
    copyOptionsData = await fs.readFile(copyPath);
    assertValidOptionsBuffer(copyOptionsData, "options copy source");
    const copyLayout = computeOptionsLayout(copyOptionsData);
    if (
      copyLayout.entryCount !== layout.entryCount ||
      copyLayout.tailStart !== layout.tailStart ||
      copyLayout.entriesSize !== layout.entriesSize ||
      copyLayout.tailSize !== layout.tailSize
    ) {
      throw new Error("Options copy requires matching options layouts.");
    }
  }

  return {
    path: normalizedPath,
    data,
    layout,
    before,
    current: snapshotFromInspection(before),
    source: {
      path: normalizedPath,
      fileName: path.basename(normalizedPath),
      fileSize: data.length,
      sha256: sha256Buffer(data),
      isValid: before.isValid,
      isOptionsFile: before.isOptionsFile,
      versionWordHex: before.versionWordHex,
      versionValid: before.versionValid,
      optionsEntryCount: before.options.entryCount,
      optionsTailStartHex: before.options.tailStartHex
    },
    copyOptionsData
  };
}

function applyCareerSettingsOverrides(data: Buffer, input: OptionsPatchRequestInput) {
  writeOptionalFloat32(data, soundVolumeOffset, input.soundVolume);
  writeOptionalFloat32(data, musicVolumeOffset, input.musicVolume);
  writeOptionalBool32(data, walkerInvertYP1Offset, input.invertWalkerP1);
  writeOptionalBool32(data, walkerInvertYP2Offset, input.invertWalkerP2);
  writeOptionalBool32(data, flightInvertYP1Offset, input.invertFlightP1);
  writeOptionalBool32(data, flightInvertYP2Offset, input.invertFlightP2);
  writeOptionalBool32(data, vibrationP1Offset, input.vibrationP1);
  writeOptionalBool32(data, vibrationP2Offset, input.vibrationP2);
  writeOptionalUInt32(data, controllerConfigP1Offset, input.controllerConfigP1);
  writeOptionalUInt32(data, controllerConfigP2Offset, input.controllerConfigP2);
}

function applyOptionsCopy(
  data: Buffer,
  layout: OptionsLayout,
  input: OptionsPatchRequestInput,
  copyOptionsData?: Buffer
) {
  if (!input.copyOptionsFromPath || (!input.copyOptionsEntries && !input.copyOptionsTail)) {
    return;
  }
  if (!copyOptionsData) {
    throw new Error("Options copy data was not prepared.");
  }
  assertValidOptionsBuffer(copyOptionsData, "options copy source");
  const copyLayout = computeOptionsLayout(copyOptionsData);
  if (
    copyLayout.entryCount !== layout.entryCount ||
    copyLayout.tailStart !== layout.tailStart ||
    copyLayout.entriesSize !== layout.entriesSize ||
    copyLayout.tailSize !== layout.tailSize
  ) {
    throw new Error("Options copy requires matching options layouts.");
  }

  if (input.copyOptionsEntries) {
    copyOptionsData.copy(data, optionsStart, optionsStart, optionsStart + layout.entriesSize);
  }
  if (input.copyOptionsTail) {
    copyOptionsData.copy(data, layout.tailStart, layout.tailStart, layout.tailStart + layout.tailSize);
  }
}

function applyOptionsTailOverrides(data: Buffer, layout: OptionsLayout, input: OptionsPatchRequestInput) {
  writeOptionalFloat32(data, layout.tailStart + 0x04, input.mouseSensitivity);
  writeOptionalUInt16(data, layout.tailStart + 0x08, input.controlSchemeIndex);
  writeOptionalUInt16(data, layout.tailStart + 0x0a, input.languageIndex);
  writeOptionalUInt32(data, layout.tailStart + 0x20, input.screenShape);
  writeOptionalUInt32(data, layout.tailStart + 0x28, input.d3dDeviceIndex);
}

function applyOptionsEntryOverrides(data: Buffer, layout: OptionsLayout, input: OptionsPatchRequestInput) {
  if (input.keybindOverrides.length === 0) {
    return;
  }

  const schemeIndex = data.readUInt16LE(layout.tailStart + 0x08);
  if (schemeIndex !== 0 && schemeIndex !== 1) {
    throw new Error(`Options entry overrides only support ControlSchemeIndex 0 or 1. Found: ${schemeIndex}.`);
  }

  const entryOffsets = new Map<number, number>();
  for (let index = 0; index < layout.entryCount; index++) {
    const offset = optionsStart + optionsEntrySize * index;
    entryOffsets.set(data.readInt32LE(offset + 0x04), offset);
  }

  const overrides = buildOptionsEntryOverrides(input.keybindOverrides);
  for (const override of overrides) {
    applyToOneEntry(data, entryOffsets, override);
  }
  data.writeUInt16LE(0, layout.tailStart + 0x08);
}

function buildOptionsEntryOverrides(rows: OptionsPatchKeybindOverride[]): NormalizedOptionsEntryOverride[] {
  const overrides = new Map<number, NormalizedOptionsEntryOverride>();
  const setSlot = (definitionRow: KeybindDefinition, entryId: number, slotIndex: 0 | 1, token: string | null) => {
    if (token === null || isKeepToken(token)) {
      return;
    }
    const slot = parseToken(entryId, definitionRow.keyboardDeviceCode, definitionRow, token);
    const actionName = `${definitionRow.groupLabel}: ${definitionRow.actionLabel}`;
    const entry = overrides.get(entryId) ?? { entryId, actionName };
    if (slotIndex === 0) {
      entry.slot0 = slot;
    } else {
      entry.slot1 = slot;
    }
    overrides.set(entryId, entry);
  };

  for (const row of rows) {
    const definitionRow = resolveKeybindDefinition(row);
    const slot0 = normalizeOptionalSlotToken(row.slot0 ?? null);
    const slot1 = normalizeOptionalSlotToken(row.slot1 ?? null);
    setSlot(definitionRow, definitionRow.entryId, 0, slot0);
    setSlot(definitionRow, definitionRow.entryId, 1, slot1);

    if (definitionRow.mirrorEntryId !== undefined) {
      const mirrorDefinition: KeybindDefinition = {
        ...definitionRow,
        entryId: definitionRow.mirrorEntryId,
        keyboardDeviceCode: definitionRow.mirrorKeyboardDeviceCode ?? definitionRow.keyboardDeviceCode
      };
      setSlot(mirrorDefinition, mirrorDefinition.entryId, 0, slot0);
      setSlot(mirrorDefinition, mirrorDefinition.entryId, 1, slot1);
    }
  }

  const has12 = overrides.has(0x12);
  const has13 = overrides.has(0x13);
  if (has12 && !has13) {
    const row = overrides.get(0x12)!;
    overrides.set(0x13, { ...row, entryId: 0x13, actionName: "Actions: Fire weapon (B)" });
  } else if (has13 && !has12) {
    const row = overrides.get(0x13)!;
    overrides.set(0x12, { ...row, entryId: 0x12, actionName: "Actions: Fire weapon" });
  }

  return [...overrides.values()].sort((left, right) => left.entryId - right.entryId);
}

function applyToOneEntry(
  data: Buffer,
  entryOffsets: Map<number, number>,
  override: NormalizedOptionsEntryOverride
) {
  const offset = entryOffsets.get(override.entryId);
  if (offset === undefined) {
    throw new Error(`Options entry_id 0x${override.entryId.toString(16).toUpperCase()} not found in file.`);
  }

  const flags = data.readUInt32LE(offset) >>> 0;
  data.writeUInt32LE(((flags & 0xffffff00) | 1) >>> 0, offset);
  if (override.slot0) {
    data.writeUInt32LE(override.slot0.deviceCode >>> 0, offset + 0x0c);
    data.writeUInt32LE(override.slot0.packedKey >>> 0, offset + 0x10);
  }
  if (override.slot1) {
    data.writeUInt32LE(override.slot1.deviceCode >>> 0, offset + 0x18);
    data.writeUInt32LE(override.slot1.packedKey >>> 0, offset + 0x1c);
  }
}

function parseToken(
  entryId: number,
  keyboardDeviceCode: number,
  definitionRow: KeybindDefinition,
  token: string
): BindingSlotPatch {
  const trimmed = token.trim();
  if (definitionRow.allowLookMouse && trimmed.toLowerCase().startsWith("mouse")) {
    return parseLookToken(entryId, trimmed);
  }
  if (
    definitionRow.allowZoomWheel &&
    (trimmed.toLowerCase() === "mousewheelup" || trimmed.toLowerCase() === "mousewheeldown")
  ) {
    return trimmed.toLowerCase() === "mousewheelup"
      ? { deviceCode: 16, packedKey: 3 }
      : { deviceCode: 16, packedKey: 4 };
  }
  if (
    definitionRow.allowMouseButtons &&
    (trimmed.toLowerCase() === "mouseleft" || trimmed.toLowerCase() === "mouseright")
  ) {
    return parseMouseButton(entryId, trimmed);
  }

  return {
    deviceCode: keyboardDeviceCode,
    packedKey: parseKeyboardPackedKey(trimmed)
  };
}

function parseLookToken(entryId: number, token: string): BindingSlotPatch {
  const defaultLookBinding = (currentEntryId: number): BindingSlotPatch => {
    if (currentEntryId === 0x1b) return { deviceCode: 11, packedKey: 0 };
    if (currentEntryId === 0x19) return { deviceCode: 12, packedKey: 0 };
    if (currentEntryId === 0x1a) return { deviceCode: 11, packedKey: 1 };
    if (currentEntryId === 0x1c) return { deviceCode: 12, packedKey: 1 };
    throw new Error(`Internal error: entry_id 0x${currentEntryId.toString(16).toUpperCase()} is not a Look entry.`);
  };

  const normalized = token.trim().toLowerCase();
  if (normalized === "mouse" || normalized === "mousex" || normalized === "mousey") {
    return defaultLookBinding(entryId);
  }
  if (normalized.startsWith("mousex")) {
    if (normalized.endsWith("-")) return { deviceCode: 12, packedKey: 0 };
    if (normalized.endsWith("+")) return { deviceCode: 11, packedKey: 0 };
    return defaultLookBinding(entryId);
  }
  if (normalized.startsWith("mousey")) {
    if (normalized.endsWith("-")) return { deviceCode: 12, packedKey: 1 };
    if (normalized.endsWith("+")) return { deviceCode: 11, packedKey: 1 };
    return defaultLookBinding(entryId);
  }
  if (normalized.startsWith("mouse(") && normalized.endsWith(")")) {
    const scan = Number.parseInt(normalized.slice("mouse(".length, -1), 10);
    if (Number.isSafeInteger(scan)) {
      return {
        deviceCode: defaultLookBinding(entryId).deviceCode,
        packedKey: scan >>> 0
      };
    }
  }
  throw new Error(`Invalid look binding '${token}'. Use Mouse, MouseX+/MouseX-, MouseY+/MouseY-, or a keyboard key.`);
}

function parseMouseButton(entryId: number, token: string): BindingSlotPatch {
  if (token.toLowerCase() === "mouseleft") {
    if (entryId === 0x12) return { deviceCode: 17, packedKey: 0 };
    if (entryId === 0x13) return { deviceCode: 15, packedKey: 0 };
    throw new Error("MouseLeft is only supported for Fire weapon.");
  }
  if (token.toLowerCase() === "mouseright") {
    if (entryId === 0x14) return { deviceCode: 16, packedKey: 2 };
    throw new Error("MouseRight is only supported for Select weapon.");
  }
  throw new Error(`Invalid mouse button binding '${token}'. Use MouseLeft/MouseRight.`);
}

function parseKeyboardPackedKey(input: string): number {
  let token = input.trim();
  if (token === "" || token.toLowerCase() === "keep" || token.toLowerCase() === "preserve" || token.toLowerCase() === "unchanged") {
    throw new Error("Keyboard binding token is empty or preserve-only.");
  }
  if (token === "-" || token.toLowerCase() === "none") {
    return 0;
  }
  if (token.toLowerCase().startsWith("key ")) {
    token = token.slice(4).trim();
  }

  const fallback = token.match(/^vk=0x([0-9a-f]+)\s+scan=0x([0-9a-f]+)$/i);
  if (fallback) {
    const vk = Number.parseInt(fallback[1], 16);
    const scan = Number.parseInt(fallback[2], 16);
    return (((vk & 0xffff) << 16) | (scan & 0xffff)) >>> 0;
  }

  const numToken = token.replace(/\s+/g, "");
  if (numToken.toLowerCase().startsWith("num")) {
    const rest = numToken.slice(3).replace(/^pad/i, "");
    const scan = numpadDigitScan.get(rest);
    if (rest.length === 1 && scan !== undefined) {
      return ((rest.charCodeAt(0) << 16) | scan) >>> 0;
    }
  }

  const named = keyNameMap.get(token.toUpperCase());
  if (named) {
    return (((named.vk & 0xffff) << 16) | (named.scan & 0xffff)) >>> 0;
  }

  if (token.length === 1) {
    const upper = token.toUpperCase();
    const letter = letterScan.get(upper);
    if (letter !== undefined) return ((upper.charCodeAt(0) << 16) | letter) >>> 0;
    const digit = digitScan.get(upper);
    if (digit !== undefined) return ((upper.charCodeAt(0) << 16) | digit) >>> 0;
    const punctuation = punctuationScan(upper);
    if (punctuation !== null) return ((upper.charCodeAt(0) << 16) | punctuation) >>> 0;
  }

  throw new Error(`Unrecognized key '${input}'. Examples: A, Num7, Up, Tab, Space, CapsLock, RShift, RControl, '-', '='.`);
}

function punctuationScan(char: string) {
  if (char === ";") return 0x0027;
  if (char === "'") return 0x0028;
  if (char === ",") return 0x0033;
  if (char === ".") return 0x0034;
  if (char === "/") return 0x0035;
  if (char === "\\") return 0x002b;
  if (char === "`") return 0x0029;
  return null;
}

function resolveKeybindDefinition(row: OptionsPatchKeybindOverride): KeybindDefinition {
  if (typeof row.entryId === "number") {
    const byEntry = definitionsByEntryId.get(row.entryId);
    if (!byEntry) {
      throw new Error(`Unsupported keybind entryId: 0x${row.entryId.toString(16).toUpperCase()}.`);
    }
    return byEntry;
  }
  if (typeof row.action === "string" && row.action.trim().length > 0) {
    const byAction = definitionsByAction.get(normalizeActionKey(row.action));
    if (!byAction) {
      throw new Error(`Unsupported keybind action: ${row.action}.`);
    }
    return byAction;
  }
  throw new Error("Keybind override requires action or entryId.");
}

function normalizeKeybindRequestRows(rows: OptionsPatchKeybindOverride[]) {
  return rows.flatMap((row) => {
    const definitionRow = resolveKeybindDefinition(row);
    const slot0 = normalizeOptionalSlotToken(row.slot0 ?? null);
    const slot1 = normalizeOptionalSlotToken(row.slot1 ?? null);
    if ((slot0 === null || isKeepToken(slot0)) && (slot1 === null || isKeepToken(slot1))) {
      return [];
    }
    return [
      {
        action: definitionRow.slug,
        entryId: definitionRow.entryId,
        slot0,
        slot1
      }
    ];
  });
}

function snapshotFromInspection(summary: ReturnType<typeof inspectSaveBuffer>): OptionsPatchSnapshot {
  return {
    settings: summary.settings,
    options: {
      entryCount: summary.options.entryCount,
      tailStartHex: summary.options.tailStartHex,
      mouseSensitivity: summary.options.mouseSensitivity,
      mouseSensitivityBitsHex: summary.options.mouseSensitivityBitsHex,
      controlSchemeIndex: summary.options.controlSchemeIndex,
      languageIndex: summary.options.languageIndex,
      screenShape: summary.options.screenShape,
      d3dDeviceIndex: summary.options.d3dDeviceIndex,
      bindingSlotLabels: summary.options.bindingSlotLabels,
      bindingCount: summary.options.bindings.length
    }
  };
}

function computeOptionsLayout(data: Buffer): OptionsLayout {
  if (data.length < optionsBaseSize || (data.length - optionsBaseSize) % optionsEntrySize !== 0) {
    throw new Error("Invalid options layout: file size does not fit the entries + tail formula.");
  }
  const entryCount = (data.length - optionsBaseSize) / optionsEntrySize;
  const tailStart = optionsStart + entryCount * optionsEntrySize;
  if (tailStart !== data.length - optionsTailSize) {
    throw new Error("Invalid options layout: tail start does not match file size.");
  }
  return {
    entryCount,
    tailStart,
    entriesSize: entryCount * optionsEntrySize,
    tailSize: optionsTailSize
  };
}

function assertValidOptionsBuffer(data: Buffer, label: string) {
  if (data.length !== expectedFileSize) {
    throw new Error(`Invalid ${label} size: expected ${expectedFileSize} bytes, got ${data.length}.`);
  }
  if (data.readUInt16LE(0) !== versionWord) {
    throw new Error(`Invalid ${label} version word: ${toHex16(data.readUInt16LE(0))}; expected ${toHex16(versionWord)}.`);
  }
}

function plannedOptionsSections(input: OptionsPatchRequestInput) {
  return [
    countSettingsOverrides(input) > 0 ? "career-settings" : null,
    input.copyOptionsFromPath ? "options-copy" : null,
    countTailOverrides(input) > 0 ? "options-tail" : null,
    input.keybindOverrides.length > 0 ? "keybinds" : null
  ].filter((section): section is string => Boolean(section));
}

function countSettingsOverrides(input: OptionsPatchRequestInput) {
  return [
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
  ].filter((value) => value !== null).length;
}

function countTailOverrides(input: OptionsPatchRequestInput) {
  return [
    input.mouseSensitivity,
    input.controlSchemeIndex,
    input.languageIndex,
    input.screenShape,
    input.d3dDeviceIndex
  ].filter((value) => value !== null).length;
}

function definition(
  slug: string,
  aliases: string[],
  groupLabel: string,
  actionLabel: string,
  entryId: number,
  keyboardDeviceCode: number,
  options: Partial<Pick<KeybindDefinition, "allowLookMouse" | "allowZoomWheel" | "allowMouseButtons" | "mirrorEntryId" | "mirrorKeyboardDeviceCode">> = {}
): KeybindDefinition {
  return {
    slug,
    aliases,
    groupLabel,
    actionLabel,
    entryId,
    keyboardDeviceCode,
    allowLookMouse: options.allowLookMouse ?? false,
    allowZoomWheel: options.allowZoomWheel ?? false,
    allowMouseButtons: options.allowMouseButtons ?? false,
    mirrorEntryId: options.mirrorEntryId,
    mirrorKeyboardDeviceCode: options.mirrorKeyboardDeviceCode
  };
}

function isSupportedSaveLikePath(filePath: string) {
  const fileName = path.basename(filePath).toLowerCase();
  const extension = path.extname(fileName);
  return extension === ".bes" || extension === ".bea" || fileName.startsWith("defaultoptions.bea");
}

function isOptionsTargetPath(filePath: string) {
  const fileName = path.basename(filePath).toLowerCase();
  return path.extname(fileName) === ".bea" || fileName.startsWith("defaultoptions.bea");
}

function optionsExtension(filePath: string) {
  return path.extname(filePath) || ".bea";
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

function writeOptionalFloat32(data: Buffer, offset: number, value: number | null) {
  if (value !== null) {
    data.writeFloatLE(value, offset);
  }
}

function writeOptionalBool32(data: Buffer, offset: number, value: boolean | null) {
  if (value !== null) {
    data.writeUInt32LE(value ? 1 : 0, offset);
  }
}

function writeOptionalUInt32(data: Buffer, offset: number, value: number | null) {
  if (value !== null) {
    data.writeUInt32LE(value >>> 0, offset);
  }
}

function writeOptionalUInt16(data: Buffer, offset: number, value: number | null) {
  if (value !== null) {
    data.writeUInt16LE(value, offset);
  }
}

function normalizeOptionalUnitFloat(value: unknown, label: string) {
  const numberValue = normalizeOptionalFiniteFloat(value, label, 0, 1);
  if (numberValue === null) {
    return null;
  }
  return Math.max(0, Math.min(1, numberValue));
}

function normalizeOptionalFiniteFloat(value: unknown, label: string, min: number, max: number) {
  if (value === null || typeof value === "undefined" || value === "") {
    return null;
  }
  const parsed = typeof value === "number" ? value : Number.parseFloat(String(value));
  if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
    throw new Error(`Options patch ${label} must be a finite number from ${min} to ${max}.`);
  }
  return parsed;
}

function normalizeOptionalUInt16(value: unknown, label: string) {
  const parsed = normalizeOptionalInteger(value, label);
  if (parsed === null) {
    return null;
  }
  if (parsed < 0 || parsed > 0xffff) {
    throw new Error(`Options patch ${label} must be an integer from 0 to 65535.`);
  }
  return parsed;
}

function normalizeOptionalUInt32(value: unknown, label: string) {
  const parsed = normalizeOptionalInteger(value, label);
  if (parsed === null) {
    return null;
  }
  if (parsed < 0 || parsed > 0xffffffff) {
    throw new Error(`Options patch ${label} must be an integer from 0 to 4294967295.`);
  }
  return parsed;
}

function normalizeOptionalInteger(value: unknown, label: string) {
  if (value === null || typeof value === "undefined" || value === "") {
    return null;
  }
  const parsed =
    typeof value === "number"
      ? value
      : String(value).trim().toLowerCase().startsWith("0x")
        ? Number.parseInt(String(value).trim().slice(2), 16)
        : Number.parseInt(String(value).trim(), 10);
  if (!Number.isSafeInteger(parsed)) {
    throw new Error(`Options patch ${label} must be an integer.`);
  }
  return parsed;
}

function normalizeOptionalBoolean(value: unknown, label: string) {
  if (value === null || typeof value === "undefined" || value === "") {
    return null;
  }
  if (typeof value === "boolean") {
    return value;
  }
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase();
    if (["true", "yes", "1", "on"].includes(normalized)) return true;
    if (["false", "no", "0", "off"].includes(normalized)) return false;
  }
  throw new Error(`Options patch ${label} must be a boolean.`);
}

function normalizeOptionalSlotToken(value: unknown) {
  if (value === null || typeof value === "undefined") {
    return null;
  }
  if (typeof value !== "string") {
    throw new Error("Keybind slot values must be strings.");
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

function isKeepToken(token: string) {
  const normalized = token.trim().toLowerCase();
  return normalized === "keep" || normalized === "preserve" || normalized === "unchanged";
}

function optionalStringValue(value: unknown) {
  if (value === null || typeof value === "undefined") {
    return null;
  }
  if (typeof value !== "string") {
    throw new Error("Options patch copyOptionsFromPath must be a string.");
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

function stringValue(value: string, label: string) {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`Options patch ${label} is required.`);
  }
  return value.trim();
}

function normalizeActionKey(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function withExclusiveEnd(range: SaveComparisonRange) {
  const start = parseHexOffset(range.startOffsetHex);
  return {
    ...range,
    endOffsetExclusiveHex: toHexOffset(start + range.byteLength)
  };
}

async function writeOptionsPatchArtifact(
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
