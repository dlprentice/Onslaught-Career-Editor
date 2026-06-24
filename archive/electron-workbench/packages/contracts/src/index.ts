export type Tone = "good" | "warn" | "danger" | "neutral";

export interface WorkbenchMetric {
  label: string;
  value: string;
  tone: Tone;
}

export interface FeatureLane {
  id: string;
  title: string;
  status: string;
  detail: string;
}

export interface ReleaseGate {
  label: string;
  status: string;
  detail: string;
}

export interface RuntimeSnapshot {
  mode: "browser-mock" | "electron-dev" | "electron-packaged";
  repoRoot: string;
  generatedAt: string;
  migration: {
    headline: string;
    summary: string;
    status: string;
  };
  metrics: WorkbenchMetric[];
  featureLanes: FeatureLane[];
  releaseGates: ReleaseGate[];
}

export type PatchTrack = "Stable" | "Experimental" | string;
export type PatchState = "original" | "patched" | "mismatch" | "out-of-range";
export type PatchTone = "ready" | "applied" | "danger" | "neutral";

export interface PatchSpecSummary {
  id: string;
  title: string;
  track: PatchTrack;
  fileOffset: number;
  fileOffsetHex: string;
  byteLength: number;
  optional: boolean;
  purpose?: string;
}

export interface PatchVerifyRow {
  spec: PatchSpecSummary;
  state: PatchState;
  stateLabel: string;
  tone: PatchTone;
  currentBytesHex?: string;
}

export interface PatchCatalogSummary {
  catalogVersion: string;
  generatedAt?: string;
  catalogPath: string;
  patchCount: number;
}

export interface SpecimenVerificationSummary {
  selectedPath: string;
  fileName: string;
  fileSize: number;
  sha256: string;
  verifiedAt: string;
  isKnownRetailSteamHash: boolean;
  catalog: PatchCatalogSummary;
  counts: {
    original: number;
    patched: number;
    mismatch: number;
    outOfRange: number;
  };
  rows: PatchVerifyRow[];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "specimen-verification.v1";
    jobId?: string;
    artifactPath?: string;
    note: string;
  };
}

export interface PatchPlanRow {
  id: string;
  title: string;
  track: string;
  optional: boolean;
  fileOffsetHex: string;
  byteLength: number;
  currentState: PatchState;
  action: "would-apply" | "already-applied" | "blocked";
  reason: string;
}

export interface PatchPlanPayload {
  executablePath: string;
  fileName: string;
  fileSize: number;
  sha256: string;
  plannedAt: string;
  patchIds: string[];
  canApplyAll: boolean;
  counts: {
    selected: number;
    readyToApply: number;
    alreadyApplied: number;
    blocked: number;
    optional: number;
  };
  rows: PatchPlanRow[];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "patch-plan.v1";
    jobId?: string;
    artifactPath?: string;
    note: string;
  };
}

export interface PatchApplyPayload {
  schemaVersion: "patch-apply.v1";
  generatedAt: string;
  command: "apply-catalog-patch";
  mutation: true;
  input: {
    executablePath: string;
    patchIds: string;
  };
  target: {
    path: string;
    fileName: string;
    fileSize: number;
    beforeSha256: string;
    afterSha256: string;
    changed: boolean;
    readbackVerified: boolean;
  };
  backup: {
    backupPath: string;
    sha256: string;
    fileSize: number;
  };
  counts: {
    selected: number;
    applied: number;
    alreadyApplied: number;
    blocked: number;
  };
  rows: Array<PatchPlanRow & {
    afterState: PatchState;
  }>;
  verification: {
    before: Pick<SpecimenVerificationSummary, "counts" | "sha256" | "isKnownRetailSteamHash">;
    after: Pick<SpecimenVerificationSummary, "counts" | "sha256" | "isKnownRetailSteamHash">;
  };
  artifact: {
    kind: "local-file-write";
    mutation: true;
    schemaVersion: "patch-apply.v1";
    backupPath: string;
    artifactPath?: string;
    note: string;
  };
}

export interface PatchRestorePayload {
  schemaVersion: "patch-restore.v1";
  generatedAt: string;
  command: "restore-catalog-patch-backup";
  mutation: true;
  input: {
    targetPath: string;
    backupPath: string;
  };
  target: {
    path: string;
    fileName: string;
    fileSize: number;
    beforeSha256: string;
    afterSha256: string;
    readbackVerified: boolean;
  };
  backup: {
    path: string;
    fileName: string;
    fileSize: number;
    sha256: string;
  };
  preRestoreBackup: {
    backupPath: string;
    sha256: string;
    fileSize: number;
  };
  verification: Pick<SpecimenVerificationSummary, "counts" | "sha256" | "isKnownRetailSteamHash">;
  artifact: {
    kind: "local-file-write";
    mutation: true;
    schemaVersion: "patch-restore.v1";
    artifactPath?: string;
    note: string;
  };
}

export interface ExecutableCopyPayload {
  schemaVersion: "patch-executable-copy.v1";
  generatedAt: string;
  command: "copy-executable";
  mutation: true;
  source: {
    path: string;
    fileName: string;
    fileSize: number;
    sha256: string;
    isKnownRetailSteamHash: boolean;
    counts: SpecimenVerificationSummary["counts"];
  };
  copy: {
    path: string;
    fileName: string;
    fileSize: number;
    sha256: string;
    readbackVerified: boolean;
  };
  catalog: PatchCatalogSummary;
  artifact: {
    kind: "local-file-copy";
    mutation: true;
    schemaVersion: "patch-executable-copy.v1";
    artifactPath?: string;
    note: string;
  };
}

