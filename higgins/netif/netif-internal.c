#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *name;
    char *address;
    int is_up;
} netif;

netif *
__list_interfaces(int *nifs)
{
    char buf[1024];
    struct ifconf ifc;
    struct ifreq *ifr;
    int s, i;
    netif *ifs = NULL;

    s = socket(AF_INET, SOCK_DGRAM, 0);
    if(s < 0)
        return NULL;
    ifc.ifc_len = sizeof(buf);
    ifc.ifc_buf = buf;
    if(ioctl(s, SIOCGIFCONF, &ifc) < 0)
        return NULL;

    ifr = ifc.ifc_req;
    *nifs = ifc.ifc_len / sizeof(struct ifreq);
    ifs = calloc (*nifs, sizeof(netif));
    for(i = 0; i < *nifs; i++) {
        struct ifreq *item = &ifr[i];
        ifs[i].name = strdup (item->ifr_name);
        ifs[i].address = strdup (inet_ntoa(((struct sockaddr_in *)&item->ifr_addr)->sin_addr));
        if (item->ifr_flags & IFF_UP)
            ifs[i].is_up = 1;
        else
            ifs[i].is_up = 0;
    }
    return ifs;
}

void
__free_interface_list(netif *ifs, int nifs)
{
    int i;

    for (i = 0; i < nifs; i++) {
        free (ifs[i].name);
        free (ifs[i].address);
    }
    free (ifs);
}
