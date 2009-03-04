# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http import resource
from higgins.http.static import Data as StaticResource
from higgins.http.http import Response as HttpResponse
from higgins.http.http_headers import DefaultHTTPHandler, last, parseKeyValue
from higgins.http.stream import BufferedStream
from twisted.internet import defer
from xml.etree.ElementTree import XML, Element, SubElement, tostring as xmltostring
import urllib
from logger import logger

def _parseSoapAction(header):
    return ''.join(header.split('"')).split('#', 1)
DefaultHTTPHandler.addParser("soapaction", (last, _parseSoapAction))

class ControlResource(resource.Resource):
    def __init__(self, service):
        self.service = service

    def _readSoapData(self, request):
        while not request.buffered_stream.length == 0:
                retval = request.buffered_stream.readExactly(512)
                if isinstance(retval, defer.Deferred):
                    data = defer.waitForDeferred(retval)
                    yield data
                    request.soap_data = request.soap_data + data.getResult()
    _readSoapData = defer.deferredGenerator(_readSoapData)

    def _dispatchSoapRequest(self, request):
        try:
            envelope = XML(request.soap_data)
            body = envelope.find("{http://schemas.xmlsoap.org/soap/envelope/}Body")
            # determine UPnP action
            action = body.find("{%s}%s" % (request.soap_ns, request.soap_action))
            # look up the action in the service
            upnp_action = self.service._upnp_actions[action.tag]
            # build a list of the action arguments
            in_args = {}
            for arg in action:
                in_args[arg.tag] = arg.text
        except Exception, e:
            logger.log_debug("failed to parse SOAP request: %s" % e)
            return HttpResponse(400)
        try:
            # execute the UPnP action
            out_args = upnp_action(self.service, in_args)
            # return the action response
            env = Element("{http://schemas.xmlsoap.org/soap/envelope/}Envelope")
            body = SubElement(env, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
            resp = SubElement(body, "{%s}%sResponse" % (request.soap_ns,request.soap_action))
            for (name,type,value) in out_args:
                arg = SubElement(resp, name)
                arg.attrib["{http://www.w3.org/1999/XMLSchema-instance}type"] = type
                arg.text = str(value)
            output = xmltostring(env)
            logger.log_debug("executed UPnP action '%s'" % request.soap_action)
            return HttpResponse(200, stream=output)
        except Exception, e:
            logger.log_debug("failed to execute UPnP action '%s': %s" % (action.name, e))
            return HttpResponse(400)

    def http_POST(self, request):
        request.buffered_stream = BufferedStream(request.stream)
        request.soap_data = ''
        request.soap_ns,request.soap_action = request.headers.getHeader('soapaction')
        return self._readSoapData(request).addCallbacks(lambda l: self._dispatchSoapRequest(request))
