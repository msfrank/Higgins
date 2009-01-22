from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring
from upnp_service import Service

class DeviceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # verify required service attributes

        # load services
        services = []
        for name,object in attrs.items():
            if isinstance(object, Service):
                services.append(object)
        for base in bases:
            if hasattr(base, 'upnp_services'):
                services = base.upnp_services + services
        attrs['upnp_services'] = services
        return super(DeviceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class Device:
    __metaclass__ = DeviceDeclarativeParser

    upnp_version = (1,0)
    upnp_manufacturer = "Higgins Project"
    upnp_model_name = "Higgins UPnP Device"
    upnp_device_name = None
    upnp_device_type = None
    upnp_friendly_name = None
    upnp_UDN = None
    upnp_services = []

    def __repr__(self):
        root = Element("{urn:schemas-upnp-org:device-1-0}root")
        version = SubElement(root, "specVersion")
        SubElement(version, "major").text = self.upnp_version[0] 
        SubElement(version, "minor").text = self.upnp_version[1] 
        device = SubElement(root, "device")
        SubElement(device, "deviceType").text = self.device_params["deviceType"]
        SubElement(device, "friendlyName").text = self.device_params["friendlyName"]
        SubElement(device, "manufacturer").text = self.device_params["manufacturer"]
        SubElement(device, "modelName").text = self.device_params["modelName"]
        SubElement(device, "UDN").text = self.device_params["UDN"]
        svc_list = SubElement(device, "serviceList")
        for svc in self.device_services:
            service = SubElement(svc_list, "service")
            SubElement(service, "serviceType").text = svc.type
            SubElement(service, "serviceId").text = svc.id
            SubElement(service, "SCPDURL").text = svc.get_scpd_url()
            SubElement(service, "controlURL").text = svc.get_control_url()
            SubElement(service, "eventSubURL").text = svc.get_event_url()
        return xmltostring(root)
