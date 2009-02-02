from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring
from service import Service

class DeviceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # verify required service attributes
        # load services
        services = []
        for name,object in attrs.items():
            if isinstance(object, Service):
                services.append(object)
        for base in bases:
            if hasattr(base, '_upnp_services'):
                services = base._upnp_services + services
        attrs['_upnp_services'] = services
        return super(DeviceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class Device:
    __metaclass__ = DeviceDeclarativeParser

    upnp_manufacturer = "Higgins Project"
    upnp_model_name = "Higgins UPnP Device"
    upnp_device_name = None
    upnp_device_type = None
    upnp_friendly_name = None
    upnp_UDN = None

    def _getUDN(self, name):
        udn = conf.get(name)
        if udn == None:
            udn=''.join([ 'uuid:'] + map(lambda x: random.choice(string.letters), xrange(20)))
            conf[name] = udn
        return udn

    def __repr__(self):
        root = Element("{urn:schemas-upnp-org:device-1-0}root")
        version = SubElement(root, "specVersion")
        SubElement(version, "major").text = "1"
        SubElement(version, "minor").text = "0"
        device = SubElement(root, "device")
        SubElement(device, "deviceType").text = self.upnp_device_type
        SubElement(device, "friendlyName").text = self.upnp_friendly_name
        SubElement(device, "manufacturer").text = self.upnp_manufacturer
        SubElement(device, "modelName").text = self.upnp_model_name
        if iscallable(self.upnp_UDN):
            SubElement(device, "UDN").text = self.upnp_UDN()
        else:
            SubElement(device, "UDN").text = self._getUDN(str(self.upnp_UDN))
        svc_list = SubElement(device, "serviceList")
        for svc in self._upnp_services:
            service = SubElement(svc_list, "service")
            SubElement(service, "serviceType").text = svc.upnp_service_type
            SubElement(service, "serviceId").text = svc.upnp_service_id
            SubElement(service, "SCPDURL").text = "%s" % urlescape(svc.upnp_service_id)
            SubElement(service, "controlURL").text = "%s/control" % urlescape(svc.upnp_service_id)
            SubElement(service, "eventSubURL").text = "%s/event" % urlescape(svc.upnp_service_id)
        return xmltostring(root)
