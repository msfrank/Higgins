# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from pkg_resources import resource_string
from higgins.http.http import Response
from higgins.core.dispatcher import Dispatcher
from higgins.core.logger import logger

class StaticResource(Dispatcher):
    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('/(.+)$', self.renderStaticContent)

    def renderStaticContent(self, request, path):
        try:
            try:
                data = resource_string('higgins.data', '/static/' + path)
                return Response(200, headers=None, stream=data)
            except IOError, e:
                if e.errno == 2:
                    logger.log_debug("couldn't find static resource %s" % path)
                    return Response(404, stream="Resource %s Not Found" % path)
                raise e
        except Exception, e:
            logger.log_debug("failed to render static resource %s: %s" % (path, str(e)))
        return Response(500, stream="Internal Server Error" % path)