export interface SaveKillSummaryRow {
  categoryIndex: number;
  categoryName: string;
  kills: number;
  meta: number;
  nextUnlockThreshold: number | null;
}

export interface SaveRankSummaryRow {
  rank: string;
  count: number;
}

export interface SaveCompletedNodeSample {
  index: number;
  world: number;
  rank: string;
  rankBitsHex: string;
}

export interface SaveBindingSummaryRow {
  entryId: number;
  entryIdHex: string;
  actionName: string;
  slot0: string;
  slot1: string;
  slot0DeviceCode: number;
  slot0PackedKeyHex: string;
  slot1DeviceCode: number;
  slot1PackedKeyHex: string;
}

export type SaveGoodieStateGroup = "locked" | "instructions" | "new" | "old" | "other" | "reserved";

export interface SaveGoodieSummaryRow {
  index: number;
  fileOffsetHex: string;
  stateRaw: number;
  stateLabel: string;
  stateGroup: SaveGoodieStateGroup;
  contentType: "Character bio" | "Model" | "Race level" | "Developer" | "Concept art" | "FMV" | "Reserved";
  title: string;
  unlockHint: string;
  assetHint: string;
  mediaQuery: string;
}

export interface SaveInspectionSummary {
  selectedPath: string;
  fileName: string;
  fileSize: number;
  sha256: string;
  inspectedAt: string;
  isValid: boolean;
  errorMessage?: string;
  isOptionsFile: boolean;
  versionWordHex: string;
  versionValid: boolean;
  counts: {
    completedNodes: number;
    partialNodes: number;
    emptyNodes: number;
    completedLinks: number;
    totalLinks: number;
    activeTechSlots: number;
    totalTechSlots: number;
  };
  goodies: {
    displayableUnlocked: number;
    new: number;
    old: number;
    locked: number;
    instructions: number;
    other: number;
    reserved: number;
  };
  goodieRows: SaveGoodieSummaryRow[];
  kills: SaveKillSummaryRow[];
  rankDistribution: SaveRankSummaryRow[];
  completedNodeSamples: SaveCompletedNodeSample[];
  settings: {
    newGoodieCountRaw: number;
    careerInProgress: boolean;
    godModeEnabled: boolean;
    soundVolume: number;
    soundVolumeBitsHex: string;
    musicVolume: number;
    musicVolumeBitsHex: string;
    walkerInvertY: [boolean, boolean];
    flightInvertY: [boolean, boolean];
    vibration: [boolean, boolean];
    controllerConfig: [number, number];
  };
  options: {
    entryCount: number | null;
    tailStartHex: string | null;
    mouseSensitivity: number | null;
    mouseSensitivityBitsHex: string | null;
    controlSchemeIndex: number | null;
    languageIndex: number | null;
    screenShape: number | null;
    d3dDeviceIndex: number | null;
    bindingSlotLabels: [string, string];
    bindings: SaveBindingSummaryRow[];
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "save-inspection.v1";
    jobId?: string;
    artifactPath?: string;
    note: string;
  };
}

export interface AppCoreSaveAnalysisPayload {
  schemaVersion: "appcore-save-analysis.v1";
  generatedAt: string;
  command: "inspect-save";
  mutation: false;
  input: {
    path: string;
    verbose: boolean;
    dumpMystery: boolean;
  };
  analysis: Omit<SaveInspectionSummary, "selectedPath" | "inspectedAt" | "artifact" | "options" | "goodies" | "goodieRows"> & {
    filePath: string;
    sha256: string;
    goodies: Omit<SaveInspectionSummary["goodies"], "new"> & {
      newCount: number;
      displayableTotal: number;
    };
    options: Omit<SaveInspectionSummary["options"], "bindingSlotLabels" | "bindings">;
  };
  document: {
    title: string;
    modeText: string;
    statusText: string;
    metrics: Array<{
      label: string;
      value: string;
      detail?: string;
    }>;
    reportText?: string;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "appcore-save-analysis.v1";
    note: string;
  };
}

export interface AppCoreSaveComparisonPayload {
  schemaVersion: "appcore-save-comparison.v1";
  generatedAt: string;
  command: "compare-saves";
  mutation: false;
  input: {
    leftPath: string;
    rightPath: string;
    verbose: boolean;
  };
  comparison: {
    leftPath: string;
    rightPath: string;
    leftFileName: string;
    rightFileName: string;
    leftFileSize: number;
    rightFileSize: number;
    leftSha256: string;
    rightSha256: string;
    sameSize: boolean;
    identical: boolean;
    differingBytes: number;
    errorMessage?: string;
    topRegions: SaveComparisonRegionCount[];
    diffRanges: Array<SaveComparisonRange & { endOffsetExclusiveHex: string }>;
  };
  document: {
    title: string;
    statusText: string;
    reportText?: string;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "appcore-save-comparison.v1";
    note: string;
  };
}

export interface AppCoreSavePatchRequestPayload {
  schemaVersion: "appcore-save-patch-request.v1";
  generatedAt: string;
  mutation: false;
  input: {
    path: string;
    rank: string;
    kills: number;
    useNewGoodies: boolean;
    killsOnly: boolean;
    patchNodes: boolean;
    patchLinks: boolean;
    patchGoodies: boolean;
    patchKills: boolean;
    allowCareerSectionsOnOptionsFile: boolean;
    levelRanks: Array<{ nodeIndex: number; rank: string }>;
    perCategoryKills: Array<{ categoryIndex: number; categoryName: string; kills: number }>;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "appcore-save-patch-request.v1";
    note: string;
  };
}

