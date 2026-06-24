import type {
  AddressConversionSummary,
  ContentDocumentSummary,
  ContentIndexSummary,
  DebugReadinessSummary,
  GameHarnessProfileSummary,
  GhidraReadinessSummary,
  HexReadSummary,
  MediaCatalogSummary,
  ReleasePolicySummary,
  RuntimeSnapshot,
  SaveComparisonSummary,
  SaveInspectionSummary,
  SpecimenVerificationSummary,
  WorkbenchJobCatalogSummary,
  WorkbenchJobRunSummary
} from "@/types/onslaught-api";

const browserGoodieRows: SaveInspectionSummary["goodieRows"] = [
  {
    index: 0,
    fileOffsetHex: "0x1F46",
    stateRaw: 3,
    stateLabel: "Old",
    stateGroup: "old",
    contentType: "Character bio",
    title: "Hawk bio",
    unlockHint: "Complete level 100",
    assetHint: "goodie_00_res_PC.aya",
    mediaQuery: "ca_fc_hawk"
  },
  {
    index: 33,
    fileOffsetHex: "0x1FCA",
    stateRaw: 3,
    stateLabel: "Old",
    stateGroup: "old",
    contentType: "Model",
    title: "Muspell Grunt",
    unlockHint: "40 infantry kills",
    assetHint: "goodie_33_res_PC.aya",
    mediaQuery: "goodie_33_res_PC"
  },
  {
    index: 66,
    fileOffsetHex: "0x204E",
    stateRaw: 2,
    stateLabel: "New",
    stateGroup: "new",
    contentType: "Race level",
    title: "Race level 901",
    unlockHint: "26 missions at A rank or better",
    assetHint: "goodie_66_res_PC.aya",
    mediaQuery: "goodie_66_res_PC"
  },
  {
    index: 79,
    fileOffsetHex: "0x2082",
    stateRaw: 3,
    stateLabel: "Old",
    stateGroup: "old",
    contentType: "Concept art",
    title: "Concept art C-grade 1",
    unlockHint: "Earn C rank or better on the matching mission tier",
    assetHint: "goodie_79_res_PC.aya",
    mediaQuery: "goodies\\ca_"
  },
  {
    index: 201,
    fileOffsetHex: "0x226A",
    stateRaw: 3,
    stateLabel: "Old",
    stateGroup: "old",
    contentType: "FMV",
    title: "FMV cutscene 1",
    unlockHint: "Unlocked at runtime after the cutscene is watched",
    assetHint: "goodie_201_res_PC.aya",
    mediaQuery: "cutscene 01"
  },
  {
    index: 232,
    fileOffsetHex: "0x22E6",
    stateRaw: 3,
    stateLabel: "Old",
    stateGroup: "old",
    contentType: "FMV",
    title: "FMV cutscene 32",
    unlockHint: "Unlocked at runtime after the cutscene is watched",
    assetHint: "FMV slot 232 maps to cutscene file 33",
    mediaQuery: "cutscene 33"
  }
];

export const browserSnapshot: RuntimeSnapshot = {
  mode: "browser-mock",
  repoRoot: "browser://fixture",
  generatedAt: new Date().toISOString(),
  migration: {
    headline: "Onslaught Workbench is the active app",
    summary:
      "Browser preview mode uses sample data for visual testing. Desktop mode owns the file, patch, media, and RE workflows through the safe desktop job runner.",
    status: "active"
  },
  metrics: [
    { label: "Function symbols", value: "5861 / 5861", tone: "good" },
    { label: "Media catalog rows", value: "4446", tone: "good" },
    { label: "Temporary parity tests", value: "19 / 19", tone: "good" },
    { label: "App gates", value: "passing", tone: "good" }
  ],
  featureLanes: [
    {
      id: "saves",
      title: "Save and options lab",
      status: "active",
      detail:
        "Native TypeScript inspect, compare, copy, plan, preview, apply, and restore for .bes/.bea/defaultoptions files."
    },
    {
      id: "patches",
      title: "Binary patch bench",
      status: "active",
      detail:
        "Catalog verify, copied-executable prepare, apply, restore, and read-back byte provenance."
    },
    {
      id: "media",
      title: "Media and lore browser",
      status: "active",
      detail:
        "Curated lore, public-safe media catalogs, language/video/asset rows, constrained OGG playback, and app-owned Bink video preparation from the selected game root."
    },
    {
      id: "re-lab",
      title: "RE automation lab",
      status: "active foundation",
      detail:
        "Hex reads, PE address conversion, Ghidra/CDB readiness, launch/debug planning, and managed process controls are exposed as typed jobs."
    }
  ],
  releaseGates: [
    {
      label: "docsync_check.py",
      status: "passing",
      detail: "Lore-book mirrors are synchronized for the current app docs."
    },
    {
      label: "release_profile_snapshot.py --check",
      status: "passing",
      detail: "Generated profile evidence files are current after the app allowlist refresh."
    },
    {
      label: "release_curated_manifest.py --check",
      status: "passing",
      detail: "Curated manifest includes the app workspace and bundle files."
    }
  ]
};

export const browserSpecimenVerification: SpecimenVerificationSummary = {
  selectedPath: "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Battle Engine Aquila\\BEA.exe",
  fileName: "BEA.exe",
  fileSize: 2506752,
  sha256: "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
  verifiedAt: new Date().toISOString(),
  isKnownRetailSteamHash: true,
  catalog: {
    catalogVersion: "2.0",
    generatedAt: "2026-03-05 16:08:00 -0500",
    catalogPath: "patches/catalog/patches.v2.json",
    patchCount: 7
  },
  counts: {
    original: 5,
    patched: 2,
    mismatch: 0,
    outOfRange: 0
  },
  rows: [
    {
      spec: {
        id: "resolution_gate",
        title: "Allow widescreen resolutions",
        track: "Stable",
        fileOffset: 0x129696,
        fileOffsetHex: "0x129696",
        byteLength: 1,
        optional: false,
        purpose: "Neutralize non-4:3 mode rejection in display mode enumeration."
      },
      state: "patched",
      stateLabel: "already patched",
      tone: "applied",
      currentBytesHex: "00"
    },
    {
      spec: {
        id: "force_windowed",
        title: "Prefer windowed startup",
        track: "Stable",
        fileOffset: 0x12a644,
        fileOffsetHex: "0x12A644",
        byteLength: 5,
        optional: false,
        purpose: "Force startup path windowed-decision flag true."
      },
      state: "patched",
      stateLabel: "already patched",
      tone: "applied",
      currentBytesHex: "B8 01 00 00 00"
    },
    {
      spec: {
        id: "extra_graphics_default_on",
        title: "Unlock extra graphics features by default",
        track: "Stable",
        fileOffset: 0x0cdd40,
        fileOffsetHex: "0xCDD40",
        byteLength: 2,
        optional: false,
        purpose: "Change GEFORCE_FX_POWER tweak registration default from 0 to 1."
      },
      state: "original",
      stateLabel: "ready (original)",
      tone: "ready",
      currentBytesHex: "6A 00"
    },
    {
      spec: {
        id: "skip_auto_toggle",
        title: "Bypass one startup fullscreen toggle check",
        track: "Experimental",
        fileOffset: 0x12bb97,
        fileOffsetHex: "0x12BB97",
        byteLength: 2,
        optional: true,
        purpose: "Skip one startup fullscreen-toggle gate when stable patches are insufficient."
      },
      state: "original",
      stateLabel: "ready (original)",
      tone: "ready",
      currentBytesHex: "75 20"
    }
  ],
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "specimen-verification.v1",
    jobId: "browser-fixture",
    artifactPath: "browser://fixture/specimen-verification/browser-fixture/verification.json",
    note: "Preview mode only. Desktop app mode computes this from the selected executable."
  }
};

