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
        attrs['upnp_UDN'] = udn
        logger.log_debug("UDN for %s is %s" % (name, udn))
        # load services
        services = {}
        for key,svc in attrs.items():
            if isinstance(svc, UPNPDeviceService):
                services[svc.upnp_service_id] = svc
        for base in bases:
            if hasattr(base, '_upnp_services'):
                base._upnp_services.update(services)
                services = base._upnp_services
        attrs['_upnp_services'] = services
        return super(DeviceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class UPNPDevice(Service):
    __metaclass__ = DeviceDeclarativeParser

    upnp_manufacturer = "Higgins Project"
    upnp_manufacturer_url = "http://syntaxjockey.com/higgins"
    upnp_model_name = "Higgins UPnP Device"
    upnp_model_description = "Higgins UPnP Device"
    upnp_model_url = "http://syntaxjockey.com/higgins"
    upnp_model_number = None
    upnp_serial_number = None
    upnp_device_name = None
    upnp_device_type = None
    upnp_friendly_name = None
    upnp_UDN = None

    def startService(self):
        Service.startService(self)

    def stopService(self):
        return maybeDeferred(Service.stopService, self)

    def get_description(self, host, relativeUrls=False):
        root = Element("root")
        root.attrib['xmlns'] = 'urn:schemas-upnp-org:device-1-0'
        version = SubElement(root, "specVersion")
        SubElement(version, "major").text = "1"
        SubElement(version, "minor").text = "0"
        device = SubElement(root, "device")
        SubElement(device, "deviceType").text = self.upnp_device_type
        SubElement(device, "friendlyName").text = self.upnp_friendly_name
        SubElement(device, "manufacturer").text = self.upnp_manufacturer
        SubElement(device, "UDN").text = "uuid:%s" % self.upnp_UDN
        if self.upnp_manufacturer_url:
            SubElement(device, "manufacturerURL").text = self.upnp_manufacturer_url
        SubElement(device, "modelName").text = self.upnp_model_name
        if self.upnp_model_name:
            SubElement(device, "modelDescription").text = self.upnp_model_description
        if self.upnp_model_url:
            SubElement(device, "modelURL").text = self.upnp_model_url
        if self.upnp_model_number:
            SubElement(device, "modelNumber").text = self.upnp_model_number
        if self.upnp_serial_number:
            SubElement(device, "serialNumber").text = self.upnp_serial_number
        if relativeUrls:
            urlbase = ''
            SubElement(device, "URLBase").text = "http://%s" % host
        else:
            urlbase = "http://%s" % host
        svc_list = SubElement(device, "serviceList")
        for svc in self._upnp_services.values():
            service = SubElement(svc_list, "service")
            SubElement(service, "serviceType").text = svc.upnp_service_type
            SubElement(service, "serviceId").text = svc.upnp_service_id
            SubElement(service, "SCPDURL").text = "%s/%s/%s" % (
                urlbase,
                self.upnp_UDN.replace(':', '_'),
                svc.upnp_service_id.replace(':', '_')
                )
            SubElement(service, "controlURL").text = "%s/%s/%s/control" % (
                urlbase,
                self.upnp_UDN.replace(':', '_'),
                svc.upnp_service_id.replace(':', '_')
                )
            SubElement(service, "eventSubURL").text = "%s/%s/%s/event" % (
                urlbase,
                self.upnp_UDN.replace(':', '_'),
                svc.upnp_service_id.replace(':', '_')
                )
        return xmlprint(root)

    def __str__(self):
        return self.upnp_UDN

# Define the public API
__all__ = ['UPNPDevice',]
