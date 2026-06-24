import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import type {
  SaveBindingSummaryRow,
  SaveComparisonRange,
  SaveComparisonRegionCount,
  SaveComparisonSummary,
  SaveCompletedNodeSample,
  SaveGoodieSummaryRow,
  SaveInspectionSummary,
  SaveKillSummaryRow,
  SaveRankSummaryRow
} from "@onslaught/contracts";

const expectedFileSize = 10004;
const versionWord = 0x4bd1;
const careerBase = 0x0002;
const nodeBase = careerBase + 0x0004;
const linkBase = careerBase + 0x1904;
const goodieBase = careerBase + 0x1f44;
const killsBase = careerBase + 0x23f4;
const techSlotsBase = careerBase + 0x2408;
const careerInProgress = careerBase + 0x2488;
const soundVolume = careerBase + 0x248c;
const musicVolume = careerBase + 0x2490;
const godModeEnabled = careerBase + 0x2494;
const flightInvertYP1 = careerBase + 0x249c;
const flightInvertYP2 = careerBase + 0x24a0;
const walkerInvertYP1 = careerBase + 0x24a4;
const walkerInvertYP2 = careerBase + 0x24a8;
const vibrationP1 = careerBase + 0x24ac;
const vibrationP2 = careerBase + 0x24b0;
const controllerConfigP1 = careerBase + 0x24b4;
const controllerConfigP2 = careerBase + 0x24b8;
const newGoodieCount = careerBase;

const nodeSize = 64;
const nodeCount = 100;
const linkSize = 8;
const linkCount = 200;
const goodieCount = 300;
const goodieDisplayableCount = 233;
const techSlotCount = 32;

const rankFloatBits = new Map<number, string>([
  [0x3f800000, "S"],
  [0x3f4ccccd, "A"],
  [0x3f19999a, "B"],
  [0x3eb33333, "C"],
  [0x3e19999a, "D"],
  [0x00000000, "E"],
  [0xbf800000, "NONE"]
]);

const killCategories = ["Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs"];
const killThresholds = [
  [25, 50, 75, 100],
  [100, 200, 300, 400],
  [25, 50],
  [40, 80, 160],
  [20, 40, 80]
];

const explicitGoodieTitles = new Map<number, { title: string; unlockHint: string }>([
  [0, { title: "Hawk bio", unlockHint: "Complete level 100" }],
  [1, { title: "Tatianna bio", unlockHint: "Level 110 at C rank or better" }],
  [2, { title: "Kramer bio", unlockHint: "Goodie 1 plus level 200 at C rank or better" }],
  [3, { title: "Lorenzo bio", unlockHint: "Goodie 2 plus level 231/232 at C rank or better" }],
  [4, { title: "Tara bio", unlockHint: "Goodie 3 plus level 321/322 at C rank or better" }],
  [5, { title: "Billy bio", unlockHint: "Goodie 4 plus level 321/322 at C rank or better" }],
  [6, { title: "Carver bio", unlockHint: "Goodie 5 plus level 621/622 at C rank or better" }],
  [7, { title: "Surt bio", unlockHint: "Goodie 6 plus level 741/742 at C rank or better" }],
  [8, { title: "Battle Engine v1", unlockHint: "Complete level 100" }],
  [9, { title: "Battle Engine v2", unlockHint: "Complete level 211/212" }],
  [10, { title: "Battle Engine v3", unlockHint: "Complete level 400" }],
  [11, { title: "Battle Engine v4", unlockHint: "Complete level 710" }],
  [33, { title: "Muspell Grunt", unlockHint: "40 infantry kills" }],
  [34, { title: "Firebreather", unlockHint: "160 infantry kills" }],
  [35, { title: "Commando", unlockHint: "80 infantry kills" }],
  [36, { title: "ATF", unlockHint: "25 aircraft kills" }],
  [37, { title: "Bomber", unlockHint: "100 aircraft kills" }],
  [38, { title: "Ground Attack", unlockHint: "50 aircraft kills" }],
  [39, { title: "Dropship", unlockHint: "75 aircraft kills" }],
  [40, { title: "Dropship v2", unlockHint: "25 aircraft kills and 80 infantry kills" }],
  [41, { title: "M Light Tank", unlockHint: "50 aircraft kills and 100 infantry kills" }],
  [42, { title: "M Tank", unlockHint: "100 vehicle kills" }],
  [43, { title: "SAM Launcher", unlockHint: "400 vehicle kills" }],
  [44, { title: "Artillery", unlockHint: "300 vehicle kills" }],
  [45, { title: "M Truck", unlockHint: "200 vehicle kills" }],
  [46, { title: "Level 500 goodie", unlockHint: "Complete level 500" }],
  [47, { title: "Gunwalker", unlockHint: "20 mech kills" }],
  [48, { title: "Gunwalker 2", unlockHint: "40 mech kills" }],
  [49, { title: "Guncrab", unlockHint: "80 mech kills" }],
  [50, { title: "Gnat mech", unlockHint: "Scripted mission unlock" }],
  [51, { title: "Arachnid", unlockHint: "40 mech kills" }],
  [52, { title: "M Battleship v2", unlockHint: "Scripted mission unlock" }],
  [53, { title: "SAM Turret (M)", unlockHint: "50 emplacement kills and 25 aircraft kills" }],
  [54, { title: "Laser Turret", unlockHint: "50 emplacement kills" }],
  [55, { title: "MG Turret", unlockHint: "25 emplacement kills" }],
  [56, { title: "Artillery Turret", unlockHint: "75 emplacement kills and 100 vehicle kills" }],
  [57, { title: "Flak Turret", unlockHint: "25 emplacement kills and 25 aircraft kills" }],
  [58, { title: "Thunderhead", unlockHint: "Level 331/332 at A rank or better" }],
  [59, { title: "Warspite", unlockHint: "Level 431/432 at A rank or better" }],
  [60, { title: "Submarine", unlockHint: "Complete level 523/524" }],
  [61, { title: "Hive", unlockHint: "Level 521/522 at A rank or better" }],
  [62, { title: "Gill-M", unlockHint: "Level 523/524 at A rank or better" }],
  [63, { title: "Carver's Plane", unlockHint: "100 aircraft kills plus level 621/622 at C rank or better" }],
  [64, { title: "Fenrir", unlockHint: "Level 731/732 at A rank or better" }],
  [65, { title: "Sentinel", unlockHint: "Level 800 at A rank or better" }],
  [66, { title: "Race level 901", unlockHint: "26 missions at A rank or better" }],
  [67, { title: "Race level 902", unlockHint: "Scripted race progression unlock" }],
  [68, { title: "Race level 903", unlockHint: "Scripted race progression unlock" }],
  [69, { title: "Race level 904", unlockHint: "Scripted race progression unlock" }],
  [70, { title: "Race level 905", unlockHint: "Scripted race progression unlock" }],
  [74, { title: "Ashley dev photo", unlockHint: "20 S ranks" }],
  [75, { title: "Foresti High FMV", unlockHint: "40 S ranks" }],
  [76, { title: "Team photo", unlockHint: "43 S ranks" }],
  [77, { title: "Dev video: UsTheMovie", unlockHint: "43 S ranks" }],
  [78, { title: "Unknown S-rank unlock", unlockHint: "43 S ranks" }]
]);

