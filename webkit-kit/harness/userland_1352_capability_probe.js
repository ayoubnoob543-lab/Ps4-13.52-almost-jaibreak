/*
 * PS4 13.52 userland capability probe.
 *
 * This file is intentionally non-exploitative: it does not trigger memory
 * corruption, use-after-free conditions, JIT spraying, ROP, native calls,
 * sandbox escape, or kernel access. It only reports standard JavaScript
 * capabilities available in the host/runtime where it is loaded.
 */
(function () {
  "use strict";

  function has(name, value) {
    return { name: name, available: Boolean(value) };
  }

  var report = {
    profile: "ps4-13.52-userland-probe",
    safe_only: true,
    exploit_attempted: false,
    native_calls_attempted: false,
    capabilities: [
      has("BigInt", typeof BigInt === "function"),
      has("ArrayBuffer", typeof ArrayBuffer === "function"),
      has("SharedArrayBuffer", typeof SharedArrayBuffer === "function"),
      has("WebAssembly", typeof WebAssembly === "object"),
      has("Worker", typeof Worker === "function"),
      has("Promise", typeof Promise === "function"),
      has("Proxy", typeof Proxy === "function"),
      has("Atomics", typeof Atomics === "object"),
      has("TextEncoder", typeof TextEncoder === "function"),
      has("URL", typeof URL === "function")
    ]
  };

  if (typeof globalThis !== "undefined") {
    globalThis.__USERLAND_1352_PROBE__ = report;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = report;
  }

  if (typeof console !== "undefined" && typeof console.log === "function") {
    console.log(JSON.stringify(report));
  }
}());
