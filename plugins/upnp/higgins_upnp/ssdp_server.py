# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2005, Tim Potter <tpot@samba.org>
# Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random
import string
from twisted.python import log
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

# TODO: Break out into a HTTPOverUDP class and implement
# process_SEARCH(), process_NOTIFY() methods.  Create UPNP specific
# class to handle services etc.

class SSDPServer(DatagramProtocol):
    """A class implementing a SSDP server.  The notifyReceived and
    searchReceived methods are called when the appropriate type of
    datagram is received by the server."""

    # not used yet
    stdheaders = [ ('Server', 'Twisted, UPnP/1.0, python-upnp'), ]
    elements = {}
    known = {}

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    def doStop(self):
        '''Make sure we send out the byebye notifications.'''

        for st in self.known:
            self.doByebye(st)
        DatagramProtocol.doStop(self)

    def datagramReceived(self, data, (host, port)):
        """Handle a received multicast datagram."""

        # Break up message in to command and headers
        # TODO: use the email module after trimming off the request line..
        # This gets us much better header support.

        header, payload = data.split('\r\n\r\n')
        lines = header.split('\r\n')
        cmd = string.split(lines[0], ' ')
        lines = map(lambda x: x.replace(': ', ':', 1), lines[1:])
        lines = filter(lambda x: len(x) > 0, lines)

        headers = [string.split(x, ':', 1) for x in lines]
        headers = dict(map(lambda x: (x[0].lower(), x[1]), headers))

        if cmd[0] == 'M-SEARCH' and cmd[1] == '*':
            # SSDP discovery
            self.discoveryRequest(headers, (host, port))
        elif cmd[0] == 'NOTIFY' and cmd[1] == '*':
            # SSDP presence
            self.notifyReceived(headers, (host, port))
        else:
            log.msg('Unknown SSDP command %s %s' % cmd)

    def discoveryRequest(self, headers, (host, port)):
        """Process a discovery request.  The response must be sent to
        the address specified by (host, port)."""

        log.msg('Discovery request for %s' % headers['st'])

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
        reactor.callLater(delay, self.transport.write,
            '\r\n'.join(response), (host, port))

    def register(self, usn, st, location):
        """Register a service or device that this SSDP server will
        respond to."""

        log.msg('Registering %s' % st)

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

        log.msg('Sending byebye notification for %s' % st)

        resp = [ 'NOTIFY * HTTP/1.1',
             'Host: %s:%d' % (self.addr, self.port),
             'NTS: ssdp:byebye',
            ]
        stcpy = dict(self.known[st].iteritems())
        stcpy['NT'] = stcpy['ST']
        del stcpy['ST']
        resp.extend(map(lambda x: ': '.join(x), stcpy.iteritems()))
        resp.extend(('', ''))
        self.transport.write('\r\n'.join(resp), (self.addr, self.port))

    def doNotify(self, st):
        """Do notification"""

        log.msg('Sending alive notification for %s' % st)

        resp = [ 'NOTIFY * HTTP/1.1',
            'Host: %s:%d' % (self.addr, self.port),
            'NTS: ssdp:alive',
            ]
        stcpy = dict(self.known[st].iteritems())
        stcpy['NT'] = stcpy['ST']
        del stcpy['ST']
        resp.extend(map(lambda x: ': '.join(x), stcpy.iteritems()))
        resp.extend(('', ''))
        self.transport.write('\r\n'.join(resp), (self.addr, self.port))

    def notifyReceived(self, headers, (host, port)):
        """Process a presence announcement.  We just remember the
        details of the SSDP service announced."""

        if headers['nts'] == 'ssdp:alive':
            if not self.elements.has_key(headers['nt']):
                # Register device/service
                self.elements[headers['nt']] = {}
                self.elements[headers['nt']]['USN'] = headers['usn']
                self.elements[headers['nt']]['host'] = (host, port)
                log.msg('Detected presence of %s' % headers['nt'])
        elif headers['nts'] == 'ssdp:byebye':
            if self.elements.has_key(headers['nt']):
                # Unregister device/service
                del(self.elements[headers['nt']])
                log.msg('Detected absence for %s' % headers['nt'])
        else:
            log.msg('Unknown subtype %s for notification type %s' %
                (headers['nts'], headers['nt']))

    def findService(self, name):
        """Return information about a service registered over SSDP."""

        # TODO: Implement me.

        # TODO: Send out a discovery request if we haven't registered
        # a presence announcement.

    def findDevice(self, name):
        """Return information about a device registered over SSDP."""

        # TODO: Implement me.

        # TODO: Send out a discovery request if we haven't registered
        # a presence announcement.
