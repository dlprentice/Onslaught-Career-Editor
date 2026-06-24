import {
  browserAddressConversion,
  browserContentDocument,
  browserContentIndex,
  browserDebugReadiness,
  browserGameHarnessProfile,
  browserGhidraReadiness,
  browserHexRead,
  browserJobCatalog,
  browserJobRun,
  browserJobRuns,
  browserMediaCatalog,
  browserReleasePolicy,
  browserSaveComparison,
  browserSaveInspection,
  browserSnapshot,
  browserSpecimenVerification
} from "@/lib/mock-data";
import type { ContentIndexSummary, OnslaughtApi, WorkbenchJobProgressEvent } from "@/types/onslaught-api";

const browserProgressHandlers = new Set<(event: WorkbenchJobProgressEvent) => void>();
const browserPreviewPixelPng = [
  "data:image/png;base64,",
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwC",
  "AAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
].join("");

function emitBrowserJobProgress(event: WorkbenchJobProgressEvent) {
  for (const handler of browserProgressHandlers) {
    handler(event);
  }
}

const browserOptionCareerInputs = [
  "soundVolume",
  "musicVolume",
  "invertWalkerP1",
  "invertWalkerP2",
  "invertFlightP1",
  "invertFlightP2",
  "vibrationP1",
  "vibrationP2",
  "controllerConfigP1",
  "controllerConfigP2"
];

const browserOptionTailInputs = [
  "mouseSensitivity",
  "controlSchemeIndex",
  "languageIndex",
  "screenShape",
  "d3dDeviceIndex"
];

function browserInputProvided(inputs: Record<string, unknown>, name: string) {
  const value = inputs[name];
  return value !== null && typeof value !== "undefined" && value !== "";
}

function browserInputCount(inputs: Record<string, unknown>, names: string[]) {
  return names.filter((name) => browserInputProvided(inputs, name)).length;
}

function browserKeybindRowCount(inputs: Record<string, unknown>) {
  const value = inputs.keybindOverrides;
  if (typeof value !== "string" || value.trim().length === 0) {
    return 0;
  }
  return value.split(/[;\n]+/).filter((row) => row.trim().length > 0).length;
}

function browserOptionsPatchStats(inputs: Record<string, unknown>) {
  const settingsOverrideCount = browserInputCount(inputs, browserOptionCareerInputs);
  const tailOverrideCount = browserInputCount(inputs, browserOptionTailInputs);
  const keybindOverrideCount = browserKeybindRowCount(inputs);
  const copySourceActive = browserInputProvided(inputs, "copyOptionsFromPath");
  const sections = [
    settingsOverrideCount > 0 ? "career-settings" : null,
    copySourceActive ? "options-copy" : null,
    tailOverrideCount > 0 ? "options-tail" : null,
    keybindOverrideCount > 0 ? "keybinds" : null
  ].filter((section): section is string => Boolean(section));

  return {
    sections: sections.join(", ") || "none",
    settingsOverrideCount,
    tailOverrideCount,
    keybindOverrideCount,
    copyOptionsEntries: copySourceActive && inputs.copyOptionsEntries !== false,
    copyOptionsTail: copySourceActive && inputs.copyOptionsTail !== false
  };
}

