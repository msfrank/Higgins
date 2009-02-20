import urllib
from twisted.internet import reactor
from higgins import netif
from higgins.http import resource
from higgins.http.static import Data as StaticResource
from higgins.upnp.control_resource import ControlResource
from higgins.upnp.logger import logger

class RootResource(resource.Resource):
    def __init__(self, server):
        resource.Resource.__init__(self)
        self.server = server
    def locateChild(self, request, segments):
        logger.log_debug("request URI: %s" % '/' + '/'.join(segments))
        # we need the Host header
        host = request.headers.getHeader('host')
        if host == None:
            logger.log_warning("request has no Host header, ignoring")
            return None, []
        # / returns 404
        if segments == []:
            return None, []
        # the first segment is the device UDN with ':' escaped as '_'
        device_id = segments[0].replace('_',':')
        try:
            device = self.server.devices[device_id]
        except:
            logger.log_warning("device '%s' doesn't exist" % device_id)
            return None, []
        # if the next segment is 'root-device.xml', return the device description
        segments = segments[1:]
        if segments == []:
            return StaticResource(device.get_description(host), 'text/xml'), []
        # otherwise the next segment is the service ID
        service_id = segments[0].replace('_',':')
        try:
            service = device._upnp_services[service_id]
        except:
            logger.log_warning("service '%s' doesn't exist" % service_id)
            return None, []
        segments = segments[1:]
        if segments == []:
            return StaticResource(service.get_description(), 'text/xml'), []
        if segments[0] == 'control':
            return ControlResource(service), []
        #if segments[0] == 'event':
        #    return EventResource(service), []
        return None, []

class UPnPServer:
    def __init__(self):
        self.devices = {}

    def start(self):
        from higgins.http.server import Site
        from higgins.http.channel import HTTPFactory
        self.site = Site(RootResource(self))
        self.listener = reactor.listenTCP(1901, HTTPFactory(self.site))
        logger.log_debug("UPnP Server listening on port 1901")

    def stop(self):
        self.listener.stopListening()
        self.server = None

    def registerDevice(self, device):
        self.devices[device.upnp_UDN] = device
        logger.log_debug("registered device %s with UPnP server" % device.upnp_UDN)

    def unregisterDevice(self, device):
        del self.devices[device.upnp_UDN]
        logger.log_debug("unregistered device %s with UPnP server" % device.upnp_UDN)
