const assert = require("node:assert/strict");
const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const fsp = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");

const {
  applyCatalogPatchSet,
  prepareExecutableCopyPath,
  restoreCatalogPatchBackup,
  verifyExecutablePath
} = require("../dist/patch-verifier.js");
const { compareSaveFilePaths, inspectSaveFilePath } = require("../dist/save-inspector.js");
const {
  applySavePatchPath,
  planSavePatchPath,
  previewSavePatchPath,
  restoreSaveBackupPath
} = require("../dist/save-patcher.js");
const {
  applyOptionsPatchPath,
  planOptionsPatchPath,
  previewOptionsPatchPath
} = require("../dist/options-patcher.js");
const { getJobCatalog } = require("../dist/re-workbench.js");
const { listWorkbenchJobRuns, startWorkbenchJob } = require("../dist/job-runner.js");
const { getReleasePolicy } = require("../dist/release-policy.js");
const { getAudioPlayback, getMediaCatalog, getMediaPreview, openVideoPlayback, prepareVideoPlayback } = require("../dist/media-catalog.js");

const repoRoot = path.resolve(__dirname, "../../..");
const goldSavePath = path.join(repoRoot, "save-attempts", "haha-cannon-goes-brrrrr.bes");
const defaultOptionsPath = path.join(repoRoot, "game", "defaultoptions.bea");
const cleanExePath = path.join(repoRoot, "game", "BEA.exe");
const patchCatalogPath = path.join(repoRoot, "patches", "catalog", "patches.v2.json");
const knownRetailSteamSha256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
const cliProject = path.join(repoRoot, "OnslaughtCareerEditor.Cli", "OnslaughtCareerEditor.Cli.csproj");
const dotnet = process.env.DOTNET_EXE || "dotnet";
const runAppCoreJobParity = process.env.ONSLAUGHT_RUN_APPCORE_PARITY === "1";
const saveParityFixtures = [
  {
    filePath: goldSavePath,
    isOptionsFile: false,
    exact: {
      "settings.flightInvertY": [true, false],
      "settings.walkerInvertY": [false, false],
      "settings.vibration": [true, true],
      "settings.controllerConfig": [1, 1]
    }
  },
  {
    filePath: defaultOptionsPath,
    isOptionsFile: true,
    exact: {
      "settings.flightInvertY": [true, false],
      "settings.walkerInvertY": [false, false],
      "settings.vibration": [true, true],
      "settings.controllerConfig": [1, 1]
    }
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "proof_defaultoptions.bea"),
    isOptionsFile: true,
    exact: {
      "settings.flightInvertY": [false, true],
      "settings.walkerInvertY": [true, false],
      "settings.vibration": [true, false],
      "settings.controllerConfig": [123, 456]
    }
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "proof_partial_kills_only.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "proof_partial_ranks.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "proof_kills_only.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "proof_ranks.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "proof_partial_goodies_only.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "proof_partial_goodies_and_inf161.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "proof_partial_goodies_plus_inf161.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "save-attempts", "me-actually-playing-the-game-to-get-ranks.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "game", "savegames", "haha-cannon-goes-brrrrr.bes"),
    isOptionsFile: false
  },
  {
    filePath: path.join(repoRoot, "game", "savegames", "me actually playing the game to get ranks.bes"),
    isOptionsFile: false
  }
];

function runCliAnalyze(filePath) {
  return execFileSync(dotnet, ["run", "--project", cliProject, "--", filePath, "--analyze"], {
    cwd: repoRoot,
    encoding: "utf8",
    maxBuffer: 1024 * 1024 * 8
  });
}

function numberFrom(text, pattern, label) {
  const match = text.match(pattern);
  assert.ok(match, `Could not find ${label} in C# CLI output.`);
  return Number(match[1].replace(/,/g, ""));
}

function floatFrom(text, pattern, label) {
  const match = text.match(pattern);
  assert.ok(match, `Could not find ${label} in C# CLI output.`);
  return Number(match[1]);
}

function parseKill(text, label) {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = text.match(new RegExp(`${escaped}\\s+:\\s+(\\d+)(?:\\s+meta=0x([0-9A-F]+))?`));
  assert.ok(match, `Could not find ${label} kill row in C# CLI output.`);
  return {
    kills: Number(match[1]),
    meta: match[2] ? Number.parseInt(match[2], 16) : 0
  };
}

function parseRankDistribution(text) {
  const match = text.match(/Rank distribution:\s+(.+)/);
  assert.ok(match, "Could not find rank distribution in C# CLI output.");
  return match[1]
    .trim()
    .split(/\s+/)
    .map((part) => {
      const [rank, rawCount] = part.split(":");
      return [rank, Number(rawCount)];
    });
}

function parseBooleanPair(text, pattern, label) {
  const match = text.match(pattern);
  assert.ok(match, `Could not find ${label} pair in C# CLI output.`);
  return [match[1] === "ON", match[2] === "ON"];
}

function parseControllerConfig(text) {
  const match = text.match(/CtrlConfig:\s+P1=(\d+)\s+P2=(\d+)/);
  assert.ok(match, "Could not find controller config pair in C# CLI output.");
  return [Number(match[1]), Number(match[2])];
}

async function assertInspectionMatchesCli(filePath, artifactRoot, expected) {
  const cliOutput = runCliAnalyze(filePath);
  const inspection = await inspectSaveFilePath(filePath, artifactRoot);
  assert.equal(inspection.isValid, true);
  assert.equal(inspection.versionValid, true);
  assert.equal(inspection.versionWordHex, "0x4BD1");
  assert.equal(inspection.fileSize, numberFrom(cliOutput, /File size:\s+([\d,]+) bytes/, "file size"));
  assert.equal(inspection.fileSize, 10004);
  assert.equal(inspection.isOptionsFile, expected.isOptionsFile);
  assert.equal(inspection.artifact.schemaVersion, "save-inspection.v1");
  assert.ok(inspection.artifact.artifactPath && fs.existsSync(inspection.artifact.artifactPath));

  assert.equal(inspection.counts.completedNodes, numberFrom(cliOutput, /Completed:\s+(\d+) nodes/, "completed nodes"));
  assert.equal(inspection.counts.partialNodes, numberFrom(cliOutput, /Incomplete:\s*(\d+) nodes/, "incomplete nodes"));
  assert.equal(inspection.counts.emptyNodes, numberFrom(cliOutput, /Unused:\s+(\d+) nodes/, "unused nodes"));
  assert.equal(inspection.counts.totalLinks, numberFrom(cliOutput, /Used:\s+(\d+)\/200/, "used links"));
  assert.equal(inspection.counts.completedLinks, numberFrom(cliOutput, /Completed:\s+(\d+)\/\d+ \(state != 0\)/, "completed links"));
  assert.equal(inspection.counts.activeTechSlots, numberFrom(cliOutput, /Active:\s+(\d+)\/32/, "active tech slots"));

  assert.equal(inspection.goodies.displayableUnlocked, numberFrom(cliOutput, /Unlocked:\s+(\d+)\/233/, "unlocked goodies"));
  assert.equal(inspection.goodies.new, numberFrom(cliOutput, /- NEW \(gold\):\s+(\d+)/, "new goodies"));
  assert.equal(inspection.goodies.old, numberFrom(cliOutput, /- OLD \(blue\):\s+(\d+)/, "old goodies"));
  assert.equal(inspection.goodies.locked, numberFrom(cliOutput, /Locked:\s+(\d+)/, "locked goodies"));
  assert.equal(inspection.goodies.reserved, numberFrom(cliOutput, /Reserved:\s+(\d+)/, "reserved goodies"));
  assert.equal(inspection.goodieRows.length, 233, "displayable goodie row count");
  assert.equal(inspection.goodieRows[0].fileOffsetHex, "0x1F46", "first goodie true-view file offset");
  assert.equal(inspection.goodieRows[232].fileOffsetHex, "0x22E6", "last displayable goodie true-view file offset");
  assert.equal(
    inspection.goodieRows.filter((row) => row.stateGroup === "new" || row.stateGroup === "old").length,
    inspection.goodies.displayableUnlocked,
    "unlocked goodie row count"
  );

  assert.deepEqual(
    inspection.rankDistribution.map((row) => [row.rank, row.count]),
    parseRankDistribution(cliOutput),
    "rank distribution"
  );

  assert.equal(inspection.settings.soundVolume, floatFrom(cliOutput, /SoundVolume:\s+([0-9.]+)/, "sound volume"));
  assert.equal(inspection.settings.musicVolume, floatFrom(cliOutput, /MusicVolume:\s+([0-9.]+)/, "music volume"));
  assert.deepEqual(
    inspection.settings.walkerInvertY,
    parseBooleanPair(cliOutput, /InvertY \(Walker\):\s+P1=(ON|OFF)[^\n]*P2=(ON|OFF)/, "walker invert-Y"),
    "walker invert-Y"
  );
  assert.deepEqual(
    inspection.settings.flightInvertY,
    parseBooleanPair(cliOutput, /InvertY \(Flight\):\s+P1=(ON|OFF)[^\n]*P2=(ON|OFF)/, "flight invert-Y"),
    "flight invert-Y"
  );
  assert.deepEqual(
    inspection.settings.vibration,
    parseBooleanPair(cliOutput, /Vibration:\s+P1=(ON|OFF)[^\n]*P2=(ON|OFF)/, "vibration"),
    "vibration"
  );
  assert.deepEqual(inspection.settings.controllerConfig, parseControllerConfig(cliOutput), "controller config");

  assert.equal(inspection.options.entryCount, numberFrom(cliOutput, /Options entries:\s+(\d+)/, "options entries"));
  assert.equal(inspection.options.bindings.length, 16);
  assert.equal(inspection.options.mouseSensitivity, floatFrom(cliOutput, /MouseSensitivity:\s+([0-9.]+)/, "mouse sensitivity"));
  assert.equal(inspection.options.controlSchemeIndex, numberFrom(cliOutput, /ControlSchemeIndex:\s+(\d+)/, "control scheme index"));

  for (const row of inspection.kills) {
    const expected = parseKill(cliOutput, row.categoryName);
    assert.equal(row.kills, expected.kills, `${row.categoryName} kill count`);
    assert.equal(row.meta, expected.meta, `${row.categoryName} meta byte`);
  }

  for (const [pathToCheck, expectedValue] of Object.entries(expected.exact ?? {})) {
    assert.deepEqual(valueAtPath(inspection, pathToCheck), expectedValue, pathToCheck);
  }

  return inspection;
}

async function assertSaveParity(artifactRoot) {
  const inspected = [];
  for (const fixture of saveParityFixtures) {
    assert.ok(fs.existsSync(fixture.filePath), `Missing parity fixture: ${path.relative(repoRoot, fixture.filePath)}`);
    inspected.push(await assertInspectionMatchesCli(fixture.filePath, artifactRoot, fixture));
  }

  const identical = await compareSaveFilePaths(goldSavePath, goldSavePath, artifactRoot);
  assert.equal(identical.identical, true);
  assert.equal(identical.differingBytes, 0);
  assert.equal(identical.artifact.schemaVersion, "save-comparison.v1");
  assert.ok(identical.artifact.artifactPath && fs.existsSync(identical.artifact.artifactPath));

  const mutatedPath = path.join(artifactRoot, "mutated-aircraft-kills.bes");
  await fsp.copyFile(goldSavePath, mutatedPath);
  const handle = await fsp.open(mutatedPath, "r+");
  try {
    const byte = Buffer.alloc(1);
    await handle.read(byte, 0, 1, 0x23f6);
    byte[0] ^= 0x01;
    await handle.write(byte, 0, 1, 0x23f6);
  } finally {
    await handle.close();
  }

  const changed = await compareSaveFilePaths(goldSavePath, mutatedPath, artifactRoot);
  assert.equal(changed.identical, false);
  assert.equal(changed.differingBytes, 1);
  assert.equal(changed.diffRanges[0]?.startOffsetHex, "0x23F6");
  assert.equal(changed.diffRanges[0]?.endOffsetHex, "0x23F6");
  assert.ok(changed.topRegions.some((region) => region.region === "Kills[Aircraft]" && region.differingBytes === 1));

  const wrongSizedPath = path.join(artifactRoot, "wrong-size.bes");
  await fsp.writeFile(wrongSizedPath, Buffer.from([0xd1, 0x4b, 0x00, 0x00]));
  const wrongSize = await inspectSaveFilePath(wrongSizedPath, artifactRoot);
  assert.equal(wrongSize.isValid, false);
  assert.equal(wrongSize.versionValid, true);
  assert.match(wrongSize.errorMessage ?? "", /Invalid file size/);
  assert.ok(wrongSize.artifact.artifactPath && fs.existsSync(wrongSize.artifact.artifactPath));

  const badVersionPath = path.join(artifactRoot, "bad-version.bes");
  await fsp.copyFile(goldSavePath, badVersionPath);
  await writeBytes(badVersionPath, 0, Buffer.from([0x00, 0x00]));
  const badVersion = await inspectSaveFilePath(badVersionPath, artifactRoot);
  assert.equal(badVersion.isValid, false);
  assert.equal(badVersion.versionValid, false);
  assert.match(badVersion.errorMessage ?? "", /Invalid version word/);
  assert.ok(badVersion.artifact.artifactPath && fs.existsSync(badVersion.artifact.artifactPath));

  const unsupportedPath = path.join(artifactRoot, "unsupported-save.bin");
  await fsp.copyFile(goldSavePath, unsupportedPath);
  await assert.rejects(
    () => inspectSaveFilePath(unsupportedPath, artifactRoot),
    /Select a \.bes career save, \.bea options file, or defaultoptions\.bea backup/
  );

  return inspected;
}

