#!/usr/bin/env node
const { spawn } = require("node:child_process");
const net = require("node:net");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "../../../../..");
const host = "127.0.0.1";
const electronPath = require("electron");
const viteCliPath = path.join(repoRoot, "node_modules", "vite", "bin", "vite.js");

const children = new Set();

function spawnChild(command, args, options = {}) {
  const child = spawn(command, args, {
    cwd: repoRoot,
    env: process.env,
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
    ...options
  });
  children.add(child);
  child.once("exit", () => children.delete(child));
  return child;
}

function pipeOutput(child, prefix) {
  child.stdout.on("data", (chunk) => process.stdout.write(`[${prefix}] ${chunk}`));
  child.stderr.on("data", (chunk) => process.stderr.write(`[${prefix}] ${chunk}`));
}

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, host, () => {
      const address = server.address();
      const selectedPort = typeof address === "object" && address ? address.port : null;
      server.close(() => {
        if (selectedPort) {
          resolve(selectedPort);
        } else {
          reject(new Error("Unable to allocate a renderer smoke port."));
        }
      });
    });
  });
}

function waitForPort(port, timeoutMs = 30000) {
  const started = Date.now();
  return new Promise((resolve, reject) => {
    const check = () => {
      const socket = net.connect({ host, port }, () => {
        socket.end();
        resolve();
      });
      socket.once("error", () => {
        socket.destroy();
        if (Date.now() - started > timeoutMs) {
          reject(new Error(`Timed out waiting for http://${host}:${port}`));
        } else {
          setTimeout(check, 250);
        }
      });
    };
    check();
  });
}

function shutdown() {
  for (const child of children) {
    if (!child.killed) {
      if (process.platform === "win32" && child.pid) {
        spawn("taskkill.exe", ["/pid", String(child.pid), "/t", "/f"], {
          stdio: "ignore",
          windowsHide: true
        });
      } else {
        child.kill();
      }
    }
  }
}

process.once("SIGINT", () => {
  shutdown();
  process.exit(130);
});
process.once("SIGTERM", () => {
  shutdown();
  process.exit(143);
});

(async () => {
  const configuredPort = process.env.ONSLAUGHT_RENDERER_SMOKE_PORT
    ? Number.parseInt(process.env.ONSLAUGHT_RENDERER_SMOKE_PORT, 10)
    : null;
  const port = configuredPort && Number.isSafeInteger(configuredPort) ? configuredPort : await getFreePort();
  const rendererUrl = `http://${host}:${port}`;

  const preview = spawnChild(process.execPath, [
    viteCliPath,
    "preview",
    "--host",
    host,
    "--port",
    String(port),
    "--strictPort"
  ], {
    cwd: path.join(repoRoot, "archive", "electron-workbench", "packages", "ui")
  });
  pipeOutput(preview, "ui-preview");

  try {
    await waitForPort(port);

    const electron = spawnChild(electronPath, [
      path.join(repoRoot, "archive/electron-workbench/apps/electron/dist/main.js")
    ], {
      env: {
        ...process.env,
        ELECTRON_RENDERER_URL: rendererUrl,
        ONSLAUGHT_RENDERER_SMOKE: "1"
      }
    });
    pipeOutput(electron, "electron-smoke");

    const exitCode = await new Promise((resolve) => {
      const timeout = setTimeout(() => {
        electron.kill();
        resolve(1);
      }, 45000);
      electron.once("exit", (code) => {
        clearTimeout(timeout);
        resolve(code ?? 1);
      });
    });

    if (exitCode !== 0) {
      throw new Error(`Electron renderer smoke failed with exit code ${exitCode}.`);
    }
  } finally {
    shutdown();
  }
})().catch((error) => {
  shutdown();
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
