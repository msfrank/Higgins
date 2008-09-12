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