const bindingRows = [
  [0x1f, "Movement: Forward"],
  [0x20, "Movement: Backward"],
  [0x1d, "Movement: Left"],
  [0x1e, "Movement: Right"],
  [0x1a, "Look: Up"],
  [0x1c, "Look: Down"],
  [0x19, "Look: Left"],
  [0x1b, "Look: Right"],
  [0x10, "Zoom: In"],
  [0x11, "Zoom: Out"],
  [0x12, "Others: Fire weapon (A)"],
  [0x13, "Others: Fire weapon (B)"],
  [0x14, "Others: Select weapon"],
  [0x21, "Others: Transform"],
  [0x15, "Others: Air brake"],
  [0x3b, "Others: Special function"]
] as const;

const keyNameMap = new Map<string, { vk: number; scan: number }>([
  ["Up", { vk: 0, scan: 0x00c8 }],
  ["Down", { vk: 0, scan: 0x00d0 }],
  ["Left", { vk: 0, scan: 0x00cb }],
  ["Right", { vk: 0, scan: 0x00cd }],
  ["Tab", { vk: 0, scan: 0x000f }],
  ["Space", { vk: " ".charCodeAt(0), scan: 0x0039 }],
  ["CapsLock", { vk: 0, scan: 0x003a }],
  ["LShift", { vk: 0, scan: 0x002a }],
  ["RShift", { vk: 0, scan: 0x0036 }],
  ["RControl", { vk: 0, scan: 0x009d }],
  ["-", { vk: "-".charCodeAt(0), scan: 0x000c }],
  ["=", { vk: "=".charCodeAt(0), scan: 0x000d }],
  ["+", { vk: "+".charCodeAt(0), scan: 0x000d }]
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

export async function inspectSaveFilePath(
  savePath: string,
  artifactRoot?: string
): Promise<SaveInspectionSummary> {
  const normalizedPath = path.resolve(savePath);
  const stat = await fs.stat(normalizedPath);
  if (!stat.isFile()) {
    throw new Error("Selected path is not a file.");
  }

  if (!isSupportedSaveLikePath(normalizedPath)) {
    throw new Error("Select a .bes career save, .bea options file, or defaultoptions.bea backup.");
  }

  const data = await fs.readFile(normalizedPath);
  const inspectedAt = new Date().toISOString();
  const sha256 = createHash("sha256").update(data).digest("hex");
  const summary = inspectBuffer(normalizedPath, data, sha256, inspectedAt);

  if (!artifactRoot) {
    return summary;
  }

  return writeInspectionArtifact(summary, artifactRoot);
}

export async function compareSaveFilePaths(
  leftPath: string,
  rightPath: string,
  artifactRoot?: string
): Promise<SaveComparisonSummary> {
  const normalizedLeft = path.resolve(leftPath);
  const normalizedRight = path.resolve(rightPath);
  if (!isSupportedSaveLikePath(normalizedLeft) || !isSupportedSaveLikePath(normalizedRight)) {
    throw new Error("Compare requires .bes/.bea/defaultoptions-like files.");
  }

  const [leftStat, rightStat] = await Promise.all([fs.stat(normalizedLeft), fs.stat(normalizedRight)]);
  if (!leftStat.isFile() || !rightStat.isFile()) {
    throw new Error("Both compare inputs must be files.");
  }

  const [left, right] = await Promise.all([fs.readFile(normalizedLeft), fs.readFile(normalizedRight)]);
  const comparedAt = new Date().toISOString();
  const leftSha256 = createHash("sha256").update(left).digest("hex");
  const rightSha256 = createHash("sha256").update(right).digest("hex");
  const summary = compareBuffers(normalizedLeft, normalizedRight, left, right, leftSha256, rightSha256, comparedAt);

  if (!artifactRoot) {
    return summary;
  }

  return writeComparisonArtifact(summary, artifactRoot);
}

export function inspectSaveBuffer(
  selectedPath: string,
  data: Buffer,
  inspectedAt = new Date().toISOString()
): SaveInspectionSummary {
  const normalizedPath = path.resolve(selectedPath);
  const sha256 = createHash("sha256").update(data).digest("hex");
  return inspectBuffer(normalizedPath, data, sha256, inspectedAt);
}

export function compareSaveBuffers(
  leftPath: string,
  rightPath: string,
  left: Buffer,
  right: Buffer,
  comparedAt = new Date().toISOString()
): SaveComparisonSummary {
  const normalizedLeft = path.resolve(leftPath);
  const normalizedRight = path.resolve(rightPath);
  const leftSha256 = createHash("sha256").update(left).digest("hex");
  const rightSha256 = createHash("sha256").update(right).digest("hex");
  return compareBuffers(normalizedLeft, normalizedRight, left, right, leftSha256, rightSha256, comparedAt);
}

function inspectBuffer(selectedPath: string, data: Buffer, sha256: string, inspectedAt: string): SaveInspectionSummary {
  const fileName = path.basename(selectedPath);
  const isOptionsFile = isOptionsLikeFileName(fileName);
  const fileSize = data.length;
  const fileVersionWord = fileSize >= 2 ? data.readUInt16LE(0) : 0;
  const base = buildEmptySummary(selectedPath, fileName, fileSize, sha256, inspectedAt, isOptionsFile, fileVersionWord);

  if (fileSize !== expectedFileSize) {
    return {
      ...base,
      isValid: false,
      errorMessage: `Invalid file size: ${fileSize.toLocaleString()} bytes (expected ${expectedFileSize.toLocaleString()})`
    };
  }

  if (fileVersionWord !== versionWord) {
    return {
      ...base,
      isValid: false,
      errorMessage: `Invalid version word: ${toHex16(fileVersionWord)} (expected ${toHex16(versionWord)})`
    };
  }

  const completedNodeSamples: SaveCompletedNodeSample[] = [];
  const rankCounts = new Map<string, number>();
  let completedNodes = 0;
  let partialNodes = 0;
  let emptyNodes = 0;

  for (let index = 0; index < nodeCount; index++) {
    const offset = nodeBase + index * nodeSize;
    const world = readUInt32(data, offset + 0x10);
    if (world === 0) {
      emptyNodes++;
      continue;
    }

    const complete = readUInt32(data, offset + 0x04);
    if (complete === 0) {
      partialNodes++;
      continue;
    }

    completedNodes++;
    const rankBits = readUInt32(data, offset + 0x3c);
    const rank = decodeRank(rankBits);
    const baseRank = rank.replace(/^~/, "").split(" ")[0];
    rankCounts.set(baseRank, (rankCounts.get(baseRank) ?? 0) + 1);

    if (completedNodeSamples.length < 10) {
      completedNodeSamples.push({
        index,
        world,
        rank,
        rankBitsHex: toHex32(rankBits)
      });
    }
  }

  let totalLinks = 0;
  let completedLinks = 0;
  for (let index = 0; index < linkCount; index++) {
    const offset = linkBase + index * linkSize;
    const state = readUInt32(data, offset);
    const toNode = readUInt32(data, offset + 4);
    if (toNode === 0xffffffff) {
      continue;
    }

    totalLinks++;
    if (state !== 0) {
      completedLinks++;
    }
  }

  let goodiesNew = 0;
  let goodiesOld = 0;
  let goodiesLocked = 0;
  let goodiesInstructions = 0;
  let goodiesOther = 0;
  let goodiesReserved = 0;
  const goodieRows: SaveGoodieSummaryRow[] = [];
  for (let index = 0; index < goodieCount; index++) {
    if (index >= goodieDisplayableCount) {
      goodiesReserved++;
      continue;
    }

    const value = readUInt32(data, goodieBase + index * 4);
    if (value === 0) goodiesLocked++;
    else if (value === 1) goodiesInstructions++;
    else if (value === 2) goodiesNew++;
    else if (value === 3) goodiesOld++;
    else goodiesOther++;

    goodieRows.push(buildGoodieRow(index, value));
  }

  const kills: SaveKillSummaryRow[] = killCategories.map((categoryName, categoryIndex) => {
    const raw = readUInt32(data, killsBase + categoryIndex * 4);
    const kills = raw & 0x00ffffff;
    return {
      categoryIndex,
      categoryName,
      kills,
      meta: raw >>> 24,
      nextUnlockThreshold: nextUnlockThreshold(categoryIndex, kills)
    };
  });

  let activeTechSlots = 0;
  for (let index = 0; index < techSlotCount; index++) {
    if (readUInt32(data, techSlotsBase + index * 4) !== 0) {
      activeTechSlots++;
    }
  }

  return {
    ...base,
    isValid: true,
    counts: {
      completedNodes,
      partialNodes,
      emptyNodes,
      completedLinks,
      totalLinks,
      activeTechSlots,
      totalTechSlots: techSlotCount
    },
    goodies: {
      displayableUnlocked: goodiesNew + goodiesOld,
      new: goodiesNew,
      old: goodiesOld,
      locked: goodiesLocked,
      instructions: goodiesInstructions,
      other: goodiesOther,
      reserved: goodiesReserved
    },
    goodieRows,
    kills,
    rankDistribution: rankDistributionRows(rankCounts),
    completedNodeSamples,
    settings: {
      newGoodieCountRaw: readUInt32(data, newGoodieCount),
      careerInProgress: readUInt32(data, careerInProgress) !== 0,
      godModeEnabled: readUInt32(data, godModeEnabled) !== 0,
      soundVolume: readFloat32(data, soundVolume),
      soundVolumeBitsHex: toHex32(readUInt32(data, soundVolume)),
      musicVolume: readFloat32(data, musicVolume),
      musicVolumeBitsHex: toHex32(readUInt32(data, musicVolume)),
      walkerInvertY: [readUInt32(data, walkerInvertYP1) !== 0, readUInt32(data, walkerInvertYP2) !== 0],
      flightInvertY: [readUInt32(data, flightInvertYP1) !== 0, readUInt32(data, flightInvertYP2) !== 0],
      vibration: [readUInt32(data, vibrationP1) !== 0, readUInt32(data, vibrationP2) !== 0],
      controllerConfig: [readUInt32(data, controllerConfigP1), readUInt32(data, controllerConfigP2)]
    },
    options: inspectOptionsTail(data)
  };
}

function compareBuffers(
  leftPath: string,
  rightPath: string,
  left: Buffer,
  right: Buffer,
  leftSha256: string,
  rightSha256: string,
  comparedAt: string
): SaveComparisonSummary {
  const maxLength = Math.max(left.length, right.length);
  const regionCounts = new Map<string, number>();
  const diffRanges: SaveComparisonRange[] = [];
  let differingBytes = 0;
  let rangeStart: number | null = null;

  for (let offset = 0; offset < maxLength; offset++) {
    const leftByte = offset < left.length ? left[offset] : undefined;
    const rightByte = offset < right.length ? right[offset] : undefined;
    const differs = leftByte !== rightByte;

    if (differs) {
      differingBytes++;
      const region = regionName(offset);
      regionCounts.set(region, (regionCounts.get(region) ?? 0) + 1);
      if (rangeStart === null) {
        rangeStart = offset;
      }
    } else if (rangeStart !== null) {
      diffRanges.push(buildRange(rangeStart, offset - 1));
      rangeStart = null;
    }
  }

  if (rangeStart !== null) {
    diffRanges.push(buildRange(rangeStart, maxLength - 1));
  }

  const topRegions: SaveComparisonRegionCount[] = [...regionCounts.entries()]
    .sort((leftEntry, rightEntry) => rightEntry[1] - leftEntry[1] || leftEntry[0].localeCompare(rightEntry[0]))
    .slice(0, 12)
    .map(([region, count]) => ({ region, differingBytes: count }));

  return {
    leftPath,
    rightPath,
    leftFileName: path.basename(leftPath),
    rightFileName: path.basename(rightPath),
    leftFileSize: left.length,
    rightFileSize: right.length,
    leftSha256,
    rightSha256,
    comparedAt,
    sameSize: left.length === right.length,
    differingBytes,
    identical: differingBytes === 0,
    topRegions,
    diffRanges: diffRanges.slice(0, 32),
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "save-comparison.v1",
      note: "Read-only save/options comparison only. No bytes were changed."
    }
  };
}

function buildEmptySummary(
  selectedPath: string,
  fileName: string,
  fileSize: number,
  sha256: string,
  inspectedAt: string,
  isOptionsFile: boolean,
  fileVersionWord: number
): SaveInspectionSummary {
  return {
    selectedPath,
    fileName,
    fileSize,
    sha256,
    inspectedAt,
    isValid: false,
    isOptionsFile,
    versionWordHex: toHex16(fileVersionWord),
    versionValid: fileVersionWord === versionWord,
    counts: {
      completedNodes: 0,
      partialNodes: 0,
      emptyNodes: 0,
      completedLinks: 0,
      totalLinks: 0,
      activeTechSlots: 0,
      totalTechSlots: techSlotCount
    },
    goodies: {
      displayableUnlocked: 0,
      new: 0,
      old: 0,
      locked: 0,
      instructions: 0,
      other: 0,
      reserved: 0
    },
    goodieRows: [],
    kills: killCategories.map((categoryName, categoryIndex) => ({
      categoryIndex,
      categoryName,
      kills: 0,
      meta: 0,
      nextUnlockThreshold: killThresholds[categoryIndex][0] ?? null
    })),
    rankDistribution: [],
    completedNodeSamples: [],
    settings: {
      newGoodieCountRaw: 0,
      careerInProgress: false,
      godModeEnabled: false,
      soundVolume: 0,
      soundVolumeBitsHex: "0x00000000",
      musicVolume: 0,
      musicVolumeBitsHex: "0x00000000",
      walkerInvertY: [false, false],
      flightInvertY: [false, false],
      vibration: [false, false],
      controllerConfig: [0, 0]
    },
    options: {
      entryCount: null,
      tailStartHex: null,
      mouseSensitivity: null,
      mouseSensitivityBitsHex: null,
      controlSchemeIndex: null,
      languageIndex: null,
      screenShape: null,
      d3dDeviceIndex: null,
      bindingSlotLabels: ["Slot0", "Slot1"],
      bindings: []
    },
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "save-inspection.v1",
      note: "Read-only save/options inspection only. No bytes were changed."
    }
  };
}