export const browserSaveInspection: SaveInspectionSummary = {
  selectedPath: "C:\\Games\\Battle Engine Aquila\\savegames\\haha-cannon-goes-brrrrr.bes",
  fileName: "haha-cannon-goes-brrrrr.bes",
  fileSize: 10004,
  sha256: "browser-fixture-save-hash",
  inspectedAt: new Date().toISOString(),
  isValid: true,
  isOptionsFile: false,
  versionWordHex: "0x4BD1",
  versionValid: true,
  counts: {
    completedNodes: 43,
    partialNodes: 0,
    emptyNodes: 57,
    completedLinks: 70,
    totalLinks: 70,
    activeTechSlots: 12,
    totalTechSlots: 32
  },
  goodies: {
    displayableUnlocked: 233,
    new: 0,
    old: 233,
    locked: 0,
    instructions: 0,
    other: 0,
    reserved: 67
  },
  goodieRows: browserGoodieRows,
  kills: [
    { categoryIndex: 0, categoryName: "Aircraft", kills: 100, meta: 0, nextUnlockThreshold: null },
    { categoryIndex: 1, categoryName: "Vehicles", kills: 400, meta: 0, nextUnlockThreshold: null },
    { categoryIndex: 2, categoryName: "Emplacements", kills: 75, meta: 0, nextUnlockThreshold: null },
    { categoryIndex: 3, categoryName: "Infantry", kills: 160, meta: 0, nextUnlockThreshold: null },
    { categoryIndex: 4, categoryName: "Mechs", kills: 80, meta: 0, nextUnlockThreshold: null }
  ],
  rankDistribution: [
    { rank: "S", count: 43 }
  ],
  completedNodeSamples: [
    { index: 0, world: 1, rank: "S", rankBitsHex: "0x3F800000" },
    { index: 1, world: 1, rank: "S", rankBitsHex: "0x3F800000" },
    { index: 2, world: 1, rank: "S", rankBitsHex: "0x3F800000" }
  ],
  settings: {
    newGoodieCountRaw: 0,
    careerInProgress: true,
    godModeEnabled: false,
    soundVolume: 1,
    soundVolumeBitsHex: "0x3F800000",
    musicVolume: 1,
    musicVolumeBitsHex: "0x3F800000",
    walkerInvertY: [false, false],
    flightInvertY: [false, false],
    vibration: [true, true],
    controllerConfig: [0, 0]
  },
  options: {
    entryCount: 16,
    tailStartHex: "0x26BE",
    mouseSensitivity: 1,
    mouseSensitivityBitsHex: "0x3F800000",
    controlSchemeIndex: 0,
    languageIndex: 0,
    screenShape: 0,
    d3dDeviceIndex: 0,
    bindingSlotLabels: ["P1", "P2"],
    bindings: [
      {
        entryId: 0x1f,
        entryIdHex: "0x1F",
        actionName: "Movement: Forward",
        slot0: "Key W",
        slot1: "Up",
        slot0DeviceCode: 9,
        slot0PackedKeyHex: "0x00570011",
        slot1DeviceCode: 9,
        slot1PackedKeyHex: "0x000000C8"
      },
      {
        entryId: 0x20,
        entryIdHex: "0x20",
        actionName: "Movement: Backward",
        slot0: "Key S",
        slot1: "Down",
        slot0DeviceCode: 9,
        slot0PackedKeyHex: "0x0053001F",
        slot1DeviceCode: 9,
        slot1PackedKeyHex: "0x000000D0"
      },
      {
        entryId: 0x12,
        entryIdHex: "0x12",
        actionName: "Others: Fire weapon (A)",
        slot0: "MouseLeft",
        slot1: "RControl",
        slot0DeviceCode: 17,
        slot0PackedKeyHex: "0x00000000",
        slot1DeviceCode: 9,
        slot1PackedKeyHex: "0x0000009D"
      }
    ]
  },
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "save-inspection.v1",
    jobId: "browser-save-fixture",
    artifactPath: "browser://fixture/save-inspection/browser-save-fixture/inspection.json",
    note: "Preview mode only. Desktop app mode computes this from the selected save/options file."
  }
};

export const browserSaveComparison: SaveComparisonSummary = {
  leftPath: "C:\\Games\\Battle Engine Aquila\\savegames\\haha-cannon-goes-brrrrr.bes",
  rightPath: "C:\\Games\\Battle Engine Aquila\\savegames\\haha-cannon-goes-brrrrr.bes",
  leftFileName: "haha-cannon-goes-brrrrr.bes",
  rightFileName: "haha-cannon-goes-brrrrr.bes",
  leftFileSize: 10004,
  rightFileSize: 10004,
  leftSha256: "browser-fixture-save-hash",
  rightSha256: "browser-fixture-save-hash",
  comparedAt: new Date().toISOString(),
  sameSize: true,
  differingBytes: 0,
  identical: true,
  topRegions: [],
  diffRanges: [],
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "save-comparison.v1",
    jobId: "browser-save-compare-fixture",
    artifactPath: "browser://fixture/save-comparison/browser-save-compare-fixture/comparison.json",
    note: "Preview mode only. Desktop app mode computes this from the selected save/options files."
  }
};

export const browserHexRead: HexReadSummary = {
  selectedPath: "C:\\Games\\Battle Engine Aquila\\BEA.exe",
  fileName: "BEA.exe",
  fileSize: 2506752,
  sha256: "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
  readAt: new Date().toISOString(),
  offset: 0x129696,
  offsetHex: "0x129696",
  requestedLength: 64,
  byteLength: 64,
  truncated: false,
  rows: [
    {
      offset: 0x129696,
      offsetHex: "0x129696",
      hex: "CC 8B 4D F8 83 C1 04 89 4D F8 8B 55 F8 8B 02 89",
      ascii: "..M.....M..U...."
    },
    {
      offset: 0x1296a6,
      offsetHex: "0x1296A6",
      hex: "45 F0 8B 4D F8 8B 55 EC 8B 02 3B 45 F0 74 10 8B",
      ascii: "E..M..U...;E.t.."
    },
    {
      offset: 0x1296b6,
      offsetHex: "0x1296B6",
      hex: "4D F8 8B 55 F0 89 11 E9 6E FF FF FF 8B 45 F8 8B",
      ascii: "M..U....n....E.."
    },
    {
      offset: 0x1296c6,
      offsetHex: "0x1296C6",
      hex: "4D F8 83 C0 04 89 45 F8 8B 55 F8 8B 02 85 C0 75",
      ascii: "M.....E..U.....u"
    }
  ],
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "hex-read.v1",
    jobId: "browser-hex-fixture",
    artifactPath: "browser://fixture/hex-read/browser-hex-fixture/hex-read.json",
    note: "Preview mode only. Desktop app mode reads a bounded byte window from the selected file."
  }
};

export const browserAddressConversion: AddressConversionSummary = {
  executablePath: "C:\\Games\\Battle Engine Aquila\\BEA.exe",
  fileName: "BEA.exe",
  fileSize: 2506752,
  sha256: "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
  convertedAt: new Date().toISOString(),
  imageBaseHex: "0x400000",
  virtualAddressHex: "0x529696",
  rvaHex: "0x129696",
  fileOffsetHex: "0x129696",
  fileOffset: 0x129696,
  section: {
    name: ".text",
    virtualAddressHex: "0x1000",
    virtualSizeHex: "0x1D8000",
    rawPointerHex: "0x1000",
    rawSizeHex: "0x1D8000"
  },
  shortcutTextVaMinusImageBase: true,
  note: "Preview mode conversion. Desktop app mode parses the selected PE headers."
};

export const browserGhidraReadiness: GhidraReadinessSummary = {
  checkedAt: new Date().toISOString(),
  repoRoot: "C:\\Projects\\OnslaughtToolkit",
  configuredInstallPath: "D:\\ghidra_12.0.3_PUBLIC_20260210\\ghidra_12.0.3_PUBLIC",
  configuredProjectRoot: "C:\\Ghidra",
  configuredMcpBundlePath: "D:\\GhydraMCP-Complete-v2.2.0-rc.2-20260211-083952",
  paths: [
    {
      label: "Ghidra install",
      path: "D:\\ghidra_12.0.3_PUBLIC_20260210\\ghidra_12.0.3_PUBLIC",
      exists: true,
      kind: "directory",
      role: "Pinned local Ghidra client root."
    },
    {
      label: "Headless postscript runner",
      path: "tools\\run_ghidra_headless_postscript.sh",
      exists: true,
      kind: "file",
      role: "Preferred Java postscript execution wrapper."
    },
    {
      label: "ExportWeakFunctionList.java",
      path: "tools\\ExportWeakFunctionList.java",
      exists: true,
      kind: "file",
      role: "Read-only Ghidra evidence script."
    }
  ],
  commands: [
    {
      label: "Export weak function list",
      command: "tools/run_ghidra_headless_postscript.sh ExportWeakFunctionList.java <out_path> all",
      mutation: false,
      status: "ready",
      detail: "Read-only inventory job for function coverage and naming queues."
    },
    {
      label: "Apply batch rename map",
      command: "tools/run_ghidra_batch_rename_headless.sh <map> apply",
      mutation: true,
      status: "blocked",
      detail: "Blocked until dry-run success and explicit arming."
    }
  ],
  readOnlyScripts: ["ExportWeakFunctionList.java", "ExportFunctionsByAddressDecompile.java", "ExportXrefsForAddresses.java"],
  mutationScripts: ["GhidraBatchRename.java", "CreateFunctionsFromAddressList.java"],
  ready: true,
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "ghidra-readiness.v1",
    note: "Preview mode only. Desktop app mode checks local paths without launching Ghidra."
  }
};