async function assertNativeSavePatchParity(artifactRoot) {
  const plan = await planSavePatchPath(
    {
      path: goldSavePath,
      rank: "S",
      kills: 100,
      patchNodes: true,
      patchLinks: true,
      patchGoodies: true,
      patchKills: true,
      levelRanks: [
        { nodeIndex: 1, rank: "S" },
        { nodeIndex: 2, rank: "A" }
      ],
      perCategoryKills: [
        { categoryIndex: 0, categoryName: "Aircraft", kills: 100 },
        { categoryIndex: 4, categoryName: "Mechs", kills: 20 }
      ]
    },
    artifactRoot,
    "native-save-plan"
  );
  assert.equal(plan.schemaVersion, "save-patch-plan.v1");
  assert.equal(plan.mutation, false);
  assert.deepEqual(plan.plan.sections, ["nodes", "links", "goodies", "kills"]);
  assert.equal(plan.plan.requiresCopiedApply, true);
  assert.equal(plan.plan.sourceUnchanged, true);
  assert.equal(plan.plan.levelRankCount, 2);
  assert.equal(plan.plan.perCategoryKillCount, 2);
  assert.ok(plan.artifact.artifactPath && fs.existsSync(plan.artifact.artifactPath));

  await assertTypeScriptPatchMatchesCli(
    artifactRoot,
    "default-save-patch",
    goldSavePath,
    { rank: "S", kills: 100 },
    ["--rank", "S", "--kills", "100"]
  );

  const seededMetaPath = path.join(artifactRoot, "seeded-kill-meta.bes");
  await fsp.copyFile(goldSavePath, seededMetaPath);
  const seededMeta = [0xa1, 0xb2, 0xc3, 0xd4, 0xe5];
  for (let index = 0; index < seededMeta.length; index++) {
    const raw = Buffer.alloc(4);
    raw.writeUInt32LE(((seededMeta[index] << 24) | 7) >>> 0);
    await writeBytes(seededMetaPath, 0x23f6 + index * 4, raw);
  }
  await assertTypeScriptPatchMatchesCli(
    artifactRoot,
    "kills-only-per-category",
    seededMetaPath,
    {
      kills: 7,
      killsOnly: true,
      perCategoryKills: [
        { categoryIndex: 0, categoryName: "Aircraft", kills: 123 },
        { categoryIndex: 4, categoryName: "Mechs", kills: 456 }
      ]
    },
    ["--kills", "7", "--kills-only", "--aircraft-kills", "123", "--mech-kills", "456"],
    async (candidatePath) => {
      const candidate = await fsp.readFile(candidatePath);
      for (let index = 0; index < seededMeta.length; index++) {
        const raw = candidate.readUInt32LE(0x23f6 + index * 4);
        assert.equal((raw >>> 24) & 0xff, seededMeta[index], `kill meta ${index}`);
      }
    }
  );

  await assertTypeScriptPatchMatchesCli(
    artifactRoot,
    "level-rank-one-based",
    goldSavePath,
    {
      rank: "E",
      levelRanks: [{ nodeIndex: 1, rank: "S" }],
      patchLinks: false,
      patchGoodies: false,
      patchKills: false
    },
    ["--rank", "E", "--level-rank", "1:S", "--no-links", "--no-goodies", "--no-kills"],
    async (candidatePath) => {
      const candidate = await fsp.readFile(candidatePath);
      assert.equal(candidate.readUInt32LE(0x0042), 0x3f800000, "level-rank 1:S must target node 0");
    }
  );

  await assertTypeScriptPatchMatchesCli(
    artifactRoot,
    "new-goodies-boundary",
    goldSavePath,
    {
      useNewGoodies: true,
      patchNodes: false,
      patchLinks: false,
      patchKills: false
    },
    ["--new", "--no-nodes", "--no-links", "--no-kills"],
    async (candidatePath, sourcePath) => {
      const source = await fsp.readFile(sourcePath);
      const candidate = await fsp.readFile(candidatePath);
      assert.equal(candidate.readUInt32LE(0x1f46 + 232 * 4), 2, "slot 232 should be patched as NEW");
      for (let index = 233; index < 300; index++) {
        const offset = 0x1f46 + index * 4;
        assert.equal(candidate.readUInt32LE(offset), source.readUInt32LE(offset), `reserved goodie ${index}`);
      }
    }
  );

  const originalGoldBytes = await fsp.readFile(goldSavePath);
  await assert.rejects(
    () => applySavePatchPath({ path: goldSavePath, rank: "S", kills: 100 }, artifactRoot, "native-apply-repo-reject"),
    /artifact\/profile root/
  );

  const copiedSaveDir = path.join(artifactRoot, "copied-save-profile");
  const copiedApplyPath = path.join(copiedSaveDir, "haha-cannon-goes-brrrrr.bes");
  await fsp.mkdir(copiedSaveDir, { recursive: true });
  await fsp.copyFile(goldSavePath, copiedApplyPath);
  const copiedOriginal = await fsp.readFile(copiedApplyPath);
  const applyPayload = await applySavePatchPath(
    {
      path: copiedApplyPath,
      rank: "S",
      kills: 100,
      patchNodes: true,
      patchLinks: true,
      patchGoodies: true,
      patchKills: true
    },
    artifactRoot,
    "native-apply-copied-save"
  );
  assert.equal(applyPayload.schemaVersion, "save-patch-apply.v1");
  assert.equal(applyPayload.mutation, true);
  assert.equal(applyPayload.artifact.mutation, true);
  assert.equal(applyPayload.target.changed, true);
  assert.equal(applyPayload.target.readbackVerified, true);
  assert.ok(applyPayload.artifact.artifactPath && fs.existsSync(applyPayload.artifact.artifactPath));
  assert.ok(fs.existsSync(applyPayload.backup.backupPath), "apply backup must exist");
  assert.ok((await fsp.readFile(applyPayload.backup.backupPath)).equals(copiedOriginal), "apply backup must match preimage");
  assert.ok((await fsp.readFile(goldSavePath)).equals(originalGoldBytes), "repo gold save must remain unchanged");

  const csharpApplyOutput = path.join(artifactRoot, "native-apply-copied-save-appcore.bes");
  execFileSync(dotnet, ["run", "--project", cliProject, "--", goldSavePath, csharpApplyOutput, "--rank", "S", "--kills", "100"], {
    cwd: repoRoot,
    encoding: "utf8",
    maxBuffer: 1024 * 1024 * 8
  });
  assert.ok((await fsp.readFile(copiedApplyPath)).equals(await fsp.readFile(csharpApplyOutput)), "apply target must match C# AppCore output");

  const restorePayload = await restoreSaveBackupPath(
    copiedApplyPath,
    applyPayload.backup.backupPath,
    artifactRoot,
    "native-restore-copied-save"
  );
  assert.equal(restorePayload.schemaVersion, "save-patch-restore.v1");
  assert.equal(restorePayload.mutation, true);
  assert.equal(restorePayload.artifact.mutation, true);
  assert.equal(restorePayload.target.readbackVerified, true);
  assert.ok(restorePayload.artifact.artifactPath && fs.existsSync(restorePayload.artifact.artifactPath));
  assert.ok(restorePayload.preRestoreBackup?.backupPath && fs.existsSync(restorePayload.preRestoreBackup.backupPath));
  assert.ok((await fsp.readFile(copiedApplyPath)).equals(copiedOriginal), "restore target must match original copied save");

  await assert.rejects(
    () => previewSavePatchPath({ path: defaultOptionsPath, rank: "S", kills: 100 }, artifactRoot, "native-bea-guard"),
    /Career section patching is blocked/
  );

  const optionsPreview = await previewSavePatchPath(
    {
      path: defaultOptionsPath,
      patchNodes: false,
      patchLinks: false,
      patchGoodies: false,
      patchKills: false
    },
    artifactRoot,
    "native-options-noop"
  );
  assert.equal(optionsPreview.schemaVersion, "save-patch-preview.v1");
  assert.equal(optionsPreview.preview.wouldChange, false);
  assert.equal(optionsPreview.preview.differingBytes, 0);
  assert.ok(optionsPreview.artifact.candidateArtifactPath && fs.existsSync(optionsPreview.artifact.candidateArtifactPath));
}

async function assertNativeOptionsPatchParity(artifactRoot) {
  const optionsInput = {
    path: defaultOptionsPath,
    soundVolume: 0.5,
    musicVolume: 0.25,
    invertWalkerP1: true,
    invertWalkerP2: false,
    invertFlightP1: false,
    invertFlightP2: true,
    vibrationP1: true,
    vibrationP2: false,
    controllerConfigP1: 123,
    controllerConfigP2: 456,
    keybindOverrides: [
      { action: "move-forward", slot0: "W", slot1: "Up" },
      { action: "fire-weapon", slot0: "MouseLeft", slot1: "RControl" }
    ]
  };

  const plan = await planOptionsPatchPath(optionsInput, artifactRoot, "native-options-plan");
  assert.equal(plan.schemaVersion, "options-patch-plan.v1");
  assert.equal(plan.mutation, false);
  assert.deepEqual(plan.plan.sections, ["career-settings", "keybinds"]);
  assert.equal(plan.plan.settingsOverrideCount, 10);
  assert.equal(plan.plan.keybindOverrideCount, 2);
  assert.equal(plan.plan.requiresCopiedApply, true);
  assert.equal(plan.plan.sourceUnchanged, true);
  assert.ok(plan.artifact.artifactPath && fs.existsSync(plan.artifact.artifactPath));

  const preview = await previewOptionsPatchPath(optionsInput, artifactRoot, "native-options-preview");
  assert.equal(preview.schemaVersion, "options-patch-preview.v1");
  assert.equal(preview.mutation, false);
  assert.equal(preview.artifact.mutation, false);
  assert.equal(preview.preview.wouldChange, true);
  assert.ok(preview.preview.candidateArtifactPath, "options candidate artifact path missing");
  assert.ok(fs.existsSync(preview.preview.candidateArtifactPath), "options candidate artifact missing");
  assert.ok(preview.artifact.artifactPath && fs.existsSync(preview.artifact.artifactPath), "options preview artifact missing");

  const csharpOptionsOutput = path.join(artifactRoot, "native-options-appcore.bea");
  execFileSync(
    dotnet,
    [
      "run",
      "--project",
      cliProject,
      "--",
      defaultOptionsPath,
      csharpOptionsOutput,
      "--no-nodes",
      "--no-links",
      "--no-goodies",
      "--no-kills",
      "--sound-volume",
      "0.5",
      "--music-volume",
      "0.25",
      "--invert-walker-p1",
      "on",
      "--invert-walker-p2",
      "off",
      "--invert-flight-p1",
      "off",
      "--invert-flight-p2",
      "on",
      "--vibration-p1",
      "on",
      "--vibration-p2",
      "off",
      "--controller-config-p1",
      "123",
      "--controller-config-p2",
      "456",
      "--bind-move-forward",
      "W",
      "Up",
      "--bind-fire-weapon",
      "MouseLeft",
      "RControl"
    ],
    {
      cwd: repoRoot,
      encoding: "utf8",
      maxBuffer: 1024 * 1024 * 8
    }
  );
  assert.ok(
    (await fsp.readFile(preview.preview.candidateArtifactPath)).equals(await fsp.readFile(csharpOptionsOutput)),
    "native options preview must match C# AppCore output"
  );

  const candidateInspection = await inspectSaveFilePath(preview.preview.candidateArtifactPath, artifactRoot);
  assert.equal(candidateInspection.isOptionsFile, true);
  assert.equal(candidateInspection.settings.soundVolume, 0.5);
  assert.equal(candidateInspection.settings.musicVolume, 0.25);
  assert.deepEqual(candidateInspection.settings.walkerInvertY, [true, false]);
  assert.deepEqual(candidateInspection.settings.flightInvertY, [false, true]);
  assert.deepEqual(candidateInspection.settings.vibration, [true, false]);
  assert.deepEqual(candidateInspection.settings.controllerConfig, [123, 456]);
  assert.equal(candidateInspection.options.controlSchemeIndex, 0);
  assert.equal(candidateInspection.options.bindings.find((row) => row.entryId === 0x1f)?.slot0, "Key W");
  assert.equal(candidateInspection.options.bindings.find((row) => row.entryId === 0x1f)?.slot1, "Up");
  assert.equal(candidateInspection.options.bindings.find((row) => row.entryId === 0x12)?.slot0, "MouseLeft");
  assert.equal(candidateInspection.options.bindings.find((row) => row.entryId === 0x13)?.slot0, "MouseLeft");

  const copySource = path.join(artifactRoot, "options-copy-source.bea");
  await fsp.copyFile(defaultOptionsPath, copySource);
  const mouseBytes = Buffer.alloc(4);
  mouseBytes.writeFloatLE(0.375);
  await writeBytes(copySource, 0x26be + 0x04, mouseBytes);
  await writeBytes(copySource, 0x24be + 0x10, Buffer.from([0x34, 0x12, 0x00, 0x00]));

  const copyPreview = await previewOptionsPatchPath(
    {
      path: defaultOptionsPath,
      copyOptionsFromPath: copySource,
      copyOptionsEntries: true,
      copyOptionsTail: true
    },
    artifactRoot,
    "native-options-copy-preview"
  );
  const csharpCopyOutput = path.join(artifactRoot, "native-options-copy-appcore.bea");
  execFileSync(
    dotnet,
    [
      "run",
      "--project",
      cliProject,
      "--",
      defaultOptionsPath,
      csharpCopyOutput,
      "--no-nodes",
      "--no-links",
      "--no-goodies",
      "--no-kills",
      "--copy-options-from",
      copySource
    ],
    { cwd: repoRoot, encoding: "utf8", maxBuffer: 1024 * 1024 * 8 }
  );
  assert.ok(copyPreview.preview.candidateArtifactPath && fs.existsSync(copyPreview.preview.candidateArtifactPath));
  assert.ok(
    (await fsp.readFile(copyPreview.preview.candidateArtifactPath)).equals(await fsp.readFile(csharpCopyOutput)),
    "native options copy preview must match C# AppCore output"
  );

  const tailPreview = await previewOptionsPatchPath(
    {
      path: defaultOptionsPath,
      mouseSensitivity: 0.42,
      languageIndex: 1,
      screenShape: 2,
      d3dDeviceIndex: 3
    },
    artifactRoot,
    "native-options-tail-preview"
  );
  assert.ok(tailPreview.preview.candidateArtifactPath && fs.existsSync(tailPreview.preview.candidateArtifactPath));
  const tailInspection = await inspectSaveFilePath(tailPreview.preview.candidateArtifactPath, artifactRoot);
  assert.equal(tailInspection.options.mouseSensitivity, 0.42);
  assert.equal(tailInspection.options.languageIndex, 1);
  assert.equal(tailInspection.options.screenShape, 2);
  assert.equal(tailInspection.options.d3dDeviceIndex, 3);

  await assert.rejects(
    () => applyOptionsPatchPath(optionsInput, artifactRoot, "native-options-apply-repo-reject"),
    /artifact\/profile root/
  );

  const copiedOptionsDir = path.join(artifactRoot, "copied-options-profile");
  const copiedOptionsPath = path.join(copiedOptionsDir, "defaultoptions.bea");
  await fsp.mkdir(copiedOptionsDir, { recursive: true });
  await fsp.copyFile(defaultOptionsPath, copiedOptionsPath);
  const copiedOriginal = await fsp.readFile(copiedOptionsPath);
  const applyPayload = await applyOptionsPatchPath(
    {
      ...optionsInput,
      path: copiedOptionsPath
    },
    artifactRoot,
    "native-options-apply-copied"
  );
  assert.equal(applyPayload.schemaVersion, "options-patch-apply.v1");
  assert.equal(applyPayload.mutation, true);
  assert.equal(applyPayload.artifact.mutation, true);
  assert.equal(applyPayload.target.changed, true);
  assert.equal(applyPayload.target.readbackVerified, true);
  assert.ok(applyPayload.artifact.artifactPath && fs.existsSync(applyPayload.artifact.artifactPath));
  assert.ok(fs.existsSync(applyPayload.backup.backupPath), "options apply backup must exist");
  assert.ok((await fsp.readFile(applyPayload.backup.backupPath)).equals(copiedOriginal), "options apply backup must match preimage");
  assert.ok((await fsp.readFile(copiedOptionsPath)).equals(await fsp.readFile(csharpOptionsOutput)), "options apply target must match C# output");
}