function inspectOptionsTail(data: Buffer): SaveInspectionSummary["options"] {
  const optionsStart = 0x24be;
  const baseSize = 0x2514;
  const entrySize = 0x20;
  const tailSize = 0x56;

  if (data.length < baseSize || (data.length - baseSize) % entrySize !== 0) {
    return emptyOptions();
  }

  const entryCount = (data.length - baseSize) / entrySize;
  const tailStart = optionsStart + entrySize * entryCount;
  if (tailStart !== data.length - tailSize) {
    return emptyOptions();
  }

  const controlSchemeIndex = data.readUInt16LE(tailStart + 0x08);

  return {
    entryCount,
    tailStartHex: toHexOffset(tailStart),
    mouseSensitivity: readFloat32(data, tailStart + 0x04),
    mouseSensitivityBitsHex: toHex32(readUInt32(data, tailStart + 0x04)),
    controlSchemeIndex,
    languageIndex: data.readUInt16LE(tailStart + 0x0a),
    screenShape: readUInt32(data, tailStart + 0x20),
    d3dDeviceIndex: readUInt32(data, tailStart + 0x28),
    bindingSlotLabels: controlSchemeIndex === 0 || controlSchemeIndex === 1 ? ["P1", "P2"] : ["Slot0", "Slot1"],
    bindings: inspectBindings(data, entryCount)
  };
}