const browserApi: OnslaughtApi = {
  getRuntimeSnapshot: async () => ({
    ...browserSnapshot,
    generatedAt: new Date().toISOString()
  }),
  selectAndVerifyExecutable: async () => ({
    ...browserSpecimenVerification,
    verifiedAt: new Date().toISOString()
  }),
  verifyExecutablePath: async () => ({
    ...browserSpecimenVerification,
    verifiedAt: new Date().toISOString()
  }),
  selectAndInspectSaveFile: async () => ({
    ...browserSaveInspection,
    inspectedAt: new Date().toISOString()
  }),
  inspectSaveFilePath: async () => ({
    ...browserSaveInspection,
    inspectedAt: new Date().toISOString()
  }),
  selectAndCompareSaveFiles: async () => ({
    ...browserSaveComparison,
    comparedAt: new Date().toISOString()
  }),
  compareSaveFilePaths: async () => ({
    ...browserSaveComparison,
    comparedAt: new Date().toISOString()
  }),
  selectAndReadHexFile: async () => ({
    ...browserHexRead,
    readAt: new Date().toISOString()
  }),
  readHexRange: async () => ({
    ...browserHexRead,
    readAt: new Date().toISOString()
  }),
  convertExecutableAddress: async () => ({
    ...browserAddressConversion,
    convertedAt: new Date().toISOString()
  }),
  getGhidraReadiness: async () => ({
    ...browserGhidraReadiness,
    checkedAt: new Date().toISOString()
  }),
  getDebugReadiness: async () => ({
    ...browserDebugReadiness,
    checkedAt: new Date().toISOString()
  }),
  getGameHarnessProfile: async () => ({
    ...browserGameHarnessProfile,
    checkedAt: new Date().toISOString()
  }),
  selectAndInspectGameFolder: async () => ({
    ...browserGameHarnessProfile,
    checkedAt: new Date().toISOString(),
    profileSource: "selected"
  }),
  inspectGameFolderPath: async (gameRoot: string) => ({
    ...browserGameHarnessProfile,
    checkedAt: new Date().toISOString(),
    gameRoot,
    workingDirectory: gameRoot,
    executablePath: `${gameRoot}\\BEA.exe`,
    profileSource: "selected"
  }),
  resetGameFolderProfile: async () => ({
    ...browserGameHarnessProfile,
    checkedAt: new Date().toISOString(),
    profileSource: "repo-default"
  }),
  getJobCatalog: async () => ({
    ...browserJobCatalog,
    generatedAt: new Date().toISOString()
  }),
  startWorkbenchJob: async (request) => {
    const definition = browserJobCatalog.definitions.find((candidate) => candidate.id === request.definitionId);
    const runId = `browser-job-${Date.now()}`;
    const startedAt = new Date().toISOString();
    const progress: WorkbenchJobProgressEvent[] = [
      {
        runId,
        definitionId: request.definitionId,
        phase: "queued",
        percent: 5,
        message: "Preview mode accepted the job.",
        emittedAt: startedAt
      },
      {
        runId,
        definitionId: request.definitionId,
        phase: "running",
        percent: 45,
        message: "Preview mode is simulating the typed runner.",
        emittedAt: new Date().toISOString()
      },
      {
        runId,
        definitionId: request.definitionId,
        phase: "completed",
        percent: 100,
        message: "Preview mode completed the job.",
        emittedAt: new Date().toISOString()
      }
    ];
    progress.forEach(emitBrowserJobProgress);
    return {
      ...browserJobRun,
      runId,
      definitionId: request.definitionId,
      title: definition?.title ?? "Preview mode job",
      lane: definition?.lane ?? "content",
      safety: definition?.safety ?? "read-only",
      startedAt,
      finishedAt: new Date().toISOString(),
      inputs: request.inputs,
      policy: definition?.policy ?? browserJobRun.policy,
      progress,
      result: browserJobResultFor(request.definitionId, request.inputs),
      artifact: {
        ...browserJobRun.artifact,
        kind:
          definition?.id === "save.applyPatch" ||
          definition?.id === "save.restoreBackup" ||
          definition?.id === "settings.applyOptionsPatch" ||
          definition?.id === "patch.applyCatalogPatch" ||
          definition?.id === "patch.restoreCatalogBackup"
            ? "local-file-write"
            : definition?.id === "game.prepareSafeProfile" ||
                definition?.id === "save.prepareCopy" ||
                definition?.id === "patch.prepareExecutableCopy"
            ? "local-file-copy"
            : definition?.safety === "launch-gated"
              ? "external-process"
              : "read-only",
        mutation:
          definition?.id === "save.applyPatch" ||
          definition?.id === "save.restoreBackup" ||
          definition?.id === "settings.applyOptionsPatch" ||
          definition?.id === "patch.applyCatalogPatch" ||
          definition?.id === "patch.restoreCatalogBackup" ||
          definition?.id === "game.prepareSafeProfile" ||
          definition?.id === "save.prepareCopy" ||
          definition?.id === "patch.prepareExecutableCopy"
      }
    };
  },
  cancelWorkbenchJob: async () => false,
  onWorkbenchJobProgress: (handler) => {
    browserProgressHandlers.add(handler);
    return () => browserProgressHandlers.delete(handler);
  },
  getWorkbenchJobRun: async (runId: string) => ({
    ...browserJobRun,
    runId
  }),
  listWorkbenchJobRuns: async () =>
    browserJobRuns.map((run) => ({
      ...run,
      startedAt: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
      finishedAt: new Date(Date.now() - 1000 * 60 * 4 + run.durationMs).toISOString()
    })),
  getMediaCatalog: async (query = "", kind = "all", limit = 80) => {
    const normalizedQuery = query.trim().toLowerCase();
    const filteredRows = browserMediaCatalog.rows.filter((row) => {
      const matchesKind = kind === "all" || row.kind === kind;
      const matchesQuery =
        !normalizedQuery ||
        [
          row.id,
          row.kind,
          row.label,
          row.group,
          row.videoFamily,
          row.sequenceId,
          row.codec,
          row.playbackStatus,
          row.playbackNote,
          row.videoPlaybackId,
          row.sourcePath,
          row.exportPath,
          row.sha256,
          row.detail
        ]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(normalizedQuery));
      return matchesKind && matchesQuery;
    });
    const rows = filteredRows.slice(0, Math.max(1, Math.min(250, Math.trunc(limit || 80))));
    return {
      ...browserMediaCatalog,
      generatedAt: new Date().toISOString(),
      query,
      kind,
      totalRows: filteredRows.length,
      returnedRows: rows.length,
      truncated: filteredRows.length > rows.length,
      rows
    };
  },
  getAudioPlayback: async (playbackId: string) => {
    const row = browserMediaCatalog.rows.find((candidate) => candidate.playbackId === playbackId);
    if (!row?.playbackId || !row.sourcePath) {
      throw new Error("Unknown preview-mode audio playback id.");
    }
    return {
      generatedAt: new Date().toISOString(),
      playbackId: row.playbackId,
      label: row.label,
      group: row.group,
      sourcePath: row.sourcePath,
      sizeBytes: row.sizeBytes ?? 44,
      mimeType: "audio/wav" as const,
      dataUrl:
        "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQAAAAA=",
      artifact: {
        kind: "read-only" as const,
        mutation: false as const,
        schemaVersion: "audio-playback.v1" as const,
        note: "Preview mode audio payload. Desktop app mode reads one cataloged OGG under the selected game root."
      }
    };
  },
  prepareVideoPlayback: async (playbackId: string, options = {}) => {
    const row = browserMediaCatalog.rows.find((candidate) => candidate.videoPlaybackId === playbackId);
    if (!row?.videoPlaybackId || !row.sourcePath) {
      throw new Error("Unknown preview-mode video playback id.");
    }
    const dryRun = options.dryRun === true;
    const cacheStatus = dryRun ? ("dry-run" as const) : ("created" as const);
    return {
      generatedAt: new Date().toISOString(),
      playbackId: row.videoPlaybackId,
      label: row.label,
      group: row.group,
      sourcePath: `C:\\Games\\Battle Engine Aquila\\data\\video\\${row.sourcePath}`,
      sizeBytes: row.sizeBytes ?? 1_586_724,
      codec: row.codec ?? "BIKi",
      mode: "inline-transcoded" as const,
      dryRun,
      launched: false,
      mimeType: "video/mp4" as const,
      playbackUrl: dryRun ? undefined : "browser://fixture/media-cache/video/pc_100_exact.mp4",
      cachePath: dryRun ? undefined : "browser://fixture/media-cache/video/pc_100_exact.mp4",
      cacheStatus,
      player: {
        kind: "vlc" as const,
        path: "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
        available: true,
        detail: "Preview mode transcode backend. Desktop app mode writes an app-owned MP4 cache before playback."
      },
      commandPreview: `"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" "--intf" "dummy" "--play-and-exit" "${row.sourcePath}" "--sout" "#transcode{vcodec=h264,acodec=mp4a}:std{access=file,mux=mp4,dst=pc_100_exact.mp4}"`,
      artifact: {
        kind: dryRun ? ("read-only" as const) : ("local-file-write" as const),
        mutation: false as const,
        schemaVersion: "video-playback.v1" as const,
        note: dryRun
          ? "Preview mode dry-run for in-app video preparation."
          : "Preview mode simulated an app-owned transcode cache without opening an external player."
      }
    };
  },
  openVideoPlayback: async (playbackId: string, options = {}) => {
    const row = browserMediaCatalog.rows.find((candidate) => candidate.videoPlaybackId === playbackId);
    if (!row?.videoPlaybackId || !row.sourcePath) {
      throw new Error("Unknown preview-mode video playback id.");
    }
    const dryRun = options.dryRun === true;
    return {
      generatedAt: new Date().toISOString(),
      playbackId: row.videoPlaybackId,
      label: row.label,
      group: row.group,
      sourcePath: `C:\\Games\\Battle Engine Aquila\\data\\video\\${row.sourcePath}`,
      sizeBytes: row.sizeBytes ?? 1_586_724,
      codec: row.codec ?? "BIKi",
      mode: "external-vlc" as const,
      dryRun,
      launched: !dryRun,
      processId: dryRun ? undefined : 42420,
      player: {
        kind: "vlc" as const,
        path: "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
        available: true,
        detail: "Preview mode VLC player. Desktop app mode resolves an installed VLC executable."
      },
      commandPreview: `"C:\\Program Files\\VideoLAN\\VLC\\vlc.exe" "--started-from-file" "--no-video-title-show" "C:\\Games\\Battle Engine Aquila\\data\\video\\${row.sourcePath}"`,
      artifact: {
        kind: "external-process" as const,
        mutation: false as const,
        schemaVersion: "video-playback.v1" as const,
        note: dryRun
          ? "Preview mode dry-run for a typed video playback request."
          : "Preview mode simulated a typed VLC playback request without opening a real player."
      }
    };
  },
  getMediaPreview: async (previewId: string) => {
    const row = browserMediaCatalog.rows.find((candidate) => candidate.previewId === previewId);
    if (!row?.previewId || !row.exportPath) {
      throw new Error("Unknown preview-mode media preview id.");
    }
    return {
      generatedAt: new Date().toISOString(),
      previewId: row.previewId,
      label: row.label,
      group: row.group,
      sourcePath: row.sourcePath,
      exportPath: row.exportPath,
      sizeBytes: 68,
      mimeType: "image/png" as const,
      dataUrl: browserPreviewPixelPng,
      artifact: {
        kind: "read-only" as const,
        mutation: false as const,
        schemaVersion: "media-preview.v1" as const,
        note: "Preview mode PNG preview. Desktop app mode resolves the preview id through the generated media catalog."
      }
    };
  },
  getContentIndex: async () => ({
    ...browserContentIndex,
    generatedAt: new Date().toISOString()
  }),
  readContentDocument: async (id: string) => {
    const item = browserContentIndex.items.find((candidate) => candidate.id === id) ?? browserContentIndex.items[0];
    return {
      ...browserContentDocument,
      id: item.id,
      title: item.title,
      group: item.group,
      relativePath: item.relativePath,
      communitySafe: item.communitySafe,
      audience: item.communitySafe ? "community" : "maintainer",
      readAt: new Date().toISOString(),
      markdown: browserMarkdownForContentItem(item)
    };
  },
  getReleasePolicy: async () => ({
    ...browserReleasePolicy,
    generatedAt: new Date().toISOString()
  }),
  openExternal: async (url: string) => {
    window.open(url, "_blank", "noopener,noreferrer");
  }
};

