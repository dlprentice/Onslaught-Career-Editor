import { useEffect, useMemo, useRef, useState } from "react";
import {
  AudioLines,
  Box,
  FileText,
  Film,
  Image as ImageIcon,
  ListMusic,
  MonitorPlay,
  Play,
  SearchCheck,
  StopCircle
} from "lucide-react";
import { MediaDetails, DetailLine } from "@/components/media/MediaDetails";
import { StatusPill } from "@/components/StatusPill";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type {
  AudioPlaybackSummary,
  MediaCatalogKindFilter,
  MediaCatalogRow,
  MediaCatalogSummary,
  MediaPreviewSummary,
  Tone,
  VideoPlaybackSummary
} from "@/types/onslaught-api";

const mediaFilters: Array<{ id: MediaCatalogKindFilter; label: string; helper: string }> = [
  { id: "all", label: "All", helper: "Browse everything" },
  { id: "audio", label: "Audio", helper: "Music and voice" },
  { id: "video", label: "Videos", helper: "Briefings and clips" },
  { id: "texture", label: "Textures", helper: "Preview images" },
  { id: "loose_mesh", label: "Meshes", helper: "Model exports" },
  { id: "language_row", label: "Language", helper: "Localized lines" }
];

interface MediaSectionProps {
  mediaCatalog: MediaCatalogSummary | null;
  mediaQuery: string;
  mediaKindFilter: MediaCatalogKindFilter;
  mediaBusy: boolean;
  mediaError: string | null;
  audioPlayback: AudioPlaybackSummary | null;
  audioPlaybackBusy: string | null;
  audioPlaybackError: string | null;
  videoPlayback: VideoPlaybackSummary | null;
  videoPlaybackBusy: string | null;
  videoPlaybackError: string | null;
  mediaPreview: MediaPreviewSummary | null;
  mediaPreviewBusy: string | null;
  mediaPreviewError: string | null;
  onMediaQueryChange: (value: string) => void;
  onMediaKindFilterChange: (value: MediaCatalogKindFilter) => void;
  onRefreshMediaCatalog: (query?: string, kind?: MediaCatalogKindFilter) => Promise<void>;
  onOpenVideoGroup: (query: string) => Promise<void>;
  onLoadAudioPlayback: (playbackId: string) => Promise<void>;
  onPrepareVideoPlayback: (videoPlaybackId: string) => Promise<void>;
  onLoadMediaPreview: (previewId: string) => Promise<void>;
}

