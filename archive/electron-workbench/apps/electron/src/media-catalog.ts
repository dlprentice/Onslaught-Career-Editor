import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { promises as fs } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import type {
  AudioPlaybackSummary,
  MediaCatalogCounts,
  MediaCatalogKind,
  MediaCatalogKindFilter,
  MediaCatalogRow,
  MediaCatalogSummary,
  MediaPreviewSummary,
  MediaVideoGroup,
  VideoPlaybackOpenOptions,
  VideoPlaybackPrepareOptions,
  VideoPlaybackSummary
} from "@onslaught/contracts";

const defaultLimit = 80;
const maxLimit = 250;
const maxPlaybackBytes = 12 * 1024 * 1024;
const maxInlineVideoBytes = 128 * 1024 * 1024;
const maxPreviewBytes = 6 * 1024 * 1024;

type JsonRecord = Record<string, unknown>;

interface RawCatalog {
  summary?: JsonRecord;
  textures?: JsonRecord[];
  loose_meshes?: JsonRecord[];
  embedded_meshes?: JsonRecord[];
  videos?: JsonRecord[];
  language_rows?: JsonRecord[];
}

async function loadAssetCatalog(appPath: string): Promise<{ catalogPath: string; found: boolean; raw: RawCatalog }> {
  const candidates = [
    path.join(appPath, "asset-catalog", "catalog.json"),
    path.join(appPath, "subagents", "asset_catalog_wave1_2026-03-14", "catalog.json")
  ];

  for (const candidate of candidates) {
    try {
      return {
        catalogPath: candidate,
        found: true,
        raw: JSON.parse(await fs.readFile(candidate, "utf8")) as RawCatalog
      };
    } catch (error) {
      if (error instanceof SyntaxError) {
        throw new Error(`Asset catalog JSON is invalid: ${candidate}`);
      }
    }
  }

  return {
    catalogPath: candidates[0],
    found: false,
    raw: {}
  };
}

export async function getMediaCatalog(
  appPath: string,
  gameRoot: string,
  queryInput = "",
  kindInput: MediaCatalogKindFilter = "all",
  limitInput = defaultLimit
): Promise<MediaCatalogSummary> {
  const { catalogPath, found: foundCatalog, raw } = await loadAssetCatalog(appPath);
  const query = queryInput.trim().toLowerCase();
  const kind = normalizeKind(kindInput);
  const limit = normalizeLimit(limitInput);
  const audio = await audioRows(gameRoot || path.join(appPath, "game"));
  const allRows = await markAvailablePreviewRows(appPath, buildMediaRows(raw, audio));

  const rows = allRows.filter(
    (row) => (kind === "all" || row.kind === kind) && rowMatchesQuery(row, query)
  );

  const returnedRows = rows.slice(0, limit);

  return {
    generatedAt: new Date().toISOString(),
    catalogPath,
    query: queryInput.trim(),
    kind,
    counts: countsFrom(raw.summary, audio),
    totalRows: rows.length,
    returnedRows: returnedRows.length,
    truncated: rows.length > returnedRows.length,
    videoGroups: videoGroupsFrom(allRows),
    rows: returnedRows,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "media-catalog.v1",
      note: foundCatalog
        ? "Read-only media catalog derived from the existing extracted asset manifest corpus."
        : "Packaged/community catalog fallback. Asset-manifest rows were not bundled; audio rows are scanned from the selected game folder."
    }
  };
}

