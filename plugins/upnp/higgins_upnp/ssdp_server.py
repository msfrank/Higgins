# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2005, Tim Potter <tpot@samba.org>
# Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random
import string
import netif
from twisted.python import log
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from logger import UPnPLogger

class SSDPServer(DatagramProtocol, UPnPLogger):

    def __init__(self, interfaces):
        self.known = {}
        self.interfaces = interfaces

    def doStop(self):
        '''Make sure we send out the byebye notifications.'''
        for st in self.known:
            self.doByebye(st)
        DatagramProtocol.doStop(self)

    def datagramReceived(self, data, (host, port)):
        """Handle a received multicast datagram."""
        header, payload = data.split('\r\n\r\n')
        lines = header.split('\r\n')
        cmd = string.split(lines[0], ' ')
        lines = map(lambda x: x.replace(': ', ':', 1), lines[1:])
        lines = filter(lambda x: len(x) > 0, lines)
        headers = [string.split(x, ':', 1) for x in lines]
        headers = dict(map(lambda x: (x[0].lower(), x[1]), headers))
        if cmd[0] == 'M-SEARCH' and cmd[1] == '*':
            self.discoveryRequest(headers, (host, port))
        elif cmd[0] == 'NOTIFY' and cmd[1] == '*':
            pass
        else:
            self.log_debug('Ignoring unknown SSDP command %s' % cmd)

    def discoveryRequest(self, headers, (host, port)):
        """Process a discovery request.  The response must be sent to
        the address specified by (host, port)."""
        self.log_debug('SSDP discovery request for %s' % headers['st'])
        # Do we know about this service?
        if headers['st'] == 'ssdp:all':
            for i in self.known:
                hcopy = dict(headers.iteritems())
                hcopy['st'] = i
                self.discoveryRequest(hcopy, (host, port))
            return
        if not self.known.has_key(headers['st']):
            return
        # Generate a response
        response = []
        response.append('HTTP/1.1 200 OK')
        for k, v in self.known[headers['st']].items():
            response.append('%s: %s' % (k, v))
        response.extend(('', ''))
        delay = random.randint(0, int(headers['mx']))
        reactor.callLater(delay, self.transport.write, '\r\n'.join(response), (host, port))

    def register(self, usn, st, location):
        """Register a service or device that this SSDP server will
        respond to."""
        self.log_debug('Registering service %s' % st)
        self.known[st] = {}
        self.known[st]['USN'] = usn
        self.known[st]['LOCATION'] = location
        self.known[st]['ST'] = st
        self.known[st]['EXT'] = ''
        self.known[st]['SERVER'] = 'Twisted, UPnP/1.0, python-upnp'
        self.known[st]['CACHE-CONTROL'] = 'max-age=1800'
        self.doNotify(st)

    def doByebye(self, st):
        """Do byebye"""
        self.log_debug('Unregistering service %s' % st)
        for iface in self.interfaces:
            resp = [ 'NOTIFY * HTTP/1.1',
                'Host: %s:%d' % (iface, 1900),
                'NTS: ssdp:byebye',
                ]
            stcpy = dict(self.known[st].iteritems())
            stcpy['NT'] = stcpy['ST']
            del stcpy['ST']
            resp.extend(map(lambda x: ': '.join(x), stcpy.iteritems()))
            resp.extend(('', ''))
            self.transport.write('\r\n'.join(resp), (iface, 1900))

    def doNotify(self, st):
        """Do notification"""
        self.log_debug('Sending alive notification for %s' % st)
        for iface in self.interfaces:
            resp = [ 'NOTIFY * HTTP/1.1',
                'Host: %s:%d' % (iface, 1900),
                'NTS: ssdp:alive',
                ]
            stcpy = dict(self.known[st].iteritems())
            stcpy['NT'] = stcpy['ST']
            del stcpy['ST']
            resp.extend(map(lambda x: ': '.join(x), stcpy.iteritems()))
            resp.extend(('', ''))
            self.transport.write('\r\n'.join(resp), (iface, 1900))

class SSDPService(UPnPLogger):
    def __init__(self, interfaces=None):
        if interfaces == None:
            self.interfaces = [addr for name,(addr,up) in netif.list_interfaces().items()]
        else:
            self.interfaces = interfaces
        self.servers = {}

    def start(self):
        self.log_debug("SSDP Server listening on port 1900")
        self.server = SSDPServer(self.interfaces)
        self.listener = reactor.listenMulticast(1900, self.server, listenMultiple=True)
        self.listener.joinGroup('239.255.255.250')
        self.listener.setLoopbackMode(0)

    def stop(self):
        self.listener.stopListening()
        self.server = None

    def register(self, usn, st, location, interface=None):
        self.server.register(usn, st, location)

    def unregister(self):
        pass
