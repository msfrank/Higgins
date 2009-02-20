import random, string, urllib
from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring
from higgins.service import Service
from higgins.conf import conf
from higgins.upnp import upnp_service
from higgins.upnp.service import Service as UPnPService
from higgins.upnp.logger import logger

class DeviceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # TODO: verify required service attributes
        # create UDN if needed
        udn_conf_key = "UPNP_" + name + "_UDN"
        udn = conf.get(udn_conf_key)
        if udn == None:
            udn = ''.join([ 'uuid:'] + map(lambda x: random.choice(string.letters), xrange(20)))
            conf[udn_conf_key] = udn
        attrs['upnp_UDN'] = udn
        logger.log_debug("UDN for %s is %s" % (name, udn))
        # load services
        services = {}
        for key,svc in attrs.items():
            if isinstance(svc, UPnPService):
                services[svc.upnp_service_id] = svc
        for base in bases:
            if hasattr(base, '_upnp_services'):
                base._upnp_services.update(services)
                services = base._upnp_services
        attrs['_upnp_services'] = services
        return super(DeviceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class Device(object, Service):
    __metaclass__ = DeviceDeclarativeParser

    upnp_manufacturer = "Higgins Project"
    upnp_model_name = "Higgins UPnP Device"
    upnp_device_name = None
    upnp_device_type = None
    upnp_friendly_name = None
    upnp_UDN = None

    def startService(self):
        Service.startService(self)
        upnp_service.registerUPnPDevice(self)

    def stopService(self):
        Service.stopService(self)
        upnp_service.unregisterUPnPDevice(self)

    def get_description(self, host=''):
        root = Element("{urn:schemas-upnp-org:device-1-0}root")
        version = SubElement(root, "specVersion")
        SubElement(version, "major").text = "1"
        SubElement(version, "minor").text = "0"
        device = SubElement(root, "device")
        SubElement(device, "deviceType").text = self.upnp_device_type
        SubElement(device, "friendlyName").text = self.upnp_friendly_name
        SubElement(device, "manufacturer").text = self.upnp_manufacturer
        SubElement(device, "modelName").text = self.upnp_model_name
        SubElement(device, "UDN").text = self.upnp_UDN
        svc_list = SubElement(device, "serviceList")
        for svc in self._upnp_services.values():
            service = SubElement(svc_list, "service")
            SubElement(service, "serviceType").text = svc.upnp_service_type
            SubElement(service, "serviceId").text = svc.upnp_service_id
            SubElement(service, "SCPDURL").text = "http://%s/%s/%s" % (
                host, self.upnp_UDN.replace(':','_'), svc.upnp_service_id.replace(':', '_')
                )
            SubElement(service, "controlURL").text = "http://%s/%s/%s/control" % (
                host, self.upnp_UDN.replace(':','_'), svc.upnp_service_id.replace(':', '_')
                )
            SubElement(service, "eventSubURL").text = "http://%s/%s/%s/event" % (
                host, self.upnp_UDN.replace(':','_'), svc.upnp_service_id.replace(':', '_')
                )
        return xmltostring(root)