export async function getMediaPreview(appPath: string, previewId: string): Promise<MediaPreviewSummary> {
  if (typeof previewId !== "string" || previewId.trim().length === 0) {
    throw new Error("Media preview id is required.");
  }

  const { raw } = await loadAssetCatalog(appPath);
  const row = buildMediaRows(raw, []).find((candidate) => candidate.previewId === previewId);
  if (!row?.previewId || !row.exportPath) {
    throw new Error("Unknown media preview id.");
  }

  const resolvedAppPath = path.resolve(appPath);
  const resolvedExportPath = path.isAbsolute(row.exportPath)
    ? path.resolve(row.exportPath)
    : path.resolve(resolvedAppPath, row.exportPath);
  if (!isInsidePath(resolvedAppPath, resolvedExportPath)) {
    throw new Error("Media preview path is outside the app workspace.");
  }
  if (path.extname(resolvedExportPath).toLowerCase() !== ".png") {
    throw new Error("Only PNG media previews are supported.");
  }

  const stat = await fs.stat(resolvedExportPath);
  if (!stat.isFile()) {
    throw new Error("Media preview target is not a file.");
  }
  if (stat.size > maxPreviewBytes) {
    throw new Error(`Media preview is too large for inline display (${stat.size} bytes).`);
  }

  const bytes = await fs.readFile(resolvedExportPath);
  return {
    generatedAt: new Date().toISOString(),
    previewId: row.previewId,
    label: row.label,
    group: row.group,
    sourcePath: row.sourcePath,
    exportPath: resolvedExportPath,
    sizeBytes: stat.size,
    mimeType: "image/png",
    dataUrl: `data:image/png;base64,${bytes.toString("base64")}`,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "media-preview.v1",
      note: "Inline PNG preview for one cataloged exported texture under the app workspace."
    }
  };
}

export async function getAudioPlayback(appPath: string, gameRoot: string, playbackId: string): Promise<AudioPlaybackSummary> {
  const rows = await audioRows(gameRoot || path.join(appPath, "game"));
  const row = rows.find((candidate) => candidate.playbackId === playbackId);
  if (!row || !row.sourcePath) {
    throw new Error("Unknown audio playback id.");
  }

  const resolvedGameRoot = path.resolve(gameRoot || path.join(appPath, "game"));
  const resolvedPath = path.resolve(row.sourcePath);
  if (!isInsidePath(resolvedGameRoot, resolvedPath)) {
    throw new Error("Audio path is outside the selected game root.");
  }

  const stat = await fs.stat(resolvedPath);
  if (!stat.isFile()) {
    throw new Error("Audio target is not a file.");
  }
  if (stat.size > maxPlaybackBytes) {
    throw new Error(`Audio file is too large for inline playback (${stat.size} bytes).`);
  }

  const bytes = await fs.readFile(resolvedPath);
  return {
    generatedAt: new Date().toISOString(),
    playbackId,
    label: row.label,
    group: row.group,
    sourcePath: resolvedPath,
    sizeBytes: stat.size,
    mimeType: "audio/ogg",
    dataUrl: `data:audio/ogg;base64,${bytes.toString("base64")}`,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "audio-playback.v1",
      note: "Inline playback data for one cataloged OGG under the selected game root."
    }
  };
}

export async function prepareVideoPlayback(
  appPath: string,
  gameRoot: string,
  playbackId: string,
  artifactRoot: string,
  options: VideoPlaybackPrepareOptions = {}
): Promise<VideoPlaybackSummary> {
  const { row, resolvedPath, stat } = await resolveCatalogedVideo(appPath, gameRoot, playbackId);
  const dryRun = options.dryRun === true;
  const player = await resolveVlcPlayer();
  const cacheKey = createHash("sha256")
    .update(`${playbackId}\n${row.sha256 ?? ""}\n${stat.size}\n${stat.mtimeMs}`)
    .digest("hex")
    .slice(0, 24);
  const cacheDir = path.join(path.resolve(artifactRoot), "media-cache", "video");
  const cachePath = path.join(cacheDir, `${cacheKey}.mp4`);
  const args = vlcTranscodeArgs(resolvedPath, cachePath);
  const commandPreview = player.path
    ? [quoteForPreview(player.path), ...args.map(quoteForPreview)].join(" ")
    : "VLC player not found; install VLC or set ONSLAUGHT_VLC_PATH.";

  let cacheStatus: VideoPlaybackSummary["cacheStatus"] = "unavailable";
  let outputStat: Awaited<ReturnType<typeof fs.stat>> | null = null;
  if (dryRun) {
    cacheStatus = "dry-run";
  } else {
    if (!player.available || !player.path) {
      throw new Error("VLC player not found. Install VLC or set ONSLAUGHT_VLC_PATH to prepare in-app Bink playback.");
    }
    await fs.mkdir(cacheDir, { recursive: true });
    outputStat = await existingFileStat(cachePath);
    if (outputStat && outputStat.size > 0) {
      cacheStatus = "hit";
    } else {
      await transcodeWithVlc(player.path, args);
      outputStat = await existingFileStat(cachePath);
      if (!outputStat || outputStat.size <= 0) {
        throw new Error("VLC transcode completed but did not write a playable MP4 cache file.");
      }
      cacheStatus = "created";
    }
  }

  let dataUrl: string | undefined;
  let playbackUrl: string | undefined;
  if (outputStat && outputStat.size > 0) {
    playbackUrl = pathToFileURL(cachePath).toString();
    if (outputStat.size <= maxInlineVideoBytes) {
      const bytes = await fs.readFile(cachePath);
      dataUrl = `data:video/mp4;base64,${bytes.toString("base64")}`;
    }
  }

  return {
    generatedAt: new Date().toISOString(),
    playbackId,
    label: row.label,
    group: row.group,
    sourcePath: resolvedPath,
    sizeBytes: stat.size,
    codec: row.codec ?? "unknown",
    mode: "inline-transcoded",
    dryRun,
    launched: false,
    mimeType: "video/mp4",
    playbackUrl,
    dataUrl,
    cachePath,
    cacheStatus,
    player,
    commandPreview,
    artifact: {
      kind: dryRun ? "read-only" : "local-file-write",
      mutation: false,
      schemaVersion: "video-playback.v1",
      note: dryRun
        ? "Dry-run only. The main process resolved a cataloged .vid file and built an in-app transcode request without writing the cache."
        : "Prepared an app-owned MP4 cache for one cataloged .vid file. The renderer received only a typed playback payload."
    }
  };
}