export const browserDebugReadiness: DebugReadinessSummary = {
  checkedAt: new Date().toISOString(),
  repoRoot: "C:\\Projects\\OnslaughtToolkit",
  paths: [
    {
      label: "CDB path resolver",
      path: "tools\\get_cdb_path.ps1",
      exists: true,
      kind: "file",
      role: "Find installed cdb.exe."
    },
    {
      label: "CDB server launcher",
      path: "tools\\start_cdb_server.ps1",
      exists: true,
      kind: "file",
      role: "Start a CDB server attached to a running process."
    },
    {
      label: "CDB client connector",
      path: "tools\\connect_cdb_client.ps1",
      exists: true,
      kind: "file",
      role: "Attach a CDB client."
    }
  ],
  probeScripts: [
    {
      label: "maladim-wave1.cdb.txt",
      path: "tools\\runtime-probes\\maladim-wave1.cdb.txt",
      exists: true,
      kind: "file",
      role: "Canned runtime probe command file."
    }
  ],
  commands: [
    {
      label: "Resolve debugger",
      command: "powershell -ExecutionPolicy Bypass -File tools/get_cdb_path.ps1",
      mutation: false,
      status: "ready",
      detail: "Read-only check for Windows debugger tools."
    },
    {
      label: "Start debug server",
      command: "powershell -ExecutionPolicy Bypass -File tools/start_cdb_server.ps1 -ProcessName BEA.exe -CommandFile <probe>",
      mutation: false,
      status: "ready",
      detail: "Runtime attach job for an already-running BEA.exe; future UI must arm it explicitly."
    }
  ],
  ready: true,
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "debug-readiness.v1",
    note: "Preview mode only. Desktop app mode checks debugger scripts without launching anything."
  }
};

export const browserGameHarnessProfile: GameHarnessProfileSummary = {
  checkedAt: new Date().toISOString(),
  repoRoot: "C:\\Projects\\OnslaughtToolkit",
  gameRoot: "C:\\Games\\Battle Engine Aquila",
  profileSource: "stored",
  configPath: "browser://fixture/onslaught-workbench-settings.json",
  executablePath: "C:\\Games\\Battle Engine Aquila\\BEA.exe",
  workingDirectory: "C:\\Games\\Battle Engine Aquila",
  recommendedArgs: [],
  files: [
    {
      label: "BEA.exe",
      path: "game\\BEA.exe",
      exists: true,
      required: true,
      role: "Executable specimen for launch and patch verification."
    },
    {
      label: "data/",
      path: "game\\data",
      exists: true,
      required: true,
      role: "Retail data directory."
    },
    {
      label: "defaultoptions.bea",
      path: "game\\defaultoptions.bea",
      exists: true,
      required: true,
      role: "Boot options source."
    }
  ],
  launchPlan: {
    label: "Launch verified game profile",
    command: "Start-Process -FilePath <game>\\BEA.exe -WorkingDirectory <game>",
    mutation: false,
    status: "ready",
    detail: "Planned launch command only. Preview mode does not start the game."
  },
  ready: true,
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "game-harness-profile.v1",
    note: "Preview mode only. Desktop app mode checks the local game folder."
  }
};

