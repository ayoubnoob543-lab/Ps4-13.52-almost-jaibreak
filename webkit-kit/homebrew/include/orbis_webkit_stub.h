#ifndef ORBIS_WEBKIT_STUB_H
#define ORBIS_WEBKIT_STUB_H

/*
 * Safe OSS/homebrew boundary.
 *
 * This header intentionally does not declare Sony module names, retail SDK
 * symbols, offsets, gadgets, exploit primitives, or payload entry points.
 * It exposes only a small host-testable contract for a future platform port.
 */

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct wk_platform_info {
    const char *platform_name;
    const char *runtime_profile;
    int filesystem_available;
    int graphics_available;
    int javascript_available;
} wk_platform_info;

typedef struct wk_runtime {
    wk_platform_info info;
    void *opaque;
} wk_runtime;

/* Available on the host prototype; platform ports must provide equivalents. */
int wk_runtime_init(wk_runtime *runtime);
void wk_runtime_shutdown(wk_runtime *runtime);
const char *wk_runtime_capability_report(const wk_runtime *runtime);
int wk_runtime_run_safe_smoke(wk_runtime *runtime, char *out, size_t out_size);

/*
 * MISSING platform contract, deliberately not implemented here:
 * - target process/event-loop integration
 * - filesystem and sandbox policy
 * - graphics/compositor backend
 * - threads, timers, allocator and memory-pressure hooks
 * - networking and certificate store
 * - JIT/W^X policy and executable-memory allocation
 * - target ABI/sysroot and application packaging
 */

#ifdef __cplusplus
}
#endif

#endif