export async function openVideoPlayback(
  appPath: string,
  gameRoot: string,
  playbackId: string,
  options: VideoPlaybackOpenOptions = {}
): Promise<VideoPlaybackSummary> {
  if (typeof playbackId !== "string" || playbackId.trim().length === 0) {
    throw new Error("Video playback id is required.");
  }

  const { row, resolvedPath, stat } = await resolveCatalogedVideo(appPath, gameRoot, playbackId);

  const dryRun = options.dryRun === true;
  const player = await resolveVlcPlayer();
  const args = ["--started-from-file", "--no-video-title-show", resolvedPath];
  const commandPreview = player.path
    ? [quoteForPreview(player.path), ...args.map(quoteForPreview)].join(" ")
    : "VLC player not found; install VLC or set ONSLAUGHT_VLC_PATH.";

  let launched = false;
  let processId: number | undefined;
  if (!dryRun) {
    if (!player.available || !player.path) {
      throw new Error("VLC player not found. Install VLC or set ONSLAUGHT_VLC_PATH to a valid vlc.exe path.");
    }
    const child = spawn(player.path, args, {
      detached: true,
      stdio: "ignore",
      windowsHide: false
    });
    child.unref();
    launched = true;
    processId = child.pid;
  }

  return {
    generatedAt: new Date().toISOString(),
    playbackId,
    label: row.label,
    group: row.group,
    sourcePath: resolvedPath,
    sizeBytes: stat.size,
    codec: row.codec ?? "unknown",
    mode: "external-vlc",
    dryRun,
    launched,
    processId,
    player,
    commandPreview,
    artifact: {
      kind: "external-process",
      mutation: false,
      schemaVersion: "video-playback.v1",
      note: dryRun
        ? "Dry-run only. The main process resolved a cataloged .vid file under the selected game root and built the VLC command without launching it."
        : "The main process launched VLC for one cataloged .vid file under the selected game root. The renderer supplied only a playback id."
    }
  };
}

function normalizeKind(kind: MediaCatalogKindFilter): MediaCatalogKindFilter {
  const valid = new Set<MediaCatalogKindFilter>([
    "all",
    "audio",
    "texture",
    "loose_mesh",
    "embedded_mesh",
    "video",
    "language_row"
  ]);
  return valid.has(kind) ? kind : "all";
}

function normalizeLimit(limit: number) {
  if (!Number.isFinite(limit)) return defaultLimit;
  return Math.min(maxLimit, Math.max(1, Math.trunc(limit)));
}

function rowsFrom(
  value: JsonRecord[] | undefined,
  kind: MediaCatalogKind,
  mapper: (row: JsonRecord, index: number) => MediaCatalogRow
) {
  return Array.isArray(value) ? value.map((row, index) => ({ ...mapper(row, index), kind })) : [];
}

