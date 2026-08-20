#include "wpe_host_offscreen.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

struct WPEHostLoopTask { WPEHostTask task; void *userdata; };
struct WPEHostLoop { struct WPEHostLoopTask *tasks; size_t count; size_t capacity; };
struct WPEHostSurface { size_t width, height, stride; uint8_t *pixels; };
struct WPEHostView {
    WPEHostSurface *surface;
    WPEHostFrameCallback frame_callback;
    void *frame_userdata;
    WPEHostInputCallback input_callback;
    void *input_userdata;
    WPEHostInputEvent *inputs;
    size_t input_count, input_capacity;
    uint64_t frame_id;
};
struct WPEHostStorage { char *root; };

static int checked_size(size_t width, size_t height, size_t *bytes) {
    if (!width || !height || width > SIZE_MAX / 4 || height > (SIZE_MAX / 4) / width) return 0;
    *bytes = width * height * 4;
    return 1;
}

WPEHostLoop *wpe_host_loop_new(void) { return calloc(1, sizeof(WPEHostLoop)); }
void wpe_host_loop_free(WPEHostLoop *loop) { if (loop) { free(loop->tasks); free(loop); } }
int wpe_host_loop_post(WPEHostLoop *loop, WPEHostTask task, void *userdata) {
    if (!loop || !task) return EINVAL;
    if (loop->count == loop->capacity) {
        size_t next = loop->capacity ? loop->capacity * 2 : 8;
        void *p = realloc(loop->tasks, next * sizeof(*loop->tasks));
        if (!p) return ENOMEM;
        loop->tasks = p; loop->capacity = next;
    }
    loop->tasks[loop->count++] = (struct WPEHostLoopTask){task, userdata};
    return 0;
}
int wpe_host_loop_run_once(WPEHostLoop *loop) {
    if (!loop || !loop->count) return 0;
    struct WPEHostLoopTask task = loop->tasks[0];
    memmove(loop->tasks, loop->tasks + 1, (loop->count - 1) * sizeof(*loop->tasks));
    --loop->count; task.task(task.userdata); return 1;
}
size_t wpe_host_loop_pending(const WPEHostLoop *loop) { return loop ? loop->count : 0; }

WPEHostSurface *wpe_host_surface_new(size_t width, size_t height) {
    WPEHostSurface *s = calloc(1, sizeof(*s)); size_t bytes;
    if (!s || !checked_size(width, height, &bytes)) { free(s); return NULL; }
    s->pixels = calloc(1, bytes); if (!s->pixels) { free(s); return NULL; }
    s->width = width; s->height = height; s->stride = width * 4; return s;
}
void wpe_host_surface_free(WPEHostSurface *surface) { if (surface) { free(surface->pixels); free(surface); } }
int wpe_host_surface_resize(WPEHostSurface *s, size_t width, size_t height) {
    size_t bytes; if (!s || !checked_size(width, height, &bytes)) return EINVAL;
    uint8_t *p = calloc(1, bytes); if (!p) return ENOMEM;
    size_t copy_w = width < s->width ? width : s->width, copy_h = height < s->height ? height : s->height;
    for (size_t y = 0; y < copy_h; ++y) memcpy(p + y * width * 4, s->pixels + y * s->stride, copy_w * 4);
    free(s->pixels); s->pixels = p; s->width = width; s->height = height; s->stride = width * 4; return 0;
}
void wpe_host_surface_clear(WPEHostSurface *s, uint32_t rgba) { if (!s) return; for (size_t y=0;y<s->height;++y) for (size_t x=0;x<s->width;++x) memcpy(s->pixels+y*s->stride+x*4,&rgba,4); }
int wpe_host_surface_fill_rect(WPEHostSurface *s, size_t x, size_t y, size_t w, size_t h, uint32_t rgba) {
    if (!s || x > s->width || y > s->height) return EINVAL;
    size_t maxw = s->width-x, maxh=s->height-y; if (w>maxw) w=maxw; if (h>maxh) h=maxh;
    for (size_t row=0;row<h;++row) for (size_t col=0;col<w;++col) memcpy(s->pixels+(y+row)*s->stride+(x+col)*4,&rgba,4);
    return 0;
}
const uint8_t *wpe_host_surface_pixels(const WPEHostSurface *s) { return s ? s->pixels : NULL; }
size_t wpe_host_surface_width(const WPEHostSurface *s) { return s ? s->width : 0; }
size_t wpe_host_surface_height(const WPEHostSurface *s) { return s ? s->height : 0; }
size_t wpe_host_surface_stride(const WPEHostSurface *s) { return s ? s->stride : 0; }
uint64_t wpe_host_surface_checksum(const WPEHostSurface *s) { uint64_t h=1469598103934665603ULL; if (!s) return 0; for(size_t i=0;i<s->stride*s->height;++i){h^=s->pixels[i];h*=1099511628211ULL;} return h; }
int wpe_host_surface_write_ppm(const WPEHostSurface *s, const char *path) { if (!s || !path) return EINVAL; FILE *f=fopen(path,"wb"); if (!f) return errno; if (fprintf(f,"P6\\n%zu %zu\\n255\\n",s->width,s->height)<0) { fclose(f); return EIO; } for(size_t y=0;y<s->height;++y) for(size_t x=0;x<s->width;++x) { const uint8_t *p=s->pixels+y*s->stride+x*4; if (fwrite(p,1,3,f)!=3) { fclose(f); return EIO; } } if (fclose(f)!=0) return EIO; return 0; }

