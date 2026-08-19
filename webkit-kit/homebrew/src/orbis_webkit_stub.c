#include "orbis_webkit_stub.h"

#include <stdio.h>
#include <string.h>

static const char k_report[] =
    "profile=host-safe\n"
    "oss_engine=external-or-host-harness\n"
    "network=disabled\n"
    "filesystem=process-local-only\n"
    "graphics=unavailable\n"
    "sony_retail_modules=missing\n"
    "orbis_sdk=sysroot-required\n";

int wk_runtime_init(wk_runtime *runtime) {
    if (runtime == NULL) {
        return -1;
    }
    memset(runtime, 0, sizeof(*runtime));
    runtime->info.platform_name = "portable-host";
    runtime->info.runtime_profile = "host-safe";
    runtime->info.filesystem_available = 0;
    runtime->info.graphics_available = 0;
    runtime->info.javascript_available = 1;
    return 0;
}

void wk_runtime_shutdown(wk_runtime *runtime) {
    if (runtime != NULL) {
        memset(runtime, 0, sizeof(*runtime));
    }
}

const char *wk_runtime_capability_report(const wk_runtime *runtime) {
    (void)runtime;
    return k_report;
}

int wk_runtime_run_safe_smoke(wk_runtime *runtime, char *out, size_t out_size) {
    int written;
    if (runtime == NULL || out == NULL || out_size == 0 ||
        !runtime->info.javascript_available) {
        return -1;
    }
    written = snprintf(out, out_size,
        "{\"harness\":\"homebrew-safe-stub\","
        "\"platform\":\"%s\","
        "\"javascript\":true,"
        "\"network\":false,"
        "\"graphics\":false,"
        "\"sony_modules\":false}",
        runtime->info.platform_name);
    if (written < 0 || (size_t)written >= out_size) {
        return -1;
    }
    return 0;
}
