/*
 * Higgins - A multi-media server
 * Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
 *
 * This program is free software; for license information see
 * the COPYING file.
 */

#ifndef NETIF_INTERNAL_H
#define NETIF_INTERNAL_H

typedef struct {
    char *name;
    char *address;
    char *netmask;
    int is_up;
    int is_loopback;
    int can_broadcast;
    int can_multicast;
} netif;

netif *__netif_list_interfaces(int *nifs);
void __netif_free_interface_list(netif *ifs, int nifs);
int __netif_shares_subnet (char *address, char *netmask, char *dest);

#endif
