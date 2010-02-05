# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import re
from higgins.http.stream import FileStream
from higgins.http.http_headers import MimeType
from higgins.http.resource import Resource
from higgins.http.base_resource import BaseResource
from higgins.http.http import Response
from higgins.http.logger import logger

class Route(BaseResource):
    def __init__(self, path, destination, options):
        self.path = path
        self.regex = re.compile(path)
        if isinstance(destination, Dispatcher):
            self._dispatcher = destination
            self._callable = None
        elif callable(destination):
            self._dispatcher = None
            self._callable = destination
        else:
            raise Exception('destination is not a UrlDispatcher or callable')
        # default options
        self._allowedMethods = BaseResource.allowedMethods(self)
        self._maxFilesize = 10485760
        self._maxParamSize = 4096
        if 'allowedMethods' in options:
            self._allowedMethods = options['allowedMethods']
        if 'maxFileSize' in options:
            self._maxFileSize = options['maxFileSize']
        if 'maxParamSize' in options:
            self._maxParamSize = options['maxParamSize']
        self._options = options

    def allowedMethods(self):
        return self._allowedMethods

    def acceptFile(self, request, subheaders):
        return None

    def acceptParam(self, request, subheaders):
        return None

    def _renderDispatcher(self, request):
        try:
            request._subUrl = self.regex.split(request.path, 1)[1]
            #logger.log_debug2("_renderDispatcher: subUrl='%s'" % request._subUrl)
            return self._dispatcher.renderHTTP(request)
        except Exception, e:
            logger.log_error('_renderDispatcher failed: %s' % str(e))
            return Response(500, stream="Internal Server Error")

    def renderHTTP(self, request):
        if self._dispatcher:
            return self._renderDispatcher(request)
        if not request.method in self._allowedMethods:
            response = Response(405, stream="Method Not Allowed")
            response.headers.setHeader("allow", self._allowedMethods)
            return response
        return BaseResource.renderHTTP(self, request)

    def render(self, request):
        if self._callable == None:
            return Response(500, stream="Internal Server Error")
        logger.log_debug("%s %s" % (request.method, request.path))
        return self._callable(request, *request._urlParams)

class BaseDispatcher(Resource):
    def __init__(self):
        self._routes = []

    def locateChild(self, request, segments):
        return self, []

    def renderHTTP(self, request):
        if not hasattr(request, '_subUrl'):
            request._subUrl = request.path
        logger.log_debug2("searching for route matching '%s'" % request._subUrl)
        for route in self._routes:
            match = route.regex.match(request._subUrl)
            if match:
                request._urlParams = match.groups()
                logger.log_debug2("subUrl '%s' matched route '%s'" % (request._subUrl, route.path))
                return route.renderHTTP(request)
        logger.log_debug("resource %s not found" % request.path)
        return Response(404, stream="Resource %s Not Found" % request.path)

    def addRoute(self, path, object, **options):
        if not isinstance(object, BaseDispatcher) and not callable(object):
            raise Exception('object is not a BaseDispatcher or callable')
        for route in self._routes:
            if route.path == path:
                raise Exception("route '%s' already exists" % path)
        self._routes.append(Route(path, object, options))

    def removeRoute(self, path):
        for route in self._routes:
            if route.path == path:
                self._routes.remove(route)
                return
        raise Exception("route '%s' doesn't exist" % path)

class RootDispatcher(BaseDispatcher):
    def __init__(self):
        BaseDispatcher.__init__(self)
        self._toplevels = []

    def addToplevelRoute(self, path, d, name, root):
        if not isinstance(d, Dispatcher):
            raise Exception('d is not a Dispatcher instance')
        d._root = self
        self._toplevels.append((d, name, root))
        BaseDispatcher.addRoute(self, path, d)

    def addRoute(self, path, object, **options):
        if isinstance(object, Dispatcher):
            object._root = self
        BaseDispatcher.addRoute(self, path, object, **options)

class Dispatcher(BaseDispatcher):
    def __init__(self):
        BaseDispatcher.__init__(self)

    def addRoute(self, path, f, **options):
        if not callable(f):
            raise Exception('f is not a callable')
        BaseDispatcher.addRoute(self, path, f, **options)

__all__ = ['Route', 'RootDispatcher', 'Dispatcher']