export function MediaSection({
  mediaCatalog,
  mediaQuery,
  mediaKindFilter,
  mediaBusy,
  mediaError,
  audioPlayback,
  audioPlaybackBusy,
  audioPlaybackError,
  videoPlayback,
  videoPlaybackBusy,
  videoPlaybackError,
  mediaPreview,
  mediaPreviewBusy,
  mediaPreviewError,
  onMediaQueryChange,
  onMediaKindFilterChange,
  onRefreshMediaCatalog,
  onOpenVideoGroup,
  onLoadAudioPlayback,
  onPrepareVideoPlayback,
  onLoadMediaPreview
}: MediaSectionProps) {
  const [activeAudioId, setActiveAudioId] = useState<string | null>(null);
  const [selectedVideoId, setSelectedVideoId] = useState<string | null>(null);
  const [activePreviewId, setActivePreviewId] = useState<string | null>(null);
  const rows = mediaCatalog?.rows ?? [];
  const audioRows = useMemo(() => rows.filter((row) => row.kind === "audio"), [rows]);
  const videoRows = useMemo(() => rows.filter((row) => row.kind === "video"), [rows]);
  const textureRows = useMemo(() => rows.filter((row) => row.kind === "texture"), [rows]);
  const meshRows = useMemo(() => rows.filter((row) => row.kind === "loose_mesh" || row.kind === "embedded_mesh"), [rows]);
  const languageRows = useMemo(() => rows.filter((row) => row.kind === "language_row"), [rows]);

  useEffect(() => {
    if (activeAudioId && !rows.some((row) => row.playbackId === activeAudioId)) setActiveAudioId(null);
    if (selectedVideoId && !rows.some((row) => row.videoPlaybackId === selectedVideoId)) setSelectedVideoId(null);
    if (activePreviewId && !rows.some((row) => row.previewId === activePreviewId)) setActivePreviewId(null);
  }, [activeAudioId, activePreviewId, rows, selectedVideoId]);

  async function changeFilter(kind: MediaCatalogKindFilter) {
    onMediaKindFilterChange(kind);
    await onRefreshMediaCatalog(mediaQuery, catalogKindForFilter(kind));
  }

  async function playAudio(row: MediaCatalogRow) {
    if (!row.playbackId) return;
    setActiveAudioId(row.playbackId);
    await onLoadAudioPlayback(row.playbackId);
  }

  async function prepareVideo(row: MediaCatalogRow) {
    if (!row.videoPlaybackId) return;
    setSelectedVideoId(row.videoPlaybackId);
    await onPrepareVideoPlayback(row.videoPlaybackId);
  }

  async function previewTexture(row: MediaCatalogRow) {
    if (!row.previewId) return;
    setActivePreviewId(row.previewId);
    await onLoadMediaPreview(row.previewId);
  }

  const activeFilter = mediaFilters.find((filter) => filter.id === mediaKindFilter) ?? mediaFilters[0];

  return (
    <Card data-testid="section-media" className="overflow-hidden">
      <CardHeader className="items-start">
        <div>
          <CardTitle>Media library</CardTitle>
          <CardDescription>
            Browse audio, videos, textures, meshes, and text rows from your local Battle Engine Aquila files. Playback
            stays next to the item you choose.
          </CardDescription>
        </div>
        <StatusPill tone={mediaCatalog ? "good" : "warn"}>
          {mediaCatalog ? `${mediaCatalog.counts.total.toLocaleString()} indexed` : "Choose files"}
        </StatusPill>
      </CardHeader>

      <div className="grid gap-5 xl:grid-cols-[18rem_minmax(0,1fr)]">
        <aside className="rounded-lg border border-workbench-border/60 bg-workbench-panel2/82 p-4">
          <form
            className="grid gap-3"
            onSubmit={(event) => {
              event.preventDefault();
              void onRefreshMediaCatalog(mediaQuery, catalogKindForFilter(mediaKindFilter));
            }}
          >
            <div>
              <label className="text-sm font-semibold text-workbench-text" htmlFor="media-search">
                Library
              </label>
              <p className="mt-1 text-sm leading-5 text-workbench-muted">Search once, then narrow by media type.</p>
              <div className="mt-3 flex items-center gap-2 rounded-md border border-workbench-border/75 bg-white px-3">
                <SearchCheck className="h-4 w-4 text-workbench-muted" aria-hidden="true" />
                <input
                  id="media-search"
                  data-testid="media-search"
                  className="min-h-10 min-w-0 flex-1 bg-transparent text-sm text-workbench-text outline-none placeholder:text-workbench-muted"
                  placeholder="Search audio, video, texture"
                  value={mediaQuery}
                  onChange={(event) => onMediaQueryChange(event.target.value)}
                />
              </div>
            </div>
            <Button type="submit" disabled={mediaBusy} className="w-full">
              <AudioLines className="h-4 w-4" aria-hidden="true" />
              {mediaBusy ? "Loading..." : "Search library"}
            </Button>
          </form>

          <div
            data-testid="media-kind"
            className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-1"
            role="group"
            aria-label="Media filters"
          >
            {mediaFilters.map((filter) => {
              const active = mediaKindFilter === filter.id;
              const Icon = filterIcon(filter.id);
              return (
                <button
                  key={filter.id}
                  type="button"
                  className={cn(
                    "min-h-[3.25rem] rounded-md border px-3 text-left transition",
                    active
                      ? "border-workbench-amber/70 bg-workbench-amber/15 text-workbench-text"
                      : "border-workbench-border/65 bg-white text-workbench-muted hover:border-workbench-teal/55 hover:text-workbench-text"
                  )}
                  aria-pressed={active}
                  onClick={() => void changeFilter(filter.id)}
                >
                  <span className="flex items-center gap-2 text-sm font-semibold">
                    <Icon className="h-4 w-4" aria-hidden="true" />
                    {filter.label}
                  </span>
                  <span className="mt-1 block text-xs opacity-80">{filter.helper}</span>
                </button>
              );
            })}
          </div>

          {mediaCatalog ? (
            <div className="mt-5 rounded-md border border-workbench-border/60 bg-white p-3 text-sm">
              <p className="font-semibold text-workbench-text">
                Showing {mediaCatalog.returnedRows.toLocaleString()} of {mediaCatalog.totalRows.toLocaleString()}
              </p>
              <p className="mt-1 text-xs leading-5 text-workbench-muted">
                {activeFilter.label} view {mediaCatalog.truncated ? "is limited to the first matching results." : "is complete for this search."}
              </p>
              <MediaDetails summary="catalog source">
                <DetailLine label="Catalog file" value={mediaCatalog.catalogPath} mono />
                <DetailLine label="Schema" value={mediaCatalog.artifact.schemaVersion} mono />
                <DetailLine label="Note" value={mediaCatalog.artifact.note} />
              </MediaDetails>
            </div>
          ) : null}
        </aside>

        <div className="min-w-0" data-testid="media-catalog">
          {mediaError ? <ErrorCallout>{mediaError}</ErrorCallout> : null}
          {audioPlaybackError ? <ErrorCallout>{audioPlaybackError}</ErrorCallout> : null}
          {videoPlaybackError ? <ErrorCallout>{videoPlaybackError}</ErrorCallout> : null}
          {mediaPreviewError ? <ErrorCallout>{mediaPreviewError}</ErrorCallout> : null}

          {!mediaCatalog ? (
            <EmptyMediaState />
          ) : mediaKindFilter === "audio" ? (
            <AudioLibrary
              rows={audioRows}
              activeAudioId={activeAudioId}
              audioPlayback={audioPlayback}
              busyId={audioPlaybackBusy}
              onPlay={playAudio}
              onStop={() => setActiveAudioId(null)}
            />
          ) : mediaKindFilter === "video" ? (
            <VideoLibrary
              rows={videoRows}
              groups={mediaCatalog.videoGroups}
              selectedVideoId={selectedVideoId}
              videoPlayback={videoPlayback}
              busyId={videoPlaybackBusy}
              onSelect={setSelectedVideoId}
              onPrepare={prepareVideo}
              onOpenGroup={onOpenVideoGroup}
            />
          ) : mediaKindFilter === "texture" ? (
            <TextureLibrary
              rows={textureRows}
              mediaPreview={mediaPreview}
              activePreviewId={activePreviewId}
              busyId={mediaPreviewBusy}
              onPreview={previewTexture}
            />
          ) : mediaKindFilter === "loose_mesh" || mediaKindFilter === "embedded_mesh" ? (
            <CompactLibrary title="Meshes" rows={meshRows} emptyText="No mesh rows match this search." />
          ) : mediaKindFilter === "language_row" ? (
            <CompactLibrary title="Language" rows={languageRows} emptyText="No language rows match this search." />
          ) : (
            <AllMediaLibrary
              rows={rows}
              audioPlayback={audioPlayback}
              activeAudioId={activeAudioId}
              audioBusyId={audioPlaybackBusy}
              videoPlayback={videoPlayback}
              selectedVideoId={selectedVideoId}
              videoBusyId={videoPlaybackBusy}
              mediaPreview={mediaPreview}
              activePreviewId={activePreviewId}
              previewBusyId={mediaPreviewBusy}
              onPlayAudio={playAudio}
              onStopAudio={() => setActiveAudioId(null)}
              onSelectVideo={setSelectedVideoId}
              onPrepareVideo={prepareVideo}
              onPreview={previewTexture}
            />
          )}
        </div>
      </div>
    </Card>
  );
}

