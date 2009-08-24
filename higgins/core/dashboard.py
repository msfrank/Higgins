# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.core.dispatcher import Dispatcher
from higgins.core.logger import logger
from higgins.http.http import Response

class DashboardResource(Dispatcher):
    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('', self.renderDashboard)
        
    def renderDashboard(self, request):
        return Response(200, stream=self.renderTemplate('templates/front.html', {}))
