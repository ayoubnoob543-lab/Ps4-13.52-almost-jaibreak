#ifndef WPE_HOST_OFFSCREEN_H
#define WPE_HOST_OFFSCREEN_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct WPEHostSurface WPEHostSurface;
typedef struct WPEHostView WPEHostView;
typedef struct WPEHostLoop WPEHostLoop;
typedef struct WPEHostStorage WPEHostStorage;

typedef enum {
    WPE_HOST_INPUT_POINTER_DOWN = 1,
    WPE_HOST_INPUT_POINTER_UP = 2,
    WPE_HOST_INPUT_KEY_DOWN = 3,
    WPE_HOST_INPUT_KEY_UP = 4
} WPEHostInputType;

typedef struct {
    WPEHostInputType type;
    int32_t x;
    int32_t y;
    uint32_t code;
} WPEHostInputEvent;

typedef void (*WPEHostTask)(void *userdata);
typedef void (*WPEHostFrameCallback)(const uint8_t *rgba, size_t stride, size_t width, size_t height, uint64_t frame_id, void *userdata);
typedef void (*WPEHostInputCallback)(const WPEHostInputEvent *event, void *userdata);

/* Host/offscreen contract only. This is not libwpe and does not claim WPE runtime compatibility. */
WPEHostLoop *wpe_host_loop_new(void);
void wpe_host_loop_free(WPEHostLoop *loop);
int wpe_host_loop_post(WPEHostLoop *loop, WPEHostTask task, void *userdata);
int wpe_host_loop_run_once(WPEHostLoop *loop);
size_t wpe_host_loop_pending(const WPEHostLoop *loop);

WPEHostSurface *wpe_host_surface_new(size_t width, size_t height);
void wpe_host_surface_free(WPEHostSurface *surface);
int wpe_host_surface_resize(WPEHostSurface *surface, size_t width, size_t height);
void wpe_host_surface_clear(WPEHostSurface *surface, uint32_t rgba);
int wpe_host_surface_fill_rect(WPEHostSurface *surface, size_t x, size_t y, size_t width, size_t height, uint32_t rgba);
const uint8_t *wpe_host_surface_pixels(const WPEHostSurface *surface);
size_t wpe_host_surface_width(const WPEHostSurface *surface);
size_t wpe_host_surface_height(const WPEHostSurface *surface);
size_t wpe_host_surface_stride(const WPEHostSurface *surface);
uint64_t wpe_host_surface_checksum(const WPEHostSurface *surface);

WPEHostView *wpe_host_view_new(size_t width, size_t height);
void wpe_host_view_free(WPEHostView *view);
WPEHostSurface *wpe_host_view_surface(WPEHostView *view);
int wpe_host_view_set_frame_callback(WPEHostView *view, WPEHostFrameCallback callback, void *userdata);
int wpe_host_view_set_input_callback(WPEHostView *view, WPEHostInputCallback callback, void *userdata);
int wpe_host_view_queue_input(WPEHostView *view, const WPEHostInputEvent *event);
int wpe_host_view_request_frame(WPEHostView *view);
int wpe_host_view_dispatch(WPEHostView *view);
uint64_t wpe_host_view_frame_id(const WPEHostView *view);

WPEHostStorage *wpe_host_storage_open(const char *root);
void wpe_host_storage_close(WPEHostStorage *storage);
int wpe_host_storage_put(WPEHostStorage *storage, const char *key, const char *value);
char *wpe_host_storage_get(WPEHostStorage *storage, const char *key);

#ifdef __cplusplus
}
#endif
#endif
