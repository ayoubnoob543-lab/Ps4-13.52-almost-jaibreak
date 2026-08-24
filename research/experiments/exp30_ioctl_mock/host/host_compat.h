#ifndef HOST_COMPAT_H
#define HOST_COMPAT_H
#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>

extern int sock;
#define printfsocket(...) \
    do { fprintf(stderr, "[payload] " __VA_ARGS__); fflush(stderr); } while (0)

/* interfaz mock de /dev/pup_update0 — implementación en shim_ioctl.c */
int mock_open_dev(void);
int mock_ioctl(int fd, unsigned long req, void *arg);
#define CHECK_SIZE(x, y) _Static_assert(sizeof(x) == y, #x)
#define PUP_IOC_DECRYPT_HDR      0xC0184401u
#define PUP_IOC_VERIFY_SEG_ADD   0xC0184402u
#define PUP_IOC_VERIFY_SEG       0xC0184403u
#define PUP_IOC_DECRYPT_SEG      0xC0184404u
#define PUP_IOC_DECRYPT_SEG_BLK  0xC0284405u
#endif
