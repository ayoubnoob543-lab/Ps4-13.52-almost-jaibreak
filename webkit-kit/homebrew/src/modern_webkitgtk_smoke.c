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
    if (!text || strcmp(text, expected) != 0)
        finish_with_error("unexpected JavaScript/DOM/CSS result");
    g_free(text);
    if (!failed && stage == 1)
        webkit_web_view_load_uri(view, "file:///tmp/webkit-kit-modern-smoke/page2.html");
    else if (!failed)
        g_main_loop_quit(loop);
}

static void load_changed(WebKitWebView *web_view, WebKitLoadEvent event, gpointer user_data)
{
    (void)web_view;
    (void)user_data;
    if (event != WEBKIT_LOAD_FINISHED)
        return;

    stage++;
    if (stage == 1) {
        const char *script =
            "(() => {"
            "const b=document.getElementById('action');"
            "b.click();"
            "const box=document.getElementById('box');"
            "const s=getComputedStyle(box);"
            "return [document.body.dataset.domReady, b.dataset.clicked, box.textContent, s.width, s.height].join('|');"
            "})()";
        webkit_web_view_evaluate_javascript(view, script, -1, NULL, NULL, NULL, evaluate_result, "yes|yes|clicked|120px|40px");
        return;
    }

    if (stage == 2) {
        const char *script =
            "JSON.stringify({url:location.pathname.endsWith('page2.html'),"
            "dom:document.getElementById('destination').textContent,"
            "js:window.page2Ready === true})";
        webkit_web_view_evaluate_javascript(view, script, -1, NULL, NULL, NULL, evaluate_result,
            "{\"url\":true,\"dom\":\"navigation-ok\",\"js\":true}");
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
