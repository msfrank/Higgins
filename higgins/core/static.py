# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from os.path import join as pathjoin
from pkg_resources import resource_string
from higgins.http.resource import Resource
from higgins.http.http import Response
from higgins.core.logger import CoreLogger

class StaticResource(resource.Resource):
    def allowedMethods(self):
        return ("GET",)
    def locateChild(self, request, segments):
        path = pathjoin(*segments)
        try:
            self.data = resource_string('higgins.data', path)
            return self, []
        except:
            return None, []
    def render(self, request):
        return Response(200, headers=None, stream=self.data)
