from twisted.web2 import resource
from twisted.web2.static import Data as StaticResource
from twisted.internet import reactor
from higgins import netif
from control_resource import ControlResource
from logger import logger

class RootResource(resource.Resource):
    def __init__(self, server):
        resource.Resource.__init__(self)
        self.server = server
    def locateChild(self, request, segments):
        # the first segment is the device UDN
        device_id = urllib.unquote(segments[0])
        try:
            device = self.server.devices[device_id]
        except:
            logger.log_warning("device '%s' doesn't exist" % device_id)
            return None, []
        # if there are no more segments, return the device description
        segments = segments[1:]
        if segments == []:
            return StaticResource(str(device), 'text/xml'), []
        # the next segment is the service ID
        service_id = urllib.unquote(segments[0])
        try:
            service = device._upnp_services[service_id]
        except:
            logger.log_warning("service '%s' doesn't exist" % service_id)
            return None, []
        segments = segments[1:]
        if segments == []:
            return StaticResource(str(service), 'text/xml'), []
        if segments[0] == 'control':
            return ControlResource(service), []
        #if segments[0] == 'event':
        #    return EventResource(service), []
        return None, []

class UPnPServer:
    def __init__(self):
        self.devices = {}

    def start(self):
        from twisted.web2.server import Site
        from twisted.web2.channel import HTTPFactory
        self.site = Site(RootResource(self))
        self.listener = reactor.listenTCP(1901, HTTPFactory(self.site))
        logger.log_debug("UPnP Server listening on port 1901")

    def stop(self):
        self.listener.stopListening()
        self.server = None

    def registerDevice(self, device):
        self.devices[device.upnp_device_name] = device

    def unregisterDevice(self, device):
        del self.devices[device.upnp_device_name]
