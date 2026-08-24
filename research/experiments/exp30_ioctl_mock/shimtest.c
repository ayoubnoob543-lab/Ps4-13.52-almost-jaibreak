#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
int mock_open_dev(void){
    const char *path=getenv("PUP_MOCK_SOCK");
    int fd=socket(AF_UNIX,SOCK_STREAM,0);
    struct sockaddr_un a; memset(&a,0,sizeof a); a.sun_family=AF_UNIX;
    strncpy(a.sun_path,path,sizeof(a.sun_path)-1);
    struct timeval tv={5,0}; setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&tv,sizeof tv);
    if(connect(fd,(struct sockaddr*)&a,sizeof a)<0){perror("connect");return -1;}
    return 1000+fd;
}
int mock_ioctl(int fd,unsigned long req,void*arg){
    int s=fd-1000;
    unsigned h[5]={0x504D434Bu,(unsigned)req,24,16,0};
    char buf[16]; memset(buf,'A',16);
    unsigned char a[24]; memset(a,0,24); *(size_t*)(a+8)=16;
    write(s,h,20); write(s,a,24); write(s,buf,16);
    fprintf(stderr,"[t] enviado, esperando respuesta...\n"); fflush(stderr);
    unsigned rh[2]; ssize_t r=read(s,rh,8);
    fprintf(stderr,"[t] leído=%zd rv=%u out=%u\n",r,(r==8?rh[0]:9999),(r==8?rh[1]:0)); fflush(stderr);
    if(r==8 && rh[1]){ char bb[16]; ssize_t r2=read(s,bb,rh[1]); fprintf(stderr,"[t] payload=%zd\n",r2);}
    return 0;
}
int main(void){ return mock_ioctl(mock_open_dev(),0xC0184404,0); }