async function assertTypeScriptPatchMatchesCli(artifactRoot, name, sourcePath, input, cliArgs, extraAssert) {
  const preview = await previewSavePatchPath({ path: sourcePath, ...input }, artifactRoot, `native-${name}`);
  assert.equal(preview.schemaVersion, "save-patch-preview.v1");
  assert.equal(preview.mutation, false);
  assert.equal(preview.artifact.mutation, false);
  assert.ok(preview.preview.candidateArtifactPath, `${name}: candidate artifact path missing`);
  assert.ok(preview.artifact.artifactPath && fs.existsSync(preview.artifact.artifactPath), `${name}: preview artifact missing`);
  assert.ok(fs.existsSync(preview.preview.candidateArtifactPath), `${name}: candidate artifact missing`);

  const extension = path.extname(sourcePath) || ".bes";
  const csharpOutput = path.join(artifactRoot, `${name}-appcore${extension}`);
  execFileSync(dotnet, ["run", "--project", cliProject, "--", sourcePath, csharpOutput, ...cliArgs], {
    cwd: repoRoot,
    encoding: "utf8",
    maxBuffer: 1024 * 1024 * 8
  });
  assert.ok(fs.existsSync(csharpOutput), `${name}: C# output missing`);

  const tsCandidate = await fsp.readFile(preview.preview.candidateArtifactPath);
  const csharpCandidate = await fsp.readFile(csharpOutput);
  assert.equal(tsCandidate.length, csharpCandidate.length, `${name}: candidate length`);
  assert.ok(tsCandidate.equals(csharpCandidate), `${name}: TypeScript patch bytes must match C# AppCore output`);

  if (extraAssert) {
    await extraAssert(preview.preview.candidateArtifactPath, sourcePath, preview);
  }

  return preview;
}

async function assertPatchVerifierParity(artifactRoot) {
  const catalog = JSON.parse(fs.readFileSync(patchCatalogPath, "utf8"));
  assert.ok(Array.isArray(catalog.patches), "Patch catalog must contain a patches array.");

  const clean = await verifyExecutablePath(cleanExePath, repoRoot, artifactRoot);
  assert.equal(clean.fileName, "BEA.exe");
  assert.equal(clean.fileSize, fs.statSync(cleanExePath).size);
  assert.equal(clean.sha256, knownRetailSteamSha256);
  assert.equal(clean.isKnownRetailSteamHash, true);
  assert.equal(clean.catalog.patchCount, catalog.patches.length);
  assert.equal(clean.counts.original, catalog.patches.length);
  assert.equal(clean.counts.patched, 0);
  assert.equal(clean.counts.mismatch, 0);
  assert.equal(clean.counts.outOfRange, 0);
  assert.equal(clean.artifact.schemaVersion, "specimen-verification.v1");
  assert.ok(clean.artifact.artifactPath && fs.existsSync(clean.artifact.artifactPath));

  for (const patch of catalog.patches) {
    const row = clean.rows.find((candidate) => candidate.spec.id === patch.id);
    assert.ok(row, `Missing verifier row for ${patch.id}`);
    const originalBytesHex = normalizeHexBytes(patch.expected_original_bytes);
    assert.equal(row.state, "original", patch.id);
    assert.equal(row.currentBytesHex, originalBytesHex, patch.id);
    assert.equal(row.spec.fileOffset, parseOffset(patch.file_offset));
    assert.equal(row.spec.byteLength, hexBytes(patch.expected_original_bytes).length);
  }

  const firstPatch = catalog.patches[0];
  const patchedDir = await fsp.mkdtemp(path.join(artifactRoot, "patched-exe-"));
  const patchedExe = path.join(patchedDir, "BEA.exe");
  await fsp.copyFile(cleanExePath, patchedExe);
  await writeBytes(patchedExe, parseOffset(firstPatch.file_offset), hexBytes(firstPatch.patched_bytes));

  const patched = await verifyExecutablePath(patchedExe, repoRoot, artifactRoot);
  assert.equal(patched.counts.patched, 1);
  assert.equal(patched.counts.original, catalog.patches.length - 1);
  assert.equal(patched.rows.find((row) => row.spec.id === firstPatch.id)?.state, "patched");

  const mismatchDir = await fsp.mkdtemp(path.join(artifactRoot, "mismatch-exe-"));
  const mismatchExe = path.join(mismatchDir, "BEA.exe");
  await fsp.copyFile(cleanExePath, mismatchExe);
  await writeBytes(mismatchExe, parseOffset(firstPatch.file_offset), Buffer.from([0x41]));

  const mismatch = await verifyExecutablePath(mismatchExe, repoRoot, artifactRoot);
  assert.equal(mismatch.counts.mismatch, 1);
  assert.equal(mismatch.counts.original, catalog.patches.length - 1);
  assert.equal(mismatch.rows.find((row) => row.spec.id === firstPatch.id)?.state, "mismatch");

  const wrongNameExe = path.join(artifactRoot, "not-bea.exe");
  await fsp.copyFile(cleanExePath, wrongNameExe);
  await assert.rejects(
    () => verifyExecutablePath(wrongNameExe, repoRoot, artifactRoot),
    /Select BEA\.exe so patch offsets are interpreted against the expected retail binary layout/
  );

  const shortDir = await fsp.mkdtemp(path.join(artifactRoot, "short-exe-"));
  const shortExe = path.join(shortDir, "BEA.exe");
  await fsp.writeFile(shortExe, Buffer.alloc(64, 0));
  const short = await verifyExecutablePath(shortExe, repoRoot, artifactRoot);
  assert.equal(short.fileSize, 64);
  assert.equal(short.isKnownRetailSteamHash, false);
  assert.equal(short.counts.outOfRange, catalog.patches.length);
  assert.equal(short.counts.original, 0);
  assert.equal(short.counts.patched, 0);
  assert.equal(short.counts.mismatch, 0);
  assert.ok(short.rows.every((row) => row.state === "out-of-range"));
  assert.ok(short.artifact.artifactPath && fs.existsSync(short.artifact.artifactPath));

  const preparedCopy = await prepareExecutableCopyPath(cleanExePath, repoRoot, artifactRoot, "patch-executable-copy-parity");
  assert.equal(preparedCopy.schemaVersion, "patch-executable-copy.v1");
  assert.equal(preparedCopy.copy.readbackVerified, true);
  assert.equal(preparedCopy.source.sha256, knownRetailSteamSha256);
  assert.equal(preparedCopy.copy.sha256, knownRetailSteamSha256);
  assert.equal(preparedCopy.source.counts.original, catalog.patches.length);
  assert.ok(preparedCopy.artifact.artifactPath && fs.existsSync(preparedCopy.artifact.artifactPath));
  assert.ok((await fsp.readFile(preparedCopy.copy.path)).equals(await fsp.readFile(cleanExePath)));
  const copiedPatchExe = preparedCopy.copy.path;
  await assert.rejects(
    () => applyCatalogPatchSet(cleanExePath, repoRoot, artifactRoot, "stable"),
    /catalog patch apply target must be inside the app artifact\/profile root/
  );
  const apply = await applyCatalogPatchSet(copiedPatchExe, repoRoot, artifactRoot, "stable", "patch-apply-parity");
  assert.equal(apply.schemaVersion, "patch-apply.v1");
  assert.equal(apply.target.changed, true);
  assert.equal(apply.target.readbackVerified, true);
  assert.equal(apply.counts.selected, 6);
  assert.equal(apply.counts.applied, 6);
  assert.equal(apply.counts.blocked, 0);
  assert.equal(apply.verification.before.isKnownRetailSteamHash, true);
  assert.equal(apply.verification.after.isKnownRetailSteamHash, false);
  assert.ok(fs.existsSync(apply.backup.backupPath));
  assert.ok((await fsp.readFile(apply.backup.backupPath)).equals(await fsp.readFile(cleanExePath)));
  assert.ok(apply.artifact.artifactPath && fs.existsSync(apply.artifact.artifactPath));
  const appliedVerification = await verifyExecutablePath(copiedPatchExe, repoRoot, artifactRoot);
  assert.equal(appliedVerification.counts.patched, 6);

  const noOp = await applyCatalogPatchSet(copiedPatchExe, repoRoot, artifactRoot, "stable", "patch-apply-noop-parity");
  assert.equal(noOp.target.changed, false);
  assert.equal(noOp.counts.applied, 0);
  assert.equal(noOp.counts.alreadyApplied, 6);
  assert.ok((await fsp.readFile(noOp.backup.backupPath)).equals(await fsp.readFile(cleanExePath)), "existing executable backup must not be overwritten by a no-op apply");

  const restored = await restoreCatalogPatchBackup(
    copiedPatchExe,
    apply.backup.backupPath,
    repoRoot,
    artifactRoot,
    "patch-restore-parity"
  );
  assert.equal(restored.schemaVersion, "patch-restore.v1");
  assert.equal(restored.target.readbackVerified, true);
  assert.equal(restored.verification.isKnownRetailSteamHash, true);
  assert.ok(fs.existsSync(restored.preRestoreBackup.backupPath));
  assert.ok(restored.artifact.artifactPath && fs.existsSync(restored.artifact.artifactPath));
  assert.ok((await fsp.readFile(copiedPatchExe)).equals(await fsp.readFile(cleanExePath)));

  const blockedDir = await fsp.mkdtemp(path.join(artifactRoot, "patch-blocked-exe-"));
  const blockedExe = path.join(blockedDir, "BEA.exe");
  await fsp.copyFile(cleanExePath, blockedExe);
  await writeBytes(blockedExe, parseOffset(firstPatch.file_offset), Buffer.from([0x41]));
  await assert.rejects(
    () => applyCatalogPatchSet(blockedExe, repoRoot, artifactRoot, firstPatch.id),
    /blocked by unsafe current bytes/
  );
  assert.ok(!(await pathExists(`${blockedExe}.original.backup`)), "blocked executable patch apply must not create a backup");
}