function emptyOptions(): SaveInspectionSummary["options"] {
  return {
    entryCount: null,
    tailStartHex: null,
    mouseSensitivity: null,
    mouseSensitivityBitsHex: null,
    controlSchemeIndex: null,
    languageIndex: null,
    screenShape: null,
    d3dDeviceIndex: null,
    bindingSlotLabels: ["Slot0", "Slot1"],
    bindings: []
  };
}

function inspectBindings(data: Buffer, entryCount: number): SaveBindingSummaryRow[] {
  const optionsStart = 0x24be;
  const entrySize = 0x20;
  const entries = new Map<number, { slot0Device: number; slot0Key: number; slot1Device: number; slot1Key: number }>();

  for (let index = 0; index < entryCount; index++) {
    const offset = optionsStart + entrySize * index;
    const active = readUInt32(data, offset) & 0xff;
    if (active === 0) {
      continue;
    }

    const entryId = data.readInt32LE(offset + 0x04);
    entries.set(entryId, {
      slot0Device: readUInt32(data, offset + 0x0c),
      slot0Key: readUInt32(data, offset + 0x10),
      slot1Device: readUInt32(data, offset + 0x18),
      slot1Key: readUInt32(data, offset + 0x1c)
    });
  }

  return bindingRows.flatMap(([entryId, actionName]) => {
    const entry = entries.get(entryId);
    if (!entry) {
      return [];
    }

    return [
      {
        entryId,
        entryIdHex: toHexOffset(entryId),
        actionName,
        slot0: formatBinding(entry.slot0Device, entry.slot0Key),
        slot1: formatBinding(entry.slot1Device, entry.slot1Key),
        slot0DeviceCode: entry.slot0Device,
        slot0PackedKeyHex: toHex32(entry.slot0Key),
        slot1DeviceCode: entry.slot1Device,
        slot1PackedKeyHex: toHex32(entry.slot1Key)
      }
    ];
  });
}