export type SavePatchRequestInput = AppCoreSavePatchRequestPayload["input"];

export interface OptionsPatchKeybindOverride {
  action?: string;
  entryId?: number;
  slot0?: string | null;
  slot1?: string | null;
}

export interface OptionsPatchRequestInput {
  path: string;
  soundVolume: number | null;
  musicVolume: number | null;
  invertWalkerP1: boolean | null;
  invertWalkerP2: boolean | null;
  invertFlightP1: boolean | null;
  invertFlightP2: boolean | null;
  vibrationP1: boolean | null;
  vibrationP2: boolean | null;
  controllerConfigP1: number | null;
  controllerConfigP2: number | null;
  mouseSensitivity: number | null;
  controlSchemeIndex: number | null;
  languageIndex: number | null;
  screenShape: number | null;
  d3dDeviceIndex: number | null;
  copyOptionsFromPath: string | null;
  copyOptionsEntries: boolean;
  copyOptionsTail: boolean;
  keybindOverrides: OptionsPatchKeybindOverride[];
}

export interface OptionsPatchSourceSummary {
  path: string;
  fileName: string;
  fileSize: number;
  sha256: string;
  isValid: boolean;
  isOptionsFile: boolean;
  versionWordHex: string;
  versionValid: boolean;
  optionsEntryCount: number | null;
  optionsTailStartHex: string | null;
}

export interface OptionsPatchSnapshot {
  settings: SaveInspectionSummary["settings"];
  options: Pick<
    SaveInspectionSummary["options"],
    | "entryCount"
    | "tailStartHex"
    | "mouseSensitivity"
    | "mouseSensitivityBitsHex"
    | "controlSchemeIndex"
    | "languageIndex"
    | "screenShape"
    | "d3dDeviceIndex"
    | "bindingSlotLabels"
  > & {
    bindingCount: number;
  };
}

export interface OptionsPatchPlanPayload {
  schemaVersion: "options-patch-plan.v1";
  generatedAt: string;
  command: "plan-options-patch";
  mutation: false;
  input: OptionsPatchRequestInput;
  source: OptionsPatchSourceSummary;
  current: OptionsPatchSnapshot;
  plan: {
    accepted: boolean;
    targetKind: "global-options";
    sections: string[];
    sectionCount: number;
    settingsOverrideCount: number;
    tailOverrideCount: number;
    keybindOverrideCount: number;
    copyOptionsEntries: boolean;
    copyOptionsTail: boolean;
    requiresCopiedApply: boolean;
    sourceUnchanged: boolean;
    notes: string[];
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "options-patch-plan.v1";
    artifactPath?: string;
    note: string;
  };
}

export interface OptionsPatchPreviewPayload {
  schemaVersion: "options-patch-preview.v1";
  generatedAt: string;
  command: "preview-options-patch";
  mutation: false;
  input: OptionsPatchRequestInput;
  source: OptionsPatchSourceSummary;
  preview: {
    success: boolean;
    message: string;
    wouldChange: boolean;
    candidateSha256: string;
    differingBytes: number;
    topRegion?: string;
    candidateArtifactPath?: string;
  };
  beforeAfter: {
    before: OptionsPatchSnapshot;
    after: OptionsPatchSnapshot;
  };
  comparison: {
    sameSize: boolean;
    identical: boolean;
    differingBytes: number;
    errorMessage?: string;
    topRegions: SaveComparisonRegionCount[];
    diffRanges: Array<SaveComparisonRange & { endOffsetExclusiveHex: string }>;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "options-patch-preview.v1";
    artifactPath?: string;
    candidateArtifactPath?: string;
    note: string;
  };
}

export interface OptionsPatchApplyPayload {
  schemaVersion: "options-patch-apply.v1";
  generatedAt: string;
  command: "apply-options-patch";
  mutation: true;
  input: OptionsPatchRequestInput;
  target: OptionsPatchSourceSummary & {
    path: string;
    changed: boolean;
    beforeSha256: string;
    afterSha256: string;
    readbackVerified: boolean;
  };
  backup: {
    backupPath: string;
    sha256: string;
    fileSize: number;
  };
  beforeAfter: OptionsPatchPreviewPayload["beforeAfter"];
  comparison: OptionsPatchPreviewPayload["comparison"];
  artifact: {
    kind: "local-file-write";
    mutation: true;
    schemaVersion: "options-patch-apply.v1";
    artifactPath?: string;
    backupPath: string;
    note: string;
  };
}

export interface SaveCopyPayload {
  schemaVersion: "save-copy.v1";
  generatedAt: string;
  command: "copy-save-file";
  mutation: false;
  input: {
    sourcePath: string;
  };
  source: {
    path: string;
    fileName: string;
    fileSize: number;
    sha256: string;
    isValid: boolean;
    isOptionsFile: boolean;
    versionWordHex: string;
    versionValid: boolean;
  };
  copy: {
    path: string;
    fileName: string;
    fileSize: number;
    sha256: string;
    readbackVerified: boolean;
  };
  inspection: {
    completedNodes: number;
    displayableGoodiesUnlocked: number;
    totalKills: number;
    optionsEntryCount: number | null;
  };
  artifact: {
    kind: "local-file-copy";
    mutation: false;
    schemaVersion: "save-copy.v1";
    artifactPath?: string;
    note: string;
  };
}

