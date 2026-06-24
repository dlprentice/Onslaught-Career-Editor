import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("onslaughtApi", {
  getRuntimeSnapshot: () => ipcRenderer.invoke("runtime:getSnapshot"),
  selectAndVerifyExecutable: () => ipcRenderer.invoke("specimen:selectAndVerifyExecutable"),
  verifyExecutablePath: (path: string) => ipcRenderer.invoke("specimen:verifyExecutablePath", path),
  selectAndInspectSaveFile: () => ipcRenderer.invoke("save:selectAndInspectFile"),
  inspectSaveFilePath: (path: string) => ipcRenderer.invoke("save:inspectFilePath", path),
  selectAndCompareSaveFiles: () => ipcRenderer.invoke("save:selectAndCompareFiles"),
  compareSaveFilePaths: (leftPath: string, rightPath: string) =>
    ipcRenderer.invoke("save:compareFilePaths", leftPath, rightPath),
  selectAndReadHexFile: (offset: string | number, length: string | number) =>
    ipcRenderer.invoke("re:selectAndReadHexFile", offset, length),
  readHexRange: (path: string, offset: string | number, length: string | number) =>
    ipcRenderer.invoke("re:readHexRange", path, offset, length),
  convertExecutableAddress: (path: string, virtualAddress: string | number) =>
    ipcRenderer.invoke("re:convertExecutableAddress", path, virtualAddress),
  getGhidraReadiness: () => ipcRenderer.invoke("re:getGhidraReadiness"),
  getDebugReadiness: () => ipcRenderer.invoke("re:getDebugReadiness"),
  getGameHarnessProfile: () => ipcRenderer.invoke("re:getGameHarnessProfile"),
  selectAndInspectGameFolder: () => ipcRenderer.invoke("re:selectAndInspectGameFolder"),
  inspectGameFolderPath: (gameRoot: string, persist = true) =>
    ipcRenderer.invoke("re:inspectGameFolderPath", gameRoot, persist),
  resetGameFolderProfile: () => ipcRenderer.invoke("re:resetGameFolderProfile"),
  getJobCatalog: () => ipcRenderer.invoke("re:getJobCatalog"),
  startWorkbenchJob: (request: unknown) => ipcRenderer.invoke("job:start", request),
  cancelWorkbenchJob: (runId: string) => ipcRenderer.invoke("job:cancel", runId),
  onWorkbenchJobProgress: (handler: (event: unknown) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, progress: unknown) => handler(progress);
    ipcRenderer.on("job:progress", listener);
    return () => ipcRenderer.removeListener("job:progress", listener);
  },
  getWorkbenchJobRun: (runId: string) => ipcRenderer.invoke("job:get", runId),
  listWorkbenchJobRuns: () => ipcRenderer.invoke("job:list"),
  getMediaCatalog: (query?: string, kind?: string, limit?: number) => ipcRenderer.invoke("media:getCatalog", query, kind, limit),
  getAudioPlayback: (playbackId: string) => ipcRenderer.invoke("media:getAudioPlayback", playbackId),
  prepareVideoPlayback: (playbackId: string, options?: unknown) => ipcRenderer.invoke("media:prepareVideoPlayback", playbackId, options),
  openVideoPlayback: (playbackId: string, options?: unknown) => ipcRenderer.invoke("media:openVideoPlayback", playbackId, options),
  getMediaPreview: (previewId: string) => ipcRenderer.invoke("media:getPreview", previewId),
  getContentIndex: () => ipcRenderer.invoke("content:getIndex"),
  readContentDocument: (id: string) => ipcRenderer.invoke("content:readDocument", id),
  getReleasePolicy: () => ipcRenderer.invoke("release:getPolicy"),
  openExternal: (url: string) => ipcRenderer.invoke("shell:openExternal", url)
});
