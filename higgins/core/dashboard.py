# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.resource import Resource
from higgins.data import renderTemplate

class DashboardResource(Resource):
    def allowedMethods(self):
        return ('GET')
    def render(self, request):
        return renderTemplate('templates/front.t', {})
