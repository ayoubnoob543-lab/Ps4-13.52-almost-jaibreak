// Safe, deterministic ECMAScript smoke test.
// No network, filesystem, exploit primitives, or platform-specific payloads.
(function () {
  const results = [];
  const check = (name, fn) => {
    try {
      const value = fn();
      results.push({ name, ok: Boolean(value), value: String(value) });
    } catch (error) {
      results.push({ name, ok: false, value: String(error) });
    }
  };

  check("array_map", () => [1, 2, 3].map((x) => x * 2).join(",") === "2,4,6");
  check("promise_microtask", () => typeof Promise === "function");
  check("typed_arrays", () => new Uint32Array([0x1352])[0] === 0x1352);
  check("unicode", () => "PS4\u00a013.52".normalize("NFC").includes("13.52"));
  check("json", () => JSON.parse(JSON.stringify({ target: "PS4", fw: "13.52" })).fw === "13.52");

  const report = {
    harness: "webkit-kit/basic-capabilities",
    safe: true,
    network: false,
    exploit_primitives: false,
    results,
  };
  if (typeof print === "function") print(JSON.stringify(report));
  else if (typeof console !== "undefined") console.log(JSON.stringify(report));
})();
