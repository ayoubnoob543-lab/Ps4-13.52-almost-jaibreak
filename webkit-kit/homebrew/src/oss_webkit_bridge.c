#include "oss_webkit_bridge.h"

#include <stdlib.h>

const char *oss_webkit_bridge_status(void) {
    const char *source = getenv("WEBKIT_SOURCE_DIR");
    return (source != NULL && source[0] != '\0')
        ? "oss-source-configured-port-adapter-required"
        : "oss-source-not-configured";
}

int oss_webkit_bridge_available(void) {
    const char *source = getenv("WEBKIT_SOURCE_DIR");
    /* A path alone never proves that the engine is built or target-compatible. */
    return source != NULL && source[0] != '\0' ? 0 : 0;
}