function AudioLibrary({
  rows,
  activeAudioId,
  audioPlayback,
  busyId,
  onPlay,
  onStop
}: {
  rows: MediaCatalogRow[];
  activeAudioId: string | null;
  audioPlayback: AudioPlaybackSummary | null;
  busyId: string | null;
  onPlay: (row: MediaCatalogRow) => Promise<void>;
  onStop: () => void;
}) {
  return (
    <section className="grid gap-4">
      <LibraryHeading
        title="Audio"
        body="Play music and voice lines where you clicked. The active row expands in place."
        count={rows.length}
      />
      <div className="max-h-[36rem] overflow-auto pr-1">
        <div className="grid gap-3">
          {rows.length ? (
            rows.map((row) => (
              <AudioRow
                key={row.id}
                row={row}
                active={activeAudioId === row.playbackId}
                playback={activeAudioId === row.playbackId ? audioPlayback : null}
                busy={busyId === row.playbackId}
                onPlay={() => onPlay(row)}
                onStop={onStop}
              />
            ))
          ) : (
            <InlineEmptyState text="No audio rows match this search. Try All or clear the search." />
          )}
        </div>
      </div>
    </section>
  );
}

function AudioRow({
  row,
  active,
  playback,
  busy,
  onPlay,
  onStop
}: {
  row: MediaCatalogRow;
  active: boolean;
  playback: AudioPlaybackSummary | null;
  busy: boolean;
  onPlay: () => Promise<void>;
  onStop: () => void;
}) {
  return (
    <div
      data-testid={active ? "audio-active-row" : undefined}
      className={cn(
        "rounded-lg border p-4 transition",
        active ? "border-workbench-amber/75 bg-workbench-amber/10" : "border-workbench-border/65 bg-workbench-panel2/78"
      )}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <p className="truncate text-base font-semibold text-workbench-text">{row.label}</p>
            {active ? <StatusPill tone="good">Now playing</StatusPill> : null}
          </div>
          <p className="mt-1 text-sm text-workbench-muted">
            {row.group} {row.sizeBytes ? `- ${formatBytes(row.sizeBytes)}` : ""}
          </p>
          <p className="mt-1 text-sm leading-5 text-workbench-muted">{humanDetail(row.detail)}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button type="button" size="sm" data-testid="audio-playback-button" onClick={() => void onPlay()} disabled={busy}>
            <Play className="h-3.5 w-3.5" aria-hidden="true" />
            {busy ? "Loading..." : "Play"}
          </Button>
          {active ? (
            <Button type="button" size="sm" variant="secondary" onClick={onStop}>
              <StopCircle className="h-3.5 w-3.5" aria-hidden="true" />
              Stop
            </Button>
          ) : null}
        </div>
      </div>
      {active && playback ? (
        <div data-testid="audio-player" className="mt-4 rounded-md border border-workbench-border/65 bg-white p-3">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-semibold text-workbench-text">Now playing: {playback.label}</p>
            <StatusPill tone="good">Ready</StatusPill>
          </div>
          <audio controls src={playback.dataUrl} className="w-full" />
        </div>
      ) : null}
      <MediaDetails>
        <DetailLine label="Source path" value={row.sourcePath ?? "Unavailable"} mono />
        <DetailLine label="Playback id" value={row.playbackId ?? "Unavailable"} mono />
        {playback ? <DetailLine label="MIME" value={playback.mimeType} mono /> : null}
        {playback ? <DetailLine label="Schema" value={playback.artifact.schemaVersion} mono /> : null}
      </MediaDetails>
    </div>
  );
}

