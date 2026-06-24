import { app, BrowserWindow, desktopCapturer, dialog, ipcMain, shell } from "electron";
import type { MediaCatalogKindFilter } from "@onslaught/contracts";
import fs from "node:fs";
import path from "node:path";
import { getContentIndex, readContentDocument } from "./content-browser";
import { cancelWorkbenchJob, getWorkbenchJobRun, listWorkbenchJobRuns, startWorkbenchJob } from "./job-runner";
import type { GameWindowFrameCaptureRequest, GameWindowFrameCaptureResult } from "./job-runner";
import { getAudioPlayback, getMediaCatalog, getMediaPreview, openVideoPlayback, prepareVideoPlayback } from "./media-catalog";
import { verifyExecutablePath } from "./patch-verifier";
import {
  convertExecutableAddress,
  getDebugReadiness,
  getGameHarnessProfile,
  getGhidraReadiness,
  getJobCatalog,
  inspectGameHarnessProfilePath,
  readHexRange,
  setGameHarnessProfile,
  clearGameHarnessProfile
} from "./re-workbench";
import { getReleasePolicy } from "./release-policy";
import { compareSaveFilePaths, inspectSaveFilePath } from "./save-inspector";

const rendererUrl = process.env.ELECTRON_RENDERER_URL;
const isRendererSmoke = process.env.ONSLAUGHT_RENDERER_SMOKE === "1";

function parseSafeExternalUrl(value: unknown): string {
  if (typeof value !== "string") {
    throw new Error("External URL must be a string.");
  }

  let parsed: URL;
  try {
    parsed = new URL(value);
  } catch {
    throw new Error("External URL is invalid.");
  }

  if (parsed.protocol !== "https:") {
    throw new Error("Only https URLs are allowed.");
  }

  return parsed.toString();
}

async function openSafeExternalUrl(value: unknown): Promise<void> {
  const safeUrl = parseSafeExternalUrl(value);
  if (!isRendererSmoke) {
    await shell.openExternal(safeUrl);
  }
}

async function captureGameWindowFrame(
  request: GameWindowFrameCaptureRequest
): Promise<GameWindowFrameCaptureResult> {
  const sources = await desktopCapturer.getSources({
    types: ["window"],
    thumbnailSize: {
      width: request.maxWidth,
      height: request.maxHeight
    },
    fetchWindowIcons: false
  });
  const normalizedTitle = request.title.trim().toLowerCase();
  const normalizedHint = request.sourceHint?.trim().toLowerCase() ?? "";
  const normalizedHwnd = request.hwndHex.replace(/^0x/i, "").toLowerCase();
  const normalizedHwndNoLeadingZeros = normalizedHwnd.replace(/^0+/, "");
  const byHwnd = normalizedHwnd
    ? sources.find((source) => {
        const normalizedId = source.id.toLowerCase();
        return (
          normalizedId.includes(normalizedHwnd) ||
          (normalizedHwndNoLeadingZeros.length > 0 && normalizedId.includes(normalizedHwndNoLeadingZeros))
        );
      })
    : null;
  const byHint = normalizedHint
    ? sources.find((source) => {
        const normalizedId = source.id.toLowerCase();
        return (
          normalizedId === normalizedHint ||
          normalizedId.includes(normalizedHint) ||
          normalizedId.includes(normalizedHwnd)
        );
      })
    : null;
  const byExactTitle = normalizedTitle
    ? sources.find((source) => source.name.trim().toLowerCase() === normalizedTitle)
    : null;
  const byLooseTitle = normalizedTitle
    ? sources.find((source) => {
        const sourceName = source.name.trim().toLowerCase();
        return sourceName.length > 0 && (sourceName.includes(normalizedTitle) || normalizedTitle.includes(sourceName));
      })
    : null;
  const source = byHwnd ?? byHint ?? byExactTitle ?? byLooseTitle ?? null;
  const matchedBy: GameWindowFrameCaptureResult["matchedBy"] = byHwnd
    ? "hwnd"
    : byHint
      ? "hint"
      : byExactTitle
      ? "exact-title"
      : byLooseTitle
        ? "loose-title"
        : "none";

  if (!source) {
    return {
      status: "source-not-found",
      sourceId: null,
      sourceName: null,
      matchedBy: "none",
      sourceCount: sources.length,
      note:
        "Desktop capture did not expose a matching BEA window source. Fullscreen Direct3D usually needs the windowed/display patch before a useful source appears."
    };
  }

  const thumbnail = source.thumbnail;
  if (thumbnail.isEmpty()) {
    return {
      status: "capture-unavailable",
      sourceId: source.id,
      sourceName: source.name,
      matchedBy,
      sourceCount: sources.length,
      note:
        "The desktop capture layer found the BEA window source, but the thumbnail was empty. This commonly happens with fullscreen Direct3D; apply the windowed/display patch before retrying."
    };
  }

  const png = thumbnail.toPNG();
  const size = thumbnail.getSize();
  const previewImage = thumbnail.resize({ width: Math.max(1, Math.min(320, size.width || request.maxWidth)) });
  const previewPng = previewImage.toPNG();
  const previewSize = previewImage.getSize();
  return {
    status: "captured",
    sourceId: source.id,
    sourceName: source.name,
    matchedBy,
    sourceCount: sources.length,
    width: size.width,
    height: size.height,
    sizeBytes: png.byteLength,
    pngBase64: png.toString("base64"),
    previewWidth: previewSize.width,
    previewHeight: previewSize.height,
    previewSizeBytes: previewPng.byteLength,
    previewPngBase64: previewPng.toString("base64"),
    note:
      "Captured one bounded desktop thumbnail. This is a still-frame probe only; no live stream was left open and no input was sent."
  };
}

