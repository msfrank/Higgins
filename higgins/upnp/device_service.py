# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from urlparse import urlparse
from uuid import uuid4
from xml.etree.ElementTree import XML, Element, SubElement
from twisted.internet import reactor, protocol
from twisted.web.client import HTTPClientFactory
from higgins.signals import Signal
from higgins.http.client.http import HTTPClientProtocol, ClientRequest
from higgins.http.http_headers import DefaultHTTPHandler, MimeType, singleHeader
from higgins.http.stream import readAndDiscard
from higgins.upnp.statevar import StateVar
from higgins.upnp.action import Action, InArgument, OutArgument
from higgins.upnp.prettyprint import xmlprint
from higgins.upnp.logger import logger

class Subscription(object):
    def __init__(self, callbacks, timeout=1800):
        self.callbacks = [(url,urlparse(url)) for url in callbacks]
        self.timeout = timeout
        self.id = 'uuid:' + str(uuid4())
        self.seqid = 0

    def _notify(self, statevars):
        # create the request body
        propset = Element("e:propertyset")
        propset.attrib['xmlns:e'] = "urn:schemas-upnp-org:event-1-0"
        prop = SubElement(propset, "e:property")
        # add each evented statevar to the property set
        for statevar in statevars:
            if statevar.sendEvents:
                SubElement(prop, statevar.name).text = statevar.text_value
            else:
                raise Exception("StateVar '%s' is not evented" % statevar.name)
        postData = xmlprint(propset)
        logger.log_debug("NOTIFY property set:\n" + postData)
        # send the NOTIFY request to each callback
        for url,urlparts in self.callbacks:
            # set the NOTIFY headers
            headers = {
                'Host': urlparts.netloc,
                'Content-Type': MimeType('text', 'xml'),
                'NT': 'upnp:event',
                'NTS': 'upnp:propchange',
                'SID': self.id,
                'SEQ': self.seqid
                }
            #
            creator = protocol.ClientCreator(reactor, HTTPClientProtocol)
            request = ClientRequest("NOTIFY", urlparts.path, headers, postData)
            d = creator.connectTCP(urlparts.hostname, urlparts.port)
            d.addCallback(self._sendNotifyRequest, request)
            logger.log_debug("sending NOTIFY to %s" % url)
        self.seqid = self.seqid + 1

    def _sendNotifyRequest(self, proto, request):
        d = proto.submitRequest(request)
        d.addCallbacks(self._notifySuccess, self._notifyFailed)

    def _notifySuccess(self, response):
        readAndDiscard(response.stream)
        logger.log_debug("NOTIFY succeeded")

    def _notifyFailed(self, failure):
        logger.log_warning("NOTIFY failed: %s" % str(failure))

class DeviceServiceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # load state variables and actions
        stateVars = {}
        actions = {}
        for key,object in attrs.items():
            if isinstance(object, StateVar):
                stateVars[key] = object
                object.name = key
            elif isinstance(object, Action):
                actions[key] = object
                object.name = key
        attrs['_stateVars'] = stateVars
        attrs['_actions'] = actions
        attrs['_subscribers'] = {}
        return super(DeviceServiceDeclarativeParser,cls).__new__(cls, name, bases, attrs)

class UPNPDeviceService(object):
    __metaclass__ = DeviceServiceDeclarativeParser

    serviceType = None
    serviceID = None

    def getDescription(self):
        scpd = Element("scpd")
        scpd.attrib['xmlns'] = 'urn:schemas-upnp-org:service-1-0'
        version = SubElement(scpd, "specVersion")
        SubElement(version, "major").text = "1"
        SubElement(version, "minor").text = "0"
        action_list = SubElement(scpd, "actionList")
        for action_name,upnp_action in self._actions.items():
            action = SubElement(action_list, "action")
            SubElement(action, "name").text = action_name
            arg_list = SubElement(action, "argumentList")
            all_args = upnp_action.in_args + upnp_action.out_args
            for upnp_arg in all_args:
                arg = SubElement(arg_list, "argument")
                SubElement(arg, "name").text = upnp_arg.name
                SubElement(arg, "direction").text = upnp_arg.direction
                SubElement(arg, "relatedStateVariable").text = upnp_arg.related.name
                if upnp_arg.retval:
                    SubElement(arg, "retval")
        var_list = SubElement(scpd, "serviceStateTable")
        for var_name,upnp_stateVar in self._stateVars.items():
            stateVar = SubElement(var_list, "stateVariable")
            if upnp_stateVar.sendEvents:
                stateVar.attrib['sendEvents'] = "yes"
            else:
                stateVar.attrib['sendEvents'] = "no"
            SubElement(stateVar, "name").text = var_name
            SubElement(stateVar, "dataType").text = upnp_stateVar.type
            #if not upnp_stateVar.text_value == None:
            #    SubElement(stateVar, "defaultValue").text = upnp_stateVar.text_value
            if not upnp_stateVar.allowedValueList == None:
                allowed_list = SubElement(stateVar, "allowedValueList")
                for allowed in upnp_stateVar.allowedValueList:
                    SubElement(allowed_list, "allowedValue").text = allowed
            if not upnp_stateVar.allowedMin == None and not upnp_stateVar.allowedMax == None:
                allowed_range = SubElement(stateVar, "allowedValueRange")
                SubElement(allowed_range, "minimum").text = str(upnp_stateVar.allowedMin)
                SubElement(allowed_range, "maximum").text = str(upnp_stateVar.allowedMax)
                if not upnp_stateVar.allowedStep == None:
                    SubElement(allowed_range, "step").text = str(upnp_stateVar.allowedStep)
        return xmlprint(scpd)

    def _subscribe(self, callbacks, timeout=1800):
        s = Subscription(callbacks, timeout)
        self._subscribers[s.id] = s
        logger.log_debug("service %s created new subscription %s" % (self.serviceID,s.id))
        s.handle = reactor.callLater(timeout, self._unsubscribe, s.id)
        s._notify([sv for sv in self._stateVars.values() if sv.sendEvents])
        return s

    def _renew(self, sid, timeout):
        try:
            s = self._subscribers[sid]
            s.handle.reset(timeout)
            logger.log_debug("service %s renewed subscription %s for %i seconds" % (self.serviceID, sid, timeout))
        except Exception, e:
            logger.log_debug("service %s failed to renew %s: %s" % (self.serviceID, sid, str(e)))

    def _unsubscribe(self, sid):
        try:
            s = self._subscribers[sid]
            s.handle.cancel()
            del self._subscribers[sid]
            logger.log_debug("service %s unsubscribed %s" % (self.serviceID, sid))
        except Exception, e:
            logger.log_debug("service %s failed to unsubscribe %s: %s" % (self.serviceID, sid, str(e)))

    def _notify(self, statevars):
        for s in self._subscribers.values(): s._notify(statevars)

    def __str__(self):
        return self.serviceID

def _generateNTS(nts):
    return str(nts)
DefaultHTTPHandler.addGenerators("NTS", (_generateNTS, singleHeader))

def _generateSEQ(seq):
    return str(seq)
DefaultHTTPHandler.addGenerators("SEQ", (_generateSEQ, singleHeader))

# Define the public API
__all__ = ['UPNPDeviceService', 'Subscription']