export const browserJobCatalog: WorkbenchJobCatalogSummary = {
  generatedAt: new Date().toISOString(),
  repoRoot: "C:\\Projects\\OnslaughtToolkit",
  definitions: [
    {
      id: "file.hexRead",
      lane: "file",
      title: "Read bounded hex window",
      safety: "read-only",
      status: "available",
      detail: "Read up to 4 KiB from a selected local file and write a compact JSON artifact.",
      artifactSchema: "hex-read.v1",
      policy: { timeoutMs: 10_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "path", label: "File path", required: true, detail: "Local file selected by dialog or typed path." },
        { name: "offset", label: "Offset", required: true, detail: "Decimal or 0x-prefixed byte offset." }
      ]
    },
    {
      id: "file.peAddressConvert",
      lane: "file",
      title: "Convert PE virtual address",
      safety: "read-only",
      status: "available",
      detail: "Parse PE section headers and map a BEA.exe virtual address to a file offset.",
      artifactSchema: "address-conversion.v1",
      policy: { timeoutMs: 10_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "executablePath", label: "BEA.exe path", required: true, detail: "Executable to parse." },
        { name: "virtualAddress", label: "Virtual address", required: true, detail: "Decimal or 0x-prefixed VA." }
      ]
    },
    {
      id: "save.prepareCopy",
      lane: "save",
      title: "Copy save/options into workspace",
      safety: "mutation-gated",
      status: "available",
      detail: "Copy a valid .bes/.bea/defaultoptions file into the app artifact root, verify read-back bytes, and use the copied path for later apply/restore jobs.",
      artifactSchema: "save-copy.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "sourcePath", label: "Source save/options path", required: true, detail: "The original source is read only; the copy is created under app userData artifacts." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be COPY SAVE FILE." },
        { name: "acceptsLocalCopy", label: "Local copy acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "save.planPatch",
      lane: "save",
      title: "Plan save patch with TypeScript",
      safety: "read-only",
      status: "available",
      detail: "Use the native TypeScript patcher to validate a save/options patch intent and write a source-preserving plan artifact without invoking C#.",
      artifactSchema: "save-patch-plan.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "path", label: "Save/options path", required: true, detail: ".bes career save, .bea options file, or defaultoptions.bea backup. The source file is not modified." },
        { name: "rank", label: "Rank", required: false, detail: "Default mission rank intent for a future copied target." },
        { name: "kills", label: "Kill count", required: false, detail: "Default kill count per category intent for a future copied target." },
        { name: "levelRanks", label: "Level ranks", required: false, detail: "Optional NODE_INDEX:RANK tokens, such as 1:S 2:A." },
        { name: "perCategoryKills", label: "Per-category kills", required: false, detail: "Optional category:kills tokens, such as aircraft:100 mechs:20." }
      ]
    },
    {
      id: "save.previewPatch",
      lane: "save",
      title: "Preview save patch with TypeScript",
      safety: "read-only",
      status: "available",
      detail: "Apply the native TypeScript patcher only to an artifact-owned candidate copy, compare it to the source, and keep the source file unchanged.",
      artifactSchema: "save-patch-preview.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "path", label: "Save/options path", required: true, detail: ".bes career save, .bea options file, or defaultoptions.bea backup. The source file is not modified." },
        { name: "rank", label: "Rank", required: false, detail: "Default mission rank for the candidate copy." },
        { name: "kills", label: "Kill count", required: false, detail: "Default kill count per category for the candidate copy." },
        { name: "levelRanks", label: "Level ranks", required: false, detail: "Optional NODE_INDEX:RANK tokens, such as 1:S 2:A." },
        { name: "perCategoryKills", label: "Per-category kills", required: false, detail: "Optional category:kills tokens, such as aircraft:100 mechs:20." }
      ]
    },
    {
      id: "save.applyPatch",
      lane: "save",
      title: "Apply save patch to copied file",
      safety: "mutation-gated",
      status: "available",
      detail: "Apply the native TypeScript patcher only to a save/options file inside the app artifact/profile root, after writing a backup and verifying read-back bytes.",
      artifactSchema: "save-patch-apply.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "path", label: "Copied save/options path", required: true, detail: "Must be inside the app artifact/profile root. Repo-local saves are rejected." },
        { name: "rank", label: "Rank", required: false, detail: "Default mission rank for the copied target." },
        { name: "kills", label: "Kill count", required: false, detail: "Default kill count per category for the copied target." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be APPLY SAVE PATCH." },
        { name: "acceptsSaveWrite", label: "Copied-save write acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "save.restoreBackup",
      lane: "save",
      title: "Restore copied save backup",
      safety: "mutation-gated",
      status: "available",
      detail: "Restore a backup created under the app artifact root back to an artifact-root copied save/options file, retaining a pre-restore backup.",
      artifactSchema: "save-patch-restore.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "targetPath", label: "Copied save/options path", required: true, detail: "Must be inside the app artifact/profile root." },
        { name: "backupPath", label: "Backup path", required: true, detail: "Must be inside the app artifact/profile root." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be RESTORE SAVE BACKUP." },
        { name: "acceptsSaveWrite", label: "Copied-save write acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "settings.planOptionsPatch",
      lane: "save",
      title: "Plan global options patch with TypeScript",
      safety: "read-only",
      status: "available",
      detail: "Validate a defaultoptions.bea/.bea settings and keybind patch intent using the native TypeScript patcher without invoking C#.",
      artifactSchema: "options-patch-plan.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "path", label: "Options path", required: true, detail: ".bea or defaultoptions.bea target. The source file is not modified." },
        { name: "soundVolume", label: "Sound volume", required: false, detail: "Optional 0.0-1.0 float." },
        { name: "musicVolume", label: "Music volume", required: false, detail: "Optional 0.0-1.0 float." },
        { name: "invertWalkerP1", label: "Walker invert P1", required: false, detail: "Optional true/false override." },
        { name: "invertWalkerP2", label: "Walker invert P2", required: false, detail: "Optional true/false override." },
        { name: "invertFlightP1", label: "Flight invert P1", required: false, detail: "Optional true/false override." },
        { name: "invertFlightP2", label: "Flight invert P2", required: false, detail: "Optional true/false override." },
        { name: "vibrationP1", label: "Vibration P1", required: false, detail: "Optional true/false override." },
        { name: "vibrationP2", label: "Vibration P2", required: false, detail: "Optional true/false override." },
        { name: "controllerConfigP1", label: "Controller config P1", required: false, detail: "Optional uint32 controller config." },
        { name: "controllerConfigP2", label: "Controller config P2", required: false, detail: "Optional uint32 controller config." },
        { name: "mouseSensitivity", label: "Mouse sensitivity", required: false, detail: "Optional finite float from 0 to 10." },
        { name: "controlSchemeIndex", label: "Control scheme", required: false, detail: "Optional uint16 options-tail override." },
        { name: "languageIndex", label: "Language index", required: false, detail: "Optional uint16 options-tail override." },
        { name: "screenShape", label: "Screen shape", required: false, detail: "Optional uint32 options-tail override." },
        { name: "d3dDeviceIndex", label: "D3D device", required: false, detail: "Optional uint32 options-tail override." },
        { name: "keybindOverrides", label: "Keybind overrides", required: false, detail: "Rows like move-forward=W,Up;fire-weapon=MouseLeft,RControl." },
        { name: "copyOptionsFromPath", label: "Copy options from", required: false, detail: "Optional .bes/.bea/defaultoptions source for entries and/or tail." },
        { name: "copyOptionsEntries", label: "Copy options entries", required: false, detail: "When copyOptionsFromPath is set, copy the options-entry table." },
        { name: "copyOptionsTail", label: "Copy options tail", required: false, detail: "When copyOptionsFromPath is set, copy the 0x56-byte options tail." }
      ]
    },
    {
      id: "settings.previewOptionsPatch",
      lane: "save",
      title: "Preview global options patch with TypeScript",
      safety: "read-only",
      status: "available",
      detail: "Apply the native TypeScript settings/keybind patch only to an artifact-owned candidate copy and keep the source unchanged.",
      artifactSchema: "options-patch-preview.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "path", label: "Options path", required: true, detail: ".bea or defaultoptions.bea target. The source file is not modified." },
        { name: "soundVolume", label: "Sound volume", required: false, detail: "Optional 0.0-1.0 float." },
        { name: "musicVolume", label: "Music volume", required: false, detail: "Optional 0.0-1.0 float." },
        { name: "invertWalkerP1", label: "Walker invert P1", required: false, detail: "Optional true/false override." },
        { name: "invertWalkerP2", label: "Walker invert P2", required: false, detail: "Optional true/false override." },
        { name: "invertFlightP1", label: "Flight invert P1", required: false, detail: "Optional true/false override." },
        { name: "invertFlightP2", label: "Flight invert P2", required: false, detail: "Optional true/false override." },
        { name: "vibrationP1", label: "Vibration P1", required: false, detail: "Optional true/false override." },
        { name: "vibrationP2", label: "Vibration P2", required: false, detail: "Optional true/false override." },
        { name: "controllerConfigP1", label: "Controller config P1", required: false, detail: "Optional uint32 controller config." },
        { name: "controllerConfigP2", label: "Controller config P2", required: false, detail: "Optional uint32 controller config." },
        { name: "mouseSensitivity", label: "Mouse sensitivity", required: false, detail: "Optional finite float from 0 to 10." },
        { name: "controlSchemeIndex", label: "Control scheme", required: false, detail: "Optional uint16 options-tail override." },
        { name: "languageIndex", label: "Language index", required: false, detail: "Optional uint16 options-tail override." },
        { name: "screenShape", label: "Screen shape", required: false, detail: "Optional uint32 options-tail override." },
        { name: "d3dDeviceIndex", label: "D3D device", required: false, detail: "Optional uint32 options-tail override." },
        { name: "keybindOverrides", label: "Keybind overrides", required: false, detail: "Rows like move-forward=W,Up;fire-weapon=MouseLeft,RControl." },
        { name: "copyOptionsFromPath", label: "Copy options from", required: false, detail: "Optional .bes/.bea/defaultoptions source for entries and/or tail." },
        { name: "copyOptionsEntries", label: "Copy options entries", required: false, detail: "When copyOptionsFromPath is set, copy the options-entry table." },
        { name: "copyOptionsTail", label: "Copy options tail", required: false, detail: "When copyOptionsFromPath is set, copy the 0x56-byte options tail." }
      ]
    },
    {
      id: "settings.applyOptionsPatch",
      lane: "save",
      title: "Apply global options patch to copied file",
      safety: "mutation-gated",
      status: "available",
      detail: "Apply settings/keybind changes only to a .bea/defaultoptions file inside the app artifact/profile root after backup and read-back verification.",
      artifactSchema: "options-patch-apply.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "path", label: "Copied options path", required: true, detail: "Must be inside the app artifact/profile root." },
        { name: "soundVolume", label: "Sound volume", required: false, detail: "Optional 0.0-1.0 float." },
        { name: "musicVolume", label: "Music volume", required: false, detail: "Optional 0.0-1.0 float." },
        { name: "invertWalkerP1", label: "Walker invert P1", required: false, detail: "Optional true/false override." },
        { name: "invertWalkerP2", label: "Walker invert P2", required: false, detail: "Optional true/false override." },
        { name: "invertFlightP1", label: "Flight invert P1", required: false, detail: "Optional true/false override." },
        { name: "invertFlightP2", label: "Flight invert P2", required: false, detail: "Optional true/false override." },
        { name: "vibrationP1", label: "Vibration P1", required: false, detail: "Optional true/false override." },
        { name: "vibrationP2", label: "Vibration P2", required: false, detail: "Optional true/false override." },
        { name: "controllerConfigP1", label: "Controller config P1", required: false, detail: "Optional uint32 controller config." },
        { name: "controllerConfigP2", label: "Controller config P2", required: false, detail: "Optional uint32 controller config." },
        { name: "mouseSensitivity", label: "Mouse sensitivity", required: false, detail: "Optional finite float from 0 to 10." },
        { name: "controlSchemeIndex", label: "Control scheme", required: false, detail: "Optional uint16 options-tail override." },
        { name: "languageIndex", label: "Language index", required: false, detail: "Optional uint16 options-tail override." },
        { name: "screenShape", label: "Screen shape", required: false, detail: "Optional uint32 options-tail override." },
        { name: "d3dDeviceIndex", label: "D3D device", required: false, detail: "Optional uint32 options-tail override." },
        { name: "keybindOverrides", label: "Keybind overrides", required: false, detail: "Rows like move-forward=W,Up;fire-weapon=MouseLeft,RControl." },
        { name: "copyOptionsFromPath", label: "Copy options from", required: false, detail: "Optional .bes/.bea/defaultoptions source for entries and/or tail." },
        { name: "copyOptionsEntries", label: "Copy options entries", required: false, detail: "When copyOptionsFromPath is set, copy the options-entry table." },
        { name: "copyOptionsTail", label: "Copy options tail", required: false, detail: "When copyOptionsFromPath is set, copy the 0x56-byte options tail." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be APPLY OPTIONS PATCH." },
        { name: "acceptsOptionsWrite", label: "Copied-options write acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "appcore.inspectSave",
      lane: "appcore",
      title: "Parity diagnostic: inspect save with AppCore host",
      safety: "read-only",
      status: "available",
      detail: "Hidden-by-default C# parity diagnostic. Run the AppCore JSON host against a .bes/.bea file and preserve the typed read-only payload.",
      commandPreview: "dotnet run --project OnslaughtCareerEditor.AppCore.Host -- inspect-save <path>",
      artifactSchema: "appcore-save-analysis.v1",
      policy: { timeoutMs: 120_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "path", label: "Save/options path", required: true, detail: ".bes career save, .bea options file, or defaultoptions.bea backup." }
      ]
    },
    {
      id: "appcore.compareSaves",
      lane: "appcore",
      title: "Parity diagnostic: compare saves with AppCore host",
      safety: "read-only",
      status: "available",
      detail: "Hidden-by-default C# parity diagnostic. Run the AppCore JSON host comparison against two .bes/.bea files and preserve the typed read-only payload.",
      commandPreview: "dotnet run --project OnslaughtCareerEditor.AppCore.Host -- compare-saves <left> <right>",
      artifactSchema: "appcore-save-comparison.v1",
      policy: { timeoutMs: 120_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "leftPath", label: "Left save/options path", required: true, detail: ".bes career save, .bea options file, or defaultoptions.bea backup." },
        { name: "rightPath", label: "Right save/options path", required: true, detail: ".bes career save, .bea options file, or defaultoptions.bea backup." }
      ]
    },
    {
      id: "appcore.planSavePatch",
      lane: "appcore",
      title: "Parity diagnostic: plan save patch with AppCore host",
      safety: "read-only",
      status: "available",
      detail: "Hidden-by-default C# parity diagnostic. Write an explicit appcore-save-patch-request.v1 JSON intent, validate it through the AppCore host, and preserve a read-only patch plan.",
      commandPreview: "dotnet run --project OnslaughtCareerEditor.AppCore.Host -- plan-save-patch <request.json>",
      artifactSchema: "appcore-save-patch-plan.v1",
      policy: { timeoutMs: 120_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "path", label: "Save/options path", required: true, detail: ".bes career save, .bea options file, or defaultoptions.bea backup. The source file is not modified." },
        { name: "rank", label: "Rank", required: false, detail: "Default mission rank intent for a future copied target." },
        { name: "kills", label: "Kill count", required: false, detail: "Default kill count per category intent for a future copied target." },
        { name: "levelRanks", label: "Level ranks", required: false, detail: "Optional NODE_INDEX:RANK tokens, such as 1:S 2:A." },
        { name: "perCategoryKills", label: "Per-category kills", required: false, detail: "Optional category:kills tokens, such as aircraft:100 mechs:20." }
      ]
    },
    {
      id: "appcore.previewSavePatch",
      lane: "appcore",
      title: "Parity diagnostic: preview save patch with AppCore host",
      safety: "read-only",
      status: "available",
      detail: "Hidden-by-default C# parity diagnostic. Patch only a temporary copy through the AppCore host, compare it back to the source, delete the temp copy, and preserve the read-only preview payload.",
      commandPreview: "dotnet run --project OnslaughtCareerEditor.AppCore.Host -- preview-save-patch <path> --rank S --kills 100",
      artifactSchema: "appcore-save-patch-preview.v1",
      policy: { timeoutMs: 120_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "path", label: "Save/options path", required: true, detail: ".bes career save, .bea options file, or defaultoptions.bea backup. The source file is not modified." },
        { name: "rank", label: "Rank", required: false, detail: "Default mission rank for the temporary patched copy." },
        { name: "kills", label: "Kill count", required: false, detail: "Default kill count per category for the temporary patched copy." }
      ]
    },
    {
      id: "patch.verifySpecimen",
      lane: "patch",
      title: "Verify patch catalog state",
      safety: "read-only",
      status: "available",
      detail: "Hash BEA.exe, classify every curated patch row, and write specimen verification evidence.",
      artifactSchema: "specimen-verification.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "executablePath", label: "BEA.exe path", required: true, detail: "Target executable specimen." }
      ]
    },
    {
      id: "patch.planCatalogPatch",
      lane: "patch",
      title: "Plan stable patch set",
      safety: "read-only",
      status: "available",
      detail: "Verify current bytes and write a read-only apply plan for the stable curated patch set.",
      artifactSchema: "patch-plan.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "executablePath", label: "BEA.exe path", required: true, detail: "Target executable specimen." },
        { name: "patchIds", label: "Patch IDs", required: false, detail: "Use stable by default; all includes experimental rows." }
      ]
    },
    {
      id: "patch.prepareExecutableCopy",
      lane: "patch",
      title: "Copy BEA.exe into workspace",
      safety: "mutation-gated",
      status: "available",
      detail: "Copy a verified BEA.exe into the app artifact root so catalog patch apply/restore never writes the original executable.",
      artifactSchema: "patch-executable-copy.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "sourcePath", label: "Source BEA.exe path", required: true, detail: "Original executable to copy." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be COPY BEA EXE." },
        { name: "acceptsLocalCopy", label: "Local copy acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "patch.applyCatalogPatch",
      lane: "patch",
      title: "Apply curated catalog patch",
      safety: "mutation-gated",
      status: "available",
      detail: "Apply curated patch bytes only to an artifact-root copied BEA.exe after byte preimage checks, backup, and post-write verification.",
      artifactSchema: "patch-apply.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "executablePath", label: "Copied BEA.exe path", required: true, detail: "Must be inside the app artifact/profile root. Repo-local BEA.exe is rejected." },
        { name: "patchIds", label: "Patch IDs", required: false, detail: "Use stable by default; all includes experimental rows." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be APPLY CATALOG PATCH." },
        { name: "acceptsExecutableWrite", label: "Executable write acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "patch.restoreCatalogBackup",
      lane: "patch",
      title: "Restore copied executable backup",
      safety: "mutation-gated",
      status: "available",
      detail: "Restore an artifact-root BEA.exe backup to an artifact-root copied executable and retain a pre-restore backup.",
      artifactSchema: "patch-restore.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "targetPath", label: "Copied BEA.exe path", required: true, detail: "Must be inside the app artifact/profile root." },
        { name: "backupPath", label: "Backup path", required: true, detail: "Must be inside the app artifact/profile root." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be RESTORE CATALOG BACKUP." },
        { name: "acceptsExecutableWrite", label: "Executable write acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "release.inspectPolicy",
      lane: "release",
      title: "Inspect release policy",
      safety: "read-only",
      status: "available",
      detail: "Classify community-safe content rows and private/source-tree release boundaries without packaging files.",
      artifactSchema: "release-policy.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: []
    },
    {
      id: "ghidra.exportWeakFunctions",
      lane: "ghidra",
      title: "Export weak function list",
      safety: "read-only",
      status: "available",
      detail: "Run the read-only weak-function inventory script through the headless postscript runner.",
      commandPreview: "tools/run_ghidra_headless_postscript.sh ExportWeakFunctionList.java <artifact_tsv> weak",
      artifactSchema: "ghidra-export.v1",
      policy: { timeoutMs: 600_000, cancellable: true, externalProcess: true },
      inputs: [
        { name: "mode", label: "Mode", required: false, detail: "Use weak by default; all exports every function." }
      ]
    },
    {
      id: "ghidra.exportAddressDecompile",
      lane: "ghidra",
      title: "Export decompile for addresses",
      safety: "read-only",
      status: "available",
      detail: "Run a read-only decompile/export pass for structured address tokens written under the artifact root.",
      commandPreview:
        "tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java <artifact_addresses> <artifact_out_dir>",
      artifactSchema: "ghidra-decompile-export.v1",
      policy: { timeoutMs: 600_000, cancellable: true, externalProcess: true },
      inputs: [
        { name: "addresses", label: "Addresses", required: false, detail: "0x-prefixed or hex address tokens." }
      ]
    },
    {
      id: "ghidra.validateRenameMap",
      lane: "ghidra",
      title: "Dry-run Ghidra rename map",
      safety: "read-only",
      status: "available",
      detail: "Run the allowlisted headless rename helper in dry mode against an artifact-root two-column rename map.",
      commandPreview: "tools/run_ghidra_batch_rename_headless.sh <map> dry",
      artifactSchema: "ghidra-rename-dry-run.v1",
      policy: { timeoutMs: 600_000, cancellable: true, externalProcess: true },
      inputs: [
        { name: "mapPath", label: "Rename map", required: true, detail: "Two-column address/name map inside the app artifact root." }
      ]
    },
    {
      id: "ghidra.applyRenameMap",
      lane: "ghidra",
      title: "Apply Ghidra rename map",
      safety: "mutation-gated",
      status: "available",
      detail: "Apply an artifact-root rename map only after a successful dry-run artifact and explicit arming.",
      commandPreview: "tools/run_ghidra_batch_rename_headless.sh <map> apply",
      artifactSchema: "ghidra-mutation.v1",
      policy: { timeoutMs: 600_000, cancellable: true, externalProcess: true },
      inputs: [
        { name: "mapPath", label: "Rename map", required: true, detail: "Two-column address/name map inside the app artifact root." },
        { name: "dryRunArtifactPath", label: "Dry-run artifact", required: true, detail: "A successful ghidra-rename-dry-run.v1 artifact for the same map." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be APPLY GHIDRA RENAME MAP." },
        { name: "acceptsGhidraMutation", label: "Ghidra mutation acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "debug.startProbeServer",
      lane: "debugger",
      title: "Attach CDB probe server",
      safety: "launch-gated",
      status: "available",
      detail: "Starts CDB and attaches to a running BEA.exe with an allowlisted command file only after visible arming and a copied/safe game profile check.",
      commandPreview:
        "powershell -ExecutionPolicy Bypass -File tools/start_cdb_server.ps1 -ProcessName BEA.exe -CommandFile <probe>",
      artifactSchema: "debug-session.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "processName", label: "Process name", required: false, detail: "Defaults to BEA.exe." },
        { name: "probeId", label: "Probe script", required: true, detail: "Allowlisted script from tools/runtime-probes." },
        { name: "gameRoot", label: "Game root", required: true, detail: "Copied/safe game profile outside the repo root." },
        { name: "port", label: "Port", required: false, detail: "Local CDB server port, default 5005." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be ATTACH CDB." },
        { name: "acceptsRuntimeAttach", label: "Runtime attach acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "runtime.listManagedProcesses",
      lane: "runtime",
      title: "List managed runtime processes",
      safety: "read-only",
      status: "available",
      detail: "Read the workbench-owned process registry for game/CDB processes launched through typed jobs.",
      artifactSchema: "managed-process-registry.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: []
    },
    {
      id: "runtime.tailManagedLog",
      lane: "runtime",
      title: "Read managed runtime log tail",
      safety: "read-only",
      status: "available",
      detail: "Read a bounded tail from a managed game/CDB log path recorded by typed jobs.",
      artifactSchema: "managed-process-log-tail.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed job run id; defaults to latest recorded log path." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded PID when no run id is supplied." },
        { name: "byteLimit", label: "Tail bytes", required: false, detail: "Optional byte cap from 256 to 65536; defaults to 8192." }
      ]
    },
    {
      id: "runtime.stopManagedProcess",
      lane: "runtime",
      title: "Stop managed runtime process",
      safety: "launch-gated",
      status: "available",
      detail: "Stops only a PID previously recorded by this workbench after a game launch or CDB attach job.",
      artifactSchema: "managed-process-stop.v1",
      policy: { timeoutMs: 10_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional job run id; defaults to latest running managed process." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded PID when no run id is supplied." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be STOP PROCESS." },
        { name: "acceptsProcessStop", label: "Process stop acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "debug.resolveCdb",
      lane: "debugger",
      title: "Resolve CDB path",
      safety: "read-only",
      status: "available",
      detail: "Run the repo helper that finds the installed x86 cdb.exe path.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/get_cdb_path.ps1",
      artifactSchema: "debug-cdb-resolve.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: true },
      inputs: []
    },
    {
      id: "debug.planProbeSession",
      lane: "debugger",
      title: "Plan CDB probe session",
      safety: "read-only",
      status: "available",
      detail: "Validate the game profile and an allowlisted runtime-probe command file, then write a non-launching CDB attach-session plan.",
      commandPreview:
        "powershell -ExecutionPolicy Bypass -File tools/start_cdb_server.ps1 -ProcessName BEA.exe -CommandFile <allowlisted_probe> -PrintOnly",
      artifactSchema: "debug-probe-plan.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "probeId", label: "Probe script", required: false, detail: "Allowlisted script from tools/runtime-probes." },
        { name: "port", label: "Port", required: false, detail: "Local CDB server port, default 5005." }
      ]
    },
    {
      id: "assets.catalogGameFiles",
      lane: "assets",
      title: "Catalog game assets",
      safety: "read-only",
      status: "available",
      detail: "Rebuild the cross-surface asset catalog from existing exported manifests into the artifact root.",
      artifactSchema: "asset-catalog.v1",
      policy: { timeoutMs: 600_000, cancellable: true, externalProcess: true },
      inputs: []
    },
    {
      id: "game.inventoryProfile",
      lane: "game",
      title: "Inventory game harness profile",
      safety: "read-only",
      status: "available",
      detail: "Check the local game directory for BEA.exe, options, data, and runtime DLLs.",
      artifactSchema: "game-harness-profile.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "gameRoot", label: "Game root", required: false, detail: "Defaults to repo-local game/ for private lane." }
      ]
    },
    {
      id: "game.planWindowCapture",
      lane: "game",
      title: "Plan game-window capture",
      safety: "read-only",
      status: "available",
      detail: "Scan for a visible BEA.exe window owned by a managed game launch and write a read-only capture/input plan.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/list_game_windows.ps1 -ProcessName BEA.exe",
      artifactSchema: "game-window-capture-plan.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID." },
        { name: "processName", label: "Process name", required: false, detail: "Restricted to BEA.exe." }
      ]
    },
    {
      id: "game.captureWindowFrame",
      lane: "game",
      title: "Capture game-window still frame",
      safety: "read-only",
      status: "available",
      detail:
        "Scan for a visible managed BEA.exe window, request one bounded desktop thumbnail, and write PNG/JSON artifacts without opening a live stream or sending input.",
      commandPreview: "desktopCapturer.getSources({ types: ['window'], thumbnailSize: { width: 960, height: 540 } })",
      artifactSchema: "game-window-frame-capture.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID." },
        { name: "processName", label: "Process name", required: false, detail: "Restricted to BEA.exe." },
        { name: "maxWidth", label: "Max width", required: false, detail: "Thumbnail width cap, default 960." },
        { name: "maxHeight", label: "Max height", required: false, detail: "Thumbnail height cap, default 540." }
      ]
    },
    {
      id: "game.captureWindowSequence",
      lane: "game",
      title: "Capture bounded frame sequence",
      safety: "read-only",
      status: "available",
      detail: "Capture a short bounded sequence of BEA window PNG frames for observe-act-observe loops without leaving a live stream open.",
      commandPreview: "desktopCapturer.getSources(...) repeated for <frameCount> bounded frames",
      artifactSchema: "game-window-frame-sequence.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID." },
        { name: "processName", label: "Process name", required: false, detail: "Restricted to BEA.exe." },
        { name: "frameCount", label: "Frame count", required: false, detail: "1-12 frames; default 3." },
        { name: "intervalMs", label: "Interval", required: false, detail: "0-5000 ms between frames; default 250." },
        { name: "maxWidth", label: "Max width", required: false, detail: "Thumbnail width cap, default 960." },
        { name: "maxHeight", label: "Max height", required: false, detail: "Thumbnail height cap, default 540." }
      ]
    },
    {
      id: "game.planWindowInput",
      lane: "game",
      title: "Plan scoped game-window input",
      safety: "read-only",
      status: "available",
      detail: "Validate a small allowlisted keyboard input sequence for a managed BEA.exe window without focusing the window or sending input.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -ProcessName BEA.exe -Sequence <allowlisted> -PrintOnly",
      artifactSchema: "game-window-input.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID." },
        { name: "hwndHex", label: "Window handle", required: false, detail: "Optional BEA.exe window handle from a capture plan." },
        { name: "sequence", label: "Input sequence", required: true, detail: "Allowlisted tap/down/up/wait actions." },
        { name: "stepDelayMs", label: "Step delay", required: false, detail: "Delay between key events, default 60 ms." }
      ]
    },
    {
      id: "game.sendWindowInput",
      lane: "game",
      title: "Send scoped game-window input",
      safety: "launch-gated",
      status: "available",
      detail: "Focus a managed BEA.exe top-level window and send only allowlisted keyboard actions after explicit arming.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -ProcessName BEA.exe -Sequence <allowlisted>",
      artifactSchema: "game-window-input.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID." },
        { name: "hwndHex", label: "Window handle", required: false, detail: "Optional BEA.exe window handle from a capture plan." },
        { name: "sequence", label: "Input sequence", required: true, detail: "Allowlisted tap/down/up/wait actions." },
        { name: "stepDelayMs", label: "Step delay", required: false, detail: "Delay between key events, default 60 ms." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be SEND GAME INPUT." },
        { name: "acceptsWindowInput", label: "Window input acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "game.planLaunchProfile",
      lane: "game",
      title: "Plan verified game launch",
      safety: "read-only",
      status: "available",
      detail: "Verify the active game profile and executable hash, then write a non-launching game launch plan.",
      commandPreview: "Start-Process -FilePath <game>\\BEA.exe -WorkingDirectory <game>",
      artifactSchema: "game-launch-plan.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "gameRoot", label: "Game root", required: false, detail: "Defaults to the active game profile." },
        { name: "args", label: "Arguments", required: false, detail: "Optional allowlisted launch arguments. Windowed mode is handled by the patch catalog." }
      ]
    },
    {
      id: "game.prepareSafeProfile",
      lane: "game",
      title: "Prepare copied game profile",
      safety: "mutation-gated",
      status: "available",
      detail: "Copy a validated local game profile into the app artifact root so launch/debug jobs can run outside the repo-local private game tree.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/prepare_game_profile.ps1 -SourceGameRoot <game> -OutputRoot <artifact_profiles>",
      artifactSchema: "game-profile-prepare.v1",
      policy: { timeoutMs: 900_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "sourceGameRoot", label: "Source game root", required: false, detail: "Defaults to the active game profile." },
        { name: "profileName", label: "Profile name", required: false, detail: "Letters, numbers, dot, underscore, and dash only." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be COPY GAME PROFILE." },
        { name: "acceptsLocalCopy", label: "Local copy acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "game.launchProfile",
      lane: "game",
      title: "Launch verified game profile",
      safety: "launch-gated",
      status: "available",
      detail: "Launch BEA.exe only after visible arming, specimen verification, and a copied/safe game profile check.",
      commandPreview: "Start-Process -FilePath <game>\\BEA.exe -WorkingDirectory <game>",
      artifactSchema: "game-launch.v1",
      policy: { timeoutMs: 30_000, cancellable: false, externalProcess: true },
      inputs: [
        { name: "gameRoot", label: "Game root", required: true, detail: "Copied/safe game profile outside the repo root." },
        { name: "args", label: "Arguments", required: false, detail: "Optional allowlisted launch arguments. Leave blank for the normal patched-profile path." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be LAUNCH BEA." },
        { name: "acceptsProfileWrites", label: "Profile write acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "content.readDocument",
      lane: "content",
      title: "Read curated document",
      safety: "read-only",
      status: "available",
      detail: "Read one allowlisted lore, save, RE, or roadmap markdown document.",
      artifactSchema: "content-document.v1",
      policy: { timeoutMs: 10_000, cancellable: false, externalProcess: false },
      inputs: [
        { name: "id", label: "Document ID", required: true, detail: "Allowlisted content document id." }
      ]
    }
  ],
  counts: {
    available: 41,
    blocked: 0,
    planned: 0,
    readOnly: 28,
    gated: 14
  },
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "job-catalog.v1",
    note: "Preview mode only. Desktop app mode builds this from local readiness checks."
  }
};

export const browserJobRun: WorkbenchJobRunSummary = {
  runId: "browser-job-fixture",
  definitionId: "content.readDocument",
  title: "Read curated document",
  lane: "content",
  safety: "read-only",
  status: "completed",
  startedAt: new Date().toISOString(),
  finishedAt: new Date().toISOString(),
  durationMs: 12,
  inputs: {
    id: "lore-book"
  },
  policy: {
    timeoutMs: 10_000,
    cancellable: false,
    externalProcess: false
  },
  progress: [
    {
      runId: "browser-job-fixture",
      definitionId: "content.readDocument",
      phase: "queued",
      percent: 5,
      message: "Preview mode accepted the job.",
      emittedAt: new Date().toISOString()
    },
    {
      runId: "browser-job-fixture",
      definitionId: "content.readDocument",
      phase: "running",
      percent: 45,
      message: "Preview mode read the curated document.",
      detail: "lore-book/BOOK.md",
      emittedAt: new Date().toISOString()
    },
    {
      runId: "browser-job-fixture",
      definitionId: "content.readDocument",
      phase: "completed",
      percent: 100,
      message: "Preview mode completed the job.",
      emittedAt: new Date().toISOString()
    }
  ],
  result: {
    summary: "Read Lore book (lore-book/BOOK.md).",
    payloadSchema: "content-document.v1",
    details: [
      { label: "Group", value: "Lore" },
      { label: "Path", value: "lore-book/BOOK.md" },
      { label: "Bytes", value: "4212" },
      { label: "Truncated", value: "no" }
    ]
  },
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "job-run.v1",
    jobId: "browser-job-fixture",
    artifactPath: "browser://fixture/job-runs/browser-job-fixture/job-run.json",
    note: "Preview mode only. Desktop app mode writes job-run artifacts under user data."
  }
};

export const browserJobRuns: WorkbenchJobRunSummary[] = [browserJobRun];

const browserContentItems: ContentIndexSummary["items"] = [
  {
    id: "lore-book",
    title: "Lore book",
    group: "Lore",
    relativePath: "lore-book/BOOK.md",
    description: "Curated preservation table of contents for community reading.",
    communitySafe: true
  },
  {
    id: "team-roster",
    title: "Team roster",
    group: "Lore",
    relativePath: "lore/team-roster.md",
    description: "Development team credits and role notes.",
    communitySafe: true
  },
  {
    id: "development-history",
    title: "Development history",
    group: "Lore",
    relativePath: "lore/development-history.md",
    description: "Project history and preservation notes.",
    communitySafe: true
  },
  {
    id: "community-preservation",
    title: "Community preservation",
    group: "Lore",
    relativePath: "lore/community-preservation.md",
    description: "Community resources, preservation context, and external references.",
    communitySafe: true
  },
  {
    id: "save-format",
    title: "Save file format",
    group: "Save Docs",
    relativePath: "reverse-engineering/save-file/save-format.md",
    description: "Retail .bes/.bea layout that matches the Save Lab inspector.",
    communitySafe: true
  },
  {
    id: "goodies-system",
    title: "Goodies system",
    group: "Save Docs",
    relativePath: "reverse-engineering/save-file/goodies-system.md",
    description: "Unlock and display-state notes for save analysis.",
    communitySafe: true
  },
  {
    id: "grade-system",
    title: "Grade system",
    group: "Save Docs",
    relativePath: "reverse-engineering/save-file/grade-system.md",
    description: "Retail rank float values and save-view gotchas.",
    communitySafe: true
  },
  {
    id: "kill-tracking",
    title: "Kill tracking",
    group: "Save Docs",
    relativePath: "reverse-engineering/save-file/kill-tracking.md",
    description: "Kill counters, packed metadata, and unlock thresholds.",
    communitySafe: true
  },
  {
    id: "cheat-codes",
    title: "Cheat codes",
    group: "RE Docs",
    relativePath: "reverse-engineering/game-mechanics/cheat-codes.md",
    description: "Decoded Steam-build cheat-code behavior and current verification status.",
    communitySafe: true
  },
  {
    id: "god-mode",
    title: "God mode",
    group: "RE Docs",
    relativePath: "reverse-engineering/game-mechanics/god-mode.md",
    description: "Steam-build Maladim behavior and current runtime evidence.",
    communitySafe: true
  },
  {
    id: "asset-extraction",
    title: "Asset extraction pipeline",
    group: "RE Docs",
    relativePath: "reverse-engineering/game-assets/extraction-pipeline.md",
    description: "Bring-your-own-assets extraction pipeline and validated coverage counts.",
    communitySafe: true
  },
  {
    id: "aya-tags",
    title: "AYA tags quick reference",
    group: "RE Docs",
    relativePath: "reverse-engineering/quick-reference/aya-tags.md",
    description: "Chunk and tag lookup for AYA resource investigation.",
    communitySafe: true
  },
  {
    id: "retail-specimen-baseline",
    title: "Retail specimen baseline",
    group: "RE Docs",
    relativePath: "reverse-engineering/binary-analysis/retail-specimen-baseline.md",
    description: "Maintainer specimen hashes, local paths, and runtime provenance.",
    communitySafe: false
  },
  {
    id: "windbg-cdb-runbook",
    title: "WinDbg CDB runbook",
    group: "RE Docs",
    relativePath: "reverse-engineering/binary-analysis/windbg-cdb-runbook.md",
    description: "Maintainer debugger setup, helper scripts, and runtime probe workflow.",
    communitySafe: false
  },
  {
    id: "ghidra-runbook",
    title: "Ghidra MCP runbook",
    group: "RE Docs",
    relativePath: "reverse-engineering/binary-analysis/ghydra-mcp-runbook.md",
    description: "Maintainer runbook for Ghidra/MCP work and mutation safety.",
    communitySafe: false
  },
  {
    id: "re-index",
    title: "Reverse-engineering index",
    group: "RE Docs",
    relativePath: "reverse-engineering/RE-INDEX.md",
    description: "Top-level map for reverse-engineering docs and current evidence lanes.",
    communitySafe: true
  },
  {
    id: "roadmap-index",
    title: "Roadmap index",
    group: "Roadmap",
    relativePath: "roadmap/ROADMAP-INDEX.md",
    description: "Top-level map for planning documents and active roadmap files.",
    communitySafe: true
  },
  {
    id: "electron-migration",
    title: "Workbench architecture",
    group: "Roadmap",
    relativePath: "roadmap/electron-workbench-migration.md",
    description: "Current app direction, architecture rules, and verified milestones.",
    communitySafe: true
  }
];

const browserReleaseContent: ReleasePolicySummary["content"] = browserContentItems.map((item) => ({
  id: item.id,
  title: item.title,
  group: item.group,
  relativePath: item.relativePath,
  communitySafe: item.communitySafe,
  audience: item.communitySafe ? "community" : "maintainer",
  packageDecision: item.communitySafe ? "ship" : "maintainer-only",
  reason: item.communitySafe
    ? "Allowed in the community app content index."
    : "Available to maintainers in the repo, but excluded from the default community content set."
}));

export const browserReleasePolicy: ReleasePolicySummary = {
  generatedAt: new Date().toISOString(),
  repoRoot: "C:\\Projects\\OnslaughtToolkit",
  counts: {
    contentTotal: browserContentItems.length,
    communityDocs: browserContentItems.filter((item) => item.communitySafe).length,
    maintainerDocs: browserContentItems.filter((item) => !item.communitySafe).length,
    allow: 2,
    review: 1,
    conditional: 1,
    deny: 8,
    existingDeniedPaths: 8
  },
  profiles: [
    {
      id: "source-tree",
      title: "Clean source tree",
      status: "blocked",
      summary: "The private working tree still contains denylisted local artifacts.",
      requiredActions: [
        "Keep hard-deny paths out of public branches and archives.",
        "Run release profile and curated manifest checks after the allowlist is refreshed.",
        "Keep agent goal state, repo state files, and generated investigation outputs private."
      ]
    },
    {
      id: "portable-bundle",
      title: "Portable community bundle",
      status: "usable-with-review",
      summary: "A bundle can ship curated docs, app code, and patch metadata while requiring users to select their own game files.",
      requiredActions: [
        "Bundle only community-safe content rows.",
        "Require bring-your-own-game paths for executable, media, saves, and extracted assets.",
        "Write generated job artifacts under user data or a user-selected output directory."
      ]
    }
  ],
  content: browserReleaseContent,
  pathRules: [
    {
      label: "Active source, docs, and tests",
      relativePath: ".",
      classification: "allow",
      audience: "community",
      exists: true,
      reason: "Normal source-tree release material once private paths are excluded."
    },
    {
      label: "Patch catalog",
      relativePath: "patches/catalog",
      classification: "allow",
      audience: "community",
      exists: true,
      reason: "Curated byte metadata; does not bundle a game executable."
    },
    {
      label: "Roadmap docs",
      relativePath: "roadmap",
      classification: "review",
      audience: "maintainer",
      exists: true,
      reason: "Useful for maintainers, but some planning notes may mention private workflow details."
    },
    {
      label: "Reference submodules",
      relativePath: "references",
      classification: "conditional",
      audience: "maintainer",
      exists: true,
      reason: "Source-reference material needs explicit upstream/license scope review before public packaging."
    },
    {
      label: "Game install",
      relativePath: "game",
      classification: "deny",
      audience: "private",
      exists: true,
      reason: "Private bring-your-own-game files; never bundle in a public app or source snapshot."
    },
    {
      label: "Media corpus",
      relativePath: "media",
      classification: "deny",
      audience: "private",
      exists: true,
      reason: "Large and rights-sensitive media must stay local unless separately cleared."
    },
    {
      label: "Save attempts",
      relativePath: "save-attempts",
      classification: "deny",
      audience: "private",
      exists: true,
      reason: "Real saves and scratch proof files are local test samples, not public release content."
    },
    {
      label: "Subagent outputs",
      relativePath: "subagents",
      classification: "deny",
      audience: "private",
      exists: true,
      reason: "Generated investigation logs and extracted manifests are not public package inputs by default."
    },
    {
      label: "Agent goal state",
      relativePath: ".codex",
      classification: "deny",
      audience: "private",
      exists: true,
      reason: "Agent goal contracts and progress ledgers are repo operating material, not community release content."
    },
    {
      label: "Repo state files",
      relativePath: "developer_agent_state.json",
      classification: "deny",
      audience: "private",
      exists: true,
      reason: "Agent handoff state is workspace coordination data, not user-facing release content."
    },
    {
      label: "Documentation state file",
      relativePath: "documentation_agent_state.json",
      classification: "deny",
      audience: "private",
      exists: true,
      reason: "Agent handoff state is workspace coordination data, not user-facing release content."
    },
    {
      label: "RE orchestration state file",
      relativePath: "re_orchestrator_state.json",
      classification: "deny",
      audience: "private",
      exists: true,
      reason: "Reverse-engineering orchestration state is workspace coordination data, not user-facing release content."
    }
  ],
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "release-policy.v1",
    artifactPath: "browser://fixture/release-policy/release-policy.json",
    note: "Preview mode only. Desktop app mode builds this from the repo and curated content index."
  }
};

