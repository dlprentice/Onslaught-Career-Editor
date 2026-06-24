import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import type {
  AddressConversionSection,
  AddressConversionSummary,
  DebugReadinessSummary,
  GameHarnessFileStatus,
  GameHarnessProfileSummary,
  GhidraReadinessSummary,
  HexReadRow,
  HexReadSummary,
  PlannedCommand,
  ToolPathStatus,
  WorkbenchJobCatalogSummary,
  WorkbenchJobDefinition,
  WorkbenchJobPolicy
} from "@onslaught/contracts";

const defaultGhidraInstallPath = "D:\\ghidra_12.0.3_PUBLIC_20260210\\ghidra_12.0.3_PUBLIC";
const defaultGhidraProjectRoot = process.env.USERPROFILE ? path.join(process.env.USERPROFILE, "Ghidra") : "C:\\Ghidra";
const defaultGhydraMcpBundlePath = "D:\\GhydraMCP-Complete-v2.2.0-rc.2-20260211-083952";
const maxHexReadLength = 4096;
const settingsFileName = "onslaught-workbench-settings.json";

interface PeSection {
  name: string;
  virtualAddress: number;
  virtualSize: number;
  rawPointer: number;
  rawSize: number;
}

interface PeLayout {
  imageBase: number;
  sections: PeSection[];
}

interface WorkbenchSettings {
  gameRoot?: string;
}

export async function readHexRange(
  selectedPath: string,
  offsetInput: string | number,
  lengthInput: string | number,
  artifactRoot?: string
): Promise<HexReadSummary> {
  const normalizedPath = path.resolve(selectedPath);
  const offset = parseNonNegativeInteger(offsetInput, "offset");
  const requestedLength = parseNonNegativeInteger(lengthInput, "length");
  if (requestedLength <= 0) {
    throw new Error("Length must be greater than zero.");
  }
  if (requestedLength > maxHexReadLength) {
    throw new Error(`Length is capped at ${maxHexReadLength} bytes per read.`);
  }

  const stat = await fs.stat(normalizedPath);
  if (!stat.isFile()) {
    throw new Error("Selected path is not a file.");
  }
  if (offset >= stat.size) {
    throw new Error(`Offset ${toHex(offset)} is outside the file.`);
  }

  const data = await fs.readFile(normalizedPath);
  const availableLength = Math.max(0, Math.min(requestedLength, data.length - offset));
  const window = data.subarray(offset, offset + availableLength);
  const readAt = new Date().toISOString();
  const sha256 = createHash("sha256").update(data).digest("hex");
  const summary: HexReadSummary = {
    selectedPath: normalizedPath,
    fileName: path.basename(normalizedPath),
    fileSize: data.length,
    sha256,
    readAt,
    offset,
    offsetHex: toHex(offset),
    requestedLength,
    byteLength: window.length,
    truncated: window.length !== requestedLength,
    rows: buildHexRows(offset, window),
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "hex-read.v1",
      note: "Read-only byte window. No bytes were changed."
    }
  };

  if (!artifactRoot) {
    return summary;
  }

  return writeHexArtifact(summary, artifactRoot);
}

export async function convertExecutableAddress(
  executablePath: string,
  virtualAddressInput: string | number
): Promise<AddressConversionSummary> {
  const normalizedPath = path.resolve(executablePath);
  const stat = await fs.stat(normalizedPath);
  if (!stat.isFile()) {
    throw new Error("Selected path is not a file.");
  }

  const data = await fs.readFile(normalizedPath);
  const virtualAddress = parseNonNegativeInteger(virtualAddressInput, "virtual address");
  const layout = parsePeLayout(data);
  if (virtualAddress < layout.imageBase) {
    throw new Error(`Virtual address ${toHex(virtualAddress)} is below image base ${toHex(layout.imageBase)}.`);
  }

  const rva = virtualAddress - layout.imageBase;
  const section = layout.sections.find((candidate) => {
    const span = Math.max(candidate.virtualSize, candidate.rawSize);
    return rva >= candidate.virtualAddress && rva < candidate.virtualAddress + span;
  });
  if (!section) {
    throw new Error(`Virtual address ${toHex(virtualAddress)} does not map to a known PE section.`);
  }

  const offsetInSection = rva - section.virtualAddress;
  if (offsetInSection >= section.rawSize) {
    throw new Error(
      `Virtual address ${toHex(virtualAddress)} is in ${section.name} but outside file-backed raw bytes.`
    );
  }

  const fileOffset = section.rawPointer + offsetInSection;
  if (fileOffset >= data.length) {
    throw new Error(`Computed file offset ${toHex(fileOffset)} is outside the executable.`);
  }

  const sha256 = createHash("sha256").update(data).digest("hex");
  return {
    executablePath: normalizedPath,
    fileName: path.basename(normalizedPath),
    fileSize: data.length,
    sha256,
    convertedAt: new Date().toISOString(),
    imageBaseHex: toHex(layout.imageBase),
    virtualAddressHex: toHex(virtualAddress),
    rvaHex: toHex(rva),
    fileOffsetHex: toHex(fileOffset),
    fileOffset,
    section: sectionToSummary(section),
    shortcutTextVaMinusImageBase: section.name === ".text" && fileOffset === rva,
    note:
      section.name === ".text" && fileOffset === rva
        ? "For this .text address, file offset equals VA - image base."
        : "Converted by PE section headers; do not assume VA - image base for every section."
  };
}