function buildMediaRows(raw: RawCatalog, audio: MediaCatalogRow[]) {
  return [
    ...audio,
    ...rowsFrom(raw.textures, "texture", textureRow),
    ...rowsFrom(raw.loose_meshes, "loose_mesh", looseMeshRow),
    ...rowsFrom(raw.embedded_meshes, "embedded_mesh", embeddedMeshRow),
    ...rowsFrom(raw.videos, "video", videoRow),
    ...rowsFrom(raw.language_rows, "language_row", languageRow)
  ];
}

async function markAvailablePreviewRows(appPath: string, rows: MediaCatalogRow[]) {
  const resolvedAppPath = path.resolve(appPath);
  return Promise.all(
    rows.map(async (row) => {
      if (!row.previewId || !row.exportPath) return row;
      const resolvedExportPath = path.isAbsolute(row.exportPath)
        ? path.resolve(row.exportPath)
        : path.resolve(resolvedAppPath, row.exportPath);
      try {
        const stat = await fs.stat(resolvedExportPath);
        if (!stat.isFile() || path.extname(resolvedExportPath).toLowerCase() !== ".png" || !isInsidePath(resolvedAppPath, resolvedExportPath)) {
          return { ...row, previewId: undefined };
        }
        return row;
      } catch {
        return { ...row, previewId: undefined };
      }
    })
  );
}

function countsFrom(summary: JsonRecord | undefined, audio: MediaCatalogRow[]): MediaCatalogCounts {
  const familyCounts = summary?.video_family_counts;
  const videoFamilies = isRecord(familyCounts)
    ? Object.fromEntries(
        Object.entries(familyCounts)
          .filter(([, value]) => typeof value === "number")
          .map(([key, value]) => [key, value as number])
      )
    : {};

  return {
    textures: numberValue(summary?.texture_catalog_entries),
    textureReferencedInPacked: numberValue(summary?.texture_entries_referenced_in_packed),
    textureLooseOnly: numberValue(summary?.texture_entries_loose_only),
    looseMeshes: numberValue(summary?.loose_mesh_catalog_entries),
    embeddedMeshes: numberValue(summary?.embedded_mesh_catalog_entries),
    videos: numberValue(summary?.video_catalog_entries),
    languageRows: numberValue(summary?.language_catalog_entries),
    audioRows: audio.length,
    musicRows: audio.filter((row) => row.group === "Music").length,
    voiceRows: audio.filter((row) => row.group !== "Music").length,
    total: numberValue(summary?.total_catalog_entries) + audio.length,
    videoFamilies
  };
}

async function audioRows(gameRoot: string): Promise<MediaCatalogRow[]> {
  const resolvedRoot = path.resolve(gameRoot);
  const rows: MediaCatalogRow[] = [];
  const musicDir = path.join(resolvedRoot, "data", "Music");
  const voiceDir = path.join(resolvedRoot, "data", "sounds", "english", "MessageBox");

  for (const filePath of await listOggFiles(musicDir)) {
    const name = path.basename(filePath, ".ogg").replace(" (Master)", "").replace(/_/g, " ");
    const stat = await fs.stat(filePath);
    rows.push({
      id: `audio:music:${path.basename(filePath).toLowerCase()}`,
      kind: "audio",
      label: name,
      group: "Music",
      sourcePath: filePath,
      sizeBytes: stat.size,
      playbackId: `audio:music:${path.basename(filePath).toLowerCase()}`,
      detail: "OGG music track from data\\Music"
    });
  }

  for (const filePath of await listOggFiles(voiceDir)) {
    const name = path.basename(filePath, ".ogg");
    const group = voiceGroupName(name);
    const stat = await fs.stat(filePath);
    rows.push({
      id: `audio:voice:${name.toLowerCase()}`,
      kind: "audio",
      label: name,
      group,
      sourcePath: filePath,
      sizeBytes: stat.size,
      playbackId: `audio:voice:${name.toLowerCase()}`,
      detail: "English MessageBox OGG voice line"
    });
  }

  return rows.sort((left, right) => {
    const group = left.group.localeCompare(right.group, undefined, { sensitivity: "base" });
    return group || left.label.localeCompare(right.label, undefined, { sensitivity: "base" });
  });
}