async function assertJobRunnerParity(artifactRoot) {
  const catalog = await getJobCatalog(repoRoot, artifactRoot);
  const nativeSaveApply = catalog.definitions.find((job) => job.id === "save.applyPatch");
  const nativeSaveCopy = catalog.definitions.find((job) => job.id === "save.prepareCopy");
  const nativeSavePlan = catalog.definitions.find((job) => job.id === "save.planPatch");
  const nativeSavePreview = catalog.definitions.find((job) => job.id === "save.previewPatch");
  const nativeSaveRestore = catalog.definitions.find((job) => job.id === "save.restoreBackup");
  const nativeOptionsPlan = catalog.definitions.find((job) => job.id === "settings.planOptionsPatch");
  const nativeOptionsPreview = catalog.definitions.find((job) => job.id === "settings.previewOptionsPatch");
  const nativeOptionsApply = catalog.definitions.find((job) => job.id === "settings.applyOptionsPatch");
  const patchPlan = catalog.definitions.find((job) => job.id === "patch.planCatalogPatch");
  const patchPrepare = catalog.definitions.find((job) => job.id === "patch.prepareExecutableCopy");
  const patchApply = catalog.definitions.find((job) => job.id === "patch.applyCatalogPatch");
  const patchRestore = catalog.definitions.find((job) => job.id === "patch.restoreCatalogBackup");
  const appCoreInspect = catalog.definitions.find((job) => job.id === "appcore.inspectSave");
  const appCoreCompare = catalog.definitions.find((job) => job.id === "appcore.compareSaves");
  const appCorePlan = catalog.definitions.find((job) => job.id === "appcore.planSavePatch");
  const appCorePreview = catalog.definitions.find((job) => job.id === "appcore.previewSavePatch");
  const releasePolicyJob = catalog.definitions.find((job) => job.id === "release.inspectPolicy");
  const resolveCdb = catalog.definitions.find((job) => job.id === "debug.resolveCdb");
  const debugPlan = catalog.definitions.find((job) => job.id === "debug.planProbeSession");
  const debugStart = catalog.definitions.find((job) => job.id === "debug.startProbeServer");
  const runtimeList = catalog.definitions.find((job) => job.id === "runtime.listManagedProcesses");
  const runtimeTail = catalog.definitions.find((job) => job.id === "runtime.tailManagedLog");
  const runtimeStop = catalog.definitions.find((job) => job.id === "runtime.stopManagedProcess");
  const ghidraExport = catalog.definitions.find((job) => job.id === "ghidra.exportWeakFunctions");
  const ghidraDecompile = catalog.definitions.find((job) => job.id === "ghidra.exportAddressDecompile");
  const ghidraRenameDryRun = catalog.definitions.find((job) => job.id === "ghidra.validateRenameMap");
  const ghidraRenameApply = catalog.definitions.find((job) => job.id === "ghidra.applyRenameMap");
  const gameWindowCapture = catalog.definitions.find((job) => job.id === "game.planWindowCapture");
  const gameWindowFrame = catalog.definitions.find((job) => job.id === "game.captureWindowFrame");
  const gameWindowSequence = catalog.definitions.find((job) => job.id === "game.captureWindowSequence");
  const gameWindowInputPlan = catalog.definitions.find((job) => job.id === "game.planWindowInput");
  const gameWindowInputSend = catalog.definitions.find((job) => job.id === "game.sendWindowInput");
  const gameLaunchPlan = catalog.definitions.find((job) => job.id === "game.planLaunchProfile");
  const prepareSafeProfile = catalog.definitions.find((job) => job.id === "game.prepareSafeProfile");
  const gameLaunch = catalog.definitions.find((job) => job.id === "game.launchProfile");
  const assetCatalog = catalog.definitions.find((job) => job.id === "assets.catalogGameFiles");
  assert.ok(nativeSavePlan, "save.planPatch must exist in the job catalog.");
  assert.equal(nativeSavePlan.safety, "read-only");
  assert.equal(nativeSavePlan.policy.externalProcess, false);
  assert.equal(nativeSavePlan.policy.cancellable, false);
  assert.ok(nativeSavePreview, "save.previewPatch must exist in the job catalog.");
  assert.equal(nativeSavePreview.safety, "read-only");
  assert.equal(nativeSavePreview.policy.externalProcess, false);
  assert.equal(nativeSavePreview.policy.cancellable, false);
  assert.ok(nativeSaveCopy, "save.prepareCopy must exist in the job catalog.");
  assert.equal(nativeSaveCopy.safety, "mutation-gated");
  assert.equal(nativeSaveCopy.policy.externalProcess, false);
  assert.equal(nativeSaveCopy.policy.cancellable, false);
  assert.ok(nativeSaveApply, "save.applyPatch must exist in the job catalog.");
  assert.equal(nativeSaveApply.safety, "mutation-gated");
  assert.equal(nativeSaveApply.policy.externalProcess, false);
  assert.equal(nativeSaveApply.policy.cancellable, false);
  assert.ok(nativeSaveRestore, "save.restoreBackup must exist in the job catalog.");
  assert.equal(nativeSaveRestore.safety, "mutation-gated");
  assert.equal(nativeSaveRestore.policy.externalProcess, false);
  assert.equal(nativeSaveRestore.policy.cancellable, false);
  assert.ok(nativeOptionsPlan, "settings.planOptionsPatch must exist in the job catalog.");
  assert.equal(nativeOptionsPlan.safety, "read-only");
  assert.equal(nativeOptionsPlan.policy.externalProcess, false);
  assert.equal(nativeOptionsPlan.policy.cancellable, false);
  assert.ok(nativeOptionsPreview, "settings.previewOptionsPatch must exist in the job catalog.");
  assert.equal(nativeOptionsPreview.safety, "read-only");
  assert.equal(nativeOptionsPreview.policy.externalProcess, false);
  assert.equal(nativeOptionsPreview.policy.cancellable, false);
  assert.ok(nativeOptionsApply, "settings.applyOptionsPatch must exist in the job catalog.");
  assert.equal(nativeOptionsApply.safety, "mutation-gated");
  assert.equal(nativeOptionsApply.policy.externalProcess, false);
  assert.equal(nativeOptionsApply.policy.cancellable, false);
  assert.ok(patchPlan, "patch.planCatalogPatch must exist in the job catalog.");
  assert.equal(patchPlan.safety, "read-only");
  assert.equal(patchPlan.policy.externalProcess, false);
  assert.equal(patchPlan.policy.cancellable, false);
  assert.ok(patchPrepare, "patch.prepareExecutableCopy must exist in the job catalog.");
  assert.equal(patchPrepare.safety, "mutation-gated");
  assert.equal(patchPrepare.status, "available");
  assert.equal(patchPrepare.policy.externalProcess, false);
  assert.equal(patchPrepare.policy.cancellable, false);
  assert.ok(patchApply, "patch.applyCatalogPatch must exist in the job catalog.");
  assert.equal(patchApply.safety, "mutation-gated");
  assert.equal(patchApply.status, "available");
  assert.equal(patchApply.policy.externalProcess, false);
  assert.equal(patchApply.policy.cancellable, false);
  assert.ok(patchRestore, "patch.restoreCatalogBackup must exist in the job catalog.");
  assert.equal(patchRestore.safety, "mutation-gated");
  assert.equal(patchRestore.status, "available");
  assert.equal(patchRestore.policy.externalProcess, false);
  assert.equal(patchRestore.policy.cancellable, false);
  if (runAppCoreJobParity) {
    assert.ok(appCoreInspect, "appcore.inspectSave must exist in the job catalog when AppCore parity is enabled.");
    assert.equal(appCoreInspect.safety, "read-only");
    assert.equal(appCoreInspect.policy.externalProcess, true);
    assert.equal(appCoreInspect.policy.cancellable, false);
    assert.ok(appCoreCompare, "appcore.compareSaves must exist in the job catalog when AppCore parity is enabled.");
    assert.equal(appCoreCompare.safety, "read-only");
    assert.equal(appCoreCompare.policy.externalProcess, true);
    assert.equal(appCoreCompare.policy.cancellable, false);
    assert.ok(appCorePlan, "appcore.planSavePatch must exist in the job catalog when AppCore parity is enabled.");
    assert.equal(appCorePlan.safety, "read-only");
    assert.equal(appCorePlan.policy.externalProcess, true);
    assert.equal(appCorePlan.policy.cancellable, false);
    assert.ok(appCorePreview, "appcore.previewSavePatch must exist in the job catalog when AppCore parity is enabled.");
    assert.equal(appCorePreview.safety, "read-only");
    assert.equal(appCorePreview.policy.externalProcess, true);
    assert.equal(appCorePreview.policy.cancellable, false);
  } else {
    assert.equal(appCoreInspect, undefined, "appcore.inspectSave should be omitted from the default product catalog.");
    assert.equal(appCoreCompare, undefined, "appcore.compareSaves should be omitted from the default product catalog.");
    assert.equal(appCorePlan, undefined, "appcore.planSavePatch should be omitted from the default product catalog.");
    assert.equal(appCorePreview, undefined, "appcore.previewSavePatch should be omitted from the default product catalog.");
  }
  assert.ok(releasePolicyJob, "release.inspectPolicy must exist in the job catalog.");
  assert.equal(releasePolicyJob.safety, "read-only");
  assert.equal(releasePolicyJob.policy.externalProcess, false);
  assert.equal(releasePolicyJob.policy.cancellable, false);
  assert.ok(resolveCdb, "debug.resolveCdb must exist in the job catalog.");
  assert.equal(resolveCdb.safety, "read-only");
  assert.equal(resolveCdb.policy.externalProcess, true);
  assert.ok(debugPlan, "debug.planProbeSession must exist in the job catalog.");
  assert.equal(debugPlan.safety, "read-only");
  assert.equal(debugPlan.policy.externalProcess, false);
  assert.equal(debugPlan.policy.cancellable, false);
  assert.ok(debugStart, "debug.startProbeServer must exist in the job catalog.");
  assert.equal(debugStart.safety, "launch-gated");
  assert.equal(debugStart.policy.externalProcess, true);
  assert.equal(debugStart.policy.cancellable, false);
  assert.ok(runtimeList, "runtime.listManagedProcesses must exist in the job catalog.");
  assert.equal(runtimeList.safety, "read-only");
  assert.equal(runtimeList.policy.externalProcess, false);
  assert.equal(runtimeList.policy.cancellable, false);
  assert.ok(runtimeTail, "runtime.tailManagedLog must exist in the job catalog.");
  assert.equal(runtimeTail.safety, "read-only");
  assert.equal(runtimeTail.policy.externalProcess, false);
  assert.equal(runtimeTail.policy.cancellable, false);
  assert.ok(runtimeStop, "runtime.stopManagedProcess must exist in the job catalog.");
  assert.equal(runtimeStop.safety, "launch-gated");
  assert.equal(runtimeStop.policy.externalProcess, false);
  assert.equal(runtimeStop.policy.cancellable, false);
  assert.ok(ghidraExport, "ghidra.exportWeakFunctions must exist in the job catalog.");
  assert.equal(ghidraExport.safety, "read-only");
  assert.equal(ghidraExport.policy.externalProcess, true);
  assert.equal(ghidraExport.policy.cancellable, true);
  assert.ok(ghidraDecompile, "ghidra.exportAddressDecompile must exist in the job catalog.");
  assert.equal(ghidraDecompile.safety, "read-only");
  assert.equal(ghidraDecompile.policy.externalProcess, true);
  assert.equal(ghidraDecompile.policy.cancellable, true);
  assert.ok(ghidraRenameDryRun, "ghidra.validateRenameMap must exist in the job catalog.");
  assert.equal(ghidraRenameDryRun.safety, "read-only");
  assert.equal(ghidraRenameDryRun.policy.externalProcess, true);
  assert.equal(ghidraRenameDryRun.policy.cancellable, true);
  assert.equal(ghidraRenameDryRun.policy.timeoutMs, 600_000);
  assert.ok(ghidraRenameApply, "ghidra.applyRenameMap must exist in the job catalog.");
  assert.equal(ghidraRenameApply.safety, "mutation-gated");
  assert.equal(ghidraRenameApply.policy.externalProcess, true);
  assert.equal(ghidraRenameApply.policy.cancellable, true);
  assert.ok(gameWindowCapture, "game.planWindowCapture must exist in the job catalog.");
  assert.equal(gameWindowCapture.safety, "read-only");
  assert.equal(gameWindowCapture.policy.externalProcess, true);
  assert.equal(gameWindowCapture.policy.cancellable, false);
  assert.ok(gameWindowFrame, "game.captureWindowFrame must exist in the job catalog.");
  assert.equal(gameWindowFrame.safety, "read-only");
  assert.equal(gameWindowFrame.policy.externalProcess, true);
  assert.equal(gameWindowFrame.policy.cancellable, false);
  assert.ok(gameWindowSequence, "game.captureWindowSequence must exist in the job catalog.");
  assert.equal(gameWindowSequence.safety, "read-only");
  assert.equal(gameWindowSequence.policy.externalProcess, true);
  assert.equal(gameWindowSequence.policy.cancellable, false);
  assert.ok(gameWindowInputPlan, "game.planWindowInput must exist in the job catalog.");
  assert.equal(gameWindowInputPlan.safety, "read-only");
  assert.equal(gameWindowInputPlan.policy.externalProcess, true);
  assert.equal(gameWindowInputPlan.policy.cancellable, false);
  assert.ok(gameWindowInputSend, "game.sendWindowInput must exist in the job catalog.");
  assert.equal(gameWindowInputSend.safety, "launch-gated");
  assert.equal(gameWindowInputSend.policy.externalProcess, true);
  assert.equal(gameWindowInputSend.policy.cancellable, false);
  assert.ok(gameLaunchPlan, "game.planLaunchProfile must exist in the job catalog.");
  assert.equal(gameLaunchPlan.safety, "read-only");
  assert.equal(gameLaunchPlan.policy.externalProcess, false);
  assert.equal(gameLaunchPlan.policy.cancellable, false);
  assert.ok(prepareSafeProfile, "game.prepareSafeProfile must exist in the job catalog.");
  assert.equal(prepareSafeProfile.safety, "mutation-gated");
  assert.equal(prepareSafeProfile.policy.externalProcess, true);
  assert.equal(prepareSafeProfile.policy.cancellable, false);
  assert.ok(gameLaunch, "game.launchProfile must exist in the job catalog.");
  assert.equal(gameLaunch.safety, "launch-gated");
  assert.equal(gameLaunch.policy.externalProcess, true);
  assert.equal(gameLaunch.policy.cancellable, false);
  assert.ok(assetCatalog, "assets.catalogGameFiles must exist in the job catalog.");
  assert.equal(assetCatalog.safety, "read-only");
  assert.equal(assetCatalog.policy.externalProcess, true);
  assert.equal(assetCatalog.policy.cancellable, true);

  const ghidraRenameMap = path.join(artifactRoot, "bad-ghidra-rename-map.txt");
  const ghidraDryRunArtifact = path.join(artifactRoot, "bad-ghidra-rename-dry-run.json");
  await fsp.writeFile(ghidraRenameMap, "0x00421200 BadDryRunName\n", "utf8");
  await fsp.writeFile(
    ghidraDryRunArtifact,
    `${JSON.stringify(
      {
        schemaVersion: "ghidra-rename-dry-run.v1",
        mapPath: ghidraRenameMap,
        saveSucceeded: true,
        lockException: false,
        applyReady: false,
        renameReport: {
          summarySeen: true,
          applied: 0,
          skipped: 0,
          missing: 1,
          bad: 0,
          failed: 0,
          missingRows: 1,
          badAddressRows: 0
        }
      },
      null,
      2
    )}\n`,
    "utf8"
  );
  const ghidraBadApply = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "ghidra.applyRenameMap",
    inputs: {
      mapPath: ghidraRenameMap,
      dryRunArtifactPath: ghidraDryRunArtifact,
      armPhrase: "APPLY GHIDRA RENAME MAP",
      acceptsGhidraMutation: true
    }
  });
  assert.equal(ghidraBadApply.status, "rejected");
  assert.ok(ghidraBadApply.errorMessage.includes("dry-run is not clean"));

  const patchProgress = [];
  const patchRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "patch.planCatalogPatch",
      inputs: { executablePath: cleanExePath, patchIds: "stable" }
    },
    (event) => patchProgress.push(event)
  );
  assert.equal(patchRun.status, "completed");
  assert.equal(patchRun.result.payloadSchema, "patch-plan.v1");
  assert.equal(Number(patchRun.result.details.find((detail) => detail.label === "Ready to apply")?.value ?? 0), 6);
  assert.equal(Number(patchRun.result.details.find((detail) => detail.label === "Blocked")?.value ?? 1), 0);
  const planPath = patchRun.result.details.find((detail) => detail.label === "Plan artifact")?.value;
  assert.ok(planPath && fs.existsSync(planPath), "Patch plan artifact must exist.");
  assert.ok(patchProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const patchPrepareUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "patch.prepareExecutableCopy",
    inputs: { sourcePath: cleanExePath }
  });
  assert.equal(patchPrepareUnarmed.status, "rejected");
  assert.ok(patchPrepareUnarmed.errorMessage.includes("COPY BEA EXE"));

  const patchPrepareProgress = [];
  const patchPrepareRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "patch.prepareExecutableCopy",
      inputs: {
        sourcePath: cleanExePath,
        armPhrase: "COPY BEA EXE",
        acceptsLocalCopy: true
      }
    },
    (event) => patchPrepareProgress.push(event)
  );
  assert.equal(patchPrepareRun.status, "completed");
  assert.equal(patchPrepareRun.result.payloadSchema, "patch-executable-copy.v1");
  assert.equal(patchPrepareRun.artifact.kind, "local-file-copy");
  assert.equal(patchPrepareRun.artifact.mutation, true);
  const copiedJobExePath = patchPrepareRun.result.details.find((detail) => detail.label === "Copied target")?.value;
  const patchCopyArtifact = patchPrepareRun.result.details.find((detail) => detail.label === "Copy artifact")?.value;
  assert.ok(copiedJobExePath && fs.existsSync(copiedJobExePath), "Executable copy target must exist.");
  assert.ok(patchCopyArtifact && fs.existsSync(patchCopyArtifact), "Executable copy artifact must exist.");
  assert.ok((await fsp.readFile(copiedJobExePath)).equals(await fsp.readFile(cleanExePath)));
  assert.ok(patchPrepareProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const patchApplyUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "patch.applyCatalogPatch",
    inputs: { executablePath: copiedJobExePath, patchIds: "stable" }
  });
  assert.equal(patchApplyUnarmed.status, "rejected");
  assert.ok(patchApplyUnarmed.errorMessage.includes("APPLY CATALOG PATCH"));

  const patchApplyProgress = [];
  const patchApplyRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "patch.applyCatalogPatch",
      inputs: {
        executablePath: copiedJobExePath,
        patchIds: "stable",
        armPhrase: "APPLY CATALOG PATCH",
        acceptsExecutableWrite: true
      }
    },
    (event) => patchApplyProgress.push(event)
  );
  assert.equal(patchApplyRun.status, "completed");
  assert.equal(patchApplyRun.result.payloadSchema, "patch-apply.v1");
  assert.equal(patchApplyRun.artifact.kind, "local-file-write");
  assert.equal(patchApplyRun.artifact.mutation, true);
  assert.equal(Number(patchApplyRun.result.details.find((detail) => detail.label === "Applied")?.value ?? 0), 6);
  const patchApplyBackup = patchApplyRun.result.details.find((detail) => detail.label === "Backup")?.value;
  const patchApplyArtifact = patchApplyRun.result.details.find((detail) => detail.label === "Apply artifact")?.value;
  assert.ok(patchApplyBackup && fs.existsSync(patchApplyBackup), "Patch apply backup must exist.");
  assert.ok(patchApplyArtifact && fs.existsSync(patchApplyArtifact), "Patch apply artifact must exist.");
  assert.ok(patchApplyProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const patchRestoreUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "patch.restoreCatalogBackup",
    inputs: { targetPath: copiedJobExePath, backupPath: patchApplyBackup }
  });
  assert.equal(patchRestoreUnarmed.status, "rejected");
  assert.ok(patchRestoreUnarmed.errorMessage.includes("RESTORE CATALOG BACKUP"));

  const patchRestoreProgress = [];
  const patchRestoreRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "patch.restoreCatalogBackup",
      inputs: {
        targetPath: copiedJobExePath,
        backupPath: patchApplyBackup,
        armPhrase: "RESTORE CATALOG BACKUP",
        acceptsExecutableWrite: true
      }
    },
    (event) => patchRestoreProgress.push(event)
  );
  assert.equal(patchRestoreRun.status, "completed");
  assert.equal(patchRestoreRun.result.payloadSchema, "patch-restore.v1");
  assert.equal(patchRestoreRun.artifact.kind, "local-file-write");
  assert.equal(patchRestoreRun.artifact.mutation, true);
  const patchRestoreArtifact = patchRestoreRun.result.details.find((detail) => detail.label === "Restore artifact")?.value;
  assert.ok(patchRestoreArtifact && fs.existsSync(patchRestoreArtifact), "Patch restore artifact must exist.");
  assert.ok((await fsp.readFile(copiedJobExePath)).equals(await fsp.readFile(cleanExePath)));
  assert.ok(patchRestoreProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const nativeSavePlanProgress = [];
  const nativeSavePlanRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "save.planPatch",
      inputs: {
        path: goldSavePath,
        rank: "S",
        kills: 100,
        patchNodes: true,
        patchLinks: true,
        patchGoodies: true,
        patchKills: true,
        levelRanks: "1:S 2:A",
        perCategoryKills: "aircraft:100 mechs:20"
      }
    },
    (event) => nativeSavePlanProgress.push(event)
  );
  assert.equal(nativeSavePlanRun.status, "completed");
  assert.equal(nativeSavePlanRun.result.payloadSchema, "save-patch-plan.v1");
  assert.equal(nativeSavePlanRun.result.details.find((detail) => detail.label === "Requires copied apply")?.value, "yes");
  assert.equal(nativeSavePlanRun.result.details.find((detail) => detail.label === "Source unchanged")?.value, "yes");
  const nativeSavePlanArtifact = nativeSavePlanRun.result.details.find((detail) => detail.label === "Plan artifact")?.value;
  assert.ok(nativeSavePlanArtifact && fs.existsSync(nativeSavePlanArtifact), "Native save patch plan artifact must exist.");
  const nativeSavePlanPayload = JSON.parse(fs.readFileSync(nativeSavePlanArtifact, "utf8"));
  assert.equal(nativeSavePlanPayload.schemaVersion, "save-patch-plan.v1");
  assert.equal(nativeSavePlanPayload.mutation, false);
  assert.deepEqual(nativeSavePlanPayload.plan.sections, ["nodes", "links", "goodies", "kills"]);
  assert.ok(nativeSavePlanProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const nativeSavePreviewProgress = [];
  const nativeSavePreviewRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "save.previewPatch",
      inputs: {
        path: goldSavePath,
        rank: "S",
        kills: 100,
        patchNodes: true,
        patchLinks: true,
        patchGoodies: true,
        patchKills: true
      }
    },
    (event) => nativeSavePreviewProgress.push(event)
  );
  assert.equal(nativeSavePreviewRun.status, "completed");
  assert.equal(nativeSavePreviewRun.result.payloadSchema, "save-patch-preview.v1");
  assert.equal(nativeSavePreviewRun.result.details.find((detail) => detail.label === "Would change")?.value, "yes");
  assert.equal(nativeSavePreviewRun.result.details.find((detail) => detail.label === "Source unchanged")?.value, "yes");
  const nativeCandidateArtifact = nativeSavePreviewRun.result.details.find((detail) => detail.label === "Candidate artifact")?.value;
  const nativePreviewArtifact = nativeSavePreviewRun.result.details.find((detail) => detail.label === "Preview artifact")?.value;
  assert.ok(nativeCandidateArtifact && fs.existsSync(nativeCandidateArtifact), "Native save patch candidate artifact must exist.");
  assert.ok(nativePreviewArtifact && fs.existsSync(nativePreviewArtifact), "Native save patch preview artifact must exist.");
  const nativePreviewPayload = JSON.parse(fs.readFileSync(nativePreviewArtifact, "utf8"));
  assert.equal(nativePreviewPayload.schemaVersion, "save-patch-preview.v1");
  assert.equal(nativePreviewPayload.mutation, false);
  assert.ok(nativePreviewPayload.preview.differingBytes > 0);
  assert.ok(nativeSavePreviewProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const nativeApplyUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "save.applyPatch",
    inputs: { path: goldSavePath, rank: "S", kills: 100 }
  });
  assert.equal(nativeApplyUnarmed.status, "rejected");
  assert.ok(nativeApplyUnarmed.errorMessage.includes("APPLY SAVE PATCH"));

  const nativeCopyUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "save.prepareCopy",
    inputs: { sourcePath: goldSavePath }
  });
  assert.equal(nativeCopyUnarmed.status, "rejected");
  assert.ok(nativeCopyUnarmed.errorMessage.includes("COPY SAVE FILE"));

  const nativeCopyProgress = [];
  const nativeCopyRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "save.prepareCopy",
      inputs: {
        sourcePath: goldSavePath,
        armPhrase: "COPY SAVE FILE",
        acceptsLocalCopy: true
      }
    },
    (event) => nativeCopyProgress.push(event)
  );
  assert.equal(nativeCopyRun.status, "completed");
  assert.equal(nativeCopyRun.artifact.kind, "local-file-copy");
  assert.equal(nativeCopyRun.artifact.mutation, true);
  assert.equal(nativeCopyRun.result.payloadSchema, "save-copy.v1");
  assert.equal(nativeCopyRun.result.details.find((detail) => detail.label === "Read-back verified")?.value, "yes");
  const copiedJobSavePath = nativeCopyRun.result.details.find((detail) => detail.label === "Copied target")?.value;
  const nativeCopyArtifact = nativeCopyRun.result.details.find((detail) => detail.label === "Copy artifact")?.value;
  assert.ok(copiedJobSavePath && fs.existsSync(copiedJobSavePath), "Native save copy target must exist.");
  assert.ok(nativeCopyArtifact && fs.existsSync(nativeCopyArtifact), "Native save copy artifact must exist.");
  assert.ok((await fsp.readFile(copiedJobSavePath)).equals(await fsp.readFile(goldSavePath)));
  assert.ok(nativeCopyProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const nativeApplyProgress = [];
  const nativeApplyRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "save.applyPatch",
      inputs: {
        path: copiedJobSavePath,
        rank: "S",
        kills: 100,
        patchNodes: true,
        patchLinks: true,
        patchGoodies: true,
        patchKills: true,
        armPhrase: "APPLY SAVE PATCH",
        acceptsSaveWrite: true
      }
    },
    (event) => nativeApplyProgress.push(event)
  );
  assert.equal(nativeApplyRun.status, "completed");
  assert.equal(nativeApplyRun.artifact.kind, "local-file-write");
  assert.equal(nativeApplyRun.artifact.mutation, true);
  assert.equal(nativeApplyRun.result.payloadSchema, "save-patch-apply.v1");
  assert.equal(nativeApplyRun.result.details.find((detail) => detail.label === "Changed")?.value, "yes");
  assert.equal(nativeApplyRun.result.details.find((detail) => detail.label === "Read-back verified")?.value, "yes");
  const nativeApplyBackup = nativeApplyRun.result.details.find((detail) => detail.label === "Backup")?.value;
  const nativeApplyArtifact = nativeApplyRun.result.details.find((detail) => detail.label === "Apply artifact")?.value;
  assert.ok(nativeApplyBackup && fs.existsSync(nativeApplyBackup), "Native save apply backup must exist.");
  assert.ok(nativeApplyArtifact && fs.existsSync(nativeApplyArtifact), "Native save apply artifact must exist.");
  const nativeApplyPayload = JSON.parse(fs.readFileSync(nativeApplyArtifact, "utf8"));
  assert.equal(nativeApplyPayload.schemaVersion, "save-patch-apply.v1");
  assert.equal(nativeApplyPayload.mutation, true);
  assert.equal(nativeApplyPayload.target.readbackVerified, true);
  assert.ok(nativeApplyProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const nativeRestoreUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "save.restoreBackup",
    inputs: { targetPath: copiedJobSavePath, backupPath: nativeApplyBackup }
  });
  assert.equal(nativeRestoreUnarmed.status, "rejected");
  assert.ok(nativeRestoreUnarmed.errorMessage.includes("RESTORE SAVE BACKUP"));

  const nativeRestoreProgress = [];
  const nativeRestoreRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "save.restoreBackup",
      inputs: {
        targetPath: copiedJobSavePath,
        backupPath: nativeApplyBackup,
        armPhrase: "RESTORE SAVE BACKUP",
        acceptsSaveWrite: true
      }
    },
    (event) => nativeRestoreProgress.push(event)
  );
  assert.equal(nativeRestoreRun.status, "completed");
  assert.equal(nativeRestoreRun.artifact.kind, "local-file-write");
  assert.equal(nativeRestoreRun.artifact.mutation, true);
  assert.equal(nativeRestoreRun.result.payloadSchema, "save-patch-restore.v1");
  assert.equal(nativeRestoreRun.result.details.find((detail) => detail.label === "Read-back verified")?.value, "yes");
  const nativeRestoreArtifact = nativeRestoreRun.result.details.find((detail) => detail.label === "Restore artifact")?.value;
  assert.ok(nativeRestoreArtifact && fs.existsSync(nativeRestoreArtifact), "Native save restore artifact must exist.");
  const nativeRestorePayload = JSON.parse(fs.readFileSync(nativeRestoreArtifact, "utf8"));
  assert.equal(nativeRestorePayload.schemaVersion, "save-patch-restore.v1");
  assert.equal(nativeRestorePayload.mutation, true);
  assert.equal(nativeRestorePayload.target.readbackVerified, true);
  assert.ok(nativeRestoreProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const nativeOptionsPlanProgress = [];
  const nativeOptionsPlanRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "settings.planOptionsPatch",
      inputs: {
        path: defaultOptionsPath,
        soundVolume: 0.5,
        musicVolume: 0.25,
        invertWalkerP1: true,
        vibrationP2: false,
        controllerConfigP1: 123,
        keybindOverrides: "move-forward=W,Up;fire-weapon=MouseLeft,RControl"
      }
    },
    (event) => nativeOptionsPlanProgress.push(event)
  );
  assert.equal(nativeOptionsPlanRun.status, "completed");
  assert.equal(nativeOptionsPlanRun.result.payloadSchema, "options-patch-plan.v1");
  assert.equal(nativeOptionsPlanRun.result.details.find((detail) => detail.label === "Requires copied apply")?.value, "yes");
  assert.equal(nativeOptionsPlanRun.result.details.find((detail) => detail.label === "Source unchanged")?.value, "yes");
  const nativeOptionsPlanArtifact = nativeOptionsPlanRun.result.details.find((detail) => detail.label === "Plan artifact")?.value;
  assert.ok(nativeOptionsPlanArtifact && fs.existsSync(nativeOptionsPlanArtifact), "Native options patch plan artifact must exist.");
  const nativeOptionsPlanPayload = JSON.parse(fs.readFileSync(nativeOptionsPlanArtifact, "utf8"));
  assert.equal(nativeOptionsPlanPayload.schemaVersion, "options-patch-plan.v1");
  assert.equal(nativeOptionsPlanPayload.mutation, false);
  assert.deepEqual(nativeOptionsPlanPayload.plan.sections, ["career-settings", "keybinds"]);
  assert.ok(nativeOptionsPlanProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const nativeOptionsPreviewProgress = [];
  const nativeOptionsPreviewRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "settings.previewOptionsPatch",
      inputs: {
        path: defaultOptionsPath,
        soundVolume: 0.5,
        musicVolume: 0.25,
        invertWalkerP1: true,
        vibrationP2: false,
        controllerConfigP1: 123,
        keybindOverrides: "move-forward=W,Up;fire-weapon=MouseLeft,RControl"
      }
    },
    (event) => nativeOptionsPreviewProgress.push(event)
  );
  assert.equal(nativeOptionsPreviewRun.status, "completed");
  assert.equal(nativeOptionsPreviewRun.result.payloadSchema, "options-patch-preview.v1");
  assert.equal(nativeOptionsPreviewRun.result.details.find((detail) => detail.label === "Would change")?.value, "yes");
  assert.equal(nativeOptionsPreviewRun.result.details.find((detail) => detail.label === "Source unchanged")?.value, "yes");
  const nativeOptionsCandidate = nativeOptionsPreviewRun.result.details.find((detail) => detail.label === "Candidate artifact")?.value;
  const nativeOptionsPreviewArtifact = nativeOptionsPreviewRun.result.details.find((detail) => detail.label === "Preview artifact")?.value;
  assert.ok(nativeOptionsCandidate && fs.existsSync(nativeOptionsCandidate), "Native options patch candidate artifact must exist.");
  assert.ok(nativeOptionsPreviewArtifact && fs.existsSync(nativeOptionsPreviewArtifact), "Native options patch preview artifact must exist.");
  const nativeOptionsPreviewPayload = JSON.parse(fs.readFileSync(nativeOptionsPreviewArtifact, "utf8"));
  assert.equal(nativeOptionsPreviewPayload.schemaVersion, "options-patch-preview.v1");
  assert.equal(nativeOptionsPreviewPayload.mutation, false);
  assert.ok(nativeOptionsPreviewPayload.preview.differingBytes > 0);
  assert.ok(nativeOptionsPreviewProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const nativeOptionsApplyUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "settings.applyOptionsPatch",
    inputs: { path: defaultOptionsPath, soundVolume: 0.5 }
  });
  assert.equal(nativeOptionsApplyUnarmed.status, "rejected");
  assert.ok(nativeOptionsApplyUnarmed.errorMessage.includes("APPLY OPTIONS PATCH"));

  const copiedJobOptionsDir = path.join(artifactRoot, "job-copied-options-profile");
  const copiedJobOptionsPath = path.join(copiedJobOptionsDir, "defaultoptions.bea");
  await fsp.mkdir(copiedJobOptionsDir, { recursive: true });
  await fsp.copyFile(defaultOptionsPath, copiedJobOptionsPath);
  const nativeOptionsApplyProgress = [];
  const nativeOptionsApplyRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "settings.applyOptionsPatch",
      inputs: {
        path: copiedJobOptionsPath,
        soundVolume: 0.5,
        musicVolume: 0.25,
        invertWalkerP1: true,
        vibrationP2: false,
        controllerConfigP1: 123,
        keybindOverrides: "move-forward=W,Up;fire-weapon=MouseLeft,RControl",
        armPhrase: "APPLY OPTIONS PATCH",
        acceptsOptionsWrite: true
      }
    },
    (event) => nativeOptionsApplyProgress.push(event)
  );
  assert.equal(nativeOptionsApplyRun.status, "completed");
  assert.equal(nativeOptionsApplyRun.artifact.kind, "local-file-write");
  assert.equal(nativeOptionsApplyRun.artifact.mutation, true);
  assert.equal(nativeOptionsApplyRun.result.payloadSchema, "options-patch-apply.v1");
  assert.equal(nativeOptionsApplyRun.result.details.find((detail) => detail.label === "Changed")?.value, "yes");
  assert.equal(nativeOptionsApplyRun.result.details.find((detail) => detail.label === "Read-back verified")?.value, "yes");
  const nativeOptionsApplyBackup = nativeOptionsApplyRun.result.details.find((detail) => detail.label === "Backup")?.value;
  const nativeOptionsApplyArtifact = nativeOptionsApplyRun.result.details.find((detail) => detail.label === "Apply artifact")?.value;
  assert.ok(nativeOptionsApplyBackup && fs.existsSync(nativeOptionsApplyBackup), "Native options apply backup must exist.");
  assert.ok(nativeOptionsApplyArtifact && fs.existsSync(nativeOptionsApplyArtifact), "Native options apply artifact must exist.");
  const nativeOptionsApplyPayload = JSON.parse(fs.readFileSync(nativeOptionsApplyArtifact, "utf8"));
  assert.equal(nativeOptionsApplyPayload.schemaVersion, "options-patch-apply.v1");
  assert.equal(nativeOptionsApplyPayload.mutation, true);
  assert.equal(nativeOptionsApplyPayload.target.readbackVerified, true);
  assert.ok(nativeOptionsApplyProgress.some((event) => event.phase === "completed" && event.percent === 100));

  if (runAppCoreJobParity) {
    const appCoreProgress = [];
    const appCoreRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "appcore.inspectSave",
      inputs: { path: goldSavePath }
    },
    (event) => appCoreProgress.push(event)
  );
  assert.equal(appCoreRun.status, "completed");
  assert.equal(appCoreRun.result.payloadSchema, "appcore-save-analysis.v1");
  assert.equal(appCoreRun.result.details.find((detail) => detail.label === "Valid")?.value, "yes");
  assert.equal(appCoreRun.result.details.find((detail) => detail.label === "Missions")?.value, "43/43");
  const appCoreArtifact = appCoreRun.result.details.find((detail) => detail.label === "AppCore artifact")?.value;
  assert.ok(appCoreArtifact && fs.existsSync(appCoreArtifact), "AppCore host artifact must exist.");
  const appCorePayload = JSON.parse(fs.readFileSync(appCoreArtifact, "utf8"));
  assert.equal(appCorePayload.schemaVersion, "appcore-save-analysis.v1");
  assert.equal(appCorePayload.mutation, false);
  assert.equal(appCorePayload.analysis.fileSize, 10004);
  assert.equal(appCorePayload.analysis.versionWordHex, "0x4BD1");
  assert.equal(appCorePayload.analysis.counts.completedNodes, 43);
  assert.ok(appCoreProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const appCoreCompareProgress = [];
  const appCoreCompareRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "appcore.compareSaves",
      inputs: { leftPath: goldSavePath, rightPath: goldSavePath }
    },
    (event) => appCoreCompareProgress.push(event)
  );
  assert.equal(appCoreCompareRun.status, "completed");
  assert.equal(appCoreCompareRun.result.payloadSchema, "appcore-save-comparison.v1");
  assert.equal(appCoreCompareRun.result.details.find((detail) => detail.label === "Identical")?.value, "yes");
  assert.equal(appCoreCompareRun.result.details.find((detail) => detail.label === "Differing bytes")?.value, "0");
  const appCoreCompareArtifact = appCoreCompareRun.result.details.find((detail) => detail.label === "AppCore artifact")?.value;
  assert.ok(appCoreCompareArtifact && fs.existsSync(appCoreCompareArtifact), "AppCore comparison artifact must exist.");
  const appCoreComparePayload = JSON.parse(fs.readFileSync(appCoreCompareArtifact, "utf8"));
  assert.equal(appCoreComparePayload.schemaVersion, "appcore-save-comparison.v1");
  assert.equal(appCoreComparePayload.mutation, false);
  assert.equal(appCoreComparePayload.comparison.identical, true);
  assert.equal(appCoreComparePayload.comparison.differingBytes, 0);
  assert.ok(appCoreCompareProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const appCorePlanProgress = [];
  const appCorePlanRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "appcore.planSavePatch",
      inputs: {
        path: goldSavePath,
        rank: "S",
        kills: 100,
        patchNodes: true,
        patchLinks: true,
        patchGoodies: true,
        patchKills: true,
        levelRanks: "1:S 2:A",
        perCategoryKills: "aircraft:100 mechs:20"
      }
    },
    (event) => appCorePlanProgress.push(event)
  );
  assert.equal(appCorePlanRun.status, "completed");
  assert.equal(appCorePlanRun.result.payloadSchema, "appcore-save-patch-plan.v1");
  assert.equal(appCorePlanRun.result.details.find((detail) => detail.label === "Requires copied apply")?.value, "yes");
  assert.equal(appCorePlanRun.result.details.find((detail) => detail.label === "Source unchanged")?.value, "yes");
  const appCoreRequestArtifact = appCorePlanRun.result.details.find((detail) => detail.label === "Request artifact")?.value;
  const appCorePlanArtifact = appCorePlanRun.result.details.find((detail) => detail.label === "Plan artifact")?.value;
  assert.ok(appCoreRequestArtifact && fs.existsSync(appCoreRequestArtifact), "AppCore patch request artifact must exist.");
  assert.ok(appCorePlanArtifact && fs.existsSync(appCorePlanArtifact), "AppCore patch plan artifact must exist.");
  const appCoreRequestPayload = JSON.parse(fs.readFileSync(appCoreRequestArtifact, "utf8"));
  const appCorePlanPayload = JSON.parse(fs.readFileSync(appCorePlanArtifact, "utf8"));
  assert.equal(appCoreRequestPayload.schemaVersion, "appcore-save-patch-request.v1");
  assert.equal(appCoreRequestPayload.mutation, false);
  assert.equal(appCoreRequestPayload.input.path, goldSavePath);
  assert.equal(appCoreRequestPayload.input.levelRanks.length, 2);
  assert.equal(appCoreRequestPayload.input.perCategoryKills.length, 2);
  assert.equal(appCorePlanPayload.schemaVersion, "appcore-save-patch-plan.v1");
  assert.equal(appCorePlanPayload.mutation, false);
  assert.equal(appCorePlanPayload.request.requestPath, appCoreRequestArtifact);
  assert.deepEqual(appCorePlanPayload.plan.sections, ["nodes", "links", "goodies", "kills"]);
  assert.equal(appCorePlanPayload.plan.requiresCopiedApply, true);
  assert.equal(appCorePlanPayload.plan.sourceUnchanged, true);
  assert.equal(appCorePlanPayload.plan.levelRankCount, 2);
  assert.equal(appCorePlanPayload.plan.perCategoryKillCount, 2);
  assert.equal(appCorePlanPayload.current.completedNodes, 43);
  assert.ok(appCorePlanProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const appCorePreviewProgress = [];
  const appCorePreviewRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "appcore.previewSavePatch",
      inputs: { path: goldSavePath, rank: "S", kills: 100 }
    },
    (event) => appCorePreviewProgress.push(event)
  );
  assert.equal(appCorePreviewRun.status, "completed");
  assert.equal(appCorePreviewRun.result.payloadSchema, "appcore-save-patch-preview.v1");
  assert.equal(appCorePreviewRun.result.details.find((detail) => detail.label === "Would change")?.value, "yes");
  assert.equal(appCorePreviewRun.result.details.find((detail) => detail.label === "Temp copy deleted")?.value, "yes");
  const appCorePreviewArtifact = appCorePreviewRun.result.details.find((detail) => detail.label === "Preview artifact")?.value;
  assert.ok(appCorePreviewArtifact && fs.existsSync(appCorePreviewArtifact), "AppCore patch preview artifact must exist.");
  const appCorePreviewPayload = JSON.parse(fs.readFileSync(appCorePreviewArtifact, "utf8"));
  assert.equal(appCorePreviewPayload.schemaVersion, "appcore-save-patch-preview.v1");
  assert.equal(appCorePreviewPayload.mutation, false);
  assert.equal(appCorePreviewPayload.preview.wouldChange, true);
  assert.equal(appCorePreviewPayload.preview.tempOutputDeleted, true);
  assert.ok(appCorePreviewPayload.preview.differingBytes > 0);
  assert.equal(appCorePreviewPayload.beforeAfter.completedNodes.after, 43);
    assert.ok(appCorePreviewProgress.some((event) => event.phase === "completed" && event.percent === 100));
  }

  const policy = await getReleasePolicy(repoRoot, artifactRoot);
  assert.equal(policy.artifact.schemaVersion, "release-policy.v1");
  assert.ok(policy.artifact.artifactPath && fs.existsSync(policy.artifact.artifactPath));
  assert.ok(policy.counts.communityDocs > 0, "Release policy should expose community-safe docs.");
  assert.ok(policy.counts.maintainerDocs > 0, "Release policy should expose maintainer-only docs.");
  assert.ok(policy.pathRules.some((rule) => rule.relativePath === "game" && rule.classification === "deny"));
  assert.ok(policy.content.some((row) => row.id === "ghidra-runbook" && row.packageDecision === "maintainer-only"));

  const releaseProgress = [];
  const releaseRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    { definitionId: "release.inspectPolicy", inputs: {} },
    (event) => releaseProgress.push(event)
  );
  assert.equal(releaseRun.status, "completed");
  assert.equal(releaseRun.result.payloadSchema, "release-policy.v1");
  assert.ok(Number(releaseRun.result.details.find((detail) => detail.label === "Community docs")?.value ?? 0) > 0);
  assert.ok(Number(releaseRun.result.details.find((detail) => detail.label === "Existing hard-deny paths")?.value ?? 0) > 0);
  const policyArtifact = releaseRun.result.details.find((detail) => detail.label === "Policy artifact")?.value;
  assert.ok(policyArtifact && fs.existsSync(policyArtifact), "Release policy job artifact must exist.");
  assert.ok(releaseProgress.some((event) => event.phase === "completed" && event.percent === 100));

  if (resolveCdb.status === "available") {
    const progress = [];
    const run = await startWorkbenchJob(
      repoRoot,
      artifactRoot,
      catalog.definitions,
      { definitionId: "debug.resolveCdb", inputs: {} },
      (event) => progress.push(event)
    );
    assert.equal(run.status, "completed");
    assert.equal(run.result.payloadSchema, "debug-cdb-resolve.v1");
    assert.ok(run.result.details.some((detail) => detail.label === "CDB path" && /cdb\.exe$/i.test(detail.value)));
    assert.ok(progress.some((event) => event.phase === "completed" && event.percent === 100));
    assert.ok(run.artifact.artifactPath && fs.existsSync(run.artifact.artifactPath));

    const history = await listWorkbenchJobRuns(artifactRoot);
    assert.ok(history.some((entry) => entry.runId === run.runId && entry.progress.length === run.progress.length));
  }

  if (debugPlan.status === "available") {
    const progress = [];
    const run = await startWorkbenchJob(
      repoRoot,
      artifactRoot,
      catalog.definitions,
      {
        definitionId: "debug.planProbeSession",
        inputs: {
          probeId: "pause-persist-wave1.cdb.txt",
          gameRoot: path.join(repoRoot, "game"),
          port: 5005
        }
      },
      (event) => progress.push(event)
    );
    assert.equal(run.status, "completed");
    assert.equal(run.result.payloadSchema, "debug-probe-plan.v1");
    assert.ok(
      run.result.details.some((detail) => detail.label === "Server command" && detail.value.includes("start_cdb_server.ps1"))
    );
    assert.ok(
      run.result.details.some((detail) => detail.label === "Client command" && detail.value.includes("connect_cdb_client.ps1"))
    );
    const planArtifact = run.result.details.find((detail) => detail.label === "Plan artifact")?.value;
    assert.ok(planArtifact && fs.existsSync(planArtifact), "Debug probe plan artifact must exist.");
    const plan = JSON.parse(fs.readFileSync(planArtifact, "utf8"));
    assert.equal(plan.schemaVersion, "debug-probe-plan.v1");
    assert.equal(plan.mutation, false);
    assert.equal(plan.probeId, "pause-persist-wave1.cdb.txt");
    assert.match(plan.password, /^bea-/);
    assert.notEqual(plan.password, "secret");
    assert.ok(plan.serverCommandPreview.includes(plan.password));
    assert.ok(plan.clientCommandPreview.includes(plan.password));
    assert.ok(progress.some((event) => event.phase === "completed" && event.percent === 100));
  }

  if (gameLaunchPlan.status === "available") {
    const progress = [];
    const run = await startWorkbenchJob(
      repoRoot,
      artifactRoot,
      catalog.definitions,
      {
        definitionId: "game.planLaunchProfile",
        inputs: {
          gameRoot: path.join(repoRoot, "game"),
          args: ""
        }
      },
      (event) => progress.push(event)
    );
    assert.equal(run.status, "completed");
    assert.equal(run.result.payloadSchema, "game-launch-plan.v1");
    assert.equal(run.result.details.find((detail) => detail.label === "Known Steam hash")?.value, "yes");
    assert.equal(run.result.details.find((detail) => detail.label === "Arguments")?.value, "none");
    assert.ok(
      run.result.details.some((detail) => detail.label === "Command preview" && !detail.value.includes("-forcewindowed"))
    );
    const planArtifact = run.result.details.find((detail) => detail.label === "Plan artifact")?.value;
    assert.ok(planArtifact && fs.existsSync(planArtifact), "Game launch plan artifact must exist.");
    const plan = JSON.parse(fs.readFileSync(planArtifact, "utf8"));
    assert.equal(plan.schemaVersion, "game-launch-plan.v1");
    assert.equal(plan.mutation, false);
    assert.deepEqual(plan.args, []);
    assert.ok(progress.some((event) => event.phase === "completed" && event.percent === 100));
  }

  const debugUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "debug.startProbeServer",
    inputs: {
      executablePath: cleanExePath,
      probeId: "defaultoptions-wave1.cdb.txt"
    }
  });
  assert.equal(debugUnarmed.status, "rejected");
  assert.ok(debugUnarmed.errorMessage.includes("ATTACH CDB"));
  assert.ok(debugUnarmed.progress.some((event) => event.phase === "rejected"));

  const gameUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "game.launchProfile",
    inputs: {
      gameRoot: path.join(repoRoot, "game"),
      args: ""
    }
  });
  assert.equal(gameUnarmed.status, "rejected");
  assert.ok(gameUnarmed.errorMessage.includes("LAUNCH BEA"));
  assert.ok(gameUnarmed.progress.some((event) => event.phase === "rejected"));

  const prepareUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "game.prepareSafeProfile",
    inputs: {
      sourceGameRoot: path.join(repoRoot, "game"),
      profileName: "bea-safe-profile"
    }
  });
  assert.equal(prepareUnarmed.status, "rejected");
  assert.ok(prepareUnarmed.errorMessage.includes("COPY GAME PROFILE"));
  assert.ok(prepareUnarmed.progress.some((event) => event.phase === "rejected"));

  if (debugStart.status === "available") {
    const debugRepoProfile = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
      definitionId: "debug.startProbeServer",
      inputs: {
        processName: "BEA.exe",
        probeId: "pause-persist-wave1.cdb.txt",
        gameRoot: path.join(repoRoot, "game"),
        port: 5005,
        armPhrase: "ATTACH CDB",
        acceptsRuntimeAttach: true
      }
    });
    assert.equal(debugRepoProfile.status, "rejected");
    assert.ok(debugRepoProfile.errorMessage.includes("copied/safe"));
  }

  const runtimeListRun = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "runtime.listManagedProcesses",
    inputs: {}
  });
  assert.equal(runtimeListRun.status, "completed");
  assert.equal(runtimeListRun.result.payloadSchema, "managed-process-registry.v1");
  const runtimeListArtifact = runtimeListRun.result.details.find((detail) => detail.label === "Registry artifact")?.value;
  assert.ok(runtimeListArtifact && fs.existsSync(runtimeListArtifact), "Managed process registry artifact must exist.");

  const stopUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "runtime.stopManagedProcess",
    inputs: {}
  });
  assert.equal(stopUnarmed.status, "rejected");
  assert.ok(stopUnarmed.errorMessage.includes("STOP PROCESS"));

  const registryDir = path.join(artifactRoot, "artifacts", "process-registry");
  await fsp.mkdir(registryDir, { recursive: true });
  const fakeGameRunId = "job-fake-game-process";
  await fsp.writeFile(
    path.join(registryDir, "managed-processes.json"),
    `${JSON.stringify(
      {
        schemaVersion: "managed-process-registry.v1",
        updatedAt: new Date().toISOString(),
        processes: [
          {
            runId: fakeGameRunId,
            definitionId: "game.launchProfile",
            kind: "game",
            processId: process.pid,
            processName: "BEA.exe",
            startedAt: new Date().toISOString(),
            lastCheckedAt: new Date().toISOString(),
            status: "running",
            gameRoot: path.join(artifactRoot, "game-profiles", "fake"),
            executablePath: path.join(artifactRoot, "game-profiles", "fake", "BEA.exe"),
            workingDirectory: path.join(artifactRoot, "game-profiles", "fake"),
            sourceArtifactPath: path.join(artifactRoot, "fake-game-launch.json")
          }
        ]
      },
      null,
      2
    )}\n`,
    "utf8"
  );
  const windowCaptureProgress = [];
  const windowCaptureRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "game.planWindowCapture",
      inputs: {
        targetRunId: fakeGameRunId,
        processName: "BEA.exe"
      }
    },
    (event) => windowCaptureProgress.push(event)
  );
  assert.equal(windowCaptureRun.status, "completed");
  assert.equal(windowCaptureRun.result.payloadSchema, "game-window-capture-plan.v1");
  const captureStatus = windowCaptureRun.result.details.find((detail) => detail.label === "Capture status")?.value;
  assert.ok(["no-window", "ready", "multiple-candidates", "unsupported"].includes(captureStatus));
  assert.equal(windowCaptureRun.result.details.find((detail) => detail.label === "Input status")?.value, "planned");
  const windowCaptureArtifact = windowCaptureRun.result.details.find((detail) => detail.label === "Plan artifact")?.value;
  assert.ok(windowCaptureArtifact && fs.existsSync(windowCaptureArtifact), "Game-window capture plan artifact must exist.");
  const windowCapturePayload = JSON.parse(fs.readFileSync(windowCaptureArtifact, "utf8"));
  assert.equal(windowCapturePayload.schemaVersion, "game-window-capture-plan.v1");
  assert.equal(windowCapturePayload.targetRunId, fakeGameRunId);
  assert.equal(windowCapturePayload.artifact.mutation, false);
  assert.equal(windowCapturePayload.input.status, "planned");
  assert.ok(windowCaptureProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const frameCaptureProgress = [];
  const frameCaptureRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "game.captureWindowFrame",
      inputs: {
        targetRunId: fakeGameRunId,
        processName: "BEA.exe",
        maxWidth: 960,
        maxHeight: 540
      }
    },
    (event) => frameCaptureProgress.push(event)
  );
  assert.equal(frameCaptureRun.status, "completed");
  assert.equal(frameCaptureRun.result.payloadSchema, "game-window-frame-capture.v1");
  const frameStatus = frameCaptureRun.result.details.find((detail) => detail.label === "Frame status")?.value;
  assert.ok(
    ["no-window", "captured", "multiple-candidates", "unsupported", "capture-unavailable", "source-not-found"].includes(frameStatus)
  );
  assert.equal(frameCaptureRun.result.details.find((detail) => detail.label === "Input status")?.value, "planned");
  const frameCaptureArtifact = frameCaptureRun.result.details.find((detail) => detail.label === "Frame artifact")?.value;
  assert.ok(frameCaptureArtifact && fs.existsSync(frameCaptureArtifact), "Game-window frame capture artifact must exist.");
  const frameCapturePayload = JSON.parse(fs.readFileSync(frameCaptureArtifact, "utf8"));
  assert.equal(frameCapturePayload.schemaVersion, "game-window-frame-capture.v1");
  assert.equal(frameCapturePayload.targetRunId, fakeGameRunId);
  assert.equal(frameCapturePayload.artifact.mutation, false);
  assert.equal(frameCapturePayload.input.status, "planned");
  assert.ok(frameCaptureProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const frameSequenceProgress = [];
  const frameSequenceRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "game.captureWindowSequence",
      inputs: {
        targetRunId: fakeGameRunId,
        processName: "BEA.exe",
        frameCount: 2,
        intervalMs: 0,
        maxWidth: 320,
        maxHeight: 180
      }
    },
    (event) => frameSequenceProgress.push(event)
  );
  assert.equal(frameSequenceRun.status, "completed");
  assert.equal(frameSequenceRun.result.payloadSchema, "game-window-frame-sequence.v1");
  const frameSequenceStatus = frameSequenceRun.result.details.find((detail) => detail.label === "Sequence status")?.value;
  assert.ok(["no-window", "captured", "partial", "multiple-candidates", "unsupported", "capture-unavailable"].includes(frameSequenceStatus));
  const frameSequenceArtifact = frameSequenceRun.result.details.find((detail) => detail.label === "Sequence artifact")?.value;
  assert.ok(frameSequenceArtifact && fs.existsSync(frameSequenceArtifact), "Game-window frame sequence artifact must exist.");
  const frameSequencePayload = JSON.parse(fs.readFileSync(frameSequenceArtifact, "utf8"));
  assert.equal(frameSequencePayload.schemaVersion, "game-window-frame-sequence.v1");
  assert.equal(frameSequencePayload.targetRunId, fakeGameRunId);
  assert.equal(frameSequencePayload.artifact.mutation, false);
  assert.equal(frameSequencePayload.requested.frameCount, 2);
  assert.ok(frameSequenceProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const windowInputPlanProgress = [];
  const windowInputPlanRun = await startWorkbenchJob(
    repoRoot,
    artifactRoot,
    catalog.definitions,
    {
      definitionId: "game.planWindowInput",
      inputs: {
        targetRunId: fakeGameRunId,
        sequence: "tap:ENTER;wait:10;tap:ESCAPE",
        stepDelayMs: 0
      }
    },
    (event) => windowInputPlanProgress.push(event)
  );
  assert.equal(windowInputPlanRun.status, "completed");
  assert.equal(windowInputPlanRun.result.payloadSchema, "game-window-input.v1");
  const windowInputPlanArtifact = windowInputPlanRun.result.details.find((detail) => detail.label === "Input plan artifact")?.value;
  assert.ok(windowInputPlanArtifact && fs.existsSync(windowInputPlanArtifact), "Game-window input plan artifact must exist.");
  const windowInputPlanPayload = JSON.parse(fs.readFileSync(windowInputPlanArtifact, "utf8"));
  assert.equal(windowInputPlanPayload.schemaVersion, "game-window-input.v1");
  assert.equal(windowInputPlanPayload.mutation, false);
  assert.equal(windowInputPlanPayload.plannedOnly, true);
  assert.equal(windowInputPlanPayload.actionCount, 3);
  assert.ok(windowInputPlanProgress.some((event) => event.phase === "completed" && event.percent === 100));

  const windowInputUnarmed = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "game.sendWindowInput",
    inputs: {
      targetRunId: fakeGameRunId,
      sequence: "tap:ENTER"
    }
  });
  assert.equal(windowInputUnarmed.status, "rejected");
  assert.ok(windowInputUnarmed.errorMessage.includes("SEND GAME INPUT"));

  const windowInputSendRun = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "game.sendWindowInput",
    inputs: {
      targetRunId: fakeGameRunId,
      sequence: "tap:ENTER",
      stepDelayMs: 0,
      armPhrase: "SEND GAME INPUT",
      acceptsWindowInput: true
    }
  });
  assert.equal(windowInputSendRun.status, "completed");
  assert.equal(windowInputSendRun.result.payloadSchema, "game-window-input.v1");
  const windowInputArtifact = windowInputSendRun.result.details.find((detail) => detail.label === "Input artifact")?.value;
  assert.ok(windowInputArtifact && fs.existsSync(windowInputArtifact), "Game-window input artifact must exist.");
  const windowInputPayload = JSON.parse(fs.readFileSync(windowInputArtifact, "utf8"));
  assert.equal(windowInputPayload.schemaVersion, "game-window-input.v1");
  assert.equal(windowInputPayload.mutation, false);
  assert.ok(["sent", "target-required", "no-window", "multiple-candidates", "unsupported"].includes(windowInputPayload.status));
  if (windowInputPayload.status === "target-required") {
    assert.equal(windowInputPayload.plannedOnly, true);
    assert.equal(windowInputPayload.actionCount, 1);
    assert.ok(Array.isArray(windowInputPayload.actions));
  }

  const fakeManagedRunId = "job-fake-managed-process";
  const fakeManagedLogDir = path.join(artifactRoot, "artifacts", "debug-session", "fake-managed");
  const fakeManagedLogPath = path.join(fakeManagedLogDir, "cdb.log");
  await fsp.mkdir(fakeManagedLogDir, { recursive: true });
  await fsp.writeFile(
    fakeManagedLogPath,
    [
      "0:000> g",
      "Breakpoint 0 hit",
      "CCareer__Load flag=1",
      "CFEPOptions__WriteDefaultOptionsFile size=0x2714",
      "tail sentinel managed log"
    ].join("\n"),
    "utf8"
  );
  await fsp.writeFile(
    path.join(registryDir, "managed-processes.json"),
    `${JSON.stringify(
      {
        schemaVersion: "managed-process-registry.v1",
        updatedAt: new Date().toISOString(),
        processes: [
          {
            runId: fakeManagedRunId,
            definitionId: "debug.startProbeServer",
            kind: "debugger",
            processId: 99999999,
            processName: "cdb.exe",
            startedAt: new Date().toISOString(),
            lastCheckedAt: new Date().toISOString(),
            status: "running",
            gameRoot: path.join(artifactRoot, "game-profiles", "fake"),
            executablePath: path.join(artifactRoot, "game-profiles", "fake", "BEA.exe"),
            workingDirectory: path.join(artifactRoot, "game-profiles", "fake"),
            logPath: fakeManagedLogPath,
            port: 5005,
            sourceArtifactPath: path.join(artifactRoot, "fake-launch.json")
          }
        ]
      },
      null,
      2
    )}\n`,
    "utf8"
  );

  const tailRun = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "runtime.tailManagedLog",
    inputs: {
      targetRunId: fakeManagedRunId,
      byteLimit: 256
    }
  });
  assert.equal(tailRun.status, "completed");
  assert.equal(tailRun.result.payloadSchema, "managed-process-log-tail.v1");
  assert.equal(tailRun.result.details.find((detail) => detail.label === "Exists")?.value, "yes");
  assert.equal(tailRun.result.details.find((detail) => detail.label === "Truncated")?.value, "no");
  const tailText = tailRun.result.details.find((detail) => detail.label === "Tail text")?.value ?? "";
  assert.ok(tailText.includes("CFEPOptions__WriteDefaultOptionsFile"));
  const tailArtifact = tailRun.result.details.find((detail) => detail.label === "Tail artifact")?.value;
  assert.ok(tailArtifact && fs.existsSync(tailArtifact), "Managed process log-tail artifact must exist.");
  const tailPayload = JSON.parse(fs.readFileSync(tailArtifact, "utf8"));
  assert.equal(tailPayload.schemaVersion, "managed-process-log-tail.v1");
  assert.equal(tailPayload.logPath, fakeManagedLogPath);
  assert.equal(tailPayload.artifact.mutation, false);

  const stopRun = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "runtime.stopManagedProcess",
    inputs: {
      targetRunId: fakeManagedRunId,
      armPhrase: "STOP PROCESS",
      acceptsProcessStop: true
    }
  });
  assert.equal(stopRun.status, "completed");
  assert.equal(stopRun.result.payloadSchema, "managed-process-stop.v1");
  assert.equal(stopRun.result.details.find((detail) => detail.label === "Current status")?.value, "exited");
  assert.equal(stopRun.result.details.find((detail) => detail.label === "Stop requested")?.value, "no");
  const stopArtifact = stopRun.result.details.find((detail) => detail.label === "Stop artifact")?.value;
  assert.ok(stopArtifact && fs.existsSync(stopArtifact), "Managed process stop artifact must exist.");

  await fsp.writeFile(
    path.join(registryDir, "managed-processes.json"),
    `${JSON.stringify(
      {
        schemaVersion: "managed-process-registry.v1",
        updatedAt: new Date().toISOString(),
        processes: [
          {
            runId: "job-fake-outside-log",
            definitionId: "debug.startProbeServer",
            kind: "debugger",
            processId: 99999998,
            processName: "cdb.exe",
            startedAt: new Date().toISOString(),
            lastCheckedAt: new Date().toISOString(),
            status: "running",
            logPath: path.join(repoRoot, "game", "BEA.exe"),
            sourceArtifactPath: path.join(artifactRoot, "fake-launch.json")
          }
        ]
      },
      null,
      2
    )}\n`,
    "utf8"
  );
  const outsideTailRun = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
    definitionId: "runtime.tailManagedLog",
    inputs: {
      targetRunId: "job-fake-outside-log",
      byteLimit: 256
    }
  });
  assert.equal(outsideTailRun.status, "rejected");
  assert.ok(outsideTailRun.errorMessage.includes("artifact root"));

  if (gameLaunch.status === "available") {
    const gameRepoProfile = await startWorkbenchJob(repoRoot, artifactRoot, catalog.definitions, {
      definitionId: "game.launchProfile",
      inputs: {
        gameRoot: path.join(repoRoot, "game"),
        args: "",
        armPhrase: "LAUNCH BEA",
        acceptsProfileWrites: true
      }
    });
    assert.equal(gameRepoProfile.status, "rejected");
    assert.ok(gameRepoProfile.errorMessage.includes("copied/safe"));
  }

  const gameLaunchPreview = execFileSync(
    "powershell.exe",
    [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      path.join(repoRoot, "tools", "start_game_profile.ps1"),
      "-GameRoot",
      path.join(repoRoot, "game"),
      "-PrintOnly"
    ],
    { encoding: "utf8" }
  );
  assert.ok(gameLaunchPreview.includes("Start-Process"));
  assert.ok(!gameLaunchPreview.includes("-forcewindowed"));
  assert.ok(!gameLaunchPreview.includes("-ArgumentList"));

  const prepareProfilePreview = execFileSync(
    "powershell.exe",
    [
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      path.join(repoRoot, "tools", "prepare_game_profile.ps1"),
      "-SourceGameRoot",
      path.join(repoRoot, "game"),
      "-OutputRoot",
      path.join(artifactRoot, "game-profiles"),
      "-ProfileName",
      "bea-safe-profile-preview",
      "-PrintOnly"
    ],
    { encoding: "utf8" }
  );
  const prepareProfilePlan = JSON.parse(prepareProfilePreview);
  assert.equal(prepareProfilePlan.schemaVersion, "game-profile-prepare.v1");
  assert.equal(prepareProfilePlan.mutation, false);
  assert.ok(prepareProfilePlan.targetGameRoot.includes("bea-safe-profile-preview"));

  if (assetCatalog.status === "available") {
    const progress = [];
    const run = await startWorkbenchJob(
      repoRoot,
      artifactRoot,
      catalog.definitions,
      { definitionId: "assets.catalogGameFiles", inputs: {}, timeoutMs: 120_000 },
      (event) => progress.push(event)
    );
    assert.equal(run.status, "completed");
    assert.equal(run.result.payloadSchema, "asset-catalog.v1");
    assert.equal(Number(run.result.details.find((detail) => detail.label === "Catalog entries")?.value ?? 0), 3817);
    const outDir = run.result.details.find((detail) => detail.label === "Output directory")?.value;
    assert.ok(outDir && fs.existsSync(path.join(outDir, "summary.json")));
    assert.ok(outDir && fs.existsSync(path.join(outDir, "catalog.json")));
    assert.ok(progress.some((event) => event.phase === "completed" && event.percent === 100));
  }

  if (process.env.ONSLAUGHT_RUN_GHIDRA_EXPORT_PARITY === "1" && ghidraExport.status === "available") {
    const progress = [];
    const run = await startWorkbenchJob(
      repoRoot,
      artifactRoot,
      catalog.definitions,
      { definitionId: "ghidra.exportWeakFunctions", inputs: { mode: "weak" }, timeoutMs: 180_000 },
      (event) => progress.push(event)
    );
    assert.equal(run.status, "completed");
    assert.equal(run.result.payloadSchema, "ghidra-export.v1");
    assert.ok(Number(run.result.details.find((detail) => detail.label === "Total functions")?.value ?? 0) > 0);
    assert.ok(run.result.details.some((detail) => detail.label === "Output TSV" && fs.existsSync(detail.value)));
    assert.ok(progress.some((event) => event.phase === "completed" && event.percent === 100));
  }

  if (process.env.ONSLAUGHT_RUN_GHIDRA_EXPORT_PARITY === "1" && ghidraDecompile.status === "available") {
    const progress = [];
    const run = await startWorkbenchJob(
      repoRoot,
      artifactRoot,
      catalog.definitions,
      {
        definitionId: "ghidra.exportAddressDecompile",
        inputs: { addresses: "0x00421200", timeoutSec: 60 },
        timeoutMs: 180_000
      },
      (event) => progress.push(event)
    );
    assert.equal(run.status, "completed");
    assert.equal(run.result.payloadSchema, "ghidra-decompile-export.v1");
    assert.ok(Number(run.result.details.find((detail) => detail.label === "OK")?.value ?? 0) > 0);
    assert.ok(run.result.details.some((detail) => detail.label === "Index TSV" && fs.existsSync(detail.value)));
    assert.ok(progress.some((event) => event.phase === "completed" && event.percent === 100));
  }
}