export const browserContentIndex: ContentIndexSummary = {
  generatedAt: new Date().toISOString(),
  repoRoot: "C:\\Projects\\OnslaughtToolkit",
  items: browserContentItems,
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "content-index.v1",
    note: "Preview mode only. Desktop app mode builds this from a curated repo-local allowlist."
  }
};

export const browserMediaCatalog: MediaCatalogSummary = {
  generatedAt: new Date().toISOString(),
  catalogPath: "browser://fixture/asset-catalog/catalog.json",
  query: "",
  kind: "all",
  counts: {
    textures: 828,
    textureReferencedInPacked: 759,
    textureLooseOnly: 69,
    looseMeshes: 213,
    embeddedMeshes: 139,
    videos: 66,
    languageRows: 2571,
    audioRows: 629,
    musicRows: 10,
    voiceRows: 619,
    total: 4446,
    videoFamilies: {
      briefing: 28,
      cutscene_numeric: 32,
      named_root: 6
    }
  },
  totalRows: 4446,
  returnedRows: 7,
  truncated: true,
  videoGroups: [
    {
      family: "briefing",
      label: "Mission briefings",
      count: 28,
      totalBytes: 78936704,
      sequenceRange: "100-800",
      playbackStatus: "needs-transcode",
      note: "Bink .vid rows are cataloged with hashes and sequence ids, then prepared through the app-owned transcode cache for in-app playback."
    },
    {
      family: "cutscene_numeric",
      label: "Story cutscenes",
      count: 32,
      totalBytes: 240785464,
      sequenceRange: "01-33",
      playbackStatus: "needs-transcode",
      note: "Bink .vid rows are cataloged with hashes and sequence ids, then prepared through the app-owned transcode cache for in-app playback."
    },
    {
      family: "named_root",
      label: "Root/menu clips",
      count: 6,
      totalBytes: 33388480,
      playbackStatus: "needs-transcode",
      note: "Bink .vid rows are cataloged with hashes and sequence ids, then prepared through the app-owned transcode cache for in-app playback."
    }
  ],
  rows: [
    {
      id: "audio:music:bea_01(master).ogg",
      kind: "audio",
      label: "BEA 01(Master)",
      group: "Music",
      sourcePath: "game\\data\\Music\\BEA_01(Master).ogg",
      sizeBytes: 4410518,
      playbackId: "audio:music:bea_01(master).ogg",
      detail: "OGG music track from data\\Music"
    },
    {
      id: "texture:goodies\\ca_f_characters\\ca_fc_hawk.tga",
      kind: "texture",
      label: "goodies\\ca_f_characters\\ca_fc_hawk.tga",
      group: "dxtntextures",
      sourcePath: "game\\data\\resources\\dxtntextures\\goodies%ca_f_characters%ca_fc_hawk.tga(0)A8R8G8B8.aya",
      exportPath: "subagents\\asset_export_wave1_2026-03-13\\loose_textures\\dxtntextures\\goodies%ca_f_characters%ca_fc_hawk.tga(0)A8R8G8B8.png",
      previewId: "texture:goodies\\ca_f_characters\\ca_fc_hawk.tga",
      referenceCount: 1,
      detail: "Hawk bio goodie texture preview target"
    },
    {
      id: "texture:atmospherics\\clouds\\cloud.tga",
      kind: "texture",
      label: "atmospherics\\clouds\\cloud.tga",
      group: "dxtntextures",
      sourcePath: "game\\data\\resources\\dxtntextures\\Atmospherics%Clouds%Cloud.tga(0)A8R8G8B8.aya",
      exportPath:
        "subagents\\asset_export_wave1_2026-03-13\\loose_textures\\dxtntextures\\Atmospherics%Clouds%Cloud.tga(0)A8R8G8B8.png",
      previewId: "texture:atmospherics\\clouds\\cloud.tga",
      referenceCount: 66,
      detail: "1 PNG export, 66 packed references"
    },
    {
      id: "mesh:arachnid.msh",
      kind: "loose_mesh",
      label: "arachnid.msh",
      group: "loose mesh",
      sourcePath: "game\\data\\resources\\meshes\\m_arachnid.msh.aya",
      exportPath: "subagents\\asset_export_wave1_2026-03-13\\loose_meshes\\m_arachnid.msh_binary.fbx",
      referenceCount: 8,
      detail: "1 FBX export, 8 packed references"
    },
    {
      id: "embedded_mesh:100_res_PC/278_embedded_body00_CMSH",
      kind: "embedded_mesh",
      label: "278_embedded_body00_CMSH",
      group: "100_res_PC",
      sourcePath: "subagents\\aya_embedded_mesh_wave1_2026-03-13\\100_res_PC\\278_embedded_body00_CMSH.bin",
      exportPath: "subagents\\asset_export_wave1_2026-03-13\\embedded_meshes\\278_embedded_body00_CMSH_binary.fbx",
      detail: "Embedded CMSH body exported from 100_res_PC"
    },
    {
      id: "video:briefings\\pc_100_exact.vid",
      kind: "video",
      label: "Mission 100 briefing (PC_100_exact.vid)",
      group: "Mission briefings",
      videoFamily: "briefing",
      sequenceId: "100",
      codec: "BIKi",
      playbackStatus: "needs-transcode",
      playbackNote:
        "Bink video sidecar is prepared through an app-owned transcode cache, then played in the workbench video panel.",
      sourcePath: "briefings\\PC_100_exact.vid",
      sizeBytes: 1586724,
      sha256: "183a6916ba819e9144a46d67233722b1ac873a87d6e4c6c808694c0737ff3669",
      videoPlaybackId: "video:video:briefings\\pc_100_exact.vid",
      detail: "BIKi sidecar, sequence 100"
    },
    {
      id: "language:215971",
      kind: "language_row",
      label: "LAP_2",
      group: "0x00034BA3",
      languageCount: 6,
      audioPresentCount: 6,
      detail: "6 languages, 6 audio-linked translations"
    }
  ],
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "media-catalog.v1",
    note: "Preview mode only. Desktop app mode reads the generated asset catalog from disk."
  }
};

export const browserContentDocument: ContentDocumentSummary = {
  id: "lore-book",
  title: "Lore book",
  group: "Lore",
  relativePath: "lore-book/BOOK.md",
  communitySafe: true,
  audience: "community",
  readAt: new Date().toISOString(),
  byteLength: 4212,
  truncated: false,
  markdown:
    "# Lore book\n\nA curated entry point for Battle Engine Aquila preservation material.\n\n- Development history\n- Team and credits\n- Save and options format notes\n- Verified cheat-code behavior\n\nBrowser preview mode renders this sample document. Desktop app mode reads the selected curated markdown document.",
  artifact: {
    kind: "read-only",
    mutation: false,
    schemaVersion: "content-document.v1",
    note: "Preview mode only. Desktop app mode reads a curated markdown document."
  }
};