export async function getGhidraReadiness(appPath: string): Promise<GhidraReadinessSummary> {
  const repoRoot = await resolveRepoRoot(appPath);
  const readOnlyScripts = [
    "ExportWeakFunctionList.java",
    "ExportFunctionsByAddressDecompile.java",
    "ExportFunctionsByPrefixDecompile.java",
    "ExportXrefsForAddresses.java",
    "DumpDisassemblyRange.java",
    "DumpPointerTable.java",
    "DumpCStringAtAddress.java",
    "ResolveVtableTypeNames.java"
  ];
  const mutationScripts = [
    "GhidraBatchRename.java",
    "CreateFunctionsFromAddressList.java",
    "ApplyPhase5HighImpactSignatureQueue.java",
    "ApplyWave217SignaturePass1.java"
  ];
  const headlessRunner = path.join(repoRoot, "tools", "run_ghidra_headless_postscript.sh");
  const renameRunner = path.join(repoRoot, "tools", "run_ghidra_batch_rename_headless.sh");
  const paths = await Promise.all([
    statusOf("Ghidra install", defaultGhidraInstallPath, "Pinned local Ghidra client root."),
    statusOf(
      "analyzeHeadless.bat",
      path.join(defaultGhidraInstallPath, "support", "analyzeHeadless.bat"),
      "Windows headless runner used by repo scripts."
    ),
    statusOf("Ghidra projects", defaultGhidraProjectRoot, "Local project root for BEA analysis."),
    statusOf("Ghydra MCP bundle", defaultGhydraMcpBundlePath, "Pinned MCP bridge/plugin bundle."),
    statusOf(
      "Ghydra bridge",
      path.join(defaultGhydraMcpBundlePath, "bridge_mcp_hydra.py"),
      "Python bridge launched by Codex MCP."
    ),
    statusOf("Headless postscript runner", headlessRunner, "Preferred Java postscript execution wrapper."),
    statusOf("Batch rename runner", renameRunner, "Dry-run/apply wrapper for rename maps."),
    ...readOnlyScripts.map((script) =>
      statusOf(script, path.join(repoRoot, "tools", script), "Read-only Ghidra evidence script.")
    ),
    ...mutationScripts.map((script) =>
      statusOf(script, path.join(repoRoot, "tools", script), "Mutation-capable Ghidra script.")
    )
  ]);

  const hasHeadlessRunner = pathExists(paths, "Headless postscript runner");
  const hasRenameRunner = pathExists(paths, "Batch rename runner");
  const hasReadOnlyExporter = pathExists(paths, "ExportWeakFunctionList.java");
  const commands: PlannedCommand[] = [
    {
      label: "Export weak function list",
      command: "tools/run_ghidra_headless_postscript.sh ExportWeakFunctionList.java <out_path> all",
      mutation: false,
      status: hasHeadlessRunner && hasReadOnlyExporter ? "ready" : "blocked",
      detail: "Read-only inventory job for function coverage and naming queues."
    },
    {
      label: "Export decompile by address list",
      command: "tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java <address_list> <out_dir>",
      mutation: false,
      status:
        hasHeadlessRunner && pathExists(paths, "ExportFunctionsByAddressDecompile.java") ? "ready" : "blocked",
      detail: "Read-only semantic evidence export for selected functions."
    },
    {
      label: "Dry-run batch rename map",
      command: "tools/run_ghidra_batch_rename_headless.sh <map> dry",
      mutation: false,
      status: hasRenameRunner && pathExists(paths, "GhidraBatchRename.java") ? "ready" : "blocked",
      detail: "Required validation gate before a rename apply."
    },
    {
      label: "Apply batch rename map",
      command: "tools/run_ghidra_batch_rename_headless.sh <map> apply",
      mutation: true,
      status: "blocked",
      detail: "Intentionally blocked until dry-run success, project-lock checks, and explicit arming are wired."
    }
  ];

  return {
    checkedAt: new Date().toISOString(),
    repoRoot,
    configuredInstallPath: defaultGhidraInstallPath,
    configuredProjectRoot: defaultGhidraProjectRoot,
    configuredMcpBundlePath: defaultGhydraMcpBundlePath,
    paths,
    commands,
    readOnlyScripts,
    mutationScripts,
    ready: pathExists(paths, "Ghidra install") && pathExists(paths, "Ghidra projects") && commands[0].status === "ready",
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "ghidra-readiness.v1",
      note: "Readiness inventory only. No Ghidra process was launched."
    }
  };
}

export async function getDebugReadiness(appPath: string): Promise<DebugReadinessSummary> {
  const repoRoot = await resolveRepoRoot(appPath);
  const runtimeProbeNames = [
    "defaultoptions-wave1.cdb.txt",
    "maladim-wave1.cdb.txt",
    "maladim-positive-wave2.cdb.txt",
    "pause-persist-wave1.cdb.txt"
  ];
  const paths = await Promise.all([
    statusOf("CDB path resolver", path.join(repoRoot, "tools", "get_cdb_path.ps1"), "Find installed cdb.exe."),
    statusOf(
      "CDB server launcher",
      path.join(repoRoot, "tools", "start_cdb_server.ps1"),
      "Start a CDB server attached to a running process."
    ),
    statusOf("CDB client connector", path.join(repoRoot, "tools", "connect_cdb_client.ps1"), "Attach a CDB client."),
    statusOf("WinDbg tail helper", path.join(repoRoot, "tools", "windbg_tail.py"), "Tail debugger output logs.")
  ]);
  const probeScripts = await Promise.all(
    runtimeProbeNames.map((probe) =>
      statusOf(probe, path.join(repoRoot, "tools", "runtime-probes", probe), "Canned runtime probe command file.")
    )
  );
  const hasResolver = pathExists(paths, "CDB path resolver");
  const hasServer = pathExists(paths, "CDB server launcher");
  const hasClient = pathExists(paths, "CDB client connector");
  const hasProbe = probeScripts.some((probe) => probe.exists);
  const commands: PlannedCommand[] = [
    {
      label: "Resolve debugger",
      command: "powershell -ExecutionPolicy Bypass -File tools/get_cdb_path.ps1",
      mutation: false,
      status: hasResolver ? "ready" : "blocked",
      detail: "Read-only check for Windows debugger tools."
    },
    {
      label: "Start debug server",
      command:
        "powershell -ExecutionPolicy Bypass -File tools/start_cdb_server.ps1 -ProcessName BEA.exe -CommandFile <probe>",
      mutation: false,
      status: hasServer && hasProbe ? "ready" : "blocked",
      detail: "Runtime attach job for an already-running BEA.exe; future UI must arm it explicitly before execution."
    },
    {
      label: "Connect debug client",
      command: "powershell -ExecutionPolicy Bypass -File tools/connect_cdb_client.ps1",
      mutation: false,
      status: hasClient ? "ready" : "blocked",
      detail: "Attach to the server and stream text output into an artifact bundle."
    }
  ];

  return {
    checkedAt: new Date().toISOString(),
    repoRoot,
    paths,
    probeScripts,
    commands,
    ready: hasResolver && hasServer && hasClient && hasProbe,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "debug-readiness.v1",
      note: "Debugger readiness inventory only. No process was launched or attached."
    }
  };
}