async function assertMediaCatalogParity(artifactRoot) {
  const gameRoot = path.join(repoRoot, "game");
  const all = await getMediaCatalog(repoRoot, gameRoot, "", "all", 12);
  assert.equal(all.artifact.schemaVersion, "media-catalog.v1");
  assert.equal(all.artifact.mutation, false);
  assert.equal(all.counts.total, 4446);
  assert.equal(all.counts.textures, 828);
  assert.equal(all.counts.looseMeshes, 213);
  assert.equal(all.counts.embeddedMeshes, 139);
  assert.equal(all.counts.videos, 66);
  assert.equal(all.counts.languageRows, 2571);
  assert.equal(all.counts.audioRows, 629);
  assert.equal(all.counts.musicRows, 10);
  assert.equal(all.counts.voiceRows, 619);
  assert.equal(all.returnedRows, 12);
  assert.equal(all.truncated, true);
  assert.equal(all.videoGroups.length, 3);
  assert.ok(all.videoGroups.some((group) => group.family === "briefing" && group.label === "Mission briefings" && group.count === 28));
  assert.ok(all.videoGroups.every((group) => group.playbackStatus === "needs-transcode"));

  const videos = await getMediaCatalog(repoRoot, gameRoot, "briefings", "video", 5);
  assert.equal(videos.kind, "video");
  assert.ok(videos.totalRows > 0, "Video filter should return briefing rows.");
  assert.ok(videos.rows.length <= 5);
  assert.ok(videos.rows.every((row) => row.kind === "video"));
  assert.ok(videos.rows.some((row) => row.sha256 && row.detail.includes("BIKi")));
  assert.ok(videos.rows.every((row) => row.codec === "BIKi"));
  assert.ok(videos.rows.some((row) => row.label.includes("Mission 100 briefing")));
  assert.ok(videos.rows.every((row) => row.playbackStatus === "needs-transcode"));
  assert.ok(videos.rows.every((row) => row.videoPlaybackId), "Video rows should expose typed playback ids.");
  assert.ok(videos.rows.every((row) => row.sourcePath && row.sourcePath.toLowerCase().endsWith(".vid")));
  const videoPlayback = await prepareVideoPlayback(repoRoot, gameRoot, videos.rows[0].videoPlaybackId, artifactRoot, { dryRun: true });
  assert.equal(videoPlayback.artifact.schemaVersion, "video-playback.v1");
  assert.equal(videoPlayback.artifact.kind, "read-only");
  assert.equal(videoPlayback.mode, "inline-transcoded");
  assert.equal(videoPlayback.cacheStatus, "dry-run");
  assert.equal(videoPlayback.dryRun, true);
  assert.equal(videoPlayback.launched, false);
  assert.equal(videoPlayback.codec, "BIKi");
  assert.ok(videoPlayback.sourcePath.toLowerCase().endsWith(".vid"));
  assert.ok(videoPlayback.commandPreview.toLowerCase().includes("vlc") || videoPlayback.player.available === false);
  const externalVideoPlayback = await openVideoPlayback(repoRoot, gameRoot, videos.rows[0].videoPlaybackId, { dryRun: true });
  assert.equal(externalVideoPlayback.artifact.kind, "external-process");
  assert.equal(externalVideoPlayback.mode, "external-vlc");
  assert.equal(externalVideoPlayback.dryRun, true);

  const language = await getMediaCatalog(repoRoot, gameRoot, "LAP_2", "language_row", 10);
  assert.equal(language.kind, "language_row");
  assert.ok(language.rows.some((row) => row.label === "LAP_2" && row.audioPresentCount === 6));

  const texture = await getMediaCatalog(repoRoot, gameRoot, "ca_fc_hawk", "texture", 5);
  assert.equal(texture.kind, "texture");
  const previewRow = texture.rows.find((row) => row.previewId && row.label.toLowerCase().includes("ca_fc_hawk"));
  assert.ok(previewRow, "Texture filter should return a Hawk goodie preview row.");
  const preview = await getMediaPreview(repoRoot, previewRow.previewId);
  assert.equal(preview.artifact.schemaVersion, "media-preview.v1");
  assert.equal(preview.mimeType, "image/png");
  assert.ok(preview.dataUrl.startsWith("data:image/png;base64,"));
  assert.ok(preview.sizeBytes > 0);

  const packagedAppRoot = await fsp.mkdtemp(path.join(os.tmpdir(), "onslaught-packaged-media-"));
  await fsp.mkdir(path.join(packagedAppRoot, "asset-catalog"), { recursive: true });
  await fsp.copyFile(
    path.join(repoRoot, "subagents", "asset_catalog_wave1_2026-03-14", "catalog.json"),
    path.join(packagedAppRoot, "asset-catalog", "catalog.json")
  );
  const packagedTexture = await getMediaCatalog(packagedAppRoot, gameRoot, "ca_fc_hawk", "texture", 5);
  assert.ok(packagedTexture.rows.some((row) => row.label.toLowerCase().includes("ca_fc_hawk")));
  assert.ok(packagedTexture.rows.every((row) => !row.previewId), "Packaged catalog must hide preview ids when PNG exports are not bundled.");

  const audio = await getMediaCatalog(repoRoot, gameRoot, "BEA_01", "audio", 5);
  assert.equal(audio.kind, "audio");
  assert.ok(audio.rows.some((row) => row.playbackId && row.label.includes("BEA")), "Audio filter should return music rows.");
  const playback = await getAudioPlayback(repoRoot, gameRoot, audio.rows[0].playbackId);
  assert.equal(playback.artifact.schemaVersion, "audio-playback.v1");
  assert.equal(playback.mimeType, "audio/ogg");
  assert.ok(playback.dataUrl.startsWith("data:audio/ogg;base64,"));
  assert.ok(playback.sizeBytes > 0);
}

