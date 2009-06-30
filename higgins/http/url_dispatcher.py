# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import re
from higgins.http.stream import FileStream
from higgins.http.http_headers import MimeType
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.http.logger import logger

class Route(object):
    def __init__(self, path, object):
        self.path = path
        self.regex = re.compile(path)
        if isinstance(object, UrlDispatcher):
            self._dispatcher = object
            self._callable = self._renderDispatcher
        elif callable(object):
            self._callable = object
        else:
            raise Exception('Callable is not a UrlDispatcher or callable')

    def _renderDispatcher(self, request, *params):
        try:
            request._subUrl = self.regex.split(request.path, 1)[1]
            logger.log_debug2("_renderDispatcher: subUrl='%s'" % request._subUrl)
            return self._dispatcher.renderHTTP(request)
        except Exception, e:
            logger.log_debug('_renderDispatcher failed: %s' % str(e))
            return Response(500, stream=str(e))

    def renderHTTP(self, request, *params):
        return self._callable(request, *params)

class UrlDispatcher(Resource):
    _routes = []

    def locateChild(self, request, segments):
        return self, []

    def renderHTTP(self, request):
        if not hasattr(request, '_subUrl'):
            request._subUrl = request.path
        logger.log_debug2("searching for route matching '%s'" % request._subUrl)
        for route in self._routes:
            match = route.regex.match(request._subUrl)
            if match:
                params = match.groups()
                logger.log_debug2("subUrl '%s' matched route '%s'" % (request._subUrl, route.path))
                return route.renderHTTP(request, *params)
        return Response(404, stream="Resource Not Found" % request.path)

    def addRoute(self, path, object, **options):
        self._routes.append(Route(path, object))