export async function getGameHarnessProfile(
  appPath: string,
  settingsRoot?: string
): Promise<GameHarnessProfileSummary> {
  const repoRoot = await resolveRepoRoot(appPath);
  if (settingsRoot) {
    const settings = await readSettings(settingsRoot);
    if (settings.gameRoot) {
      return inspectGameHarnessProfile(appPath, settings.gameRoot, "stored", settingsPath(settingsRoot), repoRoot);
    }
  }

  return inspectGameHarnessProfile(appPath, undefined, "repo-default", settingsRoot ? settingsPath(settingsRoot) : undefined, repoRoot);
}

export async function setGameHarnessProfile(
  appPath: string,
  settingsRoot: string,
  gameRoot: string
): Promise<GameHarnessProfileSummary> {
  const repoRoot = await resolveRepoRoot(appPath);
  const normalizedGameRoot = path.resolve(gameRoot);
  await assertDirectory(normalizedGameRoot, "Game folder");
  await writeSettings(settingsRoot, { gameRoot: normalizedGameRoot });
  return inspectGameHarnessProfile(appPath, normalizedGameRoot, "selected", settingsPath(settingsRoot), repoRoot);
}

export async function inspectGameHarnessProfilePath(
  appPath: string,
  gameRoot: string
): Promise<GameHarnessProfileSummary> {
  const repoRoot = await resolveRepoRoot(appPath);
  const normalizedGameRoot = path.resolve(gameRoot);
  await assertDirectory(normalizedGameRoot, "Game folder");
  return inspectGameHarnessProfile(appPath, normalizedGameRoot, "selected", undefined, repoRoot);
}

export async function clearGameHarnessProfile(
  appPath: string,
  settingsRoot: string
): Promise<GameHarnessProfileSummary> {
  await writeSettings(settingsRoot, {});
  const repoRoot = await resolveRepoRoot(appPath);
  return inspectGameHarnessProfile(appPath, undefined, "repo-default", settingsPath(settingsRoot), repoRoot);
}

async function inspectGameHarnessProfile(
  appPath: string,
  explicitGameRoot: string | undefined,
  profileSource: GameHarnessProfileSummary["profileSource"],
  configPath: string | undefined,
  knownRepoRoot?: string
): Promise<GameHarnessProfileSummary> {
  const repoRoot = knownRepoRoot ?? (await resolveRepoRoot(appPath));
  const gameRoot = explicitGameRoot ? path.resolve(explicitGameRoot) : path.join(repoRoot, "game");
  const executablePath = path.join(gameRoot, "BEA.exe");
  const files: GameHarnessFileStatus[] = await Promise.all([
    gameStatus("BEA.exe", executablePath, true, "Executable specimen for launch and patch verification."),
    gameStatus("data/", path.join(gameRoot, "data"), true, "Retail data directory."),
    gameStatus("defaultoptions.bea", path.join(gameRoot, "defaultoptions.bea"), true, "Boot options source."),
    gameStatus("savegames/", path.join(gameRoot, "savegames"), false, "Local saves directory."),
    gameStatus("binkw32.dll", path.join(gameRoot, "binkw32.dll"), true, "Video/runtime dependency."),
    gameStatus("ogg.dll", path.join(gameRoot, "ogg.dll"), true, "Audio/runtime dependency."),
    gameStatus("vorbis.dll", path.join(gameRoot, "vorbis.dll"), true, "Audio/runtime dependency."),
    gameStatus("zlib.dll", path.join(gameRoot, "zlib.dll"), true, "Compression/runtime dependency."),
    gameStatus("steam_appid.txt", path.join(gameRoot, "steam_appid.txt"), false, "Steam compatibility sidecar.")
  ]);
  const ready = files.filter((file) => file.required).every((file) => file.exists);

  return {
    checkedAt: new Date().toISOString(),
    repoRoot,
    gameRoot,
    profileSource,
    configPath,
    executablePath,
    workingDirectory: gameRoot,
    recommendedArgs: [],
    files,
    launchPlan: {
      label: "Launch verified game profile",
      command: `Start-Process -FilePath "${executablePath}" -WorkingDirectory "${gameRoot}"`,
      mutation: false,
      status: ready ? "ready" : "blocked",
      detail: "Planned launch command only. Actual launch stays behind the typed gated job path."
    },
    ready,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "game-harness-profile.v1",
      note: "Game harness inventory only. No game process was launched."
    }
  };
}