function getWorkspacePath() {
  const appPath = app.getAppPath();
  const candidates = [
    appPath,
    process.cwd(),
    path.resolve(appPath, "../../.."),
    path.resolve(appPath, "..")
  ];

  for (const candidate of candidates) {
    if (
      fs.existsSync(path.join(candidate, "package.json")) &&
      (fs.existsSync(path.join(candidate, "apps", "electron")) ||
        fs.existsSync(path.join(candidate, "asset-catalog")) ||
        fs.existsSync(path.join(candidate, "subagents", "asset_catalog_wave1_2026-03-14")))
    ) {
      return candidate;
    }
  }

  return appPath;
}

function createWindow() {
  const window = new BrowserWindow({
    width: 1440,
    height: 940,
    minWidth: 1120,
    minHeight: 720,
    backgroundColor: "#11100d",
    title: "Onslaught Workbench",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  const loadPromise = rendererUrl
    ? window.loadURL(rendererUrl)
    : window.loadFile(path.join(__dirname, "../../ui/index.html"));

  if (rendererUrl) {
    if (!isRendererSmoke) {
      window.webContents.openDevTools({ mode: "detach" });
    }
  }

  window.webContents.session.setPermissionRequestHandler((_webContents, _permission, callback) => {
    callback(false);
  });

  window.webContents.setWindowOpenHandler(({ url }) => {
    void openSafeExternalUrl(url).catch(() => {
      // New windows are never allowed inside the workbench; unsafe URLs are ignored.
    });
    return { action: "deny" };
  });

  window.webContents.on("will-navigate", (event, url) => {
    if (url === window.webContents.getURL()) {
      return;
    }

    event.preventDefault();
    void openSafeExternalUrl(url).catch(() => {
      // Keep renderer navigation pinned to the packaged/dev workbench page.
    });
  });

  if (isRendererSmoke) {
    void loadPromise.then(() => runRendererSmoke(window));
  }

  return window;
}

async function runRendererSmoke(window: BrowserWindow) {
  try {
    const smokeSavePath = path.join(process.cwd(), "save-attempts", "haha-cannon-goes-brrrrr.bes");
    const smokeScript = `
      (async () => {
        const mark = (stage) => {
          window.__onslaughtRendererSmokeStage = stage;
          console.log("onslaught-renderer-smoke-stage:" + stage);
        };
        const failures = [];
        const fail = (message) => failures.push(message);
        const assert = (condition, message) => {
          if (!condition) fail(message);
        };
        const visible = (element) => {
          if (!element) return false;
          const rect = element.getBoundingClientRect();
          const style = window.getComputedStyle(element);
          return rect.width > 0 && rect.height > 0 && style.visibility !== "hidden" && style.display !== "none";
        };
        const waitFor = async (selector, timeoutMs = 15000) => {
          const started = Date.now();
          while (Date.now() - started < timeoutMs) {
            const element = document.querySelector(selector);
            if (visible(element)) return element;
            await new Promise((resolve) => setTimeout(resolve, 50));
          }
          const text = document.body?.innerText?.replace(/\\s+/g, " ").slice(0, 900) ?? "";
          throw new Error("Timed out waiting for " + selector + " | body=" + text);
        };
        const waitForExists = async (selector, timeoutMs = 15000) => {
          const started = Date.now();
          while (Date.now() - started < timeoutMs) {
            const element = document.querySelector(selector);
            if (element) return element;
            await new Promise((resolve) => setTimeout(resolve, 50));
          }
          throw new Error("Timed out waiting for " + selector);
        };
        const waitForText = async (selector, expectedText, timeoutMs = 15000) => {
          const started = Date.now();
          while (Date.now() - started < timeoutMs) {
            const element = document.querySelector(selector);
            const text = element?.textContent ?? "";
            if (visible(element) && text.includes(expectedText)) return element;
            await new Promise((resolve) => setTimeout(resolve, 50));
          }
          const text = document.querySelector(selector)?.textContent?.replace(/\\s+/g, " ").slice(0, 900) ?? "";
          throw new Error("Timed out waiting for " + selector + " to include " + expectedText + " | text=" + text);
        };
        const visibleCopy = () => {
          const clone = document.body.cloneNode(true);
          clone.querySelectorAll('[hidden], .hidden, [aria-hidden="true"]').forEach((hidden) => hidden.remove());
          clone.querySelectorAll('[data-testid="content-markdown-preview"]').forEach((preview) => {
            // Authored markdown can intentionally contain technical terms; audit the app chrome around it.
            preview.replaceWith(document.createTextNode("Curated document body"));
          });
          clone.querySelectorAll("details:not([open])").forEach((details) => {
            const summary = details.querySelector("summary")?.textContent ?? "Details";
            details.replaceWith(document.createTextNode(summary));
          });
          return clone.textContent?.replace(/\\s+/g, " ").trim() ?? "";
        };
        const assertNoInternalCopy = (context) => {
          const banned = [
            "IPC",
            "schemaVersion",
            "payload",
            "artifact",
            "job-run",
            "fixture",
            "browser-mock",
            "mutation",
            "allowlisted",
            "raw values",
            "typed desktop-app job boundary",
            "command preview",
            "full absolute",
            "raw byte offset",
            "raw byte sequence"
          ];
          const text = visibleCopy();
          const lower = text.toLowerCase();
          const found = banned.filter((term) => lower.includes(term.toLowerCase()));
          assert(found.length === 0, "visible internal copy in " + context + ": " + found.join(", "));
        };
        const settle = async () => {
          await new Promise((resolve) => setTimeout(resolve, 50));
        };
        const clickNav = async (id) => {
          const button = document.querySelector('[data-nav-id="' + id + '"]');
          if (!button) throw new Error("Navigation button not found: " + id);
          button.click();
          await settle();
        };

        mark("home");
        await waitFor("body");
        await waitForExists('[data-nav-id="saves"]');
        await waitFor("main");
        const clickTextButton = async (selector, text) => {
          const button = Array.from(document.querySelectorAll(selector)).find((element) => element.textContent?.includes(text));
          assert(Boolean(button), selector + " should include " + text);
          if (!button) throw new Error(selector + " missing button text " + text);
          button.click();
          await settle();
          return button;
        };
        const overviewText = document.body.innerText;
        assertNoInternalCopy("home");
        assert(overviewText.includes("Start with the task you want to do"), "home should route users by task");
        assert(Boolean(document.querySelector('[data-testid="home-task-cards"]')), "home task cards should render");
        assert(Boolean(document.querySelector('[data-testid="home-agentic-loop"]')), "home should explain the bounded agentic loop");
        assert(Boolean(document.querySelector('[data-testid="command-bar"]')), "command search should render in the app shell");

        mark("save-lab");
        await clickNav("saves");
        mark("save-lab:route");
        await waitFor('[data-testid="save-path-input"]');
        assertNoInternalCopy("saves");
        const savePathInput = document.querySelector('[data-testid="save-path-input"]');
        assert(Boolean(savePathInput), "save path input should render");
        const valueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        valueSetter.call(savePathInput, ${JSON.stringify(smokeSavePath)});
        savePathInput.dispatchEvent(new Event("input", { bubbles: true }));
        await settle();
        mark("save-lab:path-entered");
        const inspectSaveButton = document.querySelector('[data-testid="inspect-save-button"]');
        assert(Boolean(inspectSaveButton), "save inspect button should render");
        inspectSaveButton.click();
        mark("save-lab:inspect-clicked");
        await waitFor('[data-testid="goodie-grid"]');
        mark("save-lab:goodie-grid");
        assert(Boolean(document.querySelector('[data-testid="goodie-search"]')), "goodie search should render");
        assert(document.body.innerText.includes("Hawk bio"), "goodie rows should include per-slot content");
        await waitFor('[data-testid="options-patch-workflow"]');
        mark("save-lab:options-workflow");
        assert(Boolean(document.querySelector('[data-testid="options-screen-shape"]')), "options screen-shape input should render");
        assert(Boolean(document.querySelector('[data-testid="options-d3d-device"]')), "options D3D device input should render");
        assert(Boolean(document.querySelector('[data-testid="options-copy-from-path"]')), "options copy source input should render");
        assert(Boolean(document.querySelector('[data-testid="options-copy-entries"]')), "options copy entries toggle should render");
        assert(Boolean(document.querySelector('[data-testid="save-selected-detail"]')), "save lab should show selected item detail panel");
        const goodieLookupButton = document.querySelector('[data-testid="goodie-media-lookup"]');
        assert(Boolean(goodieLookupButton), "goodie media lookup button should render");
        goodieLookupButton.click();
        mark("save-lab:goodie-lookup-clicked");
        await waitFor('[data-testid="section-media"]');
        await waitFor('[data-testid="media-catalog"]');
        mark("save-lab:media-lookup-opened");
        const previewButton = document.querySelector('[data-testid="media-preview-button"]');
        if (previewButton) {
          previewButton.click();
          await waitFor('[data-testid="media-preview-image"]');
        }

        mark("media");
        await clickNav("media");
        await waitFor('[data-testid="section-media"]');
        assert(Boolean(document.querySelector('[data-testid="media-kind"]')), "media kind filter should render");
        const mediaSearchInput = document.querySelector('[data-testid="media-search"]');
        assert(Boolean(mediaSearchInput), "media search input should render");
        valueSetter.call(mediaSearchInput, "");
        mediaSearchInput.dispatchEvent(new Event("input", { bubbles: true }));
        await settle();
        await clickTextButton('[data-testid="media-kind"] button', "Audio");
        await waitFor('[data-testid="media-catalog"]');
        assertNoInternalCopy("media");
        const firstAudioButton = document.querySelector('[data-testid="audio-playback-button"]');
        if (firstAudioButton) {
          firstAudioButton.click();
          const activeAudioRow = await waitFor('[data-testid="audio-active-row"]');
          const audioPlayer = await waitFor('[data-testid="audio-player"]');
          assert(activeAudioRow.contains(audioPlayer), "audio player should render inside the active media row");
          assertNoInternalCopy("media audio playback");
        } else {
          assert(document.body.innerText.includes("Audio"), "audio filter should remain available when no playback row is present");
        }
        await clickTextButton('[data-testid="media-kind"] button', "Videos");
        await waitFor('[data-testid="media-catalog"]');
        const firstVideoButton = document.querySelector('[data-testid="video-playback-button"]');
        if (firstVideoButton) {
          firstVideoButton.click();
          const selectedVideoPanel = await waitFor('[data-testid="video-selected-panel"]');
          const selectedVideoText = selectedVideoPanel.textContent ?? "";
          assert(
            ["Ready", "Needs preparation", "External fallback", "Unavailable"].some((status) => selectedVideoText.includes(status)),
            "video selected panel should render a human status"
          );
        } else {
          assert(document.body.innerText.includes("Videos"), "video filter should remain available when no playback row is present");
        }
        const visibleMediaCopy = visibleCopy();
        assert(!visibleMediaCopy.includes("Command preview"), "video command preview should stay inside collapsed Details");
        assert(!visibleMediaCopy.includes("C:\\\\"), "media should not show full Windows paths by default");
        assertNoInternalCopy("media video panel");
        await clickTextButton('[data-testid="media-kind"] button', "Textures");
        await waitFor('[data-testid="media-catalog"]');
        const firstPreviewButton = document.querySelector('[data-testid="media-preview-button"]');
        if (firstPreviewButton) {
          firstPreviewButton.click();
          await waitFor('[data-testid="media-preview-image"]');
        } else {
          assert(document.body.innerText.includes("Textures"), "texture filter should remain available when no preview row is present");
        }
        assertNoInternalCopy("media texture preview");
        const videoCatalog = await window.onslaughtApi.getMediaCatalog("Mission briefings", "video", 1);
        const videoRow = videoCatalog.rows[0];
        if (videoRow?.videoPlaybackId) {
          const videoPlayback = await window.onslaughtApi.prepareVideoPlayback(videoRow.videoPlaybackId, { dryRun: true });
          assert(videoPlayback.artifact.schemaVersion === "video-playback.v1", "video playback dry-run should return typed artifact schema");
          assert(videoPlayback.mode === "inline-transcoded", "video playback should use the in-app preparation contract");
          assert(videoPlayback.dryRun === true && videoPlayback.launched === false, "renderer smoke must not launch or transcode video during dry-run");
        }

        mark("lore");
        await clickNav("lore");
        await waitFor('[data-testid="lore-document-library"]');
        await waitFor('[data-testid="lore-article-reader"]');
        await waitFor('[data-testid="lore-article-outline"]');
        assert(!document.body.innerText.includes("Game tools"), "lore reader should not be squeezed by the global status rail");
        const contentSearch = await waitFor('[data-testid="content-search"]');
        const contentSearchSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        const setContentSearch = async (value) => {
          contentSearchSetter.call(contentSearch, value);
          contentSearch.dispatchEvent(new Event("input", { bubbles: true }));
          await settle();
        };
        const clickLoreDocument = async (buttonText) => {
          const button = Array.from(document.querySelectorAll('[data-testid="lore-document-library"] button')).find((candidate) =>
            candidate.textContent?.includes(buttonText)
          );
          assert(Boolean(button), "lore library should expose " + buttonText);
          if (!button) throw new Error("missing lore document button: " + buttonText);
          button.click();
          await waitForText('[data-testid="lore-article-reader"]', buttonText);
        };
        const clickMarkdownHref = async (href) => {
          const link = Array.from(document.querySelectorAll('[data-testid="markdown-link"]')).find(
            (candidate) => candidate.getAttribute("data-link-href") === href
          );
          assert(Boolean(link), "markdown link should render for " + href);
          if (!link) throw new Error("missing markdown link: " + href);
          link.click();
          await settle();
        };
        await clickMarkdownHref("Start-Here.md");
        await waitForText('[data-testid="lore-link-notice"]', "not in the curated reader yet");
        await clickMarkdownHref("roadmap/ROADMAP-INDEX.md");
        await waitForText('[data-testid="lore-link-notice"]', "Opened Roadmap index");
        await waitForText('[data-testid="lore-article-reader"]', "Roadmap index");
        await setContentSearch("AYA tags quick reference");
        await clickLoreDocument("AYA tags quick reference");
        await clickMarkdownHref("#texture-tags");
        await waitForText('[data-testid="lore-link-notice"]', "Jumped within this document");
        await setContentSearch("Community preservation");
        await clickLoreDocument("Community preservation");
        await clickMarkdownHref("https://www.speedrun.com/battle_engine_aquila");
        await waitForText('[data-testid="lore-link-notice"]', "Opened the link in your browser");
        let rejectedInsecureExternal = false;
        try {
          await window.onslaughtApi.openExternal("http://example.com");
        } catch {
          rejectedInsecureExternal = true;
        }
        assert(rejectedInsecureExternal, "external link bridge should reject non-https URLs");
        contentSearchSetter.call(contentSearch, "Workbench architecture");
        contentSearch.dispatchEvent(new Event("input", { bubbles: true }));
        await settle();
        const architectureButton = Array.from(document.querySelectorAll("button")).find((button) =>
          button.textContent?.includes("Workbench architecture")
        );
        assert(Boolean(architectureButton), "lore search should expose the workbench architecture document");
        if (!architectureButton) throw new Error("lore search did not expose the workbench architecture document");
        architectureButton.click();
        await waitFor('[data-testid="lore-article-reader"]');
        await waitFor('[data-testid="lore-article-outline"]');
        const architecturePreview = await waitForText('[data-testid="content-markdown-preview"]', "durable artifacts");
        const architecturePreviewText = architecturePreview.textContent ?? "";
        assert(
          architecturePreviewText.includes("durable artifacts"),
          "lore markdown body should preserve authored document wording"
        );
        assertNoInternalCopy("lore");

        mark("patch-bench");
        await clickNav("patches");
        await waitFor('[data-testid="patch-workflow"]');
        await waitFor('[data-testid="specimen-verifier"]');
        const patchText = visibleCopy();
        assertNoInternalCopy("patch bench");
        assert(patchText.includes("Original stays unchanged"), "patch bench should communicate original-file safety");
        assert(patchText.includes("Choose and verify executable"), "patch bench should be a guided flow");
        assert(patchText.includes("Choose patches"), "patch bench should separate patch selection");
        assert(patchText.includes("Review and apply to copy"), "patch bench should review before apply");
        assert(!patchText.includes("0x0052"), "raw patch offsets should stay inside collapsed Details");

        mark("re-lab");
        await clickNav("re-lab");
        await waitFor('[data-testid="section-re-lab"]');
        await waitFor('[data-testid="re-lab-data-honesty"]');
        await waitFor('[data-testid="re-results"]');
        await waitFor('[data-testid="re-inspector"]');
        await waitFor('[data-testid="ask-agent-panel"]');
        assertNoInternalCopy("re-lab");
        const reText = document.body.innerText;
        assert(reText.includes("Explore assets, functions, and structures"), "RE Lab should explain asset/function exploration");
        assert(reText.includes("Ask the agent"), "RE Lab should expose a bounded planning affordance");
        assert(reText.includes("Example investigation"), "RE Lab should label sample results honestly");
        assert(reText.includes("not live extracted game results"), "RE Lab should not imply sample rows are live data");
        assert(reText.includes("Create a bounded plan"), "RE Lab agent panel should describe bounded planning");
        assert(reText.includes("Run safe read-only tools"), "RE Lab agent panel should describe safe read-only tool use");
        assert(reText.includes("Export a summary"), "RE Lab agent panel should describe summary export");
        assert(!reText.includes("dotnet run --project OnslaughtCareerEditor.AppCore.Host"), "AppCore host jobs should be hidden by default");
        const reSearchInput = document.querySelector('[data-testid="re-search"]');
        assert(Boolean(reSearchInput), "RE Lab search should render");
        valueSetter.call(reSearchInput, "Render");
        reSearchInput.dispatchEvent(new Event("input", { bubbles: true }));
        await settle();
        const createPlanButton = await waitFor('[data-testid="create-bounded-plan"]');
        createPlanButton.click();
        await waitFor('[data-testid="re-plan-created"]');

        mark("game-harness");
        await clickNav("harness");
        await waitFor('[data-testid="section-harness"]');
        await waitFor('[data-testid="harness-launch-step"]');
        await waitFor('[data-testid="harness-launch-button"]');
        await waitFor('[data-testid="harness-launch-readiness"]');
        await waitFor('[data-testid="harness-send-input-button"]');
        await waitFor('[data-testid="capture-window-plan"]');
        await waitFor('[data-testid="agentic-loop-readiness"]');
        assertNoInternalCopy("harness");
        const harnessText = document.body.innerText;
        const launchButton = document.querySelector('[data-testid="harness-launch-button"]');
        const sendInputButton = document.querySelector('[data-testid="harness-send-input-button"]');
        assert(launchButton?.getAttribute("data-job-id") === "game.launchProfile", "Game Harness launch button should be wired to game.launchProfile");
        assert(
          document.querySelector('[data-testid="harness-launch-readiness"]')?.textContent?.match(/Not ready|Ready|Running|completed/i),
          "Game Harness launch step should show human readiness text"
        );
        assert(sendInputButton?.getAttribute("data-job-id") === "game.sendWindowInput", "Game Harness input button should be wired to scoped input");
        assert(sendInputButton?.disabled, "Game Harness input send should require visible exact-target confirmation");
        assert(harnessText.includes("Confirm exact managed target before sending input"), "Game Harness should explain scoped input arming");
        assert(harnessText.includes("Prepare Copied Profile"), "Game Harness should start with copied profile preparation");
        assert(harnessText.includes("Apply Windowed Patch"), "Game Harness should guide the windowed-patch step");
        assert(harnessText.includes("Launch Managed Game"), "Game Harness should separate managed launch");
        assert(harnessText.includes("Observe / Input / Observe"), "Game Harness should show the bounded loop");
        assert(harnessText.includes("Stop and Review"), "Game Harness should keep cleanup visible");
        assert(harnessText.includes("Exact-target input only"), "Game Harness should state scoped input safety");
        assert(harnessText.includes("Guided proof flow is available"), "Game Harness should not pretend custom objective planning is implemented");
        assert(!harnessText.includes("force_windowed"), "catalog patch id should not be primary UI copy");

        mark("release");
        await clickNav("release");
        await waitFor('[data-testid="section-release"]');
        await waitFor('[data-testid="release-gates"]');
        await waitFor('[data-testid="release-scope"]');
        await waitFor('[data-testid="release-evidence-reports"]');
        assertNoInternalCopy("release");
        const releaseText = document.body.innerText;
        assert(releaseText.includes("Public-safe candidate"), "release page should show public-safe posture");
        assert(releaseText.includes("Private evidence"), "release page should explain private evidence posture");
        assert(releaseText.includes("Packaged runtime"), "release page should name the next release proof gap");

        return { ok: failures.length === 0, failures };
      })();
      `;
    const result = await Promise.race([
      window.webContents.executeJavaScript(smokeScript, true),
      new Promise<never>((_resolve, reject) => {
        setTimeout(async () => {
          let stage = "unknown";
          try {
            const currentStage = await window.webContents.executeJavaScript(
              "window.__onslaughtRendererSmokeStage || 'not-started'",
              true
            );
            if (typeof currentStage === "string" && currentStage.trim()) {
              stage = currentStage;
            }
          } catch {
            stage = "unavailable";
          }
          reject(new Error(`Renderer smoke timed out at stage: ${stage}`));
        }, 40000);
      })
    ]);

    const resultLine = `ONSLAUGHT_RENDERER_SMOKE_RESULT ${JSON.stringify(result)}`;
    console.log(resultLine);
    if (!result.ok) {
      console.error(`ONSLAUGHT_RENDERER_SMOKE_FAILURES ${JSON.stringify(result.failures)}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 25));
    app.exit(result.ok ? 0 : 1);
  } catch (error) {
    console.error("ONSLAUGHT_RENDERER_SMOKE_ERROR", error instanceof Error ? error.message : String(error));
    app.exit(1);
  }
}

ipcMain.handle("runtime:getSnapshot", () => ({
  mode: rendererUrl ? "desktop-dev" : "desktop-packaged",
  repoRoot: getWorkspacePath(),
  generatedAt: new Date().toISOString(),
  migration: {
    headline: "Onslaught Workbench is the active app",
    summary:
      "Save/options editing, executable patching, media, lore, and RE job control now run through the safe desktop job runner.",
    status: "active"
  },
  metrics: [
    { label: "Function symbols", value: "5861 / 5861", tone: "good" },
    { label: "Media catalog rows", value: "4446", tone: "good" },
    { label: "Temporary parity tests", value: "19 / 19", tone: "good" },
    { label: "App gates", value: "passing", tone: "good" }
  ],
  featureLanes: [
    {
      id: "saves",
      title: "Save and options lab",
      status: "active",
      detail: "Native TypeScript inspect, compare, copy, plan, preview, apply, and restore for .bes/.bea/defaultoptions files."
    },
    {
      id: "patches",
      title: "Binary patch bench",
      status: "active",
      detail: "Catalog verify, copied-executable prepare, apply, restore, and read-back byte provenance."
    },
    {
      id: "media",
      title: "Media and lore browser",
      status: "active",
      detail: "Curated lore, public-safe media catalogs, language/video/asset rows, constrained OGG playback, and app-owned Bink video preparation from the selected game root."
    },
    {
      id: "re-lab",
      title: "RE automation lab",
      status: "active foundation",
      detail: "Hex reads, PE address conversion, Ghidra/CDB readiness, launch/debug planning, and managed process controls are exposed as typed jobs."
    }
  ],
  releaseGates: [
    { label: "docsync_check.py", status: "passing", detail: "Lore-book mirrors are synchronized for the current app docs." },
    { label: "release_profile_snapshot.py --check", status: "passing", detail: "Generated profile evidence files are current after the app allowlist refresh." },
    { label: "release_curated_manifest.py --check", status: "passing", detail: "Curated manifest includes the app workspace and bundle files." }
  ]
}));

ipcMain.handle("specimen:selectAndVerifyExecutable", async () => {
  const result = await dialog.showOpenDialog({
    title: "Select Battle Engine Aquila BEA.exe",
    properties: ["openFile"],
    filters: [{ name: "Battle Engine Aquila executable", extensions: ["exe"] }]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return verifyExecutablePath(result.filePaths[0], getWorkspacePath(), app.getPath("userData"));
});

ipcMain.handle("specimen:verifyExecutablePath", async (_event, executablePath: string) => {
  if (typeof executablePath !== "string" || executablePath.trim().length === 0) {
    throw new Error("Executable path is required.");
  }

  return verifyExecutablePath(executablePath, getWorkspacePath(), app.getPath("userData"));
});

ipcMain.handle("save:selectAndInspectFile", async () => {
  const result = await dialog.showOpenDialog({
    title: "Select Battle Engine Aquila save/options file",
    properties: ["openFile"],
    filters: [
      { name: "Battle Engine Aquila saves/options", extensions: ["bes", "bea"] },
      { name: "All files", extensions: ["*"] }
    ]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return inspectSaveFilePath(result.filePaths[0], app.getPath("userData"));
});

ipcMain.handle("save:inspectFilePath", async (_event, savePath: string) => {
  if (typeof savePath !== "string" || savePath.trim().length === 0) {
    throw new Error("Save/options path is required.");
  }

  return inspectSaveFilePath(savePath, app.getPath("userData"));
});

ipcMain.handle("save:selectAndCompareFiles", async () => {
  const result = await dialog.showOpenDialog({
    title: "Select two Battle Engine Aquila save/options files",
    properties: ["openFile", "multiSelections"],
    filters: [
      { name: "Battle Engine Aquila saves/options", extensions: ["bes", "bea"] },
      { name: "All files", extensions: ["*"] }
    ]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  if (result.filePaths.length !== 2) {
    throw new Error("Select exactly two files to compare.");
  }

  return compareSaveFilePaths(result.filePaths[0], result.filePaths[1], app.getPath("userData"));
});

ipcMain.handle("save:compareFilePaths", async (_event, leftPath: string, rightPath: string) => {
  if (typeof leftPath !== "string" || leftPath.trim().length === 0) {
    throw new Error("Left save/options path is required.");
  }

  if (typeof rightPath !== "string" || rightPath.trim().length === 0) {
    throw new Error("Right save/options path is required.");
  }

  return compareSaveFilePaths(leftPath, rightPath, app.getPath("userData"));
});

ipcMain.handle("re:selectAndReadHexFile", async (_event, offset: string | number, length: string | number) => {
  const result = await dialog.showOpenDialog({
    title: "Select file for read-only hex window",
    properties: ["openFile"],
    filters: [{ name: "All files", extensions: ["*"] }]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return readHexRange(result.filePaths[0], offset, length, app.getPath("userData"));
});

ipcMain.handle(
  "re:readHexRange",
  async (_event, selectedPath: string, offset: string | number, length: string | number) => {
    if (typeof selectedPath !== "string" || selectedPath.trim().length === 0) {
      throw new Error("File path is required.");
    }

    return readHexRange(selectedPath, offset, length, app.getPath("userData"));
  }
);

ipcMain.handle("re:convertExecutableAddress", async (_event, executablePath: string, virtualAddress: string | number) => {
  if (typeof executablePath !== "string" || executablePath.trim().length === 0) {
    throw new Error("Executable path is required.");
  }

  return convertExecutableAddress(executablePath, virtualAddress);
});

ipcMain.handle("re:getGhidraReadiness", () => getGhidraReadiness(getWorkspacePath()));

ipcMain.handle("re:getDebugReadiness", () => getDebugReadiness(getWorkspacePath()));

ipcMain.handle("re:getGameHarnessProfile", () => getGameHarnessProfile(getWorkspacePath(), app.getPath("userData")));

ipcMain.handle("re:selectAndInspectGameFolder", async () => {
  const result = await dialog.showOpenDialog({
    title: "Select Battle Engine Aquila game folder",
    properties: ["openDirectory"],
    filters: [{ name: "Battle Engine Aquila game folder", extensions: ["*"] }]
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return setGameHarnessProfile(getWorkspacePath(), app.getPath("userData"), result.filePaths[0]);
});

ipcMain.handle("re:inspectGameFolderPath", async (_event, gameRoot: string, persist = true) => {
  if (typeof gameRoot !== "string" || gameRoot.trim().length === 0) {
    throw new Error("Game folder path is required.");
  }

  if (persist) {
  return setGameHarnessProfile(getWorkspacePath(), app.getPath("userData"), gameRoot);
  }

  return inspectGameHarnessProfilePath(getWorkspacePath(), gameRoot);
});

ipcMain.handle("re:resetGameFolderProfile", () => clearGameHarnessProfile(getWorkspacePath(), app.getPath("userData")));

ipcMain.handle("re:getJobCatalog", () => getJobCatalog(getWorkspacePath(), app.getPath("userData")));

ipcMain.handle("job:start", async (_event, request) => {
  const catalog = await getJobCatalog(getWorkspacePath(), app.getPath("userData"));
  return startWorkbenchJob(getWorkspacePath(), app.getPath("userData"), catalog.definitions, request, (progress) => {
    _event.sender.send("job:progress", progress);
  }, { captureGameWindowFrame });
});

ipcMain.handle("job:cancel", (_event, runId: string) => {
  if (typeof runId !== "string" || runId.trim().length === 0) {
    throw new Error("Job run id is required.");
  }

  return cancelWorkbenchJob(runId);
});

ipcMain.handle("job:get", (_event, runId: string) => {
  if (typeof runId !== "string" || runId.trim().length === 0) {
    throw new Error("Job run id is required.");
  }

  return getWorkbenchJobRun(runId);
});

ipcMain.handle("job:list", () => listWorkbenchJobRuns(app.getPath("userData")));

ipcMain.handle("media:getCatalog", async (_event, query?: string, kind?: string, limit?: number) => {
  const kindFilter: MediaCatalogKindFilter = typeof kind === "string" ? (kind as MediaCatalogKindFilter) : "all";
  const profile = await getGameHarnessProfile(getWorkspacePath(), app.getPath("userData"));
  return getMediaCatalog(getWorkspacePath(), profile.gameRoot, query, kindFilter, limit);
});

ipcMain.handle("media:getAudioPlayback", async (_event, playbackId: string) => {
  if (typeof playbackId !== "string" || playbackId.trim().length === 0) {
    throw new Error("Audio playback id is required.");
  }
  const profile = await getGameHarnessProfile(getWorkspacePath(), app.getPath("userData"));
  return getAudioPlayback(getWorkspacePath(), profile.gameRoot, playbackId);
});

ipcMain.handle("media:prepareVideoPlayback", async (_event, playbackId: string, options = {}) => {
  if (typeof playbackId !== "string" || playbackId.trim().length === 0) {
    throw new Error("Video playback id is required.");
  }
  const profile = await getGameHarnessProfile(getWorkspacePath(), app.getPath("userData"));
  return prepareVideoPlayback(getWorkspacePath(), profile.gameRoot, playbackId, app.getPath("userData"), options);
});

ipcMain.handle("media:openVideoPlayback", async (_event, playbackId: string, options = {}) => {
  if (typeof playbackId !== "string" || playbackId.trim().length === 0) {
    throw new Error("Video playback id is required.");
  }
  const profile = await getGameHarnessProfile(getWorkspacePath(), app.getPath("userData"));
  return openVideoPlayback(getWorkspacePath(), profile.gameRoot, playbackId, options);
});

ipcMain.handle("media:getPreview", async (_event, previewId: string) => {
  if (typeof previewId !== "string" || previewId.trim().length === 0) {
    throw new Error("Media preview id is required.");
  }
  return getMediaPreview(getWorkspacePath(), previewId);
});

ipcMain.handle("content:getIndex", () => getContentIndex(getWorkspacePath()));

ipcMain.handle("content:readDocument", (_event, id: string) => {
  if (typeof id !== "string" || id.trim().length === 0) {
    throw new Error("Content document id is required.");
  }

  return readContentDocument(getWorkspacePath(), id);
});

ipcMain.handle("release:getPolicy", () => getReleasePolicy(getWorkspacePath(), app.getPath("userData")));

ipcMain.handle("shell:openExternal", async (_event, url: string) => {
  await openSafeExternalUrl(url);
});

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