function isSupportedSaveLikePath(filePath: string) {
  const fileName = path.basename(filePath).toLowerCase();
  const extension = path.extname(fileName);
  return extension === ".bes" || extension === ".bea" || fileName.startsWith("defaultoptions.bea");
}

function isOptionsLikeFileName(fileName: string) {
  const lower = fileName.toLowerCase();
  return path.extname(lower) === ".bea" || lower.startsWith("defaultoptions.bea");
}

function readUInt32(data: Buffer, offset: number) {
  return data.readUInt32LE(offset);
}

function readFloat32(data: Buffer, offset: number) {
  return Number(data.readFloatLE(offset).toFixed(4));
}

function formatBinding(deviceCode: number, packedKey: number) {
  const vk = (packedKey >>> 16) & 0xffff;
  const scan = packedKey & 0xffff;

  if (deviceCode === 11 || deviceCode === 12) {
    const axis = scan === 0 ? "MouseX" : scan === 1 ? "MouseY" : "MouseAxis";
    const direction = deviceCode === 11 ? "+" : "-";
    return axis === "MouseAxis" ? `Mouse(${scan})` : `${axis}${direction}`;
  }

  if (deviceCode === 16) {
    if (scan === 4) return "MouseWheelDown";
    if (scan === 3) return "MouseWheelUp";
    if (scan === 2) return "MouseRight";
    return `Mouse(${scan})`;
  }

  if ((deviceCode === 17 || deviceCode === 15) && vk === 0 && scan === 0) {
    return "MouseLeft";
  }

  if (packedKey === 0) {
    return "-";
  }

  if (vk === 0 && scan === 0x00c8) return "Up";
  if (vk === 0 && scan === 0x00d0) return "Down";
  if (vk === 0 && scan === 0x00cb) return "Left";
  if (vk === 0 && scan === 0x00cd) return "Right";
  if (vk === 0 && scan === 0x0039) return "Space";
  if (vk === 0 && scan === 0x002a) return "LShift";
  if (vk === 0 && scan === 0x0036) return "RShift";
  if (vk === 0 && scan === 0x009d) return "RControl";
  if (vk === 0 && scan === 0x003a) return "CapsLock";
  if (vk === 0 && scan === 0x000f) return "Tab";
  if (vk === 0 && scan === 0x0027) return "Key ;";
  if (vk === 0 && scan === 0x000c) return "Key -";
  if (vk === 0 && scan === 0x000d) return "Key =";

  if (vk === 0) {
    for (const [digit, digitScan] of numpadDigitScan) {
      if (digitScan === scan) {
        return `Num ${digit}`;
      }
    }
  }

  if (vk >= "0".charCodeAt(0) && vk <= "9".charCodeAt(0)) {
    const digit = String.fromCharCode(vk);
    if (numpadDigitScan.get(digit) === scan) {
      return `Num ${digit}`;
    }
  }

  if (vk >= 0x20 && vk <= 0x7e) {
    const char = String.fromCharCode(vk);
    if (char === " ") return "Space";
    if (scan === 0x000d) return "Key =";
    if (scan === 0x000c) return "Key -";
    if (scan === 0x0027) return "Key ;";
    return `Key ${char}`;
  }

  for (const [name, value] of keyNameMap) {
    if (value.vk === vk && value.scan === scan) {
      return name;
    }
  }

  return `vk=0x${vk.toString(16).toUpperCase().padStart(4, "0")} scan=0x${scan
    .toString(16)
    .toUpperCase()
    .padStart(4, "0")}`;
}

