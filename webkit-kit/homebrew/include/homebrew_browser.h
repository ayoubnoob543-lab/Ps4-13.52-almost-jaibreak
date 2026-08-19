#ifndef HOMEBREW_BROWSER_H
#define HOMEBREW_BROWSER_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct hb_browser hb_browser;

typedef struct hb_browser_config {
    const char *filesystem_root;
    unsigned timer_ms;
    size_t memory_bytes;
} hb_browser_config;

int hb_browser_create(hb_browser **out, const hb_browser_config *config);
int hb_browser_run(hb_browser *browser, unsigned iterations);
const char *hb_browser_status(const hb_browser *browser);
void hb_browser_destroy(hb_browser *browser);

#ifdef __cplusplus
}
#endif

#endif
