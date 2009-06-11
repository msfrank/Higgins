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
from time import gmtime, strftime
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from higgins.platform import netif
from higgins.upnp.logger import logger

SSDP_MULTICAST_GROUP = '239.255.255.250'

class Advertisement(object):
    def __init__(self, usn, nt, udn):
        self.usn = usn
        self.nt = nt
        self.udn = udn
        self.delayed = None

class SSDPFactory(DatagramProtocol):

    def __init__(self, iface):
        self.interface = iface
        self.devices = {}
        self.advertisements = {}
        self.expires = 180

    def _sendAlive(self, usn, nt, udn):
        if not usn in self.advertisements:
            logger.log_warning("no registered advertisement for %s" % usn)
            return
        adv = self.advertisements[usn]
        resp = [
            'NOTIFY * HTTP/1.1',
            'HOST: 239.255.255.250:1900',
            'NTS: ssdp:alive',
            'NT: %s' % nt,
            'USN: %s' % usn,
            'LOCATION: http://%s:%d/%s' % (self.interface.address, 1900, udn.replace(':','_')),
            'CACHE-CONTROL: max-age=%d' % self.expires,
            'SERVER: Twisted, UPnP/1.0, Higgins'
            ]
        self.transport.write('\r\n'.join(resp) + '\r\n\r\n', (SSDP_MULTICAST_GROUP, 1900))
        logger.log_debug("sent ssdp:alive for %s on %s" % (usn, self.interface.address))
        adv.delayed = reactor.callLater(self.expires, self._sendAlive, usn, nt, udn)

    def _startAdvertising(self, usn, nt, udn):
        adv = Advertisement(usn, nt, udn)
        self.advertisements[usn] = adv
        reactor.callLater(1, self._sendByebye, usn, nt)
        adv.delayed = reactor.callLater(2, self._sendAlive, usn, nt, udn)
        logger.log_debug("registered advertisement for %s" % usn)

    def registerDevice(self, device):
        if device.UDN in self.devices:
            raise Exception("%s is already a registered device" % device)
        # advertise the device
        self._startAdvertising("uuid:%s::upnp:rootdevice" % device.UDN,
                               "upnp:rootdevice",
                               device.UDN)
        self._startAdvertising("uuid:%s" % device.UDN,
                               "uuid:%s" % device.UDN,
                               device.UDN)
        self._startAdvertising("uuid:%s::%s" % (device.UDN, device.deviceType),
                               device.deviceType,
                               device.UDN)
        # advertise each service on the device
        for svc in device._services.values():
            self._startAdvertising("uuid:%s::%s" % (device.UDN, svc.serviceType),
                                   svc.serviceType,
                                   device.UDN)
        self.devices[device.UDN] = device
        logger.log_debug("registered device %s" % device.UDN)

    def _sendByebye(self, usn, nt):
        resp = [
            'NOTIFY * HTTP/1.1',
            'HOST: 239.255.255.250:1900',
            'NTS: ssdp:byebye',
            'NT: %s' % nt,
            'USN: %s' % usn
            ]
        self.transport.write('\r\n'.join(resp) + '\r\n\r\n', (SSDP_MULTICAST_GROUP, 1900))
        logger.log_debug("sent ssdp:byebye for %s on %s" % (usn, self.interface.address))

    def _stopAdvertising(self, usn):
        try:
            adv = self.advertisements[usn]
        except:
            raise Exception("USN %s is not being advertised" % usn)
        del self.advertisements[usn]
        adv.delayed.cancel()
        self._sendByebye(adv.usn, adv.nt)

    def unregisterDevice(self, device):
        if not device.UDN in self.devices:
            raise Exception("%s is not a registered device" % device)
        # advertise the device
        self._stopAdvertising("uuid:%s::upnp:rootdevice" % device.UDN)
        self._stopAdvertising("uuid:%s" % device.UDN)
        self._stopAdvertising("uuid:%s::%s" % (device.UDN, device.deviceType))
        # advertise each service on the device
        for svc in device._services.values():
            self._stopAdvertising("uuid:%s::%s" % (device.UDN, svc.serviceType))
        logger.log_debug("unregistered device %s" % device.UDN)
        del self.devices[device.UDN]

    def datagramReceived(self, data, (host, port)):
        try:
            try:
                header, payload = data.split('\r\n\r\n')
            except:
                header = data
            lines = header.split('\r\n')
            cmd,uri,unused = lines[0].split(' ', 3)
            lines = map(lambda x: x.replace(': ', ':', 1), lines[1:])
            lines = filter(lambda x: len(x) > 0, lines)
            headers = [x.split(':', 1) for x in lines]
            headers = dict(map(lambda x: (x[0].upper(), x[1]), headers))
            if cmd == 'M-SEARCH' and uri == '*':
                self.discoveryRequest(headers, (host, port))
        except Exception, e:
            logger.log_debug("discarding malformed datagram from %s: %s" % (host,e))

    def discoveryRequest(self, headers, (host, port)):
        def makeResponse(st, usn, location):
            resp = [
                'HTTP/1.1 200 OK',
                'DATE: %s' % strftime('%a, %d %B 20%y %H:%M:%S GMT', gmtime()),
                'EXT: ',
                'LOCATION: %s' % location,
                'SERVER: Twisted, UPnP/1.0, Higgins',
                'ST: %s' % st,
                'USN: %s' % usn,
                'CACHE-CONTROL: max-age=%d' % self.expires
                ]
            return '\r\n'.join(resp) + '\r\n'
        # if the MAN header is present, make sure its ssdp:discover
        if not headers.get('MAN', '') == '"ssdp:discover"':
            logger.log_warning("MAN header for discovery request is not 'ssdp:discover', ignoring")
            return
        logger.log_debug('received discovery request from %s:%d for %s' % (host, port, headers['ST']))
        # Generate a response
        iface = self.interface.address
        responses = []
        # return all devices and services
        if headers['ST'] == 'ssdp:all':
            for udn,device in self.devices.items():
                # advertise the device
                responses.append(makeResponse("upnp:rootdevice",
                                 "uuid:%s::upnp:rootdevice" % udn,
                                 "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
                responses.append(makeResponse("uuid:%s" % udn,
                                 "uuid:%s" % udn,
                                 "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
                responses.append(makeResponse(device.deviceType,
                                 "uuid:%s::%s" % (udn, device.deviceType),
                                 "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
                # advertise each service on the device
                for svc in device._services.values():
                    responses.append(makeResponse(svc.serviceType,
                                     "uuid:%s::%s" % (udn, svc.serviceType),
                                     "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
        # return each root device
        elif headers['ST'] == 'upnp:rootdevice':
            for udn,device in self.devices.items():
                # advertise the root device
                responses.append(makeResponse("upnp:rootdevice",
                                 "uuid:%s::upnp:rootdevice" % udn,
                                 "http://%s:1901/%s" % (iface,udn.replace(':','_'))))
        # return the specific device
        elif headers['ST'].startswith('uuid:'): 
            logger.log_warning("ignoring M-SEARCH for %s" % headers['ST'])
        # return device type
        elif headers['ST'].startswith('urn:schemas-upnp-org:device:'):
            logger.log_warning("ignoring M-SEARCH for %s" % headers['ST'])
        # return service type
        elif headers['ST'].startswith('urn:schemas-upnp-org:service:'):
            logger.log_warning("ignoring M-SEARCH for %s" % headers['ST'])
        # introduce a random delay between 0 and MX
        delayMax = int(headers['MX'])
        # send the responses
        if len(responses) > 0:
            logger.log_debug("sending %i responses" % len(responses))
            self._sendResponses(host, port, responses, delayMax)
        else:
            logger.log_warning("no responses generated for ssdp request")

    def sendAllByebyes(self):
        """
        We call this as the last step to server shutdown, to make sure any devices
        which were not unregistered get their byebyes sent.
        """
        for udn,device in self.devices.items():
            self.unregisterDevice(device)

    def _sendResponses(self, host, port, responses, delayMax):
        self.transport.write(responses.pop(0) + '\r\n', (host,port))
        logger.log_debug("wrote ssdp response to %s:%i" % (host,port))
        if len(responses) > 0:
            reactor.callLater(random.randint(0, delayMax),
                              self._sendResponses,
                              host,
                              port,
                              responses,
                              delayMax)

class SSDPServer(object):
    def __init__(self, interfaces=None):
        self.interfaces = {}
        detected = {}
        for i in [i for i in netif.list_interfaces().values() if i.can_multicast]:
            detected[i.address] = i
        if interfaces == None:
            self.interfaces = detected
        else:
            for addr in interfaces:
                if addr in detected:
                    self.interfaces[addr] = detected[addr]

    def start(self):
        self.servers = []
        for addr,iface in self.interfaces.items():
            protocol = SSDPFactory(iface)
            #listener = reactor.listenMulticast(1900, protocol, addr, listenMultiple=True)
            listener = reactor.listenMulticast(1900, protocol, listenMultiple=True)
            listener.joinGroup('239.255.255.250', addr)
            listener.setOutgoingInterface(addr)
            listener.setTTL(1)
            listener.setLoopbackMode(0)
            self.servers.append((addr,protocol,listener))
            logger.log_debug("SSDP Server listening on %s:1900" % addr)

    def stop(self):
        for addr,protocol,listener in self.servers:
            protocol.sendAllByebyes()
            listener.stopListening()
            logger.log_debug("SSDP server stopped listening on %s:1900" % addr)

    def registerDevice(self, device):
        for addr,protocol,listener in self.servers:
            protocol.registerDevice(device)

    def unregisterDevice(self, device):
        for addr,protocol,listener in self.servers:
            protocol.unregisterDevice(device)

__all__ = ['SSDPServer',]
