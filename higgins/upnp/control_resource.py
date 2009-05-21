# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet import defer
from xml.etree.ElementTree import XML, Element, SubElement
from higgins.http import resource
from higgins.http.static import Data as StaticResource
from higgins.http.http import Response as HttpResponse
from higgins.http.http_headers import DefaultHTTPHandler, last, parseKeyValue, singleHeader
from higgins.http.stream import BufferedStream
from higgins.upnp.error import UPNPError
from higgins.upnp.logger import logger
from higgins.upnp.prettyprint import xmlprint

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
            try:
                envelope = XML(request.soap_data)
                body = envelope.find("{http://schemas.xmlsoap.org/soap/envelope/}Body")
                # determine UPnP action
                action = body.find("{%s}%s" % (request.soap_ns, request.soap_action))
                # look up the action in the service
                upnp_action = self.service._upnp_actions[request.soap_action]
                # build a list of the action arguments
                in_args = {}
                for arg in action:
                    in_args[arg.tag] = arg.text
                # execute the UPnP action
                logger.log_debug("executing %s#%s" % (self.service.upnp_service_id, request.soap_action))
                out_args = upnp_action(request, self.service, in_args)
                # return the action response
                env = Element("s:Envelope")
                env.attrib['xmlns:s'] = "http://schemas.xmlsoap.org/soap/envelope/"
                env.attrib['s:encodingStyle'] = "http://schemas.xmlsoap.org/soap/encoding/"
                env.attrib['xmlns:i'] = "http://www.w3.org/1999/XMLSchema-instance"
                body = SubElement(env, "s:Body")
                resp = SubElement(body, "u:%sResponse" % request.soap_action)
                resp.attrib['xmlns:u'] = request.soap_ns
                for (name,type,value) in out_args:
                    arg = SubElement(resp, name)
                    arg.attrib["i:type"] = type
                    arg.text = value
                output = xmlprint(env)
                return HttpResponse(200, headers={'EXT': ''}, stream=output)
            except UPNPError, e:
                raise e
            except Exception, e:
                logger.log_error("caught unhandled exception: %s" % e)
                raise UPNPError(500, "Internal server error")
        except UPNPError, e:
            logger.log_debug("failed to execute %s#%s: %s" % (self.service.upnp_service_id,request.soap_action, e))
            return HttpResponse(500,
                headers={'EXT': ''},
                stream="""<?xml version="1.0"?>
<u:Envelope
  xmlns:u="http://schemas.xmlsoap.org/soap/envelope"
  u:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
    <u:Body>
        <u:Fault>
            <faultcode>u:Client</faultcode>
            <faultstring>UPnPError</faultstring>
            <detail>
                <UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
                    <errorCode>%i</errorCode>
                    <errorDescription>%s</errorDescription>
                </UPnPError>
            </detail>
        </u:Fault>
    </u:Body>
</u:Envelope>""" % (e.code, e.reason)
                )
 
    def http_POST(self, request):
        request.buffered_stream = BufferedStream(request.stream)
        request.soap_data = ''
        request.soap_ns,request.soap_action = request.headers.getHeader('soapaction')
        return self._readSoapData(request).addCallbacks(lambda l: self._dispatchSoapRequest(request))

def _parseSoapAction(header):
    return ''.join(header.split('"')).split('#', 1)
DefaultHTTPHandler.addParser("soapaction", (last, _parseSoapAction))

DefaultHTTPHandler.addGenerators("EXT", (str, singleHeader))
