import type { LucideIcon } from "lucide-react";
import {
  Activity,
  Binary,
  BookOpenText,
  Boxes,
  FileSearch,
  FlaskConical,
  Gamepad2,
  HardDrive,
  MonitorPlay,
  RadioTower,
  ShieldCheck,
  TerminalSquare,
  Wrench
} from "lucide-react";
import type { WorkbenchJobDefinition } from "@/types/onslaught-api";

export type WorkbenchSectionId =
  | "overview"
  | "saves"
  | "patches"
  | "media"
  | "lore"
  | "re-lab"
  | "harness"
  | "release";

export interface WorkbenchNavItem {
  id: WorkbenchSectionId;
  label: string;
  shortLabel: string;
  detail: string;
  purpose: string;
  nextAction: string;
  icon: LucideIcon;
}

export interface WorkbenchCommandResult {
  id: string;
  label: string;
  detail: string;
  navId: WorkbenchSectionId;
  kind: "section" | "job";
}

export interface HarnessPhase {
  title: string;
  body: string;
  icon: LucideIcon;
  state: string;
}

export const navItems: WorkbenchNavItem[] = [
  {
    id: "overview",
    label: "Home",
    shortLabel: "Home",
    detail: "Start here",
    purpose: "Choose a task and continue where you left off.",
    nextAction: "Pick the card that matches what you want to do.",
    icon: Activity
  },
  {
    id: "saves",
    label: "Save Lab",
    shortLabel: "Saves",
    detail: "Progress and options",
    purpose: "Open a save or options file, inspect what it contains, then save changes to a copy.",
    nextAction: "Open a save, review the summary, and choose a safe edit.",
    icon: FileSearch
  },
  {
    id: "patches",
    label: "Patch Bench",
    shortLabel: "Patches",
    detail: "Executable patches",
    purpose: "Apply safe display and graphics patches to a copied executable.",
    nextAction: "Choose or prepare a copied executable, then review patches before applying.",
    icon: Binary
  },
  {
    id: "media",
    label: "Media",
    shortLabel: "Media",
    detail: "Audio, video, textures",
    purpose: "Browse extracted media, preview textures, play audio, and prepare videos in app.",
    nextAction: "Load the media catalog, search by title or type, then preview or play an item.",
    icon: MonitorPlay
  },
  {
    id: "lore",
    label: "Lore",
    shortLabel: "Lore",
    detail: "Reader",
    purpose: "Read curated story, preservation, and reverse-engineering notes in one place.",
    nextAction: "Search the library or choose a document from the list.",
    icon: BookOpenText
  },
  {
    id: "re-lab",
    label: "RE Lab",
    shortLabel: "RE Lab",
    detail: "Maintainer tools",
    purpose: "Search assets, functions, strings, and structures, then ask for a bounded plan.",
    nextAction: "Search for an asset or choose an example investigation.",
    icon: FlaskConical
  },
  {
    id: "harness",
    label: "Game Harness",
    shortLabel: "Harness",
    detail: "Guided runtime loop",
    purpose: "Run a safe observe, decide, act, and review investigation against a copied profile.",
    nextAction: "Prepare a copied profile before launching or sending any input.",
    icon: Gamepad2
  },
  {
    id: "release",
    label: "Release",
    shortLabel: "Release",
    detail: "Package safety",
    purpose: "Review release readiness, public scope, and private exclusions.",
    nextAction: "Review automated gates and the next required proof step.",
    icon: ShieldCheck
  }
];

export const harnessPhases: HarnessPhase[] = [
  {
    title: "Specimen dashboard",
    body: "Select or detect a game directory, hash BEA.exe, read patch states, and write launch plans without starting the game.",
    icon: HardDrive,
    state: "active"
  },
  {
    title: "Patch workbench",
    body: "Verify, apply, and restore curated patches against copied executables with byte checks before and after.",
    icon: Wrench,
    state: "active"
  },
  {
    title: "Runtime probes",
    body: "Launch copied profiles, attach confirmed CDB probes, record managed PIDs, and read bounded log tails.",
    icon: TerminalSquare,
    state: "active foundation"
  },
  {
    title: "Ghidra headless",
    body: "Run read-only weak-function exports, address decompile exports, and rename-map dry-runs before any confirmed apply.",
    icon: Boxes,
    state: "active foundation"
  },
  {
    title: "Capture and input",
    body: "Discover the managed BEA window, capture stills or short frame sequences, and send confirmed scoped keyboard input; persistent frame streaming remains gated future work.",
    icon: RadioTower,
    state: "active foundation"
  }
];

export function navForJobLane(lane: WorkbenchJobDefinition["lane"]): WorkbenchSectionId {
  switch (lane) {
    case "save":
    case "appcore":
      return "saves";
    case "patch":
      return "patches";
    case "content":
      return "lore";
    case "assets":
      return "media";
    case "release":
      return "release";
    case "file":
    case "ghidra":
    case "debugger":
    case "runtime":
      return "re-lab";
    case "game":
      return "harness";
    default:
      return "overview";
  }
}

export function formatWorkbenchMode(mode: string) {
  switch (mode) {
    case "browser-mock":
      return "Preview";
    case "desktop-dev":
    case "electron-dev":
      return "Desktop";
    case "desktop-packaged":
    case "electron-packaged":
      return "Packaged";
    default:
      return "Workbench";
  }
}

export function formatSafetyLabel(safety: string) {
  switch (safety) {
    case "mutation-gated":
      return "requires explicit confirmation";
    case "launch-gated":
      return "launch requires confirmation";
    case "read-only":
      return "read only";
    default:
      return safety;
  }
}

export function formatEvidenceType(schema: string | undefined) {
  if (!schema) return "evidence";
  if (schema === "job-run.v1") return "job history record";
  return schema
    .replace(/\.v\d+$/, "")
    .replace(/-/g, " ")
    .replace(/\bmutation\b/gi, "confirmed change")
    .replace(/\bartifact\b/gi, "evidence file");
}
