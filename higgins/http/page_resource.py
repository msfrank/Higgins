# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.stream import FileStream
from higgins.http.http_headers import MimeType
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.core.logger import logger

class Page(object):
    def __init__(self, name, f, *children):
        self.name = name
        self.f = f
        for child in children:
            self.children[child.name] = child

class PageResource(Resource):

    pages = None

    def locateChild(self, request, segments):

    def render(self, request):
        try:
            return Response(200, {'content-type': mimetype}, FileStream(f))
        except:
            return Response(500)