export interface SavePatchPlanPayload {
  schemaVersion: "save-patch-plan.v1";
  generatedAt: string;
  command: "plan-save-patch";
  mutation: false;
  input: SavePatchRequestInput;
  source: AppCoreSavePatchPlanPayload["source"];
  current: AppCoreSavePatchPlanPayload["current"];
  plan: AppCoreSavePatchPlanPayload["plan"];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "save-patch-plan.v1";
    artifactPath?: string;
    note: string;
  };
}

export interface SavePatchPreviewPayload {
  schemaVersion: "save-patch-preview.v1";
  generatedAt: string;
  command: "preview-save-patch";
  mutation: false;
  input: SavePatchRequestInput;
  source: AppCoreSavePatchPreviewPayload["source"];
  preview: AppCoreSavePatchPreviewPayload["preview"] & {
    candidateArtifactPath?: string;
  };
  beforeAfter: AppCoreSavePatchPreviewPayload["beforeAfter"];
  comparison: AppCoreSavePatchPreviewPayload["comparison"];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "save-patch-preview.v1";
    artifactPath?: string;
    candidateArtifactPath?: string;
    note: string;
  };
}

export interface SavePatchApplyPayload {
  schemaVersion: "save-patch-apply.v1";
  generatedAt: string;
  command: "apply-save-patch";
  mutation: true;
  input: SavePatchRequestInput;
  target: SavePatchPlanPayload["source"] & {
    path: string;
    changed: boolean;
    beforeSha256: string;
    afterSha256: string;
    readbackVerified: boolean;
  };
  backup: {
    backupPath: string;
    sha256: string;
    fileSize: number;
  };
  beforeAfter: SavePatchPreviewPayload["beforeAfter"];
  comparison: SavePatchPreviewPayload["comparison"];
  artifact: {
    kind: "local-file-write";
    mutation: true;
    schemaVersion: "save-patch-apply.v1";
    artifactPath?: string;
    backupPath: string;
    note: string;
  };
}

export interface SavePatchRestorePayload {
  schemaVersion: "save-patch-restore.v1";
  generatedAt: string;
  command: "restore-save-backup";
  mutation: true;
  input: {
    targetPath: string;
    backupPath: string;
  };
  target: {
    path: string;
    fileName: string;
    fileSize: number;
    beforeSha256: string | null;
    afterSha256: string;
    readbackVerified: boolean;
  };
  backup: {
    path: string;
    fileName: string;
    fileSize: number;
    sha256: string;
  };
  preRestoreBackup?: {
    backupPath: string;
    sha256: string;
    fileSize: number;
  };
  artifact: {
    kind: "local-file-write";
    mutation: true;
    schemaVersion: "save-patch-restore.v1";
    artifactPath?: string;
    note: string;
  };
}

export interface AppCoreSavePatchPlanPayload {
  schemaVersion: "appcore-save-patch-plan.v1";
  generatedAt: string;
  command: "plan-save-patch";
  mutation: false;
  request: {
    schemaVersion: "appcore-save-patch-request.v1";
    requestPath: string;
    requestSha256: string;
  };
  input: AppCoreSavePatchRequestPayload["input"];
  source: {
    path: string;
    fileName: string;
    fileSize: number;
    sha256: string;
    isValid: boolean;
    isOptionsFile: boolean;
    versionWordHex: string;
    versionValid: boolean;
  };
  current: {
    completedNodes: number;
    partialNodes: number;
    displayableGoodiesUnlocked: number;
    totalKills: number;
    kills: Array<{ categoryIndex: number; categoryName: string; kills: number; meta: number }>;
    rankDistribution: SaveRankSummaryRow[];
  };
  plan: {
    accepted: boolean;
    targetKind: "career-save" | "global-options" | string;
    sections: string[];
    sectionCount: number;
    levelRankCount: number;
    perCategoryKillCount: number;
    willPatchCareerSections: boolean;
    requiresCopiedApply: boolean;
    sourceUnchanged: boolean;
    notes: string[];
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "appcore-save-patch-plan.v1";
    note: string;
  };
}

export interface AppCoreSavePatchPreviewPayload {
  schemaVersion: "appcore-save-patch-preview.v1";
  generatedAt: string;
  command: "preview-save-patch";
  mutation: false;
  input: {
    path: string;
    rank: string;
    kills: number;
    useNewGoodies: boolean;
    patchNodes: boolean;
    patchLinks: boolean;
    patchGoodies: boolean;
    patchKills: boolean;
    allowCareerSectionsOnOptionsFile: boolean;
    levelRanks: Array<{ nodeIndex: number; rank: string }>;
    perCategoryKills: Array<{ categoryIndex: number; categoryName: string; kills: number }>;
  };
  source: {
    path: string;
    fileName: string;
    fileSize: number;
    sha256: string;
    isValid: boolean;
    isOptionsFile: boolean;
    versionWordHex: string;
    versionValid: boolean;
  };
  preview: {
    success: boolean;
    message: string;
    wouldChange: boolean;
    tempOutputDeleted: boolean;
    candidateSha256: string;
    differingBytes: number;
    topRegion?: string;
  };
  beforeAfter: {
    completedNodes: { before: number; after: number };
    partialNodes: { before: number; after: number };
    displayableGoodiesUnlocked: { before: number; after: number };
    totalKills: { before: number; after: number };
    rankDistribution: {
      before: SaveRankSummaryRow[];
      after: SaveRankSummaryRow[];
    };
  };
  comparison: {
    sameSize: boolean;
    identical: boolean;
    differingBytes: number;
    errorMessage?: string;
    topRegions: SaveComparisonRegionCount[];
    diffRanges: Array<SaveComparisonRange & { endOffsetExclusiveHex: string }>;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "appcore-save-patch-preview.v1";
    note: string;
  };
}