async function listOggFiles(directory: string) {
  try {
    const entries = await fs.readdir(directory, { withFileTypes: true });
    return entries
      .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith(".ogg"))
      .map((entry) => path.join(directory, entry.name))
      .sort((left, right) => left.localeCompare(right, undefined, { sensitivity: "base" }));
  } catch {
    return [];
  }
}

function voiceGroupName(baseName: string) {
  const prefix = baseName.split("_")[0] ?? "";
  return /^\d+$/.test(prefix) ? `Mission ${prefix}` : "Voice";
}

function textureRow(row: JsonRecord, index: number): MediaCatalogRow {
  const refCount = numberValue(row.total_packed_ref_count);
  const pngCount = numberValue(row.export_png_count);
  const id = stringValue(row.catalog_id, `texture:${index}`);
  const exportPath = firstString(row.export_png_paths);
  return {
    id,
    kind: "texture",
    label: stringValue(row.canonical_ref, id || `Texture ${index + 1}`),
    group: firstString(row.source_roots) ?? "texture",
    sourcePath: firstString(row.source_aya_paths),
    exportPath,
    previewId: exportPath?.toLowerCase().endsWith(".png") ? id : undefined,
    referenceCount: refCount,
    detail: `${pngCount} PNG export${pngCount === 1 ? "" : "s"}, ${refCount} packed reference${refCount === 1 ? "" : "s"}`
  };
}

function looseMeshRow(row: JsonRecord, index: number): MediaCatalogRow {
  const refCount = numberValue(row.total_packed_ref_count);
  const fbxCount = numberValue(row.export_fbx_count);
  return {
    id: stringValue(row.catalog_id, `mesh:${index}`),
    kind: "loose_mesh",
    label: stringValue(row.canonical_ref, stringValue(row.catalog_id, `Loose mesh ${index + 1}`)),
    group: "loose mesh",
    sourcePath: firstString(row.source_aya_paths),
    exportPath: firstString(row.export_fbx_paths),
    referenceCount: refCount,
    detail: `${fbxCount} FBX export${fbxCount === 1 ? "" : "s"}, ${refCount} packed reference${refCount === 1 ? "" : "s"}`
  };
}

function embeddedMeshRow(row: JsonRecord, index: number): MediaCatalogRow {
  const archive = stringValue(row.source_archive, "unknown archive");
  return {
    id: stringValue(row.catalog_id, `embedded:${index}`),
    kind: "embedded_mesh",
    label: stringValue(row.body_name, `Embedded mesh ${index + 1}`),
    group: archive,
    sourcePath: stringOptional(row.source_body_path),
    exportPath: stringOptional(row.export_fbx_path),
    detail: `Embedded CMSH body exported from ${archive}`
  };
}

function videoRow(row: JsonRecord, index: number): MediaCatalogRow {
  const family = stringValue(row.family, "video");
  const relativePath = stringValue(row.relative_path, `Video ${index + 1}`);
  const sequenceId = stringOptional(row.sequence_id);
  const codec = stringValue(row.magic, "unknown");
  const label = friendlyVideoLabel(relativePath, family, sequenceId);
  const id = stringValue(row.catalog_id, `video:${index}`);
  return {
    id,
    kind: "video",
    label,
    group: videoFamilyLabel(family),
    videoFamily: family,
    sequenceId,
    codec,
    playbackStatus: codec === "BIKi" ? "needs-transcode" : "external-only",
    playbackNote:
      codec === "BIKi"
        ? "Bink video sidecar is prepared through an app-owned transcode cache, then played in the workbench video panel."
        : "Unknown video sidecar format; inspect before playback.",
    sourcePath: relativePath,
    sizeBytes: numberValue(row.size),
    sha256: stringOptional(row.sha256),
    videoPlaybackId: `video:${id}`,
    detail: `${codec} sidecar${sequenceId ? `, sequence ${sequenceId}` : ""}`
  };
}

function languageRow(row: JsonRecord, index: number): MediaCatalogRow {
  const languageCount = numberValue(row.language_count);
  const audioPresentCount = numberValue(row.audio_present_count);
  return {
    id: stringValue(row.catalog_id, `language:${index}`),
    kind: "language_row",
    label: stringValue(row.name, stringValue(row.hex, `Language row ${index + 1}`)),
    group: stringValue(row.hex, "language"),
    languageCount,
    audioPresentCount,
    detail: `${languageCount} languages, ${audioPresentCount} audio-linked translations`
  };
}