function VideoLibrary({
  rows,
  groups,
  selectedVideoId,
  videoPlayback,
  busyId,
  onSelect,
  onPrepare,
  onOpenGroup
}: {
  rows: MediaCatalogRow[];
  groups: MediaCatalogSummary["videoGroups"];
  selectedVideoId: string | null;
  videoPlayback: VideoPlaybackSummary | null;
  busyId: string | null;
  onSelect: (id: string | null) => void;
  onPrepare: (row: MediaCatalogRow) => Promise<void>;
  onOpenGroup: (query: string) => Promise<void>;
}) {
  const selectedRow =
    rows.find((row) => row.videoPlaybackId === selectedVideoId) ??
    rows.find((row) => row.videoPlaybackId === videoPlayback?.playbackId) ??
    null;

  return (
    <section className="grid gap-4 2xl:grid-cols-[minmax(17rem,0.45fr)_minmax(0,0.55fr)]">
      <div className="grid gap-4">
        <LibraryHeading
          title="Videos"
          body="Choose one clip, then prepare it for in-app playback."
          count={rows.length}
        />
        {groups.length > 0 ? (
          <div data-testid="video-groups" className="grid gap-3 lg:grid-cols-3">
            {groups.slice(0, 3).map((group) => (
              <button
                key={group.family}
                type="button"
                className="rounded-lg border border-workbench-border/65 bg-workbench-panel2/78 p-3 text-left transition hover:border-workbench-amber/65"
                onClick={() => void onOpenGroup(group.label)}
              >
                <p className="text-sm font-semibold text-workbench-text">{group.label}</p>
                <p className="mt-1 text-xs text-workbench-muted">
                  {group.count.toLocaleString()} clips {group.sequenceRange ? `- ${group.sequenceRange}` : ""}
                </p>
                <StatusPill tone={videoStatusTone(group.playbackStatus)} className="mt-3">
                  {videoStatusLabel(group.playbackStatus)}
                </StatusPill>
              </button>
            ))}
          </div>
        ) : null}
        <div className="max-h-[35rem] overflow-auto pr-1">
          <div className="grid gap-3">
            {rows.length ? (
              rows.map((row) => (
                <VideoRow
                  key={row.id}
                  row={row}
                  selected={row.videoPlaybackId === selectedRow?.videoPlaybackId}
                  busy={busyId === row.videoPlaybackId}
                  prepared={videoPlayback?.playbackId === row.videoPlaybackId}
                  onSelect={() => onSelect(row.videoPlaybackId ?? null)}
                  onPrepare={() => onPrepare(row)}
                />
              ))
            ) : (
              <InlineEmptyState text="No video rows match this search. Try All or clear the search." />
            )}
          </div>
        </div>
      </div>
      <VideoPlayerPanel row={selectedRow} playback={videoPlayback} busy={busyId === selectedRow?.videoPlaybackId} onPrepare={onPrepare} />
    </section>
  );
}

function VideoRow({
  row,
  selected,
  busy,
  prepared,
  onSelect,
  onPrepare
}: {
  row: MediaCatalogRow;
  selected: boolean;
  busy: boolean;
  prepared: boolean;
  onSelect: () => void;
  onPrepare: () => Promise<void>;
}) {
  return (
    <div
      className={cn(
        "rounded-lg border p-4 transition",
        selected ? "border-workbench-amber/75 bg-workbench-amber/10" : "border-workbench-border/65 bg-workbench-panel2/78"
      )}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <button type="button" className="min-w-0 flex-1 text-left" onClick={onSelect} data-testid="video-select-button">
          <p className="truncate text-base font-semibold text-workbench-text">{row.label}</p>
          <p className="mt-1 text-sm text-workbench-muted">
            {row.group} {row.sizeBytes ? `- ${formatBytes(row.sizeBytes)}` : ""}
          </p>
        </button>
        <StatusPill tone={prepared ? "good" : videoStatusTone(row.playbackStatus)}>
          {prepared ? "Ready" : videoStatusLabel(row.playbackStatus)}
        </StatusPill>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button
          type="button"
          size="sm"
          variant={prepared ? "secondary" : "primary"}
          data-testid="video-playback-button"
          onClick={() => void onPrepare()}
          disabled={busy}
        >
          <MonitorPlay className="h-3.5 w-3.5" aria-hidden="true" />
          {busy ? "Preparing..." : prepared ? "Play video" : "Prepare for in-app playback"}
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={onSelect}>
          Select
        </Button>
      </div>
      <MediaDetails>
        <DetailLine label="Source path" value={row.sourcePath ?? "Unavailable"} mono />
        <DetailLine label="Video id" value={row.videoPlaybackId ?? "Unavailable"} mono />
        <DetailLine label="Codec" value={row.codec ?? "Unknown"} mono />
        {row.sha256 ? <DetailLine label="SHA-256" value={row.sha256} mono /> : null}
      </MediaDetails>
    </div>
  );
}