export function getOnslaughtApi(): OnslaughtApi {
  return window.onslaughtApi ?? browserApi;
}

const browserStablePatchIds =
  "resolution_gate, force_windowed, extra_graphics_default_on, ignore_cardid_tweak_overrides, version_overlay_use_patched_format_pointer, version_overlay_patched_format_cave_string";

function browserMarkdownForContentItem(item: ContentIndexSummary["items"][number]) {
  if (item.id === "lore-book") {
    return [
      "# Lore book",
      "",
      "A curated entry point for Battle Engine Aquila preservation material.",
      "",
      "- [Roadmap Index](roadmap/ROADMAP-INDEX.md)",
      "- [AYA Tags](reverse-engineering/quick-reference/aya-tags.md)",
      "- [Start Here](Start-Here.md)",
      "",
      "Browser preview mode renders a compact sample document. The desktop app opens the curated markdown file from disk."
    ].join("\n");
  }

  if (item.id === "community-preservation") {
    return [
      "# Community preservation",
      "",
      "Community resources and preservation context for Battle Engine Aquila.",
      "",
      "| Resource | Link |",
      "| --- | --- |",
      "| Speedrun.com | [speedrun.com/battle_engine_aquila](https://www.speedrun.com/battle_engine_aquila) |"
    ].join("\n");
  }

  if (item.id === "aya-tags") {
    return [
      "# AYA tags quick reference",
      "",
      "- [Texture Tags](#texture-tags)",
      "- [Mesh Part Tags](#mesh-part-tags)",
      "",
      "## Texture Tags",
      "",
      "Texture chunks are used while cataloging packed resources.",
      "",
      "## Mesh Part Tags",
      "",
      "Mesh tags help maintainers identify geometry-related chunks."
    ].join("\n");
  }

  if (item.id === "electron-migration") {
    return `# ${item.title}\n\n${item.description}\n\nThe workbench records durable artifacts while keeping app chrome friendly.`;
  }

  return `# ${item.title}\n\n${item.description}\n\nPreview mode shows sample reading text for this document. The desktop app opens the curated markdown file from disk.`;
}
const browserAllPatchIds = `${browserStablePatchIds}, skip_auto_toggle`;

function browserPatchIdsLabel(inputs: Record<string, unknown>) {
  const rawPatchIds = typeof inputs.patchIds === "string" ? inputs.patchIds.trim() : "";
  if (!rawPatchIds || rawPatchIds === "stable") return browserStablePatchIds;
  if (rawPatchIds === "all") return browserAllPatchIds;
  return rawPatchIds;
}

function browserPatchCount(inputs: Record<string, unknown>) {
  const label = browserPatchIdsLabel(inputs);
  if (label === "stable") return "6";
  if (label === "all") return "7";
  return String(label.split(/[\s,;]+/).filter(Boolean).length);
}