function rowMatchesQuery(row: MediaCatalogRow, query: string) {
  if (!query) return true;
  return [
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
    .some((value) => String(value).toLowerCase().includes(query));
}

function videoGroupsFrom(rows: MediaCatalogRow[]): MediaVideoGroup[] {
  const groups = new Map<string, MediaCatalogRow[]>();
  for (const row of rows) {
    if (row.kind !== "video") continue;
    const key = row.videoFamily ?? row.group;
    groups.set(key, [...(groups.get(key) ?? []), row]);
  }

  return [...groups.entries()]
    .map(([family, groupRows]) => {
      const sequences = groupRows
        .map((row) => row.sequenceId)
        .filter((value): value is string => typeof value === "string" && value.length > 0)
        .sort(naturalCompare);
      return {
        family,
        label: videoFamilyLabel(family),
        count: groupRows.length,
        totalBytes: groupRows.reduce((total, row) => total + (row.sizeBytes ?? 0), 0),
        sequenceRange: sequences.length > 0 ? compactSequenceRange(sequences) : undefined,
        playbackStatus: groupRows.every((row) => row.codec === "BIKi") ? ("needs-transcode" as const) : ("external-only" as const),
        note: "Bink .vid rows are cataloged with hashes and sequence ids, then prepared through the app-owned transcode cache for in-app playback."
      };
    })
    .sort((left, right) => videoFamilySort(left.family) - videoFamilySort(right.family) || left.label.localeCompare(right.label));
}

function videoFamilyLabel(family: string) {
  switch (family) {
    case "briefing":
      return "Mission briefings";
    case "cutscene_numeric":
      return "Story cutscenes";
    case "named_root":
      return "Root/menu clips";
    default:
      return family.replace(/_/g, " ");
  }
}

function friendlyVideoLabel(relativePath: string, family: string, sequenceId?: string) {
  const fileName = path.basename(relativePath);
  if (family === "briefing" && sequenceId) {
    return `Mission ${sequenceId} briefing (${fileName})`;
  }
  if (family === "cutscene_numeric" && sequenceId) {
    return `Cutscene ${sequenceId} (${fileName})`;
  }
  return fileName;
}

function compactSequenceRange(sequences: string[]) {
  const unique = [...new Set(sequences)];
  if (unique.length === 1) return unique[0];
  return `${unique[0]}-${unique[unique.length - 1]}`;
}

function naturalCompare(left: string, right: string) {
  return left.localeCompare(right, undefined, { numeric: true, sensitivity: "base" });
}

function videoFamilySort(family: string) {
  if (family === "briefing") return 0;
  if (family === "cutscene_numeric") return 1;
  if (family === "named_root") return 2;
  return 3;
}

function isInsidePath(root: string, candidate: string) {
  const relative = path.relative(root, candidate);
  return relative.length === 0 || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

async function resolveCatalogedVideo(appPath: string, gameRoot: string, playbackId: string) {
  if (typeof playbackId !== "string" || playbackId.trim().length === 0) {
    throw new Error("Video playback id is required.");
  }

  const { raw } = await loadAssetCatalog(appPath);
  const row = buildMediaRows(raw, []).find((candidate) => candidate.videoPlaybackId === playbackId);
  if (!row?.videoPlaybackId || row.kind !== "video" || !row.sourcePath) {
    throw new Error("Unknown video playback id.");
  }

  const resolvedGameRoot = path.resolve(gameRoot || path.join(appPath, "game"));
  const videoRoot = path.join(resolvedGameRoot, "data", "video");
  const resolvedPath = resolveVideoSourcePath(videoRoot, row.sourcePath);
  const stat = await fs.stat(resolvedPath);
  if (!stat.isFile()) {
    throw new Error("Video target is not a file.");
  }

  return { row, resolvedPath, stat };
}

function resolveVideoSourcePath(videoRoot: string, sourcePath: string) {
  const normalizedRelative = sourcePath.replace(/^[/\\]+/, "");
  const resolvedVideoRoot = path.resolve(videoRoot);
  const resolvedPath = path.resolve(
    resolvedVideoRoot,
    ...normalizedRelative.split(/[\\/]+/).filter((part) => part.length > 0)
  );
  if (!isInsidePath(resolvedVideoRoot, resolvedPath)) {
    throw new Error("Video path is outside the selected game video directory.");
  }
  if (path.extname(resolvedPath).toLowerCase() !== ".vid") {
    throw new Error("Only cataloged .vid video playback is supported.");
  }
  return resolvedPath;
}

async function existingFileStat(filePath: string) {
  try {
    const stat = await fs.stat(filePath);
    return stat.isFile() ? stat : null;
  } catch {
    return null;
  }
}

function vlcTranscodeArgs(sourcePath: string, outputPath: string) {
  const vlcOutputPath = quoteVlcSoutPath(outputPath);
  return [
    "--intf",
    "dummy",
    "--play-and-exit",
    "--no-video-title-show",
    sourcePath,
    "--sout",
    `#transcode{vcodec=h264,acodec=mp4a,vb=1600,ab=128,channels=2,samplerate=44100}:std{access=file,mux=mp4,dst=${vlcOutputPath}}`
  ];
}

function quoteVlcSoutPath(filePath: string) {
  return `"${filePath.replace(/\\/g, "/").replace(/"/g, '\\"')}"`;
}

function transcodeWithVlc(playerPath: string, args: string[]) {
  return new Promise<void>((resolve, reject) => {
    const child = spawn(playerPath, args, {
      stdio: "ignore",
      windowsHide: true
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`VLC transcode exited with code ${code ?? -1}.`));
        return;
      }
      resolve();
    });
  });
}

