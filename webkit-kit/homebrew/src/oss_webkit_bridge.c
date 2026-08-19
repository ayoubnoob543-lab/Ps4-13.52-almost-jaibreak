#include "oss_webkit_bridge.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef HOMEBREW_HAVE_JSC
#include <jsc/jsc.h>
#endif

const char *oss_webkit_bridge_status(void) {
    const char *source = getenv("WEBKIT_SOURCE_DIR");
#ifdef HOMEBREW_HAVE_JSC
    if (source != NULL && source[0] != '\0') {
        return "jsc-host-available-oss-source-configured-port-adapter-required";
    }
    return "jsc-host-available-oss-source-not-configured";
#else
    (void)source;
    return "jsc-host-unavailable";
#endif
}

int oss_webkit_bridge_available(void) {
#ifdef HOMEBREW_HAVE_JSC
    return 1;
#else
    return 0;
#endif
}

int oss_webkit_bridge_run_smoke(char *output, unsigned output_size) {
#ifdef HOMEBREW_HAVE_JSC
    JSCContext *context;
    JSCValue *value;
    gchar *text;
    gboolean passed;
    int written;

    if (output == NULL || output_size == 0) {
        return -1;
    }
    context = jsc_context_new();
    value = jsc_context_evaluate(context,
        "(() => { const xs = [1,2,3].map(x => x * 2); "
        "return xs.join(',') === '2,4,6' && "
        "new Uint32Array([0x1352])[0] === 0x1352 && "
        "JSON.parse('{\\\"fw\\\":\\\"13.52\\\"}').fw === '13.52'; })()",
        -1);
    passed = jsc_value_to_boolean(value);
    text = jsc_value_to_string(value);
    written = snprintf(output, output_size,
        "{\"engine\":\"JavaScriptCore-GTK-host\",\"passed\":%s,\"value\":\"%s\"}",
        passed ? "true" : "false", text == NULL ? "" : text);
    g_free(text);
    g_object_unref(value);
    g_object_unref(context);
    if (written < 0 || (unsigned)written >= output_size) {
        return -1;
    }
    return passed ? 0 : 1;
#else
    (void)output;
    (void)output_size;
    return -2;
#endif
}
