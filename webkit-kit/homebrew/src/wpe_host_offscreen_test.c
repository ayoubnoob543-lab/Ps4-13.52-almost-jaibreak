#include "wpe_host_offscreen.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct State { int task; int input; int frame; uint64_t frame_id; size_t width, height; };
static void task(void *p) { ((struct State *)p)->task++; }
static void input(const WPEHostInputEvent *e, void *p) { if (e->type == WPE_HOST_INPUT_POINTER_DOWN && e->x == 7) ((struct State *)p)->input++; }
static void frame(const uint8_t *rgba, size_t stride, size_t w, size_t h, uint64_t id, void *p) { struct State *s=p; assert(rgba && stride == w*4 && w == 8 && h == 6); s->frame++; s->frame_id=id; s->width=w; s->height=h; }
int main(void) {
    struct State state = {0};
    WPEHostLoop *loop = wpe_host_loop_new(); assert(loop);
    assert(wpe_host_loop_post(loop, task, &state) == 0); assert(wpe_host_loop_pending(loop) == 1); assert(wpe_host_loop_run_once(loop) == 1); assert(state.task == 1); assert(wpe_host_loop_run_once(loop) == 0); wpe_host_loop_free(loop);

    WPEHostView *view = wpe_host_view_new(8, 6); assert(view);
    WPEHostSurface *surface = wpe_host_view_surface(view); assert(surface); assert(wpe_host_surface_width(surface)==8 && wpe_host_surface_height(surface)==6);
    wpe_host_surface_clear(surface, 0x00000000u); uint64_t zero = wpe_host_surface_checksum(surface); assert(wpe_host_surface_fill_rect(surface, 2, 1, 3, 2, 0x11223344u)==0); assert(wpe_host_surface_checksum(surface) != zero);
    assert(wpe_host_view_set_input_callback(view, input, &state)==0); assert(wpe_host_view_set_frame_callback(view, frame, &state)==0);
    WPEHostInputEvent event = {WPE_HOST_INPUT_POINTER_DOWN, 7, 3, 0}; assert(wpe_host_view_queue_input(view, &event)==0); assert(wpe_host_view_request_frame(view)==0); assert(wpe_host_view_dispatch(view) == 2); assert(state.input==1 && state.frame==1 && state.frame_id==1);
    assert(wpe_host_surface_resize(surface, 4, 4)==0); assert(wpe_host_surface_width(surface)==4 && wpe_host_surface_height(surface)==4); wpe_host_view_free(view);

    char root[256]; snprintf(root, sizeof(root), "/tmp/wpe-host-storage-test-%ld", (long)getpid()); WPEHostStorage *storage = wpe_host_storage_open(root); assert(storage); assert(wpe_host_storage_put(storage, "answer", "42")==0); char *value=wpe_host_storage_get(storage,"answer"); assert(value && strcmp(value,"42")==0); free(value); assert(wpe_host_storage_get(storage,"../unsafe")==NULL); wpe_host_storage_close(storage); remove("/tmp/wpe-host-storage-test-unused");
    printf("offscreen-core: PASS\nloop: PASS\nsurface: PASS\nframe-callback: PASS\ninput-queue: PASS\nstorage: PASS\nrenderer: SOFTWARE_SURFACE_ONLY\nwpe-runtime: NOT_RUN\n"); return 0;
}