export interface SaveComparisonRegionCount {
  region: string;
  differingBytes: number;
}

export interface SaveComparisonRange {
  startOffsetHex: string;
  endOffsetHex: string;
  byteLength: number;
}

export interface SaveComparisonSummary {
  leftPath: string;
  rightPath: string;
  leftFileName: string;
  rightFileName: string;
  leftFileSize: number;
  rightFileSize: number;
  leftSha256: string;
  rightSha256: string;
  comparedAt: string;
  sameSize: boolean;
  differingBytes: number;
  identical: boolean;
  topRegions: SaveComparisonRegionCount[];
  diffRanges: SaveComparisonRange[];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "save-comparison.v1";
    jobId?: string;
    artifactPath?: string;
    note: string;
  };
}

export interface HexReadRow {
  offset: number;
  offsetHex: string;
  hex: string;
  ascii: string;
}

export interface HexReadSummary {
  selectedPath: string;
  fileName: string;
  fileSize: number;
  sha256: string;
  readAt: string;
  offset: number;
  offsetHex: string;
  requestedLength: number;
  byteLength: number;
  truncated: boolean;
  rows: HexReadRow[];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "hex-read.v1";
    jobId?: string;
    artifactPath?: string;
    note: string;
  };
}

export interface AddressConversionSection {
  name: string;
  virtualAddressHex: string;
  virtualSizeHex: string;
  rawPointerHex: string;
  rawSizeHex: string;
}

export interface AddressConversionSummary {
  executablePath: string;
  fileName: string;
  fileSize: number;
  sha256: string;
  convertedAt: string;
  imageBaseHex: string;
  virtualAddressHex: string;
  rvaHex: string;
  fileOffsetHex: string;
  fileOffset: number;
  section: AddressConversionSection | null;
  shortcutTextVaMinusImageBase: boolean;
  note: string;
}

export interface ToolPathStatus {
  label: string;
  path: string;
  exists: boolean;
  kind: "file" | "directory" | "missing";
  role: string;
}

export interface PlannedCommand {
  label: string;
  command: string;
  mutation: boolean;
  status: "ready" | "blocked";
  detail: string;
}

export interface GhidraReadinessSummary {
  checkedAt: string;
  repoRoot: string;
  configuredInstallPath: string;
  configuredProjectRoot: string;
  configuredMcpBundlePath: string;
  paths: ToolPathStatus[];
  commands: PlannedCommand[];
  readOnlyScripts: string[];
  mutationScripts: string[];
  ready: boolean;
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "ghidra-readiness.v1";
    note: string;
  };
}

export interface DebugReadinessSummary {
  checkedAt: string;
  repoRoot: string;
  paths: ToolPathStatus[];
  probeScripts: ToolPathStatus[];
  commands: PlannedCommand[];
  ready: boolean;
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "debug-readiness.v1";
    note: string;
  };
}

export interface GameHarnessFileStatus {
  label: string;
  path: string;
  exists: boolean;
  required: boolean;
  role: string;
}

export interface GameHarnessProfileSummary {
  checkedAt: string;
  repoRoot: string;
  gameRoot: string;
  profileSource: "repo-default" | "stored" | "selected";
  configPath?: string;
  executablePath: string;
  workingDirectory: string;
  recommendedArgs: string[];
  files: GameHarnessFileStatus[];
  launchPlan: PlannedCommand;
  ready: boolean;
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "game-harness-profile.v1";
    note: string;
  };
}

export type GameWindowCaptureStatus = "ready" | "no-window" | "multiple-candidates" | "unsupported";

export interface GameWindowBounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
}

export interface GameWindowCandidate {
  processId: number;
  processName: string;
  title: string;
  hwndHex: string;
  visible: boolean;
  minimized: boolean;
  bounds: GameWindowBounds;
  captureSourceHint: string;
}

export interface GameWindowCapturePlanPayload {
  schemaVersion: "game-window-capture-plan.v1";
  generatedAt: string;
  mutation: false;
  processName: string;
  targetRunId: string | null;
  status: GameWindowCaptureStatus;
  counts: {
    candidates: number;
    visible: number;
    minimized: number;
  };
  selectedWindow: GameWindowCandidate | null;
  windows: GameWindowCandidate[];
  capture: {
    status: GameWindowCaptureStatus;
    method: "electron-desktop-capturer";
    sourceHint: string | null;
    note: string;
  };
  input: {
    status: "planned";
    method: "scoped-window-input";
    note: string;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "game-window-capture-plan.v1";
    note: string;
  };
}

export type GameWindowFrameCaptureStatus =
  | "captured"
  | "no-window"
  | "multiple-candidates"
  | "unsupported"
  | "capture-unavailable"
  | "source-not-found";

