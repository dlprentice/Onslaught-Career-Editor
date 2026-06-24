import fs from "node:fs/promises";
import path from "node:path";
import type {
  ReleasePolicyClassification,
  ReleasePolicyPathRule,
  ReleasePolicyProfile,
  ReleasePolicySummary
} from "@onslaught/contracts";
import { getContentIndex } from "./content-browser";

const pathRuleSeeds: Array<Omit<ReleasePolicyPathRule, "exists">> = [
  {
    label: "Active source, docs, and tests",
    relativePath: ".",
    classification: "allow",
    audience: "community",
    reason: "Normal source-tree release material once private paths are excluded."
  },
  {
    label: "Patch catalog",
    relativePath: "patches/catalog",
    classification: "allow",
    audience: "community",
    reason: "Curated byte metadata; does not bundle a game executable."
  },
  {
    label: "Roadmap docs",
    relativePath: "roadmap",
    classification: "review",
    audience: "maintainer",
    reason: "Useful for maintainers, but some planning notes may mention private workflow details."
  },
  {
    label: "Reference submodules",
    relativePath: "references",
    classification: "conditional",
    audience: "maintainer",
    reason: "Source-reference material needs explicit upstream/license scope review before public packaging."
  },
  {
    label: "Game install",
    relativePath: "game",
    classification: "deny",
    audience: "private",
    reason: "Private bring-your-own-game files; never bundle in a public app or source snapshot."
  },
  {
    label: "Media corpus",
    relativePath: "media",
    classification: "deny",
    audience: "private",
    reason: "Large and rights-sensitive media must stay local unless separately cleared."
  },
  {
    label: "Save attempts",
    relativePath: "save-attempts",
    classification: "deny",
    audience: "private",
    reason: "Real saves and scratch proof files are local test fixtures, not public release content."
  },
  {
    label: "Subagent outputs",
    relativePath: "subagents",
    classification: "deny",
    audience: "private",
    reason: "Generated investigation logs and extracted manifests are not public package inputs by default."
  },
  {
    label: "Agent goal state",
    relativePath: ".codex",
    classification: "deny",
    audience: "private",
    reason: "Agent goal contracts and progress ledgers are repo operating material, not community release content."
  },
  {
    label: "Repo state files",
    relativePath: "developer_agent_state.json",
    classification: "deny",
    audience: "private",
    reason: "Agent handoff state is workspace coordination data, not user-facing release content."
  },
  {
    label: "Documentation state file",
    relativePath: "documentation_agent_state.json",
    classification: "deny",
    audience: "private",
    reason: "Agent handoff state is workspace coordination data, not user-facing release content."
  },
  {
    label: "RE orchestration state file",
    relativePath: "re_orchestrator_state.json",
    classification: "deny",
    audience: "private",
    reason: "Reverse-engineering orchestration state is workspace coordination data, not user-facing release content."
  }
];

export async function getReleasePolicy(appPath: string, artifactRoot?: string): Promise<ReleasePolicySummary> {
  const repoRoot = await resolveRepoRoot(appPath);
  const [contentIndex, pathRules] = await Promise.all([
    getContentIndex(appPath),
    Promise.all(pathRuleSeeds.map((rule) => withExistence(repoRoot, rule)))
  ]);

  const content = contentIndex.items.map((item) => ({
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
  })) satisfies ReleasePolicySummary["content"];

  const counts = {
    contentTotal: content.length,
    communityDocs: content.filter((item) => item.communitySafe).length,
    maintainerDocs: content.filter((item) => !item.communitySafe).length,
    allow: countClassification(pathRules, "allow"),
    review: countClassification(pathRules, "review"),
    conditional: countClassification(pathRules, "conditional"),
    deny: countClassification(pathRules, "deny"),
    existingDeniedPaths: pathRules.filter((rule) => rule.classification === "deny" && rule.exists).length
  };

  const summary: ReleasePolicySummary = {
    generatedAt: new Date().toISOString(),
    repoRoot,
    counts,
    profiles: buildProfiles(counts.existingDeniedPaths),
    content,
    pathRules,
    artifact: {
      kind: "read-only",
      mutation: false,
      schemaVersion: "release-policy.v1",
      note: "Release policy inventory only. No files were copied, deleted, packaged, or uploaded."
    }
  };

  return artifactRoot ? writeReleasePolicyArtifact(summary, artifactRoot) : summary;
}

async function withExistence(
  repoRoot: string,
  rule: Omit<ReleasePolicyPathRule, "exists">
): Promise<ReleasePolicyPathRule> {
  try {
    await fs.stat(path.join(repoRoot, rule.relativePath));
    return { ...rule, exists: true };
  } catch {
    return { ...rule, exists: false };
  }
}

function countClassification(rules: ReleasePolicyPathRule[], classification: ReleasePolicyClassification) {
  return rules.filter((rule) => rule.classification === classification).length;
}

function buildProfiles(existingDeniedPaths: number): ReleasePolicyProfile[] {
  return [
    {
      id: "source-tree",
      title: "Clean source tree",
      status: existingDeniedPaths > 0 ? "blocked" : "usable-with-review",
      summary:
        existingDeniedPaths > 0
          ? "The private working tree still contains denylisted local artifacts."
          : "The source tree can be reviewed as a public-oriented checkout.",
      requiredActions: [
        "Keep hard-deny paths out of public branches and archives.",
        "Run the release profile and curated manifest checks after the allowlist is refreshed.",
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
  ];
}

async function writeReleasePolicyArtifact(
  summary: ReleasePolicySummary,
  artifactRoot: string
): Promise<ReleasePolicySummary> {
  const jobId = `release-policy-${summary.generatedAt.replace(/\D/g, "").slice(0, 14)}`;
  const artifactDir = path.join(path.resolve(artifactRoot), "artifacts", "release-policy", jobId);
  const artifactPath = path.join(artifactDir, "release-policy.json");
  const summaryWithArtifact: ReleasePolicySummary = {
    ...summary,
    artifact: {
      ...summary.artifact,
      artifactPath
    }
  };

  await fs.mkdir(artifactDir, { recursive: true });
  await fs.writeFile(artifactPath, `${JSON.stringify(summaryWithArtifact, null, 2)}\n`, "utf8");
  return summaryWithArtifact;
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
