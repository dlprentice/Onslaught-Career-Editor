import { useEffect, useMemo, useState } from "react";
import { GameHarnessSection } from "@/components/harness/GameHarnessSection";
import { HomeSection } from "@/components/home/HomeSection";
import { LoreSection } from "@/components/lore/LoreSection";
import { MediaSection } from "@/components/media/MediaSection";
import { PatchBenchSection } from "@/components/patch/PatchBenchSection";
import { ReLabSection } from "@/components/re-lab/ReLabSection";
import { ReleaseSection } from "@/components/release/ReleaseSection";
import { SaveLabSection } from "@/components/saves/SaveLabSection";
import { WorkbenchShell } from "@/components/WorkbenchShell";
import { Button } from "@/components/ui/button";
import { getOnslaughtApi } from "@/lib/bridge";
import {
  formatEvidenceType,
  formatSafetyLabel,
  formatWorkbenchMode,
  harnessPhases,
  navForJobLane,
  navItems,
  type WorkbenchCommandResult
} from "@/workbenchNav";
import type {
  AddressConversionSummary,
  AudioPlaybackSummary,
  ContentDocumentSummary,
  ContentIndexSummary,
  DebugReadinessSummary,
  GameHarnessProfileSummary,
  GhidraReadinessSummary,
  HexReadSummary,
  MediaCatalogKindFilter,
  MediaCatalogSummary,
  MediaPreviewSummary,
  ReleasePolicySummary,
  RuntimeSnapshot,
  SaveComparisonSummary,
  SaveInspectionSummary,
  SpecimenVerificationSummary,
  Tone,
  VideoPlaybackSummary,
  WorkbenchJobCatalogSummary,
  WorkbenchJobDefinition,
  WorkbenchJobInputValue,
  WorkbenchJobProgressEvent,
  WorkbenchJobRunSummary
} from "@/types/onslaught-api";

type ContentAudienceFilter = "all" | "community" | "maintainer";
type GoodieStateFilter = "all" | "unlocked" | "locked" | "new" | "old" | "instructions";

function getJobDetail(run: WorkbenchJobRunSummary, label: string) {
  return run.result.details.find((detail) => detail.label === label)?.value ?? "";
}