function VideoPlayerPanel({
  row,
  playback,
  busy,
  onPrepare
}: {
  row: MediaCatalogRow | null;
  playback: VideoPlaybackSummary | null;
  busy: boolean;
  onPrepare: (row: MediaCatalogRow) => Promise<void>;
}) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const prepared = Boolean(row && playback?.playbackId === row.videoPlaybackId);
  const playable = Boolean(prepared && (playback?.dataUrl || playback?.playbackUrl));
  const status = prepared ? "Ready" : row ? videoStatusLabel(row.playbackStatus) : "Needs preparation";
  const statusTone: Tone = prepared ? "good" : row ? videoStatusTone(row.playbackStatus) : "neutral";

  return (
    <section data-testid="video-selected-panel" className="rounded-lg border border-workbench-border/65 bg-workbench-panel2/82 p-4">
      {row ? (
        <div className="grid gap-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-lg font-semibold text-workbench-text">{row.label}</p>
              <p className="mt-1 text-sm text-workbench-muted">
                {row.group} {row.sizeBytes ? `- ${formatBytes(row.sizeBytes)}` : ""}
              </p>
            </div>
            <StatusPill tone={statusTone}>{status}</StatusPill>
          </div>
          <div className="grid min-h-[20rem] place-items-center overflow-hidden rounded-lg border border-workbench-border bg-[#0f172a]">
            {playable ? (
              <video
                ref={videoRef}
                data-testid="video-player"
                className="aspect-video w-full bg-black"
                controls
                preload="metadata"
                src={playback?.dataUrl ?? playback?.playbackUrl}
              />
            ) : (
              <div className="p-6 text-center">
                <Film className="mx-auto h-10 w-10 text-slate-300" aria-hidden="true" />
                <p className="mt-3 text-base font-semibold text-white">
                  {busy ? "Preparing app-owned playback file." : prepared ? "Prepared video is ready. Press Play." : "Choose Prepare for in-app playback."}
                </p>
                <p className="mt-2 max-w-md text-sm leading-6 text-slate-300">
                  The player appears here after the selected clip has been prepared for the in-app video panel.
                </p>
              </div>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {playable ? (
              <Button type="button" data-testid="video-playback-button" onClick={() => void videoRef.current?.play()}>
                <Play className="h-4 w-4" aria-hidden="true" />
                Play video
              </Button>
            ) : (
              <Button type="button" data-testid="video-playback-button" onClick={() => void onPrepare(row)} disabled={busy}>
                <MonitorPlay className="h-4 w-4" aria-hidden="true" />
                {busy ? "Preparing..." : "Prepare for in-app playback"}
              </Button>
            )}
          </div>
          <MediaDetails>
            <DetailLine label="Source path" value={playback?.sourcePath ?? row.sourcePath ?? "Unavailable"} mono />
            <DetailLine label="Codec" value={playback?.codec ?? row.codec ?? "Unknown"} mono />
            {playback?.mimeType ? <DetailLine label="MIME" value={playback.mimeType} mono /> : null}
            {playback?.cacheStatus ? <DetailLine label="Cache status" value={playback.cacheStatus} mono /> : null}
            {playback?.cachePath ? <DetailLine label="Cache path" value={playback.cachePath} mono /> : null}
            {playback?.player.detail ? <DetailLine label="Player" value={playback.player.detail} /> : null}
            {playback?.commandPreview ? <DetailLine label="Command preview" value={playback.commandPreview} mono /> : null}
            {playback?.artifact.schemaVersion ? <DetailLine label="Schema" value={playback.artifact.schemaVersion} mono /> : null}
          </MediaDetails>
        </div>
      ) : (
        <div className="grid min-h-[26rem] place-items-center rounded-lg border border-dashed border-workbench-border/75 bg-white p-6 text-center">
          <div>
            <Film className="mx-auto h-12 w-12 text-workbench-muted" aria-hidden="true" />
            <p className="mt-4 text-lg font-semibold text-workbench-text">Choose a video to preview.</p>
            <p className="mt-2 max-w-md text-sm leading-6 text-workbench-muted">
              Select one clip from the list. The player and preparation status will stay in this panel.
            </p>
          </div>
        </div>
      )}
    </section>
  );
}

function TextureLibrary({
  rows,
  mediaPreview,
  activePreviewId,
  busyId,
  onPreview
}: {
  rows: MediaCatalogRow[];
  mediaPreview: MediaPreviewSummary | null;
  activePreviewId: string | null;
  busyId: string | null;
  onPreview: (row: MediaCatalogRow) => Promise<void>;
}) {
  return (
    <section className="grid gap-4">
      <LibraryHeading title="Textures" body="Preview exported PNG textures without exposing file paths by default." count={rows.length} />
      <div className="grid gap-3 xl:grid-cols-2 2xl:grid-cols-3">
        {rows.length ? (
          rows.map((row) => (
            <TextureCard
              key={row.id}
              row={row}
              preview={activePreviewId === row.previewId ? mediaPreview : null}
              busy={busyId === row.previewId}
              onPreview={() => onPreview(row)}
            />
          ))
        ) : (
          <InlineEmptyState text="No texture rows match this search. Try All or clear the search." />
        )}
      </div>
    </section>
  );
}

function TextureCard({
  row,
  preview,
  busy,
  onPreview
}: {
  row: MediaCatalogRow;
  preview: MediaPreviewSummary | null;
  busy: boolean;
  onPreview: () => Promise<void>;
}) {
  return (
    <div className="rounded-lg border border-workbench-border/65 bg-workbench-panel2/78 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-base font-semibold text-workbench-text" title={row.label}>
            {shortItemName(row.label)}
          </p>
          <p className="mt-1 text-sm text-workbench-muted">{row.group}</p>
          <p className="mt-1 text-sm leading-5 text-workbench-muted">{humanDetail(row.detail)}</p>
        </div>
        <StatusPill tone={row.previewId ? "good" : "warn"}>{row.previewId ? "Preview" : "Unavailable"}</StatusPill>
      </div>
      <Button
        type="button"
        size="sm"
        className="mt-3"
        data-testid="media-preview-button"
        disabled={!row.previewId || busy}
        onClick={() => void onPreview()}
      >
        <ImageIcon className="h-3.5 w-3.5" aria-hidden="true" />
        {busy ? "Loading..." : "Preview"}
      </Button>
      {preview ? (
        <div data-testid="media-preview" className="mt-4 rounded-md border border-workbench-border/65 bg-[#0f172a] p-3">
          <div className="grid min-h-[13rem] place-items-center">
            <img
              data-testid="media-preview-image"
              src={preview.dataUrl}
              alt={shortItemName(preview.label)}
              className="max-h-[24rem] max-w-full object-contain"
            />
          </div>
          <p className="mt-2 text-sm font-semibold text-workbench-text">{shortItemName(preview.label)}</p>
        </div>
      ) : null}
      <MediaDetails>
        <DetailLine label="Source path" value={row.sourcePath ?? "Unavailable"} mono />
        <DetailLine label="Export path" value={row.exportPath ?? "Unavailable"} mono />
        <DetailLine label="Preview id" value={row.previewId ?? "Unavailable"} mono />
        {preview ? <DetailLine label="MIME" value={preview.mimeType} mono /> : null}
        {preview ? <DetailLine label="Schema" value={preview.artifact.schemaVersion} mono /> : null}
      </MediaDetails>
    </div>
  );
}

function AllMediaLibrary({
  rows,
  audioPlayback,
  activeAudioId,
  audioBusyId,
  videoPlayback,
  selectedVideoId,
  videoBusyId,
  mediaPreview,
  activePreviewId,
  previewBusyId,
  onPlayAudio,
  onStopAudio,
  onSelectVideo,
  onPrepareVideo,
  onPreview
}: {
  rows: MediaCatalogRow[];
  audioPlayback: AudioPlaybackSummary | null;
  activeAudioId: string | null;
  audioBusyId: string | null;
  videoPlayback: VideoPlaybackSummary | null;
  selectedVideoId: string | null;
  videoBusyId: string | null;
  mediaPreview: MediaPreviewSummary | null;
  activePreviewId: string | null;
  previewBusyId: string | null;
  onPlayAudio: (row: MediaCatalogRow) => Promise<void>;
  onStopAudio: () => void;
  onSelectVideo: (id: string | null) => void;
  onPrepareVideo: (row: MediaCatalogRow) => Promise<void>;
  onPreview: (row: MediaCatalogRow) => Promise<void>;
}) {
  return (
    <section className="grid gap-4">
      <LibraryHeading title="All media" body="A compact list with local actions beside playable rows." count={rows.length} />
      <div className="grid gap-3">
        {rows.length ? (
          rows.map((row) => (
            <div key={row.id} className="rounded-lg border border-workbench-border/65 bg-workbench-panel2/78 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusPill tone={row.kind === "audio" || row.kind === "video" || row.kind === "texture" ? "good" : "neutral"}>
                      {kindLabel(row.kind)}
                    </StatusPill>
                    <p className="truncate text-base font-semibold text-workbench-text">{row.kind === "texture" ? shortItemName(row.label) : row.label}</p>
                  </div>
                  <p className="mt-2 text-sm text-workbench-muted">{row.group}</p>
                  <p className="mt-1 text-sm leading-5 text-workbench-muted">{humanDetail(row.detail)}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {row.kind === "audio" && row.playbackId ? (
                    <Button
                      type="button"
                      size="sm"
                      data-testid="audio-playback-button"
                      onClick={() => void onPlayAudio(row)}
                      disabled={audioBusyId === row.playbackId}
                    >
                      <Play className="h-3.5 w-3.5" aria-hidden="true" />
                      {audioBusyId === row.playbackId ? "Loading..." : "Play"}
                    </Button>
                  ) : null}
                  {row.kind === "video" && row.videoPlaybackId ? (
                    <Button
                      type="button"
                      size="sm"
                      data-testid="video-playback-button"
                      onClick={() => void onPrepareVideo(row)}
                      disabled={videoBusyId === row.videoPlaybackId}
                    >
                      <MonitorPlay className="h-3.5 w-3.5" aria-hidden="true" />
                      {videoBusyId === row.videoPlaybackId ? "Preparing..." : "Prepare for in-app playback"}
                    </Button>
                  ) : null}
                  {row.kind === "texture" && row.previewId ? (
                    <Button
                      type="button"
                      size="sm"
                      data-testid="media-preview-button"
                      onClick={() => void onPreview(row)}
                      disabled={previewBusyId === row.previewId}
                    >
                      <ImageIcon className="h-3.5 w-3.5" aria-hidden="true" />
                      {previewBusyId === row.previewId ? "Loading..." : "Preview"}
                    </Button>
                  ) : null}
                  {row.kind === "video" && row.videoPlaybackId ? (
                    <Button type="button" size="sm" variant="ghost" onClick={() => onSelectVideo(row.videoPlaybackId ?? null)}>
                      Select
                    </Button>
                  ) : null}
                </div>
              </div>
              {row.kind === "audio" && activeAudioId === row.playbackId && audioPlayback ? (
                <AudioRow row={row} active playback={audioPlayback} busy={false} onPlay={() => onPlayAudio(row)} onStop={onStopAudio} />
              ) : null}
              {row.kind === "video" && (selectedVideoId === row.videoPlaybackId || videoPlayback?.playbackId === row.videoPlaybackId) ? (
                <div className="mt-4">
                  <VideoPlayerPanel row={row} playback={videoPlayback} busy={videoBusyId === row.videoPlaybackId} onPrepare={onPrepareVideo} />
                </div>
              ) : null}
              {row.kind === "texture" && activePreviewId === row.previewId && mediaPreview ? (
                <div className="mt-4">
                  <TextureCard row={row} preview={mediaPreview} busy={false} onPreview={() => onPreview(row)} />
                </div>
              ) : null}
              <MediaDetails>
                <DetailLine label="Source path" value={row.sourcePath ?? "Unavailable"} mono />
                <DetailLine label="Export path" value={row.exportPath ?? "Unavailable"} mono />
                <DetailLine label="Id" value={row.id} mono />
                {row.sha256 ? <DetailLine label="SHA-256" value={row.sha256} mono /> : null}
              </MediaDetails>
            </div>
          ))
        ) : (
          <InlineEmptyState text="No rows match this search. Clear the search or choose another filter." />
        )}
      </div>
    </section>
  );
}

function CompactLibrary({ title, rows, emptyText }: { title: string; rows: MediaCatalogRow[]; emptyText: string }) {
  return (
    <section className="grid gap-4">
      <LibraryHeading title={title} body="Compact rows keep source paths inside Details." count={rows.length} />
      <div className="overflow-hidden rounded-lg border border-workbench-border/65">
        {rows.length ? (
          <table className="w-full border-collapse text-left text-sm">
            <thead className="bg-workbench-panel2 text-workbench-muted">
              <tr>
                <th className="px-4 py-3 font-semibold">Kind</th>
                <th className="px-4 py-3 font-semibold">Item</th>
                <th className="px-4 py-3 font-semibold">Source</th>
                <th className="px-4 py-3 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-t border-workbench-border/65 align-top">
                  <td className="px-4 py-3">
                    <StatusPill>{kindLabel(row.kind)}</StatusPill>
                  </td>
                  <td className="max-w-[22rem] px-4 py-3">
                    <p className="truncate font-semibold text-workbench-text">{shortItemName(row.label)}</p>
                    <p className="mt-1 text-xs leading-5 text-workbench-muted">{humanDetail(row.detail)}</p>
                  </td>
                  <td className="px-4 py-3 text-workbench-muted">{row.group}</td>
                  <td className="px-4 py-3">
                    <MediaDetails summary="source fields">
                      <DetailLine label="Source path" value={row.sourcePath ?? "Unavailable"} mono />
                      <DetailLine label="Export path" value={row.exportPath ?? "Unavailable"} mono />
                      <DetailLine label="Id" value={row.id} mono />
                    </MediaDetails>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <InlineEmptyState text={emptyText} />
        )}
      </div>
    </section>
  );
}

function LibraryHeading({ title, body, count }: { title: string; body: string; count: number }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3 rounded-lg border border-workbench-border/65 bg-workbench-panel2/78 p-4">
      <div>
        <h3 className="text-lg font-semibold text-workbench-text">{title}</h3>
        <p className="mt-1 text-sm leading-6 text-workbench-muted">{body}</p>
      </div>
      <StatusPill>{count.toLocaleString()} shown</StatusPill>
    </div>
  );
}