function browserJobResultFor(definitionId: string, inputs: Record<string, unknown> = {}) {
  if (definitionId === "appcore.inspectSave") {
    return {
      summary: "Preview mode inspected haha-cannon-goes-brrrrr.bes through the AppCore host boundary.",
      payloadSchema: "appcore-save-analysis.v1",
      details: [
        { label: "Host project", value: "OnslaughtCareerEditor.AppCore.Host" },
        { label: "File", value: "haha-cannon-goes-brrrrr.bes" },
        { label: "Valid", value: "yes" },
        { label: "Kind", value: "career save" },
        { label: "Version", value: "0x4BD1 (valid)" },
        { label: "Missions", value: "43/43" },
        { label: "Goodies", value: "232/233" },
        { label: "Kill total", value: "20,938" },
        { label: "AppCore artifact", value: "browser://fixture/appcore-save-analysis/analysis.json" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "appcore.compareSaves") {
    return {
      summary: "Preview mode compared the gold save against itself through the AppCore host boundary.",
      payloadSchema: "appcore-save-comparison.v1",
      details: [
        { label: "Host project", value: "OnslaughtCareerEditor.AppCore.Host" },
        { label: "Left", value: "haha-cannon-goes-brrrrr.bes" },
        { label: "Right", value: "haha-cannon-goes-brrrrr.bes" },
        { label: "Same size", value: "yes" },
        { label: "Identical", value: "yes" },
        { label: "Differing bytes", value: "0" },
        { label: "Ranges", value: "0" },
        { label: "Top region", value: "none" },
        { label: "AppCore artifact", value: "browser://fixture/appcore-save-comparison/comparison.json" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "save.planPatch") {
    return {
      summary: "Preview mode planned the save patch through the native TypeScript patcher; source unchanged.",
      payloadSchema: "save-patch-plan.v1",
      details: [
        { label: "File", value: "haha-cannon-goes-brrrrr.bes" },
        { label: "Target kind", value: "career-save" },
        { label: "Rank", value: "S" },
        { label: "Kill count", value: "100" },
        { label: "Sections", value: "nodes, links, goodies, kills" },
        { label: "Level ranks", value: "2" },
        { label: "Per-category kills", value: "2" },
        { label: "Current kills", value: "20938" },
        { label: "Requires copied apply", value: "yes" },
        { label: "Source unchanged", value: "yes" },
        { label: "Plan artifact", value: "browser://fixture/save-patch-plan/plan.json" }
      ]
    };
  }

  if (definitionId === "save.prepareCopy") {
    const sourcePath = typeof inputs.sourcePath === "string" ? inputs.sourcePath : "save-attempts\\haha-cannon-goes-brrrrr.bes";
    const isOptionsCopy = sourcePath.toLowerCase().endsWith(".bea") || sourcePath.toLowerCase().includes("defaultoptions");
    const fileName = isOptionsCopy ? "defaultoptions.bea" : "haha-cannon-goes-brrrrr.bes";
    return {
      summary: `Preview mode copied ${isOptionsCopy ? "the options file" : "the save"} into the app workspace; source unchanged and read-back verification succeeded.`,
      payloadSchema: "save-copy.v1",
      details: [
        { label: "Source", value: sourcePath },
        { label: "Copied target", value: `browser://fixture/${isOptionsCopy ? "copied-options" : "copied-saves"}/${fileName}` },
        { label: "Kind", value: isOptionsCopy ? "options/defaultoptions" : "career save" },
        { label: "Version", value: "0x4BD1 (valid)" },
        { label: "Goodies", value: isOptionsCopy ? "n/a" : "233" },
        { label: "Kill total", value: isOptionsCopy ? "n/a" : "815" },
        { label: "Read-back verified", value: "yes" },
        { label: "Copy artifact", value: `browser://fixture/save-copy/${isOptionsCopy ? "defaultoptions" : "save"}/copy.json` }
      ]
    };
  }

  if (definitionId === "save.previewPatch") {
    return {
      summary: "Preview mode previewed the save patch through the native TypeScript patcher; source unchanged.",
      payloadSchema: "save-patch-preview.v1",
      details: [
        { label: "File", value: "haha-cannon-goes-brrrrr.bes" },
        { label: "Rank", value: "S" },
        { label: "Kill count", value: "100" },
        { label: "Sections", value: "nodes, links, goodies, kills" },
        { label: "Would change", value: "yes" },
        { label: "Differing bytes", value: "14" },
        { label: "Top region", value: "Kills[Aircraft]: 3" },
        { label: "Goodies", value: "232 -> 233" },
        { label: "Kill total", value: "20938 -> 500" },
        { label: "Source unchanged", value: "yes" },
        { label: "Candidate artifact", value: "browser://fixture/save-patch-preview/candidate.bes" },
        { label: "Preview artifact", value: "browser://fixture/save-patch-preview/preview.json" }
      ]
    };
  }

  if (definitionId === "save.applyPatch") {
    const targetPath = typeof inputs.path === "string" && inputs.path ? inputs.path : "browser://fixture/copied-saves/haha-cannon-goes-brrrrr.bes";
    const backupPath = targetPath.toLowerCase().includes("haha-cannon-goes-brrrrr.bes")
      ? "browser://fixture/save-patch-apply/backup/haha-cannon-goes-brrrrr.bes.bak"
      : `${targetPath}.bak`;
    return {
      summary: "Preview mode applied the TypeScript save patch to an artifact-root copied save; backup and read-back verification succeeded.",
      payloadSchema: "save-patch-apply.v1",
      details: [
        { label: "Target", value: targetPath },
        { label: "Rank", value: "S" },
        { label: "Kill count", value: "100" },
        { label: "Sections", value: "nodes, links, goodies, kills" },
        { label: "Changed", value: "yes" },
        { label: "Differing bytes", value: "14" },
        { label: "Top region", value: "Kills[Aircraft]: 3" },
        { label: "Backup", value: backupPath },
        { label: "Read-back verified", value: "yes" },
        { label: "Apply artifact", value: "browser://fixture/save-patch-apply/apply.json" }
      ]
    };
  }

  if (definitionId === "save.restoreBackup") {
    const targetPath =
      typeof inputs.targetPath === "string" && inputs.targetPath
        ? inputs.targetPath
        : "browser://fixture/copied-saves/haha-cannon-goes-brrrrr.bes";
    const isOptionsRestore = targetPath.toLowerCase().endsWith(".bea") || targetPath.toLowerCase().includes("defaultoptions");
    const backupPath =
      typeof inputs.backupPath === "string" && inputs.backupPath
        ? inputs.backupPath
        : isOptionsRestore
          ? "browser://fixture/options-patch-apply/backup/defaultoptions.bea.bak"
          : "browser://fixture/save-patch-apply/backup/haha-cannon-goes-brrrrr.bes.bak";
    const preRestoreName = isOptionsRestore ? "defaultoptions.bea.pre-restore.bak" : "haha-cannon-goes-brrrrr.bes.pre-restore.bak";
    const artifactFolder = isOptionsRestore ? "options-patch-restore" : "save-patch-restore";
    return {
      summary: `Preview mode restored an artifact-root ${isOptionsRestore ? "options" : "save"} backup to a copied target and retained a pre-restore backup.`,
      payloadSchema: "save-patch-restore.v1",
      details: [
        { label: "Target", value: targetPath },
        { label: "Backup", value: backupPath },
        { label: "Pre-restore backup", value: `browser://fixture/${artifactFolder}/pre-restore/${preRestoreName}` },
        { label: "Read-back verified", value: "yes" },
        { label: "Target SHA-256", value: isOptionsRestore ? "browser-fixture-restored-options-hash" : "browser-fixture-restored-save-hash" },
        { label: "Restore artifact", value: `browser://fixture/${artifactFolder}/restore.json` }
      ]
    };
  }

  if (definitionId === "settings.planOptionsPatch") {
    const stats = browserOptionsPatchStats(inputs);
    return {
      summary: "Preview mode planned the defaultoptions patch through the native TypeScript patcher; source unchanged.",
      payloadSchema: "options-patch-plan.v1",
      details: [
        { label: "File", value: "defaultoptions.bea" },
        { label: "Target kind", value: "global-options" },
        { label: "Sections", value: stats.sections },
        { label: "Settings overrides", value: String(stats.settingsOverrideCount) },
        { label: "Tail overrides", value: String(stats.tailOverrideCount) },
        { label: "Keybind rows", value: String(stats.keybindOverrideCount) },
        { label: "Copy entries", value: stats.copyOptionsEntries ? "yes" : "no" },
        { label: "Copy tail", value: stats.copyOptionsTail ? "yes" : "no" },
        { label: "Requires copied apply", value: "yes" },
        { label: "Source unchanged", value: "yes" },
        { label: "Plan artifact", value: "browser://fixture/options-patch-plan/plan.json" }
      ]
    };
  }

  if (definitionId === "settings.previewOptionsPatch") {
    const stats = browserOptionsPatchStats(inputs);
    const differingBytes = 8 + stats.settingsOverrideCount * 4 + stats.tailOverrideCount * 4 + stats.keybindOverrideCount * 8;
    return {
      summary: "Preview mode previewed the defaultoptions patch through the native TypeScript patcher; source unchanged.",
      payloadSchema: "options-patch-preview.v1",
      details: [
        { label: "File", value: "defaultoptions.bea" },
        { label: "Sections", value: stats.sections },
        { label: "Would change", value: "yes" },
        { label: "Differing bytes", value: String(differingBytes) },
        { label: "Top region", value: stats.tailOverrideCount > 0 ? "OptionsTail: 20" : "OptionsEntries: 16" },
        { label: "Sound", value: `1 -> ${inputs.soundVolume ?? "preserve"}` },
        { label: "Music", value: `1 -> ${inputs.musicVolume ?? "preserve"}` },
        { label: "Control scheme", value: `1 -> ${inputs.controlSchemeIndex ?? "preserve"}` },
        { label: "Keybind rows", value: String(stats.keybindOverrideCount) },
        { label: "Source unchanged", value: "yes" },
        { label: "Candidate artifact", value: "browser://fixture/options-patch-preview/candidate.bea" },
        { label: "Preview artifact", value: "browser://fixture/options-patch-preview/preview.json" }
      ]
    };
  }

  if (definitionId === "settings.applyOptionsPatch") {
    const targetPath =
      typeof inputs.path === "string" && inputs.path ? inputs.path : "browser://fixture/copied-options/defaultoptions.bea";
    const backupPath = targetPath.toLowerCase().includes("defaultoptions.bea")
      ? "browser://fixture/options-patch-apply/backup/defaultoptions.bea.bak"
      : `${targetPath}.bak`;
    const stats = browserOptionsPatchStats(inputs);
    const differingBytes = 8 + stats.settingsOverrideCount * 4 + stats.tailOverrideCount * 4 + stats.keybindOverrideCount * 8;
    return {
      summary: "Preview mode applied the TypeScript global-options patch to an artifact-root copied file; backup and read-back verification succeeded.",
      payloadSchema: "options-patch-apply.v1",
      details: [
        { label: "Target", value: targetPath },
        { label: "Sections", value: stats.sections },
        { label: "Changed", value: "yes" },
        { label: "Differing bytes", value: String(differingBytes) },
        { label: "Top region", value: stats.tailOverrideCount > 0 ? "OptionsTail: 20" : "OptionsEntries: 16" },
        { label: "Sound", value: `1 -> ${inputs.soundVolume ?? "preserve"}` },
        { label: "Music", value: `1 -> ${inputs.musicVolume ?? "preserve"}` },
        { label: "Control scheme", value: `1 -> ${inputs.controlSchemeIndex ?? "preserve"}` },
        { label: "Backup", value: backupPath },
        { label: "Read-back verified", value: "yes" },
        { label: "Apply artifact", value: "browser://fixture/options-patch-apply/apply.json" }
      ]
    };
  }

  if (definitionId === "appcore.planSavePatch") {
    return {
      summary: "Preview mode wrote a typed AppCore patch request JSON and validated a read-only save patch plan.",
      payloadSchema: "appcore-save-patch-plan.v1",
      details: [
        { label: "Host project", value: "OnslaughtCareerEditor.AppCore.Host" },
        { label: "File", value: "haha-cannon-goes-brrrrr.bes" },
        { label: "Target kind", value: "career-save" },
        { label: "Rank", value: "S" },
        { label: "Kill count", value: "100" },
        { label: "Sections", value: "nodes, links, goodies, kills" },
        { label: "Level ranks", value: "2" },
        { label: "Per-category kills", value: "2" },
        { label: "Current kills", value: "20938" },
        { label: "Requires copied apply", value: "yes" },
        { label: "Source unchanged", value: "yes" },
        { label: "Request artifact", value: "browser://fixture/appcore-save-patch-plan/request.json" },
        { label: "Plan artifact", value: "browser://fixture/appcore-save-patch-plan/plan.json" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "appcore.previewSavePatch") {
    return {
      summary: "Preview mode previewed the standard AppCore save patch on a temporary copy; source unchanged.",
      payloadSchema: "appcore-save-patch-preview.v1",
      details: [
        { label: "Host project", value: "OnslaughtCareerEditor.AppCore.Host" },
        { label: "File", value: "haha-cannon-goes-brrrrr.bes" },
        { label: "Rank", value: "S" },
        { label: "Kill count", value: "100" },
        { label: "Sections", value: "nodes, links, goodies, kills" },
        { label: "Would change", value: "yes" },
        { label: "Differing bytes", value: "14" },
        { label: "Top region", value: "Kills: 10" },
        { label: "Goodies", value: "232 -> 233" },
        { label: "Kill total", value: "20938 -> 500" },
        { label: "Temp copy deleted", value: "yes" },
        { label: "Preview artifact", value: "browser://fixture/appcore-save-patch-preview/preview.json" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "file.peAddressConvert") {
    return {
      summary: "Preview mode converted 0x00529696 to .text file offset 0x129696.",
      payloadSchema: "address-conversion.v1",
      details: [
        { label: "Image base", value: "0x400000" },
        { label: "Virtual address", value: "0x529696" },
        { label: "RVA", value: "0x129696" },
        { label: "File offset", value: "0x129696" },
        { label: "Section", value: ".text" }
      ]
    };
  }

  if (definitionId === "debug.resolveCdb") {
    return {
      summary: "Preview mode resolved cdb.exe through the allowlisted helper boundary.",
      payloadSchema: "debug-cdb-resolve.v1",
      details: [
        { label: "Helper", value: "tools/get_cdb_path.ps1" },
        { label: "CDB path", value: "C:\\Program Files\\WindowsApps\\Microsoft.WinDbg\\x86\\cdb.exe" },
        { label: "Exit code", value: "0" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "debug.planProbeSession") {
    return {
      summary: "Preview mode planned a CDB probe session without launching the game or debugger.",
      payloadSchema: "debug-probe-plan.v1",
      details: [
        { label: "Probe", value: "pause-persist-wave1.cdb.txt" },
        { label: "Command file", value: "tools\\runtime-probes\\pause-persist-wave1.cdb.txt" },
        { label: "Executable", value: "C:\\Games\\Battle Engine Aquila\\BEA.exe" },
        { label: "Port", value: "5005" },
        { label: "Log path", value: "browser://fixture/debug-probe-plan/cdb.log" },
        { label: "Known Steam hash", value: "yes" },
        { label: "Server command", value: "powershell -NoProfile -ExecutionPolicy Bypass -File tools\\start_cdb_server.ps1 -ProcessName BEA.exe -CommandFile tools\\runtime-probes\\pause-persist-wave1.cdb.txt" },
        { label: "Client command", value: "powershell -NoProfile -ExecutionPolicy Bypass -File tools\\connect_cdb_client.ps1 -Server 127.0.0.1 -Port 5005" },
        { label: "Plan artifact", value: "browser://fixture/debug-probe-plan/plan.json" }
      ]
    };
  }

  if (definitionId === "debug.startProbeServer") {
    return {
      summary: "Preview mode armed the CDB attach-server boundary and wrote a debug session artifact.",
      payloadSchema: "debug-session.v1",
      details: [
        { label: "Probe", value: "pause-persist-wave1.cdb.txt" },
        { label: "Process", value: "BEA.exe" },
        { label: "CDB PID", value: "4242" },
        { label: "Log path", value: "browser://fixture/debug-session/cdb.log" },
        { label: "Port", value: "5005" },
        { label: "Safe profile", value: "outside repo root" },
        { label: "Known Steam hash", value: "yes" },
        { label: "Session artifact", value: "browser://fixture/debug-session/session.json" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "runtime.listManagedProcesses") {
    return {
      summary: "Preview mode read 2 managed runtime process records.",
      payloadSchema: "managed-process-registry.v1",
      details: [
        { label: "Managed processes", value: "2" },
        { label: "Running", value: "2" },
        { label: "Exited", value: "0" },
        { label: "Stop requested", value: "0" },
        { label: "Latest", value: "game PID 31415 (running)" },
        { label: "Registry artifact", value: "browser://fixture/managed-process-registry/processes.json" }
      ]
    };
  }

  if (definitionId === "runtime.tailManagedLog") {
    return {
      summary: "Preview mode read 768 bytes from a managed debugger log tail.",
      payloadSchema: "managed-process-log-tail.v1",
      details: [
        { label: "Target run", value: "browser-job-debug-session" },
        { label: "Process", value: "cdb.exe (debugger)" },
        { label: "Process ID", value: "4242" },
        { label: "Status", value: "running" },
        { label: "Log path", value: "browser://fixture/debug-session/cdb.log" },
        { label: "Exists", value: "yes" },
        { label: "File size", value: "2048" },
        { label: "Tail bytes", value: "768" },
        { label: "Lines", value: "12" },
        { label: "Truncated", value: "yes" },
        { label: "Tail artifact", value: "browser://fixture/managed-process-log-tail/tail.json" },
        {
          label: "Tail text",
          value: "0:000> g\nBreakpoint 0 hit\nCCareer__Load flag=1\nCFEPOptions__WriteDefaultOptionsFile size=0x2714"
        }
      ]
    };
  }

  if (definitionId === "runtime.stopManagedProcess") {
    return {
      summary: "Preview mode requested stop for a recorded managed game process.",
      payloadSchema: "managed-process-stop.v1",
      details: [
        { label: "Target run", value: "browser-job-game-launch" },
        { label: "Process", value: "BEA.exe (game)" },
        { label: "Process ID", value: "31415" },
        { label: "Previous status", value: "running" },
        { label: "Current status", value: "stop-requested" },
        { label: "Stop requested", value: "yes" },
        { label: "Stop artifact", value: "browser://fixture/managed-process-stop/stop.json" }
      ]
    };
  }

  if (definitionId === "ghidra.exportWeakFunctions") {
    return {
      summary: "Preview mode exported weak function rows through the Ghidra headless boundary.",
      payloadSchema: "ghidra-export.v1",
      details: [
        { label: "Script", value: "ExportWeakFunctionList.java" },
        { label: "Mode", value: "weak" },
        { label: "Total functions", value: "5861" },
        { label: "Weak functions", value: "0" },
        { label: "Rows", value: "0" },
        { label: "Output TSV", value: "browser://fixture/ghidra-export/weak-functions.tsv" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "ghidra.exportAddressDecompile") {
    return {
      summary: "Preview mode exported decompile evidence for 1 address: 1 OK, 0 missing, 0 failed.",
      payloadSchema: "ghidra-decompile-export.v1",
      details: [
        { label: "Script", value: "ExportFunctionsByAddressDecompile.java" },
        { label: "Addresses", value: "0x00421200" },
        { label: "OK", value: "1" },
        { label: "Missing", value: "0" },
        { label: "Failed", value: "0" },
        { label: "Index TSV", value: "browser://fixture/ghidra-decompile/index.tsv" },
        { label: "Output directory", value: "browser://fixture/ghidra-decompile" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "ghidra.validateRenameMap") {
    return {
      summary: "Preview mode dry-ran an artifact-root Ghidra rename map without applying mutations.",
      payloadSchema: "ghidra-rename-dry-run.v1",
      details: [
        { label: "Runner", value: "tools/run_ghidra_batch_rename_headless.sh" },
        { label: "Map", value: typeof inputs.mapPath === "string" && inputs.mapPath ? inputs.mapPath : "browser://fixture/rename-map.txt" },
        { label: "Mode", value: "dry" },
        { label: "Exit code", value: "0" },
        { label: "Save succeeded", value: "yes" },
        { label: "Lock exception", value: "no" },
        { label: "stdout", value: "browser://fixture/ghidra-rename-dry-run/stdout.txt" },
        { label: "stderr", value: "browser://fixture/ghidra-rename-dry-run/stderr.txt" },
        { label: "Dry-run artifact", value: "browser://fixture/ghidra-rename-dry-run/dry-run.json" }
      ]
    };
  }

  if (definitionId === "ghidra.applyRenameMap") {
    return {
      summary: "Preview mode applied an artifact-root Ghidra rename map after a successful dry-run artifact.",
      payloadSchema: "ghidra-rename-apply.v1",
      details: [
        { label: "Runner", value: "tools/run_ghidra_batch_rename_headless.sh" },
        { label: "Map", value: typeof inputs.mapPath === "string" && inputs.mapPath ? inputs.mapPath : "browser://fixture/rename-map.txt" },
        {
          label: "Dry-run artifact",
          value:
            typeof inputs.dryRunArtifactPath === "string" && inputs.dryRunArtifactPath
              ? inputs.dryRunArtifactPath
              : "browser://fixture/ghidra-rename-dry-run/dry-run.json"
        },
        { label: "Mode", value: "apply" },
        { label: "Exit code", value: "0" },
        { label: "Save succeeded", value: "yes" },
        { label: "Lock exception", value: "no" },
        { label: "stdout", value: "browser://fixture/ghidra-rename-apply/stdout.txt" },
        { label: "stderr", value: "browser://fixture/ghidra-rename-apply/stderr.txt" },
        { label: "Apply artifact", value: "browser://fixture/ghidra-rename-apply/apply.json" }
      ]
    };
  }

  if (definitionId === "game.inventoryProfile") {
    return {
      summary: "Preview mode inventoried the active game harness profile without launching BEA.exe.",
      payloadSchema: "game-harness-profile.v1",
      details: [
        { label: "Profile source", value: browserGameHarnessProfile.profileSource },
        { label: "Game root", value: browserGameHarnessProfile.gameRoot },
        { label: "Executable", value: browserGameHarnessProfile.executablePath },
        { label: "Ready", value: browserGameHarnessProfile.ready ? "yes" : "no" },
        { label: "Required files", value: "present" }
      ]
    };
  }

  if (definitionId === "game.planWindowCapture") {
    return {
      summary: "Preview mode found a managed BEA window candidate and wrote a read-only capture/input plan.",
      payloadSchema: "game-window-capture-plan.v1",
      details: [
        { label: "Target run", value: "browser-job-game-launch" },
        { label: "Process", value: "BEA.exe (game)" },
        { label: "Process ID", value: "31415" },
        { label: "Capture status", value: "ready" },
        { label: "Candidates", value: "1" },
        { label: "Selected window", value: "Battle Engine Aquila" },
        { label: "Window handle", value: "0x000BEEF" },
        { label: "Capture source", value: "window:31415:0x000BEEF" },
        { label: "Input status", value: "planned" },
        { label: "Plan artifact", value: "browser://fixture/game-window-capture-plan/plan.json" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "game.captureWindowFrame") {
    const framePngBase64 =
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=";
    return {
      summary: "Preview mode captured one bounded BEA window still frame through the typed desktop-app job boundary.",
      payloadSchema: "game-window-frame-capture.v1",
      details: [
        { label: "Target run", value: "browser-job-game-launch" },
        { label: "Process", value: "BEA.exe (game)" },
        { label: "Process ID", value: "31415" },
        { label: "Frame status", value: "captured" },
        { label: "Window", value: "Battle Engine Aquila" },
        { label: "Window handle", value: "0x000BEEF" },
        { label: "Source", value: "Battle Engine Aquila" },
        { label: "Source count", value: "1" },
        { label: "Frame size", value: "960x540" },
        { label: "Frame bytes", value: "68" },
        { label: "Frame SHA-256", value: "4b5c5c92cec3b23e6a294fc0eea43234ef5126c5a64f4c6c531ac8430ab0b844" },
        { label: "Frame PNG", value: "browser://fixture/game-window-frame/frame.png" },
        { label: "Frame preview data URL", value: `data:image/png;base64,${framePngBase64}` },
        { label: "Input status", value: "planned" },
        { label: "Frame artifact", value: "browser://fixture/game-window-frame/frame.json" },
        {
          label: "Note",
          value:
            "Captured one bounded fixture PNG. Fullscreen BEA usually requires the windowed/display patch before desktop capture can see a useful frame."
        }
      ]
    };
  }

  if (definitionId === "game.captureWindowSequence") {
    const framePngBase64 =
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=";
    const frameCount = typeof inputs.frameCount === "number" ? inputs.frameCount : 3;
    const intervalMs = typeof inputs.intervalMs === "number" ? inputs.intervalMs : 250;
    return {
      summary: `Preview mode captured ${frameCount}/${frameCount} bounded BEA window frames through the typed desktop-app job boundary.`,
      payloadSchema: "game-window-frame-sequence.v1",
      details: [
        { label: "Target run", value: "browser-job-game-launch" },
        { label: "Process", value: "BEA.exe (game)" },
        { label: "Process ID", value: "31415" },
        { label: "Sequence status", value: "captured" },
        { label: "Captured frames", value: `${frameCount}/${frameCount}` },
        { label: "Interval", value: `${intervalMs} ms` },
        { label: "Window", value: "Battle Engine Aquila" },
        { label: "Window handle", value: "0x000BEEF" },
        { label: "Frame directory", value: "browser://fixture/game-window-frame-sequence/frames" },
        { label: "First frame preview data URL", value: `data:image/png;base64,${framePngBase64}` },
        { label: "Sequence artifact", value: "browser://fixture/game-window-frame-sequence/sequence.json" }
      ]
    };
  }

  if (definitionId === "game.planWindowInput" || definitionId === "game.sendWindowInput") {
    const plannedOnly = definitionId === "game.planWindowInput";
    const sequence = typeof inputs.sequence === "string" && inputs.sequence.trim() ? inputs.sequence.trim() : "tap:ENTER";
    return {
      summary: plannedOnly
        ? "Preview mode planned scoped keyboard input for a managed BEA.exe window without sending it."
        : "Preview mode sent scoped keyboard input to a managed BEA.exe window through the armed job boundary.",
      payloadSchema: "game-window-input.v1",
      details: [
        { label: "Target run", value: "browser-job-game-launch" },
        { label: "Process", value: "BEA.exe (game)" },
        { label: "Process ID", value: "31415" },
        { label: "Window handle", value: "0x000BEEF" },
        { label: "Input status", value: plannedOnly ? "ready" : "sent" },
        { label: "Planned only", value: plannedOnly ? "yes" : "no" },
        { label: "Actions", value: String(sequence.split(/[,;\n]+/).filter(Boolean).length) },
        { label: "Key events sent", value: plannedOnly ? "0" : "2" },
        { label: "Focused", value: plannedOnly ? "n/a" : "yes" },
        { label: "Sequence", value: sequence },
        {
          label: plannedOnly ? "Input plan artifact" : "Input artifact",
          value: plannedOnly ? "browser://fixture/game-window-input-plan/plan.json" : "browser://fixture/game-window-input/input.json"
        },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "game.planLaunchProfile") {
    return {
      summary: "Preview mode planned a verified game launch without starting BEA.exe.",
      payloadSchema: "game-launch-plan.v1",
      details: [
        { label: "Executable", value: "C:\\Games\\Battle Engine Aquila\\BEA.exe" },
        { label: "Working directory", value: "C:\\Games\\Battle Engine Aquila" },
        { label: "Arguments", value: "none" },
        { label: "Known Steam hash", value: "yes" },
        { label: "Command preview", value: "Start-Process -FilePath C:\\Games\\Battle Engine Aquila\\BEA.exe -WorkingDirectory C:\\Games\\Battle Engine Aquila" },
        { label: "Plan artifact", value: "browser://fixture/game-launch-plan/plan.json" }
      ]
    };
  }

  if (definitionId === "game.prepareSafeProfile") {
    return {
      summary: "Preview mode prepared a copied game profile under the app artifact root.",
      payloadSchema: "game-profile-prepare.v1",
      details: [
        { label: "Source game root", value: "C:\\Games\\Battle Engine Aquila" },
        { label: "Target game root", value: "C:\\Onslaught Workbench\\game-profiles\\bea-safe-profile" },
        { label: "Profile name", value: "bea-safe-profile" },
        { label: "Entries copied", value: "9" },
        { label: "Prepare artifact", value: "browser://fixture/game-profile-prepare/prepare.json" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "game.launchProfile") {
    return {
      summary: "Preview mode armed the verified game launch boundary and wrote a launch artifact.",
      payloadSchema: "game-launch.v1",
      details: [
        { label: "Executable", value: "C:\\Games\\BEA-safe-profile\\BEA.exe" },
        { label: "Working directory", value: "C:\\Games\\BEA-safe-profile" },
        { label: "Arguments", value: "none" },
        { label: "Process ID", value: "31415" },
        { label: "Known Steam hash", value: "yes" },
        { label: "Safe profile", value: "outside repo root" },
        { label: "Launch artifact", value: "browser://fixture/game-launch/launch.json" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  if (definitionId === "patch.planCatalogPatch") {
    const selectedPatchIds = browserPatchIdsLabel(inputs);
    const selectedPatchCount = browserPatchCount(inputs);
    return {
      summary:
        selectedPatchIds === "force_windowed"
          ? "Preview mode planned the windowed display patch without changing BEA.exe."
          : "Preview mode planned the stable patch set without changing BEA.exe.",
      payloadSchema: "patch-plan.v1",
      details: [
        { label: "File", value: "BEA.exe" },
        { label: "Patch IDs", value: selectedPatchIds },
        { label: "Ready to apply", value: selectedPatchCount },
        { label: "Already applied", value: "0" },
        { label: "Blocked", value: "0" },
        { label: "Can apply all", value: "yes" },
        { label: "Plan artifact", value: "browser://fixture/patch-plan/plan.json" }
      ]
    };
  }

  if (definitionId === "patch.prepareExecutableCopy") {
    const sourcePath = typeof inputs.sourcePath === "string" && inputs.sourcePath ? inputs.sourcePath : "game\\BEA.exe";
    return {
      summary: "Preview mode copied BEA.exe into the app workspace; source unchanged and read-back verification succeeded.",
      payloadSchema: "patch-executable-copy.v1",
      details: [
        { label: "Source", value: sourcePath },
        { label: "Copied target", value: "browser://fixture/copied-executable/BEA.exe" },
        { label: "Known Steam hash", value: "yes" },
        { label: "Catalog patches", value: "7" },
        { label: "Original rows", value: "7" },
        { label: "Patched rows", value: "0" },
        { label: "Read-back verified", value: "yes" },
        { label: "Copy artifact", value: "browser://fixture/patch-executable-copy/copy.json" }
      ]
    };
  }

  if (definitionId === "patch.applyCatalogPatch") {
    const targetPath =
      typeof inputs.executablePath === "string" && inputs.executablePath ? inputs.executablePath : "browser://fixture/copied-executable/BEA.exe";
    const backupPath = targetPath.toLowerCase().includes("bea.exe")
      ? "browser://fixture/copied-executable/BEA.exe.original.backup"
      : `${targetPath}.original.backup`;
    const selectedPatchIds = browserPatchIdsLabel(inputs);
    const selectedPatchCount = browserPatchCount(inputs);
    return {
      summary:
        selectedPatchIds === "force_windowed"
          ? "Preview mode applied the windowed display patch to an artifact-root copied BEA.exe; backup and read-back verification succeeded."
          : "Preview mode applied the stable catalog patch set to an artifact-root copied BEA.exe; backup and read-back verification succeeded.",
      payloadSchema: "patch-apply.v1",
      details: [
        { label: "Target", value: targetPath },
        { label: "Patch IDs", value: selectedPatchIds },
        { label: "Applied", value: selectedPatchCount },
        { label: "Already applied", value: "0" },
        { label: "Changed", value: "yes" },
        { label: "Backup", value: backupPath },
        { label: "Read-back verified", value: "yes" },
        { label: "Known Steam hash before", value: "yes" },
        { label: "Known Steam hash after", value: "no" },
        { label: "Apply artifact", value: "browser://fixture/patch-apply/apply.json" }
      ]
    };
  }

  if (definitionId === "patch.restoreCatalogBackup") {
    const targetPath =
      typeof inputs.targetPath === "string" && inputs.targetPath ? inputs.targetPath : "browser://fixture/copied-executable/BEA.exe";
    const backupPath =
      typeof inputs.backupPath === "string" && inputs.backupPath
        ? inputs.backupPath
        : "browser://fixture/copied-executable/BEA.exe.original.backup";
    return {
      summary: "Preview mode restored an artifact-root executable backup to a copied BEA.exe and retained a pre-restore backup.",
      payloadSchema: "patch-restore.v1",
      details: [
        { label: "Target", value: targetPath },
        { label: "Backup", value: backupPath },
        { label: "Pre-restore backup", value: "browser://fixture/patch-restore/pre-restore/BEA.exe.pre-restore.bak" },
        { label: "Read-back verified", value: "yes" },
        { label: "Known Steam hash after", value: "yes" },
        { label: "Restore artifact", value: "browser://fixture/patch-restore/restore.json" }
      ]
    };
  }

  if (definitionId === "release.inspectPolicy") {
    return {
      summary: "Preview mode classified community content and private release boundaries.",
      payloadSchema: "release-policy.v1",
      details: [
        { label: "Community docs", value: String(browserReleasePolicy.counts.communityDocs) },
        { label: "Maintainer docs", value: String(browserReleasePolicy.counts.maintainerDocs) },
        { label: "Hard-deny paths", value: String(browserReleasePolicy.counts.deny) },
        { label: "Existing hard-deny paths", value: String(browserReleasePolicy.counts.existingDeniedPaths) },
        { label: "Source tree", value: "blocked" },
        { label: "Portable bundle", value: "usable-with-review" },
        { label: "Policy artifact", value: browserReleasePolicy.artifact.artifactPath ?? "browser://fixture/release-policy/release-policy.json" }
      ]
    };
  }

  if (definitionId === "assets.catalogGameFiles") {
    return {
      summary: "Preview mode cataloged 3817 asset rows from the existing exported corpus.",
      payloadSchema: "asset-catalog.v1",
      details: [
        { label: "Catalog entries", value: "3817" },
        { label: "Textures", value: "828" },
        { label: "Loose meshes", value: "213" },
        { label: "Embedded meshes", value: "139" },
        { label: "Videos", value: "66" },
        { label: "Language rows", value: "2571" },
        { label: "Output directory", value: "browser://fixture/asset-catalog" },
        { label: "stderr", value: "none" }
      ]
    };
  }

  return {
    ...browserJobRun.result,
    summary: `Preview mode completed ${definitionId}.`
  };
}
