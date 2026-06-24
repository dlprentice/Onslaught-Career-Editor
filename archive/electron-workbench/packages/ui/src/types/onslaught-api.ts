import type { OnslaughtApi as OnslaughtApiContract } from "@onslaught/contracts";

export type {
  OnslaughtApi,
  AddressConversionSummary,
  AudioPlaybackSummary,
  ContentDocumentSummary,
  ContentIndexItem,
  ContentIndexSummary,
  DebugReadinessSummary,
  GameHarnessProfileSummary,
  GhidraReadinessSummary,
  HexReadSummary,
  MediaCatalogKind,
  MediaCatalogKindFilter,
  MediaCatalogRow,
  MediaCatalogSummary,
  MediaPreviewSummary,
  PatchState,
  ReleasePolicySummary,
  PatchVerifyRow,
  SaveComparisonSummary,
  SaveInspectionSummary,
  SpecimenVerificationSummary,
  Tone,
  RuntimeSnapshot,
  VideoPlaybackOpenOptions,
  VideoPlaybackPrepareOptions,
  VideoPlaybackSummary,
  WorkbenchJobCatalogSummary,
  WorkbenchJobDefinition,
  WorkbenchJobInputValue,
  WorkbenchJobProgressEvent,
  WorkbenchJobRunRequest,
  WorkbenchJobRunSummary
} from "@onslaught/contracts";

declare global {
  interface Window {
    onslaughtApi?: OnslaughtApiContract;
  }
}
