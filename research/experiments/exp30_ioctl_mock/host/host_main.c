/* host_main.c — sustituye main.c del payload (bootstrap PS4 → host Termux) */
#include <stdio.h>
int sock = -1;                 /* printfsocket ya no usa red */
void decrypt_pups(void);
int main(void) {
    decrypt_pups();
    fprintf(stderr,"[host] Bye!\n");
    return 0;
}
