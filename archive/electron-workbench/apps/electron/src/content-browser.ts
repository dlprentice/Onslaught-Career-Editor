import fs from "node:fs/promises";
import path from "node:path";
import type { ContentDocumentSummary, ContentIndexItem, ContentIndexSummary } from "@onslaught/contracts";

const maxDocumentChars = 24000;

const contentItems: ContentIndexItem[] = [
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

export async function getContentIndex(appPath: string): Promise<ContentIndexSummary> {
  const repoRoot = await resolveRepoRoot(appPath);
  const items = await filterExistingItems(repoRoot);
  return {
    generatedAt: new Date().toISOString(),
    repoRoot,
    items,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "content-index.v1",
      note: "Curated allowlist only. The renderer cannot request arbitrary repo files."
    }
  };
}

export async function readContentDocument(appPath: string, id: string): Promise<ContentDocumentSummary> {
  const repoRoot = await resolveRepoRoot(appPath);
  const item = contentItems.find((candidate) => candidate.id === id);
  if (!item) {
    throw new Error(`Unknown content document: ${id}`);
  }

  const documentPath = path.join(repoRoot, item.relativePath);
  const stat = await fs.stat(documentPath);
  if (!stat.isFile()) {
    throw new Error(`Content document is not a file: ${item.relativePath}`);
  }

  const raw = await fs.readFile(documentPath, "utf8");
  return {
    id: item.id,
    title: item.title,
    group: item.group,
    relativePath: item.relativePath,
    communitySafe: item.communitySafe,
    audience: item.communitySafe ? "community" : "maintainer",
    readAt: new Date().toISOString(),
    byteLength: Buffer.byteLength(raw, "utf8"),
    truncated: raw.length > maxDocumentChars,
    markdown: raw.length > maxDocumentChars ? raw.slice(0, maxDocumentChars) : raw,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "content-document.v1",
      note: "Read-only curated markdown preview."
    }
  };
}

async function filterExistingItems(repoRoot: string) {
  const checked = await Promise.all(
    contentItems.map(async (item) => {
      try {
        const stat = await fs.stat(path.join(repoRoot, item.relativePath));
        return stat.isFile() ? item : null;
      } catch {
        return null;
      }
    })
  );
  return checked.filter((item): item is ContentIndexItem => item !== null);
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
      await fs.access(path.join(candidate, "lore-book"));
      return path.resolve(candidate);
    } catch {
      // Try the next known dev/packaged root.
    }
  }
  return path.resolve(process.cwd());
}