export interface GameWindowFrameCapturePayload {
  schemaVersion: "game-window-frame-capture.v1";
  generatedAt: string;
  mutation: false;
  processName: string;
  targetRunId: string | null;
  status: GameWindowFrameCaptureStatus;
  selectedWindow: GameWindowCandidate | null;
  planArtifactPath: string | null;
  capture: {
    status: GameWindowFrameCaptureStatus;
    method: "electron-desktop-capturer";
    sourceHint: string | null;
    sourceId: string | null;
    sourceName: string | null;
    matchedBy: "hwnd" | "hint" | "exact-title" | "loose-title" | "none";
    sourceCount: number;
    note: string;
  };
  frame: {
    capturedAt: string;
    width: number;
    height: number;
    sizeBytes: number;
    mimeType: "image/png";
    sha256: string;
    pngPath: string;
    previewDataUrl: string | null;
    previewWidth: number | null;
    previewHeight: number | null;
    previewSizeBytes: number | null;
  } | null;
  input: {
    status: "planned";
    method: "scoped-window-input";
    note: string;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "game-window-frame-capture.v1";
    note: string;
  };
}

export type ReleasePolicyClassification = "allow" | "review" | "conditional" | "deny";
export type ReleasePolicyAudience = "community" | "maintainer" | "private";

export interface ReleasePolicyPathRule {
  label: string;
  relativePath: string;
  classification: ReleasePolicyClassification;
  audience: ReleasePolicyAudience;
  exists: boolean;
  reason: string;
}

export interface ReleasePolicyContentRow {
  id: string;
  title: string;
  group: ContentIndexItem["group"];
  relativePath: string;
  communitySafe: boolean;
  audience: Exclude<ReleasePolicyAudience, "private">;
  packageDecision: "ship" | "maintainer-only";
  reason: string;
}

export interface ReleasePolicyProfile {
  id: "source-tree" | "portable-bundle";
  title: string;
  status: "usable-with-review" | "blocked";
  summary: string;
  requiredActions: string[];
}

export interface ReleasePolicySummary {
  generatedAt: string;
  repoRoot: string;
  counts: {
    contentTotal: number;
    communityDocs: number;
    maintainerDocs: number;
    allow: number;
    review: number;
    conditional: number;
    deny: number;
    existingDeniedPaths: number;
  };
  profiles: ReleasePolicyProfile[];
  content: ReleasePolicyContentRow[];
  pathRules: ReleasePolicyPathRule[];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "release-policy.v1";
    artifactPath?: string;
    note: string;
  };
}

export interface GameWindowFrameSequencePayload {
  schemaVersion: "game-window-frame-sequence.v1";
  generatedAt: string;
  mutation: false;
  processName: string;
  targetRunId: string | null;
  status: "captured" | "partial" | GameWindowFrameCaptureStatus;
  selectedWindow: GameWindowCandidate | null;
  requested: {
    frameCount: number;
    intervalMs: number;
    maxWidth: number;
    maxHeight: number;
  };
  capturedCount: number;
  frames: Array<{
    index: number;
    status: GameWindowFrameCaptureStatus;
    capturedAt: string;
    pngPath: string | null;
    width: number | null;
    height: number | null;
    sizeBytes: number | null;
    sha256: string | null;
    sourceId: string | null;
    sourceName: string | null;
    previewDataUrl: string | null;
  }>;
  input: {
    status: "available";
    method: "scoped-window-input";
    note: string;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "game-window-frame-sequence.v1";
    artifactPath?: string;
    note: string;
  };
}

export type GameWindowInputStatus =
  | "ready"
  | "sent"
  | "target-required"
  | "no-window"
  | "multiple-candidates"
  | "unsupported";
export type GameWindowInputActionKind = "tap" | "down" | "up" | "wait";

export interface GameWindowInputAction {
  kind: GameWindowInputActionKind;
  key: string | null;
  virtualKey: number | null;
  durationMs: number | null;
}

export interface GameWindowInputPayload {
  schemaVersion: "game-window-input.v1";
  generatedAt: string;
  mutation: false;
  processName: string;
  processId: number | null;
  hwndHex: string | null;
  status: GameWindowInputStatus;
  plannedOnly: boolean;
  focused?: boolean;
  actionCount: number;
  keyEventsSent?: number;
  actions: GameWindowInputAction[];
  selectedWindow: {
    processId: number;
    processName: string;
    title: string;
    hwndHex: string;
    minimized: boolean;
  } | null;
  artifact: {
    kind: "read-only" | "external-process";
    mutation: false;
    schemaVersion: "game-window-input.v1";
    artifactPath?: string;
    note: string;
  };
  note: string;
}

export type ManagedProcessKind = "game" | "debugger";
export type ManagedProcessStatus = "running" | "exited" | "unknown" | "stop-requested";

export interface ManagedProcessRegistryEntry {
  runId: string;
  definitionId: string;
  kind: ManagedProcessKind;
  processId: number;
  processName: string;
  startedAt: string;
  lastCheckedAt: string;
  status: ManagedProcessStatus;
  gameRoot?: string;
  executablePath?: string;
  workingDirectory?: string;
  port?: number;
  logPath?: string;
  sourceArtifactPath?: string;
  commandPreview?: string;
  stopRequestedAt?: string;
  stopError?: string;
}

export interface ManagedProcessRegistryPayload {
  schemaVersion: "managed-process-registry.v1";
  generatedAt: string;
  mutation: false;
  counts: {
    total: number;
    running: number;
    exited: number;
    unknown: number;
    stopRequested: number;
  };
  processes: ManagedProcessRegistryEntry[];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "managed-process-registry.v1";
    note: string;
  };
}

export interface ManagedProcessStopPayload {
  schemaVersion: "managed-process-stop.v1";
  generatedAt: string;
  mutation: false;
  stopped: boolean;
  previousStatus: ManagedProcessStatus;
  currentStatus: ManagedProcessStatus;
  target: ManagedProcessRegistryEntry;
  artifact: {
    kind: "external-process";
    mutation: false;
    schemaVersion: "managed-process-stop.v1";
    note: string;
  };
}

