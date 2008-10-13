from twisted.web2 import resource
from twisted.web2.http import Response as HttpResponse
from twisted.web2.http_headers import DefaultHTTPHandler, last, parseKeyValue
from twisted.internet import defer
from twisted.web2.stream import BufferedStream
from xml.etree.ElementTree import XML, Element, SubElement, tostring as xmltostring
from higgins.logging import log_error, log_debug

class SoapBag:
    def __init__(self):
        self.args = {}
    def get(self, name, default):
        try:
            type,value = self.args[name]
            return value
        except:
            return default
    def get_string(self, name, default):
        try:
            type,value = self.args[name]
            return str(value)
        except:
            return str(default)
    def get_integer(self, name, default):
        try:
            type,value = self.args[name]
            return int(value)
        except:
            return int(default)
    def set(self, type, name, value):
        self.args[name] = (type,value)

def _parseSoapAction(header):
    return ''.join(header.split('"')).split('#', 1)
DefaultHTTPHandler.addParser("soapaction", (last, _parseSoapAction))

class SoapResource(resource.Resource):
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
            # todo: use request.soap_ns and request.soap_action to get action element
            action = body[0]
            args = SoapBag()
            for arg in action:
                try:
                    type = arg.attrib["{http://www.w3.org/1999/XMLSchema-instance}type"]
                except:
                    type = "xsd:string"
                args.set(type, arg.tag, arg.text)
            request.soap_args = args
            return self.render(request)
        except Exception, e:
            log_debug("[upnp] failed to parse soap request: %s" % e)
            return HttpResponse(400)

    def render(self, request):
        try:
            soap_method = getattr(self, "SOAP_%s" % request.soap_action)
            results = soap_method(request.soap_args)
            env = Element("{http://schemas.xmlsoap.org/soap/envelope/}Envelope")
            body = SubElement(env, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
            resp = SubElement(body, "{%s}%sResponse" % (request.soap_ns,request.soap_action))
            for name,(type,value) in results.args.items():
                arg = SubElement(resp, name)
                arg.attrib["{http://www.w3.org/1999/XMLSchema-instance}type"] = type
                arg.text = str(value)
            output = xmltostring(env)
            log_debug("[upnp] executed soap method %s" % request.soap_action)
            return HttpResponse(200, stream=output)
        except Exception, e:
            log_debug("[upnp] failed to execute soap method: %s" % e)
            return HttpResponse(404)

    def http_POST(self, request):
        request.buffered_stream = BufferedStream(request.stream)
        request.soap_data = ''
        request.soap_ns,request.soap_action = request.headers.getHeader('soapaction')
        return self._readSoapData(request).addCallbacks(lambda l: self._dispatchSoapRequest(request))
