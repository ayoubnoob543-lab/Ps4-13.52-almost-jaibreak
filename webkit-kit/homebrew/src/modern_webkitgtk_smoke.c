#include <gtk/gtk.h>
#include <webkit2/webkit2.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static GMainLoop *loop;
static WebKitWebView *view;
static int failed;
static int stage;

static void finish_with_error(const char *message)
{
    fprintf(stderr, "modern-webkit-smoke: %s\n", message);
    failed = 1;
    if (loop)
        g_main_loop_quit(loop);
}

static void evaluate_result(GObject *source, GAsyncResult *result, gpointer user_data)
{
    (void)source;
    const char *expected = user_data;
    GError *error = NULL;
    JSCValue *value = webkit_web_view_evaluate_javascript_finish(view, result, &error);
    if (!value) {
        if (error) {
            fprintf(stderr, "modern-webkit-smoke: javascript evaluation failed: %s\n", error->message);
            g_error_free(error);
        }
        finish_with_error("JavaScript evaluation returned no result");
        return;
    }

    char *text = jsc_value_to_string(value);
    printf("stage=%d result=%s\n", stage, text ? text : "<null>");
    if (!text || strcmp(text, expected) != 0) {
        finish_with_error("unexpected WebKit capability result");
        g_free(text);
        return;
    }
    g_free(text);

    if (!failed && stage == 1)
        webkit_web_view_load_uri(view, "file:///tmp/webkit-kit-modern-smoke/page2.html");
    else if (!failed && stage == 2)
        webkit_web_view_load_uri(view, "file:///tmp/webkit-kit-modern-smoke/page3.html");
    else if (!failed)
        g_main_loop_quit(loop);
}

static void evaluate(WebKitWebView *web_view, const char *script, const char *expected)
{
    webkit_web_view_evaluate_javascript(web_view, script, -1, NULL, NULL, NULL, evaluate_result, (gpointer)expected);
}

static void load_changed(WebKitWebView *web_view, WebKitLoadEvent event, gpointer user_data)
{
    (void)user_data;
    if (event != WEBKIT_LOAD_FINISHED)
        return;

    stage++;
    if (stage == 1) {
        const char *script =
            "(() => {"
            "const button=document.getElementById('action'); button.click();"
            "const box=document.getElementById('box'); const flex=getComputedStyle(document.getElementById('flex')).display;"
            "const grid=getComputedStyle(document.getElementById('grid')).display;"
            "const animation=getComputedStyle(box).animationName;"
            "const form=document.getElementById('form'); const input=document.getElementById('name');"
            "input.value='Ada'; const formOK=form.checkValidity();"
            "const svg=document.querySelector('svg'); const image=document.getElementById('image');"
            "const canvas=document.getElementById('canvas'); const ctx=canvas.getContext('2d'); ctx.fillStyle='#f00'; ctx.fillRect(0,0,8,8);"
            "let storage=false; try { localStorage.setItem('webkitSmoke','ok'); storage=localStorage.getItem('webkitSmoke')==='ok'; } catch(e) {}"
            "return JSON.stringify({dom:document.querySelectorAll('section article').length===2,event:button.dataset.clicked==='yes',text:box.textContent,flex:flex==='flex',grid:grid==='grid',animation:animation==='pulse',form:formOK,svg:!!svg,image:image.complete,canvas:canvas.toDataURL().length>30,storage:storage});"
            "})()";
        evaluate(web_view, script, "{\"dom\":true,\"event\":true,\"text\":\"clicked\",\"flex\":true,\"grid\":true,\"animation\":true,\"form\":true,\"svg\":true,\"image\":true,\"canvas\":true,\"storage\":true}");
        return;
    }

    if (stage == 2) {
        const char *script =
            "JSON.stringify({page:location.pathname.endsWith('page2.html'),storage:localStorage.getItem('webkitSmoke')==='ok',"
            "dom:document.getElementById('destination').textContent,js:window.page2Ready===true,event:document.getElementById('nav').dispatchEvent(new Event('custom'))});";
        evaluate(web_view, script, "{\"page\":true,\"storage\":true,\"dom\":\"page2-ok\",\"js\":true,\"event\":true}");
        return;
    }

    if (stage == 3) {
        const char *script =
            "JSON.stringify({page:location.pathname.endsWith('page3.html'),history:history.length>=1,dom:document.body.dataset.final==='yes',js:window.page3Ready===true});";
        evaluate(web_view, script, "{\"page\":true,\"history\":true,\"dom\":true,\"js\":true}");
        return;
    }

    finish_with_error("unexpected navigation stage");
}

int main(int argc, char **argv)
{
    (void)argv;
    gtk_init(&argc, &argv);
    loop = g_main_loop_new(NULL, FALSE);
    view = WEBKIT_WEB_VIEW(g_object_ref_sink(webkit_web_view_new()));
    g_signal_connect(view, "load-changed", G_CALLBACK(load_changed), NULL);
    webkit_web_view_load_uri(view, "file:///tmp/webkit-kit-modern-smoke/page1.html");
    g_main_loop_run(loop);
    g_object_unref(view);
    g_main_loop_unref(loop);
    return failed ? EXIT_FAILURE : EXIT_SUCCESS;
}
