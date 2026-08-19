#include "homebrew_browser.h"
#include "orbis_webkit_stub.h"
#include "oss_webkit_bridge.h"

#include <stdio.h>

int main(void) {
    hb_browser *browser = NULL;
    hb_browser_config config = {
        .filesystem_root = ".",
        .timer_ms = 1,
        .memory_bytes = 4096,
    };
    wk_runtime runtime;

    if (wk_runtime_init(&runtime) != 0 ||
        hb_browser_create(&browser, &config) != 0) {
        fputs("minimal browser initialization failed\n", stderr);
        wk_runtime_shutdown(&runtime);
        return 1;
    }
    if (hb_browser_run(browser, 3) != 0) {
        fputs("minimal browser event loop failed\n", stderr);
        hb_browser_destroy(browser);
        wk_runtime_shutdown(&runtime);
        return 1;
    }
    puts("homebrew-minimal-browser");
    puts(hb_browser_status(browser));
    puts(oss_webkit_bridge_status());
    puts(wk_runtime_capability_report(&runtime));
    hb_browser_destroy(browser);
    wk_runtime_shutdown(&runtime);
    return 0;
}
