/* shim_ioctl.c — implementación host de la interfaz mock /dev/pup_update0 */
#define _GNU_SOURCE
#include "host_compat.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

static int mock_fd = -1;
static void send_all(int fd, const void *b, size_t n) {
    while (n) { ssize_t w = write(fd,b,n); if (w<=0) _exit(9);
                b=(const char*)b+w; n-=(size_t)w; }
}
static void read_all(int fd, void *b, size_t n) {
    while (n) { ssize_t r = read(fd,b,n); if (r<=0) _exit(8);
                b=(char*)b+r; n-=(size_t)r; }
}

int mock_open_dev(void) {
    const char *path = getenv("PUP_MOCK_SOCK");
    if (!path) path = "/tmp/pupmock.sock";
    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    struct sockaddr_un a; memset(&a,0,sizeof a);
    a.sun_family = AF_UNIX;
    strncpy(a.sun_path, path, sizeof(a.sun_path)-1);
    struct timeval tv={5,0};
    setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&tv,sizeof tv);
    if (connect(fd,(struct sockaddr*)&a,sizeof a) < 0) {
        fprintf(stderr,"[mock] ERROR: no hay mock en %s\n", path);
        return -1;
    }
    mock_fd = fd;
    fprintf(stderr,"[mock] SHIM-v2 conectado (fd=%d)\n",fd);
    return 1000 + fd;
}

int mock_ioctl(int fd, unsigned long req, void *arg) {
    if (!(fd >= 1000)) { errno = EBADF; return -1; }
    req &= 0xFFFFFFFFul;   /* el número viaja como int con signo; el kernel usa los 32 bits bajos */
    unsigned char args[64]; size_t alen=0, plen=0; char *payload=NULL;
    const char *name="?";
    switch(req){
    case PUP_IOC_DECRYPT_HDR:      name="DECRYPT_HDR"; alen=24;
        plen=*(size_t*)((char*)arg+8); payload=*(char**)arg; break;
    case PUP_IOC_VERIFY_SEG_ADD:   name="VERIFY_SEG_ADD"; alen=24;
        plen=*(size_t*)((char*)arg+16); payload=*(char**)((char*)arg+8); break;
    case PUP_IOC_VERIFY_SEG:       name="VERIFY_SEG"; alen=24;
        plen=*(size_t*)((char*)arg+16); payload=*(char**)((char*)arg+8); break;
    case PUP_IOC_DECRYPT_SEG:      name="DECRYPT_SEG"; alen=24;
        plen=*(size_t*)((char*)arg+16); payload=*(char**)((char*)arg+8); break;
    case PUP_IOC_DECRYPT_SEG_BLK:  name="DECRYPT_SEG_BLK"; alen=40;
        plen=*(size_t*)((char*)arg+24); payload=*(char**)((char*)arg+16); break;
    default: name="UNKNOWN"; break;
    }
    memset(args,0,sizeof args); memcpy(args,arg,alen);
    size_t capped = plen > (1u<<20) ? (1u<<20) : plen;

    fprintf(stderr,"[mock->] ioctl %-16s req=0x%08lX args_len=%zu payload_len=%zu\n",
            name,req,alen,plen); fflush(stderr);

    unsigned hdr[5] = { 0x504D434Bu, (unsigned)req,
                        (unsigned)alen, (unsigned)capped, 0 };
    int sfd = fd - 1000;
    send_all(sfd,hdr,sizeof hdr);
    send_all(sfd,args,alen);
    if (capped && payload) send_all(sfd,payload,capped);

    unsigned rh[2]; 
    ssize_t rr;
    do { rr = read(sfd,rh,8);
    } while (rr < 0 && errno == EINTR);
    if (rr <= 0) {
        fprintf(stderr,"[shim] sin respuesta del mock (r=%zd errno=%d)\n",rr,errno);
        return -1;
    }
    unsigned out_len = rh[1] > (unsigned)plen ? (unsigned)plen : rh[1];
    if (out_len && payload) {
        static unsigned char tmp[16<<20];
        read_all(sfd,tmp,out_len);
        memcpy(payload,tmp,out_len);
        fprintf(stderr,"[mock<-] rv=%d out_len=%u head=%02x%02x%02x%02x\n",
                rh[0],out_len,tmp[0],tmp[1],tmp[2],tmp[3]);
    } else {
        fprintf(stderr,"[mock<-] rv=%d sin buffer de salida\n",rh[0]);
    }
    return (int)rh[0];
}