function EmptyMediaState() {
  return (
    <div className="grid min-h-[28rem] place-items-center rounded-lg border border-dashed border-workbench-border/75 bg-workbench-panel2/72 p-6 text-center">
      <div>
        <AudioLines className="mx-auto h-12 w-12 text-workbench-muted" aria-hidden="true" />
        <p className="mt-4 text-lg font-semibold text-workbench-text">Load the media library to begin.</p>
        <p className="mt-2 max-w-md text-sm leading-6 text-workbench-muted">
          Search by name or choose a type. The library stays read-only and keeps private game media out of public bundles.
        </p>
      </div>
    </div>
  );
}

function InlineEmptyState({ text }: { text: string }) {
  return <div className="rounded-lg border border-dashed border-workbench-border/70 bg-workbench-panel2/72 p-5 text-sm leading-6 text-workbench-muted">{text}</div>;
}

function ErrorCallout({ children }: { children: string }) {
  return <div className="mb-4 rounded-lg border border-[#fecdca] bg-[#fef3f2] p-4 text-sm leading-6 text-[#b42318]">{children}</div>;
}

function filterIcon(kind: MediaCatalogKindFilter) {
  switch (kind) {
    case "audio":
      return ListMusic;
    case "video":
      return Film;
    case "texture":
      return ImageIcon;
    case "loose_mesh":
    case "embedded_mesh":
      return Box;
    case "language_row":
      return FileText;
    default:
      return AudioLines;
  }
}

