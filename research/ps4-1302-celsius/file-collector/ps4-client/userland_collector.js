/*
 * Consent-only PS4 userland collector protocol adapter.
 *
 * This file does not exploit WebKit, access kernel memory, enumerate paths, or
 * provide a native reader. The caller must supply an explicit readChunk(path,
 * offset, length) function for files it is authorized to read.
 */

const MAX_CHUNK = 1024 * 1024;
const DEFAULT_RETRIES = 4;

function isAllowedSource(source, prefixes) {
  if (typeof source !== "string" || source.includes("\0")) return false;
  return prefixes.some((p) => source.startsWith(p) && !source.includes(".."));
}

async function sha256Hex(bytes) {
  if (!globalThis.crypto?.subtle) throw new Error("crypto.subtle is required");
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }

async function request(url, options = {}, retries = DEFAULT_RETRIES) {
  let last;
  for (let i = 0; i <= retries; i++) {
    try {
      const res = await fetch(url, options);
      if (res.ok) return res;
      last = new Error(`HTTP ${res.status}`);
    } catch (e) { last = e; }
    if (i < retries) await sleep(250 * (2 ** i));
  }
  throw last;
}

function validateManifest(manifest, prefixes) {
  if (!manifest || manifest.schema !== 1 || !Array.isArray(manifest.files)) {
    throw new Error("unsupported manifest");
  }
  for (const f of manifest.files) {
    if (!f.id || !isAllowedSource(f.source, prefixes)) throw new Error(`source not allowlisted: ${f.id}`);
    if (!Number.isInteger(f.size) || f.size < 0) throw new Error(`invalid size: ${f.id}`);
    if (!/^[0-9a-f]{64}$/.test(f.sha256)) throw new Error(`missing/invalid sha256: ${f.id}`);
    if (!f.destination || f.destination.startsWith("/") || f.destination.includes("..")) {
      throw new Error(`invalid destination: ${f.id}`);
    }
  }
}

/**
 * @param {object} cfg
 * @param {string} cfg.baseUrl       Termux server URL, e.g. http://192.168.1.2:8787
 * @param {string} cfg.token         Bearer token shared out of band
 * @param {object} cfg.manifest      Manifest validated by the operator
 * @param {string[]} cfg.allowedPrefixes e.g. ["/mnt/usb0/RESEARCH/"]
 * @param {number} [cfg.chunkSize]   <= 1 MiB
 * @param {function(string,number,number): Promise<Uint8Array>} cfg.readChunk
 */
export async function collect(cfg, onProgress = () => {}) {
  const chunkSize = Math.min(cfg.chunkSize || 256 * 1024, MAX_CHUNK);
  validateManifest(cfg.manifest, cfg.allowedPrefixes || []);
  if (typeof cfg.readChunk !== "function") throw new Error("readChunk adapter required");
  const headers = { Authorization: `Bearer ${cfg.token}` };
  const base = cfg.baseUrl.replace(/\/$/, "");
  const statusRes = await request(`${base}/v1/status`, { headers });
  const status = await statusRes.json();

  for (const entry of cfg.manifest.files) {
    let offset = Number(status[entry.id]?.last_offset || 0);
    if (status[entry.id]?.state === "complete") { onProgress(entry.id, entry.size, entry.size); continue; }
    offset = Math.max(0, Math.min(offset, entry.size));
    while (offset < entry.size) {
      const length = Math.min(chunkSize, entry.size - offset);
      const bytes = await cfg.readChunk(entry.source, offset, length);
      if (!(bytes instanceof Uint8Array) || bytes.byteLength !== length) {
        throw new Error(`short read for ${entry.id} at ${offset}`);
      }
      const digest = await sha256Hex(bytes);
      await request(`${base}/v1/chunk?id=${encodeURIComponent(entry.id)}&offset=${offset}&length=${length}`, {
        method: "PUT", headers: { ...headers, "Content-Type": "application/octet-stream", "X-Chunk-SHA256": digest }, body: bytes
      });
      offset += length;
      onProgress(entry.id, offset, entry.size);
    }
    await request(`${base}/v1/finalize?id=${encodeURIComponent(entry.id)}`, { method: "POST", headers });
  }
  return { ok: true, files: cfg.manifest.files.map((f) => f.id) };
}