export function App() {
  const [snapshot, setSnapshot] = useState<RuntimeSnapshot | null>(null);
  const [specimen, setSpecimen] = useState<SpecimenVerificationSummary | null>(null);
  const [specimenPath, setSpecimenPath] = useState("");
  const [verifyBusy, setVerifyBusy] = useState(false);
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [saveInspection, setSaveInspection] = useState<SaveInspectionSummary | null>(null);
  const [savePath, setSavePath] = useState("");
  const [goodieQuery, setGoodieQuery] = useState("");
  const [goodieStateFilter, setGoodieStateFilter] = useState<GoodieStateFilter>("all");
  const [inspectBusy, setInspectBusy] = useState(false);
  const [inspectError, setInspectError] = useState<string | null>(null);
  const [saveComparison, setSaveComparison] = useState<SaveComparisonSummary | null>(null);
  const [leftComparePath, setLeftComparePath] = useState("");
  const [rightComparePath, setRightComparePath] = useState("");
  const [compareBusy, setCompareBusy] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);
  const [hexRead, setHexRead] = useState<HexReadSummary | null>(null);
  const [hexPath, setHexPath] = useState("");
  const [hexOffset, setHexOffset] = useState("0x129696");
  const [hexLength, setHexLength] = useState("64");
  const [hexBusy, setHexBusy] = useState(false);
  const [hexError, setHexError] = useState<string | null>(null);
  const [addressConversion, setAddressConversion] = useState<AddressConversionSummary | null>(null);
  const [addressExecutablePath, setAddressExecutablePath] = useState("");
  const [virtualAddress, setVirtualAddress] = useState("0x00529696");
  const [addressBusy, setAddressBusy] = useState(false);
  const [addressError, setAddressError] = useState<string | null>(null);
  const [ghidraReadiness, setGhidraReadiness] = useState<GhidraReadinessSummary | null>(null);
  const [debugReadiness, setDebugReadiness] = useState<DebugReadinessSummary | null>(null);
  const [gameHarnessProfile, setGameHarnessProfile] = useState<GameHarnessProfileSummary | null>(null);
  const [jobCatalog, setJobCatalog] = useState<WorkbenchJobCatalogSummary | null>(null);
  const [jobRun, setJobRun] = useState<WorkbenchJobRunSummary | null>(null);
  const [jobHistory, setJobHistory] = useState<WorkbenchJobRunSummary[]>([]);
  const [jobProgress, setJobProgress] = useState<WorkbenchJobProgressEvent[]>([]);
  const [jobBusy, setJobBusy] = useState<string | null>(null);
  const [jobError, setJobError] = useState<string | null>(null);
  const [showParityDiagnostics, setShowParityDiagnostics] = useState(false);
  const [launchJobsArmed, setLaunchJobsArmed] = useState(false);
  const [contentIndex, setContentIndex] = useState<ContentIndexSummary | null>(null);
  const [contentDocument, setContentDocument] = useState<ContentDocumentSummary | null>(null);
  const [releasePolicy, setReleasePolicy] = useState<ReleasePolicySummary | null>(null);
  const [releaseBusy, setReleaseBusy] = useState(false);
  const [releaseError, setReleaseError] = useState<string | null>(null);
  const [contentQuery, setContentQuery] = useState("");
  const [contentAudienceFilter, setContentAudienceFilter] = useState<ContentAudienceFilter>("all");
  const [contentBusy, setContentBusy] = useState(false);
  const [contentError, setContentError] = useState<string | null>(null);
  const [mediaCatalog, setMediaCatalog] = useState<MediaCatalogSummary | null>(null);
  const [mediaQuery, setMediaQuery] = useState("");
  const [mediaKindFilter, setMediaKindFilter] = useState<MediaCatalogKindFilter>("all");
  const [mediaBusy, setMediaBusy] = useState(false);
  const [mediaError, setMediaError] = useState<string | null>(null);
  const [audioPlayback, setAudioPlayback] = useState<AudioPlaybackSummary | null>(null);
  const [audioPlaybackBusy, setAudioPlaybackBusy] = useState<string | null>(null);
  const [audioPlaybackError, setAudioPlaybackError] = useState<string | null>(null);
  const [videoPlayback, setVideoPlayback] = useState<VideoPlaybackSummary | null>(null);
  const [videoPlaybackBusy, setVideoPlaybackBusy] = useState<string | null>(null);
  const [videoPlaybackError, setVideoPlaybackError] = useState<string | null>(null);
  const [mediaPreview, setMediaPreview] = useState<MediaPreviewSummary | null>(null);
  const [mediaPreviewBusy, setMediaPreviewBusy] = useState<string | null>(null);
  const [mediaPreviewError, setMediaPreviewError] = useState<string | null>(null);
  const [gameFolderPath, setGameFolderPath] = useState("");
  const [gameFolderBusy, setGameFolderBusy] = useState(false);
  const [gameFolderError, setGameFolderError] = useState<string | null>(null);
  const [safeProfileBusy, setSafeProfileBusy] = useState(false);
  const [safeProfileError, setSafeProfileError] = useState<string | null>(null);
  const [safeProfileRun, setSafeProfileRun] = useState<WorkbenchJobRunSummary | null>(null);
  const [savePatchRank, setSavePatchRank] = useState("S");
  const [savePatchKills, setSavePatchKills] = useState("100");
  const [savePatchLevelRanks, setSavePatchLevelRanks] = useState("1:S 2:A");
  const [savePatchCategoryKills, setSavePatchCategoryKills] = useState("aircraft:100 mechs:20");
  const [savePatchNodes, setSavePatchNodes] = useState(true);
  const [savePatchLinks, setSavePatchLinks] = useState(true);
  const [savePatchGoodies, setSavePatchGoodies] = useState(true);
  const [savePatchKillsEnabled, setSavePatchKillsEnabled] = useState(true);
  const [copiedSavePath, setCopiedSavePath] = useState("");
  const [copiedSaveBackupPath, setCopiedSaveBackupPath] = useState("");
  const [savePatchRun, setSavePatchRun] = useState<WorkbenchJobRunSummary | null>(null);
  const [savePatchBusy, setSavePatchBusy] = useState<string | null>(null);
  const [savePatchError, setSavePatchError] = useState<string | null>(null);
  const [optionsPath, setOptionsPath] = useState("");
  const [copiedOptionsPath, setCopiedOptionsPath] = useState("");
  const [copiedOptionsBackupPath, setCopiedOptionsBackupPath] = useState("");
  const [optionsSoundVolumeEnabled, setOptionsSoundVolumeEnabled] = useState(true);
  const [optionsSoundVolume, setOptionsSoundVolume] = useState("0.75");
  const [optionsMusicVolumeEnabled, setOptionsMusicVolumeEnabled] = useState(true);
  const [optionsMusicVolume, setOptionsMusicVolume] = useState("0.65");
  const [optionsInvertWalkerP1Enabled, setOptionsInvertWalkerP1Enabled] = useState(true);
  const [optionsInvertWalkerP1, setOptionsInvertWalkerP1] = useState(true);
  const [optionsInvertWalkerP2Enabled, setOptionsInvertWalkerP2Enabled] = useState(false);
  const [optionsInvertWalkerP2, setOptionsInvertWalkerP2] = useState(false);
  const [optionsInvertFlightP1Enabled, setOptionsInvertFlightP1Enabled] = useState(false);
  const [optionsInvertFlightP1, setOptionsInvertFlightP1] = useState(false);
  const [optionsInvertFlightP2Enabled, setOptionsInvertFlightP2Enabled] = useState(false);
  const [optionsInvertFlightP2, setOptionsInvertFlightP2] = useState(false);
  const [optionsVibrationP1Enabled, setOptionsVibrationP1Enabled] = useState(false);
  const [optionsVibrationP1, setOptionsVibrationP1] = useState(true);
  const [optionsVibrationP2Enabled, setOptionsVibrationP2Enabled] = useState(true);
  const [optionsVibrationP2, setOptionsVibrationP2] = useState(false);
  const [optionsControllerConfigP1Enabled, setOptionsControllerConfigP1Enabled] = useState(true);
  const [optionsControllerConfigP1, setOptionsControllerConfigP1] = useState("1");
  const [optionsControllerConfigP2Enabled, setOptionsControllerConfigP2Enabled] = useState(false);
  const [optionsControllerConfigP2, setOptionsControllerConfigP2] = useState("0");
  const [optionsMouseSensitivityEnabled, setOptionsMouseSensitivityEnabled] = useState(false);
  const [optionsMouseSensitivity, setOptionsMouseSensitivity] = useState("1");
  const [optionsControlSchemeEnabled, setOptionsControlSchemeEnabled] = useState(false);
  const [optionsControlSchemeIndex, setOptionsControlSchemeIndex] = useState("0");
  const [optionsLanguageEnabled, setOptionsLanguageEnabled] = useState(false);
  const [optionsLanguageIndex, setOptionsLanguageIndex] = useState("0");
  const [optionsScreenShapeEnabled, setOptionsScreenShapeEnabled] = useState(false);
  const [optionsScreenShape, setOptionsScreenShape] = useState("0");
  const [optionsD3dDeviceEnabled, setOptionsD3dDeviceEnabled] = useState(false);
  const [optionsD3dDeviceIndex, setOptionsD3dDeviceIndex] = useState("0");
  const [optionsCopyFromPath, setOptionsCopyFromPath] = useState("");
  const [optionsCopyEntries, setOptionsCopyEntries] = useState(true);
  const [optionsCopyTail, setOptionsCopyTail] = useState(true);
  const [optionsKeybindOverrides, setOptionsKeybindOverrides] = useState("move-forward=W,Up;fire-weapon=MouseLeft,RControl");
  const [optionsPatchRun, setOptionsPatchRun] = useState<WorkbenchJobRunSummary | null>(null);
  const [optionsPatchBusy, setOptionsPatchBusy] = useState<string | null>(null);
  const [optionsPatchError, setOptionsPatchError] = useState<string | null>(null);
  const [patchWorkflowSourcePath, setPatchWorkflowSourcePath] = useState("");
  const [patchIds, setPatchIds] = useState("stable");
  const [copiedExecutablePath, setCopiedExecutablePath] = useState("");
  const [copiedExecutableBackupPath, setCopiedExecutableBackupPath] = useState("");
  const [patchWorkflowRun, setPatchWorkflowRun] = useState<WorkbenchJobRunSummary | null>(null);
  const [patchWorkflowBusy, setPatchWorkflowBusy] = useState<string | null>(null);
  const [patchWorkflowError, setPatchWorkflowError] = useState<string | null>(null);
  const [readinessBusy, setReadinessBusy] = useState(false);
  const [readinessError, setReadinessError] = useState<string | null>(null);
  const [commandQuery, setCommandQuery] = useState("");
  const [activeNav, setActiveNav] = useState("overview");

  const contentAudienceCounts = useMemo(() => {
    const items = contentIndex?.items ?? [];
    return {
      all: items.length,
      community: items.filter((item) => item.communitySafe).length,
      maintainer: items.filter((item) => !item.communitySafe).length
    };
  }, [contentIndex]);

  const visibleContentItems = useMemo(() => {
    const query = contentQuery.trim().toLowerCase();
    if (!contentIndex) return [];

    return contentIndex.items.filter((item) => {
      const audienceMatches =
        contentAudienceFilter === "all" ||
        (contentAudienceFilter === "community" ? item.communitySafe : !item.communitySafe);
      const queryMatches =
        !query ||
        [item.title, item.group, item.relativePath, item.description].some((value) =>
          value.toLowerCase().includes(query)
        );
      return audienceMatches && queryMatches;
    });
  }, [contentAudienceFilter, contentIndex, contentQuery]);

  const parityDiagnosticCount = useMemo(
    () => jobCatalog?.definitions.filter((job) => job.lane === "appcore").length ?? 0,
    [jobCatalog]
  );

  const visibleJobDefinitions = useMemo(
    () => jobCatalog?.definitions.filter((job) => showParityDiagnostics || job.lane !== "appcore") ?? [],
    [jobCatalog, showParityDiagnostics]
  );

  const commandResults = useMemo<WorkbenchCommandResult[]>(() => {
    const query = commandQuery.trim().toLowerCase();
    if (!query) return [];

    const sectionResults = navItems
      .filter((item) => [item.label, item.shortLabel, item.detail].some((value) => value.toLowerCase().includes(query)))
      .map((item) => ({
        id: `section:${item.id}`,
        label: item.label,
        detail: item.detail,
        navId: item.id,
        kind: "section" as const
      }));

    const jobResults = visibleJobDefinitions
      .filter((job) => [job.title, job.id, job.detail, job.lane].some((value) => value.toLowerCase().includes(query)))
      .slice(0, 6)
      .map((job) => ({
        id: `job:${job.id}`,
        label: job.title,
        detail: `${job.lane} / ${formatEvidenceType(job.artifactSchema)}`,
        navId: navForJobLane(job.lane),
        kind: "job" as const
      }));

    return [...sectionResults, ...jobResults].slice(0, 8);
  }, [commandQuery, visibleJobDefinitions]);

  const agenticLoopRows = useMemo(() => {
    const jobStatus = (ids: string[]): "pending" | "ready" | "blocked" => {
      const definitions = jobCatalog?.definitions.filter((job) => ids.includes(job.id)) ?? [];
      if (definitions.length === 0) return "pending";
      return definitions.every((job) => job.status === "available") ? "ready" : "blocked";
    };
    const jobTitles = (ids: string[]) =>
      ids
        .map((id) => jobCatalog?.definitions.find((job) => job.id === id)?.title ?? id)
        .join(", ");

    return [
      {
        label: "Profile inventory",
        state: gameHarnessProfile?.ready ? "ready" : "check",
        tone: gameHarnessProfile?.ready ? "good" : "warn",
        detail: "Detect a game folder, required DLLs, defaultoptions.bea, and BEA.exe.",
        jobs: jobTitles(["game.inventoryProfile", "patch.verifySpecimen"])
      },
      {
        label: "Safe copied profile",
        state: safeProfileRun?.status === "completed" ? "copied" : jobStatus(["game.prepareSafeProfile"]),
        tone: safeProfileRun?.status === "completed" || jobStatus(["game.prepareSafeProfile"]) === "ready" ? "good" : "warn",
        detail: "Create an app-owned game copy before launch, patch, or debugger jobs touch anything.",
        jobs: jobTitles(["game.prepareSafeProfile"])
      },
      {
        label: "Launch and attach",
        state: jobStatus(["game.launchProfile", "debug.startProbeServer"]),
        tone: jobStatus(["game.launchProfile", "debug.startProbeServer"]) === "ready" ? "good" : "warn",
        detail: "Launch a copied profile and attach CDB through fixed confirmation phrases and approved helpers.",
        jobs: jobTitles(["game.launchProfile", "debug.startProbeServer"])
      },
      {
        label: "Runtime evidence",
        state: jobStatus(["runtime.listManagedProcesses", "runtime.tailManagedLog", "runtime.stopManagedProcess"]),
        tone:
          jobStatus(["runtime.listManagedProcesses", "runtime.tailManagedLog", "runtime.stopManagedProcess"]) === "ready"
            ? "good"
            : "warn",
        detail: "Track managed PIDs, stop recorded processes, and inspect bounded log tails from recorded evidence files.",
        jobs: jobTitles(["runtime.listManagedProcesses", "runtime.tailManagedLog", "runtime.stopManagedProcess"])
      },
      {
        label: "Ghidra evidence",
        state: jobStatus(["ghidra.exportWeakFunctions", "ghidra.exportAddressDecompile", "ghidra.validateRenameMap"]),
        tone:
          jobStatus(["ghidra.exportWeakFunctions", "ghidra.exportAddressDecompile", "ghidra.validateRenameMap"]) === "ready"
            ? "good"
            : "warn",
        detail: "Run read-only headless exports and rename-map dry-runs into evidence files before any confirmed apply.",
        jobs: jobTitles(["ghidra.exportWeakFunctions", "ghidra.exportAddressDecompile", "ghidra.validateRenameMap"])
      },
      {
        label: "Visual play loop",
        state: jobStatus([
          "game.planWindowCapture",
          "game.captureWindowFrame",
          "game.captureWindowSequence",
          "game.planWindowInput",
          "game.sendWindowInput"
        ]),
        tone:
          jobStatus([
            "game.planWindowCapture",
            "game.captureWindowFrame",
            "game.captureWindowSequence",
            "game.planWindowInput",
            "game.sendWindowInput"
          ]) === "ready"
            ? "warn"
            : "neutral",
        detail:
          "BEA window discovery, bounded still-frame/sequence capture, and explicitly armed scoped keyboard input are available; persistent live frame streaming remains planned.",
        jobs: jobTitles([
          "game.planWindowCapture",
          "game.captureWindowFrame",
          "game.captureWindowSequence",
          "game.planWindowInput",
          "game.sendWindowInput"
        ])
      }
    ] satisfies Array<{ label: string; state: string; tone: Tone; detail: string; jobs: string }>;
  }, [gameHarnessProfile, jobCatalog, safeProfileRun]);
  const capturePlanJob = jobCatalog?.definitions.find((job) => job.id === "game.planWindowCapture") ?? null;
  const capturePlanRun =
    jobRun?.definitionId === "game.planWindowCapture"
      ? jobRun
      : jobHistory.find((run) => run.definitionId === "game.planWindowCapture") ?? null;
  const frameCaptureJob = jobCatalog?.definitions.find((job) => job.id === "game.captureWindowFrame") ?? null;
  const frameCaptureRun =
    jobRun?.definitionId === "game.captureWindowFrame"
      ? jobRun
      : jobHistory.find((run) => run.definitionId === "game.captureWindowFrame") ?? null;
  const frameSequenceJob = jobCatalog?.definitions.find((job) => job.id === "game.captureWindowSequence") ?? null;
  const frameSequenceRun =
    jobRun?.definitionId === "game.captureWindowSequence"
      ? jobRun
      : jobHistory.find((run) => run.definitionId === "game.captureWindowSequence") ?? null;
  const launchProfileJob = jobCatalog?.definitions.find((job) => job.id === "game.launchProfile") ?? null;
  const launchProfileRun =
    jobRun?.definitionId === "game.launchProfile"
      ? jobRun
      : jobHistory.find((run) => run.definitionId === "game.launchProfile") ?? null;
  const stopManagedProcessJob = jobCatalog?.definitions.find((job) => job.id === "runtime.stopManagedProcess") ?? null;
  const stopManagedProcessRun =
    jobRun?.definitionId === "runtime.stopManagedProcess"
      ? jobRun
      : jobHistory.find((run) => run.definitionId === "runtime.stopManagedProcess") ?? null;
  const inputPlanJob = jobCatalog?.definitions.find((job) => job.id === "game.planWindowInput") ?? null;
  const inputSendJob = jobCatalog?.definitions.find((job) => job.id === "game.sendWindowInput") ?? null;
  const inputRun =
    jobRun?.definitionId === "game.planWindowInput" || jobRun?.definitionId === "game.sendWindowInput"
      ? jobRun
      : jobHistory.find((run) => run.definitionId === "game.sendWindowInput" || run.definitionId === "game.planWindowInput") ?? null;
  const framePreviewDataUrl = frameCaptureRun ? getJobDetail(frameCaptureRun, "Frame preview data URL") : "";
  const hasFramePreview = framePreviewDataUrl.startsWith("data:image/");
  const windowedPatchTargetPath = copiedExecutablePath.trim();
  const hasWindowedPatchTarget = windowedPatchTargetPath.length > 0;

  const visibleGoodieRows = useMemo(() => {
    const query = goodieQuery.trim().toLowerCase();
    const rows = saveInspection?.goodieRows ?? [];
    return rows.filter((row) => {
      const stateMatches =
        goodieStateFilter === "all" ||
        (goodieStateFilter === "unlocked"
          ? row.stateGroup === "new" || row.stateGroup === "old"
          : row.stateGroup === goodieStateFilter);
      const queryMatches =
        !query ||
        [row.index.toString(), row.title, row.contentType, row.unlockHint, row.assetHint, row.mediaQuery].some((value) =>
          value.toLowerCase().includes(query)
        );
      return stateMatches && queryMatches;
    });
  }, [goodieQuery, goodieStateFilter, saveInspection]);

  useEffect(() => {
    void getOnslaughtApi()
      .getRuntimeSnapshot()
      .then(setSnapshot);
  }, []);

  useEffect(() => {
    void refreshReadiness();
  }, []);

  useEffect(() => {
    void refreshContentIndex();
  }, []);

  useEffect(() => {
    void refreshReleasePolicy();
  }, []);

  useEffect(() => {
    if (activeNav === "media" && !mediaCatalog && !mediaBusy && !mediaQuery.trim() && mediaKindFilter === "all") {
      void refreshMediaCatalog();
    }
  }, [activeNav, mediaCatalog, mediaBusy, mediaKindFilter, mediaQuery]);

  useEffect(() => {
    return getOnslaughtApi().onWorkbenchJobProgress((event) => {
      setJobProgress((progress) => [event, ...progress.filter((entry) => entry.emittedAt !== event.emittedAt)].slice(0, 16));
    });
  }, []);

  async function refreshReadiness() {
    setReadinessBusy(true);
    setReadinessError(null);
    try {
      const api = getOnslaughtApi();
      const [ghidra, debug, harness, jobs, history] = await Promise.all([
        api.getGhidraReadiness(),
        api.getDebugReadiness(),
        api.getGameHarnessProfile(),
        api.getJobCatalog(),
        api.listWorkbenchJobRuns()
      ]);
      setGhidraReadiness(ghidra);
      setDebugReadiness(debug);
      setGameHarnessProfile(harness);
      setGameFolderPath(harness.gameRoot);
      setJobCatalog(jobs);
      setJobHistory(history);
    } catch (error) {
      setReadinessError(error instanceof Error ? error.message : "Failed to read RE tool readiness.");
    } finally {
      setReadinessBusy(false);
    }
  }

  async function refreshContentIndex() {
    setContentBusy(true);
    setContentError(null);
    try {
      const api = getOnslaughtApi();
      const index = await api.getContentIndex();
      setContentIndex(index);
      if (index.items.length > 0) {
        setContentDocument(await api.readContentDocument(index.items[0].id));
      }
    } catch (error) {
      setContentError(error instanceof Error ? error.message : "Failed to load content index.");
    } finally {
      setContentBusy(false);
    }
  }

  async function selectContentDocument(id: string) {
    setContentBusy(true);
    setContentError(null);
    try {
      setContentDocument(await getOnslaughtApi().readContentDocument(id));
    } catch (error) {
      setContentError(error instanceof Error ? error.message : "Failed to read content document.");
    } finally {
      setContentBusy(false);
    }
  }

  async function refreshMediaCatalog(query = mediaQuery, kind = mediaKindFilter) {
    setMediaBusy(true);
    setMediaError(null);
    try {
      setMediaCatalog(await getOnslaughtApi().getMediaCatalog(query, kind, 80));
    } catch (error) {
      setMediaError(error instanceof Error ? error.message : "Failed to load media catalog.");
    } finally {
      setMediaBusy(false);
    }
  }

  async function openGoodieMedia(row: SaveInspectionSummary["goodieRows"][number]) {
    const query = row.mediaQuery || row.assetHint || row.title;
    const kind: MediaCatalogKindFilter = row.contentType === "FMV" ? "video" : "all";
    setMediaQuery(query);
    setMediaKindFilter(kind);
    setActiveNav("media");
    await refreshMediaCatalog(query, kind);
  }

  async function openVideoGroup(query: string) {
    setMediaQuery(query);
    setMediaKindFilter("video");
    await refreshMediaCatalog(query, "video");
  }

  async function loadAudioPlayback(playbackId: string) {
    setAudioPlaybackBusy(playbackId);
    setAudioPlaybackError(null);
    try {
      setAudioPlayback(await getOnslaughtApi().getAudioPlayback(playbackId));
    } catch (error) {
      setAudioPlaybackError(error instanceof Error ? error.message : "Failed to load audio playback.");
    } finally {
      setAudioPlaybackBusy(null);
    }
  }

  async function prepareVideoPlayback(videoPlaybackId: string) {
    setVideoPlaybackBusy(videoPlaybackId);
    setVideoPlaybackError(null);
    try {
      setVideoPlayback(await getOnslaughtApi().prepareVideoPlayback(videoPlaybackId));
    } catch (error) {
      setVideoPlaybackError(error instanceof Error ? error.message : "Failed to prepare video playback.");
    } finally {
      setVideoPlaybackBusy(null);
    }
  }

  async function loadMediaPreview(previewId: string) {
    setMediaPreviewBusy(previewId);
    setMediaPreviewError(null);
    try {
      setMediaPreview(await getOnslaughtApi().getMediaPreview(previewId));
    } catch (error) {
      setMediaPreviewError(error instanceof Error ? error.message : "Failed to load media preview.");
    } finally {
      setMediaPreviewBusy(null);
    }
  }

  async function refreshReleasePolicy() {
    setReleaseBusy(true);
    setReleaseError(null);
    try {
      setReleasePolicy(await getOnslaughtApi().getReleasePolicy());
    } catch (error) {
      setReleaseError(error instanceof Error ? error.message : "Failed to read release policy.");
    } finally {
      setReleaseBusy(false);
    }
  }

  async function selectAndInspectGameFolder() {
    setGameFolderBusy(true);
    setGameFolderError(null);
    try {
      const result = await getOnslaughtApi().selectAndInspectGameFolder();
      if (result) {
        setGameHarnessProfile(result);
        setGameFolderPath(result.gameRoot);
        const jobs = await getOnslaughtApi().getJobCatalog();
        setJobCatalog(jobs);
      }
    } catch (error) {
      setGameFolderError(error instanceof Error ? error.message : "Failed to inspect game folder.");
    } finally {
      setGameFolderBusy(false);
    }
  }

  async function inspectTypedGameFolder() {
    const trimmed = gameFolderPath.trim();
    if (!trimmed) {
      setGameFolderError("Enter or select a game folder first.");
      return;
    }

    setGameFolderBusy(true);
    setGameFolderError(null);
    try {
      const result = await getOnslaughtApi().inspectGameFolderPath(trimmed, true);
      setGameHarnessProfile(result);
      setGameFolderPath(result.gameRoot);
      const jobs = await getOnslaughtApi().getJobCatalog();
      setJobCatalog(jobs);
    } catch (error) {
      setGameFolderError(error instanceof Error ? error.message : "Failed to inspect game folder.");
    } finally {
      setGameFolderBusy(false);
    }
  }

  async function resetGameFolderProfile() {
    setGameFolderBusy(true);
    setGameFolderError(null);
    try {
      const result = await getOnslaughtApi().resetGameFolderProfile();
      setGameHarnessProfile(result);
      setGameFolderPath(result.gameRoot);
      const jobs = await getOnslaughtApi().getJobCatalog();
      setJobCatalog(jobs);
    } catch (error) {
      setGameFolderError(error instanceof Error ? error.message : "Failed to reset game folder.");
    } finally {
      setGameFolderBusy(false);
    }
  }

  async function prepareSafeGameProfile() {
    setSafeProfileBusy(true);
    setSafeProfileError(null);
    setSafeProfileRun(null);
    setJobProgress([]);
    try {
      const runIdSuffix = new Date().toISOString().replace(/\D/g, "").slice(0, 14);
      const result = await getOnslaughtApi().startWorkbenchJob({
        definitionId: "game.prepareSafeProfile",
        inputs: {
          sourceGameRoot: gameFolderPath.trim() || gameHarnessProfile?.gameRoot || null,
          profileName: `bea-safe-profile-${runIdSuffix}`,
          armPhrase: "COPY GAME PROFILE",
          acceptsLocalCopy: true
        }
      });
      setSafeProfileRun(result);
      setJobRun(result);
      setJobProgress(result.progress.slice().reverse());
      setJobHistory((history) => [result, ...history.filter((entry) => entry.runId !== result.runId)].slice(0, 12));

      const targetGameRoot = getJobDetail(result, "Target game root");
      if (targetGameRoot) {
        const profile = await getOnslaughtApi().inspectGameFolderPath(targetGameRoot, true);
        setGameHarnessProfile(profile);
        setGameFolderPath(profile.gameRoot);
        setSpecimenPath(profile.executablePath);
        setAddressExecutablePath(profile.executablePath);
        setPatchWorkflowSourcePath(profile.executablePath);
        setCopiedExecutablePath(profile.executablePath);
        setPatchIds("force_windowed");
        const jobs = await getOnslaughtApi().getJobCatalog();
        setJobCatalog(jobs);
      }
    } catch (error) {
      setSafeProfileError(error instanceof Error ? error.message : "Failed to prepare copied game profile.");
    } finally {
      setSafeProfileBusy(false);
    }
  }

  function currentSaveSourcePath() {
    return savePath.trim() || saveInspection?.selectedPath || "save-attempts\\haha-cannon-goes-brrrrr.bes";
  }

  function currentSavePatchTargetPath() {
    return copiedSavePath.trim() || currentSaveSourcePath();
  }

  function savePatchIntent(targetPath: string): Record<string, WorkbenchJobInputValue> {
    return {
      path: targetPath,
      rank: savePatchRank,
      kills: savePatchKills,
      patchNodes: savePatchNodes,
      patchLinks: savePatchLinks,
      patchGoodies: savePatchGoodies,
      patchKills: savePatchKillsEnabled,
      levelRanks: savePatchLevelRanks,
      perCategoryKills: savePatchCategoryKills
    };
  }

  function recordSavePatchRun(result: WorkbenchJobRunSummary) {
    setSavePatchRun(result);
    setJobRun(result);
    setJobProgress(result.progress.slice().reverse());
    setJobHistory((history) => [result, ...history.filter((entry) => entry.runId !== result.runId)].slice(0, 12));

    const copiedTarget = getJobDetail(result, "Copied target") || getJobDetail(result, "Target");
    const backup = getJobDetail(result, "Backup");
    if (copiedTarget) {
      setCopiedSavePath(copiedTarget);
    }
    if (backup) {
      setCopiedSaveBackupPath(backup);
    }
  }

  async function runSavePatchWorkflow(definitionId: string) {
    setSavePatchBusy(definitionId);
    setSavePatchError(null);
    setJobProgress([]);
    try {
      let inputs: Record<string, WorkbenchJobInputValue>;
      if (definitionId === "save.prepareCopy") {
        inputs = {
          sourcePath: currentSaveSourcePath(),
          armPhrase: "COPY SAVE FILE",
          acceptsLocalCopy: true
        };
      } else if (definitionId === "save.restoreBackup") {
        inputs = {
          targetPath: copiedSavePath.trim(),
          backupPath: copiedSaveBackupPath.trim(),
          armPhrase: "RESTORE SAVE BACKUP",
          acceptsSaveWrite: true
        };
      } else {
        inputs = savePatchIntent(definitionId === "save.applyPatch" ? currentSavePatchTargetPath() : currentSaveSourcePath());
        if (definitionId === "save.applyPatch") {
          inputs.armPhrase = "APPLY SAVE PATCH";
          inputs.acceptsSaveWrite = true;
        }
      }

      const result = await getOnslaughtApi().startWorkbenchJob({
        definitionId,
        inputs
      });
      recordSavePatchRun(result);

      const copiedTarget = getJobDetail(result, "Copied target") || getJobDetail(result, "Target");
      if (copiedTarget && !copiedTarget.startsWith("browser://")) {
        try {
          const inspection = await getOnslaughtApi().inspectSaveFilePath(copiedTarget);
          setSaveInspection(inspection);
          setSavePath(inspection.selectedPath);
        } catch {
          // The job artifact is authoritative; inspection refresh is best-effort for unsupported fixture URLs.
        }
      }
    } catch (error) {
      setSavePatchError(error instanceof Error ? error.message : "Failed to run save patch workflow.");
    } finally {
      setSavePatchBusy(null);
    }
  }

  function currentOptionsSourcePath() {
    return (
      optionsPath.trim() ||
      (saveInspection?.isOptionsFile ? saveInspection.selectedPath : "") ||
      (gameHarnessProfile?.gameRoot ? `${gameHarnessProfile.gameRoot}\\defaultoptions.bea` : "game\\defaultoptions.bea")
    );
  }

  function currentOptionsPatchTargetPath() {
    return copiedOptionsPath.trim() || currentOptionsSourcePath();
  }

  function optionalPatchValue(enabled: boolean, value: string): WorkbenchJobInputValue {
    return enabled ? value : null;
  }

  function optionalPatchBoolean(enabled: boolean, value: boolean): WorkbenchJobInputValue {
    return enabled ? value : null;
  }

  function optionsPatchIntent(targetPath: string): Record<string, WorkbenchJobInputValue> {
    const copyOptionsFromPath = optionsCopyFromPath.trim();
    return {
      path: targetPath,
      soundVolume: optionalPatchValue(optionsSoundVolumeEnabled, optionsSoundVolume),
      musicVolume: optionalPatchValue(optionsMusicVolumeEnabled, optionsMusicVolume),
      invertWalkerP1: optionalPatchBoolean(optionsInvertWalkerP1Enabled, optionsInvertWalkerP1),
      invertWalkerP2: optionalPatchBoolean(optionsInvertWalkerP2Enabled, optionsInvertWalkerP2),
      invertFlightP1: optionalPatchBoolean(optionsInvertFlightP1Enabled, optionsInvertFlightP1),
      invertFlightP2: optionalPatchBoolean(optionsInvertFlightP2Enabled, optionsInvertFlightP2),
      vibrationP1: optionalPatchBoolean(optionsVibrationP1Enabled, optionsVibrationP1),
      vibrationP2: optionalPatchBoolean(optionsVibrationP2Enabled, optionsVibrationP2),
      controllerConfigP1: optionalPatchValue(optionsControllerConfigP1Enabled, optionsControllerConfigP1),
      controllerConfigP2: optionalPatchValue(optionsControllerConfigP2Enabled, optionsControllerConfigP2),
      mouseSensitivity: optionalPatchValue(optionsMouseSensitivityEnabled, optionsMouseSensitivity),
      controlSchemeIndex: optionalPatchValue(optionsControlSchemeEnabled, optionsControlSchemeIndex),
      languageIndex: optionalPatchValue(optionsLanguageEnabled, optionsLanguageIndex),
      screenShape: optionalPatchValue(optionsScreenShapeEnabled, optionsScreenShape),
      d3dDeviceIndex: optionalPatchValue(optionsD3dDeviceEnabled, optionsD3dDeviceIndex),
      copyOptionsFromPath: copyOptionsFromPath || null,
      copyOptionsEntries: copyOptionsFromPath ? optionsCopyEntries : false,
      copyOptionsTail: copyOptionsFromPath ? optionsCopyTail : false,
      keybindOverrides: optionsKeybindOverrides
    };
  }

  function recordOptionsPatchRun(result: WorkbenchJobRunSummary) {
    setOptionsPatchRun(result);
    setJobRun(result);
    setJobProgress(result.progress.slice().reverse());
    setJobHistory((history) => [result, ...history.filter((entry) => entry.runId !== result.runId)].slice(0, 12));

    const copiedTarget = getJobDetail(result, "Copied target") || getJobDetail(result, "Target");
    const backup = getJobDetail(result, "Backup");
    if (copiedTarget) {
      setCopiedOptionsPath(copiedTarget);
    }
    if (backup) {
      setCopiedOptionsBackupPath(backup);
    }
  }

  async function runOptionsPatchWorkflow(definitionId: string) {
    setOptionsPatchBusy(definitionId);
    setOptionsPatchError(null);
    setJobProgress([]);
    try {
      let inputs: Record<string, WorkbenchJobInputValue>;
      if (definitionId === "save.prepareCopy") {
        inputs = {
          sourcePath: currentOptionsSourcePath(),
          armPhrase: "COPY SAVE FILE",
          acceptsLocalCopy: true
        };
      } else if (definitionId === "save.restoreBackup") {
        inputs = {
          targetPath: copiedOptionsPath.trim(),
          backupPath: copiedOptionsBackupPath.trim(),
          armPhrase: "RESTORE SAVE BACKUP",
          acceptsSaveWrite: true
        };
      } else {
        inputs = optionsPatchIntent(definitionId === "settings.applyOptionsPatch" ? currentOptionsPatchTargetPath() : currentOptionsSourcePath());
        if (definitionId === "settings.applyOptionsPatch") {
          inputs.armPhrase = "APPLY OPTIONS PATCH";
          inputs.acceptsOptionsWrite = true;
        }
      }

      const result = await getOnslaughtApi().startWorkbenchJob({
        definitionId,
        inputs
      });
      recordOptionsPatchRun(result);

      const copiedTarget = getJobDetail(result, "Copied target") || getJobDetail(result, "Target");
      if (copiedTarget && !copiedTarget.startsWith("browser://")) {
        try {
          const inspection = await getOnslaughtApi().inspectSaveFilePath(copiedTarget);
          setSaveInspection(inspection);
          setSavePath(inspection.selectedPath);
          setOptionsPath(inspection.selectedPath);
        } catch {
          // Preview-mode and future virtual artifact URLs do not need a secondary inspection refresh.
        }
      }
    } catch (error) {
      setOptionsPatchError(error instanceof Error ? error.message : "Failed to run options patch workflow.");
    } finally {
      setOptionsPatchBusy(null);
    }
  }

  function currentPatchSourcePath() {
    return patchWorkflowSourcePath.trim() || specimenPath.trim() || gameHarnessProfile?.executablePath || "game\\BEA.exe";
  }

  function currentPatchTargetPath() {
    return copiedExecutablePath.trim() || currentPatchSourcePath();
  }

  function recordPatchWorkflowRun(result: WorkbenchJobRunSummary) {
    setPatchWorkflowRun(result);
    setJobRun(result);
    setJobProgress(result.progress.slice().reverse());
    setJobHistory((history) => [result, ...history.filter((entry) => entry.runId !== result.runId)].slice(0, 12));

    const copiedTarget = getJobDetail(result, "Copied target") || getJobDetail(result, "Target");
    const backup = getJobDetail(result, "Backup");
    if (copiedTarget) {
      setCopiedExecutablePath(copiedTarget);
    }
    if (backup) {
      setCopiedExecutableBackupPath(backup);
    }
  }

  async function runPatchWorkflow(definitionId: string, patchIdsOverride?: string) {
    setPatchWorkflowBusy(definitionId);
    setPatchWorkflowError(null);
    setJobProgress([]);
    try {
      let inputs: Record<string, WorkbenchJobInputValue>;
      const selectedPatchIds = patchIdsOverride ?? patchIds;
      if (definitionId === "patch.prepareExecutableCopy") {
        inputs = {
          sourcePath: currentPatchSourcePath(),
          armPhrase: "COPY BEA EXE",
          acceptsLocalCopy: true
        };
      } else if (definitionId === "patch.restoreCatalogBackup") {
        inputs = {
          targetPath: copiedExecutablePath.trim(),
          backupPath: copiedExecutableBackupPath.trim(),
          armPhrase: "RESTORE CATALOG BACKUP",
          acceptsExecutableWrite: true
        };
      } else {
        inputs = {
          executablePath: definitionId === "patch.applyCatalogPatch" ? currentPatchTargetPath() : currentPatchSourcePath(),
          patchIds: selectedPatchIds
        };
        if (definitionId === "patch.applyCatalogPatch") {
          inputs.armPhrase = "APPLY CATALOG PATCH";
          inputs.acceptsExecutableWrite = true;
        }
      }

      const result = await getOnslaughtApi().startWorkbenchJob({
        definitionId,
        inputs
      });
      recordPatchWorkflowRun(result);

      const copiedTarget = getJobDetail(result, "Copied target") || getJobDetail(result, "Target");
      if (copiedTarget && !copiedTarget.startsWith("browser://")) {
        try {
          const verification = await getOnslaughtApi().verifyExecutablePath(copiedTarget);
          setSpecimen(verification);
          setSpecimenPath(verification.selectedPath);
        } catch {
          // Preview-mode and future virtual artifact URLs do not need a secondary verification refresh.
        }
      }
    } catch (error) {
      setPatchWorkflowError(error instanceof Error ? error.message : "Failed to run executable patch workflow.");
    } finally {
      setPatchWorkflowBusy(null);
    }
  }

  async function runWindowedPatchWorkflow(definitionId: "patch.planCatalogPatch" | "patch.applyCatalogPatch") {
    if (!hasWindowedPatchTarget) {
      setPatchWorkflowError("Prepare a copied profile or copy BEA.exe into the workspace before applying the windowed patch.");
      return;
    }

    setPatchIds("force_windowed");
    setPatchWorkflowBusy(definitionId);
    setPatchWorkflowError(null);
    setJobProgress([]);
    try {
      const result = await getOnslaughtApi().startWorkbenchJob({
        definitionId,
        inputs: {
          executablePath: windowedPatchTargetPath,
          patchIds: "force_windowed",
          ...(definitionId === "patch.applyCatalogPatch"
            ? {
                armPhrase: "APPLY CATALOG PATCH",
                acceptsExecutableWrite: true
              }
            : {})
        }
      });
      recordPatchWorkflowRun(result);

      if (snapshot?.mode !== "browser-mock" && !windowedPatchTargetPath.startsWith("browser://")) {
        try {
          const verification = await getOnslaughtApi().verifyExecutablePath(windowedPatchTargetPath);
          setSpecimen(verification);
          setSpecimenPath(verification.selectedPath);
        } catch {
          // The patch apply result already records the typed artifact; verification refresh is best effort.
        }
      }
    } catch (error) {
      setPatchWorkflowError(error instanceof Error ? error.message : "Failed to run the windowed patch workflow.");
    } finally {
      setPatchWorkflowBusy(null);
    }
  }

  function openPatchBenchForWindowedPatch() {
    setPatchIds("force_windowed");
    if (gameHarnessProfile?.executablePath) {
      setPatchWorkflowSourcePath(gameHarnessProfile.executablePath);
    }
    setActiveNav("patches");
  }

  function canRunWorkbenchJob(job: WorkbenchJobDefinition) {
    const runnableReadOnly = [
      "save.planPatch",
      "save.previewPatch",
      "settings.planOptionsPatch",
      "settings.previewOptionsPatch",
      "appcore.inspectSave",
      "appcore.compareSaves",
      "appcore.planSavePatch",
      "appcore.previewSavePatch",
      "file.hexRead",
      "file.peAddressConvert",
      "patch.verifySpecimen",
      "patch.planCatalogPatch",
      "release.inspectPolicy",
      "debug.planProbeSession",
      "debug.resolveCdb",
      "runtime.listManagedProcesses",
      "runtime.tailManagedLog",
      "ghidra.exportAddressDecompile",
      "ghidra.exportWeakFunctions",
      "ghidra.validateRenameMap",
      "game.inventoryProfile",
      "game.captureWindowFrame",
      "game.captureWindowSequence",
      "game.planWindowCapture",
      "game.planWindowInput",
      "game.planLaunchProfile",
      "assets.catalogGameFiles",
      "content.readDocument"
    ];
    const runnableLaunchGated = ["debug.startProbeServer", "game.launchProfile", "runtime.stopManagedProcess", "game.sendWindowInput"];
    const runnableMutationGated = [
      "save.applyPatch",
      "save.prepareCopy",
      "save.restoreBackup",
      "settings.applyOptionsPatch",
      "patch.prepareExecutableCopy",
      "patch.applyCatalogPatch",
      "patch.restoreCatalogBackup",
      "game.prepareSafeProfile",
      "ghidra.applyRenameMap"
    ];

    if (job.status !== "available") {
      return false;
    }
    if (job.safety === "read-only") {
      return runnableReadOnly.includes(job.id);
    }
    return (
      launchJobsArmed &&
      ((job.safety === "launch-gated" && runnableLaunchGated.includes(job.id)) ||
        (job.safety === "mutation-gated" && runnableMutationGated.includes(job.id)))
    );
  }

  function buildJobInputs(definitionId: string): Record<string, WorkbenchJobInputValue> {
    switch (definitionId) {
      case "file.hexRead":
        return {
          path: hexPath.trim() || gameHarnessProfile?.executablePath || specimenPath.trim() || "",
          offset: hexOffset,
          length: hexLength
        };
      case "file.peAddressConvert":
        return {
          executablePath: addressExecutablePath.trim() || specimenPath.trim() || gameHarnessProfile?.executablePath || "",
          virtualAddress
        };
      case "save.prepareCopy":
        return {
          sourcePath: currentSaveSourcePath(),
          armPhrase: "COPY SAVE FILE",
          acceptsLocalCopy: true
        };
      case "save.planPatch":
        return savePatchIntent(currentSaveSourcePath());
      case "save.previewPatch":
        return savePatchIntent(currentSaveSourcePath());
      case "save.applyPatch":
        return {
          ...savePatchIntent(currentSavePatchTargetPath()),
          armPhrase: "APPLY SAVE PATCH",
          acceptsSaveWrite: true
        };
      case "save.restoreBackup":
        const lastSaveBackup = jobRun?.result.details.find((detail) => detail.label === "Backup")?.value ?? "";
        const lastSaveTarget = jobRun?.result.details.find((detail) => detail.label === "Target")?.value ?? "";
        return {
          targetPath:
            copiedSavePath.trim() || lastSaveTarget || savePath.trim() || saveInspection?.selectedPath || "save-attempts\\haha-cannon-goes-brrrrr.bes",
          backupPath: copiedSaveBackupPath.trim() || lastSaveBackup,
          armPhrase: "RESTORE SAVE BACKUP",
          acceptsSaveWrite: true
        };
      case "settings.planOptionsPatch":
      case "settings.previewOptionsPatch":
        return optionsPatchIntent(currentOptionsSourcePath());
      case "settings.applyOptionsPatch":
        return {
          ...optionsPatchIntent(currentOptionsPatchTargetPath()),
          armPhrase: "APPLY OPTIONS PATCH",
          acceptsOptionsWrite: true
        };
      case "appcore.inspectSave":
        return {
          path: savePath.trim() || saveInspection?.selectedPath || "save-attempts\\haha-cannon-goes-brrrrr.bes"
        };
      case "appcore.compareSaves":
        return {
          leftPath: leftComparePath.trim() || saveComparison?.leftPath || saveInspection?.selectedPath || "save-attempts\\haha-cannon-goes-brrrrr.bes",
          rightPath: rightComparePath.trim() || saveComparison?.rightPath || saveInspection?.selectedPath || "save-attempts\\haha-cannon-goes-brrrrr.bes"
        };
      case "appcore.planSavePatch":
        return {
          path: savePath.trim() || saveInspection?.selectedPath || "save-attempts\\haha-cannon-goes-brrrrr.bes",
          rank: "S",
          kills: 100,
          patchNodes: true,
          patchLinks: true,
          patchGoodies: true,
          patchKills: true,
          levelRanks: "1:S 2:A",
          perCategoryKills: "aircraft:100 mechs:20"
        };
      case "appcore.previewSavePatch":
        return {
          path: savePath.trim() || saveInspection?.selectedPath || "save-attempts\\haha-cannon-goes-brrrrr.bes",
          rank: "S",
          kills: 100
        };
      case "patch.verifySpecimen":
        return {
          executablePath: currentPatchSourcePath()
        };
      case "patch.prepareExecutableCopy":
        return {
          sourcePath: currentPatchSourcePath(),
          armPhrase: "COPY BEA EXE",
          acceptsLocalCopy: true
        };
      case "patch.planCatalogPatch":
        return {
          executablePath: currentPatchSourcePath(),
          patchIds
        };
      case "patch.applyCatalogPatch":
        return {
          executablePath: currentPatchTargetPath(),
          patchIds,
          armPhrase: "APPLY CATALOG PATCH",
          acceptsExecutableWrite: true
        };
      case "patch.restoreCatalogBackup": {
        const lastExecutableBackup = jobRun?.result.details.find((detail) => detail.label === "Backup")?.value ?? "";
        const lastExecutableTarget = jobRun?.result.details.find((detail) => detail.label === "Target")?.value ?? "";
        return {
          targetPath: copiedExecutablePath.trim() || lastExecutableTarget || currentPatchTargetPath(),
          backupPath: copiedExecutableBackupPath.trim() || lastExecutableBackup,
          armPhrase: "RESTORE CATALOG BACKUP",
          acceptsExecutableWrite: true
        };
      }
      case "release.inspectPolicy":
        return {};
      case "debug.planProbeSession":
        return {
          probeId: "pause-persist-wave1.cdb.txt",
          gameRoot: gameFolderPath.trim() || gameHarnessProfile?.gameRoot || null,
          port: 5005
        };
      case "debug.startProbeServer":
        return {
          processName: "BEA.exe",
          probeId: "pause-persist-wave1.cdb.txt",
          gameRoot: gameFolderPath.trim() || gameHarnessProfile?.gameRoot || null,
          port: 5005,
          armPhrase: "ATTACH CDB",
          acceptsRuntimeAttach: true
        };
      case "runtime.listManagedProcesses":
        return {};
      case "runtime.tailManagedLog": {
        const latestLogRun = jobHistory.find((run) => run.definitionId === "debug.startProbeServer");
        return {
          targetRunId: latestLogRun?.runId ?? null,
          byteLimit: 8192
        };
      }
      case "runtime.stopManagedProcess": {
        const latestManagedRun = jobHistory.find((run) =>
          ["game.launchProfile", "debug.startProbeServer"].includes(run.definitionId)
        );
        return {
          targetRunId: latestManagedRun?.runId ?? null,
          armPhrase: "STOP PROCESS",
          acceptsProcessStop: true
        };
      }
      case "ghidra.exportWeakFunctions":
        return {
          mode: "weak"
        };
      case "ghidra.exportAddressDecompile":
        return {
          addresses: "0x00421200",
          timeoutSec: 60
        };
      case "ghidra.validateRenameMap":
        return {
          mapPath: ""
        };
      case "ghidra.applyRenameMap":
        return {
          mapPath: "",
          dryRunArtifactPath: "",
          armPhrase: "APPLY GHIDRA RENAME MAP",
          acceptsGhidraMutation: true
        };
      case "game.inventoryProfile":
        return {
          gameRoot: gameFolderPath.trim() || gameHarnessProfile?.gameRoot || null
        };
      case "game.planWindowCapture":
      case "game.captureWindowFrame":
      case "game.captureWindowSequence": {
        const latestGameRun = jobHistory.find((run) => run.definitionId === "game.launchProfile");
        const baseInputs = {
          targetRunId: latestGameRun?.runId ?? null,
          processName: "BEA.exe",
          maxWidth: 960,
          maxHeight: 540
        };
        return definitionId === "game.captureWindowSequence"
          ? {
              ...baseInputs,
              frameCount: 3,
              intervalMs: 250
            }
          : baseInputs;
      }
      case "game.planWindowInput": {
        const latestGameRun = jobHistory.find((run) => run.definitionId === "game.launchProfile");
        const latestWindowRun = jobHistory.find((run) =>
          ["game.planWindowCapture", "game.captureWindowFrame"].includes(run.definitionId)
        );
        return {
          targetRunId: latestGameRun?.runId ?? null,
          hwndHex: latestWindowRun ? getJobDetail(latestWindowRun, "Window handle") || null : null,
          sequence: "tap:ENTER",
          stepDelayMs: 60
        };
      }
      case "game.sendWindowInput": {
        const latestGameRun = jobHistory.find((run) => run.definitionId === "game.launchProfile");
        const latestWindowRun = jobHistory.find((run) =>
          ["game.planWindowCapture", "game.captureWindowFrame"].includes(run.definitionId)
        );
        return {
          targetRunId: latestGameRun?.runId ?? null,
          hwndHex: latestWindowRun ? getJobDetail(latestWindowRun, "Window handle") || null : null,
          sequence: "tap:ENTER",
          stepDelayMs: 60,
          armPhrase: "SEND GAME INPUT",
          acceptsWindowInput: true
        };
      }
      case "game.planLaunchProfile":
        return {
          gameRoot: gameFolderPath.trim() || gameHarnessProfile?.gameRoot || null,
          args: ""
        };
      case "game.prepareSafeProfile":
        return {
          sourceGameRoot: gameFolderPath.trim() || gameHarnessProfile?.gameRoot || null,
          profileName: "bea-safe-profile",
          armPhrase: "COPY GAME PROFILE",
          acceptsLocalCopy: true
        };
      case "game.launchProfile":
        return {
          gameRoot: gameFolderPath.trim() || gameHarnessProfile?.gameRoot || null,
          args: "",
          armPhrase: "LAUNCH BEA",
          acceptsProfileWrites: true
        };
      case "assets.catalogGameFiles":
        return {};
      case "content.readDocument":
        return {
          id: contentDocument?.id || contentIndex?.items[0]?.id || "lore-book"
        };
      default:
        return {};
    }
  }

  async function runWorkbenchJob(job: WorkbenchJobDefinition) {
    setJobBusy(job.id);
    setJobError(null);
    setJobRun(null);
    setJobProgress([]);
    try {
      const result = await getOnslaughtApi().startWorkbenchJob({
        definitionId: job.id,
        inputs: buildJobInputs(job.id)
      });
      setJobRun(result);
      setJobProgress(result.progress.slice().reverse());
      setJobHistory((history) => [result, ...history.filter((entry) => entry.runId !== result.runId)].slice(0, 12));
    } catch (error) {
      setJobError(error instanceof Error ? error.message : "Failed to run workbench job.");
    } finally {
      setJobBusy(null);
    }
  }

  async function selectAndVerifyExecutable() {
    setVerifyBusy(true);
    setVerifyError(null);
    try {
      const result = await getOnslaughtApi().selectAndVerifyExecutable();
      if (result) {
        setSpecimen(result);
        setSpecimenPath(result.selectedPath);
        setAddressExecutablePath(result.selectedPath);
      }
    } catch (error) {
      setVerifyError(error instanceof Error ? error.message : "Failed to verify executable.");
    } finally {
      setVerifyBusy(false);
    }
  }

  async function verifyTypedPath() {
    const trimmed = specimenPath.trim();
    if (!trimmed) {
      setVerifyError("Enter or select a BEA.exe path first.");
      return;
    }

    setVerifyBusy(true);
    setVerifyError(null);
    try {
      const result = await getOnslaughtApi().verifyExecutablePath(trimmed);
      setSpecimen(result);
      setSpecimenPath(result.selectedPath);
      setAddressExecutablePath(result.selectedPath);
    } catch (error) {
      setVerifyError(error instanceof Error ? error.message : "Failed to verify executable.");
    } finally {
      setVerifyBusy(false);
    }
  }

  async function selectAndInspectSaveFile() {
    setInspectBusy(true);
    setInspectError(null);
    try {
      const result = await getOnslaughtApi().selectAndInspectSaveFile();
      if (result) {
        setSaveInspection(result);
        setSavePath(result.selectedPath);
      }
    } catch (error) {
      setInspectError(error instanceof Error ? error.message : "Failed to inspect save/options file.");
    } finally {
      setInspectBusy(false);
    }
  }

  async function inspectTypedSavePath() {
    const trimmed = savePath.trim();
    if (!trimmed) {
      setInspectError("Enter or select a .bes/.bea path first.");
      return;
    }

    setInspectBusy(true);
    setInspectError(null);
    try {
      const result = await getOnslaughtApi().inspectSaveFilePath(trimmed);
      setSaveInspection(result);
      setSavePath(result.selectedPath);
    } catch (error) {
      setInspectError(error instanceof Error ? error.message : "Failed to inspect save/options file.");
    } finally {
      setInspectBusy(false);
    }
  }

  async function selectAndCompareSaveFiles() {
    setCompareBusy(true);
    setCompareError(null);
    try {
      const result = await getOnslaughtApi().selectAndCompareSaveFiles();
      if (result) {
        setSaveComparison(result);
        setLeftComparePath(result.leftPath);
        setRightComparePath(result.rightPath);
      }
    } catch (error) {
      setCompareError(error instanceof Error ? error.message : "Failed to compare save/options files.");
    } finally {
      setCompareBusy(false);
    }
  }

  async function compareTypedSavePaths() {
    const left = leftComparePath.trim();
    const right = rightComparePath.trim();
    if (!left || !right) {
      setCompareError("Enter or select two .bes/.bea paths first.");
      return;
    }

    setCompareBusy(true);
    setCompareError(null);
    try {
      const result = await getOnslaughtApi().compareSaveFilePaths(left, right);
      setSaveComparison(result);
      setLeftComparePath(result.leftPath);
      setRightComparePath(result.rightPath);
    } catch (error) {
      setCompareError(error instanceof Error ? error.message : "Failed to compare save/options files.");
    } finally {
      setCompareBusy(false);
    }
  }

  async function selectAndReadHexFile() {
    setHexBusy(true);
    setHexError(null);
    try {
      const result = await getOnslaughtApi().selectAndReadHexFile(hexOffset, hexLength);
      if (result) {
        setHexRead(result);
        setHexPath(result.selectedPath);
      }
    } catch (error) {
      setHexError(error instanceof Error ? error.message : "Failed to read hex window.");
    } finally {
      setHexBusy(false);
    }
  }

  async function readTypedHexRange() {
    const trimmed = hexPath.trim();
    if (!trimmed) {
      setHexError("Enter or select a file path first.");
      return;
    }

    setHexBusy(true);
    setHexError(null);
    try {
      const result = await getOnslaughtApi().readHexRange(trimmed, hexOffset, hexLength);
      setHexRead(result);
      setHexPath(result.selectedPath);
    } catch (error) {
      setHexError(error instanceof Error ? error.message : "Failed to read hex window.");
    } finally {
      setHexBusy(false);
    }
  }

  async function convertTypedAddress() {
    const executable = addressExecutablePath.trim() || specimenPath.trim();
    if (!executable) {
      setAddressError("Enter or verify a BEA.exe path first.");
      return;
    }

    setAddressBusy(true);
    setAddressError(null);
    try {
      const result = await getOnslaughtApi().convertExecutableAddress(executable, virtualAddress);
      setAddressConversion(result);
      setAddressExecutablePath(result.executablePath);
    } catch (error) {
      setAddressError(error instanceof Error ? error.message : "Failed to convert virtual address.");
    } finally {
      setAddressBusy(false);
    }
  }

  const activeSection = useMemo(
    () => navItems.find((item) => item.id === activeNav)?.label ?? "Overview",
    [activeNav]
  );

  if (!snapshot) {
    return (
      <main className="grid min-h-screen place-items-center bg-workbench-base text-workbench-text">
        <div className="rounded-lg border border-workbench-border bg-workbench-panel p-6">
          <p className="font-mono text-sm text-workbench-muted">Loading workbench bridge...</p>
        </div>
      </main>
    );
  }

  const renderedSection =
    activeNav === "overview" ? (
      <HomeSection snapshot={snapshot} onNavigate={setActiveNav} />
    ) : activeNav === "saves" ? (
      <SaveLabSection
        saveInspection={saveInspection}
        savePath={savePath}
        goodieQuery={goodieQuery}
        goodieStateFilter={goodieStateFilter}
        visibleGoodieRows={visibleGoodieRows}
        inspectBusy={inspectBusy}
        inspectError={inspectError}
        copiedSavePath={copiedSavePath}
        copiedSaveBackupPath={copiedSaveBackupPath}
        savePatchRun={savePatchRun}
        savePatchBusy={savePatchBusy}
        savePatchError={savePatchError}
        optionsSoundVolumeEnabled={optionsSoundVolumeEnabled}
        optionsSoundVolume={optionsSoundVolume}
        optionsMusicVolumeEnabled={optionsMusicVolumeEnabled}
        optionsMusicVolume={optionsMusicVolume}
        optionsScreenShapeEnabled={optionsScreenShapeEnabled}
        optionsScreenShape={optionsScreenShape}
        optionsD3dDeviceEnabled={optionsD3dDeviceEnabled}
        optionsD3dDeviceIndex={optionsD3dDeviceIndex}
        optionsCopyFromPath={optionsCopyFromPath}
        optionsCopyEntries={optionsCopyEntries}
        optionsPatchRun={optionsPatchRun}
        optionsPatchBusy={optionsPatchBusy}
        optionsPatchError={optionsPatchError}
        onSavePathChange={setSavePath}
        onGoodieQueryChange={setGoodieQuery}
        onGoodieStateFilterChange={setGoodieStateFilter}
        onBrowseSave={selectAndInspectSaveFile}
        onInspectSave={inspectTypedSavePath}
        onOpenGoodieMedia={openGoodieMedia}
        onRunSavePatchWorkflow={runSavePatchWorkflow}
        onRunOptionsPatchWorkflow={runOptionsPatchWorkflow}
        onOptionsSoundVolumeEnabledChange={setOptionsSoundVolumeEnabled}
        onOptionsSoundVolumeChange={setOptionsSoundVolume}
        onOptionsMusicVolumeEnabledChange={setOptionsMusicVolumeEnabled}
        onOptionsMusicVolumeChange={setOptionsMusicVolume}
        onOptionsScreenShapeEnabledChange={setOptionsScreenShapeEnabled}
        onOptionsScreenShapeChange={setOptionsScreenShape}
        onOptionsD3dDeviceEnabledChange={setOptionsD3dDeviceEnabled}
        onOptionsD3dDeviceIndexChange={setOptionsD3dDeviceIndex}
        onOptionsCopyFromPathChange={setOptionsCopyFromPath}
        onOptionsCopyEntriesChange={setOptionsCopyEntries}
      />
    ) : activeNav === "patches" ? (
      <PatchBenchSection
        specimen={specimen}
        specimenPath={specimenPath}
        verifyBusy={verifyBusy}
        verifyError={verifyError}
        patchWorkflowSourcePath={patchWorkflowSourcePath}
        patchIds={patchIds}
        copiedExecutablePath={copiedExecutablePath}
        copiedExecutableBackupPath={copiedExecutableBackupPath}
        patchWorkflowRun={patchWorkflowRun}
        patchWorkflowBusy={patchWorkflowBusy}
        patchWorkflowError={patchWorkflowError}
        onSpecimenPathChange={setSpecimenPath}
        onPatchWorkflowSourcePathChange={setPatchWorkflowSourcePath}
        onPatchIdsChange={setPatchIds}
        onSelectExecutable={selectAndVerifyExecutable}
        onVerifyExecutable={verifyTypedPath}
        onRunPatchWorkflow={runPatchWorkflow}
      />
    ) : activeNav === "media" ? (
      <MediaSection
        mediaCatalog={mediaCatalog}
        mediaQuery={mediaQuery}
        mediaKindFilter={mediaKindFilter}
        mediaBusy={mediaBusy}
        mediaError={mediaError}
        audioPlayback={audioPlayback}
        audioPlaybackBusy={audioPlaybackBusy}
        audioPlaybackError={audioPlaybackError}
        videoPlayback={videoPlayback}
        videoPlaybackBusy={videoPlaybackBusy}
        videoPlaybackError={videoPlaybackError}
        mediaPreview={mediaPreview}
        mediaPreviewBusy={mediaPreviewBusy}
        mediaPreviewError={mediaPreviewError}
        onMediaQueryChange={setMediaQuery}
        onMediaKindFilterChange={setMediaKindFilter}
        onRefreshMediaCatalog={refreshMediaCatalog}
        onOpenVideoGroup={openVideoGroup}
        onLoadAudioPlayback={loadAudioPlayback}
        onPrepareVideoPlayback={prepareVideoPlayback}
        onLoadMediaPreview={loadMediaPreview}
      />
    ) : activeNav === "lore" ? (
      <LoreSection
        contentIndex={contentIndex}
        contentDocument={contentDocument}
        visibleContentItems={visibleContentItems}
        contentAudienceCounts={contentAudienceCounts}
        contentQuery={contentQuery}
        contentAudienceFilter={contentAudienceFilter}
        contentBusy={contentBusy}
        contentError={contentError}
        onContentQueryChange={setContentQuery}
        onContentAudienceFilterChange={setContentAudienceFilter}
        onSelectContentDocument={selectContentDocument}
        onRefreshContentIndex={refreshContentIndex}
        onOpenExternal={(url) => getOnslaughtApi().openExternal(url)}
      />
    ) : activeNav === "re-lab" ? (
      <ReLabSection
        ghidraReadiness={ghidraReadiness}
        debugReadiness={debugReadiness}
        gameHarnessProfile={gameHarnessProfile}
        jobCatalog={jobCatalog}
        visibleJobDefinitions={visibleJobDefinitions}
        showParityDiagnostics={showParityDiagnostics}
        parityDiagnosticCount={parityDiagnosticCount}
        readinessBusy={readinessBusy}
        readinessError={readinessError}
        onRefreshReadiness={refreshReadiness}
        onShowParityDiagnosticsChange={setShowParityDiagnostics}
        onRunWorkbenchJob={runWorkbenchJob}
      />
    ) : activeNav === "harness" ? (
      <GameHarnessSection
        gameHarnessProfile={gameHarnessProfile}
        gameFolderPath={gameFolderPath}
        gameFolderBusy={gameFolderBusy}
        gameFolderError={gameFolderError}
        safeProfileBusy={safeProfileBusy}
        safeProfileError={safeProfileError}
        safeProfileRun={safeProfileRun}
        copiedExecutablePath={copiedExecutablePath}
        patchWorkflowRun={patchWorkflowRun}
        patchWorkflowBusy={patchWorkflowBusy}
        patchWorkflowError={patchWorkflowError}
        launchProfileJob={launchProfileJob}
        stopManagedProcessJob={stopManagedProcessJob}
        launchProfileBusy={jobBusy === "game.launchProfile"}
        stopManagedProcessBusy={jobBusy === "runtime.stopManagedProcess"}
        capturePlanJob={capturePlanJob}
        frameCaptureJob={frameCaptureJob}
        frameSequenceJob={frameSequenceJob}
        inputPlanJob={inputPlanJob}
        inputSendJob={inputSendJob}
        launchProfileRun={launchProfileRun}
        stopManagedProcessRun={stopManagedProcessRun}
        capturePlanRun={capturePlanRun}
        frameCaptureRun={frameCaptureRun}
        frameSequenceRun={frameSequenceRun}
        inputRun={inputRun}
        launchJobsArmed={launchJobsArmed}
        onGameFolderPathChange={setGameFolderPath}
        onBrowseGameFolder={selectAndInspectGameFolder}
        onUseGameFolder={inspectTypedGameFolder}
        onResetGameFolder={resetGameFolderProfile}
        onPrepareSafeProfile={prepareSafeGameProfile}
        onOpenPatchBenchForWindowedPatch={openPatchBenchForWindowedPatch}
        onRunWindowedPatchWorkflow={runWindowedPatchWorkflow}
        onRunWorkbenchJob={runWorkbenchJob}
        onLaunchJobsArmedChange={setLaunchJobsArmed}
      />
    ) : (
      <ReleaseSection
        releasePolicy={releasePolicy}
        releaseGates={snapshot.releaseGates}
        releaseBusy={releaseBusy}
        releaseError={releaseError}
        onRefreshReleasePolicy={refreshReleasePolicy}
      />
    );

  return (
    <WorkbenchShell
      snapshot={snapshot}
      activeNav={activeNav}
      activeSection={activeSection}
      commandQuery={commandQuery}
      commandResults={commandResults}
      verifyBusy={verifyBusy}
      inspectBusy={inspectBusy}
      onCommandQueryChange={setCommandQuery}
      onNavigate={setActiveNav}
      onVerifyExecutable={selectAndVerifyExecutable}
      onInspectSaveFile={selectAndInspectSaveFile}
      focusMode={activeNav === "lore" ? "reader" : "default"}
      aside={null}
    >
      <section className="space-y-5" data-testid="main-section" data-active-section={activeNav}>
        {renderedSection}
      </section>
    </WorkbenchShell>
  );
}
