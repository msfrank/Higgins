# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2005, Tim Potter <tpot@samba.org>
# Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

from twisted.web import resource, static
from connection_manager import ConnectionManager
from content_directory import ContentDirectory

class RootDevice(static.Data):
    isLeaf = True
    allowedMethods = ('GET',)
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

class MediaServer(resource.Resource):
    def __init__(self, urlbase, devicename, uuid):
        resource.Resource.__init__(self)
        self.urlbase = urlbase
        self.devicename = devicename
        self.uuid = uuid
        self.putChild("root-device.xml", RootDevice(self.urlbase, self.devicename, self.uuid))
        self.putChild("ContentDirectory", ContentDirectory())
        self.putChild("ConnectionManager", ConnectionManager())