WPEHostView *wpe_host_view_new(size_t width, size_t height) { WPEHostView *v=calloc(1,sizeof(*v)); if(!v) return NULL; v->surface=wpe_host_surface_new(width,height); if(!v->surface){free(v);return NULL;} return v; }
void wpe_host_view_free(WPEHostView *v) { if(v){wpe_host_surface_free(v->surface);free(v->inputs);free(v);} }
WPEHostSurface *wpe_host_view_surface(WPEHostView *v) { return v?v->surface:NULL; }
int wpe_host_view_set_frame_callback(WPEHostView *v,WPEHostFrameCallback cb,void *u){if(!v)return EINVAL;v->frame_callback=cb;v->frame_userdata=u;return 0;}
int wpe_host_view_set_input_callback(WPEHostView *v,WPEHostInputCallback cb,void *u){if(!v)return EINVAL;v->input_callback=cb;v->input_userdata=u;return 0;}
int wpe_host_view_queue_input(WPEHostView *v,const WPEHostInputEvent *e){if(!v||!e)return EINVAL;if(v->input_count==v->input_capacity){size_t n=v->input_capacity?v->input_capacity*2:8;void*p=realloc(v->inputs,n*sizeof(*v->inputs));if(!p)return ENOMEM;v->inputs=p;v->input_capacity=n;}v->inputs[v->input_count++]=*e;return 0;}
int wpe_host_view_request_frame(WPEHostView *v){if(!v)return EINVAL;v->frame_id++;return 0;}
int wpe_host_view_dispatch(WPEHostView *v){if(!v)return EINVAL;size_t n=0;while(n<v->input_count){if(v->input_callback)v->input_callback(&v->inputs[n],v->input_userdata);++n;}v->input_count=0;if(v->frame_callback&&v->frame_id){v->frame_callback(v->surface->pixels,v->surface->stride,v->surface->width,v->surface->height,v->frame_id,v->frame_userdata);v->frame_id=0;return (int)(n+1);}return (int)n;}
static void dispatch_view_task(void *userdata) { (void)wpe_host_view_dispatch((WPEHostView *)userdata); }
int wpe_host_view_schedule_on_loop(WPEHostView *v, WPEHostLoop *loop) { if (!v || !loop) return EINVAL; return wpe_host_loop_post(loop, dispatch_view_task, v); }
uint64_t wpe_host_view_frame_id(const WPEHostView *v){return v?v->frame_id:0;}

static int mkdir_if_missing(const char *path) { if (!path || !*path) return EINVAL; if (!mkdir(path, 0700) && errno != EEXIST) return errno; return 0; }
static char *duplicate_string(const char *text) { size_t n; char *copy; if (!text) return NULL; n = strlen(text) + 1; copy = malloc(n); if (copy) memcpy(copy, text, n); return copy; }
WPEHostStorage *wpe_host_storage_open(const char *root){if(!root)return NULL;WPEHostStorage*s=calloc(1,sizeof(*s));if(!s)return NULL;s->root=duplicate_string(root);if(!s->root||mkdir_if_missing(root)){free(s->root);free(s);return NULL;}return s;}
void wpe_host_storage_close(WPEHostStorage*s){if(s){free(s->root);free(s);}}
static int safe_key(const char *key){if(!key||!*key||strstr(key,"..")||strchr(key,'/')||strchr(key,'\\'))return 0;return 1;}
int wpe_host_storage_put(WPEHostStorage*s,const char*key,const char*value){if(!s||!safe_key(key)||!value)return EINVAL;size_t n=strlen(s->root)+strlen(key)+2;char*p=malloc(n);if(!p)return ENOMEM;snprintf(p,n,"%s/%s",s->root,key);FILE*f=fopen(p,"wb");free(p);if(!f)return errno;size_t len=strlen(value);int rc=fwrite(value,1,len,f)==len?0:EIO;fclose(f);return rc;}
char *wpe_host_storage_get(WPEHostStorage*s,const char*key){if(!s||!safe_key(key))return NULL;size_t n=strlen(s->root)+strlen(key)+2;char*p=malloc(n);if(!p)return NULL;snprintf(p,n,"%s/%s",s->root,key);FILE*f=fopen(p,"rb");free(p);if(!f)return NULL;if(fseek(f,0,SEEK_END)||ftell(f)<0){fclose(f);return NULL;}long len=ftell(f);rewind(f);char*out=malloc((size_t)len+1);if(!out){fclose(f);return NULL;}if(fread(out,1,(size_t)len,f)!=(size_t)len){free(out);fclose(f);return NULL;}out[len]=0;fclose(f);return out;}
