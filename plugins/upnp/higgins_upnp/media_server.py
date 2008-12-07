# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2005, Tim Potter <tpot@samba.org>
# Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import netif
from twisted.web2 import channel, resource, static
from twisted.web2.http import Response as HttpResponse
from twisted.web2.stream import FileStream
from twisted.web2.server import Site
from twisted.web2.http_headers import MimeType
from twisted.internet import reactor
from connection_manager import ConnectionManager
from content_directory import ContentDirectory
from higgins.core.models import Song
from higgins.conf import conf
from higgins.logging import log_debug, log_error

class RootDevice(static.Data):
    def __init__(self, urlbase, devicename, uuid):
        self.urlbase = urlbase
        self.devicename = devicename
        self.uuid = uuid
        static.Data.__init__(self, """
<root xmlns="urn:schemas-upnp-org:device-1-0">
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
    <URLBase>%s</URLBase>
    <device>
        <deviceType>urn:schemas-upnp-org:device:MediaServer:1</deviceType>
        <friendlyName>%s</friendlyName>
        <manufacturer>SYNTAXJOCKEY</manufacturer>
        <manufacturerURL>http://www.syntaxjockey.com</manufacturerURL>
        <modelDescription>UPnP/AV Media Server</modelDescription>
        <modelName>Higgins UPnP MediaServer</modelName>
        <modelNumber>1</modelNumber>
        <modelURL>http://www.syntaxjockey.com/higgins</modelURL>
        <serialNumber>0</serialNumber>
        <UDN>%s</UDN>
        <UPC/>
        <serviceList>
            <service>
                <serviceType>urn:schemas-upnp-org:service:ConnectionManager:1</serviceType>
                <serviceId>urn:upnp-org:serviceId:urn:schemas-upnp-org:service:ConnectionManager</serviceId>
                <SCPDURL>ConnectionManager/scpd.xml</SCPDURL>
                <controlURL>ConnectionManager/control</controlURL>
                <eventSubURL>ConnectionManager/event</eventSubURL>
            </service>
            <service>
                <serviceType>urn:schemas-upnp-org:service:ContentDirectory:1</serviceType>
                <serviceId>urn:upnp-org:serviceId:urn:schemas-upnp-org:service:ContenDirectory</serviceId>
                <SCPDURL>ContentDirectory/scpd.xml</SCPDURL>
                <controlURL>ContentDirectory/control</controlURL>
                <eventSubURL>ContentDirectory/event</eventSubURL>
            </service>
        </serviceList>
        <deviceList/>
    </device>
</root>
        """ % (self.urlbase, self.devicename, self.uuid), 'text/xml')

    def locateChild(self, request, segments):
        return self, []

class Content(resource.Resource):
    def render(self, request):
        f = open(self.song.file.path, "r")
        mimetype = MimeType.fromString(self.song.file.mimetype)
        self.song = None
        return HttpResponse(200,
                            {'Content-Type': mimetype },
                            FileStream(f))

    def locateChild(self, request, segments):
        try:
            log_debug("[upnp] streaming /content/%s" % segments[0])
            item = int(segments[0])
            self.song = Song.objects.filter(id=item)[0]
            log_debug("[upnp] /content/%s -> %s" % (segments[0], self.song.file.path))
            return self, []
        except Exception, e:
            log_debug("[upnp] can't stream /content/%s: %s" % (segments[0], e))
            return None, []

class MediaServer(resource.Resource):
    def __init__(self, addr, port, urlbase, devicename, uuid):
        resource.Resource.__init__(self)
        self.addr = addr
        self.port = port
        self.urlbase = urlbase
        self.devicename = devicename
        self.uuid = uuid
    def locateChild(self, request, segments):
        if segments[0] == "root-device.xml":
            return RootDevice(self.urlbase, self.devicename, self.uuid), segments[1:]
        if segments[0] == "content":
            return Content(), segments[1:]
        if segments[0] == "ContentDirectory":
            return ContentDirectory(self.addr, self.port), segments[1:]
        if segments[0] == "ConnectionManager":
            return ConnectionManager(), segments[1:]
        return None, []

class MSService:
    def __init__(self, ssdp, interfaces=[]):
        self.ssdp = ssdp
        if len(interfaces) == 0:
            self.interfaces = [addr for name,(addr,up) in netif.list_interfaces().items()]
        else:
            self.interfaces = interfaces
        self.servers = {}

    def start(self):
        name = conf.get("UPNP_SHARE_NAME")
        uuid = conf.get("UPNP_UUID")
        for iface in self.interfaces:
            urlbase = 'http://%s:%d/' % (iface, 31338)
            site = Site(MediaServer(iface, 31338, urlbase, name, uuid))
            server = reactor.listenTCP(31338, channel.HTTPFactory(site), interface=iface)
            self.servers[iface] = server
            # register available services
            self.ssdp.register('%s::upnp:rootdevice' % uuid,
                               'upnp:rootdevice',
                               urlbase + 'root-device.xml')
            self.ssdp.register(uuid, uuid, urlbase + 'root-device.xml')
            self.ssdp.register('%s::urn:schemas-upnp-org:device:MediaServer:1' % uuid,
                               'urn:schemas-upnp-org:device:MediaServer:1',
                               urlbase + 'root-device.xml')
            self.ssdp.register('%s::urn:schemas-upnp-org:service:ConnectionManager:1' % uuid,
                               'urn:schemas-upnp-org:device:ConnectionManager:1',
                               urlbase + 'root-device.xml')
            self.ssdp.register('%s::urn:schemas-upnp-org:service:ContentDirectory:1' % uuid,
                               'urn:schemas-upnp-org:device:ContentDirectory:1',
                               urlbase + 'root-device.xml')

    def stop(self):
        for server in self.servers.items():
            d = server.stopListening()
            if d:
                log_debug("MediaServer couldn't immediately stop listening, deferring")
            self.ssdp.unregister()
