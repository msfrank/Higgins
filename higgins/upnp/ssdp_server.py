# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.
#
# Portions of this code from the pymeds project  are licensed under
# the MIT license: http://opensource.org/licenses/mit-license.php
#
#   Copyright 2005, Tim Potter <tpot@samba.org>
#   Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random
import string
from higgins import netif
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from higgins.upnp.logger import UPnPLogger

class SSDPFactory(DatagramProtocol, UPnPLogger):

    def __init__(self, interfaces):
        self.interfaces = interfaces
        self.devices = {}

    def registerDevice(self, device):
        if device.upnp_UDN in self.devices:
            raise Exception("%s is already a registered device" % device)
        for iface in self.interfaces:
            # advertise the device
            self.sendAlive("upnp:rootdevice",
                           "uuid:%s::upnp:rootdevice" % device.upnp_UDN,
                           "http://%s:1901/%s" % (iface,device.upnp_UDN.replace(':','_')))
            self.sendAlive("uuid:%s" % device.upnp_UDN,
                           "uuid:%s" % device.upnp_UDN,
                           "http://%s:1901/%s" % (iface,device.upnp_UDN.replace(':','_')))
            self.sendAlive(device.upnp_device_type,
                           "uuid:%s::%s" % (device.upnp_UDN, device.upnp_device_type),
                           "http://%s:1901/%s" % (iface,device.upnp_UDN.replace(':','_')))
            # advertise each service on the device
            for svc in device._upnp_services.values():
                self.sendAlive(svc.upnp_service_type,
                               "uuid:%s::%s" % (device.upnp_UDN, svc.upnp_service_type),
                               "http://%s:1901/%s" % (iface,device.upnp_UDN.replace(':','_')))
            self.log_debug("registered device %s on %s" % (device.upnp_UDN, iface))
        self.devices[device.upnp_UDN] = device

    def unregisterDevice(self, device):
        if not device.upnp_UDN in self.devices:
            raise Exception("%s is not a registered device" % device)
        for iface in self.interfaces:
            # advertise the device
            self.sendByebye("upnp:rootdevice", "uuid:%s::upnp:rootdevice" % device.upnp_UDN)
            self.sendByebye("uuid:%s" % device.upnp_UDN, "uuid:%s" % device.upnp_UDN)
            self.sendByebye(device.upnp_device_type, "uuid:%s::%s" % (device.upnp_UDN, device.upnp_device_type))
            # advertise each service on the device
            for svc in device._upnp_services.values():
                self.sendByebye(svc.upnp_service_type, "uuid:%s::%s" % (device.upnp_UDN, svc.upnp_service_type))
            self.log_debug("unregistered device %s on %s" % (device.upnp_UDN, iface))
        del self.devices[device.upnp_UDN]

    def datagramReceived(self, data, (host, port)):
        try:
            try:
                header, payload = data.split('\r\n\r\n')
            except:
                header = data
            lines = header.split('\r\n')
            try:
                cmd,uri,unused = string.split(lines[0], ' ')
            except Exception, e:
                self.log_debug("failed to parse request line '%s'" % lines[0])
                raise e
            lines = map(lambda x: x.replace(': ', ':', 1), lines[1:])
            lines = filter(lambda x: len(x) > 0, lines)
            headers = [string.split(x, ':', 1) for x in lines]
            headers = dict(map(lambda x: (x[0].upper(), x[1]), headers))
            if cmd == 'M-SEARCH' and uri == '*':
                self.discoveryRequest(headers, (host, port))
        except:
            self.log_debug("discarding malformed datagram from %s" % host)

    def sendAlive(self, nt, usn, location, cacheControl=1800, server='Twisted, UPnP/1.0, Higgins'):
        for iface in self.interfaces:
            resp = [ 'NOTIFY * HTTP/1.1',
                'Host: %s:%d' % (iface, 1900),
                'NTS: ssdp:alive',
                'NT: %s' % nt,
                'USN: %s' % usn,
                'LOCATION: %s' % location,
                'CACHE-CONTROL: max-age=%d' % cacheControl,
                'SERVER: %s' % server
                ]
            self.transport.write('\r\n'.join(resp) + '\r\n\r\n', (iface, 1900))

    def sendByebye(self, nt, usn):
        for iface in self.interfaces:
            resp = [ 'NOTIFY * HTTP/1.1',
                'Host: %s:%d' % (iface, 1900),
                'NTS: ssdp:byebye',
                'NT: %s' % nt,
                'USN: %s' % usn
                ]
            self.transport.write('\r\n'.join(resp) + '\r\n\r\n', (iface, 1900))

    def discoveryRequest(self, headers, (host, port)):
        def makeResponse(st, usn, location, cacheControl=1800, server='Twisted, UPnP/1.0, Higgins'):
            resp = ['HTTP/1.1 200 OK',
                'EXT: ',
                'LOCATION: %s' % location,
                'SERVER: %s' % server,
                'ST: %s' % st,
                'USN: %s' % usn,
                'CACHE-CONTROL: max-age=%d' % cacheControl,
                ]
            return '\r\n'.join(resp) + '\r\n'
        # if the MAN header is present, make sure its ssdp:discover
        if not headers.get('MAN', '') == '"ssdp:discover"':
            self.log_warning("MAN header for discovery request is not 'ssdp:discover', ignoring")
            return
        self.log_debug('received discovery request from %s for %s' % (host, headers['ST']))
        # Generate a response
        responses = []
        # return all devices and services
        if headers['ST'] == 'ssdp:all':
            for udn,device in self.devices.items():
                for iface in self.interfaces:
                    # advertise the device
                    responses.append(makeResponse("upnp:rootdevice",
                                     "uuid:%s::upnp:rootdevice" % udn,
                                     "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
                    responses.append(makeResponse("uuid:%s" % udn,
                                     "uuid:%s" % udn,
                                     "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
                    responses.append(makeResponse(device.upnp_device_type,
                                     "uuid:%s::%s" % (udn, device.upnp_device_type),
                                     "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
                    # advertise each service on the device
                    for svc in device._upnp_services.values():
                        responses.append(makeResponse(svc.upnp_service_type,
                                         "uuid:%s::%s" % (udn, svc.upnp_service_type),
                                         "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
        # return each root device
        elif headers['ST'] == 'upnp:rootdevice':
            for udn,device in self.devices.items():
                for iface in self.interfaces:
                    # advertise the root device
                    responses.append(makeResponse("upnp:rootdevice",
                                     "uuid:%s::upnp:rootdevice" % udn,
                                     "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
        # return the specific device
        elif headers['ST'].startswith('uuid:'): 
            pass
        # return device type
        elif headers['ST'].startswith('urn:schemas-upnp-or:device:'):
            pass
        # return service type
        elif headers['ST'].startswith('urn:schemas-upnp-or:service:'):
            pass
        # introduce a random delay between 0 and MX
        delayMax = int(headers['MX'])
        # send the responses
        if len(responses) > 0:
            self.log_debug("sending %i responses" % len(responses))
            reactor.callLater(random.randint(0, delayMax),
                              self._doWriteResponse,
                              host,
                              port,
                              responses,
                              delayMax)
        else:
            self.log_warning("no responses generated for ssdp request")

    def _doWriteResponse(self, host, port, responses, delayMax):
        self.transport.write(responses.pop(0) + '\r\n', (host,port))
        self.log_debug("wrote ssdp response to %s:%i" % (host, port))
        if len(responses) > 0:
            reactor.callLater(random.randint(0, delayMax),
                              self._doWriteResponse,
                              host,
                              port,
                              responses,
                              delayMax)

    def sendAllByebyes(self):
        """
        We call this as the last step to server shutdown, to make sure any devices
        which were not unregistered get their byebyes sent.
        """
        for udn,device in self.devices.items():
            self.unregisterDevice(device)

class SSDPServer(UPnPLogger):
    def __init__(self, interfaces=None):
        if interfaces == None:
            self.interfaces = [addr for name,(addr,up) in netif.list_interfaces().items()]
        else:
            self.interfaces = interfaces

    def start(self):
        self.log_debug("SSDP Server listening on port 1900")
        self.server = SSDPFactory(self.interfaces)
        self.listener = reactor.listenMulticast(1900, self.server, listenMultiple=True)
        self.listener.joinGroup('239.255.255.250')
        self.listener.setLoopbackMode(0)

    def stop(self):
        self.server.sendAllByebyes()
        self.listener.stopListening()
        self.listener = None
        self.server = None
        self.log_debug("SSDP server stopped listening")

    def registerDevice(self, device):
        self.server.registerDevice(device)

    def unregisterDevice(self, device):
        self.server.unregisterDevice(device)

__all__ = ['SSDPServer',]
