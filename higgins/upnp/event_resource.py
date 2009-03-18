# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import urllib
from twisted.internet import defer
from xml.etree.ElementTree import XML, Element, SubElement, tostring as xmltostring
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.http.http_headers import DefaultHTTPHandler, last, parseKeyValue
from higgins.http.stream import BufferedStream
from higgins.upnp.logger import logger

def _parseCallback(header):
    return header
DefaultHTTPHandler.addParser("callback", (last, _parseCallback))

def _parseNT(header):
    return header
DefaultHTTPHandler.addParser("nt", (last, _parseNT))

def _parseTimeout(header):
    return header
DefaultHTTPHandler.addParser("timeout", (last, _parseTimeout))

class EventResource(Resource):
    def __init__(self, service):
        self.service = service

    def allowedMethods(self):
        return ('SUBSCRIBE','UNSUBSCRIBE')

    def http_SUBSCRIBE(self, request):
        try:
            logger.log_debug("event subscribe host: %s" % request.headers.getHeader('host'))
            logger.log_debug("event subscribe callback: %s" % request.headers.getHeader('callback'))
            logger.log_debug("event subscribe nt: %s" % request.headers.getHeader('nt'))
            logger.log_debug("event subscribe timeout: %s" % request.headers.getHeader('timeout'))
            return Response(200)
        except:
            return Response(400)

    def http_UNSUBSCRIBE(self, request):
        return Response(400)

__all__ = ['EventResource',]
