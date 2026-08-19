#include "orbis_webkit_stub.h"

#include <stdio.h>

int main(void) {
    wk_runtime runtime;
    char result[256];

    if (wk_runtime_init(&runtime) != 0) {
        fputs("runtime_init failed\n", stderr);
        return 1;
    }
    fputs(wk_runtime_capability_report(&runtime), stdout);
    if (wk_runtime_run_safe_smoke(&runtime, result, sizeof(result)) != 0) {
        fputs("safe smoke failed\n", stderr);
        wk_runtime_shutdown(&runtime);
        return 1;
    }
    puts(result);
    wk_runtime_shutdown(&runtime);
    return 0;
}
