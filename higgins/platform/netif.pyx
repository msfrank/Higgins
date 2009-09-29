# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

cdef extern from "netif-internal.h":
    ctypedef struct netif:
        char *name
        char *address
        char *netmask
        int is_up
        int is_loopback
        int can_broadcast
        int can_multicast
    netif *__netif_list_interfaces (int *nifs)
    void __netif_free_interface_list (netif *ifs, int nifs)
    int __netif_shares_subnet (char *address, char *netmask, char *dest)

class NetifException(Exception):
    pass

class Interface(object):
    def sharesSubnet(self, dest):
        cdef char *c_address
        cdef char *c_netmask
        cdef char *c_dest
        cdef int retval
        c_address = self.address
        c_netmask = self.netmask
        c_dest = dest
        retval = __netif_shares_subnet(c_address, c_netmask, c_dest)
        if retval > 0:
            return True
        if retval == 0:
            return False
        raise NetifException("Invalid destination address %s" % dest)
    def __str__(self):
        return "%s (%s/%s)" % (self.name,self.address,self.netmask)

def list_interfaces():
    cdef netif *ifs
    cdef int nifs
    interfaces = {}
    ifs = __netif_list_interfaces (&nifs)
    for i in range(nifs):
        iface = Interface()
        iface.name = ifs[i].name
        iface.address = ifs[i].address
        iface.netmask = ifs[i].netmask
        iface.is_up = ifs[i].is_up
        iface.is_loopback = ifs[i].is_loopback
        iface.can_broadcast = ifs[i].can_broadcast
        iface.can_multicast = ifs[i].can_multicast
        interfaces[iface.name] = iface
    __netif_free_interface_list (ifs, nifs)
    return interfaces

__all__ = ['Interface', 'list_interfaces']