function catalogKindForFilter(kind: MediaCatalogKindFilter): MediaCatalogKindFilter {
  // The public filter is "Meshes"; fetch broadly so the view can include loose and embedded mesh rows together.
  return kind === "loose_mesh" ? "all" : kind;
}

function kindLabel(kind: MediaCatalogRow["kind"]) {
  switch (kind) {
    case "loose_mesh":
    case "embedded_mesh":
      return "Mesh";
    case "language_row":
      return "Language";
    default:
      return kind.charAt(0).toUpperCase() + kind.slice(1);
  }
}

function videoStatusLabel(status: MediaCatalogRow["playbackStatus"] | undefined) {
  switch (status) {
    case "playable":
      return "Ready";
    case "external-only":
      return "External fallback";
    case "needs-transcode":
      return "Needs preparation";
    default:
      return "Unavailable";
  }
}

function videoStatusTone(status: MediaCatalogRow["playbackStatus"] | undefined): Tone {
  switch (status) {
    case "playable":
      return "good";
    case "needs-transcode":
      return "warn";
    case "external-only":
      return "warn";
    default:
      return "danger";
  }
}

function formatBytes(value: number | undefined) {
  if (!value) return "n/a";
  if (value < 1024) return `${value} B`;
  const units = ["KB", "MB", "GB"];
  let size = value / 1024;
  let unit = units[0];
  for (let index = 1; index < units.length && size >= 1024; index++) {
    size /= 1024;
    unit = units[index];
  }
  return `${size.toFixed(size >= 10 ? 1 : 2)} ${unit}`;
}

function shortItemName(value: string) {
  const normalized = value.replace(/\\/g, "/");
  return normalized.split("/").filter(Boolean).at(-1) ?? value;
}

function humanDetail(value: string) {
  return value
    .replace(/from data\\Music/gi, "from the music folder")
    .replace(/from data\/Music/gi, "from the music folder")
    .replace(/data\\Resources\\/gi, "resources: ")
    .replace(/data\/Resources\//gi, "resources: ")
    .replace(/\bBIKi\b/g, "Bink")
    .replace(/\bOGG\b/g, "Ogg")
    .replace(/\bCMSH\b/g, "embedded mesh")
    .replace(/\bFBX\b/g, "model")
    .replace(/\bPNG\b/g, "image");
}
