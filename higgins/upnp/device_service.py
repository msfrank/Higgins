# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from urlparse import urlparse
from uuid import uuid4
from xml.etree.ElementTree import XML, Element, SubElement, tostring as xmltostring
from twisted.internet import reactor, protocol
from twisted.web.client import HTTPClientFactory
from higgins.signals import Signal
from higgins.http.client.http import HTTPClientProtocol, ClientRequest
from higgins.http.http_headers import DefaultHTTPHandler, MimeType, singleHeader
from higgins.http.stream import readAndDiscard
from higgins.upnp.statevar import StateVar
from higgins.upnp.action import Action, InArgument, OutArgument
from higgins.upnp.prettyprint import prettyprint
from higgins.upnp.logger import logger

class Subscription(object):
    def __init__(self, callbacks, timeout=1800):
        self.callbacks = [(url,urlparse(url)) for url in callbacks]
        self.timeout = timeout
        self.id = 'uuid:' + str(uuid4())
        self.seqid = 0

class DeviceServiceDeclarativeParser(type):
    def __new__(cls, name, bases, attrs):
        # load state variables and actions
        stateVars = {}
        actions = {}
        for key,object in attrs.items():
            if isinstance(object, StateVar):
                stateVars[key] = object
                object.name = key
                object.service = cls
            elif isinstance(object, Action):
                actions[key] = object
                object.name = key
                object.service = cls
        # load stateVars and actions from any base classes
        #for base in bases:
        #    if hasattr(base, '_upnp_stateVars'):
        #        base._upnp_stateVars.update(stateVars)
        #        stateVars = base._upnp_stateVars
        #    if hasattr(base, '_upnp_actions'):
        #        base._upnp_actions.update(actions)
        #        actions = base._upnp_actions
        attrs['_upnp_stateVars'] = stateVars
        attrs['_upnp_actions'] = actions
        attrs['_upnp_subscribers'] = {}
        new_class = super(DeviceServiceDeclarativeParser,cls).__new__(cls, name, bases, attrs)
        logger.log_debug("%s: stateVars=%s" % (name, attrs['_upnp_stateVars']))
        logger.log_debug("%s: actions=%s" % (name, attrs['_upnp_actions']))
        logger.log_debug("%s: subscribers=%s" % (name, attrs['_upnp_subscribers']))
        return new_class

class UPNPDeviceService(object):
    __metaclass__ = DeviceServiceDeclarativeParser

    upnp_service_type = None
    upnp_service_id = None
    upnp_statevar_changed = Signal()

    def get_description(self):
        scpd = Element("{urn:schemas-upnp-org:service-1-0}scpd")
        version = SubElement(scpd, "specVersion")
        SubElement(version, "major").text = "1"
        SubElement(version, "minor").text = "0"
        action_list = SubElement(scpd, "actionList")
        for action_name,upnp_action in self._upnp_actions.items():
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
        for var_name,upnp_stateVar in self._upnp_stateVars.items():
            stateVar = SubElement(var_list, "stateVariable")
            if upnp_stateVar.sendEvents:
                stateVar.attrib['sendEvents'] = "yes"
            else:
                stateVar.attrib['sendEvents'] = "no"
            SubElement(stateVar, "name").text = var_name
            SubElement(stateVar, "dataType").text = upnp_stateVar.type
            if not upnp_stateVar.text_value == None:
                SubElement(stateVar, "defaultValue").text = upnp_stateVar.text_value
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
        return prettyprint(scpd)

    def subscribe(self, callbacks, timeout=1800):
        s = Subscription(callbacks, timeout)
        self._upnp_subscribers[s.id] = s
        logger.log_debug("service %s created new subscription %s" % (self.upnp_service_id,s.id))
        self._upnp_notify_subscriber(s)
        return s

    def renew(self, sid, timeout):
        if sid not in self._upnp_subscribers:
            raise KeyError
        logger.log_debug("service %s renewed subscription %s" % (self.upnp_service_id, sid))

    def unsubscribe(self, sid):
        if sid not in self._upnp_subscribers:
            raise KeyError
        del self._upnp_subscribers[sid]
        logger.log_debug("service %s unsubscribed %s" % (self.upnp_service_id, sid))

    def _upnp_notify_subscriber(self, subscriber):
        # create the request body
        propset = Element("{urn:schemas-upnp-org:event-1-0}propertyset")
        prop = SubElement(propset, "{urn:schemas-upnp-org:event-1-0}property")
        # add each evented statevar to the property set
        for var_name,upnp_stateVar in self._upnp_stateVars.items():
            if upnp_stateVar.sendEvents:
                SubElement(prop, var_name).text = upnp_stateVar.text_value
        postData = prettyprint(propset)
        logger.log_debug("NOTIFY property set:\n" + postData)
        # send the NOTIFY request to each callback
        for url,urlparts in subscriber.callbacks:
            # set the NOTIFY headers
            headers = {
                'Host': urlparts.netloc,
                'Content-Type': MimeType('text', 'xml'),
                'NT': 'upnp:event',
                'NTS': 'upnp:propchange',
                'SID': subscriber.id,
                'SEQ': subscriber.seqid
                }
            #
            creator = protocol.ClientCreator(reactor, HTTPClientProtocol)
            request = ClientRequest("NOTIFY", urlparts.path, headers, postData)
            d = creator.connectTCP(urlparts.hostname, urlparts.port)
            def _notifySuccess(response):
                readAndDiscard(response.stream)
                logger.log_debug("NOTIFY succeeded")
            def _notifyFailed(failure):
                logger.log_warning("NOTIFY failed: %s" % str(failure))
            def _sendNotifyRequest(proto, request):
                d = proto.submitRequest(request)
                d.addCallbacks(_notifySuccess, _notifyFailed)
            d.addCallback(_sendNotifyRequest, request)
            logger.log_debug("sending NOTIFY to %s" % url)

    def __str__(self):
        return self.upnp_service_id

def _generateNTS(nts):
    return str(nts)
DefaultHTTPHandler.addGenerators("NTS", (_generateNTS, singleHeader))

def _generateSEQ(seq):
    return str(seq)
DefaultHTTPHandler.addGenerators("SEQ", (_generateSEQ, singleHeader))

# Define the public API
__all__ = ['UPNPDeviceService', 'Subscription']
