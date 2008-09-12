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
