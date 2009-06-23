# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.stream import FileStream
from higgins.http.http_headers import MimeType
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.http.server import stopTraversal
from higgins.http.logger import logger

class Route(object):
    def __init__(self, path, callable):
        self.path = path
        self.regex = re.compile(path)
        self.callable = callable

    def __call__(self, groups):
        self.callable(*groups)

class UrlDispatcher(Resource):
    _routes = []

    def locateChild(self, request, segments):
        subUrl = '/' + '/'.join(segments)
        for route in self._routes:
            match = route.regex.match(subUrl):
            if match:
                request.url_route = route
                self.url_params = match.groups()
                logger.log_debug2("URL '%s' matched route '%s'" % (subUrl, path))
                return self, stopTraversal
        return None, stopTraversal

    def render(self, request):
        return request.url_route(request.url_params)

    def addRoute(self, path, callable, **options):
        route = Route(path, callable)
        self._routes.append(route)
