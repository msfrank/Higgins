# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

cdef extern from "netif-internal.h":
    ctypedef struct netif:
        char *name
        char *address
        int is_up
    netif *__list_interfaces (int *nifs)
    void __free_interface_list (netif *ifs, int nifs)

def list_interfaces():
    cdef netif *ifs, curr
    cdef int nifs
    interfaces = {}
    ifs = __list_interfaces (&nifs)
    for i in range(nifs):
        curr = ifs[i]
        interfaces[curr.name] = (curr.address, curr.is_up)
    __free_interface_list (ifs, nifs)
    return interfaces
