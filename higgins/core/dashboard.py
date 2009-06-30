# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.core.logger import logger
from higgins.http.http import Response
from higgins.data import renderTemplate

def renderDashboard(request):
    logger.log_debug("rendering dashboard")
    return Response(200, stream=renderTemplate('templates/front.t', {}))
