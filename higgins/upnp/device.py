# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import random, string, urllib
from twisted.internet.defer import maybeDeferred
from xml.etree.ElementTree import Element, SubElement
from higgins.service import Service
from higgins.conf import conf
from higgins.upnp.device_service import UPNPDeviceService
from higgins.upnp.prettyprint import xmlprint
from higgins.upnp.logger import logger

class DeviceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # TODO: verify required service attributes
        # create UDN if needed
        udn_conf_key = "UPNP_" + name + "_UDN"
        udn = conf.get(udn_conf_key)
        if udn == None:
            udn = ''.join(map(lambda x: random.choice(string.letters), xrange(20)))
            conf[udn_conf_key] = udn
        attrs['UDN'] = udn
        logger.log_debug("UDN for %s is %s" % (name, udn))
        # load services
        services = {}
        for key,svc in attrs.items():
            if isinstance(svc, UPNPDeviceService):
                # add the service back-reference for each StateVar and Action
                for statevar in svc._stateVars.values():
                    statevar.service = svc
                for action in svc._actions.values():
                    action.service = svc
                services[svc.serviceID] = svc
        attrs['_services'] = services
        return super(DeviceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class UPNPDevice(Service):
    __metaclass__ = DeviceDeclarativeParser

    manufacturer = "Higgins Project"
    manufacturerURL = "http://syntaxjockey.com/higgins"
    modelName = "Higgins UPnP Device"
    modelDescription = "Higgins UPnP Device"
    modelURL = "http://syntaxjockey.com/higgins"
    modelNumber = None
    serialNumber = None
    deviceName = None
    deviceType = None
    friendlyName = None
    UDN = None

    def startService(self):
        Service.startService(self)

    def stopService(self):
        return maybeDeferred(Service.stopService, self)

    def getDescription(self, host, relativeUrls=False):
        root = Element("root")
        root.attrib['xmlns'] = 'urn:schemas-upnp-org:device-1-0'
        version = SubElement(root, "specVersion")
        SubElement(version, "major").text = "1"
        SubElement(version, "minor").text = "0"
        device = SubElement(root, "device")
        SubElement(device, "deviceType").text = self.deviceType
        SubElement(device, "friendlyName").text = self.friendlyName
        SubElement(device, "manufacturer").text = self.manufacturer
        SubElement(device, "UDN").text = "uuid:%s" % self.UDN
        SubElement(device, "modelName").text = self.modelName
        if self.manufacturerURL:
            SubElement(device, "manufacturerURL").text = self.manufacturerURL
        if self.modelDescription:
            SubElement(device, "modelDescription").text = self.modelDescription
        if self.modelURL:
            SubElement(device, "modelURL").text = self.modelURL
        if self.modelNumber:
            SubElement(device, "modelNumber").text = self.modelNumber
        if self.serialNumber:
            SubElement(device, "serialNumber").text = self.serialNumber
        if relativeUrls:
            urlbase = ''
            SubElement(device, "URLBase").text = "http://%s" % host
        else:
            urlbase = "http://%s" % host
        svc_list = SubElement(device, "serviceList")
        for svc in self._services.values():
            service = SubElement(svc_list, "service")
            SubElement(service, "serviceType").text = svc.serviceType
            SubElement(service, "serviceId").text = svc.serviceID
            SubElement(service, "SCPDURL").text = "%s/%s/%s" % (
                urlbase,
                self.UDN.replace(':', '_'),
                svc.serviceID.replace(':', '_')
                )
            SubElement(service, "controlURL").text = "%s/%s/%s/control" % (
                urlbase,
                self.UDN.replace(':', '_'),
                svc.serviceID.replace(':', '_')
                )
            SubElement(service, "eventSubURL").text = "%s/%s/%s/event" % (
                urlbase,
                self.UDN.replace(':', '_'),
                svc.serviceID.replace(':', '_')
                )
        return xmlprint(root)

    def __str__(self):
        return self.UDN

# Define the public API
__all__ = ['UPNPDevice',]