export interface ManagedProcessLogTailPayload {
  schemaVersion: "managed-process-log-tail.v1";
  generatedAt: string;
  mutation: false;
  target: ManagedProcessRegistryEntry;
  logPath: string;
  exists: boolean;
  requestedBytes: number;
  fileSizeBytes: number;
  byteLength: number;
  truncated: boolean;
  lineCount: number;
  text: string;
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "managed-process-log-tail.v1";
    note: string;
  };
}

export type WorkbenchJobLane =
  | "appcore"
  | "save"
  | "file"
  | "patch"
  | "ghidra"
  | "debugger"
  | "runtime"
  | "game"
  | "assets"
  | "content"
  | "release";
export type WorkbenchJobSafety = "read-only" | "mutation-gated" | "launch-gated";
export type WorkbenchJobStatus = "available" | "blocked" | "planned";
export type WorkbenchJobRunStatus = "completed" | "failed" | "rejected" | "timed-out" | "cancelled";
export type WorkbenchJobProgressPhase =
  | "queued"
  | "running"
  | "artifact"
  | "completed"
  | "failed"
  | "rejected"
  | "timed-out"
  | "cancelled";
export type WorkbenchJobInputValue = string | number | boolean | null;

export interface WorkbenchJobInput {
  name: string;
  label: string;
  required: boolean;
  detail: string;
}

export interface WorkbenchJobPolicy {
  timeoutMs: number;
  cancellable: boolean;
  externalProcess: boolean;
}

export interface WorkbenchJobDefinition {
  id: string;
  lane: WorkbenchJobLane;
  title: string;
  safety: WorkbenchJobSafety;
  status: WorkbenchJobStatus;
  detail: string;
  commandPreview?: string;
  artifactSchema: string;
  policy: WorkbenchJobPolicy;
  inputs: WorkbenchJobInput[];
}

export interface WorkbenchJobCatalogSummary {
  generatedAt: string;
  repoRoot: string;
  definitions: WorkbenchJobDefinition[];
  counts: {
    available: number;
    blocked: number;
    planned: number;
    readOnly: number;
    gated: number;
  };
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "job-catalog.v1";
    note: string;
  };
}

export interface WorkbenchJobRunRequest {
  definitionId: string;
  inputs: Record<string, WorkbenchJobInputValue>;
  timeoutMs?: number;
}

export interface WorkbenchJobRunDetail {
  label: string;
  value: string;
}

export interface WorkbenchJobProgressEvent {
  runId: string;
  definitionId: string;
  phase: WorkbenchJobProgressPhase;
  percent: number;
  message: string;
  detail?: string;
  emittedAt: string;
}

export interface WorkbenchJobRunSummary {
  runId: string;
  definitionId: string;
  title: string;
  lane: WorkbenchJobLane;
  safety: WorkbenchJobSafety;
  status: WorkbenchJobRunStatus;
  startedAt: string;
  finishedAt: string;
  durationMs: number;
  inputs: Record<string, WorkbenchJobInputValue>;
  policy: WorkbenchJobPolicy;
  progress: WorkbenchJobProgressEvent[];
  result: {
    summary: string;
    payloadSchema?: string;
    details: WorkbenchJobRunDetail[];
  };
  errorMessage?: string;
  artifact: {
    kind: "read-only" | "local-file-copy" | "local-file-write" | "external-process";
    mutation: boolean;
    schemaVersion: "job-run.v1";
    jobId: string;
    artifactPath?: string;
    note: string;
  };
}

export type MediaCatalogKind = "texture" | "loose_mesh" | "embedded_mesh" | "video" | "language_row" | "audio";
export type MediaCatalogKindFilter = "all" | MediaCatalogKind;
export type MediaVideoPlaybackStatus = "needs-transcode" | "external-only" | "playable";

export interface MediaCatalogCounts {
  textures: number;
  textureReferencedInPacked: number;
  textureLooseOnly: number;
  looseMeshes: number;
  embeddedMeshes: number;
  videos: number;
  languageRows: number;
  audioRows: number;
  musicRows: number;
  voiceRows: number;
  total: number;
  videoFamilies: Record<string, number>;
}

export interface MediaCatalogRow {
  id: string;
  kind: MediaCatalogKind;
  label: string;
  group: string;
  videoFamily?: string;
  sequenceId?: string;
  codec?: string;
  playbackStatus?: MediaVideoPlaybackStatus;
  playbackNote?: string;
  sourcePath?: string;
  exportPath?: string;
  sizeBytes?: number;
  sha256?: string;
  referenceCount?: number;
  languageCount?: number;
  audioPresentCount?: number;
  playbackId?: string;
  videoPlaybackId?: string;
  previewId?: string;
  detail: string;
}

export interface MediaVideoGroup {
  family: string;
  label: string;
  count: number;
  totalBytes: number;
  sequenceRange?: string;
  playbackStatus: MediaVideoPlaybackStatus;
  note: string;
}

export interface MediaCatalogSummary {
  generatedAt: string;
  catalogPath: string;
  query: string;
  kind: MediaCatalogKindFilter;
  counts: MediaCatalogCounts;
  totalRows: number;
  returnedRows: number;
  truncated: boolean;
  videoGroups: MediaVideoGroup[];
  rows: MediaCatalogRow[];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "media-catalog.v1";
    note: string;
  };
}

