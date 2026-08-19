#ifndef OSS_WEBKIT_BRIDGE_H
#define OSS_WEBKIT_BRIDGE_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * This bridge is intentionally a capability boundary, not an embedded WebKit
 * implementation. A future build may point WEBKIT_SOURCE_DIR at a verified
 * OSS tree and add an explicit port adapter. No retail ABI is inferred.
 */
const char *oss_webkit_bridge_status(void);
int oss_webkit_bridge_available(void);

#ifdef __cplusplus
}
#endif

#endif
