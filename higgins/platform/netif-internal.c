/*
 * Higgins - A multi-media server
 * Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
 *
 * This program is free software; for license information see
 * the COPYING file.
 */

#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "netif-internal.h"

netif *
__netif_list_interfaces(int *nifs)
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
    /* FIXME: should check whether our supplied buffer was big enough */
    if(ioctl(s, SIOCGIFCONF, &ifc) < 0)
        return NULL;

    ifr = ifc.ifc_req;
    *nifs = ifc.ifc_len / sizeof(struct ifreq);
    ifs = calloc (*nifs, sizeof(netif));
    for(i = 0; i < *nifs; i++) {
        struct ifreq item = ifr[i];
        /* interface name */
        ifs[i].name = strdup (item.ifr_name);
        /* address */
        ifs[i].address = strdup (inet_ntoa(((struct sockaddr_in *)&item.ifr_addr)->sin_addr));
        /* netmask */
        item = ifr[i];
        ioctl (s, SIOCGIFNETMASK, &item);
        ifs[i].netmask = strdup (inet_ntoa(((struct sockaddr_in *)&item.ifr_netmask)->sin_addr));
        /* flags */
        item = ifr[i];
        ioctl (s, SIOCGIFFLAGS, &item);
        if (item.ifr_flags & IFF_UP)
            ifs[i].is_up = 1;
        else
            ifs[i].is_up = 0;
        if (item.ifr_flags & IFF_LOOPBACK)
            ifs[i].is_loopback = 1;
        else
            ifs[i].is_loopback = 0;
        if (item.ifr_flags & IFF_BROADCAST)
            ifs[i].can_broadcast = 1;
        else
            ifs[i].can_broadcast = 0;
        if (item.ifr_flags & IFF_MULTICAST)
            ifs[i].can_multicast = 1;
        else
            ifs[i].can_multicast = 0;
    }
    return ifs;
}

void
__netif_free_interface_list(netif *ifs, int nifs)
{
    int i;

    for (i = 0; i < nifs; i++) {
        free (ifs[i].name);
        free (ifs[i].address);
        free (ifs[i].netmask);
    }
    free (ifs);
}

int
__netif_shares_subnet (char *address, char *netmask, char *dest)
{
    struct in_addr src_addr, src_mask, dst_addr;

    if (inet_pton (AF_INET, address, &src_addr) <= 0)
        return -1;
    if (inet_pton (AF_INET, netmask, &src_mask) <= 0)
        return -1;
    if (inet_pton (AF_INET, dest, &dst_addr) <= 0)
        return -1;
    if ((src_addr.s_addr & src_mask.s_addr) == (dst_addr.s_addr & src_mask.s_addr))
        return 1;
    return 0;
}