function decodeRank(rankBits: number) {
  const exact = rankFloatBits.get(rankBits);
  if (exact) {
    return exact;
  }

  const bytes = Buffer.alloc(4);
  bytes.writeUInt32LE(rankBits);
  const value = bytes.readFloatLE();
  if (value >= 0.9) return `~S (${value.toFixed(2)})`;
  if (value >= 0.7) return `~A (${value.toFixed(2)})`;
  if (value >= 0.5) return `~B (${value.toFixed(2)})`;
  if (value >= 0.25) return `~C (${value.toFixed(2)})`;
  if (value >= 0.1) return `~D (${value.toFixed(2)})`;
  if (value > 0) return `~D (${value.toFixed(2)})`;
  if (value === 0) return "E";
  if (value < 0) return "NONE";
  return `? (${value.toFixed(2)})`;
}

function nextUnlockThreshold(categoryIndex: number, kills: number) {
  for (const threshold of killThresholds[categoryIndex] ?? []) {
    if (kills < threshold) {
      return threshold;
    }
  }
  return null;
}

function buildGoodieRow(index: number, stateRaw: number): SaveGoodieSummaryRow {
  const description = describeGoodie(index);
  return {
    index,
    fileOffsetHex: toHexOffset(goodieBase + index * 4),
    stateRaw,
    stateLabel: goodieStateLabel(stateRaw),
    stateGroup: goodieStateGroup(stateRaw),
    ...description
  };
}