export async function getJobCatalog(appPath: string, settingsRoot?: string): Promise<WorkbenchJobCatalogSummary> {
  const [repoRoot, ghidra, debug, harness] = await Promise.all([
    resolveRepoRoot(appPath),
    getGhidraReadiness(appPath),
    getDebugReadiness(appPath),
    getGameHarnessProfile(appPath, settingsRoot)
  ]);
  const assetCatalogReady = await hasRequiredAssetCatalogInputs(repoRoot);
  const appCoreDiagnosticsEnabled = process.env.ONSLAUGHT_ENABLE_APPCORE_DIAGNOSTICS === "1";
  const appCoreHostReady =
    appCoreDiagnosticsEnabled &&
    (await hasFile(path.join(repoRoot, "OnslaughtCareerEditor.AppCore.Host", "OnslaughtCareerEditor.AppCore.Host.csproj")));
  const catalogRows: Array<Omit<WorkbenchJobDefinition, "policy">> = [
    {
      id: "file.hexRead",
      lane: "file",
      title: "Read bounded hex window",
      safety: "read-only",
      status: "available",
      detail: "Read up to 4 KiB from a selected local file and write a compact JSON artifact.",
      artifactSchema: "hex-read.v1",
      inputs: [
        { name: "path", label: "File path", required: true, detail: "Local file selected by dialog or typed path." },
        { name: "offset", label: "Offset", required: true, detail: "Decimal or 0x-prefixed byte offset." },
        { name: "length", label: "Length", required: true, detail: "Positive byte count capped at 4096." }
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
      inputs: [
        { name: "path", label: "Copied save/options path", required: true, detail: "Must be inside the app artifact/profile root. Repo-local saves are rejected." },
        { name: "rank", label: "Rank", required: false, detail: "Default mission rank for the copied target." },
        { name: "kills", label: "Kill count", required: false, detail: "Default kill count per category for the copied target." },
        { name: "levelRanks", label: "Level ranks", required: false, detail: "Optional NODE_INDEX:RANK tokens, such as 1:S 2:A." },
        { name: "perCategoryKills", label: "Per-category kills", required: false, detail: "Optional category:kills tokens, such as aircraft:100 mechs:20." },
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
        { name: "keybindOverrides", label: "Keybind overrides", required: false, detail: "Semicolon rows like move-forward=W,Up;fire-weapon=MouseLeft,RControl." },
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
      detail: "Apply the native TypeScript settings/keybind patch only to an artifact-owned candidate copy, compare it, and keep the source unchanged.",
      artifactSchema: "options-patch-preview.v1",
      inputs: [
        { name: "path", label: "Options path", required: true, detail: ".bea or defaultoptions.bea target. The source file is not modified." },
        { name: "soundVolume", label: "Sound volume", required: false, detail: "Optional 0.0-1.0 float for the candidate copy." },
        { name: "musicVolume", label: "Music volume", required: false, detail: "Optional 0.0-1.0 float for the candidate copy." },
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
        { name: "keybindOverrides", label: "Keybind overrides", required: false, detail: "Semicolon rows like move-forward=W,Up;fire-weapon=MouseLeft,RControl." },
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
      detail: "Apply settings/keybind changes only to a .bea/defaultoptions file inside the app artifact/profile root, after writing a backup and verifying read-back bytes.",
      artifactSchema: "options-patch-apply.v1",
      inputs: [
        { name: "path", label: "Copied options path", required: true, detail: "Must be inside the app artifact/profile root. Repo-local defaultoptions.bea is rejected." },
        { name: "soundVolume", label: "Sound volume", required: false, detail: "Optional 0.0-1.0 float for the copied target." },
        { name: "musicVolume", label: "Music volume", required: false, detail: "Optional 0.0-1.0 float for the copied target." },
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
        { name: "keybindOverrides", label: "Keybind overrides", required: false, detail: "Semicolon rows like move-forward=W,Up;fire-weapon=MouseLeft,RControl." },
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
      status: appCoreHostReady ? "available" : "blocked",
      detail: "Hidden-by-default C# parity diagnostic. Run the AppCore JSON host against a .bes/.bea file and preserve the typed read-only payload.",
      commandPreview: "dotnet run --project OnslaughtCareerEditor.AppCore.Host -- inspect-save <path>",
      artifactSchema: "appcore-save-analysis.v1",
      inputs: [
        { name: "path", label: "Save/options path", required: true, detail: ".bes career save, .bea options file, or defaultoptions.bea backup." }
      ]
    },
    {
      id: "appcore.compareSaves",
      lane: "appcore",
      title: "Parity diagnostic: compare saves with AppCore host",
      safety: "read-only",
      status: appCoreHostReady ? "available" : "blocked",
      detail: "Hidden-by-default C# parity diagnostic. Run the AppCore JSON host comparison against two .bes/.bea files and preserve the typed read-only payload.",
      commandPreview: "dotnet run --project OnslaughtCareerEditor.AppCore.Host -- compare-saves <left> <right>",
      artifactSchema: "appcore-save-comparison.v1",
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
      status: appCoreHostReady ? "available" : "blocked",
      detail: "Hidden-by-default C# parity diagnostic. Write an explicit appcore-save-patch-request.v1 JSON intent, validate it through the AppCore host, and preserve a read-only patch plan.",
      commandPreview: "dotnet run --project OnslaughtCareerEditor.AppCore.Host -- plan-save-patch <request.json>",
      artifactSchema: "appcore-save-patch-plan.v1",
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
      status: appCoreHostReady ? "available" : "blocked",
      detail: "Hidden-by-default C# parity diagnostic. Patch only a temporary copy through the AppCore host, compare it back to the source, delete the temp copy, and preserve the read-only preview payload.",
      commandPreview: "dotnet run --project OnslaughtCareerEditor.AppCore.Host -- preview-save-patch <path> --rank S --kills 100",
      artifactSchema: "appcore-save-patch-preview.v1",
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
      inputs: []
    },
    {
      id: "ghidra.exportWeakFunctions",
      lane: "ghidra",
      title: "Export weak function list",
      safety: "read-only",
      status: commandReady(ghidra.commands, "Export weak function list") ? "available" : "blocked",
      detail: "Run the read-only weak-function inventory script through the headless postscript runner.",
      commandPreview: "tools/run_ghidra_headless_postscript.sh ExportWeakFunctionList.java <artifact_tsv> weak",
      artifactSchema: "ghidra-export.v1",
      inputs: [
        { name: "mode", label: "Mode", required: false, detail: "Use weak by default; all exports every function." }
      ]
    },
    {
      id: "ghidra.exportAddressDecompile",
      lane: "ghidra",
      title: "Export decompile for addresses",
      safety: "read-only",
      status: commandReady(ghidra.commands, "Export decompile by address list") ? "available" : "blocked",
      detail: "Run a read-only decompile/export pass for structured address tokens written under the artifact root.",
      commandPreview:
        "tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java <artifact_addresses> <artifact_out_dir>",
      artifactSchema: "ghidra-decompile-export.v1",
      inputs: [
        { name: "addresses", label: "Addresses", required: false, detail: "0x-prefixed or hex address tokens; defaults to CCareer__Load." },
        { name: "timeoutSec", label: "Timeout seconds", required: false, detail: "Per-function decompile timeout, capped by the job runner." }
      ]
    },
    {
      id: "ghidra.validateRenameMap",
      lane: "ghidra",
      title: "Dry-run Ghidra rename map",
      safety: "read-only",
      status: commandReady(ghidra.commands, "Dry-run batch rename map") ? "available" : "blocked",
      detail: "Run the allowlisted headless rename helper in dry mode against an artifact-root two-column rename map.",
      commandPreview: "tools/run_ghidra_batch_rename_headless.sh <map> dry",
      artifactSchema: "ghidra-rename-dry-run.v1",
      inputs: [
        { name: "mapPath", label: "Rename map", required: true, detail: "Two-column address/name map inside the app artifact root." }
      ]
    },
    {
      id: "ghidra.applyRenameMap",
      lane: "ghidra",
      title: "Apply Ghidra rename map",
      safety: "mutation-gated",
      status: commandReady(ghidra.commands, "Apply batch rename map") ? "available" : "blocked",
      detail: "Apply an artifact-root rename map only after a successful dry-run artifact and explicit arming.",
      commandPreview: "tools/run_ghidra_batch_rename_headless.sh <map> apply",
      artifactSchema: "ghidra-mutation.v1",
      inputs: [
        { name: "mapPath", label: "Rename map", required: true, detail: "Two-column address/name map inside the app artifact root." },
        { name: "dryRunArtifactPath", label: "Dry-run artifact", required: true, detail: "A successful ghidra-rename-dry-run.v1 artifact for the same map." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be APPLY GHIDRA RENAME MAP." },
        { name: "acceptsGhidraMutation", label: "Ghidra mutation acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "debug.resolveCdb",
      lane: "debugger",
      title: "Resolve CDB path",
      safety: "read-only",
      status: commandReady(debug.commands, "Resolve debugger") ? "available" : "blocked",
      detail: "Run the repo helper that finds the installed x86 cdb.exe path.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/get_cdb_path.ps1",
      artifactSchema: "debug-readiness.v1",
      inputs: []
    },
    {
      id: "debug.planProbeSession",
      lane: "debugger",
      title: "Plan CDB probe session",
      safety: "read-only",
      status: commandReady(debug.commands, "Start debug server") && harness.ready ? "available" : "blocked",
      detail: "Validate the game profile and an allowlisted runtime-probe command file, then write a non-launching CDB attach-session plan.",
      commandPreview:
        "powershell -ExecutionPolicy Bypass -File tools/start_cdb_server.ps1 -ProcessName BEA.exe -CommandFile <allowlisted_probe> -PrintOnly",
      artifactSchema: "debug-probe-plan.v1",
      inputs: [
        { name: "probeId", label: "Probe script", required: false, detail: "Allowlisted script from tools/runtime-probes." },
        { name: "gameRoot", label: "Game root", required: false, detail: "Defaults to the active game profile." },
        { name: "port", label: "Port", required: false, detail: "Local CDB server port, default 5005." }
      ]
    },
    {
      id: "debug.startProbeServer",
      lane: "debugger",
      title: "Attach CDB probe server",
      safety: "launch-gated",
      status: commandReady(debug.commands, "Start debug server") && harness.ready ? "available" : "blocked",
      detail: "Starts CDB and attaches to a running BEA.exe with an allowlisted command file only after visible arming and a copied/safe game profile check.",
      commandPreview:
        "powershell -ExecutionPolicy Bypass -File tools/start_cdb_server.ps1 -ProcessName BEA.exe -CommandFile <probe>",
      artifactSchema: "debug-session.v1",
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
      inputs: []
    },
    {
      id: "runtime.tailManagedLog",
      lane: "runtime",
      title: "Read managed runtime log tail",
      safety: "read-only",
      status: "available",
      detail: "Read a bounded tail from a log path recorded by a managed game/CDB launch job without accepting raw renderer file paths.",
      artifactSchema: "managed-process-log-tail.v1",
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
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional job run id; defaults to latest running managed process." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded PID when no run id is supplied." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be STOP PROCESS." },
        { name: "acceptsProcessStop", label: "Process stop acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "game.planWindowCapture",
      lane: "game",
      title: "Plan game-window capture",
      safety: "read-only",
      status: "available",
      detail: "Scan for a visible BEA.exe window owned by a managed game launch and write a read-only capture/input plan without opening a desktop stream.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/list_game_windows.ps1 -ProcessName BEA.exe",
      artifactSchema: "game-window-capture-plan.v1",
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id; defaults to the latest recorded game process." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID when no run id is supplied." },
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
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id; defaults to the latest recorded game process." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID when no run id is supplied." },
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
      detail:
        "Capture a short bounded sequence of BEA window PNG frames for observe-act-observe loops without leaving a live stream open.",
      commandPreview: "desktopCapturer.getSources(...) repeated for <frameCount> bounded frames",
      artifactSchema: "game-window-frame-sequence.v1",
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id; defaults to the latest recorded game process." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID when no run id is supplied." },
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
      detail:
        "Validate a small allowlisted keyboard input sequence for a managed BEA.exe window without focusing the window or sending input.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -ProcessName BEA.exe -Sequence <allowlisted> -PrintOnly",
      artifactSchema: "game-window-input.v1",
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id; defaults to latest running game process." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID when no run id is supplied." },
        { name: "hwndHex", label: "Window handle", required: false, detail: "Optional BEA.exe window handle from a capture plan." },
        { name: "sequence", label: "Input sequence", required: true, detail: "Semicolon/comma separated tap:KEY, down:KEY, up:KEY, wait:MS actions." },
        { name: "stepDelayMs", label: "Step delay", required: false, detail: "Delay between key events, 0-1000 ms; default 60." }
      ]
    },
    {
      id: "game.sendWindowInput",
      lane: "game",
      title: "Send scoped game-window input",
      safety: "launch-gated",
      status: "available",
      detail:
        "Focus a managed BEA.exe top-level window and send only allowlisted keyboard actions after explicit arming.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -ProcessName BEA.exe -Sequence <allowlisted>",
      artifactSchema: "game-window-input.v1",
      inputs: [
        { name: "targetRunId", label: "Target run id", required: false, detail: "Optional managed game launch run id; defaults to latest running game process." },
        { name: "processId", label: "Process id", required: false, detail: "Optional recorded BEA.exe PID when no run id is supplied." },
        { name: "hwndHex", label: "Window handle", required: false, detail: "Optional BEA.exe window handle from a capture plan." },
        { name: "sequence", label: "Input sequence", required: true, detail: "Semicolon/comma separated tap:KEY, down:KEY, up:KEY, wait:MS actions." },
        { name: "stepDelayMs", label: "Step delay", required: false, detail: "Delay between key events, 0-1000 ms; default 60." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be SEND GAME INPUT." },
        { name: "acceptsWindowInput", label: "Window input acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "game.inventoryProfile",
      lane: "game",
      title: "Inventory game harness profile",
      safety: "read-only",
      status: harness.ready ? "available" : "blocked",
      detail: "Check the local game directory for BEA.exe, options, data, and runtime DLLs.",
      artifactSchema: "game-harness-profile.v1",
      inputs: [
        { name: "gameRoot", label: "Game root", required: false, detail: "Defaults to repo-local game/ for private lane." }
      ]
    },
    {
      id: "game.planLaunchProfile",
      lane: "game",
      title: "Plan verified game launch",
      safety: "read-only",
      status: harness.ready ? "available" : "blocked",
      detail: "Verify the active game profile and executable hash, then write a non-launching game launch plan.",
      commandPreview: harness.launchPlan.command,
      artifactSchema: "game-launch-plan.v1",
      inputs: [
        { name: "gameRoot", label: "Game root", required: false, detail: "Defaults to the active game profile." },
        { name: "args", label: "Arguments", required: false, detail: "Optional allowlisted launch arguments. Windowed mode is handled by the patch catalog, not the default launch plan." }
      ]
    },
    {
      id: "game.prepareSafeProfile",
      lane: "game",
      title: "Prepare copied game profile",
      safety: "mutation-gated",
      status: harness.ready ? "available" : "blocked",
      detail: "Copy a validated local game profile into the app artifact root so launch/debug jobs can run outside the repo-local private game tree.",
      commandPreview: "powershell -ExecutionPolicy Bypass -File tools/prepare_game_profile.ps1 -SourceGameRoot <game> -OutputRoot <artifact_profiles>",
      artifactSchema: "game-profile-prepare.v1",
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
      status: harness.ready ? "available" : "blocked",
      detail: "Launch BEA.exe only after visible arming, specimen verification, and a copied/safe game profile check.",
      commandPreview: harness.launchPlan.command,
      artifactSchema: "game-launch.v1",
      inputs: [
        { name: "gameRoot", label: "Game root", required: true, detail: "Copied/safe game profile outside the repo root." },
        { name: "args", label: "Arguments", required: false, detail: "Optional allowlisted launch arguments. Leave blank for the normal patched-profile path." },
        { name: "armPhrase", label: "Arm phrase", required: true, detail: "Must be LAUNCH BEA." },
        { name: "acceptsProfileWrites", label: "Profile write acknowledgement", required: true, detail: "Must be true." }
      ]
    },
    {
      id: "assets.catalogGameFiles",
      lane: "assets",
      title: "Catalog game assets",
      safety: "read-only",
      status: assetCatalogReady ? "available" : "blocked",
      detail: "Rebuild the cross-surface asset catalog from existing exported manifests into the artifact root.",
      artifactSchema: "asset-catalog.v1",
      inputs: []
    },
    {
      id: "content.readDocument",
      lane: "content",
      title: "Read curated document",
      safety: "read-only",
      status: "available",
      detail: "Read one allowlisted lore, save, RE, or roadmap markdown document.",
      artifactSchema: "content-document.v1",
      inputs: [
        { name: "id", label: "Document ID", required: true, detail: "Allowlisted content document id." }
      ]
    }
  ];
  const productCatalogRows = appCoreDiagnosticsEnabled
    ? catalogRows
    : catalogRows.filter((definition) => definition.lane !== "appcore");
  const definitions = productCatalogRows.map(applyJobPolicy);
  const counts = {
    available: definitions.filter((job) => job.status === "available").length,
    blocked: definitions.filter((job) => job.status === "blocked").length,
    planned: definitions.filter((job) => job.status === "planned").length,
    readOnly: definitions.filter((job) => job.safety === "read-only").length,
    gated: definitions.filter((job) => job.safety !== "read-only").length
  };

  return {
    generatedAt: new Date().toISOString(),
    repoRoot,
    definitions,
    counts,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "job-catalog.v1",
      note: "Allowlisted job catalog only. This endpoint does not launch tools or mutate files."
    }
  };
}

function applyJobPolicy(definition: Omit<WorkbenchJobDefinition, "policy">): WorkbenchJobDefinition {
  return {
    ...definition,
    policy: jobPolicyFor(definition)
  };
}

function jobPolicyFor(definition: Omit<WorkbenchJobDefinition, "policy">): WorkbenchJobPolicy {
  if (definition.id === "file.hexRead" || definition.id === "file.peAddressConvert" || definition.id === "content.readDocument") {
    return {
      timeoutMs: 10_000,
      cancellable: false,
      externalProcess: false
    };
  }

  if (
    definition.id === "save.planPatch" ||
    definition.id === "save.previewPatch" ||
    definition.id === "settings.planOptionsPatch" ||
    definition.id === "settings.previewOptionsPatch" ||
    definition.id === "patch.verifySpecimen" ||
    definition.id === "patch.planCatalogPatch" ||
    definition.id === "release.inspectPolicy" ||
    definition.id === "debug.planProbeSession" ||
    definition.id === "game.inventoryProfile" ||
    definition.id === "game.planLaunchProfile" ||
    definition.id === "debug.resolveCdb" ||
    definition.id === "runtime.listManagedProcesses" ||
    definition.id === "runtime.tailManagedLog" ||
    definition.id === "game.planWindowCapture" ||
    definition.id === "game.captureWindowFrame" ||
    definition.id === "game.captureWindowSequence" ||
    definition.id === "game.planWindowInput"
  ) {
    return {
      timeoutMs: 30_000,
      cancellable: false,
      externalProcess:
        definition.id === "debug.resolveCdb" ||
        definition.id === "game.planWindowCapture" ||
        definition.id === "game.captureWindowFrame" ||
        definition.id === "game.captureWindowSequence" ||
        definition.id === "game.planWindowInput"
    };
  }

  if (
    definition.id === "save.applyPatch" ||
    definition.id === "save.prepareCopy" ||
    definition.id === "save.restoreBackup" ||
    definition.id === "settings.applyOptionsPatch" ||
    definition.id === "patch.prepareExecutableCopy" ||
    definition.id === "patch.applyCatalogPatch" ||
    definition.id === "patch.restoreCatalogBackup"
  ) {
    return {
      timeoutMs: 30_000,
      cancellable: false,
      externalProcess: false
    };
  }

  if (
    definition.id === "appcore.inspectSave" ||
    definition.id === "appcore.compareSaves" ||
    definition.id === "appcore.planSavePatch" ||
    definition.id === "appcore.previewSavePatch"
  ) {
    return {
      timeoutMs: 120_000,
      cancellable: false,
      externalProcess: true
    };
  }

  if (definition.lane === "ghidra" || definition.lane === "assets") {
    return {
      timeoutMs: 600_000,
      cancellable: true,
      externalProcess: true
    };
  }

  if (
    definition.id === "debug.startProbeServer" ||
    definition.id === "game.launchProfile" ||
    definition.id === "runtime.stopManagedProcess" ||
    definition.id === "game.sendWindowInput"
  ) {
    return {
      timeoutMs: definition.id === "runtime.stopManagedProcess" ? 10_000 : 30_000,
      cancellable: false,
      externalProcess: definition.id !== "runtime.stopManagedProcess"
    };
  }

  if (definition.id === "game.prepareSafeProfile") {
    return {
      timeoutMs: 900_000,
      cancellable: false,
      externalProcess: true
    };
  }

  if (definition.lane === "debugger" || definition.lane === "game") {
    return {
      timeoutMs: 300_000,
      cancellable: true,
      externalProcess: true
    };
  }

  return {
    timeoutMs: 60_000,
    cancellable: definition.safety !== "read-only",
    externalProcess: definition.safety !== "read-only"
  };
}

function buildHexRows(baseOffset: number, data: Buffer): HexReadRow[] {
  const rows: HexReadRow[] = [];
  for (let index = 0; index < data.length; index += 16) {
    const row = data.subarray(index, index + 16);
    rows.push({
      offset: baseOffset + index,
      offsetHex: toHex(baseOffset + index),
      hex: Array.from(row)
        .map((byte) => byte.toString(16).padStart(2, "0").toUpperCase())
        .join(" "),
      ascii: Array.from(row)
        .map((byte) => (byte >= 0x20 && byte <= 0x7e ? String.fromCharCode(byte) : "."))
        .join("")
    });
  }
  return rows;
}

function parsePeLayout(data: Buffer): PeLayout {
  if (data.length < 0x40 || data.toString("ascii", 0, 2) !== "MZ") {
    throw new Error("Executable is not a valid MZ/PE file.");
  }

  const peOffset = data.readUInt32LE(0x3c);
  if (peOffset <= 0 || peOffset + 0x18 >= data.length || data.toString("ascii", peOffset, peOffset + 4) !== "PE\u0000\u0000") {
    throw new Error("Executable has an invalid PE header.");
  }

  const numberOfSections = data.readUInt16LE(peOffset + 6);
  const optionalHeaderSize = data.readUInt16LE(peOffset + 20);
  const optionalHeaderOffset = peOffset + 24;
  const magic = data.readUInt16LE(optionalHeaderOffset);
  const imageBase =
    magic === 0x20b
      ? Number(data.readBigUInt64LE(optionalHeaderOffset + 24))
      : data.readUInt32LE(optionalHeaderOffset + 28);
  const sectionTableOffset = optionalHeaderOffset + optionalHeaderSize;
  const sections: PeSection[] = [];

  for (let index = 0; index < numberOfSections; index++) {
    const sectionOffset = sectionTableOffset + index * 40;
    if (sectionOffset + 40 > data.length) {
      throw new Error("PE section table extends beyond file size.");
    }

    sections.push({
      name: data
        .toString("ascii", sectionOffset, sectionOffset + 8)
        .replace(/\0.*$/, "")
        .trim(),
      virtualSize: data.readUInt32LE(sectionOffset + 8),
      virtualAddress: data.readUInt32LE(sectionOffset + 12),
      rawSize: data.readUInt32LE(sectionOffset + 16),
      rawPointer: data.readUInt32LE(sectionOffset + 20)
    });
  }

  return { imageBase, sections };
}

function sectionToSummary(section: PeSection): AddressConversionSection {
  return {
    name: section.name,
    virtualAddressHex: toHex(section.virtualAddress),
    virtualSizeHex: toHex(section.virtualSize),
    rawPointerHex: toHex(section.rawPointer),
    rawSizeHex: toHex(section.rawSize)
  };
}

async function resolveRepoRoot(appPath: string) {
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
      // Try the next known dev/packaged root.
    }
  }
  return path.resolve(process.cwd());
}

function settingsPath(settingsRoot: string) {
  return path.join(path.resolve(settingsRoot), settingsFileName);
}

async function readSettings(settingsRoot: string): Promise<WorkbenchSettings> {
  try {
    const raw = await fs.readFile(settingsPath(settingsRoot), "utf8");
    const parsed = JSON.parse(raw) as WorkbenchSettings;
    return typeof parsed.gameRoot === "string" && parsed.gameRoot.trim().length > 0
      ? { gameRoot: path.resolve(parsed.gameRoot) }
      : {};
  } catch {
    return {};
  }
}

async function writeSettings(settingsRoot: string, settings: WorkbenchSettings) {
  const normalized: WorkbenchSettings = {};
  if (settings.gameRoot) {
    normalized.gameRoot = path.resolve(settings.gameRoot);
  }

  await fs.mkdir(path.resolve(settingsRoot), { recursive: true });
  await fs.writeFile(settingsPath(settingsRoot), `${JSON.stringify(normalized, null, 2)}\n`, "utf8");
}

async function assertDirectory(targetPath: string, label: string) {
  const stat = await fs.stat(targetPath);
  if (!stat.isDirectory()) {
    throw new Error(`${label} is not a directory.`);
  }
}

async function statusOf(label: string, targetPath: string, role: string): Promise<ToolPathStatus> {
  try {
    const stat = await fs.stat(targetPath);
    return {
      label,
      path: targetPath,
      exists: true,
      kind: stat.isDirectory() ? "directory" : "file",
      role
    };
  } catch {
    return {
      label,
      path: targetPath,
      exists: false,
      kind: "missing",
      role
    };
  }
}

async function gameStatus(
  label: string,
  targetPath: string,
  required: boolean,
  role: string
): Promise<GameHarnessFileStatus> {
  try {
    await fs.stat(targetPath);
    return { label, path: targetPath, exists: true, required, role };
  } catch {
    return { label, path: targetPath, exists: false, required, role };
  }
}

function pathExists(paths: ToolPathStatus[], label: string) {
  return paths.some((item) => item.label === label && item.exists);
}

function commandReady(commands: PlannedCommand[], label: string) {
  return commands.some((command) => command.label === label && command.status === "ready");
}

async function hasRequiredAssetCatalogInputs(repoRoot: string) {
  const requiredPaths = [
    path.join(repoRoot, "tools", "export_asset_catalog.py"),
    path.join(repoRoot, "subagents", "aya_asset_manifest_wave5_2026-03-13.json"),
    path.join(repoRoot, "subagents", "asset_export_wave1_2026-03-13", "loose_textures", "manifest.json"),
    path.join(repoRoot, "subagents", "asset_export_wave1_2026-03-13", "loose_meshes", "manifest.json"),
    path.join(repoRoot, "subagents", "asset_export_wave1_2026-03-13", "embedded_meshes", "manifest.json"),
    path.join(repoRoot, "subagents", "video_manifest_wave1_2026-03-13", "manifest.json"),
    path.join(repoRoot, "subagents", "language_export_wave1_2026-03-13", "merged_matrix.json")
  ];

  const statuses = await Promise.all(
    requiredPaths.map(async (targetPath) => {
      try {
        await fs.access(targetPath);
        return true;
      } catch {
        return false;
      }
    })
  );
  return statuses.every(Boolean);
}

async function hasFile(targetPath: string) {
  try {
    const stat = await fs.stat(targetPath);
    return stat.isFile();
  } catch {
    return false;
  }
}

function parseNonNegativeInteger(value: string | number, label: string) {
  const parsed =
    typeof value === "number"
      ? value
      : value.trim().toLowerCase().startsWith("0x")
        ? Number.parseInt(value.trim().slice(2), 16)
        : Number.parseInt(value.trim(), 10);
  if (!Number.isSafeInteger(parsed) || parsed < 0) {
    throw new Error(`Invalid ${label}: ${String(value)}`);
  }
  return parsed;
}

function toHex(value: number) {
  return `0x${value.toString(16).toUpperCase()}`;
}

async function writeHexArtifact(summary: HexReadSummary, artifactRoot: string): Promise<HexReadSummary> {
  const jobId = buildJobId(summary.readAt, summary.sha256, "hex");
  const artifactDir = path.join(path.resolve(artifactRoot), "artifacts", "hex-read", jobId);
  const artifactPath = path.join(artifactDir, "hex-read.json");
  const summaryWithArtifact: HexReadSummary = {
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
    generatedAt: summary.readAt,
    mutation: false,
    input: {
      selectedPath: summary.selectedPath,
      fileName: summary.fileName,
      fileSize: summary.fileSize,
      sha256: summary.sha256,
      offset: summary.offset,
      requestedLength: summary.requestedLength
    },
    result: summaryWithArtifact
  };

  await fs.mkdir(artifactDir, { recursive: true });
  await fs.writeFile(artifactPath, `${JSON.stringify(record, null, 2)}\n`, "utf8");
  return summaryWithArtifact;
}

function buildJobId(timestamp: string, sha256: string, prefix: string) {
  const compactTimestamp = timestamp.replace(/\D/g, "").slice(0, 14);
  return `${prefix}-${compactTimestamp}-${sha256.slice(0, 8)}`;
}
