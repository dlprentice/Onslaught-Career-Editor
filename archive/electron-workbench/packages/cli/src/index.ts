#!/usr/bin/env node

import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import type { WorkbenchJobProgressEvent, WorkbenchJobRunRequest } from "@onslaught/contracts";
import { listWorkbenchJobRuns, startWorkbenchJob } from "@onslaught/electron/job-runner";
import { getJobCatalog } from "@onslaught/electron/re-workbench";

interface CliOptions {
  command: string;
  repoRoot: string;
  artifactRoot: string;
  inputPath: string | null;
  pretty: boolean;
  progress: boolean;
  limit: number;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  await fs.mkdir(options.artifactRoot, { recursive: true });

  switch (options.command) {
    case "catalog": {
      const catalog = await getJobCatalog(options.repoRoot, options.artifactRoot);
      writeJson(catalog, options.pretty);
      return;
    }
    case "run": {
      const request = await readJobRequest(options.inputPath);
      const catalog = await getJobCatalog(options.repoRoot, options.artifactRoot);
      const progressSink = options.progress
        ? (event: WorkbenchJobProgressEvent) => {
            process.stderr.write(`${JSON.stringify(event)}\n`);
          }
        : undefined;
      const summary = await startWorkbenchJob(
        options.repoRoot,
        options.artifactRoot,
        catalog.definitions,
        request,
        progressSink
      );
      writeJson(summary, options.pretty);
      return;
    }
    case "list": {
      const runs = await listWorkbenchJobRuns(options.artifactRoot, options.limit);
      writeJson(runs, options.pretty);
      return;
    }
    default:
      throw new Error(`Unknown command: ${options.command}`);
  }
}

function parseArgs(args: string[]): CliOptions {
  const command = args[0] ?? "help";
  if (command === "help" || command === "--help" || command === "-h") {
    printHelp();
    process.exit(0);
  }

  const options: CliOptions = {
    command,
    repoRoot: process.cwd(),
    artifactRoot: process.env.ONSLAUGHT_ARTIFACT_ROOT || path.join(os.homedir(), ".onslaught-workbench"),
    inputPath: null,
    pretty: false,
    progress: false,
    limit: 12
  };

  for (let index = 1; index < args.length; index++) {
    const arg = args[index];
    switch (arg) {
      case "--repo-root":
        options.repoRoot = requiredValue(args, ++index, arg);
        break;
      case "--artifact-root":
        options.artifactRoot = requiredValue(args, ++index, arg);
        break;
      case "--input":
        options.inputPath = requiredValue(args, ++index, arg);
        break;
      case "--pretty":
        options.pretty = true;
        break;
      case "--progress":
        options.progress = true;
        break;
      case "--limit":
        options.limit = parseLimit(requiredValue(args, ++index, arg));
        break;
      default:
        throw new Error(`Unknown argument: ${arg}`);
    }
  }

  options.repoRoot = path.resolve(options.repoRoot);
  options.artifactRoot = path.resolve(options.artifactRoot);
  return options;
}

async function readJobRequest(inputPath: string | null): Promise<WorkbenchJobRunRequest> {
  const raw = inputPath ? await fs.readFile(path.resolve(inputPath), "utf8") : await readStdin();
  const parsed = JSON.parse(raw) as Partial<WorkbenchJobRunRequest>;
  if (!parsed || typeof parsed.definitionId !== "string" || !parsed.inputs || typeof parsed.inputs !== "object") {
    throw new Error("Run input must be a WorkbenchJobRunRequest JSON object with definitionId and inputs.");
  }
  return {
    definitionId: parsed.definitionId,
    inputs: parsed.inputs as WorkbenchJobRunRequest["inputs"],
    timeoutMs: parsed.timeoutMs
  };
}

function readStdin() {
  return new Promise<string>((resolve, reject) => {
    let raw = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      raw += chunk;
    });
    process.stdin.on("error", reject);
    process.stdin.on("end", () => resolve(raw));
  });
}

function requiredValue(args: string[], index: number, flag: string) {
  const value = args[index];
  if (!value || value.startsWith("--")) {
    throw new Error(`${flag} requires a value.`);
  }
  return value;
}

function parseLimit(value: string) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isSafeInteger(parsed) || parsed < 1 || parsed > 100) {
    throw new Error("--limit must be an integer from 1 to 100.");
  }
  return parsed;
}

function writeJson(value: unknown, pretty: boolean) {
  process.stdout.write(`${JSON.stringify(value, null, pretty ? 2 : 0)}\n`);
}

function printHelp() {
  process.stdout.write(`Onslaught Workbench CLI

Usage:
  onslaught catalog [--repo-root <path>] [--artifact-root <path>] [--pretty]
  onslaught run [--repo-root <path>] [--artifact-root <path>] [--input request.json] [--progress] [--pretty]
  onslaught list [--artifact-root <path>] [--limit 12] [--pretty]

Commands:
  catalog  Print the available safe workbench job catalog as JSON.
  run      Execute one WorkbenchJobRunRequest from --input or stdin.
  list     Print persisted job-run history from the selected artifact root.

Defaults:
  --repo-root defaults to the current working directory.
  --artifact-root defaults to ONSLAUGHT_ARTIFACT_ROOT, then ~/.onslaught-workbench.

Output:
  Successful commands write parseable JSON to stdout.
  --progress writes job progress as stderr NDJSON, one event per line.
  Errors write to stderr and exit non-zero without writing success JSON.

Examples:
  onslaught catalog --pretty
  echo '{"definitionId":"release.inspectPolicy","inputs":{}}' | onslaught run --progress
  onslaught run --input request.json --pretty
  onslaught list --limit 5
`);
}

main().catch((error) => {
  process.stderr.write(`${error instanceof Error ? error.stack || error.message : String(error)}\n`);
  process.exitCode = 1;
});
