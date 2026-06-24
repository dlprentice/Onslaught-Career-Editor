const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "../../..");
const cliPath = path.join(repoRoot, "packages", "cli", "dist", "index.js");
const artifactRoot = fs.mkdtempSync(path.join(os.tmpdir(), "onslaught-cli-smoke-"));

function runCliRaw(args, input, extraEnv = {}) {
  return spawnSync(process.execPath, [cliPath, ...args], {
    cwd: repoRoot,
    input,
    encoding: "utf8",
    env: {
      ...process.env,
      ...extraEnv
    }
  });
}

function runCli(args, input, extraEnv) {
  const result = runCliRaw(args, input, extraEnv);
  if (result.status !== 0) {
    throw new Error(`CLI failed (${args.join(" ")}):\n${result.stderr || result.stdout}`);
  }
  return result;
}

function parseJsonStdout(result, label) {
  assert.equal(result.status, 0, `${label} should exit successfully`);
  assert.ok(result.stdout.trim().length > 0, `${label} should write JSON to stdout`);
  return JSON.parse(result.stdout);
}

function assertNoStderr(result, label) {
  assert.equal(result.stderr, "", `${label} should not write to stderr`);
}

function parseProgress(stderr) {
  return stderr
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

const helpResult = runCli(["--help"]);
assert.match(helpResult.stdout, /Usage:/, "help should include usage");
assert.match(helpResult.stdout, /catalog/, "help should describe catalog");
assert.match(helpResult.stdout, /run/, "help should describe run");
assert.match(helpResult.stdout, /list/, "help should describe list");
assert.match(helpResult.stdout, /ONSLAUGHT_ARTIFACT_ROOT/, "help should document artifact-root default");
assert.match(helpResult.stdout, /stderr NDJSON/, "help should document progress stream");
assertNoStderr(helpResult, "help");

const catalogResult = runCli(["catalog", "--artifact-root", artifactRoot]);
assertNoStderr(catalogResult, "catalog");
const catalog = parseJsonStdout(catalogResult, "catalog");
assert.ok(catalog.generatedAt, "catalog should include a generation timestamp");
assert.ok(catalog.counts.available > 0, "catalog should expose available jobs");
assert.ok(catalog.definitions.some((job) => job.id === "release.inspectPolicy"), "release.inspectPolicy should be available");

const request = JSON.stringify({ definitionId: "release.inspectPolicy", inputs: {} });
const runResult = runCli(["run", "--artifact-root", artifactRoot, "--progress"], request);
const summary = parseJsonStdout(runResult, "run via stdin");
assert.equal(summary.definitionId, "release.inspectPolicy");
assert.equal(summary.status, "completed");
assert.equal(summary.result.payloadSchema, "release-policy.v1");
const progressLines = parseProgress(runResult.stderr);
assert.ok(progressLines.length > 0, "progress stream should emit NDJSON events");
assert.ok(progressLines.every((event) => typeof event.runId === "string" && typeof event.phase === "string"), "progress events should be shaped JSON");
assert.ok(progressLines.some((event) => event.phase === "completed"), "progress stream should include completion");

const inputPath = path.join(artifactRoot, "release-inspect-request.json");
fs.writeFileSync(inputPath, request);
const inputRunResult = runCli(["run", "--artifact-root", artifactRoot, "--input", inputPath]);
assertNoStderr(inputRunResult, "run via --input without progress");
const inputSummary = parseJsonStdout(inputRunResult, "run via --input");
assert.equal(inputSummary.definitionId, "release.inspectPolicy");
assert.equal(inputSummary.status, "completed");
assert.notEqual(inputSummary.runId, summary.runId, "rapid repeated runs should receive distinct run IDs");

const listResult = runCli(["list"], undefined, { ONSLAUGHT_ARTIFACT_ROOT: artifactRoot });
assertNoStderr(listResult, "list");
const runs = parseJsonStdout(listResult, "list");
assert.ok(runs.some((run) => run.runId === summary.runId), "list should include the stdin run created by the CLI");
assert.ok(runs.some((run) => run.runId === inputSummary.runId), "list should include the --input run created by the CLI");

const invalidResult = runCliRaw(["not-a-command"]);
assert.notEqual(invalidResult.status, 0, "invalid command should exit non-zero");
assert.equal(invalidResult.stdout, "", "invalid command should not write success JSON to stdout");
assert.match(invalidResult.stderr, /Unknown command: not-a-command/, "invalid command should explain the failure on stderr");

console.log(`CLI smoke passed. Artifact root: ${artifactRoot}`);
