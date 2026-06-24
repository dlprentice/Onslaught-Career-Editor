export function shortHash(hash: string | null | undefined) {
  if (!hash) return "Not available";
  if (hash.length <= 18) return hash;
  return `${hash.slice(0, 10)}...${hash.slice(-6)}`;
}

export function fileNameFromPath(value: string | null | undefined, fallback = "Not selected") {
  if (!value) return fallback;
  const normalized = value.replace(/\\/g, "/");
  if (/^browser:\/\/fixture/i.test(value)) return "Sample data";
  const parts = normalized.split("/").filter(Boolean);
  return parts.at(-1) ?? fallback;
}

export function sourceLabel(value: string | null | undefined) {
  if (!value) return "No file chosen";
  if (/^browser:\/\/fixture/i.test(value)) return "Preview sample";
  if (/^[a-z]:\\/i.test(value) || value.includes(":\\")) return "Local file";
  return "Project file";
}

export function safeSummary(value: string | null | undefined, fallback = "Not selected") {
  if (!value) return fallback;
  return `${fileNameFromPath(value)} - ${sourceLabel(value)}`;
}

export function humanJobTitle(value: string) {
  return value
    .replace(/\bBEA\.exe\b/g, "game executable")
    .replace(/\bGhidra\b/g, "Ghidra")
    .replace(/\bCDB\b/g, "debugger")
    .replace(/\s+/g, " ")
    .trim();
}
