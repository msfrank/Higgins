# Contains portions of code from pymeds:
#   Licensed under the MIT license
#   http://opensource.org/licenses/mit-license.php
#   Copyright 2005, Tim Potter <tpot@samba.org>
#   Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random, string
from twisted.application.service import Service
from twisted.internet import reactor
from twisted.web import server as http
from media_server import MediaServer
from ssdp_server import SSDPServer
from higgins.logging import log_error, log_debug
from higgins.conf import conf
import netif

class UpnpService(Service):
    def __init__(self):
        self.name = "UPnP"
        self.description = "Exposes the Higgins media store as a UPnP share"
        # initialize config options
        ifs = netif.list_interfaces()
        self.ms_addr = None
        self.ms_port = 31338
        for ifname,ifdata in ifs.items():
            if not ifname == "127.0.0.1":
                self.ms_addr = ifdata[0]
        if self.ms_addr == None:
            log_error("UPnP failed to find any running network interfaces")
            raise Exception
        if conf.get("UPNP_SHARE_NAME") == None:
            conf.set(UPNP_SHARE_NAME="Higgins UPnP Share on %s" % self.ms_addr)
        self.ssdp_addr = conf.get('UPNP_MULTICAST_ADDRESS', '239.255.255.250')
        self.ssdp_port = conf.get('UPNP_MULTICAST_PORT', 1900)

    def startService(self):
        Service.startService(self)
        # set UPnP configuration
        self.urlbase = 'http://%s:%d/' % (self.ms_addr, self.ms_port)
        self.devicename = conf.get("UPNP_SHARE_NAME")
        self.uuid = ''.join([ 'uuid:'] + map(lambda x: random.choice(string.letters), xrange(20)))
        # first start the MediaServer
        site = http.Site(MediaServer(self.urlbase, self.devicename, self.uuid))
        self.ms_listener = reactor.listenTCP(self.ms_port, site)
        log_debug("MediaServer listening on %s:%d" % (self.ms_addr,self.ms_port))
        # next start the SSDPServer, since it depends on the MediaServer running
        self.ssdp = SSDPServer(self.ssdp_addr, self.ssdp_port)
        self.ssdp_listener = reactor.listenMulticast(self.ssdp_port, self.ssdp)
        self.ssdp_listener.joinGroup(self.ssdp_addr)
        self.ssdp_listener.setLoopbackMode(0)       # don't get our own sends
        # register available services
        self.ssdp.register('%s::upnp:rootdevice' % self.uuid,
                           'upnp:rootdevice',
                           self.urlbase + 'root-device.xml')
        self.ssdp.register(self.uuid,
                           self.uuid,
                           self.urlbase + 'root-device.xml')
        self.ssdp.register('%s::urn:schemas-upnp-org:device:MediaServer:1' % self.uuid,
                           'urn:schemas-upnp-org:device:MediaServer:1',
                           self.urlbase + 'root-device.xml')
        self.ssdp.register('%s::urn:schemas-upnp-org:service:ConnectionManager:1' % self.uuid,
                           'urn:schemas-upnp-org:device:ConnectionManager:1',
                           self.urlbase + 'root-device.xml')
        self.ssdp.register('%s::urn:schemas-upnp-org:service:ContentDirectory:1' % self.uuid,
                           'urn:schemas-upnp-org:device:ContentDirectory:1',
                           self.urlbase + 'root-device.xml')
        log_debug ("started UPnP service")

    def stopService(self):
        d = self.ssdp_listener.stopListening()
        if d:
            log_debug("SSDPServer couldn't immediately stop listening, deferring")
        d = self.ms_listener.stopListening()
        if d:
            log_debug("MediaServer couldn't immediately stop listening, deferring")
        Service.stopService(self)
        log_debug("stopped UPnP service")
        return None

from django import newforms as forms

class UpnpConfig(forms.Form):
    UPNP_SHARE_NAME = forms.CharField(label="UPnP Share Name")