function goodieStateLabel(value: number) {
  if (value === 0) return "Locked";
  if (value === 1) return "Instructions";
  if (value === 2) return "New";
  if (value === 3) return "Old";
  return `Other (${value})`;
}

function goodieStateGroup(value: number): SaveGoodieSummaryRow["stateGroup"] {
  if (value === 0) return "locked";
  if (value === 1) return "instructions";
  if (value === 2) return "new";
  if (value === 3) return "old";
  return "other";
}

function describeGoodie(index: number): Omit<SaveGoodieSummaryRow, "index" | "fileOffsetHex" | "stateRaw" | "stateLabel" | "stateGroup"> {
  const explicit = explicitGoodieTitles.get(index);
  const contentType = goodieContentType(index);
  const title = explicit?.title ?? defaultGoodieTitle(index);
  const unlockHint = explicit?.unlockHint ?? defaultGoodieUnlock(index);
  const assetHint = index <= 231 ? `goodie_${index.toString().padStart(2, "0")}_res_PC.aya` : "FMV slot 232 maps to cutscene file 33";
  const mediaQuery = goodieMediaQuery(index, contentType, title, assetHint);

  return {
    contentType,
    title,
    unlockHint,
    assetHint,
    mediaQuery
  };
}

function goodieContentType(index: number): SaveGoodieSummaryRow["contentType"] {
  if (index >= 0 && index <= 7) return "Character bio";
  if (index >= 8 && index <= 65) return "Model";
  if (index >= 66 && index <= 70) return "Race level";
  if (index >= 74 && index <= 78) return "Developer";
  if (index >= 79 && index <= 200) return "Concept art";
  if (index >= 201 && index <= 232) return "FMV";
  return "Reserved";
}

function goodieMediaQuery(
  index: number,
  contentType: SaveGoodieSummaryRow["contentType"],
  title: string,
  assetHint: string
) {
  if (contentType === "FMV") return fmvMediaQuery(index);
  if (contentType === "Character bio") return characterBioMediaQuery(index);
  if (contentType === "Concept art") return "goodies\\ca_";
  if (contentType === "Developer") return "goodies";
  if (contentType === "Model") return title;
  return assetHint.replace(".aya", "");
}

function characterBioMediaQuery(index: number) {
  const queries = [
    "ca_fc_hawk",
    "ca_fc_tatianna",
    "ca_fc_kramer",
    "ca_fc_lorenzo",
    "ca_fc_tara",
    "ca_fc_billy",
    "ca_fc_carver",
    "ca_mc_surt"
  ];
  return queries[index] ?? "goodies\\ca_f_characters";
}

function defaultGoodieTitle(index: number) {
  if (index >= 12 && index <= 32) return `Unit model ${index}`;
  if (index >= 71 && index <= 73) return `Reserved display slot ${index}`;
  if (index >= 79 && index <= 120) return `Concept art C-grade ${index - 78}`;
  if (index >= 121 && index <= 163) return `Concept art B-grade ${index - 120}`;
  if (index >= 164 && index <= 200) return `Concept art A-grade ${index - 163}`;
  if (index >= 201 && index <= 232) return `FMV cutscene ${index - 200}`;
  return `Goodie ${index}`;
}

function defaultGoodieUnlock(index: number) {
  if (index >= 12 && index <= 32) return "Campaign unit/model unlock";
  if (index >= 71 && index <= 73) return "Reserved display slot";
  if (index >= 79 && index <= 120) return "Earn C rank or better on the matching mission tier";
  if (index >= 121 && index <= 163) return "Earn B rank or better on the matching mission tier";
  if (index >= 164 && index <= 200) return "Earn A rank or better on the matching mission tier";
  if (index >= 201 && index <= 232) return "Unlocked at runtime after the cutscene is watched";
  return "Reserved or currently unmapped";
}