export interface AudioPlaybackSummary {
  generatedAt: string;
  playbackId: string;
  label: string;
  group: string;
  sourcePath: string;
  sizeBytes: number;
  mimeType: "audio/ogg" | "audio/wav";
  dataUrl: string;
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "audio-playback.v1";
    note: string;
  };
}

export interface VideoPlaybackSummary {
  generatedAt: string;
  playbackId: string;
  label: string;
  group: string;
  sourcePath: string;
  sizeBytes: number;
  codec: string;
  mode: "inline-transcoded" | "external-vlc";
  dryRun: boolean;
  launched: boolean;
  processId?: number;
  mimeType?: "video/mp4";
  playbackUrl?: string;
  dataUrl?: string;
  cachePath?: string;
  cacheStatus?: "hit" | "created" | "dry-run" | "unavailable";
  player: {
    kind: "vlc" | "none";
    path?: string;
    available: boolean;
    detail: string;
  };
  commandPreview: string;
  artifact: {
    kind: "read-only" | "local-file-write" | "external-process";
    mutation: false;
    schemaVersion: "video-playback.v1";
    note: string;
  };
}

export interface VideoPlaybackOpenOptions {
  dryRun?: boolean;
}

export interface VideoPlaybackPrepareOptions {
  dryRun?: boolean;
}

export interface MediaPreviewSummary {
  generatedAt: string;
  previewId: string;
  label: string;
  group: string;
  sourcePath?: string;
  exportPath: string;
  sizeBytes: number;
  mimeType: "image/png";
  dataUrl: string;
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "media-preview.v1";
    note: string;
  };
}

export interface ContentIndexItem {
  id: string;
  title: string;
  group: "Lore" | "Save Docs" | "RE Docs" | "Roadmap";
  relativePath: string;
  description: string;
  communitySafe: boolean;
}

export interface ContentIndexSummary {
  generatedAt: string;
  repoRoot: string;
  items: ContentIndexItem[];
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "content-index.v1";
    note: string;
  };
}

export interface ContentDocumentSummary {
  id: string;
  title: string;
  group: ContentIndexItem["group"];
  relativePath: string;
  communitySafe: boolean;
  audience: "community" | "maintainer";
  readAt: string;
  byteLength: number;
  truncated: boolean;
  markdown: string;
  artifact: {
    kind: "read-only";
    mutation: false;
    schemaVersion: "content-document.v1";
    note: string;
  };
}

export interface OnslaughtApi {
  getRuntimeSnapshot: () => Promise<RuntimeSnapshot>;
  selectAndVerifyExecutable: () => Promise<SpecimenVerificationSummary | null>;
  verifyExecutablePath: (path: string) => Promise<SpecimenVerificationSummary>;
  selectAndInspectSaveFile: () => Promise<SaveInspectionSummary | null>;
  inspectSaveFilePath: (path: string) => Promise<SaveInspectionSummary>;
  selectAndCompareSaveFiles: () => Promise<SaveComparisonSummary | null>;
  compareSaveFilePaths: (leftPath: string, rightPath: string) => Promise<SaveComparisonSummary>;
  selectAndReadHexFile: (offset: string | number, length: string | number) => Promise<HexReadSummary | null>;
  readHexRange: (path: string, offset: string | number, length: string | number) => Promise<HexReadSummary>;
  convertExecutableAddress: (
    executablePath: string,
    virtualAddress: string | number
  ) => Promise<AddressConversionSummary>;
  getGhidraReadiness: () => Promise<GhidraReadinessSummary>;
  getDebugReadiness: () => Promise<DebugReadinessSummary>;
  getGameHarnessProfile: () => Promise<GameHarnessProfileSummary>;
  selectAndInspectGameFolder: () => Promise<GameHarnessProfileSummary | null>;
  inspectGameFolderPath: (gameRoot: string, persist?: boolean) => Promise<GameHarnessProfileSummary>;
  resetGameFolderProfile: () => Promise<GameHarnessProfileSummary>;
  getJobCatalog: () => Promise<WorkbenchJobCatalogSummary>;
  startWorkbenchJob: (request: WorkbenchJobRunRequest) => Promise<WorkbenchJobRunSummary>;
  cancelWorkbenchJob: (runId: string) => Promise<boolean>;
  onWorkbenchJobProgress: (handler: (event: WorkbenchJobProgressEvent) => void) => () => void;
  getWorkbenchJobRun: (runId: string) => Promise<WorkbenchJobRunSummary | null>;
  listWorkbenchJobRuns: () => Promise<WorkbenchJobRunSummary[]>;
  getMediaCatalog: (
    query?: string,
    kind?: MediaCatalogKindFilter,
    limit?: number
  ) => Promise<MediaCatalogSummary>;
  getAudioPlayback: (playbackId: string) => Promise<AudioPlaybackSummary>;
  prepareVideoPlayback: (playbackId: string, options?: VideoPlaybackPrepareOptions) => Promise<VideoPlaybackSummary>;
  openVideoPlayback: (playbackId: string, options?: VideoPlaybackOpenOptions) => Promise<VideoPlaybackSummary>;
  getMediaPreview: (previewId: string) => Promise<MediaPreviewSummary>;
  getContentIndex: () => Promise<ContentIndexSummary>;
  readContentDocument: (id: string) => Promise<ContentDocumentSummary>;
  getReleasePolicy: () => Promise<ReleasePolicySummary>;
  openExternal: (url: string) => Promise<void>;
}
