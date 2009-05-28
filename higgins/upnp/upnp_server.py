# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from urlparse import urlparse
from twisted.internet import reactor
from higgins.http.resource import Resource
from higgins.http.static import Data as StaticResource
from higgins.upnp.control_resource import ControlResource
from higgins.upnp.event_resource import EventResource
from higgins.upnp.logger import logger

class RootResource(Resource):
    def __init__(self, server):
        Resource.__init__(self)
        self.server = server
    def locateChild(self, request, segments):
        segments = [part for part in segments if part != '']
        logger.log_debug("%s" % '/' + '/'.join(segments))
        # we need the Host header
        if request.host == None:
            logger.log_warning("can't determine host from request, ignoring")
            return None, []
        # this is a fix for coherence (seen on v0.6.2), which doesn't send the
        # port number as part of the Host header.
        urlparts = urlparse('http://' + request.host)
        host = '%s:1901' % urlparts.netloc
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
            return StaticResource(device.get_description(host, True), 'text/xml'), []
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
        if segments[0] == 'event':
            return EventResource(service), []
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
