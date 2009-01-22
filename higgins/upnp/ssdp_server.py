# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2005, Tim Potter <tpot@samba.org>
# Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random
import string
import netif
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from logger import UpnpLogger

class SSDPServer(DatagramProtocol, UpnpLogger):

    def __init__(self, interfaces):
        self.interfaces = interfaces
        self.devices = {}

    def registerDevice(self, device):
        if device.upnp_UDN in self.devices:
            raise UpnpRuntimeException("%s is already a registered device" % device)
        for iface in self.interfaces:
            # advertise the device
            self.sendAlive("upnp:rootdevice",
                           "uuid:%s::upnp:rootdevice" % device.upnp_UDN,
                           "http://%s:31338/%s/root-device.xml" % (iface,device.upnp_UDN))
            self.sendAlive("uuid:%s" % device.upnp_UDN,
                           "uuid:%s" % device.upnp_UDN,
                           "http://%s:31338/%s/root-device.xml" % (iface,device.upnp_UDN))
            self.sendAlive(device.upnp_device_type,
                           "uuid:%s::%s" % (device.upnp_UDN, device.upnp_device_type),
                           "http://%s:31338/%s/root-device.xml" % (iface,device.upnp_UDN))
            # advertise each service on the device
            for svc in device.upnp_services:
                self.sendAlive(svc.upnp_service_type,
                               "uuid:%s::%s" % (device.upnp_UDN, svc.upnp_service_type),
                               "http://%s:31338/%s/root-device.xml" % (iface,device.upnp_UDN))
        self.devices[device.upnp_UDN] = device
        self.log_debug('registered device %s' % device.upnp_UDN)

    def unregisterDevice(self, device):
        if not device.upnp_UDN in self.devices:
            raise UpnpRuntimeException("%s is not a registered device" % device)
        for iface in self.interfaces:
            # advertise the device
            self.sendByebye("upnp:rootdevice", "uuid:%s::upnp:rootdevice" % device.upnp_UDN)
            self.sendByebye("uuid:%s" % device.upnp_UDN, "uuid:%s" % device.upnp_UDN)
            self.sendByebye(device.upnp_device_type, "uuid:%s::%s" % (device.upnp_UDN, device.upnp_device_type))
            # advertise each service on the device
            for svc in device.upnp_services:
                self.sendByebye(svc.upnp_service_type, "uuid:%s::%s" % (device.upnp_UDN, svc.upnp_service_type))
        del self.devices[device.upnp_UDN]
        self.log_debug('unregistered device %s' % device.upnp_UDN)

    def datagramReceived(self, data, (host, port)):
        header, payload = data.split('\r\n\r\n')
        lines = header.split('\r\n')
        cmd,uri,unused = string.split(lines[0], ' ')
        lines = map(lambda x: x.replace(': ', ':', 1), lines[1:])
        lines = filter(lambda x: len(x) > 0, lines)
        headers = [string.split(x, ':', 1) for x in lines]
        #headers = dict(map(lambda x: (x[0].lower(), x[1]), headers))
        if cmd == 'M-SEARCH' and uri == '*':
            self.discoveryRequest(headers, (host, port))

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
            self.transport.write('\r\n'.join(resp) + '\r\n', (iface, 1900))

    def sendByebye(self, nt, usn):
        for iface in self.interfaces:
            resp = [ 'NOTIFY * HTTP/1.1',
                'Host: %s:%d' % (iface, 1900),
                'NTS: ssdp:byebye',
                'NT: %s' % nt,
                'USN: %s' % usn
                ]
            self.transport.write('\r\n'.join(resp) + '\r\n', (iface, 1900))

    def discoveryRequest(self, headers, (host, port)):
        def makeResponse(st, usn, location, cacheControl=1800, server='Twisted, UPnP/1.0, Higgins'):
            resp = ['HTTP/1.1 200 OK',
                'CACHE-CONTROL: max-age=%d' % cacheControl,
                'EXT: ',
                'LOCATION: %s' % location,
                'SERVER: %s' % server,
                'ST: %s' % st,
                'USN: %s' % usn
                ]
            return '\r\n'.join(response) + '\r\n'
        # check for ssdp:discover, as required by the upnp spec
        if not headers['MAN'] == '"ssdp:discover"':
            return
        self.log_debug('received discovery request for %s' % headers['ST'])
        # Generate a response
        responses = []
        # return all devices and services
        if headers['ST'] == 'ssdp:all':
            for udn,device in self.devices.items():
                # advertise the device
                response.append(makeResponse("upnp:rootdevice",
                                "uuid:%s::upnp:rootdevice" % udn,
                                "http://%s:31338/%s/root-device.xml" % (iface,udn)))
                response.append(makeResponse("uuid:%s" % udn,
                                "uuid:%s" % udn,
                                "http://%s:31338/%s/root-device.xml" % (iface,udn)))
                response.append(makeResponse(device.upnp_device_type,
                                "uuid:%s::%s" % (udn, device.upnp_device_type),
                                "http://%s:31338/%s/root-device.xml" % (iface,udn)))
                # advertise each service on the device
                for svc in device.upnp_services:
                    response.append(makeResponse(svc.upnp_service_type,
                                    "uuid:%s::%s" % (udn, svc.upnp_service_type),
                                    "http://%s:31338/%s/root-device.xml" % (iface,udn)))
        # return each root device
        if headers['ST'] == 'upnp:rootdevice':
            pass
        # return the specific device
        if headers['ST'].startswith('uuid:'): 
            pass
        # return device type
        if headers['ST'].startswith('urn:schemas-upnp-or:device:'):
            pass
        # return service type
        if headers['ST'].startswith('urn:schemas-upnp-or:service:'):
            pass
        # introduce a random delay between 0 and MX
        delay = random.randint(0, int(headers['MX']))
        # send the responses
        reactor.callLater(delay, self.transport.write, ''.join(responses), (host, port))

    def doStop(self):
        for udn,device in self.devices.items():
            self.unregisterDevice(device)
        DatagramProtocol.doStop(self)

class SSDPService(UpnpLogger):
    def __init__(self, interfaces=None):
        if interfaces == None:
            self.interfaces = [addr for name,(addr,up) in netif.list_interfaces().items()]
        else:
            self.interfaces = interfaces

    def start(self):
        self.log_debug("SSDP Server listening on port 1900")
        self.server = SSDPServer(self.interfaces)
        self.listener = reactor.listenMulticast(1900, self.server, listenMultiple=True)
        self.listener.joinGroup('239.255.255.250')
        self.listener.setLoopbackMode(0)

    def stop(self):
        self.listener.stopListening()
        self.server = None

    def registerDevice(self, device):
        self.server.registerDevice(device)

    def unregisterDevice(self, device):
        self.server.unregisterDevice(device)