function fmvMediaQuery(index: number) {
  const cutscene = index === 232 ? 33 : index - 200;
  return `cutscene ${cutscene.toString().padStart(2, "0")}`;
}

function rankDistributionRows(rankCounts: Map<string, number>): SaveRankSummaryRow[] {
  const preferredOrder = ["S", "A", "B", "C", "D", "E", "NONE"];
  return [...rankCounts.entries()]
    .sort(([left], [right]) => {
      const leftIndex = preferredOrder.indexOf(left);
      const rightIndex = preferredOrder.indexOf(right);
      if (leftIndex === -1 && rightIndex === -1) return left.localeCompare(right);
      if (leftIndex === -1) return 1;
      if (rightIndex === -1) return -1;
      return leftIndex - rightIndex;
    })
    .map(([rank, count]) => ({ rank, count }));
}

async function writeInspectionArtifact(
  summary: SaveInspectionSummary,
  artifactRoot: string
): Promise<SaveInspectionSummary> {
  const jobId = buildJobId(summary.inspectedAt, summary.sha256);
  const artifactDir = path.join(path.resolve(artifactRoot), "artifacts", "save-inspection", jobId);
  const artifactPath = path.join(artifactDir, "inspection.json");
  const summaryWithArtifact: SaveInspectionSummary = {
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
    generatedAt: summary.inspectedAt,
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

async function writeComparisonArtifact(
  summary: SaveComparisonSummary,
  artifactRoot: string
): Promise<SaveComparisonSummary> {
  const jobId = buildComparisonJobId(summary.comparedAt, summary.leftSha256, summary.rightSha256);
  const artifactDir = path.join(path.resolve(artifactRoot), "artifacts", "save-comparison", jobId);
  const artifactPath = path.join(artifactDir, "comparison.json");
  const summaryWithArtifact: SaveComparisonSummary = {
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
    generatedAt: summary.comparedAt,
    mutation: false,
    input: {
      leftPath: summary.leftPath,
      rightPath: summary.rightPath,
      leftSha256: summary.leftSha256,
      rightSha256: summary.rightSha256
    },
    result: summaryWithArtifact
  };

  await fs.mkdir(artifactDir, { recursive: true });
  await fs.writeFile(artifactPath, `${JSON.stringify(record, null, 2)}\n`, "utf8");
  return summaryWithArtifact;
}

function regionName(offset: number) {
  if (offset < careerBase) return "VersionWord";
  if (offset < nodeBase) return "CCareerHeader";
  if (offset < linkBase) {
    const node = Math.floor((offset - nodeBase) / nodeSize);
    const fieldOffset = (offset - nodeBase) % nodeSize;
    return `Node[${node}]+0x${fieldOffset.toString(16).toUpperCase().padStart(2, "0")}`;
  }
  if (offset < goodieBase) {
    const link = Math.floor((offset - linkBase) / linkSize);
    return `Link[${link}]`;
  }
  if (offset < killsBase) {
    const goodie = Math.floor((offset - goodieBase) / 4);
    return `Goodie[${goodie}]`;
  }
  if (offset < techSlotsBase) {
    const kill = Math.floor((offset - killsBase) / 4);
    return `Kills[${killCategories[kill] ?? kill}]`;
  }
  if (offset < careerInProgress) return "TechSlots";
  if (offset < 0x24be) return "CareerSettings";
  if (offset < expectedFileSize - 0x56) return "OptionsEntries";
  if (offset < expectedFileSize) return "OptionsTail";
  return "FileSizeMismatch";
}

function buildRange(startOffset: number, endOffset: number): SaveComparisonRange {
  return {
    startOffsetHex: toHexOffset(startOffset),
    endOffsetHex: toHexOffset(endOffset),
    byteLength: endOffset - startOffset + 1
  };
}

function buildJobId(inspectedAt: string, sha256: string) {
  const compactTimestamp = inspectedAt.replace(/\D/g, "").slice(0, 14);
  return `save-${compactTimestamp}-${sha256.slice(0, 8)}`;
}

function buildComparisonJobId(comparedAt: string, leftSha256: string, rightSha256: string) {
  const compactTimestamp = comparedAt.replace(/\D/g, "").slice(0, 14);
  return `compare-${compactTimestamp}-${leftSha256.slice(0, 6)}-${rightSha256.slice(0, 6)}`;
}

function toHex16(value: number) {
  return `0x${value.toString(16).toUpperCase().padStart(4, "0")}`;
}

function toHex32(value: number) {
  return `0x${value.toString(16).toUpperCase().padStart(8, "0")}`;
}

function toHexOffset(value: number) {
  return `0x${value.toString(16).toUpperCase()}`;
}