async function main() {
  const artifactRoot = await fsp.mkdtemp(path.join(os.tmpdir(), "onslaught-electron-parity-"));

  const inspected = await assertSaveParity(artifactRoot);
  await assertNativeSavePatchParity(artifactRoot);
  await assertNativeOptionsPatchParity(artifactRoot);
  await assertPatchVerifierParity(artifactRoot);
  await assertMediaCatalogParity(artifactRoot);
  await assertJobRunnerParity(artifactRoot);

  console.log("Electron parity passed.");
  console.log(`Save/options fixtures: ${inspected.length}`);
  for (const inspection of inspected) {
    console.log(`- ${path.relative(repoRoot, inspection.selectedPath)}`);
  }
  console.log(`Executable fixture: ${path.relative(repoRoot, cleanExePath)}`);
  console.log(`Artifacts: ${artifactRoot}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

function valueAtPath(value, pathExpression) {
  return pathExpression.split(".").reduce((current, key) => current?.[key], value);
}

function parseOffset(value) {
  if (typeof value === "number") {
    return value;
  }

  const raw = String(value).trim();
  return raw.toLowerCase().startsWith("0x") ? Number.parseInt(raw.slice(2), 16) : Number.parseInt(raw, 10);
}

function hexBytes(raw) {
  return Buffer.from(
    String(raw)
      .split(/[\s,;-]+/)
      .filter(Boolean)
      .map((token) => Number.parseInt(token.toLowerCase().startsWith("0x") ? token.slice(2) : token, 16))
  );
}

function normalizeHexBytes(raw) {
  return Array.from(hexBytes(raw))
    .map((byte) => byte.toString(16).padStart(2, "0").toUpperCase())
    .join(" ");
}

async function writeBytes(filePath, offset, bytes) {
  const handle = await fsp.open(filePath, "r+");
  try {
    await handle.write(bytes, 0, bytes.length, offset);
  } finally {
    await handle.close();
  }
}

async function pathExists(filePath) {
  try {
    await fsp.access(filePath);
    return true;
  } catch {
    return false;
  }
}
