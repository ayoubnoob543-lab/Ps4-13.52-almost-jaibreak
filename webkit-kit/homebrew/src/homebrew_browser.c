#include "homebrew_browser.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
#include <time.h>

struct hb_browser {
    char *root;
    unsigned timer_ms;
    atomic_uint ticks;
    atomic_int stop_timer;
    pthread_t timer_thread;
    int timer_started;
    void *arena;
    size_t memory_bytes;
    char status[256];
};

static void sleep_ms(unsigned milliseconds) {
    struct timespec request;
    request.tv_sec = (time_t)(milliseconds / 1000U);
    request.tv_nsec = (long)(milliseconds % 1000U) * 1000000L;
    while (nanosleep(&request, &request) != 0 && errno == EINTR) {
    }
}

static void *timer_main(void *opaque) {
    hb_browser *browser = (hb_browser *)opaque;
    while (!atomic_load(&browser->stop_timer)) {
        sleep_ms(browser->timer_ms);
        if (!atomic_load(&browser->stop_timer)) {
            (void)atomic_fetch_add(&browser->ticks, 1U);
        }
    }
    return NULL;
}

int hb_browser_create(hb_browser **out, const hb_browser_config *config) {
    hb_browser *browser;
    const char *root;
    unsigned timer_ms;
    size_t memory_bytes;

    if (out == NULL || config == NULL) {
        return -1;
    }
    root = config->filesystem_root == NULL ? "." : config->filesystem_root;
    timer_ms = config->timer_ms == 0 ? 1U : config->timer_ms;
    memory_bytes = config->memory_bytes == 0 ? 4096U : config->memory_bytes;
    browser = (hb_browser *)calloc(1, sizeof(*browser));
    if (browser == NULL) {
        return -1;
    }
    browser->root = (char *)malloc(strlen(root) + 1U);
    browser->arena = calloc(1, memory_bytes);
    if (browser->root == NULL || browser->arena == NULL) {
        free(browser->root);
        free(browser->arena);
        free(browser);
        return -1;
    }
    strcpy(browser->root, root);
    browser->timer_ms = timer_ms;
    browser->memory_bytes = memory_bytes;
    {
        struct stat root_stat;
        const int filesystem_ok = stat(browser->root, &root_stat) == 0;
        snprintf(browser->status, sizeof(browser->status),
            "created root=%s memory=%zu filesystem=%s webkit=unavailable",
            browser->root, browser->memory_bytes,
            filesystem_ok ? "available" : "missing");
    }
    *out = browser;
    return 0;
}

int hb_browser_run(hb_browser *browser, unsigned iterations) {
    unsigned i;
    if (browser == NULL || iterations == 0) {
        return -1;
    }
    (void)i;
    atomic_store(&browser->ticks, 0U);
    atomic_store(&browser->stop_timer, 0);
    if (pthread_create(&browser->timer_thread, NULL, timer_main, browser) != 0) {
        return -1;
    }
    browser->timer_started = 1;
    while (atomic_load(&browser->ticks) < iterations) {
        /* Minimal event-loop pump. No network, graphics, or privileged calls. */
        sched_yield();
    }
    atomic_store(&browser->stop_timer, 1);
    (void)pthread_join(browser->timer_thread, NULL);
    browser->timer_started = 0;
    snprintf(browser->status, sizeof(browser->status),
        "running ticks=%u root=%s memory=%zu filesystem=checked webkit=unavailable graphics=stub thread=joined",
        atomic_load(&browser->ticks), browser->root, browser->memory_bytes);
    return 0;
}

const char *hb_browser_status(const hb_browser *browser) {
    return browser == NULL ? "invalid" : browser->status;
}

void hb_browser_destroy(hb_browser *browser) {
    if (browser != NULL) {
        if (browser->timer_started) {
            atomic_store(&browser->stop_timer, 1);
            (void)pthread_join(browser->timer_thread, NULL);
        }
        free(browser->root);
        free(browser->arena);
        free(browser);
    }
}
