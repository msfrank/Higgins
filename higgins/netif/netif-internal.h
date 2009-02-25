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
    int is_up;
} netif;

netif *__list_interfaces(int *nifs);
void __free_interface_list(netif *ifs, int nifs);

#endif
