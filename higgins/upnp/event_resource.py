# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet import defer
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.http.http_headers import DefaultHTTPHandler, last, parseKeyValue, singleHeader
from higgins.upnp.logger import logger

class EventResource(Resource):
    def __init__(self, service):
        self.service = service

    def allowedMethods(self):
        return ('SUBSCRIBE','UNSUBSCRIBE')

    def http_SUBSCRIBE(self, request):
        try:
            # if there is no SID header, then this is a subscribe
            if not request.headers.hasHeader('sid'):
                # check that the NT header exists and is 'upnp:event'
                if not request.headers.hasHeader('nt'):
                    return Response(400)
                nt = request.headers.getHeader('nt')
                if not nt == 'upnp:event':
                    return Response(412)
                # get subscription timeout
                if request.headers.hasHeader('timeout'):
                    timeout = request.headers.getHeader('timeout')
                else:
                    timeout = 1800
                # get callbacks
                if not request.headers.hasHeader('callback'):
                    return Response(412)
                callbacks = request.headers.getHeader('callback')
                # create new subscription
                s = self.service.subscribe(callbacks, timeout)
                # send the SID and timeout back in the response
                return Response(200, {'sid': s.id, 'timeout': s.timeout})
            # otherwise this is a renewal
            else:
                if request.headers.hasHeader('nt'):
                    return Response(400)
                if request.headers.hasHeader('callback'):
                    return Response(400)
                sid = request.headers.getHeader('sid')
                self.service.renew(sid)
                return Response(200)
        except Exception, e:
            logger.log_error("SUBSCRIBE failed: %s" % e)
            return Response(500)

    def http_UNSUBSCRIBE(self, request):
        try:
            if not request.headers.hasHeader('sid'):
                return Response(412)
            sid = request.headers.getHeader('sid')
            self.service.unsubscribe(sid)
            return Response(200)
        except KeyError:
            return Response(412)
        except Exception, e:
            logger.log_fatal("UNSUBSCRIBE failed: %s" % e)
            return Response(500)

def _parseCallback(header):
    """Returns a list of one or more callback URLs"""
    return [cb[1:] for cb in header.split('>') if not cb == '']
DefaultHTTPHandler.addParser("Callback", (last, _parseCallback))

def _parseNT(header):
    """Returns the notification type header"""
    return header
DefaultHTTPHandler.addParser("NT", (last, _parseNT))

DefaultHTTPHandler.addGenerators("NT", (str, singleHeader))

def _parseSID(header):
    """Returns the subscription id header"""
    return header
DefaultHTTPHandler.addParser("SID", (last, _parseNT))

DefaultHTTPHandler.addGenerators("SID", (str, singleHeader))

def _parseTimeout(header):
    """Returns the event timeout"""
    try:
        unused,timeout = header.split('-')
        if timeout.lower() == 'infinite':
            return -1
        timeout = int(timeout)
        if timeout < 1800:
            timeout = 1800
        return timeout
    except Exception, e:
        logger.log_debug("failed to parse SUBSCRIBE timeout: %s" % str(e))
        return 1800
DefaultHTTPHandler.addParser("Timeout", (last, _parseTimeout))

def _generateTimeout(timeout):
    timeout = int(timeout)
    if timeout < 0:
        return 'Second-infinite'
    return 'Second-%i' % timeout
DefaultHTTPHandler.addGenerators("Timeout", (_generateTimeout, singleHeader))

__all__ = ['EventResource',]