async function resolveVlcPlayer(): Promise<VideoPlaybackSummary["player"]> {
  const candidates = [
    process.env.ONSLAUGHT_VLC_PATH,
    process.env.VLC_PATH,
    ...(process.platform === "win32"
      ? [
          process.env.ProgramFiles ? path.join(process.env.ProgramFiles, "VideoLAN", "VLC", "vlc.exe") : undefined,
          process.env["ProgramFiles(x86)"] ? path.join(process.env["ProgramFiles(x86)"], "VideoLAN", "VLC", "vlc.exe") : undefined
        ]
      : ["/usr/bin/vlc", "/usr/local/bin/vlc", "/opt/homebrew/bin/vlc"]),
    ...pathCandidatesForExecutable("vlc")
  ].filter((candidate): candidate is string => typeof candidate === "string" && candidate.trim().length > 0);

  for (const candidate of [...new Set(candidates)]) {
    try {
      const resolved = path.resolve(candidate);
      const stat = await fs.stat(resolved);
      if (stat.isFile()) {
        return {
          kind: "vlc",
          path: resolved,
          available: true,
          detail: "VLC was found and will be used for native Bink .vid playback."
        };
      }
    } catch {
      // Try the next candidate.
    }
  }

  return {
    kind: "none",
    available: false,
    detail: "VLC was not found. Install VLC or set ONSLAUGHT_VLC_PATH to enable Bink .vid playback."
  };
}

function pathCandidatesForExecutable(commandName: string) {
  const pathValue = process.env.PATH ?? "";
  const extensions =
    process.platform === "win32"
      ? (process.env.PATHEXT ?? ".EXE;.CMD;.BAT")
          .split(";")
          .map((extension) => extension.toLowerCase())
      : [""];
  return pathValue
    .split(path.delimiter)
    .filter((entry) => entry.length > 0)
    .flatMap((entry) =>
      extensions.map((extension) =>
        commandName.toLowerCase().endsWith(extension) ? path.join(entry, commandName) : path.join(entry, `${commandName}${extension}`)
      )
    );
}

function quoteForPreview(value: string) {
  return `"${value.replace(/"/g, '\\"')}"`;
}

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringValue(value: unknown, fallback: string) {
  return typeof value === "string" && value.length > 0 ? value : fallback;
}

function stringOptional(value: unknown) {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

function numberValue(value: unknown) {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function firstString(value: unknown) {
  return Array.isArray(value) ? value.find((item): item is string => typeof item === "string" && item.length > 0) : undefined;
}
